"""One-command Jira change-request loop (`omn-agent update`).

A ticket changed in Jira and the in-flight (or already delivered) work must
follow. One resumable command runs the whole designed cycle, stopping only
where a human or the host platform is required:

1. refresh the ticket from Jira into the inbox (``--no-fetch`` skips it);
2. re-plan the task -- regenerating ``input.md``; an unchanged ticket is a
   no-op, so re-running is always safe;
3. carry the change into the runtime run:
   - no run yet: materialize one from the fresh input;
   - a run is recorded and the input changed: archive the run id to
     ``runHistory`` and materialize a new run from the updated input --
     whether the run was in flight or already completed. The runtime pins
     every supplied input digest at run creation and re-verifies it on
     every operation (gate and complete included), so a regenerated
     ``input.md`` can never be carried into an existing run: "a changed
     input is a new run";
4. drive the run: dispatch every eligible phase to its owner agent (the
   implementation phase auto-binds its branch/worktree when missing), ingest
   completions, and stop only where the host must run a dispatched subagent
   or a human must decide a held gate (``--gate-policy auto`` lets the
   runtime decide clean-evidence gates itself);
5. on run completion: run the pre-PR quality gate, then push the bound
   branch -- updating the recorded PR, or opening one when none exists.

Every side-effecting step goes through the same approval discipline as
`omn-agent run` (``--approve``, or an interactive yes) and is recorded to
the task's approvals ledger. Round state lives on the task (``updateFlow``
in task-plan.json); each invocation reads it plus live runtime state and
performs every step it can.

The same classify -> route -> materialize -> drive -> deliver core also
powers the multi-provider one-command mode ``omn-agent run <Provider>
<TicketKey>`` (``cmd_run_ticket``): the ticket is fetched through the named
MCP connector (Jira, MSDev/Azure DevOps) instead of the fixed Jira client,
the resolved provider is recorded on the task, and everything downstream --
routing rules, worktree isolation, gate policy, producer-exclusion
governance, resumability, PR delivery -- is identical.
"""

from __future__ import annotations

import datetime
import getpass
import json

from . import git_ops
from .branch import bind_branch
from .common import ExitCode, OmnError, Report
from .fix_comments import (_awaiting_gate, _dispatchable_step, _status_json,
                           _steps)
from .manifest import atomic_write
from .pr import _pr_title_and_body, run_precheck
from .repo import framework_root, resolve_target
from .runner import (BRANCH_GUARDED_PHASES, RUN_ID_RE, _invoke,
                     _ensure_implementation_worktree, _require_approval)
from .taskplan import ROUTES, apply_plan, classify, load_task, save_task
from .tickets import _client, _inbox, load_ticket
from .worktree import is_closed_status

# One invocation never loops forever: every iteration must mutate the run
# (complete or dispatch), and a dispatch ends the invocation anyway, so this
# bound is only a backstop against a misbehaving runtime.
MAX_DRIVE_STEPS = 50


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc) \
        .isoformat(timespec="seconds")


def _refresh_ticket(fw_dir, key: str, report: Report, transport=None, *,
                    client=None, label="Jira") -> dict:
    """Fetch the ticket fresh from its provider into the inbox, reporting
    whether it changed since the stored copy. Defaults to the configured
    Jira connector; the provider mode passes its resolved client."""
    path = _inbox(fw_dir) / f"{key.upper()}.json"
    old = None
    if path.exists():
        try:
            old = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            old = None
    if client is None:
        client = _client(fw_dir, transport)
    ticket = client.issue(key)
    atomic_write(path, (json.dumps(ticket, indent=2, sort_keys=True) + "\n")
                 .encode("utf-8"))
    if old is None:
        report.success("U-TICKET", f"{ticket['key']} fetched from {label} "
                       f"[{ticket.get('type', '')}] {ticket.get('summary', '')}")
    elif old.get("updated") != ticket.get("updated"):
        report.success("U-TICKET", f"{ticket['key']} changed in {label}: updated "
                       f"{ticket.get('updated')} (inbox had "
                       f"{old.get('updated') or 'unknown'})")
    else:
        report.info("U-TICKET", f"{ticket['key']} is unchanged in {label} "
                    f"(updated {ticket.get('updated') or 'unknown'})")
    return ticket


def _active_step(status: dict) -> dict | None:
    """The step currently dispatched to (or being executed by) an agent."""
    for s in _steps(status):
        if s.get("status") in ("leased", "running"):
            return s
    return None


def _base_argv(run_id: str, args) -> list[str]:
    base = ["--run-id", run_id]
    if getattr(args, "gate_policy", None):
        base += ["--gate-policy", args.gate_policy]
    return base


def cmd_update(args, transport=None) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("update", str(target))
    fw_dir = framework_root(target)

    if args.dry_run:
        return _dry_run(args, report, fw_dir)

    # ---- 1. refresh the ticket -------------------------------------------
    if args.no_fetch:
        ticket = load_ticket(fw_dir, args.key)
        report.info("U-TICKET", f"--no-fetch: using the inbox copy of "
                    f"{ticket['key']} (updated "
                    f"{ticket.get('updated') or 'unknown'})")
    else:
        ticket = _refresh_ticket(fw_dir, args.key, report, transport)

    if is_closed_status(ticket.get("status")):
        report.warning("U-CLOSED", f"ticket {ticket['key']} is closed "
                       f"({ticket.get('status')}); nothing to update",
                       hint="reopen the ticket in Jira, or plan the follow-up "
                            "work as a new ticket")
        return report.finish()

    return _execute_flow(args, report, target, fw_dir, ticket)


def cmd_run_ticket(args, transport=None) -> ExitCode:
    """The multi-provider one-command mode: ``omn-agent run <Provider>
    <TicketKey>``. Resolves the provider from the MCP config, fetches the
    ticket through it, and drives the same end-to-end flow as ``update`` --
    classify, route, materialize, bind branch/worktree, dispatch/complete,
    gate policy, and PR delivery. Re-running resumes from live state."""
    from .providers import resolve_provider

    target = resolve_target(args.target)
    report = Report("run", str(target))
    fw_dir = framework_root(target)

    provider = resolve_provider(fw_dir, args.provider, transport=transport)
    report.success("E2E-PROVIDER", f"provider '{args.provider}' resolved to "
                   f"connector '{provider.name}' (kind {provider.kind}, "
                   f"{provider.client.base_url})")

    if args.dry_run:
        return _dry_run_provider(args, report, fw_dir, provider)

    # ---- 1. fetch the ticket from the provider ----------------------------
    if args.no_fetch:
        ticket = load_ticket(fw_dir, args.key)
        report.info("U-TICKET", f"--no-fetch: using the inbox copy of "
                    f"{ticket['key']} (updated "
                    f"{ticket.get('updated') or 'unknown'})")
    else:
        ticket = _refresh_ticket(fw_dir, args.key, report,
                                 client=provider.client,
                                 label=provider.label)

    if is_closed_status(ticket.get("status")):
        report.warning("U-CLOSED", f"ticket {ticket['key']} is closed "
                       f"({ticket.get('status')}); nothing to do",
                       hint=f"reopen the ticket in {provider.label}, or plan "
                            "the follow-up work as a new ticket")
        return report.finish()

    return _execute_flow(args, report, target, fw_dir, ticket,
                         provider=provider.name)


def _execute_flow(args, report: Report, target, fw_dir, ticket,
                  provider: str | None = None) -> ExitCode:
    """Classify, route, and drive one ticket end to end -- the shared core
    of `omn-agent update` and the provider mode of `omn-agent run`."""
    # ---- 2. re-plan --------------------------------------------------------
    command = args.command or classify(ticket)
    if command not in ROUTES:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"unknown command '{command}'; choose from "
                       f"{', '.join(sorted(ROUTES))}")
    task, tdir, changed = apply_plan(fw_dir, ticket, command, report)

    if provider and task.get("provider") != provider:
        task["provider"] = provider
        save_task(tdir, task)
    resume = (f"omn-agent run {provider} {task['ticket']}" if provider
              else f"omn-agent update {task['ticket']}")

    flow = task.get("updateFlow") or {}
    if not changed and flow.get("deliveredHash") == task.get("inputHash"):
        report.success("U-UPTODATE", f"nothing to do: the ticket is unchanged "
                       f"since update round {flow.get('round', '?')} was "
                       "delivered")
        return report.finish()
    if changed:
        flow = {"round": int(flow.get("round") or 0) + 1,
                "inputHash": task["inputHash"], "startedAt": _now()}
        task["updateFlow"] = flow
        save_task(tdir, task)
        report.info("U-ROUND", f"change round {flow['round']}: the routed "
                    f"input changed (hash {task['inputHash'][:12]})")

    # ---- 3. carry the change into the run ----------------------------------
    run_id = task.get("runId")
    status = _status_json(fw_dir, target, run_id) if run_id else None

    if run_id and (changed or flow.get("pendingRunArchive") == run_id):
        _archive_run(args, report, task, tdir, flow, status)
        run_id = None
        status = None

    if not run_id:
        early = _materialize(args, report, target, fw_dir, task, tdir)
        if early is not None:
            return early
        run_id = task["runId"]

    # ---- 4. drive the run ---------------------------------------------------
    base = _base_argv(run_id, args)
    dispatched_now = None
    tried_next_for = None
    for _ in range(MAX_DRIVE_STEPS):
        status = _status_json(fw_dir, target, run_id)
        if status.get("run_status") == "Completed":
            return _deliver(args, report, target, fw_dir, task, tdir,
                            resume=resume)

        active = _active_step(status)
        if active:
            sid = active["state_id"]
            if sid == dispatched_now:
                report.success("U-DISPATCHED", f"phase '{sid}' is dispatched "
                               f"to {active.get('owner_agent_id') or 'its owner agent'}")
                report.info("U-WAIT", "the host must now run the dispatched "
                            f"subagent; when it is done, re-run '{resume}' "
                            "to continue toward the PR")
                return report.finish()
            _require_approval(f"complete phase {sid}", tdir, args.approve, task)
            rc, _ = _invoke(fw_dir, target,
                            ["complete"] + base + ["--phase", sid], report)
            save_task(tdir, task)
            if rc != 0:
                report.error("U-COMPLETE", f"completing phase '{sid}' failed "
                             f"(exit {rc}); has the dispatched subagent "
                             "produced its artifact yet?",
                             hint=f"run the subagent, then re-run '{resume}'")
                return report.finish(error_code=ExitCode.UNEXPECTED)
            report.success("U-COMPLETE", f"phase '{sid}' completion ingested")
            continue

        step = _dispatchable_step(status)
        if step:
            sid = step["state_id"]
            if sid in BRANCH_GUARDED_PHASES:
                _ensure_worktree_bound(args, report, target, fw_dir, task,
                                       tdir)
            _require_approval(f"dispatch phase {sid}", tdir, args.approve,
                              task)
            rc, _ = _invoke(fw_dir, target,
                            ["dispatch"] + base + ["--phase", sid], report)
            save_task(tdir, task)
            if rc != 0:
                report.error("U-DISPATCH", f"dispatching phase '{sid}' failed "
                             f"(exit {rc}); the runtime output above is "
                             "authoritative",
                             hint=f"inspect with 'omn-agent run "
                                  f"{task['ticket']} --show'")
                return report.finish(error_code=ExitCode.UNEXPECTED)
            dispatched_now = sid
            continue

        gate = _awaiting_gate(status)
        if gate:
            # `next` is where the runtime evaluates its gate auto-approval
            # policy; give it one chance per gate before declaring it held.
            if tried_next_for != gate["state_id"]:
                tried_next_for = gate["state_id"]
                _invoke(fw_dir, target, ["next"] + base, report)
                after = _awaiting_gate(_status_json(fw_dir, target, run_id))
                if not after or after["state_id"] != gate["state_id"]:
                    report.success("U-GATE-AUTO", f"gate '{gate['state_id']}' "
                                   "was auto-decided by the runtime's gate "
                                   "policy on clean evidence")
                continue
            roles = ", ".join(gate.get("owner_roles") or []) or "its owner"
            report.info("U-GATE", f"gate '{gate['state_id']}' is held and "
                        f"awaits a human decision ({roles})")
            report.info("U-WAIT", f"decide it with 'omn-agent run "
                        f"{task['ticket']} --gate {gate['state_id']} "
                        "--decision approve --owner-role <role> --rationale "
                        f"...', then re-run '{resume}'" +
                        ("" if getattr(args, "gate_policy", None) else
                         " -- or re-run with --gate-policy auto to let the "
                         "runtime decide clean-evidence gates itself"))
            return report.finish()

        report.warning("U-STALLED", f"run_status="
                       f"{status.get('run_status')} but no phase is "
                       "dispatchable or completable and no gate awaits a "
                       "decision",
                       hint=f"inspect with 'omn-agent run {task['ticket']} "
                            "--show'")
        return report.finish()

    report.error("U-LIMIT", f"stopped after {MAX_DRIVE_STEPS} runtime steps "
                 "in one invocation",
                 hint=f"re-run '{resume}' to continue")
    return report.finish(error_code=ExitCode.UNEXPECTED)


def _dry_run(args, report: Report, fw_dir) -> ExitCode:
    """Describe the round without fetching from Jira or writing anything."""
    from .manifest import sha256_bytes
    from .taskplan import render_input, task_dir

    ticket = load_ticket(fw_dir, args.key)
    command = args.command or classify(ticket)
    if command not in ROUTES:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"unknown command '{command}'; choose from "
                       f"{', '.join(sorted(ROUTES))}")
    workflow, input_type = ROUTES[command]
    new_hash = sha256_bytes(render_input(ticket, command, input_type)
                            .encode("utf-8"))
    task = None
    if (task_dir(fw_dir, ticket["key"]) / "task-plan.json").exists():
        task, _ = load_task(fw_dir, ticket["key"])
    same = task is not None and task.get("inputHash") == new_hash
    run_ref = (task or {}).get("runId") or "(a new run)"
    report.info("U-PLAN", f"would refresh {ticket['key']} from Jira, re-plan "
                f"(/{command} -> {workflow}; inbox copy is currently "
                f"{'unchanged' if same else 'a change'}), carry the change "
                f"into {run_ref}, drive it phase by phase, and push the "
                "result to the PR")
    report.print()
    return ExitCode.DRY_RUN


def _dry_run_provider(args, report: Report, fw_dir, provider) -> ExitCode:
    """Describe the provider-mode round without fetching or writing. Unlike
    `update --dry-run`, the ticket may never have been fetched yet."""
    from .taskplan import task_dir

    key = args.key.upper()
    if not (_inbox(fw_dir) / f"{key}.json").exists():
        report.info("U-PLAN", f"would fetch {key} from {provider.label} "
                    f"(connector '{provider.name}'), classify and route it, "
                    "materialize a runtime run, bind its branch/worktree "
                    "when implementation is needed, drive it phase by phase "
                    "under the gate policy, and push the result to a PR")
        report.print()
        return ExitCode.DRY_RUN

    ticket = load_ticket(fw_dir, key)
    command = args.command or classify(ticket)
    if command not in ROUTES:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"unknown command '{command}'; choose from "
                       f"{', '.join(sorted(ROUTES))}")
    workflow, input_type = ROUTES[command]
    task = None
    if (task_dir(fw_dir, key) / "task-plan.json").exists():
        task, _ = load_task(fw_dir, key)
    run_ref = (task or {}).get("runId") or "(a new run)"
    report.info("U-PLAN", f"would refresh {key} from {provider.label}, "
                f"re-plan (/{command} -> {workflow} [{input_type}]), carry "
                f"any change into {run_ref}, drive it phase by phase, and "
                "push the result to the PR")
    report.print()
    return ExitCode.DRY_RUN


def _materialize(args, report, target, fw_dir, task, tdir) -> ExitCode | None:
    """Materialize the runtime run for the task's current input. Returns an
    exit code to stop on, or None with task['runId'] recorded."""
    _require_approval(f"materialize runtime run for {task['ticket']} "
                      f"(/{task['command']})", tdir, args.approve, task)
    argv = ["plan", "--command", task["command"],
            "--input-file", str(fw_dir / task["inputFile"]),
            "--input-type", task["inputType"],
            "--requester", f"omn-agent:{getpass.getuser()}"]
    if getattr(args, "gate_policy", None):
        argv += ["--gate-policy", args.gate_policy]
    rc, out = _invoke(fw_dir, target, argv, report)
    if rc == 0:
        m = RUN_ID_RE.search(out)
        if m:
            task["runId"] = m.group(0)
            report.success("U-RUN", f"runtime run {task['runId']} "
                           f"materialized for {task['ticket']}")
        else:
            report.warning("U-RUNID", "runtime did not report a run id; "
                           "record it manually in task-plan.json if needed")
    save_task(tdir, task)
    if rc != 0 or not task.get("runId"):
        report.error("U-RUN", f"materializing the runtime run failed "
                     f"(exit {rc}); the runtime output above is "
                     "authoritative",
                     hint=f"inspect with 'omn-agent run {task['ticket']} "
                          "--show'")
        return report.finish(error_code=ExitCode.UNEXPECTED)
    return None


def _archive_run(args, report, task, tdir, flow, status):
    """Archive the recorded run to ``runHistory`` so a new run can be
    materialized from the updated input.

    The runtime pins every supplied input digest at run creation
    (``store.data["input_digest"]``) and re-verifies it on every operation
    -- gate and complete included -- so once apply_plan regenerates input.md
    the existing run refuses everything, even the gate-reject rollback,
    with context-integrity-failure. The only runtime-consistent move is the
    one its error message names: a changed input is a new run.
    """
    run_id = task["runId"]
    if status.get("run_status") == "Completed":
        reason = "ticket updated after run completion"
        report.info("U-RERUN", f"run {run_id} completed before the ticket "
                    "changed; materializing a new run from the updated input")
    else:
        # The archive is owed even if this invocation stops here (approval
        # denied, crash): input.md is already regenerated, so the runtime
        # rejects every operation on this run from now on. Record the debt
        # before asking, so the next invocation -- where `changed` is
        # False because inputHash already advanced -- still finishes the
        # rollover instead of wedging in the drive loop.
        if flow.get("pendingRunArchive") != run_id:
            flow["pendingRunArchive"] = run_id
            task["updateFlow"] = flow
            save_task(tdir, task)
        active = _active_step(status)
        if active:
            report.warning("U-MIDFLIGHT", f"phase '{active['state_id']}' was "
                           "dispatched under the previous input; its run is "
                           "being archived, so any in-flight output is "
                           "superseded by the new run")
        reason = "ticket updated mid-run; a changed input is a new run"
        _require_approval(f"update round {flow.get('round', 1)}: archive "
                          f"in-flight run {run_id} and materialize a new "
                          "run from the updated input", tdir, args.approve,
                          task)
        report.info("U-RERUN", f"run {run_id} was in flight when the ticket "
                    "changed; the runtime pins input digests at run "
                    "creation, so a changed input is a new run")
    task.setdefault("runHistory", []).append(
        {"runId": run_id, "archivedAt": _now(), "reason": reason})
    task["runId"] = None
    flow.pop("pendingRunArchive", None)
    task["updateFlow"] = flow
    save_task(tdir, task)


def _ensure_worktree_bound(args, report, target, fw_dir, task, tdir):
    """Auto-bind the task's feature branch/worktree before a code-changing
    phase is dispatched, so one command covers a task that never ran
    `omn-agent branch`."""
    if not git_ops.is_git_repo(target):
        return
    if not (task.get("branch") or {}).get("name"):
        _require_approval(f"create feature branch and worktree for "
                          f"{task['ticket']}", tdir, args.approve, task)
        bind_branch(target, fw_dir, task, tdir, report, base=args.base)
    wt = _ensure_implementation_worktree(target, task)
    if wt is not None:
        report.info("U-WORKTREE", f"task {task['ticket']} implements in "
                    f"worktree '{wt}' on branch '{task['branch']['name']}'")


def _deliver(args, report, target, fw_dir, task, tdir, *,
             resume: str | None = None) -> ExitCode:
    """The run is complete: verify, then push -- updating the recorded PR,
    or opening one when none exists."""
    resume = resume or f"omn-agent update {task['ticket']}"
    report.success("U-RUN-DONE", f"run {task['runId']} is complete")
    bound = (task.get("branch") or {}).get("name")
    if not bound or not git_ops.is_git_repo(target):
        report.info("U-NO-BRANCH", "no feature branch is bound to this task, "
                    "so there is nothing to push")
        _mark_delivered(task, tdir)
        return report.finish()

    if not run_precheck(target, task, tdir, report, args.test_cmd):
        report.error("U-VERIFY", "pre-PR checks failed; nothing was pushed",
                     hint="fix the failures in the task's worktree, then "
                          f"re-run '{resume}'")
        return report.finish(error_code=ExitCode.VALIDATION_FAILED)

    pr = task.get("pr") or {}
    if pr.get("url"):
        _require_approval(f"push '{bound}' to update PR {pr['url']}", tdir,
                          args.approve, task)
        git_ops.push_branch(target, bound)
        _mark_delivered(task, tdir)
        report.success("U-DONE", f"pushed '{bound}'; PR {pr['url']} is "
                       "updated with the change request")
        return report.finish()

    _require_approval(f"push '{bound}' and open a pull request", tdir,
                      args.approve, task)
    git_ops.push_branch(target, bound)
    report.success("U-PUSH", f"pushed '{bound}' to origin")
    try:
        ticket = load_ticket(fw_dir, task["ticket"])
    except OmnError:
        ticket = None
    title, body = _pr_title_and_body(task, ticket)
    base = args.base or task["branch"]["base"]
    result = git_ops.create_pull_request(target, base=base, head=bound,
                                         title=title, body=body,
                                         draft=args.draft)
    task["pr"] = {"url": result["url"], "base": base, "head": bound,
                  "createdAt": _now()}
    _mark_delivered(task, tdir)
    report.success("U-DONE",
                   f"opened PR: {result['url'] or '(see gh output above)'}")
    return report.finish()


def _mark_delivered(task, tdir):
    flow = task.get("updateFlow") or {"round": 1}
    flow["deliveredHash"] = task.get("inputHash")
    flow["deliveredAt"] = _now()
    task["updateFlow"] = flow
    save_task(tdir, task)
