# Framework Change Proposal: Necessity and Reuse Ladder

```yaml
frameworkChangeProposal:
  proposalId: FC-015
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-ae91e085f481
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-015
- Change title: Embed a necessity and reuse ladder, a minimum-necessary-change definition, a safety floor, and seven over-engineering review questions into the existing architecture standard and the architect, implementer, and reviewer contracts
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-ae91e085f481
- Authored on: 2026-09-18

## Authoring Baseline

- Authored at: 2026-09-18T00:29:46Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

## Change Statement

- Objective: make the framework's existing agents behave like a senior engineer who understands the problem before choosing a solution, prefers the simplest thing that satisfies the real requirement, and refuses to build what nothing requires. Before this change the framework had the ingredients but not the rule: the architect surveyed reuse across existing components only, never naming the standard library, the platform, or an already-installed dependency as candidates; the implementer had no route-selection rule between reuse, standard library, direct code, and new abstraction; and the reviewer could not raise over-engineering at all, because its own contract forbids a finding with no written standard behind it and no such standard existed. The enabling change is therefore the written standard, and the contract edits that make three roles apply it.
- In scope: the standard's four sections and two catalogue entries added to skill S01; S01's recorded version identity raised to 1.1.0 in the registry record and the skill catalogue; the architect's reuse survey extended to four candidate kinds with a `none-found` basis that names which were searched, a capability no statement requires recorded as out of scope rather than designed for, and a new external dependency made architecture-significant; the architect's own self-check restated to match; the implementer's route selection by the ladder, the rung justification recorded in the existing `Approach taken` field, a new blocking boundary check over the safety floor, and a fourth not-machine-checkable obligation; the reviewer's existing maintainability lens extended with the seven questions and the routing rule that sends a safety breach to correctness or security; and the packaging mirror refreshed over all nine changed files.
- Out of scope: any new agent, skill file, workflow phase, gate, command, template section, validator vocabulary, configuration surface, prompt layer, or hook; any runtime change, so `runtime/framework_runtime.py` is untouched and `RUNTIME_VERSION` stays 0.5.0; any change to the planner or product owner contracts, whose existing traceability rules already reject invented scope and undeclared exclusions; any contract-version increment for the three edited agents; any line-count target or size ceiling; and copying the upstream ruleset that inspired the principle, its intensity modes, its comment markers, or its commands.
- Acceptance basis: one written standard reaching all seven named phases through bindings that already exist, with no runtime change; the three role behaviours stated in binding contract text; every verifier at its recorded baseline and the unit suite at 329 of 329; component counts unmoved; and the added instruction volume measured and reported in bytes.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/skills/architecture/clean-architecture-checklist.md` | `SR-1` | in-scope | The standard's carrier, extended in place |
| `.claude/registry/skills.yaml` | `SR-1` | in-scope | S01 version identity raised to 1.1.0 |
| `.claude/skills/agent-skill-matrix.md` | `SR-1` | in-scope | S01 catalogue row version raised to 1.1.0 |
| `.claude/agents/architect/reasoning.md` | `SR-1` | in-scope | Reuse survey candidate kinds, out-of-scope rule, dependency significance |
| `.claude/agents/architect/quality.md` | `SR-1` | in-scope | Self-check restated to match the procedure |
| `.claude/agents/omn-dev-1-implement/reasoning.md` | `SR-1` | in-scope | Route selection by the ladder |
| `.claude/agents/omn-dev-1-implement/output.md` | `SR-1` | in-scope | Rung justification carried by the existing `Approach taken` field |
| `.claude/agents/omn-dev-1-implement/quality.md` | `SR-1` | in-scope | Blocking safety-floor check and a fourth obligation |
| `.claude/agents/omn-dev-2-reviewer/reasoning.md` | `SR-1` | in-scope | Seven questions inside the existing maintainability lens |
| `omn_agent/_bundled_payload/**` | none | out-of-scope | Outside `.claude/**`; a generated mirror of the nine files above, refreshed by the repository's own sync procedure |
| `.claude/runs/run-ae91e085f481/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/proposals/framework-change-proposal-FC-015.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains a behavioural standard and three contract behaviours it did not have
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`, `change-request`, `business-intent`, `architecture-context`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path .claude/skills/architecture/clean-architecture-checklist.md --path .claude/agents/omn-dev-1-implement/reasoning.md --path .claude/agents/omn-dev-2-reviewer/reasoning.md --path .claude/agents/architect/reasoning.md --path .claude/registry/skills.yaml` returns framework-internal, every path decided by `SR-1`; `python .claude/runtime/self_hosting.py route --intent capability-addition` returns `/implement` over `implement-feature` at `scope-and-acceptance`. Both were run before the work began.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-ae91e085f481/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature`, four inputs recorded with digests |
| `E-2` | `runs/run-ae91e085f481/run-ledger.json` | resolved; 6 phases, 6 completed, 0 blocked, 56 transitions |
| `E-3` | `runs/run-ae91e085f481/events.jsonl` | resolved |
| `E-4` | `runs/run-ae91e085f481/state.json` | resolved; every phase completed, none blocked |
| `E-5` | `runs/run-ae91e085f481/completion-package.md` | resolved |
| `E-6` | `runs/run-ae91e085f481/states/implementation/artifacts/implementation-report.md` | resolved; seven artifacts across six phases, including one decision record |
| `E-7` | `runs/run-ae91e085f481/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases, every one recording `pass` |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed first attempt; 9 in-scope items, 8 exclusions, 14 acceptance criteria, 6 scope decisions, 3 non-blocking open questions, verdict `bounded`; validated 33 of 33 | `omn-product-owner` subagent, dispatched by the host | `runs/run-ae91e085f481/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed over three attempts; 14 tasks across 5 waves, acyclic edges, 10 risks. Attempt 1's adapter terminated during bootstrap on an organization spend limit and produced nothing; the lease was reclaimed as a tool failure and the phase retried. Attempt 2 was rejected for two tasks missing acceptance criteria and seven capability names quoting matrix column headings rather than declared identifiers; attempt 3 cleared all three and validated 45 of 45 | `planner` subagent, dispatched by the host | `runs/run-ae91e085f481/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed over two attempts; 4 options evaluated against every recorded constraint with the selection re-derivable, 15 modules of which 5 are recorded no-change-verified, 1 architecture-significant decision with a record at `Proposed`. Attempt 1 was rejected on eight findings including two untraced objectives, an invalid reuse outcome, an unevaluated option cell, and two undefined assumption references; attempt 2 cleared all eight and validated 78 of 78 | `architect` subagent, dispatched by the host | `runs/run-ae91e085f481/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed first attempt; 8 files changed, validated 32 of 32, status `provisional` and verification `partially-verified`, honestly reporting one failing test. The phase did not implement accepted design element `M-009` and recorded no deviation for it; the review caught this, and it was closed by a later correction pass recorded below | `omn-dev-1-implement` subagent, dispatched by the host | `runs/run-ae91e085f481/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed first attempt; validated 31 of 31, verdict `approve-with-corrections` over 2 high and 1 medium finding. The review independently found the skipped design element, the stale packaging mirror, and a misattribution in the implementation report, none of which had been disclosed to it | `omn-dev-2-reviewer` subagent, dispatched by the host | `runs/run-ae91e085f481/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed over three attempts; release note at verdict `released`, validated 32 of 32. Attempt 1's adapter stalled during module bootstrap with no progress for 600 seconds and produced nothing; the lease was reclaimed as a timeout and the phase retried. Attempt 2 was rejected on one correctable check, a version field carrying a label rather than a bare version string; attempt 3 cleared it | `omn-documentation` subagent, dispatched by the host | `runs/run-ae91e085f481/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact. None blocked. Every phase was performed by a host-dispatched subagent under its own contract, not by the operator. Two blocking correction requests raised by the review were closed by an operator-dispatched pass of `omn-dev-1-implement` after the review phase completed and before the Review Gate was decided, because the review phase's own artifact is committed evidence that no later work may edit.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | operator on behalf of omn-business-analyst | 9 in-scope items each tracing to a supplied input, 8 exclusions naming every non-goal, 14 testable criteria, 0 blocking open questions; `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Acyclic graph with a recomputable order, every risk attached to a task, carrier-file selection deliberately left to the design phase rather than presumed; `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Selection re-derivable from the option table, the decision record accepted at this gate having been authored at `Proposed`, and the design's two answerable open questions answered in the decision; `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | operator on behalf of omn-qa | Both blocking correction requests closed and re-verified before the decision; the third finding upheld and traced to a runtime defect recorded as a follow-up rather than repaired inside a change forbidden to touch the runtime; `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-qa | operator on behalf of omn-qa | Every verifier at its recorded baseline on a quiet tree and the unit suite at 329 of 329 confirmed by two independent executions; the review's one monitoring item did not reproduce across three further executions; `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-orchestrator | operator on behalf of omn-orchestrator | Six phases executed, six artifacts validated, five prior gates decided by non-producing owners, four charged retries and two host failures recorded with what each repaired or cost; `omn-documentation` produced the evidence and is excluded from deciding |

Every gate this workflow declares was decided. None was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6, 37 of 37 phases dispatchable, 0 blocked |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8; S1 to S7 pass, S8 fails on runs unrelated to this change, recorded as `O-002` |
| Unit suite | `python -m unittest discover -s tests` | pass; 329 of 329, executed twice independently |
| Packaging mirror parity | `python tests/test_bundled_payload.py` | pass; included in the suite above, after the mirror was refreshed over all nine files |

## Risk and Rollback

- Blast radius: nine framework files edited in place and their generated packaging mirror. No new file, no deleted file, no runtime module, no template, no validator, no workflow specification, no manifest, no host registration, no agent version, no gate matrix row, and no registry record other than one skill version field. Component counts are unmoved at 12 active agents, 12 skills, 8 workflows, 37 phases, and 11 commands. The change adds 5,608 bytes of instruction text, which grows the architect module set by 0.53 percent, the implementer's by 1.48 percent, and the reviewer's by 0.91 percent, and leaves the planner, product owner, and QA module sets byte-identical.
- Risk assessment: the material risk of a policy that prefers less code is that it licenses removing protection. The change answers it in the text itself, by making a safety-floor breach a blocking self-check failure for the implementer and a correctness or security finding for the reviewer rather than a maintainability one, and by stating that line count is not a criterion and a shorter implementation is not automatically better. A three-task before-and-after comparison found every validation branch preserved and no test removed. One negative result is recorded and not explained away: on the configuration-loading task, the before-condition review found a high-severity correctness defect that the after-condition review missed, on materially identical code in which the defect was confirmed still present by direct probe. With one sample per condition this cannot distinguish reviewer variance from attention dilution caused by adding seven questions to the maintainability lens, and it is carried as `O-001` rather than resolved. A second risk materialised during the run and was caught: the implementation phase silently skipped an accepted design element. The review found it without being told, which is the evidence that the framework's independence rules work, and it was corrected before the gate.
- Rollback procedure: revert the nine files to their state at the base commit and re-run `python tests/test_bundled_payload.py --sync` to regenerate the mirror. Nothing else is required: no registry record is added, no file is created, no runtime behaviour changes, and no other run's evidence depends on this capability. Reverting would restore S01 to version 1.0.0, which must be done in all three places the version is recorded, and would invalidate no committed proof.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6; 37 of 37 phases dispatchable, 0 blocked |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6; reproduced on three separate executions on a quiet tree |
| `FR-03` | Recovery behaviour | pass | 41/41, executed standalone |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | pass | Profile parses, all 7 routing rows resolve, every recorded proposal validates; checks S1 to S7 pass |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-ae91e085f481` is an `/implement` run over `implement-feature`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0. No runtime file is touched; the change is instruction text and one version field |
| `FR-08` | Documentation matches delivered behaviour | pass | The standard documents its own rules; the release note records delivered behaviour, the three corrections to committed evidence, and the follow-ups. `runtime/README.md` and the folder descriptions need no change: phase and workflow counts are unmoved and no folder gained a file |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every row of the Verification table was executed and its result read from its own output. The three gaps are recorded rather than omitted: the review-miss signal as `O-001`, the pre-existing self-hosting accounting failure as `O-002`, and the runtime prompt defect as `O-003` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 PROVEN, executed standalone against `run-c5a8d50d3238` |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-ae91e085f481/states/documentation-and-release-handoff/artifacts/release-note.md` |

Every command-verified item was executed standalone from the repository root rather than through the `--release-checklist` wrapper. The wrapper is itself a fan-out that injects probe run directories under `runs/`, and a recorded permission fault on this platform can leave them behind; running it while this change's own run is the newest record under `runs/` would corrupt the evidence this proposal links. The commands the checklist names are the same either way, and each result above is that command's own output.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | On one benchmark task the after-condition review missed a high-severity correctness defect that the before-condition review found, on materially identical code where the defect was confirmed still live. One sample per condition cannot separate reviewer variance from attention competing between the maintainability lens's new seven questions and the correctness lens | omn-dev-2-reviewer | Open. Requires repeated sampling on the same fixtures before the review change is relied upon. If dilution is confirmed, the remedy is ordering or separation inside Stage 4, not removal of the questions |
| `O-002` | Four framework runs predating this change carry no change proposal, so `S8` of the self-hosting verifier fails at 7 of 8. They are unrelated to this change and were already recorded as an open item of an earlier proposal | omn-orchestrator | Open, pre-existing. Closing it requires a proposal per run authored by whoever carried those changes; fabricating one would falsify the record |
| `O-003` | The runtime's dispatch-prompt builder prefixes every `permitted_writes` pattern with the framework directory, so an agent granted the whole repository is shown a framework-only grant. This made the implementation phase defer authorized work and record a deviation for it | architect | Open. Not repairable inside this change, whose scope forbids touching the runtime. Needs its own routed defect-repair change against `runtime/framework_runtime.py` |
| `O-004` | Whether S01's extension is correctly classified MINOR rather than MAJOR, and whether the additive edits to the three agent module sets warrant a contract-version increment in a later governance change, given that host registrations pin version 1.0.0 and gate auto-approval keys precedent on agent version | omn-tech-lead | Open, carried from the scope definition and the design. Both were judged non-blocking at their gates |
| `O-005` | This proposal is numbered FC-015 rather than FC-007, the next free identifier on this branch. The repository's primary checkout carries uncommitted proposals FC-007 through FC-014 that this worktree's base commit does not contain, and reusing one of those identifiers would collide on merge and could overwrite another change's governance record | omn-orchestrator | Open as a note, not a defect. The verifier discovers proposals by glob and does not require contiguous identifiers; the gap is cosmetic and the collision it avoids is not |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, omn-orchestrator at the Closure Gate, each recorded by the operator
- Acceptance basis: all six phases of the routed workflow executed by host-dispatched subagents with artifacts accepted by their registered validators; every gate decided by an owner who did not produce the evidence; four charged retries and two host adapter failures recorded with what each repaired or cost; one real defect found by the independent review and corrected before its gate; and five open items recorded with an owner, including the one negative measurement this change does not explain away
