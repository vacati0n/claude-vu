# Scope Definition: Content-contract tests over governance prose

```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0004
  featureName: Content-contract tests over governance prose
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-04-feature-request.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 9
  inputDigest: sha256:f63a8c3a43a79d5c0d1f218ebe85bbf6
  contextDigest: sha256:c5cc1c3bdd1db9b2d550e98fd7f931ed
```

## Metadata

- Feature name: Content-contract tests over governance prose
- Requested by: Adoption backlog ticket CKA-04 (Epic A — Verification baseline, Days 0–30), sourced from recommendation R5 of the adoption review dated 2026-08-27, per the adoption backlog under docs/
- Business goal: Edits to governance prose can no longer silently break the structural guarantees that gate governance depends on
- Target outcome: Every structural property the runtime reads from governance prose is pinned by an automated check that fails when the property is broken and stays green when only wording changes
- Scope decision date: 2026-09-04

## Business Context

- Problem statement: The runtime depends on structural properties of governance prose — gate-matrix rows owned by someone other than the producing role, supersession markers on the first line of superseded agent specifications, `Status:` banners on the four orphaned root governance documents, and the absence of coercive auto-chain language in agent contract modules — and nothing pins any of them today; a prose edit can create an undecidable gate, silently revive a dead contract, drop a status banner, or introduce gate-bypassing instructions, and no check notices
- Value hypothesis: Pinning these properties with automated verification turns silent governance decay into an immediate, visible failure before it lands, protecting the gate-decision guarantees the framework's delivery model rests on
- Affected users: Framework maintainers who edit governance prose, and every operator and downstream agent whose runs depend on gates remaining decidable and agent contracts remaining honest
- Success measure: The two verbatim ticket criteria hold — a fixture gate matrix mutated to a producer-only owner row fails a check, and the suite runs green against the current tree with the four banners landed — while wording edits that preserve structure produce no failure

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | Every continuous-integration verification run automatically checks the structural properties of governance prose that the runtime depends on, so an edit that breaks a pinned property is reported as a failing check before it lands | Delivers the request's core deliverable: a content-contract test suite discovered by the existing CKA-03 CI test surface | must-have |
| `S-002` | A gate-matrix edit that leaves any gate row owned only by its producing role, under the Producer Exclusion Rule's alias reading, is reported as a failing check | Delivers request check 1: no gate row is producer-only through any alias of the producing agent | must-have |
| `S-003` | A rewrite of a superseded agent specification that drops the supersession status marker from its first line is reported as a failing check | Delivers request check 2: superseded agent files carry their status marker on line 1 | must-have |
| `S-004` | Removal of the `Status:` banner from any of the four root governance documents (`working-memory.md`, `rule-engine.md`, root `quality-gates.md`, `decision-matrix.md`) is reported as a failing check | Delivers request check 3: the four root governance docs carry a `Status:` banner that is thereafter impossible to drop unnoticed | must-have |
| `S-005` | An agent contract module that instructs skipping, bypassing, or auto-approving a gate, or proceeding without approval, is reported as a failing check | Delivers request check 4: no agent contract module carries coercive auto-chain language | must-have |
| `S-006` | Each of the four root governance documents carries a one-line `Status:` banner, so the banner check passes on this change's tree without activation logic | Scoped in by `D-001` to satisfy the request's requirement that the banner check be authored now and be green on the current tree | must-have |
| `S-007` | Published user documentation remains consistent with the governance documents this change touches | The ticket's definition of done requires `user-guide.html` updated to match where docs were touched; `D-001` makes the four banner additions doc touches | must-have |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Any modification to gate-decision runtime behaviour: `record_gate_decision`, the gate-matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path | The ticket forbids it explicitly; this change is additive, adding checks and, per `D-001`, four one-line banners | A separate change request explicitly targeting gate-decision behaviour is raised and routed |
| `X-002` | Changes to CI configuration or the verification workflow to register the new checks | The request requires discovery by the existing CKA-03 test surface with no configuration change | The existing test surface stops discovering the suite |
| `X-003` | Assertions that bind to sentence wording of governance prose | The request directs assertions on structure only, so wording edits that preserve structure stay free | A future requirement identifies specific wording as load-bearing for the runtime |
| `X-004` | CKA-05 content beyond the presence of the four one-line `Status:` banners | Only banner presence is needed for the banner check to be green; the remainder of CKA-05 stays its own change, per `D-002` | CKA-05 is scoped and delivered in its own right |
| `X-005` | The anti-rationalization table checks that CKA-16 later adds to this suite | CKA-16 is a separate backlog ticket that extends this suite in a later phase | CKA-16 enters scoping |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | The content-contract checks are discovered and executed by the existing CI verification run with zero changes to CI configuration files | `S-001` | Review of the CI run record showing the suite executed, plus change review confirming no CI configuration file was modified | must-have |
| `A-002` | The full check suite passes against this change's tree, with the four banners landed: zero failing checks | `S-001` | Execution of the suite in the CI verification run on the change's tree | must-have |
| `A-003` | A wording-only edit to a governed document that preserves the pinned structure produces zero check failures | `S-001` | Demonstration against a structure-preserving reworded fixture copy of a governed document | must-have |
| `A-004` | Mutating a fixture gate matrix so one row's owners all fall within the producing role's alias set yields at least one failing check, while the unmutated matrix yields zero | `S-002` | Executed negative-fixture demonstration within the check suite | must-have |
| `A-005` | A fixture copy of a superseded agent specification with the status marker absent from line 1 yields at least one failing check; the current superseded specifications yield zero | `S-003` | Executed negative-fixture demonstration plus the suite run against the current tree | must-have |
| `A-006` | A fixture copy of any of the four root governance documents with its `Status:` banner removed yields at least one failing check; the four documents as landed yield zero | `S-004` | Executed negative-fixture demonstration plus the suite run against the change's tree | must-have |
| `A-007` | A fixture agent contract module containing any enumerated coercive formulation — skip, bypass, or auto-approve a gate, or proceed without approval — yields at least one failing check; the current agent contract modules yield zero | `S-005` | Executed negative-fixture demonstration plus the suite run against the current tree | must-have |
| `A-008` | All four root governance documents carry a one-line `Status:` banner: four of four present | `S-006` | Inspection of the four documents on the change's tree | must-have |
| `A-009` | `user-guide.html` matches the touched governance documents: it is updated to reflect the banner additions, or a documentation review records that no user-guide content is affected by them | `S-007` | Documentation review comparing `user-guide.html` against the four touched documents | must-have |

## Constraints and Dependencies

- Business constraints: High priority; Phase 1 (Days 0–30) of the adoption plan; CKA-16 later extends this suite, and CKA-05's acceptance criterion ("present and pinned by CKA-04") is pinned by this change
- Regulatory or policy constraints: Additive change only — no alteration to `record_gate_decision`, the gate-matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path; no change to runtime gate-decision behaviour
- Delivery constraints: The requested deliverable is a new `tests/test_content_contracts.py` on stdlib `unittest`, discovered by the CKA-03 CI test surface with no configuration change; the ticket's definition of done applies — `tests/` green, all `verify_*.py` proof scripts PROVEN, no change to gate-decision behaviour, and `user-guide.html` updated to match where docs were touched
- External dependencies: The CKA-03 CI test surface, already delivered as `.github/workflows/verify.yml`; the CKA-05 banner coupling is resolved inside this change per `D-001`, so no external landing order remains

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | The four one-line CKA-05 `Status:` banners land inside this change, and the banner check is authored unconditional — no activation gating | The request requires the check authored now and green on the current tree; of the two admissible resolutions the backlog offers, an activation-gated check would leave the banner protection dormant and permanently green on a tree where no banner ever lands, defeating the stated outcome that the banners must be impossible to drop; the banner addition is S-effort, dependency-free, CKA-05's own acceptance criterion is "present and pinned by CKA-04", and the ticket's constraint text expressly admits the banners as scope | This change touches four governance documents in addition to adding checks; the verbatim criterion "suite runs green against current tree once CKA-05 lands" is satisfied within this change because the banner portion of CKA-05 lands here; the definition-of-done documentation obligation is triggered (`S-007`); no activation logic exists that would later have to be removed | omn-product-owner |
| `D-002` | Only the presence of the four one-line `Status:` banners is scoped in from CKA-05; nothing wider | The banner check needs banner presence and nothing more; the narrowest boundary that delivers the stated outcome excludes the remainder of CKA-05 | CKA-05 remains open for anything beyond banner presence; the non-goal boundary is recorded as `X-004` | omn-product-owner |
| `D-003` | The coercive auto-chain check's acceptance threshold is set on the enumerated example formulations — skip, bypass, or auto-approve a gate, or proceed without approval; the complete pattern inventory is deferred to technical design | The request states the patterns by example rather than exhaustively; fixing scope to the enumerated set keeps `A-007` verifiable while leaving the inventory to the phase that owns it | `A-007` is decided against the enumerated formulations; the inventory may widen during design without a scope change; `Q-001` records the review | omn-product-owner |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | Does the coercive auto-chain pattern inventory need to cover formulations beyond the four enumerated — skip, bypass, or auto-approve a gate, or proceed without approval — and if so, which? | no | architect | before the technical design is approved |
| `Q-002` | What one-line `Status:` text does each of the four root governance documents carry, per CKA-05's definition? | no | requester | before implementation of the banner additions |

## Handoff

- Downstream owner: `planner`, after the Scope Gate; `architect` and `omn-qa` consume the acceptance criteria
- Gate: Scope Gate, decided by `omn-business-analyst` under the Producer Exclusion Rule; no gate decision is recorded here
- Evidence for the gate: scope items `S-001`–`S-007`, exclusions `X-001`–`X-005`, acceptance criteria `A-001`–`A-009`, scope decisions `D-001`–`D-003`, open questions `Q-001`–`Q-002`, and the verdict `bounded` they support
- Deferred to downstream: decomposition into tasks and sequence (`planner`); the technical approach, including fixture design and the full coercive-pattern inventory (`architect`); the validation strategy that executes the named verification methods (`omn-qa`); authoring the checks and the four banner lines (implementation)
