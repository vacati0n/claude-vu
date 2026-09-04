```yaml
plan:
  planId: reviewer-agent-execution-plan
  sourceInputs:
    - type: feature-request
      reference: inline
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:91557f0e82e8fb1e387591ed315c6987
  contextDigest: sha256:8ece050d279c85ca640cd13faa1ee786
```

## Executive Summary

A Reviewer Agent is added to the AI Engineering Framework as an accountable role that
reviews implementation plans and code changes across five declared dimensions:
architecture compliance, coding quality, testing strategy, security, and framework
governance. Success is that a single registered review role is discoverable, resolves to a
loadable contract, and emits a review artifact that records an explicit outcome for each
declared dimension. The work decomposes into fourteen tasks across six execution waves,
beginning with a boundary decision that separates the new role from review responsibility
already held elsewhere in the framework. The highest-impact risk is `R-007`: five tasks map
to the solution design phase, and loaded context records that phase as unable to pass skill
resolution because one of its mandatory skills is catalogued but unregistered, so those
tasks cannot execute under the framework runtime as it stands. Plan status is complete; seven
open questions are recorded, none of them blocking, and `A-001` through `A-006` require
confirmation before the tasks that rely on them begin.

## Business Objectives

- Implementation plans and code changes are reviewed by one accountable framework role
  before they progress, so review coverage is consistent rather than assigned case by case.
  Received by engineering delivery workflows. Measured as the proportion of governed changes
  that carry a recorded Reviewer Agent verdict, per the measure assumed in `A-004`.
  Traces to `S-001`, `S-002`, `S-003`.
- Review outcomes are stated consistently across the five declared review dimensions, so
  quality expectations do not vary between reviews. Received by the delivery and quality
  roles that consume review results. Measured as the proportion of emitted review artifacts
  that record an explicit outcome for each declared dimension.
  Traces to `S-004`, `S-005`, `S-006`, `S-007`, `S-008`.

## Technical Objectives

- One registered Reviewer Agent contract resolves through the framework discovery
  registries to a loadable module set. Verified by resolving the agent identifier to a
  specification path that loads in declared order. Traces to business objective 1.
- The Reviewer Agent declares an authority boundary that does not duplicate an existing
  agent's Primary review capability. Verified by inspecting the governance matrices for a
  single Primary owner of each review capability. Traces to business objective 1 and
  `A-001`.
- The review artifact has a contract-defined structure that requires an explicit recorded
  outcome for each declared review dimension. Verified by checking an emitted artifact
  against its output contract. Traces to business objective 2 and `A-002`.
- Two runs of the Reviewer Agent over identical inputs and an identical context snapshot
  produce an artifact with an identical section set and identical finding identifiers.
  Verified by comparing the two emitted artifacts. Traces to business objective 2.

## Scope

### In Scope

- The Reviewer Agent's responsibility boundary against existing review ownership (`S-001`)
- The Reviewer Agent's authority scope and accepted input set (`S-001`, `S-002`, `S-003`)
- The review artifact output contract (`S-001`, `A-002`)
- Framework governance records for the new role (`S-001`)
- The Reviewer Agent contract module set (`S-001`)
- Discovery registration for the agent and its artifact template (`S-001`, `A-002`)
- Validation coverage for the contract and its artifact (`S-001`)
- Documentation of the agent and its handoff points (`S-001`)
- Architecture-compliance review criteria (`S-004`)
- Coding-quality review criteria (`S-005`)
- Testing-strategy review criteria (`S-006`)
- Security review criteria (`S-007`)
- Framework-governance review criteria (`S-008`)

### Out of Scope

- Running any review with the new role. Excluded because the input asks for the role to be
  added, not exercised.
- Registering a new workflow or command that routes to the Reviewer Agent. Excluded because
  the input names an agent and no statement names a workflow; the routing gap is recorded in
  `Q-003`.
- Changing existing gate ownership. Excluded because gate ownership is fixed by the gate
  matrix in loaded context and no statement asks for it to change.

### Deferred

- Migration of references to the existing review identifier. Enters scope if `T-001` decides
  that the Reviewer Agent supersedes the existing review contract.
- Dispatchability of the Reviewer Agent by the framework runtime. Enters scope once an owning
  workflow phase and a host registration surface are approved, per `Q-004` and `A-006`.
- Registration of the mandatory skill that currently blocks the solution design phase. Enters
  scope once the framework accepts the registration recorded in `Q-006`.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The Reviewer Agent is a new framework-level role that coexists with the review responsibility already recorded in loaded context, rather than replacing it | S-001 | `T-004` replaces governance rows instead of adding them, `T-011`, `T-013`, and `T-014` change owner, and reference migration moves from deferred into scope | architect |
| A-002 | The Reviewer Agent produces exactly one deliverable artifact, matching the single-deliverable pattern of the registered agents in loaded context | plan-wide | The output contract, the artifact template, and the template registration multiply; `T-003` and `T-006` re-scope | architect |
| A-003 | "Implementation plans" denotes the registered planning and design artifacts already produced inside the framework | S-002 | The Reviewer Agent's accepted input set changes and `T-002` re-scopes | omn-product-owner |
| A-004 | Review coverage is measured as the proportion of governed changes carrying a recorded Reviewer Agent verdict; the input states no numeric target | plan-wide | Plan acceptance criteria 1 and 4 are restated against the confirmed measure | omn-product-owner |
| A-005 | The five named review dimensions are the complete required coverage set for the first version of the agent | S-004, S-005, S-006, S-007, S-008 | Additional dimension-criteria tasks are required and the acceptance of `T-005` and `T-007` expands | omn-product-owner |
| A-006 | Defining and registering the Reviewer Agent contract is separable from making the agent dispatchable at run time | S-003 | Runtime enablement moves from deferred into scope and further tasks precede closure | omn-tech-lead |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | `T-001` rules that the Reviewer Agent supersedes the existing review contract rather than coexisting with it | Every reference to the superseded identifier must be migrated; `T-004` replaces rather than adds governance rows and three criteria tasks change owner | medium | T-004, T-011, T-013, T-014 | Take the boundary decision in `T-001` before wave 2 begins | architect |
| R-002 | requirement | `A-002` is false and the Reviewer Agent must emit more than one deliverable artifact | Output contract, template, and template registration multiply; `T-003` and `T-006` re-scope | low | T-003, T-006 | Fix the deliverable count in the output contract produced by `T-003` | architect |
| R-003 | requirement | The artifact set confirmed in `T-009` differs from `A-003` | The Reviewer Agent's accepted input set changes and `T-002` re-scopes | medium | T-002, T-009 | Confirm the reviewed artifact set in `T-009` before `T-002` begins | omn-product-owner |
| R-004 | requirement | The coverage set confirmed in `T-009` contains dimensions beyond the five named in the input | Further dimension-criteria tasks are required and the acceptance of `T-005` and `T-007` expands | medium | T-002, T-005, T-007 | Confirm the coverage set in `T-009` before `T-002` begins | omn-product-owner |
| R-005 | technical | The authored module set declares descriptor fields or a load order the framework agent loader does not accept | The agent registers but does not resolve at invocation; `T-006` completes while the role stays unusable | medium | T-005, T-006 | Include module-set resolution against the loader contract in the coverage designed in `T-007` | omn-qa |
| R-006 | dependency | The Reviewer Agent is registered while no registered workflow declares a phase the agent owns | The role is discoverable but unroutable; records produced by `T-004` and `T-006` cannot be exercised by any run | medium | T-004, T-006 | Record the owning phase, or its absence, in the governance rows produced by `T-004` | omn-tech-lead |
| R-007 | dependency | The tasks mapped to the solution design phase are dispatched while that phase's mandatory skill set does not resolve | Five tasks cannot execute under the framework runtime and delivery stalls after wave 1 | high | T-001, T-002, T-003, T-004, T-010 | Track the unresolved skill registration in `Q-006`; no task in this plan performs the registration, which is recorded as deferred | omn-tech-lead |
| R-008 | security | The review artifact contract permits verbatim inclusion of reviewed source content | Secrets or restricted content present in reviewed material are copied into a durable framework artifact | low | T-003 | State a redaction rule for reviewed content in the output contract produced by `T-003` | omn-dev-2-reviewer |
| R-009 | operational | `A-006` is false and the contract is accepted only once the agent is dispatchable at run time | Runtime enablement moves from deferred into scope and further work precedes `T-008` | medium | T-002, T-008 | State the runtime invocability expectation in the authority scope produced by `T-002` | omn-tech-lead |
| R-010 | delivery | `T-001` is not decided before wave 2 begins | Twelve of the fourteen tasks cannot start and delivery stalls at wave 1 | medium | plan-wide | Sequence `T-001` as the sole architecture decision in wave 1 and escalate it at plan handoff | omn-tech-lead |

## Task Breakdown

### T-001 Decide the Reviewer Agent boundary against existing review ownership

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: none
- Traces to: S-001
- Status: ready
- Description: An approved statement exists of which review responsibilities the new role
  holds, which remain with the review responsibility already recorded in loaded context, and
  what identifier the new role carries.
- Acceptance Criteria:
  - The responsibility split between the new role and existing review ownership is recorded
    with no responsibility assigned to both
  - The agent identifier is recorded and conforms to the framework naming convention in
    loaded context
  - The disposition of the existing review contract is recorded as unchanged, superseded, or
    re-scoped
- Gate: Design Gate

### T-002 Define the Reviewer Agent authority scope

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-001, S-002, S-003
- Status: ready
- Description: The role's in-scope responsibilities, out-of-scope boundaries, accepted input
  types, and prohibited actions are approved, together with the expectation for whether the
  role must be dispatchable at run time.
- Acceptance Criteria:
  - Accepted input types name the plan artifacts and the change artifacts the role reviews
  - Out-of-scope boundaries name each neighbouring role and the responsibility retained by it
  - The five review dimensions are declared as the role's coverage surface
  - The runtime invocability expectation is stated as required or not required for acceptance
- Gate: Design Gate

### T-003 Define the review artifact output contract

- Owner: architect
- Complexity: M (confidence: low)
- Depends on: T-002
- Traces to: S-001, A-002
- Status: assumption-dependent
- Description: The structure, identifier scheme, severity model, and closure semantics of the
  review artifact are defined, together with the rule governing how reviewed content may be
  reproduced.
- Acceptance Criteria:
  - The artifact requires an explicit recorded outcome for each declared review dimension
  - The finding identifier scheme is fixed so that repeated runs over identical inputs assign
    identical identifiers
  - A redaction rule for reviewed content is stated
  - The artifact template matching the contract exists and is referenced by the contract
- Gate: Design Gate

### T-004 Record the Reviewer Agent in the framework governance matrices

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: T-002
- Traces to: S-001
- Status: ready
- Description: The capability, skill, and routing maps record the new role consistently with
  the approved authority scope.
- Acceptance Criteria:
  - Each review capability the role holds resolves to exactly one Primary owner across the
    governance maps
  - The role's skill coverage is recorded using existing skill identifiers only
  - The owning workflow phase is recorded, or its absence is recorded as a framework gap
- Gate: Design Gate

### T-005 Author the Reviewer Agent contract module set

- Owner: omn-dev-1-implement
- Complexity: L (confidence: medium)
- Depends on: T-003, T-004, T-010, T-011, T-012, T-013, T-014
- Traces to: S-001, S-004, S-005, S-006, S-007, S-008
- Status: ready
- Description: A complete agent contract exists in the runtime module set layout described in
  loaded context, carrying the approved authority scope, the review dimension criteria, and
  the review artifact output contract.
- Acceptance Criteria:
  - Every mandatory contract section required by the framework agent contract is present
    exactly once and in contract order
  - The declared load order names every module in the set and each named module exists
  - Every declared capability identifier already exists in the framework capability map
  - The criteria for all five review dimensions are represented in the contract
- Gate: none

### T-006 Publish the Reviewer Agent discovery records

- Owner: omn-dev-1-implement
- Complexity: S (confidence: low)
- Depends on: T-003, T-005
- Traces to: S-001, A-002
- Status: assumption-dependent
- Description: The new role and its review artifact are discoverable through the framework
  discovery registries, with every reference resolving.
- Acceptance Criteria:
  - The agent record resolves to the authored contract entry point
  - The artifact template record resolves to the template produced by `T-003`
  - Every declared dependency of both records resolves to an existing active record
- Gate: none

### T-007 Design validation coverage for the Reviewer Agent deliverables

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-003
- Traces to: S-001, S-004, S-005, S-006, S-007, S-008
- Status: ready
- Description: Validation coverage exists for contract conformance, artifact conformance,
  determinism, and the boundary that keeps the role from acting outside its authority.
- Acceptance Criteria:
  - Coverage addresses every acceptance criterion in `T-005` and `T-006`
  - Coverage includes resolution of the module set against the framework loader contract
  - Coverage includes a repeat-run comparison that evidences identical structure and
    identifiers
  - Coverage includes negative cases for each declared out-of-scope boundary
- Gate: Verification Gate

### T-008 Document the Reviewer Agent

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-006, T-007
- Traces to: S-001
- Status: ready
- Description: Framework documentation states what the role reviews, what it produces, which
  roles hand work to it, and which roles consume its output.
- Acceptance Criteria:
  - The role, its deliverable, and its upstream and downstream handoffs are documented
  - The intent-to-agent routing entry for review intent reflects the decision recorded in
    `T-001`
  - Release-impact notes for the framework change are drafted
- Gate: Closure Gate

### T-009 Confirm the review coverage scope with the requester

- Owner: omn-product-owner
- Complexity: S (confidence: high)
- Depends on: none
- Traces to: S-002, S-003
- Status: ready
- Description: The set of artifacts the role reviews, the set of review dimensions it must
  cover, and the measure of review coverage are approved.
- Acceptance Criteria:
  - The reviewed artifact set is recorded by name, resolving `Q-002`
  - The review dimension set is recorded as complete or extended, resolving `Q-005`
  - The review coverage measure is recorded, with a pre-adoption baseline or an explicit
    statement that none exists
- Gate: Scope Gate

### T-010 Define architecture-compliance review criteria

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-004
- Status: ready
- Description: The conditions under which a reviewed artifact passes or fails
  architecture-compliance review are stated, with each condition judgeable from the artifact
  and its declared context.
- Acceptance Criteria:
  - Each criterion states an observable condition and the evidence that settles it
  - Each criterion names the severity assigned when it fails
  - The criteria reference existing framework architecture guidance rather than restating it
- Gate: Design Gate

### T-011 Define coding-quality review criteria

- Owner: omn-dev-2-reviewer
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-005
- Status: ready
- Description: The conditions under which a reviewed change passes or fails coding-quality
  review are stated, with each condition judgeable from the change and its evidence.
- Acceptance Criteria:
  - Each criterion states an observable condition and the evidence that settles it
  - Each criterion names the severity assigned when it fails
  - Criteria are policy-backed rather than reviewer preference
- Gate: Review Gate

### T-012 Define testing-strategy review criteria

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-006
- Status: ready
- Description: The conditions under which the testing evidence accompanying a reviewed change
  is judged adequate are stated.
- Acceptance Criteria:
  - Each criterion states an observable condition and the evidence that settles it
  - Each criterion names the severity assigned when it fails
  - Criteria state how test adequacy is judged against the reviewed change's acceptance
    criteria
- Gate: Verification Gate

### T-013 Define security review criteria

- Owner: omn-dev-2-reviewer
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-007
- Status: ready
- Description: The conditions under which a reviewed artifact passes or fails security review
  are stated, including the handling of restricted content encountered during review.
- Acceptance Criteria:
  - Each criterion states an observable condition and the evidence that settles it
  - Each criterion names the severity assigned when it fails
  - Handling of restricted content encountered during review is stated
- Gate: Review Gate

### T-014 Define framework-governance review criteria

- Owner: omn-dev-2-reviewer
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-008
- Status: ready
- Description: The conditions under which a reviewed artifact conforms to framework
  governance, including contract conformance, registry resolution, and gate ownership, are
  stated.
- Acceptance Criteria:
  - Each criterion states an observable condition and the evidence that settles it
  - Each criterion names the severity assigned when it fails
  - Criteria cover contract conformance, registry resolution, and respect for declared gate
    ownership
- Gate: Review Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | decision-gate | The authority scope binds to the approved responsibility split |
| T-001 | T-010 | decision-gate | Architecture-compliance criteria scope depends on which review responsibilities the role holds |
| T-001 | T-011 | decision-gate | Coding-quality criteria scope depends on which review responsibilities the role holds |
| T-001 | T-012 | decision-gate | Testing-strategy criteria scope depends on which review responsibilities the role holds |
| T-001 | T-013 | decision-gate | Security criteria scope depends on which review responsibilities the role holds |
| T-001 | T-014 | decision-gate | Framework-governance criteria scope depends on which review responsibilities the role holds |
| T-009 | T-002 | decision-gate | The accepted input set binds to the confirmed reviewed artifact set and coverage set |
| T-002 | T-003 | contract | The output contract binds to the approved authority scope and accepted inputs |
| T-002 | T-004 | contract | Governance rows record the approved authority scope |
| T-003 | T-005 | contract | The module set binds to the defined output contract |
| T-003 | T-006 | produces-consumes | The template record references the template produced by `T-003` |
| T-003 | T-007 | contract | Validation coverage targets the defined output contract |
| T-004 | T-005 | policy-gate | A contract may declare only capability identifiers already recorded in the framework capability map |
| T-010 | T-005 | produces-consumes | The module set embeds the architecture-compliance criteria |
| T-011 | T-005 | produces-consumes | The module set embeds the coding-quality criteria |
| T-012 | T-005 | produces-consumes | The module set embeds the testing-strategy criteria |
| T-013 | T-005 | produces-consumes | The module set embeds the security criteria |
| T-014 | T-005 | produces-consumes | The module set embeds the framework-governance criteria |
| T-005 | T-006 | produces-consumes | The agent record must resolve to the authored contract entry point |
| T-006 | T-008 | produces-consumes | Documentation describes the registered role |
| T-007 | T-008 | verification | Documentation reflects verified conformance |

### 8.2 External Dependencies

None identified.

No prerequisite outside the plan's authority blocks an in-scope task. The host registration
surface that would make the role dispatchable is recorded as deferred and gates no in-scope
task; the unresolved skill registration behind `R-007` is likewise deferred and is tracked in
`Q-006`.

### 8.3 Implementation Order

- Wave 1: T-001, T-009
- Wave 2: T-002, T-010, T-011, T-012, T-013, T-014
- Wave 3: T-003, T-004
- Wave 4: T-005, T-007
- Wave 5: T-006
- Wave 6: T-008

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because the plan delivers new framework functionality with acceptance criteria,
design impact, registration work, validation coverage, and documentation handoff. Defect
resolution, internal quality change, and discovery workflows do not match the plan intent.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | T-009 |
| `execution-planning` | plan handoff |
| `solution-design-and-risk-assessment` | T-001, T-002, T-003, T-004, T-010 |
| `implementation` | T-005, T-006 |
| `quality-review` | T-007, T-011, T-012, T-013, T-014 |
| `documentation-and-release-handoff` | T-008 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| scope-definition | T-009 | omn-product-owner | Primary |
| architecture-decision-authoring | T-001 | architect | Primary |
| technical-approach-definition | T-002, T-003 | architect | Primary |
| architecture-analysis | T-010 | architect | Primary |
| governance-enforcement | T-004 | architect | Secondary |
| implementation-delivery | T-005, T-006 | omn-dev-1-implement | Primary |
| code-review | T-011, T-013 | omn-dev-2-reviewer | Primary |
| governance-enforcement | T-014 | omn-dev-2-reviewer | Primary |
| validation-design | T-007, T-012 | omn-qa | Primary |
| release-communication | T-008 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | architecture/clean-architecture-checklist.md | T-001, T-002, T-010 | Primary |
| S02 | business/domain-modeling.md | T-002, T-009 | Primary |
| S07 | testing/testing-strategy.md | T-007, T-012 | Primary |
| S09 | security/secure-engineering.md | T-013 | Primary |

## Acceptance Criteria

1. One accountable review role is discoverable in the framework and resolves to a loadable
   contract. Verifies business objective 1. Evidence: the registry resolution recorded by
   `T-006` and the conformance evidence from `T-007`.
2. Both governed change types named in the request, implementation plans and code changes,
   appear in the role's approved accepted input set. Verifies business objective 1. Evidence:
   the approved authority scope from `T-002` and the documentation from `T-008`.
3. The review artifact contract requires an explicit recorded outcome for each of the five
   declared review dimensions. Verifies business objective 2. Evidence: the output contract
   from `T-003` checked against the criteria from `T-010` through `T-014`.
4. The review coverage measure is recorded, with a pre-adoption baseline or an explicit
   statement that none exists. Verifies business objectives 1 and 2. Evidence: the measure
   recorded by `T-009`.

## Definition of Done

- [ ] All four plan acceptance criteria are verified with recorded evidence
- [ ] Scope, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for `T-001` through `T-014` are satisfied or formally waived
- [ ] `A-001` through `A-006` are confirmed or converted to recorded decisions
- [ ] `R-001` through `R-010` are closed or accepted with named owners
- [ ] `Q-001` through `Q-007` are closed or explicitly accepted
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Does the Reviewer Agent supersede the review responsibility already recorded in loaded context, or coexist with it? | No | architect | T-001, T-004, T-011, T-013, T-014 |
| Q-002 | Which registered artifacts constitute the "implementation plans" the Reviewer Agent reviews? | No | omn-product-owner | T-002, T-009 |
| Q-003 | Which registered workflow and phase owns the Reviewer Agent's execution, given that the gate matrix names a review workflow that has no registered workflow record? | No | omn-tech-lead | T-004, T-006 |
| Q-004 | Is dispatchability of the Reviewer Agent at run time required for this delivery to be accepted? | No | omn-tech-lead | T-002, T-008 |
| Q-005 | Are the five named review dimensions the complete coverage set for the first version of the role? | No | omn-product-owner | T-002, T-009 |
| Q-006 | How is the solution design phase made routable, given that loaded context records one of its mandatory skills as catalogued but unregistered? | No | omn-tech-lead | T-001, T-002, T-003, T-004, T-010 |
| Q-007 | The capability map declares a documentation capability identifier in a form the capability resolver does not match, so `T-008` declares the release-communication identifier instead. Should the documentation identifier be made resolvable? | No | architect | T-008 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 | T-001, T-002, T-004, T-005, T-006, T-007, T-008, A-001 |
| S-002 | T-002, T-009, A-003, Q-002 |
| S-003 | T-002, T-009, A-006, Q-004 |
| S-004 | T-005, T-007, T-010, A-005 |
| S-005 | T-005, T-007, T-011, A-005 |
| S-006 | T-005, T-007, T-012, A-005 |
| S-007 | T-005, T-007, T-013, A-005 |
| S-008 | T-005, T-007, T-014, A-005 |
