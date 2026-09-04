## Metadata

- ADR ID: D-002
- Title: Per-phase context-slice declaration for a Wave 1 phase, leaving the context-slice contract unchanged
- Date: 2026-08-19
- Status: Proposed
- Owners: `architect` (producing agent), `omn-tech-lead` (accepting owner for the Design Gate
  under the Producer Exclusion Rule)
- Related Work Items: run `run-93b302cbdb28`, phase `solution-design-and-risk-assessment`;
  supplied execution plan tasks `T-002` (this decision), `T-006`, `T-014`
- Design package: `technical-design.md` in this phase's artifacts

## Context

- Problem statement: the context guard is separate from the capability guard, and the framework's
  context-slice phase declaration names exactly three phases. Any other phase blocks at the
  context guard even after the whole capability chain clears (`F-004`). A Wave 1 agent could
  therefore be fully registered, with a resolvable module set, an active registry record, and a
  resolvable output contract, and its phase would still not dispatch. The requested decision is
  how a phase owned by a Wave 1 agent obtains the context-slice declaration it needs, what that
  declaration must contain, and whether the existing context-slice contract suffices.

- Business and technical constraints:

  - `C-011` (hard): a phase clears context resolution only if a declaration exists for its phase
    identifier, and the slice the loader produces is narrowed per phase.
  - `C-002` (hard): one primary capability surface per increment.
  - `C-005` (hard): the three currently dispatchable phases remain dispatchable — and all three
    resolve through the very declaration this decision extends.
  - `C-007` (hard): no verifier check moves from pass to fail.
  - `C-004` (hard): a phase that cannot be made dispatchable inside the increment blocks with a
    recorded reason and is reported.
  - `C-013` (hard): an increment is accepted only on the full Agent Definition of Done, and a
    partial rollout names its blocker.

- Current architecture baseline: `F-004` establishes that the declaration names exactly
  `execution-planning`, `solution-design-and-risk-assessment`, and
  `scope-invariants-and-risk-profile`, and that every other phase blocks there. `F-028`
  establishes that the context loader is implemented as frozen, content-addressed, and narrowed
  per phase, that the frozen slice is persisted per phase as a context snapshot with per-file
  digests, and that runs declare memory hydration as not requested. `F-007` establishes that a
  manifest declares its inputs, which is what a slice must be narrowed against. `F-021`
  establishes that a phase which cannot resolve is enqueued and blocked with a recorded reason
  rather than skipped. This decision rests on assumption `A-002`, that a declaration is an entry
  keyed by the phase identifier and that adding one requires no change to the context-slice
  contract, and on `A-005`, that no Wave 1 phase needs a member kind the three declared phases do
  not already use.

## Decision

- Selected option: `O-006` — per-phase declaration keyed by the phase identifier.

- Decision statement: a phase owned by a Wave 1 agent obtains context resolution through a
  declaration keyed by the canonical phase identifier the Phase Model publishes. The declaration
  must contain: the phase identifier as its key, matching the Phase Model string exactly; a
  member list of repository-relative paths, each recorded with the declared input of the owning
  manifest's input contract that it supplies, so that a member with no consuming input is visible
  as unnarrowed; per-member content addressing, so the frozen snapshot is comparable across
  attempts; and an explicit exclusion record naming what was deliberately left out and why, so an
  absent member is distinguishable from an overlooked one. The declaration introduces no member
  kind beyond those the three already-declared phases use. The existing context-slice contract
  suffices and is not changed: the disposition adds entries to a declaration that already exists
  and is already exercised by three phases, and alters no guard. That sufficiency rests on
  `A-002`; if `A-002` is false, the consequence is bounded and recorded — the context-slice
  contract itself enters scope, a further architecture decision precedes any application, and
  this decision does not pre-empt it.

- Scope of impact: `M-007` (the context-slice phase declaration), impacted as an extension and
  marked speculative because its sufficiency rests on `A-002`; and `M-012`, because the member
  list is narrowed against the owning manifest's declared inputs. No guard, and no module through
  which the three currently dispatchable phases resolve, is changed.

## Alternatives Considered

The alternatives below are the remaining options of this decision's option set in section 5.2 of
the design package, carried unchanged. Options `O-001` to `O-005` belong to the output-artifact
decision and are carried in record `D-001`.

1. `O-007` — one blanket declaration covering all thirty-six phases at once
- Benefits: no phase ever blocks at the context guard again, and no future rollout carries a
  declaration step at all. It is the smallest recurring cost of the three options, and it carries
  a recorded score of 1, above the score of 0 that `O-008` carries.
- Risks: a slice that is not narrowed per phase supplies every phase with context no declared
  input consumes, which removes the property that makes a frozen snapshot meaningful evidence of
  what a phase actually read.
- Why not selected: eliminated on `C-011`, because `F-028` establishes narrowing per phase as an
  implemented property rather than an aspiration, and on `C-002`, because declaring context for
  every phase in the framework is a framework-wide capability change carried inside an
  agent-rollout increment. Its score is recorded in the evaluation table rather than suppressed,
  because hard-constraint elimination is applied before any score is compared and a reader is
  entitled to see that a cheaper option was refused on a constraint rather than on cost.

2. `O-008` — derive the slice implicitly from the owning manifest's declared inputs instead of
   declaring it per phase
- Benefits: it removes the declaration step from every future rollout, and it derives the slice
  from the same source this decision narrows against, so the two can never drift apart. It
  satisfies every hard constraint.
- Risks: it changes the contract that the three currently dispatchable phases already resolve
  through, so `C-005` and `C-007` must be re-verified for all three; and it makes the slice a
  function of a manifest that is authored per agent, moving a runtime-owned declaration into
  agent-owned territory.
- Why not selected: it is the only option of this decision other than `O-006` to survive
  criterion 1, and so it is the highest-scoring available alternative, at a score of 0 against
  the selected option's 3 — reuse leverage 1 of 3 against a migration burden of 1, because the
  context-slice contract itself becomes contract-affecting and needs its own transition strategy.
  It spends invariants that protect a path which already works, in exchange for removing one
  declaration step, and `A-002` makes the declaration route available without touching the
  contract at all. If `A-002` proves false, this option returns as the leading candidate, which
  is why it is recorded rather than discarded.

## Consequences

- Positive outcomes expected: a Wave 1 phase clears the context guard without any change to the
  guard, so the three currently dispatchable phases are untouched by construction rather than by
  verification; the per-member recording against a declared input makes an unnarrowed slice
  visible at declaration time rather than at dispatch; and the exclusion record keeps a
  deliberate omission distinguishable from an overlooked one, which is what makes a frozen slice
  usable as evidence.

- Tradeoffs accepted: every future phase rollout carries a declaration step that cannot be
  skipped, and that step must be repeated per phase even for phases owned by an agent already
  registered. The declaration and the owning manifest's inputs are maintained separately and can
  drift; the per-member recording is the control that makes drift visible, not a guarantee
  against it.

- Risks introduced: `R-003` (`A-002` false: adding an entry does not clear the guard, so the
  context-slice contract enters scope and the increment is delayed) and `R-012` (`A-005` false: a
  phase needs a member kind no existing declaration uses, so the composition rule is incomplete
  for that phase). `R-009` is adjacent rather than introduced: bounding the manifest's supported
  phases to those whose declarations are in place, per `D-006`, is what stops a registration from
  clearing the capability guard for a phase that has no context declaration.

- Consequence for delivery sequencing: `P-009` carries this decision, and it is prerequisite to
  `P-010`. A phase is dispatched only after its declaration exists with each member recorded
  against the input requiring it. `P-009` records the declaration and the guard verdict together,
  so a false `A-002` surfaces as an observed guard verdict rather than as an inference.

## Validation Plan

- Metrics to monitor: whether the phase advances past context resolution rather than blocking
  there; the count of declared members that no declared input consumes, which should be zero;
  the count of recorded exclusions, which should be non-zero wherever a member kind was
  deliberately omitted; the guard verdicts of the three currently dispatchable phases, taken
  after the declaration is added.

- Verification checkpoints: `P-007`, the module set resolving so the manifest's declared inputs
  exist to narrow against; `P-009`, the declaration present with each member recorded against its
  consuming input and each exclusion recorded with its reason, and the context guard verdict
  recorded alongside; `P-010`, the phase dispatched only when the declaration holds; `P-011`, the
  verifier verdicts re-read before the increment status is recorded.

- Rollback or reversal conditions: reverse this decision for a phase by removing its declaration
  entry. The phase returns to blocking at the context guard, which is its current state, so the
  reversal is complete and loses nothing; no other phase's resolution is touched, because the
  entry is keyed by phase identifier. Reverse the decision as a whole if `R-003` materializes —
  adding an entry does not clear the guard — in which case the context-slice contract enters
  scope, `O-008` returns as the leading candidate, and the option set is re-evaluated against the
  actual contract requirement. Reverse it for an individual phase if `R-012` materializes for
  that phase, recording the phase at its blocking reason under `C-004` rather than declaring a
  member kind this decision did not consider.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):

Acceptance belongs to the Design Gate owners. Under the Producer Exclusion Rule, and because the
gate matrix records that the architecture owner entry names the role this agent implements,
acceptance rests with `omn-tech-lead`. This record is emitted at status `Proposed` and is not
signed by its producer.
