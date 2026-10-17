# Architecture Decision Record: D-004

## Metadata

- ADR ID: D-004
- Title: stale_after is written only for retained lessons and valued from last_seen
- Date: 2026-10-17
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-79276e78d773; technical-design.md; T-008, T-010

## Context

- Problem statement: The Scope Gate requires a stale_after rule derived from record fields only, with no wall clock, and "applies to none" only if justified; OKF defines stale_after as an absolute instant at or after which the document is stale.
- Business and technical constraints: every bundle byte derived from record fields, no write-time value (C-008); instants carry the Z offset (C-003); harvest eligibility and ranking unchanged (C-026).
- Current architecture baseline: harvest marks a lesson with no current evidence retained and re-derives evidence fields of current lessons at every harvest (F-008); every live lesson is current (F-011); §5.5 semantics (F-024).

## Decision

- Selected option: O-002.
- Decision statement: stale_after is present only when evidence_state is retained, with value last_seen, falling back to first_seen. A retained lesson's evidence has left the recorded runs, so it is stale from its last observed occurrence; a current lesson is re-derived at every harvest and carries no stale_after. Recall does not read the key. No migrated lesson carries it today.
- Scope of impact: M-002, M-003.

## Alternatives Considered

1. O-001: same rule implemented inside knowledge.py alone
- Benefits: none specific to the rule.
- Risks: check tied to the loop module.
- Why not selected: ranks second on criterion 4 (C-022).

2. O-003: bundle exported from the JSON store
- Benefits: rule could be applied at export only.
- Risks: two stores of record.
- Why not selected: eliminated by C-011.

3. O-004: record in a fenced JSON body block
- Benefits: none for the rule.
- Risks: fields not under their own key.
- Why not selected: eliminated by C-005.

4. O-005: third-party YAML library
- Benefits: none for the rule.
- Risks: new dependency.
- Why not selected: eliminated by C-016.

5. O-006: log.md appended at write time
- Benefits: none for the rule.
- Risks: time-dependent content.
- Why not selected: eliminated by C-006, C-008.

## Consequences

- Positive outcomes expected: a deterministic, meaningful staleness signal for third-party consumers with no wall clock; re-harvest stays byte-identical.
- Tradeoffs accepted: a current lesson never carries a staleness horizon; the key is absent from every document at migration.
- Risks introduced: none new; the acceptance criterion is open as Q-002.

## Validation Plan

- Metrics to monitor: documents carrying stale_after against lessons with evidence_state retained (expected equal).
- Verification checkpoints: the criterion is recorded under T-010 (P-002); a retained-lesson fixture and the migrated bundle checked in P-013.
- Rollback or reversal conditions: if omn-product-owner records a different criterion under Q-002, revise this rule under a new record before P-006.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): pending the T-010 criterion (Q-002)
