"""Tests for the one-command repository quality scan (`omn-agent quality-scan`).

Reuses the install fixture from test_branch_pr (framework source, target repo)
with the runtime replaced by a *stateful* stub that models the scan cycle --
materialize, dispatch, complete, the Quality Handoff Gate held for a human --
and records every call, so the tests assert the exact sequence the command
drives. Like the real runtime, the stub pins the run's input digest and
rejects every operation (except status) once the scope changed: "a changed
input is a new run". No ticket, no Jira, no network.
"""

from __future__ import annotations

import json
import unittest

from omn_agent.common import ExitCode

from test_branch_pr import GitFixtureTestCase

SCAN_RUNTIME = '''\
"""Stateful runtime stand-in modelling the code-quality-scan cycle.

Stages: fresh (phase pending, eligible) -> dispatched (leased) ->
completed (run Completed, Quality Handoff Gate blocked awaiting a human) ->
done (gate decided). Like the real runtime, it pins the run's input digest
and rejects every operation except `status` once the pinned input changed.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / "runs" / "stub-state.json"


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"stage": "fresh", "log": []}


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s))


def digest(path):
    text = Path(path).read_text(encoding="utf-8").strip()
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def integrity_error(s):
    if not s.get("input_file"):
        return None
    d = digest(s["input_file"])
    if d != s["input_digest"]:
        return ("context-integrity-failure: supplied input "
                f"{s['input_file']} has changed since the run was created; "
                "a changed input is a new run")
    return None


def status_json(s):
    step = {"state_id": "repository-quality-scan", "status": "pending",
            "queue_status": "ready", "owner_agent_id": "omn-dev-2-reviewer",
            "eligible": True, "attempt": 0, "max_attempts": 3,
            "blocked_reason": None, "failure_class": None,
            "available_at": None, "reason": ""}
    gate = {"state_id": "quality-handoff-gate", "status": "pending",
            "queue_status": "ready", "owner_agent_id": None, "eligible": False,
            "attempt": 0, "max_attempts": 1, "blocked_reason": None,
            "failure_class": None, "available_at": None, "decision": None,
            "owner_role": None,
            "owner_roles": ["omn-dev-2-reviewer", "omn-tech-lead"]}
    stage = s["stage"]
    run_status = "Dispatching"
    if stage == "dispatched":
        step.update(status="leased", eligible=False)
        run_status = "ExecutingState"
    elif stage == "completed":
        step.update(status="completed", eligible=False)
        gate.update(status="blocked",
                    blocked_reason="awaiting_human_decision")
        run_status = "Completed"
    elif stage == "done":
        step.update(status="completed", eligible=False)
        gate.update(status="completed", decision="approved")
        run_status = "Completed"
    return {"schema": "framework.runtime/status-view.v1",
            "run_id": "run-abcdef123456", "workflow_id": "code-quality-scan",
            "workflow_version": "1", "run_status": run_status,
            "phases": [{"phase_index": 0, "steps": [step], "gates": [gate]}],
            "summary": {}}


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    s = load()
    if cmd == "status":
        print(json.dumps(status_json(s), indent=2))
        return 0
    if cmd == "plan":
        s["stage"] = "fresh"
        s["log"].append({"cmd": "plan"})
        if "--input-file" in args:
            s["input_file"] = args[args.index("--input-file") + 1]
            s["input_digest"] = digest(s["input_file"])
        save(s)
        print("Run run-abcdef123456  (code-quality-scan v1)  "
              "run_status=Dispatching")
        return 0
    if cmd in ("gate", "dispatch", "complete", "next"):
        err = integrity_error(s)
        if err:
            print(err)
            return 4
    if cmd == "gate":
        p = argparse.ArgumentParser()
        p.add_argument("cmd")
        for f in ("--run-id", "--gate", "--decision", "--owner-role",
                  "--decided-by", "--rationale", "--gate-policy"):
            p.add_argument(f)
        a = p.parse_args(args)
        s["log"].append({"cmd": "gate", "gate": a.gate,
                         "decision": a.decision, "owner_role": a.owner_role})
        s["stage"] = "done" if a.decision == "approve" else "fresh"
        save(s)
        print(f"gate {a.gate}: {a.decision}")
        return 0
    if cmd == "dispatch":
        s["log"].append({"cmd": "dispatch", "args": args})
        s["stage"] = "dispatched"
        save(s)
        print("dispatched repository-quality-scan to omn-dev-2-reviewer")
        return 0
    if cmd == "complete":
        if s.get("fail_complete"):
            print("phase artifact missing; nothing to ingest")
            return 3
        s["log"].append({"cmd": "complete", "args": args})
        s["stage"] = "completed"
        save(s)
        print("completed repository-quality-scan; validation PASS")
        return 0
    print(f"ok {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


class QualityScanTestCase(GitFixtureTestCase):
    KEY = "QS-REPO"

    def setup_scan_repo(self):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            SCAN_RUNTIME, encoding="utf-8")

    def scan(self, *extra) -> tuple[int, str]:
        return self.run_cli("quality-scan", "--target", str(self.repo),
                            *extra)

    def stub_log(self, cmd=None) -> list[dict]:
        p = self.fw / "runs" / "stub-state.json"
        log = (json.loads(p.read_text()) if p.exists() else {}).get("log", [])
        return [e for e in log if cmd is None or e["cmd"] == cmd]

    def set_stage(self, stage: str):
        p = self.fw / "runs" / "stub-state.json"
        state = json.loads(p.read_text()) if p.exists() else {"log": []}
        state["stage"] = stage
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state))

    # ---- planning, scope rendering, and the first dispatch ------------------

    def test_scan_plans_materializes_and_dispatches(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve", "--paths", "src/api,src/core",
                              "--exclude", "vendor/",
                              "--risk-threshold", "high",
                              "--context", "pre-merge sweep")
        self.assertEqual(code, ExitCode.OK, out)

        task = self.task(self.KEY)
        self.assertEqual(task["command"], "quality-scan")
        self.assertEqual(task["workflow"], "code-quality-scan")
        self.assertEqual(task["inputType"], "quality-scan-scope")
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertEqual(task["scanFlow"]["materializedHash"],
                         task["inputHash"])

        scope = (self.fw / "tasks" / self.KEY / "input.md") \
            .read_text(encoding="utf-8")
        self.assertIn("src/api, src/core", scope)
        self.assertIn("vendor/", scope)
        self.assertIn("`.omn-agent/`", scope)
        self.assertIn("`.worktrees/`", scope)
        self.assertIn("`high`", scope)
        self.assertIn("pre-merge sweep", scope)

        self.assertEqual(len(self.stub_log("plan")), 1)
        self.assertEqual(len(self.stub_log("dispatch")), 1)
        self.assertIn("Q-WAIT", out)
        # the approvals ledger recorded the side-effecting steps
        self.assertTrue(
            (self.fw / "tasks" / self.KEY / "approvals.jsonl").is_file())

    def test_default_scope_covers_whole_repo(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        scope = (self.fw / "tasks" / self.KEY / "input.md") \
            .read_text(encoding="utf-8")
        self.assertIn("the whole repository", scope)
        self.assertIn("`medium`", scope)

    def test_scope_file_is_used_verbatim(self):
        self.setup_scan_repo()
        custom = self.tmp / "my-scope.md"
        custom.write_text("# custom scan scope\n\n- Review only: lib/\n",
                          encoding="utf-8")
        code, out = self.scan("audit", "--approve",
                              "--scope-file", str(custom))
        self.assertEqual(code, ExitCode.OK, out)
        scope = (self.fw / "tasks" / "QS-AUDIT" / "input.md") \
            .read_text(encoding="utf-8")
        self.assertEqual(scope, custom.read_text(encoding="utf-8"))

    # ---- approval discipline and dry-run -------------------------------------

    def test_side_effects_require_approval(self):
        self.setup_scan_repo()
        code, out = self.scan()  # no --approve, stdin is not a tty
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        self.assertEqual(self.stub_log(), [])

    def test_dry_run_changes_nothing(self):
        self.setup_scan_repo()
        code, out = self.scan("--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertIn("Q-PLAN", out)
        self.assertFalse((self.fw / "tasks" / self.KEY).exists())
        self.assertEqual(self.stub_log(), [])

    # ---- resume: complete, then stop at the human gate ------------------------

    def test_resume_completes_and_stops_at_gate(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)

        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(len(self.stub_log("complete")), 1, out)
        self.assertIn("Q-DONE", out)
        self.assertIn("Quality Handoff Gate", out)
        self.assertIn("omn-tech-lead", out)
        # the command never decides the gate itself
        self.assertEqual(self.stub_log("gate"), [])

    def test_gate_decided_reports_done_read_only(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.set_stage("done")
        calls = len(self.stub_log())

        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("Q-DONE", out)
        self.assertIn("decided", out)
        # only the read-only status call happened; nothing side-effecting
        self.assertEqual(len(self.stub_log()), calls)

    def test_gate_decision_flows_through_run_command(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.set_stage("completed")

        code, out = self.run_cli(
            "run", self.KEY, "--target", str(self.repo), "--approve",
            "--gate", "Quality Handoff Gate", "--decision", "approve",
            "--owner-role", "omn-tech-lead",
            "--rationale", "package accepted as review of record")
        self.assertEqual(code, ExitCode.OK, out)
        decisions = self.stub_log("gate")
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0]["decision"], "approve")
        self.assertEqual(decisions[0]["owner_role"], "omn-tech-lead")

    def test_missing_artifact_stops_and_stays_resumable(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        state_file = self.fw / "runs" / "stub-state.json"
        s = json.loads(state_file.read_text())
        s["fail_complete"] = True
        state_file.write_text(json.dumps(s))

        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.UNEXPECTED, out)
        self.assertIn("Q-COMPLETE", out)

        s = json.loads(state_file.read_text())
        s.pop("fail_complete")
        state_file.write_text(json.dumps(s))
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("Q-DONE", out)

    # ---- a changed scope is a new run -----------------------------------------

    def test_changed_scope_archives_run_and_starts_new(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        old_run = self.task(self.KEY)["runId"]

        code, out = self.scan("--approve", "--paths", "src/only-this")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("Q-RERUN", out)
        self.assertNotIn("context-integrity-failure", out)
        task = self.task(self.KEY)
        self.assertEqual(len(task["runHistory"]), 1)
        self.assertEqual(task["runHistory"][0]["runId"], old_run)
        self.assertIn("a changed input is a new run",
                      task["runHistory"][0]["reason"])
        self.assertEqual(len(self.stub_log("plan")), 2)
        self.assertEqual(len(self.stub_log("dispatch")), 2)

    def test_denied_archive_resumes_without_wedging(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        old_run = self.task(self.KEY)["runId"]

        code, out = self.scan("--paths", "src/only-this")  # no --approve
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        task = self.task(self.KEY)
        self.assertEqual(task["scanFlow"]["pendingRunArchive"], old_run)
        self.assertEqual(task["runId"], old_run)

        code, out = self.scan("--approve", "--paths", "src/only-this")
        self.assertEqual(code, ExitCode.OK, out)
        task = self.task(self.KEY)
        self.assertEqual(task["runHistory"][0]["runId"], old_run)
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertNotIn("pendingRunArchive", task["scanFlow"])

    def test_unchanged_scope_reenters_same_run(self):
        self.setup_scan_repo()
        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        plans = len(self.stub_log("plan"))

        code, out = self.scan("--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("Q-SAME", out)
        self.assertEqual(len(self.stub_log("plan")), plans)
        self.assertIsNone(self.task(self.KEY).get("runHistory"))

    # ---- name handling ---------------------------------------------------------

    def test_invalid_name_is_rejected(self):
        self.setup_scan_repo()
        code, out = self.scan("///", "--approve")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("empty slug", out)


if __name__ == "__main__":
    unittest.main()
