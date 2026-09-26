# Architect rulings — regression-validation open questions Q-001, Q-002, Q-005

Operator-supplied input to run `run-3e6f6a248b99` (fix-bug), for the Verification Gate and
`closure-and-communication`. Produced by the `architect` role on 2026-09-07 as a consultation,
answering the open questions of the validation report
(`runs/run-3e6f6a248b99/states/regression-validation/artifacts/validation-report.md`). Nothing
was executed or written. Read against the decision memo and the two earlier rulings in
`runs/inputs/gate-rollback-architect-*.md`.

## Q-001: release — an active cone descendant is reclaimed, not left and not refused

An active cone descendant is already consuming evidence the rollback is about to rebuild, so
leaving it reproduces exactly the invariant violation `rollback_preconditions` already refuses for
standing approved gates: something completes and stands over evidence being rebuilt. Refusing the
whole authorisation is too broad: it lets an unrelated in-flight lease block the human-authorised
correction the operator is trying to make. The correct shape is to fold the active descendant into
`cmd_rollback` alongside the completed cone, but reclaim it through the same path `cmd_release`
already uses for worker loss — uncharged, retryable, no new transition — rather than through
`superseded` (it never reached `completed`, so it has no `supersessions` entry to move). This
keeps the engine surface minimal: no third transition, reuse of an existing one. The adapter may
still be running and report after the runtime-side lease is reclaimed; the existing
payload/lease-ownership check on `complete` handles that: once released, the item's bound payload
digest no longer matches the live lease, so a late report is refused as a stale completion, not
silently accepted. `next` must not offer that item's `complete` after release.

Disposition: a behaviour change beyond the accepted fix scope. No current workflow produces the
shape (successors of the closed phase are guard-blocked). Record as a follow-up correction with
this ruling as its specification; it does not block closure.

## Q-002: extend M6 to read supersession as traversal; add the rollback shape to the proof surface

GD-001 already commits M6 to evaluating the carried-forward baseline rather than live state; the
residual gap is that a delivery phase's `pending` status after an authorised rollback masks a real
historical completion. M6 should accept a delivery phase as traversed when its baseline status is
`COMPLETED`, `BLOCKED`, or its work item carries a non-empty `supersessions` list — the
append-only record is exactly the evidence M12 already treats as proof the phase once completed.
A multi-phase run carrying a rollback must be added as a named scenario (a Run E) in
`verify_multi_phase` / `verify_recovery`, since the fix now legitimately produces that shape and
it was only exercised in-process on copies.

Disposition: verifier follow-up; does not block closure. Until it lands, `verify_multi_phase.py`
reports M6 failing on any run mid-rollback (DF-002), which the closure record must state.

## Q-005: intended, not a defect — and it must be written down

`bind_payload`'s digest is keyed on the currently resolved agent version; that is pre-existing
dispatch semantics unrelated to rollback, and would produce a new key for any re-dispatch
(rollback-driven or an ordinary retry) whenever the bound agent's version moved in the interim.
The memo's key-preservation claim held only for the rollback transition itself (the superseded
item's last-bound key is left unchanged in the pending record) and was never a claim about
re-dispatch after the tree moves.

Operator instruction and closure record for `run-4c51600606df` must state, verbatim in
substance: "attempt 2's dispatch of implementation binds a new idempotency key because the
implementer agent resolves at 1.1.0 against 1.0.0 at attempt 1; this is expected `bind_payload`
behaviour keyed on agent version, not a rollback defect, and does not indicate lost work or a
replay-suppression failure — the item was pending, not terminal, at bind time."
