# Defect Report — X1 admits a clearing action that carries a multi-word placeholder

## Summary

`runtime/verify_recovery.py` check X1 judges every open failure envelope's clearing action through
`clearing_action_admissible`. A placeholder in angle brackets is not executable, so the table rejects
any placeholder outside the human-judgement flags of the row it applies to. The detection only
recognises a placeholder that `shlex` leaves as one argument beginning with `<` and ending with `>`.
A placeholder of more than one word, such as `<fill in owner name>`, splits into `<fill`, `in`,
`owner` and `name>`. None of those both starts with `<` and ends with `>`, so the action passes as
admissible. An independent review found the gap after the X1 policy-exception repair (`FC-024`,
`FC-025`). The same detection is used by `executable()`, which turns an emitted action into the argv
the verifier runs, so that guard has the same gap.

## Observed behaviour

With a state work item `execution-planning` leased, `clearing_action_admissible` returns:

| Clearing action tail | Verdict |
|---|---|
| `release --run-id run-x --phase execution-planning --reason <owner>` | inadmissible: `placeholder argument ['<owner>']` |
| `release --run-id run-x --phase execution-planning --reason <fill in owner name>` | **admissible** |
| `release --run-id run-x --phase execution-planning --reason tool_failure` | admissible |

## Expected behaviour

- A clearing action that carries a placeholder in any form is inadmissible, unless the placeholder is
  one whole argument following a flag the row exempts as human judgement. That covers one word, several
  words, a placeholder glued to other text, and an unterminated `<`.
- `executable()` refuses the same forms.
- A valid action without a placeholder stays admissible, and every exemption the table grants today
  (gate, rollback `--decided-by`, policy-exception on an item blocked `awaiting_policy_exception`)
  keeps its verdict.
- Every committed envelope under `.claude/runs/` keeps its verdict, and `verify_recovery.py` still
  proves out in full. Committed run evidence is not edited.
- Regression tests in `tests/test_clearing_action_admissibility.py` pin single-word and multi-word
  placeholders as inadmissible and a valid action as admissible.

## Reproduction

1. Build a synthetic state with `execution-planning` leased and patch `verify_recovery.load_state` to
   return it.
2. Call `verify_recovery.clearing_action_admissible("run-x", {"clearing_action": action})` for each
   action in the table above.
3. The multi-word placeholder is judged admissible.

## Impact

- Severity: medium. No committed or induced envelope carries a multi-word placeholder today, so no
  verdict is wrong yet. But X1 is the proof that every emitted clearing action can be run as written,
  and a builder change that emitted `<fill in owner name>` would ship with X1 still passing.
- Blast radius: `runtime/verify_recovery.py` (placeholder detection shared by
  `clearing_action_admissible` and `executable`) and its unit tests. No runtime behaviour changes.
