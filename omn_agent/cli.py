"""omn-agent command-line interface.

Exit codes (stable contract):
    0  success
    1  invalid target / repo not found / bad arguments about the target
    2  installation or configuration incomplete
    3  validation failed
    4  incompatible existing state (nothing was changed)
    5  dry-run finished (nothing was written)
    6  permission denied
    7  unexpected error
    8  approval required for a side-effecting step (nothing was executed)
"""

from __future__ import annotations

import argparse
import sys
import traceback

from . import __version__
from .common import ExitCode, OmnError


def _target_arg(p: argparse.ArgumentParser, positional: bool):
    """Every target-taking subcommand accepts --target/-t uniformly.

    The subcommands that historically took the target positionally (init, install, upgrade,
    validate, doctor, status) keep that form as a hidden fallback, so existing scripts and
    docs stay valid; the flag wins when both are given. `_resolve_target_arg` folds the two
    into `args.target` before dispatch.
    """
    p.add_argument("--target", "-t", default=None, dest="target",
                   help="target repository path (default: current directory)")
    if positional:
        p.add_argument("target_positional", nargs="?", default=None,
                       metavar="target", help=argparse.SUPPRESS)


def _resolve_target_arg(args):
    if getattr(args, "target", None) is None:
        args.target = getattr(args, "target_positional", None) or "."


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="omn-agent",
        description="Bootstrap, validate, upgrade, and orchestrate the Omn-Agent "
                    "AI engineering framework in a target repository.")
    ap.add_argument("--version", action="version", version=f"omn-agent {__version__}")
    sub = ap.add_subparsers(dest="cmd", required=True)

    from . import (branch, branch_config, context_gen, fix_comments,
                  installer, mcp, pr, quality_scan, runner, taskplan,
                  tickets, update, validator)

    p = sub.add_parser(
        "init", help="create the framework directory layout",
        description="Create the .omn-agent directory layout, and seed "
                    "project-local config that's written once and then owned "
                    "by the project -- including branch naming templates "
                    "(see 'omn-agent branch-config --help' to view/change "
                    "them later).",
        epilog="examples:\n"
               "  omn-agent init ./my-repo\n"
               "  omn-agent init ./my-repo --feature-branch-template "
               "'feature/on-{ticket_id}-{short_description}'\n"
               "  omn-agent init ./my-repo --bugfix-branch-template "
               "'bugfix/on-{ticket_id}-{short_description}' --branch-max-length 60",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    _target_arg(p, positional=True)
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.add_argument("--feature-branch-template", metavar="TEMPLATE",
                   help="branch name template for feature/implement work "
                        f"(default: '{branch_config.DEFAULT_TEMPLATES['feature']}'); "
                        "tokens: {ticket_id} {short_description} {work_type}. "
                        "With no template flags on an interactive terminal, "
                        "you're prompted for these instead")
    p.add_argument("--bugfix-branch-template", metavar="TEMPLATE",
                   help="branch name template for bugfix work (default: "
                        f"'{branch_config.DEFAULT_TEMPLATES['bugfix']}')")
    p.add_argument("--branch-max-length", type=int, metavar="N",
                   help="max generated branch name length (default "
                        f"{branch_config.DEFAULT_MAX_LENGTH})")
    p.set_defaults(fn=installer.cmd_init)

    p = sub.add_parser("install", help="install or repair the framework payload")
    _target_arg(p, positional=True)
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.add_argument("--force", action="store_true",
                   help="replace modified/unrecorded files at framework paths "
                        "(keeps a .omn-bak backup); files at non-framework paths "
                        "are never touched")
    p.add_argument("--source", help="framework source checkout to install from")
    p.set_defaults(fn=installer.cmd_install)

    p = sub.add_parser("upgrade", help="update framework-managed files only")
    _target_arg(p, positional=True)
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.add_argument("--force", action="store_true",
                   help="replace locally modified framework files (with backup)")
    p.add_argument("--source", help="framework source checkout to upgrade from")
    p.set_defaults(fn=installer.cmd_upgrade)

    p = sub.add_parser("validate", help="validate the installation")
    _target_arg(p, positional=True)
    p.set_defaults(fn=validator.cmd_validate)

    p = sub.add_parser("doctor", help="validate plus drift/health diagnosis")
    _target_arg(p, positional=True)
    p.set_defaults(fn=validator.cmd_doctor)

    p = sub.add_parser("status", help="summarize installation, tickets, and runs")
    _target_arg(p, positional=True)
    p.set_defaults(fn=validator.cmd_status)

    mcp_p = sub.add_parser("mcp", help="manage MCP connectors")
    mcp_sub = mcp_p.add_subparsers(dest="mcp_cmd", required=True)
    p = mcp_sub.add_parser("add", help="add a connector")
    add_sub = p.add_subparsers(dest="connector", required=True)
    j = add_sub.add_parser("jira", help="configure the Jira connector")
    _target_arg(j, positional=False)
    j.add_argument("--base-url", required=True,
                   help="Jira site URL, e.g. https://yourteam.atlassian.net")
    j.add_argument("--project", action="append", default=[], metavar="KEY",
                   help="Jira project key; repeat or comma-separate for several")
    j.add_argument("--email-env", default=mcp.DEFAULT_EMAIL_ENV,
                   help="env var holding the Jira account email "
                        f"(default {mcp.DEFAULT_EMAIL_ENV}); the value is never stored")
    j.add_argument("--token-env", default=mcp.DEFAULT_TOKEN_ENV,
                   help="env var holding the Jira API token "
                        f"(default {mcp.DEFAULT_TOKEN_ENV}); the value is never stored")
    j.add_argument("--force", action="store_true",
                   help="replace an existing different 'jira' entry in .mcp.json")
    j.add_argument("--dry-run", action="store_true", help="preview without writing")
    j.set_defaults(fn=mcp.cmd_mcp_add_jira)
    m = add_sub.add_parser("msdev",
                           help="configure the MSDev (Azure DevOps) connector")
    _target_arg(m, positional=False)
    m.add_argument("--org-url", required=True,
                   help="Azure DevOps organization URL, e.g. "
                        "https://dev.azure.com/yourorg")
    m.add_argument("--project", required=True,
                   help="Azure DevOps project the work items live in")
    m.add_argument("--token-env", default=mcp.DEFAULT_MSDEV_TOKEN_ENV,
                   help="env var holding the personal access token "
                        f"(default {mcp.DEFAULT_MSDEV_TOKEN_ENV}); the value "
                        "is never stored")
    m.add_argument("--force", action="store_true",
                   help="replace an existing different 'msdev' entry in .mcp.json")
    m.add_argument("--dry-run", action="store_true", help="preview without writing")
    m.set_defaults(fn=mcp.cmd_mcp_add_msdev)
    p = mcp_sub.add_parser("init", help="guided connector setup (no flags needed)")
    init_sub = p.add_subparsers(dest="connector", required=True)
    ji = init_sub.add_parser(
        "jira",
        help="interactive Jira setup: validates the repo, tests the connection, "
             "auto-detects project keys, confirms before writing")
    _target_arg(ji, positional=False)
    ji.add_argument("--base-url", help="prefill the Jira site URL")
    ji.add_argument("--force", action="store_true",
                    help="replace an existing different 'jira' entry in .mcp.json")
    ji.set_defaults(fn=mcp.cmd_mcp_init_jira)

    ctx_p = sub.add_parser("context", help="generate project-context artifacts")
    ctx_sub = ctx_p.add_subparsers(dest="context_cmd", required=True)
    p = ctx_sub.add_parser(
        "generate", help="derive a context artifact from the target repository",
        description="Generate a context artifact the runtime's context slices "
                    "require. 'dependency-map' derives the module dependency "
                    "graph from the repository's own manifests (*.csproj "
                    "project references, package.json local dependencies, "
                    "pyproject.toml dependencies), falling back to a clearly "
                    "labelled placeholder when none are detectable.",
        epilog="examples:\n"
               "  omn-agent context generate dependency-map -t ./my-repo\n"
               "  omn-agent context generate dependency-map -t ./my-repo --force",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("artifact", choices=["dependency-map"],
                   help="which context artifact to generate")
    _target_arg(p, positional=False)
    p.add_argument("--force", action="store_true",
                   help="overwrite an existing (project-owned) file")
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.set_defaults(fn=context_gen.cmd_context_generate)

    t_p = sub.add_parser("tickets", help="ingest Jira tickets")
    t_sub = t_p.add_subparsers(dest="tickets_cmd", required=True)
    p = t_sub.add_parser("sync", help="sync open tickets from configured projects")
    _target_arg(p, positional=False)
    p.add_argument("--jql", help="override the sync JQL query")
    p.add_argument("--max", type=int, default=50,
                   help="maximum tickets to fetch (default 50)")
    p.set_defaults(fn=tickets.cmd_tickets_sync)
    p = t_sub.add_parser("pull", help="fetch specific tickets by key")
    p.add_argument("keys", nargs="+", metavar="KEY", help="issue keys, e.g. PROJ-123")
    _target_arg(p, positional=False)
    p.set_defaults(fn=tickets.cmd_tickets_pull)

    p = sub.add_parser("plan", help="turn a synced ticket into a framework task")
    p.add_argument("key", metavar="KEY", help="ticket key, e.g. PROJ-123")
    _target_arg(p, positional=False)
    p.add_argument("--command", choices=sorted(taskplan.ROUTES),
                   help="override the automatic routing")
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.set_defaults(fn=taskplan.cmd_plan)

    p = sub.add_parser(
        "run",
        help="drive the framework runtime for a planned task, or a ticket "
             "end to end from an MCP provider (side-effecting steps require "
             "approval)",
        description="Two modes. 'omn-agent run <KEY>' (legacy, unchanged) "
                    "advances a planned task one runtime step at a time via "
                    "--show/--dispatch/--complete/--gate. 'omn-agent run "
                    "<Provider> <TicketKey>' is the one-command end-to-end "
                    "mode: it resolves the provider from the MCP config "
                    "(.omn-agent/config/mcp.json), fetches the ticket "
                    "through that connector (Jira, MSDev/Azure DevOps), "
                    "classifies and routes the work (bug -> fix-bug, "
                    "refactor/investigate keep their routing, everything "
                    "else -> implement-feature), materializes the runtime "
                    "run, binds the feature branch and isolated worktree "
                    "before implementation, and drives dispatch/complete "
                    "under the gate policy until the host must run a "
                    "dispatched subagent or a human must decide a held "
                    "gate. When the run completes it runs the pre-PR "
                    "quality checks, pushes the bound branch, and creates "
                    "or updates the PR. Re-running the same command resumes "
                    "from live state.",
        epilog="examples:\n"
               "  omn-agent run PROJ-123 --show\n"
               "  omn-agent run Jira ON-115 --gate-policy auto --approve\n"
               "  omn-agent run MSDev ONN-115 --gate-policy auto --approve\n"
               "  omn-agent run Jira ON-115 --dry-run\n",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY",
                   help="ticket key of a planned task -- or an MCP provider "
                        "name (e.g. Jira, MSDev) when a ticket key follows")
    p.add_argument("ticket", nargs="?", default=None, metavar="TICKET",
                   help="ticket key to drive end to end from the named "
                        "provider (enables the one-command mode)")
    _target_arg(p, positional=False)
    p.add_argument("--approve", action="store_true",
                   help="approve the side-effecting step non-interactively "
                        "(in provider mode: every side-effecting step)")
    p.add_argument("--show", action="store_true", help="show run status (read-only)")
    p.add_argument("--report", action="store_true",
                   help="print the run's final who-did-what-when report: every phase "
                        "with its agent, start/finish times and duration, every gate "
                        "decision with decider and wait time, and the full event "
                        "timeline (read-only; also printed automatically when the "
                        "run completes)")
    p.add_argument("--watch", action="store_true",
                   help="with --show: poll and re-render in place until Ctrl+C "
                        "(read-only; never dispatches/completes/gates)")
    p.add_argument("--json", action="store_true",
                   help="with --show: machine-readable run state instead of the "
                        "table/tree")
    p.add_argument("--no-color", action="store_true",
                   help="with --show: force the plain table even on a TTY")
    p.add_argument("--interval", type=float, default=2.0,
                   help="with --show --watch: seconds between polls (default: 2.0)")
    p.add_argument("--dispatch", action="store_true",
                   help="dispatch the next (or --phase) phase to its owner agent")
    p.add_argument("--complete", action="store_true",
                   help="ingest the agent result for --phase and transition")
    p.add_argument("--phase", help="phase name for --dispatch/--complete")
    p.add_argument("--gate", help="record a human gate decision for this gate")
    p.add_argument("--gate-policy", dest="gate_policy",
                   choices=["human-required", "auto-on-clean-evidence", "human",
                            "auto"],
                   help="gate decision policy for this invocation (default: "
                        "config/gate-policy.json, else human-required). 'auto' "
                        "lets the runtime approve a decision-eligible gate "
                        "itself when the evidence is clean; every held gate "
                        "still requires --gate/--decision as today")
    p.add_argument("--decision", choices=["approve", "reject"])
    p.add_argument("--owner-role", help="gate owner role being exercised")
    p.add_argument("--decided-by", help="who decided (default: current user)")
    p.add_argument("--rationale", help="rationale for the gate decision")
    p.add_argument("--no-fetch", action="store_true",
                   help="provider mode: skip the provider refresh and use "
                        "the inbox copy of the ticket")
    p.add_argument("--command", choices=sorted(taskplan.ROUTES),
                   help="provider mode: override the automatic routing "
                        "(see 'omn-agent plan --help')")
    p.add_argument("--test-cmd", help="provider mode: test/validation "
                                      "command for the pre-PR check (see "
                                      "'pr precheck --help')")
    p.add_argument("--base", help="provider mode: base branch for branch "
                                  "bootstrap and PR creation (default: the "
                                  "task's recorded base)")
    p.add_argument("--draft", action="store_true",
                   help="provider mode: open the PR as a draft when one "
                        "must be created")
    p.add_argument("--dry-run", action="store_true",
                   help="provider mode: preview the round without changing "
                        "anything")
    p.set_defaults(fn=runner.cmd_run)

    p = sub.add_parser(
        "update",
        help="one command to carry a Jira ticket change end-to-end: refresh "
             "the ticket, re-plan, drive the run, and push the result to "
             "the PR",
        description="Resumable change-request loop for a ticket that changed "
                    "in Jira (or a fresh one). One invocation refreshes the "
                    "ticket into the inbox, re-plans the task (an unchanged "
                    "ticket is a no-op), carries the change into the runtime "
                    "run -- materializing a run when none exists, or, when "
                    "the input changed, archiving the recorded run to the "
                    "task's runHistory and materializing a new one (the "
                    "runtime pins input digests at run creation: a changed "
                    "input is a new run) -- then drives the run: dispatching "
                    "each eligible phase to its owner agent (auto-binding "
                    "the branch/worktree before implementation), ingesting "
                    "completions, and letting the runtime auto-decide "
                    "clean-evidence gates per --gate-policy. It stops only "
                    "where the host must run a dispatched subagent or a "
                    "human must decide a held gate; re-running continues "
                    "from live state. When the run completes it runs the "
                    "pre-PR quality gate and pushes the bound branch, "
                    "updating the recorded PR or opening one. Side-effecting "
                    "steps require approval, exactly like 'omn-agent run'.",
        epilog="examples:\n"
               "  omn-agent update PROJ-123 -t ./my-repo\n"
               "  omn-agent update PROJ-123 -t ./my-repo --approve "
               "--gate-policy auto\n"
               "  omn-agent update PROJ-123 -t ./my-repo --dry-run\n"
               "  omn-agent update PROJ-123 -t ./my-repo --no-fetch "
               "--test-cmd \"npm run test:ci\"",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY", help="ticket key, e.g. PROJ-123")
    _target_arg(p, positional=False)
    p.add_argument("--approve", action="store_true",
                   help="approve every side-effecting step non-interactively")
    p.add_argument("--no-fetch", action="store_true",
                   help="skip the Jira refresh and use the inbox copy of "
                        "the ticket")
    p.add_argument("--command", choices=sorted(taskplan.ROUTES),
                   help="override the automatic routing (see 'omn-agent "
                        "plan --help')")
    p.add_argument("--gate-policy", dest="gate_policy",
                   choices=["human-required", "auto-on-clean-evidence",
                            "human", "auto"],
                   help="gate decision policy passed through to the runtime "
                        "(default: config/gate-policy.json, else "
                        "human-required); 'auto' lets the runtime decide "
                        "clean-evidence gates so the loop can run further "
                        "without a human")
    p.add_argument("--test-cmd", help="test/validation command for the "
                                      "pre-PR check (see 'pr precheck "
                                      "--help')")
    p.add_argument("--base", help="base branch for branch bootstrap and PR "
                                  "creation (default: the task's recorded "
                                  "base)")
    p.add_argument("--draft", action="store_true",
                   help="open the PR as a draft when one must be created")
    p.add_argument("--dry-run", action="store_true",
                   help="preview the round without changing anything")
    p.set_defaults(fn=update.cmd_update)

    p = sub.add_parser(
        "quality-scan",
        help="one command to run a repository quality scan: junk, duplication, "
             "dead code, over-abstraction -- evidence-first, held at a human "
             "gate",
        description="Drive the framework's /quality-scan command end to end: "
                    "render the quality-scan-scope input from your flags (or "
                    "--scope-file), record the scan as task QS-<NAME>, "
                    "materialize the runtime run (a changed scope archives "
                    "the previous run to runHistory: a changed input is a "
                    "new run), dispatch the single repository-quality-scan "
                    "phase to the reviewer agent, and -- after the host has "
                    "run the dispatched subagent -- re-run the same command "
                    "to ingest and validate the review package. The scan "
                    "reviews and stops: no source change, no auto-fix, no "
                    "merge decision. It terminates at the Quality Handoff "
                    "Gate, decided by a human tech lead via 'omn-agent run "
                    "QS-<NAME> --gate \"Quality Handoff Gate\" ...'. "
                    "Side-effecting steps require approval, exactly like "
                    "'omn-agent run'; 'omn-agent run QS-<NAME> "
                    "--show/--watch/--report' work on a scan unchanged.",
        epilog="examples:\n"
               "  omn-agent quality-scan -t ./my-repo --approve\n"
               "  omn-agent quality-scan backend -t ./my-repo "
               "--paths src/api,src/core --exclude vendor/ --approve\n"
               "  omn-agent quality-scan backend -t ./my-repo "
               "--context 'pre-merge sweep for PR #42' "
               "--risk-threshold high\n"
               "  omn-agent quality-scan audit -t ./my-repo "
               "--scope-file ./scan-scope.md --dry-run",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("name", nargs="?", default=None, metavar="NAME",
                   help="scan name; becomes task key QS-<NAME> "
                        "(default: 'repo')")
    _target_arg(p, positional=False)
    p.add_argument("--paths", action="append", default=[], metavar="PATH",
                   help="path or module to review; repeat or comma-separate "
                        "(default: the whole repository)")
    p.add_argument("--exclude", action="append", default=[], metavar="PATH",
                   help="path to exclude beyond the defaults "
                        "(framework dir, .worktrees/, .git/); repeat or "
                        "comma-separate")
    p.add_argument("--context", help="ticket or PR context recorded in the "
                                     "scan scope")
    p.add_argument("--risk-threshold",
                   choices=list(quality_scan.RISK_THRESHOLDS),
                   default="medium",
                   help="lowest severity the requester considers actionable "
                        "(default: medium)")
    p.add_argument("--scope-file", metavar="FILE",
                   help="use this quality-scan-scope document verbatim "
                        "instead of rendering one from the flags")
    p.add_argument("--approve", action="store_true",
                   help="approve every side-effecting step non-interactively")
    p.add_argument("--gate-policy", dest="gate_policy",
                   choices=["human-required", "auto-on-clean-evidence",
                            "human", "auto"],
                   help="gate decision policy passed through to the runtime "
                        "(default: config/gate-policy.json, else "
                        "human-required). The Quality Handoff Gate is meant "
                        "for a human tech lead; leave this unset unless you "
                        "know you want clean-evidence auto-approval")
    p.add_argument("--dry-run", action="store_true",
                   help="preview the scan without changing anything")
    p.set_defaults(fn=quality_scan.cmd_quality_scan)

    p = sub.add_parser("branch", help="create the feature branch for a planned "
                                      "task in its own isolated worktree",
                       description="Bootstrap the feature branch for a planned "
                                   "task from its ticket metadata, named per "
                                   "the project's branch naming templates "
                                   "(see 'omn-agent branch-config show'; "
                                   "defaults to feature/<ticket>-<slug> / "
                                   "bugfix/<ticket>-<slug>), created off "
                                   "main/master (or --base) inside the task's "
                                   "own git worktree at "
                                   ".worktrees/<ticket>-<work-type>/ -- the "
                                   "main checkout is never switched, so "
                                   "concurrent tasks stay isolated. "
                                   "Idempotent: re-running reuses the "
                                   "already-bound worktree.",
                       epilog="examples:\n"
                              "  omn-agent branch PROJ-123 -t ./my-repo\n"
                              "  omn-agent branch PROJ-123 -t ./my-repo --type bugfix\n"
                              "  omn-agent branch PROJ-123 -t ./my-repo --base "
                              "develop --dry-run",
                       formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY", help="ticket key of a planned task")
    _target_arg(p, positional=False)
    p.add_argument("--type", metavar="WORKTYPE",
                   help="work type used to pick a branch naming template "
                        "(default: derived from the task's routed command; "
                        "see 'omn-agent branch-config show' for configured "
                        "work types)")
    p.add_argument("--base", help="base branch to branch from (default: "
                                  "defaultBase from config/branch-defaults.json "
                                  "if set, else main, falling back to master)")
    p.add_argument("--force", action="store_true",
                   help="delete and recreate the worktree directory when the "
                        "path exists but is not a registered git worktree")
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.set_defaults(fn=branch.cmd_branch)

    pr_p = sub.add_parser("pr", help="pre-PR quality gates and pull request "
                                     "creation")
    pr_sub = pr_p.add_subparsers(dest="pr_cmd", required=True)

    p = pr_sub.add_parser(
        "precheck", help="run the branch guard and quality gate without "
                          "opening a PR",
        description="Verify the task's isolated worktree is on its bound "
                    "feature branch (never main/master), then run its test "
                    "command inside that worktree (auto-detected, or "
                    "--test-cmd) and record the result on the task.",
        epilog="examples:\n"
               "  omn-agent pr precheck PROJ-123 -t ./my-repo\n"
               "  omn-agent pr precheck PROJ-123 -t ./my-repo --test-cmd "
               "\"npm run test:ci\"",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY", help="ticket key of a planned task")
    _target_arg(p, positional=False)
    p.add_argument("--test-cmd", help="test/validation command to run "
                                      "(default: auto-detected from the "
                                      "repository -- tests/, pyproject.toml, "
                                      "or package.json)")
    p.set_defaults(fn=pr.cmd_pr_precheck)

    p = pr_sub.add_parser(
        "create", help="run pre-PR checks then open a PR (gh CLI, or an "
                       "actionable fallback)",
        description="Run the same checks as 'pr precheck' (unless "
                    "--skip-checks), push the bound branch, and open a Pull "
                    "Request with a standardized title/body via the GitHub "
                    "CLI. If 'gh' is missing or unauthenticated, fails safely "
                    "with the exact next steps (install/auth command, or a "
                    "ready-made compare URL) instead of guessing.",
        epilog="examples:\n"
               "  omn-agent pr create PROJ-123 -t ./my-repo\n"
               "  omn-agent pr create PROJ-123 -t ./my-repo --draft\n"
               "  omn-agent pr create PROJ-123 -t ./my-repo --base develop\n"
               "  omn-agent pr create PROJ-123 -t ./my-repo --skip-checks",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY", help="ticket key of a planned task")
    _target_arg(p, positional=False)
    p.add_argument("--base", help="override the task's recorded base branch")
    p.add_argument("--draft", action="store_true", help="open the PR as a draft")
    p.add_argument("--skip-checks", action="store_true",
                   help="skip pre-PR checks (branch guard still applies; "
                        "not recommended)")
    p.add_argument("--test-cmd", help="test/validation command for the "
                                      "pre-PR check (see 'pr precheck --help')")
    p.add_argument("--dry-run", action="store_true", help="preview without writing")
    p.set_defaults(fn=pr.cmd_pr_create)

    p = pr_sub.add_parser(
        "fix-comments",
        help="one-command loop to resolve PR review comments: collect them, "
             "reject the pending gate with them, re-dispatch the fix, then "
             "verify, close the gate, and push",
        description="Drive the framework's correction cycle for a PR that "
                    "collected reviewer comments (human reviews and bot "
                    "findings such as Sonar). One invocation collects the "
                    "feedback via 'gh', rejects the gate awaiting decision "
                    "with the findings as rationale (the runtime rolls back "
                    "and carries them to the fix phase), and re-dispatches "
                    "that phase to its owner agent. After the host has run "
                    "the dispatched subagent, re-running the same command "
                    "ingests the completion, re-runs the pre-PR checks, "
                    "approves the gate on that evidence, and pushes the "
                    "bound branch so the PR updates. Resumable: it always "
                    "continues from the recorded round state. Side-effecting "
                    "steps require approval, exactly like 'omn-agent run'.",
        epilog="examples:\n"
               "  omn-agent pr fix-comments PROJ-123 -t ./my-repo\n"
               "  omn-agent pr fix-comments PROJ-123 -t ./my-repo --approve\n"
               "  omn-agent pr fix-comments PROJ-123 -t ./my-repo --dry-run\n"
               "  omn-agent pr fix-comments PROJ-123 -t ./my-repo "
               "--pr 42 --test-cmd \"npm run test:ci\"",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY",
                   help="ticket key of a planned task with an open PR")
    _target_arg(p, positional=False)
    p.add_argument("--pr", help="PR number or URL (default: the PR recorded "
                                "by 'omn-agent pr create')")
    p.add_argument("--approve", action="store_true",
                   help="approve every side-effecting step non-interactively")
    p.add_argument("--owner-role",
                   help="gate owner role deciding the reject/approve "
                        "(default: the gate's deciding owner)")
    p.add_argument("--decided-by", help="who decided (default: current user)")
    p.add_argument("--test-cmd", help="test/validation command for the "
                                      "verification step (see 'pr precheck "
                                      "--help')")
    p.add_argument("--dry-run", action="store_true",
                   help="preview the round without changing anything")
    p.set_defaults(fn=fix_comments.cmd_pr_fix_comments)

    bc_p = sub.add_parser("branch-config", help="view/update per-project branch "
                                                "naming templates")
    bc_sub = bc_p.add_subparsers(dest="branch_config_cmd", required=True)

    p = bc_sub.add_parser(
        "show", help="show the effective branch naming templates",
        description="Print the effective branch naming templates and max "
                    "length -- project-configured overrides merged over the "
                    "built-in defaults -- noting which are which.",
        epilog="examples:\n  omn-agent branch-config show -t ./my-repo",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    _target_arg(p, positional=False)
    p.set_defaults(fn=branch_config.cmd_branch_config_show)

    p = bc_sub.add_parser(
        "set", help="update branch naming templates",
        description="Validate and persist branch naming templates. Only the "
                    "options you pass are changed; anything else already "
                    "configured (or defaulted) is left as-is. Tokens: "
                    "{ticket_id} (required), {short_description}, "
                    "{work_type} (both optional).",
        epilog="examples:\n"
               "  omn-agent branch-config set -t ./my-repo "
               "--feature-template 'feature/on-{ticket_id}-{short_description}'\n"
               "  omn-agent branch-config set -t ./my-repo "
               "--bugfix-template 'bugfix/on-{ticket_id}-{short_description}'\n"
               "  omn-agent branch-config set -t ./my-repo "
               "--template chore='chore/{ticket_id}-{short_description}'\n"
               "  omn-agent branch-config set -t ./my-repo --max-length 60",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    _target_arg(p, positional=False)
    p.add_argument("--feature-template", help="template for the 'feature' work type")
    p.add_argument("--bugfix-template", help="template for the 'bugfix' work type")
    p.add_argument("--template", action="append", default=[],
                   metavar="WORKTYPE=TEMPLATE",
                   help="set a template for any other work type (repeatable)")
    p.add_argument("--max-length", type=int, metavar="N",
                   help="max generated branch name length (default "
                        f"{branch_config.DEFAULT_MAX_LENGTH})")
    p.add_argument("--dry-run", action="store_true", help="validate without writing")
    p.set_defaults(fn=branch_config.cmd_branch_config_set)

    p = bc_sub.add_parser(
        "preview", help="preview the branch name a ticket would get",
        description="Render the branch name that would be generated for a "
                    "planned ticket, without creating or switching any "
                    "branch (equivalent to 'omn-agent branch KEY --dry-run', "
                    "but never requires a git working tree).",
        epilog="examples:\n"
               "  omn-agent branch-config preview PROJ-123 -t ./my-repo\n"
               "  omn-agent branch-config preview PROJ-123 -t ./my-repo "
               "--work-type bugfix",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("key", metavar="KEY", help="ticket key of a planned task")
    _target_arg(p, positional=False)
    p.add_argument("--work-type", metavar="WORKTYPE",
                   help="override the routed work type")
    p.set_defaults(fn=branch_config.cmd_branch_config_preview)

    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    _resolve_target_arg(args)
    try:
        return int(args.fn(args))
    except OmnError as exc:
        label = "INVALID TARGET" if exc.exit_code == ExitCode.INVALID_TARGET else "ERROR"
        print(f"  [{label:<14}] {exc.message}", file=sys.stderr)
        if exc.hint:
            print(f"  {'':<17} hint: {exc.hint}", file=sys.stderr)
        print(f"RESULT: {label}", file=sys.stderr)
        return int(exc.exit_code)
    except PermissionError as exc:
        print(f"  [ERROR         ] permission denied: {exc}", file=sys.stderr)
        print("RESULT: ERROR", file=sys.stderr)
        return int(ExitCode.PERMISSION_DENIED)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return int(ExitCode.UNEXPECTED)
    except Exception:
        print("  [ERROR         ] unexpected error:", file=sys.stderr)
        traceback.print_exc()
        print("RESULT: ERROR", file=sys.stderr)
        return int(ExitCode.UNEXPECTED)


if __name__ == "__main__":
    sys.exit(main())
