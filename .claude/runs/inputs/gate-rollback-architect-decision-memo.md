# Architect decision memo — rollback re-entry after a gate rejection

Operator-supplied input to run `run-3e6f6a248b99` (fix-bug), phases `root-cause-analysis` and
`fix-implementation`. Produced by the `architect` role on 2026-09-06 as a consultation, because the
fix-bug workflow has no design phase; the Triage Gate made recording this answer to the bug
analysis's `Q-001` a condition of root-cause-analysis. Status: Proposed. Acceptance rests with
`omn-tech-lead` as the non-producing owner. Every current-state claim traces to
`runtime/state_engine.py`, `runtime/framework_runtime.py`, `runtime/recovery_policy.py`,
`runtime/verify_multi_phase.py`, `runtime/verify_recovery.py`, `config/execution-engine.md`,
`config/runtime.md`, `omn_agent/fix_comments.py`, and the stranded run `runs/run-4c51600606df`.

## Decision

**(1) Option (a): supersession in the state model.** An authorised rollback moves each target
phase `completed -> pending` under trigger `superseded`, keeping the item's idempotency key: the
payload digest keeps using the phase-canonical artifact path, and the rejection rides in the
envelope as `prior_rejection` beside the existing `prior_validation`, exactly as Run A preserves
the key across attempts (A12). Attempt n+1 writes to
`states/<phase>/artifacts/attempt-<n+1>/<artifact>` (same filename, so validator lookup,
`permitted_write`, and the conditional glob `<stem>-*.md` are unaffected); attempt 1 stays
byte-identical at its recorded path. The prior `completion` block moves unmodified into an
append-only `supersessions` list on the item with the authorisation id, and the attempt's
invocation/result/state-ledger/validation files are copied to `states/<phase>/attempts/<n>/`.
Item-level `artifact_path` and `completion` follow the current attempt, so `upstream_inputs`,
auto-approval, the completion package and final report read the superseding artifact unchanged;
the completion package gains a Superseded Attempts table and M12 iterates `supersessions` too.
The state engine refuses the `superseded` pair unless the caller supplies the supersession
record, so the engine, not only the command, enforces authorised re-entry. The re-entered attempt
**is charged** (it produced a gate-judged result); authorisation is refused when
`attempts_charged >= max_attempts`, which is the "repeated gate failure without deterministic
remediation" escalation trigger.

**(2) Target rule.** The authoriser names `--target <phase>`; the runtime validates it is the
gate's `closes_state` or a completed hard-predecessor ancestor of it (default `closes_state`).
Rationale text is never parsed for an owner. Every completed phase from target through
`closes_state` is superseded in the same authorisation (quality-review assesses the report being
rebuilt, so it cannot stand), each carrying the shared authorisation id. An undecided blocked
gate (Verification Gate) returns to pending via the existing `blocker_cleared`. One scheduler
correction is required: `refresh` leaves a guard-raised block in place when its guards drop to
`wait`, so phase 6 would stay on a stale `awaiting_recovery_task`; it must transition
`blocked -> pending` (existing pair) and resolve the envelope in that case.

**(3) Gate.** `failed -> pending` under `rollback_authorised`, same work item (a fresh item
breaks `gates_for`, matrix parsing, `_awaiting_gate`, and gate-name keying). The gate record
gains append-only `decision_history`; the rejected decision, role, decider, rationale and
timestamp are appended there and `decision` returns to null. Transition seq 33, its event, and
envelope FE-...-Review Gate-02 are untouched; the envelope is marked resolved naming the
authorisation. Set the gate item's `failure_class` to `gate-rejection` at rejection (settles
Q-002) and clear it on re-arm.

**(4) Authorisation surface.** New subcommand
`rollback --run-id --gate <name> --target <phase> --owner-role --decided-by --rationale`.
Preconditions: gate item `failed` with decision `rejected`; role listed and outside
`producer_aliases(producer_agent)` (factor those two checks out of `cmd_gate` and reuse); valid
target; budget available for every phase to supersede. `gate` decision values,
`record_gate_decision`, and `release` are unchanged. `clearing_action` becomes class-aware: for
`gate-rejection` on the gate item and on any G4-blocked successor it names this command with the
gate (the G4 verdict carries the gate name as a structured field). The `gate-rejection` option
list drops "approve an exception" until an executor exists. No bypass: G4 clears only on
`approved`, and after re-arm the gate is undecided until a listed non-producer decides again.

**(5) Stranded state.** No migration utility. `run-4c51600606df` already holds exactly the shape
`rollback` accepts; `next` derives clearing actions from live state, so after the fix it prints
the rollback command. The stale `release` text in the two open envelopes stays as evidence
(append-only ledger). Operator action:
`rollback --gate "Review Gate" --target implementation --owner-role omn-qa`; implementation
becomes pending/eligible, attempt 2 carries the nine corrections as `prior_rejection`, the
report lands under `artifacts/attempt-2/`.

**(6) Consumer contract.** After `rollback`, `status --json` shows the target step
`status: pending, eligible: true, attempt: 1` plus a new
`rollback: {gate, authorisation_id, superseded_attempt}` block; intermediate steps
`pending, eligible: false`; the re-armed gate `status: pending, decision: null, owner_roles: [...]`.
`_dispatchable_step` is unchanged. `_start_round` must issue `gate ... reject` then `rollback`
with the same role and the task's fix phase as `--target`; the fiat stub is replaced by this shape.

## Options considered

| Option | Hard constraints (M12, M13, M14, human-block, producer exclusion, budget) | Impact surface | Outcome |
|---|---|---|---|
| O-001 (a) supersession transition + attempt-scoped artifacts | All satisfied; M13 restated as "terminal except one engine-checked authorised pair" | state engine: 2 table entries, 1 field; runtime: `rollback`, `clearing_action`, `refresh` wait-fix, G4 verdict field; verifiers; consumer | **Selected**: smallest surface; every status change is a logged transition |
| O-002 (b) recovery work type | M12/M14 satisfiable; literal M13 kept; but G6, G3/G5 and successors key on the phase item's `completion`, so the recovery item must write back into a terminal item with no transition record | new `WORK_TYPE` through `new_work_item`, ordering, projection, `next`, `dispatch`, `complete`, aggregator, status view, consumer | Rejected: larger surface, hidden mutation of a terminal item |
| O-003 (c) truthful clearing action only | Leaves C-003 unmet | `clearing_action`, options, `next` | Rejected as the fix; absorbed into O-001 |
| O-004 (d) archive-and-new-run | Violates matrix, runtime rollback rule, eight workflow specs (E-013, E-014) | config + workflows + consumer | Eliminated on contract |
| Gate re-arm: same item vs fresh item | Both satisfy | Fresh item breaks gate-name keying | Same item selected |
| Command: `gate --decision rollback` / `release --reason rollback-authorised` / new `rollback` | First changes decision values (forbidden); second needs a non-canonical reason code and conflates lease reclaim with authorisation | - | New subcommand selected |

## Tradeoffs accepted

- `completed` is terminal except for one authorised, logged pair; `project_run_status`,
  `finished`, and the aggregation signature are status-vector functions and follow without change.
- Attempt 1 keeps the canonical path; later attempts live in attempt directories. Readers use
  item fields, never the canonical path.
- Per-attempt files in the phase directory are still overwritten on redispatch, as retries do
  today; the snapshot copy is the provenance record.
- A rollback re-entry spends the same budget as a retry; a third rejection routes to abort or a
  new run.
- Two human decisions (reject, then authorise) instead of one; the consumer issues both.
- Q-003 (`run_completed` fires on all-completed before final gate decisions) is not fixed here;
  supersession after `run_completed` becomes possible and is a recorded risk.

## Transitions added

```
state: (COMPLETED, PENDING): "superseded"
gate:  (FAILED, PENDING):    "rollback_authorised"
```

Both recorded with canonical reason code `enqueued`; the reason-code set is unchanged. Nothing
else. State `failed` remains terminal.

## Invariants preserved

- **M12**: attempt 1 is never rewritten; the check iterates `completion` and every
  `supersessions[].completion`.
- **M13**: the two pairs above are the only new legal transitions; the engine additionally
  refuses `superseded` without a supersession record.
- **M14**: re-entry lands in `pending`; a second `dispatch` while active with the same payload,
  or after attempt 2 completes, is replay-suppressed by the existing checks.
- **Human block**: G4 clears only on `approved`; re-arm sets `decision` null, so the successor
  waits for a fresh listed-owner decision.
- **Producer exclusion**: `rollback` applies the same role and alias checks as `gate`.
- **Retry budget**: re-entered attempts are charged; `rollback` refuses when the budget is spent.

## Verification the fix must add

- **`verify_recovery.py` Run D**: complete `execution-planning`, reject Planning Gate as
  `omn-tech-lead`; assert gate `failed`, class `gate-rejection`, successor blocked; execute the
  envelope's `clearing_action` verbatim and assert exit 0; assert phase `pending`/eligible, key
  unchanged, `supersessions[0]` digest matches the untouched file, gate `pending` with
  `decision_history[0] == rejected`, seq and FE-02 preserved and resolved; dispatch carries
  `prior_rejection`; second dispatch replays; attempt 2 completes at the attempt path with
  `attempts_charged == 2`; gate re-blocks `awaiting_human_decision`. Negatives: producer role,
  unlisted role, approved gate, exhausted budget each refused with no store change.
- **M13 extension**: probe every `(from, to)` from `completed` and `failed` in both tables;
  exactly the two pairs pass, and `superseded` without a record is refused.
- **Clearing-action executability**: for every envelope, match the command's
  `(subcommand, work_type, status)` against an admissibility table; for Run D, execute it.
- Extend M12 over `supersessions`; replace the stub rejected stage in
  `tests/test_fix_comments.py` and `tests/test_update.py` with the point-6 shape.
