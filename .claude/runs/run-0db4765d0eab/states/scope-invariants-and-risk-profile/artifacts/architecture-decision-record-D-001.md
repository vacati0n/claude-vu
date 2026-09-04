# Architecture Decision Record: D-001

## Metadata

- ADR ID: D-001
- Title: Record the self-hosting profile's precedence once, in the routing policy that predates it
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-tech-lead, omn-architect
- Related Work Items: FC-002

## Context

- Problem statement: the framework has one command profile that governs how a
  framework-internal change is routed, and it has a routing policy that predates it and that a
  contributor reads first when deciding which command to use. The two do not reference each
  other. A reader who follows the older policy is routed correctly for every ordinary change
  and incorrectly for a framework-internal one, and nothing in the document they are reading
  tells them so. The decision is where the statement that resolves this belongs, and what that
  statement is allowed to say.
- Business and technical constraints: `C-002` forbids any index from becoming a second
  authority, so wherever the statement lands it may point at a rule but not restate one.
  `C-003` requires a reader to reach the profile by following indexes rather than by knowing a
  file name. `C-010` requires any wording that would change an existing rule to be surfaced as
  an open question instead of written, which bounds this decision to describing behaviour that
  already exists. `C-011` asks for the least text at the index level that lets a reader decide
  whether to follow the link. `C-001` confines the change to human indexes, so no machine
  index and no registry record participates.
- Current architecture baseline: `F-008` establishes that `config/agent-routing.md` maps intent
  to primary agent, already states a precedence rule of its own for disagreement with a Phase
  Model, and carries no statement about framework-internal changes. `F-006` establishes that
  the change request is itself routed by `config/self-hosting-profile.md` as a
  structure-preserving change, so the profile already governs in practice. `F-007` establishes
  that the routing policy is a human index rather than a machine one, so describing it changes
  nothing that resolves. `F-011` establishes that the framework's top-level entry document
  mentions neither the profile nor the proposals it produces.

## Decision

- Selected option: `O-001`.
- Decision statement: the precedence between `config/self-hosting-profile.md` and
  `config/agent-routing.md` is recorded exactly once, in `config/agent-routing.md`, expressed in
  the shape of the precedence rule that document already carries, and worded as a pointer to the
  profile rather than as a restatement of any rule the profile owns. `config/agent-routing.md`
  gains a statement that the profile governs entry-command selection for framework-internal
  changes; it does not gain the profile's routing table, its scope rule, its evidence rule, or
  its completion rule.
- Scope of impact: `M-003` carries the statement. `M-008` remains the sole authority and is
  recorded as `no-change-verified`. `M-010` is recorded as `no-change-verified` because the
  profile selects among commands that already exist rather than adding one, so the command
  catalog is not the kind of index this statement belongs in.

## Alternatives Considered

1. `O-002`, a new self-hosting hub document that describes the whole operating mode, with the
   precedence statement placed in the hub
- Benefits: one document to maintain; the reader who finds the hub sees the mode whole; each
  index needs only a link.
- Risks: a hub useful enough to be worth reading has to describe the rules, at which point two
  documents state the same rule and the framework has no mechanism that detects their drift.
- Why not selected: violates `C-002` directly, and violates `C-008` because a hub describes the
  mode in the hub's own terms rather than in the terms of the index a reader arrived through.

2. `O-003`, describing all four surfaces in the framework's top-level entry document alone
- Benefits: the smallest edit that satisfies reachability from the entry point; touches no
  document that is a member of a frozen context slice; the least maintenance surface of the
  four options.
- Risks: the reader who enters at a kind-specific index, which is how a contributor looking for
  a template or a checklist actually arrives, is never routed to the profile at all.
- Why not selected: violates `C-008`. It is the highest-scoring rejected option, because it
  violates one hard constraint where the others violate two.

3. `O-004`, adding a section to `config/self-hosting-profile.md` naming where it is indexed, and
   leaving every index unchanged
- Benefits: the authority states everything about itself in one place, so no drift is possible
  at all.
- Risks: it serves only the reader who has already found the profile, which is precisely the
  reader who does not need it.
- Why not selected: violates `C-003` and `C-008`; it leaves the discovery failure that `S-002`
  records exactly as it is.

## Consequences

- Positive outcomes expected: a contributor deciding which command to use for a
  framework-internal change learns the precedence in the document they were already reading.
  The profile remains the only place any self-hosting rule is stated, so a later change to the
  profile cannot leave a second copy behind. The statement describes behaviour that `F-006`
  shows already governs, so nothing about how the framework runs changes.
- Tradeoffs accepted: `config/agent-routing.md` acquires a second precedence clause, so a reader
  must now hold two precedence rules in mind rather than one. That cost is accepted because the
  alternative locations either duplicate a rule or serve only the already-informed reader. The
  statement is also deliberately thin under `C-011`, which means a reader who needs the rule
  itself must follow the link rather than read it in place.
- Risks introduced: `R-007`, that an entry summarises enough of the profile to go stale when the
  profile changes, which no verifier would detect. `R-001`, that `A-001` is false and the
  profile is on a resolution path, which would make this a behavioural change rather than a
  descriptive one.

## Validation Plan

- Metrics to monitor:
  - The count of documents stating a self-hosting routing rule remains exactly one, namely
    `config/self-hosting-profile.md`.
  - The four baseline verifier commands report counts identical to the baseline captured at
    `P-005`.
- Verification checkpoints:
  - `P-002` establishes the statement exists in exactly one document before any other index
    references it.
  - `P-007` re-verifies the baseline commands and every affected committed run after the last
    edit is applied.
  - `P-008` confirms `M-008`, `M-009`, `M-010`, `M-011`, and `M-012` are unchanged, which is
    what makes the confinement to human indexes evidence rather than intent.
- Rollback or reversal conditions:
  - Revert the statement from `config/agent-routing.md`. It is additive and references nothing
    that changed, so removing it returns the document to its prior content and digest.
  - Reverse this decision if `Q-001` establishes that a resolution path depends on the profile,
    because the statement would then describe a behavioural coupling rather than a routing
    convention, and the change class would be wrong.
  - Reverse this decision if `Q-003` and `Q-002` establish that the routing policy cannot carry
    the statement in its own terms, in which case the precedence lands in the top-level entry
    document and `O-003` is reconsidered on the record rather than by default.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):

Acceptance belongs to the Invariant Gate owners named in `workflows/workflow-gate-matrix.md`.
Under the Producer Exclusion Rule, and because that rule reads through the role alias, the
architecture role that produced this record cannot accept it, so the decision rests with
`omn-tech-lead`. This record is emitted at status Proposed and stays there until an owner
records a decision.
