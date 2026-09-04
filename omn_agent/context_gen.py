"""Dependency-map generation (`omn-agent context generate dependency-map`).

``dependency-map.md`` is a context-slice member several runtime phases require
(root-cause-analysis, fix-implementation, solution-design, and others -- see
``CONTEXT_SLICE_PHASE`` in ``runtime/framework_runtime.py``). It describes the
*target project's* module and dependency structure, so it cannot be copied
from the framework source the way ``context/*.md`` seeds are: the framework's
own copy describes the framework. It is instead derived from the manifests the
target repository actually contains -- ``.csproj`` project references,
``package.json`` workspaces and local dependencies, ``pyproject.toml``
dependencies -- and falls back to an honest, clearly-labelled placeholder when
no manifest is detectable, rather than fabricating a graph.

The installer seeds this file once (project-owned afterwards, like every other
seed); this module's CLI command regenerates it on demand.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .common import ExitCode, OmnError, Report
from .repo import framework_root, resolve_target

DEPENDENCY_MAP_REL = "dependency-map.md"

_SCAN_EXCLUDE_DIRS = {".git", ".hg", ".svn", "node_modules", "bin", "obj",
                      "dist", "build", ".venv", "venv", "__pycache__",
                      ".omn-agent", ".claude"}

_PROJECT_REF_RE = re.compile(
    r"<ProjectReference\s+[^>]*Include\s*=\s*\"([^\"]+)\"", re.I)


def _scan_files(target: Path, pattern: str) -> list[Path]:
    out = []
    for p in sorted(target.rglob(pattern)):
        if any(part in _SCAN_EXCLUDE_DIRS for part in p.relative_to(target).parts[:-1]):
            continue
        out.append(p)
    return out


def _rel(target: Path, p: Path) -> str:
    return p.relative_to(target).as_posix()


def collect_dotnet_edges(target: Path) -> list[tuple[str, str]]:
    """(project, referenced project) edges from `<ProjectReference>` entries."""
    edges = []
    for csproj in _scan_files(target, "*.csproj"):
        try:
            text = csproj.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        src = csproj.stem
        for ref in _PROJECT_REF_RE.findall(text):
            edges.append((src, Path(ref.replace("\\", "/")).stem))
    return edges


def collect_node_edges(target: Path) -> list[tuple[str, str]]:
    """(package, local dependency) edges from package.json workspaces.

    Only dependencies that name another package found in the same repository
    count as edges -- registry dependencies are environment, not structure.
    """
    packages = {}
    for pkg in _scan_files(target, "package.json"):
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        name = data.get("name")
        if isinstance(name, str) and name:
            packages[name] = data
    edges = []
    for name, data in sorted(packages.items()):
        deps = {}
        for key in ("dependencies", "devDependencies", "peerDependencies"):
            block = data.get(key)
            if isinstance(block, dict):
                deps.update(block)
        for dep in sorted(deps):
            if dep != name and dep in packages:
                edges.append((name, dep))
    return edges


def collect_python_edges(target: Path) -> list[tuple[str, str]]:
    """(project, dependency) edges from pyproject.toml, local names only.

    Parsed leniently (no tomllib requirement below 3.11 is assumed even though
    this package requires 3.10+; a regex over the dependencies array is enough
    for edge detection). As with node, only a dependency whose name matches
    another pyproject in the same repository is an edge.
    """
    projects = {}
    for py in _scan_files(target, "pyproject.toml"):
        try:
            text = py.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = re.search(r"^\s*name\s*=\s*[\"']([^\"']+)[\"']", text, re.M)
        if m:
            projects[m.group(1)] = text
    edges = []
    for name, text in sorted(projects.items()):
        m = re.search(r"^\s*dependencies\s*=\s*\[(.*?)\]", text, re.M | re.S)
        if not m:
            continue
        for dep in re.findall(r"[\"']([A-Za-z0-9_.-]+)", m.group(1)):
            dep_name = re.split(r"[<>=!~\[;@ ]", dep)[0]
            if dep_name and dep_name != name and dep_name in projects:
                edges.append((name, dep_name))
    return edges


def render_dependency_map(target: Path) -> str:
    """The dependency-map.md content derived from the target's manifests."""
    sections = []
    detected = []
    for title, notation, edges in (
            (".NET project references", "`<ProjectReference>` in `*.csproj`",
             collect_dotnet_edges(target)),
            ("Node package dependencies", "local packages named in "
             "`package.json` dependencies", collect_node_edges(target)),
            ("Python project dependencies", "local projects named in "
             "`pyproject.toml` dependencies", collect_python_edges(target))):
        if not edges:
            continue
        detected.append(title)
        lines = [f"## {title}", "", f"Derived from {notation}. "
                 "`A -> B` means A depends on B.", "",
                 "| Module | Depends on |", "|---|---|"]
        for src, dst in sorted(set(edges)):
            lines.append(f"| `{src}` | `{dst}` |")
        sections.append("\n".join(lines))

    header = [
        "# Dependency Map",
        "",
        "Module and project dependency relationships for this repository. Read by the",
        "framework runtime as blast-radius context for root-cause analysis, fix",
        "implementation, and structural design phases.",
        "",
        "Regenerate with `omn-agent context generate dependency-map` after the",
        "project's module structure changes; hand-written additions below the",
        "generated sections are yours and survive regeneration only if you keep them",
        "in a separate section.",
        "",
    ]
    if sections:
        return "\n".join(header) + "\n\n".join(sections) + "\n"
    return "\n".join(header + [
        "## No manifests detected",
        "",
        "No `*.csproj`, `package.json`, or `pyproject.toml` manifests with local",
        "dependency references were found in this repository, so no dependency graph",
        "could be derived. **This file is a placeholder, not a statement that the",
        "project has no internal dependencies.** Document the module boundaries and",
        "dependency directions by hand here -- the runtime treats this file as the",
        "boundary record when it assesses a change's blast radius, and an empty",
        "record makes that assessment a guess.",
        "",
    ])


# ------------------------------------------------------------------ commands


def cmd_context_generate(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("context generate", str(target))
    fw_dir = framework_root(target)
    if not fw_dir.is_dir():
        raise OmnError(ExitCode.INCOMPLETE,
                       f"framework directory missing: {fw_dir}",
                       hint="run 'omn-agent install <target>' first")

    dest = fw_dir / DEPENDENCY_MAP_REL
    content = render_dependency_map(target)

    if args.dry_run:
        report.info("C-PLAN", f"would write {DEPENDENCY_MAP_REL} "
                    f"({len(content.splitlines())} lines)")
        report.print()
        return ExitCode.DRY_RUN
    if dest.exists() and not args.force:
        raise OmnError(ExitCode.INCOMPATIBLE,
                       f"{DEPENDENCY_MAP_REL} already exists (project-owned)",
                       hint="re-run with --force to regenerate it in place")

    dest.write_text(content, encoding="utf-8")
    report.success("C-GEN", f"wrote {DEPENDENCY_MAP_REL} "
                   f"({len(content.splitlines())} lines)")
    return report.finish()
