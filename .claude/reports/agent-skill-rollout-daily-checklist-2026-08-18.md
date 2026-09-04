# Agent and Skill Rollout Daily Checklist

Date: 2026-08-18
Source plan: self-hosting-execution-plan-2026-08-18.md section 9
Execution mode: self-hosting only (all changes must run through framework workflows)

## 1) Global Done Rules

- Every agent activation must have: runtime module set, active registry record, invocable entrypoint, and completed evidence run.
- Every skill activation must have: active skill registry record and resolved phase references.
- No workflow completion claim is accepted without at least one end-to-end completed run.
- Any blocker found during verification must open remediation work before new scope is added.

## 2) Day-by-Day Plan (14 Days)

## Day 1 - Wave 1 kickoff

Owner: omn-orchestrator

Tasks:
- Create execution board for Wave 1 delivery core agents.
- Lock baseline metrics snapshot (agents, skills, workflows, commands, invocability).
- Route first increment through planner and architect.

Verification:
- Coverage snapshot report generated.
- Increment plan and design artifacts produced.

Evidence:
- New run folder under .claude/runs
- Daily report under .claude/reports

Status: [ ]

## Day 2 - Implement omn-product-owner runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-product-owner.
- Add or verify omn-product-owner.agent entrypoint.
- Prepare agent registry record (draft to active only after proof).

Verification:
- Runtime load order resolves.
- Entry point resolves.

Evidence:
- Agent files updated
- Resolver output attached

Status: [ ]

## Day 3 - Implement omn-dev-1-implement runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-dev-1-implement.
- Validate role boundaries against architect/planner contracts.
- Activate registry record when validation passes.

Verification:
- Manifest and load order pass.
- Policy checks pass.

Evidence:
- Registry diff
- Validation summary

Status: [ ]

## Day 4 - Implement omn-dev-2-reviewer runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-dev-2-reviewer.
- Ensure review gates map to workflow gate matrix.
- Activate registry record after proof.

Verification:
- Gate reference resolution pass.
- Entry point invocable.

Evidence:
- Run ledger and events

Status: [ ]

## Day 5 - Implement omn-qa runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-qa.
- Bind quality and regression responsibilities to workflow phases.
- Activate registry record after proof.

Verification:
- Quality phase mapping pass.
- Runtime proof run completed.

Evidence:
- Completed run for quality phase ownership

Status: [ ]

## Day 6 - Wave 1 closeout run

Owner: omn-orchestrator

Tasks:
- Execute one implement-feature run that crosses scope, implementation, review, and quality.
- Review with omn-dev-2-reviewer and omn-qa.
- Publish Wave 1 closeout report.

Verification:
- End-to-end run status Completed.
- Artifacts validated.

Evidence:
- Run ledger, events, validation reports
- Wave 1 closeout report

Status: [ ]

## Day 7 - Implement omn-business-analyst runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-business-analyst.
- Activate registry record after proof.

Verification:
- Problem-framing phase ownership resolves.

Evidence:
- Resolve output and run evidence

Status: [ ]

## Day 8 - Implement omn-context-agent runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-context-agent.
- Activate registry record after proof.

Verification:
- Technical-discovery and technical-validation ownership resolves.

Evidence:
- Run and validation summary

Status: [ ]

## Day 9 - Implement omn-tech-lead runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-tech-lead.
- Activate registry record after proof.

Verification:
- Option-analysis, recommendation, merge, readiness phases resolve.

Evidence:
- Phase resolution output and run evidence

Status: [ ]

## Day 10 - Implement omn-documentation runtime

Owner: omn-dev-1-implement

Tasks:
- Add runtime module set for omn-documentation.
- Activate registry record after proof.

Verification:
- Publication and communication phases resolve.

Evidence:
- Run ledger and artifact validation

Status: [ ]

## Day 11 - Wave 2 closeout runs

Owner: omn-orchestrator

Tasks:
- Execute one investigate run end-to-end.
- Execute one research run end-to-end.
- Publish Wave 2 closeout report.

Verification:
- Both workflow runs Completed.
- Artifact validators pass.

Evidence:
- Two completed run packages
- Wave 2 report

Status: [ ]

## Day 12 - Implement omn-orchestrator and omn-dev-1-bug-analyst runtimes

Owner: omn-dev-1-implement

Tasks:
- Add runtime module sets for both agents.
- Activate registry records after proof.

Verification:
- Fix-bug and release closure ownership resolves.

Evidence:
- Resolver output and proof runs

Status: [ ]

## Day 13 - Wave 3 closeout runs

Owner: omn-orchestrator

Tasks:
- Execute one fix-bug run end-to-end.
- Execute one release run end-to-end.
- Verify escalation and blocked-state behavior in events.

Verification:
- Completed status for both runs.
- Escalation and recovery events captured when applicable.

Evidence:
- Run event streams and validation reports

Status: [ ]

## Day 14 - Wave 4 skills and specialist profiles closeout

Owner: omn-orchestrator

Tasks:
- Register S04 and S05 as active skills.
- Decide and implement or retire specialist profiles: backend-developer and omn-planning-generate-clarification-questions.
- Normalize CI/CD and coding-style skill assets to canonical ID/category, then register or retire explicitly.
- Publish final rollout summary.

Verification:
- No unresolved skill references in active workflow phase models.
- No unregistered matrix skill without explicit retired status.

Evidence:
- Skill registry diff
- Final coverage report
- Final rollout report

Status: [ ]

## 3) Daily Standup Update Template

- Date:
- Wave/Day:
- Completed today:
- Blockers:
- Evidence produced:
- Next day focus:
- Risk level (Low/Medium/High):

## 4) Final Completion Checklist

- [ ] All target remaining agents have runtime module sets.
- [ ] All target remaining agents have active registry records.
- [ ] All target remaining agents are invocable in host runtime.
- [ ] At least one completed run exists for each active workflow.
- [ ] S04 and S05 are active and resolved.
- [ ] CI/CD and coding-style skill assets are registered or explicitly retired.
- [ ] Final evidence-backed report is published.
