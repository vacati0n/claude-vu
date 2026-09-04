# Architecture Decision Record: D-002

## Metadata

- ADR ID: D-002
- Title: Route the Reviewer Agent through the existing `quality-review` phase rather than a new phase
- Date: 2026-08-18
- Status: Proposed
- Owners: architect (producer), omn-tech-lead (accepting Design Gate owner)
- Related Work Items: run-c5a8d50d3238; supplied execution plan tasks `T-009`, `T-012`, `T-006`

## Context

- Problem statement: the reviewer must become routable by a workflow, which requires a phase
  that names it as owner and declares an output artifact the runtime can validate. The
  framework can either reuse a phase that already exists or introduce a new one, and the
  choice determines whether the phase currently blocked at capability resolution becomes
  useful or stays blocked alongside a new sibling.
- Business and technical constraints: `C-009` makes a routed phase with a validatable output
  artifact part of what makes an agent invocable. `C-018` requires exactly one accountable
  role for the two named artifact types. `C-015` requires a registered validator before the
  phase can pass `G1-CAPABILITY`. `C-016` requires discoverability on the same terms as
  registered roles. `A-003` limits the first workflow surface to `implement-feature`.
- Current architecture baseline: `F-008` establishes `quality-review` as a canonical phase of
  `implement-feature`, owned by `omn-dev-2-reviewer`, producing a review findings log and a
  verification report, assessed at the Review and Verification Gates, and requiring S07, S09,
  and S08. `F-009` establishes that a phase resolves to exactly one owner agent and that an
  owner shipping a manifest must declare that phase identifier. `F-010` establishes that
  `quality-review` is enqueued and blocked at `G1-CAPABILITY`, and that only
  `implement-feature` carries canonical phase identifiers. `F-013` establishes that the phase
  graph derives hard edges from the Input and Output Artifact columns, falling back to row
  adjacency.

## Decision

- Selected option: `O-001`.
- Decision statement: the reviewer is routed through the existing `quality-review` phase of
  `implement-feature`. That phase's Owner Agent becomes `reviewer`, its Input names the
  registered plan artifact and the implementation change set, and its Output Artifact becomes
  the review outcome. No phase identifier is created, and the reviewer's manifest declares
  `quality-review` as its supported phase so that the runtime's identifier check resolves
  rather than rejecting a mismatch.
- Scope of impact: `M-006` the Phase Model row and the Phase Identifier Sources table, and
  `M-007` the workflow record's dependency array. `M-005` follows, because the phase table's
  Primary Agents cell lives in the skill matrix as well. `M-016` is verified unchanged: the
  resolution chain, the adapter, and the graph derivation resolve any agent that satisfies
  the guard.

## Alternatives Considered

1. `O-002` introduce a new review phase into `implement-feature`, leaving `quality-review`
   and its owner untouched
- Benefits: no existing phase row changes, so no in-flight run can be affected by the edit,
  and the existing owner keeps its phase.
- Risks: `quality-review` stays blocked at `G1-CAPABILITY` while a second review-bearing
  phase is added beside it, so the workflow gains a phase without losing a blocked one, and
  review resolves to two roles in one workflow.
- Why not selected: violates `C-018`.

2. `O-003` migrate the existing owner into the runtime module-set pattern, keeping the phase
   row unchanged
- Benefits: the phase row needs no edit at all, so the phase-graph derivation is untouched
  and no in-flight run can unblock unexpectedly.
- Risks: the framework gains a registered reviewer without gaining a role.
- Why not selected: violates `C-017`.

3. `O-004` full supersession, with the reviewer taking `quality-review` and every other
   review accountability
- Benefits: routes through the same existing phase, so the phase-level consequences are
  identical to the selected option.
- Risks: extends the same reasoning into two workflows whose phase identifiers are not
  canonical, so their routing cannot be verified.
- Why not selected: it agrees with the selected option on this decision and loses on the
  wider ownership question recorded in `D-001`. It is the highest-scoring rejected
  alternative.

4. `O-005` express review as a capability of the existing `architect` agent
- Benefits: `architect` already owns a routed phase, so no phase row would change.
- Risks: the design phase and the review phase would collapse into one owner, and review
  evidence would be produced by the author of the design it assesses.
- Why not selected: violates `C-005`, `C-014`, and `C-017`.

## Consequences

- Positive outcomes expected: the phase that is blocked today becomes the phase that
  becomes routable, so the change removes a known gap rather than adding a parallel path. The
  phase identifier is unchanged, so every routing key that resolves today keeps resolving.
  The derived edge into the following phase falls back to row adjacency and yields the same
  order, so the phase graph's shape does not change.
- Tradeoffs accepted: editing a live phase row means an in-flight run holding that work item
  blocked can re-evaluate its guard and move to `pending`, because guards are a pure function
  of persisted state. The design accepts this rather than avoiding it by adding a phase,
  and pays for it by ordering every guard precondition before the row change at `P-013`.
  A second tradeoff: the phase remains mandatory for S08 while performance is not among the
  five review dimensions, which is left open rather than silently resolved.
- Risks introduced: `R-003` a consumer bound to the current Output Artifact wording; `R-005`
  an in-flight run resuming into a partly built chain; `R-010` the S08 mismatch between the
  phase's mandatory skills and the reviewer's declared dimensions; `R-013` expansion beyond
  the approved surface if `A-003` is false.

## Validation Plan

- Metrics to monitor: whether `quality-review` resolves to exactly one owner agent; the
  guard verdict for that phase before and after the change; the number of work items that
  transition from `blocked` to `pending` as a consequence; the derived phase-graph edge set
  before and after.
- Verification checkpoints: `P-012` registers the validator before the row changes; `P-013`
  changes the row only once every `G1-CAPABILITY` precondition holds; `P-014` verifies that
  each approved phase resolves to the reviewer with no unresolved or deprecated reference.
- Rollback or reversal conditions: reverse if `Q-004` establishes that a validator cannot be
  registered for the review outcome, or if `P-014` finds the phase resolving to more than one
  owner. Reversal restores the Owner Agent and Output Artifact cells and removes the two
  workflow-record dependency entries, after which the phase blocks at `G1-CAPABILITY` again —
  its current state — so the framework returns to today's behaviour with no residue.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
