# Configuration: Runtime Policies

## Security and Compliance

- Do not expose secrets in logs or artifacts.
- Respect principle of least privilege in automation.
- Record sensitive changes with approval trace.

## Reliability

- Prefer idempotent operations for workflow steps.
- Require explicit retries and timeout strategy.
- Fail fast on invalid inputs.

## Auditability

- Every workflow must produce a traceable output artifact.
- Decision records must include rationale and owner.
- Release actions require timestamped status entries.

## Change Management

- Policy updates require tech lead approval.
- Breaking policy changes must include migration guidance.
