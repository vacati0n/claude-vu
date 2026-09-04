"""Minimal Azure DevOps (MSDev) work-item client (stdlib only).

Talks to the Azure DevOps REST API with a personal access token. Like the
Jira client, credentials come from environment variables named in the
connector config and are never written to disk, and the HTTP transport is
injectable so tests (and offline use) never touch the network.

Work items are addressed as ``<PREFIX>-<id>`` (e.g. ``ONN-115``) or as a bare
numeric id; only the trailing number is the Azure DevOps work item id -- the
prefix is a team convention kept as the ticket key so tasks, branches, and
worktrees stay named the way people talk about the work.

``normalize`` produces exactly the ticket shape ``JiraClient.normalize``
produces, so everything downstream (classification, routing, input
rendering, worktree sweeps) is provider-agnostic.
"""

from __future__ import annotations

import base64
import html
import os
import re
import urllib.parse

from .common import ExitCode, OmnError
from .jira_client import HttpResponse, TIMEOUT_S

API_VERSION = "7.1"

WORK_ITEM_KEY_RE = re.compile(r"^(?:[A-Za-z][A-Za-z0-9_]*-)?(\d+)$")


def work_item_id(key: str) -> int:
    """The numeric work item id inside a ``PREFIX-123`` (or bare ``123``) key."""
    m = WORK_ITEM_KEY_RE.match((key or "").strip())
    if not m:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"'{key}' is not a valid Azure DevOps ticket key",
                       hint="use the numeric work item id, optionally prefixed "
                            "(e.g. 115 or ONN-115); the trailing number is the "
                            "work item id")
    return int(m.group(1))


def _default_transport(url: str, headers: dict[str, str]) -> HttpResponse:
    import urllib.error
    import urllib.request
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return HttpResponse(resp.status, resp.read())
    except urllib.error.HTTPError as exc:
        return HttpResponse(exc.code, exc.read())
    except (urllib.error.URLError, OSError) as exc:
        raise OmnError(ExitCode.UNEXPECTED, f"cannot reach Azure DevOps: {exc}",
                       hint="check the organization URL and your network")


class MsDevClient:
    """Fetch work items from one Azure DevOps organization (optionally scoped
    to a project)."""

    def __init__(self, settings: dict, transport=None):
        base_url = (settings.get("baseUrl") or "").rstrip("/")
        if not base_url:
            raise OmnError(ExitCode.INCOMPLETE,
                           "the MSDev connector has no baseUrl configured",
                           hint="re-run 'omn-agent mcp add msdev --org-url "
                                "https://dev.azure.com/<org> --project <NAME>'")
        self.base_url = base_url
        self.project = (settings.get("project") or "").strip()
        self.projects = settings.get("projects", [])
        auth = settings.get("auth", {})
        self.token_env = auth.get("tokenEnv", "AZURE_DEVOPS_PAT")
        self._transport = transport or _default_transport

    def credentials_present(self) -> bool:
        return bool(os.environ.get(self.token_env))

    def _headers(self) -> dict[str, str]:
        token = os.environ.get(self.token_env)
        if not token:
            raise OmnError(
                ExitCode.INCOMPLETE,
                f"Azure DevOps credentials are not set: ${self.token_env}",
                hint="export the environment variable with a personal access "
                     "token (work items: read scope) and re-run; omn-agent "
                     "never stores it")
        raw = base64.b64encode(f":{token}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {raw}", "Accept": "application/json"}

    def _get(self, path: str, params: dict[str, str]) -> HttpResponse:
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(params)}"
        resp = self._transport(url, self._headers())
        if resp.status == 401:
            raise OmnError(ExitCode.INCOMPLETE,
                           "Azure DevOps rejected the credentials (401)",
                           hint=f"check ${self.token_env} (the token may have "
                                "expired)")
        if resp.status == 403:
            raise OmnError(ExitCode.INCOMPLETE,
                           "Azure DevOps denied access (403)",
                           hint="the token lacks permission for this project")
        return resp

    def issue(self, key: str) -> dict:
        """Fetch one work item, addressed as PREFIX-<id> or a bare id."""
        wid = work_item_id(key)
        scope = f"/{urllib.parse.quote(self.project)}" if self.project else ""
        resp = self._get(f"{scope}/_apis/wit/workitems/{wid}",
                         {"api-version": API_VERSION, "$expand": "links"})
        if resp.status == 404:
            raise OmnError(ExitCode.INVALID_TARGET,
                           f"Azure DevOps work item not found: {key} "
                           f"(id {wid})",
                           hint="check the id" +
                                (f" and that it belongs to project "
                                 f"'{self.project}'" if self.project else ""))
        if resp.status != 200:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"Azure DevOps work item fetch failed with HTTP "
                           f"{resp.status}")
        return self.normalize(key, resp.json())

    def normalize(self, key: str, item: dict) -> dict:
        """Shape one raw work item like a normalized Jira ticket."""
        f = item.get("fields", {})

        def person(field):
            v = f.get(field) or {}
            if isinstance(v, dict):
                return v.get("displayName") or v.get("uniqueName")
            return v or None

        tags = [t.strip() for t in (f.get("System.Tags") or "").split(";")
                if t.strip()]
        description = _html_to_text(f.get("System.Description") or "")
        if not description.strip():
            # Bugs frequently carry their substance in the repro steps field.
            description = _html_to_text(
                f.get("Microsoft.VSTS.TCM.ReproSteps") or "")
        priority = f.get("Microsoft.VSTS.Common.Priority")
        url = (item.get("_links", {}).get("html") or {}).get("href")
        if not url:
            scope = f"/{self.project}" if self.project else ""
            url = f"{self.base_url}{scope}/_workitems/edit/{item.get('id')}"
        return {
            "key": (key or "").strip().upper(),
            "id": str(item.get("id")),
            "summary": f.get("System.Title") or "",
            "type": f.get("System.WorkItemType") or "Task",
            "status": f.get("System.State") or "",
            "priority": "" if priority is None else str(priority),
            "assignee": person("System.AssignedTo"),
            "reporter": person("System.CreatedBy"),
            "labels": tags,
            "created": f.get("System.CreatedDate"),
            "updated": f.get("System.ChangedDate"),
            "description": description,
            "url": url,
        }


_TAG_RE = re.compile(r"<[^>]+>")
_BLOCK_RE = re.compile(r"</?(?:p|div|br|li|tr|h[1-6])\b[^>]*>", re.IGNORECASE)


def _html_to_text(markup: str) -> str:
    """Flatten Azure DevOps rich-text (HTML) fields to plain text."""
    if not markup:
        return ""
    text = _BLOCK_RE.sub("\n", markup)
    text = _TAG_RE.sub("", text)
    text = html.unescape(text)
    lines = [ln.strip() for ln in text.splitlines()]
    out: list[str] = []
    for ln in lines:
        if ln or (out and out[-1]):
            out.append(ln)
    return "\n".join(out).strip()
