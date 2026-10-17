# Architecture Decision Record: D-003

## Metadata

- ADR ID: D-003
- Title: The hydration choice is a run-level record written once at run creation
- Date: 2026-10-09
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-c9fb8d5bbb32; technical-design.md; T-013, T-017, T-007

## Context

- Problem statement: runs planned after the change hydrate by default and may switch it off, while runs planned before it must never hydrate and must never be inferred to.
- Business and technical constraints: recorded at plan time in run state, never inferred, absent means never (C-011); the execution-plan contract and validator stay unchanged (C-009); pre-change dispatch stays byte-identical (C-006).
- Current architecture baseline: execution-request.json is written once at run creation and never rewritten, and only command_id is read back (F-005); RUNTIME_VERSION is 0.9.0 (F-018).

## Decision

- Selected option: O-001.
- Decision statement: at run creation only, runtime/framework_runtime.py (M-002) writes knowledge_loop with hydration on or off and a basis into execution-request.json; the default is hydration_default in config/knowledge-policy.json (M-005); the flag --no-lesson-hydration records off; an absent record is a pre-change run that never hydrates; the flag against an existing run whose record disagrees is a request-validation-failure.
- Scope of impact: M-002, M-005; read by M-001 at aggregation.

## Alternatives Considered

1. O-005: record the choice in the execution-plan artifact
- Benefits: the planner states it beside the plan.
- Risks: changes an artifact contract and its validator.
- Why not selected: eliminated by C-009, C-011.

2. O-006: infer the choice at dispatch from the run's runtime_version
- Benefits: no new record.
- Risks: a dispatch-time inference the ruling forbids; no off switch.
- Why not selected: eliminated by C-011.

## Consequences

- Positive outcomes expected: the default is stated once, in the policy file; pre-change runs are identified by absence alone.
- Tradeoffs accepted: the choice cannot be changed after creation; a run needing the other setting is a new request.
- Risks introduced: R-004, R-015.

## Validation Plan

- Metrics to monitor: share of new runs recorded on and off; refusals of a conflicting flag.
- Verification checkpoints: AC-019 tests; AC-018 baseline comparison for a pre-change fixture (P-012).
- Rollback or reversal conditions: setting hydration_default to off reverses the default for new runs without touching recorded runs; reverting the runtime leaves the key unread.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): Q-001 only
