# Architecture Decision Record: D-002

## Metadata

- ADR ID: D-002
- Title: The review role emits one contract-defined review-result artifact with a per-dimension outcome register
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: runs/inputs/reviewer-agent-feature-request.md; supplied execution plan tasks T-003, T-006, T-007

## Context

Problem statement: the review verdict must be consumable by the delivery and quality roles that
act on it, without a reader reconstructing what was reviewed or what the verdict was, and it
must record an explicit outcome for each declared review dimension. The framework has no
artifact that carries a per-dimension verdict, so the shape, the identifier scheme, and the
rule governing reproduction of reviewed content all have to be fixed before any consumer binds
to them. The business intent leaves the artifact's content beyond the per-dimension outcome
open to the design.

Business and technical constraints: `C-008` requires an explicit recorded outcome for each
declared review dimension. `C-009` requires the artifact to state what was reviewed and the
verdict without reconstruction. `C-013` requires reviewed content reproduced into a durable
artifact to be bounded by a stated rule. `C-016` requires two runs over identical inputs and an
identical context snapshot to produce an identical section set and identical finding
identifiers. `C-001` forbids a second authority for the same identity metadata. `C-004`
requires a registry record's specification path to resolve to an existing file.

Current architecture baseline: `F-016` establishes that `registry/templates.yaml` holds three
records, `execution-plan`, `technical-design` at version 1.1.0, and
`architecture-decision-record`, and no record for a review-result artifact. `F-029` establishes
the framework's pattern of one registered template record per artifact contract, each naming
its producing role and owning domain. `F-017` establishes the template record schema and its
validation rules. `F-022` establishes that the runtime validation engine currently covers one
artifact type.

## Decision

Selected option: `O-001`.

Decision statement: the review role emits exactly one primary deliverable, a review-result
artifact whose structure is fixed by the role's own output contract and rendered from a new
template at `templates/review-result.md`, registered as its own record in
`registry/templates.yaml`. The contract requires an explicit recorded outcome for every
declared review dimension, so a dimension cannot be silently absent from an emitted result. It
fixes a finding identifier scheme so that repeated runs over identical inputs assign identical
identifiers. It states a bounded-reproduction rule for reviewed content: a finding cites
location and describes the defect, and reproduces reviewed content only as far as
identification requires. Validation coverage for the artifact extends the existing validation
engine rather than introducing a second validation path.

Scope of impact: `M-006` and `M-007` directly, with downstream effect on `M-001`, because the
agent record declares a data dependency on the template record, and on `M-002`, because the
contract module set binds to the artifact shape.

## Alternatives Considered

Alternatives are carried from the package evaluation table in section 5.2, stated here in terms
of what each rejected option would have meant for the review-result artifact contract.

1. `O-003` migrate the existing review contract in place and register it under its current identifier
- Benefits: the artifact contract would attach to an identifier every framework document
  already resolves, so the template record would need no reference migration; the highest reuse
  leverage of any option.
- Risks: none specific to the artifact, which is why this option is the closest alternative on
  this decision. The artifact contract under `O-003` is the same contract, differing only in
  the producing identity it names.
- Why not selected: eliminated at the package level on `C-007`, because it registers a role
  that already exists rather than adding one. The reading of `S-001` behind `C-007` is routed
  as `Q-001`; if it is answered in favour of `O-003`, this artifact contract survives unchanged
  and only its producer field differs.

2. `O-002` split ownership, with the new identity holding plan and design review plus framework governance and the existing role retaining code-change review
- Benefits: each role's artifact would be narrower, covering only the dimensions that role owns.
- Risks: a governed change would carry its verdict across two artifacts produced by two roles,
  so no single record states what was reviewed and what the verdict was.
- Why not selected: eliminated at the package level on `C-001` and `C-006`, and it defeats
  `C-009` directly, because a reader would have to assemble the verdict from two artifacts, and
  `C-008`, because neither artifact would carry an outcome for all five dimensions.

3. `O-004` coexistence, with the new identity Primary for both review capabilities while the existing role retains its Primary rows unchanged
- Benefits: no reference migration would touch the template record.
- Risks: two Primary owners could each emit a review result for the same governed change, so a
  change could carry two verdicts with no rule for which one governs.
- Why not selected: eliminated at the package level on `C-001`, `C-003`, and `C-006`. For this
  decision specifically, it makes the recorded verdict ambiguous, which is the outcome `S-008`
  and `C-009` exist to prevent.

The alternative of reusing an existing registered template rather than defining a new one is
recorded where the output contract places it, in the reuse survey in section 7 of the design
package, as the `rejected` row that licenses the new structure at `M-006`.

## Consequences

Positive outcomes expected: an emitted review result carries a verdict for every declared
dimension, is discoverable through the template registry on the same terms as every other
framework artifact, and is validatable by an extension of the existing validation engine rather
than by a second mechanism.

Tradeoffs accepted: the artifact contract is fixed before the dimension set is confirmed, so
the contract inherits `A-002`. If the confirmed dimension set differs from the five named, the
per-dimension outcome register changes after the contract is otherwise complete. The sequencing
places the requester confirmation at `P-002` ahead of the contract at `P-005` precisely to keep
that window as short as possible, but it does not close it, because the confirmation is owned
by another role.

Risks introduced: `R-005`, the confirmed dimension set differing from the five named; `R-008`,
the contract emitted without the bounded-reproduction rule; `R-012`, a finding identifier scheme
that is not stable across runs; `R-002`, the agent record registered before the template record
so its declared dependency does not resolve.

## Validation Plan

Metrics to monitor: the proportion of emitted review results that carry an explicit recorded
outcome for every declared dimension, which must be total; and the count of findings whose
reproduced content exceeds the bounded-reproduction rule, which must be zero.

Verification checkpoints: `P-005`, the artifact contract is defined with the per-dimension
outcome requirement, the finding identifier scheme, the severity model, and the
bounded-reproduction rule; `P-007`, the template exists at that shape; `P-008`, the template
record is registered and its specification path resolves; `P-010`, validation coverage
evidences artifact conformance, repeat-run identity of structure and finding identifiers, and
adherence to the bounded-reproduction rule.

Rollback or reversal conditions: if the confirmed dimension set or the reviewed-artifact set
materially changes the contract after registration, or if repeat-run identifier stability
cannot be evidenced at `P-010`, remove the template record and the template. The agent record's
declared data dependency then no longer resolves, so reversal of this decision requires
reversal of the registration at `P-011` in the same step, which is the inverse of the ordering
`P-008` before `P-011` establishes.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
