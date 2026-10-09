```yaml
implementationReport:
  reportId: IR-2026-0010
  changeReference: run-ded114f50a46, per-phase model tier in the dispatch envelope
  sourceInputs:
    - type: technical-design
      reference: runs/run-ded114f50a46/states/solution-design-and-risk-assessment/artifacts/technical-design.md
    - type: feature-request
      reference: runs/inputs/model-tier-feature-request.md
    - type: change-request
      reference: runs/inputs/model-tier-change-request.md
    - type: business-intent
      reference: runs/inputs/model-tier-business-intent.md
    - type: architecture-context
      reference: runs/inputs/model-tier-architecture-context.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: complete
  workflowPhase: implementation
  verificationStatus: verified
  inputDigest: sha256:a6e595dd838f330546bc5c9f505571c8
  contextDigest: sha256:dcbf47380685fab9899be0afd94f6e0d
```

## Metadata

- Report ID: IR-2026-0010
- Change reference: run-ded114f50a46, per-phase model tier in the dispatch envelope, implementing decision records D-001 and D-002 and decisions D-003, D-004, D-005
- Workflow phase: implementation
- Status: complete
- Verification status: verified
- Review status: pending-review

## Implementation Summary

- Change intent: every dispatch envelope now carries an additive `model_tier` record (tier, host hint, basis, escalation) resolved from one shipped declaration and from recorded run state. A phase with a recorded validator rejection or a rolled-back gate rejection resolves one tier higher on its next dispatch, capped at the strongest tier. Execution metrics report invocations and estimated context bytes by tier, and the registry coverage verifier fails on an uncovered phase or a non-monotonic promotion. The runtime version moved from 0.8.0 to 0.9.0.
- Approach taken: one new data file under `config/` keyed by workflow and phase, loaded and resolved by a pure function pair beside the existing optional-file policy loader in the runtime core (necessity and reuse ladder: extend an existing component; the one new file is justified because no existing carrier holds phase-keyed data outside the parsed tables, and no new abstraction or dependency was added). Rejections are read from the recovery ledger entries with reason code `validation_failed` and from the work item's supersessions. Hint values are the operator-resolved aliases, held in the data file only; the standard tier carries the reserved value `inherit`. Metrics group existing events and envelopes; the coverage verifier gained two checks; the mirror was refreshed by the synchronisation command only.
- Design reference: technical design `sha256:4df24c0b76d46462bbabede130e926b5`, modules M-001 to M-008, decisions D-001 to D-005, sequencing P-001 to P-010; the no-change modules M-009 to M-015 were left untouched and verified so.
- Out of scope: concurrent phase execution, any model call or vendor dependency, agent module text, entrypoint declarations, Phase Model tables, the gate matrix, validators and templates, lowering a tier after success, and an operator switch to disable or override a tier (the design raised it as an open decision and the operator resolved against it); host-side application of the hint is the dispatching session's step and cannot be implemented here, so leaving it is safe because an unapplied hint equals the prior inherit behaviour.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `.claude/config/model-tier-policy.json` | added | the one declaration: 37 phase-to-tier assignments over 8 workflows and one host hint per tier | D-001, D-003, M-002, P-001 |
| `C-002` | `.claude/runtime/framework_runtime.py` | modified | loader, rejection counter, pure resolver, `model_tier` envelope record, event detail, prompt and console line, version 0.9.0 | D-001, D-002, M-001, P-002, P-003, P-004, P-007 |
| `C-003` | `.claude/runtime/execution_metrics.py` | modified | per-tier invocations, estimated bytes, untiered bucket, non-deep share, per-phase tier | D-004, M-003, P-005 |
| `C-004` | `.claude/runtime/verify_registry_coverage.py` | modified | check for declaration coverage and check for escalation monotonicity | D-005, M-004, P-006 |
| `C-005` | `tests/test_model_tier.py` | added | tests for the declaration, loader, resolver, rejection counting, metrics, verifier checks, and real dispatch | M-008, P-008 |
| `C-006` | `.claude/config/runtime.md` | modified | new Model Tiers governance section: declaration, envelope field, escalation rule, metrics | D-005, M-005, P-009 |
| `C-007` | `.claude/config/execution-engine.md` | modified | one field line in the Agent Invocation Envelope section and the additivity sentence | D-005, M-006, P-009 |
| `C-008` | `omn_agent/_bundled_payload/config/execution-engine.md` | modified | mirror of the authoritative file, written by the synchronisation command | M-007, P-010 |
| `C-009` | `omn_agent/_bundled_payload/config/model-tier-policy.json` | added | mirror of the authoritative file, written by the synchronisation command | M-007, P-010 |
| `C-010` | `omn_agent/_bundled_payload/config/runtime.md` | modified | mirror of the authoritative file, written by the synchronisation command | M-007, P-010 |
| `C-011` | `omn_agent/_bundled_payload/runtime/execution_metrics.py` | modified | mirror of the authoritative file, written by the synchronisation command | M-007, P-010 |
| `C-012` | `omn_agent/_bundled_payload/runtime/framework_runtime.py` | modified | mirror of the authoritative file, written by the synchronisation command | M-007, P-010 |
| `C-013` | `omn_agent/_bundled_payload/runtime/verify_registry_coverage.py` | modified | mirror of the authoritative file, written by the synchronisation command | M-007, P-010 |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | declaration covers all 37 phases, standard inherits, 3 of 6 implement-feature phases non-deep, operator tier resolutions hold, hints absent from runtime logic, no tier text in agent modules or Phase Model tables, governance documents state the field and rule, version rose | contract | `C-001`, `C-002`, `C-005`, `C-006`, `C-007` | `python -m unittest tests.test_model_tier.DeclarationTestCase` | pass |
| `T-002` | absent file loads as none; unreadable file, unknown tier, missing or blank hint each fail as a policy failure | unit | `C-002`, `C-005` | `python -m unittest tests.test_model_tier.LoaderTestCase` | pass |
| `T-003` | one-tier promotion per rejection kind with stated reason, deep ceiling, never lowered, undeclared phase escalates from standard, absent declaration never promotes, resolution repeatable | unit | `C-002`, `C-005` | `python -m unittest tests.test_model_tier.ResolverTestCase` | pass |
| `T-004` | only validator rejections under the phase and supersessions count; transport failures, other phases, and gate-state entries do not; a rollback recorded by the real state engine counts once | integration | `C-002`, `C-005` | `python -m unittest tests.test_model_tier.RejectionCountTestCase` | pass |
| `T-005` | per-tier invocations and bytes sum to the run totals, untiered bucket, empty share when nothing is tiered | unit | `C-003`, `C-005` | `python -m unittest tests.test_model_tier.MetricsTestCase` | pass |
| `T-006` | coverage check fails on a removed entry, a stale entry, a missing file, and a breached non-deep bar; monotonic check passes and fails a resolver that does not rise | contract | `C-001`, `C-004`, `C-005` | `python -m unittest tests.test_model_tier.VerifierTestCase` | pass |
| `T-007` | real command line against a copy of the tree: complete tier record, original envelope fields unchanged, event detail, prompt and console line, per-tier metrics, a real validator rejection promotes the next dispatch identically to the pure derivation, absent file inherits, malformed file fails dispatch with nothing written | end-to-end | `C-001`, `C-002`, `C-003`, `C-005` | `python -m unittest tests.test_model_tier.DispatchTestCase` | pass |
| `T-008` | the bundled payload equals the authoritative tree after synchronisation | contract | `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013` | `python -m unittest tests.test_bundled_payload` | pass |
| `T-009` | regression baseline: the whole repository suite, 595 tests before the change, 638 after | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013` | `python -m unittest discover -s tests` | pass |
| `T-010` | registry coverage verifier, 8 of 8 checks including the two new ones (6 of 6 before the change) | static | `C-001`, `C-002`, `C-004` | `python .claude/runtime/verify_registry_coverage.py` | pass |
| `T-011` | manifest conformance verifier, 2 of 2, unchanged | static | `C-002` | `python .claude/runtime/verify_manifests.py` | pass |
| `T-012` | artifact validator verifier, 6 of 6, unchanged | static | `C-002` | `python .claude/runtime/verify_validators.py` | pass |
| `T-013` | vertical slice verifier, 10 of 10, unchanged, including no loading policy in agent modules | static | `C-002`, `C-003` | `python .claude/runtime/verify_vertical_slice.py` | pass |

## Verification Results

- Verification method: the baseline was taken on an unmodified copy of the tree before any edit (suite 595 tests OK; verifier verdicts recorded per check), then every command below was re-run on the changed tree and compared by pass or fail per check, not by check count, as the operator resolved. Dispatch behaviour was exercised through the real command line against a temporary copy of the framework tree, including a real validator rejection and the resulting promotion.
- Commands executed: `python -m unittest discover -s tests`; `python -m unittest tests.test_model_tier` and its seven test classes individually; `python -m unittest tests.test_bundled_payload`; `python tests/test_bundled_payload.py --sync`; `python .claude/runtime/verify_registry_coverage.py`; `python .claude/runtime/verify_manifests.py`; `python .claude/runtime/verify_validators.py`; `python .claude/runtime/verify_vertical_slice.py`; `python .claude/runtime/verify_multi_phase.py`; `python .claude/runtime/verify_recovery.py`; `python .claude/runtime/verify_self_hosting.py`.
- Result summary: executed 13 evidence rows, passed 13, failed 0. Suite 638 tests OK after the change against 595 OK before it. Verifier verdicts per check match the baseline: registry coverage, manifests, validators, and vertical slice pass in full; multi-phase fails only its check M6, recovery fails only its check X1, and self-hosting fails only its check S8, each exactly as on the unmodified tree (see the first residual risk).
- Unverified areas: none

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | With no declaration file the resolver returns standard and inherit and never promotes; with the file present, an undeclared phase does promote from standard (`C-002`) | D-001, D-002 | the design states both an absent file resolving to inherit and an undeclared phase promoting from standard; with no file there is no hint for any higher tier, so the only coherent reading keeps an absent file fully inert, which also keeps every prior run unchanged | not-required |

## Boundary Compliance

- Module boundaries preserved: the change sits in the runtime core, the metrics module, the coverage verifier, two governance documents, one config file, one test file, and the mirror. The recovery policy and state engine modules were read and not edited, agent module text and entrypoints, Phase Model tables, the gate matrix, validators, templates, and the registry were not edited, and `runtime/README.md` did not grow.
- Public interface changes: one additive top-level `model_tier` record in the invocation envelope, two additive keys on the `invocation_started` event detail, one prompt line and one console line, additive `model_tiers` and per-phase `model_tier` keys in the execution-metrics document, and two added verifier checks. No existing field was renamed or retyped, and the payload digest and idempotency key do not read the record.
- Data or migration impact: none. No persisted run data is rewritten; historical envelopes and events land in the untiered bucket; removing the declaration file returns every phase to inherit.
- Declared side effects: the files in the Change Set, plus the artifact `.claude/runs/run-ded114f50a46/states/implementation/artifacts/implementation-report.md` and the result envelope `.claude/runs/run-ded114f50a46/states/implementation/result-envelope.json`. Verification also created and removed temporary copies of the framework tree under the operating system temporary directory, outside the repository.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | Three verifier checks fail on the changed tree: multi-phase M6, recovery X1, and self-hosting S8 | high | low | each fails identically on the unmodified tree before the change (baseline outputs captured before the first edit), none reads the tier record, and each is attributed to a pre-existing condition outside this change |
| `R-002` | A hint is effective only if the dispatching session passes it as the per-dispatch override, so tiers can be advisory and metrics count advice rather than models run | medium | medium | the envelope, the dispatch prompt, and the console each state the hint and the override instruction; the runtime cannot observe the host |
| `R-003` | Execution planning sits at standard with exactly 3 of 6 implement-feature phases non-deep, so a first-attempt rejection of that phase promotes it and the per-run non-deep share can fall below the bar | medium | low | the declaration meets the bar and the coverage check enforces it; `non_deep_share` in the metrics shows the realised figure per run |
| `R-004` | The gate-rejection promotion path was verified through the real state engine record and the counter, not through a full authorised rollback command run | low | low | the counter reads the same supersessions list the state engine appends to, and the promotion arithmetic is shared with the validator-rejection path that was run end to end |

## Handoff Notes

- Reviewer focus areas: the resolver and counter in `framework_runtime.py` (`C-002`), especially that only validator rejections ledgered under the phase and supersessions count and that the ceiling holds; the declaration (`C-001`) as a reviewed change set, since a wrong assignment routes a deep phase to a cheaper reader; the deviation on absent-file behaviour (`V-001`); and the three pre-existing verifier failures (`R-001`).
- Follow-up work: confirm with the host that both non-inherit hint values are accepted as per-dispatch overrides and that the dispatching session passes them; consider whether the promotion rule should also read gate rejections that were never rolled back, which this change deliberately does not.
- Documentation impact: `config/runtime.md` gains the Model Tiers section and `config/execution-engine.md` lists the new envelope field; the user guide and the runtime README were not changed and carry no tier description.

## Open Questions

None identified.
