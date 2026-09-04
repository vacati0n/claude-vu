# Architecture Decision Record: D-003

## Metadata

- ADR ID: D-003
- Title: Separate contract registration from runtime dispatchability for the review role
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: runs/inputs/reviewer-agent-feature-request.md; supplied execution plan tasks T-002, T-004, T-006, T-008

## Context

Problem statement: registering an agent and making it executable are not the same act in this
framework, and the change request asks for a role to be added rather than exercised. The design
must decide whether the role's registration waits until it can be dispatched, or whether it
registers first and becomes routable later. The choice determines what the agent record may
declare as a dependency, what the governance rows record about phase ownership, and whether the
role is accepted at registration or at first execution. The business intent leaves the point at
which the role becomes routable open to the design.

Business and technical constraints: `C-004` requires every declared dependency of a registry
record to resolve to an existing active record. `C-005` requires an owner agent that ships a
runtime manifest to declare its owning workflow and phase identifier, and blocks a phase whose
required skills do not all resolve. `C-014` states that the role is not exercised on real work
as part of this change. `C-016` requires determinism, which is unevidenced until a repeat-run
comparison exists. `C-010` forbids changing gate ownership without a recorded decision.

Current architecture baseline: `F-025` establishes the four conditions the architecture context
asserts for invocability: an active registry record, a manifest with a resolvable module load
order, a host registration at `agents/<agent-id>.agent.md`, and a workflow phase routing to the
agent with an output artifact the runtime can validate. `F-013` establishes that
`registry/workflows.yaml` holds no record for the review-pull-request workflow whose Readiness
Gate the gate matrix names at `F-010`. `F-014` establishes that the `quality-review` phase of
`implement-feature` is already owned by the review responsibility being superseded. `F-022`
establishes that the runtime validation engine currently covers one artifact type.

## Decision

Selected option: `O-001`.

Decision statement: contract registration is separated from runtime dispatchability. The review
role registers with a data dependency on its review-result template record and no workflow
control dependency, which keeps the record valid under `C-004` while no registered workflow
declares a phase it owns. The absence of an owning phase is recorded explicitly in the
governance rows rather than left implicit. The host registration and the owning workflow phase
are sequenced after registration and after validation coverage exists, at `P-014`, and are
deferred pending acceptance of this decision and an answer to `Q-005`. Two of the four
invocability conditions in `F-025` are therefore satisfied by this change and two are
deliberately not.

Scope of impact: `M-001` and `M-002` directly, with the deferred effect falling on `M-003` and
`M-009`, both of which this design records as speculative for exactly this reason.

## Alternatives Considered

Alternatives are carried from the package evaluation table in section 5.2, stated here in terms
of what each rejected option would have meant for the separation of registration from
dispatchability.

1. `O-003` migrate the existing review contract in place and register it under its current identifier
- Benefits: this is the one option under which the decision would not arise. `F-014` establishes
  that the existing review responsibility already owns the `quality-review` phase, so migrating
  it in place inherits an owning phase, and dispatchability would follow from registration
  rather than being deferred. `R-009` would not exist.
- Risks: the inherited phase would route work to a contract whose module-set resolution and
  determinism have not yet been evidenced, because registration would precede the validation
  coverage at `P-010`. Reaching dispatchability is also the step at which the role would first
  be exercised, which strains `C-014`.
- Why not selected: eliminated at the package level on `C-007`, because it registers a role that
  already exists rather than adding one. This is the strongest alternative on this decision, and
  it is why `Q-005`, the owning-phase question, is the escalation that would most change the
  deferral.

2. `O-002` split ownership, with the new identity holding plan and design review plus framework governance and the existing role retaining code-change review
- Benefits: the new identity could be bound to a phase covering plan and design artifacts alone,
  which is a narrower routing question than the full review surface.
- Risks: dispatchability would require two phase bindings and a rule deciding which role a
  governed change routes to, so the deferral would have to be resolved twice.
- Why not selected: eliminated at the package level on `C-001` and `C-006`. For this decision
  specifically, it multiplies the routing question rather than resolving it, and `C-005` would
  require each binding to be declared consistently by both the manifest and the workflow.

3. `O-004` coexistence, with the new identity Primary for both review capabilities while the existing role retains its Primary rows unchanged
- Benefits: the existing role keeps its phase ownership, so no phase row changes at all and the
  new record could register immediately.
- Risks: two Primary owners leave the `quality-review` phase owner ambiguous, so the registry
  and the workflow specification would disagree about which role a run resolves to, which
  `C-005` states the runtime rejects rather than guesses.
- Why not selected: eliminated at the package level on `C-001`, `C-003`, and `C-006`. For this
  decision specifically, it would make the role registrable but its routing undecidable, which
  is a worse position than the deliberate deferral this decision records.

The alternative of deferring registration entirely and delivering only the contract and the
template was not carried forward as an option, because it delivers none of `S-010`: an
unregistered contract is precisely the current-state condition `F-009` records for the
superseded review responsibility.

## Consequences

Positive outcomes expected: the role becomes discoverable and its contract resolvable without
waiting on a workflow record that does not exist; validation coverage precedes any routing, so
no live phase is attached to an unverified contract; and the deferred conditions are recorded
as a decision with a named remedy rather than left as an unexplained gap.

Tradeoffs accepted: for the period between `P-011` and `P-014`, the framework carries a
registered role that no run can exercise. That state is deliberate, but it is a real cost: the
records produced at `P-006` and `P-011` cannot be validated by execution until `P-014`
completes, so the first evidence that the contract works comes from the validation coverage at
`P-010` rather than from a run.

Risks introduced: `R-009`, the role discoverable but unroutable; `R-007`, acceptance requiring
dispatchability after all, which would reverse this decision; `R-010`, the host registration
surface differing from the pattern the registered agents use, so `P-014` does not resolve.

## Validation Plan

Metrics to monitor: the count of invocability conditions from `F-025` satisfied at each point
in the sequence, which is two at `P-011` and four at `P-014`; and whether any framework record
asserts an owning phase for the role while no workflow declares one, which must remain zero.

Verification checkpoints: `P-006`, the governance rows record the owning workflow phase or
record its absence as a framework gap; `P-010`, validation coverage evidences module-set
resolution against the loader contract and repeat-run determinism before any routing exists;
`P-011`, the agent record registers with its declared dependency resolving; `P-014`, the host
registration and owning phase are established.

Rollback or reversal conditions: if `Q-004` establishes that dispatchability is required for
acceptance, this decision is reversed and `P-014` moves from deferred into scope ahead of
acceptance. If `Q-005` resolves to an owning phase before `P-011`, the agent record gains a
workflow control dependency at registration and the deferral is unnecessary. In either case the
reversal touches only the record's dependency declaration and the sequencing position of
`P-014`; no governance row and no artifact contract changes, because this decision constrains
neither.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
