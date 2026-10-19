# Architecture Decision Record: D-001

## Metadata

- ADR ID: D-001
- Title: A lesson-agnostic standard-library module owns OKF frontmatter and the §11 check, with a standalone verifier depending on it alone
- Date: 2026-10-17
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate; omn-tech-lead decides under the Producer Exclusion Rule)
- Related Work Items: run-79276e78d773; technical-design.md; T-007, T-020, T-021, T-022

## Context

- Problem statement: The lesson store must be written and read as OKF v0.2 Markdown with frontmatter, and an operator needs a deterministic §11 check that runs without the lesson loop, yet the standard library offers no YAML reader or writer.
- Business and technical constraints: standard library only (C-016); the check runs standalone without harvest, governance, or recall (C-010); the check depends on no lesson-loop code and works on any bundle path (C-022); no field value can alter document structure (C-017).
- Current architecture baseline: knowledge.py imports only the standard library and state_engine, enforced by a boundary test (F-009); no YAML writer exists in the runtime and the installed YAML package is excluded (F-025, C-016); OKF §4.1, §8, §9, and §11 define what the check must judge (F-023).

## Decision

- Selected option: O-002.
- Decision statement: New module runtime/okf.py (M-001) imports nothing from the framework and offers frontmatter subset dump and parse, document split and join, and conformance over a bundle directory. knowledge.py (M-002) maps lessons to documents through it one-way. The new verifier runtime/verify_okf_bundle.py (M-004) imports M-001 only, checks memory/lessons by default or a given path, and exits 0 on pass or absent, 1 on fail, 2 for a missing explicit path.
- Scope of impact: M-001, M-002, M-004, M-008 (FR-13 names M-004), M-013 (boundary tests), M-014 (mirror carries the new files).

## Alternatives Considered

1. O-001: serialiser, parser, bundle IO, and the §11 check inside knowledge.py, with the verifier importing it
- Benefits: one module fewer; same impact surface and reuse.
- Risks: the verifier loads the loop module with its policy and state-engine dependencies; the check cannot be reused for another bundle without it.
- Why not selected: ranks second on criterion 4 (C-022).

2. O-003: JSON store kept as source of truth, bundle generated as an export
- Benefits: no read path change.
- Risks: two stores of record.
- Why not selected: eliminated by C-011.

3. O-004: lesson record as a fenced JSON block in each document body
- Benefits: trivial round-trip.
- Risks: fields not readable under their own frontmatter key.
- Why not selected: eliminated by C-005.

4. O-005: third-party YAML library
- Benefits: full YAML support.
- Risks: new dependency on the runtime path.
- Why not selected: eliminated by C-016.

5. O-006: log.md appended incrementally at write time
- Benefits: no log regeneration.
- Risks: log content depends on write history and time.
- Why not selected: eliminated by C-006, C-008.

## Consequences

- Positive outcomes expected: the §11 check runs on any bundle with no loop dependency; the loop changes only at its store boundary; the module boundary stays testable.
- Tradeoffs accepted: the parser accepts a YAML subset, so a valid non-subset document from another tool is reported unparseable (D-007).
- Risks introduced: R-002, R-011, R-014.

## Validation Plan

- Metrics to monitor: round-trip identity over every live record shape; module boundary test results; verifier exit status on seeded bundles.
- Verification checkpoints: M-001 exists with round-trip and hostile fixtures (P-005); M-004 and FR-13 exist and S5 resolves the script path (P-007); conformance verdicts and the bundled-payload test on the final tree (P-013).
- Rollback or reversal conditions: if the subset cannot carry a live record shape without loss, revise D-007 under a new record before P-006; a revert of the change set removes M-001 and M-004.

## Approval

- Architect: unsigned; producer of this record
- Tech Lead: pending the Design Gate decision
- Product Owner (if scope-impacting): not required
