"""Tests for the one-command PR review-comment fix loop
(`omn-agent pr fix-comments`).

Reuses the real-git fixture from test_branch_pr (task, isolated worktree,
local bare origin). The runtime is replaced with a *stateful* stub that
models the gate-reject -> rollback -> re-dispatch -> complete -> re-approve
cycle and records every gate/dispatch/complete call, so the tests assert the
exact sequence the command drives. PR feedback comes from a patched
git_ops.pr_review_feedback, so no gh or network is ever touched; the gh
parsing itself is unit-tested separately with canned process output.
"""

from __future__ import annotations

import datetime
import json
import unittest
from pathlib import Path
from unittest import mock

from omn_agent import fix_comments, git_ops
from omn_agent.common import ExitCode

from test_branch_pr import GitFixtureTestCase, git

STATEFUL_RUNTIME = '''\
"""Stateful runtime stand-in modelling the review-fix cycle."""
import argparse
import json
import sys
from pathlib import Path

STATE = Path(__file__).resolve().parent.parent / "runs" / "stub-state.json"


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"stage": "awaiting-gate", "log": []}


def save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s))


def status_json(s):
    step = {"state_id": "implementation", "status": "completed",
            "queue_status": "done", "owner_agent_id": "omn-dev-1-implement",
            "eligible": False, "attempt": 0, "max_attempts": 3,
            "blocked_reason": None, "failure_class": None,
            "available_at": None, "reason": ""}
    gate = {"state_id": "code-quality-gate", "status": "completed",
            "queue_status": "done", "owner_agent_id": None, "eligible": False,
            "attempt": 0, "max_attempts": 1, "blocked_reason": None,
            "failure_class": None, "available_at": None, "decision": None,
            "owner_role": None,
            "owner_roles": ["omn-dev-2-reviewer", "omn-tech-lead"]}
    # The next gate in the workflow: awaiting decision once the first gate
    # is approved -- new review comments arriving then reject *this* one.
    merge = dict(gate, state_id="merge-gate", status="pending",
                 owner_roles=["omn-tech-lead", "omn-orchestrator"])
    stage = s["stage"]
    if stage == "awaiting-gate":
        gate.update(status="blocked")
    elif stage == "rejected":
        step.update(status="pending", eligible=True)
        gate.update(decision="rejected")
    elif stage == "dispatched":
        step.update(status="leased")
        gate.update(decision="rejected")
    elif stage == "completed":
        gate.update(status="blocked", decision=None)
    elif stage == "approved":
        gate.update(decision="approved")
        merge.update(status="blocked")
    return {"schema": "framework.runtime/status-view.v1",
            "run_id": "run-abcdef123456", "workflow_id": "implement-feature",
            "workflow_version": "1", "run_status": "active",
            "phases": [{"phase_index": 0, "steps": [step],
                        "gates": [gate, merge]}],
            "summary": {}}


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    s = load()
    if cmd == "status":
        print(json.dumps(status_json(s), indent=2))
        return 0
    if cmd == "plan":
        print("Run run-abcdef123456  (implement-feature v1)  run_status=active")
        return 0
    if cmd == "gate":
        p = argparse.ArgumentParser()
        p.add_argument("cmd")
        for f in ("--run-id", "--gate", "--decision", "--owner-role",
                  "--decided-by", "--rationale"):
            p.add_argument(f)
        a = p.parse_args(args)
        s["log"].append({"cmd": "gate", "gate": a.gate,
                         "decision": a.decision, "owner_role": a.owner_role,
                         "rationale": a.rationale})
        s["stage"] = "rejected" if a.decision == "reject" else "approved"
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
        s["stage"] = "completed"
        save(s)
        print("completed implementation")
        return 0
    print(f"ok {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''


def hours_ago(h: float) -> str:
    dt = datetime.datetime.now(datetime.timezone.utc) - \
        datetime.timedelta(hours=h)
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def findings():
    return [
        {"kind": "inline", "author": "reviewer1",
         "body": "Use a constant here", "at": hours_ago(2),
         "path": "src/app.py", "line": 42},
        {"kind": "comment", "author": "sonarqubecloud[bot]",
         "body": "Code smell: cognitive complexity 21", "at": hours_ago(1),
         "path": None, "line": None},
    ]


class FixCommentsTestCase(GitFixtureTestCase):
    def setup_pr_task(self, key="PROJ-1") -> str:
        key = self.plan_ticket(key=key)
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            STATEFUL_RUNTIME, encoding="utf-8")
        tfile = self.fw / "tasks" / key / "task-plan.json"
        task = json.loads(tfile.read_text())
        task["pr"] = {"url": "https://github.com/acme/repo/pull/7",
                      "base": "main", "head": task["branch"]["name"]}
        tfile.write_text(json.dumps(task))
        return key

    def stub_state(self) -> dict:
        p = self.fw / "runs" / "stub-state.json"
        return json.loads(p.read_text()) if p.exists() else {"log": []}

    def stub_log(self, cmd=None) -> list[dict]:
        log = self.stub_state().get("log", [])
        return [e for e in log if cmd is None or e["cmd"] == cmd]

    def fix(self, key, *extra) -> tuple[int, str]:
        return self.run_cli("pr", "fix-comments", key, "--target",
                            str(self.repo), *extra)

    # ---- preconditions ------------------------------------------------------

    def test_requires_recorded_pr(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        code, out = self.fix(key)
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no pull request is recorded", out)

    def test_requires_runtime_run(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        tfile = self.fw / "tasks" / key / "task-plan.json"
        task = json.loads(tfile.read_text())
        task["pr"] = {"url": "https://github.com/acme/repo/pull/7"}
        tfile.write_text(json.dumps(task))
        code, out = self.fix(key)
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no runtime run", out)

    # ---- round start: collect -> reject -> dispatch --------------------------

    def test_no_feedback_means_nothing_to_do(self):
        key = self.setup_pr_task()
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=[]):
            code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("nothing to fix", out)
        self.assertNotIn("fixComments", self.task(key))
        self.assertEqual(self.stub_log("gate"), [])

    def test_round_rejects_gate_with_findings_and_dispatches(self):
        key = self.setup_pr_task()
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=findings()):
            code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)

        rejects = self.stub_log("gate")
        self.assertEqual(len(rejects), 1, out)
        self.assertEqual(rejects[0]["decision"], "reject")
        self.assertEqual(rejects[0]["gate"], "code-quality-gate")
        # the deciding owner defaults to the gate's last-listed role
        self.assertEqual(rejects[0]["owner_role"], "omn-tech-lead")
        # both the human and the bot finding ride in the rationale
        self.assertIn("Use a constant here", rejects[0]["rationale"])
        self.assertIn("sonarqubecloud[bot]", rejects[0]["rationale"])
        self.assertIn("src/app.py:42", rejects[0]["rationale"])
        self.assertEqual(len(self.stub_log("dispatch")), 1)

        state = self.task(key)["fixComments"]
        self.assertEqual(state["stage"], "dispatched")
        self.assertEqual(state["round"], 1)
        self.assertEqual(state["phase"], "implementation")
        self.assertEqual(state["findings"], 2)
        rec = (self.fw / "tasks" / key / state["findingsFile"]).read_text()
        self.assertIn("Use a constant here", rec)
        self.assertIn("cognitive complexity", rec)
        # the invocation stops where the host must run the subagent
        self.assertIn("re-run", out)
        self.assertIn("fix-comments", out)

    def test_owner_role_override(self):
        key = self.setup_pr_task()
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=findings()):
            code, out = self.fix(key, "--approve", "--owner-role",
                                 "omn-orchestrator")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(self.stub_log("gate")[0]["owner_role"],
                         "omn-orchestrator")

    def test_dry_run_changes_nothing(self):
        key = self.setup_pr_task()
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=findings()):
            code, out = self.fix(key, "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertIn("would reject gate", out)
        self.assertNotIn("fixComments", self.task(key))
        self.assertEqual(self.stub_log(), [])

    def test_side_effects_require_approval(self):
        key = self.setup_pr_task()
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=findings()):
            code, out = self.fix(key)  # no --approve, stdin is not a tty
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        self.assertEqual(self.stub_log("gate"), [])
        self.assertNotIn("fixComments", self.task(key))

    # ---- resume: complete -> verify -> approve -> push ------------------------

    def resume_ready(self, key):
        """Round started (stage 'dispatched'), and the 'subagent' has
        committed a fix in the task's worktree."""
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=findings()):
            code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        wt = self.wt(key)
        (wt / "fix.py").write_text("CONSTANT = 42\n", encoding="utf-8")
        git("add", "-A", cwd=wt)
        git("commit", "-m", "address review comments", cwd=wt)

    def test_resume_completes_verifies_approves_and_pushes(self):
        key = self.setup_pr_task()
        self.resume_ready(key)
        code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)

        self.assertEqual(len(self.stub_log("complete")), 1, out)
        gates = self.stub_log("gate")
        self.assertEqual([g["decision"] for g in gates],
                         ["reject", "approve"])
        self.assertIn("pre-PR checks passed", gates[1]["rationale"])

        state = self.task(key)["fixComments"]
        self.assertEqual(state["stage"], "done")
        self.assertIn("pushedAt", state)
        # the fix commit reached origin, so the PR is updated
        branch = self.task(key)["branch"]["name"]
        local = git("rev-parse", branch, cwd=self.repo).strip()
        remote = git("rev-parse", branch, cwd=self.origin).strip()
        self.assertEqual(local, remote)
        self.assertIn("FC-DONE", out)

    def test_resume_reports_missing_artifact_and_stays_resumable(self):
        key = self.setup_pr_task()
        self.resume_ready(key)
        state_file = self.fw / "runs" / "stub-state.json"
        s = json.loads(state_file.read_text())
        s["fail_complete"] = True
        state_file.write_text(json.dumps(s))

        code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.UNEXPECTED, out)
        self.assertIn("artifact", out)
        self.assertEqual(self.task(key)["fixComments"]["stage"], "dispatched")

        s = json.loads(state_file.read_text())
        s.pop("fail_complete")
        state_file.write_text(json.dumps(s))
        code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(self.task(key)["fixComments"]["stage"], "done")

    def test_resume_stops_before_gate_and_push_when_checks_fail(self):
        key = self.setup_pr_task()
        self.resume_ready(key)
        wt = self.wt(key)
        (wt / "tests").mkdir()
        (wt / "tests" / "test_x.py").write_text(
            "import unittest\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_fail(self):\n"
            "        self.assertTrue(False)\n", encoding="utf-8")

        code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertEqual([g["decision"] for g in self.stub_log("gate")],
                         ["reject"])  # never approved
        self.assertEqual(self.task(key)["fixComments"]["stage"], "fixed")

        # fixing the tests and re-running finishes the round from 'fixed'
        (wt / "tests" / "test_x.py").write_text(
            "import unittest\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n", encoding="utf-8")
        code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(self.task(key)["fixComments"]["stage"], "done")
        self.assertEqual([g["decision"] for g in self.stub_log("gate")],
                         ["reject", "approve"])

    # ---- second round --------------------------------------------------------

    def finish_round(self, key):
        self.resume_ready(key)
        code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)

    def test_second_round_ignores_already_fixed_comments(self):
        key = self.setup_pr_task()
        self.finish_round(key)
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=findings()):  # same old comments
            code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("nothing to fix", out)
        self.assertEqual(self.task(key)["fixComments"]["round"], 1)

    def test_second_round_picks_up_new_comments(self):
        key = self.setup_pr_task()
        self.finish_round(key)
        new = findings() + [
            {"kind": "inline", "author": "reviewer2",
             "body": "Please add a docstring", "at": hours_ago(-1),
             "path": "src/app.py", "line": 1}]
        with mock.patch("omn_agent.git_ops.pr_review_feedback",
                        return_value=new):
            code, out = self.fix(key, "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        state = self.task(key)["fixComments"]
        self.assertEqual(state["round"], 2)
        self.assertEqual(state["stage"], "dispatched")
        self.assertEqual(state["findings"], 1)  # only the new comment
        rejects = [g for g in self.stub_log("gate")
                   if g["decision"] == "reject"]
        # round 2 rejects the gate now awaiting decision -- the next one in
        # the workflow, decided by its own deciding owner
        self.assertEqual(rejects[-1]["gate"], "merge-gate")
        self.assertEqual(rejects[-1]["owner_role"], "omn-orchestrator")
        self.assertIn("Please add a docstring", rejects[-1]["rationale"])
        self.assertNotIn("Use a constant here", rejects[-1]["rationale"])


class PrReviewFeedbackTestCase(unittest.TestCase):
    """gh output parsing for git_ops.pr_review_feedback, with canned process
    results -- no gh binary, no network."""

    VIEW = {
        "number": 7,
        "author": {"login": "dev-author"},
        "comments": [
            {"author": {"login": "sonarqubecloud[bot]"},
             "body": "Quality gate failed", "createdAt": "2026-08-21T09:00:00Z"},
            {"author": {"login": "dev-author"},
             "body": "will fix", "createdAt": "2026-08-21T09:05:00Z"},
        ],
        "reviews": [
            {"author": {"login": "reviewer1"}, "state": "CHANGES_REQUESTED",
             "body": "Please split this function",
             "submittedAt": "2026-08-21T10:00:00Z"},
            {"author": {"login": "reviewer2"}, "state": "APPROVED",
             "body": "", "submittedAt": "2026-08-21T11:00:00Z"},
        ],
    }
    INLINE = [
        {"user": {"login": "reviewer1"}, "body": "typo here",
         "path": "src/x.py", "line": 3,
         "created_at": "2026-08-21T08:00:00Z"},
    ]

    def feedback(self):
        def run(argv, cwd):
            out = json.dumps(self.VIEW if "view" in argv else self.INLINE)
            return mock.Mock(returncode=0, stdout=out, stderr="")
        with mock.patch("omn_agent.git_ops.gh_path", return_value="gh"), \
             mock.patch("omn_agent.git_ops.gh_authenticated",
                        return_value=True), \
             mock.patch("omn_agent.git_ops._run", side_effect=run):
            return git_ops.pr_review_feedback(Path("."), "7")

    def test_merges_sorts_and_filters(self):
        items = self.feedback()
        # oldest first; author's own reply and the empty approval are dropped
        self.assertEqual([f["kind"] for f in items],
                         ["inline", "comment", "review:changes_requested"])
        self.assertEqual(items[0]["path"], "src/x.py")
        self.assertEqual(items[0]["line"], 3)
        self.assertEqual(items[1]["author"], "sonarqubecloud[bot]")
        self.assertNotIn("will fix", [f["body"] for f in items])


class TimestampFilterTestCase(unittest.TestCase):
    def test_parse_handles_z_and_offset_forms(self):
        a = fix_comments._parse_ts("2026-08-21T10:00:00Z")
        b = fix_comments._parse_ts("2026-08-21T10:00:00+00:00")
        self.assertEqual(a, b)
        self.assertIsNone(fix_comments._parse_ts("not-a-date"))
        self.assertIsNone(fix_comments._parse_ts(""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
