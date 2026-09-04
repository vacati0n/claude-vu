"""Task-scoped git worktrees: one isolated checkout per task lifecycle.

Every planned task -- whatever its routed command (implement, bugfix,
refactor, investigate, ...) -- does its work inside its own git worktree at
``.worktrees/<ticket>-<work-type>/`` under the target repository, created off
the resolved base branch. The shared main checkout is never switched, so
concurrent tasks can never collide on a working directory. The mapping is
deterministic (the same task identity always resolves to the same path) and
recorded on the task plan (``task["worktree"]``), so re-running a task reuses
its existing worktree instead of creating a duplicate, and later steps
resolve the exact directory to run in instead of trusting the current
working directory.

This module owns the task<->worktree binding rules; the raw ``git worktree``
plumbing lives in :mod:`git_ops`.
"""

from __future__ import annotations

import datetime
import shutil
from pathlib import Path

from . import git_ops
from .common import ExitCode, OmnError

WORKTREES_DIR = ".worktrees"

# Ticket status names (lowercased) that end a task lifecycle. A closed
# ticket's worktree is released automatically on `tickets sync`/`pull`.
CLOSED_STATUS_NAMES = {"done", "closed", "resolved", "cancelled", "canceled",
                       "rejected", "won't do", "wont do", "won't fix",
                       "wont fix", "removed"}


def is_closed_status(status: str | None) -> bool:
    return (status or "").strip().lower() in CLOSED_STATUS_NAMES


def task_worktree_path(target: Path, ticket: str, work_type: str) -> Path:
    """Deterministic worktree location for a task identity: the same
    (ticket, work type) always maps to the same directory."""
    name = git_ops.slugify(f"{ticket} {work_type}", max_words=8, max_len=60)
    return target / WORKTREES_DIR / name


def _ensure_ignored(target: Path) -> None:
    """Keep the worktree container invisible to the main checkout's git
    status: ``.worktrees/.gitignore`` ignores everything inside it (itself
    included), so task isolation never dirties the shared tree."""
    container = target / WORKTREES_DIR
    container.mkdir(parents=True, exist_ok=True)
    gitignore = container / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("*\n", encoding="utf-8")


def ensure_task_worktree(target: Path, *, path: Path, branch: str, base: str,
                         force: bool = False, remote: str = "origin") -> bool:
    """Create the worktree for (``path``, ``branch``), or reuse it when the
    branch is already checked out there. Returns True when newly created.

    Conflicts are explicit errors, never silent fallbacks: the branch checked
    out anywhere else, the path registered to a different branch, and an
    unregistered directory squatting on the path (``force`` reclaims that
    last case) all refuse with the command that resolves them.
    """
    entries = git_ops.list_worktrees(target)
    holder = git_ops.worktree_holding_branch(target, branch, entries=entries)

    if holder is not None:
        if git_ops.same_path(holder, path):
            if path.is_dir():
                return False  # already bound here: reuse, never duplicate
            # The registration outlived a manual delete of the directory;
            # clear the stale record and recreate below.
            git_ops.prune_worktrees(target)
            entries = git_ops.list_worktrees(target)
        elif git_ops.same_path(holder, target):
            raise OmnError(
                ExitCode.VALIDATION_FAILED,
                f"branch '{branch}' is checked out in the main working tree",
                hint=f"tasks run in isolated worktrees; switch the main "
                     f"checkout away first (e.g. 'git checkout {base}') so "
                     f"the task worktree can own '{branch}'")
        else:
            raise OmnError(
                ExitCode.VALIDATION_FAILED,
                f"branch '{branch}' is already checked out in another "
                f"worktree: {holder}",
                hint=f"a task owns exactly one worktree; if that one is "
                     f"stale, remove it with 'git worktree remove {holder}'")

    occupant = next((e for e in entries
                     if git_ops.same_path(e["path"], path)), None)
    if occupant is not None:
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"worktree path '{path}' is already registered to branch "
            f"'{occupant['branch'] or '(detached HEAD)'}'",
            hint=f"remove it with 'git worktree remove {path}' if the task "
                 "using it is finished")

    if path.exists():
        if not force:
            raise OmnError(
                ExitCode.VALIDATION_FAILED,
                f"worktree path already exists but is not a registered git "
                f"worktree: {path}",
                hint="move the directory aside, or re-run with --force to "
                     "delete and recreate it")
        try:
            shutil.rmtree(path)
        except OSError as exc:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"could not remove '{path}': {exc}")

    _ensure_ignored(target)
    if git_ops.local_branch_exists(target, branch):
        git_ops.add_worktree(target, path, branch)
    else:
        start = f"{remote}/{base}" \
            if git_ops.remote_branch_exists(target, base, remote) else base
        git_ops.add_worktree(target, path, branch, start_point=start)
    return True


def resolve_task_worktree(target: Path, task: dict) -> Path:
    """The absolute directory a task's work must run in.

    Never falls back to the shared checkout: an unbound, missing, or
    unregistered worktree is an explicit error naming the rebind command.
    """
    ticket = task.get("ticket", "?")
    info = task.get("worktree") or {}
    rel = info.get("path")
    if not rel:
        raise OmnError(
            ExitCode.INCOMPLETE,
            f"no worktree is bound to task {ticket} yet",
            hint=f"run 'omn-agent branch {ticket}' to create its isolated "
                 "worktree")
    if info.get("status") == "removed":
        raise OmnError(
            ExitCode.INCOMPLETE,
            f"task {ticket}'s worktree was released"
            + (f": {info['reason']}" if info.get("reason") else ""),
            hint=f"re-run 'omn-agent branch {ticket}' to rebind it if work "
                 "must continue")
    path = Path(rel) if Path(rel).is_absolute() else (target / rel).resolve()
    if not path.is_dir():
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"the worktree bound to task {ticket} is missing: {path}",
            hint=f"re-run 'omn-agent branch {ticket}' to recreate it")
    if not any(git_ops.same_path(e["path"], path)
               for e in git_ops.list_worktrees(target)):
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"'{path}' exists but is not a registered git worktree",
            hint=f"re-run 'omn-agent branch {ticket}' to rebind the task")
    return path


def release_task_worktree(target: Path, task: dict, *, reason: str,
                          force: bool = False) -> None:
    """Remove a task's worktree and mark its binding released (``status:
    removed``, with when and why). The branch itself is kept -- releasing
    isolation is not deleting history. Raises when git refuses because the
    worktree still holds uncommitted work and ``force`` is False; the caller
    decides whether that is a skip or a stop."""
    info = task.get("worktree") or {}
    rel = info.get("path")
    if not rel:
        return
    path = Path(rel) if Path(rel).is_absolute() else target / rel
    registered = any(git_ops.same_path(e["path"], path)
                     for e in git_ops.list_worktrees(target))
    if registered and path.is_dir():
        git_ops.remove_worktree(target, path, force=force)
    elif registered:
        git_ops.prune_worktrees(target)
    info.update({
        "status": "removed",
        "reason": reason,
        "removedAt": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds"),
    })
    task["worktree"] = info


def cleanup_closed_ticket_worktrees(target: Path, fw_dir: Path, report, *,
                                    fetch_status) -> None:
    """Release the worktree of every task whose ticket is now closed.

    Called from ``tickets sync``/``tickets pull`` -- the moments status
    knowledge refreshes. ``fetch_status(key)`` returns the ticket's current
    status name, or None when it isn't known (such a task is left alone).
    A worktree that still holds uncommitted work is kept with a loud
    warning, never force-deleted; a status that can't be fetched is a
    per-task warning, never a sweep failure.
    """
    if not git_ops.is_git_repo(target):
        return
    # Deferred import: taskplan imports tickets, which imports this module.
    from .taskplan import iter_tasks, save_task
    for task, tdir in iter_tasks(fw_dir):
        info = task.get("worktree") or {}
        if info.get("status") != "active":
            continue
        key = task.get("ticket") or ""
        try:
            status = fetch_status(key)
        except OmnError as exc:
            report.warning("T-WT-STATUS",
                           f"could not refresh {key}'s status to decide "
                           f"worktree cleanup: {exc.message}")
            continue
        if not is_closed_status(status):
            continue
        try:
            release_task_worktree(target, task,
                                  reason=f"ticket closed ({status})")
        except OmnError as exc:
            report.warning("T-WT-DIRTY",
                           f"{key} is closed ({status}) but its worktree "
                           f"'{info.get('path')}' was kept: {exc.message}",
                           hint=exc.hint)
            continue
        save_task(tdir, task)
        report.success("T-WT-CLEAN", f"{key} is closed ({status}); removed "
                       f"its worktree '{info.get('path')}' (branch "
                       f"'{info.get('branch')}' is kept)")
