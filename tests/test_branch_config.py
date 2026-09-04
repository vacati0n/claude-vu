"""Tests for per-project branch naming templates:

* pure-function unit tests (template validation, token rendering, slug
  sanitization, work-type routing, fallback defaults) -- no filesystem;
* CLI/integration tests (`omn-agent init` flags, `omn-agent branch-config
  show/set/preview`) using a lightweight fixture with a fake '.git' marker
  directory (same trick test_omn_agent.py uses) rather than a real git
  repository, since none of this needs actual git history -- only branch
  *name* validation shells out to 'git check-ref-format', which works from
  any directory. The one test that exercises 'omn-agent branch' end-to-end
  against a project-configured template lives in test_branch_pr.py, which
  already has a real-git fixture.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from omn_agent import branch_config, cli
from omn_agent import tickets as tickets_mod
from omn_agent.common import ExitCode

from test_omn_agent import SOURCE_FILES, fake_transport, make_ticket


class BranchConfigUnitTests(unittest.TestCase):
    """Pure functions: no filesystem, no CLI."""

    # ---- sanitization -------------------------------------------------------

    def test_sanitize_lowercases_and_replaces_special_chars(self):
        self.assertEqual(
            branch_config.sanitize_branch_name("Feature/PROJ 42: Add Login!!"),
            "feature/proj-42-add-login")

    def test_sanitize_collapses_duplicate_dashes(self):
        self.assertEqual(branch_config.sanitize_branch_name("a---b--c"), "a-b-c")

    def test_sanitize_trims_leading_and_trailing_dashes(self):
        self.assertEqual(branch_config.sanitize_branch_name("-a-b-"), "a-b")

    def test_sanitize_preserves_slash_hierarchy(self):
        self.assertEqual(
            branch_config.sanitize_branch_name("feature/sub/PROJ-1"),
            "feature/sub/proj-1")

    def test_sanitize_enforces_max_length(self):
        raw = "feature/" + "x" * 100
        out = branch_config.sanitize_branch_name(raw, max_length=20)
        self.assertLessEqual(len(out), 20)
        self.assertFalse(out.endswith("-"))
        branch_config.check_valid_git_branch_name(out)   # must not raise

    def test_sanitize_empty_input_yields_empty_string(self):
        self.assertEqual(branch_config.sanitize_branch_name("---"), "")

    # ---- token rendering ------------------------------------------------------

    def test_render_template_substitutes_known_tokens(self):
        out = branch_config.render_template(
            "{work_type}/{ticket_id}-{short_description}",
            ticket_id="PROJ-9", short_description="fix-it", work_type="bugfix")
        self.assertEqual(out, "bugfix/PROJ-9-fix-it")

    def test_render_template_rejects_unknown_token(self):
        with self.assertRaises(Exception):
            branch_config.render_template(
                "{author}/{ticket_id}", ticket_id="PROJ-9",
                short_description="x", work_type="feature")

    # ---- template validation ------------------------------------------------

    def test_validate_template_requires_ticket_id(self):
        with self.assertRaises(Exception) as ctx:
            branch_config.validate_template("feature", "feature/{short_description}")
        self.assertIn("ticket_id", str(ctx.exception))

    def test_validate_template_rejects_unknown_token(self):
        with self.assertRaises(Exception) as ctx:
            branch_config.validate_template("feature", "feature/{ticket_id}-{author}")
        self.assertIn("unknown token", str(ctx.exception))

    def test_validate_template_rejects_unbalanced_braces(self):
        with self.assertRaises(Exception) as ctx:
            branch_config.validate_template("feature", "feature/{ticket_id")
        self.assertIn("unbalanced", str(ctx.exception))

    def test_validate_template_rejects_empty(self):
        with self.assertRaises(Exception):
            branch_config.validate_template("feature", "")

    def test_validate_template_accepts_default_templates(self):
        for wt, tmpl in branch_config.DEFAULT_TEMPLATES.items():
            branch_config.validate_template(wt, tmpl)   # must not raise

    def test_validate_template_accepts_work_type_token(self):
        branch_config.validate_template(
            "chore", "{work_type}/{ticket_id}-{short_description}")

    # ---- routing / fallback defaults ------------------------------------------

    def test_work_type_routing_by_command(self):
        self.assertEqual(branch_config.work_type_for_command("implement"), "feature")
        self.assertEqual(branch_config.work_type_for_command("bugfix"), "bugfix")
        self.assertEqual(branch_config.work_type_for_command("refactor"), "refactor")
        self.assertEqual(branch_config.work_type_for_command("investigate"), "chore")

    def test_work_type_routing_unknown_command_falls_back_to_itself(self):
        self.assertEqual(branch_config.work_type_for_command("something-else"),
                         "something-else")

    def test_template_for_generic_fallback_for_unconfigured_work_type(self):
        self.assertEqual(branch_config.template_for({}, "docs"),
                         "docs/{ticket_id}-{short_description}")

    def test_template_for_project_override_wins_over_default(self):
        templates = {"feature": "custom/{ticket_id}"}
        self.assertEqual(branch_config.template_for(templates, "feature"),
                         "custom/{ticket_id}")

    def test_resolve_branch_name_uses_defaults_when_unconfigured(self):
        with tempfile.TemporaryDirectory() as d:
            fw = Path(d) / ".omn-agent"
            fw.mkdir()
            name, wt, tmpl = branch_config.resolve_branch_name(
                fw, command="implement", ticket_id="PROJ-1",
                short_description="add-login-timeout")
            self.assertEqual(name, "feature/proj-1-add-login-timeout")
            self.assertEqual(wt, "feature")
            self.assertEqual(tmpl, branch_config.DEFAULT_TEMPLATES["feature"])


class BranchConfigCliTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-agent-bctest-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "framework-src"
        for rel, content in SOURCE_FILES.items():
            p = self.source / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        self.repo = self.tmp / "repo"
        (self.repo / ".git").mkdir(parents=True)   # repo-root marker only
        self.fw = self.repo / ".omn-agent"

    def run_cli(self, *argv) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def init(self, *extra) -> tuple[int, str]:
        return self.run_cli("init", str(self.repo), *extra)

    def install(self) -> tuple[int, str]:
        return self.run_cli("install", str(self.repo), "--source", str(self.source))

    def plan_ticket(self, key="PROJ-1", summary="Add login timeout") -> str:
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        ticket = make_ticket(key=key, summary=summary)
        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(self.repo)])
        os.environ["JIRA_EMAIL"] = "dev@example.com"
        os.environ["JIRA_API_TOKEN"] = "token"
        self.addCleanup(os.environ.pop, "JIRA_EMAIL", None)
        self.addCleanup(os.environ.pop, "JIRA_API_TOKEN", None)
        self.run_cli("mcp", "add", "jira", "--target", str(self.repo),
                     "--base-url", "https://x.atlassian.net", "--project", "PROJ")
        out2 = io.StringIO()
        with contextlib.redirect_stdout(out2):
            tickets_mod.cmd_tickets_sync(args, transport=fake_transport([ticket]))
        code, out = self.run_cli("plan", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        return key

    def config(self) -> dict:
        return json.loads((self.fw / "config" / "branch-naming.json").read_text())

    # ---- init seeding -----------------------------------------------------

    def test_init_seeds_default_branch_config(self):
        code, out = self.init()
        self.assertEqual(code, ExitCode.OK, out)
        cfg = self.config()
        self.assertEqual(cfg["templates"]["feature"],
                         branch_config.DEFAULT_TEMPLATES["feature"])
        self.assertEqual(cfg["templates"]["bugfix"],
                         branch_config.DEFAULT_TEMPLATES["bugfix"])
        self.assertEqual(cfg["maxLength"], branch_config.DEFAULT_MAX_LENGTH)

    def test_init_accepts_template_flags(self):
        code, out = self.init(
            "--feature-branch-template", "feature/on-{ticket_id}-{short_description}",
            "--bugfix-branch-template", "bugfix/on-{ticket_id}-{short_description}",
            "--branch-max-length", "60")
        self.assertEqual(code, ExitCode.OK, out)
        cfg = self.config()
        self.assertEqual(cfg["templates"]["feature"],
                         "feature/on-{ticket_id}-{short_description}")
        self.assertEqual(cfg["templates"]["bugfix"],
                         "bugfix/on-{ticket_id}-{short_description}")
        self.assertEqual(cfg["maxLength"], 60)

    def test_init_rerun_does_not_overwrite_configured_templates(self):
        self.init("--feature-branch-template", "feature/on-{ticket_id}")
        code, out = self.init()
        self.assertEqual(code, ExitCode.OK, out)
        cfg = self.config()
        self.assertEqual(cfg["templates"]["feature"], "feature/on-{ticket_id}")

    def test_init_rejects_invalid_template_flag(self):
        code, out = self.init("--feature-branch-template",
                              "feature/{short_description}")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("ticket_id", out)
        self.assertFalse((self.fw / "config" / "branch-naming.json").exists())

    def test_init_dry_run_writes_nothing(self):
        code, out = self.init("--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertFalse(self.fw.exists())

    # ---- branch-config show/set/preview -----------------------------------

    def test_branch_config_show_reports_defaults_when_never_configured(self):
        # install-only path: 'init' (the only place that seeds the file) was
        # never run, so branch-naming.json genuinely does not exist.
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        self.assertFalse((self.fw / "config" / "branch-naming.json").exists())
        code, out = self.run_cli("branch-config", "show", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("default", out)
        self.assertIn(branch_config.DEFAULT_TEMPLATES["feature"], out)

    def test_branch_config_requires_initialized_framework(self):
        code, out = self.run_cli("branch-config", "show", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)

    def test_branch_config_set_updates_one_template_and_preserves_other(self):
        self.install()
        code, out = self.run_cli(
            "branch-config", "set", "--target", str(self.repo),
            "--feature-template", "feature/on-{ticket_id}-{short_description}")
        self.assertEqual(code, ExitCode.OK, out)
        cfg = self.config()
        self.assertEqual(cfg["templates"]["feature"],
                         "feature/on-{ticket_id}-{short_description}")
        self.assertEqual(cfg["templates"]["bugfix"],
                         branch_config.DEFAULT_TEMPLATES["bugfix"])

    def test_branch_config_set_supports_custom_work_type(self):
        self.install()
        code, out = self.run_cli(
            "branch-config", "set", "--target", str(self.repo),
            "--template", "chore=chore/{ticket_id}-{short_description}")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(self.config()["templates"]["chore"],
                         "chore/{ticket_id}-{short_description}")

    def test_branch_config_set_rejects_invalid_template(self):
        self.init()   # seeds the file with defaults first
        code, out = self.run_cli(
            "branch-config", "set", "--target", str(self.repo),
            "--feature-template", "feature/{ticket_id}-{author}")
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("unknown token", out)
        # unchanged: still the seeded default, not the rejected template
        self.assertEqual(self.config()["templates"]["feature"],
                         branch_config.DEFAULT_TEMPLATES["feature"])

    def test_branch_config_set_requires_at_least_one_option(self):
        self.install()
        code, out = self.run_cli("branch-config", "set", "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)
        self.assertIn("nothing to set", out)

    def test_branch_config_set_dry_run_writes_nothing(self):
        self.init()
        before = (self.fw / "config" / "branch-naming.json").read_text()
        code, out = self.run_cli(
            "branch-config", "set", "--target", str(self.repo),
            "--feature-template", "feature/on-{ticket_id}", "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertEqual((self.fw / "config" / "branch-naming.json").read_text(),
                         before)

    def test_branch_config_preview_resolves_ticket_branch_name(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch-config", "preview", key, "--target",
                                 str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("feature/proj-1-add-login-timeout", out)

    def test_branch_config_preview_honors_custom_template(self):
        key = self.plan_ticket()
        self.run_cli("branch-config", "set", "--target", str(self.repo),
                     "--feature-template", "feature/on-{ticket_id}-{short_description}")
        code, out = self.run_cli("branch-config", "preview", key, "--target",
                                 str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("feature/on-proj-1-add-login-timeout", out)

    def test_branch_config_preview_work_type_override(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch-config", "preview", key, "--target",
                                 str(self.repo), "--work-type", "bugfix")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("bugfix/proj-1-add-login-timeout", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
