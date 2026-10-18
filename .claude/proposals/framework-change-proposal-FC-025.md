# Framework Change Proposal: Add the missing regression tests for the `X1` policy-exception repair (run-5e9d799db687)

```yaml
frameworkChangeProposal:
  proposalId: FC-025
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-5e9d799db687
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-025
- Change title: Add the missing regression tests for the `X1` policy-exception repair (run-5e9d799db687)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-5e9d799db687
- Authored on: 2026-10-18

## Authoring Baseline

- Authored at: 2026-10-18T09:41:35Z
- Runtime version: 0.10.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: deliver the two regression cases that the Validation Plan of `run-e7bf0d73027a` (`FC-024`) required but its fix left out. Their absence was why that run's Verification Gate was rejected (`DF-001`, `DF-002`). The runtime refused a rollback of that run to `fix-implementation`, because its Fix Gate was approved and a completed gate cannot be re-armed. The tests were therefore carried by this separate `/bugfix` run, submitted on vuhoangcao's instruction. `DF-001`: no automated case executed the `policy-exception` clearing action with role, decider and rationale filled. `DF-002`: the admissibility module had no case pinning the unchanged rollback row. The root-cause analysis traced the gap to a process step, not to code. No step traced each planned regression case to a delivered test before the Fix Gate.
- In scope: `tests/test_policy_exception_command.py` (added). It holds 2 end-to-end cases, each in its own temporary copy of `.claude/`. They drive a run to a state item blocked `awaiting_policy_exception` and execute the emitted action. The producer role is refused, a non-producer clears the block and the envelope resolves, a repeat is refused, and an unlisted role is refused once owners are listed. Also `RollbackRowUnchangedTestCase` in `tests/test_clearing_action_admissibility.py` (7 cases; the module goes from 16 to 23), and the run `run-5e9d799db687` over `fix-bug`.
- Out of scope: any runtime or verifier source, which this run left unchanged as its Triage Gate required. The `verify_recovery.py` repair itself (`FC-024`). The owner-role list of runtime-emitted policy-exception envelopes (`O-002`). The process gap the root-cause analysis names (`O-004`).
- Acceptance basis: the run planned through the framework by the routed command; every phase of the routed workflow executed by a host-dispatched subagent and accepted by its registered validator; all four gates approved with producer exclusion held. Each guard the new tests assert is shown by a mutation that makes them fail. `run-e7bf0d73027a` then passed its QA retest with these tests present.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `tests/test_policy_exception_command.py` | no rule | out-of-scope | Outside the framework surface; the `DF-001` end-to-end cases (`C-001`) |
| `tests/test_clearing_action_admissibility.py` | no rule | out-of-scope | Outside the framework surface; `RollbackRowUnchangedTestCase` for `DF-002` (`C-002`) |
| `.claude/runs/run-5e9d799db687/states/fix-implementation/artifacts/implementation-report.md` | `SR-3` | out-of-scope | Run evidence written during the run |
| `.claude/runs/inputs/recovery-x1-missing-regression-tests-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-025.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

No path this run changed is on the framework surface. The run is recorded because `S8` requires every framework run inside the self-hosted window to be accounted for by a proposal, and because its tests are the regression evidence for `FC-024`'s `SR-1` change.

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The `fix-bug` delivery of `FC-024` omitted regression cases its approved Validation Plan declared, and `run-e7bf0d73027a`'s Verification Gate rejected it on that ground.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` returns no rule for both test modules, `SR-3` for the run evidence and the input, and `SR-5` for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-5e9d799db687/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug` 1.0.0, submitted 2026-10-18T07:43:01Z at runtime 0.10.0, input `defect-report` with digest `sha256:7412953e071deb829255cfefaf1cc9e5` |
| `E-2` | `runs/run-5e9d799db687/run-ledger.json` | resolved; 5 phases, run status Completed |
| `E-3` | `runs/run-5e9d799db687/events.jsonl` | resolved; 56 events, from `run_initialized` to `run_completed` at 2026-10-18T09:08:33Z |
| `E-4` | `runs/run-5e9d799db687/state.json` | resolved; 5 phases completed, 4 gates approved, 29 transitions |
| `E-5` | `runs/run-5e9d799db687/completion-package.md` | resolved; aggregated over 5 completed phases |
| `E-6` | `runs/run-5e9d799db687/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; severity medium, reproducibility deterministic |
| `E-6` | `runs/run-5e9d799db687/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; root cause: no step traced planned regression cases to delivered tests before the Fix Gate; the Validation Plan specifies both tests and the mutations each must catch |
| `E-6` | `runs/run-5e9d799db687/states/fix-implementation/artifacts/implementation-report.md` | resolved; IR-2026-1018, `C-001` and `C-002`, tests `T-001` to `T-008`, including mutation witnesses `T-004` and `T-005` |
| `E-6` | `runs/run-5e9d799db687/states/regression-validation/artifacts/validation-report.md` | resolved; VR-run-5e9d799db687-regression-validation, verdict pass, 7 of 7 criteria met, no defects |
| `E-6` | `runs/run-5e9d799db687/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; disposition closed-with-followups, follow-ups `FU-001` to `FU-010` |
| `E-7` | `runs/run-5e9d799db687/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-5e9d799db687/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-5e9d799db687/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-5e9d799db687/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-5e9d799db687/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed on 2026-10-18 on the first attempt; validated 30 of 30 | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-5e9d799db687/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed on 2026-10-18 on the first attempt; validated 30 of 30. Executed the emitted `policy-exception` action and `verify_recovery.py` itself, as the Triage Gate required | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-5e9d799db687/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed on 2026-10-18 on the first attempt; validated 32 of 32. Changed `tests/` only; all 5 mutations fail the tests; `verify_recovery.py` 74/74 | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-5e9d799db687/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed on 2026-10-18 on the first attempt; validated 31 of 31; verdict pass | `omn-qa` subagent, dispatched by the host | `runs/run-5e9d799db687/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed on 2026-10-18 on the first attempt; validated 34 of 34; closed with follow-ups | `omn-orchestrator` subagent, dispatched by the host | `runs/run-5e9d799db687/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-5e9d799db687` at authoring: 5 completed, 0 blocked, 0 failed, 0 pending, 29 transitions, run status Completed.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | omn-tech-lead subagent a19a0a451026f870b, recorded by session operator for vuhoangcao, 2026-10-18T07:50:50Z | Severity medium and deterministic reproduction established. Conditions: execute the emitted action and the verifier rather than rely on reported evidence; change `tests/` only and keep 74/74; run the end-to-end case in an isolated tree; both cases fail against mutated code; every planned test maps to a passing test or a recorded deviation |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent ad61abc5e66f8eadc, recorded by session operator for vuhoangcao, 2026-10-18T08:44:40Z | Re-run: 25/25; `verify_recovery.py` 74/74; nothing new under `.claude/runs`. Two claimed mutations re-executed in a temporary copy and failed as claimed; only `tests/` changed |
| Verification Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent a424c21853dc34594, recorded by session operator for vuhoangcao, 2026-10-18T09:02:04Z | Re-run 25/25; QA 7 of 7 criteria met, 0 defects. Carried: the unasserted no-owners case, the dependency on committed `run-c5a8d50d3238`, and the commit order behind `FC-024` |
| Closure Gate | approve | omn-documentation | omn-documentation subagent a11b55ed69a71a624, recorded by session operator for vuhoangcao, 2026-10-18T09:08:32Z | fix-bug exit criteria met; follow-ups `FU-001` to `FU-010` owned and open |

Producer exclusion held at every gate. No gate was decided by the agent that produced the evidence it assesses.

## Verification

| Check | Command | Result |
|---|---|---|
| New and extended test modules | `python -m unittest tests.test_policy_exception_command tests.test_clearing_action_admissibility -v` | pass; 25 of 25 (2 end-to-end, 23 admissibility), re-run at the Fix and Verification Gates and in `run-e7bf0d73027a` QA attempt 2 |
| Mutation witnesses | inspection of `runs/run-5e9d799db687/states/fix-implementation/artifacts/implementation-report.md` | `T-004` and `T-005`: 5 mutations, each making the tests fail (1, 1, 2, 2 and 4 failures); 2 re-executed at the Fix Gate |
| Recovery | `python .claude/runtime/verify_recovery.py` | pass; 74/74 RECOVERY PROVEN, exit 0, re-run by the operator at authoring |
| Bundled payload | `PYTHONPATH=. python tests/test_bundled_payload.py` | pass; 11 of 11. Run bare in this worktree it fails 1 case, because it imports `omn_agent` from the main checkout (`O-005`) |
| Full suite | `python tools/run_tests_parallel.py` | 796 tests ran; the only failures are the 3 known `test_demo_capture` `EndToEndEditTestCase` ffmpeg cases |
| Run evidence untouched | `git status --short .claude/runs` | Nothing new under `.claude/runs` from the tests |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, re-run at authoring |
| Validators | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED, re-run at authoring |
| Committed evidence | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, re-run at authoring |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN on a temporary copy of the tree; in place `M14` fails, the recorded environment effect |

## Risk and Rollback

- Blast radius: two test modules. No framework, runtime or verifier source changes, and no run executes differently.
- Risk assessment: low. The end-to-end module copies `.claude/` into a temporary directory, so it never writes run evidence. It does read committed `run-c5a8d50d3238` as its conforming artifact, so a change to that record breaks the test, not the behaviour (`O-003`). It adds about 45 s to the suite (`O-006`).
- Rollback procedure: delete `tests/test_policy_exception_command.py` and remove `RollbackRowUnchangedTestCase` from `tests/test_clearing_action_admissibility.py`. That returns `run-e7bf0d73027a`'s `AC-007` and `AC-009` to not met, so its Verification Gate approval would no longer be supported. Revert `FC-024` with it, or record the risk acceptance.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | `python .claude/runtime/verify_validators.py`: 6/6; no validator changed |
| `FR-03` | Recovery behaviour | pass | 74/74 RECOVERY PROVEN; no recovery behaviour changed by this record |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN; the new tests read that run and never write it |
| `FR-05` | Self-hosting governance resolves | pass | `S6` accepts this proposal and `S7` passes for `run-5e9d799db687`; with `FC-024`, `S8` lists neither run |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-5e9d799db687` is a `/bugfix` run over `fix-bug`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Unchanged at 0.10.0; only tests changed |
| `FR-08` | Documentation matches delivered behaviour | pass | No documentation describes these tests or needed to change |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim cites a run artifact or a command re-run at authoring. The refused rollback, the bare bundled-payload failure, the unasserted owner-list case and the unobserved CI are disclosed |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 on a temporary copy |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | No consumer-visible behaviour changed |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Commit order: these test modules go in only with or after `FC-024`'s `verify_recovery.py` change, because `tests/test_clearing_action_admissibility.py` carries both runs' cases (`FU-002`) | session operator | Open until commit |
| `O-002` | Runtime-emitted policy-exception envelopes list no owner roles, so any non-producer role clears the block; exercised, not asserted (`FU-004`, `FC-024` `O-003`). Security-relevant | architect | Open |
| `O-003` | The end-to-end module depends on committed `run-c5a8d50d3238`; after commit, observe the CI unit and recovery-verifier jobs on the default branch (`FU-005`) | omn-qa | Open |
| `O-004` | Decide whether Validation Plan regression cases must be traced item by item to delivered tests before the Fix Gate, the gap this run's root cause names (`FU-006`) | architect | Open |
| `O-005` | Bare `python tests/test_bundled_payload.py` imports `omn_agent` from the main checkout in a worktree and fails one case (`FU-009`) | omn-qa | Open; not caused by this change |
| `O-006` | Unpinned paths: rollback target-range and attempt-budget refusals, and policy-exception terminal-status replay (`FU-007`). The end-to-end module copies `.claude/` twice, about 45 s (`FU-010`) | omn-qa | Open |
| `O-007` | Roll `run-e7bf0d73027a` back to `regression-validation` for a QA retest with these tests present (`FU-001`) | session operator | Closed: rollback `RB-run-e7bf0d73027a-verification-gate-01` was authorised, QA attempt 2 passed 9 of 9, and that run is Completed |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates, and omn-documentation at the Closure Gate, on 2026-10-18. Each was an independently dispatched subagent, recorded by the session operator for vuhoangcao
- Acceptance basis: every phase of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; the completion package aggregated; every guard the tests assert witnessed by a failing mutation; every open item has an owner
