# Architecture Decision Record

## Metadata

- ADR ID: D-003
- Title: Pre-existing orphan run directories handled clean-first, with the advisory week as buffer and a green-run flip precondition
- Date: 2026-09-04
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners)
- Related Work Items: CKA-03 (adoption backlog under `docs/`); execution plan tasks T-007, T-010 (this record decides T-010's question; T-007 consumes the precondition)

## Context

- Problem statement: three pre-existing orphan run directories dated 2026-08-27 fail the self-hosting proof's S8 run-accounting check. Once the verifier surface reports in CI, that verifier is red at every revision carrying the orphans. The ticket names two handlings — the advisory window absorbs the failures, or the orphans are cleaned first via the existing follow-up task — and requires the design to select one so that no required check ships permanently red.
- Business and technical constraints: C-009 (no permanently red required check on account of the orphans; the handling is stated), C-008 (the verifier checks become required at the end of week one), C-005 (this change is additive and does not itself perform cleanup), C-002 (no by-name exemption of a verifier — exemption is curation).
- Current architecture baseline: F-008 (the S8 check fails on any unaccounted run in the working tree's runs area), F-014 (the three orphans exist and an existing follow-up task owns their cleanup); A-003 (the cleanup task can land before the end of the advisory week); A-004 (the orphans are the only pre-existing verifier-failing state at the merge revision).

## Decision

- Selected option: the clean-first handling as bundled in O-001 (per the evaluation table in section 5.2 of the technical design).
- Decision statement: the orphans are cleaned first, via the existing follow-up task, which is scheduled to land on the default branch before the advisory-to-required flip; the advisory week is the buffer that makes the interim red self-hosting check non-blocking, not the handling itself. The condition that must hold at the flip: a default-branch workflow run at the flip revision shows the self-hosting proof passing (its S8 check green). The flip enactor named by the tech lead's ownership decision verifies that condition against recorded verification evidence before enacting the flip; if it does not hold, the flip is deferred (P-007), never enacted red. Scheduling dependency: this decision creates a sequencing dependency of the flip on the existing cleanup follow-up task (P-006), which remains owned outside this change.
- Scope of impact: M-009 (the orphan directories, read by the verifier surface), M-002 (the flip precondition), with the cleanup work itself out of this change's scope (C-005).

## Alternatives Considered

1. O-004 — advisory-window-only handling: the run-accounting verifier stays red through the advisory week, and the flip proceeds by exempting or accepting the red required check
- Benefits: no scheduling dependency on the cleanup task; the workflow ships with zero coordination.
- Risks: at the flip, either a permanently red required check blocks every pull request, or the failing verifier is exempted by name — which is curation and silently un-gates the self-hosting proof indefinitely.
- Why not selected: eliminated on hard constraint C-009; the advisory window only defers the problem to the flip date, it does not resolve it. The exemption path additionally violates C-002.

2. O-002 / O-003 (topology alternatives carrying the same orphan question)
- Benefits: not applicable to this decision — both topologies face the identical orphan condition.
- Risks: identical: any topology whose verifier surface includes the self-hosting proof is red at revisions carrying the orphans.
- Why not selected: the topology choice (D-001) does not discriminate on this question; they are recorded here because the package evaluation table bundles the orphan handling into the option rows, and every non-selected row was considered.

## Consequences

- Positive outcomes expected: the verifier surface reaches the flip green; the self-hosting proof's run-accounting check becomes a trustworthy required gate rather than a permanently exempted one; the advisory week doubles as the window in which the cleanup lands and its effect is observed on real runs.
- Tradeoffs accepted: the flip date acquires an external scheduling dependency (A-003) on a task this change does not own; if that task slips, the rollout policy's week-one date slips with it — deferral was chosen over exemption deliberately.
- Risks introduced: R-002 (the cleanup lands late and the flip is deferred), R-007 (failures beyond the orphans exist and the green-run precondition stays unmet for other reasons; the advisory week exists to surface them).

## Validation Plan

- Metrics to monitor: the self-hosting proof's result on default-branch runs across the advisory week — red while the orphans persist, green after the cleanup lands.
- Verification checkpoints: the cleanup change observed merged to the default branch (P-006); one default-branch run at the flip revision with the self-hosting proof passing, verified by the flip enactor against the plan's recorded verification evidence before the flip (P-007).
- Rollback or reversal conditions: if the precondition cannot be met within an acceptable deferral, the reversal is to keep the fan-in checks advisory (never exempting the verifier by name) and escalate the cleanup's scheduling to the delivery owner; no state introduced by this decision needs unwinding, because the decision performs no cleanup itself.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
