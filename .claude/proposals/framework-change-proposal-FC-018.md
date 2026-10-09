# Framework Change Proposal: Repair verify_validators V4 so it does not depend on which investigation report a run committed

```yaml
frameworkChangeProposal:
  proposalId: FC-018
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-d8937789961e
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-018
- Change title: Repair verify_validators V4 so it does not depend on which investigation report a run committed
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-d8937789961e
- Authored on: 2026-10-09

## Authoring Baseline

- Authored at: 2026-10-09T09:11:07Z
- Runtime version: 0.9.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: repair the defect in `verify_validators.py` check `V4` that FC-017 recorded as its open item `O-007`. `V4` went from 6/6 to 5/6 NOT COVERED once `run-437e2f765e4b`, the investigate run carried by FC-017, committed the first real investigation report. The selector `conforming_instance` prefers committed run artifacts over the fixture, and the investigation-report mutation row pinned two literals that only the fixture carried: the anchor, recommended option `O-002`, and the substitute, the ninth option id. The real report recommends `O-003`, so no anchor was found. The same root cause hid a second, latent failure that the root cause analysis found: a nine-option report recommending `O-002` would have carried the anchor, and the mutation would then have been silently ACCEPTED, because the substituted id would have been an evaluated option and so not a mutation at all. A loud failure and a silent pass share one cause, which is a mutation derived from a literal instead of from the instance under test. The fix adds `recommend_an_unevaluated_option`, which derives the mutation: it replaces the option id on the `- Recommended option:` line with the lowest `O-nnn` absent from the whole text, and returns `None` when the field is missing. `resolve_mutation` and `mutation_verdict` were extracted from `main()` with byte-identical behaviour. `committed_instances` and `conforming_instance` are untouched. Fifteen new tests in `tests/test_verify_validators_mutations.py` pin the behaviour; against the pre-fix file two fail on the two bug witnesses and the rest error, and against the fixed file all pass. The bundled mirror was refreshed. A post-review correction pass closed finding `F-003` (the replacement now lands on the field line) and added the `F-001` known-limit comment. The reviewer's finding `F-002` claimed that `skipTest` inside `subTest` skips the whole test. That premise was incorrect: it was verified, and it skips only that iteration. The change the finding asked for was kept anyway, as the stricter form. The root cause analysis is at `runs/run-d8937789961e/states/root-cause-analysis/artifacts/bug-analysis.md`.
- In scope: `.claude/runtime/verify_validators.py` and the run `run-d8937789961e` over the `fix-bug` workflow with this governance record.
- Out of scope: any validator under test; the runtime behaviour, which is unchanged; the two count mutation rows that substitute 99 (`O-002`); the label spelling limit (`O-003`); the four artifact types without a fixture (`O-006`); and a further instance of the same defect class in the `orchestration-result.md` row, found while authoring this proposal (`O-007`). The new test file and the bundled mirror are outside the framework surface.
- Acceptance basis: the routed run planned through the framework, with every phase executed by a host-dispatched subagent and validated on the first attempt; every gate decided by a non-producing owner; the fix tested before and after; the standalone verifiers re-run and reported as they came out; the unit suite executed twice on this exact tree, by the operator and by QA.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/verify_validators.py` | `SR-1` | in-scope | The verifier repaired: a framework surface the runtime resolves |
| `tests/test_verify_validators_mutations.py` | no rule | out-of-scope | Outside the framework surface; the 15 new tests that pin the repair |
| `omn_agent/_bundled_payload/runtime/verify_validators.py` | no rule | out-of-scope | Outside the framework surface; the bundled mirror, refreshed through `python tests/test_bundled_payload.py --sync` and never hand-edited |
| `.claude/runs/run-d8937789961e/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this repair |
| `.claude/runs/inputs/verify-validators-v4-anchor-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-018.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The verifier `V4` is declared to prove that every registered validator rejects a mutated artifact, and it reports the validators uncovered because of which report a run happened to commit, not because of any validator.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify` over the six paths of the table above returns `SR-1` in scope for `.claude/runtime/verify_validators.py` with the verdict "framework-internal change", no rule and out of scope for the test file and the bundled mirror, `SR-3` out of scope for the run evidence and the defect report, and `SR-5` out of scope for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug` at `triage-and-impact` of 5, with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-d8937789961e/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug`, input recorded with its digest |
| `E-2` | `runs/run-d8937789961e/run-ledger.json` | resolved; runtime 0.9.0, 5 phases, run status Completed |
| `E-3` | `runs/run-d8937789961e/events.jsonl` | resolved; 56 events from `run_initialized` to the final `run_completed`, E-0001 to E-0056 |
| `E-4` | `runs/run-d8937789961e/state.json` | resolved; 5 phases completed, 0 blocked, 0 failed, 29 transitions |
| `E-5` | `runs/run-d8937789961e/completion-package.md` | resolved; aggregated for 5 of 5 completed phases |
| `E-6` | `runs/run-d8937789961e/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; the root cause analysis, with the two failure modes of one cause |
| `E-6` | `runs/run-d8937789961e/states/fix-implementation/artifacts/implementation-report.md` | resolved; the fix, its tests and its post-review correction pass |
| `E-6` | `runs/run-d8937789961e/states/regression-validation/artifacts/validation-report.md` | resolved; 8 of 8 criteria met |
| `E-7` | `runs/run-d8937789961e/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-d8937789961e/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-d8937789961e/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-d8937789961e/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-d8937789961e/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |
| `E-8` | `runs/run-d8937789961e/execution-metrics.json` | resolved; the metrics cited under Verification |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed first attempt; validated 30 of 30; tier standard, host hint `inherit`; no charged retry | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-d8937789961e/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed first attempt; validated 30 of 30; tier deep, host hint `opus`. The analysis needed one offline correction before completion, finding `C6.1` (a profile label), found by the offline validator run and so not a charged attempt | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-d8937789961e/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed first attempt; validated 32 of 32; tier deep, host hint `opus`. One offline correctable finding, `C4.3`, was fixed before completion; no charged retry | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-d8937789961e/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed first attempt; validated 31 of 31; tier standard, host hint `inherit`; 8 of 8 criteria met | `omn-qa` subagent, dispatched by the host | `runs/run-d8937789961e/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed first attempt; validated 34 of 34; tier light, host hint `haiku`; no escalation | `omn-orchestrator` subagent, dispatched by the host | `runs/run-d8937789961e/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-d8937789961e`: 5 completed, 0 blocked, 0 failed, 0 pending, 0 retrying, run status Completed, 29 transitions, 0 replays suppressed. The recovery ledger holds seven classified failures, all of class `gate-approval-required`, all resolved, at 0 of 3 attempts charged. Every phase was validated on the first attempt, with no charged retry.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Triage validated 30 of 30 and the defect traces to the supplied report; `omn-dev-1-bug-analyst` produced the evidence and is excluded from deciding |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, dispatched independently of the implementer, recorded by the session operator | Verdict approve-with-corrections, no blocking findings. The rationale was recorded verbatim in the gate decision at E-0034. The corrections were then closed in a post-review pass: `F-003` closed, the `F-001` known limit commented, and `F-002` verified and kept as stricter because its premise was incorrect |
| Verification Gate | approve | omn-dev-2-reviewer | operator on behalf of omn-dev-2-reviewer | Regression validation validated 31 of 31 with 8 of 8 criteria met; `omn-qa` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-documentation | operator on behalf of omn-documentation | Closure validated 34 of 34; `omn-orchestrator` produced the evidence and is excluded from deciding |

Producer exclusion held at every gate: no gate was decided by the agent that produced its evidence.

## Verification

All commands were run from the repository root of this worktree.

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8, 37 of 37 phases dispatchable |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | fail; 5/6, `V4` only. `V4` now reports "orchestration-result.md: no mutation anchor for 'deciding the gate its own coordination record is the evidence for' in this instance". The investigation-report row, the subject of this repair, is caught by `I1` and no longer fails. The new failure is the same defect class on a different row, exposed by the closure record of this very run becoming the committed `orchestration-result.md`. A closure record cannot carry its own gate decision, so its only owned row reads gate `none`, and the derivation finds no row to mutate. Recorded as `O-007`. It was not visible to the regression-validation phase, which ran before that record existed |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 6/8, run before this proposal was on disk. `S7` fails on `run-437e2f765e4b`, whose `publication` phase is pending, so FC-017 is provisional (carried from FC-017, not changed by this change). `S8` names `run-5df08e171670`, pre-existing, and `run-d8937789961e`, which this proposal accounts for. `S1` to `S6` pass, S6 accepting FC-001 to FC-017 |
| Vertical slice | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN. The run appends replay records to that committed run; they were restored with `git checkout -- .claude/runs/run-c5a8d50d3238/state.json .claude/runs/run-c5a8d50d3238/task-context.yaml`, and `git status` then showed no change under that run |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | 14/15 NOT PROVEN, advisory item. The one failing check is `M14`, the re-run of the same request: `plan` and `dispatch` exited non-zero. Run by hand, `plan --run-id run-c5a8d50d3238` ends in `PermissionError: [WinError 5] Access is denied` on `os.replace` of `state.json.tmp`, a file-system permission refusal in this worktree. This is not evidenced as caused by the change, which touches only `verify_validators.py`, but it was not reproduced on a clean tree either. The run was restored as above and a stray `state.json.tmp` removed; `git status` shows no change under that run |
| Recovery | inspection | `verify_recovery.py` was not run, because it mutates committed run evidence and no throwaway copy was made. The FC-016 result, 73/74 with `X1` pre-existing, is cited as unchanged: the change touches only `verify_validators.py`, which `verify_recovery.py` does not import |
| Unit suite | `python tools/run_tests_parallel.py` | pass; 657 of 657 across 26 modules, executed twice on this exact tree, once by the operator and once by `omn-qa`. The FC-016 baseline was 642; the 15 new tests make 657. Not re-run while authoring this proposal, because it takes about eight minutes |
| Defect witnessed and fixed | `python tests/test_verify_validators_mutations.py`, against the pre-fix and post-fix verifier | before the fix, 2 assertion failures on the two bug witnesses (the fixture-bound anchor and the silently accepted nine-option report) and the rest errors; after the fix, 15 of 15 pass. Evidence in the implementation report and the validation report |
| Run metrics | inspection of `runs/run-d8937789961e/execution-metrics.json` | wall clock 1h04m52s, agent-active 45m17s. Invocations by tier: 1 light, 2 standard, 2 deep, 0 untiered; the non-deep share is 60 percent. Context about 408,910 legacy against about 186,612 progressive estimated tokens, 54.4 percent less. This is the first run tiered end to end under runtime 0.9.0. It is one run of one bug and is not a controlled comparison, so it proves that tiers were applied, not that they saved cost |

## Risk and Rollback

- Blast radius: one verifier (`.claude/runtime/verify_validators.py`), one new test file (`tests/test_verify_validators_mutations.py`) and one bundled mirror (`omn_agent/_bundled_payload/runtime/verify_validators.py`). No validator, runtime behaviour, config, agent, workflow, registry or template file changed, and `RUNTIME_VERSION` is unchanged at 0.9.0.
- Risk assessment: the repair removes a literal, so the residual risks are the limits of the derivation that stay. First, the two count rows that substitute 99 would make `V4` fail loudly on a real count of 99 (`O-002`). Second, the derivation matches only the template's `- Recommended option:` spelling; any other spelling fails loudly as a missing anchor and never silently (`O-003`). Third, four artifact types (`scope-definition.md`, `execution-plan.md`, `technical-design.md`, `framework-change-proposal.md`) have no fixture, so their mutation rows depend on committed run evidence and carry the same exposure this change removed for one row (`O-006`). Fourth, `V4` is still 5/6 on this tree, through the `orchestration-result.md` row (`O-007`), so the verifier does not yet report full coverage and a real validator regression would still be reported by the same line.
- Rollback procedure: revert the three files, `.claude/runtime/verify_validators.py`, `tests/test_verify_validators_mutations.py` and the bundled mirror, then run `python tests/test_bundled_payload.py --sync` and confirm `python tests/test_bundled_payload.py` passes. Reverting restores the brittle verifier and reopens the loud failure FC-017 recorded as its `O-007`, and removes 15 tests, so the suite returns to 642. No committed run evidence is invalidated.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | fail | 5/6; the investigation-report row of `V4` is repaired and caught by `I1`, but `V4` still fails on the `orchestration-result.md` row, recorded as `O-007`. Reported as returned, not as the 6/6 the repair was expected to reach |
| `FR-03` | Recovery behaviour | pass | Not re-run, because it mutates committed run evidence. The FC-016 result, 73/74 with `X1` pre-existing, is carried unchanged because `verify_recovery.py` does not import `verify_validators.py`, the only file changed |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN; the committed run restored afterwards |
| `FR-05` | Self-hosting governance resolves | fail | 6/8; `S7` on `run-437e2f765e4b` (FC-017 provisional, pre-existing) and `S8` on `run-5df08e171670` (pre-existing, `O-004`); `S8` for this run is accounted for by this proposal |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-d8937789961e` is a `/bugfix` run over `fix-bug`, all five phases completed and all four gates decided; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | `RUNTIME_VERSION` stays 0.9.0: a verifier changed, not runtime behaviour |
| `FR-08` | Documentation matches delivered behaviour | pass | No documented behaviour changed; no documentation touched |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row is a command output or a cited artifact. Gaps are recorded rather than omitted: `O-001` to `O-007`, including the `V4` residual failure |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | fail | 14/15; `M14` failed on a `PermissionError` writing `state.json.tmp` in this worktree. Advisory item. Characterised afterwards, on 2026-10-09: it is intermittent in this worktree path (14/15 in 3 of 4 clean-state runs, 15/15 in 1), and absent when the identical uncommitted tree is copied to a temporary directory (15/15 in 4 of 4) and on a clean export of the base commit (15/15 in 4 of 4), so it is an environment effect of the worktree location and not a content effect of this change |
| `FR-12` | Release note where consumer-visible behaviour changed | not applicable | No consumer-visible behaviour changed; a verifier changed |

`FR-02`, `FR-05` and `FR-11` are reported as failures as the commands returned them. The recovery result is carried from FC-016, not re-run.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The implementation report prose says 14 new tests and 656 total, while the actual figures are 15 and 657 | omn-dev-1-implement | Open. Committed run evidence is not edited; the correct figures are recorded here and in the validation report |
| `O-002` | The two count rows that substitute 99 would make `V4` fail loudly on a real count of 99 | omn-tech-lead | Open. Decide whether to derive the substitute as the other rows now do |
| `O-003` | The derivation matches only the template's `- Recommended option:` spelling, so another spelling fails loudly as a missing anchor, never silently; the `F-001` known-limit comment records it | omn-dev-1-implement | Open. Widen the match if the template ever changes the label |
| `O-004` | `S8` fails on `run-5df08e171670`, a run without a proposal, pre-existing | omn-orchestrator | Open, pre-existing. Closes only by a proposal authored by whoever carried that change; fabricating one would falsify the record |
| `O-005` | Process note: a reviewer's factual claim about test framework semantics (`F-002`, that `skipTest` inside `subTest` skips the whole test) was wrong, and was caught only because the implementer questioned it | omn-dev-2-reviewer | Open. Consider requiring a reproduction for review findings that assert tool behaviour |
| `O-006` | Four artifact types have no fixture (`scope-definition.md`, `execution-plan.md`, `technical-design.md`, `framework-change-proposal.md`), so their mutation rows depend on committed run evidence | omn-qa | Open. Add a fixture for each, or record that a committed instance must exist |
| `O-007` | `V4` still fails on the `orchestration-result.md` row, 5/6: a closure record carries no decision for its own Closure Gate, so the only row its owner holds reads gate `none` and `award_itself_its_own_gate` finds no row to mutate once a real closure record replaces the fixture. FC-017 `O-007` is closed for the investigation-report row only, and FC-017 is unedited and records it as open at its authoring baseline | omn-qa | Open. Needs its own defect-repair change: derive the mutation from a row the real record carries |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates and omn-documentation at the Closure Gate, each recorded by the operator or the independently dispatched reviewer, none of them the producer of the evidence it decided
- Acceptance basis: all five phases of the routed workflow executed by host-dispatched subagents and accepted by their registered validators on the first attempt with no charged retry; all four gates approved with producer exclusion held; the defect witnessed before the fix and closed after it; the unit suite passing 657 of 657 twice on this tree; the verifier failures (`V4`, `S7`, `S8`, `M14`) reported as returned; and seven open items recorded with an owner
