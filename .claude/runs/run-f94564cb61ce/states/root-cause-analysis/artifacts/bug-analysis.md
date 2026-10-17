```yaml
bugAnalysis:
  analysisId: BA-run-f94564cb61ce-root-cause-analysis
  defectReference: runs/inputs/release-handoff-verdict-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/release-handoff-verdict-defect-report.md
    - type: impact-and-risk-data
      reference: runs/run-f94564cb61ce/states/triage-and-impact/artifacts/bug-analysis.md
    - type: impact-and-risk-data
      reference: runs/run-f94564cb61ce/state.json
    - type: impact-and-risk-data
      reference: runs/run-f94564cb61ce/task-context.yaml
    - type: architecture-context
      reference: architect-ruling-Q-001.md (architect consult a96e516fa44073324, session scratchpad, outside the repository)
    - type: code-context
      reference: agents/omn-documentation/reasoning.md
    - type: code-context
      reference: agents/omn-documentation/output.md
    - type: code-context
      reference: agents/omn-documentation/quality.md
    - type: code-context
      reference: agents/omn-documentation/identity.md
    - type: code-context
      reference: agents/omn-documentation/manifest.yaml
    - type: code-context
      reference: agents/omn-documentation.agent.md
    - type: code-context
      reference: templates/release-note.md
    - type: code-context
      reference: registry/agents.yaml
    - type: code-context
      reference: registry/templates.yaml
    - type: code-context
      reference: runtime/release_note_validator.py
    - type: code-context
      reference: runtime/artifact_contract.py
    - type: code-context
      reference: runtime/artifact_lib.py
    - type: code-context
      reference: runtime/framework_runtime.py
    - type: code-context
      reference: runtime/verify_validators.py
    - type: code-context
      reference: runtime/close_legacy_run.py
    - type: code-context
      reference: runtime/README.md
    - type: code-context
      reference: runtime/fixtures/release-note.md
    - type: code-context
      reference: workflows/implement-feature.md
    - type: code-context
      reference: workflows/investigate.md
    - type: code-context
      reference: workflows/research.md
    - type: code-context
      reference: workflows/review-pull-request.md
    - type: code-context
      reference: workflows/release.md
    - type: code-context
      reference: workflows/fix-bug.md
    - type: code-context
      reference: workflows/refactor.md
    - type: code-context
      reference: tests/test_knowledge.py
    - type: code-context
      reference: tests/fixtures/knowledge/baseline-0.9.0/baseline.json
    - type: code-context
      reference: tests/test_bundled_payload.py
    - type: code-context
      reference: omn_agent/_bundled_payload/runtime/release_note_validator.py
    - type: code-context
      reference: proposals/framework-change-proposal-FC-020.md
    - type: symptom-evidence
      reference: runs/*/states/*/artifacts/release-note.md
    - type: symptom-evidence
      reference: runs/*/states/*/invocation-envelope.json
    - type: symptom-evidence
      reference: runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/result-envelope.json
    - type: symptom-evidence
      reference: runs/run-c9fb8d5bbb32/states/quality-review/artifacts/review-package.md
    - type: symptom-evidence
      reference: runs/*/gates/closure-gate/failure-envelope.json
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: high
  reproducibility: deterministic
  inputDigest: sha256:dfa126ab657c3125805bdade2076fa7a
  contextDigest: sha256:576abeed3e57800a2e83f0313e986f82
```

## Metadata

- Bug ID: runs/inputs/release-handoff-verdict-defect-report.md
- Reporter: the framework operator, acting as omn-orchestrator for held run run-c9fb8d5bbb32 (`E-001`)
- Severity: high
- Status: provisional

## Symptom Summary

- Observed behavior: the documentation-and-release-handoff phase of implement-feature either emits a release note the Validation Engine rejects (`withheld`, R1 fail) or emits `released` for a change its own Environment line says was never deployed, and the validator accepts it; re-observed first-hand in this run (`E-008`, `E-009`, `E-011`).
- Expected behavior: a phase whose workflow has no deployment step can read a truthful release position off Stage 8 that asserts no deployment fact and that the validator, output contract, quality check, and template accept, with deploying phases unchanged; stated by the defect report (`E-001`), implied by the Stage 8 rule that the verdict is read, not chosen (`E-002`), and bound by the Triage Gate scope and conditions (`E-032`).
- First observed date: the earliest note carrying a deployment verdict with no deployment evidence is dated 2026-08-28 (run-efe092286625 `released`, run-09099de97613 `partial`); the blocking form was first observed 2026-10-17 in run-c9fb8d5bbb32; ongoing (`E-010`, `E-013`).
- Affected environments: known affected are implement-feature documentation-and-release-handoff (9 notes) and investigate publication (1 note); known unaffected are fix-bug and refactor, which have no omn-documentation-owned phase; not observed are research findings-publication and review-pull-request documentation-impact (no recorded notes, same contract gap by reading) and release communication-and-post-release (no recorded run) (`E-006`, `E-007`, `E-010`).

## Reproduction

- Preconditions: a release-note.md produced by the documentation-and-release-handoff phase of an implement-feature run, with no deployment-status among its sourceInputs; run-c9fb8d5bbb32 supplies one with verdict `withheld`, run-efe092286625 one with verdict `released`; the contract files are unmodified on this branch (`E-028`).
- Steps to reproduce: from the repository root run `python .claude/runtime/release_note_validator.py .claude/runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/artifacts/release-note.md` and read R1 (expect FAIL, exit 1); run the same command on `.claude/runs/run-efe092286625/states/documentation-and-release-handoff/artifacts/release-note.md` with `--envelope` pointing at that state's invocation-envelope.json (expect PASS, exit 0) while that note's Environment line states nothing was deployed; then read Stage 8 of `agents/omn-documentation/reasoning.md` and confirm no row applies to a phase not supplied a deployment status.
- Reproduction frequency: deterministic
- Evidence: register below; attempts are `E-008` and `E-009`, re-run in this invocation; the task context names no relevant files, so sites were located from the defect report, the triage register, and the architect ruling, which is the recorded reason for the wider read.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Reporter account: held run, two operator rulings for `released` declined by the agent, three precedents, constraints not to rewrite earlier run evidence and to leave release-workflow phases unchanged | supplied input runs/inputs/release-handoff-verdict-defect-report.md, sha256:dfa126ab657c3125805bdade2076fa7a | low |
| `E-002` | Stage 8 reads the verdict "against the supplied deployment status"; rows are `released` (reached target environment), `partial`, `rolled-back`, and withheld/`blocked` only "for a phase that requires it"; no row covers a phase not supplied one; Stage 2 already records the communication basis | agents/omn-documentation/reasoning.md lines 129-150 and line 41 | high |
| `E-003` | releaseVerdict vocabulary is `released`, `partial`, `rolled-back` in the output contract (line 76) and template (line 36); R1 (line 92) requires one of them; V1/V2 bind verdict and status to the Stage 8 row; `None identified.` in Known Issues only for `released` (output.md line 53) | agents/omn-documentation/output.md, quality.md lines 92-98, templates/release-note.md | high |
| `E-004` | The validator hard-codes VERDICTS to the three values (line 32) and R1 tests membership only (lines 99-102); R4 needs_issue is partial/rolled-back (line 131); no check relates verdict to any input type or to Environment text | runtime/release_note_validator.py | high |
| `E-005` | Required Evidence: "A release landed, partly landed, or was rolled back" needs "the supplied deployment status" (line 225); deployment-status alone satisfies the minimum only in communication-and-post-release; manifest accepted inputs are implementation-report, validation-report, review-package, deployment-status, technical-recommendation, with verification-report optional | agents/omn-documentation/identity.md lines 105-120 and 225; manifest.yaml inputs block | high |
| `E-006` | Phase Model inputs: documentation-and-release-handoff takes verification report and change summary; publication and findings-publication take technical-recommendation.md; documentation-impact takes validation-report.md; only communication-and-post-release takes deployment status; all five emit release-note.md; each phase id appears in exactly one workflow | workflows/implement-feature.md line 44, investigate.md line 44, research.md line 43, review-pull-request.md line 41, release.md line 39 | high |
| `E-007` | fix-bug and refactor name omn-documentation only as Closure Gate co-owner; neither has an omn-documentation-owned phase | workflows/fix-bug.md lines 17, 117, 123; workflows/refactor.md lines 18, 132, 138 | high |
| `E-008` | Validator over the run-c9fb8d5bbb32 note exits 1: R1 FAIL releaseVerdict='withheld' (plus C3.2, see `E-014`); same outcome as the two triage runs | command run in this invocation: release_note_validator.py on the run-c9fb8d5bbb32 note | high |
| `E-009` | Varied precondition: validator with envelope over the run-efe092286625 note (`released`, no deployment-status input) exits 0, 32/32 checks pass | command run in this invocation: release_note_validator.py with --envelope on the run-efe092286625 note | high |
| `E-010` | Survey of all 10 notes: 0 list deployment-status; `released` 7 (4c51600606df, 8f8a1ab0d16e, 919c5d5cf156, ae91e085f481, ded114f50a46, e0dba6763475, efe092286625); `partial` 2 (09099de97613, 437e2f765e4b); withheld 1 (c9fb8d5bbb32); every envelope carries a state_id | metadata of each note and state_id of each invocation-envelope.json, read in this invocation | high |
| `E-011` | Each `released` note's Environment or Deployment considerations line states nothing was deployed (working tree, pending merge or commit, no deployment environment named) | Environment and Deployment considerations lines of the 7 notes in `E-010`, read in this invocation | high |
| `E-012` | The 2 `partial` notes record no partial deployment (09099de97613 inert on landing; 437e2f765e4b "No change reached an environment"); FC-020 O-006 records the findings-publication gap, routed to architect, Open | the two notes; proposals/framework-change-proposal-FC-020.md line 180 | high |
| `E-013` | Held run: result envelope status escalation_required, error class context-absent, verdict withheld; run state ExecutingState | runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/result-envelope.json; runs/run-c9fb8d5bbb32/state.json | high |
| `E-014` | The `E-008` run also fails Blocking C3.2 on the held note (a vendor token in the branch name its Environment line cites); independent of the verdict | command run in this invocation, as `E-008`; runtime/artifact_contract.py lines 288-293 | high |
| `E-015` | Closure Gate failure envelopes of all 8 implement-feature precedent runs with a non-withheld note read status resolved | runs/*/gates/closure-gate/failure-envelope.json status fields, read in this invocation | high |
| `E-016` | Confirmed absence: no test source references releaseVerdict, R1, or withheld (only stale compiled caches match); the fixture carries `released` with a deployment-status input and passes 31/31 | grep over tests/; runtime/fixtures/release-note.md and validator run on it in this invocation | high |
| `E-017` | The bundled payload validator keeps the same three-value VERDICTS at line 32 | omn_agent/_bundled_payload/runtime/release_note_validator.py | high |
| `E-018` | Confirmed absence: no runtime module other than the release-note validator references releaseVerdict | grep over runtime/*.py in this invocation | high |
| `E-019` | Architect ruling on `Q-001`: one value per basis (`handed-off`, `findings-published`, `delta-published`), release family unchanged, withheld never passing; R8 on sourceInputs types; R9 on envelope state_id; Stage 8 rekeyed on basis; minor bumps; superseded-contract skip in verify_validators | architect-ruling-Q-001.md, consult a96e516fa44073324, sha256:51f4a7e216c5d21de44b93fedb5f2fba (supplied account) | low |
| `E-020` | Ruling claims confirmed: validate(path, envelope) at line 170; runtime passes the envelope at framework_runtime.py line 4169, close_legacy_run.py line 68, verify_validators lines 414/666/681; envelopes carry no basis field; C7.1 degrades to Advisory not-machine-checkable without an envelope; C1.3 hard-checks schemaVersion | runtime/release_note_validator.py; framework_runtime.py; close_legacy_run.py; verify_validators.py; artifact_contract.py lines 227-231, 441-454 | high |
| `E-021` | Ruling gap: semantic_checks(rep, contract) receives no envelope; the shared cli calls extra(rep, contract) only; Report holds no envelope; no validator's semantic step reads one; so R9 cannot see state_id, and the CLI --envelope path would not reach it, without new plumbing | runtime/release_note_validator.py lines 91, 170-176; artifact_contract.py lines 476-493; artifact_lib.py lines 42-67 | high |
| `E-022` | Ruling error: V3 candidate order puts efe092286625 first (9 committed notes, then the fixture; selected efe092286625, none skipped); but main() re-validates every skipped candidate and fails V3 on a rejection, and the docstring says a rejected one still fails V3, so a selection-only agent_version skip still fails V3 | command run in this invocation listing candidate_instances and conforming_instance; verify_validators.py lines 321-372, 666-686 | high |
| `E-023` | verify_validators today: 6/6 checks passed, COVERED, exit 0; release-note mutation caught by R2 | command run in this invocation: runtime/verify_validators.py | high |
| `E-024` | Versions: omn-documentation manifest, host registration (line 18 table, line 44 bootstrap check), and registry record at 1.1.0; template and its registry record at 1.1.0; envelopes of the 9 notes record agent_version 1.0.0 (8) and 1.1.0 (437e2f765e4b); the runtime raises workflow-contract-violation when manifest and registry versions differ | manifest.yaml line 13; agents/omn-documentation.agent.md; registry/agents.yaml line 431; registry/templates.yaml line 217; template line 8; framework_runtime.py lines 974-976 | high |
| `E-025` | Ruling refinement: the 8 implement-feature notes list `verification-report`; 437e2f765e4b lists its recommendation as `final-change-summary`; documentation-impact's input is validation-report.md and `validation-report` is an accepted manifest identifier, so R8 sets naming only `verification-report` would reject a faithful note | sourceInputs of the 10 notes; `E-005`; `E-006`; output.md line 86 | high |
| `E-026` | Ruling incomplete: guarded_slice_member_digests pins registry/agents.yaml, registry/templates.yaml, templates/release-note.md, and runtime/README.md (also fix-touched); the baseline dispatch slice includes both registries; one test compares live digests, two compare the full normalised envelope and idempotency key | tests/fixtures/knowledge/baseline-0.9.0/baseline.json; tests/test_knowledge.py lines 676-764 | high |
| `E-027` | BackwardCompatibilityTestCase passes 6/6 today, so any failure after the fix is caused by the fix's edits to pinned files | command run in this invocation: unittest tests.test_knowledge.BackwardCompatibilityTestCase | high |
| `E-028` | CR-003 (from F-003) is open in run-c9fb8d5bbb32, owner omn-dev-1-implement, requiring the pre-change guarantee to survive unrelated edits and any frozen check to state how it is re-baselined; K-005 repeats it; the knowledge-loop test files are untracked and the fix-touched files are unmodified on this branch | review-package.md lines 44 and 74; release-note.md line 63 of that run; git status in this invocation | high |
| `E-029` | Bundled payload mirrors every fix-touched file; its parity test already fails 2 of 11 before any fix: file-set drift on memory/lessons/lessons.store.json, and find_source resolving to the main checkout from this worktree | omn_agent/_bundled_payload listing; command run in this invocation: tests/test_bundled_payload.py | high |
| `E-030` | FC-020 O-007: registered agents may read contract text from the main checkout, so a contract change is unexercised by them before landing; R-003 records that an agent version bump resets gate auto-approval precedent | proposals/framework-change-proposal-FC-020.md lines 142, 149, 181 | high |
| `E-031` | Validator README table lists only release/communication-and-post-release as served by release_note_validator.py | runtime/README.md line 415 | high |
| `E-032` | Triage Gate approved by omn-tech-lead: scope all four non-deploying phases; release verdicts, rows, R4/R5 unchanged; withheld never passing; settle O-006; R1/validator test verdict against basis or deployment-status input; release regression tests; mirror parity; Q-003 out of scope; Q-004 via proposal; Q-002 non-blocking | runs/run-f94564cb61ce/state.json gates Triage Gate rationale | high |

## Impact Assessment

- User impact: every operator closing an implement-feature run, including every framework self-hosting change routed through /implement, and every investigate publication, gets either a blocked final phase or a release record asserting a deployment that did not happen; 10 of 10 recorded notes are affected (`E-010`, `E-011`).
- Business impact: no business impact statement was supplied; the defect report states the governance-integrity consequence qualitatively and it is recorded as reported (`E-001`); severity rests on technical impact alone (`Q-002`).
- Technical impact: correctness of the governance record: 7 `released` and 2 placeholder `partial` notes state a release position their own evidence contradicts, and 1 run is held unable to close; no crash, no availability loss, and no security exposure (the triggering token is the vendor-name token of `E-014`, not a credential) (`E-008`, `E-012`, `E-013`).
- Blast radius: the omn-documentation contract (Stage 8, output contract, quality R1/V1/V2, Required Evidence); the release-note template; the release-note validator and the validator coverage verifier that selects committed notes; the bundled payload mirror; four phases never supplied a deployment status; the implement-feature Closure Gate, which accepted the misstated notes; persisted bad data in 9 notes plus the blocked note of run-c9fb8d5bbb32 (`E-003`, `E-004`, `E-006`, `E-010`, `E-015`, `E-017`, `E-022`).

## Root Cause Analysis

- Root cause statement: the release-verdict contract assumes every phase that publishes release-note.md publishes after a deployment (its only verdicts are deployment outcomes and their only admissible evidence is a supplied deployment status), while four of the five phases omn-documentation owns are by construction never supplied one, so those phases have no verdict that is both truthful and accepted, and the validator's membership-only R1 lets an untruthful one through.
- Why detection failed earlier: R1 tests only membership in the three-value vocabulary; V1 (verdict per Stage 8) is decided only by the producing agent; no test relates verdict to phase basis or to a deployment-status input (`E-016`); verify_validators V3 validated a misstated note as its conforming release-note instance (`E-022`, `E-023`); and the Closure Gate approved `released` notes whose Environment lines contradicted the verdict (`E-004`, `E-015`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | phase inputs | four of five omn-documentation phases are never supplied a deployment status because deployment belongs only to the release workflow; supplying a synthetic one to implement-feature is excluded | `E-006`, `E-007` | high |
| `C-002` | verdict rule | Stage 8 reads every verdict off a supplied deployment status and gives withheld only to a phase that requires one, so a non-deploying phase has no row; reading `released` as a verified handoff is excluded by its definition | `E-002`, `E-005` | high |
| `C-003` | vocabulary | output contract, R1, template, and validator, mirrored in the bundle, admit only the three deployment outcomes, so no value expresses a handoff that was not deployed | `E-003`, `E-004`, `E-017` | high |
| `C-004` | faithful path | an agent applying Stage 8 as written emits withheld with status blocked, which R1 rejects every time, so the phase cannot pass and the run holds | `E-008`, `E-013` | high |
| `C-005` | accepted path | R1 checks membership only, so `released` or `partial` without deployment evidence passes, which is why 9 notes persist a position their own evidence contradicts and the Closure Gate approved them | `E-009`, `E-010`, `E-011`, `E-012`, `E-015` | high |

## Fix Strategy

- Proposed fix: adopt the architect ruling on `Q-001` (`E-019`) as amended by the four corrections in `E-021`, `E-022`, `E-025`, and `E-026`, so that the following conditions hold after the change:
  - Stage 8 is read against the communication basis fixed at Stage 2 and, for `post-release` only, the supplied deployment status; `release-handoff` yields `handed-off`, `findings` yields `findings-published`, `documentation-delta` yields `delta-published`, each asserting no merge, release, or deployment fact; withheld with `blocked` remains for absent required evidence and is never a passing verdict; a deployment status supplied to a non-post-release phase selects no row (`E-002`, `E-032`).
  - the output contract, R1 text, template vocabulary and Known Issues guidance, Required Evidence table, and validator all state the same six-value vocabulary; `None identified.` in Known Issues is permitted for `released` and the three new values; the release rows, R4, and R5 behave exactly as before (`E-003`, `E-004`, `E-032`).
  - the Validation Engine decides the verdict against evidence, not membership: a Blocking rule fails `released`, `partial`, or `rolled-back` without a deployment-status input, and fails each new value without its basis evidence, where the accepted type sets include the manifest's accepted identifiers (`validation-report` beside `verification-report` for `handed-off` and `delta-published`; `technical-recommendation` for `findings-published`) (`E-025`); a second rule maps envelope state_id to basis, Blocking when an envelope is present and the state_id is missing or unknown, Advisory not-machine-checkable only when no envelope is supplied (`E-020`).
  - the envelope reaches that second rule on both the runtime acceptance path and the validator's own command-line `--envelope` path, without altering the shared command-line hook the other validators use (`E-021`).
  - validator coverage verification stays green without any exemption inside the validator: committed notes whose envelope records an omn-documentation version below 1.2.0 are reported by count as produced under a superseded contract and are excluded from both instance selection and the skipped-candidate re-validation, while a rejected note produced at 1.2.0 or later still fails V3; the verifier's documented selection rule changes with it (`E-022`, `Q-006`).
  - versions agree: omn-documentation 1.2.0 in its manifest, host registration (table and bootstrap check), and registry record; release-note template 1.2.0 in the template and its registry record; schemaVersion stays 1.0.0 because C1.3 hard-checks it; the registry edit is unavoidable because the runtime rejects a manifest/registry mismatch (`E-020`, `E-024`); the README validator table names all five served phases (`E-031`).
  - the bundled payload is identical to the authoritative tree for every touched file; because the parity test already fails for unrelated reasons, the sync must not sweep unrelated knowledge-branch files into the bundle without that branch owner's decision (`E-029`, `Q-007`).
  - persisted bad data stays as recorded (`E-001`, `E-032`): the change proposal lists the 9 notes with their expected re-validation (all fail the deployment-evidence rule; with their committed envelope the basis rule expects `handed-off` for the 8 implement-feature notes and `findings-published` for 437e2f765e4b), records FC-020 O-006 closed, and no run evidence or Closure Gate decision is edited; run-c9fb8d5bbb32 needs a re-dispatch yielding `handed-off`, which also needs `Q-003` settled and is exposed to FC-020 O-007 until landing (`E-014`, `E-030`).
  - the knowledge branch's pinned digests are not re-baselined by the implementer; the fix is expected to fail three of six BackwardCompatibilityTestCase tests, which are reported in the implementation report as a known consequence pending the omn-tech-lead decision in `Q-005` (`E-026`, `E-027`, `E-028`).
- Alternative options: rejected with the ruling: one basis-neutral value (states nothing the evidence shows), withheld as a non-blocking value (gate-excluded, `E-032`), a synthetic deployment-status for implement-feature (excluded by `C-001`), a new required basis metadata field (fails C1.1 on all history and forces a schemaVersion bump), a basis field in the envelope (moves payload and replay surfaces), and an agentVersion exemption inside the validator (accepts positions the contract never yielded); for coverage verification, validating historical notes against a per-version vocabulary keeps `released`-without-deployment accepted and is rejected; for the pins, see `Q-005`.
- Regression risk: medium
- Regression scope: release communication-and-post-release (shares the vocabulary, R1, R4, R5, and the validator); the runtime acceptance path and close_legacy_run (both pass the envelope, so the basis rule becomes Blocking there); verify_validators V3/V4 for every artifact type (shared candidate selection and skipped-candidate re-validation); the validator fixture and tests/test_investigate_research_handoffs.py (import the validator); tests/test_knowledge.py BackwardCompatibilityTestCase (pins four fix-touched files); tests/test_bundled_payload.py (mirror parity, already failing 2 of 11); gate auto-approval precedent for omn-documentation (keyed on agent version, `E-030`); implement-feature Closure Gate and the omn-orchestrator closure path (consume verdict and status); the orchestration-result deployment-state vocabulary is outside scope (`E-018`).

## Validation Plan

- Verification steps: invert the reproduction: the run-c9fb8d5bbb32 note's preconditions with verdict `handed-off` and a verification input pass with that state's envelope, while the run-efe092286625 note with its envelope now fails on the deployment-evidence and basis rules, showing the `C-005` condition is gone rather than R1 merely widened; withheld fails in every phase; a release-phase note with `released` and deployment-status passes exactly as the fixture does today, R4/R5 unchanged, and `handed-off` on that phase fails the basis rule; the command-line `--envelope` path reports the basis rule as decided, not not-machine-checkable; Stage 8 read against each of the five Phase Models yields exactly one row for the evidence present (`C-002` removed); verify_validators exits 0 reporting 9 superseded-contract candidates; the 9 notes re-validate as the change proposal predicts.
- Regression tests added: per omn-documentation phase, with and without an envelope, which verdicts pass; release phase unchanged including R4 and R5; withheld fails everywhere; a deployment verdict without deployment-status fails outside release; type-set acceptance including `validation-report`; the phase-to-basis table agrees with the output contract Deliverable table; the envelope reaches the basis rule through the command line; verify_validators reports superseded candidates and still fails V3 on a rejected note produced at 1.2.0; bundled-payload vocabulary parity.
- Monitoring signals after release: count of new notes whose verdict is a deployment outcome while sourceInputs carry no deployment-status, expected 0; count of omn-documentation phases ending blocked on R1 or the new rules, expected 0 where evidence is present; verify_validators superseded-candidate count, expected to stay at 9, where growth means a note was produced under the old contract (FC-020 O-007).

## Closure

- Resolution summary: None identified. Unresolved; closure is decided at the fix-bug Closure Gate, not here.
- Linked PR and release: None identified. No corrective change exists yet.
- Prevention actions: tie the verdict check to the phase basis and declared inputs in the Validation Engine rather than to vocabulary membership; require a pinned-digest test to state its re-baseline rule before a framework change lands over it (`Q-005`); have the Closure Gate cross-check the verdict against the note's Environment line (`E-004`, `E-015`, `E-016`, `E-026`).

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-005` | CR-003 pins: the fix must edit four pinned files, so land CR-003 first, re-baseline the four digests and the 0.9.0 dispatch baseline under a recorded decision naming this run, or land the fix where the knowledge loop is absent; needed before the Fix Gate | yes | omn-tech-lead | none |
| `Q-001` | Answered: architect ruling `E-019` (one value per basis; subsumes FC-020 O-006), accepted with corrections `E-021`, `E-022`, `E-025`, `E-026`; recorded per Triage Gate condition 1 | no | architect | `C-002`, `C-003` |
| `Q-003` | Run run-c9fb8d5bbb32 also fails C3.2 on its Environment line (`E-014`); out of scope per the Triage Gate; the re-dispatched note must not cite the branch name verbatim | no | omn-orchestrator | `C-004` |
| `Q-004` | Answered by the Triage Gate: the change proposal lists the 9 notes and their expected re-validation; run evidence is never edited | no | omn-tech-lead | `C-005` |
| `Q-002` | No business impact statement was supplied; severity rests on technical impact alone; confirm the governance-integrity impact the report states qualitatively | no | omn-product-owner | none |
| `Q-006` | The superseded-contract exclusion changes verify_validators' documented rule that every skipped rejected candidate fails V3 (`E-022`); confirm this amendment to the ruling | no | architect | none |
| `Q-007` | The bundle sync would also mirror memory/lessons/lessons.store.json, and find_source fails inside this nested worktree (`E-029`); decide whether the sync may run whole or only for fix-touched files | no | omn-tech-lead | none |
