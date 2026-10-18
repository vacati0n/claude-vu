```yaml
validationReport:
  reportId: VR-run-e7bf0d73027a-regression-validation-a2
  validationReference: run-e7bf0d73027a fix-bug, defect runs/inputs/recovery-x1-policy-exception-defect-report.md, change IR-2026-1015 (C-001 to C-003), retest after Verification Gate rejection RB-run-e7bf0d73027a-verification-gate-01 with the regression tests of IR-2026-1018 in place
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md
    - type: bug-analysis
      reference: runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: acceptance-criteria
      reference: runs/inputs/recovery-x1-policy-exception-defect-report.md
    - type: acceptance-criteria
      reference: runs/run-e7bf0d73027a/state.json, Triage Gate, Fix Gate and Verification Gate rationale
    - type: scope-definition
      reference: runs/run-e7bf0d73027a/task-context.yaml
    - type: test-evidence
      reference: runs/run-5e9d799db687/states/fix-implementation/artifacts/implementation-report.md
    - type: known-issues
      reference: runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass
  inputDigest: sha256:e4820205cf8350c72e629a339851cde1
  contextDigest: sha256:9978ebb5cb624a7226773a03f0b6ee13
```

## Metadata

- Validation ID: VR-run-e7bf0d73027a-regression-validation-a2
- Validator: omn-qa
- Change under validation: the policy-exception row and scoped placeholder exemption in verify_recovery.py clearing_action_admissible and its bundled mirror (IR-2026-1015), with the regression tests now present: tests/test_clearing_action_admissibility.py including RollbackRowUnchangedTestCase, and tests/test_policy_exception_command.py (IR-2026-1018, run-5e9d799db687)
- Validation date: 2026-10-18

## Validation Scope

- In scope: criteria AC-001 to AC-009, the same set and order as attempt 1, from the defect report's expected behaviour, the Triage Gate conditions addressed to the fix, and the root-cause analysis Validation Plan, each re-judged on checks executed in this attempt; the open defects DF-001 and DF-002 of attempt 1 retested; the Fix Gate's carried conditions (end-to-end gap V-001, rollback row unpinned, CI result R-002 unobserved); the regression surface the analysis named (X1 and D4, D23, D27 via the shared admissibility function, the executable helper, bundled-payload parity, FR-03 via the verifier exit code) and the full repository test suite.
- Out of scope: code quality of both test modules and the filled-role guard design of V-002 (omn-dev-2-reviewer); the Triage Gate condition addressed to root-cause-analysis (discharged there by E-018); the runtime clearing-action builder and cmd_policy_exception as change targets (unchanged, per the root-cause analysis); whether the empty-owner-list policy-exception behaviour is correct (open design question raised in run-5e9d799db687, architect); run-5e9d799db687's own verdict, deliberately not inherited; rewriting proposals FC-016 to FC-022 or closing O-015 (governance records, owner's decision); CI runner observation (no external access in this phase).
- Evidence examined: implementation-report IR-2026-1015 (sha256:e4820205cf8350c72e629a339851cde1); IR-2026-1018 of run-5e9d799db687 for provenance and claimed results; the root-cause bug-analysis; the defect report; gate rationale in state.json; task-context.yaml; attempt-1 validation report (sha256:234ba14d24a911b742245737c7fb501f); both test modules read in full; python -m unittest of both modules; both modules against git show HEAD:runtime/verify_recovery.py in a tree copy; runtime/verify_recovery.py in the worktree and with and without --keep in a tree copy; a scratch judge script over the kept policy envelope; cmp of the bundled copy; tests/test_bundled_payload.py; tools/run_tests_parallel.py; git status before and after. Rescan: tests/test_policy_exception_command.py and IR-2026-1018 are not named in the task context's changed_files, and were read because the retest's evidence lives there.

## Test Strategy

- Risk basis: the change alters a path that decides whether work proceeds (X1 sets the verifier exit code that FR-03 and the CI job gate on), so every branch of the new row and exemption predicate was exercised, with a fail-before witness against HEAD; it alters security-relevant handling (which placeholders are exempt, the producer and unlisted-role guards), so those refusals were exercised in the table and through the runtime command; it writes or migrates no data (the database trigger is the word migration in "no data or migration impact"), confirmed by run-f94564cb61ce unmodified and git status unchanged after every run.
- Levels executed: unit, integration, end-to-end, security
- Environment: this worktree on a Windows 11 host with Python 3.14.0, TEMP and TMP set to D:/rvw-tmp-5df08e for every command; a temporary copy of the framework tree at D:/rvw-tmp-5df08e/qa-e7bf-a2/tree with an identical runtime for the --keep runs and the HEAD witness; differs from target in that the CI ubuntu and windows runners were not observed.
- Not executed: performance, because no performance-sensitive path changed and S08 was not triggered; CI execution, because this phase has no external system access; the release checklist verifier, because FR-03 is the recovery verifier's exit code, observed directly here, and the checklist binds the change proposal at closure; the mutation witnesses T-004 and T-005 of IR-2026-1018, which are reported there and were not re-run here, the HEAD witness standing in for the admissibility module.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| AC-001 | An open envelope whose clearing action is `policy-exception` on a state work item blocked `awaiting_policy_exception` is judged admissible, with its human-judgement arguments allowed to stay placeholders, and inadmissible otherwise. | defect report, Expected behaviour | end-to-end | met | judge script on the kept envelope of run-d8870619db82 in the tree copy: admissible on the item blocked awaiting_policy_exception; placeholder-inadmissible once the item is pending, completed, or blocked awaiting_recovery_task; unit module 23/23 covers the other positions |
| AC-002 | `verify_recovery.py` reports 74/74. | defect report, Expected behaviour | end-to-end | met | python runtime/verify_recovery.py in the worktree: exit 0, 74/74 RECOVERY PROVEN, X1 pass over 9 open envelopes in 4 runs; tree copy --keep (twice) and without --keep, the same |
| AC-003 | the placeholder exemption covers only policy-exception on state items blocked awaiting_policy_exception, with negative cases tested | state.json Triage Gate rationale | unit | met | python -m unittest tests.test_clearing_action_admissibility -v: 23/23 OK incl. release gaining no exemption and pending, completed, other-blocked, gate-name, run-id and phase placeholder cases; against HEAD verify_recovery.py 8 of 25 fail, all policy-exception cases |
| AC-004 | the bundled payload copy changes the same way | state.json Triage Gate rationale | unit | met | cmp of runtime/verify_recovery.py and omn_agent/_bundled_payload/runtime/verify_recovery.py: identical; PYTHONPATH=. python tests/test_bundled_payload.py: 11/11 OK |
| AC-005 | Verification steps: in a temporary copy of the tree, run python runtime/verify_recovery.py --keep and then without --keep, expecting 74/74 RECOVERY PROVEN with X1 passing over the policy run's open envelope, and git status unchanged afterwards; confirm the condition, not only the symptom, by showing the table now judges the emitted policy-exception action admissible on the blocked item and still inadmissible on each negative case below. | root-cause bug-analysis, Validation Plan | end-to-end | met | tree copy: --keep exit 0 74/74 with the policy run run-d8870619db82 kept, then without --keep exit 0 74/74 and the runs listing back to its baseline; worktree git status equal to baseline after every run; condition shown by AC-001 and AC-006 evidence |
| AC-006 | positive and negative admissibility cases for policy-exception — inadmissible on a pending item, an item blocked awaiting_recovery_task or awaiting_human_decision, a completed item, an unknown phase, a gate name, and a placeholder after --run-id or --phase | root-cause bug-analysis, Validation Plan | unit | met | tests.test_clearing_action_admissibility: each named case present and passing (23/23); tests.test_policy_exception_command: producer role and unlisted role refused by the runtime with exit 2 and no write (2/2 OK) |
| AC-007 | unchanged gate and rollback cases | root-cause bug-analysis, Validation Plan | unit | met | test_gate_action_keeps_its_exemption and RollbackRowUnchangedTestCase 7/7 pass on the change and the same 8 pass against HEAD verify_recovery.py, so gate and rollback verdicts are unchanged; emitted rollback action leaves only --decided-by a placeholder |
| AC-008 | a test pinning every command-naming branch of the clearing-action builder to an admissibility row | root-cause bug-analysis, Validation Plan | unit | met | BuilderTablePinTestCase passes on the change and fails for subTest policy-exception against HEAD; it scans clearing_action and rollback_clearing_action sources for every named subcommand |
| AC-009 | an end-to-end scenario that executes the action with role, decider and rationale filled and shows the block cleared and the envelope resolved, as `E-018` did | root-cause bug-analysis, Validation Plan | end-to-end | met | python -m unittest tests.test_policy_exception_command -v: 2/2 OK; executes the envelope's action via the runtime CLI in a tree copy with the three human arguments filled; asserts item pending, blocked_reason cleared, envelope and ledger resolved, policy-exception.json written, one escalation_resolved event |

## Execution Summary

- Criteria validated: 9
- Met: 9
- Not met: 0
- Blocked: 0

## Defects

| ID | Severity | Category | Location | Symptom | Reproducibility | Status |
|---|---|---|---|---|---|---|
| DF-001 | medium | functional | runtime/verify_recovery.py and tests/ (no policy-exception execution) | Attempt 1: no automated case executed the policy-exception action filled (AC-009); retest: tests/test_policy_exception_command.py now executes it and passes 2/2 | always | resolved |
| DF-002 | medium | functional | tests/test_clearing_action_admissibility.py | Attempt 1: the module had no unchanged-rollback case (AC-007); retest: RollbackRowUnchangedTestCase present, 7/7 pass on the change and against HEAD | always | resolved |

## Regression Assessment

- Regression scope: X1 and the scenario D checks D4, D23, D27 that share clearing_action_admissible and its placeholder filter; the executable helper's one-placeholder assertion; bundled-payload exact-match; the verifier exit code that FR-03 and the CI job read; every other repository test module.
- Regressions detected: None identified.
- Coverage of changed behavior: every branch of the policy-exception row and the awaiting_policy_exception exemption predicate by the unit module and, for the emitted action, by the judge script; the gate, release and rollback exemptions by unit cases, the rollback row against a real rejected-gate store; the runtime command by the end-to-end module; D4, D23, D27 and X1 pass in the verifier; full suite 796 of 796 tests ran, 31/32 modules passed, the only failure being the 3 known test_demo_capture EndToEndEditTestCase ffmpeg cases (implementation risk R-001).
- Untested areas: an automated X1 re-check after the block is cleared (shown only by the analysis's manual E-018); whether the empty-owner-list case of cmd_policy_exception is correct (exercised, not asserted); the mutation witnesses of IR-2026-1018 (reported, not re-run); the CI ubuntu and windows runners; Python versions other than 3.14.0.

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: the CI job result is unobserved and is not evidence (implementation risk R-002); the end-to-end module depends on committed run evidence run-c5a8d50d3238 as its conforming artifact, so a change to that record would break the test rather than the behaviour; the regression tests that close DF-001 and DF-002 were delivered under run-5e9d799db687, so this run's change set IR-2026-1015 does not list them (Q-002).
- Monitoring required: the recovery verifier job on the default branch observed green first-hand; FR-03 rows in later proposals recording pass; any X1 or D4, D23, D27 output listing an inadmissible envelope.

## Verdict

- Decision: pass
- Rationale: the Stage 8 row with no open critical or high defect and no criterion not-met or blocked yields pass; all nine criteria are met on checks executed in this attempt, DF-001 and DF-002 are resolved by the tests now present, and no regression was detected.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that omn-dev-2-reviewer, deciding the Verification Gate under producer exclusion, approve on this report, noting CI result R-002 remains unobserved (Q-001) and the cross-run provenance of the tests (Q-002).

## Open Questions

- Q-001: Is the CI recovery verifier job green on ubuntu and windows runners for this change? Not observable in this phase; routed to omn-orchestrator.
- Q-002: Should the closure record of this run link IR-2026-1018 of run-5e9d799db687 as the source of the tests that resolved DF-001 and DF-002? Routed to omn-orchestrator.
