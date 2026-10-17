```yaml
validationReport:
  reportId: VR-run-f94564cb61ce-regression-validation
  validationReference: run-f94564cb61ce fix-bug, defect runs/inputs/release-handoff-verdict-defect-report.md, change IR-2026-1013 (C-001 to C-027) with the post-review corrections recorded in the Fix Gate rationale
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-f94564cb61ce/states/fix-implementation/artifacts/implementation-report.md
    - type: bug-analysis
      reference: runs/run-f94564cb61ce/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: acceptance-criteria
      reference: runs/run-f94564cb61ce/state.json, gates Triage Gate and Fix Gate rationale
    - type: acceptance-criteria
      reference: omn-tech-lead ruling on the CR-003 pins and the bundle sync (operator-supplied file, session scratchpad, outside the repository)
    - type: architecture-context
      reference: architect ruling on the release-vocabulary question (operator-supplied file, session scratchpad, outside the repository)
    - type: scope-definition
      reference: runs/run-f94564cb61ce/task-context.yaml
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  verdict: pass-with-reservations
  inputDigest: sha256:a2c468d47bb30a0f283259f0b4a9e4d3
  contextDigest: sha256:9978ebb5cb624a7226773a03f0b6ee13
```

## Metadata

- Validation ID: VR-run-f94564cb61ce-regression-validation
- Validator: omn-qa
- Change under validation: the omn-documentation 1.2.0 release-position contract, release-note validator R8/R9, verify_validators superseded-contract selection, and their bundled mirrors (IR-2026-1013 plus post-review corrections)
- Validation date: 2026-10-17

## Validation Scope

- In scope: the fifteen criteria AC-001 to AC-015 below; the defect no longer reproducing on new notes in any of the five omn-documentation phases; the regression surface named by the root-cause analysis (release-phase verdicts and R4/R5, verify_validators V3/V4 for every artifact type, modules importing the validator or verifier, BackwardCompatibilityTestCase over the four pinned files, bundled-payload parity) and the full repository test suite.
- Out of scope: the C3.2 vendor-token failure of the held run-c9fb8d5bbb32 note (Triage Gate, routed to omn-orchestrator by the root-cause analysis); editing or re-closing any of the 9 recorded notes or the held note (Triage Gate, run evidence is immutable); RCA fix conditions 1, 2, 3, and 7 as separate rows, because the Triage Gate conditions AC-001 to AC-007 carry the same content; the expected-failure clause of RCA fix condition 9, superseded by its owner in the omn-tech-lead ruling on the CR-003 pins (option a) and replaced by AC-013; code quality of the change (omn-dev-2-reviewer, decided at the Fix Gate); verify_multi_phase and verify_vertical_slice (operator instruction, they mutate the run they select).
- Evidence examined: implementation-report IR-2026-1013 (sha256:a2c468d47bb30a0f283259f0b4a9e4d3); root-cause bug-analysis; task-context.yaml; Triage and Fix Gate rationales in state.json; architect release-vocabulary ruling and omn-tech-lead CR-003 pins ruling; tests/test_release_verdict.py, tests/test_bundled_payload.py, tests/test_knowledge.py run in full; runtime/verify_validators.py, runtime/verify_manifests.py, runtime/verify_registry_coverage.py; tools/run_tests_parallel.py full suite; runtime/release_note_validator.py over a scratch copy of the held note, the 9 recorded notes, and 23 constructed notes; the HEAD validator over the same notes as a defect witness; git diff of the R4/R5 block, of runtime/artifact_contract.py, and cmp of the 13 mirrored files.

## Test Strategy

- Risk basis: the change alters a path that decides whether work proceeds (Blocking validator rules gate every omn-documentation phase and the coverage verifier), so every phase was exercised against every verdict family with and without an envelope; it alters interfaces other modules call (validate, semantic_checks, verify_validators selection), so each call site that can be executed was executed and the rest traced; no stored data is written or migrated and no security handling is altered (the database and security triggers are the words migration and token, the latter being the vendor-name check C3.2).
- Levels executed: unit, integration
- Environment: the run's worktree on a Windows 11 host, Python, framework-relative paths; constructed and held-note copies validated from the session scratchpad outside the repository; the host's ffmpeg rejects an option test_demo_capture uses, so that module fails here independently of this change.
- Not executed: end-to-end, because no harness completes an omn-documentation phase through framework_runtime and doing so on this run's tree would mutate run evidence (AC-008); performance, because no performance-sensitive path changed and S08 was not triggered; security, because no security-relevant handling changed and C3.2 behaviour is exercised at unit level only.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| AC-001 | SCOPE: cover all four non-deploying omn-documentation phases (implement-feature documentation-and-release-handoff, investigate publication, research findings-publication, review-pull-request documentation-impact) | state.json Triage Gate rationale | unit | met | probe over validate(): each of the four phases passes with its basis position and evidence and fails released (R8, R9); test_release_verdict NonDeployingPhasesHaveATruthfulPosition 4/4 |
| AC-002 | keep release communication-and-post-release verdicts, rows and R4/R5 unchanged | state.json Triage Gate rationale | unit | met | git diff: R4/R5 block byte-identical to HEAD and Stage 8 post-release rows unchanged; probe: fixture passes with and without release envelope, partial/rolled-back without known issue fail R4 only, rolled-back with no rollback criteria fails R5 only, released without known issue passes |
| AC-003 | withheld never a passing verdict | state.json Triage Gate rationale | unit | met | probe: withheld/blocked fails R1, R8, R9 in all five phases; test_withheld_fails_in_every_phase_and_without_an_envelope ok |
| AC-004 | settle FC-020 O-006 in the same change | state.json Triage Gate rationale | unit | met | probe: findings-published with technical-recommendation passes on publication and findings-publication; run-437e2f765e4b note with its envelope fails R9 naming findings-published as the expected position |
| AC-005 | CONDITIONS: R1 and the validator test the verdict against the phase's basis or declared deployment-status input, so a deployment verdict without deployment-status fails outside release | state.json Triage Gate rationale | unit | met | probe: released without deployment-status fails R8 and R9 in all four non-deploying phases and R8 on the release phase; HEAD validator passed the run-efe092286625 released note with no blocking failure, current validator fails it on R8 and R9 |
| AC-006 | release behaviour protected by regression tests | state.json Triage Gate rationale | unit | met | test_release_verdict ReleasePhaseUnchanged 4/4 and PhaseRule 4/4 pass in the 29/29 run; their assertions match the probe outcomes in AC-002 |
| AC-007 | contract/template/validator mirror parity enforced | state.json Triage Gate rationale | unit | met | tests/test_bundled_payload.py 11/11; test_release_verdict ContractAgreement 5/5 and BundledPayloadParity 1/1; cmp: all 13 touched files identical to their omn_agent/_bundled_payload mirrors; no memory/lessons path in the bundle |
| AC-008 | the envelope reaches that second rule on both the runtime acceptance path and the validator's own command-line `--envelope` path, without altering the shared command-line hook the other validators use (`E-021`) | root-cause bug-analysis, Fix Strategy | integration | blocked | command line confirmed: held-note copy with --envelope decides R9 (fail on withheld, pass on handed-off); git diff of runtime/artifact_contract.py is empty; runtime path only traced (framework_runtime.py loads invocation-envelope.json at line 4072 and calls validate(artifact, envelope) at 4169), never executed; settled by completing an omn-documentation phase through framework_runtime on a scratch tree |
| AC-009 | validator coverage verification stays green without any exemption inside the validator: committed notes whose envelope records an omn-documentation version below 1.2.0 are reported by count as produced under a superseded contract and are excluded from both instance selection and the skipped-candidate re-validation, while a rejected note produced at 1.2.0 or later still fails V3; the verifier's documented selection rule changes with it (`E-022`, the root-cause analysis's open question on the superseded-contract amendment) | root-cause bug-analysis, Fix Strategy | integration | met | runtime/verify_validators.py exit 0, 6/6 COVERED, 9 release-note candidates reported superseded; test_a_rejected_note_at_the_current_contract_still_fails_v3 ok; release_note_validator.py reads agentVersion only as a metadata field; verifier docstrings state the superseded rule |
| AC-010 | versions agree: omn-documentation 1.2.0 in its manifest, host registration (table and bootstrap check), and registry record; release-note template 1.2.0 in the template and its registry record; schemaVersion stays 1.0.0 because C1.3 hard-checks it; the registry edit is unavoidable because the runtime rejects a manifest/registry mismatch (`E-020`, `E-024`); the README validator table names all five served phases (`E-031`) | root-cause bug-analysis, Fix Strategy | unit | met | test_versions_agree ok; grep: manifest line 13, host registration lines 18 and 44, registry/agents.yaml 431, registry/templates.yaml 217, template version 1.2.0 and schemaVersion 1.0.0; README line 415 names all five phases; verify_manifests 2/2 CONFORMS; verify_registry_coverage 8/8 COVERED |
| AC-011 | persisted bad data stays as recorded (`E-001`, `E-032`): the change proposal lists the 9 notes with their expected re-validation (all fail the deployment-evidence rule; with their committed envelope the basis rule expects `handed-off` for the 8 implement-feature notes and `findings-published` for 437e2f765e4b), records FC-020 O-006 closed, and no run evidence or Closure Gate decision is edited | root-cause bug-analysis, Fix Strategy | integration | blocked | confirmed: all 9 notes with their own envelopes fail exactly R8 and R9 with the predicted positions; held-note and envelope sha256 unchanged; git status identical before and after this phase; no change proposal for this run exists under proposals/ yet (the implementation report's open question on the change proposal, routed to omn-orchestrator); settled when that proposal is produced |
| AC-012 | invert the reproduction: the run-c9fb8d5bbb32 note's preconditions with verdict `handed-off` and a verification input pass with that state's envelope, while the run-efe092286625 note with its envelope now fails on the deployment-evidence and basis rules, showing the `C-005` condition is gone rather than R1 merely widened | root-cause bug-analysis, Validation Plan | integration | met | scratch copy with handed-off and its own envelope: R1, R8, R9 pass, 33/34, sole failure C3.2 (out of scope per Triage Gate), same with status complete or blocked; HEAD validator rejected the same copy on R1; run-efe092286625 note with its envelope fails R8 and R9 |
| AC-013 | BackwardCompatibilityTestCase 6/6 on the combined tree (fix applied, CR-003 landed). | omn-tech-lead ruling on the CR-003 pins, Fix Gate condition 1 | unit | met | python -m unittest tests.test_knowledge.BackwardCompatibilityTestCase: 6 tests OK; tests/test_knowledge.py 49/49 |
| AC-014 | CR-002 (unguarded envelope JSON in verify_validators) fixed post-review by the operator with a test | state.json Fix Gate rationale | unit | met | verify_validators.superseded_reason catches OSError, UnicodeDecodeError, ValueError and a non-dict envelope; test_a_note_below_the_current_contract_is_superseded asserts None for three malformed envelopes and passes |
| AC-015 | architecture-context added to declared sourceInputs types | state.json Fix Gate rationale | unit | met | agents/omn-documentation/output.md line 90 and templates/release-note.md line 36 name architecture-context, mirrors identical; the held-note copy lists architecture-context and passes R8 |

## Execution Summary

- Criteria validated: 15
- Met: 13
- Not met: 0
- Blocked: 2

## Defects

None identified.

## Regression Assessment

- Regression scope: release communication-and-post-release verdicts, R4 and R5; the runtime acceptance path and close_legacy_run, both of which pass the envelope; verify_validators V3/V4 for every artifact type; tests/test_investigate_research_handoffs.py and test_verify_validators_mutations, which import the validator or verifier; BackwardCompatibilityTestCase over the four pinned files; bundled-payload parity; every other module through the full suite.
- Regressions detected: None identified.
- Coverage of changed behavior: R1, R8, and R9 across all five phases and six verdicts, with and without an envelope, through validate() and the command line; R4/R5 on the release phase; superseded selection and V3 through verify_validators main; contract/template/validator/mirror agreement; full suite 768 tests, 28/29 modules, the only failing module test_demo_capture (3 tests, ffmpeg rejects filter_complex_script, the known environmental failure); test_verify_validators_mutations 26/26 and test_investigate_research_handoffs 22/22 within it.
- Untested areas: framework_runtime completing an omn-documentation phase end to end (AC-008); close_legacy_run, traced but not run; a re-dispatched agent reading the 1.2.0 Stage 8 prose and choosing handed-off, which a validator run cannot show (R-001 of the implementation report); verify_multi_phase and verify_vertical_slice, not run by instruction.

## Residual Risk

- Accepted risk: the held run-c9fb8d5bbb32 note still fails C3.2, accepted as out of scope by omn-tech-lead at the Triage Gate and routed to omn-orchestrator.
- Unmitigated risk: the omn-documentation version bump resets gate auto-approval precedent keyed on agent version, so its next gates need explicit decisions (implementation report R-002, recorded but accepted by no owning role); the runtime acceptance path is traced, not executed (AC-008); the change proposal recording the 9 superseded notes and FC-020 O-006 closed does not exist yet (AC-011); registered agents may read the main checkout's contract text before landing, so a re-dispatch of run-c9fb8d5bbb32 could still read the old Stage 8; a bare command-line run without an envelope declares R9 not-machine-checkable.
- Monitoring required: count of new release notes whose verdict is released, partial, or rolled-back while sourceInputs carry no deployment-status, expected 0; count of omn-documentation phases ending blocked on R1, R8, or R9 where evidence is present, expected 0; the verify_validators superseded-candidate count, expected to stay at 9.

## Verdict

- Decision: pass-with-reservations
- Rationale: no defect was found and no criterion is not-met, but AC-008 (runtime acceptance path not executed) and AC-011 (change proposal not yet produced) are blocked, so the Stage 8 table yields pass-with-reservations; the status is provisional because AC-008 is unreachable in this environment and the agent contract's recovery for that class is a provisional report pending Q-002.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that the Verification Gate owner, omn-dev-2-reviewer, treat the fix as validated against regression, with the two reservations carried forward: the change proposal for AC-011 belongs to closure-and-communication, and AC-008 is settled by the first omn-documentation phase completed through framework_runtime under 1.2.0.

## Open Questions

- Q-001: Who produces the change proposal that lists the 9 superseded notes with their R8/R9 re-validation and records FC-020 O-006 closed, which AC-011 needs, and is it due before the Closure Gate? Routes to omn-orchestrator.
- Q-002: Is the runtime acceptance path for AC-008 to be exercised before landing (a scratch-tree completion of an omn-documentation phase), or accepted on the traced call and the executed validate(path, envelope) equivalent? Routes to omn-dev-2-reviewer as Verification Gate owner.
