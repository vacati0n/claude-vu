# Architecture Decision Record

## Metadata

- ADR ID: D-002
- Title: Blocking authority in the branch-protection required-checks list; advisory standing as absence from that list
- Date: 2026-09-04
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners)
- Related Work Items: CKA-03 (adoption backlog under `docs/`); execution plan tasks T-004, T-006, T-007 (consumers)

## Context

- Problem statement: the staged rollout requires the ubuntu unit-test check to block from day one while the verifier checks and the windows checks are advisory for the first week after merge and required thereafter — and the encoding must keep advisory failures visible, keep the flip auditable, and survive verifier-file additions without blocking-configuration changes.
- Business and technical constraints: C-008 (staged rollout with visible advisory failures), C-009 (no permanently red required check), C-010 (file additions require no CI configuration change, including no blocking-configuration change), C-005 (additive only).
- Current architecture baseline: F-010 (no CI configuration exists today, so no blocking contract exists to preserve); A-001 (the hosting platform supports branch protection requiring named checks); D-001 establishes stable per-platform fan-in check names and per-platform unit-test check names, with per-verifier names dynamic.

## Decision

- Selected option: O-001's blocking composition (per the evaluation table in section 5.2 of the technical design).
- Decision statement: blocking authority lives solely in the branch-protection required-checks list. At merge, the list names only the ubuntu unit-test check. Advisory standing for the verifier fan-in checks and the windows unit-test check is encoded as their absence from the list: they run and report — a failure shows red — but do not block. The flip at the end of week one is a settings-only change adding the two fan-in names and the windows unit-test name to the list, with no workflow edit. The per-job failure-tolerance flag (continue-on-error) is not used anywhere. The flip is enacted by the owner, and recorded in the location, that the tech lead's dedicated decision names (Q-001 in the design; the plan's flip-ownership task).
- Scope of impact: M-002 (the required-checks configuration), binding to the check names M-001 exposes; documented via M-008.

## Alternatives Considered

1. O-002's encoding — advisory standing as the workflow's per-job failure-tolerance flag for week one, removed by a workflow edit at the flip
- Benefits: the policy is visible inside the workflow file itself; no branch-protection administration is needed until the flip.
- Risks: the flag reports a failing advisory job as a passing check, hiding exactly the week-one failures the advisory window exists to observe; the flip becomes a workflow semantic change requiring a reviewed edit, a second contract-affecting transition.
- Why not selected: it defeats the advisory week's evidentiary purpose (the flip decision and the recovery-proof flake-rate evidence in R-001 depend on visible red), and it doubles the migration burden (2 versus 1 in the evaluation table).

2. O-003 — curated per-verifier jobs, each individually listed as a required check after the flip
- Benefits: the strongest conceivable blocking granularity, one required check per verifier.
- Risks: every verifier addition or rename requires a blocking-configuration edit; a forgotten edit silently un-gates the new verifier.
- Why not selected: eliminated on hard constraints C-002 and C-010; blocking must bind to stable names, which is why the fan-in checks exist (D-001).

## Consequences

- Positive outcomes expected: advisory failures are visibly red all week, producing the evidence the flip decision needs; the flip is one atomic, auditable, reversible settings change; verifier additions never touch blocking configuration because the required names are the stable fan-ins; the day-one required set is exactly the ubuntu unit-test check, as the ticket demands.
- Tradeoffs accepted: blocking truth lives in platform settings rather than in the versioned workflow file, so the workflow alone does not evidence the policy — mitigated by recording the check-name contract in section 6 of the design and publishing the policy, names, and standings in contributor documentation with handbook parity (P-008).
- Risks introduced: R-005 (a job rename detaches the required list — a renamed required check blocks forever as "expected", or blocking silently lapses); the plan's stall risk if no enactor is recorded (Q-001).

## Validation Plan

- Metrics to monitor: the required-checks list contents at merge and after the flip versus the design's stated sets; advisory-week failure visibility (red, non-blocking) on at least one observed failing advisory check.
- Verification checkpoints: the demonstration that a failing advisory check does not block a pull request during week one; the post-flip observation that the fan-in and windows checks are required; the flip record existing in the location the tech lead's decision names — per P-005 and P-007 of the design.
- Rollback or reversal conditions: removing the added names from the required list restores the advisory standing at any time with no workflow change; if a required check name detaches (R-005), the immediate reversal is removing the stale name from the list while the rename is corrected.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
