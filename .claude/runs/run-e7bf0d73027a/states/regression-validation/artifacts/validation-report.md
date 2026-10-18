```yaml
validationReport:
  reportId: VR-run-e7bf0d73027a-regression-validation
  validationReference: run-e7bf0d73027a fix-bug, defect runs/inputs/recovery-x1-policy-exception-defect-report.md, change IR-2026-1015 (C-001 to C-003)
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md
    - type: bug-analysis
      reference: runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: bug-analysis
      reference: runs/run-e7bf0d73027a/states/triage-and-impact/artifacts/bug-analysis.md
    - type: acceptance-criteria
      reference: runs/inputs/recovery-x1-policy-exception-defect-report.md
    - type: acceptance-criteria
      reference: runs/run-e7bf0d73027a/state.json, gates Triage Gate and Fix Gate rationale
    - type: scope-definition
      reference: runs/run-e7bf0d73027a/task-context.yaml
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: fail
  inputDigest: sha256:e4820205cf8350c72e629a339851cde1
  contextDigest: sha256:9978ebb5cb624a7226773a03f0b6ee13
```

## Metadata

- Validation ID: VR-run-e7bf0d73027a-regression-validation
- Validator: omn-qa
- Change under validation: the policy-exception row and scoped placeholder exemption in verify_recovery.py clearing_action_admissible, its bundled mirror, and tests/test_clearing_action_admissibility.py (IR-2026-1015)
- Validation date: 2026-10-18

## Validation Scope

- In scope: criteria AC-001 to AC-009 from the defect report's expected behaviour, the Triage Gate conditions addressed to the fix, and the root-cause analysis Validation Plan; the Fix Gate's carried conditions (the end-to-end gap of implementation deviation V-001, the rollback row not pinned by the new module, CI result R-002 unobserved); the regression surface the analysis named (X1 and D4, D23, D27 via the shared admissibility function, the executable helper, bundled-payload parity, FR-03 via the verifier exit code) and the full repository test suite.
- Out of scope: code quality and the filled-role guard design of V-002 as a design choice (omn-dev-2-reviewer, decided at the Fix Gate); the Triage Gate condition addressed to root-cause-analysis (closing its end-to-end question, discharged there by E-018); the runtime clearing-action builder and cmd_policy_exception as change targets (unchanged, per the root-cause analysis); rewriting proposals FC-016 to FC-022 or closing O-015 (governance records, owner's decision); CI runner observation (no external access in this phase, routed to omn-orchestrator at triage).
- Evidence examined: implementation-report IR-2026-1015 (sha256:e4820205cf8350c72e629a339851cde1); triage and root-cause bug-analysis artifacts; the defect report; Triage and Fix Gate rationale in state.json; task-context.yaml; git diff of runtime/verify_recovery.py; cmp of the bundled copy; tests/test_clearing_action_admissibility.py read in full and run against the change and against HEAD; tests/test_bundled_payload.py; runtime/verify_recovery.py run twice in the worktree and with and without --keep in a temporary tree copy; a scratch end-to-end script executing the emitted policy-exception action in that copy; tools/run_tests_parallel.py full suite; test_gate_rollback re-run; grep of tests/ for any policy-exception execution.

## Test Strategy

- Risk basis: the change alters a path that decides whether work proceeds (X1 decides the verifier's exit code, which FR-03 and the CI job gate on), so every branch of the new row and of the exemption predicate was exercised; it alters security-relevant handling (which placeholders are exempt, and the self-exception guard), so the producer-role refusal was exercised in both table and runtime; it writes or migrates no data (the database trigger is the word migration in "no data or migration impact"), confirmed by run-f94564cb61ce and git status unchanged after every run.
- Levels executed: unit, integration, end-to-end, security
- Environment: this worktree on a Windows 11 host with Python 3.14.0, and a temporary copy of its framework tree at D:/rvw-tmp-5df08e/qa-e7bf/tree with an identical runtime (diff -rq empty); differs from target in that the CI ubuntu and windows runners were not observed; the first full-suite run and the first two worktree verifier runs used the host's C: temp directory because the shell replaced TEMP and TMP, later runs set TMPDIR to D:/rvw-tmp-5df08e.
- Not executed: performance, because no performance-sensitive path changed and S08 was not triggered; CI execution, because this phase has no external system access; the release checklist verifier, because FR-03 is the recovery verifier's exit code, observed directly here, and the checklist binds the change proposal at closure.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| AC-001 | An open envelope whose clearing action is `policy-exception` on a state work item blocked `awaiting_policy_exception` is judged admissible, with its human-judgement arguments allowed to stay placeholders, and inadmissible otherwise. | defect report, Expected behaviour | end-to-end | met | e2e script in the tree copy: the open envelope FE-run-d8870619db82-execution-planning-01 as emitted judged admissible on the blocked item; the same action judged inadmissible (placeholder) once the item was pending; unit module 16/16 covers the other positions |
| AC-002 | `verify_recovery.py` reports 74/74. | defect report, Expected behaviour | end-to-end | met | python runtime/verify_recovery.py: worktree runs 1 and 2 exit 0, 74/74 RECOVERY PROVEN, X1 pass over 9 open envelopes in 4 runs; tree copy --keep and without --keep, the same |
| AC-003 | the placeholder exemption covers only policy-exception on state items blocked awaiting_policy_exception, with negative cases tested | state.json Triage Gate rationale | unit | met | python -m unittest tests.test_clearing_action_admissibility -v: 16/16 OK, incl. release gaining no exemption and pending, completed, other-blocked, gate-name, run-id and phase placeholder cases; against HEAD 8 of 16 fail |
| AC-004 | the bundled payload copy changes the same way | state.json Triage Gate rationale | unit | met | cmp of runtime/verify_recovery.py and omn_agent/_bundled_payload/runtime/verify_recovery.py: identical; PYTHONPATH=. python tests/test_bundled_payload.py: 11/11 OK |
| AC-005 | Verification steps: in a temporary copy of the tree, run python runtime/verify_recovery.py --keep and then without --keep, expecting 74/74 RECOVERY PROVEN with X1 passing over the policy run's open envelope, and git status unchanged afterwards; confirm the condition, not only the symptom, by showing the table now judges the emitted policy-exception action admissible on the blocked item and still inadmissible on each negative case below. | root-cause bug-analysis, Validation Plan | end-to-end | met | tree copy: --keep exit 0 74/74, then without --keep exit 0 74/74, injected inputs removed, run-f94564cb61ce identical; worktree git status equal to its baseline after every run; condition shown by AC-001 and AC-006 evidence |
| AC-006 | positive and negative admissibility cases for policy-exception — inadmissible on a pending item, an item blocked awaiting_recovery_task or awaiting_human_decision, a completed item, an unknown phase, a gate name, and a placeholder after --run-id or --phase | root-cause bug-analysis, Validation Plan | unit | met | tests.test_clearing_action_admissibility: each named case present and passing (16/16); e2e script: producer role refused by table and by the runtime (exit 2, policy-failure), repeat after clearance refused (exit 2) |
| AC-007 | unchanged gate and rollback cases | root-cause bug-analysis, Validation Plan | unit | not-met | the added module carries a gate case (test_gate_action_keeps_its_exemption) and no rollback case; rollback row behaviour is unchanged per verifier D4, D23, D27 passing, which are existing checks, not added cases; see DF-002 |
| AC-008 | a test pinning every command-naming branch of the clearing-action builder to an admissibility row | root-cause bug-analysis, Validation Plan | unit | met | BuilderTablePinTestCase passes on the change and fails for policy-exception against HEAD; it scans clearing_action and rollback_clearing_action sources for every named subcommand |
| AC-009 | an end-to-end scenario that executes the action with role, decider and rationale filled and shows the block cleared and the envelope resolved, as `E-018` did | root-cause bug-analysis, Validation Plan | end-to-end | not-met | no test or verifier scenario in the repository executes policy-exception (grep of tests/ and verify_recovery.py; implementation deviation V-001); the behaviour itself holds: executed here, exit 0, item blocked to pending, envelope resolved, policy-exception.json written, X1 re-check pass; see DF-001 |

## Execution Summary

- Criteria validated: 9
- Met: 7
- Not met: 2
- Blocked: 0

## Defects

| ID | Severity | Category | Location | Symptom | Reproducibility | Status |
|---|---|---|---|---|---|---|
| DF-001 | medium | functional | runtime/verify_recovery.py and tests/ (no policy-exception execution) | No regression test or verifier scenario executes the policy-exception action with role, decider and rationale filled; the planned end-to-end scenario (AC-009) is absent, so the runtime command has no automated execution coverage | always | open |
| DF-002 | medium | functional | tests/test_clearing_action_admissibility.py | The added regression module carries an unchanged-gate case but no unchanged-rollback case (AC-007); the rollback row is reached only by existing verifier checks D4, D23, D27 | always | open |

## Regression Assessment

- Regression scope: X1 and the scenario D checks D4, D23, D27 that share clearing_action_admissible and its placeholder filter; the executable helper's one-placeholder assertion; bundled-payload exact-match; the verifier exit code that FR-03 and the CI job read; every other repository test module.
- Regressions detected: None identified.
- Coverage of changed behavior: every branch of the new policy-exception row and of the awaiting_policy_exception exemption predicate is reached by the unit module and, for the emitted action, by the end-to-end script; the gate and release exemptions by unit cases; the rollback exemption and row by verifier D4, D23, D27 (all pass); full suite 787 of 787 tests ran, 29/31 modules passed, failures being the 3 known test_demo_capture EndToEndEditTestCase ffmpeg cases and one test_gate_rollback setUp PermissionError on os.replace in the host temp directory, which re-run alone with temp on D: passed 34/34 and does not import the changed file.
- Untested areas: automated execution of cmd_policy_exception (DF-001; executed here manually only); a rollback case in the added module (DF-002); the filled-role guard against a non-empty envelope owner list end to end (the induced envelope lists none; unit-tested only); the CI ubuntu and windows runners; Python versions other than 3.14.0.

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: a later change to cmd_policy_exception's guards or to the builder's emitted arguments could diverge from the admissibility row without any automated check executing the command (DF-001); the rollback row's exemption could change without a unit case naming it (DF-002); the CI job result is unobserved and is not evidence (implementation risk R-002).
- Monitoring required: the recovery verifier job on the default branch observed green first-hand; FR-03 rows in later proposals recording pass; any X1 or D4, D23, D27 output listing an inadmissible envelope.

## Verdict

- Decision: fail
- Rationale: the Stage 8 row with no open critical or high defect and at least one not-met criterion yields fail; AC-007 and AC-009 are not met as written, while the fixed behaviour itself is confirmed by AC-001 to AC-006 and AC-008; on the carried end-to-end question, the hermetic table test plus the analysis's earlier executed run does not satisfy AC-009, because the criterion asks for a scenario added that executes the action.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that omn-dev-2-reviewer, deciding the Verification Gate under producer exclusion, not approve on this report; recommended route is DF-001 and DF-002 to omn-dev-1-implement for the two missing regression cases (a test under tests/ leaves the verifier's 74-check total unchanged) and a retest here, unless omn-tech-lead formally accepts their risk (Q-001).

## Open Questions

- Q-001: Are DF-001 and DF-002 to be fixed by omn-dev-1-implement before closure, or is their risk formally accepted against the Validation Plan the Triage Gate approved? Routed to omn-tech-lead.
- Q-002: Is the CI recovery verifier job green on ubuntu and windows runners for this change? Not observable in this phase; routed to omn-orchestrator.
