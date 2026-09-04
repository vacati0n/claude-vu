# Quality Gates Specification

## Purpose

Define mandatory Quality Gates for each workflow step so progression is controlled, auditable, and deterministic.

## Global Policy

- No step may start unless all Entry Gate conditions pass.
- No step may complete unless all Exit Gate conditions pass.
- Validation evidence must be recorded for every gate decision.
- If escalation conditions are met, workflow pauses until escalation outcome is resolved.
- Retry attempts are bounded and deterministic.

## Gate Status Model

- `PASS`: all required checks succeeded.
- `FAIL`: one or more required checks failed.
- `BLOCKED`: external dependency or escalation unresolved.
- `WAIVED`: approved exception with expiration and owner.

## Retry Policy (Default)

- Maximum retries per step: `2`
- Cooldown between retries: `15 minutes`
- Retry requires new evidence (same evidence cannot be re-submitted).
- After max retries exhausted: mandatory escalation.

## Workflow Steps

## 1. Requirements Intake

### Entry Gate

- Problem statement exists.
- Business owner assigned.
- Priority and due window defined.

### Exit Gate

- Scope is approved.
- Acceptance criteria are testable and complete.
- Dependencies and constraints documented.

### Validation

- Checklist completeness score = 100%.
- Acceptance criteria include measurable outcomes.
- Stakeholder approval recorded.

### Escalation

- Escalate to Product Owner if requirements are ambiguous after one clarification cycle.
- Escalate to Engineering Manager if dependency ownership is unknown.

### Retry

- Retry trigger: missing fields or untestable acceptance criteria.
- Retry action: revise requirements artifact and re-run checklist.
- Max retries: 2, then escalate.

## 2. Architecture Design

### Entry Gate

- Requirements Intake Exit Gate = PASS.
- Non-functional requirements captured.
- Data classification identified.

### Exit Gate

- Architecture option selected with rationale.
- Risk register updated.
- Migration/rollback strategy documented (if applicable).

### Validation

- Architecture review checklist passes.
- Chosen design aligns with decision matrix path.
- Critical risks have owner and mitigation.

### Escalation

- Escalate to Architecture Owner if no compliant design option exists.
- Escalate to Security if handling restricted/sensitive data without approved pattern.

### Retry

- Retry trigger: failed architecture review or unresolved risk.
- Retry action: revise design and re-review.
- Max retries: 2, then escalate.

## 3. Implementation (Coding)

### Entry Gate

- Architecture Design Exit Gate = PASS.
- Work item and branch are linked.
- Definition of done includes tests and docs updates.

### Exit Gate

- Code compiles/builds successfully.
- Required static analysis passes.
- Unit tests for changed behavior are added/updated.

### Validation

- Build status = green.
- Lint/static checks = zero blocking errors.
- Traceability link exists between code changes and work item.

### Escalation

- Escalate to Tech Lead for unresolved API breaking change.
- Escalate to Security for suspicious secret/vulnerability finding.

### Retry

- Retry trigger: build/lint/test failure.
- Retry action: fix defects, push updated change set, re-run validations.
- Max retries: 2, then escalate.

## 4. Peer Review

### Entry Gate

- Implementation Exit Gate = PASS.
- PR includes summary, risk level, and test evidence.
- Required reviewers assigned.

### Exit Gate

- Required approvals obtained.
- All required checks pass.
- Review comments resolved or dispositioned.

### Validation

- Reviewer matrix satisfies policy (high-risk requires dual approval).
- No unresolved blocking comments.
- CI status for mandatory checks = PASS.

### Escalation

- Escalate to Domain Owner when reviewers disagree on blocking issue.
- Escalate to Engineering Manager if review SLA is breached.

### Retry

- Retry trigger: rejected review, failing checks, or unresolved comments.
- Retry action: apply revisions and request re-review.
- Max retries: 2, then escalate.

## 5. Testing and Verification

### Entry Gate

- Peer Review Exit Gate = PASS.
- Test plan is aligned to change scope.
- Required test environments are available.

### Exit Gate

- Required unit/integration/regression suites pass.
- Coverage non-regression policy satisfied.
- Critical defects count = 0.

### Validation

- Test reports attached and reproducible.
- Regression evidence present for defect fixes.
- Flaky-test threshold not exceeded.

### Escalation

- Escalate to QA Lead for repeated flaky failures.
- Escalate to Incident/Support owner if release-blocking defect found.

### Retry

- Retry trigger: failing required suite, unstable tests, or environment issue.
- Retry action: fix test/code/environment, then rerun required suites.
- Max retries: 2, then escalate.

## 6. Security Review

### Entry Gate

- Testing and Verification Exit Gate = PASS.
- Security scan tools configured and up to date.
- Threat surface changes identified.

### Exit Gate

- No unresolved critical/high vulnerabilities.
- No secret leakage findings.
- Required authn/authz controls verified.

### Validation

- SAST/SCA/secret scan reports attached.
- Security exceptions, if any, are approved and time-bounded.
- Audit logging requirements met for critical paths.

### Escalation

- Escalate to Security Team immediately for critical vulnerability or potential breach.
- Escalate to Engineering Leadership for unresolved high-risk waiver requests.

### Retry

- Retry trigger: blocking security finding.
- Retry action: remediate finding and rerun security checks.
- Max retries: 2, then escalate.

## 7. Documentation and Readiness

### Entry Gate

- Security Review Exit Gate = PASS.
- Release notes template available.
- Runbook owner identified.

### Exit Gate

- User/developer docs updated.
- API/contract changes documented.
- Runbook and rollback instructions updated.

### Validation

- Documentation checklist passes.
- Links to updated docs and runbooks are valid.
- Change impact and rollback notes are complete.

### Escalation

- Escalate to Documentation Owner for missing or incomplete docs.
- Escalate to Ops Lead if runbook update is incomplete for operational changes.

### Retry

- Retry trigger: failed doc checklist or missing runbook details.
- Retry action: update docs and revalidate checklist.
- Max retries: 2, then escalate.

## 8. Release Approval

### Entry Gate

- Documentation and Readiness Exit Gate = PASS.
- Rollback plan tested within policy window.
- Release window and change ticket approved.

### Exit Gate

- Deployment completed per rollout policy.
- Post-deploy health checks pass.
- Release decision recorded (`go` or `no-go`).

### Validation

- Canary/progressive rollout metrics within thresholds.
- SLO and error budget checks green.
- Rollback drill evidence available.

### Escalation

- Escalate to Incident Commander for severe post-deploy degradation.
- Escalate to Executive On-Call if customer-critical outage persists beyond SLA threshold.

### Retry

- Retry trigger: failed deployment or failed health validation.
- Retry action: rollback, remediate, and redeploy in next approved window.
- Max retries: 1 in same window, then escalate.

## 9. Post-Release Review

### Entry Gate

- Release Approval Exit Gate = PASS.
- Monitoring data collected for minimum observation window.
- Incident and support ticket summary available.

### Exit Gate

- Post-release review completed.
- Corrective actions logged with owners and due dates.
- Knowledge base/runbook updates finalized.

### Validation

- KPI comparison against pre-release baseline completed.
- Defect leakage and incident metrics reported.
- Action items tracked in backlog.

### Escalation

- Escalate to Engineering Manager if corrective actions are not assigned.
- Escalate to Product + Engineering leadership for repeated release quality regressions.

### Retry

- Retry trigger: incomplete retrospective evidence or missing ownership.
- Retry action: complete missing analysis and re-run review checklist.
- Max retries: 2, then escalate.

## Gate Evidence Requirements

For every step, store:

- Workflow step ID and timestamp.
- Gate decision (`PASS|FAIL|BLOCKED|WAIVED`).
- Validator identity (human or system).
- Evidence references (reports, links, artifacts).
- Escalation record (if any).
- Retry attempt count and outcome.

## Waiver Policy

- Waivers are allowed only for non-critical gates unless explicitly approved by Security/Engineering leadership.
- Waiver must include reason, owner, risk, compensating controls, and expiration date.
- Expired waivers automatically revert gate status to `FAIL`.

## Deterministic Progression Rules

- Step `N+1` cannot start until step `N` Exit Gate is `PASS` or valid `WAIVED`.
- `BLOCKED` status suspends workflow timer for SLA measurement.
- Any `critical` validation failure forces immediate escalation and blocks progression.
