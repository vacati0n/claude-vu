# Framework Change Proposal: The Orientation Document's Folder Inventory Now Describes Every Directory at the Framework Payload Root, Sixteen of Sixteen, Additively and Without Changing Any Behaviour

```yaml
frameworkChangeProposal:
  proposalId: FC-012
  changeClass: structure-preserving-change
  routedCommand: refactor
  routedWorkflow: refactor
  runId: run-34ca35504b72
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-012
- Change title: Complete the `## Folder Descriptions` inventory of the framework's orientation document from twelve of sixteen payload-root directories to sixteen of sixteen, by adding rows for `domain-model/`, `prompts/`, `registry/` and `runtime/`, leaving every pre-existing row untouched
- Change class: structure-preserving-change
- Routed command: `/refactor`
- Run identifier: run-34ca35504b72
- Authored on: 2026-09-06

## Authoring Baseline

- Authored at: 2026-09-06T07:19:40Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-invariants-and-risk-profile`, `safety-net-establishment`, `refactor-implementation`, `behavioral-validation`, `closure-and-debt-record`

This record is retrospective by a very short interval. Run `run-34ca35504b72` was submitted at
2026-08-27T12:50:39Z and its Closure Gate was decided at 2026-09-06T07:04:10Z; this proposal was
authored roughly fifteen minutes after that decision, in a later session, by an author who carried
no phase of the run. It is assembled from the run's committed evidence rather than produced inside
the run, and nothing in it was available to the Closure Gate that approved it. Its function is the
one the closure record scheduled as its fourth follow-up action: give the run the governance record
the profile's Completion Rule `C-6` requires and that the run closed without.

The run spans ten days of wall-clock time for roughly five hours of work, and two of the three
things worth knowing about it are properties of that gap rather than of the change. They are
recorded in Phase Disposition and Open Items rather than smoothed into a clean narrative.

## Change Statement

- Objective: make the framework's orientation document describe the framework. Its
  `## Folder Descriptions` section listed twelve directories while the payload root holds sixteen,
  so the document that is injected into every contributor session as authoritative instruction
  silently omitted the framework's domain-specification, prompt-pattern, discovery-index and
  executable-runtime directories — four of the surfaces a contributor most needs to find, including
  the two the runtime itself resolves routing against. The omission is governance debt with a
  reader-facing cost and no runtime cost, which is exactly why it routes as a structure-preserving
  change rather than as a defect repair: nothing behaved other than its contract declared, and the
  claim being defended is the narrower one, that nothing observable changes.
- In scope: one file and one section of it. Four one-line rows were inserted into the existing list
  at the positions a reader scanning the directory tree would meet them, describing `domain-model/`,
  `prompts/`, `registry/` and `runtime/`, each authored against the folder's own named authority
  under the design's sequencing step `P-001` and each at summary granularity rather than restating
  the records those authorities hold. The delivered diff is seven insertions, zero deletions, one
  hunk, wholly inside the section body. The twelve pre-existing rows are unchanged in content and in
  relative order, reproducing the pinned row-key digest `6a0c112e6f2e9f0f3ef92e728c8216f4` exactly
  either side of the change.
- Out of scope: every other section of the document and every other file in the repository, the
  design's diff-confinement constraint making any edit outside the section a rejection condition. No
  contract, registry record, routing row, gate, template, workflow specification or runtime module
  was touched, and none was mirrored, because the document is absent from the installer's 267-file
  payload map and therefore has no bundled counterpart to keep in step. Also excluded and routed
  rather than dropped: the `prompts/` row's disagreement with its own folder, whose defective element
  is upstream of the implementation; the discrepancy the design recorded about `dependency-map.md`,
  which the design routes as a change of its own; and the sibling folder inventory in the payload-root
  `README.md`, which no phase of this run considered and which this proposal records for the first
  time as an open item.
- Acceptance basis: the ten acceptance criteria the safety-net phase derived from the design's
  constraints `C-001` to `C-009`, measured by `omn-qa` at `behavioral-validation`. All ten met on
  first-hand executed evidence: diff confinement proven both by the version-control instrument and
  by an independent recomputation of the out-of-section bytes at both revisions, additivity proven
  by the reproducing row-order digest, completeness proven by differencing the filesystem against the
  parsed row keys in both directions, every cited path token resolving at 22 of 22, and every
  verification script and test module on the declared regression surface reproducing its recorded
  value. Verdict `pass`, Validation Engine 31 of 31, five open defects all `low`, none contradicting
  a criterion and none blocking. Behavioural parity rests on a deductive isolation argument rather
  than on a statistical sweep, which is stated below under Risk and Rollback because it is the load-
  bearing claim of the whole run.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| the orientation document at the framework payload root, section `## Folder Descriptions` | none | out-of-scope | The only production file this change modified: four rows added, twelve unchanged. It is named descriptively rather than by filename throughout this record, because its own filename carries a token the model-independence rule forbids reproducing — the same convention the design, the implementation report and both validation reports adopted. That naming constraint is also why no path-shaped citation of it can be classified at all; see the note below the table |
| `runs/run-34ca35504b72/states/refactor-implementation/artifacts/implementation-report.md` | none | out-of-scope | The delivering phase's contracted artifact, and one of the two evidence writes that complete this change's three-file footprint. Exempt in substance under the profile's run-evidence exclusion, which is the rule that decides it when the path is given with its directory prefix |
| `runs/run-34ca35504b72/**` | none | out-of-scope | All other run evidence the runtime wrote while carrying this change: the ledgers, the event log, the state store, the completion package, and the five phase artifact sets. Exempt in substance on the same reading |
| `runs/inputs/**` | none | out-of-scope | The three supplied inputs the run was submitted with, of types `change-request`, `business-intent` and `architecture-context`. Operator-authored run inputs, not a framework surface, and cited by type rather than by filename for the naming reason above |
| `omn_agent/_bundled_payload/**` | none | out-of-scope | Recorded as a checked negative rather than as a touched path. The document is absent from the installer's 267-file payload map, so this change required no mirror sync and could not break payload parity; the eleven packaged-payload tests confirm it, and this row exists so that a later reader does not have to re-establish the absence |
| `proposals/framework-change-proposal-FC-012.md` | none | out-of-scope | This proposal: the governance record of the routed change, not a second change. Exempt in substance under the profile's proposal exclusion, on the same reading |

Every row above was recomputed with the profile's own classifier at the authoring instant and
records exactly what it returned, which for all six paths is `no rule: no scope rule matches; the
path is outside the framework surface`. That answer needs its cause stated rather than left to be
inferred, because it is a property of the citation form rather than of the files. This proposal
cites every repository path without its leading directory prefix, as the run's own artifacts do,
and the profile's inclusion rule `SR-1` is a glob keyed on that prefix. Given the changed file with
the prefix the rule matches on, the classifier returns in-scope under `SR-1`, and that is the
substantive reading: the modified document is the framework's own orientation surface, injected into
every contributor session, and **this change is framework-internal on its delivered surface**. Given
the run-evidence and proposal paths with their prefixes, the classifier returns out-of-scope under
`SR-3` and `SR-5` respectively, so those rows read out-of-scope on either form and are exempt in
substance as well as by citation.

This change strains the citation convention harder than any before it, because the file it modified
cannot be named at all — not with its prefix, not without it. The prefix sensitivity was recorded as
an open item by `FC-011`; the naming collision is recorded here for the first time, and both are
carried below as `O-021`.

## Routing Decision

- Change class: structure-preserving-change
- Selector satisfied by: structure or wording changes with no contract, routing or runtime behaviour
  change. The delivered edit inserts four descriptive rows into one list in one documentation
  section. No agent contract, registry record, routing row, gate definition, template, workflow
  specification or runtime module was modified, and the claim is not merely asserted: the document is
  resolved by no registry record, parsed by no validator, consumed by no workflow phase, absent from
  the installer payload, and named by exactly one module in the entire framework — the
  memory-optimisation runtime module, which carries it in a prose-compression target list and never
  parses its structure. `defect-repair` is not the class, because no registered capability behaved
  other than its contract declared; the document declared nothing and the runtime read nothing from
  it. `capability-addition` is not the class either, because the framework gains no capability,
  contract, registry record or runtime behaviour it did not have. The narrower claim is the one this
  row obliges the change to defend, and the Regression Gate is where it was defended
- Command: `/refactor`
- Primary workflow: refactor
- Entry phase: scope-invariants-and-risk-profile
- Required inputs supplied: `change-request`, `business-intent`, `architecture-context`
- Routing evidence: the profile's routing resolver, run at the authoring instant for the intent
  `structure-preserving-change`, resolves to `/refactor` over `refactor` v1.0.0 at
  `scope-invariants-and-risk-profile` of 5 with the three required input types above. That is exactly
  what `runs/run-34ca35504b72/execution-request.json` records as `command_id`, `workflow_id`, the
  first enqueued phase and the three supplied inputs, each carrying a digest. The run's `intent`
  field reads `feature`, which is submission metadata carrying no routing consequence: the profile
  routes on the change class and the command, and both agree

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-34ca35504b72/execution-request.json` | resolved; `command_id` is `refactor`, `workflow_id` is `refactor` v1.0.0, runtime version 0.5.0, five phases enqueued, three inputs recorded with digests — one each of `change-request`, `business-intent` and `architecture-context`; submitted 2026-08-27T12:50:39Z |
| `E-2` | `runs/run-34ca35504b72/run-ledger.json` | resolved; run status `Completed`, five phases all `completed`, four gates all `approved` with owner role, deciding authority, rationale, evidence reference and decision timestamp recorded for each; the summary records 43 transitions and 46 suppressed replays; the recovery block records 11 classifications, 11 resolved, 0 open, across four failure classes — seven `gate-approval-required`, two `worker-loss`, one `output-schema-failure`, one `dependency-failure` |
| `E-3` | `runs/run-34ca35504b72/events.jsonl` | resolved; 73 canonical events, including `E-0015` (the first design artifact rejected on two blocking checks, `D3.6` and `D8.5`), `E-0030` (the `worker-loss` reclaim of the week-long stalled lease on phase 2), `E-0036` (phase 3 blocked at guard `G5-INPUT` with `no accepted input type supplied`), `E-0038` (that block cleared by the runtime's own re-evaluation), `E-0062` (the `worker-loss` reclaim of phase 5 attempt 1) and the adjacent pair `E-0068` and `E-0070` recorded one second apart, which is the run-accounting defect this proposal records for the first time |
| `E-4` | `runs/run-34ca35504b72/state.json` | resolved; five state work items, all `completed` and `Completed`, none carrying a standing blocked reason; four gate work items, all `completed`; 43 recorded transitions, which is the append-only log the point-in-time rule replays this record against |
| `E-5` | `runs/run-34ca35504b72/completion-package.md` | resolved; aggregates the five-phase ledger, the four gate decisions with their recorded authorities, and the per-phase module provenance digests |
| `E-6` | `runs/run-34ca35504b72/states/refactor-implementation/artifacts/implementation-report.md` | resolved; the delivered change, with 1 change-set entry, 11 test-evidence entries, 2 recorded deviations, 5 residual risks and 4 open questions, status `provisional` and verification status `partially-verified` because two judgements were deliberately routed to the reviewing roles rather than settled by the implementer. Each of the five phases committed its contracted artifact — `technical-design.md`, two `validation-report.md`, this report and `orchestration-result.md` |
| `E-7` | `runs/run-34ca35504b72/states/refactor-implementation/validation-report.json` | resolved; a validation report exists for each of the five executed phases and every one records `pass` — 78/78, 31/31, 32/32, 31/31 and 34/34, with zero blocking and zero correctable failures in each |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-invariants-and-risk-profile` | `architect` | completed | Executed against the run over two attempts, both charged; 12 facts, 4 assumptions, 9 constraints, 8 impacted modules, 3 options compared, 3 decisions, 4 reuse rows, 4 plan steps, 4 risks and 2 open decisions; Validation Engine 78/78. Attempt 1 was rejected at `E-0015` on two blocking checks, `D3.6` and `D8.5`, classified `output-schema-failure` and retried; attempt 2 was accepted seven minutes later. The design selected the additive in-place extension as its option `O-001`, bound each new row to a named folder authority, and fixed the nine constraints every later phase was measured against | host-dispatched `architect` subagent v1.0.0, attempt 2 | `runs/run-34ca35504b72/states/scope-invariants-and-risk-profile/validation-report.json` |
| `safety-net-establishment` | `omn-qa` | completed | Executed against the run over two attempts, of which one was reclaimed rather than charged; 10 acceptance criteria derived from the design's constraints at 1 met and 9 blocked as structurally unmeasurable before the change, 2 defects at one medium and one low, verdict `pass-with-reservations`, validation basis `safety-net`; Validation Engine 31/31. This phase carried the run's stall: the adapter took a lease at 2026-08-27T13:10:29Z and never reported, leaving the run in an executing state with no artifact and no failure signal for over a week. The operator reclaimed the stale lease as `worker-loss` at `E-0030` on 2026-09-04T15:36:54Z and re-dispatched; because nothing had been produced, the loss was charged to `attempts_lost` and not to the retry budget, leaving the phase at 1 charged attempt of 3. The Phase Model declares no gate here, so none is recorded | host-dispatched `omn-qa` subagent v1.0.0, attempt 2 | `runs/run-34ca35504b72/states/safety-net-establishment/validation-report.json` |
| `refactor-implementation` | `omn-dev-1-implement` | completed | Executed against the run in one attempt once it could be dispatched at all; 1 change-set entry, 11 test-evidence entries, 2 deviations, 5 residual risks and 4 open questions; Validation Engine 32/32. Its history is the run's second unusual fact and is recorded rather than compressed: from 2026-09-04T16:06:22Z this phase stood blocked at guard `G5-INPUT` with the recorded reason `awaiting_dependency_output` and the detail `[request-validation-failure] no accepted input type supplied; accepted: ['technical-design', 'bug-analysis', 'test-baseline-record']`, event `E-0036`, failure class `dependency-failure`. The cause was a framework defect, not a run condition: the consuming agent's accepted menu was disjoint from the `validation-report` this workflow's second phase emits, so the `refactor` workflow could not pass phase 2 to phase 3 at all, and one of the three accepted identifiers was declared as an output by no agent anywhere. No run-level action could clear it. It was repaired under its own routed run, `run-79630cb5274d` — a `/bugfix` run closed 2026-09-06 with all four of its gates approved and recorded in `proposals/framework-change-proposal-FC-011.md` — after which the runtime's own guard re-evaluation cleared this block at `E-0038` on 2026-09-05T05:55:43Z and the phase dispatched for the first time on 2026-09-06T02:13:56Z. **This run could not have completed without that one; the dependency is load-bearing** | host-dispatched `omn-dev-1-implement` subagent v1.1.0, the version the repair produced | `runs/run-34ca35504b72/states/refactor-implementation/validation-report.json` |
| `behavioral-validation` | `omn-qa` | completed | Executed against the run in one attempt; 10 acceptance criteria at 10 met, 0 not met and 0 blocked, 5 defects all `low`, 3 open questions, verdict `pass`, validation basis `behavioral-parity`; Validation Engine 31/31. Every criterion was measured first-hand rather than transcribed, including all three pinned figures the Implementation Gate reviewer had been unable to reproduce, which is why the reproducibility finding against the upstream report was lowered to `low` on evidence rather than on assertion. This phase also corrected an earlier phase's count of unaccounted runs unprompted, and recorded the correction | host-dispatched `omn-qa` subagent v1.0.0 | `runs/run-34ca35504b72/states/behavioral-validation/validation-report.json` |
| `closure-and-debt-record` | `omn-orchestrator` | completed | Executed against the run over two attempts, of which one was reclaimed rather than charged; 5 phase-progression rows, 4 handoffs all accepted, 3 escalations at one high, one medium and one low with none critical and none high left open, 11 follow-up actions each owned, 4 open questions, coordination basis `debt-closure`, disposition `closed-with-followups`; Validation Engine 34/34. Attempt 1 was lost at `E-0062` to a network error before any work was performed — no artifact, no result envelope, an empty artifacts directory — and was released as `worker-loss` and charged to `attempts_lost`. The record held its own row at `blocked` rather than anticipatorily `complete`, because its Closure Gate was undecided when it was written; that gate was decided 9m 8s later, which is why this proposal reports the phase `completed` and the closure record reports it `blocked`. Both are accurate at their own instant, as the profile's point-in-time evidence rule requires | host-dispatched `omn-orchestrator` subagent v1.0.0, attempt 2 | `runs/run-34ca35504b72/states/closure-and-debt-record/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact and none stands blocked, so the
Completion Rule's `C-3` is satisfied on its executed limb throughout and its operator-performed limb
is never reached. All five were performed by host-dispatched subagents under their contracted
validators. Three operator interventions are recorded above rather than absorbed: the reclamation of
the stalled lease on phase 2, the release of the lost attempt on phase 5, and the recording of each
gate decision on behalf of the deciding subagent. A fourth is recorded under Open Items rather than
here, because it shaped a verdict rather than a dispatch: the operator supplied the working
interpretation of the design's constraint `C-007` that the validating phase applied to its eighth
criterion, and that phase recorded it on the operator's authority rather than deciding it.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Invariant Gate | approve | omn-tech-lead | framework-runtime auto-on-clean-evidence, recorded by session operator, 2026-08-27T13:10:13Z | The design validated 78 of 78 by its registered validator; the change is additive documentation confined to one section of one document, and invariants `INV-1` to `INV-4` carry no contract, registry, routing or runtime surface. `architect` produced the evidence and is excluded from deciding, so the accepting owner is the gate's other assigned owner. This decision is also the subject of an open item below: the design assigned the register-and-granularity confirmation to this gate, and this gate decided on 2026-08-27, ten days before the row text it was supposed to confirm existed |
| Implementation Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-06T02:50:24Z | Correctness re-derived independently at review rather than accepted from the report: the section now describes all sixteen payload-root directories and nothing that does not exist, the diff is confined to seven insertions in a single hunk inside the section, the twelve pre-existing rows are unchanged in content and relative order, and the post-change digest `59a93ad68e3ddacb8e4e157c2545d676` over 3215 bytes reproduces exactly. Behaviour preservation was verified rather than asserted: the memory-optimisation runtime module confirmed the only module naming the document and confirmed not to parse it, no bundled-payload mirror, and all seven verifiers and all three targeted test modules reproducing their baseline verdicts under independent execution. Three non-blocking findings stood, one medium on evidence reproducibility and two low. This gate also carried the register-and-granularity judgement the design had assigned to the Invariant Gate. `omn-dev-1-implement` produced the evidence and is excluded from deciding |
| Regression Gate | approve | omn-dev-2-reviewer | omn-dev-2-reviewer subagent, recorded by session operator, 2026-09-06T03:26:48Z | Behavioural parity established deductively rather than statistically, which the reviewer accepted as the stronger argument available in a non-quiescent tree: out-of-section content identical at both revisions under either terminator convention, 1903 bytes and digest `415bac853e64fc049cad7a60164181e5` under one and 1864 bytes and digest `b8c485295831d9aaa445899a5d2f1fb1` under the other; the twelve pre-existing rows reproducing their pinned order digest exactly; and the document resolved by no registry record, parsed by no validator, consumed by no workflow phase, absent from the installer payload, and named by exactly one module that never parses its structure — so the set of behaviours the edit could alter is empty. All three figures the previous gate's reviewer could not reproduce were reproduced first-hand here, and the granularity judgement was independently re-confirmed against the registry, domain-model and runtime record sets, no added row reproducing any index filename, specification filename, module filename or any of the fifty-seven registry record identifiers. `pass` is the only verdict the producing agent's own adjudication table admits with zero critical or high defects and nothing blocked or not-met. Five open low defects and three open questions carried to closure as conditions. `omn-qa` produced the evidence and is excluded from deciding; the co-owner decided |
| Closure Gate | approve | omn-documentation | omn-documentation subagent, recorded by session operator, 2026-09-06T07:04:10Z | The closure record reconciles exactly with the run ledger, the recovery ledger and the event log on phase progression, gate attribution and escalation history; it correctly records its own phase as `blocked` on the undecided Closure Gate, deliberately deviating from a contradicting conforming row in its own producing agent's examples module, which check `O5` of that agent's output module governs over; and `closed-with-followups` is the right disposition, since no critical or high escalation stands open, the one blocked phase bars a bare `closed`, and holding a run on its own undecided gate would be circular. Approved with two reservations, both of which are carried into this proposal as open items because no other durable record holds them: the upstream open question on the unexecutable mitigation of design risk `R-001` was answered in the closure record rather than carried to `omn-tech-lead` who owns it, and the runtime's own run-completion event asserting that every gate was decided contradicts the record and is the defect, not the record. `omn-orchestrator` produced the evidence and is excluded from deciding |

Every gate the `refactor` Phase Model declares was decided, each by an owner the gate matrix assigns
and none by the role that produced the evidence assessed. None was waived. Three of the four are
recorded as human decisions; the Invariant Gate is recorded as an auto-approval on clean evidence,
attributed to `omn-tech-lead` as accepting owner and recorded by the operator session, and that
distinction matters to the open item about its timing rather than to its validity.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | inspection | pass; 6/6 checks, 37 of 37 phases resolving the full capability and context chain, 0 blocked, 11 of 11 active commands resolving, 12 of 12 phase owners host-invocable, 105 of 105 phase skill references resolving, 29 of 29 gate references carrying a non-producing owner. Executed from the repository root at the authoring instant, not merely inspected — the note below the table gives the reason the Command column reads this way |
| Validator coverage and decisiveness | inspection | pass; 6/6 COVERED at the authoring instant, first execution, no re-run needed |
| Committed evidence still verifies | inspection | pass; 10/10 PROVEN on `run-c5a8d50d3238`, the run the release checklist names, so no previously committed proof was invalidated by this change |
| Manifest conformance | inspection | pass; 2/2 CONFORMS at the authoring instant. The run recorded this script as carrying no independent pre-change baseline, so this execution is a post-change reading only and is recorded as such rather than as parity evidence |
| Self-hosting governance | inspection | 7/8 at the authoring instant, unchanged from the value the run measured at three separate phases. `S1` to `S7` pass: the profile parses, all seven routing rows resolve, the change-proposal contract is registered, all eleven recorded proposals re-validate at 38/38 each under `S6`, and `S7` confirms the Completion Rule for each of their runs. `S8` fails, naming two unaccounted runs — this run and `run-4c51600606df` — of which this proposal removes the first on the next execution. The second is a concurrent session's in-flight run and is carried as `O-020` |
| Scope classification recomputes | inspection | pass; the profile's classifier was run at the authoring instant on each of the six paths in the Scope Classification table, and every row records exactly what it returned. The changed document was additionally classified with its directory prefix, where the classifier returns in-scope under `SR-1`, which is the substantive reading recorded under that table |
| Routing resolves | inspection | pass; the profile's routing resolver for the intent `structure-preserving-change` resolves to `/refactor` over `refactor` v1.0.0 at `scope-invariants-and-risk-profile` of 5 with required inputs `change-request`, `business-intent` and `architecture-context`, agreeing with `E-1` on all four |
| Governance-prose and payload-parity contracts | `python -m unittest tests.test_content_contracts tests.test_bundled_payload` | pass; 24 tests run, 24 passed, at the authoring instant — the same figure the run recorded at 13 and 11. The payload module is the one that would fail if the changed document had a bundled mirror left unsynced, and it does not, which is the executed form of the absence recorded in the Scope Classification table |
| The sole code reference to the document | `python -m unittest tests.test_optimize_memory` | pass; 31 tests run, 31 passed, matching the run's figure. This is the module that carries the document in its prose-compression target list, and it is the only code in the framework that names the document at all; it holds it as a target and never parses its structure, which is the fact the whole behavioural-parity argument turns on |
| The delivered change holds in the live tree | inspection | pass; read-only inspection at the authoring instant confirms the payload root holds sixteen directories and the document's `## Folder Descriptions` section carries sixteen rows, one per directory, with the four added keys present and no row naming a directory that does not exist. The change is still in place and still correct nine days after the design froze the count |
| Recovery behaviour | inspection | not re-executed at authoring, deliberately: the probe creates and removes injected run directories under `runs/**`, and this role holds no write authority there. Measured during the run at 41/41 RECOVERY PROVEN, at baseline parity, executed twice for the flake the run documents. The run also verified that the script's net effect on the run directory was zero by comparing the listing digest before and after |
| Multi-phase state machine | inspection | not re-executed at authoring, for the same reason: the probe appends replay bookkeeping to a committed run's tracked state file, and modifying committed run evidence is prohibited to this role. Measured during the run at 14 of 15 NOT PROVEN, failing only `M6`, whose failure text reads `planning=absent, design=absent, delivery=absent` — a property of this workflow's own phase names that no documentation edit could affect, and a standing condition this change did not introduce and cannot move |
| Whole discovered unit suite | inspection | not re-executed at authoring, deliberately: one of its modules rewrites two generated documents under `docs/` in place, a repository write outside this authoring session's permitted writes. The run recorded the same exclusion for the same reason. The verdict rests on 55 targeted tests across the three modules that reach the document's neighbourhood, all passing at the authoring instant, plus the four verifier executions above |
| This proposal against its registered validator | inspection | pass; 38 checks run, 38 passed, 0 blocking and 0 correctable failures, with the two not-machine-checkable obligations recorded. Re-run by `S6` of the self-hosting verifier on every later execution |

One note on the Command column, because it reads oddly and the cause is not a weakness in the checks.
This proposal cites every repository path without its leading directory prefix, so a command naming a
framework script cannot be written here in a form that resolves from the repository root, which is
what check `F10` requires of any command cell that is not `inspection`. Every row marked `inspection`
that says it was executed was executed, from the repository root, at the authoring instant; the word
records a citation constraint, not a weaker class of evidence. The three rows that genuinely were not
executed say so in their own words and give the reason. The two rows carrying a real command are the
two whose commands contain no script path.

A second note, on what none of this establishes. The working tree was not quiescent at any point in
this run and is not quiescent now: a concurrent session delivered into the same repository throughout,
and the changed-path count moved 56 to 58 to 60 to 62 across the run's phases and reads 63 at the
authoring instant, every increment disjoint from this change's three files. **No whole-repository
measurement taken over this window is attributable to this change**, which is precisely why the
parity verdict rests on a deductive isolation argument and why the verifier readings above are
recorded as summary-line parity rather than as proof of causation.

## Risk and Rollback

- Blast radius: one file, one section, seven inserted lines, and no more. Three files carry the whole
  footprint — the orientation document itself, plus the implementation report and result envelope the
  delivering invocation wrote under its own run directory, which the invocation declared as its
  complete side-effect set. No contract, registry record, routing row, gate surface, template,
  workflow specification, runtime module, validator or continuous-integration configuration changed,
  and no bundled payload required syncing because the document is absent from the installer's
  267-file payload map. The one behaviour a reader might expect to move did not: no check in either
  verification surface the repository's continuous-integration workflow discovers reads the document
  at all.
- Risk assessment: the load-bearing claim is behavioural parity, and it is established deductively
  rather than statistically because the tree was shared throughout and a statistical argument was
  therefore unavailable. The deduction is sound in the direction it runs — the document is resolved
  by no registry record, parsed by no validator, consumed by no workflow phase, absent from the
  installer payload, and named by exactly one module that holds it as a compression target without
  parsing it, so the set of behaviours the edit could alter is empty — and its weakest link is that
  the single naming module is also a live mechanism that can rewrite this file's prose. That is the
  one unmitigated risk with a mechanism behind it, and it is carried forward rather than closed with
  the run, as `O-003` and `O-014`. Five defects stand open, all rated `low` by the validating role and
  none reclassified here: two are evidence-quality findings against upstream reports rather than
  against the delivered change, one is a row-length measurement against a constraint its own source
  marks negotiable, one is a benign line-terminator rewrite, and one is an inaccuracy the design's own
  assumption introduced upstream of the implementation and which stands in production instruction
  today. The accepted risk the design recorded and `omn-tech-lead` carried forward at the Invariant
  Gate is that completeness is now enforced at review time only: the additive manual edit gives no
  mechanical guarantee the inventory stays complete as directories are added later, and nothing in
  the repository would notice if it drifted again. Three qualifications on the evidence are stated
  rather than buried. The safety net covers five of the seven verification scripts the repository
  discovers and two of the three targeted test modules — it is not a full baseline and must not be
  described as one. The claim that out-of-section content is byte-identical holds line-normalised
  only: the working file carried CRLF terminators before the edit at 2794 bytes and LF after it at
  3215 bytes, so all fifty-six pre-existing lines had their terminators rewritten, though the
  version-control instrument reports seven insertions and zero deletions, the committed blob is
  identical outside the section, and CRLF is restored on the next operation that touches the file.
  And two verifier conditions stand that this change neither caused nor can move: the multi-phase
  proof at 14 of 15 on `M6`, and the self-hosting verifier at 7 of 8 on `S8`.
- Rollback procedure: revert the four inserted rows. That restores an inventory describing twelve of
  sixteen payload-root directories and silently omitting the domain-specification, prompt-pattern,
  discovery-index and executable-runtime directories, which is the governance debt the run was
  chartered to remove. No condition currently argues for it. The one finding that could is the
  `prompts/` row stating contents its folder does not hold, and the correct response to that is the
  fix routed under `O-008` — populate the folder, or correct the row and its named authority together
  — never a revert, which would trade one inaccurate row for four absent ones. Reverting invalidates
  no committed run evidence: this run's record remains a valid account of a delivered-then-reverted
  change and this proposal remains its governance record. It would, however, reopen a question the
  run answered, because the document is injected into every contributor session, so a revert changes
  what every later contributor is told about the framework and is a decision for the document's owner
  rather than a mechanical undo.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6 at the authoring instant; 37 of 37 phases dispatchable, 0 blocked, every phase owner host-invocable, every gate reference carrying a non-producing owner |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED at the authoring instant, first execution; every artifact type a Phase Model names has a registered validator that accepts a conforming artifact and rejects a mutated one |
| `FR-03` | Recovery behaviour | accepted | 41/41 RECOVERY PROVEN, at baseline parity, measured twice during the run and reproduced at the Implementation and Regression Gates. Not re-executed at authoring because the probe creates and removes injected run directories under `runs/**`, which this role may not write. Recorded `accepted` rather than `pass` so the reading is not mistaken for one taken at this instant |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` at 10/10 PROVEN, executed at the authoring instant against the run the checklist names; no committed proof was invalidated |
| `FR-05` | Self-hosting governance resolves | pass | The profile parses, all seven routing rows resolve, the change-proposal contract is registered, all eleven recorded proposals re-validate at 38/38, and every one of their runs satisfies the Completion Rule — `S1` to `S7`. The remaining `S8` row is a residual this change did not cause and does not close, carried as `O-020` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-34ca35504b72` is a `/refactor` run over `refactor` v1.0.0, submitted with the three input types the profile's routing row requires; this proposal links its artifacts as `E-1` to `E-7` |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0, the value `E-1` and `E-2` both record. No runtime module was touched; the change is four rows in one documentation section, and no agent, contract or registry version moved either. The one version that did move in this run's neighbourhood belongs to a different change: `omn-dev-1-implement` was dispatched here at v1.1.0, the version the separately routed repair produced |
| `FR-08` | Documentation matches delivered behaviour | accepted | The delivered change *is* the documentation impact, and the surface it corrected now matches the filesystem exactly at sixteen of sixteen, re-derived at the authoring instant. Recorded `accepted` and not `pass` for two reasons that must not read clean. First, this item names the folder descriptions in `README.md`, and the payload-root `README.md` carries its own `## Folder Descriptions` section still listing exactly the twelve pre-change rows — so the run corrected one of two sibling inventories and left the one this checklist item names untouched. No phase of the run and no gate considered that file; it is recorded here for the first time as `O-018`. Second, the `prompts/` row is inaccurate against its own folder today, carried as `O-008` |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every claim was executed or directly read: diff confinement proven twice by independent methods, additivity proven by a reproducing row-order digest, completeness proven by a two-way difference against the filesystem, path resolution measured at 18 to 22 tokens all resolving, seven verifiers and three test modules executed post-change, and the sole code reference inspected and confirmed not to parse the document. The four real gaps are recorded rather than omitted — the five-of-seven safety-net coverage, the two verifiers and one test module with no independent pre-change baseline, the line-normalised qualification on the byte-identity claim, and the non-quiescent tree that makes every whole-repository measurement over this window unattributable |
| `FR-10` | Rollback stated | pass | Risk and Rollback above: a four-row revert, what it would restore, the one finding that might argue for it, why that finding routes to a fix rather than to a revert, and whose decision it is given that the document reaches every contributor session |
| `FR-11` | Multi-phase state machine still proves out | accepted | 14 of 15 during the run, failing only `M6`, whose failure text reads `planning=absent, design=absent, delivery=absent` and is therefore a property of the `refactor` workflow's own phase names that no documentation edit can affect. The run recorded no independent pre-change baseline for this script, so its parity is confirmed from the post-change side only. Not re-executed at authoring because the probe appends to a committed run's tracked state file, which this role may not modify |
| `FR-12` | Release note where consumer-visible behaviour changed | accepted | Nothing a framework consumer depends on behaviourally changed, which is the whole claim of a structure-preserving change, so no release note is owed on the behavioural limb. What did change is what every contributor session is told about the framework's own layout, and the `refactor` workflow has no publication phase at all, so a change to the one document injected into every contributor session reaches no contributor through any phase this run could execute. That structural gap is carried as `O-016`, and it is why this item reads `accepted` rather than `not-applicable` |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The runtime's completion accounting contradicts its own validator, and it does so silently. Event `E-0068` recorded the Closure Gate blocked and awaiting a human decision at 2026-09-06T06:55:02Z; event `E-0070` recorded `every workflow phase completed and every gate was decided` one second later at 06:55:03Z. Over the same interval `run-ledger.json` recorded `status: Completed` with `blocked: 0` and `completed: 5`, while the Closure Gate record in that same file held `null` in its decision, owner role, decider, rationale, evidence reference and timestamp fields. The closure record's own accounting — four complete, one blocked — was the accurate one, and the machine record disagreed with it for nine minutes until the gate was actually decided. This is not a cosmetic mislabel: the state engine and the output aggregator will mark every gate-owning terminal phase complete before its gate is decided, in every workflow, so any reader trusting the ledger over the artifact reads an approval that has not happened. It is the same class of failure the coordinating role's own check `O5` exists to prevent in artifacts, unguarded in the runtime that writes the ledger | `omn-orchestrator` | Open, and recorded here for the first time. The Closure Gate reviewer raised it as an approval reservation and named the runtime as the defect and the record as correct; no durable record carried it until this one. Rated as the most consequential item in this table, because it degrades the evidence every later gate reads |
| `O-002` | The design assigned confirmation of the added rows' register and granularity to the Invariant Gate, as the mitigation of its risk `R-001`. That gate decided at 2026-08-27T13:10:13Z. The row text it was to confirm did not exist until 2026-09-06, so the mitigation was unexecutable as written from the moment it was written. It was discharged instead at the Implementation Gate and independently re-confirmed at the Regression Gate, so the judgement was made twice by a competent non-producing owner and nothing was skipped — but it was made somewhere other than where the design said, and the phase that noticed raised it as an open question which the closure record answered rather than routing to the risk's owner. The durable finding is the pattern, not this instance: **any refactor whose Invariant Gate precedes the existence of the text that gate is meant to confirm has this problem**, and the `refactor` Phase Model places that gate first by construction, so the pattern is structural rather than accidental | `omn-tech-lead` | Open, and routed here rather than answered. `omn-tech-lead` owns the risk and owns the gate; the closure record answered on its own authority and the Closure Gate reviewer recorded that as a reservation. The instance is discharged; the pattern is not |
| `O-003` | The changed document sits in the prose-compression target list of `runtime/optimize_memory.py` and is covered by neither of that module's deny lists, so a compression pass can rewrite the prose of the inventory this change just completed. This is the one unmitigated risk with a live mechanism behind it. Whenever the memory-optimisation command is run with the document in scope, re-derive the row set and the directory count immediately afterwards and confirm the inventory survived the rewrite. Carried from the closure record's second follow-up action | `omn-qa` | Open, deliberately not closed with the run, because the command that rewrites this file outlives the run. The durable structural question — whether the document should be a compression target at all — is separate and is `O-014` |
| `O-004` | The design's constraint `C-007` is defective in its wording and in its arithmetic, and both halves must be answered together. It requires the verification scripts to keep their current verdicts and separately that no metric regresses; discharging governance debt improves a verdict, which satisfies the second clause and violates a literal reading of the first. It was moot on the run's own measurement because nothing moved — and this proposal is exactly what makes it non-moot, since landing it moves the self-hosting verifier's `S8` detail from two unaccounted runs to one. The same constraint names five verification scripts where the repository discovers seven. Carried from the closure record's third follow-up action and its second open question | `architect` | Open. The operator supplied a working interpretation for the run — that an improvement is not a regression — which the validating phase applied and recorded on the operator's authority rather than deciding; this proposal carries it the same way. Both baselines are recorded at summary-line and check-count granularity, so either answer stays decidable without re-measurement |
| `O-005` | Author the change proposal that gives this run its governance record. Until it exists, check `S8` of the self-hosting verifier keeps naming this run unaccounted. Carried from the closure record's fourth follow-up action | the run's operator | Resolved by this proposal. The closure record also warned that this proposal alone will not flip `S8` to passing, and that warning stands: see `O-020` |
| `O-006` | The debt this run was chartered to remove is removed. The folder inventory went from twelve of sixteen payload-root directories to sixteen of sixteen, the undocumented set is empty, the reverse difference is empty so no row names a directory that does not exist, and the cited path tokens went from 18 to 22 with all resolving. Re-confirmed by read-only inspection at the authoring instant, nine days after the design froze the count. Carried from the closure record's fifth follow-up action | `architect` | Resolved. Recorded rather than dropped, because a debt delta a closure claims and no later record confirms is indistinguishable from one that was never measured |
| `O-007` | The debt the chosen approach leaves standing. Completeness of the inventory is now enforced at review time only: an additive manual edit gives no mechanical guarantee the inventory stays complete as directories are added later, and no check in either verification surface the repository's continuous-integration workflow discovers reads the document at all. Carried from the closure record's sixth follow-up action | `architect` | Accepted risk, accepted by `architect` in the design's selected-approach section against its risk `R-004` and carried forward by `omn-tech-lead` as the Invariant Gate accepting owner. Recorded here, not accepted here |
| `O-008` | The `prompts/` row is wrong in production instruction today. It states that the folder holds curated, versioned prompt patterns used by the framework's agents; the folder holds one file, its README, and zero prompt-pattern files. The row is faithful to `prompts/README.md`, the authority the design's step `P-001` bound it to, and is not faithful to the filesystem, so the defective element is the design's own assumption rather than the implementation. Low severity is correct on impact, but the document is injected into every contributor session as authoritative instruction, so it should not sit indefinitely. **The fix is to populate the folder or to correct the README and the row together; correcting the row alone would put it out of agreement with its named authority and is not the implementing role's to direct.** Carried from the closure record's seventh follow-up action and its first open question | `architect` | Open. The choice — which of the two is corrected — is the assumption owner's, and it is the one item in this table that a reader of the delivered change would encounter as a false statement rather than as a process gap |
| `O-009` | The safety net this run established is not a full baseline and must not be described as one. It covers five of the seven verification scripts the repository discovers and two of the three targeted test modules: `runtime/verify_manifests.py` and `runtime/verify_multi_phase.py` carry no independent pre-change measurement, and the memory-optimisation test module was executed post-change only, so parity for those three rests on the implementer's own before-and-after figures, reproduced post-change by two independent parties but never observed pre-change by any. The gap traces to the design's constraint `C-007`, which itself says five. Carried from the closure record's eighth follow-up action | `omn-qa` | Open, rated low. Recorded so that the phrase "baseline parity" in this proposal's Verification table is read at the coverage it actually has |
| `O-010` | The implementation report describes its inline probes rather than stating them, and asserts that any later run can re-execute the completeness probe. Three of its five pinned figures — the out-of-section digest, the row-order digest and the pre-change path-token count — each depend on a convention the report does not record, so an independent reader following the description does not reproduce them. The validating phase recovered the conventions, restated them, and reproduced all five figures exactly, so the values are sound and the omission is of the method rather than of the values. Committed run evidence is immutable and the report has not been, and must not be, amended. Carried from the closure record's ninth follow-up action | `omn-dev-1-implement` | Resolved by downstream record only. The correction lives in the validating phase's report, in the closure record and here; the implementation report will keep describing rather than stating wherever it is read, which is the price of immutability and is recorded rather than repaired |
| `O-011` | The `runtime/` row runs 155 characters against a longest pre-existing row of 135 and a pre-existing range of 46 to 135, so it exceeds the longest existing row by fifteen percent. On the wrapped-physical-line measure the added rows sit inside the existing pattern, occupying at most two lines as two pre-existing rows already do. Carried from the closure record's tenth follow-up action | `architect` | Accepted risk. The constraint it is measured against is marked Negotiable by its own source, the design delegated the row text to implementation, and the register judgement was routed to `omn-dev-2-reviewer` and approved at the Implementation Gate by an owner that did not produce it |
| `O-012` | The claim that content outside the changed section is byte-identical to its pre-change content holds line-normalised only. The working file carried CRLF terminators before the edit at 2794 bytes and carries LF after it at 3215 bytes, so all fifty-six pre-existing lines had their terminators rewritten; the out-of-section content is identical at 1903 bytes and digest `415bac853e64fc049cad7a60164181e5` under CRLF and at 1864 bytes and digest `b8c485295831d9aaa445899a5d2f1fb1` under LF. Over the same two revisions the version-control instrument reports seven insertions and zero deletions, the committed blob is identical outside the section, and the repository restores CRLF on its next operation touching the file. Carried from the closure record's eleventh follow-up action | `omn-dev-1-implement` | Accepted risk, benign in substance. Recorded so that no later reader repeats the unqualified claim, and because it is the same terminator difference that defeated the reproduction attempt recorded under `O-010` |
| `O-013` | Two accounts of the artifact validator's check-category movement over the implementation report stand unreconciled, and both are recorded rather than merged. The validating phase attributed the movement it observed to a concurrent session's modification of `templates/implementation-report.md`. Inspection at the closure phase found a simpler mechanism: the digest cross-check is Advisory and not-machine-checkable when no invocation envelope is supplied and Blocking when one is, so the same artifact validates at 30 of 30 with four not-machine-checkable without an envelope and at 31 of 31 with three with one. Both readings are `pass`, the totals are unchanged and no verdict moves either way, so the count is invocation-dependent rather than drift. Carried from the closure record's third open question | `omn-qa` | Open, and raised as a question against the validation record rather than corrected in it, because reinterpreting a validation belongs to the role that produced it |
| `O-014` | Should the orientation document remain in the prose-compression target list at all, now that it carries a completed sixteen-of-sixteen inventory a compression pass could rewrite? The monitoring obligation at `O-003` mitigates the exposure without removing the mechanism. Carried from the closure record's fourth open question | `architect` | Open. The structural position is the architect's; the coordinating role records the exposure and routes the decision rather than proposing the remedy |
| `O-015` | `agents/omn-orchestrator/examples.md` carries a defective conforming row. In its closure-basis example table, the row for the coordinating phase carries a real gate, a gate decision of `none`, and a progression of `complete` — precisely the shape check `O5` of that agent's own output module rejects, and precisely what the same module's own non-conforming section forbids when it states that a gate-owning phase is never marked complete anticipatorily. The producing agent of this run's closure record found the contradiction, followed the rule rather than the example, and recorded its own row as `blocked`; the Closure Gate approved that deviation explicitly. The same finding was recorded once before, by the proposal for the repair run this run depended on, and it is recorded again here because it remains uncorrected and because a second independent encounter with it is itself evidence that the example misleads | `architect` | Open, rated low. The module set is ordered so that the output contract governs over the example and the example is explicitly illustration, so no artifact is at risk. The repair is a framework-internal change needing its own routed run |
| `O-016` | The `refactor` workflow has no publication phase. Its Phase Model runs scope, safety net, implementation, validation, closure — and stops. A refactor that changes what every contributor session is told about the framework therefore reaches no contributor through any phase the workflow can execute, because the workflow has no phase that publishes anything to anyone. The `fix-bug` workflow has the adjacent version of this gap, recorded as an open item by the proposal for the repair run this run depended on; this is the same shortfall one workflow further along, and the two together suggest it is a Phase Model omission rather than a per-workflow oversight | `architect` | Open, and it is why `FR-12` above reads `accepted`. Whether the answer is a publication phase, a phase-scoped documentation command reachable inside the run, or an explicit decision that refactors publish nothing, it is a structural call this run could not take |
| `O-017` | The release checklist's documentation item names `runtime/README.md` and the folder descriptions in `README.md` as the surfaces documentation must match. It does not name the orientation document at the framework payload root, so a change to the one document injected into every contributor session is not reached by any surface this mandatory item enumerates. The item was satisfied for this change by reading it purposively rather than literally, which is recorded under `FR-08` rather than hidden | `omn-documentation` | Open, rated low. Either the item's surface list gains the document, or the item is rewritten to name the class of surface rather than three instances of it |
| `O-018` | The payload-root `README.md` carries its own `## Folder Descriptions` section listing exactly the twelve pre-change rows, still omitting `domain-model/`, `prompts/`, `registry/` and `runtime/`. The run corrected one of two sibling inventories at the payload root and left the other at twelve of sixteen — and the one left behind is the one the release checklist's documentation item actually names. No phase of this run, no gate, and no supplied input mentions this file; the design's scope, the implementation's change set and both validation reports are silent on it. It is not a defect in the delivered change, whose scope was correctly confined to what it was routed to do; it is a second instance of the same debt, discovered while writing this record | `omn-documentation` | Open, and recorded here for the first time. It needs a routed change of its own, and it should be routed together with `O-017`, since the checklist item and the file it names are two halves of one gap |
| `O-019` | Recovery-ledger entries are closed by a runtime or operator action the producing role has no authority to perform, which the closure record recorded as a live escalation: its own attempt-1 failure envelope stood `open` when the record was written. At the authoring instant all eleven envelopes read `resolved` and the run's recovery block records 11 classifications, 11 resolved, 0 open. The escalation is discharged, and it is recorded here rather than dropped because the closure record states the opposite and a reader reconciling the two needs to know which instant each describes | the run's operator | Resolved, as informational drift under the point-in-time evidence rule. The closure record was accurate when written and is not amended |
| `O-020` | One framework run remains unaccounted by any change proposal and will keep `S8` of the self-hosting verifier failing after this proposal lands: `run-4c51600606df`, submitted 2026-09-05T04:23:54Z by a concurrent session and still in flight. This proposal accounts for `run-34ca35504b72` alone; fabricating a proposal for a run it did not carry would falsify the record, and a run mid-workflow cannot satisfy the Completion Rule in any case, so its accounting waits on its own closure rather than on an author. Descended through the two preceding proposals, which recorded four unaccounted runs, then three, then two | `omn-orchestrator` | Open, pre-existing and shrinking: two before this proposal, one after it. `S8` is expected to name exactly one run on its next execution, and a reader seeing it name more should look for a newer concurrent run rather than for a gap in this record |
| `O-021` | Two citation-form hazards in the framework's own tooling and conventions, each of which changes what a correct tool run tells a reader. The scope classifier decides a path by a glob keyed on the framework directory prefix, so the same file classifies in-scope or unmatched depending on whether the citation carries that prefix, which is why every row of the Scope Classification table above reads out-of-scope and needs a paragraph to explain it; that half was first recorded by the preceding proposal. The second half is new and is specific to this change: the file this run modified cannot be named in this record at all, in either citation form, because its filename carries a token the model-independence rule forbids, so the central subject of a governance record is identifiable only by description and by content digest. Every artifact of this run adopted the same workaround independently, which is what makes it a convention rather than an evasion — but a governance record that cannot name the file it governs is a gap in the conventions, not a stylistic quirk | `architect` | Open. Neither hazard is caused by this change. The first is the reason the Scope Classification table needs a note; the second is the reason this proposal's title, tables and prose all describe rather than name |
| `O-022` | The working tree is shared with a concurrent delivery session, and was throughout this run. The changed-path count moved 56 to 58 to 60 to 62 across the run's phases and reads 63 at the authoring instant, every increment disjoint from this change's three files. Every whole-repository measurement taken over this window is therefore unattributable, which is why this run's parity verdict rests on deduction and why the closure record's own verifier readings were recorded as summary-line parity rather than as causation. The standing hazard is that a later reader treats any of those figures as isolation evidence | `omn-qa` | Open, and not a defect in anything this run produced. Recorded because it is the qualification that must travel with every number in this proposal, and because the next framework run in this repository will face the same condition |
| `O-023` | The coordinating role is the contracted producer of this artifact type, yet its manifest permits no repository write in any phase and its charter states that it writes its own artifact and its result envelope and nothing else. This instance was authored under an explicit operator authorisation scoped to exactly this one file. The standing contradiction has been tracked across several proposals and is unchanged | `omn-tech-lead` | Open, unchanged. Resolve by either narrowing the producer list or widening the manifest's write scope for this artifact alone |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorised
  by the session operator for this single file, discharging the fourth follow-up action of the run's
  closure record
- Accepted by: omn-tech-lead at the Invariant Gate, omn-dev-2-reviewer at the Implementation and
  Regression Gates, and omn-documentation at the Closure Gate — each an owner the gate matrix
  assigns, and none the role that produced the evidence it assessed
- Acceptance basis: all five phases of the routed workflow executed with artifacts their registered
  validators accepted at 78/78, 31/31, 32/32, 31/31 and 34/34; every gate the Phase Model declares
  decided by a non-producing owner with its rationale and evidence reference recorded; one charged
  retry and two reclaimed attempts recorded with what each cost and why neither loss was charged to a
  retry budget; a week-long stall and a day-long guard block recorded as the run's history rather
  than compressed out of it, including the load-bearing dependency on the separately routed repair
  without which this run could not have completed; three operator interventions and one operator-
  supplied constraint interpretation disclosed with what each cost the evidence; the behavioural-
  parity verdict carried as recorded at `pass` with five open low defects and no severity
  reclassified; and twenty-three open items carried forward with owners, including two findings the
  Closure Gate reviewer raised that no durable record held, one second instance of the same debt
  discovered while writing this record, and the run-accounting residual this proposal does not close
