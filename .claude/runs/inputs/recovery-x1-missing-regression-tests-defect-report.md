# Defect Report — the X1 policy-exception fix lacks two of its planned regression tests

## Summary

Run `run-e7bf0d73027a` (`/bugfix`, defect `runs/inputs/recovery-x1-policy-exception-defect-report.md`)
fixed `runtime/verify_recovery.py` so that X1 judges the runtime's `policy-exception` clearing
action admissible. The fix was confirmed by QA: `verify_recovery.py` reports 74/74 and the new module
`tests/test_clearing_action_admissibility.py` passes 16/16. QA's validation report nevertheless
returned `fail` because the root-cause Validation Plan approved at that run's Triage Gate called for
two regression cases that do not exist. The Verification Gate was rejected with these as the
outstanding defects. The runtime refused to roll that run back to `fix-implementation` because its
Fix Gate is already approved, so the missing tests are carried by this separate run.

## Observed behaviour

- DF-001 (medium, always): no automated test or verifier scenario executes
  `framework_runtime.py policy-exception` with role, decider and rationale filled in. Nothing shows,
  by execution, that the command as emitted by the clearing-action builder clears an
  `awaiting_policy_exception` block and resolves its failure envelope. The root-cause analysis
  answered this once by a manual run (its `E-018`), which is not repeatable coverage.
- DF-002 (medium, always): `tests/test_clearing_action_admissibility.py` carries an
  unchanged-gate case (`test_gate_action_keeps_its_exemption`) but no unchanged-rollback case. The
  rollback row of `clearing_action_admissible` is reached only by existing verifier checks D4, D23
  and D27.

Source: `runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md`
(criteria AC-007 and AC-009, defects DF-001 and DF-002) and the Verification Gate rationale in
`runs/run-e7bf0d73027a/state.json`.

## Expected behaviour

- An automated case, under `tests/` so the verifier's 74-check total is unchanged, drives a run to
  a state item blocked `awaiting_policy_exception`, executes the emitted `policy-exception` clearing
  action with only the human arguments filled, and asserts the block is cleared and the envelope is
  resolved. It also asserts the guards the runtime command applies, such as refusing the producer's
  own role.
- An unchanged-rollback case in `tests/test_clearing_action_admissibility.py` pins the rollback
  row's admissibility, including its `--decided-by` placeholder exemption, to the behaviour it had
  before the X1 fix.
- `python .claude/runtime/verify_recovery.py` still reports 74/74. The full suite passes apart from
  the known local ffmpeg failures in `test_demo_capture`.

## Reproduction

1. `python -m unittest tests.test_clearing_action_admissibility -v` lists no rollback case and no case
   that runs `cmd_policy_exception`.
2. `grep -rn "policy-exception\|cmd_policy_exception" tests/` finds no test that executes the command.

## Impact

- Severity: medium. Behaviour is correct today. Without these tests a regression in the
  `policy-exception` command or the rollback admissibility row would go unnoticed outside the verifier.
  The test gap also blocks closure of run `run-e7bf0d73027a`.
- Blast radius: `tests/` only. No runtime or verifier source change is expected. If writing the tests
  exposes a real defect, the root-cause analysis decides the scope.
