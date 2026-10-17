```yaml
bugAnalysis:
  analysisId: BA-run-f94564cb61ce-triage-and-impact
  defectReference: runs/inputs/release-handoff-verdict-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/release-handoff-verdict-defect-report.md
    - type: code-context
      reference: agents/omn-documentation/reasoning.md
    - type: code-context
      reference: agents/omn-documentation/output.md
    - type: code-context
      reference: agents/omn-documentation/quality.md
    - type: code-context
      reference: agents/omn-documentation/identity.md
    - type: code-context
      reference: agents/omn-documentation/execution.md
    - type: code-context
      reference: agents/omn-documentation/manifest.yaml
    - type: code-context
      reference: templates/release-note.md
    - type: code-context
      reference: runtime/release_note_validator.py
    - type: code-context
      reference: runtime/artifact_contract.py
    - type: code-context
      reference: runtime/orchestration_result_validator.py
    - type: code-context
      reference: workflows/implement-feature.md
    - type: code-context
      reference: workflows/fix-bug.md
    - type: code-context
      reference: workflows/refactor.md
    - type: code-context
      reference: workflows/investigate.md
    - type: code-context
      reference: workflows/research.md
    - type: code-context
      reference: workflows/release.md
    - type: code-context
      reference: workflows/review-pull-request.md
    - type: symptom-evidence
      reference: runs/*/states/*/artifacts/release-note.md
    - type: symptom-evidence
      reference: runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/result-envelope.json
    - type: symptom-evidence
      reference: runs/*/gates/closure-gate/failure-envelope.json
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: high
  reproducibility: deterministic
  inputDigest: sha256:dfa126ab657c3125805bdade2076fa7a
  contextDigest: sha256:f35d4b31201916991fcce2c388d3951a
```

## Metadata

- Bug ID: runs/inputs/release-handoff-verdict-defect-report.md
- Reporter: the framework operator, acting as omn-orchestrator for held run run-c9fb8d5bbb32 (`E-001`)
- Severity: high
- Status: provisional

## Symptom Summary

- Observed behavior: the documentation-and-release-handoff phase of implement-feature either emits a release note the Validation Engine rejects (`withheld`, R1 fail) or emits `released` for a change its own Environment line says was never deployed, and the validator accepts it (`E-008`, `E-009`, `E-011`).
- Expected behavior: a phase whose workflow has no deployment step can read a truthful release position off Stage 8 that asserts no deployment fact and that the validator, output contract, quality check, and template accept, with deploying phases unchanged; stated by the defect report (`E-001`) and implied by the Stage 8 rule that the verdict is read, not chosen (`E-002`).
- First observed date: the earliest recorded note carrying a deployment verdict with no deployment evidence is dated 2026-08-28 (run-efe092286625 `released`, run-09099de97613 `partial`); the blocking form was first observed 2026-10-17 in run-c9fb8d5bbb32 (`E-010`, `E-013`).
- Affected environments: known affected are implement-feature documentation-and-release-handoff (9 recorded notes) and investigate publication (1 note); known unaffected are fix-bug and refactor, which have no omn-documentation-owned phase; not observed are research findings-publication and review-pull-request documentation-impact (no recorded notes, same contract gap by reading) and release communication-and-post-release (no recorded run) (`E-006`, `E-007`, `E-010`).

## Reproduction

- Preconditions: a release-note.md produced by the documentation-and-release-handoff phase of an implement-feature run, with no deployment-status among its sourceInputs; run-c9fb8d5bbb32 supplies one with verdict `withheld`, run-efe092286625 one with verdict `released`.
- Steps to reproduce: from the worktree root run `python .claude/runtime/release_note_validator.py .claude/runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/artifacts/release-note.md` and read R1 (expect FAIL, exit 1); then run the same command against `.claude/runs/run-efe092286625/states/documentation-and-release-handoff/artifacts/release-note.md` and read the result (expect PASS, exit 0) while that note's Environment line states nothing was deployed; then read Stage 8 of `agents/omn-documentation/reasoning.md` and confirm no row applies to a phase that is not supplied a deployment status.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below; attempts are `E-008` and `E-009`.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Reporter account: the held run, two operator rulings for `released` declined by the agent, three precedents, operator constraints not to rewrite earlier run evidence and to leave release-workflow phases unchanged | supplied input runs/inputs/release-handoff-verdict-defect-report.md, sha256:dfa126ab657c3125805bdade2076fa7a | low |
| `E-002` | Stage 8 table defines `released` as every change in scope reached its target environment, `partial`, `rolled-back`, and withheld/`blocked` only for deployment status absent "for a phase that requires it"; no row covers a phase not supplied one; the table is read against the supplied deployment status and is not chosen | agents/omn-documentation/reasoning.md lines 130-150 | high |
| `E-003` | releaseVerdict vocabulary is `released`, `partial`, `rolled-back` in the output contract, the Blocking check R1, and the template; V1/V2 bind verdict and status to the Stage 8 row | agents/omn-documentation/output.md line 76, quality.md lines 89-98, templates/release-note.md line 36 | high |
| `E-004` | The validator hard-codes the same three values and R1 tests membership only; no check relates the verdict to any deployment-status input or to the note's Environment text | runtime/release_note_validator.py lines 32 and 91-102 | high |
| `E-005` | The only admissible evidence for a landed, partly landed, or rolled-back release is the supplied deployment status; deployment-status alone satisfies the input minimum only in communication-and-post-release; execution.md lists deployment status as consumed only by the release phase | agents/omn-documentation/identity.md lines 112-117 and 225, execution.md lines 78-81 and 203-209, manifest.yaml lines 112-124 | high |
| `E-006` | omn-documentation owns exactly five phases; inputs per Phase Model: implement-feature documentation-and-release-handoff takes verification report and change summary; investigate publication takes technical-recommendation and decision dependencies; research findings-publication takes technical-recommendation and evidence references; review-pull-request documentation-impact takes validation-report and release implications; release communication-and-post-release takes deployment status with monitoring health record, final change summary, stakeholder list; all five emit release-note.md | workflows/implement-feature.md line 44, investigate.md line 44, research.md line 43, review-pull-request.md line 41, release.md line 39; manifest.yaml supportedWorkflows lines 150-165 | high |
| `E-007` | fix-bug and refactor have no omn-documentation-owned phase; their closure phases are owned by omn-orchestrator and emit orchestration-result.md; omn-documentation only co-owns their Closure Gate | workflows/fix-bug.md Phase Model and line 117, workflows/refactor.md Phase Model and line 132 | high |
| `E-008` | Two runs of the validator over the run-c9fb8d5bbb32 note each exit 1 with R1 FAIL releaseVerdict='withheld'; identical output both times | command run in this analysis: release_note_validator.py on run-c9fb8d5bbb32 documentation-and-release-handoff release-note.md | high |
| `E-009` | Varied precondition: the validator over the run-efe092286625 note (verdict `released`, no deployment-status input, Environment says not merged, released, or deployed) exits 0 with result PASS | command run in this analysis: release_note_validator.py on run-efe092286625 documentation-and-release-handoff release-note.md | high |
| `E-010` | Survey of all 10 recorded notes under runs/*/states/*/artifacts/release-note.md: 0 of 10 list a deployment-status input; `released` 7 (all implement-feature: 4c51600606df, 8f8a1ab0d16e, 919c5d5cf156, ae91e085f481, ded114f50a46, e0dba6763475, efe092286625); `partial` 2 (09099de97613 implement-feature, 437e2f765e4b investigate); withheld 1 (c9fb8d5bbb32 implement-feature); `rolled-back` 0; validator exits 0 for 9 and 1 for c9fb8d5bbb32 | sourceInputs and releaseVerdict read from each note; workflow read from each run's state.json; validator run on each in this analysis | high |
| `E-011` | Each of the 7 `released` notes states in its Environment or Deployment considerations line that nothing was deployed (working tree, pending merge, no deployment environment named); ded114f50a46 records that `released` followed an operator instruction with no deployment status supplied | Environment and Deployment considerations lines of the 7 notes listed in `E-010` | high |
| `E-012` | The 2 `partial` notes record no partial deployment: 09099de97613 says the change is inert on landing, 437e2f765e4b declares `partial` a placeholder; FC-020 open item O-006 records the findings-publication gap, routed to architect, Open | the two notes; proposals/framework-change-proposal-FC-020.md line 180 | high |
| `E-013` | Held run envelope: status escalation_required, error class context-absent, verdict withheld, artifact blocked, 60 checks run, 59 pass, R1 failed; records that an orchestrator ruling to record `released` was not applied and that the Validation Engine was not run; run state is ExecutingState | runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/result-envelope.json; runs/run-c9fb8d5bbb32/state.json | high |
| `E-014` | The same validator runs as `E-008` also fail Blocking check C3.2 on the held note: a vendor token in the worktree branch name cited in its Environment line; this failure is independent of the verdict | command run in this analysis, as `E-008`; runtime/artifact_contract.py lines 288-293 | high |
| `E-015` | All 8 implement-feature precedent runs carrying a non-withheld note record their Closure Gate escalation resolved; run-efe092286625 records the Closure Gate approved by omn-orchestrator over the `released` note | runs/*/gates/closure-gate/failure-envelope.json status fields; runs/run-efe092286625/final-report.md and events.jsonl | high |
| `E-016` | Confirmed absence: no test asserts the verdict vocabulary against the phase's communication basis; the only test importing the validator contains no releaseVerdict, R1, or withheld reference; the validator fixture carries `released` and passes | grep over tests/; tests/test_investigate_research_handoffs.py; runtime/fixtures/release-note.md and validator run on it | high |
| `E-017` | The bundled payload mirrors the same three-value vocabulary in the validator, output contract, and template | omn_agent/_bundled_payload/runtime/release_note_validator.py line 32, agents/omn-documentation/output.md line 76, templates/release-note.md line 36 | high |
| `E-018` | No other runtime module reads releaseVerdict; the orchestration-result validator keeps its own deployment-state vocabulary, including `not-attempted`, separate from the release note | grep over runtime/*.py; runtime/orchestration_result_validator.py lines 50-73 | high |

## Impact Assessment

- User impact: every operator closing an implement-feature run, including every framework self-hosting change routed through /implement, and every investigate run's publication, gets either a blocked final phase or a release record asserting a deployment that did not happen; 10 of 10 recorded notes are affected (`E-010`).
- Business impact: no business impact statement was supplied; the defect report's Impact section states the governance-integrity consequence qualitatively and is recorded as reported (`E-001`); severity rests on technical impact alone, routed as `Q-002`.
- Technical impact: correctness of the governance record: 7 persisted `released` and 2 placeholder `partial` notes state a release position their own evidence contradicts, and 1 run is held unable to close; no crash and no runtime availability loss (`E-008`, `E-010`, `E-011`, `E-012`, `E-013`).
- Blast radius: the omn-documentation contract (Stage 8, output contract, quality R1/V1/V2, Required Evidence table); the release-note template; runtime/release_note_validator.py; the bundled payload mirror of all three; four phases never supplied a deployment status (implement-feature documentation-and-release-handoff, investigate publication, research findings-publication, review-pull-request documentation-impact); the implement-feature Closure Gate, which accepted the misstated notes; persisted bad data in 9 recorded notes plus the blocked note of held run run-c9fb8d5bbb32 (`E-003`, `E-004`, `E-005`, `E-006`, `E-010`, `E-011`, `E-012`, `E-013`, `E-015`, `E-017`).

## Root Cause Analysis

- Root cause statement: the release-verdict contract assumes every phase that publishes release-note.md publishes after a deployment (its only verdicts are deployment outcomes and their only admissible evidence is a supplied deployment status), while four of the five phases omn-documentation owns are by construction never supplied one, so those phases have no verdict that is both truthful and accepted.
- Why detection failed earlier: R1 in the validator tests only membership in the three-value vocabulary, quality check V1 (verdict per Stage 8) is decided only by the producing agent, no test relates verdict to phase basis or to a deployment-status input, and the Closure Gate approved `released` notes whose Environment lines contradicted the verdict (`E-004`, `E-015`, `E-016`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | phase inputs | four of five omn-documentation phases are never supplied a deployment status, because deployment belongs only to the release workflow; supplying one to implement-feature is excluded since that workflow has no deployment step | `E-006`, `E-007` | high |
| `C-002` | verdict rule | Stage 8 defines every verdict against a supplied deployment status and gives withheld only to a phase that requires one, so a phase that does not has no row; reading `released` as a verified handoff is excluded because `released` means reaching the target environment | `E-002`, `E-005` | high |
| `C-003` | vocabulary | output contract, R1, template, and validator, mirrored in the bundled payload, admit only the three deployment outcomes, so no value expresses a handoff that was not deployed | `E-003`, `E-004`, `E-017` | high |
| `C-004` | faithful path | an agent applying Stage 8 as written emits withheld with status blocked, which R1 rejects every time, so the phase cannot pass and the run holds | `E-008`, `E-013` | high |
| `C-005` | accepted path | R1 checks vocabulary membership only, so `released` or `partial` without deployment evidence passes, which is why 9 notes persist a release position their own evidence contradicts and the Closure Gate approved them | `E-009`, `E-010`, `E-011`, `E-012`, `E-015` | high |

## Fix Strategy

- Proposed fix: for each phase whose workflow declares no deployment step, Stage 8 must yield a release position keyed on the phase's communication basis rather than on missing evidence, asserting no deployment fact, accepted consistently by output contract, R1, V1/V2, template, validator, and bundled mirror; the release phase's verdicts, rows, and R4/R5 rules stay unchanged; the 9 persisted notes are left as recorded per the operator constraint (`E-001`), and the change record must name them as carrying a verdict the corrected contract would not yield; conditional on the vocabulary decision in `Q-001`; local containment meanwhile is the existing hold on run-c9fb8d5bbb32.
- Alternative options: (a) one basis-neutral value for every non-deploying phase versus (b) distinct values per basis (release-handoff, findings, documentation-delta), which also closes FC-020 O-006 but widens the vocabulary; (c) make withheld a legal non-blocking verdict for non-deploying phases, which keeps the vocabulary small but overloads a value that today means blocked; rejected direction: supplying a synthetic deployment-status to implement-feature, which `C-001` excludes.
- Regression risk: medium
- Regression scope: release communication-and-post-release (shares the vocabulary, R1, R4, R5, and the validator); the validator fixture and tests/test_investigate_research_handoffs.py (import the validator); the bundled payload mirror (must stay identical to the authoritative tree); the implement-feature Closure Gate and the omn-orchestrator closure path (consume the note's verdict and status); re-validation of the 10 recorded notes (shared validator, now judged against a changed vocabulary); no other runtime module reads releaseVerdict, so the orchestration-result deployment-state vocabulary is outside the scope (`E-018`).

## Validation Plan

- Verification steps: invert the reproduction: a non-deploying-phase note carrying the new position and no deployment-status input passes the validator; that same position on a release communication-and-post-release note is rejected, and a `released` note there still requires its deployment status; Stage 8 read against each of the five Phase Models yields exactly one row per phase, so the condition in `C-002` is gone rather than the R1 symptom masked.
- Regression tests added: a test per omn-documentation phase asserting which verdicts the validator accepts for that phase's basis; a test that `released`, `partial`, and `rolled-back` with R4/R5 behave unchanged for the release phase; a test that the bundled payload vocabulary equals the authoritative one.
- Monitoring signals after release: count of new release notes whose verdict is a deployment outcome while their sourceInputs carry no deployment-status; expected value 0, any non-zero value indicates recurrence; also count of documentation-and-release-handoff phases ending blocked on R1, expected 0.

## Closure

- Resolution summary: None identified. Unresolved; closure is decided at the fix-bug Closure Gate, not here.
- Linked PR and release: None identified. No corrective change exists yet.
- Prevention actions: tie the verdict check to the phase's declared inputs or communication basis in the Validation Engine rather than to vocabulary membership alone, and require the Closure Gate to cross-check the verdict against the note's Environment line (`E-004`, `E-015`, `E-016`).

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Which release position the non-deploying phases read off Stage 8: one value, one per communication basis, or a legal withheld, and whether it subsumes FC-020 O-006; a contract-vocabulary decision with structural reach across five phases | yes | architect | `C-002`, `C-003` |
| `Q-002` | No business impact statement was supplied; severity rests on technical impact alone; confirm the governance-integrity impact the defect report states qualitatively | no | omn-product-owner | none |
| `Q-003` | Run run-c9fb8d5bbb32 also fails Blocking check C3.2 on its Environment line, a separate defect independent of the verdict, so correcting the verdict contract alone will not let that held run pass validation (`E-014`) | no | omn-orchestrator | `C-004` |
| `Q-004` | Where the account of the 9 persisted notes whose verdict the corrected contract would not yield is recorded, given the constraint that run evidence is not rewritten | no | omn-tech-lead | `C-005` |
