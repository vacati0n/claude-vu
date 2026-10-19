# Architecture Decision Record: D-005

## Metadata

- ADR ID: D-005
- Title: An explicit migrate subcommand verifies the bundle before removing the JSON store, and readers refuse a JSON-only state
- Date: 2026-10-17
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-79276e78d773; technical-design.md; T-024, T-025, T-026, T-027

## Context

- Problem statement: Current lessons must move into the bundle with identifiers, fields, and history intact, and the JSON store must be removed, without an aggregation or a reader ever migrating implicitly.
- Business and technical constraints: removal only after complete migration is verified (C-011); no run evidence file edited (C-012); every byte derived from records (C-008).
- Current architecture baseline: load_store reads the JSON store (F-002); the store holds 43 lessons and the set has moved since the request (F-011, F-012); aggregation harvests rewrite the live store during this run (F-027); harvest_for_run records failures without failing aggregation (F-003); recall fails open (F-007).

## Decision

- Selected option: O-002.
- Decision statement: The knowledge command line gains a migrate subcommand that, under the lock, loads the JSON store with the existing reader, writes the full bundle through write_store, re-loads the bundle, and compares it record for record (equal dictionaries, count, and lesson_id set). Only on equality does it remove the JSON store and report counts; on any mismatch it leaves both forms in place and fails with migration-mismatch. Re-running after an interruption repeats the write and comparison. When only the JSON store exists, every reader and writer raises store-migration-pending; with both present, the bundle is authoritative.
- Scope of impact: M-002, M-003, M-009 to M-012 (one-time step documented), M-013.

## Alternatives Considered

1. O-001: same migration with all bundle IO inside knowledge.py
- Benefits: none specific to migration.
- Risks: check tied to the loop module.
- Why not selected: ranks second on criterion 4 (C-022).

2. O-003: keep the JSON store and export the bundle
- Benefits: no migration at all.
- Risks: JSON store never removed.
- Why not selected: eliminated by C-011.

3. O-004: JSON record in each document body
- Benefits: trivial migration.
- Risks: fields not under their own key.
- Why not selected: eliminated by C-005.

4. O-005: third-party YAML library
- Benefits: none for migration.
- Risks: new dependency.
- Why not selected: eliminated by C-016.

5. O-006: log.md appended at write time
- Benefits: none.
- Risks: migrated lessons would lack creation entries.
- Why not selected: eliminated by C-006, C-008.

## Consequences

- Positive outcomes expected: the JSON store disappears only after a verified copy exists; an aggregation can never migrate; other checkouts see a named reason instead of silent loss.
- Tradeoffs accepted: other checkouts must run migrate once, and recall withholds lessons there until they do; the store-migration-pending branch remains until no JSON-only checkout exists.
- Risks introduced: R-003, R-004, R-012.

## Validation Plan

- Metrics to monitor: document count against record count at migration; lesson_id set equality; history entry counts.
- Verification checkpoints: baseline copy captured (P-003); migration verified with the JSON store present (P-009); removal and suite move in the same change (P-010); AC-016 to AC-018 and a forced-mismatch fixture (P-013).
- Rollback or reversal conditions: before removal, delete the bundle and keep the JSON store; after removal, revert the change set, which restores the tracked JSON file, and re-apply governance actions recorded after migration.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
