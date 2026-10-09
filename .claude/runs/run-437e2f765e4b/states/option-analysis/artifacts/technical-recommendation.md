```yaml
technicalRecommendation:
  recommendationId: REC-run-437e2f765e4b-001
  decisionReference: "runs/inputs/parallel-implementation-investigation-request.md: operator decision on fan-out inside the implementation phase (run-437e2f765e4b, option-analysis)"
  decisionBasis: option-analysis
  sourceInputs:
    - type: investigation-report
      reference: runs/run-437e2f765e4b/states/technical-discovery/artifacts/investigation-report.md
  producedBy: omn-tech-lead
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  recommendedOption: O-004
  readinessDecision: proceed-with-conditions
  inputDigest: sha256:6e659dd518a400560696fed736e0c4c5
  contextDigest: sha256:7e89d49a7c72f558eb49a242951bda58
```

## Metadata

- Recommendation ID: REC-run-437e2f765e4b-001
- Decision owner: omn-orchestrator at the Recommendation Gate of the next phase; the operator accepts or rejects the committed recommendation
- Requested by: The operator
- Decision date: 2026-10-09

## Decision Context

- Decision to make: Which of four directions should the framework take to shorten the implementation phase, given the operator's criteria, and is building concurrent implementer work justified at all.
- Delivery constraints: Gates, validators, artifact contracts and one owner per phase hold as written; the runtime calls no model; the baseline is the 1h55m30s (6930 seconds) implementation phase of run-ded114f50a46 with suite time excluded from both sides; token cost may not exceed baseline by more than 25 percent unless the elapsed-time gain exceeds 40 percent; no decision deadline is stated (investigation report E-002, E-039). This is option analysis only: the committed recommendation is the next phase's output, and no command was run for this artifact.
- Assumptions in force: The token baseline is only a read estimate of 57746 tokens per dispatch, not measured usage (E-039, E-041; `Q-001`). The in-phase ceiling reads six tasks over a longest chain of four, about one third elapsed-time reduction, and treats task durations as equal because only complexity labels exist (E-029, E-030, E-031; `Q-003`). The task-to-file overlap is derived and rests on one run (E-032, E-035; `Q-003`). Whether the host can isolate a dispatch or nest dispatches is unknown (E-024, E-044; `Q-005`). Evidence identifiers E-nnn cite the supplied investigation report.

## Evaluation Criteria

| ID | Criterion | Why it matters | Priority | Source |
|---|---|---|---|---|
| `EC-001` | No weakening of gates, validators, artifact contracts or the one-owner-per-phase rule | A speedup bought by loosening governance is the trade the framework forbids | must-have | Operator constraints in the investigation request (E-002); charter invariant I6 |
| `EC-002` | Phase token cost not more than 25 percent over baseline unless elapsed-time gain exceeds 40 percent | The operator's stated price for any extra spend | must-have | Operator decision rule in the investigation request (E-002) |
| `EC-003` | Measurably lower elapsed time for the implementation phase, with suite time excluded from both sides | The one outcome the effort exists to deliver; time spent in the test suite does not count | high | Operator baseline and exclusion in the investigation request (E-002) |
| `EC-004` | The option's gain and cost rest on recorded measurement, not on estimate | The baseline tokens, suite share and coordination cost are all unmeasured today (E-041) | high | Charter invariant I4 and I8, a delivery principle this role applies |
| `EC-005` | Introduces no concurrent-write hazard or new coordination mechanism | No lock, overlap guard or sibling-merge code exists, and three in-phase tasks share one runtime file (E-011, E-020, E-032, E-045) | medium | Repository facts in the investigation report (E-011, E-020, E-045) |

## Options

| ID | Option | Summary | Effort | Delivery risk | Reversibility | Evidence |
|---|---|---|---|---|---|---|
| `O-001` | Do nothing | Keep one implementer invocation per implementation phase and take no further change | trivial | low | reversible | E-004, E-026, E-028, E-038, E-039 |
| `O-002` | Host-level fan-out | A host session starts several implementer invocations for one implementation work item, each on a subset of the six in-phase tasks, producing one report | unknown | high | costly-to-reverse | E-005, E-008, E-011, E-020, E-022, E-026, E-029, E-030, E-031, E-032, E-039 |
| `O-003` | Split into declared phases | Declare more than one implementation phase in the Phase Model, each with one owner and one output artifact, so sibling phases can run concurrently | unknown | high | costly-to-reverse | E-004, E-005, E-006, E-013, E-014, E-027, E-028, E-040 |
| `O-004` | Measured non-parallel levers | Keep one invocation; first record per-command timing and actual token use for the phase, then act only on levers the record names (repeated full-suite runs, per-dispatch read volume) | unknown | low | reversible | E-033, E-037, E-039, E-041, E-043 |

## Tradeoff Analysis

| Option | Criteria met | Criteria missed | Strengths | Weaknesses | Sequencing implication |
|---|---|---|---|---|---|
| `O-001` | `EC-001`, `EC-002`, `EC-004`, `EC-005` | `EC-003` | Every contract holds; the phase is observable as one invocation, 32 of 32 checks (E-038); no tokens added | Delivers no elapsed-time reduction and leaves 6930 of 10831 agent-active seconds in this phase (E-039) | None; can be chosen now, and any later option stays open |
| `O-002` | None. | `EC-001`, `EC-002`, `EC-003`, `EC-004`, `EC-005` | Ceiling of about one third in-phase from 6 tasks over a chain of 4 (E-029, E-031); 4 of 5 unordered pairs have disjoint primary write sets (E-032) | Ceiling is below the 40 percent exception while one extra invocation adds about 100 percent on the read proxy, so EC-002 is missed; no owner for a combined report and one digest pair (E-026, E-028); no partial-completion status (E-009); no lock or merge code (E-011, E-045); coordination cost unmeasured | Needs isolated working copies, a combining step and a report-ownership rule (architect) before any build |
| `O-003` | None. | `EC-001`, `EC-002`, `EC-003`, `EC-004`, `EC-005` | Keeps one owner and one artifact per phase and reuses the validator by artifact name (E-012, E-013) | Gain needs concurrent leases across phases while the specifications disagree (E-005, E-006); gate layout undefined for added phases (E-004); each added phase repeats a read of about 57746 estimated tokens (E-039); same-file overlap is split across phases, not removed; changing a Phase Model is a contract change, which EC-001 does not let this analysis assume safe | Needs the lease question settled and a changed Phase Model through the framework's own change route first |
| `O-004` | `EC-001`, `EC-002`, `EC-004`, `EC-005` | `EC-003` | No gate, validator or contract changes and no invocation added (E-039); closes the two measurement gaps that block pricing any option (E-041) | The gain is unquantified and may sit mostly in suite time, which the operator excludes from the baseline (E-002, E-043); the delivered parallel runner therefore does not count toward EC-003; read-volume savings move tokens more than time | Measurement first, in at least one further implementation run, then re-run the option comparison with a measured baseline |

## Risk and Blocker Register

| ID | Risk or blocker | Severity | Likelihood | Delivery impact | Mitigation | Owner | Status |
|---|---|---|---|---|---|---|---|
| `RK-001` | The token baseline is a read estimate only, so the 25 percent rule cannot be applied against a measured figure | medium | certain | Any token-cost comparison, for or against fan-out, is an estimate until usage is recorded | Record actual token use for the phase in a further run (`Q-002`) | omn-orchestrator | open |
| `RK-002` | Suite time is excluded from the criterion, so levers aimed at the suite, including the delivered parallel runner, may leave the in-scope phase time unchanged | medium | likely | O-004 could finish with no in-scope elapsed-time gain, and a reported saving could be miscounted against EC-003 | Record suite and non-suite time separately (`Q-002`) and state the in-scope gain only | omn-tech-lead | open |
| `RK-003` | The ceiling and overlap figures rest on one run, equal task durations and a derived task-to-file join | medium | possible | The one-third ceiling could be higher or lower; the rejection of O-002 and O-003 on EC-002 holds only while the ceiling stays under 40 percent | Read further implementation plans and reports (`Q-003`) | omn-orchestrator | open |
| `RK-004` | The specifications disagree on concurrent leases across phases, and no contract names the owner of a combined implementation report | medium | possible | Blocks O-002 and O-003 until settled; no effect on O-001 or O-004 | Route to architect (`Q-006`) only if O-002 or O-003 is revived | architect | open |
| `RK-005` | The elapsed-time reduction that counts as measurably lower is undefined | medium | possible | A measured gain could meet no accepted standard, leaving the decision to be re-argued | Obtain the threshold from the scope owner (`Q-004`) | omn-product-owner | open |

## Assessment Summary

- Criteria applied: 5
- Options evaluated: 4
- Risks and blockers recorded: 5
- Blocking items open: 0

## Recommendation

- Recommended option: O-004
- Rationale: This is a provisional lean, not the committed recommendation. `O-004` is the only option besides `O-001` that meets the must-have criteria `EC-001` and `EC-002`, and unlike `O-001` it meets `EC-004` by producing the measured baseline that every later option needs; it still misses `EC-003`, because no in-scope elapsed-time gain is yet shown. `O-002` and `O-003` miss `EC-002` as well as `EC-001`, `EC-003`, `EC-004` and `EC-005`: their measured ceiling is about one third, below the 40 percent exception, while each added invocation adds about 100 percent on the read proxy against the 25 percent limit, and the token baseline is an estimate only.
- Preconditions: Per-command timing split into suite and non-suite time, and actual token use, are recorded for the phase in at least one further run; the committed recommendation phase re-weighs this lean against those figures.
- Options rejected: `O-001`, because it delivers no elapsed-time reduction (`EC-003`) and leaves the measurement gap (`EC-004`) open; `O-002`, because it misses `EC-002` and `EC-001` and has no mechanism for `EC-005`; `O-003`, because it misses `EC-002` and depends on a lease question the specifications leave unsettled (`EC-001`).

## Delivery Impact

- Effort and capacity: Unknown on the declared scale; the evidence supports no effort figure for instrumentation, and none is stated here.
- Sequencing constraints: Measure before any build; the committed recommendation follows in the next phase; any later revival of `O-002` or `O-003` waits on architect answers to `Q-005`, `Q-006` and `Q-007`.
- Dependencies: A role permitted to execute commands for timing and token recording; further implementation runs to widen the single-run basis; the scope owner's threshold for measurably lower.
- Reversal plan: Reversible; the option changes no framework contract, so nothing needs unwinding, and the options set stays as open afterwards as it is now.

## Readiness

- Recommended decision: proceed-with-conditions
- Conditions to satisfy: The committed recommendation phase weighs this lean against the preconditions above; the token baseline is described as an estimate wherever it is cited; no option that weakens a gate, validator, contract or the one-owner-per-phase rule is carried forward.
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
