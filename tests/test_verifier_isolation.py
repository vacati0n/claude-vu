"""Verifiers that execute the runtime write into disposable copies, never into run evidence.

* `verify_multi_phase.py` check `M14` replays the runtime against a committed run. It does so in
  a disposable copy of the framework tree, so the committed run `run-c5a8d50d3238` is left
  byte-identical; the copy is removed even when a replay command raises; and a replay that
  produces a real side effect -- here, an extra transition written into the copy -- still
  fails `M14`, because the fingerprint is taken from the copy the replay ran in.
* `verify_recovery.py` removes the inputs and runs it injected even when a scenario raises.
  That case runs in a copy of the framework tree held in a temp directory, with the first
  scenario replaced in a child process by one that plans a run and then raises.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
CLAUDE = REPO / ".claude"
sys.path.insert(0, str(CLAUDE / "runtime"))

import verify_multi_phase as vmp   # noqa: E402
import verify_self_hosting as vsh  # noqa: E402

RUN_ID = "run-c5a8d50d3238"
RUN_DIR = CLAUDE / "runs" / RUN_ID


def digest_tree(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


class _TrackScratch:
    """Wraps `scratch_tree` so a test can see which copies were made."""

    def __init__(self):
        self.made = []
        self._real = vsh.scratch_tree

    def __call__(self, *args, **kwargs):
        root = self._real(*args, **kwargs)
        self.made.append(root)
        return root


class M14ReplaysInADisposableCopy(unittest.TestCase):

    def setUp(self):
        self.before = digest_tree(RUN_DIR)
        self.track = _TrackScratch()
        patcher = mock.patch.object(vsh, "scratch_tree", self.track)
        patcher.start()
        self.addCleanup(patcher.stop)

    def assert_run_untouched_and_copies_removed(self):
        self.assertEqual(digest_tree(RUN_DIR), self.before,
                         f"{RUN_ID} changed under the M14 replay")
        self.assertTrue(self.track.made, "M14 made no disposable copy")
        for root in self.track.made:
            self.assertFalse(root.exists(), f"disposable copy {root} was left behind")

    def m14(self, result):
        return next(c for c in result.checks if c["id"] == "M14")

    def test_replay_leaves_the_committed_run_byte_identical(self):
        check = self.m14(vmp.run_checks(RUN_DIR, replay=True))
        self.assertEqual(check["result"], "PASS", check["detail"])
        self.assertIn("disposable copy", check["detail"])
        self.assert_run_untouched_and_copies_removed()

    def test_a_duplicated_transition_in_the_copy_still_fails_m14(self):
        real_run = subprocess.run

        def replay_with_side_effect(argv, *args, **kwargs):
            done = real_run(argv, *args, **kwargs)
            if isinstance(argv, list) and len(argv) > 2 and argv[2] == "plan":
                # argv[1] is the copied runtime, so this writes only into the copy.
                state = Path(argv[1]).parent.parent / "runs" / RUN_ID / "state.json"
                data = json.loads(state.read_text(encoding="utf-8"))
                data["transitions"].append(dict(data["transitions"][-1]))
                state.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return done

        with mock.patch.object(vmp.subprocess, "run", side_effect=replay_with_side_effect):
            check = self.m14(vmp.run_checks(RUN_DIR, replay=True))
        self.assertEqual(check["result"], "FAIL", check["detail"])
        self.assertIn("transitions", check["detail"])
        self.assert_run_untouched_and_copies_removed()

    def test_a_rewritten_artifact_in_the_copy_still_fails_m14(self):
        real_run = subprocess.run

        def replay_with_artifact_rewrite(argv, *args, **kwargs):
            done = real_run(argv, *args, **kwargs)
            if isinstance(argv, list) and len(argv) > 2 and argv[2] == "plan":
                # Artifact paths resolve against the copied framework root, never the original.
                claude_copy = Path(argv[1]).parent.parent
                state = claude_copy / "runs" / RUN_ID / "state.json"
                items = json.loads(state.read_text(encoding="utf-8"))["work_items"].values()
                path = next(i["completion"]["artifact_path"] for i in items
                            if (i.get("completion") or {}).get("artifact_path"))
                artifact = claude_copy / path
                artifact.write_text(artifact.read_text(encoding="utf-8") + "\nrewritten\n",
                                    encoding="utf-8")
            return done

        with mock.patch.object(vmp.subprocess, "run", side_effect=replay_with_artifact_rewrite):
            check = self.m14(vmp.run_checks(RUN_DIR, replay=True))
        self.assertEqual(check["result"], "FAIL", check["detail"])
        self.assertIn("artifact_digests", check["detail"])
        self.assert_run_untouched_and_copies_removed()

    def test_the_copy_is_removed_when_a_replay_command_raises(self):
        real_run = subprocess.run

        def failing_replay(argv, *args, **kwargs):
            if isinstance(argv, list) and str(argv[1]).endswith("framework_runtime.py"):
                raise RuntimeError("induced replay failure")
            return real_run(argv, *args, **kwargs)

        with mock.patch.object(vmp.subprocess, "run", side_effect=failing_replay):
            with self.assertRaises(RuntimeError):
                vmp.run_checks(RUN_DIR, replay=True)
        self.assert_run_untouched_and_copies_removed()


CHILD = textwrap.dedent("""
    import sys
    sys.path.insert(0, sys.argv[1])
    import verify_recovery as vr

    def raising_scenario():
        vr.plan(vr.write_input("repaired", "induced: raises after planning"))
        raise RuntimeError("induced scenario failure")

    vr.scenario_a = raising_scenario
    sys.argv = ["verify_recovery.py"]
    try:
        vr.main()
    except RuntimeError as exc:
        print("RAISED:", exc)
        sys.exit(3)
    sys.exit(0)
""")


class RecoveryCleansUpWhenAScenarioRaises(unittest.TestCase):

    def setUp(self):
        self.root = vsh.scratch_tree("recovery-test-", keep_run=RUN_ID)
        self.addCleanup(vsh.remove_tree, self.root)
        self.runs = self.root / ".claude" / "runs"

    def test_injected_inputs_and_runs_are_removed(self):
        before = sorted(p.relative_to(self.runs).as_posix() for p in self.runs.rglob("*"))
        done = subprocess.run([sys.executable, "-c", CHILD,
                               str(self.root / ".claude" / "runtime")],
                              cwd=str(self.root), capture_output=True, text=True)
        self.assertEqual(done.returncode, 3, done.stdout + done.stderr)
        self.assertIn("RAISED: induced scenario failure", done.stdout)
        self.assertIn("injected runs and inputs removed", done.stdout)
        after = sorted(p.relative_to(self.runs).as_posix() for p in self.runs.rglob("*"))
        self.assertEqual(after, before, "injected inputs or runs were left behind")


if __name__ == "__main__":
    unittest.main()
