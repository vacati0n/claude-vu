# Framework Change Proposal: Complete the repair of verify_validators V4: instance applicability and locator parity

```yaml
frameworkChangeProposal:
  proposalId: FC-019
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-5f4422f26c3e
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-019
- Change title: Complete the repair of verify_validators V4: instance applicability and locator parity
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-5f4422f26c3e
- Authored on: 2026-10-09

## Authoring Baseline

- Authored at: 2026-10-09T10:15:00Z
- Runtime version: 0.9.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: complete the repair of `verify_validators.py` check `V4`. This is the second repair. FC-018 (run `run-d8937789961e`) fixed the investigation-report mutation row, but its own closure record, which that run committed as the newest `orchestration-result.md`, then left `V4` failing 5/6 on that artifact type. FC-018 recorded the failure honestly as its `FR-02` fail and its open item `O-007`; this proposal closes that item. FC-018 itself is unedited and accurate at its authoring baseline. Two defects shared one verifier. First, `V4` selected one instance per artifact type by run-id sort order and never checked that the mutation applies to it. Second, the orchestration locator `award_itself_its_own_gate` required identifiers wrapped in backticks, while the contract engine (`artifact_contract`, `defined_ids`) treats backticks as optional. The closure record of FC-018's run rendered its phase identifiers without backticks, so the locator found no row and `V4` reported "no mutation anchor". Measured in triage: 90 committed instances across 13 artifact types, exactly one lacking the anchor. The honest account of how the earlier work went wrong has three parts. The FC-018 triage judged only one artifact type fragile, and was wrong. It rejected a fallback-instance option, and was wrong to. And the defect report that started this run claimed the trigger was a gate row of `none`; that mechanism was also wrong, because the real trigger is unbackticked identifier rendering. The first repair's closure record is what exposed all of it. The root cause analysis is at `runs/run-5f4422f26c3e/states/root-cause-analysis/artifacts/bug-analysis.md`. Selection-only would have passed by silently using an older instance, and locator-only would leave the class open, so both were chosen. The fix, all in `.claude/runtime/verify_validators.py`: `award_itself_its_own_gate` finds the row by its ID cell with or without backticks (`PHASE_ID_CELL`); new `candidate_instances`, `instance_label` and `mutation_outcome`; `conforming_instance` tries the candidates in the existing order and takes the first the mutation resolves on, never filtering on conformance, and returns the skipped candidates (its return shape is now four values). The main loop reports every skipped candidate. `V3` validates the used instance and every skipped candidate. `V4` fails naming every candidate when none applies. The console mutation line prints the observed outcome (it used to read "caught by O4 (all: None)"). The JSON summaries gain `skipped_candidates` and `mutation.finding`; the schema name is unchanged and no consumer exists beyond the test module, per the review. `tests/test_verify_validators_mutations.py` now holds 26 tests: 15 from the first repair and 11 from this run, and the new ones fail on the pre-fix verifier. An independent review (`omn-dev-2-reviewer`, opus) returned approve-with-corrections, every finding backed by a command it ran. Finding `F-001` (medium): a skipped candidate was never validated by `V3`; closed with `V3` over skipped candidates and a test that reproduces the exit-0 case and fails before the fix. Finding `F-002` (low): a test depended on the working directory; closed. A correction pass closed both and the operator re-verified. The bundled mirror was refreshed.
- In scope: `.claude/runtime/verify_validators.py` and the run `run-5f4422f26c3e` over the `fix-bug` workflow with this governance record.
- Out of scope: any validator under test; runtime behaviour, which is unchanged; the two count mutation rows that substitute 99 (carried from FC-018); the label spelling limit (carried from FC-018); the orchestration contract's identifier rendering (`O-003`); the investigate-chain scheduler limitation behind the `S7` failure (`O-004`). The new test file and the bundled mirror are outside the framework surface.
- Acceptance basis: the routed run planned through the framework, with every phase executed by a host-dispatched subagent and validated on the first attempt with zero charged retries; every gate decided by a non-producing owner; the fix tested before and after; an independent reviewer whose findings carried command evidence; the standalone verifiers re-run and reported as they came out; the unit suite executed three times on this tree.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/verify_validators.py` | `SR-1` | in-scope | The verifier repaired: a framework surface the runtime resolves |
| `tests/test_verify_validators_mutations.py` | no rule | out-of-scope | Outside the framework surface; 26 tests, 11 of them new in this run |
| `omn_agent/_bundled_payload/runtime/verify_validators.py` | no rule | out-of-scope | Outside the framework surface; the bundled mirror, refreshed through `python tests/test_bundled_payload.py --sync` and never hand-edited |
| `.claude/runs/run-5f4422f26c3e/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this repair |
| `.claude/runs/inputs/verify-validators-v4-instance-selection-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-019.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The verifier `V4` is declared to prove that every registered validator rejects a mutated artifact, and it reported the validators uncovered because of which instance it happened to select and how that instance rendered its identifiers, not because of any validator.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` over the six paths of the table above returns `SR-1` in scope for `.claude/runtime/verify_validators.py` with the verdict "framework-internal change", no rule and out of scope for the test file and the bundled mirror, `SR-3` out of scope for the run evidence and the defect report, and `SR-5` out of scope for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` of 5, with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-5f4422f26c3e/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug`, input recorded with its digest |
| `E-2` | `runs/run-5f4422f26c3e/run-ledger.json` | resolved; runtime 0.9.0, 5 phases, run status Completed |
| `E-3` | `runs/run-5f4422f26c3e/events.jsonl` | resolved; 56 events from `run_initialized` to the final `run_completed`, E-0001 to E-0056 |
| `E-4` | `runs/run-5f4422f26c3e/state.json` | resolved; 5 phases completed, 0 blocked, 0 failed, 29 transitions |
| `E-5` | `runs/run-5f4422f26c3e/completion-package.md` | resolved; aggregated for 5 of 5 completed phases |
| `E-6` | `runs/run-5f4422f26c3e/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; the triage, with the measured extent of 90 instances across 13 types |
| `E-6` | `runs/run-5f4422f26c3e/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; the root cause analysis, with the two defects and the rejected single-fix options |
| `E-6` | `runs/run-5f4422f26c3e/states/fix-implementation/artifacts/implementation-report.md` | resolved; the fix, its tests and its post-review correction pass |
| `E-6` | `runs/run-5f4422f26c3e/states/regression-validation/artifacts/validation-report.md` | resolved; 8 of 8 criteria met |
| `E-6` | `runs/run-5f4422f26c3e/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; the closure record |
| `E-7` | `runs/run-5f4422f26c3e/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-5f4422f26c3e/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-5f4422f26c3e/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-5f4422f26c3e/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-5f4422f26c3e/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |
| `E-8` | `runs/run-5f4422f26c3e/execution-metrics.json` | resolved; the metrics cited under Verification |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed first attempt; validated 30 of 30; tier standard, host hint `inherit`; no charged retry | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-5f4422f26c3e/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed first attempt; validated 30 of 30; tier deep, host hint `opus`; no charged retry | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-5f4422f26c3e/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed first attempt; validated 32 of 32; tier deep, host hint `opus`. One offline correctable finding, `M4`, was fixed before completion; it was found by the offline validator run and so was not a charged attempt | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-5f4422f26c3e/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed first attempt; validated 31 of 31; tier standard, host hint `inherit`; 8 of 8 criteria met | `omn-qa` subagent, dispatched by the host | `runs/run-5f4422f26c3e/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed first attempt; validated 34 of 34; tier light, host hint `haiku`; no escalation | `omn-orchestrator` subagent, dispatched by the host | `runs/run-5f4422f26c3e/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-5f4422f26c3e`: 5 completed, 0 blocked, 0 failed, 0 pending, 0 retrying, run status Completed, 29 transitions, 0 replays suppressed. The recovery ledger holds seven classified failures, all of class `gate-approval-required`, all resolved, at 0 of 3 attempts charged. Every phase was validated on the first attempt, with no charged retry.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Triage validated 30 of 30 and the defect traces to the supplied report; `omn-dev-1-bug-analyst` produced the evidence and is excluded from deciding |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, dispatched independently of the implementer, recorded by the session operator | Verdict approve-with-corrections, recorded verbatim in the gate decision at E-0034. Findings `F-001` (medium) and `F-002` (low) each carried the command the reviewer ran, and both were closed in a correction pass that the operator re-verified |
| Verification Gate | approve | omn-dev-2-reviewer | operator on behalf of omn-dev-2-reviewer | Regression validation validated 31 of 31 with 8 of 8 criteria met; `omn-qa` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-documentation | operator on behalf of omn-documentation | Closure validated 34 of 34; `omn-orchestrator` produced the evidence and is excluded from deciding |

Producer exclusion held at every gate: no gate was decided by the agent that produced its evidence. Contrast with FC-018: the premise of that review's `F-002` was wrong and was caught only because the implementer questioned it. In this run the rule that a finding about tool behaviour must carry command evidence was applied, and it worked: both findings were reproducible.

## Verification

All commands were run from the repository root of this worktree, standalone, and the results are what they returned.

| Check | Command | Result |
|---|---|---|
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED. `V4` reads the real committed closure records: orchestration-result.md is caught by `O4`, investigation-report.md by `I1`, and the line ends "no candidate skipped". `V3` accepts all 13 types, orchestration-result.md at 34/34 on a committed run artifact. This is the result FC-018 could not reach (5/6) |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, 37 of 37 phases dispatchable |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 CONFORMS |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | fail; 6/8 NOT SELF-HOSTING, run before this proposal was on disk. `S1` to `S6` pass, `S6` accepting FC-001 to FC-018. `S7` fails on `run-437e2f765e4b` (FC-017's investigate run), whose `C-3` is False because its publication phase is pending: the scheduler does not block downstream phases of a blocked phase, a framework limitation that run made visible (`O-004`). `S8` names two unaccounted runs, `run-5df08e171670` (pre-existing, `O-005`) and `run-5f4422f26c3e`, which this proposal accounts for |
| Vertical slice | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN. The run appends replay records to that committed run; they were restored with `git checkout -- .claude/runs/run-c5a8d50d3238/state.json .claude/runs/run-c5a8d50d3238/task-context.yaml`, and `git status` then showed no change under that run |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | 14/15 NOT PROVEN, advisory item, the same result as FC-018. The one failing check is `M14`, the re-run of the same request: `dispatch` of `execution-planning` exited non-zero. `M1` to `M13` and `M15` pass. The run was restored as above and a stray `state.json.tmp` removed; `git status` shows no change under that run. This verifier does not import `verify_validators.py`, and the failure is not evidenced as caused by this change |
| Recovery | inspection | `verify_recovery.py` was not run, because it mutates committed run evidence and no throwaway copy was made. The FC-016 result, 73/74 with `X1` pre-existing, is cited as unchanged: `verify_recovery.py` does not import `verify_validators.py`, the only runtime file changed |
| Unit suite | `python tools/run_tests_parallel.py` | pass; 668 of 668, executed three times independently on this tree: by the operator, by `omn-qa`, and by the operator again after the corrections. Not re-run while authoring this proposal. The FC-018 baseline was 657; the 11 new tests make 668 |
| Defect witnessed and fixed | `python tests/test_verify_validators_mutations.py`, against the pre-fix and post-fix verifier | the 11 new tests fail on the pre-fix verifier and pass on the fixed one; 26 of 26 pass after the fix. The `V3` exit-0 case for a skipped candidate (`F-001`) also fails before its correction. Evidence in the implementation report and the validation report |
| Run metrics | inspection of `runs/run-5f4422f26c3e/execution-metrics.json` | wall clock 59m32s, agent-active 43m41s. Invocations by tier: 1 light, 2 standard, 2 deep, 0 untiered; the non-deep share is 60 percent. Observation, not proof of a tier defect: the two light-tier (haiku) closure records, this run's and FC-018's, differ in identifier rendering (FC-018's omitted backticks). That format variance is what the framework's own verifier then had to be hardened against. It is one pair of records and is not a controlled comparison |

## Risk and Rollback

- Blast radius: one verifier (`.claude/runtime/verify_validators.py`), one new test file (`tests/test_verify_validators_mutations.py`) and one bundled mirror (`omn_agent/_bundled_payload/runtime/verify_validators.py`). No validator, runtime behaviour, config, agent, workflow, registry or template file changed, and `RUNTIME_VERSION` is unchanged at 0.9.0.
- Risk assessment: `R-001`: `V4` may now pass on an older instance while a newer one goes unmutated. The mitigations are that skipped candidates are printed and stored in the JSON summaries, and that `V3` validates every skipped candidate. No role has formally accepted the risk, which is why it is monitored under `O-001`. Two carried limits remain from FC-018: the two count rows that substitute 99 would fail loudly on a real count of 99, and the derivation matches only the template's field-label spelling, so another spelling fails loudly as a missing anchor and never silently.
- Rollback procedure: revert the three files, `.claude/runtime/verify_validators.py`, `tests/test_verify_validators_mutations.py` and the bundled mirror, then run `python tests/test_bundled_payload.py --sync` and confirm `python tests/test_bundled_payload.py` passes. The first repair, FC-018, lives in the same file, so reverting this proposal alone restores the pre-FC-019 selector and locator, not the pre-FC-018 verifier; `V4` then returns to 5/6 on the orchestration-result.md row. The test count falls from 668 to 657. No committed run evidence is invalidated.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED, `V4` reading the real committed closure records, no candidate skipped |
| `FR-03` | Recovery behaviour | pass | Not re-run, because it mutates committed run evidence. The FC-016 result, 73/74 with `X1` pre-existing, is carried unchanged because `verify_recovery.py` does not import `verify_validators.py` |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN; the committed run restored afterwards |
| `FR-05` | Self-hosting governance resolves | fail | 6/8; `S7` on `run-437e2f765e4b` (FC-017's investigate run, publication pending, `O-004`) and `S8` on `run-5df08e171670` (pre-existing, `O-005`) and on `run-5f4422f26c3e`, which this proposal accounts for |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-5f4422f26c3e` is a `/bugfix` run over `fix-bug`, all five phases completed and all four gates decided; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | `RUNTIME_VERSION` stays 0.9.0: a verifier changed, not runtime behaviour |
| `FR-08` | Documentation matches delivered behaviour | pass | No documented behaviour changed; no documentation touched |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row is a command output or a cited artifact. Gaps are recorded rather than omitted: `O-001` to `O-007` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | fail | 14/15; `M14` failed on the re-run of the same request. Advisory item, identical to FC-018's result. Characterised afterwards, on 2026-10-09: intermittent in this worktree path (14/15 in 3 of 4 clean-state runs, 15/15 in 1) and absent when the identical uncommitted tree is copied to a temporary directory (15/15 in 4 of 4) and on a clean export of the base commit (15/15 in 4 of 4), so it is an environment effect of the worktree location, not caused by this change |
| `FR-12` | Release note where consumer-visible behaviour changed | not applicable | No consumer-visible behaviour changed; a verifier changed |

`FR-05` and `FR-11` are reported as failures as the commands returned them. The recovery result is carried from FC-016, not re-run.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | `R-001`: `V4` may pass on an older instance while a newer one goes unmutated | omn-tech-lead | Open. Monitor the printed skipped-candidate lines; decide whether to accept the risk formally |
| `O-002` | The `V3` `F7` check rejects the change proposal when the verifier runs from inside the framework directory (cwd-dependent) | omn-tech-lead | Open. A separate defect, not part of this repair |
| `O-003` | Whether the orchestration contract should fix identifier rendering, or verifiers keep locating rows by meaning | architect | Open. This repair chose the second; the contract question is undecided |
| `O-004` | `S7` fails on `run-437e2f765e4b`: its publication phase is pending behind a blocked recommendation phase, which the scheduler never marks blocked | architect | Open. The real repair is the three investigate-chain contract defects FC-017 recorded, after which that run could be completed |
| `O-005` | `S8` fails on `run-5df08e171670`, a run without a proposal, pre-existing | omn-orchestrator | Open, pre-existing. Closes only by a proposal authored by whoever carried that change; fabricating one would falsify the record |
| `O-006` | The implementation report prose counts 25 tests and 667 in total, while the actual figures after the post-review pass are 26 and 668 | omn-dev-1-implement | Open. Committed evidence is not edited; the correct figures are recorded here |
| `O-007` | Four artifact types have no fixture (`scope-definition.md`, `execution-plan.md`, `technical-design.md`, `framework-change-proposal.md`), so their coverage depends on committed run evidence | omn-qa | Open. Add a fixture for each, or record that a committed instance must exist |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates and omn-documentation at the Closure Gate, each recorded by the operator or the independently dispatched reviewer, none of them the producer of the evidence it decided
- Acceptance basis: all five phases of the routed workflow executed by host-dispatched subagents and accepted by their registered validators on the first attempt with no charged retry; all four gates approved with producer exclusion held; the defect witnessed before the fix and closed after it; the unit suite passing 668 of 668 three times on this tree; `V4` at 6/6 and FC-018's open item closed; the verifier failures (`S7`, `S8`, `M14`) reported as returned; and seven open items recorded with an owner
