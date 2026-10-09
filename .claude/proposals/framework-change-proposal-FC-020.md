# Framework Change Proposal: Repair the investigate and research input hand-offs (agent input contracts versus Phase Model edges)

```yaml
frameworkChangeProposal:
  proposalId: FC-020
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-5d3c99aaaae1
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-020
- Change title: Repair the investigate and research input hand-offs (agent input contracts versus Phase Model edges)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-5d3c99aaaae1
- Authored on: 2026-10-09

## Authoring Baseline

- Authored at: 2026-10-09T13:27:00Z
- Runtime version: 0.9.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

## Change Statement

- Objective: repair the defect that FC-017 recorded as its open item `O-001`. In the `investigate` and `research` workflows the next phase's agent did not accept the identifier of the upstream artifact, so phases blocked at guard `G5-INPUT` and no run could complete without operator-performed work. The defect report is `runs/inputs/investigate-chain-input-contracts-defect-report.md`. Triage measured the real extent (`runs/run-5d3c99aaaae1/states/triage-and-impact/artifacts/bug-analysis.md`): across all workflows there are 29 hand-offs, 13 of them blocked at `G5-INPUT` in five workflows (investigate 3 of 4, research 3 of 4, review-pull-request 2 of 4, release 2 of 4, implement-feature 2 of 5), forming 10 distinct identifier and consumer pairs. Triage also corrected the defect report on four points: research has three gaps, not four; the scope is wider than investigate and research; the workaround of supplying `investigation-question` up front clears only one phase; and supplied inputs persist in the input pool. The root cause analysis (`runs/run-5d3c99aaaae1/states/root-cause-analysis/artifacts/bug-analysis.md`) found that each consuming agent's accepted-input list was written without reference to the Phase Model edges that feed it, and nothing checks an edge against the producer identifier and the consumer contract. The earlier repair FC-011 fixed its one edge the same way and deferred the per-edge check, because that check would have failed on arrival. The operator scoped this repair to the investigate and research chains and the two profile rows that route into them (`decision-support`, `external-research`); the hand-offs of the other workflows are follow-ups. The fix: `omn-context-agent` also accepts `requirement-framing` (additive; `framed-objective` and `research-brief` are kept, though no phase produces them); `omn-documentation` accepts `technical-recommendation`; the `recommendation` and `recommendation-draft` Input cells in `workflows/investigate.md` and `workflows/research.md` also name `investigation-report.md`, one new hard edge each, so `omn-tech-lead` needs no manifest change; the two profile rows name `problem-statement`. Both agents move to 1.1.0 across their manifest, `registry/agents.yaml` (version and data dependency) and host registration, as FC-011 did, and the investigate and research workflows move to version 1.1.0 in `registry/workflows.yaml`. The documentation contract text gains a precedence rule: the artifact from `recommendation` or `recommendation-draft` governs; the draft from `option-analysis` or `option-synthesis` is superseded and context only; with only the draft, nothing is published as a recommendation. `templates/release-note.md` and the `sourceInputs` vocabulary of `output.md` name `technical-recommendation`. `tests/test_investigate_research_handoffs.py` holds 22 regression tests, 20 original and 2 added after review; all fail on the pre-fix tree and pass after. Blocked hand-offs fall from 13 to 7, and the 7 that remain are pinned as `KNOWN_BLOCKED_EDGES`, so the list must shrink as follow-ups land. The bundled mirror was refreshed.
- In scope: the context-agent and documentation-agent contracts and registrations, the two workflow Input cells, the two workflow versions, the two profile routing rows, the two template lines, and the run `run-5d3c99aaaae1` over the `fix-bug` workflow with this governance record.
- Out of scope: the 7 remaining blocked hand-offs in `review-pull-request`, `release` and `implement-feature` (`O-001`); the other two profile rows, `change-review` and `framework-release` (`O-002`); any runtime function, so `RUNTIME_VERSION` is unchanged; the sibling changes FC-018 and FC-019, which sit in the same working tree and edit `.claude/runtime/verify_validators.py`, a file this change does not touch. The new test file and the bundled mirror are outside the framework surface.
- Acceptance basis: the routed run planned through the framework, with all five phases executed by host-dispatched subagents; every gate decided by a non-producing owner; the fix tested before and after, with the 22 new tests failing on the pre-fix tree; an independent review whose findings were closed by a correction pass before its gate; the standalone verifiers re-run and reported as they came out; and a post-repair check with real agents on a run that had been blocked by this very defect, FC-017's run, reported with its two caveats.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/agents/omn-context-agent.agent.md` | `SR-1` | in-scope | Host registration of the context agent, moved to 1.1.0 |
| `.claude/agents/omn-context-agent/manifest.yaml` | `SR-1` | in-scope | Accepted input list gains `requirement-framing`; version 1.1.0 |
| `.claude/agents/omn-context-agent/identity.md` | `SR-1` | in-scope | Contract text for the accepted inputs |
| `.claude/agents/omn-context-agent/execution.md` | `SR-1` | in-scope | Contract text for the accepted inputs |
| `.claude/agents/omn-context-agent/output.md` | `SR-1` | in-scope | Contract text for the accepted inputs |
| `.claude/agents/omn-documentation.agent.md` | `SR-1` | in-scope | Host registration of the documentation agent, moved to 1.1.0 |
| `.claude/agents/omn-documentation/manifest.yaml` | `SR-1` | in-scope | Accepted input list gains `technical-recommendation`; version 1.1.0 |
| `.claude/agents/omn-documentation/identity.md` | `SR-1` | in-scope | Contract text, including the precedence rule |
| `.claude/agents/omn-documentation/execution.md` | `SR-1` | in-scope | Contract text, including the precedence rule |
| `.claude/agents/omn-documentation/output.md` | `SR-1` | in-scope | The `sourceInputs` vocabulary names `technical-recommendation` |
| `.claude/registry/agents.yaml` | `SR-1` | in-scope | Both agent versions and the data dependency |
| `.claude/registry/workflows.yaml` | `SR-1` | in-scope | Investigate and research workflow versions 1.1.0 |
| `.claude/workflows/investigate.md` | `SR-1` | in-scope | `recommendation` Input cell also names `investigation-report.md` |
| `.claude/workflows/research.md` | `SR-1` | in-scope | `recommendation-draft` Input cell also names `investigation-report.md` |
| `.claude/config/self-hosting-profile.md` | `SR-1` | in-scope | The `decision-support` and `external-research` rows name `problem-statement` |
| `.claude/templates/investigation-report.md` | `SR-1` | in-scope | Template line aligned with the repaired hand-off |
| `.claude/templates/release-note.md` | `SR-1` | in-scope | The source-inputs line names `technical-recommendation` |
| `tests/test_investigate_research_handoffs.py` | no rule | out-of-scope | Outside the framework surface; 22 regression tests |
| `omn_agent/_bundled_payload/**` | no rule | out-of-scope | Outside the framework surface; the bundled mirror, refreshed through `python tests/test_bundled_payload.py --sync` and never hand-edited |
| `.claude/runs/run-5d3c99aaaae1/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this repair |
| `.claude/runs/inputs/investigate-chain-input-contracts-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-020.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

The scope paths were checked against `git status` and `git diff --stat`: 18 tracked framework and mirror paths are listed as modified under `.claude/`, one of which, `.claude/runtime/verify_validators.py`, belongs to FC-018 and FC-019 and is not claimed here; the remaining 17 `.claude/` paths are the rows above. The mirror rows stand for the matching 18 modified paths under `omn_agent/_bundled_payload/`, one of which mirrors that same verifier.

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The agent contracts declare that each phase consumes the artifact the Phase Model feeds it, and the consuming agents rejected the identifier of that artifact.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` was re-run over every scope path of the table above and returned `SR-1` in scope for the 17 framework paths with the verdict "framework-internal change", no rule and out of scope for the test file and the bundled mirror, `SR-3` out of scope for the run evidence and the defect report, and `SR-5` out of scope for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` of 5, with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-5d3c99aaaae1/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug`, input recorded with its digest |
| `E-2` | `runs/run-5d3c99aaaae1/run-ledger.json` | resolved; runtime 0.9.0, 5 phases, run status Completed |
| `E-3` | `runs/run-5d3c99aaaae1/events.jsonl` | resolved; 56 events from `run_initialized` to the final run completion |
| `E-4` | `runs/run-5d3c99aaaae1/state.json` | resolved; 5 phases completed, 0 blocked, 0 failed, 29 transitions |
| `E-5` | `runs/run-5d3c99aaaae1/completion-package.md` | resolved; aggregated for 5 of 5 completed phases |
| `E-6` | `runs/run-5d3c99aaaae1/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; the triage, with the measured extent of 13 blocked hand-offs of 29 |
| `E-6` | `runs/run-5d3c99aaaae1/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; the root cause analysis |
| `E-6` | `runs/run-5d3c99aaaae1/states/fix-implementation/artifacts/implementation-report.md` | resolved; the fix, its tests and its post-review correction pass |
| `E-6` | `runs/run-5d3c99aaaae1/states/regression-validation/artifacts/validation-report.md` | resolved; 8 of 8 criteria met |
| `E-6` | `runs/run-5d3c99aaaae1/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; the closure record |
| `E-7` | `runs/run-5d3c99aaaae1/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-5d3c99aaaae1/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-5d3c99aaaae1/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-5d3c99aaaae1/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-5d3c99aaaae1/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |
| `E-8` | `runs/run-5d3c99aaaae1/execution-metrics.json` | resolved; the metrics cited under Verification |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed; validated 30 of 30; tier standard, host hint `inherit` | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-5d3c99aaaae1/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed; validated 30 of 30; tier deep, host hint `opus` | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-5d3c99aaaae1/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed; validated 32 of 32; tier deep, host hint `opus`. An independent review returned approve-with-corrections and a correction pass closed its two findings before the Fix Gate | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-5d3c99aaaae1/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed; validated 31 of 31; tier standard, host hint `inherit`; 8 of 8 criteria met | `omn-qa` subagent, dispatched by the host | `runs/run-5d3c99aaaae1/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed; validated 34 of 34; tier light, host hint `haiku`. The first run of the artifact failed one blocking check, `C6.2`, in the offline validator run; the producer corrected it before completion, so the failure was not a charged attempt | `omn-orchestrator` subagent, dispatched by the host | `runs/run-5d3c99aaaae1/states/closure-and-communication/validation-report.json`, `runs/run-5d3c99aaaae1/states/closure-and-communication/failure-envelope.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-5d3c99aaaae1`: 5 completed, 0 blocked, 0 failed, 0 pending, four gates completed, run status Completed, 29 transitions. Every phase was executed by a host-dispatched subagent.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Triage validated 30 of 30 and the defect traces to the supplied report; `omn-dev-1-bug-analyst` produced the evidence and is excluded from deciding |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, dispatched independently of the implementer, recorded by the session operator | Independent reviewer verdict approve; adjudication approve-with-corrections, rationale recorded verbatim in the gate decision. The medium finding `F-001` and the low finding `F-002` were closed by a correction pass before the gate was decided |
| Verification Gate | approve | omn-dev-2-reviewer | operator on behalf of omn-dev-2-reviewer | Regression validation validated 31 of 31 with 8 of 8 criteria met; `omn-qa` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-documentation | operator on behalf of omn-documentation | Closure validated 34 of 34; `omn-orchestrator` produced the evidence and is excluded from deciding |

Producer exclusion held at every gate: no gate was decided by the agent that produced its evidence.

## Verification

All commands were run from the repository root of this worktree, standalone, and the results are what they returned on this tree.

| Check | Command | Result |
|---|---|---|
| Regression tests | `python tests/test_investigate_research_handoffs.py` | 22 tests, all failing on the pre-fix tree and passing after, per the implementation report and the validation report of the run. Blocked hand-offs fall from 13 to 7, the 7 pinned as `KNOWN_BLOCKED_EDGES`. Not re-run while authoring this proposal |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, 37 of 37 phases dispatchable |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 CONFORMS |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED, run on this tree with the FC-018 and FC-019 repairs present |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8 NOT SELF-HOSTING. `S1` to `S7` pass: `S6` accepts FC-001 to FC-020 (each 38/38) and `S7` passes for every recorded run. `S8` fails and names only `run-5df08e171670 (2026-09-14T07:19:57Z)`, a pre-existing older run without a proposal |
| Vertical slice | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN. The command appends replay records to that committed run; they were restored with `git checkout -- .claude/runs/run-c5a8d50d3238/state.json .claude/runs/run-c5a8d50d3238/task-context.yaml`, and `git status` then showed no change under that run |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | 14/15 NOT PROVEN, the one failing check `M14`, the re-run of the same request. `M14` is intermittent in this worktree path: 15/15 on an identical copy of the tree in a temporary directory and on a clean export of the base commit. The result got here is reported as returned; the run was restored as above and any stray `state.json.tmp` removed |
| Recovery | inspection | `verify_recovery.py` was not re-run, because it mutates committed run evidence and no throwaway copy was made. The FC-016 result, 73/74 with `X1` pre-existing, is cited as unchanged: no runtime function changed, so `RUNTIME_VERSION` stays 0.9.0 |
| Unit suite | `python tools/run_tests_parallel.py` | 690 tests discovered, 687 pass, 3 fail. All three failures are in `tests/test_demo_capture.py`, class `EndToEndEditTestCase`, because ffmpeg 9.0.2, installed by WinGet at 19:32 on 2026-10-09, rejects the `filter_complex_script` option that `runtime/demo/editor.py` uses. The same three failures reproduce identically on a clean `git archive` export of the base commit, so they are independent of this change (defect `DF-001`, `O-005`). The suite was not re-run while authoring this proposal |
| Post-repair check with real agents | the resumed run `run-437e2f765e4b` (FC-017's investigate run), the first run through the repaired chain | the `recommendation` phase dispatched, guard `G5-INPUT` passing through the new `investigation-report.md` edge; a real `omn-tech-lead` subagent delivered a technical recommendation validated 33 of 33 on the first attempt; then `publication` dispatched with two `technical-recommendation` artifacts, the option-analysis draft and the recommendation final, and a real `omn-documentation` subagent at tier light delivered a release note validated 32 of 32 (status provisional, verdict partial placeholder); the run completed, and `verify_self_hosting` `S7` passes for it. Two caveats, stated plainly below |
| Run metrics | inspection of `runs/run-5d3c99aaaae1/execution-metrics.json` | wall clock 2h12m41s, agent-active 1h31m03s; invocations by tier 1 light, 2 standard, 2 deep, 0 untiered, non-deep share 60 percent. One run of one bug, not a controlled comparison |

Caveat 1: the documentation agent reported that the Required Inputs rule and the precedence rule were absent from the contract text it read, and that it read its context from the main checkout path. Registered subagents therefore appear to take their agent contract text from the main checkout, not from this worktree, so the precedence rule of the repaired documentation contract was NOT exercised by that run. The choice the agent made, the recommendation-phase artifact, matches the rule. The rule can be exercised only once the change lands in the main checkout (`O-007`).

Caveat 2: the friction items that the two real agents reported against the repaired contracts are open items, not fixed here (`O-008`).

## Risk and Rollback

- Blast radius: the 17 framework files listed in Scope Classification, one test file and the bundled mirror. No runtime function, config policy other than the two profile rows, or validator changed, and `RUNTIME_VERSION` is unchanged at 0.9.0.
- Risk assessment: `R-001`: the precedence rule in the documentation contract has not been exercised by a registered agent (`O-007`). `R-002`: 7 hand-offs remain blocked in `review-pull-request`, `release` and `implement-feature`; they are pinned as known gaps in the test, not hidden (`O-001`). `R-003`: the version bumps to 1.1.0 reset gate auto-approval precedent for the two agents, which is stricter, so a human decision is required where an automatic one might have been taken. The new edge `investigation-report.md` to `recommendation` makes the investigate and research Phase Models stricter by one hard input each.
- Rollback procedure: revert the listed framework files, the new test file and the bundled mirror, run `python tests/test_bundled_payload.py --sync` and confirm `python tests/test_bundled_payload.py` passes, and return both agent versions to 1.0.0 in the manifest, the registry and the host registration. Existing runs are pinned at workflow 1.0.0 and are unaffected. No committed run evidence is invalidated; `run-437e2f765e4b` stays completed, but it could not be re-run through the old chain.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED |
| `FR-03` | Recovery behaviour | pass | Not re-run, because it mutates committed run evidence. The FC-016 result, 73/74 with `X1` pre-existing, is carried unchanged because no runtime function changed |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN; the committed run restored afterwards |
| `FR-05` | Self-hosting governance resolves | fail | 7/8; `S8` fails only on `run-5df08e171670`, a pre-existing older run without a proposal; `O-009` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-5d3c99aaaae1` is a `/bugfix` run over `fix-bug`, all five phases completed and all four gates decided; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | `RUNTIME_VERSION` stays 0.9.0: contracts, registry, workflow and profile text changed, no runtime function |
| `FR-08` | Documentation matches delivered behaviour | pass | The contract text, templates and workflow Input cells describe the repaired hand-offs; the gaps that remain are recorded as `O-001` to `O-010` |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row is a command output or a cited artifact. This record discloses that the precedence rule was not exercised by a registered agent, that 7 hand-offs remain blocked, that the unit suite has 3 failures from an independent cause, and that `M14` failed in this worktree |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | fail | 14/15; `M14` failed on the re-run of the same request. Intermittent in this worktree path and 15/15 on an identical copy in a temporary directory and on a clean export of the base commit, so an environment effect, not caused by this change |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | The consumer-visible effect is that `/investigate` and `/research` runs can now complete through the runtime; it is communicated by the closure record `runs/run-5d3c99aaaae1/states/closure-and-communication/artifacts/orchestration-result.md` and this proposal |

`FR-05` and `FR-11` are reported as failures as the commands returned them. The recovery result is carried from FC-016, not re-run.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The 7 remaining blocked hand-offs in `review-pull-request`, `release` and `implement-feature`, pinned as known gaps in `KNOWN_BLOCKED_EDGES` | architect | Open. Each follow-up must shrink the pinned list. This proposal closes FC-017 `O-001`, the three investigate-chain contract defects, for the investigate and research chains only |
| `O-002` | The other two profile rows, `change-review` and `framework-release`, name entry input types that their entry agents reject | omn-tech-lead | Open |
| `O-003` | The implementer host registration still says 1.0.0 against its 1.1.0 manifest | omn-tech-lead | Open |
| `O-004` | Whether to withdraw the producerless accepted identifiers `framed-objective` and `research-brief`, kept here for additivity | architect | Open |
| `O-005` | `DF-001`: ffmpeg 9.0.2 rejects the `filter_complex_script` option used by `runtime/demo/editor.py`, failing 3 tests in `tests/test_demo_capture.py`; reproduced on a clean export of the base commit | omn-tech-lead | Open, independent of this change |
| `O-006` | The documentation contract has no verdict for a findings publication; `releaseVerdict` partial in the release note of `run-437e2f765e4b` is a placeholder | architect | Open |
| `O-007` | Registered subagents appear to read agent contract text from the main checkout, so a contract change cannot be exercised by registered agents in a worktree before landing; the precedence rule is unexercised | omn-qa | Open. Exercise the rule once the change lands in the main checkout |
| `O-008` | Friction items reported by the two real agents against the repaired contracts: digests of the same investigation report differ between the envelope and the task context (36094 against 36095 bytes noted); `task-context.yaml` still shows investigate v1.0.0 and reuses question identifiers across phases; the word "token" falsely triggers the security affected-area and makes skill `S09` required; the dispatch prompt's Prohibited section contradicts the envelope's permitted command execution; the output contracts do not state that the validator rejects one reserved substring; `agentVersion` 1.1.0 in the manifest against the `identity.md` status line 1.0.0; Stage 8 has no verdict for a findings publication | architect | Open |
| `O-009` | `S8` fails on `run-5df08e171670`, an older run without a proposal, pre-existing | omn-orchestrator | Open, pre-existing. Closes only by a proposal authored by whoever carried that change; fabricating one would falsify the record |
| `O-010` | Version strings: the module status lines that say 1.0.0 and the profile identity version | omn-tech-lead | Open |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates and omn-documentation at the Closure Gate, each recorded by the operator or the independently dispatched reviewer, none of them the producer of the evidence it decided
- Acceptance basis: all five phases of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; all four gates approved with producer exclusion held; the defect witnessed by 22 tests that fail before the fix and pass after; blocked hand-offs reduced from 13 to 7 with the remainder pinned; a real-agent run through the repaired chain completing; the verifier results reported as returned, including the multi-phase `M14`, the three independent unit-suite failures and the pre-existing `S8`; and ten open items recorded with an owner
