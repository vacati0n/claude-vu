"""Tests for the multi-provider one-command flow: `omn-agent run <Provider>
<TicketKey>` (e.g. 'run Jira ON-115 --gate-policy auto --approve').

Covers provider resolution from config/mcp.json (case-insensitive names,
kind aliases, and the unknown-provider / missing-connector / ticket-not-found
error contract), the MSDev (Azure DevOps) client normalization, the full
fetch -> classify -> route -> materialize -> bind -> dispatch -> resume ->
gate-policy -> PR delivery cycle for both providers, and the legacy
single-argument `run` mode staying untouched.

Reuses the real-git fixture from test_branch_pr and the stateful runtime
stub from test_update; Jira and Azure DevOps are exercised only through fake
transports -- no network is touched.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from omn_agent import cli, providers, update
from omn_agent.common import ExitCode, OmnError
from omn_agent.jira_client import HttpResponse
from omn_agent.msdev_client import MsDevClient, work_item_id

from test_branch_pr import GitFixtureTestCase, git
from test_omn_agent import fake_transport, make_ticket
from test_update import STATEFUL_RUNTIME


def make_workitem(wid=115, wtype="User Story", title="Add login timeout",
                  state="New", tags="", changed="2026-08-19T10:00:00Z"):
    return {
        "id": wid,
        "fields": {
            "System.Title": title,
            "System.WorkItemType": wtype,
            "System.State": state,
            "Microsoft.VSTS.Common.Priority": 2,
            "System.AssignedTo": {"displayName": "Dev User"},
            "System.CreatedBy": {"displayName": "Sam"},
            "System.Tags": tags,
            "System.CreatedDate": "2026-08-18T09:00:00Z",
            "System.ChangedDate": changed,
            "System.Description": "<div>As a user I want to log in.</div>"
                                  "<p>Acceptance criteria:</p><li>works</li>",
        },
        "_links": {"html": {"href": "https://dev.azure.com/acme/Platform/"
                                    f"_workitems/edit/{wid}"}},
    }


def fake_msdev_transport(items):
    def transport(url, headers):
        assert "Authorization" in headers
        m = re.search(r"/_apis/wit/workitems/(\d+)", url)
        if m:
            wid = int(m.group(1))
            for it in items:
                if it["id"] == wid:
                    return HttpResponse(200, json.dumps(it).encode())
            return HttpResponse(404, b"{}")
        return HttpResponse(404, b"{}")
    return transport


class MsDevClientTestCase(unittest.TestCase):
    settings = {"kind": "msdev", "baseUrl": "https://dev.azure.com/acme",
                "project": "Platform", "auth": {"tokenEnv": "TEST_ADO_PAT"}}

    def setUp(self):
        os.environ["TEST_ADO_PAT"] = "pat"
        self.addCleanup(os.environ.pop, "TEST_ADO_PAT", None)

    def test_work_item_id_parses_prefixed_and_bare_keys(self):
        self.assertEqual(work_item_id("ONN-115"), 115)
        self.assertEqual(work_item_id("onn-7"), 7)
        self.assertEqual(work_item_id("115"), 115)
        with self.assertRaises(OmnError) as ctx:
            work_item_id("ONN-")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)

    def test_issue_normalizes_to_the_jira_ticket_shape(self):
        client = MsDevClient(self.settings,
                             transport=fake_msdev_transport([make_workitem(
                                 tags="auth; backend")]))
        t = client.issue("onn-115")
        self.assertEqual(t["key"], "ONN-115")
        self.assertEqual(t["id"], "115")
        self.assertEqual(t["type"], "User Story")
        self.assertEqual(t["status"], "New")
        self.assertEqual(t["priority"], "2")
        self.assertEqual(t["labels"], ["auth", "backend"])
        self.assertEqual(t["assignee"], "Dev User")
        self.assertEqual(t["reporter"], "Sam")
        self.assertIn("As a user I want to log in.", t["description"])
        self.assertNotIn("<div>", t["description"])
        self.assertIn("Acceptance criteria:", t["description"])
        self.assertIn("_workitems/edit/115", t["url"])
        self.assertEqual(t["updated"], "2026-08-19T10:00:00Z")

    def test_issue_not_found_is_invalid_target(self):
        client = MsDevClient(self.settings,
                             transport=fake_msdev_transport([]))
        with self.assertRaises(OmnError) as ctx:
            client.issue("ONN-404")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)
        self.assertIn("not found", ctx.exception.message)
        self.assertIn("ONN-404", ctx.exception.message)

    def test_missing_credentials_is_incomplete(self):
        os.environ.pop("TEST_ADO_PAT", None)
        client = MsDevClient(self.settings,
                             transport=fake_msdev_transport([]))
        with self.assertRaises(OmnError) as ctx:
            client.issue("ONN-115")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INCOMPLETE)
        self.assertIn("TEST_ADO_PAT", ctx.exception.message)

    def test_missing_base_url_is_incomplete(self):
        with self.assertRaises(OmnError) as ctx:
            MsDevClient({"kind": "msdev"})
        self.assertEqual(ctx.exception.exit_code, ExitCode.INCOMPLETE)


class ProviderResolutionTestCase(unittest.TestCase):
    def setUp(self):
        self.fw = Path(tempfile.mkdtemp(prefix="omn-agent-providers-"))
        self.addCleanup(shutil.rmtree, self.fw, ignore_errors=True)

    def write_config(self, servers: dict):
        path = self.fw / "config" / "mcp.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"schemaVersion": "1.0",
                                    "servers": servers}), encoding="utf-8")

    def test_no_connectors_configured(self):
        with self.assertRaises(OmnError) as ctx:
            providers.resolve_provider(self.fw, "Jira")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INCOMPLETE)
        self.assertIn("no MCP connectors", ctx.exception.message)

    def test_unknown_provider_lists_configured(self):
        self.write_config({"jira": {"kind": "jira", "baseUrl": "https://x.y",
                                    "auth": {}}})
        with self.assertRaises(OmnError) as ctx:
            providers.resolve_provider(self.fw, "GitLab")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)
        self.assertIn("unknown provider 'GitLab'", ctx.exception.message)
        self.assertIn("jira", ctx.exception.message)

    def test_name_match_is_case_insensitive(self):
        self.write_config({"jira": {"kind": "jira", "baseUrl": "https://x.y",
                                    "auth": {}}})
        p = providers.resolve_provider(self.fw, "Jira")
        self.assertEqual((p.name, p.kind), ("jira", "jira"))

    def test_kind_alias_finds_differently_named_connector(self):
        self.write_config({"ado-main": {"kind": "azure-devops",
                                        "baseUrl": "https://dev.azure.com/a",
                                        "project": "P", "auth": {}}})
        for spelling in ("MSDev", "msdev", "azure-devops", "ADO"):
            p = providers.resolve_provider(self.fw, spelling)
            self.assertEqual((p.name, p.kind), ("ado-main", "msdev"), spelling)

    def test_ambiguous_kind_requires_the_connector_name(self):
        base = {"kind": "msdev", "baseUrl": "https://dev.azure.com/a",
                "project": "P", "auth": {}}
        self.write_config({"ado-a": dict(base), "ado-b": dict(base)})
        with self.assertRaises(OmnError) as ctx:
            providers.resolve_provider(self.fw, "MSDev")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)
        self.assertIn("ambiguous", ctx.exception.message)
        p = providers.resolve_provider(self.fw, "ado-b")
        self.assertEqual(p.name, "ado-b")

    def test_missing_connector_for_configured_kind(self):
        self.write_config({"linear": {"kind": "linear",
                                      "baseUrl": "https://linear.app"}})
        with self.assertRaises(OmnError) as ctx:
            providers.resolve_provider(self.fw, "Linear")
        self.assertEqual(ctx.exception.exit_code, ExitCode.INCOMPLETE)
        self.assertIn("no connector", ctx.exception.message)
        self.assertIn("jira", ctx.exception.hint)
        self.assertIn("msdev", ctx.exception.hint)


class RunE2ETestCase(GitFixtureTestCase):
    """The one-command flow against the real-git fixture and the stateful
    runtime stub from test_update."""

    JIRA_TICKETS = [make_ticket(key="PROJ-1", itype="Story",
                                summary="Add login timeout")]

    def setup_providers(self, msdev_items=None):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        os.environ["JIRA_EMAIL"] = "dev@example.com"
        os.environ["JIRA_API_TOKEN"] = "token"
        os.environ["AZURE_DEVOPS_PAT"] = "pat"
        for var in ("JIRA_EMAIL", "JIRA_API_TOKEN", "AZURE_DEVOPS_PAT"):
            self.addCleanup(os.environ.pop, var, None)
        code, out = self.run_cli(
            "mcp", "add", "jira", "--target", str(self.repo),
            "--base-url", "https://x.atlassian.net", "--project", "PROJ")
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli(
            "mcp", "add", "msdev", "--target", str(self.repo),
            "--org-url", "https://dev.azure.com/acme", "--project", "Platform")
        self.assertEqual(code, ExitCode.OK, out)
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            STATEFUL_RUNTIME, encoding="utf-8")
        self.jira_transport = fake_transport(list(self.JIRA_TICKETS))
        self.msdev_transport = fake_msdev_transport(
            msdev_items if msdev_items is not None else [make_workitem()])

    def e2e(self, provider, key, *extra) -> tuple[int, str]:
        """Invoke the provider mode the way runner.cmd_run does, with the
        fake transport injected."""
        transport = (self.msdev_transport
                     if provider.lower() in ("msdev", "azure-devops", "ado")
                     else self.jira_transport)
        args = cli.build_parser().parse_args(
            ["run", provider, key, "--target", str(self.repo), *extra])
        args.provider, args.key = args.key, args.ticket
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            try:
                code = update.cmd_run_ticket(args, transport=transport)
            except OmnError as exc:
                print(exc.message, file=out)
                code = exc.exit_code
        return code, out.getvalue()

    def set_stage(self, stage: str):
        p = self.fw / "runs" / "stub-state.json"
        state = json.loads(p.read_text()) if p.exists() else {"log": []}
        state["stage"] = stage
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(state))

    def stub_log(self, cmd=None) -> list[dict]:
        p = self.fw / "runs" / "stub-state.json"
        log = (json.loads(p.read_text()) if p.exists() else {}).get("log", [])
        return [e for e in log if cmd is None or e["cmd"] == cmd]

    def record_pr(self, key: str):
        tfile = self.fw / "tasks" / key / "task-plan.json"
        task = json.loads(tfile.read_text())
        task["pr"] = {"url": "https://github.com/acme/repo/pull/7",
                      "base": "main", "head": task["branch"]["name"]}
        tfile.write_text(json.dumps(task))

    def commit_work(self, key: str):
        wt = self.wt(key)
        (wt / "change.py").write_text("TIMEOUT = 30\n", encoding="utf-8")
        git("add", "-A", cwd=wt)
        git("commit", "-m", "implement the ticket", cwd=wt)

    # ---- the one-command flow, Jira ----------------------------------------

    def test_jira_one_command_fetches_routes_binds_and_dispatches(self):
        self.setup_providers()
        code, out = self.e2e("Jira", "PROJ-1", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        # stage-by-stage progress: provider, fetched, routed, run, branch,
        # dispatched, paused at the host-subagent boundary
        for marker in ("E2E-PROVIDER", "U-TICKET", "P-PLAN", "U-RUN",
                       "B-CREATE", "U-DISPATCHED", "U-WAIT"):
            self.assertIn(marker, out)
        self.assertIn("fetched from Jira", out)
        task = self.task("PROJ-1")
        self.assertEqual(task["provider"], "jira")
        self.assertEqual(task["command"], "implement")
        self.assertEqual(task["runId"], "run-abcdef123456")
        self.assertEqual(task["branch"]["name"],
                         "feature/proj-1-add-login-timeout")
        self.assertTrue(self.wt("PROJ-1").is_dir())
        self.assertEqual(len(self.stub_log("dispatch")), 1)
        # the pause names the exact resume command
        self.assertIn("omn-agent run jira PROJ-1", out)

    def test_jira_rerun_resumes_and_delivers_the_pr(self):
        self.setup_providers()
        code, out = self.e2e("Jira", "PROJ-1", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.commit_work("PROJ-1")
        self.record_pr("PROJ-1")

        code, out = self.e2e("Jira", "PROJ-1", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        # resumed: no re-plan churn, the dispatched phase was completed
        self.assertIn("P-SAME", out)
        self.assertEqual(len(self.stub_log("plan")), 1)
        self.assertEqual(len(self.stub_log("complete")), 1)
        self.assertIn("U-DONE", out)
        self.assertIn("PR", out)
        branch = self.task("PROJ-1")["branch"]["name"]
        local = git("rev-parse", branch, cwd=self.repo).strip()
        remote = git("rev-parse", branch, cwd=self.origin).strip()
        self.assertEqual(local, remote)

    # ---- the one-command flow, MSDev ----------------------------------------

    def test_msdev_one_command_behaves_identically(self):
        self.setup_providers()
        code, out = self.e2e("MSDev", "ONN-115", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        for marker in ("E2E-PROVIDER", "U-TICKET", "P-PLAN", "U-RUN",
                       "B-CREATE", "U-DISPATCHED", "U-WAIT"):
            self.assertIn(marker, out)
        self.assertIn("Azure DevOps", out)
        task = self.task("ONN-115")
        self.assertEqual(task["provider"], "msdev")
        self.assertEqual(task["command"], "implement")
        self.assertTrue((self.fw / "tickets" / "inbox" / "ONN-115.json")
                        .exists())
        self.assertEqual(task["branch"]["name"],
                         "feature/onn-115-add-login-timeout")

        # resume to full delivery, exactly like Jira
        self.commit_work("ONN-115")
        self.record_pr("ONN-115")
        code, out = self.e2e("MSDev", "ONN-115", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("P-SAME", out)
        self.assertIn("U-DONE", out)
        branch = self.task("ONN-115")["branch"]["name"]
        self.assertEqual(git("rev-parse", branch, cwd=self.repo).strip(),
                         git("rev-parse", branch, cwd=self.origin).strip())

    def test_msdev_bug_routes_to_bugfix(self):
        self.setup_providers(msdev_items=[make_workitem(
            wid=115, wtype="Bug", title="Crash on login")])
        code, out = self.e2e("MSDev", "ONN-115", "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        task = self.task("ONN-115")
        self.assertEqual(task["command"], "bugfix")
        self.assertEqual(task["workflow"], "fix-bug")
        self.assertEqual(task["branch"]["name"],
                         "bugfix/onn-115-crash-on-login")

    # ---- gate policy: auto-decided vs held -----------------------------------

    def test_gate_policy_auto_reports_the_auto_decision(self):
        self.setup_providers()
        code, out = self.e2e("Jira", "PROJ-1", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.commit_work("PROJ-1")
        self.record_pr("PROJ-1")
        self.set_stage("completed")   # step done, gate blocked
        code, out = self.e2e("Jira", "PROJ-1", "--gate-policy", "auto",
                             "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("U-GATE-AUTO", out)
        self.assertIn("U-DONE", out)

    def test_held_gate_pauses_with_decision_instructions(self):
        self.setup_providers()
        code, out = self.e2e("Jira", "PROJ-1", "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.set_stage("completed")
        code, out = self.e2e("Jira", "PROJ-1", "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("U-GATE", out)
        self.assertIn("held", out)
        self.assertIn("--gate-policy auto", out)
        # nothing was pushed while the gate holds
        self.assertEqual([g for g in self.stub_log("gate")
                          if g.get("decision") == "approve"], [])

    # ---- error contract -------------------------------------------------------

    def test_unknown_provider_is_actionable(self):
        self.setup_providers()
        code, out = self.run_cli("run", "GitLab", "PROJ-1",
                                 "--target", str(self.repo), "--approve")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("unknown provider 'GitLab'", out)
        self.assertIn("jira", out)
        self.assertIn("msdev", out)

    def test_missing_connector_kind_is_actionable(self):
        self.setup_providers()
        cfg_path = self.fw / "config" / "mcp.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["servers"]["linear"] = {"kind": "linear",
                                    "baseUrl": "https://linear.app"}
        cfg_path.write_text(json.dumps(cfg))
        code, out = self.run_cli("run", "Linear", "ABC-1",
                                 "--target", str(self.repo), "--approve")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no connector", out)

    def test_ticket_not_found_is_actionable(self):
        self.setup_providers()
        code, out = self.e2e("Jira", "PROJ-404", "--approve")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("not found", out)
        code, out = self.e2e("MSDev", "ONN-404", "--approve")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("not found", out)

    def test_dry_run_previews_without_writing(self):
        self.setup_providers()
        code, out = self.e2e("Jira", "PROJ-1", "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertIn("would fetch PROJ-1 from Jira", out)
        self.assertFalse((self.fw / "tasks" / "PROJ-1").exists())
        self.assertFalse(
            (self.fw / "tickets" / "inbox" / "PROJ-1.json").exists())
        self.assertEqual(self.stub_log(), [])

    # ---- backward compatibility ------------------------------------------------

    def test_provider_mode_rejects_stepwise_flags(self):
        self.setup_providers()
        code, out = self.run_cli("run", "Jira", "PROJ-1", "--show",
                                 "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("--show", out)

    def test_legacy_mode_rejects_provider_flags(self):
        self.setup_providers()
        code, out = self.run_cli("run", "PROJ-1", "--draft",
                                 "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("provider mode", out)

    def test_legacy_single_argument_run_is_unchanged(self):
        key = self.plan_ticket()
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--show")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("no runtime run exists yet", out)
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(self.task(key)["runId"], "run-abcdef123456")


if __name__ == "__main__":
    unittest.main()
