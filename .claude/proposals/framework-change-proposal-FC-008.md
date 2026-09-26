# Framework Change Proposal: Declare the PyYAML Runtime Dependency and Make Installation Verification Report a Missing Runtime Import

```yaml
frameworkChangeProposal:
  proposalId: FC-008
  changeClass: capability-addition
  routedCommand: implement
  routedWorkflow: implement-feature
  runId: run-efe092286625
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: omn-orchestrator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-008
- Change title: Declare `pyyaml>=6` as a distribution dependency, correct the false standard-library-only claim in both documentation surfaces, and extend `validate`/`doctor` with static module-top-level import resolution reporting the new `V-IMPORT` finding
- Change class: capability-addition
- Routed command: `/implement`
- Run identifier: run-efe092286625
- Authored on: 2026-09-04

## Authoring Baseline

- Authored at: 2026-09-04T15:47:10Z
- Runtime version: 0.5.0
- Dispatchable phases framework-wide: 37 of 37
- Routed workflow dispatchable phases: `scope-and-acceptance`, `execution-planning`, `solution-design-and-risk-assessment`, `implementation`, `quality-review`, `documentation-and-release-handoff`

This is a **retrospective record**. The run it documents opened 2026-08-27T13:14:08Z and closed at
its Closure Gate on 2026-08-28T06:30:06Z; this proposal was authored eight days later, on
2026-09-04, in a session whose only authorized write is this file. It is not a closure-time
account, and nothing in it was written while the run was live. Every claim below is reconstructed
from the run evidence the runtime persisted under `.claude/runs/run-efe092286625/`, plus the
verifier output executed at the instant recorded above. Where the record does not establish
something, this proposal says so rather than filling the gap.

## Change Statement

- Objective: make a fresh installation of the `omn-agent` CLI actually run, make its published dependency claim true, and make its own installation health verification report a broken installation instead of certifying it. Before this change the installed runtime files imported a third-party YAML library at module top level, `pyproject.toml` declared `dependencies = []`, `README.md` line 10 claimed the tool was "standard library only", and `omn_agent/validator.py::_check_python` only `compile()`d the installed files without resolving their imports — so a clean install produced a dead runtime that the install, the documentation, and `doctor` all called healthy. Ticket CKA-01, Epic A of the adoption backlog under `docs/`, carrying recommendation R1 of the adoption review dated 2026-08-27.
- In scope: the five-entry change set `C-001` to `C-005` recorded by implementation report IR-2026-0003 — a static module-top-level import-resolution step added inside the existing per-file verification helper on the shared `run_validation` path, emitting one stable `V-IMPORT` ERROR finding naming the checked file, the unresolved module root and the checking interpreter, with a hint naming the providing distribution where known (`omn_agent/validator.py`); the `pyyaml>=6` entry in the distribution's dependency metadata (`pyproject.toml`); the corrected dependency-footprint claim in `README.md` and in the HTML handbook `docs/user-guide.html`; and seven added tests pinning the detection behaviour, its boundedness, the hint content, and the agreement of the packaging metadata with both documentation surfaces (`tests/test_omn_agent.py`).
- Out of scope: automatic remediation of a missing dependency (scope exclusion `X-003`); detection below module top level — function-local, conditional, dynamic and transitive imports — bounded by scope decision `D-001` and exclusion `X-002`; declaring any runtime dependency other than PyYAML (`X-001`); CI gating and the work of adoption tickets CKA-02 and CKA-03 (`X-004`); and every gate-decision surface — `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, and every human-block path — forbidden outright by the ticket's additive-check-only constraint and recorded as exclusion `X-005`. `docs/USER-GUIDE.md` was deliberately left unchanged: it carries no false claim, and the design named only the README and the HTML handbook as documentation modules.
- Acceptance basis: eight measurable acceptance criteria in scope definition SCOPE-2026-0001, `A-001` to `A-008`, of which `A-001`, `A-004` and `A-007` reproduce the ticket's three verbatim criteria. The Verification Gate recorded `A-001` met by a clean-venv install resolving pyyaml-6.0.3; `A-004` and `A-005` met by `doctor` and `validate` in a dependency-absent environment exiting 3 with `V-IMPORT` findings naming `yaml` and carrying an install hint; and `A-007` met by targeted 29-test re-runs green against a 272-test collection matching the recorded full-suite pass. `A-002`, `A-003` and `A-006` rest on static test `T-006`, the reviewer's full read of both documentation surfaces, and a 22-test healthy-path slice. `A-008` was accepted with one attributed exception: `verify_self_hosting.py` check `S8`, failing on three pre-existing unaccounted runs plus this run itself, which omn-qa recorded as not attributable to CKA-01 and routed to omn-tech-lead.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `omn_agent/validator.py` | none | out-of-scope | The changed code module; the classifier returns "no scope rule matches; the path is outside the framework surface" |
| `pyproject.toml` | none | out-of-scope | Distribution metadata gaining its first dependency entry; no scope rule matches |
| `README.md` | none | out-of-scope | Repository-root README; `SR-2` names only `decision-matrix.md`, `quality-gates.md`, `rule-engine.md` and `working-memory.md`, so this file is not one of the four in-scope root documents |
| `docs/user-guide.html` | none | out-of-scope | HTML handbook aligned with the corrected claim; no scope rule matches |
| `tests/test_omn_agent.py` | none | out-of-scope | The seven added tests; no scope rule matches |
| `.claude/runs/run-efe092286625/**` | `SR-3` | out-of-scope | Run evidence written by the runtime while the change was carried |
| `.claude/proposals/framework-change-proposal-FC-008.md` | `SR-5` | out-of-scope | This proposal: the governance record of the run, not a second change |

Every row was recomputed with `python .claude/runtime/self_hosting.py classify --path <path>` at the
authoring instant, and **no delivered path is in scope**. Under the profile's Scope Rule this change
is therefore not framework-internal: the `omn-agent` CLI package, its packaging metadata, its
documentation and its tests all sit outside the inclusion set `SR-1` (`.claude/**`) and `SR-2` (the
four named root governance documents). The proposal exists anyway because `S8` of
`verify_self_hosting.py` counts every run under `runs/` inside the self-hosted window, and this run
is one. That mismatch between the Scope Rule and the `S8` window is recorded as open item `O-002`
rather than papered over by claiming an inclusion the classifier refuses.

## Routing Decision

- Change class: capability-addition
- Selector satisfied by: the framework's own installation-verification capability gained behaviour it did not have — `validate` and `doctor` now resolve the module-top-level imports of installed runtime files and report a stable `V-IMPORT` ERROR naming an unresolvable module, where previously they compiled the files and certified a dead runtime as healthy; and the distribution's install contract changed, gaining its first declared dependency. The narrower `structure-preserving-change` claim is not defensible: the externally observable finding vocabulary and the install contract both changed
- Command: `/implement`
- Primary workflow: implement-feature
- Entry phase: `scope-and-acceptance`
- Required inputs supplied: `feature-request`
- Routing evidence: `python .claude/runtime/self_hosting.py route --intent capability-addition` resolves to `/implement` over `implement-feature` v1.0.0 at entry phase `scope-and-acceptance`, which is exactly what `runs/run-efe092286625/execution-request.json` records. The profile's Required Inputs column lists four types for this class; the run was submitted with one, `feature-request` at `runs/inputs/cka-01-feature-request.md`, and `G5-INPUT` passed on every phase because each owning agent's input contract is a menu contract requiring none of them by name. The run record carries no separate Scope Rule classification step performed before the work began, so profile condition `C-1` is evidenced here by the execution request and by the recomputation above, not by a recorded pre-work classification

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-efe092286625/execution-request.json` | resolved; `command_id` is `implement`, `workflow_id` is `implement-feature`, runtime 0.5.0, submitted 2026-08-27T13:14:08Z, one input recorded with digest: `feature-request` at `runs/inputs/cka-01-feature-request.md` |
| `E-2` | `runs/run-efe092286625/run-ledger.json` | resolved |
| `E-3` | `runs/run-efe092286625/events.jsonl` | resolved; 91 canonical events, including every validation rejection and the retry each one scheduled |
| `E-4` | `runs/run-efe092286625/state.json` | resolved; `run_status` Completed, six phases all completed, none blocked at close, and all six gate decisions recorded with owner role, decider and rationale |
| `E-5` | `runs/run-efe092286625/completion-package.md` | resolved; 6 of 6 phases completed, 52 transitions, 10 replays suppressed, open escalations none |
| `E-6` | `runs/run-efe092286625/states/implementation/artifacts/implementation-report.md` | resolved; each of the six phases committed its contracted artifact, including the release note at `states/documentation-and-release-handoff/artifacts/release-note.md` |
| `E-7` | `runs/run-efe092286625/states/implementation/validation-report.json` | resolved; a validation report exists for each of the six executed phases, every one recording `pass` |

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `scope-and-acceptance` | `omn-product-owner` | completed | Executed over two charged attempts; scope definition SCOPE-2026-0001 with 4 in-scope items, 5 exclusions, 8 acceptance criteria, 3 scope decisions, 0 open questions, verdict `bounded`, Validation Engine 33/33. Attempt 1 was rejected with 1 blocking failure at `C3.2`, the vendor-token scan firing on a filename citation; corrected with no semantic change and re-completed | host-dispatched `omn-product-owner` subagent | `runs/run-efe092286625/states/scope-and-acceptance/validation-report.json` |
| `execution-planning` | `planner` | completed | Executed in one attempt; execution plan of 7 tasks over 4 waves with 10 dependency edges, 3 assumptions, 7 risks, 0 open questions, Validation Engine 45/45 | host-dispatched `planner` subagent | `runs/run-efe092286625/states/execution-planning/validation-report.json` |
| `solution-design-and-risk-assessment` | `architect` | completed | Executed over three charged attempts, the full budget; technical design with 18 facts, 9 constraints, 8 impacted modules, 6 options, 3 decisions (`D-001` detection, `D-002` provisioning, `D-003` finding shape), 2 decision records, 6 risks and 2 non-blocking open decisions, Validation Engine 78/78. Attempt 1 rejected with 6 blocking and 2 correctable failures (`D8.3`, `D9.2`, `D11.5`, `D15.2`, `D16.1`, `D16.4`, `D17.1`, `D17.7`); attempt 2 rejected with 2 blocking (`D8.2`, `D8.4`); attempt 3 accepted | host-dispatched `architect` subagent | `runs/run-efe092286625/states/solution-design-and-risk-assessment/validation-report.json` |
| `implementation` | `omn-dev-1-implement` | completed | Executed in one attempt; implementation report IR-2026-0003 with a 5-entry change set, 7 test-evidence entries, 1 recorded deviation (`V-001`, sibling resolution accepting a package directory), 3 residual risks and 1 non-blocking open question, Validation Engine 32/32. Report status `provisional`, verification status `partially-verified` | host-dispatched `omn-dev-1-implement` subagent | `runs/run-efe092286625/states/implementation/validation-report.json` |
| `quality-review` | `omn-dev-2-reviewer` | completed | Executed in one attempt; review package RP-2026-0002, verdict `approve-with-corrections`, 1 low finding (`F-001`, an uncovered exception guard) with 1 non-blocking correction request, 1 open question, Validation Engine 31/31. The reviewer re-executed the 7 targeted tests and a 22-test healthy-path slice, and independently confirmed the 272-test collection count | host-dispatched `omn-dev-2-reviewer` subagent | `runs/run-efe092286625/states/quality-review/validation-report.json` |
| `documentation-and-release-handoff` | `omn-documentation` | completed | Executed over two charged attempts; release note RN-CKA-01-run-efe092286625 at version `0+CKA-01-unreleased`, verdict `released`, 6 known issues, Validation Engine 32/32. Attempt 1 rejected with 0 blocking and 1 correctable failure at `R7`; corrected and re-completed | host-dispatched `omn-documentation` subagent | `runs/run-efe092286625/states/documentation-and-release-handoff/validation-report.json` |

Every phase of the routed workflow executed with a validated artifact and none blocked at close;
the run recorded 52 transitions and reached `run_completed` twice, once when the last phase
committed and once when the Closure Gate landed. Four attempts were charged to rejections across
three phases — one at `scope-and-acceptance`, two at `solution-design-and-risk-assessment`, one at
`documentation-and-release-handoff` — and the design phase consumed its full budget of three
attempts. Three phases were additionally held `blocked` mid-run awaiting an upstream gate decision
(`solution-design-and-risk-assessment`, `implementation`, `documentation-and-release-handoff`);
each block cleared when its gate was decided, and none was blocked at close.

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Scope Gate | approve | omn-business-analyst | `human:omn-business-analyst subagent a528e0d0ac83d4643, recorded by session operator for vuhoangcao` | All scope items trace to CKA-01; the three verbatim acceptance criteria survive as `A-001`/`A-004`/`A-007`; exclusions reproduce the additive-only constraint and fence off CKA-02 and CKA-03; no open questions. The attempt-1 failure was a mechanical vendor-string scan on a filename citation, corrected with no semantic change. `omn-product-owner` produced the evidence and is excluded from deciding |
| Planning Gate | approve | omn-tech-lead | `human:omn-tech-lead subagent ad4e278f1dd461c30, recorded by session operator for vuhoangcao` | The breakdown covers all four scope items and eight criteria with traceability and no invented work; the dependency graph is acyclic and executable as one small change; every plan assumption was verified against `pyproject.toml`, `README.md` line 10 and `validator.py::_check_python`; verification steps prove every acceptance criterion. One non-blocking condition: pin the exact unittest invocation in the `T-006` evidence. `planner` produced the evidence and is excluded from deciding |
| Design Gate | approve | omn-tech-lead | `human:omn-tech-lead subagent ad4e278f1dd461c30, recorded by session operator for vuhoangcao` | Selected approach `O-001` plus provisioning `D-002` covers every deliverable and criterion across four touched modules; the forbidden-path claim was verified by symbol search of `validator.py`; implementability facts were re-verified against source. Carry-forward: resolve the open version-range question `Q-001` as `pyyaml>=6` at `T-001`; `T-006` must not assert a finding for `verify_vertical_slice.py`; decision records `D-001` and `D-002` move to Accepted with this decision. `architect` produced the evidence and is excluded from deciding |
| Review Gate | approve | omn-qa | `human:omn-qa subagent a30a032dd42ad17af, recorded by session operator for vuhoangcao` | The review package's evidence reproduced under independent re-execution; the single low finding `F-001` is an evidence gap, not a behaviour defect, and its correction request `CR-001` was satisfied by an executed hermetic demonstration; the `approve-with-corrections` verdict follows the package's own adjudication; producer exclusion held, `omn-dev-2-reviewer` having produced the evidence |
| Verification Gate | approve | omn-qa | `human:omn-qa subagent a30a032dd42ad17af, recorded by session operator for vuhoangcao` | All three verbatim acceptance criteria met on executed evidence: a clean-venv `pip install` pulled pyyaml-6.0.3; `doctor` and `validate` in a dependency-absent environment exit 3 with `V-IMPORT` findings naming `yaml` and an install hint; targeted 29-test re-runs green with a 272-test collection matching the recorded full-suite pass. Healthy-path silence held. Proof scripts green except `verify_self_hosting.py` `S8`, failing on three pre-existing 2026-08-27 unaccounted runs plus this expected in-flight run — not attributable to CKA-01, routed to omn-tech-lead |
| Closure Gate | approve | omn-orchestrator | `human:omn-orchestrator subagent a1a27250a26d1ea84, recorded by session operator for vuhoangcao` | The release note faithfully accounts for change set `C-001` to `C-005` with known limitations owned and tracked; all six phases validated pass and all five prior gates carry recorded approvals; the only open finding is low `F-001` with an executed-evidence disposition; remaining items were routed outside the run with named owners. Merge and release judgement stays with omn-tech-lead. `omn-documentation` produced the evidence and is excluded from deciding |

Every gate the workflow declares was decided, none was waived, and each decision names an owner who
did not produce the evidence it assesses. Each gate first blocked at `G6-GATE-EVIDENCE` with
`awaiting_human_decision`, and each block was resolved in place; the six failure envelopes under
`runs/run-efe092286625/gates/` all read `status: resolved`, and the Decided By column above quotes
their `resolved_by` strings verbatim. The Scope Gate held the run 15h 8m 43s between its evidence
completing and the decision landing; no other gate held it longer than eleven minutes.

## Verification

| Check | Command | Result |
|---|---|---|
| Registry coverage | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6 COVERED — 37 of 37 phases dispatchable, 29/29 gate references decidable under the Producer Exclusion Rule, 105/105 phase skill references resolved |
| Validator coverage and decisiveness | `python .claude/runtime/verify_validators.py` | pass; 6/6 COVERED |
| Recovery behaviour | `python .claude/runtime/verify_recovery.py` | pass; 41/41 RECOVERY PROVEN. A first execution in this session aborted reading an injected run's failure envelope while other verifier executions were running concurrently against the same `runs/` directory; the clean re-execution is the recorded result and the abort is a concurrency artefact of this authoring session, not a recovery finding |
| Committed evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN |
| Self-hosting governance | `python .claude/runtime/verify_self_hosting.py` | 7/8 at the authoring instant: `S1` to `S7` pass, with all seven recorded proposals validating 38/38 and every named run satisfying the Completion Rule. `S8` fails, listing six unaccounted runs — the four pre-existing ones of `O-001` in `FC-007`, including this run, plus two transient runs injected minutes earlier by concurrent `verify_recovery.py` executions. This proposal removes this run's row on the next execution |
| Scope classification recomputes | `python .claude/runtime/self_hosting.py classify --path omn_agent/validator.py` (and each of the other four delivered paths) | pass; all five return out-of-scope with no matching rule, agreeing with the Scope Classification table above and with open item `O-002` |
| Routing resolves | `python .claude/runtime/self_hosting.py route --intent capability-addition` | pass; resolves to `/implement` over `implement-feature` v1.0.0 at `scope-and-acceptance`, agreeing with the run's execution request |
| Delivered change: test suite and acceptance demonstrations | inspection | recorded at the Review and Verification Gates rather than re-executed at closure. The implementer recorded a 265-test pre-change baseline, a pre-change failing witness (4 failures, 1 error on the 7 new tests) and a 272-test post-change pass; the reviewer independently re-executed the 7 targeted tests and a 22-test healthy-path slice and confirmed the 272 collection count; omn-qa recorded the clean-venv install and dependency-absent `doctor`/`validate` demonstrations at the Verification Gate. This record takes those verdicts as the recorded facts they are, and does not re-run the delivered change's suite |
| Multi-phase state machine | inspection | deliberately not re-executed. `verify_multi_phase.py` appends replay bookkeeping to committed run evidence, and modifying committed run evidence is prohibited to this role; the constraint is carried as open item `O-009` and the checklist item as `FR-11` |

## Risk and Rollback

- Blast radius: five files, none of them inside the framework surface the profile governs — `omn_agent/validator.py`, `pyproject.toml`, `README.md`, `docs/user-guide.html` and `tests/test_omn_agent.py`. No framework runtime module, workflow specification, registry record, agent manifest, artifact template, registered validator, gate-decision surface or CI configuration changed. The additive-only boundary was verified by symbol search: `record_gate_decision`, `_require_approval`, producer-exclusion and human-block symbols occur only in `omn_agent/runner.py`, `omn_agent/update.py`, `omn_agent/quality_scan.py` and `omn_agent/fix_comments.py`, none of which the change set touches. The reviewer recorded one examination limit: the working tree carried no version-control history at review time, so the five-file claim rests on the implementer's declared side effects plus content inspection of the modules the design required unchanged, not on a diff.
- Risk assessment: the externally visible surface moved twice, and both moves are recorded rather than absorbed. The distribution's install contract gains its first dependency, ending its zero-dependency status, so restricted or offline installs must now source one further distribution — implementation risk `R-003`, release-note issue `K-006`, with the unpinned lower bound's supply-chain exposure carried as design risk `R-006` owned by omn-tech-lead. The report vocabulary gains one ERROR finding code, so an environment that prior verification certified healthy while missing a module-top-level import now receives a non-OK exit; the release note records this as the delivered intent of scope item `S-003`, not a regression. Detection is deliberately bounded and stays blind below module top level and outside the descriptor-named file set (design risk `R-004`, release-note `K-002`), accepted at the Design Gate. The primary detection hazard is the opposite failure — a false `V-IMPORT` on a healthy install (design risk `R-001`) — held down by executed healthy-path negatives and by deviation `V-001`, which the reviewer assessed as narrowing rather than widening that exposure. One evidence gap remains open: the exception guard converting a raising environment lookup into a finding is verified by inspection only (`F-001`/`CR-001`/`K-001`), and an operator running verification from a different interpreter than the one executing the installed runtime still gets an answer about the wrong environment (`R-002`/`K-003`, recorded unmitigated).
- Rollback procedure: remove the import-resolution step and its finding code from `omn_agent/validator.py`, returning that helper to compile-only behaviour; remove the `pyyaml>=6` entry from `pyproject.toml`; revert the corrected footprint wording in `README.md` and `docs/user-guide.html`; and remove the seven added tests. No stored state, artifact schema, bootstrap descriptor schema or gate behaviour exists to unwind, and already-installed environments are untouched by the reversal. The condition that would justify it, stated in the release note's rollback criteria, is a healthy installation beginning to report `V-IMPORT` findings, since the healthy path is required to stay silent. Reverting invalidates no other run's evidence: `runs/run-efe092286625/` remains a valid record of a delivered-then-reverted change, and this proposal remains its governance record.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6 COVERED; 37 of 37 phases dispatchable, 29/29 gate references decidable, 105/105 skill references resolved |
| `FR-02` | Validator coverage and decisiveness | pass | 6/6 COVERED |
| `FR-03` | Recovery behaviour | pass | 41/41 RECOVERY PROVEN on the clean execution recorded in Verification |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN |
| `FR-05` | Self-hosting governance resolves | accepted | 7/8 at the authoring instant. `S1` to `S7` pass: the profile parses, all 7 routing rows resolve, the change-proposal contract is registered, all 7 recorded proposals validate 38/38, and every named run satisfies the Completion Rule. `S8` fails, and its residual is exactly the backlog this proposal is part of closing — open item `O-001` of `FC-007` records four framework runs carrying no proposal, of which this proposal accounts for one, `run-efe092286625`. Recording `pass` here would be unsupported: `S8` is red at this instant and stays red until the remaining runs are accounted for, one proposal per run. Accepted on that basis, with the residual tracked as `O-003` |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-efe092286625` is an `/implement` run over `implement-feature`, the command and workflow the profile routes `capability-addition` to, and this proposal links its run artifacts as `E-1` to `E-7`. Caveat, stated rather than omitted: the profile's Scope Rule does not classify this change framework-internal, so what the run demonstrates is that the framework carried and gated the change, not that the profile selected it — `O-002` |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Stays 0.5.0, the version recorded in both the execution request and the current runtime. No file under the framework runtime changed; the change set touches the CLI package, its packaging metadata, its documentation and its tests |
| `FR-08` | Documentation matches delivered behaviour | pass | `README.md` and `docs/user-guide.html` were corrected as part of the delivery and their agreement with the declared dependency is pinned by static test `T-006` and confirmed by the reviewer's full read; the handbook's troubleshooting table maps the new finding to its remedy. The framework runtime README and the repository folder descriptions are untouched and unaffected. `docs/USER-GUIDE.md` carries no false claim and was deliberately left unchanged; the symmetry suggestion is recorded as `O-007` rather than silently dropped |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | Every capability claim is backed by executed evidence under `runs/run-efe092286625/`: the implementer's baseline, failing witness and post-change suite; the reviewer's independent re-execution of the targeted tests, a healthy-path slice and the collection count; and omn-qa's clean-venv install and dependency-absent `doctor`/`validate` demonstrations recorded in the Verification Gate rationale. The remaining gaps are recorded, not omitted: the uncovered exception guard (`F-001`/`CR-001`/`K-001`) and the bounded-detection blind spot (`R-004`/`K-002`). One record-level inconsistency is carried as `O-004` |
| `FR-10` | Rollback stated | pass | Risk and Rollback above: a five-file revert with the trigger condition named from the release note's rollback criteria, and the statement that reverting invalidates no other run's evidence |
| `FR-11` | Multi-phase state machine still proves out | accepted | Advisory item, not re-executed at this authoring. `verify_multi_phase.py` appends replay bookkeeping to committed run evidence, and this role may not modify committed run evidence; the same constraint was accepted at `FC-007` `FR-11` and its `O-003`. Carried here as `O-009`; the run's own Verification Gate recorded the proof scripts green apart from the attributed `S8` exception |
| `FR-12` | Release note where consumer-visible behaviour changed | pass | `runs/run-efe092286625/states/documentation-and-release-handoff/artifacts/release-note.md`, version `0+CKA-01-unreleased`, verdict `released`, 6 known issues, Validation Engine 32/32 |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | This proposal is a retrospective record. The run closed at its Closure Gate on 2026-08-28T06:30:06Z; this account was authored on 2026-09-04, eight days later, by a role that took no part in the run and reconstructed it entirely from persisted evidence. It carries none of the contemporaneity a closure-time record has, and no phase or gate of the run assessed it | omn-orchestrator | Recorded, not resolvable. Authored under an explicit operator authorization scoped to this one file, to close this run's `S8` accounting under `O-001` of `FC-007`; future changes should carry their proposal at closure rather than after it |
| `O-002` | The profile's Scope Rule does not classify this change framework-internal — all five delivered paths return out-of-scope with no matching rule — yet `S8` counts the run and demands a proposal for it. The CLI package, its packaging metadata and its documentation are framework tooling that the inclusion set `SR-1`/`SR-2` does not reach | omn-tech-lead | Open. Resolve by either widening the inclusion set to the CLI distribution and its packaging surface, or narrowing the `S8` window to runs whose change the Scope Rule classifies framework-internal. Until then, a run like this one is governed by the Evidence Rule without being selected by the Scope Rule |
| `O-003` | Three framework runs inside the self-hosted window remain unaccounted at the authoring instant — `run-34ca35504b72` (2026-08-27T12:50:39Z), `run-e0dba6763475` (2026-09-03T11:34:17Z) and `run-8f8a1ab0d16e` (2026-09-04T05:50:51Z) — so `S8` stays red after this proposal lands. Two further rows in the same listing are transient runs injected by concurrent `verify_recovery.py` executions, which that verifier removes on completion | omn-orchestrator | Open, pre-existing, inherited from `O-001` of `FC-007`. Closing it requires one proposal per run, authored against each run's own evidence; fabricating a proposal for a run this change did not carry would falsify the record |
| `O-004` | Known issue `K-004` of the release note states the two P-005 acceptance demonstrations were not executed, but the Verification Gate decision recorded twelve minutes earlier states they were, with results (pyyaml-6.0.3 resolved in a clean venv; exit 3 with `V-IMPORT` naming `yaml`). The release note says as much itself: the gate record was not among its inputs. A reader of the note alone will understate what was demonstrated | omn-documentation | Open. The gate decision in `runs/run-efe092286625/state.json` is the later and more complete record; reconcile the note's known-issue row against it, or record the gate decision as an input the closure phase must receive |
| `O-005` | Decision records `D-001` and `D-002` still read `Status: Proposed` with unsigned approval lines, although the Design Gate's recorded rationale moved both to Accepted on 2026-08-28. A reader of the committed design record sees a status contradicting the recorded gate decision | architect | Open, non-blocking, raised as `Q-001` of review package RP-2026-0002 and carried as release-note `K-005`. No runtime behaviour depends on it; neither the implementer nor the reviewer may modify committed run evidence, which is why it is still open |
| `O-006` | The exception guard in `_import_resolves` that converts a raising environment lookup into a `V-IMPORT` finding rather than an escaping exception is exercised by no executed test; it is verified by inspection only | omn-qa | Open, non-blocking. Finding `F-001`, correction request `CR-001`, release-note `K-001`. The Review Gate recorded `CR-001` as satisfied by an executed hermetic demonstration; the durable regression check is still owed |
| `O-007` | `docs/USER-GUIDE.md` section 2 carries no false claim but does not state the PyYAML footprint, so the markdown guide and the HTML handbook now differ in what they say about the tool's dependencies | omn-documentation | Open, deliberate. Excluded from the change by the design's module set and recorded in the implementation report's handoff notes and the release note's support handoff notes as a proposed correction for the role owning the file |
| `O-008` | The `Recorded Framework Changes` index in `config/self-hosting-profile.md` carries no row for this proposal. Adding one is a framework-internal edit under `SR-1`, outside the single-file write this session was authorized to make | operator | Open. The index is a directory, not an authority — `verify_self_hosting.py` discovers proposals by glob, so the absent row blocks nothing. Append it with the next routed framework change or as operator housekeeping |
| `O-009` | `runtime/verify_multi_phase.py` appends replay bookkeeping to committed run evidence when executed, so running the definition-of-done proof drifts tracked run evidence without any agent editing it. `FR-11` was therefore recorded `accepted` here rather than executed | omn-tech-lead | Open, unmitigated, unchanged since `O-003` of `FC-007`. Executors must check the version-control state of run evidence after the proof and restore committed content |
| `O-010` | `omn-orchestrator` is the contracted producer of this artifact, yet its manifest permits no repository write in any phase. This instance was authored by `omn-orchestrator` under an explicit operator authorization scoped to exactly this one file | omn-tech-lead | Open, unchanged; tracked since `O-003` of `FC-005`, `O-006` of `FC-006` and `O-006` of `FC-007`. Resolve by either narrowing the producer list or widening the manifest's write scope for this artifact alone |

## Sign-off

- Proposed by: omn-orchestrator, under `config/self-hosting-profile.md` v1.0.0, authoring authorized by the session operator for exactly this one file, on 2026-09-04, eight days after the run closed
- Accepted by: the run's own recorded gate owners — omn-business-analyst at the Scope Gate, omn-tech-lead at the Planning and Design Gates, omn-qa at the Review and Verification Gates, and omn-orchestrator at the Closure Gate, each as a non-producing owner under the Producer Exclusion Rule. No separate acceptance of this retrospective record has been taken, and none is claimed here
- Acceptance basis: all six phases of the routed workflow executed with artifacts their registered validators accepted (33/33, 45/45, 78/78, 32/32, 31/31, 32/32), every gate decided by an owner who did not produce the evidence it assesses and each decision quoted from its resolved failure envelope, four charged retries recorded with the check identifiers each one repaired, every mandatory release-checklist item recorded with `FR-05` accepted rather than asserted, and ten open items recorded with owners — including the Scope Rule mismatch this run exposes and the three-run accounting residual this proposal does not close
