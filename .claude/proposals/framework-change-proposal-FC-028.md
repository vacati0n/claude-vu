# Framework Change Proposal: Run the release checklist and the M14 replay in disposable copies so committed run evidence is never rewritten (run-2cf7a34e3daa)

```yaml
frameworkChangeProposal:
  proposalId: FC-028
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-2cf7a34e3daa
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-028
- Change title: Run the release checklist and the M14 replay in disposable copies so committed run evidence is never rewritten (run-2cf7a34e3daa)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-2cf7a34e3daa
- Authored on: 2026-10-19

## Authoring Baseline

- Authored at: 2026-10-19T04:19:07Z
- Runtime version: 0.10.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: make `python .claude/runtime/verify_self_hosting.py --release-checklist`, the step every framework change must pass, leave the working tree exactly as it found it. On a clean checkout it rewrote committed `runs/run-c5a8d50d3238/state.json` and `task-context.yaml`, so contributors ran it on a temporary copy of the tree to avoid committing or reverting changes to past run evidence. The root-cause analysis traced the writes to one place: `verify_multi_phase.py` check `M14` re-executed `plan`, `dispatch` and `complete` against the committed run in place. The runtime's replay path saves bookkeeping by design (refreshed stamps, re-rendered guard details, appended replay records, a rebuilt `task-context.yaml`), and `M14`'s fingerprint leaves that bookkeeping out, so `M14` passed while the files changed. The checklist runner executed each item at the repository root and judged it by exit code only, and `FR-11` is advisory, so nothing caught it. `verify_recovery.py` removed its injected runs only at the end of `main()`, so a raising scenario left them under `runs/`.
- In scope: `runtime/verify_self_hosting.py`. `--release-checklist` runs every command item in its own disposable copy of the working tree, as git sees it (tracked plus untracked, not ignored), so uncommitted work is verified as it stands. A new check `S11` compares the content digest of every file git lists before and after the checklist, and fails if any item changed a file in the repository or inside its own copy. `S10` is decided as before. `runtime/verify_multi_phase.py`: `M14` replays in a disposable copy that leaves out other run directories, runs the copied runtime with the copy as its root, fingerprints the copy, names the bookkeeping files the replay rewrote there, and removes the copy in a `finally` block. `runtime/verify_recovery.py`: injected-run cleanup moves into `finally`. `runtime/README.md` and `validation/framework-release-checklist.md` describe the new behaviour. Two test modules are added: `tests/test_release_checklist_clean_tree.py` (4 cases) runs the whole checklist and asserts that `git status` and every listed file are unchanged and that `S11` passed. `tests/test_verifier_isolation.py` (5 cases) covers `M14` leaving the committed run byte-identical, `M14` still failing on a duplicated transition and on a rewritten artifact, the copy being removed when a replay command raises, and recovery cleanup when a scenario raises.
- Out of scope: `framework_runtime.py` and `state_engine.py`. Making the runtime's replay path write-free stays with the architect. The 253 replay records already committed in `run-c5a8d50d3238` are not rewritten or re-baselined. The Windows `os.replace` save failure seen during triage is to be routed as its own defect.
- Acceptance basis: the run was planned through the framework by the routed command. Every phase of the routed workflow was executed by a host-dispatched subagent and accepted by its registered validator. All four gates were approved with producer exclusion held. QA re-ran the full checklist and every verifier in place and found the tree byte-identical, and a pre-fix control on `HEAD` reproduced the rewrite.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/verify_self_hosting.py` | `SR-1` | in-scope | Per-item disposable copies and check `S11` |
| `.claude/runtime/verify_multi_phase.py` | `SR-1` | in-scope | `M14` replays in a disposable copy and fingerprints it |
| `.claude/runtime/verify_recovery.py` | `SR-1` | in-scope | Injected-run cleanup in `finally` |
| `.claude/runtime/README.md` | `SR-1` | in-scope | Documentation of `M14` and `S11`, including the Closure Gate's wording corrections |
| `.claude/validation/framework-release-checklist.md` | `SR-1` | in-scope | One paragraph after the `FR-11` note; no item identifier or obligation changed |
| `.claude/memory/lessons/lessons.store.json` | `SR-1` | in-scope | Written by the runtime's lesson harvest when this run's phases completed, not edited by hand |
| `tests/test_release_checklist_clean_tree.py` | no rule | out-of-scope | Outside the framework surface; the clean-tree regression test |
| `tests/test_verifier_isolation.py` | no rule | out-of-scope | Outside the framework surface; `M14` and recovery isolation tests |
| `.claude/runs/run-2cf7a34e3daa/state.json` | `SR-3` | out-of-scope | Run evidence written during the run |
| `.claude/runs/inputs/release-checklist-mutates-committed-runs-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-028.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The release checklist and `M14` claim to verify without side effects, and both rewrote committed run evidence.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` returns `SR-1` for the three verifiers, the runtime README, the release checklist and the lesson store, no rule for both test modules, `SR-3` for the run evidence and the input, and `SR-5` for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-2cf7a34e3daa/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug` 1.0.0, submitted 2026-10-18T11:32:42Z at runtime 0.10.0, input `defect-report` with digest `sha256:1baebc70bf310ad1b1104d5370b40dac` |
| `E-2` | `runs/run-2cf7a34e3daa/run-ledger.json` | resolved; 5 phases, run status Completed |
| `E-3` | `runs/run-2cf7a34e3daa/events.jsonl` | resolved; 56 events, from `run_initialized` to `run_completed` at 2026-10-19T04:18:24Z |
| `E-4` | `runs/run-2cf7a34e3daa/state.json` | resolved; 5 phases completed, 4 gates approved, 29 transitions |
| `E-5` | `runs/run-2cf7a34e3daa/completion-package.md` | resolved; aggregated over 5 completed phases |
| `E-6` | `runs/run-2cf7a34e3daa/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; severity medium, reproducibility deterministic; cause pinned on `M14` with a `--no-replay` control |
| `E-6` | `runs/run-2cf7a34e3daa/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; no checklist item other than `FR-11` writes; recovery cleanup outside `finally` confirmed; amended fix strategy and Validation Plan |
| `E-6` | `runs/run-2cf7a34e3daa/states/fix-implementation/artifacts/implementation-report.md` | resolved; IR-2026-1019, deviations V-001 to V-005 |
| `E-6` | `runs/run-2cf7a34e3daa/states/regression-validation/artifacts/validation-report.md` | resolved; VR-run-2cf7a34e3daa-regression-validation, verdict pass, 3 of 3 criteria met, no defects |
| `E-6` | `runs/run-2cf7a34e3daa/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; disposition closed-with-followups, follow-ups `FU-001` to `FU-010` |
| `E-7` | `runs/run-2cf7a34e3daa/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-2cf7a34e3daa/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-2cf7a34e3daa/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-2cf7a34e3daa/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-2cf7a34e3daa/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `dev-1-bug-analyst` | completed | Executed on 2026-10-18 on the first attempt; validated 30 of 30 | `dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-2cf7a34e3daa/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `dev-1-bug-analyst` | completed | Executed on 2026-10-18 on the first attempt; validated 30 of 30. Ran every checklist item in a disposable git copy to close the Triage Gate's first condition | `dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-2cf7a34e3daa/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `dev-1-implement` | completed | Executed on 2026-10-18 and 2026-10-19; validated 32 of 32. The first dispatch was interrupted after writing the code and tests and before writing its report; a second dispatch of the same attempt reviewed the code, added one missing test and wrote the report | `dev-1-implement` subagent, dispatched by the host | `runs/run-2cf7a34e3daa/states/fix-implementation/validation-report.json` |
| `regression-validation` | `qa` | completed | Executed on 2026-10-19 on the first attempt; validated 31 of 31; verdict pass | `qa` subagent, dispatched by the host | `runs/run-2cf7a34e3daa/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `orchestrator` | completed | Executed on 2026-10-19 on the first attempt; validated 34 of 34; closed with follow-ups | `orchestrator` subagent, dispatched by the host | `runs/run-2cf7a34e3daa/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-2cf7a34e3daa` at authoring: 5 completed, 0 blocked, 0 failed, 0 pending, 29 transitions, run status Completed.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | tech-lead | tech-lead subagent a02e34fe4fab1c375, recorded by session operator for vuhoangcao, 2026-10-18T11:43:16Z | DF-001 reproduced deterministically with a `--no-replay` control and traced to two source-confirmed causes. Conditions: close Q-001 first; isolate `M14` in a disposable copy removed in `finally`; copy the working tree as it is; fail the checklist on any tree difference; add regression tests; leave committed evidence and the runtime replay design untouched |
| Fix Gate | approve | dev-2-reviewer | dev-2-reviewer subagent ad05a67feccdff38f, recorded by session operator for vuhoangcao, 2026-10-19T03:41:03Z | No verifier path writes committed run evidence; 5 of 5 isolation tests and `M14` 15 of 15 re-run with the tree byte-identical. Non-blocking findings F-001 to F-004 |
| Verification Gate | approve | dev-2-reviewer | dev-2-reviewer subagent a99c3641e45ce401c, recorded by session operator for vuhoangcao, 2026-10-19T04:10:24Z | All three expected-behaviour criteria met by checks QA ran itself; spot-check re-run with every listed file digest unchanged; no open defect |
| Closure Gate | approve | documentation | documentation subagent aa64082a8e1e45450, recorded by session operator for vuhoangcao, 2026-10-19T04:18:24Z | fix-bug exit criteria met; ten follow-ups owned; documentation matches the delivered code, with three README wording corrections applied after the gate |

Producer exclusion held at every gate. No gate was decided by the agent that produced the evidence it assesses.

## Verification

| Check | Command | Result |
|---|---|---|
| Checklist leaves the tree unchanged | `python .claude/runtime/verify_self_hosting.py --release-checklist`, with `git status --porcelain --untracked-files=all` and a sha256 of every listed file before and after | pass; identical before and after; `S11` passed over every listed file and every item's `copy_writes` was empty. Re-run by the operator at authoring with this proposal present |
| Defect reproduced before the fix | inspection of `runs/run-2cf7a34e3daa/states/regression-validation/artifacts/validation-report.md` | QA ran the pre-fix `verify_multi_phase.py --run-id run-c5a8d50d3238` on an extract of `HEAD`: `M14` passed while rewriting `state.json` and `task-context.yaml` |
| New test modules | `python -m unittest tests.test_verifier_isolation tests.test_release_checklist_clean_tree -v` | pass; 9 of 9 in QA; the tree identical before and after |
| `S11` negative control | QA scratch control outside the repository | an item writing into the tree, and one writing inside its own copy, each failed `S11` while `S10` passed; not pinned by a committed test (`O-001`) |
| Full suite | `python tools/run_tests_parallel.py` | 576 tests ran; the only failures are the 3 known `test_demo_capture` `EndToEndEditTestCase` ffmpeg cases, which fail the same way at `HEAD` |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED |
| Validators | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED |
| Recovery | `python .claude/runtime/verify_recovery.py` | pass; 74/74 RECOVERY PROVEN; tree unchanged |
| Committed evidence | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN, in place, with `run-c5a8d50d3238` byte-identical afterwards |
| Manifests | `python .claude/runtime/verify_manifests.py` | pass; 2/2 |

## Risk and Rollback

- Blast radius: three verifiers and their documentation. No runtime source changes and no run executes differently. The release checklist now takes about 192 s instead of 69 s on the authoring host, because each command item copies, snapshots and removes the working tree, and the new clean-tree test repeats the checklist in both CI unit jobs (`O-002`).
- Risk assessment: low. Verdicts are unchanged: every verifier gives the same check counts as at `HEAD`. A scratch copy that cannot be removed is reported as a warning, not raised, so it cannot replace a verdict; it can leave files in the system temp directory.
- Rollback procedure: revert the three verifier files, the two documentation edits and the two test modules. That reinstates the defect: the checklist and `verify_multi_phase.py` again rewrite `run-c5a8d50d3238`. No committed evidence depends on the new behaviour, and reverting invalidates only this proposal's claim that the checklist leaves the tree unchanged.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | `python .claude/runtime/verify_validators.py`: 6/6; no validator changed |
| `FR-03` | Recovery behaviour | pass | 74/74 RECOVERY PROVEN; cleanup now runs in `finally`, proven by `tests/test_verifier_isolation.py` |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | pass | `S6` accepts this proposal, `S7` passes for `run-2cf7a34e3daa`, `S8` lists no unaccounted run, and the new `S11` passes |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-2cf7a34e3daa` is a `/bugfix` run over `fix-bug`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Unchanged at 0.10.0; only verifiers changed, and `framework_runtime.py` and `state_engine.py` are untouched |
| `FR-08` | Documentation matches delivered behaviour | pass | `runtime/README.md` rows for both verifiers and the Idempotency section, and the checklist paragraph after `FR-11`, checked at the Closure Gate and corrected as it asked |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim cites a run artifact or a command re-run at authoring. The untested `S11` failure path, single-host evidence and the CI duration are disclosed |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15, now run in place without writing the run it proves |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | The checklist's tree-integrity check `S11` is described in `runtime/README.md` and the release checklist; no consumer-facing command changed |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | No committed test proves `S11` fails when an item writes into the tree or its copy; shown only by a scratch negative control (`FU-002`, F-001) | tech-lead | Open |
| `O-002` | The checklist takes about 192 s instead of 69 s, and the clean-tree test repeats it in both CI unit jobs; decide whether it stays in default discovery (`FU-003`, F-002) | tech-lead | Open |
| `O-003` | Evidence is from one Windows host; CI and POSIX runners have not run the change (`FU-004`) | qa | Open until the PR's CI reports |
| `O-004` | `S11` compares content, so a mode-only change on a host that tracks file mode is not seen; confirm deviations V-001 and V-002 from the Triage Gate wording (`FU-005`, `FU-010`) | architect | Open |
| `O-005` | An error inside the recovery cleanup could mask the scenario's own exception (`FU-006`, F-004) | dev-1-implement | Open |
| `O-006` | Route the Windows `os.replace` save failure seen during triage as its own defect (`FU-007`) | orchestrator | Open |
| `O-007` | Keep or re-baseline the replay records already committed in `run-c5a8d50d3238` (`FU-008`) | tech-lead | Open |
| `O-008` | Author this proposal after closure and re-run the full release checklist with it present (`FU-001`) | session operator | Closed: re-run at authoring, see Verification |

## Sign-off

- Proposed by: operator, acting as orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: tech-lead at the Triage Gate, dev-2-reviewer at the Fix and Verification Gates, and documentation at the Closure Gate, on 2026-10-18 and 2026-10-19. Each was an independently dispatched subagent, recorded by the session operator for vuhoangcao
- Acceptance basis: every phase of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; the completion package aggregated; the checklist and every verifier re-run with the working tree byte-identical; every open item has an owner
