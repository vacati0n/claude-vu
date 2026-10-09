# Framework Change Proposal: Investigation of Fan-Out Inside the Implementation Phase

```yaml
frameworkChangeProposal:
  proposalId: FC-017
  changeClass: decision-support
  routedCommand: investigate
  routedWorkflow: investigate
  runId: run-437e2f765e4b
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-017
- Change title: Investigation of fan-out inside the implementation phase (option B of subagent token optimization)
- Change class: decision-support
- Routed command: `/investigate`
- Run identifier: run-437e2f765e4b
- Authored on: 2026-10-09
- Revised on: 2026-10-09, after the run was resumed and completed. The first authoring recorded the run at the instant it stalled; this revision keeps that history and adds what happened afterwards

## Authoring Baseline

- Authored at: 2026-10-09T13:26:00Z (first authored 2026-10-09T05:06:19Z, while the run was stalled; revised once the run had completed at 2026-10-09T13:22:31Z)
- Runtime version: 0.9.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `problem-framing`, `technical-discovery`, `option-analysis`, `recommendation`, `publication`

## Change Statement

- Objective: decide whether one implementation phase should be carried out by several concurrent implementer invocations, as option B of subagent token optimization that FC-016 left as a separate later step. The operator fixed the criteria inside the request: the baseline is the implementation-phase elapsed wall-clock of `run-ded114f50a46` (1h55m) with suite time excluded; a token cost more than 25 percent above that baseline is rejected unless the elapsed-time gain exceeds 40 percent; and no gate, validator, contract or the one-owner-per-phase rule may be weakened. This change modifies no framework file. It is an investigation whose output is a recommendation plus evidence. The recommendation is `O-004`, measured non-parallel levers, proceed-with-conditions: do not build fan-out now. Its grounds, verified by the discovery report and spot-checked by the operator, are these. Only 6 of the 14 plan tasks of `run-ded114f50a46` belonged to its implementation phase (`T-003`, `T-006`, `T-009`, `T-010`, `T-011`, `T-014`). The longest in-phase dependency chain is 4, so the ceiling is about one third elapsed-time reduction, below the 40 percent threshold. Each extra invocation adds roughly 100 percent read volume on the only proxy available (57,746 estimated tokens per dispatch). Request fact 2, that most tasks edit the same file, was refuted as worded: 3 of 6, which is half. No agent owns a combined implementation report. The specifications conflict on concurrent leases. No host isolation or merge mechanism exists in the repository. The recommendation exists twice, and the two agree. The first was performed by the operator through an `omn-tech-lead` subagent while the phase was blocked, at `runs/run-437e2f765e4b/states/recommendation/operator-performed/technical-recommendation.md`, validated 32 of 32 offline and never ingested by the runtime. The second is the runtime-accepted artifact of a later re-dispatch, `runs/run-437e2f765e4b/states/recommendation/artifacts/technical-recommendation.md`, validated 33 of 33 on the first attempt, recommending the same option `O-004`, proceed-with-conditions. The run was resumed after the repair FC-020 (run `run-5d3c99aaaae1`) fixed the input contracts that had blocked it, and it then completed: all five phases completed, run status Completed.
- In scope: the investigation run `run-437e2f765e4b` over the `investigate` workflow, its recommendation, and this governance record. The operator decisions `Q-001` (baseline) and `Q-002` (token rule) were supplied inside the request, chosen by the operator because the user declined to answer the question tool; they are overrulable.
- Out of scope: any build of fan-out; any edit to a runtime, config, agent, workflow, registry or template file; the three contract defects of the investigate chain, which this change did not repair and which FC-020 later repaired for the investigate and research chains (carried as `O-001`, now closed); the tier of `technical-discovery` (carried as `O-002`). No in-scope path is touched.
- Acceptance basis: the routed run planned through the framework, resumed after the repair, and completed with all five phases executed by host-dispatched subagents and validated by their registered validators on the first attempt; the stall and the operator-performed work disclosed rather than removed; every gate decided by a non-producing owner; the recommendation validated 33 of 33 and agreeing with the operator-performed one; no framework file changed by this change, proved at first authoring by an empty diff against commit 280d36d (the working tree now carries other, separately proposed changes, FC-018 to FC-020); verifiers re-run on this tree and reported as they came out.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runs/run-437e2f765e4b/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this investigation |
| `.claude/runs/inputs/parallel-implementation-investigation-request.md` | `SR-3` | out-of-scope | Supplied run input, used as both `problem-statement` and `investigation-question` |
| `.claude/proposals/framework-change-proposal-FC-017.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed investigation, not a second change |

No in-scope path is touched by this change.

## Routing Decision

- Change class: decision-support
- Selector satisfied by: the option set was unknown and the current-state behaviour of the implementation phase could not yet support a specification, so the change could not be specified
- Command: `/investigate`
- Primary workflow: investigate
- Entry phase: `problem-framing`
- Required inputs supplied: `problem-statement`, `investigation-question`
- Input note: both inputs are the same request file. At first authoring the profile required the type `investigation-request`, which no agent accepts; this was defect 1 of `O-001`. FC-020 changed the profile row to name `problem-statement`, so `python .claude/runtime/self_hosting.py route --intent decision-support` now returns that input type; this run's own inputs are unchanged and were chosen before that repair.
- Classification evidence: `python .claude/runtime/self_hosting.py classify` over `.claude/runs/run-437e2f765e4b/state.json`, `.claude/runs/inputs/parallel-implementation-investigation-request.md` and `.claude/proposals/framework-change-proposal-FC-017.md` returns each path out of scope (re-run on this tree for this revision, same result), the first two by `SR-3` and the third by `SR-5`, with the verdict "not a framework-internal change". `python .claude/runtime/self_hosting.py route --intent decision-support` returned, at first authoring, `/investigate` over `investigate` at `problem-framing` of 5, with input `investigation-request`. Re-run on this tree after FC-020 it returns the same command, workflow and entry phase with input `problem-statement`.

Three probe runs preceded this one. All were untracked, never committed, deleted before this run, and nothing was relied on from them. `run-7c8fd475ce17` was planned with the profile's own input type `investigation-request`; its entry phase blocked at `G5-INPUT` and no phase executed. `run-acc87c7b75cd` was planned with `problem-statement`; framing executed and its gate was approved, then `technical-discovery` blocked at `G5-INPUT` because nothing produces `framed-objective`; it was a stalled run, deleted rather than left to fail `C-3` forever. `run-805d54fe61ff` was planned with both input types and nothing executed; it was replaced because the request gained the operator decisions, which changes the input digest and the run identity.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-437e2f765e4b/execution-request.json` | resolved; `command_id` is `investigate`, `workflow_id` is `investigate`, inputs recorded with digests |
| `E-2` | `runs/run-437e2f765e4b/run-ledger.json` | resolved; runtime 0.9.0, 5 phases, run status Completed, last updated 2026-10-09T13:22:31Z |
| `E-3` | `runs/run-437e2f765e4b/events.jsonl` | resolved; 54 events, from `run_initialized` to the final run completion; the first 36 are the stalled history, the rest the resumed run |
| `E-4` | `runs/run-437e2f765e4b/state.json` | resolved; 5 phases completed, 0 blocked, 0 failed, 0 pending, 29 transitions |
| `E-5` | `runs/run-437e2f765e4b/completion-package.md` | resolved; aggregated for 5 of 5 completed phases, run status Completed, 3 gate decisions |
| `E-6` | `runs/run-437e2f765e4b/states/technical-discovery/artifacts/investigation-report.md` | resolved; the discovery report that carries the measured evidence |
| `E-6` | `runs/run-437e2f765e4b/states/recommendation/artifacts/technical-recommendation.md` | resolved; the runtime-accepted recommendation, option `O-004` |
| `E-6` | `runs/run-437e2f765e4b/states/publication/artifacts/release-note.md` | resolved; the publication, status provisional, releaseVerdict partial |
| `E-7` | `runs/run-437e2f765e4b/states/problem-framing/validation-report.json` | resolved; 36 of 36 |
| `E-7` | `runs/run-437e2f765e4b/states/technical-discovery/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-437e2f765e4b/states/option-analysis/validation-report.json` | resolved; option-analysis validated 33 of 33 |
| `E-7` | `runs/run-437e2f765e4b/states/recommendation/validation-report.json` | resolved; 33 of 33 |
| `E-7` | `runs/run-437e2f765e4b/states/publication/validation-report.json` | resolved; 32 of 32 |
| `E-8` | `runs/run-437e2f765e4b/states/recommendation/failure-envelope.json` | resolved; records the `G5-INPUT` block of the recommendation phase, class dependency-failure, now resolved |
| `E-8` | `runs/run-437e2f765e4b/states/recommendation/operator-performed/technical-recommendation.md` | resolved; the operator-performed recommendation, kept as history |
| `E-9` | `runs/run-437e2f765e4b/execution-metrics.json` | resolved; regenerated for this revision, the metrics cited under Verification |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `problem-framing` | `omn-business-analyst` | completed | Executed first attempt; validated 36 of 36; dispatched at tier light (`haiku`) | `omn-business-analyst` subagent, dispatched by the host | `runs/run-437e2f765e4b/states/problem-framing/validation-report.json` |
| `technical-discovery` | `omn-context-agent` | completed | Executed first attempt; validated 31 of 31. Dispatched at `inherit` although the policy declares light: an operator override, because the substance of a discovery report cannot be validated mechanically (`O-002`, `O-006`) | `omn-context-agent` subagent, dispatched by the host | `runs/run-437e2f765e4b/states/technical-discovery/validation-report.json` |
| `option-analysis` | `omn-tech-lead` | completed | Executed first attempt; validated 33 of 33; standard tier, `inherit` | `omn-tech-lead` subagent, dispatched by the host | `runs/run-437e2f765e4b/states/option-analysis/validation-report.json` |
| `recommendation` | `omn-tech-lead` | completed | History in two parts. First, the phase was BLOCKED by the runtime at guard `G5-INPUT` (reason `dependency_wait`, class dependency-failure): no accepted input type was supplied, the phase accepted `investigation-report`, `review-package`, `validation-report` and `technical-design`, while its predecessor emits `technical-recommendation`, which the phase did not accept (`O-001`). While it was blocked the work was performed by the operator through an `omn-tech-lead` subagent, at `runs/run-437e2f765e4b/states/recommendation/operator-performed/technical-recommendation.md`, validated 32 of 32 offline, and never ingested by the runtime. Later, after FC-020 repaired the hand-off by adding `investigation-report.md` as an input of this phase, the phase was re-dispatched through the runtime and executed by a real `omn-tech-lead` subagent at tier standard (`inherit`), first attempt, validated 33 of 33 by the technical-recommendation validator; the recommended option is `O-004`, proceed-with-conditions, consistent with the operator-performed recommendation. The runtime-accepted artifact is the one that stands; the operator-performed file is kept as history | first the operator through an `omn-tech-lead` subagent (not ingested); then an `omn-tech-lead` subagent dispatched by the runtime host (accepted) | `runs/run-437e2f765e4b/states/recommendation/failure-envelope.json`, `runs/run-437e2f765e4b/states/recommendation/operator-performed/technical-recommendation.md`, `runs/run-437e2f765e4b/states/recommendation/artifacts/technical-recommendation.md`, `runs/run-437e2f765e4b/states/recommendation/validation-report.json` |
| `publication` | `omn-documentation` | completed | Executed first attempt after the Recommendation Gate was approved; validated 32 of 32 by the release-note validator; tier light (`haiku`). The artifact is status provisional with releaseVerdict partial. The agent says plainly that `partial` is a placeholder: nothing was delivered to an environment, and the documentation contract has no verdict for a findings publication with no deployment status. That is a contract gap, recorded as an open item of FC-020 and carried here as `O-008`. The run was then aggregated and its completion package written | `omn-documentation` subagent, dispatched by the host | `runs/run-437e2f765e4b/states/publication/artifacts/release-note.md`, `runs/run-437e2f765e4b/states/publication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-437e2f765e4b` for this revision: all five phases completed, 0 blocked, 0 failed, 0 pending, three gates completed, 29 transitions, run status Completed. At first authoring the same command reported 3 completed, 1 blocked, 1 pending and run status WaitingForHuman, and this proposal was then `provisional`. That statement is superseded, not erased: the run was stalled, it was resumed after FC-020, and the routed workflow has now fully executed, so this proposal is `complete`. The history of the stall and of the operator-performed recommendation stays in the table above. The recovery ledger holds seven classified failures, all resolved at 0 of 3 attempts charged, one of them the `G5-INPUT` dependency failure of the recommendation phase.

The 165 first-attempt validation checks across the five executed phases (36, 31, 33, 33 and 32) all passed with no charged retry.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Framing Gate | approve | omn-product-owner | operator on behalf of omn-product-owner | Framing validated 36 of 36 and traces to the request. The first attempt to decide this gate as `omn-business-analyst`, the producer, was rejected by the Producer Exclusion Rule and recorded; the decision was then made on behalf of the non-producing owner |
| Technical Gate | approve | omn-architect | operator on behalf of omn-architect | Discovery report validated 31 of 31; `omn-context-agent` produced the evidence and is excluded from deciding |
| Recommendation Gate | approve | omn-orchestrator | operator on behalf of omn-orchestrator, on 2026-10-09 | Recommendation validated 33 of 33 and recommends `O-004`, consistent with the operator-performed recommendation; `omn-tech-lead` produced the evidence and is excluded from deciding under the Producer Exclusion Rule, so the decision belongs to the other required owner. At first authoring this gate was undecided because no runtime-accepted evidence existed; it was decided only after the re-dispatched phase completed |

The Publication phase carries no gate. Producer exclusion held at every gate. The operator decisions `Q-001` and `Q-002` were chosen by the operator because the user declined to answer the question tool. They are operator decisions, not user decisions, and the user may overrule either.

## Verification

All commands were run from the repository root of this worktree for this revision, standalone, and the results are what they returned.

| Check | Command | Result |
|---|---|---|
| No framework file changed by this change | `git diff --stat 280d36d -- .claude/runtime .claude/config .claude/agents .claude/workflows .claude/registry .claude/templates` | empty at first authoring. On this tree it is no longer empty, because separately proposed changes now sit in the working tree (FC-018 and FC-019 for `verify_validators.py`, FC-020 for agent, registry, workflow, profile and template files). None of those is this change: this investigation edited no framework file |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, 37 of 37 phases dispatchable |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED. This supersedes the 5/6 reported at first authoring: the `V4` fixture defect (old `O-007`) was repaired by FC-018 and FC-019, and `V4` now reads the committed reports, this run's included |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 CONFORMS |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8 NOT SELF-HOSTING. `S1` to `S7` pass: `S6` accepts FC-001 to FC-020 (each 38/38) and `S7` passes for every recorded run. `S8` fails and names only `run-5df08e171670 (2026-09-14T07:19:57Z)`, a pre-existing older run without a proposal. For FC-017 this is the change from `S6` failing on its stale `publication` status and `S7` failing on the stalled run |
| Vertical slice | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN. The command appends replay records to that committed run; they were restored with `git checkout -- .claude/runs/run-c5a8d50d3238/state.json .claude/runs/run-c5a8d50d3238/task-context.yaml`, and `git status` then showed no change under that run |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | 14/15 NOT PROVEN, the one failing check `M14`, the re-run of the same request. `M14` is intermittent in this worktree path: it passes 15/15 on an identical copy in a temporary directory and on a clean export of the base commit. The result got here is reported as returned, and the run was restored as above and any stray `state.json.tmp` removed |
| Recovery | inspection | `verify_recovery.py` was not re-run, because it mutates committed run evidence and no throwaway copy was made. The FC-016 result, 73/74 with `X1` pre-existing, is cited as unchanged: no runtime function changed since FC-016 |
| Run metrics | `python .claude/runtime/framework_runtime.py metrics --run-id run-437e2f765e4b`, read from `runs/run-437e2f765e4b/execution-metrics.json` | wall clock 8h41m29s, which includes the long stall between the blocked recommendation phase and its resumption, so it is not a measure of work; agent-active 27m14s; 5 of 5 phases completed, 5 invocations across 4 distinct agents; validation runs 5 passed, 0 failed; context about 430,966 legacy against about 203,763 progressive estimated tokens, 52.7 percent less; invocations by tier 3 light, 2 standard, 0 deep, 0 untiered, non-deep share 100 percent. The metric counts by policy tier, so the `technical-discovery` dispatch at `inherit` is counted as light. These replace the 22m04s, 21m51s and three-phase figures of first authoring |

## Risk and Rollback

- Blast radius: no framework file changed by this change. The change adds untracked artifacts only: the run directory, the request file and this proposal.
- Risk assessment: the risk is acting on an under-measured baseline. The token baseline is an estimate, 57,746 estimated tokens per dispatch, not actual token use, and suite time is not recorded separately from the rest of the implementation-phase wall-clock, so the 1h55m baseline was adjusted from other evidence rather than read. The recommendation is therefore proceed-with-conditions, and `O-003` exists to make a future decision measurable. The earlier risks that the investigate chain could not complete and that `V4` was failing are resolved by FC-020 and by FC-018 and FC-019. A residual risk is the publication placeholder verdict, which could be misread as a partial delivery (`O-008`). The operator-performed recommendation sits beside the accepted one and could be mistaken for it; the table above names which stands.
- Rollback procedure: nothing to roll back, because no framework file changed. Reverting means deleting this proposal, the untracked request file and the run directory; no committed proof is invalidated.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED; the failure reported at first authoring was repaired by FC-018 and FC-019 |
| `FR-03` | Recovery behaviour | pass | Not re-run, because it mutates committed run evidence. The FC-016 result, 73/74 with `X1` pre-existing, is carried unchanged because no runtime function changed |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN; the committed run restored afterwards |
| `FR-05` | Self-hosting governance resolves | fail | 7/8; `S8` fails only on `run-5df08e171670`, a pre-existing older run without a proposal; `O-005` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-437e2f765e4b` is an `/investigate` run over `investigate`, all five phases completed and all three gates decided; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | `RUNTIME_VERSION` stays 0.9.0; no runtime change |
| `FR-08` | Documentation matches delivered behaviour | pass | Nothing delivered that changes behaviour; no documentation touched |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row is a command output or a cited artifact; gaps recorded rather than omitted, including the operator-performed phase, the stall, the 14/15 multi-phase result and `O-001` to `O-008` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | fail | 14/15; `M14` failed on the re-run of the same request. Intermittent in this worktree path and 15/15 on an identical copy in a temporary directory and on a clean export of the base commit, so an environment effect, not caused by this change |
| `FR-12` | Release note where consumer-visible behaviour changed | not applicable | No consumer-visible behaviour changed; the run did produce a release note as its publication phase, status provisional, but that note announces no change |

`FR-05` and `FR-11` are reported as failures as the commands returned them. The recovery result is carried from FC-016, not re-run.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Three contract defects in the investigate chain, so no investigate run had completed without operator-performed work: (1) the profile routed `/investigate` with `investigation-request`, which no agent accepts; (2) nothing produced `framed-objective`, so `problem-framing` could not hand off to `technical-discovery`; (3) `recommendation` did not accept `technical-recommendation`, so `option-analysis` could not hand off to it | architect | CLOSED for the investigate and research chains by FC-020 (run `run-5d3c99aaaae1`), which repaired the input contracts; this run was then resumed and completed through the repaired chain. The hand-off defects of the other workflows remain open under FC-020 `O-001` |
| `O-002` | `config/model-tier-policy.json` declares `technical-discovery` at light, although its substance is unverifiable by validators; the operator dispatched it at `inherit` | omn-tech-lead | Open. Consider declaring standard |
| `O-003` | Per-command timing split (suite against non-suite) and actual token use are not recorded for implementation phases, so a fan-out decision cannot be measured today | omn-orchestrator | Open. Record both so a future decision can be measured |
| `O-004` | Recommendation phase work was performed by the operator and not ingested by the runtime; publication was not executed; the run was stalled and would fail the completion rule, `S7` | omn-orchestrator | CLOSED. Superseded: after FC-020 the recommendation phase was re-dispatched and accepted, publication executed, and the run completed; `S7` now passes. The earlier statement that the run is stalled or fails `S7` no longer holds |
| `O-005` | `S8` fails on pre-existing runs without proposals (`run-5df08e171670`) | omn-orchestrator | Open, pre-existing. Closes only by a proposal authored by whoever carried those changes; fabricating one would falsify the record |
| `O-006` | Two of the dispatches ran at tiers chosen by the operator and not the policy: `technical-discovery` at `inherit` where the policy declares light. The metrics count by policy tier, so they report that dispatch as light | omn-tech-lead | Open. Resolved if `O-002` moves the declaration |
| `O-007` | `verify_validators.py` check `V4` mutated a fixed literal that only the first committed investigation report carried, so this run's report took it to 5/6 | omn-qa | CLOSED. Repaired by FC-018 and completed by FC-019; `verify_validators.py` returns 6/6 on this tree |
| `O-008` | The publication release note carries releaseVerdict partial as a placeholder, because the documentation contract has no verdict for a findings publication with no deployment status | architect | Open. Carried as FC-020 `O-006`; decide a verdict or a rule for findings publications |

The three untracked probe runs disclosed under Routing Decision remain deleted and nothing was relied on from them.

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-product-owner at the Framing Gate, omn-architect at the Technical Gate and omn-orchestrator at the Recommendation Gate, each recorded by the operator, none of them the producer of the evidence it decided
- Acceptance basis: all five phases of the routed workflow executed by host-dispatched subagents and accepted by their registered validators on the first attempt of the runtime dispatch, with the earlier block and the operator-performed recommendation disclosed; all three gates approved with producer exclusion held; probe runs disclosed; operator decisions stated as overrulable; the verifier results reported as returned, including the multi-phase `M14` and the pre-existing `S8`; and eight open items recorded with an owner, two of them now closed
