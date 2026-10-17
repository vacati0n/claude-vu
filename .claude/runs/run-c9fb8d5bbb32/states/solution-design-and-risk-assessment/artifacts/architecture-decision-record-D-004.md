# Architecture Decision Record: D-004

## Metadata

- ADR ID: D-004
- Title: Lessons reach a dispatch only outside the payload digest
- Date: 2026-10-09
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-c9fb8d5bbb32; technical-design.md; T-006, T-007, T-014, T-015

## Context

- Problem statement: lessons must reach the agent in envelope and prompt, while the idempotency key must stay exact for pre-change runs and stable across retries and rollbacks of every run, even when the store changes between attempts.
- Business and technical constraints: byte-identical pre-change dispatch and exact key (C-006); no context-slice member edited (C-007); lesson data never in context_slice, input_contract, or the payload digest (C-008); bounded, labelled rendering (C-005, C-012).
- Current architecture baseline: the payload digest is built from context digest, input digest, agent version, and canonical path (F-002); a changed payload on an active item raises context-integrity-failure (F-003); memory_slice is a literal outside the digest (F-001); the model tier field set the additive-outside-digest precedent (F-016).

## Decision

- Selected option: O-001.
- Decision statement: runtime/framework_runtime.py (M-002) places lessons only in memory_slice, in an optional bounded prompt section present only when lessons are shown, and in a lessons_shown key of the invocation_started detail emitted only for runs with a knowledge_loop record; it reads the record after replay detection and payload binding; runs with no record emit today's literal and nothing else new.
- Scope of impact: M-002, M-003 (reads lessons_shown), M-001 (selection).

## Alternatives Considered

1. O-004: the store joins the context slice or the inputs
- Benefits: agents read lessons through the existing slice mechanism.
- Risks: every store change moves the context digest, the payload digest, and the key; an active item re-dispatched after a harvest fails integrity.
- Why not selected: eliminated by C-008, C-006.

2. O-002: same carriers under a different module boundary
- Benefits: identical carriers.
- Risks: as recorded under D-001.
- Why not selected: loses on criterion 4 (C-024).

## Consequences

- Positive outcomes expected: keys are reproduced exactly; M12 and M14 run unmodified; a retry after a harvest still matches its payload.
- Tradeoffs accepted: the context-slice exclusion text stays unchanged even on hydrated runs.
- Risks introduced: R-001, R-007, R-014.

## Validation Plan

- Metrics to monitor: idempotency key equality against the baseline; prompt section line count.
- Verification checkpoints: AC-014 to AC-018 tests; verify_multi_phase M12 and M14 (P-012).
- Rollback or reversal conditions: any baseline mismatch on the absent-record path blocks the Review Gate until the leak is removed.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
