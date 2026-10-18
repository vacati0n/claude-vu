```yaml
bugAnalysis:
  analysisId: BA-run-5e9d799db687-triage-and-impact
  defectReference: runs/inputs/recovery-x1-missing-regression-tests-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/recovery-x1-missing-regression-tests-defect-report.md
    - type: validation-report
      reference: runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md
    - type: implementation-report
      reference: runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md
    - type: regression-targets
      reference: runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: environment-context
      reference: runs/run-e7bf0d73027a/state.json
    - type: code-context
      reference: tests/test_clearing_action_admissibility.py
    - type: code-context
      reference: runtime/verify_recovery.py
    - type: code-context
      reference: runtime/framework_runtime.py
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:7412953e071deb829255cfefaf1cc9e5
  contextDigest: sha256:121324ea4b3868f9df909d8a8060fd2c
```

## Metadata

- Bug ID: runs/inputs/recovery-x1-missing-regression-tests-defect-report.md
- Reporter: omn-qa (defects DF-001 and DF-002 of run-e7bf0d73027a), carried by the Verification Gate rejection of omn-dev-2-reviewer and written up in the supplied defect report
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: the regression suite delivered with the X1 policy-exception fix of run-e7bf0d73027a holds no automated case that executes the policy-exception runtime command and no unchanged-rollback admissibility case, so QA scored AC-009 and AC-007 not-met and the Verification Gate was rejected (`E-002`, `E-003`, `E-004`, `E-013`, `E-014`). DF-001 and DF-002 are analysed as one defect: they share one symptom, one origin in the same Validation Plan, and one rejection.
- Expected behavior: per the root-cause Validation Plan of run-e7bf0d73027a (`E-010`) and the supplied report (`E-001`), the repository test suite carries an end-to-end case that executes the emitted policy-exception action with only role, decider and rationale filled and shows the block cleared, the envelope resolved and the guards applied, plus an unchanged-rollback case beside the existing gate-exemption case, with the recovery verifier still at 74 checks.
- First observed date: 2026-10-18T03:52:13Z, the Verification Gate rejection of run-e7bf0d73027a (`E-014`); the gap itself has existed since fix-implementation of that run completed; ongoing.
- Affected environments: known affected: this worktree at HEAD 097e8f4 with the uncommitted run-e7bf0d73027a fix, Windows, Python 3.14.0 (`E-002`, `E-009`); known unaffected: none; not observed: the CI ubuntu and windows runners and any other Python version.

## Reproduction

- Preconditions: repository root of this worktree at HEAD 097e8f4, with the run-e7bf0d73027a working-tree changes present (modified runtime/verify_recovery.py and its bundled copy, untracked tests/test_clearing_action_admissibility.py) (`E-007`, `E-009`); Python 3.14.0; no other precondition varies the outcome, since the defect is the absence of code.
- Steps to reproduce: 1. from the repository root run python -m unittest tests.test_clearing_action_admissibility -v and observe 16 tests, OK, with no test name containing rollback; 2. run grep -rn "cmd_policy_exception" tests/ and observe no match (exit 1); 3. run grep -rn "policy-exception" tests/ and observe that every match is in the admissibility module and builds or inspects an action string rather than executing it; 4. run grep -rln "clearing_action_admissible" tests/ and observe that only the admissibility module reaches the table; 5. run grep -n "policy-exception" .claude/runtime/verify_recovery.py and observe that no verifier scenario executes the command.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below, `E-001` to `E-016`.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Defect report states DF-001 and DF-002 as always-present medium gaps, expected behaviour, two reproduction steps, and blast radius tests only; runtime refusal of rollback in run-e7bf0d73027a is stated, not shown | supplied defect-report, digest sha256:7412953e071deb829255cfefaf1cc9e5 | low |
| `E-002` | Executed: the admissibility module runs 16 tests, all OK, in 0.006s; the test names include test_gate_action_keeps_its_exemption and no rollback case | python -m unittest tests.test_clearing_action_admissibility -v, run in this phase | high |
| `E-003` | Executed: no file under tests/ names cmd_policy_exception (exit 1); all five policy-exception matches are in the admissibility module (docstring, action builder, string assertions, builder pin); the module contains no subprocess call and no runtime main invocation (confirmed absence) | grep -rn over tests/ and over the module, run in this phase | high |
| `E-004` | Executed: the only rollback reference in the admissibility module is the builder pin reading rollback_clearing_action source at line 183; no test method names rollback (confirmed absence) | grep -n rollback and grep of test method names in tests/test_clearing_action_admissibility.py, run in this phase | high |
| `E-005` | Executed: clearing_action_admissible is reached by exactly one module under tests/ | grep -rln clearing_action_admissible tests/, run in this phase | high |
| `E-006` | Read: verify_recovery.py names policy-exception only at an envelope assertion (line 567) and the admissibility rows (lines 660, 707); D4, D23, D27 and X1 call check_clearing_actions (lines 832, 1082, 1126, 1209); the executable helper at lines 593 to 601 fills only the --decided-by placeholder | .claude/runtime/verify_recovery.py, read and grepped in this phase | high |
| `E-007` | Read: the working-tree change to verify_recovery.py is 37 insertions and 2 deletions; it adds the policy-exception exemption predicate and row and leaves the rollback row and the rollback exemption set {--decided-by} unchanged | git diff of .claude/runtime/verify_recovery.py, run in this phase | high |
| `E-008` | Executed: the bundled verify_recovery.py is byte-identical to the runtime copy | cmp of .claude/runtime/verify_recovery.py and omn_agent/_bundled_payload/runtime/verify_recovery.py, run in this phase | high |
| `E-009` | Executed: HEAD is 097e8f4; tests/test_clearing_action_admissibility.py has no commit history (untracked) and verify_recovery.py is modified uncommitted; interpreter is Python 3.14.0 | git rev-parse, git log, git status, python --version, run in this phase | high |
| `E-010` | Read: the root-cause Validation Plan of run-e7bf0d73027a lists, among regression tests to add, unchanged gate and rollback cases and an end-to-end scenario that executes the action with role, decider and rationale filled, as its manual execution record did | runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md, Validation Plan | high |
| `E-011` | Read: the implementation report records deviation V-001 (no end-to-end scenario, because a new verifier check changes the 74-check total and the verifier helper allows only --decided-by as placeholder; escalated to omn-qa) and records no deviation for the absent rollback case (confirmed by grep) | runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md | high |
| `E-012` | Read: the Fix Gate was approved by omn-dev-2-reviewer with the end-to-end gap V-001 and the unpinned rollback row carried forward as conditions rather than required | runs/run-e7bf0d73027a/state.json, gates, Fix Gate rationale | high |
| `E-013` | Read: QA scored AC-007 and AC-009 not-met, opened DF-001 and DF-002 as medium, always, and returned fail; the report records that QA executed the command manually with the expected outcome | runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md | high |
| `E-014` | Read: Verification Gate rejected by omn-dev-2-reviewer naming DF-001 and DF-002 with no risk accepted; gate item failed, closure-and-communication blocked awaiting_recovery_task; rejection event at 2026-10-18T03:52:13Z | runs/run-e7bf0d73027a/state.json and events.jsonl | high |
| `E-015` | Read: cmd_policy_exception replays on a terminal item, refuses a non-blocked item and any blocked_reason other than awaiting_policy_exception, refuses a role the envelope does not list, and refuses the producer's own role | .claude/runtime/framework_runtime.py lines 4915 to 5001 | high |
| `E-016` | Reported, not executed in this phase: the emitted policy-exception action exits 0, moves the item blocked to pending and resolves the envelope; verify_recovery.py reports 74/74; D4, D23, D27 pass; the full suite passes apart from test_demo_capture | root-cause manual-execution record, implementation report T-003, QA validation report, Fix Gate rationale of run-e7bf0d73027a | low |

## Impact Assessment

- User impact: framework contributors and operators of run-e7bf0d73027a; that run cannot reach closure while the Verification Gate stands rejected (`E-014`); no runtime user sees wrong behaviour today, which rests on reported execution only (`E-016`).
- Business impact: no business impact statement was supplied; severity rests on technical impact alone, and the question is routed to omn-product-owner as `Q-003`.
- Technical impact: a regression in the policy-exception command's guards or arguments (`E-015`), or in the rollback row's placeholder exemption, would pass every test under tests/ undetected (`E-003`, `E-004`, `E-005`); the rollback row stays reachable only through verifier checks D4, D23, D27 (`E-006`); no correctness, data or security consequence is observed. Severity medium: a secondary path (regression detection) is absent and a workflow path (closure of run-e7bf0d73027a) is blocked, with acceptable workarounds in the verifier checks and in a formal risk decision.
- Blast radius: the repository test suite (admissibility module); the runtime policy-exception command surface left without execution coverage; the verifier admissibility table's rollback and policy-exception rows and their bundled-payload copy, which share the same function (`E-006`, `E-008`); the run record and closure of run-e7bf0d73027a; the uncommitted working-tree state the new tests must build on (`E-009`); no persisted bad data was written, since the rejected gate in run-e7bf0d73027a is a correct record.

## Root Cause Analysis

- Root cause statement: no step between the root-cause Validation Plan and the Fix Gate traced each planned regression case to a delivered test, so the unchanged-rollback case was dropped without being recorded and the end-to-end case was deferred on a verifier 74-check constraint that a case in the test suite does not touch, and the Fix Gate carried both gaps forward instead of holding them.
- Why detection failed earlier: the implementation report's deviation table, the one record mapping plan items to delivered work, captured V-001 but not the rollback omission (`E-011`), and the Fix Gate review saw both gaps and carried them as conditions rather than rejecting (`E-012`); no check observed in this run's evidence requires item-by-item Validation Plan tracing before the Fix Gate, and whether one should exist is `Q-001`.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Plan sets two targets | The root-cause Validation Plan required an unchanged-rollback case and an end-to-end case that executes the policy-exception action with role, decider and rationale filled | `E-010` | high |
| `C-002` | End-to-end case deferred on a misplaced constraint | Fix-implementation read the 74-check verifier total and the single-placeholder verifier helper as excluding the end-to-end case, did not place it in the test suite where the total is unaffected, and escalated it as V-001 | `E-011`, `E-006` | high |
| `C-003` | Rollback case dropped unrecorded | Fix-implementation added a gate-exemption case but no rollback case and recorded no deviation for it | `E-011`, `E-004`, `E-002` | high |
| `C-004` | Fix Gate carries both gaps | The Fix Gate was approved with both gaps carried forward as conditions, so no phase before QA required them | `E-012` | high |
| `C-005` | Coverage gap in the delivered suite | No test executes cmd_policy_exception and no test pins the rollback row; only verifier checks D4, D23, D27 reach that row | `E-002`, `E-003`, `E-004`, `E-005`, `E-006` | high |
| `C-006` | Observed symptom | QA scored AC-007 and AC-009 not-met and the Verification Gate was rejected, leaving run-e7bf0d73027a unable to close | `E-013`, `E-014` | high |

Alternatives tested: the cases exist elsewhere and QA missed them, eliminated by `E-003`, `E-005`, `E-006`; the gap was a formally accepted risk rather than a defect, eliminated by `E-014`; the rollback row's behaviour itself changed under the X1 fix, eliminated by `E-007`. Whether the untested command behaviour is itself correct rests on `E-016` alone and is `Q-002`.

## Fix Strategy

- Proposed fix: the repository test suite must gain (a) an end-to-end case that drives an isolated run to a state item blocked awaiting_policy_exception, executes the action as the clearing-action builder emits it with only role, decider and rationale filled, and asserts the item returns to pending, the envelope is resolved and the decision is recorded, plus refusal of the producer's own role and of an unlisted role (`E-015`); and (b) an unchanged-rollback case beside the gate-exemption case that pins the rollback row's admissibility, including its --decided-by exemption and the absence of an --owner-role exemption, to its pre-fix behaviour (`E-007`); the verifier total stays 74 and no runtime or verifier source changes; conditional on `Q-002`, a real defect exposed by writing these cases returns to root-cause analysis rather than being fixed inside a test.
- Alternative options: a new verifier scenario instead of a suite case covers the same path but changes the 74-check total, needs the single-placeholder helper widened, and touches bundled-payload parity (`E-006`, `E-008`); an in-process call of the command with constructed arguments is lighter but does not prove the emitted action string parses and runs; a formal risk acceptance by omn-tech-lead closes the gate without tests and is that role's decision, not a fix.
- Regression risk: low
- Regression scope: the run tree under .claude/runs, which the runtime writes to and which an end-to-end case shares unless it runs in an isolated copy (the verifier's run-f94564cb61ce restore duty is the precedent); the admissibility module's existing 16 cases, shared fixtures and builder pin; the verifier's 74-check total and executable helper, connected only if the case is placed in the verifier; the bundled-payload parity test, connected through the shared verify_recovery.py copy; the full suite's run time and temp-directory use, connected through the TEMP path the runtime uses.

## Validation Plan

- Verification steps: rerun the five reproduction steps and observe a rollback case listed and a case that executes cmd_policy_exception; confirm the condition, not only the symptom, by mapping each regression item of the root-cause Validation Plan (`E-010`) to a named passing test with none unmapped; show the end-to-end case fails on a temporary copy where a command guard is inverted and the rollback case fails on a copy where the rollback exemption set is widened; run python .claude/runtime/verify_recovery.py and observe 74/74 with run-f94564cb61ce unchanged afterwards; run the full suite and observe only the known test_demo_capture failures; observe git status shows no residue under .claude/runs.
- Regression tests added: the end-to-end policy-exception execution case with its two guard refusals, and the unchanged-rollback admissibility case, as stated in the Proposed fix.
- Monitoring signals after release: the CI unit and recovery-verifier jobs observed first-hand as green on the default branch; the admissibility module's test count rising from 16; any Validation Plan regression item with no mapped test at a Fix Gate indicates recurrence.

## Closure

- Resolution summary: None identified; the defect is open and closure is a gate decision made elsewhere.
- Linked PR and release: None identified; pending fix-implementation of this run.
- Prevention actions: trace every Validation Plan regression item to a delivered test or a recorded deviation before the Fix Gate is requested, routed as `Q-001`; place end-to-end cases in the test suite when a verifier check total is fixed.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Should the framework require item-by-item tracing of Validation Plan regression cases to delivered tests before the Fix Gate; answered by a design decision on the implement and Fix Gate contracts | no | architect | `C-002`, `C-003`, `C-004` |
| `Q-002` | Is the untested behaviour correct first-hand: execute the emitted policy-exception action and verify_recovery.py in this run, since `E-016` is reported only | no | omn-dev-1-bug-analyst | `C-005` |
| `Q-003` | What is the business impact of the blocked closure and the coverage gap; answered by a business impact statement | no | omn-product-owner | none |
| `Q-004` | The run-e7bf0d73027a fix and its test module are uncommitted (`E-009`); who sequences their commit relative to the tests this run adds | no | omn-orchestrator | none |
