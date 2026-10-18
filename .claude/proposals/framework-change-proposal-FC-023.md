# Framework Change Proposal: Store the lessons as an Open Knowledge Format v0.2 bundle

```yaml
frameworkChangeProposal:
  proposalId: FC-023
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-79276e78d773
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-023
- Change title: Store the lessons as an Open Knowledge Format v0.2 bundle
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-79276e78d773
- Authored on: 2026-10-17

## Authoring Baseline

- Authored at: 2026-10-17T14:10:00Z
- Runtime version: 0.11.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

## Change Statement

- Objective: replace the private JSON lesson store of FC-022, `memory/lessons/lessons.store.json`, with a bundle in the Open Knowledge Format v0.2 (specification: https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md), so that the framework's learned knowledge can be read as documents, consumed by other tools, and traced to its origin and trust (`runs/inputs/okf-lessons-feature-request.md`, `runs/inputs/okf-lessons-business-intent.md`). The bundle lives at `memory/lessons/`. It holds a root `index.md` whose only frontmatter key is `okf_version: "0.2"`, a `log.md` of `## YYYY-MM-DD` groups newest first, and one concept document `L-<10 hex>.md` per lesson. Each document's frontmatter carries a non-empty `type`, `title`, `description` and `tags`; `sources` naming the run events and artifacts the lesson was harvested from; `generated` with `by: knowledge-loop/1.0.0` and `at` the lesson's last sighting; `verified` as a `human:<id>` entry only when governance history records an approval; `status` mapped from governance (candidate to draft, approved to stable, retired to deprecated); `stale_after` only for a retained lesson; and the full closed field list of the lesson record under the producer extension key `lesson_record`. Timestamps are ISO 8601 with a `Z` UTC offset. A new standard-library module `runtime/okf.py` writes and parses the YAML subset the bundle uses and implements the OKF section 11 conformance rules (`OKF-11.1`, `OKF-11.2`, `OKF-11.3-index`, `OKF-11.3-log`); `runtime/verify_okf_bundle.py` applies them and is the new advisory release checklist item `FR-13`. `runtime/knowledge.py` keeps the dict interface of `load_store` and `write_store`, so harvest, governance, recall, effectiveness and aggregation are unchanged callers; writes are per document, atomic, and skip unchanged bytes, with `index.md` written last. A `migrate` subcommand converts a JSON store; a checkout holding only the JSON store raises `store-migration-pending` until it is migrated. `render_section` receives the same records as before, so the dispatched lesson text, including the `CR-005` neutralisation of FC-022, is byte-identical. The 43 lessons were migrated with their identifiers, fields and governance history, and the JSON store was removed by the verified migration. `RUNTIME_VERSION` moves from 0.10.0 to 0.11.0 because the store format read and written at dispatch and aggregation changed. The change set is `C-001` to `C-069` of implementation report IR-2026-1014 plus two post-review corrections, `CR-001` and `CR-003`, recorded under Gate Decisions. The bundled mirror was refreshed by its sync procedure.
- In scope: the two new runtime modules; the changes to `runtime/knowledge.py`, `runtime/framework_runtime.py` and `runtime/optimize_memory.py`; the new checklist item in `validation/framework-release-checklist.md`; the four documents `config/runtime.md`, `memory/README.md`, `memory/memory-governance.md` and `memory/memory-resolver.md`; the migrated bundle under `memory/lessons/` and the removal of the JSON store; the payload exclusion in `omn_agent/source.py`; the new test module `tests/test_okf_bundle.py` and the changes to `tests/test_knowledge.py`; the bundled mirror of the changed framework files; and the run `run-79276e78d773` over the `implement-feature` workflow with this governance record.
- Out of scope: converting any other `memory/` document to OKF; publishing the bundle outside the repository or shipping it to installed copies; changing which lessons are harvested, when they become eligible, or how they are ranked; every artifact validator, every Phase Model table and every agent module text; any edit of past run evidence.
- Acceptance basis: the routed run planned through the framework with all six phases executed by host-dispatched subagents and accepted by their registered validators; every gate decided by a non-producing owner; acceptance criteria `A-001` to `A-024` mapped to executed tests; the bundle passing the deterministic section 11 check with zero findings; an independent review whose blocking finding was corrected and re-verified; and the standalone verifiers reported as they returned.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/okf.py` | `SR-1` | in-scope | New module: deterministic YAML-subset writer and parser, OKF section 11 conformance rules |
| `.claude/runtime/verify_okf_bundle.py` | `SR-1` | in-scope | New verifier: checks `memory/lessons` by default; exit 0 pass or absent, 1 fail, 2 missing explicit path |
| `.claude/runtime/knowledge.py` | `SR-1` | in-scope | Bundle read and write behind the unchanged `load_store` and `write_store` interface, lock `memory/lessons/lessons.lock`, `migrate` subcommand; `CR-001` correction in `migrate` |
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | `RUNTIME_VERSION` 0.11.0 |
| `.claude/runtime/optimize_memory.py` | `SR-1` | in-scope | Denies the bundle; `CR-003` correction matches the path relative to the framework root |
| `.claude/validation/framework-release-checklist.md` | `SR-1` | in-scope | New advisory item `FR-13`, owner omn-qa |
| `.claude/config/runtime.md` | `SR-1` | in-scope | Lessons subsection describes the bundle |
| `.claude/memory/README.md` | `SR-1` | in-scope | Lesson category describes the bundle |
| `.claude/memory/memory-governance.md` | `SR-1` | in-scope | Status mapping, `verified` and `stale_after` rules |
| `.claude/memory/memory-resolver.md` | `SR-1` | in-scope | Resolution reads the bundle |
| `.claude/memory/lessons/index.md` | `SR-1` | in-scope | New reserved file, `okf_version: "0.2"` |
| `.claude/memory/lessons/log.md` | `SR-1` | in-scope | New reserved file, change log |
| `.claude/memory/lessons/L-9b5801a992.md` | `SR-1` | in-scope | One of the 43 migrated concept documents `L-*.md`; the others sit beside it under the same rule |
| `.claude/memory/lessons/lessons.store.json` | `SR-1` | in-scope | Removed by the verified migration |
| `omn_agent/source.py` | no rule | out-of-scope | Outside the framework surface; `memory/lessons` excluded from the installed payload by relative path, `lessons.store.*` pattern retired |
| `tests/test_okf_bundle.py` | no rule | out-of-scope | Outside the framework surface; new module, 31 tests |
| `tests/test_knowledge.py` | no rule | out-of-scope | Outside the framework surface; updated for the bundle, 52 tests |
| `omn_agent/_bundled_payload/**` | no rule | out-of-scope | Outside the framework surface; mirrors of the changed framework files, refreshed by the sync procedure, never hand-edited; holds no `memory/lessons` file |
| `.claude/runs/run-79276e78d773/**` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |
| `.claude/runs/inputs/okf-lessons-feature-request.md` | `SR-3` | out-of-scope | Supplied `feature-request` input; the `change-request`, `business-intent` and `architecture-context` inputs sit beside it under the same rule |
| `.claude/proposals/framework-change-proposal-FC-023.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

The scope paths were checked against `git status` and `git diff --stat`. Under `.claude/`, 9 tracked framework paths are modified, 1 is deleted (the JSON store), and 47 framework paths are new (2 runtime modules, 2 reserved bundle files, 43 lesson documents). Under `omn_agent/`, `source.py` and 8 mirror paths are modified and 2 mirror paths are new. No path of another change is claimed.

Reconciliation with the base branch, after the run closed. The base branch meanwhile deleted the `omn_agent` package (its installer, payload exclusion and bundled mirror) and renamed the agents from `omn-<role>` to `<role>`. Merging it into this change therefore dropped the `omn_agent/` rows above: the installer exclusion and the mirror no longer exist, so `tests/test_knowledge.py` loses its two installer-exclusion tests (52 to 50) and `tests/test_bundled_payload.py` is gone. The bundle's `owner` fields were rewritten from `omn-tech-lead` to `tech-lead` through `write_store`, matching the base branch's rename of the JSON store, and the bundle still conforms with zero findings. FR-13's owner is `qa`. `runtime/verify_okf_bundle.py` now ends with the `N/N checks passed -- <verdict>` summary line that the base branch's CI requires of every discovered verifier. Run evidence and the role names quoted from it are left as recorded.

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework gains a capability it did not have: its lessons become a conformant, portable knowledge bundle with stated provenance and trust, and a deterministic conformance check.
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`, `change-request`, `business-intent`, `architecture-context`
- Classification evidence: `python .claude/runtime/self_hosting.py classify --path <path>` was run over every row of the table above and returned `SR-1` in scope with the verdict "framework-internal change" for the framework paths, no rule and out of scope for `omn_agent/source.py` and the test modules, `SR-3` out of scope for the run evidence and the input, and `SR-5` out of scope for this proposal. `python .claude/runtime/self_hosting.py route --intent capability-addition` returns `/implement` over `implement-feature v1.0.0` at `scope-and-acceptance` of 6, with inputs `feature-request`, `change-request`, `business-intent`, `architecture-context`.

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-79276e78d773/execution-request.json` | resolved; routed through `/implement` over `implement-feature` v1.0.0, four inputs recorded with their digests, planned at runtime 0.10.0 |
| `E-2` | `runs/run-79276e78d773/run-ledger.json` | resolved; 6 phases, run status Completed |
| `E-3` | `runs/run-79276e78d773/events.jsonl` | resolved; 87 events from `run_initialized` to the final `run_completed` |
| `E-4` | `runs/run-79276e78d773/state.json` | resolved; 6 phases completed, 0 blocked, 0 failed, 48 transitions, 0 replays suppressed, six gate decisions with rationale |
| `E-5` | `runs/run-79276e78d773/completion-package.md` | resolved; aggregated for 6 of 6 completed phases |
| `E-6` | `runs/run-79276e78d773/states/scope-and-acceptance/artifacts/scope-definition.md` | resolved; 18 scope items, 7 exclusions, `A-001` to `A-024` |
| `E-6` | `runs/run-79276e78d773/states/execution-planning/artifacts/execution-plan.md` | resolved; the accepted plan, `T-001` to `T-039` |
| `E-6` | `runs/run-79276e78d773/states/solution-design-and-risk-assessment/artifacts/technical-design.md` | resolved; option `O-002` selected (a lesson-agnostic OKF module beside the knowledge module) |
| `E-6` | `runs/run-79276e78d773/states/solution-design-and-risk-assessment/artifacts/architecture-decision-record-D-001.md` | resolved; one of six decision records `D-001` to `D-006`, accepted at the Design Gate |
| `E-6` | `runs/run-79276e78d773/states/implementation/artifacts/implementation-report.md` | resolved; IR-2026-1014, change set `C-001` to `C-069` |
| `E-6` | `runs/run-79276e78d773/states/quality-review/artifacts/review-package.md` | resolved; RP-2026-0011, verdict approve-with-corrections, findings `F-001` (high), `F-002` and `F-003` (low) |
| `E-6` | `runs/run-79276e78d773/states/documentation-and-release-handoff/artifacts/release-note.md` | resolved; verdict handed-off, status provisional, known issues `K-001` to `K-007` |
| `E-7` | `runs/run-79276e78d773/states/scope-and-acceptance/validation-report.json` | resolved; 33 of 33 |
| `E-7` | `runs/run-79276e78d773/states/execution-planning/validation-report.json` | resolved; 45 of 45 |
| `E-7` | `runs/run-79276e78d773/states/solution-design-and-risk-assessment/validation-report.json` | resolved; 78 of 78 |
| `E-7` | `runs/run-79276e78d773/states/implementation/validation-report.json` | resolved; 32 of 32 |
| `E-7` | `runs/run-79276e78d773/states/quality-review/validation-report.json` | resolved; 31 of 31 |
| `E-7` | `runs/run-79276e78d773/states/documentation-and-release-handoff/validation-report.json` | resolved; 34 of 34 |
| `E-8` | `runs/run-79276e78d773/recovery-ledger.json` | resolved; 3 charged `output-schema-failure` retries and the gate-approval waits, all resolved |
| `E-8` | `runs/run-79276e78d773/execution-metrics.json` | resolved; the metrics cited under Verification |
| `E-8` | `runs/run-79276e78d773/knowledge-harvest.json` | resolved; the run's own aggregation harvested into the bundle with no operator command: status succeeded, 27 runs scanned, 78 occurrences, 43 lessons, bundle unchanged |
| `E-8` | `runs/run-79276e78d773/final-report.md` | resolved; who did what and when, including gate wait times |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed in 2 attempts. Attempt 1 was rejected on `SD4` (an escaped pipe broke a table row), classified `output-schema-failure`, and retried; attempt 2 validated 33 of 33 | `omn-product-owner` subagent, dispatched by the host | `runs/run-79276e78d773/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed in 2 attempts. Attempt 1 was rejected on `V4.1` and `V4.8` (tasks with fewer than two acceptance criteria) and retried; attempt 2, promoted to tier deep by the escalation rule, validated 45 of 45 | `planner` subagent, dispatched by the host | `runs/run-79276e78d773/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed in 2 attempts. Attempt 1 was rejected on `D4.3` (an untraced acceptance bullet) and retried; attempt 2 validated 78 of 78; technical design and decision records `D-001` to `D-006` | `architect` subagent, dispatched by the host | `runs/run-79276e78d773/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed; validated 32 of 32 on the first attempt; change set `C-001` to `C-069`. The post-review corrections `CR-001` and `CR-003` were made after this phase completed and are recorded under Gate Decisions | `omn-dev-1-implement` subagent v1.1.0, dispatched by the host | `runs/run-79276e78d773/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed; validated 31 of 31 on the first attempt; verdict approve-with-corrections, 1 high and 2 low findings | `omn-dev-2-reviewer` subagent v1.1.0, dispatched by the host | `runs/run-79276e78d773/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed; validated 34 of 34 on the first attempt; verdict handed-off, status provisional because the post-review corrections are recorded in gate records and this proposal, not in an artifact it received | `omn-documentation` subagent v1.2.0, dispatched by the host | `runs/run-79276e78d773/states/documentation-and-release-handoff/validation-report.json` |

Exact runtime statuses were read from `python .claude/runtime/framework_runtime.py status --run-id run-79276e78d773`: 6 completed, 0 blocked, 0 failed, 0 pending, six gates completed, run status Completed, 48 transitions, 87 events, 0 replays suppressed. Every phase was executed by a host-dispatched subagent; the operator performed no phase's work.

The run was planned at runtime 0.10.0 with the knowledge loop on. Its dispatches hydrated 18 lessons in total, and every aggregation harvested. The store is not frozen while a run is in flight, which is why the scope fixed the lesson count at migration time (43) and excluded the carrying run from the migration-count criterion.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | `omn-business-analyst subagent a571b7e63bb7c98ac, recorded by session operator for vuhoangcao` | Scope bounded with acceptance criteria `A-001` to `A-024` each with a verification method; validator 33 of 33. Rulings: frontmatter is derived mechanically from the lesson record; `generated.at` is the last sighting; the `stale_after` rule is the architect's to set; a `Z` suffix satisfies the UTC-offset requirement; the rendered prompt section carries no timestamp |
| Planning Gate | approve | omn-tech-lead | `omn-tech-lead subagent ac059d1a8684013e1, recorded by session operator for vuhoangcao` | Every task has at least two criteria and a gate. Rulings: the bundle lives at `memory/lessons`; installer and optimiser exclusion is by relative path; the conformance item is advisory so recorded proposals stay valid; `RUNTIME_VERSION` becomes 0.11.0; `T-025`, `T-026`, `T-027` and `T-013` land as one change |
| Design Gate | approve | omn-tech-lead | `omn-tech-lead subagent a4d823ed9c79d02bc, recorded by session operator for vuhoangcao` | Option `O-002` and `D-001` to `D-006` accepted. A process-actor `verified` entry was ruled out, because it would make the bundle bytes depend on the eligibility threshold. Binding conditions: the rendered section is byte-identical; a second write is byte-identical; tests use temporary roots; no edit under `runs/` except evidence the runtime writes; the exclusion lands before any bundle exists; the JSON store is removed only by a verified migration; the knowledge change set is frozen |
| Review Gate | approve | omn-qa | `omn-qa subagent aa2b26c926605097c, recorded by session operator for vuhoangcao` | Blocking correction `CR-001` is closed: migrate treats an existing bundle as authoritative, refuses with `migration-mismatch` and writes nothing when the bundle holds lessons or records the JSON store lacks or differs on, with tests for both cases. `CR-003` is closed and `CR-002` stays a non-blocking improvement owned by the architect |
| Verification Gate | approve | omn-qa | `omn-qa subagent aa2b26c926605097c, recorded by session operator for vuhoangcao` | Re-run from the repository root on the corrected tree: `tests/test_okf_bundle.py` 31 OK, `tests/test_knowledge.py` 52 OK, `tests/test_bundled_payload.py` 11 OK, `tests/test_optimize_memory.py` 31 OK, and the bundle verifier passed over 43 documents with zero findings. No past run evidence is modified |
| Closure Gate | approve | omn-orchestrator | `omn-orchestrator subagent a22525a88ae5e6723, recorded by session operator for vuhoangcao` | All six phases complete and every upstream gate approved by a non-producing owner. The only high finding `F-001` was closed through `CR-001` with a passing re-run; the release note is provisional only because that evidence lives in gate records and this proposal. Open items `CR-002` and `Q-002` are non-blocking and owned |

Every gate the workflow declares was decided, none was waived, and no gate was decided by the agent that produced its evidence. Each gate first blocked with `awaiting_human_decision` and was resolved in place; the Decided By column quotes the recorded `decided_by` strings, and the rationales are condensed from `state.json`.

Post-review corrections. The records below exist in no run artifact other than the gate rationales; they are transcribed here so the record survives the session.

- `CR-001` (for `F-001`, high): omn-dev-1-implement subagent `af6b7af53ba0bed24`, an operator-dispatched post-review correction. Before the correction, `migrate` with both the JSON store and a bundle present could overwrite bundle-only lessons or governance history. Now the bundle is authoritative: `migrate` raises `migration-mismatch` and writes nothing when the bundle holds a lesson or a record that the JSON store lacks or differs on, keeps the JSON store, and completes only when the bundle is a partial, equal copy. Tested by `MigrationTestCase.test_migrate_with_both_forms_never_overwrites_the_bundle` and `MigrationTestCase.test_migrate_completes_a_bundle_that_is_a_partial_copy` in `tests/test_okf_bundle.py`, through the Python call and the command line (exit 2).
- `CR-003` (for `F-003`, low): the same subagent. The optimiser's `memory/lessons` denial now matches the path relative to the framework root through `_framework_parts`, so an ancestor directory pair named `memory/lessons` no longer denies unrelated files. Tested by `OptimizerIsolationTestCase.test_the_bundle_denial_ignores_an_ancestor_memory_lessons_pair` in `tests/test_knowledge.py`.
- `CR-002` (for `F-002`, low): not corrected. The verifier reports valid YAML outside the writer's subset as unparseable without saying so. Carried as `O-001`.
- No scoped re-review by omn-dev-2-reviewer was run; omn-qa inspected both corrections in the code and re-executed the suites at the Review and Verification Gates.

## Verification

All commands were run from the repository root of this working tree with `PYTHONPATH=.` and the temporary directory on a drive with free space. Commands that mutate committed run evidence were run on a temporary copy of the final tree.

| Check | Command | Result |
|---|---|---|
| OKF bundle tests | `python tests/test_okf_bundle.py` | 31 of 31, by omn-qa at the Verification Gate and by the implementer after the corrections |
| Knowledge loop tests | `python tests/test_knowledge.py` | 52 of 52, by omn-qa and by the implementer |
| Optimiser tests | `python tests/test_optimize_memory.py` | 31 of 31, by omn-qa and by the implementer |
| Bundled payload parity | `python tests/test_bundled_payload.py` | 11 of 11, by omn-qa and by the implementer; mirror synced with `--sync` before commit |
| OKF section 11 conformance | `python .claude/runtime/verify_okf_bundle.py` | pass; 43 documents, 2 reserved files, 0 findings |
| Dispatched lesson text | inspection of implementation `T-` evidence and the `render_section` byte-identity tests | identical bytes for the same records before and after the change, including the `CR-005` neutralisation |
| Release checklist | `python .claude/runtime/verify_self_hosting.py --release-checklist` | Run on a temporary copy of the final tree, because `FR-03`, `FR-04` and `FR-11` mutate committed run evidence in place. 7/9 NOT SELF-HOSTING: `S1` to `S7` pass, with `S6` accepting FC-001 to FC-023 (FC-023 38 of 38); `S8` fails only on the pre-existing `run-5df08e171670`; `S10` fails on `FR-03`, `FR-05` and `FR-06`, all for those pre-existing causes. Executed items: `FR-01` 8/8, `FR-02` 6/6, `FR-04` 10/10, `FR-11` 15/15, `FR-13` 0 findings pass; `FR-03` 73/74 (`X1`), `FR-05` and `FR-06` 7/8 (`S8`) fail |
| Unit suite | `python tools/run_tests_parallel.py` | 802 of 802 tests ran, 29 of 30 modules pass, run by the operator on the final tree. The only failing module is `tests/test_demo_capture.py`, whose end-to-end tests fail because ffmpeg 9.0.2 rejects `-filter_complex_script`, the same failure recorded before this change (`O-005`). `test_okf_bundle` 31, `test_knowledge` 52, `test_optimize_memory` 31 and `test_bundled_payload` 11 pass |
| Run metrics | inspection of `runs/run-79276e78d773/execution-metrics.json` | Wall clock 2h52m54s, agent-active 2h07m38s; 9 invocations of 6 agents; by tier 2 light, 2 standard, 5 deep, non-deep share 44 percent; validation runs 6 passed and 3 failed; 6 gate decisions, 0 automatic; 18 lessons hydrated. One run, not a controlled comparison |

## Risk and Rollback

- Blast radius: the framework files listed in Scope Classification, the 45 bundle files, `omn_agent/source.py`, two test modules, and the bundled mirror. The lesson store format read and written at dispatch and aggregation changes; the dispatched text does not. `RUNTIME_VERSION` moves to 0.11.0.
- Risk assessment: a checkout that still holds only a 0.10.0 JSON store raises `store-migration-pending` at every knowledge-loop read until `python .claude/runtime/knowledge.py migrate` is run once (release note breaking change; `Q-002` asks whether any installed copy can hold one; the store was never shipped to installed copies). Per-document files replace one store file, so concurrent branches now conflict per lesson rather than on one file, and the index and log must be regenerated on merge rather than hand-merged (carried from FC-022, its open item on concurrent store rewrites). The YAML subset is narrow by design; a hand edit outside it is reported as unparseable (`CR-002`).
- Rollback procedure: revert the commit that carries this change; that restores `runtime/knowledge.py` 0.10.0 behaviour and the JSON store as committed at FC-022, removes `runtime/okf.py`, `runtime/verify_okf_bundle.py`, `FR-13` and the bundle, returns `RUNTIME_VERSION` to 0.10.0, and then requires `PYTHONPATH=. python tests/test_bundled_payload.py --sync`. Lessons harvested or governed after the change would be lost unless first exported from the bundle. Reverting invalidates no committed run evidence other than this run's claim to have carried the change.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 8/8 COVERED; 37 of 37 phases dispatchable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED, run from the repository root |
| `FR-03` | Recovery behaviour | fail | 73/74 on a temporary copy of the final tree; `X1` fails on a placeholder in the pre-existing failure envelope `FE-run-d8870619db82-execution-planning-01`, not caused by this change; `O-006` |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238`: 10/10 PROVEN on a temporary copy of the final tree |
| `FR-05` | Self-hosting governance resolves | fail | 7/8; `S6` accepts FC-023 (38 of 38) and every earlier proposal; `S8` fails only on the pre-existing `run-5df08e171670`; `O-006` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-79276e78d773` is an `/implement` run over `implement-feature`; all six phases completed and all six gates decided; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Moved from 0.10.0 to 0.11.0 because the lesson store read and written at dispatch and aggregation changed format |
| `FR-08` | Documentation matches delivered behaviour | pass | `config/runtime.md` and the three `memory/` documents describe the bundle, the migration and the conformance check; the release note describes the breaking change and its required action. the FC-022 open item on the operator handbook (the operator handbook and `runtime/README.md` do not describe the `knowledge.py` command line) remains open and is not widened by this change |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every Verification row is a command output or a cited record; this proposal discloses `CR-002`, `Q-002`, the provisional release note and the pre-existing failures |
| `FR-10` | Rollback stated | pass | Risk and Rollback above |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 PROVEN on a temporary copy of the final tree |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-79276e78d773/states/documentation-and-release-handoff/artifacts/release-note.md`, verdict handed-off, status provisional |
| `FR-13` | Lesson bundle conforms to OKF v0.2 section 11 | pass | `verify_okf_bundle.py`: 43 documents, 2 reserved files, 0 findings |

`FR-03` and `FR-05` are reported as failures, as the commands returned them; both are pre-existing and neither is caused by this change. `FR-06` is a pass on its own requirement, although the checklist runs the same verifier for it and that verifier fails on `S8` for `run-5df08e171670`.

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | `CR-002` (review `F-002`, low): the verifier reports valid YAML outside the writer's subset as unparseable without naming the subset limit | architect | Open, non-blocking |
| `O-002` | `Q-002`: can any installed copy hold a JSON store written by runtime 0.10.0? The store was excluded from the installed payload since FC-022; `CR-001` now refuses rather than overwrites if one meets a bundle | omn-tech-lead | Open, non-blocking; confirm |
| `O-003` | The release note is provisional because `CR-001` and `CR-003` and their re-run are recorded in gate records and this proposal, not in an artifact the documentation phase received (`K-007`) | omn-documentation | Open. Re-run the note against this proposal to move it to complete; the verdict does not change |
| `O-004` | The index and log use `- ` list markers where the specification's examples use `* `; the reviewer judged both valid list syntax and not a finding | architect | Open, cosmetic |
| `O-005` | `DF-001`: ffmpeg 9.0.2 rejects the `-filter_complex_script` option used by `runtime/demo/editor.py`, failing the end-to-end tests of `tests/test_demo_capture.py` (carried from FC-022) | omn-tech-lead | Open, independent of this change |
| `O-006` | Pre-existing verifier failures carried from FC-022: `X1` in `verify_recovery.py` on a placeholder in `FE-run-d8870619db82-execution-planning-01`, and `S8` on `run-5df08e171670`, an older run without a proposal | omn-orchestrator | Open, pre-existing |
| `O-007` | Operator environment, not the framework: the system drive ran out of space during this run because of large task output files left by other sessions, so subagents ran with the temporary directory on another drive and left scratch directories they could not delete | operator | Open; the files are outside the repository and are left for the user to remove |

## Sign-off

- Proposed by: operator, acting as omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, and omn-orchestrator at the Closure Gate. Each was an independently dispatched subagent whose decision the session operator recorded, and none produced the evidence it decided
- Acceptance basis: all six phases of the routed workflow were executed by host-dispatched subagents and accepted by their registered validators, three after one charged retry each; all six gates were approved with producer exclusion held. The post-review corrections `CR-001` and `CR-003` were confirmed by omn-qa with a passing re-run, and the bundle conforms to OKF v0.2 section 11 with zero findings.
