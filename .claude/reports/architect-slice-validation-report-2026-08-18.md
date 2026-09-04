# Architect Slice Validation Report

- Date: 2026-08-18
- Scope: Unblock Architect Slice — make `solution-design-and-risk-assessment` executable
- Command: `/implement`
- Workflow: `implement-feature`
- Phase: `solution-design-and-risk-assessment`
- Run: `run-308f4d0ee447`
- Result: **PASS** — the phase resolves, executes, and produces an artifact that passes the
  Validation Engine 78 of 78. Slice verification is 10 of 10, PROVEN. Two limitations and
  one concurrency finding are recorded in section 8.

## 1. Exit Criteria

| Criterion | Result | Evidence |
|---|---|---|
| Runtime resolve for the architect phase returns success | PASS | `framework_runtime.py resolve --phase solution-design-and-risk-assessment` exits 0 and prints RESOLVED, with all four phase-mandatory skills, the host registration, the output contract, and the registered validator |
| A new run folder contains complete evidence | PASS | `runs/run-308f4d0ee447/` carries the request, context snapshot, envelope, dispatch and adapter prompts, artifact, three decision records, result envelope, validation report, 14-event stream, run ledger, and completion package |
| Validator pass | PASS | `design_validator.py`: 78 of 78 machine-decidable checks pass, 0 blocking, 0 correctable, 10 declared not-machine-checkable |

## 2. Deliverables

| File | Change |
|---|---|
| `registry/skills.yaml` | 1.1.0 to 1.2.0. Two records added: S03 and S11. No schema change |
| `skills/agent-skill-matrix.md` | Skill Catalog rows for S03 and S11 moved to registered; registration grounds and the Investigate S11 rationale recorded |
| `agents/architect.agent.md` | New. Host-platform entry point for agent `architect` |
| `runtime/framework_runtime.py` | Generalized off the planner phase: per-phase slices and context slices, validator registry, manifest-derived input contracts and prohibitions, multi-input dispatch, conditional-artifact write permissions |
| `runtime/design_validator.py` | New. Validation Engine for `technical-design.md` and its decision records |
| `runtime/artifact_lib.py` | New. Shared validator primitives, extracted from `plan_validator.py` |
| `runtime/plan_validator.py` | Rewired onto `artifact_lib`. No check changed |
| `runtime/verify_vertical_slice.py` | Parameterized by slice; slice inferred from the run ledger |
| `runtime/close_legacy_run.py` | New. Migration utility, see section 8.3 |
| `runs/inputs/reviewer-agent-business-intent.md` | New operator input |
| `runs/inputs/framework-architecture-context.md` | New operator input |

## 3. What Blocked the Phase, and Why

The runtime failed the phase before any invocation:

```
RUNTIME FAILURE [missing-capability-failure] phase 'solution-design-and-risk-assessment'
requires unregistered skills ['S03']; skills/skill-resolver.md blocks execution start
```

Three independent blockers existed. All three are now cleared.

| Blocker | Why it blocked | Cleared by |
|---|---|---|
| S03 unregistered | The phase declares S01, S03, S06, S09 as mandatory. `resolve_phase_skills` requires a registry record at status `active` | Record added to `registry/skills.yaml` |
| No host registration | `cmd_dispatch` refuses an agent with no `agents/<id>.agent.md`. Only `planner` had one | `agents/architect.agent.md` added |
| No validator for `technical-design.md` | The Validation Engine covered one artifact type. Without one the runtime cannot decide whether the returned artifact conforms | `design_validator.py` added and registered in `VALIDATORS` |

The first was the recorded gap. The second and third were not visible until the first
cleared, because resolution fails fast.

## 4. Skill Registration

Both records are registration of pre-existing files. No skill file was modified, and no
guidance changed. Registration records identity metadata only; it grants neither skill to
any agent, so no agent's resolved skill bundle changed.

| Skill ID | Registry identifier | Display name | Category | Ground for registering |
|---|---|---|---|---|
| S03 | `engineering-playbook` | .NET Engineering | .NET | Mandatory for `solution-design-and-risk-assessment`, which the runtime routes |
| S11 | `observability-logging` | Logging and Observability | Logging | Retained as mandatory for Investigate → Technical Discovery |

S11 was assessed against the task's condition, "register if retained as mandatory in the
Investigate matrix phases". It is retained: Investigate exists to reconstruct current-state
behavior, and observability evidence is the primary source for that reconstruction. The
rationale is now recorded in the matrix rather than left implicit.

The registration ground was widened in `skills/agent-skill-matrix.md`. Previously a record
was registered only when an active agent manifest declared it, which is why the 2026-08-18
skill registry work correctly left S03 and S11 out. A skill that a routed workflow phase
declares mandatory is now also grounds, because the resolver blocks execution on it.

Derivation, uniqueness, and path-existence rules were re-checked across all nine records:
each `identifier` equals its `specificationPath` basename, each `skillCode` is unique, each
`specificationPath` resolves, and each record carries exactly the schema's field set under
`failOnUnknownFields`.

Still unregistered: S04, S05, S10. No routed phase and no active agent manifest requires
them.

## 5. Host Entry Point

`agents/architect.agent.md` is an adapter, not a contract. It loads
`agents/architect/manifest.yaml` and the seven modules that manifest declares, in the
declared order, and states nothing about how to do architecture work.

The no-duplication property is checked mechanically, not asserted: check C10 compares
normalized 12-word shingles of the adapter body against every authoritative module. The
overlap is empty.

It differs from `planner.agent.md` in three places that the architect contract forces:

1. it maps several supplied inputs onto the manifest's required input identifiers, where
   the planner takes one;
2. it permits a third write target, the conditional decision record, and defers the
   condition to the output module rather than restating it;
3. it names `agents/architect.md` and `agents/omn-architect.md` as the superseded and
   deprecated specifications, so a reader who finds them knows they are not the contract.

## 6. Runtime Generalization

The runtime was built for one phase and named the planner in nine places. Each was replaced
by a lookup rather than a second special case.

| Was | Now |
|---|---|
| `SLICE_ID` constant | `SLICES`, keyed by phase |
| `CONTEXT_SLICE_PATHS` constant | `CONTEXT_SLICE_BASE` plus `CONTEXT_SLICE_PHASE`, keyed by phase |
| `import plan_validator` | `VALIDATORS`, keyed by artifact; existence checked at resolve, not at complete |
| `quality_ref: "agents/planner/quality.md"` | derived from the agent's manifest directory |
| Prohibitions hardcoded in the envelope | carried verbatim from the manifest's `authorityScope.prohibited` |
| `inputs.accepted` only | `accepted`, or `required` plus `optional`, with the required set enforced |
| One `--input-file` | repeatable `--input <type>=<path>` |
| Two permitted writes | primary artifact, result envelope, and a glob per declared conditional artifact |
| Dispatch prompt naming planner stages R1 to R13 | routing and addressing only; every instruction deferred to the module set |

A phase is now executable when four things exist: a Phase Model row, a manifest declaring
the same phase and output artifact, a host registration, and a registered validator. The
runtime enforces all four and names which is missing.

## 7. Execution and Validation

### 7.1 The run

`/implement` → `implement-feature` → `solution-design-and-risk-assessment` → `architect` →
`technical-design.md`, dispatched through the `host-subagent` adapter in `bootstrap` mode,
which exists for a registration added after the host session started.

Four inputs were supplied against the manifest's three required identifiers plus one
optional: `change-request`, `business-intent`, `architecture-context`, and the
`execution-plan` produced by run `run-b6780677468b`. Chaining the architect phase onto the
planner phase's real output is what makes this a second link rather than a second isolated
demonstration.

Context slice: 17 members, frozen, per-file digests.
Input digest `sha256:9b2ffccc86173b79b469d7b81155db11`, context digest
`sha256:44927b3bcdd3fa660562ae2b83f0ce6e`, both carried into the artifact metadata and
cross-checked by the validator.

### 7.2 The artifact

`technical-design.md`, 65,117 bytes, thirteen sections, status `complete`, plus three
architecture decision records at status `Proposed`.

| Register | Count |
|---|---|
| Facts | 30 |
| Assumptions | 5 |
| Constraints | 16 |
| Impacted modules | 13 (2 speculative, 2 `no-change-verified`) |
| Options | 4 |
| Decisions | 5, of which 3 architecture-significant |
| Reuse survey rows | 13 |
| Sequencing constraints | 14 |
| Risks | 15 |
| Open decisions | 9, none blocking |
| Decision records | 3 |

All 14 planner tasks in the supplied execution plan are bound by a sequencing constraint,
and no `T-nnn` identifier was created.

### 7.3 Validation

`design_validator.py` runs 78 machine-decidable checks against `agents/architect/output.md`
and the A1 to A16 check set in `agents/architect/quality.md`, and declares 10 further
obligations not-machine-checkable rather than skipping them silently.

Two checks are cross-artifact, and they are why this validator exists rather than a generic
section checker:

- **D3.3** every `T-nnn` the design references must exist in the execution plan the
  envelope supplied. A design cannot invent a planner task.
- **D8.4** the option named in Selected Approach must be the option the evaluation table
  marks selected. A design cannot state one approach and evaluate another.

Final result: 78 of 78 passed, 0 blocking, 0 correctable.

### 7.4 The validation engine rejected the first attempt

The agent self-reported 98 of 98 of its own quality checks passing. The independent
validator still found a real breach:

```
FAIL [Blocking] D4.3 (A5.3): Every requirement traces to a statement identifier
  untraced: Non-functional requirements, determinism requirement — traced to `C-016` only
```

Per the rejection rules in `agents/architect/quality.md`, the run returned to Execution for
one repair pass. The agent added the statement trace, changed one line, renumbered nothing,
and left both digests byte-identical. Revalidation passed 78 of 78.

The event stream records this honestly and is append-only: `validation_failed` at E-0007
and `run_aborted` at E-0009 are preserved, followed by `retry_scheduled`,
`invocation_started`, `invocation_completed`, and `validation_passed`.

Six other checks failed on the first pass and were **validator defects, not artifact
defects**. Each was over-fitting the template's bullet rendering rather than testing the
contract, which `output.md` states governs over the template. The validator was corrected
to accept a standalone `Label:` line as well as a `- Label:` bullet, to treat a wrapped
bullet as one item, to allow a qualifying clause before a label's colon, and to accept a
template the design declares as an impacted module it proposes to create. No check was
weakened in what it decides; each still fails on a genuine breach.

### 7.5 Slice verification

`verify_vertical_slice.py --slice architect`: **10 of 10, PROVEN**.

| Check | Result |
|---|---|
| C1 architect registered, active, specification path resolves | PASS |
| C2 host registration exists and is host-compatible | PASS |
| C3 module load order resolves from the manifest | PASS |
| C4 manifest skills and phase-mandatory skills resolve | PASS |
| C5 full routing chain resolves to a registered host entry point | PASS |
| C6 run ledger records a completed real invocation, no module digest drift | PASS |
| C7 artifact produced at the declared path, no undeclared side effect | PASS |
| C8 artifact conforms to the output and quality contract | PASS |
| C9 execution evidence complete: 14 events, no missing canonical event | PASS |
| C10 no architect contract duplication | PASS |

The planner slice re-verifies at 10 of 10 after the refactor, so slice 1 did not regress.

## 8. Limitations and Findings

### 8.1 Ten quality checks are not machine-decidable

A6.2 ("a layer name is not a module"), A8.2 ("options differ structurally"), A15.1 (forward
closure over the statement register), and seven others require semantic judgement or
evidence the artifact does not carry. They are reported as `not-machine-checkable` with the
quality reference attached, and remain the agent's own self-verification obligation. They
are not counted as passes.

### 8.2 Forward closure is unverifiable from the artifact alone

The design references `S-001` to `S-016`, but `output.md` declares no statement register
section, so the statements exist only inside the agent's reasoning. D4.1 and D4.3 can
therefore check that a trace is *present*, not that it points at a real statement, and
A15.1 cannot be checked at all. Closing this needs either a statement register in the
output contract or the register carried in `structured_output`.

### 8.3 The runtime was rewritten mid-run by a concurrent process

Between this run's dispatch and its completion, `runtime/framework_runtime.py` was replaced
by a multi-phase implementation (0.2.0 to 0.3.0) adding `state_engine.py`, a per-phase state
store, gates, and `verify_multi_phase.py`. That work was not part of this task and has not
been altered here.

The consequence: `complete --run-id` no longer exists in the form that created this run, and
0.3.0's `complete --run-id --phase` cannot load a run directory that carries no `state.json`.
The run was therefore closed by `runtime/close_legacy_run.py`, which validates the artifact
already on disk through the registered Validation Engine with the frozen envelope, emits its
events through the runtime's own `RunLedger` so every event is canonical, and refuses any run
that already carries a 0.3.0 state store or whose artifact fails validation. It never invokes
an agent and never writes an artifact. It should be deleted once no pre-slice-3 run directory
remains.

The generalization in section 6 was carried forward into 0.3.0 by that concurrent work: the
current runtime still resolves the architect phase, still selects `design_validator` from the
artifact registry, and still refuses a phase with no registered validator.

## 9. Residual Items

1. The three decision records are at `Proposed` and unaccepted. Acceptance belongs to the
   Design Gate owners in `workflows/workflow-gate-matrix.md`, never to the producing agent.
2. Nine open decisions are recorded, none blocking. `Q-001`, on whether a new agent identity
   is required, would change the selected option if answered the other way.
3. S04, S05, and S10 remain unregistered. No routed phase requires them.
4. Four of the six `implement-feature` phases still have no registered capability. That is
   recorded as gap 1 in `runtime/README.md`.
