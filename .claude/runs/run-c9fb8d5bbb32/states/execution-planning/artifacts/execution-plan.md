```yaml
plan:
  planId: run-c9fb8d5bbb32-knowledge-loop-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/knowledge-loop-feature-request.md
    - type: product-requirement
      reference: runs/run-c9fb8d5bbb32/states/scope-and-acceptance/artifacts/scope-definition.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:e7a9416b2344d53a4264e32b5a976681
  contextDigest: sha256:2945ec39a62c55e1f979d25b41ca92b0
# Upstream identifier notation. The approved scope definition SCOPE-2026-0001 (digest
# sha256:7bca33ce5e27316b26b53f78e44cbb11) uses identifier families that collide with this
# plan's registers, so its items are cited in a distinct form: scope items SC-001 to SC-011,
# acceptance criteria AC-001 to AC-023, exclusions X-001 to X-009, decisions D-001 to D-009,
# open questions SQ-001 and SQ-002. Every bare S-nnn, A-nnn, R-nnn, T-nnn, Q-nnn token in this
# artifact resolves against this plan's own registers.
# Affected areas from the task context: performance, security (S08 and S09 cited in 10.2).
# Repository reads: the paths named by the architecture context were confirmed present, and the
# scan rule of runtime/optimize_memory.py was read (Markdown files only). No wider rescan.
```

## Executive Summary

The framework gains a closed knowledge loop: failures recorded in run evidence become governed lessons that later dispatches of the matching phase are shown, for the operators and agents of later runs. Success is that a phase whose output has an eligible lesson receives it in its envelope and prompt with no operator step, that runs planned before the change dispatch exactly as today, and that a per-lesson report shows whether the failure recurred after agents were warned. The work decomposes into twenty-seven tasks across twelve execution waves, opening with an inventory of the recorded evidence and the decision on how a run's plan records its hydration choice. The highest-impact risk is `R-006`: a dispatch or plan change that alters the envelope, prompt, or idempotency key of a run planned before the change would fail the replay checks and break the additive-only constraint. Six design-phase tasks, among them the store, recall, plan-choice, and aggregation decisions, are routed to `architect` rather than decided here. Plan status is complete; three open questions are recorded, none blocking, and eleven tasks are assumption-dependent until `A-001` through `A-010` are confirmed.

## Business Objectives

1. Agents of later runs are shown the failure patterns earlier runs recorded against their phase before they write, without an operator carrying them by hand; received by operators and dispatched agents; measured as a recorded `C3.2` or `C7.1` failure reaching the next dispatch of its phase with no operator step. Traces to `S-002`, `S-003`, `S-009`, `S-012`, `S-013`.
2. Operators control which lessons agents see, and no lesson history is lost; received by operators; measured as only approved or recurring lessons being shown, retired lessons never being shown, and no lesson record ever being removed. Traces to `S-006`, `S-007`, `S-008`.
3. The framework shows whether its learning works; received by operators and the requester; measured as a per-lesson count of dispatches shown the lesson and of later recurrences of its failure. Traces to `S-010`, `S-011`.
4. Existing runs, gates, and verifiers keep their behaviour; received by every operator of an existing run; measured as runs planned before the change dispatching unchanged and every verifier staying at its recorded baseline. Traces to `S-014`, `S-017`.

## Technical Objectives

- Harvest is deterministic and idempotent: one lesson per fingerprint, and unchanged evidence yields a byte-identical store. Verified by AC-002, AC-005, AC-006. Traces to business objectives 1 and 2, and to `S-004`, `S-005`, `S-016`.
- A lesson record carries only its declared fields, so free text from evidence never reaches the store or a prompt. Verified by AC-004 and the review in `T-019`. Traces to business objectives 1 and 2, and to `S-029`.
- Eligibility is a function of lesson status, distinct-run count, and a configured threshold alone. Verified by AC-011, AC-012, AC-013. Traces to business objective 2 and to `S-007`, `S-021`.
- Recall is phase-scoped, capped at five, ordered by distinct-run count with deterministic ties, and renders a bounded prompt section. Verified by AC-014, AC-015, AC-016, AC-017, AC-010. Traces to business objective 1 and to `S-009`, `S-022`, `S-026`, `S-027`.
- Dispatch output and idempotency key are unchanged for runs planned before the change and for runs whose plan switches hydration off. Verified by AC-018, AC-019, and the replay checks M12 and M14. Traces to business objective 4 and to `S-014`, `S-020`, `S-025`.
- Harvest runs on run aggregation and tolerates a repository without a runs directory. Verified by AC-021, AC-003. Traces to business objective 1 and to `S-012`, `S-030`.
- Effectiveness accounting attributes each later recurrence to the dispatches that were shown the lesson, and metrics record the hydrated count. Verified by AC-020, AC-022. Traces to business objective 3 and to `S-010`, `S-011`.
- The lesson store is unaffected by the memory optimization tool. Verified by AC-009. Traces to business objective 2 and to `S-031`.
- The change uses no model call and no dependency beyond the standard library, and alters no gate, validator, artifact contract, Phase Model table, or agent module text. Verified by the review in `T-016`. Traces to business objective 4 and to `S-017`, `S-018`, `S-019`.

## Scope

### In Scope

- One lesson per recurring failure pattern with its counts, dates, description, and evidence references (SC-001; `S-004`, `S-015`, `S-023`, `S-029`, `S-030`). Covered by `T-001`, `T-002`, `T-003`.
- Idempotent re-harvest with fingerprint upsert (SC-002; `S-005`, `S-016`). Covered by `T-002`, `T-003`.
- Operator approve, retire, and annotate commands with owner, rationale, history, and no deletion (SC-003; `S-006`, `S-008`, `S-024`, `S-031`). Covered by `T-002`, `T-004`.
- Eligibility by approval or by recurrence in at least two distinct runs; retired lessons never eligible (SC-004; `S-007`, `S-021`). Covered by `T-005`.
- Phase-scoped hydration of at most five lessons into the memory slice and a bounded prompt section (SC-005; `S-009`, `S-013`, `S-022`, `S-026`, `S-027`). Covered by `T-006`, `T-007`.
- Unchanged dispatch for runs planned before the change or with hydration off (SC-006; `S-014`, `S-025`). Covered by `T-013`, `T-014`, `T-015`.
- Hydration on by default for runs planned after the change, recorded in the plan, with an off flag (SC-007; `S-020`). Covered by `T-013`, `T-017`.
- Per-lesson effectiveness report (SC-008; `S-010`). Covered by `T-008`, `T-009`.
- Harvest on run aggregation with no operator step (SC-009; `S-012`). Covered by `T-011`, `T-012`.
- Lessons-hydrated count in execution metrics (SC-010; `S-011`). Covered by `T-010`.
- Memory and runtime-policy documents describe the implemented loop (SC-011; `S-028`). Covered by `T-020`.
- Self-hosting delivery: runtime version increment, mirror refresh, change proposal, release checklist (`S-032`). Covered by `T-021`, `T-022`, `T-023`, `T-024`.
- Validation of all twenty-three scope criteria (`S-033`). Covered by `T-025`, `T-026`, `T-027`, `T-015`.
- Additive-only and no-model constraints confirmed on the delivered change set (`S-017`, `S-018`, `S-019`). Covered by `T-016`.

### Out of Scope

- Model calls, embeddings, vector stores, or network dependencies (X-001). Excluded by the standard-library and no-model constraint (`S-018`, `S-019`).
- Automatic change to validators, templates, gate rules, or agent module text from a lesson (X-002). Excluded because lessons inform agents and operators only.
- Harvesting from sources other than recorded run evidence (X-003). Excluded by the business intent non-goal.
- Gate-approval waits as lessons (X-004). Excluded because approval waits are normal flow (`S-023`).
- Hydrating or backfilling runs planned before the change (X-005). Excluded because those runs must dispatch unchanged (`S-025`).
- Changes to gates, validators, artifact contracts, Phase Model tables, or agent module text (X-006). Excluded by the additive-only constraint (`S-017`).
- Automatic retirement of lessons (X-007). Excluded because retirement is an operator action.
- Deletion of lesson records (X-008). Excluded because retired lessons keep their history.
- Graphical, hosted, or web reporting (X-009). Excluded because a command-line report is required only.

### Deferred

- A numeric recurrence-reduction target that the effectiveness report is judged against (SQ-001). Brought into scope when the requester states a target through `omn-business-analyst`; until then the report records recurrence without a pass threshold.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The evidence fields the architecture context names (failing check IDs and report reference on validation failures, gate and target on rollbacks, check descriptions in validation reports) are present in every run on disk, older runs included | `S-001`, `S-004` | Harvest needs per-shape handling for older runs; `T-001` lists the variants and `T-003` grows | architect |
| A-002 | The recorded `C3.2` and `C7.1` failures each resolve to an artifact type from the evidence on disk | `S-015` | AC-001 cannot be met over recorded evidence and the scope owner must restate it | architect |
| A-003 | A run's plan can record the hydration choice so that a plan lacking the record identifies a run planned before the change | `S-020`, `S-025` | Pre-change detection needs another signal; `T-013` and `T-017` change | architect |
| A-004 | Replay checks M12 and M14 replay a run planned before the change, so they stay on the unhydrated path | `S-014` | Replay baselines would change, breaching `S-017`; `T-015` fails | omn-qa |
| A-005 | The default change from opt-in to on for runs planned after the change (SQ-002) is accepted at the Scope Gate | `S-020` | Hydration defaults off; `T-013`, `T-017`, `T-018`, `T-020` change their stated default | omn-tech-lead |
| A-006 | Harvesting all recorded runs at each aggregation costs little enough that no incremental harvest is needed; no budget is stated | `S-012` | `T-011` must define an incremental harvest and `T-012` grows | architect |
| A-007 | A dispatch baseline can be captured from the runtime as committed before the change, for the phases AC-018 compares | `S-014` | AC-018 needs a different reference and `T-014` changes | omn-qa |
| A-008 | Updating `config/runtime.md` and the `memory/` documents is not a change to a gate, validator, artifact contract, Phase Model table, or agent module text | `S-017`, `S-028` | `T-020` needs a separate change request | omn-tech-lead |
| A-009 | AC-018 byte identity is judged after normalising the fields that already vary per dispatch today: build timestamps and the runtime version stamp | `S-014`, `S-032` | The version increment in `T-021` breaks AC-018 as literally worded; see `Q-002` | omn-product-owner |
| A-010 | The bundled payload mirror carries `memory/` contents, so a store committed under `memory/` reaches installed copies | `S-006`, `S-032` | Installed copies receive no lessons and `T-022` acceptance changes; see `Q-001` | omn-tech-lead |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | SQ-002 is rejected at the Scope Gate (`A-005` false) | Hydration defaults off; plan-flag semantics and documentation change after design | low | T-013, T-017, T-018, T-020 | `T-013` records the default as one decision point so either answer is a single change | omn-tech-lead |
| R-002 | requirement | Recorded `C3.2` or `C7.1` failures do not resolve to an artifact type (`A-002` false) | AC-001 cannot be met over recorded evidence | low | T-001, T-027 | `T-001` confirms both before design closes; the scope owner restates AC-001 if not | omn-product-owner |
| R-003 | requirement | A failure recurs in a retry of the same phase and run that was shown the lesson | The effectiveness report over- or under-counts recurrence and misleads the business | medium | T-008, T-009 | `T-008` defines the attribution rule for retries, rollbacks, and later runs | architect |
| R-004 | requirement | The documentation update is judged a change to a governed contract (`A-008` false) | `T-020` waits on a separate change request and AC-023 slips | low | T-020 | `T-016` checks the change set against the additive-only surfaces and records the verdict | omn-tech-lead |
| R-005 | technical | Older runs record evidence in a different shape (`A-001` false) | Lessons are missed or miscounted | medium | T-001, T-002, T-003 | `T-001` inventories shapes per run before the store contract is fixed | architect |
| R-006 | technical | A dispatch or plan change alters the envelope, prompt, or idempotency key of a run planned before the change (`A-003`, `A-004`, `A-007` false) | Replay checks fail and a verifier loses its baseline, breaching the additive-only constraint | medium | T-007, T-013, T-014, T-015, T-017 | `T-013` defines pre-change detection, `T-014` captures the baseline, `T-015` verifies | architect |
| R-007 | technical | Harvest output varies with ordering, timestamps, or platform line endings | AC-005 fails and every harvest rewrites the store | medium | T-002, T-003, T-012 | `T-002` fixes the serialisation rules; AC-005 is tested in `T-026` | architect |
| R-008 | security | Free text from evidence carrying a credential-like string reaches the store or a prompt | Sensitive content is persisted and shown to later agents | medium | T-002, T-003, T-007, T-019 | `T-002` restricts records to declared fields; `T-019` reviews the flow; AC-004 tests it | omn-dev-2-reviewer |
| R-009 | security | Operator-written remedy text or a check description is read by an agent as an instruction | Later agents act on injected directions | low | T-004, T-006, T-007, T-019 | `T-006` defines rendering of lesson text as data; `T-019` reviews it | architect |
| R-010 | operational | Harvest fails during run aggregation | Run aggregation is blocked or its outputs are corrupted | low | T-011, T-012 | `T-011` defines how a harvest failure is isolated from aggregation | architect |
| R-011 | operational | Harvest cost grows with the number of recorded runs (`A-006` false) | Every aggregation slows | low | T-011, T-012 | `T-011` states the cost bound or defines incremental harvest | architect |
| R-012 | operational | The memory optimization tool or a later scan rule rewrites the lesson store | Lesson records are mangled | low | T-002, T-026 | `T-002` places the store outside the tool's scan; AC-009 tests it | architect |
| R-013 | delivery | The runtime version increment changes the version stamp in pre-change dispatch output (`A-009` false) | AC-018 fails as literally worded | medium | T-014, T-015, T-021 | `Q-002` settles the comparison; `T-014` records the normalised fields | omn-product-owner |
| R-014 | delivery | The bundled mirror is not refreshed after the last framework edit | The bundled payload test fails and a suite run of about 26 minutes is repeated | medium | T-015, T-022 | `T-022` depends on every framework edit in the change set | omn-dev-1-implement |

## Task Breakdown

### T-001 Inventory the recorded run evidence the harvest reads

- Owner: architect
- Complexity: S (confidence: low)
- Depends on: none
- Traces to: S-001, S-003, S-004, S-015, A-001, A-002
- Status: assumption-dependent
- Description: A record exists of the evidence shapes on disk that harvest consumes, per source and per run, with the counts the feature request cites reconciled.
- Acceptance Criteria:
  - Each source (run events, recovery ledgers, validation reports) is listed with the fields harvest needs and the runs that lack any of them
  - The count of recorded validation failures and the runs carrying them is stated
  - At least one `C3.2` failure and one `C7.1` failure are named with the artifact type each resolves to, or their absence is recorded
  - Approval-wait events are identified as excluded
- Gate: Design Gate

### T-002 Define the lesson store contract

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-004, S-005, S-006, S-023, S-029, S-031
- Status: ready
- Description: An approved contract states the lesson record, its fingerprint for each pattern kind, its lifecycle and history, its store location under `memory/`, and its serialisation rules.
- Acceptance Criteria:
  - The fingerprint is stated for artifact-type-plus-check patterns and for gate-plus-phase patterns
  - The record's fields are an explicit closed list that admits no free text taken from evidence
  - The states candidate, active, and retired, the owner, the rationale, the optional remedy, and the history entry are defined
  - Serialisation rules make two writes of the same lessons byte-identical
  - The store location lies outside the memory optimization tool's scan and outside the runs directory
  - Where the eligibility threshold is configured is stated
- Gate: Design Gate

### T-003 Deliver lesson harvest with fingerprint upsert

- Owner: omn-dev-1-implement
- Complexity: L (confidence: low)
- Depends on: T-002
- Traces to: S-004, S-005, S-015, S-016, S-023, S-029, S-030, A-001
- Status: assumption-dependent
- Description: A harvest capability reads recorded run evidence and upserts one lesson per fingerprint into the store per the approved contract.
- Acceptance Criteria:
  - AC-001, AC-002, AC-003, AC-004, AC-005, AC-006 hold on the delivered capability
  - A harvest after an approval or annotation leaves status, owner, rationale, and remedy unchanged (AC-008)
  - No lesson is created from an approval wait
- Gate: Review Gate

### T-004 Deliver the lesson governance commands

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-002, T-003
- Traces to: S-006, S-008, S-024
- Status: ready
- Description: Operators can approve, retire, and annotate a named lesson from the command line, with every change recorded in its history and nothing removed.
- Acceptance Criteria:
  - AC-007 holds for each of the three commands
  - AC-008 holds for a lesson approved and annotated before a harvest
  - A command naming an unknown lesson leaves the store unchanged and reports the failure
- Gate: Review Gate

### T-005 Deliver hydration eligibility evaluation

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-007, S-021
- Status: ready
- Description: Eligibility of a lesson is evaluated from its status, distinct-run count, and the configured threshold, with a default threshold of two.
- Acceptance Criteria:
  - AC-011, AC-012, AC-013 hold
  - The threshold is read from the location the store contract names
- Gate: Review Gate

### T-006 Define the recall selection contract

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-002
- Traces to: S-009, S-022, S-024, S-026, S-027
- Status: ready
- Description: An approved contract states how a dispatch matches, ranks, caps, records, and renders lessons in the memory slice and the prompt section.
- Acceptance Criteria:
  - Matching requires both the phase identifier and the phase's output artifact type
  - Ranking by distinct-run count and the deterministic tie-break are stated
  - The memory slice fields for a hydrated dispatch are listed, including the record of which lessons were shown
  - The prompt section is bounded at one heading line and two lines per lesson, with and without a remedy
  - Lesson text is rendered as quoted data that the section labels as such
- Gate: Design Gate

### T-007 Deliver lesson hydration at dispatch

- Owner: omn-dev-1-implement
- Complexity: L (confidence: medium)
- Depends on: T-005, T-006, T-013, T-014, T-017
- Traces to: S-002, S-009, S-013, S-022, S-024, S-026, S-027
- Status: ready
- Description: A dispatch of a run whose plan has hydration on carries the selected eligible lessons in its memory slice and its prompt section; other dispatches are unchanged.
- Acceptance Criteria:
  - AC-010, AC-014, AC-015, AC-016, AC-017 hold
  - A run planned before the change or with hydration off produces the captured baseline output (AC-018)
  - A flag-off dispatch carries a memory slice with hydrated false and a reason naming the plan flag (AC-019)
- Gate: Review Gate

### T-008 Define the lesson effectiveness attribution rule

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: T-002, T-006
- Traces to: S-010
- Status: ready
- Description: An approved rule states which dispatches count as shown a lesson and which later failures count as recurrences after being shown.
- Acceptance Criteria:
  - The rule covers retries within one phase and run, rollbacks, and later runs
  - The rule names the evidence each count is drawn from
  - Applying the rule to the AC-020 fixture by hand yields 3 shown and 1 recurrence
- Gate: Design Gate

### T-009 Deliver the lesson effectiveness report

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-003, T-007, T-008
- Traces to: S-010
- Status: ready
- Description: A command-line report lists, per lesson, the dispatches shown the lesson and the later recurrences of its failure, per the attribution rule.
- Acceptance Criteria:
  - AC-020 holds
  - A lesson never shown reports zero shown dispatches
- Gate: Review Gate

### T-010 Record lessons hydrated in execution metrics

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-007
- Traces to: S-011
- Status: ready
- Description: Each invocation's execution metrics carry a lessons-hydrated count equal to the lessons in its memory slice.
- Acceptance Criteria:
  - AC-022 holds for hydrated and unhydrated invocations
  - An invocation dispatched with hydration off records a lessons-hydrated count of zero
- Gate: Review Gate

### T-011 Define harvest at run aggregation

- Owner: architect
- Complexity: S (confidence: low)
- Depends on: T-002
- Traces to: S-012, A-006
- Status: assumption-dependent
- Description: An approved decision states when aggregation invokes harvest, the cost bound it accepts, and how a harvest failure is isolated from aggregation.
- Acceptance Criteria:
  - The aggregation point that triggers harvest is named
  - The decision states whether harvest is full or incremental and why
  - The outcome of aggregation when harvest fails is stated
- Gate: Design Gate

### T-012 Deliver harvest at run aggregation

- Owner: omn-dev-1-implement
- Complexity: S (confidence: low)
- Depends on: T-003, T-011
- Traces to: S-012, A-006
- Status: assumption-dependent
- Description: Aggregating a run harvests its evidence, so its lessons are available to the next dispatch with no operator step.
- Acceptance Criteria:
  - AC-021 holds
  - A harvest failure produces the aggregation outcome the decision states
- Gate: Review Gate

### T-013 Define how a run's plan records its hydration choice

- Owner: architect
- Complexity: M (confidence: low)
- Depends on: none
- Traces to: S-014, S-020, S-025, A-003, A-005
- Status: assumption-dependent
- Description: An approved decision states where a plan records hydration on or off, how a plan without the record is treated as planned before the change, and the default.
- Acceptance Criteria:
  - The plan flag, its default for new plans, and how an operator sets it off are stated
  - The decision states why a pre-change run's envelope, prompt, and idempotency key cannot change
  - The default is stated once, so `R-001` resolves as a single change
- Gate: Design Gate

### T-014 Capture the pre-change dispatch baseline

- Owner: omn-dev-1-implement
- Complexity: S (confidence: low)
- Depends on: T-013, T-025
- Traces to: S-014, A-007, A-009
- Status: assumption-dependent
- Description: A stored baseline of dispatch envelope, prompt, and idempotency key, taken from the runtime as committed before the change, exists for the cases AC-018 compares.
- Acceptance Criteria:
  - The baseline names the runtime revision it was taken from
  - The baseline covers a run planned before the change
  - Any field normalised before comparison is listed with the reason
- Gate: Review Gate

### T-015 Verify unchanged behaviour for runs planned before the change

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: T-014, T-022, T-026
- Traces to: S-014, S-017, A-004, A-009
- Status: assumption-dependent
- Description: Recorded evidence shows that runs planned before the change dispatch as the baseline and that every verifier stays at its recorded baseline.
- Acceptance Criteria:
  - AC-018 passes against the stored baseline
  - Replay checks M12 and M14 pass unchanged
  - The full unit suite passes and every verifier reports its recorded baseline
  - The evidence names the revision tested
- Gate: Verification Gate

### T-016 Review the change set against the additive-only constraint

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: high)
- Depends on: T-022
- Traces to: S-017, S-018, S-019
- Status: ready
- Description: A recorded verdict states whether the change set leaves gates, validators, artifact contracts, Phase Model tables, and agent module text unchanged, calls no model, and adds no dependency beyond the standard library.
- Acceptance Criteria:
  - Each protected surface is checked against the change set with a result recorded per surface
  - No added import or call reaches beyond the standard library or a model
  - The verdict states whether the documentation edits fall outside the protected surfaces
- Gate: Review Gate

### T-017 Deliver the plan-time hydration choice

- Owner: omn-dev-1-implement
- Complexity: S (confidence: low)
- Depends on: T-013
- Traces to: S-020, S-025, A-005
- Status: assumption-dependent
- Description: A plan created after the change records hydration on unless the operator sets the flag off, and plans created before the change are untouched.
- Acceptance Criteria:
  - AC-019 holds for both plan fixtures
  - No existing plan file is rewritten
- Gate: Review Gate

### T-018 Publish the release note

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-020, T-027
- Traces to: S-020, S-032
- Status: ready
- Description: A release note states what the knowledge loop adds, the new default for runs planned after the change, how to switch it off, and how to govern lessons.
- Acceptance Criteria:
  - The note names the runtime version that introduces the loop
  - The note states that runs planned before the change are unaffected
  - The note carries the verification outcome recorded in `T-027`
- Gate: Closure Gate

### T-019 Review lesson content flow for exposure

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: high)
- Depends on: T-003, T-004, T-007
- Traces to: S-024, S-029
- Status: ready
- Description: A recorded verdict states whether evidence text can reach the store or a prompt outside the declared fields, and whether lesson text is rendered as data.
- Acceptance Criteria:
  - Every path from evidence to store and from store to prompt is traced with a finding per path
  - The AC-004 test is confirmed to search every store file
  - Remedy text rendering is confirmed to follow the recall contract
- Gate: Review Gate

### T-020 Document the lesson category in the governing documents

- Owner: omn-documentation
- Complexity: S (confidence: low)
- Depends on: T-004, T-005, T-007, T-017
- Traces to: S-028, A-008
- Status: assumption-dependent
- Description: `memory/README.md`, `memory/memory-governance.md`, `memory/memory-resolver.md`, and `config/runtime.md` describe the lesson category as implemented.
- Acceptance Criteria:
  - AC-023 holds for all four documents
  - The Memory Loading and Writeback Policy sections of `config/runtime.md` state the new default for runs planned after the change
  - `runtime/README.md` and agent module text are unchanged
- Gate: Review Gate

### T-021 Increment the runtime version

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: low)
- Depends on: T-014
- Traces to: S-032, A-009
- Status: assumption-dependent
- Description: The framework runtime reports a version above 0.9.0 for the delivered change.
- Acceptance Criteria:
  - The reported runtime version is incremented once
  - The baseline in `T-014` was captured before the increment
- Gate: Review Gate

### T-022 Refresh the bundled payload mirror

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: low)
- Depends on: T-003, T-004, T-005, T-007, T-009, T-010, T-012, T-017, T-020, T-021
- Traces to: S-032, A-010
- Status: assumption-dependent
- Description: The bundled payload mirror matches the framework directory after the last framework edit, refreshed by its sync procedure rather than by hand.
- Acceptance Criteria:
  - The bundled payload test passes
  - No file under the mirror was edited other than by the sync procedure
- Gate: Review Gate

### T-023 Confirm the framework release checklist passes

- Owner: omn-qa
- Complexity: S (confidence: medium)
- Depends on: T-024
- Traces to: S-032
- Status: ready
- Description: Recorded evidence shows `validation/framework-release-checklist.md` satisfied for this change.
- Acceptance Criteria:
  - The release checklist verification reports pass
  - Any item recorded as not applicable names its reason
- Gate: Closure Gate

### T-024 Author the framework change proposal

- Owner: omn-documentation
- Complexity: M (confidence: medium)
- Depends on: T-015, T-016, T-019, T-027
- Traces to: S-032
- Status: ready
- Description: A change proposal under `proposals/`, authored from `templates/framework-change-proposal.md`, links the artifacts of this run.
- Acceptance Criteria:
  - The proposal passes `runtime/change_proposal_validator.py`
  - The proposal links the verification evidence from `T-015` and `T-027`
- Gate: Closure Gate

### T-025 Define the validation strategy for the twenty-three scope criteria

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-002, T-006, T-008, T-011, T-013
- Traces to: S-033
- Status: ready
- Description: A validation strategy names, for each of AC-001 through AC-023, the check, its fixture, the evidence it produces, and its pass condition.
- Acceptance Criteria:
  - Each of AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-012, AC-013, AC-014, AC-015, AC-016, AC-017, AC-018, AC-019, AC-020, AC-021, AC-022, AC-023 has a named check and pass condition
  - The strategy states how AC-001 runs over a copy of recorded evidence rather than the live runs directory
  - The strategy states what the AC-018 baseline captures
- Gate: Design Gate

### T-026 Deliver the unit tests that carry the validation strategy

- Owner: omn-dev-1-implement
- Complexity: L (confidence: medium)
- Depends on: T-003, T-004, T-005, T-007, T-009, T-010, T-012, T-014, T-017, T-020, T-025
- Traces to: S-033
- Status: ready
- Description: Unit tests under the repository-root `tests/` directory implement every check the validation strategy names.
- Acceptance Criteria:
  - Every check named for AC-001 through AC-023 in the strategy has a test that passes
  - The tests use fixtures and never read or write the live runs directory
- Gate: Review Gate

### T-027 Record verification evidence for the scope criteria

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-026
- Traces to: S-033
- Status: ready
- Description: Recorded evidence states pass or fail for each scope criterion other than AC-018, which `T-015` records.
- Acceptance Criteria:
  - A result with its evidence is recorded for AC-001, AC-002, AC-003, AC-004, AC-005, AC-006, AC-007, AC-008, AC-009, AC-010, AC-011, AC-012, AC-013, AC-014, AC-015, AC-016, AC-017, AC-019, AC-020, AC-021, AC-022, AC-023
  - Command output listing the `C3.2` and `C7.1` lessons with all six fields is recorded for AC-001
- Gate: Verification Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | produces-consumes | The store contract binds to the inventoried evidence shapes |
| T-002 | T-003 | contract | Harvest writes the defined store |
| T-002 | T-004 | contract | The commands change fields the contract defines |
| T-003 | T-004 | produces-consumes | The commands act on harvested lessons |
| T-002 | T-005 | contract | Eligibility reads status, count, and threshold as defined |
| T-002 | T-006 | contract | Recall reads the defined record |
| T-005 | T-007 | produces-consumes | Selection consumes eligibility |
| T-006 | T-007 | contract | Hydration implements the recall contract |
| T-013 | T-007 | contract | Hydration honours the plan-choice decision |
| T-014 | T-007 | produces-consumes | The byte-identity criterion is judged against the captured baseline |
| T-017 | T-007 | produces-consumes | Hydration reads the recorded plan choice |
| T-002 | T-008 | contract | Attribution is keyed by the defined fingerprint |
| T-006 | T-008 | contract | Attribution reads the shown-lessons record the recall contract defines |
| T-003 | T-009 | produces-consumes | The report reads harvested lessons |
| T-007 | T-009 | produces-consumes | The report reads which dispatches were shown each lesson |
| T-008 | T-009 | contract | The report applies the attribution rule |
| T-007 | T-010 | produces-consumes | The count equals the lessons hydration selects |
| T-002 | T-011 | contract | The trigger invokes harvest as the contract defines it |
| T-003 | T-012 | produces-consumes | Aggregation invokes the delivered harvest |
| T-011 | T-012 | contract | The trigger follows the approved decision |
| T-013 | T-014 | contract | The baseline covers the cases the decision keeps unchanged |
| T-025 | T-014 | produces-consumes | The strategy states what the baseline captures |
| T-014 | T-015 | produces-consumes | Verification compares against the baseline |
| T-022 | T-015 | verification | The suite includes the bundled payload test over the refreshed mirror |
| T-026 | T-015 | produces-consumes | Verification runs the delivered tests |
| T-022 | T-016 | verification | The review assesses the complete change set |
| T-013 | T-017 | contract | The plan records the choice as decided |
| T-020 | T-018 | produces-consumes | The note cites the documented default and off switch |
| T-027 | T-018 | produces-consumes | The note carries the verification outcome |
| T-003 | T-019 | verification | The review traces evidence into the store |
| T-004 | T-019 | verification | The review covers operator-written remedy text |
| T-007 | T-019 | verification | The review traces store content into prompts |
| T-004 | T-020 | produces-consumes | The documents describe the delivered lifecycle |
| T-005 | T-020 | produces-consumes | The documents state the delivered threshold |
| T-007 | T-020 | produces-consumes | The documents describe delivered hydration |
| T-017 | T-020 | produces-consumes | The documents name the delivered plan flag |
| T-014 | T-021 | produces-consumes | The baseline must record the pre-increment version stamp |
| T-003 | T-022 | produces-consumes | The mirror carries the harvest change |
| T-004 | T-022 | produces-consumes | The mirror carries the command change |
| T-005 | T-022 | produces-consumes | The mirror carries the eligibility change |
| T-007 | T-022 | produces-consumes | The mirror carries the dispatch change |
| T-009 | T-022 | produces-consumes | The mirror carries the report change |
| T-010 | T-022 | produces-consumes | The mirror carries the metrics change |
| T-012 | T-022 | produces-consumes | The mirror carries the aggregation change |
| T-017 | T-022 | produces-consumes | The mirror carries the plan change |
| T-020 | T-022 | produces-consumes | The mirror carries the documentation change |
| T-021 | T-022 | produces-consumes | The mirror carries the version increment |
| T-024 | T-023 | produces-consumes | The release checklist requires a validated change proposal |
| T-015 | T-024 | produces-consumes | The proposal links the backward-compatibility evidence |
| T-016 | T-024 | produces-consumes | The proposal links the additive-only verdict |
| T-019 | T-024 | produces-consumes | The proposal links the exposure verdict |
| T-027 | T-024 | produces-consumes | The proposal links the criteria evidence |
| T-002 | T-025 | contract | Store checks bind to the store contract |
| T-006 | T-025 | contract | Recall checks bind to the recall contract |
| T-008 | T-025 | contract | Report checks bind to the attribution rule |
| T-011 | T-025 | contract | Aggregation checks bind to the trigger decision |
| T-013 | T-025 | contract | Compatibility checks bind to the plan-choice decision |
| T-025 | T-026 | produces-consumes | The tests implement the strategy |
| T-003 | T-026 | verification | Tests validate harvest |
| T-004 | T-026 | verification | Tests validate the commands |
| T-005 | T-026 | verification | Tests validate eligibility |
| T-007 | T-026 | verification | Tests validate hydration |
| T-009 | T-026 | verification | Tests validate the report |
| T-010 | T-026 | verification | Tests validate the metrics count |
| T-012 | T-026 | verification | Tests validate aggregation harvest |
| T-014 | T-026 | produces-consumes | The AC-018 test reads the baseline |
| T-017 | T-026 | verification | Tests validate the plan choice |
| T-020 | T-026 | verification | The AC-023 test searches the updated documents |
| T-026 | T-027 | produces-consumes | Evidence comes from the delivered tests |

### 8.2 External Dependencies

None identified. Every prerequisite is held by an agent inside the selected workflow; the recorded run evidence is repository content read through `T-001`, and the Scope Gate answers to SQ-001 and SQ-002 rest with that gate's owners.

### 8.3 Implementation Order

- Wave 1: T-001, T-013
- Wave 2: T-002, T-017
- Wave 3: T-003, T-005, T-006, T-011
- Wave 4: T-004, T-008, T-012
- Wave 5: T-025
- Wave 6: T-014
- Wave 7: T-007, T-021
- Wave 8: T-009, T-010, T-019, T-020
- Wave 9: T-022, T-026
- Wave 10: T-015, T-016, T-027
- Wave 11: T-018, T-024
- Wave 12: T-023

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because the plan delivers new framework functionality against an approved scope, carries five design decisions that need an approved technical approach, and closes with verification, documentation, and a change proposal; the change request routes `capability-addition` to this workflow.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | completed upstream; no task |
| `execution-planning` | this artifact |
| `solution-design-and-risk-assessment` | T-001, T-002, T-006, T-008, T-011, T-013, T-025 |
| `implementation` | T-003, T-004, T-005, T-007, T-009, T-010, T-012, T-014, T-017, T-020, T-021, T-022, T-026 |
| `quality-review` | T-015, T-016, T-019, T-027 |
| `documentation-and-release-handoff` | T-018, T-023, T-024 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

Under the Producer Exclusion Rule, the Design Gate decision rests with `omn-tech-lead`, because `architect` produces the evidence it assesses.

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| architecture-analysis | T-001 | architect | Primary |
| technical-approach-definition | T-002, T-006, T-008, T-011, T-013 | architect | Primary |
| structural-risk-analysis | T-013 | architect | Primary |
| implementation-delivery | T-003, T-004, T-005, T-007, T-009, T-010, T-012, T-014, T-017, T-021, T-022, T-026 | omn-dev-1-implement | Primary |
| validation-design | T-025 | omn-qa | Primary |
| quality-verification | T-015, T-023, T-027 | omn-qa | Primary |
| code-review | T-016, T-019 | omn-dev-2-reviewer | Primary |
| governance-enforcement | T-016 | omn-dev-2-reviewer | Primary |
| documentation | T-020, T-024 | omn-documentation | Primary |
| release-communication | T-018 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S02 | business/domain-modeling.md | T-001, T-002 | Primary |
| S01 | architecture/clean-architecture-checklist.md | T-002, T-006, T-011, T-013 | Primary |
| S07 | testing/testing-strategy.md | T-014, T-015, T-025, T-026, T-027 | Primary |
| S09 | security/secure-engineering.md | T-002, T-006, T-019 | Secondary |
| S08 | performance/performance-engineering.md | T-011 | Advisory |
| S12 | error-handling/error-handling-strategy.md | T-003, T-012 | Secondary |
| S11 | logging/observability-logging.md | T-010 | Secondary |
| S10 | git/git-collaboration.md | T-022, T-024 | Secondary |

## Acceptance Criteria

1. A recorded `C3.2` failure and a recorded `C7.1` failure each become a lesson that the next dispatch of the matching phase receives in its memory slice and prompt. Verifies business objective 1. Evidence: AC-001 and AC-014 results recorded at `T-027`.
2. A failure recurring in a newly aggregated run reaches the next dispatch with no harvest command run in between. Verifies business objective 1. Evidence: AC-021 result recorded at `T-027`.
3. Only approved or recurring lessons are shown, retired lessons are never shown, and every governance action leaves the lesson count unchanged with one history entry added. Verifies business objective 2. Evidence: AC-007, AC-008, AC-011, AC-012, AC-013 results recorded at `T-027`.
4. No free text from recorded evidence appears in the store, and lesson text reaches prompts only as labelled data. Verifies business objective 2. Evidence: AC-004 result at `T-027` and the exposure verdict at `T-019`.
5. For each lesson the framework reports the dispatches shown it and the later recurrences of its failure, and each invocation's metrics carry its hydrated count. Verifies business objective 3. Evidence: AC-020 and AC-022 results recorded at `T-027`.
6. Runs planned before the change, and runs planned with hydration off, dispatch as the stored baseline with an unchanged idempotency key, and every verifier stays at its recorded baseline. Verifies business objective 4. Evidence: the verification record at `T-015`.
7. The change set alters no gate, validator, artifact contract, Phase Model table, or agent module text, calls no model, and adds no dependency beyond the standard library. Verifies business objective 4. Evidence: the verdict at `T-016`.

## Definition of Done

- [ ] All seven plan acceptance criteria are verified with recorded evidence
- [ ] Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for `T-001` through `T-027` are satisfied or formally waived
- [ ] `A-001` through `A-010` are confirmed or converted to recorded decisions
- [ ] `R-001` through `R-014` are closed or accepted with named owners
- [ ] `Q-001`, `Q-002`, and `Q-003` are closed or explicitly accepted with the decision recorded
- [ ] The full unit suite passes and the bundled payload test passes over the refreshed mirror
- [ ] The change proposal passes its validator and the framework release checklist passes
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Should the lesson store harvested from this repository's runs ship to installed copies through the bundled payload, or ship empty so each installation learns from its own runs? | No | omn-tech-lead | T-002, T-022 |
| Q-002 | Is AC-018 byte identity judged after normalising build timestamps and the runtime version stamp, which already vary per dispatch and which the version increment changes? | No | omn-product-owner | T-014, T-015, T-021 |
| Q-003 | `implement-feature` has no phase before implementation that `omn-qa` owns; `T-025` is mapped to `solution-design-and-risk-assessment` so the strategy precedes the tests that carry it. Is that placement accepted? | No | omn-tech-lead | T-025 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 rejections and rollbacks are recorded in run evidence today | T-001 |
| S-002 no recorded evidence reaches a later dispatch; memory slice unhydrated | T-007 |
| S-003 the same mechanical rejection recurs; operators keep private notes | T-001 |
| S-004 harvest distils one fingerprinted lesson per recurring failure pattern | T-001, T-002, T-003 |
| S-005 re-harvest is idempotent through fingerprint upsert | T-002, T-003 |
| S-006 governed store under memory with candidate, active, retired, owner, rationale | T-002, T-004, A-010 |
| S-007 eligible when approved or recurring in the configured distinct-run count | T-005 |
| S-008 operators approve, retire, annotate; nothing deleted | T-004 |
| S-009 dispatch hydrates matched lessons into slice and prompt, ranked and capped | T-006, T-007 |
| S-010 per-lesson report of recurrence after being shown | T-008, T-009 |
| S-011 metrics record lessons hydrated per invocation | T-010 |
| S-012 harvest runs at aggregation with no operator step | T-011, T-012 |
| S-013 a phase with an eligible lesson receives it in envelope and prompt | T-007 |
| S-014 pre-change or flag-off runs dispatch unchanged | T-013, T-014, T-015 |
| S-015 harvesting current runs yields C3.2 and C7.1 lessons | T-001, T-003, A-002 |
| S-016 harvesting twice yields an identical store | T-003 |
| S-017 additive only | T-015, T-016, A-008 |
| S-018 runtime never calls a model | T-016 |
| S-019 standard library only | T-016 |
| S-020 D-001 hydration on by default, recorded in the plan, flag switches off | T-013, T-017, T-018, A-005 |
| S-021 D-002 automatic eligibility at two distinct runs | T-005 |
| S-022 D-003, D-004 at most five, highest distinct-run count, deterministic ties | T-006, T-007 |
| S-023 D-005 approval waits are not lessons | T-002, T-003 |
| S-024 D-006 remedy optional; without remedy shown with description alone | T-004, T-006, T-007, T-019 |
| S-025 D-007 pre-change runs never hydrate, plans not backfilled | T-013, T-017 |
| S-026 D-008 section bounded at one heading and two lines per lesson | T-006, T-007 |
| S-027 D-009 lesson reaches only its recorded phase and artifact type | T-006, T-007 |
| S-028 SC-011 governing documents describe the implemented loop | T-020 |
| S-029 lesson record holds only declared fields; credential-like text excluded | T-002, T-003, T-019 |
| S-030 no runs directory yields exit 0 and zero lessons | T-003 |
| S-031 memory optimization tool leaves lesson records unchanged | T-002 |
| S-032 self-hosting route, version increment, mirror sync, change proposal | T-021, T-022, T-023, T-024, T-018 |
| S-033 twenty-three scope criteria decide the change | T-025, T-026, T-027, T-015 |
| S-034 exclusions X-001 to X-009 bound the change | Scope, Out of Scope (context; no task) |
| AC-001 (S-033) | T-001, T-003, T-025, T-026, T-027 |
| AC-002 (S-033) | T-003, T-025, T-026, T-027 |
| AC-003 (S-033) | T-003, T-025, T-026, T-027 |
| AC-004 (S-033) | T-002, T-003, T-019, T-025, T-026, T-027 |
| AC-005 (S-033) | T-002, T-003, T-025, T-026, T-027 |
| AC-006 (S-033) | T-003, T-025, T-026, T-027 |
| AC-007 (S-033) | T-004, T-025, T-026, T-027 |
| AC-008 (S-033) | T-003, T-004, T-025, T-026, T-027 |
| AC-009 (S-033) | T-002, T-025, T-026, T-027 |
| AC-010 (S-033) | T-006, T-007, T-025, T-026, T-027 |
| AC-011 (S-033) | T-005, T-025, T-026, T-027 |
| AC-012 (S-033) | T-005, T-025, T-026, T-027 |
| AC-013 (S-033) | T-005, T-025, T-026, T-027 |
| AC-014 (S-033) | T-006, T-007, T-025, T-026, T-027 |
| AC-015 (S-033) | T-006, T-007, T-025, T-026, T-027 |
| AC-016 (S-033) | T-006, T-007, T-025, T-026, T-027 |
| AC-017 (S-033) | T-006, T-007, T-025, T-026, T-027 |
| AC-018 (S-033) | T-007, T-013, T-014, T-017, T-025, T-026, T-015 |
| AC-019 (S-033) | T-007, T-013, T-017, T-025, T-026, T-027 |
| AC-020 (S-033) | T-008, T-009, T-025, T-026, T-027 |
| AC-021 (S-033) | T-011, T-012, T-025, T-026, T-027 |
| AC-022 (S-033) | T-010, T-025, T-026, T-027 |
| AC-023 (S-033) | T-020, T-025, T-026, T-027 |
