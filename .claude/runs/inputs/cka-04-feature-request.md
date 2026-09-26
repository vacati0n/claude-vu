# Feature Request — CKA-04: Content-contract tests over governance prose

## Source

Ticket CKA-04 in the adoption backlog under `docs/` (Epic A — Verification baseline,
Days 0–30). Source recommendation: R5 of the ClaudeKit Adoption Review (2026-08-27).
Type: Task. Priority: High. Effort: S. Depends on: nothing (lands with or before CKA-03,
which is already delivered as `.github/workflows/verify.yml`).

## Request

The runtime depends on structural properties of governance prose that nothing pins today.
`framework_runtime.py` reads gate ownership from `workflows/workflow-gate-matrix.md` and
enforces the Producer Exclusion Rule through `producer_aliases()`; a prose edit that leaves
a gate row owned only by its producing role (through any alias) creates an undecidable gate
and no test notices. Superseded agent specifications (`agents/architect.md`,
`agents/planner.md`) carry their supersession marker in their first heading; a rewrite that
drops it silently revives a dead contract. Agent contract modules must never carry coercive
auto-chain language (the claudekit failure mode: contract prose instructing an agent to
proceed past approval gates automatically), and the four orphaned root governance docs
(`working-memory.md`, `rule-engine.md`, root `quality-gates.md`, `decision-matrix.md`) are
receiving `Status:` banners under CKA-05 that must then be impossible to drop.

Deliverable: a new `tests/test_content_contracts.py` (stdlib `unittest`, discovered by the
CKA-03 CI test surface with no config change) asserting structure the code depends on:

1. Every `workflow-gate-matrix.md` gate row names at least one owner outside
   `producer_aliases(producer)` for the phase's producing agent — i.e. no row is
   producer-only under the Producer Exclusion Rule's alias reading.
2. Superseded agent files carry their status marker on line 1.
3. The four root governance docs carry a `Status:` banner (the CKA-05 coupling: this
   check must be authored now and must be green on the current tree — the scope decision
   on how to satisfy that coupling belongs to scope-and-acceptance; the backlog offers
   two admissible resolutions: land the four CKA-05 banners in this change, since CKA-05
   is S-effort, dependency-free, and its own acceptance criterion is "present and pinned
   by CKA-04", or gate the check so it activates when the first banner lands).
4. No agent contract module under `agents/*/` matches coercive auto-chain patterns
   (e.g. instructions to skip, bypass, or auto-approve a gate, or to proceed without
   approval).

Assert on structure (table cells, first-line markers), not sentences, so wording edits
that preserve structure stay free.

## Acceptance criteria (from the ticket, verbatim)

- Mutating a fixture gate matrix to a producer-only owner row fails a test.
- Suite runs green against current tree once CKA-05 lands.

## Constraints

- Additive change only: the ticket list forbids altering `record_gate_decision`, the
  gate matrix semantics, producer exclusion, `runner._require_approval`, or any
  human-block path. This ticket adds tests (and, if scoped in, four status banners);
  it changes no runtime behavior.
- Assertions bind to structure the code reads, not to prose wording.
- Definition of done for every ticket in the backlog: `tests/` green, all `verify_*.py`
  proof scripts PROVEN, no change to gate-decision behavior, and where docs were
  touched, `user-guide.html` updated to match.

## Priority and deadline

High priority; Phase 1 (Days 0–30) of the adoption plan. CKA-16 (anti-rationalization
tables) later extends this suite, and CKA-05's acceptance criterion is pinned by it.
