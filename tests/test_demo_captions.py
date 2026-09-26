"""Tests for the captions, the subtitle file, and the narration script.

Everything the narrator says is also shown on screen as it is said, written out as a standard
subtitle file, and written out again as a script a presenter can read beforehand. All three
come from the same source -- the lines actually recorded, with the durations the speech
engine actually produced -- so they cannot drift apart.

What is pinned here:
  * a line is split where a reader would pause, never mid-phrase, and never into a cue too
    short to read;
  * cues share their line's duration in proportion to how long each takes to say, cover it
    exactly, and never overlap;
  * a cue wraps into two balanced lines rather than one long and one short;
  * the overlay track is cut wherever the caption changes, and only there;
  * the subtitle file is well-formed SRT with ordered, non-overlapping, ascending stamps;
  * the script carries every spoken line with the time it is heard.
"""

from __future__ import annotations

import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from demo import captions as cap        # noqa: E402
from demo import editor as ded          # noqa: E402
from demo import overlays as dov        # noqa: E402
from demo.context import DEFAULT_OPTIONS  # noqa: E402

LINE = ("The framework is now handing the scope and acceptance stage to the product owner. "
        "Before it does, it writes down exactly which documents that specialist is allowed "
        "to read, 13 of them, and takes a fingerprint of each one, so there is a record of "
        "what it was looking at that cannot be changed afterwards.")


class CueSplittingTestCase(unittest.TestCase):
    def test_a_line_is_split_where_a_reader_would_pause(self):
        cues = cap.split_cues(LINE)
        self.assertGreater(len(cues), 2)
        self.assertEqual(" ".join(cues).replace("  ", " "), " ".join(LINE.split()))
        for c in cues[:-1]:
            self.assertTrue(c[-1] in ".,;:!?" or c.endswith("and") or c.endswith("but"),
                            f"cue ends mid-phrase: {c!r}")

    def test_no_cue_dangles_on_a_relative_pronoun(self):
        """Breaking after "which" or "that" reads worse than a longer caption."""
        for c in cap.split_cues(LINE):
            self.assertFalse(c.rstrip().endswith(("which", "that", "of", "the", "a", "to")),
                             f"cue dangles: {c!r}")

    def test_cues_stay_within_the_size_a_caption_band_can_show(self):
        for text in (LINE, "Short one.", "word " * 200):
            for c in cap.split_cues(text):
                self.assertLessEqual(len(cap.wrap_cue(c, dov.CAPTION_WIDTH)), 2, c)

    def test_an_empty_line_produces_nothing(self):
        self.assertEqual(cap.split_cues(""), [])
        self.assertEqual(cap.split_cues(None), [])
        self.assertEqual(cap.time_cues("", 0, 10), [])

    def test_a_short_line_is_one_cue(self):
        self.assertEqual(cap.split_cues("Validation passed."), ["Validation passed."])


class CueTimingTestCase(unittest.TestCase):
    def test_cues_cover_the_spoken_line_exactly_and_never_overlap(self):
        cues = cap.time_cues(LINE, 10.0, 24.0)
        self.assertAlmostEqual(cues[0]["start"], 10.0, places=6)
        self.assertAlmostEqual(cues[-1]["end"], 34.0, places=3)
        for a, b in zip(cues, cues[1:]):
            self.assertAlmostEqual(a["end"], b["start"], places=6)
            self.assertGreater(a["end"], a["start"])

    def test_a_longer_cue_is_held_longer(self):
        cues = cap.time_cues(LINE, 0.0, 30.0)
        spans = [(c["end"] - c["start"], len(c["text"].split())) for c in cues]
        longest = max(spans, key=lambda s: s[1])
        shortest = min(spans, key=lambda s: s[1])
        self.assertGreater(longest[0], shortest[0])

    def test_a_cue_is_never_flashed_too_briefly_to_read(self):
        for c in cap.time_cues(LINE, 0.0, 1.0):
            self.assertGreaterEqual(c["end"] - c["start"], cap.MIN_CUE_SECONDS - 1e-9)

    def test_wrapping_balances_the_two_lines(self):
        lines = cap.wrap_cue("A person has now decided this checkpoint and the answer "
                             "is approved", 52)
        self.assertEqual(len(lines), 2)
        self.assertLess(abs(len(lines[0]) - len(lines[1])), 26)
        self.assertEqual(" ".join(lines).split(),
                         "A person has now decided this checkpoint and the answer "
                         "is approved".split())


class OverlaySlicingTestCase(unittest.TestCase):
    def _seg(self, at, duration):
        return {"scene": {"kind": "dispatch"}, "in": 0.0, "out": duration,
                "speed": 1.0, "role": "beat", "at": at, "duration": duration}

    def test_a_segment_is_cut_where_the_caption_changes(self):
        # the opening card pushes the body along by `offset`, so this segment occupies
        # 5.0 to 17.0 of the finished film: two cues, then silence to the end of the beat
        seg = self._seg(0.0, 12.0)
        cues = [{"start": 5.0, "end": 9.0, "text": "first"},
                {"start": 9.0, "end": 14.0, "text": "second"}]
        slices = ded._caption_slices(seg, cues, offset=5.0)
        self.assertAlmostEqual(sum(d for d, _ in slices), seg["duration"], places=6)
        self.assertEqual([t for _, t in slices], ["first", "second", None])
        self.assertEqual([round(d, 3) for d, _ in slices], [4.0, 5.0, 3.0])

    def test_a_caption_that_starts_after_the_beat_leaves_a_silent_head(self):
        seg = self._seg(0.0, 12.0)
        cues = [{"start": 8.0, "end": 12.0, "text": "later"}]
        slices = ded._caption_slices(seg, cues, offset=0.0)
        self.assertEqual([t for _, t in slices], [None, "later"])

    def test_a_segment_with_nothing_spoken_over_it_is_left_whole(self):
        slices = ded._caption_slices(self._seg(0.0, 6.0), [], offset=0.0)
        self.assertEqual(slices, [(6.0, None)])

    def test_slices_always_sum_to_the_segment(self):
        cues = cap.time_cues(LINE, 3.0, 20.0)
        for at, duration in ((0.0, 4.0), (2.0, 9.5), (11.0, 30.0)):
            slices = ded._caption_slices(self._seg(at, duration), cues, offset=0.0)
            self.assertAlmostEqual(sum(d for d, _ in slices), duration, places=6)
            self.assertTrue(all(d > 0 for d, _ in slices))

    @unittest.skipUnless(dov.has_pil(), "Pillow not installed")
    def test_the_caption_is_drawn_into_the_frame(self):
        scene = {"kind": "dispatch", "title": "Handing the work over", "subtitle": "x",
                 "phase": "p1", "projection": {"phases": [], "gates": {}}}
        plain = dov.beat_overlay(scene, run_id="r", command="implement",
                                 capture_size=(1280, 720), fraction=0.5)
        with_caption = dov.beat_overlay(scene, run_id="r", command="implement",
                                        capture_size=(1280, 720), fraction=0.5,
                                        caption="The framework is now handing this stage "
                                                "to the product owner.")
        self.assertEqual(with_caption.size, dov.CANVAS)
        band = (dov.LOWER_BOX[0], dov.LOWER_BOX[1] + 90,
                dov.LOWER_BOX[0] + dov.LOWER_BOX[2], dov.LOWER_BOX[1] + 180)
        self.assertNotEqual(list(plain.crop(band).getdata()),
                            list(with_caption.crop(band).getdata()))

    @unittest.skipUnless(dov.has_pil(), "Pillow not installed")
    def test_the_caption_band_never_covers_the_footage(self):
        x, y, w, h = dov._video_target((1920, 1032))
        self.assertLessEqual(y + h, dov.LOWER_BOX[1])
        self.assertLessEqual(dov.LOWER_BOX[1] + dov.LOWER_BOX[3], dov.CANVAS[1])


class SubtitleFileTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-cap-"))
        self.cues = cap.time_cues(LINE, 1.5, 22.0) + cap.time_cues("And then this.", 30.0, 4.0)

    def test_the_subtitle_file_is_well_formed_and_ordered(self):
        path = cap.write_srt(self.cues, self.tmp / "out.srt")
        text = path.read_text(encoding="utf-8")
        blocks = [b for b in text.split("\n\n") if b.strip()]
        self.assertEqual(len(blocks), len(self.cues))
        stamps = []
        for i, block in enumerate(blocks, 1):
            lines = block.strip().splitlines()
            self.assertEqual(lines[0], str(i))
            m = re.fullmatch(r"(\d\d:\d\d:\d\d,\d\d\d) --> (\d\d:\d\d:\d\d,\d\d\d)", lines[1])
            self.assertIsNotNone(m, lines[1])
            stamps.append(m.groups())
            self.assertTrue(lines[2:])
            self.assertLessEqual(len(lines[2:]), 2)
        for (s, e), (ns, _) in zip(stamps, stamps[1:]):
            self.assertLess(s, e)
            self.assertLessEqual(e, ns)

    def test_the_clock_is_hours_minutes_seconds_milliseconds(self):
        self.assertEqual(cap._srt_clock(0), "00:00:00,000")
        self.assertEqual(cap._srt_clock(3661.5), "01:01:01,500")
        self.assertEqual(cap._srt_clock(-5), "00:00:00,000")


class ScriptTestCase(unittest.TestCase):
    def test_the_script_carries_every_spoken_line_with_its_time(self):
        scenes = [{"kind": "opening", "title": "The opening", "subtitle": "six phases"},
                  {"kind": "dispatch", "title": "Handing the work over", "subtitle": "po"},
                  {"kind": "note", "title": "Never spoken", "subtitle": ""}]
        spoken = {0: {"at": 1.5, "seconds": 20.0, "text": "Welcome to the demonstration."},
                  1: {"at": 95.0, "seconds": 18.0, "text": LINE}}
        with tempfile.TemporaryDirectory() as tmp:
            path = cap.write_script(scenes, spoken, Path(tmp) / "script.md",
                                    title="A recorded run", run_id="run-x",
                                    total_seconds=336.0, source="2:02 of screen recording")
            text = path.read_text(encoding="utf-8")
        self.assertIn("# A recorded run", text)
        self.assertIn("run-x", text)
        self.assertIn("5:36", text)                       # running time, not seconds
        self.assertIn("## 0:01  The opening", text)
        self.assertIn("## 1:35  Handing the work over", text)
        self.assertIn("Welcome to the demonstration.", text)
        self.assertIn(LINE, text)
        self.assertNotIn("Never spoken", text)            # a beat with no line is omitted


class DefaultsTestCase(unittest.TestCase):
    def test_captions_are_on_by_default(self):
        self.assertTrue(DEFAULT_OPTIONS["captions"])


if __name__ == "__main__":
    unittest.main()
