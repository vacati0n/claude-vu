# Architect confirmation — Q-006 and Q-007 of the root-cause analysis

Operator-supplied input to run `run-3e6f6a248b99` (fix-bug), for `fix-implementation` and the
Fix Gate. Produced by the `architect` role on 2026-09-06 as a consultation, answering the two
questions the root-cause analysis (`runs/run-3e6f6a248b99/states/root-cause-analysis/artifacts/bug-analysis.md`,
`Q-006`, `Q-007`) raised against the decision memo
(`runs/inputs/gate-rollback-architect-decision-memo.md`). Nothing was executed or written.

## Q-006: confirmed

The implementer must keep two distinct values where today only one exists. Verified in
`runtime/framework_runtime.py`'s dispatch path: `artifact_rel` (the canonical
`runs/<run>/states/<phase>/artifacts/<name>` path) is the single value fed both into
`payload_digest` (which fixes the idempotency key via `bind_payload`) and into
`expected_output_schema.artifact_path`, `permitted_writes`, and the state-ledger's `artifact_path`
written by `write_state_ledger`. `permitted_write` matches a declared side effect only against
`expected_output_schema.artifact_path`, `result_envelope_path`, the conditional globs, and
`constraints.permitted_writes` — never against the digest input. So for a superseded re-entry
(attempt >= 2) the implementer must compute an attempt-scoped path and use it everywhere those
three surfaces (envelope schema, permitted_writes, state-ledger artifact_path) are populated,
while `payload_digest` keeps using the unchanged canonical `artifact_rel`. Attempt 1 keeps both
identical, so nothing changes for the common case.

## Q-007: confirmed

The correction is not scoped to the successor phase alone. `refresh`'s "waiting" branch only
sets eligibility false and continues; it never transitions an item out of `BLOCKED`, and this
branch is reached identically for state and gate work items, since `evaluate_gate_guards`
returns `wait` (`G6-GATE-EVIDENCE`, `dependency_wait`) whenever the phase a gate closes reverts
from `completed` to `pending` under supersession. Meanwhile `next_action` returns the first gate
item with status `BLOCKED` with no check on the status of the phase it closes, and `cmd_gate`
refuses only when the item is terminal or not `BLOCKED` — neither checks `blocked_reason` or
evidence freshness. Left as the memo states it, a gate closing a phase being rebuilt stays
`BLOCKED`/`awaiting_human_decision` and is both offered by `next` and accepted by `gate`, letting
a decision land on superseded evidence. The fix must make `refresh` clear or re-route a
guard-raised block for **both work types** when guards fall to `wait`, and neither `next` nor
`gate` may offer or accept a decision on a gate whose closed evidence is being rebuilt.

## Locations

`runtime/framework_runtime.py`: dispatch and envelope construction (~2339-2538),
`permitted_write` (~3050-3069), `refresh` (~1866-1968), `next_action` (~2227-2245),
`cmd_gate` (~3700-3721).
