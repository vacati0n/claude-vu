```yaml
implementationReport:
  reportId: IR-2026-1013
  changeReference: run-f94564cb61ce fix-bug, defect runs/inputs/release-handoff-verdict-defect-report.md
  sourceInputs:
    - type: bug-analysis
      reference: runs/run-f94564cb61ce/states/triage-and-impact/artifacts/bug-analysis.md
    - type: bug-analysis
      reference: runs/run-f94564cb61ce/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: architecture-decision-record
      reference: architect ruling on the release-vocabulary question (operator-supplied file, session scratchpad, outside the repository)
    - type: change-request
      reference: omn-tech-lead ruling on the CR-003 pins and the bundle sync (operator-supplied file, session scratchpad, outside the repository)
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: fix-implementation
  verificationStatus: partially-verified
  inputDigest: sha256:ee54571a8bdd7313d36ff6b821da59dd
  contextDigest: sha256:850b48df6ab3cc41c8f0e1fe7fb61411
```

## Metadata

- Report ID: IR-2026-1013
- Change reference: run-f94564cb61ce fix-bug, defect runs/inputs/release-handoff-verdict-defect-report.md
- Workflow phase: fix-implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

## Implementation Summary

- Change intent: each of the four non-deploying omn-documentation phases now has a truthful release position that the Validation Engine accepts (`handed-off`, `findings-published`, `delta-published`), the release phase keeps `released`, `partial`, `rolled-back` with R4 and R5 unchanged, withheld fails everywhere, and the validator decides the verdict against evidence (R8 on `sourceInputs` types, R9 on the envelope `state_id`) instead of vocabulary membership, so a deployment verdict with no deployment status no longer passes.
- Approach taken: implemented the root-cause-analysis fix strategy, which adopts the architect ruling on the vocabulary question as corrected by that analysis's evidence entries on envelope plumbing, verifier re-validation, the `validation-report` type set, and the four pinned files; Stage 8 rekeyed on basis; R8/R9 added inside the existing `semantic_checks` (rung 2, reusing the shared contract engine) with an optional `envelope` parameter, and the command-line path reads `--envelope` in the validator's own `main` so `artifact_contract.cli` is untouched (rung 6); verify_validators gains one `SUPERSEDED_CONTRACTS` table and two small functions beside the existing candidate selector (rung 7: no existing selector rule could exclude by contract version, and the analysis forbids an exemption inside the validator); the only new file is the regression test module, required because the knowledge test files are frozen to this phase; bundle mirrored with `PYTHONPATH=. python tests/test_bundled_payload.py --sync`; no dependency added.
- Design reference: root-cause-analysis bug-analysis (sha256:1e9b135e23d17f7d36a81df95519e9f0) Fix Strategy, eight conditions; triage bug-analysis (sha256:f902dcda2b9ee3ef30f1f5a402eb9991); architect ruling sections 1 to 6; Triage Gate rationale in state.json; omn-tech-lead ruling on the CR-003 pins and the bundle sync.
- Out of scope: the 9 recorded notes and the held run-c9fb8d5bbb32 note stay as recorded (run evidence is immutable and outside this agent's writes); the change proposal that lists them and records FC-020 O-006 closed lives under proposals/, which this agent may not write (Q-002); the C3.2 vendor-token failure of the held note is out of scope per the Triage Gate; tests/test_knowledge.py and tests/fixtures/knowledge/ were not touched; the orchestration-result deployment-state vocabulary is untouched because no other module reads releaseVerdict; the module Status lines that still read version 1.0.0 were left as the 1.1.0 bump left them.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | agents/omn-documentation/reasoning.md | modified | Stage 8 table keyed on communication basis, one complete row per non-deploying basis, withheld rows per basis, deployment status selects no row outside post-release | RCA fix condition 1; architect ruling section 3 |
| `C-002` | agents/omn-documentation/identity.md | modified | Required Evidence rows for the three new positions and a quality-summary bullet for the basis rule | RCA fix condition 2 (Required Evidence table) |
| `C-003` | agents/omn-documentation/output.md | modified | Release position column in the Deliverable table, six-value releaseVerdict row, Known Issues `None identified.` rule, evidence-type rule, Environment guidance, `validation-report` declared type | RCA fix condition 2; evidence entry on the type set |
| `C-004` | agents/omn-documentation/quality.md | modified | R1 text names six values and withheld never passes; new Blocking R8 and R9 rows | RCA fix conditions 2 and 3 |
| `C-005` | agents/omn-documentation/system.md | modified | Boundary row refusing to record a non-deploying publication as released | architect ruling section 5 (recommended charter row) |
| `C-006` | templates/release-note.md | modified | Template 1.2.0: usage names the five phases, six-value verdict comment, `validation-report` type, Known Issues comment | RCA fix conditions 2 and 6 |
| `C-007` | runtime/release_note_validator.py | modified | Six-value VERDICTS, PHASE_BASIS, VERDICT_OF_BASIS, VERDICT_EVIDENCE, Blocking R8, R9 (Advisory only without an envelope), envelope reaches R9 via validate and the own command line, communicationBasis count | RCA fix conditions 2, 3, 4 |
| `C-008` | runtime/verify_validators.py | modified | Committed notes produced below omn-documentation 1.2.0 are reported as superseded and excluded from selection and re-validation; documented selection rule updated; envelope label robust to out-of-tree paths | RCA fix condition 5 |
| `C-009` | agents/omn-documentation.agent.md | modified | Host registration version table and bootstrap check at 1.2.0 | RCA fix condition 6 |
| `C-010` | agents/omn-documentation/manifest.yaml | modified | metadata.version 1.2.0 | RCA fix condition 6 |
| `C-011` | registry/agents.yaml | modified | omn-documentation record at 1.2.0, required because the runtime rejects a manifest/registry mismatch | RCA fix condition 6 |
| `C-012` | registry/templates.yaml | modified | release-note record at 1.2.0, description names the five phases and the basis rule | RCA fix condition 6; `V-003` |
| `C-013` | runtime/README.md | modified | Validator table names all five served phases; paragraph on R8, R9, and the superseded-contract rule | RCA fix condition 6 |
| `C-014` | omn_agent/_bundled_payload/agents/omn-documentation.agent.md | modified | Mirror of `C-009` | RCA fix condition 7 |
| `C-015` | omn_agent/_bundled_payload/agents/omn-documentation/identity.md | modified | Mirror of `C-002` | RCA fix condition 7 |
| `C-016` | omn_agent/_bundled_payload/agents/omn-documentation/manifest.yaml | modified | Mirror of `C-010` | RCA fix condition 7 |
| `C-017` | omn_agent/_bundled_payload/agents/omn-documentation/output.md | modified | Mirror of `C-003` | RCA fix condition 7 |
| `C-018` | omn_agent/_bundled_payload/agents/omn-documentation/quality.md | modified | Mirror of `C-004` | RCA fix condition 7 |
| `C-019` | omn_agent/_bundled_payload/agents/omn-documentation/reasoning.md | modified | Mirror of `C-001` | RCA fix condition 7 |
| `C-020` | omn_agent/_bundled_payload/agents/omn-documentation/system.md | modified | Mirror of `C-005` | RCA fix condition 7 |
| `C-021` | omn_agent/_bundled_payload/registry/agents.yaml | modified | Mirror of `C-011` | RCA fix condition 7 |
| `C-022` | omn_agent/_bundled_payload/registry/templates.yaml | modified | Mirror of `C-012` | RCA fix condition 7 |
| `C-023` | omn_agent/_bundled_payload/runtime/README.md | modified | Mirror of `C-013` | RCA fix condition 7 |
| `C-024` | omn_agent/_bundled_payload/runtime/release_note_validator.py | modified | Mirror of `C-007` | RCA fix condition 7 |
| `C-025` | omn_agent/_bundled_payload/runtime/verify_validators.py | modified | Mirror of `C-008` | RCA fix condition 7 |
| `C-026` | omn_agent/_bundled_payload/templates/release-note.md | modified | Mirror of `C-006` | RCA fix condition 7 |
| `C-027` | tests/test_release_verdict.py | added | 29 regression tests: per-phase positions with and without envelope, withheld everywhere, R8 type sets, R9 incl. command line, release phase R4/R5, contract agreement, versions, bundle parity, superseded selection and V3 | RCA Validation Plan, regression tests added |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Defect witness: the new module run against an unmodified HEAD copy of the framework tree fails 24 of 29 tests; only the withheld and four release-phase regressions pass | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013`, `C-027` | `PYTHONPATH=. python -W ignore -m unittest tests.test_release_verdict` (in a git-archive HEAD copy) | fail |
| `T-002` | The same module on the fixed tree: every assertion of `T-001` holds | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013`, `C-027` | `PYTHONPATH=. python -W ignore -m unittest tests.test_release_verdict` | pass |
| `T-003` | Regression baseline before any edit: 739 tests, 27 of 28 modules; only test_demo_capture fails (3, ffmpeg option unsupported) | regression | `C-001` to `C-027` (comparator) | `PYTHONPATH=. python -W ignore tools/run_tests_parallel.py` | fail |
| `T-004` | Full suite after the change: 767 tests, 28 of 29 modules; the same 3 test_demo_capture failures and nothing else; test_knowledge 49/49 | regression | `C-001` to `C-027` | `PYTHONPATH=. python -W ignore tools/run_tests_parallel.py` | fail |
| `T-005` | BackwardCompatibilityTestCase on the combined tree (CR-003 landed, this change present): 6 of 6 pass | regression | `C-006`, `C-011`, `C-012`, `C-013` | `PYTHONPATH=. python -W ignore -m unittest tests.test_knowledge.BackwardCompatibilityTestCase -v` | pass |
| `T-006` | Release fixture with no envelope passes 32/32, R9 declared not-machine-checkable | regression | `C-006`, `C-007` | `python -W ignore runtime/release_note_validator.py runtime/fixtures/release-note.md` | pass |
| `T-007` | Each of the 9 superseded notes, with its own envelope, fails exactly R8 and R9; the held note fails C3.2, R1, R8, R9; the investigate note's R9 expects findings-published | regression | `C-007` | `python -W ignore runtime/release_note_validator.py <note> --envelope <its invocation-envelope.json>` over all 10 notes | pass |
| `T-008` | Reproduction inverted: the held-run note with releaseVerdict handed-off and its envelope passes R1, R8, R9; only C3.2 remains | regression | `C-007` | `python -W ignore runtime/release_note_validator.py <scratch copy> --envelope runs/run-c9fb8d5bbb32/states/documentation-and-release-handoff/invocation-envelope.json` | pass |
| `T-009` | Existing suites that import the validator or the verifier: test_verify_validators_mutations 26/26, test_investigate_research_handoffs 22/22 | regression | `C-007`, `C-008` | `PYTHONPATH=. python -W ignore tools/run_tests_parallel.py` (module lines) | pass |
| `T-010` | Verifier baseline before any edit: 5 of 6; V3 fails only on framework-change-proposal F7 (FC-020 scope rows) | regression | `C-008` | `python -W ignore runtime/verify_validators.py` | fail |
| `T-011` | Verifier after the change: 5 of 6, V3 fails only on the same F7; release-note validated on the fixture, 9 candidates reported superseded, V4 caught by R2 | integration | `C-007`, `C-008` | `python -W ignore runtime/verify_validators.py` | fail |
| `T-012` | Manifest and registry verifiers accept the 1.2.0 versions: 2/2 CONFORMS and 8/8 COVERED | static | `C-009`, `C-010`, `C-011`, `C-012` | `python -W ignore runtime/verify_manifests.py`; `python -W ignore runtime/verify_registry_coverage.py` | pass |
| `T-013` | Bundle parity 11/11 after sync; bundle diff holds only the 13 mirrors and no memory/lessons path | contract | `C-014`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026` | `PYTHONPATH=. python -W ignore -m unittest tests.test_bundled_payload`; `git status --short --untracked-files=all omn_agent/` | pass |

## Verification Results

- Verification method: the new module was run first against an unmodified HEAD copy to witness the defect, then on the fixed tree; the full suite and the validator coverage verifier were run before any edit and again after, and compared; the 10 recorded notes were re-validated with their own envelopes; runtime verifiers were run from the framework directory; verify_multi_phase and verify_vertical_slice were not run, because they mutate the run they select.
- Commands executed: `PYTHONPATH=. python -W ignore tools/run_tests_parallel.py` (before and after); `PYTHONPATH=. python -W ignore -m unittest tests.test_release_verdict` (pre-edit tree: 23 of 28 failed; HEAD copy: 24 of 29 failed; fixed tree: 29/29); `PYTHONPATH=. python -W ignore -m unittest tests.test_knowledge.BackwardCompatibilityTestCase -v`; `PYTHONPATH=. python -W ignore -m unittest tests.test_bundled_payload`; `PYTHONPATH=. python tests/test_bundled_payload.py --sync`; `python -W ignore runtime/verify_validators.py` (before and after); `python -W ignore runtime/release_note_validator.py` over the fixture, the 10 notes, and the inverted held note; `python -W ignore runtime/verify_manifests.py`; `python -W ignore runtime/verify_registry_coverage.py`.
- Result summary: 13 evidence entries executed, 9 passed, 4 failed; `T-001` fails by design as the defect witness; `T-003` and `T-004` fail only on the 3 environmental test_demo_capture failures present at baseline; `T-010` and `T-011` fail only on the framework-change-proposal F7 failure present at baseline; no failure is attributable to this change; CR-003 has landed in tests/test_knowledge.py, and BackwardCompatibilityTestCase passes 6/6 and test_knowledge 49/49 on the combined tree with this change present (`T-004`, `T-005`).
- Unverified areas: the runtime acceptance path end to end (a dispatched omn-documentation phase completed through framework_runtime) was not executed, only the same validate(path, envelope) call it makes; verify_multi_phase and verify_vertical_slice were not run; a re-dispatch of run-c9fb8d5bbb32 under the 1.2.0 contract was not exercised, and registered agents may still read the main checkout's contract text (`R-001`).

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | R8 fails an absent or malformed sourceInputs list and a verdict outside the vocabulary, but does not reject entries whose type is outside the declared list (`C-007`) | architect ruling section 2, "absent/malformed/out-of-vocabulary list fails" | the RCA fix condition states R8 only against verdict evidence, and recorded notes legitimately list `architecture-context`; a per-entry type ban would be a new restriction no accepted condition names | raised as `Q-002` to architect |
| `V-002` | `validation-report` added to the declared sourceInputs types in the output contract and the template comment (`C-003`, `C-006`) | architect ruling section 1, list review evidence as `verification-report` | the RCA requires R8 to accept `validation-report`; a contract that the validator accepts but the output contract does not declare would disagree with itself | raised as `Q-002` to architect |
| `V-003` | The release-note registry description and the template usage line rewritten to name the five phases, beyond the version bump (`C-006`, `C-012`) | RCA fix condition 6, version bump only for the registry record | both stated the release phase alone, which the change makes false; the registry file is edited by this change in any case | not-required |
| `V-004` | verify_validators reports a summary envelope through `instance_label` rather than `relative_to` (`C-008`) | RCA fix condition 5 | the old form raised for an envelope outside the framework tree, which the new verifier tests construct; output is unchanged for in-tree paths | not-required |

## Boundary Compliance

- Module boundaries preserved: the shared command-line hook `artifact_contract.cli` and every other validator are unchanged; the envelope reaches R9 through the release-note validator's own `validate` and `main`; the superseded rule lives in the verifier and is read from the validator's `CURRENT_CONTRACT_VERSION`, so the validator exempts nothing; schemaVersion stays 1.0.0 and no workflow file changed.
- Public interface changes: `release_note_validator.semantic_checks` gains an optional `envelope` parameter and `main` an optional `argv`; new module constants PHASE_BASIS, VERDICT_OF_BASIS, VERDICT_EVIDENCE, CURRENT_CONTRACT_VERSION; verify_validators gains SUPERSEDED_CONTRACTS, superseded_reason, superseded_candidates, committed_with_envelopes and a `superseded_candidates` key per summary; omn-documentation contract and release-note template move to 1.2.0 with three new verdict values.
- Data or migration impact: none on stored data; the 9 recorded notes and the held note now fail R8 and R9 on re-validation and are reported as superseded by the verifier, and no run evidence was edited.
- Declared side effects: `C-001` to `C-027`, plus runs/run-f94564cb61ce/states/fix-implementation/artifacts/implementation-report.md and runs/run-f94564cb61ce/states/fix-implementation/result-envelope.json; scratch copies used for `T-001` and `T-008` sit in the session scratchpad outside the repository.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | Registered agents may read contract text from the main checkout (FC-020 O-007), so a re-dispatch of run-c9fb8d5bbb32 before landing could still read the old Stage 8 | medium | the held run would again emit withheld or a deployment verdict | none in this change; the superseded-candidate count in verify_validators would grow past 9 if a note is produced under the old contract |
| `R-002` | The omn-documentation version bump resets gate auto-approval precedent keyed on agent version (FC-020 R-003) | high | the next omn-documentation gates need explicit decisions | none; an expected consequence of the bump |
| `R-003` | verify_validators V3 fails on the framework-change-proposal F7 scope-row check for FC-020, identical before and after this change (`T-010`, `T-011`) | high | the coverage verifier reports NOT COVERED regardless of this fix | baseline evidence recorded; not caused by this change |
| `R-004` | test_demo_capture fails 3 tests because the installed ffmpeg rejects an option, identical at baseline (`T-003`, `T-004`) | high | the full suite exits 1 on this host | baseline evidence recorded; environmental |
| `R-005` | Without an envelope R9 is not machine-checkable, so a release-phase note carrying handed-off and a verification record passes a bare command-line run | low | an operator validating by hand could accept a wrong basis | the runtime acceptance path, close_legacy_run, and verify_validators all pass the envelope; R9 reports not-machine-checkable explicitly |
| `R-006` | The held run's note still fails C3.2 on a vendor token in its Environment line after a handed-off re-dispatch (`T-008`) | high | run-c9fb8d5bbb32 cannot close until that is settled | out of scope per the Triage Gate; routed to omn-orchestrator by the analysis |

## Handoff Notes

- Reviewer focus areas: R8 and R9 in runtime/release_note_validator.py and the command-line envelope path (`C-007`, `V-001`, `R-005`); the superseded-contract exclusion in runtime/verify_validators.py and its documented rule (`C-008`, `V-004`); the Stage 8 table against the five Phase Models (`C-001`); the `validation-report` type addition (`V-002`); the four pinned files edited under the tech-lead ruling (`C-006`, `C-011`, `C-012`, `C-013`).
- Follow-up work: the change proposal listing the 9 superseded notes with their `T-007` re-validation and recording FC-020 O-006 closed (`Q-001`); re-dispatch of run-c9fb8d5bbb32 to yield handed-off once C3.2 is settled; the architect confirmation of the superseded-contract amendment and of `V-001`/`V-002` (`Q-002`); settling the FC-020 F7 scope rows (`R-003`).
- Documentation impact: omn-documentation contract 1.2.0 and release-note template 1.2.0 are the new documentation; runtime/README.md updated; the bundled payload mirrors all of it; any operator guidance that tells an implement-feature run to record `released` is now false.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | The change proposal under proposals/, outside this agent's writes, must list the 9 superseded notes and their re-validation and record FC-020 O-006 closed; who produces it in this run | no | omn-orchestrator | `C-007`, `C-008` |
| `Q-002` | Confirm the superseded-contract exclusion in the verifier, R8 not rejecting out-of-list entry types, and `validation-report` as a declared sourceInputs type | no | architect | `C-003`, `C-006`, `C-007`, `C-008` |
