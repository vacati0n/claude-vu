# Architecture Decision Record D-001

## Metadata

- ADR ID: D-001
- Title: Bind the content-contract gate check to the runtime's own readers by import
- Date: 2026-09-04
- Status: Proposed
- Owners: architect (producer), omn-tech-lead (accepting owner, Design Gate)
- Related Work Items: CKA-04; run run-919c5d5cf156; the plan's T-002; the plan's R-006

## Context

Problem statement: the check that no gate-matrix row is producer-only must read gate
ownership, phase producers, and role aliases with exactly the semantics the runtime
enforces; any divergence either lets a producer-only row pass undetected or fails a
decidable row falsely (the plan's R-006).

Business and technical constraints: C-005 requires the alias reading to be the same source
the runtime reads; C-001 forbids altering `producer_aliases` or the gate-matrix semantics;
C-002 fixes the deliverable as a test module discovered without CI configuration change;
C-003 requires structure-only binding.

Current architecture baseline: F-001 establishes `producer_aliases` in
`runtime/framework_runtime.py` (line 1265); F-004 establishes the importable readers
`parse_gate_matrix` (line 1238), `parse_phase_model` (line 754), and `phase_gates`
(line 1257); F-003 establishes the Phase Model tables of all eight active workflows as the
declared producer source; F-009 establishes the existing tests-to-runtime import pattern.

## Decision

Selected option: O-001.

Decision statement: `tests/test_content_contracts.py` imports `producer_aliases`,
`parse_gate_matrix`, `parse_phase_model`, and `phase_gates` from
`runtime/framework_runtime.py` and derives, for every active workflow, each Phase Model
row's producing agent (Owner Agent cell) and gate names; it asserts that every
Phase-Model-named gate resolves in the gate matrix, and that each such gate's owner set
minus `producer_aliases(producer)` is non-empty. No alias expansion, matrix parsing, or
Phase Model parsing is reimplemented in the test suite. Matrix rows named by no Phase Model
row are inert to the runtime and are reported as skipped (D-005 in the design package).

Scope of impact: M-001, M-002 (read-only consumer), M-007, M-008.

## Alternatives Considered

1. O-002 — self-contained test module reimplementing the matrix, Phase Model, and alias
parsing locally
- Benefits: no coupling to runtime function names; the test survives runtime refactors
  untouched.
- Risks: silent semantic drift — a change to the runtime's alias or parse semantics leaves
  the check asserting a property the runtime no longer enforces, which is precisely the
  failure the check exists to prevent.
- Why not selected: violates hard constraint C-005; eliminated in the evaluation table.

2. O-003 — new runtime helper module hosting the check logic, with a thin test delegating
to it
- Benefits: check logic sits beside the readers it consumes; the test module stays minimal.
- Risks: introduces a structural component for a capability the test suite already hosts;
  widens the runtime module set maintainers and validators track.
- Why not selected: satisfies the hard constraints but scores lower on reuse leverage
  (criterion 3); the hosting capability had a suitable existing candidate.

## Consequences

Positive outcomes expected: the pinned property and the enforced property are
definitionally identical; a producer-only row fails the same alias arithmetic the runtime
would apply; the plan's R-006 is closed by construction.

Tradeoffs accepted: the four runtime reader functions become load-bearing for the test
suite; renaming or re-signaturing any of them breaks the suite loudly (R-002 in the design
package). The loud break is preferred over silent divergence.

Risks introduced: R-002 (coupling to reader names and signatures); R-005 (inert matrix rows
remain unpinned and are surfaced as skips rather than failures).

## Validation Plan

Metrics to monitor: count of skipped inert rows reported by check 1 per run (expected
stable at its current value; growth signals Phase Model or matrix drift).

Verification checkpoints: P-002 confirms the import binding works under the hermetic
temporary-root pattern before fixtures are authored; P-005 demonstrates a producer-only
fixture failing through the imported alias arithmetic, exercised in both alias directions
(`omn-` prefixed and de-prefixed).

Rollback or reversal conditions: if the runtime reader surface is deliberately restructured,
rebind the imports in one place; if import binding proves unviable under the hermetic
pattern (P-002 fails), fall back to O-003 — relocating the shared logic into the runtime —
which preserves C-005; O-002 remains prohibited.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
