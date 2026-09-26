# Architecture Decision Record — D-003

## Metadata

- ADR ID: D-003
- Title: Select the capture backend by probing at start, with the window-rectangle backend as the recorded fallback and its residual carried as an accepted gap
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan tasks T-004, T-006, T-016, T-017. This record settles the architectural half of the capture-path question the execution plan carries, whose remaining operator election is Q-001 in the design package.

## Context

- Problem statement: the presentation must be material of the application performing the run.
  Two capture paths are available, they leave different residuals, and the preferred one is
  not reachable on the operator host as configured. The question is which path the
  architecture commits to, and what happens to the acceptance criterion when the reachable
  path cannot fully establish what the preferred path would.
- Business and technical constraints: C-002 (no new mandatory dependency, and the framework
  installs or configures no external tool on the operator's host), C-005 (only the target
  window may ever be recorded; publication safety outranks completeness), C-013 (delivered
  behaviour is judged against the acceptance criteria as written; no criterion is softened or
  reworded), C-015 (every segment is material of the application performing that run).
- Current architecture baseline: F-007 (the recording application is installed with its
  control server bundled but disabled, and its configuration is not writable by the agent),
  F-009 (the target belongs to a GPU-composited desktop application), F-016 (two backends,
  preferred and fallback; the encoder's window-level input is deliberately unused because a
  GPU-composited window returns black frames, so the window's rectangle is captured instead),
  F-017 (the session refuses to start unless the target is the foreground window, and occluded
  spans are sampled, merged, and recorded for exclusion).

## Decision

- Selected option: O-001.
- Decision statement: the capture adapter probes the recording application's control server
  when a session starts. Where the server answers, the control-server backend is used and
  captures the window itself, provisioned into the layer's own scene collection and profile
  and never into the operator's. Where it does not answer, the encoder backend records the
  rectangle the target window occupies, having first raised the target and refused to start
  unless it is the foreground window, and the occluded spans are recorded for exclusion. On
  the operator host as configured (F-007) the server does not answer, so the encoder backend
  is the path in force.

  The consequence for acceptance is recorded rather than repaired. `AC-008` — that every
  segment of a finished presentation is material of the application performing that run —
  stands exactly as written. Under the encoder backend it is satisfied for every span the
  helper confirms the target was the window on screen, and a residual remains for the
  intervals between foreground samples, in which the rectangle's content is not positively
  established as the target window. That residual is **an accepted, recorded gap against the
  criterion as written**. The criterion is not narrowed to "the rectangle the window
  occupies", and it is not reworded to match the backend that happens to be reachable; C-013
  forbids both, and this decision records the gap instead so that a reader can see precisely
  what was and was not established.
- Scope of impact: M-007, M-008, M-009, M-011.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: fewer moving parts in the capture path.
- Risks: no independent observer of the target while the run proceeds, which is the mechanism
  that bounds this decision's residual to the sampling interval.
- Why not selected: rejected under D-002; without the detached observer, the residual is not
  bounded at all and the encoder backend could not be offered as a fallback.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: none bearing on capture.
- Risks: as recorded in the evaluation table.
- Why not selected: eliminated by C-003 before capture is reached.

3. O-004 — reconstruct after the fact from persisted evidence only, with no camera
- Benefits: no capture residual of any kind, and no publication exposure.
- Risks: nothing of the application is ever recorded.
- Why not selected: eliminated by C-015. It removes the residual by removing the evidence,
  which is the opposite of what the criterion asks for.

4. O-005 — a general run-telemetry pipeline with the presentation as a consumer
- Benefits: none bearing on capture.
- Risks: a durable interface to own.
- Why not selected: eliminated by C-007.

5. O-006 — draw a synthetic dashboard instead of filming
- Benefits: no capture at all, so no occlusion, no residual, and no publication exposure.
- Risks: the picture is a diagram of the run, not the run.
- Why not selected: eliminated by C-015, and rejected by the requester when it was first
  built. It survives only as the lowest rung of the substitution ladder in D-006, never as the
  primary path.

## Consequences

- Positive outcomes expected: a capture path exists on a host with no configuration performed
  by the framework, satisfying C-002; the preferred path remains reachable the moment an
  operator enables the control server through the application's own interface, with no change
  to the framework; the exclusion mechanism makes publication of non-target material a
  recorded omission rather than a silent inclusion, satisfying C-005.
- Tradeoffs accepted: on the host as configured, window identity is established by sampling
  rather than by the capture mechanism itself, leaving the residual this record accepts; the
  evidence produced for the segment-level criterion describes whichever backend produced the
  footage, so a later change of backend invalidates it; the acceptance criterion is carried
  with a gap rather than reported as met.
- Risks introduced: R-001 (an interruption shorter than the sampling period reaching a
  finished presentation), R-010 (the backend changing between the evidence and the
  presentation), R-011 (the accepted gap not being carried forward with the evidence, or the
  criterion being reworded to close it), R-014 (the disclosure position being judged
  insufficient at review).

## Validation Plan

- Metrics to monitor: the backend recorded in the capture manifest for each session; the count
  and total duration of recorded occluded spans; the correspondence between those spans and
  what the finished presentation contains.
- Verification checkpoints: P-002 (the backend in force recorded before any segment-level
  evidence is produced); P-004 (exclusion verified on a deliberately obscured run before any
  presentation is offered for release). The accepted gap is carried as a named condition of
  both, never as an amendment to the criterion.
- Rollback or reversal conditions: reverse the fallback if the residual is judged unacceptable
  at the Design Gate, in which case the control-server backend becomes the only capture path
  and the capability degrades to the substitute in D-006 on any host where the server is
  disabled. Reverse the acceptance of the gap if the operator enables the control server
  (Q-001), in which case the window-identity residual disappears and the P-002 evidence is
  re-produced on the backend actually in use.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
