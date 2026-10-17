```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0001
  featureName: Lesson Store as an Open Knowledge Format Bundle
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/okf-lessons-feature-request.md
    - type: change-request
      reference: runs/inputs/okf-lessons-change-request.md
    - type: business-intent
      reference: runs/inputs/okf-lessons-business-intent.md
    - type: architecture-context
      reference: runs/inputs/okf-lessons-architecture-context.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  scopeVerdict: partially-bounded
  acceptanceCriteriaCount: 24
  inputDigest: sha256:a04c14e196b440b4f7962a21e5811f1b
  contextDigest: sha256:c1ad2ea0fc009dd392b176211321aa8f
```

## Metadata

- Feature name: Lesson Store as an Open Knowledge Format Bundle
- Requested by: Not stated in the supplied inputs
- Business goal: Lessons the framework learns are portable and reviewable, state where they came from and how far they can be trusted, and keep the governance the knowledge loop has today
- Target outcome: The lesson store is a conformant OKF v0.2 bundle, proven by a deterministic check, and agents receive unchanged lesson text at dispatch
- Scope decision date: 2026-10-17
- Status: provisional

## Business Context

- Problem statement: Lessons the framework has learned are held in one framework-private JSON document. Operators cannot read them as documents, other tools cannot consume them, and the record does not say who produced or confirmed a lesson.
- Value hypothesis: Lessons that state their origin and trust in an open, documented format can be reviewed and reused outside the runtime, with no loss of the governance the knowledge loop has today.
- Affected users: Framework operators who review and govern lessons; agents that receive lessons at dispatch; tools outside the runtime that read the lesson record.
- Success measure: The conformance check passes the bundle and fails seeded defects (`A-014`); each lesson states origin and trust (`A-004` to `A-007`); dispatch text is unchanged (`A-011`); existing verdicts stay at baseline (`A-022`).

## In Scope

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | Lessons are held as a bundle under the lesson memory location: one document per lesson, a root index that declares the OKF version, and a change log | Feature request, expected outcome 1 | must-have |
| `S-002` | Each lesson document states a type, title, description, and tags, each non-empty | Feature request, expected outcome 2 | must-have |
| `S-003` | Each lesson document states the run artifacts it was harvested from, and which producer generated it and when | Feature request, expected outcome 2 (sources, generated) | must-have |
| `S-004` | Each lesson document states whether an operator has approved it, and its status as draft, stable, or deprecated | Feature request, expected outcome 2 (verified, status); `D-001` | must-have |
| `S-005` | Every other lesson field, including governance history, stays readable in the lesson document under its own key | Feature request, expected outcome 2 (extension keys); business intent, Intent | must-have |
| `S-006` | The change log records each lesson's creation and each governance change, newest first | Feature request, expected outcome 1 (change log); `D-003` | must-have |
| `S-007` | Harvest, approve, retire, annotate, recall, effectiveness reporting, and the aggregation step read and write the bundle with the same results as before | Feature request, expected outcome 3 | must-have |
| `S-008` | Agents receive each lesson at dispatch with exactly the same text as before, including the existing neutralisation of field content | Feature request, expected outcome 3; business intent, Success | must-have |
| `S-009` | Re-harvesting unchanged run evidence leaves the bundle unchanged | Feature request, expected outcome 3 | must-have |
| `S-010` | An interrupted lesson write never leaves a lesson document, the index, or the change log partly written | Business intent, Intent (no loss of current behaviour); architecture context (current atomic write) | must-have |
| `S-011` | An operator can run a deterministic check of the bundle against OKF §11 on its own, and it reports pass or fail | Feature request, expected outcome 4; `D-004` | must-have |
| `S-012` | The lessons in the current store become documents with their identifiers and governance history intact, and the JSON store is removed | Feature request, expected outcome 5 | must-have |
| `S-013` | The change leaves every existing run evidence file unchanged | Feature request, constraints | must-have |
| `S-014` | The lesson bundle is absent from the installed payload and the bundled mirror, as the JSON store was | Feature request, constraints | must-have |
| `S-015` | The memory optimiser leaves the bundle unchanged | Feature request, constraints; change request, surfaces | must-have |
| `S-016` | Every existing gate, artifact validator, and verifier keeps its recorded baseline verdict | Business intent, Success | must-have |
| `S-017` | An operator can browse from the root index to every lesson document | Business intent, Problem; feature request, Request | should-have |
| `S-018` | The memory documentation describes the bundle in place of the JSON store | Change request, surfaces this change is expected to touch | should-have |

## Out of Scope

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Publishing the bundle outside the repository | Non-goal stated in the business intent | A separate request names an external consumer and a publication target |
| `X-002` | Changing which lessons are harvested, when they become eligible, or how they rank | Non-goal stated in the business intent | A separate change request on harvest eligibility or ranking |
| `X-003` | Converting any other memory document to OKF | Non-goal stated in the business intent | A separate change request names that document |
| `X-004` | Any process or machine actor that marks a lesson verified | The inputs name no confirming process (`D-001`) | A supplied requirement names the confirming process |
| `X-005` | Making the conformance check a mandatory item of the framework release checklist | A new mandatory item invalidates every recorded change proposal under rule F9 (architecture context) | A separate change to the F9 rule of the proposal validator |
| `X-006` | Changing the governance states, their meanings, or the governance actions | The request maps the three existing states and keeps the actions | A separate change request to lesson governance |
| `X-007` | Changing the Phase Model tables, agent module text, gates, or artifact validators | Listed as "not touched" in the change request | A separate change request naming one of them |

## Acceptance Criteria

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | The bundle holds one concept document per lesson record in the store at migration, plus `index.md` and `log.md`; zero missing or extra documents | `S-001` | count of concept documents and reserved files compared with the migrated record count | must-have |
| `A-002` | Root `index.md` frontmatter contains exactly one key, `okf_version`, with value `"0.2"` | `S-001` | read of the root index frontmatter by the conformance check | must-have |
| `A-003` | Every concept document has a non-empty `type`, `title`, and `description`, and a non-empty `tags` list; zero exceptions | `S-002` | conformance check over all concept documents | must-have |
| `A-004` | Each document's `sources` holds one entry per distinct run artifact path among its lesson evidence references, each with a non-empty `resource`; zero exceptions | `S-003` | comparison of each `sources` value with its lesson record evidence field | must-have |
| `A-005` | Every `generated.by` matches `<producer>/<version>` and every `generated.at` is an ISO 8601 instant with a UTC offset; zero non-matching values | `S-003` | pattern check over all concept documents | must-have |
| `A-006` | Every `status` is `draft` for candidate, `stable` for active, and `deprecated` for retired, matching the governance state of its lesson; zero mismatches | `S-004` | comparison of each `status` with the governance state in its lesson record | must-have |
| `A-007` | `verified` is present on exactly the lessons with an approval in their history, with a `human:<id>` actor and time; no `process:` actor appears | `S-004` | comparison of `verified` entries with approval entries in history | must-have |
| `A-008` | Every lesson field not mapped to a standard key by `S-002` to `S-004` appears under a producer extension key with an unchanged value, governance history included; zero missing or changed fields | `S-005` | field-by-field comparison of each migrated lesson record with its document | must-have |
| `A-009` | `log.md` opens with a title line, groups entries under `## YYYY-MM-DD` headings newest first, writes each entry as a Creation, Update, or Deprecation bullet in the bold-label form the format defines, and holds one entry per creation and governance action in history | `S-006` | format check of the change log and count comparison with history entries | must-have |
| `A-010` | Harvest, approve, retire, annotate, recall, effectiveness reporting, and the aggregation step produce on the bundle the same results they produced on the store for the same lesson set; zero mismatches | `S-007` | run of each step on the migrated bundle compared with results recorded before migration | must-have |
| `A-011` | The `render_section` output for the same lesson set is byte-identical before and after the change, including the neutralised field content; zero byte mismatches | `S-008` | byte comparison of the rendered section captured before migration with the rendered section after | must-have |
| `A-012` | A re-harvest over unchanged run evidence leaves every bundle file byte-identical, including `log.md`; zero changed files | `S-009` | harvest run twice over unchanged evidence, with a file hash comparison | must-have |
| `A-013` | An interruption injected at each write step leaves every concept document, `index.md`, and `log.md` in either its prior complete state or its new complete state; zero partly written files | `S-010` | fault injection at each write step, with a parse and state check after each | must-have |
| `A-014` | The conformance check passes the migrated bundle and fails each of three seeded defects: unparseable frontmatter, an empty `type`, and a root index that breaks the reserved-file rule | `S-011` | run of the check over the migrated bundle and over three seeded fixture bundles | must-have |
| `A-015` | The conformance check runs without the harvest, governance, or recall steps and gives identical output and exit status on two runs over the same bundle | `S-011` | standalone run twice, with output and exit status compared | must-have |
| `A-016` | Migration yields one concept document per lesson record in the store at migration time (42 at the time of the request), and the set of `lesson_id` values is identical before and after; zero missing or extra identifiers | `S-012` | count and set comparison of `lesson_id` values before and after migration | must-have |
| `A-017` | Each migrated lesson keeps its full governance history, with the same number of entries and the same actor and time on each entry; zero mismatches | `S-012` | per-lesson comparison of history entries before and after migration | must-have |
| `A-018` | `memory/lessons/lessons.store.json` does not exist after migration | `S-012` | file existence check | must-have |
| `A-019` | Every run evidence file that exists before the change keeps its hash; zero changed files | `S-013` | hash comparison of the pre-existing run evidence before and after the change | must-have |
| `A-020` | The installed payload and the bundled mirror contain zero files under the lesson bundle path, including files named `index.md`, `log.md`, or `L-*.md` in any directory | `S-014` | listing of the installed payload and the bundled mirror for the bundle path | must-have |
| `A-021` | A run of the memory optimiser leaves every bundle file byte-identical; zero changed files | `S-015` | hash comparison of the bundle before and after an optimiser run | must-have |
| `A-022` | Each existing gate, artifact validator, and verifier returns the verdict recorded as its baseline on the same inputs; zero changed verdicts | `S-016` | rerun of each against its recorded baseline | must-have |
| `A-023` | The root index links each concept document exactly once, with a description, under a `#` heading; zero missing or duplicate links | `S-017` | comparison of the index links with the set of concept document files | should-have |
| `A-024` | The memory documents named in the change request name no JSON store as the current lesson store; zero occurrences | `S-018` | text search of the named memory documents | should-have |

## Constraints and Dependencies

- Business constraints: No gate, validator, or acceptance rule is weakened (`S-016`); the dispatched lesson text does not change (`S-008`); harvest eligibility and ranking do not change (`X-002`).
- Regulatory or policy constraints: No run evidence under `runs/` is edited (`S-013`); the memory optimiser does not rewrite the bundle (`S-015`); the bundle stays out of installed copies and the bundled mirror (`S-014`). No regulatory constraint is supplied.
- Delivery constraints: Standard library only, with no third-party YAML dependency (feature request); the bundled mirror is refreshed by the framework sync step after the change (architecture context); affected areas recorded in the task context are database, performance, and security, assessed downstream.
- External dependencies: The OKF v0.2 SPEC, cited by the feature request, is not among the supplied inputs; the rules attributed to it are taken as the request states them (`Q-006`). The current lesson store, which the feature request states holds 42 lessons, is the migration source.

## Scope Decisions

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | `verified` is written only for an operator approval, with a `human:<id>` actor; no `process:` actor is introduced | The inputs define the process actor form but name no confirming process; a new confirmation would add behaviour the inputs do not support | No lesson is marked verified by a machine; a machine confirmation becomes a separate change (`X-004`) | omn-product-owner, on the approval rule the feature request states |
| `D-002` | `sources` holds one entry per distinct run artifact path; each full evidence reference is kept under a producer extension key | The request requires one entry per run artifact and that nothing the lesson store records is lost; evidence references point to events inside artifacts | A lesson's `sources` count can be lower than its evidence reference count; every reference stays readable (`S-005`) | omn-product-owner |
| `D-003` | Creation entries are written on a lesson's first write; update entries on approve and annotate; deprecation entries on retire | The three entry types of the format map to the governance actions the request names; the request asks for a change log without naming entry types | The entry count is fixed by the lesson history (`A-009`) | omn-product-owner |
| `D-004` | The carrier of the conformance check (module or command) is left to design; its behaviour is fixed here | The change request defers the carrier to design, and the choice of structure belongs to the architect | The location and invocation form stay open until design; `S-011`, `A-014`, and `A-015` bind behaviour only | omn-product-owner for the boundary; architect owns the carrier |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | What text populates `type`, `title`, `description`, and `tags` for each lesson, given that the lesson record holds none of these fields? (`S-002`) | yes | omn-business-analyst | Scope Gate (scope-and-acceptance) |
| `Q-002` | For the migrated lessons, do `generated.by` and `generated.at` carry the original harvest actor and time, or the migration actor and time? (`S-003`, `S-012`) | yes | omn-business-analyst | Scope Gate (scope-and-acceptance) |
| `Q-003` | What condition makes a lesson stale, and for which lessons does `stale_after` apply? No criterion for `stale_after` can be written until this is answered. (`S-004`) | yes | omn-business-analyst | Scope Gate (scope-and-acceptance) |
| `Q-004` | Does OKF v0.2 accept the `Z` designator as the UTC offset that every timestamp must carry, given that existing records use it? (`S-004`, `S-008`) | yes | omn-business-analyst | Scope Gate (scope-and-acceptance) |
| `Q-005` | Does the rendered lesson section, or any other dispatch output, include a timestamp or stored field whose format this change alters? (`S-008`) | yes | omn-context-agent | Scope Gate (scope-and-acceptance) |
| `Q-006` | The OKF v0.2 SPEC text is not among the supplied inputs. Is the request's statement of §5, §7, §8, §9, and §11 accurate? (`S-001`, `S-011`) | no | omn-business-analyst | solution-design-and-risk-assessment |
| `Q-007` | Should the conformance check be listed as an advisory item in the framework release checklist? (`S-011`, `X-005`) | no | omn-qa | solution-design-and-risk-assessment |

## Handoff

- Downstream owner: planner (execution-planning), after the gate; architect and omn-qa consume the same artifact
- Gate: Scope Gate (scope-and-acceptance); the decision rests with omn-business-analyst under the Producer Exclusion Rule
- Evidence for the gate: `S-001` to `S-018`, with the criteria `A-001` to `A-024` that bound them; `X-001` to `X-007`; `D-001` to `D-004`; and `Q-001` to `Q-007`, of which `Q-001` to `Q-005` are blocking and hold the verdict at `partially-bounded`. No gate decision and no readiness claim is recorded here.
- Deferred to downstream: decomposition into tasks, waves, and sequence (planner); the bundle reader and writer, the frontmatter writer and parser, the write and lock mechanism, the migration method, and the carrier of the conformance check (architect, `D-004`); the test strategy behind each verification method (omn-qa); the database, performance, and security assessments of the affected areas (planner and architect).
