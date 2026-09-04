```yaml
plan:
  planId: review-package-routing-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/review-package-routing-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:59644fd3b625988cc30879fe11c2dfcb
  contextDigest: sha256:c02a893250a487966bd7e0b20eb783cd
```

## Executive Summary

The review package artifact type is contracted and validated but is declared as the output of
no workflow phase, so a review verdict reaches a run as prose in an Output Artifact column
rather than as a validated artifact under run evidence. This plan routes that artifact type
into the phases that produce review verdicts, so gate owners and downstream consumers read one
validated record instead of an undeclared prose entry. Success is that every approved
review-producing phase declares the artifact, the artifact type's registry record and the phase
declarations agree, and the phase sequencing the runtime derives from the Input and Output
Artifact columns still resolves. The work decomposes into ten tasks across five execution
waves, beginning with an approval of exactly which phases are review-producing and a
confirmation that the artifact type is already contracted and validated. The highest-impact
risk is `R-003`: if declaring an Output Artifact does not by itself place a validated artifact
under run evidence, the declaration work in `T-003` would not achieve the intended outcome and
further work outside this task set is required. Plan status is complete; `A-001` through
`A-005` each have a confirming or deciding task ahead of the work that depends on them, and
`Q-001` through `Q-005` are recorded as non-blocking with named owners.

## Business Objectives

- A review verdict is retrievable as a validated artifact under run evidence rather than as a
  prose entry, measured as the proportion of approved review-producing phases whose verdict is
  carried by a validated artifact, with a target of all of them. Traces to `S-004`, `S-005`.
- The framework carries no active contracted artifact type that no routed phase emits, measured
  as the count of active artifact type records with no declaring phase, with the review package
  no longer among them. Traces to `S-002`, `S-003`.
- Consumers of the review lifecycle read one review output form across review-producing phases,
  measured as the number of distinct declared review output forms across the approved phase
  set, with a target of one. Traces to `S-001`.

## Technical Objectives

- Each approved review-producing phase declares the review package artifact type as its Output
  Artifact in its Phase Model table, verified by inspecting those tables against the approved
  phase list. Traces to business objective 2.
- A review package recorded by an approved phase conforms to the artifact type's contracted
  structure and is rejected when it does not, verified by the recorded result of the validation
  coverage. Traces to business objective 1 and `A-002`.
- The phase edges the runtime derives from the Input and Output Artifact columns of the affected
  workflows continue to resolve after the change, verified by comparing the derived edges to the
  recorded after-state. Traces to business objective 2 and `A-005`.
- The review verdict is addressable at a declared artifact location under the run's evidence
  rather than only in workflow prose, verified by the recorded declaration mechanism. Traces to
  business objective 1 and `A-003`.

## Scope

### In Scope

- Approving which workflow phases are review-producing and must emit the review package
  (`S-001`, `S-004`). Covered by `T-001`.
- Confirming that the artifact type is already contracted and validated (`S-002`). Covered by
  `T-005`.
- Deciding how a declared Output Artifact becomes validated run evidence (`S-004`, `S-005`).
  Covered by `T-008`.
- Deciding the disposition of the prose outputs the review package supersedes (`S-005`).
  Covered by `T-010`.
- Determining and preserving the phase sequencing derived from the Input and Output Artifact
  columns (`S-001`). Covered by `T-002` and `T-004`.
- Declaring the artifact in the approved phases' Phase Model tables and re-pointing the
  consuming Input entries (`S-001`, `S-003`, `S-004`). Covered by `T-003`.
- Aligning the artifact type's registry record with the declared emitting phases (`S-002`,
  `S-003`). Covered by `T-006`.
- Validation coverage for the routed artifact (`S-002`, `S-005`). Covered by `T-007`.
- Documentation of the review output form for gate owners (`S-004`, `S-005`). Covered by
  `T-009`.

### Out of Scope

- Changing the structure of the review package artifact type itself. Excluded because `S-002`
  states the type is already contracted and validated, and no supplied statement requests a
  structural change.
- Producing an actual review verdict or performing any review. Excluded because the request
  routes an artifact type into a lifecycle; it does not commission a review.
- Registering owner agents for the review-producing phases, or otherwise making those phases
  runtime-executable. Excluded because no supplied statement requests capability resolution.
- Changing gate names or gate ownership for the affected workflows. Excluded because no
  supplied statement requests a gate change.
- Routing any artifact type other than the review package. Excluded because the request names
  one artifact type.

### Deferred

- End-to-end demonstration that an executed review-producing phase emits a validated review
  package. Enters scope once an owner agent for at least one approved review-producing phase
  holds a registry record, so that the phase no longer blocks at capability resolution.
- Applying the same routing treatment to other contracted artifact types that no phase emits.
  Enters scope when a statement identifies another such artifact type.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | "The review lifecycle" means the phases that the review package artifact type's registry record already names as its consumers, and no others | `S-004` | The approved phase set changes; `T-003` changes a different set of phases, the edge set in `T-002` changes, and `T-006` becomes a registry correction rather than an alignment | omn-product-owner |
| A-002 | The review package artifact type already carries a structural contract and a validation path, so no artifact-contract authoring is required | `S-002` | A contract-definition outcome and a validation-path outcome are added ahead of `T-007`, and technical objective 2 is unmet until they exist | architect |
| A-003 | Declaring an artifact in a phase's Output Artifact column is the mechanism by which that phase places the artifact under run evidence | plan-wide | An additional change beyond the Phase Model declaration is required; `T-003` alone does not achieve business objective 1 and further tasks are added | architect |
| A-004 | The prose Output Artifact entries of the approved phases are superseded by the review package rather than retained alongside it | `S-005` | Affected phases declare both forms, business objective 3 is unmet for those phases, and `T-009` must document two coexisting forms | omn-product-owner |
| A-005 | Every phase whose Input column names a superseded output can be re-pointed to the review package without changing that phase's own outcome | plan-wide | `T-003` grows to cover an outcome change in a consuming phase, and the after-state recorded in `T-002` and checked in `T-004` changes | architect |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | `T-001` approves a review-producing phase set that differs from the set the artifact type's registry record names | The declaration scope of `T-003`, the edge set of `T-002`, and the alignment target of `T-006` all change | medium | T-001, T-002, T-003, T-006 | `T-001` approves the phase set before any declaration work begins | omn-product-owner |
| R-002 | requirement | `T-010` records that a prose output is retained alongside the review package for one or more phases | The review verdict is not the single validated record for those phases and business objective 3 is unmet for them | medium | T-003, T-009, T-010 | `T-010` requires a named consumer for every retained prose output | omn-product-owner |
| R-003 | technical | `T-008` finds that placing an artifact under run evidence requires a change beyond the Phase Model declaration | `T-003` alone does not achieve business objective 1, and work outside the current task set is required | medium | T-003, T-008 | `T-008` names any additional required change as a distinct outcome before `T-003` starts | architect |
| R-004 | technical | `T-005` identifies no validation path for the artifact type | The emitted package is not a validated artifact, technical objective 2 is unmet, and contract work precedes `T-007` | low | T-005, T-007 | `T-005` records the absence as a gap carried by `Q-002` | architect |
| R-005 | dependency | `T-002` identifies a consuming phase whose Input entry names a superseded output it materially depends on | Derived sequencing changes, `T-003` scope grows, and the after-state checked by `T-004` changes | medium | T-002, T-003, T-004 | `T-002` records every affected consumer with its required replacement Input entry before `T-003` starts | architect |
| R-006 | security | An approved review-producing phase records findings that quote restricted content into the review package | Restricted content becomes durable run evidence rather than transient review prose | low | T-007, T-009 | `Q-005` establishes whether the artifact type may carry restricted content; the answer determines whether further coverage is required | omn-dev-2-reviewer |
| R-007 | operational | A run reaches an approved review-producing phase and blocks at capability resolution because that phase's owner agent holds no registry record | The routed artifact cannot be observed in an executed run, so plan acceptance rests on declaration-level and coverage-level evidence | high | T-004, T-007 | `T-007` states the expected run outcome for a phase blocked at capability resolution, and the end-to-end demonstration is deferred under `Q-004` | omn-tech-lead |
| R-008 | delivery | `T-003` changes some but not all approved phases, or `T-006` is not applied | The artifact type's registry record and the Phase Model tables disagree about which phases emit the artifact | medium | T-003, T-006 | `T-006` requires the registry record and the Phase Model declarations to name the same phase set | omn-tech-lead |

## Task Breakdown

### T-001 Approve the set of review-producing phases that must emit the review package

- Owner: omn-product-owner
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-001, S-004, A-001
- Status: ready
- Description: An approved list exists of the workflow phases that must declare the review
  package as their Output Artifact, and the review-adjacent phases considered and excluded are
  recorded as non-goals.
- Acceptance Criteria:
  - The approved list names each phase by its canonical phase identifier together with the
    workflow that declares it
  - Every review-adjacent phase considered and excluded is recorded with its exclusion reason
- Gate: Scope Gate

### T-002 Determine the sequencing impact of the declaration change

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-001, T-010
- Traces to: S-001, A-005
- Status: ready
- Description: For each affected workflow, the phase edges the runtime derives from the Input
  and Output Artifact columns are recorded in a before state and an intended after state, and
  every phase whose Input entry must be re-pointed is identified.
- Acceptance Criteria:
  - Each affected workflow carries a recorded before-state and after-state edge set
  - Every phase whose Input entry names a superseded output is listed with the replacement
    Input entry it requires
  - Any consuming phase that cannot be re-pointed without changing its own outcome is recorded
    against `A-005`
- Gate: Design Gate

### T-003 Declare the review package as the Output Artifact of each approved phase

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-001, T-002, T-008, T-010
- Traces to: S-001, S-003, S-004, A-003, A-004, A-005
- Status: assumption-dependent
- Description: Every phase in the approved list names the review package as its Output Artifact
  in its Phase Model row, every consuming Input entry identified in `T-002` names it, and the
  superseded prose entries are handled as `T-010` decided.
- Acceptance Criteria:
  - Every phase in the approved list names the review package in its Output Artifact entry
  - Every Input entry identified in `T-002` names the review package
  - Superseded prose entries are absent, or present with the justification `T-010` recorded
  - No phase outside the approved list has a changed Input or Output Artifact entry
- Gate: Review Gate

### T-004 Verify the derived sequencing of the affected workflows

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-002, T-003
- Traces to: S-001, A-005
- Status: ready
- Description: Each affected workflow resolves its Phase Model after the change, and the edges
  the runtime derives match the after-state recorded in `T-002`.
- Acceptance Criteria:
  - Each affected workflow resolves its Phase Model without a resolution error
  - The derived edge set matches the `T-002` after-state, and every difference is recorded with
    a disposition
- Gate: Verification Gate

### T-005 Confirm that the review package artifact type is contracted and validated

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-002, A-002
- Status: ready
- Description: The claim that the artifact type is contracted and validated is confirmed
  against the framework as it stands, or the part of the claim that does not hold is recorded
  as a gap.
- Acceptance Criteria:
  - The structural contract for the artifact type is identified by its repository-relative path,
    or its absence is recorded
  - The mechanism that decides conformance is identified, or its absence is recorded as a gap
    carried by `Q-002`
- Gate: Design Gate

### T-006 Align the artifact type's registry record with the declared emitting phases

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-001, T-003
- Traces to: S-002, S-003
- Status: ready
- Description: The review package registry record and the Phase Model declarations name the
  same set of emitting phases.
- Acceptance Criteria:
  - The registry record and the Phase Model declarations name an identical phase set
  - Any difference found is resolved on one side with the reason recorded
- Gate: Review Gate

### T-007 Design validation coverage for the routed review package

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-001, T-005
- Traces to: S-002, S-005
- Status: ready
- Description: Validation coverage exists for a conforming review package, a non-conforming
  review package, and an approved phase that records no package, for every phase in the
  approved list.
- Acceptance Criteria:
  - Coverage addresses a conforming and a non-conforming review package for each approved phase
  - Coverage states the expected run outcome when an approved phase records no package
  - Coverage states the expected run outcome for an approved phase that blocks at capability
    resolution and therefore records nothing
- Gate: Verification Gate

### T-008 Decide how a declared Output Artifact becomes validated run evidence

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-005
- Traces to: S-004, S-005, A-003
- Status: ready
- Description: An approved statement exists of what must be true for a phase's declared Output
  Artifact to be recorded as validated run evidence, and of whether that condition is met by the
  Phase Model declaration alone.
- Acceptance Criteria:
  - The condition is stated by reference to a phase that already records a validated artifact
  - The statement says whether the Phase Model declaration alone satisfies the condition for the
    approved review-producing phases
  - Any further change required is named as a distinct outcome rather than assumed absent
- Gate: Design Gate

### T-009 Document the review output form for gate owners

- Owner: omn-documentation
- Complexity: S (confidence: medium)
- Depends on: T-003, T-010
- Traces to: S-004, S-005, A-004
- Status: ready
- Description: The review lifecycle documentation states that a review verdict is carried by the
  review package artifact under run evidence, names the phases that emit it, and states what it
  supersedes.
- Acceptance Criteria:
  - Documentation names each emitting phase and the artifact that carries its verdict
  - Documentation states where a gate owner assessing review evidence locates the verdict
  - Documentation states which prose outputs were superseded and which were retained
- Gate: Closure Gate

### T-010 Decide the disposition of the superseded prose outputs

- Owner: omn-product-owner
- Complexity: S (confidence: medium)
- Depends on: T-001
- Traces to: S-005, A-004
- Status: ready
- Description: For each phase in the approved list, a decision is recorded on whether the
  existing prose Output Artifact entries are replaced by the review package or retained
  alongside it.
- Acceptance Criteria:
  - Every phase in the approved list carries exactly one recorded disposition
  - Every retained prose output is justified by a named consumer
- Gate: Scope Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | decision-gate | The sequencing impact is derived only over the phases the approved list names |
| T-001 | T-003 | decision-gate | The phases whose Output Artifact entry changes are exactly the approved list |
| T-001 | T-006 | decision-gate | The registry record is aligned to the approved phase set |
| T-001 | T-007 | decision-gate | Coverage enumerates the approved phase set |
| T-001 | T-010 | decision-gate | A disposition is decided per phase in the approved list |
| T-002 | T-003 | produces-consumes | `T-003` applies the Input re-pointing list `T-002` produces |
| T-002 | T-004 | produces-consumes | `T-004` compares the derived edges against the after-state `T-002` records |
| T-003 | T-004 | verification | `T-004` validates the declarations `T-003` produced |
| T-003 | T-006 | produces-consumes | The registry record is aligned to the declarations `T-003` produced |
| T-003 | T-009 | produces-consumes | Documentation describes the declarations `T-003` produced |
| T-005 | T-007 | contract | Coverage binds to the structural contract and conformance mechanism `T-005` confirms |
| T-005 | T-008 | contract | The evidence condition is stated against the artifact contract `T-005` confirms |
| T-008 | T-003 | decision-gate | What each declaration must satisfy changes with the recorded evidence condition |
| T-010 | T-002 | decision-gate | The after-state edge set depends on whether prose outputs are retained |
| T-010 | T-003 | decision-gate | Whether prose entries are removed or retained changes the declared entries |
| T-010 | T-009 | decision-gate | Documentation states which prose outputs were superseded |

### 8.2 External Dependencies

None identified. Every prerequisite this plan depends on is owned by an agent inside the
framework agent set. The registration of owner agents for the review-producing phases is
recorded as deferred scope and as `R-007`, not as a prerequisite that blocks a listed task,
because every listed task completes at declaration, coverage, or documentation level.

### 8.3 Implementation Order

- Wave 1: T-001, T-005
- Wave 2: T-007, T-008, T-010
- Wave 3: T-002
- Wave 4: T-003
- Wave 5: T-004, T-006, T-009

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because the plan delivers new framework functionality with an approval decision, a
design decision, a declaration change, verification, and documentation, rather than restoring
behavior, preserving behavior under internal change, or reducing decision uncertainty.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | T-001, T-010 |
| `execution-planning` | plan handoff, this artifact |
| `solution-design-and-risk-assessment` | T-002, T-005, T-008 |
| `implementation` | T-003, T-006 |
| `quality-review` | T-004, T-007 |
| `documentation-and-release-handoff` | T-009 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| scope-definition | T-001, T-010 | omn-product-owner | Primary |
| acceptance-authority | T-001, T-010 | omn-product-owner | Primary |
| architecture-analysis | T-005, T-008 | architect | Primary |
| impact-analysis | T-002 | architect | Primary |
| sequencing-guidance | T-002 | architect | Primary |
| technical-approach-definition | T-008 | architect | Primary |
| implementation-delivery | T-003, T-006 | omn-dev-1-implement | Primary |
| validation-design | T-007 | omn-qa | Primary |
| quality-verification | T-004 | omn-qa | Primary |
| documentation | T-009 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S02 | business/domain-modeling.md | T-001, T-010 | Primary |
| S01 | architecture/clean-architecture-checklist.md | T-002, T-005, T-008 | Primary |
| S07 | testing/testing-strategy.md | T-004, T-007 | Primary |
| S09 | security/secure-engineering.md | T-007 | Secondary |
| S10 | git/git-collaboration.md | T-003, T-006, T-009 | Secondary |

## Acceptance Criteria

1. Every phase in the approved review-producing phase list declares the review package as its
   Output Artifact. Verifies business objective 2. Evidence: the approved list from `T-001`
   cross-checked against the declarations assessed at the Review Gate in `T-003`.
2. The condition under which an approved review-producing phase records its verdict as a
   validated artifact under run evidence is stated, and coverage exists that a non-conforming
   package is rejected. Verifies business objective 1. Evidence: the recorded statement from
   `T-008` and the coverage record from `T-007`.
3. The artifact type's registry record and the Phase Model declarations name an identical set
   of emitting phases. Verifies business objective 2. Evidence: the alignment record from
   `T-006`.
4. Each approved review-producing phase declares one review output form, and every retained
   prose output is justified by a named consumer. Verifies business objective 3. Evidence: the
   disposition record from `T-010` and the declarations from `T-003`.
5. Each affected workflow resolves its Phase Model after the change and its derived edges match
   the recorded after-state, so the declared verdict location remains reachable. Verifies
   business objective 1. Evidence: the verification record from `T-004`.
6. A gate owner assessing review evidence can locate the verdict for each emitting phase from
   the documentation alone. Verifies business objective 3. Evidence: the documentation record
   accepted at the Closure Gate in `T-009`.

## Definition of Done

- [ ] All six plan acceptance criteria are verified with recorded evidence
- [ ] Scope, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for `T-001` through `T-010` are satisfied or formally waived
- [ ] `A-001` through `A-005` are confirmed or converted to recorded decisions
- [ ] `R-001` through `R-008` are closed or accepted with named owners
- [ ] `Q-001` through `Q-005` are closed or explicitly accepted with the acceptance recorded
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Does "the review lifecycle" mean exactly the phases the review package registry record names as its consumers, or a different set? | No | omn-product-owner | T-001, T-003 |
| Q-002 | Does a validation path for the review package artifact type exist today, or must one be introduced before the artifact can be called validated? | No | architect | T-005, T-007 |
| Q-003 | Is a Phase Model Output Artifact declaration sufficient for the artifact to be recorded under run evidence, or is a further change required? | No | architect | T-003, T-008 |
| Q-004 | Can an emitted review package be demonstrated end to end while the review-producing phases block at capability resolution, or is declaration-level evidence accepted for closure? | No | omn-tech-lead | T-004, T-007 |
| Q-005 | May a review package carry restricted content, and if so what must not be recorded into durable run evidence? | No | omn-dev-2-reviewer | T-007, T-009 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 | T-001, T-002, T-003, T-004 |
| S-002 | T-005, T-006, T-007, A-002, Q-002 |
| S-003 | T-003, T-006 |
| S-004 | T-001, T-003, T-008, T-009, A-001, Q-001 |
| S-005 | T-007, T-008, T-009, T-010, A-004 |
