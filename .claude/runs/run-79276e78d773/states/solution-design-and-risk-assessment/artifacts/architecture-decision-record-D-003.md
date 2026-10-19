# Architecture Decision Record: D-003

## Metadata

- ADR ID: D-003
- Title: Bundle read and write contract with whole-file replacement, derived reserved files, and a bundle digest
- Date: 2026-10-17
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-79276e78d773; technical-design.md; T-008, T-009, T-011, T-015

## Context

- Problem statement: The single-file store write becomes a multi-file write, which must stay deterministic, interruption-safe per file, and invisible to every caller above the store boundary.
- Business and technical constraints: loop results and rendered text unchanged (C-007); every byte derived from record fields with byte-identical re-harvest (C-008); each file replaced whole (C-009); governance and ranking unchanged (C-026); recall cost proportional to lesson count (C-023).
- Current architecture baseline: write_store writes a temporary file and os.replace only when bytes differ (F-001); load_store returns schema and lessons or None and raises store-unreadable (F-002); StoreLock guards writers (F-003); recall reports store and store_digest (F-007); harvest reports store fields in its outcome (F-008).

## Decision

- Selected option: O-002.
- Decision statement: load_store parses every root L-*.md, requires type Lesson, a lesson_record with exactly the LESSON_FIELDS keys, and lesson_id equal to the file stem, raises store-unreadable naming the file otherwise, and returns STORE_SCHEMA with lessons sorted by fingerprint. write_store, under the lock at memory/lessons/lessons.lock, replaces changed documents, removes orphaned documents and temporary files, rewrites log.md, then index.md last, skipping any file whose bytes are equal. The bundle digest is the state_engine digest over sorted lines of each root .md name and its sha256; recall and the harvest outcome report store memory/lessons with this digest.
- Scope of impact: M-002, M-003, M-013, M-023 (old evidence keeps the JSON name).

## Alternatives Considered

1. O-001: same contract inside knowledge.py with no separate module
- Benefits: fewer imports.
- Risks: check tied to the loop module.
- Why not selected: ranks second on criterion 4 (C-022).

2. O-003: JSON store remains authoritative, bundle exported
- Benefits: single-file atomic write retained.
- Risks: two stores of record.
- Why not selected: eliminated by C-011.

3. O-004: fenced JSON in each document body
- Benefits: simpler parse.
- Risks: fields not under their own key.
- Why not selected: eliminated by C-005.

4. O-005: third-party YAML library
- Benefits: none for the write order.
- Risks: new dependency.
- Why not selected: eliminated by C-016.

5. O-006: log.md appended at write time
- Benefits: fewer bytes rewritten.
- Risks: log not recoverable from records; time-dependent content.
- Why not selected: eliminated by C-006, C-008.

## Consequences

- Positive outcomes expected: callers above the store boundary are unchanged; a write interrupted between files is repaired by the next write; unchanged evidence writes nothing.
- Tradeoffs accepted: documents can disagree with index.md and log.md after an interruption until the next write (A-003); recall reads every document (A-005).
- Risks introduced: R-005, R-006.

## Validation Plan

- Metrics to monitor: bundle file hashes across two harvests; elapsed time recorded in knowledge-harvest.json.
- Verification checkpoints: write and read exist after the baseline (P-006); AC-010 to AC-013 with fault injection after each write step (P-013).
- Rollback or reversal conditions: if S-010 is ruled to require cross-file agreement (A-003 false), replace the write order with a staged directory swap under a new record.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
