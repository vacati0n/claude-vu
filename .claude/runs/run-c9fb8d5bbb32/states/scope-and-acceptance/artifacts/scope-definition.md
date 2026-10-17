```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0001
  featureName: "Knowledge Management Loop: Learn From Run Evidence"
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/knowledge-loop-feature-request.md
    - type: change-request
      reference: runs/inputs/knowledge-loop-change-request.md
    - type: business-intent
      reference: runs/inputs/knowledge-loop-business-intent.md
    - type: architecture-context
      reference: runs/inputs/knowledge-loop-architecture-context.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 23
  inputDigest: sha256:0291dd44e6a7a797463e20a80755817c
  contextDigest: sha256:d261b4f8b4cedf6df4bd4c96cc1eb2cd
```

## Metadata

- Feature name: Knowledge Management Loop: Learn From Run Evidence
- Requested by: Framework operator, through the feature request and business intent inputs
- Business goal: Later runs act on what earlier runs learned without an operator carrying it by hand, and the framework shows whether that learning reduces recurrence.
- Target outcome: Recorded failure patterns that recur reach the phase that produces the failing artifact before it writes, and the effect of each lesson is reported per run.
- Scope decision date: 2026-10-09

## Business Context

- Problem statement: Failures that the framework's validators and gates already record recur across runs, because no later dispatch sees what earlier runs recorded. Each recurrence costs a charged attempt, a retry, and operator time.
- Value hypothesis: Showing a phase the failure patterns recorded against its output reduces their recurrence, and a per-lesson report shows whether it does.
- Affected users: Operators who run framework workflows and today keep private notes to warn agents; agents dispatched in later runs; installed framework copies, which carry no operator notes.
- Success measure: For each lesson, the framework reports how often its failure recurred in dispatches already shown that lesson (`S-008`). No numeric recurrence target is supplied; see `Q-001`.

## In Scope

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | Operators see one lesson per recurring failure pattern in recorded run evidence (validation failures, gate rejections, rollbacks), each with occurrence count, distinct-run count, first and last seen, check description, and evidence references | Feature request, expected outcome 1 (harvest) | must-have |
| `S-002` | Re-harvesting unchanged evidence leaves the lesson record unchanged, and new evidence for a known pattern adds to its existing lesson | Feature request, expected outcome 1 (idempotent upsert) and acceptance intent 4 | must-have |
| `S-003` | Operators approve, retire, or annotate a lesson from the command line; the lesson keeps its owner, rationale, and history, and nothing is deleted | Feature request, expected outcome 2 (govern); `D-006` for the optional remedy | must-have |
| `S-004` | A lesson is eligible for hydration when it is approved, or automatically when it recurs in at least two distinct runs; a retired lesson is never eligible | Feature request, expected outcome 2; `D-002` | must-have |
| `S-005` | Each dispatch of a phase is shown the eligible lessons recorded against that phase, at most five, in its memory slice and in a "Lessons from earlier runs" section of its prompt | Feature request, expected outcome 3 and acceptance intent 1; `D-003`, `D-009` | must-have |
| `S-006` | A run planned before this change, or planned with hydration switched off, dispatches exactly as it does today | Feature request, acceptance intent 2; architecture context (replay checks) | must-have |
| `S-007` | A run planned after this change is hydrated by default, its plan records that choice, and a plan flag switches hydration off | Session operator direction (c); `D-001` | must-have |
| `S-008` | For each lesson, the framework reports how often its failure recurred in dispatches that had already been shown the lesson | Feature request, expected outcome 4; business intent, success | must-have |
| `S-009` | Lessons from a completed run are available to the next dispatch with no separate operator step | Feature request, expected outcome 5 | must-have |
| `S-010` | Each invocation's execution metrics record how many lessons were hydrated into it | Feature request, expected outcome 4 | should-have |
| `S-011` | The memory and runtime-policy documents describe the lesson category, its lifecycle, its eligibility rule, and the hydration choice as implemented | Change request, surfaces table (`memory/`, `config/runtime.md`) | should-have |

## Out of Scope

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Any model call, embedding, vector store, or network dependency in harvest, recall, or measurement | The runtime never calls a model and uses the standard library only (feature request constraints; business intent non-goal) | A change request proposing model-assisted harvesting, with its own constraint review |
| `X-002` | Automatic change to validators, artifact templates, gate rules, or agent module text derived from a lesson | Business intent non-goal; lessons inform agents and operators only | A change request citing approved lessons and a gate decision on the proposed change |
| `X-003` | Harvesting from sources other than recorded run evidence, such as chat transcripts, external tickets, or operator notes | Business intent non-goal | A change request naming the new source and its evidence format |
| `X-004` | Gate-approval waits recorded as lessons | Normal flow, not failure (architecture context; `D-005`) | A change request showing that an approval-wait pattern is a defect |
| `X-005` | Hydrating runs planned before this change, and backfilling their plans | Those runs must dispatch byte-identically (`D-007`) | An owner decision to backfill a named run, recorded in a change request |
| `X-006` | Changes to gates, validators, artifact contracts, Phase Model tables, and agent module text | Additive-only constraint (feature request) | A separate change request for each affected surface |
| `X-007` | Automatic retirement of lessons | Retirement is an operator action (`S-003`) | Evidence that a lesson's failure stopped recurring across a set of runs, proposed in a change request |
| `X-008` | Deletion of lesson records | Nothing is deleted; retired lessons keep their history (feature request) | A change request defining a retention policy |
| `X-009` | Graphical, hosted, or web reporting of lesson effectiveness | The feature request requires a command-line report only | An operator request for a dashboard |

## Acceptance Criteria

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | Harvesting the recorded runs yields at least one lesson keyed by check `C3.2` and at least one keyed by check `C7.1`, each with occurrence count, distinct-run count, first seen, last seen, check description, and at least one evidence reference, all non-empty | `S-001` | Unit test over a copy of recorded run evidence, plus command output listing both lessons with all six fields | must-have |
| `A-002` | One rollback_scheduled event for gate G and target phase P, recorded in two distinct runs, yields exactly one lesson keyed by the pair (G, P) with distinct-run count 2 | `S-001` | Unit test over a two-run fixture | must-have |
| `A-003` | Harvesting a repository with no runs directory exits with status 0 and reports zero lessons | `S-001` | Unit test invoking the harvest command against a directory without a runs directory, checking exit status and reported count | must-have |
| `A-004` | A lesson record holds only check identifier, check description, artifact or gate-and-phase key, counts, first and last seen dates, and evidence references; a fixture with a planted credential-like string in event detail text yields a store that does not contain that string | `S-001` | Unit test with a planted credential-like string in fixture events, searching every store file for it | must-have |
| `A-005` | Two consecutive harvests of unchanged evidence produce store files with identical bytes, compared file by file | `S-002` | Unit test hashing every store file after each harvest | must-have |
| `A-006` | Adding one validation_failed event for an existing fingerprint and harvesting once raises that lesson's occurrence count by exactly one, and leaves exactly one lesson with that fingerprint | `S-002` | Unit test on a fixture before and after appending one event | must-have |
| `A-007` | Each approve, retire, and annotate command changes only the status or remedy field of the named lesson, appends exactly one history entry to it, and leaves the lesson count unchanged | `S-003` | Unit test counting lessons and history entries before and after each command | must-have |
| `A-008` | A harvest run after an approval or annotation leaves the status, owner, rationale, and remedy of that lesson unchanged | `S-003` | Unit test that approves and annotates a lesson, harvests again, and compares the four fields | must-have |
| `A-009` | Running the memory optimization tool over a store holding lesson records leaves every lesson record byte-identical | `S-003` | Unit test running the optimizer on a fixture store and comparing lesson files | must-have |
| `A-010` | A lesson without a remedy is shown with its check description and no remedy line; a lesson with a remedy shows the remedy text unchanged | `S-003` | Unit test on the rendered lessons section for both kinds of lesson | should-have |
| `A-011` | A candidate lesson with distinct-run count 2 is eligible for hydration, and a candidate lesson with distinct-run count 1 is not | `S-004` | Unit test over fixture lessons with counts 1 and 2 | must-have |
| `A-012` | An active lesson is eligible at distinct-run count 1, and a retired lesson is ineligible at every count | `S-004` | Unit test over active and retired fixture lessons | must-have |
| `A-013` | With the threshold set to 3, a candidate lesson at distinct-run count 2 is ineligible; with the threshold set to 2 it is eligible | `S-004` | Unit test that changes the threshold value and re-evaluates eligibility | must-have |
| `A-014` | For a dispatch of phase P, an eligible lesson recorded against P appears in the memory slice with hydrated true, and the prompt contains the "Lessons from earlier runs" heading and that lesson's check ID | `S-005` | Unit test on an opted-in dispatch fixture, checking the slice fields and the prompt text | must-have |
| `A-015` | A lesson recorded against another phase, or whose artifact type differs from the output of phase P, appears in neither the memory slice nor the prompt of P's dispatch | `S-005` | Unit test with one non-matching lesson in the fixture | must-have |
| `A-016` | With seven eligible lessons for one phase, exactly five are hydrated, namely those with the five highest distinct-run counts, and two repeated dispatches select the identical five | `S-005` | Unit test over seven fixture lessons with distinct counts | must-have |
| `A-017` | With five hydrated lessons, the "Lessons from earlier runs" section has at most eleven lines: one heading and two lines per lesson | `S-005` | Unit test counting lines in the rendered section | must-have |
| `A-018` | For a run planned before the change or with hydration switched off, the dispatch envelope and prompt are byte-identical to a baseline captured before the change, the idempotency key is unchanged, and replay checks M12 and M14 pass unchanged | `S-006` | Unit test against the stored baseline, plus the existing replay checks M12 and M14 | must-have |
| `A-019` | A plan created after the change records hydration as on; a plan with the flag set off yields a memory slice with hydrated false and a reason that names the plan flag | `S-007` | Unit test on two plan fixtures, plus plan command output | must-have |
| `A-020` | The effectiveness report lists, per lesson, the dispatches that were shown the lesson and the later recurrences of its failure; a fixture with three shown dispatches and one later recurrence reports 3 and 1 | `S-008` | Unit test on the fixture, plus report command output | must-have |
| `A-021` | A lesson already recorded in one run that recurs in a newly aggregated run is eligible for the next dispatch, with no harvest command run in between | `S-009` | Unit test that aggregates the fixture run, then dispatches the next phase and inspects its memory slice | must-have |
| `A-022` | The execution metrics of each invocation carry a lessons-hydrated count equal to the lessons in its memory slice, and zero for an unhydrated run | `S-010` | Unit test on hydrated and unhydrated metrics fixtures | should-have |
| `A-023` | The memory README, memory governance, memory resolver, and runtime configuration documents each name the lesson category, the states candidate, active, and retired, the two-run threshold, and the plan-time hydration flag | `S-011` | Unit test that searches each document for the required terms | should-have |

## Constraints and Dependencies

- Business constraints: Additive only. Gates, validators, artifact contracts, Phase Model tables, and agent module text stay unchanged, and no verifier loses its recorded baseline (feature request; business intent). Each rejection costs a charged attempt, three per phase (business intent).
- Regulatory or policy constraints: No regulatory constraint is stated in the supplied inputs. The architecture context records that `config/runtime.md` makes memory hydration opt-in per run. `D-001` changes that default for runs planned after this change, and `Q-002` asks for its confirmation.
- Delivery constraints: Standard library only, with no network, embedding, or vector store dependency (feature request). The change is framework-internal and is routed through the self-hosting profile with a change proposal (change request). The framework runtime version increments (change request). The bundled payload mirror is refreshed by its sync procedure and never edited by hand (architecture context). Loading policy stays in the runtime and configuration, not in agent modules (architecture context). The full unit suite takes about 26 minutes (architecture context).
- External dependencies: Recorded run evidence under the runs directory (validation events, recovery ledgers, validation reports). An installed copy has no runs directory, and `A-003` covers that case. No external system, ticket tracker, or stakeholder access is required.

## Scope Decisions

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | Hydration is on by default for runs planned after this change; each plan records its choice, and a plan flag switches it off | Session operator direction (c). Expected outcomes 3 and 5 require lessons to reach later runs with no operator step, and the flag keeps an off switch | Runs planned after the change may receive lessons, and the opt-in default in the runtime configuration no longer holds for them (`Q-002`) | Session operator; overrulable by `omn-business-analyst` at the Scope Gate |
| `D-002` | A candidate lesson becomes eligible automatically at two distinct runs | Session operator direction (a). Recurrence across runs is the evidence the feature request names; two is the lowest count that separates recurrence from a single occurrence | A failure seen in one run is never shown automatically; a failure seen in two runs is | Session operator; overrulable by `omn-business-analyst` |
| `D-003` | At most five lessons are hydrated into one dispatch | Session operator direction (b). The feature request requires the prompt to grow by a bounded amount | Eligible lessons beyond five for one phase are not shown in that dispatch | Session operator; overrulable by `omn-business-analyst` |
| `D-004` | Under the cap, the lessons with the highest distinct-run count are selected, and ties resolve deterministically | Recurrence is the strongest evidence in the eligibility rule, so it also orders the cap | When more than five lessons are eligible, those recurring in fewer runs are dropped first | `omn-product-owner`, under its priority and threshold decision right |
| `D-005` | Gate-approval waits are not lessons | Session operator direction (d). The architecture context classes approval waits as normal flow | No lesson is created from an approval wait, however often it recurs | Session operator |
| `D-006` | The human-written remedy on a lesson is optional | Session operator direction (e). The business intent requires lessons to arise without operator authoring | A lesson without a remedy is shown with its check description alone | Session operator |
| `D-007` | Runs planned before the change never hydrate, and their plans are not backfilled | Session operator direction (c). The feature request requires byte-identical dispatch for those runs | Earlier runs keep today's dispatch output and idempotency key | Session operator; feature request acceptance intent 2 |
| `D-008` | The "Lessons from earlier runs" section is bounded at one heading line and two lines per hydrated lesson | The feature request requires bounded prompt growth; the numeric bound is an acceptance threshold this phase sets | At five lessons the section is at most eleven lines (`A-017`) | `omn-product-owner`, under its acceptance threshold decision right |
| `D-009` | A lesson reaches only the phase whose output artifact type and phase identifier it was recorded against | The feature request, expected outcome 3, matches lessons by output artifact and phase identifier | A lesson recorded against one phase is not shown to another phase, even when an artifact type is shared | `omn-product-owner`, under its scope decision right |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | What reduction in recurrence, if any, must lessons achieve before the business treats the loop as effective? The inputs state no numeric target; this change is judged on the per-lesson report existing and recording recurrence (`S-008`) | no | `omn-business-analyst`, on behalf of the requester | Scope Gate |
| `Q-002` | Is the change of default from opt-in to on, for runs planned after this change (`D-001`), accepted as a change to the runtime governance policy in `config/runtime.md`? | no | `omn-tech-lead`, as delivery and runtime policy owner | Scope Gate |

## Handoff

- Downstream owner: `planner`, which consumes the bounded scope for execution planning
- Gate: Scope Gate of `implement-feature`; the decision rests with `omn-business-analyst`, because the Producer Exclusion Rule applies to this artifact
- Evidence for the gate: `S-001` to `S-011`, `X-001` to `X-009`, `A-001` to `A-023`, `D-001` to `D-009`, `Q-001` and `Q-002`, and the check results in the result envelope
- Deferred to downstream: decomposition and delivery sequence (`planner`); carrier module, store layout, plan-flag location, fingerprint encoding, threshold configuration, and command names (`architect`); test strategy and execution of the verification methods (`omn-qa`)
