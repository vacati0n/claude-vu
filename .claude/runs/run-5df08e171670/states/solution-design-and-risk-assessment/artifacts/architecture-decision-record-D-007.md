# Architecture Decision Record — D-007

## Metadata

- ADR ID: D-007
- Title: Carry the operator-facing surface on the existing command's contract as an additive minor version
- Date: 2026-09-14
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners; accepting owner omn-tech-lead under the Producer Exclusion Rule)
- Related Work Items: run-5df08e171670, phase solution-design-and-risk-assessment; execution-plan task T-028

## Context

- Problem statement: the capability needs an operator-facing request, and that request has to
  be discoverable from a published contract whose recorded version tells the truth about what
  changed. The alternatives are a new command with its own record, or an additive parameter
  group on the command the request names.
- Business and technical constraints: C-001 (additive only; no existing artifact contract
  changes), C-011 (recording is opt-in on the one command the request names), C-012 (the
  recorded version states an additive change with safe defaults under the declared versioning
  rule), C-003 (a run that does not request recording pays only the guard, so the default must
  be off).
- Current architecture baseline: F-021 (the request parser registers ten recording arguments,
  the command specification documents nine, the change record states seven, and the registry
  record stands at 1.1.0), F-020 (four guarded runtime sites, including the observation
  subcommand that carries the manual operations), F-025 (the wrapper modules forward the
  request to the runtime and both documentation surfaces carry it).

## Decision

- Selected option: O-001.
- Decision statement: the recording request is an optional parameter group on the existing
  command, every member of which has a safe default of off or unset, so an existing invocation
  is unchanged in form and in behaviour. The command's registry record moves from 1.0.0 to
  1.1.0 as a minor increment under the declared versioning rule, its published specification
  gains a Parameters section describing the group, and the runtime's manual operations live on
  a separate observation subcommand rather than being folded into the command itself. The
  three surfaces — parser, specification, and registry record — describe one contract and are
  treated as a single unit for agreement and for rollback; F-021 records that they do not
  currently agree on the size of the group, which P-003 sequences ahead of the contract being
  offered as evidence.
- Scope of impact: M-016, M-017, M-018, M-019, M-020, M-022.

## Alternatives Considered

1. O-002 — the same tap, with the recording owned inside the runtime process
- Benefits: none bearing on the contract surface; the parameter group would be identical.
- Risks: none bearing on the contract surface.
- Why not selected: rejected under D-002 on grounds unrelated to this decision.

2. O-003 — instrument each phase and dispatch site directly
- Benefits: none bearing on the contract surface.
- Risks: as recorded in the evaluation table.
- Why not selected: eliminated by C-003.

3. O-004 — reconstruct after the fact from persisted evidence only
- Benefits: the request could be a separate after-the-fact command with no change to the
  existing command's contract at all.
- Risks: it requires a further command to produce anything, against C-011.
- Why not selected: eliminated by C-015; and a separate command would put the capability
  outside the command the request names, which C-011 forbids.

4. O-005 — a general run-telemetry pipeline with the presentation as a consumer
- Benefits: a pipeline would justify its own command and its own record.
- Risks: a second durable interface and a second contract to version.
- Why not selected: eliminated by C-007. Its migration burden in the evaluation table is the
  highest of any option for exactly this reason.

5. O-006 — draw a synthetic dashboard instead of filming
- Benefits: a narrower parameter group, since no capture parameters would be needed.
- Risks: the picture is a diagram of the run.
- Why not selected: eliminated by C-015.

## Consequences

- Positive outcomes expected: no existing invocation changes in form or behaviour, which is
  what keeps C-001 and C-003 true at the contract surface; the request is discoverable from
  the command's own published contract, which is what `AC-014` verifies; the version increment
  states the nature of the change under the declared rule rather than merely counting up.
- Tradeoffs accepted: the command's parameter surface grows substantially for a capability
  most invocations will never use; the manual operations live on a separate subcommand, so the
  capability's surface is split across two places an operator must know about; three
  artifacts must be kept in agreement, and F-021 shows that they currently are not.
- Risks introduced: R-006 (the three surfaces offered as evidence while they disagree on the
  size of the group), and the divergence between the change record's account and the delivered
  surface, carried as R-003 and Q-002.

## Validation Plan

- Metrics to monitor: the count of recording parameters in the parser, in the published
  specification, and as described by the registry record, which must be one number; the
  behaviour of an invocation carrying no recording parameter, against its behaviour before the
  change.
- Verification checkpoints: P-003 (the three surfaces brought into agreement before any is
  offered as evidence of the versioning rule); P-001 (the divergence register, which includes
  the flag-count discrepancy); P-010 (the change-wide regression evidence, taken after both).
- Rollback or reversal conditions: reverse if the additive-with-safe-defaults claim fails —
  that is, if any existing invocation is shown to change behaviour — in which case the version
  increment is not a minor one and the contract change must be re-decided. Reversal restores
  the record to 1.0.0 together with the specification and the parser, never singly, so the
  three never disagree about the contract's version.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
