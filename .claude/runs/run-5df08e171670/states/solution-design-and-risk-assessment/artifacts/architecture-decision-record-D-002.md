# Architecture Decision Record — D-002

## Metadata

- ADR ID: D-002
- Title: A process detached from the run owns the recording and watches its target
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan tasks T-006, T-007, T-010

## Context

- Problem statement: a recording must run for the whole duration of a run, survive whatever
  the run does, and be watched while it runs so that material which is not of the target
  window can be excluded — none of which a component owned by the run's own process can
  promise.
- Business and technical constraints: C-004 (nothing in the layer may raise into the run it
  observes), C-005 (only the target window may be recorded, and publication safety outranks
  completeness), C-006 (external integration behind an adapter boundary, outside the execution
  path), C-008 (a fault here is not a run failure and must not enter failure classification).
- Current architecture baseline: F-016 (two backends, with the encoder backend capturing the
  target window's rectangle), F-017 (the session refuses to start unless the target is the
  foreground window; a detached helper samples foreground state while filming, merges spans
  closer than one second into one interruption, and records the occluded spans for exclusion),
  and the reuse survey's finding that the runtime leases adapters synchronously and owns no
  background process, so no such facility existed to reuse.

## Decision

- Selected option: O-001.
- Decision statement: the recording is owned by a process detached from the run's own process.
  That process starts the capture, holds it open while the run proceeds, samples whether the
  target is still the window on screen, merges and records the spans during which it was not,
  and finalises the recording when stopped. The run's process starts and stops it and never
  owns it.
- Scope of impact: M-008, M-009, M-011.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: one fewer process to start, stop, and orphan; no cross-process handshake.
- Risks: the recording shares the run's lifetime and its failure modes, and no independent
  observer exists to notice that the target stopped being the window on screen.
- Why not selected: this is the alternative this decision displaces. It ties O-001 on hard
  constraints, impact surface, reuse leverage and migration burden, and loses on criterion 4:
  it makes C-004 a discipline rather than a structural property, and removes the mechanism
  C-005 depends on.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: none bearing on recording ownership.
- Risks: as recorded in the evaluation table.
- Why not selected: eliminated by C-003 before ownership is reached.

3. O-004 — reconstruct after the fact from persisted evidence only, with no camera
- Benefits: no recording process to own at all.
- Risks: no material of the application.
- Why not selected: eliminated by C-015.

4. O-005 — a general run-telemetry pipeline with the presentation as a consumer
- Benefits: none bearing on recording ownership.
- Risks: a durable interface to own.
- Why not selected: eliminated by C-007.

5. O-006 — draw a synthetic dashboard instead of filming
- Benefits: no capture process and no publication exposure.
- Risks: the picture is a diagram of the run.
- Why not selected: eliminated by C-015.

## Consequences

- Positive outcomes expected: a recording that cannot take the run down with it, satisfying
  C-004 structurally; an observer that can watch the target independently of what the run is
  doing, which is what makes the exclusion in C-005 possible; a recording that survives the
  end of the command that started it, which is what allows filming to open at run acceptance
  and close after the final gate.
- Tradeoffs accepted: a second process exists while filming and must be stopped; an abnormally
  terminated run can orphan it; the cross-process boundary means the run learns about capture
  state through the capture manifest rather than directly.
- Risks introduced: R-005 (an orphaned recording process holding the target and a manifest
  left in a recording state), R-001 (an interruption shorter than the sampling period escaping
  the exclusion).

## Validation Plan

- Metrics to monitor: the recorded occluded spans against the finished presentation; the
  capture manifest's terminal state after a normal run and after an aborted run.
- Verification checkpoints: P-004 (exclusion verified on a deliberately obscured run before
  any presentation is offered for release); P-006 (the stop path exercised on an aborted run
  as part of fault absorption); P-007 (a complete lifecycle filmed from acceptance to final
  gate decision).
- Rollback or reversal conditions: reverse if the detached process is shown to affect the
  observed run's status, artifacts, gate decisions, or recovery outcome, or if orphaning
  proves unrecoverable without operator action. Reversal is the removal of the capture
  modules; the layer then falls to its drawn substitute under D-006.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
