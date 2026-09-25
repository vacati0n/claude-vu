import unittest

from app.report import week_label, render_header


class WeekLabelTests(unittest.TestCase):
    def test_returns_iso_week_label(self):
        self.assertEqual(week_label("2026-09-15"), "2026-W38")

    def test_handles_iso_year_boundary(self):
        # 2021-01-01 falls in ISO week 53 of 2020: the ISO year differs
        # from the calendar year at this boundary.
        self.assertEqual(week_label("2021-01-01"), "2020-W53")

    def test_rejects_garbage_like_parse_iso_date(self):
        with self.assertRaises(ValueError):
            week_label("15/09/2026")


class RenderHeaderTests(unittest.TestCase):
    def test_includes_week_label(self):
        self.assertEqual(
            render_header("2026-09-15"),
            "Sales report for 2026-09-15 (2026-W38)",
        )
