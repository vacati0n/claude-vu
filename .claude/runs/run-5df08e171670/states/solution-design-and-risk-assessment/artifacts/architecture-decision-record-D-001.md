# Architecture Decision Record — D-001

## Metadata

- ADR ID: D-001
- Title: Observe the run at its single event emission point, behind a per-run switch
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan tasks T-001, T-002, T-008, T-013

## Context

- Problem statement: a run must be able to observe its own progress in enough detail to cut a
  presentation from it, without creating a second instrumentation surface and without any cost
  to a run that did not request it.
- Business and technical constraints: C-001 (additive only), C-003 (one existence check per
  emitted event and no import on the unrequested path), C-006 (external integration behind an
  adapter boundary, outside the execution path), C-007 (the record must not become a metrics
  pipeline or an interface), C-009 (no addition to what a dispatch reads), C-010 (path-facing
  elements derive from the install-prefix variable), C-011 (opt-in, on one command).
- Current architecture baseline: F-001 (every state change passes through one ordered, stamped
  emission point), F-002 (the envelope and the dispatch prompt are on disk at the adapter
  boundary, the only place the agent exchange is visible), F-003, F-004, F-005 (nothing new had
  to be instrumented; a consumer and a clock were what was missing), F-012 (every site reaching
  the package is guarded by one existence check and imports inside the guard), F-019 (the host
  session already posts every tool call, read through a pointer file at the runs root).

## Decision

- Selected option: O-001.
- Decision statement: the observation layer attaches at the ledger's single event emission
  point, reached only through an existence check on a per-run switch file and a lazy import
  inside that guard, and derives everything else from evidence the runtime already persists.
  Tool-call observation is supplied by an optional configuration fragment the operator merges
  into the host session, which posts to the runtime's observation subcommand and is resolved
  through a pointer file at the runs root; that pointer is the single write the layer makes
  outside a run's own directory.
- Scope of impact: M-001, M-002, M-003, M-015, M-016.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: one fewer process; identical observation point and identical reuse leverage.
- Risks: bears on D-002 rather than on where observation attaches; it accepts this decision.
- Why not selected: it does not differ on the observation point, so it does not displace this
  decision; it is rejected on the separate grounds recorded in D-002.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: markers could carry site-specific detail the canonical event does not.
- Risks: observation concerns spread through the execution path, against C-006.
- Why not selected: eliminated by C-003. Cost cannot be confined to one guard when every
  instrumented site pays, so the unrequested path is no longer free.

3. O-004 — reconstruct after the fact from persisted evidence only, with no live tap
- Benefits: the lowest possible cost on the observed run; no live component at all.
- Risks: no time base tying the record to a picture.
- Why not selected: eliminated by C-015. With no camera there is no material of the
  application, so the presentation cannot be evidence of the run.

4. O-005 — build a general run-telemetry pipeline and cut the presentation as one consumer
- Benefits: one general capability serving observation and any later consumer.
- Risks: a durable interface the framework must own and version.
- Why not selected: eliminated by C-007, which forbids exactly this pipeline arriving by the
  back door.

5. O-006 — draw a synthetic dashboard of the run instead of filming it
- Benefits: no capture, no external tool, no publication exposure.
- Risks: the picture is a diagram of the run rather than the run.
- Why not selected: eliminated by C-015, and already rejected by the requester.

## Consequences

- Positive outcomes expected: the unrequested path costs one existence check per event and
  never imports the layer (C-003); a dispatch reads nothing new (C-009); no second
  instrumentation surface exists, so the record cannot drift from the run; the layer reads the
  run's evidence and never writes to it.
- Tradeoffs accepted: the observation layer sees only what reaches the emission point and the
  adapter boundary, so anything the runtime does not already persist is invisible to it; the
  tool-hook fragment is an operator-merged configuration, so its absence is silent and its
  presence observes the whole host session while a run is recording.
- Risks introduced: R-004 (a caller reaching the package outside a guard defeats the
  zero-cost property), R-008 (a downstream consumer treating the marker record as an
  interface), R-009 (the merged fragment observing work unrelated to the recorded run).

## Validation Plan

- Metrics to monitor: the per-event cost on a run that did not request recording, measured
  rather than reviewed; the count of runtime sites reaching the package, against the count the
  guard covers; marker counts reconciled against the event stream and the phase directories.
- Verification checkpoints: P-005 (unrequested-path cost measured before the property is
  asserted); P-007 (marker reconciliation on a complete recorded lifecycle, including a
  replayed step); P-004 (pointer-file gating verified against a session performing unrelated
  work).
- Rollback or reversal conditions: reverse if the unrequested path is shown to cost more than
  the guard, or if any consumer outside the presentation path is found depending on the marker
  record. Reversal is the removal of the guarded sites and the package, which returns the
  runtime to a state in which the layer is unreachable.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
