# Architecture Decision Record: D-003

## Metadata

- ADR ID: D-003
- Title: Define the review outcome as a new registered artifact rather than rendering it into an existing registered template
- Date: 2026-08-18
- Status: Proposed
- Owners: architect (producer), omn-tech-lead (accepting Design Gate owner)
- Related Work Items: run-c5a8d50d3238; supplied execution plan tasks `T-010`, `T-011`, `T-013`

## Context

- Problem statement: the reviewer's single deliverable must carry an explicit result for each
  of the five declared review dimensions and be consumable by the delivery and quality roles
  that act on it, without a reader reconstructing what was reviewed or what the verdict was.
  The framework can either bind that deliverable to a template it already registers or
  register a new one, and the choice determines whether one registered template ends up with
  two producers and two contracts.
- Business and technical constraints: `C-007` requires an explicit result for each of the
  five named dimensions. `C-010` prohibits reproducing restricted content found in reviewed
  material. `C-001` forbids a second authority for the same identity metadata, which applies
  at the artifact level as much as at the agent level. `C-002` makes a registration record a
  contract surface. `C-015` requires a registered validator before the producing phase can
  pass `G1-CAPABILITY`. `C-013` declines a numeric coverage target.
- Current architecture baseline: `F-015` establishes that the template registry holds three
  active records — the execution plan, the technical design, and the architecture decision
  record — and no record covering a review outcome. `F-012` establishes that the Validation
  Engine covers two artifact types through per-artifact validators. `F-014` establishes that
  there is no retry and no recovery pass, so an artifact that fails validation blocks.

## Decision

- Selected option: `O-001`.
- Decision statement: the review outcome is a new registered artifact with a fixed section
  set providing exactly one explicit result position per declared review dimension. Each
  finding carries a severity and the identifier of the reviewed element, and the structure
  provides no position for verbatim reviewed content, so the prohibition in `C-010` is
  enforced by the shape of the artifact rather than by the producer's discretion. The
  artifact is discovered through the existing template registry, not through a new index.
- Scope of impact: `M-009` the new template and `M-010` its registry record. `M-001` binds to
  it as the reviewer's declared output. `M-006` names it as the phase's Output Artifact,
  `M-007` declares it as a workflow dependency, and `M-011` is the registered validator that
  makes it checkable.

## Alternatives Considered

1. `O-002` new `reviewer` agent plus a new review phase, with the same new artifact
- Benefits: identical artifact structure; the phase change would not touch a live row.
- Risks: two review-bearing phases in one workflow make two roles accountable for the same
  artifacts.
- Why not selected: violates `C-018`. It agrees with the selected option that a new artifact
  is needed, and loses on the routing question recorded in `D-002`.

2. `O-003` migrate the existing review owner into the runtime module-set pattern
- Benefits: the existing phase already names a review findings log and a verification report,
  so a migrated role could bind to whatever those become.
- Risks: neither is a registered artifact today, so binding to them would leave the
  deliverable undefined rather than reusing a definition.
- Why not selected: violates `C-017`.

3. `O-004` full supersession
- Benefits: agrees with the selected option on the artifact; the same new template and
  registry record would be created.
- Risks: the artifact would have to serve gates in three workflows at once, widening its
  contract before it has been exercised in one.
- Why not selected: it loses on the ownership question recorded in `D-001`. It is the
  highest-scoring rejected alternative.

4. `O-005` express review as a capability of the existing `architect` agent
- Benefits: the technical design template is already registered and already carries a
  structured findings-shaped surface, so the highest reuse leverage of any option.
- Risks: one registered template would acquire two producers and two contracts, and the
  agent would produce evidence about its own output.
- Why not selected: violates `C-005`, `C-014`, and `C-017`. Its reuse advantage is exactly
  the single-authority defect `C-001` names, expressed at the artifact level.

The reuse survey additionally rejected each of the three registered templates individually.
Each is bound to a different producer and a different section contract — a design package, a
plan, and one decision — and none carries a per-dimension result position. That rejection is
what licenses new structure here; without it, a new template would be new structure proposed
over an unexamined component.

## Consequences

- Positive outcomes expected: an emitted outcome carries a result for every declared
  dimension by construction rather than by convention, so `S-014` is satisfied structurally;
  the outcome is consumable without reconstruction because each finding names the reviewed
  element and its severity; and coverage becomes measurable as a proportion from the run
  evidence, which is what `C-013` asks for without setting a level.
- Tradeoffs accepted: the framework gains a fourth registered artifact type and a third
  validator, which is real surface area. The alternative that avoids it gives one registered
  template two producers, which the single-authority principle rules out, so the surface area
  is accepted rather than designed away. A second tradeoff: fixing five result positions
  makes the structure rigid, so adding a sixth dimension later is a template and validator
  change, not a content change.
- Risks introduced: `R-004` the template referenced before it is registered, which enforced
  dependency resolution rejects; `R-006` restricted content reproduced in an outcome;
  `R-012` a dimension beyond the five proving to be required, which expands the contract, the
  template, and the validation coverage together; `R-016` the framework-governance dimension
  requiring an external policy source; `R-017` records created before the contract is stable.

## Validation Plan

- Metrics to monitor: the count of explicit result positions per emitted outcome against the
  count of declared dimensions; the proportion of findings carrying both a severity and a
  reviewed-element identifier; the count of validation rejections for this artifact type and
  the reason distribution.
- Verification checkpoints: `P-003` fixes the dimension set with recorded exclusions before
  `P-005` writes the contract; `P-005` states the restricted-content prohibition; `P-007`
  registers the template before any record depends on it; `P-012` registers the validator;
  `P-014` verifies conformance coverage including a case with restricted content in the
  reviewed material.
- Rollback or reversal conditions: reverse if `Q-007` establishes that the
  framework-governance dimension needs an external policy source, which changes the declared
  input set the outcome reports against, or if `Q-004` establishes that no validator can be
  registered, which leaves the artifact uncheckable under a runtime with no recovery pass.
  Reversal withdraws the template registry record and the template; nothing else depends on
  them once the workflow record entries are reverted first.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
