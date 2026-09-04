"""Tests for `omn-agent run --show`'s `--watch`/`--json`/`--no-color` additions.

These live in `omn_agent/runner.py` and `omn_agent/cli.py` (unlike the tree/icon
rendering itself, which is tested directly in `tests/test_framework_runtime_render.py`
against the installed `framework_runtime.py`). Two things need covering here that a
full CLI round-trip cannot exercise safely:

* `--watch` polls forever until Ctrl+C, so it is tested by calling `runner._watch`
  directly with an injected `sleep_fn` and a `max_iterations` bound -- never through
  `cli.main`, which would hang.
* whether `--color`/`--no-color` gets forwarded to the runtime process depends on
  *this* process's real stdout, which `_invoke`'s `capture_output=True` pipe hides from
  the child -- so the decision has to be made in `runner._show_argv` against the
  parent's own `sys.stdout.isatty()`, simulated here by swapping in a stream whose
  `isatty()` is controlled.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from omn_agent import cli, runner
from omn_agent.common import ExitCode, OmnError

from test_omn_agent import SOURCE_FILES, make_ticket, fake_transport
from omn_agent import tickets as tickets_mod

STATUS_ECHO_STUB = '''\
"""Runtime stand-in that reports which flags a `status` invocation received, so
runner.py's flag-forwarding logic can be checked without a real framework runtime."""
import sys


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "plan":
        print("Run run-abcdef123456  (implement-feature v1)  run_status=active")
        return 0
    if cmd == "status":
        print("STATUS-ARGV " + " ".join(args[1:]))
        return 0
    print(f"ok {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


class _IsattyStringIO(io.StringIO):
    def __init__(self, *, isatty):
        super().__init__()
        self._isatty = isatty

    def isatty(self):
        return self._isatty


class ShowArgvUnitTestCase(unittest.TestCase):
    """`_show_argv` in isolation: no subprocess, no filesystem."""

    def _args(self, *, json=False, no_color=False):
        return type("Args", (), {"json": json, "no_color": no_color})()

    def test_json_wins_and_carries_no_color_flags(self):
        argv = runner._show_argv("run-1", self._args(json=True))
        self.assertEqual(argv, ["status", "--run-id", "run-1", "--json"])

    def test_no_color_flag_is_forwarded(self):
        with mock.patch.object(runner.sys, "stdout", _IsattyStringIO(isatty=True)):
            argv = runner._show_argv("run-1", self._args(no_color=True))
        self.assertIn("--no-color", argv)
        self.assertNotIn("--color", argv)

    def test_real_tty_forwards_color(self):
        with mock.patch.object(runner.sys, "stdout", _IsattyStringIO(isatty=True)):
            argv = runner._show_argv("run-1", self._args())
        self.assertIn("--color", argv)

    def test_non_tty_forwards_neither_flag(self):
        with mock.patch.object(runner.sys, "stdout", _IsattyStringIO(isatty=False)):
            argv = runner._show_argv("run-1", self._args())
        self.assertNotIn("--color", argv)
        self.assertNotIn("--no-color", argv)


class WatchLoopUnitTestCase(unittest.TestCase):
    """`_watch` polls `status --compact` on a bounded, injected clock -- never sleeps
    for real and never calls dispatch/complete/gate."""

    def test_polls_status_repeatedly_and_stays_read_only(self):
        calls = []

        def fake_invoke(fw_dir, target, argv, report):
            calls.append(argv)
            return 0, ""

        sleeps = []
        with mock.patch.object(runner, "_invoke", fake_invoke):
            rc = runner._watch(Path("fw"), Path("target"),
                               ["status", "--run-id", "run-1"], report=mock.Mock(),
                               interval=0.01, max_iterations=3,
                               sleep_fn=sleeps.append)

        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 3)
        for argv in calls:
            self.assertEqual(argv[0], "status")
            self.assertIn("--compact", argv)
            for forbidden in ("dispatch", "complete", "gate"):
                self.assertNotIn(forbidden, argv)
        self.assertEqual(sleeps, [0.01, 0.01])  # no sleep after the final iteration

    def test_keyboard_interrupt_stops_cleanly(self):
        def fake_invoke(fw_dir, target, argv, report):
            return 0, ""

        def raise_interrupt(_interval):
            raise KeyboardInterrupt

        with mock.patch.object(runner, "_invoke", fake_invoke):
            rc = runner._watch(Path("fw"), Path("target"), ["status", "--run-id", "r"],
                               report=mock.Mock(), interval=0.01,
                               sleep_fn=raise_interrupt)
        self.assertEqual(rc, 0)


class WatchFlagValidationTestCase(unittest.TestCase):
    """The flag-combination guard runs before any target/task resolution, so it needs
    no fixture at all."""

    def _args(self, **over):
        base = dict(target="unused", key="X", approve=False, show=False, watch=False,
                   json=False, no_color=False, interval=2.0, dispatch=False,
                   complete=False, phase=None, gate=None, decision=None,
                   owner_role=None, decided_by=None, rationale=None)
        base.update(over)
        return type("Args", (), base)()

    def test_watch_without_show_is_rejected(self):
        with self.assertRaises(OmnError) as ctx:
            runner.cmd_run(self._args(watch=True))
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)

    def test_json_without_show_is_rejected(self):
        with self.assertRaises(OmnError):
            runner.cmd_run(self._args(json=True))

    def test_no_color_without_show_is_rejected(self):
        with self.assertRaises(OmnError):
            runner.cmd_run(self._args(no_color=True))

    def test_non_positive_watch_interval_is_rejected(self):
        for bad in (0, -1.5):
            with self.assertRaises(OmnError) as ctx:
                runner.cmd_run(self._args(show=True, watch=True, interval=bad))
            self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)


class ShowCliIntegrationTestCase(unittest.TestCase):
    """End-to-end through `cli.main`, against the echoing stub -- covers CLI parsing
    (`--json`/`--no-color`/`--interval` actually exist and reach `cmd_run`) without
    going anywhere near the infinite `--watch` loop."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-agent-show-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "framework-src"
        for rel, content in SOURCE_FILES.items():
            p = self.source / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        self.repo = self.tmp / "repo"
        (self.repo / ".git").mkdir(parents=True)
        self.fw = self.repo / ".omn-agent"

    def run_cli(self, *argv, isatty=False):
        out = _IsattyStringIO(isatty=isatty)
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def _materialize_run(self):
        code, out = self.run_cli("install", str(self.repo), "--source", str(self.source))
        self.assertEqual(code, ExitCode.OK, out)
        import os
        os.environ["JIRA_EMAIL"] = "dev@example.com"
        os.environ["JIRA_API_TOKEN"] = "token"
        self.addCleanup(os.environ.pop, "JIRA_EMAIL", None)
        self.addCleanup(os.environ.pop, "JIRA_API_TOKEN", None)
        self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                     "--base-url", "https://x.atlassian.net", "--project", "PROJ")
        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(self.repo)])
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = tickets_mod.cmd_tickets_sync(args, transport=fake_transport(
                [make_ticket()]))
        self.assertEqual(code, ExitCode.OK, buf.getvalue())
        code, out = self.run_cli("plan", "PROJ-1", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo), "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        # Swap in the echoing stub so `--show` reports exactly what it was asked to run.
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            STATUS_ECHO_STUB, encoding="utf-8")

    def test_show_json_forwards_json_flag(self):
        self._materialize_run()
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo),
                                 "--show", "--json")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("STATUS-ARGV", out)
        self.assertIn("--json", out)

    def test_show_no_color_forwards_no_color_flag(self):
        self._materialize_run()
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo),
                                 "--show", "--no-color", isatty=True)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("--no-color", out)

    def test_show_on_a_tty_forwards_color(self):
        self._materialize_run()
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo),
                                 "--show", isatty=True)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("--color", out)

    def test_show_piped_forwards_no_flag_and_stays_plain(self):
        self._materialize_run()
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo),
                                 "--show", isatty=False)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("STATUS-ARGV", out)
        self.assertNotIn("--color", out)
        self.assertNotIn("--no-color", out)


if __name__ == "__main__":
    unittest.main()
