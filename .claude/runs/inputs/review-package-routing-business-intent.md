# Business Intent: Route the Review Package

Supplied by the operator for framework change `FC-001`, routed as change class
`capability-addition` by `config/self-hosting-profile.md`. This states intent and acceptance
expectation only. It defines no solution, names no module, and takes no design decision.

## Why the change is wanted

The framework contracts an artifact it never asks any phase to produce. `templates/review-package.md`
is registered, `runtime/review_package_validator.py` decides its conformance, and
`reports/validation-recovery-hardening-report-2026-08-18.md` records the consequence plainly:
the artifact is "not yet named in any Phase Model's Output Artifact column, so no phase routes
it". `runtime/README.md` carries the same statement as known gap 7.

A contracted artifact that nothing emits is a capability the framework claims and does not
offer. Every other artifact type it validates is named by a phase.

## Outcome expected

1. A phase of the review lifecycle declares the review package as the artifact it emits.
2. The Validation Engine's coverage proof counts that artifact as routed rather than as an
   exception, so the count of contracted-but-unrouted artifact types reaches zero.
3. The recorded gap is closed in the record that raised it, rather than left standing while the
   behaviour changes underneath it.

## Acceptance intent

- One phase, not several, names the artifact. Two phases emitting one artifact type would
  reintroduce the ambiguity the Phase Model exists to remove.
- The phase that names it is the phase whose declared work the artifact already describes. No new
  phase is introduced and no phase changes owner.
- Registry coverage, validator coverage, and every previously proven run still verify after the
  change, with unresolved counts unchanged or lower.

## Constraints the business places on the change

- Gate ownership is not in scope. Nothing in this intent authorizes a change to
  `workflows/workflow-gate-matrix.md`.
- No agent gains or loses a contract. If naming the artifact would require an owning agent to
  declare a new output, that is a decision to surface, not a change to make silently.
- The change must not claim the phase becomes executable. Whether a phase can be dispatched is
  decided by capability registration, which this change does not perform.

## Open to the design

- Which review phase is the correct emitter, and on what ground.
- Whether the Input column of any downstream phase must change to consume the artifact by name.
- What the change implies for the phase's blocked reason, if anything.
