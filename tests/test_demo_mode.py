"""Tests for demo mode (`/implement --demo`, runtime 0.8.0).

The invariants pinned here:
  * zero bloat: a run planned without `--demo` never creates `runs/<run>/demo/` and never
    imports the demo package from the event tap;
  * `--demo` throws the switch before the first event, so the recording starts at
    `run_initialized`, every marker carries a millisecond timestamp, and the same event
    replayed produces no second marker;
  * the Recorder enriches markers from what is on disk at event time: the dispatch prompt
    on `invocation_started`, the result envelope on `invocation_completed`, the validation
    report on `validation_*`, and the context estimate on `work_item_leased`;
  * host tool hooks land as `tool_invocation` markers on the active run only;
  * the projection and the text dashboard are pure functions of the marker stream;
  * the timeline folds bookkeeping markers and compresses towards the target while never
    cutting a narrated scene short;
  * the builder falls back in order (mp4 -> gif -> html) and records why, and the HTML deck
    is always produced; the autonomous trigger on `run_completed` runs the build and
    releases the active-run pointer;
  * a demo failure never propagates into the runtime.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402
import state_engine as se       # noqa: E402
import demo                      # noqa: E402
from demo import context as dctx           # noqa: E402
from demo import recorder as drec          # noqa: E402
from demo import renderer as drend         # noqa: E402
from demo import timeline as dtl           # noqa: E402
from demo import video_builder as dvb      # noqa: E402

REQUEST = """# Add a text summary tool to the workspace

## Request

Add a `summarize` tool that prints a twelve-line summary of a Markdown document.

## Acceptance criteria

- Deterministic for an unchanged input.
"""


def _capture(fn, *a, **kw):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = fn(*a, **kw)
    return rc, buf.getvalue()


def _synthetic_run(tmp: Path, run_id: str = "run-demo00000001") -> Path:
    """A run directory with a store, a request, and one dispatched phase on disk."""
    run_dir = tmp / "runs" / run_id
    run_dir.mkdir(parents=True)
    (tmp / "runs" / "inputs").mkdir(exist_ok=True)
    req = tmp / "runs" / "inputs" / "req.md"
    req.write_text(REQUEST, encoding="utf-8")
    se.StateStore.create(run_dir, run_id=run_id, command_id="implement",
                         workflow_id="implement-feature", workflow_version="1.0.0",
                         runtime_version=fr.RUNTIME_VERSION, input_digest="sha256:t", inputs=[])
    (run_dir / "execution-request.json").write_text(json.dumps({
        "run_id": run_id, "command_id": "implement", "workflow_id": "implement-feature",
        "phases": ["scope-and-acceptance", "execution-planning"],
        "inputs": [{"type": "feature-request", "reference": "runs/inputs/req.md"}],
        "requester": "test"}), encoding="utf-8")
    state = run_dir / "states" / "scope-and-acceptance"
    (state / "artifacts").mkdir(parents=True)
    (state / "dispatch-prompt.md").write_text(
        "# Agent Dispatch: omn-product-owner v1.0.0\n\n| Field | Value |\n|---|---|\n"
        "| run_id | `x` |\n\n## Instruction to the agent\n\nExecute your bootstrap "
        "procedure, then do your own work.\n\n1. Read the envelope.\n", encoding="utf-8")
    (state / "invocation-envelope.json").write_text(json.dumps({
        "invocation_id": "inv-1", "run_id": run_id, "state_id": "scope-and-acceptance",
        "agent_id": "omn-product-owner", "agent_version": "1.0.0",
        "timeout_profile": {"attempt": 1},
        "capability_bindings": {"load_order": ["a", "b", "c"], "load_profile": {"core": ["a"]}},
        "skill_dispatch": [{"skillCode": "S01", "status": "required"},
                           {"skillCode": "S06", "status": "not-triggered"}],
        "upstream_artifacts": [],
        "context_budget": {"progressive_estimate_tokens": 12000,
                           "legacy_estimate_tokens": 40000, "savings_pct": 70.0}}),
        encoding="utf-8")
    (state / "artifacts" / "scope-definition.md").write_text("# Scope\n\nbody\n" * 20,
                                                             encoding="utf-8")
    (state / "result-envelope.json").write_text(json.dumps({
        "invocation_id": "inv-1", "status": "succeeded",
        "artifact_refs": [f"runs/{run_id}/states/scope-and-acceptance/artifacts/"
                          f"scope-definition.md"],
        "structured_output": {"scope_id": "SD-1", "counts": {"criteria": 4},
                              "note": "Scope bounded to the summarizer and its test; the CLI "
                                      "surface is otherwise unchanged."},
        "confidence": 0.9, "declared_side_effects": []}), encoding="utf-8")
    (state / "validation-report.json").write_text(json.dumps({
        "checksRun": 33, "checksPassed": 33, "blockingFailures": 0, "correctableFailures": 0,
        "checks": []}), encoding="utf-8")
    return run_dir


def _events(run_id: str) -> list:
    """The canonical event sequence of one phase, as the runtime emits it."""
    def ev(n, et, state, actor, summary, details=None, actor_type="runtime", ts="12:00:00"):
        return {"event_id": f"E-{n:04d}", "run_id": run_id, "work_item_id": f"{run_id}::{state}",
                "event_type": et, "timestamp": f"2026-09-08T{ts}Z", "actor_type": actor_type,
                "actor_id": actor, "state_id": state, "reason_code": None, "summary": summary,
                "details_ref": details or {}}
    return [
        ev(1, "run_initialized", "scope-and-acceptance", "execution-coordinator",
           "run accepted for /implement -> implement-feature across 2 phase(s)"),
        ev(2, "work_item_enqueued", "scope-and-acceptance", "task-router",
           "state work item 1/2 routed to owner agent omn-product-owner",
           {"work_type": "state", "owner_agent_id": "omn-product-owner"}),
        ev(3, "work_item_enqueued", "Scope Gate", "task-router",
           "gate work item 'Scope Gate' enqueued to close phase scope-and-acceptance",
           {"work_type": "gate", "owner_roles": ["omn-business-analyst"]}),
        ev(4, "work_item_enqueued", "execution-planning", "task-router",
           "state work item 2/2 routed to owner agent planner",
           {"work_type": "state", "owner_agent_id": "planner"}),
        ev(5, "context_hydrated", "scope-and-acceptance", "context-loader",
           "context slice frozen: 13 member(s), 1 input(s)", ts="12:00:01"),
        ev(6, "work_item_leased", "scope-and-acceptance", "invocation-gateway",
           "invocation envelope built and leased", {"idempotency_key": "k", "adapter": "host"},
           ts="12:00:01"),
        ev(7, "invocation_started", "scope-and-acceptance", "invocation-gateway",
           "dispatching agent omn-product-owner v1.0.0 through host registration x",
           {"invocation_id": "inv-1"}, ts="12:00:01"),
        ev(8, "invocation_completed", "scope-and-acceptance", "omn-product-owner",
           "agent returned status 'succeeded' with 1 artifact ref(s)", actor_type="agent",
           ts="12:04:30"),
        ev(9, "validation_passed", "scope-and-acceptance", "validation-engine",
           "artifact conforms: 33/33 checks passed", ts="12:04:31"),
        ev(10, "escalation_opened", "Scope Gate", "state-engine",
           "gate work item blocked: awaiting_human_decision", {"work_type": "gate"},
           ts="12:04:31"),
        ev(11, "aggregation_completed", "execution-planning", "output-aggregator",
           "completion package and provenance manifest persisted for 1/2 completed phase(s)",
           ts="12:04:31"),
        ev(12, "escalation_resolved", "Scope Gate", "ba-human",
           "Scope Gate approved by omn-business-analyst (evidence: scope-and-acceptance)",
           {"gate": "Scope Gate", "owner_role": "omn-business-analyst",
            "decided_by": "ba-human", "rationale": "Scope is bounded."},
           actor_type="human", ts="12:30:00"),
        ev(13, "escalation_resolved", "execution-planning", "state-engine",
           "state work item unblocked", ts="12:30:00"),
    ]


class DemoSwitchTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-demo-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _synthetic_run(self.tmp)

    def test_off_by_default_costs_nothing_and_writes_nothing(self):
        ledger = fr.RunLedger(self.run_dir)
        with mock.patch.object(demo, "on_event") as tap:
            ledger.emit("run_initialized", state_id="scope-and-acceptance", actor_type="runtime",
                        actor_id="execution-coordinator", summary="s")
        tap.assert_not_called()
        self.assertFalse((self.run_dir / "demo").exists())
        self.assertFalse(demo.is_enabled(self.run_dir))

    def test_enable_is_idempotent_and_reads_the_title_from_the_request(self):
        first = demo.enable(self.run_dir, requester="op", options={"target_seconds": 45})
        again = demo.enable(self.run_dir, requester="someone-else",
                            options={"narration": "off", "title": None})
        self.assertTrue(demo.is_enabled(self.run_dir))
        self.assertEqual(first["enabled_at"], again["enabled_at"])
        self.assertEqual(again["requester"], "op")
        self.assertEqual(again["options"]["target_seconds"], 45)
        self.assertEqual(again["options"]["narration"], "off")
        self.assertEqual(again["options"]["title"], "Add a text summary tool to the workspace")
        self.assertEqual((self.tmp / "runs" / ".active-demo").read_text(encoding="utf-8"),
                         self.run_dir.name)

    def test_a_recorder_failure_never_reaches_the_runtime(self):
        demo.enable(self.run_dir)
        ledger = fr.RunLedger(self.run_dir)
        with mock.patch.object(drec.Recorder, "record_event", side_effect=RuntimeError("boom")):
            ev = ledger.emit("run_initialized", state_id="scope-and-acceptance",
                             actor_type="runtime", actor_id="execution-coordinator", summary="s")
        self.assertEqual(ev["event_id"], "E-0001")
        log = (self.run_dir / "demo" / "recorder.log").read_text(encoding="utf-8")
        self.assertIn("boom", log)


class RecorderTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-demo-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _synthetic_run(self.tmp)
        demo.enable(self.run_dir, options={"narration": "off"})
        self.rec = drec.Recorder(self.run_dir)

    def _record_all(self):
        for ev in _events(self.run_dir.name):
            self.rec.record_event(ev)
        return self.rec.markers()

    def test_markers_carry_millisecond_stamps_sequence_and_snapshot(self):
        markers = self._record_all()
        self.assertEqual(len(markers), 13)
        for i, m in enumerate(markers, 1):
            self.assertEqual(m["seq"], i)
            self.assertEqual(m["marker_id"], f"M-{i:06d}")
            self.assertRegex(m["timestamp"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}Z$")
            self.assertIn(m["action_type"], drec.ACTION_TYPES)
            for key in ("timestamp", "agent_name", "action_type", "payload",
                        "visual_snapshot_text", "t_ms", "run_id", "source_event_id"):
                self.assertIn(key, m)
            self.assertIn("WORKFLOW PIPELINE", m["visual_snapshot_text"])
        self.assertEqual(markers[0]["t_ms"], 0)
        self.assertTrue(all(b["t_ms"] >= a["t_ms"] for a, b in zip(markers, markers[1:])))

    def test_events_are_mapped_and_enriched_from_disk(self):
        markers = {m["source_event_id"]: m for m in self._record_all()}
        lease = markers["E-0006"]
        self.assertEqual(lease["action_type"], "dispatch")
        self.assertEqual(lease["payload"]["prompt_tokens_est"], 12000)
        self.assertEqual(lease["payload"]["legacy_tokens_est"], 40000)
        self.assertEqual(lease["payload"]["skills_required"], ["S01"])
        self.assertEqual(lease["payload"]["core_modules"], 1)
        start = markers["E-0007"]
        self.assertEqual(start["action_type"], "prompt_exchange")
        self.assertEqual(start["agent_name"], "omn-product-owner")
        self.assertTrue(start["payload"]["prompt_digest"].startswith("sha256:"))
        self.assertIn("Execute your bootstrap procedure", start["payload"]["prompt_excerpt"])
        self.assertNotIn("| Field |", start["payload"]["prompt_excerpt"])
        self.assertTrue(start["payload"]["thinking"])
        done = markers["E-0008"]
        self.assertEqual(done["action_type"], "agent_response")
        self.assertEqual(done["payload"]["status"], "succeeded")
        self.assertIn("Scope bounded", done["payload"]["agent_note"])
        self.assertGreater(done["payload"]["response_tokens_est"], 0)
        self.assertFalse(done["payload"]["thinking"])
        val = markers["E-0009"]
        self.assertEqual((val["payload"]["result"], val["payload"]["checks_passed"],
                          val["payload"]["checks_run"]), ("pass", 33, 33))
        self.assertEqual(markers["E-0010"]["action_type"], "gate_awaiting")
        gate = markers["E-0012"]
        self.assertEqual(gate["action_type"], "gate_decision")
        self.assertEqual(gate["payload"]["decision"], "approved")
        self.assertEqual(gate["phase"], "scope-and-acceptance")
        self.assertEqual(markers["E-0013"]["action_type"], "phase_unblocked")

    def test_a_replayed_event_is_not_a_second_marker(self):
        evs = _events(self.run_dir.name)
        self.rec.record_event(evs[0])
        self.assertIsNone(self.rec.record_event(evs[0]))
        self.assertEqual(len(self.rec.markers()), 1)

    def test_projection_is_a_pure_function_of_the_stream(self):
        markers = self._record_all()
        a = drec.build_projection(markers)
        b = drec.build_projection(markers)
        self.assertEqual(a, b)
        phase = next(p for p in a["phases"] if p["state_id"] == "scope-and-acceptance")
        self.assertEqual(phase["status"], "completed")
        self.assertEqual(phase["attempt"], 1)
        self.assertEqual(a["gates"]["Scope Gate"]["status"], "approved")
        self.assertEqual(a["tokens"]["prompt_est"], 12000)
        self.assertEqual(a["counters"]["invocations"], 1)
        self.assertEqual(a["counters"]["gates_decided"], 1)
        text = drend.render_text(a, markers[-1], title="T")
        self.assertEqual(text, drend.render_text(a, markers[-1], title="T"))
        self.assertIn("[=] 1 scope-and-acceptance", text)
        self.assertIn("<*> Scope Gate", text)
        self.assertTrue(all(ord(ch) < 128 for ch in text.replace("T", "")))

    def test_host_hook_lands_on_the_active_run_only(self):
        evs = _events(self.run_dir.name)
        for ev in evs[:7]:
            self.rec.record_event(ev)
        payload = {"session_id": "abc123def456", "hook_event_name": "PostToolUse",
                   "tool_name": "Read", "tool_input": {"file_path": "x/y.md", "content": "SECRET"},
                   "tool_response": {"ok": True}}
        m = demo.ingest_host_hook(self.tmp / "runs", payload)
        self.assertEqual(m["action_type"], "tool_invocation")
        self.assertEqual(m["agent_name"], "host:omn-product-owner")
        self.assertEqual(m["phase"], "scope-and-acceptance")
        self.assertEqual(m["payload"]["tool_name"], "Read")
        self.assertNotIn("SECRET", json.dumps(m))
        (self.tmp / "runs" / ".active-demo").unlink()
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("OMN_DEMO_RUN_ID", None)
            self.assertIsNone(demo.ingest_host_hook(self.tmp / "runs", payload))

    def test_backfill_reconstructs_markers_from_events_once(self):
        (self.run_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(e) for e in _events(self.run_dir.name)) + "\n",
            encoding="utf-8")
        self.assertEqual(self.rec.backfill_from_events()["recorded"], 13)
        self.assertEqual(self.rec.backfill_from_events()["recorded"], 0)
        markers = self.rec.markers()
        self.assertTrue(all(m["source"] == "backfill" for m in markers))
        self.assertEqual(markers[-1]["t_ms"], 30 * 60 * 1000)


class TimelineTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-demo-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _synthetic_run(self.tmp)
        demo.enable(self.run_dir, options={"narration": "off"})
        rec = drec.Recorder(self.run_dir)
        for ev in _events(self.run_dir.name):
            rec.record_event(ev)
        rec.record_tool_invocation({"tool_name": "Grep", "tool_input": {"pattern": "x"}})
        self.markers = rec.markers()

    def test_bookkeeping_is_folded_and_the_story_beats_remain(self):
        scenes = dtl.build_scenes(self.markers, {"title": "T"})
        kinds = [s["kind"] for s in scenes]
        self.assertEqual(kinds, ["opening", "dispatch", "prompt_exchange", "agent_response",
                                 "validation", "gate_decision", "tool_group"])
        self.assertEqual(scenes[0]["marker_ids"], ["M-000001", "M-000002", "M-000003",
                                                   "M-000004"])
        self.assertEqual(scenes[1]["marker_ids"], ["M-000005", "M-000006"])   # hydration + lease
        self.assertIn("M-000010", scenes[4]["marker_ids"])                    # gate arming
        self.assertIn("M-000011", scenes[4]["marker_ids"])                    # aggregation
        self.assertIn("M-000013", scenes[5]["marker_ids"])                    # unblocked
        self.assertTrue(scenes[2]["thinking"])
        self.assertFalse(scenes[3]["thinking"])
        self.assertIn("12.0k tokens", scenes[1]["subtitle"])
        self.assertIn("In its own words", scenes[3]["narration"])
        self.assertTrue(all(s["narration"] for s in scenes))

    def test_compression_honours_target_but_never_cuts_narration(self):
        scenes = dtl.build_scenes(self.markers, {})
        base = dtl.total_ms([dict(s) for s in scenes])
        dtl.compress(scenes, target_seconds=10, narration_ms={2: 9000})
        self.assertLess(dtl.total_ms(scenes) - 9500, base)
        self.assertGreaterEqual(scenes[2]["duration_ms"], 9500)
        for s in scenes:
            self.assertGreaterEqual(s["duration_ms"], dtl.MIN_SCENE_MS)
        self.assertEqual(scenes[0]["start_ms"], 0)
        self.assertEqual(scenes[1]["start_ms"], scenes[0]["duration_ms"])
        self.assertAlmostEqual(scenes[-1]["progress"], 1 - scenes[-1]["duration_ms"]
                               / dtl.total_ms(scenes), places=6)

    def test_scenes_are_deterministic(self):
        a = dtl.build_scenes(self.markers, {"title": "T"})
        b = dtl.build_scenes(self.markers, {"title": "T"})
        self.assertEqual([(s["kind"], s["title"], s["narration"]) for s in a],
                         [(s["kind"], s["title"], s["narration"]) for s in b])


class BuilderTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-demo-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _synthetic_run(self.tmp)
        demo.enable(self.run_dir, options={"narration": "off", "target_seconds": 6, "fps": 4,
                                           "width": 320, "height": 180})
        # the events are on disk as the runtime would have left them, so a later `emit`
        # numbers its event after them rather than reusing E-0001
        events = _events(self.run_dir.name)
        (self.run_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(e) for e in events) + "\n", encoding="utf-8")
        rec = drec.Recorder(self.run_dir)
        for ev in events:
            rec.record_event(ev)

    def test_html_deck_is_always_produced_and_fallbacks_are_recorded(self):
        with mock.patch.object(dvb, "find_ffmpeg", return_value=(None, "ffmpeg not found (test)")):
            manifest = dvb.build(self.run_dir, reason="manual", formats=["mp4", "html"],
                                 quiet=True)
        self.assertEqual(manifest["errors"], [])
        self.assertIn("html", manifest["outputs"])
        self.assertNotIn("mp4", manifest["outputs"])
        stages = [f["stage"] for f in manifest["fallbacks"]]
        self.assertIn("mp4", stages)
        html = Path(manifest["outputs"]["html"]).read_text(encoding="utf-8")
        self.assertIn("deck-data", html)
        self.assertIn("Agent Thinking", html)
        self.assertIn("Execution telemetry", html)
        self.assertIn("Add a text summary tool to the workspace", html)
        self.assertTrue((self.run_dir / "demo" / dvb.MANIFEST).exists())

    @unittest.skipUnless(drend.has_pil(), "Pillow not installed")
    def test_gif_fallback_when_ffmpeg_is_missing(self):
        with mock.patch.object(dvb, "find_ffmpeg", return_value=(None, "ffmpeg not found (test)")):
            manifest = dvb.build(self.run_dir, reason="manual", quiet=True)
        self.assertEqual(manifest["errors"], [])
        self.assertIn("gif", manifest["outputs"])
        self.assertIn("html", manifest["outputs"])
        gif = Path(manifest["outputs"]["gif"])
        self.assertGreater(gif.stat().st_size, 1000)
        self.assertEqual(gif.read_bytes()[:6], b"GIF89a")
        self.assertGreater(manifest["frames"], 5)
        self.assertEqual(manifest["engine"], "Pillow animated GIF")

    @unittest.skipUnless(drend.has_pil(), "Pillow not installed")
    def test_mp4_path_pipes_raw_frames_to_ffmpeg(self):
        fake = self.tmp / "fake-ffmpeg.py"
        fake.write_text(
            "import sys\n"
            "data = sys.stdin.buffer.read()\n"
            "out = sys.argv[-1]\n"
            "open(out, 'wb').write(b'MP4:' + str(len(data)).encode())\n"
            "sys.exit(0)\n", encoding="utf-8")
        launcher = self.tmp / ("fake-ffmpeg.cmd" if os.name == "nt" else "fake-ffmpeg")
        if os.name == "nt":
            launcher.write_text(f'@"{sys.executable}" "{fake}" %*\n', encoding="utf-8")
        else:
            launcher.write_text(f'#!/bin/sh\nexec "{sys.executable}" "{fake}" "$@"\n',
                                encoding="utf-8")
            launcher.chmod(0o755)
        with mock.patch.object(dvb, "find_ffmpeg", return_value=(str(launcher), "test")):
            manifest = dvb.build(self.run_dir, reason="manual", formats=["mp4", "html"],
                                 quiet=True)
        self.assertEqual(manifest["errors"], [])
        self.assertIn("mp4", manifest["outputs"])
        body = Path(manifest["outputs"]["mp4"]).read_bytes()
        self.assertTrue(body.startswith(b"MP4:"))
        self.assertEqual(int(body[4:]), manifest["frames"] * 320 * 180 * 3)
        self.assertEqual(manifest["engine"], "ffmpeg (test)")

    def _finish_the_run(self, gates_decided: bool = True):
        """Leave the state store as a genuinely finished run: every phase committed and
        every gate decided. The demo only compiles a film when nothing is left to decide."""
        (self.run_dir / "state.json").write_text(json.dumps({
            "work_items": {"p1": {"work_type": "state", "status": "completed"},
                           "g1": {"work_type": "gate", "status": "completed"}},
            "gates": {"Scope Gate": {"decision": "approved" if gates_decided else None}},
        }), encoding="utf-8")

    def _emit_completed(self):
        ledger = fr.RunLedger(self.run_dir)
        with mock.patch.object(dvb, "find_ffmpeg", return_value=(None, "no ffmpeg (test)")), \
                mock.patch.dict(os.environ, {"OMN_DEMO_TTS": "off"}):
            return _capture(ledger.emit, "run_completed", state_id="execution-planning",
                            actor_type="runtime", actor_id="execution-coordinator",
                            summary="every workflow phase completed",
                            details={"final_report": "final-report.md"})

    def test_the_film_waits_for_the_last_gate_rather_than_the_last_phase(self):
        """`run_completed` fires when the final phase commits, which is before the gate
        closing it has been decided. Compiling there would cut the film one beat short of
        the final human approval."""
        self._finish_the_run(gates_decided=False)
        self._emit_completed()
        self.assertFalse((self.run_dir / "demo" / dvb.MANIFEST).exists())
        self.assertTrue((self.tmp / "runs" / ".active-demo").exists())

    def test_run_completed_triggers_the_build_and_releases_the_pointer(self):
        self._finish_the_run()
        rc, out = self._emit_completed()
        self.assertTrue((self.run_dir / "demo" / dvb.MANIFEST).exists())
        manifest = json.loads((self.run_dir / "demo" / dvb.MANIFEST).read_text(encoding="utf-8"))
        self.assertEqual(manifest["reason"], "run_completed")
        self.assertIn("html", manifest["outputs"])
        self.assertIn("demo           : compiled", out)
        self.assertFalse((self.tmp / "runs" / ".active-demo").exists())
        markers = drec.Recorder(self.run_dir).markers()
        self.assertEqual(markers[-1]["action_type"], "run_completed")


class CliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-demo-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = _synthetic_run(self.tmp)
        self._runs = fr.RUNS
        fr.RUNS = self.tmp / "runs"
        self.addCleanup(setattr, fr, "RUNS", self._runs)

    def _args(self, **kw):
        # A real Namespace, deliberately not a Mock: a Mock invents any attribute asked of
        # it and the invented value reads as true, so a flag added to the parser but not to
        # this fixture would silently take a branch no test meant to exercise. With a
        # Namespace the same omission raises AttributeError and names the flag.
        base = {"run_id": self.run_dir.name, "build": False, "backfill": False, "hook": False,
                "out": None, "target_seconds": None, "formats": None, "narration": None,
                "fps": None, "keep_frames": False, "snapshot": False,
                "record_start": False, "record_stop": False, "capture_backend": "auto",
                "capture_fps": 30, "window_title": "Claude", "window_exe": "Claude.exe",
                "capture_offset": 0.0, "drawn": False, "keep_work": False,
                "print_hook": False}
        base.update(kw)
        return fr.argparse.Namespace(**base)

    def test_status_reports_a_run_without_demo_mode(self):
        rc, out = _capture(fr.cmd_demo, self._args())
        self.assertEqual(rc, 0)
        self.assertIn("not enabled", out)

    def test_backfill_then_status_with_snapshot(self):
        (self.run_dir / "events.jsonl").write_text(
            "\n".join(json.dumps(e) for e in _events(self.run_dir.name)) + "\n",
            encoding="utf-8")
        rc, out = _capture(fr.cmd_demo, self._args(backfill=True))
        self.assertEqual(rc, 0)
        self.assertIn("13 marker(s) reconstructed", out)
        rc, out = _capture(fr.cmd_demo, self._args(snapshot=True))
        self.assertIn("markers        : 13", out)
        self.assertIn("WORKFLOW PIPELINE", out)

    def test_hook_reads_stdin_and_is_inert_without_an_active_run(self):
        payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "a.md"}})
        with mock.patch.object(sys, "stdin", io.StringIO(payload)):
            rc, out = _capture(fr.cmd_demo, self._args(run_id=None, hook=True))
        self.assertEqual((rc, out), (0, ""))
        demo.enable(self.run_dir)
        with mock.patch.object(sys, "stdin", io.StringIO(payload)):
            rc, out = _capture(fr.cmd_demo, self._args(run_id=None, hook=True))
        self.assertEqual(rc, 0)
        self.assertIn("demo marker M-000001 recorded", out)

    def test_print_hook_resolves_the_framework_directory_and_matches_the_shipped_file(self):
        # `runtime/demo/hooks.settings.json` cannot know whether it was installed as
        # `.claude` or as `.omn-agent`, so it ships a `<framework-dir>` placeholder and
        # `--print-hook` resolves it. The two must stay one block: an operator who merges
        # the file by hand and an operator who pipes the command must wire up the same hook.
        rc, out = _capture(fr.cmd_demo, self._args(run_id=None, print_hook=True))
        self.assertEqual(rc, 0)
        printed = json.loads(out)

        command = printed["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
        self.assertEqual(
            command, f"python {fr.FW_PREFIX}/runtime/framework_runtime.py demo --hook")
        self.assertNotIn("<framework-dir>", command)

        shipped = json.loads(
            (RUNTIME / "demo" / "hooks.settings.json").read_text(encoding="utf-8"))
        resolved = json.loads(
            json.dumps(shipped["hooks"]).replace("<framework-dir>", fr.FW_PREFIX))
        self.assertEqual(printed["hooks"], resolved)

    def test_omn_agent_run_accepts_and_forwards_the_flag(self):
        from omn_agent import cli, runner
        ns = cli.build_parser().parse_args(["run", "PROJ-1", "--demo", "--approve"])
        self.assertTrue(ns.demo)
        self.assertFalse(cli.build_parser().parse_args(["run", "PROJ-1"]).demo)
        # the runtime argv the CLI wrapper builds for a planned task carries the switch
        calls = []

        def fake_invoke(fw_dir, target, argv, report):
            calls.append(argv)
            return 0, "run_id : run-0123456789ab"
        task = {"ticket": "PROJ-1", "command": "implement", "inputFile": "runs/inputs/x.md",
                "inputType": "feature-request"}
        with mock.patch.object(runner, "_invoke", side_effect=fake_invoke), \
                mock.patch.object(runner, "resolve_target", return_value=self.tmp), \
                mock.patch.object(runner, "framework_root", return_value=self.tmp), \
                mock.patch.object(runner, "load_task", return_value=(dict(task), self.tmp)), \
                mock.patch.object(runner, "save_task"), \
                mock.patch.object(runner, "_require_approval"), \
                mock.patch.object(runner, "_finish", return_value=0):
            ns = cli.build_parser().parse_args(["run", "PROJ-1", "--demo", "--approve"])
            runner.cmd_run(ns)
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], "plan")
        self.assertIn("--demo", calls[0])

    def test_plan_flag_is_declared_on_every_request_parser(self):
        parser = fr.argparse.ArgumentParser()
        fr.add_request_args(parser, with_phase=True)
        ns = parser.parse_args(["--demo", "--demo-title", "T", "--demo-seconds", "45",
                                "--demo-narration", "off", "--demo-record"])
        self.assertTrue(ns.demo)
        self.assertEqual((ns.demo_title, ns.demo_seconds, ns.demo_narration), ("T", 45.0, "off"))
        self.assertTrue(ns.demo_record)
        bare = parser.parse_args([])
        self.assertFalse(bare.demo)
        # every demo flag is off or unset unless asked for: planning a run must never start
        # a screen recording by accident
        self.assertFalse(bare.demo_record)
        self.assertIsNone(bare.demo_title)
        self.assertIsNone(bare.demo_seconds)
        self.assertIsNone(bare.demo_narration)


if __name__ == "__main__":
    unittest.main()
