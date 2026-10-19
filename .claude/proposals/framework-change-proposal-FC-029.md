# Framework Change Proposal: Make the `release` clearing action runnable as written (run-34fbc64712b5)

```yaml
frameworkChangeProposal:
  proposalId: FC-029
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-34fbc64712b5
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-029
- Change title: Make the `release` clearing action runnable as written (run-34fbc64712b5)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-34fbc64712b5
- Authored on: 2026-10-19

## Authoring Baseline

- Authored at: 2026-10-19T07:40:00Z
- Runtime version: 0.10.1. The run was submitted at 0.10.0, and this change raises it.
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: close `FC-027` open item `O-002`. `clearing_action` in `runtime/framework_runtime.py` built its `release` command with `--detail <what happened>`, which is free text in angle brackets, unquoted. That command is the clearing action for a state work item blocked `awaiting_recovery_task` that no guard raised, and the optional reclaim in the retry-class prose. bash, PowerShell and cmd.exe all reject it before `release` runs. `verify_recovery.placeholders` flags it, so `X1` rejects any open envelope that carries it. The root-cause analysis found the cause: `--detail` needs no human judgement, but the builder left it a placeholder instead of filling it the way the gate and policy-exception branches fill theirs.
- In scope: `runtime/framework_runtime.py`. `clearing_action` now fills `--detail` with fixed text, quoted by the existing `_shell_word` helper: "operator cleared the block with the prescribed release action". The `none required` retry prefix, the `release` subcommand and every other branch are unchanged. `RUNTIME_VERSION` goes from 0.10.0 to 0.10.1, as `FR-07` requires. Also in scope: `tests/test_release_clearing_action.py` (added, 12 tests built only from the builder's output), the version pin in `tests/test_knowledge.py`, and the run `run-34fbc64712b5` over `fix-bug`.
- Out of scope: any verifier change, and no `X1` exemption, as the Triage Gate required. The 33 committed failure-envelope entries in 14 runs that carry the old text, all resolved and left as recorded. The `runtime/README.md` synopsis that still shows `--detail "<what happened>"`, which the Triage Gate made optional (`O-004`). The retry reclaim's no-op on a `retrying` item (`O-003`).
- Acceptance basis: the run was planned through the framework by the routed command. Every phase of the routed workflow was executed by a host-dispatched subagent and accepted by its registered validator. All four gates were approved with producer exclusion held. The new tests fail against the old text as mutation witnesses, and every verifier passes on a temporary copy of the tree.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | `clearing_action` detail and `RUNTIME_VERSION`: the change this proposal carries |
| `tests/test_release_clearing_action.py` | no rule | out-of-scope | Outside the framework surface; the regression tests the Validation Plan names |
| `tests/test_knowledge.py` | no rule | out-of-scope | Outside the framework surface; the exact `RUNTIME_VERSION` pin moves to 0.10.1 (`V-002`) |
| `.claude/runs/run-34fbc64712b5/` | `SR-3` | out-of-scope | Run evidence written during the run |
| `.claude/runs/inputs/release-clearing-action-placeholder-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-029.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. `clearing_action`'s docstring promises the exact next action that clears the condition, and the `release` action it emits cannot be executed as written.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` returns `SR-1` for `runtime/framework_runtime.py`, no rule for both test modules, `SR-3` for the run evidence and the input, and `SR-5` for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-34fbc64712b5/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug` 1.0.0, submitted 2026-10-19T05:18:45Z at runtime 0.10.0, input `defect-report` with digest `sha256:71fa90ad70f8c8ffcafa075848b9659e` |
| `E-2` | `runs/run-34fbc64712b5/run-ledger.json` | resolved; 5 phases, run status Completed |
| `E-3` | `runs/run-34fbc64712b5/events.jsonl` | resolved; 56 events, from `run_initialized` to `run_completed` at 2026-10-19T07:22:53Z |
| `E-4` | `runs/run-34fbc64712b5/state.json` | resolved; 5 phases completed, 4 gates approved, 29 transitions |
| `E-5` | `runs/run-34fbc64712b5/completion-package.md` | resolved; aggregated over 5 completed phases |
| `E-6` | `runs/run-34fbc64712b5/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; severity medium, reproducibility deterministic |
| `E-6` | `runs/run-34fbc64712b5/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; root cause: the builder left a no-judgement flag as an unquoted placeholder. Fix: a fixed, quoted detail. No current code path reaches the non-retry form, so the `X1` failure was latent; the retry reclaim is the form written today |
| `E-6` | `runs/run-34fbc64712b5/states/fix-implementation/artifacts/implementation-report.md` | resolved; IR-2026-1020, change set `C-001` to `C-003`, deviations `V-001` (version rise) and `V-002` (version pin), and the mutation witnesses |
| `E-6` | `runs/run-34fbc64712b5/states/regression-validation/artifacts/validation-report.md` | resolved; VR-run-34fbc64712b5-regression-validation, verdict pass, 19 of 19 criteria met, one low defect `DF-001` outside the change |
| `E-6` | `runs/run-34fbc64712b5/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; disposition closed-with-followups, follow-ups `FU-001` to `FU-009` |
| `E-7` | `runs/run-34fbc64712b5/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-34fbc64712b5/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-34fbc64712b5/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-34fbc64712b5/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-34fbc64712b5/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `dev-1-bug-analyst` | completed | Executed on 2026-10-19 on the first attempt; validated 30 of 30. Reproduced the placeholder for all five classes that reach the builder, and the shell rejection | `dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-34fbc64712b5/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `dev-1-bug-analyst` | completed | Executed on 2026-10-19 on the first attempt; validated 30 of 30. Ran `verify_recovery.py` on a temporary copy only | `dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-34fbc64712b5/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `dev-1-implement` | completed | Executed on 2026-10-19 on the first attempt; validated 32 of 32. 12 new tests; 3 mutations each fail them | `dev-1-implement` subagent, dispatched by the host | `runs/run-34fbc64712b5/states/fix-implementation/validation-report.json` |
| `regression-validation` | `qa` | completed | Executed on 2026-10-19 on the first attempt; validated 31 of 31; verdict pass | `qa` subagent, dispatched by the host | `runs/run-34fbc64712b5/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `orchestrator` | completed | Executed on 2026-10-19 on the first attempt; validated 34 of 34; closed with follow-ups | `orchestrator` subagent, dispatched by the host | `runs/run-34fbc64712b5/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-34fbc64712b5` at authoring: 5 completed, 0 blocked, 0 failed, 0 pending, 29 transitions, run status Completed.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | tech-lead | tech-lead subagent a45d41e5be2175289, recorded by session operator for vuhoangcao, 2026-10-19T05:29:20Z | The literal ends `--detail <what happened>`, `release` defaults `--detail`, and `placeholders` flags it. Conditions: change only `clearing_action` (README optional), no `X1` exemption, committed run evidence untouched, builder-driven tests that cover the retry reclaim, every verifier passes |
| Fix Gate | approve | dev-2-reviewer | dev-2-reviewer subagent ab11c9038a4496337, recorded by session operator for vuhoangcao, 2026-10-19T06:39:36Z | Re-ran 89 tests on a clean clone plus the diff; two mutation witnesses re-executed and failed; `verify_recovery.py` 74/74 with `X1` passing. `V-001` is required by mandatory `FR-07`; `V-002` still asserts exact equality |
| Verification Gate | approve | dev-2-reviewer | dev-2-reviewer subagent a95f0bf7692864b39, recorded by session operator for vuhoangcao, 2026-10-19T07:15:18Z | 19 of 19 criteria met; re-ran the new module 12/12 and `verify_recovery.py` 74/74 on a fresh clone. `DF-001` is a timing race in code the diff does not touch, seen once under load and not recurring |
| Closure Gate | approve | documentation | documentation subagent a1be4c26f4e69d784, recorded by session operator for vuhoangcao, 2026-10-19T07:22:53Z | All three fix-bug exit criteria met; validator 34/34; this proposal and the merge order follow closure |

Producer exclusion held at every gate. No gate was decided by the agent that produced the evidence it assesses. The Fix and Verification Gates were decided by separate dev-2-reviewer dispatches.

## Verification

| Check | Command | Result |
|---|---|---|
| New test module | `python -m unittest tests.test_release_clearing_action -v` | pass; 12 of 12, re-run at the Fix and Verification Gates |
| Related modules | `python -m unittest tests.test_release_clearing_action tests.test_clearing_action_admissibility tests.test_knowledge tests.test_gate_rollback` | pass; re-run by the operator at authoring, see the release checklist |
| Mutation witnesses | inspection of `runs/run-34fbc64712b5/states/fix-implementation/artifacts/implementation-report.md` | old text restored: 7 of 12 tests fail; placeholder quoted: 18 subtest failures; unquoted bracket-free text: 1 failure. Two re-executed at the Fix Gate |
| Shells | `bash -n` on the emitted action; PowerShell parser; cmd.exe | exit 0, 0 parse errors, exit 0; on the unfixed tree exit 2, a redirection error, and a syntax error |
| End-to-end | the unedited emitted action against an item the recovery controller blocked, on a temporary copy | exit 0; the item moves blocked to pending and the fixed detail is recorded |
| Recovery | `python .claude/runtime/verify_recovery.py` on a temporary copy | pass; 74/74 RECOVERY PROVEN, `X1` passing |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py` on a temporary copy | pass; 15/15 PROVEN |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, re-run at authoring |
| Validators | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED, re-run at authoring |
| Manifests | `python .claude/runtime/verify_manifests.py` | pass; 2/2 CONFORMS, re-run at authoring |
| Committed evidence | `python .claude/runtime/verify_vertical_slice.py` | pass; 10/10 PROVEN, re-run at authoring |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | pass; 8/8, re-run at authoring |
| Full suite | `python tools/run_tests_parallel.py` on a temporary copy | the only failures are the 3 known `test_demo_capture` ffmpeg cases, which fail identically without the fix |
| Run evidence untouched | `git status --short .claude/runs` | only `run-34fbc64712b5` and its input are new; no committed run changed |

## Risk and Rollback

- Blast radius: the text of one clearing action. No state transition, `release` semantics or verifier rule changes. A future envelope records the fixed detail instead of the placeholder, and a `release` executed from it records that detail in its transition.
- Risk assessment: low. The verifiers and the full suite give the same results with and without the fix, apart from the new tests. This change depends on `verify_recovery.placeholders`, which the `FC-027` change adds; the new test module imports it.
- Rollback procedure: revert the `clearing_action` lines and `RUNTIME_VERSION` in `runtime/framework_runtime.py`, delete `tests/test_release_clearing_action.py`, and restore the pin in `tests/test_knowledge.py`. With the `FC-027` verifier in place, any open envelope carrying the restored action then fails `X1`.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | `python .claude/runtime/verify_validators.py`: 6/6; no validator changed |
| `FR-03` | Recovery behaviour | pass | 74/74 RECOVERY PROVEN on a temporary copy; `X1` accepts the emitted action |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py`: 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | pass | `S6` accepts this proposal and `S7` passes for `run-34fbc64712b5`; `S8` does not list it |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-34fbc64712b5` is a `/bugfix` run over `fix-bug`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | 0.10.0 to 0.10.1; the emitted clearing action changed. A patch rise, because no capability was added |
| `FR-08` | Documentation matches delivered behaviour | pass | No document describes the emitted detail text. The README synopsis shows the operator's own `--detail` as a quoted placeholder, which stays valid usage (`O-004`) |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim cites a run artifact or a command re-run at authoring. The latent reachability, the reclaim no-op, `DF-001` and the single-host evidence are disclosed |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 on a temporary copy |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | The clearing-action text an operator reads changed; this proposal and the change's description are its note |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Merge order: this change builds on the `FC-027` `X1` repair (run `run-ca5b47a3f8b7`), whose `placeholders` function the new tests import. It lands with or after that change (`FU-002`) | session operator | Open until merge |
| `O-002` | No current code path reaches the non-retry, non-guard `release` branch; decide whether it is meant to be reachable (`FU-007`) | architect | Open |
| `O-003` | The retry reclaim now parses, but `release` on a `retrying` item reports nothing to reclaim and leaves it unchanged (`FU-003`) | architect | Open |
| `O-004` | The `runtime/README.md` synopsis still shows `--detail "<what happened>"` (`FU-004`) | documentation | Open; optional under the Triage Gate |
| `O-005` | `DF-001`: a `verify_recovery.py` crash in `wait_for_backoff` (`available_at` None), seen once under heavy load and not reproduced; owed its own fix-bug run (`FU-005`) | qa | Open; not caused by this change |
| `O-006` | The host's agent adapter and this run's gate records still name the retired agent identifiers; the dispatched agents loaded the current registrations (`FU-006`) | architect | Open |
| `O-007` | Behaviour was confirmed on one Windows host only (`FU-008`) | qa | Open until CI runs |
| `O-008` | The knowledge harvest rewrote `memory/lessons/lessons.store.json` in the working tree with lessons from earlier committed runs. This change does not commit it, as `FC-027` did not; the run's harvest record names that store digest | architect | Open |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: tech-lead at the Triage Gate, dev-2-reviewer at the Fix and Verification Gates, and documentation at the Closure Gate, on 2026-10-19. Each was an independently dispatched subagent, recorded by the session operator for vuhoangcao
- Acceptance basis: every phase of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; the completion package aggregated; the new tests witnessed by failing mutations; every open item has an owner
