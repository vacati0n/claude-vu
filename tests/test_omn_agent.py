"""End-to-end tests for the omn-agent CLI.

Runs against a small synthetic framework source and a synthetic target repo in
a temp directory, so tests are hermetic: no network, no dependence on the real
framework checkout. Jira calls go through an injected fake transport.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
import urllib.parse
from pathlib import Path

from omn_agent import cli
from omn_agent.common import ExitCode
from omn_agent.jira_client import HttpResponse
from omn_agent import tickets as tickets_mod

RUNTIME_STUB = '''\
"""Minimal framework runtime stand-in for installer tests."""
import sys


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else ""
    if cmd == "plan":
        print("Run run-abcdef123456  (implement-feature v1)  run_status=active")
        return 0
    if cmd == "next":
        print("NEXT: dispatch phase scope-and-acceptance to omn-product-owner")
        return 0
    print(f"ok {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''

SOURCE_FILES = {
    "runtime/framework_runtime.py": RUNTIME_STUB,
    "runtime/state_engine.py": "STATES = ['pending', 'done']\n",
    "runtime/scope_definition_validator.py": "def validate(text):\n    return []\n",
    "registry/agents.yaml": "apiVersion: framework.registry/v1\nrecords: []\n",
    "registry/workflows.yaml": "apiVersion: framework.registry/v1\nrecords: []\n",
    "registry/skills.yaml": "apiVersion: framework.registry/v1\nrecords: []\n",
    "registry/templates.yaml": "apiVersion: framework.registry/v1\nrecords: []\n",
    "registry/commands.yaml": "apiVersion: framework.registry/v1\nrecords: []\n",
    "config/runtime.md": "# runtime config\n",
    "templates/scope-definition.md": "# scope definition\n",
    "agents/capability-matrix.md": "# capability matrix\n",
    "workflows/implement-feature.md": "# implement-feature\n",
    "skills/agent-skill-matrix.md": "# skill matrix\n",
    "commands/implement.md": "# /implement\n",
    "domain-model/agent-specification.md": "# agent spec\n",
    "validation/framework-validation-checklist.md": "# checklist\n",
    "context/product-context.md": "# product context\n",
    "context/technical-context.md": "# technical context\n",
    "context/release-context.md": "# release context\n",
    "memory/architecture.md": "# architecture memory\n",
}


def make_ticket(key="PROJ-1", itype="Story", summary="Add login", updated="2026-08-19T10:00:00.000+0000"):
    return {
        "key": key, "id": "10001",
        "fields": {
            "summary": summary,
            "issuetype": {"name": itype},
            "status": {"name": "To Do"},
            "priority": {"name": "High"},
            "assignee": None,
            "reporter": {"displayName": "Sam"},
            "labels": [],
            "created": "2026-08-18T09:00:00.000+0000",
            "updated": updated,
            "description": "As a user I want to log in.\n\nAcceptance criteria:\n- works",
        },
    }


def fake_transport(issues, projects=()):
    def transport(url, headers):
        assert "Authorization" in headers
        if "/rest/api/2/issue/" in url:
            key = url.split("/rest/api/2/issue/")[1].split("?")[0]
            for i in issues:
                if i["key"] == key:
                    return HttpResponse(200, json.dumps(i).encode())
            return HttpResponse(404, b"{}")
        if "/rest/api/2/search/jql" in url:
            return HttpResponse(200, json.dumps(
                {"issues": issues, "isLast": True}).encode())
        if "/rest/api/2/myself" in url:
            return HttpResponse(200, json.dumps(
                {"displayName": "Dev User", "emailAddress": "dev@example.com"}
            ).encode())
        if "/rest/api/2/project/search" in url:
            return HttpResponse(200, json.dumps(
                {"values": list(projects), "isLast": True,
                 "total": len(projects)}).encode())
        return HttpResponse(404, b"{}")
    return transport


def scripted(*answers):
    """Deterministic stand-in for input(): yields answers, then EOF."""
    it = iter(answers)

    def input_fn(prompt):
        try:
            return next(it)
        except StopIteration:
            raise EOFError
    return input_fn


class OmnAgentTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-agent-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "framework-src"
        for rel, content in SOURCE_FILES.items():
            p = self.source / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        self.repo = self.tmp / "repo"
        (self.repo / ".git").mkdir(parents=True)
        self.fw = self.repo / ".omn-agent"

    # ---- helpers ---------------------------------------------------------

    def run_cli(self, *argv) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def install(self, *extra) -> tuple[int, str]:
        return self.run_cli("install", str(self.repo), "--source",
                            str(self.source), *extra)

    def install_and_sync_ticket(self, ticket=None):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        issues = [ticket or make_ticket()]
        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(self.repo)])
        os.environ["JIRA_EMAIL"] = "dev@example.com"
        os.environ["JIRA_API_TOKEN"] = "token"
        self.addCleanup(os.environ.pop, "JIRA_EMAIL", None)
        self.addCleanup(os.environ.pop, "JIRA_API_TOKEN", None)
        self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                     "--base-url", "https://x.atlassian.net", "--project", "PROJ")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = tickets_mod.cmd_tickets_sync(args, transport=fake_transport(issues))
        return code, out.getvalue()

    # ---- install lifecycle -------------------------------------------------

    def test_fresh_install_succeeds_and_validates(self):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("RESULT: SUCCESS", out)
        for d in ("bootstrap", "runtime", "registry", "config", "templates",
                  "agents", "workflows", "reports", "runs", "tickets", "tasks",
                  "context", "memory"):
            self.assertTrue((self.fw / d).is_dir(), d)
        manifest = json.loads(
            (self.fw / "bootstrap" / "install-manifest.json").read_text())
        self.assertTrue(manifest["installedAt"])
        self.assertIn("runtime/framework_runtime.py", manifest["files"])
        self.assertIn("context/product-context.md", manifest["seeds"])
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)

    def test_reinstall_is_idempotent_noop(self):
        self.install()
        before = {p: p.stat().st_mtime_ns
                  for p in self.fw.rglob("*") if p.is_file()
                  and "install-manifest" not in p.name}
        code, out = self.run_cli("install", str(self.repo), "--source",
                                 str(self.source))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("0 create" if "0 create" in out else "unchanged", out)
        self.assertNotIn(" create:", out)
        after = {p: p.stat().st_mtime_ns
                 for p in self.fw.rglob("*") if p.is_file()
                 and "install-manifest" not in p.name}
        self.assertEqual(before, after)

    def test_partial_install_is_repaired(self):
        self.install()
        (self.fw / "registry" / "agents.yaml").unlink()
        (self.fw / "runtime" / "state_engine.py").unlink()
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        self.assertTrue((self.fw / "registry" / "agents.yaml").is_file())
        code, _ = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.OK)

    def test_dry_run_writes_nothing_and_exits_5(self):
        code, out = self.install("--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertFalse(self.fw.exists())

    def test_invalid_targets(self):
        code, _ = self.run_cli("install", str(self.tmp / "nope"),
                               "--source", str(self.source))
        self.assertEqual(code, ExitCode.INVALID_TARGET)
        plain = self.tmp / "plain-dir"
        plain.mkdir()
        code, out = self.run_cli("install", str(plain), "--source", str(self.source))
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("INVALID TARGET", out)
        f = self.tmp / "afile"
        f.write_text("x")
        code, _ = self.run_cli("validate", str(f))
        self.assertEqual(code, ExitCode.INVALID_TARGET)

    def test_init_is_idempotent_and_enables_install(self):
        plain = self.tmp / "fresh"
        plain.mkdir()
        code, out = self.run_cli("init", str(plain))
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("init", str(plain))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("nothing to do", out)
        code, out = self.run_cli("validate", str(plain))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        code, out = self.run_cli("install", str(plain), "--source", str(self.source))
        self.assertEqual(code, ExitCode.OK, out)

    def test_validation_failure_on_corrupt_entrypoint(self):
        self.install()
        (self.fw / "runtime" / "framework_runtime.py").write_text(
            "def broken(:\n", encoding="utf-8")
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("does not compile", out)

    # ---- runtime dependency detection (V-IMPORT) ---------------------------

    def test_validate_and_doctor_report_missing_toplevel_import(self):
        # An installed runtime file whose module-top-level import cannot be
        # resolved must produce an ERROR finding naming the module, in both
        # validate and doctor, instead of certifying a dead runtime.
        (self.source / "runtime" / "framework_runtime.py").write_text(
            "import omn_absent_dep_xyz\n" + RUNTIME_STUB, encoding="utf-8")
        self.install()
        for cmd in ("validate", "doctor"):
            code, out = self.run_cli(cmd, str(self.repo))
            self.assertEqual(code, ExitCode.VALIDATION_FAILED, f"{cmd}: {out}")
            self.assertIn("V-IMPORT", out, cmd)
            self.assertIn("omn_absent_dep_xyz", out, cmd)

    def test_import_check_resolves_sibling_payload_modules(self):
        # Payload files import siblings (e.g. a validator importing
        # artifact_lib) at module top level, resolved at execution time by
        # the payload's own sys.path insertion. The check must not
        # false-positive on them.
        (self.source / "runtime" / "artifact_lib.py").write_text(
            "VALUE = 1\n", encoding="utf-8")
        (self.source / "runtime" / "scope_definition_validator.py").write_text(
            "import artifact_lib\n\n\ndef validate(text):\n    return []\n",
            encoding="utf-8")
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertNotIn("V-IMPORT", out)

    def test_import_check_ignores_non_toplevel_imports(self):
        # Detection is bounded to module-top-level imports: function-local,
        # conditional, and relative imports produce no finding.
        (self.source / "runtime" / "scope_definition_validator.py").write_text(
            "from . import omn_absent_rel_xyz\n"
            "\n"
            "def validate(text):\n"
            "    import omn_absent_local_xyz\n"
            "    return []\n"
            "\n"
            "if False:\n"
            "    import omn_absent_conditional_xyz\n",
            encoding="utf-8")
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertNotIn("V-IMPORT", out)

    def test_import_finding_hint_names_known_distribution(self):
        from omn_agent import validator
        self.assertIn("pyyaml", validator._import_hint("yaml"))
        self.assertIn("omn_absent_other",
                      validator._import_hint("omn_absent_other"))

    def test_incompatible_states_exit_4_without_changes(self):
        (self.repo / ".omn-agent").write_text("not a directory")
        code, out = self.install()
        self.assertEqual(code, ExitCode.INCOMPATIBLE, out)
        (self.repo / ".omn-agent").unlink()

        self.install()
        mpath = self.fw / "bootstrap" / "install-manifest.json"
        mpath.write_text("{corrupt", encoding="utf-8")
        code, out = self.install()
        self.assertEqual(code, ExitCode.INCOMPATIBLE, out)
        self.assertEqual(mpath.read_text(encoding="utf-8"), "{corrupt")

        mpath.write_text(json.dumps({"schemaVersion": 99, "files": {}}))
        code, out = self.install()
        self.assertEqual(code, ExitCode.INCOMPATIBLE, out)

    def test_foreign_omn_dir_without_manifest_is_incompatible(self):
        self.fw.mkdir()
        (self.fw / "somebody-elses.txt").write_text("hi")
        code, out = self.install()
        self.assertEqual(code, ExitCode.INCOMPATIBLE, out)
        self.assertTrue((self.fw / "somebody-elses.txt").exists())

    # ---- overwrite safety ----------------------------------------------------

    def test_user_modified_file_is_preserved_on_upgrade(self):
        self.install()
        tpl = self.fw / "templates" / "scope-definition.md"
        tpl.write_text("# my customized template\n", encoding="utf-8")
        (self.source / "templates" / "scope-definition.md").write_text(
            "# scope definition v2\n", encoding="utf-8")
        code, out = self.run_cli("upgrade", str(self.repo), "--source",
                                 str(self.source))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("skip (modified by user)", out)
        self.assertEqual(tpl.read_text(encoding="utf-8"), "# my customized template\n")

    def test_upgrade_updates_unmodified_managed_files(self):
        self.install()
        (self.source / "templates" / "scope-definition.md").write_text(
            "# scope definition v2\n", encoding="utf-8")
        code, out = self.run_cli("upgrade", str(self.repo), "--source",
                                 str(self.source))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual((self.fw / "templates" / "scope-definition.md")
                         .read_text(encoding="utf-8"), "# scope definition v2\n")

    def test_force_overwrites_with_backup(self):
        self.install()
        tpl = self.fw / "templates" / "scope-definition.md"
        tpl.write_text("# customized\n", encoding="utf-8")
        (self.source / "templates" / "scope-definition.md").write_text(
            "# v2\n", encoding="utf-8")
        code, out = self.run_cli("upgrade", str(self.repo), "--source",
                                 str(self.source), "--force")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(tpl.read_text(encoding="utf-8"), "# v2\n")
        self.assertEqual((tpl.parent / (tpl.name + ".omn-bak"))
                         .read_text(encoding="utf-8"), "# customized\n")

    def test_unknown_files_never_touched(self):
        self.install()
        mine = self.fw / "templates" / "my-own-notes.md"
        mine.write_text("mine\n", encoding="utf-8")
        code, out = self.run_cli("upgrade", str(self.repo), "--source",
                                 str(self.source))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(mine.read_text(encoding="utf-8"), "mine\n")
        code, out = self.run_cli("doctor", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("my-own-notes.md", out)

    def test_upgrade_requires_completed_install(self):
        code, out = self.run_cli("upgrade", str(self.repo), "--source",
                                 str(self.source))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)

    def test_seeds_created_once_then_owned_by_project(self):
        self.install()
        ctx = self.fw / "context" / "product-context.md"
        ctx.write_text("# our product\n", encoding="utf-8")
        (self.source / "context" / "product-context.md").write_text(
            "# new default\n", encoding="utf-8")
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(ctx.read_text(encoding="utf-8"), "# our product\n")

    # ---- status / doctor ------------------------------------------------------

    def test_status_reports_lifecycle(self):
        code, out = self.run_cli("status", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.install()
        code, out = self.run_cli("status", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("installed", out)
        self.assertIn("validation passes", out)

    # ---- mcp / tickets / plan / run ------------------------------------------

    def test_mcp_add_jira_writes_configs_merge_safe(self):
        self.install()
        mcp_root = self.repo / ".mcp.json"
        mcp_root.write_text(json.dumps(
            {"mcpServers": {"other": {"command": "x"}}}), encoding="utf-8")
        code, out = self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                                 "--base-url", "https://x.atlassian.net",
                                 "--project", "PROJ")
        self.assertEqual(code, ExitCode.OK, out)
        cfg = json.loads((self.fw / "config" / "mcp.json").read_text())
        self.assertEqual(cfg["servers"]["jira"]["projects"], ["PROJ"])
        # only environment-variable *names* are stored, never credential values
        self.assertEqual(cfg["servers"]["jira"]["auth"],
                         {"emailEnv": "JIRA_EMAIL", "tokenEnv": "JIRA_API_TOKEN"})
        doc = json.loads(mcp_root.read_text())
        self.assertIn("other", doc["mcpServers"])
        self.assertIn("jira", doc["mcpServers"])
        # rerun -> no-op, still OK
        code, out = self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                                 "--base-url", "https://x.atlassian.net",
                                 "--project", "PROJ")
        self.assertEqual(code, ExitCode.OK, out)
        # conflicting jira entry is preserved without --force
        doc["mcpServers"]["jira"] = {"command": "custom"}
        mcp_root.write_text(json.dumps(doc), encoding="utf-8")
        code, out = self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                                 "--base-url", "https://x.atlassian.net",
                                 "--project", "PROJ")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("preserved", out)
        self.assertEqual(json.loads(mcp_root.read_text())["mcpServers"]["jira"],
                         {"command": "custom"})

    def _init_jira(self, inputs, projects=(), with_creds=True):
        """Run the guided flow with scripted answers; returns (code, output)."""
        from omn_agent import mcp as mcp_mod
        if with_creds:
            os.environ["JIRA_EMAIL"] = "dev@example.com"
            os.environ["JIRA_API_TOKEN"] = "secret"
            self.addCleanup(os.environ.pop, "JIRA_EMAIL", None)
            self.addCleanup(os.environ.pop, "JIRA_API_TOKEN", None)
        else:
            os.environ.pop("JIRA_EMAIL", None)
            os.environ.pop("JIRA_API_TOKEN", None)
        args = cli.build_parser().parse_args(
            ["mcp", "init", "jira", "--target", str(self.repo)])
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                code = mcp_mod.cmd_mcp_init_jira(
                    args, transport=fake_transport([], projects),
                    input_fn=scripted(*inputs))
        except Exception as exc:                       # OmnError path
            from omn_agent.common import OmnError
            self.assertIsInstance(exc, OmnError)
            return exc.exit_code, out.getvalue() + exc.message
        return code, out.getvalue()

    def test_mcp_init_jira_autodetects_projects(self):
        self.install()
        projects = [{"key": "PROJ", "name": "Main Product"},
                    {"key": "OPS", "name": "Operations"}]
        # scheme-less URL, pick project 1 by number, confirm with default (enter)
        code, out = self._init_jira(["x.atlassian.net", "1", ""], projects)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("Connected to Jira as Dev User", out)
        self.assertIn("Main Product", out)
        cfg = json.loads((self.fw / "config" / "mcp.json").read_text())
        self.assertEqual(cfg["servers"]["jira"]["baseUrl"],
                         "https://x.atlassian.net")
        self.assertEqual(cfg["servers"]["jira"]["projects"], ["PROJ"])
        self.assertNotIn("secret", (self.fw / "config" / "mcp.json").read_text())
        self.assertTrue((self.repo / ".mcp.json").exists())

    def test_mcp_init_jira_manual_entry_without_credentials(self):
        self.install()
        code, out = self._init_jira(
            ["https://x.atlassian.net", "proj, ops", "y"], with_creds=False)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("can't be auto-detected", out)
        cfg = json.loads((self.fw / "config" / "mcp.json").read_text())
        self.assertEqual(cfg["servers"]["jira"]["projects"], ["OPS", "PROJ"])

    def test_mcp_init_jira_retries_bad_url_and_empty_projects(self):
        self.install()
        code, out = self._init_jira(
            ["not a url", "x.atlassian.net", "", "PROJ", "y"], with_creds=False)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("does not look like a Jira site URL", out)
        cfg = json.loads((self.fw / "config" / "mcp.json").read_text())
        self.assertEqual(cfg["servers"]["jira"]["projects"], ["PROJ"])

    def test_mcp_init_jira_cancel_writes_nothing(self):
        self.install()
        code, out = self._init_jira(["x.atlassian.net", "PROJ", "n"],
                                    with_creds=False)
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        self.assertFalse((self.fw / "config" / "mcp.json").exists())
        self.assertFalse((self.repo / ".mcp.json").exists())

    def test_mcp_init_jira_rerun_prefills_existing_config(self):
        self.install()
        self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                     "--base-url", "https://x.atlassian.net", "--project", "PROJ")
        # accept every default: URL, projects, confirm
        code, out = self._init_jira(["", "", ""], with_creds=False)
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("already up to date", out)
        cfg = json.loads((self.fw / "config" / "mcp.json").read_text())
        self.assertEqual(cfg["servers"]["jira"]["projects"], ["PROJ"])

    def test_mcp_init_jira_requires_terminal(self):
        import sys
        from unittest import mock
        self.install()
        with mock.patch.object(sys.stdin, "isatty", return_value=False):
            code, out = self.run_cli("mcp", "init", "jira", "--target",
                                     str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("mcp add jira", out)

    def test_mcp_add_jira_accepts_schemeless_url(self):
        self.install()
        code, out = self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                                 "--base-url", "x.atlassian.net",
                                 "--project", "PROJ")
        self.assertEqual(code, ExitCode.OK, out)
        cfg = json.loads((self.fw / "config" / "mcp.json").read_text())
        self.assertEqual(cfg["servers"]["jira"]["baseUrl"],
                         "https://x.atlassian.net")

    def test_tickets_sync_is_idempotent(self):
        code, out = self.install_and_sync_ticket()
        self.assertEqual(code, ExitCode.OK, out)
        inbox = self.fw / "tickets" / "inbox" / "PROJ-1.json"
        self.assertTrue(inbox.exists())
        self.assertIn("1 new", out)
        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(self.repo)])
        out2 = io.StringIO()
        with contextlib.redirect_stdout(out2):
            code = tickets_mod.cmd_tickets_sync(
                args, transport=fake_transport([make_ticket()]))
        self.assertEqual(code, ExitCode.OK)
        self.assertIn("1 unchanged", out2.getvalue())

    def test_mcp_add_rejects_impossible_project_keys(self):
        # A key like 'KEY=PROJ' can never exist in Jira; unrejected it used
        # to surface later as a JQL syntax error (HTTP 400) during sync.
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                                 "--base-url", "https://x.atlassian.net",
                                 "--project", "key=PROJ")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("not a valid Jira project key", out)
        self.assertFalse((self.fw / "config" / "mcp.json").exists())

    def test_tickets_sync_quotes_project_keys_in_jql(self):
        # A bare project key that is a JQL reserved word (e.g. ON) makes
        # real Jira reject the query with 400; keys must always be quoted.
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        os.environ["JIRA_EMAIL"] = "dev@example.com"
        os.environ["JIRA_API_TOKEN"] = "token"
        self.addCleanup(os.environ.pop, "JIRA_EMAIL", None)
        self.addCleanup(os.environ.pop, "JIRA_API_TOKEN", None)
        self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                     "--base-url", "https://x.atlassian.net",
                     "--project", "ON", "--project", "PROJ")
        seen_jql = []

        def transport(url, headers):
            if "/rest/api/2/search/jql" in url:
                query = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                seen_jql.append(query["jql"][0])
                return HttpResponse(200, json.dumps(
                    {"issues": [], "isLast": True}).encode())
            return HttpResponse(404, b"{}")

        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(self.repo)])
        out2 = io.StringIO()
        with contextlib.redirect_stdout(out2):
            code = tickets_mod.cmd_tickets_sync(args, transport=transport)
        self.assertEqual(code, ExitCode.OK, out2.getvalue())
        self.assertEqual(len(seen_jql), 1)
        self.assertIn('project in ("ON", "PROJ")', seen_jql[0])

    def test_tickets_require_configuration(self):
        self.install()
        code, out = self.run_cli("tickets", "sync", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("mcp add jira", out)

    def test_plan_routes_bug_to_bugfix_and_is_idempotent(self):
        code, out = self.install_and_sync_ticket(
            make_ticket(key="PROJ-9", itype="Bug", summary="Crash on save"))
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("plan", "PROJ-9", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        task = json.loads(
            (self.fw / "tasks" / "PROJ-9" / "task-plan.json").read_text())
        self.assertEqual(task["command"], "bugfix")
        self.assertEqual(task["workflow"], "fix-bug")
        self.assertEqual(task["inputType"], "defect-report")
        self.assertTrue((self.fw / "tasks" / "PROJ-9" / "input.md").exists())
        code, out = self.run_cli("plan", "PROJ-9", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("already up to date", out)

    def test_plan_dry_run(self):
        self.install_and_sync_ticket()
        code, out = self.run_cli("plan", "PROJ-1", "--target", str(self.repo),
                                 "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertFalse((self.fw / "tasks" / "PROJ-1").exists())

    def test_run_requires_approval(self):
        self.install_and_sync_ticket()
        self.run_cli("plan", "PROJ-1", "--target", str(self.repo))
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.APPROVAL_REQUIRED, out)
        task = json.loads(
            (self.fw / "tasks" / "PROJ-1" / "task-plan.json").read_text())
        self.assertIsNone(task["runId"])

    def test_run_with_approval_materializes_run_and_records_it(self):
        self.install_and_sync_ticket()
        self.run_cli("plan", "PROJ-1", "--target", str(self.repo))
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo),
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        task = json.loads(
            (self.fw / "tasks" / "PROJ-1" / "task-plan.json").read_text())
        self.assertEqual(task["runId"], "run-abcdef123456")
        approvals = (self.fw / "tasks" / "PROJ-1" / "approvals.jsonl") \
            .read_text().strip().splitlines()
        self.assertEqual(len(approvals), 1)
        self.assertIn("materialize", json.loads(approvals[0])["step"])
        # second call is read-only (next) -- no new approval needed
        code, out = self.run_cli("run", "PROJ-1", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("NEXT:", out)

    # ---- uniform --target/-t across subcommands -----------------------------

    def test_target_flag_accepted_by_positional_style_subcommands(self):
        # doctor/validate/status/init historically took the target positionally
        # and rejected -t with an argparse error; now both forms work.
        self.install()
        for sub in ("doctor", "validate", "status"):
            for form in (["-t", str(self.repo)],
                         ["--target", str(self.repo)],
                         [str(self.repo)]):
                code, out = self.run_cli(sub, *form)
                self.assertEqual(code, ExitCode.OK, f"{sub} {form}: {out}")

    def test_init_accepts_target_flag(self):
        repo2 = self.tmp / "repo2"
        (repo2 / ".git").mkdir(parents=True)
        code, out = self.run_cli("init", "-t", str(repo2))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertTrue((repo2 / ".omn-agent").is_dir())

    def test_target_flag_wins_over_positional(self):
        self.install()
        bogus = self.tmp / "does-not-exist"
        # Flag names the real repo; positional names a bogus path. Flag wins.
        code, out = self.run_cli("doctor", str(bogus), "-t", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)

    def test_flag_style_subcommands_unchanged(self):
        self.install()
        code, out = self.run_cli("branch-config", "show", "-t", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)


class BundledPayloadInstallTestCase(unittest.TestCase):
    """A wheel-style install -- no --source flag and no framework tree next to
    the package -- resolves the payload bundled inside the package (CKA-02).
    The existing explicit-source tests above keep proving the first candidate;
    these prove the appended last candidate at the CLI level. A plain TestCase
    (not OmnAgentTestCase) so the inherited tests are not re-run.
    """

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-agent-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "framework-src"
        for rel, content in SOURCE_FILES.items():
            p = self.source / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        self.repo = self.tmp / "repo"
        (self.repo / ".git").mkdir(parents=True)

    def run_cli(self, *argv) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def _fake_installed_package(self) -> Path:
        from omn_agent.source import BUNDLED_PAYLOAD_DIR
        pkg = self.tmp / "site-packages" / "omn_agent"
        bundle = pkg / BUNDLED_PAYLOAD_DIR
        for rel, content in SOURCE_FILES.items():
            p = bundle / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        return pkg

    def _patched_package_location(self, pkg: Path):
        from unittest import mock
        from omn_agent import source as source_mod
        return mock.patch.object(source_mod, "__file__", str(pkg / "source.py"))

    def test_install_without_source_resolves_bundled_payload(self):
        pkg = self._fake_installed_package()
        with self._patched_package_location(pkg):
            code, out = self.run_cli("install", str(self.repo))
            self.assertEqual(code, ExitCode.OK, out)
            self.assertIn("RESULT: SUCCESS", out)
            code, out = self.run_cli("validate", str(self.repo))
            self.assertEqual(code, ExitCode.OK, out)

    def test_dry_run_plans_identically_from_bundle_and_explicit_source(self):
        pkg = self._fake_installed_package()
        code, out_explicit = self.run_cli("install", str(self.repo),
                                          "--source", str(self.source),
                                          "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out_explicit)
        with self._patched_package_location(pkg):
            code, out_bundle = self.run_cli("install", str(self.repo), "--dry-run")
            self.assertEqual(code, ExitCode.DRY_RUN, out_bundle)

        def planned(out: str) -> list[str]:
            return sorted(line.split("would ", 1)[1]
                          for line in out.splitlines() if "would " in line)

        self.assertEqual(planned(out_bundle), planned(out_explicit))
        self.assertGreater(len(planned(out_bundle)), 0)


class DependencyDeclarationTestCase(unittest.TestCase):
    """The install contract and the documented dependency footprint agree.

    The installed framework runtime files import PyYAML at module top level,
    so the distribution must declare it and the docs must not claim the tool
    is standard-library only outright (the CLI package itself is; the
    installed runtime is not).
    """

    REPO = Path(__file__).resolve().parent.parent

    def test_pyproject_declares_pyyaml(self):
        text = (self.REPO / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"pyyaml>=6"', text)

    def test_readme_states_true_dependency_footprint(self):
        text = (self.REPO / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("Python 3.10+, standard library only", text)
        self.assertIn("pyyaml", text.lower())

    def test_user_guide_states_true_dependency_footprint(self):
        text = (self.REPO / "docs" / "user-guide.html").read_text(
            encoding="utf-8")
        self.assertIn("pyyaml", text.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
