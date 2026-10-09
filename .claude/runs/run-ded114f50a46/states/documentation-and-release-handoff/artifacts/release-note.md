```yaml
releaseNote:
  releaseId: run-ded114f50a46-release-handoff
  version: 0.9.0
  sourceInputs:
    - type: architecture-context
      reference: runs/inputs/model-tier-architecture-context.md
    - type: verification-report
      reference: runs/run-ded114f50a46/states/quality-review/artifacts/review-package.md
    - type: final-change-summary
      reference: runs/run-ded114f50a46/states/implementation/artifacts/implementation-report.md
  producedBy: omn-documentation
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  releaseVerdict: released
  inputDigest: sha256:2c9da3d54ddd61b2fdb37a93cc66bea7
  contextDigest: sha256:54658dbc51ce3d1c2ac9ad1d35f7aaf6
```

## Metadata

- Version: 0.9.0
- Release date and time: 2026-10-08, the date of this publication. The operator instructed that the change is delivered and verified, and the verdict `released` follows that instruction. No deployment status was supplied, so no time of landing is stated. The Closure Gate decision belongs to its owner, not to this note.
- Environment: The change is a working-tree change set against HEAD (review-package, Review Scope); no deployment environment is named in the supplied evidence.
- Release owner: Not assigned in the supplied evidence. Release and merge decisions belong to omn-tech-lead and omn-orchestrator (identity.md, boundary table).

## Highlights

- Feature additions: Each dispatch envelope now carries a `model_tier` record (tier, host hint, basis, escalation) for its phase. The declaration covers 37 phases across 8 workflows: 14 light, 14 standard, 9 deep (implementation-report, Change Set C-001). A phase whose validator rejection or rolled-back gate rejection is recorded resolves one tier higher on its next dispatch, capped at deep. The runtime makes no model call; the tier has effect only when the dispatching session passes the hint (K-005).
- Bug fixes: None identified.
- Improvements: Execution metrics report invocations and estimated context bytes per tier, and the share of invocations at a non-deep tier (implementation-report, C-003; review-package, focus checks).

## Technical Changes and Compatibility

- API or contract changes: Additive only. One top-level `model_tier` field in the invocation envelope; two added keys on the `invocation_started` event detail; one prompt line and one console line stating the tier; `model_tiers` and per-phase `model_tier` keys in execution metrics; two new checks (C7, C8) in `verify_registry_coverage.py`. The loader now refuses a standard-tier hint other than `inherit` (post-review correction, operator-verified). Runtime version 0.8.0 is now 0.9.0 (framework_runtime.py, RUNTIME_VERSION).
- Database or migration impact: None. No persisted run data is rewritten; historical envelopes and events fall into an untiered bucket (implementation-report, Boundary Compliance).
- Configuration changes: New file `config/model-tier-policy.json`, with a bundled mirror under `omn_agent/_bundled_payload/config/`. Hints: light `haiku`, standard `inherit`, deep `opus`. Removing the file returns every phase to `inherit`, and an absent file never promotes a phase.
- Backward compatibility notes: The original envelope fields keep their names and values; the reviewer confirmed by execution that two dispatches differ only by `model_tier` and timestamp-derived fields (review-package, focus checks). No agent entrypoint, Phase Model table, gate matrix, validator, or template changed (review-package, Standards and Architecture Conformance). Consumers that read only the original fields need no action. Consumers that dispatch need to pass `host_hint` as the per-dispatch model override, or the tier has no effect (K-005).

## Operational Notes

- Deployment considerations: Ship `config/model-tier-policy.json` with runtime 0.9.0. A malformed declaration, or one whose standard hint is not `inherit`, fails dispatch as a policy failure; an absent declaration makes every phase inherit. Host acceptance of the `haiku` and `opus` overrides is not confirmed by any supplied evidence (implementation-report, Handoff Notes).
- Monitoring and alerts: Read `non_deep_share` in `execution-metrics.json` for each implement-feature run. The declared bar is at least 3 of 6 invocations at a non-deep tier. A healthy run meets it; a run where execution planning is rejected and promoted to deep falls to 2 of 6 (K-006).
- Rollback criteria: Revert if any original envelope field changes name or value, or if an existing verifier leaves its recorded baseline (task-context, C-004). The documented off position is removing `config/model-tier-policy.json`.

## Validation Summary

- Test status: The Verification Gate decision (omn-qa, recorded by the operator) cites the full unit suite at 642 of 642 OK, with registry coverage 8/8, validators 6/6, and manifests 2/2 (run-ledger.json, Verification Gate). The operator states that 642 is the corrected tree, after the review corrections were closed; the reviewer's 638 OK (review-package, Test Adequacy Assessment) was the pre-correction tree, so the two figures cover different trees and 642 is the current one. This agent did not reproduce these results. Observed escalation: this run's own documentation phase was first dispatched at tier light, was rejected by the validator on R1, and was automatically escalated to standard on its second attempt (invocation envelope, model_tier.escalation: 1 validator rejection, promoted from light to standard); this is evidence the escalation works.
- Known risk acceptance: None identified.
- Post-release checks: After the change reaches an environment, confirm that an implement-feature run's `non_deep_share` meets 3 of 6; that each envelope's `model_tier` matches `config/model-tier-policy.json` for its phase; and that `verify_recovery` X1 and `verify_self_hosting` S8 are still the only failing checks (K-004).

## Known Issues

| ID | Issue | Impact | Workaround | Tracking |
|---|---|---|---|---|
| `K-001` | Resolved. Review finding F-001 (medium): the loader checked only that the standard hint was non-empty. `load_model_tier_policy` now rejects a standard hint other than `inherit`. | None remaining for current installs. A copy of the declaration or runtime from before the correction can still let an edited standard hint stop undeclared phases inheriting. | Use runtime 0.9.0 with the corrected loader; keep the standard hint at `inherit`. | Review-package RP-2026-0009, F-001 and CR-001; closed by the post-review correction pass and verified by the operator; the review package itself still shows the status open |
| `K-002` | Resolved. Review finding F-002 (low): the Model Tiers section of config/runtime.md omitted the absent-file no-promotion rule. The section now states it. | None remaining for readers of the current document; a reader of the earlier wording could expect promotion with no declaration file. | Read config/runtime.md, Model Tiers, as it now stands. | Review-package RP-2026-0009, F-002 and CR-002; closed by the post-review correction pass and verified by the operator |
| `K-003` | Resolved. Review finding F-003 (low): the suite did not exercise rollback promotion or the `inherit` prompt branch. tests/test_model_tier.py now has rollback and inherit tests. | None remaining for those two cases. The field-by-field comparison of original envelope fields against a pre-change envelope (A-006) is not listed among the added tests in the supplied evidence. | None; the reviewer's execution at review time confirms the A-006 behavior. | Review-package RP-2026-0009, F-003 and CR-003; closed by the post-review correction pass and verified by the operator |
| `K-004` | Recovery verifier check X1 and self-hosting verifier check S8 fail on the changed tree and on an unmodified HEAD export. S8 also lists run-ded114f50a46 as in progress. | Anyone who reads these verifiers as green will be wrong; S8 cannot pass for this run until its change proposal accounts for it. | None; both failures predate this change. | No tracking reference in the supplied evidence; open question to omn-tech-lead on owner and tracking for X1 and S8 |
| `K-005` | The tier is advice. The runtime makes no model call, and the tier takes effect only if the dispatching session passes `host_hint` as the per-dispatch override. Host acceptance of the overrides is unconfirmed. | Operators expecting cost to fall get none where the hint is not passed; metrics count declared tiers, not models run. | Pass `host_hint` from the `model_tier` record as the per-dispatch override. | implementation-report R-002 and Handoff Notes; review-package Residual Risk; owner of the dispatching session |
| `K-006` | Execution planning sits at standard, leaving exactly 3 of 6 implement-feature phases non-deep with no margin. A first-attempt rejection promotes it to deep. | The implement-feature run drops to 2 of 6 non-deep, below the declared bar, though the declaration itself meets it. | None recorded in the supplied evidence; watch `non_deep_share`. | implementation-report R-003; review-package Residual Risk |
| `K-007` | Not delivered: no per-dispatch switch to disable or override a tier. | A team wanting one dispatch at another tier must edit the shared declaration file. | Remove `config/model-tier-policy.json` to return all phases to `inherit`. | Open question Q-004 (task-context.yaml); owner omn-product-owner |
| `K-008` | Review open question Q-001: whether the PINNED_LIGHT and PINNED_DEEP sets in `verify_registry_coverage.py` count as a second tier assignment under acceptance criterion A-003. | If they do, A-003 is not met and this note cannot state it as met. | None recorded. | review-package RP-2026-0009, Q-001; owner omn-qa |

## Communication

- Stakeholders notified: None yet. No stakeholder list or communication requirement was supplied, so the audience is inferred: framework operators who dispatch implement-feature runs, and the owners named in Known Issues.
- Support handoff notes: A `model_tier` record that names `haiku` or `opus` does not mean the model changed; the tier takes effect only if the session passes the hint, and the runtime cannot observe that (K-005). A `deep` tier on a phase after a rejection is a designed promotion, one tier per recorded rejection, not a fault; check `escalation` in the record. A phase in this framework's own run history that shows light then standard after a validator rejection is the same designed promotion. The untiered bucket in execution metrics holds historical invocations and is not an error. The review package still shows F-001 to F-003 as open; K-001 to K-003 record them as resolved on the operator's verification, so read the review package as the state at review time.
