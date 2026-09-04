"""Git and GitHub CLI primitives for the branch/PR lifecycle.

Every function shells out to the real ``git`` (and, for PR creation, ``gh``)
binaries and translates failure into :class:`OmnError` with an actionable
hint -- this module never guesses at repository state, it asks git.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

from .common import ExitCode, OmnError

PROTECTED_BRANCHES = {"main", "master"}

_GITHUB_HTTPS_RE = re.compile(r"^https?://(?:[^/]+@)?github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?/?$")
_GITHUB_SSH_RE = re.compile(r"^git@github\.com:(?P<owner>[^/]+)/(?P<repo>[^/]+?)(?:\.git)?$")


def _run(argv: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return _run(["git", *args], cwd)


def _git_ok(args: list[str], cwd: Path) -> bool:
    return _git(args, cwd).returncode == 0


def is_git_repo(cwd: Path) -> bool:
    return _git_ok(["rev-parse", "--is-inside-work-tree"], cwd)


def current_branch(cwd: Path) -> str | None:
    """The current branch name, or None on detached HEAD."""
    proc = _git(["symbolic-ref", "--short", "-q", "HEAD"], cwd)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def is_dirty(cwd: Path,
            exclude: tuple[str, ...] = (".omn-agent", ".mcp.json",
                                        ".worktrees")) -> bool:
    """True if the working tree has uncommitted changes, ignoring the
    framework's own bookkeeping by default -- ``.omn-agent/`` (tickets/tasks/
    runs state written on every plan/run step), ``.mcp.json`` (the Jira
    connector registration), and ``.worktrees/`` (per-task isolated
    checkouts) are the tool's own operational writes, not the user's
    unrelated in-progress changes."""
    args = ["status", "--porcelain"]
    if exclude:
        args += ["--", ".", *(f":(exclude){e}" for e in exclude)]
    proc = _git(args, cwd)
    return bool(proc.stdout.strip())


def local_branch_exists(cwd: Path, name: str) -> bool:
    return _git_ok(["show-ref", "--verify", "--quiet", f"refs/heads/{name}"], cwd)


def remote_branch_exists(cwd: Path, name: str, remote: str = "origin") -> bool:
    return _git_ok(["show-ref", "--verify", "--quiet", f"refs/remotes/{remote}/{name}"], cwd)


def has_remote(cwd: Path, remote: str = "origin") -> bool:
    return _git_ok(["remote", "get-url", remote], cwd)


def remote_url(cwd: Path, remote: str = "origin") -> str | None:
    proc = _git(["remote", "get-url", remote], cwd)
    return proc.stdout.strip() if proc.returncode == 0 else None


def fetch(cwd: Path, remote: str = "origin") -> bool:
    """Fetch ``remote``. Returns False when no such remote is configured
    (nothing to fetch, not an error). Raises OmnError if a configured
    remote's fetch actually fails."""
    if not has_remote(cwd, remote):
        return False
    proc = _git(["fetch", remote, "--prune"], cwd)
    if proc.returncode != 0:
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"git fetch from '{remote}' failed",
            hint=(proc.stderr or proc.stdout or "").strip() or
                 "check network access and remote credentials, then retry")
    return True


def resolve_base_branch(cwd: Path, preferred: str | None = None,
                         remote: str = "origin") -> str:
    """Resolve the base branch to branch from.

    An explicit ``preferred`` (``--base``) must exist locally or on the
    remote, or this fails outright -- it is never silently substituted.
    With no preference, tries ``main`` then ``master``."""
    if preferred:
        if local_branch_exists(cwd, preferred) or \
                remote_branch_exists(cwd, preferred, remote):
            return preferred
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"base branch '{preferred}' does not exist locally or on "
            f"'{remote}'",
            hint="create it first, or omit --base to use the default "
                 "(main, falling back to master)")
    for c in ("main", "master"):
        if local_branch_exists(cwd, c) or remote_branch_exists(cwd, c, remote):
            return c
    raise OmnError(
        ExitCode.VALIDATION_FAILED,
        "no base branch found (tried: main, master)",
        hint="create one of these branches, or pass --base with an existing "
             "branch name")


def resolve_ref(cwd: Path, name: str, remote: str = "origin") -> str | None:
    """The ref to inspect for ``name``: the remote-tracking ref when it exists
    (the freshest view after a fetch), else the local branch, else None."""
    if remote_branch_exists(cwd, name, remote):
        return f"{remote}/{name}"
    if local_branch_exists(cwd, name):
        return name
    return None


def describe_commit(cwd: Path, ref: str) -> dict | None:
    """``{hash, date, subject}`` of ``ref``'s tip, or None when it doesn't resolve."""
    proc = _git(["log", "-1", "--format=%H%x00%ad%x00%s", "--date=short", ref], cwd)
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    parts = proc.stdout.strip().split("\x00")
    if len(parts) != 3:
        return None
    return {"hash": parts[0], "date": parts[1], "subject": parts[2]}


def most_recently_active_branch(cwd: Path, *, exclude: set[str] = frozenset(),
                                remote: str = "origin") -> str | None:
    """The long-lived branch with the most recent commit, by committer date.

    Looks across local heads and remote-tracking branches, normalizes
    ``<remote>/x`` to ``x``, and skips HEAD pointers and anything in
    ``exclude``. Returns None when nothing but the excluded branches exists.
    """
    proc = _git(["for-each-ref", "--sort=-committerdate",
                 "--format=%(refname:short)", "refs/heads",
                 f"refs/remotes/{remote}"], cwd)
    if proc.returncode != 0:
        return None
    for ref in proc.stdout.splitlines():
        ref = ref.strip()
        if not ref or ref.endswith("/HEAD") or ref == "HEAD":
            continue
        name = ref[len(remote) + 1:] if ref.startswith(f"{remote}/") else ref
        if name in exclude:
            continue
        return name
    return None


def commits_behind(cwd: Path, base: str, other: str,
                   remote: str = "origin") -> int | None:
    """How many commits ``other`` has that ``base`` doesn't, or None when
    either ref doesn't resolve. Advisory only -- never raises."""
    base_ref = resolve_ref(cwd, base, remote)
    other_ref = resolve_ref(cwd, other, remote)
    if not base_ref or not other_ref:
        return None
    proc = _git(["rev-list", "--count", f"{base_ref}..{other_ref}"], cwd)
    if proc.returncode != 0:
        return None
    try:
        return int(proc.stdout.strip())
    except ValueError:
        return None


# ---- worktrees --------------------------------------------------------------
#
# Tasks never switch the shared checkout: each one gets its own worktree, so
# any number of tasks can run concurrently without colliding on a working
# directory. These are the raw git primitives; the task<->worktree binding
# rules live in the `worktree` module.

def same_path(a: Path | str, b: Path | str) -> bool:
    """Filesystem-level path equality (case- and separator-insensitive where
    the OS is), tolerant of paths that don't exist yet."""
    return os.path.normcase(os.path.normpath(os.path.abspath(str(a)))) == \
        os.path.normcase(os.path.normpath(os.path.abspath(str(b))))


def list_worktrees(cwd: Path) -> list[dict]:
    """Every worktree registered on the repository, main working tree first:
    ``{path: Path, branch: str | None}`` (branch is None on detached HEAD)."""
    proc = _git(["worktree", "list", "--porcelain"], cwd)
    if proc.returncode != 0:
        raise OmnError(ExitCode.UNEXPECTED, "'git worktree list' failed",
                       hint=(proc.stderr or proc.stdout or "").strip())
    entries: list[dict] = []
    current: dict | None = None
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line:
            current = None
            continue
        key, _, value = line.partition(" ")
        if key == "worktree":
            current = {"path": Path(value), "branch": None}
            entries.append(current)
        elif key == "branch" and current is not None:
            current["branch"] = value.removeprefix("refs/heads/")
    return entries


def worktree_holding_branch(cwd: Path, branch: str,
                            entries: list[dict] | None = None) -> Path | None:
    """The worktree (main working tree included) that has ``branch`` checked
    out, or None -- git allows a branch in at most one worktree at a time."""
    for e in entries if entries is not None else list_worktrees(cwd):
        if e["branch"] == branch:
            return e["path"]
    return None


def add_worktree(cwd: Path, path: Path, branch: str,
                 start_point: str | None = None) -> None:
    """Register a new worktree at ``path``. With ``start_point``, creates
    ``branch`` off it; without one, checks out the already-existing
    ``branch``. The main working tree's checkout is never touched."""
    args = ["worktree", "add"]
    if start_point:
        args += ["-b", branch, str(path), start_point]
    else:
        args += [str(path), branch]
    proc = _git(args, cwd)
    if proc.returncode != 0:
        raise OmnError(
            ExitCode.UNEXPECTED,
            f"failed to create worktree at '{path}' for branch '{branch}'",
            hint=(proc.stderr or proc.stdout or "").strip())


def prune_worktrees(cwd: Path) -> None:
    """Drop worktree registrations whose directories no longer exist.
    Advisory only -- never raises."""
    _git(["worktree", "prune"], cwd)


def remove_worktree(cwd: Path, path: Path, force: bool = False) -> None:
    """Remove a registered worktree (directory and registration). Git
    refuses while it holds uncommitted or untracked work unless ``force`` --
    surfaced as an explicit error, never swallowed."""
    args = ["worktree", "remove"]
    if force:
        args.append("--force")
    args.append(str(path))
    proc = _git(args, cwd)
    if proc.returncode != 0:
        raise OmnError(
            ExitCode.VALIDATION_FAILED,
            f"could not remove worktree '{path}'",
            hint=(proc.stderr or proc.stdout or "").strip() or
                 f"inspect it, then 'git worktree remove --force {path}'")


def push_branch(cwd: Path, branch: str, remote: str = "origin") -> None:
    if not has_remote(cwd, remote):
        raise OmnError(
            ExitCode.INCOMPLETE, f"no '{remote}' remote is configured",
            hint=f"add one with 'git remote add {remote} <url>', then retry")
    proc = _git(["push", "-u", remote, branch], cwd)
    if proc.returncode != 0:
        raise OmnError(
            ExitCode.UNEXPECTED, f"git push to '{remote}/{branch}' failed",
            hint=(proc.stderr or proc.stdout or "").strip() or
                 "check remote credentials and try 'git push' manually")


def slugify(text: str, max_words: int = 6, max_len: int = 40) -> str:
    words = re.findall(r"[A-Za-z0-9]+", (text or "").lower())
    slug = "-".join(words[:max_words])
    return slug[:max_len].rstrip("-") or "change"


def is_protected(branch: str | None) -> bool:
    return branch is None or branch in PROTECTED_BRANCHES


# ---- GitHub CLI (PR creation) ---------------------------------------------

def gh_path() -> str | None:
    return shutil.which("gh")


def gh_authenticated(cwd: Path) -> bool:
    gh = gh_path()
    if not gh:
        return False
    proc = _run([gh, "auth", "status"], cwd)
    return proc.returncode == 0


def github_compare_url(url: str | None, base: str, head: str) -> str | None:
    if not url:
        return None
    m = _GITHUB_HTTPS_RE.match(url) or _GITHUB_SSH_RE.match(url)
    if not m:
        return None
    return (f"https://github.com/{m['owner']}/{m['repo']}"
            f"/compare/{base}...{head}?expand=1")


def create_pull_request(cwd: Path, *, base: str, head: str, title: str,
                         body: str, draft: bool = False) -> dict:
    """Create a PR with ``gh``. Raises OmnError with exact next-step
    instructions when gh is missing or unauthenticated, never a bare crash."""
    fallback = github_compare_url(remote_url(cwd), base, head)
    fallback_line = (f"open this URL to create the PR by hand: {fallback}"
                      if fallback else
                      "push the branch and open a PR in your Git host's web UI")

    gh = gh_path()
    if not gh:
        raise OmnError(
            ExitCode.INCOMPLETE, "GitHub CLI 'gh' is not installed",
            hint="install it from https://cli.github.com/, run 'gh auth login', "
                 f"then re-run this command -- or {fallback_line}")
    if not gh_authenticated(cwd):
        raise OmnError(
            ExitCode.INCOMPLETE, "'gh' is installed but not authenticated",
            hint=f"run 'gh auth login', then re-run this command -- or {fallback_line}")

    argv = [gh, "pr", "create", "--base", base, "--head", head,
            "--title", title, "--body", body]
    if draft:
        argv.append("--draft")
    proc = _run(argv, cwd)
    if proc.returncode != 0:
        raise OmnError(
            ExitCode.UNEXPECTED, "'gh pr create' failed",
            hint=(proc.stderr or proc.stdout or "").strip() or fallback_line)
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    url = lines[-1] if lines else ""
    return {"url": url}


def _require_gh(cwd: Path) -> str:
    gh = gh_path()
    if not gh:
        raise OmnError(
            ExitCode.INCOMPLETE, "GitHub CLI 'gh' is not installed",
            hint="install it from https://cli.github.com/ and run 'gh auth login'")
    if not gh_authenticated(cwd):
        raise OmnError(
            ExitCode.INCOMPLETE, "'gh' is installed but not authenticated",
            hint="run 'gh auth login', then retry")
    return gh


def _gh_json(gh: str, argv: list[str], cwd: Path, what: str):
    proc = _run([gh, *argv], cwd)
    if proc.returncode != 0:
        raise OmnError(ExitCode.UNEXPECTED, f"{what} failed",
                       hint=(proc.stderr or proc.stdout or "").strip() or
                            "run the gh command by hand to see why")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise OmnError(ExitCode.UNEXPECTED,
                       f"{what} returned output that is not valid JSON",
                       hint=str(exc))


def pr_review_feedback(cwd: Path, pr_ref: str) -> list[dict]:
    """Every piece of reviewer feedback on a PR, oldest first, each as
    ``{kind, author, body, path, line, at}``: issue comments, review bodies
    (approvals with no text carry no feedback and are skipped), and inline
    review comments. Bot comments (Sonar and friends) are included; the PR
    author's own comments are excluded -- their replies in a thread are not
    findings. Any gh failure surfaces as an OmnError carrying gh's own
    message, never a silent empty list."""
    gh = _require_gh(cwd)
    view = _gh_json(gh, ["pr", "view", pr_ref, "--json",
                         "number,author,comments,reviews"], cwd,
                    f"'gh pr view {pr_ref}'")
    pr_author = ((view.get("author") or {}).get("login") or "").lower()

    items: list[dict] = []

    def add(kind, author, body, at, path=None, line=None):
        body = (body or "").strip()
        author = author or ""
        if not body or author.lower() == pr_author:
            return
        items.append({"kind": kind, "author": author, "body": body,
                      "at": at or "", "path": path, "line": line})

    for c in view.get("comments") or []:
        add("comment", (c.get("author") or {}).get("login"),
            c.get("body"), c.get("createdAt"))
    for r in view.get("reviews") or []:
        state = (r.get("state") or "").lower()
        add(f"review:{state}" if state else "review",
            (r.get("author") or {}).get("login"),
            r.get("body"), r.get("submittedAt"))

    number = view.get("number")
    if number:
        inline = _gh_json(
            gh, ["api", f"repos/{{owner}}/{{repo}}/pulls/{number}/comments"
                        "?per_page=100"], cwd,
            f"fetching inline review comments for PR #{number}")
        for c in inline or []:
            add("inline", (c.get("user") or {}).get("login"),
                c.get("body"), c.get("created_at"),
                path=c.get("path"),
                line=c.get("line") or c.get("original_line"))

    items.sort(key=lambda f: f["at"])
    return items
