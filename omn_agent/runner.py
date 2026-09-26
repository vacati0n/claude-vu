"""Approval-gated driver for the installed framework runtime (`omn-agent run`).

This module never reimplements orchestration. It shells out to the runtime the
installer put in the target repo (``.omn-agent/runtime/framework_runtime.py``),
which owns run state, gates, validation, and recovery. What this wrapper adds:

* every side-effecting runtime step (materializing a run, dispatching a phase,
  ingesting a completion, recording a gate decision) requires explicit
  approval -- ``--approve`` on the command line, or an interactive yes on a
  TTY; otherwise the command stops with exit code 8 and does nothing;
* every approval is recorded to ``.omn-agent/tasks/<KEY>/approvals.jsonl``
  (who, when, which step);
* read-only steps (showing status, reporting the next action) run freely.
"""

from __future__ import annotations

import datetime
import getpass
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

from . import git_ops, worktree
from .common import ExitCode, OmnError, Report
from .repo import framework_root, resolve_target
from .taskplan import load_task, save_task

RUN_ID_RE = re.compile(r"\brun-[0-9a-f]{6,}\b")

# Phases that change code and so must only run inside the task's own worktree.
BRANCH_GUARDED_PHASES = {"implementation"}


def _ensure_implementation_worktree(target: Path, task: dict) -> Path | None:
    """Refuse to dispatch a code-changing phase unless the task's own
    worktree exists and is checked out on its bound branch. Implementation
    never runs in the shared main checkout -- each task's worktree is the
    explicit place its code changes happen, so concurrent tasks stay
    isolated. Returns the worktree path (None outside a git repo)."""
    if not git_ops.is_git_repo(target):
        return None
    bound = (task.get("branch") or {}).get("name")
    if not bound:
        raise OmnError(
            ExitCode.INCOMPLETE,
            f"no feature branch is bound to task {task['ticket']} yet",
            hint=f"run 'omn-agent branch {task['ticket']}' before "
                 "implementation")
    wt = worktree.resolve_task_worktree(target, task)
    current = git_ops.current_branch(wt)
    if git_ops.is_protected(current):
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"task worktree '{wt}' is on protected branch "
            f"'{current or '(detached HEAD)'}'",
            hint=f"re-run 'omn-agent branch {task['ticket']}' to rebind it")
    if current != bound:
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"task worktree '{wt}' is on '{current}' but task "
            f"{task['ticket']} is bound to branch '{bound}'",
            hint=f"git -C \"{wt}\" checkout {bound}, or re-run 'omn-agent "
                 f"branch {task['ticket']}' to rebind")
    return wt


def _require_approval(step: str, tdir: Path, approve_flag: bool, task: dict):
    if approve_flag:
        actor = getpass.getuser()
    elif sys.stdin.isatty():
        try:
            answer = input(f"omn-agent: approve side-effecting step '{step}'? [y/N] ")
        except EOFError:
            answer = ""
        if answer.strip().lower() not in ("y", "yes"):
            raise OmnError(ExitCode.APPROVAL_REQUIRED,
                           f"step '{step}' was not approved; nothing was executed")
        actor = getpass.getuser()
    else:
        raise OmnError(ExitCode.APPROVAL_REQUIRED,
                       f"step '{step}' is side-effecting and requires approval",
                       hint="re-run with --approve (non-interactive) or from a "
                            "terminal to confirm interactively")
    record = {"at": datetime.datetime.now(datetime.timezone.utc)
              .isoformat(timespec="seconds"),
              "actor": actor, "step": step}
    with open(tdir / "approvals.jsonl", "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
    task.setdefault("approvals", []).append(record)


def _runtime(fw_dir: Path) -> Path:
    rt = fw_dir / "runtime" / "framework_runtime.py"
    if not rt.is_file():
        raise OmnError(ExitCode.INCOMPLETE, f"runtime entrypoint missing: {rt}",
                       hint="run 'omn-agent install' to repair the installation")
    return rt


def _invoke(fw_dir: Path, target: Path, argv: list[str],
            report: Report) -> tuple[int, str]:
    cmd = [sys.executable, str(_runtime(fw_dir))] + argv
    report.info("R-EXEC", "runtime: " + " ".join(argv))
    proc = subprocess.run(cmd, cwd=str(target), capture_output=True, text=True)
    out = (proc.stdout or "") + (proc.stderr or "")
    print(out.rstrip())
    return proc.returncode, out


def _show_argv(run_id: str, args) -> list[str]:
    """Build the `status` invocation for `--show`.

    `_invoke` always captures the runtime subprocess's output through a pipe (so it can
    scan it for a run id and fold it into this wrapper's own `Report`), so the runtime
    process itself never sees the real terminal and its own TTY check would always come
    back false. Colorizing is decided here, against *this* process's real stdout, and
    passed down explicitly with `--color`/`--no-color` so a redirected `omn-agent run
    ... --show > file` still gets the plain, byte-for-byte table today's tooling parses.
    """
    argv = ["status", "--run-id", run_id]
    if args.json:
        argv.append("--json")
        return argv
    if args.no_color or os.environ.get("NO_COLOR"):
        argv.append("--no-color")
    elif sys.stdout.isatty():
        argv.append("--color")
    return argv


def _watch(fw_dir: Path, target: Path, argv: list[str], report: Report, *,
           interval: float, max_iterations: int | None = None,
           sleep_fn=time.sleep) -> int:
    """Read-only poll loop over `status --compact`, re-rendering in place.

    Every cycle is a fresh, independent `status` invocation -- the one runtime command
    that never leases, dispatches, completes, or decides a gate -- so leaving this
    running can never advance or approve anything by itself; only a separate
    `--dispatch`/`--complete`/`--gate` call (its own approval prompt) does that.
    `max_iterations` exists for tests; real callers loop until Ctrl+C.
    """
    watch_argv = argv + ["--compact"]
    rc = 0
    iterations = 0
    try:
        while True:
            if sys.stdout.isatty():
                sys.stdout.write("\x1b[2J\x1b[H")
                sys.stdout.flush()
            rc, _ = _invoke(fw_dir, target, watch_argv, report)
            iterations += 1
            if max_iterations is not None and iterations >= max_iterations:
                break
            sleep_fn(interval)
    except KeyboardInterrupt:
        print()
    return rc


def cmd_run(args) -> ExitCode:
    if getattr(args, "ticket", None):
        return _run_provider_mode(args)
    used = [name for name, on in _provider_only_flags(args) if on]
    if used:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"{', '.join(used)} only applies to the provider "
                       "mode 'omn-agent run <Provider> <TicketKey>'",
                       hint="e.g. 'omn-agent run Jira ON-115 --gate-policy "
                            "auto --approve'")
    modes = [bool(args.show), bool(args.dispatch), bool(args.complete),
             bool(args.gate), bool(getattr(args, "report", False)),
             bool(getattr(args, "policy_exception", False))]
    if sum(modes) > 1:
        raise OmnError(ExitCode.INVALID_TARGET,
                       "choose one of --show / --report / --dispatch / --complete / "
                       "--gate / --policy-exception")
    if (args.watch or args.json or args.no_color) and not args.show:
        raise OmnError(ExitCode.INVALID_TARGET,
                       "--watch / --json / --no-color only apply to --show")
    if args.watch and args.interval <= 0:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"--interval must be > 0, got {args.interval}")

    target = resolve_target(args.target)
    report = Report("run", str(target))
    fw_dir = framework_root(target)
    task, tdir = load_task(fw_dir, args.key)
    run_id = task.get("runId")

    # ---- read-only paths -------------------------------------------------
    if getattr(args, "report", False):
        if not run_id:
            report.info("R-STATE", f"task {task['ticket']} is planned but no runtime "
                        "run exists yet, so there is nothing to report on")
            return report.finish()
        rc, _ = _invoke(fw_dir, target, ["report", "--run-id", run_id], report)
        return ExitCode.OK if rc == 0 else ExitCode.UNEXPECTED

    if args.show:
        if not run_id:
            report.info("R-STATE", f"task {task['ticket']} is planned but no runtime "
                        "run exists yet")
            return report.finish()
        argv = _show_argv(run_id, args)
        if args.watch:
            rc = _watch(fw_dir, target, argv, report, interval=args.interval)
            return ExitCode.OK if rc == 0 else ExitCode.UNEXPECTED
        rc, _ = _invoke(fw_dir, target, argv, report)
        return ExitCode.OK if rc == 0 else ExitCode.UNEXPECTED

    base = ["--run-id", run_id] if run_id else \
        ["--command", task["command"],
         "--input-file", str(fw_dir / task["inputFile"]),
         "--input-type", task["inputType"],
         "--requester", f"omn-agent:{getpass.getuser()}"]
    if getattr(args, "gate_policy", None):
        base += ["--gate-policy", args.gate_policy]
    if getattr(args, "demo", False):
        # Idempotent on the runtime side: the first command that carries it throws the run's
        # demo switch (backfilling a run already in flight); later ones find it thrown.
        base += ["--demo"]

    # ---- side-effecting paths (approval required) ------------------------
    if args.dispatch:
        if args.phase in BRANCH_GUARDED_PHASES:
            wt = _ensure_implementation_worktree(target, task)
            if wt is not None:
                report.info("R-WORKTREE",
                            f"task {task['ticket']} implements in worktree "
                            f"'{wt}' on branch '{task['branch']['name']}' -- "
                            "all code changes go there, never in the shared "
                            "checkout")
        _require_approval(f"dispatch phase {args.phase or '(next)'}", tdir,
                          args.approve, task)
        argv = ["dispatch"] + base + (["--phase", args.phase] if args.phase else [])
        rc, _ = _invoke(fw_dir, target, argv, report)
        save_task(tdir, task)
        return _finish(report, task, rc, "dispatch")

    if args.complete:
        if not args.phase:
            raise OmnError(ExitCode.INVALID_TARGET, "--complete requires --phase")
        _require_approval(f"complete phase {args.phase}", tdir, args.approve, task)
        rc, _ = _invoke(fw_dir, target, ["complete"] + base + ["--phase", args.phase],
                        report)
        save_task(tdir, task)
        return _finish(report, task, rc, "complete")

    if getattr(args, "policy_exception", False):
        if not args.phase:
            raise OmnError(ExitCode.INVALID_TARGET,
                           "--policy-exception requires --phase")
        if not (args.owner_role and args.rationale):
            raise OmnError(ExitCode.INVALID_TARGET,
                           "--policy-exception requires --owner-role and --rationale")
        _require_approval(f"policy exception on phase {args.phase}", tdir,
                          args.approve, task)
        argv = ["policy-exception"] + base + [
            "--phase", args.phase,
            "--owner-role", args.owner_role,
            "--decided-by", args.decided_by or getpass.getuser(),
            "--rationale", args.rationale]
        rc, _ = _invoke(fw_dir, target, argv, report)
        save_task(tdir, task)
        return _finish(report, task, rc, "policy-exception")

    if args.gate:
        if not (args.decision and args.rationale and args.owner_role):
            raise OmnError(ExitCode.INVALID_TARGET,
                           "--gate requires --decision, --owner-role and --rationale")
        _require_approval(f"gate {args.gate}: {args.decision}", tdir, args.approve,
                          task)
        argv = ["gate"] + base + [
            "--gate", args.gate, "--decision", args.decision,
            "--owner-role", args.owner_role,
            "--decided-by", args.decided_by or getpass.getuser(),
            "--rationale", args.rationale]
        rc, _ = _invoke(fw_dir, target, argv, report)
        save_task(tdir, task)
        return _finish(report, task, rc, "gate")

    # ---- default: advance one step ---------------------------------------
    if not run_id:
        _require_approval(f"materialize runtime run for {task['ticket']} "
                          f"(/{task['command']})", tdir, args.approve, task)
        rc, out = _invoke(fw_dir, target, ["plan"] + base, report)
        if rc == 0:
            m = RUN_ID_RE.search(out)
            if m:
                task["runId"] = m.group(0)
                report.success("R-RUN", f"runtime run {task['runId']} materialized "
                               f"for {task['ticket']}")
            else:
                report.warning("R-RUNID", "runtime did not report a run id; record "
                               "it manually in task-plan.json if needed")
        save_task(tdir, task)
        if rc == 0:
            report.info("R-NEXT", f"see the next actionable step with "
                        f"'omn-agent run {task['ticket']}'")
        return _finish(report, task, rc, "plan")

    rc, _ = _invoke(fw_dir, target, ["next"] + base, report)
    if rc == 0:
        report.info("R-NEXT", "the NEXT line above names the step; execute it via "
                    f"'omn-agent run {task['ticket']} --dispatch/--complete/--gate "
                    "...' (approval required)")
    return _finish(report, task, rc, "next")


def _provider_only_flags(args) -> list[tuple[str, bool]]:
    return [("--no-fetch", bool(getattr(args, "no_fetch", False))),
            ("--command", bool(getattr(args, "command", None))),
            ("--test-cmd", bool(getattr(args, "test_cmd", None))),
            ("--base", bool(getattr(args, "base", None))),
            ("--draft", bool(getattr(args, "draft", False))),
            ("--dry-run", bool(getattr(args, "dry_run", False)))]


def _run_provider_mode(args) -> ExitCode:
    """'omn-agent run <Provider> <TicketKey>': drive the ticket end to end
    through the named MCP connector. Step-level flags belong to the legacy
    single-argument mode, which is unchanged."""
    stepwise = [("--show", args.show),
                ("--report", bool(getattr(args, "report", False))),
                ("--watch", args.watch), ("--json", args.json),
                ("--no-color", args.no_color), ("--dispatch", args.dispatch),
                ("--complete", args.complete), ("--gate", bool(args.gate)),
                ("--phase", bool(args.phase)),
                ("--decision", bool(args.decision))]
    used = [name for name, on in stepwise if on]
    if used:
        raise OmnError(
            ExitCode.INVALID_TARGET,
            f"{', '.join(used)} cannot be combined with the provider mode "
            "'omn-agent run <Provider> <TicketKey>'",
            hint="the provider mode drives the whole flow itself; for "
                 f"step-level control use 'omn-agent run {args.ticket} "
                 "--show/--dispatch/--complete/--gate ...' on the planned "
                 "task")
    from . import update
    args.provider, args.key = args.key, args.ticket
    return update.cmd_run_ticket(args)


def _finish(report: Report, task: dict, rc: int, step: str) -> ExitCode:
    if rc != 0:
        report.error("R-RUNTIME", f"runtime step '{step}' exited with {rc}; its "
                     "output above is authoritative",
                     hint=f"inspect the run with 'omn-agent run {task['ticket']} "
                          "--show'")
        return report.finish(error_code=ExitCode.UNEXPECTED)
    report.success("R-OK", f"runtime step '{step}' completed")
    return report.finish()
