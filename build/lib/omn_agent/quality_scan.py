"""One-command repository quality scan (`omn-agent quality-scan`).

Drives the framework's `/quality-scan` command (workflow ``code-quality-scan``)
end to end from the CLI, stopping only where a human or the host platform is
required:

1. render (or copy) the ``quality-scan-scope`` input document and record the
   scan as a task under ``tasks/QS-<NAME>/`` -- the same task shape every
   other command produces, so ``omn-agent run QS-<NAME> --show/--watch/
   --report/--gate`` work on a scan unchanged;
2. materialize the runtime run. A changed scope is a new run: the runtime
   pins input digests at run creation, so when the rendered scope differs
   from the one a recorded run was created from, that run id is archived to
   the task's ``runHistory`` and a fresh run materialized -- exactly the
   rule ``omn-agent update`` follows;
3. drive the run: dispatch the single ``repository-quality-scan`` phase to
   the reviewer agent, stop while the host runs the dispatched subagent,
   and on re-run ingest the completion;
4. stop at the **Quality Handoff Gate**. The validated review package is the
   deliverable; the accept/reject decision belongs to a human tech lead:
   ``omn-agent run QS-<NAME> --gate "Quality Handoff Gate" --decision
   approve --owner-role omn-tech-lead --rationale ...``.

The scan reviews and stops: it changes no source, fixes nothing, and decides
nothing. Every side-effecting step goes through the same approval discipline
as ``omn-agent run`` (``--approve``, or an interactive yes) and is recorded
to the task's approvals ledger. Re-running is always safe: an unchanged
scope re-enters the same run, and a finished scan is reported read-only.
"""

from __future__ import annotations

import datetime
import getpass
import re

from . import SCHEMA_VERSION
from .common import ExitCode, OmnError, Report
from .fix_comments import _awaiting_gate, _dispatchable_step, _status_json, _steps
from .manifest import atomic_write, sha256_bytes, sha256_file
from .repo import framework_root, resolve_target
from .runner import RUN_ID_RE, _invoke, _require_approval
from .taskplan import load_task, save_task, task_dir

COMMAND = "quality-scan"
WORKFLOW = "code-quality-scan"
INPUT_TYPE = "quality-scan-scope"
PHASE = "repository-quality-scan"
GATE = "Quality Handoff Gate"
GATE_DECIDER = "omn-tech-lead"

RISK_THRESHOLDS = ("critical", "high", "medium", "low")

# Same backstop as `omn-agent update`: every loop iteration must mutate the
# run, and a dispatch ends the invocation anyway.
MAX_DRIVE_STEPS = 10

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc) \
        .isoformat(timespec="seconds")


def scan_key(name: str) -> str:
    slug = _SLUG_RE.sub("-", name.strip().lower()).strip("-")
    if not slug:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"scan name {name!r} reduces to an empty slug",
                       hint="use letters, digits, or dashes, e.g. "
                            "'backend' or 'api-v2'")
    return f"QS-{slug.upper()}"


def _flag_list(values: list[str] | None) -> list[str]:
    """Flatten repeatable, comma-separable flag values."""
    out: list[str] = []
    for v in values or []:
        out += [p.strip() for p in v.split(",") if p.strip()]
    return out


def render_scope(name: str, fw_name: str, args) -> str:
    """Render the quality-scan-scope input document from the command line."""
    paths = _flag_list(getattr(args, "paths", None))
    excludes = _flag_list(getattr(args, "exclude", None))
    threshold = getattr(args, "risk_threshold", None) or "medium"
    context = (getattr(args, "context", None) or "").strip()
    lines = [
        f"# {scan_key(name)}: repository quality scan '{name}'",
        "",
        f"- Routed as: /{COMMAND} ({INPUT_TYPE})",
        "",
        "## Repository",
        "",
        "- Repository path: this repository, at the current working revision.",
        "",
        "## Review Scope",
        "",
    ]
    if paths:
        lines.append(f"- Review only: {', '.join(paths)}")
    else:
        lines.append("- Review only: the whole repository, minus the "
                     "exclusions below.")
    lines += [
        "",
        "## Excluded Paths",
        "",
        f"- `{fw_name}/` (framework installation and run evidence)",
        "- `.worktrees/` (task worktrees)",
        "- `.git/`",
    ]
    lines += [f"- {e}" for e in excludes]
    lines += [
        "",
        "## Context",
        "",
        f"- {context}" if context else
        "- Ad-hoc quality scan requested via 'omn-agent quality-scan'; "
        "no ticket attached.",
        "",
        "## Risk Threshold",
        "",
        f"- Findings of severity `{threshold}` and above are actionable; "
        "lower findings are recorded only.",
        "",
    ]
    return "\n".join(lines)


def apply_scan_plan(fw_dir, key: str, content: bytes,
                    summary: str, report: Report) -> tuple[dict, "object", bool]:
    """Write or refresh the scan's task plan and scope document.

    Mirrors ``taskplan.apply_plan``: an unchanged scope is a no-op, and a
    hand-edited scope document is preserved with a warning. Returns
    ``(task, task_dir, changed)``.
    """
    new_hash = sha256_bytes(content)
    tdir = task_dir(fw_dir, key)
    input_path = tdir / "input.md"
    existing = None
    if (tdir / "task-plan.json").exists():
        existing, _ = load_task(fw_dir, key)

    if existing and existing.get("inputHash") == new_hash \
            and input_path.exists() and sha256_file(input_path) == new_hash:
        report.success("Q-SAME", f"scan {key} is already planned with this "
                       f"scope (/{COMMAND} -> {WORKFLOW})")
        return existing, tdir, False

    if input_path.exists() and existing \
            and sha256_file(input_path) != existing.get("inputHash"):
        report.warning("Q-EDITED", f"{input_path.name} was edited by hand; "
                       "preserved",
                       hint="delete the file if you want it regenerated "
                            "from the command line")
        return existing, tdir, False
    tdir.mkdir(parents=True, exist_ok=True)
    atomic_write(input_path, content)
    report.success("Q-SCOPE", f"wrote {input_path.relative_to(fw_dir)}")

    task = existing or {
        "schemaVersion": SCHEMA_VERSION,
        "ticket": key,
        "runId": None,
        "approvals": [],
    }
    task.update({
        "command": COMMAND,
        "workflow": WORKFLOW,
        "inputType": INPUT_TYPE,
        "inputFile": str(input_path.relative_to(fw_dir).as_posix()),
        "inputHash": new_hash,
        "summary": summary,
        "plannedAt": _now(),
    })
    save_task(tdir, task)
    report.success("Q-PLAN", f"{key} routed to /{COMMAND} -> {WORKFLOW} "
                   f"workflow ({INPUT_TYPE})")
    return task, tdir, True


def _base_argv(run_id: str, args) -> list[str]:
    base = ["--run-id", run_id]
    if getattr(args, "gate_policy", None):
        base += ["--gate-policy", args.gate_policy]
    return base


def _scope_content(name: str, fw_dir, args) -> bytes:
    if getattr(args, "scope_file", None):
        from pathlib import Path
        p = Path(args.scope_file)
        if not p.is_file():
            raise OmnError(ExitCode.INVALID_TARGET,
                           f"scope file not found: {p}")
        return p.read_bytes()
    return render_scope(name, fw_dir.name, args).encode("utf-8")


def _archive_changed_run(args, report, task, tdir):
    """The scope changed under a recorded run: archive that run id so a new
    run is materialized from the updated scope. The runtime pins input
    digests at run creation and re-verifies them on every operation, so a
    changed input is a new run -- the same rule `omn-agent update` follows,
    with the same record-the-debt-first shape so a denied approval never
    wedges the next invocation."""
    run_id = task["runId"]
    flow = task.get("scanFlow") or {}
    if flow.get("pendingRunArchive") != run_id:
        flow["pendingRunArchive"] = run_id
        task["scanFlow"] = flow
        save_task(tdir, task)
    _require_approval(f"archive run {run_id} and materialize a new run "
                      "from the changed scan scope", tdir, args.approve, task)
    report.info("Q-RERUN", f"the scan scope changed; run {run_id} is "
                "archived, because a changed input is a new run")
    task.setdefault("runHistory", []).append(
        {"runId": run_id, "archivedAt": _now(),
         "reason": "scan scope changed; a changed input is a new run"})
    task["runId"] = None
    flow.pop("pendingRunArchive", None)
    task["scanFlow"] = flow
    save_task(tdir, task)


def _materialize(args, report, target, fw_dir, task, tdir) -> ExitCode | None:
    """Materialize the runtime run for the scan's scope. Returns an exit
    code to stop on, or None with task['runId'] recorded."""
    _require_approval(f"materialize runtime run for {task['ticket']} "
                      f"(/{task['command']})", tdir, args.approve, task)
    argv = ["plan", "--command", task["command"],
            "--input-file", str(fw_dir / task["inputFile"]),
            "--input-type", task["inputType"],
            "--requester", f"omn-agent:{getpass.getuser()}"]
    if getattr(args, "gate_policy", None):
        argv += ["--gate-policy", args.gate_policy]
    rc, out = _invoke(fw_dir, target, argv, report)
    if rc == 0:
        m = RUN_ID_RE.search(out)
        if m:
            task["runId"] = m.group(0)
            report.success("Q-RUN", f"runtime run {task['runId']} "
                           f"materialized for {task['ticket']}")
        else:
            report.warning("Q-RUNID", "runtime did not report a run id; "
                           "record it manually in task-plan.json if needed")
    save_task(tdir, task)
    if rc != 0 or not task.get("runId"):
        report.error("Q-RUN", f"materializing the runtime run failed "
                     f"(exit {rc}); the runtime output above is "
                     "authoritative",
                     hint=f"inspect with 'omn-agent run {task['ticket']} "
                          "--show'")
        return report.finish(error_code=ExitCode.UNEXPECTED)
    return None


def _handoff(report, fw_dir, task, status) -> ExitCode:
    """The run is complete: the review package is the deliverable and the
    Quality Handoff Gate carries the human decision."""
    run_id = task["runId"]
    artifact = fw_dir / "runs" / run_id / "states" / PHASE / "artifacts" \
        / "review-package.md"
    if artifact.is_file():
        report.success("Q-PACKAGE", "review package: "
                       f"{artifact.relative_to(fw_dir)}")
    gate = _awaiting_gate(status)
    if gate:
        report.success("Q-DONE", f"scan {task['ticket']} is complete; the "
                       f"validated review package is held at the {GATE}")
        report.info("Q-GATE", "the decision belongs to a human tech lead: "
                    f"accept with 'omn-agent run {task['ticket']} --gate "
                    f"\"{GATE}\" --decision approve --owner-role "
                    f"{GATE_DECIDER} --rationale ...', or reject it back "
                    "for a re-scan")
        report.info("Q-NEXT", "route the accepted correction requests as "
                    "cleanup work: '/refactor' for structure, '/bugfix' "
                    "for defects the scan uncovered")
    else:
        report.success("Q-DONE", f"scan {task['ticket']} is complete and "
                       f"its {GATE} is decided")
    return report.finish()


def cmd_quality_scan(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("quality-scan", str(target))
    fw_dir = framework_root(target)

    name = (getattr(args, "name", None) or "repo").strip()
    key = scan_key(name)
    content = _scope_content(name, fw_dir, args)

    if args.dry_run:
        new_hash = sha256_bytes(content)
        existing = None
        if (task_dir(fw_dir, key) / "task-plan.json").exists():
            existing, _ = load_task(fw_dir, key)
        same = existing is not None and existing.get("inputHash") == new_hash
        run_ref = (existing or {}).get("runId") or "(a new run)"
        report.info("Q-PLAN", f"would record scan {key} (/{COMMAND} -> "
                    f"{WORKFLOW}; scope is currently "
                    f"{'unchanged' if same else 'a change'}), drive "
                    f"{run_ref} through the {PHASE!r} phase, and stop at "
                    f"the {GATE} for the human decision")
        report.print()
        return ExitCode.DRY_RUN

    # ---- 1. plan the scan ---------------------------------------------------
    task, tdir, _changed = apply_scan_plan(
        fw_dir, key, content, f"repository quality scan '{name}'", report)

    # ---- 2. a changed scope is a new run --------------------------------------
    # The recorded run pinned the scope it was materialized from
    # (scanFlow.materializedHash); when the task's current scope hash differs,
    # that run can no longer accept any operation, so it is archived. The
    # comparison is against the recorded hash rather than this invocation's
    # `changed` flag, so a denied archive approval never wedges the resume
    # (the scope file is already rewritten by then, making `changed` False).
    run_id = task.get("runId")
    flow = task.get("scanFlow") or {}
    materialized = flow.get("materializedHash") or task["inputHash"]
    if run_id and (materialized != task["inputHash"]
                   or flow.get("pendingRunArchive") == run_id):
        _archive_changed_run(args, report, task, tdir)
        run_id = None

    if not run_id:
        early = _materialize(args, report, target, fw_dir, task, tdir)
        if early is not None:
            return early
        run_id = task["runId"]
        flow = task.get("scanFlow") or {}
        flow["materializedHash"] = task["inputHash"]
        task["scanFlow"] = flow
        save_task(tdir, task)

    # ---- 3. drive the single-phase run ----------------------------------------
    base = _base_argv(run_id, args)
    dispatched_now = None
    for _ in range(MAX_DRIVE_STEPS):
        status = _status_json(fw_dir, target, run_id)
        if status.get("run_status") == "Completed":
            return _handoff(report, fw_dir, task, status)

        active = next((s for s in _steps(status)
                       if s.get("status") in ("leased", "running")), None)
        if active:
            sid = active["state_id"]
            if sid == dispatched_now:
                report.success("Q-DISPATCHED", f"phase '{sid}' is dispatched "
                               f"to {active.get('owner_agent_id') or 'the reviewer agent'}")
                report.info("Q-WAIT", "the host must now run the dispatched "
                            "reviewer subagent; when it has written the "
                            "review package, re-run 'omn-agent quality-scan "
                            f"{name}' to ingest it")
                return report.finish()
            _require_approval(f"complete phase {sid}", tdir, args.approve,
                              task)
            rc, _ = _invoke(fw_dir, target,
                            ["complete"] + base + ["--phase", sid], report)
            save_task(tdir, task)
            if rc != 0:
                report.error("Q-COMPLETE", f"completing phase '{sid}' failed "
                             f"(exit {rc}); has the dispatched reviewer "
                             "produced its review package yet?",
                             hint="run the subagent, then re-run "
                                  f"'omn-agent quality-scan {name}'")
                return report.finish(error_code=ExitCode.UNEXPECTED)
            report.success("Q-COMPLETE", f"phase '{sid}' completion ingested "
                           "and validated")
            continue

        step = _dispatchable_step(status)
        if step:
            sid = step["state_id"]
            _require_approval(f"dispatch phase {sid}", tdir, args.approve,
                              task)
            rc, _ = _invoke(fw_dir, target,
                            ["dispatch"] + base + ["--phase", sid], report)
            save_task(tdir, task)
            if rc != 0:
                report.error("Q-DISPATCH", f"dispatching phase '{sid}' "
                             f"failed (exit {rc}); the runtime output above "
                             "is authoritative",
                             hint=f"inspect with 'omn-agent run "
                                  f"{task['ticket']} --show'")
                return report.finish(error_code=ExitCode.UNEXPECTED)
            dispatched_now = sid
            continue

        gate = _awaiting_gate(status)
        if gate:
            return _handoff(report, fw_dir, task, status)

        report.warning("Q-STALLED", f"run_status="
                       f"{status.get('run_status')} but no phase is "
                       "dispatchable or completable and no gate awaits a "
                       "decision",
                       hint=f"inspect with 'omn-agent run {task['ticket']} "
                            "--show'")
        return report.finish()

    report.error("Q-LIMIT", f"stopped after {MAX_DRIVE_STEPS} runtime steps "
                 "in one invocation",
                 hint=f"re-run 'omn-agent quality-scan {name}' to continue")
    return report.finish(error_code=ExitCode.UNEXPECTED)
