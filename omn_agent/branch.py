"""Worktree bootstrap from ticket metadata (`omn-agent branch`).

Turns a planned task into a live feature branch inside its own isolated git
worktree. The branch is named per the project's branch naming templates
(``omn-agent branch-config show``; defaults to ``feature/<ticket>-<slug>`` /
``bugfix/<ticket>-<slug>``) and created off the repository's default branch
(``main``/``master``, or ``--base``) -- but never by switching the shared
main checkout. Each task owns ``.worktrees/<ticket>-<work-type>/`` instead,
so any number of tasks can run concurrently without colliding on a working
directory. Both the branch and the worktree are recorded on the task so
later steps -- most importantly dispatching the ``implementation`` phase --
resolve and verify the task's own worktree before any code changes happen.

Guardrails:
    * a missing base branch, or a fetch that fails against a configured
      remote, blocks worktree creation (never silently falls back);
    * the resolved base's tip (hash/date/subject) is always printed, and a
      base dramatically behind the repo's most recently active branch draws
      a loud warning with the actual commit counts, so branching off an
      abandoned ``main`` stub is visible before it happens (a per-repo
      ``config/branch-defaults.json`` ``defaultBase`` avoids it entirely);
    * conflicts are explicit errors: the task's branch checked out anywhere
      else, the worktree path registered to another branch, or an
      unregistered directory already on the path (``--force`` reclaims that
      last one);
    * a dirty main checkout only draws a warning -- the task's worktree is
      created fresh off the base branch and never inherits or disturbs the
      shared tree's uncommitted changes;
    * re-running for a task that already has a bound worktree reuses it, so
      the same task never gets a second worktree (idempotent).
"""

from __future__ import annotations

import datetime

from .common import ExitCode, OmnError, Report
from . import branch_config, git_ops, worktree
from .repo import framework_root, resolve_target
from .taskplan import load_task, save_task


def cmd_branch(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("branch", str(target))
    fw_dir = framework_root(target)
    task, tdir = load_task(fw_dir, args.key)

    if not git_ops.is_git_repo(target):
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"{target} is not a git working tree",
                       hint="run 'git init' in the target repository first")

    if args.dry_run:
        slug = git_ops.slugify(task.get("summary", "") or task["ticket"])
        branch, work_type, template = branch_config.resolve_branch_name(
            fw_dir, command=task["command"], ticket_id=task["ticket"],
            short_description=slug, work_type=args.type)
        wt_path = worktree.task_worktree_path(target, task["ticket"], work_type)
        wt_rel = wt_path.relative_to(target).as_posix()
        existing = (task.get("branch") or {}).get("name")
        holder = git_ops.worktree_holding_branch(target, branch)
        action = "reuse the existing worktree at" \
            if holder is not None and git_ops.same_path(holder, wt_path) \
            else "create worktree"
        report.info("B-PLAN", f"would {action} '{wt_rel}' on branch "
                    f"'{branch}' for {task['ticket']} (work type "
                    f"'{work_type}', template {template!r})" +
                    (f" (currently bound to '{existing}')" if existing and
                     existing != branch else ""))
        report.print()
        return ExitCode.DRY_RUN

    wt_rel = bind_branch(target, fw_dir, task, tdir, report,
                         work_type=args.type, base=args.base,
                         force=args.force)
    report.info("B-NEXT", f"implement inside '{wt_rel}' (the main checkout "
                f"stays untouched), then run 'omn-agent pr create "
                f"{task['ticket']}' once validations pass")
    return report.finish()


def bind_branch(target, fw_dir, task, tdir, report, *, work_type=None,
                base=None, force=False) -> str:
    """Create (or reuse) the task's isolated worktree on its feature branch
    and record both on the task. The extracted core of `omn-agent branch`,
    also driven by `omn-agent update` to auto-bind a task before its
    implementation phase is dispatched. Returns the worktree's repo-relative
    path."""
    slug = git_ops.slugify(task.get("summary", "") or task["ticket"])
    branch, work_type, template = branch_config.resolve_branch_name(
        fw_dir, command=task["command"], ticket_id=task["ticket"],
        short_description=slug, work_type=work_type)
    wt_path = worktree.task_worktree_path(target, task["ticket"], work_type)
    wt_rel = wt_path.relative_to(target).as_posix()

    if git_ops.is_dirty(target):
        report.warning("B-DIRTY-MAIN",
                       "the main checkout has uncommitted changes; the task "
                       "worktree is created fresh off the base branch and "
                       "will not include them",
                       hint="commit or stash them in the main checkout if "
                            "they belong to this task")

    fetched = git_ops.fetch(target)
    if fetched:
        report.info("B-FETCH", "fetched 'origin'")
    else:
        report.warning("B-FETCH", "no 'origin' remote configured; using local "
                        "branches only")

    defaults = branch_config.load_branch_defaults(fw_dir)
    preferred = base or defaults["defaultBase"]
    requested_base = base
    base = git_ops.resolve_base_branch(target, preferred=preferred)
    if not requested_base and defaults["defaultBase"]:
        report.info("B-BASE", f"using configured default base "
                    f"'{defaults['defaultBase']}' "
                    f"({branch_config.DEFAULTS_REL})")

    # Always show what the base actually is, so a stale base is visible in the
    # output even when the divergence heuristic below has nothing to compare to.
    base_ref = git_ops.resolve_ref(target, base)
    tip = git_ops.describe_commit(target, base_ref) if base_ref else None
    if tip:
        report.info("B-BASE-TIP", f"base '{base}' is at {tip['hash'][:12]} "
                    f"({tip['date']}) {tip['subject']}")

    # A default-resolved main/master can be an abandoned stub in a repo whose
    # real integration branch is elsewhere (e.g. develop). Compare the chosen
    # base against the most recently active branch and warn loudly -- with the
    # actual commit counts -- before any branch is created off it.
    freshest = git_ops.most_recently_active_branch(target, exclude={base, branch})
    if freshest:
        behind = git_ops.commits_behind(target, base, freshest)
        threshold = defaults["divergenceWarningThreshold"]
        if behind is not None and behind >= threshold:
            report.warning(
                "B-STALE-BASE",
                f"base '{base}' is {behind} commits behind '{freshest}', the "
                f"most recently active branch in this repository -- the new "
                f"branch will not contain that history",
                hint=f"if '{freshest}' is the real integration branch, re-run "
                     f"with --base {freshest}, or set it once as defaultBase "
                     f"in {branch_config.DEFAULTS_REL}")

    created = worktree.ensure_task_worktree(
        target, path=wt_path, branch=branch, base=base, force=force)

    now = datetime.datetime.now(datetime.timezone.utc) \
        .isoformat(timespec="seconds")
    prev_branch = task.get("branch") or {}
    prev_wt = task.get("worktree") or {}
    reused = not created and prev_wt.get("path") == wt_rel \
        and prev_wt.get("branch") == branch
    task["branch"] = {
        "name": branch,
        "base": base,
        "type": work_type,
        "template": template,
        "createdAt": prev_branch["createdAt"]
        if reused and prev_branch.get("name") == branch else now,
    }
    task["worktree"] = {
        "path": wt_rel,
        "branch": branch,
        "base": base,
        "status": "active",
        "createdAt": prev_wt["createdAt"] if reused else now,
    }
    save_task(tdir, task)

    if created:
        report.success("B-CREATE", f"created worktree '{wt_rel}' on new "
                        f"branch '{branch}' (off '{base}')")
    else:
        report.success("B-REUSE", f"reusing existing worktree '{wt_rel}' on "
                        f"branch '{branch}'")
    return wt_rel
