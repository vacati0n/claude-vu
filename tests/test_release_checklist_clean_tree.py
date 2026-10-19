"""The release checklist leaves the working tree exactly as it found it.

`python .claude/runtime/verify_self_hosting.py --release-checklist` runs every command item of
the framework release checklist. Before each item ran in its own disposable copy, item `FR-11`
replayed the runtime in place against committed run `run-c5a8d50d3238` and rewrote its
`state.json` and `task-context.yaml` while reporting a pass.

This test runs the whole checklist from the repository root and compares the repository before
and after by file content -- every file git lists, tracked and untracked, ignored files aside --
and by `git status`, which on its own would miss a second write to a file that is already
modified or untracked. The checklist's own exit code is not asserted: `FR-05`/`FR-06` fail on
`S8` while a framework run is in flight without its change proposal, which says nothing about
the tree. What is asserted is that `S11`, the checklist's own tree-integrity check, ran and
passed. The machine record is written outside the repository.

The checklist takes several minutes; the test is skipped where git is unavailable.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CHECKLIST = [sys.executable, ".claude/runtime/verify_self_hosting.py", "--release-checklist"]


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(REPO), capture_output=True)


def _git_available() -> bool:
    try:
        return _git("rev-parse", "--is-inside-work-tree").returncode == 0
    except OSError:
        return False


def content_snapshot() -> dict:
    """Path -> sha256 for every file git lists (tracked plus untracked, not ignored)."""
    out = _git("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    assert out.returncode == 0, out.stderr
    snap = {}
    for rel in sorted({p for p in out.stdout.decode("utf-8").split("\0") if p}):
        f = REPO / rel
        snap[rel] = hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else None
    return snap


def status_lines() -> str:
    out = _git("status", "--porcelain", "--untracked-files=all")
    assert out.returncode == 0, out.stderr
    return out.stdout.decode("utf-8")


@unittest.skipUnless(_git_available(), "git is unavailable or the checkout is not a work tree")
class ReleaseChecklistLeavesTreeUnchanged(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="checklist-test-"))
        record = cls.tmp / "self-hosting.json"
        cls.snapshot_before = content_snapshot()
        cls.status_before = status_lines()
        cls.proc = subprocess.run(CHECKLIST + ["--json-out", str(record)], cwd=str(REPO),
                                  capture_output=True, text=True)
        cls.snapshot_after = content_snapshot()
        cls.status_after = status_lines()
        cls.record = (json.loads(record.read_text(encoding="utf-8"))
                      if record.exists() else None)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_every_listed_file_is_byte_identical(self):
        changed = sorted(p for p in set(self.snapshot_before) | set(self.snapshot_after)
                         if self.snapshot_before.get(p, 0) != self.snapshot_after.get(p, 0))
        self.assertEqual(changed, [], "the release checklist changed files in the repository")

    def test_git_status_is_unchanged(self):
        self.assertEqual(self.status_after, self.status_before)

    def test_s11_ran_and_passed(self):
        self.assertIsNotNone(self.record, self.proc.stdout + self.proc.stderr)
        checks = {c["id"]: c for c in self.record["checks"]}
        self.assertIn("S11", checks)
        self.assertEqual(checks["S11"]["result"], "pass", checks["S11"]["detail"])

    def test_every_command_item_ran(self):
        self.assertIsNotNone(self.record, self.proc.stdout + self.proc.stderr)
        executed = [i for i in self.record["checklist_execution"] if i["mode"] == "command"]
        self.assertTrue(executed)
        for item in executed:
            self.assertIn(item["result"], ("pass", "fail"), item["id"])
            self.assertEqual(item["copy_writes"], [], item["id"])


if __name__ == "__main__":
    unittest.main()
