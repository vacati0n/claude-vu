# Framework Change Proposal: Reject every placeholder form in the `X1` clearing-action check (run-ca5b47a3f8b7)

```yaml
frameworkChangeProposal:
  proposalId: FC-027
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-ca5b47a3f8b7
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-027
- Change title: Reject every placeholder form in the `X1` clearing-action check (run-ca5b47a3f8b7)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-ca5b47a3f8b7
- Authored on: 2026-10-19

## Authoring Baseline

- Authored at: 2026-10-19T03:30:00Z
- Runtime version: 0.10.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: close a gap an independent review found after the `X1` policy-exception repair (`FC-024`, `FC-025`). `verify_recovery.py` recognised a placeholder only when `shlex` left it as one argument that starts with `<` and ends with `>`. A placeholder of several words, such as `<fill in owner name>`, splits into `<fill`, `in`, `owner` and `name>`, so a `release` clearing action carrying it was judged admissible. The same gap let glued (`x<who>`, `<who>x`) and unterminated (`<who`) forms through, in both `clearing_action_admissible` and `executable`.
- In scope: `runtime/verify_recovery.py`, which gets one shared helper, `placeholders`, used by both `clearing_action_admissible` and `executable`. A span from the argument that opens `<` to the one that closes it is one placeholder, an unterminated `<` runs to the end, and any argument carrying a bracket belongs to one. Only a placeholder that is exactly one whole argument directly after a flag the row exempts stays exempt. Also `tests/test_clearing_action_admissibility.py`, which gains `PlaceholderFormTestCase` with 7 cases (the module goes from 23 to 30). The run `run-ca5b47a3f8b7` over `fix-bug` and its supplied input are carried with it.
- Out of scope: the runtime's clearing-action builder. `framework_runtime.py` `clearing_action` still emits `release ... --detail <what happened>` for an item blocked `awaiting_recovery_task` (`O-002`). The Triage Gate kept the builder unchanged and refused a `--detail` exemption. Also out of scope: any change to run evidence already committed under `runs/`.
- Acceptance basis: the run planned through the framework by the routed command; every phase of the routed workflow executed by a host-dispatched subagent and accepted by its registered validator; all four gates approved with producer exclusion held. Every committed failure envelope keeps its admissible or inadmissible verdict, and the new tests fail against the previous detection.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/verify_recovery.py` | `SR-1` | in-scope | The defect and its fix: the shared `placeholders` helper (`C-001` of the implementation report) |
| `tests/test_clearing_action_admissibility.py` | no rule | out-of-scope | Outside the framework surface; `PlaceholderFormTestCase`, the regression cases (`C-002`) |
| `.claude/runs/run-ca5b47a3f8b7/states/fix-implementation/artifacts/implementation-report.md` | `SR-3` | out-of-scope | Run evidence written during the run |
| `.claude/runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-027.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. `X1` declares that every open envelope names an action admissible for its work item, and it judged an action carrying a multi-word placeholder admissible although that action cannot be run as written.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` returns `SR-1` for `verify_recovery.py`, no rule for the test module, `SR-3` for the run evidence and the input, and `SR-5` for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-ca5b47a3f8b7/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug` 1.0.0, submitted 2026-10-18T11:29:04Z at runtime 0.10.0, input `defect-report` with digest `sha256:aee763c105fb957aa177c2ed4e1298a9` |
| `E-2` | `runs/run-ca5b47a3f8b7/run-ledger.json` | resolved; 5 phases, run status Completed |
| `E-3` | `runs/run-ca5b47a3f8b7/events.jsonl` | resolved; 56 events, from `run_initialized` to `run_completed` at 2026-10-19T03:04:11Z |
| `E-4` | `runs/run-ca5b47a3f8b7/state.json` | resolved; 5 phases completed, 4 gates approved, 29 transitions |
| `E-5` | `runs/run-ca5b47a3f8b7/completion-package.md` | resolved; aggregated over 5 completed phases |
| `E-6` | `runs/run-ca5b47a3f8b7/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; severity medium, reproducibility deterministic; found that the builder itself emits `--detail <what happened>` |
| `E-6` | `runs/run-ca5b47a3f8b7/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; root cause: placeholders are unquoted free text, but both guards recognised only one that survives `shlex` as a single bracketed argument; the Validation Plan names each regression test |
| `E-6` | `runs/run-ca5b47a3f8b7/states/fix-implementation/artifacts/implementation-report.md` | resolved; `C-001` and `C-002`, tests `T-001` to `T-009`, deviation `V-001`, residual risks `R-001` to `R-003`, 5 mutations each caught |
| `E-6` | `runs/run-ca5b47a3f8b7/states/regression-validation/artifacts/validation-report.md` | resolved; verdict pass, 15 of 15 criteria met, 1 low defect (`DF-001`) |
| `E-6` | `runs/run-ca5b47a3f8b7/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; disposition closed-with-followups, follow-ups `FU-001` to `FU-006` |
| `E-7` | `runs/run-ca5b47a3f8b7/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-ca5b47a3f8b7/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-ca5b47a3f8b7/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-ca5b47a3f8b7/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-ca5b47a3f8b7/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed on 2026-10-18 on the first attempt; validated 30 of 30. Reproduced the defect and took a per-envelope verdict baseline of every committed envelope | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-ca5b47a3f8b7/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed on 2026-10-18 on the first attempt; validated 30 of 30. Ran the corrected detection on an isolated copy: 74/74, no verdict flips | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-ca5b47a3f8b7/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed on 2026-10-18 on the first attempt; validated 32 of 32. Changed `verify_recovery.py` and the admissibility test module only; all 5 mutations fail the tests | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-ca5b47a3f8b7/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed on 2026-10-18 on the first attempt; validated 31 of 31; verdict pass | `omn-qa` subagent, dispatched by the host | `runs/run-ca5b47a3f8b7/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed on 2026-10-18 on the first attempt; validated 34 of 34; closed with follow-ups | `omn-orchestrator` subagent, dispatched by the host | `runs/run-ca5b47a3f8b7/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-ca5b47a3f8b7` at authoring: 5 completed, 0 blocked, 0 failed, 0 pending, 29 transitions, run status Completed.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | tech-lead | omn-tech-lead subagent ab7cd2ae690ee7e28, recorded by session operator for vuhoangcao, 2026-10-18T11:41:41Z | Deterministic reproduction re-run. Scope: only the shared detection in `verify_recovery.py` and its tests; no `--detail` exemption. Conditions: the builder's `--detail <what happened>` is an open follow-up; tests pin every placeholder form and keep every exemption; every committed envelope keeps its verdict, else stop |
| Fix Gate | approve | dev-2-reviewer | omn-dev-2-reviewer subagent ab5642b9eba077228, recorded by session operator for vuhoangcao, 2026-10-18T12:23:44Z | Re-run 30/30 unit tests and `verify_recovery.py` 74/74 on a copy; no baseline envelope flips; own mutation caught. Low findings carried: lone `>` and two bracket pairs after an exempt flag unpinned (F-1, F-2); literal bracket text now refused (F-3) |
| Verification Gate | approve | dev-2-reviewer | omn-dev-2-reviewer subagent ab5642b9eba077228, recorded by session operator for vuhoangcao, 2026-10-18T12:48:03Z | QA 15 of 15 met, validator 31/31, 1 low defect; reproduction no longer fires; fix-bug exit criteria hold |
| Closure Gate | approve | documentation | omn-documentation subagent ae9ddaf613cce9165, recorded by session operator for vuhoangcao, 2026-10-19T03:04:11Z | Exit criteria met; closed-with-followups, `FU-001` to `FU-006` owned and open; no documentation of the `X1` placeholder detection is stale |

Producer exclusion held at every gate. No gate was decided by the agent that produced the evidence it assesses.

## Verification

| Check | Command | Result |
|---|---|---|
| Reproduction | host probe calling `clearing_action_admissible` on a leased item | `<fill in owner name>` and `<owner>` inadmissible; `tool_failure` admissible. Before the fix the first was admissible |
| Admissibility and policy-exception tests | `python -m unittest tests.test_clearing_action_admissibility tests.test_policy_exception_command` | pass; 32 of 32 (30 admissibility, 2 end-to-end), re-run by the operator at authoring |
| Mutation witnesses | inspection of `runs/run-ca5b47a3f8b7/states/fix-implementation/artifacts/implementation-report.md` | 5 mutations, each failing the new tests; the previous detection fails 5 of the new test methods (8 assertions per QA) |
| Committed envelope verdicts | per-envelope scan of every `runs/*/recovery-ledger.json` through `clearing_action_admissible`, before and after | 247 baseline envelopes, 17 open; no admissible or inadmissible verdict flips. Only the two resolved `run-4c51600606df` envelopes change their reason, to `'<what happened>'`; both were and stay inadmissible |
| Recovery | `python .claude/runtime/verify_recovery.py` | pass; 74/74 RECOVERY PROVEN on a temporary copy of the tree, re-run at authoring; `X1` passes over 9 open envelopes across 4 runs |
| Full suite | `python tools/run_tests_parallel.py` | 574 of 574 tests ran on a temporary copy, re-run at authoring; the only failures are the 5 that fail identically without this change (3 `test_demo_capture` ffmpeg cases, 2 `test_knowledge` cases), plus one transient Windows `os.replace` access-denied error in `test_gate_rollback` setup that passed 34 of 34 on an immediate re-run |
| Run evidence untouched | `git status --short .claude/runs` | only this run's directory and its input are new |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, re-run at authoring |
| Validators | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED, re-run at authoring |
| Manifests | `python .claude/runtime/verify_manifests.py` | pass; 2/2 CONFORMS, re-run at authoring |
| Committed evidence | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, re-run at authoring |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN on a temporary copy of the tree |
| Self-hosting | `python .claude/runtime/verify_self_hosting.py --release-checklist` | pass; 9/9 SELF-HOSTING with this proposal present, `S8` lists no unaccounted run. Its in-place multi-phase step rewrote committed `run-c5a8d50d3238` files, which were restored from version control (`O-007`) |

## Risk and Rollback

- Blast radius: the recovery verifier's placeholder detection and one test module. No runtime behaviour changes and no run executes differently; `RUNTIME_VERSION` is unchanged.
- Risk assessment: low. The detection is stricter, so the failure mode is a false refusal, not a false admission. Quoted text that legitimately contains `<` or `>`, such as `--detail 'retry count > 3'`, is now judged a placeholder (`DF-001`, `O-001`); no committed or induced envelope carries such text. The runtime builder still emits `--detail <what happened>` on one release path; `X1` now refuses that action if an induced run ever leaves it open (`O-002`).
- Rollback procedure: revert the `placeholders` helper and its two call sites in `verify_recovery.py`, and remove `PlaceholderFormTestCase` from `tests/test_clearing_action_admissibility.py`. No committed evidence depends on the change, so reverting invalidates nothing beyond this run's claim that the defect is fixed.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | `python .claude/runtime/verify_validators.py`: 6/6; no validator changed |
| `FR-03` | Recovery behaviour | pass | `verify_recovery.py` 74/74 RECOVERY PROVEN; `X1` passes with the stricter detection |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN; no committed envelope changes its verdict |
| `FR-05` | Self-hosting governance resolves | pass | `S6` accepts this proposal and `S7` passes for `run-ca5b47a3f8b7`; `S8` does not list it |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-ca5b47a3f8b7` is a `/bugfix` run over `fix-bug`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Unchanged at 0.10.0; only the verifier and tests changed |
| `FR-08` | Documentation matches delivered behaviour | pass | No document describes the `X1` placeholder detection; the Closure Gate found nothing stale |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim cites a run artifact or a command re-run at authoring. The builder action, the literal-bracket refusal, the unpinned edges, the pre-existing suite failures and the unobserved CI are disclosed |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 on a temporary copy |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | No consumer-visible behaviour changed; only the verifier is stricter |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Quoted argument text containing a literal `<` or `>` is now refused (`DF-001`, `FU-004`, risk `R-003`). Decide whether such text should stay admissible | architect | Open |
| `O-002` | The runtime builder `clearing_action` emits `release ... --detail <what happened>` for an item blocked `awaiting_recovery_task`. A shell cannot run it as written and `X1` now refuses it; fill or drop `--detail` in the builder (`FU-005`, risk `R-001`) | architect | Open |
| `O-003` | Unpinned edges: a lone `>` argument, and two bracket pairs after an exempt flag; both behave correctly but no test pins them (`FU-006`) | dev-1-implement | Open |
| `O-004` | Five suite failures that predate this change: 3 `test_demo_capture` ffmpeg cases and 2 `test_knowledge` cases (`FU-001`, risk `R-002`) | tech-lead | Open; not caused by this change |
| `O-005` | Observed on one Windows host only; observe the CI unit and recovery-verifier jobs on the default branch (`FU-003`) | omn-qa | Open |
| `O-006` | The change proposal and commit for this run (`FU-002`) | session operator | Closed by this proposal |
| `O-007` | `verify_self_hosting.py --release-checklist` rewrites committed `runs/run-c5a8d50d3238/state.json` and `task-context.yaml` in place; run it on a copy, or make that step write a copy | omn-qa | Open; not caused by this change |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates, and omn-documentation at the Closure Gate, on 2026-10-18 and 2026-10-19. Each was an independently dispatched subagent, recorded by the session operator for vuhoangcao
- Acceptance basis: every phase of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; the completion package aggregated; every new guard witnessed by a failing mutation; no committed envelope's verdict changed; every open item has an owner
