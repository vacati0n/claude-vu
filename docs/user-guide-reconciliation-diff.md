# Handbook reconciliation: the recorded comparison

This file records the normalised comparison the Design Gate required between the
published handbook as committed immediately before it became a build output
(`tests/fixtures/user-guide-pre-change.html`) and the page as regenerated when the
reconciliation closed (`tests/fixtures/user-guide-reconciled.html`, a frozen copy of
what `docs/user-guide.html` then was). It is the enumeration that
`docs/user-guide-reconciliation.md` indexes, and every hunk in it is classified.

## Method

Both pages are reduced to two streams by `visible_text_stream` and
`element_stream` in `tests/test_render_user_guide.py`, and each pair of streams is
diffed with the standard library's sequence matcher over whole segments:

- the **visible-text stream**: one segment per block-level element (paragraph,
  heading, list item, table row with cells separated by `|`, navigation entry,
  callout tag, code line), with the style block and the stylesheet link removed,
  inter-tag whitespace collapsed, and entities decoded;
- the **element-and-class sequence**: every opening tag as `name.class.class`,
  classes sorted, all other attributes dropped, the style block excluded.

The declared-anchor set and the internal-link-target set were compared as sets:
both pages declare exactly the 21 identifiers of the design's baseline and both
link graphs are closed over them, so they produce no hunk.

`PreChangeEquivalence` in the same test module recomputes both diffs from the two
fixtures and fails unless this file carries every hunk, in order, with the same
segments and the same offsets, and unless every hunk's classification resolves.
Because both sides are frozen, a later edit to the handbook does not appear here;
it is a new change with its own record.

## Classification

Each entry's heading names the hunk, its 0-based start offsets in the pre-change
and regenerated streams, and one or more classifications in backticks:

- `item N` — accounted for by row N of `docs/user-guide-reconciliation.md`
  (sections 1 and 2): content merged, dropped, folded, or rendered under a rule;
- `wording: <section>` — same material in divergent wording, markup, paragraph
  boundary or sample form; the section names a row of the record's section 3, and
  the source's form governs under `R1`;
- `ordering` — the same material in the source's order, an entry of the record's
  section 4 under `R7`;
- `derived: <construct>` — intended-derived presentation the renderer holds or
  computes: `banner`, `navigation`, `code-marking`, `callout-shape`, and the other
  constructs the test module enumerates;
- `defect` — a difference that should not exist. None is recorded: a hunk carrying
  it fails the test, so a defect is fixed rather than filed here.

A hunk that both changes wording and carries a recorded item cites both. Merged
items (record items 1 to 15, 21 and 22) appear on both sides of the comparison and
therefore produce no hunk of their own; they are cited only where a hunk's wording
touches them.

Hunk lines are `- ` for the pre-change side and `+ ` for the regenerated side.


## Visible-text stream: 334 segments before, 420 after, 51 hunks

### T-01 · at 1/1 · `derived: banner` · `wording: masthead`

The generated banner opens the page; the published strapline is superseded by the source's, ruled one fact by omn-product-owner (Q-001).

```diff
- Omn-Agent AI Engineering Framework · Team Guide
+ Generated file · do not edit This page is generated from docs/USER-GUIDE.md, where this guide is versioned. Edit that file, then regenerate with python tools/render_user_guide.py. A change made directly to this file is discarded by the next regeneration and fails the repository's drift check.
+ The user guide for teams working with the Omn-Agent AI Engineering Framework.
```

### T-02 · at 3/4 · `wording: masthead` · `ordering` · `item 17`

The lede is reworded; the framework chain leaves the masthead for chapter 1, and its hand-written accessibility label goes with it (item 17).

```diff
- Omn-Agent turns AI-assisted development from "chat with a model" into a governed delivery process: specialized agents own phases of real workflows, every output is validated against a contract, and progress waits at human gates until someone accountable approves. The omn-agent CLI installs it into your repository, keeps it healthy, and turns Jira tickets into approval-gated runs.
- command→ workflow→ phase→ owner agent→ artifact ✓→ human gate→ next phase
+ Omn-Agent turns AI-assisted development from "chat with a model" into a governed delivery process. Work travels through workflows made of phases; each phase is owned by a specialized agent that produces a validated artifact; progress is held at human gates until someone accountable approves. The omn-agent CLI installs the framework into your repository, keeps it healthy, and connects it to Jira so tickets become executable, approval-gated work.
```

### T-03 · at 8/8 · `item 16` · `derived: navigation`

Navigation label regenerated from the chapter heading.

```diff
- The flows, by intent
+ The flows: pick by what you're trying to do
```

### T-04 · at 10/10 · `item 16` · `derived: navigation`

Two navigation labels regenerated from their chapter headings.

```diff
- Yours vs. the framework's
- Keeping it healthy
+ What's yours and what's the framework's
+ Keeping the installation healthy
```

### T-05 · at 13/13 · `item 16` · `derived: navigation`

Navigation label regenerated from the chapter heading.

```diff
- Customizing
+ Customizing the framework for your team
```

### T-06 · at 16/16 · `ordering` · `wording: 1. The mental model` · `item 17`

The chain arrives here from the masthead; its introducing sentence reads as the source does.

```diff
- Everything follows the chain above. The pieces:
+ Everything in the framework follows one chain:
+ command→workflow→phase→owner agent→artifact ✓→human gate→next phase
```

### T-07 · at 19/20 · `wording: 1. The mental model`

```diff
- Phases are each owned by one agent — a product owner scopes, a planner plans, an architect designs, a developer implements, a reviewer reviews, QA validates.
- Artifacts are the phase outputs (scope-definition, execution-plan, technical-design, implementation-report, …). Every artifact type has a validator; a phase does not complete until its artifact passes.
- Gates are human decision points between phases. A gate names its owner roles — and the agent that produced the evidence may never approve its own gate.
- A run is one request travelling through one workflow. Its state lives in .omn-agent/runs/: state table, event stream, failure envelopes, recovery ledger. Nothing is silently skipped — a phase that cannot execute is blocked with a recorded reason, never dropped.
+ Phases are owned by one agent each — a product owner agent scopes, a planner plans, an architect designs, a developer implements, a reviewer reviews, QA validates.
+ Artifacts are the phase outputs (scope-definition.md, execution-plan.md, technical-design.md, implementation-report.md, …). Every artifact type has a validator; a phase does not complete until its artifact passes.
+ Gates are human decision points between phases. A gate names its owner roles, and the agent that produced the evidence may never approve its own gate.
+ A run is one request travelling through one workflow. Run state lives in .omn-agent/runs/ — state table, event stream, failure envelopes, recovery ledger. Nothing is silently skipped: a phase that cannot execute is blocked with a recorded reason, never dropped.
```

### T-08 · at 25/26 · `wording: 2. Installation`

Item 1's dependency sentence is on both sides; only the Prerequisites clause before it differs.

```diff
- Prerequisites: Python 3.10+ and a target repository — anything with .git or a standard project marker. The omn-agent CLI package itself uses the Python standard library only; the framework runtime files it installs import PyYAML, so the distribution declares pyyaml as a dependency and pip install pulls it automatically.
+ Prerequisites: Python 3.10+, a target repository (anything with .git or a standard project marker). The omn-agent CLI package itself uses the Python standard library only; the framework runtime files it installs import PyYAML, so the distribution declares pyyaml as a dependency and pip install pulls it automatically.
```

### T-09 · at 28/29 · `wording: 2. Installation`

The install sample's first comment; the published form had folded the next comment into it.

```diff
- # install the framework into your repo, then confirm health
+ # install the framework into your repo
```

### T-10 · at 30/31 · `wording: 2. Installation`

The second comment of the same sample, which the published form had folded into the first.

```diff
+ # confirm health
```

### T-11 · at 33/35 · `wording: 2. Installation` · `item 38`

Dependency-map paragraph reworded, the regenerate command set as a sample block; the flag-wins clause is item 38.

```diff
- Install also seeds a dependency-map.md derived from your repository's own manifests (.csproj project references, package.json local dependencies, pyproject.toml dependencies) — the boundary record agents read when they assess a change's blast radius. No manifests detected? It seeds an honest placeholder for you to fill in. Regenerate any time with omn-agent context generate dependency-map -t ./my-repo --force.
- Installing from a different framework checkout? Pass --source <path>. Every write-capable command accepts --dry-run to preview the full plan without touching anything (exit code 5). Every command accepts the target uniformly as -t/--target; the historically positional ones (init, install, upgrade, validate, doctor, status) still take the bare positional too.
+ Install also seeds a dependency-map.md derived from your repository's own manifests (.csproj project references, package.json local dependencies, pyproject.toml dependencies) — the boundary record several phases read when they assess a change's blast radius. When no manifest is detectable it seeds an honest placeholder telling you to fill it in. Regenerate it any time with:
+ omn-agent context generate dependency-map -t ./my-repo --force
+ If you are installing from a different framework checkout, pass --source <path>. Every write-capable command accepts --dry-run to preview the full plan without touching anything (exits with code 5). Every command that takes a target accepts it uniformly as -t/--target; the historically positional ones (init, install, upgrade, validate, doctor, status) still accept the bare positional too, and the flag wins when both are given.
```

### T-12 · at 37/40 · `wording: 2. Installation`

Install table first column: the published form had shortened the paths.

```diff
- | bootstrap/ | descriptor + install manifest | generated — do not edit
- | runtime/ | workflow engine, state machine, artifact validators | framework-managed
- | registry/ | agent / workflow / skill / template / command registries | framework-managed
- | agents/ workflows/ templates/ skills/ commands/ config/ domain-model/ validation/ | agent contracts, workflow specs, artifact templates, playbooks | framework-managed
- | context/ memory/ dependency-map.md | product, technical & release context; architecture memory; the module dependency map | yours — seeded once, never overwritten
- | reports/ runs/ tickets/ tasks/ | operational output | yours — never touched by the installer
+ | .omn-agent/bootstrap/ | descriptor + install manifest | generated — do not edit
+ | .omn-agent/runtime/ | workflow engine, state machine, artifact validators | framework-managed
+ | .omn-agent/registry/ | agent / workflow / skill / template / command registries | framework-managed
+ | .omn-agent/agents/ workflows/ templates/ skills/ commands/ config/ domain-model/ validation/ | agent contracts, workflow specs, artifact templates, playbooks | framework-managed
+ | .omn-agent/context/ memory/ dependency-map.md | product, technical & release context; architecture memory; the module dependency map | yours — seeded once, never overwritten
+ | .omn-agent/reports/ runs/ tickets/ tasks/ | operational output | yours — never touched by the installer
```

### T-13 · at 46/49 · `wording: 3. Two ways to work`

```diff
- With the framework installed, ask for work with a command. It routes to its workflow and the agents take over, phase by phase:
+ With the framework installed, ask for work with a command. Each command routes to its workflow and the agents take over, phase by phase:
```

### T-14 · at 50/53 · `wording: 3. Two ways to work`

```diff
- | /refactor | refactor | scope, invariants & risk | architect → developer → QA
+ | /refactor | refactor | scope, invariants & risk profile | architect → developer → QA
```

### T-15 · at 56/59 · `wording: 3. Two ways to work`

```diff
- | /document | implement-feature | documentation & handoff | documentation agent
- | /test | review-pull-request | test-risk validation | QA
- Chapter 4 walks each of these flows end to end — phases, owners, artifacts, and the gates you'll approve.
+ | /document | implement-feature (docs phase) | documentation & handoff | documentation agent
+ | /test | review-pull-request (test phase) | test-risk validation | QA
+ Section 4 walks each of these flows end to end — phases, owners, artifacts, and the gates you'll approve.
```

### T-16 · at 70/73 · `wording: 3. Two ways to work`

Cross-reference wording and the plan paragraph reworded; the connector-config sentence (item 4) is on both sides.

```diff
- Besides refreshing the inbox, sync and pull also release the isolated worktree of any task whose ticket has closed since the last refresh — see Auto-cleanup in chapter 5.
- plan classifies the ticket deterministically — Bug → fix-bug, refactor / tech-debt keywords → refactor, spike / research → investigate, everything else → implement-feature. It renders the runtime input document from the ticket (.omn-agent/tasks/PROJ-42/input.md) and records the routing. Wrong call? Override with --command bugfix|implement|refactor|investigate. A ticket with no acceptance criteria says so explicitly in its input document — the Scope Gate is where they get defined.
+ Besides refreshing the inbox, sync and pull also release the isolated worktree of any task whose ticket has closed since the last refresh — see "Worktrees clean themselves up" in section 5a.
+ plan classifies the ticket deterministically — Bug → fix-bug, refactor / tech-debt keywords → refactor, spike / research → investigate, everything else → implement-feature — renders the runtime input document from the ticket (.omn-agent/tasks/PROJ-42/input.md), and records the routing. Override with --command bugfix|implement|refactor|investigate if the automatic call is wrong. If the ticket has no acceptance criteria, the input document says so explicitly and the Scope Gate is where they get defined.
```

### T-17 · at 74/77 · `wording: 3. Two ways to work`

```diff
- Not every flow needs a ticket: omn-agent quality-scan enters the code-quality-scan workflow directly from the command line — it renders its own scope input and records the scan as task QS-<NAME> (4.7).
+ Not every flow needs a ticket: omn-agent quality-scan enters the code-quality-scan workflow directly from the command line — it renders its own scope input and records the scan as task QS-<NAME> (section 4.7).
```

### T-18 · at 78/81 · `item 31` · `wording: 4. The flows`

The Section column is item 31; the separator and 'chapter 5' are wording.

```diff
- | You want to… | Flow | Command
- | Ship a new capability or user story | implement-feature | /implement
- | Repair broken behavior | fix-bug | /bugfix
- | Improve structure without changing behavior | refactor | /refactor
- | Answer a question before committing to build | investigate / research | /investigate · /research
- | Judge a pull request | review-pull-request | /review
- | Ship a release candidate | release | /release
- | Find code junk & technical debt, evidence-first | code-quality-scan | /quality-scan
- All flows share the same run mechanics — materialize, dispatch, complete, gate (chapter 5) — but differ in their phases, artifacts, and who approves. Where a phase shows no gate, the run moves straight on once its artifact validates. Where a gate lists two roles, remember the Producer Exclusion Rule: the agent that produced the evidence never decides its own gate.
+ | You want to… | Flow | Command | Section
+ | Ship a new capability or user story | implement-feature | /implement | 4.1
+ | Repair broken behavior | fix-bug | /bugfix | 4.2
+ | Improve structure without changing behavior | refactor | /refactor | 4.3
+ | Answer a question before committing to build | investigate / research | /investigate / /research | 4.4
+ | Judge a pull request | review-pull-request | /review | 4.5
+ | Ship a release candidate | release | /release | 4.6
+ | Find code junk & technical debt, evidence-first | code-quality-scan | /quality-scan | 4.7
+ All flows share the same run mechanics — materialize, dispatch, complete, gate (section 5) — but differ in their phases, artifacts, and who approves. Where a phase shows no gate, the run moves straight on once its artifact validates. Where a gate lists two roles, remember the Producer Exclusion Rule: the agent that produced the evidence never decides its own gate.
```

### T-19 · at 96/99 · `item 41`

```diff
+ The ticket-driven sequence, end to end:
```

### T-20 · at 103/107 · `wording: 4.1 to 4.7`

```diff
- Enter with: an agreed feature request — a ticket with no acceptance criteria is fine; the Scope Gate is where they get written down. Done when: the Closure Gate approves — acceptance criteria verified, docs and release notes updated, PR open for final review on GitHub.
+ Enter with: an agreed feature request. A ticket with no acceptance criteria is fine — the Scope Gate is where they get written down. Done when: the Closure Gate approves — acceptance criteria verified, docs and release notes updated, PR open for final review on GitHub.
```

### T-21 · at 112/116 · `wording: 4.1 to 4.7`

Same words; the published form had run the two paragraphs together.

```diff
- Same terminal sequence as 4.1 — plan routes Bug-type tickets here automatically, and the branch is named bugfix/<ticket>-<slug>. Enter with: a defect report with an observable symptom and reproduction context (or equivalent diagnostic evidence). Done when: the defect no longer reproduces, the root cause is documented with evidence, and a regression test covers the failure path.
+ Same terminal sequence as 4.1 — plan routes Bug-type tickets here automatically, and the branch is named bugfix/<ticket>-<slug>.
+ Enter with: a defect report with an observable symptom and reproduction context (or equivalent diagnostic evidence). Done when: the defect no longer reproduces, the root cause is documented with evidence, and a regression test covers the failure path.
```

### T-22 · at 121/126 · `wording: 4.1 to 4.7`

The 4.3 opening likewise, plus the 4.4 heading separator.

```diff
- Same terminal sequence as 4.1; refactor / tech-debt ticket keywords route here, and the branch is named refactor/<ticket>-<slug>. Enter with: a defined refactor scope, explicitly documented behavioral invariants, and baseline tests or metrics. Done when: invariants are proven unchanged, quality metrics improved or within accepted limits, and the technical-debt delta is recorded with follow-ups.
- 4.4 · Investigate & research — /investigate · /research
+ Same terminal sequence as 4.1; refactor / tech-debt keywords route here, and the branch is named refactor/<ticket>-<slug>.
+ Enter with: a defined refactor scope, explicitly documented behavioral invariants, and baseline tests or metrics. Done when: invariants are proven unchanged, quality metrics improved or within accepted limits, and the technical-debt delta is recorded with follow-ups.
+ 4.4 · Investigate & research — /investigate / /research
```

### T-23 · at 130/136 · `wording: 4.1 to 4.7`

```diff
- Enter with: a question, its decision owner, and the scope, timeline, and constraints — spike / research ticket keywords route here. Done when: the recommendation is evidence-backed and decision-ready, with assumptions and risks explicit — the owner can proceed or defer with rationale.
+ Enter with: a question, its decision owner, and the scope, timeline, and constraints. Spike / research ticket keywords route here. Done when: the recommendation is evidence-backed and decision-ready, with assumptions and risks explicit — the owner can proceed or defer with rationale.
```

### T-24 · at 167/173 · `item 5` · `item 32` · `wording: 4.1 to 4.7`

'A scan is a normal task living at' is item 5's merged form; the --scope-file sentence is item 32; QS-BACKEND for QS-<NAME> is wording.

```diff
- A normal task A scan lives at tasks/QS-<NAME>/, so omn-agent run QS-<NAME> --show / --watch / --report work unchanged — and a re-run with a changed scope archives the previous run to the task's runHistory and materializes a new one: a changed input is a new run, exactly as in omn-agent update. Inside Claude Code, /quality-scan <scope> is the same flow.
+ A normal task A scan is a normal task living at tasks/QS-<NAME>/, so omn-agent run QS-BACKEND --show / --watch / --report work unchanged, and a re-run with a changed scope archives the previous run to the task's runHistory and materializes a new one — a changed input is a new run, exactly as in omn-agent update. Prefer writing the scope yourself? Pass --scope-file ./scan-scope.md. (Inside Claude Code, /quality-scan <scope> is the same flow.)
```

### T-25 · at 180/186 · `item 33` · `item 42` · `item 12` · `item 18` · `item 40` · `wording: 5a. Branch and PR lifecycle`

Chapter 5's forward pointers (item 33) replace the condensed opening; the heading separator is wording; the lead-in is item 42; the chain keeps the '(worktree)' qualifier and gate marking (item 12) with the source's capitalised tokens (wording) and a derived label (item 18); the branch sample's commentary is item 40.

```diff
- While agents are working, the run can be watched live in a second terminal — see below.
- Branch & Pull Request lifecycle
- Jira→ plan→ branch (worktree)→ implement→ validate→ push→ PR→ review
- omn-agent branch PROJ-42 -t ./my-repo # feature/proj-42-<slug> off main, in .worktrees/proj-42-feature/
+ Once the run reaches the implementation phase, branching becomes part of the sequence -- see section 5a. Gate decisions are human by default; a team that wants clean, low-risk gates decided by the runtime itself opts in with the gate policy -- see section 5c. When the run completes, the final report is printed automatically and saved -- see section 5d. And while agents are working, you can watch the run live in a second terminal -- see section 5e.
+ Branch and Pull Request lifecycle
+ The full chain from ticket to review is:
+ Jira→Plan→Branch (worktree)→Implement→Validate→Push→PR→Review
+ omn-agent branch PROJ-42 -t ./my-repo
+ # -> creates feature/proj-42-<slug> (or your project's own template -- see
+ # 5b), off main (or --base), inside the task's own isolated worktree at
+ # .worktrees/proj-42-feature/, and binds both to the task. The main
+ # checkout is never switched.
```

### T-26 · at 185/196 · `item 40` · `wording: 5a. Branch and PR lifecycle`

The sample's --complete line and reworded comments; the pr fix-comments and update lines (items 21, 22) match on both sides and are outside this hunk.

```diff
- # ... implement and commit inside .worktrees/proj-42-feature/ ...
- omn-agent pr precheck PROJ-42 -t ./my-repo # optional: worktree guard + tests, no PR
- omn-agent pr create PROJ-42 -t ./my-repo # checks, push, open the PR via gh
+ # ... the developer agent implements inside .worktrees/proj-42-feature/
+ # (the dispatch output names the exact directory), with test coverage ...
+ omn-agent run PROJ-42 -t ./my-repo --complete --phase implementation --approve
+ omn-agent pr precheck PROJ-42 -t ./my-repo # optional: checks only, no PR
+ omn-agent pr create PROJ-42 -t ./my-repo # checks, push, open the PR
```

### T-27 · at 190/203 · `item 19` · `item 23` · `item 24` · `item 25` · `item 26` · `item 27` · `item 28` · `item 29` · `item 30` · `wording: 5a. Branch and PR lifecycle`

The branch-config clause is dropped (item 19); the routed-command table, guardrails, self-ignore sentence, worktree-only paragraph, pr precheck and pr create detail, the outcome sentence and the whole of 5b are items 23 to 30; the callout bodies and the defaultBase sample are wording.

```diff
- omn-agent branch KEY names the branch per the project's branch naming templates (defaults: feature/{ticket_id}-{short_description} / bugfix/…, fully lowercased; view or change with omn-agent branch-config show|set|preview). The work type that picks the template comes from the task's routed command — implement→feature, bugfix→bugfix, refactor→refactor, investigate→chore — unless overridden with --type. The branch is created off the configured default base (falling back to main then master, or an explicit --base, which must exist).
- Worktree isolation Each task gets its own git worktree at .worktrees/<ticket>-<work-type>/ — the shared main checkout is never switched, so any number of tasks can run concurrently without branch collisions or dirty-tree conflicts. The mapping is deterministic and recorded (path, branch, base, status) as worktree in tasks/<KEY>/task-plan.json; re-running branch reuses the existing worktree, never creates a second one. Every later step — implementation dispatch, pr precheck, pr create — resolves the task's worktree from that record (never the current working directory) and verifies it is on the bound branch before proceeding. A dirty main checkout only draws a warning (B-DIRTY-MAIN): the worktree is created fresh off the base, so nothing leaks. Conflicts are explicit errors — the branch checked out elsewhere, the path registered to another branch, or an unregistered directory on the path (--force reclaims only that last case).
- Auto-cleanup Worktrees clean themselves up when the ticket closes. Every tickets sync / tickets pull checks the current status of each ticket with an active worktree (sync re-fetches them by key — its default JQL hides closed tickets) and releases the worktree of any that turn out closed (T-WT-CLEAN): directory and registration removed, branch kept, task marked worktree.status: removed with the reason. A worktree still holding uncommitted work is kept with a warning (T-WT-DIRTY), never force-deleted — inspect it, then git worktree remove <path> (also how to remove any worktree by hand). omn-agent branch KEY rebinds a released task with a fresh worktree if work must continue.
- pr precheck re-confirms the worktree guard, then runs a test command inside the task's worktree (auto-detected — tests/, pyproject.toml+pytest, or package.json — or --test-cmd) and records the result on the task. pr create runs the same checks (skip with --skip-checks; the worktree guard still applies), pushes the branch, and opens a PR via the GitHub CLI with a standardized title and body — failing safely with exact next steps (or a ready-made compare URL) when gh is missing or unauthenticated.
- Branch safety omn-agent branch KEY always prints the resolved base branch's tip commit (hash, date, subject) before creating anything, and warns loudly with the actual commit counts when the base is dramatically behind the repository's most recently active branch — so branching off an abandoned main stub in a develop-based repo can no longer happen silently. Teams whose integration branch isn't main/master set it once in .omn-agent/config/branch-defaults.json ({"defaultBase": "develop"}) instead of passing --base every time; an explicit --base still wins.
+ omn-agent branch KEY names the branch per the project's branch naming templates (section 5b; defaults to feature/<ticket>-<slug> / bugfix/<ticket>-<slug>, fully lowercased). The work type used to pick a template comes from the task's routed command unless overridden with --type:
+ | Routed command | Work type
+ | implement | feature
+ | bugfix | bugfix
+ | refactor | refactor
+ | investigate | chore
+ It is created off the project's configured default base (see below), falling back to main then master, or an explicit --base (which must already exist -- an unknown --base fails rather than silently falling back).
+ Worktree isolation Each task gets its own worktree. The branch is checked out in an isolated git worktree at .worktrees/<ticket>-<work-type>/ -- a deterministic path per task identity, recorded (path, branch, base, status) as worktree in tasks/<KEY>/task-plan.json. Because every task has its own working directory, concurrent tasks never collide: no branch switching in the shared checkout, no dirty-tree conflicts between tasks. Re-running the command for the same task reuses its existing worktree -- the same task never gets a second one. .worktrees/ self-ignores via a generated .gitignore.
+ Guardrails:
+ a dirty main checkout only draws a warning (B-DIRTY-MAIN) -- the worktree is created fresh off the base branch, so uncommitted changes in the shared tree never leak into task work;
+ the task's branch already checked out elsewhere (another worktree, or the main tree), the worktree path registered to a different branch, or an unregistered directory occupying the path each fail with the exact command that resolves them (--force deletes and recreates only that last, unregistered-directory case);
+ a missing base branch, or a fetch that fails against a configured remote, blocks it outright -- never silently substituted;
+ the resolved base's tip commit (hash, date, subject) is always printed (B-BASE-TIP), so a stale base is visible before anything is created;
+ when the base is dramatically behind the repository's most recently active branch (default threshold: 100 commits), a loud warning (B-STALE-BASE) states the exact commit count and names the fix -- so branching off an abandoned main stub in a develop-based repo can no longer happen silently;
+ --dry-run previews the branch name, worktree path, and action without touching anything.
+ Auto-cleanup Worktrees clean themselves up when the ticket closes. Every tickets sync / tickets pull checks the current status of each ticket with an active worktree (sync re-fetches them by key -- its default JQL hides closed tickets) and releases the worktree of any that turn out closed (T-WT-CLEAN): the directory and its git registration are removed, the branch is kept, and the task records worktree.status: removed with the reason. A worktree that still holds uncommitted work is kept with a warning (T-WT-DIRTY) instead of being force-deleted -- inspect it, then git worktree remove <path> (also the way to remove any worktree by hand). Re-running omn-agent branch KEY on a released task rebinds it with a fresh worktree if work must continue.
+ Branch safety
+ Per-repo default base. If your integration branch isn't main/master, set it once instead of passing --base on every invocation:
+ // .omn-agent/config/branch-defaults.json
+ { "defaultBase": "develop", "divergenceWarningThreshold": 100 }
+ An explicit --base still wins over the configured default, which wins over the main/master fallback. A missing file keeps today's behavior exactly.
+ Implementation only runs in the task's worktree. Once a branch is bound, omn-agent run KEY --dispatch --phase implementation resolves the task's recorded worktree -- never the current working directory -- and checks it exists, is registered with git, and is on the bound branch before dispatching; an unbound task, a missing or unregistered worktree, a protected branch, or a mismatched checkout each fail with a message naming the fix (omn-agent branch KEY, or git -C <worktree> checkout <branch>). The dispatch output states the worktree directory all code changes belong in.
+ omn-agent pr precheck KEY re-confirms the worktree guard, then runs a test/validation command inside the task's worktree and records the result on the task. It auto-detects one when --test-cmd isn't given: a tests/ directory runs python -m unittest discover -s tests, pyproject.toml with pytest installed runs pytest, package.json runs npm test. Finding none is a recorded warning, not a failure -- the gate simply couldn't verify anything.
+ omn-agent pr create KEY runs the same checks (skip with --skip-checks, though the worktree guard still applies), pushes the branch to origin, and opens a Pull Request via the GitHub CLI (gh) with a standardized title (type(KEY): summary) and body (ticket link, changes, testing result, a Closes KEY trailer). --base overrides the task's recorded base branch; --draft opens it as a draft; --dry-run previews without pushing or creating anything.
+ If gh isn't installed or isn't authenticated, pr create fails safely with the exact next step (an install link and gh auth login, or just gh auth login) plus a ready-made GitHub compare URL so the PR can still be opened by hand -- it never crashes or guesses.
+ Both commands write their outcome onto tasks/<KEY>/task-plan.json (branch, worktree, prChecks, pr), alongside the approvals that run already records there.
+ Branch naming templates
+ Every project can define its own branch naming convention once, at omn-agent init time, rather than living with the built-in default. It's persisted at .omn-agent/config/branch-naming.json -- project-local, seeded once and then owned by the project, exactly like context/ and memory/.
+ omn-agent init ./my-repo \
+ --feature-branch-template 'feature/on-{ticket_id}-{short_description}' \
+ --bugfix-branch-template 'bugfix/on-{ticket_id}-{short_description}' \
+ --branch-max-length 60
+ On an interactive terminal, omitting both template flags prompts for them instead (press Enter to accept the built-in default for either one). Passing either flag, or running non-interactively (CI), skips the prompt entirely and uses whatever combination of flags and defaults you gave.
+ Token reference
+ | Token | Required | Meaning
+ | {ticket_id} | yes -- every template must contain it | the task's ticket key, e.g. PROJ-42
+ | {short_description} | no | a slug derived from the ticket summary
+ | {work_type} | no | the resolved work type itself (feature, bugfix, or a custom one)
+ Normalization and validation rules
+ The whole rendered name is normalized, per /-separated segment (so template-authored hierarchy like feature/... survives instead of being flattened into one dash-joined blob):
+ lowercased;
+ anything outside [a-z0-9_-] (spaces, punctuation, {/} left over from a stray token, …) becomes -;
+ duplicate - collapse to a single -;
+ leading/trailing - are trimmed;
+ the result is truncated to --max-length (default 80), trimming a dangling -// left by the cut.
+ A template is validated at save time (omn-agent init or branch-config set) -- on failure, a clear error is printed and nothing is written:
+ it must contain the {ticket_id} token;
+ it must use no token outside {ticket_id} / {short_description} / {work_type} (an unknown token like {author} is rejected by name);
+ braces must balance;
+ rendering it with sample values and normalizing must produce a name git check-ref-format --branch accepts.
+ Viewing and changing templates later
+ omn-agent branch-config show -t ./my-repo
+ # feature: 'feature/on-{ticket_id}-{short_description}' (project-configured)
+ # bugfix: 'bugfix/{ticket_id}-{short_description}' (default)
+ omn-agent branch-config set -t ./my-repo \
+ --feature-template 'feature/on-{ticket_id}-{short_description}'
+ # only --feature-template changes; --bugfix-template, --template, and
+ # --max-length are all independently optional and leave anything else as-is
+ omn-agent branch-config set -t ./my-repo \
+ --template chore='chore/{ticket_id}-{short_description}'
+ # adds/updates a template for any work type beyond feature/bugfix
+ omn-agent branch-config preview PROJ-42 -t ./my-repo
+ # BC-PREVIEW: PROJ-42 (work type 'feature', template '...') -> feature/on-proj-42-...
+ # -- resolves the branch name a ticket would get, no git side effects at all
+ # (equivalent to 'omn-agent branch PROJ-42 --dry-run', which also shows it)
+ --work-type on preview, and --type on branch itself, override the work type routed from the ticket's command -- useful for a one-off branch that doesn't match the ticket's usual category.
+ Migration and backward compatibility
+ Nothing here is a breaking requirement: an installation with no branch-naming.json at all -- whether it predates this feature or simply never ran init (only install, which doesn't write this file) -- resolves branch names using the exact same built-in defaults the file would otherwise have contained. There is no migration step to run; omn-agent branch and omn-agent branch-config preview work identically with or without a saved config. Adopt project-specific templates whenever you want to, with branch-config set on an existing installation or a fresh init on a new one.
+ One behavior did change from the built-in defaults an earlier version of omn-agent branch used: type prefixes are now feature/bugfix (not feat/fix), and the ticket key in a generated name is lowercased along with everything else. Anyone who wants the old short prefixes back can still get them explicitly with --type feat / --type fix (or configure them as named templates via branch-config set --template feat=...).
```

### T-28 · at 197/274 · `wording: 5. Driving a run`

```diff
- dispatch — the runtime leases the phase and emits the agent's invocation envelope and dispatch prompt under .omn-agent/runs/<run>/states/<phase>/.
+ dispatch — the runtime leases the phase and emits the agent's invocation envelope and dispatch prompt (under .omn-agent/runs/<run>/states/<phase>/).
```

### T-29 · at 199/276 · `wording: 5. Driving a run`

```diff
- complete — the runtime validates the artifact against its contract. Pass → transition; fail → a recorded failure envelope with a recovery action.
- gate — the named human owner approves or rejects, with a rationale. The producing agent can never decide its own gate. Under the opt-in gate policy below, the runtime may take this step itself when the evidence is unambiguously clean.
+ complete — the runtime validates the artifact against its contract; pass → transition, fail → recorded failure envelope with a recovery action.
+ gate — the named human owner approves or rejects with a rationale. The producing agent can never decide its own gate. Under the opt-in gate policy (section 5c), the runtime may take this step itself when the evidence is unambiguously clean.
```

### T-30 · at 204/281 · `wording: 5. rework loop`

```diff
- A human rejects a gate (--gate <name> --decision reject --rationale "…"). A rejection is a classified failure, not just a recorded opinion: the runtime writes a failure envelope naming the phase whose evidence must be rebuilt, and every successor phase blocks with the rejection and rationale visible (--show prints <gate> was rejected by <role> (<rationale>)). The envelope's clearing action states the exact release command; release the phase, re-dispatch it, and the agent reworks in the same worktree — new artifact, revalidation, and the same gate is decided again.
+ A human rejects a gate (--gate <name> --decision reject --rationale "…"). A rejection is a classified failure, not just a recorded opinion: the runtime writes a failure envelope naming the phase whose evidence must be rebuilt, and every successor phase blocks with the rejection and rationale visible (omn-agent run KEY --show prints <gate> was rejected by <role> (<rationale>)). The envelope's clearing action states the exact release command; release the phase, re-dispatch it, and the agent reworks in the same worktree — new artifact, revalidation, and the same gate is decided again.
```

### T-31 · at 207/284 · `wording: 5. rework loop`

```diff
- The ticket was closed, then reopened with changes. Closing released the worktree (branch kept — see Auto-cleanup above). omn-agent branch KEY rebinds the task to a fresh worktree on the same branch, and work continues where the commits left off.
- Bounded rework Each phase declares a retry budget, and once its charged attempts are spent, release refuses to exceed it — the remaining options are a recovery task that repairs the output outside the work item, or a corrected request on a new run. Nothing loops silently forever.
+ The ticket was closed, then reopened with changes. Closing released the worktree (branch kept — section 5a). omn-agent branch KEY rebinds the task to a fresh worktree on the same branch, and work continues where the commits left off.
+ Bounded rework Rework is bounded: each phase declares a retry budget, and once its charged attempts are spent, release refuses to exceed it — the remaining options are a recovery task that repairs the output outside the work item, or a corrected request on a new run. Nothing loops silently forever.
```

### T-32 · at 222/299 · `wording: 5. update loop`

An ellipsis character against three periods.

```diff
- Drive the run: dispatch each eligible phase to its owner agent (auto-binding the feature branch and worktree before the implementation phase if omn-agent branch was never run), ingest completions, and let the runtime auto-decide clean-evidence gates per --gate-policy. The command stops where the host must run a dispatched subagent, or where a gate needs a human (omn-agent run KEY --gate …); re-running continues from live state.
+ Drive the run: dispatch each eligible phase to its owner agent (auto-binding the feature branch and worktree before the implementation phase if omn-agent branch was never run), ingest completions, and let the runtime auto-decide clean-evidence gates per --gate-policy. The command stops where the host must run a dispatched subagent, or where a gate needs a human (omn-agent run KEY --gate ...); re-running continues from live state.
```

### T-33 · at 233/310 · `wording: 5. run, any provider`

```diff
- MSDev tickets are addressed as <PREFIX>-<id> (the trailing number is the Azure DevOps work item id) or as the bare id; the normalized ticket then flows through exactly the machinery above. One invocation fetches the ticket through the named connector, classifies and routes it (Bug → fix-bug, refactor/investigate keywords keep their routing, everything else → implement-feature; --command overrides), materializes the runtime run, binds the feature branch and isolated worktree before implementation, drives dispatch/complete under the gate policy, and — when the run completes — runs the pre-PR checks and pushes, creating or updating the PR (--test-cmd, --base, --draft supported). It pauses only where the host must run a dispatched subagent or a gate is genuinely held for a human (the auto policy's conditions and the Producer Exclusion Rule are unchanged — see Gate auto-approval policy below), printing each stage as it goes: provider resolved, fetched, routed, branch/worktree bound, dispatched, gate auto-decided or held, PR created or updated. Re-running the same command resumes from live state; the resolved provider is recorded on the task (provider in task-plan.json).
+ MSDev tickets are addressed as <PREFIX>-<id> (the trailing number is the Azure DevOps work item id) or as the bare id; the normalized ticket then flows through exactly the machinery above. One invocation fetches the ticket through the named connector, classifies and routes it (Bug → fix-bug, refactor/investigate keywords keep their routing, everything else → implement-feature; --command overrides), materializes the runtime run, binds the feature branch and isolated worktree before implementation, drives dispatch/complete under the gate policy, and — when the run completes — runs the pre-PR checks and pushes, creating or updating the PR (--test-cmd, --base, --draft supported). It pauses only where the host must run a dispatched subagent or a gate is genuinely held for a human (the auto policy's conditions and the Producer Exclusion Rule are unchanged — section 5c), printing each stage as it goes: provider resolved, fetched, routed, branch/worktree bound, dispatched, gate auto-decided or held, PR created or updated. Re-running the same command resumes from live state; the resolved provider is recorded on the task (provider in task-plan.json).
```

### T-34 · at 235/312 · `ordering`

'Who owns which gate' arrives before the gate auto-approval subsection.

```diff
+ Who owns which gate
+ Every flow's gates and their owner roles are listed phase by phase in section 4 — find your flow there for the exact sequence you'll be asked to approve.
```

### T-35 · at 236/315 · `wording: 5c. Gate auto-approval`

```diff
- Every gate is a human decision by default. On a clean, low-severity change that can mean several rubber-stamp approvals in a row, each a stop-and-wait round trip. Opt in to let the runtime itself approve gates whose evidence is unambiguously clean — keeping human judgement for the decisions that warrant it, and the final PR review on GitHub:
+ Every gate is a human decision by default. On a clean, low-severity change that can mean several rubber-stamp approvals in a row, each one a stop-and-wait round trip. Teams that want to keep human judgement for the decisions that warrant it — and the final PR review on GitHub — can let the runtime itself approve a gate whose evidence is unambiguously clean:
```

### T-36 · at 239/318 · `wording: 5c. Gate auto-approval`

One comment line set as two.

```diff
- # or durably: .omn-agent/config/gate-policy.json
+ # or durably, per repository
+ # .omn-agent/config/gate-policy.json
```

### T-37 · at 245/325 · `item 34` · `wording: 5c. Gate auto-approval`

The qualifiers are item 34; the merged condition is split as the source has it.

```diff
- A decision-eligible gate auto-approves only when ALL conditions hold — any one failing keeps that gate on the human path, byte-for-byte today's behavior, and the run prints why it was held:
- the upstream phase's validation passed clean (no undeclared side effects);
- the artifact's declared severity is below severityThreshold (default high — so critical/high always stay human);
- no open question is marked Blocking, and no deviation was escalated;
+ Under auto-on-clean-evidence, a decision-eligible gate auto-approves only when ALL of these hold — any one failing keeps that gate on the human path, byte-for-byte today's behavior, and the run prints why it was held:
+ the upstream phase's validation passed clean (no undeclared side effects; retries are fine if the final attempt passed);
+ the artifact's declared severity is below severityThreshold (default high, so critical/high always stay human; artifact types with no severity field are unaffected);
+ no open question in the artifact is marked Blocking;
+ no deviation was escalated;
```

### T-38 · at 251/332 · `item 34` · `item 35` · `wording: 5c. Gate auto-approval`

'in the policy' is item 34; the recorded-role clause is item 35.

```diff
- the gate isn't pinned human-required.
- Audit trail An auto-decision travels the exact same code path as a human one — identical gate record, transition, and ledger event — attributed to decidedBy: "runtime:auto-policy" with every evaluated condition and threshold in the record. The Producer Exclusion Rule binds the automated decider exactly as it binds a human. Full spec and a worked example: .omn-agent/config/gate-policy.md.
+ the gate isn't pinned human-required in the policy.
+ Audit trail The decision is recorded through the same path as a human one — identical gate record, transition, and ledger event — attributed to decidedBy: "runtime:auto-policy" with every evaluated condition and threshold in the record, so the audit trail is exactly as traceable. The Producer Exclusion Rule binds the automated decider just like a human: the recorded role is always a listed gate owner that did not produce the evidence. Full specification and a worked example (three of four gates auto-approve, one escalates over a blocking open question): .omn-agent/config/gate-policy.md.
```

### T-39 · at 254/335 · `item 36` · `wording: 5d. The final report`

```diff
- When the last phase completes and the last gate is decided, the runtime prints a final report and saves it at .omn-agent/runs/<run-id>/final-report.md. It's rebuilt on every aggregation (so a mid-flight run has a current copy) and renderable any time with omn-agent run KEY --report. It contains, all derived from the persisted run ledger:
- Run — command, workflow, status, start, last activity, total elapsed;
- Agent Activity — per phase: which agent (and version), started, finished, duration, attempts, validation result;
- Gate Decisions — decision, decider, role, decided-at, and Waited: how long the gate held the run between evidence completing and the decision landing. Auto-approved gates show runtime:auto-policy (policy);
- Timeline — every recorded event in commit order: time, actor, event, summary.
+ When the last phase completes and the last gate is decided, the runtime prints a final report to the console and saves it at .omn-agent/runs/<run-id>/final-report.md. It is also rebuilt on every aggregation, so a run inspected mid-flight has a current copy, and you can render it on demand at any time:
+ omn-agent run PROJ-42 -t ./my-repo --report # read-only
+ What it contains, all derived from the persisted run ledger (never asserted):
+ Run — command, workflow, status, start, last activity, total elapsed.
+ Agent Activity — one row per phase in workflow order: which agent (and version), when it started (first dispatch), when it finished (the completion the Validation Engine accepted), how long it took, how many attempts it needed, and its validation result. A phase that needed a retry shows it in the attempts column at a glance.
+ Gate Decisions — decision, decider, role, decided-at, and Waited: how long the gate held the run between its evidence completing and the decision landing. Auto-approved gates show runtime:auto-policy (policy) as the decider, so human and policy decisions are distinguishable in one column.
+ Timeline — every recorded event in commit order: time, actor (agent:omn-qa, human:operator, runtime:validation-engine, …), event type, and summary.
```

### T-40 · at 268/351 · `wording: 5e. Watching a run live` · `ordering`

The callout is reworded; 'Who owns which gate' leaves this position.

```diff
- Read-only by construction Every --watch refresh is an independent status query — the one runtime command that never leases, dispatches, completes, or decides anything — so leaving it running can never advance or approve the run by itself. Advancing stays with your own --dispatch / --complete / --gate calls and their approval prompts. The typical setup: terminal 1 drives the run, terminal 2 watches it.
- Who owns which gate
- Every flow's gates and their owner roles are listed phase by phase in chapter 4 — find your flow there for the exact sequence you'll be asked to approve.
+ Read-only by construction Watching is read-only by construction. Every refresh is an independent status query — the one runtime command that never leases, dispatches, completes, or decides anything — so leaving --watch running can never advance or approve the run by itself. Advancing stays with your own --dispatch / --complete / --gate calls and their approval prompts. The typical setup: terminal 1 drives the run, terminal 2 watches it.
```

### T-41 · at 273/354 · `wording: 6. Yours and the framework's`

```diff
- The installer classifies every file before writing anything, using the install manifest — content hashes recorded at install time:
+ The installer classifies every file before writing anything, using the install manifest (content hashes recorded at install time):
```

### T-42 · at 280/361 · `item 37` · `wording: 6. Yours and the framework's`

```diff
- Your files are safe Edit anything you like — a framework file you modify becomes yours, and upgrades will warn and step around it forever after. --force replaces modified files at framework paths only, and always leaves the previous content at <file>.omn-bak. context/ and memory/ are seeded once and then belong to the project. If .omn-agent wasn't written by this tool, or its manifest is unreadable or from a newer tool version, every command stops with exit 4 and changes nothing.
+ Your files are safe
+ Consequences you can rely on:
+ Edit anything you like. A framework file you modify becomes yours; upgrades will warn and step around it forever after.
+ --force replaces modified files at framework paths only, and always leaves the previous content at <file>.omn-bak.
+ context/ and memory/ are seeded once and then belong to the project — fill in product-context.md, technical-context.md, and memory/architecture.md; the agents read them every run.
+ If .omn-agent exists but wasn't written by this tool, or its manifest is unreadable or from a newer tool version, every command stops with exit 4 and changes nothing.
```

### T-43 · at 286/372 · `wording: 7. Keeping it healthy`

The upgrade sample's --dry-run line, in the other order and without 'first'.

```diff
- omn-agent upgrade ./my-repo --dry-run # see what an upgrade would do
```

### T-44 · at 288/373 · `wording: 7. Keeping it healthy`

```diff
+ omn-agent upgrade ./my-repo --dry-run # see what an upgrade would do first
```

### T-45 · at 289/375 · `wording: 7. Keeping it healthy`

```diff
- Validation also enumerates every file the runtime's own context-slice tables reference (reported as V-SLICE when one is missing) — so a setup gap like a missing dependency-map.md is named on day one, not discovered as a context-integrity-failure several phases into a live run.
+ Validation also enumerates every file the runtime's own context-slice tables reference (reported as V-SLICE when one is missing), so a setup gap — like a missing dependency-map.md — is named on day one instead of surfacing as a context-integrity-failure several phases into a live run.
```

### T-46 · at 307/393 · `item 39` · `wording: 8. Troubleshooting`

```diff
- | INVALID TARGET: not a repository… | The directory has no repo marker. git init there, or omn-agent init <dir> to mark it.
- | Exit 4: …no install manifest | .omn-agent wasn't written by this tool. Move it aside, or restore bootstrap/install-manifest.json from version control, then re-run.
+ | INVALID TARGET: target is not a repository or project root | The directory has no repo marker. git init there, or omn-agent init <dir> to mark it.
+ | Exit 4: …exists with content but has no install manifest | .omn-agent wasn't written by this tool. Move it aside, or restore bootstrap/install-manifest.json from version control, then re-run.
```

### T-47 · at 310/396 · `item 39` · `wording: 8. Troubleshooting`

```diff
- | validate exits 3 | A framework file is corrupt (does not compile / does not resolve). omn-agent install restores the framework copy; your intentional edits are still skipped — doctor shows which.
+ | validate exits 3 (does not compile, does not resolve) | A framework file is corrupt or was edited into a broken state. omn-agent install restores the framework copy (your intentional edits are still skipped — use doctor to see which).
```

### T-48 · at 312/398 · `item 39` · `wording: 8. Troubleshooting`

```diff
- | skip (modified by user) | Expected: you changed that file and it's protected. Keep your version, or upgrade --force to take the framework's (backup kept).
- | Jira 401 / credentials not set | Export the env vars named in config/mcp.json (default JIRA_EMAIL, JIRA_API_TOKEN — an Atlassian API token, not a password). Read at call time, never stored.
- | Exit 8 on run | Normal: the step is side-effecting and wasn't approved. Re-run with --approve, or answer y at the prompt.
- | A phase shows blocked | The state table names the reason (missing input, unregistered capability, failed validation). omn-agent run <KEY> --show prints it; the failure envelope in runs/<run>/… carries the recovery action.
- | V-SLICE: …dependency-map.md | The dependency map was deleted or never generated. omn-agent context generate dependency-map -t <repo> recreates it from your repo's manifests.
+ | Upgrade says skip (modified by user) | Expected: you changed that file and it's being protected. Keep your version, or upgrade --force to take the framework's (backup kept).
+ | Jira credentials are not set / 401 | Export the env vars named in config/mcp.json (default JIRA_EMAIL, JIRA_API_TOKEN — an Atlassian API token, not a password). They are read at call time and never stored.
+ | Exit 8 on run | Normal: the step is side-effecting and wasn't approved. Re-run with --approve or answer y at the prompt.
+ | A run phase is blocked | The state table names the reason (missing input, unregistered capability, failed validation). omn-agent run <KEY> --show prints it; the failure envelope in runs/<run>/… carries the recovery action.
+ | V-SLICE: context-slice member missing: dependency-map.md | The dependency map was deleted or never generated. omn-agent context generate dependency-map -t <repo> recreates it from your repo's manifests.
```

### T-49 · at 322/408 · `item 39` · `wording: 8. Troubleshooting`

```diff
- | branch: …exists but is not a registered git worktree | Something else created a directory at the task's worktree path. Move it aside, or omn-agent branch KEY --force to delete and recreate it.
- | branch: …checked out in the main working tree (or another worktree) | Git allows a branch in one worktree at a time. Switch the main checkout away (git checkout <base>), or remove the stale worktree (git worktree remove <path>), then re-run.
- | the worktree bound to task … is missing | The worktree directory was deleted by hand. omn-agent branch KEY recreates it — the branch and its commits are unaffected.
- | task …'s worktree was released: ticket closed | The ticket closed, so sync/pull removed the worktree. If work must continue anyway, omn-agent branch KEY rebinds it with a fresh worktree.
+ | branch: worktree path already exists but is not a registered git worktree | Something else created a directory at the task's worktree path. Move it aside, or omn-agent branch KEY --force to delete and recreate it.
+ | branch: branch '…' is checked out in the main working tree (or another worktree) | Git allows a branch in one worktree at a time. Switch the main checkout away (git checkout <base>), or remove the stale worktree (git worktree remove <path>), then re-run.
+ | run --dispatch/pr: the worktree bound to task … is missing | The worktree directory was deleted by hand. omn-agent branch KEY recreates it (the branch and its commits are unaffected).
+ | run --dispatch/pr: task …'s worktree was released: ticket closed (…) | The ticket closed, so sync/pull removed the worktree. If work must continue anyway, omn-agent branch KEY rebinds it with a fresh worktree.
```

### T-50 · at 331/417 · `wording: 9. Customizing`

```diff
- Skills. skills/ holds the engineering playbooks agents apply — testing strategy, error handling, security. Tune them to your standards.
+ Skills. skills/ holds the engineering playbooks agents apply (testing strategy, error handling, security, …). Tune them to your standards.
```

### T-51 · at 333/419 · `item 20` · `wording: footer`

Separators are wording; the source statement is folded into the banner (item 20).

```diff
- Framework source: the repository's .claude/ tree · Tool: omn-agent 0.1.0 · Full command reference: omn-agent --help and the repo's README.md · This guide is versioned at docs/USER-GUIDE.md.
+ Framework source: this repository's .claude/ tree. Tool: omn-agent 0.1.0. Full command reference: omn-agent --help and README.md.
```


## Element-and-class sequence: 1211 segments before, 1447 after, 66 hunks

### E-01 · at 3/3 · `derived: banner`

```diff
+ div.banner
+ span.tag
+ code
+ code
```

### E-02 · at 10/14 · `wording: masthead`

Two bolded runs the source's lede carries.

```diff
+ strong
+ strong
```

### E-03 · at 11/17 · `ordering` · `item 17`

The framework chain leaves the masthead.

```diff
- div.chain
- span
- b
- span
- b
- span
- b
- span
- b
- span
- b
- span.gate
- b
- span
```

### E-04 · at 48/40 · `ordering` · `item 17`

The framework chain arrives in chapter 1.

```diff
+ div.chain
+ span
+ b
+ span
+ b
+ span
+ b
+ span
+ b
+ span
+ b
+ span.gate
+ b
+ span
```

### E-05 · at 79/85 · `wording: 2. Installation` · `derived: code-marking`

The '# confirm health' comment line's marking.

```diff
+ span.comment
```

### E-06 · at 91/98 · `wording: 2. Installation`

The regenerate command as a sample block.

```diff
+ pre
```

### E-07 · at 128/136 · `wording: 2. Installation`

Install table: one code span per path.

```diff
+ code
+ code
+ code
+ code
+ code
+ code
+ code
```

### E-08 · at 132/147 · `wording: 2. Installation`

Install table: one code span per path.

```diff
+ code
+ code
```

### E-09 · at 138/155 · `wording: 2. Installation`

Install table: one code span per path.

```diff
+ code
+ code
+ code
```

### E-10 · at 223/243 · `wording: 3. Two ways to work`

Italics around a quoted connection message.

```diff
- em
```

### E-11 · at 234/253 · `wording: 3. Two ways to work`

Italics around a cross-reference.

```diff
- em
```

### E-12 · at 267/285 · `item 31`

The Section column's header cell.

```diff
+ th
```

### E-13 · at 273/292 · `item 31`

```diff
+ td
```

### E-14 · at 279/299 · `item 31`

```diff
+ td
```

### E-15 · at 285/306 · `item 31`

```diff
+ td
```

### E-16 · at 292/314 · `item 31`

```diff
+ td
```

### E-17 · at 298/321 · `item 31`

```diff
+ td
```

### E-18 · at 304/328 · `item 31`

```diff
+ td
```

### E-19 · at 310/335 · `item 31`

```diff
+ td
```

### E-20 · at 359/385 · `item 41`

```diff
+ p
```

### E-21 · at 415/442 · `wording: 4.1 to 4.7`

The 4.2 opening as its own paragraph.

```diff
+ p
```

### E-22 · at 462/490 · `wording: 4.1 to 4.7`

The 4.3 opening as its own paragraph.

```diff
+ p
```

### E-23 · at 650/679 · `item 32` · `wording: 4.1 to 4.7`

Bold for italics; the --scope-file code span is item 32.

```diff
- em
+ strong
+ code
```

### E-24 · at 672/702 · `item 33`

```diff
+ code
+ strong
```

### E-25 · at 674/706 · `item 42`

```diff
+ p
```

### E-26 · at 699/732 · `item 40` · `derived: code-marking`

The branch sample's commentary lines.

```diff
+ span.comment
+ span.comment
+ span.comment
+ span.comment
```

### E-27 · at 700/737 · `item 19` · `wording: 5a. Branch and PR lifecycle`

The branch-config code span is dropped with item 19; the surrounding sentence is reworded.

```diff
- code
```

### E-28 · at 706/742 · `item 24`

```diff
+ div.tbl
+ table
+ tr
+ th
+ th
+ tr
+ td
```

### E-29 · at 707/750 · `item 24`

```diff
+ td
```

### E-30 · at 708/752 · `item 24`

```diff
+ tr
+ td
```

### E-31 · at 709/755 · `item 24`

```diff
+ td
```

### E-32 · at 710/757 · `item 24`

```diff
+ tr
+ td
```

### E-33 · at 711/760 · `item 24`

```diff
+ td
```

### E-34 · at 712/762 · `item 24`

```diff
+ tr
+ td
```

### E-35 · at 713/765 · `item 24` · `wording: 5a. Branch and PR lifecycle`

The table's last cell; then the default-base sentence's bold.

```diff
+ td
+ code
+ p
+ strong
```

### E-36 · at 725/781 · `item 25`

```diff
+ p
+ ul
+ li
+ strong
+ code
+ li
+ strong
+ strong
+ strong
+ code
+ li
+ strong
+ strong
+ li
+ strong
+ code
+ li
+ strong
```

### E-37 · at 727/801 · `item 25`

```diff
+ code
+ li
```

### E-38 · at 734/810 · `wording: 5a. Branch and PR lifecycle` · `derived: callout-shape`

Auto-cleanup code spans; the Branch safety callout now wraps several blocks.

```diff
+ code
+ code
+ code
+ code
+ div.callout
+ span.tag
+ p
```

### E-39 · at 738/821 · `wording: 5a. Branch and PR lifecycle` · `derived: code-marking`

The branch-defaults.json sample block the published form had set inline.

```diff
+ pre
+ code
+ span.comment
+ p
+ code
+ code
```

### E-40 · at 740/829 · `item 27`

```diff
+ strong
+ code
+ code
+ code
+ p
+ strong
```

### E-41 · at 749/844 · `ordering`

The Branch safety callout leaves its published position.

```diff
- div.callout
- span.tag
```

### E-42 · at 752/845 · `item 29`

```diff
+ p
```

### E-43 · at 753/847 · `item 23` · `item 29` · `item 30`

pr create detail, the outcome sentence, and the whole of section 5b.

```diff
+ code
+ code
+ code
+ code
+ code
+ code
+ code
+ code
+ code
+ p
+ code
+ code
+ code
+ code
+ p
+ code
+ code
+ code
+ code
+ code
+ code
+ code
+ h3
+ p
+ code
+ code
+ code
+ code
+ pre
+ code
+ p
+ h3
+ div.tbl
+ table
+ tr
+ th
+ th
+ th
+ tr
+ td
+ code
+ td
+ td
+ code
+ tr
+ td
+ code
+ td
+ td
+ tr
+ td
+ code
+ td
+ td
+ code
+ code
+ h3
+ p
+ strong
+ code
+ code
+ ol
+ li
+ li
+ code
+ code
+ code
+ code
+ li
+ code
+ code
+ li
+ code
+ li
+ code
+ code
+ code
+ p
+ strong
+ code
+ code
+ em
+ ul
+ li
+ code
+ li
+ code
+ code
+ code
+ code
+ li
+ li
+ code
+ h3
+ pre
+ code
+ span.comment
+ span.comment
+ span.comment
+ span.comment
+ span.comment
+ span.comment
+ span.comment
+ span.comment
+ p
+ code
+ code
+ code
+ code
+ h3
+ p
+ code
+ code
+ code
+ code
+ code
+ code
+ code
+ p
```

### E-44 · at 801/1014 · `wording: 5. rework loop`

```diff
- em
```

### E-45 · at 835/1047 · `wording: 5. update loop`

```diff
- em
```

### E-46 · at 877/1088 · `wording: 5. run, any provider`

```diff
- em
```

### E-47 · at 885/1095 · `ordering`

'Who owns which gate' arrives here.

```diff
+ a
+ h3
+ p
```

### E-48 · at 890/1103 · `wording: 5c. Gate auto-approval` · `derived: code-marking`

```diff
+ span.comment
```

### E-49 · at 891/1105 · `wording: 5c. Gate auto-approval`

```diff
+ code
```

### E-50 · at 893/1108 · `wording: 5c. Gate auto-approval`

The conditions as an ordered list.

```diff
- ul
+ ol
```

### E-51 · at 896/1111 · `wording: 5c. Gate auto-approval`

```diff
- em
+ strong
```

### E-52 · at 903/1118 · `item 34` · `wording: 5c. Gate auto-approval`

```diff
+ li
```

### E-53 · at 919/1135 · `item 36`

```diff
+ pre
```

### E-54 · at 920/1137 · `item 36` · `derived: code-marking`

```diff
+ span.comment
+ p
```

### E-55 · at 927/1146 · `wording: 5d. The final report`

```diff
- em
+ strong
```

### E-56 · at 931/1150 · `item 36`

```diff
+ code
+ code
+ code
```

### E-57 · at 953/1175 · `wording: 5e. Watching a run live`

```diff
+ strong
```

### E-58 · at 957/1180 · `ordering`

'Who owns which gate' leaves its published position.

```diff
- h3
- p
- a
```

### E-59 · at 989/1209 · `item 37` · `derived: callout-shape`

```diff
+ p
+ ul
+ li
+ strong
+ li
+ code
+ em
+ code
+ li
```

### E-60 · at 994/1223 · `item 37`

```diff
+ li
+ code
+ strong
```

### E-61 · at 1088/1320 · `item 39` · `wording: 8. Troubleshooting`

```diff
- td
```

### E-62 · at 1091/1322 · `item 39` · `wording: 8. Troubleshooting`

```diff
+ td
```

### E-63 · at 1108/1340 · `item 39` · `wording: 8. Troubleshooting`

```diff
+ code
```

### E-64 · at 1170/1403 · `item 39`

```diff
+ code
+ code
```

### E-65 · at 1174/1409 · `item 39`

```diff
+ code
+ code
```

### E-66 · at 1210/1447 · `item 20`

```diff
- code
```
