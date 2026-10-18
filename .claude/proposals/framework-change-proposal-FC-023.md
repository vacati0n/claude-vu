# Framework Change Proposal: Account for the demonstration-capture run (`/implement --demo`, run-5df08e171670), delivered outside its run and held at the Review Gate

```yaml
frameworkChangeProposal:
  proposalId: FC-023
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-5df08e171670
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
```

## Metadata

- Proposal identifier: FC-023
- Change title: Account for the demonstration-capture run (`/implement --demo`, run-5df08e171670), delivered outside its run and held at the Review Gate
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-5df08e171670
- Authored on: 2026-10-17

## Authoring Baseline

- Authored at: 2026-10-17T13:20:00Z
- Runtime version: 0.10.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

The run was planned at runtime 0.8.0 (`runs/run-5df08e171670/state.json`); its last two phases were dispatched and completed on 2026-10-17 at runtime 0.10.0, which `run-ledger.json` now records. This proposal does not move `RUNTIME_VERSION`; see `FR-07`.

## Change Statement

- Objective: give `run-5df08e171670` the governance record the profile requires, so that `S8` of `runtime/verify_self_hosting.py` no longer finds a framework run inside the self-hosted window that no proposal accounts for. The run was submitted on 2026-09-14 through `/implement` over `implement-feature` to carry the `/implement --demo` demonstration-capture capability (`runs/inputs/demo-mode-feature-request.md`). Its first three phases executed and their gates were approved on 2026-09-14; it then stalled with `implementation` ready and never dispatched. The capability itself landed in the repository outside the run, in commit 2e9e99e of 2026-09-26 ("add new version", 531 files, most of them unrelated). FC-017 to FC-022 each recorded the resulting `S8` failure as pre-existing and open (FC-017 open item 005, FC-018 open item 004, FC-019 open item 005, FC-020 open item 009, FC-021 open item 010, FC-022 open item 015), noting that only a record of the change itself could close it. The profile names no route other than a proposal whose run passes the Completion Rule (`S7`, `S8`; `## Completion Rule`), and it makes no exception for a run whose change landed out of band (`## Bootstrap Exception` applies to no later change). This proposal therefore resumes the run through the runtime instead of authoring around it. On 2026-10-17 `implementation` and `quality-review` were dispatched to their registered owners, which recorded the code as delivered rather than writing it. Each was accepted by its registered validator. The run was aggregated. The independent review rejects the delivered change, so the run is held at the Review Gate, and this record reports it that way.
- In scope: the record of the demonstration-capture capability as committed in 2e9e99e (`runtime/demo/**`, the `--demo*` options, `enable_demo`, the emit tap, the status display and the `demo` subcommand in `runtime/framework_runtime.py`, `commands/implement.md` and its registry record, and the demo test files), and the run `run-5df08e171670` over `implement-feature` carried to its current position with this governance record. No framework file is edited by this proposal.
- Out of scope: repairing any finding of the review (`O-002` to `O-005`). Deciding the Review, Verification or Closure Gate, which is the human owner's decision (`O-001`). The 477 files in 2e9e99e outside the implementation report's `C-001` to `C-054`. Every other recorded change. The `/bugfix` run `run-e7bf0d73027a` and its proposal, which carry the `verify_recovery.py` `X1` repair in the same working tree.
- Acceptance basis: the run planned through the framework by the routed command, with every phase of the routed workflow either executed by a host-dispatched subagent and accepted by its registered validator, or blocked with the reason the runtime recorded; the aggregated completion package; producer exclusion held at every decided gate; the review's reject verdict reported as returned, with every critical and high finding carried as an open item with an owner. Status is `provisional` because the Review, Verification and Closure Gates are undecided.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/demo/__init__.py` | `SR-1` | in-scope | Demo package entry: enable, emit tap, autobuild claim (delivered in 2e9e99e) |
| `.claude/runtime/demo/editor.py` | `SR-1` | in-scope | Cuts the recording against the marker stream; site of review `F-001` and `F-003` |
| `.claude/runtime/demo/capture_helper.py` | `SR-1` | in-scope | Window occlusion sampling; site of review `F-002` |
| `.claude/runtime/demo/narration.py` | `SR-1` | in-scope | Narration engines; site of review `F-004` and `F-009` |
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | `--demo*` options, `enable_demo`, emit tap, status display, `demo` subcommand; site of review `F-005` |
| `.claude/commands/implement.md` | `SR-1` | in-scope | The `--demo` flags on the command specification |
| `tests/test_demo_capture.py` | no rule | out-of-scope | Outside the framework surface; demo test suite |
| `omn_agent/_bundled_payload/runtime/demo/editor.py` | no rule | out-of-scope | Outside the framework surface; bundled mirror, byte-identical per the review |
| `.claude/runs/run-5df08e171670/states/implementation/artifacts/implementation-report.md` | `SR-3` | out-of-scope | Run evidence written during the resumed run |
| `.claude/runs/inputs/demo-mode-feature-request.md` | `SR-3` | out-of-scope | The supplied `feature-request` input |
| `.claude/proposals/framework-change-proposal-FC-023.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

The full list of delivered paths is the implementation report's `C-001` to `C-054` (`M-001` to `M-022` of the design). This proposal edits none of them.

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains a runtime behaviour it did not have — an opt-in recording of a governed run, compiled into a narrated demonstration film at run completion.
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request` `change-request` `business-intent` `architecture-context`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` returns `SR-1` in scope ("framework-internal change") for the framework paths above, no rule for the test file and the bundled mirror, `SR-3` for the run evidence and inputs, and `SR-5` for this proposal. `python .claude/runtime/self_hosting.py route --intent capability-addition` returns `/implement` over `implement-feature v1.0.0` at `scope-and-acceptance`, with the four inputs the run records.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-5df08e171670/execution-request.json` | resolved; routed through `/implement` over `implement-feature`, submitted 2026-09-14T07:19:57Z at runtime 0.8.0, four inputs recorded with their digests |
| `E-2` | `runs/run-5df08e171670/run-ledger.json` | resolved; 6 phases, run status WaitingForHuman |
| `E-3` | `runs/run-5df08e171670/events.jsonl` | resolved; 66 events, from `run_initialized` to the Review and Verification Gate escalations opened after `quality-review` completed |
| `E-4` | `runs/run-5df08e171670/state.json` | resolved; 5 phases completed, 1 blocked `awaiting_human_decision`, 36 transitions; Scope, Planning and Design Gates approved, Review and Verification Gates blocked awaiting a decision, Closure Gate pending |
| `E-5` | `runs/run-5df08e171670/completion-package.md` | resolved; aggregated over 5 completed phases and 1 blocked phase, three gates undecided |
| `E-6` | `runs/run-5df08e171670/states/scope-and-acceptance/artifacts/scope-definition.md` | resolved; scope and 14 acceptance criteria |
| `E-6` | `runs/run-5df08e171670/states/execution-planning/artifacts/execution-plan.md` | resolved; the execution plan |
| `E-6` | `runs/run-5df08e171670/states/solution-design-and-risk-assessment/artifacts/technical-design.md` | resolved; the technical design, with decision records `D-001` to `D-007` beside it |
| `E-6` | `runs/run-5df08e171670/states/implementation/artifacts/implementation-report.md` | resolved; the delivered code `C-001` to `C-054` mapped to the design, deviation `V-001` (committed in 2e9e99e before the phase was dispatched), risks `R-001` to `R-005` |
| `E-6` | `runs/run-5df08e171670/states/quality-review/artifacts/review-package.md` | resolved; RP-2026-0005, verdict reject, findings `F-001` to `F-010` (1 critical, 4 high, 1 medium, 4 low) |
| `E-7` | `runs/run-5df08e171670/states/scope-and-acceptance/validation-report.json` | resolved; 33 of 33 |
| `E-7` | `runs/run-5df08e171670/states/execution-planning/validation-report.json` | resolved; 45 of 45 |
| `E-7` | `runs/run-5df08e171670/states/solution-design-and-risk-assessment/validation-report.json` | resolved; 78 of 78 |
| `E-7` | `runs/run-5df08e171670/states/implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-5df08e171670/states/quality-review/validation-report.json` | resolved; 31 of 31, attempt 2 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed on 2026-09-14 on the first attempt; validated 33 of 33 | `omn-product-owner` subagent, dispatched by the host | `runs/run-5df08e171670/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed on 2026-09-14 on the first attempt; validated 45 of 45 | `planner` subagent, dispatched by the host | `runs/run-5df08e171670/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed on 2026-09-14, accepted on attempt 2; validated 78 of 78 | `architect` subagent, dispatched by the host | `runs/run-5df08e171670/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Dispatched 2026-10-17 at runtime 0.10.0, after the code had landed in 2e9e99e; the agent recorded the delivered code against the design without modifying it (`V-001`), with executed test evidence; validated 32 of 32 on the first attempt; status provisional, partially verified | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-5df08e171670/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Dispatched 2026-10-17. Attempt 1 rejected by the validator on `C6.2` (an undefined identifier `F-020`) and retried; attempt 2 validated 31 of 31. Verdict reject: 1 critical, 4 high, 1 medium, 4 low findings | `omn-dev-2-reviewer` subagent, independent of the implementer, dispatched by the host | `runs/run-5df08e171670/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | blocked | Blocked `awaiting_human_decision`: the Review Gate and the Verification Gate that close `quality-review` are undecided, so the phase is not dispatched. Not performed | not performed | `runs/run-5df08e171670/state.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-5df08e171670` at authoring: 5 completed, 1 blocked, 0 failed, 0 pending, 36 transitions, run status WaitingForHuman.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | omn-business-analyst subagent a3511899e4038408d, recorded by the session operator for vuhoangcao, 2026-09-14T07:30:34Z | Every deliverable, criterion and constraint traces onto a scope item or a named exclusion; the one contradiction is resolved by `D-002`; all 14 criteria name the scope item they bound and how they are decided |
| Planning Gate | approve | omn-tech-lead | omn-tech-lead subagent a6c306330530bf26c, recorded by the session operator for vuhoangcao, 2026-09-14T07:50:33Z | The breakdown covers all eleven in-scope rows and fourteen criteria without adding a deliverable; the dependency graph is acyclic and its waves recompute as stated |
| Design Gate | approve | omn-tech-lead | omn-tech-lead subagent a307c9acb773c30c5, recorded by the session operator for vuhoangcao, 2026-09-14T08:22:20Z | Sound, proportionate and executable design; six options scored against fixed criteria; every risk carries a trigger, an owner and a checkpoint |
| Review Gate | undecided | omn-qa | not decided | Blocked `awaiting_human_decision`. The review it assesses returns reject. Approving it would contradict the evidence, and rejecting it opens a rollback that only a human authoriser can direct (`O-001`) |
| Verification Gate | undecided | omn-qa | not decided | Blocked `awaiting_human_decision`, as above |
| Closure Gate | undecided | omn-orchestrator | not decided | Pending; its phase has not run |

Producer exclusion held at every decided gate. No gate was decided in the resumed part of the run.

## Verification

| Check | Command | Result |
|---|---|---|
| Demo test suites | `python tools/run_tests_parallel.py` | Per the implementation report and the review: the demo suites pass except the 3 `EndToEndEditTestCase` tests in `tests/test_demo_capture.py`, which fail because the installed ffmpeg 9.0.2 rejects `-filter_complex_script` (review `F-003`, FC-020 open item 005). The rest of the full suite passes |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, 37 of 37 phases dispatchable (re-run while authoring) |
| Recovery | `python .claude/runtime/verify_recovery.py` | 73/74 at authoring, `X1` pre-existing; its repair is carried by `run-e7bf0d73027a` under its own proposal, see `FR-03` |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | Before this proposal, `S7` passed and `S8` listed `run-5df08e171670` and `run-e7bf0d73027a`; with this proposal `run-5df08e171670` is accounted for, see `FR-05` |
| Delivered code against the design | inspection of `runs/run-5df08e171670/states/implementation/artifacts/implementation-report.md` | `C-001` to `C-054` mapped to `M-001` to `M-022`; deviations `V-001` to `V-006` recorded, among them `V-001` (committed before the phase ran) and `V-006` (the commit mixes 477 unrelated files) |
| Independent review | inspection of `runs/run-5df08e171670/states/quality-review/artifacts/review-package.md` | Reject. `F-001` critical: `rebalance_spans` widens a span with no occlusion check, so footage of another window can be published. `F-002` high: occlusions shorter than 0.4 s are discarded. `F-003` high: the filmed build fails on the installed encoder. `F-004` high: the default narration engine sends text off the host without opt-in. `F-005` high: `enable_demo` faults are not absorbed |

## Risk and Rollback

- Blast radius: no file is changed by this proposal; it adds run evidence under `runs/run-5df08e171670/` and this record. The capability it records spans `C-001` to `C-054`, opt-in behind `--demo`. Without the flag the demo package is never imported, per the design and the implementation report.
- Risk assessment: the review's unmitigated risks stand until the open items close. Until `F-001` and `F-002` are repaired, a film built under the default pace may contain footage of a window other than the target. Until `F-004` is repaired, narration text may leave the host. Neither affects a run without `--demo`. Recording the run without deciding its gates leaves it `WaitingForHuman`, which is its true state.
- Rollback procedure: delete this proposal and restore `runs/run-5df08e171670/` to its prior commit with `git checkout <base> -- .claude/runs/run-5df08e171670`, removing its `states/implementation/` and `states/quality-review/` directories. `S8` then fails on this run again. Reverting the capability itself is a path-scoped revert of `C-001` to `C-054` (implementation report `R-005`), never a revert of 2e9e99e, and is outside this record.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | `python .claude/runtime/verify_validators.py` from the repository root; no validator changed by this record |
| `FR-03` | Recovery behaviour | pass | 74/74 with the `X1` repair carried in the same working tree by `run-e7bf0d73027a`; 73/74 without it. This record changes no recovery behaviour |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`; no committed proof edited |
| `FR-05` | Self-hosting governance resolves | pass | `S6` accepts this proposal, `S7` passes for `run-5df08e171670`, and `S8` no longer lists it |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-5df08e171670` is an `/implement` run over `implement-feature`; this proposal links its artifacts. The code landed outside the run, which `V-001` and this record state |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Unchanged at 0.10.0; this record changes no runtime behaviour |
| `FR-08` | Documentation matches delivered behaviour | pass | No documentation changed. The documentation phase did not run (blocked); `commands/implement.md` already describes the `--demo` flags (review: all ten flags agree across parser, command spec and registry) |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim cites a run artifact; the reject verdict, the out-of-band delivery, the undecided gates and the encoder failure are disclosed |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | `verify_multi_phase.py --run-id run-c5a8d50d3238`; unaffected |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | Consumer-visible behaviour is unchanged by this record; the release handoff of the capability is the blocked documentation phase |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The Review and Verification Gates of `run-5df08e171670` are blocked `awaiting_human_decision` over a reject verdict, and the Closure Gate is pending. A human decides whether to reject and authorise a rollback of `implementation`, or to open repair work first | omn-qa | Open. The run stays `WaitingForHuman` |
| `O-002` | Review `F-001` (critical) and `F-002` (high): publication safety. Footage recorded while another window covered the target can be published | omn-tech-lead | Open; route as a `defect-repair` through `/bugfix` |
| `O-003` | Review `F-003` (high): `-filter_complex_script` is rejected by ffmpeg 9.0.2, so every filmed build falls back; this is the cause of the 3 `test_demo_capture` failures (FC-020 open item 005, FC-021 open item 011) | omn-tech-lead | Open; route as a `defect-repair` |
| `O-004` | Review `F-004` (high): the `auto` narration engine sends narration text to a network service with no opt-in or threat review | omn-tech-lead | Open; route as a `defect-repair` |
| `O-005` | Review `F-005` (high), `F-006` to `F-010`: unabsorbed faults at `enable_demo`, missing negative-path tests, duplicate-build claim on error, a stale docstring, unescaped shell interpolation, tracked bytecode | omn-tech-lead | Open |
| `O-006` | The `S8` failure recorded as pre-existing by FC-017 open item 005, FC-018 open item 004, FC-019 open item 005, FC-020 open item 009, FC-021 open item 010 and FC-022 open item 015 | omn-orchestrator | Closed by this proposal: `run-5df08e171670` is accounted for |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-business-analyst at the Scope Gate and omn-tech-lead at the Planning and Design Gates, on 2026-09-14, each an independently dispatched subagent recorded by the session operator. The Review, Verification and Closure Gates are undecided, so the change is not accepted, and this record is provisional
- Acceptance basis: every phase of the routed workflow accounted for: five executed by host-dispatched subagents and accepted by their registered validators, one blocked with its recorded reason; the completion package aggregated; the reject verdict and its findings carried as open items with owners; the out-of-band delivery in 2e9e99e disclosed rather than concealed
