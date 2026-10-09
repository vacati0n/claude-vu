```yaml
bugAnalysis:
  analysisId: BA-run-d8937789961e-triage
  defectReference: verify-validators-v4-anchor
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/verify-validators-v4-anchor-defect-report.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:1ef34a52237bc465ce0df969d097a321
  contextDigest: sha256:af95bb67d09092740f15c6736e259409
```

## Metadata

- Bug ID: verify-validators-v4-anchor
- Reporter: operator, through a supplied defect report
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: The validator coverage verifier, run from the repository root, ends at 5 of 6 checks passed and reports NOT COVERED. Check V4 fails with one finding: investigation-report.md has no mutation anchor in the selected instance. Every other artifact type passes V3 and V4.
- Expected behavior: Per the defect report, V4 should not depend on which artifacts runs happened to commit; for every registered type it should find an instance carrying the text its mutation needs, and still prove the validator rejects the mutated artifact by the named check.
- First observed date: Unknown; no later than this run, and after run-437e2f765e4b began on 2026-10-09, since that run committed the investigation report that triggers it.
- Affected environments: Known affected: this worktree, run from its repository root. Known unaffected: none observed. Not observed: the main checkout, a hosted CI run, any other worktree.

## Reproduction

- Preconditions: The run evidence directory holds exactly one committed investigation report, from run-437e2f765e4b, whose recommended option is O-003. Run from the repository root with no environment changes.
- Steps to reproduce: From the repository root run python runtime/verify_validators.py. Read the line for check V4 and the final summary line. Expect FAIL for V4 naming investigation-report.md and the summary 5/6 checks passed, NOT COVERED. Repeating the run gave the same result every time.
- Reproduction frequency: deterministic
- Evidence: Evidence Register below; the reproduction is E-001, observed three times with identical output.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | The verifier run three times from the repository root: V4 FAIL with one finding, no mutation anchor for investigation-report.md; V1, V2, V3, V5, V6 PASS; summary 5/6 NOT COVERED; mutation results for the other twelve types caught by their named check | Command: python runtime/verify_validators.py | high |
| `E-002` | The MUTATIONS table pins the investigation-report mutation to the literal recommended-option line naming O-002, replaced by O-009; committed_instances collects accepted artifacts of the type from every run state in sorted order; conforming_instance returns the last committed one and consults the fixture only when none is committed; V4 records a rejection when the literal is absent from the selected text | File read: runtime/verify_validators.py, MUTATIONS table, committed_instances, conforming_instance, V3/V4 loop | high |
| `E-003` | The only committed investigation report (run-437e2f765e4b, technical-discovery) has the recommended-option line naming O-003; the fixture has it naming O-002 | Files read: run-437e2f765e4b investigation-report.md; runtime/fixtures/investigation-report.md | high |
| `E-004` | Read-only probe importing the verifier: for each of the seven literal-anchored types the count of committed instances, how many contain the literal, and which is selected (last in sorted run order); the probe wrote nothing under the repository | Command: probe script held in the session scratchpad, importing verify_validators | high |
| `E-005` | Rule I1 passes when the recommended option names any option the report evaluated; the template says only an option identifier from the table above; the contract does not fix a value | Files read: runtime/investigation_report_validator.py, templates/investigation-report.md | high |
| `E-006` | The implementation-report validator accepts only the review status pending-review (rule M6), so its literal is pinned by the contract; the scope-definition and requirement-framing literals are count field names the templates require; the plan and design literals are mandatory section headings | Files read: runtime/implementation_report_validator.py, templates/scope-definition.md, templates/requirement-framing.md, MUTATIONS table | high |
| `E-007` | Tracked files under runtime and templates show no modification against the last commit; the new run directory and proposal FC-017 are untracked | Command: git status and git diff against HEAD | high |
| `E-008` | Six artifact types already derive their mutation from the instance, and their docstrings record that an earlier literal went dead for the same reason when a real run replaced the fixture (bug-analysis, release-note, count mutations) | File read: runtime/verify_validators.py, derivation functions | high |
| `E-009` | The release checklist makes FR-02 the verifier command above, mandatory, owned by omn-qa | File read: validation/framework-release-checklist.md | high |
| `E-010` | The supplied defect report states: 6 of 6 before run-437e2f765e4b; run identifiers are content hashes; the implementation-report literal has the same latent fragility; severity medium; no source changed between the two results | Supplied input: runs/inputs/verify-validators-v4-anchor-defect-report.md | low |
| `E-011` | No test file under tests references the verifier; confirmed by search of the tests directory | Command: file search of tests for verify_validators | high |

## Impact Assessment

- User impact: Operators and omn-qa running the release checklist see FR-02 fail and cannot obtain a clean release verification; no end user or product behavior is touched. Affected: every framework change verified while this run evidence exists.
- Business impact: No business impact statement was supplied; severity rests on technical impact alone, and the defect report's own statement that release verification is blocked is recorded as context (E-010, E-009).
- Technical impact: A false negative in a coverage check: V4 reports a validator as unproven when the validator was never shown to fail. No data is corrupted and no validator behavior changed. A latent second effect: the verifier outcome is a function of run history rather than of validator behavior.
- Blast radius: The V4 check of the validator coverage verifier; the FR-02 gate of the framework release checklist and the self-hosting release verification that runs it; the investigation validator's mutation proof (I1). Persisted bad data: none written; committed run evidence is read-only here and is not at fault. Latent reach, under the same selection rule: six other literal-anchored types, listed in the Regression scope, none of which fail now. Environments not observed: main checkout, hosted CI.

## Root Cause Analysis

- Root cause statement: The mutation anchor for the investigation report is pinned to one option identifier that the artifact contract leaves free, while the instance selector prefers the last committed run artifact without checking that it carries the anchor, so any genuine report recommending a different option leaves V4 with nothing to mutate.
- Why detection failed earlier: No check tested the verifier's own selection against varied instances; no test under tests references the verifier (E-011), and the same defect had already occurred and been fixed for other types one at a time by making each mutation derived, without sweeping the remaining literals (E-008).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Trigger: new run evidence | Run-437e2f765e4b committed the first real investigation report, recommending O-003 | `E-003`, `E-004` | high |
| `C-002` | Instance selection | The selector takes the last committed instance and no longer consults the fixture, so the only committed report becomes the sole sample | `E-002`, `E-004` | high |
| `C-003` | Pinned anchor | The investigation-report mutation searches for the line naming O-002, a value taken from the fixture, not from the contract | `E-002`, `E-003` | high |
| `C-004` | Contract is value-free | The validator accepts any evaluated option as recommended, so O-003 is a conforming value and the instance is not at fault | `E-005`, `E-001` | high |
| `C-005` | V4 records the gap | The literal is absent from the selected text, so V4 records no mutation anchor and fails without exercising the validator | `E-002`, `E-001` | high |
| `C-006` | Symptom | V4 fails, the run reports 5 of 6 NOT COVERED, and FR-02 fails | `E-001`, `E-009` | high |

## Fix Strategy

- Proposed fix: The investigation-report mutation must be derived from the instance under test, as the six other derived types are, so that it works for any evaluated recommendation and substitutes an option identifier the report never evaluated; V4 must still fail when the validator accepts the mutation or rejects it by a different check; the other literal-anchored types are assessed in the same change and altered only where their literal is not pinned by their contract. No committed run evidence, validator, or template is altered.
- Alternative options: Make the selector prefer the last instance that carries the anchor and fall back to the fixture otherwise; it is smaller but lets V4 silently test a fixture while real instances go unmutated, and so weakens the proof. Or require the fixture sample always; it removes the dependence on run history but stops V4 testing real artifacts, which the earlier selection rule chose deliberately.
- Regression risk: medium
- Regression scope: The investigation validator rule I1, reached because the derived substitute must be an unevaluated option or the rejection is attributed to the wrong check; the other six literal types (implementation-report review status, scope-definition criteria count, requirement-framing requirement count, execution-plan Risks heading, technical-design Sign-off heading, change-proposal ledger link), each connected through the same MUTATIONS table and selector; V3 acceptance of the selected instances, which share the selector; the self-hosting release verification and FR-02, which consume the verifier summary; the bundled payload mirror of the verifier, connected by the payload sync test.

## Validation Plan

- Verification steps: Repeat the reproduction on unchanged run evidence and expect V4 to pass with the investigation report caught by I1; then offer the selector instances recommending different options and expect V4 to hold for each; confirm it still fails when a validator is made to accept the mutation, so that the cause (a value-pinned anchor) and not merely the symptom is shown removed.
- Regression tests added: A test under tests, run by python -m unittest discover -s tests, that fails before the fix and passes after: it supplies an investigation report recommending an option other than O-002 and asserts the mutation can be applied and is rejected by I1; plus a test that a validator accepting the mutation still fails V4; plus a sweep asserting every table row can be applied to an instance varying its free values.
- Monitoring signals after release: V4 detail text containing no mutation anchor on any release verification; FR-02 failing after a new run commits an artifact of any registered type.

## Closure

- Resolution summary: None identified.
- Linked PR and release: None identified.
- Prevention actions: Add the test under tests that exercises the verifier against varied instances (E-011), and require every new mutation row to be derived from the instance unless its literal is pinned by the artifact contract.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | The root-cause-analysis phase must confirm the chain by re-running the probe against a varied second investigation instance, and decide which of the six latent literals, if any, need derivation; the defect report's statements that the verifier passed 6 of 6 beforehand and that run identifiers are content hashes were not confirmed here | no | omn-dev-1-bug-analyst | `C-002`, `C-003` |
| `Q-002` | No business impact statement was supplied; whether release verification being blocked changes priority is for the product owner | no | omn-product-owner | none |
