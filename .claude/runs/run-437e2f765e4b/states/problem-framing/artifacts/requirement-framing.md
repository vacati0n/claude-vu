# Requirement Framing: Fan-Out Inside the Implementation Phase

```yaml
requirementFraming:
  framingId: FRAME-2026-0001
  subject: Fan-out inside the implementation phase
  sourceInputs:
    - type: problem-statement
      reference: runs/inputs/parallel-implementation-investigation-request.md
  producedBy: omn-business-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  framingVerdict: framed
  requirementCount: 21
  inputDigest: sha256:3bd27e57003656f495ec9fa1a02df521
  contextDigest: sha256:60f5fa83b6fea5d72b27e1e770411d31
```

## Metadata

- Subject: Fan-out inside the implementation phase
- Requested by: The operator
- Decision owner: The operator, who accepts or rejects the recommendation
- Workflow phase: problem-framing
- Framing date: 2026-10-09

## Business Context

- Business intent: Decide whether reducing the implementation phase's share of delivery time and token cost justifies a change to how that phase runs, and if so the least risky form of that change. The stated mechanism, several implementer invocations running at the same time on disjoint tasks, is recorded as a supplied constraint from the problem-statement input, not as a requirement. The supplied outcome may be "do not build this".
- Problem statement: The implementation phase carried the largest single share of agent-active time in the most recent implement-feature run, and the framework has not established whether changing that phase is justified or how it could change without weakening its gates.
- Affected stakeholders: The operator, as decision owner; the gate owners whose independence and accountability a change would touch (omn-product-owner, omn-tech-lead, omn-qa, omn-orchestrator).
- Current-state pain: The implementation phase took 1h55m of the 3h00m agent-active time of run-ded114f50a46.

## Target Outcomes

| ID | Outcome | Measure | Business Driver |
|---|---|---|---|
| `O-001` | A supported decision on whether one implementation phase should run as several concurrent implementer invocations, and if so the least risky design | The decision owner accepts or rejects the recommendation, which records its evidence | Decide whether a third change is justified at all |
| `O-002` | Lower elapsed wall-clock time for the implementation phase | Elapsed time against the 1h55m baseline of run-ded114f50a46 for the same task set, with repository test-suite time excluded from both sides; suite share not supplied (`Q-001`) | Delivery time |
| `O-003` | Bounded token cost for the implementation phase | Phase token cost against its baseline, under the operator's token-cost rule in the supplied input; baseline figure not supplied (`Q-002`) | Token cost of delivery |
| `O-004` | Framework governance holds while parallelism is considered | Each option names the gates, validators, contracts, and accountability rules it touches, and none is weakened | Independence of gate decisions and single-owner accountability |
| `O-005` | Findings that can be traced and whose confidence can be judged | Each finding cites its grounding and states its confidence; each supplied fact is marked | The decision owner weighs the recommendation on evidence |

## Requirements

| ID | Requirement | Type | Outcome Ref | Priority |
|---|---|---|---|---|
| `R-001` | Each evaluated option records how concurrent write scope is partitioned, how overlapping writes to one file are handled, and how a write outside an invocation's permitted scope is handled | functional | `O-001` | Blocking |
| `R-002` | Each evaluated option records its risk to the framework's independence and gate rules | non-functional | `O-001` | Blocking |
| `R-003` | Each evaluated option records what must change in the runtime, the invocation envelope, the validator, and the contracts | functional | `O-001` | Blocking |
| `R-004` | Each multi-invocation option records the outcome when one invocation of a phase fails or returns no report | functional | `O-001` | Blocking |
| `R-005` | The investigation records, with source evidence, the assumptions the runtime, the state engine, and the implementation-report validator make about one invocation per phase | functional | `O-001` | Blocking |
| `R-006` | The option set includes doing nothing, a fan-out under one phase, a split into several declared phases, and other measured means of reducing implementation time | functional | `O-001` | Blocking |
| `R-007` | The recommendation records whether a third change is justified and the case for not building it | functional | `O-001` | Blocking |
| `R-008` | Each evaluated option records how attribution of work and evidence to each task is preserved | non-functional | `O-001` | Correctable |
| `R-009` | Each multi-invocation option records the outcome when one task is invoked more than once | functional | `O-001` | Correctable |
| `R-010` | The recommendation records the evidence that would change it | functional | `O-001` | Correctable |
| `R-011` | Each option's elapsed-time estimate excludes repository test-suite time from both the baseline and the option | functional | `O-002` | Blocking |
| `R-012` | Each option's elapsed-time estimate includes its coordination cost before any elapsed gain is claimed | functional | `O-002` | Blocking |
| `R-013` | Each option's elapsed-time estimate is stated against the implementation-phase baseline of run-ded114f50a46 for the same task set, using measured wave widths and the write-set overlap | functional | `O-002` | Blocking |
| `R-014` | Each option's token cost for the implementation phase is stated relative to the baseline of run-ded114f50a46 | functional | `O-003` | Blocking |
| `R-015` | The recommendation applies the operator's token-cost rule to each option | functional | `O-003` | Blocking |
| `R-016` | Each gate decision under any option is held by an owner who did not produce the evidence for it | non-functional | `O-004` | Blocking |
| `R-017` | No option causes the runtime to make an inference-service call | non-functional | `O-004` | Blocking |
| `R-018` | No option weakens a gate, a validator, an artifact contract, or the one-owner-per-phase accountability rule | non-functional | `O-004` | Blocking |
| `R-019` | Each supplied fact is marked verified, refuted, or unverified, with its source, before any option relies on it | non-functional | `O-005` | Blocking |
| `R-020` | Each finding cites the files read and the commands run that ground it | non-functional | `O-005` | Correctable |
| `R-021` | Each finding states its confidence | non-functional | `O-005` | Correctable |

## Acceptance Intent

| ID | Acceptance Intent | Requirement Ref | Demonstrated By | Priority |
|---|---|---|---|---|
| `AI-001` | Each multi-invocation option's write-scope account covers partitioning, same-file overlap, and out-of-scope writes | `R-001` | The write-scope entry of each option in the recommendation | Blocking |
| `AI-002` | Each option states a risk to independence and gate rules that a reader can weigh | `R-002` | The independence-risk entry of each option | Blocking |
| `AI-003` | Each option lists the runtime, envelope, validator, and contract changes it requires | `R-003` | The change list of each option | Blocking |
| `AI-004` | Each multi-invocation option states what happens to the phase when one invocation fails or returns no report | `R-004` | The failure entry of each multi-invocation option | Blocking |
| `AI-005` | The current-state assumptions about one invocation per phase each cite their source | `R-005` | The current-state section of the findings | Blocking |
| `AI-006` | The option set contains all four named options, each with its own account | `R-006` | The option-set section of the findings | Blocking |
| `AI-007` | The recommendation states a verdict on building and the case against building | `R-007` | The recommendation section | Blocking |
| `AI-008` | Each option states how attribution of work and evidence to tasks survives | `R-008` | The attribution entry of each option | Correctable |
| `AI-009` | Each multi-invocation option states what happens when one task is run twice | `R-009` | The repeat-invocation entry of each multi-invocation option | Correctable |
| `AI-010` | The recommendation names the evidence that would reverse it | `R-010` | The reversal conditions in the recommendation | Correctable |
| `AI-011` | Each elapsed-time comparison shows test-suite time removed from both the baseline and the option | `R-011` | The elapsed-time comparison for each option | Blocking |
| `AI-012` | Each elapsed-time comparison shows coordination cost added before any gain is stated | `R-012` | The elapsed-time comparison for each option | Blocking |
| `AI-013` | Each elapsed-time comparison names the baseline run, the wave widths, and the write-set overlap it uses | `R-013` | The stated inputs of each elapsed-time comparison | Blocking |
| `AI-014` | Each option's token cost is shown against the baseline run | `R-014` | The token-cost comparison for each option | Blocking |
| `AI-015` | Each option is shown against the operator's token-cost rule, with the result stated | `R-015` | The rule check recorded for each option in the recommendation | Blocking |
| `AI-016` | Each gate named for a change under any option lists an owner who did not produce its evidence | `R-016` | The gate-owner entries in the recommendation | Blocking |
| `AI-017` | Each option states that it adds no inference-service call to the runtime | `R-017` | The runtime-call statement of each option | Blocking |
| `AI-018` | Each option states which gate, validator, contract, and accountability rule it touches, and how each still holds | `R-018` | The governance entry of each option | Blocking |
| `AI-019` | Each supplied fact carries a verified, refuted, or unverified mark with its source | `R-019` | The findings record for each supplied fact | Blocking |
| `AI-020` | Each finding names the files and commands that ground it | `R-020` | Each finding in the findings record | Correctable |
| `AI-021` | Each finding carries a stated confidence | `R-021` | Each finding in the findings record | Correctable |

## Framing Boundaries

| ID | Excluded Concern | Reason | Revisit Trigger |
|---|---|---|---|
| `B-001` | Technical approach and design of any option, including how a write-scope partition is built | Design belongs to `architect` | The operator accepts a build option and requests its design |
| `B-002` | Task breakdown, wave sequencing, and dispatch order of any option | Decomposition belongs to `planner` | An option is accepted for build |
| `B-003` | Scope of any accepted change | Scope belongs to `omn-product-owner`; this framing records a recommendation only | The operator accepts a build recommendation |
| `B-004` | The degree of elapsed-time reduction that counts as measurably lower | Thresholds belong to `omn-product-owner` (`Q-003`) | The recommendation reaches the Recommendation Gate |
| `B-005` | Verification design for the elapsed-time and token-cost measurements | Verification design belongs to `omn-qa` | An option's measurement is designed for a run |
| `B-006` | Access, permission, and security of runtime operations | The security affected area in the task context was triggered by the word token, which the supplied input uses for token cost of the implementation phase | A supplied input proposes permission or access changes for concurrent invocations |
| `B-007` | Reducing repository test-suite runtime and the parallel test runner | Delivered separately; its time is excluded from both sides of the measure | Suite time is re-measured for the baseline or an option |
| `B-008` | Decisions at the Technical Gate and the Recommendation Gate | Decided by `omn-context-agent` with `architect`, and by `omn-tech-lead` with `omn-orchestrator`; this artifact decides neither | Each gate is reached by its phase |

## Assumptions

| ID | Assumption | Basis | Confidence | Impact If False |
|---|---|---|---|---|
| `AS-001` | The operator's existing severity vocabulary is Blocking and Correctable, and it fills the Priority columns | The severity scale in the quality contract is the only severity vocabulary in the frozen context slice | medium | Priority labels are remapped; no requirement or acceptance intent changes |
| `AS-002` | The 1h55m baseline is the implementation-phase elapsed time recorded for run-ded114f50a46 | Stated in the supplied input; the run evidence is outside the frozen slice and was not read | medium | Every elapsed-time comparison shifts by the same error |
| `AS-003` | The wave widths 2,1,2,1,3,1,1,2,1 describe the plan of run-ded114f50a46 and sum to its 14 tasks | Arithmetic on the supplied figures: the widths sum to 14 across 9 waves; the plan itself was not read | high | The best-case ratio of about 1.5 changes |
| `AS-004` | The write-set overlap described in the input holds beyond the one run it describes | Supplied as a single observation; no second run is cited | low | Any fan-out speedup estimate built on the overlap is over- or understated |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | The repository test-suite time inside run-ded114f50a46's implementation phase is not supplied, so the baseline with suite time excluded cannot yet be stated | no | omn-context-agent | option-analysis |
| `Q-002` | The token cost of run-ded114f50a46's implementation phase is not supplied, so the operator's token-cost rule has no baseline | no | omn-context-agent | option-analysis |
| `Q-003` | The reduction in elapsed time that counts as measurably lower is not stated | no | omn-product-owner | recommendation |
| `Q-004` | Whether the write-set overlap in supplied fact 2 holds across the plan's tasks is unverified | no | omn-context-agent | option-analysis |
| `Q-005` | Whether a dispatched agent can start further agents, and what the implementer's declared tools allow, is unverified (supplied fact 3) | no | omn-context-agent | technical-discovery |
| `Q-006` | Whether the runtime, the state engine, and the implementation-report validator assume one invocation per phase is unverified against source (supplied fact 4) | no | omn-context-agent | technical-discovery |
| `Q-007` | Whether separate working copies with a merge step are feasible in this framework (supplied fact 5) is a design question | no | architect | option-analysis |

## Handoff

- Downstream owner: omn-product-owner decides the Framing Gate; omn-context-agent consumes the framing after the gate, for technical-discovery.
- Gate: Framing Gate of `investigate`, phase problem-framing (owners: omn-business-analyst as producer, omn-product-owner as decider).
- Evidence for the gate: Traceability is complete from `O-001` to `O-005`, through `R-001` to `R-021`, to `AI-001` to `AI-021`; every requirement is typed; the verdict is framed with no blocking question. Questions `Q-001` to `Q-007` travel with the handoff as non-blocking, each with its owner.
- Deferred to downstream: Technical approach and design of any option (`architect`, `B-001`); task breakdown and wave sequencing (`planner`, `B-002`); scope of any change and the measurably-lower threshold (`omn-product-owner`, `B-003`, `Q-003`); verification design (`omn-qa`, `B-005`); the build recommendation decision at the Recommendation Gate (`omn-tech-lead`, `omn-orchestrator`, `B-008`).
