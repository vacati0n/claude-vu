# Defect Report — A rejected gate has no executable rollback: the run stalls forever

## Summary

The runtime classifies a gate rejection as a `rollback` (failure-classification matrix row
"Gate rejection | gate state | rollback | blocker marked unresolved",
`config/execution-engine.md`; `runtime/recovery_policy.py` lines 104-109), and every workflow
specification's Failure Recovery section promises the corresponding return — for example
`workflows/implement-feature.md`: "Return to implementation stage when review or QA fails."
Nothing executes that rollback. After a rejection the gate work item is `failed`, the phase it
closes stays `completed`, every downstream phase is blocked by guard `G4-GATE` with reason
`awaiting_recovery_task`, and no runtime command can move any of them. The run can never
complete, and the correction the rejection asked for has no phase to land in.

## Observed behaviour (reproduced on run `run-4c51600606df`, 2026-09-06T09:05:36Z)

1. `gate --gate "Review Gate" --decision reject --owner-role omn-qa ...` recorded the decision.
   `record_gate_decision` emitted failure envelope `FE-run-4c51600606df-Review Gate-02`
   (class `gate-rejection`, action `rollback`, resulting status `failed`) whose decision options
   read "rebuild the rejected evidence and re-submit it to the gate / approve an exception and
   proceed / abort the run", and whose `clear by` line names
   `release --phase "Review Gate" --reason tool_failure`.
2. Resulting work-item states: `implementation` = `completed` (attempt 1); `quality-review` =
   `completed` (attempt 1); `gate:Review Gate` = `failed`; `gate:Verification Gate` =
   `blocked` awaiting_human_decision; `documentation-and-release-handoff` = `blocked`,
   blocked_by `guard`, reason `awaiting_recovery_task`.
3. `dispatch --phase implementation` and `dispatch --phase quality-review` both print
   `REPLAY ... is already completed; dispatch suppressed.`
4. `release --phase "Review Gate"` cannot apply: `cmd_release` acts only on items in
   `ACTIVE_STATUSES` ({leased, running}) or on `blocked` items with a non-guard `blocked_by`;
   a `failed` gate is neither, so it prints `NOTHING TO RELEASE`.
5. `next` reports `NEXT: record a decision for Verification Gate` and nothing dispatchable.
6. `runtime/state_engine.py` `TRANSITIONS`: the `state` table has no transition out of
   `completed`; the `gate` table has no transition out of `failed`. Guard `G4-GATE`
   (`runtime/framework_runtime.py`, around line 1785) returns `block` / `awaiting_recovery_task`
   for as long as any closing gate's decision is `rejected`. The three facts together make the
   rejection terminal for forward progress.
7. `omn_agent/fix_comments.py` is built on the contrary assumption: its module docstring says
   the rejection "is classified as a rollback and the re-dispatched phase carries the feedback
   forward", and `_dispatch_fix` fails with "the gate is rejected but no phase became
   dispatchable" — which is now the only possible outcome. The `omn-agent pr fix-comments`
   round therefore cannot complete against this runtime.

## Expected behaviour (the contract)

- `config/execution-engine.md`: a gate rejection is a `rollback`; the blocker is marked
  unresolved and the run returns to the last accepted state.
- Every workflow's Failure Recovery section: review or verification failure returns the work
  to the implementing phase.
- `runtime/README.md`: "Every command is safe to repeat" and a blocked transition always names
  "the command that clears it". The envelope names `release`, which does nothing here.
- The human-block invariants must survive the fix: a rejected gate must still hold the run
  until a human with a gate-owner role authorises the rollback (the envelope already asks
  for `rollback-authorisation`); the rejection and its rationale stay in the ledger and the
  event stream as immutable evidence; the Producer Exclusion Rule and `record_gate_decision`'s
  decision semantics are unchanged; `runner._require_approval` is untouched.

## Impact

- Severity: high. Every gate rejection, on every workflow, strands the run. The only ways
  forward are a new run over a new input (repeating every completed phase) or hand-editing
  `state.json`, which the framework forbids as modification of committed run evidence.
- Blast radius: `runtime/state_engine.py` (transition tables), `runtime/framework_runtime.py`
  (`record_gate_decision`'s rejection branch, `cmd_release`, `cmd_dispatch` replay check,
  guard `G4-GATE`, `next`), `runtime/recovery_policy.py` (rollback options), and the
  consumer `omn_agent/fix_comments.py`. Verifier `verify_multi_phase.py` check `M12` pins
  "every committed artifact is present and unchanged since it was committed", so re-running a
  phase must produce a new attempt's artifact without rewriting the committed one; the fix
  must state how it keeps M12 true (attempt-scoped artifact paths, or an explicit supersession
  record).
- Concrete blocked work: `run-4c51600606df` (ticket CKA-06 in the adoption backlog under
  `docs/`) has its corrections applied on the tree and cannot be re-reviewed or closed.

## Reproduction

Plan any run, complete a phase whose gate has two owners, and record `--decision reject`
from the non-producing owner. Then run `next`, `dispatch --phase <producing phase>`, and
`release --phase "<gate name>"`. All three leave the run where it was.

## Constraints on the fix

- Framework-internal, class `defect-repair`, routed `/bugfix` → `fix-bug` per
  `config/self-hosting-profile.md`; a change proposal must account for the run.
- Additive to the human-block model: no path may let a rejected gate be bypassed without a
  recorded human authorisation from a gate-owner role; no auto-approval; no change to
  `record_gate_decision`'s decision values or to producer exclusion.
- Every artifact this run produces must avoid the vendor substring the artifact validators
  reject; write framework paths without the leading dot-directory prefix.
- `tests/` green (baseline on this tree: 404 tests OK, of which 48 belong to the in-flight
  CKA-06 change and 14 to run-79630cb5274d); all `verify_*.py` PROVEN, `verify_recovery.py`
  and `verify_multi_phase.py` especially, since both encode the recovery and immutability
  contracts this fix touches.
