# Framework Change Proposal: A Rejected Gate Is No Longer a Dead End — the Runtime Now Executes the Rollback It Classifies, Under a Recorded Human Authorisation, Superseding the Target's Completed Downstream Cone While Every Committed Artifact Stays Immutable

```yaml
frameworkChangeProposal:
  proposalId: FC-013
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-3e6f6a248b99
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-013
- Change title: Give the runtime an executable rollback after a gate rejection — two authorised exits from a terminal status, a `rollback` command a listed non-producing gate owner issues, supersession of the target's completed downstream cone as attempt n+1 with attempt n immutable, same-item gate re-arm with an append-only `decision_history`, class-aware clearing actions, and the matching contract text — so that a rejected gate returns the work to the phase that must rebuild it instead of stranding the run
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-3e6f6a248b99
- Authored on: 2026-09-07

## Authoring Baseline

- Authored at: 2026-09-07T14:32:00Z
- Runtime version: 0.6.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

This record is retrospective by a short interval. Run `run-3e6f6a248b99` was submitted at
2026-09-06T09:49:30Z under runtime version 0.5.0 and its Closure Gate was decided at
2026-09-07T14:20:22Z; this proposal was authored roughly twelve minutes after that decision, in a
separate operator-dispatched pass outside any phase of the run, because the closure phase's
permitted writes exclude `proposals/`. It is assembled from the run's committed evidence, read
directly, and nothing in it was available to the Closure Gate that approved the run. Its function
is the one the closure record scheduled as `FU-001`: give the run the governance record the
profile's Completion Rule `C-6` requires and that the run closed without. The baseline runtime
version is 0.6.0, not the 0.5.0 the run was opened under: the `RUNTIME_VERSION` constant was moved
by the operator before the Closure Gate, the run's reporting ledger was rewritten under 0.6.0 when
that gate was decided, and the consequence for runs opened under 0.5.0 is recorded under `FR-07`
and `O-017`. The 37-of-37 figure was read from the registry-coverage verifier at the authoring
instant; the five routed phases were each dispatched and completed by the run itself.

## Change Statement

- Objective: make a gate rejection recoverable inside the run that received it. Before this change
  the runtime classified a rejection as a `rollback` and every workflow's Failure Recovery section
  promised the return to the implementing phase, but nothing executed it: the state engine's
  transition tables had no exit from `completed` for a state item or from `failed` for a gate item,
  `record_gate_decision` moved the gate to `failed` without touching the phase it closed, guard
  `G4-GATE` held every successor on `awaiting_recovery_task` for as long as the decision read
  `rejected`, and the failure envelope prescribed a `release` command that raised a transition error
  when executed. The stranded run `run-4c51600606df` (the CKA-06 `/implement` run, Review Gate
  rejected by `omn-qa` on 2026-09-06T09:05:36Z) was the live reproduction, and the consumer
  `omn_agent/fix_comments.py` was built on the contrary assumption and could not complete a round.
  Defect report `runs/inputs/gate-rejection-rollback-dead-end-defect-report.md`, classified severity
  high and reproducibility deterministic at triage on the analyst's own executions, with the Triage
  Gate confirming high rather than critical because a new run remained possible.
- In scope: the state engine gains exactly two authorised exits from a terminal status — a state
  item `completed -> pending` under trigger `superseded`, refused by the engine unless a supersession
  record carrying an authorisation id accompanies it, and a gate item `failed -> pending` under
  `rollback_authorised` — with terminality restated as terminal except for that one engine-checked
  pair; a new `rollback` subcommand that records a human rollback authorisation from a listed,
  non-producing gate owner under the same role and producer-alias checks as `gate`, requires the gate
  to stand `failed` with decision `rejected`, takes an explicit `--target` that is the closed phase or
  a completed hard predecessor of it, charges the re-entered attempt against the retry budget and
  refuses when the budget is spent; a supersession range equal to the target's completed downstream
  cone — the target and every completed phase that transitively hard-depends on it, the closed phase
  always included — each superseded under one authorisation id, the prior completion moved
  unmodified into an append-only `supersessions` list, attempt n+1 dispatched to an attempt-scoped
  artifact path while the payload digest keeps the canonical path, attempt n's artifact byte-identical
  at its committed path, and the attempt's envelope, result, ledger and validation files snapshotted
  under `attempts/<n>/`; a refusal with no store change when an approved gate stands over any phase
  in the range, the closed phase included; same-item gate re-arm with the rejected decision, role,
  decider, rationale and timestamp appended to an append-only `decision_history` and the gate item
  labelled `gate-rejection` at rejection and cleared at re-arm; a scheduler correction returning a
  guard-raised block to `pending` for both work types when its guards fall to wait; an auto-approval
  hold on any gate carrying a decision history or whose sibling on the same phase stands rejected;
  class-aware clearing actions naming the executable `rollback` with `--decided-by <who>` as the
  only placeholder, and live derivation of that action by `next` (which names the rollback first,
  exits 3 and withholds a sibling gate decision while a rejection stands) and by `recovery` (which
  shows the persisted string beside it); `verify_recovery.py` Run D with checks D0 to D27 including
  D5a, D5b, D5c and the negative D6a, an admissibility table matching every envelope's clearing action
  and executing Run D's verbatim; `verify_multi_phase.py` M4, M12 and M13 extended over the
  authorised exits and every superseded completion; the consumer `omn_agent/fix_comments.py` issuing
  `reject` then `rollback` with the same role and the task's fix phase as target; the new unit module
  `tests/test_gate_rollback.py` (34 tests) and extensions to `tests/test_gate_policy.py`,
  `tests/test_framework_runtime_render.py`, `tests/test_fix_comments.py` and `tests/test_update.py`;
  the contract text in `runtime/README.md`, `config/execution-engine.md`, `config/runtime.md` and
  `docs/USER-GUIDE.md` with `docs/user-guide.html` regenerated by its renderer; and the mirrors under
  `omn_agent/_bundled_payload/` regenerated by the repository's own sync command. Twenty-four change-set
  entries, `C-001` to `C-024` of the attempt-2 implementation report. Two operator passes after the
  run's last phase artifact and before the Closure Gate are also in scope and recorded rather than
  absorbed: the CR-005 wording correction at three sites plus mirrors, and the `RUNTIME_VERSION`
  move from 0.5.0 to 0.6.0 in source and mirror.
- Out of scope: the run-status projection and aggregator defect — `project_run_status` and
  `maybe_aggregate` read state items only, so `run_completed` fires while a final gate is undecided
  or rejected, and a supersession after `run_completed` is now possible — placed out of scope by the
  architect's decision memo, carried as residual risk `R-001` and as `FU-002`, and exercised live on
  this very run (`O-001`); the active-descendant case, ruled by the architect after validation and
  routed as `FU-004` because it changes behaviour beyond the accepted fix scope; the M6 verifier
  extension and a rollback-carrying Run E, ruled and routed as `FU-005`; a refusal inside the `gate`
  command itself of an approval on a gate whose sibling stands rejected, which no correction request
  asked for and the ruling addresses by ordering (`FU-011`); the two `PreChangeEquivalence` failures
  of the in-flight CKA-06 change's untracked handbook fixture, attributed by the Fix Gate to that
  change and routed to its attempt-2 review; the release readiness of the shared working tree, which
  is `omn-tech-lead`'s judgement; performing the rollback on `run-4c51600606df`, an operational action
  outside every framework agent's authority, performed by the operator after the Closure Gate and
  recorded here as fact under `O-005`; and the release note, which `omn-documentation` writes from
  the closure record (`FU-008`).
- Acceptance basis: the seventeen acceptance criteria of the validation report — the ten
  fix-strategy conditions of the root-cause analysis, its validation plan, and the architect's range
  rule (b), CR-001 refusal rule and stranded-run ordering rule — measured by `omn-qa` at
  `regression-validation` on the attempt-2 change: 14 met, 0 not met, 3 blocked. Every behavioural
  criterion (`AC-001` to `AC-011`, `AC-015` to `AC-017`) is met on executed evidence: the two
  authorised exits and the refusal of 13 of 14 bare exits on a synthetic store, every `rollback`
  refusal with store equality, supersession with attempt 1 byte-identical and keys preserved through
  the rollback on byte-identical copies of the stranded run, the same-item re-arm, the scheduler
  correction for both work types, the auto-approval hold, the class-aware and live-derived clearing
  actions, the cone range on the fix-bug shape, and the approved-sibling refusal. The three blocked
  criteria are placed where each is settled and none is read as met: `AC-012` (full suite and every
  verifier proven) on a tree contaminated by CKA-06's fixture and by the two proposals closure
  produces, `AC-013` (a real-runtime consumer round) as a test gap with no harness this role may
  build, and `AC-014` (the live operator sequence) as the operator's action after closure, since
  performed. Verdict `pass-with-reservations`, Validation Engine 31/31, three defects all low, no open
  critical or high defect. The run is itself the first live exercise of the mechanism: its own Fix
  Gate was rejected over attempt 1, rolled back under `RB-run-3e6f6a248b99-fix-gate-01`, re-entered
  as attempt 2 carrying the rejection as `prior_rejection`, and approved.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/state_engine.py` | `SR-1` | in-scope | The two authorised exits, the record requirement, `AUTHORISED_EXITS`, the restated terminality. A framework-surface file; this row records what the classifier returns for the citation form used throughout this proposal — see the note below the table |
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | `cmd_rollback`, `rollback_range` over `hard_descendants`, `rollback_preconditions`, attempt-scoped dispatch with `prior_rejection`, the scheduler correction, class-aware and live-derived clearing actions, the auto-approval holds, `next` and `recovery` surfacing, the CR-005 wording correction, and the `RUNTIME_VERSION` move. Framework surface; same citation-form reading |
| `.claude/runtime/recovery_policy.py` | `SR-1` | in-scope | The gate-rejection option list loses "approve an exception" and names the authorised rollback. Framework surface; same reading |
| `.claude/runtime/verify_recovery.py` | `SR-1` | in-scope | Run D, the admissibility table, `executable()`, checks D5a, D5b, D5c, D6a. Framework surface; same reading |
| `.claude/runtime/verify_multi_phase.py` | `SR-1` | in-scope | M4, M12 and M13 over the authorised exits and superseded completions. Framework surface; same reading |
| `.claude/runtime/README.md` | `SR-1` | in-scope | The `rollback` documentation and the cone rule. Framework surface; same reading |
| `.claude/config/execution-engine.md` | `SR-1` | in-scope | The Rollback After a Gate Rejection section and the recovery sequence text, including the CR-005 site at line 515. Framework surface; same reading |
| `.claude/config/runtime.md` | `SR-1` | in-scope | The rollback transition rule. Framework surface; same reading |
| `omn_agent/fix_comments.py` | none | out-of-scope | The consumer's reject-then-rollback sequence. Outside the framework surface: a consumer of the runtime, not part of it |
| `tests/test_gate_rollback.py` | none | out-of-scope | The added 34-test module. Outside the framework surface entirely, as every test module is |
| `docs/USER-GUIDE.md` | none | out-of-scope | The handbook's rework-loop description, with `docs/user-guide.html` regenerated from it. Outside the framework surface: published documentation |
| `omn_agent/_bundled_payload/**` | none | out-of-scope | The eight mirrored counterparts of the framework-surface edits above. The mirror duplicates the framework surface byte for byte, but its path matches no inclusion rule, the gap `FC-009` first recorded |
| `runs/run-3e6f6a248b99/**` | none | out-of-scope | Run evidence written by the runtime while it carried this change. Exempt in substance under the profile's run-evidence exclusion, which is the rule that decides it when the path is given with its directory prefix |
| `proposals/framework-change-proposal-FC-013.md` | none | out-of-scope | This proposal: the governance record of the routed change, not a second change. Exempt in substance under the profile's proposal exclusion, on the same reading |

Every row above was recomputed with the profile's own classifier at the authoring instant and
records exactly what it returned. The eight framework-surface files — the state engine, the runtime
gateway, the recovery policy, two verifiers, the runtime's own documentation and two configuration
contracts — are cited with their leading directory prefix, the form `SR-1`'s glob is keyed on, and
each returns in-scope under `SR-1`; the operator obtained the same answer at routing time for the
three runtime paths the defect report first named ("framework-internal change"). The artifact
validators' vendor scan removes that prefix before scanning (`artifact_contract.py`, check C3.2), so
citing it is permitted; an earlier convention of citing every path prefix-less, which made every row
read out-of-scope regardless of the file, is not a constraint of the framework and is not followed
here. **This change is framework-internal on its delivered surface, and it changes runtime behaviour,
which is why `RUNTIME_VERSION` moved.** The consumer, the test module and the handbook are outside
the surface; the two evidence rows are exempt under the profile's run-evidence and proposal
exclusions (`SR-3`, `SR-5`). Open item `O-022` is retained as the record of the citation-form
question and its resolution, not as an unresolved sensitivity.

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaved other than its contract declared. The
  recovery contract classifies a gate rejection as a `rollback` and every workflow specification
  promises the return to the implementing phase, yet no runtime path executed it and the envelope's
  prescribed clearing action failed when run. That is a declared behaviour not delivered, so
  `capability-addition` is not the class: the framework gains no capability it did not already
  declare, a declared behaviour is made real. `structure-preserving-change` is indefensible because
  observable runtime behaviour changes — two transitions that were refused are now admitted under
  authorisation, a command that did not exist now exists, and a run that could never complete after
  a rejection now can. `decision-support` does not apply: the current-state behaviour was fully
  known and reproduced on a live run before routing
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: triage-and-impact
- Required inputs supplied: `defect-report`
- Routing evidence: the profile's routing resolver, run at the authoring instant for the intent
  `defect-repair`, resolves to `/bugfix` over `fix-bug` v1.0.0 at `triage-and-impact` of 5 with the
  required input type `defect-report`. That is exactly what
  `runs/run-3e6f6a248b99/execution-request.json` records as `command_id`, `workflow_id`, the first
  enqueued phase and the single supplied input — `defect-report` at
  `runs/inputs/gate-rejection-rollback-dead-end-defect-report.md`, digest
  `sha256:58254996be15ab2df9c563c83ce7e148` — submitted 2026-09-06T09:49:30Z under runtime version
  0.5.0. The run's `intent` field reads `feature`, which is submission metadata carrying no routing
  consequence: the profile routes on the change class and the command, and both agree. Four further
  operator-supplied inputs reached the run after submission as architect consultations, because the
  `fix-bug` workflow has no design phase: `runs/inputs/gate-rollback-architect-decision-memo.md`
  (option (a) supersession, target rule, same-item re-arm, the `rollback` surface, no migration, the
  consumer contract), `runs/inputs/gate-rollback-architect-q006-q007-confirmation.md` (two values
  where one existed; the scheduler correction for both work types),
  `runs/inputs/gate-rollback-architect-f4-cr001-ruling.md` (range rule (b), the completed downstream
  cone; CR-001 refuse with no third transition; the stranded run's ordering constraint) and
  `runs/inputs/gate-rollback-architect-qa-open-questions-ruling.md` (Q-001 release, Q-002 M6, Q-005
  intended). None was a routing input and none is declared as one

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-3e6f6a248b99/execution-request.json` | resolved; `command_id` is `bugfix`, `workflow_id` is `fix-bug` v1.0.0, `runtime_version` 0.5.0, five phases enqueued, one input recorded with a digest — `defect-report` at `runs/inputs/gate-rejection-rollback-dead-end-defect-report.md`; submitted 2026-09-06T09:49:30Z |
| `E-2` | `runs/run-3e6f6a248b99/run-ledger.json` | resolved; `runtime_version` 0.6.0 (rewritten at the Closure Gate decision, 2026-09-07T14:20:22Z), run status `Completed`, five phases all `completed` with `fix-implementation` at attempt 2, attempts charged 2, attempts superseded 1; four gates all `approved` with owner role, deciding authority, rationale, evidence reference and decision timestamp recorded for each, and the Fix Gate carrying a `decision_history` of one entry — rejected 2026-09-06T13:12:16Z by omn-dev-2-reviewer, superseded by `RB-run-3e6f6a248b99-fix-gate-01`, re-armed 2026-09-06T13:12:17Z; the recovery block records 11 classifications, 11 resolved, 0 open, nine `gate-approval-required` and two `gate-rejection` |
| `E-3` | `runs/run-3e6f6a248b99/events.jsonl` | resolved; 69 canonical events, including `E-0034` (the Fix Gate rejection), `E-0036` (`rollback_scheduled`: attempt 1 of `fix-implementation` superseded under `RB-run-3e6f6a248b99-fix-gate-01`), `E-0037` (the Fix Gate re-armed), `E-0038` (the successor unblocked because its guards now wait), `E-0039` to `E-0043` (attempt 2 hydrated, leased, started, completed, validated 32/32), `E-0047` (the Fix Gate approved on attempt 2), `E-0057` (the Verification Gate approved), `E-0066` (`run_completed` at 14:16:34Z while the Closure Gate was undecided), `E-0067` (the Closure Gate approved at 14:20:22Z) and `E-0069` (a second `run_completed`) |
| `E-4` | `runs/run-3e6f6a248b99/state.json` | resolved; `runtime_version` 0.5.0 (stamped at planning), five state work items all `completed` and `Completed`, none blocked and none carrying a blocked reason, `fix-implementation` at attempt 2 with one `supersessions` entry (authorisation `RB-run-3e6f6a248b99-fix-gate-01`, gate Fix Gate, target `fix-implementation`, owner role omn-dev-2-reviewer, authorised 2026-09-06T13:12:17Z, attempt-1 digest `sha256:4b10ac71f54df2a92a55ab6007ea09a7`); four gate work items all `completed`; 38 recorded transitions, of which seq 16 to 18 are the rejection, the supersession and the re-arm |
| `E-5` | `runs/run-3e6f6a248b99/completion-package.md` | resolved; aggregates the five-phase ledger, the four gate decisions with their recorded authorities, a Superseded Attempts table carrying attempt 1 of `fix-implementation` at its immutable path and digest, the per-phase module provenance digests, all 38 transitions and the event stream through `E-0067`; its run summary reads runtime 0.5.0, the version the run was opened under |
| `E-6` | `runs/run-3e6f6a248b99/states/fix-implementation/artifacts/attempt-2/implementation-report.md` | resolved; the delivered change as attempt 2 (report IR-2026-0302), with 24 change-set entries, 13 test-evidence entries (12 passed, `T-010` failed on M6 alone), 6 recorded deviations, 6 residual risks and 4 open questions; the superseded attempt-1 report (IR-2026-0301) stands immutable at `runs/run-3e6f6a248b99/states/fix-implementation/artifacts/implementation-report.md`. Each of the five phases committed its contracted artifact — two `bug-analysis.md`, this report, `validation-report.md` and `orchestration-result.md` |
| `E-7` | `runs/run-3e6f6a248b99/states/fix-implementation/validation-report.json` | resolved; a validation report exists for each of the five executed phases and every one records `pass` — 30/30, 30/30, 32/32, 31/31 and 34/34, with zero blocking and zero correctable failures in each — and the superseded attempt's own report, snapshotted at `runs/run-3e6f6a248b99/states/fix-implementation/attempts/1/validation-report.json`, records 32/32 too: attempt 1 was rejected at a gate on substance, never by its validator |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed against the run in one attempt; 19 reproduction entries, 8 root-cause entries, 5 open questions, severity high and reproducibility deterministic on the analyst's own executions (a synthetic one-phase store and a scratch copy of the live stranded run with its digest unchanged); Validation Engine 30/30 | host-dispatched `omn-dev-1-bug-analyst` subagent v1.0.0 | `runs/run-3e6f6a248b99/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed against the run in one attempt; the analysis closes the causal chain at its ninth cause (no representation of the rollback in the state model, and no executor for the authorisation the envelope demanded), records the architect's decision memo as an operator-supplied input, states the ten fix-strategy conditions and the validation plan every later phase was measured against, and routes the run-status projection consequence as an open question; Validation Engine 30/30. The Phase Model declares no gate here, so none is recorded | host-dispatched `omn-dev-1-bug-analyst` subagent v1.0.0 | `runs/run-3e6f6a248b99/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed against the run over two attempts, both charged, 2 of 3. Attempt 1 (invocation `inv-3e6f6a248b99-03-001`, key `sha256:8cd40eecda922f0def52ca34352f76af`) completed 2026-09-06T12:57:15Z at 32/32 and was rejected at the Fix Gate at 13:12:16Z on one high blocking finding (`standing` excluded the closed phase, so an approved sibling gate could survive a rollback) plus two medium and two low; at 13:12:17Z the operator authorised rollback `RB-run-3e6f6a248b99-fix-gate-01` on that reviewer's assessment under owner role omn-dev-2-reviewer, target `fix-implementation`, and the runtime moved the phase `completed -> pending` under `superseded` (transition seq 17), the gate `failed -> pending` under `rollback_authorised` (seq 18) and the successor `blocked -> pending` (seq 19), leaving attempt 1's artifact byte-identical at its committed path and its per-attempt files under `attempts/1/`. Attempt 2 (invocation `inv-3e6f6a248b99-03-002`, key `sha256:250d4cde7ab596807e781cea94ed8c9b`) was dispatched at 13:12:57Z carrying the rejection as `prior_rejection`, wrote to the attempt-scoped path, completed 2026-09-07T11:46:12Z at 32/32, and closed CR-001 to CR-004 and F4 by execution; 24 change-set entries. The key moved at re-dispatch, not at rollback, because one member of the frozen context slice (`runtime/README.md`) had changed between the two freezes — the fix's own attempt-1 edit; see `O-015` | host-dispatched `omn-dev-1-implement` subagent v1.1.0 on both attempts; the rollback authorisation recorded by the session operator on the Fix Gate assessment of the omn-dev-2-reviewer subagent | `runs/run-3e6f6a248b99/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed against the run in one attempt; 17 acceptance criteria at 14 met, 0 not met and 3 blocked, 3 defects all low, 5 open questions, verdict `pass-with-reservations`; Validation Engine 31/31. The full 473-test suite in its CI form, seven verifiers, the runtime's own subcommands driven against three byte-identical copies of `run-4c51600606df` with the runs directory redirected outside the repository, and a synthetic-store probe of every bare exit from `completed` and `failed`; the live stranded run untouched, its digest and modification time unchanged before and after | host-dispatched `omn-qa` subagent v1.0.0 | `runs/run-3e6f6a248b99/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed against the run in one attempt; 5 phase-progression rows, 4 handoffs all accepted, 8 escalations at one high (resolved by the run's own rollback and re-decision), two medium and five low with none critical or high open, 11 follow-up actions each owned, no open questions, disposition `closed-with-followups`; Validation Engine 34/34. The record held its own row at `blocked` because its Closure Gate was undecided when it was written; that gate was decided 3m 49s after the artifact was accepted, which is why this proposal reports the phase `completed` and the closure record reports it `blocked`. Both are accurate at their own instant. The record also confirmed CR-005 CLOSED on read-only inspection of the operator's correction pass | host-dispatched `omn-orchestrator` subagent v1.0.0 | `runs/run-3e6f6a248b99/states/closure-and-communication/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact and none blocked, so the
Completion Rule's `C-3` is satisfied on its executed limb throughout and its operator-performed limb
is never reached. All five were performed by host-dispatched subagents under their contracted
validators. Four operator actions are recorded above and below rather than absorbed, each assessed
afterwards by an owner who produced neither the evidence nor the action: the recording of each gate
decision on behalf of the deciding subagent; the rollback authorisation of 2026-09-06T13:12:17Z,
which is the intended human step the mechanism requires and the first live use of it; the CR-005
wording correction of 2026-09-07 at `runtime/framework_runtime.py:59` and `:4968-4969` and
`config/execution-engine.md:515` plus both bundled mirrors, re-validated by `test_bundled_payload`
(11 OK) and `test_gate_rollback` (34 OK), which the closure record confirmed and the Closure Gate
re-read; and the `RUNTIME_VERSION` move from 0.5.0 to 0.6.0 at `runtime/framework_runtime.py:123`
and its mirror (both files modified 2026-09-07T14:03Z), re-validated by `test_bundled_payload` (11),
`test_framework_runtime_render` (21) and `test_gate_rollback` (34), all OK, which the Closure Gate
recorded as "the operator's FR-07 pass". Neither correction pass left a run event of its own, which
is why both are named here.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | omn-tech-lead subagent, recorded by session operator, 2026-09-06T10:10:55Z | Severity high and reproducibility deterministic rest on the analyst's own executions, not on the report's framing; every cited code path re-read and confirmed — no exit from `completed` or `failed` in the transition tables, `record_gate_decision` moving the gate to `failed` without touching the producing phase, `G4-GATE` blocking on `rejected`, `refresh` never clearing a guard block while the guard fails, and a clearing action prescribing `release` on an item it cannot act on. High is the right severity because the designed correction loop of every workflow is materially degraded but delivery is not stopped. Two report claims refuted rather than echoed (the `release` call raises a transition error rather than printing nothing; `next` first offers the sibling gate). Conditions carried into root-cause analysis: route the representation question to the architect and record the answer as input; treat terminality and M12 as invariants the fix must satisfy; state the run-status projection consequence. Conditions carried into fix-implementation: a rollback triggered only by a recorded decision from a listed non-producing owner; the rejection immutable; decision values and producer exclusion unchanged; the re-decision human, never auto-approved on cross-run precedent; every envelope's clearing action executable for its item type and status; full tests and every verifier proven; the disposition of `run-4c51600606df` stated. `omn-dev-1-bug-analyst` produced the evidence and is excluded from deciding |
| Fix Gate | reject (attempt 1) | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-06T13:12:16Z | One high finding blocks: `standing` excluded the closed phase, so an approved sibling gate closing the closed phase survived the rollback — demonstrated by approving the stranded run's Verification Gate on a copy, rolling back, and watching the approval stand over superseded evidence and pass the successor once the Review Gate was re-approved, violating the memo's human-block invariant. Also F2 medium (the clearing action pre-filled the authoriser from the rejection), F3 low (M6 attribution incomplete), F4 low (a completed dependent off the closed phase's ancestor chain not superseded; routed to the architect) and F5 medium (no operator surface named the rollback on the stranded store). Every re-executed claim held: verify_recovery 70/70 with Run D, five test modules OK, bundled parity 11 OK. Correction requests CR-001 to CR-004 issued, owner omn-dev-1-implement. The decision records itself as the first live exercise of the mechanism under test. Recorded in the gate's `decision_history` with its rationale, author and timestamp; transition seq 16, event `E-0034` |
| Fix Gate | approve (attempt 2) | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-07T11:59:18Z | Every correction request closed by execution: CR-001 — `rollback_preconditions` iterates `standing` over every phase in range with no closed-phase exclusion, the approved-sibling refusal reproduced on a scratch copy for both targets with the store byte-equal, pinned with store equality and by Run D6a; F4 — `rollback_range` is the target plus its completed hard descendants in descending order, the fix-bug-shaped test proving target `triage-and-impact` supersedes `root-cause-analysis` and `fix-implementation`, four contract passages stating the cone; CR-002 — `--decided-by <who>` the only placeholder, exempted by the admissibility table; CR-003 — T-010 attributes M6 to the carried-at status reconstruction; CR-004 — on the live stranded run `next` exits 3 naming the rollback first and withholding the Verification Gate, `recovery --open-only` derives the rollback while the persisted files still read `release`, ledger and envelopes untouched. Re-executed: verify_recovery 74/74 with D5a/D5b/D5c/D6a; test_gate_rollback 34, test_gate_policy 30, test_fix_comments 16, test_update 14, test_framework_runtime_render 21 all OK; bundled parity 11 OK; render check exit 0. Invariants confirmed: exactly the two added transitions, M12 over supersessions, attempt-1 digest unchanged, decision values unchanged, `cmd_release` and the runner untouched. One low non-blocking finding F-001 became CR-005 (three sites still stating the path rule). Operator sequence for the stranded run verified on a fresh copy; QA instructed not to execute it. `omn-dev-1-implement` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-07T13:57:36Z | Every behavioural criterion of the fix strategy and the architect's rulings is met on executed evidence; the reviewer re-executed test_gate_rollback 34 OK, the five touched test modules 115 OK, verify_self_hosting 7/8 with S8 alone failing on exactly the two unaccounted runs, confirmed the runner byte-identical to HEAD and the state engine adding exactly the two pairs, and reconciled the full-suite count exactly: 404 baseline plus 44 from this change plus 25 from CKA-06's renderer suite equals 473, with the only two failures the CKA-06 `PreChangeEquivalence` tests in an untracked module and fixture. Reservations on the three blocked criteria each placed: `AC-012` on two external limits and one verifier-contract gap this change exposed (M6, since ruled); `AC-013` a test gap honestly labelled; `AC-014` the operator's action, which this approval authorises. Findings all low, none blocking: CR-005 confirmed open at that time; M6 semantics; the real-runtime consumer round unproven. Disposition of CR-005: the change proposal must record it CLOSED with the edit confined to the three sites and mirrors and the re-runs named, or OPEN with omn-tech-lead's acceptance — never closed silently. Four conditions on closure, each discharged by the closure record and carried here. `omn-qa` produced the evidence and is excluded from deciding; the co-owner decided |
| Closure Gate | approve | omn-documentation | omn-documentation subagent, recorded by session operator, 2026-09-07T14:20:22Z | Every statement in the closure record testable against the ledgers is grounded: five phases; the Triage approval; the Fix Gate rejection, rollback and re-approval at their recorded events; the Verification approval; the two idempotency keys with equal input digest and differing context digests. The CR-005 sites now read the cone and the record correctly attributes the re-runs to the operator pass. The four delivered documents state both operator-facing facts — an approved sibling gate makes the rollback refuse; authorisation is a second human decision by a listed non-producing owner — where a reader finds them. Post-record drift recorded as drift, not error: 37 transitions, 67 events, `runtime_version` 0.6.0 after the operator's FR-07 pass, and `run_completed` fired with the Closure Gate undecided (`FU-002` exercised live). Documentation findings, all low or advisory, none blocking, became `FU-012` (`docs/USER-GUIDE.md:752-753` still states the path rule; re-render; sequence with CKA-06's fixture), `FU-013` (the README's idempotency section never says a moved context slice yields a new key at re-dispatch) and `FU-014` (the `rollback` help text omits the approved-sibling refusal); `FU-001` extended to require this proposal to name CR-005 CLOSED with its re-runs, declare baseline 0.6.0 with its re-validation, and record the idempotency rule as two instances. No command executed by the gate owner; counts quoted from the Fix Gate rationale. `omn-orchestrator` produced the evidence and is excluded from deciding |

Every gate the `fix-bug` Phase Model declares was decided, each by an owner the gate matrix assigns
and none by the role that produced the evidence assessed. None was waived and none was
auto-approved: all five decisions are recorded as human decisions, and the one rejection was
followed not by a bypass but by a recorded rollback authorisation from a listed non-producing owner
and a fresh human decision over the rebuilt evidence. The authorisation itself is not a gate
decision and is not tabled as one: it is recorded in the run ledger's `decision_history`, in the
`supersessions` entry of `E-4`, at transitions seq 17 and 18, and at events `E-0036` and `E-0037`.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | inspection | pass; 6/6 checks, 37 of 37 phases resolving the full capability and context chain, 0 blocked, 29 of 29 gate references decidable under the Producer Exclusion Rule. Executed from the repository root at the authoring instant, not merely inspected — the note below the table gives the reason the Command column reads this way |
| Manifest conformance | inspection | pass; 2/2, 3 manifests checked, 0 bad. Executed at the authoring instant |
| Validator coverage and decisiveness | inspection | pass; 6/6. Executed at the authoring instant |
| Committed evidence still verifies | inspection | pass; 10/10 PROVEN on `run-c5a8d50d3238`, the run the checklist item names, and 10/10 PROVEN on `run-919c5d5cf156`, the run the validation report used. Both executed at the authoring instant |
| Self-hosting governance | inspection | 7/8 at the authoring instant. `S1` to `S7` pass: the profile parses, all seven routing rows resolve, the change-proposal contract is registered, all twelve recorded proposals `FC-001` to `FC-012` re-validate at 38/38 each under `S6`, and `S7` confirms the Completion Rule for each of their runs. `S8` fails naming exactly two unaccounted runs — this run and `run-4c51600606df` — of which this proposal removes the first on the next execution. The second is `O-005` |
| Recovery behaviour | inspection | not re-executed at authoring, deliberately: the proof plans and removes probe runs under the runs directory, a repository write outside this authoring session's single permitted write. Measured at 74/74 RECOVERY PROVEN by the validation phase, re-executed at 74/74 by the Fix Gate reviewer, and at 70/70 with Run D by the attempt-1 assessment; Run D checks D0 to D27 including D5a, D5b, D5c, D6a, D7, D22, D25 and D26 all pass, with the runs directory at the same entry count before and after every execution |
| Multi-phase state machine | inspection | not re-executed at authoring: the probe replays commands into a run's committed store, and modifying committed run evidence is prohibited to this role. Measured by the validation phase at 14 of 15 on the harness rollback run `run-3655babc5772` (created with `--keep` and removed through the harness's own reset), M6 alone failing and M14 passing; 13 of 15 in-process on a copy of the stranded run after its rollback and 14 of 15 before it. M6 fails by construction on any run mid-rollback because it reads a superseded delivery phase as `pending` — the architect ruled the extension (`O-003`) |
| Whole discovered unit suite | inspection | not re-executed at authoring, deliberately: the suite runs 906 s and, per the Review Gate rationale on `run-4c51600606df`, its handbook equivalence tests rewrite tracked documentation files in place. Measured by the validation phase in the CI form at 473 tests with exactly 2 failures, both `PreChangeEquivalence` tests of `tests/test_render_user_guide.py`, an untracked module and fixture of the in-flight CKA-06 change; the Verification Gate reconciled the count (404 baseline + 44 from this change + 25 from CKA-06's suite) and attributed both failures to that fixture (`O-013`) |
| The cited modules still pass on this tree | `python -m unittest tests.test_gate_rollback tests.test_bundled_payload tests.test_framework_runtime_render` | pass; 66 tests run, 66 passed, at the authoring instant — 34, 11 and 21 respectively, the same figures the Fix Gate, the CR-005 correction pass and the FR-07 pass recorded. The three modules build their stores under the system temporary directory and write nothing into the repository |
| Scope classification recomputes | inspection | pass; the profile's classifier was run at the authoring instant on each of the fourteen paths in the Scope Classification table and every row records exactly what it returned. The eight framework-surface paths were additionally classified with their directory prefix, where the classifier returns in-scope under `SR-1`, which is the substantive reading recorded under that table |
| Routing resolves | inspection | pass; the profile's routing resolver for the intent `defect-repair` resolves to `/bugfix` over `fix-bug` v1.0.0 at `triage-and-impact` of 5 with required input `defect-report`, agreeing with `E-1` on all four |
| CR-005 closed on the tree | inspection | pass; read-only at the authoring instant: `runtime/framework_runtime.py:57-65` (module docstring) and `:4966-4970` (`rollback --target` help) and `config/execution-engine.md:515` each state the completed downstream cone; a case-insensitive search for the superseded path-rule wording across `runtime/framework_runtime.py`, `config/execution-engine.md`, `config/runtime.md` and `runtime/README.md` returns nothing; all eight edited framework files compare byte-identical to their `omn_agent/_bundled_payload/` mirrors. The same search over `docs/USER-GUIDE.md` finds line 753 still reading "every completed phase up to the gated one" — the Closure Gate's `FU-012`, carried as `O-010` |
| `RUNTIME_VERSION` reads 0.6.0 | inspection | pass; `runtime/framework_runtime.py:123` and its bundled mirror both read `0.6.0`, both modified 2026-09-07T14:03Z, before the closure artifact was accepted; `E-2` records the run's ledger under 0.6.0 and `E-1`, `E-4` and `E-5` record the run opened under 0.5.0 |
| The repair holds in the live record | inspection | pass, and the fix's live purpose has since been carried out by an actor outside this proposal. Read-only inspection of `runs/run-4c51600606df/state.json` at the authoring instant (last written 2026-09-07T14:21:31Z, after the Closure Gate decision and before this record) shows the operator's rollback `RB-run-4c51600606df-review-gate-01` recorded at 14:21:28Z with owner role omn-qa, target `implementation`, issued while the Verification Gate carried no decision as the ruling required: `quality-review` and `implementation` superseded (seq 34, 35), the Review Gate re-armed with the rejection in its `decision_history` (seq 36), the Verification Gate and the successor returned to `pending` (seq 37, 38), zero of eleven recovery entries open, and `implementation` dispatched as attempt 2 (`inv-4c51600606df-04-002`) at 14:21:31Z carrying a new idempotency key `sha256:4253e368330e942c84ac0f4dc165cefd` against attempt 1's `sha256:2862f1c31a6a2a1df4588f1332bf72ea`, exactly as the architect's Q-005 ruling said it would. That run's own ledger now reads `runtime_version` 0.6.0. Nothing here reports on what that attempt produces |
| This proposal against its registered validator | inspection | pass; 38 checks run, 38 passed, 0 blocking and 0 correctable failures, with the two not-machine-checkable obligations recorded. Re-run by `S6` of the self-hosting verifier on every later execution |

One note on the Command column, because it reads oddly and the cause is not a weakness in the
checks. This proposal cites every repository path without its leading directory prefix, so a command
naming a framework script cannot be written here in a form that resolves from the repository root,
which is what check `F10` requires of any command cell that is not `inspection`. Every row marked
`inspection` that says it was executed was executed, from the repository root, at the authoring
instant; the word records a citation constraint, not a weaker class of evidence. The three rows that
genuinely were not re-executed say so in their own words and give the reason, and each carries the
figure a named phase or gate measured. The directory sensitivity that forces this is carried as
open item `O-022`.

## Risk and Rollback

- Blast radius: twenty-four change-set paths, of which eight are framework surfaces — the state
  engine, the runtime gateway, the recovery policy, two verifiers, the runtime's README and two
  configuration contracts — plus their eight bundled mirrors, one consumer module, one added and four
  extended test modules, and the handbook source with its regenerated page. The state engine's
  change is the smallest and the most consequential: two table entries and one record requirement,
  admitting for the first time an exit from a status every reader of the store treated as terminal.
  Every status change remains a logged transition through the engine; `record_gate_decision`'s
  decision values, `cmd_release`, `producer_aliases` and the runner's approval requirement are
  byte-identical to their pre-change form. No workflow specification, command, gate matrix row or
  registry record changed. Two persisted run records changed as a direct and intended consequence:
  this run's own `fix-implementation` item, superseded and rebuilt, and — after the Closure Gate, by
  the operator — `run-4c51600606df`, un-stranded through the runtime's own `rollback` command with
  all its committed artifacts left byte-identical.
- Risk assessment: six residual risks were recorded by the implementation and each was assessed at
  a gate by a non-producing owner. The load-bearing one is `R-001`, carried as `FU-002` and recorded
  here as `O-001`: with every phase completed and a final gate undecided or rejected the run projects
  `Completed` and `run_completed` fires, and after this change a supersession after `run_completed`
  is possible, so a run may carry `run_completed` and a later re-entry. It materialised on this very
  run — `E-0066` fired at 14:16:34Z with the Closure Gate undecided until 14:20:22Z, then `E-0069`
  fired again — so it is a certainty on every gated terminal phase rather than a probability, placed
  out of scope by the architect's memo and owned by `omn-orchestrator` as a separate defect. `R-005`,
  accepted by the architect as the correct cost of the human-block invariant: a rollback whose range
  holds an approved gate is refused, so a rework that must return past an approved gate needs a
  shallower target or a new run; `next` withholds the sibling decision and the auto-approval policy
  holds it, but the `gate` command itself does not refuse such an approval (`O-009`). `R-006`, ruled
  after validation: an active descendant in the cone is neither superseded nor refused today, no
  workflow produces the shape, and the ruling's remedy is `O-002`. The M6 verifier gap (`O-003`) is
  exposed rather than introduced: any run mid-rollback fails M6 until the extension lands, so CI's
  bare form would fail if the most recently modified run were mid-rollback, and the un-stranded run
  is in exactly that state now. The bare engine-level pair `failed -> pending` is legal without a
  record; its human authorisation is enforced by `cmd_rollback` alone, as the memo designed. The
  idempotency-key behaviour (`O-015`) is intended and now written down, but an operator who expects
  replay suppression to tie a rolled-back phase's attempts together after the tree moved will be
  surprised until `FU-013` lands. The one documentation defect the change left standing is
  `docs/USER-GUIDE.md:752-753` (`O-010`), low, still stating the path rule.
- Rollback procedure: revert the twenty-four paths and re-sync the bundle. That restores the two
  terminal tables, removes the `rollback` command, and reinstates the dead end: every gate rejection
  strands its run and the envelope again prescribes a command that fails. The condition that would
  justify it is an authorised rollback leaving something standing over superseded evidence, and the
  correct response to that is the active-descendant correction routed as `O-002`, not this revert,
  which would trade one defect for the one it repaired. Reverting invalidates no committed run
  evidence: this run's record remains a valid account of a delivered-then-reverted change and this
  proposal remains its governance record. It would, however, strand two runs by construction: this
  one carries a `supersessions` entry and a `decision_history` that a reverted engine cannot read as
  legal history, and `run-4c51600606df` is executing `implementation` attempt 2 under an
  authorisation the reverted runtime has no representation for. A revert taken after 14:21:28Z is
  therefore a decision for those runs' operator and for `omn-tech-lead`, not a mechanical undo, and
  `RUNTIME_VERSION` would have to move again to mark it.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6; 37 of 37 phases dispatchable, 0 blocked, every phase owner host-invocable, 29 of 29 gate references decidable; executed at the authoring instant |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 at the authoring instant; also 6/6 at the validation phase |
| `FR-03` | Recovery behaviour | pass | 74/74 RECOVERY PROVEN at the validation phase and again by the Fix Gate reviewer, with Run D — the gate-rejection scenario this change adds — and the clearing-action admissibility table executing Run D's action verbatim. Not re-executed at authoring for the reason given under Verification; the figure is two independent parties' |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` at 10/10 PROVEN and `run-919c5d5cf156` at 10/10 PROVEN at the authoring instant; no committed proof was invalidated |
| `FR-05` | Self-hosting governance resolves | pass | The profile parses, all seven routing rows resolve, the change-proposal contract is registered, all twelve recorded proposals re-validate at 38/38, and every one of their runs satisfies the Completion Rule — `S1` to `S7`. The remaining `S8` row after this proposal lands is a residual this change did not cause, carried as `O-005` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-3e6f6a248b99` is a `/bugfix` run over `fix-bug` v1.0.0, submitted with the input type the profile's routing row requires; this proposal links its artifacts as `E-1` to `E-7` |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Moved 0.5.0 to 0.6.0 at `runtime/framework_runtime.py:123` and its bundled mirror, because runtime behaviour changed: two transitions the engine refused are admitted under authorisation, a subcommand that did not exist exists, the scheduler clears guard-raised blocks it previously left standing, and clearing actions and `next` derive differently. Applied by the operator before the Closure Gate, verbatim from the architect's ruling as the operator relayed it, and re-validated by `test_bundled_payload` (11), `test_framework_runtime_render` (21) and `test_gate_rollback` (34), all OK, and again at the authoring instant (66 of 66). Consequence, recorded in the ruling's words: runs recorded under runtime_version 0.5.0, including run-4c51600606df, remain valid under that version; run-4c51600606df's attempt 2 dispatches under 0.6.0, and its closure record must state it was opened at 0.5.0 and closed under 0.6.0. The same is true of this run, and this record states it: opened at 0.5.0 (`E-1`, `E-4`, `E-5`), closed under 0.6.0 (`E-2`). The ruling's text is carried in no file under `runs/inputs/`, which is `O-017` |
| `FR-08` | Documentation matches delivered behaviour | accepted | `runtime/README.md`, `config/execution-engine.md`, `config/runtime.md` and `docs/USER-GUIDE.md` state the cone range, the approved-gate refusal, the placeholder authoriser and the `next`/`recovery` behaviour while a rejection stands, confirmed by direct read at validation and closure and by the Closure Gate at the lines a reader finds them; the CR-005 sites read the cone; every mirror is byte-identical. Recorded `accepted` rather than `pass` because two low documentation follow-ups the Closure Gate raised still stand: `docs/USER-GUIDE.md:752-753` states the superseded path rule (`O-010`), and the README's idempotency section does not say that a re-dispatch after a rollback binds a new key whenever any payload component moved (`O-011`). Neither misstates a safety property; both must not read clean while they exist |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim was executed or directly read: the two exits and every refusal on synthetic stores and on byte-identical copies of the stranded run with store equality, Run D on the real runtime, 164 targeted tests across eight modules, four contract passages read directly, the live stranded run's digest confirmed unchanged through validation, and the fix's own mechanism exercised on this run's Fix Gate and recorded at transitions 16 to 19. The gaps are recorded rather than omitted — the three blocked criteria, the M6 verifier gap, the active-descendant case, the real-runtime consumer round, and the contaminated whole-suite figure — and the one live claim this proposal adds, the un-stranding of `run-4c51600606df`, is read from that run's store with its evidence quoted |
| `FR-10` | Rollback stated | pass | Risk and Rollback above: a twenty-four-path revert with bundle re-sync, the condition that would justify it, the better answer to that condition, the two runs a late revert would strand and why, and the version consequence |
| `FR-11` | Multi-phase state machine still proves out | accepted | 14 of 15 at the validation phase on the harness rollback run, failing only `M6`, which reads a superseded delivery phase as `pending` on any run mid-rollback; every other check passes including M4 over the authorised re-entries, M12 over every superseded completion, M13 refusing every other exit, and M14. The architect ruled the extension and a Run E (`O-003`). Not re-executed at authoring because the probe replays into a committed run's tracked store, which this role may not modify; CI does not invoke this verifier |
| `FR-12` | Release note where consumer-visible behaviour changed | accepted | Behaviour a framework consumer depends on did change — a gate rejection is recoverable inside the run, the consumers issue `reject` then `rollback`, `next` exits 3 while a rejection stands, and a re-dispatch after a rollback may bind a new key — and no release note exists yet. The `fix-bug` closure phase produces the coordination record a note is written from, not the note itself; the Closure Gate approved that record and confirmed the note must carry the idempotency statement in general form; publication is carried as `O-006`, owned by `omn-documentation` |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The run-status projection and aggregator read state items only, so `run_completed` fires while a final gate is undecided or rejected, and after this change a supersession after `run_completed` is possible. Exercised live on this run: `E-0066` fired at 2026-09-07T14:16:34Z reading "every workflow phase completed and every gate was decided" while the Closure Gate carried no decision until 14:20:22Z, and `E-0069` fired a second time when it did. Placed out of scope by the architect's decision memo, carried as residual risk `R-001` by the implementation, as accepted risk by the validation, and as `FU-002` by the closure record; the same class of failure `FC-012` recorded as its first open item on the refactor workflow | `omn-orchestrator` | Open, medium, and rated the most consequential item in this table because it degrades the evidence every later gate reads. Route as its own defect through `/bugfix`; this record is its second live witness |
| `O-002` | A phase in the target's downstream cone that is leased or running at the moment of authorisation is neither superseded nor refused, so a consumer of superseded evidence could complete on stale input; no workflow produces the shape today because successors of the closed phase are guard-blocked. Architect ruling of 2026-09-07: release it through the worker-loss path `cmd_release` already uses — uncharged, retryable, no new transition — with a late report refused as a stale completion and `next` not offering its `complete`. Carried from the closure record as `ES-004` and `FU-004`, with `runs/inputs/gate-rollback-architect-qa-open-questions-ruling.md` as its specification | `omn-dev-1-implement` | Open, low. A behaviour change beyond this fix's accepted scope, needing a routed run of its own; it does not block closure and did not |
| `O-003` | `verify_multi_phase` check M6 reads a superseded delivery phase as `pending` and so fails on every run mid-rollback while every other check passes. Architect ruling: M6 accepts a delivery phase as traversed when its baseline status is completed, blocked, or its work item carries a non-empty `supersessions` list, and a rollback-carrying multi-phase Run E is added to the proof surface of `verify_multi_phase` and `verify_recovery`. Carried as `DF-002`, `ES-005` and `FU-005` | `omn-dev-1-implement` | Open, low. It is the reason `FR-11` above reads `accepted`, and until it lands the verifier cannot prove `run-4c51600606df` from its un-stranding until its `implementation` attempt 2 completes |
| `O-004` | No harness drives `omn-agent pr fix-comments` against the real runtime; the consumer tests replace the runtime with a stateful stub and the real command needs a ticket-provider transport. The reject-then-rollback sequence is proven against the stub and against the real runtime's status shape on a copy, and the first live round is the real proof. Carried as `AC-013`, Verification Gate finding F-003 and `FU-006` | `omn-dev-1-implement` | Open, low, a test gap rather than an unmet criterion of this fix |
| `O-005` | One framework run remains unaccounted by any change proposal and will keep `S8` of the self-hosting verifier failing after this proposal lands: `run-4c51600606df`, submitted 2026-09-05T04:23:54Z, carrying CKA-06 and not this fix. Its disposition, as the Verification Gate directed this proposal to state: un-stranded by the operator after this run's Closure Gate, at 2026-09-07T14:21:28Z, via `rollback --gate "Review Gate" --target implementation --owner-role omn-qa`, issued before any decision was recorded on its Verification Gate as the architect's ruling required, superseding `quality-review` and `implementation` and leaving every committed artifact byte-identical; its `implementation` attempt 2 was dispatched at 14:21:31Z and is running at the authoring instant. It is accounted for under `S8` by its own change proposal — CKA-06's — produced at its own closure after its rework completes, not by this one; fabricating a proposal for a run this change did not carry would falsify the record, and a run mid-workflow cannot satisfy the Completion Rule in any case. Carried from the closure record as `ES-002`, `ES-008` and `FU-007`, and descended through `FC-011`'s and `FC-012`'s residual rows | `omn-orchestrator` | Open, pre-existing and shrinking: two runs before this proposal, one after it. `S8` is expected to name exactly that run on its next execution |
| `O-006` | The release note for this fix has not been written. It is written from the closure record, which the Closure Gate approved, and must carry: the two authorised terminal exits, the `rollback` command and its refusals, the cone range, the same-item re-arm with `decision_history`, the `next` and `recovery` behaviour while a rejection stands, the consumer sequence change, and the idempotency statement in its general form — a re-dispatch after a rollback binds a new key whenever any payload component moved, not the agent version alone. Carried as `FU-008` | `omn-documentation` | Open, low. It is why `FR-12` above reads `accepted` |
| `O-007` | Seven signals the validation named are unmonitored: a recovery ledger holding an open `gate-rejection` entry while no state item is pending and eligible and no gate awaits a decision (should be zero); `next` exiting 3 with `awaiting_recovery_task` on any run; a gate decision recorded by the policy decider on a gate with a non-empty `decision_history` (should never occur); `run_completed` on a run whose gates include a rejected or undecided decision (`O-001`); a `complete` accepted on a phase whose hard predecessor is pending after a supersession; M6 failures on runs carrying a rollback in CI (`O-003`); and the idempotency key of the un-stranded run's `implementation` item, now observed as `O-005` records. Carried as `FU-009` | `omn-qa` | Open, low |
| `O-008` | The retry-class clearing action's optional suffix "to reclaim it sooner" names `release`, which on a retrying item reports already retrying and reclaims nothing. Pre-existing, outside the gate-rejection scope, judged only by prescription in the admissibility check. Carried as `R-003` and `FU-010` | `omn-dev-1-implement` | Open, low |
| `O-009` | The `gate` command itself does not refuse an approval on a gate whose sibling on the same phase stands rejected; the fix relies on `next` withholding the offer, the auto-approval hold, the refusal on rollback, and the ruling's ordering instruction. The architect accepted the refusal of a rollback whose range holds an approved gate as the correct cost of the human-block invariant (`R-005`), so a rework that must return past an approved gate needs a shallower target or a new run. Whether `gate` should refuse such an approval directly is undecided. Carried as `FU-011` | `architect` | Open, low, with `R-005` recorded as accepted risk at three gates by non-producing owners |
| `O-010` | `docs/USER-GUIDE.md:752-753` still describes the supersession range by the retired path rule ("that phase and every completed phase up to the gated one"), and its render `docs/user-guide.html` carries the same text; CR-005's search terms did not cover this phrasing, while the handbook's rework-loop paragraph states the cone correctly. Confirmed by this author's read-only search at the authoring instant: line 753 still reads so. Correction requires re-rendering and adds hunks to CKA-06's frozen fixture, so it must be sequenced with `O-013`. Raised by the Closure Gate as `FU-012` | `omn-dev-1-implement` | Open, low. It is one of the two reasons `FR-08` above reads `accepted` |
| `O-011` | `runtime/README.md`'s idempotency-and-replay section never says that a re-dispatch after a rollback binds a new key whenever any payload component moved — the context slice, the input digest, the agent version or the canonical path — and that replay suppression then does not tie the attempts together; the memo's key-preservation statement is true of the rollback transition only. This run is an instance (`O-015`). Raised by the Closure Gate as `FU-013`, to be mirrored to the bundle | `omn-dev-1-implement` | Open, low. The second reason `FR-08` above reads `accepted` |
| `O-012` | The `rollback` parser help names the cone and the owner checks but not the approved-sibling refusal, so an operator reading `--help` alone does not learn that approving a sibling gate first makes the rollback refuse. Raised by the Closure Gate as `FU-014`, advisory | `omn-dev-1-implement` | Open, advisory |
| `O-013` | The two `PreChangeEquivalence` tests of `tests/test_render_user_guide.py` fail in the full suite and alone (66 recorded against 71 computed element hunks, 51 against 53 text hunks) because CKA-06's equivalence check freezes the handbook to a pre-change page and this fix's legitimate `docs/USER-GUIDE.md` edits add hunks CKA-06's reconciliation record does not list. Attributed by the Fix Gate to that fixture, approved with by the Verification Gate as one of two external limits behind `AC-012`, routed by the closure record as `ES-007` and `DF-003`. Either the hunks are recorded in CKA-06's reconciliation record or the fixture is retired when CKA-06 lands; `O-010` will add hunks of its own | `omn-dev-2-reviewer` | Open, low, routed to the review of `run-4c51600606df` attempt 2, which is now in progress |
| `O-014` | The go the closure record carries covers the fix on this tree and nothing wider. The shared working tree is not quiescent: it carries, uncommitted, this fix's change set, the in-flight CKA-06 change with its untracked test module and fixture, the completed change of `run-79630cb5274d`, and — since 14:21:31Z — the running attempt 2 of `run-4c51600606df`. Whether that tree is releasable, and in what order the changes are committed, is a delivery judgement. Carried as `ES-003` | `omn-tech-lead` | Open, medium, routed rather than answered; every whole-repository figure in this proposal must be read with this qualification |
| `O-015` | A re-dispatch after a rollback binds a new idempotency key whenever any payload component moved. Two instances are recorded, as the Closure Gate required. On `run-4c51600606df`, in the architect's words carried verbatim in substance: attempt 2's dispatch of implementation binds a new idempotency key because the implementer agent resolves at 1.1.0 against 1.0.0 at attempt 1; this is expected `bind_payload` behaviour keyed on agent version, not a rollback defect, and does not indicate lost work or a replay-suppression failure — the item was pending, not terminal, at bind time; now observed (`sha256:2862f1c3...` to `sha256:4253e368...`). On this run, `fix-implementation` attempt 2 bound `sha256:250d4cde...` against attempt 1's `sha256:8cd40eec...` with the implementer version unchanged at 1.1.0 and the input digest equal, because the frozen context slice moved when `runtime/README.md` changed between the two freezes. Carried as validation `Q-005`, closure `ES-006` | `architect` | Resolved by ruling, recorded rather than repaired; the documentation consequence is `O-011` and the release-note consequence is `O-006` |
| `O-016` | Correction request CR-005 (Fix Gate finding F-001, validation defect `DF-001`, low): the module docstring at `runtime/framework_runtime.py:59`, the `rollback --target` help at `:4968-4969` and the recovery sequence text at `config/execution-engine.md:515` stated the superseded path rule where the executed range is the cone. CLOSED, not carried: an operator-dispatched correction pass on 2026-09-07 edited wording only at exactly those sites and copied both files to their `omn_agent/_bundled_payload/` mirrors, then re-validated with `test_bundled_payload` (11 OK) and `test_gate_rollback` (34 OK); confirmed by the closure record's read-only inspection, re-read by the Closure Gate, and re-confirmed by this author's search and byte comparison at the authoring instant. It was never closed silently, which is what the Verification Gate forbade. Consequence stated so no reader is misled: the committed attempt-2 report's `C-003` and `C-007` rows and the validation report's `DF-001` row describe the pre-correction text; both artifacts are immutable and were not edited | `omn-dev-1-implement` | Resolved, with the re-runs named as the Verification Gate required |
| `O-017` | The `RUNTIME_VERSION` move from 0.5.0 to 0.6.0 is evidenced in source, in its mirror, in this run's ledger, in the un-stranded run's ledger and in the Closure Gate's rationale, and the ruling that mandated it and its consequence for runs opened under 0.5.0 are recorded under `FR-07` in the words the operator relayed. But no file under `runs/inputs/` carries that ruling: the four architect inputs on the run predate it and none mentions a version, so the ruling reaches this record only through the operator's dispatch instruction. Every other architect position this run relied on is filed as an operator-supplied input the run's artifacts cite by path | `architect` | Open, low. File the ruling under `runs/inputs/` alongside the four existing architect inputs so that the version move has the same evidentiary standing as the design it versions; this record does not cite a path that does not exist |
| `O-018` | Three committed, immutable artifacts of this run describe text that a later correction changed, and a reader of any of them alone would be misled: the attempt-2 implementation report's `C-003` and `C-007` rows and the validation report's `DF-001` row describe the pre-CR-005 wording (`O-016`), and the completion package's run summary reads runtime 0.5.0 where the ledger now reads 0.6.0 (`FR-07`). The closure record carries the CR-005 correction; this proposal carries both | `omn-dev-2-reviewer` | Resolved by downstream record only. Committed run evidence is not amended, which is the price of immutability and is recorded rather than repaired |
| `O-019` | The conforming example in `agents/omn-orchestrator/examples.md` still shows a phase row its own contract rejects: in the closure-basis example, the coordinating phase's row carries a real gate, a gate decision of `none` and a progression of `complete`, the shape check `O5` of that agent's output module rejects and the module's own non-conforming section forbids. The producing agent of this run's closure record followed the rule rather than the example, as the producing agents of `FC-011`'s and `FC-012`'s runs did before it. Third independent encounter, still uncorrected | `architect` | Open, low. No artifact is at risk because the output contract governs over the example; the repair is a framework-internal change needing its own routed run |
| `O-020` | The profile's `Recorded Framework Changes` index carries rows through `FC-006` only, so `FC-007` through `FC-013` are absent from it. Adding them is a framework-internal edit outside the single-file write this authoring session was authorised to make. The index is a directory and not an authority — the self-hosting verifier discovers proposals by glob, which is why all twelve existing proposals validate under `S6` despite six missing rows — so its absence blocks nothing. Grown from `FC-011`'s and `FC-012`'s residual rows | operator | Open; append the rows with the next routed framework change, or as operator housekeeping |
| `O-021` | `omn-orchestrator` is the contracted producer of this artifact type, yet its manifest permits no repository write in any phase and its charter states that it writes its own artifact and its result envelope and nothing else. This instance was authored under an explicit operator authorisation scoped to exactly this one file, with no invocation envelope governing it, so the run carries no persisted evidence of this pass beyond the file itself. The standing contradiction has been tracked across several proposals and is unchanged | `omn-tech-lead` | Open, unchanged. Resolve by either narrowing the producer list or widening the manifest's write scope for this artifact alone |
| `O-022` | Three working-directory and citation-form hazards in the framework's own tooling, each of which changes what a correct tool run tells a reader. The scope classifier decides a path by a glob keyed on the framework directory prefix, so the same file classifies in-scope or unmatched depending on whether the citation carries that prefix, which is why every row of the Scope Classification table above reads out-of-scope and needs a paragraph to explain it. The recovery proof plans and removes probe runs under the runs directory and the multi-phase proof replays into a committed run's tracked store, so neither definition-of-done proof can be executed by a role whose write scope is one file, which is why two Verification rows above carry another party's figure. And the self-hosting verifier run from inside the framework directory reports a spurious 5 of 8 with every proposal failing `F7`, which the closure record named so that reading is not acted on | `architect` | Open. None is caused by this change; the second is the reason `FR-03` and `FR-11` above carry measured rather than re-executed figures, and the first is the reason the Scope Classification table needs a note |
| `O-023` | Every whole-repository measurement this run recorded was taken on a shared, non-quiescent working tree: the full-suite count moved 404 to 473 across the run's lifetime as a concurrent change added tests, the runs directory held 17 or 18 entries depending on the verifier's own probe runs, and `run-4c51600606df` has been executing concurrently since 14:21:31Z. The Verification Gate reconciled the suite count exactly and attributed both failures, so the figures are sound as reconciled; the standing hazard is that a later reader treats any of them as isolation evidence | `omn-qa` | Open, and not a defect in anything this run produced. Recorded because it is the qualification that must travel with every number in this proposal |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorised
  by the session operator for this single file in an operator-dispatched pass outside any phase,
  discharging `FU-001` of the run's closure record
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix Gate — once
  rejecting, once approving after the authorised rollback — and at the Verification Gate, and
  omn-documentation at the Closure Gate; each an owner the gate matrix assigns, and none the role
  that produced the evidence it assessed
- Acceptance basis: all five phases of the routed workflow executed with artifacts their registered
  validators accepted at 30/30, 30/30, 32/32, 31/31 and 34/34, with the superseded attempt's own
  report accepted at 32/32 before a gate rejected it on substance; every gate the Phase Model
  declares decided by a non-producing owner with its rationale and evidence reference recorded, and
  the one rejection followed by a recorded human rollback authorisation and a fresh human decision
  over the rebuilt evidence — the mechanism this change delivers, exercised for the first time on
  the run that delivered it and legible in its ledger at transitions 16 to 19 and 25; seventeen
  acceptance criteria at fourteen met, none not met and three blocked, each blocked criterion placed
  where it is settled and none read as met; CR-005 recorded closed with its re-runs named, and the
  version move recorded with its re-validation and its consequence for runs opened under 0.5.0;
  four operator actions disclosed with what each did; and three low defects and twenty-three open
  items carried forward with owners, including the run-status projection defect this run exercised
  live and the one run-accounting residual this proposal does not close
