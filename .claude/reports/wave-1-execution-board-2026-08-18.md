# Wave 1 Execution Board — Delivery Core Agents

Date: 2026-08-18
Source plan: `reports/self-hosting-execution-plan-2026-08-18.md` section 9.3, Wave 1
Source checklist: `reports/agent-skill-rollout-daily-checklist-2026-08-18.md` Days 1–6
Baseline: `reports/maturity-snapshot-2026-08-18.json`
Execution mode: self-hosting (`config/self-hosting-profile.md`, class `capability-addition`)

## 1. What this board is

The tracking surface for the four Wave 1 delivery core agents against the five-part Agent
Definition of Done. It records state, not intent: every cell marked done names the evidence
that decides it, and every cell not marked done names the blocker the runtime recorded.

This board is an evidence report under `reports/`, which `config/self-hosting-profile.md`
`SR-4` places out of routing scope. It is emitted by the rollout increment; it is not a
second change.

## 2. Definition of Done (per agent)

| ID | Condition | Decided by |
|---|---|---|
| `D-1` | Runtime module set exists and load order resolves | `agents/<id>/manifest.yaml` + declared `loadOrder` files on disk |
| `D-2` | Host entrypoint is invocable | `agents/<id>.agent.md` resolves, `verify_registry_coverage.py` C3 |
| `D-3` | Active record exists in `registry/agents.yaml` | registry read |
| `D-4` | At least one completed run references the agent as owner | `runs/<run-id>/state.json` work item `status: completed` |
| `D-5` | Output artifacts pass validator checks | `runs/<run-id>/states/<phase>/validation-report.json` |

`D-1` through `D-3` are preconditions the framework can be moved to. `D-4` and `D-5` are
consequences that only a real run produces, so no agent is promoted on the first three alone.

## 3. Board state

Legend: `done` / `open` / `blocked`. Counts are from the Day-1 baseline snapshot.

| Agent | D-1 module set | D-2 entrypoint | D-3 registry record | D-4 completed run | D-5 validator pass | Status |
|---|---|---|---|---|---|---|
| `omn-product-owner` | open | done | open | open | blocked | not started |
| `omn-dev-1-implement` | open | done | open | open | blocked | not started |
| `omn-dev-2-reviewer` | open | done | open | open | open | not started |
| `omn-qa` | open | done | open | open | blocked | not started |

Wave 1 aggregate: 4/20 DoD conditions satisfied at baseline, all of them `D-2`.

## 4. Phase ownership in scope

Phases each Wave 1 agent owns across the seven active workflows, with the Output Artifact
column exactly as its Phase Model declares it.

| Agent | Workflow / Phase | Output Artifact column | Names a file? | Validator registered? |
|---|---|---|---|---|
| `omn-product-owner` | `implement-feature/scope-and-acceptance` | `scope-definition.md` (was `scoped requirement summary`) | **yes** | **yes** |
| `omn-dev-1-implement` | `implement-feature/implementation` | code changes and automated test evidence | no | n/a |
| `omn-dev-1-implement` | `fix-bug/fix-implementation` | corrective change set with regression tests | no | n/a |
| `omn-dev-1-implement` | `refactor/refactor-implementation` | incremental refactor changes with updated tests | no | n/a |
| `omn-dev-2-reviewer` | `review-pull-request/code-quality-review` | `review-package.md` | **yes** | **yes** |
| `omn-dev-2-reviewer` | `implement-feature/quality-review` | review findings log, verification report | no | n/a |
| `omn-dev-2-reviewer` | `release/artifact-packaging` | versioned artifacts with packaging evidence | no | n/a |
| `omn-qa` | `refactor/safety-net-establishment` | strengthened test suite and baseline validation record | no | n/a |
| `omn-qa` | `refactor/behavioral-validation` | parity validation report and regression status | no | n/a |
| `omn-qa` | `fix-bug/regression-validation` | verification evidence and residual risk notes | no | n/a |
| `omn-qa` | `review-pull-request/test-risk-validation` | test adequacy verdict with residual risk notes | no | n/a |
| `omn-qa` | `release/candidate-validation` | validation evidence with release candidate verdict | no | n/a |

## 5. The structural finding this board opens with

**Registering an agent is necessary for its phase to dispatch, and for eleven of these twelve
phases it is not sufficient.**

`framework_runtime.py` parses the Output Artifact column literally: line 334 takes the cell
text and strips backticks, and `resolve_output_contract` then requires that exact string to
appear both in the owning manifest's `outputs[].artifact` and in the `VALIDATORS` map. A
prose cell such as `scoped requirement summary` therefore cannot resolve to an output
contract, whatever the registry says about the agent.

Consequence for sequencing: the baseline blocked reason
`awaiting_capability_registration` is the *first* failure in the `G1-CAPABILITY` chain, not
the only one. Clearing it on a prose-output phase reveals the next one rather than making the
phase dispatchable. Eleven of the twelve Wave 1 phases need an artifact-type decision — a named
artifact file, a template, and a registered validator — before `D-4` and `D-5` are reachable at
all.

`review-pull-request/code-quality-review` is the exception and the shortest path to a
dispatchable Wave 1 phase: it already names `review-package.md`, `review_package_validator.py`
is already registered, and `templates/review-package.md` already exists. What it lacks is the
agent side only.

A second condition applies to every phase: `G2-CONTEXT` requires an entry in
`CONTEXT_SLICE_PHASE`, which today declares three phases. None of the twelve above is one of
them.

This finding is the input to the routed increment; it is not a decision. Which artifact types
the prose phases should emit, and whether the Phase Model columns change, belongs to the
architect phase.

## 6. Increment sequence

One primary capability increment at a time, per the execution policy. Each row is routed
under `/implement` as change class `capability-addition`.

| # | Increment | Primary surface | Wave 1 DoD advanced | Status |
|---|---|---|---|---|
| `W1-I0` | Day 1: board, baseline snapshot, planner and architect routing of the rollout | reports + run evidence | none directly; establishes the plan and design of record | in progress |
| `W1-I1` | `omn-product-owner` runtime module set and registry record | `agents/omn-product-owner/`, `registry/agents.yaml` | D-1, D-3 | done; the phase also needed the artifact-type decision from section 5 — `scope-definition.md`, its template, and `scope_definition_validator.py` — and is now dispatchable and executed in `run-93b302cbdb28` |
| `W1-I2` | `omn-dev-1-implement` runtime module set and registry record | `agents/omn-dev-1-implement/`, `registry/agents.yaml` | D-1, D-3 | pending |
| `W1-I3` | `omn-dev-2-reviewer` runtime module set and registry record | `agents/omn-dev-2-reviewer/`, `registry/agents.yaml` | D-1, D-3 | pending |
| `W1-I4` | `omn-qa` runtime module set and registry record | `agents/omn-qa/`, `registry/agents.yaml` | D-1, D-3 | pending |
| `W1-I5` | Wave 1 closeout run crossing scope, implementation, review, quality | run evidence | D-4, D-5 | pending |

`W1-I5` depends on the artifact-type decision named in section 5. If that decision lands
outside Wave 1 scope, `D-4` and `D-5` stay open for the agents whose phases it governs, and
this board records them as open rather than reporting Wave 1 complete.

## 7. Blockers

| ID | Blocker | Raised by | Affects | State |
|---|---|---|---|---|
| `B-1` | Eleven of twelve Wave 1 phases declare a prose Output Artifact, which cannot resolve to an output contract or a validator | Runtime source, `framework_runtime.py:334` and `resolve_output_contract` | D-4, D-5 for all four agents | open, routed to the architect phase of `W1-I0` |
| `B-2` | No Wave 1 phase has a `CONTEXT_SLICE_PHASE` entry, so each blocks at `G2-CONTEXT` even once `G1-CAPABILITY` clears | Runtime source, `CONTEXT_SLICE_PHASE` | D-4, D-5 for all four agents | open, routed to the architect phase of `W1-I0` |

## 8. Update rule

This board is updated by the increment that changes the state it records, in the same change
as the evidence. A cell moves to `done` only when the artifact named in section 2 exists and
the relevant verifier re-run reports it. No cell is advanced on the strength of a plan.
