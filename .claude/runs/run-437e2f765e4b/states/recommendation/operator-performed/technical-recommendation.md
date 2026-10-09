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
  contextDigest: sha256:7e89d49a7c72f558eb49a242951bda58
```

## Metadata

- Recommendation ID: REC-run-437e2f765e4b-002
- Decision owner: omn-orchestrator at the Recommendation Gate; the operator accepts or rejects the recommendation
- Requested by: The operator
- Decision date: 2026-10-09

## Decision Context

- Decision to make: Whether the framework should build concurrent implementer work inside the implementation phase, or keep one invocation per phase and pursue measured non-parallel levers, and which framework repairs should follow.
- Delivery constraints: Gates, validators, artifact contracts and the one-owner-per-phase rule hold as written; the runtime calls no model; the baseline is the 6930 second (1h55m30s) implementation phase of run-ded114f50a46 with suite time excluded from both sides; token cost may not exceed baseline by more than 25 percent unless the elapsed-time gain exceeds 40 percent; no deadline is stated (E-002, E-039). This artifact was produced as operator-performed work because the recommendation phase of this run is blocked by a framework contract gap: its input contract does not accept the technical-recommendation artifact that option-analysis produced (known defect, RK-006). The provisional option analysis of this run (REC-run-437e2f765e4b-001) was read as a working basis and is not listed as a source input for that reason; every figure below traces to the investigation report. No command was run for this artifact.
- Assumptions in force: The token baseline is a read estimate of 57746 tokens per dispatch, not measured usage (E-039, E-041). The in-phase fan-out ceiling is six tasks over a longest chain of four, about one third, with task durations treated as equal because only complexity labels exist (E-029, E-030, E-031). The task-to-file overlap is derived and rests on one run (E-032, E-035). Host isolation and nested dispatch are unknown (E-024, E-044). The digests in the metadata block are carried from the option-analysis envelope because no envelope exists for this operator-performed phase. Evidence identifiers E-nnn cite the supplied investigation report.

## Evaluation Criteria

| ID | Criterion | Why it matters | Priority | Source |
|---|---|---|---|---|
| `EC-001` | No weakening of gates, validators, artifact contracts or the one-owner-per-phase rule | A speedup bought by loosening governance is the trade the framework forbids | must-have | Operator constraints in the investigation request (E-002); charter invariant I6 |
| `EC-002` | Phase token cost not more than 25 percent over baseline unless elapsed-time gain exceeds 40 percent | The operator's stated price for any extra spend | must-have | Operator decision rule in the investigation request (E-002) |
| `EC-003` | Measurably lower elapsed time for the implementation phase, with suite time excluded from both sides | The one outcome the effort exists to deliver; time spent in the test suite does not count | high | Operator baseline and exclusion in the investigation request (E-002) |
| `EC-004` | The option's gain and cost rest on recorded measurement, not on estimate | The baseline tokens, suite share and coordination cost are all unmeasured today (E-041) | high | Charter invariants I4 and I8, a delivery principle this role applies |
| `EC-005` | Introduces no concurrent-write hazard or new coordination mechanism | No lock, overlap guard or sibling-combine code exists, and three in-phase tasks share one runtime file (E-011, E-020, E-032, E-045) | medium | Repository facts in the investigation report (E-011, E-020, E-045) |

## Options

| ID | Option | Summary | Effort | Delivery risk | Reversibility | Evidence |
|---|---|---|---|---|---|---|
| `O-001` | Do nothing | Keep one implementer invocation per implementation phase and take no further change | trivial | low | reversible | E-004, E-026, E-028, E-038, E-039 |
| `O-002` | Host-level fan-out | A host session starts several implementer invocations for one implementation work item, each on a subset of the six in-phase tasks, producing one report | unknown | high | costly-to-reverse | E-005, E-008, E-011, E-020, E-022, E-026, E-029, E-030, E-031, E-032, E-039 |
| `O-003` | Split into declared phases | Declare more than one implementation phase in the Phase Model, each with one owner and one output artifact, so sibling phases can run concurrently | unknown | high | costly-to-reverse | E-004, E-005, E-006, E-013, E-014, E-027, E-028, E-040 |
| `O-004` | Measured non-parallel levers | Keep one invocation; record per-command timing (suite and non-suite separately) and actual token use for the phase, act only on levers that record names, and repair the known framework contract defects that obstruct governed runs | unknown | low | reversible | E-033, E-037, E-039, E-041, E-043 |

## Tradeoff Analysis

| Option | Criteria met | Criteria missed | Strengths | Weaknesses | Sequencing implication |
|---|---|---|---|---|---|
| `O-001` | `EC-001`, `EC-002`, `EC-005` | `EC-003`, `EC-004` | Every contract holds; the phase is observable as one invocation, 32 of 32 checks (E-038); no tokens added | Delivers no elapsed-time reduction, leaves 6930 of 10831 agent-active seconds in this phase (E-039), and leaves the measurement gap open (E-041) | None; can be chosen now and every later option stays open |
| `O-002` | None. | `EC-001`, `EC-002`, `EC-003`, `EC-004`, `EC-005` | Ceiling of about one third in-phase from six tasks over a chain of four (E-029, E-031); 4 of 5 unordered pairs have disjoint primary write sets (E-032) | The ceiling is below the 40 percent exception while one extra invocation adds about 100 percent on the read proxy, so EC-002 is missed; no owner for a combined report and one digest pair (E-026, E-028); no partial-completion status (E-009); no lock or combine code (E-011, E-045); coordination cost unmeasured | Needs isolated working copies, a combining step and a report-ownership rule from the architect before any build |
| `O-003` | None. | `EC-001`, `EC-002`, `EC-003`, `EC-004`, `EC-005` | Keeps one owner and one artifact per phase and reuses the validator by artifact name (E-012, E-013) | Gain needs concurrent leases across phases while the specifications disagree (E-005, E-006); gate layout undefined for added phases (E-004); each added phase repeats a read of about 57746 estimated tokens (E-039); same-file overlap is split across phases, not removed; a Phase Model change is a contract change that EC-001 does not let this analysis assume safe | Needs the lease question settled and a changed Phase Model through the framework's own change route first |
| `O-004` | `EC-001`, `EC-002`, `EC-005` | `EC-003`, `EC-004` | No gate, validator or contract weakened and no invocation added (E-039); produces the measured baseline that pricing any option needs (E-041); the contract repairs it carries remove defects that block or distort governed runs | EC-003 is not met today: the in-scope gain is unquantified and may sit mostly in suite time, which the operator excludes (E-002, E-043), so the delivered parallel runner does not count toward it; EC-004 is met only once the measurement exists, not by choosing the option; read-volume savings move tokens more than time | Measurement first, in at least one further implementation run, then re-run the comparison against measured figures |

## Risk and Blocker Register

| ID | Risk or blocker | Severity | Likelihood | Delivery impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| `RK-001` | The token baseline is a read estimate only, so the 25 percent rule cannot be applied against a measured figure | medium | certain | Any token-cost comparison, for or against fan-out, stays an estimate until usage is recorded | Record actual token use for the phase in a further run (`Q-002`) | omn-orchestrator | open |
| `RK-002` | Suite time is excluded from the criterion, so levers aimed at the suite, including the delivered parallel runner, may leave in-scope phase time unchanged | medium | likely | O-004 could finish with no in-scope elapsed-time gain, and a reported saving could be miscounted against EC-003 | Record suite and non-suite time separately (`Q-002`) and state the in-scope gain only | omn-tech-lead | open |
| `RK-003` | The ceiling and overlap figures rest on one run, equal task durations and a derived task-to-file join | medium | possible | The one-third ceiling could be higher or lower; rejecting O-002 and O-003 on EC-002 holds only while the ceiling stays under 40 percent and the read proxy stays near double | Read further implementation plans and reports (`Q-003`) | omn-orchestrator | open |
| `RK-004` | The specifications disagree on concurrent leases across phases, and no contract names the owner of a combined implementation report | medium | possible | Blocks O-002 and O-003 until settled; no effect on O-001 or O-004 | Route to the architect (`Q-005`, `Q-006`) only if O-002 or O-003 is revived | architect | open |
| `RK-005` | The elapsed-time reduction that counts as measurably lower is undefined | medium | possible | A measured gain could meet no accepted standard, leaving the decision to be re-argued | Obtain the threshold from the scope owner (`Q-004`) | omn-product-owner | open |
| `RK-006` | Three handoff defects occurred while running this investigation: the self-hosting profile routes the investigate command with input type investigation-request, which no agent accepts; no producer exists for framed-objective, so problem-framing cannot hand off to technical-discovery unless the investigation question is supplied up front; the recommendation phase does not accept technical-recommendation, so option-analysis cannot hand off to it | medium | certain | Each governed investigate run needs operator-performed work to complete; this run did, for this phase, and the work is recorded as operator-performed rather than runtime-dispatched | Route as framework-internal changes through the self-hosting classify and route commands, each with a change proposal, owned by the architect | architect | open |
| `RK-007` | The model-tier policy file declares technical-discovery as the light tier although its substance (reading evidence, deriving joins, qualifying facts) cannot be validated mechanically, so a weaker tier can pass structural checks with weaker findings | medium | possible | Discovery quality, which every later option analysis rests on, is not protected by any validator | Reassess the tier for technical-discovery in the policy file under the framework's change route, with an escalation rule keyed to evidence rather than structure | architect | open |

## Assessment Summary

- Criteria applied: 5
- Options evaluated: 4
- Risks and blockers recorded: 7
- Blocking items open: 0

## Recommendation

- Recommended option: O-004
- Rationale: Do not build fan-out inside the implementation phase now. The measured ceiling for the six in-phase tasks is about one third (E-029, E-031), below the 40 percent gain that EC-002 requires before token cost may exceed 25 percent, while each extra invocation adds about 100 percent on the only available proxy (E-039); O-002 therefore misses the must-have EC-002, and it also has no owner for a combined report, no partial-completion status and no write-overlap guard, which misses EC-001 and EC-005. O-003 misses EC-001 and EC-002 for the same token reason and because the specifications disagree on concurrent leases. O-001 and O-004 are the only options that hold the must-have criteria; O-004 is preferred because it is the only one that can ever satisfy EC-003 and EC-004, by producing the suite-excluded timing and measured token use that no option can currently be priced against. The honest limit is that EC-003 is not met today and may not be met by O-004 either, if the time sits in the suite. What would change this recommendation: measured token overhead of a second invocation at or under 25 percent (for example because a narrowed read set cuts the per-dispatch read), or a suite-excluded, duration-weighted ceiling above 40 percent holding across several implementation runs; and, in either case, architect answers that a combined report has an owner, that concurrent leases are permitted, and that the host isolates a dispatch in its own working copy.
- Preconditions: Per-command timing split into suite and non-suite time, and actual token use, are recorded for the phase in at least one further implementation run; the scope owner states what counts as measurably lower; any contract repair listed under Delivery Impact goes through the framework's own change route with a change proposal.
- Options rejected: O-001, because it delivers no elapsed-time reduction (EC-003) and leaves the measurement gap (EC-004) open; O-002, because it misses EC-002 (ceiling under 40 percent against about 100 percent more read volume) and EC-001 and EC-005 (no report owner, no overlap guard); O-003, because it misses EC-002 and depends on a lease question the specifications leave unsettled (EC-001).

## Delivery Impact

- Effort and capacity: Unknown on the declared scale; the evidence supports no effort figure for instrumentation or the repairs, and none is stated here.
- Sequencing constraints: Measure before any build. Follow-up framework changes worth doing instead of fan-out, each a separate framework-internal change with its own proposal, in this order of value: first, repair the investigate handoff chain (the self-hosting profile's investigate input type that no agent accepts; the missing producer for framed-objective; the recommendation phase's refusal of technical-recommendation), because it makes every investigate run depend on operator-performed work; second, add recorded per-command timing and actual token use to the phase evidence, so EC-003 and EC-004 can be judged; third, reassess the technical-discovery tier in the model-tier policy file; fourth, act on whichever lever the measurement names (repeated whole-suite runs, per-dispatch read volume, the plan not being an input to the implementation phase per E-033). Any revival of O-002 or O-003 waits on architect answers to `Q-005`, `Q-006` and `Q-007`.
- Dependencies: A role permitted to execute commands for timing and token recording; further implementation runs to widen the single-run basis; the scope owner's threshold for measurably lower; the architect for the contract repairs.
- Reversal plan: Reversible. Measurement changes no contract; each repair is a separate change that can be reverted on its own proposal; the option set stays as open afterwards as it is now.

## Readiness

- Recommended decision: proceed-with-conditions
- Conditions to satisfy: Record suite and non-suite time and actual token use before re-weighing any parallel option; state the in-scope gain only, never a gain in suite time, against EC-003; describe the token baseline as an estimate wherever it is cited; carry forward no option that weakens a gate, validator, contract or the one-owner-per-phase rule; record that this phase was operator-performed because of the handoff defect in RK-006.
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
