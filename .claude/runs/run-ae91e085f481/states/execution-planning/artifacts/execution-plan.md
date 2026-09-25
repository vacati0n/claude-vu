# Execution Plan — Minimum Necessary Change policy

```yaml
plan:
  planId: SCOPE-2026-0007-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/mnc-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:0089f08e0f80fccd37040a21394244d4
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
```

## Executive Summary

This plan embeds a single necessity-and-reuse standard into the framework's existing
architect, implementer, and reviewer contracts so that design, implementation, and review
already understand the problem before choosing the simplest solution that satisfies it,
without adding any new agent, phase, gate, command, or runtime mechanism. The work
decomposes into fourteen tasks across five execution waves, beginning with the architect's
selection of an existing file to carry the standard. Success is a standard already
reachable by all seven named phases, an updated reuse-survey, route-selection,
safety-floor, and review procedure, unchanged framework verifier and test-suite baselines,
and a reported instruction-byte delta per module set, all closed through a change proposal
and a release-checklist run. The highest-impact risk is `R-004`: one or more of the seven
phases may have no existing loading path that reaches it without a runtime change, which
the excluded scope forbids. Two should-have items carried from the accepted scope
definition — recording a new dependency as architecture-significant, and incrementing the
carrier skill's recorded version — are included at reduced priority, conditioned on the
carrier-file decision. Plan status is complete; two non-blocking open questions remain, for
the requester and for the tech lead.

## Business Objectives

- Reduce unnecessary engineering effort, tokens, review time, and defect surface spent
  building what nothing requires, measured by the reported instruction-byte delta per
  module set and by every framework verifier and the test suite remaining at baseline.
  Traces to `S-001`, `S-005`, `S-017`.
- Give a reviewer a named, written standard to raise over-engineering as a finding,
  measured by the reviewer's procedure applying all seven questions to every change review
  and never demanding a line-count reduction. Traces to `S-007`, `S-015`.
- Preserve required safety, correctness, and protection levels while reducing unnecessary
  code, so that no simplification removes or weakens validation, error handling,
  authorization, audit, accessibility, observability, data integrity, or the tests that
  prove the change, measured by the implementer's self-check blocking any safety-floor
  removal and by the reviewer classifying any safety-floor breach as a correctness or
  security finding. Traces to `S-006`.

## Technical Objectives

- The architect, implementer, and reviewer contracts each carry the shared standard,
  reachable by all seven named phases without a runtime change, verified by the `T-009`
  baseline verification and by inspection of each phase's resolved skill bindings or
  context slice. Traces to business objective 1, `S-012`.
- The architect's reuse survey evaluates existing components, the standard library, native
  platform capability, and installed dependencies for every required capability, verified
  by text review of the updated procedure. Traces to business objective 1, `S-013`.
- The implementer selects an implementation route by the ladder and records the justifying
  rung without a new report field, verified by text review of the updated procedure and the
  implementation-report validator's unchanged field set. Traces to business objective 1,
  `S-014`.
- The implementer's self-check blocks any removal or weakening of a safety-floor item,
  verified by text review of the updated self-check. Traces to business objective 3,
  `S-006`.
- The reviewer applies the seven review questions to every change review with findings
  mapped to the existing severity categories, verified by text review of the updated
  procedure. Traces to business objectives 2 and 3, `S-015`.
- Every framework verifier, the test suite, and the component counts remain at their
  recorded baseline, and the runtime module stays byte-identical to it, verified by the
  `T-009` comparison against the `T-007` snapshot. Traces to business objectives 1 and 3,
  `S-016`, `S-017`.

## Scope

### In Scope

- One written standard stating the ladder, the minimum-necessary-change definition, the
  safety floor, and the seven review questions, carried by an existing file (`S-001`,
  `S-003`, `S-004`, `S-005`, `S-006`, `S-007`, `S-012`) — `T-001`, `T-002`
- The standard reachable by the design, implementation, refactor-implementation,
  quality-review, code-quality-review, structural-compliance, and repository-quality-scan
  phases without a runtime change (`S-002`, `S-011`, `S-012`) — `T-001`
- An extended architect reuse-survey procedure and self-check (`S-013`) — `T-003`
- An extended implementer route-selection procedure recording the justifying rung in the
  existing `Approach taken` field (`S-014`) — `T-004`
- An extended implementer safety-floor self-check (`S-006`, `S-014`) — `T-005`
- An extended reviewer procedure applying the seven review questions (`S-007`, `S-015`) —
  `T-006`
- A pre-change baseline snapshot and a post-change verification of every framework
  verifier, the test suite, and the component counts (`S-016`, `S-017`) — `T-007`, `T-009`
- A reported instruction-byte delta per edited module set and for the standard (`S-017`) —
  `T-008`
- A refreshed packaging mirror so its drift test keeps passing (`S-011`) — `T-010`
- A change proposal linking this run's artifacts and a release-checklist run (`A-008`) —
  `T-011`
- A recorded decision on whether the edits warrant a later contract-version increment,
  carried from the accepted scope definition (`A-008`) — `T-012`
- The should-have items carried from the accepted scope definition: recording a new
  external dependency as architecture-significant, and incrementing the carrier skill's
  recorded version if applicable (`A-007`) — `T-013`, `T-014`

### Out of Scope

- A new agent, skill file, workflow phase, gate, command, template section, validator
  vocabulary, configuration surface, prompt layer, or hook. Excluded because `S-008` names
  each of these as a non-goal and the request requires the behaviour to be carried by the
  existing lifecycle.
- Copying the upstream ruleset's text, intensity modes, comment markers, or commands.
  Excluded because `S-009` states the upstream is a source of the principle only.
- Any change to the runtime module, its version constant, any template, validator,
  workflow specification, manifest, host registration, or gate-matrix row, other than the
  standard's own carrier version identity. Excluded by `S-010` and `S-011`.
- Modification of the planner and product owner contracts. Excluded by `S-018`: their
  existing traceability rules already reject invented scope and undeclared exclusions.
- A line-count reduction target, a maximum size for delivered code, or any review finding
  whose substance is that the change could be shorter. Excluded by `S-006`: line count is
  stated as not a criterion.
- Widening the reviewer's output contract to enable the repository-quality-scan's
  junk-detection lenses on every change review. Excluded because the seven questions route
  into the existing finding categories, and widening the lens set is a separate,
  undeclared change to the reviewer's output contract.
- Raising the contract version of the architect, implementer, or reviewer. Excluded because
  host registrations pin version 1.0.0 and a bump is a governance decision addressed by
  `T-012`, not performed by this plan's edits.
- The outcome-side, task-level before-and-after comparison named in the business intent.
  Excluded because no representative task set, baseline, or owner is supplied; carried as
  `Q-001`.

### Deferred

- None identified. The should-have items carried from the accepted scope definition are
  included in scope above rather than deferred, because their entry condition already
  holds within this run: `T-001`'s carrier-file decision is expected to resolve during this
  plan's execution, not at a later trigger.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | An existing file (agent module or skill file) is suitable to carry the standard without adding a new file | S-002, S-010 | T-001 cannot select a carrier; T-002's target changes or the change widens into an excluded new file | architect |
| A-002 | The carrier file's existing loading path (skill binding, phase-required-skill list, or context-slice membership) already reaches all seven named phases without any change to the runtime | S-011, S-012 | T-001 cannot satisfy phase coverage without touching the runtime, which is excluded | architect |
| A-003 | The implementation report's existing `Approach taken` field has capacity to also carry the ladder-rung justification | S-014 | T-004 cannot record the justification without a template change, which is out of scope | architect |
| A-004 | The reviewer's existing severity table already maps cleanly to a correctness-or-security category and a maintainability-or-architecture category for all seven questions | S-015 | T-006 cannot classify every finding without a severity-table change | omn-dev-2-reviewer |
| A-005 | The verifier, test-suite, and component-count figures recorded as the current baseline remain valid immediately before this plan's edits begin | S-016, S-017 | T-009's comparison is against a stale baseline and cannot attribute a mismatch to this change | omn-tech-lead |
| A-006 | Refreshing the packaging mirror for content-only edits to an existing file is a mechanical sync step | S-011 | T-010 requires more than a mechanical refresh, possibly needing investigation outside planning authority | omn-dev-1-implement |
| A-007 | The two should-have items carried from the accepted scope definition (dependency-significance recording, skill version increment) are intended to flow into this execution plan | plan-wide | T-013 and T-014 are removed from the task set | omn-product-owner |
| A-008 | This change carries two governance obligations from the accepted scope definition into this plan: the self-hosting profile's change-proposal-and-checklist requirement, and the deferred contract-version-increment question for the tech lead to decide | plan-wide | T-011 and T-012 are unnecessary or miscalibrated, and the closure requirements for this run differ | omn-orchestrator, omn-tech-lead |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | T-001's survey of existing files finds none suitable to carry the standard without adding a new file | Violates the no-new-file exclusion, or the standard is under-delivered | low | T-001, T-002 | Escalate to omn-product-owner before authoring if no file qualifies | architect |
| R-002 | requirement | The implementation report's existing `Approach taken` field is already fully occupied by other mandatory content and cannot also carry the rung justification | T-004 cannot satisfy its acceptance criteria without a template change, which is out of scope | low | T-004 | Architect confirms field capacity while authoring T-002 | architect |
| R-003 | requirement | The reviewer's existing severity table has no clean mapping for one or more of the seven review questions | T-006 cannot classify every finding without a severity-table change | low | T-006 | Confirm category coverage before authoring T-006 | omn-dev-2-reviewer |
| R-004 | technical | One or more of the seven named phases has no existing skill-binding or context-slice path that can carry the standard without a runtime change | Phase-coverage acceptance (S-012) cannot be met for that phase without an excluded runtime change | medium | T-001 | T-001 surveys the loading path for every one of the seven phases before selecting a carrier | architect |
| R-005 | technical | The packaging mirror's refresh procedure does not automatically pick up content-only edits to an existing file | The mirror drift test fails, blocking closure | low | T-010 | Run the existing refresh procedure first and escalate only on failure | omn-dev-1-implement |
| R-006 | dependency | An unrelated change lands on the recorded baseline after it was captured, so verifier and test-suite figures no longer match what this plan expects | T-009 cannot cleanly attribute a mismatch to this change | medium | T-007, T-009 | T-007 captures a fresh pre-change snapshot immediately before implementation begins | omn-tech-lead |
| R-007 | security | An implementer or reviewer reads "less code" as license to relax a safety-floor item on a change that also touches a trust boundary, error handling, authorization, audit, accessibility, observability, or data-integrity path | A safety regression ships before the strengthened review catches it | low | T-005, T-006 | T-005 makes safety-floor removal a Blocking self-check failure; T-006 makes it a correctness or security finding | omn-dev-2-reviewer |
| R-008 | delivery | The change proposal is not produced, or the release checklist is not run, before closure is attempted | The Closure Gate cannot pass even though task-level acceptance is met | medium | T-011 | T-011 explicitly packages the change proposal and runs the release-checklist verification | omn-orchestrator |
| R-009 | requirement | omn-product-owner determines on review that the two should-have items carried from the scope definition were not intended to enter this execution plan | T-013 and T-014 are removed from the task set | low | T-013, T-014 | Confirm A-007 with omn-product-owner before design work begins | omn-product-owner |
| R-010 | dependency | omn-tech-lead decides in T-012 that the additive module edits do warrant a contract-version increment | A follow-up governance change is required outside this plan's scope to update host registrations and gate precedent | low | T-012 | T-012 records the decision as accepted and routes any resulting bump to a separate change | omn-tech-lead |

## Task Breakdown

### T-001 Select the standard's carrier file

- Owner: architect
- Complexity: M (confidence: low)
- Depends on: none
- Traces to: S-002, S-010, S-011, S-012, A-001, A-002
- Status: assumption-dependent (A-002)
- Description: An existing file is selected to carry the shared necessity-and-reuse
  standard, and the mechanism by which each of the seven named phases (solution design and
  risk assessment, implementation, refactor implementation, quality review, code quality
  review, structural compliance, repository quality scan) already loads that file — through
  a phase's required-skill list, an agent's declared skill bindings, or a frozen
  context-slice membership — is identified for each phase without any change to the
  runtime module or its version constant.
- Acceptance Criteria:
  - One existing file is named as the carrier, with no new file added to the repository
    tree
  - For each of the seven named phases, the existing loading path that delivers the
    carrier file to that phase is identified and recorded
- Gate: Design Gate

### T-002 Author the necessity-and-reuse standard's content

- Owner: architect
- Complexity: S (confidence: low)
- Depends on: T-001
- Traces to: S-001, S-003, S-004, S-005, S-006, S-007, S-012, A-001
- Status: assumption-dependent (A-001)
- Description: The carrier file selected by T-001 states, in one place, that understanding
  the problem precedes the ladder; the seven rungs in order with the rule to stop at the
  first rung that holds; the minimum-necessary-change definition, with everything outside
  its boundary requiring a recorded justification; the safety floor naming each protected
  concern, with line count stated as not a criterion; and the seven review questions by
  name, with the outcome that the seventh yields a correctness or security finding and the
  other six yield a maintainability or architecture finding.
- Acceptance Criteria:
  - All five required elements are present in the carrier file's text
  - Every rule stated in the accepted scope definition's acceptance criteria for this item
    appears with equal or stronger force, none softened
- Gate: Design Gate

### T-003 Extend the architect's reuse-survey requirements

- Owner: architect
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-013
- Status: ready
- Description: The architect's reuse-survey procedure and self-check require, for every
  required capability, candidates of all four kinds — existing components, the standard
  library, native platform or framework capability, and already-installed dependencies —
  require a stated basis naming which kinds were searched when none is found, and require a
  capability that no accepted statement requires to be recorded as out of scope rather than
  surveyed or designed.
- Acceptance Criteria:
  - The procedure text lists all four candidate kinds for every required capability
  - The self-check fails when a capability search omits a basis statement, or when an
    unrequired capability is designed instead of recorded out of scope
- Gate: Design Gate

### T-004 Extend the implementer's route-selection procedure

- Owner: omn-dev-1-implement
- Complexity: S (confidence: low)
- Depends on: T-002
- Traces to: S-014, A-003
- Status: assumption-dependent (A-003)
- Description: The implementer's procedure requires the route for every change-set entry
  to be chosen by the ladder, stopping at the first rung that holds, and requires the rung
  that justified any new abstraction, file, or dependency to be recorded in the
  implementation report's existing `Approach taken` field, without adding a new field to
  that report.
- Acceptance Criteria:
  - The procedure states the stop-at-first-rung rule for every change-set entry
  - The rung justification is recorded in the existing `Approach taken` field with no new
    report field introduced
- Gate: Review Gate

### T-005 Extend the implementer's safety-floor self-check

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-006, S-014
- Status: ready
- Description: The implementer's self-check carries a Blocking check that fails whenever a
  change removes or weakens input validation at a trust boundary, error handling that
  prevents data loss, authorization or audit paths, accessibility, required observability,
  data integrity, or the tests that prove the change, and it states that justifying every
  new abstraction, file, or dependency is a recorded obligation.
- Acceptance Criteria:
  - The self-check names every safety-floor item and marks its removal or weakening
    Blocking
  - The self-check text does not introduce a line-count threshold as a check condition
- Gate: Review Gate

### T-006 Extend the reviewer's procedure with the seven review questions

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: low)
- Depends on: T-002
- Traces to: S-007, S-015, A-004
- Status: assumption-dependent (A-004)
- Description: The reviewer's procedure requires the seven questions — existence, reuse,
  dependency, abstraction, complexity, scope, safety — to be applied to every change
  review, requires each finding to be measured against the standard rather than against
  line count, and classifies a safety-floor breach as a correctness or security finding and
  the other six as maintainability or architecture findings at the severity the existing
  severity table yields.
- Acceptance Criteria:
  - The procedure names all seven questions and requires them on every review
  - The procedure states that a finding is never that the change could be shorter, and
    that the severity category set is unchanged
- Gate: Review Gate

### T-007 Capture a fresh pre-change baseline snapshot

- Owner: omn-tech-lead
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-016, S-017
- Status: ready
- Description: Every framework verifier, the unit test suite, and the component counts are
  run and recorded as they stand immediately before any module edit in this plan begins, so
  a later comparison is attributable to this change alone.
- Acceptance Criteria:
  - Recorded figures cover registry coverage, phase dispatchability, validators, vertical
    slice, multi-phase, recovery, manifests, the test-suite pass count, and the five
    component counts
  - The snapshot is timestamped and precedes the first edit made under T-003 through T-006
- Gate: Planning Gate

### T-008 Measure added instruction volume per module set

- Owner: omn-tech-lead
- Complexity: S (confidence: high)
- Depends on: T-003, T-004, T-005, T-006
- Traces to: S-017
- Status: ready
- Description: The byte size of each agent module set edited under T-003 through T-006,
  and of the carrier file authored under T-002, is measured before and after, and the
  difference is recorded per module set.
- Acceptance Criteria:
  - A before, after, and delta byte figure is recorded for every edited module set and for
    the carrier file
  - Figures are attributable to a specific file, not aggregated across files
- Gate: Verification Gate

### T-009 Verify framework baselines after the change

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: T-003, T-004, T-005, T-006, T-007
- Traces to: S-016, S-017, A-005
- Status: assumption-dependent (A-005)
- Description: Every framework verifier, the unit test suite, and the component counts are
  re-run after T-003 through T-006 are complete and compared against the snapshot T-007
  recorded, and the runtime module is confirmed byte-identical to its recorded baseline.
- Acceptance Criteria:
  - Every verifier, the test suite, and the component counts match the T-007 snapshot
    exactly
  - The runtime module's digest matches its baseline and its version constant still reads
    its recorded value
- Gate: Verification Gate

### T-010 Refresh the packaging mirror

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: low)
- Depends on: T-003, T-004, T-005, T-006
- Traces to: A-006
- Status: assumption-dependent (A-006)
- Description: The packaging mirror is refreshed to reflect the edited carrier file and
  agent modules, so the mirror's drift test passes without any file being newly added
  outside the mirror refresh itself.
- Acceptance Criteria:
  - The packaging-mirror drift test passes after the refresh
  - No file is added to the framework tree other than the mirror's own refreshed copies
- Gate: Review Gate

### T-011 Produce the framework closure package for this change

- Owner: omn-documentation
- Complexity: M (confidence: medium)
- Depends on: T-008, T-009, T-010, T-012, T-013, T-014
- Traces to: A-008
- Status: ready
- Description: A single closure package is produced: a change proposal from the
  framework's change-proposal template, linking this run's artifacts — the scope
  definition, this execution plan, the design, implementation, and review evidence, the
  byte measurement, the baseline verification result, the mirror refresh confirmation, and
  the version-bump decision — together with a run of the framework release checklist
  against that proposal.
- Acceptance Criteria:
  - The change proposal links every run artifact named above by reference
  - The release-checklist verification records a result for this change
- Gate: Closure Gate

### T-012 Decide whether the module edits warrant a contract-version increment

- Owner: omn-tech-lead
- Complexity: S (confidence: medium)
- Depends on: T-003, T-004, T-005, T-006
- Traces to: A-008
- Status: ready
- Description: Given the final edited text of the architect, implementer, and reviewer
  modules, a decision is recorded on whether the additive edits warrant a later
  contract-version increment, given that host registrations pin the current version and
  gate-approval precedent keys on producing-agent version; if a bump is warranted, it is
  recorded as a separate follow-up change, not performed here.
- Acceptance Criteria:
  - A decision — bump warranted, or not warranted — is recorded with its rationale
  - If warranted, a follow-up change is named rather than performed inside this plan
- Gate: Closure Gate

### T-013 Record any new external dependency as architecture-significant

- Owner: architect
- Complexity: XS (confidence: low)
- Depends on: T-001
- Traces to: A-007
- Status: assumption-dependent (A-007)
- Description: If the design selected under T-001 or authored under T-002 introduces a new
  external dependency, that introduction is recorded as an architecture-significant
  decision with the reason no lower rung of the ladder held; if no new dependency is
  introduced, this is recorded as not applicable.
- Acceptance Criteria:
  - An architecture-significant decision record exists naming the new dependency and the
    unheld lower rungs, when a new external dependency is introduced
  - An explicit not-applicable statement is recorded, when no new external dependency is
    introduced
- Gate: Design Gate

### T-014 Increment the carrier skill's recorded version

- Owner: architect
- Complexity: XS (confidence: low)
- Depends on: T-001
- Traces to: A-007
- Status: assumption-dependent (A-007)
- Description: If the carrier file selected under T-001 is an existing skill file, its
  recorded version is raised by one minor increment in the skill registry and in the skill
  catalog, the two are kept in agreement, and the registry coverage verifier still resolves
  the standard by its display name; if the carrier is not a skill file, this is recorded as
  not applicable.
- Acceptance Criteria:
  - The registry record and skill catalog show the same incremented minor version and the
    coverage verifier resolves it, when the carrier file is an existing skill file
  - An explicit not-applicable statement is recorded, when the carrier file is not a skill
    file
- Gate: Design Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | decision-gate | The authoring target depends on which existing file T-001 selects as carrier |
| T-001 | T-013 | decision-gate | Whether a new dependency was introduced is only assessable once T-001 fixes the carrier and loading approach |
| T-001 | T-014 | decision-gate | A skill-version increment applies only if T-001 selects an existing skill file as carrier |
| T-002 | T-003 | contract | The reuse-survey rule references the authored standard's text |
| T-002 | T-004 | contract | The route-selection procedure references the authored standard's ladder |
| T-002 | T-005 | contract | The safety-floor self-check references the authored standard's safety-floor list |
| T-002 | T-006 | contract | The seven-questions procedure references the authored standard's review questions |
| T-003 | T-008 | produces-consumes | Byte measurement needs the architect module's final edited text |
| T-004 | T-008 | produces-consumes | Byte measurement needs the implementer module's final edited text |
| T-005 | T-008 | produces-consumes | Byte measurement needs the implementer module's final edited text |
| T-006 | T-008 | produces-consumes | Byte measurement needs the reviewer module's final edited text |
| T-003 | T-009 | verification | Verification confirms the edited architect module did not regress a baseline verifier |
| T-004 | T-009 | verification | Verification confirms the edited implementer module did not regress a baseline verifier |
| T-005 | T-009 | verification | Verification confirms the edited implementer module did not regress a baseline verifier |
| T-006 | T-009 | verification | Verification confirms the edited reviewer module did not regress a baseline verifier |
| T-007 | T-009 | produces-consumes | Verification compares current results against the fresh baseline T-007 captured |
| T-003 | T-010 | produces-consumes | The mirror refresh mirrors the architect module's final edited text |
| T-004 | T-010 | produces-consumes | The mirror refresh mirrors the implementer module's final edited text |
| T-005 | T-010 | produces-consumes | The mirror refresh mirrors the implementer module's final edited text |
| T-006 | T-010 | produces-consumes | The mirror refresh mirrors the reviewer module's final edited text |
| T-003 | T-012 | contract | The version-bump decision is assessed against the architect module's final edited text |
| T-004 | T-012 | contract | The version-bump decision is assessed against the implementer module's final edited text |
| T-005 | T-012 | contract | The version-bump decision is assessed against the implementer module's final edited text |
| T-006 | T-012 | contract | The version-bump decision is assessed against the reviewer module's final edited text |
| T-008 | T-011 | produces-consumes | The change proposal records the measured byte deltas |
| T-009 | T-011 | verification | The change proposal records the verification result against baseline |
| T-010 | T-011 | produces-consumes | The change proposal records that the packaging mirror was refreshed |
| T-012 | T-011 | produces-consumes | The change proposal records the version-bump decision |
| T-013 | T-011 | produces-consumes | The change proposal records the dependency-significance outcome |
| T-014 | T-011 | produces-consumes | The change proposal records the skill-version outcome |

### 8.2 External Dependencies

None identified. Every prerequisite in this plan is owned by an agent within the
framework's authority; no party outside the framework is required to act.

### 8.3 Implementation Order

- Wave 1: T-001, T-007
- Wave 2: T-002, T-013, T-014
- Wave 3: T-003, T-004, T-005, T-006
- Wave 4: T-008, T-009, T-010, T-012
- Wave 5: T-011

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because: the request delivers new, product-requested behaviour into existing
agent contracts with design, implementation, and review impact and a documented closure,
matching the shape of `implement-feature` rather than a defect fix, a pure investigation,
or a standalone refactor.

| Phase | Tasks |
|---|---|
| execution-planning | plan handoff |
| solution-design-and-risk-assessment | T-001, T-002, T-003, T-013, T-014 |
| implementation | T-004, T-005, T-010 |
| quality-review | T-006, T-007, T-008, T-009, T-012 |
| documentation-and-release-handoff | T-011 |

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
| reuse-assessment | T-001, T-003 | architect | Primary |
| technical-approach-definition | T-002 | architect | Primary |
| architecture-decision-authoring | T-013, T-014 | architect | Primary |
| implementation-delivery | T-004, T-005, T-010 | omn-dev-1-implement | Primary |
| code-review | T-006 | omn-dev-2-reviewer | Primary |
| quality-verification | T-009 | omn-qa | Primary |
| quality-verification | T-007, T-008 | omn-tech-lead | Secondary |
| release-readiness | T-012 | omn-tech-lead | Primary |
| documentation | T-011 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | architecture/clean-architecture-checklist.md | T-001, T-002, T-003, T-013, T-014 | Primary |
| S09 | security/secure-engineering.md | T-005, T-006 | Secondary |
| S07 | testing/testing-strategy.md | T-007, T-009 | Secondary |
| S03 | dotnet/engineering-playbook.md | T-004, T-010 | Secondary |

## Acceptance Criteria

1. The carrier file states all five required elements of the standard and is already
   reachable, without a runtime change, by all seven named phases. Verifies business
   objective 1. Evidence: T-001 and T-002 outputs, confirmed at the Design Gate.
2. The architect, implementer, and reviewer procedures apply the ladder, the safety floor,
   and the seven review questions exactly as the standard states, with no rule softened.
   Verifies business objectives 1, 2, and 3. Evidence: T-003, T-004, T-005, T-006 outputs,
   confirmed at the Review Gate.
3. Every framework verifier, the test suite, and the component counts match their recorded
   baseline after the change, and the runtime module is unchanged. Verifies business
   objectives 1 and 3. Evidence: T-009 verification result compared to the T-007 snapshot,
   confirmed at the Verification Gate.
4. The added instruction volume is reported in bytes per module set, and a change proposal
   linking all run artifacts passes the release-checklist run. Verifies business objective
   1. Evidence: T-008 measurement and T-011 change proposal, confirmed at the Closure Gate.

## Definition of Done

- [ ] Acceptance criteria 1 through 4 are verified with recorded evidence
- [ ] Scope, Planning, Design, Review, Verification, and Closure Gates are approved with
      owners recorded
- [ ] Task acceptance criteria for T-001 through T-014 are satisfied or formally waived
- [ ] Assumptions A-001 through A-008 are confirmed or converted to recorded decisions
- [ ] Risks R-001 through R-010 are closed or accepted with named owners
- [ ] Open Questions Q-001 and Q-002 are closed or explicitly accepted
- [ ] The change proposal is published and the release-checklist result is recorded
- [ ] Durable outcomes are recorded to memory per memory/memory-governance.md

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Which representative implementation tasks form the before-and-after outcome comparison the business intent describes, who runs it, against which baseline figures, and is it delivered inside this change or as a follow-up? | No | requester | plan-wide |
| Q-002 | Is there a ceiling on added instruction bytes per module set above which the change is rejected as framework bloat, or is reporting the measured bytes sufficient? | No | requester | T-008, T-011 |
