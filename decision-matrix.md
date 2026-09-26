# Engineering Decision Matrix

Status: specification — not implemented — executable counterpart: `workflows/workflow-gate-matrix.md`.

This document defines deterministic decision trees for key engineering domains.

## Global Rules

- Every decision step is binary: Yes or No.
- Every path ends in exactly one terminal action.
- If required data is missing at any step, outcome is `Escalate for missing input`.
- Priority order for conflicts: Security > Data Integrity > Availability > Performance > Developer Convenience.

---

## 1. Architecture

### Inputs

- Functional requirement documented
- Non-functional requirements (NFRs) documented
- SLA/SLO target documented
- Data classification documented
- Throughput and latency estimates documented

### Decision Tree

1. Is the data classification `Restricted` or higher?
- Yes -> 2
- No -> 3

2. Is zero-trust segmentation required by policy?
- Yes -> Outcome A1: Choose service decomposition with network isolation boundaries.
- No -> Outcome A2: Choose modular monolith with strict internal access controls.

3. Is expected peak throughput > 5x current baseline within 12 months?
- Yes -> 4
- No -> 5

4. Is team on-call maturity >= medium (24/7 ownership + runbooks + SLO alerting)?
- Yes -> Outcome A3: Choose distributed services aligned to domain boundaries.
- No -> Outcome A4: Choose modular monolith and scale vertically first.

5. Is p95 latency target < 100 ms for user-facing critical paths?
- Yes -> 6
- No -> 7

6. Is cross-domain transaction consistency required?
- Yes -> Outcome A5: Choose modular monolith with ACID boundaries.
- No -> Outcome A6: Choose service split with async event integration.

7. Is independent deployment cadence per domain required?
- Yes -> Outcome A7: Choose distributed services.
- No -> Outcome A8: Choose modular monolith.

---

## 2. Coding

### Inputs

- Task type (feature, bugfix, refactor)
- Risk level (low, medium, high)
- Affected components list
- Public API impact known

### Decision Tree

1. Does the change affect a public API contract?
- Yes -> 2
- No -> 3

2. Is a backward-compatible path available?
- Yes -> Outcome C1: Implement additive change + deprecation notice + migration note.
- No -> Outcome C2: Require versioned API change + approval from architecture owner.

3. Is the change touching auth, payment, or data write paths?
- Yes -> 4
- No -> 5

4. Is there an existing test harness for this path?
- Yes -> Outcome C3: Implement with tests first for critical path, then code.
- No -> Outcome C4: Build minimal harness, then implement with mandatory peer pairing.

5. Is cyclomatic complexity of modified function expected > 10?
- Yes -> Outcome C5: Refactor into smaller units before feature logic.
- No -> 6

6. Is duplicated logic introduced in more than one module?
- Yes -> Outcome C6: Extract shared utility/module before merge.
- No -> Outcome C7: Proceed with direct implementation.

---

## 3. Review

### Inputs

- PR size (lines changed)
- Risk label present
- Test evidence attached
- Change type (functional/non-functional)

### Decision Tree

1. Is PR risk labeled `high`?
- Yes -> 2
- No -> 3

2. Are two qualified reviewers assigned?
- Yes -> Outcome R1: Require dual approval including one domain owner.
- No -> Outcome R2: Block merge until reviewer set is complete.

3. Is diff size > 500 lines changed?
- Yes -> 4
- No -> 5

4. Is there a decomposition rationale in PR description?
- Yes -> Outcome R3: Allow review, but require checklist completion.
- No -> Outcome R4: Request split into smaller PRs before review.

5. Are failing checks present?
- Yes -> Outcome R5: Block merge until all required checks pass.
- No -> 6

6. Does PR modify production configuration or infrastructure code?
- Yes -> Outcome R6: Require ops/infrastructure reviewer approval.
- No -> Outcome R7: Standard approval path.

---

## 4. Testing

### Inputs

- Change scope
- Critical path impact
- Historical defect density
- Existing test coverage

### Decision Tree

1. Does the change affect critical user journey or revenue path?
- Yes -> 2
- No -> 3

2. Are integration tests covering the changed path?
- Yes -> Outcome T1: Run full integration + regression suite.
- No -> Outcome T2: Add integration tests, then run full suite.

3. Is historical defect density for the module above threshold?
- Yes -> 4
- No -> 5

4. Is property-based or fuzz testing feasible for input space?
- Yes -> Outcome T3: Add property/fuzz tests plus targeted regression tests.
- No -> Outcome T4: Expand edge-case table tests and regression tests.

5. Is code coverage delta negative for modified files?
- Yes -> Outcome T5: Add tests until coverage is non-negative.
- No -> 6

6. Is change non-functional only (docs/comments/refactor with no behavior change)?
- Yes -> Outcome T6: Run smoke tests + static checks only.
- No -> Outcome T7: Run unit + targeted integration tests.

---

## 5. Release

### Inputs

- Release type (patch/minor/major)
- Migration requirement
- Rollback plan
- Observability readiness

### Decision Tree

1. Does release include schema or data migration?
- Yes -> 2
- No -> 3

2. Is migration backward compatible with previous app version?
- Yes -> Outcome L1: Deploy app and migration in phased rollout.
- No -> Outcome L2: Use maintenance window + pre-approved rollback checkpoint.

3. Is canary environment available and healthy?
- Yes -> 4
- No -> Outcome L3: Block release until canary is healthy.

4. Are SLO dashboards and alerts green for baseline period?
- Yes -> 5
- No -> Outcome L4: Block release and remediate observability gaps.

5. Is rollback executable in <= 15 minutes and tested within last 30 days?
- Yes -> Outcome L5: Proceed with progressive rollout.
- No -> Outcome L6: Block release until rollback drill is completed.

---

## 6. Escalation

### Inputs

- Incident severity
- Customer impact
- Time-to-mitigate estimate
- Security involvement

### Decision Tree

1. Is there confirmed or suspected security breach?
- Yes -> Outcome E1: Trigger security incident process immediately.
- No -> 2

2. Is customer-facing outage > 15 minutes for critical service?
- Yes -> 3
- No -> 4

3. Is mitigation ETA <= 30 minutes with current responders?
- Yes -> Outcome E2: Continue incident response, update status every 15 minutes.
- No -> Outcome E3: Escalate to incident commander and executive on-call.

4. Is data integrity at risk (loss/corruption/inconsistent writes)?
- Yes -> Outcome E4: Freeze writes where possible and escalate to domain owner.
- No -> 5

5. Is repeated incident pattern observed 3+ times in 30 days?
- Yes -> Outcome E5: Escalate to engineering manager for corrective action plan.
- No -> Outcome E6: Handle in normal support queue.

---

## Terminal Outcomes Index

- Architecture: A1-A8
- Coding: C1-C7
- Review: R1-R7
- Testing: T1-T7
- Release: L1-L6
- Escalation: E1-E6

## Operational Use

- Apply one tree at a time per decision context.
- Record chosen path in ticket/PR using step numbers.
- If multiple trees apply, resolve conflicts using Global Rules priority order.
