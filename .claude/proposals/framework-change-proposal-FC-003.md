# Framework Change Proposal: Make the Self-Hosting Surface Discoverable

```yaml
frameworkChangeProposal:
  proposalId: FC-003
  changeClass: structure-preserving-change
  routedCommand: refactor
  routedWorkflow: refactor
  runId: run-0db4765d0eab
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-003
- Change title: Make the self-hosting surface discoverable from the framework's own indexes
- Change class: structure-preserving-change
- Routed command: `/refactor`
- Run identifier: run-0db4765d0eab
- Authored on: 2026-08-18

## Change Statement

- Objective: let a reader arriving at the framework's entry points reach the self-hosting profile, the change-proposal contract, and the framework release checklist by following indexes, without knowing the file names first.
- In scope: seven human indexes, each gaining a pointer of the kind it already carries, plus the precedence statement recorded once beside the rule it qualifies.
- Out of scope: the profile itself, every machine index, and any rule change.
- Acceptance basis: every verifier reports the same counts as before the change, and no registry record, Phase Model, gate row, or agent contract is touched.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/README.md` | `SR-1` | in-scope | Top-level entry index: folder list, layered responsibilities, contributor usage |
| `.claude/config/README.md` | `SR-1` | in-scope | Policy document index |
| `.claude/config/agent-routing.md` | `SR-1` | in-scope | The one place the precedence between the profile and intent routing is recorded |
| `.claude/commands/README.md` | `SR-1` | in-scope | Command contract index |
| `.claude/templates/template-catalog.md` | `SR-1` | in-scope | Controlled template index and its governance rules |
| `.claude/validation/README.md` | `SR-1` | in-scope | Validation and checklist index |
| `.claude/runtime/README.md` | `SR-1` | in-scope | Runtime current-state record: Files table, coverage table, known gaps |
| `.claude/runs/run-0db4765d0eab/state.json` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |

## Routing Decision

- Change class: structure-preserving-change
- Selector satisfied by: seven index documents gain references to surfaces that already exist; no contract, routing, or runtime behaviour changes
- Command: `/refactor`
- Primary workflow: refactor
- Entry phase: scope-invariants-and-risk-profile
- Required inputs supplied: `change-request`, `business-intent`, `architecture-context`

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-0db4765d0eab/execution-request.json` | `/refactor` over `refactor` v1.0.0, three inputs, submitted 2026-08-18T14:42:16Z |
| `E-2` | `runs/run-0db4765d0eab/run-ledger.json` | Run ledger written by the runtime at version 0.4.1 |
| `E-3` | `runs/run-0db4765d0eab/events.jsonl` | Ordered canonical events across both dispatch attempts and the gate decision |
| `E-4` | `runs/run-0db4765d0eab/state.json` | Five phases: one completed, four blocked with a recorded reason each |
| `E-5` | `runs/run-0db4765d0eab/completion-package.md` | Aggregated package: phase ledger, gate decisions, module provenance with digests |
| `E-6` | `runs/run-0db4765d0eab/states/scope-invariants-and-risk-profile/artifacts/technical-design.md` | 13-section design selecting `O-001` over three alternatives, with one decision record at Proposed |
| `E-7` | `runs/run-0db4765d0eab/states/scope-invariants-and-risk-profile/validation-report.json` | `design_validator.py` PASS, 78/78, 10 not machine-checkable, on attempt 2 |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-invariants-and-risk-profile` | `architect` | completed | Executed by the registered agent. Attempt 1 was rejected on `D12.3`, a risk class outside the declared vocabulary; the failure classified as retryable `output-schema-failure`, backed off 2.263s, and attempt 2 validated 78/78 | architect | `runs/run-0db4765d0eab/states/scope-invariants-and-risk-profile/failure-envelope.json` |
| `safety-net-establishment` | `omn-qa` | blocked | Blocked `awaiting_capability_registration`; the safety net for a documentation change is the four verifier commands the change request names as its baseline, recorded in Verification below | operator | this proposal, Verification section |
| `refactor-implementation` | `omn-dev-1-implement` | blocked | Blocked `awaiting_capability_registration`; the operator applied `M-001` through `M-007`, one pointer per index, in the design's sequencing order | operator | the seven files in Scope Classification |
| `behavioral-validation` | `omn-qa` | blocked | Blocked `awaiting_capability_registration`; parity established by re-running each baseline command and comparing counts, and by re-verifying every committed run after the frozen-slice member was edited | operator | this proposal, Verification section |
| `closure-and-debt-record` | `omn-orchestrator` | blocked | Blocked `awaiting_capability_registration`; closure is this proposal, and the debt delta is the two open items below | operator | `runs/run-0db4765d0eab/completion-package.md` |

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Invariant Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Design validated 78/78 after one retryable rejection and a repair pass; seven human indexes gain a pointer each, no machine index changes, so the structure-preserving claim holds. `architect` produced the evidence and is excluded from deciding |

The Implementation, Regression, and Closure Gates are recorded undecided in the completion package, because each assesses evidence a blocked phase never produced. No gate was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage unchanged | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6 checks, dispatchable 3 of 36, blocked 33, identical to the baseline |
| Validator coverage unchanged | `python .claude/runtime/verify_validators.py` | pass; 4/4 checks over 7 artifact types |
| Self-hosting governance unchanged | `python .claude/runtime/verify_self_hosting.py` | pass; S1 to S8 |
| Committed run evidence still verifies after a frozen-slice member was edited | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, and the same for `run-308f4d0ee447`, `run-b6780677468b`, and `run-3e22f11cb34d` |
| This run's own executed phase is provable by the slice verifier | `python .claude/runtime/verify_vertical_slice.py --run-id run-0db4765d0eab --slice architect` | fail; 5/10. The verifier looks for phase `solution-design-and-risk-assessment` and this run's architect phase is `scope-invariants-and-risk-profile`. A pre-existing limit of the proof script, recorded as `O-002`, not a defect in this change |
| No rule was added by an index | inspection | pass; every added passage points at an authority and states no rule of its own, except the precedence sentence in `config/agent-routing.md`, which records where an existing rule already yields |

## Risk and Rollback

- Blast radius: seven documentation files. No registry record, Phase Model, gate row, agent contract, or runtime module changes.
- Risk assessment: the design's `R-005` is the one that materialised. `runtime/README.md` is a member of the frozen context slice of every architect phase, and editing it moved the digest the in-flight design cited between its two attempts; the agent re-checked its facts against the new snapshot and recorded the movement rather than carrying a stale citation. The standing risk is drift: the same reference now lives in seven places, and nothing mechanical checks that they still agree with the profile.
- Rollback procedure: remove the added passage from each of the seven files. Nothing else was written outside run evidence. Reverting `runtime/README.md` moves its digest again, so the affected runs are re-verified after a rollback exactly as they were after the change.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6 checks, unresolved=0 |
| `FR-02` | Validator coverage and decisiveness | pass | 4/4 checks, 7 artifact types |
| `FR-03` | Recovery behaviour | pass | 41/41 checks across 3 injected runs |
| `FR-04` | Committed evidence still verifies | pass | Four runs re-verified 10/10 after the frozen-slice edit |
| `FR-05` | Self-hosting governance resolves | pass | `verify_self_hosting.py` S1 to S8 |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-0db4765d0eab` is a `/refactor` run; this proposal links its artifacts |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | No runtime module changed; version stays 0.4.1 |
| `FR-08` | Documentation matches delivered behaviour | pass | This change is that requirement: seven indexes now describe what exists, and `runtime/README.md` records what the mode does not yet support |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | New known gap 8 states that self-hosting decides the route and holds the record rather than executing most phases, with the dispatchable counts |
| `FR-10` | Rollback stated | pass | Risk and Rollback above; seven passages, and the re-verification obligation on one of them |
| `FR-11` | Multi-phase state machine still proves out | pass | `verify_multi_phase.py --run-id run-c5a8d50d3238` 15/15 PROVEN. Against this run it reports 14/15, because its `M6` looks for implement-feature phase names; the same limit as `O-002` |
| `FR-12` | Release note where consumer-visible behaviour changed | not-applicable | No behaviour changed. Every edit is a reference in a human index |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | The same reference now appears in seven indexes and nothing mechanical checks they still agree with the profile. A drift check is available: the profile is parseable and every reference names it | omn-documentation | Deferred; recorded as design risk and accepted at the Invariant Gate |
| `O-002` | `verify_vertical_slice.py` and `verify_multi_phase.py` recognise only implement-feature phase identifiers, so a refactor run's executed architect phase cannot be proven by either, even though the runtime accepted its artifact at 78/78 | omn-qa | Open; routes as `capability-addition` under the profile and is the next increment's work |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Invariant Gate, recorded by the operator
- Acceptance basis: the executed phase was validated by its registered validator, every baseline command reports its baseline counts, every committed run re-verified after the frozen-slice edit, and both open items are recorded with an owner and a route
