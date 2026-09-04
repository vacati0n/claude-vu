# Architecture Decision Record: D-001

## Metadata

- ADR ID: D-001
- Title: Introduce the Reviewer Agent as a distinct registered agent and narrow the existing review-owning role rather than retiring it
- Date: 2026-08-18
- Status: Proposed
- Owners: architect (producer), omn-tech-lead (accepting Design Gate owner), omn-product-owner (scope confirmation)
- Related Work Items: run-c5a8d50d3238; supplied execution plan tasks `T-001`, `T-002`, `T-005`

## Context

- Problem statement: the framework must gain one accountable role that reviews
  implementation plans and code changes, without acquiring a second owner for the same
  capability. Review responsibility today sits with `omn-dev-2-reviewer`, which is Primary
  for Code Review and Governance, owns three gates across three workflows, and holds no
  agent registry record (`F-005`). The business intent leaves it open to the design whether
  the new role coexists with that responsibility or supersedes it, while requiring that
  exactly one role be accountable and that any change to an existing role's accountability
  be surfaced as a decision.
- Business and technical constraints: `C-004` requires exactly one Primary owner per
  capability identifier and one primary owner per task scope. `C-017` requires the change to
  add a role. `C-018` requires exactly one accountable role for the two named artifact types.
  `C-019` and `C-003` require any change to an existing role's accountability, and any change
  to gate ownership, to be recorded as a decision. `C-011` requires every document naming the
  current review owner to keep resolving. `C-001` forbids a second authority for identity
  metadata.
- Current architecture baseline: `F-002` establishes that only `planner` and `architect` hold
  active agent registry records, each resolving to a runtime module set. `F-005` establishes
  the existing review owner's capability and gate ownership and the absence of a registry
  record. `F-006` establishes that the Code Review and Governance column maps to the
  identifiers `code-review` and `governance-enforcement`. `F-007` establishes that the
  capability matrix records ownership at column level rather than at identifier level, and
  that several columns already carry more than one Primary. `F-021` establishes the
  deprecate-and-retain-row precedent used for the architecture role.

## Decision

- Selected option: `O-001`.
- Decision statement: the Reviewer Agent is introduced as a distinct agent `reviewer`,
  packaged as a runtime module set with a host registration and an active agent registry
  record. Primary ownership of `code-review` and `governance-enforcement` transfers to it.
  `omn-dev-2-reviewer` is narrowed rather than retired: it remains active, becomes Secondary
  for that capability group, retains Primary for Quality Verification, and retains ownership
  of the `implement-feature` Review Gate, the `fix-bug` Fix Gate, and the
  `review-pull-request` Readiness Gate.
- Scope of impact: `M-004` capability ownership and `M-012` the existing role's declared
  authority change directly. `M-001`, `M-002`, and `M-003` are the new agent's packaging,
  entry point, and discovery record. `M-005` records the resulting skill coverage. `M-017`
  and `M-018` are verified unchanged, which is a direct consequence of narrowing rather than
  retiring.

## Alternatives Considered

1. `O-002` new `reviewer` agent plus a new review phase, leaving the existing role and the
   `quality-review` phase untouched
- Benefits: no existing role's accountability changes at all; the smallest set of edits to
  records that already exist.
- Risks: two review-bearing phases in one workflow make two roles accountable for the same
  artifacts, and the phase that is blocked today stays blocked.
- Why not selected: violates `C-018`.

2. `O-003` migrate `omn-dev-2-reviewer` itself into the runtime module-set pattern, adding no
   new role
- Benefits: no ownership transfer, so no coexistence period and no risk of two Primaries;
  every existing gate and matrix reference keeps its current meaning.
- Risks: the framework gains a registered reviewer without gaining a role, which is not the
  change the intent describes.
- Why not selected: violates `C-017`.

3. `O-004` full supersession: the new agent assumes every review accountability of
   `omn-dev-2-reviewer`, which is deprecated with its row retained
- Benefits: one review-shaped role rather than two, which is the most intelligible end state;
  uses the sanctioned deprecation precedent at `F-021`.
- Risks: retiring the existing role removes the owner of three gates across three workflows;
  two of those workflows carry no canonical phase identifiers, so their rewiring cannot be
  verified by routing and lands outside the approved first surface.
- Why not selected: it satisfies every hard constraint but carries an impact surface of 8
  against 5 and a migration burden of 8 against 5. Nothing in the requirements needs the
  existing role retired, because `C-018` concerns who reviews the two named artifact types,
  not how many review-shaped roles exist. This is the highest-scoring rejected alternative.

4. `O-005` express review as a capability of the existing `architect` agent
- Benefits: the highest reuse leverage of any option; no new agent identity to register.
- Risks: one agent would produce and be positioned to approve evidence about its own design
  output, and review authority would sit inside architecture decision authority.
- Why not selected: violates `C-005`, `C-014`, and `C-017`.

## Consequences

- Positive outcomes expected: exactly one role is accountable for reviewing implementation
  plans and code changes; the new role is discoverable on the same terms as the two already
  registered; every document naming the existing review owner keeps resolving, because that
  role stays active; and no gate owner entry changes, so `C-003` is satisfied without a
  gate-ownership decision.
- Tradeoffs accepted: two roles with review in their names coexist, which costs
  intelligibility and creates a standing risk that a later reader re-merges them. The
  reviewer becomes Primary for a capability group whose gate is owned by the role it took
  that capability from, so the Review Gate's owner and the phase's owner differ. Both costs
  are accepted to keep the change inside one workflow surface, and both are made explicit in
  `M-004`, `M-008`, and `M-012` rather than left to inference.
- Risks introduced: `R-001` two Primary owners if records are edited before the disposition
  is recorded; `R-002` the capability matrix cannot express identifier-level ownership, so
  the single-Primary property cannot be evidenced from the record as it stands; `R-014` the
  disposition is unavailable if the existing role proves to be retired rather than
  unmigrated.

## Validation Plan

- Metrics to monitor: the number of Primary owners resolving for `code-review` and for
  `governance-enforcement`; the number of unresolved references to `omn-dev-2-reviewer`
  across workflows, gates, and matrices; the proportion of review-bearing phases in the
  approved surface resolving to exactly one accountable role.
- Verification checkpoints: `P-001` records the disposition before any record is edited;
  `P-011` records ownership in the two matrices; `P-014` verifies end-to-end resolution with
  no unresolved or deprecated reference; `P-015` aligns the existing role's contract text
  with the matrices.
- Rollback or reversal conditions: reverse if `Q-001` establishes that the existing role is
  retired rather than unmigrated, or if `P-014` finds an unresolved reference that narrowing
  cannot repair. Reversal restores the `M-004` ownership cell and the `M-012` authority text;
  the new agent's packaging and record become inert once no phase routes to it.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
