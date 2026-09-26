"""Regression net for the CI verification workflow (.github/workflows/verify.yml).

The workflow is a contract-heavy artifact: branch protection binds to its stable
check names, its two verification surfaces must be located by discovery (never a
curated file list), and its environment rules (no NO_COLOR, no continue-on-error)
protect the render tests and the advisory week's visibility. These tests lock
those properties so a workflow edit that breaks the contract fails the suite
before it detaches branch protection or silently un-gates a surface.

Hermetic: the discovery expression and the verifier-assertion wrapper are
extracted from the workflow file itself and executed against this repository's
tree and against synthetic verifier scripts in temporary directories. No network,
no hosted runner required.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
WORKFLOW = REPO / ".github" / "workflows" / "verify.yml"

STABLE_CHECK_NAMES = (
    "tests-ubuntu",
    "tests-windows",
    "verifiers-ubuntu-ok",
    "verifiers-windows-ok",
)


def _load():
    text = WORKFLOW.read_text(encoding="utf-8")
    return text, yaml.safe_load(text)


def _effective(text: str) -> str:
    """The workflow with comment lines stripped: the header comment is REQUIRED
    to document the NO_COLOR / continue-on-error policy by name, so policy scans
    look only at lines that do something."""
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#"))


class WorkflowStructure(unittest.TestCase):
    def setUp(self):
        self.text, self.wf = _load()

    def test_parses_and_triggers(self):
        trig = self.wf.get(True) or self.wf.get("on")  # yaml 1.1 reads `on` as True
        self.assertIn("pull_request", trig)
        self.assertIn("push", trig)
        self.assertTrue(trig["push"].get("branches"),
                        "push trigger must be scoped to the default branch")

    def test_job_topology_and_stable_names(self):
        jobs = self.wf["jobs"]
        self.assertEqual(
            set(jobs),
            {"discover", "tests", "verifier-ubuntu", "verifier-windows",
             "verifiers-ubuntu-ok", "verifiers-windows-ok"})
        # branch protection binds to these rendered names; renaming is a
        # contract change (a renamed required check blocks every PR forever)
        self.assertEqual(jobs["tests"]["name"], "tests-${{ matrix.platform }}")
        platforms = [e["platform"]
                     for e in jobs["tests"]["strategy"]["matrix"]["include"]]
        self.assertEqual(sorted(platforms), ["ubuntu", "windows"])
        self.assertEqual(jobs["verifiers-ubuntu-ok"]["name"], "verifiers-ubuntu-ok")
        self.assertEqual(jobs["verifiers-windows-ok"]["name"], "verifiers-windows-ok")

    def test_verifier_matrix_fans_out_from_discovery_output(self):
        jobs = self.wf["jobs"]
        for job_id in ("verifier-ubuntu", "verifier-windows"):
            self.assertEqual(jobs[job_id]["needs"], "discover")
            self.assertEqual(
                jobs[job_id]["strategy"]["matrix"]["verifier"],
                "${{ fromJSON(needs.discover.outputs.verifiers) }}")
            self.assertIs(jobs[job_id]["strategy"]["fail-fast"], False,
                          "one verifier's failure must not cancel its siblings")

    def test_fan_ins_always_run_and_check_results_explicitly(self):
        jobs = self.wf["jobs"]
        for job_id, upstream in (("verifiers-ubuntu-ok", "verifier-ubuntu"),
                                 ("verifiers-windows-ok", "verifier-windows")):
            self.assertEqual(jobs[job_id]["if"], "always()",
                             "a skipped fan-in neither blocks nor informs")
            self.assertEqual(jobs[job_id]["needs"], ["discover", upstream])
            step = jobs[job_id]["steps"][0]
            self.assertIn("needs.discover.result", step["env"]["DISCOVER_RESULT"])
            self.assertIn(upstream, step["env"]["VERIFIER_RESULT"])
            self.assertIn("exit 1", step["run"])

    def test_environment_and_permission_policy(self):
        effective = _effective(self.text)
        self.assertNotIn("NO_COLOR", effective,
                         "render tests assert color output; CI must not set NO_COLOR")
        self.assertNotIn("continue-on-error", effective,
                         "advisory standing is absence from the required-checks "
                         "list, never a masked-green job")
        self.assertEqual(self.wf["permissions"], {"contents": "read"})
        # the rollout policy must stay documented where the workflow is edited
        for name in STABLE_CHECK_NAMES:
            self.assertIn(name, self.text)

    def test_no_curated_file_list(self):
        # discovery, not curation: no test or verifier filename may appear in
        # the workflow, so adding a file never requires a CI edit
        for path in (REPO / ".claude" / "runtime").glob("verify_*.py"):
            self.assertNotIn(path.name, self.text)
        for path in (REPO / "tests").glob("test_*.py"):
            self.assertNotIn(path.name, self.text)


class DiscoveryExpression(unittest.TestCase):
    def test_enumerates_exactly_the_present_verifier_set(self):
        _, wf = _load()
        code = wf["jobs"]["discover"]["steps"][1]["run"]
        actual = sorted(
            p.name for p in (REPO / ".claude" / "runtime").glob("verify_*.py"))
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "gh_output"
            out.write_text("", encoding="utf-8")
            env = dict(os.environ, GITHUB_OUTPUT=str(out))
            proc = subprocess.run([sys.executable, "-c", code], cwd=REPO,
                                  env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            kv = dict(line.split("=", 1)
                      for line in out.read_text(encoding="utf-8").splitlines()
                      if "=" in line)
        self.assertEqual(json.loads(kv["verifiers"]), actual)
        self.assertEqual(kv["count"], str(len(actual)))
        self.assertGreater(len(actual), 0)


class VerifierAssertionWrapper(unittest.TestCase):
    """The wrapper embedded in the verifier jobs: exit 0 alone is not a pass."""

    @classmethod
    def setUpClass(cls):
        _, wf = _load()
        cls.wrapper = wf["jobs"]["verifier-ubuntu"]["steps"][3]["run"]
        cls.wrapper_windows = wf["jobs"]["verifier-windows"]["steps"][3]["run"]

    def run_wrapper(self, cwd, verifier_name):
        env = dict(os.environ, VERIFIER=verifier_name)
        return subprocess.run([sys.executable, "-c", self.wrapper], cwd=cwd,
                              env=env, capture_output=True, text=True)

    def synthetic(self, td, body):
        rt = Path(td) / ".claude" / "runtime"
        rt.mkdir(parents=True, exist_ok=True)
        name = "verify_synthetic.py"
        (rt / name).write_text(body, encoding="utf-8")
        return name

    def test_platform_wrappers_are_identical(self):
        self.assertEqual(self.wrapper, self.wrapper_windows,
                         "the two platform jobs must assert the same contract")

    def test_accepts_all_checks_passed_with_positive_verdict(self):
        with tempfile.TemporaryDirectory() as td:
            name = self.synthetic(td, "print('5/5 checks passed -- PROVEN')\n")
            self.assertEqual(self.run_wrapper(td, name).returncode, 0)

    def test_rejects_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as td:
            name = self.synthetic(
                td, "print('5/5 checks passed -- PROVEN')\nraise SystemExit(1)\n")
            self.assertNotEqual(self.run_wrapper(td, name).returncode, 0)

    def test_rejects_negative_verdict_despite_exit_zero(self):
        with tempfile.TemporaryDirectory() as td:
            name = self.synthetic(td, "print('3/5 checks passed -- NOT PROVEN')\n")
            self.assertNotEqual(self.run_wrapper(td, name).returncode, 0)

    def test_rejects_missing_summary_line_despite_exit_zero(self):
        with tempfile.TemporaryDirectory() as td:
            name = self.synthetic(td, "print('all good, trust me')\n")
            self.assertNotEqual(self.run_wrapper(td, name).returncode, 0)


class DocumentationParity(unittest.TestCase):
    """The check-name contract is published where contributors read; the HTML
    handbook is generated from the markdown guide by
    `python tools/render_user_guide.py`, and the drift step in this workflow
    fails a commit that changes one without regenerating the other."""

    def test_check_names_documented_everywhere(self):
        for rel in ("README.md", "docs/USER-GUIDE.md", "docs/user-guide.html"):
            body = (REPO / rel).read_text(encoding="utf-8")
            for name in STABLE_CHECK_NAMES:
                self.assertIn(name, body, f"{name} missing from {rel}")
            self.assertIn("verify.yml", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
