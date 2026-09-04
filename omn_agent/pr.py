"""Pre-PR quality gates and Pull Request creation (`omn-agent pr ...`).

Two steps, usable independently or chained:

    omn-agent pr precheck KEY -t <repo>   # branch guard + tests, no PR
    omn-agent pr create   KEY -t <repo>   # precheck (unless --skip-checks),
                                          # then open a PR via 'gh', or fail
                                          # safely with exact next steps

Both require a branch and worktree already bound to the task by ``omn-agent
branch``. Checks run inside the task's own isolated worktree -- never the
shared main checkout -- and both refuse a worktree that is missing, on a
protected branch (main/master), or on a branch other than the one recorded
for the task.
"""

from __future__ import annotations

import datetime
import shutil
import subprocess
import sys

from .common import ExitCode, OmnError, Report
from . import git_ops, worktree
from .repo import framework_root, resolve_target
from .taskplan import load_task, save_task
from .tickets import load_ticket

MAX_RECORDED_OUTPUT = 4000


def _require_worktree(target, task):
    """The task's bound branch plus the isolated worktree it is checked out
    in, verified -- PR steps never trust the shared checkout's state."""
    bound = (task.get("branch") or {}).get("name")
    if not bound:
        raise OmnError(
            ExitCode.INCOMPLETE, f"no branch is bound to task {task['ticket']}",
            hint=f"run 'omn-agent branch {task['ticket']}' first")
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
            f"{task['ticket']} is bound to '{bound}'",
            hint=f"git -C \"{wt}\" checkout {bound}, or re-run 'omn-agent "
                 f"branch {task['ticket']}' to rebind")
    return bound, wt


def _detect_test_command(target) -> list[str] | None:
    if (target / "tests").is_dir():
        return [sys.executable, "-m", "unittest", "discover", "-s", "tests"]
    if (target / "pyproject.toml").exists() and shutil.which("pytest"):
        return ["pytest"]
    if (target / "package.json").exists() and shutil.which("npm"):
        return ["npm", "test", "--silent"]
    return None


def run_precheck(target, task, tdir, report: Report, test_cmd: str | None) -> bool:
    """Run the worktree guard and quality gate. Returns whether it passed.
    Records the outcome on the task either way. Tests run inside the task's
    own worktree, where its code changes actually live."""
    _, wt = _require_worktree(target, task)
    report.success("PR-BRANCH", f"task worktree is on bound branch "
                    f"'{task['branch']['name']}'")

    def _record(code_base: str, label: str, passed: bool, output: str):
        if passed:
            report.success(f"{code_base}-OK", f"{label} passed")
        else:
            report.error(f"{code_base}-FAIL", f"{label} failed",
                        hint=output.strip()[-500:] or "(no output)")

    command_str = None
    if test_cmd:
        command_str = test_cmd
        proc = subprocess.run(test_cmd, cwd=str(wt), shell=True,
                              capture_output=True, text=True)
        passed = proc.returncode == 0
        output = ((proc.stdout or "") + (proc.stderr or ""))[-MAX_RECORDED_OUTPUT:]
        _record("PR-TEST", f"test command '{test_cmd}'", passed, output)
    else:
        detected = _detect_test_command(wt)
        if detected is None:
            passed = True
            output = ""
            report.warning("PR-TEST-SKIP", "no test command detected "
                            "(no tests/, pyproject.toml+pytest, or package.json); "
                            "pass --test-cmd to run one",
                            hint="quality gates are not verified for this run")
        else:
            command_str = " ".join(detected)
            proc = subprocess.run(detected, cwd=str(wt), capture_output=True,
                                  text=True)
            passed = proc.returncode == 0
            output = ((proc.stdout or "") + (proc.stderr or ""))[-MAX_RECORDED_OUTPUT:]
            _record("PR-TEST", f"'{command_str}'", passed, output)

    task["prChecks"] = {
        "passed": passed,
        "command": command_str,
        "output": output,
        "at": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds"),
    }
    save_task(tdir, task)
    return passed


def cmd_pr_precheck(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("pr precheck", str(target))
    fw_dir = framework_root(target)
    task, tdir = load_task(fw_dir, args.key)
    passed = run_precheck(target, task, tdir, report, args.test_cmd)
    if passed:
        report.info("PR-NEXT", f"ready: 'omn-agent pr create {task['ticket']}'")
    return report.finish()


def _pr_title_and_body(task, ticket) -> tuple[str, str]:
    branch = task["branch"]
    key = task["ticket"]
    summary = task.get("summary", "") or key
    title = f"{branch['type']}({key}): {summary}"

    ticket_line = ticket.get("url") if ticket else None
    ticket_line = ticket_line or key
    checks = task.get("prChecks") or {}
    tests_line = ("automated tests passed" if checks.get("passed") and
                  checks.get("command") else
                  "no automated test command was run (see --test-cmd)"
                  if checks.get("passed") else "automated tests failed")

    body = (
        f"## Summary\n\n{summary}\n\n"
        f"## Ticket\n\n{ticket_line}\n\n"
        f"## Changes\n\n"
        f"- Implemented via the Omn-Agent `{task.get('workflow', '')}` workflow "
        f"(branch `{branch['name']}` off `{branch['base']}`).\n\n"
        f"## Testing\n\n- {tests_line}\n\n"
        f"## Checklist\n\n"
        f"- [x] Acceptance criteria addressed (see ticket)\n"
        f"- [{'x' if checks.get('passed') else ' '}] Automated tests pass\n"
        f"- [ ] Reviewed\n\n"
        f"Closes {key}\n"
    )
    return title, body


def cmd_pr_create(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("pr create", str(target))
    fw_dir = framework_root(target)
    task, tdir = load_task(fw_dir, args.key)

    if not (task.get("branch") or {}).get("name"):
        raise OmnError(ExitCode.INCOMPLETE,
                       f"no branch is bound to task {task['ticket']}",
                       hint=f"run 'omn-agent branch {task['ticket']}' first")

    if args.dry_run:
        report.info("PR-PLAN", f"would run pre-PR checks (unless --skip-checks) "
                    f"then open a PR for branch '{task['branch']['name']}' "
                    f"against '{args.base or task['branch']['base']}'")
        report.print()
        return ExitCode.DRY_RUN

    if args.skip_checks:
        report.warning("PR-SKIP", "pre-PR checks skipped (--skip-checks)")
        _require_worktree(target, task)
    else:
        passed = run_precheck(target, task, tdir, report, args.test_cmd)
        if not passed:
            return report.finish(error_code=ExitCode.VALIDATION_FAILED)

    base = args.base or task["branch"]["base"]
    head = task["branch"]["name"]
    git_ops.push_branch(target, head)
    report.success("PR-PUSH", f"pushed '{head}' to origin")

    try:
        ticket = load_ticket(fw_dir, task["ticket"])
    except OmnError:
        ticket = None
    title, body = _pr_title_and_body(task, ticket)

    result = git_ops.create_pull_request(target, base=base, head=head,
                                         title=title, body=body,
                                         draft=args.draft)
    task["pr"] = {
        "url": result["url"],
        "base": base,
        "head": head,
        "createdAt": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds"),
    }
    save_task(tdir, task)
    report.success("PR-CREATE", f"opened PR: {result['url'] or '(see gh output above)'}")
    return report.finish()
