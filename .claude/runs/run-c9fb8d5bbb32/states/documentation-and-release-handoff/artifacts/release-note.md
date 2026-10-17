```yaml
releaseNote:
  releaseId: RN-run-c9fb8d5bbb32-handoff
  version: 0.10.0
  sourceInputs:
    - type: architecture-context
      reference: runs/inputs/knowledge-loop-architecture-context.md
    - type: verification-report
      reference: runs/run-c9fb8d5bbb32/states/quality-review/artifacts/review-package.md
    - type: verification-report
      reference: runs/run-c9fb8d5bbb32/state.json, gates Review Gate and Verification Gate
    - type: final-change-summary
      reference: runs/run-c9fb8d5bbb32/task-context.yaml
    - type: validation-report
      reference: runs/run-f94564cb61ce/states/regression-validation/artifacts/validation-report.md
    - type: verification-report
      reference: runs/run-f94564cb61ce/state.json, gate Fix Gate
    - type: final-change-summary
      reference: proposals/framework-change-proposal-FC-020.md, open item O-005
    - type: verification-report
      reference: inline, operator relay of the CR-003 scoped re-review outcome in the dispatch of inv-c9fb8d5bbb32-06-002
  producedBy: omn-documentation
  agentVersion: 1.2.0
  schemaVersion: 1.0.0
  status: provisional
  releaseVerdict: handed-off
  inputDigest: sha256:9b906060954b5108ac8fbda3117b016e
  contextDigest: sha256:598693b3d4e606388ca8c2715f151cf0
```

## Metadata

- Version: 0.10.0
- Release date and time: None. Not released. Closure handoff prepared 2026-10-17 under invocation inv-c9fb8d5bbb32-06-002.
- Environment: the working tree of run run-c9fb8d5bbb32, on this run's worktree branch. The change set is delivered and review-approved there only; it has not been merged, released, or deployed, and no environment is reached. No deployment status was supplied.
- Release owner: omn-tech-lead (release decision); omn-orchestrator (Closure Gate).

## Highlights

- Feature additions: Recurring failures in recorded run evidence are harvested into governed lessons. An approved lesson, or a candidate seen in at least two distinct runs, is shown to later dispatches of the phase it was recorded against, at most five per dispatch, labelled as recorded evidence rather than instructions. Hydration is chosen per run at plan time, on by default for runs planned after this change, and a plan flag switches it off. Operators approve, retire, and annotate lessons from the command line, and a per-lesson effectiveness report is available.
- Bug fixes: None identified.
- Improvements: None identified.

## Technical Changes and Compatibility

- API or contract changes: Additive. The memory slice carries hydrated lessons and the hydration record. The invocation_started detail gains lessons_shown. Per-phase execution metrics gain lessons_hydrated and lessons_hydrated_by_invocation, with a run total. The runtime version stamp moves from 0.9.0 to 0.10.0. A flag-off dispatch adds lessons_shown as an empty list (K-003), and its memory_slice.reason text differs from the pre-change text, the one difference the Design Gate permitted.
- Database or migration impact: One new tracked store, memory/lessons/lessons.store.json, created and rewritten by harvest. Existing run evidence is read in place. No existing run or plan is backfilled. Branches that rewrite the store conflict on merge (K-009).
- Configuration changes: New policy file config/knowledge-policy.json: hydration default on, threshold of two distinct runs, default lesson owner omn-tech-lead, fixed cap of five. A plan flag switches hydration off for one run. The store is excluded from the installed payload.
- Backward compatibility notes: A pre-change run, one with no hydration record, never hydrates and keeps its idempotency key; review confirmed the key unchanged in the pre-change and flag-off tests. Its envelope and prompt match the 0.9.0 baseline after the closed normalisation list; omn-qa holds a reservation on this (K-001). The reworked identity test (BackwardCompatibilityTestCase) passes 6 of 6, per omn-qa in run-f94564cb61ce. The context slice exclusion text still reads that memory hydration is not requested, even on hydrated runs (accepted risk). The evidence states no consumer action.

## Operational Notes

- Deployment considerations: Nothing has been deployed. Merge and release are held by omn-tech-lead. The bundled payload mirror must match the authoritative tree; review found the eight authoritative files identical to the mirror, and the in-place re-runs are closure condition (1) (K-002). Installed copies receive no lessons. Pre-change runs are harvested only by an operator command, never by their own aggregation.
- Monitoring and alerts: After each aggregation, read status and elapsed_seconds in runs/<run>/knowledge-harvest.json. Healthy means a status other than skipped or failed, with elapsed time near 0.3 to 0.5 seconds as review measured over 25 runs. A skipped or failed status needs attention (K-011). Watch for merge conflicts on the lesson store (K-009).
- Rollback criteria: No rollback trigger is stated in the evidence; the decision to revert is omn-tech-lead's. Per the operator ruling, rollback is reverting the change set: hydration is recorded per run at plan time, so pre-change runs are untouched and behave as before after reversion.

## Validation Summary

- Test status: Review Gate approved by omn-qa as second owner; Verification Gate approved by omn-qa as pass-with-reservations, the A-018 reservation pending omn-product-owner (IR Q-004). Per those records, each of A-001 to A-023 maps to an executed test, tests/test_knowledge.py ran 49 of 49, and the suite ran 739 of 739 tests with the sole failing module environmental (K-006). Post-review corrections CR-002 and CR-005 are satisfied per both gate records. On the later combined tree, omn-qa recorded the full suite at 768 tests with only test_demo_capture failing (run-f94564cb61ce regression validation). CR-003 is resolved with corrections by a scoped re-review, per the operator relay and the run-f94564cb61ce Fix Gate record; CR-001 and CR-004 remain open and non-blocking.
- Known risk acceptance: Accepted by omn-tech-lead at the Design Gate, per the review package: fail-open recall on a corrupt store, full harvest at every aggregation, and the unchanged memory exclusion text beside a hydrated memory slice. CR-001, CR-004, and the CR-003 follow-ups are open items, not accepted risk.
- Post-release checks: The Verification Gate closure conditions, carried as handoff items: (1) in-place re-run of the plain bundle test and of verify_multi_phase with --run-id run-c5a8d50d3238 after landing, owner omn-qa (K-002); (2) CR-004 disposition by omn-tech-lead (K-003); (3) IR Q-004 confirmation by omn-product-owner (K-001); (4) CR-001 disposition by omn-orchestrator without rewriting evidence (K-004); (5) the CR-003 follow-ups for omn-dev-1-implement (K-005, K-013, K-014); (6) the carried known issues K-006 to K-010. The change proposal and release checklist are FC-022 (K-012).

## Known Issues

| ID | Issue | Impact | Workaround | Tracking |
|---|---|---|---|---|
| `K-001` | Acceptance criterion A-018 (pre-change path identical to the 0.9.0 baseline) carries a reservation: the flag-off reason difference is not yet confirmed as permitted. | Maintainers cannot yet rely on the pre-change identity as confirmed. | None stated. | Verification Gate record; IR Q-004; owner omn-product-owner. |
| `K-002` | The plain bundle test and verify_multi_phase with --run-id run-c5a8d50d3238 have not been re-run in place after landing; replay checks passed only on temporary copies because a file lock blocked the in-place run. | A bundle or replay regression would surface only after landing. | Temporary-copy runs passed: bundle test 11 of 11, replay checks 15 of 15 (Review Gate record). | Verification Gate closure condition (1); owner omn-qa. |
| `K-003` | A flag-off dispatch adds lessons_shown as an empty list to the invocation_started detail, a difference from the 0.9.0 baseline that Design Gate condition (1) required to be escalated. | Anyone comparing flag-off event detail with a 0.9.0 log sees one extra key; review found no consumer affected. | None stated. | Review CR-004; Verification Gate closure condition (2); owner omn-tech-lead. |
| `K-004` | The run record has no owned disposition for six replay entries and a regenerated task-context file that the default-target verifier wrote into this run. | Auditors of this run see entries that no envelope accounts for. | None stated. | Review CR-001; Verification Gate closure condition (4); owner omn-orchestrator. |
| `K-005` | The identity test's re-baseline rule cannot be executed when runtime/framework_runtime.py changes for reasons unrelated to the knowledge loop (medium, CR-003 re-review follow-up). | A maintainer changing the runtime for another reason cannot re-baseline the test by its stated rule. | None stated. | CR-003 scoped re-review follow-up, relayed by the operator; no tracking reference supplied; owner omn-dev-1-implement. |
| `K-006` | test_demo_capture fails because ffmpeg 9.0.2 rejects the filter_complex_script option; it reproduces on the base commit and lies outside this change set. | Anyone running the full suite with that ffmpeg sees 3 failing tests in that module. | None stated. | FC-020 O-005 (DF-001); owner omn-tech-lead. |
| `K-007` | The force-refresh branch of maybe_aggregate returns before the harvest step and has no test or stated expected behaviour. | A force-refreshed aggregation skips harvest, and no test pins that behaviour. | None stated. | Verification Gate closure condition (6); review Test Adequacy gap, handed to omn-qa. |
| `K-008` | verify_multi_phase without --run-id selects the latest run, including an in-flight one, and writes replay entries into it. | Operators who omit --run-id alter the run the verifier selects. | Always pass --run-id. | Review Q-002; owner omn-tech-lead. |
| `K-009` | The single tracked lesson store is rewritten by every knowledge-loop aggregation in any worktree, so parallel branches conflict on it. | Whoever merges such branches must reconcile the governance history by hand. | None stated. | Review Q-003 and residual risk under D-002; owner architect. |
| `K-010` | The operator handbook does not document the knowledge.py command line (annotate, recall, harvest, report). | Operators cannot find in the handbook how to approve, annotate, or report lessons. | Use the knowledge.py subcommands directly. | Verification Gate closure condition (6); no tracking reference supplied; open question to omn-orchestrator. |
| `K-011` | A stale lock left by a hard-killed writer makes every later aggregation harvest record skipped, with no console or ledger signal, so the loop can stop closing unnoticed. | Operators may assume lessons are current while harvest has stopped. | Check status in knowledge-harvest.json after each aggregation; no lock-clearing procedure is stated. | Review residual risk (unmitigated); no tracking reference supplied; open question to omn-tech-lead. |
| `K-012` | The framework change proposal and the release checklist are not among the supplied inputs, so this handoff does not establish that they exist or pass. | A framework update cannot be released until they exist and pass. | None stated. | FC-022; owner omn-orchestrator. |
| `K-013` | The identity comparison runs without the shipped lesson store (low, CR-003 re-review follow-up). | The test does not exercise the store a real checkout carries. | None stated. | CR-003 scoped re-review follow-up, relayed by the operator; no tracking reference supplied; owner omn-dev-1-implement. |
| `K-014` | A build failure in the identity test is misreported as a KeyError (low, CR-003 re-review follow-up). | A maintainer diagnosing a failing run sees a misleading error. | None stated. | CR-003 scoped re-review follow-up, relayed by the operator; no tracking reference supplied; owner omn-dev-1-implement. |

## Communication

- Stakeholders notified: None notified; this run distributed nothing. Audience inferred from the phase, not supplied: omn-orchestrator as Closure Gate owner, omn-tech-lead as release owner, and the routed owners named in Known Issues. Communication basis: release-handoff.
- Support handoff notes: A harvest status of skipped can mean a stale lock (K-011), not a fault in aggregation; read status and elapsed_seconds first. The test_demo_capture failure (K-006) is environmental and not caused by this change. A run with no hydration record shows no lessons; that is the pre-change path, not missing data. A flag-off run carries an empty lessons_shown key (K-003); that is not a fault. A failing identity test after an unrelated runtime edit may be K-005 or K-014 rather than a regression. Why provisional: the CR-003 re-review outcome and its follow-ups (K-005, K-013, K-014) reach this note only through the operator's relay, and no run artifact records them. Open questions, still open at handoff: (a) to omn-orchestrator, record the CR-003 scoped re-review outcome and follow-ups in an artifact with tracking, and record tracking for K-010, in FC-022; (b) to omn-tech-lead, no lock-recovery procedure is stated for K-011 and no rollback trigger is stated; (c) to omn-dev-1-implement, the three CR-003 follow-ups. Superseded since the previous attempt: the pre-change identity test fragility (review CR-003) is resolved and K-005 now carries its first follow-up.
