# Architecture Decision Record: D-001

## Metadata

- ADR ID: D-001
- Title: The knowledge loop is a dedicated standard-library runtime module with its own command line
- Date: 2026-10-09
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-c9fb8d5bbb32; technical-design.md; T-002, T-003, T-004, T-005, T-007, T-009

## Context

- Problem statement: harvest, store governance, eligibility, recall selection, and effectiveness accounting have no implementation (F-017), and the dispatch runtime emits only a literal memory slice (F-001).
- Business and technical constraints: standard library only, no model call (C-010); additive only (C-009); the loop must be testable apart from the dispatch runtime (C-024); metrics must not import the dispatch runtime (F-015).
- Current architecture baseline: runtime/framework_runtime.py is the single dispatch and aggregation module (F-008); execution_metrics.py reads evidence directly and imports nothing from it (F-015).

## Decision

- Selected option: O-001.
- Decision statement: runtime/knowledge.py (M-001) owns harvest, store, governance, eligibility, recall selection, and the effectiveness report, exposes the subcommands harvest, list, approve, retire, annotate, recall, report, depends only on the standard library and the state_engine digest helper, and imports nothing from runtime/framework_runtime.py (M-002), which calls it one-way at plan, dispatch, and aggregation.
- Scope of impact: M-001 (new), M-002 (calls), M-003 (reads only event evidence), M-012 (tests).

## Alternatives Considered

1. O-002: all loop logic inside runtime/framework_runtime.py as subcommands
- Benefits: no new file; RunLedger reused directly.
- Risks: loop tests must import the whole runtime and its registry resolution; a report reused elsewhere would import the dispatch runtime.
- Why not selected: ties O-001 on hard constraints, impact surface, and reuse, and loses on criterion 4 (C-024).

2. O-003 to O-007: eliminated by hard constraints C-014, C-002, C-015, C-008, C-006, C-009, C-011 (technical-design.md, 5.2); none offers a structural alternative to the module boundary.
- Benefits: none retained.
- Risks: each violates a hard constraint.
- Why not selected: eliminated.

## Consequences

- Positive outcomes expected: the loop is unit-testable over temporary roots; installs gain a standalone command line; the dispatch runtime grows only by thin hooks.
- Tradeoffs accepted: event reading is duplicated in a few lines rather than reusing RunLedger, to keep the dependency one-way.
- Risks introduced: R-001, R-009.

## Validation Plan

- Metrics to monitor: import graph of M-001 (standard library and state_engine only); test count and pass rate of M-012.
- Verification checkpoints: review at the Review Gate confirms no import of M-002 from M-001 or M-003; the full suite passes (P-012).
- Rollback or reversal conditions: if the module boundary forces a second import path into the runtime, fold M-001 into M-002 per O-002 under a new record.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
