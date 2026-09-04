## Metadata

- ADR ID: D-002
- Title: Reject the architect as the review package emitter, and defer the owning-agent output declaration
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: FC-001; execution plan tasks T-003, T-008

## Context

- Problem statement: `F-004` establishes that a phase's declared artifact is resolved against
  the owning agent's manifest outputs as well as against the `VALIDATORS` map, so a Phase Model
  declaration is one half of a resolvable output contract and the owning agent's `outputs` block
  is the other. `F-011` records both halves as the remaining work. This change makes the
  phase-side declaration under `D-001`. Something must be decided about the agent-side half,
  because leaving it unstated would let a reader conclude either that it was done or that it is
  unnecessary, and both readings are wrong.
- Business and technical constraints: `C-003` forbids any agent gaining or losing a contract in
  this change, and requires an owning-agent output declaration the change would need to be
  surfaced as a decision rather than made silently. `C-002` requires the declaring phase to be
  the one whose declared work the artifact already describes. `C-010` forbids claiming the phase
  becomes executable. `C-005` requires a traded blocked reason to be surfaced.
- Current architecture baseline: `F-019` establishes that `agents/architect/manifest.yaml`
  declares outputs `technical-design` and `architecture-decision-record` only, while declaring
  `supportedWorkflows` including `review-pull-request` at phase `structural-compliance`. `F-017`
  establishes that the `architect` registry record declares nine capabilities, none of which is
  `code-review` or `governance-enforcement`. `F-018` establishes that the architect contract
  places reviewing pull requests and assessing concrete diffs out of scope, and assigns
  verification of a concrete change to `omn-dev-2-reviewer`. `F-009` establishes that the review
  package artifact type declares exactly the capabilities `code-review` and
  `governance-enforcement`, and carries findings, correction requests, and a readiness verdict.
  `F-005` establishes that `review-pull-request/structural-compliance` blocks with failure class
  `workflow-contract-violation`. `F-006` establishes that `omn-dev-2-reviewer` is host-invocable
  and holds no registry record. `M-007` and `M-008` are the two agent contracts in question.

## Decision

- Selected option: `O-001`.
- Decision statement: two things follow from the selection, and both are decided here. First,
  `architect` is rejected as the emitter of the review package, because an artifact carrying a
  review verdict may not be declared as an architect output when `F-018` places producing one
  outside the architect contract's scope and `F-017` shows its capability set holds neither
  capability the artifact type declares. Second, the owning-agent `outputs` declaration for the
  review package is deferred to the registration of `omn-dev-2-reviewer`, where it is authored
  as part of a new manifest rather than added to an existing contract, so `C-003` is satisfied
  without leaving the obligation unrecorded. This change makes no agent contract change of any
  kind.
- Scope of impact: `M-008` is recorded as `no-change-verified`, because the architect manifest's
  `outputs` block does not change although `F-011` would lead a reader to expect it to. `M-007`
  is recorded as `no-change-verified` at speculative confidence, because `A-002` leaves the
  existence of an `omn-dev-2-reviewer` manifest unconfirmed. `M-001` carries the phase-side
  declaration alone.

## Alternatives Considered

1. `O-002` declare the artifact at `review-pull-request/structural-compliance`, whose owner is
   `architect`
- Benefits: closes the blocker at the phase where `F-005` and `F-011` recorded it, using the one
  candidate owner that is registered and host-invocable.
- Risks: to resolve an output contract it requires the architect manifest to declare the review
  package, which `C-003` reserves, and `F-018` makes that a role-boundary reconciliation rather
  than an additive edit because the architect contract forbids producing a review verdict.
- Why not selected: the option loses the reuse-leverage criterion in the package evaluation
  table, and the specific reuse candidate it depends on, the architect output contract, is
  recorded as `rejected` in the reuse survey for exactly this reason.

2. `O-003` declare the artifact in all four phases the artifact type's registry description names
- Benefits: would force every owning agent's output obligation to be recorded at once.
- Risks: three of the four owning agents hold no registry record, and `F-021` places one of the
  affected workflow files inside a frozen context slice.
- Why not selected: eliminated on `C-001`, and additionally on `C-006` and `C-007`.

3. `O-004` declare the artifact at `implement-feature/quality-review`
- Benefits: the same owner as the selected option, so the deferral decided here would be
  identical.
- Risks: `F-021` places `workflows/implement-feature.md` inside this run's frozen context slice.
- Why not selected: eliminated on `C-006` and `C-007`.

4. `O-005` declare routing on the artifact-type registry record instead of in a Phase Model
- Benefits: would sidestep the owning-agent resolution in `F-004` entirely, since no phase would
  declare the artifact.
- Risks: it would also sidestep the resolution the runtime actually performs, so no phase would
  ever resolve the artifact as its output, and `M-001` would gain nothing.
- Why not selected: eliminated on `C-004`.

## Consequences

- Positive outcomes expected: no agent contract changes, so `C-003` holds without exception. The
  obligation that remains is named rather than assumed absent, so a reader of gap 7 can tell
  which half of the remaining work this change performed. The architect contract's boundary
  against the reviewer is preserved rather than eroded by an artifact assignment.
- Tradeoffs accepted: `review-pull-request/structural-compliance` remains blocked with the class
  `F-005` records, so the phase gap 7 singles out is not cleared by this change. The declaration
  made under `D-001` resolves no output contract until `omn-dev-2-reviewer` is registered with a
  manifest declaring the artifact, so the routed phase remains undispatchable, which `C-010`
  accepts.
- Risks introduced: `R-003` `A-002` is false and an existing manifest must change, engaging
  `C-003`; `R-008` the phase gap 7 names remains blocked and a reader believes routing closed it.

## Validation Plan

- Metrics to monitor: the `outputs` block of every agent contract touched by the change, which
  must be none; the per-phase blocked reason for `review-pull-request/structural-compliance`,
  which must be unchanged; and the per-phase blocked reason for
  `review-pull-request/code-quality-review`, which `A-004` expects to be unchanged.
- Verification checkpoints: `P-003` records what must be true for a declared Output Artifact to
  become validated run evidence and names the part the declaration alone does not satisfy;
  `P-008` compares the per-phase blocked reasons against the recorded before-state; and `Q-003`
  confirms `A-002` before `P-005`.
- Rollback or reversal conditions: reverse if `Q-003` establishes that `omn-dev-2-reviewer`
  ships a manifest with an `outputs` block, because the deferral then becomes a live contract
  change that `C-003` reserves, in which case `D-002` is withdrawn and the declaration is
  escalated to that agent's owners before `P-005` proceeds. Reverse also if the owners answering
  `Q-004` determine that `structural-compliance` is verdict-issuing rather than
  expectation-setting, because the rejection of `architect` as emitter would then rest on a
  boundary that is itself under revision.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
