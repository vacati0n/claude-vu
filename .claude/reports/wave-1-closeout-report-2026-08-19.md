# Wave 1 Closeout Report — Delivery Core Agents

Date: 2026-08-19
Closeout run: `run-27e36c138498`, `/bugfix` over `fix-bug` v1.0.0, status **Completed**
Governance record: `proposals/framework-change-proposal-FC-005.md`, validated 38/38
Supersedes: `reports/wave-1-execution-board-2026-08-19.md`
Snapshot: `reports/maturity-snapshot-2026-08-19-closeout.json`

**Verdict: WAVE 1 COMPLETE.**

## 1. Final Definition of Done, per agent

| Agent | D-1 module set | D-2 entrypoint | D-3 registry record | D-4 completed run | D-5 validator pass | Status |
|---|---|---|---|---|---|---|
| `omn-product-owner` | done | done | done | done | done | **complete** |
| `omn-dev-1-implement` | done | done | done | done | done | **complete** |
| `omn-dev-2-reviewer` | done | done | done | done | done | **complete** |
| `omn-qa` | done | done | done | **done** | **done** | **complete** |

20 of 20 conditions satisfied, against 4 of 20 at the Day-1 baseline.

### Evidence per agent

| Agent | D-4: completed run as phase owner | D-5: artifact accepted by its registered validator |
|---|---|---|
| `omn-product-owner` | `run-93b302cbdb28/scope-and-acceptance` | `scope-definition.md` — `scope_definition_validator` 33/33 |
| `omn-dev-1-implement` | `run-93b302cbdb28/implementation`, `run-27e36c138498/fix-implementation` | `implementation-report.md` — `implementation_report_validator` 32/32 |
| `omn-dev-2-reviewer` | `run-93b302cbdb28/quality-review` | `review-package.md` — `review_package_validator` 31/31 |
| `omn-qa` | `run-27e36c138498/regression-validation` | `validation-report.md` — `validation_report_validator` 31/31 |

## 2. QA D-4 and D-5, verified explicitly

`omn-qa` owns five phases and none of them lies in `implement-feature`, the only workflow with a
completed run before this one. `fix-bug` was selected as the closeout workflow because its
`regression-validation` phase is QA-owned and reachable from a defect report.

**D-4.** `runs/run-27e36c138498/state.json` records `regression-validation` at status `completed`
with `completion.agent_id = omn-qa`. The run's ledger records the invocation
`inv-27e36c138498-04-001` against agent `omn-qa` v1.0.0 through adapter `host-subagent` in
`native` mode, resolving the host registration `agents/omn-qa.agent.md`.

**D-5.** `runs/run-27e36c138498/states/regression-validation/validation-report.json` records
`result: pass`, 31 of 31 checks passed, 3 declared not-machine-checkable, produced by the
registered validator `validation_report_validator` for artifact type `validation-report.md`.
The artifact's verdict is `pass-with-reservations`; the reservations are recorded, not waived.

## 3. The fix-bug runtime proof

First end-to-end completion of `fix-bug`. Five phases, five agents, four gates, one classified
failure recovered.

| # | Phase | Owner | Status | Artifact | Validator result |
|---|---|---|---|---|---|
| 1 | `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | `bug-analysis.md` | 30/30 |
| 2 | `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | `bug-analysis.md` | 30/30 |
| 3 | `fix-implementation` | `omn-dev-1-implement` | completed | `implementation-report.md` | 32/32 |
| 4 | `regression-validation` | `omn-qa` | completed | `validation-report.md` | 31/31 |
| 5 | `closure-and-communication` | `omn-orchestrator` | completed | `orchestration-result.md` | 34/34 |

| Gate | Decision | Owner role, non-producing |
|---|---|---|
| Triage Gate | approve | `omn-tech-lead` |
| Fix Gate | approve | `omn-dev-2-reviewer` |
| Verification Gate | approve | `omn-dev-2-reviewer` |
| Closure Gate | approve | `omn-documentation` |

Run status `Completed`: 5 phases completed, 0 blocked, 0 failed, 35 transitions.

### What the run had to survive

Three things went wrong and were handled by the framework's own paths rather than around them.

**The workflow could not be entered.** Planning the run first produced every phase waiting behind
a blocked `triage-and-impact`: its Output Artifact cell was prose, so it blocked at
`G1-CAPABILITY`, and `G3-PREDECESSOR` held the remaining four behind it. Four phases reported
dispatchable while none was reachable. The correction — giving the phase the `bug-analysis.md`
its owner's manifest already declared as its only output, editing the Input column that named
the replaced prose string in the same change per sequencing constraint `P-005`, and declaring the
phase's context slice — cleared the block, and re-planning the same run re-entered it and
re-evaluated the guards rather than starting a second one.

**An attempt was refused on policy.** `fix-implementation` attempt 1 declared writes to
`runs/run-93b302cbdb28/state.json` and `runs/run-c5a8d50d3238/state.json`. Its manifest's
`authorityScope.repositoryWrites.excluded` carries `runs/**`, so a change can never rewrite the
evidence assessing it. The Recovery Controller classified it `policy-failure`, non-retryable,
escalate. The cause was the operator's dispatch instruction requiring `verify_multi_phase.py`,
which writes replay bookkeeping into the run store it inspects. Cleared by recorded operator
policy exception; attempt 2 wrote no run-store path and proved it by digesting all 213 files
under `runs/` before and after each command group. The exclusion was not relaxed.

**Two verifier regressions were introduced and repaired.** Both were claimed as pre-existing in
the implementation report, both were disproved against measurements taken before dispatch, and
the claim was withdrawn rather than quietly amended.

| Check | Cause | Repair |
|---|---|---|
| `verify_validators.py` `V4` | This run committed real `bug-analysis.md` artifacts at severity `critical`. `conforming_instance` prefers a committed run artifact over a fixture, so the mutation anchor pinned to a fixture's `- Severity: high` stopped matching | The `bug-analysis.md` mutation is now a derivation reading the severity the instance carries, matching the pattern four other artifact types already use. Still caught by `B2` alone |
| `verify_multi_phase.py` `M6` on `run-c5a8d50d3238` | A completed historical run's delivery phase read `pending` instead of `blocked`, because the scheduler cleared a guard-raised block once capability arrived. The run did not change; the framework did | `M6` now replays the run's append-only transition log through the existing `GD-001` helpers, with the baseline instant from `run-ledger.json`. Since-cleared phases are reported as informational drift |

Each repair was checked for decisiveness, because a check repaired into one that cannot fail is
not repaired.

## 4. Final verification results

| Proof | Result |
|---|---|
| `verify_self_hosting.py --mode-evidence --release-checklist` | **10/10 — SELF-HOSTING** |
| `verify_registry_coverage.py` | 6/6 — COVERED; **31 of 36** phases dispatchable |
| `verify_validators.py` | **6/6 — COVERED**; 13 artifact types, `V5` and `V6` added by this run |
| `verify_recovery.py` | 41/41 — RECOVERY PROVEN |
| `verify_multi_phase.py --run-id run-93b302cbdb28` | 15/15 — PROVEN |
| `verify_multi_phase.py --run-id run-c5a8d50d3238` | 15/15 — PROVEN, restored from 14/15 |
| `verify_vertical_slice.py` × 4 (`run-b6780677468b`, `run-308f4d0ee447`, `run-93b302cbdb28` planner and architect) | 10/10 — PROVEN each |
| Change proposals `FC-001` … `FC-005` | 5 of 5 PASS |

One check does not pass, and it is not a regression.

`verify_multi_phase.py --run-id run-27e36c138498` reports **14/15**. The failing check is `M6`,
"the run traversed planning, design, and a delivery phase", which looks for `implement-feature`
phase identifiers. A `fix-bug` run has none, so the check is inapplicable to it by construction.
This is the pre-existing limitation recorded as `O-002` of `FC-003`, and the identical result was
measured against the earlier `fix-bug` run `run-c9bdf5dbca7a` in the Day-1 baseline, before any
change in this increment. Reporting the run as PROVEN would require the check to mean something
it does not.

### fix-bug resolves without unexpected blocks

All five phases resolve the full capability and context chain. No phase of `fix-bug` reports
`awaiting_capability_registration`, and none reports any other block.

```
triage-and-impact          omn-dev-1-bug-analyst   RESOLVED
root-cause-analysis        omn-dev-1-bug-analyst   RESOLVED
fix-implementation         omn-dev-1-implement     RESOLVED
regression-validation      omn-qa                  RESOLVED
closure-and-communication  omn-orchestrator        RESOLVED
```

### Framework movement, Day-1 baseline to closeout

| Metric | Baseline | Closeout |
|---|---|---|
| Active agent registry records | 2 | 12 active, 3 retired |
| Runtime module sets | 2 | 12 |
| Phase owners with a registry record | 2 of 12 | 12 of 12 |
| Registered validators | 7 | 13 |
| Dispatchable phases | 3 of 36 | **31 of 36** |
| Active skill records | 10 | 12 |
| Active workflows with a completed run | 1 | 2 |
| Completed runs | 2 | 3 |

## 5. Evidence preserved

No existing evidence was modified. The increment added: one run directory
`runs/run-27e36c138498/` with five phase artifact sets and their validation reports, one input
file, one change proposal `FC-005`, one maturity snapshot, and this report. The two `state.json`
writes recorded under the policy exception are verifier replay bookkeeping — no work item,
transition, event, gate decision, or artifact digest changed in either run, and both still verify
15/15.

## 6. Remaining out-of-scope items

None blocks Wave 1. Each is recorded with an owner and a route.

| ID | Item | Owner | Where tracked |
|---|---|---|---|
| `O-001` | No rule governs what the Output Artifact column must contain, while three consumers read it under three unstated requirements. The divergence runs both ways: a cell naming two artifacts blocks the phase while the coverage proof demands a validator for each. Correcting the remaining prose cells does not remove the cause | architect | `FC-004` `O-001`, `FC-005` `O-001`, narrowed with measured evidence by this run's root-cause analysis |
| `O-004` | No verifier resolves a manifest's `contractRef` or `lifecycleRef`, which is why 45 dangling references survived every check before `SC-001` | omn-qa | `FC-004` `O-004`. Partially addressed: `V5` and `V6`, added by this run, close the adjacent gap where a prose Output Artifact cell was never examined at all |
| `O-005` | Five phases across four workflows remain blocked at `awaiting_contract_reconciliation`. `review-pull-request` is worst affected, its blocked phase at row 2 of 5, so no pull request can reach a merge decision | architect | `FC-005` `O-005`. Same decision as `O-001` |
| `O-002` (FC-005) | `verify_multi_phase.py` writes replay bookkeeping into the run store it verifies, so no agent whose contract excludes `runs/**` can execute it. Verification that changes what it measures is operator-only | architect | `FC-005` `O-002`. Surfaced by this run's policy refusal |
| `O-003` (FC-005) | `omn-orchestrator` is routed the action of authoring the change proposal accounting for a run, but its manifest permits no repository write, so the routed role cannot perform it | omn-tech-lead | `FC-005` `O-003` |
| `O-004` (FC-005) | Five runs hold a durably blocked phase, not the two the operator's framing to the phase agents stated. The closure phase measured the store and corrected the record | omn-orchestrator | `FC-005` `O-004` |
| `O-002` (FC-003) | `verify_multi_phase.py` and `verify_vertical_slice.py` recognise only `implement-feature` phase identifiers, so a `fix-bug` or `refactor` run cannot be proven by either | omn-qa | `FC-003` `O-002`. Why this run reports 14/15 |
| `O-003` (FC-004) | 28 phases carry context-slice members with no declared consuming input. The mechanism reports them per slice as `unnarrowed` | architect | `FC-004` `O-003` |

Three of the eight were found by the agents of this run rather than by the operator, on evidence
the operator's own framing had understated.

## 7. Scope discipline

The run changed four files: `workflows/fix-bug.md`, `runtime/framework_runtime.py`,
`runtime/verify_validators.py`, and `runtime/verify_multi_phase.py`. The `triage-and-impact`
correction was made because the closeout run demonstrably required it — the empirical plan showed
every phase, including the QA phase this closeout depends on, waiting behind the blocked entry
phase. It was not made because the item was convenient to fix.

The five remaining prose-cell phases and the column contract were left untouched, as instructed,
and remain escalated to `architect`. Wave 1 scope was not widened. Wave 2 has not been started.

## 8. Verdict

**WAVE 1 COMPLETE.**

All four delivery core agents satisfy all five Definition of Done conditions, each backed by a
completed run and a registered validator's acceptance rather than by assertion. Every verifier
passes, with one inapplicable check reported as inapplicable rather than as a pass. The framework
is in self-hosting mode at 10/10, with five change proposals validating and every framework change
since Day 1 accounted for by a run.
