# Implementation Report: investigate and research hand each phase's artifact to the next

```yaml
implementationReport:
  reportId: IR-2026-1011
  changeReference: investigate-chain-input-contracts-defect-report / run-5d3c99aaaae1
  sourceInputs:
    - type: bug-analysis
      reference: runs/run-5d3c99aaaae1/states/triage-and-impact/artifacts/bug-analysis.md
    - type: bug-analysis
      reference: runs/run-5d3c99aaaae1/states/root-cause-analysis/artifacts/bug-analysis.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: fix-implementation
  verificationStatus: partially-verified
  inputDigest: sha256:2f35d56562119ffa7aa9b843912cfb2b
  contextDigest: sha256:ca90fe0d7fe9988b21eeb8702bf15cb6
```

## Metadata

- Report ID: IR-2026-1011
- Change reference: investigate-chain-input-contracts-defect-report / run-5d3c99aaaae1
- Workflow phase: fix-implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

## Implementation Summary

- Change intent: every phase of `investigate` and `research` now passes guard G5-INPUT once its predecessor's artifact is committed, with `problem-statement` as the only supplied input, and both self-hosting profile rows that route to these workflows name an entry type the entry agent accepts; an input type no consumer declares is still refused, and the seven hand-offs outside this repair still block exactly as before.
- Approach taken: declaration-only, per the root-cause analysis Fix Strategy as refined by the operator. No runtime module, validator, gate or template contract changed. The context agent's accepted menu gained `requirement-framing` additively and documentation's gained `technical-recommendation`; every surface stating either contract (minimum-satisfaction prose, contract module, lifecycle phase table, source-input vocabulary, report template comment, host registration, registry data dependencies) moved with it. Both agents move 1.0.0 to 1.1.0 in manifest, registry record and host registration with `contractVersion` held, following the earlier refactor-handoff repair. Tech-lead is unchanged: the `recommendation` and `recommendation-draft` Input cells also name `investigation-report.md`, so the Task Router derives one extra edge from discovery and routes the evidence base tech-lead already accepts; both workflows move 1.0.0 to 1.1.0 as an additive change. The two profile rows name `problem-statement`. One new test module was added at ladder rung 7, because no existing module composes a Phase Model edge with producer and consumer contracts (the refactor-handoff module covers one consumer only); it reuses the runtime's own loaders, guard functions and router and adds no dependency. The bundled payload was refreshed by its own sync command.
- Design reference: the finalized root-cause analysis `runs/run-5d3c99aaaae1/states/root-cause-analysis/artifacts/bug-analysis.md` (digest `sha256:e261befdea3413b2c786fdf766a4eaad`), Fix Strategy and Validation Plan, with the triage analysis (digest `sha256:88972d03e6aa522dbdd6ed395e89410b`) as context, and the operator directives of this invocation.
- Out of scope: the seven other blocked hand-offs (implement-feature execution-planning and solution-design-and-risk-assessment, fix-bug root-cause-analysis, review-pull-request structural-compliance and merge-decision, release artifact-packaging and communication-and-post-release) and the change-review and framework-release profile rows, held as known gaps by the new census tests; withdrawing `framed-objective` and `research-brief`, deferred by operator directive; the stalled run run-437e2f765e4b, which was read but never re-evaluated; the implementer host registration version drift; the stale build copy under `build/lib`, which the earlier repair also left alone; documentation's release-note source-input vocabulary, which never listed accepted inputs; any runtime, validator or gate change.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `<fw>/agents/omn-context-agent/manifest.yaml` | modified | Accept `requirement-framing` additively, restate minimum satisfaction, version 1.0.0 to 1.1.0 | root-cause Fix Strategy, context agent hand-off; `V-001` |
| `C-002` | `<fw>/agents/omn-context-agent/identity.md` | modified | Name the requirement framing in the required-input table and the business-analyst upstream row | root-cause Fix Strategy, identity text |
| `C-003` | `<fw>/agents/omn-context-agent/output.md` | modified | Add `requirement-framing` to the source-input type vocabulary | root-cause Fix Strategy, sourceInputs vocabulary |
| `C-004` | `<fw>/agents/omn-context-agent/execution.md` | modified | Context Loading and Phase Ownership name the requirement framing both phases consume | root-cause Fix Strategy, lifecycle text |
| `C-005` | `<fw>/agents/omn-context-agent.agent.md` | modified | Host registration version 1.1.0 twice; its question check names the requirement framing | root-cause Fix Strategy, host registration version |
| `C-006` | `<fw>/templates/investigation-report.md` | modified | Source-input type comment names `requirement-framing` | root-cause Fix Strategy, report template comment |
| `C-007` | `<fw>/agents/omn-documentation/manifest.yaml` | modified | Accept `technical-recommendation` for the two findings phases, restate minimum satisfaction, version 1.1.0 | root-cause Fix Strategy, documentation hand-off |
| `C-008` | `<fw>/agents/omn-documentation/identity.md` | modified | Required-input row and tech-lead upstream row for the recommendation the findings phases publish | root-cause Fix Strategy, identity text |
| `C-009` | `<fw>/agents/omn-documentation/execution.md` | modified | Context Loading names the recommendation; Phase Ownership names `technical-recommendation.md` for both findings phases | root-cause Fix Strategy, lifecycle table |
| `C-010` | `<fw>/agents/omn-documentation.agent.md` | modified | Host registration version 1.1.0 twice | root-cause Fix Strategy, host registration version |
| `C-011` | `<fw>/registry/agents.yaml` | modified | Both records at 1.1.0; data dependencies `requirement-framing` and `technical-recommendation` at ">=1.0.0 <2.0.0" | root-cause Fix Strategy, registry data dependencies |
| `C-012` | `<fw>/workflows/investigate.md` | modified | `recommendation` Input cell also names `investigation-report.md` | root-cause Fix Strategy, tech-lead Input column |
| `C-013` | `<fw>/workflows/research.md` | modified | `recommendation-draft` Input cell also names `investigation-report.md` | root-cause Fix Strategy, tech-lead Input column |
| `C-014` | `<fw>/registry/workflows.yaml` | modified | `investigate` and `research` move 1.0.0 to 1.1.0 with a one-line additive note | root-cause Fix Strategy, workflow versions |
| `C-015` | `<fw>/config/self-hosting-profile.md` | modified | decision-support and external-research rows name `problem-statement` | root-cause Fix Strategy, entry inputs; `V-002`, `V-003` |
| `C-016` | `tests/test_investigate_research_handoffs.py` | added | Twenty contract tests: both chains, six named hand-offs, Task Router edges, boundary pairs, profile routes, known-gap census, version agreement | root-cause Validation Plan, regression tests |
| `C-017` | `omn_agent/_bundled_payload/agents/omn-context-agent.agent.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-018` | `omn_agent/_bundled_payload/agents/omn-context-agent/execution.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-019` | `omn_agent/_bundled_payload/agents/omn-context-agent/identity.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-020` | `omn_agent/_bundled_payload/agents/omn-context-agent/manifest.yaml` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-021` | `omn_agent/_bundled_payload/agents/omn-context-agent/output.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-022` | `omn_agent/_bundled_payload/agents/omn-documentation.agent.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-023` | `omn_agent/_bundled_payload/agents/omn-documentation/execution.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-024` | `omn_agent/_bundled_payload/agents/omn-documentation/identity.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-025` | `omn_agent/_bundled_payload/agents/omn-documentation/manifest.yaml` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-026` | `omn_agent/_bundled_payload/config/self-hosting-profile.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-027` | `omn_agent/_bundled_payload/registry/agents.yaml` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-028` | `omn_agent/_bundled_payload/registry/workflows.yaml` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-029` | `omn_agent/_bundled_payload/templates/investigation-report.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-030` | `omn_agent/_bundled_payload/workflows/investigate.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |
| `C-031` | `omn_agent/_bundled_payload/workflows/research.md` | modified | Payload mirror refreshed by the sync command | root-cause Fix Strategy, bundled payload sync |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Witness: the new module run against a copy of the working tree taken before any edit reports all 20 tests failing (28 failures counting subtests, 0 errors, 0 passing) | regression | `C-001`, `C-005`, `C-007`, `C-010`, `C-011`, `C-012`, `C-013`, `C-014`, `C-015`, `C-016` | `python -m unittest tests.test_investigate_research_handoffs -v` in the pre-edit copy | pass |
| `T-002` | The new module on the repaired tree: both chains pass G5-INPUT at all five phases from `problem-statement` alone; the six named hand-offs carry the delivered identifier through narrowing; boundary pairs still refuse undeclared, optional-only and empty pools; census equals the seven known gaps and two profile rows; versions agree | contract | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013`, `C-014`, `C-015`, `C-016` | `python -m unittest tests.test_investigate_research_handoffs -v` | pass |
| `T-003` | Task Router: the dependency graph of every active workflow, before against after, differs only by the edge technical-discovery to recommendation, the edge technical-validation to recommendation-draft, and the two version strings; every edge stays hard | contract | `C-012`, `C-013`, `C-014` | inline scratch script calling `parse_phase_model` and `derive_dependencies` over both trees, outputs diffed | pass |
| `T-004` | Per-edge census over all 29 consecutive hand-offs with the runtime's own contract functions: blocked count falls from 13 to 7, and the 7 are exactly the out-of-scope edges | contract | `C-001`, `C-007`, `C-011`, `C-012`, `C-013` | inline scratch script over both trees using `derive_dependencies`, `narrow_inputs`, `resolve_input_contract` | pass |
| `T-005` | Scratch mirror of the repaired tree outside the repository: `plan`, `next`, `dispatch` and `gate` drive investigate and research from `problem-statement`; every phase passes G5-INPUT and each envelope supplies the expected identifier; plans with `investigation-request` or `research-question` still block at entry | end-to-end | `C-001`, `C-004`, `C-005`, `C-007`, `C-009`, `C-011`, `C-012`, `C-013`, `C-014`, `C-015` | `python <fw>/runtime/framework_runtime.py plan`, `next`, `dispatch`, `gate` in the mirror via a scratch driver | pass |
| `T-006` | The router names `problem-statement` for decision-support and external-research and reports workflow version 1.1.0 | contract | `C-014`, `C-015` | `python <fw>/runtime/self_hosting.py route --intent decision-support`; same for external-research | pass |
| `T-007` | Manifest, registry coverage and validator verifiers return full passes, as at baseline: 2/2, 8/8, 6/6 | static | `C-001`, `C-007`, `C-011`, `C-012`, `C-013`, `C-014` | `python <fw>/runtime/verify_manifests.py`; `verify_registry_coverage.py`; `verify_validators.py` | pass |
| `T-008` | Self-hosting verifier returns the same 6/8 verdict as baseline, S2 passing for every routing row; S7 and S8 fail on the same runs as before | static | `C-014`, `C-015` | `python <fw>/runtime/verify_self_hosting.py`, before and after | pass |
| `T-009` | The stalled run run-437e2f765e4b still loads pinned at investigate v1.0.0 with the same state table; multi-phase verifier without replay returns the same 13/15 as baseline; every file under runs other than this run's own is byte-identical before and after | regression | `C-001`, `C-007`, `C-011`, `C-012`, `C-014` | `python <fw>/runtime/framework_runtime.py status --run-id run-437e2f765e4b`; `python <fw>/runtime/verify_multi_phase.py --run-id run-437e2f765e4b --no-replay`; file digest comparison | pass |
| `T-010` | The payload mirror carries no drift after the sync; the refactor-handoff contract module still passes | regression | `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031` | `python tests/test_bundled_payload.py --sync`; `python -m unittest tests.test_bundled_payload tests.test_agent_input_contracts` | pass |
| `T-011` | Whole unit suite, baseline before any edit and again after | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013`, `C-014`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031` | `python tools/run_tests_parallel.py` | pass |

## Verification Results

- Verification method: a byte copy of the working tree was taken before any edit and the whole suite, the four verifiers, the stalled run's status and the per-edge census were recorded as the baseline. The new module was proven against that copy to fail in every test, then run on the repaired tree. The Task Router graph and census were diffed across both trees, and both chains were driven end to end in a throwaway mirror outside the repository with phase completion simulated in the mirror's own run record. Committed run evidence was digest-compared before and after every step.
- Commands executed: `python tools/run_tests_parallel.py` (before and after); `python -m unittest tests.test_investigate_research_handoffs -v` (pre-edit copy and repaired tree); `python -m unittest tests.test_bundled_payload tests.test_agent_input_contracts`; `python tests/test_bundled_payload.py --sync`; `python <fw>/runtime/verify_manifests.py`, `verify_registry_coverage.py`, `verify_validators.py`, `verify_self_hosting.py` (before and after); `python <fw>/runtime/verify_multi_phase.py --run-id run-437e2f765e4b --no-replay` (before and after); `python <fw>/runtime/framework_runtime.py status --run-id run-437e2f765e4b` (before and after); `python <fw>/runtime/self_hosting.py route --intent decision-support` and `--intent external-research`; mirror-only `plan`, `next`, `dispatch`, `gate`; scratch census and graph scripts; `git checkout` of the two run-c5a8d50d3238 files the suite rewrites, then `git status`.
- Result summary: 11 evidence entries executed, 11 passed, 0 failed. New module: 20 of 20 fail before, 20 of 20 pass after. Census: 13 of 29 blocked before, 7 after. Suite: 668 of 668 passed in 26 modules before; 688 of 688 passed in 27 modules after, the 20 added tests being the new module. Verifiers: 2/2, 8/8, 6/6 and 6/8 both before and after.
- Unverified areas: whether the real context, tech-lead and documentation agents accept the renamed inputs in their own first reasoning stage and whether their validators pass on real artifacts was not observed, because no model was invoked; the mirror used one-line stand-in artifacts. Gate auto-approval precedent after the version moves was not exercised.

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | `requirement-framing` was added beside `framed-objective` and `research-brief` instead of replacing them (`C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`); the analysis's negative tests for those two identifiers were not written | root-cause Fix Strategy, context agent accepts requirement-framing in place of the two producerless identifiers | Operator directive: removal narrows a contract and is left to a follow-up; both identifiers stay accepted and stay producerless | raised as `Q-001` to architect |
| `V-002` | The command specifications for `/investigate` and `/research` name prose inputs (an investigation or research question, decision owner, constraints), not the identifier the profile now names (`C-015`); they were not edited | operator directive to keep router, verifier, registry and command specifications consistent | The business analyst contract defines `problem-statement` as the question an investigate or research run is opened for, so the two agree in meaning; editing the command specifications would widen scope | raised as `Q-002` to omn-tech-lead |
| `V-003` | The self-hosting profile identity stays at version 1.0.0 although two Routing Table rows changed (`C-015`) | profile identity version | Neither the analysis nor the operator names a profile version move; no verifier or loader keys on it | raised as `Q-003` to omn-tech-lead |

## Boundary Compliance

- Module boundaries preserved: only declarations changed; the runtime's guard, narrowing, contract resolver, dependency derivation, validators and gates are byte-identical; the tech-lead manifest is untouched.
- Public interface changes: two agent contracts widen additively (context agent accepts `requirement-framing`, documentation accepts `technical-recommendation`), both agents and both workflows move to 1.1.0, two Input cells gain one artifact, two profile rows name `problem-statement`; no identifier was removed.
- Data or migration impact: none to data. Existing runs keep the workflow version they were planned at; run-437e2f765e4b still loads pinned at investigate v1.0.0 and was not re-evaluated.
- Declared side effects: the 31 change-set paths `C-001` to `C-031`, plus this report and `runs/run-5d3c99aaaae1/states/fix-implementation/result-envelope.json`. The full suite rewrote `runs/run-c5a8d50d3238/state.json` and `task-context.yaml` both at baseline and after; both were restored with `git checkout` and `git status` then showed no change under any existing run. Scratch copies and the mirror lived outside the repository.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | Any `next` over run-437e2f765e4b would now return its blocked recommendation to pending and rewrite that run's evidence; until resolved it keeps self-hosting S7 failing | medium | medium | No scheduler command was run against it; its disposition is `Q-004` |
| `R-002` | Documentation's menu is agent-global, so a `technical-recommendation` in the pool of its implement-feature, review-pull-request or release phase would now satisfy it | low | low | Census shows no such pool today: those phases' blocked or passing verdicts are unchanged |
| `R-003` | The version moves reset gate auto-approval precedent for investigate and research gates and for gates assessing documentation output | medium | low | Gates fall back to human decision, the stricter path; recorded for the gate owners |
| `R-004` | S8 fails on run-5df08e171670 and on this run until its change proposal exists; S7 fails on run-437e2f765e4b; all three predate this change | high | low | Baseline verifier output shows the same failures; proposals are outside this agent's write scope |
| `R-005` | The implementer host registration states 1.0.0 and instructs an abort against its 1.1.0 manifest, and nothing checks it; the new version test covers only the two agents changed here | medium | medium | Not fixed here by directive; routed as `Q-005` |

## Handoff Notes

- Reviewer focus areas: `C-001` and `C-007` with `V-001` (additive menus, producerless identifiers kept); `C-012` and `C-013`, the one added dependency edge each (`T-003`); `C-015` with `V-002` and `V-003`; `C-016`, whose census lists must only shrink; `R-001` for the stalled run.
- Follow-up work: the seven known-gap hand-offs and the change-review and framework-release profile rows, each removing its entry from the census lists in `C-016`; withdrawing `framed-objective` and `research-brief`; a host-registration version check across all agents; the change proposal for this run.
- Documentation impact: the runtime guide and catalogue pages that list agent or workflow versions, or the profile's routing inputs, should show 1.1.0 and `problem-statement`; the build copy under `build/lib` is stale.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | Should `framed-objective` and `research-brief`, which no agent produces, now be withdrawn from the context agent's menu, and under which version | no | architect | `C-001`, `C-002`, `C-003`, `C-005`, `C-006` |
| `Q-002` | Should the `/investigate` and `/research` command specifications name the `problem-statement` input type the profile now routes | no | omn-tech-lead | `C-015` |
| `Q-003` | Should the self-hosting profile identity version move for the two changed Routing Table rows | no | omn-tech-lead | `C-015` |
| `Q-004` | Is run-437e2f765e4b resumed, which rewrites its recorded block, or retired | no | omn-tech-lead | `C-001`, `C-007`, `C-012` |
| `Q-005` | The implementer host registration's 1.0.0 version against its 1.1.0 manifest is a separate defect to route | no | omn-tech-lead | `C-016` |
