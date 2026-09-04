## Metadata

- ADR ID: D-003
- Title: The Phase Model Output Artifact column is the sole authority for artifact routing
- Date: 2026-08-18
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: FC-001; execution plan task T-006

## Context

- Problem statement: the supplied execution plan asks that the artifact type's registry record
  and the Phase Model declarations name an identical set of emitting phases. That request
  presumes the registry record declares emitting phases. `F-010` establishes that the template
  registry record schema carries no such field, and `F-009` establishes that the `review-package`
  record's description is prose stating that one artifact type serves the `quality-review` phase
  of implement-feature, both review-pull-request assessments, and the `artifact-packaging` phase
  of release. Under `D-001` exactly one of those phases will declare the artifact. Unless the
  status of that prose is decided, an alignment performed on the registry side would turn a
  prose description into a routing declaration, and the framework would then carry two places
  where an artifact type's routing is declared.
- Business and technical constraints: `C-004` states that the framework's discovery registries
  are single-authority and that this change adds no second place where an artifact type is
  declared. `C-001` permits exactly one declaring phase, which is what creates the divergence
  from the record's four-phase description. `C-007` requires registry coverage and validator
  coverage to still verify after the change.
- Current architecture baseline: `F-003` establishes that the coverage proof reads the Output
  Artifact column of every active Phase Model and treats a token ending in `.md` as a routed
  artifact type. `F-004` establishes that the runtime resolves a phase's declared artifact from
  the same column, against the owning agent's manifest outputs and the `VALIDATORS` map. `F-007`
  and `F-015` establish that the runtime derives sequencing from the Input and Output Artifact
  columns. Both mechanisms the framework actually executes read the Phase Model column, and
  neither reads the registry description, which `F-010` establishes has no field for them to
  read. `M-006` is the record in question and `M-001` is the declaration site.

## Decision

- Selected option: `O-001`.
- Decision statement: the Output Artifact column of a `## Phase Model` table is the sole
  authority for which phase emits which artifact type. The artifact-type record in
  `registry/templates.yaml` declares artifact identity, meaning identifier, version, status,
  specification path, and capabilities, and describes intended service scope; it does not
  declare routing, and it is not aligned to the set of phases that declare the artifact. The
  alignment the execution plan asks for is therefore satisfied by confirming that exactly one
  routing declaration site exists, not by editing the registry record to name emitting phases.
- Scope of impact: `M-006` is recorded as `no-change-verified`, because the `review-package`
  record does not change and its four-phase description continues to state service scope rather
  than routing. `M-001` remains the only routing declaration this change touches.

## Alternatives Considered

1. `O-005` declare routing by adding a machine-read emitting-phase field to the artifact-type
   record, leaving every Phase Model unchanged
- Benefits: routing would be readable from one registry file without opening a workflow
  specification, and no workflow file, frozen-slice member, or derived edge set would be touched.
- Risks: `F-003` and `F-004` both read the Phase Model column and neither reads the registry
  record, so the field would declare routing that nothing enforces, and `F-010` shows the schema
  would have to be extended to hold it.
- Why not selected: eliminated on `C-004`. It is the option this record exists to rule out, and
  ruling it out is what makes the alignment request answerable.

2. `O-002` declare the artifact at `review-pull-request/structural-compliance`
- Benefits: would place the declaration at the phase the recorded gap names.
- Risks: the routing-authority question is identical under it, so it resolves nothing here, and
  it carries the agent-contract cost recorded in `D-002`.
- Why not selected: it loses the reuse-leverage criterion in the package evaluation table.

3. `O-003` declare the artifact in all four phases the record's description names
- Benefits: the record's description and the declaring phase set would coincide, so the
  divergence this record addresses would not arise.
- Risks: `F-021` places one affected workflow file inside a frozen context slice, and the
  coincidence would be accidental rather than governed, so a later description edit would
  silently reintroduce the divergence.
- Why not selected: eliminated on `C-001`, and additionally on `C-006` and `C-007`.

4. `O-004` declare the artifact at `implement-feature/quality-review`
- Benefits: none specific to the routing-authority question, which is unchanged under it.
- Risks: the same frozen-slice membership as `O-003`, through `F-021`.
- Why not selected: eliminated on `C-006` and `C-007`.

## Consequences

- Positive outcomes expected: one authority answers the question of which phase emits an
  artifact type, and it is the authority the runtime already reads. The execution plan's
  alignment objective becomes decidable, because it is a confirmation that a single declaration
  site exists rather than an edit that would create a second one. A future artifact type is
  routed the same way, without a registry schema extension.
- Tradeoffs accepted: the `review-package` record's description will name four phases while one
  declares the artifact, and that prose will read as a routing statement to a reader who does
  not know this decision. The framework gains no single file from which every artifact type's
  emitting phases can be read; that view is assembled from the Phase Model tables, as `F-003`
  already assembles it.
- Risks introduced: `R-007` a reader treats the registry description as a routing declaration
  and creates the second authority `C-004` forbids.

## Validation Plan

- Metrics to monitor: the number of places in the framework that declare which phase emits
  `review-package.md`, which must be one; and the registry coverage and validator coverage
  results, which `C-007` requires to still verify.
- Verification checkpoints: `P-007` confirms that the routed declaration and the artifact-type
  record declare routing in exactly one place, and `P-008` re-runs the coverage proofs after the
  declaration and compares them to the recorded before-state.
- Rollback or reversal conditions: reverse if the owners answering `Q-006` decide the registry
  record must name its emitting phases, in which case `C-004` requires an explicit relaxation
  and the routing authority must be redefined for every artifact type at once rather than for
  this one. Reverse also if a coverage proof is found to read the registry description as
  routing, because the premise that only the Phase Model column is read would then be false and
  `F-003` would need restating.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
