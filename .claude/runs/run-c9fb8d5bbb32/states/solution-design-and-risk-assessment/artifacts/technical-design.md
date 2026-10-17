```yaml
design:
  designId: run-c9fb8d5bbb32-knowledge-loop-technical-design
  changeReference: runs/inputs/knowledge-loop-change-request.md
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/knowledge-loop-feature-request.md
    - type: change-request
      reference: runs/inputs/knowledge-loop-change-request.md
    - type: business-intent
      reference: runs/inputs/knowledge-loop-business-intent.md
    - type: architecture-context
      reference: runs/inputs/knowledge-loop-architecture-context.md
    - type: execution-plan
      reference: runs/run-c9fb8d5bbb32/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003, D-004, D-005]
  consumesPlan: runs/run-c9fb8d5bbb32/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:f8efa673a8795a3db6fc296d898e7c09
  contextDigest: sha256:15acab9bbb76151f78b5c74a2361a31c
# Identifier notation. Bare S, F, A, C, M, O, D, P, R, Q tokens resolve against this design's
# own registers. Upstream items are cited in a distinct form: scope acceptance criteria as
# AC-001 to AC-023 (scope definition digest sha256:7bca33ce5e27316b26b53f78e44cbb11), scope
# exclusions as X-001 to X-009, scope and plan decisions and questions by ordinal in words.
# Planner tasks T-001 to T-027 are cited, never created.
# Planning Gate rulings (omn-tech-lead), relayed with the dispatch, are normalised as S-029 to
# S-035; operator facts as S-036.
# Repository reads: the task context names no repository modules, so the sites named by the
# architecture context were read (runtime/framework_runtime.py cmd_dispatch, plan_run,
# build_context_slice, build_dispatch_prompt, maybe_aggregate; runtime/state_engine.py;
# runtime/execution_metrics.py; runtime/optimize_memory.py; runtime/verify_multi_phase.py).
# Rescan beyond them, reason: the payload-exclusion ruling names a dependency the context does
# not (omn_agent/source.py, tests/test_bundled_payload.py); the evidence inventory (T-001) read
# runs/*/events.jsonl, recovery-ledger.json and one validation-report.json.
# Skills: S03 was read; the runtime under change is not .NET (F-024), so it informs nothing
# here. S06 stays not-triggered: the lesson store is one JSON file, not a database.
```

## Metadata

- Feature or Change ID: run-c9fb8d5bbb32 (/implement, implement-feature v1.0.0, change class capability-addition)
- Author: architect 1.0.0
- Reviewers: omn-tech-lead, omn-architect (Design Gate); omn-qa for the test strategy focus areas
- Last Updated: 2026-10-09

## Objective

- Desired outcome: Recorded run evidence becomes governed lessons that later dispatches of the matching phase receive as data, while every run planned before the change dispatches exactly as under runtime 0.9.0.
- Architectural objectives:
  - One new runtime boundary, `runtime/knowledge.py`, owns harvest, store, governance, eligibility, recall selection, and effectiveness accounting, depends only on the standard library and evidence files, and is depended on one-way by `runtime/framework_runtime.py` (S-001, S-014, S-015, S-036).
  - A deterministic, governed lesson store contract lives under `memory/`, outside the memory optimizer's scan and outside the shipped payload (S-002, S-003, S-004, S-024, S-025, S-031).
  - A run-level hydration record is fixed once at plan time in run state, and an absent record means a pre-change run that never hydrates (S-011, S-029, S-032).
  - Lessons reach a dispatch only through `memory_slice`, an optional bounded prompt section, and one `invocation_started` detail key, none of which enters the payload digest (S-007, S-021, S-022, S-030, S-033).
  - Harvest attaches to run aggregation as an isolated post-step that cannot fail or alter aggregation (S-010, S-034).
  - Effectiveness and per-invocation counts derive from append-only invocation evidence (S-008, S-009).
  - Governance actions are operator commands over an append-only history, and nothing is deleted (S-005, S-006, S-018).
- In scope: harvest, store, governance, eligibility, recall at dispatch, run-level record and plan flag, aggregation hook, effectiveness report, metrics count, payload exclusion, documentation of the category, version increment, mirror refresh, test strategy.
- Out of scope:
  - Model calls, embeddings, vector stores, network access (S-020; X-001).
  - Automatic change to validators, templates, gate rules, or agent module text from a lesson (S-020; X-002).
  - Evidence sources other than recorded run evidence (S-020; X-003); approval waits as lessons (S-023; X-004).
  - Hydrating or backfilling runs planned before the change (S-011; X-005).
  - Any change to gates, validators, artifact contracts including the execution-plan contract, Phase Model tables, or agent module text (S-013, S-032; X-006).
  - Automatic retirement, deletion of lesson records, graphical reporting (S-006; X-007, X-008, X-009).
  - Any edit to a context-slice member file, including `runtime/README.md` and the registries (S-026, S-030).
  - Any change to `context_slice` content or to `input_contract` for any run (S-030).
  - Incremental harvest; deferred until evidence shows the full harvest is too costly (S-010).

## Requirements Summary

- Functional requirements:
  - Harvest distils one lesson per fingerprint from events, recovery ledgers, and validation reports (S-001, S-002, S-012, S-023).
  - Re-harvest is idempotent by fingerprint upsert (S-003).
  - Store under `memory/` with candidate, active, retired, owner, rationale, optional remedy, history; approve, retire, annotate from the command line; nothing deleted (S-004, S-006).
  - Eligible when active, or when candidate and recurring in at least the configured distinct-run count, default 2; retired never eligible (S-005, S-018).
  - Dispatch hydrates matched lessons by phase identifier and output artifact type into `memory_slice` and a prompt section, ranked and capped at five (S-007, S-021).
  - Per-lesson report of dispatches shown the lesson and later recurrences (S-008); lessons hydrated per invocation in execution metrics (S-009).
  - Harvest on run aggregation with no operator step (S-010).
  - Hydration on by default only for runs planned after the change, recorded per run at plan time, switched off by a plan flag (S-029).
- Non-functional requirements:
  - Determinism: unchanged evidence yields a byte-identical store (S-003).
  - Backward compatibility: pre-change and flag-off runs dispatch byte-identically after the closed normalisation list; idempotency key exact; M12 and M14 unmodified (S-011, S-022, S-030).
  - Standard library only, no model call (S-014, S-015).
  - Prompt growth bounded; lesson text rendered as labelled data (S-007, S-033).
  - Aggregation availability: a harvest failure never fails or corrupts aggregation (S-034).
  - Harvest cost proportional to recorded evidence; no budget stated (S-010).
  - Lessons of this repository never ship to installed copies (S-031).
- Acceptance criteria:
  - AC-001 to AC-006 bind harvest and idempotency (S-001, S-003, S-012).
  - AC-007 to AC-010 bind governance, optimizer isolation, and remedy rendering (S-006, S-025, S-033).
  - AC-011 to AC-013 bind eligibility (S-005).
  - AC-014 to AC-017 bind recall and the section bound (S-007).
  - AC-018 and AC-019 bind backward compatibility and the plan flag (S-011, S-029, S-030).
  - AC-020 binds effectiveness (S-008); AC-021 aggregation harvest (S-010); AC-022 metrics (S-009); AC-023 documentation (S-026).
  - The plan's seven acceptance criteria are cited, not restated, from the execution plan (digest sha256:13107a308ca6cec3bfc8f1e03c31ddd7) (S-035).

Statements (normalised from the supplied inputs, in input order):

| ID | Statement | Source |
|---|---|---|
| S-001 | Harvest reads events, recovery ledgers, and validation reports and distils one lesson per recurring failure pattern, keyed by artifact type plus check ID or gate plus phase | feature request, outcome 1 |
| S-002 | A lesson carries occurrence count, distinct-run count, first and last seen, the check description, and evidence references | feature request, outcome 1 |
| S-003 | Re-harvesting unchanged evidence is idempotent; two harvests produce an identical store | feature request, outcome 1 and acceptance intent |
| S-004 | Lessons live in a governed store under memory/ with statuses candidate, active, retired, an owner, and a rationale | feature request, outcome 2 |
| S-005 | A lesson is eligible when approved, or automatically when it recurs in at least a configured number of distinct runs | feature request, outcome 2 |
| S-006 | Operators approve, retire, or annotate a lesson from the command line; nothing is deleted; retired lessons keep history | feature request, outcome 2 |
| S-007 | Dispatch hydrates lessons matched by output artifact and phase into memory_slice and a short prompt section, ranked and capped | feature request, outcome 3 |
| S-008 | The loop reports, per lesson, how often the failure recurred in a dispatch already shown the lesson | feature request, outcome 4 |
| S-009 | Execution metrics record lessons hydrated per invocation | feature request, outcome 4 |
| S-010 | Harvest runs when a run aggregates, with no operator step | feature request, outcome 5 |
| S-011 | A run planned before the change, or with hydration off, dispatches byte-identically to today | feature request, acceptance intent |
| S-012 | Harvesting the current runs produces lessons for the recorded C3.2 and C7.1 failures | feature request, acceptance intent |
| S-013 | Additive only: gates, validators, artifact contracts, Phase Model tables, agent module text unchanged | feature request, constraints |
| S-014 | The runtime never calls a model; lessons are derived mechanically | feature request, constraints |
| S-015 | Standard library only; no vector store, embedding, or network dependency | feature request, constraints |
| S-016 | The change is capability-addition, framework-internal, routed through /implement | change request |
| S-017 | Surfaces: a new runtime module, framework_runtime hooks and version increment, execution_metrics, memory/ store and documents, config/runtime.md, tests, bundled mirror refresh | change request |
| S-018 | Only recurring or approved lessons are shown, and stale ones can be retired | business intent |
| S-019 | No gate, validator, or acceptance rule is weakened; every verifier stays at its baseline | business intent |
| S-020 | Non-goals: model fine-tuning or calls, automatic validator or template or agent-text change, non-run sources | business intent |
| S-021 | Lessons are data carried in the envelope and rendered into the dispatch prompt | architecture context |
| S-022 | The idempotency key must survive a rollback; M12 and M14 replay run-c5a8d50d3238; a run whose request predates the opt-in dispatches as today | architecture context |
| S-023 | Approval waits are normal flow; check descriptions resolve from any report of the same artifact type | architecture context |
| S-024 | runs/ and proposals/ are excluded from the payload, so the store lives under memory/, and harvest tolerates a repository with no runs/ | architecture context |
| S-025 | The memory optimizer must not mangle a machine-maintained store | architecture context |
| S-026 | Loading policy stays in runtime and config/; new documentation goes to config/runtime.md and memory/ documents, not runtime/README.md | architecture context |
| S-027 | Edit the framework directory, then refresh the mirror by its sync procedure; never hand-edit the mirror | architecture context |
| S-028 | Artifact validators reject the host vendor substring; paths are written without the dot-directory prefix | architecture context |
| S-029 | Hydration is on by default only for runs planned after this change, recorded per run at plan time, never inferred at dispatch; no record means never hydrate; a plan flag switches it off; config/runtime.md states this | Planning Gate ruling |
| S-030 | AC-018 normalises a closed list (fields that already differ between two 0.9.0 dispatches, and the version stamp); the key matches exactly; M12 and M14 pass unmodified; no new content enters the key for pre-change runs | Planning Gate ruling |
| S-031 | This repository's harvested lessons must not ship to installed copies; the exclusion mechanism leaves the payload-sync tests' baseline unchanged | Planning Gate ruling |
| S-032 | The run-level flag must not change the execution-plan contract or its validator; it lives in run state | Planning Gate ruling |
| S-033 | Operator remedy text is rendered as labelled data inside a bounded line budget | Planning Gate ruling |
| S-034 | A harvest failure at aggregation never fails or corrupts aggregation | Planning Gate ruling |
| S-035 | A concrete validation strategy with unit tests in repository-root tests/ is Design Gate input | Planning Gate ruling |
| S-036 | Prefer one new standard-library module with a command line plus minimal hooks; runtime version 0.9.0 to 0.10.0 | operator facts |

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | Every envelope carries `memory_slice` as the literal `{hydrated: false, reason: "memory hydration not requested by this run"}`, and the context slice `excluded` list names `memory/*` | runtime/framework_runtime.py cmd_dispatch and build_context_slice; this invocation envelope |
| F-002 | The payload digest is computed from context digest, input digest, agent version, and canonical artifact path; the idempotency key digests run, state, owner, agent version, and payload digest; `memory_slice`, `built_at`, and `model_tier` are outside both | runtime/framework_runtime.py cmd_dispatch; runtime/state_engine.py idempotency_key and bind_payload |
| F-003 | A dispatch of a completed item is replay-suppressed before any envelope is built; an active item re-dispatched with a different payload digest raises context-integrity-failure | runtime/framework_runtime.py cmd_dispatch |
| F-004 | The context digest digests every slice member's content: the base set (four registries, capability and skill matrices, gate matrix, three context files), the workflow specification, and per-phase members including templates, domain-model/agent-specification.md, memory/architecture.md, dependency-map.md, runtime/README.md | runtime/framework_runtime.py CONTEXT_SLICE_BASE, CONTEXT_SLICE_PHASE, build_context_slice |
| F-005 | execution-request.json is written once, at run creation, carrying runtime_version and no hydration key; an existing run re-enters without rewriting it, and stored_command reads only command_id from it | runtime/framework_runtime.py plan_run and stored_command |
| F-006 | The dispatch prompt carries the line naming the runtime version, and renders a prior rejection rationale as a quoted block that the text labels as data, not instruction | runtime/framework_runtime.py build_dispatch_prompt |
| F-007 | Envelope `built_at` and `context_slice.frozen_at` are set from the clock at each dispatch | runtime/framework_runtime.py cmd_dispatch and build_context_slice |
| F-008 | maybe_aggregate runs from the complete, gate, and aggregate commands, returns early when the status-vector signature is unchanged, and writes completion-package.md, execution metrics, final-report.md, and the run ledger | runtime/framework_runtime.py maybe_aggregate |
| F-009 | M12 re-digests every committed artifact; M14 replays plan, dispatch, and complete against the committed run and compares event count, transitions, statuses, idempotency keys, and artifact digests | runtime/verify_multi_phase.py fingerprint, M12, M14 |
| F-010 | 30 validation_failed events sit in 18 of 25 runs with an event stream; 4 carry an empty failures list; check IDs are dotted (C3.2) or undotted (R7); C3.2 occurs at scope-and-acceptance in run-919c5d5cf156 and run-efe092286625; C7.1 at scope-and-acceptance in run-09099de97613 and at fix-implementation in run-79630cb5274d; events carry state_id, not artifact type | runs/*/events.jsonl, read for this design |
| F-011 | validation-report.json lists every check with id, severity, description, and a per-check detail, and records the artifact as an absolute path | runs/run-919c5d5cf156/states/scope-and-acceptance/validation-report.json |
| F-012 | rollback_scheduled occurs 3 times in run-3e6f6a248b99 and run-4c51600606df, carrying gate, target, and superseded_artifact; gate-rejection failure envelopes occur in recovery-ledger.json of those two runs only, naming gate and closes_state beside a free-text resolution that names the deciding operator; other ledger classes seen are gate-approval-required and output-schema-failure | runs/run-3e6f6a248b99 events.jsonl and recovery-ledger.json; runs/*/recovery-ledger.json |
| F-013 | The memory optimizer discovers only `*.md` files and classifies any other suffix as not a markdown document | runtime/optimize_memory.py discover and classify |
| F-014 | memory is a seed directory; _walk skips names matching EXCLUDE_PATTERNS; the bundle test mirrors managed plus seed directories through the same _walk and _excluded filter and asserts no excluded or stray file in the bundle | omn_agent/source.py; tests/test_bundled_payload.py |
| F-015 | execution_metrics.compute builds per_phase rows from envelopes and invocation_started and validation events, and imports nothing from framework_runtime.py; estimate_dispatch_budget output is written into every envelope as context_budget | runtime/execution_metrics.py; runtime/framework_runtime.py cmd_dispatch |
| F-016 | The model tier precedent ships a managed policy file, adds an additive envelope field outside the payload digest, and adds its value to the invocation_started detail | config/runtime.md, Model Tiers |
| F-017 | config/runtime.md Writeback Policy requires ownership and rationale metadata and fingerprint-keyed upsert; no runtime code produces a memory_slice other than the literal in F-001 | config/runtime.md, Memory Loading; runtime/*.py search |
| F-018 | RUNTIME_VERSION is 0.9.0 | runtime/framework_runtime.py |
| F-019 | StateStore.save writes a temporary file and replaces the target with os.replace | runtime/state_engine.py |
| F-020 | memory/ holds ten Markdown documents and no machine-maintained store | memory/ directory listing |
| F-021 | Seed directories are created from the source only when missing and are never updated or overwritten by the installer | omn_agent/source.py, SEED_DIRS |
| F-022 | runtime/ holds one validator per artifact, including plan_validator.py and design_validator.py; tests/ holds test_model_tier.py, test_bundled_payload.py, test_optimize_memory.py, test_lean_dispatch.py | runtime/ and tests/ directory listings |
| F-023 | Agent module text carries no loading policy, and verify_vertical_slice check C10 keeps it so | architecture context input |
| F-024 | The runtime under change is Python; execution_metrics.py and design_validator.py import yaml, an installed dependency; the .NET stack in context/technical-context.md describes product delivery | runtime/execution_metrics.py; context/technical-context.md |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | Every run whose events record a validation failure also holds a state.json mapping that state_id to its output artifact | Check lessons are keyed by artifact type, which events do not carry (F-010) | Failures in runs without the mapping are skipped and counted unresolved; lesson counts drop | omn-dev-1-implement |
| A-002 | The fields that differ between two dispatches of one invocation under 0.9.0 are `built_at`, `context_slice.frozen_at`, and the task-context digest with its prompt echo | Fixes the closed normalisation list for AC-018 | The list grows only by an omn-tech-lead decision; the baseline comparison changes | omn-qa |
| A-003 | A full harvest over the 25 recorded runs at each knowledge-loop aggregation costs little enough that no incremental harvest is needed | No harvest budget is stated | An incremental cursor is needed and D-006 changes | omn-tech-lead |
| A-004 | No installer path other than _walk copies memory/ files | Payload exclusion relies on the EXCLUDE_PATTERNS filter alone | The store could reach installs another way; D-005 changes | omn-dev-1-implement |
| A-005 | No existing test pins exact execution-metrics keys or exact dispatch bytes for a fixture this change moves off the pre-change path | The metrics change is additive | A pinned test needs a recorded update; delivery effort grows | omn-dev-1-implement |
| A-006 | omn-tech-lead is the default owner of a harvested lesson, following the ownership pattern of memory/architecture.md | A lesson needs an owner at creation | The default owner value in the policy changes | omn-tech-lead |
| A-007 | Acceptance treats the flag-off `memory_slice.reason` required by AC-019 as the one permitted difference from the baseline under AC-018 | AC-018 and AC-019 both name flag-off runs | The flag-off reason reverts to the pre-change text | omn-product-owner |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | functional | One lesson per fingerprint: artifact type plus check ID, or gate plus target phase; approval waits are never lessons | hard | S-001, S-002, S-012, S-023 |
| C-002 | functional | Unchanged evidence yields a byte-identical store | hard | S-003 |
| C-003 | functional | Statuses candidate, active, retired; approve, retire, annotate change only status or remedy and append one history entry; nothing deleted | hard | S-004, S-006 |
| C-004 | functional | Eligible when active, or candidate with distinct runs at or above the threshold (default 2); retired never | hard | S-005, S-018 |
| C-005 | functional | Recall matches phase identifier and output artifact type, caps at five, ranks by distinct runs with deterministic ties, bounds the section at one heading and two lines per lesson | hard | S-007 |
| C-006 | migration | Pre-change and flag-off runs dispatch byte-identically after the closed normalisation list; idempotency key exact; M12 and M14 unmodified | hard | S-011, S-022, S-030 |
| C-007 | migration | No context-slice member file is edited, so no context digest moves (F-004) | hard | S-026, S-030 |
| C-008 | structural | Lesson data and the hydration record never enter context_slice, input_contract, or any payload-digest component, for any run | hard | S-021, S-030 |
| C-009 | structural | Gates, validators, artifact contracts (the execution-plan contract included), Phase Model tables, agent module text unchanged | hard | S-013, S-019, S-032 |
| C-010 | structural | Standard library only; no model call; no network | hard | S-014, S-015, S-020 |
| C-011 | structural | The hydration choice is recorded per run at plan time in run state, never inferred at dispatch; no record means never hydrate; the off flag is honoured | hard | S-029, S-032 |
| C-012 | security | A lesson record holds a closed field list with no free text taken from evidence; operator remedy is bounded and rendered as labelled data | hard | S-021, S-033 |
| C-013 | operability | A harvest failure at aggregation never fails or corrupts aggregation | hard | S-034 |
| C-014 | operability | The store lives under memory/, outside the optimizer scan, and harvest tolerates a repository with no runs/ | hard | S-024, S-025 |
| C-015 | operability | This repository's lessons never ship to installed copies; the payload-sync tests stay unchanged | hard | S-031 |
| C-016 | operability | Loading policy stays in runtime and config/; documentation goes to config/runtime.md and memory/ documents, never agent modules or runtime/README.md | hard | S-026 |
| C-017 | quality-attribute | Harvest cost stays proportional to recorded evidence; no budget is stated | negotiable | S-010 |
| C-018 | operability | Self-hosting delivery: mirror refreshed by its sync procedure only, change proposal, release checklist | hard | S-016, S-017, S-027 |
| C-019 | compliance | Artifacts of this change write framework paths without the dot-directory prefix | hard | S-028 |
| C-020 | functional | A per-lesson report counts dispatches shown the lesson and later recurrences | hard | S-008 |
| C-021 | functional | Execution metrics carry a lessons-hydrated count per invocation | hard | S-009 |
| C-022 | functional | Harvest runs at aggregation with no operator step | hard | S-010 |
| C-023 | operability | RUNTIME_VERSION moves from 0.9.0 to 0.10.0 | negotiable | S-036, S-017 |
| C-024 | quality-attribute | The loop is unit-testable and maintainable apart from the dispatch runtime | negotiable | S-036 |
| C-025 | functional | A validation strategy with unit tests in repository-root tests/ follows the tests/test_model_tier.py precedent | hard | S-035 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | runtime/knowledge.py (new) | extension | F-017, F-010, F-012 | command line: harvest, list, approve, retire, annotate, recall, report; functions called by M-002 | confirmed |
| M-002 | runtime/framework_runtime.py | contract-change | F-001, F-002, F-005, F-006, F-008, F-018 | execution-request.json key; plan flag; memory_slice; prompt section; invocation_started detail; aggregation post-step; runtime version; imports M-001 | confirmed |
| M-003 | runtime/execution_metrics.py | contract-change | F-015 | execution-metrics.json per_phase and top-level counts; estimate_dispatch_budget unchanged | confirmed |
| M-004 | memory/lessons/lessons.store.json (new store) | extension | F-020, F-013 | lesson record schema; lock file beside it | confirmed |
| M-005 | config/knowledge-policy.json (new) | extension | F-016 | policy keys read by M-001 and M-002 | confirmed |
| M-006 | omn_agent/source.py | behavior-change | F-014, F-021, A-004 | EXCLUDE_PATTERNS gains one entry | confirmed |
| M-007 | omn_agent/_bundled_payload/ mirror | operational-impact | F-014 | refreshed by sync; carries M-001, M-005, M-008 to M-011 | confirmed |
| M-008 | config/runtime.md | behavior-change | F-017, F-016 | Memory Loading and Writeback Policy text | confirmed |
| M-009 | memory/README.md | behavior-change | F-020 | lesson category description | confirmed |
| M-010 | memory/memory-governance.md | behavior-change | F-020 | lesson lifecycle and ownership | confirmed |
| M-011 | memory/memory-resolver.md | behavior-change | F-017 | lesson resolution and writeback rule | confirmed |
| M-012 | tests/test_knowledge.py (new) | extension | F-022 | unit tests over temporary framework roots | confirmed |
| M-013 | runtime/state_engine.py | no-change-verified | F-002, F-019 | idempotency_key, bind_payload unchanged | confirmed |
| M-014 | runtime/verify_multi_phase.py | no-change-verified | F-009 | M12, M14 unchanged | confirmed |
| M-015 | runtime/optimize_memory.py | no-change-verified | F-013 | scan rule already excludes the JSON store | confirmed |
| M-016 | runtime/plan_validator.py and the other artifact validators | no-change-verified | F-022 | none | confirmed |
| M-017 | runtime/README.md | no-change-verified | F-004 | slice member; untouched by rule C-007 | confirmed |
| M-018 | registry YAML indexes (agents, workflows, skills, templates) | no-change-verified | F-004 | slice members; untouched by rule C-007 | confirmed |
| M-019 | workflows/implement-feature.md Phase Model | no-change-verified | F-004 | none | confirmed |
| M-020 | agent module sets under agents/ | no-change-verified | F-023 | none | confirmed |
| M-021 | tests/test_bundled_payload.py | no-change-verified | F-014 | baseline unchanged; enforces the new exclusion through _excluded | confirmed |

Boundary crossings: M-002 to M-001 (in-process call at plan, dispatch, aggregation; one-way); M-001 to runs/ evidence files (read-only); M-001 to M-004 and M-005 (store write under lock, policy read); M-003 to invocation_started events (read-only); M-006 to the installer payload boundary (what ships). M-001 never imports M-002, and M-003 never imports M-001 or M-002.

### 5.2 Options Considered

| Option | Structural change | Hard constraints | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|
| O-001 | New module M-001 with JSON store M-004 and policy M-005; hooks in M-002 and M-003; exclusion entry in M-006 | all hard constraints met, C-001 to C-016, C-018 to C-022, C-025 | 2 (M-002, M-003) | 15 of 16 capabilities | meets C-002, C-012; best on C-024 (unit-testable without runtime registries) | 2 additive contract changes | standalone command line in installs; isolated aggregation step | selected: highest score |
| O-002 | Same store, record, and hooks, with all loop logic inside M-002 as new subcommands | all hard constraints met | 2 (M-002, M-003) | 15 of 16 capabilities | meets C-002, C-012; weaker on C-024 (logic inside a 6,000-line module; tests import the whole runtime) | 2 additive contract changes | command line only through M-002 subcommands | viable; second on criterion 4 (C-024) |
| O-003 | Lessons as Markdown entries in memory/known-issues.md | eliminated: violates C-014 (optimizer rewrites Markdown, F-013), C-002, C-015 (seeded document ships) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-014, C-002, C-015 |
| O-004 | Store file joins the context slice or the inputs so agents read lessons there | eliminated: violates C-008 and C-006 (store changes move the payload digest and key, F-002, F-003) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-008, C-006 |
| O-005 | Hydration choice recorded in the execution-plan artifact | eliminated: violates C-009, C-011 (plan contract and validator change) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-009, C-011 |
| O-006 | Hydration inferred at dispatch from the run's runtime_version | eliminated: violates C-011 (never inferred) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-011 |
| O-007 | Committed empty store as a seed instead of an exclusion | eliminated: violates C-015 (this repository's harvest fills the same file and the sync mirrors it, F-014) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-015 |

Recomputed ranking: criterion 1 leaves O-001 and O-002; criterion 2 ties at 2; criterion 3 ties at 15 of 16; criterion 4 favours O-001 on C-024; O-001 ranks first, O-002 second.

### 5.3 Selected Approach

- Selected: O-001.
- Structural change:
  - Module (D-001). runtime/knowledge.py, standard library plus the state_engine digest helper, imports nothing from framework_runtime.py. Command line: harvest, list, approve, retire, annotate, recall (read-only preview of what a dispatch would receive), report.
  - Store (D-002). One file, memory/lessons/lessons.store.json, schema id framework.memory/lessons.v1, top-level keys schema and lessons. Lesson record, closed list: lesson_id (L- plus the first 10 hex of the fingerprint digest), fingerprint, kind (validation-check or gate-rejection), check_id, check_description, check_severity, gate, artifact_type, phases (sorted), occurrences, distinct_runs, first_seen, last_seen, evidence (sorted event and ledger references), evidence_state (current or retained), status, owner, rationale, remedy, history.
  - Fingerprints. check:artifact-type:check-id for validation failures; gate:gate-name:phase-id for gate rejections.
  - Harvest rule (D-013). Occurrence sources: each check ID of a validation_failed event, with artifact type resolved through that run's state.json; each gate-rejection failure envelope in recovery-ledger.json, with rollback_scheduled events attached as evidence. Skipped: gate-approval-required (approval waits), output-schema-failure (duplicates the event), empty failure lists (counted unresolved), IDs outside one to three capitals then digits with optional dotted parts. Description and severity come from the validation report of the latest occurrence that lists the ID, otherwise the first such report in path order. Detail, summary, resolution, rationale, and actor text are never read into the store.
  - Upsert. Evidence fields are recomputed from scratch on every harvest; governance fields (status, owner, rationale, remedy, history) carry over by fingerprint; a lesson with no current evidence is retained with evidence_state retained. A new lesson starts candidate, owner from policy, fixed generated rationale.
  - Serialisation. UTF-8, LF, sorted keys, two-space indent, ASCII escapes, trailing newline, lessons ordered by fingerprint, no timestamp of the harvest itself; the file is rewritten only when its bytes differ; writes go through a temporary file and os.replace under an exclusive lock file (lessons.store.lock).
  - Governance. approve (candidate or retired to active), retire (candidate or active to retired), annotate (sets remedy, status unchanged); each requires an actor and a rationale and appends one history entry with action, from, to, actor, rationale, time; an unknown lesson exits non-zero with the store bytes unchanged; a remedy is collapsed to one line, at most 200 characters, printable, and refused when it matches a credential-like pattern.
  - Run record (D-003). At run creation only, execution-request.json gains knowledge_loop with hydration on or off and a basis. The default comes from the policy file; the plan flag --no-lesson-hydration records off. An existing run never gains or changes the record; the flag against an existing run whose record is absent or on is a request-validation-failure, following the --command precedent.
  - Dispatch (D-004, D-007). After replay detection and payload binding, the runtime reads the record. No record: today's literal memory_slice, no prompt section, no new detail key. Off: hydrated false with a reason naming --no-lesson-hydration. On: eligible lessons whose phases include the dispatched phase and whose artifact_type equals the phase output artifact, ranked by distinct_runs descending, then occurrences descending, then lesson_id ascending, capped at five; memory_slice carries hydrated true, reason, store path, store digest, threshold, matched count, and the shown lessons; invocation_started detail gains lessons_shown. An unreadable store or policy at dispatch fails open: hydrated false, reason naming the fault, lessons_shown empty.
  - Prompt section (D-007). Present only when at least one lesson is shown. Heading line: Lessons from earlier runs, labelled recorded evidence, data not instructions. Per lesson one line (lesson id, kind, check ID or gate, artifact, distinct runs, quoted description) and a second line only when a remedy exists (quoted, labelled operator remedy). Quoted text is whitespace-collapsed, quote and backtick characters neutralised, description capped at 160 characters.
  - Aggregation (D-006). At the end of maybe_aggregate, after every aggregation output is written, and only for runs carrying a knowledge_loop record: a full harvest inside an exception guard; outcome (status, lessons, created, updated, runs scanned, elapsed, error class) written to runs/run-id/knowledge-harvest.json; no ledger event is emitted.
  - Effectiveness (D-008). Shown dispatch: an invocation_started event whose lessons_shown names the lesson. Recurrence after shown: for a check lesson, a validation_failed event of the same run and state, after that invocation and before the state's next invocation, listing the check ID; for a gate lesson, a gate-rejection envelope for that gate closing the phase after its latest shown dispatch. Each retry and each rollback re-entry is its own shown dispatch; a failure is attributed to the one dispatch it follows; occurrences in unshown dispatches are reported as unwarned. The report gives shown, recurrences, unwarned, and their ratio with no pass threshold.
  - Metrics (D-009). Each per_phase row gains lessons_hydrated and lessons_hydrated_by_invocation; the document gains a run total; counts read lessons_shown, and a missing key counts zero.
  - Policy (D-010). config/knowledge-policy.json carries schema, hydration_default (on), auto_eligible_distinct_runs (2), default_owner (omn-tech-lead). The cap of five is fixed, not configurable. Absent file: new runs are recorded off with that basis. Unreadable file: policy-failure at run creation, fail-open at dispatch.
  - Payload exclusion (D-005). EXCLUDE_PATTERNS gains lessons.store.*, covering the store and its lock in the installer, the bundle sync, and the bundle tests at once.
- Rationale: O-001 is the only top-scoring option (5.2); it keeps the one-way dependency M-002 to M-001, lets M-012 test the loop over temporary roots, and confines every pre-change path to an absent-record branch that emits today's literals.
- Highest-scoring rejected alternative and why it lost: O-002 ties O-001 on hard constraints, impact surface, and reuse, but places the loop inside the dispatch runtime, so its tests import the whole runtime and the report cannot be reused from M-003 without importing M-002; it loses on criterion 4 (C-024).
- Tradeoffs accepted:
  - The context slice `excluded` text keeps reading that memory hydration is not requested even on hydrated runs, because changing it would move the context digest (C-008); the prompt section and config/runtime.md state that lessons arrive only through memory_slice (R-014).
  - Full harvest over all runs at each knowledge-loop aggregation, accepting linear cost for simplicity and idempotency (C-017, A-003).
  - Fail-open recall: a corrupt store silently withholds lessons for a dispatch rather than blocking delivery; the reason is recorded in memory_slice.
  - Pre-change runs, this run included, are harvested only by the operator command, never by their own aggregation.
  - One new installer exclusion entry in M-006, outside the surfaces the change request listed, to satisfy C-015.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Dedicated standard-library module M-001 with its own command line; M-002 depends on it one-way (O-001) | yes | architecture-decision-record-D-001.md |
| D-002 | Single JSON lesson store M-004 with closed record, fingerprints, canonical serialisation, rebuild plus governance overlay, lock and atomic replace (O-001) | yes | architecture-decision-record-D-002.md |
| D-003 | Run-level knowledge_loop record in execution-request.json at creation; policy default; --no-lesson-hydration; absent record never hydrates (O-001) | yes | architecture-decision-record-D-003.md |
| D-004 | Lessons travel only in memory_slice, an optional prompt section, and lessons_shown; never in any payload-digest component (O-001) | yes | architecture-decision-record-D-004.md |
| D-005 | lessons.store.* joins EXCLUDE_PATTERNS in M-006 (O-001) | yes | architecture-decision-record-D-005.md |
| D-006 | Isolated full harvest as the last step of maybe_aggregate, for knowledge-loop runs only, outcome in knowledge-harvest.json (O-001) | no | inline, 5.3 Aggregation |
| D-007 | Recall eligibility, matching, ranking, cap, rendering, and fail-open behaviour (O-001) | no | inline, 5.3 Dispatch and Prompt section |
| D-008 | Effectiveness attribution rule over invocation and validation evidence (O-001) | no | inline, 5.3 Effectiveness |
| D-009 | Additive lessons_hydrated fields in execution metrics (O-001) | no | inline, 5.3 Metrics |
| D-010 | Policy file keys, fixed cap, absent and unreadable behaviour (O-001) | no | inline, 5.3 Policy |
| D-011 | AC-018 baseline captured from unmodified 0.9.0, closed list derived by two dispatches of one invocation plus the version stamp (O-001) | no | inline, 9 Test Strategy |
| D-012 | RUNTIME_VERSION 0.10.0, set only after the baseline exists (O-001) | no | inline, P-009 |
| D-013 | Harvest evidence rules: sources, skips, ID pattern, description resolution (O-001) | no | inline, 5.3 Harvest rule |

## API and Data Model Impact

- API changes:
  - M-002 execution-request.json: current shape has no hydration key; target adds knowledge_loop with hydration and basis for runs created at 0.10.0 or later. Compatibility: readers treat an absent key as a pre-change run (C-011). Coexistence: permanent, since pre-change runs are never backfilled. Retirement condition: the absent-key branch may be retired only when no pre-change run remains under runs/. Rollback position: a reverted runtime ignores the key, because stored_command reads only command_id (F-005).
  - M-002 plan flag: --no-lesson-hydration on every subcommand that can create a run; against an existing run it is refused when it disagrees with the record. Rollback position: removing the flag leaves recorded runs readable.
  - M-002 memory_slice: current literal unchanged for pre-change runs; for knowledge-loop runs the off shape keeps the two keys with a different reason, and the on shape adds store, store_digest, threshold, matched, lessons. Compatibility: additive and outside the payload digest (F-002, C-008). Rollback position: a reverted runtime emits the literal again.
  - M-002 prompt: one optional section, present only when lessons are shown; absent for pre-change and flag-off runs.
  - M-002 invocation_started detail: lessons_shown, emitted only for knowledge-loop runs, so pre-change event streams are unchanged (F-009).
  - M-002 runtime version 0.10.0; the stamp is in the closed normalisation list.
  - M-003 execution-metrics.json: schema id stays v1; per_phase rows gain lessons_hydrated and lessons_hydrated_by_invocation, and the document gains a run total. Compatibility: additive; consumers that ignore unknown keys are unaffected; estimate_dispatch_budget is untouched, so context_budget inside envelopes is unchanged. Rollback position: the next metrics recompute under a reverted runtime drops the keys.
- Contract compatibility notes: no change reaches context_slice, input_contract, the payload digest, or the idempotency key of any run (C-008), and no context-slice member file is edited (C-007), so the key of every pre-change work item is reproduced exactly.
- Schema or migration changes:
  - New store M-004 and policy M-005; direction is forward creation only, with no existing data migrated; reversible by reverting the change set, while the store file is kept so that governance history survives a re-introduction; during transition the dispatch reader treats a missing store as zero lessons and every writer holds the lock.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Read run event streams | RunLedger.events() in runtime/framework_runtime.py | rejected | Importing it from M-001 would invert the one-way dependency M-002 to M-001 (D-001) and load the whole runtime |
| Read run event streams | standard library json over JSON lines | reuse-as-is | Same direct read execution_metrics.py already performs (F-015) |
| Parse evidence, state, reports, policy | standard library json | reuse-as-is | Every source is JSON (F-010, F-011, F-012) |
| Lesson identifiers and store digest | runtime/state_engine.py digest helper | reuse-as-is | Standard-library leaf module; same digest form as other run evidence (F-002) |
| Atomic store write | StateStore.save temporary-file and replace pattern (F-019) | reuse-extended | Pattern reused in M-001 with an exclusive lock file from the standard library |
| Governed memory category and lifecycle vocabulary | memory/ documents and memory/memory-governance.md | reuse-extended | Documents describe the lesson category; Markdown storage itself fails C-014 (O-003) |
| Fingerprint-keyed upsert rule | config/runtime.md Writeback Policy and memory/memory-resolver.md (F-017) | reuse-extended | Specified rule implemented for one category |
| Envelope carrier for memory | memory_slice field (F-001) | reuse-extended | Reserved slot gains the hydrated shape |
| Rendering text as labelled data | prior_rejection rendering in build_dispatch_prompt (F-006) | reuse-extended | Same quote-and-label convention, bounded to one line per item |
| Policy carrier | config/model-tier-policy.json pattern (F-016) | reuse-extended | New managed config file in the same form |
| Aggregation trigger | maybe_aggregate (F-008) | reuse-extended | Post-step appended after all outputs |
| Per-invocation metrics | execution_metrics.compute per_phase rows (F-015) | reuse-extended | Additive fields from the invocation_started detail |
| Payload exclusion | omn_agent/source.py EXCLUDE_PATTERNS (F-014) | reuse-extended | One pattern; installer, sync, and bundle tests share the filter |
| Run-level record | execution-request.json (F-005) | reuse-extended | Written once at creation, so absence identifies pre-change runs |
| Command-line parsing | standard library argparse | reuse-as-is | Same as every runtime script |
| Check descriptions | validation-report.json (F-011) | reuse-as-is | Validator-authored description and severity per check |
| Harvest, eligibility, recall selection, attribution | none-found | none-found | Searched existing components (runtime/*.py has no harvest or recall; F-017), the standard library (no domain logic), the Python platform (none), installed dependencies (PyYAML parses only) |

## Operational Considerations

- Logging and observability updates: runs/run-id/knowledge-harvest.json per knowledge-loop aggregation (M-002, C-013); lessons_shown in invocation_started (M-002); lessons_hydrated in metrics (M-003, C-021); the report and list subcommands (M-001, C-020); the dispatch console prints a lessons line only for knowledge-loop runs (M-002, C-006).
- Error handling strategy: harvest skips an unreadable evidence file and counts it, never aborting the scan (M-001, C-002); the aggregation step catches every exception after all aggregation outputs exist and records the class (M-002, C-013); the store is replaced atomically, so a failure leaves the prior file intact (M-004); governance commands fail with non-zero exit and an unchanged store (M-001, C-003); dispatch fails open on an unreadable store or policy (M-002, D-007); an unreadable policy at run creation is a policy-failure (M-005, D-010).
- Security considerations: closed record fields and an ID pattern keep evidence free text, actor names, and validator detail out of the store (M-001, M-004, C-012); remedy is screened, length-capped, collapsed to one line, and rendered quoted and labelled as data (M-002, C-012); the store and lock never ship (M-006, C-015); no secret, credential, network, or model path is introduced (C-010).
- Performance considerations: dispatch adds one policy read and one store read, and the prompt grows by at most eleven lines (M-002, C-005); harvest reads every run's events, ledger, and failing reports once per new aggregation signature of a knowledge-loop run, linear in recorded evidence with no stated budget (M-001, C-017, A-003); elapsed time and runs scanned are recorded so a regression is visible.
- Deployment and operability impact: installs receive M-001 and M-005 through the managed payload and create their own store on first harvest; the bundle is refreshed by the sync procedure after the last edit (M-007, C-018); documentation lands in M-008 to M-011 only (C-016).

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | Store, recall, attribution, aggregation, run-record, and validation contracts in this package and its records are accepted at the Design Gate | M-001, M-002, M-004, M-005 | none | Contract definition precedes every producer and consumer | T-001, T-002, T-006, T-008, T-011, T-013, T-025 |
| P-002 | A dispatch baseline (envelope, prompt, key) of a pre-change fixture run is captured from the unmodified 0.9.0 runtime, with the closed list derived from two dispatches of one invocation | M-002, M-003, M-013 | P-001 | The reference must exist before the code it judges changes | T-014 |
| P-003 | The exclusion entry exists in M-006 before any store file appears in the authoritative tree | M-006, M-004 | P-001 | A sync after a store exists would mirror it into the committed bundle | T-003 |
| P-004 | Store, harvest, governance, and eligibility exist in M-001 against the contract | M-001, M-004, M-005 | P-001, P-003 | Producer of the store precedes its readers | T-003, T-004, T-005 |
| P-005 | The run record and plan flag exist in M-002 | M-002, M-005 | P-001, P-002 | The record producer precedes the dispatch reader, and the baseline precedes any M-002 edit | T-017 |
| P-006 | Dispatch hydration, the prompt section, and lessons_shown exist in M-002 | M-002, M-001 | P-002, P-004, P-005 | Recall consumes the store, the record, and the baseline comparison | T-007 |
| P-007 | Metrics count in M-003 and the report in M-001 read lessons_shown | M-003, M-001 | P-006 | Both consume the detail key the dispatch emits | T-009, T-010 |
| P-008 | The isolated harvest step exists at the end of maybe_aggregate | M-002, M-001 | P-004, P-005 | It calls the delivered harvest and reads the run record | T-012 |
| P-009 | RUNTIME_VERSION reads 0.10.0 | M-002 | P-002 | The baseline must carry the pre-increment stamp | T-021 |
| P-010 | Documents describe the delivered behaviour, including the default, the off flag, and fail-open recall | M-008, M-009, M-010, M-011 | P-004, P-006, P-008 | Documentation describes delivered contracts | T-020, T-018 |
| P-011 | The mirror is refreshed by its sync procedure after the last framework edit | M-007 | P-006, P-007, P-008, P-009, P-010 | The bundle must match the final tree | T-022 |
| P-012 | Unit tests in M-012, the full suite, and the verifiers pass on the final tree, including M12 and M14 unmodified | M-012, M-014, M-021 | P-011 | Verification of a boundary precedes reliance on it | T-026, T-015, T-016, T-019, T-027 |
| P-013 | The change proposal and release checklist cite the verification evidence | M-002, M-007 | P-012 | They record evidence that only P-012 produces | T-023, T-024 |

### Test Strategy Focus Areas

- Carrier: tests/test_knowledge.py (M-012), following tests/test_model_tier.py; every test builds a temporary framework root and copies any recorded evidence it needs, never reading or writing the live runs/ directory.
- AC-001: harvest over a copy of runs/; pass when lessons exist for check C3.2 on scope-definition.md (2 distinct runs) and for C7.1 on scope-definition.md and on implementation-report.md (1 run each, F-010), each listed with all six fields.
- AC-002: two-run fixture, one gate-rejection for gate G closing phase P in each; pass when exactly one gate lesson with distinct runs 2.
- AC-003: root without runs/; pass when exit 0, zero lessons reported, no store written.
- AC-004: a credential-like marker planted in event summaries, report details, and ledger resolutions; pass when no store file contains it.
- AC-005: two harvests; pass when every store file digest is equal.
- AC-006: append one validation_failed for an existing fingerprint; pass when occurrences rise by one and last_seen moves.
- AC-007 and AC-008: approve, retire, annotate, then harvest; pass when lesson count is constant, one history entry is added per command, and status, owner, rationale, remedy survive the harvest; an unknown lesson leaves store bytes unchanged.
- AC-009: run the optimizer's discovery and classification over a fixture memory directory holding the store; pass when the store is classified non-Markdown and its bytes are unchanged.
- AC-010 and AC-017: render with and without remedy, and with five lessons; pass when the remedy line appears only with a remedy and the section is at most eleven lines.
- AC-011 to AC-013: eligibility over candidate counts 1 and 2, active at 1, retired at any count, and threshold 3 set through a fixture policy file.
- AC-014 to AC-016: dispatch a knowledge-loop fixture run; pass when a matching eligible lesson is in memory_slice and the prompt, a non-matching phase or artifact lesson is absent, and seven eligible lessons yield the five with the highest distinct runs in tie order.
- AC-018: dispatch the pre-change fixture under 0.10.0 and compare with the P-002 baseline after normalising the closed list (A-002); pass when envelope and prompt bytes match and the key is identical; verify_multi_phase M12 and M14 pass unmodified; the same comparison for a flag-off fixture differs only in memory_slice.reason (A-007, Q-001).
- AC-019: plan a new run with and without the flag; pass when the record reads on and off and the off dispatch names the flag in its reason; the flag against a pre-change run is refused.
- AC-020: fixture with three shown dispatches (run X attempts 1 and 2, run Y attempt 1) and one validation_failed after run X attempt 1; pass when the report gives 3 shown and 1 recurrence.
- AC-021: aggregate a knowledge-loop fixture run, then dispatch the next phase with no harvest command; pass when the recurring lesson is hydrated.
- AC-022: pass when lessons_hydrated equals the shown count per invocation, and is zero for a pre-change fixture.
- AC-023: pass when the four documents of M-008 to M-011 name the category, lifecycle, eligibility rule, default, and off flag.
- Beyond the criteria: a forced harvest exception leaves aggregation outputs equal to a run without the step and records status failed; a store file placed in a temporary tree is absent from the payload map; a held lock makes a second writer wait or fail without writing; the slice member digests of M-017 and M-018 equal the baseline.

### Rollout and Rollback

- Rollout: runs created at 0.10.0 or later are recorded on by default and hydrate once eligible lessons exist; every pre-change run, this one included, stays on the absent-record branch; operators may run harvest once over existing evidence to seed this repository's store.
- Rollback: set hydration_default to off in M-005 so new runs record off; or revert the change set, after which recorded keys are ignored and the store file is kept unread; bundle and installs never held the store (D-005).

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | contract | A knowledge-loop branch leaks into the absent-record path (a key, a prompt line, a console line, a detail key) | Pre-change dispatch differs from the baseline; AC-018 fails | medium | M-002, D-004, P-006 | Baseline comparison test in P-012 against P-002 | omn-dev-1-implement |
| R-002 | contract | An edit touches a context-slice member such as runtime/README.md or a registry | Context digest and the key of every pre-change item move | medium | M-017, M-018, P-010 | Slice member digests compared with the baseline in P-012; review against C-007 | omn-dev-2-reviewer |
| R-003 | migration | Baseline capture finds a differing field outside A-002 | The closed list needs an owner decision before AC-018 can pass | low | P-002, D-011 | Record the field and its cause in the baseline; escalate to the ruling owner | omn-tech-lead |
| R-004 | contract | Acceptance reads AC-018 as strict identity for flag-off runs (A-007 false) | AC-019 and AC-018 cannot both pass as worded | medium | D-003, P-005 | Q-001 settles it; either answer is a one-string change | omn-product-owner |
| R-005 | structural | Older runs lack the state.json mapping or carry other evidence shapes (A-001 false) | Lessons are missed or miscounted | low | M-001, P-004 | Unresolved occurrences counted and printed by harvest; a legacy-shape fixture in P-012 | omn-dev-1-implement |
| R-006 | security | Evidence free text or a credential-like string reaches the store or a prompt | Sensitive content persists and is shown to later agents | medium | M-001, M-004, D-002 | Closed record, ID pattern, no detail or summary reads; AC-004 test in P-012 | omn-dev-2-reviewer |
| R-007 | security | Remedy or description text is read as an instruction or breaks the line budget | Later agents act on injected text, or the section exceeds its bound | low | M-002, D-004, P-006 | One-line collapse, length caps, neutralised quotes, labelled quoting, remedy screening | omn-dev-2-reviewer |
| R-008 | operability | Concurrent harvest and governance writes in a shared tree | An operator action is lost or the store is corrupted | low | M-004, D-002 | Exclusive lock, re-read under lock, atomic replace | omn-dev-1-implement |
| R-009 | operability | The harvest step raises or half-writes at aggregation | Aggregation fails or its outputs differ | low | M-002, D-006, P-008 | Step runs last inside a guard; atomic store write; forced-failure test | omn-dev-1-implement |
| R-010 | performance | Harvest cost grows with recorded runs (A-003 false) | Every knowledge-loop aggregation slows | low | M-001, D-006, P-008 | Elapsed and runs scanned recorded per harvest; incremental harvest by a later change request | omn-tech-lead |
| R-011 | operability | The exclusion entry is missing when a store exists, or another installer path copies memory/ (A-004 false) | This repository's lessons ship in the bundle or installs | low | M-006, M-007, D-005, P-003 | P-003 ordering; bundle tests already reject excluded files; reviewer checks installer copy paths | omn-dev-2-reviewer |
| R-012 | delivery | A test pins exact metrics keys or dispatch bytes (A-005 false) | The suite fails and is rerun | low | M-003, P-007 | Run the metrics and dispatch tests before the full suite | omn-dev-1-implement |
| R-013 | delivery | A check expects the C7.1 lessons to hydrate automatically | They split by artifact type into two one-run lessons below the threshold (F-010), so the check fails | medium | M-001, P-012 | Recall fixtures use an eligible lesson; AC-001 asserts existence, not eligibility | omn-qa |
| R-014 | structural | An agent reads the unchanged context-slice exclusion text beside a hydrated memory_slice | The agent ignores or doubts the shown lessons | low | M-002, D-004 | Prompt heading and config/runtime.md state that lessons arrive only through memory_slice | omn-documentation |
| R-015 | operability | The policy file is unreadable when a run is created | Run creation fails as a policy-failure | low | M-005, D-010 | Failure names the file; a shipped valid file in M-005; absent file degrades to off | omn-dev-1-implement |

## Estimate and Confidence

- Overall: L (confidence: low) -- cross-boundary change over the runtime, the installer package, documents, and tests, with two additive contract changes; low because P-002 rests on A-002 and P-004 on A-001.
- Breakdown: P-001 S (high, delivered by this package); P-002 S (low, A-002); P-003 XS (high); P-004 M (low, A-001); P-005 S (medium); P-006 M (medium); P-007 S (medium); P-008 S (medium); P-009 XS (high); P-010 S (medium); P-011 XS (high); P-012 M (medium); P-013 S (medium).
- Scope assumptions:
  - The rulings in S-029 to S-034 stand as relayed.
  - Q-001 to Q-004 are answered as their default consequence states.
  - A-001 to A-005 hold; no incremental harvest is required.
- Uncertainty drivers: the evidence shape of older runs (A-001), the exact closed list (A-002), tests that pin exact output (A-005), and the length of the full unit suite when a rerun is needed.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | For flag-off runs, is the AC-019 reason text the one permitted difference from the AC-018 baseline? | no | omn-product-owner | D-003, P-005 | Yes: design as stated. No: the flag-off reason reuses the pre-change text and AC-019's flag naming moves to the record and plan output |
| Q-002 | Should a pre-change run's own aggregation also harvest? | no | omn-tech-lead | D-006, P-008 | No (design): pre-change aggregation keeps today's side effects. Yes: aggregations of old runs write the store, with no dispatch effect |
| Q-003 | What recurrence reduction, if any, must the report show before the loop counts as effective? | no | omn-business-analyst | D-008, P-007 | No target: the report records without a threshold. A target: a pass line is added to the report |
| Q-004 | Is omn-tech-lead the default owner of harvested lessons (A-006)? | no | omn-tech-lead | D-002, D-010 | Yes: as designed. Another role: one value in the policy file changes |
| Q-005 | Accept the records for D-001 to D-005, emitted at Proposed; implementation waits on them | no | omn-tech-lead | D-001, D-002, D-003, D-004, D-005 | Accepted: P-002 onward may start. Rejected: the affected plan steps are redesigned before implementation |

## Sign-off

- Architect: unsigned; producer of this package, excluded from deciding the Design Gate
- Tech Lead (accepting owner of the Design Gate under the Producer Exclusion Rule; co-owner omn-architect): unsigned
- QA (test strategy focus areas, input to T-025): unsigned
- Product Owner (Q-001 only): unsigned
