# Validation Report: investigate and research hand each phase's artifact to the next

```yaml
validationReport:
  reportId: VR-2026-1012
  validationReference: investigate-chain-input-contracts-defect-report / run-5d3c99aaaae1
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-5d3c99aaaae1/states/fix-implementation/artifacts/implementation-report.md
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass
  inputDigest: sha256:3721ed3ac1443e21319a17206baaa68d
  contextDigest: sha256:c716697f95e877dda4684d7265aaafe0
```

## Metadata

- Validation ID: VR-2026-1012
- Validator: omn-qa
- Change under validation: declaration-only repair so every phase of investigate and research passes guard G5-INPUT from problem-statement alone (context agent and documentation agent 1.1.0, two Input cells, two profile rows)
- Validation date: 2026-10-09

## Validation Scope

- In scope: the eight operator criteria for this repair: the chain of both workflows end to end, the 13-to-7 hand-off census, guard refusals at the two changed agents, the new 22-test module, the standalone verifiers, untouched run evidence, version and mirror agreement, and the full unit suite including the three reported environment failures.
- Out of scope: the seven remaining blocked hand-offs and the change-review and framework-release profile rows (held as known gaps by the implementer under an operator directive); withdrawal of framed-objective and research-brief; the stalled run run-437e2f765e4b beyond a read-only status; the earlier verify_validators repair, which the operator declared validated elsewhere; the implementer host registration version drift; the stale build copy.
- Evidence examined: the implementation report (digest in metadata); tests/test_investigate_research_handoffs.py; agents/omn-documentation/identity.md; manifests, registry records and host registrations of both changed agents; the 17 changed framework paths and their mirror pairs; the executed commands recorded in the Evidence cells of the criteria below, run in this session on two throwaway copies (post-repair and pre-repair, built per criterion 2) and on a clean export of the base commit.

## Test Strategy

- Risk basis: the change alters the input contract that decides whether a phase proceeds or stops, and an interface other modules consume (the Task Router edge and agent menus), so depth is every changed hand-off exercised through the runtime's own guard, a before-and-after census of all workflows, and the whole unit suite.
- Levels executed: unit, integration, end-to-end.
- Environment: Windows host, Python interpreter of the repository, throwaway copies of the working tree outside the repository for every command that writes run evidence or lets a verifier replay; read-only commands ran in the repository itself. No model was invoked, so each phase artifact is a one-line stand-in, and gate approvals are simulated on the copy.
- Not executed: performance and security levels, because the change declares no timing, data or access behavior and touches only declarations and prose; real agent reasoning over real artifacts, because no model is invoked by a validation of the guard (recorded under Untested areas).

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| AC-001 | every phase of investigate and of research passes G5-INPUT with problem-statement as the only supplied input, derived on a throwaway copy by planning and driving a scratch run of each workflow with the real plan/next/dispatch/gate commands and a stand-in artifact per phase | operator acceptance criterion 1 (task statement) | end-to-end | met | Post-repair copy: `drive_chain.py investigate investigate` and `drive_chain.py research research` (plan with only `--input problem-statement=...`, then next, dispatch, gate per phase) printed G5-INPUT=pass for 5 of 5 phases in each workflow and CHAIN COMPLETE for both; envelopes supplied requirement-framing, investigation-report, technical-recommendation as delivered. Pre-repair copy, same driver: investigate stops BLOCKED at technical-discovery, research at technical-validation, each "no accepted input type supplied". |
| AC-002 | the number of blocked hand-offs across all workflows falls from 13 to 7 and the 7 remaining are exactly the out-of-scope ones listed as known gaps in tests/test_investigate_research_handoffs.py, shown by running the census on the copy BEFORE the fix (pre-fix files reconstructed from `git show HEAD:<path>` for each modified framework path under agents, registry, workflows, config, templates) and AFTER | operator acceptance criterion 2 (task statement) | integration | met | `census.py` (runtime guard functions over all 29 consecutive hand-offs): pre-repair copy "blocked: 13" (the 7 below plus investigate recommendation, technical-discovery, publication and research technical-validation, recommendation-draft, findings-publication); post-repair copy "blocked: 7" = fix-bug root-cause-analysis, implement-feature execution-planning and solution-design-and-risk-assessment, release artifact-packaging and communication-and-post-release, review-pull-request merge-decision and structural-compliance, identical to KNOWN_BLOCKED_EDGES read from the test module. Reconstruction: 17 files replaced from the base commit, `diff -rq` showed exactly those 17 differing. |
| AC-003 | the guard still rejects: an input type nobody declares, optional-only types and empty pools at the changed agents | operator acceptance criterion 3 (task statement) | unit | met | `reject.py` on the post-repair copy, 10 cases, 0 unexpected: at omn-context-agent undeclared investigation-request, undeclared mixed with an accepted type (un-narrowed, "declares no input type"), optional-only context-sources, empty pool all REJECT, requirement-framing ACCEPT; at omn-documentation undeclared requirement-framing, undeclared investigation-report, optional-only scope-definition, empty pool all REJECT, technical-recommendation ACCEPT. The same script on the pre-repair copy rejects both control inputs. |
| AC-004 | tests/test_investigate_research_handoffs.py (22 tests) passes, and fails on the reconstructed pre-fix tree for the defect itself; tests.test_agent_input_contracts and tests.test_bundled_payload pass | operator acceptance criterion 4 (task statement) | unit | met | `python -m unittest tests.test_investigate_research_handoffs` post-repair copy: Ran 22, OK. Same command on the pre-repair copy: Ran 22, FAILED (failures=31), covering 22 of 22 distinct tests including both chain tests at technical-discovery, recommendation, publication, technical-validation, recommendation-draft, findings-publication. `python -m unittest tests.test_agent_input_contracts tests.test_bundled_payload`: Ran 25, OK. |
| AC-005 | standalone non-mutating verifiers: verify_manifests 2/2, verify_registry_coverage 8/8, verify_validators 6/6; verify_vertical_slice and verify_multi_phase against run-c5a8d50d3238 ONLY on the throwaway copy, expecting 10/10 and 15/15 | operator acceptance criterion 5 (task statement) | integration | met | In the repository: `verify_manifests.py` 2/2 CONFORMS; `verify_registry_coverage.py` 8/8 COVERED; `verify_validators.py` 6/6 COVERED. On the post-repair copy only: `verify_vertical_slice.py --run-id run-c5a8d50d3238` 10/10 PROVEN; `verify_multi_phase.py --run-id run-c5a8d50d3238` 15/15 PROVEN. Neither replay verifier was run in the repository. |
| AC-006 | existing run evidence untouched: `framework_runtime.py status --run-id run-437e2f765e4b` works read-only; `git status`/`git diff --stat` show no modification under any existing run; no next/dispatch/complete against any existing run in the repository | operator acceptance criterion 6 (task statement) | integration | met | `status --run-id run-437e2f765e4b` printed investigate v1.0.0, recommendation blocked at awaiting_dependency_output, publication pending. A SHA-256 listing of all 1114 files under runs (excluding this run's own directory), taken before and after every command in this session including the full suite, was identical (`diff` empty). `git diff --stat over the runs directory` printed nothing and `git status` lists only untracked entries that were untracked at the start. The suite and replay verifiers ran on the copy, so the restore of run-c5a8d50d3238 was not needed. |
| AC-007 | versions: manifest, registry/agents.yaml and host registration agree at 1.1.0 for both agents; mirror byte-identical (`cmp` the changed pairs, tests.test_bundled_payload); the documentation contract contains the precedence rule; no runtime function, validator or gate changed (`git diff --stat` for framework_runtime.py and *_validator.py is empty) | operator acceptance criterion 7 (task statement) | unit | met | Manifest metadata.version 1.1.0 (context agent, documentation), registry record version 1.1.0 for both (parsed from registry/agents.yaml), each host registration states 1.1.0 twice. `cmp` over the 17 changed framework paths against their bundled-payload counterparts: 17 IDENTICAL; tests.test_bundled_payload passed (AC-004). agents/omn-documentation/identity.md states that the recommendation produced by recommendation or recommendation-draft governs and the option-analysis or option-synthesis one is a superseded draft. `git diff --stat -- framework_runtime.py '*_validator.py'` printed nothing; the only modified runtime path is verify_validators.py (the earlier repair, out of scope). |
| AC-008 | the full unit suite run by the operator (690 discovered, 687 pass, 3 FAIL, all in tests/test_demo_capture.py EndToEndEditTestCase) is verified independently: the three fail identically on a clean `git archive HEAD` export, and every other module passes | operator acceptance criterion 8 (task statement) | unit | met | `git archive HEAD` extracted to a temp directory, `python -m unittest discover -s tests -p test_demo_capture.py -k EndToEndEditTestCase`: Ran 3, FAILED (failures=1, errors=2), message "ffmpeg failed: Unrecognized option 'filter_complex_script'". `python tools/run_tests_parallel.py` on the post-repair copy: "26/27 modules passed, 690 of 690 discovered tests ran"; the only FAIL/ERROR lines are those same three tests with the same message, so 687 pass. The ffmpeg on this host reports version 9.0.2; its install time is as reported by the operator, not observed. |

## Execution Summary

- Criteria validated: 8
- Met: 8
- Not met: 0
- Blocked: 0

## Defects

| ID | Severity | Category | Location | Symptom | Reproducibility | Status |
|---|---|---|---|---|---|---|
| DF-001 | medium | operational | tests/test_demo_capture.py EndToEndEditTestCase (three tests) and the demo edit step that invokes ffmpeg | With ffmpeg 9.0.2 on this host the edit step fails with "Unrecognized option 'filter_complex_script'", so no film or edit list is produced and three tests fail; identical on a clean export of the base commit and on the post-repair copy | always | open |

## Regression Assessment

- Regression scope: every other workflow's hand-offs (29 examined), the agent input menus of the two changed agents, the Task Router edges of investigate and research, the two profile routes, the bundled payload mirror, the stalled run's recorded state, and the whole unit suite (690 tests).
- Regressions detected: None identified. DF-001 is an environment defect independent of this change and is not a regression from it, since it fails identically on the base commit export.
- Coverage of changed behavior: the guard verdict at each of the six changed hand-offs is exercised both through scratch runs of the real commands (AC-001) and through the 22-test module (AC-004); the widened menus and their refusals by AC-003; the version, registry and mirror changes by AC-007.
- Untested areas: real agent reasoning and validators over real (not stand-in) artifacts for the context, tech-lead and documentation phases, since no model is invoked; gate auto-approval precedent after the version moves; the seven remaining blocked hand-offs and two profile rows, which still block by design; resuming run-437e2f765e4b, which would rewrite that run's evidence; verify_self_hosting, which this validation was not asked to run.

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: DF-001 carries forward with no acceptance and no owner assigned; the seven known-gap hand-offs keep failing at G5-INPUT for implement-feature, fix-bug, review-pull-request and release; documentation's menu is agent-global, so a technical-recommendation in the pool of another documentation phase would now satisfy it (the census shows no such pool today).
- Monitoring required: the census and tests/test_investigate_research_handoffs.py, whose known-gap lists can only shrink; the first real investigate or research run, to observe the context, tech-lead and documentation agents accept the renamed inputs; the demo capture tests after any ffmpeg change.

## Verdict

- Decision: pass
- Rationale: every one of the eight criteria is met by an executed check, no critical or high defect is open, and no criterion is blocked or not met, so the adjudication table yields pass; DF-001 is a medium environment defect outside the changed surface and does not move the row.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that the gate owner treat the repair as validated for the Verification Gate and route DF-001 as a separate defect to omn-dev-1-bug-analyst, with the untested areas above carried as noted residual risk.

## Open Questions

- Q-001: Which role owns the demo capture incompatibility with ffmpeg 9.0.2 (DF-001), and should it be fixed in the filter invocation or by pinning the tool version? Routes to omn-tech-lead.
- Q-002: Should the first real investigate or research run be observed before the known-gap follow-ups are scheduled, given that no model-driven phase has yet consumed the renamed inputs? Routes to omn-orchestrator.
