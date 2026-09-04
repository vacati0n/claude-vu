## Metadata

- ADR ID: D-001
- Title: Route the review package by declaring it as the Output Artifact of `review-pull-request/code-quality-review`
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: FC-001; execution plan tasks T-001, T-002, T-003, T-010

## Context

- Problem statement: `review-package.md` is a contracted, validated artifact type that no
  workflow phase emits. `F-002` establishes it is registered in `registry/templates.yaml`,
  carries a validator in the `VALIDATORS` map, and passes its fixture with a declared mutation
  caught by `P3`. `F-003` establishes that the coverage proof reads the Output Artifact column
  of every active Phase Model and asserts coverage in one direction only, so an artifact type
  that no phase routes is invisible to it. `F-011` records the same defect as known gap 7. The
  framework therefore contracts a capability it does not offer, and a review verdict reaches a
  run as prose in an Output Artifact column rather than as a validated artifact under run
  evidence.
- Business and technical constraints: `C-001` permits exactly one phase to declare the
  artifact. `C-002` requires that phase to be the one whose declared work the artifact already
  describes, with no new phase and no owner change. `C-003` forbids any agent gaining or losing
  a contract in this change. `C-004` forbids a second place where an artifact type is declared.
  `C-005` requires the declared artifact to be one the Validation Engine can decide, and
  requires a traded blocked reason to be surfaced. `C-006` and `C-007` require committed run
  evidence to remain valid and every previously proven run to still verify. `C-008` makes the
  Phase Model a machine-read contract whose Input and Output Artifact columns determine enforced
  sequencing. `C-010` forbids claiming the phase becomes executable.
- Current architecture baseline: `F-001` establishes that `workflows/review-pull-request.md`
  declares five phases and that every Output Artifact cell in that table is prose naming no
  file. `F-004` establishes that a phase's declared artifact is resolved against the owning
  agent's manifest outputs and the `VALIDATORS` map, and that a prose artifact resolves no file
  contract. `F-015` establishes the three rules from which the runtime derives phase edges.
  `F-020` establishes the five phase identifiers and their owners. `F-009` and `F-016` establish
  that the artifact type declares the capabilities `code-review` and `governance-enforcement`,
  and that `omn-dev-2-reviewer`, the owner of `code-quality-review`, holds that column at
  Primary.

## Decision

- Selected option: `O-001`.
- Decision statement: the review package is routed by naming `review-package.md` in the Output
  Artifact cell of exactly one Phase Model row, the `code-quality-review` row of
  `workflows/review-pull-request.md`, replacing the prose token that cell carries today. No
  other cell in that table changes, except an Input entry that the recorded before-state shows
  names the replaced token from a phase other than the immediately following row, which is
  re-pointed to the same artifact token.
- Scope of impact: `M-001` as a contract-change, with `M-002` taking an operational impact as
  its routed-artifact coverage result changes. `M-003`, `M-004`, `M-005`, `M-006`, `M-008`,
  `M-009`, and `M-011` are recorded as `no-change-verified`, and `M-007` and `M-012` are
  recorded as `no-change-verified` at speculative confidence.

## Alternatives Considered

1. `O-002` declare the artifact at `review-pull-request/structural-compliance`
- Benefits: closes the defect where the framework recorded it, since `F-005` and `F-011` name
  that phase as the one blocked for want of a contract reconciliation, and its owner `architect`
  is the only registered, host-invocable owner among the candidate phases.
- Risks: `F-004` resolves a declared artifact against the owning agent's manifest outputs, and
  `F-019` establishes the architect manifest declares only `technical-design` and
  `architecture-decision-record`, so the declaration would resolve no output contract. Supplying
  that half is reserved by `C-003` and, per `F-018`, would carry a role-boundary reconciliation
  rather than an additive manifest edit.
- Why not selected: it ties `O-001` on hard-constraint satisfaction and on impact surface, and
  loses at the third evaluation criterion, reuse leverage, scoring seven against eight, because
  the capability "an owning agent whose declared work the artifact describes and whose contract
  permits producing it" has no reusable candidate under it. `D-002` records the rejection ground.

2. `O-003` declare the artifact in all four phases the artifact type's registry description names
- Benefits: discharges `F-011`'s statement of the remaining work in full and leaves one review
  output form across every review-producing phase.
- Risks: it edits `workflows/implement-feature.md`, which `F-021` establishes is a member of
  this run's frozen context slice, so `A-006` makes it change what committed implement-feature
  runs reproduce.
- Why not selected: eliminated on `C-001`, which permits exactly one phase, and additionally on
  `C-006` and `C-007`.

3. `O-004` declare the artifact at `implement-feature/quality-review`
- Benefits: the phase's prose output, recorded by `F-024` as "review findings log, verification
  report", is the review output nearest to the workflow the framework actually executes, and its
  owner is the same `omn-dev-2-reviewer` that `O-001` selects.
- Risks: the same frozen-slice membership as `O-003`, through `F-021`.
- Why not selected: eliminated on `C-006` and `C-007`, because editing a frozen-slice member
  changes the context digest that committed runs' verification reproduces.

4. `O-005` declare routing in a new machine-read emitting-phase field on the `review-package`
   record in `registry/templates.yaml`, leaving every Phase Model unchanged
- Benefits: touches no workflow specification, so no frozen-slice member and no derived edge set
  is affected.
- Risks: `F-003` and `F-004` both read the Phase Model column, so a registry field would not be
  read by either, and `F-010` establishes the record schema carries no such field today.
- Why not selected: eliminated on `C-004`, because it would create a second place where an
  artifact type is declared.

## Consequences

- Positive outcomes expected: the set of contracted artifact types that no Phase Model Output
  Artifact column names becomes empty, and `F-003`'s coverage proof counts `review-package.md`
  as routed with a validator present. The artifact is declared against the phase whose owning
  role holds the artifact's own registered capabilities, so no agent is assigned an artifact its
  contract forbids producing. Under `F-015` and `A-003` the derived edge set of the affected
  workflow is unchanged.
- Tradeoffs accepted: `C-001` permits one phase, so three review-producing phases keep prose
  Output Artifact entries and `F-011`'s statement of the remaining work is only partly
  discharged. The declared emitter's owner holds no registry record (`F-006`), so no run can
  exercise the declaration and `C-012` is satisfied at declaration level only, which `C-010`
  accepts. The benefit of closing gap 7 at the phase that recorded it is forgone.
- Risks introduced: `R-001` an Input entry naming the replaced token changes the derived edge
  set; `R-002` a committed slice contains the edited file; `R-004` the blocked reason for the
  phase changes; `R-005` the blocked-phase count rises; `R-008` the phase gap 7 names remains
  blocked and a reader believes otherwise; `R-010` three review-producing phases keep prose
  outputs.

## Validation Plan

- Metrics to monitor: the routed-artifact coverage result of check `V1`; the blocked-phase count
  reported by the registry coverage proof; the per-phase blocked reason recorded for
  `code-quality-review`; and the derived edge set of the affected workflow, before and after.
- Verification checkpoints: `P-004` records the before-state edge set and every Input entry
  requiring a replacement; `P-005` applies the single-cell declaration; `P-007` confirms exactly
  one routing declaration site; and `P-008` re-runs both coverage proofs and compares all three
  metrics against the recorded before-state.
- Rollback or reversal conditions: reverse if `P-008` shows the blocked-phase count rising, the
  per-phase blocked reason traded, or the derived edge set differing from the after-state
  recorded at `P-004` without an accepted disposition. Reversal restores the prose token in the
  one cell, which returns the coverage result and the edge set to their current values and,
  under `F-022` and `A-001`, affects no run evidence.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
