```yaml
bugAnalysis:
  analysisId: BA-run-d8937789961e-root-cause
  defectReference: verify-validators-v4-anchor
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/verify-validators-v4-anchor-defect-report.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:1ef34a52237bc465ce0df969d097a321
  contextDigest: sha256:a88575c76fff3cf25d7bf5c9ee10d8b8
```

## Metadata

- Bug ID: verify-validators-v4-anchor
- Reporter: operator, through a supplied defect report
- Severity: medium
- Status: complete

## Symptom Summary

- Observed behavior: The validator coverage verifier, run from the repository root, ends at 5 of 6 checks passed and reports NOT COVERED; check V4 fails with one finding, no mutation anchor for investigation-report.md in the selected instance, while every other artifact type passes V3 and V4 (E-001).
- Expected behavior: Per the defect report, V4 should not depend on which artifacts runs happened to commit; for every registered type it should find an instance carrying what its mutation needs and still prove the validator rejects the mutated artifact by the named check.
- First observed date: Unknown; after run-437e2f765e4b committed its investigation report on 2026-10-09; the last recorded clean result is the coverage report of 2026-08-18 (E-013).
- Affected environments: Known affected: this worktree, run from its repository root. Known unaffected: none observed. Not observed: the main checkout, a hosted CI run, any other worktree.

## Reproduction

- Preconditions: The run evidence holds exactly one committed investigation report, from run-437e2f765e4b, which evaluates O-001 to O-004 and recommends O-003; tracked runtime and template files unchanged against the last commit; run from the repository root.
- Steps to reproduce: From the repository root run python runtime/verify_validators.py. Read the V4 line and the final summary line. Expect FAIL for V4 naming investigation-report.md with no mutation anchor, and the summary 5/6 checks passed, NOT COVERED. Repeated in this phase with the same result; triage observed it three times.
- Reproduction frequency: deterministic
- Evidence: Evidence Register below; the reproduction is E-001, re-run in this phase, and its in-memory counterpart is E-019.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Verifier from the repository root: V4 FAIL, one finding, no mutation anchor for investigation-report.md; V1, V2, V3, V5, V6 PASS; the selected investigation report passes V3 at 31 of 31; summary 5/6 NOT COVERED | Command: python runtime/verify_validators.py, re-run this phase | high |
| `E-002` | The MUTATIONS row pins the investigation-report mutation to the recommended-option line naming O-002, replaced by one naming O-009; committed_instances collects accepted artifacts in sorted run order; conforming_instance returns the last and consults the fixture only when none is committed; V4 records no anchor when the literal is absent | File read: runtime/verify_validators.py, MUTATIONS, committed_instances, conforming_instance, V3/V4 loop | high |
| `E-003` | The committed investigation report (run-437e2f765e4b, technical-discovery) recommends O-003; the fixture recommends O-002 and evaluates O-001 to O-003 | Files read: that report; runtime/fixtures/investigation-report.md | high |
| `E-004` | Probe over the seven literal-anchored types: execution-plan 12 of 12 committed carry the anchor, implementation-report 13 of 13, scope-definition 10 of 10, technical-design 14 of 14, requirement-framing 1 of 1, change proposal from the governance source carries it, investigation-report 0 of 1 | Command: read-only probe in the session scratchpad importing verify_validators | high |
| `E-005` | Rule I1 passes when every option id named in the recommended-option field is defined in the Options Evaluated section; the template fixes no value | Files read: runtime/investigation_report_validator.py, templates/investigation-report.md | high |
| `E-006` | The implementation-report validator accepts only review status pending-review (M6), so that literal is pinned by the contract; the plan Risks and design Sign-off literals are mandatory headings of their templates | Files read: runtime/implementation_report_validator.py, templates/execution-plan.md, templates/technical-design.md | high |
| `E-007` | git diff against the last commit shows no change under runtime or templates; run-437e2f765e4b, this run, and FC-017 are untracked | Command: git status and git diff --stat HEAD | high |
| `E-008` | Six artifact types already derive their mutation from the instance, and their docstrings record that earlier literals went dead the same way when a real run replaced the fixture | File read: runtime/verify_validators.py, derivation functions | high |
| `E-009` | The release checklist makes FR-02 the verifier command, mandatory, owned by omn-qa | File read: validation/framework-release-checklist.md | high |
| `E-010` | The defect report states: 6 of 6 before run-437e2f765e4b; run identifiers are content hashes; release verification is blocked; severity medium | Supplied input: runs/inputs/verify-validators-v4-anchor-defect-report.md | low |
| `E-011` | No test file under tests references verify_validators; confirmed by search of the tests directory this phase | Command: content search of tests | high |
| `E-012` | A run identifier is run- followed by the first 12 hex digits of a sha256 over command, workflow, and input digest, so sorted run order is content-hash order | File read: runtime/framework_runtime.py, make_run_id | high |
| `E-013` | The coverage report of 2026-08-18 (runtime 0.4.0) records pass, with the investigation report taken from the fixture and its mutation failing C6.2 and I1; git tracks no committed investigation report; the verifier, validator, fixture, and template were last changed in one commit | Files read: reports/validator-coverage-2026-08-18.json; command: git ls-files and git log | medium |
| `E-014` | Probe: the committed report evaluates O-001 to O-004 and recommends O-003, so the literal is absent; on the fixture the literal mutation is rejected with C6.2 and I1 | Command: read-only probe in the session scratchpad | high |
| `E-015` | The shared engine requires option ids in three-digit form (C6.1), every referenced id defined (C6.2), and defined ids contiguous from 001 (C6.4); I1 reads only three-digit ids | File read: runtime/artifact_contract.py, C6 block, defined_ids, referenced_ids | high |
| `E-016` | Probe: a conforming copy of the committed report widened to nine options and recommending O-002 is accepted, carries the literal anchor, and the literal mutation is accepted, because its substitute O-009 is an evaluated option | Command: read-only probe in the session scratchpad, copies only | high |
| `E-017` | Probe: on conforming copies recommending O-002 of three options, O-005 of five, O-009 of nine, and naming O-003 and O-004 together, substituting the lowest three-digit id absent from the text yields O-004, O-006, O-010, O-005, each rejected with C6.2 and I1 | Command: read-only probe in the session scratchpad, copies only | high |
| `E-018` | Probe: single-option copies (only O-003; only O-001) are rejected unmutated by C4.5, two rows minimum; the same rule yields O-005 and O-002, absent from the text, and I1 fails | Command: read-only probe in the session scratchpad, copies only | high |
| `E-019` | In-memory probe on unchanged evidence: as shipped 5/6; with the row replaced by the derivation 6/6 COVERED, investigation report caught by I1; with a validator accepting everything V4 FAILs as mutation accepted; with I1 suppressed V4 FAILs as rejected but not by I1; git status unchanged afterwards | Command: read-only probe in the session scratchpad running main() with module state replaced in process | high |
| `E-020` | The self-hosting profile requires its second evidence row, the run ledger link, so the change-proposal literal is pinned; the scope-definition and requirement-framing templates require the count fields their literals anchor on | Files read: config/self-hosting-profile.md, templates/scope-definition.md, templates/requirement-framing.md | high |
| `E-021` | Mutation resolution and the V4 verdict are inline in main(), so no function exposes them to a test; existing tests import runtime scripts by inserting the runtime directory into the module path | Files read: runtime/verify_validators.py main(); tests/test_model_tier.py | high |
| `E-022` | The bundled payload mirror holds a byte-identical copy of the verifier | Command: file comparison against omn_agent/_bundled_payload/runtime/verify_validators.py | high |
| `E-023` | Release context requires each release to pass the quality gates | File read: context/release-context.md | high |

## Impact Assessment

- User impact: Operators and omn-qa running the release checklist see FR-02 fail and cannot obtain a clean release verification; no end user or product behavior is touched. Affected: every framework change verified while this run evidence exists.
- Business impact: From the defect report's impact statement (E-010), corroborated first-hand: FR-02 is mandatory (E-009) and every release must pass its quality gates (E-023), so no framework release can record a clean FR-02 while the defect stands; no product or end-user consequence.
- Technical impact: A false negative in a coverage check: V4 reports the investigation validator unproven although it rejects the mutation (E-019). A second latent effect: a conforming report evaluating nine or more options and recommending O-002 makes the same row produce an accepted mutation (E-016).
- Blast radius: The V4 check of the validator coverage verifier; the FR-02 gate of the release checklist and the self-hosting release verification that runs it; the investigation validator's mutation proof (I1). Persisted bad data: none; committed run evidence is conforming and not at fault. Latent reach under the same selection rule: the six other literal-anchored types, all contract-pinned (E-004, E-006, E-020). Not observed: main checkout, hosted CI.

## Root Cause Analysis

- Root cause statement: The investigation-report mutation row encodes two values copied from the fixture, recommended option O-002 as anchor and O-009 as substitute, instead of the contract invariant that a recommendation must name an evaluated option, so whether V4 can apply the mutation and whether the substitute is unevaluated both depend on which instance the selector returns, an assumption that broke when the selector, as designed, returned a conforming report recommending O-003.
- Why detection failed earlier: No test exercises the verifier against varied instances (E-011, E-021); the row was only ever run against the fixture, where it passed (E-013); and the same defect had been fixed one type at a time by deriving each mutation without sweeping the remaining literals (E-008).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Trigger: new run evidence | Run-437e2f765e4b committed the first real investigation report, evaluating O-001 to O-004 and recommending O-003 | `E-003`, `E-014` | high |
| `C-002` | Instance selection | The selector returns the last committed instance in content-hash order and no longer consults the fixture; it is not the cause, since unchanged it yields 6 of 6 once the row is derived | `E-002`, `E-004`, `E-012`, `E-019` | high |
| `C-003` | Pinned anchor and substitute | Both values of the row are fixture values: an O-003 report has no anchor, and a conforming nine-option report recommending O-002 has one but its substitute is evaluated | `E-002`, `E-014`, `E-016` | high |
| `C-004` | Contract is value-free | I1 with C6.2 and C6.4 fixes only that the recommendation lies within O-001 to O-00n; the committed report conforms, and an id outside that set is rejected for every varied instance | `E-005`, `E-015`, `E-017`, `E-001` | high |
| `C-005` | V4 records the gap | The literal is absent from the selected text, so V4 records no mutation anchor without running the validator | `E-002`, `E-001`, `E-019` | high |
| `C-006` | Symptom | V4 fails, the run reports 5 of 6 NOT COVERED, and FR-02 fails | `E-001`, `E-009` | high |

## Fix Strategy

- Proposed fix: The investigation-report row must derive its mutation from the instance under test, as the six callable rows do, keeping check I1 and its description: in runtime/verify_validators.py a new derivation function (for example recommend_an_unevaluated_option) locates the recommended-option field bullet and substitutes one backticked three-digit id, the lowest O-nnn appearing nowhere in the text, which for a conforming report is O-(n+1) and can never be evaluated because defined ids are a subset of ids in the text (E-015, E-017); the single-option case is non-conforming but still yields an absent id that I1 rejects (E-018); the function returns nothing when the field is missing or no id is free, so V4 fails loudly (E-019). Derive only: committed_instances and conforming_instance stay unchanged, with no fallback. Mutation resolution and the V4 verdict move out of main() into module functions main() calls with unchanged behavior, so a test can import them (E-021). No validator, template, fixture, or run evidence changes; the six other literal rows need no derivation now (E-004, E-006, E-020).
- Alternative options: Fall back to another instance or the fixture when the anchor is missing: smaller, but it does not cure the accepted-mutation case (E-016), leaves real instances unmutated, and keeps the outcome a function of hash order (E-012); combined with derivation it adds nothing, since derivation fails only on an instance V3 already rejects. Or always mutate the fixture: removes history dependence but stops V4 proving the validator on real artifacts. Or mutate every committed instance: strongest proof, but widens V3 to older artifacts and changes the verifier's scope.
- Regression risk: medium
- Regression scope: V4 for investigation-report.md, through the derived substitute, which also trips C6.2 as the literal did; V3 and V4 for all thirteen registered types, through the loop extracted from main(); the summaries and json-out record of schema validator-coverage.v1, through the same loop; FR-02 and the self-hosting release verification, which consume the verifier summary; the bundled payload mirror, through the payload parity test (E-022).

## Validation Plan

- Verification steps: Repeat the reproduction on unchanged run evidence and expect 6/6 COVERED with investigation-report.md caught by I1 from the committed instance; then run the new test file, which drives the derived row over varied instances, so the value-pinned anchor and substitute, not merely the symptom, are shown removed; then python -m unittest discover -s tests.
- Regression tests added: A new test file under tests (for example test_verify_validators_mutations.py) importing the verifier, building instances in a temporary directory from runtime/fixtures/investigation-report.md: recommendation changed to O-003 must yield an applicable mutation rejected by I1; a conforming nine-option copy recommending O-002 must be rejected by I1; a single-option copy must get an id absent from its text; a copy without the field must yield none; the V4 verdict must report a finding for a stub validator accepting the mutation and for one rejecting by another check; every MUTATIONS row must resolve against its fixture. The first two fail before the fix and pass after.
- Monitoring signals after release: V4 detail text containing no mutation anchor or mutation accepted on any release verification; FR-02 failing after a new run commits an artifact of any registered type.

## Closure

- Resolution summary: None identified.
- Linked PR and release: None identified.
- Prevention actions: The new test file exercising mutation rows against varied instances (E-011, E-021), and a rule that a new mutation row is derived from the instance unless its literal is pinned by the artifact contract.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Answered in this phase and retained so identifiers are not renumbered: the chain held against varied instances (E-016 to E-019), no other literal row needs derivation (E-004, E-006, E-020), and both unconfirmed triage claims hold (E-012, E-013) | no | omn-dev-1-bug-analyst | `C-002`, `C-003` |
| `Q-002` | Whether release verification being blocked raises the priority of this fix is a product decision, not a severity fact | no | omn-product-owner | none |
| `Q-003` | The main checkout and a hosted CI run were not observed; omn-qa should run FR-02 there after the fix | no | omn-qa | none |
| `Q-004` | The two count rows substitute 99; a real count of 99 would make the mutation accepted and V4 fail loudly, a residual outside this defect | no | omn-tech-lead | none |
