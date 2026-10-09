# Architecture Decision Record D-002

## Metadata

- ADR ID: D-002
- Title: Resolve the tier at dispatch from recorded run state and carry it in an additive envelope record
- Date: 2026-10-08
- Status: Proposed
- Owners: omn-tech-lead (Design Gate owner who accepts), architect (author)
- Related Work Items: run-ded114f50a46 design package, impacted modules M-001, M-003, M-009, M-010; planner tasks T-006, T-008, T-009

## Context

- Problem statement: a cheaper attempt that fails its validator, or whose gate is rejected and rolled back, must never be retried at the same tier, and the result must be the same whether the next dispatch happens in the same session or in a fresh one. The tier must reach the dispatching session without changing any original envelope field.
- Business and technical constraints: C-004 (additive envelope, deterministic from run state), C-005 (undeclared inherits, no verifier changes outcome), C-006 (promotion-only, capped at deep, identical across sessions), C-011 (replay-stable artifacts), C-012 (per-tier metrics sum to totals), C-013 (no gate or validator weakened).
- Current architecture baseline: F-002 (additive envelope rule), F-008 (append-only recovery ledger, resolved entries kept), F-009 (a validator rejection is ledgered under the phase with reason code validation_failed; a missing artifact is an uncharged transport failure), F-010 (supersessions list and gate rejection ledgered under the gate), F-011 (invocation_started events), F-012 (envelope rewritten per dispatch), F-018 (prompt and console surfaces).

## Decision

- Selected option: O-001
- Decision statement: at each dispatch the runtime derives the tier as a pure function of the declared tier and of two recorded counts for the phase: validator rejections, read from recovery-ledger entries under the phase's state id with the validation-failed reason code, and gate rejections with rollback, read from the supersessions list of the phase's work item. The resolved tier is the declared tier raised by one step per recorded rejection and capped at deep; a tier is never lowered. A transport failure, which produced nothing to judge, is not counted. The result is written as one additive model_tier record in the envelope carrying tier, host hint, basis, and escalation with its reason (rejection kinds and counts), copied as tier and an escalated flag into the invocation_started event, and shown on one line of the dispatch prompt and console output. Nothing is held in memory between dispatches.
- Scope of impact: M-001 (resolver, record, event detail, prompt line), M-003 (per-tier metrics read the record and the event), M-009 and M-010 (read only, unchanged), M-006 (field documented).

## Alternatives Considered

1. O-005 Abstract labels with a label-to-alias table in runtime code
- Benefits: the envelope hint would be a translated value.
- Risks: model identifiers in runtime logic, and a second place the hint must be maintained.
- Why not selected: violates C-003 and is eliminated; the record copies the declared hint verbatim.

2. O-006 Escalation counted by in-memory attempt counters of the dispatching session
- Benefits: no ledger read.
- Risks: a fresh session loses the count, so a rejected cheaper attempt could be retried at the same tier.
- Why not selected: violates C-006 and is eliminated.

## Consequences

- Positive outcomes expected: escalation is reproducible from persisted files, an in-session and a fresh-session dispatch agree, and historical envelopes without the record stay valid.
- Tradeoffs accepted: the rejection count depends on the ledger and supersession records keeping their current meaning; a gate rejection that is not rolled back does not promote, because the phase is not dispatched again.
- Risks introduced: R-003 (new field or event detail disturbs a replay comparison), R-004 (the count reads the wrong entries), R-001 (a promoted standard phase lowers the non-deep share).

## Validation Plan

- Metrics to monitor:
  - Per-tier invocations and the non-deep share from the execution metrics of each run.
  - Count of rejected attempts retried at the same tier, expected zero.
- Verification checkpoints:
  - After a validator rejection and after a gate rejection with rollback, the next envelope shows one tier higher with a reason naming the rejection kind; a deep phase stays deep.
  - A dispatch built from recorded state alone yields the same record as the in-session dispatch.
  - Original envelope fields match a pre-change envelope for the same run state, and every existing verifier returns its recorded baseline.
- Rollback or reversal conditions:
  - Remove the resolver call and the record if replay stability or any existing verifier leaves its baseline; envelopes written before the change are unaffected and the declaration file can stay unused.

## Approval

- Architect: unsigned; the producing agent does not accept its own record.
- Tech Lead: pending the Design Gate decision.
- Product Owner (if scope-impacting): not required; scope is unchanged.
