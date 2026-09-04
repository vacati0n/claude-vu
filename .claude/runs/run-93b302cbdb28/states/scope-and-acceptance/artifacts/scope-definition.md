# Scope Definition: Wave 1 delivery core agent rollout

```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0001
  featureName: Wave 1 delivery core agent rollout
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/wave-1-rollout-feature-request.md
    - type: change-request
      reference: runs/inputs/wave-1-rollout-change-request.md
    - type: business-intent
      reference: runs/inputs/wave-1-rollout-business-intent.md
    - type: architecture-context
      reference: runs/inputs/wave-1-rollout-architecture-context.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  scopeVerdict: partially-bounded
  acceptanceCriteriaCount: 13
  inputDigest: sha256:5653a190c21b2c09fd70d5d0c98ed9bb
  contextDigest: sha256:291a2c3abab3c91c9c4521d12d69b45f
```

## Metadata

- Feature name: Wave 1 delivery core agent rollout
- Requested by: the framework operator, through the supplied feature request, change request, and business intent for the Wave 1 delivery core rollout
- Business goal: the framework executes the delivery path it already routes, so a change can move from scope through implementation, review, and quality without an operator standing in for a missing owner at each step
- Target outcome: each of the four delivery core roles carries at least one of its phases from dispatch to an accepted output inside a framework run, and every phase they own that this change does not carry is reported as blocked with its reason
- Scope decision date: 2026-08-19

## Business Context

- Problem statement: the framework decides the route, holds the gates, and keeps the record, but executes 3 of its 36 declared phases; the delivery path after planning and design has no owner able to execute, so the operator performs those phases by hand against the run while the framework records them as blocked, and six of seven active workflows hold no completed run as a result
- Value hypothesis: if the four delivery core roles execute their own phases, the operator stops being the bottleneck on every increment, and the claim that the framework carries its own changes rests on execution evidence rather than on routing evidence alone
- Affected users: the framework operator who currently performs the unexecuted phases by hand, the downstream phase owners that consume those phases' outputs, and the reviewers who read the maturity board as the record of what the framework can actually do
- Success measure: the measures the supplied business intent states, namely that active agent registry records rise from 2 to 6, that six runtime module sets resolve, that the dispatchable phase count rises above 3, that a passing validation report exists for every executed Wave 1 phase, and that no verifier verdict regresses

## In Scope

What this change delivers, stated as what becomes true for the affected users. Ordered by business priority, ties broken by the order the expectation appeared in the supplied inputs.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | Each of the four delivery core roles, covering product ownership, implementation, review, and quality, is recognised by the framework as an executable owner, so a run that reaches a phase one of them owns proceeds to that owner instead of halting for want of a registered capability | Delivers the feature request's expected outcome that each role hold an active registry record and a resolving runtime contract, and the business intent's measures for owner count and module set count | must-have |
| `S-002` | At least one phase owned by a Wave 1 role runs to completion inside a framework run and produces an output the framework accepts against stated criteria rather than on trust | Delivers the feature request's expected outcome of completed-run evidence and a validated output, and the business intent's floor that at least one Wave 1 phase dispatches and completes | must-have |
| `S-003` | Every phase this change makes executable states what it must produce as a named, checkable artifact rather than as a description of one, so its output can be accepted or rejected on stated criteria | The supplied architecture context records that a phase whose output is described in prose cannot resolve to an output contract, and that extending an artifact declaration to a further phase is a product decision about scope | must-have |
| `S-004` | Every phase owned by a Wave 1 role that this change does not make executable is reported with the reason it was not, and no role is reported as rolled out on conditions it does not meet | Delivers the business intent's acceptance boundary, which requires a role meeting only part of the definition of done to be reported as partially rolled out with its blocker named | must-have |
| `S-005` | The parts of the delivery path that execute today keep executing, and the runs held as replay references stay reproducible | Delivers the behavioural invariants the change request states and the business intent's requirement that no metric regress, under a stated low tolerance for silent breakage | must-have |
| `S-006` | All four Wave 1 roles reach the completed-and-accepted bar that `S-002` sets for one, so the delivery path is executable at every step rather than at a single step | Delivers the feature request's expected outcome stated for each of the four roles, held above the floor rather than merged into it | should-have |

## Out of Scope

The boundary. Each exclusion names something a reader of the In Scope table could otherwise reasonably assume was included.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Runtime contracts and registration for the Wave 2 to Wave 4 agents | Named a non-goal by the supplied business intent, and the delivery core is a capability surface on its own under the stated one-surface-per-increment constraint | The four delivery core roles meet their acceptance boundary and a further wave is requested |
| `X-002` | Registration of skills S04 and S05, and normalization of the CI/CD and coding-style assets | Named a non-goal, and the phase-mandatory skill references the Wave 1 phases depend on already resolve | A phase a Wave 1 role owns is found to require a skill reference that does not resolve |
| `X-003` | Any change to gate ownership or to the Producer Exclusion Rule | Named a non-goal and held as a behavioural invariant; the Wave 1 roles gain execution, not decision rights | A Wave 1 role is found to be the only available owner of a gate it also produces evidence for |
| `X-004` | Making every one of the 36 declared phases dispatchable, and making every phase the four roles own dispatchable | Named a non-goal, and the stated constraint holds one primary capability surface per increment; phases not reached are reported under `S-004` rather than silently dropped | The delivery core meets its acceptance boundary and the remaining phases are requested as their own change |
| `X-005` | Updates to the board, the maturity snapshot, and the evidence records held under the reports surface | The change request places that surface outside routing scope under the self-hosting profile's closed exemption set | The exemption set in the self-hosting profile changes |
| `X-006` | Deciding the sequence in which the four roles are rolled out, and the size of each increment | Decomposition, sequencing, and increment sizing are decided by the execution planning phase against this boundary; this artifact issues no sequence and no breakdown | Execution planning reports that no sequence satisfies this boundary, which returns the boundary here as a scope question |
| `X-007` | Choosing the artifact type, the template shape, and the validating form for each phase that gains a named output | The shape of an output and the means of checking it are technical decisions taken in solution design; this artifact states only that a checkable output must exist | Solution design reports that no artifact type can satisfy `S-003` for a given phase, which returns that phase here as a scope question |

## Acceptance Criteria

Every criterion states a condition with a threshold, names the in-scope item it bounds, and names the method by which somebody would decide it holds.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | A run routed to a phase owned by any of the four roles dispatches to that role and proceeds to execution, recording neither a capability-registration block nor a context-resolution block against it | `S-001` | Inspection of the run's recorded work-item state for the routed phase, one routed run per role | must-have |
| `A-002` | The framework recognises six roles as executable owners where it recognised two, and no owner recognised before the change is lost | `S-001` | Registry coverage check run before and after the change, with the two owner lists compared | must-have |
| `A-003` | At least one phase owned by a Wave 1 role reaches a completed state in a run held under the runs surface, and that run's record names the output the phase produced | `S-002` | Inspection of the completed run record and of the output path it names | must-have |
| `A-004` | The output that phase produces is accepted by the framework's own validation, with a validation report recorded against it that reports a passing result and zero blocking failures | `S-002` | Reading of the validation report recorded for that phase, for its result and its blocking-failure count | must-have |
| `A-005` | Every phase this change makes executable declares its output by name, and that name resolves both to an owning contract and to a registered means of checking the output against it | `S-003` | Resolution check of each such phase's declared output, run against the framework's own capability chain | must-have |
| `A-006` | Every one of the twelve phases the four roles own appears in the run record either as executed with a validated output or as blocked with a recorded reason, and none is absent from the record | `S-004` | Enumeration of the twelve phases against the work-item records the run holds | must-have |
| `A-007` | No Wave 1 role is reported as rolled out unless it meets all five conditions of the acceptance boundary, and a role meeting only the registration conditions is reported as partially rolled out with its blocker named | `S-004` | Review of the reported rollout status for each of the four roles against the evidence recorded for that role | must-have |
| `A-008` | The three phases that dispatch today still dispatch after the change, namely execution planning and solution design in the feature workflow and the scope and invariants phase in the refactor workflow | `S-005` | A routed run for each of the three phases, compared against its recorded pre-change dispatch state | must-have |
| `A-009` | The two completed runs held as replay references remain readable and their fingerprints are unchanged | `S-005` | Fingerprint comparison of the two runs, taken before and after the change | must-have |
| `A-010` | Every verifier that reports a verdict before the change reports the same verdict after it, with no check moving from pass to fail | `S-005` | Full verifier run before and after the change, compared verdict by verdict and check by check | must-have |
| `A-011` | No phase-mandatory skill reference becomes unresolved, and the resolved reference count does not fall below the count recorded before the change | `S-005` | Skill resolution check run before and after the change, with the resolved counts compared | must-have |
| `A-012` | Each of the four existing host entrypoints still resolves after its role gains a runtime contract | `S-005` | Host resolution check for each of the four role identifiers | must-have |
| `A-013` | All four Wave 1 roles, not one, hold both a completed phase and an accepted output for that phase | `S-006` | Enumeration of the four roles against the completed-run record and the validation report recorded for each | should-have |

## Constraints and Dependencies

- Business constraints: one primary capability surface per increment, stated by both the feature request and the change request; no capability counts as complete without completed-run evidence held under the runs surface; no registry activation without the runtime contract that record points at; and registering a role whose phase still cannot dispatch is a partial increment that must say so
- Regulatory or policy constraints: the self-hosting profile governs this change, placing every framework path in routing scope against a closed exemption set for runs, reports, proposals, and build caches; requiring every phase of the routed workflow to be enqueued and either executed with a validated output or blocked with a recorded reason; requiring a phase output and its validation report wherever the routed workflow has a dispatchable phase; and requiring every mandatory item of the framework release checklist to be recorded with its result
- Delivery constraints: the six behavioural invariants the change request states bind this change, covering the phases that must keep dispatching, the replay-reference runs that must keep their fingerprints, the verifier verdicts that must not regress, the skill references that must stay resolved, and the gate ownership that must not move; the stated risk posture accepts an increment that lands partially and says so, and does not accept silent breakage of the path that executes today
- External dependencies: none outside this repository; inside it, the acceptance boundary depends on a definition of done held in a document that is neither a supplied input nor part of this run's frozen context, and `Q-001` records that dependency

## Scope Decisions

Each decision records a boundary choice a reader could reasonably have expected to go the other way, with the reason a reviewer needs in order to assess it.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | This change bounds all four delivery core roles, not only the first one named | The business intent measures success as the recognised owner count rising from two to six and as the delivery path being carried end to end; bounding only the first role would leave that outcome undelivered. The one-surface-per-increment constraint governs how the work is broken up, which the phase that owns decomposition decides, not how far the boundary reaches | The boundary covers four roles, so the change is expected to land across more than one increment, and a role that does not reach the acceptance boundary is reported as partially rolled out under `S-004` rather than dropped from scope | omn-product-owner |
| `D-002` | Reaching a completed and accepted phase for one role is the floor; reaching it for all four is the target | The business intent sets at least one dispatching and completing Wave 1 phase as its measure, while the feature request states completed-run evidence for each of the four. Both readings are recorded rather than one chosen, as `S-002` at must-have and `S-006` at should-have, so a partial landing is assessed against a stated bar instead of against silence | A change that carries one role to an accepted output delivers stated value and is not a failure; a change that carries all four meets the requester's full expectation, and the difference is visible at the gate rather than argued after it | omn-product-owner |
| `D-003` | Requiring a checkable named output for a phase is inside this boundary; choosing what that output is, is not | The supplied architecture context records that extending an artifact declaration to a further phase is a product decision about scope rather than a structural finding, and separately that the output's shape has two available forms. The first is a boundary question, answered here as `S-003`; the second is a design question, excluded as `X-007` | Solution design receives a stated obligation that every executable phase carry a checkable output, together with full freedom over the form that output takes | omn-product-owner |
| `D-004` | The conditional surfaces the change request declares are inside this boundary rather than a widening of it | The change request declares its blast radius up front and marks four surfaces as conditional on the design decision; treating those as outside the boundary would force the design either to fail `S-003` or to widen scope after the gate had assessed it | A change to a workflow phase declaration, a new template, a new validating rule, or a runtime phase-context entry sits inside this boundary when it is required to satisfy `S-001` or `S-003`, while whether it is required at all remains a design decision | omn-product-owner |
| `D-005` | The acceptance boundary is read as the five expected outcomes the feature request states per role, pending confirmation | The business intent defers acceptance to a five-part definition of done held in a document that is neither a supplied input nor part of this run's frozen context, and this agent may not reach outside those to read it. The feature request states five expected outcomes per role whose first three are registration conditions and whose last two are execution conditions, which matches the business intent's own description of a role that satisfies the first three and not the last two. The reading is recorded rather than assumed silently | Every acceptance criterion in this artifact is written against that reading; if confirmation contradicts it, the criteria change and the verdict is decided again. This is the reason the scope verdict is partially-bounded rather than bounded | omn-product-owner |
| `D-006` | Which phase each role carries to completion is left to the phase that assesses feasibility | Only one of the twelve phases these four roles own already declares a named output, and which of the remainder is cheapest to make checkable is a feasibility judgement this artifact has no supplied basis to make. Deciding it here would be choosing the technical route under the appearance of choosing scope | The boundary states that each role reaches the bar and leaves the selection of the phase to solution design, which `Q-002` records and routes | omn-product-owner |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | Do the five expected outcomes the feature request states per role match the five-part definition of done that the business intent names as the acceptance boundary, and is the reading recorded in `D-005` correct, that the first three are the registration conditions and the last two the execution conditions? | yes | omn-business-analyst | Before the Scope Gate decision is taken on this artifact |
| `Q-002` | Which phase does each of the four roles carry to a completed and accepted output in this change, given that only one of the twelve phases they own already declares a named output? | no | architect | Before the solution design and risk assessment phase closes |
| `Q-003` | The supplied architecture context records the feature workflow's scope and implementation phases as describing their outputs in prose, while the workflow specification in this run's frozen context names an output for both. Which reading is current, and how many phases owned by the four roles therefore still need a named output? | no | omn-context-agent | Before the execution planning phase closes |

## Handoff

- Downstream owner: `planner`, which decomposes this boundary in the execution planning phase of the feature workflow, followed by `architect` for the technical approach and `omn-qa` for the validation strategy built against these criteria
- Gate: Scope Gate; this agent is a named owner of that gate and is the producer of this evidence, so under the Producer Exclusion Rule the decision rests with `omn-business-analyst`, and no gate decision is recorded here
- Evidence for the gate: six in-scope items `S-001` to `S-006`, seven exclusions `X-001` to `X-007`, thirteen acceptance criteria `A-001` to `A-013` each naming the item it bounds and the method that verifies it, six scope decisions `D-001` to `D-006` each carrying its rationale and impact, and three open questions `Q-001` to `Q-003` of which `Q-001` blocks; recorded at status provisional and scope verdict partially-bounded because that blocking question stands
- Deferred to downstream: decomposition, sequencing, and increment sizing to execution planning; the artifact type, template shape, and validating form for every phase that gains a named output, together with the selection of which phase each role carries, to solution design and risk assessment; the test strategy and the execution of validation to `omn-qa`; and the decision on this artifact to `omn-business-analyst`
