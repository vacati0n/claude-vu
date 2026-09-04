"""MCP connector configuration (`omn-agent mcp add jira` / `omn-agent mcp init jira`).

Two entry points share one write path, and neither ever stores a secret:

* ``mcp add jira`` -- flag-based, scriptable (unchanged, backward-compatible).
* ``mcp init jira`` -- guided interactive setup for people who don't know
  their project keys or config details: validates the repo first, normalizes
  the site URL, tests the connection, auto-detects project keys from Jira
  when credentials are present, and confirms before writing anything.

What gets written:

1. ``.omn-agent/config/mcp.json`` -- omn-agent's own connector record: base
   URL, project keys, and the *names* of the environment variables that hold
   credentials. `tickets sync/pull` reads this.
2. ``<repo>/.mcp.json`` -- the standard MCP server registration that agent
   hosts (e.g. Claude Code) read, pointing the ``jira`` server at Atlassian's
   remote MCP endpoint via ``mcp-remote`` (OAuth in the browser on first use).
   The file is merged, never clobbered: existing servers are preserved, and an
   existing ``jira`` entry with different content is left alone with a warning
   unless ``--force`` is given.

Credentials are only ever read from environment variables at call time.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.parse
from pathlib import Path

from . import SCHEMA_VERSION
from .common import ExitCode, OmnError, Report
from .jira_client import JiraClient
from .manifest import atomic_write
from .repo import framework_root, resolve_target

MCP_CONFIG_REL = "config/mcp.json"
ATLASSIAN_REMOTE_MCP = "https://mcp.atlassian.com/v1/sse"
ATLASSIAN_TOKEN_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
DEFAULT_EMAIL_ENV = "JIRA_EMAIL"
DEFAULT_TOKEN_ENV = "JIRA_API_TOKEN"
DEFAULT_MSDEV_TOKEN_ENV = "AZURE_DEVOPS_PAT"
MSDEV_MCP_PACKAGE = "@azure-devops/mcp"
MAX_LISTED_PROJECTS = 40


def load_mcp_config(fw_dir: Path) -> dict | None:
    path = fw_dir / MCP_CONFIG_REL
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        raise OmnError(ExitCode.INCOMPLETE,
                       f"{MCP_CONFIG_REL} is unreadable: {exc}",
                       hint="re-run 'omn-agent mcp init jira' to rewrite it")


def jira_settings(fw_dir: Path) -> dict:
    cfg = load_mcp_config(fw_dir)
    server = (cfg or {}).get("servers", {}).get("jira")
    if not server:
        raise OmnError(ExitCode.INCOMPLETE, "Jira is not configured for this repo",
                       hint="run 'omn-agent mcp init jira' for guided setup, or "
                            "'omn-agent mcp add jira --base-url "
                            "https://<site>.atlassian.net --project <KEY>'")
    return server


def normalize_base_url(raw: str, *, what: str = "Jira site",
                       example: str = "https://yourteam.atlassian.net") -> str:
    """Accept 'team.atlassian.net' as well as a full URL; reject anything else."""
    raw = (raw or "").strip().rstrip("/")
    if not raw:
        raise OmnError(ExitCode.INVALID_TARGET, f"the {what} URL is empty")
    if "://" not in raw:
        raw = "https://" + raw
    parsed = urllib.parse.urlparse(raw)
    if parsed.scheme not in ("https", "http") or not parsed.netloc \
            or "." not in parsed.netloc:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"'{raw}' does not look like a {what} URL",
                       hint=f"expected something like {example}")
    return raw


# Jira project keys: a letter, then letters/digits/underscore. Anything else
# can never match a real project and would only fail later, inside the JQL.
PROJECT_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def parse_project_keys(values: list[str]) -> list[str]:
    keys: set[str] = set()
    for value in values:
        for part in value.split(","):
            part = part.strip().upper()
            if not part:
                continue
            if not PROJECT_KEY_RE.match(part):
                raise OmnError(ExitCode.INVALID_TARGET,
                               f"'{part}' is not a valid Jira project key",
                               hint="keys are letters, digits, and underscores "
                                    "starting with a letter, e.g. PROJ")
            keys.add(part)
    return sorted(keys)


def _require_installed(target: Path) -> Path:
    fw_dir = framework_root(target)
    if not fw_dir.is_dir():
        raise OmnError(ExitCode.INCOMPLETE,
                       "framework is not installed in the target",
                       hint="run 'omn-agent install <target>' first")
    return fw_dir


def _write_server(target: Path, fw_dir: Path, name: str, server: dict,
                  report: Report, *, force: bool, mcp_entry: dict,
                  cred_envs: list[str], next_hint: str):
    """Record one connector in config/mcp.json and register its MCP server
    in the repo's .mcp.json (merge-safe). Shared by every connector kind."""
    cfg = load_mcp_config(fw_dir) or {"schemaVersion": SCHEMA_VERSION, "servers": {}}
    existing = cfg["servers"].get(name)
    if existing == server:
        report.info("M-SAME", f"{MCP_CONFIG_REL} already up to date")
    else:
        cfg["servers"][name] = server
        path = fw_dir / MCP_CONFIG_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write(path, (json.dumps(cfg, indent=2) + "\n").encode("utf-8"))
        envs = " / ".join(f"${e}" for e in cred_envs)
        report.success("M-CONFIG", f"{'updated' if existing else 'wrote'} "
                       f"{MCP_CONFIG_REL} (no secrets stored; credentials are read "
                       f"from {envs} at call time)")

    _merge_root_mcp_json(target, report, name=name, entry=mcp_entry,
                         force=force)

    report.info("M-NEXT", next_hint)


def _write_jira_server(target: Path, fw_dir: Path, server: dict,
                       report: Report, *, force: bool):
    auth = server["auth"]
    _write_server(
        target, fw_dir, "jira", server, report, force=force,
        mcp_entry={"command": "npx",
                   "args": ["-y", "mcp-remote", ATLASSIAN_REMOTE_MCP]},
        cred_envs=[auth["emailEnv"], auth["tokenEnv"]],
        next_hint="set the credential environment variables, then run "
                  "'omn-agent tickets sync' -- or let an MCP-capable agent "
                  "host use the 'jira' server directly (browser OAuth on "
                  "first use)")


# ------------------------------------------------------------------ mcp add


def cmd_mcp_add_jira(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("mcp add jira", str(target))
    fw_dir = _require_installed(target)

    base_url = normalize_base_url(args.base_url)
    projects = parse_project_keys(args.project)
    if not projects:
        raise OmnError(ExitCode.INVALID_TARGET,
                       "at least one --project <KEY> is required",
                       hint="don't know your project keys? run "
                            "'omn-agent mcp init jira' for guided setup")

    server = {
        "kind": "jira",
        "baseUrl": base_url,
        "projects": projects,
        "auth": {"emailEnv": args.email_env, "tokenEnv": args.token_env},
    }

    if args.dry_run:
        report.info("M-PLAN", f"would record Jira connector: {base_url}, projects "
                    f"{', '.join(projects)} in {MCP_CONFIG_REL}")
        report.info("M-PLAN", f"would register 'jira' MCP server in "
                    f"{target / '.mcp.json'}")
        report.print()
        return ExitCode.DRY_RUN

    _write_jira_server(target, fw_dir, server, report, force=args.force)
    return report.finish()


# ---------------------------------------------------------------- mcp add msdev


def cmd_mcp_add_msdev(args) -> ExitCode:
    """Record the MSDev (Azure DevOps) connector: organization URL, project,
    and the name of the environment variable holding the PAT."""
    target = resolve_target(args.target)
    report = Report("mcp add msdev", str(target))
    fw_dir = _require_installed(target)

    org_url = normalize_base_url(
        args.org_url, what="Azure DevOps organization",
        example="https://dev.azure.com/yourorg")
    project = (args.project or "").strip()
    if not project:
        raise OmnError(ExitCode.INVALID_TARGET,
                       "--project <NAME> is required",
                       hint="the Azure DevOps project the work items live in")

    server = {
        "kind": "msdev",
        "baseUrl": org_url,
        "project": project,
        "auth": {"tokenEnv": args.token_env},
    }

    if args.dry_run:
        report.info("M-PLAN", f"would record MSDev connector: {org_url}, "
                    f"project {project} in {MCP_CONFIG_REL}")
        report.info("M-PLAN", f"would register 'msdev' MCP server in "
                    f"{target / '.mcp.json'}")
        report.print()
        return ExitCode.DRY_RUN

    org_name = org_url.rstrip("/").rsplit("/", 1)[-1]
    _write_server(
        target, fw_dir, "msdev", server, report, force=args.force,
        mcp_entry={"command": "npx",
                   "args": ["-y", MSDEV_MCP_PACKAGE, org_name]},
        cred_envs=[args.token_env],
        next_hint=f"export ${args.token_env} (a personal access token with "
                  "work-item read scope), then drive a ticket end to end "
                  "with 'omn-agent run MSDev <KEY-123> --gate-policy auto "
                  "--approve'")
    return report.finish()


# ------------------------------------------------------------------ mcp init


class _Cancelled(Exception):
    pass


def _make_asker(input_fn):
    def ask(prompt: str, default: str | None = None) -> str:
        suffix = f" [{default}]" if default else ""
        try:
            answer = input_fn(f"  {prompt}{suffix}: ").strip()
        except EOFError:
            raise _Cancelled()
        return answer or (default or "")
    return ask


def cmd_mcp_init_jira(args, transport=None, input_fn=None) -> ExitCode:
    """Guided Jira setup. Same result as `mcp add jira`, no flags required."""
    target = resolve_target(args.target)          # repo validated before anything
    report = Report("mcp init jira", str(target))
    fw_dir = _require_installed(target)

    if input_fn is None:
        if not sys.stdin.isatty():
            raise OmnError(ExitCode.INCOMPLETE,
                           "guided setup needs an interactive terminal",
                           hint="use the flag-based form instead: omn-agent mcp add "
                                "jira --base-url https://<site>.atlassian.net "
                                "--project <KEY>")
        input_fn = input
    ask = _make_asker(input_fn)

    existing = {}
    try:
        existing = ((load_mcp_config(fw_dir) or {}).get("servers", {})
                    .get("jira") or {})
    except OmnError:
        pass   # unreadable config: init exists to rewrite it
    auth = existing.get("auth", {})
    email_env = auth.get("emailEnv", DEFAULT_EMAIL_ENV)
    token_env = auth.get("tokenEnv", DEFAULT_TOKEN_ENV)

    print("Jira setup for " + str(target))
    print("  Answers are written to config only; credentials never leave your "
          "environment.")
    try:
        base_url = _ask_base_url(ask, args.base_url or existing.get("baseUrl"))
        client = JiraClient({"baseUrl": base_url,
                             "auth": {"emailEnv": email_env, "tokenEnv": token_env}},
                            transport=transport)
        detected = _detect_projects(client, email_env, token_env)
        projects = _ask_projects(ask, detected, existing.get("projects") or [])

        print()
        print("  Ready to write:")
        print(f"    site       {base_url}")
        print(f"    projects   {', '.join(projects)}")
        print(f"    secrets    read from ${email_env} / ${token_env} (never stored)")
        print(f"    files      .omn-agent/{MCP_CONFIG_REL} and .mcp.json (merged)")
        confirm = ask("Write configuration? (Y/n)", "y").lower()
        if confirm not in ("y", "yes"):
            raise _Cancelled()
    except _Cancelled:
        raise OmnError(ExitCode.APPROVAL_REQUIRED,
                       "setup cancelled; nothing was written")

    server = {
        "kind": "jira",
        "baseUrl": base_url,
        "projects": projects,
        "auth": {"emailEnv": email_env, "tokenEnv": token_env},
    }
    _write_jira_server(target, fw_dir, server, report,
                       force=bool(getattr(args, "force", False)))
    return report.finish()


def _ask_base_url(ask, default: str | None) -> str:
    while True:
        raw = ask("Jira site URL (e.g. yourteam.atlassian.net)", default)
        try:
            return normalize_base_url(raw)
        except OmnError as exc:
            print(f"  ! {exc.message}" + (f" -- {exc.hint}" if exc.hint else ""))
            default = None


def _detect_projects(client: JiraClient, email_env: str,
                     token_env: str) -> list[dict]:
    """Try to list the account's projects; degrade to manual entry, never fail."""
    if not client.credentials_present():
        print(f"  No credentials found in ${email_env} / ${token_env}, so project "
              "keys can't be auto-detected.")
        print(f"  (Create an API token at {ATLASSIAN_TOKEN_URL}, export both "
              "variables, and re-run to get auto-detection.)")
        return []
    try:
        me = client.myself()
        who = me.get("displayName") or me.get("emailAddress") or "your account"
        print(f"  Connected to Jira as {who}.")
        detected = client.list_projects()
    except OmnError as exc:
        print(f"  ! Could not auto-detect projects: {exc.message}")
        print("    Continuing with manual project entry.")
        return []
    if not detected:
        print("  Jira returned no visible projects; enter keys manually.")
    return detected


def _ask_projects(ask, detected: list[dict], current: list[str]) -> list[str]:
    default = ",".join(current) if current else None
    if detected:
        print(f"  Projects visible to your account "
              f"({min(len(detected), MAX_LISTED_PROJECTS)} of {len(detected)}):")
        for i, p in enumerate(detected[:MAX_LISTED_PROJECTS], 1):
            print(f"    {i:>3}. {p['key']:<12} {p['name']}")
        prompt = "Track which projects? (numbers or keys, comma-separated)"
    else:
        prompt = "Project key(s) to track (comma-separated, e.g. PROJ)"
    while True:
        raw = ask(prompt, default)
        keys = _resolve_selection(raw, detected)
        bad = [k for k in keys if not PROJECT_KEY_RE.match(k)]
        if bad:
            print(f"  ! not a valid Jira project key: {', '.join(bad)} "
                  "(keys are letters, digits, and underscores starting with "
                  "a letter, e.g. PROJ)")
            default = None
            continue
        if keys:
            unknown = [k for k in keys
                       if detected and k not in {p["key"] for p in detected}]
            for k in unknown:
                print(f"  ! {k} was not in the detected list; keeping it anyway "
                      "(it may be visible to a different account).")
            return keys
        print("  ! Enter at least one project (numbers from the list, or keys "
              "like PROJ).")
        default = None


def _resolve_selection(raw: str, detected: list[dict]) -> list[str]:
    keys: set[str] = set()
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        if part.isdigit() and detected:
            idx = int(part)
            if 1 <= idx <= min(len(detected), MAX_LISTED_PROJECTS):
                keys.add(detected[idx - 1]["key"])
            # an out-of-range number is simply not a selection
        else:
            keys.add(part.upper())
    return sorted(keys)


# ------------------------------------------------------------------ .mcp.json


def _merge_root_mcp_json(target: Path, report: Report, *, name: str,
                         entry: dict, force: bool):
    """Register one server in the repo's standard .mcp.json, merge-safe."""
    path = target / ".mcp.json"
    doc: dict = {}
    if path.exists():
        try:
            doc = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            report.warning("M-MCPJSON", f".mcp.json exists but is unreadable ({exc}); "
                           "leaving it untouched",
                           hint=f"fix the JSON, then re-run 'omn-agent mcp add {name}'")
            return
        if not isinstance(doc, dict):
            report.warning("M-MCPJSON", ".mcp.json is not a JSON object; leaving it "
                           "untouched")
            return
    servers = doc.setdefault("mcpServers", {})
    current = servers.get(name)
    if current == entry:
        report.info("M-MCPJSON", f".mcp.json already registers the '{name}' server")
        return
    if current is not None and not force:
        report.warning("M-MCPJSON", f".mcp.json already has a different '{name}' "
                       "server; preserved",
                       hint="re-run with --force to replace it")
        return
    servers[name] = entry
    atomic_write(path, (json.dumps(doc, indent=2) + "\n").encode("utf-8"))
    report.success("M-MCPJSON", f"registered '{name}' MCP server in {path.name}")
