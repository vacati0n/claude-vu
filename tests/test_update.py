"""Tests for the one-command Jira change-request loop (`omn-agent update`).

Reuses the real-git fixture from test_branch_pr (task, isolated worktree,
local bare origin). The runtime is replaced with a *stateful* stub that
models the update cycle -- dispatch, complete, policy-driven gate approval,
run completion -- and records every call, so the tests assert the exact
sequence the command drives. Like the real runtime, the stub pins the run's
input digest and rejects every operation (except status) once input.md
changed: "a changed input is a new run". Jira is exercised only through the
fake transport from test_omn_agent; no network is touched.
"""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import unittest

from omn_agent import cli, update
from omn_agent.common import ExitCode

from test_branch_pr import GitFixtureTestCase, git

STATEFUL_RUNTIME = '''\
"""Stateful runtime stand-in modelling the update change-request cycle.

Like the real runtime, it pins the run's input digest and rejects every
operation except `status` once the pinned input file changed -- the
context-integrity rule that makes a changed input a new run.
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
    """Non-None when the pinned input no longer digests to what the run was
    created from (mirrors framework_runtime.read_supplied)."""
    if not s.get("input_file"):
        return None
    d = digest(s["input_file"])
    if d != s["input_digest"]:
        return (f"context-integrity-failure: supplied input "
                f"{s['input_file']} has changed since the run was created "
                f"({s['input_digest']} -> {d}); a changed input is a new run")
    return None


def status_json(s):
    step = {"state_id": "implementation", "status": "pending",
            "queue_status": "ready", "owner_agent_id": "omn-dev-1-implement",
            "eligible": True, "attempt": 0, "max_attempts": 3,
            "blocked_reason": None, "failure_class": None,
            "available_at": None, "reason": ""}
    gate = {"state_id": "code-quality-gate", "status": "pending",
            "queue_status": "ready", "owner_agent_id": None, "eligible": False,
            "attempt": 0, "max_attempts": 1, "blocked_reason": None,
            "failure_class": None, "available_at": None, "decision": None,
            "owner_role": None,
            "owner_roles": ["omn-dev-2-reviewer", "omn-tech-lead"]}
    stage = s["stage"]
    run_status = "Dispatching"
    if stage == "awaiting-gate":
        step.update(status="completed", eligible=False)
        gate.update(status="blocked")
        run_status = "WaitingForHuman"
    elif stage == "rejected":
        gate.update(decision="rejected")
    elif stage == "dispatched":
        step.update(status="leased", eligible=False)
        run_status = "ExecutingState"
    elif stage == "completed":
        step.update(status="completed", eligible=False)
        gate.update(status="blocked")
        run_status = "WaitingForHuman"
    elif stage == "done":
        step.update(status="completed", eligible=False)
        gate.update(status="completed", decision="approved")
        run_status = "Completed"
    return {"schema": "framework.runtime/status-view.v1",
            "run_id": "run-abcdef123456", "workflow_id": "implement-feature",
            "workflow_version": "1", "run_status": run_status,
            "phases": [{"phase_index": 0, "steps": [step], "gates": [gate]}],
            "summary": {}}


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    auto = "--gate-policy" in args
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
        print("Run run-abcdef123456  (implement-feature v1)  "
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
                         "decision": a.decision, "owner_role": a.owner_role,
                         "rationale": a.rationale})
        s["stage"] = "rejected" if a.decision == "reject" else "done"
        save(s)
        print(f"gate {a.gate}: {a.decision}")
        return 0
    if cmd == "dispatch":
        s["log"].append({"cmd": "dispatch", "args": args})
        s["stage"] = "dispatched"
        save(s)
        print("dispatched implementation to omn-dev-1-implement")
        return 0
    if cmd == "complete":
        if s.get("fail_complete"):
            print("phase artifact missing; nothing to ingest")
            return 3
        s["log"].append({"cmd": "complete", "args": args})
        # With a gate policy the runtime auto-approves the clean-evidence
        # gate right after the completion; without it the gate holds.
        s["stage"] = "done" if auto else "completed"
        save(s)
        print("completed implementation")
        return 0
    if cmd == "next":
        s["log"].append({"cmd": "next", "auto": auto})
        if auto and s["stage"] == "completed":
            s["stage"] = "done"
        save(s)
        print("NEXT: (stub)")
        return 0
    print(f"ok {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


class UpdateTestCase(GitFixtureTestCase):
    def setup_run_task(self, key="PROJ-1", stage="awaiting-gate",
                       pr=False) -> str:
        """A planned task with a bound worktree and a runtime run, then the
        runtime replaced by the stateful stub pinned at `stage`."""
        key = self.plan_ticket(key=key)
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            STATEFUL_RUNTIME, encoding="utf-8")
        self.set_stage(stage)
        self.pin_input(key)
        if pr:
            tfile = self.fw / "tasks" / key / "task-plan.json"
            task = json.loads(tfile.read_text())
            task["pr"] = {"url": "https://github.com/acme/repo/pull/7",
                          "base": "main", "head": task["branch"]["name"]}
            tfile.write_text(json.dumps(task))
        return key

    def set_stage(self, stage: str):
        p = self.fw / "runs" / "stub-state.json"
        state = json.loads(p.read_text()) if p.exists() else {"log": []}
        state["stage"] = stage
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state))

    def pin_input(self, key: str):
        """Pin the task's current input.md digest in the stub run, the way
        the real runtime pins it at run creation."""
        src = self.fw / "tasks" / key / "input.md"
        text = src.read_text(encoding="utf-8").strip()
        p = self.fw / "runs" / "stub-state.json"
        state = json.loads(p.read_text()) if p.exists() else {"log": []}
        state["input_file"] = str(src)
        state["input_digest"] = hashlib.sha256(
            text.encode("utf-8")).hexdigest()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state))

    def stub_log(self, cmd=None) -> list[dict]:
        p = self.fw / "runs" / "stub-state.json"
        log = (json.loads(p.read_text()) if p.exists() else {}).get("log", [])
        return [e for e in log if cmd is None or e["cmd"] == cmd]

    def touch_ticket(self, key="PROJ-1",
                     description="New acceptance criteria from Jira"):
        """Simulate the ticket having changed in Jira: rewrite the inbox copy
        with a new description and updated timestamp."""
        path = self.fw / "tickets" / "inbox" / f"{key}.json"
        ticket = json.loads(path.read_text())
        ticket["description"] = description
        ticket["updated"] = "2026-08-21T12:00:00.000+0000"
        path.write_text(json.dumps(ticket, indent=2, sort_keys=True))

    def upd(self, key, *extra) -> tuple[int, str]:
        return self.run_cli("update", key, "--target", str(self.repo),
                            "--no-fetch", *extra)

    # ---- preconditions ------------------------------------------------------

    def test_requires_synced_ticket(self):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.upd("PROJ-9")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("not in the inbox", out)

    def test_side_effects_require_approval(self):
        key = self.setup_run_task()
        self.touch_ticket(key)
        code, out = self.upd(key)  # no --approve, stdin is not a tty
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        self.assertEqual(self.stub_log("gate"), [])

    def test_dry_run_changes_nothing(self):
        key = self.setup_run_task()
        self.touch_ticket(key)
        before = (self.fw / "tasks" / key / "task-plan.json").read_text()
        code, out = self.upd(key, "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertIn("would refresh", out)
        self.assertEqual(self.stub_log(), [])
        self.assertEqual(
            (self.fw / "tasks" / key / "task-plan.json").read_text(), before)

    # ---- ticket change carried into an in-flight run --------------------------

    def test_midrun_change_archives_run_and_starts_new(self):
        """The runtime pins input digests at run creation and re-verifies
        them on every operation, so a regenerated input.md can never be
        carried into the in-flight run -- not even by a gate rejection. The
        run is archived and a new one materialized from the updated input."""
        key = self.setup_run_task()
        old_run = self.task(key)["runId"]
        self.touch_ticket(key)
        code, out = self.upd(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)

        # no operation is attempted on the stale run (the stub, like the
        # real runtime, would reject it with context-integrity-failure)
        self.assertEqual(self.stub_log("gate"), [])
        task = self.task(key)
        self.assertEqual(len(task["runHistory"]), 1)
        self.assertEqual(task["runHistory"][0]["runId"], old_run)
        self.assertIn("a changed input is a new run",
                      task["runHistory"][0]["reason"])
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertEqual(len(self.stub_log("plan")), 1)
        self.assertEqual(len(self.stub_log("dispatch")), 1)
        self.assertEqual(task["updateFlow"]["round"], 1)
        self.assertEqual(task["updateFlow"]["inputHash"], task["inputHash"])
        self.assertNotIn("pendingRunArchive", task["updateFlow"])
        self.assertIn("U-RERUN", out)
        # the invocation stops where the host must run the subagent
        self.assertIn("U-WAIT", out)
        self.assertIn("re-run", out)

    def test_denied_midrun_archive_resumes_without_wedging(self):
        """Regression (ON-14): apply_plan rewrites input.md before the
        archive is approved, and the task-plan inputHash advances, so on the
        next invocation `changed` is False -- yet the old run can no longer
        accept any operation. The recorded archive debt must let the next
        invocation finish the rollover instead of wedging in the drive
        loop."""
        key = self.setup_run_task()
        old_run = self.task(key)["runId"]
        self.touch_ticket(key)
        code, out = self.upd(key)  # no --approve, stdin is not a tty
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        task = self.task(key)
        self.assertEqual(task["updateFlow"]["pendingRunArchive"], old_run)
        self.assertEqual(task["runId"], old_run)
        self.assertEqual(task.get("runHistory"), None)

        code, out = self.upd(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        task = self.task(key)
        self.assertEqual(task["runHistory"][0]["runId"], old_run)
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertEqual(self.stub_log("gate"), [])
        self.assertEqual(len(self.stub_log("dispatch")), 1)
        self.assertNotIn("pendingRunArchive", task["updateFlow"])
        self.assertIn("U-WAIT", out)

    def test_unchanged_ticket_is_a_noop_replan(self):
        key = self.setup_run_task(stage="dispatched", pr=True)
        code, out = self.upd(key, "--approve", "--gate-policy", "auto")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("P-SAME", out)
        # no change round, so no gate rejection
        self.assertEqual([g for g in self.stub_log("gate")
                          if g["decision"] == "reject"], [])

    # ---- resume: complete -> auto gate -> verify -> push ----------------------

    def test_resume_completes_and_updates_pr(self):
        key = self.setup_run_task(stage="dispatched", pr=True)
        wt = self.wt(key)
        (wt / "change.py").write_text("TIMEOUT = 30\n", encoding="utf-8")
        git("add", "-A", cwd=wt)
        git("commit", "-m", "apply ticket change", cwd=wt)

        code, out = self.upd(key, "--approve", "--gate-policy", "auto")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(len(self.stub_log("complete")), 1, out)
        self.assertIn("U-DONE", out)
        self.assertIn("PR", out)

        # the change commit reached origin, so the PR is updated
        branch = self.task(key)["branch"]["name"]
        local = git("rev-parse", branch, cwd=self.repo).strip()
        remote = git("rev-parse", branch, cwd=self.origin).strip()
        self.assertEqual(local, remote)

        flow = self.task(key)["updateFlow"]
        self.assertEqual(flow["deliveredHash"], self.task(key)["inputHash"])

    def test_delivered_and_unchanged_short_circuits(self):
        key = self.setup_run_task(stage="dispatched", pr=True)
        code, out = self.upd(key, "--approve", "--gate-policy", "auto")
        self.assertEqual(code, ExitCode.OK, out)
        calls = len(self.stub_log())

        code, out = self.upd(key, "--approve", "--gate-policy", "auto")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("U-UPTODATE", out)
        self.assertEqual(len(self.stub_log()), calls)

    def test_missing_artifact_stops_and_stays_resumable(self):
        key = self.setup_run_task(stage="dispatched", pr=True)
        state_file = self.fw / "runs" / "stub-state.json"
        s = json.loads(state_file.read_text())
        s["fail_complete"] = True
        state_file.write_text(json.dumps(s))

        code, out = self.upd(key, "--approve", "--gate-policy", "auto")
        self.assertEqual(code, ExitCode.UNEXPECTED, out)
        self.assertIn("artifact", out)

        s = json.loads(state_file.read_text())
        s.pop("fail_complete")
        state_file.write_text(json.dumps(s))
        code, out = self.upd(key, "--approve", "--gate-policy", "auto")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("U-DONE", out)

    def test_held_gate_stops_with_instructions(self):
        key = self.setup_run_task(stage="dispatched", pr=True)
        code, out = self.upd(key, "--approve")  # no gate policy
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("U-GATE", out)
        self.assertIn("--gate-policy auto", out)
        # complete happened, but nothing approved the gate and nothing pushed
        self.assertEqual(len(self.stub_log("complete")), 1)
        self.assertEqual([g for g in self.stub_log("gate")
                          if g["decision"] == "approve"], [])

    # ---- no run yet: materialize, auto-bind, dispatch --------------------------

    def test_materializes_run_and_auto_binds_branch(self):
        key = self.plan_ticket()
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            STATEFUL_RUNTIME, encoding="utf-8")
        code, out = self.upd(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)

        task = self.task(key)
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertEqual(task["branch"]["name"],
                         "feature/proj-1-add-login-timeout")
        self.assertTrue(self.wt(key).is_dir())
        self.assertIn("B-CREATE", out)
        self.assertEqual(len(self.stub_log("dispatch")), 1)
        self.assertIn("U-WAIT", out)

    # ---- completed run + change: a fresh run for the new round -----------------

    def test_completed_run_with_change_starts_new_run(self):
        key = self.setup_run_task(stage="done", pr=True)
        old_run = self.task(key)["runId"]
        self.touch_ticket(key)
        code, out = self.upd(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)

        task = self.task(key)
        self.assertIn("U-RERUN", out)
        self.assertEqual(len(task["runHistory"]), 1)
        self.assertEqual(task["runHistory"][0]["runId"], old_run)
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertEqual(len(self.stub_log("plan")), 1)
        self.assertEqual(len(self.stub_log("dispatch")), 1)
        self.assertIn("U-WAIT", out)

    # ---- Jira refresh and the closed-ticket guard ------------------------------

    def test_refresh_pulls_from_jira_and_closed_ticket_stops(self):
        key = self.setup_run_task()
        from test_omn_agent import fake_transport
        args = cli.build_parser().parse_args(
            ["update", key, "--target", str(self.repo), "--approve"])
        out_io = io.StringIO()
        with contextlib.redirect_stdout(out_io):
            code = update.cmd_update(
                args, transport=fake_transport([self.closed_ticket(key=key)]))
        out = out_io.getvalue()
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("U-TICKET", out)
        self.assertIn("U-CLOSED", out)
        # the refreshed (closed) ticket landed in the inbox
        inbox = json.loads(
            (self.fw / "tickets" / "inbox" / f"{key}.json").read_text())
        self.assertEqual(inbox["status"], "Done")
        # nothing was driven
        self.assertEqual(self.stub_log(), [])


if __name__ == "__main__":
    unittest.main()
