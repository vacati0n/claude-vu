# Defect Report — the `release` clearing action carries an unfillable `--detail` placeholder

## Summary

`clearing_action` in `runtime/framework_runtime.py` builds one `release` command and uses it in
two places. It is the whole clearing action for a work item blocked `awaiting_recovery_task` that
no guard raised. It is also the optional reclaim the retry-class prose offers ("To reclaim it
sooner: ..."). The command ends `--detail <what happened>`. That text is free prose in angle
brackets, unquoted. A shell reads `<` as an input redirect, so the action cannot be run as
written. The X1 check of `verify_recovery.py`, since `FC-027`, finds the placeholder by
`placeholders` and rejects any open envelope that carries this action. `--detail` is not one of
the flags a human must fill: `release` already defaults it ("adapter did not report a result").

This was recorded as open item `O-002` of `FC-027` (owner architect).

## Observed behaviour

- For a state work item blocked `awaiting_recovery_task` without guard `G3-PREDECESSOR`,
  `clearing_action` returns
  `python .claude/runtime/framework_runtime.py release --run-id <run> --phase <phase> --reason tool_failure --detail <what happened>`.
- `shlex.split` of that action yields `<what` and `happened>` as two arguments, and
  `verify_recovery.placeholders` returns `['<what happened>']`.
- A POSIX shell given the action fails on the redirect, because no file `what` exists, and
  `release` never runs.
- The retry-class clearing action embeds the same command after "To reclaim it sooner:".

## Expected behaviour

- The emitted `release` action parses as written and carries no placeholder that
  `verify_recovery.placeholders` recognises. Either `--detail` is dropped, so `release` uses its
  own default, or it is filled with a quoted default.
- The retry-class prose names the same runnable command.
- `verify_recovery.py` X1 accepts an envelope that carries the action. Every other verifier still
  passes.

## Reproduction

1. In Python, with `.claude/runtime` on the path, build a `clearing_action` for a state item
   blocked `awaiting_recovery_task` with a non-retry classification and no guard.
2. `verify_recovery.placeholders(shlex.split(action))` returns `['<what happened>']`.

## Impact

- Severity: medium. The prescribed recovery for a non-guard `awaiting_recovery_task` block cannot
  be executed verbatim. With the `FC-027` verifier, any run that leaves such an envelope open
  fails X1.
- Blast radius: the clearing action text in `runtime/framework_runtime.py`, which is runtime
  behaviour. No state transition, `release` semantics or verifier rule is expected to change.
