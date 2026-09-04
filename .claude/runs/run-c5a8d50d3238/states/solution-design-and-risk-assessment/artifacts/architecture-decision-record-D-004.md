# Architecture Decision Record: D-004

## Metadata

- ADR ID: D-004
- Title: The Reviewer Agent produces gate evidence and never approves a gate; Review Gate ownership is unchanged
- Date: 2026-08-18
- Status: Proposed
- Owners: architect (producer), omn-tech-lead (accepting Design Gate owner)
- Related Work Items: run-c5a8d50d3238; supplied execution plan tasks `T-002`, `T-012`, `T-005`

## Context

- Problem statement: the reviewer produces the artifact assessed at the Review and
  Verification Gates. If it also held approval authority at a gate assessing its own output,
  the framework would have an agent approving its own evidence. The gate matrix already
  states a rule for this case, and the design must state which side of that rule the reviewer
  falls on, because leaving it to inference is how the two roles silently collapse.
- Business and technical constraints: `C-005` prohibits an agent approving a gate for an
  artifact it produced, even when its role appears in that gate's owner list. `C-003`
  prohibits any change to gate ownership without a recorded decision naming the gate matrix
  owners. `C-014` requires the reviewer's authority to be disjoint from gate approval
  authority. `C-019` requires any change to an existing role's accountability to be surfaced
  as a decision.
- Current architecture baseline: `F-017` establishes the Producer Exclusion Rule and that
  approval then requires a different listed owner; the rule already carries the architect
  case for the Design and Invariant Gates. `F-018` establishes that `omn-dev-2-reviewer` is
  the sole required owner of the `implement-feature` Review Gate. `F-008` establishes that
  `quality-review` is assessed at the Review and Verification Gates. `A-007` registers the
  assumption that the review outcome is evidence assessed at a gate rather than the gate
  decision itself.

## Decision

- Selected option: `O-001`.
- Decision statement: the reviewer produces the evidence assessed at the Review and
  Verification Gates and holds no gate approval authority anywhere in the framework. Its
  declared authority states this as an explicit prohibition naming the holder of the withheld
  authority. Review Gate owner entries are unchanged: `omn-dev-2-reviewer` remains the
  required owner and the gate matrix records the reviewer as the producer of the evidence
  assessed there. Because no owner entry changes, `C-003` is satisfied by this record without
  a separate gate-ownership decision.
- Scope of impact: `M-008` the Producer Exclusion Rule section and the gate matrix usage
  notes, which gain the reviewer case in the form already used for the planner and architect
  cases. `M-001` carries the prohibition in the reviewer's declared authority. `M-017` and
  `M-018` are verified unchanged.

## Alternatives Considered

1. `O-002` new `reviewer` agent plus a new review phase
- Benefits: a new phase could be given a gate whose owner is chosen fresh, avoiding any
  interaction with an existing owner list.
- Risks: two review-bearing phases in one workflow, and a new gate or a reused gate assessing
  two producers' evidence.
- Why not selected: violates `C-018`.

2. `O-003` migrate the existing review owner into the runtime module-set pattern
- Benefits: the migrated role would own both the phase and the gate, which is the current
  arrangement and needs no gate-matrix edit.
- Risks: it would make the producer of the review evidence the owner of the gate assessing
  it, which is precisely the case `C-005` exists to prevent, so it would require either a
  gate-ownership change or a standing exception.
- Why not selected: violates `C-017`, and it converts a satisfied constraint into one
  requiring an exception.

3. `O-004` full supersession, with the reviewer assuming the existing role's gate ownerships
- Benefits: one role holds review across the framework, which is the most intelligible end
  state.
- Risks: the reviewer would own the Review Gate while producing the evidence assessed there,
  so the Producer Exclusion Rule would force a second listed owner to be introduced for that
  gate, and the same problem would repeat for the Fix Gate and the Readiness Gate.
- Why not selected: it satisfies the hard constraints only by adding gate owners in three
  workflows, each of which `C-003` requires be recorded as its own decision. It is the
  highest-scoring rejected alternative.

4. `O-005` express review as a capability of the existing `architect` agent
- Benefits: the architect's producer exclusion is already recorded, so the pattern would be
  reused rather than extended.
- Risks: the same agent would produce the design, produce the review of that design, and
  appear in the owner list of the gate assessing both.
- Why not selected: violates `C-005`, `C-014`, and `C-017`.

## Consequences

- Positive outcomes expected: the producer and the approver of Review Gate evidence are
  different roles by construction, so `C-005` holds without an exception; no gate owner entry
  changes, so `C-003` requires no further decision and no workflow outside the approved
  surface is touched; and the reviewer's authority is stated as disjoint from gate approval
  in the same place a downstream reader looks for its permitted actions.
- Tradeoffs accepted: the Review Gate's owner and the `quality-review` phase's owner are
  different roles, which is unusual in the current matrix and will read as an inconsistency
  to anyone who has not read this record. That is the direct price of keeping gate ownership
  unchanged, and it is paid explicitly in the gate matrix rather than left implicit. A second
  consequence follows and is not resolved here: the reviewer cannot review its own creation,
  so the accepting owner for the tasks that author the reviewer's own module set, template,
  and registry record must be named, which is `Q-008`.
- Risks introduced: `R-007` the reviewer's declared authority written to include gate
  approval or architecture decisions; and, through `Q-008`, the possibility that the Review
  Gate has no available accepting owner for the reviewer's own authoring tasks.

## Validation Plan

- Metrics to monitor: the count of gates listing the reviewer as an approving owner, which
  must be zero; the count of gate decisions recorded by the producer of the assessed
  evidence, which must be zero; the presence of an explicit gate-approval prohibition in the
  reviewer's declared authority naming the holder of the withheld authority.
- Verification checkpoints: `P-004` states the prohibition with the holder named; `P-006`
  records the producer relationship in the gate matrix before `P-013` makes the reviewer
  dispatchable; `P-014` verifies that no gate lists the reviewer as an approving owner for
  evidence it produced; the QA focus areas include an attempt to exceed the declared
  authority and the expected refusal.
- Rollback or reversal conditions: reverse if the gate matrix owners decide that the reviewer
  should hold Review Gate approval, which would require a separate recorded decision naming
  those owners under `C-003`, or if `Q-008` resolves in a way that makes the unchanged owner
  entry unworkable. Reversal removes the added gate-matrix sentences; the reviewer's authority
  prohibition would then require its own amendment through `M-001`.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
