```yaml
technicalRecommendation:
  recommendationId: REC-run-437e2f765e4b-002
  decisionReference: "runs/inputs/parallel-implementation-investigation-request.md: operator decision on fan-out inside the implementation phase (run-437e2f765e4b, recommendation)"
  decisionBasis: recommendation
  sourceInputs:
    - type: investigation-report
      reference: runs/run-437e2f765e4b/states/technical-discovery/artifacts/investigation-report.md
  producedBy: omn-tech-lead
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  recommendedOption: O-004
  readinessDecision: proceed-with-conditions
  inputDigest: sha256:6e659dd518a400560696fed736e0c4c5
  contextDigest: sha256:644e130f4ebb3a92155a37fc98bed239
```

## Metadata

- Recommendation ID: REC-run-437e2f765e4b-002
- Decision owner: omn-orchestrator at the Recommendation Gate; the operator accepts or rejects the recommendation
- Requested by: The operator
- Decision date: 2026-10-09

## Decision Context

- Decision to make: Should the framework build concurrent implementer invocations inside one implementation phase, or take another direction to shorten that phase, given the operator's criteria.
- Delivery constraints: Gates, validators, artifact contracts and one owner per phase hold as written; the runtime calls no model; the baseline is the 6930 second (1h55m30s) implementation phase of run-ded114f50a46 with suite time excluded from both sides; phase token cost may not exceed baseline by more than 25 percent unless the elapsed-time gain exceeds 40 percent; no deadline is stated (E-002, E-039). This role ran no command; every figure is read from the supplied investigation report (digest sha256:6e659dd518a400560696fed736e0c4c5) and from the option-analysis artifact of this run (digest sha256:27e39091b3e94cd42103ef04c9abee31), whose options and criteria are carried through unchanged.
- Assumptions in force: (1) The token baseline is a read estimate of 57746 tokens per dispatch, not measured usage, and the same proxy prices a fan-out invocation as one more full read; if a fan-out invocation read far less than the whole phase input, the token finding for O-002 would weaken (E-039, E-041; Q-002). (2) The in-phase ceiling reads six tasks over a longest chain of four, about one third, with durations taken as equal; the complexity labels put the off-chain tasks at S and XS, so a duration-weighted ceiling is more likely below one third than above it, but no durations exist to compute it (E-029, E-030, E-031; Q-003). (3) The task-to-file overlap is derived from three documents and rests on one run (E-032, E-035; Q-003). (4) Whether the host can isolate a dispatch or nest dispatches is unknown (E-024, E-044; Q-005). E-nnn identifiers cite the supplied investigation report.

## Evaluation Criteria

| ID | Criterion | Why it matters | Priority | Source |
|---|---|---|---|---|
| `EC-001` | No weakening of gates, validators, artifact contracts or the one-owner-per-phase rule | A speedup bought by loosening governance is the trade the framework forbids | must-have | Operator constraints in the investigation request (E-002); charter invariant I6 |
| `EC-002` | Phase token cost not more than 25 percent over baseline unless elapsed-time gain exceeds 40 percent | The operator's stated price for any extra spend | must-have | Operator decision rule in the investigation request (E-002) |
| `EC-003` | Measurably lower elapsed time for the implementation phase, with suite time excluded from both sides | The one outcome the effort exists to deliver; suite time does not count | high | Operator baseline and exclusion in the investigation request (E-002) |
| `EC-004` | The option's gain and cost rest on recorded measurement, not on estimate | Baseline tokens, suite share and coordination cost are all unmeasured today (E-041) | high | Charter invariants I4 and I8, a delivery principle this role applies |
| `EC-005` | Introduces no concurrent-write hazard or new coordination mechanism | No lock, overlap guard or sibling-combining code exists, and three in-phase tasks share one runtime file (E-011, E-020, E-032, E-045) | medium | Repository facts in the investigation report (E-011, E-020, E-045) |

## Options

| ID | Option | Summary | Effort | Delivery risk | Reversibility | Evidence |
|---|---|---|---|---|---|---|
| `O-001` | Do nothing | Keep one implementer invocation per implementation phase and take no further change | trivial | low | reversible | E-004, E-026, E-028, E-038, E-039 |
| `O-002` | Host-level fan-out | A host session starts several implementer invocations for one implementation work item, each on a subset of the six in-phase tasks, producing one report | unknown | high | costly-to-reverse | E-005, E-008, E-011, E-020, E-022, E-026, E-029, E-030, E-031, E-032, E-039 |
| `O-003` | Split into declared phases | Declare more than one implementation phase in the Phase Model, each with one owner and one output artifact, so sibling phases can run concurrently | unknown | high | costly-to-reverse | E-004, E-005, E-006, E-013, E-014, E-027, E-028, E-040 |
| `O-004` | Measured non-parallel levers | Keep one invocation; first record per-command timing split into suite and non-suite time and actual token use for the phase, then act only on levers the record names (repeated full-suite runs, per-dispatch read volume) | unknown | low | reversible | E-033, E-037, E-039, E-041, E-043 |

## Tradeoff Analysis

| Option | Criteria met | Criteria missed | Strengths | Weaknesses | Sequencing implication |
|---|---|---|---|---|---|
| `O-001` | `EC-001`, `EC-002`, `EC-004`, `EC-005` | `EC-003` | Every contract holds; phase behaviour is observable as one invocation with 32 of 32 checks (E-038); no tokens added | No elapsed-time reduction; leaves 6930 of 10831 agent-active seconds in this phase and its suite share unmeasured (E-039, E-041); produces no evidence for any later decision | None; any later option stays open |
| `O-002` | None. | `EC-001`, `EC-002`, `EC-003`, `EC-004`, `EC-005` | Ceiling of about one third from 6 tasks over a chain of 4 (E-029, E-031); 4 of 5 unordered in-phase pairs have disjoint primary write sets (E-032) | EC-002: ceiling is below the 40 percent exception while each added invocation adds about 100 percent on the read proxy; EC-001: no contract names the owner of a combined report and the validator permits one producer and one digest pair, so it cannot be shown to hold without a contract change (E-026, E-028); no partial-completion status (E-009); no lock or combining code (E-011, E-045); coordination cost unmeasured; tests, documents and mirror stay serial (E-035) | Needs isolated working copies, a combining step and a report-ownership rule from architect before any build |
| `O-003` | None. | `EC-001`, `EC-002`, `EC-003`, `EC-004`, `EC-005` | Keeps one owner and one artifact per phase and reuses the validator by artifact name (E-012, E-013) | Gain needs concurrent leases across phases while the specifications disagree (E-005, E-006); gate layout undefined for added phases (E-004); each added phase repeats an estimated 57746 token read (E-039); same-file overlap moves across phases, it is not removed; a Phase Model change is a contract change, which EC-001 does not let this analysis assume safe | Needs the lease question settled and a changed Phase Model through the framework's own change route first |
| `O-004` | `EC-001`, `EC-002`, `EC-004`, `EC-005` | `EC-003` | No gate, validator or contract changes and no invocation added; closes the two measurement gaps that block pricing every other option (E-039, E-041) | Shows no in-scope elapsed-time gain by itself; may find the gain sits mostly in suite time, which the operator excludes and which the delivered parallel runner already addresses (E-002, E-043); read-volume savings move tokens more than time | Measurement in at least one further implementation run, then re-run this comparison on measured figures |

## Risk and Blocker Register

| ID | Risk or blocker | Severity | Likelihood | Delivery impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| `RK-001` | The token baseline is a read estimate only, so EC-002 cannot be applied to a measured figure | medium | certain | Any token comparison, for or against fan-out, stays an estimate until usage is recorded | Record actual token use for the phase in a further run (`Q-002`) | omn-orchestrator | open |
| `RK-002` | Suite time is excluded from EC-003, so levers aimed at the suite may leave the in-scope phase time unchanged | medium | likely | O-004 could finish with no in-scope elapsed-time gain, and a suite saving could be miscounted against EC-003 | Record suite and non-suite time separately and report the in-scope gain only (`Q-002`) | omn-orchestrator | open |
| `RK-003` | Ceiling and overlap figures rest on one run, equal task durations and a derived task-to-file join | medium | possible | The rejection of O-002 and O-003 on EC-002 holds only while the true ceiling stays under 40 percent | Read further implementation plans and reports (`Q-003`) | omn-orchestrator | open |
| `RK-004` | The specifications disagree on concurrent leases across phases, and no contract names the owner of a combined implementation report | medium | possible | Blocks O-002 and O-003 until settled; no effect on O-001 or O-004 | Route to architect (`Q-006`, `Q-007`) only if O-002 or O-003 is revived | architect | open |
| `RK-005` | The elapsed-time reduction that counts as measurably lower is undefined | medium | possible | A measured gain could meet no accepted standard, and the decision would be re-argued | Obtain the threshold from the scope owner (`Q-004`) | omn-product-owner | open |
| `RK-006` | Measurement becomes an open-ended deferral that never reaches a build-or-stop decision | low | possible | The question is re-opened without new evidence and the phase stays at its baseline | Re-weigh this comparison once, after the next implementation run records the split figures | omn-orchestrator | open |

## Assessment Summary

- Criteria applied: 5
- Options evaluated: 4
- Risks and blockers recorded: 6
- Blocking items open: 0

## Recommendation

- Recommended option: O-004
- Rationale: Recommend O-004 and recommend against building any fan-out now. Both must-have criteria decide it: EC-001 cannot be shown to hold for O-002 or O-003 without a contract change, and EC-002 is missed by both because the in-phase ceiling is about one third (E-029, E-031), under the 40 percent gain that would excuse a token rise above 25 percent, while one extra invocation adds about 100 percent on the only available token proxy (E-039). The ceiling is before coordination cost and before the serial tests, documents and mirror, so the real gain is lower and is not established at all (E-035, E-041). Between the two options that meet the must-haves, O-004 beats O-001 on EC-004 in the only sense that matters for the next decision: it records the split timing and token figures that every other option needs, at low delivery risk and full reversibility. Honest limits: O-004 misses EC-003 itself, no measured elapsed-time gain exists for any option, and if the scope owner sets a threshold O-004 cannot reach, O-001 is equivalent.
- Preconditions: Per-command timing split into suite and non-suite time, and actual token use, are recorded for the implementation phase in at least one further run by a role permitted to execute commands; the token baseline is called an estimate wherever it is cited.
- Options rejected: `O-001`, because it misses EC-003 and, while meeting the same must-haves as O-004 at no extra delivery risk, produces no evidence for any later decision; `O-002`, because it misses EC-002 (ceiling under 40 percent, extra invocation about 100 percent on the proxy) and EC-001 (no combined-report owner, one digest pair) and has no mechanism for EC-005; `O-003`, because it misses EC-002 and EC-001 and depends on a lease question the specifications leave unsettled.

## Delivery Impact

- Effort and capacity: Unknown on the declared scale; the evidence supports no effort figure for instrumentation, and none is stated.
- Sequencing constraints: Measure first; re-weigh this comparison once after the next implementation run records the split figures; any revival of O-002 or O-003 waits on architect answers to Q-005, Q-006 and Q-007. Evidence that would change this recommendation: measured suite-excluded phase time showing a duration-weighted ceiling above 40 percent; measured usage showing a fan-out within 25 percent of baseline tokens; other runs showing the disjoint write sets hold; host support for isolated working copies; an architect position on combined-report ownership and concurrent leases.
- Dependencies: A role permitted to execute commands for timing and token recording; further implementation runs to widen the single-run basis; the scope owner's threshold for measurably lower.
- Reversal plan: Reversible; the option changes no framework contract, so nothing needs unwinding and the option set stays as open afterwards as it is now.

## Readiness

- Recommended decision: proceed-with-conditions
- Conditions to satisfy: Instrumentation for split timing and actual token use is arranged through a role permitted to execute; no option that weakens a gate, validator, contract or the one-owner-per-phase rule is carried forward; the one-time re-weighing after the next run is scheduled so RK-006 does not stand.
- Blocking items outstanding: None identified.
- Deciding authority: `omn-orchestrator`

## Open Questions

| ID | Question | Owner | Affects |
|---|---|---|---|
| `Q-001` | What does the repository history stat for commit 280d36d list, and does it match the thirteen change-set rows of the baseline phase? | omn-tech-lead | The baseline scope; `O-001`, `O-004` |
| `Q-002` | How long did suite execution and each non-suite step take inside the implementation phase, and what was its actual token use? | omn-orchestrator | `RK-001`, `RK-002`; `EC-002`, `EC-003`, `EC-004` |
| `Q-003` | Do the same-file overlap, wave shape and task durations hold in other implementation runs? | omn-orchestrator | `RK-003`; the ceiling of `O-002` and `O-003` |
| `Q-004` | What elapsed-time reduction counts as measurably lower for an option that does not raise token cost? | omn-product-owner | `RK-005`; `EC-003` for `O-004` |
| `Q-005` | Can the host run an implementer dispatch in an isolated working copy, and can a dispatched agent start further agents? | architect | `O-002`; `EC-005` |
| `Q-006` | Who would produce and own one combined implementation report under a fan-out, given one producer id per report? | architect | `RK-004`; `O-002`; `EC-001` |
| `Q-007` | May more than one phase of one run be leased at once, given the conflicting specifications? | architect | `RK-004`; `O-003`; `EC-001` |
