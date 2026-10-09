```yaml
bugAnalysis:
  analysisId: BA-run-5f4422f26c3e-root-cause-analysis
  defectReference: verify-validators-v4-instance-selection
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/verify-validators-v4-instance-selection-defect-report.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:baeb1ae26b580213f84ddc74c1193155
  contextDigest: sha256:a88575c76fff3cf25d7bf5c9ee10d8b8
```

## Metadata

- Bug ID: verify-validators-v4-instance-selection
- Reporter: a person, through a defect report written after the previous repair run's own verification
- Severity: medium
- Status: complete

## Symptom Summary

- Observed behavior: The validator coverage verifier reports 5 of 6 checks and NOT COVERED; V4 fails for orchestration-result.md with no mutation anchor in the selected instance, while the console mutation line for that type still reads caught by O4 with all-checks None.
- Expected behavior: V4 should reach a verdict for every type from an instance the declared mutation applies to, independent of which run sorts last, and fail loudly naming every candidate only when none can carry it, per the supplied defect report.
- First observed date: Unknown; no later than 2026-10-09, when the triage phase and this phase reproduced it; it appeared once run-d8937789961e committed its closure record.
- Affected environments: Known affected, this working tree from the repository root (V4 only) and from inside the framework directory (V4, plus a separate V3 failure, E-012). Not observed, the main checkout and hosted CI.

## Reproduction

- Preconditions: The working tree as found, with the run evidence of run-d8937789961e and of this run's triage phase committed under runs; working location the repository root; no source changed between attempts; scratch probes import the verifier and patch functions in memory only, and the working-tree status was compared before and after every probe and found unchanged.
- Steps to reproduce: From the repository root, run the interpreter on runtime/verify_validators.py inside the framework directory and read the V4 line, the orchestration-result.md mutation line, and the summary. Then, in a scratch directory outside the repository, import the same module and for each of the 13 registered types list every committed and governance instance, whether the declared mutation resolves an anchor on it, whether its validator accepts it, and which check rejects the mutated text.
- Reproduction frequency: deterministic
- Evidence: Evidence Register below; E-001 is the reproduction, E-004, E-006, E-016 to E-018 are the probes.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Run from the repository root in this phase: V1, V2, V3, V5, V6 pass; V4 fails with one finding, no mutation anchor for orchestration-result.md; summary 5/6 NOT COVERED | Command: runtime/verify_validators.py run from the repository root | high |
| `E-002` | The selector takes the last committed instance in sorted run order, consults the governance records and then the fixture only when none is committed, and never tests the mutation against what it returns; the V3/V4 loop validates and mutates that one instance | File read: runtime/verify_validators.py, committed_instances, conforming_instance, main | high |
| `E-003` | When the derivation returns nothing, resolve_mutation yields no anchor and mutation_verdict returns a V4 finding with checks None, without running the validator; no path tries another instance | File read: runtime/verify_validators.py, resolve_mutation, mutation_verdict | high |
| `E-004` | Re-measured over 13 types: 90 committed instances (the triage's 89 plus this run's own triage artifact) and 18 governance records; all 108 accepted by their validator; exactly one lacks the anchor, the orchestration result of run-d8937789961e; the other 107 are caught by their named check | Command: scratch probe importing the verifier, sweep with the current locator | high |
| `E-005` | In the five committed closure records the PH-005 row is identical in owner, gate (Closure Gate), decision (none) and decider (not-applicable); four render identifier and owner cells with backticks, run-d8937789961e renders them plain; the locator skips any line without the backticked phase prefix | Files read: the five committed orchestration-result.md records; award_itself_its_own_gate | high |
| `E-006` | A scratch locator matching the identifier cell with or without backticks anchors the run-d8937789961e record, and the orchestration validator rejects the mutated text by O4 alone; with that locator all 108 non-fixture instances anchor and all are caught | Command: scratch probe, sweep and end-to-end run with the locator variant | high |
| `E-007` | No rule requires backticked identifiers: the word backtick occurs in none of the orchestrator modules, the template or the validator; the shared contract engine defines identifiers with an optional backtick; the validator accepts the plain record 34 of 34 | Text search of those files; runtime/artifact_contract.py, defined_ids; E-001 summary | high |
| `E-008` | The run-d8937789961e closure record sorts last among the five orchestration results, so the selector returns it | Command: probe listing committed instances in selector order | high |
| `E-009` | Four types have no fixture (execution-plan, scope-definition, technical-design, framework-change-proposal); three types have one committed instance (investigation-report, requirement-framing, technical-recommendation) | Directory listing of runtime/fixtures; probe sweep counts | high |
| `E-010` | The console mutation line prints the expected check after the words caught by, whatever the outcome: orchestration-result.md reads caught by O4 (all: None) while V4 fails for it | Command output of E-001; main, mutation results block | high |
| `E-011` | The previous triage probed only the seven literal-anchored types, called the derived types fixed, and scoped regression to literal types, none being orchestration-result | File read: runs/run-d8937789961e triage bug-analysis.md, evidence and Fix Strategy | high |
| `E-012` | From inside the framework directory the verifier reports 4/6: V3 also fails, the change proposal FC-018 rejected by F7; the same proposal passes its validator from the repository root and fails F7 from inside, where scope rows recompute differently; the V4 finding is identical at both locations | Commands: verifier and change proposal validator run from both locations | high |
| `E-013` | Check FR-02 of the release checklist runs this verifier, is mandatory and owned by omn-qa; the release context requires every release to pass its quality gates | Files read: validation/framework-release-checklist.md; context/release-context.md | high |
| `E-014` | The supplied report states the cause as a closure record whose only owned row names gate none, says FR-02 fails whenever the newest instance lacks the anchor, and asserts severity medium | Supplied input: runs/inputs/verify-validators-v4-instance-selection-defect-report.md | low |
| `E-015` | Sorted run order is lexical on run identifiers, not chronological: run-5f4422f26c3e (created 09:13Z on 2026-10-09) sorts before run-d8937789961e (08:03Z the same day), and run-efe092286625 (2026-08-27) sorts after run-437e2f765e4b (2026-10-09) | Files read: created_at in the state.json of those runs | high |
| `E-016` | End-to-end on unchanged evidence: baseline 5/6; selection-only passes 6/6 by using the run-79630cb5274d record and skipping run-d8937789961e; locator-only and both pass 6/6 on the run-d8937789961e record caught by O4; V3 passes in all; selection with the new locator picks the same instance as today for all 13 types | Command: scratch probe running main with patched functions, JSON reports in scratch | high |
| `E-017` | Synthetic cases from the fixture: unbackticked rows conform, have no anchor under the current locator and are caught by O4 under the new one; a record whose orchestrator row carries no gate conforms and has no anchor under either locator; selection then falls back to the fixture; when no candidate applies it returns none listing every candidate; an accept-all validator still fails V4 | Command: scratch probe, synthetic files in scratch only | high |
| `E-018` | Filtering candidates on validator acceptance weakens V3: from inside the framework directory it turns the F7 rejection into no conforming instance available, and a non-conforming last candidate is silently skipped; filtering on mutation applicability alone keeps rejected F7 reported | Command: scratch probe run from inside the framework directory, both selection variants | high |
| `E-019` | The existing test module passes 15 of 15 on the defective code: it checks each row on its fixture and calls the selector only for fixtureless types; three proposed test shapes (plain rows caught by O4, fallback past an unanchored last candidate, every candidate named when none applies) fail on the current code | Commands: tests/test_verify_validators_mutations.py; scratch test file against the current module | high |

## Impact Assessment

- User impact: Operators and omn-qa running the release checklist cannot obtain a clean FR-02 result; no end user or product behavior is touched. Affected: everyone verifying a framework change while an unanchored record sorts last for its type.
- Business impact: From the supplied report's impact section (E-014), corroborated first-hand: FR-02 is mandatory and every release must pass its quality gates (E-013), so no framework release can record a clean FR-02 while the defect stands; no product or end-user consequence.
- Technical impact: A false negative in a coverage check, failing closed: V4 reports orchestration-result.md unproven although its validator rejects the mutation (E-006). No validator decision changed and no data was corrupted. The verdict depends on run-identifier sort order and on identifier rendering, not on validator behavior. Severity medium: a secondary verification path fails, no wrong pass, and a manual per-type check is the workaround.
- Blast radius: The V3 and V4 checks of the verifier, which share one selected instance per type for all 13 types; the verifier's console summary and JSON report; the FR-02 gate and the self-hosting release verification that runs it; the O4 mutation proof; the bundled payload mirror of the verifier; the automated test over mutation rows. Measured extent: 1 of 108 non-fixture instances, in 1 of 13 types (E-004). Reachable under other preconditions: any conforming record that legitimately lacks the mutation's shape, such as an orchestration record whose orchestrator row has no gate (E-017), and the three single-instance and four fixtureless types with shallow fallback (E-009). Persisted bad data: none; run evidence is read-only and not at fault. Not observed: main checkout and hosted CI.

## Root Cause Analysis

- Root cause statement: V4 binds each artifact type to one instance chosen by run-identifier sort order without testing that the declared mutation applies to it, and the orchestration mutation locates its row by a backticked identifier rendering that the shared contract engine treats as optional, so a conforming plain-rendered closure record that sorted last left V4 with nothing to mutate.
- Why detection failed earlier: No check ran the selector against every committed instance; the existing test module checks each row on its fixture and passes 15 of 15 on the defective code (E-019); the previous triage probed only literal-anchored types and called the derived ones safe (E-011); the repair run that produced the plain record ran its verifier before committing it.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Trigger: new run evidence | run-d8937789961e committed a conforming closure record rendering identifier and owner cells without backticks, and its identifier sorts last among orchestration results | `E-005`, `E-008`, `E-015` | high |
| `C-002` | Locator contract mismatch | The derivation accepts only backticked phase identifiers, while the shared contract engine and the validator accept either rendering and no rule requires backticks | `E-005`, `E-007` | high |
| `C-003` | No anchor on this instance | The PH-005 row that anchors the four other records is skipped in this one although its gate, decision and decider are identical; a rendering-neutral locator finds it and O4 rejects the mutation | `E-005`, `E-006` | high |
| `C-004` | Selection without applicability | The selector returns the last-sorted candidate with no applicability test and no fallback, so any conforming instance lacking the mutation's shape decides the type, and such instances exist under any locator | `E-002`, `E-004`, `E-017` | high |
| `C-005` | V4 records a gap | resolve_mutation yields no anchor, mutation_verdict returns a finding with checks None, and V4 fails without exercising the validator | `E-003`, `E-001` | high |
| `C-006` | Symptom | V4 fails, the run reports 5 of 6 NOT COVERED, FR-02 cannot pass, and the console line misreports the type as caught by O4 | `E-001`, `E-010`, `E-013` | high |

Alternatives tested: the reporter's account of an owned row naming gate none is eliminated, the gate is Closure Gate (`E-005`, `E-014`); a validator unable to catch the mutation is eliminated, O4 rejects it (`E-006`, `E-016`); the working-location V3 failure as the same cause is eliminated, it is F7 in another module, varies with location while V4 does not (`E-012`).

## Fix Strategy

- Proposed fix: Remove both conditions, with no change to validators, templates, fixtures or run evidence. First, the orchestration row locator must identify the row by its identifier cell under the same optional-backtick rule the contract engine uses, so the instance V4 selects today is the one it mutates (E-006, E-016). Second, selection must try candidates in a fixed order, committed instances from last to first in the existing sort order, then governance records last to first, then the fixture, and take the first on which the declared mutation resolves; it must not filter on validator acceptance, so V3 still validates exactly the instance V4 uses and still fails when that instance is rejected (E-018). When no candidate applies, V4 fails naming every candidate and why it was skipped; skipped candidates are reported even when V4 passes, so a fallback is never silent. The selector's documentation must stop calling the order newest, since it is lexical (E-015). The console mutation line must report the observed outcome instead of the expected check; it is in scope because it misreported this very failure (E-010). Selection must never consult the mutation verdict, so an accepting or wrongly rejecting validator still fails V4 (E-017). Persisted bad data: none.
- Alternative options: Selection only clears today's failure by mutating an older record and silently stops exercising plain-rendered records, the format the newest runs produce, so V4 would prove less than it reports (E-016). Locator only clears today's failure and keeps the newest instance, but leaves the class open: a conforming record with no gated orchestrator row has no anchor under any locator (E-017). Filtering candidates on conformance as well, as the report proposes, weakens V3 and hides rejections such as F7 (E-018). Ordering candidates by creation time would match the word newest but changes the selected instance for several types; keeping the existing order changes no selection today (E-016). Requiring backticks in the orchestration contract changes a validator and template, is outside this repair, and is routed as `Q-001`.
- Regression risk: medium
- Regression scope: V3 acceptance, which shares the selected instance; the V4 verdict for all 13 types through the changed selection (today identical per E-016); the single-instance and fixtureless types, whose fallback is shallow; the existing mutation-row test, which unpacks the selector's result; the console summary and JSON report read by FR-02 and the self-hosting release verification, through the added skipped-candidate detail; the bundled payload mirror, through the payload sync test; the touched code is award_itself_its_own_gate, conforming_instance with a candidate helper beside committed_instances, and the V3/V4 loop and mutation print in main.

## Validation Plan

- Verification steps: Repeat the reproduction on unchanged run evidence and expect 6/6, with orchestration-result.md selected from run-d8937789961e, caught by O4 and no candidate skipped, which shows the locator cause removed rather than routed around. Then show the selection cause removed: a last candidate lacking the anchor above an anchored one selects the older and reports the skip; no applicable candidate fails V4 naming each candidate; a non-conforming applicable last candidate is still selected and fails V3; an accept-all or wrong-check validator still fails V4.
- Regression tests added: In tests/test_verify_validators_mutations.py, each failing before the fix (E-019) and passing after: plain-rendered orchestration rows resolve an anchor caught by O4; the selector skips an unanchored last candidate for an older anchored one and reports it; when no candidate applies the result is none and names every candidate; a non-conforming applicable candidate is not skipped; an accept-all validator fails V4 after selection; the mutation line for an unanchored type does not claim caught; every registered type resolves an applicable candidate on the real tree.
- Monitoring signals after release: V4 detail naming a skipped candidate or no applicable candidate on any release verification; FR-02 failing after a run commits any registered artifact type; a selected instance differing from the last-sorted one.

## Closure

- Resolution summary: None identified.
- Linked PR and release: None identified.
- Prevention actions: Run the selector against every committed instance of every type as a standing test, and require each derived mutation to locate its target by the contract engine's own identifier rule rather than by one rendering; the Fix, Verification and Closure Gates remain with their owners.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Should the orchestration contract fix identifier rendering, or must verifiers keep matching the engine's optional-backtick rule; a contract decision, not proposed here | no | architect | `C-002` |
| `Q-002` | Do the count-based derivations (review counts 1 to 9, options 2 to 39, met 0 to 39) miss a conforming boundary instance; not demonstrated, and the fallback now covers it | no | omn-dev-1-implement | `C-004` |
| `Q-003` | The F7 rejection of the change proposal from inside the framework directory is a separate working-location defect in the proposal validator; confirm and route as its own fix | no | omn-tech-lead | none |
| `Q-004` | The main checkout and hosted CI were not observed; does the failure reproduce there with their run evidence | no | omn-qa | none |
