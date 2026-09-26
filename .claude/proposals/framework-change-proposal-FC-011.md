# Framework Change Proposal: The Implementer's Accepted-Input Menu Now Names the Identifier the Refactor Workflow Delivers, and No Longer Names One No Agent Produces

```yaml
frameworkChangeProposal:
  proposalId: FC-011
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-79630cb5274d
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-011
- Change title: Widen the accepted-input menu of `omn-dev-1-implement` to accept `validation-report`, withdraw the orphan identifier `test-baseline-record`, and bring the five surfaces that describe that menu into agreement with it
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-79630cb5274d
- Authored on: 2026-09-06

## Authoring Baseline

- Authored at: 2026-09-06T02:52:14Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication`

This record is retrospective by a short interval rather than a long one. Run `run-79630cb5274d` was
submitted at 2026-09-05T04:47:38Z and its Closure Gate was decided at 2026-09-06T02:13:42Z; this
proposal was authored roughly forty minutes after that decision, in a later session, by an author
who carried no phase of the run. It is therefore assembled from the run's committed evidence rather
than produced inside the run, and nothing in it was available to the Closure Gate that approved the
run. Its function is the one the closure record itself scheduled as `FU-001`: give the run the
governance record the profile's Completion Rule `C-6` requires and that the run closed without.

## Change Statement

- Objective: make the `refactor` workflow able to hand phase 2 to phase 3. Guard `G5-INPUT` blocked
  `refactor-implementation` because the producing agent of the preceding phase, `omn-qa`, emits the
  output identifier `validation-report` while the consuming agent, `omn-dev-1-implement`, accepted
  only `technical-design`, `bug-analysis` and `test-baseline-record` — two disjoint sets, so the
  delivered artifact did not survive input narrowing and contract resolution raised
  `no accepted input type supplied`. A third fact compounded it: `test-baseline-record` was declared
  as an output by no agent anywhere in the framework, so a third of the consuming menu could never
  be satisfied by anything the framework produces. Defect report
  `runs/inputs/refactor-implementation-input-contract-defect-report.md`, classified severity high at
  triage on the analyst's own rubric, on the ground that the workaround exists but is unusable in
  normal operation.
- In scope: a declaration-only repair across eleven paths. The accepted menu of
  `agents/omn-dev-1-implement/manifest.yaml` gains `validation-report` additively and loses
  `test-baseline-record`, with its minimum-satisfaction prose restated to match; the required-input
  list in `agents/omn-dev-1-implement/identity.md`, the phase-ownership row in
  `agents/omn-dev-1-implement/execution.md`, the data dependencies in `registry/agents.yaml` and the
  source-input enumeration comment in `templates/implementation-report.md` are each brought into
  agreement with that menu; the agent and its registry record move from 1.0.0 to 1.1.0 under the
  agent's own semantic-versioning rule while `contractVersion` stays at 1.0.0; the same five files
  are mirrored into `omn_agent/_bundled_payload/` by the repository's own sync command, because the
  suite fails on drift between the two trees; and one contract-level regression module,
  `tests/test_agent_input_contracts.py`, is added, running 14 tests over the runtime's real
  narrowing and resolution functions.
- Out of scope: no runtime module was touched, so the input guard, `narrow_inputs` and
  `resolve_input_contract` in `runtime/framework_runtime.py` are byte-identical either side of the
  change and the repair comes entirely from the declarations they read. Also excluded, each routed
  rather than dropped: the thirteen remaining declared data edges that share this defect's cause;
  the two framework-wide prevention checks and the extended per-phase dispatchability verdict the
  analysis deferred because they misreport against the repository as it stands; the phase-accounting
  clause of the Completion Rule, established by the analysis as an independent defect with an
  independent cause and fix; per-phase narrowing of an agent's accepted menu, which is a structural
  decision routed to `architect`; advancing, dispatching or completing the stalled run
  `run-34ca35504b72`, excluded by the invocation that produced the change; the retired phrasing that
  survives at `workflows/workflow-engine.md` line 189, outside the authorised surface list; and
  hand-syncing the second payload copy tracked under `build/`, deliberately not done.
- Acceptance basis: the seven acceptance criteria of the root-cause analysis's Validation Plan,
  measured by `omn-qa` at `regression-validation`. Six met on first-hand executed evidence —
  contract replay of the pre-fix and post-fix menus, both sibling pools still resolving, the refusal
  branch still refusing, the per-edge scan falling by exactly one edge and dropping the refactor
  edge, the stalled run's persisted state clearing through the runtime's own pass, all five
  description surfaces read directly, and exactly one test module added. `AC-006` is recorded
  `blocked` and never as met, because settling it requires `run-34ca35504b72` to be advanced to
  completion, which no check inside this run could reach. Verdict `pass-with-reservations`,
  Validation Engine 31/31, six defects at two medium and four low, and no open critical or high
  defect.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `agents/omn-dev-1-implement/manifest.yaml` | none | out-of-scope | The accepted-input menu itself, its minimum-satisfaction prose and the version move to 1.1.0. A framework-surface file; this row records what the classifier returns for the citation form used throughout this proposal — see the note below the table |
| `agents/omn-dev-1-implement/identity.md` | none | out-of-scope | The agent contract's required-input list. Framework surface; same citation-form reading as above |
| `agents/omn-dev-1-implement/execution.md` | none | out-of-scope | The execution lifecycle's phase-ownership row for `refactor-implementation`. Framework surface; same reading |
| `registry/agents.yaml` | none | out-of-scope | The registry record's data dependencies and its version move to 1.1.0. Framework surface; same reading |
| `templates/implementation-report.md` | none | out-of-scope | The artifact template's source-input enumeration comment. Framework surface; same reading |
| `tests/test_agent_input_contracts.py` | none | out-of-scope | The added 14-test contract module. No inclusion rule matches and none is expected to: the path sits outside the framework surface entirely |
| `omn_agent/_bundled_payload/**` | none | out-of-scope | The five mirrored counterparts of the five edits above. The mirror's contents duplicate the framework surface byte for byte, but its path matches no inclusion rule, which is the gap `FC-009` first recorded |
| `runs/run-79630cb5274d/**` | none | out-of-scope | Run evidence written by the runtime while it carried this change. Exempt in substance under the profile's run-evidence exclusion, which is the rule that decides it when the path is given with its directory prefix |
| `proposals/framework-change-proposal-FC-011.md` | none | out-of-scope | This proposal: the governance record of the routed change, not a second change. Exempt in substance under the profile's proposal exclusion, on the same reading |

Every row above was recomputed with the profile's own classifier at the authoring instant and
records exactly what it returned, which for all nine paths is `no rule: no scope rule matches; the
path is outside the framework surface`. That answer needs its cause stated rather than left to be
inferred, because for five of these rows it is a property of the citation form and not of the file.
This proposal cites every repository path without its leading directory prefix, as the run's own
artifacts do. The profile's inclusion rule `SR-1` is a glob over the framework directory, keyed on
that prefix. Given the same five files with the prefix the rule matches on, the classifier returns
in-scope under `SR-1`, and that is the substantive reading: this change edits an agent manifest, two
of that agent's contract modules, the registry record the runtime resolves routing against, and an
artifact template — four framework surfaces the runtime reads at dispatch time. **This change is
framework-internal on its delivered surface.** The two evidence rows are exempt in substance for the
reasons the profile's run-evidence and proposal exclusions give, and read out-of-scope either way.
The prefix sensitivity is recorded as open item `O-015` rather than resolved here by asserting a
rule the classifier did not return for the string it was given.

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaved other than its contract declared. The
  `refactor` Phase Model routes an artifact across the `safety-net-establishment` to
  `refactor-implementation` edge and the workflow declares that phase dispatchable, yet the
  consuming agent's declared menu made the delivered artifact unusable and the guard blocked the
  phase with a recorded reason. That is a defect in a registered declaration, not a capability the
  framework lacked, so `capability-addition` is not the class: nothing new is gained, a declared
  behaviour is restored. `structure-preserving-change` is equally indefensible, because observable
  runtime behaviour changes — a phase that could not be dispatched can now be dispatched
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: triage-and-impact
- Required inputs supplied: `defect-report`
- Routing evidence: the profile's routing resolver, run at the authoring instant for the intent
  `defect-repair`, resolves to `/bugfix` over `fix-bug` v1.0.0 at `triage-and-impact` of 5 with the
  required input type `defect-report`. That is exactly what
  `runs/run-79630cb5274d/execution-request.json` records as `command_id`, `workflow_id`, the first
  enqueued phase and the single supplied input, digest `sha256:76384910923398dcb752564a5c3f523f`.
  The run's `intent` field reads `feature`, which is submission metadata carrying no routing
  consequence: the profile routes on the change class and the command, and both agree

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-79630cb5274d/execution-request.json` | resolved; `command_id` is `bugfix`, `workflow_id` is `fix-bug` v1.0.0, five phases enqueued, one input recorded with a digest — `defect-report` at `runs/inputs/refactor-implementation-input-contract-defect-report.md`; submitted 2026-09-05T04:47:38Z |
| `E-2` | `runs/run-79630cb5274d/run-ledger.json` | resolved; run status `Completed`, five phases all `completed`, four gates all `approved` with owner role, deciding authority, rationale, evidence reference and decision timestamp recorded for each; the recovery block records 10 classifications, 10 resolved, 0 open |
| `E-3` | `runs/run-79630cb5274d/events.jsonl` | resolved; 66 canonical events, including `E-0030` and `E-0031` (attempt 1 rejected for undeclared side effects, classified `policy-failure`), `E-0033` (the operator policy exception), `E-0038` and `E-0039` (attempt 2 rejected at `C7.1`, classified `output-schema-failure`, retry scheduled) and `E-0053` (the `worker-loss` reclaim of `regression-validation` attempt 1) |
| `E-4` | `runs/run-79630cb5274d/state.json` | resolved; five state work items, all `completed` and `Completed`, none blocked and none carrying a blocked reason; four gate work items, all `completed`; 41 recorded transitions |
| `E-5` | `runs/run-79630cb5274d/completion-package.md` | resolved; aggregates the five-phase ledger, the four gate decisions with their recorded authorities, and the per-phase module provenance digests |
| `E-6` | `runs/run-79630cb5274d/states/fix-implementation/artifacts/implementation-report.md` | resolved; the delivered change, with 11 change-set entries, 7 test-evidence entries, 4 recorded deviations and 4 residual risks. Each of the five phases committed its contracted artifact — two `bug-analysis.md`, this report, `validation-report.md` and `orchestration-result.md` |
| `E-7` | `runs/run-79630cb5274d/states/fix-implementation/validation-report.json` | resolved; a validation report exists for each of the five executed phases and every one records `pass` — 30/30, 30/30, 32/32, 31/31 and 34/34, with zero blocking and zero correctable failures in each |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | completed | Executed against the run in one attempt; 24 reproduction entries, 6 root-cause entries, 4 open questions, severity confirmed high on the analyst's own rubric, and the Completion Rule consequence deliberately routed out as a separate defect with an independent cause; Validation Engine 30/30 | host-dispatched `omn-dev-1-bug-analyst` subagent v1.0.0 | `runs/run-79630cb5274d/states/triage-and-impact/validation-report.json` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | completed | Executed against the run in one attempt, returning `completed_with_findings`; 38 reproduction entries, 6 root-cause entries, 6 open questions, and the Fix Strategy and Validation Plan every later phase was measured against; Validation Engine 30/30. The Phase Model declares no gate here, so none is recorded | host-dispatched `omn-dev-1-bug-analyst` subagent v1.0.0 | `runs/run-79630cb5274d/states/root-cause-analysis/validation-report.json` |
| `fix-implementation` | `omn-dev-1-implement` | completed | Executed against the run over three attempts, consuming the whole retry budget; 11 change-set entries, 7 test-evidence entries, 4 deviations and 4 residual risks; Validation Engine 32/32. Attempt 1 was rejected at `E-0030` with zero blocking and zero correctable failures but four undeclared side effects, all under `runs/run-34ca35504b72/`, a permanent write exclusion for this agent, and classified `policy-failure` at `E-0031`; the operator recorded a policy exception at `E-0033` and cleared it. Attempt 2 was rejected at `E-0038` on determinism check `C7.1` and retried. Attempt 3 was accepted at 32/32 | host-dispatched `omn-dev-1-implement` subagent, v1.0.0 on attempt 1 and v1.1.0 on attempts 2 and 3, with two frozen-snapshot metadata fields corrected directly by the operator on attempt 3 | `runs/run-79630cb5274d/states/fix-implementation/validation-report.json` |
| `regression-validation` | `omn-qa` | completed | Executed against the run over two attempts, of which one was reclaimed rather than charged; 7 acceptance criteria at 6 met, 0 not met and 1 blocked, 6 defects at two medium and four low, 5 open questions, verdict `pass-with-reservations`; Validation Engine 31/31. Attempt 1 was released as `worker-loss` at `E-0053` after the host process exited between the artifact being written and the result envelope being written; the attempt-2 agent adopted the artifact it found, independently re-verified it, and corrected it in nine places including retracting a false `AC-005` claim — the retraction that surfaced `DF-006` | host-dispatched `omn-qa` subagent v1.0.0, attempt 2 | `runs/run-79630cb5274d/states/regression-validation/validation-report.json` |
| `closure-and-communication` | `omn-orchestrator` | completed | Executed against the run in one attempt; 5 phase-progression rows, 4 handoffs all accepted, 9 escalations at six medium and three low with none critical or high open, 7 follow-up actions each owned, 5 open questions, disposition `closed-with-followups`; Validation Engine 34/34. The record held its own row at `blocked` rather than anticipatorily `complete`, because its Closure Gate was undecided when it was written; that gate was decided 6m 4s later, which is why this proposal reports the phase `completed` and the closure record reports it `blocked`. Both are accurate at their own instant, as the profile's point-in-time evidence rule requires | host-dispatched `omn-orchestrator` subagent v1.0.0 | `runs/run-79630cb5274d/states/closure-and-communication/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact and none blocked, so the
Completion Rule's `C-3` is satisfied on its executed limb throughout and its operator-performed limb
is never reached. All five were performed by host-dispatched subagents under their contracted
validators. Three operator interventions are recorded above rather than absorbed: the policy
exception at `E-0033`, the two frozen-snapshot metadata corrections on attempt 3, and the recording
of each gate decision on behalf of the deciding subagent. Each was assessed at a gate by an owner
who produced neither the evidence nor the intervention.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | omn-tech-lead subagent, recorded by session operator, 2026-09-05T05:11:46Z | Severity and reproducibility confirmed on first-hand evidence that re-derives independently: the disjoint identifier sets in the two manifests are as recorded, the `G5-INPUT` block detail on the stalled run matches the analysis character for character, and high is the correct rubric row for a workaround that exists but is unusable in normal operation. Routing the Completion Rule consequence out as a separate defect was accepted as sound, the two having independent causes and independent fixes. Approved with four conditions carried into root-cause analysis, none of which changed the root cause, the severity or the fix direction. `omn-dev-1-bug-analyst` produced the evidence and is excluded from deciding |
| Fix Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-05T07:10:06Z | All five description surfaces verified independently and now state the same accepted set; the widening leaves both existing identifiers and the menu's refusal behaviour intact; the withdrawal breaks no caller, because no agent manifest declares that identifier as an output and none of the 54 committed invocation envelopes ever supplied it. The added module was re-run independently at 14/14 and exercises the runtime's real narrowing and resolution functions rather than restating them; the minor version bump follows the agent's own written compatibility rule and `contractVersion` correctly stays at 1.0.0. The evidence is not isolated from a concurrent writer and the report says so; the change being declaration-only, that gap was carried into validation as a condition rather than treated as a blocker here. `omn-dev-1-implement` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-06T01:50:43Z | The defect is independently confirmed no longer reproducible: replaying the runtime's own narrowing and resolution against the committed manifest reproduces the stalled run's recorded block detail character for character and against the working tree resolves cleanly; the stalled run reads its blocked phase as pending and Ready with every block field null and its failure envelope resolved by the runtime state engine; an independent per-edge scan drops exactly the refactor edge. The isolated evidence suffices without the contaminated whole-suite figure, the change's eleven paths being disjoint from every foreign working-tree entry. `pass-with-reservations` is the verdict the validating role's own adjudication table yields for one blocked criterion with nothing not-met and no open critical or high defect. `omn-qa` produced the evidence and is excluded from deciding; the co-owner decided |
| Closure Gate | approve | omn-documentation | omn-documentation subagent, recorded by session operator, 2026-09-06T02:13:42Z | Spot-checked against the run ledger, the state store and all 66 events: the closure record's phase progression, its three gate attributions and its recording of its own phase as blocked rather than anticipatorily complete all reconcile with the machine record; the seven Verification Gate conditions are discharged with substance rather than restated; and the three operator interventions are each recorded with what was done and what it costs the evidence. `closed-with-followups` is correct for a run carrying one unsettled criterion, six medium-and-low defects, five routed open questions and no open critical or high escalation. Approved with two reservations recorded separately: the record's quotation of its own gate work item as pending is now stale, and the contract-example contradiction the producing agent found is carried in no durable record. `omn-orchestrator` produced the evidence and is excluded from deciding |

Every gate the `fix-bug` Phase Model declares was decided, each by an owner the gate matrix assigns
and none by the role that produced the evidence assessed. None was waived and none was
auto-approved: all four are recorded as human decisions.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | inspection | pass; 6/6 checks, 37 of 37 phases resolving the full capability and context chain, 0 blocked. Executed from the repository root at the authoring instant, not merely inspected — the note below the table gives the reason the Command column reads this way |
| Validator coverage and decisiveness | inspection | pass; 6/6. Executed twice from the repository root: the first execution aborted with a permission error reading the state file of a foreign in-flight run that a concurrent session removed mid-scan, and the immediate re-run returned 6/6 with that run absent from the tree. The failure was an artefact of a non-quiescent repository, not of this change |
| Recovery behaviour | inspection | pass; 41/41. Executed twice for the same reason: the first execution failed asserting that a probe run it had itself just created did not exist, a concurrent session having removed it underneath; the immediate re-run returned 41/41 and removed its injected runs |
| Committed evidence still verifies | inspection | pass; 10/10 PROVEN on `run-c5a8d50d3238`, so no previously committed proof was invalidated by this change |
| Self-hosting governance | inspection | 7/8 at the authoring instant. `S1` to `S7` pass: the profile parses, all seven routing rows resolve, the change-proposal contract is registered, all ten recorded proposals re-validate at 38/38 each under `S6`, and `S7` confirms the Completion Rule for each of their runs. `S8` fails, naming three unaccounted runs — `run-34ca35504b72`, `run-4c51600606df` and this run — of which this proposal removes the third on the next execution. The other two are open item `O-013` |
| Scope classification recomputes | inspection | pass; the profile's classifier was run at the authoring instant on each of the nine paths in the Scope Classification table, and every row records exactly what it returned. The five framework-surface paths were additionally classified with their directory prefix, where the classifier returns in-scope under `SR-1`, which is the substantive reading recorded under that table |
| Routing resolves | inspection | pass; the profile's routing resolver for the intent `defect-repair` resolves to `/bugfix` over `fix-bug` v1.0.0 at `triage-and-impact` of 5 with required input `defect-report`, agreeing with `E-1` on all four |
| The added contract module still passes | `python -m unittest tests.test_agent_input_contracts` | pass; 14 tests run, 14 passed, at the authoring instant against the current tree — the same figure the Fix and Verification Gates recorded |
| The repair holds in the live record | inspection | pass, and it has gone further than the run itself could take it. Read-only inspection of `runs/run-34ca35504b72/state.json` at the authoring instant reads `refactor-implementation` as `running` and `Executing`, with no blocked reason and no failure class: the phase this defect held blocked since 2026-08-27 has been dispatched and is executing for the first time. That run is being carried forward by an actor outside this proposal, which is the strongest available evidence that the repair is real and the weakest possible ground for claiming anything about its outcome — nothing here reports on what that phase produces |
| Whole discovered unit suite | inspection | not re-executed at authoring, deliberately: the suite rewrites documentation files in place while it runs, a repository write outside this authoring session's permitted writes. The run's own figure moved 342 to 399 to 404 across its lifetime as a concurrent writer added tests, and the validation records the whole-suite number as a contaminated measurement rather than as isolation evidence. The verdict rests on 83 targeted checks at 83 passed, the contract replays, and the persisted state of the repaired run |
| Multi-phase state machine | inspection | not re-executed at authoring. The probe appends replay bookkeeping to a committed run's tracked state file, and modifying committed run evidence is prohibited to this role. Measured at the Verification Gate at 14 of 15, failing only `M6`, which requires one run to have traversed planning, design and delivery phases and which a `fix-bug` run structurally cannot satisfy; the identical verdict was recorded at baseline before any file was touched, so it is not attributable to this change |
| This proposal against its registered validator | inspection | pass; 38 checks run, 38 passed, 0 blocking and 0 correctable failures, with the two not-machine-checkable obligations recorded. Re-run by `S6` of the self-hosting verifier on every later execution |

One note on the Command column, because it reads oddly and the cause is not a weakness in the
checks. This proposal cites every repository path without its leading directory prefix, so a command
naming a framework script cannot be written here in a form that resolves from the repository root,
which is what check `F10` requires of any command cell that is not `inspection`. Every row marked
`inspection` that says it was executed was executed, from the repository root, at the authoring
instant; the word records a citation constraint, not a weaker class of evidence. The three rows that
genuinely were not executed say so in their own words and give the reason. The directory sensitivity
that forces this is carried as open item `O-015`.

## Risk and Rollback

- Blast radius: eleven paths and no more. Five declaration surfaces — an agent manifest, two of that
  agent's contract modules, its registry record and one artifact template — plus their five mirrored
  counterparts under `omn_agent/_bundled_payload/`, plus one added test module. No runtime module,
  workflow specification, command, gate surface, validator or continuous-integration configuration
  changed, which is what makes the pre-fix and post-fix replays comparable: only the data under the
  unchanged functions moved. One persisted run record changed as a direct and intended consequence —
  `run-34ca35504b72`'s `refactor-implementation` work item returning from blocked to pending — and
  that write was performed by the runtime's own re-evaluation pass rather than by any agent.
- Risk assessment: four residual risks were recorded by the implementation and each was assessed at
  a gate by a non-producing owner. The load-bearing one is `R-001`, carried into closure as `ES-006`
  and recorded here as `O-002`: the widened menu is agent-global, so the two sibling implementation
  phases now accept a validation report as sole satisfaction of their menu although neither should
  ever see one. Nothing but guard ordering prevents a future workflow that places a validation phase
  ahead of an implementation phase from passing the input guard, where the failure would surface as
  a poor implementation report rather than as a blocked phase. No executable path reaches it today,
  because the predecessor and gate guards run ahead of the input guard and evaluation returns on the
  first blocking verdict, and the added module holds both sibling pools resolving and the menu still
  refusing a pool carrying no accepted identifier; nothing pins that ordering against future change.
  It was identified at analysis, carried openly, and accepted at three gates. `R-003`, recorded here
  as `O-010`, is certain rather than probable: moving the registry record to 1.1.0 removes the gate
  auto-approval precedent for every gate assessing this agent's output until one gate is decided at
  the new version, so the next such gate requires a human decision — accepted because it fails
  toward a human decision rather than away from one. `R-002` and `R-004` are measurement conditions
  rather than product risks and are recorded under Verification. One defect the change introduced
  stands: `DF-006`, a second payload copy tracked under `build/` still declaring the withdrawn
  identifier and version 1.0.0, rated low because no test, verifier or runtime path reads it, and
  carried as `O-005`.
- Rollback procedure: revert the eleven paths. That restores the disjoint menu, re-blocks the
  `refactor` phase 2 to phase 3 edge at `G5-INPUT`, and reinstates an orphan identifier no agent
  produces. The condition that would justify it is `R-001` materialising — an implementation phase
  resolving its input contract on a stray validation report — and the correct response to that is
  the per-phase menu scoping routed to `architect` under `O-002`, not this revert, which would trade
  one defect for the one it repaired. Reverting invalidates no committed run evidence: this run's
  record remains a valid account of a delivered-then-reverted change and this proposal remains its
  governance record. It would, however, strand work in flight, because `run-34ca35504b72` is
  executing the phase this change unblocked at the authoring instant; a revert taken after that
  point removes the premise that phase was dispatched under, and is a decision for the run's
  operator rather than a mechanical undo.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6; 37 of 37 phases dispatchable, 0 blocked, every phase owner host-invocable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6, on a re-run after a concurrent session removed a foreign run's state file mid-scan; the first execution's permission error is recorded under Verification rather than omitted |
| `FR-03` | Recovery behaviour | pass | 41/41, likewise on a re-run after concurrent interference with the verifier's own probe run |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` at 10/10 PROVEN; no committed proof was invalidated |
| `FR-05` | Self-hosting governance resolves | pass | The profile parses, all seven routing rows resolve, the change-proposal contract is registered, all ten recorded proposals re-validate at 38/38, and every one of their runs satisfies the Completion Rule — `S1` to `S7`. The two remaining `S8` rows are a residual this change did not cause, recorded as `O-013` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-79630cb5274d` is a `/bugfix` run over `fix-bug` v1.0.0, submitted with the input type the profile's routing row requires; this proposal links its artifacts as `E-1` to `E-7` |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0. No runtime module changed; the repair is declaration-only and the guard, the narrowing function and the contract resolver are byte-identical either side of it. The version that did move is the agent's, 1.0.0 to 1.1.0, with `contractVersion` correctly held at 1.0.0 |
| `FR-08` | Documentation matches delivered behaviour | accepted | Four of the five edited surfaces were themselves the documentation impact, so no surface this change was authorised to touch still describes the old menu, and the validation confirmed all five agree by direct read. One live specification surface still carries the retired phrasing — `workflows/workflow-engine.md` line 189 — recorded as defect `DF-005`, rated low, accepted at the Verification Gate and carried as `O-007`. Recorded `accepted` rather than `pass` because that surface exists and the item must not read clean while it does |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim was executed or directly read: contract replays either side of the change, 83 targeted checks at 83 passed, five description surfaces read directly, the per-edge population measured on both sides, the repaired run's persisted state inspected read-only. The three real gaps are recorded rather than omitted — the unsettleable `AC-006`, the rule-dependent edge population where the implementation measured 11 to 10 and the validation reproduced 14 to 13 under the runtime's own matcher, and the contaminated whole-suite figure |
| `FR-10` | Rollback stated | pass | Risk and Rollback above: an eleven-path revert, the condition that would justify it, the better answer to that condition, and the in-flight work a late revert would strand |
| `FR-11` | Multi-phase state machine still proves out | accepted | 14 of 15 at the Verification Gate, failing only `M6`, with the identical verdict recorded at baseline before any file was touched, so it is not attributable to this change. Not re-executed at authoring because the probe appends to a committed run's tracked state file, which this role may not modify; that tooling hazard is carried in `O-015`'s neighbourhood as a standing condition on executing the proofs |
| `FR-12` | Release note where consumer-visible behaviour changed | accepted | Behaviour a framework consumer depends on did change — the `refactor` workflow can now pass phase 2 to phase 3 — and no release note exists yet. The `fix-bug` closure phase produces the coordination record a note is written from, not the note itself; the Closure Gate approved that record, and publication of the known-issue status and the note is carried as `O-011`, owned by `omn-documentation` |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | `AC-006` is unsettled and must not be read as met. It bundles a half this run confirmed with a half no check inside the run could reach, because settling it requires `run-34ca35504b72` to be advanced to completion. The criterion also needs re-specifying: as written it spans two runs and was always going to end `blocked`, an observation the Verification Gate made independently. Carried from the closure record as `FU-002` and `ES-001` | `omn-product-owner` | Open. Criterion design belongs to `omn-qa` with the product owner, and the scope call on whether a criterion may span two runs is the product owner's, which is why it is owned here rather than absorbed into a closure |
| `O-002` | The widened accepted menu is agent-global, so nothing but guard ordering prevents a future workflow that places a validation phase ahead of an implementation phase from passing the input guard. Root removal needs per-phase input scoping rather than an agent-global menu. Carried from the closure record as `ES-006` and from the implementation as `R-001` | `architect` | Open, accepted risk at three gates — Triage, Fix and Verification — each by an owner that did not produce the evidence. Routed for a structural decision this run could not take |
| `O-003` | A guard re-evaluation that unblocks a work item does not refresh that run's reporting ledger: `run-34ca35504b72`'s state store and its run ledger disagreed about the same work item, the ledger keeping its pre-clearing timestamp. The cause is structural — the re-evaluation command reaches the ledger writer only on the branch that actually decided a gate. Carried as `DF-001`, `ES-002` and `Q-003` | `architect` | Open. Bounded by two properties recorded with it: it self-corrects at the next command that writes that run's ledger, and it fails safe, because the stale side reads blocked rather than ready |
| `O-004` | The `V-003` rationale in the committed implementation report states that the invocation envelope and the state ledger recorded agent version 1.0.0; both read 1.1.0, and the report's own `agentVersion` value is defended on that statement. Committed run evidence is immutable and the report was not, and must not be, edited. Carried as `DF-002` and `ES-003` | `omn-dev-2-reviewer` | Resolved by downstream record only. The closure record carries the correction and so does this proposal; the report itself will keep stating the false claim wherever it is read, which is the price of immutability and is recorded rather than repaired |
| `O-005` | A second copy of the framework payload is tracked in version control under `build/`, still declaring the withdrawn identifier and version 1.0.0. Before this change the two copies were byte-identical; the only five files that now differ are exactly the five this change edited. The mirror check's scope covers the other copy alone, so nothing in the repository would report this one drifting again. Carried as `DF-006`, `ES-007` and `Q-005` | `omn-tech-lead` | Open, deferred not dismissed, and explicitly not to be cleared by hand-syncing, which would entrench tracked build output as something to maintain rather than decide. The decision asked for is which copy is authoritative and whether build output belongs in version control at all |
| `O-006` | The canonical reason-code set carries no value for an operator-authorised policy exception, so event `E-0033` was recorded with a tool-failure reason code while its own detail describes an authorised boundary crossing in which no tool failed. No accurate code was available and no verifier catches it, so a reader or a query filtering on reason code misclassifies that event. Carried as `DF-003`, `ES-008` and `Q-002` | `architect` | Open. The decision asked for is whether such a value is added, or whether authorised boundary crossings are recorded by another mechanism |
| `O-007` | `workflows/workflow-engine.md`, line 189, still names the safety-net output by the phrasing this change retired everywhere else, so one live specification surface continues to describe an output by a name no agent declares. It sits outside the surface list this run was authorised to edit. The same phrase survives in a dated report, which is a historical record and is not to be edited. Carried as `DF-005` and `FU-004` | `architect` | Open, rated low. It needs a change of its own, and it is the reason `FR-08` above reads `accepted` rather than `pass` |
| `O-008` | The added test module's docstring states a declared-data-edge population as unqualified fact, but the population is rule-dependent: the validation reproduced 14 falling to 13 under the runtime's own containment matcher, stricter matching measures 13 to 12, and the implementation's own scan measured 11 to 10 over the same repository. Each figure needs the term-matching rule that produced it named beside it. The figures appear only in the docstring and in no assertion. Carried as `DF-004`, `FU-005` and `Q-001` | `omn-dev-1-implement` | Open, rated low. The related question — whether the framework should fix one canonical rule for comparing Phase Model terms — is routed to `architect` with `Q-001` |
| `O-009` | Four signals the validation named are unmonitored: work items blocked for a missing dependency output whose declared predecessors are all complete, which is this defect's exact signature; the declared-data-edge mismatch population, always reported with the matching rule that produced it; divergence between any run's state store and its reporting ledger, which `O-003` shows is currently unwatched; and the per-phase dispatchable count read alongside the edge population rather than alone. Carried as `FU-006` | `omn-qa` | Open, rated low |
| `O-010` | Moving the registry record to 1.1.0 removes the gate auto-approval precedent for every gate assessing this agent's output until one gate is decided at the new version, so the next such gate requires a human decision. Carried as `FU-007` and implementation risk `R-003` | `omn-tech-lead` | Accepted risk, recorded rather than treated as a problem: it fails toward a human decision rather than away from one, which is the direction a version bump should fail in |
| `O-011` | The known-issue status and the release-note entry have not been published. The Closure Gate this waited on was decided and approved at 2026-09-06T02:13:42Z, so the blocking half of `FU-003` is discharged and the publishing half is not; the closure record is the source the note is written from and does not replace it | `omn-documentation` | Open. It is why `FR-12` above reads `accepted` |
| `O-012` | The conforming example in `agents/omn-orchestrator/examples.md` shows a phase row its own contract rejects. In the closure-basis example table, the row for the coordinating phase carries a real gate, a gate decision of `none`, and a progression of `complete` — precisely the shape check `O5` of that agent's output contract rejects, and precisely what the same module's own non-conforming example forbids when it states that a gate-owning phase is never marked complete anticipatorily. The producing agent found this while writing the closure record and followed the rule rather than the example, recording its own row as `blocked`; the Closure Gate approved with the reservation that the finding was carried in no durable record. This proposal is that record | `architect` | Open, and recorded here for the first time. Rated low: the module set is ordered so that the output contract governs over the example and the example is explicitly illustration, so no artifact is at risk. The repair is to correct the example row, and it is a framework-internal change needing its own routed run |
| `O-013` | Two framework runs remain unaccounted by any change proposal and fail `S8` of the self-hosting verifier: `run-34ca35504b72`, held since 2026-08-27 and only now advancing, and `run-4c51600606df`, submitted 24 minutes before this run. This proposal accounts for `run-79630cb5274d` alone; fabricating proposals for runs it did not carry would falsify the record. Descended from `O-001` of `FC-007` | `omn-orchestrator` | Open, pre-existing and shrinking: four runs at `FC-007`, three before this proposal, two after it. `run-34ca35504b72` additionally cannot satisfy the Completion Rule while it is mid-workflow, so its accounting waits on its own closure rather than on an author |
| `O-014` | `omn-orchestrator` is the contracted producer of this artifact type, yet its manifest permits no repository write in any phase and its charter states that it writes its own artifact and its result envelope and nothing else. This instance was authored under an explicit operator authorisation scoped to exactly this one file. The standing contradiction is tracked since `O-003` of `FC-005` | `omn-tech-lead` | Open, unchanged. Resolve by either narrowing the producer list or widening the manifest's write scope for this artifact alone |
| `O-015` | Three working-directory and citation-form hazards in the framework's own tooling, each of which changes what a correct tool run tells a reader. The scope classifier decides a path by a glob keyed on the framework directory prefix, so the same file classifies in-scope or unmatched depending on whether the citation carries that prefix, which is why every row of the Scope Classification table above reads out-of-scope and needs a paragraph to explain it. The validator-coverage verifier reports a spurious partial verdict when run from the framework directory and a full pass when run from the repository root, which the closure record names explicitly so a reader does not act on the failure seen from the wrong directory. And the multi-phase proof appends replay bookkeeping to a committed run's tracked state file, so running the definition-of-done proofs drifts committed run evidence without any agent editing it | `architect` | Open. None is caused by this change; the third is the reason `FR-11` above reads `accepted`, and the first is the reason the Scope Classification table needs a note |
| `O-016` | The profile's `Recorded Framework Changes` index carries rows through `FC-006` only, so `FC-007` through `FC-011` are absent from it. Adding them is a framework-internal edit outside the single-file write this authoring session was authorised to make. The index is a directory and not an authority — the self-hosting verifier discovers proposals by glob, which is why all ten currently validate under `S6` despite five missing rows — so its absence blocks nothing. Grown from `O-005` of `FC-007` | operator | Open; append the rows with the next routed framework change, or as operator housekeeping |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorised
  by the session operator for this single file, discharging `FU-001` of the run's closure record
- Accepted by: omn-tech-lead at the Triage Gate, omn-dev-2-reviewer at the Fix and Verification
  Gates, and omn-documentation at the Closure Gate — each an owner the gate matrix assigns, and none
  the role that produced the evidence it assessed
- Acceptance basis: all five phases of the routed workflow executed with artifacts their registered
  validators accepted at 30/30, 30/30, 32/32, 31/31 and 34/34; every gate the Phase Model declares
  decided by a non-producing owner with its rationale and evidence reference recorded; four charged
  retries and one reclaimed attempt recorded with what each repaired; three operator interventions
  disclosed with what each cost the evidence, including the qualification that the determinism pass
  on the final fix attempt was operator-assisted rather than agent-deterministic and is therefore
  weaker evidence of that agent's own determinism than an unassisted pass would have been; one
  acceptance criterion recorded unsettled and never as met; and six defects and sixteen open items
  carried forward with owners, including the one defect this change introduced and the two
  run-accounting residuals it does not close
