```yaml
design:
  designId: run-79276e78d773-okf-lesson-bundle-technical-design
  changeReference: runs/inputs/okf-lessons-change-request.md
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/okf-lessons-feature-request.md
    - type: change-request
      reference: runs/inputs/okf-lessons-change-request.md
    - type: business-intent
      reference: runs/inputs/okf-lessons-business-intent.md
    - type: architecture-context
      reference: runs/inputs/okf-lessons-architecture-context.md
    - type: execution-plan
      reference: runs/run-79276e78d773/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003, D-004, D-005, D-006]
  consumesPlan: runs/run-79276e78d773/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:160718068b2d75a7e7d71628f2c09025
  contextDigest: sha256:7dc594ecd8e764b25cbc1e8aaab42fac
# Identifier notation. Bare S, F, A, C, M, O, D, P, R, Q tokens resolve against this design's own
# registers. S-001 to S-018 carry the same subjects as the scope statements of the same number
# (scope definition digest sha256:81bea5e4244406eb46c1b8bcf2b47c2a). Scope acceptance criteria are
# cited as AC-001 to AC-024 (the scope's own A-nnn criteria, renamed so they cannot collide with
# this design's assumptions). Scope exclusions are cited as X-001 to X-007, plan technical
# objectives as TO-1 to TO-6, and scope or plan decisions, assumptions, risks and questions by
# ordinal in words. Planner tasks T-001 to T-039 (plan digest
# sha256:54a4d2361348528162d4d0932767eae6) are cited, never created.
# Scope Gate and Planning Gate rulings and the operator notes are normalised as S-022 to S-034.
# Repository reads: the task context names no repository modules, so the sites the architecture
# context and change request name were read (runtime/knowledge.py, runtime/framework_runtime.py
# call sites, runtime/optimize_memory.py, omn_agent/source.py, tests/test_knowledge.py,
# tests/test_bundled_payload.py, the live lesson store). Rescan beyond them, reason: the advisory
# listing ruling names a dependency the context does not (validation/framework-release-checklist.md,
# runtime/change_proposal_validator.py F9, runtime/verify_self_hosting.py S5 and S10,
# runtime/self_hosting.py), and a text search for the store name located the documents of F-020.
# The supplied OKF v0.2 SPEC copy was read for T-001 (5.3, T-001 verdicts).
# Skills: S01, S02, S06, S08, S09, S12 inform this design. S03 was read; the runtime under change
# is not .NET (F-025), so it informs nothing here. Affected areas recorded: database (the store
# migration, D-005), performance (recall reads one file per lesson, R-006), security (field
# content reaching document structure, R-001, R-016).
```

## Metadata

- Feature or Change ID: run-79276e78d773 (/implement, implement-feature v1.0.0, framework-internal capability addition)
- Author: architect 1.0.0
- Reviewers: omn-tech-lead, omn-architect (Design Gate); omn-qa for the test strategy focus areas; omn-product-owner for Q-002 and Q-006
- Last Updated: 2026-10-17

## Objective

- Desired outcome: The lesson store becomes an OKF v0.2 bundle of Markdown concept documents, a root index, and a change log under memory/lessons, which a third party can browse, link, and check, while every lesson-loop step, the dispatched lesson text, and every recorded verdict behave as before.
- Architectural objectives:
  - One lesson-agnostic, standard-library module owns the frontmatter subset writer and parser and the OKF §11 check, and depends on no lesson-loop code; the lesson loop depends on it one-way (S-011, S-019, S-033).
  - The lesson loop's store boundary changes form only: load and write keep the in-memory record shape, so harvest, governance, eligibility, recall, rendering, and effectiveness stay unchanged above it (S-005, S-007, S-008).
  - Every bundle file is a deterministic function of the lesson records, with no write-time value, and each file is replaced whole (S-009, S-010, S-023, S-024, S-027).
  - The bundle path is excluded from distribution and from the memory optimiser by its relative path, and nothing else is newly excluded (S-014, S-015, S-030).
  - The JSON store is retired only after a verified, record-for-record migration (S-012, S-033).
- In scope: OKF rule verdicts (T-001), the bundle layout, lesson document mapping, serialisation subset, reserved-file contracts, write and read contract, bundle digest, stale_after rule, conformance check and its standalone verifier, advisory checklist item, migration and JSON removal, payload and optimiser exclusions, runtime version, documentation surfaces, mirror refresh, and the test strategy.
- Out of scope:
  - Publishing the bundle outside the repository (X-001).
  - Any change to harvest eligibility, timing, ranking, governance states, or governance actions (X-002, X-006).
  - Converting any other memory document to OKF (X-003).
  - A process or machine actor in verified (X-004).
  - A mandatory checklist item for the conformance check (X-005).
  - Any change to Phase Model tables, agent module text, gates, or artifact validators (X-007).
  - Any edit to an existing file under runs/, including envelopes that name the JSON store (S-013).
  - Any change to the recall ranking or rendering text; stale_after is not read by recall (S-008, X-002).

## Requirements Summary

- Functional requirements:
  - Bundle at memory/lessons: one concept document per lesson, a root index declaring okf_version, and a change log (S-001, S-029).
  - Each document states type, title, description, tags, sources, generated, status, verified where approved, and every other lesson field under an extension key (S-002 to S-005, S-022, S-023).
  - The change log records each creation and governance change, newest first, dated from record fields (S-006, S-027).
  - Harvest, approve, retire, annotate, recall, effectiveness reporting, and the aggregation step behave as before on the bundle (S-007); new envelopes name the bundle (S-026).
  - A standalone deterministic OKF §11 check reports pass or fail, listed as an advisory release-checklist item (S-011, S-031).
  - Existing lessons migrate with identifiers and history intact, and the JSON store is removed (S-012).
  - The bundle is absent from the payload and mirror, and the optimiser leaves it unchanged (S-014, S-015).
  - Memory documentation describes the bundle (S-018); the root index links every document (S-017).
- Non-functional requirements:
  - Determinism: re-harvest over unchanged evidence leaves every bundle file byte-identical (S-009).
  - Interruption safety: no bundle file is ever partly written (S-010).
  - Standard library only (S-019).
  - No lesson field value can alter document, index, or log structure (TO-5; S-008, S-017).
  - Baseline verdicts of every gate, validator, and verifier hold (S-016); no run evidence file changes (S-013).
- Acceptance criteria:
  - AC-001 to AC-003 and AC-023 bind the bundle layout and index (S-001, S-002, S-017).
  - AC-004 to AC-008 bind the document mapping (S-003 to S-005); AC-009 the change log (S-006).
  - AC-010 to AC-013 bind loop parity, render bytes, idempotency, and interruption (S-007 to S-010).
  - AC-014 and AC-015 bind the conformance check (S-011); AC-016 to AC-018 migration (S-012).
  - AC-019 to AC-022 bind protected surfaces (S-013 to S-016); AC-024 documentation (S-018).
  - The stale_after criterion (S-024) is to be recorded by omn-product-owner under T-010 (Q-002).

Statements (normalised from the supplied inputs and rulings, in source order):

| ID | Statement | Source |
|---|---|---|
| S-001 | Lessons are held as a bundle: one document per lesson, a root index declaring the OKF version, and a change log | scope S-001 |
| S-002 | Each lesson document states a non-empty type, title, description, and tags | scope S-002 |
| S-003 | Each lesson document states its source run artifacts, and which producer generated it and when | scope S-003 |
| S-004 | Each lesson document states operator approval and its status as draft, stable, or deprecated | scope S-004 |
| S-005 | Every other lesson field, governance history included, stays readable under its own key | scope S-005 |
| S-006 | The change log records each creation and each governance change, newest first | scope S-006 |
| S-007 | Harvest, approve, retire, annotate, recall, effectiveness reporting, and aggregation work on the bundle with the same results | scope S-007 |
| S-008 | Agents receive each lesson at dispatch with exactly the same text as before | scope S-008 |
| S-009 | Re-harvesting unchanged evidence leaves the bundle unchanged | scope S-009 |
| S-010 | An interrupted write never leaves a document, the index, or the change log partly written | scope S-010 |
| S-011 | An operator can run a deterministic standalone OKF §11 check that reports pass or fail | scope S-011 |
| S-012 | Current lessons become documents with identifiers and history intact, and the JSON store is removed | scope S-012 |
| S-013 | Every existing run evidence file stays unchanged | scope S-013 |
| S-014 | The bundle is absent from the installed payload and the bundled mirror | scope S-014 |
| S-015 | The memory optimiser leaves the bundle unchanged | scope S-015 |
| S-016 | Every existing gate, artifact validator, and verifier keeps its baseline verdict | scope S-016 |
| S-017 | An operator can browse from the root index to every lesson document | scope S-017 |
| S-018 | The memory documentation describes the bundle in place of the JSON store | scope S-018 |
| S-019 | Standard library only; no third-party YAML dependency | feature request, constraints |
| S-020 | Framework-internal change under the self-hosting profile; the mirror is refreshed only by the framework sync step | change request; delivery constraints |
| S-021 | Non-goals and exclusions X-001 to X-007 bound the change | business intent; scope exclusions |
| S-022 | type, title, description, and tags come only from existing record fields | Scope Gate ruling on the first scope question |
| S-023 | generated.by is producer/version and generated.at is last_seen | Scope Gate ruling on the second scope question; operator note |
| S-024 | The stale_after rule derives from record fields only, with no wall clock; "applies to none" only if justified | Scope Gate ruling on the third scope question; operator note |
| S-025 | Z is an explicit UTC offset | Scope Gate ruling on the fourth scope question |
| S-026 | render_section shows no timestamp; memory_slice store and store_digest of new envelopes name the bundle | Scope Gate ruling on the fifth scope question |
| S-027 | A lesson with empty history gets a deterministic creation entry dated from first_seen | Scope Gate ruling |
| S-028 | AC-004 compares on the artifact path without the fragment suffix | Scope Gate ruling |
| S-029 | Bundle at memory/lessons as index.md, log.md, and L-*.md; the lock file is not a .md file | Planning Gate ruling |
| S-030 | Distribution and optimiser exclusions are scoped by relative path (T-030, T-034) | Planning Gate ruling |
| S-031 | The conformance check is listed as advisory only | Planning Gate ruling (X-005; closes the plan's second question) |
| S-032 | RUNTIME_VERSION becomes 0.11.0 under FR-07; T-012 owns it; T-029 excludes the version string from verdict comparison | Planning Gate ruling |
| S-033 | No implementation before the Design Gate; T-014 read-only first; lesson set frozen until T-027; T-025, T-026, T-027, T-013 land as one change; T-001 uses the supplied SPEC; plan assumption five confirmed | Planning Gate conditions |
| S-034 | Description neutralised as render_section does; an extension key carries every record field so load returns identical records | operator notes |
| S-035 | Artifacts write framework paths without the dot-directory prefix and carry no vendor substring | architecture context |

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | STORE_REL is memory/lessons/lessons.store.json, LOCK_REL memory/lessons/lessons.store.lock, STORE_SCHEMA framework.memory/lessons.v1; canonical bytes are sorted-key, two-space, ASCII-escaped JSON with a trailing newline; write_store writes a temporary file then os.replace, only when bytes differ, and returns whether it wrote | runtime/knowledge.py constants, canonical_bytes, write_store |
| F-002 | load_store returns schema and lessons, or None when no store exists, and raises store-unreadable on a malformed store | runtime/knowledge.py load_store |
| F-003 | StoreLock is an exclusive-create lock file with a timeout and error class lock-contention; harvest_for_run tries the lock once, records skipped or failed in knowledge-harvest.json, and never raises | runtime/knowledge.py StoreLock, harvest_for_run |
| F-004 | A lesson record has 20 fields in LESSON_FIELDS order (lesson_id to history); lesson_id is L- plus 10 hex of the fingerprint digest; values are strings, integers, nulls, lists, and history mappings | runtime/knowledge.py LESSON_FIELDS, lesson_id_for; memory/lessons/lessons.store.json |
| F-005 | approve moves candidate or retired to active, retire moves candidate or active to retired, annotate sets remedy; each appends one history entry of action, from, to, actor (one line, cap 300), rationale, and time from the clock | runtime/knowledge.py TRANSITIONS, govern |
| F-006 | neutralise collapses to one line, turns double quotes and backticks into single quotes, drops non-printables, and caps; render_section uses it with cap 160 for the description and shows no timestamp | runtime/knowledge.py neutralise, render_section |
| F-007 | recall returns store as STORE_REL and store_digest as the digest of the store file bytes; dispatch_memory_slice fails open on any recall error | runtime/knowledge.py recall, dispatch_memory_slice |
| F-008 | harvest rebuilds evidence fields from scratch, carries governance fields by fingerprint, marks a lesson with no current evidence retained, writes nothing when nothing is computed and no store exists, and reports store and store_digest in its outcome | runtime/knowledge.py harvest |
| F-009 | knowledge.py imports only the standard library and state_engine, enforced by a module boundary test | runtime/knowledge.py imports; tests/test_knowledge.py ModuleBoundaryTestCase |
| F-010 | RUNTIME_VERSION is 0.10.0; framework_runtime.py reaches the loop only through plan_record, run_record, dispatch_memory_slice, render_section, and harvest_for_run, and names no store path | runtime/framework_runtime.py RUNTIME_VERSION and kl call sites |
| F-011 | The live store holds 43 lessons, all candidate, all with empty history, evidence_state current, and remedy null, two of them gate lessons; evidence references are run artifact paths with a fragment that may contain spaces; some descriptions contain colons and apostrophes | memory/lessons/lessons.store.json |
| F-012 | AC-016 records 42 lessons at request time; the store now holds 43 and carries evidence from this run, so the lesson set has moved since the request | scope definition AC-016; memory/lessons/lessons.store.json; working-tree status |
| F-013 | EXCLUDE_PATTERNS includes lessons.store.*, matched by name against path parts in _walk; memory is a seed directory; enumerate_payload and enumerate_seeds both go through _walk, which has the base-relative path | omn_agent/source.py |
| F-014 | The bundle parity test builds its payload map through _walk and fails on any bundled file absent from that map | tests/test_bundled_payload.py |
| F-015 | The optimiser scans memory and context, denies path segments such as runs and reports and the names changelog.md, change-log.md, history.md, memory.md, classifies only .md files, does not deny index.md or log.md, and its generated marker does not match an OKF generated mapping | runtime/optimize_memory.py DENIED_SEGMENTS, DENIED_NAMES, GENERATED_MARKERS, _denied, classify |
| F-016 | The release checklist has FR-01 to FR-12, FR-11 and FR-12 advisory; the release-checklist mode runs command items and only a failing mandatory item fails S10; S5 requires a command item's script path to exist and its owner to be host-invocable | validation/framework-release-checklist.md; runtime/verify_self_hosting.py S5, S10; runtime/self_hosting.py |
| F-017 | Proposal check F9 requires a result row only for mandatory checklist items | runtime/change_proposal_validator.py F9 |
| F-018 | tests/test_knowledge.py names the JSON store in its copy-ignore pattern, idempotency file set, lock-name filter, optimiser test, dispatch store assertion, unreadable-store fixture, aggregation absence checks, payload exclusion test, and expects RUNTIME_VERSION 0.10.0 | tests/test_knowledge.py |
| F-019 | BackwardCompatibilityTestCase rebuilds the pre-change runtime from REFERENCE_COMMIT and a frozen KNOWLEDGE_CHANGE_SET that lists the JSON store; the set is read only to select runtime code files and to test context-slice membership, never for file existence; its re-baseline rule forbids changing it in the same change as runtime/knowledge.py | tests/test_knowledge.py BackwardCompatibilityTestCase, reference_runtime_sources, framework_relative |
| F-020 | config/runtime.md, memory/README.md, and memory/memory-governance.md name the JSON store as the lesson store; memory/memory-resolver.md describes lesson resolution; the knowledge.py module text names it too | text search of config/, memory/, runtime/ |
| F-021 | runtime/README.md lists runtime scripts in a table that omits knowledge.py and optimize_memory.py; FC-022 documented the loop in config/runtime.md and memory documents only; runtime/README.md is a context-slice member | runtime/README.md; FC-022 technical design C-016; this dispatch's context slice |
| F-022 | A dispatch of a completed item is replay-suppressed before any envelope is built, and M14 replays only completed items | runtime/verify_multi_phase.py M14; runtime/framework_runtime.py cmd_dispatch |
| F-023 | OKF v0.2: index.md and log.md are reserved at every level (§3.1); type is the only required key and producers may add keys that consumers preserve (§4.1); index files carry no frontmatter except okf_version in the root index, and list entries under # headings (§8, §12); log.md groups entries under ## YYYY-MM-DD headings, newest first (§9); §11 requires parseable frontmatter, a non-empty type, and reserved files following §8 and §9 | supplied OKF v0.2 SPEC copy |
| F-024 | OKF v0.2: sources entries require resource, which may be a relative path (§5.1, §6.2); generated (by required) and verified (list of by and at) are both in §5.2; §5.3 is trust tiers; status is draft, stable, or deprecated (§5.4); stale_after is an absolute instant, stale when now is at or past it (§5.5); timestamps carry an explicit offset and the examples use Z; actors are producer/version, human:id, or process:id (§7) | supplied OKF v0.2 SPEC copy |
| F-025 | The runtime under change is standard-library Python; the .NET stack in the technical context describes product delivery | runtime/*.py; context/technical-context.md |
| F-026 | Evidence references are relative to the framework root, and the bundle lies two directory levels below it | memory/lessons/lessons.store.json evidence values; S-029 |
| F-027 | The aggregation harvest runs at complete, gate, and aggregate for any run carrying a knowledge_loop record, this run included, and rewrites the live store | runtime/framework_runtime.py harvest_for_run call site; this run's dispatch prompt lesson section; F-012 |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | No installer, sync, or test path other than _walk enumerates memory files | The path-scoped exclusion relies on _walk alone (D-006) | Bundle files could ship by another path; D-006 changes | omn-dev-1-implement |
| A-002 | The package-data globs already cover any new runtime .py file | M-001 and M-004 must reach installs and the mirror | The declared-globs test fails until a glob is added | omn-dev-1-implement |
| A-003 | S-010 asks each file to be complete on its own, not that documents, index, and log agree after an interruption (plan assumption four) | Fixes the write contract's guarantee (D-003) | Cross-file agreement needs a staged directory swap; D-003 changes | omn-business-analyst |
| A-004 | A consumer resolves a relative sources resource against the document's own location (§6.2), so a two-level-up path reaches the run artifact | Fixes the sources value form (D-002) | Resources must use another form; AC-004's comparison changes | omn-qa |
| A-005 | Reading one document per lesson at each hydrated dispatch is acceptable at current lesson counts; no latency budget is stated | Recall reads the whole bundle (D-003) | An index-only fast path or cache is needed | omn-tech-lead |
| A-006 | No lesson record value is a float or another type outside F-004 | The serialiser refuses floats (D-007) | A write fails with store-unwritable until the type is supported | omn-dev-1-implement |
| A-007 | No aggregation of a knowledge-loop run happens between T-014 and T-027, so the lesson set stays frozen as S-033 requires | Same-set comparisons for AC-010, AC-011, AC-016 (F-027) | Parity runs against a captured copy and the migration count is taken at T-025 | omn-tech-lead |
| A-008 | FR-08 inspection accepts config/runtime.md and the memory documents as the documentation of the bundle and the verifier, as for FC-022 (F-021) | Avoids editing a context-slice member mid-run | runtime/README.md gains a row and later dispatches see a new context digest | omn-documentation |
| A-009 | AC-019 is measured over run directories other than the carrying run, whose own state and event files the runtime appends to | The carrying run's evidence changes as the run proceeds (F-027) | AC-019 cannot pass as worded for the carrying run | omn-qa |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | functional | Bundle at memory/lessons: L-*.md per lesson, index.md with okf_version "0.2", log.md; the lock file is not .md | hard | S-001, S-029 |
| C-002 | functional | type, title, description, tags non-empty and derived only from record fields | hard | S-002, S-022 |
| C-003 | functional | sources holds one entry per distinct artifact path; generated.by is producer/version, generated.at is last_seen; every instant carries the Z offset | hard | S-003, S-023, S-025, S-028 |
| C-004 | functional | verified only for operator approvals with a human actor; status draft, stable, deprecated for candidate, active, retired | hard | S-004, S-021 |
| C-005 | functional | Every record field is kept under an extension key, and the read path returns records equal to those written | hard | S-005, S-034 |
| C-006 | functional | The change log holds one creation entry per lesson and one entry per history entry, newest first, dated from record fields | hard | S-006, S-027 |
| C-007 | functional | Loop steps give the same results, and rendered lesson text is byte-identical | hard | S-007, S-008, S-026 |
| C-008 | quality-attribute | Every bundle byte derives from record fields; no write-time value; re-harvest is byte-identical | hard | S-009, S-023, S-024 |
| C-009 | quality-attribute | Each bundle file is replaced whole; no partial file survives an interruption | hard | S-010 |
| C-010 | functional | A deterministic §11 check runs standalone, without harvest, governance, or recall | hard | S-011 |
| C-011 | migration | Migrated lessons keep identifiers, fields, and history; the JSON store is removed only after complete migration is verified | hard | S-012, S-033 |
| C-012 | compliance | No existing run evidence file is edited | hard | S-013 |
| C-013 | operability | The bundle is excluded from payload and mirror by relative path; no other path is newly excluded | hard | S-014, S-030 |
| C-014 | operability | The optimiser leaves the bundle unchanged, scoped by relative path | hard | S-015, S-030 |
| C-015 | structural | Gates, artifact validators, Phase Model tables, and agent text unchanged; every verifier keeps its baseline verdict | hard | S-016, S-021 |
| C-016 | structural | Standard library only | hard | S-019 |
| C-017 | security | No field value can add, remove, or reorder frontmatter keys, index entries, or log entries, or form a path outside the bundle | hard | S-008, S-017 |
| C-018 | operability | The conformance check is an advisory checklist item, never mandatory | hard | S-031 |
| C-019 | operability | RUNTIME_VERSION 0.11.0, set after the baseline exists | hard | S-032, S-033 |
| C-020 | operability | Mirror refreshed by the sync step only; change proposal and release checklist under the self-hosting profile | hard | S-020 |
| C-021 | compliance | Artifacts write paths without the dot-directory prefix and carry no vendor substring | hard | S-035 |
| C-022 | quality-attribute | The conformance check depends on no lesson-loop code and works on any bundle path | negotiable | S-011 |
| C-023 | quality-attribute | Dispatch recall cost stays proportional to lesson count; no budget is stated | negotiable | S-007 |
| C-024 | functional | The root index links each concept document exactly once, with a description, under a # heading | hard | S-017 |
| C-025 | operability | The memory documents name the bundle and no JSON store as the current lesson store | hard | S-018 |
| C-026 | structural | Governance states, actions, harvest eligibility, and ranking are unchanged | hard | S-021 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | runtime/okf.py (new) | extension | F-023, F-024, F-025 | frontmatter subset dump and parse; document split and join; conformance over a bundle directory | confirmed |
| M-002 | runtime/knowledge.py | contract-change | F-001 to F-009 | BUNDLE_REL replaces STORE_REL; load_store, write_store, StoreLock path; recall store and store_digest; harvest outcome store fields; migrate subcommand; new error classes; imports M-001 | confirmed |
| M-003 | memory/lessons (store data: JSON document to bundle) | contract-change | F-011, F-012, F-026 | on-disk lesson store format and file set | confirmed |
| M-004 | runtime/verify_okf_bundle.py (new) | extension | F-016, F-023 | standalone verifier: optional path, JSON output, exit status | confirmed |
| M-005 | runtime/framework_runtime.py | behavior-change | F-010 | RUNTIME_VERSION 0.11.0 only; call sites unchanged | confirmed |
| M-006 | omn_agent/source.py | behavior-change | F-013, A-001 | EXCLUDE_PATHS added; lessons.store.* retired from EXCLUDE_PATTERNS | confirmed |
| M-007 | runtime/optimize_memory.py | behavior-change | F-015 | _denied gains the memory/lessons segment-pair rule | confirmed |
| M-008 | validation/framework-release-checklist.md | extension | F-016, F-017 | advisory item FR-13 | confirmed |
| M-009 | config/runtime.md | behavior-change | F-020 | store and lifecycle paragraph | confirmed |
| M-010 | memory/README.md | behavior-change | F-020 | lesson category description | confirmed |
| M-011 | memory/memory-governance.md | behavior-change | F-020 | lesson store location and lifecycle | confirmed |
| M-012 | memory/memory-resolver.md | behavior-change | F-020 | lesson resolution text | confirmed |
| M-013 | tests/test_knowledge.py | behavior-change | F-018, F-019 | test fixtures and assertions naming the store; new okf, migration, conformance, interruption tests | confirmed |
| M-014 | omn_agent/_bundled_payload mirror | operational-impact | F-013, F-014 | refreshed by sync; carries M-001, M-002, M-004, M-005, M-007 to M-012 | confirmed |
| M-015 | tests/test_bundled_payload.py | no-change-verified | F-014 | inherits the exclusion through _walk; a bundle file in the mirror fails parity | confirmed |
| M-016 | runtime/execution_metrics.py | no-change-verified | F-010 | reads invocation events, never the store | confirmed |
| M-017 | runtime/state_engine.py | no-change-verified | F-009 | digest helper reused | confirmed |
| M-018 | runtime/change_proposal_validator.py | no-change-verified | F-017 | F9 still mandatory-only | confirmed |
| M-019 | runtime/verify_self_hosting.py and runtime/self_hosting.py | no-change-verified | F-016 | checklist parse and S5, S10 unchanged | confirmed |
| M-020 | runtime/README.md | no-change-verified | F-021, A-008 | context-slice member left untouched | confirmed |
| M-021 | runtime artifact validators, workflows/implement-feature.md Phase Model, agent module sets | no-change-verified | F-022, F-010 | none | confirmed |
| M-022 | config/knowledge-policy.json | no-change-verified | F-008 | threshold and owner keys unchanged | confirmed |
| M-023 | existing run evidence under runs/ | no-change-verified | F-007, F-022 | old envelopes and knowledge-harvest.json keep the JSON store name | confirmed |

Boundary crossings: M-002 to M-001 (in-process, one-way); M-004 to M-001 (in-process, one-way; never M-002); M-005 to M-002 (unchanged one-way calls); M-002 to M-003 (all reads and writes under the lock); M-006 to the installer and mirror boundary; M-007 to the optimiser scan boundary; M-019 to M-004 (subprocess through the checklist). M-001 imports nothing from the framework.

### 5.2 Options Considered

| Option | Structural change | Hard constraints | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|
| O-001 | Serialiser, parser, bundle IO, and §11 check all inside M-002; the verifier imports M-002 | all met | 2 (M-002, M-003) | 10 of 15 capabilities | meets C-008, C-009, C-017; weaker on C-022 (check loads the loop module and its policy dependency) | one migration of 43 records | verifier tied to the loop module | viable; second on criterion 4 (C-022) |
| O-002 | New lesson-agnostic M-001 (serialiser, parser, §11 check); M-002 maps lessons to documents through it; verifier M-004 imports M-001 only | all met | 2 (M-002, M-003) | 10 of 15 capabilities | meets C-008, C-009, C-017, and C-022 | one migration of 43 records | verifier works on any bundle path | selected: highest score |
| O-003 | Keep the JSON store as source of truth and generate the bundle as an export | eliminated: violates C-011 (JSON store not removed) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-011 |
| O-004 | Lesson record as a fenced JSON block in each document body | eliminated: violates C-005 (fields not under their own frontmatter key) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-005 |
| O-005 | Third-party YAML library for frontmatter | eliminated: violates C-016 | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-016 |
| O-006 | Documents per lesson, with log.md appended incrementally at write time instead of derived from records | eliminated: violates C-006 and C-008 (entries for migrated lessons and recovery depend on write history and time) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | not scored (eliminated) | eliminated by C-006, C-008 |

Recomputed ranking: criterion 1 leaves O-001 and O-002; criterion 2 ties at 2; criterion 3 ties at 10 of 15; criterion 4 favours O-002 on C-022; O-002 ranks first, O-001 second.

### 5.3 Selected Approach

- Selected: O-002.
- T-001 verdicts (supplied SPEC copy; answers the plan's architect-owned first question; plan assumption one holds, plan risk one does not materialise):
  - §5.1 matches the request; resource is required in each entry (F-024).
  - §5.2 holds both generated and verified; the request's placement of verified in §5.3 is a numbering slip, since §5.3 is trust tiers, which this design does not use. No contract changes.
  - §5.4 and §5.5 match; status is always written, so the default never applies.
  - §7 matches: producer/version, human:id, process:id.
  - §8 matches; the entry description is a SHOULD, and this design always writes one.
  - §9 matches on ISO date headings, newest first; the bold leading word is a convention, not a rule, so the check does not enforce it while the writer always emits it (Q-003).
  - §11 matches; rule 2 is applied to concept documents, because §8 limits the root index frontmatter to okf_version (Q-003).
  - Z satisfies the explicit-offset rule, consistent with S-025 and the SPEC examples.
- Structural change:
  - Module M-001 (D-001). Standard library only, no framework import. Offers: dump a mapping to the frontmatter subset, parse the subset, split and join a document into frontmatter and body, and conformance over a bundle directory.
  - Serialisation subset (D-007).
    - UTF-8 without BOM, LF endings, trailing newline; the document opens with a line of three dashes and the frontmatter closes with the same line.
    - Keys are bare and must match a letter or underscore followed by letters, digits, or underscores; indentation is two spaces.
    - Every string is double-quoted. Backslash and double quote are backslash-escaped. Every character outside printable ASCII becomes a four-hex or eight-hex unicode escape, so frontmatter bytes are ASCII only and no value can span a line.
    - null, true, false, and base-10 integers are bare; floats are refused (A-006).
    - Lists and mappings are block form. A list of mappings puts its first key on the dash line. Empty collections are written as empty flow brackets.
    - Mapping key order is the caller's order for the top level and the lesson_record mapping, and sorted for every nested mapping.
    - The parser accepts that canonical form, plus plain scalars (null, tilde, or empty as null; true and false; integers; anything else a string), single-quoted strings, one-line flow lists and mappings of scalars, and full-line comments. Anything else is unparseable.
  - Bundle layout and mapping (D-002).
    - BUNDLE_REL is memory/lessons. Each concept document is named lesson_id plus .md; index.md and log.md complete the bundle; the lock is memory/lessons/lessons.lock.
    - Before a file name is formed, lesson_id must match L- followed by exactly 10 lowercase hex characters; otherwise the write fails with store-unwritable.
    - Frontmatter keys, in this order:
      - type: always Lesson.
      - title: neutralised kind (cap 40), a space, neutralised check_id or else gate or else a question mark (cap 60), the word on, and neutralised artifact_type (cap 60).
      - description: the check description neutralised at cap 160 exactly as render_section does, or "no description recorded".
      - tags: kind, artifact_type, then each phase, each neutralised (cap 60), de-duplicated in order with empties dropped; the single tag lesson if nothing remains.
      - sources: one entry per distinct evidence path. The path is the text before the first hash; resource is that path prefixed by two parent-directory steps (F-026, A-004). Entries are sorted, and the key is omitted when there is no evidence.
      - generated: by is knowledge-loop/1.0.0, where 1.0.0 is the lesson document format version; at is last_seen, or first_seen when last_seen is absent; the key is omitted when neither exists.
      - verified: present only when history holds approve entries; one entry per approve entry, in history order. by is human: followed by the actor sanitised (characters outside letters, digits, dot, underscore, at, and hyphen become hyphens, trimmed, cap 64, a leading human: prefix dropped, empty becomes unknown); at is the entry time.
      - status: candidate is draft, active is stable, retired is deprecated, anything else is draft.
      - stale_after: see D-004.
      - lesson_record: every LESSON_FIELDS value, in LESSON_FIELDS order.
    - Body: a level-1 heading with the title, a blank line, then a line reading Summary: followed by the description. The body is never read back.
  - Read and write contract (D-003).
    - load_store returns None when the bundle directory holds neither index.md nor any L-*.md. Otherwise it parses every L-*.md at the bundle root and requires type Lesson, a lesson_record mapping holding exactly the LESSON_FIELDS keys, and lesson_id equal to the file stem; any failure raises store-unreadable naming the file.
    - It returns schema STORE_SCHEMA (kept as the in-memory interface identifier) and the lessons sorted by fingerprint, so every caller above it is unchanged.
    - When the legacy JSON store exists and the bundle does not, every reader and writer raises store-migration-pending; recall fails open on it as on any error (F-007).
    - write_store, under the lock, performs four steps in order:
      - It replaces each changed concept document through a temporary file and os.replace, skipping any document whose bytes are equal.
      - It removes L-*.md files with no record and any leftover temporary file.
      - It rewrites log.md.
      - It rewrites index.md last.
    - Every file is skipped when its bytes are equal; write_store returns whether any file was written or removed.
    - index.md and log.md are pure functions of the record set, so a write interrupted between files is repaired by the next write (A-003).
    - Bundle digest: the state_engine digest over the lines formed by each root .md name and the sha256 hex of its bytes, sorted by name. recall and the harvest outcome report store as memory/lessons and store_digest as this digest (S-026).
  - Reserved files (D-008).
    - index.md has a frontmatter of exactly okf_version "0.2", then a # Lessons heading and one list entry per lesson in fingerprint order.
    - Each entry links the title to the document's file name relative to the index, followed by a spaced hyphen and the description. Title and description are Markdown-escaped by a backslash before backslash and square brackets.
    - log.md has no frontmatter. It opens with a # Lesson Change Log title, then ## date headings, newest first. Each lesson has a Creation entry dated first_seen, falling back to last_seen, then to 1970-01-01.
    - Each history entry maps to an entry dated by its time: approve and annotate become Update, and retire becomes Deprecation.
    - Each entry is one list line: a bold action word, a link to the lesson document, the resulting status (draft, stable, deprecated), and the actor (knowledge-loop/1.0.0 for creation, the sanitised human actor otherwise). No rationale or free text is included.
    - Within a date, entries order by timestamp descending, then fingerprint, then history position descending. The entry count equals the lessons plus all history entries (AC-009).
  - stale_after rule (D-004). Present only when evidence_state is retained, with value last_seen (falling back to first_seen). A retained lesson's evidence has left the recorded runs, so it is stale from its last observed occurrence. A current lesson is re-derived at every harvest and carries no stale_after. Recall does not read the key (X-002). No migrated lesson carries it today (F-011).
  - Conformance and verifier (D-009).
    - okf conformance takes a bundle directory and returns bundle, result (pass, fail, or absent), documents, reserved, and findings. Each finding has path, rule, and detail, sorted by path then rule. The output holds no timestamp.
    - The check is recursive over .md files. Rules:
      - OKF-11.1: a non-reserved document has no parseable frontmatter.
      - OKF-11.2: a concept document has an empty or missing type.
      - OKF-11.3-index: the root index frontmatter holds anything other than okf_version; a non-root index carries frontmatter; or a body line is not a # heading, a list entry with a bracketed link, or blank, or the first non-blank line is not a heading.
      - OKF-11.3-log: the first non-blank line is not a # title, a ## heading is not a valid ISO date, dates are not strictly descending, or a list entry precedes the first date.
    - M-004 checks memory/lessons by default, or a given path, with an option for JSON output. It exits 0 on pass or absent, 1 on fail, and 2 when an explicitly given path does not exist.
  - Migration (D-005). A migrate subcommand of the knowledge command line holds the lock and proceeds in four steps:
    - It loads the JSON store with the existing reader and writes the full bundle through write_store.
    - It re-loads the bundle and compares it record for record with the JSON records (equal dictionaries, equal count, equal lesson_id set).
    - Only on equality does it remove the JSON store, then report counts.
    - On any mismatch, it leaves the JSON store and the written files in place and fails with migration-mismatch.
    - Re-running it after an interruption rewrites the bundle and repeats the comparison. Migration never runs implicitly, so an aggregation cannot migrate (F-027).
  - Exclusions (D-006).
    - omn_agent/source.py gains EXCLUDE_PATHS holding memory/lessons. _walk skips any file whose base-relative path equals or lies under an entry. lessons.store.* is retired, because every file it ever matched lies under that path (F-013).
    - optimize_memory denies any path whose segments contain memory followed directly by lessons (case-insensitive), with its own reason naming the lesson bundle. memory/index.md and every other memory document are unaffected (F-015).
  - Checklist (D-010). FR-13, advisory, owner omn-qa: the lesson bundle conforms to OKF v0.2 §11. Its Verification cell names M-004 in the same form as FR-11, so S5 resolves the script path (F-016) and F9 verdicts are unchanged (F-017).
  - Version (D-011). RUNTIME_VERSION 0.11.0 in M-005, set after the T-014 baseline exists.
  - Documentation (D-012). M-009 to M-012 and the knowledge.py module text describe the bundle, the reserved files, the write contract, the bundle digest, migration, and the verifier; runtime/README.md stays unchanged (A-008).
- Rationale: O-002 is the only top-scoring option (5.2). It keeps the §11 check free of lesson-loop code (C-022), confines the loop change to load_store, write_store, the lock path, and reported store names, and leaves every caller above the store boundary unchanged (C-007, C-026).
- Highest-scoring rejected alternative and why it lost: O-001 ties on hard constraints, impact surface, and reuse, but the verifier would import the loop module with its policy and state-engine dependencies, and the check could not be reused for another bundle without that module; it loses on criterion 4 (C-022).
- Tradeoffs accepted:
  - Recall reads every document at each hydrated dispatch instead of one file (C-023, A-005).
  - The parser accepts a subset of YAML, so a valid but non-subset document written by another tool is reported unparseable (D-007).
  - Documents can disagree with index.md and log.md after an interruption, until the next write (A-003).
  - The STORE_SCHEMA identifier survives as an in-memory interface name with no file carrying it.
  - Governance actions recorded after migration are lost on a revert unless re-applied (6, Schema or migration changes).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | New standard-library module M-001 and standalone verifier M-004; M-002 and M-004 depend on M-001 one-way (O-002) | yes | architecture-decision-record-D-001.md |
| D-002 | Bundle layout, file naming with identifier guard, lesson-to-frontmatter mapping, and the lesson_record extension key (O-002) | yes | architecture-decision-record-D-002.md |
| D-003 | Read and write contract: lock, four-step write order, whole-file replace, skip-equal, derived reserved files, bundle digest in recall and harvest outcome (O-002) | yes | architecture-decision-record-D-003.md |
| D-004 | stale_after only for retained lessons, valued last_seen (O-002) | yes | architecture-decision-record-D-004.md |
| D-005 | Explicit migrate subcommand with verify-before-delete; readers refuse a JSON-only state with store-migration-pending (O-002) | yes | architecture-decision-record-D-005.md |
| D-006 | Path-scoped exclusion in M-006 and M-007; lessons.store.* retired (O-002) | yes | architecture-decision-record-D-006.md |
| D-007 | Frontmatter serialisation subset and parser acceptance (O-002) | no | inline, 5.3 Serialisation subset |
| D-008 | index.md and log.md derivation and ordering (O-002) | no | inline, 5.3 Reserved files |
| D-009 | Conformance rules, output shape, and verifier exit contract (O-002) | no | inline, 5.3 Conformance and verifier |
| D-010 | Advisory checklist item FR-13 owned by omn-qa (O-002) | no | inline, 5.3 Checklist |
| D-011 | RUNTIME_VERSION 0.11.0 after the baseline (O-002) | no | inline, P-008 |
| D-012 | Documentation in M-009 to M-012; runtime/README.md unchanged (O-002) | no | inline, 5.3 Documentation |

## API and Data Model Impact

- API changes:
  - M-002 store constants: STORE_REL and LOCK_REL are replaced by BUNDLE_REL (memory/lessons) and a lock at memory/lessons/lessons.lock. Current shape: one JSON path. Target shape: a directory path. Compatibility approach: the only importer outside M-002 is M-013 (F-010), which changes in the same change (P-010). Coexistence period: none. Retirement condition: not applicable. Rollback position: a revert restores both constants.
  - M-002 load_store and write_store: signatures and the returned in-memory shape are unchanged; the storage behind them changes. New error classes are store-unwritable, store-migration-pending, and migration-mismatch; store-unreadable now names a document. Rollback position: a revert restores the JSON reader.
  - M-002 recall and memory_slice: store becomes memory/lessons and store_digest the bundle digest, for envelopes built after the change only. Current shape: the JSON path and file digest. Compatibility: neither field enters any payload digest, and render_section is unchanged (F-006, F-010). Coexistence period: permanent, since old envelopes are never rewritten (C-012). Retirement condition: none needed. Rollback position: a reverted runtime reports the JSON path again.
  - M-002 harvest outcome and knowledge-harvest.json: store and store_digest name the bundle for new records; existing records are unchanged. Rollback position as above.
  - M-002 command line: the migrate subcommand is added; report prints the bundle path; list, approve, retire, annotate, recall, and report are otherwise unchanged.
  - M-001 and M-004: new interfaces only (5.3).
- Contract compatibility notes: no context-slice member is edited (M-020), and no payload-digest component changes; existing envelopes, ledgers, and harvest records keep the JSON store name as historical evidence (C-012).
- Schema or migration changes:
  - M-003: the JSON document becomes a bundle of 43 or more concept documents plus two reserved files. The count is taken at T-025 (F-012).
  - Direction: forward, one time, JSON to bundle, by the migrate subcommand (D-005).
  - Reversibility: reversible until the JSON store is removed. After removal, reversal is a revert of the change set, which restores the tracked JSON file from history and removes the bundle; governance actions taken after migration are lost unless re-applied.
  - Reader and writer behaviour during transition: with only the JSON store present, every reader and writer refuses with store-migration-pending, harvest at aggregation records failed without failing aggregation (F-003), and recall fails open (F-007). With both present, the bundle is authoritative and migrate completes the removal. Installs never held a JSON store (F-013), so they start with no store.
  - Retirement condition for the store-migration-pending branch: once no checkout carrying a JSON-only store remains, a later change may remove the branch.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Frontmatter writing | standard library; existing runtime modules | none-found | Searched existing components (no YAML writer in runtime/*.py), the standard library (no YAML module), the platform (none), installed dependencies (a YAML package exists but is excluded by C-016) |
| Frontmatter parsing | installed YAML dependency used by execution_metrics.py | rejected | C-016 forbids a third-party dependency for this path; O-005 |
| Atomic whole-file write with skip-equal | write_store temporary file and os.replace (F-001) | reuse-extended | Same pattern applied per bundle file |
| Exclusive writer lock | StoreLock (F-003) | reuse-extended | New lock path, same semantics and error class |
| Title and description text | neutralise and the render_section caps (F-006) | reuse-as-is | Gives byte-equal text to the dispatch rendering (C-007) |
| Bundle digest | state_engine digest helper and bytes_digest (F-001, F-009) | reuse-as-is | Same digest form as other run evidence |
| Lesson model, harvest, governance, eligibility, recall, effectiveness | runtime/knowledge.py (F-004, F-005, F-008) | reuse-as-is | Unchanged above the store boundary (C-026) |
| Payload and mirror exclusion | _walk in omn_agent/source.py (F-013) | reuse-extended | One path rule beside the name patterns; installer, sync, and bundle test inherit it |
| Optimiser exclusion | _denied in runtime/optimize_memory.py (F-015) | reuse-extended | One segment-pair rule beside the segment and name rules |
| Release-checklist execution | release-checklist mode of verify_self_hosting.py (F-016) | reuse-as-is | Runs a new command item without change |
| Command-line parsing | standard library argparse | reuse-as-is | Same as every runtime script |
| Index and change-log rendering | memory documents (hand-written); runtime/*.py | none-found | Searched existing components (no Markdown index writer), the standard library and platform (none), installed dependencies (none) |
| Bundle conformance check | runtime artifact validators | rejected | Bound to framework artifact contracts and the Validation Engine; C-015 forbids changing them, and C-010 needs a standalone check |
| Store migration | FC-022 seed procedure (operator-run harvest) | rejected | It builds a store from run evidence and cannot carry governance history; C-011 needs a record-for-record copy |
| Interruption-safe recovery | derived-file regeneration on every write | reuse-extended | The skip-equal write already rewrites any file whose content differs |

## Operational Considerations

- Logging and observability updates:
  - The migrate subcommand prints lesson count, documents written, and the JSON removal (M-002, C-011).
  - knowledge-harvest.json for new aggregations names the bundle and its digest (M-002, S-026).
  - M-004 prints a pass, fail, or absent verdict with sorted findings, or JSON on request (M-004, C-010).
  - FR-13 results are recorded in change proposals as advisory (M-008, C-018).
- Error handling strategy:
  - store-unreadable names the failing document, and the read stops (M-002).
  - store-unwritable is raised for an invalid lesson_id or an unsupported value type before any file is replaced (M-002, A-006).
  - store-migration-pending is raised for a JSON-only state (D-005).
  - migration-mismatch leaves both forms in place (D-005).
  - lock-contention is unchanged (F-003).
  - The aggregation step and recall keep their fail-safe behaviour (F-003, F-007).
  - The verifier separates a missing explicit path (exit 2) from a non-conforming bundle (exit 1) (M-004).
- Security considerations:
  - Every string is quoted and escaped to ASCII on one line, so no field value can open a frontmatter delimiter, add a key, or break a list (C-017, D-007).
  - Index entries are Markdown-escaped. Log entries carry no free text, only identifiers, fixed words, mapped statuses, and sanitised actors (D-008).
  - The lesson_id guard keeps file names inside the bundle (C-017, R-016).
  - Rationale text stays only inside lesson_record, never in the index or log.
  - The bundle never ships (C-013).
  - No secret, credential, network, or model path is introduced (C-016).
- Performance considerations:
  - Recall and harvest parse one document per lesson instead of one JSON file, linear in lesson count (C-023, A-005). Elapsed time is already recorded in knowledge-harvest.json, so growth is visible (F-003).
  - Writes touch only changed files (D-003).
  - The bundle digest hashes each document once per recall (M-002).
- Deployment and operability impact:
  - Installs receive M-001, M-002, and M-004 through the managed payload and create their own bundle on first harvest (M-006, C-013).
  - The mirror is refreshed by the sync step after the last framework edit (M-014, C-020).
  - Operators of other checkouts run migrate once after pulling the change; until then recall withholds lessons and names the class (D-005, R-012).

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The OKF verdicts, reserved-file, frontmatter, stale_after, write, carrier, migration, and exclusion contracts in this package and its records are accepted at the Design Gate | M-001, M-002, M-003, M-006, M-007 | none | Contract definition precedes every producer and consumer (S-033) | T-001, T-002, T-006, T-009, T-017, T-019, T-024, T-030, T-034 |
| P-002 | The stale_after acceptance criterion is recorded and every scope criterion is mapped to a verification method | M-003 | P-001 | Verification methods consume the accepted contracts and the criterion | T-010, T-004 |
| P-003 | The reference baseline is captured read-only on the unchanged tree: render bytes, loop outputs, verifier verdicts, run evidence hashes, and a copy of the store | M-002, M-003, M-005 | P-001 | The reference must exist before any code it judges changes (S-033) | T-014 |
| P-004 | The path-scoped exclusions exist in M-006 and M-007 before any bundle file exists in the authoritative tree | M-006, M-007 | P-001 | A sync or optimiser run after a bundle exists would mirror or rewrite it | T-031, T-035 |
| P-005 | M-001 serialiser, parser, and conformance exist | M-001 | P-001 | M-002 and M-004 consume M-001 | T-007, T-021 |
| P-006 | M-002 bundle read and write, index, change log, lock path, and bundle naming in recall and harvest exist | M-002 | P-003, P-005 | The store producer precedes migration and its readers; the baseline precedes any M-002 edit | T-008, T-003, T-011, T-012 |
| P-007 | M-004 verifier and the FR-13 advisory item exist | M-004, M-008 | P-005 | S5 needs the script path to exist before the item names it | T-020, T-022 |
| P-008 | RUNTIME_VERSION reads 0.11.0 | M-005 | P-003 | The baseline must carry the pre-increment stamp | T-012 |
| P-009 | The live store is migrated into the bundle and the migration is verified complete against the P-003 copy, with the JSON store still present | M-002, M-003 | P-003, P-004, P-006 | The verification is the reversibility safeguard that must precede removal (C-011) | T-025, T-027 |
| P-010 | The JSON store is removed, and the test suite is moved to the bundle, in the same change as P-009 | M-003, M-013 | P-009 | The suite names the store until it changes (F-018); removal is irreversible without a revert (S-033) | T-026, T-013 |
| P-011 | The documents describe the delivered bundle, reserved files, write contract, digest, migration, and verifier | M-009, M-010, M-011, M-012 | P-006, P-010 | Documentation describes delivered contracts | T-036 |
| P-012 | The mirror is refreshed by the sync step after the last framework edit | M-014 | P-004, P-007, P-008, P-010, P-011 | The mirror must match the final tree (C-020) | T-032 |
| P-013 | Verification on the final tree against the P-003 baseline: bundle content, loop parity, interruption, conformance verdicts, protected surfaces, distribution, documentation, and review | M-001 to M-015, M-019 | P-002, P-012 | Verification of a boundary precedes reliance on it | T-005, T-015, T-016, T-018, T-023, T-029, T-033, T-037 |
| P-014 | The release note, change proposal, and release checklist cite the P-013 evidence | M-008, M-014 | P-013 | They record evidence only P-013 produces | T-028, T-038, T-039 |

### Test Strategy Focus Areas

- Carrier: tests/test_knowledge.py (M-013). Every test builds a temporary framework root. The copy-ignore becomes a callable that skips memory/lessons by relative path and keeps every other memory file, used by the tree builder and the runtime installer. KNOWLEDGE_CHANGE_SET and REFERENCE_COMMIT are not edited (F-019).
- Existing tests moved to the bundle:
  - The store helper writes through write_store.
  - Idempotency expects the file set index.md, log.md, and one L-*.md per lesson.
  - The governance byte comparison filters lessons.lock.
  - The optimiser test expects the bundle-path denial reason for index.md, log.md, and a concept document.
  - Dispatch expects store memory/lessons and the bundle path absent from context_slice.
  - The unreadable-store fixture is a concept document with broken frontmatter, and recall fails open naming store-unreadable.
  - Aggregation absence checks expect no bundle directory.
  - Payload exclusion places bundle files and a memory/index.md in a temporary memory tree, expects only memory/index.md in the seeds, and expects EXCLUDE_PATHS to name memory/lessons.
  - The documentation test names the bundle and no JSON store.
  - The version test expects 0.11.0.
  - The module boundary test expects knowledge to import only the standard library, state_engine, and okf, and okf and the verifier to import only the standard library and okf.
- Serialiser: round-trip identity for every live record shape (F-011). Hostile fixtures cover newlines, a line of three dashes, a colon followed by a space, a leading hash, square brackets, double and single quotes, backslashes, tabs, non-ASCII and astral characters, strings that look like integers or null, and empty lists and mappings. Pass when the parsed value equals the input, the key set is unchanged, and output bytes are equal across two dumps.
- AC-001, AC-016, AC-017, AC-018: migrate a copy of the P-003 store. Pass when the document count equals the record count at migration, lesson_id sets match, every record re-loads equal including history entry count and actors, and the JSON store is absent. A forced mismatch must leave the JSON store present.
- AC-002, AC-003, AC-005 to AC-008, AC-023: field checks over every document against its record. AC-004 compares each resources set, with the two parent steps removed, against the distinct evidence paths before the fragment (S-028, Q-001).
- AC-009: count of log entries equals lessons plus history entries; dates strictly descending; a fixture with approve, annotate, and retire entries on two dates.
- AC-010, AC-011, AC-015: compare loop outputs and render bytes with the P-003 baseline over the same lesson set (A-007); conformance twice gives equal output and exit status.
- AC-012: two harvests over unchanged evidence; every bundle file hash equal, log.md included.
- AC-013: fault injection after each write step (each document replace, the removal, log.md, index.md). Pass when every file parses, is either its prior or its new version, and the next write restores index and log agreement.
- AC-014: the migrated bundle passes; seeded bundles with unparseable frontmatter, an empty type, and a malformed index or log each fail with the expected rule.
- AC-019 to AC-022: hash comparison of run directories other than the carrying run (A-009); payload and mirror listings under memory/lessons are empty; an optimiser run leaves every bundle hash unchanged; verifiers return their baseline verdicts with the version string excluded (S-032).
- AC-024: text search of M-009 to M-012.
- Beyond the criteria: a lesson_id outside the guard fails with store-unwritable and nothing written; a JSON-only fixture yields store-migration-pending for harvest and governance and a fail-open recall; M-004 exits 2 for a missing explicit path; FR-13 is reported advisory and S10 is unchanged.

### Rollout and Rollback

- Rollout: the change lands as one change carrying P-009 and P-010 (S-033). This repository's store is migrated by the migrate subcommand within it. Other checkouts run migrate once after pulling. Installs start with no store and create a bundle on first harvest.
- Rollback: revert the change set. The tracked JSON store returns from history, and the bundle files, M-001, M-004, and FR-13 leave with the revert. Envelopes and harvest records written after the change keep the bundle name as historical evidence. Governance actions recorded in the bundle after migration must be re-applied.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | security | A field value carrying delimiter-like lines, key-like text, link syntax, or control characters reaches a bundle file | A document gains or loses keys, the index or log breaks, or altered text reaches dispatch | medium | M-001, M-002, D-007, D-008 | Quote-and-escape-everything subset, Markdown escaping, free-text-free log; hostile fixtures in P-005 and P-013 | omn-dev-2-reviewer |
| R-002 | contract | A value does not round-trip through the subset (escape, integer-looking string, empty collection) | Fields are lost (S-005) or rendered text changes (S-008) | medium | M-001, D-002, D-007 | Round-trip identity tests over every live record shape in P-005 and P-013 | omn-dev-1-implement |
| R-003 | migration | Migration drops or alters a field or history entry | Governance history is lost; AC-016 to AC-018 fail | low | M-002, M-003, D-005, P-009 | Verify-before-delete inside migrate; the P-003 copy; P-010 only after P-009 | omn-qa |
| R-004 | delivery | A knowledge-loop aggregation runs between T-014 and T-027 (A-007 false) | Same-set comparisons lose their reference; the count moves again (F-012) | medium | M-003, P-003, P-009 | Comparisons use the P-003 copy in a temporary tree; the migration count is taken at T-025; omn-tech-lead holds complete and gate commands until T-027 | omn-tech-lead |
| R-005 | operability | An interruption leaves documents updated but index or log stale, and S-010 is ruled to need cross-file agreement (A-003 false) | AC-013 fails as reinterpreted | low | M-002, D-003, P-006 | Next write regenerates both; if ruled otherwise, a staged directory swap under a new record | omn-business-analyst |
| R-006 | performance | Lesson count grows so per-dispatch parsing of every document becomes noticeable (A-005 false) | Dispatch latency grows | low | M-002, D-003 | Elapsed time recorded per harvest; an index-only fast path by a later change request | omn-tech-lead |
| R-007 | operability | The path rule misses a bundle file or another path enumerates memory (A-001 false), or the optimiser rule over-matches | Bundle files ship or are rewritten, or unrelated memory files leave scope | low | M-006, M-007, D-006, P-004 | Fixtures with memory/index.md and memory/log.md outside the bundle; parity test over the mirror in P-013 | omn-dev-2-reviewer |
| R-008 | contract | A consumer resolves the relative sources resource differently (A-004 false) | Sources point nowhere for that consumer; AC-004's comparison changes | low | D-002 | §6.2 allows relative paths and §6.1 requires tolerance of broken links; Q-001 settles the comparison | architect |
| R-009 | delivery | Suites or the frozen comparison set still name the JSON store when it is removed | Suite failures between T-026 and T-013 | medium | M-013, P-010 | T-026 and T-013 land in one change; KNOWLEDGE_CHANGE_SET stays frozen, and its store entry needs no file because the set is never checked for existence (F-019) | omn-dev-1-implement |
| R-010 | delivery | A framework file changes after the mirror refresh | The mirror drifts; P-013 evidence is stale | low | M-014, P-012 | P-012 last among edits; parity test rerun in P-013 | omn-dev-1-implement |
| R-011 | contract | A record holds a float or another unsupported type (A-006 false) | A write fails with store-unwritable | low | M-001, D-007 | Type refusal before any replace; fixture in P-005 | omn-dev-1-implement |
| R-012 | operability | Another checkout pulls the change with a JSON-only store | Recall withholds lessons there until migrate runs | medium | M-002, D-005 | Fail-open reason names store-migration-pending; M-009 to M-012 describe the one-time step (P-011) | omn-documentation |
| R-013 | delivery | FR-08 inspection requires runtime/README.md to list the verifier (A-008 false) | A context-slice member is edited, and an active item re-dispatched after it raises a context-integrity failure | low | M-020, D-012 | Q-004 settles it before P-011; if required, edit only when no work item is active | omn-documentation |
| R-014 | delivery | New runtime files fall outside the package-data globs (A-002 false) | Declared-globs test fails; installs lack M-001 | low | M-001, M-004, M-014 | The bundled-payload test in P-013 detects it | omn-dev-1-implement |
| R-015 | contract | A third-party reading of §11 rule 2 or of the §9 entry form differs from this design | The bundle is judged non-conforming elsewhere | low | D-009 | Q-003 records the interpretation; the writer emits the bold convention anyway | omn-tech-lead |
| R-016 | security | A crafted lesson_id forms a file name outside the bundle | A write lands outside memory/lessons | low | M-002, D-002, P-006 | Identifier guard before any path is formed; fixture in P-013 | omn-dev-2-reviewer |
| R-017 | delivery | AC-019 is read as including the carrying run (A-009 false) | AC-019 cannot pass | low | P-013 | Q-006 notes the scope; T-029 records the excluded directory | omn-qa |

## Estimate and Confidence

- Overall: L (confidence: low). It is a cross-boundary change over the lesson loop, a new module and verifier, the installer, the optimiser, documents, tests, and a one-time data migration with two contract-change modules. Confidence is low because P-009 rests on A-007 and the write contract on A-003.
- Breakdown: P-001 S (high, delivered by this package); P-002 S (medium); P-003 S (medium, A-007); P-004 S (high); P-005 M (medium, A-006); P-006 M (medium, A-003); P-007 S (high); P-008 XS (high); P-009 S (low, A-007); P-010 M (medium); P-011 S (medium, A-008); P-012 XS (high); P-013 M (medium); P-014 S (medium).
- Scope assumptions:
  - The Scope Gate and Planning Gate rulings stand as relayed (S-022 to S-033).
  - Q-001 to Q-006 resolve as their default consequence states.
  - A-001 to A-009 hold.
  - No other lesson-store consumer exists beyond those in F-010.
- Uncertainty drivers: lesson-set movement during delivery (A-007), the interruption reading (A-003), hostile-content coverage of the serialiser (R-001, R-002), and suite rework (R-009).

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Is AC-004 compared after removing the two parent-directory steps from each resource as well as the fragment from each evidence reference? | no | omn-business-analyst | D-002, P-002 | Yes (design): comparison as in the test focus. No: resources carry the bare framework-relative path, and A-004 and R-008 change |
| Q-002 | Record the acceptance criterion for the stale_after rule of D-004 (T-010) | no | omn-product-owner | D-004, P-002 | Accepted: AC for retained-only presence valued last_seen. Changed: D-004 is revised before P-006 |
| Q-003 | Accept the §11 rule 2 reading (concept documents only) and the §9 reading (bold action word emitted, not enforced) | no | omn-tech-lead | D-009, P-005 | Accepted: as designed. Rejected: the check enforces the bold word, or the root index carries a type key and AC-002's one-key criterion conflicts |
| Q-004 | Does FR-08 require runtime/README.md to list the verifier and module (A-008)? | no | omn-documentation | D-012, P-011 | No (design): unchanged. Yes: one table row, edited while no work item is active (R-013) |
| Q-005 | Accept the records for D-001 to D-006, emitted at Proposed; implementation waits on them | no | omn-tech-lead | D-001, D-002, D-003, D-004, D-005, D-006 | Accepted: P-002 onward may start. Rejected: the affected steps are redesigned first |
| Q-006 | AC-016 names 42 lessons and the store now holds 43 (F-012); is the count at migration time the reference, and does AC-019 exclude the carrying run (A-009)? | no | omn-product-owner | P-009, P-013 | Yes (design): counts and hashes as in the test focus. No: AC-016 and AC-019 are reworded before P-013 |

## Sign-off

- Architect: unsigned; producer of this package, excluded from deciding the Design Gate
- Tech Lead (accepting owner of the Design Gate under the Producer Exclusion Rule; co-owner omn-architect): unsigned
- QA (test strategy focus areas, input to T-004): unsigned
- Product Owner (Q-002 and Q-006 only): unsigned
