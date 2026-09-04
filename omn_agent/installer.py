"""Bootstrap logic: init, install, and upgrade.

Every file the installer might touch is classified before anything is
written, against both the incoming payload and the install manifest:

    CREATE          target file missing                        -> write
    UNCHANGED       target content == payload content          -> no-op (adopt)
    UPDATE          content == recorded install hash           -> safe overwrite
    SKIP_MODIFIED   content != recorded install hash           -> warn, keep
    SKIP_UNKNOWN    file exists at a managed path, no record   -> warn, keep
    SEED            seed file missing                          -> write once
    SEED_KEPT       seed file present (project-owned)          -> no-op

``--force`` promotes SKIP_MODIFIED / SKIP_UNKNOWN to a backed-up overwrite of
files at *framework payload paths only*; files at paths the payload does not
claim are never touched by any mode. Dry-run plans and prints, writes nothing,
and exits 5. Install never reports success without running full validation.
"""

from __future__ import annotations

import dataclasses
import enum
import sys
from pathlib import Path

from . import branch_config, context_gen
from .common import ExitCode, OmnError, Report, Severity
from .manifest import (atomic_write, load_manifest, new_manifest, save_manifest,
                       sha256_bytes, sha256_file)
from .repo import framework_root, resolve_target
from .source import (MANAGED_DIRS, OPERATIONAL_DIRS, SEED_DIRS,
                     build_bootstrap_descriptor, enumerate_payload, enumerate_seeds,
                     find_source, render_bootstrap_files)
from .validator import run_validation

BACKUP_SUFFIX = ".omn-bak"


class Op(enum.Enum):
    CREATE = "create"
    UNCHANGED = "unchanged"
    UPDATE = "update"
    SKIP_MODIFIED = "skip (modified by user)"
    SKIP_UNKNOWN = "skip (not framework-managed)"
    FORCE = "overwrite (forced, backup kept)"
    SEED = "seed"
    SEED_KEPT = "seed kept (project-owned)"


@dataclasses.dataclass
class Action:
    rel: str
    op: Op
    content: bytes | None = None    # exactly one of content / src is set for writes
    src: Path | None = None
    new_hash: str = ""


def check_compatible(fw_dir: Path) -> dict | None:
    """Return the manifest (or None), or raise INCOMPATIBLE on foreign state."""
    if fw_dir.exists() and not fw_dir.is_dir():
        raise OmnError(ExitCode.INCOMPATIBLE,
                       f"{fw_dir} exists but is not a directory",
                       hint="move the file aside, then re-run")
    manifest = load_manifest(fw_dir)   # raises INCOMPATIBLE if unreadable
    if manifest is None and fw_dir.is_dir() and any(fw_dir.iterdir()):
        raise OmnError(
            ExitCode.INCOMPATIBLE,
            f"{fw_dir} exists with content but has no install manifest",
            hint="this directory was not written by omn-agent (or the manifest was "
                 "deleted); refusing to modify it. Move it aside, or restore "
                 "bootstrap/install-manifest.json from version control")
    return manifest


def _payload_bytes(action_src: Path | None, content: bytes | None) -> bytes:
    return content if content is not None else action_src.read_bytes()  # type: ignore[union-attr]


def plan_file(rel: str, dest: Path, payload_hash: str, recorded: str | None,
              force: bool) -> Op:
    if not dest.exists():
        return Op.CREATE
    current = sha256_file(dest)
    if current == payload_hash:
        return Op.UNCHANGED
    if recorded is None:
        return Op.FORCE if force else Op.SKIP_UNKNOWN
    if current == recorded:
        return Op.UPDATE
    return Op.FORCE if force else Op.SKIP_MODIFIED


def plan_install(fw_dir: Path, source: Path, manifest: dict | None,
                 force: bool) -> tuple[list[Action], dict]:
    payload = enumerate_payload(source)
    descriptor = build_bootstrap_descriptor(payload)
    generated = render_bootstrap_files(descriptor)
    recorded_files = (manifest or {}).get("files", {})
    recorded_seeds = (manifest or {}).get("seeds", {})

    actions: list[Action] = []
    for rel, data in sorted(generated.items()):
        h = sha256_bytes(data)
        op = plan_file(rel, fw_dir / rel, h, recorded_files.get(rel), force)
        actions.append(Action(rel, op, content=data, new_hash=h))
    for rel, src in payload.items():
        h = sha256_file(src)
        op = plan_file(rel, fw_dir / rel, h, recorded_files.get(rel), force)
        actions.append(Action(rel, op, src=src, new_hash=h))
    for rel, src in enumerate_seeds(source).items():
        if (fw_dir / rel).exists():
            actions.append(Action(rel, Op.SEED_KEPT))
        else:
            actions.append(Action(rel, Op.SEED, src=src, new_hash=sha256_file(src)))
    # dependency-map.md is a generated seed: derived from the target repository's
    # own manifests rather than copied from the framework source, whose copy
    # describes the framework itself. Seeded once, project-owned afterwards,
    # exactly like the context/ and memory/ seeds above; regenerate on demand
    # with 'omn-agent context generate dependency-map'.
    if (fw_dir / context_gen.DEPENDENCY_MAP_REL).exists():
        actions.append(Action(context_gen.DEPENDENCY_MAP_REL, Op.SEED_KEPT))
    else:
        data = context_gen.render_dependency_map(fw_dir.parent).encode("utf-8")
        actions.append(Action(context_gen.DEPENDENCY_MAP_REL, Op.SEED,
                              content=data, new_hash=sha256_bytes(data)))
    return actions, {"recorded_seeds": recorded_seeds}


def apply_actions(fw_dir: Path, actions: list[Action], manifest: dict,
                  report: Report) -> None:
    for d in OPERATIONAL_DIRS + MANAGED_DIRS + SEED_DIRS:
        (fw_dir / d).mkdir(parents=True, exist_ok=True)
    for a in actions:
        dest = fw_dir / a.rel
        if a.op in (Op.CREATE, Op.UPDATE, Op.SEED, Op.FORCE):
            if a.op == Op.FORCE:
                backup = dest.with_name(dest.name + BACKUP_SUFFIX)
                if backup.exists():
                    report.error("I-BACKUP", f"{a.rel}: backup already exists, "
                                 f"refusing forced overwrite",
                                 hint=f"resolve {backup} first")
                    continue
                dest.replace(backup)
                report.warning("I-FORCED", f"{a.rel}: overwritten (--force); previous "
                               f"content kept at {a.rel}{BACKUP_SUFFIX}")
            dest.parent.mkdir(parents=True, exist_ok=True)
            atomic_write(dest, _payload_bytes(a.src, a.content))
        if a.op == Op.SEED:
            manifest["seeds"][a.rel] = a.new_hash
        elif a.op != Op.SEED_KEPT and a.op not in (Op.SKIP_MODIFIED, Op.SKIP_UNKNOWN):
            manifest["files"][a.rel] = a.new_hash


def summarize_plan(actions: list[Action], report: Report, *, dry_run: bool):
    counts: dict[Op, int] = {}
    for a in actions:
        counts[a.op] = counts.get(a.op, 0) + 1
        if a.op in (Op.SKIP_MODIFIED, Op.SKIP_UNKNOWN):
            hint = ("your changes are preserved; re-run with --force to replace it "
                    "(a .omn-bak backup is kept)" if a.op == Op.SKIP_MODIFIED else
                    "this file is not recorded in the install manifest, so omn-agent "
                    "treats it as yours; move it aside or use --force to replace it")
            report.warning("I-SKIP", f"{a.rel}: {a.op.value}", hint=hint)
        elif dry_run and a.op in (Op.CREATE, Op.UPDATE, Op.SEED, Op.FORCE):
            report.info("I-PLAN", f"would {a.op.value}: {a.rel}")
    summary = ", ".join(f"{n} {op.value}" for op, n in sorted(counts.items(),
                                                              key=lambda kv: kv[0].value))
    verb = "planned" if dry_run else "applied"
    report.info("I-SUMMARY", f"{verb}: {summary or 'nothing to do'}")


# ------------------------------------------------------------------ commands


def cmd_init(args, input_fn=None) -> ExitCode:
    target = resolve_target(args.target, require_repo=False)
    report = Report("init", str(target))
    fw_dir = framework_root(target)
    manifest = check_compatible(fw_dir)

    feature_t = getattr(args, "feature_branch_template", None)
    bugfix_t = getattr(args, "bugfix_branch_template", None)
    max_len = getattr(args, "branch_max_length", None)

    if args.dry_run:
        state = "already initialized" if manifest else "would create framework layout"
        report.info("I-DRYRUN", f"{state} at {fw_dir}")
        if not branch_config.config_path(fw_dir).exists():
            report.info("I-DRYRUN", f"would seed {branch_config.CONFIG_REL} "
                        "(branch naming templates)")
        report.print()
        return ExitCode.DRY_RUN

    created = []
    for d in OPERATIONAL_DIRS + MANAGED_DIRS + SEED_DIRS:
        p = fw_dir / d
        if not p.exists():
            p.mkdir(parents=True)
            created.append(d)
    if manifest is None:
        manifest = new_manifest(source="(init only)")
    save_manifest(fw_dir, manifest, installed=False)

    if feature_t or bugfix_t or not sys.stdin.isatty():
        branch_config.seed_config(fw_dir, feature_template=feature_t,
                                  bugfix_template=bugfix_t, max_length=max_len,
                                  report=report)
    else:
        branch_config.seed_config_interactive(
            fw_dir, max_length=max_len, report=report, input_fn=input_fn or input)

    if created:
        report.success("I-INIT", f"created framework layout ({len(created)} directories) "
                       f"at {fw_dir}")
    else:
        report.success("I-INIT", f"layout already present at {fw_dir}; nothing to do")
    if not manifest.get("installedAt"):
        report.info("I-NEXT", "layout only -- run 'omn-agent install' to install the "
                    "framework payload")
    return report.finish()


def cmd_install(args) -> ExitCode:
    return _install_like(args, upgrade=False)


def cmd_upgrade(args) -> ExitCode:
    return _install_like(args, upgrade=True)


def _install_like(args, *, upgrade: bool) -> ExitCode:
    command = "upgrade" if upgrade else "install"
    target = resolve_target(args.target, require_repo=not upgrade)
    report = Report(command, str(target))
    fw_dir = framework_root(target)
    source = find_source(getattr(args, "source", None))
    if source.resolve() == fw_dir.resolve():
        raise OmnError(ExitCode.INVALID_TARGET,
                       "source and target are the same installation",
                       hint="pass --source pointing at the framework checkout you "
                            "want to install from")

    manifest = check_compatible(fw_dir)
    if upgrade:
        if manifest is None or not manifest.get("installedAt"):
            raise OmnError(ExitCode.INCOMPLETE,
                           f"nothing to upgrade: no completed installation at {fw_dir}",
                           hint="run 'omn-agent install' first")
    if manifest is None:
        manifest = new_manifest(source=str(source))

    force = bool(getattr(args, "force", False))
    actions, _ = plan_install(fw_dir, source, manifest, force)

    if args.dry_run:
        summarize_plan(actions, report, dry_run=True)
        report.print()
        return ExitCode.DRY_RUN

    apply_actions(fw_dir, actions, manifest, report)
    # Orphans: recorded files the new payload no longer ships. Never deleted.
    payload_paths = {a.rel for a in actions if a.op != Op.SEED_KEPT}
    for rel in sorted(set(manifest["files"]) - payload_paths):
        if (fw_dir / rel).exists():
            report.info("I-ORPHAN", f"{rel}: no longer part of the framework payload; "
                        "left in place")
        else:
            del manifest["files"][rel]
    manifest["source"] = str(source)
    save_manifest(fw_dir, manifest, installed=True)
    summarize_plan(actions, report, dry_run=False)

    # Never claim success without validation.
    validation = run_validation(target)
    for f in validation.findings:
        if f.severity >= Severity.WARNING:
            report.findings.append(f)
    if validation.worst >= Severity.ERROR:
        report.error("I-VALIDATE", f"{command} finished but validation failed; "
                     "see findings above",
                     hint="run 'omn-agent doctor' for a full diagnosis")
        return report.finish(error_code=ExitCode.VALIDATION_FAILED)
    skipped = [a for a in actions if a.op in (Op.SKIP_MODIFIED, Op.SKIP_UNKNOWN)]
    report.success("I-DONE", f"{command} complete and validated"
                   + (f" ({len(skipped)} file(s) preserved, see warnings)"
                      if skipped else ""))
    return report.finish()
