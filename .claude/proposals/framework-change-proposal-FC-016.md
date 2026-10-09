# Framework Change Proposal: Per-Phase Model Tier in the Dispatch Envelope

```yaml
frameworkChangeProposal:
  proposalId: FC-016
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-ded114f50a46
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-016
- Change title: Per-phase model tier in the dispatch envelope (step 1 of subagent token optimization)
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-ded114f50a46
- Authored on: 2026-10-08

## Authoring Baseline

- Authored at: 2026-10-08T16:15:39Z
- Runtime version: 0.9.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

## Change Statement

- Objective: let the framework declare, per phase, which model class should execute it, and carry that declaration in the dispatch envelope, so that light phases can be executed by a cheaper model while demanding phases keep the strongest one. A recorded rejection is evidence that the chosen tier was too weak, so the runtime escalates one tier per recorded rejection, capped at the deepest tier. The runtime only advises: it copies an opaque hint into the envelope and never calls a model. Before this change every dispatched phase ran on whatever model the dispatching session happened to use, which made cost a property of the session rather than of the phase.
- In scope: a new declarative policy file, `config/model-tier-policy.json`, assigning each of the 37 phases to one of three tiers (14 light, 14 standard, 9 deep) and mapping each tier to an opaque hint (light to `haiku`, standard to `inherit`, deep to `opus`); a loader and an additive envelope field `model_tier` in the runtime, with escalation of one tier per validator rejection recorded in the recovery ledger or per gate-rejection rollback recorded in supersessions, capped at deep, derived only from recorded state; execution metrics extended to report invocations by tier and the non-deep share; two new registry coverage checks, `C7` declaration coverage and `C8` escalation monotonicity; the two configuration documents that describe the envelope and the runtime; `RUNTIME_VERSION` moved from 0.8.0 to 0.9.0; the unit tests for the feature; and the packaging mirror refreshed. For the routed workflow, `scope-and-acceptance` is light, `execution-planning` standard, `solution-design-and-risk-assessment` deep, `implementation` deep, `quality-review` deep, and `documentation-and-release-handoff` light, so 3 of 6 phases are non-deep with no margin.
- Out of scope: parallel phase execution (a separate later change, step 2); agent module text; Phase Model tables; gates; validators; templates; any model call or vendor SDK in the runtime; and an operator override switch. An absent policy file never promotes a phase: the field is simply omitted and behaviour is as in 0.8.0.
- Acceptance basis: every one of the 37 phases declared and resolvable to a tier (check `C7`); escalation provably monotone and capped (check `C8`); the envelope field additive so that earlier runs replay unchanged; every verifier at its recorded baseline; the unit suite green with the new tests; and the hint reaching a real dispatch envelope and a real escalation observed in this run's own evidence.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/config/model-tier-policy.json` | `SR-1` | in-scope | New file; the declarative tier assignment for all 37 phases and the tier-to-hint map |
| `.claude/config/runtime.md` | `SR-1` | in-scope | Runtime governance text extended with the tier and escalation rules |
| `.claude/config/execution-engine.md` | `SR-1` | in-scope | Envelope contract gains the additive `model_tier` field |
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | Policy loader, envelope field, escalation, `RUNTIME_VERSION` 0.8.0 to 0.9.0 |
| `.claude/runtime/execution_metrics.py` | `SR-1` | in-scope | Tier breakdown and non-deep share reported per run |
| `.claude/runtime/verify_registry_coverage.py` | `SR-1` | in-scope | Checks `C7` and `C8` added |
| `tests/test_model_tier.py` | none | out-of-scope | Outside the framework root; unit tests for the feature |
| `omn_agent/_bundled_payload/**` | none | out-of-scope | Outside the framework root; a generated mirror of the in-scope files, refreshed by `python tests/test_bundled_payload.py --sync` |
| `.claude/runs/run-ded114f50a46/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/runs/inputs/model-tier-feature-request.md` | `SR-3` | out-of-scope | Supplied run input; the other three `model-tier-*.md` inputs are the same |
| `.claude/proposals/framework-change-proposal-FC-016.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains a runtime capability, a per-phase model tier carried in the dispatch envelope, that it did not have
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`, `change-request`, `business-intent`, `architecture-context`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path .claude/runtime/framework_runtime.py --path .claude/config/model-tier-policy.json` returns framework-internal, each path decided by `SR-1`; `python .claude/runtime/self_hosting.py route --intent capability-addition` returns `/implement` over `implement-feature` at `scope-and-acceptance`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-ded114f50a46/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature`, inputs recorded with digests |
| `E-2` | `runs/run-ded114f50a46/run-ledger.json` | resolved; runtime 0.9.0, 6 states, 6 gates, status Completed |
| `E-3` | `runs/run-ded114f50a46/events.jsonl` | resolved |
| `E-4` | `runs/run-ded114f50a46/state.json` | resolved; every phase completed, none blocked, 40 transitions |
| `E-5` | `runs/run-ded114f50a46/completion-package.md` | resolved |
| `E-6` | `runs/run-ded114f50a46/states/implementation/artifacts/implementation-report.md` | resolved; the delivered files and test counts of the implementation phase |
| `E-7` | `runs/run-ded114f50a46/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed first attempt; validated 33 of 33. Dispatched before runtime 0.9.0 existed, so its envelope carries no `model_tier` | `omn-product-owner` subagent, dispatched by the host | `runs/run-ded114f50a46/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | The offline validator run before completion failed 42 of 45; the artifact was corrected before it was completed, and then validated 45 of 45. Dispatched before runtime 0.9.0 existed, so no `model_tier` in its envelope | `planner` subagent, dispatched by the host | `runs/run-ded114f50a46/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed; validated 78 of 78, with 2 architecture decision records authored at `Proposed`. Dispatched before runtime 0.9.0 existed, so no `model_tier` in its envelope | `architect` subagent, dispatched by the host | `runs/run-ded114f50a46/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed; validated 32 of 32, 13 files changed, unit suite moved from 595 to 638 tests. Dispatched before runtime 0.9.0 existed, so no `model_tier` in its envelope | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-ded114f50a46/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed first attempt at tier deep (`opus`); validated 31 of 31, verdict `approve-with-corrections` with 0 critical, 0 high, 1 medium (`F-001`) and 2 low (`F-002`, `F-003`) findings. A post-review correction pass by `omn-dev-1-implement` closed all three before the Review Gate, taking the suite to 642 tests | `omn-dev-2-reviewer` subagent, dispatched by the host | `runs/run-ded114f50a46/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Attempt 1 was dispatched at tier light (`haiku`) and rejected on check `R1`, because `releaseVerdict` carried `withheld`, which is not in the vocabulary. The runtime recorded one charged attempt, and the next dispatch envelope carried `model_tier` standard with escalation `{from: light, to: standard, validator_rejections: 1}`. Attempt 2 validated 32 of 32 with verdict `released` | `omn-documentation` subagent, dispatched by the host | `runs/run-ded114f50a46/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact. None blocked. Every phase was performed by a host-dispatched subagent under its own contract, not by the operator. The first four phases were dispatched before runtime 0.9.0 existed, so their envelopes carry no `model_tier`; the run's own metrics show 4 untiered, 1 light, 1 standard and 1 deep invocation, a non-deep share of 67 percent of 7 invocations by the runtime's own metric. The correction pass after the review was operator-dispatched, because the review artifact is committed evidence that no later work may edit.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | operator on behalf of omn-business-analyst | Scope traces to the supplied inputs; open question `Q-001` (what counts as success) resolved by the operator's default: success is at least 3 of 6 phases non-deep. `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Plan validated 45 of 45 after correction, tasks and risks traceable; `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Two decision records accepted at this gate having been authored at `Proposed`. Operator resolutions: `execution-planning` at standard accepted with no margin; hints `haiku`, `inherit`, `opus`; verifier baselines compared by pass or fail; no override switch. `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | operator on behalf of omn-qa | The medium and two low findings closed by the correction pass and re-verified before the decision, suite at 642; `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-qa | operator on behalf of omn-qa | Verifiers at their recorded baselines except the two pre-existing failures recorded as `O-002`, suite at 642 of 642 executed twice; `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-orchestrator | operator on behalf of omn-orchestrator | Six phases executed and validated, five prior gates decided by non-producing owners, one charged retry recorded with what it cost and what it triggered; `omn-documentation` produced the evidence and is excluded from deciding |

Every gate this workflow declares was decided. None was waived. The defaults recorded at the Scope and Design Gates (the success threshold for `Q-001`, the hint aliases, the baseline comparison rule, and the absence of an override switch) were chosen by the operator because the user declined to answer the question tool. They are operator defaults, not user decisions, and the user may overrule any of them.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8, two checks added (`C7` declaration coverage, `C8` escalation monotonicity), 37 of 37 phases dispatchable |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | 73/74; check `X1` fails, identically on a clean export of HEAD, run on a throwaway copy; recorded as `O-002` |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN from a clean state. An earlier 14/15 was caused by the verifier and the test suite appending replay records to that committed run's `state.json`, restored with `git checkout`; recorded as `O-006` |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8; `S8` fails on runs without proposals, pre-existing, and on this run until this proposal exists; recorded as `O-002` |
| Unit suite | `python -m unittest discover -s tests` | pass; 642 of 642, executed twice by the operator (638 before the correction pass) |
| Packaging mirror parity | `python tests/test_bundled_payload.py` | pass; after the mirror was refreshed |
| Run metrics | `runs/run-ded114f50a46/execution-metrics.json` | context about 495,747 to about 286,866 estimated tokens, 42.1 percent less under the progressive rules. This is the 0.7 saving, not a tier saving. Tier cost savings are not yet measured, because the first four phases were untiered |

## Risk and Rollback

- Blast radius: six framework files edited or created (`config/model-tier-policy.json` new, `config/runtime.md`, `config/execution-engine.md`, `runtime/framework_runtime.py`, `runtime/execution_metrics.py`, `runtime/verify_registry_coverage.py`), the new test file `tests/test_model_tier.py`, and the generated packaging mirror. No agent, workflow, template, validator, gate, or manifest changes. Component counts are unmoved at 37 phases. The envelope gains one additive field.
- Risk assessment: a hint only takes effect if the dispatching session passes it to the host as the per-dispatch model override; the runtime only advises, so an operator who ignores the hint gets 0.8.0 behaviour at 0.8.0 cost. A cheaper first attempt can waste an attempt: this was observed once, on the documentation phase, where the light tier produced an out-of-vocabulary verdict and cost one charged attempt before escalation corrected it. `execution-planning` at standard leaves zero margin for the success threshold of 3 of 6 non-deep phases, because the other three phases of the workflow are deep or light by design. Because escalation is derived only from recorded state and capped at deep, the worst case is the deepest tier plus the charged attempts already budgeted by recovery policy.
- Rollback procedure: revert the six framework files, delete or revert `config/model-tier-policy.json`, revert `tests/test_model_tier.py`, and re-run `python tests/test_bundled_payload.py --sync` to regenerate the mirror. Set `RUNTIME_VERSION` back to 0.8.0. Replay of earlier runs is unaffected, because the `model_tier` field is additive and an absent policy file omits it. Reverting would invalidate no committed proof; this run's own evidence would remain as a record of the change that was reverted.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8; 37 of 37 phases dispatchable, including the new `C7` and `C8` |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6, executed standalone |
| `FR-03` | Recovery behaviour | fail | 73/74; `X1` fails, identical on a clean export of HEAD, so pre-existing and not caused by this change; recorded as `O-002` |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | fail | 7/8; `S1` to `S7` pass, `S8` fails on runs without proposals, pre-existing, plus this run until this proposal exists; recorded as `O-002` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-ded114f50a46` is an `/implement` run over `implement-feature`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Moved 0.8.0 to 0.9.0 because runtime behaviour changed: the envelope gains `model_tier` and escalation |
| `FR-08` | Documentation matches delivered behaviour | pass | `config/runtime.md` and `config/execution-engine.md` updated with the tier and escalation rules; phase and workflow counts unmoved |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row was executed and read from its own output. Gaps recorded rather than omitted: tier savings unmeasured as `O-003`, the failing pre-existing checks as `O-002`, the replay-record mutation as `O-006` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 PROVEN from a clean state, executed standalone against `run-c5a8d50d3238`; see `O-006` |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-ded114f50a46/states/documentation-and-release-handoff/artifacts/release-note.md` |

Every command-verified item was executed standalone from the repository root rather than through the `--release-checklist` wrapper, which mutates committed evidence. The commands the checklist names are the same either way, and each result above is that command's own output. `FR-03` and `FR-05` are reported as failures honestly; both failures are shown to pre-date this change and are carried as open items rather than explained away.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The hint takes effect only if the dispatching session passes it to the host as the per-dispatch model override. Operators have no written dispatch procedure that says so | omn-tech-lead | Open. Needs documentation of the dispatch procedure for operators, including a reminder that the host must apply the hint |
| `O-002` | Two failures pre-date this change: `X1` in `verify_recovery.py` (73/74, identical on a clean export of HEAD) and `S8` in `verify_self_hosting.py` (runs without proposals) | omn-orchestrator | Open, pre-existing. `S8` closes only by a proposal per earlier run authored by whoever carried those changes; fabricating one would falsify the record |
| `O-003` | Tier cost savings are unmeasured, because the first four phases of this run were untiered. The 42.1 percent context saving is the 0.7 progressive-loading saving, not a tier saving | omn-qa | Open. Requires a fully tiered run to measure |
| `O-004` | Step 2, parallel phase execution, is a separate change | omn-tech-lead | Open. To be proposed and routed on its own |
| `O-005` | `verify_registry_coverage.py` baselines are compared by pass or fail. Whether check counts (now 8) should themselves be baselined is undecided | omn-qa | Open, operator default of pass or fail comparison applied at the Design Gate |
| `O-006` | `FR-11` mutates `run-c5a8d50d3238` replay records: the verifier and the test suite append replay records to that committed run's `state.json`, which caused an earlier 14/15 until it was restored with `git checkout` | omn-orchestrator | Open, pre-existing. Needs the verifier to run on a copy |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, omn-orchestrator at the Closure Gate, each recorded by the operator
- Acceptance basis: all six phases of the routed workflow executed by host-dispatched subagents with artifacts accepted by their registered validators; every gate decided by an owner who did not produce the evidence; one escalation from light to standard observed in the run's own evidence; the untiered first four phases and the unmeasured tier savings stated plainly; the operator-chosen defaults stated as overrulable; and six open items recorded with an owner
