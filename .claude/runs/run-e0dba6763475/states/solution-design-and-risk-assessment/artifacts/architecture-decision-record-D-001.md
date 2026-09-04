## Metadata

- ADR ID: D-001
- Title: Carry the framework payload as declared package data inside the omn_agent package
- Date: 2026-09-03
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: CKA-02 (adoption backlog under docs/), run-e0dba6763475, CKA-02-technical-design

## Context

- Problem statement: a non-editable install of the built distribution carries no
  framework payload, so the CLI cannot install anything without an explicit
  `--source` checkout. The current packaging configuration declares only the
  `omn_agent` package with no package data (F-001), no build-inclusion directive
  file exists (F-002), and the distribution metadata lists no payload path (F-010).
- Business and technical constraints: the non-editable build must carry the complete
  managed-plus-seed payload tree (C-003) filtered by the installer's
  exclusion-pattern set (C-004); the bundled payload must be resolvable from the
  installed package location (C-006); the change must be additive only (C-002); the
  distribution file lists must be regenerated to match with zero discrepancies
  (C-007).
- Current architecture baseline: F-006 fixes the managed and seed directory sets;
  F-007 fixes the exclusion-pattern set; F-013 establishes that payload enumeration
  operates on whatever source directory it is given, so a bundled source needs no
  new enumeration machinery.

## Decision

- Selected option: O-001.
- Decision statement: the framework payload is carried inside the `omn_agent`
  package as a bundled data subtree (M-003) that mirrors the authoritative payload
  tree — every managed directory plus both seed directories (F-006), filtered by
  the installer's exclusion patterns (F-007) — declared as package data in the
  packaging configuration (M-001), rather than shipped through source-distribution
  include directives or a second distribution unit.
- Scope of impact: M-001 (distribution contract change) and M-003 (new bundled
  subtree), with downstream effect on M-002 (the resolution fallback targets the
  bundled location, ADR D-002) and M-004 (metadata regeneration).

## Alternatives Considered

1. O-002 — ship the root-level payload directory through source-distribution
   include directives (a build-inclusion directive file)
- Benefits: no duplication of the payload into the package tree; minimal
  configuration change; the payload stays at its current root location.
- Risks: the payload is carried in the source distribution but does not land at a
  location resolvable from the installed package in a non-editable install
  (A-001), leaving the binary distribution incomplete.
- Why not selected: violates C-006, and C-003 for the binary distribution, under
  A-001. Eliminated in the section 5.2 evaluation of the design package.

2. O-003 — carry the payload in a second, dedicated data-carrying package
   installed alongside `omn_agent`
- Benefits: isolates payload versioning from code versioning; keeps the code
  package small.
- Risks: two distribution units must be versioned, built, and released in
  lockstep; version skew between them is a new failure mode; resolution acquires a
  cross-package dependency.
- Why not selected: satisfies every hard constraint but loses to O-001 on impact
  surface (3 versus 1), reuse leverage (3 versus 6), migration burden (2 versus 1),
  and operability.

## Consequences

- Positive outcomes expected: a non-editable install is self-contained — the
  clean-environment walkthrough (C-009) and dry-run parity (C-008) become
  achievable with no explicit source option; the dependent gating ticket is
  unblocked.
- Tradeoffs accepted: the payload is duplicated inside the package tree, the
  distribution grows by the payload size, and a synchronization obligation exists
  between the authoritative tree and the bundled copy (A-003).
- Risks introduced: R-001 (bundle drift from the authoritative tree), R-004
  (packaged set or filter divergence from F-006/F-007), R-007 (unintended content
  shipped to every downstream install), and R-002 (A-001 false, re-opening the
  mechanism evaluation).

## Validation Plan

- Metrics to monitor: dry-run payload parity between paired editable and
  non-editable installs at the assurance level decided under P-006 (C-008); count
  of bundled files matching the exclusion patterns, required to be zero (C-004);
  count of discrepancies between distribution file lists and the configured payload
  tree, required to be zero (C-007).
- Verification checkpoints: P-003 (bundle completeness and framework-tree validity
  per F-005 before the fallback is enabled), P-005 (metadata regeneration), P-007
  (distribution inspection, walkthrough, parity, suite, and proof scripts).
- Rollback or reversal conditions: if the bundle proves incomplete, stale, or
  unmaintainable, withdraw the package-data declaration from M-001 and the bundled
  subtree M-003; the distributions revert to the current shape (F-001, F-010) with
  no effect on any installed target or on existing resolution modes.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
