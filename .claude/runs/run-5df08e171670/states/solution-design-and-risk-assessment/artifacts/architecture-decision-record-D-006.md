# Architecture Decision Record — D-006

## Metadata

- ADR ID: D-006
- Title: Degrade through a recorded substitution ladder whose lowest rung draws the run
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan tasks T-023, T-024

## Context

- Problem statement: the capability depends on external tools for capture, encoding, image
  composition, and speech, and each of them is absent on some host. None may become a
  requirement of the framework, and an absence must not look like a failure or be inferred by
  the reader from a missing output.
- Business and technical constraints: C-002 (no new mandatory dependency, and the framework
  installs or configures nothing on the operator's host), C-006 (external integration behind
  an adapter boundary), C-008 (an absence is not a fault and never reaches failure
  classification), C-015 (every segment of a finished presentation is material of the
  application performing that run).
- Current architecture baseline: F-008 (no system encoder on the operator host; an image
  library present; platform speech voices available), F-007 (the recording application's
  control server disabled), F-016 (two capture backends), F-010 (the drawn substitute exists
  as three delivered modules: a dashboard renderer, an output builder, and a deck builder).

## Decision

- Selected option: O-001.
- Decision statement: every external tool sits behind an adapter that tries the available
  options in a fixed order and records which one produced the result. Capture falls from the
  control-server backend to the encoder backend (D-003); speech falls through the platform
  engine chain to no narration; output falls from an encoded film to an animated image and
  then to a self-contained deck; frame composition falls back when the image library is
  absent. The lowest rung, reached when nothing was filmed at all, draws the run from its own
  marker record instead. Every fall is written into the layer's manifests and log, so the
  substitution is a recorded fact and never an inference from a missing file.

  The drawn substitute is the fallback and never the primary. It does not satisfy C-015,
  because a drawing of a run is not material of the application performing it; a presentation
  produced on that rung is a reduced output, and the two requirements coexist without
  contradiction only because the reduced output is never offered as the finished one.
- Scope of impact: M-005, M-008, M-012, M-013, M-014.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: none bearing on degradation; the ladder would be identical.
- Risks: none bearing on degradation.
- Why not selected: rejected under D-002 on grounds unrelated to this decision.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: none bearing on degradation.
- Risks: as recorded in the evaluation table.
- Why not selected: eliminated by C-003.

3. O-004 — reconstruct after the fact from persisted evidence only
- Benefits: the fewest external dependencies of any option, so the shallowest ladder.
- Risks: it is permanently on the lowest rung, since nothing is ever filmed.
- Why not selected: eliminated by C-015. It makes the reduced output the only output.

4. O-005 — a general run-telemetry pipeline with the presentation as a consumer
- Benefits: none bearing on degradation.
- Risks: a durable interface to own.
- Why not selected: eliminated by C-007.

5. O-006 — draw a synthetic dashboard instead of filming
- Benefits: no external capture dependency at all.
- Risks: the picture is a diagram of the run.
- Why not selected: eliminated by C-015 as a primary path. This decision is precisely what
  preserves it in its correct place: the bottom of the ladder, reached when nothing was
  filmed, and never the finished output.

## Consequences

- Positive outcomes expected: the framework acquires no mandatory dependency, so it installs
  where it installed before, satisfying C-002; every absence is recorded, which is what
  `AC-012` asks to be demonstrated; a recorded run always yields something, so a missing tool
  never produces a failed run.
- Tradeoffs accepted: a presentation can be markedly weaker than intended while still counting
  as produced, and only the recorded substitution says so; the lower rungs are exercised
  rarely, so their defects surface late; the drawn substitute is three modules of structure
  that exist solely for the case where the primary path produced nothing.
- Risks introduced: the ladder's lower rungs cannot be demonstrated on a fully equipped host,
  which is the exposure the execution plan carries as a host-variation dependency and which
  P-008 sequences; a reduced output mistaken for a finished one bears on the release question
  Q-005.

## Validation Plan

- Metrics to monitor: the recorded substitution for each run, per adapter; the rung reached
  and the output form produced.
- Verification checkpoints: P-008 (the ladder exercised with each optional tool absent in
  turn, after a complete lifecycle has been produced on a fully equipped host); P-002 (the
  capture rung specifically, recorded before any segment-level evidence).
- Rollback or reversal conditions: reverse a rung if it produces an output that could be
  mistaken for a finished presentation without its substitution being evident; reverse the
  drawn substitute entirely if its existence proves to invite use as a primary path, in which
  case a run that filmed nothing produces no presentation and records why.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
