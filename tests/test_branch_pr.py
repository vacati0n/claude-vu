"""Tests for the branch/PR lifecycle: `omn-agent branch` (per-task isolated
worktrees), `omn-agent pr ...`, and the implementation-phase worktree guard
in `omn-agent run`.

Uses a real git repository (git init + an initial commit on main, pushed to a
local bare "origin") so worktree creation, base-branch resolution, and pushing
exercise actual git behavior -- still fully hermetic, since the remote is just
another directory on disk, never a network call. PR creation itself is
exercised only through the missing/unauthenticated 'gh' fallback paths so no
real GitHub call is ever made.
"""

from __future__ import annotations

import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from omn_agent import cli, git_ops
from omn_agent import tickets as tickets_mod
from omn_agent.common import ExitCode

from test_omn_agent import SOURCE_FILES, fake_transport, make_ticket


def git(*args, cwd):
    proc = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True,
                          text=True)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


class GitFixtureTestCase(unittest.TestCase):
    """Reusable real-git fixture: framework source, target repo with a local
    bare origin, and helpers to install, sync/plan tickets, and inspect
    tasks. Holds no tests itself -- concrete suites (branch/PR here,
    fix-comments in test_fix_comments) subclass it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-agent-gittest-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

        self.source = self.tmp / "framework-src"
        for rel, content in SOURCE_FILES.items():
            p = self.source / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")

        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git("init", "-b", "main", cwd=self.repo)
        git("config", "user.email", "test@example.com", cwd=self.repo)
        git("config", "user.name", "Test", cwd=self.repo)
        (self.repo / "README.md").write_text("hello\n", encoding="utf-8")
        git("add", "-A", cwd=self.repo)
        git("commit", "-m", "initial", cwd=self.repo)

        # A local bare "origin" so fetch/push are real but hermetic.
        self.origin = self.tmp / "origin.git"
        subprocess.run(["git", "init", "--bare", str(self.origin)], check=True)
        git("remote", "add", "origin", str(self.origin), cwd=self.repo)
        git("push", "-u", "origin", "main", cwd=self.repo)
        git("fetch", "origin", cwd=self.repo)

        self.fw = self.repo / ".omn-agent"

    # ---- helpers ----------------------------------------------------------

    def run_cli(self, *argv) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def install(self) -> tuple[int, str]:
        return self.run_cli("install", str(self.repo), "--source",
                            str(self.source))

    def plan_tickets(self, specs: list[tuple[str, str, str]]):
        """Install once, sync every (key, issue type, summary) ticket, and
        plan each -- so several tasks can coexist in one repo."""
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        tickets = [make_ticket(key=k, itype=t, summary=s) for k, t, s in specs]
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
            tickets_mod.cmd_tickets_sync(args, transport=fake_transport(tickets))
        for key, _, _ in specs:
            code, out = self.run_cli("plan", key, "--target", str(self.repo))
            self.assertEqual(code, ExitCode.OK, out)

    def plan_ticket(self, key="PROJ-1", itype="Story",
                    summary="Add login timeout") -> str:
        self.plan_tickets([(key, itype, summary)])
        return key

    def task(self, key="PROJ-1") -> dict:
        return json.loads(
            (self.fw / "tasks" / key / "task-plan.json").read_text())

    def wt(self, key="PROJ-1") -> Path:
        """The task's bound worktree directory."""
        return self.repo / Path(self.task(key)["worktree"]["path"])

    def sync(self, tickets) -> str:
        """Re-run 'tickets sync' with the given raw Jira issues (Jira env
        vars and the connector are already configured by plan_tickets)."""
        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(self.repo)])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            tickets_mod.cmd_tickets_sync(args, transport=fake_transport(tickets))
        return out.getvalue()

    @staticmethod
    def closed_ticket(key="PROJ-1", summary="Add login timeout",
                      status="Done") -> dict:
        t = make_ticket(key=key, summary=summary,
                        updated="2026-08-21T10:00:00.000+0000")
        t["fields"]["status"]["name"] = status
        return t


class BranchPrTestCase(GitFixtureTestCase):
    # ---- branch bootstrap (worktree-isolated) -------------------------------

    def test_branch_creates_branch_in_isolated_worktree(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        # the shared main checkout is never switched
        self.assertEqual(git_ops.current_branch(self.repo), "main")
        task = self.task()
        self.assertEqual(task["branch"]["name"], "feature/proj-1-add-login-timeout")
        self.assertEqual(task["branch"]["base"], "main")
        self.assertEqual(task["branch"]["type"], "feature")
        self.assertEqual(task["worktree"]["path"], ".worktrees/proj-1-feature")
        self.assertEqual(task["worktree"]["branch"], task["branch"]["name"])
        self.assertEqual(task["worktree"]["base"], "main")
        self.assertEqual(task["worktree"]["status"], "active")
        wt = self.wt()
        self.assertTrue(wt.is_dir())
        self.assertEqual(git_ops.current_branch(wt),
                         "feature/proj-1-add-login-timeout")
        # the worktree container never dirties the main checkout
        self.assertFalse(git_ops.is_dirty(self.repo, exclude=(".omn-agent",
                                                              ".mcp.json")))

    def test_branch_type_override(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch", key, "--target", str(self.repo),
                                 "--type", "bugfix")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(git_ops.current_branch(self.repo), "main")
        self.assertTrue(git_ops.current_branch(self.wt()).startswith("bugfix/"))
        self.assertTrue(self.task()["worktree"]["path"].endswith("-bugfix"))

    def test_branch_reuses_existing_worktree(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        bound = self.task()["branch"]["name"]
        first_path = self.task()["worktree"]["path"]
        count = len(git_ops.list_worktrees(self.repo))
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("B-REUSE", out)
        # re-running the same task never creates a second worktree
        self.assertEqual(len(git_ops.list_worktrees(self.repo)), count)
        self.assertEqual(self.task()["worktree"]["path"], first_path)
        self.assertEqual(git_ops.current_branch(self.wt()), bound)

    def test_branch_warns_on_dirty_main_checkout_but_stays_isolated(self):
        key = self.plan_ticket()
        (self.repo / "scratch.txt").write_text("wip", encoding="utf-8")
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("B-DIRTY-MAIN", out)
        # the uncommitted change stays in the main checkout and never leaks
        # into the task's fresh worktree
        self.assertEqual(git_ops.current_branch(self.repo), "main")
        self.assertTrue((self.repo / "scratch.txt").exists())
        self.assertFalse((self.wt() / "scratch.txt").exists())

    def test_branch_dry_run_writes_nothing(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch", key, "--target", str(self.repo),
                                 "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertEqual(git_ops.current_branch(self.repo), "main")
        self.assertNotIn("branch", self.task())
        self.assertNotIn("worktree", self.task())
        self.assertFalse((self.repo / ".worktrees").exists())

    def test_branch_uses_project_configured_template(self):
        key = self.plan_ticket()
        code, out = self.run_cli(
            "branch-config", "set", "--target", str(self.repo),
            "--feature-template", "feature/on-{ticket_id}-{short_description}")
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(git_ops.current_branch(self.wt()),
                         "feature/on-proj-1-add-login-timeout")
        self.assertEqual(self.task()["branch"]["template"],
                         "feature/on-{ticket_id}-{short_description}")

    def test_branch_explicit_missing_base_fails_clearly(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch", key, "--target", str(self.repo),
                                 "--base", "does-not-exist")
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("does not exist", out)
        self.assertEqual(git_ops.current_branch(self.repo), "main")
        self.assertFalse((self.repo / ".worktrees").exists())

    def test_branch_always_prints_base_tip(self):
        key = self.plan_ticket()
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("B-BASE-TIP", out)
        self.assertIn("base 'main' is at", out)
        tip = git_ops.describe_commit(self.repo, "main")
        self.assertIn(tip["hash"][:12], out)
        self.assertIn(tip["subject"], out)

    def test_branch_warns_when_base_is_far_behind_active_branch(self):
        key = self.plan_ticket()
        # Simulate an abandoned main: a 'develop' branch with far more history,
        # pushed so it is also the remote's most recently active branch.
        git("checkout", "-b", "develop", cwd=self.repo)
        for i in range(6):
            (self.repo / f"work{i}.txt").write_text(str(i), encoding="utf-8")
            git("add", f"work{i}.txt", cwd=self.repo)
            git("commit", "-m", f"work {i}", cwd=self.repo)
        git("push", "-u", "origin", "develop", cwd=self.repo)
        git("checkout", "main", cwd=self.repo)
        (self.fw / "config" / "branch-defaults.json").write_text(
            json.dumps({"divergenceWarningThreshold": 5}), encoding="utf-8")

        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)  # a warning, never a block
        self.assertIn("B-STALE-BASE", out)
        self.assertIn("6 commits behind 'develop'", out)
        self.assertIn("--base develop", out)

    def test_branch_no_stale_warning_below_threshold(self):
        key = self.plan_ticket()
        git("checkout", "-b", "develop", cwd=self.repo)
        (self.repo / "one.txt").write_text("1", encoding="utf-8")
        git("add", "one.txt", cwd=self.repo)
        git("commit", "-m", "one", cwd=self.repo)
        git("push", "-u", "origin", "develop", cwd=self.repo)
        git("checkout", "main", cwd=self.repo)
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertNotIn("B-STALE-BASE", out)

    def test_branch_uses_configured_default_base(self):
        key = self.plan_ticket()
        git("checkout", "-b", "develop", cwd=self.repo)
        (self.repo / "d.txt").write_text("d", encoding="utf-8")
        git("add", "d.txt", cwd=self.repo)
        git("commit", "-m", "develop work", cwd=self.repo)
        git("push", "-u", "origin", "develop", cwd=self.repo)
        git("checkout", "main", cwd=self.repo)
        (self.fw / "config" / "branch-defaults.json").write_text(
            json.dumps({"defaultBase": "develop"}), encoding="utf-8")

        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("B-BASE", out)
        self.assertEqual(self.task()["branch"]["base"], "develop")

    def test_branch_explicit_base_overrides_configured_default(self):
        key = self.plan_ticket()
        git("checkout", "-b", "develop", cwd=self.repo)
        git("push", "-u", "origin", "develop", cwd=self.repo)
        git("checkout", "main", cwd=self.repo)
        (self.fw / "config" / "branch-defaults.json").write_text(
            json.dumps({"defaultBase": "develop"}), encoding="utf-8")
        code, out = self.run_cli("branch", key, "--target", str(self.repo),
                                 "--base", "main")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(self.task()["branch"]["base"], "main")

    def test_commits_behind_and_most_recently_active_branch(self):
        git("checkout", "-b", "develop", cwd=self.repo)
        for i in range(3):
            (self.repo / f"c{i}.txt").write_text(str(i), encoding="utf-8")
            git("add", f"c{i}.txt", cwd=self.repo)
            git("commit", "-m", f"c{i}", cwd=self.repo)
        git("push", "-u", "origin", "develop", cwd=self.repo)
        git("checkout", "main", cwd=self.repo)
        self.assertEqual(git_ops.commits_behind(self.repo, "main", "develop"), 3)
        self.assertEqual(git_ops.commits_behind(self.repo, "develop", "main"), 0)
        self.assertIsNone(git_ops.commits_behind(self.repo, "main", "no-such"))
        self.assertEqual(
            git_ops.most_recently_active_branch(self.repo, exclude={"main"}),
            "develop")

    def test_branch_requires_git_repo(self):
        # A non-git target: '.omn-agent' itself is a valid repo-root marker,
        # so install/plan/branch all still resolve the target -- only the
        # git-specific guard should reject it.
        non_git = self.tmp / "non-git-repo"
        non_git.mkdir()
        code, out = self.run_cli("init", str(non_git))
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("install", str(non_git), "--source",
                                 str(self.source))
        self.assertEqual(code, ExitCode.OK, out)
        ticket = make_ticket(key="PROJ-9", summary="No git here")
        args = cli.build_parser().parse_args(
            ["tickets", "sync", "--target", str(non_git)])
        os.environ["JIRA_EMAIL"] = "dev@example.com"
        os.environ["JIRA_API_TOKEN"] = "token"
        self.addCleanup(os.environ.pop, "JIRA_EMAIL", None)
        self.addCleanup(os.environ.pop, "JIRA_API_TOKEN", None)
        self.run_cli("mcp", "add", "jira", "--target", str(non_git),
                     "--base-url", "https://x.atlassian.net", "--project", "PROJ")
        out2 = io.StringIO()
        with contextlib.redirect_stdout(out2):
            tickets_mod.cmd_tickets_sync(args, transport=fake_transport([ticket]))
        self.run_cli("plan", "PROJ-9", "--target", str(non_git))
        code, out = self.run_cli("branch", "PROJ-9", "--target", str(non_git))
        self.assertEqual(code, ExitCode.INVALID_TARGET, out)

    # ---- implementation-phase worktree guard --------------------------------

    def test_dispatch_implementation_requires_bound_worktree(self):
        key = self.plan_ticket()
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "implementation",
                                 "--approve")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no feature branch is bound", out)

    def test_dispatch_implementation_ignores_main_checkout_branch(self):
        # A branch checked out in the shared tree is not the task's binding:
        # only 'omn-agent branch' (worktree creation) binds a task.
        key = self.plan_ticket()
        self.run_cli("run", key, "--target", str(self.repo), "--approve")
        git("checkout", "-b", "feat/unbound", cwd=self.repo)
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "implementation",
                                 "--approve")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no feature branch is bound", out)

    def test_dispatch_implementation_rejects_worktree_branch_mismatch(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        self.run_cli("run", key, "--target", str(self.repo), "--approve")
        git("checkout", "-b", "feat/hijacked", cwd=self.wt())
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "implementation",
                                 "--approve")
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("is bound to branch", out)

    def test_dispatch_implementation_fails_when_worktree_deleted(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        self.run_cli("run", key, "--target", str(self.repo), "--approve")
        shutil.rmtree(self.wt())
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "implementation",
                                 "--approve")
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("missing", out)

    def test_dispatch_implementation_succeeds_in_bound_worktree(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        self.run_cli("run", key, "--target", str(self.repo), "--approve")
        # the shared checkout's state is irrelevant -- even parked on main
        self.assertEqual(git_ops.current_branch(self.repo), "main")
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "implementation",
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("R-WORKTREE", out)

    def test_dispatch_other_phase_is_not_branch_guarded(self):
        key = self.plan_ticket()
        self.run_cli("run", key, "--target", str(self.repo), "--approve")
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "scope-and-acceptance",
                                 "--approve")
        self.assertEqual(code, ExitCode.OK, out)

    # ---- pr precheck --------------------------------------------------------

    def test_pr_precheck_requires_branch(self):
        key = self.plan_ticket()
        code, out = self.run_cli("pr", "precheck", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no branch is bound", out)

    def test_pr_precheck_rejects_worktree_branch_mismatch(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        git("checkout", "-b", "feat/hijacked", cwd=self.wt())
        code, out = self.run_cli("pr", "precheck", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("is bound to", out)

    def test_pr_precheck_warns_when_no_tests_detected(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        code, out = self.run_cli("pr", "precheck", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertIn("no test command detected", out)
        self.assertTrue(self.task()["prChecks"]["passed"])

    def test_pr_precheck_runs_detected_passing_tests(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        # the task's code (tests included) lives in its worktree
        tests_dir = self.wt() / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_x.py").write_text(
            "import unittest\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_ok(self):\n"
            "        self.assertTrue(True)\n", encoding="utf-8")
        code, out = self.run_cli("pr", "precheck", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertTrue(self.task()["prChecks"]["passed"])

    def test_pr_precheck_reports_failing_tests(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        tests_dir = self.wt() / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_x.py").write_text(
            "import unittest\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_fail(self):\n"
            "        self.assertTrue(False)\n", encoding="utf-8")
        code, out = self.run_cli("pr", "precheck", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertFalse(self.task()["prChecks"]["passed"])

    def test_pr_precheck_honors_explicit_test_cmd(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        code, out = self.run_cli("pr", "precheck", key, "--target", str(self.repo),
                                 "--test-cmd", "exit 1")
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)

    # ---- pr create ----------------------------------------------------------

    def test_pr_create_requires_branch(self):
        key = self.plan_ticket()
        code, out = self.run_cli("pr", "create", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("no branch is bound", out)

    def test_pr_create_dry_run_writes_nothing(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        code, out = self.run_cli("pr", "create", key, "--target", str(self.repo),
                                 "--dry-run")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertNotIn("pr", self.task())

    def test_pr_create_fails_safely_without_gh(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        with mock.patch("omn_agent.git_ops.gh_path", return_value=None):
            code, out = self.run_cli("pr", "create", key, "--target",
                                     str(self.repo), "--skip-checks")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("cli.github.com", out)
        # the branch was still pushed to origin even though gh is missing
        pushed = subprocess.run(
            ["git", "branch", "-r"], cwd=str(self.repo), capture_output=True,
            text=True).stdout
        self.assertIn("origin/" + self.task()["branch"]["name"], pushed)

    def test_pr_create_fails_safely_when_unauthenticated(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        with mock.patch("omn_agent.git_ops.gh_path", return_value="/usr/bin/gh"), \
             mock.patch("omn_agent.git_ops.gh_authenticated", return_value=False):
            code, out = self.run_cli("pr", "create", key, "--target",
                                     str(self.repo), "--skip-checks")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("gh auth login", out)

    def test_pr_create_runs_checks_unless_skipped(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        tests_dir = self.wt() / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_x.py").write_text(
            "import unittest\n\n"
            "class T(unittest.TestCase):\n"
            "    def test_fail(self):\n"
            "        self.assertTrue(False)\n", encoding="utf-8")
        code, out = self.run_cli("pr", "create", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        # never reached gh / push since checks failed first
        pushed = subprocess.run(
            ["git", "branch", "-r"], cwd=str(self.repo), capture_output=True,
            text=True).stdout
        self.assertNotIn("origin/" + self.task()["branch"]["name"], pushed)

    def test_pr_create_uses_standardized_title_and_body(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        from omn_agent.pr import _pr_title_and_body
        task = self.task()
        title, body = _pr_title_and_body(task, None)
        self.assertEqual(title, "feature(PROJ-1): Add login timeout")
        self.assertIn("Closes PROJ-1", body)
        self.assertIn("## Summary", body)
        self.assertIn("## Checklist", body)

    # ---- worktree isolation and conflict handling ---------------------------

    def test_two_tasks_get_isolated_worktrees(self):
        self.plan_tickets([("PROJ-1", "Story", "Add login timeout"),
                           ("PROJ-2", "Bug", "Fix logout crash")])
        for key in ("PROJ-1", "PROJ-2"):
            code, out = self.run_cli("branch", key, "--target", str(self.repo))
            self.assertEqual(code, ExitCode.OK, out)

        wt1, wt2 = self.wt("PROJ-1"), self.wt("PROJ-2")
        b1 = self.task("PROJ-1")["branch"]["name"]
        b2 = self.task("PROJ-2")["branch"]["name"]
        self.assertNotEqual(wt1, wt2)
        self.assertNotEqual(b1, b2)
        self.assertEqual(git_ops.current_branch(wt1), b1)
        self.assertEqual(git_ops.current_branch(wt2), b2)
        self.assertEqual(git_ops.current_branch(self.repo), "main")

        # a change in one task's worktree is invisible to the other task and
        # to the shared checkout
        (wt1 / "feature.py").write_text("x = 1\n", encoding="utf-8")
        self.assertFalse((wt2 / "feature.py").exists())
        self.assertFalse((self.repo / "feature.py").exists())
        self.assertFalse(git_ops.is_dirty(self.repo))

        # both tasks can dispatch implementation independently -- neither
        # blocks or re-points the other
        for key in ("PROJ-1", "PROJ-2"):
            self.run_cli("run", key, "--target", str(self.repo), "--approve")
            code, out = self.run_cli("run", key, "--target", str(self.repo),
                                     "--dispatch", "--phase", "implementation",
                                     "--approve")
            self.assertEqual(code, ExitCode.OK, out)

    def test_worktree_mapping_is_deterministic(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(self.task()["worktree"]["path"],
                         ".worktrees/proj-1-feature")

    def test_branch_conflicts_with_unregistered_dir_unless_forced(self):
        key = self.plan_ticket()
        squatter = self.repo / ".worktrees" / "proj-1-feature"
        squatter.mkdir(parents=True)
        (squatter / "junk.txt").write_text("junk", encoding="utf-8")
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("not a registered git worktree", out)
        code, out = self.run_cli("branch", key, "--target", str(self.repo),
                                 "--force")
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(git_ops.current_branch(squatter),
                         "feature/proj-1-add-login-timeout")
        self.assertFalse((squatter / "junk.txt").exists())

    def test_branch_recreates_manually_deleted_worktree(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        wt = self.wt()
        shutil.rmtree(wt)
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        self.assertTrue(wt.is_dir())
        self.assertEqual(git_ops.current_branch(wt),
                         self.task()["branch"]["name"])

    def test_branch_fails_when_branch_held_by_main_checkout(self):
        key = self.plan_ticket()
        git("checkout", "-b", "feature/proj-1-add-login-timeout", cwd=self.repo)
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("main working tree", out)

    # ---- automatic cleanup when the ticket closes ---------------------------

    def test_sync_auto_removes_worktree_when_ticket_closed(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        wt = self.wt()
        out = self.sync([self.closed_ticket(key=key)])
        self.assertIn("T-WT-CLEAN", out)
        self.assertFalse(wt.exists())
        self.assertFalse(any(git_ops.same_path(e["path"], wt)
                             for e in git_ops.list_worktrees(self.repo)))
        task = self.task()
        self.assertEqual(task["worktree"]["status"], "removed")
        self.assertIn("ticket closed", task["worktree"]["reason"])
        # only the isolation is released -- the branch itself is kept
        self.assertTrue(git_ops.local_branch_exists(
            self.repo, task["branch"]["name"]))

    def test_sync_keeps_dirty_worktree_of_closed_ticket(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        (self.wt() / "wip.py").write_text("x = 1\n", encoding="utf-8")
        out = self.sync([self.closed_ticket(key=key)])
        self.assertIn("T-WT-DIRTY", out)
        self.assertTrue(self.wt().is_dir())
        self.assertTrue((self.wt() / "wip.py").exists())
        self.assertEqual(self.task()["worktree"]["status"], "active")

    def test_sync_leaves_open_ticket_worktree_alone(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        still_open = make_ticket(key=key, summary="Add login timeout",
                                 updated="2026-08-21T10:00:00.000+0000")
        out = self.sync([still_open])
        self.assertNotIn("T-WT-CLEAN", out)
        self.assertTrue(self.wt().is_dir())
        self.assertEqual(self.task()["worktree"]["status"], "active")

    def test_pull_auto_removes_worktree_when_ticket_closed(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        wt = self.wt()
        args = cli.build_parser().parse_args(
            ["tickets", "pull", key, "--target", str(self.repo)])
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            tickets_mod.cmd_tickets_pull(
                args, transport=fake_transport([self.closed_ticket(key=key)]))
        self.assertIn("T-WT-CLEAN", out.getvalue())
        self.assertFalse(wt.exists())
        self.assertEqual(self.task()["worktree"]["status"], "removed")

    def test_dispatch_names_released_worktree_clearly(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        self.run_cli("run", key, "--target", str(self.repo), "--approve")
        self.sync([self.closed_ticket(key=key)])
        code, out = self.run_cli("run", key, "--target", str(self.repo),
                                 "--dispatch", "--phase", "implementation",
                                 "--approve")
        self.assertEqual(code, ExitCode.INCOMPLETE, out)
        self.assertIn("was released", out)
        self.assertIn("ticket closed", out)

    def test_branch_rebinds_after_cleanup(self):
        key = self.plan_ticket()
        self.run_cli("branch", key, "--target", str(self.repo))
        self.sync([self.closed_ticket(key=key)])
        code, out = self.run_cli("branch", key, "--target", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)
        task = self.task()
        self.assertEqual(task["worktree"]["status"], "active")
        self.assertTrue(self.wt().is_dir())
        self.assertEqual(git_ops.current_branch(self.wt()),
                         task["branch"]["name"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
