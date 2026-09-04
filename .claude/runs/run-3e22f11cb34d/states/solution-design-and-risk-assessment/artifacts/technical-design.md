```yaml
design:
  designId: FC-001-review-package-routing-technical-design
  changeReference: FC-001
  sourceInputs:
    - type: change-request
      reference: runs/inputs/review-package-routing-feature-request.md
    - type: business-intent
      reference: runs/inputs/review-package-routing-business-intent.md
    - type: architecture-context
      reference: runs/inputs/review-package-routing-architecture-context.md
    - type: execution-plan
      reference: runs/run-3e22f11cb34d/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003]
  consumesPlan: runs/run-3e22f11cb34d/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:87e7a870518ba78d52e011e0ccd641be
  contextDigest: sha256:7d8ca68a52d086a09b4c0e56a1e900b7
```

## Metadata

- Feature or Change ID: FC-001
- Author: architect
- Reviewers: omn-tech-lead, omn-qa
- Last Updated: 2026-08-18

## Objective

- Desired outcome: the review package artifact type is routed by the same mechanism that
  routes every other validated artifact type in the framework, a Phase Model Output Artifact
  cell that resolves to a file contract, so that the set of contracted-but-unrouted artifact
  types is empty and a review verdict has a declared location under run evidence.
- Architectural objectives:
  - Exactly one Phase Model Output Artifact cell in the review lifecycle resolves to the
    `review-package.md` file contract. Traces to `S-001`, `S-003`, `S-007`, `S-010`.
  - The set of contracted artifact types that no Phase Model Output Artifact column names is
    empty. Traces to `S-002`, `S-005`, `S-008`.
  - The declared emitter is the phase whose owning role holds the artifact's registered
    capabilities, so no agent is assigned an artifact its own contract forbids producing.
    Traces to `S-011`, `S-014`.
  - The phase edges the runtime derives from the affected Phase Model's Input and Output
    Artifact columns are unchanged by the declaration. Traces to `S-012`, `S-017`.
  - Artifact routing is declared in exactly one place. Traces to `S-008`, `S-012`.
- In scope: the Output Artifact declaration of one phase of `workflows/review-pull-request.md`;
  the derived edge set of that workflow; the routed-artifact coverage assertion; the
  artifact-type registry record's role as identity rather than routing; the gap record that
  raised the defect.
- Out of structural scope, and each bounds the impact surface before analysis begins:
  - The structure of `templates/review-package.md`. `F-002` establishes it is contracted and
    decidable; no statement asks for a structural change to it.
  - The `VALIDATORS` map and `resolve_output_contract` in `runtime/framework_runtime.py`.
    `F-002` and `F-004` establish the resolution mechanism already covers the artifact type;
    the missing half is the phase-side declaration.
  - Gate names and gate ownership in `workflows/workflow-gate-matrix.md`. `C-009` forbids it.
  - Making any phase dispatchable. `C-010` forbids claiming it, and `F-014` places
    dispatchability behind capability registration this change does not perform.
  - Declaring the artifact in any owning agent's manifest `outputs`. `C-003` reserves that as
    a decision to surface; `D-002` surfaces it.
  - Routing any artifact type other than the review package, and routing this one to more than
    one phase. `C-001` permits one phase.

## Requirements Summary

- Functional requirements:
  - One phase of the review lifecycle declares `review-package.md` as the artifact it emits
    (`S-003`, `S-007`).
  - Exactly one phase, not several, names the artifact (`S-010`).
  - The declaring phase is the phase whose declared work the artifact already describes; no new
    phase is introduced and no phase changes owner (`S-011`).
  - The recorded gap is closed in the record that raised it (`S-009`).
- Non-functional requirements:
  - The routed-artifact coverage proof counts the artifact as routed, so the count of
    contracted-but-unrouted artifact types reaches zero (`S-008`).
  - Registry coverage, validator coverage, and every previously proven run still verify after
    the change, with unresolved counts unchanged or lower (`S-012`).
  - No agent gains or loses a contract; an owning-agent output declaration the change would
    require is surfaced as a decision rather than made (`S-014`).
  - The change does not claim the phase becomes executable (`S-015`).
  - A review verdict is retrievable as a validated artifact under run evidence rather than as
    prose in an Output Artifact column (`S-004`).
- Acceptance criteria: cited from the supplied business intent rather than restated. The
  framework carries no active contracted artifact type that no routed phase emits (`S-006`),
  and the change is accepted on declaration-level and coverage-level evidence because `S-015`
  excludes executability from its claim. The execution plan's acceptance criteria 1 through 6
  are the planner's and are not restated here.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | `workflows/review-pull-request.md` declares five phases, and every Output Artifact cell in that table is prose describing a deliverable; none names a file | Architecture context, asserted property 1 |
| F-002 | `review-package.md` is registered in `registry/templates.yaml`, carries a validator in the `VALIDATORS` map, and passes `verify_validators.py` against its fixture with a declared mutation caught by `P3` | Architecture context, asserted property 2; corroborated by the `review-package` record in `registry/templates.yaml` |
| F-003 | `verify_validators.py` check `V1` reads the Output Artifact column of every active Phase Model, treats any token ending in `.md` as a routed artifact type, and asserts coverage in one direction only: every routed artifact has a validator. A validated artifact that no phase routes is invisible to it | Architecture context, asserted property 3 |
| F-004 | `runtime/framework_runtime.resolve_output_contract` resolves a phase's declared artifact against the owning agent's manifest outputs and the `VALIDATORS` map; a phase whose artifact is prose resolves no file contract | Architecture context, asserted property 4 |
| F-005 | `review-pull-request/structural-compliance` blocks with failure class `workflow-contract-violation`, because the artifact that phase asks of `architect` is neither declared in the architect manifest's `outputs` nor covered by a validator | Architecture context, asserted property 5 |
| F-006 | `code-quality-review` is owned by `omn-dev-2-reviewer`, which is host-invocable through `agents/omn-dev-2-reviewer.agent.md` and holds no record in `registry/agents.yaml` | Architecture context, asserted property 6; corroborated by `registry/agents.yaml` |
| F-007 | A Phase Model is a machine-read contract: the runtime derives sequencing edges from its Input and Output Artifact columns, so a change to either changes what the runtime enforces | Architecture context, design constraint 1; corroborated by the Resolution Rules of `workflows/implement-feature.md` |
| F-008 | `registry/agents.yaml` holds exactly two records, `planner` and `architect`, both active | `registry/agents.yaml` |
| F-009 | The `review-package` record in `registry/templates.yaml` is active at version 1.0.0, names `templates/review-package.md`, declares capabilities `code-review` and `governance-enforcement`, and describes one artifact type serving the `quality-review` phase of implement-feature, both review-pull-request assessments, and the `artifact-packaging` phase of release, with the Category column carrying the review lens | `registry/templates.yaml` |
| F-010 | The template registry record schema declares no field naming which phases emit an artifact type; `description` is prose | `registry/templates.yaml`, `recordSchema` |
| F-011 | `runtime/README.md` known gap 7 records that `review-package.md` is validated but not routed; that four phases across three workflows emit a review output each named in prose as "review findings log", "quality findings with correction requests", "structural and security findings assessment", and "versioned artifacts with packaging evidence"; and that what remains is naming `review-package.md` in those Output Artifact columns and in the owning agents' manifest `outputs` | `runtime/README.md` |
| F-012 | The framework already routes one artifact type from two phases: `technical-design.md` from `implement-feature/solution-design-and-risk-assessment` and `refactor/scope-invariants-and-risk-profile`, and `investigation-report.md` from `investigate/technical-discovery` and `research/technical-validation`, each with one registered validator | `runtime/README.md`, Validation Engine coverage table |
| F-013 | 33 of 36 declared phases block at `G1-CAPABILITY`; a phase needs an agent registry record and a registered validator before it can be dispatched | `runtime/README.md`, known gap 1 |
| F-014 | `G1-CAPABILITY` requires the whole chain to resolve: active registry record, manifest declaring this workflow and phase, host registration, resolvable phase skills, registered validator | `runtime/README.md`, transition guards |
| F-015 | The runtime derives a hard edge when an earlier phase's Output Artifact is named in a later phase's Input column; failing that, the immediately preceding row creates one; an edge is downgraded to soft when the Input column declares an explicit alternative the supplied inputs already satisfy | `runtime/README.md`, "Where the dependency graph comes from" |
| F-016 | `agents/capability-matrix.md` rates `omn-dev-2-reviewer` Primary for Code Review and Governance and Primary for Quality Verification, and rates `architect` Secondary for Code Review and Governance. The capability identifiers for that column are `code-review` and `governance-enforcement` | `agents/capability-matrix.md` |
| F-017 | The `architect` record in `registry/agents.yaml` declares nine capabilities, none of which is `code-review` or `governance-enforcement` | `registry/agents.yaml` |
| F-018 | The architect contract places reviewing pull requests and assessing concrete diffs out of scope, and assigns verification of a concrete change to `omn-dev-2-reviewer`; its declared role in `review-pull-request` is structural compliance expectations at participation `supporting` | `agents/architect/identity.md`, `agents/architect/system.md` |
| F-019 | `agents/architect/manifest.yaml` declares outputs `technical-design` and `architecture-decision-record` only, and declares `supportedWorkflows` including `review-pull-request` at phase `structural-compliance` | `agents/architect/manifest.yaml` |
| F-020 | The five review-pull-request phase identifiers and their owners are `code-quality-review` (omn-dev-2-reviewer, skills S03, S07, S09), `structural-compliance` (architect, skills S01, S06, S09), `test-risk-validation` (omn-qa), `documentation-impact` (omn-documentation), and `merge-decision` (omn-tech-lead) | `skills/agent-skill-matrix.md`, Review Pull Request table |
| F-021 | `workflows/implement-feature.md` and `runtime/README.md` are both members of this run's frozen context slice | Invocation envelope, `context_slice.members` |
| F-022 | `workflows/review-pull-request.md` is not a member of this run's frozen context slice | Invocation envelope, `context_slice.members` |
| F-023 | `workflows/workflow-gate-matrix.md` names four gates for review-pull-request, owned respectively by omn-dev-2-reviewer with omn-tech-lead, by omn-architect with omn-tech-lead, by omn-qa with omn-dev-2-reviewer, and by omn-tech-lead with omn-orchestrator | `workflows/workflow-gate-matrix.md` |
| F-024 | `workflows/implement-feature.md` declares `quality-review`, owned by `omn-dev-2-reviewer`, with the prose Output Artifact "review findings log, verification report" | `workflows/implement-feature.md`, Phase Model |
| F-025 | A context slice is declared for three phases only, `execution-planning`, `solution-design-and-risk-assessment`, and `scope-invariants-and-risk-profile`, so every other phase blocks at `G2-CONTEXT` if it ever clears `G1-CAPABILITY` | `runtime/README.md`, known gap 6 |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | No committed run's frozen context slice contains `workflows/review-pull-request.md` | `C-006` and `C-007` turn on whether the file this change edits sits inside committed run evidence, and `F-022` establishes only that it is absent from this run's slice | The affected runs must be re-verified before the change is accepted, `P-005` gains a prerequisite, and `C-007` may fail | omn-tech-lead |
| A-002 | `omn-dev-2-reviewer` ships no agent manifest, so it has no `outputs` block that the routed declaration could contradict | `C-003` forbids an agent gaining or losing a contract, and `F-006` establishes only the absence of a registry record, not the absence of a manifest | `C-003` engages: the declaration requires an `outputs` change to an existing manifest, `D-002` changes from deferral to escalation, and `M-007` becomes a contract-change | omn-tech-lead |
| A-003 | No Input column in `workflows/review-pull-request.md` names the prose Output Artifact token that this change replaces, from a phase other than the immediately following row | `F-015` derives a hard edge from an Input entry naming an earlier phase's Output Artifact, and `F-022` puts the Input columns outside the confirmed fact set | One or more Input entries must be re-pointed to `review-package.md`, the after-state edge set recorded in `P-004` changes, and `P-005` grows in scope | omn-tech-lead |
| A-004 | The blocked reason recorded for `code-quality-review` is unchanged by the declaration, because the `G1-CAPABILITY` chain fails first at the missing agent registry record | `C-005` forbids trading one blocked reason for another without surfacing it, and `F-014` orders the chain but does not state which link the reporter names | The change trades one blocked reason for another, which must be surfaced before acceptance, and `D-001`'s rationale weakens | omn-tech-lead |
| A-005 | A Phase Model Output Artifact declaration alone leaves the blocked-phase count reported by `verify_registry_coverage.py` unchanged | `C-007` requires unresolved counts unchanged or lower, and `F-013` records the count without stating its sensitivity to an Output Artifact declaration | `S-012` is unmet, and the change is rejected at the Verification Gate | omn-qa |
| A-006 | A committed run's verification recomputes its context slice from the files on disk, so editing a slice member changes what that verification reproduces | `C-006` and `C-011` both attach to `runtime/README.md`, which `F-021` places inside this run's own slice | No re-verification obligation attaches to the gap-record update, `P-006` loses its prerequisite, and `R-006` falls away | omn-tech-lead |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | functional | Exactly one phase declares `review-package.md` as its Output Artifact | Hard | `S-010` |
| C-002 | structural | The declaring phase is the phase whose declared work the artifact already describes; no new phase is introduced and no phase changes owner | Hard | `S-011` |
| C-003 | structural | No agent gains or loses a contract in this change; an owning-agent output declaration the change would require is surfaced as a decision, not made | Hard | `S-014` |
| C-004 | structural | The framework's discovery registries are single-authority; the change adds no second place where an artifact type is declared | Hard | Architecture context, design constraint 4 |
| C-005 | structural | A phase's declared artifact must be one the Validation Engine can decide, and trading one blocked reason for another must be surfaced rather than accepted as an improvement | Hard | Architecture context, design constraint 2; `S-018` |
| C-006 | migration | Committed run evidence must remain valid; a change to any file inside a frozen context slice requires the affected runs to be re-verified rather than assumed intact | Hard | Architecture context, design constraint 3 |
| C-007 | quality-attribute | Registry coverage, validator coverage, and every previously proven run still verify after the change, with unresolved counts unchanged or lower | Hard | `S-012` |
| C-008 | structural | A Phase Model is a machine-read contract; a change to its Input or Output Artifact column changes the sequencing the runtime enforces | Hard | Architecture context, design constraint 1; `F-007` |
| C-009 | compliance | Gate ownership is out of scope; `workflows/workflow-gate-matrix.md` is not changed | Hard | `S-013` |
| C-010 | functional | The change does not claim the phase becomes executable | Hard | `S-015` |
| C-011 | operability | The recorded gap is closed in the record that raised it | Hard | `S-009` |
| C-012 | quality-attribute | A review verdict is retrievable as a validated artifact under run evidence rather than as prose in an Output Artifact column | Hard | `S-001`, `S-004` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `workflows/review-pull-request.md` Phase Model table, `code-quality-review` row, Output Artifact cell | contract-change | F-001, F-011, F-020 | The machine-read Output Artifact declaration read by the Task Router, by `resolve_output_contract`, and by `verify_validators.py` check `V1` | confirmed |
| M-002 | `runtime/verify_validators.py` check `V1` | operational-impact | F-003 | Routed-artifact coverage assertion; its input set gains one token and its reported result changes | confirmed |
| M-003 | `runtime/framework_runtime.py`, `resolve_output_contract` and the `VALIDATORS` map | no-change-verified | F-002, F-004 | Phase output contract resolution. The map already carries the artifact type and the resolution logic is unchanged; this change supplies only the phase-side declaration | confirmed |
| M-004 | `runtime/review_package_validator.py` | no-change-verified | F-002 | Artifact conformance decision, already proven against its fixture | confirmed |
| M-005 | `templates/review-package.md` | no-change-verified | F-002, F-009 | Artifact structural contract, including the Category column that carries the review lens | confirmed |
| M-006 | `registry/templates.yaml`, record `review-package` | no-change-verified | F-009, F-010 | Artifact-type identity record. The schema declares no emitting-phase field, and its description states service scope, not routing; changing it to name emitters would create the second declaration site `C-004` forbids | confirmed |
| M-007 | `omn-dev-2-reviewer` agent contract, host-registered at `agents/omn-dev-2-reviewer.agent.md` | no-change-verified | F-006, A-002 | Owning-agent `outputs` declaration, which `F-004` resolves a declared artifact against | speculative |
| M-008 | `agents/architect/manifest.yaml`, `outputs` block | no-change-verified | F-017, F-018, F-019 | Architect output contract. A reader would expect it to change, because `F-011` names the owning agents' manifest outputs as part of the remaining work; it does not, because `O-002` is rejected | confirmed |
| M-009 | `workflows/implement-feature.md` Phase Model table, `quality-review` row | no-change-verified | F-021, F-024 | Output Artifact declaration. A reader would expect it to change, because `F-011` names its prose output as one of the four; it does not, because `C-001` permits one phase and `F-021` places the file inside committed run evidence | confirmed |
| M-010 | `runtime/README.md`, known gap 7 | operational-impact | F-011, F-021, A-006 | The recorded gap register, which is also a member of this run's own frozen context slice | confirmed |
| M-011 | `workflows/workflow-gate-matrix.md`, review-pull-request rows | no-change-verified | F-023 | Gate ownership. The review-pull-request gate that closes `code-quality-review` already exists and `C-009` holds its ownership unchanged | confirmed |
| M-012 | `runtime/verify_registry_coverage.py` per-phase dispatchability report | no-change-verified | F-013, A-004, A-005 | Blocked-phase count and per-phase blocked reason | speculative |

Boundary crossings recorded. The change crosses two boundaries, and both are where its risk
concentrates. First, the workflow-specification boundary to the agent-manifest boundary:
`F-004` resolves a phase's declared artifact against the owning agent's manifest outputs, so a
declaration in `M-001` is only half of a resolvable output contract, and the other half lives
in `M-007`. Second, the workflow-specification boundary to the runtime-validator boundary: the
same resolution consults the `VALIDATORS` map in `M-003`, which `F-002` establishes already
carries the artifact type. The change adds the phase-side token and crosses no other boundary.

### 5.2 Options Considered

| Option | Structural change | C-001 | C-003 | C-004 | C-006 | C-007 | Impact surface | Reuse leverage | Migration burden | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | `review-pull-request/code-quality-review` declares `review-package.md` as its Output Artifact | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | 1 | 8 | 1 | Selected |
| O-002 | `review-pull-request/structural-compliance` declares `review-package.md` as its Output Artifact | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | 1 | 7 | 2 | Not selected |
| O-003 | All four phases the artifact type's registry description names declare it | Violated | Satisfied | Satisfied | Violated | Violated | 3 | 8 | 3 | Eliminated on C-001, and additionally on C-006 and C-007 |
| O-004 | `implement-feature/quality-review` declares `review-package.md` as its Output Artifact | Satisfied | Satisfied | Satisfied | Violated | Violated | 1 | 8 | 2 | Eliminated on C-006 and C-007 |
| O-005 | Routing is declared by a new machine-read emitting-phase field on the `review-package` record in `registry/templates.yaml`, leaving every Phase Model unchanged | Satisfied | Satisfied | Violated | Satisfied | Satisfied | 1 | 4 | 2 | Eliminated on C-004 |

Impact surface counts modules in 5.1 carrying `contract-change` or `dependency-change` under
that option. Reuse leverage counts the capabilities in section 7 satisfied by `reuse-as-is` or
`reuse-extended` under that option, out of eight. Migration burden counts the contract-affecting
changes that option requires a transition strategy for, including deferred ones.

`O-003` is eliminated on `C-001`, which permits one phase. It is additionally eliminated on
`C-006` and `C-007`, because it edits `workflows/implement-feature.md`, which `F-021`
establishes is a member of this run's frozen context slice.

`O-004` is eliminated on `C-006` and `C-007` for the same reason: `F-021` places
`workflows/implement-feature.md` inside committed run evidence, so editing it changes what the
verification of every committed implement-feature run reproduces (`A-006`).

`O-005` is eliminated on `C-004`. It would make `registry/templates.yaml` a second place where
artifact routing is declared, alongside the Phase Model column that `F-003` and `F-004` already
read, and `F-010` establishes the record schema carries no such field today.

### 5.3 Selected Approach

- Selected: `O-001`. The supplied intent leaves which review phase is the correct emitter, and
  on what ground, open to the design (`S-016`); this subsection decides both, and `D-001`
  records the decision.
- Structural change: the Output Artifact cell of the `code-quality-review` row in
  `workflows/review-pull-request.md` names `review-package.md` in place of its prose token. No
  other cell in that table changes unless `P-004` finds a non-adjacent Input dependency on the
  replaced token, in which case that Input entry names `review-package.md`. Nothing else in the
  framework changes, because `F-002` establishes the artifact type is already contracted and
  decidable, `F-004` establishes the resolution mechanism already covers it, and `C-009` holds
  gate ownership out.
- Rationale: re-derived from 5.2 in criterion order. `O-003`, `O-004`, and `O-005` are
  eliminated on hard constraints. `O-001` and `O-002` both satisfy every hard constraint and tie
  on impact surface at one module, so the selection is decided at the third criterion, reuse
  leverage. `O-001` scores eight of eight and `O-002` scores seven, because the capability "an
  owning agent whose declared work the artifact describes and whose contract permits producing
  it" has a reusable candidate under `O-001` and none under `O-002`. `F-016` rates
  `omn-dev-2-reviewer` Primary for Code Review and Governance, and `F-009` records that the
  artifact type declares exactly the capabilities `code-review` and `governance-enforcement`
  that column names. `F-017` records that the `architect` capability set holds neither, and
  `F-018` records that the architect contract places reviewing pull requests and assessing
  concrete diffs out of scope while assigning verification of a concrete change to
  `omn-dev-2-reviewer`. So the phase whose declared work the artifact already describes, in the
  sense `C-002` requires, is the one whose owning role holds the artifact's own registered
  capabilities.
- Highest-scoring rejected alternative and why it lost: `O-002`, declaring the artifact at
  `review-pull-request/structural-compliance`. It is the option the framework's own record
  points at, because `F-005` and `F-011` name that phase as the one blocked for want of a
  contract reconciliation, and closing a defect where it was recorded is a genuine benefit. It
  lost on reuse leverage and on migration burden. Under `O-002` the declaration would resolve no
  output contract, because `F-004` resolves against the owning agent's manifest outputs and
  `F-019` establishes the architect manifest declares only `technical-design` and
  `architecture-decision-record`. Supplying that half is reserved by `C-003` as a decision to
  surface, and it would not be additive, because `F-018` places the production of a review
  verdict outside the architect contract's scope, so the manifest change would carry a
  role-boundary reconciliation with it. `O-002` therefore leaves either a declaration that
  resolves nothing or a contract change that `C-003` forbids making silently. `D-002` records
  the rejection and its ground, and `Q-004` routes the reconciliation of that phase to its
  owners rather than leaving it to be inferred.
- Tradeoffs accepted:
  - `C-001` permits one phase, so three review-producing phases keep prose Output Artifact
    entries after this change, and `F-011`'s statement of the remaining work is only partly
    discharged. That is the product's constraint, not a structural finding, and `F-012`
    establishes the framework already routes one artifact type from two phases without
    ambiguity, so extending routing to the remaining three is structurally available. `Q-001`
    routes that to `omn-product-owner` and `R-010` carries the consequence.
  - `O-001` declares the artifact against a phase whose owner holds no registry record
    (`F-006`), so the declaration cannot be exercised by a run. `C-010` accepts that, `A-004`
    and `R-004` carry the blocked-reason consequence, and `C-012` is satisfied at declaration
    level only until capability registration happens.
  - `O-002`'s benefit is forgone, so `review-pull-request/structural-compliance` remains blocked
    with `workflow-contract-violation` after this change. `R-008` records that plainly, so no
    reader concludes gap 7's named blocker was cleared.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Route the review package by declaring `review-package.md` as the Output Artifact of exactly one phase, `review-pull-request/code-quality-review`, selecting `O-001` | Yes | ADR D-001, status Proposed |
| D-002 | Reject `architect` as the emitter and defer the owning-agent `outputs` declaration to the registration of `omn-dev-2-reviewer`, surfacing it rather than making it, which follows from `O-001` | Yes | ADR D-002, status Proposed |
| D-003 | The Phase Model Output Artifact column is the sole authority for artifact routing; the artifact-type record in `registry/templates.yaml` declares identity and service scope, not routing, which `O-005` would have reversed | Yes | ADR D-003, status Proposed |
| D-004 | Leave every Input column in `workflows/review-pull-request.md` unchanged under `O-001`, unless `P-004` identifies a non-adjacent Input entry naming the replaced token | No | Inline; follows from `F-015` and `A-003` and changes no contract by itself |
| D-005 | The routed phase's Output Artifact cell carries exactly one artifact token under `O-001`; the prose token is replaced rather than supplemented | No | Inline; follows from `F-004` requiring an unambiguous declared artifact and from `C-001` |
| D-006 | The gap-record update in `M-010` is sequenced after the declaration `O-001` makes, and carries the re-verification obligation of `C-006` | No | Inline; applies `C-006` and `A-006` to a file `F-021` places inside a frozen slice |

## API and Data Model Impact

- API changes: `M-001` is the only contract-change module, and the contract it changes is the
  machine-read declaration in one Phase Model cell. No programmatic interface, endpoint, or
  message shape changes anywhere in the framework.
- Contract compatibility notes: for `M-001` under `D-001` and `D-005`.
  - Current shape: the `code-quality-review` row's Output Artifact cell carries a prose
    deliverable description, recorded by `F-011` as "quality findings with correction requests",
    consistent with `F-001` that no cell in that table names a file. Under `F-004` this resolves
    no file contract.
  - Target shape: the same cell names exactly one artifact token, `review-package.md`. Under
    `F-003` the token is then counted as a routed artifact type, and under `F-004` it resolves
    against the `VALIDATORS` map, which `F-002` establishes already carries it.
  - Compatibility approach: replacement of one cell, not supplementation. Two tokens in one cell
    would leave the phase's declared artifact ambiguous to `F-004`'s resolution, and `C-001` and
    `S-010` require one declared review output form. Every Input column in the same table is
    left unchanged, so under `F-015` every edge in that workflow remains the row-order edge it
    is today, which `F-001` and `A-003` establish. The one exception is a non-adjacent Input
    entry naming the replaced token, which `P-004` identifies and `P-005` re-points.
  - Coexistence period: none. The prose token and the artifact token cannot both stand in one
    cell without making the declared artifact ambiguous, so there is no interval in which both
    forms are declared and no retirement condition to record.
  - Rollback position: restore the prose token in that one cell. Under `F-003` the coverage
    proof then stops counting `review-package.md` as routed and returns to its current result;
    under `F-015` the edge set is unchanged either way; and no run evidence is affected, because
    `F-022` establishes the file is absent from this run's slice and `A-001` from every
    committed slice. If `P-006` has already edited `M-010`, that record is reverted alongside
    and the affected runs are re-verified again.
- Schema or migration changes: None identified. The change alters one declaration cell in a
  specification file. No persisted schema, stored record, or data model is touched, so there is
  no migration direction, no reversibility question, and no reader or writer behaviour during
  transition to state.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| A contracted structure for a review verdict artifact | `templates/review-package.md` | reuse-as-is | `F-002` establishes it is registered and passes its fixture, and `F-009` establishes the Category column already carries the review lens, so a code-review lens needs no template change |
| A mechanism that decides the artifact's conformance | `runtime/review_package_validator.py` | reuse-as-is | `F-002` establishes it sits in the `VALIDATORS` map and rejects a declared mutation by the named check `P3`; the change adds no conformance rule |
| A single-authority declaration of which phase emits which artifact | The Output Artifact column of the `## Phase Model` table | reuse-as-is | `F-003` and `F-004` both read that column, so it is already the routing authority; `D-003` records that it stays the only one |
| Artifact-type identity registration | The `review-package` record in `registry/templates.yaml` | reuse-as-is | `F-009` establishes the record is active and complete; `F-010` establishes it declares no emitting phase, so it needs no change to support routing |
| Derivation of phase sequencing from declared artifacts | The runtime's Input and Output Artifact edge rules | reuse-as-is | `F-015` states the three rules; the change is designed so all three produce the same edge set before and after |
| An owning agent whose declared work the artifact describes and whose contract permits producing it | `omn-dev-2-reviewer` | reuse-as-is | `F-016` rates it Primary for Code Review and Governance, and `F-009` establishes the artifact type declares exactly those capabilities; `F-006` establishes it owns `code-quality-review` |
| The same capability, considered against the only registered agent owning a review-pull-request phase | `architect` | rejected | `F-017` establishes its capability set holds neither `code-review` nor `governance-enforcement`, and `F-018` places reviewing pull requests and assessing concrete diffs outside its contract while assigning verification of a concrete change to `omn-dev-2-reviewer`. Declaring a review verdict as an architect output would contradict the architect's own contract, so the component is unsuitable for this capability |
| A coverage proof that a contracted artifact type is routed | `runtime/verify_validators.py` check `V1` | reuse-as-is | `F-003` establishes `V1` already reads the Output Artifact column and asserts a validator exists for every routed token; the declaration supplies the token it was waiting for |

Every capability the selected approach requires appears above, and no new structure is proposed
by this design. The one `rejected` row licenses nothing new; it records why the only registered
candidate for that capability is unsuitable, so that a downstream reader does not re-propose it.

## Operational Considerations

- Logging and observability updates: `M-002` and `M-012` are the observability surfaces this
  change moves. `F-003` establishes that `V1`'s routed-artifact set gains one token, so its
  reported coverage changes, while `F-013` and `A-005` say the blocked-phase count reported by
  `M-012` does not. Both must be captured as a before-state and compared after, which `P-008`
  requires, because `C-007` is only decidable against a recorded before-state.
- Error handling strategy: `F-005` records `workflow-contract-violation` as the class
  `review-pull-request/structural-compliance` blocks with, and the framework treats that class
  as non-retryable with a rollback action. The design keeps `code-quality-review` failing at the
  earlier link of the `F-014` chain, the missing agent registry record of `F-006`, rather than
  at contract resolution, which is what `A-004` asserts and `R-004` covers. `C-005` forbids
  trading one blocked reason for another silently, so `P-008` compares the per-phase reason and
  not only the count.
- Security considerations: the artifact this change routes carries findings, correction
  requests, and a verdict (`F-009`), so once the routed phase is dispatchable, review content
  becomes durable run evidence rather than transient prose. Under `C-010` and `F-006` no run
  reaches that phase as a result of this change, so nothing restricted becomes durable now.
  Whether the artifact type may carry restricted content is unresolved and is `Q-005`, owned by
  `omn-dev-2-reviewer`, with `R-009` carrying the risk. `C-009` keeps gate ownership unchanged,
  so no approval authority moves as a side effect of the routing. Compliance impact is limited
  to that evidence-retention question, because the change alters one declaration cell and moves
  no data.
- Performance considerations: no performance constraint and no performance quality attribute is
  recorded for this change, and `C-001` through `C-012` contain none. `F-004` establishes that
  the declared artifact is resolved through a path the runtime already executes for every routed
  phase, so the change adds one token to an existing resolution rather than a new one. No
  performance expectation is asserted beyond that.
- Deployment and operability impact: the change is a specification edit, applied by the
  implementation owner rather than by this agent. Its operability cost is entirely in `C-006`,
  because `F-021` places `runtime/README.md` inside this run's own frozen context slice and
  `A-006` makes editing it change what committed-run verification reproduces. `P-006` and
  `D-006` sequence that obligation, and `R-006` carries the risk that the change invalidates the
  evidence produced for the change.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The emitting phase, and the disposition of the prose token it replaces, are approved and recorded before any declaration is made | M-001 | none | `F-004` resolves a declared artifact against its owning agent, so declaring against the wrong owner produces the non-retryable class `F-005` records rather than a routed artifact | T-001, T-010 |
| P-002 | The artifact type's structural contract and its conformance mechanism are confirmed to exist, by path, before the declaration is made | M-004, M-005, M-006 | none | `C-005` requires a declared artifact the Validation Engine can decide; declaring one it cannot would make the phase undispatchable for a new reason | T-005 |
| P-003 | The condition under which a declared Output Artifact becomes validated run evidence is recorded, and the part of that condition the declaration alone does not satisfy is named as a distinct outcome | M-001, M-003 | P-002 | `F-004` and `F-014` together make the declaration necessary and not sufficient; leaving sufficiency assumed would let the change be accepted on an outcome it does not deliver | T-008 |
| P-004 | The before-state and after-state edge sets of `workflows/review-pull-request.md` are recorded, and every Input entry naming the token to be replaced is listed with the replacement it requires | M-001 | P-001 | `C-008` makes the Input and Output columns the runtime's sequencing source, and `F-022` puts the current Input columns outside the confirmed fact set, so the after-state cannot be verified against an unrecorded before-state | T-002 |
| P-005 | The Output Artifact cell of the approved phase names exactly one artifact token, and no Input column in that table changes except an entry `P-004` identified as naming the replaced token from a non-adjacent phase | M-001 | P-003, P-004 | `F-004` requires an unambiguous declared artifact, and `F-015` preserves the edge set only while no Input column is left naming a token no phase emits | T-003 |
| P-006 | The recorded gap is closed only after every run whose frozen context slice contains the record has been re-verified or had its evidence closed | M-010 | P-005 | `C-006` and `F-021` place `runtime/README.md` inside a committed frozen slice, and `A-006` makes editing it change what those runs' verification reproduces, so the record must not be edited before the evidence it belongs to is settled | T-009 |
| P-007 | The routed declaration and the artifact-type record are confirmed to declare routing in exactly one place | M-001, M-006 | P-005 | `C-004` forbids a second declaration site, and an alignment performed on the registry side would create one, because `F-010` shows the record schema has no field for it | T-006 |
| P-008 | The coverage proofs are re-run and the routed-artifact result, the blocked-phase count, and the per-phase blocked reasons are compared against the before-state recorded at `P-004` and `P-002` | M-002, M-012 | P-005, P-007 | `C-007` requires unresolved counts unchanged or lower and `C-005` requires a traded blocked reason to be surfaced, and neither is decidable without the comparison | T-004, T-007 |

These are structural constraints, not tasks. The planner owns the executable breakdown, and the
`Binds` column names the supplied planner tasks each constraint binds, so the planner can
reconcile without re-deriving. Every supplied task `T-001` through `T-010` is bound by exactly
one constraint above.

### Test Strategy Focus Areas

- The derived edge set of `workflows/review-pull-request.md` before and after the declaration,
  compared against the after-state recorded at `P-004`, with every difference dispositioned.
- The routed-artifact coverage result of `V1`, proving `review-package.md` is counted as routed
  and that a validator is present for it.
- The per-phase blocked reason for `code-quality-review` before and after, proving no reason was
  traded (`C-005`, `A-004`).
- The blocked-phase count before and after, proving it is unchanged or lower (`C-007`, `A-005`).
- A conforming and a non-conforming review package against `review_package_validator.py`, and
  the expected run outcome when the approved phase records no package because it blocks at
  capability resolution (`F-006`, `F-014`).
- Re-verification of every committed run whose frozen context slice contains a file this change
  edits, which is at minimum `runtime/README.md` (`F-021`) and, if `A-001` is false, also
  `workflows/review-pull-request.md`.

### Rollout and Rollback

- Rollout: `P-001` through `P-008` in order. `P-005` is the only step that changes a machine-read
  contract, and it changes one cell. `P-006` is gated on the re-verification obligation of
  `C-006` rather than on the declaration alone, because it touches a frozen-slice member.
- Rollback: restore the prose token in the one cell, which returns `M-001` to its current
  declaration, `M-002` to its current reported coverage, and `M-012` to its current per-phase
  reason, with no run evidence affected under `F-022` and `A-001`. If `P-006` has already been
  performed, the record edit is reverted with it and the affected runs are re-verified again.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | contract | `A-003` is false: an Input entry in `workflows/review-pull-request.md` names the prose token the declaration replaces, from a phase other than the immediately following row | The derived edge set changes, and the after-state the change is verified against is wrong | medium | M-001, P-004 | `P-004` records the before-state edge set and every dangling Input entry before `P-005` makes the edit, and `P-005` re-points any entry it finds | omn-tech-lead |
| R-002 | migration | `A-001` is false: a committed run's frozen context slice contains `workflows/review-pull-request.md` | `C-006` attaches a re-verification obligation the sequencing did not carry, and `C-007` may fail | low | M-001, P-005 | `Q-002` confirms `A-001` before `P-005`; if false, `P-005` gains the same prerequisite `P-006` carries | omn-tech-lead |
| R-003 | structural | `A-002` is false: `omn-dev-2-reviewer` ships a manifest whose `outputs` do not declare the review package | `C-003` engages, because the declaration then requires an agent contract change this change may not make | medium | M-007, D-002 | `D-002` surfaces the owning-agent output declaration as a proposed decision rather than performing it, and `Q-003` confirms `A-002` before `P-005` | omn-tech-lead |
| R-004 | delivery | `A-004` is false: the blocked reason recorded for `code-quality-review` changes after the declaration | `C-005` requires the trade to be surfaced, and the change needs re-approval before acceptance | low | M-012, P-008 | `P-008` compares the per-phase reason against the recorded before-state rather than assuming it | omn-qa |
| R-005 | delivery | `A-005` is false: the blocked-phase count rises after the declaration | `C-007` fails and the change is rejected at the Verification Gate | low | M-012, P-008 | `P-008` compares the count against the recorded before-state | omn-qa |
| R-006 | migration | `P-006` edits `runtime/README.md`, which `F-021` places inside this run's own frozen context slice, while `A-006` holds | This run's committed evidence no longer reproduces, so the change invalidates the evidence produced for the change | medium | M-010, P-006 | `P-006` is sequenced after `P-005` and requires the affected runs to be re-verified or their evidence closed before the record is edited | omn-tech-lead |
| R-007 | structural | The artifact-type registry record's description continues to name four emitting phases while one phase declares the artifact | A reader treats the registry description as a routing declaration, creating the second authority `C-004` forbids | medium | M-006, D-003 | `D-003` records that the Phase Model is the sole routing authority and the record declares identity and service scope, and `P-007` confirms one declaration site | omn-tech-lead |
| R-008 | contract | `review-pull-request/structural-compliance` remains blocked with `workflow-contract-violation` after this change, because its declared artifact is still prose and `F-018` places producing a review verdict outside its owner's contract | Gap 7's named blocker is not closed by this change, and a reader may believe routing the artifact type closed it | high | M-008, D-002 | `D-002` records the rejection of `architect` as emitter with its ground, and `Q-004` routes reconciliation of that phase to its owners as work outside this change | omn-tech-lead |
| R-009 | security | Once the routed phase becomes dispatchable, a review package quotes restricted change content into durable run evidence | Restricted content becomes durable evidence rather than transient review prose | low | M-001, P-002 | `C-010` keeps the phase non-executable under this change, and `Q-005` establishes whether the artifact type may carry restricted content before the phase becomes dispatchable | omn-dev-2-reviewer |
| R-010 | delivery | `C-001` permits one phase, so three review-producing phases keep prose Output Artifact entries after the change | `F-011`'s statement of the remaining work is only partly discharged, and the review lifecycle still carries more than one review output form | medium | M-009, D-001 | `Q-001` routes the scope of the remaining three phases to `omn-product-owner` as follow-on work, citing `F-012` that the framework already routes one artifact type from two phases | omn-product-owner |

## Estimate and Confidence

- Overall: `S` (confidence: low). The change is bounded within one boundary and uses a
  declaration mechanism `F-004` and `F-015` already define. Confidence is `low` rather than
  `medium` because two impacted modules are recorded at speculative confidence and the estimate
  rests on six unconfirmed assumptions.
- Breakdown:
  - `P-001`, `P-002`, `P-003`: `XS` each. Approvals and confirmations against records that
    `F-002`, `F-009`, and `F-010` establish already exist.
  - `P-004`: `S`. It requires the before-state of a file that `F-022` places outside this run's
    frozen context slice, so it reads new material rather than confirming known material.
  - `P-005`: `XS`. One cell in one table, with at most one Input entry re-pointed.
  - `P-006`: `S`. The edit itself is trivial; the re-verification obligation `C-006` attaches to
    it is not.
  - `P-007`: `XS`. A confirmation that one declaration site exists.
  - `P-008`: `S`. Two coverage proofs and a three-way before-and-after comparison.
- Scope assumptions:
  - The estimate covers `P-001` through `P-008` and assumes `A-001` through `A-006` hold.
  - It excludes registering `omn-dev-2-reviewer` and declaring the artifact in any owning
    agent's manifest `outputs`.
  - It excludes making any phase dispatchable and changing `templates/review-package.md`.
  - It excludes reconciling `review-pull-request/structural-compliance` and routing the artifact
    to the three remaining review-producing phases.
- Uncertainty drivers: `F-022` puts the Input columns of the file being changed outside the
  confirmed fact set, so the edge-set before-state rests on `A-003` and `R-001` rather than on a
  fact. `A-002` leaves the existence of an owning-agent manifest unconfirmed, which is what
  decides whether `C-003` engages. `A-004` and `A-005` leave the reported blocked reason and
  count unconfirmed, which is what decides whether `C-005` and `C-007` hold. Each is confirmable
  by a named owner ahead of `P-005`, and none is confirmed by this design.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does "the review lifecycle" mean exactly one phase, given that `F-012` establishes the framework already routes `technical-design.md` from two phases and `investigation-report.md` from two without ambiguity? | No | omn-product-owner | D-001, M-009, R-010 | If one phase stands, this change routes the artifact type and three review-producing phases keep prose outputs. If several are permitted, `C-001` is relaxed, the remaining three enter scope as follow-on work, and `O-003` becomes viable for every phase outside a frozen context slice |
| Q-002 | Does any committed run's frozen context slice contain `workflows/review-pull-request.md` (`A-001`)? | No | omn-tech-lead | P-005, R-002 | If none does, the declaration carries no re-verification obligation. If one does, `C-006` attaches one and `P-005` gains the prerequisite `P-006` already carries |
| Q-003 | Does `omn-dev-2-reviewer` ship an agent manifest with an `outputs` block (`A-002`)? | No | omn-tech-lead | M-007, D-002, R-003 | If it does not, the owning-agent output declaration is authored at registration and no agent contract changes now. If it does, `C-003` engages and the declaration must be surfaced and decided before `P-005` |
| Q-004 | What reconciles `review-pull-request/structural-compliance`, whose declared artifact is prose (`F-005`) and whose owner's contract places producing a review verdict out of scope (`F-018`)? | No | omn-tech-lead | M-008, D-002, R-008 | If that phase's declared work is expectation-setting, its Output Artifact is a design artifact and not a review package, and gap 7's phrasing of the remaining work is wrong for that phase. If it is verdict-issuing, the phase owner is wrong and `C-002` is engaged. Either answer is outside this change and neither may be decided by this agent |
| Q-005 | May a review package carry restricted change content once the routed phase becomes dispatchable? | No | omn-dev-2-reviewer | P-002, R-009 | If it may not, a content constraint enters the artifact contract before the phase executes. If it may, durable run evidence carries it and access control becomes an operability concern for the run store |
| Q-006 | Is the Phase Model Output Artifact column accepted as the sole routing authority, so the artifact-type registry record is not aligned to the emitting phase set (`D-003`, `C-004`, `F-010`)? | No | omn-tech-lead | M-006, D-003, R-007 | If accepted, the alignment `P-007` performs is a confirmation that one declaration site exists. If not, a routing field on `registry/templates.yaml` is required, which `C-004` forbids and which would need an explicit constraint relaxation |
| Q-007 | The registered design validator extracts a gate name as one capitalised word followed by the word Gate, so it cannot represent the three-word gate name `workflows/workflow-gate-matrix.md` carries for the review-pull-request assessment phases, and a design that names that gate exactly fails a Blocking check. Is the extraction widened, or is the matrix name shortened? | No | omn-tech-lead | M-011 | If the extraction is widened, a design may name that gate exactly. If the matrix name is shortened, `C-009` is engaged because gate naming is out of scope for this change. Until either happens, a design must refer to that gate by the phase it closes, which is what this package does. Recorded as a framework gap found during self-verification, not as a design dependency |

`Q-001` is an `E-AUTHORITY` event, because whether the change routes the artifact to one phase
or to several is a product-scope decision, and this design applies `C-001` as supplied rather
than deciding it. `Q-004` is likewise an `E-AUTHORITY` event, because reconciling an agent's
declared outputs with a phase it owns belongs to the agent and workflow owners.

Decision records `D-001`, `D-002`, and `D-003` remain at status `Proposed` and require Design
Gate acceptance before `P-005` begins. No open decision above is blocking, so this package is
`complete` rather than `blocked`.

## Sign-off

- Architect: architect, the producing role, excluded from accepting this package
- Tech Lead: omn-tech-lead, the accepting owner for the Design Gate
- QA: omn-qa, for the verification implications at `P-008`
- Product Owner: omn-product-owner, for product confirmation of `Q-001` only

Design Gate owners come from `workflows/workflow-gate-matrix.md` and are `omn-architect` and
`omn-tech-lead`. Under the Producer Exclusion Rule in that matrix, which reads through role
aliases, `architect` produced this package and the `omn-architect` entry names the same role, so
acceptance rests with `omn-tech-lead`. Lines are left unsigned by the producing agent.

This agent performed analysis and design only. No production code, test, migration, script, or
configuration was written; no specification file was edited; no external system, repository, or
ticketing tool was accessed; and every fact above cites supplied context or a member of the
frozen context slice recorded in this run's invocation envelope.
