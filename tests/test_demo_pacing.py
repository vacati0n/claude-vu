"""Tests for how a demo is paced and narrated for an audience seeing it once.

The brisk cut assumes the viewer knows the framework: it names each beat and moves on. The
relaxed, explaining cut assumes the opposite, and inverts the relationship between picture
and script -- the narration explains what each step *means*, and the film is paced to the
narration rather than the narration squeezed into the film.

What is pinned here:
  * the two pace profiles differ in the direction they claim to, and neither mutates the
    module defaults the brisk path and the existing tests rely on;
  * `explain` speaks the long line the first time a kind of beat occurs and the short one
    for every repeat, so a concept is explained once rather than three times;
  * a beat given more narration than it has footage is first un-condensed, then slowed to
    the floor, and only then held on its last frame -- in that order, so the picture keeps
    moving for as long as there is film left to show;
  * every beat ends up with at least as much screen time as the sentence spoken over it,
    which is what keeps two lines of narration from overlapping;
  * a beat that owns no footage borrows from the beat after it, and never the reverse;
  * the speech rate reaches the engine, and the filtergraph pins a constant frame rate
    before any hold, without which a variable-rate screen capture pads nothing at all.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(Path(__file__).resolve().parent))   # the marker fixtures next door

from demo import editor as ded            # noqa: E402
from demo import narration as tts         # noqa: E402
from demo import timeline as dtl          # noqa: E402
from demo.context import DEFAULT_OPTIONS  # noqa: E402

from test_demo_capture import _iso, _markers, _marker   # noqa: E402


def _scenes(markers=None):
    return dtl.build_scenes(markers or _markers(), {"title": "A recorded run"})


class PaceProfileTestCase(unittest.TestCase):
    def test_relaxed_holds_longer_and_condenses_less_than_brisk(self):
        brisk, relaxed = ded.Pace("brisk"), ded.Pace("relaxed")
        self.assertGreater(relaxed.KEEP_WHOLE_S, brisk.KEEP_WHOLE_S)
        self.assertGreater(relaxed.CONDENSED_S, brisk.CONDENSED_S)
        self.assertGreater(relaxed.MIN_SEGMENT_S, brisk.MIN_SEGMENT_S)
        self.assertGreater(relaxed.INTRO_S, brisk.INTRO_S)
        self.assertGreater(relaxed.OUTRO_S, brisk.OUTRO_S)
        self.assertLess(relaxed.MAX_SPEED, brisk.MAX_SPEED)

    def test_the_brisk_profile_is_the_module_default_and_stays_untouched(self):
        before = (ded.KEEP_WHOLE_S, ded.CONDENSED_S, ded.MIN_SEGMENT_S)
        brisk = ded.Pace("brisk")
        ded.Pace("relaxed")
        self.assertEqual((brisk.KEEP_WHOLE_S, brisk.CONDENSED_S, brisk.MIN_SEGMENT_S), before)
        self.assertEqual((ded.KEEP_WHOLE_S, ded.CONDENSED_S, ded.MIN_SEGMENT_S), before)

    def test_relaxed_is_the_default_for_a_demo(self):
        self.assertEqual(ded.Pace().name, "relaxed")
        self.assertEqual(DEFAULT_OPTIONS["pace"], "relaxed")
        self.assertTrue(DEFAULT_OPTIONS["explain"])
        self.assertLess(DEFAULT_OPTIONS["speech_rate"], 0)

    def test_the_same_run_yields_a_longer_film_at_the_relaxed_pace(self):
        scenes = _scenes()
        spans_a = ded.scene_spans(scenes, _markers(), _iso(0), 120)
        spans_b = ded.scene_spans(_scenes(), _markers(), _iso(0), 120)
        brisk = ded.body_duration(ded.plan_edit(spans_a, ded.Pace("brisk")))
        relaxed = ded.body_duration(ded.plan_edit(spans_b, ded.Pace("relaxed")))
        self.assertGreater(relaxed, brisk)


class ExplainNarrationTestCase(unittest.TestCase):
    def test_every_beat_carries_a_plain_language_explanation(self):
        markers = _markers() + [
            _marker(8, 96, "gate_awaiting", phase="p1", payload={"gate": "Scope Gate",
                                                                 "owner_roles": ["omn-qa"]}),
            _marker(9, 100, "gate_decision", phase="p1",
                    payload={"gate": "Scope Gate", "decision": "approved",
                             "owner_role": "omn-qa", "decided_by": "sam",
                             "rationale": "Scope is bounded."}),
            _marker(10, 110, "retry", phase="p1",
                    payload={"failure_class": "output-schema-failure", "action": "retry"}),
            _marker(11, 118, "run_completed", payload={"progressive_tokens": 42000}),
        ]
        scenes = dtl.build_scenes(markers, {"title": "A recorded run"})
        dtl.choose_narration(scenes, None, mode="explain")
        for s in scenes:
            self.assertTrue(s["narration_long"], s["kind"])
            self.assertTrue(s["spoken"], s["kind"])
        # the explanation says what a thing means, so it is materially longer than the label
        first = {s["kind"]: s for s in reversed(scenes)}
        for kind in ("dispatch", "prompt_exchange", "validation", "gate_decision"):
            s = first[kind]
            self.assertGreater(len(s["narration_long"].split()),
                               len(s["narration"].split()), kind)
        # and it avoids the runtime's own vocabulary, which means nothing to a new viewer
        opening = scenes[0]["narration_long"].lower()
        for jargon in ("idempotency", "envelope", "digest", "phase model", "artifact"):
            self.assertNotIn(jargon, opening)

    def test_a_concept_is_explained_once_and_named_thereafter(self):
        markers = _markers() + [
            _marker(8, 100, "dispatch", phase="p2", title="Dispatch: p2",
                    payload={"agent_id": "architect", "prompt_tokens_est": 9000}),
            _marker(9, 108, "prompt_exchange", phase="p2", agent="architect",
                    payload={"prompt_bytes": 4000}),
        ]
        scenes = dtl.build_scenes(markers, {})
        density = dtl.choose_narration(scenes, None, mode="explain")
        self.assertEqual(density, "explain")
        by_kind = {}
        for s in scenes:
            by_kind.setdefault(s["kind"], []).append(s)
        for kind in ("dispatch", "prompt_exchange"):
            said = by_kind[kind]
            self.assertGreaterEqual(len(said), 2, kind)
            self.assertEqual(said[0]["spoken"], said[0]["narration_long"], kind)
            self.assertEqual(said[1]["spoken"], said[1]["narration"], kind)
            self.assertLess(len(said[1]["spoken"].split()),
                            len(said[0]["spoken"].split()), kind)

    def test_the_opening_and_the_close_are_always_explained_in_full(self):
        markers = _markers() + [_marker(8, 118, "run_completed",
                                        payload={"progressive_tokens": 42000})]
        scenes = dtl.build_scenes(markers, {"title": "A recorded run"})
        dtl.choose_narration(scenes, None, mode="explain")
        self.assertEqual(scenes[0]["spoken"], scenes[0]["narration_long"])
        self.assertEqual(scenes[-1]["spoken"], scenes[-1]["narration_long"])

    def test_explain_is_never_trimmed_to_meet_a_target(self):
        scenes_a, scenes_b = _scenes(), _scenes()
        dtl.choose_narration(scenes_a, 20, mode="explain")
        dtl.choose_narration(scenes_b, 6000, mode="explain")
        self.assertEqual([s["spoken"] for s in scenes_a], [s["spoken"] for s in scenes_b])

    def test_token_counts_are_spoken_as_words_not_as_notation(self):
        self.assertEqual(dtl._spoken_count(43400), "roughly 43 thousand")
        self.assertEqual(dtl._spoken_count(750), "about 750")
        self.assertNotIn("k", dtl._spoken_count(43400))


class FitToNarrationTestCase(unittest.TestCase):
    def setUp(self):
        self.pace = ded.Pace("relaxed")
        self.scenes = _scenes()
        self.spans = ded.scene_spans(self.scenes, _markers(), _iso(0), 120)
        self.segments = ded.plan_edit(self.spans, self.pace)

    def _need(self, seconds: float) -> dict:
        covered = {id(s["scene"]) for s in self.segments}
        return {i: seconds for i, s in enumerate(self.scenes) if id(s) in covered}

    def test_every_beat_gets_at_least_the_time_its_sentence_needs(self):
        need = self._need(30.0)
        ded.fit_narration(self.segments, self.scenes, need, self.pace)
        for i, scene in enumerate(self.scenes):
            if i not in need:
                continue
            have = sum(s["duration"] for s in self.segments if s["scene"] is scene)
            self.assertGreaterEqual(have, need[i], self.scenes[i]["kind"])

    def test_the_picture_keeps_moving_before_anything_is_held(self):
        report = ded.fit_narration(self.segments, self.scenes, self._need(24.0), self.pace)
        self.assertGreater(report["beats_uncondensed"] + report["beats_slowed"], 0)
        for s in self.segments:
            self.assertGreaterEqual(s["speed"], self.pace.MIN_SPEED - 1e-9)
        # a beat with plenty of footage is filled by playing more of it, not by freezing
        thinking = next(sc for sc in self.scenes if sc["kind"] == "prompt_exchange")
        segs = [s for s in self.segments if s["scene"] is thinking]
        self.assertEqual(sum(s.get("hold", 0.0) for s in segs), 0.0)

    def test_a_beat_with_no_footage_left_is_held_on_its_last_frame(self):
        report = ded.fit_narration(self.segments, self.scenes, self._need(90.0), self.pace)
        self.assertGreater(report["beats_held"], 0)
        held = [s for s in self.segments if s.get("hold", 0)]
        self.assertTrue(held)
        for s in held:
            self.assertGreater(s["duration"], (s["out"] - s["in"]) / s["speed"])

    def test_segments_stay_laid_end_to_end_after_fitting(self):
        ded.fit_narration(self.segments, self.scenes, self._need(30.0), self.pace)
        t = 0.0
        for s in self.segments:
            self.assertAlmostEqual(s["at"], t, places=6)
            t += s["duration"]

    def test_narration_that_already_fits_changes_nothing(self):
        before = [(s["speed"], s["duration"]) for s in self.segments]
        report = ded.fit_narration(self.segments, self.scenes, self._need(0.5), self.pace)
        self.assertEqual(report, {"beats_uncondensed": 0, "beats_slowed": 0, "beats_held": 0})
        self.assertEqual([(s["speed"], s["duration"]) for s in self.segments], before)


class RebalanceTestCase(unittest.TestCase):
    def test_a_starved_beat_borrows_from_the_one_after_it(self):
        spans = [{"scene": {"kind": "a"}, "start": 0.0, "end": 0.3},
                 {"scene": {"kind": "b"}, "start": 0.3, "end": 40.0}]
        report = ded.rebalance_spans(spans, 8.0)
        self.assertEqual(report["spans_rebalanced"], 1)
        self.assertAlmostEqual(spans[0]["end"], 8.0)
        self.assertAlmostEqual(spans[1]["start"], 8.0)
        self.assertAlmostEqual(spans[1]["end"], 40.0)     # the run of footage is unbroken

    def test_a_beat_is_never_robbed_to_feed_its_predecessor(self):
        spans = [{"scene": {"kind": "a"}, "start": 0.0, "end": 0.3},
                 {"scene": {"kind": "b"}, "start": 0.3, "end": 5.0}]
        ded.rebalance_spans(spans, 8.0)
        self.assertAlmostEqual(spans[1]["end"] - spans[1]["start"], 4.7)
        self.assertAlmostEqual(spans[0]["end"], 0.3)

    def test_the_last_beat_borrows_from_nothing(self):
        spans = [{"scene": {"kind": "a"}, "start": 0.0, "end": 0.3}]
        self.assertEqual(ded.rebalance_spans(spans, 8.0)["spans_rebalanced"], 0)
        self.assertAlmostEqual(spans[0]["end"], 0.3)


class SpeechRateTestCase(unittest.TestCase):
    def test_the_default_delivery_is_slower_than_the_engine_default(self):
        self.assertLess(tts.DEFAULT_SPEECH_RATE, 0)
        self.assertLess(tts._wpm(None), tts.BASE_WPM)
        self.assertLess(tts._wpm(-3), tts._wpm(0))
        self.assertGreater(tts._wpm(3), tts._wpm(0))

    def test_the_rate_is_clamped_and_survives_nonsense(self):
        self.assertEqual(tts._rate(99), 6)
        self.assertEqual(tts._rate(-99), -6)
        self.assertEqual(tts._rate("not a number"), tts.DEFAULT_SPEECH_RATE)
        self.assertEqual(tts._rate(None), tts.DEFAULT_SPEECH_RATE)
        self.assertGreaterEqual(tts._wpm(-6), 90)

    def test_the_rate_reaches_the_engine(self):
        seen = {}

        def fake(lines, work, voice, ffmpeg, rate=None):
            seen["rate"] = rate
            return [{"index": lines[0][0], "path": "x.wav", "duration_ms": 1000}]

        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.dict(tts.ENGINE_FN, {"sapi": fake}, clear=False):
            out = tts.synthesize([(0, "hello")], Path(tmp), engine="sapi", rate=-4)
        self.assertEqual(out["engine"], "sapi")
        self.assertEqual(seen["rate"], -4)


class FiltergraphPacingTestCase(unittest.TestCase):
    def test_a_hold_is_preceded_by_a_constant_frame_rate(self):
        """A screen capture is variable frame rate, and `tpad` silently clones nothing
        without a cadence to clone at -- which cost this pipeline a whole build to find."""
        segments = [{"scene": {"kind": "a"}, "in": 0.0, "out": 4.0, "speed": 0.5,
                     "role": "beat", "hold": 6.0, "duration": 14.0, "at": 0.0}]
        g = ded.build_filtergraph(segments, capture_size=(1280, 720), fps=30, has_intro=False,
                                  has_outro=False, intro_idx=2, outro_idx=3, overlay_idx=1)
        line = next(l for l in g.splitlines() if l.startswith("[0:v]trim"))
        self.assertIn("tpad=stop_mode=clone:stop_duration=6.000", line)
        self.assertLess(line.index("fps=30"), line.index("tpad"))
        self.assertLess(line.index("setpts"), line.index("fps=30"))

    def test_the_cards_follow_the_pace(self):
        segments = [{"scene": {"kind": "a"}, "in": 0.0, "out": 4.0, "speed": 1.0,
                     "role": "beat", "duration": 4.0, "at": 0.0}]
        g = ded.build_filtergraph(segments, capture_size=(1280, 720), fps=30, has_intro=True,
                                  has_outro=True, intro_idx=2, outro_idx=3, overlay_idx=1,
                                  intro_s=9.0, outro_s=13.0)
        self.assertIn("fade=t=out:st=8.40", g)
        self.assertIn("fade=t=out:st=12.40", g)


if __name__ == "__main__":
    unittest.main()
