"""Regression tests for the repositoryWrites scope-explosion defect (ON-165).

`agents/omn-qa/manifest.yaml` once declared `repositoryWrites.scope` as a YAML
prose string; `list(prose)` in the dispatch-envelope assembly exploded it into
~200 single-character glob entries in every omn-qa dispatch. These tests pin
the guard (`_glob_list`), the phase-conditional grant (`scopePhases` /
`_repo_write_scope_applies`), the fixed manifest itself, and the authoring-time
check (`verify_manifests.py` M1) that catches the mistake class at edit time.

They import the framework's own runtime from `.claude/runtime`, the same tree
`verify_registry_coverage.py` verifies, so they exercise the real code path,
not a stub.
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402
import verify_manifests as vm   # noqa: E402


class GlobListTests(unittest.TestCase):
    def test_list_passes_through(self):
        self.assertEqual(fr._glob_list(["**", "src/**"]), ["**", "src/**"])

    def test_prose_string_is_never_exploded(self):
        prose = "automated test files only, and only in one phase"
        self.assertEqual(fr._glob_list(prose), [])

    def test_none_and_scalars_declare_nothing(self):
        self.assertEqual(fr._glob_list(None), [])
        self.assertEqual(fr._glob_list(42), [])
        self.assertEqual(fr._glob_list({"a": 1}), [])

    def test_empty_list_stays_empty(self):
        self.assertEqual(fr._glob_list([]), [])


class ScopePhasesTests(unittest.TestCase):
    def test_absent_scope_phases_applies_everywhere(self):
        self.assertTrue(fr._repo_write_scope_applies({}, "fix-bug",
                                                     "fix-implementation"))

    def test_named_phase_applies(self):
        rw = {"scopePhases": ["refactor/safety-net-establishment"]}
        self.assertTrue(fr._repo_write_scope_applies(
            rw, "refactor", "safety-net-establishment"))

    def test_other_phase_does_not_apply(self):
        rw = {"scopePhases": ["refactor/safety-net-establishment"]}
        self.assertFalse(fr._repo_write_scope_applies(
            rw, "refactor", "behavioral-validation"))
        self.assertFalse(fr._repo_write_scope_applies(
            rw, "fix-bug", "regression-validation"))


class RealManifestTests(unittest.TestCase):
    def qa_repo_writes(self) -> dict:
        manifest = fr.load_yaml("agents/omn-qa/manifest.yaml")
        return manifest["authorityScope"]["repositoryWrites"]

    def test_omn_qa_scope_is_a_list(self):
        rw = self.qa_repo_writes()
        self.assertTrue(rw["allowed"])
        self.assertIsInstance(rw["scope"], list)
        self.assertTrue(rw["scope"])
        for pattern in rw["scope"]:
            self.assertIsInstance(pattern, str)
            # A glob pattern, not a prose sentence.
            self.assertNotIn(" ", pattern)

    def test_omn_qa_grant_is_phase_conditional(self):
        rw = self.qa_repo_writes()
        self.assertEqual(rw["scopePhases"], ["refactor/safety-net-establishment"])

    def test_omn_qa_scope_never_contains_single_character_entries(self):
        # The exact regression: exploded prose produced entries like "a", "u".
        rw = self.qa_repo_writes()
        scope = fr._glob_list(rw.get("scope"))
        self.assertTrue(all(len(p) > 1 for p in scope), scope)
        self.assertLess(len(scope), 20)

    def test_write_scope_empty_outside_safety_net_phase(self):
        rw = self.qa_repo_writes()
        allowed = bool(rw.get("allowed"))
        for wf, phase, expected in (
                ("refactor", "safety-net-establishment", True),
                ("refactor", "behavioral-validation", False),
                ("fix-bug", "regression-validation", False)):
            applies = allowed and fr._repo_write_scope_applies(rw, wf, phase)
            write_scope = fr._glob_list(rw.get("scope")) if applies else []
            self.assertEqual(bool(write_scope), expected, (wf, phase))


class VerifyManifestsTests(unittest.TestCase):
    def test_m1_passes_on_this_repo(self):
        res = vm.Result()
        vm.m1_repository_writes_are_lists(res)
        self.assertTrue(res.passed, res.checks)

    def test_m1_rejects_prose_scope(self):
        self.assertFalse(vm.repository_writes_shape_ok(
            {"allowed": True,
             "scope": "automated test files only, in one phase"}))

    def test_m1_rejects_absent_scope_on_allowed_grant(self):
        self.assertFalse(vm.repository_writes_shape_ok({"allowed": True}))

    def test_m1_rejects_prose_excluded(self):
        self.assertFalse(vm.repository_writes_shape_ok(
            {"allowed": True, "scope": ["**"], "excluded": "runs and proposals"}))

    def test_m1_accepts_list_shapes(self):
        self.assertTrue(vm.repository_writes_shape_ok(
            {"allowed": True, "scope": ["**"], "excluded": ["runs/**"]}))
        self.assertTrue(vm.repository_writes_shape_ok(
            {"allowed": True, "scope": ["**"]}))

    def test_m2_passes_on_this_repo(self):
        res = vm.Result()
        vm.m2_examples_cross_referenced(res)
        self.assertTrue(res.passed, res.checks)

    def test_script_exits_zero_on_this_repo(self):
        proc = subprocess.run(
            [sys.executable, str(RUNTIME / "verify_manifests.py")],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class ReportSubcommandTests(unittest.TestCase):
    """`framework_runtime.py report` against this repo's own committed ON-165 run."""

    RUN_ID = "run-27e36c138498"

    def test_report_renders_committed_run(self):
        if not (REPO / ".claude" / "runs" / self.RUN_ID).is_dir():
            self.skipTest(f"committed run {self.RUN_ID} not present")
        proc = subprocess.run(
            [sys.executable, str(RUNTIME / "framework_runtime.py"),
             "report", "--run-id", self.RUN_ID],
            capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = proc.stdout
        for section in ("## Run", "## Agent Activity", "## Gate Decisions",
                        "## Timeline"):
            self.assertIn(section, out)
        # Every phase row names its agent; every gate row names its decider.
        self.assertIn("`omn-dev-1-implement`", out)
        self.assertIn("`fix-implementation`", out)
        self.assertIn("| approved |", out)


if __name__ == "__main__":
    unittest.main()
