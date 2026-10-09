```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0001
  featureName: Per-phase model tier in the dispatch envelope
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/model-tier-feature-request.md
    - type: change-request
      reference: runs/inputs/model-tier-change-request.md
    - type: business-intent
      reference: runs/inputs/model-tier-business-intent.md
    - type: architecture-context
      reference: runs/inputs/model-tier-architecture-context.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 21
  inputDigest: sha256:1a5d5bd8ac684410b76f88bce2701855
  contextDigest: sha256:6a1ac11b59924eceec1c6184befe245a
```

## Metadata

- Feature name: Per-phase model tier in the dispatch envelope
- Requested by: The operator who supplied the feature request, change request, business intent, and architecture context (individual not named in the inputs)
- Business goal: Make the cost of a delivery run proportional to the difficulty of each phase, without weakening any gate, validator, or acceptance rule
- Target outcome: Each phase is dispatched at a declared tier, a failed cheaper attempt is promoted rather than repeated, and the share of non-deep work is visible in the run's own metrics
- Scope decision date: 2026-10-08

## Business Context

- Problem statement: Every phase of a delivery run is executed by whatever model the operator's session uses, so read-and-summarise phases cost as much as phases needing depth, and the operator has no lever short of changing the whole session
- Value hypothesis: Routing light phases to a cheaper class of model and promoting on failure lowers the cost per run while the mechanical gates and validators keep correctness unchanged
- Affected users: Operators running delivery workflows; gate owners and downstream phase agents who consume phase outputs
- Success measure: A measurable share of a representative implement-feature run's invocations is dispatched at a non-deep tier, reported by the run's own metrics; every verifier stays at its recorded baseline; no rejected cheaper attempt is retried at the same tier (`Q-001` records that no minimum share is stated)

## In Scope

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | Every dispatchable phase has exactly one declared tier (light, standard, or deep), and each tier maps to one host model hint, all in a single authoritative declaration outside agent text | Feature request, Expected outcome bullet 1; architecture context on tier data living outside workflow tables | must-have |
| `S-002` | Every dispatch envelope carries an additive model tier record stating the resolved tier, the host model hint, and the basis for the choice | Feature request, Expected outcome bullet 2; architecture context on additive fields | must-have |
| `S-003` | A phase whose prior attempt was rejected by its validator, or whose gate was rejected and rolled back, is dispatched one tier higher, the envelope records the escalation and its reason, and deep never escalates further | Feature request, Expected outcome bullet 3; business intent success bullet 3 | must-have |
| `S-004` | A phase with no declaration resolves to inheriting the host model, and no existing run, replay, or verifier changes outcome | Feature request, Expected outcome bullet 4; business intent success bullet 2 | must-have |
| `S-005` | The run's execution metrics report invocations and estimated context bytes by tier | Feature request, Expected outcome bullet 5; business intent success bullet 1 | must-have |
| `S-006` | The framework's own verification detects a dispatchable phase with no declared tier and detects an escalation that is not monotonic | Change request, Surfaces row on verifiers; feature request, "readable by the runtime and verifiable" (`D-001`) | must-have |
| `S-007` | The framework's distributed copy carries the same tier behaviour as the authoritative copy | Change request, Surfaces row on the bundled payload mirror (`D-003`) | should-have |
| `S-008` | The envelope field and the escalation rule are documented in the runtime governance documentation | Change request, Surfaces row on execution-engine and runtime documentation | should-have |
| `S-009` | The runtime version increments to identify the release that carries tiering | Change request, Surfaces row on the runtime (`RUNTIME_VERSION` increments) | should-have |

## Out of Scope

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Running phases concurrently | Feature request and business intent both name it a separate later change | A separate change request for parallel phase execution is supplied |
| `X-002` | Choosing vendors or model identifiers inside runtime logic, any model call by the runtime, and any vendor SDK dependency | Business intent non-goal; architecture context that the runtime only names a tier and the host chooses | A supplied input asks the runtime itself to invoke a model |
| `X-003` | Changes to agent module text, workflow Phase Model tables, the gate matrix, validators, templates, or artifact contracts | Change request "Not touched"; feature request "Additive only" | A supplied input names one of these as a deliverable |
| `X-004` | Changing which phases exist, who owns them, or what they must produce | Business intent non-goal | A supplied input requests a change to a workflow's phase set |
| `X-005` | Editing the agent entrypoint model declarations, which stay as they are | Architecture context: the host override makes the hint effective while entrypoint declarations stay unchanged | The host stops accepting a per-dispatch override |
| `X-006` | Lowering a phase's tier after success or on any signal other than a recorded rejection | Inputs specify promotion only; demotion is not requested (`D-002`) | A supplied input requests demotion or adaptive tiering |

## Acceptance Criteria

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | 100 percent of dispatchable phases across the active workflows resolve to exactly one tier from light, standard, deep; zero phases are uncovered | `S-001` | Framework verifier run reports zero uncovered dispatchable phases | must-have |
| `A-002` | The phases the request names as light (scope definition, technical discovery, documentation hand-off, artifact packaging, repository scan) resolve to light, and those it names as deep (solution design, root-cause analysis, implementation, quality review) resolve to deep | `S-001` | Review of the declaration against the request's named lists | must-have |
| `A-003` | Each of the three tiers maps to exactly one host model hint, and tier assignment is stated in exactly one authoritative location | `S-001` | Review of the declaration and a search of the framework for any second tier assignment | must-have |
| `A-004` | Zero tier assignments appear in agent module text | `S-001` | Text search of the agent module files returns zero matches | must-have |
| `A-005` | Every dispatched envelope of an implement-feature run carries a model tier record with non-empty tier, host model hint, and basis | `S-002` | Inspection of every envelope produced by dispatching all phases of one run | must-have |
| `A-006` | The original envelope fields are present and unchanged in name and value compared with the same run state before this change | `S-002` | Field-by-field comparison of an envelope against a pre-change envelope for the same run state | must-have |
| `A-007` | The change adds zero model invocations and zero vendor SDK dependencies | `S-002` | Review of the change set and the dependency declarations | must-have |
| `A-008` | After a validator rejection at attempt N of a light or standard phase, attempt N+1 resolves exactly one tier higher and its envelope states escalated with a reason naming the rejection | `S-003` | Dispatch of a phase after a recorded validator rejection, with envelope inspection | must-have |
| `A-009` | After a gate rejection and rollback of a light or standard phase, the next attempt resolves exactly one tier higher and its envelope states escalated with a reason naming the gate rejection | `S-003` | Dispatch of a phase after a recorded gate rejection and rollback, with envelope inspection | must-have |
| `A-010` | A deep phase after any rejection stays at deep, and its envelope does not record a tier above deep | `S-003` | Dispatch of a deep phase after a recorded rejection, with envelope inspection | must-have |
| `A-011` | Zero rejected light or standard attempts are retried at the same tier | `S-003` | Review of the attempt and tier history of a run containing rejections | must-have |
| `A-012` | The tier resolved after a rejection is identical whether dispatch happens in the same session or a fresh one reading only recorded run state | `S-003` | Comparison of two dispatches of the same phase, one in-session and one from recorded state alone | must-have |
| `A-013` | A phase with no declaration resolves to inheriting the host model and its envelope records no escalation unless a rejection is recorded | `S-004` | Dispatch of a phase absent from the declaration, with envelope inspection | must-have |
| `A-014` | Every existing framework verifier, including the replay stability check, returns the same result as its recorded baseline | `S-004` | Run of all verifiers compared with the recorded baseline results | must-have |
| `A-015` | The execution metrics list invocations and estimated context bytes for each tier, and the per-tier values sum to the run totals | `S-005` | Comparison of the per-tier figures with the run totals for a completed run | must-have |
| `A-016` | The execution metrics state the share of invocations at a non-deep tier as a figure, and for an implement-feature run that figure is greater than zero | `S-005` | Reading the execution metrics of a completed implement-feature run | must-have |
| `A-017` | The verifier returns failure when one dispatchable phase is removed from the declaration | `S-006` | Verifier run against a declaration with one phase removed | must-have |
| `A-018` | The verifier returns failure when an escalation resolves to the same or a lower tier than the prior attempt | `S-006` | Verifier run against an escalation record that does not rise | must-have |
| `A-019` | The distributed copy differs from the authoritative copy in zero files | `S-007` | Run of the payload synchronisation check reports zero differences | should-have |
| `A-020` | The runtime governance documentation states the envelope field, its three parts, the escalation rule, and the deep ceiling, and the runtime README is not enlarged | `S-008` | Review of the documentation against that four-item list and of the README size before and after | should-have |
| `A-021` | The runtime version value after the change is greater than the value before it | `S-009` | Comparison of the version value before and after | should-have |

## Constraints and Dependencies

- Business constraints: Cost must fall without weakening any gate, validator, or acceptance rule; a phase's tier is advice and correctness is still decided mechanically
- Regulatory or policy constraints: Additive only, so the original envelope fields, Phase Model tables, gates, validators, artifact contracts, and agent module text are unchanged; no column is added to machine-parsed workflow tables; tier assignment is configuration and is not duplicated into agent modules; loading policy stays in runtime and configuration; new documentation goes in runtime governance documentation, not the runtime README; any new field must be deterministic from run state so replay stays stable; escalation derives from recorded rejection state, not in-memory state
- Delivery constraints: The authoritative framework tree is edited first and the distributed copy is refreshed by the synchronisation command, never by hand; the run's affected area is performance (term "profile" in the change request); every verifier must stay at its recorded baseline
- External dependencies: The host must accept a per-dispatch model override for a tier hint to take effect (architecture context); this framework does not control that capability

## Scope Decisions

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | Verification of declaration coverage and escalation monotonicity is in scope as `S-006` | The feature request requires the declaration to be verifiable, and a tier that cannot be checked could silently leave a phase undeclared | Delivery includes a framework-level check, not only runtime behaviour | omn-product-owner |
| `D-002` | Escalation is promotion-only; lowering a tier is excluded as `X-006` | The inputs state promotion on rejection and never request demotion; adding it would widen the request | Tiers can only rise within an attempt sequence, so risk to quality is bounded | omn-product-owner |
| `D-003` | Distributed-copy parity (`S-007`) and documentation (`S-008`) are should-have, not must-have | The change request lists them as surfaces, but the business success measures are met by runtime behaviour, metrics, and verification alone | If cut, installed copies and documentation lag while the runtime outcome is still delivered | omn-product-owner |
| `D-004` | The host model hint is scoped as configuration advice only, with its form left open in `Q-002` | The business intent bars choosing vendors or model identifiers inside the runtime while the feature request requires a tier-to-hint mapping; the two are reconciled by keeping the hint as declared configuration | The delivered mapping cannot embed runtime logic that selects a model | omn-product-owner |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | What minimum share of an implement-feature run's invocations must be non-deep for the business to call this successful? | no | omn-business-analyst | Scope Gate |
| `Q-002` | In what form is the host model hint declared, given the non-goal against model identifiers inside the runtime? | no | architect | solution-design-and-risk-assessment |
| `Q-003` | Which tier does each phase the request does not name receive, and which phase identifiers do the request's named categories map to? | no | architect | solution-design-and-risk-assessment |

## Handoff

- Downstream owner: planner, owner of the execution-planning phase
- Gate: Scope Gate (implement-feature), decided by omn-business-analyst under the Producer Exclusion Rule
- Evidence for the gate: Scope items `S-001` to `S-009`, exclusions `X-001` to `X-006`, acceptance criteria `A-001` to `A-021` each with a scope reference and verification method, decisions `D-001` to `D-004`, and non-blocking questions `Q-001` to `Q-003`
- Deferred to downstream: Task decomposition and sequencing to planner; the choice of declaration carrier, hint form, and per-phase assignments to architect; the test strategy and validation execution to QA
