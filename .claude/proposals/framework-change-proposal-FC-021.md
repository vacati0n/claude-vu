# Framework Change Proposal: Repair the omn-documentation release-verdict contract (a truthful release position for every non-deploying publication phase)

```yaml
frameworkChangeProposal:
  proposalId: FC-021
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-f94564cb61ce
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-021
- Change title: Repair the omn-documentation release-verdict contract (a truthful release position for every non-deploying publication phase)
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-f94564cb61ce
- Authored on: 2026-10-17

## Authoring Baseline

- Authored at: 2026-10-17T06:10:00Z
- Runtime version: 0.10.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

The runtime version is 0.10.0 because the sibling change FC-022, in the same working tree, raised it from 0.9.0 for its own runtime change; the run that carried this change recorded runtime 0.10.0 (`runs/run-f94564cb61ce/state.json`). This change does not move it; see `FR-07`.

## Change Statement

- Objective: repair the defect in `runs/inputs/release-handoff-verdict-defect-report.md`. `omn-documentation` owns five publication phases, but its release-verdict contract described only deployment outcomes: Stage 8 of `reasoning.md` read the verdict off a supplied deployment status, `output.md`, quality check `R1`, `runtime/release_note_validator.py` and `templates/release-note.md` all accepted only `released`, `partial` and `rolled-back`, and four of the five phases are never supplied a deployment status. The defect surfaced in the knowledge run `run-c9fb8d5bbb32` (FC-022): its `documentation-and-release-handoff` phase, attempt 1 at omn-documentation 1.1.0, emitted `withheld` with status `blocked`, because Stage 8 had no truthful verdict for an undeployed release handoff. The operator twice ruled that `released` applied, per precedent, and the agent declined both times; the user chose to repair the contract first (observed by the operator, and summarised in the defect report). Triage (`runs/run-f94564cb61ce/states/triage-and-impact/artifacts/bug-analysis.md`) confirmed severity high with deterministic reproduction and a survey of the 10 committed release notes, 9 of which carry a deployment verdict that no deployment status supports: 7 `released` notes for undeployed implement-feature handoffs and 2 `partial` notes, one of them the placeholder FC-020 recorded as `O-006`. The Triage Gate scoped the repair to all four non-deploying phases, kept the release phase unchanged, ruled that `withheld` is never a passing verdict, and required FC-020 `O-006` to be settled in the same change. The root cause analysis (`runs/run-f94564cb61ce/states/root-cause-analysis/artifacts/bug-analysis.md`) found that the validator tested vocabulary membership only, so nothing related the verdict to the phase basis or to a deployment-status input. It adopted the architect ruling on its `Q-001` (one position per communication basis: `handed-off` for `release-handoff`, `findings-published` for `findings`, `delta-published` for `documentation-delta`; a Blocking `R8` that ties each position to the evidence type it is read off; a Blocking `R9` that maps the invocation envelope `state_id` to the phase basis; a superseded-contract exclusion in `verify_validators.py`), corrected by its evidence entries `E-021` (the envelope did not reach the semantic checks, so new plumbing was needed on the runtime and the `--envelope` paths), `E-022` (a selection-only skip would still fail `V3`, because skipped candidates are re-validated), `E-025` (`validation-report` must be accepted beside `verification-report`) and `E-026` (the knowledge baseline pins four of the files this fix edits). The architect's follow-up ruling confirmed the open points: `V-001` stands (`R8` does not reject entries whose type is outside the declared list), the superseded exclusion (RCA `Q-006`) is confirmed, `V-002` (`validation-report` as a declared `sourceInputs` type) is confirmed, and `architecture-context` was added to the declared `sourceInputs` types, an operator edit after the review in `output.md` and the template. The fix: Stage 8 rekeyed on the communication basis; `R1` names six values and `withheld` never passes; new Blocking `R8` and `R9`; `PHASE_BASIS` in the validator; `verify_validators.py` reports committed notes produced below omn-documentation 1.2.0 as superseded and excludes them from selection and re-validation; omn-documentation and the release-note template move to 1.2.0 across the manifest, the host registration, `registry/agents.yaml` and `registry/templates.yaml`; `runtime/README.md` names all five served phases. After the review the operator also guarded the envelope JSON parse in `verify_validators.superseded_reason` with a test (Fix Gate `CR-002`, 29/29) and re-synced the mirror with `PYTHONPATH=. python tests/test_bundled_payload.py --sync`. Under the omn-tech-lead ruling on `Q-005`, option (a), the knowledge run's `CR-003` landed first, test files only and owned by FC-022, so this fix's edits to the four pinned files do not fail the knowledge baseline test. `tests/test_release_verdict.py` holds 29 regression tests; 24 of them fail on an unmodified HEAD copy and all pass after.
- In scope: the omn-documentation contract modules and host registration, the two registry records, the release-note template, the release-note validator, the validator coverage verifier, the runtime README validator table and paragraph, the regression test file, the bundled mirror of those files, and the run `run-f94564cb61ce` over the `fix-bug` workflow with this governance record.
- Out of scope: the release phase `communication-and-post-release`, whose verdicts, Stage 8 rows and `R4`/`R5` are unchanged; the 9 superseded notes and every other piece of committed run evidence, which stay as recorded; any function of `runtime/framework_runtime.py`. The sibling change FC-022, the knowledge loop carried by `run-c9fb8d5bbb32`, sits in the same working tree and owns `config/runtime.md`, `config/knowledge-policy.json`, `memory/*`, `runtime/knowledge.py`, `runtime/framework_runtime.py`, `runtime/execution_metrics.py`, `omn_agent/source.py`, `tests/test_knowledge.py`, `tests/fixtures/knowledge/`, `runs/run-c9fb8d5bbb32/` and `runs/inputs/knowledge-loop-*.md`; none of them is claimed here. The test file and the bundled mirror are outside the framework surface.
- Acceptance basis: the routed run planned through the framework, with all five phases executed by host-dispatched subagents and accepted by their registered validators; the Triage, Fix and Verification Gates decided by non-producing owners; the defect witnessed by tests that fail before and pass after; the three Verification Gate closure conditions met, the second of them by this proposal; a real-agent run through the repaired contract completing at 1.2.0; the verifier results reported as they came out; and the Closure Gate decided by omn-documentation after this proposal exists.

Two rulings this change rests on exist only as operator-supplied session files outside the repository. The run artifacts cite them as such, and this proposal is their durable record. The first is the architect ruling on RCA `Q-001`, from a read-only architect consult (subagent a96e516fa44073324). It sets one value per communication basis: `handed-off`, `findings-published` and `delta-published`, while `released`, `partial` and `rolled-back` stay for `post-release` only and `withheld` stays outside the vocabulary. It adds `R8`, tying each value to a `sourceInputs` evidence type, and `R9`, deriving the basis from the envelope `state_id` and Advisory not-machine-checkable only without an envelope. It rekeys the Stage 8 table on basis, keeps `R4`/`R5` byte-identical, makes minor 1.2.0 bumps with `schemaVersion` unchanged, and excludes notes produced below 1.2.0 from `V3` selection in `verify_validators.py`, with no exemption inside the validator. It rejected a neutral value, a non-blocking `withheld`, a synthetic deployment status, a new required basis field, and a basis field in the envelope. The second is the omn-tech-lead ruling on `Q-005` and `Q-007` (subagent abfed4f59e37b54d6). On `Q-005` it chose option (a): the knowledge run's `CR-003` lands first, in test files only. This fix must not edit `tests/test_knowledge.py` or `tests/fixtures/knowledge/`, and must not re-capture any baseline. It may edit the four pinned files (`registry/agents.yaml`, `registry/templates.yaml`, `templates/release-note.md`, `runtime/README.md`) and no other context-slice member. The Fix Gate conditions were BackwardCompatibilityTestCase 6/6 on the combined tree, the reworked identity test shown to fail when the knowledge change alters a pre-change dispatch, and no slice member edited beyond the four. On `Q-007` it permitted a whole-bundle sync only as `PYTHONPATH=. python tests/test_bundled_payload.py --sync`, because without `PYTHONPATH` the sync copies the lesson store into the bundle.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/agents/omn-documentation.agent.md` | `SR-1` | in-scope | Host registration: version table and bootstrap check at 1.2.0 |
| `.claude/agents/omn-documentation/identity.md` | `SR-1` | in-scope | Required Evidence rows for the three new positions |
| `.claude/agents/omn-documentation/manifest.yaml` | `SR-1` | in-scope | `metadata.version` 1.2.0 |
| `.claude/agents/omn-documentation/output.md` | `SR-1` | in-scope | Release position per phase, six-value `releaseVerdict`, `validation-report` and `architecture-context` as declared `sourceInputs` types |
| `.claude/agents/omn-documentation/quality.md` | `SR-1` | in-scope | `R1` names six values, `withheld` never passes; new Blocking `R8` and `R9` |
| `.claude/agents/omn-documentation/reasoning.md` | `SR-1` | in-scope | Stage 8 table keyed on the communication basis |
| `.claude/agents/omn-documentation/system.md` | `SR-1` | in-scope | Boundary row refusing to record a non-deploying publication as released |
| `.claude/registry/agents.yaml` | `SR-1` | in-scope | omn-documentation record at 1.2.0 |
| `.claude/registry/templates.yaml` | `SR-1` | in-scope | release-note record at 1.2.0, description names the five phases |
| `.claude/runtime/README.md` | `SR-1` | in-scope | Validator table names all five served phases; paragraph on `R8`, `R9` and the superseded rule |
| `.claude/runtime/release_note_validator.py` | `SR-1` | in-scope | Six-value `VERDICTS`, `PHASE_BASIS`, `R8`, `R9`, envelope on the runtime and `--envelope` paths |
| `.claude/runtime/verify_validators.py` | `SR-1` | in-scope | `SUPERSEDED_CONTRACTS`; notes below omn-documentation 1.2.0 reported and excluded; guarded envelope parse (`CR-002`) |
| `.claude/templates/release-note.md` | `SR-1` | in-scope | Template 1.2.0: five phases, six values, declared types, Known Issues comment |
| `tests/test_release_verdict.py` | no rule | out-of-scope | Outside the framework surface; 29 regression tests |
| `omn_agent/_bundled_payload/**` | no rule | out-of-scope | Outside the framework surface; the bundled mirror of the 13 files above, refreshed through `PYTHONPATH=. python tests/test_bundled_payload.py --sync` and never hand-edited |
| `.claude/runs/run-f94564cb61ce/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this repair |
| `.claude/runs/inputs/release-handoff-verdict-defect-report.md` | `SR-3` | out-of-scope | The supplied `defect-report` input |
| `.claude/proposals/framework-change-proposal-FC-021.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

The scope paths were checked against `git status` and `git diff --stat`: 19 tracked framework paths are modified under `.claude/`, 13 of them the rows above and 6 of them FC-022's (`config/runtime.md`, `memory/README.md`, `memory/memory-governance.md`, `memory/memory-resolver.md`, `runtime/execution_metrics.py`, `runtime/framework_runtime.py`), which are not claimed here. Of the 20 modified paths under `omn_agent/`, 13 mirror this change's rows; the other 6 mirrors and `omn_agent/source.py` are FC-022's. Of the untracked paths, `tests/test_release_verdict.py`, `runs/run-f94564cb61ce/` and the defect report are this change's; `config/knowledge-policy.json`, `memory/lessons/`, `tests/test_knowledge.py`, `tests/fixtures/knowledge/`, `runs/run-c9fb8d5bbb32/` and the `knowledge-loop-*` inputs are FC-022's, and so is the lesson store that this run's knowledge harvest wrote (see Verification).

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaves other than its contract declares. The documentation agent is registered to own four non-deploying publication phases, and its release-verdict contract yielded no position for them that was both truthful and accepted by the Validation Engine.
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: `triage-and-impact`
- Required inputs supplied: `defect-report`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` was run over every scope path of the table above and returned `SR-1` in scope for the 13 framework paths with the verdict "framework-internal change", no rule and out of scope for the test file and the bundled mirror, `SR-3` out of scope for the run evidence and the defect report, and `SR-5` out of scope for this proposal. `python .claude/runtime/self_hosting.py route --intent defect-repair` returns `/bugfix` over `fix-bug v1.0.0` at `triage-and-impact` of 5, with input `defect-report`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-f94564cb61ce/execution-request.json` | resolved; routed through `/bugfix` over `fix-bug`, input `defect-report` recorded with its digest |
| `E-2` | `runs/run-f94564cb61ce/run-ledger.json` | resolved; runtime 0.10.0, 5 phases, run status Completed |
| `E-3` | `runs/run-f94564cb61ce/events.jsonl` | resolved; 56 events from `run_initialized` to the final `run_completed` (`E-0056`). `E-0053` `run_completed` is emitted in the same second that `E-0051` opens the Closure Gate escalation, before any decision (`O-001`); the Closure Gate decision is `E-0054` |
| `E-4` | `runs/run-f94564cb61ce/state.json` | resolved; 5 phases completed, 0 blocked, 0 failed, 29 transitions; all four gates approved with rationales, the Closure Gate after this proposal was authored |
| `E-5` | `runs/run-f94564cb61ce/completion-package.md` | resolved; aggregated for 5 of 5 completed phases |
| `E-6` | `runs/run-f94564cb61ce/states/triage-and-impact/artifacts/bug-analysis.md` | resolved; the triage: severity high, reproduction deterministic, the 10 committed notes surveyed |
| `E-6` | `runs/run-f94564cb61ce/states/root-cause-analysis/artifacts/bug-analysis.md` | resolved; the root cause analysis, the architect ruling and its corrections `E-021`, `E-022`, `E-025`, `E-026` |
| `E-6` | `runs/run-f94564cb61ce/states/fix-implementation/artifacts/implementation-report.md` | resolved; the fix `C-001` to `C-027`, its tests `T-001` to `T-013` and deviations `V-001` to `V-004` |
| `E-6` | `runs/run-f94564cb61ce/states/regression-validation/artifacts/validation-report.md` | resolved; verdict pass-with-reservations, 13 of 15 criteria met, `AC-008` and `AC-011` blocked at that time |
| `E-6` | `runs/run-f94564cb61ce/states/closure-and-communication/artifacts/orchestration-result.md` | resolved; disposition `held`, status provisional, because this proposal did not yet exist and the Closure Gate was undecided |
| `E-7` | `runs/run-f94564cb61ce/states/triage-and-impact/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-f94564cb61ce/states/root-cause-analysis/validation-report.json` | resolved; 30 of 30 |
| `E-7` | `runs/run-f94564cb61ce/states/fix-implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-f94564cb61ce/states/regression-validation/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-f94564cb61ce/states/closure-and-communication/validation-report.json` | resolved; 34 of 34 |
| `E-8` | `runs/run-f94564cb61ce/execution-metrics.json` | resolved; the metrics cited under Verification |
| `E-8` | `runs/run-f94564cb61ce/knowledge-harvest.json` | resolved; the knowledge harvest the 0.10.0 runtime ran at this run's aggregation, cited under Verification |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed on the first attempt; validated 30 of 30; tier standard | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-f94564cb61ce/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed on the first attempt; validated 30 of 30; tier deep. The architect ruling on its `Q-001` was obtained by a read-only architect consult and corrected by the analysis's own evidence | `omn-dev-1-bug-analyst` subagent, dispatched by the host | `runs/run-f94564cb61ce/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed on the first attempt; validated 32 of 32; tier deep. An independent review returned approve-with-corrections; after it the operator made the post-review edits recorded in the Fix Gate rationale (the `CR-002` guard with its test, and `architecture-context` as a declared type in `output.md` and the template) and re-synced the mirror | `omn-dev-1-implement` subagent, dispatched by the host; post-review edits by the operator | `runs/run-f94564cb61ce/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed on the first attempt; validated 31 of 31; tier standard; verdict pass-with-reservations, 13 of 15 criteria met, 2 blocked (`AC-008`, `AC-011`), 0 defects | `omn-qa` subagent, dispatched by the host | `runs/run-f94564cb61ce/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed on the first attempt; validated 34 of 34; tier light. Disposition `held`, provisional, with open questions `Q-001` to `Q-004` and escalation `ES-002` | `omn-orchestrator` subagent, dispatched by the host | `runs/run-f94564cb61ce/states/closure-and-communication/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-f94564cb61ce`: 5 completed, 0 blocked, 0 failed, 0 pending, 28 transitions, run status Completed; three gates completed and the Closure Gate blocked `awaiting_human_decision` at authoring; the Closure Gate was then approved at 2026-10-17T06:10:45Z (`E-0054`), giving 29 transitions and four gates completed. The failure envelopes under the phase and gate directories are all `gate-approval-required` escalations with 0 attempts charged, all resolved. Every phase was executed by a host-dispatched subagent.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | omn-tech-lead subagent a7f51b28255cabbd2, recorded by the session operator | Severity high and deterministic reproduction confirmed; `Q-001` is a fix-design decision for the root cause analysis. Scope: all four non-deploying omn-documentation phases; release-phase verdicts, rows and `R4`/`R5` unchanged; `withheld` never a passing verdict; FC-020 `O-006` settled in the same change. Conditions: the validator tests the verdict against the phase basis or a declared deployment-status input; release behaviour protected by regression tests; contract, template, validator and mirror parity enforced. The proposal lists the 9 historical notes and their expected re-validation; run evidence is never edited |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent a72fae474c55ebf68, independent of the implementer, recorded by the session operator | Approve-with-corrections. Independent re-run: `test_release_verdict` 29/29 (24 of 29 fail on a HEAD copy), bundled payload 11/11, BackwardCompatibilityTestCase 6/6, verify_validators 6/6 with 9 superseded reported, verify_manifests 2/2. `CR-002` fixed after the review by the operator with a test; `CR-001` (`V-001`) and RCA `Q-006` ruled by the architect; the review's `CR-003` (superseded-count monitoring wording) carried to this proposal |
| Verification Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent a72fae474c55ebf68, which did not produce the evidence (omn-qa did), recorded by the session operator | omn-qa evidence independently re-checked; 9 notes fail exactly `R8` and `R9` as predicted. Closure conditions: (1) `AC-008`, the held run-c9fb8d5bbb32 documentation phase completed through the runtime at 1.2.0 with `handed-off`; (2) `AC-011`, this proposal; (3) omn-tech-lead accepts or decides `R-002` |
| Closure Gate | approve | omn-documentation | omn-documentation subagent ae01f3b6680787eed, which did not produce the evidence (omn-orchestrator did), recorded by the session operator | Explicit first 1.2.0 decision under `R-002`, after this proposal existed. The closure record was `held` only because this proposal did not exist and the gate was undecided; all three Verification Gate closure conditions are met; the orchestrator's open items carry into this proposal with owners; `Q-001` answered by the decision (no separate known-issue record needed), `Q-002` by the CR-003 paragraph, `Q-004` tracked in FC-022 |

Producer exclusion held at every gate: no gate was decided by the agent that produced its evidence. The Verification Gate closure conditions stand as follows. (1) `AC-008` is met: the knowledge run's documentation phase, attempt 2 (invocation `inv-c9fb8d5bbb32-06-002`, omn-documentation 1.2.0, contract read from this worktree), completed through `framework_runtime` with `releaseVerdict` `handed-off`, validated 34 of 34 with `R1`, `R8`, `R9` and `C3.2` passing at Blocking; attempt 1 had been rejected on `C3.2`, `R1`, `R8` and `R9` and retried. (2) `AC-011` is met by this proposal; see Verification. (3) `R-002` was accepted by omn-tech-lead (subagent abfed4f59e37b54d6), recorded verbatim: "gate-policy condition 7 keys precedent on producing-agent version, so 1.1.0 precedent does not carry to 1.2.0. This reset is intended, not a cost to avoid. 1.1.0 precedent includes Closure Gates that approved misstated verdicts (E-015), so the first 1.2.0 pass of each gate over omn-documentation evidence must be an explicit human decision. No precedent is carried forward." That acceptance exists in no run artifact; this proposal is its record.

## Verification

Commands marked as run by the operator were run from the repository root of this worktree, or, where they mutate the run they select, on a temporary copy of the tree. The rows marked as re-run while authoring were re-run from the repository root and returned what is shown.

| Check | Command | Result |
|---|---|---|
| Regression tests | `python -m unittest tests.test_release_verdict` | 29 tests, 24 failing on an unmodified HEAD copy and all 29 passing after (`T-001`, `T-002`, Fix Gate). Re-run while authoring with `PYTHONPATH=.`: 29/29 OK |
| Bundle parity | `python tests/test_bundled_payload.py` | 11/11 with `PYTHONPATH=.`; re-run while authoring: OK |
| Superseded notes re-validated | `python .claude/runtime/release_note_validator.py <note> --envelope <its invocation-envelope.json>` | Re-run while authoring over all 10 committed notes: the 9 below fail exactly `R8` and `R9`, 32 of 34; the run-c9fb8d5bbb32 attempt-2 note passes 34 of 34 |
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 8/8 COVERED, 37 of 37 phases dispatchable (operator, and re-run while authoring) |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass from the repository root; 6/6 COVERED, `V3` reports 9 release-note candidates produced under a superseded contract and validates the release note on a committed 1.2.0 run artifact, 34 of 34 (operator, and re-run while authoring). The same command run from `.claude/` or `.claude/runtime/` returns 5/6, `V3` failing on the FC-020 `F7` scope rows; this reproduces on a pristine `git archive` of HEAD, so it is pre-existing and explains the implementer's `T-011` and `R-003` and the closure record's `Q-003` (`O-002`) |
| Manifest and contract shape | `python .claude/runtime/verify_manifests.py` | pass; 2/2 CONFORMS (operator, and re-run while authoring) |
| Vertical slice | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, on a temporary copy of the tree (operator) |
| Multi-phase state machine | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15, on a temporary copy of the tree (operator) |
| Recovery | `python .claude/runtime/verify_recovery.py` | 73/74 on a temporary copy of the tree (operator); the one failure, `X1`, is pre-existing: a placeholder in `FE-run-d8870619db82-execution-planning-01` |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | Before this proposal existed, `S8` listed `run-f94564cb61ce` and `run-5df08e171670`; with it, see the result recorded under `FR-05` |
| Unit suite | `python tools/run_tests_parallel.py` | 768 tests; the only failures are the 3 in `tests/test_demo_capture.py`, from ffmpeg 9.0.2 (FC-020 `O-005`), per the regression-validation report of the run (omn-qa). Not re-run while authoring |
| Post-repair check with a real agent | inspection of the knowledge run's documentation phase, invocation `inv-c9fb8d5bbb32-06-002` | omn-documentation 1.2.0, reading its contract from this worktree, completed `documentation-and-release-handoff` through `framework_runtime` with `handed-off`, 34 of 34, `R1`, `R8`, `R9` and `C3.2` passing. That run is FC-022's and is not linked as evidence of this one |
| Knowledge harvest at aggregation | inspection of `runs/run-f94564cb61ce/knowledge-harvest.json` | 26 runs scanned, 42 lessons, 3 created, 1 updated, store written, 0.118 s. The lesson store is FC-022's surface, not this change's |
| Run metrics | inspection of `runs/run-f94564cb61ce/execution-metrics.json` | wall clock 1h56m46s, agent-active 1h31m10s; invocations by tier 1 light, 2 standard, 2 deep, 0 untiered, non-deep share 60 percent; 0 lessons hydrated. One run of one defect, not a controlled comparison |

The 9 superseded notes, each re-validated against its own committed invocation envelope under the corrected validator (`AC-011`). Every one fails exactly `R8` and `R9`, and none was edited:

| Run | Phase | Recorded verdict | Recorded agent version | Fails | Expected position (`R9`) |
|---|---|---|---|---|---|
| `run-4c51600606df` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-8f8a1ab0d16e` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-919c5d5cf156` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-ae91e085f481` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-ded114f50a46` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-e0dba6763475` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-efe092286625` | `documentation-and-release-handoff` | released | 1.0.0 | `R8`, `R9` | handed-off |
| `run-09099de97613` | `documentation-and-release-handoff` | partial | 1.0.0 | `R8`, `R9` | handed-off |
| `run-437e2f765e4b` | `publication` | partial | 1.1.0 | `R8`, `R9` | findings-published |

Eight notes are expected at `handed-off` and `run-437e2f765e4b` at `findings-published`. No Closure Gate decision is reopened; the failures are documentary. This change closes FC-020 `O-006`: a findings publication now has the position `findings-published`, and the `partial` placeholder in the release note of `run-437e2f765e4b` is identified as superseded rather than relabelled.

The review's `CR-003` correction, carried here (closure record `Q-002`): the identifier `CR-003` names two things in this session. The one carried here is the Fix Gate review's `CR-003`, the superseded-count monitoring wording. The knowledge run's `CR-003`, the BackwardCompatibilityTestCase pins, landed first under the omn-tech-lead `Q-005` ruling and belongs to FC-022. The corrected wording: a note produced at 1.2.0 that fails validation fails `V3`, and is never counted as superseded. The superseded count grows only from runtimes that record an omn-documentation version below 1.2.0 in the envelope; it does not grow from agents that read old contract text. The mitigation in the implementation report's `R-001` and the monitoring line in the regression-validation report are corrected accordingly. Until a 1.2.0 note was committed, `V3` validated the release note against `runtime/fixtures/release-note.md`, with no envelope and `R9` not machine-checkable. The run-c9fb8d5bbb32 attempt-2 note is now a committed 1.2.0 instance, and `V3` validates it.

## Risk and Rollback

- Blast radius: the 13 framework files listed in Scope Classification, one test file and the bundled mirror. The release-note validator and the validator coverage verifier change what the Validation Engine accepts for `release-note.md` in all five omn-documentation phases. No function of `runtime/framework_runtime.py` and no workflow changed, and `schemaVersion` stays 1.0.0.
- Risk assessment: `R-001`: no runtime exercise of `findings-published` (investigate, research) or `delta-published` (review-pull-request) yet; only `handed-off` has been exercised end to end (`O-004`). `R-002`: the 1.2.0 bump resets gate auto-approval precedent for omn-documentation evidence. omn-tech-lead accepted this as intended, and the first 1.2.0 pass of each gate must be an explicit human decision (`O-006`). `R-003`: `R9` cannot be decided on a bare command-line run without an envelope, where it is declared not-machine-checkable (`O-005`). `R-004`: registered subagents may read the main checkout's contract text (FC-020 `O-007`); this was mitigated in this session by pointing agents at worktree paths (`O-003`). `R-005`: the release phase is stricter in one respect: a deployment verdict now needs a `deployment-status` entry among `sourceInputs` (`R8`).
- Rollback procedure: revert the 13 framework files and the test file, run `PYTHONPATH=. python tests/test_bundled_payload.py --sync` and confirm `python tests/test_bundled_payload.py` passes, and return omn-documentation and the release-note template to 1.1.0 in the manifest, the host registration and both registry records. No committed run evidence is edited by a revert. Reverting does invalidate one piece of evidence: the run-c9fb8d5bbb32 attempt-2 note, recorded as `handed-off` at 1.2.0, would fail `R1` under the reverted validator, so FC-022's documentation phase would no longer re-validate. Revert this change only together with, or after, a decision on FC-022.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED from the repository root, 9 superseded notes reported; 5/6 from `.claude/` or `.claude/runtime/`, a pre-existing cwd-dependent result (`O-002`) |
| `FR-03` | Recovery behaviour | fail | 73/74 on a temporary copy; `X1` pre-existing (placeholder in `FE-run-d8870619db82-execution-planning-01`); no failure introduced by this change |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238` 10/10 PROVEN on a temporary copy |
| `FR-05` | Self-hosting governance resolves | fail | `S6` and `S7` pass with this proposal; `S8` fails only on `run-5df08e171670`, a pre-existing older run without a proposal (FC-020 `O-009`, `O-010` here) |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-f94564cb61ce` is a `/bugfix` run over `fix-bug`, all five phases completed and all four gates decided; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | `RUNTIME_VERSION` is unchanged by this fix. It moves from 0.9.0 to 0.10.0 under FC-022, for FC-022's runtime change. This fix changes no runtime function, but it does change artifact acceptance through `runtime/release_note_validator.py` and the instance selection of `runtime/verify_validators.py`. Those changes are versioned by omn-documentation 1.2.0 and release-note template 1.2.0, not by `RUNTIME_VERSION` |
| `FR-08` | Documentation matches delivered behaviour | pass | The contract modules, the template, both registry descriptions and the `runtime/README.md` validator table and paragraph describe the five phases and their positions |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row is a command output, a cited artifact or an operator observation marked as such. This record discloses that `findings-published` and `delta-published` are unexercised end to end, that `R9` is undecidable without an envelope, the cwd-dependent verifier result, the pre-existing recovery `X1`, the 3 independent unit-suite failures and the pre-existing `S8` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 on a temporary copy |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | The consumer-visible effect is that an omn-documentation phase without a deployment step now publishes `handed-off`, `findings-published` or `delta-published` instead of blocking or misstating `released`. The release-note template, the runtime README and this proposal state it; no separate release note was drafted |

`FR-03` and `FR-05` are reported as failures as the commands returned them; neither failure is caused by this change.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | Pre-existing runtime defect (`ES-002`): `run_completed` is emitted in the same second the Closure Gate escalation opens, before any decision. Seen in run-c9fb8d5bbb32 (`E-0076`, `E-0078` before `E-0079`), run-5d3c99aaaae1 (`E-0051`, `E-0053` before `E-0054`), run-efe092286625 (`E-0088`, `E-0090` before `E-0091`), run-ded114f50a46 (`E-0070`, `E-0072` before `E-0073`), and in this run (`E-0051`, `E-0053`, with the Closure Gate still undecided) | omn-tech-lead | Open. A follow-up session has been proposed |
| `O-002` | `verify_validators.py` returns a cwd-dependent result: 6/6 COVERED from the repository root, 5/6 from `.claude/` or `.claude/runtime/`, where `V3` fails on the FC-020 `F7` scope rows. This reproduces on a pristine `git archive` of HEAD, and it explains the implementer's `T-011`/`R-003` and the closure record's `Q-003` | omn-qa | Open, pre-existing |
| `O-003` | FC-020 `O-007`: registered subagents may read contract text from the main checkout, not the worktree | omn-qa | Open. Mitigated in this session by pointing agents at worktree paths; the 1.2.0 attempt read this worktree's contract |
| `O-004` | No end-to-end runtime exercise of `findings-published` (investigate `publication`, research `findings-publication`) or `delta-published` (review-pull-request `documentation-impact`) yet | omn-qa | Open. Exercise on the first run of each workflow under 1.2.0 |
| `O-005` | `R9` is declared not-machine-checkable on a bare command-line run without an envelope, so a hand validation can accept a wrong basis (closure `FU-005`) | omn-qa | Open, accepted as low |
| `O-006` | `R-002`: the 1.2.0 bump resets gate auto-approval precedent keyed on the producing-agent version | omn-tech-lead | Accepted by omn-tech-lead; no precedent is carried forward, and the first 1.2.0 pass of each gate over omn-documentation evidence is an explicit human decision |
| `O-007` | The Closure Gate of `run-f94564cb61ce` is undecided. The closure record is `held`, provisional, with its `Q-001` to `Q-004` and `ES-002` open | omn-documentation | Closed. Approved by omn-documentation at 2026-10-17T06:10:45Z (`E-0054`); the Closure Gate row and the Sign-off are updated |
| `O-008` | Monitoring after landing (closure `FU-004`, corrected per the review's `CR-003`): new notes with a deployment verdict and no `deployment-status` input (expect 0); omn-documentation phases ending blocked on `R1`, `R8` or `R9` where evidence is present (expect 0); the superseded count, expected to stay at 9 and to grow only from a runtime that records an omn-documentation version below 1.2.0 | omn-documentation | Open |
| `O-009` | FC-020 `O-006`: the documentation contract had no verdict for a findings publication | architect | Closed by this change: `findings-published` on the `findings` basis; the `run-437e2f765e4b` note is reported as superseded, not edited |
| `O-010` | `S8` fails on `run-5df08e171670`, an older run without a proposal (FC-020 `O-009`) | omn-orchestrator | Open, pre-existing |
| `O-011` | `DF-001`: ffmpeg 9.0.2 rejects the `filter_complex_script` option used by `runtime/demo/editor.py`, failing 3 tests in `tests/test_demo_capture.py` (FC-020 `O-005`) | omn-tech-lead | Open, independent of this change |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification Gates and omn-documentation at the Closure Gate, each an independently dispatched subagent recorded by the session operator, none of them the producer of the evidence it decided
- Acceptance basis: all five phases of the routed workflow executed by host-dispatched subagents and accepted by their registered validators; all four gates approved with producer exclusion held; the defect witnessed by 29 tests, 24 of which fail before the fix; the 9 superseded notes re-validated against their own envelopes as predicted and left as recorded; a real-agent run at 1.2.0 completing with `handed-off`; the verifier results reported as returned, including the pre-existing recovery `X1`, the cwd-dependent verifier result, the 3 independent unit-suite failures and the pre-existing `S8`; and eleven open items recorded with an owner
