# Runtime Contract Reconciliation Report — Closing the O-001 Remainder

Date: 2026-08-19
Governance record: **none authored.** See section 6 for the reason and the owner.
Routing status: **not routed.** This change was made outside self-hosting mode.
Baseline recorded: `validation/framework-validation-checklist.md` Phase 12
Relates to: `O-001` of `proposals/framework-change-proposal-FC-004.md`, `O-005` of
`proposals/framework-change-proposal-FC-005.md`

**Verdict: RUNTIME VERIFIED AND FROZEN. GOVERNANCE RECORD OUTSTANDING.**

This report is a dated evidence report under `SR-4` of `config/self-hosting-profile.md`, emitted by
an increment rather than routed as one. It is not a change proposal and does not stand in for one.

## 1. What was reconciled

Five phases were blocked at `G1-CAPABILITY` with reason `awaiting_contract_reconciliation`, each
because its Phase Model Output Artifact cell stated prose rather than naming a file. No new artifact
type was required: in every case an existing binding contract already declared the artifact.

| Workflow / phase | Owner | Cell before | Artifact named | Contract that already sanctioned it |
|---|---|---|---|---|
| `implement-feature/documentation-and-release-handoff` | `omn-documentation` | release note draft, closure package | `release-note.md` | `agents/omn-documentation/output.md` deliverable table, basis `release-handoff` |
| `investigate/publication` | `omn-documentation` | published findings package and decision-support summary | `release-note.md` | same table, basis `findings` |
| `research/findings-publication` | `omn-documentation` | final research package and decision communication | `release-note.md` | same table, basis `findings` |
| `review-pull-request/documentation-impact` | `omn-documentation` | documentation deltas and release-impact notes | `release-note.md` | same table, basis `documentation-delta` |
| `review-pull-request/structural-compliance` | `architect` | structural and security findings assessment | `review-package.md` | `runtime/review_package_validator.py` `producers` tuple already named `architect` for this phase |

A second, independent blocker was uncovered once the output contracts resolved. `G1-CAPABILITY`
returns before `G2-CONTEXT` is evaluated, so these five phases had never reached the context gate,
and none of them had an entry in `CONTEXT_SLICE_PHASE` — 31 slices declared for 36 phases, the five
missing ones being exactly the five blocked. Correcting the output contracts moved them from
`awaiting_contract_reconciliation` to `awaiting_capability_registration` until the slices were
declared.

## 2. Files changed

Contract reconciliation:

| File | Change |
|---|---|
| `workflows/implement-feature.md` | 1 Output Artifact cell |
| `workflows/investigate.md` | 1 Output Artifact cell |
| `workflows/research.md` | 1 Output Artifact cell |
| `workflows/review-pull-request.md` | 2 Output Artifact cells, 2 Input cells that quoted the superseded prose |
| `agents/architect/manifest.yaml` | `review-package.md` declared as a conditional output, for `structural-compliance` only |
| `templates/review-package.md` | its own tracking table named 2 rows as prose; both now name the file |
| `runtime/framework_runtime.py` | 5 `CONTEXT_SLICE_PHASE` entries declared |
| `runtime/verify_validators.py` | `OUTSTANDING_UNDECIDABLE_ROWS` emptied; `V5` detail states the cleared case |

Documentation drift correction:

| File | Change |
|---|---|
| `agents/README.md` | registration narrative; legacy-layout claim |
| `agents/agent-catalog.md` | 3 rows listing module-set agents as single-file/pending |
| `skills/agent-skill-matrix.md` | capability claim |
| `config/self-hosting-profile.md` | `C-3` rationale; `E-6`/`E-7` waiver condition |
| `runtime/README.md` | known gaps 1, 6, 7, 8, 9; numbering preserved because `FC-001` cites gap 7 by number |
| 5 workflow specifications | 7 `Phase Identifier Sources` rows reading "Owner has no runtime manifest." |
| `validation/framework-validation-checklist.md` | Phase 12, Runtime Baseline Freeze |

## 3. Verified state, measured 2026-08-19

Every command run to completion; exit codes read from the process, not from a pipe.

| Command | Verdict | Exit |
|---|---|---|
| `verify_registry_coverage.py` | 6/6 — COVERED | 0 |
| `verify_validators.py` | 6/6 — COVERED | 0 |
| `verify_vertical_slice.py` | 10/10 — PROVEN | 0 |
| `verify_multi_phase.py` | 15/15 — PROVEN | 0 |
| `verify_self_hosting.py` | 8/8 — SELF-HOSTING | 0 |
| `verify_recovery.py` | 41/41 — RECOVERY PROVEN | 0 |

| Measure | Value | Reported by |
|---|---|---|
| Phases dispatchable | **36 of 36**, 0 blocked | `C6` |
| Phase owners host-invocable | 12 of 12 | `C3` |
| Skill references resolving | 101 of 101 | `C4` |
| Gate references with a permitted decider | 28 of 28 | `C5` |
| Rows naming a decidable artifact | 36 of 36 | `V5` |
| Output Artifact reader agreement | `agree=36`, no drift | `V6` |
| Registered validators | 13 | `V2` |
| Context slices declared | 36 of 36 | `CONTEXT_SLICE_PHASE` |
| Rows recorded outstanding | 0 | `OUTSTANDING_UNDECIDABLE_ROWS` |

`verify_multi_phase.py` re-verified every committed run after `runtime/README.md` and four Phase
Models — all frozen context-slice members — were edited: 46 to 46 events, 22 to 22 transitions,
artifact digests unchanged.

## 4. Effect on the two recorded open items

| Item | Record | Effect |
|---|---|---|
| `O-001` | `FC-004`, owner `omn-tech-lead` | Its five-row remainder is decidable; `V5` finds no outstanding row. The item is **not formally closed**, because closing it belongs to a routed change record that does not exist. |
| `O-005` | `FC-005`, owner `architect` | Same five rows, stated from the `review-pull-request` side. Same status. |

Neither `FC-004` nor `FC-005` was edited. Both are signed records read against the baseline they
carry, per `GD-001` of `config/self-hosting-profile.md#point-in-time-evidence-rule`, and both still
state the pre-fix counts, correctly.

## 5. Items unchanged and still open

`runtime/README.md` known gaps 2, 3, 4 and 5 remain open and were re-verified as still accurate:
gates are recorded rather than solicited; retry is scheduled but nothing fires at a deadline;
`lease_expires_at` is carried but never enforced; `workflows/workflow-engine.md` has no planning
state and names a different owner than three Phase Models. `O-002`, `O-003` and `O-004` of `FC-004`
are untouched.

## 6. Why no change proposal accompanies this report

A change proposal was **not** authored, and authoring one would have required fabricating evidence.
The Evidence Rule of `config/self-hosting-profile.md` requires seven links, `E-1` to `E-7`, each
resolved against the filesystem, and states that "prose describing a run that no artifact supports
is rejected".

1. **`E-1` to `E-5` require a run.** No run carried this change. `E-1` demands
   `runs/<run-id>/execution-request.json`, and `E-2` exists specifically to prove the run "is the
   framework's own record rather than a directory named like one".
2. **`C-1` cannot be satisfied retroactively.** The Completion Rule requires that the change "was
   classified by `## Scope Rule` and routed by `## Routing Table` **before the work began**". The
   work began first. `C-1` is the one Completion Rule condition `verify_self_hosting.py` does not
   decide — `completion_rule()` decides `C-2` to `C-5` — so a proposal asserting it would pass every
   check while being false.
3. **`E-6` and `E-7` are now mandatory and their waiver is unreachable.** Both are required where the
   routed workflow has at least one dispatchable phase, and all seven now do.
   `change_proposal_validator.py` check `F12` decides that itself through the capability chain, so
   the condition "is not the author's to assert". Satisfying them would require phase artifacts from
   a run that would have to attribute already-applied edits to phases that did not perform them.

`verify_self_hosting.py` reports 8/8 today. That is accurate for what `S1` to `S8` ask: `S8` detects
a *run* unaccounted for by a proposal, and no run was created, so nothing fails. The gap is a change
that was never routed, which no verifier in the repository detects. It is recorded here rather than
left to inference.

**Owner and route.** Closing the record is `omn-tech-lead`'s decision, as owner of `O-001`. The
honest route is forward, not backward: open a routed run under the profile for the *next*
framework change and let it carry `O-001` and `O-005` to closure with real phase evidence, rather
than reconstructing a run for work already applied. `self_hosting.py route --intent capability-addition`
resolves that path today.

## 7. Freeze statement

The runtime baseline in `validation/framework-validation-checklist.md` Phase 12 is the frozen
reference. It is measured, not asserted, and Phase 12 states that where the table and a verifier
disagree, the verifier decides and the table is stale. A later change is accepted only against the
six commands and the five contract rules recorded there.
