## Metadata

- ADR ID: D-002
- Title: Append a bundled-payload candidate to source resolution, strictly last
- Date: 2026-09-03
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: CKA-02 (adoption backlog under docs/), run-e0dba6763475, CKA-02-technical-design

## Context

- Problem statement: `find_source` currently probes only an explicit `--source`
  path and a framework tree next to the package checkout (F-003), so a non-editable
  install has no resolvable source even once the payload is bundled (ADR D-001).
  The fallback must be added without changing the outcome in any environment where
  an existing candidate resolves.
- Business and technical constraints: resolution precedence is unchanged — explicit
  source first, then the checkout-adjacent tree, then and only then the bundled
  payload (C-001); the failure message when nothing resolves retains the existing
  actionable guidance naming the `--source` remedy (C-005); the bundled payload
  must be resolvable from the installed package location (C-006); the change is
  additive only (C-002).
- Current architecture baseline: F-003 fixes the existing candidate order; F-004
  fixes the typed failure and its hint; F-005 fixes the framework-tree validity
  check every candidate must pass; F-008 establishes that the installer consumes
  `find_source` unchanged and guards against source-equals-target.

## Decision

- Selected option: O-001.
- Decision statement: `find_source` (M-002) gains exactly one new candidate — the
  bundled payload location inside the installed package (M-003, per ADR D-001) —
  appended strictly after the existing candidates. The existing framework-tree
  validity check (F-005) applies to the bundled candidate unchanged (inline
  decision D-003), and the existing failure path and guidance (F-004) are retained
  when no candidate resolves.
- Scope of impact: M-002, with M-005 (installer) and M-006 (validator) verified
  unchanged as consumers, and M-008 (test suite) extended with coverage for the new
  environment class.

## Alternatives Considered

1. O-002 — resolve a payload shipped through source-distribution include
   directives at its root-level location
- Benefits: no bundled subtree inside the package; the fallback would point at the
  payload's current root-relative shape.
- Risks: under A-001 the payload does not land at a location resolvable from the
  installed package in a non-editable install, so the fallback would target a
  location that does not exist precisely in the environment that needs it.
- Why not selected: violates C-006 (and C-003 for the binary distribution).
  Eliminated in the section 5.2 evaluation of the design package.

2. O-003 — resolve the payload from a second, dedicated data-carrying package
- Benefits: the fallback location is isolated from the code package's own layout.
- Risks: resolution acquires a cross-package dependency; a version skew between the
  two packages makes the resolved payload silently mismatched with the CLI.
- Why not selected: satisfies the hard constraints but loses to O-001 on impact
  surface, reuse leverage, migration burden, and operability in the section 5.2
  evaluation.

## Consequences

- Positive outcomes expected: resolution succeeds in the fresh-environment class
  (C-009) while every existing environment class resolves exactly as before
  (C-001); the failure behaviour in environments with no candidate at all is
  unchanged (C-005).
- Tradeoffs accepted: the candidate list grows by one probe, and the resolution
  contract now depends on the bundled copy being complete and current (coupling to
  ADR D-001 and its synchronization obligation A-003).
- Risks introduced: R-003 (the bundled candidate resolving ahead of an existing
  candidate through an ordering defect), and exposure to R-001 (a stale bundle
  resolving successfully but delivering drifted content).

## Validation Plan

- Metrics to monitor: resolved-source identity across the three environment
  classes (explicit source; checkout-adjacent tree; neither present with the
  bundle available); failure-message content in the no-candidate environment.
- Verification checkpoints: P-002 (contract acceptance before implementation),
  P-004 (fallback delivered against the proven bundle from P-003), P-007
  (three-environment precedence demonstration and failure-guidance check, plus the
  suite and proof scripts per C-010).
- Rollback or reversal conditions: if the fallback changes the resolved source in
  any environment where an existing candidate is present, or resolves an invalid
  bundle, withdraw the appended candidate from M-002; resolution reverts to F-003
  behaviour with the failure path F-004 intact.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
