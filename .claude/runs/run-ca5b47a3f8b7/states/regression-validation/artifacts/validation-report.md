```yaml
validationReport:
  reportId: VR-run-ca5b47a3f8b7-regression-validation
  validationReference: run-ca5b47a3f8b7::fix-implementation (defect runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md)
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-ca5b47a3f8b7/states/fix-implementation/artifacts/implementation-report.md
    - type: defect-report
      reference: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
    - type: bug-analysis
      reference: runs/run-ca5b47a3f8b7/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: acceptance-criteria
      reference: runs/run-ca5b47a3f8b7/state.json
  producedBy: qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass
  inputDigest: sha256:495ea7248751e26c05f245b42d64e2f2
  contextDigest: sha256:9af9244df5ecf1e5560f1fac2e4a5c44
```

## Metadata

- Validation ID: VR-run-ca5b47a3f8b7-regression-validation
- Validator: qa
- Change under validation: shared `placeholders` helper in .claude/runtime/verify_recovery.py used by `clearing_action_admissible` and `executable`, plus PlaceholderFormTestCase in tests/test_clearing_action_admissibility.py (implementation report IR-2026-1019, digest sha256:495ea7248751e26c05f245b42d64e2f2, change set `C-001`, `C-002`)
- Validation date: 2026-10-18

## Validation Scope

- In scope: placeholder detection in every form (one word, several words, glued prefix, glued suffix, unterminated) by the X1 admissibility table and the execution guard; the whole-argument exemption after row-exempt flags (gate, rollback `--decided-by`, policy-exception); valid-action admissibility; the committed-envelope true/false baseline; the recovery verification over induced runs; the full unit suite as the regression surface, including every test module that imports verify_recovery.py (test_clearing_action_admissibility, test_gate_rollback, test_policy_exception_command); the framework verifiers named by the dispatch.
- Out of scope: the builder's `--detail <what happened>` emission in .claude/runtime/framework_runtime.py, a follow-up per the Triage Gate (tech-lead) and the root-cause open question on the builder (architect); code quality of the change, which the Fix Gate (dev-2-reviewer) judged; post-release monitoring signals of the Validation Plan, which only operation can observe; CI and non-Windows platforms, not reachable from this host (the root-cause open question on platforms, orchestrator); this run's still-missing change proposal flagged by self-hosting S8, a closure-phase obligation (orchestrator).
- Evidence examined: implementation report (supplied input, read in full); defect report runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md (read in full); root-cause bug-analysis (read in full); Triage Gate and Fix Gate records in runs/run-ca5b47a3f8b7/state.json; `git diff` and `git status` of the worktree; commands run in this invocation, listed per criterion below: the admissibility module in the worktree, the new tests against the committed module, repro.py, builder.py, probe_exempt.py, two QA probes (qa_edge.py, literal_bracket.py), scan.py with a before.json comparison, a rejudge of this run's envelopes under both modules, `tools/run_tests_parallel.py` on a changed copy and a baseline copy, test_knowledge with the committed lessons store, verify_recovery.py, verify_multi_phase.py and verify_self_hosting.py on copies, and verify_registry_coverage.py, verify_validators.py, verify_manifests.py and `verify_vertical_slice.py --run-id run-c5a8d50d3238` in place.

## Test Strategy

- Risk basis: the change alters a predicate that decides whether a recovery verification passes and whether the execution guard runs an action (Stage 4: exhaustive branch coverage), and its interface is called by both guards (every call site exercised); every branch of `placeholders` (no bracket, unterminated closed later, unterminated to the end, whole versus not whole, exempt flag versus not, first position) was driven by the unit module and qa_edge.py, and both call sites by the unit module, builder.py and the recovery verification; no data is written or migrated, and the full before-and-after comparison was applied to the committed-envelope verdicts instead.
- Levels executed: unit, integration
- Environment: host Windows 11 checkout at commit 340a41b with Python 3.14.0; unit module, probes, scan and four read-only verifiers in the worktree, with `git status` compared before and after each; full suites and the three writing verifiers in isolated copies of the tracked tree in a scratch directory outside the worktree, the changed copy byte-identical to the worktree for both changed files (md5 checked), the baseline copy differing only in those two files at HEAD; target CI and other platforms were not reached.
- Not executed: end-to-end beyond the recovery verification's induced command-line runs, because the change has no user journey other than the verifier itself; performance, because area performance is not triggered and the predicate is a single linear pass; a dedicated security level, because the triggered security area rests on the word token meaning argv tokens (root-cause Technical impact) and the change handles no credential, authorization or external input; the database area was triggered by the word migration in the implementation report's "Data or migration impact: none" and has no surface here.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| AC-001 | A clearing action that carries a placeholder in any form is inadmissible, unless the placeholder is one whole argument following a flag the row exempts as human judgement. That covers one word, several words, a placeholder glued to other text, and an unterminated `<`. | defect report, Expected behaviour | unit | met | `python -m unittest tests.test_clearing_action_admissibility -v` 30/30 OK, the five form tests and the exempt-flag test among them; repro.py and builder.py report every form inadmissible; qa_edge.py: whole exempt trio yields [], every non-whole or non-exempt form is reported |
| AC-002 | `executable()` refuses the same forms. | defect report, Expected behaviour | unit | met | every PlaceholderFormTestCase refusal asserts AssertionError from `vr.executable` (30/30 OK); builder.py: "executable refuses" for `<owner>x`, `x<owner>`, `<owner`, `--rationale <fill in text>` and the builder's `<what happened>`; qa_edge.py refuses multi-word and glued deciders |
| AC-003 | A valid action without a placeholder stays admissible, and every exemption the table grants today (gate, rollback `--decided-by`, policy-exception on an item blocked `awaiting_policy_exception`) keeps its verdict. | defect report, Expected behaviour | unit | met | repro.py: `tool_failure` -> (True, release on execution-planning status=leased); test_valid_action_is_admissible, test_gate_action_keeps_its_exemption, test_emitted_action_leaves_only_the_decider_and_is_admissible, test_emitted_action_with_placeholders_is_admissible all ok; probe_exempt.py whole `<role>`, `<who>`, `<text>` -> [] |
| AC-004 | Every committed envelope under `.claude/runs/` keeps its verdict, and `verify_recovery.py` still proves out in full. Committed run evidence is not edited. | defect report, Expected behaviour | integration | met | scan.py: 251 envelopes, 0 errors; all 247 before.json keys present with 0 true/false flips; 4 new envelopes of this run judge identically under HEAD and fixed modules (rejudge_new.py); verify_recovery.py on a copy 74/74 RECOVERY PROVEN; `git status` shows no tracked file under .claude/runs modified |
| AC-005 | Regression tests in `tests/test_clearing_action_admissibility.py` pin single-word and multi-word placeholders as inadmissible and a valid action as admissible. | defect report, Expected behaviour | unit | met | test_single_word_placeholder_is_inadmissible, test_multi_word_placeholder_is_inadmissible, test_valid_action_is_admissible ok; against the committed module the new tests fail 8 times across 5 methods (multi-word, glued prefix, glued suffix, unterminated, exempt-flag), so they pin the fix |
| AC-006 | Scope: only the shared placeholder detection in verify_recovery.py plus tests in tests/test_clearing_action_admissibility.py; no --detail exemption. | Triage Gate rationale, runs/run-ca5b47a3f8b7/state.json | integration | met | `git diff` touches only those two files for this change; the third modified file, lessons.store.json, holds runtime-harvested lessons from other runs, mtime 11:39Z, before the fix-implementation invocation at 11:47:54Z; builder.py: the builder's `--detail <what happened>` release action is inadmissible under leased and blocked states |
| AC-007 | the builder's unparseable --detail <what happened> stays an open follow-up, not a blocker | Triage Gate rationale, runs/run-ca5b47a3f8b7/state.json | integration | met | `git diff --stat` shows framework_runtime.py unmodified; builder.py still prints the action ending `--detail <what happened>`; implementation report Out of scope and `R-001` record the follow-up |
| AC-008 | tests pin multi-word, glued prefix, glued suffix, unterminated and single-word placeholders as inadmissible and refused by executable, keep a valid action admissible and keep the gate, --decided-by and policy-exception exemptions | Triage Gate rationale, runs/run-ca5b47a3f8b7/state.json | unit | met | the five form tests assert inadmissible and `executable` refusal; test_valid_action_is_admissible; test_gate_action_keeps_its_exemption, test_emitted_action_leaves_only_the_decider_and_is_admissible, test_emitted_action_with_placeholders_is_admissible; 30/30 OK in this run |
| AC-009 | every committed envelope keeps its true/false verdict against the baseline, with no run evidence edited, else stop and escalate | Triage Gate rationale, runs/run-ca5b47a3f8b7/state.json | integration | met | scan.py compared on `ok` per key with before.json: 247 of 247 unchanged, 0 missing; only the two resolved run-4c51600606df envelopes change reason text to `<what happened>`, both still False; no tracked run evidence modified per `git status` |
| AC-010 | Shared placeholders helper closes the defect in clearing_action_admissible and executable within the Triage Gate scope | Fix Gate rationale, runs/run-ca5b47a3f8b7/state.json | unit | met | the diff routes both `clearing_action_admissible` and `executable` through `placeholders`; the new tests fail against the committed module and pass with the fix; AC-001, AC-002 and AC-006 evidence |
| AC-011 | rerun the reproduction expecting `<fill in owner name>` inadmissible, `<owner>` inadmissible, `tool_failure` admissible | root-cause bug-analysis, Validation Plan | unit | met | `python repro.py`: `<fill in owner name>` False, `<owner>` False, `tool_failure` True |
| AC-012 | rerun the builder probe expecting the builder action, glued, and unterminated forms inadmissible and refused by the execution guard | root-cause bug-analysis, Validation Plan | unit | met | `python builder.py`: builder action False under leased and blocked, "executable refused"; `<owner>x`, `x<owner>`, `<owner` each False and "executable refuses" |
| AC-013 | rerun scan.py and confirm every envelope's true/false verdict equals before.json | root-cause bug-analysis, Validation Plan | integration | met | `python scan.py after.json` then a per-key `ok` comparison: 0 flips over 247 keys; the 4 keys absent from before.json are this run's own envelopes, equal under both modules |
| AC-014 | run the full recovery verification in an isolated copy and the unit tests, expecting 74/74 and all pass. | root-cause bug-analysis, Validation Plan | integration | met | verify_recovery.py on an isolated copy: 74/74, X1 PASS over 9 open envelopes across 4 runs; the unit tests, which the source names as the admissibility unit tests (its `E-011`), 30/30 OK |
| AC-015 | new in tests/test_clearing_action_admissibility.py, each judged inadmissible and refused by executable: test_multi_word_placeholder_is_inadmissible, test_glued_prefix_placeholder_is_inadmissible, test_glued_suffix_placeholder_is_inadmissible, test_unterminated_placeholder_is_inadmissible, test_single_word_placeholder_is_inadmissible; plus test_valid_action_is_admissible; kept unchanged: test_gate_action_keeps_its_exemption, test_emitted_action_leaves_only_the_decider_and_is_admissible, test_emitted_action_with_placeholders_is_admissible. | root-cause bug-analysis, Validation Plan | unit | met | all six named new tests present and ok via `assert_refused` (inadmissible plus `executable` AssertionError); `git diff` of the test file adds only the docstring lines and the new class, so the three kept tests are unchanged and ok |

## Execution Summary

- Criteria validated: 15
- Met: 15
- Not met: 0
- Blocked: 0

## Defects

| ID | Severity | Category | Location | Symptom | Reproducibility | Status |
|---|---|---|---|---|---|---|
| DF-001 | low | functional | .claude/runtime/verify_recovery.py `placeholders` | a quoted argument holding literal bracket text (`--detail 'retry count > 3'`, `--detail 'see <step 4> above'`) on a leased release is judged inadmissible; the committed module judged both admissible; no committed or induced envelope carries such text | always | open |

## Regression Assessment

- Regression scope: X1 verdicts on every committed and induced open envelope; scenario-D rollback executions through the execution guard; the gate, rollback decider and policy-exception exemptions; every test module importing verify_recovery.py; the rest of the unit suite; the multi-phase, self-hosting, registry, validator, manifest and vertical-slice verifiers.
- Regressions detected: None identified.
- Coverage of changed behavior: both call sites of `placeholders` and every branch of it are reached by the unit module (30/30), builder.py, probe_exempt.py and qa_edge.py; scenario D and X1 by verify_recovery.py 74/74; full suite on copies: baseline 567 ran, changed 574 ran, failing set identical (5: test_demo_capture x3 for an ffmpeg `filter_complex_script` option error, test_knowledge BackwardCompatibility x2), test_knowledge failing the same 2 with the committed lessons store; neither failing module imports verify_recovery.py; verify_multi_phase 15/15, verify_registry_coverage 8/8, verify_validators 6/6, verify_manifests 2/2, verify_vertical_slice 10/10, verify_self_hosting 8/8 on a tracked-tree copy and 7/8 with this run copied in (S8 only: run-ca5b47a3f8b7 unaccounted, its proposal not yet written).
- Untested areas: a lone `>` and two bracket pairs after an exempt flag (Fix Gate F-1, F-2) behave as required in qa_edge.py but no automated test pins them; DF-001's literal-bracket edge is pinned by no test either way; behavior under CI and non-Windows platforms; any test inside the 5 pre-existing failing tests' bodies, which stop at their first failure.

## Residual Risk

- Accepted risk: the builder's `--detail <what happened>` emission left as a non-blocking follow-up, accepted by tech-lead at the Triage Gate; the Fix Gate low findings F-1, F-2 (unpinned forms) and F-3 (literal-bracket text refused, DF-001, implementation `R-003`) carried as non-blocking by dev-2-reviewer at the Fix Gate.
- Unmitigated risk: an induced or real run that leaves the builder's bare release prescription open will now fail X1 until the builder follow-up lands (implementation `R-001`); the 5 pre-existing full-suite failures mask any new failure in test_demo_capture and test_knowledge (implementation `R-002`); DF-001 has no explicit risk acceptance by its design owner (`Q-001`); results rest on one host and platform (`Q-002`).
- Monitoring required: the X1 detail line and the per-envelope true/false verdicts against before.json, per the root-cause Validation Plan; any open envelope with a `<` outside an exempt whole argument judged admissible indicates recurrence; any open envelope judged inadmissible for a quoted literal bracket indicates DF-001 has surfaced.

## Verdict

- Decision: pass
- Rationale: all 15 criteria are met on evidence executed in this invocation, no criterion is not-met or blocked, and the only defect, DF-001, is low, so Stage 8 yields its first row, pass with status complete.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that dev-2-reviewer, who decides the fix-bug Verification Gate because this agent produced its evidence, approve it, carrying DF-001, `Q-001` and `Q-002` forward; the decision rests with the gate owner.

## Open Questions

- Q-001: Must a quoted argument holding literal angle-bracket text stay admissible, or is refusing it (DF-001) the intended consequence of treating every bracket span as a placeholder? Routes to architect, as owner of the accepted fix strategy.
- Q-002: Behavior was confirmed only on this Windows host with Python 3.14.0; a CI run of the admissibility module and the recovery verification would confirm it elsewhere. Routes to orchestrator.
