# Architecture Decision Record: D-002

## Metadata

- ADR ID: D-002
- Title: Lessons live in one canonical JSON store under memory/lessons/ with a closed record and a governance overlay
- Date: 2026-10-09
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-c9fb8d5bbb32; technical-design.md; T-002, T-003, T-004, T-005

## Context

- Problem statement: lessons need a governed, deterministic home that harvest can upsert by fingerprint and operators can govern without losing history.
- Business and technical constraints: one lesson per fingerprint (C-001); byte-identical store over unchanged evidence (C-002); lifecycle and no deletion (C-003); closed fields, no evidence free text (C-012); under memory/, outside the optimizer scan (C-014); never shipped (C-015).
- Current architecture baseline: memory/ holds only Markdown documents (F-020); the optimizer scans only Markdown (F-013); writeback policy requires fingerprint upsert, owner, and rationale (F-017); evidence carries free text beside the fields a lesson needs (F-011, F-012).

## Decision

- Selected option: O-001.
- Decision statement: memory/lessons/lessons.store.json (M-004), schema framework.memory/lessons.v1, holds lessons with the closed field list in technical-design.md 5.3; fingerprints are check:artifact-type:check-id and gate:gate-name:phase-id; every harvest recomputes evidence fields from scratch and carries status, owner, rationale, remedy, and history over by fingerprint; serialisation is canonical with no harvest timestamp; writes are atomic under an exclusive lock.
- Scope of impact: M-001 (writer and reader), M-002 (reader at dispatch), M-004 (new), M-005 (threshold and default owner).

## Alternatives Considered

1. O-003: Markdown entries in memory/known-issues.md
- Benefits: reuses an existing governed document.
- Risks: the optimizer rewrites Markdown; prose edits break byte identity; the seeded document ships to installs.
- Why not selected: eliminated by C-014, C-002, C-015.

2. O-007: a committed empty store shipped as a seed
- Benefits: installs start with an empty, valid store.
- Risks: this repository's harvest writes the same authoritative file, and the sync mirrors it into the bundle.
- Why not selected: eliminated by C-015.

3. O-002: same store under a different module boundary
- Benefits: identical store contract.
- Risks: as recorded under D-001.
- Why not selected: loses on criterion 4 (C-024); the store contract itself is unchanged by it.

## Consequences

- Positive outcomes expected: idempotent harvest by construction; operator history preserved across harvests; no evidence free text in the store.
- Tradeoffs accepted: full recomputation on each harvest (C-017); a lesson whose evidence disappears is retained rather than removed.
- Risks introduced: R-005, R-006, R-008, R-013.

## Validation Plan

- Metrics to monitor: store digest across consecutive harvests; lesson count and history length before and after governance commands.
- Verification checkpoints: AC-001 to AC-009 tests in M-012; the exposure review at the Review Gate.
- Rollback or reversal conditions: if byte identity cannot hold across platforms, or a field outside the closed list is needed, the schema id is incremented under a new record.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
