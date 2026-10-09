```yaml
bugAnalysis:
  analysisId: BA-run-5f4422f26c3e-triage-and-impact
  defectReference: verify-validators-v4-instance-selection
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/verify-validators-v4-instance-selection-defect-report.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:baeb1ae26b580213f84ddc74c1193155
  contextDigest: sha256:af95bb67d09092740f15c6736e259409
```

## Metadata

- Bug ID: verify-validators-v4-instance-selection
- Reporter: a person, through a defect report written after the previous repair run's own verification
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: The validator coverage verifier reports 5 of 6 checks and NOT COVERED; its V4 check fails for orchestration-result.md, saying no mutation anchor was found in the selected instance, while the validator itself accepts that instance and rejects the mutation on the other four committed instances.
- Expected behavior: V4 should reach a verdict from an instance of each type to which the declared mutation applies, independent of which run committed last, and fail only when no candidate can carry it, per the supplied defect report.
- First observed date: Unknown; no later than 2026-10-09, when this run reproduced it. It appeared once the previous repair run committed its closure record.
- Affected environments: Known affected, this working tree run from the repository root. Known affected differently, a run from inside the framework directory, which also fails V3 for the change proposal type (E-012). Not observed, the main checkout and hosted CI.

## Reproduction

- Preconditions: The working tree as found, with the run evidence of run-d8937789961e committed under runs; the working location is the repository root; no source changed between attempts.
- Steps to reproduce: From the repository root, run the interpreter on runtime/verify_validators.py inside the framework directory. Read the V4 line and the final summary line. Then run a read-only probe that imports the same module and, for each of the 13 registered types, lists every committed instance, whether the mutation resolves an anchor on it, and whether its validator accepts it.
- Reproduction frequency: deterministic
- Evidence: Evidence Register below, E-001 to E-004 for the attempts.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | The verifier run twice from the repository root: V1, V2, V3, V5, V6 pass; V4 fails with one finding, no mutation anchor for orchestration-result.md; summary 5/6 NOT COVERED; the other twelve types are caught by their named check | Command: the verifier script under runtime, run from the repository root | high |
| `E-002` | The selector takes the last committed instance in sorted run order, consults the governance source and fixture only when none is committed, and never tests the mutation against it; the V3 and V4 loop validates and mutates that one same instance | File read: runtime/verify_validators.py, committed_instances, conforming_instance, main V3/V4 loop | high |
| `E-003` | When the mutation derivation returns nothing, resolve_mutation reports no anchor and mutation_verdict returns a V4 finding; no code path tries another instance | File read: runtime/verify_validators.py, resolve_mutation, mutation_verdict | high |
| `E-004` | Measured over all 13 types and 89 committed instances: exactly one pair lacks the anchor, orchestration-result.md from run-d8937789961e; every other instance is anchored, accepted by its validator, and its mutation is caught by the named check. Counts per type, committed/lacking: bug-analysis 8/0, execution-plan 12/0, change-proposal 0 committed (18 governance records, 0 lacking), implementation-report 14/0, investigation-report 1/0, orchestration-result 5/1, release-note 8/0, requirement-framing 1/0, review-package 9/0, scope-definition 10/0, technical-design 14/0, technical-recommendation 1/0, validation-report 6/0 | Command: read-only probe in the session scratchpad importing the verifier module; nothing written to the repository | high |
| `E-005` | In all five committed closure records the row for PH-005 is identical in gate (Closure Gate), decision (none) and recorded decider (not-applicable); the four that anchor render the phase and owner cells with backticks, run-d8937789961e renders them plain; the derivation selects rows only if the text contains the backticked phase identifier | Files read: the five committed orchestration-result.md records; runtime/verify_validators.py, award_itself_its_own_gate | high |
| `E-006` | A scratch variant of the row locator that accepts an unbackticked identifier finds the anchor on the run-d8937789961e record, and its validator then rejects the mutated record by O4 alone | Command: read-only probe in the session scratchpad; no repository file changed | high |
| `E-007` | No contract text requires backticked identifiers in this artifact: no match for backtick in the orchestrator agent modules, the template, or the orchestration validator, which accepts the run-d8937789961e record 34 of 34 | Command: text search of the orchestrator modules, template and validator; validator run in E-004 | high |
| `E-008` | The run-d8937789961e closure record is the newest committed orchestration result and was committed by the previous repair run for this verifier | Files read: runs/run-d8937789961e closure artifact; sorted run order in E-002 | high |
| `E-009` | Four types have no fixture: execution-plan, scope-definition, technical-design, framework-change-proposal; the other nine have a fixture that carries the anchor; three types have a single committed instance: investigation-report, requirement-framing, technical-recommendation | Command: read-only probe in the session scratchpad | high |
| `E-010` | The summary prints the expected check, not the observed one, on the mutation line of a failing type: orchestration-result.md is shown as caught by O4 with all-checks None although V4 failed for it | Command: output of E-001, Mutation results block | high |
| `E-011` | The previous triage probed only the seven literal-anchored types, listed the six derived types as already fixed, rejected newest-with-anchor selection as weakening, and scoped regression to six literal types, none being orchestration-result | File read: runs/run-d8937789961e triage artifact, evidence and Fix Strategy | high |
| `E-012` | Run from inside the framework directory the verifier reports 4/6: V3 also fails, the change proposal type rejected by F7, in addition to the same V4 finding | Command: the verifier run with the framework directory as working location | high |
| `E-013` | The release checklist makes check FR-02, the verifier run, mandatory and owned by omn-qa | File read: validation/framework-release-checklist.md | high |
| `E-014` | The supplied report states the cause as a closure record carrying only a row naming gate none, says the earlier conclusion of no fallback was refuted, and asserts severity medium | Supplied input: runs/inputs/verify-validators-v4-instance-selection-defect-report.md | low |

## Impact Assessment

- User impact: Operators and omn-qa running the release checklist cannot obtain a clean FR-02 result; no end user or product behavior is touched. Affected: everyone verifying a framework change while the closure record of run-d8937789961e is the newest of its type.
- Business impact: No business impact statement was supplied; severity rests on technical impact alone, and the report's statement that FR-02 fails is recorded as context (E-013, E-014).
- Technical impact: A false negative in a coverage check, failing closed: V4 reports orchestration-result.md as unproven although its validator rejects the mutation (E-006). No data is corrupted and no validator decision changed. The verifier verdict is a function of which run committed last and of how that run rendered identifiers, not of validator behavior. Severity medium: a secondary verification path fails with the stated check unable to run, no wrong pass, and a manual per-type check as workaround.
- Blast radius: The V4 and V3 checks of the verifier, which share the one selected instance for all 13 types; the FR-02 gate of the release checklist and the self-hosting release verification that runs it; the O4 mutation proof of the orchestration validator; the bundled payload mirror of the verifier; the automated test over mutation resolution. Measured extent today: 1 of 89 committed instances lacks its anchor, in 1 of 13 types, and 12 types are unaffected (E-004). Reachable under other preconditions: any type whose newest instance is rendered differently from its predecessors, and the three single-instance types with only a fixture to fall back to (E-009). Persisted bad data: none; committed run evidence is read-only and not at fault. Not observed: main checkout and hosted CI.

## Root Cause Analysis

- Root cause statement: The orchestration mutation locates its target row by a backticked identifier rendering that the artifact contract leaves free, and the instance selector takes the newest committed record without testing that the mutation applies to it, so any conforming record rendered differently from its predecessors leaves V4 with nothing to mutate; triage-level, to be confirmed in root-cause analysis.
- Why detection failed earlier: No check exercised the selector against the committed instances of every type, so the one-instance-per-type assumption was never measured; the previous triage probed only literal-anchored types and called the derived ones safe (E-011), and the repair run that produced the fragile record ran its verifier before committing that record.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Trigger: new run evidence | The previous repair run committed a closure record that renders its phase and owner cells without backticks, and it became the newest orchestration result | `E-005`, `E-008` | high |
| `C-002` | Format-dependent locator | The derivation selects the owned row only if the text contains the backticked phase identifier, a rendering neither the template, the contract nor the validator requires | `E-005`, `E-007` | high |
| `C-003` | No anchor on this instance | The row that anchors the four other records, PH-005 with gate Closure Gate, is not found in this record, though its gate, decision and decider are identical | `E-005`, `E-006` | high |
| `C-004` | Selection without applicability | The selector returns the newest committed instance and neither tests the mutation against it nor tries older instances, so one unanchored record decides the type | `E-002`, `E-004` | high |
| `C-005` | V4 records a gap | resolve_mutation returns no anchor, mutation_verdict returns a finding, and V4 fails without ever exercising the validator | `E-003`, `E-001` | high |
| `C-006` | Symptom | V4 fails, the run reports 5 of 6 NOT COVERED, and FR-02 cannot pass | `E-001`, `E-013` | high |

## Fix Strategy

- Proposed fix: V4 must use, for each type, an instance that is conforming and to which the declared mutation applies, trying committed instances newest to oldest, then the governance source, then the fixture, and fail only when none can carry it, naming every candidate tried; V3 must be checked against that same instance; the row location for the orchestration mutation must not depend on identifier rendering the contract leaves free; V4 must still fail when a validator accepts the mutation or rejects it by another check; the mutation line must report the observed outcome. No committed run evidence, validator, template or fixture is altered. Persisted bad data: none.
- Alternative options: Normalise the rendering by requiring backticked identifiers in the orchestration contract; it removes this trigger but changes a validator and template contract and leaves the selection class open. Or fix only the locator; it clears today's failure but leaves V4 dependent on the newest instance for the other 12 types, which the report names as the class.
- Regression risk: medium
- Regression scope: V3 acceptance of the selected instance, connected through the shared selector; the mutation verdict for all 13 types, since each now resolves through the changed selection; the single-instance types investigation-report, requirement-framing and technical-recommendation, which fall to a fixture once their one record fails to anchor; the FR-02 gate and the self-hosting release verification, which consume the verifier summary; the bundled payload mirror, connected by the payload sync test; the existing automated test over mutation resolution, which pins the current selection.

## Validation Plan

- Verification steps: Repeat the reproduction on unchanged run evidence and expect V4 to pass with orchestration-result.md caught by O4; present the selector a newest instance lacking the anchor above an older one that has it, and expect the older to be used; present a type where no candidate can carry the mutation, and expect a loud V4 failure naming every candidate; present a validator that accepts the mutation, and expect V4 to fail, so the cause and not merely the symptom is shown removed.
- Regression tests added: Tests under tests that fail before the fix and pass after: newest instance without the anchor with an older one that has it; no candidate able to carry the mutation; an orchestration record with unbackticked identifiers resolving its anchor; V3 run on the instance V4 used; a sweep asserting every registered type resolves an anchor on each of its committed instances.
- Monitoring signals after release: V4 detail text containing no mutation anchor, or any pair of type and instance reported without an anchor by the sweep, on any release verification; FR-02 failing after a run commits an artifact of any registered type.

## Closure

- Resolution summary: None identified.
- Linked PR and release: None identified.
- Prevention actions: Measure instance selection against every committed instance of every type as a standing test, and require a derived mutation to locate its target by meaning rather than by rendering; the Triage Gate and closure remain with omn-tech-lead and the gate owners.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Should the orchestration contract fix identifier rendering, or must every verifier locate rows by meaning; routed as a contract decision, since a validator change is not this role's to propose | no | architect | `C-002` |
| `Q-002` | Do the count-based derivations (review package counts 1 to 9, options evaluated 2 to 39, met 0 to 39) leave no anchor on a boundary instance; read in code, not measured on any instance | no | omn-dev-1-implement | `C-004` |
| `Q-003` | The V3 failure for the change proposal type when run from inside the framework directory is a separate defect, F7 by working location; confirm and route | no | omn-tech-lead | none |
| `Q-004` | The main checkout and hosted CI were not observed; does the failure reproduce there with their run evidence | no | omn-qa | none |
| `Q-005` | No business impact statement was supplied; confirm medium against release cost | no | omn-product-owner | none |
