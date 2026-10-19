```yaml
releaseNote:
  releaseId: FC-023
  version: 0.11.0
  sourceInputs:
    - type: architecture-context
      reference: runs/inputs/okf-lessons-architecture-context.md
    - type: verification-report
      reference: runs/run-79276e78d773/states/quality-review/artifacts/review-package.md
    - type: validation-report
      reference: runs/run-79276e78d773/states/implementation/validation-report.json
    - type: final-change-summary
      reference: runs/run-79276e78d773/task-context.yaml
  producedBy: omn-documentation
  agentVersion: 1.2.0
  schemaVersion: 1.0.0
  status: provisional
  releaseVerdict: handed-off
  inputDigest: sha256:f6a9f769682c7efc59bfdbb427f51a87
  contextDigest: sha256:598693b3d4e606388ca8c2715f151cf0
```

## Metadata

- Version: 0.11.0
- Release date and time: 2026-10-17, at the documentation-and-release-handoff phase. No release event occurred.
- Environment: None reached. The change is uncommitted in the working tree over HEAD 915e884, and this note names no environment as reached.
- Release owner: omn-tech-lead holds the release decision, which is not made here. omn-orchestrator holds the Closure Gate this handoff feeds.

## Highlights

- Feature additions: Operators can run `python runtime/verify_okf_bundle.py` for a standalone pass or fail check of the lesson bundle against OKF v0.2 section 11, and can browse each lesson from the root index at `memory/lessons/index.md` (review-package, Test Adequacy Assessment, T-009; Standards and Architecture Conformance).
- Bug fixes: None identified.
- Improvements: Each lesson is a document that states its sources, its producer and time, its operator approval where one exists, and its status as draft, stable or deprecated. The lesson text that agents receive at dispatch is unchanged (review-package, Test Adequacy Assessment, render_section byte parity; task-context D-001).

## Technical Changes and Compatibility

- API or contract changes: Breaking for a checkout that holds only the JSON store. The lesson store moves from `memory/lessons/lessons.store.json` (schema framework.memory/lessons.v1) to a bundle under `memory/lessons`: one concept document per lesson, plus `index.md` and `log.md`. The JSON file is removed. The in-memory store interface used by callers above `load_store` and `write_store` is unchanged (review-package, Standards and Architecture Conformance). New command surfaces: `python runtime/knowledge.py migrate` and `python runtime/verify_okf_bundle.py` (review-package, Test Adequacy Assessment).
- Database or migration impact: The live lesson store is migrated to 43 concept documents, and the JSON store is absent. The review corroborates the migration by the absent JSON store and the 43 documents, and did not re-run it (review-package, Test Adequacy Assessment). A checkout that still holds the JSON store must run `python runtime/knowledge.py migrate` once. Until it does, readers and writers raise store-migration-pending.
- Configuration changes: None identified.
- Backward compatibility notes: A checkout holding only the JSON store, after it pulls this change, is affected as follows. Lesson readers and writers raise store-migration-pending. Recall withholds lessons, and the harvest aggregation records the harvest as failed, naming store-migration-pending (task-context R-001 and R-012). The required action is one run of `python runtime/knowledge.py migrate` in that checkout. No deadline is stated in a supplied input. Where both the JSON store and the bundle exist and differ, the migrate outcome is open (K-001 and K-005). A revert of this change loses governance actions recorded after migration unless they are re-applied (review-package, Residual Risk; task-context, Rollout and Rollback).

## Operational Notes

- Deployment considerations: Nothing is deployed. Each checkout that holds the JSON store runs migrate once after it pulls the change. The bundle is excluded from the installed payload and the bundled mirror by its relative path, and no other path is newly excluded (review-package, Test Adequacy Assessment, payload exclusion by path).
- Monitoring and alerts: A healthy bundle gives `python runtime/verify_okf_bundle.py` a pass with exit 0 and 0 findings, as reviewed over 43 documents and 2 reserved files (review-package, Test Adequacy Assessment, T-009). Watch for store-migration-pending in recall or harvest output, which marks a checkout not yet migrated. Watch the elapsed time recorded in knowledge-harvest.json as the lesson count grows (review-package, Residual Risk, monitoring required).
- Rollback criteria: No rollback criterion is stated in a supplied input, and no rollback was taken. The decision on any rollback belongs to omn-tech-lead.

## Validation Summary

- Test status: From the review package RP-2026-0011, Test Adequacy Assessment, as executed by omn-dev-2-reviewer before the corrections: test_okf_bundle 29 OK; test_knowledge 51 OK; test_bundled_payload 11 OK; test_optimize_memory 31 OK; verify_okf_bundle pass over 43 documents with 0 findings. The framework validator record of the implementation report, from the validation-report.json for the implementation state, shows 32 of 32 checks pass. That record covers document structure and the report's recorded verification status, not behaviour. Task-context records the Review Gate and the Verification Gate as approved by omn-qa. No supplied artifact records the test runs made after CR-001 and CR-003, and no re-review of F-001 is recorded. The post-correction position is open (K-007).
- Known risk acceptance: After an interruption, concept documents can disagree with `index.md` and `log.md` until the next write. This is accepted in the design's Tradeoffs and Accepted risk, and the design's owner of the Design Gate is omn-tech-lead, recorded as approved in task-context. The serialisation subset limit (D-007) is accepted in the design's Tradeoffs (review-package, Standards and Architecture Conformance; task-context D-007).
- Post-release checks: After the change is committed and pulled, run `python runtime/verify_okf_bundle.py`. In each checkout that held the JSON store, run `python runtime/knowledge.py migrate` once, then confirm that recall returns lessons. Confirm that the bundle is absent from the installed payload.

## Known Issues

| ID | Issue | Impact | Workaround | Tracking |
|---|---|---|---|---|
| `K-001` | Review finding F-001, high, open in the review: when the JSON store and the bundle both exist and differ, migrate rewrites the bundle from the JSON store, discards bundle-only lessons and governance history, and reports success. Reproduced by the reviewer in a scratch copy. | An operator who runs migrate in that state loses approvals and lessons recorded only in the bundle. | None identified. The review names the both-forms state as the one to avoid until CR-001 closes. | RP-2026-0011, F-001 and CR-001, owner omn-dev-1-implement. CR-001 is reported applied after the review; the reviewer's standing is not recorded. |
| `K-002` | Review finding F-002, low, open: the verifier reports valid YAML outside the writer's subset as OKF-11.1 "frontmatter is not parseable" and does not state that the cause is the subset limit. | Someone checking a conformant third-party bundle that uses block scalars, anchors or multi-line plain scalars is told section 11 fails, without the reason. | None identified. The lesson bundle is written inside the subset and is unaffected. | RP-2026-0011, F-002 and CR-002, owner architect, non-blocking, open. |
| `K-003` | Review finding F-003, low, open: the optimiser's bundle denial matches `memory/lessons` over the absolute path, not the path relative to the scan root. | Under a framework placed below a directory pair named memory and lessons, the optimiser would skip every memory document. No current layout does this. | None needed for current layouts. | RP-2026-0011, F-003 and CR-003, owner omn-dev-1-implement. CR-003 is reported applied after the review; the reviewer's standing is not recorded. |
| `K-004` | Unmitigated risk in the review: a checkout holding only the JSON store that reaches the both-forms state, through an interruption or a migration-mismatch, and then records a governance action or a harvest, loses that work on the next migrate. Whether any install ever held a JSON store is unconfirmed. | Operators of such a checkout can lose governance work recorded after the mismatch. | None identified. | RP-2026-0011, Residual Risk; open question Q-002, owner omn-tech-lead. |
| `K-005` | Open question Q-001: when the JSON store and the bundle both exist and differ, which form wins, the bundle as design section 6 states, or the JSON store as design section 5.3 implies? No ruling is in a supplied input. | A checkout in the both-forms state cannot complete migration until the architect rules. | None identified. | RP-2026-0011, Q-001, routed to architect, open. |
| `K-006` | Open question Q-002: can any installed copy hold a JSON store written by runtime 0.10.0? The design says none did, and the review does not confirm it. | If one can, F-001 becomes critical and the review verdict becomes reject, and the operator meets K-004. | None identified. | RP-2026-0011, Q-002, routed to omn-tech-lead, open. |
| `K-007` | Open question: the corrections CR-001 and CR-003 are reported as applied, and the Review and Verification Gates as approved by omn-qa, but no supplied artifact records the corrected change, its test runs, or a reviewer re-review. | The status of this note is provisional. The change's post-review behaviour is not confirmed by a record this run can cite. | None identified. | Routed to omn-dev-1-implement for the change record of CR-001 and CR-003, to omn-dev-2-reviewer for the re-review standing of F-001 and F-003, and to omn-qa for the post-correction verification record. Open. |

## Communication

- Stakeholders notified: None. No stakeholder list or communication requirement was supplied, so the audience is inferred and not supplied: framework maintainers, and the owners of checkouts that hold the lesson store. This note is handed to omn-orchestrator for the Closure Gate and to omn-tech-lead as the published record. This agent sent no notification.
- Support handoff notes: store-migration-pending in a checkout means a JSON store has not been migrated. It is not corruption; run `python runtime/knowledge.py migrate` once. An absent `memory/lessons/lessons.store.json` is intended. An index or log that disagrees with the documents after an interrupted write is the accepted state until the next write (accepted risk in the design's Tradeoffs). An OKF-11.1 failure on a third-party bundle with valid YAML outside the subset is the subset limit (K-002), not a section 11 violation. Look first at the bundle with `python runtime/verify_okf_bundle.py`, then check whether a JSON store is still present in that checkout.
