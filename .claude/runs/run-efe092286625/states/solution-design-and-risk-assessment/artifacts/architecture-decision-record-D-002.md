# Architecture Decision Record

## Metadata

- ADR ID: D-002
- Title: Declare the payload's YAML dependency in the distribution's install contract
- Date: 2026-08-28
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; producer excluded from acceptance)
- Related Work Items: CKA-01 (adoption backlog under `docs/`, Epic A — verification baseline); run run-efe092286625; technical design CKA-01-technical-design; plan tasks T-001, T-002, T-003

## Context

- Problem statement: the installed framework payload's runtime files import the third-party
  module named `yaml` at module top level (F-008) and are executed with the same interpreter
  that runs the CLI (F-010), but the distribution declares an empty dependency set (F-001)
  and the published documentation claims the tool is standard-library only (F-002). A clean
  install therefore produces a runtime that dies on its first import while the documentation
  says nothing is missing.
- Business and technical constraints: C-008 (hard, forcing: the ticket's verbatim
  deliverable requires `pyyaml` declared in `dependencies` in `pyproject.toml` so a clean
  install pulls it); C-007 (documentation states the true footprint, handbook agrees); C-004
  (preservation of existing certified behavior); C-009 (smallest compliant change,
  negotiable).
- Current architecture baseline: F-001 (empty declared dependency set); F-002 (the false
  documentation claim); F-007 (the CLI package itself uses the standard library only); F-014
  (the YAML module is the only third-party top-level root anywhere in the payload); F-018
  (the root module `yaml` is provided by the distribution `pyyaml`).

## Decision

- Selected option: O-004 — the only provisioning option in the package's evaluation table
  (5.2) that satisfies hard constraint C-008, which forces the selection.
- Decision statement: the CLI distribution declares `pyyaml` as an install-time dependency
  on behalf of the payload runtime files it installs and executes with the same interpreter.
  The CLI package itself remains standard-library only (F-007); documentation (`README.md`)
  and the HTML handbook (`user-guide.html`) are corrected to state this true footprint.
- Scope of impact: M-002 (`pyproject.toml` distribution metadata, contract-change), M-003
  (`README.md`), M-004 (`user-guide.html`); no code module changes under this decision.

## Alternatives Considered

1. O-005 — vendor a minimal YAML parser into the framework payload
- Benefits: keeps the distribution's declared dependency set empty; installs need nothing
  from the package index.
- Risks: creates new structure the project must maintain; duplicates a capability the
  ecosystem provides; changes payload files the additive posture and C-009 disfavor
  touching.
- Why not selected: eliminated on C-008 — the ticket's verbatim deliverable requires the
  declaration, not a substitute; also rejected in the package's reuse survey (section 7).

2. O-006 — leave the dependency undeclared and rely on detection (D-001) alone
- Benefits: no install-contract change; no supply-chain declaration.
- Risks: clean installs remain broken on first run; the acceptance criterion that a
  clean-venv install pulls the dependency (S-008) is unmet; documentation truth is
  achievable only by documenting a manual install step.
- Why not selected: eliminated on C-008 — detection exists to catch broken environments,
  not to substitute for a working install.

## Consequences

- Positive outcomes expected: a clean-environment install produces a runnable runtime; the
  install contract, the documentation, and the actual import behavior of the payload agree
  with one another; the dependency the runtime always had becomes visible and manageable.
- Tradeoffs accepted: the distribution is no longer zero-dependency; installs require the
  package index (or a mirror) to serve one additional distribution; the documentation claim
  loses its simplicity and must distinguish the CLI package (standard library only, F-007)
  from the installed payload (requires the YAML module, F-008).
- Risks introduced: R-003 (installs in restricted or offline environments), R-006
  (supply-chain exposure of the declared distribution).

## Validation Plan

- Metrics to monitor: clean-venv install resolution (the declared dependency appears in the
  resolved set) and first invocation of the installed CLI; documentation review of
  `README.md` and `user-guide.html` against the declared dependency set.
- Verification checkpoints: P-002 (declaration precedes the corrected documentation claim),
  P-004 (handbook agreement follows the corrected statement), P-005 (recorded install and
  broken-environment evidence).
- Rollback or reversal conditions: if the declaration must be withdrawn, removing it returns
  the metadata to its prior shape; already-installed environments keep functioning, and the
  D-001 detection finding remains the operator's signal for environments where the module is
  absent. Documentation reverts with the same change.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
