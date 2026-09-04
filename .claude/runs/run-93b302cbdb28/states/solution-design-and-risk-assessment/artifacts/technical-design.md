```yaml
design:
  designId: wave-1-delivery-core-agent-rollout-technical-design
  changeReference: runs/inputs/wave-1-rollout-change-request.md
  sourceInputs:
    - type: change-request
      reference: runs/inputs/wave-1-rollout-change-request.md
    - type: business-intent
      reference: runs/inputs/wave-1-rollout-business-intent.md
    - type: architecture-context
      reference: runs/inputs/wave-1-rollout-architecture-context.md
    - type: execution-plan
      reference: runs/run-93b302cbdb28/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002]
  consumesPlan: runs/run-93b302cbdb28/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:6cb9485fea49474aae41df46bb43f9a2
  contextDigest: sha256:079539584551833ae3bf361840ce2616
```

## Metadata

- Feature or Change ID: `run-93b302cbdb28` — Wave 1 Delivery Core Agent Rollout
- Author: architect
- Reviewers: omn-tech-lead (Design Gate accepting owner), omn-qa (verification focus areas)
- Last Updated: 2026-08-19

Statement register: `S-001` to `S-019`, extracted from the change request and the business
intent in supply order and, within each input, in document order. The supplied execution plan
is consumed as a design consumer: its task identifiers `T-001` to `T-015` are referenced where
a sequencing constraint binds one, and none is created here.

No implementation work was performed. No external system, repository, or ticketing tool was
accessed; all context was read from the supplied inputs and the frozen context slice this run
declares.

## Objective

- Desired outcome: a phase owned by a Wave 1 delivery core agent reaches a resolvable output
  contract and a resolvable context slice by declaration alone, so that the guard chain the
  runtime already enforces (`F-001`, `F-004`) clears for that phase without any change to the
  guards themselves.

- Architectural objectives:

  - `AO-1` Every phase a Wave 1 agent owns resolves an output contract by string identity across
    the three declaration points the runtime reads: the Phase Model Output Artifact cell, the
    owning manifest's declared output, and the validator map key. Traces to `S-009`, `S-015`.
  - `AO-2` Every phase brought into an increment resolves a context slice at the context guard
    rather than blocking there. Traces to `S-009`, `S-014`.
  - `AO-3` The two dispositions are expressed once, covering all twelve phases the four Wave 1
    agents own, so that a later increment applies them without a new architecture decision.
    Traces to `S-002`, `S-003`, `S-009`.
  - `AO-4` Applying either disposition to a phase leaves the guard verdicts of the three
    currently dispatchable phases (`F-020`) unchanged. Traces to `S-004`, `S-019`.
  - `AO-5` A phase whose disposition cannot be applied inside an increment carries a recorded
    blocking reason at a named guard, so increment status is derivable from a run record rather
    than asserted. Traces to `S-008`, `S-011`, `S-018`.

- In scope: the artifact-type disposition of the eleven prose Output Artifact cells and of the
  one cell that already names a file (`F-011`); the composition and keying of a per-phase
  context-slice declaration; the declaration set a delivery core agent must carry for a phase it
  owns to become dispatchable; the order those declarations must be established in; the
  structural risks each carries.

- Out of scope, structurally:

  - Authoring any module set, registry record, template, validator, or Phase Model column edit.
    Those are the consuming work; this package defines what they must satisfy.
  - Changing which agent owns which phase (`C-015`). A phase whose disposition would require
    re-ownership is reported at its blocking reason, per `D-004`.
  - Changing gate ownership or the Producer Exclusion Rule (`C-009`, `S-017`).
  - The structure of the context-slice contract itself. `A-002` assumes it suffices; `Q-002`
    routes the confirmation and `R-003` records the consequence if it does not.
  - Wave 2 to Wave 4 agents, and making all thirty-six phases dispatchable (`S-017`).
  - Registering skills `S04` and `S05`, which no routed phase declares as mandatory (`S-017`).

  This list is non-empty because the change touches shared boundaries: five workflow
  specifications, the runtime validator map, and the agent registry are each read by phases
  outside this increment (`F-009`, `F-011`, `F-022`).

## Requirements Summary

Functional requirements:

- Every phase the four Wave 1 agents own carries a named artifact-type disposition, including
  the one phase that already names a file artifact (`S-009`, `S-002`).
- A phase owned by a Wave 1 agent obtains the context-slice declaration it needs to clear
  context resolution, and the declaration's required content is stated (`S-009`, `S-014`).
- The disposition set is applicable one primary capability surface at a time (`S-005`).
- A phase that cannot be made dispatchable inside an increment is reported at its blocking
  reason rather than removed from scope (`S-008`, `S-018`).
- No registry record is activated ahead of the runtime module set it points at (`S-006`).
- The declaration set a delivery core agent must carry is expressed so that a second agent can
  be registered against it without a new architecture decision (`S-002`, `S-013`).

Non-functional requirements:

- The two dispatchable `implement-feature` phases and the one dispatchable `refactor` phase
  (`F-020`) keep dispatching (`S-004` invariants `INV-1` and `INV-2`; `S-019`).
- The two completed runs held as replay references (`F-020`) stay readable with unchanged
  fingerprints (`S-004` invariant `INV-3`; `S-019`).
- No verifier check moves from pass to fail (`S-004` invariant `INV-4`; `S-016`).
- No phase-mandatory skill reference becomes unresolved (`S-004` invariant `INV-5`; `F-020`).
- Gate ownership and the Producer Exclusion Rule are unchanged (`S-004` invariant `INV-6`;
  `S-017`; `F-016`).
- A completion claim rests on a run record carrying the evidence, never on the declarations
  alone (`S-007`, `S-011`).

Acceptance criteria: cited, not restated. The business intent's `BI-1` to `BI-5` (`S-012` to
`S-016`) and its five-part acceptance boundary (`S-018`) govern increment acceptance. The
supplied execution plan's acceptance criteria for `T-001` and `T-002` govern acceptance of the
two dispositions this package records, and its `T-006` criteria govern the declaration set
recorded inline as `D-003`.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The runtime gates every state work item on five guards, and the capability guard resolves the whole capability chain | Architecture context, section 1 |
| F-002 | The capability chain has five links: an active record in the agent registry; a manifest declaring the workflow and phase in its supported workflows; a host registration; phase-mandatory skills resolvable through the skill registry; a registered validator for the phase's output artifact | Architecture context, section 1 |
| F-003 | No Wave 1 agent holds an active record in the agent registry and none has a manifest; host registration is present for all twelve phase owners | Architecture context, section 1; agent registry, which holds only `planner` and `architect` |
| F-004 | The context guard is separate from the capability guard. The context-slice phase declaration names exactly three phases — `execution-planning`, `solution-design-and-risk-assessment`, and `scope-invariants-and-risk-profile` — and any other phase blocks at the context guard even after the capability guard clears | Architecture context, section 1; runtime notes, known gap 6 |
| F-005 | Two runtime module sets exist, for `planner` and `architect`. Each holds a manifest plus seven modules in a declared load order: charter, contract, reasoning, execution, output, quality, examples | Architecture context, section 2; `agents/architect/manifest.yaml` |
| F-006 | Output-contract resolution requires the quality module to exist by path independently of the manifest, and requires each declared output's template reference and contract reference to resolve | Architecture context, section 2 |
| F-007 | A manifest also carries authority scope, inputs, outputs, supported workflows, skills, collaboration, determinism, and versioning | Architecture context, section 2 |
| F-008 | Each of the four Wave 1 agents already has a single-file prose contract of around fifty lines, and the planner manifest records the precedent for superseding it: a versioning entry naming the superseded file with a reason | Architecture context, section 2 |
| F-009 | The Phase Model Output Artifact cell is read literally, stripping only backticks, and that exact string must be present in the owning manifest's declared outputs and must be a key of the runtime validator map | Architecture context, section 3 |
| F-010 | Seven validators are registered. Two are hand-written against the Planner and Architect numbered check sets, four are declared as data and executed by the artifact contract engine, and one is a governance artifact no phase emits | Architecture context, section 3; runtime notes |
| F-011 | The four Wave 1 agents own twelve phases. Eleven carry prose Output Artifact cells; exactly one, `review-pull-request/code-quality-review`, names a file artifact | Architecture context, section 3 |
| F-012 | The precedent for changing an Output Artifact column is recorded: `review-pull-request/code-quality-review` moved from prose to a named artifact under a change proposal, with its reasoning and four rejected alternatives held in a prior run. Extending the declaration to the other review-producing phases is structurally available and is a product decision about scope, not a structural finding | Architecture context, section 3; runtime notes, known gap 7 |
| F-013 | A validator removes one of the five capability-chain conditions and is not sufficient for dispatch: four artifact types gained a validator without their phases becoming dispatchable | Architecture context, section 3; runtime notes, known gap 9 |
| F-014 | A new artifact type has two available shapes: a contract declared as data and executed by the artifact contract engine, or a hand-written validator where the owning agent ships a numbered check set in its quality module that the validator must reproduce exactly | Architecture context, section 4 |
| F-015 | Three templates were raised to version 1.1.0 to become decidable, each gaining a leading metadata block and the tables that turn its agent's decision rules into something checkable, and one template was added new. That is the precedent for what a new template must carry | Architecture context, section 4 |
| F-016 | Gate ownership is read from the workflow gate matrix and never invented by the runtime; twenty-eight gate references across the active Phase Models are all decidable, with the Producer Exclusion Rule enforced including through the legacy role alias | Architecture context, section 5; workflow gate matrix |
| F-017 | `omn-product-owner` is a listed owner of the Scope Gate it produces evidence for, so under the Producer Exclusion Rule that decision rests with `omn-business-analyst` | Architecture context, section 5 |
| F-018 | Self-hosting constraints bind this increment: every path under the framework directory is in routing scope, with a closed exemption set covering runs, reports, proposals, and caches; every phase of the routed workflow must be enqueued and either executed with a validated artifact or blocked with a recorded reason; a phase artifact and its validation report are required where the routed workflow has a dispatchable phase; every mandatory release-checklist item must be recorded with its result | Architecture context, section 6 |
| F-019 | Recorded structural risks unchanged by this increment: gate decisions are recorded rather than solicited; retry is scheduled rather than driven; there is no lease expiry timer; the workflow engine document has no planning state and disagrees with the `implement-feature` specification, and names a different owner than the Phase Model for three states | Architecture context, section 7; runtime notes, known gaps 2 to 6 |
| F-020 | Current state: two of twelve phase owners hold active registry records; twelve of twelve host entrypoints resolve; two runtime module sets exist; three of thirty-six phases are dispatchable — two in `implement-feature` and one in `refactor` — and thirty-three block with the reason `awaiting_capability_registration`; seven validators are registered against six artifact types named as files by active Phase Models; one hundred and one of one hundred and one phase-mandatory skill references resolve; six runs exist, of which two are Completed and four are WaitingForHuman, and six of seven active workflows have zero completed runs | Change request, current state, frozen in the maturity snapshot |
| F-021 | A phase whose owner has no registered capability is not skipped: it is enqueued, blocked with a recorded reason, and reported as an open escalation | `workflows/implement-feature.md` resolution rules; runtime notes, known gap 1 |
| F-022 | The phase dependency graph is derived from the workflow specification: an earlier phase whose Output Artifact is named in a later phase's Input column creates a hard edge; failing that the immediately preceding row creates one; and an edge is downgraded to soft when the Input column declares an explicit alternative the supplied inputs already satisfy. Changing those columns changes the sequencing the runtime enforces | Runtime notes; `workflows/implement-feature.md` resolution rules |
| F-023 | `execution-planning` holds a soft edge because its Input column declares an explicit alternative that supplied inputs satisfy, while `solution-design-and-risk-assessment` holds a hard edge because its Input column names the execution plan with no alternative | Runtime notes |
| F-024 | `review-pull-request/structural-compliance` is owned by an agent that is registered and host-invocable, yet blocks with the reason `awaiting_contract_reconciliation`, because the assessment that phase asks for is not among its owner's declared outputs and naming an artifact there was rejected on role-boundary grounds | Runtime notes, known gaps 1 and 7 |
| F-025 | The template registry is the discovery index for artifact templates and holds seven active records, each with an identifier matching a lower-case hyphenated pattern and a specification path. The record for the existing review artifact type declares that one artifact type serves the quality-review phase of `implement-feature`, both `review-pull-request` assessments, and the artifact-packaging phase of `release`, with a category column carrying the review lens | Template registry |
| F-026 | The capability matrix is authoritative for capability identifiers, and an identifier is added there before an agent manifest, a registry record, or an execution plan may reference it | Capability matrix |
| F-027 | The `implement-feature` Design Gate is owned by `omn-architect` and `omn-tech-lead`, the gate matrix records that the `omn-architect` entries name the architecture role now implemented by `architect`, and the Producer Exclusion Rule reads through role aliases | Workflow gate matrix |
| F-028 | The context loader is implemented as frozen, content-addressed, and narrowed per phase; the frozen slice is persisted per phase as a context snapshot with per-file digests, and runs declare memory hydration as not requested | Runtime notes, implemented-components table and run layout |
| F-029 | A rejected artifact is classified and retried under a bounded budget while a missing capability blocks, and the distinction is drawn by the failure classification matrix before any action is chosen | Runtime notes, failure classification and retry |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | An output contract resolves once the same string appears in the Phase Model Output Artifact cell, in the owning manifest's declared outputs, and as a validator map key, together with the template and contract reference resolution `F-006` states, and nothing further is required | `D-001` states a resolution path, and `F-009` establishes the three declaration points without establishing that they are sufficient | `D-001`'s resolution path is incomplete; every phase applying it re-scopes and `P-003` and `P-004` gain a further step | omn-tech-lead |
| A-002 | A context-slice declaration for a phase is an entry keyed by the phase identifier, and adding one does not require changing the context-slice contract itself | `D-002` rests on the existing contract sufficing; `F-004` establishes which phases are declared, not how a declaration is added | An additional architecture decision precedes `P-009`, the context-slice contract enters scope, and the increment is delayed | omn-tech-lead |
| A-003 | No Input column of a currently dispatchable phase would fail to resolve its declared alternative after a prose Output Artifact string it names is replaced by an artifact identifier | `F-022` makes column edits sequencing-affecting and `F-023` shows a dispatchable phase whose Input column names a prose string produced by a Wave 1 phase | A column edit re-derives an edge into a dispatchable phase, changing its predecessor set and putting `INV-1` or `INV-2` at risk | omn-tech-lead |
| A-004 | The output each prose cell describes can be carried by an artifact type owned by the agent that already owns the phase, without changing phase ownership | `D-001` assigns role-shaped types on the assumption that the output belongs to the owning role | That phase's disposition becomes a role-boundary reconciliation rather than a column change, exactly as `F-024` records for one phase already, and the phase is reported blocked instead of applied | omn-product-owner |
| A-005 | A Wave 1 phase's context slice can be composed from the member kinds the three declared phases already use — registries, matrices, the routed workflow specification, templates, domain and context documents — without a new member kind | `D-002` states what a declaration must contain by reference to the existing composition | The composition rule in `D-002` is incomplete for that phase and a new member kind must be defined before `P-009` | omn-tech-lead |
| A-006 | The replay fingerprint that the multi-phase verifier proves unchanged is computed over the persisted run record, not re-derived from the current content of the context-slice member files | A workflow specification is a declared member of the frozen context slice of completed runs, and `D-001` edits five such specifications while `INV-3` requires those runs' fingerprints to stay unchanged | Any Phase Model column edit changes the re-derived context digest of a completed reference run, and `INV-3` fails for a reason unrelated to the disposition | omn-tech-lead |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | No registry activation without the runtime module set it points at | Hard | `S-006` |
| C-002 | structural | One primary capability surface per increment | Hard | `S-005` |
| C-003 | operability | No completion claim without a run under the run record location carrying the evidence | Hard | `S-007`, `F-018` |
| C-004 | structural | A phase that cannot be made dispatchable inside the increment blocks with a recorded reason and is reported, rather than the scope being quietly narrowed | Hard | `S-008`, `F-018`, `F-021` |
| C-005 | structural | The three currently dispatchable phases remain dispatchable | Hard | `S-004` (`INV-1`, `INV-2`), `S-019`, `F-020` |
| C-006 | migration | The two completed runs held as replay references remain readable with unchanged fingerprints | Hard | `S-004` (`INV-3`), `S-019`, `F-020` |
| C-007 | quality-attribute | All four verifiers keep their current verdict; no check moves from pass to fail | Hard | `S-004` (`INV-4`), `S-016` |
| C-008 | structural | No phase-mandatory skill reference becomes unresolved | Hard | `S-004` (`INV-5`), `F-020` |
| C-009 | compliance | Gate ownership and the Producer Exclusion Rule are unchanged | Hard | `S-004` (`INV-6`), `S-017`, `F-016` |
| C-010 | structural | An output contract resolves only when the artifact string is simultaneously the Phase Model Output Artifact cell, a declared output of the owning manifest, and a validator map key | Hard | `F-009`, `A-001` |
| C-011 | structural | A phase clears context resolution only if a context-slice declaration exists for its phase identifier, and the slice the loader produces is narrowed per phase | Hard | `F-004`, `F-028` |
| C-012 | quality-attribute | A new artifact type must carry a registered template at the shape the template precedent sets and a validator that decides in both directions; a validator that accepts everything is not a decision | Hard | `F-014`, `F-015`, `F-010` |
| C-013 | compliance | An increment is accepted only on the full five-part Agent Definition of Done; a partial rollout is reported with the blocker named | Hard | `S-018` |
| C-014 | operability | A capability identifier referenced by a manifest or a registry record must already exist in the capability matrix | Hard | `F-026` |
| C-015 | structural | Phase ownership is not changed by this increment; a phase whose disposition would require re-ownership is reported rather than re-owned | Hard | Supplied execution plan, Out of Scope; `F-024` |
| C-016 | functional | The disposition names an artifact-type outcome for every phase the four Wave 1 agents own, not only for the phase inside the current increment | Hard | `S-009`, `S-008` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `workflows/implement-feature.md` Phase Model table | contract-change | F-009, F-011, F-022 | Output Artifact cells of `scope-and-acceptance`, `implementation`, `quality-review`; Input column of `execution-planning` | confirmed |
| M-002 | `workflows/fix-bug.md` Phase Model table | contract-change | F-009, F-011, F-022 | Output Artifact cells of `fix-implementation`, `regression-validation`; Input columns naming those strings | confirmed |
| M-003 | `workflows/refactor.md` Phase Model table | contract-change | F-009, F-011, F-022 | Output Artifact cells of `safety-net-establishment`, `refactor-implementation`, `behavioral-validation`; Input columns naming those strings | confirmed |
| M-004 | `workflows/review-pull-request.md` Phase Model table | contract-change | F-009, F-011, F-024 | Output Artifact cell of `test-risk-validation`; the `code-quality-review` cell is already a named artifact and is unchanged | confirmed |
| M-005 | `workflows/release.md` Phase Model table | contract-change | F-009, F-011, F-022 | Output Artifact cells of `artifact-packaging`, `candidate-validation`; Input columns naming those strings | confirmed |
| M-006 | Runtime validator map in `runtime/framework_runtime.py` | contract-change | F-009, F-010, F-013 | The key set the output-contract resolution reads | confirmed |
| M-007 | Context-slice phase declaration in `runtime/framework_runtime.py` | extension | F-004, A-002 | The phase-identifier key set the context guard reads | speculative |
| M-008 | `runtime/artifact_contract.py` declarative contract set | extension | F-014, F-010 | The declared contract per newly registered artifact type | confirmed |
| M-009 | `registry/templates.yaml` | extension | F-025, F-015 | Template discovery records for newly registered artifact types | confirmed |
| M-010 | `templates/` artifact template files | extension | F-015 | The metadata block and decision tables a decidable template carries | confirmed |
| M-011 | `registry/agents.yaml` | extension | F-002, F-003, F-020 | Active agent records and their specification paths and capability arrays | confirmed |
| M-012 | `agents/<wave-1-id>/` runtime module sets | extension | F-005, F-006, F-007, F-008 | Manifest declarations: supported workflows and phase, declared outputs, authority scope, skills, versioning supersedes; the seven modules named in the declared load order, including the quality module required by path | confirmed |
| M-013 | `agents/<wave-1-id>.agent.md` host registrations | behavior-change | F-003, F-008 | The manifest and module set the registration loads; the registration status table | confirmed |
| M-014 | `skills/agent-skill-matrix.md` and `registry/skills.yaml` | no-change-verified | F-020 | none | confirmed |
| M-015 | `workflows/workflow-gate-matrix.md` | no-change-verified | F-016 | none | confirmed |
| M-016 | `agents/capability-matrix.md` | no-change-verified | F-026 | none; every capability a Wave 1 record would declare already exists there | confirmed |
| M-017 | `runtime/design_validator.py` and `runtime/plan_validator.py` | no-change-verified | F-010 | none; the two hand-written validators serve artifact types this increment does not alter | confirmed |
| M-018 | The four verifiers over registry coverage, validators, recovery, and self-hosting | operational-impact | F-020 | Reported counts of dispatchable phases, active records, routed artifact types, and blocked reasons | confirmed |
| M-019 | The completed runs held as replay references, and their persisted context snapshots | operational-impact | A-006, F-028 | The frozen context slice members that name a workflow specification, and the fingerprint a replay compares | speculative |
| M-020 | `reports/` board and evidence records | operational-impact | F-018 | Recorded counts and per-phase status; exempt from routing scope under the closed exemption set | confirmed |

`M-014` through `M-017` are recorded because a reader would reasonably expect a rollout that
touches registries and the runtime to touch them. It does not: neither disposition adds or
removes a skill reference (`C-008`), changes a gate owner (`C-009`), introduces a capability
identifier (`C-014`), or alters the two artifact types whose validators are hand-written against
numbered check sets (`F-010`). `M-018` is impacted because the counts those verifiers report
change even where no verdict does, which is the distinction `C-007` turns on.

Boundary crossings recorded in the impact set:

- The artifact string crosses three declaration surfaces that must agree simultaneously: the
  Phase Model cell (`M-001`, `M-002`, `M-003`, `M-004`, `M-005`), the owning manifest's declared
  outputs (`M-012`), and the validator map (`M-006`). This is where `C-010` concentrates.
- The phase identifier crosses from the Phase Model to the context-slice declaration (`M-007`).
- A workflow specification file crosses from an editable declaration into the frozen context
  slice of runs that already completed (`M-019`). This crossing is why `P-001` exists.
- A new artifact type crosses from the template file (`M-010`) to the template registry
  (`M-009`) to the validator engine (`M-008`) before it may be named in a cell.

### 5.2 Options Considered

The evaluation is recorded so the selection can be re-derived rather than trusted. Criterion 1,
hard-constraint satisfaction, is applied first and is absolute: an option that violates any hard
constraint is eliminated whatever else it scores. Criteria 2 to 6 then rank the options that
survive. Impact surface is the count of impacted modules the option gives `contract-change` or
`dependency-change`; reuse leverage is the count of applicable reuse-survey rows in section 7
the option satisfies by `reuse-as-is` or `reuse-extended`, over the applicable row set that
section names for each decision; migration burden is the count of contract-affecting artifacts
the option introduces that require a transition strategy. Score is
`reuse leverage − migration burden`, and ties break toward the smaller impact surface, then
toward the lower option identifier.

Two decisions are evaluated in one table. `O-001` to `O-005` are the option set of the
output-artifact decision, scored over that decision's nine applicable survey rows; `O-006` to
`O-008` are the option set of the context-slice decision, scored over its three. `Not affected`
in a constraint column is an evaluation, not an omission: it records that the option neither
satisfies nor violates that constraint because the constraint governs the other decision and the
option leaves it exactly as it found it.

| Option | Addresses | Structural change | C-002 | C-005 | C-010 | C-011 | C-012 | C-015 | C-016 | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability | Score | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | output-artifact decision | One new artifact type, template, registry record, and validator per prose-output phase | Satisfied | Satisfied | Satisfied | Not affected | Satisfied | Satisfied | Satisfied | 6 | 4 of 9 | Satisfies C-007 and C-013 | 11 | Eleven types, templates, and validators to keep decidable | −7 | Survives criterion 1; not selected |
| O-002 | output-artifact decision | Role-shaped artifact types: reuse the existing review artifact type where its registry record already declares the phase, and introduce one new type per remaining Wave 1 role | Satisfied | Satisfied | Satisfied | Not affected | Satisfied | Satisfied | Satisfied | 6 | 5 of 9 | Satisfies C-007 and C-013 | 3 | Three new types, each serving several phases through a lens column | 2 | Selected |
| O-003 | output-artifact decision | One universal phase-output artifact type for all eleven prose cells | Satisfied | Satisfied | Satisfied | Not affected | Violated | Satisfied | Satisfied | 6 | 4 of 9 | Fails C-012: one type spanning four roles' decision rules can only carry their union, which decides nothing | 1 | One type, but no decidable validator to operate | 3 | Eliminated on C-012 |
| O-004 | output-artifact decision | Decide the disposition only for the phase inside increment 1; the other ten cells stay prose and undecided | Satisfied | Satisfied | Satisfied | Not affected | Satisfied | Violated | Violated | 2 | 4 of 9 | Fails C-016 and narrows the requested decision without recording the narrowing | 1 | One type now, an unrecorded decision per later increment | 3 | Eliminated on C-016, C-015 |
| O-005 | output-artifact decision | Relax output-contract resolution so a prose cell resolves, leaving the columns unchanged | Satisfied | Violated | Violated | Not affected | Satisfied | Satisfied | Satisfied | 1 | 1 of 9 | Changes the resolution path all three dispatchable phases already traverse (`F-020`) | 1 | One runtime contract change with framework-wide reach | 0 | Eliminated on C-010, C-005 |
| O-006 | context-slice decision | Per-phase declaration keyed by the phase identifier, composed from existing member kinds and narrowed to the owning manifest's declared inputs | Satisfied | Satisfied | Not affected | Satisfied | Satisfied | Satisfied | Satisfied | 0 | 3 of 3 | Satisfies C-007; the guard contract is untouched | 0 | One declaration per phase brought into an increment | 3 | Selected for the context-slice decision |
| O-007 | context-slice decision | One blanket declaration covering all thirty-six phases at once | Violated | Satisfied | Not affected | Violated | Satisfied | Satisfied | Satisfied | 0 | 1 of 3 | An undifferentiated slice is not narrowed per phase, so a frozen snapshot stops evidencing what a phase read | 0 | Every phase carries context no declared input consumes | 1 | Eliminated on C-011, C-002 |
| O-008 | context-slice decision | Derive the slice implicitly from the owning manifest's declared inputs instead of declaring it per phase | Satisfied | Satisfied | Not affected | Satisfied | Satisfied | Satisfied | Satisfied | 1 | 1 of 3 | Changes the guard contract the three dispatchable phases (`F-020`) already resolve through, so C-005 and C-007 need re-verification | 1 | No per-phase step, one contract to re-verify | 0 | Survives criterion 1; not selected |

Constraints not columned above — `C-001`, `C-003`, `C-004`, `C-006`, `C-007`, `C-008`, `C-009`,
`C-013`, `C-014` — are satisfied by every option and therefore do not discriminate; they bind the
application of the selected options and appear in sections 6, 8, 9, and 10.

A score is recorded for every option, including the eliminated ones. Two eliminated options,
`O-003` and `O-004`, score 3, above the selected `O-002` at 2. Recording that is the point rather
than an embarrassment: it shows the selection was made by hard-constraint satisfaction first and
by score only among the options that survived, and it stops a later reader re-proposing a cheap
option without seeing why it was refused. Among survivors the ranking is `O-002` at 2 over
`O-001` at −7 for the output-artifact decision, and `O-006` at 3 over `O-008` at 0 for the
context-slice decision. Neither selection depends on a tiebreak.

### 5.3 Selected Approach

- Selected: `O-002`.

- Structural change:

  The approach is composite. `O-002` carries its primary structural change, the output-artifact
  disposition recorded as `D-001`. Its context-slice component is the selected option of the
  second decision evaluated in 5.2, `O-006`, recorded as `D-002`; both rows are marked selected
  in the evaluation table and both selections are re-derivable from it.

  Part one, the output-artifact disposition (`D-001`). Every phase a Wave 1 agent owns declares
  a named artifact type in its Output Artifact cell, shaped by the role that owns the phase
  rather than by the individual phase. A type serving several phases carries a lens column,
  exactly as the existing review artifact type carries a category column for the review lens
  (`F-015`, `F-025`). The disposition, covering all twelve phases (`C-016`):

| # | Workflow / phase | Owner | Current cell | Disposition | Artifact type |
|---|---|---|---|---|---|
| 1 | `implement-feature/scope-and-acceptance` | omn-product-owner | prose | new type | `scoped-requirement-summary.md` |
| 2 | `implement-feature/implementation` | omn-dev-1-implement | prose | new type | `implementation-evidence.md` |
| 3 | `fix-bug/fix-implementation` | omn-dev-1-implement | prose | new type | `implementation-evidence.md` |
| 4 | `refactor/refactor-implementation` | omn-dev-1-implement | prose | new type | `implementation-evidence.md` |
| 5 | `review-pull-request/code-quality-review` | omn-dev-2-reviewer | `review-package.md` | unchanged | `review-package.md` |
| 6 | `implement-feature/quality-review` | omn-dev-2-reviewer | prose | reuse existing type | `review-package.md` |
| 7 | `release/artifact-packaging` | omn-dev-2-reviewer | prose | reuse existing type | `review-package.md` |
| 8 | `refactor/safety-net-establishment` | omn-qa | prose | new type | `validation-evidence.md` |
| 9 | `refactor/behavioral-validation` | omn-qa | prose | new type | `validation-evidence.md` |
| 10 | `fix-bug/regression-validation` | omn-qa | prose | new type | `validation-evidence.md` |
| 11 | `review-pull-request/test-risk-validation` | omn-qa | prose | new type | `validation-evidence.md` |
| 12 | `release/candidate-validation` | omn-qa | prose | new type | `validation-evidence.md` |

  Rows 5 to 7 require no new type: the existing review artifact type's registry record already
  declares that it serves the quality-review phase of `implement-feature`, both
  `review-pull-request` assessments, and the artifact-packaging phase of `release` (`F-025`),
  and `F-012` records that the first of those declarations already landed. Rows 1 to 4 and 8 to
  12 require three new types, one per remaining Wave 1 role, because the reuse survey in section
  7 finds no existing candidate for a scope summary, an implementation-evidence record, or a
  validation-evidence record.

  The identifiers proposed above follow the lower-case hyphenated pattern the template registry
  enforces (`F-025`). The exact strings are fixed when each type is registered; what `D-001`
  binds is that one identifier serves one role's phases and that the same string appears at all
  three declaration points (`C-010`).

  Each new type carries: a template file at the shape the precedent sets — a leading metadata
  block and the tables that turn its owning agent's decision rules into something checkable
  (`F-015`); a template registry record (`F-025`); and a validator built on the declarative
  contract engine by default, reserving a hand-written validator for an owning agent whose
  quality module declares a numbered check set the validator must reproduce exactly (`F-014`).
  Every validator must reject a mutated artifact by a named check, not merely report a result
  (`C-012`).

  Deciding the disposition for all twelve phases is not the same as applying it to all twelve.
  Application is bounded to one primary capability surface per increment (`C-002`); the
  disposition exists so that each later increment applies a decision that is already made.

  Part two, the context-slice declaration disposition (`D-002`). A phase owned by a Wave 1 agent
  obtains context resolution through a declaration keyed by the canonical phase identifier the
  Phase Model publishes. The declaration must contain: the phase identifier as its key, matching
  the Phase Model string exactly (`F-004`); a member list of repository-relative paths, each
  recorded with the declared input of the owning manifest's input contract that it supplies, so
  a member with no consuming input is visible as unnarrowed (`C-011`, `F-007`, `F-028`);
  per-member content addressing, so the frozen snapshot is comparable across attempts (`F-028`);
  an explicit exclusion record naming what was deliberately left out and why, so an absent
  member is distinguishable from an overlooked one (`F-028`); and nothing requiring a member
  kind outside those the three declared phases already use (`A-005`).

  The existing context-slice contract suffices: the disposition adds entries to a declaration
  that already exists and is already exercised by three phases (`F-004`), and changes no guard.
  That sufficiency rests on `A-002`. If `A-002` is false, the consequence is recorded and
  bounded: the context-slice contract itself enters scope, a further architecture decision
  precedes any application, and `R-003` and `Q-002` carry it. This design does not pre-decide
  that change.

- Rationale: `O-002` is the only surviving option of the output-artifact decision that satisfies
  `C-012` and `C-016` together while reusing an artifact type the framework already registered
  for three of the twelve phases. It carries the same impact surface as `O-001` — the same five
  Phase Model tables and the same validator map — at a third of the migration burden, because
  role-shaping collapses eleven prose cells onto three new types rather than eleven. `O-006` is
  the only surviving option of the context-slice decision that leaves the guard contract
  untouched, which matters disproportionately here: `C-005` and `C-007` are invariants over a
  path that already works, and an option that rewrites the guard contract spends those invariants
  to save a declaration step.

- Highest-scoring rejected alternative and why it lost:

  - For the output-artifact decision, `O-001`, one artifact type per prose-output phase. It is
    the only other option that survives criterion 1, and it scores identically on every hard
    constraint and on impact surface, and it decides more narrowly: a per-phase validator can
    encode exactly that phase's decision rules. It lost on reuse leverage, 4 of 9 against 5,
    because it creates a new type even for the three phases the existing review artifact type
    already declares; and decisively on migration burden, eleven contract-affecting artifact
    types against three, each needing a template, a registry record, a validator that decides in
    both directions, and a transition strategy. Its score is −7 against the selected option's 2.
    The narrower decidability it buys is available inside `O-002` through the lens column the
    existing review artifact type already demonstrates (`F-025`).
  - For the context-slice decision, `O-008`, deriving the slice from the owning manifest's
    declared inputs instead of declaring it per phase. It is the only other option of that
    decision to survive criterion 1 — `O-007` scores higher at 1 but is eliminated on `C-011`
    and `C-002`, so it is not an available alternative. `O-008` removes a step from every future
    rollout, which is real value. It lost because it changes the contract that the three
    currently dispatchable phases resolve through (`F-020`), so `C-005` and `C-007` would have
    to be re-verified for a change whose benefit is the removal of one declaration, and because
    `A-002` makes the declaration route available without touching the contract at all.

- Tradeoffs accepted:

  - Three new artifact types are three contract surfaces to keep decidable rather than one. The
    option that keeps one, `O-003`, cannot decide anything, so the multiplication is accepted and
    bounded by `C-012` rather than designed away.
  - A role-shaped type serves several phases with different lenses, so each type's validator must
    decide across all of them. That is a harder validator than a per-phase one; `R-005` records
    the failure mode where it decides nothing, and the test focus areas in section 9 require
    rejection by a named check.
  - Reusing the existing review artifact type binds three phases to one type, so a later change
    to that type reaches all three. `F-012` records that this coupling was already accepted when
    the type was introduced.
  - Per-phase context-slice declaration means every future phase rollout carries a declaration
    step that cannot be skipped. That cost is accepted in exchange for leaving the guard contract
    untouched.
  - The design commits to editing five workflow specifications, two of which are members of the
    frozen context slice of runs that already completed (`F-028`, `A-006`). `R-001` and `P-001`
    carry that exposure; it is not eliminated, because no disposition that makes a prose cell
    resolvable can avoid editing the cell.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Selecting `O-002`: every phase a Wave 1 agent owns declares a role-shaped named artifact type in its Output Artifact cell — the existing review artifact type where its registry record already declares the phase, and one new type per remaining Wave 1 role, each carrying a template at the precedent shape, a template registry record, and a validator that decides in both directions | Yes | ADR `D-001`, status Proposed |
| D-002 | Selecting `O-006`: a Wave 1 phase obtains context resolution through a per-phase declaration keyed by its phase identifier, narrowed to the owning manifest's declared inputs and composed from existing member kinds; the existing context-slice contract suffices and is not changed | Yes | ADR `D-002`, status Proposed |
| D-003 | The registration contract a delivery core agent must satisfy is the enumeration of the five capability-chain links (`F-002`), the context guard (`F-004`), the module-set shape including the quality module required by path (`F-005`, `F-006`), the manifest declarations including an authority scope bounded to the phases it owns (`F-007`), the versioning entry superseding the single-file contract (`F-008`), the capability-identifier precondition (`F-026`, `C-014`), and the two dispositions `O-002` and `O-006` above | No | Inline; it enumerates declarations `F-002` to `F-008` already require and adds no structure beyond `D-001` and `D-002` |
| D-004 | A phase whose disposition would require changing which agent owns it is recorded at a blocking reason of the contract-reconciliation kind rather than re-owned, which bounds the reach of `O-002` | No | Inline; applies `C-015` to the precedent `F-024` already established |
| D-005 | A validator for a new artifact type introduced by `O-002` is built on the declarative contract engine by default, and hand-written only where the owning agent's quality module declares a numbered check set it must reproduce exactly | No | Inline; a consequence of `D-001` recorded in its decision record, selecting between the two shapes `F-014` already offers |
| D-006 | The manifest's supported-workflow declarations for a newly registered Wave 1 agent are bounded to the phases whose output declarations under `O-002` and context declarations under `O-006` are already in place | No | Inline; prevents the side effect `R-009` describes, using the manifest field `F-002` already requires |

## API and Data Model Impact

API changes, in the sense the framework's contracts use — declarations read at resolution time:

- `M-001`, the `implement-feature` Phase Model table: the Output Artifact cells of
  `scope-and-acceptance`, `implementation`, and `quality-review` change from prose to named
  artifact identifiers, per the disposition table in 5.3.
- `M-002`, the `fix-bug` Phase Model table: the Output Artifact cells of `fix-implementation`
  and `regression-validation` change from prose to named artifact identifiers.
- `M-003`, the `refactor` Phase Model table: the Output Artifact cells of
  `safety-net-establishment`, `refactor-implementation`, and `behavioral-validation` change from
  prose to named artifact identifiers.
- `M-004`, the `review-pull-request` Phase Model table: the Output Artifact cell of
  `test-risk-validation` changes from prose to a named artifact identifier. The
  `code-quality-review` cell already names one and is unchanged (`F-011`).
- `M-005`, the `release` Phase Model table: the Output Artifact cells of `artifact-packaging`
  and `candidate-validation` change from prose to named artifact identifiers.
- `M-006`, the runtime validator map: gains one key per newly registered artifact type — three
  under `D-001`.
- `M-012`, each Wave 1 manifest: declares the artifact identifier of every phase it owns that is
  in the increment, with template and contract references that resolve (`F-006`).
- `M-007`, the context-slice phase declaration: gains one entry per phase brought into an
  increment. This is additive, not a contract change, provided `A-002` holds.

Contract compatibility notes for the five Phase Model tables `M-001`, `M-002`, `M-003`, `M-004`,
and `M-005` (`D-001`). One transition strategy governs all five, because the cell they each carry
is the same declaration read by the same resolution path (`F-009`):

- Current shape: a prose Output Artifact cell that the runtime reads literally and that resolves
  against neither the owning manifest nor the validator map (`F-009`, `F-011`).
- Target shape: a backtick-quoted artifact identifier, identical to the owning manifest's
  declared output and to a validator map key.
- Compatibility approach: the cell is edited only inside the change that also carries the
  manifest declaration and the validator key, so the three-point identity `C-010` requires is
  never partially true. A cell naming a type whose template, registry record, or validator does
  not yet exist resolves worse than the prose it replaced, because the phase then blocks on a
  condition that did not previously apply (`F-013`).
- Coexistence period: none. A cell is prose or an identifier, never both.
- Retirement condition: not applicable; no dual semantics are introduced.
- Rollback position: restore the prose cell. The phase returns to blocking with the reason
  `awaiting_capability_registration` it already carries (`F-020`), which is its current state, so
  the rollback is complete and loses nothing. The rollback is per table, so reverting `M-002`
  does not disturb `M-001`, `M-003`, `M-004`, or `M-005`.
- Sequencing obligation carried into section 9: every Input column that names a replaced prose
  string is reconciled in the same change (`P-005`). `F-023` establishes that at least one
  dispatchable phase's Input column names such a string and holds a soft edge only because it
  also declares an explicit alternative; editing the Output cell without the paired Input
  reconciliation re-derives that edge (`F-022`, `A-003`, `R-004`). Within `M-001` this applies to
  the `execution-planning` Input column; within `M-002`, `M-003`, `M-004`, and `M-005` it applies
  to any Input column naming a replaced string, which `P-005` requires be searched for rather
  than assumed absent.

Contract compatibility notes for `M-006` (`D-001`):

- Current shape: seven registered validator keys against six artifact types that active Phase
  Models name as files (`F-010`, `F-020`).
- Target shape: the same set plus one key per newly registered artifact type.
- Compatibility approach: purely additive. An added key changes no existing key's resolution, and
  `F-013` establishes that adding one removes exactly one of five capability conditions, so no
  phase becomes dispatchable as a side effect of the addition alone.
- Coexistence period: none required.
- Retirement condition: not applicable.
- Rollback position: remove the key. Any phase naming it blocks with a capability reason, which
  is the state it held before the disposition was applied.

Contract compatibility notes for `M-012` (`D-001`, `D-003`, `D-006`):

- Current shape: no manifest exists for any Wave 1 agent (`F-003`).
- Target shape: a manifest declaring the phases the agent owns that are in the increment, the
  artifact identifier for each, an authority scope bounded to those phases, and a versioning
  entry superseding the single-file contract (`F-007`, `F-008`).
- Compatibility approach: the supported-workflow declarations are bounded to phases whose output
  and context declarations are already in place (`D-006`), so registering the agent does not
  clear the capability guard for a phase whose declarations are incomplete.
- Coexistence period: the single-file contract remains readable while the module set supersedes
  it, following the precedent `F-008` records.
- Retirement condition: the single-file contract is retired when no reference resolves to it.
- Rollback position: deactivate the registry record. The module set becomes an unreferenced
  directory and every phase returns to its current blocked reason; `C-001` guarantees the record
  never precedes the module set, so there is no state in which a record points at nothing.

Schema and migration changes: none identified in the persistent-data sense, because no data
store participates; the framework's declarations are files read at resolution time (`F-009`,
`F-028`). One persisted-state concern exists and is recorded rather than dismissed. Completed
runs persist a frozen context snapshot whose members include a workflow specification (`F-028`),
and `D-001` edits five such specifications (`M-019`). The migration direction is read-side only:
no completed run's record is written, so the change is reversible by construction. Reader
behavior during transition is the open point — a replay reading the persisted snapshot is
unaffected, while a replay that re-derives the digest from current file content would observe a
difference. `A-006` registers the assumption, `Q-004` routes it, `R-001` carries the risk, and
`P-001` requires it established before the first cell edit.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Decidable artifact type for a review-shaped phase output | The existing review artifact type `review-package.md` | reuse-as-is | Its template registry record already declares that it serves the quality-review phase of `implement-feature`, both `review-pull-request` assessments, and the artifact-packaging phase of `release` (`F-025`), and `F-012` records that one of those declarations already landed. Rows 5 to 7 of the disposition table need no new type |
| Decidable artifact type for a validation-evidence phase output | The seven registered types (`F-010`, `F-025`) | none-found | The search covered every registered validator and every template registry record. The review type carries a review lens and declares capabilities of code review and governance enforcement, not verification evidence; the bug-analysis, investigation-report, release-note, execution-plan, technical-design, and change-proposal types each declare a different owning capability. No candidate carries a verification verdict with residual risk |
| Decidable artifact type for an implementation-evidence phase output | The seven registered types (`F-010`, `F-025`) | none-found | Same search basis: every registered validator and every template registry record. The nearest candidate is the review type, and it was examined and rejected in the row below rather than left unexamined |
| Implementation evidence carried by the review artifact type | The existing review artifact type | rejected | Its declared capabilities are code review and governance enforcement (`F-025`), while the phases in question are owned by an implementation role (`F-011`). Using it would have an implementer emit a review verdict on its own work, which `C-009` and the Producer Exclusion Rule in `F-016` preserve against, and which the gate matrix enforces through role aliases |
| Decidable artifact type for a scope-and-acceptance phase output | The seven registered types (`F-010`, `F-025`) | none-found | Same search basis: every registered validator and every template registry record. The execution-plan type is owned by the planning capability and the review type by review capabilities; no registered type carries scoped requirements with acceptance criteria |
| Validator construction for a new artifact type | The declarative artifact contract engine | reuse-extended | `F-014` establishes it already executes four of the seven registered validators. A new type declares its contract as data rather than adding a fifth hand-written validator; `D-005` reserves the hand-written shape for an owning agent whose quality module declares a numbered check set |
| Template shape for a new artifact type | The version 1.1.0 template precedent | reuse-extended | `F-015` establishes what a template must carry to be decidable: a leading metadata block and the tables that turn its agent's decision rules into something checkable. Each new type follows that shape with its own decision tables |
| Template discovery record for a new artifact type | The template registry record schema | reuse-as-is | `F-025` establishes the record shape and the identifier pattern; a new type registers against it unchanged |
| Context-slice declaration mechanism | The existing context-slice phase declaration | reuse-extended | `F-004` establishes it already declares three phases; a Wave 1 phase adds an entry keyed by its phase identifier, subject to `A-002` |
| Context-slice member composition | The member kinds the three declared phases already use | reuse-extended | `F-028` establishes the loader is frozen, content-addressed, and narrowed per phase; a new phase composes from the same kinds, narrowed to its owning manifest's declared inputs (`A-005`) |
| Runtime module set and registry record shape for an agent | The two existing module sets and the agent registry record schema | reuse-as-is | `F-005` to `F-008` establish the shape, the load order, the quality module required by path, and the supersedes precedent. `D-003` enumerates them rather than inventing a new pattern |
| Recording a phase that cannot be made dispatchable | The recorded blocked-reason mechanism | reuse-as-is | `F-021` establishes that a phase is enqueued and blocked with a recorded reason rather than skipped, and `F-024` establishes that a distinct reason already exists for a phase blocked on contract reconciliation. `C-004` and `D-004` reuse both unchanged |

The survey holds twelve rows. Nine are applicable to the output-artifact decision and are the
denominator of its reuse-leverage scores in 5.2: the four artifact-type rows, the rejected row,
validator construction, template shape, template discovery record, and the runtime module set and
registry record shape. Three are applicable to the context-slice decision and are the denominator
of its scores: the context-slice declaration mechanism, the context-slice member composition, and
recording a phase that cannot be made dispatchable. `O-002` satisfies five of its nine by reuse —
the review-shaped type, validator construction, template shape, template discovery record, and
the module set and registry record shape — while `O-001` satisfies four of the same nine, because
it creates a new type even for the phases the review type already declares. That single row is
the whole reuse difference between them, and it is recomputable from this table.

New structure is proposed only where the outcome is `none-found` or `rejected`: the three new
artifact types. Every other capability the selected approach requires reuses an existing
component, and the one rejection — implementation evidence carried by the review artifact type —
records why that component is unsuitable rather than leaving it unexamined.

## Operational Considerations

- Logging and observability updates: applying either disposition changes what a phase records.
  A phase that previously emitted only a blocked reason and an open escalation (`M-018`, `F-021`)
  begins emitting a dispatch, a result envelope, a validation report, and progress events. The
  blocked-reason set narrows rather than disappears, because `F-013` establishes that clearing
  one condition of five leaves the others reporting. The verifier counts in `M-018` are the
  measure `S-011` names, so they are read after the declarations are in place (`P-011`), never
  before.

- Error handling strategy: the failure classification the framework already applies is the one
  this design relies on (`F-029`). A phase whose declarations are incomplete blocks at the first
  failing guard with a recorded reason and a structured failure envelope; it does not dispatch
  and fail late. A phase whose declarations resolve but whose artifact is rejected is classified
  and retried under a bounded budget. That asymmetry is deliberate and shapes the sequencing: a
  partially correct declaration is recoverable, an absent one is not, so `P-002` through `P-005`
  establish declarations in the order that keeps a failure recoverable (`C-004`, `M-006`).

- Security considerations: neither disposition grants authority. The security surface they touch
  is the authority scope a newly registered agent declares (`M-012`, `F-007`) and the phases its
  manifest claims to support (`F-002`). `D-006` bounds the supported-workflow declarations to
  phases whose declarations are complete, and `R-008` and `R-009` carry the two ways that bound
  can fail — an authority scope copied without narrowing, and a registration that clears the
  capability guard for phases the increment did not cover. Compliance impact: every path this
  design touches is in routing scope under the closed exemption set (`F-018`), so each
  application is itself a routed framework change requiring its own run record; and `C-009` with
  `F-016` and `F-017` keeps gate ownership and the Producer Exclusion Rule unchanged, including
  for `omn-product-owner`, which is a listed owner of the Scope Gate its own phase produces
  evidence for. The disposition changes what that phase emits, never who accepts it.

- Performance considerations: none identified beyond `C-007`. The supplied context records no
  performance constraint or quality attribute over resolution cost, and the change alters
  declarations read at resolution time (`F-009`, `F-028`) rather than any execution path.
  Asserting a performance expectation here would reference no constraint, so none is asserted.
  `C-007` is treated as a correctness property — no verifier check moves from pass to fail — and
  is verified at `P-011`.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The derivation of a completed run's replay fingerprint is established — computed over the persisted record, or re-derived from current file content | M-019, M-001, M-002, M-003, M-004, M-005 | none | `C-006` is an invariant over records that already exist. An edit made before this is established cannot be shown non-breaking, and reverting the edit does not restore the evidence that the fingerprint was read beforehand. This is the reversibility safeguard for every later cell edit | T-001, T-012 |
| P-002 | The artifact type exists as a template file at the precedent shape and as a template registry record, before that type is named in any Output Artifact cell | M-009, M-010 | none | `F-006` requires each declared output's template reference to resolve; naming a type whose template does not resolve makes the output contract unresolvable | T-001, T-012 |
| P-003 | A validator is registered under the exact artifact identifier, and decides in both directions, before that identifier appears in an Output Artifact cell | M-006, M-008 | P-002 | `C-010` requires the identifier to be a validator map key at the moment the cell is read, and `C-012` requires the validator to decide rather than to report | T-001, T-012, T-013 |
| P-004 | The owning agent's manifest declares the artifact identifier among its outputs, with template and contract references resolving, before the Output Artifact cell names it | M-012 | P-002 | The third point of the three-point identity `C-010` requires, and the resolution `F-006` requires | T-001, T-006, T-007, T-012 |
| P-005 | The Output Artifact cell is edited together with every Input column that names the replaced prose string, in one change | M-001, M-002, M-003, M-004, M-005 | P-001, P-003, P-004 | `F-022` derives the dependency graph from those columns and `F-023` shows a dispatchable phase whose Input column names such a string. Editing one without the other re-derives an edge and puts `C-005` at risk | T-001, T-012 |
| P-006 | Every capability identifier a Wave 1 registry record will declare exists in the capability matrix before the record is activated | M-016, M-011 | none | `C-014` and `F-026`: an identifier is added to the matrix before a manifest or a record may reference it | T-006, T-008 |
| P-007 | The runtime module set exists and every module in its declared load order resolves on disk, including the quality module required by path, before the registry record is activated | M-012, M-011 | P-004, P-006 | `C-001` forbids activation ahead of the module set, and `F-006` requires the quality module by path independently of the manifest | T-006, T-007, T-008 |
| P-008 | Host entrypoint resolution is demonstrated after the module set and the registry record exist, and the result is recorded | M-013 | P-007 | `F-003` and `F-008`: the registration is an entry point that loads the manifest, so what it resolves changes when the manifest appears. The change must be observed rather than assumed | T-006, T-009 |
| P-009 | The context-slice declaration for the phase exists, with each member recorded against the declared input requiring it, before the phase is dispatched | M-007, M-012 | P-007 | `C-011`: the context guard is separate and blocks after the capability guard clears (`F-004`). The per-member recording is what makes an unnarrowed slice visible | T-002, T-014 |
| P-010 | A phase is dispatched only after `P-005`, `P-007`, `P-008`, and `P-009` hold for it; a phase for which any does not hold is left blocked with its recorded reason | M-011, M-018 | P-005, P-007, P-008, P-009 | `C-004` and `F-021`: a phase that cannot clear a guard is reported at that guard, never narrowed out of scope | T-003, T-010, T-011, T-015 |
| P-011 | The four verifier verdicts are re-read after the increment's declarations are in place, and before the increment status is recorded | M-018 | P-010 | `C-007` is an invariant over the whole framework, so it is evidence taken after the change; `C-003` forbids a completion claim resting on anything but the run record | T-005, T-010, T-013, T-015 |
| P-012 | A phase whose disposition would require changing which agent owns it is recorded at its blocking reason rather than applied | M-004, M-011 | none | `C-015` and `D-004`. `F-024` establishes that a phase in this family already blocked for exactly this cause, so the condition is precedent rather than hypothesis | T-003, T-004, T-012, T-015 |

These are structural constraints, not tasks. Every `T-nnn` reference names a task the supplied
execution plan already created; none is created here, and the breakdown they belong to remains
the planner's. `Binds` names the tasks a step constrains, which is not the same as performing
them: `T-001` and `T-002` are answered by the decisions `D-001` and `D-002` and their records,
and the steps that bind them state the conditions under which what those tasks decide may be
applied. `T-003` is answered by `Q-005`, which routes the target-phase decision to its owner
rather than deciding it here, and `P-010` and `P-012` constrain what that answer must satisfy.
`T-006` is answered by `D-003`, and `P-004` and `P-006` through `P-008` enumerate the
declarations that contract requires. Every one of the fifteen supplied tasks is bound by at
least one step above.

### Test Strategy Focus Areas

For `omn-qa`:

- Guard-by-guard verdicts for the three currently dispatchable phases, taken after each Phase
  Model column edit, not only at the end of the increment (`C-005`).
- The replay fingerprint of the two completed reference runs, taken before and after the first
  column edit, with the derivation recorded (`C-006`, `A-006`, `P-001`).
- The three-point identity of every newly named artifact identifier: the Phase Model cell, the
  owning manifest's declared output, and the validator map key, checked as three separate
  observations so a failure names which point is missing (`C-010`, `R-002`).
- Each new validator's decisiveness in both directions: a conforming artifact accepted, and a
  mutated artifact rejected by the named check (`C-012`, `R-005`).
- Context-slice resolution for the phase brought into the increment, with each member recorded
  against the declared input requiring it and each exclusion recorded with its reason (`C-011`,
  `R-012`).
- The four verifier verdicts and the count deltas they report, distinguishing a changed count
  from a changed verdict (`C-007`, `R-010`).
- The blocked reason carried by every Wave 1 phase the increment did not cover, including any
  phase blocked on contract reconciliation rather than capability registration (`C-004`,
  `R-009`, `P-012`).
- Whether any Input column names a prose string the increment replaced (`A-003`, `R-004`).

### Rollout and Rollback

- Rollout: one primary capability surface per increment (`C-002`), following `P-001` to `P-011`
  for the phase the increment covers. Within an increment the order is: establish the fingerprint
  derivation and the capability identifiers, then the type's template and registry record, then
  the validator, then the manifest declaration, then the column edit with its Input
  reconciliation, then the module set and registry record, then entrypoint verification, then the
  context-slice declaration, then dispatch, then the verifier re-read. Phases the increment does
  not cover are left blocked with their recorded reasons and reported (`P-010`, `P-012`).
- Rollback: every declaration this design introduces is removable, and removing it returns the
  phase to the blocked reason it already carries (`F-020`). Restore a prose cell and its Input
  column; remove a validator key; remove a template record; deactivate a registry record. `C-001`
  guarantees no state in which a record points at an absent module set. The single exposure that
  removal does not undo is the one `R-001` names: if a completed run's fingerprint is re-derived
  from current file content, the first cell edit is observable in that run's replay before any
  rollback, which is why `P-001` precedes `P-005`.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | migration | The first Phase Model column edit lands in a specification named by a completed reference run's frozen context slice, and `A-006` is false | `INV-3` and `C-006` fail for a reason unrelated to the disposition, and the failure is observed after the edit rather than before | medium | M-019, D-001, P-001 | `P-001` establishes the fingerprint derivation before any cell edit; `Q-004` routes the question | omn-tech-lead |
| R-002 | contract | A newly named identifier is present at all three declaration points and the output contract still does not resolve, making `A-001` false | `D-001`'s resolution path is incomplete; every applying phase re-scopes and the increment cannot produce an accepted artifact | medium | D-001, M-006, P-003 | `P-003` and `P-004` establish each declaration point separately so the failing point is identifiable rather than inferred; `Q-001` routes the requirement | omn-tech-lead |
| R-003 | structural | Adding an entry keyed by the phase identifier does not clear the context guard, making `A-002` false | An additional architecture decision precedes `P-009`, the context-slice contract enters scope, and the increment is delayed | medium | D-002, M-007, P-009 | `P-009` records the declaration and the guard verdict together, so the failure is observed at the guard; `Q-002` routes the contract question | omn-tech-lead |
| R-004 | structural | A cell edit lands without reconciling an Input column that names the replaced prose string, making `A-003` false | A currently dispatchable phase gains or loses a hard predecessor and `C-005` fails; `INV-1` or `INV-2` breaks silently, since a changed edge produces no error | medium | M-001, P-005 | `P-005` makes the cell edit and the Input reconciliation one change; the test focus areas require a search for any Input column naming a replaced string | omn-tech-lead |
| R-005 | contract | A declarative contract is registered whose checks no conforming-and-mutated pair distinguishes | The phase reports an accepted artifact that decides nothing, and `BI-4` is reported satisfied without evidence, violating `C-012` | medium | D-001, M-008, P-003 | `P-003` requires the validator to decide in both directions before the identifier is named in a cell; the test focus areas require rejection by a named check | omn-qa |
| R-006 | structural | A phase's prose output is an assessment its owning agent's contract places outside its scope, making `A-004` false, as `F-024` records for one phase already | The disposition for that phase becomes a role-boundary reconciliation, and the phase is reported blocked instead of applied | medium | D-001, P-012 | `P-012` records the phase at its blocking reason rather than applying the disposition; `Q-003` routes the ownership question to product authority | omn-product-owner |
| R-007 | migration | A cell edit executes ahead of the template, registry record, or validator the identifier names | The phase's output contract is unresolvable and it blocks on a condition that did not previously apply, which is worse than the prose it replaced | low | M-001, M-002, M-003, M-004, M-005, P-005 | The prerequisite chain from `P-002` and `P-003` and `P-004` into `P-005` | omn-tech-lead |
| R-008 | security | A module set is authored by copying the existing pattern without narrowing its authority scope | A dispatchable agent declares authority wider than the phases it owns, and the permitted-write set the runtime derives is wider than the phase needs | low | M-012, P-007 | `P-007` requires the module set to resolve with an authority scope bounded to the phases the agent owns; `D-003` enumerates it as a registration requirement | omn-tech-lead |
| R-009 | operability | A registry record is activated while the manifest declares supported phases whose output or context declarations are absent | Previously blocked phases clear the capability guard and dispatch without resolvable declarations, contradicting `C-004` and `C-013` | medium | M-011, M-012, P-007, P-010 | `D-006` bounds the supported-workflow declarations to phases whose declarations are in place; `P-010` leaves every other phase blocked with its recorded reason | omn-tech-lead |
| R-010 | operability | Verifier verdicts are read before the increment's declarations are complete | A count change is mistaken for a verdict change and `C-007` appears to regress, or a real regression is masked by a partially applied increment | low | M-018, P-011 | `P-011` fixes the reading point after the declarations and before the status is recorded; the test focus areas separate a changed count from a changed verdict | omn-qa |
| R-011 | delivery | Increment status is recorded from the declarations rather than from a run record | A capability is reported delivered that no run demonstrates, contradicting `C-003` and `S-007` | medium | P-010, P-011 | `P-010` produces the run record and `P-011` the verifier evidence; a complete status rests on both | omn-tech-lead |
| R-012 | structural | The owning agent's input contract names an input that no existing context-slice member kind supplies, making `A-005` false | `D-002`'s composition rule is incomplete for that phase, and a new member kind must be defined before the phase can resolve a slice | low | M-007, D-002, P-009 | `P-009` records each member against the declared input requiring it, so a missing input is visible at declaration time rather than at dispatch | omn-tech-lead |

## Estimate and Confidence

- Overall: `L` (confidence: low).

- Breakdown:

  - `D-001` applied to one phase — `P-002` through `P-005`: `M`. One contract change across two
    declaration surfaces, plus a new template, a template record, and a validator, with a clear
    transition and a complete rollback position.
  - `D-002` applied to one phase — `P-009`: `S`. A bounded change within one boundary using an
    existing mechanism, conditional on `A-002`.
  - The module set, registry record, and entrypoint verification for one agent — `P-006` through
    `P-008`: `L`. A cross-boundary change spanning the module set, the registry, and the host
    registration, touching all five capability-chain links.
  - Evidence taken before and after — `P-001` and `P-011`: `S` each.
  - Reporting the phases the increment does not cover — `P-010`, `P-012`: `S`.
  - Applying `D-001` to the remaining phases in later increments: `L`, not decomposed per phase,
    because those increments are deferred and their entry conditions are not yet recorded.

- Scope assumptions: the estimate covers deciding both dispositions and applying them to one
  phase inside one increment, under `C-002`. It excludes authoring any module set, template,
  validator, registry record, or column edit — that is the consuming work. It excludes the
  deferred increments and the eleven phases outside increment 1. It assumes `A-001` through
  `A-006` hold; each is registered with its impact if false.

- Uncertainty drivers: confidence is `low` because the estimate depends on two speculative
  impacts (`M-007`, `M-019`) and on three unconfirmed assumptions that change the shape of the
  work rather than its size — `A-001` determines whether the resolution path is complete,
  `A-002` determines whether the context-slice contract enters scope at all, and `A-006`
  determines whether `P-001` is a check or a re-baseline. `F-024` shows one phase in this family
  already failed on role-boundary grounds, so `R-006` is drawn from precedent rather than from
  judgement. Effort is expressed as complexity only; scheduling, resourcing, and sequencing
  feasibility belong to `omn-tech-lead`.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does output-contract resolution require anything beyond the three-point string identity in `C-010` and the template and contract reference resolution in `F-006`? | No | omn-tech-lead | D-001, M-006, P-003 | If it does, `D-001`'s resolution path gains a step and `P-003` and `P-004` extend; if not, the disposition applies as recorded |
| Q-002 | Does the existing context-slice contract admit a new per-phase declaration without being changed? | No | omn-tech-lead | D-002, M-007, P-009 | If not, the context-slice contract enters scope, a further architecture decision precedes `P-009`, and this package's out-of-scope boundary is re-drawn by that decision rather than by this one |
| Q-003 | For which Wave 1-owned phases, if any, does the disposition imply changing the owning agent, as `F-024` already records for one phase outside this set? | No | omn-product-owner | D-001, P-012 | Each such phase is reported at its blocking reason rather than applied, and its rollout leaves this design's scope. Deciding phase ownership is product and delivery authority, not architecture authority, so it is routed rather than decided here |
| Q-004 | Is a completed run's replay fingerprint computed over the persisted run record, or re-derived from the current content of its context-slice member files? | No | omn-tech-lead | M-019, P-001 | If re-derived, every Phase Model edit requires a recorded re-baseline of `INV-3` before it lands, and `P-001` becomes a design change rather than a check |
| Q-005 | Which phase is the increment-1 target, and which Wave 1-owned phases are excluded from it? | No | omn-product-owner | P-010, P-012 | Both dispositions are phase-independent, so the answer changes which phase applies them first, not what they say. Scope authority rests with the product owner; this package does not narrow it |
| Q-006 | Do `D-001` and `D-002` hold as recorded? | No | omn-tech-lead | D-001, D-002, P-005, P-009 | Acceptance is a Design Gate decision. The gate's owners are `omn-architect` and `omn-tech-lead`, and under the Producer Exclusion Rule the architecture role produced these records, so the accepting owner named here is `omn-tech-lead` (`F-027`). Both records remain at status Proposed until accepted, and no applying step — `P-005` or `P-009` — may begin against an unaccepted record |
| Q-007 | Ten of the twelve phase owners hold no registry record and resolve only to a host registration file (`F-003`, `F-020`), so agent references in this package resolve through the agent contract set rather than through the registry | No | omn-tech-lead | M-011, M-013 | This is the framework gap the runtime notes already record. It is registered here because this package names those agents as owners; it resolves as each agent registers, which is what this increment begins |

No entry is blocking: none prevents approach selection, and each affects application rather than
design. Package status is therefore `complete` rather than `blocked`. `Q-001` through `Q-004`
each correspond to a registered assumption and a risk — `A-001` and `R-002`, `A-002` and `R-003`,
`A-004` and `R-006`, `A-006` and `R-001` — so an answer that contradicts the assumption has a
recorded consequence rather than an undefined one.

Both decision records remain at status `Proposed`. Acceptance is a Design Gate decision and is
not this agent's to make.

## Sign-off

- Architect: `architect` — producing role, excluded from accepting this package under the
  Producer Exclusion Rule
- Tech Lead: `omn-tech-lead` — accepting owner for the Design Gate
- QA: `omn-qa` — verification focus areas in section 9
- Product confirmation: `omn-product-owner` — required for `Q-003` and `Q-005` before `P-005`,
  `P-010`, or `P-012` is applied

Design Gate owners per the workflow gate matrix are `omn-architect` and `omn-tech-lead`. The
matrix records that `omn-architect` names the architecture role now implemented by `architect`
and that the Producer Exclusion Rule reads through role aliases (`F-027`), so acceptance of this
package and of decision records `D-001` and `D-002` rests with `omn-tech-lead`. All lines are
left unsigned by the producing agent.

Items requiring approval before execution: `D-001` and `D-002` at the Design Gate; `Q-003` and
`Q-005` from product authority; the verification focus areas in section 9 by `omn-qa` before
`P-011` is treated as evidence.

### Appendix A: Traceability Closure

Forward closure — every statement maps to an objective, a module, a constraint, or an open
question:

| Statement | Covered by |
|---|---|
| S-001 | M-011, M-012 |
| S-002 | AO-3, M-001 to M-013 |
| S-003 | AO-3, D-001, D-002 |
| S-004 | C-005, C-006, C-007, C-008, C-009 |
| S-005 | C-002 |
| S-006 | C-001 |
| S-007 | C-003 |
| S-008 | C-004, C-016 |
| S-009 | AO-1, AO-2, AO-3, C-016 |
| S-010 | AO-1, AO-2 |
| S-011 | AO-5, M-018 |
| S-012 | M-011 |
| S-013 | M-012 |
| S-014 | AO-2, P-009, P-010 |
| S-015 | AO-1, C-010, C-012 |
| S-016 | C-007, M-018 |
| S-017 | Out-of-scope list, C-009 |
| S-018 | AO-5, C-013 |
| S-019 | AO-4, C-005, C-006 |

Backward closure: every module in 5.1 carries an `F-nnn` or `A-nnn` basis; every decision in 5.4
names the option it derives from (`D-001` from `O-002`; `D-002` from `O-006`; `D-003` to `D-006`
from the two selected options as consequences); every option in 5.2 is scored against the
constraint set in 4.3, and every reuse-leverage figure in 5.2 is recomputable from the survey in
section 7 and the applicable row sets that section names.

Lateral closure: every risk in section 10 attaches to an existing `M-nnn`, `D-nnn`, or `P-nnn`;
every plan step in section 9 references modules from 5.1; each of `D-001` and `D-002` has exactly
one decision record; both speculative impacts (`M-007`, `M-019`) carry risks (`R-003`, `R-001`);
every approach-changing assumption carries a risk (`A-001` to `R-002`, `A-002` to `R-003`,
`A-003` to `R-004`, `A-004` to `R-006`, `A-005` to `R-012`, `A-006` to `R-001`); every supplied
planner task `T-001` to `T-015` is named in the `Binds` column of at least one sequencing
constraint.

Register integrity: every claim about the current framework in this package carries an `F-nnn` or
`A-nnn` reference. No production code, test, migration, script, or configuration was written; no
application module was edited; no external system, repository, or ticketing tool was accessed.
