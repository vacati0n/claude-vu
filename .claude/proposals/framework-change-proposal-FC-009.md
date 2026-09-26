# Framework Change Proposal: Ship the Framework Payload Inside the Distributed Package, with a Bundled-Payload Resolution Fallback

```yaml
frameworkChangeProposal:
  proposalId: FC-009
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-e0dba6763475
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-009
- Change title: Carry the framework payload as package data inside the distributed package, and append a bundled-payload candidate to source resolution as a strict last resort
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-e0dba6763475
- Authored on: 2026-09-04

## Authoring Baseline

- Authored at: 2026-09-04T15:44:10Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

This is a **retrospective record**. The run it documents closed at its Closure Gate on
2026-09-04T04:58:35Z; this proposal was authored roughly eleven hours later, by an
`omn-orchestrator` instance that took no part in the run and decided none of its gates, under an
operator authorization scoped to this one file. No run artifact was produced, amended, or consulted
for the first time by that authoring: every claim below is read back out of evidence the runtime
wrote between 2026-09-03T11:34:17Z and 2026-09-04T04:58:35Z. The record exists because the run had
none, not because the run needed one to close. Open item `O-001` records that plainly.

## Change Statement

- Objective: make a non-editable install of the distributed package self-contained. Before this
  change a fresh-environment user who installed the built wheel got a command-line tool that could
  install nothing: the framework payload was not carried by the built distribution, and source
  resolution probed only an explicit `--source` path and a payload tree adjacent to a source
  checkout — a candidate that exists for an editable install of the source repository and not for a
  wheel installed into site-packages. Every such user had to supply a path to a checkout they might
  not have. Ticket CKA-02 of the adoption backlog under `docs/` (Epic A, Days 0–30), carrying
  recommendation R1 of the adoption review dated 2026-08-27; it blocks ticket CKA-03.
- In scope: the three deliverables the ticket names, delivered as change-set entries `C-001` to
  `C-005` of implementation report IR-2026-0004 — a bundled payload data subtree at
  `omn_agent/_bundled_payload/` holding 267 files that mirror the framework payload directory at the
  repository root (every managed directory plus both seed directories, filtered by the installer's
  own exclusion-pattern constant); a package-data declaration in `pyproject.toml` using two
  recursive glob patterns, the second required because the build backend's glob resolution never
  matches dot-named entries and the payload carries them; exactly one new last-resort candidate
  appended to `find_source` in `omn_agent/source.py`, taken only in the no-explicit-source branch,
  plus one public constant naming the bundle directory; a new regression module
  `tests/test_bundled_payload.py` (11 tests) that pins mirror parity by file set and per-file
  content digest, framework-tree validity, exclusion-filter cleanliness, packaging-glob coverage,
  three-environment precedence, invalid-explicit non-fallback and retained failure guidance, and
  doubles as the mirror's one-line sync tool; and two added command-line tests in
  `tests/test_omn_agent.py`. The third ticket deliverable, regenerating the stale distribution
  metadata, was deferred inside the run under deviation `V-001` and executed outside it — see
  `O-005`.
- Out of scope: the three exclusions scope definition SCOPE-2026-0001 bounds the change with —
  `X-001`, any alteration to gate-decision recording, gate-matrix semantics, producer exclusion,
  approval-requirement enforcement or any human-block path; `X-002`, the dependent
  continuous-integration gating ticket CKA-03; `X-003`, any change to source-resolution precedence
  for existing users. Also out: user documentation, which the accepted design sequences after
  verified behaviour at `P-009` and which the run deliberately did not perform, leaving known issue
  `K-008` open.
- Acceptance basis: six measurable acceptance criteria, `A-001` to `A-006` in SCOPE-2026-0001, of
  which `A-001` and `A-002` reproduce the ticket's two criteria verbatim. All six were recorded met
  with executed evidence at the Verification Gate by `omn-qa`: 316 tests green; a built wheel whose
  payload file list matched the bundle at 267 files with zero exclusion hits; a clean-environment
  non-editable install running `init`, `install` and `validate` with no `--source` flag; dry-run
  parity of 253 planned writes and 17 seeded files on both resolution paths; and regenerated
  metadata payload entries set-identical to the bundle.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `pyproject.toml` | none | out-of-scope | The package-data declaration; no scope rule matches, the path is outside the framework surface |
| `omn_agent/source.py` | none | out-of-scope | The appended resolution candidate and its constant; outside the framework surface |
| `omn_agent/_bundled_payload/**` | none | out-of-scope | The 267-file bundled mirror. Its *contents* duplicate the framework surface byte for byte, but its path matches no inclusion rule, so the profile decides it out-of-scope — the gap `O-003` records |
| `tests/test_bundled_payload.py` | none | out-of-scope | The new regression module; outside the framework surface |
| `tests/test_omn_agent.py` | none | out-of-scope | The two added command-line tests; outside the framework surface |
| `omn_agent.egg-info/SOURCES.txt` | none | out-of-scope | The regenerated distribution metadata; outside the framework surface |
| `.claude/runs/run-e0dba6763475/**` | `SR-3` | out-of-scope | Run evidence written by the runtime while it carried this change |
| `.claude/proposals/framework-change-proposal-FC-009.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

Every row recomputes to `out-of-scope`, and that is the honest reading:
`python .claude/runtime/self_hosting.py classify` decides each of the six delivered paths
`[OUT] no rule: no scope rule matches; the path is outside the framework surface`. **No touched
path of this change matches an inclusion rule of the Scope Rule.** The change was nonetheless
carried end to end by a framework command over a framework workflow with all six gates decided, and
`verify_self_hosting.py` check `S8` counts the run inside the self-hosted window and demands a
proposal for it. The record is therefore accurate in both directions at once: self-hosted in
execution, unreached by the Scope Rule in classification. Open item `O-003` carries that gap to its
owner rather than papering over it with a rule the profile does not actually decide.

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework's delivery vehicle gains a capability it did not have — the
  built distribution now carries the framework payload, and source resolution grows a third
  candidate that resolves it from the installed package location. The narrower
  `structure-preserving-change` claim is indefensible: observable behaviour changes in a whole
  environment class, since a non-editable install that previously could resolve nothing now
  resolves the bundle. The selector holds on substance; what does not hold is the Scope Rule's
  inclusion test, recorded above and at `O-003`
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`
- Classification and routing evidence: `python .claude/runtime/self_hosting.py route --intent capability-addition`
  resolves to `/implement` over `implement-feature` at `scope-and-acceptance`, which is exactly what
  `runs/run-e0dba6763475/execution-request.json` records: `command_id` `implement`, `workflow_id`
  `implement-feature`, one input of type `feature-request` at `runs/inputs/cka-02-feature-request.md`
  with digest `sha256:c153cb3a0a4f3d8bc12bb9e8a069b1a0`, submitted 2026-09-03T11:34:17Z

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-e0dba6763475/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature`, runtime 0.5.0, six phases declared, one input recorded with digest: `feature-request` at `runs/inputs/cka-02-feature-request.md` |
| `E-2` | `runs/run-e0dba6763475/run-ledger.json` | resolved |
| `E-3` | `runs/run-e0dba6763475/events.jsonl` | resolved; 79 canonical events, `E-0001` `run_initialized` through `E-0079` the Closure Gate resolution |
| `E-4` | `runs/run-e0dba6763475/state.json` | resolved; `run_status` Completed, six phases all `completed`, none blocked at close, 44 transitions, 18 replays suppressed, six gates each carrying a decision, an owner role and a named decider |
| `E-5` | `runs/run-e0dba6763475/completion-package.md` | resolved; 6 of 6 phases completed, 0 blocked, 0 failed, 0 pending; open escalations `None.` |
| `E-6` | `runs/run-e0dba6763475/states/implementation/artifacts/implementation-report.md` | resolved; each of the six phases committed its contracted artifact, and the design phase committed three — `technical-design.md` plus decision records `architecture-decision-record-D-001.md` and `architecture-decision-record-D-002.md` |
| `E-7` | `runs/run-e0dba6763475/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases and every one records `pass` with zero blocking and zero correctable failures |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed in one attempt; scope definition SCOPE-2026-0001 with 4 in-scope items, 3 exclusions, 6 acceptance criteria, 3 scope decisions, 1 non-blocking open question (`Q-001`, count parity versus set parity), verdict `bounded`, Validation Engine 33/33 with 3 checks not machine-checkable | host-dispatched `omn-product-owner` subagent | `runs/run-e0dba6763475/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed over two attempts; 10 tasks across 5 waves over 16 dependency edges, 3 assumptions, 6 risks, 1 open question, Validation Engine 45/45 with 5 not machine-checkable. Attempt 1 was rejected at `V4.1` and `V4.8` (2 blocking, 0 correctable), classified `output-schema-failure`, one attempt charged, and the artifact was accepted on the next attempt | host-dispatched `planner` subagent | `runs/run-e0dba6763475/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed over two attempts; 13 facts, 3 assumptions, 10 constraints, 8 modules, 3 options, 4 decisions, 8 reuse rows, 9 plan steps, 7 risks, 3 open decisions, and 2 committed decision records — `D-001` (carry the payload as declared package data inside the package) and `D-002` (append the bundled candidate to resolution, strictly last) — Validation Engine 78/78 with 10 not machine-checkable. Attempt 1 was rejected at `D4.3`, `D14.3` and `D15.2` (2 blocking, 1 correctable), one attempt charged, accepted on the next | host-dispatched `architect` subagent | `runs/run-e0dba6763475/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed in one attempt; implementation report IR-2026-0004 with 5 change-set entries, 13 test-evidence entries all passing, 2 recorded deviations (`V-001` the deferred metadata regeneration, `V-002` the committed-mirror sync), 3 residual risks (`R-001` bundle drift, `R-002` stale metadata, `R-003` three pre-existing proof-script failures) and 1 blocking open question (`Q-001`, which environment runs the build-backend steps), Validation Engine 32/32 with 3 not machine-checkable. The artifact was accepted at report status `provisional` and verification status `partially-verified`, which is what the run recorded and what the two downstream phases then had to resolve | host-dispatched `omn-dev-1-implement` subagent | `runs/run-e0dba6763475/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed in one attempt over 14h 56m; review package RP-2026-0004, verdict `approve`, 1 medium finding (`F-001`, the deferred metadata regeneration) recorded `resolved` after an out-of-run regeneration the reviewer verified entry by entry, 1 non-blocking correction request (`CR-001`), 0 critical, 0 high, 0 low, Validation Engine 31/31 with 3 not machine-checkable. The review independently re-executed the suite (316 tests), the new module (11 of 11), the added command-line tests (2 of 2) and four proof scripts at exit 0 | host-dispatched `omn-dev-2-reviewer` subagent | `runs/run-e0dba6763475/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed in one attempt; release note `RN-CKA-02-run-e0dba6763475` at version `0+CKA-02-unreleased`, verdict `released`, 8 known issues `K-001` to `K-008` carrying the stale-mirror window, the dot-named-directory glob gap, the payload-delivery-vector exposure, the three pre-existing proof-script failures and the undocumented user-facing behaviour, Validation Engine 32/32 with 3 not machine-checkable | host-dispatched `omn-documentation` subagent | `runs/run-e0dba6763475/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact, and none was blocked at
close. Three phases were held mid-run at `G4-GATE` waiting on a predecessor gate —
`solution-design-and-risk-assessment` on the Planning Gate, `implementation` on the Design Gate,
`documentation-and-release-handoff` on the Review Gate — and each was released by the decision
landing, not by a waiver: the recovery ledger records all three as `every guard now passes; the
condition the envelope recorded no longer holds`. All six phases were performed by host-dispatched
subagents under their contracted validators.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | `approved by omn-business-analyst, recorded by subagent:a717ccd6a30dd408f (omn-business-analyst)` | Independent assessment: scope faithfully bounds the ticket (payload packaging, bundled-source fallback with preserved precedence, metadata regeneration); criteria measurable and matching the ticket verbatim; the only low-severity finding, count parity versus set parity, already tracked as non-blocking question `Q-001`. `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | `approved by omn-tech-lead, recorded by subagent:af0aceaad65f9a3f4 (omn-tech-lead)` | Independent assessment: the 10-task breakdown is feasible and correctly sequenced (acyclic graph, waves matching edges); both verbatim ticket criteria mapped; risks credible; no blocking defect. Minor conditions carried forward — durable regression tests for the fallback in `T-006`, and the assurance decision recorded before it, edge-enforced. `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | `approved by omn-tech-lead, recorded by subagent:af0aceaad65f9a3f4 (omn-tech-lead)` | Independent assessment under producer exclusion: the factual register was verified against the repository (packaging configuration, candidate order, managed-directory and exclusion-pattern constants, installer guard); the selected package-data option is feasible and the fallback preserves precedence and the error path; decision records `D-001` and `D-002` accepted; all ten plan tasks bound. Minor: resolve the bundle-sync verification question before the bundle step completes, and watch whether the source distribution also needs an include-directive file. `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | `approved by omn-qa, recorded by subagent:aeddb5b479336d222 (omn-qa)` | Independent assessment under producer exclusion: the review package is complete and its single finding verifiably resolved (regenerated metadata set-identical to the bundle), with evidence reproduced under independent re-execution — 316 tests green and a real-wheel walkthrough. No blocking finding. `omn-dev-2-reviewer` produced the evidence and is excluded from deciding |
| Verification Gate | approve | omn-qa | `approved by omn-qa, recorded by subagent:aeddb5b479336d222 (omn-qa)` | Independent re-execution: all six acceptance criteria met on executed evidence — 316 tests green; wheel digest match with 267 payload files and zero exclusion hits; clean-environment validate OK; dry-run parity 253 and 17 on both paths; metadata payload entries set-identical to the bundle. Mirror-sync risk controlled by the parity tests; three pre-existing proof-script failures attributed to unrelated governance debt rather than to this change. Merge-ready |
| Closure Gate | approve | omn-orchestrator | `approved by omn-orchestrator, recorded by subagent:abd3b63c38b57a234 (omn-orchestrator)` | Independent orchestrator assessment under producer exclusion: the release note is faithful to delivered behaviour with honest known issues (`K-001` to `K-008`, including the stale-mirror window and the dot-glob gap); all six phases completed and all five prior gates decided by eligible non-producer owners; handoff items tracked with owners. Low finding: a wording tension between the release verdict and the body, disambiguated by the `0+CKA-02-unreleased` version string. `omn-documentation` produced the evidence and is excluded from deciding |

Every gate the workflow declares was decided, and none was waived. Each row's Decided By cell
reproduces the `resolution` string of the gate's own failure envelope under
`runs/run-e0dba6763475/gates/`, whose `resolved_by` field records the same decider prefixed
`human:`. Every gate held its successor in `blocked` with reason `awaiting_human_decision` until the
decision landed; the recorded waits ranged from 56 seconds at the Scope Gate to 30 minutes 5 seconds
at the Verification Gate. The Closure Gate was decided by `omn-orchestrator` because
`omn-documentation` produced the artifact it assesses — the mirror image of this role's exclusion in
the workflows where it produces that evidence itself.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6, 11 commands resolving, 37 of 37 phases dispatchable, 29/29 gate references decidable under the Producer Exclusion Rule |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 RECOVERY PROVEN, injected runs and inputs removed. The first invocation at authoring aborted before any scenario ran, because the harness's fixture run identity is derived deterministically from its own injected input and a concurrently executing invocation of the same verifier held that directory; a clean re-execution once the collision cleared reported 41/41. Recorded as `O-008`, an environment hazard unrelated to this change |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8 at authoring: `S1` to `S7` pass, and `S6` reports all 7 recorded proposals accepted at 38/38 each. `S8` fails on four runs inside the self-hosted window with no proposal — `run-34ca35504b72`, `run-8f8a1ab0d16e`, `run-e0dba6763475`, `run-efe092286625` — one of which is this run, whose row this proposal removes on the next execution. The other three are `O-002` |
| Scope classification recomputes | `python .claude/runtime/self_hosting.py classify --path pyproject.toml` (and each other delivered path) | pass, and it is the finding: all six delivered paths return out-of-scope with no matching rule; the run directory returns `SR-3` and this proposal `SR-5`. Recorded at `O-003` |
| Routing resolves | `python .claude/runtime/self_hosting.py route --intent capability-addition` | pass; resolves to `/implement` over `implement-feature` at `scope-and-acceptance`, agreeing with the run's execution request |
| Bundled mirror still matches the framework surface | `python .claude/runtime/verify_registry_coverage.py` — see note | inspection at authoring: the bundled subtree holds 267 files, and a digest comparison of the bundled runtime gateway against the authoritative one under the framework surface returns identical. This is a spot check of one file, not the parity suite; the delivered control is `tests/test_bundled_payload.py`, re-executed by the reviewer at 11 of 11 |
| Delivered change under test | inspection | recorded at the Review and Verification Gates rather than re-executed at closure or at authoring: the reviewer re-ran the full suite (316 tests, OK, exit 0), the new module (11 of 11), the added command-line tests (2 of 2) and four proof scripts at exit 0, and `omn-qa` verified all six acceptance criteria on executed evidence. This record takes those verdicts as the recorded facts they are and does not re-score them |
| Multi-phase state machine | inspection | deliberately not executed at authoring: the probe appends replay bookkeeping to a committed run's tracked state file, and modifying committed run evidence is prohibited to this role. The run's own record already carries the reading — release note `K-007` records the multi-phase traversal check failing on one historical run on conditions predating this change, attributed and accepted by `omn-qa` at the Verification Gate. Recorded as `O-007` |

## Risk and Rollback

- Blast radius: five delivered change-set entries and one out-of-run regeneration, none of them on
  the framework surface. `pyproject.toml` gains a package-data table with two recursive glob
  patterns; `omn_agent/source.py` gains one appended candidate in one branch plus one public
  constant; `omn_agent/_bundled_payload/` is new and holds 267 files; `tests/test_bundled_payload.py`
  is new; `tests/test_omn_agent.py` gains two tests; `omn_agent.egg-info/SOURCES.txt` was
  regenerated. No runtime module, workflow specification, registry record, gate-decision surface,
  agent manifest, artifact template, validator or command specification under the framework surface
  changed. The implementation report records a symbol search across every changed file finding none
  of the forbidden gate-behaviour surfaces, and the reviewer confirmed it independently and observed
  that the executed mirror-parity check rules out gate-behaviour alteration riding in through the
  bundle, since the bundle is byte-identical to the authoritative tree.
- Risk assessment: the change duplicates the entire framework surface into a second tree that the
  framework's own proof scripts do not read — the implementation report records that no proof script
  reads any changed file, which is what makes the three pre-existing proof-script failures
  attributable elsewhere, and is also what leaves the bundle outside every framework verifier. The
  only control on it is the delivered parity suite, so a payload edit followed by a build made
  without running the suite ships governance prose no framework check has inspected (release note
  `K-005`, reviewer-recorded as unmitigated). Alongside it stand: bundle drift between refreshes
  (`R-001`, controlled by the parity tests, owner `omn-dev-1-implement`); the packaging globs'
  inability to reach a dot-named directory, guarded only by a loud test failure (`K-006`,
  unmitigated); the distribution becoming a payload delivery vector reaching every installer
  (`K-004`, design risk `R-007`, accepted with the exclusion filter and content inspection as
  controls); the absence of any repeatable automated inspection of a built distribution's contents,
  the wheel check having been a one-off host run (`K-001`, handed to `omn-qa` with CKA-03); and user
  documentation still describing only the `--source` flow (`K-008`). Three residual risks were
  recorded at implementation and two of them closed within the cycle: `R-002`, the stale metadata,
  was closed by the regeneration the reviewer verified; `R-003`, the three failing proof scripts,
  was closed as attribution rather than as repair.
- Rollback procedure: withdraw the package-data declaration from `pyproject.toml`, remove the
  appended candidate and its constant from `omn_agent/source.py`, delete the 267-file
  `omn_agent/_bundled_payload/` subtree and `tests/test_bundled_payload.py`, revert the two added
  command-line tests, and regenerate the distribution metadata. Per the implementation report's
  boundary-compliance account this restores the prior distribution and resolution shape without
  touching any installed target, because installed targets are governed by the install manifest and
  no installed-target layout changed. The conditions that would justify it are the two the release
  note names: any pre-existing environment class ceasing to resolve identically — a precedence
  regression, which criteria `A-004` and `A-005` and the reviewer's re-executed precedence tests
  demonstrated absent — or the bundle being found to ship content drifted from the authoritative
  payload undetected. Reverting invalidates no other run's evidence: `run-e0dba6763475` remains a
  valid record of a delivered-then-reverted change, and this proposal remains its governance record.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | `verify_registry_coverage.py` 6/6 at authoring; 11 active commands resolving, 37 of 37 phases dispatchable, 29/29 gate references decidable |
| `FR-02` | Validator coverage and decisiveness | pass | `verify_validators.py` 6/6 at authoring |
| `FR-03` | Recovery behaviour | pass | `verify_recovery.py` 41/41 RECOVERY PROVEN at authoring. The first invocation aborted on a fixture-run identity collision with a concurrently executing invocation of the same verifier, before any scenario ran; the clean re-execution is the recorded result. The collision is `O-008` |
| `FR-04` | Committed evidence still verifies | pass | `verify_vertical_slice.py --run-id run-c5a8d50d3238` 10/10 PROVEN at authoring; no committed proof was invalidated |
| `FR-05` | Self-hosting governance resolves | accepted | `verify_self_hosting.py` reports 7/8 at authoring. `S1` to `S7` pass: the profile parses, all 7 routing rows resolve, every scope rule is reachable with exclusions binding, the change-proposal contract is registered, the release checklist parses, and all 7 recorded proposals validate at 38/38 with their runs satisfying the Completion Rule. `S8` fails on four runs inside the self-hosted window carrying no proposal. That residual is exactly open item `O-001` of `FC-007` and exactly the backlog this proposal is part of closing: it accounts for `run-e0dba6763475`, one of the four, and three sibling proposals are being authored for the rest. Recording `pass` here would assert a state the verifier does not report; the acceptance is recorded instead, with `O-002` carrying the remainder |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `runs/run-e0dba6763475/execution-request.json` records `command_id` `implement` and `workflow_id` `implement-feature`, which is what the profile routes `capability-addition` to; this proposal links that run's artifacts at `E-1` to `E-7`, every link resolving under `runs/run-e0dba6763475/` |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0, as inspected at authoring in the runtime gateway. No runtime module on the framework surface changed; the bundled copy of that same module is byte-identical to the authoritative one by digest comparison, so the distribution carries the runtime rather than altering it |
| `FR-08` | Documentation matches delivered behaviour | accepted | The documents this item names are untouched and unaffected: no runtime README, no folder description, and no catalog is changed by this change. But the delivered behaviour is not yet described anywhere a user reads — the user guide and the handbook document install flows with `--source` only, and whether the repository README misstates source resolution was not established, because no existing documentation was supplied to the run. The release note records this as known issue `K-008` with proposed replacement content and a named applying role, and the Closure Gate approved that note with the issue open. Acceptance is recorded on that basis; the outstanding work is `O-006` |
| `FR-09` | Capability claims backed by evidence, gaps recorded | accepted | Every claim about the delivered code carries executed evidence re-run independently: 13 test-evidence entries at implementation, and the reviewer's own re-execution of 316 tests, 11 of 11 new tests, 2 of 2 command-line tests and four proof scripts at exit 0. Gaps are recorded rather than omitted — the reviewer explicitly marks the pre-change 303-test baseline, the simulated site-packages driver runs and the attribution re-run as claimed but not confirmed. The acceptance is for one gap the item's own wording exposes: the strongest evidence for both ticket acceptance criteria, the real-wheel clean-environment walkthrough, exists only as a host-run transcript in a session scratchpad that is not committed under `runs/` or `reports/` and does not resolve in the repository at authoring. The reviewer relied on it as confirmed third-party evidence and `omn-qa` approved the Verification Gate on it. Recorded as `O-004` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above: a six-path revert with its trigger conditions named, and an explicit statement of what reverting does and does not invalidate |
| `FR-11` | Multi-phase state machine still proves out | accepted | Not executed at authoring: the probe appends replay bookkeeping to a committed run's tracked state file, and modifying committed run evidence is prohibited to this role. The run's own record carries the reading instead — release note `K-007` and implementation risk `R-003` record the multi-phase traversal check failing on one historical run, on conditions predating this change, with attribution evidence, and `omn-qa` accepted that attribution at the Verification Gate. `FR-11` is advisory. Post-commit re-execution is `O-007` |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-e0dba6763475/states/documentation-and-release-handoff/artifacts/release-note.md`, release `RN-CKA-02-run-e0dba6763475` at version `0+CKA-02-unreleased`, verdict `released`, 8 known issues, Validation Engine 32/32 |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | This proposal is a retrospective governance record, authored 2026-09-04T15:44:10Z, roughly eleven hours after the run's Closure Gate decision at 2026-09-04T04:58:35Z, by an `omn-orchestrator` instance that took no part in the run. The run closed without a proposal and was accounted for afterwards; the record is therefore assembled from committed evidence rather than written alongside the work | omn-orchestrator | Recorded, not open. Disclosed rather than implied; every claim traces to run evidence written before the authoring instant, and the Authoring Baseline fixes the state the claims are judged against under `GD-001` |
| `O-002` | Three framework runs inside the self-hosted window still carry no change proposal and keep `S8` failing — `run-34ca35504b72` (2026-08-27T12:50:39Z), `run-efe092286625` (2026-08-27T13:14:08Z) and `run-8f8a1ab0d16e` (2026-09-04T05:50:51Z). This proposal removes only `run-e0dba6763475` from that list | omn-orchestrator | Open, pre-existing. Inherited from `O-001` of `FC-007`, which recorded all four; closing it requires a proposal per run, authored from each run's own evidence |
| `O-003` | No path this change touched matches an inclusion rule of the profile's Scope Rule: the classifier decides `pyproject.toml`, `omn_agent/**`, `tests/**` and the distribution metadata all out-of-scope with no matching rule. `SR-1` reaches the framework surface and `SR-2` the four root governance documents, but nothing reaches the distribution that ships the framework payload — so a change to the framework's own delivery vehicle is invisible to classification while still being routed, gated and counted by `S8` | architect | Open. Either the Scope Rule gains a rule covering the packaging and bundling surface, or the profile states explicitly that a self-hosted run may carry a change the Scope Rule does not reach. The gap is recorded rather than resolved here: amending the profile is a framework-internal edit outside the single-file write this authoring was authorized to make |
| `O-004` | The evidence that closes both ticket acceptance criteria — the real-wheel, clean-environment install walkthrough and the wheel content inspection — exists only as a host-run transcript held in a session scratchpad, cited by the review package as `cka-02-wheel-verification.md`. It is not committed under `runs/` or `reports/` and does not resolve in the repository at authoring, so the two strongest acceptance claims are not independently re-checkable from the record | omn-qa | Open. Either commit the transcript as a dated report or supersede it with the repeatable distribution-content check that known issue `K-001` hands to CKA-03 |
| `O-005` | Ticket deliverable 3, the distribution-metadata regeneration, was deferred inside the run under deviation `V-001` with blocking question `Q-001`, and then performed outside every phase by the run coordinator's host build. It is recorded only in the review package's finding `F-001`, which the reviewer verified entry by entry; no phase artifact carries the work itself | omn-tech-lead | Open as a record gap rather than as undelivered work. The deliverable is satisfied and verified; what is missing is a run artifact that owns it |
| `O-006` | User documentation does not describe the delivered behaviour: the user guide and the handbook document install flows with `--source` only, and whether the repository README misstates source resolution was never established, because no existing documentation was supplied to the run. The release note carries proposed replacement content and the three-candidate resolution order for whoever applies it | omn-documentation | Open, tracked as release-note known issue `K-008` and sequenced by the accepted design at `P-009`; the Closure Gate approved the note with the issue open rather than suppressing it |
| `O-007` | The multi-phase state-machine proof was not re-executed at authoring, because the probe appends replay bookkeeping to a committed run's tracked state file and this role may not modify committed run evidence. The run's record carries the reading second-hand, through `K-007` and `R-003` | omn-qa | Open. Unchanged from `O-003` and `O-004` of `FC-007`, which record the same tooling hazard; executors must check version-control state of run evidence after running the proof and restore committed content |
| `O-008` | `verify_recovery.py` derives its fixture run identity deterministically from its own injected input, so two concurrent invocations collide on one directory under the run store. At authoring the first invocation aborted on exactly that collision — the second invocation then refused to start, reporting the fixture run absent while its partial directory remained — and only a later re-execution, once the collision cleared, reported 41/41. Concurrent proposal authoring makes the collision likely rather than theoretical | omn-tech-lead | Open, environment hazard, unrelated to the change this proposal documents. Give the harness a per-invocation fixture identity, or serialize it |
| `O-009` | `omn-orchestrator` is the contracted producer of this artifact, yet its manifest permits no repository write in any phase. This instance authored the file under an explicit operator authorization scoped to exactly it | omn-tech-lead | Open, unchanged; the standing contradiction is tracked since `O-003` of `FC-005`, `O-006` of `FC-006` and `O-006` of `FC-007`. Resolve by narrowing the producer list or widening the manifest's write scope for this artifact alone |
| `O-010` | The `Recorded Framework Changes` index in `config/self-hosting-profile.md` carries no `FC-009` row. Adding one is a framework-internal edit (`SR-1`) outside the single-file write this authoring was authorized to make; the index is a directory, not an authority — `verify_self_hosting.py` discovers proposals by glob, so its absence blocks nothing | operator | Open; append the row with the next routed framework change or as operator housekeeping |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorized by the session operator for this single file; this instance took no part in run-e0dba6763475 and decided none of its gates
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, and omn-orchestrator at the Closure Gate as non-producing owner — every one of the six decided by an owner who did not produce the evidence it assesses
- Acceptance basis: all six phases of the routed workflow executed with artifacts their registered validators accepted at 33/33, 45/45, 78/78, 32/32, 31/31 and 32/32; two charged retries recorded with the checks that failed and what each repaired; three mid-run predecessor-gate holds released by decisions rather than waivers; six acceptance criteria met on executed evidence at the Verification Gate; and ten open items recorded with owners — including the classification gap this change exposes, the acceptance evidence that lives outside the repository, and the three-run accounting residual this proposal does not close
