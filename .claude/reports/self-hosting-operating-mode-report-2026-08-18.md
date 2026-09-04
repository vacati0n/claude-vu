# Self-Hosting Operating Mode — Execution Report

**Date:** 2026-08-18
**Command:** `/implement` — Self-Hosting Operating Mode
**Increment:** Phase 5 of `reports/self-hosting-execution-plan-2026-08-18.md`
**Runtime version:** 0.4.1 (from 0.4.0)
**Objective:** make framework development itself run through framework workflows by default.

## 1. Verdict

| Exit criterion | Status | Evidence |
|---|---|---|
| New framework changes are planned, executed, and reviewed via framework commands, not ad hoc | **met** | `verify_self_hosting.py --mode-evidence --release-checklist` — 10/10, `reports/self-hosting-2026-08-18.json` |
| Two consecutive framework changes completed in self-hosting mode | **met, three** | `run-3e22f11cb34d` → `run-c9bdf5dbca7a` → `run-0db4765d0eab`, each with a validated proposal under `proposals/` |

Reproduce:

```bash
python .claude/runtime/verify_self_hosting.py --mode-evidence --release-checklist
```

Two things this report does not claim. Routing every framework change through a framework command
is not the same as executing it with framework agents: three of thirty-six phases are dispatchable,
so most phases of every run block with a recorded reason and the operator performs that work against
the run. And the mode governs this repository's own development; it says nothing about a consumer of
the framework, which has no separate release train yet.

## 2. What Was Delivered

| Task | Deliverable | Executable form |
|---|---|---|
| One command profile for framework-internal change routing | `config/self-hosting-profile.md` — profile `framework-internal-change` v1.0.0: 6 scope rules, 7 routing rows, 7 evidence rows, 7 completion conditions | `runtime/self_hosting.py` (`classify`, `route`, `evidence`, `checklist`) |
| Change proposals must link run artifacts from framework execution | `templates/framework-change-proposal.md` + record in `registry/templates.yaml` | `runtime/change_proposal_validator.py`, registered in the `VALIDATORS` map |
| A release checklist for framework updates | `validation/framework-release-checklist.md` — 12 items, 10 mandatory, 7 executable | `verify_self_hosting.py --release-checklist` executes every command-mode item |
| Proof that the mode holds | `runtime/verify_self_hosting.py` — S1 to S10 | `reports/self-hosting-2026-08-18.json` |

Nothing here is spec-only. The profile is parsed and resolved rather than read: every routing row is
resolved through `resolve_command`, `resolve_workflow`, and `parse_phase_model`, the same resolvers
the runtime gateway uses, so a row naming an unroutable command fails verification.

### 2.1 The profile

One profile, because two would mean two answers to "which command carries this change".

| Change class | Command | Workflow | Entry phase |
|---|---|---|---|
| `decision-support` | `/investigate` | `investigate` | `problem-framing` |
| `external-research` | `/research` | `research` | `research-framing` |
| `defect-repair` | `/bugfix` | `fix-bug` | `triage-and-impact` |
| `structure-preserving-change` | `/refactor` | `refactor` | `scope-invariants-and-risk-profile` |
| `capability-addition` | `/implement` | `implement-feature` | `scope-and-acceptance` |
| `change-review` | `/review` | `review-pull-request` | `code-quality-review` |
| `framework-release` | `/release` | `release` | `readiness-assessment` |

The Scope Rule decides what is framework-internal, with exclusions taking precedence over
inclusions and a closed exemption set of four: run evidence, dated reports, proposals, and
interpreter output. Each exempt path exists for one reason — routing the evidence of a routed
change would recurse without terminating. `S3` probes every rule for reachability and proves the
exclusions bind.

### 2.2 The evidence requirement

Seven required links per change, checked against the filesystem, plus one agreement check: the
run's `command_id` must equal the command the profile routes the declared change class to.

The validator's value is that it refuses to take the author's word for the run. `F2` re-reads
`execution-request.json`. `F5` and `F6` re-read `state.json` and require every enqueued phase to be
accounted for with the status the runtime recorded and, where blocked, the reason it recorded. `F7`
recomputes every scope classification row against the profile. `F8` resolves every gate decision
against `workflow-gate-matrix.md`. `F13` compares the declared input types against the inputs the
run records. Thirty-seven checks in total, and `verify_validators.py` proves the validator decides
rather than accepts: mutating one evidence link to a path that does not exist is caught by `F3`.

### 2.3 The release checklist

Ten mandatory items and two advisory, each with an owner role the framework carries and each either
a command or a declared inspection. Seven are executed by `verify_self_hosting.py --release-checklist`;
all seven passed for all three changes.

## 3. Three Consecutive Changes in Self-Hosting Mode

| ID | Change | Class | Command | Run | Phases executed | Proposal |
|---|---|---|---|---|---|---|
| `FC-001` | Route `review-package.md` into the review workflow, closing known gap 7 | `capability-addition` | `/implement` | `run-3e22f11cb34d` | 2 of 6 (planner, architect) | 37/37 |
| `FC-002` | Repair the defaulted command on an existing run (`DEF-001`) | `defect-repair` | `/bugfix` | `run-c9bdf5dbca7a` | 0 of 5, all blocked with a reason | 37/37 |
| `FC-003` | Make the self-hosting surface discoverable from seven indexes | `structure-preserving-change` | `/refactor` | `run-0db4765d0eab` | 1 of 5 (architect) | 37/37 |

Each was classified and routed before the work began, carried by a run of the routed command, held
at its gates, and recorded in a proposal that links the run's own artifacts. Three registered agent
invocations produced validated artifacts: an execution plan at 45/45 and two technical designs at
78/78 each.

### 3.1 What self-hosting caught that ad hoc work would not have

This is the part worth reading. Every item below was found by the framework rejecting its own work.

**The architect's first design was rejected for a policy violation.** It wrote one file outside
`permitted_writes` and declared it. The runtime classified `policy-failure`, which is non-retryable,
emitted a failure envelope naming the clearing action, and blocked the phase with
`awaiting_policy_exception`. The same ingest also found six blocking validator failures the agent's
own 98-check self-verification had passed — including a design that named a `Quality Gate` the gate
matrix does not carry, and three decision records whose filenames the validator's discovery rule
could not see. The operator cleared the block, the runtime granted attempt 2, and the repaired design
validated 78/78.

**A runtime defect that blocked six of seven commands.** `DEF-001`: every subcommand takes
`--command`, defaulting to `implement`, and each calls `plan_run` first, so a subcommand issued
against an existing non-`implement` run re-planned it under `implement-feature` — injecting six
foreign work items into a `refactor` run's store and recording its real phases as contract
violations. The documented usage in `runtime/README.md` was the usage that corrupted the store. It
cost two runs, both recorded under `reports/` with their state and reason rather than quietly
deleted. Fixed by making an existing run's own record the authority for its command and refusing a
disagreeing `--command`.

**A wrong required-input list in the profile itself.** The first `/refactor` submission blocked at
`G5-INPUT`: the profile listed two inputs for `structure-preserving-change` and the architect input
contract requires three. The row was corrected and the reason recorded beside it.

**An Evidence Rule that forbade repairing defects.** `E-6` and `E-7` demanded a phase artifact and
its validation report from every routed change. No `/bugfix` run can produce either, because no phase
of `fix-bug` is dispatchable — so the rule as first written made four of seven change classes
unroutable to completion. Both are now conditional on dispatchability, and `F12` decides that
condition by resolving each phase through the runtime's capability chain rather than accepting the
author's claim.

**A frozen-slice digest moving under an in-flight run.** Editing `runtime/README.md` for `FC-002`
moved a digest the `FC-003` design cited between its two attempts. The agent re-checked its facts
against the new snapshot, moved only the citation, and recorded the movement — which is the risk its
own design had recorded one attempt earlier.

**The architect's second design was rejected on a vocabulary check.** `D12.3`: risk class
`compliance`, which is not in the declared set. Retryable `output-schema-failure`, 2.263s of
backoff, one repair pass, 78/78.

Six findings, none of which a document review would have produced.

## 4. The Bootstrap Exception

The profile could not route the increment that authored it. That increment — the four deliverables in
section 2 — is recorded here as the bootstrap, not as a self-hosted change. It is the only such
exception, and every framework change after it is bound by the Completion Rule. Two amendments were
made to the profile after `FC-001` and before `FC-003`, both to correct the profile against what the
runtime actually requires, and both are recorded in the profile beside the rule they changed:

| Amendment | Cause |
|---|---|
| `structure-preserving-change` requires `business-intent` | The first `/refactor` run blocked at `G5-INPUT` |
| `E-6` and `E-7` conditional on dispatchability, decided by `F12` | No `/bugfix` run can produce a phase artifact |

## 5. Verification

| Proof | Command | Result |
|---|---|---|
| Self-hosting mode | `verify_self_hosting.py --mode-evidence --release-checklist` | 10/10 — SELF-HOSTING |
| Registry coverage | `verify_registry_coverage.py` | 6/6 — COVERED, dispatchable 3 of 36, unresolved 0 |
| Validation Engine | `verify_validators.py` | 4/4 — COVERED, 7 artifact types, each accepted and each mutation caught by its named check |
| Recovery | `verify_recovery.py` | 41/41 — RECOVERY PROVEN |
| Committed run evidence | `verify_vertical_slice.py --run-id <run>` | 10/10 PROVEN for `run-c5a8d50d3238`, `run-308f4d0ee447`, `run-b6780677468b`, `run-3e22f11cb34d` |
| Multi-phase state machine | `verify_multi_phase.py --run-id run-c5a8d50d3238` | 15/15 PROVEN |

`RUNTIME_VERSION` moved 0.4.0 → 0.4.1 for `FC-002` and stayed there for `FC-003`, which changed no
runtime module. Every committed run was re-verified after the version bump and after each edit to a
frozen-slice member.

## 6. Metrics Against the Roadmap

| Metric | Before | After |
|---|---|---|
| Framework changes routed by a command profile | 0 | 3 of 3 |
| Change classes with a resolvable route | 0 | 7 of 7 |
| Registered validators | 6 | 7 |
| Artifact types proven decisive by mutation | 6 | 7 |
| Framework release checklist items | 0 | 12, of which 7 executable |
| Runs inside the self-hosted window unaccounted for by a proposal | n/a | 0 |
| Dispatchable phases / declared phases | 3 / 36 | 3 / 36 |
| Routed artifact types with no emitting phase | 1 (`review-package.md`) | 0 |

The dispatchable ratio is unchanged and that is the honest number: this increment changed how a
framework change is decided, recorded, and proven, not how many phases an agent can execute.

## 7. Deferred and Open, Recorded Not Hidden

| Item | Owner | Where recorded |
|---|---|---|
| Three review-producing phases keep prose Output Artifact entries | omn-product-owner | `FC-001` `O-001`, known gap 7 |
| `review-pull-request/structural-compliance` still blocks on contract reconciliation | architect, omn-tech-lead | `FC-001` `O-002`, known gap 7 |
| `design_validator.py` `D15.1` cannot match a three-word gate name | omn-tech-lead | `FC-001` `O-003` |
| `design_validator.py` `D17.1` discovers decision records case-sensitively, which an agent cannot correct on a case-insensitive filesystem | architect | `FC-001` `O-004` |
| `fix-bug` has no dispatchable phase, so a defect repair is carried entirely by the operator | omn-tech-lead | `FC-002` `O-001`, known gap 8 |
| Seven indexes now carry the same reference with no mechanical drift check | omn-documentation | `FC-003` `O-001` |
| `verify_vertical_slice.py` and `verify_multi_phase.py` recognise only `implement-feature` phase identifiers, so a `refactor` run's executed phase cannot be proven by either | omn-qa | `FC-003` `O-002` |

The last item is the sharpest limit this increment leaves. `run-0db4765d0eab` executed one phase and
the runtime accepted its artifact at 78/78, yet neither proof script can attest to it, because both
were written around one workflow's phase names. Generalising them routes as `capability-addition` and
is the natural next increment.

## 8. Files Added and Changed

Added: `config/self-hosting-profile.md`, `templates/framework-change-proposal.md`,
`validation/framework-release-checklist.md`, `runtime/self_hosting.py`,
`runtime/change_proposal_validator.py`, `runtime/verify_self_hosting.py`,
`proposals/framework-change-proposal-FC-00{1,2,3}.md`, four records under `reports/`, and four run
input documents under `runs/inputs/`.

Changed: `runtime/framework_runtime.py` (`VALIDATORS`, `stored_command`, `plan_run`, `cmd_dispatch`,
`add_request_args`, `RUNTIME_VERSION`), `runtime/verify_validators.py` (governance-artifact source
and one mutation), `registry/templates.yaml` (one record),
`workflows/review-pull-request.md` (one Phase Model cell), and the seven indexes `FC-003` names.
