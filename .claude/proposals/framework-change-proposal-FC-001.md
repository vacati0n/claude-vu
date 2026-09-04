# Framework Change Proposal: Route the Review Package

```yaml
frameworkChangeProposal:
  proposalId: FC-001
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-3e22f11cb34d
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-001
- Change title: Route the review package artifact into the review workflow
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-3e22f11cb34d
- Authored on: 2026-08-18

## Change Statement

- Objective: give the contracted artifact type `review-package.md` an emitting phase, so a review verdict becomes validated run evidence rather than prose in an Output Artifact column.
- In scope: the Output Artifact cell of one Phase Model row, and the gap record that raised the defect.
- Out of scope: gate ownership, agent manifest outputs, capability registration, the three other review-producing phases.
- Acceptance basis: the artifact type is counted as routed by `verify_validators.py`, and registry coverage, per-phase blocked reasons, and every committed run's evidence are unchanged.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/workflows/review-pull-request.md` | `SR-1` | in-scope | The one machine-read contract this change edits |
| `.claude/runtime/README.md` | `SR-1` | in-scope | Known gap 7, the record that raised the defect |
| `.claude/runs/run-3e22f11cb34d/state.json` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/proposals/framework-change-proposal-FC-001.md` | `SR-5` | out-of-scope | This record; the governance record of the change, not a second change |

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains a routed artifact type it did not have, so a phase declares a contracted output where it previously declared prose
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: scope-and-acceptance
- Required inputs supplied: `feature-request`, `change-request`, `business-intent`, `architecture-context`

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-3e22f11cb34d/execution-request.json` | `/implement` over `implement-feature` v1.0.0, four inputs, submitted 2026-08-18T13:42:26Z |
| `E-2` | `runs/run-3e22f11cb34d/run-ledger.json` | Run ledger written by the runtime, runtime version 0.4.0 |
| `E-3` | `runs/run-3e22f11cb34d/events.jsonl` | Ordered canonical events across 20 state transitions |
| `E-4` | `runs/run-3e22f11cb34d/state.json` | Six phase work items: 2 completed, 4 blocked, each blocker with a recorded reason |
| `E-5` | `runs/run-3e22f11cb34d/completion-package.md` | Aggregated package: phase ledger, gate decisions, module provenance with digests |
| `E-6` | `runs/run-3e22f11cb34d/states/solution-design-and-risk-assessment/artifacts/technical-design.md` | 13-section design selecting `O-001` over four alternatives, with three decision records at Proposed |
| `E-7` | `runs/run-3e22f11cb34d/states/solution-design-and-risk-assessment/validation-report.json` | `design_validator.py` PASS, 78/78, 10 not machine-checkable, on attempt 2 |

Two further artifacts of the same run carry the same weight and are linked here for completeness: `runs/run-3e22f11cb34d/states/execution-planning/artifacts/execution-plan.md` and its validation report `runs/run-3e22f11cb34d/states/execution-planning/validation-report.json`, PASS 45/45.

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | blocked | Blocked `awaiting_capability_registration`; scope and acceptance supplied by the operator as the run's `business-intent` input, which the profile requires for this class | operator | `runs/inputs/review-package-routing-business-intent.md` |
| `execution-planning` | `planner` | completed | Executed by the registered agent; 14 tasks, 8 waves, validated 45/45 | planner | `runs/run-3e22f11cb34d/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed by the registered agent. Attempt 1 was rejected: an undeclared write plus six blocking validator failures, classified `policy-failure`, escalated, cleared by the operator, and retried. Attempt 2 validated 78/78 | architect | `runs/run-3e22f11cb34d/states/solution-design-and-risk-assessment/failure-envelope.json` |
| `implementation` | `omn-dev-1-implement` | blocked | Blocked `awaiting_capability_registration`; the operator applied the design's `M-001` and `M-010` in sequencing order `P-005` then `P-006`, changing one Phase Model cell and the gap record | operator | `workflows/review-pull-request.md`, `runtime/README.md` |
| `quality-review` | `omn-dev-2-reviewer` | blocked | Blocked `awaiting_capability_registration`; review performed by the operator as the design's Test Strategy Focus Areas require, and recorded in Verification below | operator | this proposal, Verification section |
| `documentation-and-release-handoff` | `omn-documentation` | blocked | Blocked `awaiting_capability_registration`; documentation impact discharged by the gap record edit `M-010` and by `reports/self-hosting-operating-mode-report-2026-08-18.md` | operator | `runtime/README.md` known gap 7 |

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Planning Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Plan validated 45/45; every task traces to the supplied intent; no blocking open question |
| Design Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Design validated 78/78 after a rejected attempt and a repair pass; one cell changes in one machine-read contract; rollback is that one cell. `architect` produced the evidence and is excluded from deciding |

The Scope, Review, Verification, and Closure Gates are recorded undecided in the completion package, because each assesses evidence a blocked phase never produced. An undecided gate holds its successor rather than being waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Routed-artifact coverage counts the review package | `python .claude/runtime/verify_validators.py` | pass; `V1` names `review-package.md (1 phase(s))` where it previously named none |
| Registry coverage unchanged | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6 checks, dispatchable 3 of 36, blocked 33, identical to the before state |
| No blocked reason traded | `python .claude/runtime/verify_registry_coverage.py` | pass; `code-quality-review` remains `awaiting_capability_registration`, and no per-phase reason changed anywhere |
| Derived edge set preserved | inspection | pass; `structural-compliance <- code-quality-review` survives as a hard edge, its basis moving from Input-token match to Phase Model row order |
| Committed run evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, and the same for `run-308f4d0ee447`, `run-b6780677468b`, and this run |
| Recovery path exercised under a real rejection | `python .claude/runtime/framework_runtime.py recovery --run-id run-3e22f11cb34d` | pass; one classified `policy-failure`, non-retryable, escalated with a clearing action, then resolved |

## Risk and Rollback

- Blast radius: one Phase Model cell and one paragraph of a gap record. No registry, agent contract, gate row, or runtime module changes.
- Risk assessment: the design's `R-004` and `R-008` carry the two risks that materialised as expected — the declaration is half of an output contract, so the phase still blocks, and `structural-compliance` remains blocked for contract reconciliation. The residual risk is that a reader takes routed to mean dispatchable; the gap record now states the difference in the same paragraph.
- Rollback procedure: restore the prose token `quality findings with correction requests` in the `code-quality-review` Output Artifact cell, and restore the previous text of known gap 7. Nothing else was written outside run evidence, and no run evidence would be invalidated.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6 checks, unresolved=0, dispatchable 3 of 36 unchanged |
| `FR-02` | Validator coverage and decisiveness | pass | 4/4 checks, 7 artifact types, `review-package.md` now counted as routed |
| `FR-03` | Recovery behaviour | pass | 41/41 checks across 3 injected runs |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN, plus three further runs |
| `FR-05` | Self-hosting governance resolves | pass | `verify_self_hosting.py` S1 to S8 |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-3e22f11cb34d` is a `/implement` run; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Runtime behaviour unchanged; `RUNTIME_VERSION` stays 0.4.0. `M-003` records the resolution path as no-change-verified |
| `FR-08` | Documentation matches delivered behaviour | pass | `runtime/README.md` known gap 7 and the Validation Engine coverage table both updated in the same change |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | The change claims routing, not dispatchability, and the gap record states which of the two it delivered |
| `FR-10` | Rollback stated | pass | Risk and Rollback above; one cell and one paragraph |
| `FR-11` | Multi-phase state machine still proves out | pass | `verify_multi_phase.py --run-id run-c5a8d50d3238` 15/15 PROVEN |
| `FR-12` | Release note where consumer-visible behaviour changed | not-applicable | No behaviour a consumer depends on changed: the routed phase cannot be dispatched, so no run's output differs |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Three review-producing phases keep prose Output Artifact entries. Extending the declaration is available and is a scope decision | omn-product-owner | Deferred; recorded in known gap 7 and as `Q-001` in the design |
| `O-002` | `review-pull-request/structural-compliance` remains blocked with `awaiting_contract_reconciliation`; closing it is a role-boundary reconciliation, not a column edit | architect, omn-tech-lead | Deferred; recorded as `Q-004` in the design |
| `O-003` | `design_validator.py` check `D15.1` matches gate names with `[A-Z][A-Za-z]+ Gate`, so a three-word gate name in the matrix cannot be cited verbatim | omn-tech-lead | Open; found by the architect during this change and recorded as `Q-007` against `M-011` |
| `O-004` | `design_validator.py` check `D17.1` discovers decision records case-sensitively, which on a case-insensitive filesystem an agent cannot correct by rewriting a filename. The three records are named `architecture-decision-record-FC-001-D-00n.md` rather than the canonical form | architect | Open; the superseded lowercase files were deleted by the operator, and the accepted names were left unchanged because renaming an accepted artifact would rewrite validated evidence |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Planning and Design Gates, recorded by the operator
- Acceptance basis: both executed phases validated by their registered validators, every invariant in the supplied change request verified by command, and every deferral recorded rather than closed silently
