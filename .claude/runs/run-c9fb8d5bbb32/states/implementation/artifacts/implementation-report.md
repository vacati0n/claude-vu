```yaml
implementationReport:
  reportId: IR-2026-1012
  changeReference: run-c9fb8d5bbb32 -- knowledge management loop (harvest, govern, recall, measure), change request runs/inputs/knowledge-loop-change-request.md
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/knowledge-loop-feature-request.md
    - type: change-request
      reference: runs/inputs/knowledge-loop-change-request.md
    - type: business-intent
      reference: runs/inputs/knowledge-loop-business-intent.md
    - type: architecture-context
      reference: runs/inputs/knowledge-loop-architecture-context.md
    - type: technical-design
      reference: runs/run-c9fb8d5bbb32/states/solution-design-and-risk-assessment/artifacts/technical-design.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: implementation
  verificationStatus: partially-verified
  inputDigest: sha256:d9234f512603ced8267c83f26cbfc66f
  contextDigest: sha256:ef1263786bd989ee336d4b5f33be1ef5
```

## Metadata

- Report ID: IR-2026-1012
- Change reference: run-c9fb8d5bbb32 -- knowledge management loop (harvest, govern, recall, measure), change request runs/inputs/knowledge-loop-change-request.md
- Workflow phase: implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

## Implementation Summary

- Change intent: recorded run evidence (validation_failed check IDs, gate-rejection envelopes of gate work items, with rollback_scheduled events as evidence) is now harvested into a governed, fingerprint-keyed lesson store under memory/lessons/; operators can approve, retire, and annotate lessons from a command line; runs created at runtime 0.10.0 carry a plan-time knowledge_loop record (on by default, off with --no-lesson-hydration) and their dispatches receive up to five matching eligible lessons in memory_slice, a bounded prompt section, and lessons_shown; every aggregation of such a run ends with an isolated harvest; effectiveness and per-invocation hydration counts are reported; runs planned before the change dispatch as under 0.9.0 apart from the closed normalisation list.
- Approach taken: selected option O-001 as accepted (D-001 to D-005, inline D-006 to D-013), in plan order P-002 (0.9.0 baseline captured first, on temporary roots), P-003 (installer exclusion before any store existed), P-004 to P-009, P-010 (four documents only), P-011 (mirror refreshed by its sync procedure), P-012 (tests over temporary roots). Necessity and reuse ladder: one new module runtime/knowledge.py and one policy file config/knowledge-policy.json, each required at the rung where no existing component provides harvest, eligibility, recall selection, or attribution (design reuse survey: none-found) and a separate module is required by D-001's one-way dependency; everything else reuses existing carriers (memory_slice, invocation_started detail, execution-request.json, maybe_aggregate, EXCLUDE_PATTERNS, the state_engine digest helper, the temp-file-and-replace write); no new dependency was introduced (standard library only).
- Design reference: technical design run-c9fb8d5bbb32-knowledge-loop-technical-design (digest sha256:ba0378752796bb8a1cbffe017d809473) and decision records D-001 to D-005, Accepted at the Design Gate with the eight binding conditions relayed in the dispatch; impacted modules M-001 to M-012; scope acceptance criteria A-001 to A-023.
- Out of scope: every context-slice member (runtime/README.md, the registries, memory/architecture.md, the slice's excluded text) is untouched by rule, and a test pins all 45 slice-member digests to the 0.9.0 baseline; state_engine.py, verify_multi_phase.py, optimize_memory.py, every artifact validator, Phase Model tables, and agent module text are unchanged (M-013 to M-020); config/execution-engine.md is not one of the four documents the design names; the change proposal and the release checklist (P-013) belong to later phases. Leaving these is safe because no pre-change dispatch path reads anything new and the payload digest inputs are unchanged.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `tests/fixtures/knowledge/baseline-0.9.0/baseline.json` | added | Record of the 0.9.0 baseline: run id, key, the fields two dispatches of one invocation differed in, invocation_started detail, guarded slice-member digests | P-002, D-011 |
| `C-002` | `tests/fixtures/knowledge/baseline-0.9.0/dispatch-prompt.md` | added | 0.9.0 dispatch prompt of the baseline invocation | P-002, D-011 |
| `C-003` | `tests/fixtures/knowledge/baseline-0.9.0/dispatch-stdout.txt` | added | 0.9.0 dispatch console output of the baseline invocation | P-002, D-011 |
| `C-004` | `tests/fixtures/knowledge/baseline-0.9.0/envelope.json` | added | 0.9.0 invocation envelope of the baseline invocation | P-002, D-011 |
| `C-005` | `tests/fixtures/knowledge/baseline-0.9.0/pre-change-run/events.jsonl` | added | Pre-dispatch event stream of the pre-change fixture run planned under 0.9.0 | P-002, D-011 |
| `C-006` | `tests/fixtures/knowledge/baseline-0.9.0/pre-change-run/execution-request.json` | added | Pre-change execution request (no knowledge_loop record) | P-002, D-011 |
| `C-007` | `tests/fixtures/knowledge/baseline-0.9.0/pre-change-run/state.json` | added | Pre-dispatch state store of the pre-change fixture run | P-002, D-011 |
| `C-008` | `omn_agent/source.py` | modified | Add lessons.store.* to EXCLUDE_PATTERNS so store, lock, and temp file never reach installer, bundle sync, or bundle tests | D-005, M-006, P-003 |
| `C-009` | `config/knowledge-policy.json` | added | Policy: hydration_default on, auto_eligible_distinct_runs 2, default_owner omn-tech-lead | D-010, M-005, P-004 |
| `C-010` | `runtime/knowledge.py` | added | Harvest, canonical store with lock and atomic replace, governance, eligibility, recall, prompt-section rendering, effectiveness report, run-record helpers, isolated post-aggregation step, command line | D-001, D-002, D-007, D-008, D-013, M-001, M-004, P-004 |
| `C-011` | `runtime/framework_runtime.py` | modified | Plan-time knowledge_loop record and --no-lesson-hydration; memory_slice, prompt section, lessons_shown, and console line after payload binding; harvest step last in maybe_aggregate; RUNTIME_VERSION 0.10.0 | D-003, D-004, D-006, D-012, M-002, P-005 to P-009 |
| `C-012` | `runtime/execution_metrics.py` | modified | Per-phase lessons_hydrated and lessons_hydrated_by_invocation, run lessons_hydrated_total | D-009, M-003, P-007 |
| `C-013` | `config/runtime.md` | modified | Lessons subsection under Memory Loading: harvest, store, lifecycle, eligibility, plan-time record, recall, fail-open, aggregation step, measurement | M-008, P-010 |
| `C-014` | `memory/README.md` | modified | Describe the lesson category, lifecycle, threshold, plan flag, and ownership | M-009, P-010 |
| `C-015` | `memory/memory-governance.md` | modified | Lesson lifecycle, ownership, eligibility, hydration record, and the aggregation write trigger | M-010, P-010 |
| `C-016` | `memory/memory-resolver.md` | modified | Lesson category and its per-dispatch resolution and writeback rule | M-011, P-010 |
| `C-017` | `omn_agent/_bundled_payload/config/knowledge-policy.json` | added | Mirror of `C-009` by the sync procedure | M-007, P-011 |
| `C-018` | `omn_agent/_bundled_payload/config/runtime.md` | modified | Mirror of `C-013` by the sync procedure | M-007, P-011 |
| `C-019` | `omn_agent/_bundled_payload/memory/README.md` | modified | Mirror of `C-014` by the sync procedure | M-007, P-011 |
| `C-020` | `omn_agent/_bundled_payload/memory/memory-governance.md` | modified | Mirror of `C-015` by the sync procedure | M-007, P-011 |
| `C-021` | `omn_agent/_bundled_payload/memory/memory-resolver.md` | modified | Mirror of `C-016` by the sync procedure | M-007, P-011 |
| `C-022` | `omn_agent/_bundled_payload/runtime/execution_metrics.py` | modified | Mirror of `C-012` by the sync procedure | M-007, P-011 |
| `C-023` | `omn_agent/_bundled_payload/runtime/framework_runtime.py` | modified | Mirror of `C-011` by the sync procedure | M-007, P-011 |
| `C-024` | `omn_agent/_bundled_payload/runtime/knowledge.py` | added | Mirror of `C-010` by the sync procedure | M-007, P-011 |
| `C-025` | `tests/test_knowledge.py` | added | 47 unit tests over temporary roots covering scope A-001 to A-023 and Design Gate conditions 1 to 8 | M-012, P-012 |
| `C-026` | `memory/lessons/lessons.store.json` | added | Store written by one operator-directed live harvest so it reflects real evidence (39 lessons) | M-004, design Rollout and Rollback (operator seeds the store once) |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Unmodified 0.9.0 baseline: two dispatches of one invocation on two temporary roots; same key; differ only in built_at, context_slice.frozen_at, task_context.digest and its prompt echo; console identical | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007` | python capture_baseline.py . tests/fixtures/knowledge/baseline-0.9.0 (session scratch helper, run before any runtime edit) | pass |
| `T-002` | Regression baseline before any edit and after the exclusion entry: bundle parity, packaging, source fallback with this checkout's package | regression | `C-008` | PYTHONPATH=. python tests/test_bundled_payload.py | pass |
| `T-003` | HarvestRecordedEvidenceTestCase (5): copy of recorded runs yields C3.2 on scope-definition.md over 2 or more runs, C7.1 split by artifact type, gate lessons, all six fields, closed field list | unit | `C-009`, `C-010`, `C-025` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-004` | GateLessonTestCase (1): gate G closing phase P rejected in two runs is one lesson with distinct_runs 2; approval waits and successor envelopes skipped | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-005` | EmptyRootTestCase (1): no runs directory exits 0, reports zero lessons, writes nothing | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-006` | NoEvidenceTextTestCase (1): credential-shaped marker planted in event summaries and details, report details, ledger detail, resolution, actor, and gate rationale is absent from every store file | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-007` | IdempotencyTestCase (4): byte-identical re-harvest; one appended event raises occurrences by one and moves last_seen; vanished evidence retained; legacy run without state counted unresolved | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-008` | GovernanceTestCase (4): approve, annotate, retire change one field and append one entry, survive harvest; unknown lesson, credential-like or over-long remedy leave bytes unchanged; invalid transition refused; held lock fails writers | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-009` | OptimizerIsolationTestCase (1): optimizer discovery skips the store, classifies it not-markdown, bytes unchanged | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-010` | EligibilityTestCase (3): candidate at 1 and 2, active at 1, retired at any count, threshold 3 then 2 from the policy file, unreadable policy is policy-failure, absent policy records off | unit | `C-009`, `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-011` | RenderTestCase (1): remedy line only with a remedy and unchanged; five lessons render at most eleven lines; quotes and backticks neutralised | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-012` | DispatchHydrationTestCase (9): real CLI; record on; seven eligible yield the five highest in tie order; non-matching absent; prompt section, lessons_shown, console line; payload untouched; metrics count 5; flag-off record and reason; flag refused on an on run; fail-open store | integration | `C-009`, `C-010`, `C-011`, `C-012` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-013` | BackwardCompatibilityTestCase (6): pre-change fixture under 0.10.0 equals the 0.9.0 envelope, prompt, console, and event detail after the closed list, same key; flag-off differs only in memory_slice.reason plus lessons_shown in the event; flag refused on a pre-change run; 45 slice-member digests equal baseline; metrics zero | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-011`, `C-012` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-014` | EffectivenessTestCase (1): three shown dispatches and one later recurrence report 3 and 1, plus one unwarned | unit | `C-010` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-015` | AggregationHarvestTestCase (4): aggregation harvest makes a recurrence eligible for the next dispatch with no harvest command; forced harvest exception leaves every aggregation output and console equal to a run without the step and records failed; lock contention records skipped; pre-change run has no step | integration | `C-010`, `C-011` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-016` | PayloadExclusionTestCase (2): store, lock, and temp file absent from enumerate_seeds; bundle holds no store | unit | `C-008`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-017` | ModuleBoundaryTestCase (2): runtime/knowledge.py imports only the standard library and state_engine; execution_metrics.py imports neither runtime nor knowledge | static | `C-010`, `C-012` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-018` | DocumentationTestCase (2): the four documents name lesson, candidate, active, retired, two distinct runs, --no-lesson-hydration; config/runtime.md names fail-open and the policy file; version 0.10.0 | static | `C-011`, `C-013`, `C-014`, `C-015`, `C-016` | PYTHONPATH=. python -W ignore tests/test_knowledge.py | pass |
| `T-019` | Model-tier regression suite (47 tests) on the final tree, live store present | regression | `C-011`, `C-012` | python -W ignore tests/test_model_tier.py | pass |
| `T-020` | Bundle parity after the mirror sync, with this checkout's package (11 tests) | regression | `C-008`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024` | PYTHONPATH=. python tests/test_bundled_payload.py | pass |
| `T-021` | Bundle tests as literally instructed: the tests directory on sys.path resolves the main checkout's installed package, which lacks the new exclusion, so parity drifts on the live store; the source-fallback test also fails, as it did before the change | regression | `C-008` | python tests/test_bundled_payload.py | fail |
| `T-022` | Replay verifier against committed run run-c5a8d50d3238 in place: M0 to M13 pass including M12; M14 fails because a child command hit WinError 5 on os.replace of the tracked state.json (three attempts) | regression | `C-011` | python runtime/verify_multi_phase.py --run-id run-c5a8d50d3238 | fail |
| `T-023` | Same unmodified verifier on temporary copies holding committed run run-c5a8d50d3238: final tree 15/15 with M12 and M14 pass; HEAD 0.9.0 tree 15/15 | regression | `C-011` | python runtime/verify_multi_phase.py --run-id run-c5a8d50d3238 (cwd: temporary copy of the final tree, then of git archive HEAD) | pass |
| `T-024` | Replay verifier with default selection, which chose this in-flight run: 14/15, M12 and M14 pass, M6 fails because the delivery phase is still running | regression | `C-011` | python runtime/verify_multi_phase.py | fail |
| `T-025` | Vertical slice verification (10 checks) | regression | `C-011` | python runtime/verify_vertical_slice.py | pass |
| `T-026` | Registry coverage verification (8 checks) | regression | `C-009`, `C-011` | python runtime/verify_registry_coverage.py | pass |
| `T-027` | Prompt-rendering regression suite (21 tests) | regression | `C-011` | PYTHONPATH=. python -W ignore tests/test_framework_runtime_render.py | pass |
| `T-028` | Lean-dispatch and metrics regression suite (21 tests) | regression | `C-011`, `C-012` | PYTHONPATH=. python -W ignore tests/test_lean_dispatch.py | pass |
| `T-029` | Memory optimizer regression suite (31 tests) | regression | `C-014`, `C-015`, `C-016` | PYTHONPATH=. python -W ignore tests/test_optimize_memory.py | pass |
| `T-030` | Live harvest: 25 runs, 70 occurrences, 39 lessons written; second harvest unchanged with the same store digest; list and report run | integration | `C-010`, `C-026` | python runtime/knowledge.py harvest; python runtime/knowledge.py list --eligible; python runtime/knowledge.py report | pass |

## Verification Results

- Verification method: framework paths in commands are written without the framework directory prefix, and every command ran from the repository root unless a cwd is named; the 0.9.0 baseline was captured from the unmodified tree before any runtime edit (`T-001`); the bundle tests ran before and after the exclusion entry (`T-002`); after implementation the new suite, the named regression suites, the three verifiers, and the live harvest were executed on the final tree; the in-place M14 failure was investigated once by replaying the same command sequence and the same verifier on temporary copies under both HEAD and the final tree (`T-023`); committed run run-c5a8d50d3238 was restored with git checkout after every verifier run and shows no change.
- Commands executed: python capture_baseline.py . tests/fixtures/knowledge/baseline-0.9.0; PYTHONPATH=. python tests/test_bundled_payload.py (before, after the exclusion, after sync); python runtime/knowledge.py harvest (twice), list --eligible, report; PYTHONPATH=. python tests/test_bundled_payload.py --sync; PYTHONPATH=. python -W ignore tests/test_knowledge.py; python -W ignore tests/test_model_tier.py; python tests/test_bundled_payload.py; python runtime/verify_multi_phase.py; python runtime/verify_multi_phase.py --run-id run-c5a8d50d3238 (three times); the same verifier on temporary copies of the final tree and of git archive HEAD; python runtime/verify_vertical_slice.py; python runtime/verify_registry_coverage.py; PYTHONPATH=. python -W ignore tests/test_framework_runtime_render.py, tests/test_lean_dispatch.py, tests/test_optimize_memory.py; git checkout -- runs/run-c5a8d50d3238/.
- Result summary: 30 evidence entries executed, 27 passed, 3 failed (`T-021`, `T-022`, `T-024`); tests/test_knowledge.py 47 of 47, test_model_tier 47 of 47, bundle tests 11 of 11 with this checkout's package, verifiers 15 of 15 on copies, 10 of 10, 8 of 8.
- Unverified areas: M14 in place against committed run run-c5a8d50d3238 (blocked by the file lock, proven only on copies); the plain-invocation bundle test and plain --sync in this worktree (resolve the main checkout's package until the change lands); the full unit suite, deliberately not run in this phase.

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | Gate lessons are keyed by the phase the gate closes (evidence_bundle_ref.closes_state), and only the gate work item's envelope counts; the successor's consequent gate-rejection envelope is skipped (`C-010`) | D-013 gate fingerprint, scope A-002 "target phase" | The design's test strategy states "gate G closing phase P"; counting the successor envelope would double each rejection | not-required |
| `V-002` | knowledge-harvest.json also carries schema, run_id, at, retained, occurrences, unresolved, store_written, store_digest (`C-010`) | D-006 outcome fields | Additive diagnostics; no ledger event and no aggregation output changes | not-required |
| `V-003` | A run recorded on with no matching lesson gets hydrated true with matched 0 and an empty list; a missing store counts as zero lessons; the console lessons line prints for every on run (`C-010`, `C-011`) | D-007 dispatch shape | The design does not fix the zero-match shape; flag-off and pre-change paths stay as specified | not-required |
| `V-004` | A remedy over 200 characters is refused rather than truncated; actor and rationale are collapsed to one line and capped at 300 characters (`C-010`) | D-002 governance remedy screening | Refusal never alters operator text silently; caps keep the store to one-line fields | not-required |
| `V-005` | The bundle sync and the bundle tests were run with PYTHONPATH=. rather than the literal plain command, and tests/test_knowledge.py puts the repository root first on sys.path (`C-017` to `C-024`, `C-025`) | P-011 sync procedure | The plain command resolves the main checkout's package, which lacks the exclusion and would mirror the live store into the bundle | not-required |

## Boundary Compliance

- Module boundaries preserved: runtime/knowledge.py imports only the standard library and state_engine and never framework_runtime.py; framework_runtime.py calls it one-way at plan, dispatch, prompt rendering, and aggregation; execution_metrics.py reads only invocation_started detail (`T-017`); no context-slice member, validator, Phase Model table, or agent module text was edited (`T-013`).
- Public interface changes: additive only -- plan flag --no-lesson-hydration on every request subcommand; execution-request.json key knowledge_loop for new runs; memory_slice on and off shapes for knowledge-loop runs; optional prompt section; invocation_started detail lessons_shown for knowledge-loop runs; execution-metrics per-phase and run counts; new runtime/knowledge.py command line; RUNTIME_VERSION 0.10.0. The payload digest inputs and the idempotency key are unchanged.
- Data or migration impact: new store memory/lessons/lessons.store.json (schema framework.memory/lessons.v1) and lock file, forward creation only; no existing run is backfilled; reversible by setting hydration_default off or reverting the change set.
- Declared side effects: this invocation wrote the 26 change-set files plus the artifact runs/run-c9fb8d5bbb32/states/implementation/artifacts/implementation-report.md and the result envelope runs/run-c9fb8d5bbb32/states/implementation/result-envelope.json. The runtime child processes of the verifiers also wrote outside that set: the default-target verifier recorded 6 replay entries in runs/run-c9fb8d5bbb32/state.json and regenerated runs/run-c9fb8d5bbb32/task-context.yaml (`T-024`), and the targeted verifier's writes to runs/run-c5a8d50d3238 were reverted with git checkout; all temporary roots were removed.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | In this worktree a tracked run file is locked between runtime child processes (WinError 5 on os.replace; a file-cache process is running), so in-place M14 cannot pass here | high | The replay check reads as failing in this checkout although the code passes it | `T-023` passes 15 of 15 on copies of both HEAD and the final tree; in-place failure is an environment condition |
| `R-002` | A plain bundle test or plain --sync run from this worktree resolves the main checkout's package, which lacks lessons.store.*, so a sync would mirror the live store into the bundle | medium | This repository's lessons could reach the bundle if synced that way before landing | Mirror synced with this checkout's package; `T-016` and `T-020` prove no store in the bundle |
| `R-003` | The default-target verifier run recorded 6 runtime replay entries in this run's state.json and regenerated its task-context.yaml | medium | Run evidence of run-c9fb8d5bbb32 carries entries a verifier added | Events and transitions unchanged (M14 fingerprint 49 to 49, 25 to 25); entries are runtime-attributed; raised as `Q-003` |
| `R-004` | The slice-member digest guard pins 45 files to the 0.9.0 baseline | high | Any later deliberate edit to one of them fails BackwardCompatibilityTestCase until re-baselined | baseline.json states the re-baseline rule; failure message names the file |
| `R-005` | A lock file left by a hard-killed writer blocks harvest and governance | low | Aggregation harvests record skipped; governance fails | Lock is removed in finally; contention message names the lock path and says a stale lock may be removed |
| `R-006` | run-308f4d0ee447 has no state.json, so its 7 check occurrences cannot resolve an artifact type | high | Those 7 occurrences are not counted in any lesson | Counted and printed as unresolved by every harvest (`T-007`, `T-030`) |

## Handoff Notes

- Reviewer focus areas: plan_run and cmd_dispatch hooks in runtime/framework_runtime.py (`C-011`) for any leak into the absent-record path; the harvest closed field list and the skip rules in runtime/knowledge.py (`C-010`, `V-001`); the forced-failure and lock-contention behaviour of the aggregation step (`T-015`); the environment conditions behind `T-021`, `T-022`, and `R-003`.
- Follow-up work: re-run tests/test_bundled_payload.py and verify_multi_phase.py --run-id run-c5a8d50d3238 from the main checkout after the change lands there (`Q-001`, `Q-002`); the change proposal and release checklist (P-013) for the documentation phase; the full unit suite for the operator; config/execution-engine.md could list the memory_slice on shape, which the design did not name.
- Documentation impact: config/runtime.md, memory/README.md, memory/memory-governance.md, memory/memory-resolver.md updated and mirrored; runtime/README.md deliberately unchanged (context-slice member); the operator handbook does not yet mention the knowledge.py command line.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | Is M14 on temporary copies of the final tree (`T-023`) accepted for the replay obligation, or must it be re-run in place from a checkout without the file lock? | no | omn-qa | `C-011` |
| `Q-002` | Should the bundle tests and the sync be re-run from the main checkout once its package carries the exclusion entry? | no | omn-tech-lead | `C-008`, `C-017`, `C-024` |
| `Q-003` | Do the 6 replay entries the default-target verifier recorded in this run's state.json stand as runtime-recorded evidence? | no | omn-orchestrator | `C-011` |
| `Q-004` | The design's open decisions were implemented at their stated defaults (flag-off reason is the one permitted difference, pre-change aggregation does not harvest, no effectiveness threshold, omn-tech-lead default owner); does each owner confirm? | no | omn-product-owner | `C-009`, `C-010`, `C-011` |
