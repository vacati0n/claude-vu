```yaml
plan:
  planId: PLAN-run-ded114f50a46
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/model-tier-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:7fa529598e6e925362f09ed43c4a4a9e
  contextDigest: sha256:62e7676afa2df10b3af32629f294e88a
```

## Executive Summary

This plan delivers a per-phase model tier for the framework's operators: each dispatchable phase is declared light, standard, or deep in one authoritative place, and each dispatch envelope carries an additive tier record. A rejected light or standard attempt is promoted one tier on the next attempt and never retried at the same tier. Success means at least 3 of the 6 implement-feature phases are dispatched at a non-deep tier, as reported by the run's own metrics, with every existing verifier at its recorded baseline (A-002). The work is 14 tasks in 9 execution waves: 3 design decisions, 6 implementation tasks, 3 verification tasks, and 2 documentation or handoff tasks. The highest-impact risk is R-001: the 3-of-6 target is reachable only if `execution-planning`, which the request does not name, is assigned a non-deep tier. The plan status is complete; no blocking open question exists.

## Business Objectives

- BO-1: Lower the cost of an implement-feature run for operators by dispatching at least 3 of its 6 phases at a non-deep tier, measured by the non-deep invocation share in the run's execution metrics. Traces to S-001, S-005, A-002.
- BO-2: Keep correctness mechanically decided while cost falls, for gate owners and downstream agents, measured by every verifier returning its recorded baseline result and zero rejected light or standard attempts retried at the same tier. Traces to S-003, S-004.
- BO-3: Give operators visibility and a documented lever over per-phase tiering, measured by a tier record in every envelope, per-tier figures in metrics, and the rules stated in runtime governance documentation. Traces to S-002, S-005, S-008.

## Technical Objectives

- TO-1: One authoritative declaration assigns exactly one tier to every dispatchable phase and one host hint to each tier, with no tier assignment in agent module text; verified by a coverage check that fails when a phase is removed. Traces to BO-1.
- TO-2: The envelope carries an additive tier record (tier, host hint, basis) that is deterministic from run state, with original fields unchanged and no model invocation or vendor dependency added; verified by field comparison and replay stability. Traces to BO-2, BO-3.
- TO-3: Escalation is promotion-only, derived from recorded rejection state, capped at deep, and identical in-session and from recorded state alone; verified by a monotonicity check. Traces to BO-2.
- TO-4: Execution metrics report invocations and estimated context bytes per tier, summing to the run totals; verified by comparison with a completed run. Traces to BO-1, BO-3.
- TO-5: The distributed copy equals the authoritative copy, the runtime version value rises, and the governance documentation states the field and rule; verified by the synchronisation check, a version comparison, and a documentation review. Traces to BO-3.

## Scope

### In Scope

- S-001: One declared tier per dispatchable phase and one host hint per tier, in a single authoritative declaration outside agent text. Tasks T-001, T-002, T-003, T-004, T-005.
- S-002: An additive tier record in every dispatch envelope: resolved tier, host hint, basis. Tasks T-006, T-007.
- S-003: One-tier promotion after a validator rejection or a gate rejection with rollback, recorded with its reason, with no escalation above deep. Tasks T-008, T-009.
- S-004: A phase with no declaration inherits the host model, and no existing run, replay, or verifier changes outcome. Tasks T-005, T-006.
- S-005: Execution metrics report invocations and estimated context bytes by tier. Task T-010.
- S-006: Framework verification detects a dispatchable phase with no declared tier and a non-monotonic escalation. Task T-011.
- S-007: The distributed copy carries the same tier behaviour as the authoritative copy. Task T-012.
- S-008: The envelope field and escalation rule are documented in runtime governance documentation. Task T-013.
- S-009: The runtime version value increments. Task T-014.

### Out of Scope

- X-002: Vendor or model identifiers in runtime logic, any model call by the runtime, any vendor SDK dependency; the runtime only names a tier and the host chooses.
- X-003: Changes to agent module text, Phase Model tables, the gate matrix, validators, templates, or artifact contracts; the request is additive only.
- X-004: Changing which phases exist, who owns them, or what they produce; not requested.
- X-005: Editing agent entrypoint model declarations; the host override makes the hint effective while they stay unchanged.

### Deferred

- X-001: Concurrent phase execution; brought into scope by a separate change request for parallel phase execution.
- X-006: Lowering a tier after success or adaptive tiering; brought into scope by a supplied input requesting demotion.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | Statements S-001 to S-009 adopt the identifiers of the approved scope items one-to-one; upstream acceptance criteria are cited as UAC-nnn and upstream questions as UQ-nnn | plan-wide | Trace between this plan and the scope definition breaks | omn-product-owner |
| A-002 | Upstream question UQ-001 is resolved: success is at least 3 of 6 implement-feature phases dispatched at a non-deep tier (supplied by the invoking operator, not by a revised scope artifact) | S-005 | The measure in BO-1 and the T-002 constraint change | omn-business-analyst |
| A-003 | The host accepts a per-dispatch model override, so a tier hint can take effect | S-002 | The hint is advisory only and BO-1 savings do not materialise | omn-tech-lead |
| A-004 | Recorded run state (recovery ledger, attempt counters) distinguishes a validator rejection from a gate rejection with rollback and persists across sessions | S-003 | Escalation cannot be derived from recorded state; T-008 and T-009 gain a recording task | architect |
| A-005 | omn-documentation can perform the distributed-copy refresh in the closing phase | S-007 | T-012 is reassigned to another owner | omn-tech-lead |
| A-006 | The existing verification surface can host the new checks without changing any existing verifier result | S-006 | T-011 splits into a surface change and a check addition | architect |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | `execution-planning` is assigned deep, or a named-light phase is assigned standard | Fewer than 3 of 6 phases non-deep; BO-1 unmet | medium | T-002, T-005 | T-002 acceptance requires at least 3 of 6 non-deep; T-005 reads the metric | architect |
| R-002 | requirement | Request categories (technical discovery, artifact packaging, repository scan, root-cause analysis) map ambiguously to phase identifiers | A dispatchable phase is left undeclared or mis-tiered | medium | T-002, T-011 | T-002 records the mapping; T-011 fails on any uncovered phase | architect |
| R-003 | technical | Recorded rejection state is insufficient to reproduce an escalation in a fresh session | Escalation differs between sessions; UAC-012 fails | medium | T-008, T-009 | T-008 decides the state read; T-005 compares in-session and fresh dispatch | architect |
| R-004 | technical | A new envelope field or metric changes an artifact the replay check compares | An existing verifier leaves its baseline | medium | T-005, T-006, T-010 | T-006 and T-010 acceptance require deterministic output; T-005 runs all verifiers | omn-dev-1-implement |
| R-005 | dependency | The host stops accepting a per-dispatch model override | Tier hint has no effect; cost does not fall | low | T-006 | Accepted; the record remains advisory and the architecture records the host dependency | omn-tech-lead |
| R-006 | dependency | The distributed copy is hand-edited, or the authoritative tree changes after the refresh | Parity check reports differences | medium | T-012 | T-012 runs last and its acceptance requires zero differences | omn-documentation |
| R-007 | operational | Cheaper tiers produce more rejected attempts | Promotion cost offsets the saving | low | T-009, T-010 | T-010 reports per-tier invocations so the effect is visible | omn-tech-lead |

## Task Breakdown

### T-001 Decide the tier declaration structure

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: none
- Traces to: S-001, S-004
- Status: ready
- Description: The location, keying by workflow and phase, and form of the host hint of the single tier declaration are recorded as a decision (resolves Q-002), with no model identifier required in runtime logic.
- Acceptance Criteria:
  - The decision names one authoritative location outside agent text and workflow tables
  - The decision states the form of the host hint and the behaviour for an undeclared phase
- Gate: Design Gate

### T-002 Decide the tier of each dispatchable phase

- Owner: architect
- Complexity: M (confidence: low)
- Depends on: T-001
- Traces to: S-001, A-002
- Status: assumption-dependent
- Description: Every dispatchable phase of every active workflow is assigned exactly one tier, with the request's named categories mapped to phase identifiers (resolves Q-001).
- Acceptance Criteria:
  - Each phase has exactly one tier and the request's light and deep lists resolve as named
  - At least 3 of the 6 implement-feature phases are assigned a non-deep tier
- Gate: Design Gate

### T-003 Create the tier declaration

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-001, T-002
- Traces to: S-001
- Status: ready
- Description: The authoritative declaration exists, containing T-002's assignments and one host hint per tier, in the location T-001 decided, with no tier text in agent modules.
- Acceptance Criteria:
  - A text search of agent module files for tier assignments returns zero matches
  - A search of the framework finds tier assignment stated in exactly one location
- Gate: none

### T-004 Design verification evidence for the tier change

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-002, T-008
- Traces to: S-001, S-002, S-003, S-004, S-005
- Status: ready
- Description: A validation design maps each scope acceptance criterion UAC-001 to UAC-021 to a named evidence procedure, including rejection scenarios for light, standard, and deep phases.
- Acceptance Criteria:
  - Every UAC-nnn is mapped to one procedure and one expected result
  - Escalation scenarios cover validator rejection, gate rejection with rollback, and a deep phase
- Gate: Verification Gate

### T-005 Verify the tier change against the scope acceptance criteria

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-004, T-007
- Traces to: S-001, S-002, S-003, S-004
- Status: ready
- Description: The T-004 procedures are executed and their results recorded, including all existing verifiers against their recorded baselines and the in-session versus fresh-session escalation comparison.
- Acceptance Criteria:
  - Every UAC-nnn has recorded evidence with a pass or fail result
  - All existing verifiers, including replay stability, match their recorded baselines
- Gate: Verification Gate

### T-006 Implement tier resolution with the additive envelope record

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-003
- Traces to: S-002, S-004, A-003
- Status: assumption-dependent
- Description: Every dispatch envelope carries a tier record with non-empty tier, host hint, and basis, derived deterministically from run state; an undeclared phase resolves to inheriting the host model.
- Acceptance Criteria:
  - Every envelope of one implement-feature run carries a complete tier record
  - Original envelope fields are unchanged in name and value against a pre-change envelope
- Gate: none

### T-007 Review the tier change set against the additivity constraint

- Owner: omn-dev-2-reviewer
- Complexity: M (confidence: medium)
- Depends on: T-009, T-010, T-011, T-014
- Traces to: S-002
- Status: ready
- Description: The change set is reviewed and a readiness verdict recorded stating that it adds zero model invocations, zero vendor dependencies, and no edits to the surfaces excluded by X-003 and X-005.
- Acceptance Criteria:
  - The review package states the verdict against each exclusion
  - Findings of critical or major severity are resolved or formally accepted
- Gate: Review Gate

### T-008 Decide the escalation derivation rule

- Owner: architect
- Complexity: M (confidence: low)
- Depends on: none
- Traces to: S-003, S-004, A-004
- Status: assumption-dependent
- Description: The recorded state that triggers promotion after a validator rejection or a gate rejection with rollback is named, with the deep ceiling and the reason format, so that the result is independent of session.
- Acceptance Criteria:
  - The decision names the recorded state read for both rejection kinds
  - The decision states that deep never rises and no tier is ever lowered
- Gate: Design Gate

### T-009 Implement promotion-only escalation

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-006, T-008
- Traces to: S-003, A-004
- Status: assumption-dependent
- Description: After a recorded rejection, the next attempt of a light or standard phase resolves exactly one tier higher and its envelope records the escalation and reason; a deep phase stays deep.
- Acceptance Criteria:
  - A dispatch after each rejection kind shows one tier higher with a reason naming the rejection
  - A dispatch from recorded state alone yields the same tier as an in-session dispatch
- Gate: none

### T-010 Implement per-tier execution metrics

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-006
- Traces to: S-005
- Status: ready
- Description: Execution metrics list invocations and estimated context bytes for each tier and the non-deep invocation share as a figure.
- Acceptance Criteria:
  - Per-tier values sum to the run totals for a completed run
  - The non-deep share for an implement-feature run is at least 3 of 6 invocations
- Gate: none

### T-011 Implement the tier verification checks

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-003, T-009
- Traces to: S-006, A-006
- Status: assumption-dependent
- Description: Framework verification fails when a dispatchable phase has no declared tier and when an escalation resolves to the same or a lower tier than the prior attempt.
- Acceptance Criteria:
  - The check fails against a declaration with one phase removed
  - The check fails against an escalation record that does not rise
- Gate: none

### T-012 Refresh the distributed copy

- Owner: omn-documentation
- Complexity: S (confidence: low)
- Depends on: T-005, T-013
- Traces to: S-007, A-005
- Status: assumption-dependent
- Description: The distributed copy is refreshed from the final authoritative tree by the payload synchronisation command, never by hand.
- Acceptance Criteria:
  - The synchronisation check reports zero differing files
  - No distributed file is edited outside the synchronisation command
- Gate: Closure Gate

### T-013 Document the tier governance rules

- Owner: omn-documentation
- Complexity: S (confidence: medium)
- Depends on: T-007, T-009
- Traces to: S-008
- Status: ready
- Description: The runtime governance documentation states the envelope field, its three parts, the escalation rule, and the deep ceiling, and the runtime README is not enlarged.
- Acceptance Criteria:
  - A review finds all four items stated in the governance documentation
  - The runtime README size is not greater than before the change
- Gate: Closure Gate

### T-014 Increment the runtime version

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-006
- Traces to: S-009
- Status: ready
- Description: The runtime version value after the change is greater than the value before it.
- Acceptance Criteria:
  - The version value after the change is greater than the recorded value before it
  - No file other than the version declaration changes as part of this task
- Gate: none

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | contract | Assignments are keyed in the structure T-001 decides |
| T-001 | T-003 | contract | The declaration takes the form T-001 decides |
| T-002 | T-003 | produces-consumes | The declaration holds T-002's assignments |
| T-002 | T-004 | contract | Evidence procedures bind to the decided assignments |
| T-008 | T-004 | contract | Escalation scenarios bind to the decided rule |
| T-003 | T-006 | produces-consumes | Resolution reads the declaration |
| T-006 | T-009 | contract | Escalation extends the tier resolution |
| T-008 | T-009 | decision-gate | Escalation scope depends on the decided rule |
| T-006 | T-010 | produces-consumes | Metrics read the tier record |
| T-003 | T-011 | produces-consumes | The coverage check reads the declaration |
| T-009 | T-011 | contract | The monotonicity check binds to the escalation record |
| T-006 | T-014 | produces-consumes | The version identifies the release that first emits the tier record |
| T-009 | T-007 | verification | Review covers the escalation change |
| T-010 | T-007 | verification | Review covers the metrics change |
| T-011 | T-007 | verification | Review covers the verification change |
| T-014 | T-007 | verification | Review covers the version change |
| T-004 | T-005 | produces-consumes | Execution uses the evidence design |
| T-007 | T-005 | verification | Verification runs against the reviewed change set |
| T-009 | T-013 | produces-consumes | Documented behaviour must match implemented behaviour |
| T-007 | T-013 | verification | Documentation describes the reviewed change set |
| T-005 | T-012 | produces-consumes | The copy is taken from the verified authoritative tree |
| T-013 | T-012 | produces-consumes | The copy includes the final documentation |
| Host platform owner | T-006 | external | The hint takes effect only if the host accepts a per-dispatch override |

### 8.2 External Dependencies

| Responsible party | What is needed | Blocks |
|---|---|---|
| Host platform owner | Acceptance of a per-dispatch model override | T-006 (effectiveness only; matching risk R-005) |

### 8.3 Implementation Order

- Wave 1: T-001, T-008
- Wave 2: T-002
- Wave 3: T-003, T-004
- Wave 4: T-006
- Wave 5: T-009, T-010, T-014
- Wave 6: T-011
- Wave 7: T-007
- Wave 8: T-005, T-013
- Wave 9: T-012

## Suggested Workflow

Selected workflow: implement-feature

Selected because: the plan delivers new framework functionality, which maps to `implement-feature`; this run is already executing it.

| Phase | Tasks |
|---|---|
| scope-and-acceptance | none (completed upstream) |
| execution-planning | none (this plan) |
| solution-design-and-risk-assessment | T-001, T-002, T-008 |
| implementation | T-003, T-006, T-009, T-010, T-011, T-014 |
| quality-review | T-004, T-005, T-007 |
| documentation-and-release-handoff | T-012, T-013 |

| Gate | Required owners |
|---|---|
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| technical-approach-definition | T-001, T-002, T-008 | architect | Primary |
| implementation-delivery | T-003, T-006, T-009, T-010, T-011, T-014 | omn-dev-1-implement | Primary |
| validation-design | T-004 | omn-qa | Primary |
| quality-verification | T-005 | omn-qa | Primary |
| code-review | T-007 | omn-dev-2-reviewer | Primary |
| documentation | T-013 | omn-documentation | Primary |
| release-readiness | T-012 | omn-documentation | Secondary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | skills/architecture/clean-architecture-checklist.md | T-001, T-002, T-008 | Primary |
| S02 | skills/business/domain-modeling.md | T-001, T-002 | Secondary |
| S03 | skills/dotnet/engineering-playbook.md | T-003, T-006, T-009, T-010, T-011, T-014 | Primary |
| S07 | skills/testing/testing-strategy.md | T-004, T-005 | Primary |
| S08 | skills/performance/performance-engineering.md | T-007, T-010 | Secondary |
| S10 | skills/git/git-collaboration.md | T-012 | Advisory |

## Acceptance Criteria

1. BO-1: The coverage check reports zero uncovered dispatchable phases and at least 3 of the 6 implement-feature phases resolve non-deep. Evidence: T-005 record for UAC-001, UAC-002, and UAC-016.
2. BO-1, BO-3: Execution metrics list invocations and estimated context bytes per tier, summing to the run totals. Evidence: metrics of a completed run, UAC-015.
3. BO-2: After a rejection, a light or standard phase resolves exactly one tier higher with a stated reason, a deep phase stays deep, and the result is identical across sessions. Evidence: envelope inspection, UAC-008 to UAC-012.
4. BO-2: Every existing verifier, including replay stability, returns its recorded baseline result, and an undeclared phase inherits the host model. Evidence: verifier runs, UAC-013 and UAC-014.
5. BO-3: Every envelope of an implement-feature run carries a complete tier record and its original fields are unchanged. Evidence: field-by-field comparison, UAC-005 and UAC-006.
6. BO-2: The change adds zero model invocations, zero vendor dependencies, and zero tier assignments in agent text. Evidence: review verdict from T-007 and text search, UAC-004 and UAC-007.
7. BO-3: The governance documentation states the four required items, the runtime version value rises, and the distributed copy differs in zero files. Evidence: documentation review, version comparison, synchronisation check, UAC-019 to UAC-021.

## Definition of Done

- [ ] All plan acceptance criteria are verified with recorded evidence
- [ ] All mandatory gates are approved with owners recorded
- [ ] Task acceptance criteria are satisfied or formally waived
- [ ] Assumptions are confirmed or converted to recorded decisions
- [ ] Risks are closed or accepted with named owners
- [ ] Open questions are closed or explicitly accepted
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Which phase identifiers across active workflows do the request's named categories (technical discovery, artifact packaging, repository scan, root-cause analysis) map to, and which tier does each unnamed phase receive? | no | architect | T-002, T-011 |
| Q-002 | In what form is the host model hint declared, given that the runtime may not embed model identifiers? | no | architect | T-001, T-003 |
