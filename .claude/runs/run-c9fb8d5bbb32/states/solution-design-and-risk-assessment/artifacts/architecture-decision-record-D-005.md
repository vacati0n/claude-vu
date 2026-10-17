# Architecture Decision Record: D-005

## Metadata

- ADR ID: D-005
- Title: The lesson store is excluded from the shipped payload by an installer exclusion pattern
- Date: 2026-10-09
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-c9fb8d5bbb32; technical-design.md; T-002, T-022

## Context

- Problem statement: memory/ is a seed directory mirrored into the bundle, so a store committed there would carry this repository's lessons into every install.
- Business and technical constraints: this repository's lessons never ship and the payload-sync tests stay unchanged (C-015); the store lives under memory/ (C-014); the mirror is refreshed only by its sync procedure (C-018).
- Current architecture baseline: memory is in SEED_DIRS; _walk skips names matching EXCLUDE_PATTERNS for the installer, the sync, and the bundle tests alike (F-014); seeds are copied only when missing (F-021).

## Decision

- Selected option: O-001.
- Decision statement: omn_agent/source.py (M-006) adds the pattern lessons.store.* to EXCLUDE_PATTERNS, which removes the store and its lock from payload enumeration, the bundle sync, and the bundle tests at once; installs create their own store on first harvest.
- Scope of impact: M-006, M-007 (mirror stays free of the store), M-004, M-021 (unchanged; enforces the pattern through _excluded).

## Alternatives Considered

1. O-007: a committed empty store as a seed
- Benefits: installs start with a valid empty file.
- Risks: this repository's harvest fills the same file and the sync mirrors it.
- Why not selected: eliminated by C-015.

2. O-003: lessons in a shipped Markdown document
- Benefits: none for exclusion.
- Risks: ships by construction.
- Why not selected: eliminated by C-014, C-002, C-015.

## Consequences

- Positive outcomes expected: the bundle and installs never hold this repository's lessons; no test code changes.
- Tradeoffs accepted: one edit outside the surfaces the change request listed.
- Risks introduced: R-011.

## Validation Plan

- Metrics to monitor: files matching the pattern inside the bundle (expected none).
- Verification checkpoints: tests/test_bundled_payload.py passes over the refreshed mirror; M-012 checks a store placed in a temporary tree is absent from the payload map (P-012).
- Rollback or reversal conditions: if another installer path copies memory/ files (A-004 false), replace the pattern with an exclusion at that path under a new record.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
