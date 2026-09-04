# Validation and Recovery Hardening -- Execution Report

**Date:** 2026-08-18
**Command:** `/implement` -- Validation and Recovery Hardening
**Runtime version:** 0.4.0 (from 0.3.0)
**Objective:** improve the reliability and confidence of autonomous execution.

## 1. Verdict

| Exit criterion | Status | Evidence |
|---|---|---|
| Validator coverage across all core emitted artifact types | **met** | `verify_validators.py` -- 4/4 checks, 6 artifact types, `reports/validator-coverage-2026-08-18.json` |
| Controlled retry observed in at least one induced-failure test run | **met** | `verify_recovery.py` -- 41/41 checks across 3 injected runs, `reports/recovery-verification-2026-08-18.json` |

Two things this report does not claim. Registering a validator removes one of the five
`G1-CAPABILITY` conditions for the phases that emit the newly covered artifacts; it does not make
those phases dispatchable, because their owner agents still hold no registry record, no manifest,
and no context slice. Dispatchable phases remain 3 of 36. And `review-package.md` is contracted
and validated but is not yet named in any Phase Model's Output Artifact column, so no phase routes
it. Both are recorded as gaps 7 and 8 in `runtime/README.md`.

## 2. What Changed

### 2.1 Validator coverage

Every artifact type the active Phase Models name as a file now has a registered validator.

| Artifact | Validator | Checks on a conforming instance | Emitting phases |
|---|---|---|---|
| `execution-plan.md` | `plan_validator.py` | 45/45, 5 not machine-checkable | 1 |
| `technical-design.md` | `design_validator.py` | 78/78, 10 not machine-checkable | 2 |
| `bug-analysis.md` | `bug_analysis_validator.py` | 29/29, 4 not machine-checkable | 1 |
| `investigation-report.md` | `investigation_report_validator.py` | 30/30, 4 not machine-checkable | 2 |
| `release-note.md` | `release_note_validator.py` | 31/31, 4 not machine-checkable | 1 |
| `review-package.md` | `review_package_validator.py` | 30/30, 4 not machine-checkable | not yet routed |

The two existing validators are hand-written because the Planner and Architect contracts declare
their own numbered check sets, and a validator for those must reproduce that numbering exactly.
The four new artifact types have no such check set: their owning agents ship prose contracts
rather than a `quality.md` module. Writing four near-identical validators over that authority
would have duplicated the same structural, field, vocabulary, and identifier logic four times, so
those rules are declared as data and executed by one engine, `artifact_contract.py`. Each
per-artifact module adds only what is specific to its artifact.

The artifact-specific checks are the owning agent's own decision rules and constraints, made
decidable:

| Check | Artifact | Rule, and where it comes from |
|---|---|---|
| `B1` | bug-analysis | every causal step cites an evidence identifier -- *"Require evidence for each causal claim"* |
| `B4` | bug-analysis | an unreproduced defect is not a complete diagnosis -- *"Validate reproducibility before final diagnosis"* |
| `B5` | bug-analysis | an unresolved critical defect records what is unresolved -- *"No closure of unresolved critical defects"* |
| `I2` | investigation-report | every evaluated option cites its evidence -- the agent's consolidation responsibility |
| `I3`, `I4` | investigation-report | every observation is confidence-marked and staleness-dated -- *"marks confidence, names stale assumptions"* |
| `I5` | investigation-report | contradictions are recorded, explicitly as none where there are none |
| `R3` | release-note | a declared contract change carries a compatibility statement |
| `R4`, `R5` | release-note | a partial or rolled-back release records an issue and its rollback criteria |
| `P3` | review-package | the severity summary recomputes from the findings -- *"No severity downscaling without evidence"* |
| `P4` | review-package | no unqualified approval over an unresolved critical or high finding -- *"No approval with unresolved critical findings"* |
| `P6` | review-package | approval is withheld when no test evidence was reviewed -- *"Missing test evidence blocks approval"* |

Judgement that is not decidable by inspection is reported as `not-machine-checkable` and remains
the agent's own obligation, in the same style the two existing validators established. Nothing is
silently skipped.

**Template revisions this required.** The three bare templates carried no provenance and no
identifiers, so a validator over them could only have checked section presence. Each is now at
version 1.1.0, with section titles and order unchanged:

- `templates/bug-analysis.md` -- added the metadata block, an Evidence Register, and a Causal
  Chain table whose rows must cite it.
- `templates/investigation-report.md` -- added the metadata block, and confidence and staleness
  columns on the Evidence table and evidence citations on the options table.
- `templates/release-note.md` -- added the metadata block and the Known Issues table.
- `templates/review-package.md` -- new. It records why four differently-named review outputs are
  one artifact type: each is a severity-classified findings set over a defined scope closing with
  a readiness decision, and the Category column carries the lens.

All four are registered in `registry/templates.yaml`, which previously held three records.

### 2.2 Classified retry policy

`recovery_policy.py` is the Recovery Controller. It decides policy and applies none: it performs
no transition, holds no state, and imports neither the state engine nor the runtime, so the policy
is testable independently of the machine that obeys it. `framework_runtime.py` maps a returned
classification onto whichever transition its state tables permit.

- **Classification.** Twelve failure classes, from the Failure Classification Matrix in
  `config/execution-engine.md`, extended with the classes `config/runtime.md#failure-classes`
  names that the matrix does not row out. Three are retryable: transport failure, output schema
  failure, and worker loss. An unrecognised class escalates rather than being treated as
  transient.
- **Discrimination at one detection point.** A rejected artifact is not one failure. An
  undeclared side effect is a policy violation that no repair pass undoes; a structural defect
  the Validation Engine named is the schema-correctable omission the retry-eligibility list
  admits. They are classified differently and act differently.
- **Bounded retry.** `config/runtime.md#retry-policy` quoted field for field: three attempts,
  exponential from a two-second base, doubling, capped at sixty seconds, jitter of plus or minus
  twenty percent. The cap applies after the jitter, so the field the profile calls a maximum is
  one.
- **Deterministic jitter.** Derived from the work item's idempotency key rather than drawn at
  random. A random draw would make the same failure produce a different envelope on each
  evaluation, breaking the replay guarantee the runtime rests on. Stability per work item and
  spread across work items is what jitter is for; unpredictability is not needed here.
- **The `Retrying` state.** `state_engine.py` now implements seven of the eight canonical task
  states, adding `retrying` with `available_at` and the four transitions
  `config/task-queue.md` declares for it. `Cancelled` remains the one unimplemented state.
- **Attempt accounting.** An attempt whose adapter never reported produced nothing to judge and
  is charged to `attempts_lost`, not to the budget -- `config/task-queue.md` makes lease expiry a
  recovery classification that does not itself mean failure. Repeated loss is bounded by the
  escalation trigger instead.

### 2.3 Structured failure envelopes

Every blocked transition emits one -- guard-raised blocks, rejected artifacts, exhausted budgets,
and rejected gates alike. The field set is the union of the recovery ledger requirements in
`config/runtime.md` and the escalation contract in `config/execution-engine.md`, which is what
that moment needs from both: class and detection point, chosen action and reason, retry position
and next deadline, impacted artifacts, required decision type, owners, proposed options ordered
least destructive first, and evidence references.

One field is the runtime's own addition. `clearing_action` is the exact command that resolves the
condition, because a structured failure that does not say what to do next is a diagnosis without
a prescription. Where no command can resolve it, it says so and why -- a budget-exhausted work
item reports that `release` will refuse, rather than pointing at a command that cannot succeed.

Two destinations, for two readers: `states/<phase>/failure-envelope.json` for an operator looking
at one stuck phase, and an append-only `recovery-ledger.json` for an auditor. Entries are marked
resolved in place rather than removed, because an entry that vanished on resolution would erase
the evidence that anything was recovered. `framework_runtime.py recovery --run-id <id>` prints
them.

## 3. Evidence: Failure Injection

`verify_recovery.py` drives three runs through the real command line, injecting one fault each at
the adapter boundary. The harness stands in for the agent adapter and nothing else: it writes the
artifact and the result envelope the adapter would have written, then hands control back. Every
transition, classification, and envelope asserted on is produced by the runtime.

The conforming artifact each run starts from is a plan the runtime itself already accepted in a
committed run, re-stamped with the new run's frozen digests. The injected fault is a single
surgical mutation -- one mandatory section renamed -- so every rejection is attributable.

### Run A -- `run-62db758f9671`: rejected, then repaired

```
execution-planning:  pending -> leased -> running -> retrying -> pending -> leased -> running -> completed
```

Attempt 1 was rejected (42/45 checks passed), classified `output-schema-failure` at detection
point `validation`, retryable, action `retry` with 1 of 3 charged attempts spent. The work item
moved to `retrying` with a deadline; the run projected the canonical `Retrying` lifecycle state; a
dispatch before the deadline was refused and reported it. After the backoff the scheduler promoted
the item, the re-dispatch carried three named failed checks back to the agent as a repair pass,
and attempt 2 was accepted at 45/45. The idempotency key was unchanged across both attempts. The
ledger entry is marked resolved, not deleted.

### Run B -- `run-aca5399b113f`: the budget bounds it

Three attempts, each returning the same invalid artifact, charged 1 then 2 then 3. The third
classification reported `budget_exhausted`, chose `escalate` rather than `retry`, and blocked the
work item with `awaiting_recovery_task` raised by `recovery-controller` -- not `failed`, because
the artifact exists and is still repairable evidence. A fourth attempt was refused:

```
RUNTIME FAILURE [policy-failure] execution-planning has spent 3 of 3 charged attempts;
releasing it again would exceed the retry budget its work item declares
```

The refusal changed nothing: the item is still blocked on the same condition with the same open
envelope. Three ledger entries survive, occurrences 1, 2, 3, actions `retry`, `retry`, `escalate`.

### Run C -- `run-d8870619db82`: a non-retryable failure is not retried

The artifact conformed (validation PASS) but the adapter declared a write to
`memory/architecture.md`, outside its permitted set. Classified `policy-failure`, non-retryable,
blocked with `awaiting_policy_exception` and required decision `policy-exception` -- with two of
three attempts unspent. No `retry_scheduled` event was emitted for the run at all. This is the
discrimination check: the policy decides by class, not by whether something failed.

### Guard-raised blocks, and policy closure

The same run A asserts that the five phases blocked at a guard also carry classified envelopes:
6 blocked work items, 6 guard-raised classifications across `G1-CAPABILITY`, `G4-GATE`, and
`G6-GATE-EVIDENCE`, each naming a required decision type and a clearing action.

A final scenario closes over every row of the matrix without inventing runs for failures no
current path can raise: for all twelve classes across five attempt positions, the chosen action
matches the row that declares it, no non-retryable class ever produces a retry, no budget is
exceeded, an unclassified failure escalates, backoff grows and is capped, and jitter is stable per
work item while spread across work items.

## 4. Evidence: Validation Summaries

`verify_validators.py` asks two questions of every artifact type. Coverage: every artifact a Phase
Model names as a file has a registered validator, and every registered validator module exists,
imports, and exposes `validate()`. Decisiveness: a validator that accepts everything and a
validator that rejects everything both report a result, and neither is a decision -- so each is
run over a conforming artifact, which must be accepted, and over the same artifact with one
declared mutation, which must be rejected *by the named check*.

| Artifact | Mutation | Caught by | All checks that failed |
|---|---|---|---|
| `execution-plan.md` | renaming a mandatory section | `V2.1` | `V2.1`, `V2.3`, `V2.4` |
| `technical-design.md` | renaming a mandatory section | `D2.1` | `D2.1`, `D2.3`, `D2.4`, `D17.1` |
| `bug-analysis.md` | disagreeing with the metadata block about severity | `B2` | `B2` |
| `investigation-report.md` | recommending an option the report never evaluated | `I1` | `C6.2`, `I1` |
| `release-note.md` | disagreeing with itself about the version | `R2` | `R2` |
| `review-package.md` | understating the high-severity finding count | `P3` | `P3` |

Conforming instances come from committed runs wherever one exists, because an artifact the runtime
has already accepted outranks a fixture; `execution-plan.md` and `technical-design.md` are read
from `runs/`, with their invocation envelopes, so the cross-artifact checks resolve. The other four
read `runtime/fixtures/`.

## 5. Regression

Every pre-existing proof still passes, unchanged:

| Proof | Result |
|---|---|
| `verify_vertical_slice.py --slice planner` | 10/10 -- PROVEN |
| `verify_vertical_slice.py --slice architect` | 10/10 -- PROVEN |
| `verify_multi_phase.py --run-id run-c5a8d50d3238` | 15/15 -- PROVEN |
| `verify_registry_coverage.py` | 6/6 -- COVERED |
| `verify_validators.py` | 4/4 -- COVERED |
| `verify_recovery.py` | 41/41 -- RECOVERY PROVEN |

`verify_multi_phase.py` check M14 re-executes the runtime against the committed run and confirms
the fingerprint is unchanged: 53 events and 26 transitions before and after, artifact digests
unchanged, and every repeated call recorded as a suppressed replay. (The cumulative replay count
in that check's detail line rises each time the check itself is run, which is the point of it.)
Adding a status to the state engine did not invalidate any recorded transition.

Run against the injected run A, `verify_multi_phase.py` reports 14 of 15 -- the one check that
does not hold is M6, which requires the run to have traversed planning, design, and a delivery
phase. The injected run stops after planning by design, so M6 is not applicable to it rather than
failing on it. M3 (transition legality), M5 (no completion without a lease and an invocation), M10
(event stream integrity), M11 (every blocked item reasoned), and M14 (idempotency) all pass across
the retry path.

## 6. Files

**Added**

| Path | Role |
|---|---|
| `runtime/artifact_contract.py` | declarative artifact contract engine (508 lines) |
| `runtime/recovery_policy.py` | Recovery Controller: classification, retry profile, envelopes, ledger (504) |
| `runtime/bug_analysis_validator.py` | Validation Engine for `bug-analysis.md` (187) |
| `runtime/investigation_report_validator.py` | Validation Engine for `investigation-report.md` (193) |
| `runtime/release_note_validator.py` | Validation Engine for `release-note.md` (180) |
| `runtime/review_package_validator.py` | Validation Engine for `review-package.md` (256) |
| `runtime/verify_validators.py` | validator coverage and decisiveness proof (271) |
| `runtime/verify_recovery.py` | failure injection proof (655) |
| `runtime/fixtures/` | one conforming reference artifact per new type, plus its README |
| `templates/review-package.md` | new canonical template |
| `reports/validator-coverage-2026-08-18.json` | machine-readable validation summaries |
| `reports/recovery-verification-2026-08-18.json` | machine-readable injection results |

**Modified**

| Path | Change |
|---|---|
| `runtime/framework_runtime.py` | six validator registrations; classification at every failure point; retry scheduling and promotion; failure envelopes on every blocked transition; the `recovery` command; retry position in the run ledger and the state table; version 0.4.0 |
| `runtime/state_engine.py` | the `retrying` status, its four transitions, `available_at`, `retry_due`, the `Retrying` run projection |
| `runtime/verify_multi_phase.py` | M2 now names seven persisted statuses |
| `runtime/README.md` | slice 5 section, failure classification and retry documentation, envelope documentation, coverage table, updated component status, gaps 3, 4, 7, 8 |
| `templates/bug-analysis.md` | version 1.1.0: metadata block, Evidence Register, Causal Chain table |
| `templates/investigation-report.md` | version 1.1.0: metadata block, confidence and staleness columns, option evidence citations |
| `templates/release-note.md` | version 1.1.0: metadata block, Known Issues table |
| `registry/templates.yaml` | four new records: bug-analysis, investigation-report, review-package, release-note |

The three injected run directories are retained as evidence:
`run-62db758f9671` (repaired), `run-aca5399b113f` (budget exhausted), `run-d8870619db82` (policy
violation), together with their inputs under `runs/inputs/recovery-injection-*.md`. Re-running
`verify_recovery.py` removes and recreates exactly those three; it refuses to remove any run
directory whose inputs it did not write.

## 7. Open Items

1. **Retry is scheduled, not driven.** A deadline is evaluated when a command next reads the run,
   so an unattended run does not advance past its own backoff. `next` reports the deadline;
   nothing fires at it. Closing this needs a process the runtime does not have.
2. **Rollback and remediation are decided, not executed.** A classification can choose them, and
   the envelope names the target, but no state is rewound automatically.
3. **No lease expiry timer.** Declaring an adapter lost is still an operator action. What follows
   the reclaim is now the runtime's.
4. **`review-package.md` is not routed.** Naming it in the four review phases' Output Artifact
   columns and in the owning agents' manifest `outputs` is an agent and workflow contract change.
   Until then `review-pull-request/structural-compliance` stays blocked with
   `awaiting_contract_reconciliation`.
5. **The four new validators are not yet reachable through a run.** Their phases need their owner
   agents registered with manifests, quality contracts, and context slices. Dispatchable phases
   remain 3 of 36.
6. **The escalation trigger counts a class across the whole run.** A phase that failed, recovered,
   and later fails the same way again accumulates toward the breaker threshold rather than
   counting within an attempt window. This is conservative -- it escalates sooner rather than
   later -- but it is not what a per-window breaker would do.
