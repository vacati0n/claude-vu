# Self-Hosting Execution Plan

Date: 2026-08-18
Scope: Continue building the AI agent framework using the framework itself.

## 1. Current State (Evidence-Based)

- Proven executable slice: /implement -> implement-feature -> execution-planning -> planner.
- Runtime is partial by design (single-phase execution path).
- Agent registry has 2 active records (planner, architect).
- Command registry has 1 active record (implement).
- Workflow registry has 3 active records (implement-feature, refactor, investigate).
- Host-invocable agent entrypoints: 1 (*.agent.md for planner only).
- Skill registry has 7 records: S01, S02, S06, S07, S08, S09, S12.
- Blocking gap for architect phase: S03 missing (and S11 also not registered for investigation matrix requirements).
- Workflow model inconsistency exists between workflow-engine.md and implement-feature.md phase ordering.

## 2. Target Definition (Fully Executable v1)

The framework is considered fully executable v1 when all of the following are true:

1. Commands registered and routable: implement, bugfix, refactor, investigate, review, release, document, test, research.
2. Every active workflow has a machine-resolvable Phase Model table.
3. Every phase owner agent is host-invocable via an *.agent.md entrypoint.
4. Required skills for each phase resolve from registry/skills.yaml with zero unresolved codes.
5. Runtime executes multi-phase transitions with persisted state transitions (not one-phase only).
6. Validation engine supports each core artifact type emitted by active workflows.
7. Recovery behavior exists for retry and classified failure handling.

## 3. Build Strategy: "Use It To Build It"

Use a controlled bootstrap loop:

- Planner plans each increment.
- Architect designs each increment.
- Implement/reviewer/qa/orchestrator agents execute and validate increments.
- Each increment updates runtime + registries + evidence reports.
- Only merge increments that add executable capability plus proof artifacts.

Rule: no "spec-only" merge without executable proof when feature claims runtime capability.

## 4. Phased Roadmap

## Phase 0 - Normalize Contracts (1-2 days)

Objective:
- Remove contradictory source-of-truth signals.

Tasks:
- Reconcile workflow-engine.md with workflows/implement-feature.md phase order.
- Decide canonical owner naming migration from omn-architect aliases to architect.
- Align template-catalog owners with active runtime agents.

Exit Criteria:
- No contradictory phase order between machine-routing sources.
- All owner references in active workflows map to registered or explicitly aliased agents.

Evidence:
- Diff report + validation checklist update.

## Phase 1 - Unblock Architect Slice (1-2 days)

Objective:
- Make solution-design-and-risk-assessment executable.

Tasks:
- Register S03 in registry/skills.yaml.
- Register S11 if retained as mandatory in investigate matrix phases.
- Add architect.agent.md host entrypoint.
- Execute vertical slice: /implement -> architect phase -> technical-design output + validation.

Exit Criteria:
- Runtime resolve for architect phase returns success.
- New run folder contains complete evidence and validator pass.

Evidence:
- New run ledger/events/validation report.

## Phase 2 - Expand Runtime State Engine (3-5 days)

Objective:
- Move from one-phase execution to multi-phase orchestration.

Tasks:
- Implement persisted state transition model (pending, leased, running, completed, failed, blocked).
- Add transition guards from phase gates and contracts.
- Add idempotent work item keys and replay-safe completion handling.

Exit Criteria:
- End-to-end implement-feature runs across at least planning + design + one delivery phase.
- Re-run of same request does not duplicate side effects.

Evidence:
- Multi-phase run events with ordered state transitions.

## Phase 3 - Register Operational Surface (2-3 days)

Objective:
- Make command/workflow/agent coverage match intended usage.

Tasks:
- Register remaining command records in registry/commands.yaml.
- Add machine-resolvable Phase Model sections to remaining active workflows.
- Add *.agent.md entrypoints for active execution agents.

Exit Criteria:
- 100% of active commands resolve to active workflows.
- 100% of active workflow phase owners are invocable.

Evidence:
- Registry coverage report with counts and unresolved=0.

## Phase 4 - Validation and Recovery Hardening (3-4 days)

Objective:
- Improve reliability and confidence of autonomous execution.

Tasks:
- Extend validators to technical-design, bug-analysis, investigation-report, release-note, review package artifacts.
- Implement retry policy with bounded attempts and classified failures.
- Emit structured failure envelopes for blocked transitions.

Exit Criteria:
- Validator coverage across all core emitted artifact types.
- Controlled retry observed in at least one induced-failure test run.

Evidence:
- Failure injection runs + validation summaries.

## Phase 5 - Self-Hosting Operating Mode (2 days)

Objective:
- Make framework development itself run through framework workflows by default.

Tasks:
- Define one command profile for "framework-internal change" routing.
- Require change proposals to include run artifact links from framework execution.
- Add release checklist for framework updates.

Exit Criteria:
- New framework changes are planned/executed/reviewed via framework commands, not ad hoc.

Evidence:
- Two consecutive framework changes completed in self-hosting mode.

Status: complete. Three consecutive framework changes were carried in self-hosting mode
(`FC-001`, `FC-002`, `FC-003`), and the increment is reported in
`reports/self-hosting-operating-mode-report-2026-08-18.md` with the machine record in
`reports/self-hosting-2026-08-18.json`.

## 5. Priority Backlog (Next 7 Days)

P0
- Register S03 in registry/skills.yaml.
- Add architect.agent.md.
- Prove architect vertical slice with runtime evidence.

P1
- Reconcile workflow-engine.md vs implement-feature.md.
- Add Phase Model tables for refactor and investigate.

P2
- Add second command record (bugfix or refactor) and prove one run.

## 6. Governance Rules for Safe Self-Hosting

- Every capability claim must include executable evidence under .claude/runs.
- Registry change without resolution test is blocked.
- Workflow phase additions must include owner invocability proof.
- Reports that conflict are superseded by latest evidence-backed run report.

## 7. Weekly Maturity Metrics

Track weekly:

- Invocable agents / active agents.
- Registered commands / command specs.
- Workflows with Phase Model / active workflows.
- Resolved required skills / total required skills.
- Runtime components implemented / planned runtime components.
- End-to-end successful runs per workflow.

Target trend: monotonic increase in executable coverage; zero increase in unresolved dependencies.

## 8. AI Self-Scaling Plan (v2)

Objective:
- Enable the framework to autonomously expand itself with controlled risk until Fully Executable v2.

### 8.1 Scaling Principles

- Execution-first: every new capability must be proven by a completed run under `.claude/runs/`.
- Small safe increments: each increment changes one primary surface only (runtime, registry, validator, or workflow model).
- Contract before code: phase contract and artifact schema must be machine-readable before implementation.
- Auto-detect drift: registry, workflow, and runtime inconsistencies are treated as blockers.
- Promotion by evidence: only promoted when gates, validators, and replay checks all pass.

### 8.2 Autonomous Scaling Loop

Loop per increment:

1. Detect Gap
- Scan for unresolved skills, non-invocable owners, unvalidated artifact types, missing phase models.

2. Generate Change Proposal
- Planner produces execution plan.
- Architect produces technical design and risk profile.

3. Execute Change
- Implementation agent applies scoped change.
- Reviewer and QA validate output and behavior.

4. Validate and Replay
- Run validators on produced artifacts.
- Replay same request to verify idempotency and stable side effects.

5. Promote or Roll Back
- Promote if all gates pass and evidence package is complete.
- Roll back and create follow-up issue if any blocking check fails.

### 8.3 Scale Phases (Next Level)

## Phase A - Auto-Discovery Foundation (2-3 days)

Objective:
- Make gap detection automatic and repeatable.

Tasks:
- Add nightly audit script for registry coverage, invocability, phase-model coverage, and required-skill resolution.
- Emit one machine-readable dashboard artifact per run (json summary).
- Fail CI when critical drift exceeds threshold.

Exit Criteria:
- One command can produce a full maturity snapshot with pass/fail status.

Evidence:
- `reports/maturity-snapshot-<date>.json` + linked run evidence.

## Phase B - Capability Factory (3-5 days)

Objective:
- Standardize how new capabilities are added by agents.

Tasks:
- Create templates for: new command record, workflow phase model, agent entrypoint, validator skeleton.
- Add an orchestrated command profile for "add-capability" routed through planner -> architect -> implement -> review -> qa.
- Enforce one-capability-per-increment policy.

Exit Criteria:
- Two new capabilities onboarded through the same factory flow without manual exceptions.

Evidence:
- Two completed capability runs with identical execution pattern.

## Phase C - Multi-Workflow Runtime Completion (4-7 days)

Objective:
- Move from workflow-specific execution to reusable workflow engine behavior.

Tasks:
- Generalize transition engine across all active workflows.
- Add queue leasing, retry budget, and dead-letter handling for blocked states.
- Support human-escalation checkpoints without breaking deterministic logs.

Exit Criteria:
- At least one successful end-to-end run per active workflow.

Evidence:
- Run matrix report with workflow-by-workflow pass status.

## Phase D - Validator Mesh (3-5 days)

Objective:
- Guarantee artifact correctness uniformly across workflows.

Tasks:
- Add validators for all core artifact families not yet covered.
- Introduce validator versioning and compatibility policy.
- Add cross-artifact consistency checks (plan vs design vs review vs release note).

Exit Criteria:
- 100% of emitted core artifacts validated by machine-checkable rules.

Evidence:
- Validator coverage report + induced-failure test suite results.

## Phase E - Autonomous Portfolio Mode (3-4 days)

Objective:
- Let the framework self-prioritize scaling work safely.

Tasks:
- Add scoring model: impact, risk, dependency depth, validator readiness.
- Auto-build weekly scaling backlog from detected gaps.
- Cap concurrent high-risk increments to avoid systemic breakage.

Exit Criteria:
- Weekly backlog generated automatically and executed with no manual triage for at least one full cycle.

Evidence:
- `reports/auto-backlog-<week>.md` + completed run set.

### 8.4 Guardrails for Safe Autonomous Scale

- Max parallel risky increments: 2.
- Any runtime-core change requires at least one replay pass on previous successful run ID.
- Any registry schema change requires migration check and backward compatibility statement.
- Any validator rule change requires before/after diff on at least one historical artifact.
- Any unresolved blocking failure auto-opens a remediation increment before new feature increments.

### 8.5 KPI Targets (4 Weeks)

- End-to-end successful runs per active workflow: >= 1 by week 2, >= 3 by week 4.
- Validator coverage for core artifacts: >= 80% by week 2, 100% by week 4.
- Replay stability (same input, same declared side effects): >= 95% by week 4.
- Mean time to close blocking drift: < 24h by week 4.
- Manual intervention rate in scaling increments: < 20% by week 4.

### 8.6 First 72-Hour Execution Plan

Day 1:
- Deliver maturity snapshot command and json report artifact.
- Freeze current baseline run IDs for replay checks.

Day 2:
- Implement capability factory templates and command profile.
- Execute one low-risk capability increment through full loop.

Day 3:
- Add validator mesh seed for one missing artifact family.
- Run replay and publish first autonomous scaling status report.

## 9. Post Self-Hosting Plan: Remaining Agents and Skills

Objective:
- Implement, register, and operationalize all remaining agents and skill assets so every active workflow phase is owned by a runtime-capable, evidence-validated agent.

### 9.1 Remaining Scope Snapshot

Remaining agent implementation scope (beyond planner and architect):

- `omn-product-owner`
- `omn-business-analyst`
- `omn-context-agent`
- `omn-dev-1-bug-analyst`
- `omn-dev-1-implement`
- `omn-dev-2-reviewer`
- `omn-qa`
- `omn-tech-lead`
- `omn-documentation`
- `omn-orchestrator`
- `backend-developer` (specialized execution profile)
- `omn-planning-generate-clarification-questions` (planning support profile)

Remaining skill registration scope:

- S04 `avalonia/desktop-ux-guidelines.md` (currently unregistered)
- S05 `react/react-engineering.md` (currently unregistered)

Remaining skill normalization scope (ID/category not yet standardized in matrix):

- `cicd/release-automation.md`
- `coding-style/dotnet-coding-style.md`

### 9.2 Implementation Strategy

- Vertical slices by workflow, not by file type.
- Register agent record only when the runtime module set and evidence run are ready.
- Keep one primary capability per increment to minimize blast radius.
- Promote only after validator pass and replay stability pass.

### 9.3 Wave Plan (4 Waves)

## Wave 1 - Delivery Core Agents (3-4 days)

Scope:
- `omn-product-owner`, `omn-dev-1-implement`, `omn-dev-2-reviewer`, `omn-qa`

Why first:
- These agents close the critical delivery path after planning and design.

Tasks:
- Create runtime module sets (`manifest.yaml` + 7 module files) per agent.
- Register agents in `registry/agents.yaml` when runtime-ready.
- Ensure `*.agent.md` entrypoint resolves and is invocable.
- Execute one implement-feature run covering scope -> implementation -> review -> quality.

Exit Criteria:
- Each of 4 agents has: runtime module set, active registry record, completed run evidence.

## Wave 2 - Discovery and Decision Agents (3-4 days)

Scope:
- `omn-business-analyst`, `omn-context-agent`, `omn-tech-lead`, `omn-documentation`

Why second:
- These agents unlock investigate/research/release communication quality.

Tasks:
- Implement runtime module sets and register agents.
- Prove one investigate run and one research run end-to-end.
- Add artifact validators for investigation and publication outputs if missing.

Exit Criteria:
- Investigate and research workflows each have at least one successful end-to-end run.

## Wave 3 - Ops and Closure Agents (2-3 days)

Scope:
- `omn-orchestrator`, `omn-dev-1-bug-analyst`

Why third:
- These roles enforce closure, escalation, and defect lifecycle reliability.

Tasks:
- Implement runtime module sets and register both agents.
- Prove one fix-bug run and one release run with closure evidence.
- Verify escalation and blocked-state handling in run ledger events.

Exit Criteria:
- Fix-bug and release workflows each have one successful evidence-backed run.

## Wave 4 - Specialist Profiles and Skill Completion (2-3 days)

Scope:
- `backend-developer`, `omn-planning-generate-clarification-questions`
- Skills S04, S05
- Normalize `cicd/release-automation.md` and `coding-style/dotnet-coding-style.md`

Why fourth:
- Specialist profiles and UI stack skills are scale multipliers, not blockers for base workflow execution.

Tasks:
- Decide whether each specialist is a full runtime agent or a constrained profile.
- Register S04 and S05 in `registry/skills.yaml` with full metadata.
- Assign canonical skill IDs/categories for CI/CD and coding-style assets, then register or formally retire.

Exit Criteria:
- No unregistered skill row remains in the skill matrix without explicit retirement status.

### 9.4 Parallelization Rules

Can run in parallel:

- Wave 1 and Wave 2 preparation (contract authoring + template scaffolding).
- Validator authoring for target artifacts while agent runtime modules are being built.
- Skill registration work for S04/S05 while Wave 3 execution runs.

Must stay sequential:

- Agent registry activation -> runtime proof run -> promotion.
- Workflow-level completion claim before at least one end-to-end run exists.
- Skill deprecation decisions before removing matrix references.

### 9.5 Definition of Done (Per Agent and Per Skill)

Agent DoD:

- Runtime module set exists and loads in declared order.
- `*.agent.md` entrypoint resolves in host runtime.
- Active record exists in `registry/agents.yaml`.
- At least one completed run references the agent as owner.
- Output artifact passes its validator.

Skill DoD:

- Record exists in `registry/skills.yaml` with `skillCode`, category, version, status, and specification path.
- All phase-mandatory references to that skill resolve.
- No unresolved skill reference remains in active workflow phase models.

### 9.6 14-Day Execution Backlog

Days 1-3:
- Implement Wave 1 agent runtimes and activate records.

Days 4-6:
- Execute delivery core workflow run and close Wave 1 gaps.

Days 7-9:
- Implement Wave 2 agent runtimes and run investigate/research evidence passes.

Days 10-11:
- Implement Wave 3 agents and run fix-bug/release proofs.

Days 12-14:
- Complete Wave 4 specialist profiles and register/normalize remaining skills.

### 9.7 Success Metrics for This Plan

- Active registered agents: from 2 to 12+.
- End-to-end successful runs: at least one per active workflow.
- Unregistered catalog skills: from 2 to 0 (or explicit retired state).
- Workflow-phase owner runtime proof coverage: 100%.
- Validator pass rate on newly added artifact families: >= 95%.
