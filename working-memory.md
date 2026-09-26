# Working Memory Specification

Status: specification — not implemented — executable counterpart: `runtime/recovery_policy.py` and the run-state model.

## Purpose

Define a runtime Working Memory model used only during workflow execution to maintain operational context, coordination state, and action continuity.

## Scope

- Applies to one workflow execution instance.
- Shared across all participating agents in that execution.
- Not persisted as long-term system memory by default.

## Core Principle

Working Memory is ephemeral. It is created when workflow execution starts and destroyed when workflow execution ends, is canceled, or times out.

## Lifecycle

## 1. Initialize

Trigger:
- Workflow state changes to Running.

Actions:
- Create a new Working Memory object with unique execution ID.
- Seed mandatory fields from workflow request and orchestration context.

## 2. Update

Trigger:
- Any step completion, failure, file mutation, plan revision, or risk/issue event.

Actions:
- Apply deterministic update rules to relevant fields.
- Append event to change log with timestamp and actor.

## 3. Snapshot

Trigger:
- Step boundary, gate decision, escalation, or manual checkpoint.

Actions:
- Produce read-only snapshot for audit/debug during active execution.
- Keep snapshots bound to the same execution lifecycle.

## 4. Terminate

Trigger:
- Workflow Completed, Failed, Canceled, or Expired.

Actions:
- Finalize summary for output artifact.
- Purge in-memory state and temporary snapshots per retention policy.

## Required Data Model

## WorkingMemory

- execution_id: string (unique)
- workflow_id: string
- status: pending|running|blocked|completed|failed|canceled
- started_at_utc: ISO-8601 timestamp
- updated_at_utc: ISO-8601 timestamp
- expires_at_utc: ISO-8601 timestamp
- current_task: CurrentTask
- current_plan: CurrentPlan
- files_changed: FileChange[]
- pending_work: PendingWorkItem[]
- issues: IssueItem[]
- risks: RiskItem[]
- next_actions: NextAction[]
- change_log: MemoryEvent[]

## 1) Current task

Purpose:
- Capture what is being executed right now.

Fields:
- task_id: string
- title: string
- description: string
- owner: string (agent or human)
- step: string (workflow step name)
- state: not_started|in_progress|blocked|done
- started_at_utc: timestamp
- target_completion_utc: timestamp
- dependencies: string[]

Update rules:
- Only one current_task may have state=in_progress at a time.
- If task state becomes blocked, a matching issue or risk entry must be created.

## 2) Current plan

Purpose:
- Track the active execution plan and progress.

Fields:
- plan_id: string
- goal: string
- assumptions: string[]
- steps: PlanStep[]
- percent_complete: number (0-100)
- last_replan_reason: string

PlanStep:
- step_id: string
- title: string
- status: not_started|in_progress|completed|blocked
- owner: string
- due_utc: timestamp
- evidence_refs: string[]

Update rules:
- At most one PlanStep can be in_progress.
- percent_complete must equal completed_steps / total_steps * 100 (rounded to whole number).
- Replan requires setting last_replan_reason.

## 3) Files changed

Purpose:
- Track file-level modifications during execution.

Fields (FileChange):
- path: string (workspace-relative)
- operation: create|update|delete|rename
- change_type: code|config|docs|test|infra|other
- author: string
- timestamp_utc: timestamp
- summary: string
- validation_status: pending|passed|failed

Update rules:
- New file mutation appends one FileChange event.
- Repeated mutations of same file may be merged in view, but raw event history must remain intact in change_log.
- validation_status=failed requires at least one issue entry.

## 4) Pending work

Purpose:
- Track known, unfinished work required for completion.

Fields (PendingWorkItem):
- item_id: string
- title: string
- reason: string
- priority: low|medium|high|critical
- owner: string
- due_utc: timestamp
- unblock_condition: string
- status: open|in_progress|resolved

Update rules:
- No duplicate open items with same normalized title and owner.
- When status resolves, related next_actions must be closed or replaced.

## 5) Issues

Purpose:
- Track defects, blockers, and non-conformances encountered during execution.

Fields (IssueItem):
- issue_id: string
- title: string
- category: bug|blocker|quality_gate|dependency|environment|other
- severity: low|medium|high|critical
- detected_in_step: string
- description: string
- owner: string
- status: open|mitigated|resolved
- escalation_required: boolean
- linked_files: string[]

Update rules:
- Any critical issue sets workflow status to blocked unless explicitly waived by policy.
- escalation_required=true must create a corresponding next_actions entry.

## 6) Risks

Purpose:
- Track potential future negative outcomes and mitigations.

Fields (RiskItem):
- risk_id: string
- title: string
- probability: low|medium|high
- impact: low|medium|high|critical
- exposure_score: integer (1-9)
- trigger_signal: string
- mitigation: string
- contingency: string
- owner: string
- status: active|monitoring|closed

Update rules:
- exposure_score must be deterministic from probability x impact mapping.
- Any risk with impact=critical must appear in next_actions.

Deterministic exposure mapping:
- probability: low=1, medium=2, high=3
- impact: low=1, medium=2, high=3, critical=3
- exposure_score = probability_value * impact_value

## 7) Next actions

Purpose:
- Define immediate, executable actions to move workflow forward.

Fields (NextAction):
- action_id: string
- title: string
- type: execute|validate|escalate|communicate|decide
- owner: string
- due_utc: timestamp
- related_object: task|plan_step|file|issue|risk|pending_work
- related_id: string
- success_criteria: string
- status: queued|in_progress|done|canceled

Update rules:
- Must be sorted by priority then due_utc.
- At least one queued next action is required while workflow status is running or blocked.
- No next action may reference a non-existent related object.

## Supporting Structures

MemoryEvent:
- event_id: string
- timestamp_utc: timestamp
- actor: string
- event_type: initialize|update|checkpoint|gate_decision|escalation|retry|terminate
- object_type: workflow|task|plan|file|issue|risk|action|pending_work
- object_id: string
- before_hash: string
- after_hash: string
- summary: string

## Deterministic Rules

- All timestamps must be UTC.
- All list ordering must be stable and deterministic.
- Equality checks use normalized strings (trimmed, lowercase where policy allows).
- Concurrent updates resolve by monotonic event timestamp, then lexical actor ID.
- If update conflicts cannot be resolved deterministically, set status=blocked and create issue category=quality_gate.

## Validation Requirements

A Working Memory instance is valid only if:

1. All required top-level fields exist.
2. current_task and current_plan are present while status is running or blocked.
3. files_changed, pending_work, issues, risks, next_actions are arrays (empty allowed).
4. Referential integrity holds for all related_id references.
5. Update rules for each section are satisfied.

Validation failures:
- severity critical if referential integrity fails or required fields missing.
- severity high for rule violations that break determinism.
- severity medium for format/consistency defects.

## Escalation Behavior

Escalate when any condition is true:

- Validation severity critical.
- More than 2 retries on same failed transition.
- Critical issue remains open beyond escalation threshold.
- No eligible next action exists while workflow is running.

Escalation actions:
- Set workflow status=blocked.
- Create issue category=quality_gate with escalation_required=true.
- Append next action type=escalate with assigned owner.

## Retry Behavior

Retry applies to failed transitions such as validation, gate checks, or step updates.

Rules:
- Max retries per transition: 2.
- Each retry must include new evidence in change_log.
- On final retry failure, enforce escalation behavior.

## Retention and Purge

- In-memory object retention: until workflow terminal state plus grace window.
- Default grace window: 15 minutes for diagnostics.
- After grace window, purge full object and snapshots.
- Persist only approved final summary artifact, not full Working Memory state.

## Minimal Interface Contract

Operations:
- initialize(workflow_context) -> WorkingMemory
- update(memory, event) -> WorkingMemory
- validate(memory) -> ValidationResult
- snapshot(memory) -> MemorySnapshot
- terminate(memory, terminal_status) -> FinalSummary

ValidationResult:
- is_valid: boolean
- violations: Violation[]
- recommended_action: continue|retry|escalate|terminate

Violation:
- code: string
- severity: critical|high|medium|low
- message: string
- object_ref: string

## Example Skeleton

```yaml
execution_id: EXE-2026-08-05-001
workflow_id: WF-1001
status: running
current_task:
  task_id: T-12
  title: Implement API validation
  state: in_progress
current_plan:
  plan_id: P-9
  goal: Complete feature delivery
  steps:
    - step_id: S-1
      title: Update handler
      status: completed
    - step_id: S-2
      title: Add tests
      status: in_progress
files_changed:
  - path: src/handler.ts
    operation: update
pending_work: []
issues: []
risks:
  - risk_id: R-3
    title: Regression in auth flow
    probability: medium
    impact: high
    exposure_score: 6
next_actions:
  - action_id: A-1
    title: Run integration tests
    type: validate
    status: queued
```
