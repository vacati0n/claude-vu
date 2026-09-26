# Framework Change Proposal: Content-Contract Tests over Governance Prose and Root-Document Status Banners

```yaml
frameworkChangeProposal:
  proposalId: FC-007
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-919c5d5cf156
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-007
- Change title: Add the content-contract test suite that pins four structural properties of governance prose, and the pinned `Status:` banner on the four repository-root governance documents
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-919c5d5cf156
- Authored on: 2026-09-04

## Authoring Baseline

- Authored at: 2026-09-04T15:17:20Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

## Change Statement

- Objective: give the framework an automatic, pre-landing failure when an edit to governance prose breaks a structural property the runtime reads. Before this change, a maintainer could silently break gate decidability, remove a supersession marker, delete a status banner, or introduce coercive auto-chain instruction into an agent contract, and nothing failed until a run misbehaved. Ticket CKA-04, traced to recommendation R5 of the adoption review dated 2026-08-27, plus the banner portion of CKA-05 scoped in by scope decision D-001 (SCOPE-2026-0004).
- In scope: the new content-contract suite `tests/test_content_contracts.py` (13 tests) pinning four properties — gate-matrix rows stay decidable outside the producing role's alias set, read through the runtime's own alias readers by import; superseded agent specifications keep their line-1 supersession marker; the four root governance documents keep their pinned `Status:` banner; and no agent contract module carries coercive auto-chain instruction, scanned across seven pattern families behind a two-part structural discriminator — and the one-line pinned banner `Status: specification — not implemented` inserted, with a blank separator line, at the top of `decision-matrix.md`, `quality-gates.md`, `rule-engine.md`, and `working-memory.md`.
- Out of scope: any runtime module, workflow specification, registry record, gate-decision surface, or CI configuration change (scope exclusions X-001 additive-only and X-002 zero-CI-change, both held on the inspected diff); the remainder of CKA-05 beyond banner presence (scope decision D-002/X-004); and widening the coercive-scan discriminator beyond its accepted precision-over-recall inventory, designated to CKA-16 by decision record D-002.
- Acceptance basis: nine measurable acceptance criteria in SCOPE-2026-0004. A-001 through A-008 met on executed or directly inspected evidence at the Verification Gate (CI discovery confirmed, full suite 342 tests OK, producer-only fixture failing in both alias directions, marker, banner, and coercive fixtures demonstrated, four banners exact, structure-preserving rewording free); A-009 settled at the documentation phase with an explicit no-impact finding for the user guide, recorded in release note RN-2026-0006.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `decision-matrix.md` | `SR-2` | in-scope | Root governance document; two lines inserted — the pinned banner and a blank separator |
| `quality-gates.md` | `SR-2` | in-scope | Root governance document; two lines inserted — the pinned banner and a blank separator |
| `rule-engine.md` | `SR-2` | in-scope | Root governance document; two lines inserted — the pinned banner and a blank separator |
| `working-memory.md` | `SR-2` | in-scope | Root governance document; two lines inserted — the pinned banner and a blank separator |
| `tests/test_content_contracts.py` | none | out-of-scope | The new suite itself; no scope rule matches, the path is outside the framework surface, yet the change as a whole is framework-internal because the four in-scope paths above make it so |
| `.claude/runs/run-919c5d5cf156/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/proposals/framework-change-proposal-FC-007.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains an enforcement capability it did not have — a CI-discovered content-contract suite that fails a landing when governance prose breaks a runtime-read structural property. The narrower `structure-preserving-change` claim is not defensible: the verification run's observable behaviour changes, since thirteen new tests join it and can fail it
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path quality-gates.md` (and each of the other three root documents) returns framework-internal under `SR-2`; `--path tests/test_content_contracts.py` returns out-of-scope with no matching rule, and the profile's Scope Rule states that a change touching both in-scope and out-of-scope paths is framework-internal; `python .claude/runtime/self_hosting.py route --intent capability-addition` resolves to `/implement` over `implement-feature` at `scope-and-acceptance`, which is the command and workflow the run's execution request records

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-919c5d5cf156/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature`, one input recorded with digest: `feature-request` at `runs/inputs/cka-04-feature-request.md` |
| `E-2` | `runs/run-919c5d5cf156/run-ledger.json` | resolved |
| `E-3` | `runs/run-919c5d5cf156/events.jsonl` | resolved |
| `E-4` | `runs/run-919c5d5cf156/state.json` | resolved; six phases, all completed, none blocked; five upstream gates decided, Closure Gate decided in this closure session |
| `E-5` | `runs/run-919c5d5cf156/completion-package.md` | resolved |
| `E-6` | `runs/run-919c5d5cf156/states/implementation/artifacts/implementation-report.md` | resolved; each of the six phases committed its contracted artifact, including the release note at `states/documentation-and-release-handoff/artifacts/release-note.md` |
| `E-7` | `runs/run-919c5d5cf156/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases, every one recording `pass` |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed against the run over two attempts; 7 in-scope items, 5 exclusions, 9 acceptance criteria, 3 scope decisions, 0 blocking open questions, verdict `bounded`, Validation Engine 33/33. Attempt 1 rejected at `C3.2`; corrected and re-completed | host-dispatched `omn-product-owner` subagent | `runs/run-919c5d5cf156/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed against the run in one attempt; 8 tasks over 3 waves, acyclic dependency graph, 4 assumptions, 7 risks, 2 non-blocking open questions, Validation Engine 45/45 | host-dispatched `planner` subagent | `runs/run-919c5d5cf156/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed against the run over two attempts; 3 options against 8 constraints, 6 decisions including accepted decision records D-001 (alias logic bound by import to the runtime's own readers) and D-002 (the two-part coercive-scan discriminator), Validation Engine 78/78. Attempt 1 rejected at `D8.5`, `D16.1`, `D16.4`; corrected and re-completed | host-dispatched `architect` subagent | `runs/run-919c5d5cf156/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed against the run over two attempts; 5 change-set entries each carrying test evidence, 1 recorded deviation, 4 residual risks (R-001 to R-004), Validation Engine 32/32. Attempt 1 rejected at `C4.3`; corrected and re-completed | host-dispatched `omn-dev-1-implement` subagent | `runs/run-919c5d5cf156/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed against the run over two attempts; 2 findings (1 medium, 1 low), 2 correction requests, verdict `approve-with-corrections`, review re-executed the module (13/13) and the full suite (342, exit clean, tracked tree unchanged), Validation Engine 31/31. Attempt 1 rejected for an undeclared transient side effect — the pre-existing untracked interpreter bytecode cache under `tests/` — declared and re-completed | host-dispatched `omn-dev-2-reviewer` subagent | `runs/run-919c5d5cf156/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed against the run over two attempts; release note RN-2026-0006 at verdict `released` with 5 known issues, carrying the A-009 no-impact finding for the user guide and the CR-001/CR-002 dispositions, Validation Engine 32/32. Attempt 1 rejected at `R2`, `R7`; corrected and re-completed | host-dispatched `omn-documentation` subagent | `runs/run-919c5d5cf156/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact. None blocked. All six were performed by host-dispatched subagents under their contracted validators; the framework selected the route, held every gate, and validated every artifact.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | omn-business-analyst subagent, recorded by session operator | Scope bounded: 7 traceable items, 5 bounding exclusions, 9 measurable criteria preserving both verbatim ticket criteria; both open questions non-blocking with owners; `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | omn-tech-lead subagent, recorded by session operator | All 7 scope items and 9 criteria decomposed into 8 tasks over an acyclic 3-wave graph; both real risks owned and mitigated at design; three binding conditions set for design; `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | omn-tech-lead subagent, recorded by session operator | All three Planning Gate conditions honoured and independently verified; ADRs D-001 and D-002 accepted; change strictly additive; checks cover A-001 to A-009; `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | omn-qa subagent, recorded by session operator | Zero blocking findings; F-001's substance already resolved on the tree and verified by read and post-fix execution; F-002 account-precision only, correctly repaired at closure rather than in the digest-pinned report; decided as non-producer second owner under the Producer Exclusion Rule |
| Verification Gate | approve | omn-qa | omn-qa subagent, recorded by session operator | A-001 to A-008 met on executed or directly inspected evidence; A-009 deferred to documentation by the plan's own sequencing and carried as a closure condition; both attributed negative proof verdicts accepted (multi-phase 14/15 in flight, self-hosting 7/8), answering Q-001 with no repair required |
| Closure Gate | approve | omn-orchestrator | omn-orchestrator, in the closure session this proposal is part of | All four Verification Gate closure conditions verified: A-009 settled with an explicit no-impact finding in RN-2026-0006; CR-001 and CR-002 dispositions persisted in RN-2026-0006's Known Issues and Support handoff notes; this run's S8 accounting resolved by this proposal; handoff hygiene (bytecode cache, R-004 replay hazard) carried in RN-2026-0006. `omn-documentation` produced the evidence and is excluded from deciding |

Every gate this workflow declares was decided. None was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6, 37 of 37 phases dispatchable, 29/29 gate references decidable under the Producer Exclusion Rule |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8 at authoring: S1 to S7 pass; S8 fails on the four pre-existing unaccounted runs plus this run, whose row this proposal removes on its next execution; the four pre-existing rows remain and are open item `O-001` |
| Scope classification recomputes | `python .claude/runtime/self_hosting.py classify --path quality-gates.md` (each of the four root documents, and the test module) | pass; four paths in-scope under `SR-2`, the test module out-of-scope with no matching rule |
| Routing resolves | `python .claude/runtime/self_hosting.py route --intent capability-addition` | pass; resolves to `/implement` over `implement-feature` at `scope-and-acceptance`, agreeing with the run's execution request |
| Content-contract suite and full verification run | inspection | recorded at the Review and Verification Gates rather than re-executed at closure: the reviewer re-executed the module (13/13, same six itemized exclusions) and the full suite (342 OK, exit clean, tracked tree unchanged), and omn-qa verified A-001 to A-008 on executed evidence; this gate takes those verdicts as the recorded facts they are |
| Multi-phase state machine | inspection | deliberately not re-executed at closure: `verify_multi_phase.py` appends replay bookkeeping to the newest committed run's tracked state file (release note `K-004`), and modifying committed run evidence is prohibited to this role; the Verification Gate accepted the attributed in-flight 14/15 reading, self-resolving at commit (`K-001`) |

## Risk and Rollback

- Blast radius: one new test module under `tests/` and two inserted lines (banner plus blank separator) at the top of each of the four repository-root governance documents. No runtime module, workflow specification, registry record, gate-decision surface, agent manifest, artifact template, validator, or CI configuration file changed; the additive-only boundary (X-001) and the zero-CI-change boundary (X-002) both held on the inspected diff.
- Risk assessment: four residual risks recorded and owned. The suite couples by import to four runtime reader names (`producer_aliases`, `parse_gate_matrix`, `parse_phase_model`, `phase_gates`), a deliberately loud failure mode accepted in decision record D-001. The check-4 discriminator trades recall for precision — a coercive instruction phrased declaratively, in the third person, or in a table cell evades it — accepted by the design owner in decision record D-002 with CKA-16 as the widening vehicle (release note `K-003`). The multi-phase proof mutates tracked run-evidence state when executed (`K-004`), an unmitigated tooling hazard predating this change. The committed implementation report predates the review's corrections; the durable correction record is RN-2026-0006's Support handoff notes (`K-005`).
- Rollback procedure: remove `tests/test_content_contracts.py` and the four banner lines with their separators — a five-file, additive-only revert with no runtime, gate-decision, or CI behaviour attached. The condition that would justify it is the suite failing wording-only edits that preserve pinned structure, which scope exclusion X-003 binds it not to do and which the Verification Gate demonstrated free (criterion A-003). Reverting invalidates no other run's evidence; this run's evidence remains a valid record of a delivered-then-reverted change, and this proposal remains its governance record.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6; 37 of 37 phases dispatchable, 29/29 gate references decidable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 |
| `FR-03` | Recovery behaviour | pass | 41/41 |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | pass | Profile parses, all 7 routing rows resolve, the change-proposal contract is registered, and every recorded proposal validates (S1 to S7). S8's four pre-existing unaccounted runs are a residual this change did not cause, recorded as open item `O-001` and release note `K-002` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-919c5d5cf156` is an `/implement` run over `implement-feature`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0. No runtime module changed; the suite consumes four runtime readers read-only by import |
| `FR-08` | Documentation matches delivered behaviour | pass | RN-2026-0006 (Validation Engine 32/32) records the delivered behaviour; A-009 settled with an explicit no-impact finding for `docs/USER-GUIDE.md` and `docs/user-guide.html`; no catalog or README is touched by the change |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every executed claim re-verified by the independent review and at the Verification Gate; the recall gap of check 4 and the report-precision gap are recorded as `K-003` and `K-005` rather than omitted |
| `FR-10` | Rollback stated | pass | Risk and Rollback above; five-file additive revert, trigger condition named |
| `FR-11` | Multi-phase state machine still proves out | accepted | omn-qa accepted the attributed in-flight 14/15 reading at the Verification Gate (`K-001`, self-resolving at commit); not re-executed at closure because the probe mutates committed run evidence (`K-004`), which this role may not do; post-commit re-execution is open item `O-004` |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-919c5d5cf156/states/documentation-and-release-handoff/artifacts/release-note.md`, verdict `released`, 5 known issues |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Four framework runs predating this change — `run-34ca35504b72`, `run-efe092286625`, `run-e0dba6763475`, `run-8f8a1ab0d16e` — carry no change proposal and fail `S8` of the self-hosting verifier. This proposal accounts for `run-919c5d5cf156` only; fabricating proposals for runs this change did not carry would falsify the record | omn-orchestrator | Open, pre-existing. Grown from `O-005` of `FC-006` (two runs) to four; closing it requires a proposal per run, authored by whoever carried each change |
| `O-002` | Check 4's discriminator evades a coercive instruction phrased declaratively, in the third person, or in a table cell — the accepted precision-over-recall tradeoff | architect | Open, accepted in decision record D-002; CKA-16 is the designated widening vehicle; monitor the per-run exclusion itemization for drift |
| `O-003` | `runtime/verify_multi_phase.py` appends replay bookkeeping to the newest committed run's tracked state file, so executing the definition-of-done proofs drifts tracked run evidence without any agent editing it | omn-tech-lead | Open, unmitigated (`K-004`, implementation risk R-004). Executors must check version-control state of run evidence after the proof and restore committed content |
| `O-004` | The multi-phase proof reads 14/15 while this run's delivery phase is uncommitted (`K-001`); re-execution after this change commits is owed to confirm the reading clears | omn-qa | Scheduled, self-resolving at commit per the Verification Gate's accepted verdict |
| `O-005` | The `Recorded Framework Changes` index in `config/self-hosting-profile.md` does not yet carry the `FC-007` row. Adding it is a framework-internal edit (`SR-1`) outside the single-file write this closure session was authorized to make; the index is a directory, not an authority — `verify_self_hosting.py` discovers proposals by glob, so its absence blocks nothing | operator | Open; append the row with the next routed framework change or as operator housekeeping |
| `O-006` | `omn-orchestrator` is the contracted producer of this artifact, yet its manifest permits no repository write in any phase. This instance was authored by `omn-orchestrator` under an explicit operator authorization scoped to exactly this one file; the standing contradiction is tracked since `O-003` of `FC-005` and `O-006` of `FC-006` | omn-tech-lead | Open, unchanged; resolve by either narrowing the producer list or widening the manifest's write scope for this artifact alone |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorized by the session operator for this closure
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, and omn-orchestrator at the Closure Gate as non-producing owner
- Acceptance basis: all six phases of the routed workflow executed with artifacts accepted by their registered validators, every gate decided by an owner who did not produce the evidence it assesses, five charged retries recorded with what each repaired, all four Verification Gate closure conditions verified against the release note and the run record, and six open items recorded with owners — including the four-run accounting residual this change did not cause and does not close
