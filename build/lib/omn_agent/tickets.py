"""Ticket ingestion: `omn-agent tickets sync` and `omn-agent tickets pull`.

Synced tickets land as normalized JSON in ``.omn-agent/tickets/inbox/<KEY>.json``.
The inbox is operational data owned by this tool, so re-syncing updates files
in place; idempotency is reported by comparing each ticket's ``updated``
timestamp (created / updated / unchanged counts).

Both commands also sweep task worktrees: a task whose ticket turns out to be
closed has its worktree released automatically (the branch is kept). The
default sync JQL excludes closed tickets, so the sweep re-fetches each
bound ticket by key rather than trusting the search results.
"""

from __future__ import annotations

import datetime
import json
from pathlib import Path

from . import worktree
from .common import ExitCode, OmnError, Report
from .jira_client import JiraClient
from .manifest import atomic_write
from .mcp import jira_settings
from .repo import framework_root, resolve_target

SYNC_STATE_REL = "tickets/sync-state.json"


def _inbox(fw_dir: Path) -> Path:
    p = fw_dir / "tickets" / "inbox"
    p.mkdir(parents=True, exist_ok=True)
    return p


def load_ticket(fw_dir: Path, key: str) -> dict:
    path = _inbox(fw_dir) / f"{key.upper()}.json"
    if not path.exists():
        raise OmnError(ExitCode.INCOMPLETE, f"ticket {key} is not in the inbox",
                       hint=f"run 'omn-agent tickets pull {key}' or "
                            "'omn-agent tickets sync' first")
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise OmnError(ExitCode.UNEXPECTED, f"ticket file unreadable: {path} ({exc})")


def _store(fw_dir: Path, tickets: list[dict], report: Report):
    inbox = _inbox(fw_dir)
    created = updated = unchanged = 0
    for t in tickets:
        path = inbox / f"{t['key']}.json"
        blob = (json.dumps(t, indent=2, sort_keys=True) + "\n").encode("utf-8")
        if not path.exists():
            created += 1
        else:
            try:
                old = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                old = {}
            if old.get("updated") == t.get("updated"):
                unchanged += 1
                continue
            updated += 1
        atomic_write(path, blob)
    report.success("T-SYNC", f"{len(tickets)} ticket(s): {created} new, "
                   f"{updated} updated, {unchanged} unchanged")


def _client(fw_dir: Path, transport=None) -> JiraClient:
    return JiraClient(jira_settings(fw_dir), transport=transport)


def _fresh_status(client: JiraClient, fw_dir: Path, key: str) -> str | None:
    """The ticket's current status, fetched by key (the default sync JQL
    excludes closed tickets, so a closed ticket is invisible to search).
    The refreshed ticket is stored back into the inbox on the way."""
    ticket = client.issue(key)
    atomic_write(_inbox(fw_dir) / f"{ticket['key']}.json",
                 (json.dumps(ticket, indent=2, sort_keys=True) + "\n")
                 .encode("utf-8"))
    return ticket.get("status")


def cmd_tickets_sync(args, transport=None) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("tickets sync", str(target))
    fw_dir = framework_root(target)
    client = _client(fw_dir, transport)

    if args.jql:
        jql = args.jql
    else:
        if not client.projects:
            raise OmnError(ExitCode.INCOMPLETE, "no Jira projects configured",
                           hint="re-run 'omn-agent mcp add jira --project <KEY>' "
                                "or pass --jql")
        # Keys must be quoted: a bare key that is a JQL reserved word
        # (e.g. ON, IN, OR, BY) makes Jira reject the whole query with 400.
        keys = ", ".join(f'"{k}"' for k in client.projects)
        jql = (f"project in ({keys}) AND statusCategory != Done "
               f"ORDER BY updated DESC")

    report.info("T-JQL", f"query: {jql}")
    tickets = client.search(jql, max_results=args.max)
    _store(fw_dir, tickets, report)

    worktree.cleanup_closed_ticket_worktrees(
        target, fw_dir, report,
        fetch_status=lambda key: _fresh_status(client, fw_dir, key))

    state_path = fw_dir / SYNC_STATE_REL
    state = {"lastSyncAt": datetime.datetime.now(datetime.timezone.utc)
             .isoformat(timespec="seconds"),
             "jql": jql, "count": len(tickets)}
    atomic_write(state_path, (json.dumps(state, indent=2) + "\n").encode("utf-8"))
    if tickets:
        report.info("T-NEXT", f"plan work from a ticket with "
                    f"'omn-agent plan {tickets[0]['key']}'")
    return report.finish()


def cmd_tickets_pull(args, transport=None) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("tickets pull", str(target))
    fw_dir = framework_root(target)
    client = _client(fw_dir, transport)

    tickets = [client.issue(key) for key in args.keys]
    _store(fw_dir, tickets, report)
    for t in tickets:
        report.info("T-TICKET", f"{t['key']} [{t['type']}] {t['summary']}")

    # Pull already fetched these tickets fresh; sweep with what it knows
    # (tasks whose tickets weren't pulled are left alone).
    by_key = {t["key"]: t.get("status") for t in tickets}
    worktree.cleanup_closed_ticket_worktrees(
        target, fw_dir, report, fetch_status=by_key.get)
    return report.finish()
