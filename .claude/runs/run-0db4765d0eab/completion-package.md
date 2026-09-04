# Completion Package: run-0db4765d0eab

Produced by the Output Aggregator in `runtime/framework_runtime.py`. This package covers every phase of the run, not one invocation.

## Run Summary

| Field | Value |
|---|---|
| run_id | `run-0db4765d0eab` |
| command | `/refactor` |
| workflow | `refactor` v1.0.0 |
| runtime | `0.4.0` |
| run status | `WaitingForHuman` |
| input digest | `sha256:158fc31efe3d1b46ce302a185888e7da` |
| phases | 5 (1 completed, 4 blocked, 0 failed, 0 pending) |
| state transitions | 13 |
| replays suppressed | 0 |

## Phase Ledger

| # | Phase | Owner | Status | Queue | Artifact | Validation |
|---|---|---|---|---|---|---|
| 1 | `scope-invariants-and-risk-profile` | `architect` | completed | Completed | `runs/run-0db4765d0eab/states/scope-invariants-and-risk-profile/artifacts/technical-design.md` | pass (78/78) |
| 2 | `safety-net-establishment` | `omn-qa` | blocked | Blocked | - | awaiting_capability_registration |
| 3 | `refactor-implementation` | `omn-dev-1-implement` | blocked | Blocked | - | awaiting_capability_registration |
| 4 | `behavioral-validation` | `omn-qa` | blocked | Blocked | - | awaiting_capability_registration |
| 5 | `closure-and-debt-record` | `omn-orchestrator` | blocked | Blocked | - | awaiting_capability_registration |

## Gate Decisions

| Gate | Closes | Required owners | Decision | Owner role | Recorded by |
|---|---|---|---|---|---|
| Invariant Gate | `scope-invariants-and-risk-profile` | omn-architect, omn-tech-lead | approved | omn-tech-lead | operator, on behalf of omn-tech-lead (architect is the producer and is excluded from deciding this gate) |
| Implementation Gate | `refactor-implementation` | omn-dev-2-reviewer | undecided | - | - |
| Regression Gate | `behavioral-validation` | omn-qa, omn-dev-2-reviewer | undecided | - | - |
| Closure Gate | `closure-and-debt-record` | omn-orchestrator, omn-documentation | undecided | - | - |

Gate approval is a human decision. The runtime records it, enforces the Producer Exclusion Rule of `workflows/workflow-gate-matrix.md`, and refuses to invent one; an undecided gate holds its successor phase in `blocked`.

## Module Provenance

Modules loaded by each executed agent, in the order its manifest declares.

| Phase | # | Module | Digest |
|---|---|---|---|
| `scope-invariants-and-risk-profile` | 1 | `agents/architect/system.md` | `sha256:7a08861f6a692bd5b4e65be426a0fcb7` |
| `scope-invariants-and-risk-profile` | 2 | `agents/architect/identity.md` | `sha256:a2ddb7032106c2e4ec70f0cddff9bae1` |
| `scope-invariants-and-risk-profile` | 3 | `agents/architect/reasoning.md` | `sha256:80894ab095455279790bb46409340ee6` |
| `scope-invariants-and-risk-profile` | 4 | `agents/architect/execution.md` | `sha256:384164c51047d05f590d9f796d731b1c` |
| `scope-invariants-and-risk-profile` | 5 | `agents/architect/output.md` | `sha256:63a9e786aaef073f0cee8fe992ea05fd` |
| `scope-invariants-and-risk-profile` | 6 | `agents/architect/quality.md` | `sha256:90ec2ac3e9e1337d42ab7be8f4f11418` |
| `scope-invariants-and-risk-profile` | 7 | `agents/architect/examples.md` | `sha256:4badefef323665829e5d262b4d0c6839` |

## State Transition Log

Every persisted work-item transition, in commit order. This is the run's primary evidence: the state of a work item is never asserted, it is derived from this log.

| seq | work item | from | to | trigger | reason | actor |
|---|---|---|---|---|---|---|
| 1 | `safety-net-establishment` (state) | pending | blocked | `blocker_detected` | `policy_block` | runtime:state-engine |
| 2 | `refactor-implementation` (state) | pending | blocked | `blocker_detected` | `policy_block` | runtime:state-engine |
| 3 | `behavioral-validation` (state) | pending | blocked | `blocker_detected` | `policy_block` | runtime:state-engine |
| 4 | `closure-and-debt-record` (state) | pending | blocked | `blocker_detected` | `policy_block` | runtime:state-engine |
| 5 | `scope-invariants-and-risk-profile` (state) | pending | leased | `lease_acquired` | `leased` | runtime:invocation-gateway |
| 6 | `scope-invariants-and-risk-profile` (state) | leased | running | `invocation_started` | `execution_started` | runtime:invocation-gateway |
| 7 | `scope-invariants-and-risk-profile` (state) | running | retrying | `retryable_failure_classified` | `validation_failed` | runtime:recovery-controller |
| 8 | `scope-invariants-and-risk-profile` (state) | retrying | pending | `backoff_elapsed` | `enqueued` | runtime:recovery-controller |
| 9 | `scope-invariants-and-risk-profile` (state) | pending | leased | `lease_acquired` | `leased` | runtime:invocation-gateway |
| 10 | `scope-invariants-and-risk-profile` (state) | leased | running | `invocation_started` | `execution_started` | runtime:invocation-gateway |
| 11 | `scope-invariants-and-risk-profile` (state) | running | completed | `result_accepted` | `output_accepted` | runtime:validation-engine |
| 12 | `Invariant Gate` (gate) | pending | blocked | `awaiting_decision` | `approval_wait` | runtime:state-engine |
| 13 | `Invariant Gate` (gate) | blocked | completed | `decision_approved` | `output_accepted` | human:operator, on behalf of omn-tech-lead (architect is the producer and is excluded from deciding this gate) |

## Event Stream

| # | Event | Work item | Actor | Reason | Summary |
|---|---|---|---|---|---|
| E-0001 | `run_initialized` | `scope-invariants-and-risk-profile` | runtime:execution-coordinator | `enqueued` | run accepted for /refactor -> refactor across 5 phase(s) |
| E-0002 | `work_item_enqueued` | `scope-invariants-and-risk-profile` | runtime:task-router | `enqueued` | state work item 1/5 routed to owner agent architect |
| E-0003 | `work_item_enqueued` | `gate::Invariant Gate` | runtime:task-router | `enqueued` | gate work item 'Invariant Gate' enqueued to close phase scope-invariants-and-risk-profile |
| E-0004 | `work_item_enqueued` | `safety-net-establishment` | runtime:task-router | `enqueued` | state work item 2/5 routed to owner agent omn-qa |
| E-0005 | `work_item_enqueued` | `refactor-implementation` | runtime:task-router | `enqueued` | state work item 3/5 routed to owner agent omn-dev-1-implement |
| E-0006 | `work_item_enqueued` | `gate::Implementation Gate` | runtime:task-router | `enqueued` | gate work item 'Implementation Gate' enqueued to close phase refactor-implementation |
| E-0007 | `work_item_enqueued` | `behavioral-validation` | runtime:task-router | `enqueued` | state work item 4/5 routed to owner agent omn-qa |
| E-0008 | `work_item_enqueued` | `gate::Regression Gate` | runtime:task-router | `enqueued` | gate work item 'Regression Gate' enqueued to close phase behavioral-validation |
| E-0009 | `work_item_enqueued` | `closure-and-debt-record` | runtime:task-router | `enqueued` | state work item 5/5 routed to owner agent omn-orchestrator |
| E-0010 | `work_item_enqueued` | `gate::Closure Gate` | runtime:task-router | `enqueued` | gate work item 'Closure Gate' enqueued to close phase closure-and-debt-record |
| E-0011 | `escalation_opened` | `safety-net-establishment` | runtime:state-engine | `policy_block` | state work item blocked: awaiting_capability_registration |
| E-0012 | `escalation_opened` | `refactor-implementation` | runtime:state-engine | `policy_block` | state work item blocked: awaiting_capability_registration |
| E-0013 | `escalation_opened` | `behavioral-validation` | runtime:state-engine | `policy_block` | state work item blocked: awaiting_capability_registration |
| E-0014 | `escalation_opened` | `closure-and-debt-record` | runtime:state-engine | `policy_block` | state work item blocked: awaiting_capability_registration |
| E-0015 | `context_hydrated` | `scope-invariants-and-risk-profile` | runtime:context-loader | `context_hydration_completed` | context slice frozen: 17 member(s), 3 input(s) |
| E-0016 | `work_item_leased` | `scope-invariants-and-risk-profile` | runtime:invocation-gateway | `leased` | invocation envelope built and leased to the host-subagent adapter in native mode |
| E-0017 | `invocation_started` | `scope-invariants-and-risk-profile` | runtime:invocation-gateway | `execution_started` | dispatching agent architect v1.0.0 through host registration agents/architect.agent.md |
| E-0018 | `invocation_completed` | `scope-invariants-and-risk-profile` | agent:architect | `output_accepted` | agent returned status 'succeeded' with 2 artifact ref(s) |
| E-0019 | `validation_failed` | `scope-invariants-and-risk-profile` | runtime:validation-engine | `validation_failed` | artifact rejected: 0 blocking, 1 correctable |
| E-0020 | `retry_scheduled` | `scope-invariants-and-risk-profile` | runtime:recovery-controller | `retry_wait` | artifact rejected; classified output-schema-failure -> retry |
| E-0021 | `context_hydrated` | `scope-invariants-and-risk-profile` | runtime:context-loader | `context_hydration_completed` | context slice frozen: 17 member(s), 3 input(s) |
| E-0022 | `work_item_leased` | `scope-invariants-and-risk-profile` | runtime:invocation-gateway | `leased` | invocation envelope built and leased to the host-subagent adapter in native mode |
| E-0023 | `invocation_started` | `scope-invariants-and-risk-profile` | runtime:invocation-gateway | `execution_started` | dispatching agent architect v1.0.0 through host registration agents/architect.agent.md |
| E-0024 | `invocation_completed` | `scope-invariants-and-risk-profile` | agent:architect | `output_accepted` | agent returned status 'succeeded' with 2 artifact ref(s) |
| E-0025 | `validation_passed` | `scope-invariants-and-risk-profile` | runtime:validation-engine | `output_accepted` | artifact conforms: 78/78 checks passed |
| E-0026 | `escalation_opened` | `gate::Invariant Gate` | runtime:state-engine | `approval_wait` | gate work item blocked: awaiting_human_decision |
| E-0027 | `aggregation_completed` | `closure-and-debt-record` | runtime:output-aggregator | `output_accepted` | completion package and provenance manifest persisted for 1/5 completed phase(s) |
| E-0028 | `escalation_resolved` | `gate::Invariant Gate` | human:operator, on behalf of omn-tech-lead (architect is the producer and is excluded from deciding this gate) | `output_accepted` | Invariant Gate approved by omn-tech-lead (evidence: scope-invariants-and-risk-profile) |

## Replay Suppression

No repeated call has been made against this run.

## Open Escalations

| Work item | Blocked reason | Detail |
|---|---|---|
| `safety-net-establishment` (state) | `awaiting_capability_registration` | G1-CAPABILITY: [missing-capability-failure] agent 'omn-qa' has no record in registry/agents.yaml |
| `refactor-implementation` (state) | `awaiting_capability_registration` | G1-CAPABILITY: [missing-capability-failure] agent 'omn-dev-1-implement' has no record in registry/agents.yaml |
| `behavioral-validation` (state) | `awaiting_capability_registration` | G1-CAPABILITY: [missing-capability-failure] agent 'omn-qa' has no record in registry/agents.yaml |
| `closure-and-debt-record` (state) | `awaiting_capability_registration` | G1-CAPABILITY: [missing-capability-failure] agent 'omn-orchestrator' has no record in registry/agents.yaml |

## Residual Items

- Phases with a registered validator: ['execution-planning', 'solution-design-and-risk-assessment'].
- Phases whose declared output artifact has no registered validator, and which therefore cannot be dispatched: ['safety-net-establishment', 'refactor-implementation', 'behavioral-validation', 'closure-and-debt-record'].
- `Retrying` and `Cancelled`, canonical task states in `config/task-queue.md`, are not implemented by this runtime.
