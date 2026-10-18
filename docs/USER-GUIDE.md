# AI Engineering Framework Handbook

*The user guide for teams working with the AI Engineering Framework in Claude Code.*

The framework turns AI-assisted development from "chat with a model" into a governed
delivery process. Work travels through **workflows** made of **phases**; each
phase is owned by a **specialized agent** that produces a validated **artifact**;
progress is held at **human gates** until someone accountable approves. The
whole framework lives under `.claude/`, where Claude Code reads it directly:
you start work with a Claude Code slash command, and there is no separate CLI
or installer.

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
  `.claude/runs/` — state table, event stream, failure envelopes, recovery
  ledger. Nothing is silently skipped: a phase that cannot execute is *blocked
  with a recorded reason*, never dropped.

## 2. Setup {#install}

**Prerequisites:** Claude Code, Python 3.10+, and **PyYAML** for the runtime
(`pip install pyyaml`). The runtime under `.claude/runtime/` imports nothing
else.

There is nothing to install. Open the repository in Claude Code and the
framework is already in place: Claude Code reads the slash commands from
`.claude/commands/` and the subagents from `.claude/agents/`, and the runtime
is called directly with `python .claude/runtime/framework_runtime.py`.

### What lives where

| Directory under `.claude/` | Contents |
|---|---|
| `commands/` | the slash-command contracts; `command-catalog.md` is the authoritative index |
| `agents/` | one subagent registration (`<agent>.agent.md`) and one contract directory per role |
| `workflows/` | the phase-based lifecycle specifications and the gate matrix |
| `skills/` `templates/` `prompts/` | engineering playbooks, artifact schemas, prompt patterns |
| `registry/` | the discovery indexes the runtime resolves routing against |
| `runtime/` | the state engine, invocation gateway, artifact validators, and verification scripts |
| `config/` `domain-model/` `validation/` | routing, quality-gate, and runtime policy; the domain specifications; the release checklist |
| `context/` `memory/` | product, technical, and release context; durable engineering knowledge |
| `runs/` `reports/` `proposals/` | run evidence written by the runtime, generated reports, change proposals |

`.claude/CLAUDE.md` describes the layer model these directories implement.

## 3. Two ways to work {#work}

### A. Inside Claude Code — slash commands

Ask for work with a command. Each command routes to its workflow and the
agents take over, phase by phase:

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
| `/optimize-memory` | refactor | scope, invariants & risk profile | architect → developer → QA |

`/optimize-memory` rewrites the memory, context, and standing instruction files
to their minimum token cost without changing what they instruct; it runs
through refactor because "nothing observable changed" is the invariant claim
that workflow exists to hold to account. Grouped runbooks such as
`/implement:implement-feature` or `/review:review-pr` document how to start a
lifecycle through one of these contracts.

[Section 4](#flows) walks each of these flows end to end — phases, owners, artifacts,
and the gates you'll approve.

### B. From the terminal — the runtime directly

The slash commands drive the runtime; anything they do can also be done by
calling it yourself from the repository root:

```bash
# materialize a run from an input document
python .claude/runtime/framework_runtime.py plan --command implement \
    --input feature-request=.claude/runs/inputs/<request>.md
python .claude/runtime/framework_runtime.py next   --run-id <run-id>   # the exact next command
python .claude/runtime/framework_runtime.py status --run-id <run-id>   # read-only: state table
```

`--command` selects the routing command (`implement`, `bugfix`, `refactor`,
`investigate`, `research`, `review`, `quality-scan`, `release`, …) and
defaults to `implement` for a new run. For a run that already exists, the
run's own record is the authority, so `--command` may be omitted on every
later call and one that disagrees with the run is refused. Input documents
conventionally live under `.claude/runs/inputs/`. If the input has no
acceptance criteria, the Scope Gate is where they get defined.

> **Changing the framework itself**
> A change to the framework's own files is routed, not chosen by judgement.
> Classify the path, route the change class to its command, and verify the
> result against the release checklist:
>
> ```bash
> python .claude/runtime/self_hosting.py classify --path <path>
> python .claude/runtime/self_hosting.py route --intent <change-class>
> python .claude/runtime/verify_self_hosting.py --release-checklist
> ```
>
> Such a change also produces a change proposal from
> `templates/framework-change-proposal.md` that links the runs that carried
> it — see [section 6](#ownership).

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

All flows share the same run mechanics — plan, dispatch, complete,
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

**Enter with:** an agreed feature request. A request with no acceptance
criteria is fine — the Scope Gate is where they get written down.
**Done when:** the Closure Gate approves — acceptance criteria verified,
docs and release notes updated.

**Filming it:** add `--demo` to `/implement` (or to the runtime's `plan`), start the
recording, and the run films itself and cuts a narrated presentation video from the real
screen recording when the Closure Gate approves — see section 5e.

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

`/optimize-memory` runs this same flow over the memory and context files.

**Enter with:** a defined refactor scope, explicitly documented behavioral
invariants, and baseline tests or metrics.
**Done when:** invariants are proven unchanged, quality metrics improved or
within accepted limits, and the technical-debt delta is recorded with
follow-ups.

### 4.4 Investigate & research — `/investigate` / `/research` {#flow-investigate}

For questions that need an evidence-backed answer before anyone commits to
building. **No code changes** — the deliverable is a recommendation the
decision owner can act on. The two flows are twins: `/investigate` targets a
concrete problem or decision; `/research` explores a broader option space.

| # | Phase (investigate / research) | Owner | Artifact | Gate after (owners) |
|---|---|---|---|---|
| 1 | problem-framing / research-framing | business analyst | requirement-framing.md | Framing Gate (BA, PO) |
| 2 | technical-discovery / technical-validation | context agent | investigation-report.md | Technical Gate (context agent, architect) |
| 3 | option-analysis / option-synthesis | tech lead | technical-recommendation.md | — |
| 4 | recommendation / recommendation-draft | tech lead | technical-recommendation.md | Recommendation Gate (tech lead, orchestrator) |
| 5 | publication / findings-publication | documentation | release-note.md (findings) | — |

**Enter with:** a question, its decision owner, and the scope, timeline,
and constraints.
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

`/test` enters this flow at its test-risk-validation phase.

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

**Enter with:** `/quality-scan <scope>`. The same flow from the terminal:

```bash
# write the scope document, then plan and dispatch in one call
python .claude/runtime/framework_runtime.py dispatch --command quality-scan \
    --input quality-scan-scope=.claude/runs/inputs/backend-quality-scan-scope.md

# ... the host runs the dispatched reviewer subagent ...

# ingest and validate the review package; the run stops at the human gate
python .claude/runtime/framework_runtime.py complete --run-id <run-id> \
    --phase repository-quality-scan

# the tech lead's decision, recorded like any other gate
python .claude/runtime/framework_runtime.py gate --run-id <run-id> \
    --gate "Quality Handoff Gate" --decision approve --owner-role tech-lead \
    --decided-by <who> --rationale "package accepted as review of record"
```

A re-scan with a **changed scope document is a new run**: the run identity is
a digest of the inputs, so a changed input is a different request.

**Done when:** the validated review package is held at the Quality Handoff
Gate. The tech lead — a human, by default gate policy — reads it and decides:
accept it as the review of record, route the correction requests as cleanup
work (`/refactor` for structure, `/bugfix` for defects it uncovered), or
reject it back for a re-scan. The verdict vocabulary maps naturally:
`approve` = no material junk, `approve-with-corrections` = cleanup
recommended, `reject` = cleanup required before further review or merge.

## 5. Driving a run {#run}

A slash command drives these steps for you; this is what happens underneath,
and what you can run yourself when you want step-level control:

```bash
python .claude/runtime/framework_runtime.py plan --input feature-request=<path>   # materialize the run
python .claude/runtime/framework_runtime.py next --run-id <run-id>                # read-only: the next step
python .claude/runtime/framework_runtime.py dispatch --run-id <run-id> --phase scope-and-acceptance
python .claude/runtime/framework_runtime.py complete --run-id <run-id> --phase scope-and-acceptance
python .claude/runtime/framework_runtime.py gate --run-id <run-id> --gate "Scope Gate" \
    --decision approve --owner-role product-owner --decided-by <who> \
    --rationale "AC agreed with stakeholder"
python .claude/runtime/framework_runtime.py status --run-id <run-id>              # read-only: full state table
python .claude/runtime/framework_runtime.py report --run-id <run-id>              # read-only: who did what, when
```

Every command is safe to repeat: a run is identified by a digest of its
command, workflow, and inputs, so planning the same request twice re-enters
the run it already reached, and a repeated dispatch or completion is
recorded as a replay and changes nothing. Gate decisions are human by
default; a team that wants clean, low-risk gates decided by the runtime
itself opts in with the gate policy -- see section 5a. When the run
completes, the **final report** is written and printed -- see section 5b.
And while agents are working, you can
[watch the run live in a second terminal](#live-view) -- see section 5c.

The cycle for each phase:

{.steps}
1. **dispatch** — the runtime leases the phase and emits the agent's invocation
   envelope and dispatch prompt (under `.claude/runs/<run>/states/<phase>/`).
2. The **owner agent executes** (a Claude Code subagent) and produces the
   phase artifact.
3. **complete** — the runtime validates the artifact against its contract;
   pass → transition, fail → recorded failure envelope with a recovery action.
4. **gate** — the named human owner approves or rejects with a rationale.
   The producing agent can never decide its own gate. Under the opt-in gate
   policy (section 5a), the runtime may take this step itself when the
   evidence is unambiguously clean.

> **Recorded decisions**
> A gate decision names both the owner role being exercised (`--owner-role`)
> and who actually recorded it (`--decided-by`). The runtime refuses a role
> that does not own the gate and enforces the Producer Exclusion Rule, so the
> agent that produced the evidence can never be recorded as its approver.

### When changes are requested: the rework loop {#rework}

An implemented change that comes back with change requests is not a new
run — it's the same run stepping backwards once, with everything recorded.
Which loop you're in depends on where the "no" came from:

- **The validator rejects the artifact** (`complete` fails). The runtime
  records a failure envelope and schedules a retry within the phase's
  attempt budget. Re-dispatching carries the previous validation findings
  into the agent's prompt, so it repairs against the named failures instead
  of starting blind. Every extra pass shows up in the final report's
  attempts column.
- **A human rejects a gate** (`gate --decision reject --rationale "…"`). A
  rejection is a classified failure, not just a recorded opinion: the
  runtime writes a failure envelope naming the phase whose evidence must be
  rebuilt, and every successor phase blocks with the rejection and rationale
  visible in `status`. The rollback itself is a second human decision: the
  envelope's clearing action states the exact `rollback` command, filled in —
  `python .claude/runtime/framework_runtime.py rollback --run-id <run> --gate
  "<gate>" --target <phase> --owner-role <role> --decided-by <who> --rationale
  "…"` — and a listed owner of the gate (not the producing agent) runs it,
  naming the phase to return to (the gated phase by default, or an earlier
  completed phase such as `implementation`). The runtime then *supersedes*
  the target's completed downstream cone — that phase and every completed
  phase that depends on it, the gated one included: each returns to pending
  as a new attempt under the same idempotency key, its previous artifact left
  untouched at its committed path, and the rejected gate is re-armed with the
  rejection kept in its decision history. While the rejection stands, `next`
  names this rollback command first and offers no decision on another gate
  closing the same phase: approving such a gate before the rollback would
  make the rollback refuse (an approved gate cannot be re-armed), leaving a
  shallower target or a new run as the remedies. Re-dispatch the phase and
  the agent reworks against the rejection rationale, which rides in its
  envelope as `prior_rejection` — new artifact in an attempt-scoped
  directory, revalidation, and the same gate is decided again by a human
  (never auto-approved after a rollback).
- **A pull request gets "changes requested".** That review lives outside the
  run. Make the fix on the same branch — through `/bugfix`, or by
  re-dispatching the implementation phase if the rework should travel
  through review and verification again — and push: the open PR updates.
- **The request itself changed** — new acceptance criteria, a reworded
  description, a scope tweak. A changed input is a new run: the runtime pins
  every input digest at run creation and re-verifies it on every operation,
  so an edited input document can never be carried into an existing run.
  Plan again from the updated input.

> **Bounded rework**
> Rework is bounded: each phase declares a retry budget, and once its charged
> attempts are spent, `release` refuses to exceed it and `rollback` refuses to
> re-enter the phase — the remaining options are a recovery task that repairs
> the output outside the work item, or a corrected request on a new run.
> A rollback re-entry spends the same budget as a retry, so a third rejection
> of the same phase routes to abort or a new run. Nothing loops silently forever.

### Who owns which gate

Every flow's gates and their owner roles are listed phase by phase in
[section 4](#flows) — find your flow there for the exact sequence you'll be asked to
approve.

## 5a. Gate auto-approval policy

Every gate is a human decision by default. On a clean, low-severity change
that can mean several rubber-stamp approvals in a row, each one a stop-and-wait
round trip. Teams that want to keep human judgement for the decisions that
warrant it can let the **runtime itself** approve a gate whose evidence is
unambiguously clean:

```bash
# per invocation
python .claude/runtime/framework_runtime.py next --run-id <run-id> --gate-policy auto

# or durably, per repository
# .claude/config/gate-policy.json
{
  "mode": "auto-on-clean-evidence",
  "severityThreshold": "high",
  "pinned": { "fix-bug": { "Closure Gate": "human-required" } }
}
```

Under `auto-on-clean-evidence`, a decision-eligible gate auto-approves **only
when ALL of these hold** — any one failing keeps that gate on the human path,
and the run prints *why* it was held:

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
> escalates over a blocking open question): `.claude/config/gate-policy.md`.

## 5b. The final report: who did what, when

When the last phase completes and the last gate is decided, the runtime prints
a **final report** to the console and saves it at
`.claude/runs/<run-id>/final-report.md`. It is also rebuilt on every
aggregation, so a run inspected mid-flight has a current copy, and you can
render it on demand at any time:

```bash
python .claude/runtime/framework_runtime.py report --run-id <run-id>   # read-only
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
  (`agent:qa`, `human:operator`, `runtime:validation-engine`, …), event
  type, and summary.

## 5c. Watching a run in the terminal {#live-view}

`status` is the run's read-only view, safe to call as often as you like from a
second terminal while agents work:

```bash
python .claude/runtime/framework_runtime.py status --run-id <run-id>                       # the tree
python .claude/runtime/framework_runtime.py status --run-id <run-id> --compact             # tree only
python .claude/runtime/framework_runtime.py status --run-id <run-id> --json                # machine-readable
python .claude/runtime/framework_runtime.py status --run-id <run-id> --no-color            # force the plain table
python .claude/runtime/framework_runtime.py recovery --run-id <run-id> --open-only          # why it is not proceeding
```

On a terminal, `status` renders a **colorized, phase-grouped tree** — phase →
step → gate — with a status icon and color per row (done, running, pending,
blocked, retrying, failed), and the reason that matters right now: a blocked
step shows its blocked reason, a retrying step shows its attempt and deadline,
a pending gate lists the owner roles still to decide. `--compact` stops after
the tree, before the transitions, recovery ledger, and events sections.

The rendering degrades gracefully everywhere: the `NO_COLOR` convention and
`--no-color` force the plain table, and redirected output (piping to a file)
gets the plain table automatically. `--json` emits the same tree as a
`framework.runtime/status-view.v1` document for external dashboards or editor
integrations.

> **Read-only by construction**
> **Watching is read-only by construction.** `status`, `recovery`, `report`,
> and `metrics` never lease, dispatch, complete, or decide anything, so
> calling them can never advance or approve the run. Advancing stays with
> `dispatch`, `complete`, and `gate`. The typical setup: Claude Code drives
> the run, a second terminal watches it.

## 5d. What an agent reads, and what a run cost

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
- **Parallel dispatch.** The runtime's `next` output lists every phase that may run
  alongside the one it names. In the shipped workflows almost every phase consumes its
  predecessor's artifact, so groups are usually one phase wide.

What it cost is recorded in `runs/<run-id>/execution-metrics.json`, summarised in the final
report and printed by the runtime's `metrics` subcommand: duration, phases, agent
invocations, skill reads, context files read, validation runs, gate decisions, and a
byte-based context estimate under the old and the new rules.

## 5e. Filming a run as a demo: `--demo`

Any `/implement` run can film itself. The result is a real screen recording of Claude
Desktop doing the work, cut down by the run's own telemetry into a short presentation with
titles, a live workflow rail, and a voiceover.

Two commands, and the second is optional because a run that completes while filming cuts
itself:

```bash
python .claude/runtime/framework_runtime.py plan --demo --demo-record \
    --input feature-request=.claude/runs/inputs/<request>.md
#   ... then drive the run as usual; the camera is already rolling ...
python .claude/runtime/framework_runtime.py demo --run-id <run-id> --record-stop --build
```

`--demo-record` starts the camera during planning, before the run's first event, so the film
opens on the run being accepted. For a run that already exists, or one started with
`/implement --demo`, start the camera separately with
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
the work. The framework creates its own scene collection and profile for the capture and
never touches yours.

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
`.claude/runtime/demo/hooks.settings.json` into the host's `.claude/settings.json`. Only tool
names and a short excerpt of each target are recorded, never file contents. The command in
that file carries a `<framework-dir>` placeholder, since a file on disk cannot know the name
of the directory it sits in; run `framework_runtime.py demo --print-hook` to get the block
with the path already filled in. Skip the merge and the film still builds, but it shows only
the runtime's own events.

Without `--demo` none of this is loaded: the runtime's only cost is one file-existence check
per event.

## 6. What's yours and what's the framework's {#ownership}

Everything under `.claude/` is checked into your repository, so version control
is the record of every change. What differs is how a change is governed:

| The file… | Who changes it, and how |
|---|---|
| `context/`, `memory/` | **yours** — fill them in and keep them current; the agents read them every run |
| `runs/`, `reports/` | written by the runtime; run evidence is immutable once committed |
| framework files: `agents/`, `workflows/`, `commands/`, `registry/`, `runtime/`, `templates/`, `config/`, … | changed through the self-hosting route, never by hand-picked judgement |

> **Framework changes are governed** {.yours}
> Consequences you can rely on:
>
> - **Context is yours.** Write real content into `context/product-context.md`,
>   `context/technical-context.md`, and `memory/architecture.md`; every agent's
>   context slice includes them.
> - **A framework change is routed.** `self_hosting.py classify --path <path>`
>   names its change class and `self_hosting.py route --intent <change-class>`
>   names the command that must carry it — so the framework is developed
>   through its own workflows.
> - **Every framework change leaves a record.** A change proposal from
>   `templates/framework-change-proposal.md`, saved under `proposals/`, links
>   the runs that carried it; `verify_self_hosting.py` re-reads those runs
>   rather than trusting the proposal's claims.
> - **History stays as it was.** Older evidence under `runs/`, `reports/`, and
>   `proposals/` still names agents with the retired `omn-` prefix; the
>   runtime maps those names to the current ones instead of rewriting the
>   record.

## 7. Keeping the framework healthy {#health}

The runtime ships its own proofs. Each runs alone, with no arguments, and ends
with an `N/N checks passed` summary:

```bash
python .claude/runtime/verify_registry_coverage.py   # routing, Phase Models, owners, dispatchability
python .claude/runtime/verify_validators.py          # every artifact type accepts and rejects correctly
python .claude/runtime/verify_recovery.py            # induces failures and proves the recovery
python .claude/runtime/verify_self_hosting.py --release-checklist   # before a framework release
python -m unittest discover -s tests                 # the unit-test suite
python tools/run_tests_parallel.py                   # the same suite, in parallel
```

`verify_registry_coverage.py` reports, per phase, whether it can be dispatched
and the exact reason when it cannot — so a setup gap is named before it
surfaces as a blocked phase several steps into a live run.

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
| `ModuleNotFoundError: No module named 'yaml'` | The Python running the runtime lacks PyYAML. `pip install pyyaml` into the same interpreter you call `framework_runtime.py` with. |
| `plan` refuses a `--command` for an existing run | Expected: the run's own record is the authority on its command. Omit `--command` on every call after the first. |
| A run phase is `blocked` | The state table names the reason (missing input, unregistered capability, failed validation). `status --run-id <run>` prints it; `recovery --run-id <run>` prints the failure envelope and its clearing action. |
| `dispatch` is refused with a deadline | The phase is `retrying` and waiting out its backoff. `next` reports when it becomes dispatchable; the runtime has no process of its own, so nothing fires at the deadline until a command reads the run. |
| A dispatched agent never reported back | The runtime cannot tell a slow adapter from a lost one. `release --run-id <run> --phase <phase> --reason tool_failure` declares it lost and schedules the retry. |
| `complete` refuses an artifact that already completed | Committed evidence is immutable: the artifact was edited after it was accepted. Restore it, or reject the gate and roll back to rebuild it under a new attempt. |
| The agent identifier does not resolve in Claude Code | The agent registration was added after the session started. Restart the session, or dispatch with `--dispatch-mode bootstrap`, which supplies the registration as the prompt. |
| A gate didn't auto-approve under `--gate-policy auto` | Expected: some condition failed and the run printed which (`held for a human decision (…)`). Severity at/above threshold, a blocking open question, an escalated deviation, an open QA defect, a pinned gate, or no approved precedent each hold it. Decide it by hand as usual. |
| A gate was rejected / changes requested after implementation | Expected rework loop, not a dead end. The failure envelope names the exact `rollback` command; a listed gate owner runs it naming the phase to return to, the runtime supersedes that phase (previous artifact kept) and re-arms the gate, then re-dispatch and the agent reworks before the gate is decided again by a human — see [the rework loop](#rework). |
| A `--demo` run produced `presentation_demo.gif` or only `.html`, not `.mp4` | Expected fallback: the runtime found no `ffmpeg` (GIF) or no Pillow (HTML with text frames). `runs/<run>/demo/build-manifest.json` names the missing piece. Install `ffmpeg` (or `pip install imageio-ffmpeg`) and re-run `framework_runtime.py demo --run-id <run> --build`; the recording is untouched. |
| The demo drew a dashboard instead of showing the real window | Nothing was filmed for that run, or the edit failed and fell back. `demo --run-id <run> --snapshot` reports whether a capture exists; `build-manifest.json` names the reason under `fallbacks`. Film it with `demo --run-id <run> --record-start`. |
| `--record-start` reports that the window could not be brought to the front | The ffmpeg backend records the window's rectangle on screen, so it refuses rather than film whatever is covering it. Click the Claude Desktop window and start again, or switch on OBS's WebSocket server (Tools → WebSocket Server Settings) to capture the window itself regardless of what is in front. |
| The film shows only part of the run | Beats that happened before the recording started are not in the footage; the manifest says how many under `fallbacks.coverage`. Start the recording before driving the run, or re-cut a hand-made recording with `--capture-offset <seconds>`. |
| The demo film is silent | No text-to-speech engine produced audio; the manifest's `narration.attempts` lists what was tried and why each failed. On Windows the built-in SAPI voice needs no install; elsewhere `pip install pyttsx3` (offline) or `edge-tts` (online, needs ffmpeg) adds one. |
| The demo film is much longer than `--demo-seconds` | Expected in the default explaining mode: there the narration sets the length and `--demo-seconds` is ignored, because a sentence is never cut short. For a fixed short cut use `demo --run-id <run> --build --pace brisk --no-explain --target-seconds 60`. |
| The demo film is too fast, or assumes too much knowledge | It was cut brisk. Re-cut the same footage with `demo --run-id <run> --build --pace relaxed --explain`, and add `--speech-rate -3` to slow the voice further. No new recording is needed. |
| Long stretches of the film sit on a still frame | The narration needs more time than the recording holds. `build-manifest.json` reports it under `narration.fit` as `beats_held`. Record a longer run, or shorten the film with `--no-explain`. |

## 9. Customizing the framework for your team {#custom}

- **Context first.** The highest-leverage 30 minutes: write real content into
  `context/product-context.md`, `context/technical-context.md`, and
  `memory/architecture.md`. Every agent's context slice includes them. Keep
  `dependency-map.md` current too — it's the blast-radius record root-cause
  analysis and design phases read.
- **Templates.** Artifact templates live under `templates/`; the validators
  check structure, so keep the required sections. A template change is a
  framework change, so route it with `self_hosting.py` ([section 6](#ownership)).
- **Skills.** `skills/` holds the engineering playbooks agents apply
  (testing strategy, error handling, security, …). Tune them to your standards.
- **Memory.** `memory/decision-log.md`, `known-issues.md`, and
  `coding-standard.md` are living documents — the framework reads them, your
  team maintains them. `/optimize-memory` keeps them lean without changing
  what they say.

---

*Framework source: this repository's `.claude/` tree. Command index:
`.claude/commands/command-catalog.md`. Full runtime reference:
`.claude/runtime/README.md`.*
