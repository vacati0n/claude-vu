"""Target-repository resolution and validation.

A target must exist and be a directory for every command. Commands other than
``init`` additionally require it to look like a repository or project root, so
the tool never scatters framework directories into an arbitrary folder by
accident. ``init`` itself creates the first marker (``.omn-agent``), which
makes the same directory a valid target for every later command.
"""

from __future__ import annotations

from pathlib import Path

from .common import ExitCode, OmnError

FRAMEWORK_DIR = ".omn-agent"

# Presence of any one of these marks a directory as a repo / project root.
REPO_MARKERS = (
    ".git", ".hg", ".svn",
    FRAMEWORK_DIR,
    "pyproject.toml", "setup.py", "package.json", "go.mod", "Cargo.toml",
    "pom.xml", "build.gradle", "build.gradle.kts", "Gemfile", "composer.json",
    "Makefile", "CMakeLists.txt",
)


def resolve_target(raw: str, *, require_repo: bool = True) -> Path:
    """Return the absolute target path, or raise OmnError(INVALID_TARGET)."""
    target = Path(raw).expanduser()
    try:
        target = target.resolve()
    except OSError as exc:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"target path cannot be resolved: {raw} ({exc})")
    if not target.exists():
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"target path does not exist: {target}",
                       hint="create the directory (or check the path) and re-run")
    if not target.is_dir():
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"target path is not a directory: {target}")
    if require_repo and not is_repo_root(target):
        # A solution file anywhere at top level also counts (e.g. .NET repos).
        if not any(target.glob("*.sln")):
            raise OmnError(
                ExitCode.INVALID_TARGET,
                f"target is not a repository or project root: {target}",
                hint="run 'git init' in the target (or use 'omn-agent init <target>' "
                     "first, which marks the directory for the framework)")
    return target


def is_repo_root(target: Path) -> bool:
    return any((target / marker).exists() for marker in REPO_MARKERS)


def framework_root(target: Path) -> Path:
    return target / FRAMEWORK_DIR
