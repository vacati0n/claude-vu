# Architect ruling — supersession range (F4) and approved sibling gates (CR-001)

Operator-supplied input to run `run-3e6f6a248b99` (fix-bug), `fix-implementation` attempt 2 and
the Fix Gate. Produced by the `architect` role on 2026-09-06 as a consultation answering findings
F1/F4 of the Fix Gate assessment recorded on the run. Nothing was executed or written.

## RANGE RULE: (b) — the completed downstream cone of the target

The memo's path rule (a) only walks backward from `closes_state` to `target` via
`hard_ancestors(closes_state)`; it never walks forward from `target` to phases that hard-depend
on it. F4's own example shows the fault line: when `target == closes_state`, the "between" set
collapses to one node, so `root-cause-analysis` — completed, and hard-dependent on the target
`triage-and-impact` — is left standing on evidence being rebuilt, violating the invariant that no
artifact may stand on superseded evidence. Because a valid `target` is already required to be a
hard predecessor of `closes_state` (so `closes_state` is itself a member of the target's downstream
cone), the full transitive-descendant closure of `target` — restricted to completed items —
strictly contains the memo's path and additionally catches every completed dependent the path
rule misses, including ones off the `closes_state` ancestor chain (fix-implementation's second
parent, `root-cause-analysis`). The extra budget charge is the correct cost of the human-block
invariant, not overreach.

## CR-001 RULE: refuse — no third transition

M13 as restated legalises exactly two transitions: `state (COMPLETED, PENDING) superseded` and
`gate (FAILED, PENDING) rollback_authorised`. There is no `gate (COMPLETED, PENDING)` pair.
Superseding an approved gate's decision would require inventing that third transition,
contradicting the deliberately minimal engine surface O-001 was selected for. The existing
`standing` check already refuses when an approved gate closes an intermediate phase; CR-001 is
simply removing the `p != closes` exclusion so a sibling gate approved on `closes_state` itself is
checked the same way — no new transition, same refusal message, same operator remedy (a
shallower target, or a new run). The refusal changes nothing in the store.

## WORKFLOWS CHECKED

`workflows/fix-bug.md`: the `fix-implementation` row has two hard inputs, `triage-and-impact` and
`root-cause-analysis` — the F4 downstream-cone case. `workflows/implement-feature.md`: the
`quality-review` row lists both Review Gate and Verification Gate on one phase — the F1/CR-001
sibling-gate case.

## Consequence for the stranded run `run-4c51600606df`

Its Verification Gate is undecided (blocked), so `rollback --gate "Review Gate" --target
implementation` is admissible under CR-001. It must be issued **before** any decision is recorded
on the Verification Gate; an approval there first would make the rollback refuse.
