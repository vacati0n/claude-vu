# Framework Change Proposal: Admit the runtime's `policy-exception` clearing action in recovery check `X1` (run-e7bf0d73027a)

```yaml
frameworkChangeProposal:
  proposalId: FC-024
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-e7bf0d73027a
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-024
- Change title: Admit the runtime's `policy-exception` clearing action in recovery check `X1` (run-e7bf0d73027a)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-e7bf0d73027a
- Authored on: 2026-10-18

## Authoring Baseline

- Authored at: 2026-10-18T09:41:35Z
- Runtime version: 0.10.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: make `python .claude/runtime/verify_recovery.py` prove recovery again. Since 097e8f4 it has reported 73/74, NOT PROVEN, because check `X1` judged the runtime's own clearing action for an `awaiting_policy_exception` block inadmissible. The runtime emits `framework_runtime.py policy-exception --run-id <id> --phase <phase> --owner-role <role> --decided-by <who> --rationale <text>`, and `cmd_policy_exception` clears the block. The verifier's admissibility table in `clearing_action_admissible` had no row for `policy-exception`, and no placeholder exemption for its three human-judgement flags. The root-cause analysis established that the runtime action is the intended contract and the table was not extended when that command was added. The fix adds the row and an exemption scoped to state items blocked `awaiting_policy_exception`.
- In scope: `runtime/verify_recovery.py` (`clearing_action_admissible`: the `awaiting_policy_exception` predicate, the exemption of `--owner-role`, `--decided-by` and `--rationale` on exactly that item, and the `policy-exception` row with its listed-owner and producer-exclusion guards), and its byte-identical bundled copy `omn_agent/_bundled_payload/runtime/verify_recovery.py`. Also the 16 admissibility cases in `tests/test_clearing_action_admissibility.py` delivered by this run, and the run `run-e7bf0d73027a` over `fix-bug`.
- Out of scope: the clearing-action builder and `cmd_policy_exception` in `runtime/framework_runtime.py`, which are unchanged. The regression cases this run's Verification Gate found missing (`DF-001`, `DF-002`), which are carried by `run-5e9d799db687` under `FC-025`. The undecided owner-role list of runtime-emitted policy-exception envelopes (`O-003`). The demonstration-capture run and its proposal `FC-023`.
- Acceptance basis: the run planned through the framework by the routed command; every phase of the routed workflow executed by a host-dispatched subagent and accepted by its registered validator; all four gates decided with producer exclusion held. The Verification Gate was rejected once, rolled back under an authorisation, and approved on QA attempt 2. `verify_recovery.py` reports 74/74 on the delivered tree.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/verify_recovery.py` | `SR-1` | in-scope | `clearing_action_admissible`: the `policy-exception` row and its scoped placeholder exemption |
| `omn_agent/_bundled_payload/runtime/verify_recovery.py` | no rule | out-of-scope | Outside the framework surface; bundled mirror, byte-identical (`tests/test_bundled_payload.py` 11/11) |
| `tests/test_clearing_action_admissibility.py` | no rule | out-of-scope | Outside the framework surface; the 16 admissibility cases of this run (it gains 7 more under `FC-025`) |
| `.claude/runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md` | `SR-3` | out-of-scope | Run evidence written during the run |
| `.claude/runs/inputs/recovery-x1-policy-exception-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-024.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The recovery verifier, the framework's authority on current recovery behaviour (`GD-001` item 5), rejected a clearing action the runtime emits by contract and can execute.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` returns `SR-1` in scope ("framework-internal change") for `.claude/runtime/verify_recovery.py`, no rule for the bundled mirror and the test module, `SR-3` for the run evidence and the input, and `SR-5` for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-e7bf0d73027a/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug` 1.0.0, submitted 2026-10-17T13:16:00Z at runtime 0.10.0, input `defect-report` with digest `sha256:f9de6fe446b80423637c7ebcb42381e7` |
| `E-2` | `runs/run-e7bf0d73027a/run-ledger.json` | resolved; 5 phases, run status Completed |
| `E-3` | `runs/run-e7bf0d73027a/events.jsonl` | resolved; 69 events, from `run_initialized` to `run_completed` at 2026-10-18T09:34:02Z |
| `E-4` | `runs/run-e7bf0d73027a/state.json` | resolved; 5 phases completed, 4 gates approved, 38 transitions; the Verification Gate carries one rejection in `decision_history` |
| `E-5` | `runs/run-e7bf0d73027a/completion-package.md` | resolved; aggregated over 5 completed phases, with the superseded `regression-validation` attempt 1 listed under Superseded Attempts |
| `E-6` | `runs/run-e7bf0d73027a/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; severity medium, reproducibility deterministic |
| `E-6` | `runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; root cause: the admissibility table was not extended when `policy-exception` became the clearing action; `Q-001` answered by an executed run (`E-018`) |
| `E-6` | `runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md` | resolved; IR-2026-1015, the row and exemption, 16 admissibility tests (8 fail against HEAD), deviations `V-001` and `V-002` |
| `E-6` | `runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md` | resolved; attempt 1, verdict fail: `AC-007` and `AC-009` not met, `DF-001` and `DF-002` open, no regression; superseded by `RB-run-e7bf0d73027a-verification-gate-01` |
| `E-6` | `runs/run-e7bf0d73027a/states/regression-validation/artifacts/attempt-2/validation-report.md` | resolved; attempt 2, verdict pass: 9 of 9 criteria met, `DF-001` and `DF-002` resolved |
| `E-6` | `runs/run-e7bf0d73027a/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; disposition closed-with-followups, follow-ups `FU-001` to `FU-008` |
| `E-7` | `runs/run-e7bf0d73027a/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-e7bf0d73027a/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-e7bf0d73027a/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-e7bf0d73027a/states/regression-validation/validation-report.json` | resolved; 31 of 31, attempt 2 |
| `E-7` | `runs/run-e7bf0d73027a/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed on 2026-10-17 on the first attempt; validated 30 of 30 | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-e7bf0d73027a/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed on 2026-10-17 on the first attempt; validated 30 of 30. `Q-001` closed by executing `policy-exception` in a temporary tree copy, as the Triage Gate required | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-e7bf0d73027a/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed on 2026-10-17 on the first attempt; validated 32 of 32. `verify_recovery.py` 74/74, 16 new tests, bundled copy byte-identical | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-e7bf0d73027a/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Attempt 1 (2026-10-17) returned fail on `AC-007` and `AC-009` and was superseded by rollback `RB-run-e7bf0d73027a-verification-gate-01`. Attempt 2 (2026-10-18), run after `run-5e9d799db687` delivered the missing tests, returned pass with 9 of 9 criteria met; validated 31 of 31 | `omn-qa` subagent, dispatched by the host for each attempt | `runs/run-e7bf0d73027a/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed on 2026-10-18 on the first attempt; validated 34 of 34; closed with follow-ups | `omn-orchestrator` subagent, dispatched by the host | `runs/run-e7bf0d73027a/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-e7bf0d73027a` at authoring: 5 completed, 0 blocked, 0 failed, 0 pending, 38 transitions, run status Completed.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | omn-tech-lead subagent a7d77e86c588e22cd, recorded by session operator for vuhoangcao, 2026-10-17T13:29:19Z | Severity medium, blast radius and deterministic reproduction settled; validator 30/30. Conditions: close `Q-001` by executing `policy-exception` end to end; the exemption covers only `policy-exception` on items blocked `awaiting_policy_exception`, with negative cases tested; the bundled copy changes the same way |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent acc8a10555792a6cf, recorded by session operator for vuhoangcao, 2026-10-17T14:30:28Z | Re-run: 16 new tests pass and 8 fail against HEAD; `verify_recovery.py` 74/74; bundled copy byte-identical; all three Triage Gate conditions hold. The end-to-end gap `V-001` was carried to QA |
| Verification Gate | reject, then approve | omn-dev-2-reviewer | Rejected by omn-dev-2-reviewer subagent aa873028df2545b4e, 2026-10-18T03:52:13Z. Approved by omn-dev-2-reviewer subagent a1b1e436e38c12a2d, 2026-10-18T09:26:57Z. Both recorded by session operator for vuhoangcao | Rejected because `AC-007` and `AC-009` were unmet (`DF-001`, `DF-002`). The runtime refused a rollback to `fix-implementation` because the Fix Gate was approved, so the tests were carried by `run-5e9d799db687`. The rollback to `regression-validation` was authorised on vuhoangcao's instruction. Approved on attempt 2: 9 of 9 criteria met; independent re-run 25/25 |
| Closure Gate | approve | omn-documentation | omn-documentation subagent ac3e08e474e38163d, recorded by session operator for vuhoangcao, 2026-10-18T09:34:02Z | fix-bug exit criteria hold on evidence from other roles; follow-ups `FU-001` to `FU-008` carried as known-issue status. Approval closes the run; it does not authorise a commit or release |

Producer exclusion held at every gate. No gate was decided by the agent that produced the evidence it assesses.

## Verification

| Check | Command | Result |
|---|---|---|
| Recovery | `python .claude/runtime/verify_recovery.py` | pass; 74/74 RECOVERY PROVEN, exit 0, re-run by the operator at authoring. The worktree was unchanged afterwards |
| Admissibility and policy-exception regression tests | `python -m unittest tests.test_policy_exception_command tests.test_clearing_action_admissibility -v` | pass; 25 of 25 (the 16 of this run, plus 9 delivered under `FC-025`), per QA attempt 2 and the Verification Gate re-run |
| Fail-before witness | inspection of `runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md` | Run against the HEAD `verify_recovery.py`, 8 of the 16 admissibility tests fail, per the implementation report and the Fix Gate re-run |
| Bundled payload | `PYTHONPATH=. python tests/test_bundled_payload.py` | pass; 11 of 11, copy byte-identical |
| Full suite | `python tools/run_tests_parallel.py` | All tests pass except the 3 known `test_demo_capture` `EndToEndEditTestCase` ffmpeg failures (`FC-023` `O-003`), per QA attempt 2 |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, re-run at authoring |
| Validators | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED, re-run at authoring |
| Committed evidence | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, re-run at authoring |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN on a temporary copy of the tree. In place it fails `M14` and rewrites `run-c5a8d50d3238`, the environment effect `FC-020` to `FC-022` record; the operator restored the run with `git restore` |

## Risk and Rollback

- Blast radius: `clearing_action_admissible` in `runtime/verify_recovery.py` and its bundled mirror. That function is reached by `X1` and by scenario D checks `D4`, `D23` and `D27`, all of which pass. No runtime behaviour changes, so no run executes differently.
- Risk assessment: low. The exemption is scoped to one subcommand on one blocked reason, and negative cases pin each neighbouring state. The residual risk is that runtime-emitted policy-exception envelopes list no owner roles. Any non-producer role is then admissible: this is exercised but not asserted (`O-003`).
- Rollback procedure: revert the `clearing_action_admissible` hunk in both copies of `verify_recovery.py`. Reverting it breaks the 16 admissibility tests and the `FC-025` tests that depend on the row, and returns `verify_recovery.py` to 73/74, so revert `FC-025`'s tests with it. Run evidence under `runs/run-e7bf0d73027a/` stays as a historical record.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | `python .claude/runtime/verify_validators.py`: 6/6; no validator changed |
| `FR-03` | Recovery behaviour | pass | 74/74 RECOVERY PROVEN; this change is the repair of the `X1` failure recorded since 097e8f4 |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | pass | `S6` accepts this proposal and `S7` passes for `run-e7bf0d73027a`; with `FC-025`, `S8` lists neither run |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-e7bf0d73027a` is a `/bugfix` run over `fix-bug`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Unchanged at 0.10.0; only the verifier changed, and `runtime/framework_runtime.py` has no diff |
| `FR-08` | Documentation matches delivered behaviour | pass | No document describes the `X1` admissibility table (`runtime/README.md`, `README.md`, `validation/` searched); the function docstring was extended with the new row |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim cites a run artifact or a command re-run at authoring. The Verification Gate rejection, the refused rollback, the separate test run, the unasserted owner-list case and the unobserved CI are disclosed |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 on a temporary copy; the in-place `M14` failure is the recorded environment effect |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | No consumer-visible behaviour changes: the verifier now passes where it failed, and the runtime is unchanged |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Commit order: the `verify_recovery.py` change and its bundled copy go in with or before the `FC-025` test modules (`FU-001`) | session operator | Open until commit |
| `O-002` | The CI recovery-verifier job has not been observed on the ubuntu or windows runners (`FU-003`); confirm on the default branch after commit | omn-qa | Open |
| `O-003` | Runtime-emitted policy-exception envelopes list no owner roles, so the listed-owner guard is unreachable and any non-producer role is admissible; exercised, not asserted (`FU-004`). Security-relevant | architect | Open |
| `O-004` | Nothing re-checks `X1` automatically after the block clears; the IR-2026-1018 mutation witnesses were not re-run at the Verification Gate (`FU-006`) | omn-qa | Open |
| `O-005` | 3 `test_demo_capture` `EndToEndEditTestCase` cases fail locally on an ffmpeg option, before and after this change (`FU-008`, `FC-023` `O-003`) | omn-tech-lead | Open; not caused by this change |
| `O-006` | The `X1` half of `FC-022` open item 015 (the `FR-03` failure recorded as pre-existing) | session operator | Closed by this proposal: `verify_recovery.py` reports 74/74 (`FU-007`) |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates, and omn-documentation at the Closure Gate, on 2026-10-17 and 2026-10-18. Each was an independently dispatched subagent, recorded by the session operator for vuhoangcao
- Acceptance basis: every phase of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; the completion package aggregated; the Verification Gate rejection carried through an authorised rollback rather than overridden; every open item has an owner
