# Architecture Decision Record

## Metadata

- ADR ID: D-001
- Title: The memory token optimizer entry point routes to the existing refactor lifecycle
- Date: 2026-08-28
- Status: Proposed
- Owners: architect (author), omn-tech-lead (Design Gate)
- Related Work Items: OMT-01; modules `M-002`, `M-003`, `M-007`; sequencing constraint `P-004`

## Context

- Problem statement: The framework gains an entry point that rewrites its durable knowledge surfaces and claims that nothing they instruct has changed. Every entry point must resolve to exactly one primary workflow (`C-001`). The question is whether that workflow is a new one built for this entry point, or one the framework already has.
- Business and technical constraints: `C-001` requires exactly one primary workflow holding an active discovery record. `C-002` forbids adding a workflow, phase, gate row, role manifest entry, or artifact validator. `C-008` requires existing verifier results to move by the one added contract and nothing else.
- Current architecture baseline: `F-001` records ten contracts with active records, and that a contract on disk with no record fails coverage. `F-002` records that two contracts already share a primary workflow with another contract, so sharing is established. `F-003` records that the `refactor` workflow declares five phases and all five are dispatchable. `F-004` records that all thirty-seven phases across eight workflows are dispatchable, so no capability is missing that a new workflow would supply.

## Decision

- Selected option: `O-001`.
- Decision statement: The entry point's discovery record names `refactor` as its primary workflow. The claim the entry point makes — that wording changed and meaning did not — is the invariant claim that workflow exists to hold to account: `scope-invariants-and-risk-profile` states what may not change and `behavioral-validation` checks that it did not. No workflow, phase, gate, role, or validator is added.
- Scope of impact: `M-003` gains one record. `M-002` supplies the contract that record resolves to. `M-007` is recorded as no-change-verified: the shared workflow itself does not change, and coverage verification decides that rather than the author asserting it.

## Alternatives Considered

1. Option `O-002` — a dedicated lifecycle for the entry point
- Benefits: Phase names could be worded for this work specifically, and the lifecycle would be free to diverge later without affecting another contract.
- Risks: Adds five phases, gate rows requiring non-producing owners, role manifest entries, context slices, and an artifact validator, each a permanent maintenance obligation. Restates an invariant claim the framework already models, so two lifecycles would answer the same question.
- Why not selected: Violates `C-002`, and buys nothing: the existing five phases map to this work exactly, with none missing and none unused.

2. Option `O-003` — no entry point; a maintenance script run outside the framework
- Benefits: The smallest possible change, one module and nothing else.
- Risks: Nothing governs the script, so the denial boundary `C-003` requires has nothing to bind it, and no contract states any guarantee for a reader to rely on.
- Why not selected: Violates `C-003` and `C-004`. The capability would sit outside every control that makes rewriting trusted surfaces safe.

## Consequences

- Positive outcomes expected: The capability costs one discovery record. The five phases, their gates, their owners, and their validators are inherited rather than rebuilt, so the framework's phase, owner, skill, and gate counts do not move.
- Tradeoffs accepted: The entry point cannot express a phase the `refactor` workflow does not have. Accepted because none is needed, and gaining one later is a smaller change than carrying five unused ones now.
- Risks introduced: `R-006` — if adding a contract to a shared workflow disturbs that workflow, its gates, or its owning roles (`A-003` false), the change becomes a lifecycle change, which `C-002` forbids.

## Validation Plan

- Metrics to monitor: The active command record count, which must rise by exactly one; the phase, phase-owner, skill-reference, and gate-reference counts, each of which must not move.
- Verification checkpoints: Coverage verification after registration, per `P-005`, comparing every check against the baseline recorded before the change; resolution of the new record to its contract on disk and to an active workflow record.
- Rollback or reversal conditions: Reverse if coverage verification shows any count other than the command record count moving, or if the shared workflow requires any edit to accept the second contract. Reversal is removal of the record and the contract together; a partial removal is detected by coverage check `C1`.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
