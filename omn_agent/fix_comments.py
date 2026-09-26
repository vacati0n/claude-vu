"""One-command PR review-comment fix loop (`omn-agent pr fix-comments`).

Automates the framework's designed correction cycle for a task whose PR is
already open and has collected reviewer feedback (human comments, Sonar and
other bot findings):

1. collect the feedback from the PR via ``gh``;
2. reject the gate currently awaiting a decision, carrying the findings as
   the rejection rationale -- the runtime classifies that as ``gate-rejection``
   with action rollback, but a rollback is a second human decision, not a
   consequence of the first;
3. authorise that rollback with the runtime's ``rollback`` command, as the
   same owner role, naming the task's fix phase as the target: the runtime
   supersedes the completed fix phase (and every completed phase between it
   and the gated one) as a new attempt under the same idempotency key,
   re-arms the gate, and carries the findings forward as ``prior_rejection``;
4. re-dispatch the fix phase (the host-subagent adapter: the host platform
   runs the registered subagent, this CLI never implements code itself);
5. on the next invocation -- after the host has run the subagent -- ingest
   the completion, re-run the pre-PR quality gate, approve the re-armed gate
   on that clean evidence, and push the bound branch so the PR updates.

The command is resumable: round state lives on the task (``fixComments`` in
task-plan.json), and each invocation reads it plus live runtime state and
performs every step it can, stopping only where the host must run the
dispatched subagent. Every side-effecting step goes through the same
approval discipline as ``omn-agent run`` (``--approve``, or an interactive
yes), and is recorded to the task's approvals ledger.
"""

from __future__ import annotations

import datetime
import getpass
import json
import subprocess
import sys
from pathlib import Path

from . import git_ops
from .common import ExitCode, OmnError, Report
from .pr import _require_worktree, run_precheck
from .repo import framework_root, resolve_target
from .runner import _invoke, _require_approval, _runtime
from .taskplan import load_task, save_task

MAX_RATIONALE_ITEMS = 12
MAX_RATIONALE_ITEM_LEN = 200
MAX_RATIONALE_LEN = 4000

# The code-changing phase of each routed workflow: the target a review-comment
# rollback re-enters. A workflow absent here rolls back to the gated phase
# itself (the runtime's default target).
FIX_PHASE_BY_WORKFLOW = {
    "implement-feature": "implementation",
    "fix-bug": "fix-implementation",
    "refactor": "refactor-implementation",
}


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc) \
        .isoformat(timespec="seconds")


def _parse_ts(value: str) -> datetime.datetime | None:
    """A feedback timestamp as an aware datetime, or None when unparseable.
    GitHub emits ``...Z``, this module emits ``...+00:00``; both must compare
    correctly, so string comparison is never used."""
    if not value:
        return None
    try:
        dt = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def _status_json(fw_dir: Path, target: Path, run_id: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(_runtime(fw_dir)), "status", "--run-id", run_id,
         "--json"],
        cwd=str(target), capture_output=True, text=True)
    out = proc.stdout or ""
    if proc.returncode != 0:
        raise OmnError(ExitCode.UNEXPECTED, "runtime 'status --json' failed",
                       hint=((proc.stderr or out).strip() or
                             "inspect the run with 'omn-agent run ... --show'")
                            [-500:])
    start = out.find("{")
    if start < 0:
        raise OmnError(ExitCode.UNEXPECTED,
                       "runtime 'status --json' printed no JSON object",
                       hint=out.strip()[-500:] or "(no output)")
    try:
        return json.loads(out[start:])
    except json.JSONDecodeError as exc:
        raise OmnError(ExitCode.UNEXPECTED,
                       "could not parse runtime 'status --json' output",
                       hint=str(exc))


def _gates(status: dict) -> list[dict]:
    return [g for ph in status.get("phases") or []
            for g in ph.get("gates") or []]


def _steps(status: dict) -> list[dict]:
    return [s for ph in status.get("phases") or []
            for s in ph.get("steps") or []]


def _awaiting_gate(status: dict) -> dict | None:
    """The gate work item currently awaiting a decision, if any."""
    for g in _gates(status):
        if g.get("status") == "blocked" and not g.get("decision"):
            return g
    return None


def _dispatchable_step(status: dict) -> dict | None:
    for s in _steps(status):
        if s.get("status") == "pending" and s.get("eligible"):
            return s
    return None


def _fix_phase(task: dict, status: dict) -> str | None:
    """The task's fix phase, when the run holds it completed; None lets the
    runtime default the rollback target to the phase the gate closes."""
    phase = FIX_PHASE_BY_WORKFLOW.get(task.get("workflow") or "")
    if not phase:
        return None
    step = next((s for s in _steps(status) if s.get("state_id") == phase), None)
    if step is None or step.get("status") != "completed":
        return None
    return phase


def _rolled_back_step(status: dict, gate: str) -> dict | None:
    """The step a rollback past `gate` re-entered, if the runtime shows one."""
    for s in _steps(status):
        rb = s.get("rollback") or {}
        if rb.get("gate") == gate and s.get("status") == "pending":
            return s
    return None


def _deciding_role(gate: dict) -> str | None:
    """The gate's deciding owner. Each gate lists its producing owner first
    and the deciding owner second (Producer Exclusion Rule), so the last
    listed role is the one that may decide."""
    roles = gate.get("owner_roles") or []
    return roles[-1] if roles else None


def _build_rationale(findings: list[dict], round_no: int,
                     findings_rel: str) -> str:
    lines = [f"review-comment fix round {round_no}: {len(findings)} "
             f"unaddressed finding(s) from PR review"]
    for f in findings[:MAX_RATIONALE_ITEMS]:
        loc = f" [{f['path']}:{f['line']}]" if f.get("path") else ""
        body = " ".join(f["body"].split())[:MAX_RATIONALE_ITEM_LEN]
        lines.append(f"- {f['author']} ({f['kind']}){loc}: {body}")
    if len(findings) > MAX_RATIONALE_ITEMS:
        lines.append(f"- ... and {len(findings) - MAX_RATIONALE_ITEMS} more")
    lines.append(f"full feedback: {findings_rel}")
    return "\n".join(lines)[:MAX_RATIONALE_LEN]


def _write_findings(tdir: Path, findings: list[dict], round_no: int,
                    pr_ref: str, collected_at: str) -> str:
    rel = f"fix-comments/round-{round_no}-findings.md"
    path = tdir / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# PR review feedback -- round {round_no}", "",
             f"Source: {pr_ref}", f"Collected: {collected_at}", ""]
    for n, f in enumerate(findings, 1):
        loc = f", {f['path']}:{f['line']}" if f.get("path") else ""
        lines += [f"## {n}. {f['author']} ({f['kind']}{loc}) at {f['at']}",
                  "", f["body"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return rel


def cmd_pr_fix_comments(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("pr fix-comments", str(target))
    fw_dir = framework_root(target)
    task, tdir = load_task(fw_dir, args.key)

    pr_ref = getattr(args, "pr", None) or (task.get("pr") or {}).get("url")
    if not pr_ref:
        raise OmnError(
            ExitCode.INCOMPLETE,
            f"no pull request is recorded for task {task['ticket']}",
            hint=f"create one with 'omn-agent pr create {task['ticket']}', "
                 "or pass --pr <number|url>")
    run_id = task.get("runId")
    if not run_id:
        raise OmnError(
            ExitCode.INCOMPLETE,
            f"task {task['ticket']} has no runtime run to carry the fix cycle",
            hint=f"run 'omn-agent run {task['ticket']}' first")
    bound, wt = _require_worktree(target, task)

    state = task.get("fixComments") or {}
    stage = state.get("stage")

    if stage not in ("rejected", "dispatched", "fixed"):
        early = _start_round(args, report, target, fw_dir, task, tdir, state,
                             run_id, str(pr_ref))
        if early is not None:
            return early
        state = task["fixComments"]
        stage = state["stage"]

    if stage == "rejected":
        if not state.get("rollback"):
            early = _authorise_rollback(args, report, target, fw_dir, task,
                                        tdir, state, run_id)
            if early is not None:
                return early
        return _dispatch_fix(args, report, target, fw_dir, task, tdir, state,
                             run_id, wt)

    if stage == "dispatched":
        early = _complete_fix(args, report, target, fw_dir, task, tdir, state,
                              run_id)
        if early is not None:
            return early

    return _verify_and_push(args, report, target, fw_dir, task, tdir, state,
                            run_id, bound)


def _start_round(args, report, target, fw_dir, task, tdir, state, run_id,
                 pr_ref) -> ExitCode | None:
    """Collect feedback and reject the awaiting gate with it. Returns an exit
    code to stop on (nothing to fix, dry-run, or failure), or None once the
    round is started and recorded at stage 'rejected'."""
    round_no = int(state.get("round") or 0) + 1
    since = _parse_ts(state.get("collectedAt") or "") \
        if state.get("stage") == "done" else None

    findings = git_ops.pr_review_feedback(target, pr_ref)
    if since is not None:
        fresh = [f for f in findings
                 if (_parse_ts(f["at"]) or since) > since]
        report.info("FC-FEEDBACK",
                    f"{len(findings)} feedback item(s) on the PR; "
                    f"{len(fresh)} new since round {round_no - 1}")
    else:
        fresh = findings
        report.info("FC-FEEDBACK",
                    f"{len(findings)} feedback item(s) on the PR")
    if not fresh:
        report.success("FC-CLEAN",
                       "no unaddressed reviewer comments; nothing to fix")
        return report.finish()

    status = _status_json(fw_dir, target, run_id)
    gate = _awaiting_gate(status)
    if gate is None:
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            "no gate on this run is awaiting a decision, so there is nothing "
            "to reject the findings into",
            hint=f"advance the run first ('omn-agent run {task['ticket']}' "
                 "names the next step), then re-run fix-comments")
    role = args.owner_role or _deciding_role(gate)
    if not role:
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"gate '{gate['state_id']}' declares no owner roles",
            hint="pass --owner-role explicitly")

    if args.dry_run:
        fix_phase = _fix_phase(task, status) or gate.get("closes_state") \
            or "the gated phase"
        report.info("FC-PLAN",
                    f"round {round_no}: would reject gate "
                    f"'{gate['state_id']}' as {role} with {len(fresh)} "
                    f"finding(s), authorise a rollback to {fix_phase} as the "
                    f"same role, re-dispatch that phase, and record the "
                    f"feedback under {tdir / 'fix-comments'}")
        report.print()
        return ExitCode.DRY_RUN

    collected_at = _now()
    findings_rel = _write_findings(tdir, fresh, round_no, pr_ref, collected_at)
    report.info("FC-FINDINGS",
                f"recorded {len(fresh)} finding(s) to {tdir / findings_rel}")
    rationale = _build_rationale(fresh, round_no, findings_rel)

    _require_approval(f"fix-comments round {round_no}: reject gate "
                      f"{gate['state_id']}", tdir, args.approve, task)
    rc, _ = _invoke(fw_dir, target, [
        "gate", "--run-id", run_id, "--gate", gate["state_id"],
        "--decision", "reject", "--owner-role", role,
        "--decided-by", args.decided_by or getpass.getuser(),
        "--rationale", rationale], report)
    task["fixComments"] = {
        "round": round_no, "stage": "rejected", "gate": gate["state_id"],
        "ownerRole": role, "collectedAt": collected_at,
        "findings": len(fresh), "findingsFile": findings_rel,
    }
    save_task(tdir, task)
    if rc != 0:
        report.error("FC-GATE",
                     f"rejecting gate '{gate['state_id']}' failed (exit {rc}); "
                     "the runtime output above is authoritative",
                     hint=f"inspect with 'omn-agent run {task['ticket']} "
                          "--show', then re-run fix-comments")
        return report.finish(error_code=ExitCode.UNEXPECTED)
    report.success("FC-REJECT",
                   f"gate '{gate['state_id']}' rejected with the round "
                   f"{round_no} findings as rationale")
    return None


def _authorise_rollback(args, report, target, fw_dir, task, tdir, state,
                        run_id) -> ExitCode | None:
    """Authorise the rollback the rejection classified, as the same role that
    rejected, targeting the task's fix phase. Returns an exit code to stop on,
    or None once the runtime shows the fix phase re-entered and the
    authorisation is recorded on the task."""
    gate = state["gate"]
    role = args.owner_role or state.get("ownerRole")
    status = _status_json(fw_dir, target, run_id)
    fix_phase = _fix_phase(task, status)
    argv = ["rollback", "--run-id", run_id, "--gate", gate,
            "--owner-role", role,
            "--decided-by", args.decided_by or getpass.getuser(),
            "--rationale",
            f"review-comment fix round {state['round']}: rollback to "
            f"{fix_phase or 'the gated phase'} authorised so the findings in "
            f"{state.get('findingsFile') or 'the rejection'} are rebuilt against"]
    if fix_phase:
        argv += ["--target", fix_phase]
    _require_approval(f"fix-comments round {state['round']}: authorise rollback "
                      f"past gate {gate} to {fix_phase or 'the gated phase'}",
                      tdir, args.approve, task)
    rc, _ = _invoke(fw_dir, target, argv, report)
    status = _status_json(fw_dir, target, run_id)
    step = _rolled_back_step(status, gate)
    if rc != 0 and step is None:
        save_task(tdir, task)
        report.error("FC-ROLLBACK",
                     f"authorising the rollback past gate '{gate}' failed "
                     f"(exit {rc}); the gate stays rejected and no phase is "
                     "dispatchable",
                     hint=f"inspect with 'omn-agent run {task['ticket']} "
                          "--show' (the gate's failure envelope names the "
                          "exact rollback command), then re-run fix-comments")
        return report.finish(error_code=ExitCode.UNEXPECTED)
    rb = (step or {}).get("rollback") or {}
    state["rollback"] = {
        "authorisationId": rb.get("authorisation_id"),
        "target": (step or {}).get("state_id") or fix_phase,
        "supersededAttempt": rb.get("superseded_attempt"),
        "ownerRole": role,
    }
    save_task(tdir, task)
    if rc != 0:
        report.info("FC-ROLLBACK",
                    f"the runtime already shows the rollback past '{gate}' "
                    "authorised; continuing from it")
    report.success("FC-ROLLBACK",
                   f"rollback {rb.get('authorisation_id') or ''} past gate "
                   f"'{gate}' authorised as {role}: phase "
                   f"'{state['rollback']['target']}' re-enters as a new attempt "
                   "carrying the findings")
    return None


def _dispatch_fix(args, report, target, fw_dir, task, tdir, state, run_id,
                  wt) -> ExitCode:
    status = _status_json(fw_dir, target, run_id)
    step = _dispatchable_step(status)
    if step is None:
        report.error("FC-DISPATCH",
                     "the rollback is authorised but no phase became "
                     "dispatchable",
                     hint=f"inspect with 'omn-agent run {task['ticket']} "
                          "--show'; once a phase is pending, re-run "
                          "fix-comments")
        return report.finish(error_code=ExitCode.UNEXPECTED)

    _require_approval(f"fix-comments round {state['round']}: dispatch phase "
                      f"{step['state_id']}", tdir, args.approve, task)
    rc, _ = _invoke(fw_dir, target, [
        "dispatch", "--run-id", run_id, "--phase", step["state_id"]], report)
    if rc != 0:
        save_task(tdir, task)
        report.error("FC-DISPATCH",
                     f"dispatching phase '{step['state_id']}' failed "
                     f"(exit {rc})",
                     hint=f"inspect with 'omn-agent run {task['ticket']} "
                          "--show', then re-run fix-comments")
        return report.finish(error_code=ExitCode.UNEXPECTED)

    state["stage"] = "dispatched"
    state["phase"] = step["state_id"]
    save_task(tdir, task)
    report.success("FC-DISPATCH",
                   f"phase '{step['state_id']}' dispatched to "
                   f"{step.get('owner_agent_id') or 'its owner agent'} with "
                   "the findings carried as the prior rejection")
    report.info("FC-WAIT",
                f"the host must now run the dispatched subagent, which fixes "
                f"the findings in worktree '{wt}'; when it is done, re-run "
                f"'omn-agent pr fix-comments {task['ticket']}' to verify, "
                "close the gate, and push")
    return report.finish()


def _complete_fix(args, report, target, fw_dir, task, tdir, state,
                  run_id) -> ExitCode | None:
    phase = state["phase"]
    _require_approval(f"fix-comments round {state['round']}: complete phase "
                      f"{phase}", tdir, args.approve, task)
    rc, _ = _invoke(fw_dir, target, [
        "complete", "--run-id", run_id, "--phase", phase], report)
    if rc != 0:
        save_task(tdir, task)
        report.error("FC-COMPLETE",
                     f"completing phase '{phase}' failed (exit {rc}); has the "
                     "dispatched subagent produced its artifact yet?",
                     hint="run the subagent to make the fixes, then re-run "
                          f"'omn-agent pr fix-comments {task['ticket']}'")
        return report.finish(error_code=ExitCode.UNEXPECTED)
    state["stage"] = "fixed"
    save_task(tdir, task)
    report.success("FC-COMPLETE", f"phase '{phase}' completion ingested")
    return None


def _verify_and_push(args, report, target, fw_dir, task, tdir, state, run_id,
                     bound) -> ExitCode:
    passed = run_precheck(target, task, tdir, report, args.test_cmd)
    if not passed:
        report.error("FC-VERIFY",
                     "pre-PR checks failed after the fix; the gate stays "
                     "closed and nothing was pushed",
                     hint="fix the failures in the task's worktree, then "
                          f"re-run 'omn-agent pr fix-comments "
                          f"{task['ticket']}'")
        return report.finish(error_code=ExitCode.VALIDATION_FAILED)

    status = _status_json(fw_dir, target, run_id)
    gate = _awaiting_gate(status)
    if gate is not None:
        role = args.owner_role or state.get("ownerRole") or \
            _deciding_role(gate)
        _require_approval(f"fix-comments round {state['round']}: approve gate "
                          f"{gate['state_id']}", tdir, args.approve, task)
        rc, _ = _invoke(fw_dir, target, [
            "gate", "--run-id", run_id, "--gate", gate["state_id"],
            "--decision", "approve", "--owner-role", role,
            "--decided-by", args.decided_by or getpass.getuser(),
            "--rationale",
            f"review-comment fix round {state['round']} verified: pre-PR "
            f"checks passed (see "
            f"{state.get('findingsFile') or 'the recorded findings'})"],
            report)
        if rc != 0:
            save_task(tdir, task)
            report.error("FC-GATE",
                         f"approving gate '{gate['state_id']}' failed "
                         f"(exit {rc})",
                         hint=f"inspect with 'omn-agent run {task['ticket']} "
                              "--show', then re-run fix-comments")
            return report.finish(error_code=ExitCode.UNEXPECTED)
        report.success("FC-APPROVE",
                       f"gate '{gate['state_id']}' approved on clean "
                       "evidence")
    else:
        report.info("FC-GATE", "no gate is awaiting a decision; skipping "
                    "re-approval")

    _require_approval(f"fix-comments round {state['round']}: push '{bound}' "
                      "to update the PR", tdir, args.approve, task)
    git_ops.push_branch(target, bound)
    state["stage"] = "done"
    state["pushedAt"] = _now()
    save_task(tdir, task)
    report.success("FC-DONE",
                   f"round {state['round']} complete: pushed '{bound}'; the "
                   "PR is updated")
    report.info("FC-NEXT", "reply to / resolve the review threads on the PR "
                "and let CI and Sonar re-scan; re-run fix-comments if new "
                "comments arrive")
    return report.finish()
