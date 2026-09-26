```yaml
plan:
  planId: CKA-04-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-04-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:f63a8c3a43a79d5c0d1f218ebe85bbf6
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
```

## Executive Summary

This plan delivers ticket CKA-04: a content-contract check suite at `tests/test_content_contracts.py` that pins the structural properties of governance prose the runtime depends on, protecting framework maintainers and every downstream consumer of decidable gates. Success is defined by the two verbatim ticket criteria: a fixture gate matrix mutated to a producer-only owner row fails a check, and the suite runs green on the change's tree with the four `Status:` banners landed. Per the gate-approved upstream scope decision, the four one-line banners on the root governance documents land inside this change and the banner check is authored unconditional. The work decomposes into eight tasks across three execution waves, beginning with the check design and the banner-text confirmation in parallel. The highest-impact risk is R-005: a coercive-language scan that fails to distinguish coercive instruction from prohibition phrasing would flag contract text that forbids bypassing gates and turn the suite red on the current tree. Plan status is complete; two non-blocking open questions, Q-001 and Q-002, require answers before design approval and banner authoring respectively.

## Business Objectives

1. Framework maintainers and downstream run operators are protected from silent governance decay: an edit to governance prose that breaks a structural property the runtime reads is reported as a failing check before it lands. Measured as: each pinned property's negative fixture yields at least one failing check while the corresponding current-tree content yields zero. Traces to S-003, S-004, S-005, S-006, S-014.
2. Governance-prose maintenance stays low-friction for maintainers: wording edits that preserve pinned structure produce no check failures. Measured as: a structure-preserving reword fixture of a governed document yields zero failures. Traces to S-013, S-017.
3. The banner outcome the input assigns to the CKA-05 coupling is in force and durable: the four root governance documents carry `Status:` banners that cannot be dropped unnoticed. Measured as: four of four banners present on the change's tree, and a banner-removal fixture yields a failing check. Traces to S-007, S-011, S-015, S-020.

## Technical Objectives

1. A content-contract check module exists at `tests/test_content_contracts.py` on stdlib `unittest` (both named in the input) and is discovered and executed by the existing CI verification run with zero CI configuration change. Verified by the CI run record. Traces to business objective 1 and S-008.
2. Every gate row in `workflows/workflow-gate-matrix.md` names at least one owner outside the producing role's alias set, and that property is pinned by a check with a producer-only negative fixture. Verified by executed negative-fixture demonstration. Traces to business objective 1 and S-009.
3. The superseded agent specifications named in the input carry their supersession status marker on line 1, and that property is pinned by a check with a marker-absent negative fixture. Verified by executed negative-fixture demonstration. Traces to business objective 1 and S-010.
4. Each of the four root governance documents carries a one-line `Status:` banner, and banner presence is pinned by an unconditional check with a banner-removed negative fixture. Verified by executed negative-fixture demonstration plus inspection of the four documents. Traces to business objective 3 and S-011.
5. No agent contract module under `agents/*/` matches the enumerated coercive formulations — skip, bypass, or auto-approve a gate, or proceed without approval — and that property is pinned by a check with a coercive-fixture demonstration. Verified by executed negative-fixture demonstration plus a green run over the current modules. Traces to business objective 1 and S-012.
6. Every assertion in the suite binds to structure — table cells, first-line markers, banner lines, pattern structure — never to sentence wording. Verified by a structure-preserving reword demonstration yielding zero failures. Traces to business objective 2 and S-013.

## Scope

### In Scope

- A content-contract check suite at `tests/test_content_contracts.py`, discovered and executed by the existing CI verification run with zero configuration change (S-008). Maps to T-001, T-002, T-006.
- A check that no gate-matrix row is producer-only under the alias reading of the Producer Exclusion Rule (S-004, S-009, S-014). Maps to T-002.
- A check that superseded agent specifications carry their status marker on line 1 (S-005, S-010). Maps to T-002.
- A check that the four root governance documents carry a `Status:` banner (S-007, S-011). Maps to T-002.
- A check that no agent contract module matches the enumerated coercive auto-chain formulations (S-006, S-012). Maps to T-001, T-002.
- The four one-line `Status:` banners landed on `working-memory.md`, `rule-engine.md`, root `quality-gates.md`, and `decision-matrix.md` (S-007, S-011, S-015). Maps to T-003, T-004.
- Structure-only assertion binding, demonstrated by a structure-preserving reword fixture (S-013, S-017). Maps to T-005, T-007.
- Constraint-compliance review and CI verification evidence, including `tests/` green and all `verify_*.py` proof scripts PROVEN (S-014, S-015, S-016, S-018). Maps to T-005, T-006.
- User documentation consistency for the touched governance documents (S-018). Maps to T-008.

### Out of Scope

- Any modification to gate-decision runtime behavior: `record_gate_decision`, the gate-matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path. Excluded because S-016 forbids it; this change is additive only.
- CI configuration or verification-workflow changes. Excluded because S-008 requires discovery by the existing CKA-03 test surface with no configuration change.
- Assertions bound to sentence wording of governance prose. Excluded because S-013 and S-017 direct structure-only binding so wording edits stay free.
- CKA-05 content beyond the presence of the four one-line `Status:` banners. Excluded because the gate-approved upstream scope decision narrows the coupling to banner presence only.
- The anti-rationalization table checks that CKA-16 later adds to this suite. Excluded because S-020 places them in a separate, later ticket.

### Deferred

- Widening the coercive-pattern inventory beyond the four enumerated formulations. Enters the check's content when T-001 answers Q-001 affirmatively; it requires plan re-scoping only if the widened inventory changes which current modules match, which R-001 tracks.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The delivered CKA-03 CI test surface discovers a new stdlib `unittest` module under `tests/` with zero configuration change | S-002 | The suite cannot run in CI without a forbidden configuration change; T-006 fails and the constraint conflict escalates for a scope decision | omn-tech-lead |
| A-002 | The exact banner wording confirmed under the CKA-05 definition fits the one-line `Status:` structural form the banner check asserts | S-007 | T-002 and T-004 rework: either the banner check's structural form or the banner lines change | omn-product-owner |
| A-003 | The gate-approved upstream scope decision stands: the four banners land inside this change and the banner check is authored unconditional, with no activation gating | S-011 | T-003 and T-004 retire, the banner check gains activation gating, and the plan re-scopes | omn-product-owner (already confirmed at the Scope Gate) |
| A-004 | The coercive-language check's acceptance threshold is the four enumerated formulations — skip, bypass, or auto-approve a gate, or proceed without approval — and design may widen the inventory without changing plan structure | S-012 | If widening changes which current agent contract modules match, T-002 fixtures and the current-tree green criterion re-scope | architect |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | The design widens the coercive-pattern inventory beyond the enumerated formulations in a way that changes which current agent contract modules match | Check fixtures and the current-tree green criterion re-scope | low | T-001, T-002 | T-001 fixes the inventory and demonstrates the current modules pass; Q-001 records the review | architect |
| R-002 | requirement | The banner text confirmed under the CKA-05 definition does not fit the one-line structural form the banner check asserts | Banner check or banner lines rework before the change can land green | low | T-002, T-004 | T-003 confirms the text and T-001 fixes the structural form before T-004 lands the lines | omn-product-owner |
| R-003 | requirement | The gate-approved upstream decision to land the four banners inside this change is reopened | T-003 and T-004 retire; the banner check needs activation gating; the plan re-scopes | low | T-003, T-004 | Escalate to omn-product-owner and treat as a scope change returning to the scope phase | omn-product-owner |
| R-004 | technical | An assertion binds to sentence wording rather than structure | Wording-only edits fail checks, breaching the structure-only constraint and raising maintenance cost | medium | T-002 | T-005 reviews assertion binding; T-007 includes a structure-preserving reword demonstration | omn-dev-2-reviewer |
| R-005 | technical | The coercive-language scan flags prohibition phrasing already present in agent contract modules, such as contract text that forbids bypassing gates | The suite is red on the current tree, failing the verbatim green criterion | medium | T-001, T-002, T-006 | The design distinguishes coercive instruction from prohibition phrasing; current-tree green is demonstrated at T-006 | architect |
| R-006 | technical | The check's alias reading diverges from the alias semantics the runtime enforces through `producer_aliases()` | A producer-only row passes undetected, or a decidable row fails falsely; the pinned property no longer matches what the code reads | medium | T-001, T-002 | The design binds the check to the same alias source the runtime reads; the producer-only negative fixture demonstrates detection | architect |
| R-007 | dependency | The existing CI test surface does not discover the new module without a configuration change | The suite does not run in CI, or a forbidden configuration change would be required; the constraint conflict escalates | low | T-006 | T-006 verifies discovery from the CI run record; on failure escalate to omn-tech-lead for a scope decision | omn-tech-lead |

## Task Breakdown

### T-001 Define the content-contract check design

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: none
- Traces to: S-006, S-008, S-009, S-010, S-011, S-012, S-013, S-016, S-017, A-004
- Status: ready
- Description: An approved design exists that fixes, for each of the four checks, the structural property asserted and the negative-fixture strategy; the alias-reading source for the producer-exclusion check; the coercive-pattern inventory and its treatment of prohibition phrasing; and the one-line structural form of the `Status:` banner — all within the additive-only and zero-CI-configuration-change constraints.
- Acceptance Criteria:
  - The design fixes the structural property and negative-fixture approach for each of the four checks
  - The coercive-pattern inventory is recorded, distinguishes coercive instruction from prohibition phrasing, and closes Q-001
  - The banner structural form and the alias-reading source are stated such that the current tree, with the banners landed, passes every check
- Gate: Design Gate

### T-002 Author the content-contract check module

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-006, S-008, S-009, S-010, S-011, S-012, S-013, S-014, S-016, S-017
- Status: ready
- Description: `tests/test_content_contracts.py` exists on stdlib `unittest`, realizes the four checks and negative fixtures the approved design fixes, binds every assertion to structure only, and modifies no file governed by the additive-only constraint and no CI configuration file.
- Acceptance Criteria:
  - The module exists at the requested path and implements exactly the four designed checks with their negative fixtures
  - Mutating the fixture gate matrix to a producer-only owner row yields at least one failing check
  - No CI configuration file and no gate-decision behavior surface is modified by the change
- Gate: Review Gate

### T-003 Confirm the banner text for the four root governance documents

- Owner: omn-product-owner
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-007, S-011, A-002
- Status: ready
- Description: The one-line `Status:` text each of the four root governance documents carries, per the CKA-05 definition, is confirmed and recorded, closing Q-002.
- Acceptance Criteria:
  - A recorded banner text exists for each of the four documents
  - Each confirmed text is a single line beginning `Status:`
  - Q-002 is closed with the confirmation recorded
- Gate: none

### T-004 Author the four banner lines on the root governance documents

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-001, T-003
- Traces to: S-007, S-011, S-015, A-003
- Status: ready
- Description: Each of `working-memory.md`, `rule-engine.md`, root `quality-gates.md`, and `decision-matrix.md` carries its confirmed one-line `Status:` banner in the structural form the banner check asserts, and no other content of those documents changes.
- Acceptance Criteria:
  - Four of four documents carry the confirmed banner line
  - The banner check passes against the four documents as landed
  - No content beyond the added banner line changes in any of the four documents
- Gate: Review Gate

### T-005 Review the change for constraint compliance

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: high)
- Depends on: T-002, T-004
- Traces to: S-008, S-013, S-016, S-017
- Status: ready
- Description: A recorded review verdict exists confirming the change is additive — no modification to `record_gate_decision`, the gate-matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path — that no CI configuration file changed, and that every assertion binds to structure rather than wording.
- Acceptance Criteria:
  - The review record confirms no file governed by the additive-only constraint was modified
  - The review record confirms no CI configuration file was modified
  - The review record confirms each assertion binds to table cells, first-line markers, banner lines, or pattern structure, not sentence wording
  - The review record confirms all four banner lines are present as inspected on the change's tree
- Gate: Review Gate

### T-006 Verify the suite runs green in the CI verification run

- Owner: omn-qa
- Complexity: S (confidence: low)
- Depends on: T-002, T-004, T-007
- Traces to: S-008, S-014, S-015, S-018, A-001
- Status: assumption-dependent
- Description: The CI run record shows the content-contract checks were discovered and executed by the existing verification run with zero configuration change; all checks pass on the change's tree with the banners landed; each negative-fixture demonstration fails as designed; and the repository definition-of-done evidence — `tests/` green and all `verify_*.py` proof scripts PROVEN — is recorded.
- Acceptance Criteria:
  - The CI run record shows the new checks executed without any CI configuration change
  - Zero failing checks on the change's tree, and each negative fixture yields at least one failing check
  - `tests/` green and all `verify_*.py` proof scripts PROVEN are recorded as evidence
- Gate: Verification Gate

### T-007 Design validation coverage for the content-contract checks

- Owner: omn-qa
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-013, S-014, S-015, S-017, S-018
- Status: ready
- Description: Validation coverage exists mapping every plan acceptance criterion — negative-fixture detection for each of the four checks, current-tree green, discovery without configuration change, and structure-preserving reword freedom — to an executable verification method with named evidence.
- Acceptance Criteria:
  - Every plan acceptance criterion maps to a verification method and named evidence
  - Coverage includes a structure-preserving reword demonstration for at least one governed document
- Gate: Verification Gate

### T-008 Update user documentation for the touched governance documents

- Owner: omn-documentation
- Complexity: XS (confidence: high)
- Depends on: T-004
- Traces to: S-018
- Status: ready
- Description: `user-guide.html` matches the four touched governance documents: it reflects the banner additions, or a documentation review records that no user-guide content is affected by them.
- Acceptance Criteria:
  - Either the updated `user-guide.html` reflects the banner additions, or a recorded review states no user-guide content is affected
  - Release-impact notes for the governance-document touches are drafted
- Gate: Closure Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | contract | The module implements the checks, fixtures, and pattern inventory the approved design fixes |
| T-001 | T-004 | contract | The banner lines must land in the structural form the banner check asserts, which the design fixes |
| T-001 | T-007 | contract | Validation coverage targets the designed checks and fixtures |
| T-002 | T-005 | verification | The review assesses the authored module against the additive-only and structure-binding constraints |
| T-002 | T-006 | verification | The CI run verifies the authored checks |
| T-003 | T-004 | decision-gate | Banner authoring binds to the confirmed banner text |
| T-004 | T-005 | verification | The review assesses the banner additions for additive-only compliance and presence |
| T-004 | T-006 | verification | Current-tree green requires the banners landed |
| T-004 | T-008 | produces-consumes | Documentation reflects the landed banner additions |
| T-007 | T-006 | produces-consumes | The verification run executes the designed validation coverage |

### 8.2 External Dependencies

None identified. The CI test surface the input names as a prerequisite is recorded as already delivered (S-002), so no prerequisite outside the plan's authority remains pending; the residual risk that its discovery behavior does not hold is tracked as R-007 against A-001.

### 8.3 Implementation Order

Topological order over 8.1, ties within a wave by ascending identifier:

- Wave 1: T-001, T-003
- Wave 2: T-002, T-004, T-007
- Wave 3: T-005, T-006, T-008

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because: the plan delivers new verification functionality with bounded, gate-approved scope and measurable acceptance criteria, requiring design decisions, implementation, peer review, QA verification, and documentation handoff — the full phase set of that workflow.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | T-003 |
| `execution-planning` | plan handoff (this artifact) |
| `solution-design-and-risk-assessment` | T-001 |
| `implementation` | T-002, T-004 |
| `quality-review` | T-005, T-006, T-007 |
| `documentation-and-release-handoff` | T-008 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

This section recommends; the plan is handed off and no workflow is started here.

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| technical-approach-definition | T-001 | architect | Primary |
| structural-risk-analysis | T-001 | architect | Primary |
| acceptance-authority | T-003 | omn-product-owner | Primary |
| implementation-delivery | T-002, T-004 | omn-dev-1-implement | Primary |
| code-review | T-005 | omn-dev-2-reviewer | Primary |
| governance-enforcement | T-005 | omn-dev-2-reviewer | Primary |
| validation-design | T-007 | omn-qa | Primary |
| quality-verification | T-006 | omn-qa | Primary |
| documentation | T-008 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | architecture/clean-architecture-checklist.md | T-001 | Primary |
| S02 | business/domain-modeling.md | T-003 | Primary |
| S07 | testing/testing-strategy.md | T-002, T-005, T-006, T-007 | Primary |
| S09 | security/secure-engineering.md | T-001, T-005 | Secondary |

## Acceptance Criteria

1. A fixture gate matrix mutated so one row's owners all fall within the producing role's alias set yields at least one failing check, while the unmutated matrix yields zero. Verifies business objective 1. Evidence: executed negative-fixture demonstration in the CI run record from T-006.
2. Fixture copies missing the line-1 supersession marker, missing a `Status:` banner, or containing an enumerated coercive formulation each yield at least one failing check, while the current tree with the four banners landed yields zero failing checks. Verifies business objectives 1 and 3. Evidence: CI run record from T-006.
3. The content-contract checks are discovered and executed by the existing CI verification run with no CI configuration file modified. Verifies business objective 1. Evidence: CI run record from T-006 plus the review record from T-005.
4. A structure-preserving, wording-only edit to a governed document yields zero check failures. Verifies business objective 2. Evidence: reword demonstration defined in T-007 coverage and executed under T-006.
5. All four root governance documents carry their one-line `Status:` banner. Verifies business objective 3. Evidence: inspection recorded in the T-005 review record.

## Definition of Done

- [ ] Plan acceptance criteria 1 through 5 are verified with recorded evidence
- [ ] Planning, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for T-001 through T-008 are satisfied or formally waived
- [ ] A-001 through A-004 are confirmed or converted to recorded decisions
- [ ] R-001 through R-007 are closed or accepted with named owners
- [ ] Q-001 and Q-002 are closed or explicitly accepted
- [ ] `tests/` green and all `verify_*.py` proof scripts PROVEN are recorded as closure evidence
- [ ] `user-guide.html` is updated to match the touched documents, or the no-impact review is recorded
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Does the coercive auto-chain pattern inventory need to cover formulations beyond the four enumerated — skip, bypass, or auto-approve a gate, or proceed without approval — and if so, which? Carried forward from the approved scope definition; needed before the Design Gate. | No | architect | T-001, T-002 |
| Q-002 | What one-line `Status:` text does each of the four root governance documents carry, per the CKA-05 definition? Carried forward from the approved scope definition; needed before banner authoring. | No | omn-product-owner | T-003, T-004 |

## Traceability Matrix

Statements are normalized from the supplied feature request in document order. Context statements assert no requirement and require no task.

| Statement | Covered by |
|---|---|
| S-001 — ticket identity: CKA-04, Epic A (Verification baseline, Days 0–30), sourced from recommendation 5 of the adoption review dated 2026-08-27; type Task, priority High, effort S (context) | context; no task required |
| S-002 — CKA-04 depends on nothing and lands with or before CKA-03, already delivered as `.github/workflows/verify.yml` (constraint) | A-001, T-006 |
| S-003 — the runtime depends on structural properties of governance prose that nothing pins today (context) | business objective 1; T-001, T-002 |
| S-004 — `framework_runtime.py` reads gate ownership from `workflows/workflow-gate-matrix.md` and enforces the Producer Exclusion Rule through `producer_aliases()`; a producer-only row creates an undecidable gate unnoticed (context) | T-001, T-002 |
| S-005 — superseded agent specifications (`agents/architect.md`, `agents/planner.md`) carry their supersession marker in their first heading; a rewrite dropping it silently revives a dead contract (context) | T-002 |
| S-006 — agent contract modules must never carry coercive auto-chain language (outcome) | T-001, T-002 |
| S-007 — the four orphaned root governance documents receive `Status:` banners under CKA-05 that must then be impossible to drop (outcome) | T-003, T-004, A-002 |
| S-008 — deliverable: new `tests/test_content_contracts.py` on stdlib `unittest`, discovered by the CKA-03 CI test surface with no configuration change (constraint) | T-002, T-006, A-001 |
| S-009 — check 1: every gate-matrix gate row names at least one owner outside the producing agent's alias set (outcome) | T-002 |
| S-010 — check 2: superseded agent files carry their status marker on line 1 (outcome) | T-002 |
| S-011 — check 3: the four root governance documents carry a `Status:` banner; the check is authored now and green on the current tree; the coupling resolution was decided upstream (outcome) | T-002, T-003, T-004, A-003 |
| S-012 — check 4: no agent contract module under `agents/*/` matches coercive auto-chain patterns, enumerated as skip, bypass, or auto-approve a gate, or proceed without approval (outcome) | T-001, T-002, Q-001 |
| S-013 — assert on structure (table cells, first-line markers), not sentences, so structure-preserving wording edits stay free (constraint) | T-002, T-005, T-007 |
| S-014 — acceptance: mutating a fixture gate matrix to a producer-only owner row fails a test (outcome) | T-002, T-006, T-007 |
| S-015 — acceptance: suite runs green against the current tree once the banner portion lands (outcome) | T-004, T-006 |
| S-016 — additive change only: no alteration to `record_gate_decision`, gate-matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path; no runtime behavior change (constraint) | T-005; out-of-scope boundary |
| S-017 — assertions bind to structure the code reads, not prose wording (constraint) | T-005, T-007 |
| S-018 — definition of done: `tests/` green, all `verify_*.py` proof scripts PROVEN, no gate-decision behavior change, `user-guide.html` updated where docs were touched (constraint) | T-006, T-008 |
| S-019 — high priority; Phase 1 (Days 0–30) of the adoption plan (context) | context; no task required |
| S-020 — CKA-16 later extends this suite; CKA-05's acceptance criterion is pinned by CKA-04 (context) | business objective 3; out-of-scope boundary |
