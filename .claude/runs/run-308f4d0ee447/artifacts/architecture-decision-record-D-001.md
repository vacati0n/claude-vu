# Architecture Decision Record: D-001

## Metadata

- ADR ID: D-001
- Title: Register the review role under a new agent identity that supersedes the existing review responsibility
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: runs/inputs/reviewer-agent-feature-request.md; supplied execution plan tasks T-001, T-004, T-011, T-013, T-014

## Context

Problem statement: the framework must gain one accountable review role for implementation
plans and code changes, while review responsibility is already recorded elsewhere in the
framework. Two roles cannot hold the same review responsibility, so the disposition of the
existing responsibility must be decided before any governance record, capability declaration,
or dimension criteria set is authored against it. The business intent leaves the choice
between coexistence and supersession open to the design.

Business and technical constraints: `C-001` makes the discovery registries single-authority,
so a second authority for the same ownership metadata is a defect rather than an option.
`C-003` allows one primary owner per task scope. `C-006` requires a single accountable role
for both governed change types. `C-007` requires that the change add a review role as a
registered agent identity. `C-011` requires any change to an existing role's accountability to
be surfaced as a decision. `C-012` requires every existing reference to the review
responsibility to keep resolving throughout the transition.

Current architecture baseline: `F-006` establishes that `omn-dev-2-reviewer` is recorded as
Primary for Code Review and Governance and as Primary for Quality Verification, and that the
identifiers under Code Review and Governance are `code-review` and `governance-enforcement`.
`F-007` establishes that `omn-qa` is also recorded as Primary for Quality Verification.
`F-009` establishes that `omn-dev-2-reviewer` holds a contract under `agents/` and no registry
record. `F-010` establishes that it owns the implement-feature Review Gate and the
review-pull-request Readiness Gate. `F-008` and `F-012` establish that the framework has
already executed one role supersession, retaining the superseded row and adding a resolution
note at the gate matrix so that documents still naming the superseded identifier resolve
during migration.

## Decision

Selected option: `O-001`.

Decision statement: the review role is registered under a new agent identity, `reviewer`,
which supersedes the review responsibility recorded at `omn-dev-2-reviewer`. The superseded
rows in `agents/capability-matrix.md` and `skills/agent-skill-matrix.md` and the superseded
contract itself are marked and retained during reference migration, following the pattern the
framework already applied to the architecture role. The new identity takes Primary ownership of
Code Review and Governance, declaring only the existing identifiers `code-review` and
`governance-enforcement`. Gate ownership rows are untouched; the gate matrix's existing
role-resolution note covers the superseded identifier. At no point during the transition do two
rows carry Primary for the same capability.

Scope of impact: `M-004`, `M-005`, and `M-008` directly, with downstream effect on `M-001`,
`M-002`, and `M-010`.

## Alternatives Considered

1. `O-003` migrate the existing review contract in place and register it under its current identifier
- Benefits: the highest reuse leverage of any option, because it reuses the existing identity
  and every reference to it; the smallest impact surface; and the lowest migration burden,
  because no reference migration is created at all. It satisfies `C-001`, `C-003`, `C-006`,
  and `C-012`.
- Risks: the framework gains no new role, so if the request genuinely requires an added role
  the change does not deliver it and the correction is a second supersession later.
- Why not selected: violates `C-007`. `S-001` and `S-011` state that the change adds a role to
  the framework, and this option registers a role that already exists rather than adding one.
  This is the single constraint on which the selection turns, so the reading of `S-001` is
  routed to `omn-product-owner` as `Q-001` rather than treated as settled.

2. `O-002` split ownership, with the new identity holding plan and design review plus framework governance and the existing role retaining code-change review
- Benefits: no supersession and no reference migration; each role keeps a coherent scope.
- Risks: every governed change needs a routing rule to decide which reviewer owns it, and the
  boundary between the two scopes becomes a second place where review ownership is decided.
- Why not selected: violates `C-006`, because neither role is accountable for both governed
  change types, and violates `C-001`, because the scope boundary becomes a second authority
  for the same ownership question.

3. `O-004` coexistence, with the new identity Primary for both review capabilities while the existing role retains its Primary rows unchanged
- Benefits: the smallest impact surface of any option and no migration obligation at all; it
  is the disposition the supplied execution plan assumed.
- Risks: ownership is ambiguous at every gate and in every capability lookup.
- Why not selected: violates `C-003` by giving two roles Primary for the same capability,
  violates `C-001` by creating a second authority for the same ownership metadata, and
  violates `C-006` by leaving two accountable roles rather than one.

## Consequences

Positive outcomes expected: each review capability resolves to exactly one Primary owner
across the governance records; the review role is discoverable on the same terms as the
already-registered agents; and the transition reuses a supersession pattern the framework has
already executed, so no new migration mechanism is introduced.

Tradeoffs accepted: a reference migration is created that `O-003` would have avoided, and the
supplied context does not establish how many framework documents name the superseded
identifier for review responsibility. The coexistence period is therefore bounded by a
retirement condition rather than by a known amount of work.

Consequence for Quality Verification ownership, recorded here because `C-011` requires it:
superseding a role that holds a Primary rating requires stating where that rating goes. Under
this decision, Primary ownership of Quality Verification consolidates on `omn-qa`, which
`F-007` records as already holding it, and the review role holds Secondary there. No capability
becomes unowned and no new Primary owner is introduced. This consequence is recorded inline in
the design package as `D-005` and routed for confirmation as `Q-008`.

Risks introduced: `R-003`, both identities left carrying Primary for the same capability during
coexistence; `R-004`, a coexistence period with no enforced end; `R-013`, reversal of this
decision if the reading of `S-001` behind `C-007` is answered differently.

## Validation Plan

Metrics to monitor: the count of framework documents still naming the superseded identifier
for review responsibility, tracked from `P-012` until the retirement condition is met; and the
count of Primary owners resolving for `code-review` and `governance-enforcement`, which must be
exactly one at every point in the transition, not only at its end.

Verification checkpoints: `P-006`, governance records carry the role with one Primary owner per
review capability and the superseded rows retained; `P-010`, validation coverage evidences
single-Primary resolution and confirms that a document naming the superseded identifier still
resolves; `P-012`, the reference migration is completed or its remaining references are
recorded.

Rollback or reversal conditions: if `Q-001` is answered in favour of registering the existing
identifier, or if single-Primary resolution cannot be maintained during coexistence, remove the
added governance rows and clear the supersession markers. Review ownership returns to the
superseded identity with no other record changed, because the superseded rows were retained
rather than replaced at every step.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
