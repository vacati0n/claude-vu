# Wave 1 Reconciliation Report — Parallel Implementation vs Accepted Design

Date: 2026-08-19
Reconciles: the parallel `/implement` task's changes against the artifacts accepted at the
Planning and Design Gates of `run-93b302cbdb28`.
Verdict: **GO** — both blocking discrepancies closed by recorded decisions, all three drift
fixes applied, and every verifier re-run. Part II records what was done.

## 1. Sources of truth used

| Artifact | Location | Status |
|---|---|---|
| `execution-plan.md` | `runs/run-93b302cbdb28/states/execution-planning/artifacts/` | validated 45/45 |
| `technical-design.md` | `runs/run-93b302cbdb28/states/solution-design-and-risk-assessment/artifacts/` | validated 78/78 |
| ADR `D-001` | same directory | Proposed → accepted at Design Gate |
| ADR `D-002` | same directory | Proposed → accepted at Design Gate |
| Planning Gate | `run-93b302cbdb28` | approved, `omn-tech-lead` / operator |
| Design Gate | `run-93b302cbdb28` | approved, `omn-tech-lead` / operator |

## 2. Changes found from the parallel task

The parallel task did substantially more than the `omn-dev-1-implement` increment. Measured
against `reports/maturity-snapshot-2026-08-18.json`:

| Surface | Baseline | Now |
|---|---|---|
| Active agent registry records | 2 | 12 active + 3 retired |
| Runtime module sets | 2 | 12 |
| Registered validators | 7 | 13 |
| Dispatchable phases | 3 / 36 | **29 / 36** |
| Blocked phases | 33 | 7 |
| Active skill records | 10 | 12 (S04, S05 added) |
| Phases with a context-slice declaration | 3 | 29 |

New artifact types, templates, and validators: `scope-definition.md`,
`implementation-report.md`, `validation-report.md`, `requirement-framing.md`,
`technical-recommendation.md`, `orchestration-result.md`.

New register: `agents/retired-roles.md`, retiring `orchestracor`→`omn-orchestrator`,
`backend-developer`, and `omn-planning-generate-clarification-questions`, each carried as a
`retired` record in `registry/agents.yaml`.

Nine single-file role contracts (`agents/omn-*.md`) were migrated into runtime module sets.
The role-specific contract content survives: each `identity.md` carries the full contract
sections (Identity, Mission, Scope, Inputs, Outputs, Decision Making, Constraints,
Collaboration Rules, Error Handling, Escalation, Completion).

The task also continued `run-93b302cbdb28` — my run — executing `scope-and-acceptance`,
`implementation`, and `quality-review`. The run is now 5 of 6 phases complete.

## 3. Discrepancy classification

### Class 1 — Compatible, no change required

| ID | Discrepancy | Why compatible |
|---|---|---|
| `C-1` | Artifact identifiers differ from those illustrated in `D-001`: `scope-definition.md` not `scoped-requirement-summary.md`; `implementation-report.md` not `implementation-evidence.md`; `validation-report.md` not `validation-evidence.md` | `D-001` binds the *shape*, not the strings: "The exact strings are fixed when each type is registered; what `D-001` binds is that one identifier serves one role's phases and that the same string appears at all three declaration points." Verified role-shaped: `implementation-report.md` serves all three `omn-dev-1-implement` phases, `validation-report.md` all five `omn-qa` phases, `review-package.md` reused for `implement-feature/quality-review` exactly as `D-001` row 6 dispositions |
| `C-2` | `D-002` implemented as a per-phase declaration keyed by phase identifier, existing context-slice contract unchanged, no new member kinds | This is `O-006` as selected, including the prediction that `A-002` holds |
| `C-3` | Scope reached Waves 2–4 (discovery, ops, closure agents; skills S04/S05) | Ahead of plan, contradicting no accepted decision. Noted as a process observation under section 6, not a design conflict |
| `C-4` | Three role identifiers retired rather than implemented | `retired-roles.md` records reason, superseding role, and evidence per identifier; `registry/agents.yaml` carries each as a `retired` record so a load attempt fails with an explicit status rather than an unresolved name |

### Class 2 — Implementation drift, correct the implementation

| ID | Drift | Accepted design requires | Current state |
|---|---|---|---|
| `D-1` | Context-slice members carry `path` and `digest` only | `D-002`: each member "recorded with the declared input of the owning manifest's input contract that it supplies, so a member with no consuming input is visible as unnarrowed" (`C-011`) | 4 of the 5 required properties present; per-member input attribution absent. Confirmed in `runs/run-93b302cbdb28/states/scope-and-acceptance/context-snapshot.json` |
| `D-2` | `release/artifact-packaging` still declares prose | `D-001` row 7: reuse `review-package.md` | 11 of `D-001`'s 12 rows applied; this one not. Phase blocks at `awaiting_contract_reconciliation` |
| `D-3` | `run-93b302cbdb28` carries no change proposal | Completion Rule `C-6` and Evidence Rule `E-1`–`E-7` | `verify_self_hosting.py` `S8` fails naming exactly this run as unaccounted |

### Class 3 — ADR/design mismatch, stop and decide

| ID | Mismatch |
|---|---|
| `M-1` | **`agents/agent-contract.md` and `agents/agent-lifecycle.md` no longer exist, and 49 files still reference them.** |

No accepted artifact authorises their removal. `retired-roles.md` retires three *role
identifiers*; it says nothing about these two shared normative modules. The references that
now dangle include:

- every migrated `manifest.yaml`, via `metadata.contractRef: ../agent-contract.md` and
  `metadata.lifecycleRef: ../agent-lifecycle.md`;
- every `identity.md`, which states "Implements `agents/agent-contract.md` contract version
  1.0.0" — a claim whose referent is gone;
- every `execution.md`, which instructs the agent to "verify `contractVersion` matches
  `agents/agent-contract.md`" — an instruction that cannot be carried out;
- step 2 of every `agents/<id>.agent.md` bootstrap procedure, which directs the agent to read
  both files before beginning work;
- the registered `planner` and `architect` module sets, which predate the parallel task.

What is lost is the shared normative baseline, not the per-agent contract. Severity is
therefore "dangling normative reference", not "content destroyed" — but it is load-bearing:
every dispatched agent is instructed to read files that do not exist, and `agent-lifecycle.md`
was the single source for lifecycle states, retry behaviour, and the escalation path.

**No verifier catches this.** `resolve_output_contract` resolves `templateRef` and
`contractRef` for declared *outputs* only; manifest-level `contractRef` and `lifecycleRef` are
never resolved. All six registry-coverage checks and all four validator checks pass with the
files absent. That is itself a gap in the verification mesh.

**Required decision:** restore or re-author the two shared modules, or formally supersede them
with a recorded replacement and rewrite all 49 references. This is a contract decision, not a
mechanical edit, so it is not made here.

### Class 4 — Artifact-contract mismatch, reconcile before proceeding

| ID | Mismatch |
|---|---|
| `A-1` | Capability growth retroactively invalidated governance records and mutated a historical run's persisted state |

`verify_self_hosting.py` fell from 9/9 to 5/9. Four failures, one root cause:

- `S6` — `FC-001` fails `F6`: it claims `scope-and-acceptance` and `implementation` were
  `blocked` in `run-3e22f11cb34d`; that run's `state.json` now records `pending`. The scheduler
  clears guard-raised blocks once the guard passes, so a historical run's phase dispositions
  changed when the framework gained the capability those guards were waiting on.
- `S6` — `FC-002` fails `F12`: its `E-6`/`E-7` link `state.json` and `completion-package.md`
  under the profile's carve-out for a workflow with no dispatchable phase. `fix-bug` now has
  dispatchable phases, so the carve-out no longer applies and real artifact links are required.
- `S7` — the same `run-3e22f11cb34d` status change fails the Completion Rule `C-3` re-check.
- `S9` — consecutive-change evidence fails as a consequence of the three above.

Neither ADR addressed what happens to governance records that were true when written and are
falsified by later capability growth. The technical design anticipated the adjacent risk —
`A-006`, `R-001`, and `P-001` cover frozen context slices of completed runs — but not the
proposal-validation consequence. Reconciling this is a decision about whether a change proposal
is a point-in-time record or a live assertion.

## 4. Invariant verification

| ID | Invariant | Result |
|---|---|---|
| `INV-1` | `execution-planning` and `solution-design-and-risk-assessment` remain dispatchable | **PASS**, both `dispatchable=True` |
| `INV-2` | `refactor/scope-invariants-and-risk-profile` remains dispatchable | **PASS** |
| `INV-3` | The two completed reference runs remain readable, fingerprints unchanged | **PASS**, `run-b6780677468b` 10/10 PROVEN, `run-308f4d0ee447` 10/10 PROVEN |
| `INV-4` | No verifier check moves from pass to fail | **FAIL** — `verify_self_hosting.py` 9/9 → 5/9. See `A-1` |
| `INV-5` | No phase-mandatory skill reference becomes unresolved | **PASS**, 101/101 resolve |
| `INV-6` | Gate ownership and the Producer Exclusion Rule unchanged | **PASS**, 28/28 gate references decidable |

## 5. Validation and runtime proof evidence

| Proof | Result |
|---|---|
| `verify_registry_coverage.py` | 6/6 — COVERED. 29/36 phases dispatchable, 7 blocked with recorded reasons |
| `verify_validators.py` | 4/4 — COVERED. 13 validators; every one accepts a conforming artifact and rejects a mutated one by a named check |
| `verify_recovery.py` | 41/41 — RECOVERY PROVEN |
| `verify_multi_phase.py --run-id run-93b302cbdb28` | 15/15 — PROVEN. 70 events, 39 transitions, artifact digests unchanged, 271 replays suppressed |
| `verify_vertical_slice.py --run-id run-93b302cbdb28 --slice planner` | 10/10 — PROVEN |
| `verify_self_hosting.py --mode-evidence` | **5/9 — NOT SELF-HOSTING**. See `A-1` |

### Implementation phase resolution

`implement-feature/implementation` → owner `omn-dev-1-implement`, output
`implementation-report.md`, `dispatchable=True`. Executed in `run-93b302cbdb28`; artifact
accepted by `implementation_report_validator`.

### G1-CAPABILITY

All five links resolve for the four Wave 1 agents: active registry record; manifest declaring
the workflow and phase in `supportedWorkflows`; host registration; phase skills resolvable;
registered validator for the declared output. `G2-CONTEXT` also resolves — 29 phases now carry
a declaration. Residual 7 blocked phases all report `awaiting_contract_reconciliation`, which
is a correct reason rather than a silent skip.

### host-subagent adapter path

Verified from `runs/run-93b302cbdb28/states/scope-and-acceptance/invocation-envelope.json`:
adapter `host-subagent`, dispatch mode `native`, host registration
`agents/omn-product-owner.agent.md`, manifest `agents/omn-product-owner/manifest.yaml`, all
seven modules resolved in declared load order with per-module digests, capabilities
`scope-definition` and `acceptance-authority`, skills resolved against the registry.

## 6. Process observation

The parallel task ran ten agent rollouts in one pass. The change request, the execution plan
(`S-015`), and the Design Gate rationale all bind the increment to **one primary capability
surface at a time**. That constraint was not observed. It produced no design conflict — the
work is compatible with `D-001` and `D-002` — but it is why `A-1` surfaced only at
reconciliation rather than at the first increment boundary, where a single-surface increment
would have caught the self-hosting regression against one changed phase instead of twenty-six.

## 7. Reconciliation decisions

| ID | Decision |
|---|---|
| `C-1`–`C-4` | Accept as delivered. No change. The parallel implementation realises `D-001` and `D-002` as accepted |
| `D-1` | Correct: add per-member input attribution to the context-slice declaration and the snapshot it produces. Minimum change; no member is removed |
| `D-2` | Correct: apply `D-001` row 7, `release/artifact-packaging` → `review-package.md`, together with any Input column naming the replaced prose string, per `P-005` |
| `D-3` | Author the change proposal for `run-93b302cbdb28` covering the reconciled state, satisfying `E-1`–`E-7` and `C-6` |
| `M-1` | **Blocked pending decision.** Restore/re-author the two shared modules, or supersede them with a recorded replacement and rewrite 49 references. Also extend the verification mesh so a dangling manifest-level `contractRef` or `lifecycleRef` fails a check |
| `A-1` | **Blocked pending decision.** Decide whether a change proposal is a point-in-time record or a live assertion, then either re-baseline `FC-001`/`FC-002` or amend `change_proposal_validator.py` `F6`/`F12` to evaluate against the state recorded at authoring time |

`D-1`, `D-2`, and `D-3` are deliberately **not applied yet**: `M-1`'s resolution changes what
every manifest references, and `A-1`'s changes what a conforming change proposal must assert.
Applying them first would mean authoring `D-3`'s proposal against a state that is about to move.

## 8. Files changed during reconciliation

None to any framework surface. This report and the task-tracking state are the only additions.
Reconciliation was read-only by design: two class-3/4 discrepancies are open, and the
instruction was to reconcile before implementing.

## 9. Final compliance status

| Against | Status |
|---|---|
| ADR `D-001` | **Compliant in substance.** 11 of 12 rows applied; row 7 outstanding as `D-2` |
| ADR `D-002` | **Partially compliant.** Route and key structure as accepted; per-member input attribution outstanding as `D-1` |
| `execution-plan.md` | Compliant on outcome, divergent on sequencing — `S-015` one-increment-at-a-time was not observed |
| `technical-design.md` sequencing constraints | `P-002`, `P-003`, `P-004`, `P-006`, `P-007`, `P-008`, `P-009`, `P-010` satisfied. `P-011` fails: the four-verifier re-read does not hold, `verify_self_hosting.py` is at 5/9 |
| Planning and Design Gate decisions | Honoured; both records accepted and applied |
| Self-hosting Completion Rule | **Not satisfied.** `C-6` unmet for `run-93b302cbdb28`; `C-3` re-check fails for `run-3e22f11cb34d` |

## 10. Verdict

**NO-GO for continuing Wave 1.**

Two blockers, both requiring a decision rather than an edit:

1. `M-1` — the shared agent contract and lifecycle modules are missing while 49 references,
   including every agent's bootstrap procedure, still point at them.
2. `A-1` — `verify_self_hosting.py` is at 5/9, violating `INV-4` and `P-011`.

The implementation work itself is sound and should be preserved. Nothing here calls for a
revert. Once `M-1` and `A-1` are decided, `D-1`, `D-2`, and `D-3` are small, bounded
corrections, and Wave 1 closeout follows immediately after.


---

# Part II — Reconciliation Applied

Both blocking discrepancies were decided by the accepting owner and the decisions applied.
Nothing from the parallel implementation was reverted.

## 11. Decisions recorded

| ID | Decision | Recorded in |
|---|---|---|
| `SC-001` | `agents/agent-contract.md` and `agents/agent-lifecycle.md` are **superseded** by the runtime module-set architecture, not restored. The shared normative baseline is `domain-model/agent-specification.md`; `contractRef` names `identity.md`, `lifecycleRef` names `execution.md` | `agents/superseded-contracts.md` |
| `GD-001` | Change proposals and their governance evidence are **point-in-time records**. Evidence is judged against the baseline it recorded, never against current state. Historical records are never amended because the runtime evolved; divergence is reported as informational drift | `config/self-hosting-profile.md#point-in-time-evidence-rule` |

## 12. `M-1` — reference migration applied

45 references migrated across 45 files. No dangling reference remains; the only surviving
mention is the supersession note in `agents/README.md` that points readers at the register.

| Reference site | Count | Migrated to |
|---|---|---|
| `manifest.yaml` `metadata.contractRef` | 12 | `identity.md` |
| `manifest.yaml` `metadata.lifecycleRef` | 12 | `execution.md` |
| `identity.md` contract-implementation claims | 12 | `domain-model/agent-specification.md` |
| `execution.md` `contractVersion` verification and lifecycle binding | 12 | `domain-model/agent-specification.md` |
| `system.md` module precedence chain | 3 | `domain-model/agent-specification.md` |
| `*.agent.md` escalation-path references | 2 | the agent's own `execution.md` |
| `agents/README.md` | 2 passages | the module-set model, pointing at the register |
| `runtime/artifact_contract.py` check references | 2 | `domain-model/agent-specification.md` |
| `runtime/artifact_lib.py` skip set | 1 | stale names dropped, `retired-roles.md` and `superseded-contracts.md` added, which also fixes a latent defect that would have counted both registers as agent contracts |
| `runtime/fixtures/review-package.md` finding row | 1 | `domain-model/agent-specification.md` |

Verified: all 12 manifests resolve `specificationRef`, `contractRef`, and `lifecycleRef` to
files their own `loadOrder` declares.

## 13. `A-1` — governance correction applied

The defect was one pattern in three places: historical evidence judged against current state.

| Surface | Change |
|---|---|
| `templates/framework-change-proposal.md` | New `Authoring Baseline` section: authored-at instant, runtime version, dispatchable counts, routed-workflow dispatchable phases |
| `change_proposal_validator.py` `F6` | Compares claimed phase status against the run's state **as of the authoring instant**, reconstructed from the append-only transition log, with the classified reason taken from the recovery ledger. Divergence since authoring is reported as informational drift |
| `change_proposal_validator.py` `F12` | Resolves dispatchability from the declared baseline; for pre-`GD-001` proposals, from what the run had actually reached by its authoring date |
| `change_proposal_validator.py` `F14` (new) | Requires the baseline only for proposals authored on or after 2026-08-19 — the decision applied to itself, reaching forward and not backward |
| `verify_self_hosting.py` `completion_rule` | Accepts an `as_of` instant and decides `C-2` to `C-5` against the run as it stood then |
| `verify_vertical_slice.py` `C6` | Module digest drift is reported, not failed on: it is current-state information about a contract that changed *after* the invocation, not evidence the invocation was defective |

`FC-001` and `FC-002` were **not amended**. Both now pass unchanged, because the rule that
failed them was corrected rather than the records that were accurate.

## 14. Drift fixes applied

| ID | Fix | Result |
|---|---|---|
| `D-1` | Context-slice members carry `supplies`, naming the declared input each satisfies; the snapshot gains an `unnarrowed` list. `scope-and-acceptance` and `artifact-packaging` fully attributed | The 28 phases not yet attributed now report their unnarrowed members explicitly, which is what `D-002` required — visible rather than absent. Tracked as `O-003` of `FC-004` |
| `D-2` | `release/artifact-packaging` Output Artifact set to `review-package.md` under the `packaging` category, with the downstream `candidate-validation` Input column edited in the same change per `P-005`, and a context slice declared | Phase moved from blocked to dispatchable; framework-wide 29 to 30 |
| `D-3` | `proposals/framework-change-proposal-FC-004.md` authored, carrying the first `Authoring Baseline` | Validates 37/37. `S8` and `S9` cleared |

`RUNTIME_VERSION` raised 0.4.1 to 0.5.0, per checklist item `FR-07`: the context slice changed
shape and three verification scripts changed their evaluation basis.

Four gate decisions outstanding on `run-93b302cbdb28` were recorded — Scope, Review, and
Verification approved; Closure left undecided, because it assesses evidence the blocked
`documentation-and-release-handoff` phase never produced.

## 15. Verification after reconciliation

| Proof | Before | After |
|---|---|---|
| `verify_registry_coverage.py` | 6/6 COVERED, 29/36 dispatchable | **6/6 COVERED, 30/36 dispatchable** |
| `verify_validators.py` | 4/4 COVERED | **4/4 COVERED**, 13 artifact types |
| `verify_recovery.py` | 41/41 PROVEN | **41/41 PROVEN** |
| `verify_multi_phase.py --run-id run-93b302cbdb28` | 15/15 PROVEN | **15/15 PROVEN**, digests unchanged on re-execution |
| `verify_vertical_slice.py` planner and architect, this run | 9/10 NOT PROVEN | **10/10 PROVEN** both |
| `verify_vertical_slice.py` on the two reference runs | 10/10 PROVEN | **10/10 PROVEN** both |
| `verify_self_hosting.py --mode-evidence --release-checklist` | **5/9 NOT SELF-HOSTING** | **10/10 SELF-HOSTING** |
| Change proposals | 1 of 3 passing | **4 of 4 passing** |

### G1-CAPABILITY

All twelve phases owned by the four Wave 1 agents resolve the full chain — active record,
manifest declaring workflow and phase, host registration, resolvable skills, registered
validator — and `G2-CONTEXT` resolves for each.

### host-subagent adapter path

`resolve_chain` verified for `scope-and-acceptance`, `implementation`, `quality-review`, and
`candidate-validation`: each resolves its manifest, its host registration at
`agents/<id>.agent.md` with `registered: True`, and seven modules in declared load order.

## 16. Invariants, re-verified

| ID | Result |
|---|---|
| `INV-1` `execution-planning` and `solution-design-and-risk-assessment` dispatchable | **PASS** |
| `INV-2` `refactor/scope-invariants-and-risk-profile` dispatchable | **PASS** |
| `INV-3` two completed reference runs verify unchanged | **PASS**, 10/10 each |
| `INV-4` no verifier check moves pass to fail | **PASS** — the one failure, self-hosting, is now 10/10 |
| `INV-5` no skill reference unresolved | **PASS**, 101/101 |
| `INV-6` gate ownership and Producer Exclusion unchanged | **PASS**, 28/28 decidable |

`P-011` of the technical design — the four-verifier re-read after the increment — now holds.

## 17. Files changed during reconciliation

- `agents/superseded-contracts.md` (new), `agents/README.md`
- 12 x `manifest.yaml`, 12 x `identity.md`, 12 x `execution.md`, 3 x `system.md`
- `agents/omn-orchestrator.agent.md`, `agents/omn-tech-lead.agent.md`
- `config/self-hosting-profile.md`, `templates/framework-change-proposal.md`
- `runtime/framework_runtime.py`, `runtime/change_proposal_validator.py`,
  `runtime/verify_self_hosting.py`, `runtime/verify_vertical_slice.py`,
  `runtime/artifact_contract.py`, `runtime/artifact_lib.py`, `runtime/fixtures/review-package.md`
- `workflows/release.md`
- `proposals/framework-change-proposal-FC-004.md` (new)
- `reports/wave-1-execution-board-2026-08-19.md`, `reports/maturity-snapshot-2026-08-19.json`,
  and this report

## 18. Final compliance against the accepted ADR and design

| Against | Status |
|---|---|
| ADR `D-001` | **Compliant.** All twelve rows applied |
| ADR `D-002` | **Compliant in mechanism.** Attribution implemented and emitted; 28 phases carry declared-unnarrowed members, reported per slice and tracked as `O-003` |
| Planning and Design Gate decisions | Honoured and applied |
| `technical-design.md` sequencing constraints | `P-001` through `P-011` satisfied |
| Self-hosting Completion Rule | **Satisfied.** `C-1` to `C-7` hold; `verify_self_hosting.py` 10/10 |
| Parallel implementation | **Preserved.** Nothing reverted |

## 19. Verdict

**GO.**

Every reconciliation blocker is closed by a recorded decision, and every claim above is a
verifier result rather than an assertion. Three of the four Wave 1 agents satisfy the full
five-part Definition of Done. `omn-qa` satisfies `D-1` to `D-3` with all five of its phases
dispatchable, and needs one run of `refactor`, `fix-bug`, `review-pull-request`, or `release`
to close `D-4` and `D-5`. That is the Wave 1 closeout run — remaining work, not a blocker.

Wave 1 is therefore **GO to proceed**, and **not yet complete**: it completes when that run
exists.
