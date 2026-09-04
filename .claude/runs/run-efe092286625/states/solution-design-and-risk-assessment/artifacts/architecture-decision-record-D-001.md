# Architecture Decision Record

## Metadata

- ADR ID: D-001
- Title: Static top-level import resolution inside the existing verification helper
- Date: 2026-08-28
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; producer excluded from acceptance)
- Related Work Items: CKA-01 (adoption backlog under `docs/`, Epic A — verification baseline); run run-efe092286625; technical design CKA-01-technical-design; plan tasks T-004, T-005, T-006

## Context

- Problem statement: the `validate` and `doctor` commands certify an installation as healthy
  even when the environment lacks a third-party module the installed runtime files import at
  module top level, because the per-file verification helper only compiles those files and
  never resolves their imports (technical design facts F-003, F-008). A broken installation
  must instead produce a finding that names the missing module, in both commands, without
  altering any gate-decision or human-approval path.
- Business and technical constraints: C-001 (additive check only — no change to
  `record_gate_decision`, gate matrix semantics, producer exclusion,
  `runner._require_approval`, or any human-block path); C-002 (finding in both commands,
  naming the module); C-003 (top-level imports only); C-004 (healthy installation preserved
  with no new findings); C-005 (verification executes no payload code and writes nothing);
  C-006 (report, never raise); C-009 (smallest compliant change, negotiable).
- Current architecture baseline: F-004 and F-012 (the helper already visits every
  descriptor-named entrypoint and validator); F-005 (`doctor` reuses the shared
  `run_validation` path); F-006 (shared report model with stable finding codes); F-009
  (payload files import siblings at top level, resolved by their own execution-time path
  insertion); F-010 (the runner executes the runtime with the same interpreter that runs the
  CLI); F-011 (the codebase's recorded precedent for reading the runtime statically rather
  than importing it); F-014 (the only third-party top-level root anywhere in the payload is
  the YAML module).

## Decision

- Selected option: O-001.
- Decision statement: missing-dependency detection is implemented as a static step inside
  the existing per-file verification helper on the shared validation path. After a
  successful compile, the step derives the checked file's module-top-level import roots and
  resolves each against two sources: the executing environment's import machinery, and
  sibling payload files in the checked file's own directory. A root that resolves through
  neither source produces one ERROR finding through the existing report model, carrying a
  new stable finding code and naming the checked file and the unresolved module; the healthy
  path emits nothing, and no resolution failure is raised out of verification.
- Scope of impact: M-001 (`omn_agent/validator.py`), with observable effect on the
  `validate`/`doctor` report stream; M-005 through M-008 verified unchanged.

## Alternatives Considered

1. O-002 — standalone check walking every payload file under the installed runtime directory
- Benefits: individually checks payload files the bootstrap descriptor does not name, closing
  the residual gap recorded as R-004.
- Risks: enlarges the false-finding exposure on healthy installations (C-004), abandons the
  existing check site and descriptor enumeration (reuse leverage 5 versus 7), and adds a
  second enumeration that can drift from the descriptor.
- Why not selected: rejected on the recorded criteria — reuse leverage 5 versus 7 and higher
  C-004 exposure, violating no hard constraint. It adds no detection value for the stated
  acceptance criteria: the single undeclared third-party root (F-014) is imported by
  descriptor-named files (F-008).

2. O-003 — dynamic probe: verification imports or executes each runtime file and reports the observed import failure
- Benefits: exercises the exact failure the operator would hit, including transitive
  resolution.
- Risks: runs payload top-level code (side effects) at verification time; pulls transitive
  resolution beyond the bounded scope.
- Why not selected: eliminated on hard constraint C-005 (verification must not execute
  payload code), and it exceeds the C-003 boundedness the approved scope fixed.

## Consequences

- Positive outcomes expected: a dead runtime is reported as broken with the missing module
  named, in both commands, from one shared check path; healthy installations are untouched;
  the verification baseline becomes trustworthy enough for the dependent CI-gating work.
- Tradeoffs accepted: detection is blind below module top level (C-003, scope exclusion
  X-002) and does not individually check payload files outside the descriptor-named set.
- Risks introduced: R-001 (sibling-rule miss producing a false finding on a healthy
  install), R-002 (verification run from a different environment than the executing one),
  R-004 (future third-party import confined to a non-descriptor-named file), R-005 (tests
  asserting exact healthy output).

## Validation Plan

- Metrics to monitor: finding set of `validate`/`doctor` on a healthy installation (must be
  unchanged pre/post); presence and wording of the missing-module finding in a
  dependency-less environment; existing test suite and proof-script verdicts.
- Verification checkpoints: P-001 (detection contract fixed), P-003 (healthy-environment
  silence demonstrated, including sibling imports), P-005 (broken-environment evidence for
  both commands recorded).
- Rollback or reversal conditions: if healthy installations report false findings that the
  sibling rule cannot be corrected to absorb, remove the detection step and its finding
  code, returning verification to compile-only behavior; no stored state or gate behavior
  exists to unwind.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
