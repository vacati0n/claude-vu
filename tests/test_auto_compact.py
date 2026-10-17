"""Tests for the session auto-compact budget: `.claude/settings.json` sets the Claude Code
auto-compact window to an absolute 100,000 tokens, so a session in the framework checkout
compacts once its context passes 100k instead of near the model's full window (about 967k on
a 1M-context model).

The threshold is set through `CLAUDE_CODE_AUTO_COMPACT_WINDOW`, the only documented control
that takes an absolute token count. `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` is a percentage of the
window and would mean a different token count on every model, so it must not be used for this.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLAUDE = REPO / ".claude"
SETTINGS = CLAUDE / "settings.json"
sys.path.insert(0, str(REPO))

from omn_agent.source import enumerate_payload  # noqa: E402

AUTO_COMPACT_TOKENS = 100_000
WINDOW_VAR = "CLAUDE_CODE_AUTO_COMPACT_WINDOW"
# Bounds documented by Claude Code for the window variable.
WINDOW_MIN, WINDOW_MAX = 100_000, 1_000_000


class AutoCompactSettingsTestCase(unittest.TestCase):
    def setUp(self):
        self.settings = json.loads(SETTINGS.read_text(encoding="utf-8"))

    def test_window_is_an_absolute_100k_tokens(self):
        value = self.settings["env"][WINDOW_VAR]
        # Settings `env` values are strings; Claude Code reads a plain integer only, and a
        # suffixed value such as "100k" would read as 100 and clamp.
        self.assertIsInstance(value, str)
        self.assertTrue(value.isdigit(), value)
        self.assertEqual(int(value), AUTO_COMPACT_TOKENS)
        self.assertGreaterEqual(int(value), WINDOW_MIN)
        self.assertLessEqual(int(value), WINDOW_MAX)

    def test_auto_compact_is_not_disabled_or_overridden(self):
        self.assertNotEqual(self.settings.get("autoCompactEnabled"), False)
        self.assertNotIn("CLAUDE_AUTOCOMPACT_PCT_OVERRIDE", self.settings.get("env", {}))
        self.assertNotIn("DISABLE_AUTO_COMPACT", self.settings.get("env", {}))
        self.assertNotIn("DISABLE_COMPACT", self.settings.get("env", {}))

    def test_host_settings_are_not_part_of_the_installed_payload(self):
        # The settings govern the framework's own checkout; the installer must not copy them
        # into `.omn-agent/`, where Claude Code would never read them.
        self.assertNotIn("settings.json", enumerate_payload(CLAUDE))


if __name__ == "__main__":
    unittest.main()
