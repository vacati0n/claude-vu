## Metadata

- ADR ID: D-001
- Title: Role-shaped named artifact types for the Output Artifact cell of every Wave 1-owned phase
- Date: 2026-08-19
- Status: Proposed
- Owners: `architect` (producing agent), `omn-tech-lead` (accepting owner for the Design Gate
  under the Producer Exclusion Rule), `omn-product-owner` (consulted for `Q-003` and `Q-005`)
- Related Work Items: run `run-93b302cbdb28`, phase `solution-design-and-risk-assessment`;
  supplied execution plan tasks `T-001` (this decision), `T-006`, `T-012`, `T-013`
- Design package: `technical-design.md` in this phase's artifacts

## Context

- Problem statement: eleven of the twelve phases the four Wave 1 delivery core agents own declare
  their output as prose in the workflow Phase Model. The runtime reads that cell literally and
  requires the exact string to be both a declared output of the owning manifest and a key of the
  registered validator map (`F-009`). A prose cell can satisfy neither, so those phases cannot
  reach a resolvable output contract, and the fourth and fifth conditions of the Agent Definition
  of Done stay out of reach however completely the agent is otherwise registered. The requested
  decision is what artifact type each prose-output phase should emit (`S-009`).

- Business and technical constraints:

  - `C-010` (hard): an output contract resolves only when one string is simultaneously the Phase
    Model Output Artifact cell, a declared output of the owning manifest, and a validator map
    key.
  - `C-012` (hard): a new artifact type must carry a registered template at the shape the
    existing template precedent sets and a validator that decides in both directions; a validator
    that accepts everything is not a decision.
  - `C-016` (hard): the disposition names an outcome for every phase the four agents own, not
    only for the phase inside the current increment.
  - `C-015` (hard): phase ownership is not changed; a phase whose disposition would require
    re-ownership is reported rather than re-owned.
  - `C-002` (hard): one primary capability surface per increment bounds application, not the
    decision.
  - `C-005`, `C-006`, `C-007` (hard): the three currently dispatchable phases keep dispatching,
    the two completed reference runs keep their fingerprints, and no verifier check moves from
    pass to fail.
  - `C-004` (hard): a phase that cannot be made dispatchable inside the increment blocks with a
    recorded reason and is reported.

- Current architecture baseline: `F-009` establishes literal cell reading and the three-point
  resolution requirement. `F-011` establishes that eleven of the twelve Wave 1-owned phases carry
  prose cells and one already names a file artifact. `F-010` establishes the seven registered
  validators and that four are executed by the declarative artifact contract engine while two are
  hand-written against numbered check sets. `F-014` establishes the two available shapes for a
  new type's validator. `F-015` establishes what a template must carry to be decidable. `F-025`
  establishes the template registry record shape and, decisively, that the existing review
  artifact type is already declared to serve the quality-review phase of `implement-feature`,
  both `review-pull-request` assessments, and the artifact-packaging phase of `release`. `F-012`
  establishes the precedent for changing an Output Artifact column and that extending the
  declaration to further review-producing phases is a scope decision rather than a structural
  finding. `F-013` establishes that a validator removes one of five capability conditions and is
  not sufficient for dispatch. `F-022` and `F-023` establish that the runtime derives the phase
  dependency graph from the Input and Output Artifact columns, so a cell edit is
  sequencing-affecting. `F-024` establishes that one phase in the same family already blocks on
  contract reconciliation because the assessment its cell asks for lies outside its owner's
  declared scope. This decision rests on assumption `A-001`, that the three-point identity plus
  template and contract reference resolution is sufficient, and on `A-004`, that each prose cell
  describes an output the phase's current owner can own.

## Decision

- Selected option: `O-002` — role-shaped artifact types.

- Decision statement: every phase a Wave 1 agent owns declares a named artifact type in its
  Output Artifact cell, shaped by the role that owns the phase rather than by the individual
  phase. Where the existing review artifact type's registry record already declares the phase,
  that type is reused unchanged. For each remaining Wave 1 role, exactly one new artifact type is
  introduced and shared across every phase that role owns, carrying a lens column to distinguish
  the phases, as the existing review type already does for the review lens. The disposition is:
  the scope-and-acceptance phase emits a new scoped-requirement-summary type; the three
  implementation phases emit one new implementation-evidence type; the three reviewer phases emit
  the existing review artifact type, one of which already declares it; and the five validation
  phases emit one new validation-evidence type. Each new type carries a template file at the
  precedent shape, a template registry record, and a validator built on the declarative contract
  engine by default, with a hand-written validator reserved for an owning agent whose quality
  module declares a numbered check set the validator must reproduce exactly. Deciding the
  disposition for all twelve phases is not applying it to all twelve: application remains bounded
  to one primary capability surface per increment.

- Scope of impact: `M-001` through `M-005` (the Phase Model tables of the five workflows),
  `M-006` (the runtime validator map), `M-008` (the declarative contract set), `M-009` (the
  template registry), `M-010` (the template files), and `M-012` (each Wave 1 manifest's declared
  outputs). `M-019` is impacted speculatively, because two of the five specifications edited are
  members of the frozen context slice of runs that already completed. `M-014` through `M-017` are
  verified unaffected.

## Alternatives Considered

The alternatives below are the remaining options of this decision's option set in section 5.2 of
the design package, carried unchanged. Options `O-006` to `O-008` belong to the context-slice
decision and are carried in record `D-002`.

1. `O-001` — one new artifact type, template, registry record, and validator per prose-output
   phase
- Benefits: the highest decidability available. A per-phase validator encodes exactly that
  phase's decision rules with no lens column and no shared semantics. It satisfies every hard
  constraint, and its impact surface is identical to the selected option: the same five Phase
  Model tables and the same validator map.
- Risks: eleven contract-affecting artifact types, each requiring a template, a registry record,
  a validator that decides in both directions, and a transition strategy. Eleven types must stay
  decidable as the phases evolve, and each is a surface on which a validator can silently degrade
  into one that accepts everything.
- Why not selected: it scored lowest of every option evaluated — reuse leverage 4 of 9 against a
  migration burden of 11, for a score of −7 against the selected option's 2. It forgoes the one
  reuse row the selected option takes, because it creates a new type even for the three phases
  the existing review artifact type already declares. The narrower decidability it buys is
  available inside the selected option through the lens column that the existing review artifact
  type already demonstrates (`F-025`), so the eleven-fold migration burden purchases nothing the
  selection cannot obtain.

2. `O-003` — one universal phase-output artifact type for all eleven prose cells
- Benefits: the smallest possible migration burden, one new type; a single template and a single
  validator to maintain. It carries a recorded score of 3, above the selected option's 2.
- Risks: a type spanning four roles' decision rules can only carry their union, and a validator
  over that union cannot reject any conforming artifact of any single phase.
- Why not selected: eliminated on `C-012`. A validator that accepts everything reports a result
  and decides nothing, so the type would satisfy the letter of the resolution requirement while
  making the acceptance evidence in `BI-4` meaningless. Its higher score is recorded rather than
  suppressed, because hard-constraint elimination is applied before any score is compared.

3. `O-004` — decide the disposition only for the phase inside increment 1, leaving the other ten
   cells prose and undecided
- Benefits: the smallest impact surface of any option, two modules rather than six, and the least
  work before the first phase dispatches. It also carries a recorded score of 3.
- Risks: each later increment requires a fresh architecture decision for the phases it covers,
  and the framework's blocked-phase reasons stay undiagnosed for ten phases.
- Why not selected: eliminated on `C-016` and `C-015`, and it narrows the requested decision,
  which `S-008` forbids doing quietly. The change request asks what artifact type each
  prose-output phase should emit; answering for one phase is not an answer.

4. `O-005` — relax output-contract resolution so a prose cell resolves, leaving every column
   unchanged
- Benefits: no workflow specification is edited at all, so `C-006` and the replay-fingerprint
  exposure in `R-001` never arise, and eleven phases clear one condition at once.
- Risks: the resolution path is the one all three currently dispatchable phases traverse, and it
  is the mechanism that makes an artifact judgeable at all.
- Why not selected: eliminated on `C-010` and `C-005`. It removes the property that makes an
  output contract resolvable rather than satisfying it, and it changes a path the invariants
  protect.

## Consequences

- Positive outcomes expected: eleven prose cells become resolvable identifiers, so the output
  condition of the capability chain is removable for every Wave 1 phase as its increment arrives;
  three of the twelve phases need no new type at all, because the existing review artifact type
  already declares them; and each later increment applies a decision that is already recorded
  rather than opening one, which is what makes the rollout pattern reusable.

- Tradeoffs accepted: three new artifact types are three contract surfaces to keep decidable
  rather than one, and each must decide across several phases through its lens column, which is a
  harder validator than a per-phase one. Reusing the existing review type binds three phases to
  one type, so a later change to it reaches all three — a coupling `F-012` records as already
  accepted for that type. Five workflow specifications are edited, two of which are members of
  the frozen context slice of completed runs, and no disposition that makes a prose cell
  resolvable can avoid editing the cell.

- Risks introduced: `R-001` (a completed reference run's fingerprint is re-derived from current
  file content and `INV-3` fails on the first cell edit), `R-002` (`A-001` false: the three-point
  identity is not sufficient for resolution), `R-004` (`A-003` false: an unreconciled Input column
  re-derives an edge into a dispatchable phase), `R-005` (a registered contract whose checks
  distinguish nothing), `R-006` (`A-004` false: a phase's output lies outside its owner's scope,
  as `F-024` already records for one phase), `R-007` (a cell edit ahead of the template, registry
  record, or validator it names).

- Consequence for delivery sequencing: `P-001` through `P-005` and `P-012` in the design package
  exist to carry this decision. Nothing may edit a cell before the fingerprint derivation is
  established, before the type's template and registry record exist, before its validator is
  registered and shown to decide, and before the owning manifest declares the identifier; and no
  cell may be edited without reconciling every Input column that names the prose string it
  replaces.

## Validation Plan

- Metrics to monitor: the count of Wave 1-owned phases whose Output Artifact cell resolves to a
  registered validator; the count that still report a capability-registration or
  contract-reconciliation reason; the guard verdicts of the three currently dispatchable phases,
  read after each cell edit; the four verifier verdicts, distinguishing a changed count from a
  changed verdict.

- Verification checkpoints: `P-001`, the fingerprint derivation established before any cell edit;
  `P-002` and `P-003`, template and registry record present and the validator shown to accept a
  conforming artifact and reject a mutated one by the named check; `P-004`, the identifier
  present in the owning manifest's declared outputs; `P-005`, the cell and its dependent Input
  columns edited as one change; `P-010`, the phase dispatched only when all of them hold;
  `P-011`, the verifier verdicts re-read before any status is recorded.

- Rollback or reversal conditions: reverse this decision for a phase by restoring its prose cell
  together with the Input columns edited alongside it, removing the validator map key, and
  removing the template registry record. The phase returns to the blocked reason it already
  carries, which is its current state, so the reversal loses nothing. Reverse the decision as a
  whole if `R-002` materializes — the three-point identity proves insufficient — because the
  disposition would then name a resolution path that does not resolve, and the option set must be
  re-derived against the actual requirement. Reverse it for an individual phase if `R-006`
  materializes for that phase, recording it at its blocking reason under `D-004` rather than
  applying the disposition.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):

Acceptance belongs to the Design Gate owners. Under the Producer Exclusion Rule, and because the
gate matrix records that the architecture owner entry names the role this agent implements,
acceptance rests with `omn-tech-lead`. This record is emitted at status `Proposed` and is not
signed by its producer.
