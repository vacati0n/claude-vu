```yaml
design:
  designId: SCOPE-2026-0007-technical-design
  changeReference: SCOPE-2026-0007
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/mnc-feature-request.md
    - type: change-request
      reference: runs/inputs/mnc-change-request.md
    - type: business-intent
      reference: runs/inputs/mnc-business-intent.md
    - type: architecture-context
      reference: runs/inputs/mnc-architecture-context.md
    - type: execution-plan
      reference: runs/run-ae91e085f481/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001]
  consumesPlan: runs/run-ae91e085f481/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:25a02ca166aa92074ee2fbe8142b210d
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: SCOPE-2026-0007
- Author: architect
- Reviewers: omn-tech-lead, omn-qa
- Last Updated: 2026-09-17

## Objective

- Desired outcome: The necessity-and-reuse standard (the ladder, the minimum-necessary-change
  definition, the safety floor, and the seven review questions) is carried by one existing
  knowledge artifact that already reaches, through bindings that exist today, every one of
  the seven phases the feature request names, with zero new files and zero runtime change.
  The architect's own reuse-survey and significance procedures are the first consumers to
  apply the standard to themselves.
- Architectural objectives:
  - The standard is delivered as additive content on an existing skill file, reachable by
    `solution-design-and-risk-assessment`, `implementation`, `refactor-implementation`,
    `quality-review`, `code-quality-review`, `structural-compliance`, and
    `repository-quality-scan` without any change to `runtime/framework_runtime.py`. Traces
    to `S-001`, `S-006`, `S-009`, `S-010`.
  - The architect's own reuse-survey rule (`A6`) and significance rule (`A9`) name the full
    candidate set — existing components, the standard library, native platform or framework
    capability, and already-installed dependencies — and a new-dependency significance
    trigger, so the procedure that helps carry the standard also follows it. Traces to
    `S-011`, and the change request's architect-behaviour proposal.
  - The architect's self-check (`A7.3`) states the same candidate-kind rule its procedure
    states, so the two cannot drift apart. Traces to `S-013` and the change request's
    architect self-check proposal.
  - Not an objective of this design phase, but a structural consequence it hands forward:
    the implementer's route-selection and safety-floor self-check, and the reviewer's
    seven-question procedure, apply the same standard in their own later phases. Traces to
    `S-012`, `S-013`.
- In scope: this phase's own tasks (`T-001`, `T-002`, `T-003`, `T-013`, `T-014`) — selecting
  and extending the standard's carrier; authoring the carrier's new content; extending the
  architect's own reuse-survey, significance, and self-check wording; deciding the
  dependency-significance and skill-version questions those two tasks raise.
- Out of scope:
  - Any change to `runtime/framework_runtime.py` or its version constant, to any template,
    validator, workflow specification, manifest, host registration, or registry record other
    than the carrier skill's own version identity (`S-006`, `S-008`, `S-009`, `S-027`).
  - A new agent, skill file, workflow phase, gate, command, template section, validator
    vocabulary, configuration surface, prompt layer, or hook (`S-006`).
  - Authoring the literal wording for the implementer's (`omn-dev-1-implement`) or the
    reviewer's (`omn-dev-2-reviewer`) own module edits (`S-012`, `S-013`, `S-022`–`S-025`):
    this design states the structural requirement those edits must satisfy and binds them
    as sequencing constraints, but the wording itself is authored by the owning agent in its
    own phase, consistent with this agent never becoming the implementer.
  - Modification of the planner or product-owner contracts (`S-016`).
  - A line-count threshold or any finding whose substance is "the change could be shorter"
    (`S-005`, and scope-definition `X-007`).

## Requirements Summary

- Functional requirements:
  - One written standard states, in one place: understanding the problem precedes the
    ladder; the seven rungs in order with the stop-at-first-rung rule; the
    minimum-necessary-change definition; the safety floor with line count stated as not a
    criterion; and the seven review questions with the finding category each yields
    (`S-010`).
  - The architect's reuse survey names four candidate kinds for every required capability
    and records an unrequired capability as out of scope rather than surveying or designing
    it (`S-011`).
  - The architect's significance rule additionally names a new external dependency as
    architecture-significant (`S-011`; change request, architect-behaviour proposal;
    consumed by a future design's own `A9` application, not by this one, since `D-004`
    finds no new dependency here).
- Non-functional requirements:
  - Zero runtime change, zero new repository files, and unchanged agent contract versions
    (`1.0.0`) for `architect`, `omn-dev-1-implement`, and `omn-dev-2-reviewer` (`S-006`,
    `S-008`, `S-009`).
  - Every framework verifier, the `omn_agent` unit test suite, and the five component counts
    remain at their recorded baseline after the whole change is delivered (`S-014`,
    `S-015`); this design phase's own contribution to that baseline is verified by
    inspection, not by execution, per the Estimate section below.
- Acceptance criteria: this design targets the scope definition's own acceptance criteria
  for phase reachability without a runtime change, for the reuse-survey rule and
  out-of-scope recording, and for skill version identity (`S-012`, `S-013`); those criteria
  are cited by subject here, not by the scope definition's own identifiers, because that
  register uses the same letter-prefixed numbering as this design's own Assumptions
  register.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | S01 (`skills/architecture/clean-architecture-checklist.md`) is declared by ten agent manifests, including `architect`, `omn-dev-1-implement`, and `omn-dev-2-reviewer` | Architecture context |
| F-002 | S01 is a context-slice member of `implementation`, `refactor-implementation`, `quality-review`, `code-quality-review`, `repository-quality-scan`, `structural-compliance`, `technical-discovery`, `technical-validation`, `option-analysis`, and `option-synthesis` | Architecture context; confirmed by inspection of `runtime/framework_runtime.py` `CONTEXT_SLICE_PHASE` |
| F-003 | S01 is not a context-slice member of `solution-design-and-risk-assessment`; the architect receives it through the agent's own manifest skill binding (S01, Primary) and the phase's mandatory-skill list (S01, S03, S06, S09), not through a slice entry | Inspection of `runtime/framework_runtime.py` `CONTEXT_SLICE_PHASE` and `skills/agent-skill-matrix.md` |
| F-004 | S01 carries, before this change, three rules: the decision rule "Introduce a new layer only when it reduces coupling or clarifies ownership," the common mistake "Creating abstractions without real variation points," and the anti-pattern "Sharing utility modules that hide cross-layer dependencies" | Architecture context; confirmed by direct inspection of `skills/architecture/clean-architecture-checklist.md` |
| F-005 | Skill identity metadata (code, category, version, status) lives in `registry/skills.yaml` and the Skill Catalog of `skills/agent-skill-matrix.md`; S01's currently recorded version is `1.0.0` in both | Direct inspection of `registry/skills.yaml` and `skills/agent-skill-matrix.md` |
| F-006 | `domain-model/skill-specification.md` records semantic versioning for skills: MAJOR for a breaking rule or structure change, MINOR for additive guidance and examples, PATCH for wording fixes and metadata corrections | Direct inspection of `domain-model/skill-specification.md` |
| F-007 | The dispatch prompt the runtime builds carries routing and addressing only; every instruction about how to do the work lives in the module set; there are no host hooks or settings files in this repository; the dispatch envelope is the only injection mechanism | Architecture context |
| F-008 | Agent host registrations pin `metadata.version is 1.0.0` and abort on a mismatch; module digests are frozen into each run's invocation envelope | Architecture context |
| F-009 | The architect's `reasoning.md` A6 today records candidates only as "existing components," with outcomes `reuse-as-is`, `reuse-extended`, `rejected`, `none-found`; new structure is permitted only where the outcome is `rejected` or `none-found`; a `none-found` outcome requires a recorded search basis | Direct inspection of this run's own loaded module, `agents/architect/reasoning.md` A6 |
| F-010 | The architect's `quality.md` A7.3 requires every `none-found` outcome to state where the search looked, but does not name which candidate kinds that basis must cover | Direct inspection of this run's own loaded module, `agents/architect/quality.md` A7.3 |
| F-011 | The architect's `reasoning.md` A9 names five conditions that make a decision architecture-significant; introducing a new external dependency is not among them today | Direct inspection of this run's own loaded module, `agents/architect/reasoning.md` A9 |
| F-012 | The implementer's `reasoning.md` Stage 3 states no rule for choosing between reuse, standard library, direct code, and new abstraction; Stage 5 states "write the code the entry describes, and nothing the entry does not describe" and "touch no file outside the change set," but does not name a stop-at-first-rung route rule or forbid speculative abstraction, refactor of untouched code, or safety-floor weakening as its own named rule | Architecture context; confirmed by direct inspection of `agents/omn-dev-1-implement/reasoning.md` Stage 3, Stage 5 |
| F-013 | The implementer's `output.md` defines `Approach taken` as one of four Implementation Summary bullets, stating "the route actually used, not the route considered" | Direct inspection of `agents/omn-dev-1-implement/output.md` section 2 |
| F-014 | The implementer's `quality.md` Boundary checks (`B1`–`B6`) name authorization, validation, audit paths, and weakened tests (`B4`); they do not separately name error handling, accessibility, observability, or data integrity; its Not-machine-checkable obligations (`N1`–`N3`) do not include a justification obligation for new abstractions, files, or dependencies | Direct inspection of `agents/omn-dev-1-implement/quality.md` |
| F-015 | The reviewer's `reasoning.md` Stage 4 applies seven lenses to a change review — correctness, architecture, standards, security, maintainability, test-adequacy, packaging — and a separate junk-detection lens set for `repository-quality-scan` only; Stage 6 assigns severity from a four-row table keyed to consequence, not to lens identity | Architecture context; confirmed by direct inspection of `agents/omn-dev-2-reviewer/reasoning.md` Stage 4, Stage 6 |
| F-016 | `runtime/review_package_validator.py`'s `CATEGORIES` already accept all thirteen categories for every review phase; only the reviewer's `output.md` prose restricts the junk lenses to the scan phase | Architecture context |
| F-017 | `runtime/implementation_report_validator.py` checks declared field bullets by label and non-emptiness, and table columns by declared header; adding a column or a bullet changes the contract, changing a field's description does not | Architecture context |
| F-018 | `runtime/design_validator.py` D7.3 checks that a `none-found` row states a basis; it does not check which candidate kinds the basis names | Architecture context |
| F-019 | Every artifact validator rejects the vendor substring, and the dot-directory path prefix is stripped before that scan | Architecture context |
| F-020 | `tests/test_bundled_payload.py` fails on any drift between the framework tree and the mirror under `omn_agent/_bundled_payload/`; `--sync` regenerates the mirror | Architecture context |
| F-021 | Recorded framework baselines as of 2026-09-15: `verify_registry_coverage.py` 6/6 with 37 of 37 phases dispatchable; `verify_validators.py` 6/6; `verify_manifests.py` 2/2; `verify_recovery.py` 41/41; `verify_vertical_slice.py` 10/10; `verify_multi_phase.py` 15/15; `verify_self_hosting.py` 7/8 (S8 failing on four pre-existing, unrelated runs); the `omn_agent` unit test suite: 329 tests, OK | Architecture context |
| F-022 | Recorded module-set byte sizes as of 2026-09-15: `planner` 91,711; `architect` 119,162; `omn-dev-1-implement` 76,418; `omn-dev-2-reviewer` 85,093; `omn-product-owner` 73,869; `omn-qa` 93,035; active agents 12, skills 12, workflows 8, phases 37, commands 11 | Architecture context |
| F-023 | The repository's primary checkout carries roughly 194 uncommitted changes at a newer runtime version; of the files this change touches, only `agents/omn-dev-1-implement/identity.md` (one line) and `templates/implementation-report.md` have uncommitted edits there, and `runtime/framework_runtime.py` differs by about 1,700 lines | Architecture context |
| F-024 | The planner's contract already treats an untraced task as invented scope; the product owner's contract already requires explicit exclusions | Architecture context |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The framework documents this design cites by direct inspection (`domain-model/skill-specification.md` and the `architect`, `omn-dev-1-implement`, `omn-dev-2-reviewer` modules) read the same at implementation time as they do now | The transition strategy and the target content below are stated against today's text | The implementer's own baseline read supersedes this design's "current shape" statements, and the deviation is recorded there, not here | omn-tech-lead |
| A-002 | The `F-021`/`F-022` baseline is still valid immediately before this change's edits land | The post-change verification (`T-009`) must attribute any mismatch to this change alone | A fresh pre-change snapshot (`T-007`) is the baseline actually used, not `F-021`/`F-022` | omn-tech-lead |
| A-003 | Extending S01's prose with the new sections and one new anti-pattern/common-mistake entry is "additive guidance" (MINOR) under `F-006`, not a "breaking rule or structure change" (MAJOR) | `T-014`'s version-increment decision rests on this classification | The version target for `T-014` is wrong and must be revised by `omn-tech-lead` before the registry and catalog are edited | omn-tech-lead |
| A-004 | Applying the ladder inside the existing `architect` A6, implementer Stage 3/5, and reviewer Stage 4 stages is not itself "an added reasoning loop" under the business intent's execution-cost constraint (`S-030`), because it is additional guidance content evaluated within stages these agents already execute, not an additional stage, gate, or invocation | No other measurable proxy for "reasoning loop" is supplied | The whole approach registers as violating the non-goals list (`S-006`) and must be re-evaluated at the Design Gate | omn-tech-lead |
| A-005 | The target content this design specifies for `skills/architecture/clean-architecture-checklist.md`, `agents/architect/reasoning.md`, and `agents/architect/quality.md` is applied to the repository by the implementation-phase owner (`omn-dev-1-implement`), because this agent's own permitted writes for this run do not include those paths, even though the supplied execution plan attributes `T-002` and `T-003` to the `architect` role | `T-002` and `T-003` are attributed to `architect` in the supplied execution plan, and this design's own write boundary would otherwise make those tasks impossible to close from inside this phase | Closure of `T-002`/`T-003` stalls on a permitted-writes mismatch that only `omn-orchestrator` can resolve; no content in this design changes either way | omn-orchestrator |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | Structural | No new agent, skill file, workflow phase, gate, command, template section, validator vocabulary, configuration surface, prompt layer, or hook | Hard | `S-006` |
| C-002 | Structural | No change to `runtime/framework_runtime.py`; `RUNTIME_VERSION` stays `0.5.0` | Hard | `S-009` |
| C-003 | Structural | No change to any template, validator, workflow specification, manifest, host registration, gate-matrix row, or registry record, other than the carrier skill's own version identity | Hard | `S-027` |
| C-004 | Structural | Agent contract versions for `architect`, `omn-dev-1-implement`, and `omn-dev-2-reviewer` stay at `1.0.0` | Hard | `F-008`; scope-definition `X-006` |
| C-005 | Security | No simplification may remove or weaken a safety-floor item: input validation at a trust boundary, error handling that prevents data loss, authorization or audit paths, accessibility, required observability, data integrity, or the tests that prove the change | Hard | `S-004` |
| C-006 | Functional | The delivered standard must already be reachable, without a runtime change, by all seven named phases: `solution-design-and-risk-assessment`, `implementation`, `refactor-implementation`, `quality-review`, `code-quality-review`, `structural-compliance`, `repository-quality-scan` | Hard | `S-010` |
| C-007 | Quality-attribute | Line count is not a review criterion; no finding may be "the change could be shorter" | Hard | `S-005`; scope-definition `X-007` |
| C-008 | Operability | Added instruction volume is measured and reported in bytes per module set; no numeric ceiling is supplied | Negotiable | `S-015` |
| C-009 | Structural | The heading `Skill: Architecture Foundations` must remain unchanged, because the registry indexes S01 by that display name | Hard | `F-005` |
| C-010 | Structural | No new file is added to the repository tree; the packaging mirror is refreshed mechanically | Hard | `S-006`, `S-026` |
| C-011 | Structural | The planner and product-owner contracts are not modified | Hard | `S-016` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `skills/architecture/clean-architecture-checklist.md` (S01) | extension | F-001, F-004, F-005 | none (knowledge document, consumed via agent skill bindings and phase context-slice membership) | confirmed |
| M-002 | `registry/skills.yaml` (S01 record) | behavior-change | F-005 | skill registry lookup by identifier and version | confirmed |
| M-003 | `skills/agent-skill-matrix.md` (S01 Skill Catalog row) | behavior-change | F-005 | none | confirmed |
| M-004 | `agents/architect/reasoning.md` (A6, A9) | behavior-change | F-009, F-011 | none | confirmed |
| M-005 | `agents/architect/quality.md` (A7.3) | behavior-change | F-010 | none | confirmed |
| M-006 | `agents/omn-dev-1-implement/reasoning.md` (Stage 3, Stage 5) | behavior-change | F-012 | none | confirmed |
| M-007 | `agents/omn-dev-1-implement/output.md` (`Approach taken` field) | behavior-change | F-013 | none | confirmed |
| M-008 | `agents/omn-dev-1-implement/quality.md` (Boundary checks, Not-machine-checkable obligations) | behavior-change | F-014 | none | confirmed |
| M-009 | `agents/omn-dev-2-reviewer/reasoning.md` (Stage 4 maintainability lens) | behavior-change | F-015 | none | confirmed |
| M-010 | `omn_agent/_bundled_payload/**` (packaging mirror) | operational-impact | F-020 | `tests/test_bundled_payload.py` drift check | confirmed |
| M-011 | `runtime/framework_runtime.py` | no-change-verified | F-007, F-008 | none | confirmed |
| M-012 | `agents/planner/**`, `agents/omn-product-owner/**` | no-change-verified | F-024 | none | confirmed |
| M-013 | `templates/implementation-report.md` | no-change-verified | F-013, F-017, F-023 | none | confirmed |
| M-014 | `workflows/**`, `registry/agents.yaml`, `registry/workflows.yaml`, `registry/templates.yaml`, `workflows/workflow-gate-matrix.md` | no-change-verified | F-008 (by extension of C-003) | none | confirmed |
| M-015 | `agents/architect.agent.md`, `agents/omn-dev-1-implement.agent.md`, `agents/omn-dev-2-reviewer.agent.md` (host registrations) | no-change-verified | F-008 | none | confirmed |

`M-011` through `M-015` are recorded because a reader would reasonably expect a cross-cutting
behavioral policy to touch the runtime, a template, or a registration surface. It does not:
the standard reaches every named phase through bindings that already exist (`F-001`–`F-003`).

### 5.2 Options Considered

| Option | Structural change | C-001 | C-006 | Impact surface | Reuse leverage | Migration burden | Outcome |
|---|---|---|---|---|---|---|---|
| O-001 | Extend S01 in place with new sections and an updated anti-pattern/common-mistake list; raise its recorded version | Satisfied | Satisfied | 0 | 9 | 0 | Selected |
| O-002 | Add the standard's content to `domain-model/agent-specification.md` | Satisfied | Violated | 0 | 9 | 0 | Eliminated on C-006 |
| O-003 | Duplicate the standard's content into each affected agent's own `reasoning.md` | Violated | Violated | 3 | 0 | 0 | Eliminated on C-001, C-006 |
| O-004 | Introduce a new, dedicated skill file for the ladder | Violated | Violated | 0 | 0 | 0 | Eliminated on C-001 |

Impact surface counts modules with `contract-change` or `dependency-change`; none exist in
this design (see 5.1), so every option scores 0 on that column. Reuse leverage counts
capabilities satisfied by `reuse-as-is` or `reuse-extended` in 7 below. O-004's `C-006`
column is scored `Violated` because a brand-new file carries no manifest skill binding or
context-slice membership of its own until a separate structural change adds one, which
`C-001` already forbids.

### 5.3 Selected Approach

- Selected: `O-001`.
- Structural change: extend S01 (`skills/architecture/clean-architecture-checklist.md`) in
  place with four new subsections — the ladder, the minimum-necessary-change definition, the
  safety floor, and the seven review questions — plus one new anti-pattern entry and one new
  common-mistake entry, and raise its recorded version from `1.0.0` to `1.1.0` in
  `registry/skills.yaml` and `skills/agent-skill-matrix.md`. The architect's own
  `reasoning.md` (A6, A9) and `quality.md` (A7.3) are extended in place to reference the same
  candidate-kind vocabulary. The target content for both is specified in the appendix below.
- Rationale: `O-001` is the only option satisfying both hard constraints that decide this
  question (`C-001`, `C-006`). It reuses an artifact ten agent manifests and ten phases
  already load, so it costs zero new files and zero runtime change.
- Highest-scoring rejected alternative and why it lost: `O-002`, adding the content to
  `domain-model/agent-specification.md`. It is also zero-impact-surface and equally reusable
  in principle, but `domain-model/agent-specification.md` is not a context-slice member of
  five of the seven named phases (`implementation`, `refactor-implementation`,
  `quality-review`, `code-quality-review`, `repository-quality-scan`), so it fails `C-006`
  outright.
- Tradeoffs accepted: S01 now carries two conceptually distinct bodies of guidance — general
  clean-architecture principles and the necessity-and-reuse governance ladder — inside one
  skill file. The alternative that would keep them separate (`O-004`) requires a new file,
  which a hard constraint forbids, so the tradeoff is accepted rather than designed away
  (see `D-001`).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Carry the necessity-and-reuse standard by extending S01 in place rather than any new file or a different existing document | Yes | ADR D-001, status Proposed |
| D-002 | Raise S01's recorded version from `1.0.0` to `1.1.0` under the MINOR rule for additive guidance, contingent on `A-003` | No | Inline; pure identity bookkeeping following from D-001, no independent contract, dependency, structural, or quality-attribute implication |
| D-003 | Extend the architect's own `reasoning.md` (A6, A9) and `quality.md` (A7.3) in place rather than any new module | No | Inline; reuse-extended of the agent's own existing procedure, no external contract or dependency change |
| D-004 | No new external dependency is introduced by this design; `T-013` is not applicable | No | Inline; rung 1 of the ladder applied to itself — no accepted statement requires a dependency capability, so none is surveyed or designed |

## API and Data Model Impact

None identified. No module in 5.1 is classified `contract-change` or `dependency-change`:
every edit is additive prose to an existing knowledge or procedure document (`extension` or
`behavior-change`), or a metadata update to an existing registry record. No API, schema, or
data model is touched (`C-002`, `C-003`), so no transition strategy, coexistence period, or
rollback position is required beyond the plain-text revert stated in Delivery Plan.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Deliver a shared necessity-and-reuse standard reachable by all seven named phases without a runtime change | S01 `skills/architecture/clean-architecture-checklist.md` | reuse-extended | F-001–F-003 establish S01 already reaches all seven phases through ten agent manifests' skill bindings and ten phases' context-slice membership; extending it in place needs no new file and no runtime change (`C-001`, `C-002`, `C-006`) |
| Same capability | The other eleven existing skill files (S02–S12) | rejected | None is bound to all seven named phases; each fails `C-006` for at least one phase (searched: `skills/agent-skill-matrix.md` phase-skill rows and `runtime/framework_runtime.py` `CONTEXT_SLICE_PHASE` entries for each of the seven phases) |
| Same capability | `domain-model/agent-specification.md` | rejected | Not a context-slice member of `implementation`, `refactor-implementation`, `quality-review`, `code-quality-review`, or `repository-quality-scan`; fails `C-006` (searched: the same `CONTEXT_SLICE_PHASE` entries) |
| Same capability | Per-agent duplication across each affected `reasoning.md` | rejected | Duplicating the same text into three or more private procedure modules is the duplication the standard itself forbids, and `structural-compliance` is not owned by `omn-dev-2-reviewer` at all, so no single agent's `reasoning.md` reaches every phase; fails `C-006` |
| Architect's own reuse-survey candidate-kind rule | `agents/architect/reasoning.md` A6 (existing procedure) | reuse-extended | F-009 establishes the survey already exists; the requested candidate kinds are added to it directly |
| Architect's own none-found self-check wording | `agents/architect/quality.md` A7.3 (existing check) | reuse-extended | F-010 establishes the check already exists; its wording is extended to name the same candidate kinds A6 states |
| Architect's own significance rule | `agents/architect/reasoning.md` A9 (existing list) | reuse-extended | F-011 establishes the five-item significance list already exists; a sixth item is appended |
| New external dependency for this change | — | none-found | Rung 1 of the ladder applied to itself: no accepted statement requires a new dependency to deliver this standard; the search covered the feature request, the change request, the business intent, and the architecture context for any stated need, and found none; recorded out of scope rather than surveyed (`D-004`) |
| Carrier skill's version identity update | `registry/skills.yaml`, `skills/agent-skill-matrix.md` (existing records) | reuse-extended | F-005 establishes both records already carry S01's identity; the version field is updated in place under the MINOR rule (`F-006`), contingent on `A-003` |

## Operational Considerations

- Logging and observability updates: None identified. No runtime code path, log statement, or
  observability signal is touched; every edit is documentation or registry-metadata prose
  (`C-002`).
- Error handling strategy: None identified. No executable error path is touched by this
  design; the safety floor's error-handling protection (`C-005`) is stated as policy content
  in `M-001` for a later implementer to apply to actual code changes, not exercised here.
- Security considerations: Assessed. The safety-floor content in `M-001` explicitly protects
  authorization, audit, validation, and data-integrity paths from being weakened under this
  policy's own banner (`C-005`); this design introduces no new attack surface because it
  edits no executable code, credential, or access path. `F-019` confirms the existing
  vendor-substring scan already governs artifact content, and this design's content contains
  no such substring.
- Performance considerations: None identified. No runtime code path is touched (`C-002`); the
  business intent's execution-cost constraint (`S-030`, `A-004`) is addressed structurally by
  choosing extension-in-place over any new reasoning stage, not by a runtime performance
  change.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The carrier-file decision and the standard's target content are fixed before any dependent module states or references the standard | M-001 | none | Every downstream procedure edit cites the same standard text; defining it after those edits begin forces rework if wording changes | T-001, T-002 |
| P-002 | The carrier skill's registry identity (`registry/skills.yaml`, `skills/agent-skill-matrix.md`) is raised to `1.1.0` only after the S01 content edit is final | M-001, M-002, M-003 | P-001 | A version identity must describe content that already exists; bumping first records a version for content not yet written | T-014 |
| P-003 | The architect's own `reasoning.md` (A6, A9) and `quality.md` (A7.3) wording changes are made only after the standard's content is final | M-004, M-005 | P-001 | The reuse-survey rule and its self-check reference the standard's candidate-kind list by name; they cannot precede content that does not yet exist | T-003 |
| P-004 | The implementer's `reasoning.md`, `output.md`, and `quality.md` wording changes are made only after the standard's content is final | M-006, M-007, M-008 | P-001 | Same citation reason as P-003 | T-004, T-005 |
| P-005 | The reviewer's `reasoning.md` wording change is made only after the standard's content is final | M-009 | P-001 | Same citation reason as P-003 | T-006 |
| P-006 | The packaging-mirror refresh runs only after every module edit under P-002 through P-005 is complete | M-010 | P-002, P-003, P-004, P-005 | Refreshing before every source edit lands risks a second refresh, and the drift test is only meaningful against final content | T-010 |
| P-007 | The post-change baseline verification runs only after every module edit and the mirror refresh are complete | M-001–M-010 | P-002, P-003, P-004, P-005, P-006 | Comparing against baseline before every edit lands would attribute an incomplete change's results to the finished design | T-009 |
| P-008 | The remaining supplied planner tasks this phase does not itself further sequence — the fresh pre-change baseline snapshot (`T-007`), the instruction-byte measurement (`T-008`), the closure package (`T-011`), the version-bump governance decision (`T-012`), and the dependency-significance recording (`T-013`) — carry no additional module-level structural prerequisite from this design beyond `P-001` through `P-007` | M-001 | P-001 | These tasks are owned by roles outside this design phase (`omn-tech-lead`, `omn-documentation`) or are already resolved by this design's own decision (`D-004` for `T-013`); recording them here closes planner-task coverage without inventing a module-level ordering constraint none of them structurally requires | T-007, T-008, T-011, T-012, T-013 |

No step here is irreversible: every edit is a text or metadata change with a trivial version-
control revert, so no reversibility safeguard step is required (`A10.5` is vacuously
satisfied).

### Test Strategy Focus Areas

For whoever verifies this phase's own deliverables: confirm the registry coverage verifier
still resolves S01 by its display name after the version bump (`C-009`); confirm
`runtime/design_validator.py` D7.3 still accepts a `none-found` row under the extended A7.3
wording; confirm, by inspecting resolved skill bindings and context-slice membership at
runtime `0.5.0`, that each of the seven named phases still receives S01 unchanged in
mechanism; confirm the `omn_agent` test suite and the packaging-mirror drift test both stay
at their recorded pass counts after P-006.

### Rollout and Rollback

Rollout follows `P-001` through `P-008` in order. Rollback is a plain-text revert of the
touched files (`M-001` through `M-005`, and the registry records) to their prior content;
no data migration, coexistence period, or consumer coordination is required, because nothing
this design touches is a runtime contract.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | `A-003` is false: extending S01's prose is judged a breaking rule/structure change rather than additive guidance | The version increment should be MAJOR, not MINOR, invalidating `T-014`'s classification | low | M-002, M-003, D-002 | `omn-tech-lead` confirms the classification before the registry edit lands (`P-002`) | omn-tech-lead |
| R-002 | delivery | `A-002` is false: an unrelated change lands on the recorded baseline between this design and the post-change verification | `T-009` cannot cleanly attribute a mismatch to this change alone | medium | P-007 | `T-007` (execution-planning phase) captures a fresh pre-change snapshot immediately before implementation begins; `T-009` compares against that snapshot, not against `F-021`/`F-022` directly | omn-tech-lead |
| R-003 | delivery | `A-005` is false: the workflow instead expects this design phase to write the affected files directly | `T-002` and `T-003` cannot close within this run's permitted-writes boundary; closure stalls until clarified | low | P-001, P-003 | This design states the full target content for `T-002` and `T-003` (appendix) so any downstream writer can apply it verbatim without re-deciding anything structural | omn-orchestrator |
| R-004 | structural | A future phase is added to the framework that the seven-phase list did not anticipate, and it does not receive S01 through any existing binding | The standard would not automatically reach a new phase without a further change | low | M-001 | None required now; `C-006`'s phase-coverage requirement is scoped to the seven named phases; a new phase's skill bindings are decided when that phase is designed | omn-tech-lead |
| R-005 | security | An implementer or reviewer reads "prefer less code" as license to relax a safety-floor item on a future change that also touches a trust boundary | A safety regression ships before the strengthened review catches it | low | M-006, M-008, M-009 | The safety-floor wording in the target content (appendix) makes removal or weakening of a safety-floor item a Blocking self-check failure for the implementer and a correctness-or-security finding for the reviewer, never a maintainability finding | omn-dev-2-reviewer |
| R-006 | delivery | The packaging-mirror refresh does not automatically pick up the content-only edits this design specifies | `tests/test_bundled_payload.py` fails, blocking closure | low | M-010 | Run the existing `--sync` refresh procedure first, per `P-006`; escalate only on failure | omn-dev-1-implement |

## Estimate and Confidence

- Overall: `M` (confidence: medium).
- Breakdown:
  - `P-001` (S01 content authoring, fully specified below): `S`, confidence high.
  - `P-002` (version bump, two registry records): `XS`, confidence low (depends on `A-003`).
  - `P-003` (architect's own `reasoning.md`/`quality.md` wording, fully specified below): `S`,
    confidence high.
  - `P-004` (implementer edits, structural requirement fixed here, exact wording delegated to
    `omn-dev-1-implement`'s own phase): `S`, confidence medium.
  - `P-005` (reviewer edit, same delegation): `S`, confidence medium.
  - `P-006` (mirror refresh, mechanical): `XS`, confidence high.
  - `P-007` (post-change verification): `S`, confidence low (depends on `A-002`).
- Scope assumptions: the estimate covers only this phase's own tasks (`T-001`, `T-002`,
  `T-003`, `T-013`, `T-014`) plus the sequencing this design hands to `T-004`, `T-005`,
  `T-006`, `T-009`, `T-010`. It excludes the closure package (`T-011`) and the version-bump
  governance decision (`T-012`), which are outside this agent's authority.
- Uncertainty drivers: `A-002` and `A-003` each hold two breakdown items at low confidence;
  the delegated wording for `P-004`/`P-005` holds two items at medium confidence because this
  design fixes their structural requirement but not their final prose.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does the workflow expect this design phase to write `skills/architecture/clean-architecture-checklist.md`, `agents/architect/reasoning.md`, and `agents/architect/quality.md` directly, or does a later implementation-phase agent apply this design's target content? | No | omn-orchestrator | P-001, P-003, D-001, D-003 | Either way, the content specified in the appendix is unchanged; only which phase performs the repository write differs |
| Q-002 | Is extending S01's prose with the content this design specifies "additive guidance" (MINOR) or a "breaking rule or structure change" (MAJOR) under `domain-model/skill-specification.md`? | No | omn-tech-lead | M-002, M-003, D-002, P-002 | MINOR confirms `1.1.0` as specified; MAJOR requires a different version target, decided before `P-002` |
| Q-003 | Do the additive edits to the `architect`, `omn-dev-1-implement`, and `omn-dev-2-reviewer` module sets warrant a contract-version increment in a later governance change (carried from the scope definition's `Q-002`)? | No | omn-tech-lead | none in this design directly; named because Sign-off shares the same owners | A "yes" opens a separate governance change; this design's content is unaffected either way |

Decision record `D-001` remains at status `Proposed` and requires Design Gate acceptance
before `P-002` and `P-003` begin.

## Sign-off

- Architect: architect (producing role; excluded from accepting this package)
- Tech Lead: omn-tech-lead (accepting owner for the Design Gate, per the Producer Exclusion
  Rule in `workflows/workflow-gate-matrix.md`)
- QA: omn-qa

## Appendix: Target Content for T-002 and T-003

This appendix states the target content this design specifies for the tasks the supplied
execution plan attributes to the `architect` role — the current shape and the target shape,
in the same idiom section 6 uses for a contract change. It is a specification for a later
writer to apply, not a diff or an edit command; per `A-005`/`Q-001`, the repository write
itself is performed by whichever agent the workflow directs.

### A.1 Target content for `skills/architecture/clean-architecture-checklist.md` (T-002)

Current shape: the skill ends after its `## Common Mistakes` section (`F-004`); the heading
`Skill: Architecture Foundations` indexes the registry record (`C-009`).

Target shape: the skill retains its unchanged heading and every existing section, followed
by four new subsections under one new heading, and one new line in each of the two existing
list sections named below.

New heading and subsections (target content, following the existing `## Common Mistakes`
section): a new level-2 heading titled "Necessity and Reuse Ladder", with the body below
rendered beneath it.

~~~markdown
Applies to every design option, every change-set entry, and every review of a change.
Understand the problem first: read the task and the code it touches, and trace the real
flow end to end. Then climb the ladder and stop at the first rung that holds.

1. Does this need to exist? A capability no accepted statement requires is not built; it
   is recorded as out of scope or raised as an open question to the owning role.
2. Does the codebase already have it? Reuse the existing helper, component, or pattern.
3. Does the standard library solve it? Use it.
4. Does the platform or framework in use solve it natively? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can it be written directly in a few lines at the call site? Write it there.
7. Only then: implement the minimum code necessary. A new abstraction, file, or dependency
   is introduced only when the reason no lower rung held is recorded.

### Minimum Necessary Change

Required behaviour, required safety, required integration, and required tests together
are the minimum necessary change. Everything outside that boundary requires a recorded
justification: opportunistic refactoring, cleanup of code the change does not touch,
speculative generalization, and configuration or extension points for requirements that
do not yet exist.

### Safety Floor

The ladder minimizes unnecessary code, never necessary protection. No simplification may
remove or weaken input validation at a trust boundary, error handling that prevents data
loss, authorization or audit paths, accessibility, observability the design requires, data
integrity, or the tests that prove the change. A shorter implementation is not
automatically better: correctness, readability, and maintainability are requirements, and
line count is not a criterion. Where two equally small solutions differ, the
edge-case-correct one is chosen.

### Review Questions

A change is measured against this ladder with seven questions, each answered against the
accepted change and the code, never against line count:

- Existence: was something built that no accepted statement requires?
- Reuse: does the change duplicate something the codebase already provides?
- Dependency: was a dependency added where the standard library, the platform, or an
  installed dependency already served?
- Abstraction: was an interface, wrapper, factory, helper class, or configuration point
  introduced before a second concrete use required it?
- Complexity: does a simpler implementation exist with the same behaviour and the same
  safety?
- Scope: did the change touch code the accepted change did not require?
- Safety: did a simplification remove or weaken anything the safety floor protects?

A finding under the first six questions is a maintainability or architecture finding at
the severity the evidence supports. A finding under the seventh is a correctness or
security finding.
~~~

Target addition, one new line in the existing `## Anti-patterns` list:

`- Speculative abstraction, generalization, or configuration for a requirement that does not exist.`

Target addition, one new line in the existing `## Common Mistakes` list:

`- Reducing line count by removing validation, error handling, or tests.`

Target identity: version `1.1.0`, recorded in `registry/skills.yaml` and in the Skill
Catalog row of `skills/agent-skill-matrix.md` (`D-002`, `P-002`).

### A.2 Target wording for `agents/architect/reasoning.md`, A6 Reuse Survey (T-003)

Current wording, first sentence: "For each capability the change requires, record the
existing components that could provide it and the outcome:"

Target wording: "For each capability the change requires, record the candidates that could
provide it — existing components, the standard library, native platform or framework
capability, and already-installed dependencies — and the outcome:"

Current wording, the `none-found` sentence: "A `none-found` outcome requires stating where
the search looked."

Target wording: "A `none-found` outcome requires stating which of these four candidate kinds
the search covered. Without that, it is indistinguishable from not having looked."

Target addition, a new closing sentence immediately after the existing sentence "Proposing
new structure over an unexamined existing component is a boundary violation under
`system.md` invariant 3.": "A capability that no statement requires is not surveyed and not
designed for; it is recorded as out of scope in the Objective section, or raised as an open
question to the owning role, per the necessity and reuse ladder in
`skills/architecture/clean-architecture-checklist.md`."

### A.3 Target wording for `agents/architect/reasoning.md`, A9 significance list (T-003)

Current shape: five bullets ending with "it commits the system to a quality-attribute
tradeoff".

Target shape: a sixth bullet follows it: "- it introduces a new external dependency".

### A.4 Target wording for `agents/architect/quality.md`, A7.3 (T-003)

Current wording: "Every `none-found` outcome states where the search looked"

Target wording: "Every `none-found` outcome states which of the four candidate kinds —
existing components, the standard library, native platform or framework capability,
already-installed dependencies — the search covered"

Severity is unchanged: `Blocking`.
