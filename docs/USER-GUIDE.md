# Omn-Agent Handbook

*The user guide for teams working with the Omn-Agent AI Engineering Framework.*

Omn-Agent turns AI-assisted development from "chat with a model" into a governed
delivery process. Work travels through **workflows** made of **phases**; each
phase is owned by a **specialized agent** that produces a validated **artifact**;
progress is held at **human gates** until someone accountable approves. The
`omn-agent` CLI installs the framework into your repository, keeps it healthy,
and connects it to Jira so tickets become executable, approval-gated work.

---

## 1. The mental model {#model}

Everything in the framework follows one chain:

```chain
command  →  workflow  →  phase  →  owner agent  →  artifact ✓  →  **human gate**  →  next phase
```

- **Commands** (`/implement`, `/bugfix`, …) are how you ask for work. Each routes
  to exactly one workflow.
- **Workflows** (implement-feature, fix-bug, refactor, …) define an ordered set
  of phases with explicit dependencies.
- **Phases** are owned by one agent each — a product owner agent scopes, a
  planner plans, an architect designs, a developer implements, a reviewer
  reviews, QA validates.
- **Artifacts** are the phase outputs (scope-definition.md, execution-plan.md,
  technical-design.md, implementation-report.md, …). Every artifact type has a
  validator; a phase does not complete until its artifact passes.
- **Gates** are human decision points between phases. A gate names its owner
  roles, and the agent that produced the evidence may never approve its own
  gate.
- **A run** is one request travelling through one workflow. Run state lives in
  `.omn-agent/runs/` — state table, event stream, failure envelopes, recovery
  ledger. Nothing is silently skipped: a phase that cannot execute is *blocked
  with a recorded reason*, never dropped.

## 2. Installation {#install}

**Prerequisites:** Python 3.10+, a target repository (anything with `.git` or a
standard project marker). The `omn-agent` CLI package itself uses the Python
standard library only; the framework runtime files it installs import
**PyYAML**, so the distribution declares `pyyaml` as a dependency and
`pip install` pulls it automatically.

```bash
# from the framework repository
pip install -e .

# install the framework into your repo
omn-agent install ./my-repo

# confirm health
omn-agent validate ./my-repo
omn-agent status ./my-repo
```

`install` copies the framework payload into `./my-repo/.omn-agent/`, records a
content-hash manifest of every file it wrote, and **validates before claiming
success** — layout, registries, runtime entrypoints (they must compile and their
module-top-level imports must resolve),
validator references, required context, **every context-slice member the
runtime can demand at dispatch time**, broken symlinks. Re-running `install`
on a healthy repo is a no-op; on a damaged one it repairs exactly what is
missing.

Install also seeds a **`dependency-map.md`** derived from your repository's own
manifests (`.csproj` project references, `package.json` local dependencies,
`pyproject.toml` dependencies) — the boundary record several phases read when
they assess a change's blast radius. When no manifest is detectable it seeds an
honest placeholder telling you to fill it in. Regenerate it any time with:

```bash
omn-agent context generate dependency-map -t ./my-repo --force
```

If you are installing from a different framework checkout, pass
`--source <path>`. Every write-capable command accepts `--dry-run` to preview
the full plan without touching anything (exits with code 5). Every command that
takes a target accepts it uniformly as `-t`/`--target`; the historically
positional ones (`init`, `install`, `upgrade`, `validate`, `doctor`, `status`)
still accept the bare positional too, and the flag wins when both are given.

### What gets installed

| Directory | Contents | Ownership |
|---|---|---|
| `.omn-agent/bootstrap/` | descriptor + install manifest | generated — do not edit |
| `.omn-agent/runtime/` | workflow engine, state machine, artifact validators | framework-managed |
| `.omn-agent/registry/` | agent / workflow / skill / template / command registries | framework-managed |
| `.omn-agent/agents/` `workflows/` `templates/` `skills/` `commands/` `config/` `domain-model/` `validation/` | agent contracts, workflow specs, artifact templates, playbooks | framework-managed |
| `.omn-agent/context/` `memory/` `dependency-map.md` | product, technical & release context; architecture memory; the module dependency map | **yours** — seeded once, never overwritten |
| `.omn-agent/reports/` `runs/` `tickets/` `tasks/` | operational output | **yours** — never touched by the installer |

## 3. Two ways to work {#work}

### A. Inside Claude Code — slash commands

With the framework installed, ask for work with a command. Each command routes
to its workflow and the agents take over, phase by phase:

| Command | Workflow | Starts with | Lead agents |
|---|---|---|---|
| `/implement` | implement-feature | scope & acceptance | product owner → planner → architect → developer |
| `/bugfix` | fix-bug | triage & impact | bug analyst → developer → QA |
| `/refactor` | refactor | scope, invariants & risk profile | architect → developer → QA |
| `/investigate` | investigate | problem framing | business analyst → context agent → tech lead |
| `/research` | research | research framing | business analyst → context agent → tech lead |
| `/review` | review-pull-request | code quality review | reviewer → architect → QA → tech lead |
| `/quality-scan` | code-quality-scan | repository quality scan | reviewer → tech lead (human gate) |
| `/release` | release | readiness assessment | tech lead → QA → orchestrator |
| `/document` | implement-feature (docs phase) | documentation & handoff | documentation agent |
| `/test` | review-pull-request (test phase) | test-risk validation | QA |

[Section 4](#flows) walks each of these flows end to end — phases, owners, artifacts,
and the gates you'll approve.

### B. From the terminal — tickets in, gated runs out

```bash
# one-time: connect Jira (no secrets are ever written to disk)
export JIRA_EMAIL=you@example.com
export JIRA_API_TOKEN=<your Atlassian API token>
omn-agent mcp init jira -t ./my-repo
```

`mcp init jira` walks you through setup: it validates the repo, accepts the
site address with or without `https://`, tests the connection ("Connected to
Jira as …"), shows a numbered pick-list of the projects your account can see —
so you never need to know project keys — and asks for confirmation before
writing anything. With no credentials exported it still works; you just type
the project keys yourself. For scripts and CI, the flag-based form gives the
same result: `omn-agent mcp add jira -t ./my-repo --base-url
yourteam.atlassian.net --project PROJ`.

```bash
# pull work
omn-agent tickets sync -t ./my-repo          # open tickets from your projects
omn-agent tickets pull PROJ-42 -t ./my-repo  # or one specific ticket

# route a ticket onto a workflow
omn-agent plan PROJ-42 -t ./my-repo
```

Besides refreshing the inbox, `sync` and `pull` also release the isolated
worktree of any task whose ticket has closed since the last refresh — see
"Worktrees clean themselves up" in section 5a.

`plan` classifies the ticket deterministically — **Bug → fix-bug**, *refactor /
tech-debt* keywords → refactor, *spike / research* → investigate, everything
else → implement-feature — renders the runtime input document from the ticket
(`.omn-agent/tasks/PROJ-42/input.md`), and records the routing. Override with
`--command bugfix|implement|refactor|investigate` if the automatic call is
wrong. If the ticket has no acceptance criteria, the input document says so
explicitly and the Scope Gate is where they get defined.

> **MCP**
> `mcp add jira` also registers Atlassian's remote MCP server in your repo's
> `.mcp.json` (merge-safe — existing entries are preserved), so MCP-capable agent
> hosts can read Jira directly. The connector config stores only
> environment-variable *names*, never credentials.

Jira is not the only ticket source: `omn-agent mcp add msdev --org-url
https://dev.azure.com/yourorg --project <NAME>` connects Azure DevOps
(work-item reads authenticate with a PAT from `$AZURE_DEVOPS_PAT`). And the
whole pull → plan → run → PR pipeline collapses into one resumable command
per ticket: `omn-agent run Jira ON-115 --gate-policy auto --approve` (or
`run MSDev ONN-115 …`) — see
[one command from ticket to PR](#run-e2e).

Not every flow needs a ticket: `omn-agent quality-scan` enters the
code-quality-scan workflow directly from the command line — it renders its
own scope input and records the scan as task `QS-<NAME>`
(section [4.7](#flow-quality-scan)).

## 4. The flows: pick by what you're trying to do {#flows}

Every request enters through exactly one flow. Find yours:

| You want to… | Flow | Command | Section |
|---|---|---|---|
| [Ship a new capability or user story](#flow-implement) | implement-feature | `/implement` | 4.1 |
| [Repair broken behavior](#flow-bugfix) | fix-bug | `/bugfix` | 4.2 |
| [Improve structure without changing behavior](#flow-refactor) | refactor | `/refactor` | 4.3 |
| [Answer a question before committing to build](#flow-investigate) | investigate / research | `/investigate` / `/research` | 4.4 |
| [Judge a pull request](#flow-review) | review-pull-request | `/review` | 4.5 |
| [Ship a release candidate](#flow-release) | release | `/release` | 4.6 |
| [Find code junk & technical debt, evidence-first](#flow-quality-scan) | code-quality-scan | `/quality-scan` | 4.7 |

All flows share the same run mechanics — materialize, dispatch, complete,
gate ([section 5](#run)) — but differ in their phases, artifacts, and who approves.
Where a phase shows no gate, the run moves straight on once its artifact
validates. Where a gate lists two roles, remember the Producer Exclusion
Rule: the agent that produced the evidence never decides its own gate.

### 4.1 Implement a feature — `/implement` {#flow-implement}

For new capabilities, user stories, and enhancements. The longest flow:
scope is agreed before planning, design before code, review before
verification.

| # | Phase | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | scope-and-acceptance | product owner | scope-definition.md | Scope Gate (PO, BA) |
| 2 | execution-planning | planner | execution-plan.md | Planning Gate (tech lead, orchestrator) |
| 3 | solution-design-and-risk-assessment | architect | technical-design.md | Design Gate (architect, tech lead) |
| 4 | implementation | developer | implementation-report.md | — |
| 5 | quality-review | reviewer | review-package.md | Review Gate (reviewer, QA), then Verification Gate (QA) |
| 6 | documentation-and-release-handoff | documentation | release-note.md | Closure Gate (orchestrator, docs) |

The ticket-driven sequence, end to end:

```bash
omn-agent plan PROJ-42 -t ./my-repo      # routes the ticket to implement-feature
omn-agent run  PROJ-42 -t ./my-repo      # materialize the run
# phases 1-3: dispatch -> agent produces the artifact -> complete -> approve the gate
omn-agent branch PROJ-42 -t ./my-repo    # before implementation: branch + isolated worktree
# phase 4: implementation happens inside .worktrees/proj-42-feature/
# phases 5-6: review, verification, docs -- then:
omn-agent pr create PROJ-42 -t ./my-repo # checks, push, open the PR
```

**Enter with:** an agreed feature request. A ticket with no acceptance
criteria is fine — the Scope Gate is where they get written down.
**Done when:** the Closure Gate approves — acceptance criteria verified,
docs and release notes updated, PR open for final review on GitHub.

**Filming it:** add `--demo` to the first `run` (or to `/implement`), start the recording,
and the run films itself and cuts a narrated presentation video from the real screen
recording when the Closure Gate approves — see section 5g.

### 4.2 Fix a bug — `/bugfix` {#flow-bugfix}

For observable defects with business impact. Evidence-first: nothing is
changed until the failure is reproduced and traced to its cause.

| # | Phase | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | triage-and-impact | bug analyst | bug-analysis.md | Triage Gate (bug analyst, tech lead) |
| 2 | root-cause-analysis | bug analyst | bug-analysis.md (updated) | — |
| 3 | fix-implementation | developer | implementation-report.md | Fix Gate (reviewer) |
| 4 | regression-validation | QA | validation-report.md | Verification Gate (QA, reviewer) |
| 5 | closure-and-communication | orchestrator | orchestration-result.md | Closure Gate (orchestrator, docs) |

Same terminal sequence as 4.1 — `plan` routes Bug-type tickets here
automatically, and the branch is named `bugfix/<ticket>-<slug>`.

**Enter with:** a defect report with an observable symptom and reproduction
context (or equivalent diagnostic evidence).
**Done when:** the defect no longer reproduces, the root cause is documented
with evidence, and a regression test covers the failure path.

### 4.3 Refactor — `/refactor` {#flow-refactor}

For structural improvement where behavior must not change. Distinctive
shape: behavioral invariants are declared up front, and QA builds the
safety net *before* any code moves.

| # | Phase | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | scope-invariants-and-risk-profile | architect | technical-design.md | Invariant Gate (architect, tech lead) |
| 2 | safety-net-establishment | QA | validation-report.md | — |
| 3 | refactor-implementation | developer | implementation-report.md | Implementation Gate (reviewer) |
| 4 | behavioral-validation | QA | validation-report.md | Regression Gate (QA, reviewer) |
| 5 | closure-and-debt-record | orchestrator | orchestration-result.md | Closure Gate (orchestrator, docs) |

Same terminal sequence as 4.1; *refactor / tech-debt* keywords route here,
and the branch is named `refactor/<ticket>-<slug>`.

**Enter with:** a defined refactor scope, explicitly documented behavioral
invariants, and baseline tests or metrics.
**Done when:** invariants are proven unchanged, quality metrics improved or
within accepted limits, and the technical-debt delta is recorded with
follow-ups.

### 4.4 Investigate & research — `/investigate` / `/research` {#flow-investigate}

For questions that need an evidence-backed answer before anyone commits to
building. **No code, no branch, no PR** — the deliverable is a
recommendation the decision owner can act on. The two flows are twins:
`/investigate` targets a concrete problem or decision; `/research` explores
a broader option space.

| # | Phase (investigate / research) | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | problem-framing / research-framing | business analyst | requirement-framing.md | Framing Gate (BA, PO) |
| 2 | technical-discovery / technical-validation | context agent | investigation-report.md | Technical Gate (context agent, architect) |
| 3 | option-analysis / option-synthesis | tech lead | technical-recommendation.md | — |
| 4 | recommendation / recommendation-draft | tech lead | technical-recommendation.md | Recommendation Gate (tech lead, orchestrator) |
| 5 | publication / findings-publication | documentation | release-note.md (findings) | — |

**Enter with:** a question, its decision owner, and the scope, timeline,
and constraints. *Spike / research* ticket keywords route here.
**Done when:** the recommendation is evidence-backed and decision-ready,
with assumptions and risks explicit — the owner can proceed or defer with
rationale.

### 4.5 Review a pull request — `/review` {#flow-review}

For a stable diff that carries a scope summary, a linked requirement, and
test evidence.

| # | Phase | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | code-quality-review | reviewer | review-package.md | Code Quality Gate (reviewer, tech lead) |
| 2 | structural-compliance | architect | review-package.md (architecture & security findings) | Architecture Gate (architect, tech lead) |
| 3 | test-risk-validation | QA | validation-report.md | Verification Gate (QA, reviewer) |
| 4 | documentation-impact | documentation | release-note.md (documentation delta) | — |
| 5 | merge-decision | tech lead | technical-recommendation.md | Merge Gate (tech lead, orchestrator) |

**Done when:** a merge recommendation with a risk summary stands — critical
findings resolved, major findings resolved or formally accepted, test and
documentation coverage sufficient for the scope.

### 4.6 Release — `/release` {#flow-release}

For shipping a frozen release candidate whose implementation, review, and
QA gates are already complete.

| # | Phase | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | readiness-assessment | tech lead | technical-recommendation.md | Readiness Gate (tech lead, QA) |
| 2 | artifact-packaging | reviewer | review-package.md (packaging evidence) | Artifact Gate (reviewer, tech lead) |
| 3 | candidate-validation | QA | validation-report.md | — |
| 4 | deployment-execution | orchestrator | orchestration-result.md | Deployment Gate (orchestrator, tech lead) |
| 5 | communication-and-post-release | documentation | release-note.md + post-release actions | Communication Gate (docs, PO) |

> **Coordination only**
> `deployment-execution` is a *coordination* phase — the orchestrator
> records deployment, monitoring, and rollback state supplied to it; it
> performs no deployment itself.

**Enter with:** a frozen candidate scope and documented deployment and
rollback plans.
**Done when:** deployment is complete with healthy system indicators, no
critical blocker stands unresolved, and stakeholders have the full release
communication.

### 4.7 Scan for code junk — `/quality-scan` {#flow-quality-scan}

For a single-pass technical-debt review of a bounded repository scope:
duplicated logic, dead code, thin wrappers and over-abstraction, generated
low-value noise, legacy drift, and code whose main cost is human review load.
The scan **reviews and stops** — it modifies nothing, fixes nothing, and
decides nothing; its whole lifecycle is one phase ending at a human gate.

| # | Phase | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | repository-quality-scan | reviewer | review-package.md (junk-detection categories) | Quality Handoff Gate (reviewer, **tech lead decides**) |

Findings use the junk-detection category set — `duplication`, `dead-code`,
`over-abstraction`, `generated-noise`, `legacy-drift`, `reviewability` — and
every finding names its file and symbol, the standard it is measured against,
and its stated confidence (`confidence: high|medium|low` opens the finding
text). Anything the evidence cannot settle becomes an **open question**
(`Q-nnn`) for a human to validate, never an asserted claim. Correction
requests arrive prioritized (remove, refactor, split, centralize) as the tech
lead's action list.

**Enter with:** one command. `omn-agent quality-scan` renders the
`quality-scan-scope` input from your flags (or takes yours verbatim with
`--scope-file`), records the scan as task `QS-<NAME>`, materializes the run,
and dispatches the reviewer — resumable, with the same approval discipline
as `omn-agent run`:

```bash
# one command: scope -> task QS-BACKEND -> run -> dispatch to the reviewer
omn-agent quality-scan backend -t ./my-repo \
    --paths src/api,src/core --exclude vendor/ \
    --context 'pre-merge sweep for PR #42' --risk-threshold high --approve

# ... the host runs the dispatched reviewer subagent ...

# resume: ingest + validate the review package, stop at the human gate
omn-agent quality-scan backend -t ./my-repo --approve

# the tech lead's decision, recorded like any other gate
omn-agent run QS-BACKEND -t ./my-repo --gate "Quality Handoff Gate" \
    --decision approve --owner-role omn-tech-lead \
    --rationale "package accepted as review of record" --approve
```

> **A normal task**
> A scan is a normal task living at `tasks/QS-<NAME>/`, so
> `omn-agent run QS-BACKEND --show / --watch /
> --report` work unchanged, and a re-run with a **changed scope archives the
> previous run** to the task's `runHistory` and materializes a new one — a
> changed input is a new run, exactly as in `omn-agent update`. Prefer writing
> the scope yourself? Pass `--scope-file ./scan-scope.md`. (Inside Claude Code,
> `/quality-scan <scope>` is the same flow.)

**Done when:** the validated review package is held at the Quality Handoff
Gate. The tech lead — a human, by default gate policy — reads it and decides:
accept it as the review of record, route the correction requests as cleanup
work (`/refactor` for structure, `/bugfix` for defects it uncovered), or
reject it back for a re-scan. The verdict vocabulary maps naturally:
`approve` = no material junk, `approve-with-corrections` = cleanup
recommended, `reject` = cleanup required before further review or merge.

## 5. Driving a run {#run}

```bash
omn-agent run PROJ-42 -t ./my-repo                 # step 1: materialize the run
omn-agent run PROJ-42 -t ./my-repo                 # read-only: shows the next step
omn-agent run PROJ-42 -t ./my-repo --dispatch --phase scope-and-acceptance
omn-agent run PROJ-42 -t ./my-repo --complete --phase scope-and-acceptance
omn-agent run PROJ-42 -t ./my-repo --gate "Scope Gate" --decision approve \
    --owner-role omn-product-owner --rationale "AC agreed with stakeholder"
omn-agent run PROJ-42 -t ./my-repo --show          # read-only: full state table
omn-agent run PROJ-42 -t ./my-repo --show --watch  # read-only: live view, re-renders until Ctrl+C
omn-agent run PROJ-42 -t ./my-repo --report        # read-only: who did what, when
```

Once the run reaches the `implementation` phase, branching becomes part of
the sequence -- see section 5a. Gate decisions are human by default; a team
that wants clean, low-risk gates decided by the runtime itself opts in with
the gate policy -- see section 5c. When the run completes, the **final
report** is printed automatically and saved -- see section 5d. And while
agents are working, you can
[watch the run live in a second terminal](#live-view) -- see section 5e.

## 5a. Branch and Pull Request lifecycle

The full chain from ticket to review is:

```chain
Jira → Plan → Branch *(worktree)* → Implement → Validate → Push → PR → **Review**
```

```bash
omn-agent branch PROJ-42 -t ./my-repo
# -> creates feature/proj-42-<slug> (or your project's own template -- see
#    5b), off main (or --base), inside the task's own isolated worktree at
#    .worktrees/proj-42-feature/, and binds both to the task. The main
#    checkout is never switched.

omn-agent run PROJ-42 -t ./my-repo --dispatch --phase implementation --approve
# ... the developer agent implements inside .worktrees/proj-42-feature/
#     (the dispatch output names the exact directory), with test coverage ...
omn-agent run PROJ-42 -t ./my-repo --complete --phase implementation --approve

omn-agent pr precheck PROJ-42 -t ./my-repo         # optional: checks only, no PR
omn-agent pr create PROJ-42 -t ./my-repo           # checks, push, open the PR
omn-agent pr fix-comments PROJ-42 -t ./my-repo     # later: resolve the PR's review comments (see the rework loop)
omn-agent update PROJ-42 -t ./my-repo              # later: the ticket changed in Jira? carry the change to the PR (see the rework loop)
```

**`omn-agent branch KEY`** names the branch per the project's branch naming
templates (section 5b; defaults to `feature/<ticket>-<slug>` /
`bugfix/<ticket>-<slug>`, fully lowercased). The work type used to pick a
template comes from the task's routed command unless overridden with
`--type`:

| Routed command | Work type |
|---|---|
| `implement` | `feature` |
| `bugfix` | `bugfix` |
| `refactor` | `refactor` |
| `investigate` | `chore` |

It is created off the project's configured **default base** (see below),
falling back to `main` then `master`, or an explicit `--base` (which must
already exist -- an unknown `--base` fails rather than silently falling back).

> **Worktree isolation**
> **Each task gets its own worktree.** The branch is checked out in an
> isolated git worktree at `.worktrees/<ticket>-<work-type>/` -- a
> deterministic path per task identity, recorded (path, branch, base, status)
> as `worktree` in `tasks/<KEY>/task-plan.json`. Because every task has its own
> working directory, concurrent tasks never collide: no branch switching in
> the shared checkout, no dirty-tree conflicts between tasks. Re-running the
> command for the same task reuses its existing worktree -- the same task never
> gets a second one. `.worktrees/` self-ignores via a generated `.gitignore`.

Guardrails:

- a **dirty main checkout** only draws a warning (`B-DIRTY-MAIN`) -- the
  worktree is created fresh off the base branch, so uncommitted changes in
  the shared tree never leak into task work;
- the task's **branch already checked out elsewhere** (another worktree, or
  the main tree), the **worktree path registered to a different branch**, or
  an **unregistered directory occupying the path** each fail with the exact
  command that resolves them (`--force` deletes and recreates only that last,
  unregistered-directory case);
- a **missing base branch**, or a **fetch that fails** against a configured
  remote, blocks it outright -- never silently substituted;
- the resolved base's **tip commit (hash, date, subject) is always printed**
  (`B-BASE-TIP`), so a stale base is visible before anything is created;
- when the base is dramatically behind the repository's most recently active
  branch (default threshold: 100 commits), a **loud warning** (`B-STALE-BASE`)
  states the exact commit count and names the fix -- so branching off an
  abandoned `main` stub in a `develop`-based repo can no longer happen
  silently;
- `--dry-run` previews the branch name, worktree path, and action without
  touching anything.

> **Auto-cleanup**
> **Worktrees clean themselves up when the ticket closes.** Every
> `tickets sync` / `tickets pull` checks the current status of each ticket
> with an active worktree (sync re-fetches them by key -- its default JQL
> hides closed tickets) and releases the worktree of any that turn out closed
> (`T-WT-CLEAN`): the directory and its git registration are removed, the
> branch is kept, and the task records `worktree.status: removed` with the
> reason. A worktree that still holds uncommitted work is kept with a warning
> (`T-WT-DIRTY`) instead of being force-deleted -- inspect it, then
> `git worktree remove <path>` (also the way to remove any worktree by hand).
> Re-running `omn-agent branch KEY` on a released task rebinds it with a
> fresh worktree if work must continue.

> **Branch safety**
> **Per-repo default base.** If your integration branch isn't `main`/`master`,
> set it once instead of passing `--base` on every invocation:
>
> ```json
> // .omn-agent/config/branch-defaults.json
> { "defaultBase": "develop", "divergenceWarningThreshold": 100 }
> ```
>
> An explicit `--base` still wins over the configured default, which wins over
> the `main`/`master` fallback. A missing file keeps today's behavior exactly.

**Implementation only runs in the task's worktree.** Once a branch is bound,
`omn-agent run KEY --dispatch --phase implementation` resolves the task's
recorded worktree -- never the current working directory -- and checks it
exists, is registered with git, and is on the bound branch before
dispatching; an unbound task, a missing or unregistered worktree, a
protected branch, or a mismatched checkout each fail with a message naming
the fix (`omn-agent branch KEY`, or `git -C <worktree> checkout <branch>`).
The dispatch output states the worktree directory all code changes belong in.

**`omn-agent pr precheck KEY`** re-confirms the worktree guard, then runs a
test/validation command *inside the task's worktree* and records the result
on the task. It auto-detects one when `--test-cmd` isn't given: a `tests/`
directory runs
`python -m unittest discover -s tests`, `pyproject.toml` with `pytest`
installed runs `pytest`, `package.json` runs `npm test`. Finding none is a
recorded warning, not a failure -- the gate simply couldn't verify anything.

**`omn-agent pr create KEY`** runs the same checks (skip with
`--skip-checks`, though the worktree guard still applies), pushes the branch
to `origin`, and opens a Pull Request via the GitHub CLI (`gh`) with a
standardized title (`type(KEY): summary`) and body (ticket link, changes,
testing result, a `Closes KEY` trailer). `--base` overrides the task's
recorded base branch; `--draft` opens it as a draft; `--dry-run` previews
without pushing or creating anything.

If `gh` isn't installed or isn't authenticated, `pr create` fails safely with
the exact next step (an install link and `gh auth login`, or just
`gh auth login`) plus a ready-made GitHub compare URL so the PR can still be
opened by hand -- it never crashes or guesses.

Both commands write their outcome onto `tasks/<KEY>/task-plan.json`
(`branch`, `worktree`, `prChecks`, `pr`), alongside the `approvals` that
`run` already records there.

## 5b. Branch naming templates

Every project can define its own branch naming convention once, at
`omn-agent init` time, rather than living with the built-in default. It's
persisted at `.omn-agent/config/branch-naming.json` -- project-local, seeded
once and then owned by the project, exactly like `context/` and `memory/`.

```bash
omn-agent init ./my-repo \
  --feature-branch-template 'feature/on-{ticket_id}-{short_description}' \
  --bugfix-branch-template 'bugfix/on-{ticket_id}-{short_description}' \
  --branch-max-length 60
```

On an interactive terminal, omitting both template flags prompts for them
instead (press Enter to accept the built-in default for either one). Passing
either flag, or running non-interactively (CI), skips the prompt entirely and
uses whatever combination of flags and defaults you gave.

### Token reference

| Token | Required | Meaning |
|---|---|---|
| `{ticket_id}` | yes -- every template must contain it | the task's ticket key, e.g. `PROJ-42` |
| `{short_description}` | no | a slug derived from the ticket summary |
| `{work_type}` | no | the resolved work type itself (`feature`, `bugfix`, or a custom one) |

### Normalization and validation rules

The **whole rendered name** is normalized, per `/`-separated segment (so
template-authored hierarchy like `feature/...` survives instead of being
flattened into one dash-joined blob):

1. lowercased;
2. anything outside `[a-z0-9_-]` (spaces, punctuation, `{`/`}` left over from
   a stray token, …) becomes `-`;
3. duplicate `-` collapse to a single `-`;
4. leading/trailing `-` are trimmed;
5. the result is truncated to `--max-length` (default 80), trimming a
   dangling `-`/`/` left by the cut.

A template is validated **at save time** (`omn-agent init` or
`branch-config set`) -- on failure, a clear error is printed and *nothing is
written*:

- it must contain the `{ticket_id}` token;
- it must use no token outside `{ticket_id}` / `{short_description}` /
  `{work_type}` (an unknown token like `{author}` is rejected by name);
- braces must balance;
- rendering it with sample values and normalizing must produce a name
  `git check-ref-format --branch` accepts.

### Viewing and changing templates later

```bash
omn-agent branch-config show -t ./my-repo
# feature: 'feature/on-{ticket_id}-{short_description}' (project-configured)
# bugfix:  'bugfix/{ticket_id}-{short_description}' (default)

omn-agent branch-config set -t ./my-repo \
  --feature-template 'feature/on-{ticket_id}-{short_description}'
# only --feature-template changes; --bugfix-template, --template, and
# --max-length are all independently optional and leave anything else as-is

omn-agent branch-config set -t ./my-repo \
  --template chore='chore/{ticket_id}-{short_description}'
# adds/updates a template for any work type beyond feature/bugfix

omn-agent branch-config preview PROJ-42 -t ./my-repo
# BC-PREVIEW: PROJ-42 (work type 'feature', template '...') -> feature/on-proj-42-...
# -- resolves the branch name a ticket would get, no git side effects at all
# (equivalent to 'omn-agent branch PROJ-42 --dry-run', which also shows it)
```

`--work-type` on `preview`, and `--type` on `branch` itself, override the
work type routed from the ticket's command -- useful for a one-off branch
that doesn't match the ticket's usual category.

### Migration and backward compatibility

Nothing here is a breaking requirement: an installation with no
`branch-naming.json` at all -- whether it predates this feature or simply
never ran `init` (only `install`, which doesn't write this file) -- resolves
branch names using the exact same built-in defaults the file would otherwise
have contained. There is no migration step to run; `omn-agent branch` and
`omn-agent branch-config preview` work identically with or without a saved
config. Adopt project-specific templates whenever you want to, with
`branch-config set` on an existing installation or a fresh `init` on a new
one.

One behavior did change from the built-in defaults an earlier version of
`omn-agent branch` used: type prefixes are now `feature`/`bugfix` (not
`feat`/`fix`), and the ticket key in a generated name is lowercased along
with everything else. Anyone who wants the old short prefixes back can still
get them explicitly with `--type feat` / `--type fix` (or configure them as
named templates via `branch-config set --template feat=...`).

> **Approval model**
> **Every side-effecting step requires approval.** Materializing a run,
> dispatching a phase, ingesting a completion, and recording a gate decision each
> ask for confirmation on a terminal, or take `--approve` non-interactively.
> Without approval the command exits with code 8 and executes nothing. Every
> approval is recorded — who, when, which step — in
> `.omn-agent/tasks/<KEY>/approvals.jsonl`.

The cycle for each phase:

{.steps}
1. **dispatch** — the runtime leases the phase and emits the agent's invocation
   envelope and dispatch prompt (under `.omn-agent/runs/<run>/states/<phase>/`).
2. The **owner agent executes** (in Claude Code) and produces the phase
   artifact.
3. **complete** — the runtime validates the artifact against its contract;
   pass → transition, fail → recorded failure envelope with a recovery action.
4. **gate** — the named human owner approves or rejects with a rationale.
   The producing agent can never decide its own gate. Under the opt-in gate
   policy (section 5c), the runtime may take this step itself when the
   evidence is unambiguously clean.

### When changes are requested: the rework loop {#rework}

An implemented ticket that comes back with change requests is not a new
run — it's the same run stepping backwards once, with everything recorded.
Which loop you're in depends on where the "no" came from:

- **The validator rejects the artifact** (`--complete` fails). The runtime
  records a failure envelope and schedules a retry within the phase's
  attempt budget. Re-dispatching carries the previous validation findings
  into the agent's prompt, so it repairs against the named failures instead
  of starting blind. Every extra pass shows up in the final report's
  attempts column.
- **A human rejects a gate** (`--gate <name> --decision reject
  --rationale "…"`). A rejection is a classified failure, not just a
  recorded opinion: the runtime writes a failure envelope naming the phase
  whose evidence must be rebuilt, and every successor phase blocks with the
  rejection and rationale visible (`omn-agent run KEY --show` prints
  `<gate> was rejected by <role> (<rationale>)`). The rollback itself is a
  second human decision: the envelope's clearing action states the exact
  `rollback` command, filled in — `python .omn-agent/runtime/framework_runtime.py
  rollback --run-id <run> --gate "<gate>" --target <phase> --owner-role <role>
  --decided-by <who> --rationale "…"` — and a listed owner of the gate (not the
  producing agent) runs it, naming the phase to return to (the gated phase by
  default, or an earlier completed phase such as `implementation`). The runtime
  then *supersedes* the target's completed downstream cone — that phase and
  every completed phase that depends on it, the gated one included: each
  returns to pending as a new attempt under the same idempotency key, its
  previous artifact left untouched at its committed path, and the rejected
  gate is re-armed with the rejection kept in its decision history. While the
  rejection stands, `next` names this rollback command first and offers no
  decision on another gate closing the same phase: approving such a gate
  before the rollback would make the rollback refuse (an approved gate cannot
  be re-armed), leaving a shallower target or a new run as the remedies.
  Re-dispatch the phase and the agent reworks **in the same worktree** against
  the rejection rationale, which rides in its envelope as `prior_rejection` —
  new artifact in an attempt-scoped directory, revalidation, and the same gate
  is decided again by a human (never auto-approved after a rollback).
- **The GitHub PR gets "changes requested".** That review lives outside the
  run, but the task's branch and worktree stay bound in
  `task-plan.json`. `omn-agent pr fix-comments KEY` drives this whole loop
  as [one resumable command](#fix-comments). Or do it by hand: make the fix in
  the task's worktree — re-dispatch the implementation phase if the rework
  should travel through review and verification again — then re-run
  `omn-agent pr precheck KEY` and push: the open PR updates on the same
  branch.
- **The Jira ticket itself changed** — new acceptance criteria, a reworded
  description, a scope tweak. `omn-agent update KEY` drives this whole loop
  as [one resumable command](#update): it refreshes the ticket, re-plans
  the task, rejects the awaiting gate with the change request as rationale
  (the same rollback mechanics as a human rejection), and drives the run
  back to a pushed PR.
- **The ticket was closed, then reopened with changes.** Closing released
  the worktree (branch kept — section 5a). `omn-agent branch KEY` rebinds
  the task to a fresh worktree on the same branch, and work continues where
  the commits left off.

> **Bounded rework**
> Rework is bounded: each phase declares a retry budget, and once its charged
> attempts are spent, `release` refuses to exceed it and `rollback` refuses to
> re-enter the phase — the remaining options are a recovery task that repairs
> the output outside the work item, or a corrected request on a new run.
> A rollback re-entry spends the same budget as a retry, so a third rejection
> of the same phase routes to abort or a new run. Nothing loops silently forever.

### One-command review-comment loop: `pr fix-comments` {#fix-comments}

When the open PR collects reviewer feedback — human review comments and bot
findings such as Sonar — the whole rework loop above is one command:

```bash
omn-agent pr fix-comments PROJ-42 -t ./my-repo --approve
```

The first invocation collects the feedback via `gh` (issue comments, review
bodies, and inline review comments; the PR author's own replies are
excluded), records it under `tasks/<KEY>/fix-comments/`, rejects the gate
currently awaiting a decision with those findings as the rejection
rationale, then authorises the rollback as the same owner role with the
task's fix phase (`implementation`, `fix-implementation`, or
`refactor-implementation`) as the target — the runtime supersedes that phase
and every completed phase up to the gated one, re-arms the gate, and carries
the findings into the fix phase's re-dispatch as `prior_rejection` — and
dispatches that phase to its owner agent. It then stops: the host must run
the dispatched subagent, which makes the fixes in the task's bound worktree.

Re-running the same command afterwards finishes the round: it ingests the
phase completion, re-runs the pre-PR checks (`--test-cmd` supported),
approves the gate on that clean evidence, and pushes the bound branch so
the open PR updates. Reply to and resolve the review threads on GitHub, and
let CI and Sonar re-scan.

> **Resumable**
> The command is resumable at every step — a failed completion, failing
> tests, or a declined approval leave the recorded round state
> (`fixComments` in `task-plan.json`) where it was, and the next invocation
> continues from there. A later round only picks up comments newer than the
> last fixed round, so already-addressed feedback is never re-litigated.
> Side-effecting steps (gate decisions, dispatch, complete, push) require
> approval exactly like `omn-agent run`: `--approve`, or an interactive yes.

### One-command Jira change-request loop: `update` {#update}

When the change comes from Jira rather than the PR — the ticket's
description or acceptance criteria changed after work started — the whole
cycle is one command:

```bash
omn-agent update PROJ-42 -t ./my-repo --approve --gate-policy auto
```

Each invocation performs every step it can, in order:

1. **Refresh** the ticket from Jira into the inbox (`--no-fetch` uses the
   stored copy; a ticket that turns out closed stops the loop). 
2. **Re-plan** the task — `input.md` is regenerated only when the routed
   input actually changed, so an unchanged ticket makes the whole command a
   safe no-op (it reports "nothing to do" once the round is delivered).
3. **Carry the change into the run.** No run yet → materialize one. A run
   is recorded and the input changed — whether it's in flight or already
   completed → the run id is archived to `runHistory` on the task and a new
   run starts from the updated input. The runtime pins every input digest
   at run creation and re-verifies it on every operation, so a regenerated
   `input.md` can never be carried into an existing run: a changed input is
   a new run.
4. **Drive the run**: dispatch each eligible phase to its owner agent
   (auto-binding the feature branch and worktree before the implementation
   phase if `omn-agent branch` was never run), ingest completions, and let
   the runtime auto-decide clean-evidence gates per `--gate-policy`. The
   command stops where the host must run a dispatched subagent, or where a
   gate needs a human (`omn-agent run KEY --gate ...`); re-running continues
   from live state.
5. **Deliver**: when the run completes, the pre-PR quality gate runs
   (`--test-cmd` supported) and the bound branch is pushed — updating the
   recorded PR, or opening one (`--draft`, `--base` supported) when none
   exists.

> **Resumable**
> Round state lives in `updateFlow` on `task-plan.json`; each invocation reads
> it plus live runtime state and performs every step it can, so re-running is
> always safe. Side-effecting steps
> (archiving an in-flight run, materialize, dispatch, complete, push) require
> approval exactly like `omn-agent run`: `--approve`, or an interactive yes.

### One command from ticket to PR, any provider: `run <Provider> <TicketKey>` {#run-e2e}

The same end-to-end cycle also starts directly from a ticket key — no prior
`tickets pull`, `plan`, or `branch` needed — and from any configured ticket
provider, not just Jira:

```bash
omn-agent run Jira  ON-115  -t ./my-repo --gate-policy auto --approve
omn-agent run MSDev ONN-115 -t ./my-repo --gate-policy auto --approve
```

The provider name resolves against the connectors recorded in
`.omn-agent/config/mcp.json` — case-insensitively, with kind aliases
(`MSDev`, `azure-devops`, and `ado` all find the Azure DevOps connector).
Configure them once:

```bash
omn-agent mcp add jira  -t ./my-repo --base-url yourteam.atlassian.net --project PROJ
omn-agent mcp add msdev -t ./my-repo --org-url https://dev.azure.com/yourorg --project Platform
export AZURE_DEVOPS_PAT=<personal access token with work-item read scope>
```

MSDev tickets are addressed as `<PREFIX>-<id>` (the trailing number is the
Azure DevOps work item id) or as the bare id; the normalized ticket then
flows through exactly the machinery above. One invocation fetches the
ticket through the named connector, classifies and routes it (Bug →
fix-bug, refactor/investigate keywords keep their routing, everything else →
implement-feature; `--command` overrides), materializes the runtime run,
binds the feature branch and isolated worktree before implementation,
drives dispatch/complete under the gate policy, and — when the run
completes — runs the pre-PR checks and pushes, creating or updating the PR
(`--test-cmd`, `--base`, `--draft` supported). It pauses only where the
host must run a dispatched subagent or a gate is genuinely held for a human
(the auto policy's conditions and the Producer Exclusion Rule are
unchanged — section 5c), printing each stage as it goes: provider resolved,
fetched, routed, branch/worktree bound, dispatched, gate auto-decided or
held, PR created or updated. Re-running the same command resumes from live
state; the resolved provider is recorded on the task (`provider` in
`task-plan.json`).

> **Errors**
> Unknown provider names, connectors whose kind this build doesn't implement,
> and tickets that don't exist all fail with an actionable message naming the
> fix. The legacy single-argument form (`omn-agent run KEY --show /
> --dispatch / --complete / --gate`) is untouched and remains the step-level
> control for any task, however it was started.

### Who owns which gate

Every flow's gates and their owner roles are listed phase by phase in
[section 4](#flows) — find your flow there for the exact sequence you'll be asked to
approve.

## 5c. Gate auto-approval policy

Every gate is a human decision by default. On a clean, low-severity change
that can mean several rubber-stamp approvals in a row, each one a stop-and-wait
round trip. Teams that want to keep human judgement for the decisions that
warrant it — and the final PR review on GitHub — can let the **runtime itself**
approve a gate whose evidence is unambiguously clean:

```bash
# per invocation
omn-agent run PROJ-42 -t ./my-repo --gate-policy auto

# or durably, per repository
# .omn-agent/config/gate-policy.json
{
  "mode": "auto-on-clean-evidence",
  "severityThreshold": "high",
  "pinned": { "fix-bug": { "Closure Gate": "human-required" } }
}
```

Under `auto-on-clean-evidence`, a decision-eligible gate auto-approves **only
when ALL of these hold** — any one failing keeps that gate on the human path,
byte-for-byte today's behavior, and the run prints *why* it was held:

1. the upstream phase's validation passed clean (no undeclared side effects;
   retries are fine if the final attempt passed);
2. the artifact's declared severity is **below** `severityThreshold`
   (default `high`, so `critical`/`high` always stay human; artifact types
   with no severity field are unaffected);
3. no open question in the artifact is marked **Blocking**;
4. no deviation was **escalated**;
5. on QA-owned gates, no defect stands **open**;
6. this exact workflow + agent version has an **approved precedent** at this
   gate — the first pass of anything unproven is never auto-approved;
7. the gate isn't **pinned** `human-required` in the policy.

> **Audit trail**
> The decision is recorded through the same path as a human one — identical gate
> record, transition, and ledger event — attributed to
> `decidedBy: "runtime:auto-policy"` with every evaluated condition and threshold
> in the record, so the audit trail is exactly as traceable. The Producer
> Exclusion Rule binds the automated decider just like a human: the recorded role
> is always a listed gate owner that did not produce the evidence. Full
> specification and a worked example (three of four gates auto-approve, one
> escalates over a blocking open question): `.omn-agent/config/gate-policy.md`.

## 5d. The final report: who did what, when

When the last phase completes and the last gate is decided, the runtime prints
a **final report** to the console and saves it at
`.omn-agent/runs/<run-id>/final-report.md`. It is also rebuilt on every
aggregation, so a run inspected mid-flight has a current copy, and you can
render it on demand at any time:

```bash
omn-agent run PROJ-42 -t ./my-repo --report        # read-only
```

What it contains, all derived from the persisted run ledger (never asserted):

- **Run** — command, workflow, status, start, last activity, total elapsed.
- **Agent Activity** — one row per phase in workflow order: which agent (and
  version), when it started (first dispatch), when it finished (the completion
  the Validation Engine accepted), how long it took, how many attempts it
  needed, and its validation result. A phase that needed a retry shows it in
  the attempts column at a glance.
- **Gate Decisions** — decision, decider, role, decided-at, and **Waited**:
  how long the gate held the run between its evidence completing and the
  decision landing. Auto-approved gates show `runtime:auto-policy (policy)`
  as the decider, so human and policy decisions are distinguishable in one
  column.
- **Timeline** — every recorded event in commit order: time, actor
  (`agent:omn-qa`, `human:operator`, `runtime:validation-engine`, …), event
  type, and summary.

## 5e. Watching a run live in the terminal {#live-view}

While agents work through phases you don't have to poll by hand — `--show`
has a live visual mode:

```bash
omn-agent run PROJ-42 -t ./my-repo --show                        # one snapshot
omn-agent run PROJ-42 -t ./my-repo --show --watch                # live: re-renders in place until Ctrl+C
omn-agent run PROJ-42 -t ./my-repo --show --watch --interval 5   # poll every 5s (default: 2)
omn-agent run PROJ-42 -t ./my-repo --show --json                 # machine-readable, for dashboards/editors
omn-agent run PROJ-42 -t ./my-repo --show --no-color             # force the plain table
```

On a terminal, `--show` renders a **colorized, phase-grouped tree** — phase →
step → gate — with a status icon and color per row, the queue status, and the
reason that matters right now: a blocked step shows its blocked reason, a
retrying step shows `attempt 2 of 3 at <time>`, a pending gate lists the owner
roles still to decide, a decided gate shows `approve by <role>`. With
`--watch` the tree clears and redraws every interval, so a second terminal
becomes a live progress board for the run.

The rendering degrades gracefully everywhere: icons fall back to ASCII on a
console that can't encode them, the `NO_COLOR` convention and `--no-color`
force the plain table, and redirected output (piping to a file) gets the plain
table automatically. `--json` emits the same tree as structured data for
external dashboards or editor integrations.

> **Read-only by construction**
> **Watching is read-only by construction.** Every refresh is an independent
> status query — the one runtime command that never leases, dispatches,
> completes, or decides anything — so leaving `--watch` running can never
> advance or approve the run by itself. Advancing stays with your own
> `--dispatch` / `--complete` / `--gate` calls and their approval prompts. The
> typical setup: terminal 1 drives the run, terminal 2 watches it.

## 5f. What an agent reads, and what a run cost

A dispatched agent used to read everything: its whole seven-module contract, every file in
its frozen context slice, and every upstream artifact end to end, on every attempt. Runtime
0.7.0 keeps the same phases, agents, skills, gates, and artifacts, and changes only how much
each agent reads:

- **Task context.** `runs/<run-id>/task-context.yaml` is the run's shared state: objective,
  scope, acceptance criteria, decisions, constraints, changed files, risks, open questions,
  completed phases, and gate decisions, as one-line facts with the identifiers the source
  artifacts gave them. The runtime rebuilds it from accepted artifacts at every step; agents
  read it first and open an upstream artifact's sections only where a fact is missing.
- **Progressive module loading.** The charter, reasoning procedure, output contract, and
  quality contract are read in full; the full agent contract, lifecycle module, and examples
  are loaded when their stated trigger applies. `--load-profile full` on a dispatch restores
  the old behaviour for that one dispatch.
- **Conditional skills.** Domain skills (database, security, performance, React, Avalonia)
  are read only when the task touches that domain, derived from the inputs or declared with
  `--affected-area <area>`; when the runtime cannot tell, every skill is read, and security
  is always read in review and validation phases.
- **Parallel dispatch.** The runtime's next-step output lists every phase that may run
  alongside the one it names. In the shipped workflows almost every phase consumes its
  predecessor's artifact, so groups are usually one phase wide.

What it cost is recorded in `runs/<run-id>/execution-metrics.json`, summarised in the final
report (`omn-agent run KEY --report`) and printed by the runtime's `metrics` subcommand:
duration, phases, agent invocations, skill reads, context files read, validation runs, gate
decisions, and a byte-based context estimate under the old and the new rules.

## 5g. Filming a run as a demo: `--demo`

Any `/implement` run can film itself. The result is a real screen recording of Claude
Desktop doing the work, cut down by the run's own telemetry into a short presentation with
titles, a live workflow rail, and a voiceover.

Two commands, and the second is optional because a run that completes while filming cuts
itself:

```bash
python .omn-agent/runtime/framework_runtime.py plan --demo --demo-record \
    --input feature-request=.omn-agent/runs/inputs/<request>.md
#   ... then drive the run as usual; the camera is already rolling ...
python .omn-agent/runtime/framework_runtime.py demo --run-id <run-id> --record-stop --build
```

`--demo-record` starts the camera during planning, before the run's first event, so the film
opens on the run being accepted. For a run that already exists, or one driven through the
ticket CLI with `omn-agent run PROJ-42 --demo`, start the camera separately with
`demo --run-id <run-id> --record-start`; beats that happen before it starts are simply not in
the footage, and the manifest says how many.

### How the cut is decided

A recording of a real run is mostly waiting: an agent thinks for four minutes, a gate waits
for a human. That cannot be watched at normal speed, and it cannot be trimmed blind either,
because the moment something happens is the moment worth showing.

The telemetry solves it. Every marker carries a wall-clock timestamp and the recording
records the instant its own clock read zero, so every beat of the run has a frame number in
the footage. Around each beat the editor keeps a lead-in and a landing at real speed, and
condenses whatever sits between them, with a badge stating the factor. Nothing is staged and
nothing is hidden. The full edit decision list is written into `build-manifest.json`.

### Who the demo is for

That decision changes completely depending on the audience, so it is a setting.

**Relaxed and explained, the default.** For someone meeting the framework once — a customer,
an executive, anybody who will listen rather than read the screen. Every beat is held long
enough to take in, waiting is condensed far less, the captions are large, and the narration
explains what each step *means* in plain language rather than naming it: not "the invocation
gateway leases the phase" but "the framework is now handing this stage to the Product Owner,
and first it writes down exactly which documents that specialist is allowed to read."

In this mode the script is recorded first and the picture is paced to it, so the film runs to
minutes rather than to a target. A two-minute run becomes a five-minute explanation. Where a
beat has more narration than footage, the editor first stops condensing, then plays the
footage in gentle slow motion, and only holds a still frame as a last resort, so the picture
keeps moving while there is film left to show. A concept is explained the first time it
appears and simply named after that, so nobody is told three times what a dispatch is.

**Brisk.** The short highlight reel, for an audience that already knows the framework. Beats
are named rather than explained and waiting is condensed hard.

```bash
demo --run-id <run-id> --build                              # relaxed and explained
demo --run-id <run-id> --build --pace brisk --no-explain    # the short cut
demo --run-id <run-id> --build --speech-rate -3             # slower voice again
```

The same footage can be re-cut either way as often as you like; recording is the slow part
and it only happens once.

### What lands under `runs/<run-id>/demo/`

- **`capture/session.mkv`** and **`capture/capture-manifest.json`** — the raw recording, and
  the window, rectangle, backend, and clock-zero instant it was made with. Matroska, not
  MP4, so a recording that is interrupted is still playable.
- **`markers.jsonl`** — one millisecond-stamped marker per fact: every runtime event, the
  dispatch prompt each agent received (size, digest, excerpt, context-token estimate), each
  agent's result, every validation verdict, every gate decision with its owner and rationale,
  and every tool call when the host hook is wired.
- **`presentation_demo.mp4`** — the film, 1920x1080: the captured window inset, a workflow
  rail showing every phase and gate with the live one lit, a lower third naming the beat,
  condensed-speed badges, a progress bar, and opening and closing cards carrying the run's
  own numbers.
- **`presentation_demo.srt`** and **`presentation_demo-script.md`** — the narration as a
  subtitle file, and as a script to read before presenting.
- **`presentation_demo-poster.png`** and **`build-manifest.json`** — a still for slides, and
  what was produced, what was skipped, and why.

### Captions, and the script

Every line the narrator speaks is also shown on screen as it is said, so the film can be
followed with the sound off — on a phone, in a meeting, or by someone hard of hearing.

The timing is not guessed. The narration is recorded before the picture is cut, so each
line's real duration is known; it is then split where a reader would pause, and each caption
gets a share of the time in proportion to how long it takes to say. On screen the caption is
the largest text in the frame, with the beat's name above it in smaller type, because the
sentence is what the viewer is actually following.

The same words are written beside the film twice more. `presentation_demo.srt` is a standard
subtitle file, so the video can be uploaded anywhere and keep its captions.
`presentation_demo-script.md` is the script: each beat with the time it appears, what is on
screen, and what is said over it. Read it before you present, or hand it to whoever is
presenting instead of you.

`--demo-no-captions` leaves the picture clean. The subtitle file and the script are written
either way, so turning captions off never costs you the script.

### Two ways to record

**OBS Studio** is used when its WebSocket server is switched on, in OBS under
Tools → WebSocket Server Settings → Enable. OBS captures the window itself, so another
window in front of Claude Desktop never appears in the recording, and OBS's own encoder does
the work. The framework creates its own scene collection and profile named `OMN Demo
Capture` and never touches yours.

**ffmpeg** is the fallback and needs no setup at all. It records the window's rectangle on
screen, so the window is raised first and the recording is refused if it will not come
forward. The manifest names which backend was used.

Because that fallback films a place on the screen rather than a window, anything that comes
in front of Claude Desktop during the take — another application, or your desktop if the
window is minimised — would be filmed instead. So the recorder watches which window is
actually in front for the whole take, brings the window back when it loses it, and writes
down every second during which it did not have it. The editor then refuses to put those
seconds in the film, and the build manifest says how many were withheld and why. This
matters more than it sounds: a demo is made to be shown to other people, and whatever else
was on that screen would be shown with it. OBS window capture is immune to the whole
problem, which is the strongest reason to switch its WebSocket server on.

Only the target window is ever recorded, and the recording's own audio is never mapped into
the film, so whatever was playing on the machine during the take is not published. Only the
generated narration is heard.

### Tuning and repair

`--demo-title <text>` sets the opening card, `--demo-pace relaxed|brisk` and
`--demo-explain` / `--demo-no-explain` choose the audience, `--demo-speech-rate <-6..6>` the
delivery speed, `--demo-narration auto|off|<engine>` the voice, and `--demo-no-captions`
hides the on-screen text. Afterwards:

```bash
demo --run-id <run-id> --snapshot                  # markers recorded so far
demo --run-id <run-id> --build                     # re-cut from the same footage
demo --run-id <run-id> --build --drawn             # ignore the footage, draw the dashboard
demo --run-id <run-id> --backfill --build          # film a past run from its event log
demo --run-id <run-id> --build --capture-offset 12 # footage you recorded by hand
```

`--demo` may be added to a run already in flight; the events already recorded are backfilled.
A run that was never recorded at all still produces a demo: with no footage the framework
draws the dashboard instead, which needs nothing installed and always yields at least a
self-contained HTML deck.

To capture the agents' tool calls too, merge the `hooks` block of
`runtime/demo/hooks.settings.json` into the host's `.claude/settings.json`. Only tool names
and a short excerpt of each target are recorded, never file contents. The command in that
file carries a `<framework-dir>` placeholder, since the framework directory is `.omn-agent`
in a repository the installer wrote to and `.claude` in the framework's own checkout; run
`framework_runtime.py demo --print-hook` to get the block with the path already filled in.
Skip the merge and the film still builds, but it shows only the runtime's own events.

Without `--demo` none of this is loaded: the runtime's only cost is one file-existence check
per event.

## 6. What's yours and what's the framework's {#ownership}

The installer classifies **every file before writing anything**, using the
install manifest (content hashes recorded at install time):

| The file… | What happens |
|---|---|
| doesn't exist | created |
| matches the incoming payload | untouched |
| matches its recorded install hash | framework-managed and unmodified → safely updated |
| differs from its recorded hash | **you changed it → skipped, with a warning** |
| isn't in the manifest at all | **yours → never touched, in any mode** |

> **Your files are safe** {.yours}
> Consequences you can rely on:
>
> - **Edit anything you like.** A framework file you modify becomes yours;
>   upgrades will warn and step around it forever after.
> - `--force` replaces modified files *at framework paths only*, and always
>   leaves the previous content at `<file>.omn-bak`.
> - `context/` and `memory/` are seeded once and then belong to the project —
>   fill in `product-context.md`, `technical-context.md`, and
>   `memory/architecture.md`; the agents read them every run.
> - If `.omn-agent` exists but wasn't written by this tool, or its manifest is
>   unreadable or from a newer tool version, every command **stops with exit 4
>   and changes nothing**.

## 7. Keeping the installation healthy {#health}

```bash
omn-agent validate ./my-repo   # pass/fail against everything the bootstrap declares
omn-agent doctor   ./my-repo   # validate + local drift, unknown files, backups
omn-agent status   ./my-repo   # install state, tickets, tasks, runs, Jira config
omn-agent upgrade  ./my-repo   # update framework-managed files only
omn-agent upgrade  ./my-repo --dry-run   # see what an upgrade would do first
```

`doctor` tells you exactly which framework files you've modified (drift), which
files inside framework directories are yours, and which `.omn-bak` backups are
lying around. Install and upgrade never report success without a full
validation pass.

Validation also enumerates **every file the runtime's own context-slice tables
reference** (reported as `V-SLICE` when one is missing), so a setup gap —
like a missing `dependency-map.md` — is named on day one instead of surfacing
as a `context-integrity-failure` several phases into a live run.

### Exit codes

| Code | Meaning |
|---|---|
| 0 | success |
| 1 | invalid target / repo not found |
| 2 | installation or configuration incomplete |
| 3 | validation failed |
| 4 | incompatible existing state — nothing was changed |
| 5 | dry-run finished — nothing was written |
| 6 | permission denied |
| 7 | unexpected error |
| 8 | approval required — nothing was executed |

### Continuous integration on the framework repository

The framework's own repository gates every pull request (and default-branch
push) with `.github/workflows/verify.yml`: the unit-test suite plus every
`verify_*.py` proof script under `.claude/runtime/`, each verifier in its own
job on its own runner, on ubuntu and windows. Both surfaces are located by
discovery — adding a `tests/test_*.py` or `verify_*.py` file needs no CI
change — and a failing verifier fails CI naming itself.

Branch protection binds to four stable check names: `tests-ubuntu` (required
from day one), `tests-windows`, `verifiers-ubuntu-ok`, and
`verifiers-windows-ok` (advisory for the first week, then required). Advisory
means absent from the required-checks list — failures still show red;
`continue-on-error` is never used. The advisory-to-required flip is a
settings-only change, enacted only after a default-branch run shows
`verify_self_hosting.py` passing (the pre-existing orphan run directories are
cleaned first). The workflow never sets `NO_COLOR`, and a new verifier must be
runnable alone, with no arguments, in any order.

This handbook's own HTML rendering (`docs/user-guide.html`) is generated from
this Markdown source (`docs/USER-GUIDE.md`). After editing this file,
regenerate the HTML:

```bash
python tools/render_user_guide.py
```

The `tests` job in `.github/workflows/verify.yml` also runs
`python tools/render_user_guide.py --check`, which fails a pull request
whose HTML is stale and prints the regeneration command above. A change made
directly to `docs/user-guide.html` is discarded by the next regeneration.

## 8. Troubleshooting {#trouble}

| Symptom | Cause & fix |
|---|---|
| `INVALID TARGET: target is not a repository or project root` | The directory has no repo marker. `git init` there, or `omn-agent init <dir>` to mark it. |
| Exit 4: `…exists with content but has no install manifest` | `.omn-agent` wasn't written by this tool. Move it aside, or restore `bootstrap/install-manifest.json` from version control, then re-run. |
| `validate` exits 2 | Files are missing. `omn-agent install` repairs in place. |
| `validate` exits 3 (`does not compile`, `does not resolve`) | A framework file is corrupt or was edited into a broken state. `omn-agent install` restores the framework copy (your intentional edits are still skipped — use `doctor` to see which). |
| `V-IMPORT: … imports 'yaml', which does not resolve …` | The Python environment running `omn-agent` lacks a module the installed runtime imports at top level. Install the distribution the finding's hint names (for `yaml`: `pip install pyyaml`) into the same interpreter you run `omn-agent` with. |
| Upgrade says `skip (modified by user)` | Expected: you changed that file and it's being protected. Keep your version, or `upgrade --force` to take the framework's (backup kept). |
| `Jira credentials are not set` / 401 | Export the env vars named in `config/mcp.json` (default `JIRA_EMAIL`, `JIRA_API_TOKEN` — an Atlassian API token, not a password). They are read at call time and never stored. |
| Exit 8 on `run` | Normal: the step is side-effecting and wasn't approved. Re-run with `--approve` or answer `y` at the prompt. |
| A run phase is `blocked` | The state table names the reason (missing input, unregistered capability, failed validation). `omn-agent run <KEY> --show` prints it; the failure envelope in `runs/<run>/…` carries the recovery action. |
| `V-SLICE: context-slice member missing: dependency-map.md` | The dependency map was deleted or never generated. `omn-agent context generate dependency-map -t <repo>` recreates it from your repo's manifests. |
| A gate didn't auto-approve under `--gate-policy auto` | Expected: some condition failed and the run printed which (`held for a human decision (…)`). Severity at/above threshold, a blocking open question, an escalated deviation, an open QA defect, a pinned gate, or no approved precedent each hold it. Decide it by hand as usual. |
| A gate was rejected / changes requested after implementation | Expected rework loop, not a dead end. The failure envelope names the exact `rollback` command; a listed gate owner runs it naming the phase to return to, the runtime supersedes that phase (previous artifact kept) and re-arms the gate, then re-dispatch and the agent reworks in the same worktree before the gate is decided again by a human — see [the rework loop](#rework). |
| The open PR collected review comments (reviewers, Sonar) | One command drives the whole correction cycle: `omn-agent pr fix-comments KEY` collects the feedback, rejects the pending gate with it, authorises the rollback to the fix phase, and re-dispatches the fix; re-run it after the subagent to verify, close the re-armed gate, and push — see [the review-comment loop](#fix-comments). |
| The Jira ticket changed after work started | One command carries the change end-to-end: `omn-agent update KEY` refreshes the ticket, re-plans, rejects the awaiting gate with the change request (or starts a new run if the old one completed), drives the run, and pushes the result to the PR — see [the change-request loop](#update). |
| You want a fresh ticket driven to a PR in one go | One command runs the whole lifecycle from any configured provider: `omn-agent run Jira ON-115 --gate-policy auto --approve` (or `run MSDev ONN-115 …`) fetches, routes, binds the branch/worktree, drives the run, and creates or updates the PR; re-running resumes — see [one command from ticket to PR](#run-e2e). |
| A `--demo` run produced `presentation_demo.gif` or only `.html`, not `.mp4` | Expected fallback: the runtime found no `ffmpeg` (GIF) or no Pillow (HTML with text frames). `runs/<run>/demo/build-manifest.json` names the missing piece. Install `ffmpeg` (or `pip install imageio-ffmpeg`) and re-run `framework_runtime.py demo --run-id <run> --build`; the recording is untouched. |
| The demo drew a dashboard instead of showing the real window | Nothing was filmed for that run, or the edit failed and fell back. `demo --run-id <run> --snapshot` reports whether a capture exists; `build-manifest.json` names the reason under `fallbacks`. Film it with `demo --run-id <run> --record-start`. |
| `--record-start` reports that the window could not be brought to the front | The ffmpeg backend records the window's rectangle on screen, so it refuses rather than film whatever is covering it. Click the Claude Desktop window and start again, or switch on OBS's WebSocket server (Tools → WebSocket Server Settings) to capture the window itself regardless of what is in front. |
| The film shows only part of the run | Beats that happened before the recording started are not in the footage; the manifest says how many under `fallbacks.coverage`. Start the recording before driving the run, or re-cut a hand-made recording with `--capture-offset <seconds>`. |
| The demo film is silent | No text-to-speech engine produced audio; the manifest's `narration.attempts` lists what was tried and why each failed. On Windows the built-in SAPI voice needs no install; elsewhere `pip install pyttsx3` (offline) or `edge-tts` (online, needs ffmpeg) adds one. |
| The demo film is much longer than `--demo-seconds` | Expected in the default explaining mode: there the narration sets the length and `--demo-seconds` is ignored, because a sentence is never cut short. For a fixed short cut use `demo --run-id <run> --build --pace brisk --no-explain --target-seconds 60`. |
| The demo film is too fast, or assumes too much knowledge | It was cut brisk. Re-cut the same footage with `demo --run-id <run> --build --pace relaxed --explain`, and add `--speech-rate -3` to slow the voice further. No new recording is needed. |
| Long stretches of the film sit on a still frame | The narration needs more time than the recording holds. `build-manifest.json` reports it under `narration.fit` as `beats_held`. Record a longer run, or shorten the film with `--no-explain`. |
| `branch`: `worktree path already exists but is not a registered git worktree` | Something else created a directory at the task's worktree path. Move it aside, or `omn-agent branch KEY --force` to delete and recreate it. |
| `branch`: `branch '…' is checked out in the main working tree` (or another worktree) | Git allows a branch in one worktree at a time. Switch the main checkout away (`git checkout <base>`), or remove the stale worktree (`git worktree remove <path>`), then re-run. |
| `run --dispatch`/`pr`: `the worktree bound to task … is missing` | The worktree directory was deleted by hand. `omn-agent branch KEY` recreates it (the branch and its commits are unaffected). |
| `run --dispatch`/`pr`: `task …'s worktree was released: ticket closed (…)` | The ticket closed, so sync/pull removed the worktree. If work must continue anyway, `omn-agent branch KEY` rebinds it with a fresh worktree. |
| `T-WT-DIRTY` warning on every sync | A closed ticket's worktree still holds uncommitted work, so it is never auto-deleted. Inspect it, salvage or discard the changes, then `git worktree remove <path>` (add `--force` to discard). |

## 9. Customizing the framework for your team {#custom}

- **Context first.** The highest-leverage 30 minutes: write real content into
  `context/product-context.md`, `context/technical-context.md`, and
  `memory/architecture.md`. Every agent's context slice includes them. Keep
  `dependency-map.md` current too (`omn-agent context generate dependency-map`) —
  it's the blast-radius record root-cause analysis and design phases read.
- **Templates.** Editing an artifact template under `templates/` marks it yours;
  the validators check structure, so keep the required sections.
- **Skills.** `skills/` holds the engineering playbooks agents apply
  (testing strategy, error handling, security, …). Tune them to your standards.
- **Memory.** `memory/decision-log.md`, `known-issues.md`, and
  `coding-standard.md` are living documents — the framework reads them, your
  team maintains them.

---

*Framework source: this repository's `.claude/` tree. Tool: `omn-agent` 0.1.0.
Full command reference: `omn-agent --help` and `README.md`.*
