# Framework Change Proposal: Wave 1 Delivery Core Rollout and Reconciliation

```yaml
frameworkChangeProposal:
  proposalId: FC-004
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-93b302cbdb28
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-004
- Change title: Wave 1 delivery core agent rollout, with the contract supersession and governance corrections its reconciliation required
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-93b302cbdb28
- Authored on: 2026-08-19

## Authoring Baseline

- Authored at: 2026-08-19T08:00:00Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 30 of 36
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`

## Change Statement

- Objective: give the delivery path after planning and design an executable owner, so a framework run traverses scope, implementation, review, and quality rather than halting at capability resolution.
- In scope: runtime module sets and active registry records for the ten unregistered phase owners; three role-shaped artifact types with templates and validators; per-phase context-slice declarations; the supersession of the two shared contract modules the module-set architecture replaced; and the point-in-time correction to governance evidence that the rollout exposed.
- Out of scope: the six phases that remain blocked at contract reconciliation, each of which is recorded rather than narrowed away; Wave 4 specialist profiles.
- Acceptance basis: every executed phase validated by its registered validator, every invariant re-verified after the change, and every phase that still cannot dispatch reported with the reason the runtime recorded.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/agents/*/` | `SR-1` | in-scope | Ten new runtime module sets, plus the reference migration across all twelve |
| `.claude/agents/superseded-contracts.md` | `SR-1` | in-scope | New register resolving the two superseded shared contract modules |
| `.claude/agents/retired-roles.md` | `SR-1` | in-scope | Register resolving three retired role identifiers |
| `.claude/registry/agents.yaml` | `SR-1` | in-scope | Ten active records added, three retired records added |
| `.claude/registry/skills.yaml` | `SR-1` | in-scope | S04 and S05 activated |
| `.claude/registry/templates.yaml` | `SR-1` | in-scope | Records for the new artifact types |
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | Validator map, context-slice declarations and their per-member attribution, runtime version |
| `.claude/runtime/*_validator.py` | `SR-1` | in-scope | Six new validators; `change_proposal_validator.py` corrected to point-in-time |
| `.claude/runtime/verify_self_hosting.py`, `verify_vertical_slice.py` | `SR-1` | in-scope | Completion Rule and execution proof corrected to point-in-time |
| `.claude/workflows/*.md` | `SR-1` | in-scope | Output Artifact and Input columns for the phases the disposition covers |
| `.claude/config/self-hosting-profile.md` | `SR-1` | in-scope | Governance decision `GD-001` recorded |
| `.claude/templates/*.md` | `SR-1` | in-scope | New artifact templates; the change-proposal template gains the authoring baseline |
| `.claude/runs/run-93b302cbdb28/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/reports/**` | `SR-4` | out-of-scope | Board, baseline snapshot, and reconciliation report emitted by this increment |

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains agent runtime contracts, registry records, artifact types, validators, and phase execution it did not have
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`, `change-request`, `business-intent`, `architecture-context`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path .claude/agents/omn-product-owner/manifest.yaml` returns `SR-1`, framework-internal; `route --intent capability-addition` returns `/implement` over `implement-feature`

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-93b302cbdb28/execution-request.json` | resolved |
| `E-2` | `runs/run-93b302cbdb28/run-ledger.json` | resolved |
| `E-3` | `runs/run-93b302cbdb28/events.jsonl` | resolved |
| `E-4` | `runs/run-93b302cbdb28/state.json` | resolved |
| `E-5` | `runs/run-93b302cbdb28/completion-package.md` | resolved |
| `E-6` | `runs/run-93b302cbdb28/states/scope-and-acceptance/artifacts/scope-definition.md` | resolved |
| `E-7` | `runs/run-93b302cbdb28/states/scope-and-acceptance/validation-report.json` | resolved |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed by the registered agent; `scope-definition.md` validated 33/33 | omn-product-owner | `runs/run-93b302cbdb28/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed by the registered agent; 15 tasks across 9 waves, plan status `partial` with increments 2 to 4 deferred under the one-increment constraint, validated 45/45 | planner | `runs/run-93b302cbdb28/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed by the registered agent. Attempt 1 was rejected by the Validation Engine on five checks, classified `output-schema-failure`, retried under the bounded policy; attempt 2 validated 78/78 and emitted decision records `D-001` and `D-002` | architect | `runs/run-93b302cbdb28/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed by the registered agent; `implementation-report.md` validated 32/32 | omn-dev-1-implement | `runs/run-93b302cbdb28/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed by the registered agent; `review-package.md` validated 31/31 | omn-dev-2-reviewer | `runs/run-93b302cbdb28/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | blocked | Blocked `awaiting_contract_reconciliation`; the phase declares a prose Output Artifact that `omn-documentation` does not declare among its outputs. The phase lies outside the twelve rows `D-001` dispositions, so it is reported rather than re-dispositioned here. Documentation impact for this change is discharged by this proposal and by `reports/wave-1-reconciliation-report-2026-08-19.md` | operator | `runs/run-93b302cbdb28/state.json` |

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | operator on behalf of omn-business-analyst | `scope-definition.md` validated 33/33; scope, acceptance criteria and non-goals bounded to the Wave 1 delivery core. `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Plan validated 45/45; `partial` status correctly declared rather than scope silently narrowed |
| Design Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Design validated 78/78 after one classified repair pass; `D-001` and `D-002` accepted. `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | operator on behalf of omn-qa | `review-package.md` validated 31/31, severity counts recomputed from the findings table, every open critical or high finding addressed. `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-qa | operator on behalf of omn-qa | Framework verification re-run after reconciliation: registry coverage 6/6, validator coverage 4/4 over 13 types, recovery 41/41, multi-phase replay 15/15 |

The Closure Gate is recorded undecided, because it assesses evidence the blocked
`documentation-and-release-handoff` phase never produced. No gate was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | 6/6 COVERED; 30 of 36 phases dispatchable, up from 3 |
| Validator coverage | `python .claude/runtime/verify_validators.py` | 4/4 COVERED; 13 artifact types, each accepting a conforming artifact and rejecting a mutated one by a named check |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | 41/41 RECOVERY PROVEN |
| Multi-phase replay | `python .claude/runtime/verify_multi_phase.py --run-id run-93b302cbdb28` | 15/15 PROVEN; artifact digests unchanged on re-execution |
| Prior committed evidence | `python .claude/runtime/verify_vertical_slice.py --run-id run-b6780677468b --slice planner` | 10/10 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py --mode-evidence` | 9/9 SELF-HOSTING |
| Manifest reference resolution | inspection | 12 of 12 manifests resolve `specificationRef`, `contractRef`, and `lifecycleRef` to files their own `loadOrder` declares |

## Risk and Rollback

- Blast radius: every agent contract surface, the validator map, five workflow Phase Models, three registries, and three verification scripts. This is the largest single framework change to date, and it is larger than the one-increment-at-a-time constraint the accepted plan set. That divergence is recorded as `O-002` rather than presented as compliant.
- Risk assessment: two risks materialised. The design predicted that editing a Phase Model would touch documents inside the frozen context slice of completed runs (`A-006`, `R-001`); it did, and the affected runs re-verify. The design did not predict that capability growth would falsify governance records that were accurate when written; it did, which is `GD-001` and the reason three verification scripts changed.
- Rollback procedure: reverting requires restoring the two superseded shared contract modules from an external copy, since this change did not delete them and cannot restore them; reverting `registry/agents.yaml` to two active records; removing the six added validators and their `VALIDATORS` entries; and restoring the prose Output Artifact cells in five workflow specifications. Reverting invalidates the executed-phase evidence in `run-93b302cbdb28` for four phases, because their owners would no longer resolve. A partial revert of the point-in-time corrections alone is available and independent: reverting `GD-001` returns `F6`, `F12`, and the Completion Rule to current-state evaluation, and immediately re-fails `FC-001` and `FC-002`.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6 checks, unresolved=0, 30/36 dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 4/4 checks, 13 artifact types, each rejecting its mutation by a named check |
| `FR-03` | Recovery behaviour | pass | 41/41 checks across the injected runs |
| `FR-04` | Committed evidence still verifies | pass | `run-b6780677468b` and `run-308f4d0ee447` both 10/10 PROVEN after the change |
| `FR-05` | Self-hosting governance resolves | pass | `verify_self_hosting.py` 9/9 |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-93b302cbdb28` is an `/implement` run; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Raised 0.4.1 to 0.5.0: the context slice now carries per-member attribution and an unnarrowed set, and three verification scripts changed their evaluation basis |
| `FR-08` | Documentation matches delivered behaviour | pass | `agents/superseded-contracts.md`, `agents/retired-roles.md`, `agents/README.md`, and `reports/wave-1-reconciliation-report-2026-08-19.md` |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Six phases remain blocked and each carries a recorded reason; the unnarrowed context-slice members of 28 phases are now reported per slice rather than left implicit |
| `FR-10` | Rollback stated | pass | Risk and Rollback above, including the restore dependency the supersession creates |
| `FR-11` | Multi-phase state machine still proves out | pass | `verify_multi_phase.py --run-id run-93b302cbdb28` 15/15 PROVEN |
| `FR-12` | Release note where consumer-visible behaviour changed | not-applicable | The `documentation-and-release-handoff` phase that would produce one is blocked at contract reconciliation and recorded as such |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Six phases remain blocked at `awaiting_contract_reconciliation`: four `omn-documentation` phases, `fix-bug/triage-and-impact`, and `review-pull-request/structural-compliance`. Each declares a prose Output Artifact its owner does not declare among its outputs | omn-tech-lead | Open; outside the twelve rows `D-001` dispositions. Routes as `capability-addition` and is the next increment's work |
| `O-002` | The rollout delivered ten agents in one pass, against the one-primary-capability-per-increment constraint in the accepted plan (`S-015`) and the change request. No design conflict resulted, but the self-hosting regression surfaced only at reconciliation rather than at the first increment boundary | omn-orchestrator | Recorded; the constraint stands for subsequent waves |
| `O-003` | 28 phases carry context-slice members with no declared consuming input. `D-002` requires the attribution; the mechanism now exists and reports them as unnarrowed, but only `scope-and-acceptance` and `artifact-packaging` are attributed | architect | Open; visible per slice under `unnarrowed`, so it is reported rather than hidden |
| `O-004` | No verifier resolves a manifest's `contractRef` or `lifecycleRef`, which is why 45 dangling references survived every check. `SC-001` fixed the references; the verification gap remains | omn-qa | Open; routes as `capability-addition` |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Design Gate, omn-qa at the Review and Verification Gates, omn-business-analyst at the Scope Gate, each recorded by the operator
- Acceptance basis: five of six phases executed by their registered agents and validated by their registered validators, every invariant re-verified after the change, the two blocking reconciliation findings closed by recorded decisions `SC-001` and `GD-001`, and four open items recorded with an owner and a route
