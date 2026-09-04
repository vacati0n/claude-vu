"""Ticket-provider resolution for the multi-provider one-command flow.

`omn-agent run <Provider> <TicketKey>` names its ticket source by provider.
A provider is a connector recorded in ``.omn-agent/config/mcp.json`` under
``servers`` (written by ``omn-agent mcp add jira`` / ``mcp add msdev``); the
entry's ``kind`` selects the client implementation. Resolution is
case-insensitive and alias-aware, so ``Jira``, ``jira``, ``MSDev``, and
``azure-devops`` all land on the connector the user means, and every failure
mode names its fix:

* nothing configured at all      -> INCOMPLETE with the setup command;
* name matches no connector      -> INVALID_TARGET listing what is configured;
* connector kind not implemented -> INCOMPLETE naming the supported kinds.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

from .common import ExitCode, OmnError
from .jira_client import JiraClient
from .mcp import load_mcp_config
from .msdev_client import MsDevClient

# kind -> client implementation. A config may reference kinds this build
# does not implement (e.g. written by a newer omn-agent); that is the
# "missing connector" error, distinct from an unknown provider name.
CONNECTORS = {
    "jira": JiraClient,
    "msdev": MsDevClient,
}

# Spellings people use for a kind. Provider names are matched against the
# configured server names first; aliases only widen the kind fallback.
KIND_ALIASES = {
    "jira": "jira",
    "msdev": "msdev",
    "azure-devops": "msdev",
    "azuredevops": "msdev",
    "ado": "msdev",
}


@dataclasses.dataclass
class Provider:
    name: str        # the configured connector name in config/mcp.json
    kind: str        # canonical connector kind ("jira", "msdev", ...)
    client: object   # a client exposing .issue(key) -> normalized ticket

    @property
    def label(self) -> str:
        return {"jira": "Jira", "msdev": "Azure DevOps (MSDev)"} \
            .get(self.kind, self.name)


def _kind_of(server: dict) -> str:
    return (server.get("kind") or "").strip().lower()


def configured_providers(fw_dir: Path) -> dict[str, dict]:
    """The connector records from config/mcp.json (may be empty)."""
    cfg = load_mcp_config(fw_dir)
    return (cfg or {}).get("servers") or {}


def resolve_provider(fw_dir: Path, name: str, transport=None) -> Provider:
    """Map a user-supplied provider name onto a configured connector."""
    servers = configured_providers(fw_dir)
    if not servers:
        raise OmnError(
            ExitCode.INCOMPLETE,
            "no MCP connectors are configured for this repo",
            hint="run 'omn-agent mcp init jira' (guided) or 'omn-agent mcp "
                 "add jira/msdev ...' to configure a ticket provider first")

    wanted = (name or "").strip().lower()
    match = next((k for k in servers if k.lower() == wanted), None)
    if match is None:
        # Fall back to the kind: 'MSDev' finds a connector saved under any
        # name as long as exactly one entry has that kind.
        kind = KIND_ALIASES.get(wanted)
        by_kind = [k for k, s in servers.items()
                   if kind and KIND_ALIASES.get(_kind_of(s)) == kind]
        if len(by_kind) == 1:
            match = by_kind[0]
        elif len(by_kind) > 1:
            raise OmnError(
                ExitCode.INVALID_TARGET,
                f"provider '{name}' is ambiguous: connectors "
                f"{', '.join(sorted(by_kind))} all have kind "
                f"'{kind}'",
                hint="use the connector name from "
                     ".omn-agent/config/mcp.json instead")
        else:
            raise OmnError(
                ExitCode.INVALID_TARGET,
                f"unknown provider '{name}'; configured providers: "
                f"{', '.join(sorted(servers))}",
                hint="provider names map to the connectors in "
                     ".omn-agent/config/mcp.json; add one with "
                     "'omn-agent mcp add jira/msdev ...'")

    server = servers[match]
    kind = KIND_ALIASES.get(_kind_of(server), _kind_of(server))
    cls = CONNECTORS.get(kind)
    if cls is None:
        raise OmnError(
            ExitCode.INCOMPLETE,
            f"provider '{match}' is configured with kind "
            f"'{_kind_of(server) or '(none)'}', but no connector for that "
            "kind is available in this omn-agent build",
            hint=f"supported connector kinds: {', '.join(sorted(CONNECTORS))}"
                 "; fix the 'kind' in .omn-agent/config/mcp.json or upgrade "
                 "omn-agent")
    return Provider(name=match, kind=kind,
                    client=cls(server, transport=transport))
