# Architecture Decision Record — D-004

## Metadata

- ADR ID: D-004
- Title: Absorb every observation-layer fault inside the layer and keep it out of failure classification
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan tasks T-010, T-011

## Context

- Problem statement: the layer sits on the hot path of a governed run and calls out to
  external tools that may be absent, misconfigured, or failing. A fault there must not change
  what the run does, what it records, or how it recovers — and it must not be silent either.
- Business and technical constraints: C-001 (additive only; no change to recovery
  classification), C-004 (nothing in the layer may raise into the run it observes), C-008 (a
  fault here is not a run failure and must not enter the failure-classification machinery; it
  is caught and logged).
- Current architecture baseline: F-012 (every runtime site reaching the layer is guarded and
  imports inside the guard), F-011 (the layer's public surface is the set of entry points at
  which absorption must happen), and the reuse survey's rejection of the runtime's failure
  classification machinery as a candidate, precisely because C-008 forbids reaching it.

## Decision

- Selected option: O-001.
- Decision statement: every entry point of the observation layer catches whatever it raises
  and writes it to the layer's own log in the run's observation directory, then returns
  normally. No fault in the layer is classified, no recovery policy is consulted, no retry is
  scheduled by the runtime, and no run status, artifact, gate decision, or recovery outcome
  changes because of one. The absence that results is recorded, so a broken observation path
  produces a run indistinguishable from an unrecorded run plus a log entry, never a degraded
  run and never a silent one.
- Scope of impact: M-001, M-016; the property is depended on by M-003, M-005, M-008, M-011.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: a single process makes the fault surface easier to enumerate.
- Risks: a fault in an in-process recorder has a path into the run's own process that no
  catch-and-log discipline fully closes.
- Why not selected: rejected under D-002; it weakens the very property this decision makes
  structural.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: a fault could be localised to the site that produced it.
- Risks: absorption would have to be repeated at every instrumented site, and each site is a
  new opportunity to omit it.
- Why not selected: eliminated by C-003; and it multiplies the absorption surface rather than
  confining it.

3. O-004 — reconstruct after the fact from persisted evidence only
- Benefits: the strongest possible containment, since nothing runs during the run.
- Risks: no material of the application.
- Why not selected: eliminated by C-015.

4. O-005 — a general run-telemetry pipeline with the presentation as a consumer
- Benefits: a telemetry pipeline would carry its own failure semantics.
- Risks: those semantics would be a second recovery policy the framework must own, against
  C-001 and C-008.
- Why not selected: eliminated by C-007.

5. O-006 — draw a synthetic dashboard instead of filming
- Benefits: no external capture, so a narrower fault surface.
- Risks: the picture is a diagram of the run.
- Why not selected: eliminated by C-015.

## Consequences

- Positive outcomes expected: the observed run is provably unaffected, which is what `AC-004`
  asks to be demonstrated; the framework's recovery classification is untouched, which is what
  keeps C-001 true; every absorbed fault leaves a written trace, so the failure is visible
  without being escalated.
- Tradeoffs accepted: a presentation can be quietly incomplete — the run succeeds and the
  output is missing or degraded, and only the layer's own log says why; a genuine defect in
  the layer can persist unnoticed across runs because nothing escalates it; the layer's log is
  therefore the only place its health is visible.
- Risks introduced: R-007 (a crashed build leaving a claimed-but-absent output with no
  automatic retry), and the absorption property is what R-005 and R-004 are tested against.

## Validation Plan

- Metrics to monitor: the observed run's status, artifacts, gate decisions, and recovery
  outcome compared against an unrecorded run of the same work; the presence of a log entry for
  every induced fault.
- Verification checkpoints: P-006 (a fault induced at each absorption site before the
  recording path is exercised on a run whose outcome matters); P-005 (the unrequested path,
  which shares the same guards).
- Rollback or reversal conditions: reverse if an induced fault is shown to change the observed
  run in any of the four respects above, or if absorbed faults prove to accumulate unnoticed
  to the point that the layer's output cannot be trusted. Reversal is not a change of policy
  but the removal of the guarded sites.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
