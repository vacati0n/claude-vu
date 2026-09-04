```yaml
design:
  designId: reviewer-agent-technical-design
  changeReference: runs/inputs/reviewer-agent-feature-request.md
  sourceInputs:
    - type: change-request
      reference: runs/inputs/reviewer-agent-feature-request.md
    - type: business-intent
      reference: runs/inputs/reviewer-agent-business-intent.md
    - type: architecture-context
      reference: runs/inputs/framework-architecture-context.md
    - type: execution-plan
      reference: runs/run-b6780677468b/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003]
  consumesPlan: runs/run-b6780677468b/artifacts/execution-plan.md
  inputDigest: sha256:9b2ffccc86173b79b469d7b81155db11
  contextDigest: sha256:44927b3bcdd3fa660562ae2b83f0ce6e
```

## Metadata

- Feature or Change ID: runs/inputs/reviewer-agent-feature-request.md
- Author: architect
- Reviewers: omn-architect, omn-tech-lead
- Last Updated: 2026-08-18

## Objective

Desired structural outcome: review accountability for governed framework changes resolves
to a single registered agent identity that is discoverable on the same terms as the agents
already registered, and whose verdict is carried by one contract-defined artifact requiring
an explicit outcome for each declared review dimension.

The system under design is the framework itself, so every impacted module is a framework
component: a discovery registry record, an agent contract module set, an artifact template,
a governance matrix, a workflow phase row, or a current-state runtime record.

Architectural objectives:

- Each review capability resolves to exactly one Primary owner across the framework's
  governance records, with no responsibility held by two roles. Traces to `S-001`, `S-004`,
  `S-011`.
- The review role holds a registered agent identity that resolves from a discovery registry
  record to a loadable module set, on the same terms as the existing registered agents.
  Traces to `S-001`, `S-010`.
- The review verdict is expressed by a contract-defined artifact whose structure requires an
  explicit recorded outcome for each declared review dimension, and which states what was
  reviewed and the verdict without the reader reconstructing either. Traces to `S-003`,
  `S-006`, `S-007`, `S-009`.
- The role's accepted input set and authority boundary are declared such that both governed
  change types are named and each neighbouring role's retained responsibility is explicit.
  Traces to `S-002`, `S-005`, `S-008`.

In structural scope: the agent discovery record; the review contract module set; capability
ownership rows; skill coverage rows; the review-result artifact contract, its template, and
its template record; the disposition of the review responsibility already recorded in the
framework; and the workflow phase and host registration surfaces as they bear on whether the
registered role is routable.

Out of structural scope, which bounds the impact surface before analysis begins:

- Any exercise of the new role on real work. Excluded by `S-013` and `C-014`.
- Implementation of the runtime's invocation, adapter, or validation machinery. The change
  adds records and contracts that the existing runtime surfaces resolve; it does not extend
  those surfaces. Bounded by `A-005` and `D-003`.
- Any change to gate ownership. Excluded by `C-010`; ownership rows are unchanged and the
  reasoning is recorded under `M-010`.
- Command registry routing and memory governance records. No supplied statement reaches
  them, and `F-027` places them outside the agent-to-skill and workflow-to-agent directions
  this change touches.
- The engineering content of the five dimension criteria. This design fixes where the
  criteria live and what shape they must take, not what they say.

## Requirements Summary

Functional requirements:

- One accountable role reviews both implementation plans and code changes (`S-002`,
  `S-004`).
- The review occurs before the reviewed change progresses (`S-005`).
- The role states an explicit outcome for each of the five named review dimensions:
  architecture compliance, coding quality, testing strategy, security, and framework
  governance (`S-003`, `S-006`).
- A governed change carries a recorded verdict from the review role (`S-008`).
- An emitted review result records an outcome for every declared review dimension (`S-009`).

Non-functional requirements:

- The role is discoverable through the framework's own discovery surfaces, on the same terms
  as the roles already registered (`S-010`).
- Review results are consumable by the delivery and quality roles that act on them, stating
  what was reviewed and the verdict without a reader reconstructing either (`S-007`).
- Review coverage is expressed as a measured proportion with no numeric target (`S-012`).
- Two runs of the role over identical inputs and an identical context snapshot produce an
  artifact with an identical section set and identical finding identifiers, on the same terms
  as the roles already registered (`S-010`, `C-016`).

Acceptance criteria: cited rather than restated. The acceptance intent supplied with the
business intent rests on three conditions, each traced above: a recorded verdict per governed
change (`S-008`), a complete per-dimension outcome set on every emitted result (`S-009`), and
discoverability on registered-role terms (`S-010`). The four plan-level acceptance criteria
in the supplied execution plan are owned by `planner` and `omn-product-owner` and are not
restated here.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The framework is composed of five component types, agents, skills, workflows, templates, and commands, each with a discovery registry and a specification set | Architecture context input; `registry/agents.yaml`, `registry/skills.yaml`, `registry/workflows.yaml`, `registry/templates.yaml` |
| F-002 | `registry/agents.yaml` holds two records, `planner` and `architect`, both at status `active` | `registry/agents.yaml` |
| F-003 | The agent record schema requires identifier, displayName, description, version, status, specificationPath, dependencies, tags, owner, and capabilities, and the registry enforces unknown-field rejection, all-fields-required, and dependency resolution | `registry/agents.yaml` |
| F-004 | The agent record schema resolves a runtime module set to `agents/<identifier>/manifest.yaml`, and both active records resolve that way | `registry/agents.yaml` |
| F-005 | `agents/capability-matrix.md` is authoritative for the capability identifiers referenced by agent manifests, registry records, and execution plans; an identifier is added there before it may be referenced, and an agent needing an absent capability records a framework gap rather than inventing one | `agents/capability-matrix.md` |
| F-006 | `agents/capability-matrix.md` records `omn-dev-2-reviewer` as Primary for Code Review and Governance and as Primary for Quality Verification, and maps Code Review and Governance to the identifiers `code-review` and `governance-enforcement` | `agents/capability-matrix.md` |
| F-007 | `agents/capability-matrix.md` also records `omn-qa` as Primary for Quality Verification | `agents/capability-matrix.md` |
| F-008 | `agents/capability-matrix.md` records `omn-architect` as deprecated in favour of `architect`, with the deprecated row retained so that documents still naming it resolve during reference migration | `agents/capability-matrix.md` |
| F-009 | `omn-dev-2-reviewer` holds an agent contract under `agents/` and holds no record in `registry/agents.yaml` | `registry/agents.yaml`; architecture context input, asserted property 3 |
| F-010 | `workflows/workflow-gate-matrix.md` assigns the implement-feature Review Gate and the review-pull-request Readiness Gate to `omn-dev-2-reviewer` | `workflows/workflow-gate-matrix.md` |
| F-011 | `workflows/workflow-gate-matrix.md` states the producer exclusion rule: an agent may not approve a gate for an artifact it produced, even where its role appears in that gate's owner list | `workflows/workflow-gate-matrix.md` |
| F-012 | `workflows/workflow-gate-matrix.md` records that gate-owner entries naming `omn-architect` name the architecture role now implemented by `architect`, with the reference migration deferred | `workflows/workflow-gate-matrix.md` |
| F-013 | `registry/workflows.yaml` holds three records, `implement-feature`, `refactor`, and `investigate`, and holds no record for `review-pull-request` | `registry/workflows.yaml` |
| F-014 | `workflows/implement-feature.md` publishes six canonical phase identifiers; `quality-review` is owned by `omn-dev-2-reviewer`, produces a review findings log and a verification report, and is gated by the Review Gate and the Verification Gate | `workflows/implement-feature.md` |
| F-015 | `workflows/implement-feature.md` states that an owner agent shipping a runtime manifest must declare the workflow and the phase identifier in its supported-workflow block, and that a phase whose required skills are not all resolvable through `registry/skills.yaml` is blocked at skill resolution and does not start | `workflows/implement-feature.md` |
| F-016 | `registry/templates.yaml` holds three records, `execution-plan`, `technical-design` at version 1.1.0, and `architecture-decision-record`, and holds no record for a review-result artifact | `registry/templates.yaml` |
| F-017 | The template record schema requires the same ten fields as the agent record schema and enforces unknown-field rejection, all-fields-required, and dependency resolution | `registry/templates.yaml` |
| F-018 | `registry/skills.yaml` holds active records for S01, S02, S03, S06, S07, S08, S09, S11, and S12, and resolves agent skill references by skill code | `registry/skills.yaml` |
| F-019 | `skills/agent-skill-matrix.md` records S04, S05, and S10 as catalogued but unregistered, and records `registry/skills.yaml` as the authority for skill identity metadata including registration status | `skills/agent-skill-matrix.md` |
| F-020 | `skills/agent-skill-matrix.md` assigns `omn-dev-2-reviewer` Primary in S07 and S09, and carries a Declaration Precedence row for each agent that ships a runtime manifest, stating the manifest-versus-matrix delta | `skills/agent-skill-matrix.md` |
| F-021 | The Skill Catalog in `skills/agent-skill-matrix.md` contains no skill for framework governance | `skills/agent-skill-matrix.md` |
| F-022 | `runtime/README.md` records the Validation Engine as partial with one artifact type covered, `execution-plan.md`, and records the Agent Adapter as implemented with a single adapter | `runtime/README.md` |
| F-023 | `runtime/README.md` records, as known gaps, that S03 is unregistered and blocks `solution-design-and-risk-assessment` at skill resolution, and that only `planner` carries a host registration so `architect` remains non-invocable | `runtime/README.md` |
| F-024 | The architecture context asserts that the runtime executes two phases of `implement-feature`, `execution-planning` and `solution-design-and-risk-assessment`, and that no other phase has a registered validator | Architecture context input, asserted property 4 |
| F-025 | The architecture context asserts that an agent becomes invocable when it holds an active registry record, a manifest with a resolvable module load order, a host registration at `agents/<agent-id>.agent.md`, and a workflow phase routing to it with an output artifact the runtime can validate | Architecture context input, asserted property 2 |
| F-026 | `domain-model/agent-specification.md` requires an agent to declare Agent ID, Name, Domain Role, Authority Scope, Supported Workflow Phases, Input Contract, Output Contract, Decision Rights, Escalation Targets, Status, and Version, and constrains the framework to one primary owner per task scope | `domain-model/agent-specification.md` |
| F-027 | `dependency-map.md` records the permitted dependency directions: Commands to Workflows, Workflows to Agents and Skills, Agents to Skills, and Workflows and Agents to Memory | `dependency-map.md` |
| F-028 | The supplied execution plan decomposes the change into fourteen tasks, T-001 through T-014, across six waves, and maps T-001, T-002, T-003, T-004, and T-010 to the solution-design phase | Execution plan input |
| F-029 | `registry/templates.yaml` records one template record per artifact contract, each naming its producing role and owning domain | `registry/templates.yaml` |
| F-030 | The known-gap record in `runtime/README.md` and the record in `registry/skills.yaml` disagree about the registration status of S03, and the same known-gap record and the architecture context's asserted property 4 disagree about whether `solution-design-and-risk-assessment` executes | `runtime/README.md`, `registry/skills.yaml`, architecture context input |

`F-030` records a divergence between two framework records about the same current-state
property. It is recorded, not reconciled. `C-001` makes the discovery registries the single
authority for identity metadata, and `F-019` records that rule inside the skill matrix
itself, so the substantive question is settled by a declared precedence rather than by this
agent. The stale narrative is routed to its owner as `Q-006` and corrected at `P-013`.

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The "implementation plans" the role reviews are the framework's registered plan and design artifacts, `execution-plan.md` and `technical-design.md` | `S-002` names a class of change, not the artifacts; the role's accepted input types cannot be declared without the set | The accepted input types change, the authority scope at `P-003` is restated, and the dimension criteria at `P-004` re-scope | omn-product-owner |
| A-002 | The five named review dimensions are the complete coverage set for the first version of the role | The artifact contract requires one recorded outcome per declared dimension, so the dimension set fixes the contract shape | The artifact's outcome register gains rows and the criteria set at `P-004` expands after the contract at `P-005` is fixed | omn-product-owner |
| A-003 | "Code changes" denotes a change set and its accompanying evidence supplied to the role as input data, not content the role retrieves | `F-025` states four conditions for invocability and none of them is a retrieval surface; the framework's agents consume supplied context | The role requires a retrieval capability absent from `agents/capability-matrix.md`, which `C-002` forbids inventing, so both the input contract and the runtime surface change | omn-tech-lead |
| A-004 | Review coverage is measured as the proportion of governed changes carrying a recorded verdict from the role, with no numeric target and no pre-adoption baseline | `S-012` fixes the form of the measure but no baseline is supplied and the reuse survey found no measurement surface | The acceptance measure is restated and a measurement surface enters scope | omn-product-owner |
| A-005 | Defining and registering the role's contract is separable from making the role dispatchable at run time | `F-025` lists four conditions for invocability and no supplied statement requires all four in this change | `P-014` moves from deferred into scope, `D-003` is reversed, and acceptance waits on a host registration and an owning workflow phase | omn-tech-lead |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | The framework's discovery registries are single-authority; a second authority for the same identity metadata is a defect, not a design option | Hard | Architecture context constraint; `F-019` |
| C-002 | structural | A capability identifier may be referenced by a manifest, a registry record, or an execution plan only if it already exists in `agents/capability-matrix.md`; an absent capability is recorded as a framework gap, never invented | Hard | `F-005` |
| C-003 | structural | One primary owner per task scope | Hard | `F-026` |
| C-004 | structural | A registry record carries every schema-required field, its specification path resolves to an existing file, and every declared dependency resolves to an existing active record | Hard | `F-003`, `F-017` |
| C-005 | structural | An owner agent that ships a runtime manifest declares the owning workflow and phase identifier in its supported-workflow block, and a phase whose required skills do not all resolve is blocked at skill resolution | Hard | `F-015` |
| C-006 | functional | A single accountable role holds review responsibility for both governed change types, implementation plans and code changes | Hard | `S-002`, `S-004` |
| C-007 | functional | The change adds a review role to the framework as a registered agent identity | Hard | `S-001`, `S-011` |
| C-008 | functional | The review result records an explicit outcome for each declared review dimension | Hard | `S-003`, `S-006`, `S-009` |
| C-009 | functional | The review result states what was reviewed and the verdict without the reader reconstructing either | Hard | `S-007` |
| C-010 | compliance | No change to gate ownership is authorized without being recorded as a decision naming the gate matrix owners | Hard | Architecture context constraint |
| C-011 | compliance | No existing role's accountability changes without that change being surfaced as a decision | Hard | `S-011` |
| C-012 | migration | Registration and governance records are the framework's contract surface, so every existing reference to the review responsibility continues to resolve throughout any transition | Hard | Architecture context constraint; `F-010`, `F-014` |
| C-013 | security | Reviewed content reproduced into a durable review artifact is bounded by a stated rule, so restricted content present in reviewed material is not copied into a framework artifact | Hard | Execution plan input, recorded security risk on the review artifact contract |
| C-014 | operability | The new role is not exercised on real work as part of this change | Hard | `S-013` |
| C-015 | quality-attribute | Review coverage is expressed as a measured proportion with no numeric target | Negotiable | `S-012` |
| C-016 | quality-attribute | Two runs of the role over identical inputs and an identical context snapshot produce an artifact with an identical section set and identical finding identifiers | Hard | Execution plan input, recorded technical objective; `F-004` |

Statements `S-001` through `S-016` are the normalization of the supplied change request and
business intent, in supplied order and document order: `S-001` a Reviewer Agent is added to
the framework; `S-002` it reviews implementation plans and code changes; `S-003` its review
covers the five named dimensions; `S-004` one accountable role holds review responsibility so
expectations do not vary; `S-005` review occurs before the reviewed change progresses;
`S-006` the role states an explicit outcome per dimension; `S-007` results are consumable
without reconstruction; `S-008` a governed change carries a recorded verdict; `S-009` an
emitted result records an outcome for every declared dimension; `S-010` the role is
discoverable on registered-role terms; `S-011` the change adds a role and changes no existing
role's accountability without a surfaced decision; `S-012` coverage is a measured proportion
with no numeric target; `S-013` the role is not exercised on real work in this change;
`S-014` coexistence versus supersession is open to the design; `S-015` the artifact's content
beyond the per-dimension outcome is open to the design; `S-016` the point at which the role
becomes routable is open to the design.

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `registry/agents.yaml` | contract-change | F-002, F-003, F-004 | Agent record set; specification-path resolution; declared dependency resolution | confirmed |
| M-002 | Review contract module set at `agents/reviewer/` | extension | F-004, F-026 | Manifest load order, declared capabilities, accepted input types, authority scope, supported-workflow block | confirmed |
| M-003 | Host registration at `agents/reviewer.agent.md` | extension | F-025, A-005 | Host adapter entry point | speculative |
| M-004 | `agents/capability-matrix.md` | contract-change | F-005, F-006, F-007, F-008 | Agent-to-capability ownership rows; Coverage Notes | confirmed |
| M-005 | `skills/agent-skill-matrix.md` | contract-change | F-019, F-020, F-021 | Agent to Skill Coverage table; Declaration Precedence table | confirmed |
| M-006 | Review-result artifact template at `templates/review-result.md` | extension | F-016, F-029 | Review-result artifact structure; per-dimension outcome register; finding identifier scheme | confirmed |
| M-007 | `registry/templates.yaml` | contract-change | F-016, F-017, F-029 | Template record set; specification-path resolution | confirmed |
| M-008 | Review contract at `agents/omn-dev-2-reviewer.md` | contract-change | F-006, F-009, F-010 | Role status marker; review responsibility declaration | confirmed |
| M-009 | `workflows/implement-feature.md` | dependency-change | F-014, F-015, F-025 | Phase Model owner column for `quality-review`; Phase Identifier Sources table; supported-workflow binding | speculative |
| M-010 | `workflows/workflow-gate-matrix.md` | behavior-change | F-010, F-011, F-012 | Gate owner resolution note | confirmed |
| M-011 | `registry/workflows.yaml` | no-change-verified | F-013 | none | confirmed |
| M-012 | `dependency-map.md` | no-change-verified | F-027 | none | confirmed |
| M-013 | `runtime/README.md` | operational-impact | F-022, F-023, F-030 | Known-gaps record; implemented-surface table | confirmed |

`M-010` is `behavior-change` rather than `contract-change` because gate ownership itself is
untouched, as `C-010` requires: no owner is added or removed. What changes is which role the
existing owner entry resolves to, which the matrix already handles for the architecture role
under `F-012` and which the same note extends to the review role.

`M-011` and `M-012` are recorded because a reader would reasonably expect a new agent to
change them. `M-011` does not change: no workflow is registered by this change, and under
`D-003` the review record declares no workflow control dependency, so no existing workflow
record gains one. `M-012` does not change: the role introduces only Agents-to-Skills and
Workflows-to-Agents edges, both already permitted by `F-027`.

Boundary crossings in the impact set: the agent record to the manifest, at `M-001` to
`M-002`; the agent record to the template record, at `M-001` to `M-007`, which is the edge
`C-004` constrains; the template record to the template file, at `M-007` to `M-006`; and the
workflow phase row to the manifest's supported-workflow block, at `M-009` to `M-002`, which
is the crossing `C-005` constrains and which `D-003` defers.

### 5.2 Options Considered

| Option | Structural change | C-001 | C-003 | C-006 | C-007 | C-012 | Impact surface | Reuse leverage | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | Register a new review identity that supersedes the review responsibility already recorded, retaining the superseded rows during reference migration | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | 6 | 10 | 2 | One added identity and one retained superseded row; existing owner entries resolve unchanged | Selected |
| O-002 | Register a new identity holding plan and design review plus framework governance, leaving code-change review with the existing role | Violated | Satisfied | Violated | Satisfied | Satisfied | 6 | 9 | 2 | Two review owners; a routing rule per change type is required | Eliminated on C-001, C-006 |
| O-003 | Migrate the existing review contract in place to the runtime module-set pattern and register it under its current identifier | Satisfied | Satisfied | Satisfied | Violated | Satisfied | 5 | 11 | 1 | No new identity; every existing reference resolves unchanged | Eliminated on C-007 |
| O-004 | Register a new identity as Primary for both review capabilities while the existing role retains its Primary rows unchanged | Violated | Violated | Violated | Satisfied | Satisfied | 4 | 10 | 0 | Two Primary owners; ownership is ambiguous at every gate | Eliminated on C-001, C-003, C-006 |

Impact surface counts modules carrying `contract-change` or `dependency-change` in 5.1 under
that option. Reuse leverage counts capabilities in section 7 whose outcome under that option
is `reuse-as-is` or `reuse-extended`. Migration burden counts contract-affecting changes that
require a transition strategy, that is, changes with existing consumers.

Criteria are applied in the order fixed by the reasoning procedure. Criterion 1, hard
constraint satisfaction, eliminates `O-002`, `O-003`, and `O-004`. One option survives, so
criteria 2 through 6 do not decide the selection and are recorded for comparison only.

### 5.3 Selected Approach

- Selected: `O-001`.
- Structural change: a review role is registered under the new agent identity `reviewer` as a
  runtime module set at `M-002`, resolved from a new record in `M-001` whose declared
  dependency is on the review-result template record in `M-007`, which in turn resolves to the
  new artifact template at `M-006`. The role takes Primary ownership of Code Review and
  Governance in `M-004`, using only the identifiers `code-review` and `governance-enforcement`
  that `F-006` already records. The review responsibility recorded at `M-008` is marked
  superseded by the new identity and retained, and the corresponding rows in `M-004` and
  `M-005` are retained during reference migration, following the treatment `F-008` records for
  the architecture role. Gate ownership is untouched; the resolution note at `M-010` covers the
  superseded identifier exactly as `F-012` covers the architecture one. The host registration
  at `M-003` and the owning workflow phase at `M-009` are sequenced after registration and
  deferred under `D-003`.
- Rationale: `O-001` is the only option satisfying every hard constraint. It is the only one
  that gives both governed change types a single accountable owner as `C-006` requires while
  keeping exactly one Primary owner per review capability as `C-003` and `C-001` require, and
  it does so by reusing a supersession pattern the framework has already executed once, which
  `F-008` and `F-012` establish and which `C-012` makes mandatory for any transition.
- Highest-scoring rejected alternative and why it lost: `O-003`, migrating the existing review
  contract in place. It scores best of all four on every criterion after the first: the
  smallest impact surface at 5, the highest reuse leverage at 11 because it reuses the existing
  identity and every reference to it, and the lowest migration burden at 1 because no reference
  migration is created at all. It satisfies `C-001`, `C-003`, `C-006`, and `C-012`. It loses on
  `C-007` alone: `S-001` and `S-011` state that the change adds a role to the framework, and
  `O-003` adds no role, it registers one that already exists. That reading of `S-001` is the
  single point on which the selection turns, so it is routed to its owner as `Q-001` rather
  than being treated as settled.
- Tradeoffs accepted: the selection creates a reference migration that `O-003` would have
  avoided. Every framework document naming the superseded review identifier must be rewired,
  and the supplied context does not establish how many such documents exist, which is why
  `R-004` tracks the coexistence period and `P-012` records remaining references rather than
  assuming the rewiring completes in one step. The selection also accepts, deliberately, a
  registered role that is not routable at the point of registration, recorded as `D-003` and
  tracked as `R-009`; the alternative of enabling routing at registration would attach an
  unverified contract to a live workflow phase ahead of the validation coverage at `P-010`.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | The review role is registered under a new agent identity that supersedes the review responsibility already recorded in the framework, with the superseded rows retained during reference migration | Yes | ADR D-001, status Proposed |
| D-002 | The role emits exactly one primary deliverable, a review-result artifact with a contract-defined structure requiring an explicit recorded outcome for each declared review dimension, registered as its own template record | Yes | ADR D-002, status Proposed |
| D-003 | Contract registration is separated from runtime dispatchability: the role registers with a data dependency on its artifact template and no workflow control dependency, and the host registration and owning workflow phase are sequenced after the Design Gate | Yes | ADR D-003, status Proposed |
| D-004 | The role declares only capability identifiers already present in `agents/capability-matrix.md`, namely `code-review` and `governance-enforcement`; the framework-governance dimension is carried by the contract's own criteria rather than by a new capability or skill identifier | No | Inline; applies `C-002` and `F-005` without introducing structure. The absence of a governance skill is recorded as `Q-007` |
| D-005 | Primary ownership of Quality Verification consolidates on `omn-qa`, which `F-007` records as already holding it, and the review role holds Secondary there | No | Inline; recorded as a consequence in ADR D-001, because superseding a role that holds a Primary rating requires stating where that rating goes under `C-003`. Confirmation is routed as `Q-008` |

## API and Data Model Impact

The framework has no runtime API and no persisted data store in the impact surface: `F-001`
establishes that its component types are declarative registry records and specification sets,
and every module in 5.1 is one of those. `C-012`, drawn from the supplied architecture context,
establishes that registration and governance records are the framework's own contract surface
rather than implementation detail. Contract changes below are therefore record and document
contract changes, and each carries the transition strategy `C-012` requires.

API changes:

- `M-001` gains one agent record for the review identity, resolving to the manifest at
  `M-002` and declaring a data dependency on the template record added to `M-007`.
- `M-007` gains one template record for the review-result artifact, resolving to `M-006`.
- `M-004` gains a Primary row for the review identity under Code Review and Governance and
  marks the superseded row.
- `M-005` gains a coverage row and a Declaration Precedence row for the review identity and
  marks the superseded row.
- `M-008` gains a supersession marker.
- `M-009` gains a phase-owner binding only if `D-003` is later reversed or `Q-005` resolves
  to an owning phase; no change is made by this design.

Contract compatibility notes for `M-001`, the agent registry:

- Current shape: two active records, resolving to manifests under `agents/`.
- Target shape: three active records, the added one carrying every schema-required field, a
  specification path resolving to the manifest at `M-002`, and a dependency array containing
  one data dependency on the review-result template record.
- Compatibility approach: purely additive. The record schema is unchanged, so the registry's
  unknown-field rejection and all-fields-required rules stay satisfied per `C-004`, and no
  existing record or consumer changes.
- Coexistence period: none required.
- Retirement condition: not applicable; the record is added, not replaced. A workflow control
  dependency is added only when the deferred routing under `D-003` is approved.
- Rollback position: remove the record. No other record depends on it, because the declared
  dependency points from the agent record outward to the template record, so discovery
  returns to two active agents with no unresolved reference.

Contract compatibility notes for `M-007`, the template registry:

- Current shape: three active template records, none for a review result.
- Target shape: four, the added one resolving to the template file at `M-006` and following
  the one-record-per-artifact-contract pattern `F-029` records.
- Compatibility approach: purely additive; no existing record changes.
- Coexistence period: none required.
- Retirement condition: not applicable.
- Rollback position: remove the record. Because the agent record at `M-001` declares a data
  dependency on it, rolling this back requires rolling back `M-001` first or in the same
  step, which is the inverse of the ordering `P-008` before `P-011` establishes.

Contract compatibility notes for `M-004` and `M-005`, the governance matrices (`D-001`):

- Current shape: the superseded identity holds Primary for Code Review and Governance and for
  Quality Verification in `M-004`, and holds a coverage row in `M-005` with Primary in S07 and
  S09.
- Target shape: the review identity holds Primary for Code Review and Governance in `M-004`
  and a coverage row plus a Declaration Precedence row in `M-005`; the superseded rows are
  marked and retained; Quality Verification Primary rests solely with `omn-qa` per `D-005`.
- Compatibility approach: the superseded rows are retained so that documents still naming the
  superseded identifier resolve during migration, which is the treatment `F-008` records for
  the architecture role and which `C-012` requires. At no point do two rows carry Primary for
  the same capability, which is what keeps `C-001` and `C-003` satisfied throughout.
- Coexistence period: until every framework document naming the superseded identifier for
  review responsibility has been rewired to the new identity.
- Retirement condition: the superseded rows are removed when no framework document references
  the superseded identifier for review responsibility, which `P-012` evidences.
- Rollback position: remove the added rows and clear the supersession markers. Review
  ownership returns to the superseded identity with no other record changed, because the
  retained rows were never removed.

Contract compatibility notes for `M-008`, the superseded review contract:

- Current shape: an agent contract under `agents/` with no registry record, named as Primary
  review owner by `M-004` and as gate owner by `M-010`.
- Target shape: the same contract marked superseded by the review identity and retained
  readable, matching the treatment the deprecated architecture contract receives.
- Compatibility approach: the file is retained and readable throughout; nothing that reads it
  breaks.
- Coexistence period: as for `M-004` and `M-005`.
- Retirement condition: removal of the file is a separate governed change and is not part of
  this one.
- Rollback position: clear the supersession marker.

Schema or migration changes: none. No record schema is altered, and there is no data store to
migrate. The transition is a reference migration across declarative records. It is
forward-only in structure and reversible in effect for as long as the superseded rows are
retained. During the transition, readers resolving the superseded identifier continue to
resolve, because the superseded rows are retained; writers adding new references use the new
identity. `M-009` is the one reader whose resolution is not settled by this design, which is
why it is marked speculative and tracked by `R-009` and `Q-005`.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Agent identity and discovery | `registry/agents.yaml` record schema | reuse-as-is | `F-003` establishes the schema; the change adds a record and alters no field, so the registry's validation rules apply unchanged |
| Agent contract structure | The runtime module-set pattern of a manifest plus a declared load order, used by both records in `F-004` | reuse-as-is | `F-004` establishes the pattern for every registered agent; `F-026` establishes the properties a contract must declare. A second contract shape would create the second authority `C-001` forbids |
| Review capability ownership identifiers | `code-review` and `governance-enforcement` in `agents/capability-matrix.md` | reuse-as-is | `F-006` records both identifiers as existing; `C-002` forbids inventing a new one, so the role declares these and nothing else |
| Role supersession and reference migration | The deprecation pattern recorded for the architecture role in `F-008` and `F-012` | reuse-as-is | The framework has executed this transition once already, including retention of the superseded row and a resolution note at the gate matrix. `C-012` requires exactly the property that pattern provides |
| Skill coverage for four of the five review dimensions | S01, S03, S07, and S09 in `registry/skills.yaml` | reuse-as-is | `F-018` records all four as active. Architecture compliance maps to S01, coding quality to S03, testing strategy to S07, and security to S09, so four dimensions need no new skill identifier |
| Skill coverage for the framework-governance dimension | The Skill Catalog in `skills/agent-skill-matrix.md` and the records in `registry/skills.yaml` were both searched | none-found | `F-021` establishes that no catalogued skill covers framework governance. No new skill is proposed: registering one is a registry change outside this change's scope under `C-014`, and the dimension is carried by the contract's own criteria per `D-004`. The gap is recorded as `Q-007` |
| Review result artifact structure | `templates/execution-plan.md` and `templates/technical-design.md`, the registered artifact templates | rejected | Both are examined and both are unsuitable. Each carries a fixed section set with plan or design semantics and neither has a per-dimension verdict register, which `C-008` requires. Overloading either would place two artifact contracts under one template record, producing the second authority `C-001` forbids. This row is what licenses the new structure at `M-006` |
| Artifact metadata and identifier conventions | The metadata block and zero-padded identifier scheme carried by the registered templates | reuse-extended | The review artifact adopts the same metadata block form, including the input and context digests, and the same zero-padded identifier convention, extending it with a finding scheme of its own. `C-016` requires identifier stability, which the existing convention already provides |
| Artifact template discovery | `registry/templates.yaml` record schema | reuse-as-is | `F-017` establishes the schema and `F-029` the one-record-per-contract pattern; the change adds a record and alters no field |
| Gate assessment surface | The Review Gate and Verification Gate rows and the producer exclusion rule in `workflows/workflow-gate-matrix.md` | reuse-as-is | `F-010` and `F-011` establish both. The role produces evidence assessed at gates that already exist and already have owners, so `C-010` is satisfied without a gate change |
| Host invocation surface | The host registration pattern and adapter surface recorded in `runtime/README.md` | reuse-as-is | `F-025` names the host registration as one of four invocability conditions and `F-022` records the adapter as implemented. The role reuses the pattern rather than defining one, with activation deferred under `D-003`, which is why `M-003` is speculative |
| Validation of the emitted artifact | The runtime Validation Engine | reuse-extended | `F-022` records coverage of one artifact type today. The review artifact needs coverage, which extends the existing engine rather than adding a second validation path. The extension is designed by `omn-qa` at `P-010`, not here |
| Review coverage measurement | `registry/agents.yaml`, `registry/skills.yaml`, `registry/workflows.yaml`, `registry/templates.yaml`, `agents/capability-matrix.md`, `workflows/workflow-gate-matrix.md`, and `runtime/README.md` were all searched | none-found | No framework record carries a coverage measure or a baseline. No new structure is proposed for it: `C-015` makes the measure negotiable and `A-004` records the assumed form, so the need is routed as `Q-009` rather than designed |

New structure appears in exactly two places, `M-002` and `M-006`, and each is licensed by a
row above. `M-006` is licensed by the `rejected` row, where both registered templates were
examined. `M-002` is licensed by the `reuse-as-is` row on contract structure: the module set
is a new instance of an existing pattern, not a new pattern. No capability whose candidate was
left unexamined receives new structure.

## Operational Considerations

Logging and observability: no observability surface is added. `F-022` establishes the run
evidence path already recorded for the runtime, and registration alone produces no new signal.
The one operational record that must change is `M-013`, whose known-gaps entry becomes wrong
the moment `M-001` gains a third record, which is why `P-013` exists and `R-011` tracks it.

Error handling strategy: the failure modes introduced are registry resolution failures at
`M-001` and `M-007`, namely a specification path that does not resolve to an existing file and
a declared dependency that does not resolve to an existing active record, both governed by
`C-004`. The design prevents rather than handles them: `P-007` places the template file before
`P-008` registers the record that names it, and `P-008` places the template record before
`P-011` registers the agent record that depends on it. The second failure mode is skill
resolution under `C-005`, where a phase whose skills do not all resolve does not start; this is
why the owning phase at `M-009` is settled at `P-014` and not assumed earlier.

Security considerations: the change introduces one durable artifact that reproduces content
drawn from reviewed material, at `M-006`. `C-013` bounds that reproduction and `D-002` places
the rule inside the artifact contract, so a finding cites location and describes the defect and
reproduces reviewed content only as far as identification requires. `R-008` tracks the case
where the contract is emitted without the rule. No credential, secret, authentication, or
authorization surface is introduced: under `A-003` the role consumes supplied inputs and
produces one artifact, and `F-025` lists no retrieval condition among the four that make an
agent invocable. Compliance impact is limited to `C-013`, because the change alters framework
records rather than any system that processes regulated data.

Performance considerations: no performance constraint is recorded for this change and none is
implied by any statement. The change adds declarative records and one artifact contract. The
only measured quantity in scope is `C-015`, which is a proportion with no target, so this
design makes no performance claim and sets no performance expectation.

Deployment and operability impact: the role becomes discoverable at `P-011` and remains
unroutable until `P-014`, which `D-003` records deliberately and `R-009` tracks. That state is
recorded in the governance rows produced at `P-006` so that a reader can distinguish a
deliberately absent owning phase from an oversight, which is the distinction `M-011` and
`C-005` together make load-bearing.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The review role's responsibility boundary against the existing review ownership is decided and recorded, including the disposition of the superseded contract and the identifier the new role carries | M-004, M-005, M-008 | none | Every governance row, capability declaration, and criteria set binds to the ownership split; deciding it later forces every dependent record to be rewritten | T-001 |
| P-002 | The reviewed-artifact set, the review dimension set, and the coverage measure are confirmed by the requester | M-002, M-006 | none | `A-001`, `A-002`, and `A-004` are unconfirmed, and the accepted input types and the artifact's per-dimension register bind directly to the confirmed sets | T-009 |
| P-003 | The role's authority scope, accepted input types, declared capabilities, out-of-scope boundaries, and runtime-invocability expectation are defined | M-002 | P-001, P-002 | Declared capabilities must be drawn from the existing capability set under `C-002` and accepted inputs from the confirmed artifact set; a module set cannot be authored against an undefined scope | T-002 |
| P-004 | The criteria for all five review dimensions are stated, each with an observable condition, the evidence that settles it, and the severity assigned when it fails | M-002, M-006 | P-001 | The artifact's per-dimension outcome register and its severity model bind to these; the artifact contract cannot fix a severity model before the severities exist | T-010, T-011, T-012, T-013, T-014 |
| P-005 | The review-result artifact contract is defined, covering the per-dimension outcome requirement, the finding identifier scheme, the severity model, closure semantics, and the bounded-reproduction rule for reviewed content | M-006 | P-003, P-004 | Contract definition precedes every consumer change; the module set, the template record, and the validation coverage all bind to this shape | T-003 |
| P-006 | The governance records carry the role with each review capability resolving to exactly one Primary owner and the superseded rows marked and retained | M-004, M-005, M-008 | P-003 | A contract may declare only capabilities the matrices already own under `C-002`, and a second Primary owner would breach `C-003` the moment the contract is authored | T-004 |
| P-007 | The review-result template exists at the shape defined by `P-005` | M-006 | P-005 | The template record's specification path must denote an existing file before any record claims it does, per `C-004` | T-003, T-006 |
| P-008 | The review-result template record is registered | M-007 | P-007 | The agent record's declared data dependency must resolve to an existing active record under `C-004`, so the template record precedes the agent record | T-006 |
| P-009 | The review contract module set exists with a declared load order in which every named module resolves | M-002 | P-005, P-006 | The agent record's specification path resolves to the manifest, and the manifest's load order must resolve before a record asserts that it does | T-005 |
| P-010 | Validation coverage exists for contract conformance, artifact conformance, module-set resolution against the loader contract, repeat-run identity of structure and finding identifiers, and negative cases for each declared out-of-scope boundary | M-002, M-006 | P-009 | Verification of a boundary precedes work that assumes the boundary holds, and `C-016` is unevidenced until a repeat-run comparison exists | T-007 |
| P-011 | The review agent record is registered | M-001 | P-008, P-009 | `C-004` requires the specification path to resolve and every declared dependency to resolve to an existing active record; both must exist first | T-006 |
| P-012 | The reference migration for the superseded review identifier is completed, or its remaining references are recorded | M-004, M-005, M-008, M-010 | P-011 | The superseded rows are retained only while references still name them; retiring them before the references are rewired breaks resolution under `C-012` | T-008 |
| P-013 | The runtime current-state record reflects the added registration surface and the corrected registration state | M-013 | P-011 | `runtime/README.md` is the current-state record for registration and invocation; leaving it stale leaves a second, contradicting authority for the same property, which `C-001` forbids | T-008 |
| P-014 | The host registration and the owning workflow phase for the review role are established | M-003, M-009 | P-010, P-011 | Dispatchability requires the record, the manifest, the host registration, and a routing phase together per `F-025`; enabling routing before validation coverage exists would attach an unverified contract to a live phase | none |

These are structural constraints, not tasks. `Binds` names the tasks in the supplied execution
plan that each constraint governs; those identifiers belong to `planner` and none is created
here. `P-014` binds no supplied task because the plan records dispatchability as deferred,
which `D-003` confirms as the design position rather than an omission.

### Test Strategy Focus Areas

For `omn-qa`, targeting `P-010`:

- Module-set resolution against the loader contract: the declared load order names every
  module in the set, and every named module exists.
- Registry resolution: the agent record's specification path resolves, every declared
  dependency resolves to an existing active record, and the template record's specification
  path denotes an existing file. This is the `C-004` surface and the direct evidence against
  `R-002`.
- Single-Primary resolution: `code-review` and `governance-enforcement` each resolve to
  exactly one Primary owner across `M-004` and `M-005`, throughout the coexistence period and
  not only at its end. This is the direct evidence against `R-003`.
- Artifact conformance: an emitted review result carries an explicit recorded outcome for every
  declared dimension, with no dimension silently absent.
- Determinism: a repeat-run comparison over identical inputs and an identical context snapshot
  evidences an identical section set and identical finding identifiers, per `C-016` and
  `R-012`.
- Bounded reproduction: an emitted artifact does not reproduce reviewed content beyond the rule
  stated at `P-005`, per `C-013`.
- Negative cases for each declared out-of-scope boundary, including that the role declines to
  approve a gate for an artifact it produced, per `F-011`.
- Reference resolution during coexistence: a document naming the superseded identifier still
  resolves at every point in the sequence, per `C-012`.

### Rollout and Rollback

- Rollout: follow `P-001` through `P-013`. `P-014` is deferred pending acceptance of `D-003`
  and an answer to `Q-005`.
- Rollback: reverse the registration order, removing the agent record from `P-011`, then the
  template record from `P-008`, then clearing the supersession markers from `P-006`. Because
  the superseded rows are retained at every step rather than replaced, every reference naming
  the superseded identifier resolves at every point in both directions, so rollback from any
  step returns the framework to two registered agents and unchanged review ownership with no
  unresolved reference and no orphaned record.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | The review contract declares a capability identifier absent from `agents/capability-matrix.md` | The role registers but capability resolution fails and ownership becomes unverifiable, breaching `C-002` | medium | M-002, M-004, D-004 | `P-006` records ownership using existing identifiers only and precedes `P-009`, so the contract is authored against recorded ownership rather than intended ownership | omn-tech-lead |
| R-002 | contract | The agent record is registered before the template record, so its declared data dependency does not resolve to an existing active record | Registry validation rejects the record under `C-004` and the role is undiscoverable | medium | M-001, M-007, P-011 | `P-008` precedes `P-011` in the sequencing constraints, and `P-010` verifies dependency resolution before registration is relied on | omn-tech-lead |
| R-003 | structural | Both the new and the superseded identity are left carrying Primary for the same review capability during the coexistence period | Two authorities for one ownership question, breaching `C-001` and `C-003` for the duration | medium | M-004, D-001 | `P-006` marks the superseded row rather than duplicating the Primary rating, and `P-012` completes the rewiring | omn-tech-lead |
| R-004 | migration | The coexistence period has no enforced end and the superseded rows become permanent | The framework carries two review identities indefinitely, which is the condition `C-001` exists to prevent | medium | M-008, P-012 | The retirement condition is recorded in the API and Data Model Impact section, and `P-012` records remaining references explicitly when the rewiring is incomplete rather than closing silently | omn-tech-lead |
| R-005 | contract | `A-002` is false and the confirmed dimension set differs from the five named | The artifact's per-dimension outcome register and the criteria set change after the contract at `P-005` is fixed | medium | M-006, P-004, P-005 | `P-002` confirms the dimension set and precedes both `P-004` and `P-005` | omn-product-owner |
| R-006 | contract | `A-001` is false and the reviewed-artifact set differs from the registered plan and design artifacts | The role's accepted input types change and the authority scope at `P-003` is restated after the module set binds to it | medium | M-002, P-003 | `P-002` confirms the reviewed-artifact set and precedes `P-003` | omn-product-owner |
| R-007 | delivery | `A-005` is false and acceptance requires the role to be dispatchable at run time | `P-014` moves from deferred into scope and the role cannot be accepted at registration, reversing `D-003` after governance rows have changed | medium | M-003, D-003 | `P-003` states the invocability expectation explicitly, so the expectation is settled before the contract is authored rather than discovered at acceptance | omn-tech-lead |
| R-008 | security | The review artifact contract is emitted without a bounded-reproduction rule for reviewed content | Restricted content present in reviewed material is copied into a durable framework artifact, breaching `C-013` | low | M-006, D-002 | `P-005` states the bounded-reproduction rule as part of the artifact contract, and `P-010` covers it as a verification target | omn-dev-2-reviewer |
| R-009 | operability | The role is registered while no registered workflow declares a phase it owns | The role is discoverable but unroutable, and no run can exercise the records produced at `P-011` | high | M-001, M-009, D-003 | `D-003` records the condition deliberately rather than leaving it accidental, `P-006` records the absent owning phase in the governance rows so a reader can see it, and `P-014` carries the remedy | omn-tech-lead |
| R-010 | structural | The host registration surface this role requires differs from the pattern the registered agents use, so the speculative impact at `M-003` materializes differently than analyzed | `P-014` does not resolve and dispatchability stays blocked after registration has already changed the governance records | medium | M-003, P-014 | `P-010` verifies module-set resolution against the loader contract before `P-014` relies on it | omn-tech-lead |
| R-011 | operability | The known-gaps record in `runtime/README.md` continues to state registration and skill-resolution facts that the registries contradict, per `F-030` | A reader takes the stale record as current and concludes the role cannot be registered or the owning phase cannot run | medium | M-013, P-013 | `P-013` updates the current-state record after `P-011`, and the divergence is recorded as `Q-006` with a named owner rather than reconciled by this design | omn-tech-lead |
| R-012 | contract | The artifact contract is emitted without a finding identifier scheme that is stable across runs | Repeat runs assign different identifiers and `C-016` fails after the contract is registered | medium | M-006, P-005, P-010 | `P-005` fixes the scheme as part of the contract, and `P-010` evidences it by repeat-run comparison | omn-qa |
| R-013 | delivery | The requester reads `S-001` as registering the existing review role rather than adding a new one, reversing `C-007` | `O-003` becomes the correct selection and `D-001` is reversed after governance rows have already changed | low | D-001, P-001 | `Q-001` routes the reading to its owner, and it is answered before `P-006` changes any governance row | omn-product-owner |
| R-014 | structural | `A-003` is false and the role requires a retrieval capability for the code changes it reviews | The accepted input set and the runtime surface both change, and the required capability is absent from `agents/capability-matrix.md`, which `C-002` forbids inventing | low | M-002, P-003 | `P-003` fixes the accepted input types as supplied data, and any retrieval need is recorded as a framework gap rather than met with an invented identifier | omn-tech-lead |
| R-015 | delivery | The coverage measure confirmed at `P-002` requires a measurement surface the framework does not have, per the `none-found` row in the reuse survey | Acceptance depends on a surface no framework record provides, and measurement work enters scope after the contract is fixed | low | P-002 | `P-002` records the measure together with a baseline or an explicit statement that none exists, and `Q-009` routes the surface question to its owner | omn-product-owner |

## Estimate and Confidence

- Overall: `L` (confidence: medium).

`L` because the change crosses four boundaries, the agent registry, the template registry, the
governance matrices, and the contract module set, and carries a coexistence obligation for the
superseded identifier. Not `XL`, because no structural decision remains unresolved that blocks
selection: the deferred routing is a recorded decision at `D-003`, not an open one.

- Breakdown:

| Constraint | Level | Confidence | Basis |
|---|---|---|---|
| P-001 | M | medium | One ownership decision recorded consistently across three records |
| P-002 | S | low | Requester confirmation; depends on unconfirmed `A-001`, `A-002`, and `A-004` |
| P-003 | M | low | Authority scope depends on unconfirmed `A-001`, `A-003`, and `A-005` |
| P-004 | M | medium | Five criteria sets, each requiring an observable condition, settling evidence, and a severity |
| P-005 | M | low | Artifact contract binds to the dimension set confirmed at `P-002`, so it inherits `A-002` |
| P-006 | S | medium | Additive rows plus supersession markers on records whose shape is established by `F-006` and `F-020` |
| P-007 | S | medium | One template file at a contract-defined shape |
| P-008 | XS | high | One additive registry record against an unchanged schema |
| P-009 | L | medium | A complete contract module set across a declared load order, matching the pattern in `F-004` |
| P-010 | M | medium | Validation coverage including determinism and negative boundary cases |
| P-011 | XS | high | One additive registry record against an unchanged schema |
| P-012 | M | low | The number of documents naming the superseded identifier is not established by the supplied context |
| P-013 | XS | high | One current-state record corrected against the registries |
| P-014 | M | low | Deferred; depends on the speculative impact at `M-003` and on `Q-005` |

- Scope assumptions: the estimate covers `P-001` through `P-013` and assumes `A-001`, `A-002`,
  `A-003`, and `A-005` hold. It excludes `P-014`, any exercise of the role on real work under
  `C-014`, registration of a skill for the framework-governance dimension, extension of the
  runtime validation engine beyond the coverage designed at `P-010`, and any change to gate
  ownership under `C-010`.
- Uncertainty drivers: the number of framework documents naming the superseded review
  identifier is not established by the supplied context, which drives `R-004` and holds `P-012`
  at low confidence; the host registration surface for a third registered agent is speculative
  at `M-003`, which drives `R-010`; and the reviewed-artifact set and dimension set are
  unconfirmed assumptions, which drive `R-005` and `R-006` and hold the overall confidence at
  medium rather than high.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does adding a Reviewer Agent require a new agent identity, or is registering the existing review role under its current identifier an acceptable reading of the request? | No | omn-product-owner | D-001, P-001, M-008 | If a new identity is required, `C-007` holds and `O-001` stands. If registering the existing identifier is acceptable, `C-007` relaxes and `O-003` becomes the selection, with a smaller impact surface, higher reuse leverage, and no reference migration at all |
| Q-002 | Which registered artifacts constitute the implementation plans the role reviews? | No | omn-product-owner | A-001, M-002, P-002, P-003 | Confirms or replaces `A-001`. A wider set widens the accepted input types and the criteria surface, and re-scopes `P-003` |
| Q-003 | Are the five named review dimensions the complete coverage set for the first version of the role? | No | omn-product-owner | A-002, M-006, P-004, P-005 | Confirms or replaces `A-002`. Additional dimensions add outcome rows to the artifact contract and criteria to the module set, after both are otherwise fixed |
| Q-004 | Is dispatchability at run time required for this change to be accepted? | No | omn-tech-lead | A-005, D-003, M-003, P-014 | If not required, `P-014` stays deferred as designed. If required, `P-014` enters scope and acceptance waits on a host registration and an owning workflow phase |
| Q-005 | Which registered workflow and phase will own the role's execution, given that the gate matrix names a review-pull-request Readiness Gate while `registry/workflows.yaml` holds no record for that workflow? | No | omn-tech-lead | M-009, M-011, P-014 | Determines whether the role attaches to an existing `implement-feature` phase, which would make `M-009` a contract change, or requires a workflow record that does not exist today |
| Q-006 | Which record is current where `runtime/README.md` and the registries disagree, per `F-030`? | No | omn-tech-lead | M-013, P-013 | `C-001` makes the registries authoritative for registration state, so confirming this makes the known-gaps entry a stale narrative to correct at `P-013` rather than a constraint on the design. If the README is instead current, the registries are wrong and a registry correction precedes `P-011` |
| Q-007 | Does the framework-governance review dimension require a registered skill identifier, given that neither the Skill Catalog nor the skill registry contains one? | No | omn-tech-lead | M-005, P-004, D-004 | If a skill is required, a skill registration enters scope ahead of `P-004`. If not, the dimension is carried by the contract's own criteria as `D-004` designs |
| Q-008 | Does consolidating Primary ownership of Quality Verification on `omn-qa` require confirmation from the capability matrix owners before `P-006`? | No | omn-tech-lead | D-005, M-004, P-006 | `C-011` requires the accountability change to be surfaced as a decision, which `D-005` does. If explicit confirmation is also required, `P-006` waits on it |
| Q-009 | Is a review coverage measurement surface required by this change, given that the reuse survey found none in any framework record? | No | omn-product-owner | A-004, P-002 | If required, a measurement surface enters scope and `C-015` becomes a design obligation rather than a recorded form. If not, `P-002` records that no pre-adoption baseline exists |

Decision records `D-001`, `D-002`, and `D-003` remain at status `Proposed` and require Design
Gate acceptance before `P-006` changes any governance record. Under the producer exclusion rule
in `workflows/workflow-gate-matrix.md`, acceptance rests with `omn-tech-lead`, because the
architecture role produced them.

No implementation work was performed by this agent. No production code, test, migration,
script, or configuration was written, no application module was edited, and no external system,
repository, or ticketing tool was accessed. All context was consumed from the frozen input and
context snapshot recorded in the metadata block.

## Sign-off

- Architect: omn-architect, the architecture role implemented by `architect`; producing role,
  excluded from accepting this package under the producer exclusion rule
- Tech Lead: omn-tech-lead, accepting owner for the Design Gate
- QA: omn-qa, for the verification implications at `P-010`
- Product confirmation: omn-product-owner, for `Q-001`, `Q-002`, `Q-003`, and `Q-009`

Design Gate owners are `omn-architect` and `omn-tech-lead` per
`workflows/workflow-gate-matrix.md`. Because the architecture role produced this package, the
producer exclusion rule applies and acceptance rests with `omn-tech-lead`. Lines are left
unsigned by the producing agent.
