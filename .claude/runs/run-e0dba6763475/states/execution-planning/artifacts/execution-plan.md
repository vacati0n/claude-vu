```yaml
plan:
  planId: CKA-02-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-02-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:c153cb3a0a4f3d8bc12bb9e8a069b1a0
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
```

## Executive Summary

This plan makes the distributed package self-contained for fresh-environment users: a non-editable install of the built package initializes, installs, and validates with no explicit source flag, while every existing installation mode keeps its current behaviour. The work is requested by ticket CKA-02 in the adoption backlog under docs/ and is bounded by the upstream scope definition produced in this run. It decomposes into ten tasks across five execution waves, beginning with the packaging-mechanism decision and the parity-assurance clarification. Delivery covers carrying the complete framework payload in the built distributions, adding a bundled-payload resolution fallback behind the existing candidates, and regenerating the distribution metadata to match. The highest-impact risk is R-003: an incompletely enumerated payload directory set would ship non-editable installs that miss files and fail the parity check. One open question, Q-001, is non-blocking and is resolved by task T-008 ahead of validation design. Plan status is complete.

## Business Objectives

1. A user who installs the published package into a fresh environment can use the tool immediately, with no separate framework checkout to locate or supply. Received by fresh-environment adopters; measured by the clean-environment walkthrough and the dry-run parity comparison. Traces to S-003, S-007, S-008.
2. Existing installation modes keep their current behaviour, so the adoption improvement costs current users nothing. Received by explicit-source and checkout-adjacent users; measured by the precedence demonstrations and the failure-guidance check. Traces to S-010, S-011.
3. The dependent continuous-integration gating ticket (CKA-03) is unblocked. Received by the adoption programme; measured by backlog dependency closure once this change is delivered. Traces to S-012.

## Technical Objectives

1. A non-editable build carries the complete framework payload tree — all managed directories plus the seed directories — with zero files matching the installer's exclusion patterns. Verified by inspection of the built distributions and the dry-run parity comparison. Traces to business objective 1 and S-004, S-013.
2. Source resolution selects the bundled payload only when neither an explicit source nor a checkout-adjacent tree resolves, leaving the existing candidate order unchanged. Verified by demonstration across the three named environment configurations. Traces to business objective 2 and S-005, S-010, S-017.
3. When no source candidate resolves, the failure message retains the existing actionable guidance, naming at least the explicit-source remedy. Verified by demonstration in an environment where nothing resolves. Traces to business objective 2 and S-005.
4. Freshly built source and binary distributions show zero discrepancies between their file lists and the configured payload tree. Verified by comparison of the freshly built distributions against the source payload tree. Traces to business objective 1 and S-006, S-014.

## Scope

### In Scope

- A working non-editable install: initialize, install, and validate succeed in a clean environment with no explicit source flag (S-007). Delivered by T-002 and T-004; verified by T-007.
- The complete framework payload — all managed directories plus the seed directories, filtered by the installer's exclusion patterns — carried in the built distributions (S-004, S-013). Delivered by T-001 and T-002.
- A bundled-payload resolution fallback behind the existing candidates, with existing precedence preserved and the failure guidance kept actionable (S-005, S-010, S-017). Delivered by T-003 and T-004.
- Distribution file lists regenerated to match the new packaging configuration with zero discrepancies (S-006, S-014). Delivered by T-005.
- Validation, constraint-compliance review, and documentation of the change per the delivery constraints (S-009, S-011). Delivered by T-006, T-007, T-009, and T-010.

### Out of Scope

- Any alteration to gate-decision recording, gate-matrix semantics, producer exclusion, approval-requirement enforcement, or any human-block path. Excluded because the request constrains this change to be additive only (S-009).
- The dependent continuous-integration gating ticket (CKA-03). Excluded because it is a separate backlog ticket that depends on this one; delivering it here would widen the change beyond its request (S-012).
- Any reordering of source-resolution precedence for existing users. Excluded because the request constrains precedence to remain unchanged (S-010).

### Deferred

- Strengthening the dry-run comparison from file-count parity to file-set identity. Enters scope if the decision recorded by T-008 requires set identity (S-018, Q-001).

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The exclusion-pattern set the installer applies is enumerable and authoritative for the packaging filter; the request lists it non-exhaustively | S-004 | The packaging filter is mis-scoped; T-002 is re-scoped and the zero-excluded-files check is re-baselined | architect |
| A-002 | The two candidate packaging mechanisms named in the request are stated preferences, not mandates; either satisfies scope and the design decision selects one | S-004, S-015 | T-001 narrows to confirming the mandated mechanism; no other task changes | omn-product-owner |
| A-003 | The managed and seed directory sets are enumerable from the framework payload tree at the planned revision | S-004 | Packaging scope cannot be bounded; T-001 escalates to architect and T-002 is re-scoped | architect |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | The parity-assurance decision resolves to file-set identity after validation design has begun | The parity portion of validation coverage and its execution are reworked | low | T-006, T-007 | T-008 is sequenced ahead of T-006 by a decision-gate edge | omn-product-owner |
| R-002 | technical | The exclusion-pattern set applied at packaging diverges from the set the installer applies (A-001 false) | The bundled payload carries excluded files or omits needed ones; the zero-excluded-files and parity checks fail | medium | T-002, T-007 | T-001 records the authoritative pattern set before packaging begins | architect |
| R-003 | technical | The managed-plus-seed directory set is enumerated incompletely at packaging (A-003 false) | Non-editable installs miss payload files; the dry-run parity check fails | medium | T-002, T-007 | T-001 records the packaged directory set; the paired parity comparison in T-007 detects drift | architect |
| R-004 | technical | The bundled fallback changes the resolved source in an environment where an existing candidate is present | Existing users' behaviour changes; the precedence acceptance checks fail | low | T-004, T-007 | Three-environment precedence demonstration designed in T-006 and executed in T-007 | omn-qa |
| R-005 | technical | Regenerated distribution metadata still disagrees with the configured payload | The file-list acceptance check fails; stale entries ship | low | T-005, T-007 | Zero-discrepancy comparison executed in T-007 | omn-dev-1-implement |
| R-006 | delivery | Packaging or resolution work touches a forbidden gate-behavior path | The additive-only constraint is breached; the change is rejected at review and reworked | low | T-002, T-004, T-009 | T-009 explicitly checks the named forbidden areas; the suite and proof scripts are executed in T-007 | omn-dev-2-reviewer |

## Task Breakdown

### T-001 Select the payload packaging mechanism

- Owner: architect
- Complexity: S (confidence: high)
- Depends on: none
- Traces to: S-004, S-015, A-002
- Status: ready
- Description: An approved packaging decision record exists that selects one mechanism from the candidates the request names, enumerates the managed and seed directories the built package must carry, and records the authoritative exclusion-pattern set the packaging filter must match.
- Acceptance Criteria:
  - One packaging mechanism is selected and recorded with the rationale for the selection
  - The packaged directory set (managed plus seed) is enumerated in the decision record
  - The recorded exclusion-pattern set matches the set the installer applies
- Gate: Design Gate

### T-002 Deliver payload packaging in the built distributions

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-001
- Traces to: S-004, S-013, A-001, A-003
- Status: assumption-dependent
- Description: A non-editable build carries the complete framework payload tree recorded in the packaging decision, filtered so that zero files match the recorded exclusion-pattern set.
- Acceptance Criteria:
  - A freshly built distribution contains every file of the recorded payload directory set
  - The carried payload contains zero files matching the recorded exclusion-pattern set
- Gate: Review Gate

### T-003 Define the source-resolution fallback contract

- Owner: architect
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-005, S-010, S-017
- Status: ready
- Description: A resolution contract exists stating the full candidate order — explicit source first, then the checkout-adjacent tree, then the bundled payload — the location at which the bundled payload is resolvable under the selected mechanism, and the failure guidance retained when no candidate resolves.
- Acceptance Criteria:
  - The contract states the candidate order with the bundled payload strictly last
  - The contract states where the bundled payload resides under the selected packaging mechanism
  - The contract states the failure-message content, naming at least the explicit-source remedy
- Gate: Design Gate

### T-004 Deliver the bundled-payload resolution fallback

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-002, T-003
- Traces to: S-005, S-010
- Status: ready
- Description: Resolution behaves per the defined contract: the existing candidates keep winning, the bundled payload resolves only when neither existing candidate is present, and the failure guidance is retained when nothing resolves.
- Acceptance Criteria:
  - With an explicit source given, resolution selects it
  - With a checkout-adjacent tree present and no explicit source, resolution selects the tree
  - With neither present, resolution selects the bundled payload
  - With no candidate resolvable, the command fails with the guidance stated in the contract
- Gate: Review Gate

### T-005 Regenerate distribution metadata to match the configured payload

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-006, S-014
- Status: ready
- Description: The built source and binary distributions' file lists agree with the configured payload tree, with no stale entries surviving from the previous configuration.
- Acceptance Criteria:
  - Every configured payload file appears in the freshly built distributions' file lists
  - No listed entry is absent from the source payload tree
- Gate: Review Gate

### T-006 Design validation coverage for the delivered change

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-003, T-008
- Traces to: S-007, S-008, S-011, S-017
- Status: ready
- Description: Validation coverage exists addressing every plan acceptance criterion: the clean-environment walkthrough, the parity comparison at the assurance level decided in T-008, the three-environment precedence demonstration, the failure-guidance check, the distribution inspections, and the regression obligations from the delivery constraints.
- Acceptance Criteria:
  - Coverage addresses each acceptance criterion of T-002, T-004, and T-005
  - The parity comparison is specified at the assurance level recorded by T-008
  - The regression obligations from the delivery constraints are included as explicit checks
- Gate: Verification Gate

### T-007 Execute acceptance verification with recorded evidence

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-002, T-004, T-005, T-006
- Traces to: S-007, S-008, S-011, S-013, S-014, S-017
- Status: ready
- Description: Every item of the designed validation coverage is executed with recorded evidence: the clean-environment walkthrough, the paired parity comparison, the three-environment precedence demonstration, the failure-guidance check, the distribution inspections, the existing test suite, and the proof scripts.
- Acceptance Criteria:
  - Each coverage item from T-006 has a recorded pass or a recorded, dispositioned failure
  - The clean-environment walkthrough shows initialize, install, and validate succeeding with no explicit source flag
  - The suite run is recorded green and every proof script is recorded PROVEN
- Gate: Verification Gate

### T-008 Resolve the parity-assurance level for the dry-run comparison

- Owner: omn-product-owner
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-008, S-018
- Status: ready
- Description: A recorded decision states whether the dry-run comparison between a non-editable and an editable install must show file-count parity or file-set identity.
- Acceptance Criteria:
  - A decision record exists selecting exactly one assurance level — file-count parity or file-set identity — as the binding assurance for the dry-run comparison
  - The decision record states the rationale for the selected level
  - The decision record names Q-001 as the question it closes, and Q-001 is marked closed by it
- Gate: Scope Gate

### T-009 Review the delivered change for additive-only compliance

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: high)
- Depends on: T-002, T-004, T-005
- Traces to: S-009
- Status: ready
- Description: A review record confirms the delivered change leaves gate-decision recording, gate-matrix semantics, producer exclusion, approval-requirement enforcement, and every human-block path untouched.
- Acceptance Criteria:
  - Each named forbidden area is explicitly checked and recorded untouched
  - Any finding is severity-classified with a correction request
- Gate: Review Gate

### T-010 Update documentation for the delivered behaviour

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-004, T-007
- Traces to: S-011
- Status: ready
- Description: User-facing documentation reflects the self-contained install behaviour and the resolution order, release-impact notes are drafted, and the handbook matches every touched document per the delivery constraint.
- Acceptance Criteria:
  - The install and source-resolution documentation reflects the delivered behaviour
  - The handbook matches every touched document
  - Release-impact notes are drafted
- Gate: Closure Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | decision-gate | Packaging work binds to the selected mechanism and the recorded directory and filter sets |
| T-001 | T-003 | decision-gate | The resolution contract states where the bundled payload resides, which the selected mechanism determines |
| T-002 | T-004 | produces-consumes | The fallback resolves the bundled payload that the packaging places in the built distribution |
| T-003 | T-004 | contract | The fallback implementation binds to the defined resolution contract |
| T-002 | T-005 | produces-consumes | The regenerated metadata must list the payload the packaging configuration carries |
| T-003 | T-006 | contract | Validation coverage targets the candidate order and failure guidance the contract defines |
| T-008 | T-006 | decision-gate | The parity comparison is designed at the assurance level the decision records |
| T-002 | T-007 | verification | Acceptance verification validates the payload the packaging produced |
| T-004 | T-007 | verification | Acceptance verification validates the delivered resolution behaviour |
| T-005 | T-007 | verification | Acceptance verification validates the regenerated file lists |
| T-006 | T-007 | produces-consumes | Verification executes the coverage the design produced |
| T-002 | T-009 | verification | The review assesses the packaging change against the forbidden areas |
| T-004 | T-009 | verification | The review assesses the resolution change against the forbidden areas |
| T-005 | T-009 | verification | The review assesses the metadata change against the forbidden areas |
| T-004 | T-010 | produces-consumes | Documentation describes the delivered resolution behaviour |
| T-007 | T-010 | verification | Documentation reflects verified behaviour and its evidence |

### 8.2 External Dependencies

None identified. The request declares no dependency on any party outside the plan's authority, and the upstream scope definition records no external dependency.

| Responsible party | What is needed | Blocks |
|---|---|---|
| — | None identified | — |

### 8.3 Implementation Order

- Wave 1: T-001, T-008
- Wave 2: T-002, T-003
- Wave 3: T-004, T-005, T-006
- Wave 4: T-007, T-009
- Wave 5: T-010

## Suggested Workflow

Selected workflow: `implement-feature`

Selected because: the plan delivers new user-facing capability — a self-contained install of the published package — with measurable acceptance criteria, a design decision, implementation, constraint-compliance review, verification, and release documentation; it continues the run in which this plan was produced.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | T-008 |
| `execution-planning` | plan handoff (this artifact) |
| `solution-design-and-risk-assessment` | T-001, T-003 |
| `implementation` | T-002, T-004, T-005 |
| `quality-review` | T-006, T-007, T-009 |
| `documentation-and-release-handoff` | T-010 |

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
| acceptance-authority | T-008 | omn-product-owner | Primary |
| architecture-analysis | T-001, T-003 | architect | Primary |
| technical-approach-definition | T-001, T-003 | architect | Primary |
| implementation-delivery | T-002, T-004, T-005 | omn-dev-1-implement | Primary |
| validation-design | T-006 | omn-qa | Primary |
| quality-verification | T-007 | omn-qa | Primary |
| code-review | T-009 | omn-dev-2-reviewer | Primary |
| governance-enforcement | T-009 | omn-dev-2-reviewer | Primary |
| documentation | T-010 | omn-documentation | Primary |
| release-communication | T-010 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S02 | business/domain-modeling.md | T-008 | Primary |
| S01 | architecture/clean-architecture-checklist.md | T-001, T-003 | Primary |
| S07 | testing/testing-strategy.md | T-006, T-007 | Primary |
| S09 | security/secure-engineering.md | T-004 | Secondary |

## Acceptance Criteria

1. In a clean environment, a non-editable install of the built package followed by initialize, install, and validate succeeds, with every command exiting successfully and no explicit source flag supplied. Verifies business objective 1. Evidence: scripted walkthrough record from T-007 at the Verification Gate.
2. A dry-run install in a non-editable environment enumerates the payload at parity with an editable install of the same revision, at the assurance level decided by T-008. Verifies business objective 1. Evidence: paired comparison record from T-007.
3. In each existing configuration, resolution selects the same source as before this change — the explicit source when given, the checkout-adjacent tree when present with no explicit source — and the bundled copy only when neither is present; when nothing resolves, the failure message names the explicit-source remedy. Verifies business objective 2. Evidence: three-environment demonstration and failure-message record from T-007.
4. Freshly built distributions carry zero files matching the installer's exclusion patterns and show zero discrepancies between their file lists and the configured payload tree. Verifies business objective 1. Evidence: distribution inspection record from T-007.
5. This change is recorded delivered in the adoption backlog, leaving the dependent gating ticket blocked only on already-delivered work. Verifies business objective 3. Evidence: backlog status record at the Closure Gate.

## Definition of Done

- [ ] All five plan acceptance criteria are verified with recorded evidence
- [ ] The Scope, Planning, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for T-001 through T-010 are satisfied or formally waived
- [ ] The existing test suite is recorded green and every proof script is recorded PROVEN, per the delivery constraint carried from scope (S-011, S-016)
- [ ] A-001 through A-003 are confirmed or converted to recorded decisions
- [ ] R-001 through R-006 are closed or accepted with named owners
- [ ] Q-001 is closed by the decision record from T-008 or explicitly accepted
- [ ] Documentation and release-impact notes are published, with the handbook matching every touched document
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Is file-count parity or file-set identity the intended assurance for the dry-run comparison between a non-editable and an editable install? Count parity could pass while the contents differ. Carried forward from the upstream scope definition. | No | omn-product-owner | T-006, T-007, T-008 |

## Traceability Matrix

Statements S-001 through S-012 are normalized from the supplied feature request in document order; S-013 through S-018 are normalized from the upstream scope definition's claims that refine or extend the request, in document order. Forward closure: 18 of 18 statements covered. Backward closure: 10 of 10 tasks traced. Lateral closure: every risk, assumption, and edge resolves to existing identifiers.

| Statement | Covered by |
|---|---|
| S-001 | Context (non-editable install cannot install); motivates business objective 1; addressed by T-002, T-004 |
| S-002 | Context (resolution finds only a checkout-adjacent tree); motivates technical objective 2; addressed by T-003, T-004 |
| S-003 | Context (users must pass an explicit source path); motivates business objective 1; addressed by T-004, T-007 |
| S-004 | T-001, T-002; A-001, A-002, A-003 |
| S-005 | T-003, T-004 |
| S-006 | T-005 |
| S-007 | T-006, T-007 |
| S-008 | T-006, T-007, T-008 |
| S-009 | T-009; Out of Scope exclusion 1 |
| S-010 | T-003, T-004, T-006, T-007; Out of Scope exclusion 3 |
| S-011 | T-006, T-007, T-010; Definition of Done |
| S-012 | Context (priority; blocks the dependent gating ticket); acceptance criterion 5; Out of Scope exclusion 2 |
| S-013 | T-002, T-007 |
| S-014 | T-005, T-007 |
| S-015 | T-001; A-002 |
| S-016 | Definition of Done (delivery constraints carried, not duplicated as acceptance criteria); T-007 |
| S-017 | T-003, T-006, T-007 |
| S-018 | Q-001; T-008 |
