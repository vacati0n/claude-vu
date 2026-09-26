# Architecture Decision Record — D-005

## Metadata

- ADR ID: D-005
- Title: Compile once per run, claimed before the build, and only when nothing is left to decide
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan tasks T-013, T-014, T-015

## Context

- Problem statement: the presentation must be produced without a further command, exactly
  once, and only after the run genuinely has nothing left to decide. Two properties of the
  runtime make that harder than it sounds: the event that means "the last phase is done" fires
  before the gate closing that phase is decided, and more than one event legitimately means
  "the run is finished".
- Business and technical constraints: C-004 and C-008 (a fault in the compilation path is
  absorbed, not classified), C-011 (compilation occurs exactly once, after the final gate
  decision), C-010 (everything written derives from the install-prefix variable and stays
  under the run's own directory).
- Current architecture baseline: F-015 (every phase committed and every gate decided, read
  from the run's own state store rather than the ledger's summary, because the summary counts
  phases and a gate is not a phase), F-014 (compilation claimed by an exclusive file creation
  performed before the build), F-001 (the emission point at which finishing events arrive).
  The reuse survey records the ledger's completion summary as a `rejected` candidate for
  exactly the reason F-015 gives.

## Decision

- Selected option: O-001.
- Decision statement: on each finishing event, the layer asks the run's own state store
  whether every phase is committed and every gate decided. Only when that holds does it stop
  any recording still running and compile. The right to compile is claimed by creating a claim
  file exclusively, and the claim is written before the build rather than after, so a second
  finishing event finds the claim taken and a crashed build is not retried automatically on
  the next event. The camera therefore stops on the event that leaves nothing undecided,
  which is after the final gate decision and not after the last phase.
- Scope of impact: M-001, M-008, M-011.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: stopping the camera would need no cross-process call.
- Risks: the recording would end with the run process, which may end before the final gate is
  decided, cutting the presentation short of the beat it is building towards.
- Why not selected: rejected under D-002, and it would make this decision's stopping point
  unreachable.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: a phase-local site could signal its own completion.
- Risks: a gate is not a phase, so phase-local signals cannot establish that nothing is left to
  decide.
- Why not selected: eliminated by C-003, and it does not solve the problem this decision
  addresses.

3. O-004 — reconstruct after the fact from persisted evidence only
- Benefits: compilation naturally occurs after everything, with no trigger to get right.
- Risks: it requires a further command, against C-011's "without a further command", and there
  is no camera to stop.
- Why not selected: eliminated by C-015.

4. O-005 — a general run-telemetry pipeline with the presentation as a consumer
- Benefits: a pipeline could own a completion signal reusable by other consumers.
- Risks: a durable interface to own and version.
- Why not selected: eliminated by C-007.

5. O-006 — draw a synthetic dashboard instead of filming
- Benefits: nothing to stop, so only the compile-once half of the problem remains.
- Risks: the picture is a diagram of the run.
- Why not selected: eliminated by C-015.

## Consequences

- Positive outcomes expected: exactly one presentation per recorded run, with no further
  command, satisfying C-011 and `AC-007`; a recording whose end follows the final gate
  decision, so the approval the whole presentation builds towards is in the footage; the same
  minutes of encoding are never spent twice for the same result.
- Tradeoffs accepted: a build that crashes leaves a claim in place and therefore a run with no
  presentation and no automatic retry — chosen deliberately, because automatically retrying a
  crashing encode repeats the cost for the same outcome; re-cutting after such a failure is a
  manual act against the existing recording; the decision depends on the run's state store
  being an accurate account of gates, which is a property of the runtime rather than of this
  layer.
- Risks introduced: R-007 (a claimed-but-absent output), R-012 (an encode running while the
  operator believes the run is finished).

## Validation Plan

- Metrics to monitor: the count of finished presentations per recorded run; the timestamp of
  the recording's end against the timestamp of the final gate decision; the presence of the
  claim file against the presence of the output.
- Verification checkpoints: P-007 (one complete recorded lifecycle, confirming a single output
  and a recording whose end follows the final gate decision, on a run that emits more than one
  finishing event); P-009 (re-cutting from the existing recording, which is also the manual
  recovery from a crashed build).
- Rollback or reversal conditions: reverse the claim-before-build position if crashed builds
  prove common enough that a run with no presentation is the usual outcome; reverse the
  state-store trigger if the store is shown not to reflect gate decisions reliably, in which
  case the trigger has no sound source and compilation returns to being an explicit command.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
