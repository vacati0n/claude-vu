# Architecture Context — Wave 1 Delivery Core Agent Rollout

Current structural state of the framework, as read from source on 2026-08-18. Every claim
below is checkable against the file named beside it.

## 1. The capability chain a phase must clear

`runtime/framework_runtime.py` gates every state work item on five guards. `G1-CAPABILITY`
resolves the whole chain and is the one that stops Wave 1 phases today:

| Link | Source of truth | Wave 1 state |
|---|---|---|
| active record in `registry/agents.yaml` | `registry/agents.yaml` | missing for all four agents |
| manifest declaring the workflow and phase in `supportedWorkflows` | `agents/<id>/manifest.yaml` | no manifest exists for any of the four |
| host registration | `agents/<id>.agent.md` | present for all twelve phase owners |
| phase-mandatory skills resolvable | `registry/skills.yaml` | resolves; 101 of 101 references |
| registered validator for the phase's output artifact | `VALIDATORS` in `framework_runtime.py` | see section 3 |

`G2-CONTEXT` is a separate guard: `CONTEXT_SLICE_PHASE` declares `execution-planning`,
`solution-design-and-risk-assessment`, and `scope-invariants-and-risk-profile`, and nothing else.
Any other phase blocks there even after `G1-CAPABILITY` clears.

## 2. The runtime module set pattern

Two exist, `agents/planner/` and `agents/architect/`. Both hold `manifest.yaml` plus seven
modules in a declared `loadOrder`:

```
system.md      operating-charter        authoritative operating instructions and invariants
identity.md    agent-contract           the Standard Agent Contract implementation
reasoning.md   reasoning-procedure      deterministic analysis procedure
execution.md   execution-lifecycle      lifecycle states, phase gates, retry, escalation
output.md      output-contract          structural and semantic contract for the artifact
quality.md     quality-contract         self-verification checks, gates, rejection rules
examples.md    reference-examples       conforming and non-conforming examples
```

`resolve_output_contract` requires `quality.md` to exist by path, independently of the manifest,
and requires each declared output's `templateRef` and `contractRef` to resolve. The manifest
also carries `authorityScope`, `inputs`, `outputs`, `supportedWorkflows`, `skills`,
`collaboration`, `determinism`, and `versioning`.

Each of the four Wave 1 agents already has a single-file prose contract at `agents/<id>.md`,
around 50 lines. `agents/planner/manifest.yaml` records the precedent for what happens to it:
`versioning.supersedes` names the superseded single file with a reason.

## 3. Output artifacts and validators

`framework_runtime.py:334` reads the Phase Model Output Artifact cell literally, stripping only
backticks. `resolve_output_contract` then requires that exact string to be present in the
owning manifest's `outputs[].artifact` and to be a key of `VALIDATORS`.

Registered validators (7): `execution-plan.md`, `technical-design.md`, `bug-analysis.md`,
`investigation-report.md`, `release-note.md`, `review-package.md`, and
`framework-change-proposal.md`. The first two are hand-written against the Planner and Architect
numbered check sets; four are declared as data and executed by `artifact_contract.py`; the last
is a governance artifact no phase emits.

Wave 1 phases against that map:

| Workflow / Phase | Owner | Output Artifact column | Resolvable |
|---|---|---|---|
| `implement-feature/scope-and-acceptance` | `omn-product-owner` | scoped requirement summary | no, prose |
| `implement-feature/implementation` | `omn-dev-1-implement` | code changes and automated test evidence | no, prose |
| `fix-bug/fix-implementation` | `omn-dev-1-implement` | corrective change set with regression tests | no, prose |
| `refactor/refactor-implementation` | `omn-dev-1-implement` | incremental refactor changes with updated tests | no, prose |
| `review-pull-request/code-quality-review` | `omn-dev-2-reviewer` | `review-package.md` | **yes** |
| `implement-feature/quality-review` | `omn-dev-2-reviewer` | review findings log, verification report | no, prose |
| `release/artifact-packaging` | `omn-dev-2-reviewer` | versioned artifacts with packaging evidence | no, prose |
| `refactor/safety-net-establishment` | `omn-qa` | strengthened test suite and baseline validation record | no, prose |
| `refactor/behavioral-validation` | `omn-qa` | parity validation report and regression status | no, prose |
| `fix-bug/regression-validation` | `omn-qa` | verification evidence and residual risk notes | no, prose |
| `review-pull-request/test-risk-validation` | `omn-qa` | test adequacy verdict with residual risk notes | no, prose |
| `release/candidate-validation` | `omn-qa` | validation evidence with release candidate verdict | no, prose |

`runtime/README.md` known gap 7 records the precedent for changing one of these columns:
`review-pull-request/code-quality-review` was moved from a prose entry to `review-package.md`
under proposal `FC-001`, and the reasoning plus four rejected alternatives are held in
`runs/run-3e22f11cb34d/states/solution-design-and-risk-assessment/`. The same note records that
extending the declaration to the three other review-producing phases is available and is a
product decision about scope, not a structural finding.

`runtime/README.md` known gap 9 records the converse: four artifact types gained a validator
without their phases becoming dispatchable, because a validator removes one condition of five.

## 4. Artifact contract engine

`artifact_contract.py` executes artifact contracts declared as data rather than coded. Four of
the seven validators are built this way. A new artifact type therefore has two available
shapes: a declarative contract executed by that engine, or a hand-written validator where the
owning agent ships a numbered check set in its `quality.md` that a validator must reproduce
exactly.

`templates/bug-analysis.md`, `templates/investigation-report.md`, and `templates/release-note.md`
were raised to 1.1.0 to become decidable: each gained a leading metadata block and the tables
that turn its agent's decision rules into something checkable. `templates/review-package.md`
was added new. That is the precedent for what a new template must carry.

## 5. Gate ownership

Read from `workflows/workflow-gate-matrix.md`, never invented by the runtime. 28 gate references
across the active Phase Models, all decidable, with the Producer Exclusion Rule enforced —
including through the `omn-` alias the matrix still uses for the architecture role. Wave 1 phases
are closed by the Scope Gate, Review Gate, Verification Gate, Implementation Gate, Regression
Gate, Code Quality Gate, and Artifact Gate.

`agents/omn-product-owner.agent.md` records that this role is a listed owner of the Scope Gate it
produces evidence for, so under the Producer Exclusion Rule the decision rests with
`omn-business-analyst`.

## 6. Self-hosting constraints on this increment

`config/self-hosting-profile.md`:

- `SR-1` puts every path under `.claude/**` in routing scope; `SR-3` to `SR-6` exempt runs,
  reports, proposals, and `__pycache__`, and the exemption set is closed.
- `C-3` requires every phase of the routed workflow to be enqueued and either executed with a
  validated artifact or blocked with a recorded reason.
- `E-6` and `E-7` require a phase artifact and its validation report where the routed workflow
  has a dispatchable phase. `implement-feature` has two, so both are required here and cannot be
  satisfied by the run's own record of blocking.
- `C-7` requires every mandatory item of `validation/framework-release-checklist.md` recorded
  with its result.

## 7. Recorded structural risks

From `runtime/README.md` known gaps, unchanged by this increment and relevant to it:

- Gate decisions are recorded, not solicited; an undecided gate holds its successor indefinitely.
- Retry is scheduled, not driven; a deadline is evaluated when a command next reads the run.
- No lease expiry timer; a lost adapter leaves a work item `running` until `release` is run.
- `workflows/workflow-engine.md` has no planning state and disagrees with
  `workflows/implement-feature.md`; the registry points at the latter, so routing is unambiguous.
- `workflows/workflow-engine.md` names a different owner than the Phase Model for the refactor
  scope state and for two analysis states in `investigate` and `research`.
