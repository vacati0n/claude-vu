# Architecture Decision Record: D-006

## Metadata

- ADR ID: D-006
- Title: The lesson bundle is excluded from distribution and the memory optimiser by relative path, and the lessons.store.* pattern is retired
- Date: 2026-10-17
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-79276e78d773; technical-design.md; T-030, T-031, T-034, T-035

## Context

- Problem statement: The bundle uses the reserved names index.md and log.md, which other memory documents also use, so a name pattern cannot exclude the bundle without excluding unrelated files.
- Business and technical constraints: bundle excluded from payload and mirror by relative path, nothing else newly excluded (C-013); optimiser leaves the bundle unchanged, scoped by relative path (C-014); mirror refreshed only by the sync step (C-020).
- Current architecture baseline: EXCLUDE_PATTERNS holds lessons.store.*, matched by name in _walk, which has the base-relative path, and both payload and seed enumeration use it (F-013); the parity test builds through _walk (F-014); the optimiser denies segments and names but not index.md or log.md (F-015).

## Decision

- Selected option: O-002.
- Decision statement: omn_agent/source.py (M-006) gains EXCLUDE_PATHS holding memory/lessons, and _walk skips any file whose base-relative path equals or lies under an entry; lessons.store.* is retired because every file it matched lies under that path. runtime/optimize_memory.py (M-007) denies any path whose segments contain memory followed directly by lessons, case-insensitive, with its own reason naming the lesson bundle. memory/index.md and every other memory document stay in scope.
- Scope of impact: M-006, M-007, M-013, M-014, M-015 (inherits through _walk).

## Alternatives Considered

1. O-001: same exclusions with all bundle code inside knowledge.py
- Benefits: none specific to exclusion.
- Risks: check tied to the loop module.
- Why not selected: ranks second on criterion 4 (C-022).

2. O-003: JSON store retained with an exported bundle
- Benefits: existing pattern keeps working for the store.
- Risks: export still needs a path rule.
- Why not selected: eliminated by C-011.

3. O-004: JSON in document bodies
- Benefits: none for exclusion.
- Risks: fields not under their own key.
- Why not selected: eliminated by C-005.

4. O-005: third-party YAML library
- Benefits: none for exclusion.
- Risks: new dependency.
- Why not selected: eliminated by C-016.

5. O-006: log.md appended at write time
- Benefits: none for exclusion.
- Risks: time-dependent content.
- Why not selected: eliminated by C-006, C-008.

## Consequences

- Positive outcomes expected: installer, sync, and bundle tests inherit one rule; no unrelated memory file leaves scope; installs create their own bundle.
- Tradeoffs accepted: a second exclusion mechanism beside name patterns in M-006.
- Risks introduced: R-007.

## Validation Plan

- Metrics to monitor: payload and mirror listings under memory/lessons (expected none); bundle hashes across an optimiser run (expected equal).
- Verification checkpoints: exclusions exist before any bundle file is in the authoritative tree (P-004); fixtures with memory/index.md outside the bundle and the parity test over the refreshed mirror (P-013).
- Rollback or reversal conditions: if another path enumerates memory files (A-001 false), add the exclusion at that path under a new record.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
