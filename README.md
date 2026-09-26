# omn-agent

Bootstrap, installer, and orchestration CLI for the **Omn-Agent AI Engineering
Framework**. It installs the framework (the tree under `.claude/` in this
repository) into any target repository as `.omn-agent/`, keeps that
installation healthy and upgradable without ever destroying your files, and
connects the framework to Jira so tickets become actionable, approval-gated
work for the framework's agents.

Python 3.10+. The `omn_agent` CLI package itself uses the Python standard
library only; the framework runtime files it installs (and runs with the same
interpreter) import PyYAML, so the distribution declares `pyyaml` as a
dependency and `pip install` pulls it automatically. `validate` and `doctor`
check the Python environment they run in — run them with the same interpreter
that runs the framework.

```bash
pip install -e .        # provides the `omn-agent` console command
# or run without installing:
python -m omn_agent --help
```

## Commands

| Command | What it does | Writes |
|---|---|---|
| `omn-agent init <repo>` | Create the `.omn-agent/` directory layout | layout + manifest |
| `omn-agent install <repo>` | Install or repair the framework payload, then validate | managed files |
| `omn-agent validate <repo>` | Check layout, manifest, registries, entrypoints, validators, context, symlinks | nothing |
| `omn-agent doctor <repo>` | Validate + local-drift and health diagnosis | nothing |
| `omn-agent status <repo>` | Installation, ticket, task, and run summary | nothing |
| `omn-agent upgrade <repo>` | Update framework-managed files only | managed files |
| `omn-agent mcp init jira -t <repo>` | Guided Jira setup: tests the connection, auto-detects project keys, confirms before writing | `config/mcp.json`, `.mcp.json` |
| `omn-agent mcp add jira -t <repo> --base-url ... --project KEY` | Flag-based (scriptable) Jira setup — same result as `mcp init` | `config/mcp.json`, `.mcp.json` |
| `omn-agent tickets sync -t <repo>` | Pull open tickets from configured projects into the inbox | `tickets/inbox/*.json` |
| `omn-agent tickets pull KEY... -t <repo>` | Fetch specific tickets by key | `tickets/inbox/*.json` |
| `omn-agent plan KEY -t <repo>` | Route a ticket onto a framework workflow and render its input document | `tasks/<KEY>/` |
| `omn-agent run KEY -t <repo>` | Drive the installed framework runtime for the task, one approved step at a time | runtime run state |
| `omn-agent run KEY -t <repo> --show [--watch] [--json] [--no-color]` | Read-only: show run status as a colorized phase/step/gate tree (a TTY) or the plain table (piped/`--no-color`/`NO_COLOR`); `--watch` re-renders in place until Ctrl+C; `--json` prints machine-readable state instead | nothing |
| `omn-agent run KEY -t <repo> --demo` | Record the run for an autonomous demo: every event, dispatch prompt, agent result, validation, gate decision, and (with the optional host hook) tool call becomes a millisecond-stamped marker under `runs/<run>/demo/` | `runs/<run>/demo/` |
| `framework_runtime.py demo --run-id <run> --record-start` / `--record-stop --build` | Film the Claude Desktop window (OBS Studio when its WebSocket server is on, else ffmpeg) and cut it into `presentation_demo.mp4`: the markers' timestamps give every beat a frame, so waits are condensed with a stated speed factor and each beat is captioned. A run that completes while filming cuts itself | `runs/<run>/demo/capture/`, `presentation_demo.mp4` |
| `omn-agent update KEY -t <repo>` | One-command change-request loop for a ticket that changed in Jira: refresh the ticket, re-plan, carry the change into the run (a changed input is a new run: the previous run is archived to the task's runHistory and a fresh one materialized), drive every phase it can, then push the result to the PR; resumable | `tickets/inbox/<KEY>.json`, `tasks/<KEY>/`, runtime run state, gate decisions, pushed branch, PR |
| `omn-agent quality-scan [NAME] -t <repo>` | One-command repository quality scan: render the scan scope from flags (or `--scope-file`), record it as task `QS-<NAME>`, materialize and dispatch the `code-quality-scan` run to the reviewer agent, ingest the validated review package on re-run, and stop at the Quality Handoff Gate for a human tech lead; resumable, no source change ever | `tasks/QS-<NAME>/`, runtime run state |
| `omn-agent branch KEY -t <repo>` | Create the ticket's feature branch (project-templated name) off main/master inside its own isolated worktree at `.worktrees/<ticket>-<work-type>/` | git branch + worktree, `tasks/<KEY>/task-plan.json` |
| `omn-agent pr precheck KEY -t <repo>` | Worktree guard + quality gate (tests, run inside the task's worktree), no PR opened | `tasks/<KEY>/task-plan.json` |
| `omn-agent pr create KEY -t <repo>` | Pre-PR checks, push, then open a PR (via `gh`, or an actionable fallback) | pushed branch, PR, `tasks/<KEY>/task-plan.json` |
| `omn-agent pr fix-comments KEY -t <repo>` | One-command review-comment loop: collect PR feedback (via `gh`), reject the pending gate with it, re-dispatch the fix; re-run after the subagent to verify, close the gate, and push | gate decisions, `tasks/<KEY>/fix-comments/`, pushed branch, `tasks/<KEY>/task-plan.json` |
| `omn-agent branch-config show -t <repo>` | Show effective branch naming templates (project overrides + defaults) | nothing |
| `omn-agent branch-config set -t <repo> --feature-template ...` | Validate and persist branch naming templates | `config/branch-naming.json` |
| `omn-agent branch-config preview KEY -t <repo>` | Preview the branch name a ticket would get, no git side effects | nothing |

`install`, `upgrade`, `init`, `mcp add jira`, `plan`, and `update` support
`--dry-run` (preview everything, write nothing, exit 5).

## Overwrite safety

Every file is classified against the install manifest
(`.omn-agent/bootstrap/install-manifest.json`, content hashes as installed)
before anything is written:

- **missing** → created
- **identical to the payload** → untouched
- **matches its recorded install hash** → framework-managed and unmodified → safe to update
- **differs from its recorded hash** → *you* changed it → skipped with a warning
- **not in the manifest at all** → *yours* → never touched by any mode

`--force` only widens the third and fourth cases at framework payload paths,
and always leaves a `.omn-bak` backup. `context/` and `memory/` are seeded
once and then owned by the project. If `.omn-agent` exists but wasn't written
by this tool (or its manifest is unreadable / from a newer tool), the command
stops with exit 4 and changes nothing. Install and upgrade never report
success without running full validation.

## Jira → tasks → approved execution

```bash
export JIRA_EMAIL=you@example.com JIRA_API_TOKEN=...   # never written to disk
omn-agent mcp init jira -t ./my-repo   # guided: connection test, project pick-list, confirm
# scriptable alternative, same result:
#   omn-agent mcp add jira -t ./my-repo --base-url team.atlassian.net --project PROJ
omn-agent tickets sync -t ./my-repo
omn-agent plan PROJ-42 -t ./my-repo        # Bug→fix-bug, refactor→refactor, spike→investigate, else implement-feature
omn-agent run PROJ-42 -t ./my-repo         # materialize the runtime run (asks for approval)
omn-agent run PROJ-42 -t ./my-repo         # read-only: shows the next actionable step
omn-agent run PROJ-42 -t ./my-repo --dispatch --phase scope-and-acceptance --approve
omn-agent branch PROJ-42 -t ./my-repo      # feature/proj-42-<slug> off main, in .worktrees/proj-42-feature/
omn-agent run PROJ-42 -t ./my-repo --dispatch --phase implementation --approve
# ... implement and commit inside .worktrees/proj-42-feature/ ...
omn-agent pr create PROJ-42 -t ./my-repo   # pre-PR checks, push, open the PR

# the ticket changed in Jira? one resumable command carries the change to the PR:
omn-agent update PROJ-42 -t ./my-repo --approve --gate-policy auto
```

## One-command code quality scan

The framework payload ships a `/quality-scan` command (workflow
`code-quality-scan`): a single-pass, evidence-based review of a bounded
repository scope for duplicated logic, dead code, over-abstraction,
generated low-value noise, legacy drift, and review-load hotspots. It
**reviews and stops** — no source change, no auto-fix, no merge decision.
The single `repository-quality-scan` phase is owned by the reviewer agent,
emits a validated `review-package.md` under junk-detection categories
(`duplication`, `dead-code`, `over-abstraction`, `generated-noise`,
`legacy-drift`, `reviewability`, each finding carrying a stated confidence
and ambiguous cases recorded as open questions), and terminates at the
**Quality Handoff Gate**, decided by a human tech lead.

`omn-agent quality-scan` drives the whole flow as one resumable CLI command:

```bash
omn-agent quality-scan backend -t ./my-repo \
    --paths src/api,src/core --exclude vendor/ \
    --context 'pre-merge sweep for PR #42' --risk-threshold high --approve
# -> renders the scan scope, records task QS-BACKEND, materializes the run,
#    dispatches the repository-quality-scan phase to the reviewer agent, and
#    stops while the host runs the dispatched subagent

# ... host runs the reviewer subagent named in the dispatch output ...

omn-agent quality-scan backend -t ./my-repo --approve
# -> resume: ingests and validates the review package, then stops at the
#    Quality Handoff Gate with the package as the deliverable

omn-agent run QS-BACKEND -t ./my-repo --gate "Quality Handoff Gate" \
    --decision approve --owner-role omn-tech-lead \
    --rationale "package accepted as review of record" --approve
# -> the human tech lead's decision, recorded like any other gate
```

The scan is a normal task (`tasks/QS-<NAME>/`), so `omn-agent run QS-<NAME>
--show/--watch/--report` work unchanged. A re-run with a changed scope
archives the previous run to `runHistory` and materializes a new one — the
same "a changed input is a new run" rule `update` follows — and side-effecting
steps require approval exactly like `omn-agent run`. Inside Claude Code,
`/quality-scan <scope>` is the same flow. See `docs/USER-GUIDE.md` §4.7.

## Branch and Pull Request lifecycle

`omn-agent branch KEY` binds a task to a feature branch named per the
project's **branch naming templates** (see below; defaults to
`feature/<ticket>-<slug>` / `bugfix/<ticket>-<slug>`, e.g.
`feature/proj-42-add-login-timeout`), created off `main` (falling back to
`master`, or `--base`) **inside the task's own git worktree** at
`.worktrees/<ticket>-<work-type>/`. The shared main checkout is never
switched. The work type used to pick a template is derived from the task's
routed command (`implement`→`feature`, `bugfix`→`bugfix`,
`refactor`→`refactor`, `investigate`→`chore`) unless overridden with
`--type`. Re-running it reuses the already-bound worktree -- the same task
never gets a second one. It fails outright -- never silently substitutes
another branch or directory -- if an explicit `--base` doesn't exist, if a
configured remote's fetch fails, if the task's branch is already checked out
in another worktree (or the main tree), or if an unregistered directory
occupies the worktree path (`--force` deletes and recreates it). A dirty
main checkout only draws a warning: the worktree is created fresh off the
base branch, so uncommitted changes in the shared tree never leak into it.

### How concurrent work is isolated

Every task lifecycle (implement, bugfix, refactor, investigate, ...) owns
exactly one worktree, deterministically located at
`.worktrees/<ticket>-<work-type>/` and recorded -- with its branch, base,
and status -- as `worktree` in `tasks/<KEY>/task-plan.json`. Because each
worktree is a separate working directory with its own checkout, any number
of tasks can run concurrently: no branch switching, no shared dirty state,
no collisions. Every later step (`run --dispatch --phase implementation`,
`pr precheck`, `pr create`) resolves the task's worktree from that recorded
mapping -- never from the current working directory -- and verifies it is on
the bound branch before proceeding. `.worktrees/` self-ignores via a
generated `.gitignore`, so task worktrees never dirty the main checkout.

**Automatic cleanup:** `tickets sync` and `tickets pull` release the
worktree of any task whose ticket has closed (Done/Closed/Resolved/
Cancelled/Won't Do...) -- sync re-fetches each bound ticket by key, since
its default JQL hides closed tickets. The branch is kept; only the checkout
directory and its registration go, and the task records
`worktree.status: removed` with when and why. A worktree still holding
uncommitted work is never force-deleted -- it is kept with a loud warning
naming the manual command (`git worktree remove <path>`), which also removes
any finished worktree by hand.

### Branch naming templates

Each project defines its own branch naming convention once, at
`omn-agent init` time, persisted at `.omn-agent/config/branch-naming.json`
(project-local, seeded once and then owned by the project -- exactly like
`context/` and `memory/`):

```bash
omn-agent init ./my-repo \
  --feature-branch-template 'feature/on-{ticket_id}-{short_description}' \
  --bugfix-branch-template 'bugfix/on-{ticket_id}-{short_description}' \
  --branch-max-length 60
# on an interactive terminal, omitting both template flags prompts for them
# instead (Enter accepts the built-in default)
```

**Tokens:** `{ticket_id}` (required in every template), `{short_description}`,
and the optional `{work_type}`. **Normalization**, applied to the whole
rendered name: lowercased, anything outside `[a-z0-9_-]` becomes `-`,
duplicate `-` collapse to one, leading/trailing `-` are trimmed, per
`/`-separated segment (so template-authored hierarchy like `feature/...`
survives) -- then truncated to `--max-length` (default 80). **Validation**,
enforced at save time with a clear error and nothing written on failure: the
template must contain `{ticket_id}`, use no token outside the three known
ones, have balanced braces, and render to a name `git check-ref-format`
accepts.

View or change templates after init without touching git:

```bash
omn-agent branch-config show -t ./my-repo
omn-agent branch-config set -t ./my-repo --feature-template '...'   # only the
                                          # passed option changes; others are untouched
omn-agent branch-config set -t ./my-repo --template chore='chore/{ticket_id}-{short_description}'
omn-agent branch-config preview PROJ-42 -t ./my-repo   # resolved name, no branch created
```

**Backward compatibility:** an installation from before this feature existed
(or one that only ever ran `install`, never `init`) has no
`branch-naming.json` at all -- `load_config` returns the exact same built-in
defaults it would otherwise have written, so `omn-agent branch` keeps working
unchanged. Nothing is migrated automatically; run `branch-config set` (or a
fresh `init`) whenever you want project-specific templates.

Once a branch is bound, `omn-agent run KEY --dispatch --phase implementation`
refuses to proceed unless the task's worktree exists, is registered with git,
and is checked out on the bound branch (never `main`/`master`) -- a missing,
hijacked, or protected worktree is blocked with a clear message rather than
silently allowed, and the dispatch output names the exact worktree directory
the implementation must happen in.

`omn-agent pr precheck KEY` verifies the branch guard and runs a test/validation
command (`--test-cmd`, or auto-detected: `tests/` → `unittest`, `pyproject.toml`
+ `pytest` → `pytest`, `package.json` → `npm test`; none found → a recorded
warning, not a failure), so it can be run standalone as a quality gate.
`omn-agent pr create KEY` runs the same checks (unless `--skip-checks`), pushes
the branch, and opens a PR with a standardized `type(KEY): summary` title and a
body carrying the ticket link, changes, testing result, and a `Closes KEY`
trailer -- via the `gh` CLI when available. If `gh` is missing or
unauthenticated, it fails safely with the exact next command to run
(`gh auth login`, or an install link) plus a ready-made GitHub compare URL as a
manual fallback, instead of guessing or crashing.

`omn-agent pr fix-comments KEY` closes the loop after the PR collects review
feedback (human comments and bot findings such as Sonar). One invocation
collects the feedback via `gh`, rejects the gate awaiting decision with the
findings as the rejection rationale (the runtime classifies that as a
rollback and re-dispatches the fix phase carrying the feedback forward), and
dispatches that phase to its owner agent. After the host has run the
dispatched subagent, re-running the same command ingests the completion,
re-runs the pre-PR checks, approves the gate on that clean evidence, and
pushes the bound branch so the PR updates. The command is resumable (round
state lives in `fixComments` on the task; the collected feedback is recorded
under `tasks/<KEY>/fix-comments/`), a repeated round only picks up comments
newer than the last fixed round, and every side-effecting step goes through
the same approval discipline as `omn-agent run`.

`omn-agent update KEY` is the mirror-image loop for a **ticket that changed
in Jira** (it also works end-to-end for a fresh ticket). One invocation
refreshes the ticket into the inbox (`--no-fetch` skips Jira), re-plans the
task -- an unchanged ticket is a no-op, so re-running is always safe -- and
carries the change into the runtime run: materializing a run when none
exists, rejecting the gate awaiting a decision with the change request as
rationale when a run is in flight (the runtime classifies that as a rollback
and the re-dispatched phase carries the change forward), or archiving the
finished run to `runHistory` and materializing a new one when the previous
run already completed. It then drives the run as far as it can -- dispatching
each eligible phase to its owner agent (auto-binding the feature
branch/worktree before implementation), ingesting completions, and letting
the runtime auto-decide clean-evidence gates per `--gate-policy` -- stopping
only where the host must run a dispatched subagent or a human must decide a
held gate. When the run completes it runs the pre-PR quality gate and pushes
the bound branch, updating the recorded PR or opening one. Round state lives
in `updateFlow` on the task; a delivered, unchanged ticket short-circuits to
"nothing to do".

```bash
omn-agent update PROJ-42 -t ./my-repo --approve --gate-policy auto
# ... host runs the dispatched subagent in .worktrees/proj-42-feature/ ...
omn-agent update PROJ-42 -t ./my-repo --approve --gate-policy auto   # resume: complete, verify, push to the PR
```

Every outcome is recorded on `tasks/<KEY>/task-plan.json` (`branch`,
`prChecks`, `pr`, `fixComments`, `updateFlow`), the same file `run`'s
approvals already live in.

`mcp add jira` stores only environment-variable *names*, never credentials,
and merge-safely registers Atlassian's remote MCP server in the repo's
standard `.mcp.json` so MCP-capable agent hosts can read Jira directly.
`omn-agent run` is a thin wrapper over the installed runtime
(`.omn-agent/runtime/framework_runtime.py`) — orchestration, gates,
validation, and recovery live there. The wrapper adds exactly one thing:
**every side-effecting step (materialize, dispatch, complete, gate) requires
explicit approval** — `--approve` or an interactive yes — is recorded to
`tasks/<KEY>/approvals.jsonl`, and otherwise exits 8 having executed nothing.

### Watching a run

`--show` is always read-only. On an interactive terminal it renders a
colorized phase → step → gate tree with status icons (`✓` done, `▶` running,
`⏳` pending, `⛔` blocked, `↻` retrying, `✗` failed; a legacy console
codepage that can't encode them falls back to ASCII automatically). Piped to
a file or another process, it's the exact same plain table `--show` has
always printed — parsing tools and scripts are unaffected unless you pass a
flag:

```bash
omn-agent run PROJ-42 -t ./my-repo --show                 # tree on a TTY, plain table piped
omn-agent run PROJ-42 -t ./my-repo --show --watch          # re-renders in place until Ctrl+C
omn-agent run PROJ-42 -t ./my-repo --show --watch --interval 5
omn-agent run PROJ-42 -t ./my-repo --show --no-color       # force the plain table on a TTY
omn-agent run PROJ-42 -t ./my-repo --show --json           # machine-readable state instead
```

`--watch` (and the polling `status --compact` it drives underneath) never
dispatches, completes, or decides a gate — every cycle is an independent
read of `.omn-agent/runs/<run-id>/state.json`, so leaving it open while
another actor works the run cannot itself advance or approve anything.
`--no-color` and the standard `NO_COLOR` environment variable both force the
plain table even on a TTY; `--json` composes with `--watch` too, printing one
state document per poll instead of a tree.

## Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | invalid target / repo not found |
| 2 | installation or configuration incomplete |
| 3 | validation failed |
| 4 | incompatible existing state (nothing changed) |
| 5 | dry-run finished (nothing written) |
| 6 | permission denied |
| 7 | unexpected error |
| 8 | approval required (nothing executed) |

## Layout installed into a target repo

```
.omn-agent/
  bootstrap/    generated descriptor + install manifest (do not edit)
  runtime/      framework runtime, state engine, artifact validators   [managed]
  registry/     agent/workflow/skill/template/command registries        [managed]
  config/       runtime configuration + mcp.json + branch-naming.json    [managed]
  templates/  agents/  workflows/  skills/  commands/
  domain-model/  validation/                                            [managed]
  context/  memory/     seeded once, then owned by the project
  reports/  runs/  tickets/  tasks/    operational — never touched by the installer
```

The managed set is the framework's real dependency closure: the runtime's
context slices read `registry/`, `agents/`, `skills/`, `workflows/`,
`templates/`, `domain-model/`, `context/`, and `memory/`, so all of them are
installed even though the runtime itself lives in `runtime/`.

The framework *source* defaults to the `.claude/` tree next to this package;
point `--source` at any framework checkout to install from somewhere else.

## Tests

```bash
python -m unittest discover -s tests
```

Hermetic tests (synthetic framework source, fake Jira transport, no network):
fresh install, idempotent rerun, partial-install repair, dry-run, invalid
targets, validation failure, incompatible-state refusal, modified-file
preservation, forced overwrite with backup, unknown-file safety, seed
ownership, MCP merge safety, ticket sync idempotency, routing, and approval
gating -- plus `tests/test_branch_pr.py`, covering branch bootstrap (naming,
idempotency, dirty-tree/missing-base guardrails), the implementation-phase
branch guard in `run`, and the PR precheck/create lifecycle including the
`gh` missing/unauthenticated fallback paths (a real local git repository and
a local bare "origin", no network) -- and `tests/test_branch_config.py`,
covering branch naming template validation, token rendering, slug
sanitization, work-type routing, fallback defaults, `init`'s flag/prompt
seeding, and `branch-config show/set/preview`. `tests/test_quality_scan.py`
covers the one-command quality scan against a stateful runtime stub: scope
rendering and `--scope-file`, approval gating, dry-run, dispatch/resume/
complete, the held Quality Handoff Gate (and deciding it through `omn-agent
run --gate`), changed-scope run archival with the denied-approval resume
path, and unchanged-scope re-entry.

`tests/test_framework_runtime_render.py` covers the `status` command's
colorized tree/icon renderer and `--json` projection directly against
`.claude/runtime/framework_runtime.py` (the framework's own source, installed
into a target as `.omn-agent/runtime/`): icon/color selection per work-item
status, the ASCII fallback when stdout can't encode the Unicode icons,
`NO_COLOR`/`--no-color`/`--color` precedence, phase/step/gate nesting, the
`--json` schema, and that the default (non-TTY, no flags) path still renders
the original plain table byte for byte. `tests/test_run_show.py` covers
`omn-agent run --show`'s `--watch`/`--json`/`--no-color` in `runner.py`: that
color/no-color is decided from this process's own real stdout and forwarded
to the runtime subprocess (never guessed by the subprocess itself, since
`_invoke`'s output capture hides its real TTY-ness), that `--watch`'s poll
loop only ever calls the read-only `status` command, and the flag-guard that
rejects `--watch`/`--json`/`--no-color` without `--show`. The `--watch` loop
itself is tested with an injected clock and iteration bound, never a real
sleep.

## Continuous integration

`.github/workflows/verify.yml` runs on every pull request and on pushes to the
default branch, on ubuntu and windows, with two surfaces located **by
discovery, never a curated file list**: the unit-test suite above, and every
proof script matching `verify_*.py` under `.claude/runtime/` — each verifier in
its own job on its own runner, so a failing verifier fails CI naming itself and
one verifier's crash or flake (including the timing-sensitive recovery proof)
cannot change any other verifier's result. A verifier passes only when it exits
0 **and** its own `N/N checks passed` summary shows a non-negative verdict.
Adding a `tests/test_*.py` or `verify_*.py` file needs no CI change.

Branch protection binds to four stable check names — renaming any of them is a
contract change:

| Check | Standing |
|---|---|
| `tests-ubuntu` | required from day one |
| `tests-windows` | advisory week 1, required after the flip |
| `verifiers-ubuntu-ok` | advisory week 1, required after the flip |
| `verifiers-windows-ok` | advisory week 1, required after the flip |

Advisory means *absent from the required-checks list* (failures still show
red); `continue-on-error` is never used. The flip is a settings-only change,
enacted only after a default-branch run shows `verify_self_hosting.py` passing
(the pre-existing orphan run directories must be cleaned first). The workflow
never sets `NO_COLOR`, and new verifiers must be self-contained: runnable
alone, with no arguments, in any order.

`docs/user-guide.html` is generated from `docs/USER-GUIDE.md`: edit the
Markdown, then run `python tools/render_user_guide.py` to regenerate the
HTML. The `tests` job also runs `python tools/render_user_guide.py --check`,
which fails a pull request whose HTML is stale and prints the regeneration
command above. A change made directly to `docs/user-guide.html` is discarded
by the next regeneration.
