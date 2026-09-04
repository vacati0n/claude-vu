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
      reference: runs/run-c5a8d50d3238/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003, D-004]
  consumesPlan: runs/run-c5a8d50d3238/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:da4a20cbe33a60d23ff785c2b8f49124
  contextDigest: sha256:c03357d6457b8908d5f91f96d183273e
```

## Metadata

- Feature or Change ID: reviewer-agent
- Author: architect
- Reviewers: omn-tech-lead, omn-qa
- Last Updated: 2026-08-18

## Objective

Desired structural outcome: the framework gains one registered, routable role accountable
for reviewing implementation plans and code changes, whose single deliverable is a
registered artifact carrying an explicit result for each declared review dimension, and
whose authority is disjoint from architecture decision authority and gate approval
authority.

Architectural objectives:

- AO-1: After the change, each capability identifier in the code-review and governance
  group has exactly one Primary owner, and exactly one role is accountable for reviewing
  the two named artifact types. Traces to `S-001`, `S-009`, `S-010`, `S-016`.
- AO-2: The review outcome is a first-class registered artifact with a fixed structure
  carrying one result position per declared dimension, readable without reconstructing what
  was reviewed or what the verdict was. Traces to `S-011`, `S-012`, `S-014`, `S-020`.
- AO-3: The reviewer resolves through the framework's existing discovery chain — registry
  record, manifest module set, host registration, phase routing, registered validator —
  without introducing a second authority for identity metadata. Traces to `S-001`, `S-015`.
- AO-4: The reviewer's declared authority is disjoint from architecture decision authority,
  gate approval authority, and implementation authority, so no structural question acquires
  a second owner. Traces to `S-010`, `S-013`, `S-016`.
- AO-5: The reviewer's reviewed-artifact inputs resolve to named framework artifacts rather
  than to prose categories. Traces to `S-002`, `S-003`.

In structural scope: a new agent module set and host registration; the agent discovery
record; capability ownership and skill coverage records; the `quality-review` phase row of
`implement-feature` and the workflow record's dependency declaration; the Producer
Exclusion note for the Review Gate; a new review outcome template and its template record;
a registered validator for that artifact; and the narrowing of the existing review-owning
role's declared accountability.

Out of structural scope, which bounds the impact surface before analysis begins:

- The agent dispatch and adapter mechanism. No statement requests a change to it, and it
  already routes any agent satisfying the invocability chain (`F-004`, `F-011`).
- Gate ownership transfer. `C-003` forbids it without an authorizing decision, and the
  selected approach requires none.
- Review dimensions beyond the five named. `S-004` through `S-008` enumerate five and
  `S-017` sets no coverage target.
- Exercising the reviewer on real work. Excluded by `S-018`.
- Capability registration for `scope-and-acceptance`, `implementation`, and
  `documentation-and-release-handoff`. They remain blocked at `G1-CAPABILITY` (`F-010`);
  this change unblocks `quality-review` only.
- The runtime's absent retry, recovery, and cancellation surfaces (`F-014`). They constrain
  this design's error handling but are not changed by it.
- Reviewer participation in `fix-bug`, `review-pull-request`, `refactor`, `investigate`, and
  `release`. Deferred by `A-003`.

## Requirements Summary

Functional requirements:

- One accountable framework role reviews implementation plans and code changes before they
  progress (`S-001`, `S-002`, `S-003`, `S-010`).
- The role states an explicit outcome for each of the five named review dimensions:
  architecture compliance, coding quality, testing strategy, security, and framework
  governance (`S-004`, `S-005`, `S-006`, `S-007`, `S-008`, `S-011`).
- A governed change carries a recorded verdict from the review role (`S-013`).
- The role is discoverable through the framework's own discovery surfaces on the same terms
  as already-registered roles (`S-015`).

Non-functional requirements:

- Review results are consumable by the delivery and quality roles that act on them, without
  a reader reconstructing what was reviewed or what the verdict was (`S-012`).
- Coverage is expressed as a measured proportion and is not committed to at a numeric level
  (`S-017`).
- The change adds a role and does not change any existing role's accountability without
  that being surfaced as a decision (`S-016`).

Acceptance intent: cited from the supplied business intent rather than restated — an
emitted review result records an outcome for every declared review dimension (`S-014`), a
governed change carries a recorded verdict (`S-013`), and the role is discoverable on the
same terms as registered roles (`S-015`). The supplied execution plan's acceptance criteria
are the planner's and are not reproduced here.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The framework is composed of five component types — agents, skills, workflows, templates, commands — each with a discovery registry and a specification set | Architecture context; `registry/agents.yaml`, `registry/skills.yaml`, `registry/workflows.yaml`, `registry/templates.yaml` |
| F-002 | `registry/agents.yaml` holds two records, `planner` and `architect`, both at status `active`, each resolving to a runtime module set at `agents/<identifier>/manifest.yaml` | `registry/agents.yaml`; architecture context assertion 1 |
| F-003 | `registry/agents.yaml` validates with `failOnUnknownFields`, `requireAllFields`, and `enforceDependencyResolution` all true, over a record schema requiring identifier, displayName, description, version, status, specificationPath, dependencies, tags, owner, and capabilities | `registry/agents.yaml` |
| F-004 | An agent becomes invocable when it holds an active registry record, a manifest with a resolvable module load order, a host registration at `agents/<agent-id>.agent.md`, and a workflow phase that routes to it with an output artifact the runtime can validate | Architecture context assertion 2 |
| F-005 | Review responsibility today sits with `omn-dev-2-reviewer`: Primary for Code Review and Governance in `agents/capability-matrix.md`; sole owner of the `implement-feature` Review Gate, the `fix-bug` Fix Gate, and the `review-pull-request` Readiness Gate; and holding no record in `registry/agents.yaml` | `agents/capability-matrix.md`; `workflows/workflow-gate-matrix.md`; `registry/agents.yaml`; architecture context assertion 3 |
| F-006 | `agents/capability-matrix.md` maps the Code Review and Governance column to the capability identifiers `code-review` and `governance-enforcement`, and requires a capability identifier to exist in that table before any agent manifest, registry record, or execution plan references it | `agents/capability-matrix.md` |
| F-007 | `agents/capability-matrix.md` records ownership against eleven coarse columns rather than against the fine-grained capability identifiers it maps them to, and several columns carry more than one Primary: Quality Verification names `omn-dev-2-reviewer` and `omn-qa`; Architecture and Design names `architect`, `omn-architect`, and `omn-tech-lead` | `agents/capability-matrix.md` |
| F-008 | The `implement-feature` Phase Model declares `quality-review` as a canonical phase owned by `omn-dev-2-reviewer`, with Input "code diff, test evidence, design references", Output Artifact "review findings log, verification report", gates Review Gate and Verification Gate, and required skills S07, S09, S08 | `workflows/implement-feature.md` |
| F-009 | A phase in `implement-feature` resolves to exactly one owner agent, and an owner agent shipping a runtime manifest must declare that workflow and phase identifier in `supportedWorkflows`; the runtime rejects a mismatch rather than guessing | `workflows/implement-feature.md` |
| F-010 | The runtime executes `execution-planning` and `solution-design-and-risk-assessment`; the other four `implement-feature` phases are enqueued and blocked at guard `G1-CAPABILITY` with reason `awaiting_capability_registration`, so a run reaches a waiting state rather than completion. Only `implement-feature` carries canonical phase identifiers | `runtime/README.md`; architecture context assertion 4 |
| F-011 | Guard `G1-CAPABILITY` requires an active registry record, a manifest declaring this workflow and phase, a host registration, resolvable phase skills, and a registered validator; guards are a pure function of persisted state, so re-evaluating them produces the same verdicts | `runtime/README.md` |
| F-012 | The Validation Engine is partial and covers two artifact types, `execution-plan.md` and `technical-design.md`, through per-artifact validators | `runtime/README.md` |
| F-013 | The `implement-feature` phase graph derives hard edges from the Input and Output Artifact columns of the Phase Model table, falling back to row adjacency when no earlier Output Artifact is named in a later phase's Input column | `runtime/README.md` |
| F-014 | The runtime implements no retry, no recovery pass, and no cancellation; a rejected artifact blocks with reason `awaiting_recovery_task`, and committed evidence is immutable | `runtime/README.md` |
| F-015 | `registry/templates.yaml` holds three active records — `execution-plan`, `technical-design`, `architecture-decision-record` — and no record covering a review outcome artifact | `registry/templates.yaml` |
| F-016 | `registry/workflows.yaml` declares the `implement-feature` record's dependencies as `planner`, `architect`, `execution-plan`, and `technical-design`, and validates with `enforceDependencyResolution` true | `registry/workflows.yaml` |
| F-017 | `workflows/workflow-gate-matrix.md` states the Producer Exclusion Rule: an agent may not approve a gate for an artifact it produced, even when its role appears in that gate's owner list, and approval then requires a different listed owner | `workflows/workflow-gate-matrix.md` |
| F-018 | `omn-dev-2-reviewer` is the sole required owner of the `implement-feature` Review Gate | `workflows/workflow-gate-matrix.md` |
| F-019 | `skills/agent-skill-matrix.md` catalogues twelve skill identifiers; S01, S02, S03, S06, S07, S08, S09, S11, and S12 resolve as active records in `registry/skills.yaml`, while S04, S05, and S10 are unregistered | `skills/agent-skill-matrix.md` |
| F-020 | For an agent shipping a runtime manifest the manifest `skills` block is authoritative for that agent's declared skills, while `skills/agent-skill-matrix.md` remains authoritative for workflow-phase requirements; divergence is recorded in the matrix's Declaration Precedence delta table | `skills/agent-skill-matrix.md` |
| F-021 | `agents/capability-matrix.md` records `omn-architect` as deprecated in favour of `architect` while retaining its matrix row so that documents still naming it resolve during the migration | `agents/capability-matrix.md` |
| F-022 | `dependency-map.md` records the permitted dependency directions Commands to Workflows, Workflows to Agents, Workflows to Skills, and Agents to Skills, and classifies Workflows to Agents to Workflows as an intentional governance loop | `dependency-map.md` |
| F-023 | `domain-model/agent-specification.md` requires an agent to declare Agent ID, Name, Domain Role, Authority Scope, Supported Workflow Phases, Input Contract, Output Contract, Decision Rights, Escalation Targets, Status, and Version, and constrains the framework to one primary owner per task scope | `domain-model/agent-specification.md` |
| F-024 | The supplied execution plan decomposes the change into fourteen tasks `T-001` through `T-014` across seven waves and assigns `T-002` and `T-010` to `architect` | Supplied execution plan |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | "Implementation plans" in `S-002` denotes the registered `execution-plan` artifact, and "code changes" in `S-003` denotes the change set produced by the `implementation` phase of `implement-feature` | The reviewer's declared input types must resolve to named framework artifacts (`F-008`, `F-015`) rather than to prose categories | The declared input types and the outcome contract change after the authority scope is set, re-scoping `M-001` and `M-009` | omn-business-analyst |
| A-002 | The five named dimensions are the complete required review coverage for the first version | The outcome contract fixes one result position per dimension, so the count must be closed before the contract is written | The outcome contract, its template, and the validation coverage all expand, re-scoping `M-009` | omn-product-owner |
| A-003 | The reviewer's first workflow surface is `implement-feature`; participation in other registered workflows is deferred | Phase routing must name a workflow whose phase identifiers are canonical (`F-009`, `F-010`) | The impact surface expands into workflows whose phase identifiers are not canonicalized, so routing cannot be built for them | omn-product-owner |
| A-004 | `omn-dev-2-reviewer` holds no registry record because it has not been migrated to the runtime module pattern, not because its role is retired | The ownership disposition depends on whether the existing role is live; `F-005` establishes the absence of a record but not its cause | The narrowing disposition is unavailable, only full supersession remains, and `M-017` and `M-018` become contract changes | omn-tech-lead |
| A-005 | The Validation Engine can register a validator for a third artifact type without a change to the invocation gateway or the adapter | `G1-CAPABILITY` requires a registered validator (`F-011`) and the engine covers two artifact types today (`F-012`) | `G1-CAPABILITY` never passes for `quality-review`, so the reviewer is registered but not dispatchable and `M-011` is not a viable impact | omn-tech-lead |
| A-006 | The framework-governance review dimension is assessed against the framework's own registries, matrices, and contract module sets rather than against an external policy corpus | The dimension has no stated definition, and the outcome contract must state what it is assessed against | The reviewer gains an additional declared input type and an external dependency, and the reuse outcome for governance coverage changes | omn-business-analyst |
| A-007 | The review outcome is evidence assessed at a gate, not the gate decision itself | `F-017` and `F-018` together determine whether one agent could both produce the evidence and approve the gate | Gate ownership entries change, which `C-003` requires be recorded as a decision naming the gate matrix owners | omn-tech-lead |
| A-008 | The framework maintains documentation surfaces that enumerate agents and must carry an entry for a newly added agent | `S-015` requires discoverability on the same terms as registered roles, and the frozen context slice contains no documentation-surface member establishing where agents are enumerated | `M-013` becomes `no-change-verified` and `P-016` narrows to release-impact notes only | omn-documentation |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | Structural | The framework's discovery registries are single-authority; a second authority for the same identity metadata is a defect, not a design option | Hard | Architecture context; `F-001` |
| C-002 | Structural | Registration and governance records are contract surface; a change to one is a contract change, not an implementation detail | Hard | Architecture context |
| C-003 | Compliance | No change to gate ownership is authorized without being recorded as a decision naming the gate matrix owners | Hard | Architecture context; `S-016` |
| C-004 | Structural | Exactly one Primary owner exists for each capability identifier, and there is one primary owner per task scope | Hard | `F-006`, `F-023`, `S-010` |
| C-005 | Structural | An agent may not approve a gate for an artifact it produced | Hard | `F-017` |
| C-006 | Structural | A capability identifier exists in `agents/capability-matrix.md` before any manifest, registry record, or execution plan references it | Hard | `F-006` |
| C-007 | Functional | An emitted review outcome states an explicit result for each of the five named dimensions | Hard | `S-004`, `S-005`, `S-006`, `S-007`, `S-008`, `S-011`, `S-014` |
| C-008 | Functional | The reviewer reviews implementation plans and code changes | Hard | `S-002`, `S-003` |
| C-009 | Structural | An agent is invocable only with an active registry record, a manifest with a resolvable load order, a host registration, and a routed phase with a validatable output artifact | Hard | `F-004`, `F-011` |
| C-010 | Security | An emitted review outcome does not reproduce restricted content found in reviewed material | Hard | `S-012`; supplied execution plan risk `R-009` |
| C-011 | Migration | Existing routing continues to resolve during and after the change; no document naming the current review owner is left with an unresolvable reference | Hard | `F-021`, `C-002` |
| C-012 | Operability | A routed phase does not start unless every phase-mandatory skill resolves as an active record in `registry/skills.yaml` | Hard | `F-019`, `F-009` |
| C-013 | Quality-attribute | Coverage is expressed as a measured proportion and is not committed to at a numeric level | Negotiable | `S-017` |
| C-014 | Structural | The reviewer's declared authority does not overlap architecture decision authority, gate approval authority, or implementation authority | Hard | `S-010`, `S-016`, `F-023` |
| C-015 | Operability | A registered validator exists for the reviewer's output artifact before its phase can pass `G1-CAPABILITY` | Hard | `F-011`, `F-012` |
| C-016 | Functional | The role is discoverable through the framework's own discovery surfaces on the same terms as already-registered roles | Hard | `S-015` |
| C-017 | Functional | The change adds a role to the framework | Hard | `S-016` |
| C-018 | Functional | Exactly one accountable framework role reviews implementation plans and code changes | Hard | `S-009`, `S-010` |
| C-019 | Compliance | No existing role's accountability changes without that change being surfaced as a recorded decision | Hard | `S-016`, `C-003` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `agents/reviewer/` runtime module set (new) | extension | F-002, F-004, F-023 | Manifest `loadOrder`; declared authority scope, input contract, output contract, lifecycle states, self-verification checks | confirmed |
| M-002 | `agents/reviewer.agent.md` host registration (new) | extension | F-004, F-011 | Host-subagent adapter entry point | confirmed |
| M-003 | `registry/agents.yaml` record set | extension | F-002, F-003 | Agent discovery record set; record schema unchanged | confirmed |
| M-004 | `agents/capability-matrix.md` Code Review and Governance ownership | contract-change | F-005, F-006, F-007 | Capability ownership table; Capability Identifiers mapping | confirmed |
| M-005 | `skills/agent-skill-matrix.md` Agent to Skill Coverage row and Implement Feature phase row | contract-change | F-008, F-019, F-020 | Agent skill coverage row; phase Primary Agents and Required Skills cells; Declaration Precedence delta table | confirmed |
| M-006 | `workflows/implement-feature.md` Phase Model `quality-review` row and Phase Identifier Sources table | contract-change | F-008, F-009, F-013 | Owner Agent, Input, and Output Artifact cells; derived phase-graph edges | confirmed |
| M-007 | `registry/workflows.yaml` `implement-feature` record dependencies | contract-change | F-016 | Workflow record dependency array | confirmed |
| M-008 | `workflows/workflow-gate-matrix.md` Review Gate producer note | extension | F-017, F-018, A-007 | Producer Exclusion Rule section; Review Gate owner entry unchanged | confirmed |
| M-009 | `templates/review-outcome.md` (new) | extension | F-015, C-007 | Review outcome section set; one result position per declared dimension | confirmed |
| M-010 | `registry/templates.yaml` record set | extension | F-015 | Template discovery record set | confirmed |
| M-011 | Validation Engine validator registration for the review outcome artifact | extension | F-011, F-012, A-005 | Registered validator set for artifact types | speculative |
| M-012 | `agents/omn-dev-2-reviewer.md` declared authority scope | contract-change | F-005, A-004 | Declared accountability for review of the two named artifact types | confirmed |
| M-013 | Framework agent documentation surfaces | operational-impact | A-008 | Agent enumeration entries | speculative |
| M-014 | `registry/skills.yaml` record set | no-change-verified | F-019 | none | confirmed |
| M-015 | `dependency-map.md` | no-change-verified | F-022 | none | confirmed |
| M-016 | Runtime resolution chain, adapter, and phase-graph derivation in `runtime/framework_runtime.py` | no-change-verified | F-011, F-013 | none | confirmed |
| M-017 | `workflows/workflow-gate-matrix.md` `fix-bug` Fix Gate owner row | no-change-verified | F-005 | none | confirmed |
| M-018 | `workflows/workflow-gate-matrix.md` `review-pull-request` Readiness Gate owner row | no-change-verified | F-005 | none | confirmed |

Five entries are recorded `no-change-verified` because a reader would reasonably expect
them to be impacted and they are not. `M-014`: every skill the reviewer needs already
resolves as an active record, so no skill record is added (`F-019`). `M-015`: an added
agent is a new node inside dependency directions that already exist, so no direction
changes (`F-022`). `M-016`: the resolution chain, the single adapter, and the phase-graph
derivation resolve any agent satisfying `G1-CAPABILITY`, so the reviewer requires no change
to them; the only runtime-adjacent change is the validator registration in `M-011`.
`M-017` and `M-018`: the selected approach leaves the existing review owner active and
retains its gate ownership in the other two workflows, so those rows do not change. Under
the highest-scoring rejected alternative they would.

Boundary crossings recorded in the impact set: Workflows to Agents at `M-006` (phase
routing); Agents to Skills at `M-001` and `M-005` (declared skill dependency); Agents to
Templates at `M-001` and `M-009` (output binding); Runtime to Registries at `M-003`,
`M-007`, and `M-010` (resolution); Runtime to Validation Engine at `M-011`. Each crossing
follows a direction `F-022` already permits; none is introduced or reversed.

### 5.2 Options Considered

Options are derived from five distinct structural strategies, in the order those strategies
are declared by the analysis procedure: extend an existing boundary; introduce a new
boundary; relocate a responsibility; change a contract; change a dependency direction.

| Option | Structural change | C-004 | C-005 | C-014 | C-017 | C-018 | Quality attribute (C-013) | Impact surface | Reuse leverage | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | New `reviewer` agent takes review of the two named artifact types and the existing `quality-review` phase; `omn-dev-2-reviewer` is narrowed, not retired, and keeps its three gate ownerships | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | Neutral; C-013 is negotiable and non-numeric, so no option is distinguished by it | 5 | 10 | 5 | Unblocks `quality-review` at `G1-CAPABILITY`; three gate rows in two other workflows keep their current owner | Selected |
| O-002 | New `reviewer` agent plus a new review phase inserted into `implement-feature`, leaving `quality-review` and `omn-dev-2-reviewer` untouched | Satisfied | Satisfied | Satisfied | Satisfied | Violated | Neutral | 3 | 9 | 3 | Leaves `quality-review` blocked and adds a second review-bearing phase, so review resolves to two roles in one workflow | Eliminated on C-018 |
| O-003 | Migrate `omn-dev-2-reviewer` itself into the runtime module-set pattern; no new role is added | Satisfied | Satisfied | Satisfied | Violated | Satisfied | Neutral | 3 | 10 | 3 | Unblocks `quality-review` without adding a role, which is not the change the intent describes | Eliminated on C-017 |
| O-004 | New `reviewer` agent assumes every review accountability of `omn-dev-2-reviewer` across all workflows and gates; the existing role is deprecated with its row retained | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | Neutral | 8 | 10 | 8 | Unblocks `quality-review` but leaves two further workflows mid-migration, and their phase identifiers are not canonical, so their routing cannot be verified | Not selected |
| O-005 | Express review as a capability of the existing `architect` agent, with no new agent identity | Satisfied | Violated | Violated | Violated | Satisfied | Neutral | 4 | 11 | 4 | Would make one agent the reviewer of its own design output | Eliminated on C-005, C-014, C-017 |

Impact surface counts impacted modules carrying `contract-change` or `dependency-change`.
Reuse leverage counts capabilities in section 7 satisfied by `reuse-as-is` or
`reuse-extended`. Migration burden counts contract-affecting changes requiring a transition
strategy. `C-001`, `C-002`, `C-003`, `C-006` through `C-013`, `C-015`, `C-016`, and `C-019`
are satisfied by every option and are omitted as columns because they do not discriminate;
the five constraint columns shown are the hard constraints on which the options differ.

`O-002` violates `C-018` because two review-bearing phases in one workflow make two roles
accountable for the same artifacts. `O-003` violates `C-017` because promoting an existing
contract adds no role. `O-005` violates `C-005` because the agent would produce and then be
positioned to approve evidence about its own output, `C-014` because review authority would
sit inside architecture decision authority, and `C-017` for the same reason as `O-003`.

### 5.3 Selected Approach

- Selected: `O-001`.
- Structural change: a new `reviewer` agent is packaged as a runtime module set with a host
  registration and an active agent registry record. Primary ownership of `code-review` and
  `governance-enforcement` transfers to it; `omn-dev-2-reviewer` remains active, becomes
  Secondary for that group, retains Primary for Quality Verification, and retains ownership
  of the `implement-feature` Review Gate, the `fix-bug` Fix Gate, and the
  `review-pull-request` Readiness Gate. The existing `quality-review` phase of
  `implement-feature` is reused rather than replaced: its Owner Agent becomes `reviewer` and
  its Output Artifact becomes a new registered review outcome artifact, which a registered
  validator can check. The reviewer produces the evidence assessed at the Review and
  Verification Gates and approves neither.
- Rationale: `O-001` is one of two options satisfying every hard constraint, and it carries
  the smaller impact surface of the two. It is the only option that both adds a role
  (`C-017`) and leaves exactly one role accountable for the two named artifact types
  (`C-018`). It reuses the existing `quality-review` phase, so no phase identifier is
  invented and the phase that is blocked today is the phase that becomes routable. Because
  the Review Gate owner entry does not change, `C-003` is satisfied without a gate-ownership
  decision, and `C-005` holds trivially: the producer and the approver are different roles.
- Highest-scoring rejected alternative and why it lost: `O-004`, full supersession. It
  satisfies every hard constraint and reads as the natural meaning of "one accountable
  role", but retiring `omn-dev-2-reviewer` removes the owner of three gates across three
  workflows. Two of those workflows have no canonical phase identifiers (`F-010`), so their
  rewiring cannot be verified by routing and would land outside the approved first surface
  (`A-003`). Its impact surface is 8 against `O-001`'s 5, and its migration burden is 8
  against 5. Nothing in the requirements needs the existing role retired: `C-018` is about
  who reviews the two named artifact types, not about how many review-shaped roles exist.
- Tradeoffs accepted: two roles with review in their names coexist, which costs
  intelligibility and creates a standing risk that a later reader re-merges them. That cost
  is accepted because the alternative expands the change into two workflows the requirements
  do not reach. The design pays for it by making the split explicit in `M-004` and `M-012`
  and by recording the disposition as `D-001` rather than leaving it implied. A second
  tradeoff: the reviewer is Primary for a capability group whose gate is owned by the role it
  took that capability from. That is deliberate — it is what keeps `C-005` satisfied without
  changing a gate owner — but it means the Review Gate's owner and the phase's owner differ,
  which the gate matrix must state rather than leave to inference (`M-008`).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | The Reviewer Agent is introduced as a distinct registered agent `reviewer`; `code-review` and `governance-enforcement` Primary ownership transfers to it; `omn-dev-2-reviewer` is narrowed rather than retired and retains its three gate ownerships | Yes | ADR D-001, status Proposed |
| D-002 | The reviewer is routed through the existing `quality-review` phase of `implement-feature` rather than through a new phase, and that phase's Output Artifact becomes the review outcome | Yes | ADR D-002, status Proposed |
| D-003 | The review outcome is a new registered artifact with one result position per declared dimension, rather than being rendered into an existing registered template | Yes | ADR D-003, status Proposed |
| D-004 | The reviewer produces gate evidence and never approves a gate; the Review Gate owner entry is unchanged and the gate matrix records the reviewer as the producer of the evidence assessed there | Yes | ADR D-004, status Proposed |
| D-005 | The reviewer declares only skills that already resolve as active registered records — S01 for architecture compliance, S03 for coding quality, S07 for testing strategy, S09 for security — and proposes no new skill record; the framework-governance dimension is assessed against the framework's own registries and matrices per `A-006` | No | Inline. It creates no component, changes no contract, and is reversible by a manifest edit. Recorded here so the absence of a governance skill is visible rather than silent |

## API and Data Model Impact

In this system the interfaces are the record schemas and table columns that other
components read. The reviewer's own contract surface is `M-001` and `M-009`; the changes
below are to surfaces existing consumers already read.

API changes:

- `M-004` gains a `reviewer` row and demotes one cell of the existing owner's row. The
  Capability Identifiers mapping is unchanged, so no capability identifier is invented
  (`C-006`).
- `M-005` gains a `reviewer` row in Agent to Skill Coverage and changes the Primary Agents
  cell of the Implement Feature `quality-review` row.
- `M-006` changes the Owner Agent, Input, and Output Artifact cells of the `quality-review`
  row and adds a Phase Identifier Sources entry stating that the identifier originates in
  the reviewer's manifest.
- `M-007` adds two dependency entries to the `implement-feature` record: the reviewer as a
  control dependency and the review outcome template as a data dependency.
- `M-008` adds the reviewer case to the Producer Exclusion Rule section. No owner entry
  changes.
- `M-012` narrows the declared accountability of the existing review-owning contract.

Contract compatibility notes:

`M-004` capability ownership. Current shape: eleven coarse columns with `omn-dev-2-reviewer`
Primary for Code Review and Governance and no `reviewer` row. Target shape: a `reviewer` row
Primary for that column, with the existing owner Secondary for it and Primary retained for
Quality Verification. Compatibility approach: additive row plus one cell demotion; every
existing capability identifier keeps resolving. Coexistence period: from the matrix edit
until the existing role's contract text is aligned at `P-015`. Retirement condition: the
coexistence ends when `M-004` and `M-012` state the same disposition. Rollback position:
restore the Primary cell and remove the `reviewer` row; capability routing returns to the
current owner with no other surface affected.

`M-005` skill coverage. Current shape: no `reviewer` row; the `quality-review` row names
`omn-dev-2-reviewer` and `omn-qa` as Primary Agents and requires S07, S09, S08. Target
shape: a `reviewer` row, and the Primary Agents cell naming `reviewer`. Compatibility
approach: additive, and the Declaration Precedence rule (`F-020`) already governs any
divergence between the reviewer's manifest and this matrix, so a divergence is recorded in
the delta table rather than becoming a conflict. Coexistence period: none required.
Retirement condition: not applicable. Rollback position: remove the row and restore the
Primary Agents cell. Open point: the phase remains mandatory for S08 while performance is
not among the five dimensions, which is `Q-003` and `R-010`, not a compatibility break —
S08 resolves as an active record either way (`F-019`), so skill resolution still passes.

`M-006` phase row. Current shape: Owner Agent `omn-dev-2-reviewer`, Output Artifact "review
findings log, verification report", phase blocked at `G1-CAPABILITY`. Target shape: Owner
Agent `reviewer`, Input naming the registered plan artifact and the implementation change
set per `A-001`, Output Artifact naming the review outcome. Compatibility approach: the
phase identifier `quality-review` is unchanged, so every routing key that resolves today
keeps resolving, and the manifest of the new owner declares that same identifier as `F-009`
requires. The derived hard edge into `documentation-and-release-handoff` currently comes
from that phase's Input column naming "verification report"; once the Output Artifact is
renamed, the edge falls back to row adjacency under `F-013` rule 2, which yields the same
order, so the phase graph's shape does not change. Coexistence period: none — `F-009`
permits exactly one owner agent, so there is no dual-owner window. Retirement condition: not
applicable. Rollback position: restore the Owner Agent and Output Artifact cells; the phase
returns to blocking at `G1-CAPABILITY`, which is its current state (`F-010`), so rollback
returns the framework to today's behaviour with no residue.

`M-007` workflow record. Current shape: dependencies naming `planner`, `architect`,
`execution-plan`, `technical-design`. Target shape: the same plus the reviewer and the
review outcome template. Compatibility approach: purely additive, but `F-016` enforces
dependency resolution, so this edit is only valid after both referents are registered.
Coexistence period: none. Retirement condition: not applicable. Rollback position: remove
the two entries.

`M-008` gate matrix producer note. Current shape: a usage section naming the planner and
architect producer cases and a Producer Exclusion Rule naming the Design and Invariant
Gates. Target shape: the same sections additionally recording that the reviewer produces the
evidence assessed at the Review and Verification Gates and approves neither. Compatibility
approach: additive prose against unchanged owner entries, which is what keeps `C-003`
satisfied without a gate-ownership decision. Coexistence period: none. Retirement condition:
not applicable. Rollback position: remove the added sentences.

`M-012` existing review contract. Current shape: a contract holding accountability for code
review and governance, for quality verification, and for three gates, with no registry
record. Target shape: the same contract with review of the registered plan artifact and the
implementation change set held by `reviewer`, and with Quality Verification and the three
gate ownerships retained. Compatibility approach: every document naming
`omn-dev-2-reviewer` keeps resolving because the role stays active, so the deprecation
precedent recorded at `F-021` is not needed here. Coexistence period: from acceptance of
`D-001` until the narrowed text is recorded. Retirement condition: the period ends when
`M-004` and `M-012` agree; nothing is removed, so there is no marker to retire. Rollback
position: restore the original authority text together with the `M-004` cell.

Schema and data model changes: none in the persisted sense — the framework's records are
declarative documents, not a data store, and no record schema changes. There is one
migration-shaped effect on persisted run state, and it is the one an implementer is most
likely to miss. Guards are a pure function of persisted state and are re-evaluated on
demand (`F-011`), so a run that already holds a `quality-review` work item blocked at
`G1-CAPABILITY` will re-evaluate that guard after the phase row and its supporting records
change. Direction: forward-only, from `blocked` to `pending`, which the state model permits.
Reversibility: reversible by reverting `M-006` and `M-007`, after which the guard blocks
again. Reader and writer behaviour during transition: an in-flight run reads the registries
at the moment it re-evaluates, so a run can unblock partway through the sequence unless the
records it depends on are already complete; committed artifacts are immutable and are not
rewritten by any step here (`F-014`). `P-013` exists to make that window empty, and `R-005`
covers it if it is not.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Agent contract packaging | The runtime module-set pattern used by `planner` and `architect`: manifest, declared `loadOrder`, module set | reuse-as-is | `F-002` and `F-004` establish it as the packaging that makes an agent invocable, and `C-009` requires it. No alternative packaging is invocable |
| Agent discovery | `registry/agents.yaml` record set | reuse-as-is | `F-002`, `F-003`. `C-001` forbids a second authority for identity metadata, so the reviewer is discovered here or not at all |
| Host dispatch entry point | The `host-subagent` adapter reached through `agents/<agent-id>.agent.md` | reuse-as-is | `F-004`, `F-011`. One adapter exists and the registration is an entry point rather than a contract, so a new agent needs no adapter change (`M-016`) |
| Capability ownership expression | The Code Review and Governance column and its identifiers `code-review` and `governance-enforcement` | reuse-as-is | `F-006`. Both identifiers already exist and cover exactly what the reviewer does, so `C-006` is satisfied without inventing one |
| Review outcome artifact structure | `templates/technical-design.md`, `templates/execution-plan.md`, `templates/architecture-decision-record.md` | rejected | `F-015`. Each is bound to a different producer and a different section contract — a design package, a plan, and one decision. None carries a per-dimension result position, and `C-007` requires exactly five. Binding a review outcome to any of them would give one registered template two producers and two contracts, which is the single-authority defect `C-001` names, expressed at the artifact level. This row is what licenses the only new artifact structure in this design |
| Review outcome discovery | `registry/templates.yaml` record set | reuse-as-is | `F-015`. The new template is discovered through the existing template registry, not through a new index |
| Phase routing for review work | The existing `quality-review` phase of `implement-feature` | reuse-extended | `F-008`, `F-010`. The phase already exists, is canonical, and is blocked only at capability resolution. Extending it — naming a registered owner and a validatable output artifact — is precisely what unblocks it, and it means no phase identifier is invented |
| Gate evidence semantics | The Review Gate, the Verification Gate, and the Producer Exclusion Rule | reuse-extended | `F-017`, `F-018`. The rule already carries the architect and planner producer cases; the reviewer case is recorded in the same form. Owner entries are unchanged, which is how `C-003` is satisfied |
| Skill coverage for four of five dimensions | S01 clean-architecture-checklist, S03 engineering-playbook, S07 testing-strategy, S09 secure-engineering | reuse-as-is | `F-019`. All four resolve as active registered records, so `C-012` holds and `M-014` needs no change |
| Skill coverage for the framework-governance dimension | An existing registered skill covering framework governance | none-found | The search covered the twelve-row Skill Catalog in `skills/agent-skill-matrix.md` and the records it maps into `registry/skills.yaml`; no category covers framework governance, and the two uncatalogued skill files named there are release automation and coding style. No new skill is proposed: under `A-006` the dimension is assessed against the framework's own registries and matrices, and creating a skill record would extend the skill taxonomy, which `Q-007` routes rather than this design deciding |
| Artifact validation | The Validation Engine's per-artifact validator pattern already used for the two supported artifact types | reuse-extended | `F-012`. A third artifact type follows the same pattern; `A-005` carries the assumption that registering it needs no gateway or adapter change, which is why `M-011` is speculative |
| Role migration without breaking references | The `omn-architect` to `architect` precedent: deprecate while retaining the row so documents still naming it resolve | reuse-as-is | `F-021`, `C-011`. The selected approach does not need it, because the existing role stays active. It is recorded because it is the transition strategy `O-004` would require, and because it establishes that the framework has a sanctioned way to retire a role later without breaking references |
| Run evidence and handoff | The canonical result envelope, per-phase ledger, and run layout | reuse-as-is | `F-011`, `F-014`. The reviewer's runs are recorded by the same machinery as any routed phase, so no evidence surface is added |

New structure is proposed at exactly two places: the reviewer's own module set and host
registration, licensed by the change itself adding a role (`C-017`), and the review outcome
template, licensed by the `rejected` row above.

## Operational Considerations

Logging and observability: no new observability surface is required. A routed phase already
emits canonical progress events, a per-phase ledger, and a result envelope (`M-016`,
`F-011`), and the review outcome is itself the durable evidence read at the Review and
Verification Gates (`M-006`, `M-008`). The measurement `S-017` asks for — coverage as a
proportion — is derivable from the run evidence that already exists, so `C-013` needs no
new instrumentation.

Error handling: the runtime implements no retry and no recovery pass, and an artifact that
fails validation blocks with `awaiting_recovery_task` (`F-014`). This places a specific
obligation on `M-001`: the reviewer's module set must declare self-verification checks that
reject a non-conforming outcome before emission, because nothing downstream will repair one.
`C-015` compounds this — until `M-011` exists, a non-conforming outcome would not even be
detected. The design therefore orders the validator before the phase row (`P-012` before
`P-013`) rather than treating validation as a later hardening step.

Security considerations: the review outcome is a distribution surface, because `S-012`
requires it to be consumable by the delivery and quality roles, and its inputs are reviewed
material that may contain restricted content. `C-010` states the prohibition, and `M-009`
answers it structurally: the outcome carries each finding by reference to the identifier of
the reviewed element and its severity, and the template provides no position for verbatim
reviewed content. `R-006` carries the residual risk. Separately, the reviewer holds no gate
approval authority and no write authority over the records it reviews (`C-005`, `C-014`),
so a mistaken or manipulated outcome cannot itself alter the framework's contract surface —
it can only fail to raise a finding, which is a detection gap rather than a privilege
escalation. Compliance impact is confined to gate governance: `C-003` and `C-019` require
the ownership disposition and the producer relationship to be recorded as decisions, which
`D-001` and `D-004` do.

Performance considerations: no performance constraint is recorded for this change. `C-013`
is the only quality-attribute constraint, it is negotiable, and `S-017` explicitly declines
a numeric level, so the design sets no throughput or latency target and asserts no
performance expectation. The one performance-shaped observation is structural rather than
quantitative: `quality-review` is phase-mandatory for S08 (`F-008`) while performance is not
among the five dimensions (`A-002`), so the phase would require coverage that no declared
dimension provides. That is recorded as `Q-003` and `R-010`.

Deployment and operability impact: every step is a change to declarative framework records,
so there is no deployment unit. The only step with runtime effect is `P-013`, which can move
an in-flight run's `quality-review` work item from `blocked` to `pending` because guards are
re-evaluated from persisted state on demand (`F-011`). `M-016` is unchanged, so the
resolution chain, the adapter, and the phase-graph derivation behave exactly as they do
today for the two phases already executing.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The ownership disposition is recorded: exactly one Primary owner for `code-review` and `governance-enforcement`, and the retained position of the existing role | M-004, M-012 | none | Every downstream record expresses the disposition; recording them first creates two Primaries against `C-004` with no authority to resolve which is right | T-001 |
| P-002 | The reviewed-artifact definitions are approved, so each reviewed phrase maps to a named framework artifact | M-001 | none | `C-008` and AO-5 require declared input types that resolve; declaring them over an unapproved definition binds the contract to a guess | T-008 |
| P-003 | The review dimension set is fixed as a bounded list with recorded exclusions | M-009 | none | `C-007` fixes one result position per dimension, so the count must be closed before the contract is written | T-013 |
| P-004 | The reviewer's authority scope is defined, with each prohibition naming the holder of the withheld authority | M-001 | P-001, P-002 | `C-014` and `C-005` are satisfied in the authority text or nowhere; the module set expresses it, so defining it later forces the module set to be rewritten | T-002 |
| P-005 | The review outcome contract is defined: one result position per dimension, each finding carrying a severity and the identifier of the reviewed element, and no position for verbatim reviewed content | M-009 | P-003, P-004 | `C-007` and `C-010`. Defining the contract after the template makes the contract descriptive of the template rather than binding on it | T-010 |
| P-006 | The gate matrix records that the reviewer produces the evidence assessed at the Review and Verification Gates and approves neither, with owner entries unchanged | M-008 | P-004 | `C-005` is a reversibility safeguard for the whole change: it must hold before the reviewer can be dispatched into a gated phase, not after | T-012 |
| P-007 | The review outcome template exists and holds an active record in the template registry | M-009, M-010 | P-005 | `C-002`; and `F-003` enforces dependency resolution, so any later record declaring a data dependency on this template requires it to exist first | T-011 |
| P-008 | The reviewer's runtime module set exists with a resolvable load order, declaring only skills that resolve as active records | M-001 | P-004, P-005 | `C-009` and `C-012`; the record's specification path must denote an existing manifest, and an unresolvable skill blocks the phase | T-003 |
| P-009 | The host registration for the reviewer exists | M-002 | P-008 | `G1-CAPABILITY` requires it (`F-004`, `F-011`); without it the agent resolves in the registry but cannot be dispatched | T-004 |
| P-010 | The reviewer's agent registry record exists, satisfies the record schema, and resolves every declared dependency | M-003 | P-007, P-008 | `F-003` validates with all fields required, unknown fields rejected, and dependency resolution enforced, so the record is only valid once its referents exist | T-004 |
| P-011 | Capability ownership and skill coverage are recorded in the two matrices, consistent with the disposition | M-004, M-005, M-012 | P-001, P-008 | `C-006` requires the capability identifier to exist in the matrix before a manifest or record references it, and phase routing reads ownership | T-005 |
| P-012 | A registered validator exists for the review outcome artifact | M-011 | P-007 | `C-015`; `G1-CAPABILITY` requires a registered validator, and with no recovery pass (`F-014`) an unvalidated artifact type has no safety net | T-006 |
| P-013 | The `quality-review` phase row names the reviewer and the review outcome, and the workflow record declares the new dependencies | M-006, M-007 | P-006, P-009, P-010, P-011, P-012 | This is the step that makes the reviewer dispatchable and can move an in-flight run's work item from `blocked` to `pending` (`F-011`); every `G1-CAPABILITY` precondition and the producer-exclusion safeguard must already hold, or the guard unblocks into a partly built chain | T-012, T-009 |
| P-014 | Resolution is verified end to end: registry lookup, capability routing, skill resolution, host registration, validator, and phase ownership, with no unresolved or deprecated reference | M-003, M-004, M-005, M-006, M-011 | P-013 | `C-016`; the boundary must be verified before anything is written that assumes it holds | T-006, T-014 |
| P-015 | The existing review-owning contract's authority text is narrowed to match the recorded disposition | M-012 | P-001, P-011 | `C-019` and `C-011`: the matrices and the contract must state the same accountability, and every reference to the role must keep resolving | none |
| P-016 | Framework documentation surfaces carry the reviewer, with its inputs, deliverable, prohibitions, handoff targets, and escalation path | M-013 | P-014 | `C-016`; documentation written before resolution is verified documents an intention rather than a behaviour | T-007 |

These are structural constraints, not tasks. `Binds` names the planner tasks each constrains,
drawn from the supplied execution plan; no task identifier is created here, and the task
breakdown itself belongs to `planner`. `P-015` binds no task because the supplied plan holds
amendment of the existing review-owning contract as deferred work that enters scope once the
disposition requires it; `D-001` is that disposition, so the plan's deferred item is now
reachable and needs an owner.

### Test Strategy Focus Areas

For `omn-qa`:

- Registry resolution: the reviewer's record satisfies the record schema with every required
  field populated and no unknown field, its specification path denotes an existing manifest,
  and every declared dependency resolves (`F-003`, `P-010`).
- Capability routing: `quality-review` resolves to exactly one owner agent, and `code-review`
  and `governance-enforcement` each resolve to exactly one Primary owner (`C-004`, `F-009`).
- Skill resolution: every skill the reviewer declares and every skill the phase requires,
  including S08, resolves as an active record (`C-012`, `F-019`).
- Outcome conformance: an emitted review outcome carries exactly one explicit result position
  per declared dimension, for all five, and each finding carries a severity and the identifier
  of the reviewed element (`C-007`).
- Authority refusal: an attempt to have the reviewer approve a gate, take an architecture
  decision, or produce implementation is refused, and the refusal is recorded rather than
  silently dropped (`C-005`, `C-014`).
- Restricted content: reviewed material containing restricted content yields an outcome that
  does not reproduce it (`C-010`).
- Producer exclusion: no gate lists the reviewer as an approving owner for evidence the
  reviewer produced (`C-005`, `M-008`).
- In-flight run behaviour: a run whose `quality-review` work item is blocked at
  `G1-CAPABILITY` before the change re-evaluates to `pending` after `P-013`, and no committed
  artifact is mutated (`F-011`, `F-014`).

### Rollout and Rollback

Rollout follows `P-001` through `P-016`. The ordering places every enabling record before
`P-013`, which is the only step that changes observable runtime behaviour, and places
verification (`P-014`) before documentation (`P-016`).

Rollback reverses `P-013` first: restore the `quality-review` Owner Agent and Output Artifact
cells and remove the two workflow-record dependency entries. The phase then blocks at
`G1-CAPABILITY` again, which is its current state (`F-010`), so the framework returns to
today's behaviour. Next restore the `M-004` ownership cell and the `M-012` authority text.
The new files and additive records — the module set, the host registration, the template, and
the two registry records — are inert once no phase routes to them; removing them is optional
and has no dependent reference, provided the workflow record entries are reverted first,
because dependency resolution is enforced (`F-016`).

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | Ownership records are edited before the disposition is recorded | Two Primary owners exist for `code-review` and `governance-enforcement`, so capability routing is ambiguous and `C-004` fails | medium | M-004, D-001 | `P-001` precedes `P-011` and `P-015` | omn-tech-lead |
| R-002 | structural | Ownership is recorded only at column level, as the matrix records it today (`F-007`) | "Exactly one Primary per capability identifier" is asserted but cannot be evidenced from the record, so the acceptance criterion depending on it has no evidence | medium | M-004, D-001 | `Q-002` routes the expression question to the matrix owners; `P-011` records ownership in the approved form and `P-014` verifies the form actually recorded | omn-tech-lead |
| R-003 | contract | A consumer binds to the current `quality-review` Output Artifact wording | The derived phase-graph edge into the following phase changes, or a downstream input contract stops being satisfiable | low | M-006, D-002 | The `M-006` transition keeps the phase identifier unchanged and relies on the documented row-adjacency fallback (`F-013`); `P-014` verifies resolution before `P-016` | omn-tech-lead |
| R-004 | contract | The review outcome template is referenced by the workflow record or the reviewer's manifest before it is registered | Enforced dependency resolution rejects the record, blocking registration | medium | M-007, M-010 | `P-007` precedes `P-010` and `P-013` | omn-dev-1-implement |
| R-005 | migration | The phase row changes while a run holds that work item blocked at `G1-CAPABILITY` | The guard re-evaluates and the item moves to `pending`, so an in-flight run resumes into a phase whose supporting records are only partly in place | medium | M-006, P-013 | `P-013` depends on every `G1-CAPABILITY` precondition, so the guard can only re-evaluate to `pending` once the chain is complete | omn-tech-lead |
| R-006 | security | An emitted review outcome reproduces restricted content found in reviewed material | Secrets or restricted change content are distributed through an artifact that `S-012` requires be consumable by other roles | medium | M-009, D-003 | `C-010` is stated in the outcome contract at `P-005`, and `M-009` provides no position for verbatim reviewed content; the QA focus area covers it at `P-014` | omn-tech-lead |
| R-007 | structural | The reviewer's declared authority is written to include architecture decisions or gate approval | Two agents decide the same structural question, or a gate is approved by the producer of its evidence | medium | M-001, D-004 | `P-004` names the holder of each withheld authority, and `P-006` records the producer exclusion before `P-013` makes the reviewer dispatchable | omn-tech-lead |
| R-008 | operability | `A-005` is false: the Validation Engine cannot register a third artifact type without a gateway or adapter change | `G1-CAPABILITY` never passes for `quality-review`, so the reviewer is registered but not dispatchable and the routability outcome defers | medium | M-011, P-012 | `P-012` precedes `P-013`, so the gap surfaces before the phase row changes; `Q-004` routes the confirmation | omn-tech-lead |
| R-009 | delivery | The reviewer's registry record is created before its self-verification checks exist | A dispatchable agent can be routed while unable to pass its own checks, and there is no retry or recovery pass to catch it (`F-014`) | medium | M-003, P-010 | `P-008` requires the module set including its declared checks before `P-010` creates the record; `P-014` verifies before `P-016` documents | omn-tech-lead |
| R-010 | contract | The phase remains mandatory for S08 while performance is not among the five dimensions | The phase's mandatory skill set and the reviewer's declared coverage disagree; resolution still passes, so the mismatch is invisible to routing | medium | M-005, M-006 | `Q-003` resolves whether S08 remains phase-mandatory or the dimension set expands; `P-011` records the outcome before `P-013` | omn-product-owner |
| R-011 | contract | `A-001` is false: the reviewed artifacts denote something other than the registered plan artifact and the implementation change set | The declared input types and the outcome contract change after the authority scope is set | low | M-001, P-002 | `P-002` precedes `P-004` and `P-005` | omn-business-analyst |
| R-012 | contract | `A-002` is false: a dimension beyond the five is required | The outcome contract, its template, and the validation coverage all expand after they are authored | medium | M-009, D-003 | `P-003` fixes the dimension set with recorded exclusions before `P-005` | omn-product-owner |
| R-013 | operability | `A-003` is false: the reviewer is required in workflows beyond `implement-feature` | Those workflows carry no canonical phase identifiers (`F-010`), so routing cannot be built for them and the surface expands into an unroutable area | medium | M-006, M-007 | `Q-005` approves the surface with explicit non-goals before `P-013` | omn-product-owner |
| R-014 | structural | `A-004` is false: the existing review role is retired rather than unmigrated | The narrowing disposition is unavailable, only `O-004` remains, and `M-017` and `M-018` become contract changes across two further workflows | low | M-012, D-001 | `Q-001` confirms the role's status before `P-001` records the disposition | omn-tech-lead |
| R-015 | operability | `A-008` is false: the documentation surfaces do not enumerate agents, or enumerate them elsewhere | Documentation of the new role lands in the wrong surface or is omitted, so `S-015` discoverability is only partly satisfied | low | M-013, P-016 | `P-016` follows `P-014`, so documentation is written against verified resolution; `Q-006` confirms the surfaces | omn-documentation |
| R-016 | contract | `A-006` is false: the framework-governance dimension requires an external policy source | The reviewer gains an additional declared input type and an unresolved external dependency, and the `none-found` reuse outcome for governance coverage changes | low | M-001, M-009 | `Q-007` confirms the basis before `P-005` fixes the outcome contract | omn-business-analyst |
| R-017 | delivery | Registry and matrix records are created before the outcome contract is stable | Records must be re-edited after run evidence referencing them is already committed and immutable (`F-014`) | low | M-003, M-010 | `P-005` and `P-007` precede `P-010` | omn-tech-lead |

## Estimate and Confidence

- Overall: `L` (confidence: low). `L` because the change crosses the agent, skill, workflow,
  template, and validation boundaries in one movement and carries a coexistence obligation on
  `M-004` and `M-012`. Not `XL`, because the impact surface is bounded and every impacted
  record is named. Confidence is `low` rather than medium because the overall estimate depends
  on `M-011`, whose impact is speculative under `A-005`.

- Breakdown:
  - `P-001`, `P-002`, `P-003`: `XS` each (confidence: high). Recorded decisions with no
    structural change.
  - `P-004`: `S` (confidence: medium). Authority scope within one new boundary; depends on
    `A-001`.
  - `P-005`: `M` (confidence: medium). A new contract with five fixed result positions and a
    content prohibition; depends on `A-002`.
  - `P-006`: `XS` (confidence: high). Additive prose in an existing rule section with no owner
    entry change.
  - `P-007`: `S` (confidence: medium). One new template and one additive registry record.
  - `P-008`: `L` (confidence: low). The full module set expressing authority, inputs,
    lifecycle, output binding, and self-verification checks; low because it depends on `A-001`
    and `A-002`.
  - `P-009`: `XS` (confidence: high). One host registration entry point.
  - `P-010`: `S` (confidence: medium). One registry record under strict schema validation with
    enforced dependency resolution.
  - `P-011`: `M` (confidence: low). Two governance matrices, one of which cannot express
    identifier-level ownership in its current form (`F-007`, `R-002`).
  - `P-012`: `M` (confidence: low). A third registered validator; low because `A-005` is
    unconfirmed and `M-011` is speculative.
  - `P-013`: `M` (confidence: medium). Two records, but the widest blast radius, including
    in-flight runs.
  - `P-014`: `M` (confidence: low). End-to-end resolution verification across five records;
    low because it depends on `P-012`.
  - `P-015`: `S` (confidence: medium). Narrowing existing contract text.
  - `P-016`: `S` (confidence: low). Depends on `A-008`.

- Scope assumptions: the estimate covers `P-001` through `P-016` for the `implement-feature`
  surface only (`A-003`). It excludes exercising the reviewer on real work (`S-018`),
  dimensions beyond the five (`A-002`), participation in any other workflow, capability
  registration for the three phases that remain blocked, and any change to the dispatch or
  adapter mechanism (`M-016`). It assumes `A-001` and `A-004` hold.

- Uncertainty drivers: `A-005`, which makes `M-011` speculative and holds `P-012` and `P-014`
  at low confidence; `F-007`, because the capability matrix cannot express identifier-level
  ownership, so `P-011`'s form is not yet determined; `A-008`, which makes `M-013`
  speculative; and the interaction between the phase row change and in-flight runs (`R-005`),
  which is understood but not yet exercised.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Is `omn-dev-2-reviewer` unmigrated rather than retired (`A-004`)? | No | omn-tech-lead | M-012, D-001, R-014 | If unmigrated, the narrowing disposition in `D-001` stands. If retired, only `O-004` remains viable and the change expands into `fix-bug` and `review-pull-request`, turning `M-017` and `M-018` into contract changes |
| Q-002 | Does `agents/capability-matrix.md` record capability ownership at identifier level, or only at the coarse column level it uses today (`F-007`)? | No | omn-tech-lead | M-004, D-001, R-002 | If only at column level, `C-004`'s single-Primary property cannot be evidenced from the record, and either the matrix's expression form changes or the criterion is evidenced elsewhere. Recorded as a genuine framework gap rather than resolved here |
| Q-003 | Does S08 remain phase-mandatory for `quality-review` once the reviewer owns it, given performance is not among the five dimensions? | No | omn-product-owner | M-005, M-006, R-010 | If it remains, the reviewer is routed to a phase requiring coverage no declared dimension provides. If it is removed, the phase's mandatory skill set changes, which is itself a workflow contract change |
| Q-004 | Can the Validation Engine register a validator for a third artifact type without a change to the invocation gateway or the adapter (`A-005`)? | No | omn-tech-lead | M-011, P-012, R-008 | If not, `G1-CAPABILITY` never passes and the reviewer is registered but not dispatchable, deferring the routability outcome to a later change |
| Q-005 | Which registered workflows beyond `implement-feature` require reviewer participation (`A-003`)? | No | omn-product-owner | M-006, M-007, R-013 | Any additional workflow lacks canonical phase identifiers today, so its Phase Model must be canonicalized before routing can be built for it |
| Q-006 | Which framework documentation surfaces enumerate agents and must carry the reviewer (`A-008`)? | No | omn-documentation | M-013, P-016, R-015 | Determines whether `M-013` is a real impact or `no-change-verified` |
| Q-007 | Is the framework-governance dimension assessed against the framework's own registries and matrices, or against an external policy source (`A-006`)? | No | omn-business-analyst | M-001, M-009, R-016 | An external source adds a declared input type and an unresolved dependency, and changes the `none-found` reuse outcome for governance skill coverage |
| Q-008 | Who accepts the Review Gate for the reviewer's own module set, template, and registry record, given `omn-dev-2-reviewer` is the sole listed owner and the reviewer does not yet exist (`F-018`)? | No | omn-tech-lead | M-008, P-006 | The supplied plan routes the authoring tasks to the Review Gate; the reviewer cannot review its own creation, so the accepting owner for those items must be named before those items reach the gate |
| Q-009 | Do the Design Gate owners accept `D-001` through `D-004`, and does the product owner confirm `D-001`'s ownership disposition, which changes an existing role's accountability (`S-016`, `C-019`)? | No | omn-tech-lead | D-001, D-002, D-003, D-004, P-001 | The Design Gate owners are `omn-tech-lead` and the architecture role; `architect` produced these records, so under the Producer Exclusion Rule `omn-tech-lead` is the accepting owner, and `omn-product-owner` confirmation is additionally required for `D-001`. Until accepted, `P-001` cannot record the disposition and no downstream record may be edited. The design is complete; execution is gated on acceptance |

All four decision records remain at status `Proposed`. Acceptance belongs to the Design Gate
owners and is never taken by this agent.

## Sign-off

- Architect: `architect` — producing role; excluded from accepting this package under the
  Producer Exclusion Rule in `workflows/workflow-gate-matrix.md`. The Design Gate owner entry
  naming `omn-architect` names the architecture role now implemented by `architect`.
- Tech Lead: `omn-tech-lead` — accepting owner for the Design Gate, and for `D-002`, `D-003`,
  and `D-004`.
- QA: `omn-qa` — review of the test strategy focus areas and the validation coverage they
  imply.
- Product confirmation: `omn-product-owner` — required for `D-001`, because it changes an
  existing role's accountability (`S-016`, `C-019`), and for `Q-003` and `Q-005`.

Lines are left unsigned by the producing agent. No implementation work was performed: this
package contains analysis and design only, no production code, tests, migrations, scripts, or
configuration, and no external system, repository, or ticketing tool was accessed.
