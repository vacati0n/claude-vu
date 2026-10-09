```yaml
reviewPackage:
  packageId: RP-2026-0009
  reviewReference: run-ded114f50a46 quality-review, per-phase model tier in the dispatch envelope (IR-2026-0010)
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/model-tier-feature-request.md
    - type: change-request
      reference: runs/inputs/model-tier-change-request.md
    - type: business-intent
      reference: runs/inputs/model-tier-business-intent.md
    - type: architecture-context
      reference: runs/inputs/model-tier-architecture-context.md
    - type: implementation-report
      reference: runs/run-ded114f50a46/states/implementation/artifacts/implementation-report.md
    - type: design-reference
      reference: runs/run-ded114f50a46/states/solution-design-and-risk-assessment/artifacts/technical-design.md
    - type: code-diff
      reference: working-tree change set against HEAD for the thirteen paths the change account declares
    - type: test-evidence
      reference: inline
  producedBy: omn-dev-2-reviewer
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: complete
  verdict: approve-with-corrections
  inputDigest: sha256:2f957a695c8848e0db7db11e297e8647
  contextDigest: sha256:7c56e10872c3a10df579c4c56767bfbe
```

## Metadata

- Review ID: RP-2026-0009
- Reviewer: omn-dev-2-reviewer
- Change under review: run-ded114f50a46, implementation report IR-2026-0010 (digest sha256:538f1c74a4178bc1d543d1375ccfc087), change-set entries C-001 to C-013: the tier declaration `.claude/config/model-tier-policy.json`, the loader, rejection counter, resolver and envelope record in `.claude/runtime/framework_runtime.py`, per-tier metrics in `.claude/runtime/execution_metrics.py`, checks C7 and C8 in `.claude/runtime/verify_registry_coverage.py`, `tests/test_model_tier.py`, the two governance documents, and the bundled mirror
- Review date: 2026-10-08

## Review Scope

- In scope: every path of the change set C-001 to C-013, read as the working-tree diff against HEAD plus the two untracked files, measured against technical design decisions D-001 to D-005, constraints C-001 to C-013, the Phase-to-Tier Mapping, deviation V-001, and acceptance criteria A-001 to A-021; with specific checks on escalation derived only from recorded state, monotonicity and the deep ceiling, additivity of the envelope field and replay stability (M14), default behaviour with the declaration absent, mirror parity, decisiveness of C7 and C8, and the absence of any agent module or Phase Model edit
- Out of scope: host-side application of the hint (the runtime cannot observe it; recorded as residual risk R-002 of the change account), formal acceptance-criteria validation (owned by omn-qa), and the pre-existing verifier failures X1 and S8, which were attributed rather than reviewed as defects of this change; no repository path outside the change set was found modified (`git status` and a recursive comparison of HEAD against the working tree list only the thirteen declared paths plus this run's own evidence)
- Evidence reviewed: the full `git diff` of the ten modified paths; `.claude/config/model-tier-policy.json` and `tests/test_model_tier.py` in full; the technical design (sha256:4df24c0b76d46462bbabede130e926b5 per the change account) in full; the implementation report in full; the four supplied inputs; `cmd_complete`, `record_gate_decision`, the transport-failure branch, and `RecoveryLedger` source read to confirm what the rejection counter reads; the implementer's baseline verifier transcript for verify_multi_phase; and the results of the commands listed under Test Adequacy Assessment, all run on exported copies of HEAD and of the working tree outside the repository

## Findings

| ID | Severity | Category | Location | Requirement | Finding | Correction Request | Status |
|---|---|---|---|---|---|---|---|
| `F-001` | medium | maintainability | `.claude/runtime/framework_runtime.py:4301` | Design D-001 (reserved `inherit` value for the standard tier) and hard constraint C-005 (a phase with no declaration inherits the host model) | `load_model_tier_policy` accepts any non-empty string as the standard hint, and C7 does not check it either, so an edited declaration silently makes undeclared phases and absent-entry phases stop inheriting; the guarantee rests only on a unit test of the shipped file, not on the load boundary installed copies pass through | `CR-001` | open |
| `F-002` | low | standards | `.claude/config/runtime.md:305` | Acceptance criterion A-020 and statement S-008 (the governance documentation states the escalation rule); deviation V-001 | The Model Tiers section says one tier higher per recorded rejection without stating the V-001 exception that an absent declaration file never promotes, and says a phase with no entry resolves to `inherit`, which holds only while the standard hint is `inherit` (see F-001); documented and implemented behaviour diverge on the absent-file path | `CR-002` | open |
| `F-003` | low | test-adequacy | `tests/test_model_tier.py:387` | Testing Strategy S07 (map tests directly to acceptance criteria) and design Test Strategy Focus Areas items 2 and 4 | The suite does not compare original envelope fields against a pre-change envelope (A-006 only asserts presence and four values), does not drive gate-rejection promotion through a real `rollback` command (A-009, acknowledged as R-004), and does not assert the `inherit` branch of the prompt tier line; this review confirmed all three by execution, so the gap is regression protection, not present behaviour | `CR-003` | open |

## Severity Summary

- Critical: 0
- High: 0
- Medium: 1
- Low: 2

## Standards and Architecture Conformance

- Coding standards: necessity and reuse ladder of S01 applied to every change-set entry; the one new file is justified by the design's reuse table, the loader reuses the `load_gate_policy` optional-file pattern, metrics and verifier extend existing modules, no new dependency or abstraction; the C7 pinned category sets are a second statement of nine tier assignments, made by design D-005 and raised as Q-001 rather than as a finding; conforms apart from F-001
- Architecture rules: design D-001 to D-005 and constraints C-001 to C-013; the declaration matches the Phase-to-Tier Mapping row for row (37 phases, 14 light, 14 standard, 9 deep); the resolver is pure and reads only the recovery ledger (state id plus reason code `validation_failed`) and the work item's `supersessions`, gate rejections ledger under the gate's own state id and transport failures under `tool_failure`, so neither counts; promotion is one tier per rejection, capped at deep, never lowered; the envelope gains one top-level field and the payload digest and idempotency key do not read it; no agent module, entrypoint, Phase Model table, gate matrix, validator, template or registry file changed; conforms apart from F-001
- Security criteria: Security Engineering S09; the declaration holds alias strings only, no credential or secret; the runtime makes no model call and adds no vendor dependency; hints are copied into the envelope and prompt verbatim from a file in the managed framework directory, which carries the same trust as runtime code; a tampered declaration changes which reader handles a phase but not which validator or gate decides it (design R-009, pinned by C7); conforms
- Exceptions requested: None identified.

## Test Adequacy Assessment

- Test evidence reviewed: confirmed by this run, each on exported copies of HEAD and of the working tree outside the repository: `python -m unittest tests.test_model_tier tests.test_bundled_payload -v` ran 54 tests OK; `python -m unittest discover -s tests` ran 595 OK on HEAD and 638 OK on the changed tree; `python .claude/runtime/verify_registry_coverage.py` 6/6 on HEAD and 8/8 on the changed tree; `verify_manifests.py` 2/2, `verify_validators.py` 6/6, `verify_vertical_slice.py` 10/10, `verify_multi_phase.py` 15/15 including M14 on both trees; `verify_recovery.py` 73/74 on both trees failing only X1, on placeholder arguments in the clearing action of its own injected policy-violation run run-d8870619db82; `verify_self_hosting.py` failing only S8 on both trees, on run-5df08e171670 at HEAD and additionally on this in-progress run on the changed tree; byte comparison of the six mirrored paths found zero differences; `plan` plus `dispatch` of the same request on both runtimes produced envelopes that differ only by the added `model_tier` field and by the timestamp-derived `built_at`, `frozen_at` and task-context digest; `verify_recovery.py --keep` on the changed copy showed execution-planning promoted standard to deep after one validator rejection and after a real gate rejection with rollback, with `escalated` true on the event; claimed but not reproduced: the change account's statement that multi-phase M6 fails, since the implementer's own baseline transcript shows M6 failing on this run while implementation was still running and it now passes, so it was run state, not code
- Coverage of changed behavior: C-001 by T-001 and C7; C-002 resolver, loader and counter by T-002, T-003, T-004 and T-007, escalation from recorded state confirmed end to end for validator rejection and gate rollback; C-003 by T-005 and T-007; C-004 by T-006 including a failing flat resolver, so C8 is decisive rather than tautological, and C7 fails on a removed entry, a stale entry, an absent file and a breached bar; C-005 is the suite; C-006 and C-007 by T-001; C-008 to C-013 by T-008 and the byte comparison; every change-set entry is cited by at least one executed check
- Gaps requiring new tests: handed to omn-qa: an automated field-by-field comparison of the original envelope fields against a pre-change envelope (A-006), gate-rejection promotion through a real `rollback` command (A-009), the `inherit` branch of the prompt tier line, and a load-time rejection of a non-`inherit` standard hint once CR-001 lands (F-003, F-001)

## Correction Requests

| ID | Addresses | Required change | Blocking | Owner |
|---|---|---|---|---|
| `CR-001` | `F-001` | A declaration whose standard tier does not carry the reserved `inherit` value is refused at load time or reported by the release verifier, so that C-005 holds for every installed declaration and not only for the shipped one | no | omn-dev-1-implement |
| `CR-002` | `F-002` | The Model Tiers section of `config/runtime.md` states that an absent declaration never promotes (V-001) and that a phase with no entry takes the standard tier's hint, and the mirror is refreshed by the synchronisation command | no | omn-dev-1-implement |
| `CR-003` | `F-003` | Executed tests cover A-006 against a pre-change envelope, A-009 through a real rollback, and the `inherit` prompt branch | no | omn-qa |

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: tiers are advice; the saving depends on the dispatching session passing the hint as the per-dispatch override, which the runtime cannot observe (change account R-002); a first-attempt rejection of execution-planning drops a run below 3 of 6 non-deep invocations (change account R-003); until CR-001 lands an edited standard hint breaks inheritance for undeclared phases (F-001)
- Monitoring required: `non_deep_share` in `execution-metrics.json` of each implement-feature run; self-hosting S8 must account for run-ded114f50a46 through its change proposal at closure, while run-5df08e171670 remains a pre-existing unaccounted run; recovery X1 stays pre-existing and unrelated to this change

## Verdict

- Decision: approve-with-corrections
- Rationale: no critical or high finding exists, test evidence was reviewed and reproduced, the full declared scope was examined, and one medium and two low findings remain open, so the Stage 8 table yields approve-with-corrections with status complete
- Blocking findings outstanding: None identified.
- Readiness recommendation: recommend that the Review Gate owner proceed, with CR-001 to CR-003 carried as non-blocking corrections; the gate decision belongs to the owner named in `workflows/workflow-gate-matrix.md`, not to this review

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| `Q-001` | Do the PINNED_LIGHT and PINNED_DEEP sets in `.claude/runtime/verify_registry_coverage.py`, required by design D-005, count as a second tier assignment under acceptance criterion A-003, or as verification of the one declaration | no | omn-qa | acceptance of A-003; no finding or verdict here |
