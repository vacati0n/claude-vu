"""Tests for demo mode's screen-capture path: OBS control, the capture manifest, the edit
decision list, the composed presentation frame, and the ffmpeg cut.

Nothing here opens a window, drives OBS, or records a screen. What is pinned is everything
between the recording and the film:

  * the obs-websocket client reads the host's own config and reports, rather than raises,
    when the server is off;
  * the capture manifest carries the one fact the editor cannot work without -- the instant
    the recording's own clock read zero -- and markers map onto video time through it;
  * the edit decision list keeps the head and the tail of a long wait at real speed and
    condenses only the middle, never drops below the minimum segment, and lays segments end
    to end without gaps;
  * a beat recorded before the camera started is excluded rather than mis-timed;
  * the composed frame is canvas-sized, leaves a transparent hole exactly where the footage
    is placed, and never truncates the title;
  * the build routes to the editor when a recording exists and to the drawn dashboard when
    it does not;
  * the whole cut runs end to end against a synthetic recording (ffmpeg required; skipped
    when it is absent).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import demo                                  # noqa: E402
import state_engine as se                    # noqa: E402
import framework_runtime as fr               # noqa: E402
from demo import capture as dcap             # noqa: E402
from demo import editor as ded               # noqa: E402
from demo import obs_ws                      # noqa: E402
from demo import overlays as dov             # noqa: E402
from demo import recorder as drec            # noqa: E402
from demo import video_builder as dvb        # noqa: E402

T0 = datetime(2026, 9, 12, 10, 0, 0, tzinfo=timezone.utc)


def _ffmpeg():
    path, _ = dvb.find_ffmpeg()
    return path


def _iso(offset_seconds: float) -> str:
    return (T0 + timedelta(seconds=offset_seconds)).isoformat(
        timespec="milliseconds").replace("+00:00", "Z")


def _marker(seq: int, at: float, action: str, *, phase: str | None = None,
            title: str = "", payload: dict | None = None, agent: str = "runtime:x") -> dict:
    return {"marker_id": f"M-{seq:06d}", "seq": seq, "timestamp": _iso(at),
            "t_ms": int(at * 1000), "run_id": "run-cap00000001", "agent_name": agent,
            "action_type": action, "phase": phase, "title": title or action,
            "payload": payload or {}, "visual_snapshot_text": "", "source": "runtime",
            "source_event_id": f"E-{seq:04d}"}


def _markers() -> list:
    """A run whose beats are 0s, 4s, 10s, 70s and 95s into the recording: one short gap, one
    very long one, so both edit shapes are exercised."""
    return [
        _marker(1, 0, "run_initialized", phase="p1",
                payload={"command_id": "implement", "workflow_id": "implement-feature",
                         "phases": ["p1", "p2"]}),
        _marker(2, 0.2, "work_item_enqueued", phase="p1",
                payload={"work_type": "state", "owner_agent_id": "planner", "index": 1}),
        _marker(3, 0.3, "work_item_enqueued", phase="p1",
                payload={"work_type": "gate", "gate": "Scope Gate",
                         "owner_roles": ["omn-qa"]}),
        _marker(4, 4, "dispatch", phase="p1", title="Dispatch: p1",
                payload={"agent_id": "planner", "prompt_tokens_est": 12000}),
        _marker(5, 10, "prompt_exchange", phase="p1", agent="planner",
                title="planner is thinking", payload={"prompt_bytes": 8000}),
        _marker(6, 70, "agent_response", phase="p1", agent="planner",
                title="planner responded",
                payload={"status": "succeeded", "artifact_refs": ["a/execution-plan.md"]}),
        _marker(7, 95, "validation", phase="p1", title="Validation passed",
                payload={"result": "pass", "checks_passed": 45, "checks_run": 45}),
    ]


def _run(tmp: Path, markers: list | None = None, *, enable: bool = True) -> Path:
    run_dir = tmp / "runs" / "run-cap00000001"
    run_dir.mkdir(parents=True)
    se.StateStore.create(run_dir, run_id=run_dir.name, command_id="implement",
                         workflow_id="implement-feature", workflow_version="1.0.0",
                         runtime_version=fr.RUNTIME_VERSION, input_digest="sha256:t", inputs=[])
    (run_dir / "execution-request.json").write_text(json.dumps(
        {"run_id": run_dir.name, "command_id": "implement",
         "workflow_id": "implement-feature", "phases": ["p1", "p2"], "inputs": []}),
        encoding="utf-8")
    if enable:
        demo.enable(run_dir, options={"narration": "off", "title": "A recorded run"})
    if markers:
        d = run_dir / "demo"
        d.mkdir(parents=True, exist_ok=True)
        with (d / "markers.jsonl").open("w", encoding="utf-8") as fh:
            for m in markers:
                fh.write(json.dumps(m) + "\n")
    return run_dir


def _capture_manifest(run_dir: Path, video: Path, *, duration: float, t0_offset: float = 0.0,
                      size=(1280, 720), state: str = "recorded") -> dict:
    """A manifest as the capture session would have written it. `t0_offset` shifts the
    recording's zero relative to the first marker."""
    d = run_dir / "demo" / "capture"
    d.mkdir(parents=True, exist_ok=True)
    data = {
        "schema": "framework.runtime/demo-capture-manifest.v1", "run_id": run_dir.name,
        "backend": "ffmpeg-gdigrab", "video": str(video), "fps": 30,
        "rect": [0, 0, size[0], size[1]],
        "window": {"title": "Claude", "class": "Chrome_WidgetWin_1", "exe": "Claude.exe",
                   "pid": 1},
        "started_at": _iso(-t0_offset), "stopped_at": _iso(duration - t0_offset),
        "duration_seconds": duration, "warnings": [], "state": state,
    }
    (d / dcap.MANIFEST).write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def _synthetic_capture(path: Path, seconds: int = 100, size=(1280, 720)) -> Path:
    ff = _ffmpeg()
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([ff, "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
                    f"testsrc=size={size[0]}x{size[1]}:rate=30", "-t", str(seconds),
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
                    str(path)], check=True, timeout=600)
    return path


class ObsWebSocketTestCase(unittest.TestCase):
    def test_config_is_read_from_the_host_and_reports_when_disabled(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / obs_ws.CONFIG_REL
            cfg.parent.mkdir(parents=True)
            cfg.write_text(json.dumps({"server_enabled": False, "server_port": 4455,
                                       "server_password": "pw", "auth_required": True}),
                           encoding="utf-8")
            with mock.patch.dict(os.environ, {"APPDATA": tmp}):
                c = obs_ws.read_config()
                self.assertFalse(c["enabled"])
                self.assertEqual(c["port"], 4455)
                self.assertIn("WebSocket Server Settings", c["reason"])
                p = obs_ws.probe()
            self.assertFalse(p["reachable"])
            self.assertNotIn("password", json.dumps(p))

    def test_probe_never_raises_without_any_obs_installation(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.dict(os.environ, {"APPDATA": tmp}):
                self.assertFalse(obs_ws.probe()["reachable"])

    def test_connect_failure_is_an_obs_error_naming_the_port(self):
        with mock.patch.object(obs_ws, "read_config",
                               return_value={"enabled": True, "port": 45999,
                                             "password": None, "auth_required": False,
                                             "reason": None}):
            with self.assertRaises(obs_ws.OBSError) as cm:
                obs_ws.OBSClient.connect(timeout=0.5)
        self.assertIn("45999", str(cm.exception))


class CaptureManifestTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-cap-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _run(self.tmp, _markers())

    def test_absent_capture_reads_as_none_and_has_capture_is_false(self):
        self.assertIsNone(dcap.load_manifest(self.run_dir))
        self.assertFalse(demo.has_capture(self.run_dir))

    def test_a_recorded_manifest_with_a_real_file_counts_as_a_capture(self):
        video = self.run_dir / "demo" / "capture" / "session.mkv"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"not really a video")
        _capture_manifest(self.run_dir, video, duration=100)
        self.assertTrue(demo.has_capture(self.run_dir))
        m = dcap.load_manifest(self.run_dir)
        self.assertEqual(m["state"], "recorded")
        self.assertEqual(m["backend"], "ffmpeg-gdigrab")
        self.assertTrue(m["started_at"].endswith("Z"))

    def test_a_recording_still_in_progress_is_not_a_capture_to_edit(self):
        video = self.run_dir / "demo" / "capture" / "session.mkv"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"x")
        _capture_manifest(self.run_dir, video, duration=10, state="recording")
        self.assertFalse(demo.has_capture(self.run_dir))

    def test_starting_a_second_recording_is_refused(self):
        video = self.run_dir / "demo" / "capture" / "session.mkv"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"x")
        _capture_manifest(self.run_dir, video, duration=10, state="recording")
        with self.assertRaises(dcap.CaptureError) as cm:
            dcap.start_detached(self.run_dir)
        self.assertIn("already in progress", str(cm.exception))


class EditDecisionTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-cap-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.markers = _markers()
        self.run_dir = _run(self.tmp, self.markers)
        from demo.timeline import build_scenes
        self.scenes = build_scenes(self.markers, {"title": "A recorded run"})

    def test_markers_map_onto_video_time_through_the_manifest(self):
        spans = ded.scene_spans(self.scenes, self.markers, _iso(0), 120)
        self.assertTrue(spans)
        self.assertAlmostEqual(spans[0]["start"], 0.0, places=2)
        # the opening scene absorbs the routing burst, so the next beat is the dispatch at 4s
        self.assertAlmostEqual(spans[1]["start"], 4.0, places=2)
        for a, b in zip(spans, spans[1:]):
            self.assertAlmostEqual(a["end"], b["start"], places=3)

    def test_a_recording_that_started_late_excludes_the_beats_it_missed(self):
        # zero of the recording is 60s after the first marker: everything before that is gone
        spans = ded.scene_spans(self.scenes, self.markers, _iso(60), 60)
        starts = [round(s["start"], 1) for s in spans]
        self.assertTrue(all(s >= 0 for s in starts))
        self.assertLess(len(spans), len(self.scenes))
        kinds = [s["scene"]["kind"] for s in spans]
        self.assertNotIn("opening", kinds)
        self.assertIn("agent_response", kinds)

    def test_spans_are_clamped_to_the_length_of_the_recording(self):
        spans = ded.scene_spans(self.scenes, self.markers, _iso(0), 30)
        self.assertTrue(all(s["end"] <= 30.0001 for s in spans))
        self.assertTrue(all(s["start"] >= 0 for s in spans))
        self.assertTrue(all(s["end"] > s["start"] for s in spans))

    def test_a_brief_beat_is_slowed_rather_than_dropped(self):
        """Two events a fraction of a second apart are two things the run did, and both
        captions have to be readable."""
        markers = self.markers + [
            _marker(8, 95.2, "gate_awaiting", phase="p1", title="Scope Gate awaits",
                    payload={"gate": "Scope Gate", "owner_roles": ["omn-qa"]}),
            _marker(9, 95.3, "gate_decision", phase="p1", title="Scope Gate approved",
                    payload={"gate": "Scope Gate", "decision": "approved",
                             "owner_role": "omn-qa", "decided_by": "sam"}),
            _marker(10, 95.45, "aggregation", title="package", payload={"completed": 1,
                                                                        "phases": 2}),
        ]
        from demo.timeline import build_scenes
        scenes = build_scenes(markers, {})
        spans = ded.scene_spans(scenes, markers, _iso(0), 120)
        segments = ded.plan_edit(spans)
        held = [s for s in segments if s["role"] == "held"]
        self.assertTrue(held, [s["role"] for s in segments])
        for s in held:
            self.assertLess(s["speed"], 1.0)
            self.assertGreaterEqual(s["speed"], ded.MIN_SPEED)
            self.assertGreater(s["duration"], s["out"] - s["in"])   # longer on screen
        # every beat inside the recording reaches the film
        self.assertEqual({id(s["scene"]) for s in segments}, {id(s["scene"]) for s in spans})

    def test_short_spans_play_untouched_and_long_ones_keep_head_and_tail(self):
        spans = ded.scene_spans(self.scenes, self.markers, _iso(0), 120)
        segments = ded.plan_edit(spans)
        by_role = {}
        for s in segments:
            by_role.setdefault(s["role"], []).append(s)
        self.assertIn("condensed", by_role)
        self.assertIn("beat", by_role)
        for s in by_role["beat"]:
            self.assertEqual(s["speed"], 1.0)
            self.assertLessEqual(s["out"] - s["in"], ded.KEEP_WHOLE_S + 0.001)
        for s in by_role["condensed"]:
            self.assertGreater(s["speed"], 1.0)
            self.assertLessEqual(s["speed"], ded.MAX_SPEED)
            self.assertAlmostEqual(s["duration"], ded.CONDENSED_S, places=2)
        # every condensed segment is flanked by a real-speed head and tail of the same beat
        for i, s in enumerate(segments):
            if s["role"] != "condensed":
                continue
            self.assertEqual(segments[i - 1]["role"], "head")
            self.assertEqual(segments[i + 1]["role"], "tail")
            self.assertIs(segments[i - 1]["scene"], s["scene"])
            self.assertIs(segments[i + 1]["scene"], s["scene"])

    def test_output_segments_are_laid_end_to_end_with_no_gap(self):
        segments = ded.plan_edit(ded.scene_spans(self.scenes, self.markers, _iso(0), 120))
        t = 0.0
        for s in segments:
            self.assertAlmostEqual(s["at"], t, places=6)
            t += s["duration"]
        self.assertAlmostEqual(ded.body_duration(segments), t, places=6)
        self.assertLess(t, 120)          # the film is shorter than the recording

    def test_the_cut_is_never_longer_than_what_it_was_cut_from(self):
        spans = ded.scene_spans(self.scenes, self.markers, _iso(0), 120)
        segments = ded.plan_edit(spans)
        raw = sum(s["end"] - s["start"] for s in spans)
        self.assertLess(ded.body_duration(segments), raw)
        for s in segments:
            self.assertGreaterEqual(s["in"], 0)
            self.assertLessEqual(s["out"], 120.0001)
            self.assertGreater(s["out"], s["in"])

    def test_the_filtergraph_declares_every_segment_and_concatenates_them(self):
        segments = ded.plan_edit(ded.scene_spans(self.scenes, self.markers, _iso(0), 120))
        g = ded.build_filtergraph(segments, capture_size=(1280, 720), fps=30, has_intro=True,
                                  has_outro=True, intro_idx=2, outro_idx=3, overlay_idx=1)
        for i in range(len(segments)):
            self.assertIn(f"[s{i}]", g)
        self.assertIn(f"concat=n={len(segments)}:v=1:a=0[raw]", g)
        self.assertIn("[outv]", g)
        self.assertIn("concat=n=3:v=1:a=0[outv]", g)
        self.assertEqual(g.count("[intro]"), 2)
        self.assertNotIn("setpts=(PTS-STARTPTS)/1.000000", g)   # 1x needs no rescale


class OverlayTestCase(unittest.TestCase):
    @unittest.skipUnless(dov.has_pil(), "Pillow not installed")
    def test_the_frame_is_canvas_sized_and_leaves_a_hole_for_the_footage(self):
        scene = {"kind": "dispatch", "title": "Dispatch: execution planning",
                 "subtitle": "planner · ~12.0k tokens", "phase": "p1",
                 "projection": {"phases": [{"state_id": "p1", "index": 1, "status": "running",
                                            "owner": "planner", "gates": ["Scope Gate"],
                                            "attempt": 1}],
                                "gates": {"Scope Gate": {"status": "awaiting",
                                                         "owner_roles": ["omn-qa"]}},
                                "command_id": "implement"}}
        img = dov.beat_overlay(scene, run_id="run-x", command="implement",
                               capture_size=(1280, 720), fraction=0.4, speed=12.0)
        self.assertEqual(img.size, dov.CANVAS)
        self.assertEqual(img.mode, "RGBA")
        x, y, w, h = dov._video_target((1280, 720))
        self.assertEqual(img.getpixel((x + w // 2, y + h // 2))[3], 0)   # transparent hole
        self.assertGreater(img.getpixel((40, 36))[3], 0)                 # brand bar is drawn
        self.assertGreater(img.getpixel((dov.RAIL_BOX[0] + 40,
                                         dov.RAIL_BOX[1] + 40))[3], 0)   # rail is drawn

    @unittest.skipUnless(dov.has_pil(), "Pillow not installed")
    def test_the_footage_keeps_its_aspect_ratio_inside_the_box(self):
        for size in ((1920, 1032), (1280, 720), (800, 1200)):
            x, y, w, h = dov._video_target(size)
            self.assertAlmostEqual(w / h, size[0] / size[1], places=1)
            bx, by, bw, bh = dov.VIDEO_BOX
            self.assertGreaterEqual(x, bx)
            self.assertGreaterEqual(y, by)
            self.assertLessEqual(x + w, bx + bw + 1)
            self.assertLessEqual(y + h, by + bh + 1)
            self.assertEqual((w % 2, h % 2), (0, 0))

    @unittest.skipUnless(dov.has_pil(), "Pillow not installed")
    def test_a_long_title_is_shrunk_rather_than_cut(self):
        long_title = ("Autonomous end to end demonstration of the multi agent delivery "
                      "framework, recorded live and cut by its own telemetry")
        img = dov.title_card(long_title, "/implement --demo", ["one", "two"])
        self.assertEqual(img.size, dov.CANVAS)
        # the last word has to be on the card somewhere: something is drawn low enough to
        # hold a third line
        band = img.crop((300, 440, 1500, 560))
        self.assertTrue(any(p[3] > 0 for p in band.getdata()))

    @unittest.skipUnless(dov.has_pil(), "Pillow not installed")
    def test_the_closing_card_carries_the_run_numbers(self):
        img = dov.outro_card("A recorded run", [("6/6", "phases"), ("7", "gates")], "footer")
        self.assertEqual(img.size, dov.CANVAS)
        self.assertEqual(img.getpixel((10, 10))[3], 255)       # opaque card


class FinishAndOcclusionTestCase(unittest.TestCase):
    """When the run is done, and what of the recording may be shown."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-cap-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _run(self.tmp, _markers())

    def _state(self, phases_done: bool, gates_decided: bool):
        state = {
            "work_items": {
                "p1": {"work_type": "state",
                       "status": "completed" if phases_done else "running"},
                "g1": {"work_type": "gate", "status": "blocked"},
            },
            "gates": {"Scope Gate": {"decision": "approved" if gates_decided else None}},
        }
        (self.run_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")

    def test_a_run_is_not_finished_while_a_gate_is_undecided(self):
        """The runtime emits `run_completed` when the last phase commits, which is before
        the gate closing it has been decided. Stopping the camera there would cut the film
        one beat short of the final human approval."""
        self._state(phases_done=True, gates_decided=False)
        self.assertFalse(demo.run_is_finished(self.run_dir))
        self._state(phases_done=True, gates_decided=True)
        self.assertTrue(demo.run_is_finished(self.run_dir))

    def test_a_run_is_not_finished_while_a_phase_is_running(self):
        self._state(phases_done=False, gates_decided=True)
        self.assertFalse(demo.run_is_finished(self.run_dir))

    def test_a_run_with_no_state_store_is_not_finished(self):
        self.assertFalse(demo.run_is_finished(self.tmp / "nowhere"))

    def test_the_film_is_compiled_once_however_many_events_say_it_is_done(self):
        self.assertTrue(demo.claim_autobuild(self.run_dir))
        self.assertFalse(demo.claim_autobuild(self.run_dir))
        self.assertFalse(demo.claim_autobuild(self.run_dir))

    def test_footage_of_anything_but_the_target_window_is_never_published(self):
        """The ffmpeg backend films the screen inside the window's rectangle, so whatever
        comes in front is filmed instead -- someone's desktop, for instance. Those spans are
        recorded while filming and excluded here."""
        from demo.timeline import build_scenes
        markers = _markers()
        scenes = build_scenes(markers, {})
        clean = ded.scene_spans(scenes, markers, _iso(0), 120)
        guarded = ded.scene_spans(scenes, markers, _iso(0), 120, occluded=[[8.0, 80.0]])
        self.assertLess(sum(s["end"] - s["start"] for s in guarded),
                        sum(s["end"] - s["start"] for s in clean))
        for s in guarded:
            self.assertFalse(ded._overlaps(s["start"] + 0.01, s["end"] - 0.01,
                                           [[8.0, 80.0]]),
                             f"{s['scene']['kind']} publishes hidden footage")

    def test_a_wholly_hidden_recording_publishes_nothing(self):
        from demo.timeline import build_scenes
        markers = _markers()
        spans = ded.scene_spans(build_scenes(markers, {}), markers, _iso(0), 120,
                                occluded=[[0.0, 200.0]])
        self.assertEqual(spans, [])


class BuildRoutingTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-cap-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _run(self.tmp, _markers())

    def test_without_a_recording_the_build_draws_the_dashboard(self):
        with mock.patch.object(dvb, "build", return_value={"outputs": {"html": "x"}}) as drawn:
            demo.build(self.run_dir, reason="manual")
        drawn.assert_called_once()

    def test_with_a_recording_the_build_edits_it(self):
        video = self.run_dir / "demo" / "capture" / "session.mkv"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"x")
        _capture_manifest(self.run_dir, video, duration=100)
        with mock.patch.object(ded, "edit",
                               return_value={"outputs": {"mp4": "x"}}) as cut, \
                mock.patch.object(dvb, "build") as drawn:
            demo.build(self.run_dir, reason="manual")
        cut.assert_called_once()
        drawn.assert_not_called()

    def test_drawn_forces_the_dashboard_even_with_a_recording(self):
        video = self.run_dir / "demo" / "capture" / "session.mkv"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"x")
        _capture_manifest(self.run_dir, video, duration=100)
        with mock.patch.object(ded, "edit") as cut, \
                mock.patch.object(dvb, "build", return_value={"outputs": {}}) as drawn:
            demo.build(self.run_dir, reason="manual", drawn=True)
        cut.assert_not_called()
        drawn.assert_called_once()

    def test_a_failed_edit_falls_back_to_the_dashboard(self):
        video = self.run_dir / "demo" / "capture" / "session.mkv"
        video.parent.mkdir(parents=True, exist_ok=True)
        video.write_bytes(b"not a video")
        _capture_manifest(self.run_dir, video, duration=100)
        with mock.patch.object(dvb, "build",
                               return_value={"outputs": {"html": "x"}}) as drawn:
            result = demo.build(self.run_dir, reason="manual", quiet=True)
        drawn.assert_called_once()
        self.assertIn("html", result["outputs"])

    def test_an_edit_without_a_recording_reports_instead_of_raising(self):
        m = ded.edit(self.run_dir, quiet=True)
        self.assertTrue(m["errors"])
        self.assertFalse(m["outputs"])
        self.assertIn("no capture manifest", m["errors"][0])


class FakeObsBackendTestCase(unittest.TestCase):
    """The OBS backend against a stand-in server speaking protocol v5.

    OBS cannot be driven on a machine whose WebSocket server is switched off, and switching
    it on is the operator's decision, not the framework's. What can still be proven is
    everything the framework does over that connection: the authentication handshake, the
    provisioning sequence, the window specification it asks OBS to capture, and the arithmetic
    that turns OBS's own reported recording position into the instant the clock read zero.
    """

    def setUp(self):
        sys.path.insert(0, str(Path(__file__).resolve().parent / "fixtures"))
        from fake_obs import FakeOBS
        self.server = FakeOBS(password="pw", auth=True)
        self.server.out_path = str(Path(tempfile.gettempdir()) / "obs-out.mkv")
        self.server.start()
        self.server.ready.wait(5)
        self.addCleanup(self.server.sock.close)
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-obs-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _run(self.tmp, _markers())
        self.cfg = {"enabled": True, "port": self.server.port, "password": "pw",
                    "auth_required": True, "reason": None}

    def _session(self):
        session = dcap.CaptureSession.__new__(dcap.CaptureSession)
        session.run_dir = self.run_dir
        session.dir = self.run_dir / "demo" / "capture"
        session.fps = 30
        session.stem = "session"
        session.rect = [0, 0, 1281, 721]          # odd on purpose: must be made even
        session.window = {"title": "Claude", "class": "Chrome_WidgetWin_1",
                          "exe": "Claude.exe", "pid": 1}
        session.t0 = None
        session.command = None
        session.backend_version = None
        session.obs_source = None
        session.warnings = []
        session.video_path = session.dir / "session.mp4"
        return session

    def test_the_backend_authenticates_provisions_and_records(self):
        session = self._session()
        backend = dcap.OBSBackend()
        with mock.patch.object(obs_ws, "read_config", return_value=self.cfg), \
                mock.patch.object(dcap.time, "sleep", lambda *_: None):
            backend.start(session)
        self.assertTrue(self.server.auth_ok)
        self.assertIn("32.2.2", session.backend_version)

        issued = [r for r, _ in self.server.requests]
        for expected in ("GetVersion", "CreateSceneCollection", "CreateProfile",
                         "SetProfileParameter", "CreateScene", "SetCurrentProgramScene",
                         "CreateInput", "StartRecord", "GetRecordStatus"):
            self.assertIn(expected, issued, issued)
        self.assertLess(issued.index("CreateInput"), issued.index("StartRecord"))

        by_type = {}
        for rtype, data in self.server.requests:
            by_type.setdefault(rtype, []).append(data)
        self.assertEqual(by_type["CreateSceneCollection"][0]["sceneCollectionName"],
                         dcap.OBS_COLLECTION)
        self.assertEqual(by_type["CreateProfile"][0]["profileName"], dcap.OBS_PROFILE)

        # the window OBS is told to capture, and true window capture rather than BitBlt
        created = by_type["CreateInput"][0]
        self.assertEqual(created["inputKind"], "window_capture")
        self.assertEqual(created["inputSettings"]["window"],
                         "Claude:Chrome_WidgetWin_1:Claude.exe")
        self.assertEqual(created["inputSettings"]["method"], dcap.WGC_METHOD)
        self.assertFalse(created["inputSettings"]["capture_audio"])

        # the canvas is the window's own size, rounded to even, and the run's directory
        params = {(d["parameterCategory"], d["parameterName"]): d["parameterValue"]
                  for d in by_type["SetProfileParameter"]}
        self.assertEqual(params[("Video", "BaseCX")], "1280")
        self.assertEqual(params[("Video", "BaseCY")], "720")
        self.assertEqual(params[("Video", "FPSCommon")], "30")
        self.assertEqual(params[("SimpleOutput", "FilePath")], str(session.dir))
        self.assertEqual(session.rect, [0, 0, 1280, 720])

        # t0 is derived from how far in OBS says it already is, not from the call's own clock
        self.assertIsNotNone(session.t0)
        import time as _t
        self.assertGreater(_t.time() - session.t0, 0.3)
        self.assertLess(_t.time() - session.t0, 5.0)

    def test_stop_returns_the_path_obs_reports(self):
        session = self._session()
        backend = dcap.OBSBackend()
        with mock.patch.object(obs_ws, "read_config", return_value=self.cfg), \
                mock.patch.object(dcap.time, "sleep", lambda *_: None):
            backend.start(session)
            out = backend.stop(session)
        self.assertEqual(str(out), self.server.out_path)
        self.assertIn("StopRecord", [r for r, _ in self.server.requests])

    def test_a_wrong_password_is_refused(self):
        bad = dict(self.cfg, password="not-the-password")
        with mock.patch.object(obs_ws, "read_config", return_value=bad):
            with self.assertRaises(obs_ws.OBSError):
                obs_ws.OBSClient.connect(port=self.server.port, password="not-the-password")
        self.assertFalse(getattr(self.server, "auth_ok", True))


@unittest.skipUnless(_ffmpeg() and dov.has_pil(), "ffmpeg and Pillow are required")
class EndToEndEditTestCase(unittest.TestCase):
    """The whole cut, against a synthetic recording standing in for a screen capture."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="omn-cap-e2e-"))
        cls.video = _synthetic_capture(cls.tmp / "capture.mp4", seconds=100)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.work = Path(tempfile.mkdtemp(prefix="omn-cap-run-"))
        self.addCleanup(shutil.rmtree, self.work, ignore_errors=True)
        self.run_dir = _run(self.work, _markers())
        _capture_manifest(self.run_dir, self.video, duration=100)

    def test_the_edit_produces_a_playable_film_shorter_than_the_recording(self):
        m = ded.edit(self.run_dir, quiet=True,
                     options={"narration": "off", "title": "A recorded run"})
        self.assertEqual(m["errors"], [])
        out = Path(m["outputs"]["mp4"])
        self.assertTrue(out.exists())
        self.assertGreater(out.stat().st_size, 20_000)
        self.assertGreater(m["segments"], 3)
        self.assertGreater(m["condensed"], 0)
        self.assertEqual(m["source"], "screen-capture")

        probe = ded._probe(_ffmpeg(), out)
        self.assertEqual((probe["width"], probe["height"]), dov.CANVAS)
        self.assertLess(probe["duration"], 100)
        self.assertAlmostEqual(probe["duration"], m["duration_ms"] / 1000, delta=2.0)
        self.assertTrue(Path(m["outputs"]["poster"]).exists())

    def test_the_edit_decision_list_is_recorded_for_review(self):
        m = ded.edit(self.run_dir, quiet=True, options={"narration": "off"})
        self.assertEqual(len(m["edl"]), m["segments"])
        for e in m["edl"]:
            for key in ("at", "duration", "in", "out", "speed", "role", "beat", "title"):
                self.assertIn(key, e)
            self.assertGreaterEqual(e["speed"], 1.0)
        self.assertEqual(m["edl"][0]["at"], 0)

    def test_the_recording_audio_is_never_published(self):
        m = ded.edit(self.run_dir, quiet=True, options={"narration": "off"})
        out = subprocess.run([_ffmpeg(), "-hide_banner", "-i", m["outputs"]["mp4"]],
                             capture_output=True, text=True).stderr
        self.assertNotIn("Audio:", out)


if __name__ == "__main__":
    unittest.main()
