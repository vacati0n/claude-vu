"""Minimal Jira REST client (stdlib only).

Talks to Jira Cloud / Server REST API v2 with basic auth. Credentials come
from environment variables named in the connector config and are never
written to disk. The HTTP transport is injectable so tests (and offline use)
never touch the network.

Search uses the current Cloud endpoint (``/rest/api/2/search/jql`` with
``nextPageToken`` pagination) and falls back to the legacy ``/rest/api/2/search``
(``startAt`` pagination) for Server/Data Center sites that answer 404/410.
"""

from __future__ import annotations

import base64
import json
import os
import urllib.error
import urllib.parse
import urllib.request

from .common import ExitCode, OmnError

FIELDS = ("summary,issuetype,status,priority,assignee,reporter,labels,"
          "created,updated,description")
TIMEOUT_S = 30


class HttpResponse:
    def __init__(self, status: int, body: bytes):
        self.status = status
        self.body = body

    def json(self) -> dict:
        try:
            return json.loads(self.body.decode("utf-8"))
        except ValueError as exc:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"Jira returned a non-JSON response: {exc}")


def _default_transport(url: str, headers: dict[str, str]) -> HttpResponse:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
            return HttpResponse(resp.status, resp.read())
    except urllib.error.HTTPError as exc:
        return HttpResponse(exc.code, exc.read())
    except (urllib.error.URLError, OSError) as exc:
        raise OmnError(ExitCode.UNEXPECTED, f"cannot reach Jira: {exc}",
                       hint="check the base URL and your network")


class JiraClient:
    def __init__(self, settings: dict, transport=None):
        self.base_url = settings["baseUrl"].rstrip("/")
        self.projects = settings.get("projects", [])
        auth = settings.get("auth", {})
        self.email_env = auth.get("emailEnv", "JIRA_EMAIL")
        self.token_env = auth.get("tokenEnv", "JIRA_API_TOKEN")
        self._transport = transport or _default_transport

    def _headers(self) -> dict[str, str]:
        email = os.environ.get(self.email_env)
        token = os.environ.get(self.token_env)
        if not email or not token:
            raise OmnError(
                ExitCode.INCOMPLETE,
                f"Jira credentials are not set: ${self.email_env} / ${self.token_env}",
                hint="export both environment variables (an Atlassian API token, "
                     "not your password) and re-run; omn-agent never stores them")
        raw = base64.b64encode(f"{email}:{token}".encode("utf-8")).decode("ascii")
        return {"Authorization": f"Basic {raw}", "Accept": "application/json"}

    def _get(self, path: str, params: dict[str, str]) -> HttpResponse:
        url = f"{self.base_url}{path}?{urllib.parse.urlencode(params)}"
        resp = self._transport(url, self._headers())
        if resp.status == 401:
            raise OmnError(ExitCode.INCOMPLETE, "Jira rejected the credentials (401)",
                           hint=f"check ${self.email_env} and ${self.token_env}")
        if resp.status == 403:
            raise OmnError(ExitCode.INCOMPLETE, "Jira denied access (403)",
                           hint="the account lacks permission for this project")
        return resp

    def credentials_present(self) -> bool:
        return bool(os.environ.get(self.email_env) and os.environ.get(self.token_env))

    def myself(self) -> dict:
        """Connection test: who does Jira think we are?"""
        resp = self._get("/rest/api/2/myself", {})
        if resp.status != 200:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"Jira connection test failed with HTTP {resp.status}")
        return resp.json()

    def list_projects(self) -> list[dict]:
        """Projects visible to the account, as [{'key': ..., 'name': ...}]."""
        projects = self._projects_search()
        if projects is None:
            projects = self._projects_legacy()
        return [{"key": p.get("key", ""), "name": p.get("name", "")}
                for p in projects if p.get("key")]

    def _projects_search(self) -> list[dict] | None:
        """Cloud endpoint, paginated; None when the site does not serve it."""
        out: list[dict] = []
        while True:
            resp = self._get("/rest/api/2/project/search",
                             {"startAt": str(len(out)), "maxResults": "50"})
            if resp.status in (404, 410) and not out:
                return None
            if resp.status != 200:
                raise OmnError(ExitCode.UNEXPECTED,
                               f"Jira project listing failed with HTTP {resp.status}")
            data = resp.json()
            page = data.get("values", [])
            out.extend(page)
            if not page or data.get("isLast", True) or len(out) >= data.get("total", 0):
                return out

    def _projects_legacy(self) -> list[dict]:
        resp = self._get("/rest/api/2/project", {})
        if resp.status != 200:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"Jira project listing failed with HTTP {resp.status}")
        data = resp.json()
        return data if isinstance(data, list) else []

    def issue(self, key: str) -> dict:
        resp = self._get(f"/rest/api/2/issue/{urllib.parse.quote(key)}",
                         {"fields": FIELDS})
        if resp.status == 404:
            raise OmnError(ExitCode.INVALID_TARGET, f"Jira issue not found: {key}")
        if resp.status != 200:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"Jira issue fetch failed with HTTP {resp.status}")
        return self.normalize(resp.json())

    def search(self, jql: str, max_results: int) -> list[dict]:
        issues = self._search_new(jql, max_results)
        if issues is None:
            issues = self._search_legacy(jql, max_results)
        return [self.normalize(i) for i in issues]

    def _search_new(self, jql: str, max_results: int) -> list[dict] | None:
        issues: list[dict] = []
        token = None
        while len(issues) < max_results:
            params = {"jql": jql, "fields": FIELDS,
                      "maxResults": str(min(50, max_results - len(issues)))}
            if token:
                params["nextPageToken"] = token
            resp = self._get("/rest/api/2/search/jql", params)
            if resp.status in (404, 410) and not issues:
                return None            # endpoint absent -> legacy fallback
            if resp.status != 200:
                raise OmnError(ExitCode.UNEXPECTED,
                               f"Jira search failed with HTTP {resp.status}: "
                               f"{resp.body[:300].decode('utf-8', 'replace')}")
            data = resp.json()
            issues.extend(data.get("issues", []))
            token = data.get("nextPageToken")
            if not token or data.get("isLast", not token):
                break
        return issues[:max_results]

    def _search_legacy(self, jql: str, max_results: int) -> list[dict]:
        issues: list[dict] = []
        while len(issues) < max_results:
            resp = self._get("/rest/api/2/search",
                             {"jql": jql, "fields": FIELDS, "startAt": str(len(issues)),
                              "maxResults": str(min(50, max_results - len(issues)))})
            if resp.status != 200:
                raise OmnError(ExitCode.UNEXPECTED,
                               f"Jira search failed with HTTP {resp.status}: "
                               f"{resp.body[:300].decode('utf-8', 'replace')}")
            data = resp.json()
            page = data.get("issues", [])
            issues.extend(page)
            if not page or len(issues) >= data.get("total", 0):
                break
        return issues[:max_results]

    def normalize(self, issue: dict) -> dict:
        f = issue.get("fields", {})

        def name(field):
            v = f.get(field)
            return (v or {}).get("name") if isinstance(v, dict) else v

        def person(field):
            v = f.get(field) or {}
            return v.get("displayName") or v.get("emailAddress")

        description = f.get("description")
        if isinstance(description, dict):      # ADF document (API v3 shapes)
            description = _adf_to_text(description)
        return {
            "key": issue.get("key"),
            "id": issue.get("id"),
            "summary": f.get("summary") or "",
            "type": name("issuetype") or "Task",
            "status": name("status") or "",
            "priority": name("priority") or "",
            "assignee": person("assignee"),
            "reporter": person("reporter"),
            "labels": f.get("labels") or [],
            "created": f.get("created"),
            "updated": f.get("updated"),
            "description": description or "",
            "url": f"{self.base_url}/browse/{issue.get('key')}",
        }


def _adf_to_text(node: dict) -> str:
    """Flatten an Atlassian Document Format tree to plain text."""
    if node.get("type") == "text":
        return node.get("text", "")
    parts = [_adf_to_text(c) for c in node.get("content", []) if isinstance(c, dict)]
    joined = "".join(parts)
    if node.get("type") in ("paragraph", "heading", "listItem", "codeBlock",
                            "blockquote"):
        return joined + "\n"
    return joined
