"""Turn a synced ticket into an actionable framework task (`omn-agent plan`).

Classification is deterministic (issue type, then labels/summary keywords) and
maps onto the framework's real command -> workflow routing, so the produced
task drives the installed runtime as-is:

    Bug                          -> bugfix      -> fix-bug            (defect-report)
    refactor / tech-debt         -> refactor    -> refactor           (change-request)
    investigate / research/spike -> investigate -> investigate        (business-intent)
    everything else              -> implement   -> implement-feature  (feature-request)

Output, under ``.omn-agent/tasks/<KEY>/``:
    input.md        the runtime input document rendered from the ticket
    task-plan.json  routing decision, input hash, run id (once started), approvals

Re-running is safe: an unchanged ticket is a no-op, an updated ticket
regenerates ``input.md`` only while its content still matches what this tool
last wrote -- a hand-edited input document is preserved with a warning.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from . import SCHEMA_VERSION
from .common import ExitCode, OmnError, Report
from .manifest import atomic_write, sha256_bytes, sha256_file
from .repo import framework_root, resolve_target
from .tickets import load_ticket

ROUTES = {
    "bugfix": ("fix-bug", "defect-report"),
    "implement": ("implement-feature", "feature-request"),
    "refactor": ("refactor", "change-request"),
    "investigate": ("investigate", "business-intent"),
}

_REFRACTOR_WORDS = ("refactor", "tech debt", "tech-debt", "cleanup", "restructure")
_INVESTIGATE_WORDS = ("investigate", "research", "spike", "feasibility", "explore")


def classify(ticket: dict) -> str:
    itype = (ticket.get("type") or "").lower()
    text = " ".join([ticket.get("summary", ""), *ticket.get("labels", [])]).lower()
    if itype == "bug":
        return "bugfix"
    if any(w in text for w in _REFRACTOR_WORDS):
        return "refactor"
    if itype in ("spike",) or any(w in text for w in _INVESTIGATE_WORDS):
        return "investigate"
    return "implement"


def render_input(ticket: dict, command: str, input_type: str) -> str:
    desc = (ticket.get("description") or "").strip()
    has_ac = "acceptance criteria" in desc.lower()
    lines = [
        f"# {ticket['key']}: {ticket.get('summary', '').strip()}",
        "",
        f"- Source: {ticket.get('url', ticket['key'])}",
        # Jira workflow Status is deliberately NOT rendered here: input.md is
        # the run's identity digest, and a mere status transition (e.g.
        # "Ready for review" -> "In Progress") must not invalidate an
        # in-flight run when the requirement itself is unchanged.
        f"- Issue type: {ticket.get('type', '')}   Priority: "
        f"{ticket.get('priority', '') or 'unset'}",
        f"- Labels: {', '.join(ticket.get('labels', [])) or 'none'}",
        f"- Routed as: /{command} ({input_type})",
        "",
        "## Description",
        "",
        desc or "_The ticket has no description._",
        "",
    ]
    if not has_ac:
        lines += [
            "## Acceptance criteria",
            "",
            "_Not provided in the ticket. To be defined and approved at the scope "
            "gate before implementation starts._",
            "",
        ]
    return "\n".join(lines)


def task_dir(fw_dir: Path, key: str) -> Path:
    return fw_dir / "tasks" / key.upper()


def load_task(fw_dir: Path, key: str) -> tuple[dict, Path]:
    tdir = task_dir(fw_dir, key)
    path = tdir / "task-plan.json"
    if not path.exists():
        raise OmnError(ExitCode.INCOMPLETE, f"no task plan for {key}",
                       hint=f"run 'omn-agent plan {key}' first")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")), tdir
    except (OSError, ValueError) as exc:
        raise OmnError(ExitCode.UNEXPECTED, f"task plan unreadable: {path} ({exc})")


def save_task(tdir: Path, task: dict):
    atomic_write(tdir / "task-plan.json",
                 (json.dumps(task, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def iter_tasks(fw_dir: Path):
    """Yield ``(task, task_dir)`` for every readable task plan, sorted by
    key. An unreadable plan is skipped, never a crash -- iteration is used
    by best-effort sweeps."""
    tasks_dir = fw_dir / "tasks"
    if not tasks_dir.is_dir():
        return
    for tdir in sorted(tasks_dir.iterdir()):
        path = tdir / "task-plan.json"
        if not path.is_file():
            continue
        try:
            yield json.loads(path.read_text(encoding="utf-8-sig")), tdir
        except (OSError, ValueError):
            continue


def apply_plan(fw_dir: Path, ticket: dict, command: str,
               report: Report) -> tuple[dict, Path, bool]:
    """Write or refresh a ticket's task plan and input document.

    The shared core of `omn-agent plan`, also driven by `omn-agent update`.
    Returns ``(task, task_dir, changed)`` where ``changed`` is False when the
    routed input already matches what the task plan last recorded (the
    P-SAME no-op), and True when input.md / task-plan.json were rewritten --
    including for a brand-new task.
    """
    workflow, input_type = ROUTES[command]
    content = render_input(ticket, command, input_type).encode("utf-8")
    new_hash = sha256_bytes(content)

    tdir = task_dir(fw_dir, ticket["key"])
    input_path = tdir / "input.md"
    existing = None
    if (tdir / "task-plan.json").exists():
        existing, _ = load_task(fw_dir, ticket["key"])

    if existing and existing.get("inputHash") == new_hash \
            and input_path.exists() and sha256_file(input_path) == new_hash:
        report.success("P-SAME", f"task for {ticket['key']} is already up to date "
                       f"(/{command} -> {workflow})")
        return existing, tdir, False

    if input_path.exists() and existing \
            and sha256_file(input_path) != existing.get("inputHash"):
        report.warning("P-EDITED", f"{input_path.name} was edited by hand; preserved",
                       hint="delete the file if you want it regenerated from the ticket")
    else:
        tdir.mkdir(parents=True, exist_ok=True)
        atomic_write(input_path, content)
        report.success("P-INPUT", f"wrote {input_path.relative_to(fw_dir)}")

    task = existing or {
        "schemaVersion": SCHEMA_VERSION,
        "ticket": ticket["key"],
        "runId": None,
        "approvals": [],
    }
    task.update({
        "command": command,
        "workflow": workflow,
        "inputType": input_type,
        "inputFile": str(input_path.relative_to(fw_dir).as_posix()),
        "inputHash": new_hash,
        "summary": ticket.get("summary", ""),
        "plannedAt": datetime.datetime.now(datetime.timezone.utc)
        .isoformat(timespec="seconds"),
    })
    save_task(tdir, task)
    report.success("P-PLAN", f"{ticket['key']} routed to /{command} -> {workflow} "
                   f"workflow ({input_type})")
    return task, tdir, True


def cmd_plan(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("plan", str(target))
    fw_dir = framework_root(target)

    ticket = load_ticket(fw_dir, args.key)
    command = args.command or classify(ticket)
    if command not in ROUTES:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"unknown command '{command}'; choose from "
                       f"{', '.join(sorted(ROUTES))}")
    workflow, input_type = ROUTES[command]

    if args.dry_run:
        content = render_input(ticket, command, input_type).encode("utf-8")
        new_hash = sha256_bytes(content)
        existing = None
        if (task_dir(fw_dir, ticket["key"]) / "task-plan.json").exists():
            existing, _ = load_task(fw_dir, ticket["key"])
        state = ("no changes" if existing and existing.get("inputHash") == new_hash
                 else "would write task plan and input.md")
        report.info("P-PLAN", f"{ticket['key']} -> /{command} -> {workflow} "
                    f"({input_type}); {state}")
        report.print()
        return ExitCode.DRY_RUN

    task, _, changed = apply_plan(fw_dir, ticket, command, report)
    if changed:
        report.info("P-NEXT", f"start it with 'omn-agent run {ticket['key']} "
                    "--approve' (each side-effecting runtime step requires "
                    "approval)")
    return report.finish()
