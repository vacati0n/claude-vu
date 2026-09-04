"""Validation, diagnosis (doctor), and status reporting.

Validation resolves everything the generated bootstrap descriptor claims:
required directories, readable manifest and registries, runtime entrypoints
that exist, compile, *and resolve their module-top-level imports*, validator
references that resolve, required context seeds, and broken symlinks anywhere
under the framework directory.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

from .common import ExitCode, OmnError, Report, Severity
from .manifest import load_manifest, sha256_file
from .repo import framework_root, resolve_target
from .source import BOOTSTRAP_JSON, MANAGED_DIRS, MANIFEST_PATH, SEED_DIRS

REQUIRED_DIRS = tuple(MANAGED_DIRS) + tuple(SEED_DIRS) + (
    "bootstrap", "reports", "runs", "tickets", "tasks",
)


def run_validation(target: Path) -> Report:
    report = Report("validate", str(target))
    fw_dir = framework_root(target)

    if not fw_dir.is_dir():
        report.error("V-NOTINSTALLED", f"framework directory missing: {fw_dir}",
                     hint="run 'omn-agent install <target>'")
        return report

    manifest = _load_or_report(lambda: load_manifest(fw_dir), report, "V-MANIFEST",
                               f"install manifest ({MANIFEST_PATH})")
    if manifest is None and not report.findings:
        report.error("V-MANIFEST", f"install manifest missing: {MANIFEST_PATH}",
                     hint="run 'omn-agent install' to (re)establish the manifest")
    if manifest is not None and not manifest.get("installedAt"):
        report.error("V-NOTINSTALLED", "layout is initialized but the framework "
                     "payload was never installed",
                     hint="run 'omn-agent install <target>'")

    for d in REQUIRED_DIRS:
        if not (fw_dir / d).is_dir():
            report.error("V-DIR", f"required directory missing: {d}",
                         hint="run 'omn-agent install' to repair the layout")

    descriptor = _read_bootstrap(fw_dir, report)

    if descriptor:
        for rel in descriptor.get("registries", []):
            _check_registry(fw_dir, rel, report)
        for name, rel in descriptor.get("entrypoints", {}).items():
            _check_python(fw_dir, rel, report, code="V-ENTRYPOINT",
                          what=f"runtime entrypoint '{name}'")
        for artifact, rel in descriptor.get("validators", {}).items():
            path = fw_dir / rel
            if not path.is_file():
                report.error("V-VALIDATOR", f"validator for '{artifact}' does not "
                             f"resolve: {rel}",
                             hint="run 'omn-agent install' to repair")
            else:
                _check_python(fw_dir, rel, report, code="V-VALIDATOR",
                              what=f"validator '{artifact}'")
        for rel in descriptor.get("requiredContext", []):
            if not (fw_dir / rel).is_file():
                report.error("V-CONTEXT", f"required context file missing: {rel}",
                             hint="run 'omn-agent install' to seed it")

    # Every file the runtime's own context-slice tables can demand at dispatch
    # time must exist now, not when a run is already several phases deep. This
    # reads the tables out of the installed runtime itself, so a runtime whose
    # slices change changes this check with it -- validate/doctor can never
    # report a clean installation the runtime would fail on.
    slice_members = _context_slice_members(fw_dir)
    already = set(descriptor.get("requiredContext", [])) if descriptor else set()
    for rel in sorted(slice_members - already):
        if not (fw_dir / rel).is_file():
            report.error(
                "V-SLICE",
                f"context-slice member missing: {rel} (the runtime requires it "
                f"at dispatch time)",
                hint="run 'omn-agent install' to restore a framework-managed "
                     "file, or 'omn-agent context generate dependency-map' for "
                     "the dependency map")

    if manifest:
        missing = [rel for rel in manifest.get("files", {})
                   if not (fw_dir / rel).exists()]
        for rel in missing[:20]:
            report.error("V-FILE", f"framework-managed file missing: {rel}")
        if len(missing) > 20:
            report.error("V-FILE", f"...and {len(missing) - 20} more managed files "
                         "missing")
        if missing:
            report.error("V-INCOMPLETE", f"{len(missing)} managed file(s) missing -- "
                         "installation is incomplete",
                         hint="run 'omn-agent install' to repair it in place")

    for broken in _broken_symlinks(fw_dir):
        report.error("V-SYMLINK", f"broken symlink: {broken.relative_to(fw_dir)}")

    mcp_cfg = fw_dir / "config" / "mcp.json"
    if mcp_cfg.exists():
        try:
            json.loads(mcp_cfg.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            report.error("V-MCP", f"config/mcp.json is unreadable: {exc}",
                         hint="re-run 'omn-agent mcp add jira' or fix the JSON")

    if report.worst < Severity.ERROR:
        report.success("V-OK", "installation is valid: layout, manifest, registries, "
                       "entrypoints, validators, and context all resolve")
    return report


def _context_slice_members(fw_dir: Path) -> set[str]:
    """Every file path the installed runtime's context-slice tables reference.

    Read statically (AST, literals only) from ``runtime/framework_runtime.py``
    rather than imported: importing the runtime would require its own
    dependencies (PyYAML and siblings) in whatever environment validation runs
    in, and a validator that cannot even load is worse than one that reads.
    Both table shapes are handled: ``CONTEXT_SLICE_BASE`` is a list of paths,
    and ``CONTEXT_SLICE_PHASE`` values hold either bare paths or
    ``(path, supplies)`` pairs. A runtime without these tables (or one whose
    tables are not literal) contributes nothing, so older or reduced runtimes
    validate exactly as before.
    """
    path = fw_dir / "runtime" / "framework_runtime.py"
    if not path.is_file():
        return set()
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return set()   # V-ENTRYPOINT already reports an uncompilable runtime
    members: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for t in node.targets:
            if not (isinstance(t, ast.Name)
                    and t.id in ("CONTEXT_SLICE_BASE", "CONTEXT_SLICE_PHASE")):
                continue
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, TypeError, SyntaxError, MemoryError):
                continue
            entries = value if t.id == "CONTEXT_SLICE_BASE" \
                else [e for phase in value.values() for e in phase]
            for e in entries:
                rel = e if isinstance(e, str) else e[0]
                if isinstance(rel, str):
                    members.add(rel)
    return members


def _load_or_report(fn, report: Report, code: str, what: str):
    try:
        return fn()
    except OmnError as exc:
        report.error(code, f"{what}: {exc.message}", hint=exc.hint)
        return None


def _read_bootstrap(fw_dir: Path, report: Report) -> dict | None:
    path = fw_dir / BOOTSTRAP_JSON
    if not path.is_file():
        report.error("V-BOOTSTRAP", f"bootstrap descriptor missing: {BOOTSTRAP_JSON}",
                     hint="run 'omn-agent install' to regenerate it")
        return None
    try:
        descriptor = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        report.error("V-BOOTSTRAP", f"bootstrap descriptor unreadable: {exc}",
                     hint="run 'omn-agent install' to regenerate it")
        return None
    for key in ("entrypoints", "registries", "validators"):
        if key not in descriptor:
            report.error("V-BOOTSTRAP", f"bootstrap descriptor lacks '{key}'",
                         hint="run 'omn-agent install' to regenerate it")
    return descriptor


def _check_registry(fw_dir: Path, rel: str, report: Report):
    path = fw_dir / rel
    if not path.is_file():
        report.error("V-REGISTRY", f"registry file missing: {rel}",
                     hint="run 'omn-agent install' to repair")
        return
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        report.error("V-REGISTRY", f"registry file unreadable: {rel} ({exc})")
        return
    meaningful = [ln for ln in text.splitlines()
                  if ln.strip() and not ln.lstrip().startswith("#")]
    if not meaningful or ":" not in meaningful[0]:
        report.error("V-REGISTRY", f"registry file does not look like a YAML "
                     f"mapping: {rel}")


# Distributions known to provide a third-party import root, for actionable
# hints on a V-IMPORT finding.
KNOWN_DISTRIBUTIONS = {"yaml": "pyyaml"}


def _import_hint(root: str) -> str:
    dist = KNOWN_DISTRIBUTIONS.get(root)
    if dist:
        return (f"install '{dist}' into this Python environment "
                f"(e.g. 'pip install {dist}')")
    return (f"install the distribution that provides '{root}' into the "
            f"Python environment that runs omn-agent")


def _toplevel_import_roots(tree: ast.Module) -> list[str]:
    """Module-top-level import roots, in first-appearance order.

    Only statements directly in the module body count: function-local,
    conditional, and dynamic imports are deliberately out of scope, and
    relative imports (level > 0) resolve inside the payload by construction.
    """
    roots: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            root = name.split(".")[0]
            if root and root not in roots:
                roots.append(root)
    return roots


def _import_resolves(root: str, sibling_dir: Path) -> bool:
    """Whether a module-top-level import root would resolve at execution time.

    Two sources, mirroring how the installed runtime actually resolves its
    imports: sibling payload modules in the checked file's own directory
    (the payload files put that directory on sys.path when they execute),
    and the executing environment's import machinery -- the runner invokes
    the runtime with this same interpreter, so find_spec answers for the
    right environment. Never executes the checked code. A lookup failure
    counts as unresolved; the caller reports it as a finding, never raises.
    """
    if (sibling_dir / f"{root}.py").is_file() \
            or (sibling_dir / root / "__init__.py").is_file():
        return True
    try:
        return importlib.util.find_spec(root) is not None
    except Exception:   # find_spec may raise on odd meta-path finders
        return False


def _check_python(fw_dir: Path, rel: str, report: Report, *, code: str, what: str):
    path = fw_dir / rel
    if not path.is_file():
        report.error(code, f"{what} missing: {rel}",
                     hint="run 'omn-agent install' to repair")
        return
    try:
        text = path.read_text(encoding="utf-8")
        compile(text, str(path), "exec")
    except (OSError, UnicodeDecodeError, SyntaxError) as exc:
        report.error(code, f"{what} does not compile: {rel} ({exc})",
                     hint="run 'omn-agent install' to restore the framework copy")
        return   # an uncompilable file has no reliably derivable import set
    for root in _toplevel_import_roots(ast.parse(text)):
        if not _import_resolves(root, path.parent):
            report.error(
                "V-IMPORT",
                f"{what} imports '{root}', which does not resolve in this "
                f"Python environment ({sys.executable}): {rel}",
                hint=_import_hint(root))


def _broken_symlinks(fw_dir: Path):
    for path in fw_dir.rglob("*"):
        if path.is_symlink() and not path.exists():
            yield path


# ------------------------------------------------------------------ commands


def cmd_validate(args) -> ExitCode:
    target = resolve_target(args.target)
    report = run_validation(target)
    if any(f.code in ("V-NOTINSTALLED", "V-INCOMPLETE") for f in report.findings):
        return report.finish(error_code=ExitCode.INCOMPLETE)
    return report.finish(error_code=ExitCode.VALIDATION_FAILED)


def cmd_doctor(args) -> ExitCode:
    target = resolve_target(args.target)
    report = run_validation(target)
    report.command = "doctor"
    fw_dir = framework_root(target)

    manifest = None
    try:
        manifest = load_manifest(fw_dir)
    except OmnError:
        pass  # already reported by run_validation

    if manifest:
        drift, backups, unknown = [], [], []
        managed = manifest.get("files", {})
        for rel, recorded in managed.items():
            p = fw_dir / rel
            if p.exists() and sha256_file(p) != recorded:
                drift.append(rel)
        for d in MANAGED_DIRS:
            root = fw_dir / d
            if not root.is_dir():
                continue
            for p in root.rglob("*"):
                if not p.is_file():
                    continue
                rel = p.relative_to(fw_dir).as_posix()
                if p.name.endswith(".omn-bak"):
                    backups.append(rel)
                elif rel not in managed and "__pycache__" not in rel \
                        and not p.name.endswith((".pyc", ".pyo")):
                    unknown.append(rel)
        for rel in drift:
            report.warning("D-DRIFT", f"framework-managed file modified locally: {rel}",
                           hint="upgrades will skip it; 'omn-agent upgrade --force' "
                                "replaces it with a .omn-bak backup")
        for rel in unknown:
            report.info("D-UNKNOWN", f"file inside a framework directory is not "
                        f"framework-managed (yours, never touched): {rel}")
        for rel in backups:
            report.info("D-BACKUP", f"backup from a forced overwrite: {rel}")
        if not drift and not backups:
            report.success("D-CLEAN", f"{len(managed)} managed files match the "
                           "install manifest (no local drift)")
    return report.finish(error_code=ExitCode.VALIDATION_FAILED)


def cmd_status(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("status", str(target))
    fw_dir = framework_root(target)

    if not fw_dir.is_dir():
        report.warning("S-NONE", "framework is not installed",
                       hint="run 'omn-agent install <target>'")
        report.print()
        return ExitCode.INCOMPLETE

    manifest = load_manifest(fw_dir)   # INCOMPATIBLE propagates with exit 4
    if manifest is None:
        report.warning("S-NONE", "framework directory exists but has no manifest")
        report.print()
        return ExitCode.INCOMPLETE

    installed = manifest.get("installedAt")
    report.info("S-STATE", "installed" if installed else "initialized, not installed")
    report.info("S-VERSION", f"tool {manifest.get('toolVersion', '?')}, manifest "
                f"schema {manifest.get('schemaVersion', '?')}")
    if installed:
        report.info("S-WHEN", f"installed at {installed} from "
                    f"{manifest.get('source', '?')}")
    report.info("S-FILES", f"{len(manifest.get('files', {}))} managed files, "
                f"{len(manifest.get('seeds', {}))} project-owned seeds")

    inbox = fw_dir / "tickets" / "inbox"
    tasks = fw_dir / "tasks"
    tickets_n = len(list(inbox.glob("*.json"))) if inbox.is_dir() else 0
    tasks_n = len([p for p in tasks.iterdir() if p.is_dir()]) if tasks.is_dir() else 0
    runs = fw_dir / "runs"
    runs_n = len(list(runs.glob("run-*"))) if runs.is_dir() else 0
    report.info("S-WORK", f"{tickets_n} synced ticket(s), {tasks_n} planned task(s), "
                f"{runs_n} runtime run(s)")

    mcp_cfg = fw_dir / "config" / "mcp.json"
    report.info("S-MCP", "Jira/MCP configured" if mcp_cfg.exists()
                else "Jira/MCP not configured (omn-agent mcp add jira)")

    validation = run_validation(target)
    if validation.worst >= Severity.ERROR:
        report.error("S-HEALTH", "validation reports errors",
                     hint="run 'omn-agent doctor' for details")
        return report.finish(error_code=ExitCode.VALIDATION_FAILED)
    report.success("S-HEALTH", "validation passes")
    return report.finish(ok_code=ExitCode.OK if installed else ExitCode.INCOMPLETE)
