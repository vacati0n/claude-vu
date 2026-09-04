# Framework Change Proposal: Memory Token Optimizer Command

```yaml
frameworkChangeProposal:
  proposalId: FC-006
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-09099de97613
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-006
- Change title: Add the `/optimize-memory` entry point and the runtime module that compresses the framework's durable knowledge surfaces
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-09099de97613
- Authored on: 2026-08-28

## Authoring Baseline

- Authored at: 2026-08-28T07:23:52Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

## Change Statement

- Objective: give the framework a control on the per-run cost of its own durable knowledge. Memory, context, and standing instruction files are read into the context slice of every dispatch, so their size is paid on each run and by every agent a run dispatches, and that cost only grows — recording a decision, a standard, or a known issue is the framework working correctly, and each recording makes every later run more expensive to start. Twenty-one files totalling 65,162 bytes were in that position when this change began, and nothing in the framework measured or reduced it.
- In scope: the `commands/optimize-memory.md` contract; the `runtime/optimize_memory.py` module that performs discovery, the compression request, the invariant judgement, the session record, and the undo; the active discovery record in `registry/commands.yaml`; the catalog row and the corrected contract count; the proposal index appended to `config/self-hosting-profile.md`; and the automated coverage in `tests/test_optimize_memory.py`.
- Out of scope: executing a pass over this repository's own knowledge surfaces, which is a separate change carrying its own review of its own difference record; deciding what belongs in memory or context, which stays with `memory/memory-governance.md`; any new workflow, phase, gate row, role manifest entry, or artifact validator; and proving that reworded prose means the same thing, which the framework cannot decide and therefore does not claim.
- Acceptance basis: the entry point resolves through framework discovery with every contract on disk carrying a record; a default invocation leaves every in-scope file byte-identical; a candidate that drops content is refused with the loss named; every modification has a recoverable pre-image and a recorded digest pair; denied paths are unreachable regardless of argument; and every framework verifier returns to its recorded baseline with one added command record and no other count moved.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/commands/optimize-memory.md` | `SR-1` | in-scope | The new command contract |
| `.claude/runtime/optimize_memory.py` | `SR-1` | in-scope | The new runtime module |
| `.claude/registry/commands.yaml` | `SR-1` | in-scope | One additive active record, `primaryWorkflow: refactor` |
| `.claude/commands/command-catalog.md` | `SR-1` | in-scope | Catalog row for the new contract |
| `.claude/commands/README.md` | `SR-1` | in-scope | Contract count corrected from ten to eleven |
| `.claude/config/self-hosting-profile.md` | `SR-1` | in-scope | The proposal index, appended after the last parsed heading |
| `.claude/runtime/verify_validators.py` | `SR-1` | in-scope | The `release-note.md` mutation expressed as a derivation, repairing a regression this run's own release note caused |
| `.claude/runs/run-09099de97613/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/proposals/framework-change-proposal-FC-006.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains a command contract, an active registry record, and a runtime behaviour it did not have
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`, `change-request`, `business-intent`, `architecture-context`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path .claude/commands/optimize-memory.md --path .claude/runtime/optimize_memory.py --path .claude/config/self-hosting-profile.md` returns framework-internal, every path decided by `SR-1`; `python .claude/runtime/self_hosting.py route --intent capability-addition` returns `/implement` over `implement-feature` at `scope-and-acceptance`. Both were run before the work began.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-09099de97613/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature`, four inputs recorded with digests |
| `E-2` | `runs/run-09099de97613/run-ledger.json` | resolved |
| `E-3` | `runs/run-09099de97613/events.jsonl` | resolved |
| `E-4` | `runs/run-09099de97613/state.json` | resolved; six phases, all completed, none blocked |
| `E-5` | `runs/run-09099de97613/completion-package.md` | resolved |
| `E-6` | `runs/run-09099de97613/states/implementation/artifacts/implementation-report.md` | resolved; eight artifacts in total across six phases, including two decision records |
| `E-7` | `runs/run-09099de97613/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases, every one recording `pass` |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed against the run over two attempts; 9 in-scope items, 6 exclusions, 10 acceptance criteria, 0 blocking open questions, verdict `bounded`. Attempt 1 was rejected at `C7.1` for recording the feature-request digest alone where the combined input-set digest was required; corrected and re-completed | Operator, exercising the `omn-product-owner` contract | `runs/run-09099de97613/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed against the run; 9 tasks over 6 waves, an acyclic edge table from which the stated order recomputes, 3 assumptions, 7 risks, 2 non-blocking open questions | Operator, exercising the `planner` contract | `runs/run-09099de97613/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed against the run over two attempts; 4 options evaluated against 8 constraints with the selection re-derivable, 9 modules of which 3 are recorded no-change-verified, 2 architecture-significant decisions each with a record at `Proposed`. Attempt 1 was rejected at `D16.4` for leaving two supplied planner tasks unbound by any sequencing constraint; corrected and re-completed | Operator, exercising the `architect` contract | `runs/run-09099de97613/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed against the run; 7 change-set entries each carrying test evidence, 2 recorded deviations, 4 residual risks. Status `provisional` and verification `partially-verified`, because the compression request path cannot be exercised in this environment and the contract permits `complete` only where the evidence leaves nothing unreached | Operator, exercising the `omn-dev-1-implement` contract | `runs/run-09099de97613/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed against the run; 6 findings including one critical, verdict `approve-with-corrections`, both blocking correction requests closed before the gate. The review re-executed the evidence rather than accepting the implementation report's claims, and found a real defect: both the pre-image write and the dry-run candidate write joined an absolute path, so for a scope root outside the repository each resolved to the original file | Operator, exercising the `omn-dev-2-reviewer` contract | `runs/run-09099de97613/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed against the run; release note at verdict `partial` with 3 known issues, including the distinction between the checked structural guarantee and the semantic one a reader may assume | Operator, exercising the `omn-documentation` contract | `runs/run-09099de97613/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact. None blocked. All six were performed by the operator against the run rather than by a host-dispatched subagent; the framework selected the route, held every gate, and validated every artifact, and the run's own record shows which.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | operator on behalf of omn-business-analyst | Scope bounded with 0 blocking open questions; the guarantee boundary drawn explicitly, so the artifact does not sell a guarantee the change cannot keep; `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Acyclic graph, recomputable order, the single external dependency blocking a demonstration rather than the delivery path; `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Selection re-derivable from the option table; both decision records accepted at this gate, having been authored at `Proposed`; `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | operator on behalf of omn-qa | Both blocking correction requests closed and re-executed; 31 of 31 automated checks passing; `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-qa | operator on behalf of omn-qa | Coverage discriminating rather than decorative; the one unexercised path disclosed in three artifacts with a correction owed before first use; `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Closure Gate | approve | omn-orchestrator | operator on behalf of omn-orchestrator | Six phases executed, six artifacts validated, five prior gates decided by non-producing owners, two charged retries recorded with what they repaired; `omn-documentation` produced the evidence and is excluded from deciding |

Every gate this workflow declares was decided. None was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6, 11 of 11 command records resolve, 37 of 37 phases dispatchable, 8 workflows |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6, restored from 5/6 by expressing the `release-note.md` mutation as a derivation |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py --release-checklist` | recorded in Release Checklist Result below |
| Optimizer behaviour | `cd tests; python -m unittest test_optimize_memory` | pass; 31/31, covering one constructed candidate per loss class, the denial boundary per denied segment, and all four recovery outcomes |
| Optimizer discovery over the real surfaces | `python .claude/runtime/optimize_memory.py scan` | pass; 21 eligible of 21 considered, 65,162 bytes in scope, no file modified |
| Absent-dependency path | `python .claude/runtime/optimize_memory.py run` | pass; exits 2 before reading any file, naming the missing client library |
| Profile still parses and routes | `python .claude/runtime/self_hosting.py route --intent capability-addition` | pass; resolves to `/implement` over `implement-feature` |

## Risk and Rollback

- Blast radius: one new runtime module, one new command contract, one additive registry record, two reader-facing index documents, one appended profile section, one new test module, and one verification-script repair. No workflow, phase model, gate matrix row, agent manifest, artifact template, or artifact validator changed. No knowledge surface was modified: the twenty-one files the change exists to compress are byte-identical to their state before it.
- Risk assessment: one critical defect materialised and was caught before the Review Gate. The pre-image write and the dry-run candidate write both joined the session directory with a path that is absolute for a file outside the repository, and joining an absolute path discards everything to its left — so for a scope root outside the repository, backing a file up would have overwritten it with itself and a dry run would have written its candidate over the original. The drive-letter scrub masked it on one platform and not the other, so it was platform-conditional and silent. It was repaired at its cause by confining every session write, with five regression tests fixing the defect's shape in place. One regression was introduced by this run's own success: committing a real `release-note.md` broke a mutation anchor pinned to an older note's version string, the same failure mode `FC-005` recorded for `bug-analysis.md`, and it was repaired the same way — as a derivation rather than a literal. Two risks remain accepted and recorded: the compression request path ships unexercised because this environment carries no client library or credential, and the guarantee is structural and identifier-level rather than semantic.
- Rollback procedure: remove the `optimize-memory` record from `registry/commands.yaml` and `commands/optimize-memory.md` together — a partial removal is caught by coverage check `C1` — delete `runtime/optimize_memory.py` and `tests/test_optimize_memory.py`, restore the ten-contract count in `commands/README.md`, remove the catalog row, and remove the appended profile section. The `verify_validators.py` derivation should be kept: it is a repair to a verification script that was fragile independently of this change, and reverting it would reintroduce a `V4` failure the moment any future run commits a release note. Reverting invalidates no other run's evidence, because no other run depends on this capability. An optimization pass already applied is undone separately through the module's own restore path, from the session record it wrote; rollback of the capability and rollback of a pass are independent operations and neither implies the other.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6; 11 of 11 command records resolve, 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6; restored from 5/6 at its cause, by expressing the `release-note.md` mutation as a derivation |
| `FR-03` | Recovery behaviour | pass | 41/41 |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | pass | Profile parses, all 7 routing rows resolve, all recorded proposals validate |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-09099de97613` is an `/implement` run over `implement-feature`; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0. The new module is not imported by the runtime and changes no behaviour the version denotes; the `verify_validators.py` repair restores a check rather than altering runtime behaviour |
| `FR-08` | Documentation matches delivered behaviour | pass | `commands/README.md` count corrected to eleven, `commands/command-catalog.md` carries the row, the command contract documents the delivered behaviour including what it does not guarantee. `runtime/README.md` needs no change: it records phase and workflow counts, and both are unmoved |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim in the Verification table above was executed and its result read from its own output. The one gap — the unexercised compression request path — is recorded in the design as `A-002`, in the implementation report as an unverified area, in the review as `F-004` with `CR-004`, and in the release note as `K-001`, rather than omitted |
| `FR-10` | Rollback stated | pass | Risk and Rollback above, including which part of the change should not be reverted and why |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 PROVEN on `run-c5a8d50d3238` |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-09099de97613/states/documentation-and-release-handoff/artifacts/release-note.md`, verdict `partial`, 3 known issues |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The compression request path has never been executed end to end; this environment carries no provider client library and no credential. Its first live invocation will be its first test | omn-tech-lead | Open. `CR-004` of the review requires it exercised before any pass is applied to a knowledge surface. Exposure is bounded: every failure on that path is recorded per file and leaves the original untouched |
| `O-002` | The guarantee is structural and identifier-level. A candidate preserving every heading, table row, identifier, link, code block, and list item may still have reworded prose in a way that changes an obligation expressed only in prose. Whether a checkable prose-level invariant exists is unanswered | architect | Open. Carried as design risk `R-001`, review question `Q-002`, and known issue `K-002`. The contract states the boundary in its own words and names the recorded difference record as the control; this is a documentation control over a reader's assumption, not a mechanical one, and is not considered closed |
| `O-003` | A pass in which no candidate is ever refused is indistinguishable from a pass in which every candidate was correct, so a silently broken judgement looks like a clean run | omn-dev-2-reviewer | Open. Recorded as monitoring guidance in the release note; whether it should raise a signal of its own is unresolved |
| `O-004` | Two low findings remain open: a redundant construction in the fenced-block comparison, and no coverage for the session report renderer | omn-dev-1-implement | Open, non-blocking. `CR-003` and `CR-005` |
| `O-005` | Two framework runs from 2026-08-27, `run-34ca35504b72` and `run-efe092286625`, carry no change proposal and fail `S8` of the self-hosting verifier. They predate this change and are unrelated to it; this proposal accounts for `run-09099de97613` only | omn-orchestrator | Open, pre-existing. Recorded here because `S8` reports it on every run of the verifier, and a reader of this proposal will see it. Closing it requires a proposal per run, authored by whoever carried those changes; fabricating one would falsify the record |
| `O-006` | `omn-orchestrator` is routed the action of authoring the change proposal that accounts for a run, but its manifest permits no repository write in any phase | omn-tech-lead | Open, unchanged. Tracked as `O-003` of `FC-005`; this proposal was authored by the operator for the same reason |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, omn-orchestrator at the Closure Gate, each recorded by the operator
- Acceptance basis: all six phases of the routed workflow executed with artifacts accepted by their registered validators, every gate decided by an owner who did not produce the evidence, two charged retries recorded with what each repaired, one critical defect found by the review and corrected at its cause with regression coverage, one verification regression repaired at its cause, and six open items recorded with an owner — including the two this change does not close and the one it did not cause
