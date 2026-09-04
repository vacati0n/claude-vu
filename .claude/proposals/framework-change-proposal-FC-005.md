# Framework Change Proposal: Unblock the fix-bug Entry Phase and Close Wave 1

```yaml
frameworkChangeProposal:
  proposalId: FC-005
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-27e36c138498
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-005
- Change title: Unblock the fix-bug entry phase, repair the detection gap it exposed, and close Wave 1 of the agent rollout
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-27e36c138498
- Authored on: 2026-08-19

## Authoring Baseline

- Authored at: 2026-08-19T10:20:00Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 31 of 36
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: make the `fix-bug` workflow able to reach any phase at all, so that a defect can be repaired through the framework and so that `omn-qa` can satisfy conditions `D-4` and `D-5` of the Agent Definition of Done, which no other active workflow could give it.
- In scope: the `triage-and-impact` Output Artifact cell and the Input column that named its prose string, the context-slice declaration for that phase, the coverage gap that let the condition pass every check, and the false agreement claim in the output-contract reader's own documentation.
- Out of scope: the artifact-type decision for the five remaining prose-cell phases, and any contract governing what the Output Artifact column must carry. Both are recorded open, escalated to `architect`.
- Acceptance basis: a run of `/bugfix` reaches and completes `regression-validation` with its artifact accepted by the registered validator; no `fix-bug` phase reports `awaiting_capability_registration`; no previously passing verifier check regresses.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/workflows/fix-bug.md` | `SR-1` | in-scope | Output Artifact cell, the Input column naming its prose string, and the narrative that contradicted the corrected table |
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | `CONTEXT_SLICE_PHASE` entry for `triage-and-impact`, and the corrected claim in `declared_output_artifact` |
| `.claude/runtime/verify_validators.py` | `SR-1` | in-scope | Checks `V5` and `V6` added; the `bug-analysis.md` mutation expressed as a derivation |
| `.claude/runtime/verify_multi_phase.py` | `SR-1` | in-scope | `M6` evaluated against the run's recorded baseline per `GD-001` |
| `.claude/runs/run-27e36c138498/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/reports/**` | `SR-4` | out-of-scope | Closeout report emitted by this increment |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaved other than its contract declares — four phases of `fix-bug` reported dispatchable while none could ever be reached
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug`

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-27e36c138498/execution-request.json` | resolved |
| `E-2` | `runs/run-27e36c138498/run-ledger.json` | resolved |
| `E-3` | `runs/run-27e36c138498/events.jsonl` | resolved |
| `E-4` | `runs/run-27e36c138498/state.json` | resolved |
| `E-5` | `runs/run-27e36c138498/completion-package.md` | resolved |
| `E-6` | `runs/run-27e36c138498/states/regression-validation/artifacts/validation-report.md` | resolved |
| `E-7` | `runs/run-27e36c138498/states/regression-validation/validation-report.json` | resolved |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed by the registered agent; severity `critical`, reproducibility `deterministic` established against this run's own transition log; blast radius widened on evidence from one phase to six; root cause deliberately withheld as the next phase's work | omn-dev-1-bug-analyst | `runs/run-27e36c138498/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed by the registered agent; closed the open question by showing it mis-framed — no rule governs the Output Artifact column, and three consumers read it under three unstated requirements | omn-dev-1-bug-analyst | `runs/run-27e36c138498/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed by the registered agent over two attempts. Attempt 1 was refused as a `policy-failure` for declaring writes under `runs/**`, which the manifest excludes; cleared by recorded operator policy exception; attempt 2 wrote no run-store path and proved it by digesting all 213 files under `runs/` before and after | omn-dev-1-implement | `runs/run-27e36c138498/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed by the registered agent; verdict `pass-with-reservations`, all three acceptance criteria met with the third recorded as breached once during the run and repaired | omn-qa | `runs/run-27e36c138498/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed by the registered agent; disposition `held` rather than closed, because an open high-severity escalation bars closure under its own decision rules | omn-orchestrator | `runs/run-27e36c138498/states/closure-and-communication/validation-report.json` |

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Severity and reproducibility both evidenced against the run's own transition log; `omn-dev-1-bug-analyst` produced the evidence and is excluded from deciding |
| Fix Gate | approve | omn-dev-2-reviewer | operator on behalf of omn-dev-2-reviewer | Artifact validated 32/32, side effects declared only after the policy exception; both regressions closed at their cause and independently re-measured |
| Verification Gate | approve | omn-dev-2-reviewer | operator on behalf of omn-dev-2-reviewer | Artifact validated 31/31; all three acceptance criteria met; `omn-qa` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-documentation | operator on behalf of omn-documentation | Artifact validated 34/34; `omn-orchestrator` produced the evidence and is excluded from deciding |

Every gate this workflow declares was decided. None was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6, 31 of 36 phases dispatchable |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6, including the two checks this change added |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 |
| Multi-phase state machine, this run's predecessor | `python .claude/runtime/verify_multi_phase.py --run-id run-93b302cbdb28` | pass; 15/15 PROVEN |
| Multi-phase state machine, the checklist's pinned run | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN, restored from 14/15 |
| Prior committed evidence | `python .claude/runtime/verify_vertical_slice.py --run-id run-b6780677468b --slice planner` | pass; 10/10 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py --mode-evidence --release-checklist` | pass; 10/10 with this proposal in place |

## Risk and Rollback

- Blast radius: one workflow specification, one runtime module, two verification scripts. No registry record, agent contract, or template changed.
- Risk assessment: two risks materialised and both were caught before the Fix Gate. A verifier regression was introduced by this run's own success — committing real `bug-analysis.md` artifacts broke a mutation anchor pinned to a fixture's severity — and a second historical run was failed by a check reading current state rather than its recorded baseline, the fourth instance of the condition `GD-001` governs. Both were repaired at their cause rather than around them, and each repair was checked for decisiveness so that a check repaired into one that cannot fail would not pass as repaired.
- Rollback procedure: restore the prose Output Artifact cell and the Input column in `workflows/fix-bug.md`, remove the `triage-and-impact` entry from `CONTEXT_SLICE_PHASE`, and revert `V5`, `V6`, the `bug-analysis.md` mutation derivation, and the `M6` baseline evaluation. Reverting returns `fix-bug` to a workflow no run can enter, and invalidates the executed-phase evidence of all five phases of this run, including the only evidence that satisfies `omn-qa` `D-4` and `D-5`.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6, 31 of 36 dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6, restored from 5/6 by expressing the `bug-analysis.md` mutation as a derivation |
| `FR-03` | Recovery behaviour | pass | 41/41 |
| `FR-04` | Committed evidence still verifies | pass | `run-b6780677468b` and `run-308f4d0ee447` 10/10 each |
| `FR-05` | Self-hosting governance resolves | pass | 10/10 with this proposal in place |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-27e36c138498` is a `/bugfix` run; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0; a context-slice entry and a corrected comment change no behaviour the version denotes |
| `FR-08` | Documentation matches delivered behaviour | pass | The `fix-bug` narrative was corrected to agree with its own Phase Model table |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Five phases executed with validated artifacts; five phases across four workflows remain blocked and are recorded, not omitted |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 on both runs |
| `FR-12` | Release note where consumer-visible behaviour changed | not-applicable | `fix-bug` gains no consumer-visible behaviour; it gains the ability to be entered at all |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | No rule governs what the Output Artifact column must contain, while three consumers read it under three unstated requirements. Correcting the five remaining prose cells does not remove the cause, and the divergence runs both ways: a cell naming two artifacts blocks the phase while the coverage proof demands a validator for each | architect | Open, escalated. Tracked as `O-001` of `FC-004`; this proposal narrows it with measured evidence and does not close it |
| `O-002` | `verify_multi_phase.py` writes replay bookkeeping into the run store it verifies, so no agent whose contract excludes `runs/**` can execute it. Verification that changes what it measures is available only to the operator | architect | Open, escalated. Surfaced by this run when the condition refused an implementing agent's result |
| `O-003` | `omn-orchestrator` is routed the action of authoring the change proposal that accounts for a run, but its manifest permits no repository write in any phase, so the routed role cannot perform it | omn-tech-lead | Open. This proposal was authored by the operator for exactly that reason |
| `O-004` | Five runs hold a durably blocked phase, not the two the upstream artifacts of this run stated. The operator's framing to the phase agents understated it; the closure phase measured the store and corrected it | omn-orchestrator | Recorded. No action beyond accuracy in future accounts |
| `O-005` | Five phases across four workflows remain blocked at `awaiting_contract_reconciliation`, `review-pull-request` worst affected because its blocked phase sits at row 2 of 5, so no pull request can reach a merge decision | architect | Open; the same decision as `O-001` |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates, omn-documentation at the Closure Gate, each recorded by the operator
- Acceptance basis: all five phases executed by their registered agents and validated by their registered validators, every gate decided by a non-producing owner, one classified failure recovered through the runtime's own policy path, two regressions repaired at their cause with decisiveness re-checked, and five open items recorded with an owner
