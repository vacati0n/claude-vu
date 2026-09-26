# Framework Change Proposal: Pull-Request CI Gate over the Discovered Unit-Test Suite and the Discovered Proof-Script Verdicts

```yaml
frameworkChangeProposal:
  proposalId: FC-010
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-8f8a1ab0d16e
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-010
- Change title: Add the CI verification workflow that gates every pull request and default-branch push on two discovery-located surfaces — the unit-test suite and every proof script — with a committed contract net and contributor documentation
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-8f8a1ab0d16e
- Authored on: 2026-09-04

## Authoring Baseline

- Authored at: 2026-09-04T15:39:56Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

This record is retrospective. Run `run-8f8a1ab0d16e` was submitted at 2026-09-04T05:50:51Z and its
Closure Gate was decided at 2026-09-04T07:34:05Z; this proposal was authored roughly eight hours
after that decision, in a later session, by an author who did not carry the run. It is therefore an
account assembled from the run's committed evidence, not a closure-time artifact, and nothing in it
should be read as having been available to the Closure Gate that approved the run. Its function is
to give the run the governance record the profile's Completion Rule `C-6` requires and that the run
closed without.

## Change Statement

- Objective: give the repository an automatic, pre-merge verification gate where it previously had
  none. Before this change no CI configuration existed at all: the unit-test suite and the
  framework's own proof scripts ran only when a contributor remembered to run them locally, so a
  regression in any test or any verifier could merge unobserved. Ticket CKA-03 in the adoption
  backlog under `docs/`, tracing to recommendation R1 of the adoption review dated 2026-08-27, and
  the closing ticket of that plan's first phase, on which six later tickets (CKA-06, CKA-07,
  CKA-08, CKA-09, CKA-13, CKA-15) depend for the CI hook itself.
- In scope: the new CI workflow definition `.github/workflows/verify.yml`, running on every pull
  request and every default-branch push, with two surfaces located by discovery rather than by a
  curated list — the unit-test suite by standard-library discovery from the repository root on both
  stated platforms, and every `verify_*.py` under the framework payload runtime directory fanned
  out one job per discovered verifier per platform onto a fresh runner, each asserted to exit 0
  *and* print its own all-checks-passed summary with a non-negative verdict; four stable check
  names (`tests-ubuntu`, `tests-windows`, `verifiers-ubuntu-ok`, `verifiers-windows-ok`) for
  branch protection to bind to, with advisory standing encoded as absence from the required-checks
  list rather than as a per-job failure-tolerance flag; the committed 13-test contract net
  `tests/test_ci_workflow.py` locking the workflow's rename-sensitive and no-curation properties
  into the unit-test suite; and the contributor-facing record of the surfaces, the check names,
  their standings and the flip precondition in `README.md`, `docs/USER-GUIDE.md` and the
  hand-synced `docs/user-guide.html`, with check-name parity across all three asserted by test.
- Out of scope: the branch-protection required-checks configuration itself, which is a hosting
  platform settings surface no repository file carries (scope exclusion recorded as the change's
  own boundary, enactment owned by omn-tech-lead); the cleanup of the three pre-existing orphan run
  directories dated 2026-08-27 that fail the self-hosting proof's run-accounting check (`X-001`,
  owned by a separate follow-up task, with decision record D-003 selecting clean-first and making a
  green self-hosting run the flip precondition); every gate-decision runtime surface the ticket
  names — `record_gate_decision`, the gate-matrix semantics, producer exclusion,
  `runner._require_approval`, and any human-block path (`X-002`); CI surfaces or triggers beyond
  the two named (`X-003`); repairing the recovery proof's timing sensitivity or the render tests'
  colour assertions (`X-004`); and platforms beyond the two stated (`X-005`).
- Acceptance basis: twelve measurable acceptance criteria `A-001` to `A-012` in scope definition
  SCOPE-2026-0003, each bound to one of six in-scope items with a named verification method. The
  run's record does not carry a per-criterion disposition table for `A-001` to `A-012`, and this
  proposal does not invent one. What the record does carry is the Verification Gate's own
  enumeration of what omn-qa re-executed — the 13-test contract net (13/13), the workflow parsing
  as YAML, the discovery expression enumerating exactly the seven verifiers present on disk, the
  verifier-assertion wrapper accepting a really passing proof script and rejecting every failing
  verdict form found on disk, both verbatim ticket criteria confirmed structurally, no
  framework-runtime path among the declared side effects, and no colour-suppression value set
  anywhere — together with its explicit statement that live hosted-run behaviour remains
  reported-only and is routed to the advisory-week soak and the flip preconditions. Acceptance was
  therefore granted on structural and locally executed evidence, with the live surface openly
  unconfirmed.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.github/workflows/verify.yml` | none | out-of-scope | The delivered CI workflow. No inclusion rule matches: the path is outside the framework surface the profile's Scope Rule covers |
| `tests/test_ci_workflow.py` | none | out-of-scope | The committed 13-test contract net. No rule matches; the path is outside the framework surface |
| `README.md` | none | out-of-scope | Repository README. `SR-2` names four root governance documents and this is not one of them, so no rule matches |
| `docs/USER-GUIDE.md` | none | out-of-scope | Handbook section documenting the CI surface. No rule matches |
| `docs/user-guide.html` | none | out-of-scope | Hand-synced HTML counterpart of the handbook change. No rule matches |
| `.claude/runs/run-8f8a1ab0d16e/**` | `SR-3` | out-of-scope | Run evidence written by the runtime while it carried this change |
| `.claude/proposals/framework-change-proposal-FC-010.md` | `SR-5` | out-of-scope | This proposal: the governance record of the routed change, not a second change |

Every row recomputes to out-of-scope under the profile, and that is the load-bearing fact of this
section rather than a rounding detail. The Scope Rule's inclusion set is `SR-1` (`.claude/**`) and
`SR-2` (four named root governance documents); not one of the five delivered paths matches either,
so the profile's Scope Rule does not classify this change as framework-internal on its delivered
surface. `python .claude/runtime/self_hosting.py classify` returns `not a framework-internal
change` for each of the five. The change was nevertheless carried by a run of the framework's own
`/implement` command, and the profile's own accounting reaches it on that basis alone: check `S8`
of `verify_self_hosting.py` requires a change proposal for every run under `runs/` inside the
self-hosted window, regardless of what the touched paths classify as. This proposal is written to
that obligation, and it is the reason the routing below is recorded as applied at submission rather
than as derived from the Scope Rule.

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the repository gains an enforcement capability it did not have — an
  automatic pre-merge verification gate over two discovered surfaces, plus a stable four-name check
  contract that branch protection binds to. The narrower `structure-preserving-change` claim is
  indefensible: observable behaviour changes for every contributor, since a pull request can now
  fail on evidence nothing previously produced
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`
- Routing evidence: `python .claude/runtime/self_hosting.py route --intent capability-addition`
  resolves to `/implement` over `implement-feature` v1.0.0 at `scope-and-acceptance` of 6, which is
  exactly what `runs/run-8f8a1ab0d16e/execution-request.json` records as `command_id`,
  `workflow_id` and the first enqueued phase. The routing row's Required Inputs column lists four
  types (`feature-request`, `change-request`, `business-intent`, `architecture-context`) and the run
  was submitted with one, `feature-request`; per the profile's Routing Resolution that is not a
  routing shortcut but a narrowing the owning agent's input contract absorbs, and the run's
  `G5-INPUT` guard passed at every phase with the recorded detail `required none (menu contract)`

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-8f8a1ab0d16e/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature` v1.0.0, six phases enqueued, one input recorded with digest: `feature-request` at `runs/inputs/cka-03-feature-request.md`, submitted 2026-09-04T05:50:51Z |
| `E-2` | `runs/run-8f8a1ab0d16e/run-ledger.json` | resolved |
| `E-3` | `runs/run-8f8a1ab0d16e/events.jsonl` | resolved; 73 canonical events, ending `run_completed` — every workflow phase completed and every gate decided |
| `E-4` | `runs/run-8f8a1ab0d16e/state.json` | resolved; `run_status` Completed, six phases all `completed`, none blocked at the close, 40 transitions, all six gates carrying a recorded decision |
| `E-5` | `runs/run-8f8a1ab0d16e/completion-package.md` | resolved; 6 completed, 0 blocked, 0 failed, 0 pending; 0 replays suppressed; no open escalation |
| `E-6` | `runs/run-8f8a1ab0d16e/states/implementation/artifacts/implementation-report.md` | resolved; each of the six phases committed its contracted artifact, and the design phase committed three architecture decision records alongside its technical design |
| `E-7` | `runs/run-8f8a1ab0d16e/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases and every one records `pass` with zero blocking and zero correctable failures. Each report's `artifact` field carries an absolute path under an earlier repository root — stale provenance in the record, with no bearing on the recorded verdicts |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed against the run in one attempt, 5m 52s; scope definition SCOPE-2026-0003 with 6 in-scope items, 5 exclusions, 12 acceptance criteria, 4 scope decisions, 2 non-blocking open questions, verdict `bounded`, Validation Engine 33/33 with 3 declared not-machine-checkable | host-dispatched `omn-product-owner` v1.0.0 subagent | `runs/run-8f8a1ab0d16e/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed against the run in one attempt, 10m 9s; 10 tasks over 6 waves on a 15-edge dependency graph, 5 assumptions, 9 risks, 2 non-blocking open questions, Validation Engine 45/45 with 5 not-machine-checkable | host-dispatched `planner` v1.0.0 subagent | `runs/run-8f8a1ab0d16e/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed against the run over two attempts, 18m 36s; 4 options against 12 constraints and 14 recorded facts, 9 modules, 7 decisions, 9 risks, 3 open decisions, and three committed decision records D-001 (discovery-fed per-verifier matrix with runner-boundary isolation), D-002 (blocking authority in the required-checks list, advisory standing as absence from it) and D-003 (orphans cleaned first, with a green self-hosting run as the flip precondition), Validation Engine 78/78 with 10 not-machine-checkable. Attempt 1 was rejected by the Validation Engine at `D8.3`, `D13.2` and `D16.4` — 2 blocking and 1 correctable — classified `output-schema-failure`, retried after 2.236s of backoff, and accepted on attempt 2 | host-dispatched `architect` v1.0.0 subagent | `runs/run-8f8a1ab0d16e/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed against the run in one attempt, 40m 20s; implementation report IR-2026-0005 at status `provisional` and verification status `partially-verified`, with 5 change-set entries `C-001` to `C-005`, 7 test-evidence entries all passing (27/27 local assertions, 13/13 committed net, 316/316 full suite), 2 recorded deviations (`V-001` the `main` branch literal, `V-002` two per-platform matrices), 3 residual risks `R-001` to `R-003`, and 3 open questions of which `Q-001` was raised blocking at the Review Gate, Validation Engine 32/32 with 3 not-machine-checkable | host-dispatched `omn-dev-1-implement` v1.0.0 subagent | `runs/run-8f8a1ab0d16e/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed against the run in one attempt, 11m 35s; review package RP-2026-0005 reading all five change-set entries in full, re-executing the committed net independently (13 tests, OK), verdict `approve-with-corrections` on 2 findings both low — `F-001` the overstated push-run cancellation guarantee, `F-002` the untested interpreter-floor coupling — with 0 critical, 0 high, 0 medium, 2 non-blocking correction requests `CR-001`/`CR-002` to omn-dev-1-implement, and no blocking finding outstanding, Validation Engine 31/31 with 3 not-machine-checkable | host-dispatched `omn-dev-2-reviewer` v1.1.0 subagent | `runs/run-8f8a1ab0d16e/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed against the run in one attempt, 5m 15s; release note RN-2026-0005-CKA-03 at version `0+CKA-03-unreleased`, verdict `released`, carrying 6 known issues `K-001` to `K-006` — the two correction requests, the structurally-only-verified live behaviour, the expected red advisory fan-ins on pre-existing orphan state, the unconfirmed default-branch literal, and the unenacted required set — Validation Engine 32/32 with 3 not-machine-checkable | host-dispatched `omn-documentation` v1.0.0 subagent | `runs/run-8f8a1ab0d16e/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact and none blocked at the
close. All six were performed by host-dispatched subagents under their contracted validators: the
framework held every gate, validated every artifact, and rejected one of them. The recovery ledger
records ten entries, every one resolved — one charged retry (the design phase's rejected first
attempt, one of three attempts consumed) and nine non-retryable `gate-approval-required`
escalations, six raised on gate work items awaiting a human decision at `G6-GATE-EVIDENCE` and
three raised on successor phases held at `G4-GATE` because the gate ahead of them carried no
decision yet. Those three holds are the mechanism working: `solution-design-and-risk-assessment`,
`implementation` and `documentation-and-release-handoff` each sat blocked until the gate closing
their predecessor was decided, and each was released by the state engine with the recorded
resolution `every guard now passes; the condition the envelope recorded no longer holds`.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | `human:a46ff6cfcc3516fe1`, recorded resolution `approved by omn-business-analyst, recorded by a46ff6cfcc3516fe1` | Scope bounded and faithful to CKA-03: six in-scope items, five exclusions and four decisions all trace to the ticket; both verbatim acceptance criteria covered measurably among twelve; both open questions non-blocking. One condition passed downstream — the default-branch push trigger runs both verification surfaces, and the PR-only wording in `S-002`/`A-003` is imprecision rather than an approved narrowing. `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | `human:aa8a3a7c55b4553a7`, recorded resolution `approved by omn-tech-lead, recorded by aa8a3a7c55b4553a7` | Executable ten-task six-wave plan with dependency-forced ordering: orphan handling and flip ownership decided first, design binding implementation, the advisory-to-required flip conditioned on evidence. All 12 scope criteria traced; the orphan-accounting risk structurally contained. Two conditions set for the phases downstream: verification evidence must include a default-branch push run executing verifier jobs, and the both-surfaces-on-push reading is settled by the Scope Gate owner's condition. `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | `human:a7adf4bc0da17e28c`, recorded resolution `approved by omn-tech-lead, recorded by a7adf4bc0da17e28c` | Both Planning Gate conditions honoured; the selected topology implementable on both platforms, with runner-boundary isolation neutralising the recovery-verifier cascade, per-verifier check names satisfying the failure-naming requirement, advisory-by-omission keeping week-one failures visible, and the colour-suppression hazard handled by declared absence. The orphan question decided explicitly clean-first; additive-only verified. Three conditions for implementation: confirm the platform matrix and required-named-check facilities, record flip ownership before merge, and demonstrate the fan-in checks failing rather than skipping under upstream cancellation. `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | `human:a47c7d0002c8b2e07`, recorded resolution `approved by omn-qa, recorded by a47c7d0002c8b2e07` | The review package covers every contract dimension with constraint-by-constraint design-conformance checks and honest reported-versus-confirmed labelling; both findings correctly classified low and non-blocking; with zero critical, high and medium findings, `approve-with-corrections` is the verdict the adjudication table yields, and the two correction requests travel to the implementer as open low corrections. Decided as non-producer second owner, `omn-dev-2-reviewer` having produced the findings |
| Verification Gate | approve | omn-qa | `human:a47c7d0002c8b2e07`, recorded resolution `approved by omn-qa, recorded by a47c7d0002c8b2e07` | Acceptance evidence re-executed rather than accepted on assertion: 13/13 contract tests, workflow YAML parses, the discovery expression enumerates exactly the seven verifiers on disk, the wrapper's output matches a really passing proof script and rejects every failing verdict form present on disk, both ticket criteria confirmed structurally, no framework-runtime path among declared side effects, no colour-suppression value set. The recovery and self-hosting verifiers were excluded by design as timing-sensitive and in flight, and live hosted-run behaviour was left reported-only and routed to the advisory-week soak and flip preconditions |
| Closure Gate | approve | omn-orchestrator | `human:ab6162ce6e3d61a0d`, recorded resolution `approved by omn-orchestrator, recorded by ab6162ce6e3d61a0d` | The release note faithfully and traceably describes the delivered change set and bounds its verification claims, labelling live hosted-run behaviour as structurally verified only and routing confirmation to omn-qa; every open item carried with a named owner; every upstream phase completed with passing validation and every upstream gate decided by a non-producer; no critical or high escalation open. Post-closure follow-ups logged to the tech lead, QA and the implementer. `omn-documentation` produced the evidence and is excluded from deciding |

Every gate the workflow declares was decided, and none was waived. Every decision was recorded by a
human actor against a gate that had first held the run blocked at `awaiting_human_decision`: the
runtime invented no approval, and the total time the six gates held the run was 13m 36s. The
Closure Gate rationale is the one place this proposal's own subject appears, and it is worth being
precise about what it does not say: it records no change proposal, because none existed. The
accounting obligation it left open is what this record closes.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6 — 11/11 commands resolve, 8/8 workflows publish a Phase Model over 37 phases, 12/12 phase owners host-invocable, 105/105 skill references resolve, 29/29 gate references decidable under the Producer Exclusion Rule, 37 of 37 phases dispatchable |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 — every artifact type a Phase Model names carries a registered validator, and each rejects a mutated artifact at a named check |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 RECOVERY PROVEN. Recorded side effect: the proof injects runs under `runs/` and reports removing them; during this authoring window an injected run was briefly visible to `S8` before cleanup, and tracked evidence of `run-34ca35504b72` carries uncommitted modifications produced by executions of this proof — open item `O-004` |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, with agent module digest drift since execution reported as informational under `GD-001` |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8 at the authoring instant. `S1` to `S7` pass, including `S6` (all seven recorded proposals accepted, each 38/38) and `S7` (every recorded change carried by a run satisfying the Completion Rule). `S8` fails on four unaccounted runs — `run-34ca35504b72`, `run-e0dba6763475`, `run-efe092286625` and `run-8f8a1ab0d16e`. This proposal removes the last of those four on the verifier's next execution; the other three are open item `O-002` |
| Scope classification recomputes | `python .claude/runtime/self_hosting.py classify --path .github/workflows/verify.yml` (and each of the other four delivered paths) | pass; all five return `not a framework-internal change` with no matching rule, agreeing with every row of Scope Classification above |
| Routing resolves | `python .claude/runtime/self_hosting.py route --intent capability-addition` | pass; resolves to `/implement` over `implement-feature` v1.0.0 at `scope-and-acceptance`, agreeing with the run's execution request |
| The delivered contract net still holds | `python -m unittest tests.test_ci_workflow` | pass; 13 tests, OK — re-executed at this authoring instant against the delivered workflow, matching the count the implementation report claimed and the reviewer independently confirmed during the run |
| Live hosted-run behaviour | inspection | not verified, and recorded as such rather than asserted. The matrix fan-out from the discovery output, the rendered per-verifier check names, fan-in behaviour under a real upstream failure and a real cancellation, superseded-run cancellation, and both platforms' hosted-runner results were reachable from no environment the run had. The Verification Gate accepted the change on structural and locally executed evidence with this gap stated, and routed confirmation to omn-qa as `Q-001` and release-note issue `K-003` |
| Multi-phase state machine | inspection | deliberately not re-executed. Its live-replay check appends replay bookkeeping to the target run's tracked state file, and modifying committed run evidence is prohibited to this role and outside the single-file write this authoring session was authorized to make. Recorded as `FR-11` accepted below and as open item `O-004` |

## Risk and Rollback

- Blast radius: five repository paths, none of them inside the framework payload directory — one new
  CI workflow definition, one new test module, and CI sections added to three documentation files.
  No runtime module, workflow specification, registry record, gate-decision surface, agent manifest,
  artifact template or validator changed; `RUNTIME_VERSION` remains 0.5.0. The independent review
  assessed that non-modification from the declared side effects plus content inspection of the
  framework runtime files it read, and stated plainly that its environment carried no
  version-control baseline for a byte-level diff — so the additive-only claim rests on declared
  side effects and inspection rather than on a diff. One boundary sits outside the repository
  altogether: blocking authority lives in the hosting platform's required-checks list, which no
  repository file carries and which this change did not and could not touch.
- Risk assessment: three residual risks recorded and owned, and six known issues published. The
  verifier fan-in checks will report red from the first live run on pre-existing repository state,
  because three orphan run directories fail the self-hosting proof's run-accounting check until an
  externally owned cleanup lands (`R-001`, `K-004`); advisory standing is what keeps that visible
  but non-blocking, and decision record D-003 makes a green self-hosting run the precondition for
  ever making those checks required. A future edit renaming one of the four stable check names
  would detach branch protection, either blocking every pull request as forever-expected or letting
  blocking silently lapse (`R-002`); the committed net fails the suite on any rename, which is the
  whole reason it exists. The recovery proof's backoff-deadline assertion may flake on hosted
  runners, especially on the second platform (`R-003`), contained by runner-boundary isolation and
  disabled fail-fast rather than by ordering. Two low findings remain open as non-blocking
  corrections: the workflow's documented cancellation guarantee overstates what the platform gives
  for pending push runs (`F-001`/`CR-001`/`K-001`), and nothing ties the workflow's four
  interpreter-version literals to the declared packaging floor, so a bump in either file alone
  passes the whole suite (`F-002`/`CR-002`/`K-002`). Three coordination items are unenacted at
  closure: the default-branch literal is unconfirmed (`K-005`), and neither the day-one required set
  nor the later flip is yet enacted or owned on record (`K-006`), which means the staged rollout the
  documentation describes is described rather than in force. The largest exposure is none of these
  individually but the shape they share: everything about the gate's live behaviour is verified
  structurally and nothing about it has been observed running.
- Rollback procedure: delete `.github/workflows/verify.yml` and the gate stops existing; the
  committed contract net and the three documentation sections revert with it, a five-path additive
  revert with no runtime, gate-decision or registry behaviour attached, because the change added no
  such behaviour in either direction. Nothing in the repository depends on the four check names
  except the branch-protection list, which is a settings surface reverted by removing the names
  from it. The condition that would justify reversion is not a red advisory fan-in — that is
  expected on pre-existing orphan state and is exactly what the advisory window absorbs — but a
  flake rate during the advisory week that makes the fan-out indefensible, in which case decision
  record D-001 names the sequential consolidated loop as the fallback shape to re-derive from
  before any verifier check becomes required. Reverting invalidates no other run's evidence:
  `run-8f8a1ab0d16e` remains a valid record of a delivered-then-reverted change, and this proposal
  remains its governance record.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6; 37 of 37 phases dispatchable, 12/12 phase owners host-invocable, 29/29 gate references decidable |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6; every registered validator accepts a conforming artifact and rejects a mutated one at a named check |
| `FR-03` | Recovery behaviour | pass | 41/41 RECOVERY PROVEN; the proof's own run injection and its effect on tracked run evidence are recorded as `O-004` rather than omitted |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN; module digest drift reported as informational under `GD-001` |
| `FR-05` | Self-hosting governance resolves | accepted | 7/8 at the authoring instant. The profile parses, all seven routing rows resolve, the change-proposal contract is registered, and all seven recorded proposals validate at 38/38 (`S1` to `S7`). `S8` fails on four unaccounted runs, which is open item `O-001` of `FC-007` and the exact backlog this proposal is part of closing: it accounts for `run-8f8a1ab0d16e`, one of the four, and three sibling proposals for `run-34ca35504b72`, `run-e0dba6763475` and `run-efe092286625` are being authored in parallel and are not yet in place. Recording `pass` here would assert a state the verifier contradicts, so the failure is accepted with its residual named as `O-002` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `runs/run-8f8a1ab0d16e/execution-request.json` records an `/implement` run over `implement-feature`, which is what the profile routes `capability-addition` to; this proposal links that run's artifacts as `E-1` to `E-7`, and `verify_self_hosting.py` will report the `FC-010` row on its next execution |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0, verified in `runtime/framework_runtime.py`. No runtime module changed; the delivered workflow executes the proof scripts read-only and asserts their exit status and summary line |
| `FR-08` | Documentation matches delivered behaviour | pass | The change is its own documentation event: `README.md`, `docs/USER-GUIDE.md` and `docs/user-guide.html` each carry the two surfaces, the four check names, their standings, advisory-by-omission and the flip precondition, and check-name parity across all three is asserted by the committed net rather than by review alone. `runtime/README.md` and the folder descriptions are untouched by the change. The one documentation defect the record carries is the overstated cancellation claim in the workflow header, published as `K-001` with its correction request rather than left silent |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every executed claim was either re-executed by the independent review (the 13-test net, confirmed 13/13) or re-executed at the Verification Gate (discovery enumeration, wrapper accept and reject semantics, YAML parse, policy scans), and the claims that were not are labelled as claimed rather than confirmed — the 316-test full suite and the five scratch-script assertion runs. The gap that matters is stated in three places at once: live hosted-run behaviour is verified only structurally, recorded as unverified in the implementation report, out of scope in the review, and published as `K-003` with omn-qa named as its owner |
| `FR-10` | Rollback stated | pass | Risk and Rollback above: a five-path additive revert, the trigger condition named, the fallback topology named, and the settings surface that must revert with it identified |
| `FR-11` | Multi-phase state machine still proves out | accepted | Not executed. The proof's live-replay check appends replay bookkeeping to the target run's tracked state file; modifying committed run evidence is prohibited to this role and lies outside the single-file write this authoring session was authorized to make. The item is advisory in the checklist for a runnability reason and is accepted here for an authority reason; post-authorization re-execution is carried as `O-004` |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-8f8a1ab0d16e/states/documentation-and-release-handoff/artifacts/release-note.md`, RN-2026-0005-CKA-03 at version `0+CKA-03-unreleased`, verdict `released`, 6 known issues, Validation Engine 32/32 |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | This proposal is a retrospective record. The run closed at 2026-09-04T07:34:05Z with its Closure Gate approved and no change proposal in existence, so Completion Rule `C-6` was unsatisfied for roughly eight hours and the Closure Gate decided without the artifact the profile requires. Nothing in this record was available to that decision | omn-orchestrator | Closed for the accounting, open as a process fact. The record now exists; the gap between closure and record cannot be repaired retrospectively and is stated rather than smoothed. The repair is procedural: a run carrying a framework change should not reach its Closure Gate without its proposal drafted |
| `O-002` | Three framework runs inside the self-hosted window still carry no change proposal — `run-34ca35504b72` (2026-08-27T12:50:39Z), `run-e0dba6763475` (2026-09-03T11:34:17Z) and `run-efe092286625` (2026-08-27T13:14:08Z) — so `S8` still fails at this authoring instant. This proposal accounts for `run-8f8a1ab0d16e` only; writing proposals for runs this author did not carry would falsify the record | omn-orchestrator | Open, pre-existing, inherited as `O-001` of `FC-007` where the set was four. Sibling proposals for all three are reported as being authored in parallel; `S8` clears only when every one is in place, and this record cannot assert that they are |
| `O-003` | `omn-orchestrator` is the contracted producer of this artifact, yet its manifest permits no repository write in any phase. This instance was authored by `omn-orchestrator` under an explicit operator authorization scoped to exactly this one file; the standing contradiction is tracked since `O-003` of `FC-005` and `O-006` of `FC-006` and `FC-007` | omn-tech-lead | Open, unchanged; resolve by either narrowing the producer list in the artifact contract or widening the manifest's write scope for this artifact alone |
| `O-004` | Executing the framework's own proofs drifts tracked run evidence. `verify_recovery.py` injects runs under `runs/` and, although it reports removing them, tracked evidence of `run-34ca35504b72` carries uncommitted modifications produced by executions of it in this window, and an injected run was briefly counted by `S8` mid-window before cleanup. `verify_multi_phase.py` appends replay bookkeeping to a tracked run's state file, which is why `FR-11` above is accepted rather than executed | omn-tech-lead | Open, unmitigated, and not repaired here: restoring committed content is a repository write outside this authoring session's single-file authorization, and concurrent authoring sessions were operating on the same tree. Grown from `O-003` of `FC-007`, which recorded the hazard for the multi-phase proof only; the recovery proof exhibits it too. Executors must check the version-control state of run evidence after either proof and restore committed content |
| `O-005` | The `Recorded Framework Changes` index in `config/self-hosting-profile.md` carries no `FC-010` row. Adding it is a framework-internal edit under `SR-1`, outside the single-file write this session was authorized to make; the index is a directory rather than an authority, since `verify_self_hosting.py` discovers proposals by glob, so its absence blocks nothing | operator | Open; append the row with the next routed framework change or as operator housekeeping. Inherited from `O-005` of `FC-007`, which remains open for `FC-007` itself |
| `O-006` | The delivered gate is not yet in force and its live behaviour is unobserved. `CR-001` and `CR-002` are open low corrections owned by omn-dev-1-implement; `Q-001` (first live hosted runs confirming matrix fan-out, rendered check names, fan-in fail-never-skip under real failure and cancellation, and both platforms' results) is owned by omn-qa; `Q-002` (whether the default branch is literally the name the push trigger encodes) and `Q-003` (who enacts the day-one required set and the flip, and where the flip is recorded) are owned by omn-tech-lead; and the flip additionally waits on the externally owned orphan cleanup that decision record D-003 makes its precondition | omn-tech-lead | Open at closure and carried forward by the Closure Gate's logged follow-ups and by `K-001` to `K-006` of RN-2026-0005-CKA-03. Until `Q-003` is enacted, no check blocks a merge at all and the documented staged rollout is not yet operative |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorized by the session operator for this one file, retrospectively and after the run it documents had closed
- Accepted by: omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, and omn-orchestrator at the Closure Gate as non-producing owner — every one of them recorded during the run at 2026-09-04, none of them on this proposal, which no gate has assessed
- Acceptance basis: all six phases of the routed workflow executed with artifacts accepted by their registered validators at 33/33, 45/45, 78/78, 32/32, 31/31 and 32/32; every gate decided by a human owner who did not produce the evidence it assesses, after the runtime had held the run blocked awaiting that decision; ten recovery-ledger entries all resolved, one of them a charged retry that repaired a design artifact rejected at `D8.3`, `D13.2` and `D16.4`; no critical or high escalation open at closure; and six open items recorded with owners, including that this record is retrospective, that `S8` does not yet clear, and that the delivered gate's live behaviour has still never been observed running
