"""Framework source discovery and payload enumeration.

The installer does not hard-code the framework's content. It copies a
*payload* out of a framework source checkout -- a directory shaped like the
authoritative framework tree (the ``.claude`` directory of the framework
repository, or an installed ``.omn-agent`` directory; the sub-directory names
are identical). The payload is enumerated fresh on every run, and the
generated bootstrap descriptor is derived from what the payload actually
contains, so every reference it records is resolvable at install time.

Directory classes
-----------------
managed      framework-owned; installed and upgraded under manifest control
seeded       created from the source once, then owned by the project
             (context and memory are the project's knowledge, not ours)
operational  created empty; their contents are never touched by this tool
"""

from __future__ import annotations

import fnmatch
import json
from pathlib import Path

from . import SCHEMA_VERSION, __version__
from .common import ExitCode, OmnError

# Directories synced from the source, file by file, under manifest control.
MANAGED_DIRS = (
    "runtime", "registry", "config", "templates", "agents", "workflows",
    "skills", "commands", "domain-model", "validation",
)

# Created from the source only when missing; never updated or overwritten.
SEED_DIRS = ("context", "memory")

# Created as empty directories; contents belong to the project / runtime.
OPERATIONAL_DIRS = (
    "bootstrap", "reports", "runs", "runs/inputs",
    "tickets", "tickets/inbox", "tasks",
)

# Directories a source must provide to be usable at all. The runtime cannot
# resolve a single phase without these.
REQUIRED_SOURCE_FILES = (
    "runtime/framework_runtime.py",
    "runtime/state_engine.py",
    "registry/agents.yaml",
    "registry/workflows.yaml",
)

EXCLUDE_PATTERNS = ("__pycache__", "*.pyc", "*.pyo", ".DS_Store", "*.omn-bak", "*.tmp-omn")

# Payload copy bundled inside this package (declared as package data in
# pyproject.toml), the last-resort source candidate: it is what lets a
# non-editable wheel install into site-packages resolve a source with no
# --source flag. The bundle is a committed mirror of the repository's
# framework payload tree, kept in sync by tests/test_bundled_payload.py
# (run it with --sync to refresh the mirror).
BUNDLED_PAYLOAD_DIR = "_bundled_payload"

BOOTSTRAP_JSON = "bootstrap/bootstrap.json"
BOOTSTRAP_README = "bootstrap/README.md"
MANIFEST_PATH = "bootstrap/install-manifest.json"


def find_source(explicit: str | None) -> Path:
    """Locate the framework source tree.

    Order: an explicit ``--source`` path, then a ``.claude`` or ``.omn-agent``
    framework tree next to this package's checkout, then -- last -- the payload
    copy bundled inside the installed package, which is what makes a
    non-editable (site-packages) install self-contained. An explicit path that
    does not qualify stays an error and never falls back to the bundle.
    Anything else is an error with an actionable message -- guessing a payload
    source would be unsafe.
    """
    candidates: list[Path] = []
    if explicit:
        p = Path(explicit).expanduser().resolve()
        # Accept either the framework tree itself or a repo that contains one.
        candidates = [p, p / ".claude", p / ".omn-agent"]
    else:
        here = Path(__file__).resolve().parent.parent
        candidates = [here / ".claude", here / ".omn-agent",
                      Path(__file__).resolve().parent / BUNDLED_PAYLOAD_DIR]

    for cand in candidates:
        if cand.is_dir() and _is_framework_tree(cand):
            return cand

    where = explicit or "next to the omn-agent package"
    raise OmnError(
        ExitCode.INVALID_TARGET,
        f"no framework source found ({where})",
        hint="pass --source <path> pointing at a framework checkout (a directory "
             "containing runtime/framework_runtime.py and registry/agents.yaml, "
             "or a repo whose .claude/.omn-agent directory contains them)")


def _is_framework_tree(root: Path) -> bool:
    return all((root / rel).is_file() for rel in REQUIRED_SOURCE_FILES)


def _excluded(name: str) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in EXCLUDE_PATTERNS)


def _walk(root: Path, base: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    if not root.is_dir():
        return out
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if _excluded(path.name):
            continue
        if any(_excluded(part) for part in path.relative_to(base).parts[:-1]):
            continue
        out[path.relative_to(base).as_posix()] = path
    return out


def enumerate_payload(source: Path) -> dict[str, Path]:
    """All managed files: target-relative posix path -> absolute source path."""
    payload: dict[str, Path] = {}
    for d in MANAGED_DIRS:
        payload.update(_walk(source / d, source))
    if not payload:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"framework source contains no managed files: {source}")
    return payload


def enumerate_seeds(source: Path) -> dict[str, Path]:
    seeds: dict[str, Path] = {}
    for d in SEED_DIRS:
        seeds.update(_walk(source / d, source))
    return seeds


def build_bootstrap_descriptor(payload: dict[str, Path]) -> dict:
    """Derive bootstrap.json from the actual payload, so every reference resolves."""
    validators = {}
    for rel in payload:
        p = Path(rel)
        if p.parts[0] == "runtime" and p.name.endswith("_validator.py"):
            artifact = p.name[: -len("_validator.py")].replace("_", "-")
            validators[artifact] = rel
    entrypoints = {"runtime": "runtime/framework_runtime.py",
                   "stateEngine": "runtime/state_engine.py"}
    registries = sorted(r for r in payload if r.startswith("registry/"))
    # Every context file the runtime's own context-slice tables can demand at
    # dispatch time. `dependency-map.md` is generated per target rather than
    # copied from the source (see omn_agent.context_gen), but it is required
    # all the same: a run that reaches root-cause-analysis without it fails
    # with a context-integrity-failure, which is far too late to learn about
    # a setup gap that `validate`/`doctor` can name on day one.
    required_context = [f"context/{n}.md"
                        for n in ("product-context", "technical-context", "release-context")]
    required_context.append("dependency-map.md")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "framework": "omn-agent",
        "frameworkVersion": __version__,
        "layout": {
            "managed": list(MANAGED_DIRS),
            "seeded": list(SEED_DIRS),
            "operational": list(OPERATIONAL_DIRS),
        },
        "entrypoints": entrypoints,
        "registries": registries,
        "validators": dict(sorted(validators.items())),
        "requiredContext": required_context,
    }


def render_bootstrap_files(descriptor: dict) -> dict[str, bytes]:
    """Content of the generated (managed) bootstrap files."""
    readme = (
        "# Omn-Agent bootstrap\n\n"
        "This directory is written by the `omn-agent` installer.\n\n"
        "- `bootstrap.json` -- machine-readable descriptor of the installed layout,\n"
        "  runtime entrypoints, registries, and validator references. Validation\n"
        "  (`omn-agent validate` / `doctor`) resolves every reference in it.\n"
        "- `install-manifest.json` -- content hashes of every framework-managed file\n"
        "  as installed. The installer uses it to tell framework-managed files from\n"
        "  files you have modified or created; only unmodified framework-managed\n"
        "  files are ever updated in place.\n\n"
        "Do not edit these files by hand. Everything outside the managed framework\n"
        "directories -- and any file you change inside them -- is treated as yours\n"
        "and is never overwritten (see `omn-agent upgrade --help`).\n"
    )
    return {
        BOOTSTRAP_JSON: (json.dumps(descriptor, indent=2) + "\n").encode("utf-8"),
        BOOTSTRAP_README: readme.encode("utf-8"),
    }
