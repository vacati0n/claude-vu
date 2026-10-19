```yaml
plan:
  planId: PLAN-79276e78d773-okf-lesson-bundle
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/okf-lessons-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:68967bc015098f6c332ca509f1a73b76
  contextDigest: sha256:d78ae7219c9213d6226b6f0ad2b306d4
```

## Executive Summary

This plan moves the framework's harvested lessons from one framework-private JSON document into an OKF v0.2 bundle under the lesson memory location, for the operators who review and govern lessons, the agents that receive lessons at dispatch, and tools outside the runtime. Success means a deterministic standalone check judges the bundle conformant and every lesson states its origin and trust. The knowledge loop, the dispatched lesson text and every existing verdict must also stay as they were (BO-1 to BO-5). The work is 39 tasks in 13 execution waves: twelve design and decision tasks, sixteen implementation-phase tasks, eight review and verification tasks, and three closure tasks. The highest-impact risk is R-008: lesson field content could alter the structure of a frontmatter block, the root index or the change log, which would defeat the existing neutralisation of dispatched text. The plan status is complete. The five blocking scope questions were settled at the Scope Gate, and the two remaining questions, Q-001 and Q-002, are non-blocking and close during design.

## Business Objectives

- BO-1: Operators and tools outside the runtime can read, browse and review every lesson as an open-format document. Measured by the conformance check passing the bundle and by the root index linking every lesson document (S-001, S-002, S-011, S-017).
- BO-2: Each lesson states where it came from and how far it can be trusted. Measured by every lesson document carrying sources, generated and status, and carrying verified exactly where an operator approved it (S-003, S-004).
- BO-3: The knowledge loop keeps its governance and behaviour with no loss. Measured by loop-step parity, byte-identical dispatched lesson text, idempotent re-harvest, interruption safety and complete migration of identifiers, fields and history (S-005, S-006, S-007, S-008, S-009, S-010, S-012).
- BO-4: The change weakens no framework protection or distribution boundary. Measured by unchanged run evidence, unchanged baseline verdicts, an optimiser that leaves the bundle alone, and a bundle that is absent from the payload and the mirror (S-013, S-014, S-015, S-016).
- BO-5: Operators find current documentation of the lesson store. Measured by the memory documents naming the bundle as the lesson store (S-018).

## Technical Objectives

- TO-1: Bundle files conform to OKF v0.2 §11, as decided by a deterministic check that runs standalone. Traces to BO-1. Verified by T-023.
- TO-2: Frontmatter serialisation uses the standard library only, is byte-stable for equal input, and round-trips every lesson field value exactly. Traces to BO-2 and BO-3. Verified by T-005 and T-015.
- TO-3: Every bundle file write leaves that file complete under interruption, and is skipped when its bytes are unchanged. Traces to BO-3. Verified by T-018 and T-015.
- TO-4: Every date and generated value in the bundle derives from lesson record fields, never from write time. Traces to BO-3. Verified by T-015.
- TO-5: No lesson field value can alter the structure of a lesson document, the root index or the change log. Traces to BO-2 and BO-3. Verified by T-016 and T-005.
- TO-6: The bundle path is excluded from the installed payload, the bundled mirror and the memory optimiser, and no other path is newly excluded. Traces to BO-4. Verified by T-029 and T-033.

## Scope

Notation: S-001 to S-018 are the In Scope items of scope-definition (sha256:81bea5e4244406eb46c1b8bcf2b47c2a), adopted unchanged as this plan's statements. AC-nnn names that artifact's acceptance criterion nnn. SQ-nnn names its open question nnn. D-nnn and X-nnn are its decisions and exclusions. "Scope Gate ruling" cites the approved Scope Gate decision recorded in the run state. Surfaces come from the change request (sha256:8421834b6a46a2a11175f90e398440c1) and the architecture context (sha256:8859dd1736058635fdf5470ac277b2dc). The task context names no repository files, so no repository rescan was performed.

### In Scope

- S-001: Lessons are held as a bundle with one document per lesson, a root index declaring the OKF version, and a change log. Covered by T-001, T-002, T-003, T-004, T-005.
- S-002: Each lesson document states a non-empty type, title, description and tags. Covered by T-004, T-005, T-006, T-007, T-008.
- S-003: Each lesson document states its source run artifacts, and the producer that generated it and when. Covered by T-004, T-005, T-006, T-007, T-008.
- S-004: Each lesson document states its operator approval and its status as draft, stable or deprecated. Covered by T-004, T-005, T-006, T-007, T-008, T-009, T-010.
- S-005: Every other lesson field, governance history included, stays readable under its own key. Covered by T-004, T-005, T-006, T-007, T-008.
- S-006: The change log records each creation and each governance change, newest first. Covered by T-002, T-004, T-005, T-011.
- S-007: Harvest, approve, retire, annotate, recall, effectiveness reporting and the aggregation step work on the bundle with the same results as before. Covered by T-004, T-008, T-012, T-013, T-014, T-015.
- S-008: Agents receive each lesson at dispatch with exactly the same text as before. Covered by T-004, T-014, T-015, T-016.
- S-009: Re-harvesting unchanged evidence leaves the bundle unchanged. Covered by T-004, T-013, T-015, T-017.
- S-010: An interrupted write never leaves a lesson document, the index or the change log partly written. Covered by T-004, T-017, T-018.
- S-011: An operator can run a deterministic standalone OKF §11 check that reports pass or fail. Covered by T-001, T-004, T-007, T-013, T-019, T-020, T-021, T-022, T-023.
- S-012: The current lessons become documents with identifiers and history intact, and the JSON store is removed. Covered by T-004, T-005, T-013, T-024, T-025, T-026, T-027, T-028.
- S-013: Every existing run evidence file stays unchanged. Covered by T-004, T-012, T-014, T-029.
- S-014: The bundle is absent from the installed payload and the bundled mirror. Covered by T-004, T-030, T-031, T-032, T-033.
- S-015: The memory optimiser leaves the bundle unchanged. Covered by T-004, T-029, T-034, T-035.
- S-016: Every existing gate, artifact validator and verifier keeps its recorded baseline verdict. Covered by T-004, T-014, T-016, T-029.
- S-017: An operator can browse from the root index to every lesson document. Covered by T-002, T-003, T-004, T-005.
- S-018: The memory documentation describes the bundle in place of the JSON store. Covered by T-004, T-028, T-036, T-037.

### Out of Scope

- X-001: Publishing the bundle outside the repository. Excluded because the business intent states it as a non-goal.
- X-002: Changing harvest eligibility, timing or ranking. Excluded because the business intent states it as a non-goal.
- X-003: Converting any other memory document to OKF. Excluded because the business intent states it as a non-goal.
- X-004: Any process or machine actor that marks a lesson verified. Excluded because the inputs name no confirming process (D-001).
- X-005: A mandatory release checklist item for the conformance check. Excluded because a new mandatory item would invalidate every recorded change proposal under rule F9.
- X-006: Changing governance states, their meanings or the governance actions. Excluded because the request maps the three existing states and keeps the actions.
- X-007: Changing Phase Model tables, agent module text, gates or artifact validators. Excluded because the change request lists them as not touched.

### Deferred

- Agreement of the root index, the change log and the lesson documents with each other after an interruption between files. This comes into scope if omn-business-analyst refutes A-004 (R-002).
- Tuning recall read cost beyond present behaviour. This comes into scope if T-016 finds that dispatch latency grows with lesson count (R-010).

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The statement of OKF v0.2 §5, §7, §8, §9 and §11 in the feature request and the architecture context matches the SPEC text | S-001, S-011 | The contracts in T-002 and T-006 and the check in T-021 change, and scope criteria may change (R-001) | architect |
| A-002 | Reference outputs captured on the unchanged tree are accepted as the recorded baselines for S-007, S-008, S-013 and S-016 | S-016 | T-014 is redefined, and T-015 and T-029 compare against a different reference (R-007) | omn-qa |
| A-003 | No harvest or governance action changes the lesson set between baseline capture in T-014 and migration in T-025 | S-008, S-012 | Same-lesson-set comparisons for AC-010 and AC-011 become invalid, and T-014 must be repeated (R-007) | omn-tech-lead |
| A-004 | S-010 requires each file to be complete on its own. It does not require the root index, the change log and the lesson documents to agree with each other after an interruption | S-010 | T-017 must provide cross-file agreement, T-018 adds a cross-file check, and T-003, T-008 and T-011 grow (R-002) | omn-business-analyst |
| A-005 | The change is a framework-internal capability addition governed by the self-hosting profile, so it carries a framework change proposal and the framework release checklist | plan-wide | T-038 and T-039 are removed (R-013) | omn-tech-lead |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | T-001 finds the SPEC text differs from the request's statement of §5, §7, §8, §9 or §11 (A-001 false) | The contracts in T-002 and T-006 and the check in T-021 change; scope criteria may change | low | T-001, T-002, T-006, T-021 | T-001 confirms the rules before any contract closes; tracked as Q-001 | architect |
| R-002 | requirement | S-010 is ruled to require cross-file agreement after an interruption (A-004 false) | T-017 and T-018 widen; T-003, T-008 and T-011 grow in complexity | medium | T-003, T-008, T-011, T-017, T-018 | omn-business-analyst confirms A-004 before T-017 closes | omn-business-analyst |
| R-003 | technical | A field value with multi-line text, quoting or delimiter-like lines does not round-trip through the standard-library frontmatter writer and parser | Field loss breaks S-005; changed text breaks S-008 | medium | T-006, T-007, T-008 | T-004 sets round-trip fixtures over every migrated record; T-005 and T-015 verify | architect |
| R-004 | technical | A bundle date or generated value derives from write time instead of record fields | Re-harvest changes bytes and AC-012 fails | medium | T-002, T-006, T-011, T-024 | T-002, T-006 and T-024 bind every date to record fields; T-015 verifies | architect |
| R-005 | technical | Migration drops or alters a field or history entry, including for lessons with empty history | Governance history is lost and S-005 and S-012 fail | medium | T-024, T-025, T-026, T-027 | T-026 removes the JSON store only after T-027 records complete migration | architect |
| R-006 | dependency | The OKF v0.2 SPEC text is not supplied before T-001 closes | Q-001 stays open and R-001 carries into build | medium | T-001 | The operator supplies the SPEC text per 8.2; otherwise the Design Gate records the residual risk | architect |
| R-007 | dependency | The baseline cannot be taken on the unchanged tree, or the lesson set changes between T-014 and T-025 (A-002 or A-003 false) | S-007, S-008 and S-016 comparisons lose their reference | low | T-014, T-015, T-025, T-027, T-029 | T-014 precedes T-025 in 8.1; omn-tech-lead holds lesson-set changes until T-025 completes | omn-qa |
| R-008 | security | Lesson field content harvested from run evidence contains frontmatter delimiters, key-like lines or link syntax | A document gains or loses keys, the index or change log breaks, or altered text reaches dispatch past the existing neutralisation | medium | T-003, T-006, T-007, T-008, T-011, T-016 | T-006 sets a structural safety rule for every field; T-004 adds hostile-content fixtures; T-016 reviews | architect |
| R-009 | operational | An exclusion rule matches generic names such as index.md or log.md outside the bundle, or misses a bundle file | Unrelated memory files leave the payload, or bundle files ship or are rewritten | medium | T-030, T-031, T-034, T-035 | T-030 and T-034 define rules scoped to the bundle path; T-029 and T-033 verify | architect |
| R-010 | operational | Recall at dispatch reads one document per lesson instead of one store document | Dispatch latency grows with lesson count | low | T-008, T-016 | T-016 reviews read cost; any tuning is deferred per Scope | architect |
| R-011 | delivery | Existing automated suites and backward-compatibility comparisons reference the JSON store name and its exclusion pattern | Suite failures after T-026 until T-013 lands | high | T-013, T-026 | T-013 depends on T-026 and updates the suite in the same change | omn-dev-1-implement |
| R-012 | delivery | A framework file changes after T-032 refreshes the mirror | The mirror drifts from the tree and T-033 evidence becomes stale | medium | T-032, T-033 | T-032 depends on every framework-editing task through 8.1 | omn-dev-1-implement |
| R-013 | delivery | The change is not governed by the self-hosting profile (A-005 false) | T-038 and T-039 are removed | low | T-038, T-039 | omn-tech-lead confirms the change class at the Planning Gate | omn-tech-lead |

The task context lists three affected areas: database (R-005), performance (R-010) and security (R-008).

## Task Breakdown

### T-001 Confirm the OKF v0.2 rules the bundle binds to

- Owner: architect
- Complexity: S (confidence: low)
- Depends on: none (external prerequisite in 8.2)
- Traces to: S-001, S-011, A-001
- Status: assumption-dependent (A-001; closes Q-001)
- Description: The technical design records whether the statement in the feature request and the architecture context holds for SPEC §5 (including §5.3 and §5.4, per the Scope Gate ruling), §7, §8, §9 and §11, and lists each difference.
- Acceptance Criteria:
  - The design gives each of §5.1 to §5.5, §7, §8, §9 and §11 a verdict of confirmed or differs
  - Q-001 is closed, or the Design Gate records its residual risk
- Gate: Design Gate

### T-002 Define the reserved-file contract for the root index and the change log

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: T-001
- Traces to: S-001, S-006, S-017
- Status: ready
- Description: The design fixes the root index frontmatter and link layout. It also fixes the change log title, date grouping and entry forms, maps entry types to governance actions per D-003, and takes every date from record fields.
- Acceptance Criteria:
  - The index contract allows exactly one frontmatter key, `okf_version`, valued "0.2", and one link with a description per lesson document under a # heading
  - The change log contract maps creation, approve, annotate and retire to Creation, Update and Deprecation entries, and dates a lesson with empty history from `first_seen`, never from write time (Scope Gate ruling)
- Gate: Design Gate

### T-003 Produce the root index of the bundle

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-002, T-007, T-017
- Traces to: S-001, S-017
- Status: ready
- Description: Every bundle write leaves a root index that conforms to the T-002 contract and links every lesson document present.
- Acceptance Criteria:
  - The root index frontmatter holds only `okf_version` with value "0.2"
  - The index links each lesson document exactly once with its description, with zero missing or duplicate links
  - Writing the index over an unchanged lesson set leaves its bytes unchanged
- Gate: Review Gate

### T-004 Map every scope acceptance criterion to a verification method and evidence record

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-002, T-006, T-010, T-017, T-019
- Traces to: S-001, S-002, S-003, S-004, S-005, S-006, S-007, S-008, S-009, S-010, S-011, S-012, S-013, S-014, S-015, S-016, S-017, S-018
- Status: ready
- Description: A verification approach exists that names, for AC-001 to AC-024 and the stale_after criterion from T-010, the check, the fixture or seeded defect it needs, and the evidence it records.
- Acceptance Criteria:
  - Each of AC-001 to AC-024, plus the T-010 criterion, maps to exactly one of T-005, T-015, T-018, T-023, T-027, T-029, T-033 and T-037
  - The approach names three seeded defect bundles for AC-014, the write steps that receive an injected interruption for AC-013, and hostile field-content fixtures for R-008
  - The approach includes a check of the `generated.at` and `generated.by` values (Scope Gate carry-forward on AC-005)
- Gate: Design Gate

### T-005 Verify the bundle content against its contracts

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-003, T-004, T-008, T-011, T-026
- Traces to: S-001, S-002, S-003, S-004, S-005, S-006, S-012, S-017
- Status: ready
- Description: Recorded evidence shows that the final bundle meets AC-001 to AC-009, AC-018, AC-023 and the T-010 stale_after criterion.
- Acceptance Criteria:
  - The evidence records zero exceptions for AC-001 to AC-009 and AC-023 on the final bundle
  - AC-004 is compared on the artifact path without its event suffix (Scope Gate carry-forward)
  - The JSON lesson store is absent (AC-018), and the T-010 criterion holds for every lesson
- Gate: Verification Gate

### T-006 Define the lesson document frontmatter contract

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-001, T-009
- Traces to: S-002, S-003, S-004, S-005
- Status: ready
- Description: The design maps every lesson record field to a standard OKF key or a producer extension key. It also fixes the text rules for type, title, description and tags, using existing record fields only (Scope Gate ruling on SQ-001).
- Acceptance Criteria:
  - Every lesson record field maps to exactly one frontmatter key, with sources per D-002, verified per D-001, and status mapped from candidate, active and retired to draft, stable and deprecated
  - `generated.by` uses the producer/version actor form and `generated.at` takes `last_seen` (Scope Gate ruling on SQ-002)
  - The description is neutralised the same way the rendered lesson section neutralises it, and every field value has a stated rule that keeps it from altering frontmatter structure (R-008)
- Gate: Design Gate

### T-007 Provide deterministic frontmatter serialisation and parsing

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-006
- Traces to: S-002, S-003, S-004, S-005, S-011
- Status: ready
- Description: Lesson frontmatter is written and read using the standard library only. Equal field values always produce equal bytes, and reading what was written returns the same values.
- Acceptance Criteria:
  - Writing and then reading the frontmatter of every migrated lesson returns field values identical to the record
  - Two writes of the same record produce identical bytes
  - The change adds no third-party dependency
- Gate: Review Gate

### T-008 Hold each lesson as a concept document that the lesson loop reads and writes

- Owner: omn-dev-1-implement
- Complexity: L (confidence: medium)
- Depends on: T-006, T-007, T-017
- Traces to: S-002, S-003, S-004, S-005, S-007
- Status: ready
- Description: Harvest, approve, retire, annotate, recall, effectiveness reporting and the aggregation step read and write lesson records through per-lesson concept documents that follow the T-006 contract.
- Acceptance Criteria:
  - Each loop step runs on the bundle without using the JSON store
  - Every concept document written carries the frontmatter keys the T-006 contract requires
  - Running a step again over unchanged lessons leaves every document's bytes unchanged
- Gate: Review Gate

### T-009 Decide the stale_after rule from lesson record fields

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: T-001
- Traces to: S-004
- Status: ready
- Description: The design states which lessons carry stale_after and the instant it holds. The rule derives from record fields only, with no wall clock. A ruling that the rule applies to no lesson must carry its justification (Scope Gate ruling on SQ-003).
- Acceptance Criteria:
  - The rule names its input fields and yields the same value on every write of an unchanged record
  - The design records the rule, or the justified ruling that it applies to no lesson
- Gate: Design Gate

### T-010 Record the acceptance criterion for the stale_after rule

- Owner: omn-product-owner
- Complexity: XS (confidence: high)
- Depends on: T-009
- Traces to: S-004
- Status: ready
- Description: The scope acceptance criteria gain one verifiable criterion for the T-009 rule, as the Scope Gate required.
- Acceptance Criteria:
  - One criterion states the expected stale_after presence and value for each lesson, with its verification method
  - The criterion derives its expected value from the record fields T-009 names, with no reference to write time
- Gate: Design Gate

### T-011 Produce the change log for every lesson write

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-002, T-017
- Traces to: S-006
- Status: ready
- Description: The change log holds one entry per lesson creation and per governance action in history, in the T-002 form, with the newest date group first.
- Acceptance Criteria:
  - The change log opens with a title line and groups entries under date headings, newest first (AC-009)
  - The entry count equals the number of creations plus history entries in the lesson set
  - Every date derives from record fields, so an unchanged lesson set yields an unchanged change log
- Gate: Review Gate

### T-012 Name the bundle in the memory slice of new invocation envelopes

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-008, T-017
- Traces to: S-007, S-013
- Status: ready
- Description: New invocation envelopes record the bundle as the lesson store and carry the bundle digest that T-017 defines. Envelopes already recorded under runs are left untouched (Scope Gate ruling on SQ-005).
- Acceptance Criteria:
  - An envelope built after the change names the bundle location and its digest in the memory slice
  - For the same lesson set, the lessons hydrated into the memory slice equal those hydrated before the change
  - No envelope recorded before the change is altered
- Gate: Review Gate

### T-013 Update the automated knowledge-loop test suite to the bundle

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-003, T-004, T-008, T-011, T-012, T-021, T-025, T-026
- Traces to: S-007, S-009, S-011, S-012
- Status: ready
- Description: The automated suite covers bundle round trip, idempotent re-harvest, migration and the conformance check as T-004 assigns them, and no longer refers to the JSON store.
- Acceptance Criteria:
  - The suite passes on the final tree with zero references to the JSON store file name or its exclusion pattern
  - Each behaviour that T-004 assigns to automated coverage has at least one passing case
- Gate: Review Gate

### T-014 Capture the pre-change reference baseline

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: none
- Traces to: S-007, S-008, S-013, S-016, A-002, A-003
- Status: assumption-dependent (A-002, A-003)
- Description: Before the store changes form, a recorded baseline exists for the current lesson set. It holds the rendered lesson section, the result of each loop step, the hash of every run evidence file, and the verdict of every gate, artifact validator and verifier.
- Acceptance Criteria:
  - The baseline records the lesson set it was taken from, by lesson identifier and record digest
  - The rendered lesson section is stored byte for byte
  - Every gate, artifact validator and verifier covered by S-016 has a recorded verdict and input reference
- Gate: Verification Gate

### T-015 Verify the lesson loop behaves as before on the bundle

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-003, T-004, T-008, T-011, T-012, T-014, T-026
- Traces to: S-007, S-008, S-009
- Status: ready
- Description: Recorded evidence shows that AC-010, AC-011 and AC-012 hold on the final bundle against the T-014 baseline.
- Acceptance Criteria:
  - Each loop step result matches the baseline for the same lesson set, with zero mismatches (AC-010)
  - The rendered lesson section is byte-identical to the baseline, neutralised content included (AC-011)
  - A second harvest over unchanged evidence changes zero bundle files (AC-012)
- Gate: Verification Gate

### T-016 Review the change set against the technical design

- Owner: omn-dev-2-reviewer
- Complexity: M (confidence: medium)
- Depends on: T-013, T-032
- Traces to: S-008, S-016
- Status: ready
- Description: A review package with severity-classified findings and a verdict exists for the full change set. It covers field-content safety (R-008) and recall read cost (R-010).
- Acceptance Criteria:
  - The review package records a verdict, with zero unresolved critical or major findings
  - The findings state whether any lesson field value can alter the structure of a frontmatter block, the index or the change log
- Gate: Review Gate

### T-017 Define the bundle write contract

- Owner: architect
- Complexity: M (confidence: low)
- Depends on: none
- Traces to: S-009, S-010, A-004
- Status: assumption-dependent (A-004)
- Description: The design fixes four things: how each bundle file is written so that an interruption leaves it complete, when a write is skipped because the bytes are unchanged, how concurrent writers are excluded, and how the bundle digest is formed.
- Acceptance Criteria:
  - The concept documents, the root index and the change log each have a stated write rule that leaves the file in its prior or new complete state
  - The digest rule yields the same value for byte-identical bundles
  - The design states how the index and change log recover after an interruption between files (A-004)
- Gate: Design Gate

### T-018 Verify interruption safety of every bundle write

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-003, T-004, T-008, T-011
- Traces to: S-010
- Status: ready
- Description: Recorded evidence shows that AC-013 holds at every write step T-004 names.
- Acceptance Criteria:
  - After an interruption at each named step, every concept document, the root index and the change log parse and match their prior or new complete state, with zero partly written files
  - The evidence records one outcome for each write step T-004 names, with zero named steps left without a recorded interruption result
- Gate: Verification Gate

### T-019 Choose the carrier of the conformance check

- Owner: architect
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-011
- Status: ready
- Description: The design names where the conformance check lives, and how an operator runs it standalone and from the verification tooling (D-004).
- Acceptance Criteria:
  - The design names one carrier and one standalone invocation form
  - The carrier runs without the harvest, governance or recall steps
- Gate: Design Gate

### T-020 Decide whether the release checklist lists the conformance check as advisory

- Owner: omn-qa
- Complexity: XS (confidence: high)
- Depends on: T-019
- Traces to: S-011
- Status: ready (closes Q-002)
- Description: A recorded decision states whether the framework release checklist gains an advisory item that runs the conformance check. A mandatory item is never an option (X-005).
- Acceptance Criteria:
  - The decision is recorded with its rationale and names no mandatory item
  - Where the decision adds an advisory item, it names the T-019 standalone invocation form that the item runs
- Gate: Design Gate

### T-021 Provide the standalone OKF §11 conformance check

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-002, T-007, T-019
- Traces to: S-011
- Status: ready
- Description: Through the T-019 carrier, an operator can run a deterministic check that reports pass or fail for a bundle against §11.
- Acceptance Criteria:
  - The check reports fail for a non-reserved document without parseable frontmatter, for an empty type, and for a reserved file that breaks §8 or §9
  - Two runs over the same bundle give identical output and exit status
- Gate: Review Gate

### T-022 Apply the release-checklist listing decision

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-020, T-021
- Traces to: S-011
- Status: ready
- Description: The framework release checklist matches the T-020 decision.
- Acceptance Criteria:
  - The checklist carries the advisory item only if T-020 chose it, and gains no mandatory item
  - Every recorded change proposal keeps its rule F9 verdict
- Gate: Review Gate

### T-023 Verify the conformance check verdicts

- Owner: omn-qa
- Complexity: S (confidence: high)
- Depends on: T-004, T-021, T-026
- Traces to: S-011
- Status: ready
- Description: Recorded evidence shows that AC-014 and AC-015 hold.
- Acceptance Criteria:
  - The check passes the final bundle and fails each of the three seeded defect bundles (AC-014)
  - Two standalone runs give identical output and exit status (AC-015)
- Gate: Verification Gate

### T-024 Define the migration method

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: T-002, T-006
- Traces to: S-012
- Status: ready
- Description: The design states how every record in the JSON store becomes one concept document with its identifier, fields and history intact, and how the root index and change log are produced from the migrated set.
- Acceptance Criteria:
  - The method maps every record field and history entry, including for lessons with empty history (Scope Gate carry-forward)
  - The method takes every generated value and date from record fields, so a later re-harvest leaves the migrated bundle unchanged
- Gate: Design Gate

### T-025 Migrate the existing lessons into the bundle

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-003, T-008, T-011, T-014, T-024
- Traces to: S-012
- Status: ready
- Description: The bundle holds one concept document for each record in the store at migration time, with the root index and change log produced per T-024.
- Acceptance Criteria:
  - The bundle's lesson identifier set equals the store's set at migration time (42 lessons when the request was made)
  - Every history entry keeps its actor and time
- Gate: Review Gate

### T-026 Remove the JSON lesson store

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-027
- Traces to: S-012
- Status: ready
- Description: After T-027 confirms the migration, the JSON lesson store no longer exists and no lesson loop step reads it.
- Acceptance Criteria:
  - The JSON lesson store file is absent from the lesson memory location
  - No loop step reads or writes the JSON store
- Gate: Review Gate

### T-027 Verify migration completeness

- Owner: omn-qa
- Complexity: S (confidence: high)
- Depends on: T-004, T-014, T-025
- Traces to: S-012
- Status: ready
- Description: Recorded evidence shows that AC-016 and AC-017 hold before the JSON store is removed.
- Acceptance Criteria:
  - The lesson identifier sets before and after migration are identical, with zero missing or extra identifiers (AC-016)
  - Each lesson keeps the same history entry count, actors and times (AC-017)
- Gate: Verification Gate

### T-028 Publish the release note for the lesson store change

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-005, T-015, T-016, T-018, T-023, T-029, T-033, T-037
- Traces to: S-012, S-018
- Status: ready
- Description: A release note states that lessons now live in an OKF v0.2 bundle, that the JSON store is removed, and how an operator runs the conformance check. It cites the verification evidence.
- Acceptance Criteria:
  - The release note names the bundle location, the removal of the JSON store, and the standalone check
  - The release note cites the review verdict and each verification record
- Gate: Closure Gate

### T-029 Verify protected surfaces stay unchanged

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-004, T-014, T-032
- Traces to: S-013, S-015, S-016
- Status: ready
- Description: Recorded evidence shows that AC-019, AC-021 and AC-022 hold on the final tree.
- Acceptance Criteria:
  - Every pre-existing run evidence file keeps its baseline hash, with zero changed files (AC-019)
  - A memory optimiser run changes zero bundle files (AC-021)
  - Every gate, artifact validator and verifier returns its baseline verdict, with zero changed verdicts (AC-022)
- Gate: Verification Gate

### T-030 Define the distribution exclusion for the bundle

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-014
- Status: ready
- Description: The design states the rule that excludes every bundle file from the installed payload and the bundled mirror without excluding any other file, given that index.md and log.md are generic names.
- Acceptance Criteria:
  - The rule matches every file under the bundle path and no file outside it
  - The design states that files named index.md or log.md outside the bundle path stay in the installed payload and the bundled mirror (R-009)
- Gate: Design Gate

### T-031 Exclude the bundle from the installed payload

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-030
- Traces to: S-014
- Status: ready
- Description: An installation built after the change contains no file under the bundle path, and no file outside the bundle path is newly excluded.
- Acceptance Criteria:
  - The installed payload holds zero files under the bundle path
  - No file outside the bundle path is newly excluded from the installed payload
- Gate: Review Gate

### T-032 Refresh the bundled mirror from the final framework tree

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-012, T-022, T-026, T-030, T-031, T-035, T-036
- Traces to: S-014
- Status: ready
- Description: The bundled mirror equals the final framework tree under the T-030 exclusion.
- Acceptance Criteria:
  - The mirror holds zero files under the bundle path
  - The mirror matches the final framework tree for every other file
- Gate: Review Gate

### T-033 Verify the bundle is absent from distribution

- Owner: omn-qa
- Complexity: XS (confidence: high)
- Depends on: T-004, T-032
- Traces to: S-014
- Status: ready
- Description: Recorded evidence shows that AC-020 holds.
- Acceptance Criteria:
  - Listings of the installed payload and the bundled mirror show zero files under the bundle path, including files named `index.md`, `log.md` or `L-*.md` (AC-020)
  - The same listings show every memory file outside the bundle path that the final framework tree holds, with zero files missing
- Gate: Verification Gate

### T-034 Define how the memory optimiser leaves the bundle unchanged

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-015
- Status: ready
- Description: The design states the rule by which the memory optimiser skips every bundle file.
- Acceptance Criteria:
  - The rule covers every bundle file and leaves the optimiser's treatment of other memory documents unchanged
  - The rule is scoped to the bundle path, so memory documents named index.md or log.md outside it are still optimised (R-009)
- Gate: Design Gate

### T-035 Keep the memory optimiser from rewriting the bundle

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-034
- Traces to: S-015
- Status: ready
- Description: An optimiser run leaves every bundle file byte-identical and treats other memory documents as before.
- Acceptance Criteria:
  - An optimiser run over the memory location changes zero bundle files
  - The optimiser's output for other memory documents is unchanged
- Gate: Review Gate

### T-036 Describe the bundle in the memory documentation

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-002, T-006, T-017
- Traces to: S-018
- Status: ready
- Description: The memory documents that the change request names describe the bundle as the lesson store, including its document, index and change log forms.
- Acceptance Criteria:
  - The memory readme, memory governance, memory resolver and runtime configuration documents name the bundle as the current lesson store
  - None of those documents names the JSON store as the current lesson store
- Gate: Review Gate

### T-037 Verify the memory documentation names the bundle

- Owner: omn-qa
- Complexity: XS (confidence: high)
- Depends on: T-004, T-036
- Traces to: S-018
- Status: ready
- Description: Recorded evidence shows that AC-024 holds.
- Acceptance Criteria:
  - A text search of the named memory documents finds zero references to the JSON store as the current lesson store (AC-024)
  - Each of the memory readme, memory governance, memory resolver and runtime configuration documents names the bundle location as the current lesson store
- Gate: Verification Gate

### T-038 Record the framework change proposal for this change

- Owner: omn-documentation
- Complexity: S (confidence: low)
- Depends on: T-028
- Traces to: A-005
- Status: assumption-dependent (A-005)
- Description: A framework change proposal exists for this capability addition and links the run artifacts that carried it.
- Acceptance Criteria:
  - The proposal links this run's scope definition, execution plan, technical design, review package and release note
  - The proposal states the change class that the self-hosting classification gives this change (A-005)
- Gate: Closure Gate

### T-039 Verify the framework release checklist for this change

- Owner: omn-qa
- Complexity: XS (confidence: low)
- Depends on: T-038
- Traces to: A-005
- Status: assumption-dependent (A-005)
- Description: Recorded evidence shows that the change satisfies the framework release checklist.
- Acceptance Criteria:
  - The self-hosting release checklist verification reports pass for this change
  - The verification record cites the T-038 proposal and lists zero failed checklist items
- Gate: Closure Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| External: operator supplying the OKF v0.2 SPEC text | T-001 | external | Confirming the rules needs the SPEC text, which is not a supplied input |
| T-001 | T-002 | decision-gate | Confirmed §8 and §9 rules shape the reserved-file contract |
| T-002 | T-003 | contract | The index follows the reserved-file contract |
| T-007 | T-003 | produces-consumes | The index frontmatter is written by the serialiser |
| T-017 | T-003 | contract | The index write follows the write contract |
| T-002 | T-004 | contract | Index and change log checks bind to the reserved-file contract |
| T-006 | T-004 | contract | Document checks bind to the frontmatter contract |
| T-010 | T-004 | produces-consumes | The stale_after criterion must exist before it is mapped |
| T-017 | T-004 | contract | Interruption steps come from the write contract |
| T-019 | T-004 | contract | Conformance checks run through the chosen carrier |
| T-003 | T-005 | verification | Verifies the root index |
| T-004 | T-005 | produces-consumes | Uses the verification method |
| T-008 | T-005 | verification | Verifies the lesson documents |
| T-011 | T-005 | verification | Verifies the change log |
| T-026 | T-005 | verification | Verifies the final bundle and the absent store |
| T-001 | T-006 | decision-gate | Confirmed §5 and §7 rules shape the frontmatter contract |
| T-009 | T-006 | decision-gate | The stale_after rule sets that key's presence |
| T-006 | T-007 | contract | The serialiser writes the contracted keys |
| T-006 | T-008 | contract | Documents follow the frontmatter contract |
| T-007 | T-008 | produces-consumes | Documents are written and read through the serialiser |
| T-017 | T-008 | contract | Document writes follow the write contract |
| T-001 | T-009 | decision-gate | The rule depends on the confirmed §5.5 meaning |
| T-009 | T-010 | decision-gate | The criterion states the decided rule |
| T-002 | T-011 | contract | The change log follows the reserved-file contract |
| T-017 | T-011 | contract | Change log writes follow the write contract |
| T-008 | T-012 | produces-consumes | Memory slice hydration reads lessons from the bundle |
| T-017 | T-012 | contract | The envelope carries the bundle digest the write contract defines |
| T-003 | T-013 | produces-consumes | The suite covers the index |
| T-004 | T-013 | produces-consumes | The suite follows the verification method |
| T-008 | T-013 | produces-consumes | The suite covers the document round trip |
| T-011 | T-013 | produces-consumes | The suite covers the change log |
| T-012 | T-013 | produces-consumes | The suite covers memory slice naming |
| T-021 | T-013 | produces-consumes | The suite covers the conformance check |
| T-025 | T-013 | produces-consumes | The suite covers migration |
| T-026 | T-013 | produces-consumes | The suite drops its references to the removed store |
| T-003 | T-015 | verification | Verifies index behaviour on re-harvest |
| T-004 | T-015 | produces-consumes | Uses the verification method |
| T-008 | T-015 | verification | Verifies loop steps on the bundle |
| T-011 | T-015 | verification | Verifies change log stability on re-harvest |
| T-012 | T-015 | verification | Verifies recall hydration |
| T-014 | T-015 | produces-consumes | Compares against the baseline |
| T-026 | T-015 | verification | Verifies the loop on the final bundle-only tree |
| T-013 | T-016 | produces-consumes | The review covers the updated suite |
| T-032 | T-016 | produces-consumes | The review takes the final change set, which T-032 closes |
| T-003 | T-018 | verification | Verifies index write safety |
| T-004 | T-018 | produces-consumes | Uses the named interruption steps |
| T-008 | T-018 | verification | Verifies document write safety |
| T-011 | T-018 | verification | Verifies change log write safety |
| T-001 | T-019 | decision-gate | Confirmed §11 rules shape what the carrier runs |
| T-019 | T-020 | decision-gate | The listing decision depends on how the check is invoked |
| T-002 | T-021 | contract | The check enforces the reserved-file rules |
| T-007 | T-021 | produces-consumes | The check parses frontmatter with the parser |
| T-019 | T-021 | contract | The check lives in the chosen carrier |
| T-020 | T-022 | decision-gate | The checklist follows the listing decision |
| T-021 | T-022 | produces-consumes | An advisory item runs the check |
| T-004 | T-023 | produces-consumes | Uses the seeded defect bundles |
| T-021 | T-023 | verification | Verifies the check |
| T-026 | T-023 | verification | The check is run over the final bundle |
| T-002 | T-024 | contract | Migration produces the index and log per contract |
| T-006 | T-024 | contract | Migration maps fields per the frontmatter contract |
| T-003 | T-025 | produces-consumes | Migration writes the index |
| T-008 | T-025 | produces-consumes | Migration writes documents through the bundle writer |
| T-011 | T-025 | produces-consumes | Migration writes the change log |
| T-014 | T-025 | produces-consumes | The baseline must record the lesson set before it changes form (A-003) |
| T-024 | T-025 | contract | Migration follows the method |
| T-027 | T-026 | produces-consumes | Removal needs evidence that migration is complete (R-005) |
| T-004 | T-027 | produces-consumes | Uses the verification method |
| T-014 | T-027 | produces-consumes | Compares with the baseline lesson set |
| T-025 | T-027 | verification | Verifies migration |
| T-005 | T-028 | produces-consumes | The release note cites bundle content evidence |
| T-015 | T-028 | produces-consumes | The release note cites loop parity evidence |
| T-016 | T-028 | produces-consumes | The release note cites the review verdict |
| T-018 | T-028 | produces-consumes | The release note cites interruption evidence |
| T-023 | T-028 | produces-consumes | The release note cites conformance evidence |
| T-029 | T-028 | produces-consumes | The release note cites protected-surface evidence |
| T-033 | T-028 | produces-consumes | The release note cites distribution evidence |
| T-037 | T-028 | produces-consumes | The release note cites documentation evidence |
| T-004 | T-029 | produces-consumes | Uses the verification method |
| T-014 | T-029 | produces-consumes | Compares against the baseline hashes and verdicts |
| T-032 | T-029 | verification | Verifies the final tree |
| T-030 | T-031 | contract | The installer follows the exclusion rule |
| T-012 | T-032 | produces-consumes | The mirror takes the changed framework tree |
| T-022 | T-032 | produces-consumes | The mirror takes the checklist change |
| T-026 | T-032 | produces-consumes | The mirror takes the store removal and the bundle code |
| T-030 | T-032 | contract | The mirror follows the exclusion rule |
| T-031 | T-032 | produces-consumes | The mirror takes the installer exclusion |
| T-035 | T-032 | produces-consumes | The mirror takes the optimiser change |
| T-036 | T-032 | produces-consumes | The mirror takes the memory documentation |
| T-004 | T-033 | produces-consumes | Uses the verification method |
| T-032 | T-033 | verification | Verifies the payload and the mirror |
| T-034 | T-035 | contract | The optimiser follows the skip rule |
| T-002 | T-036 | produces-consumes | The documentation describes the index and change log |
| T-006 | T-036 | produces-consumes | The documentation describes the lesson documents |
| T-017 | T-036 | produces-consumes | The documentation describes the store digest and write rules |
| T-004 | T-037 | produces-consumes | Uses the verification method |
| T-036 | T-037 | verification | Verifies the documentation |
| T-028 | T-038 | produces-consumes | The proposal links the release note |
| T-038 | T-039 | verification | Verifies the checklist for the proposal |

### 8.2 External Dependencies

| Responsible party | What is needed | Blocks |
|---|---|---|
| External: operator supplying the OKF v0.2 SPEC text | The OKF v0.2 SPEC text for §5, §7, §8, §9 and §11, supplied as an input to the design phase (R-006) | T-001 |

### 8.3 Implementation Order

- Wave 1: T-001, T-014, T-017, T-030, T-034
- Wave 2: T-002, T-009, T-019, T-031, T-035
- Wave 3: T-006, T-010, T-011, T-020
- Wave 4: T-004, T-007, T-024, T-036
- Wave 5: T-003, T-008, T-021, T-037
- Wave 6: T-012, T-018, T-022, T-025
- Wave 7: T-027
- Wave 8: T-026
- Wave 9: T-005, T-013, T-015, T-023, T-032
- Wave 10: T-016, T-029, T-033
- Wave 11: T-028
- Wave 12: T-038
- Wave 13: T-039

## Suggested Workflow

Selected workflow: implement-feature

Selected because: The request adds new framework functionality, a bundle storage contract and a conformance check. The change request classes it as a capability addition and routes it to this workflow. This plan is the execution-planning evidence for the Planning Gate. It recommends the workflow and does not start it. Implementation-phase tasks need the Design Gate approved before they start.

| Phase | Tasks |
|---|---|
| solution-design-and-risk-assessment | T-001, T-002, T-004, T-006, T-009, T-010, T-017, T-019, T-020, T-024, T-030, T-034 |
| implementation | T-003, T-007, T-008, T-011, T-012, T-013, T-014, T-021, T-022, T-025, T-026, T-027, T-031, T-032, T-035, T-036 |
| quality-review | T-005, T-015, T-016, T-018, T-023, T-029, T-033, T-037 |
| documentation-and-release-handoff | T-028, T-038, T-039 |

| Gate | Required owners |
|---|---|
| Planning Gate | omn-tech-lead, omn-orchestrator (planner produced this evidence and does not decide) |
| Design Gate | omn-architect, omn-tech-lead (architect produces the design, so omn-tech-lead decides) |
| Review Gate | omn-dev-2-reviewer, omn-qa (omn-dev-2-reviewer produces the findings, so omn-qa decides) |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation (omn-documentation produces T-028, so omn-orchestrator decides) |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| architecture-analysis | T-001 | architect | Primary |
| technical-approach-definition | T-002, T-006, T-017, T-019, T-024, T-030, T-034 | architect | Primary |
| architecture-decision-authoring | T-009 | architect | Primary |
| acceptance-authority | T-010 | omn-product-owner | Primary |
| validation-design | T-004, T-020 | omn-qa | Primary |
| quality-verification | T-005, T-014, T-015, T-018, T-023, T-027, T-029, T-033, T-037, T-039 | omn-qa | Primary |
| implementation-delivery | T-003, T-007, T-008, T-011, T-012, T-013, T-021, T-022, T-025, T-026, T-031, T-032, T-035 | omn-dev-1-implement | Primary |
| code-review | T-016 | omn-dev-2-reviewer | Primary |
| documentation | T-036, T-038 | omn-documentation | Primary |
| release-communication | T-028 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | skills/architecture/clean-architecture-checklist.md | T-001, T-002, T-006, T-009, T-017, T-019, T-024, T-030, T-034 | Primary |
| S02 | skills/business/domain-modeling.md | T-006, T-009, T-010, T-024 | Primary |
| S03 | skills/dotnet/engineering-playbook.md | T-007, T-008, T-021 | Advisory |
| S06 | skills/database/database-engineering.md | T-024, T-025, T-026, T-027 | Primary |
| S07 | skills/testing/testing-strategy.md | T-004, T-005, T-013, T-014, T-015, T-018, T-023, T-027, T-029, T-033, T-037, T-039 | Primary |
| S08 | skills/performance/performance-engineering.md | T-016 | Advisory |
| S09 | skills/security/secure-engineering.md | T-006, T-016 | Secondary |
| S10 | skills/git/git-collaboration.md | T-032, T-038 | Secondary |
| S11 | skills/logging/observability-logging.md | T-028 | Advisory |
| S12 | skills/error-handling/error-handling-strategy.md | T-017, T-021 | Secondary |

## Acceptance Criteria

1. BO-1: The conformance check passes the bundle, fails each of three seeded defects, and gives identical output on repeated runs. Evidence: the T-023 verification record for AC-014 and AC-015.
2. BO-1: The root index declares OKF v0.2 and links every lesson document exactly once. Evidence: the T-005 verification record for AC-002 and AC-023.
3. BO-2: Every lesson document carries a non-empty type, title, description and tags, plus sources, generated and status. It carries verified exactly where an operator approved the lesson, and stale_after as the T-010 criterion states. Evidence: the T-005 verification record for AC-003 to AC-007 and the T-010 criterion.
4. BO-3: For the same lesson set, every loop step gives its baseline result, the dispatched lesson text is byte-identical, and a re-harvest changes no bundle file. Evidence: the T-015 verification record against the T-014 baseline for AC-010 to AC-012.
5. BO-3: Every lesson's identifier, fields and governance history survive migration, the change log reflects the history, and the JSON store is gone. Evidence: the T-027 and T-005 verification records for AC-008, AC-009 and AC-016 to AC-018.
6. BO-3: An interruption at any write step leaves no partly written bundle file. Evidence: the T-018 verification record for AC-013.
7. BO-4: Run evidence hashes, baseline verdicts and the bundle under an optimiser run are all unchanged, and the payload and mirror hold no bundle file. Evidence: the T-029 and T-033 verification records for AC-019 to AC-022.
8. BO-5: The memory documentation names the bundle as the current lesson store. Evidence: the T-037 verification record for AC-024.

## Definition of Done

- [ ] All eight plan acceptance criteria are verified with recorded evidence
- [ ] The Planning, Design, Review, Verification and Closure Gates are approved, with deciding owners recorded
- [ ] Each task's acceptance criteria are satisfied or formally waived by the gate owner
- [ ] A-001 to A-005 are confirmed by their named roles or converted to recorded decisions
- [ ] R-001 to R-013 are closed or accepted with named owners
- [ ] Q-001 and Q-002 are closed or explicitly accepted at the Design Gate
- [ ] The release note (T-028) and the memory documentation (T-036) are published
- [ ] The change proposal (T-038) is recorded and the release checklist verification (T-039) passes
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Do the feature request and the architecture context state OKF v0.2 §5, §7, §8, §9 and §11 accurately, given that the SPEC text is not a supplied input? Carried from SQ-006; per the Scope Gate it closes at design on §5.3 and §5.4 | no | architect | T-001, T-002, T-006, T-021 |
| Q-002 | Should the framework release checklist list the conformance check as an advisory item? Carried from SQ-007 | no | omn-qa | T-020, T-022 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 | T-001, T-002, T-003, T-004, T-005 |
| S-002 | T-004, T-005, T-006, T-007, T-008 |
| S-003 | T-004, T-005, T-006, T-007, T-008 |
| S-004 | T-004, T-005, T-006, T-007, T-008, T-009, T-010 |
| S-005 | T-004, T-005, T-006, T-007, T-008 |
| S-006 | T-002, T-004, T-005, T-011 |
| S-007 | T-004, T-008, T-012, T-013, T-014, T-015 |
| S-008 | T-004, T-014, T-015, T-016 |
| S-009 | T-004, T-013, T-015, T-017 |
| S-010 | T-004, T-017, T-018, A-004 |
| S-011 | T-001, T-004, T-007, T-013, T-019, T-020, T-021, T-022, T-023, A-001, Q-001, Q-002 |
| S-012 | T-004, T-005, T-013, T-024, T-025, T-026, T-027, T-028, A-003 |
| S-013 | T-004, T-012, T-014, T-029 |
| S-014 | T-004, T-030, T-031, T-032, T-033 |
| S-015 | T-004, T-029, T-034, T-035 |
| S-016 | T-004, T-014, T-016, T-029, A-002 |
| S-017 | T-002, T-003, T-004, T-005 |
| S-018 | T-004, T-028, T-036, T-037 |
