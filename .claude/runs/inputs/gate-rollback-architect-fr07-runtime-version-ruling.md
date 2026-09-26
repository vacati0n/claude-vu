# Architect ruling — FR-07, `RUNTIME_VERSION` for run `run-3e6f6a248b99`

Operator-supplied record for run `run-3e6f6a248b99` (fix-bug) and its proposal FC-013 (`O-017`).
Produced by the `architect` role on 2026-09-07 as a consultation, as owner of release-checklist item
`FR-07` (`validation/framework-release-checklist.md`). Applied verbatim by the session operator the
same day. Nothing else was executed or written by the architect.

## FR-07 RULING: move to 0.6.0

FR-07 read false for this run: `runtime/framework_runtime.py` line 123 still held `"0.5.0"` while
`runtime/state_engine.py` gained two legal transitions and `runtime/framework_runtime.py` gained a
new `rollback` subcommand, class-aware clearing actions, the `refresh` guard correction,
attempt-scoped artifact paths and snapshots, gate `decision_history`, and rollback surfacing in
`next`/`recovery` — all runtime behaviour changes, the first among FC-005..FC-012 where the "no
runtime module changed" reading fails. The prior 0.4.1 → 0.5.0 precedent (`runtime/README.md`,
Slice 5) bumped minor for a comparable bundle of new capability, while 0.4.1 itself was a narrow
patch for one bad default. This run adds a new subcommand plus new state-machine transitions —
additive capability, not a narrow fix — so it matches the minor-bump precedent even though the
workflow classed the run `defect-repair`; FR-07 asks whether runtime behaviour changed, not how
the run was classed.

## EDIT SET (applied by the operator, 2026-09-07)

- `runtime/framework_runtime.py:123` — `RUNTIME_VERSION = "0.6.0"`.
- `omn_agent/_bundled_payload/runtime/framework_runtime.py` — copied from the edited source;
  `cmp` identical.
- No README line names the literal value, so none was edited.
- Re-validation: `test_bundled_payload` 11 OK; `test_framework_runtime_render` 21 OK (its
  `"0.5.0"` literals at lines 110/205/277 are fixture inputs, not asserted output);
  `test_gate_rollback` 34 OK. `test_gate_policy.py` and `test_gate_rollback.py` reference
  `fr.RUNTIME_VERSION` dynamically. No test asserts the literal old or new value.

## RECORD WORDING

"Runs recorded under runtime_version 0.5.0, including the stranded run-4c51600606df, remain valid
under that version; run-4c51600606df's attempt 2 dispatches under 0.6.0, and its closure record
must state it was opened at 0.5.0 and closed under 0.6.0, per the `close_legacy_run.py`
cross-version wording already implemented at line 183."
