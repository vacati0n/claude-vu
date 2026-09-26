# Rule Engine Specification

Status: specification — not implemented — executable counterpart: `runtime/recovery_policy.py` and the run-state model.

## Purpose

Define a deterministic Rule Engine that validates outputs from every agent before output is accepted, merged, or released.

## Scope

- Applies to all agent-generated outputs.
- Supports text, code diffs, config updates, test plans, and release notes.
- Runs in pre-merge and pre-release stages, and optionally during draft generation.

## Design Principles

- Deterministic: Same input and same rule set must produce identical results.
- Explicit: Every rule has clear conditions and outcomes.
- Traceable: Every decision includes rule IDs and evidence.
- Fail-safe: Any rule execution failure defaults to block when severity is `critical`.
- Extensible: New rules can be added without changing engine core.

## Core Entities

### 1. AgentOutput

- `output_id`: unique identifier
- `agent_id`: source agent identifier
- `timestamp_utc`: ISO-8601 timestamp
- `artifact_type`: `code|doc|config|plan|mixed`
- `content`: normalized output payload
- `metadata`: repository, branch, target files, context

### 2. Rule

- `rule_id`: unique stable identifier (example: `SEC-001`)
- `group`: `architecture|coding|testing|security|documentation`
- `title`: short human-readable name
- `description`: rule intent
- `severity`: `critical|high|medium|low`
- `applies_when`: deterministic predicate
- `check`: deterministic evaluation function
- `pass_condition`: explicit boolean condition
- `fail_message`: operator-facing failure text
- `evidence_fields`: exact fields collected on failure
- `auto_fixable`: `true|false`
- `policy_action`: `block|warn|info`

### 3. EvaluationResult

- `output_id`
- `engine_version`
- `ruleset_version`
- `started_at_utc`
- `completed_at_utc`
- `rule_results[]`
- `final_decision`: `accept|accept_with_warnings|reject`

### 4. RuleResult

- `rule_id`
- `status`: `pass|fail|not_applicable|error`
- `severity`
- `policy_action`
- `evidence`
- `message`

## Input Normalization

Before evaluation, engine must:

1. Normalize line endings to LF.
2. Canonicalize paths to workspace-relative format.
3. Strip non-deterministic fields (random IDs, runtime timestamps inside content unless required).
4. Parse output into structured segments: files changed, symbols changed, tests impacted, docs impacted.
5. Compute content hash for reproducibility.

## Evaluation Pipeline

1. Load active ruleset by `ruleset_version`.
2. Validate ruleset integrity (unique IDs, valid severities, valid actions).
3. For each rule in stable sort order (`group`, then `rule_id`):
- Evaluate `applies_when`.
- If false, mark `not_applicable`.
- If true, execute `check`.
- Map boolean result to `pass` or `fail`.
- On runtime error, mark `error` and apply error policy.
4. Aggregate all `RuleResult` values.
5. Compute `final_decision` by policy.
6. Emit machine-readable report and human-readable summary.

## Decision Policy

- `reject` if any `critical` rule has `fail` or `error`.
- `reject` if any `high` rule with `policy_action=block` has `fail`.
- `accept_with_warnings` if only `warn` rules fail.
- `accept` if no blocking failures and no critical errors.

## Error Policy

- If a rule check throws an exception:
- `critical` -> treat as `fail` and `block`.
- `high|medium|low` -> set `status=error`, surface warning, continue evaluation.

## Rule Groups and Baseline Rules

## Architecture Rules

### ARC-001: Architecture Decision Alignment

- Severity: `high`
- Applies when: output modifies architecture-related components or boundaries.
- Check: output references an approved architecture decision record (ADR) ID or approved equivalent.
- Pass condition: exactly one valid ADR ID found and status is `approved`.
- Policy action: `block`

### ARC-002: Boundary Consistency

- Severity: `high`
- Applies when: output introduces new module/service dependencies.
- Check: dependency direction matches allowed dependency graph.
- Pass condition: no disallowed dependency edge detected.
- Policy action: `block`

### ARC-003: Non-Functional Requirement Coverage

- Severity: `medium`
- Applies when: output introduces new user-facing capability.
- Check: latency, availability, and scalability impact are declared.
- Pass condition: all required NFR fields are present and non-empty.
- Policy action: `warn`

### ARC-004: Migration Strategy Presence

- Severity: `high`
- Applies when: output changes schema, storage model, or integration contract.
- Check: migration and rollback steps are explicitly described.
- Pass condition: both migration and rollback sections present.
- Policy action: `block`

## Coding Rules

### COD-001: Build and Static Analysis Clean

- Severity: `critical`
- Applies when: output contains code changes.
- Check: compile/build succeeds and required linters have zero errors.
- Pass condition: all required checks exit successfully with zero lint errors.
- Policy action: `block`

### COD-002: Public API Compatibility

- Severity: `high`
- Applies when: output modifies public interfaces.
- Check: compatibility check reports no breaking changes, or version bump is present.
- Pass condition: no breaking diff OR major-version bump declared.
- Policy action: `block`

### COD-003: Complexity Guardrail

- Severity: `medium`
- Applies when: output modifies functions/methods.
- Check: complexity delta is within configured threshold.
- Pass condition: per-function complexity <= threshold.
- Policy action: `warn`

### COD-004: Duplicate Logic Prevention

- Severity: `medium`
- Applies when: substantial new logic blocks are introduced.
- Check: similarity scan against existing codebase.
- Pass condition: duplication score below threshold.
- Policy action: `warn`

### COD-005: Change Scope Discipline

- Severity: `low`
- Applies when: PR-level output includes unrelated file classes.
- Check: touched files match declared intent scope.
- Pass condition: all touched files belong to declared scope or are justified.
- Policy action: `info`

## Testing Rules

### TST-001: Required Test Presence

- Severity: `critical`
- Applies when: output changes executable behavior.
- Check: matching unit/integration tests are included or updated.
- Pass condition: impacted behaviors have corresponding tests.
- Policy action: `block`

### TST-002: Test Execution Success

- Severity: `critical`
- Applies when: test suite is defined for affected modules.
- Check: required test suites pass.
- Pass condition: zero failing tests in required suites.
- Policy action: `block`

### TST-003: Regression Protection

- Severity: `high`
- Applies when: output fixes a defect.
- Check: regression test exists that fails before and passes after fix.
- Pass condition: linked regression test evidence present.
- Policy action: `block`

### TST-004: Coverage Non-Regression

- Severity: `medium`
- Applies when: output modifies code paths with existing coverage baselines.
- Check: coverage delta against baseline.
- Pass condition: coverage drop <= allowed threshold.
- Policy action: `warn`

### TST-005: Flaky Test Gate

- Severity: `high`
- Applies when: newly added tests are detected.
- Check: stability run across N deterministic re-runs.
- Pass condition: pass rate is 100% for required N runs.
- Policy action: `block`

## Security Rules

### SEC-001: Secret Leakage Prevention

- Severity: `critical`
- Applies when: output includes code, config, or docs.
- Check: secret scanner for keys, tokens, passwords, private cert material.
- Pass condition: zero confirmed secret findings.
- Policy action: `block`

### SEC-002: Dependency Vulnerability Gate

- Severity: `critical`
- Applies when: dependencies or lockfiles are modified.
- Check: vulnerability scan using approved database.
- Pass condition: zero unresolved critical/high vulnerabilities in modified dependency graph.
- Policy action: `block`

### SEC-003: Input Validation and Output Encoding

- Severity: `high`
- Applies when: output adds or changes input handling or rendering.
- Check: required validation and context-appropriate encoding patterns present.
- Pass condition: all tainted-input sinks are guarded by approved controls.
- Policy action: `block`

### SEC-004: Authorization Enforcement

- Severity: `critical`
- Applies when: output touches protected resource paths.
- Check: authorization checks exist at enforcement points.
- Pass condition: no protected action is reachable without required authorization.
- Policy action: `block`

### SEC-005: Security Logging for Critical Events

- Severity: `medium`
- Applies when: auth, privilege, or policy decisions are changed.
- Check: audit/security logs emitted for critical decisions.
- Pass condition: required security events are logged with actor and outcome.
- Policy action: `warn`

## Documentation Rules

### DOC-001: Change Summary Completeness

- Severity: `medium`
- Applies when: any non-trivial output is generated.
- Check: summary includes what changed, why, impact, and rollback notes.
- Pass condition: all summary fields present.
- Policy action: `warn`

### DOC-002: API/Contract Documentation Sync

- Severity: `high`
- Applies when: public API or contract changes.
- Check: API reference/changelog updated.
- Pass condition: doc updates detected and linked to changed contract.
- Policy action: `block`

### DOC-003: Runbook Update Requirement

- Severity: `high`
- Applies when: operational behavior, alerts, or recovery steps change.
- Check: runbook modification exists.
- Pass condition: runbook includes new failure modes and mitigation steps.
- Policy action: `block`

### DOC-004: Traceability Links

- Severity: `low`
- Applies when: ticketed work item exists.
- Check: output references issue/ticket and decision artifact IDs.
- Pass condition: valid links are present.
- Policy action: `info`

## Rule Configuration Model

```yaml
engine:
  engineVersion: 1.0.0
  rulesetVersion: 2026.08
  failClosedOnCriticalError: true
  executionOrder:
    - architecture
    - coding
    - testing
    - security
    - documentation

thresholds:
  complexityMaxPerFunction: 10
  maxCoverageDropPercent: 0.5
  flakyReruns: 5

policy:
  highSeverityDefaultAction: block
  mediumSeverityDefaultAction: warn
  lowSeverityDefaultAction: info
```

## Deterministic Evaluation Requirements

- Rule predicates must use only declared inputs and configured thresholds.
- No network calls during decision phase unless response is pinned to immutable snapshot.
- Time-dependent rules must use provided evaluation timestamp, not wall-clock reads.
- Sorting and iteration order must be stable.

## Output Report Format

```json
{
  "output_id": "OUT-2026-08-05-001",
  "engine_version": "1.0.0",
  "ruleset_version": "2026.08",
  "final_decision": "reject",
  "rule_results": [
    {
      "rule_id": "SEC-001",
      "status": "fail",
      "severity": "critical",
      "policy_action": "block",
      "message": "Potential secret detected in config artifact",
      "evidence": {
        "file": "config/app.env",
        "line": 12,
        "pattern": "AWS_SECRET_ACCESS_KEY"
      }
    }
  ]
}
```

## Enforcement Points

- Draft validation: optional, advisory mode.
- Pull request validation: mandatory, blocking mode.
- Pre-release validation: mandatory, blocking mode.

## Governance

- Ruleset owner: Engineering Productivity + Security.
- Change control: PR with approval from one owner in each affected group.
- Versioning: semantic version for engine, date-based version for ruleset.
- Audit retention: keep evaluation reports for minimum 180 days.

## Minimal Acceptance Criteria for Implementation

- Engine can parse and evaluate all baseline rules.
- Engine emits deterministic final decision and per-rule evidence.
- Blocking policy works exactly as defined.
- Reports are exportable as JSON and human-readable markdown.
- Ruleset can be updated without core code changes.
