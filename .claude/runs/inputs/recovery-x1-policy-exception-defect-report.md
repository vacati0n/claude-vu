# Defect Report — verify_recovery X1 rejects the runtime's policy-exception clearing action

## Summary

`python .claude/runtime/verify_recovery.py` reports 73/74 checks passed, NOT PROVEN, on `main`
since 097e8f4, and the repository CI (`.github/workflows/verify.yml`) shows the job red on every
pull request. The failing check is `X1`, "every open envelope's clearing action is admissible for
its work item's type and status, or names no command". Release checklist item `FR-03` has
recorded this failure as pre-existing in FC-021 and FC-022 (`O-015`).

## Observed behaviour

```
[FAIL] X1    every open envelope's clearing action is admissible for its work item's type and status, or names no command
        inadmissible: ["FE-run-d8870619db82-execution-planning-01: placeholder argument ['<role>', '<who>', '<text>'] in ['python', '.claude/runtime/framework_runtime.py', 'policy-exception', '--run-id', 'run-d8870619db82', '--phase', 'execution-planning', '--owner-role', '<role>', '--decided-by', '<who>', '--rationale', '<text>']"]
```

`run-d8870619db82` is a run the verifier itself injects and removes; the run id differs on each
invocation, the envelope shape does not.

## Mechanism (observed by the operator against the source)

- `runtime/framework_runtime.py`, the clearing-action builder for `blocked_reason ==
  "awaiting_policy_exception"`, emits `framework_runtime.py policy-exception --run-id <id> --phase
  <phase> --owner-role <role> --decided-by <who> --rationale <text>`. The comment there states the
  role, decider and rationale are the human's judgement and stay placeholders, exactly as for the
  gate-decision action.
- `cmd_policy_exception` exists and clears `awaiting_policy_exception` blocks; its docstring records
  that before it existed the block was terminal on the supported surface.
- `runtime/verify_recovery.py`, `clearing_action_admissible`, holds the admissibility table. It
  knows `release`, `gate`, `rollback` and prose actions. Its set of argument flags allowed to stay
  placeholders is defined only for `gate` and `rollback`, and it has no row for `policy-exception`,
  so any placeholder is reported as inadmissible and an unknown subcommand would be rejected too.

Which side is wrong is for the root cause analysis to establish; the operator's reading is that
the runtime action is the intended contract and the verifier's table was not updated when the
`policy-exception` command was added.

## Expected behaviour

An open envelope whose clearing action is `policy-exception` on a state work item blocked
`awaiting_policy_exception` is judged admissible, with its human-judgement arguments allowed to
stay placeholders, and inadmissible otherwise. `verify_recovery.py` reports 74/74.

## Reproduction

1. `python .claude/runtime/verify_recovery.py` from the repository root on `main`.
2. Observe `X1` FAIL as above and the verdict `73/74 checks passed -- NOT PROVEN`.
3. Restore `.claude/runs/run-f94564cb61ce/` with `git restore` afterwards: the verifier rewrites it.

## Impact

- Severity: medium. No run is mis-executed, but the recovery verifier — the framework's authority
  on current recovery behaviour (GD-001 item 5) — cannot prove recovery, `FR-03` fails for every
  framework change, and CI is red on every pull request.
- Blast radius: `runtime/verify_recovery.py` (or the clearing-action builder, if the analysis
  finds the runtime at fault).
