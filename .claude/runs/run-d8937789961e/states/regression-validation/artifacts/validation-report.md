```yaml
validationReport:
  reportId: VR-2026-1009
  validationReference: run-d8937789961e / fix-bug / verify-validators-v4-anchor (defect report runs/inputs/verify-validators-v4-anchor-defect-report.md)
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-d8937789961e/states/fix-implementation/artifacts/implementation-report.md
    - type: acceptance-criteria
      reference: runs/inputs/verify-validators-v4-anchor-defect-report.md
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass
  inputDigest: sha256:610f65f25166ad678c501d2a080545a7
  contextDigest: sha256:f156a71bc88d83d55f5e9fda06d2f8e2
```

## Metadata

- Validation ID: VR-2026-1009
- Validator: omn-qa
- Change under validation: the investigation-report mutation row of the validator coverage verifier derived from the instance under test, with the V4 verdict extracted into importable functions, plus the new test file and the bundle mirror
- Validation date: 2026-10-09

## Validation Scope

- In scope: the defect acceptance criterion (the verifier reports 6/6 COVERED with the real investigation report of run-437e2f765e4b present), the new test file and its two bug witnesses against the pre-fix verifier, the defect report's constraints, the standalone non-mutating verifiers registry coverage and manifests, the bundle parity tests, and the full unit suite.
- Out of scope: the three verifiers that mutate committed run evidence (vertical slice, multi phase, recovery), excluded by the operator dispatch; running the release verification in the main checkout and a hosted CI run, routed to omn-qa by the root-cause analysis and not reachable from this worktree; the two count rows that substitute 99, carried as residual risk R-001 of the implementation report to omn-tech-lead; the defect report's request to report how many other types share the fragility, an analysis deliverable of the root-cause phase already gated by the Fix Gate.
- Evidence examined: the implementation report IR-2026-1009 (read in full via the envelope), the defect report (read in full), the task context, the new test file header and its test list, the diff of the verifier against HEAD for the MUTATIONS table, the real investigation report of run-437e2f765e4b (its recommendation line and options table), and the outputs of the commands recorded in the Acceptance Criteria Results table.

## Test Strategy

- Risk basis: the change alters a verification path that decides whether a validator is proven to reject a mutation, so the verifier was run end to end on the real run evidence, the unit tests were run both against the fixed verifier and against the pre-fix file taken from HEAD, and the surrounding verifiers, bundle parity and the full suite were run for regression.
- Levels executed: unit, integration, end-to-end
- Environment: the isolated git worktree on its own branch at the repository root, runtime version 0.9.0, Windows; the committed run evidence of run-437e2f765e4b is present but untracked in this worktree, so it differs from a main checkout where it may be tracked.
- Not executed: performance and security levels, because the change touches no performance-sensitive or security-relevant path and writes only a temporary directory; the verifiers vertical slice, multi phase and recovery, because they rewrite committed run evidence.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| `AC-001` | For every registered artifact type it should find a conforming instance that carries the text the mutation needs, and should still prove that the validator rejects the mutated artifact by the named check. | defect report, Expected behaviour | end-to-end | met | `python runtime/verify_validators.py` at the repository root ended `6/6 checks passed -- COVERED`; the line `investigation-report.md recommending an option the report never evaluated -> caught by I1 (all: ['C6.2', 'I1'])`; the selected instance is the real report whose line 108 reads `- Recommended option: O-003` (option O-003 is the pre-fix failing case); the pre-fix verifier from HEAD, run by the same harness on the same tree, ended `5/6 checks passed -- NOT COVERED` with `no mutation anchor` for that type |
| `AC-002` | The fix needs an automated regression test that fails before the fix and passes after, in the repository's existing test style (`tests/`, run by `python -m unittest discover -s tests`). | defect report, Constraints | unit | met | `python -m unittest tests.test_verify_validators_mutations -v` ended `Ran 15 tests ... OK`; the same file loaded against the pre-fix verifier ended `Ran 15 tests, FAILED (failures=2, errors=25)`, the two failures being the witnesses by assertion (`unexpectedly None : no mutation anchor in a report recommending O-003` and `True is not false : the substitute named an option the report evaluated`), the errors being the new functions absent; the full-suite run listed `test_verify_validators_mutations 15 tests` ok |
| `AC-003` | Do not weaken V4: it must still fail when a validator does not reject its mutation. | defect report, Constraints | unit | met | in the 15 passing tests, `test_validator_accepting_the_mutation_fails`, `test_validator_rejecting_by_another_check_fails` and `test_missing_anchor_fails_without_running_the_validator` all ok, so V4 still fails for an accepting validator, for a rejection by another check, and for a missing anchor; the diff of the MUTATIONS table against HEAD shows one changed line, the investigation row |
| `AC-004` | Do not modify, delete or re-generate any committed run evidence, including `run-437e2f765e4b`. | defect report, Constraints | integration | met | `git diff --quiet HEAD -- runs` printed `tracked-runs-unchanged`; `git status --short` after every command lists no modified tracked run path, and after the full suite the two replay-record files of run-c5a8d50d3238 were restored with `git checkout --` and the status list returned to the seven entries it held before; run-437e2f765e4b is untracked here, so git cannot attest its content, and its three artifacts were only read by the verifier, which writes to a temporary directory |
| `AC-005` | Do not change any registered validator, template or the mutation intent of any table row. | defect report, Constraints | integration | met | `git diff --stat HEAD` lists only the verifier and its bundled mirror among tracked files; `git status --short` shows no validator, template or fixture path modified or added; the MUTATIONS table diff against HEAD changes only the investigation row from a literal pair to the callable `recommend_an_unevaluated_option` with check `I1` and the description unchanged |
| `AC-006` | The other verifiers stay at their baselines when run standalone and non-mutating: registry coverage 8 of 8 and manifests 2 of 2. | operator dispatch, regression targets | integration | met | `python runtime/verify_registry_coverage.py` ended `8/8 checks passed -- COVERED`; `python runtime/verify_manifests.py` ended `2/2 checks passed -- CONFORMS` |
| `AC-007` | The bundle parity test passes. | operator dispatch, regression targets | integration | met | `python -m unittest tests.test_bundled_payload` ended `Ran 11 tests ... OK`, including the environment-dependent test, which did not fail here |
| `AC-008` | The full unit suite passes with no regression against the 657 of 657 the operator recorded on this tree. | operator dispatch, regression targets | unit | met | `python tools/run_tests_parallel.py` re-run in this validation ended `26/26 modules passed, 657 of 657 discovered tests ran, 345.6s wall`; replay records of run-c5a8d50d3238 restored afterwards by `git checkout --` |

## Execution Summary

- Criteria validated: 8
- Met: 8
- Not met: 0
- Blocked: 0

## Defects

None identified.

## Regression Assessment

- Regression scope: V4 and the other five checks of the verifier for all thirteen registered validators; the V3 per-type validator checks; the 31/31 investigation validator rules, reached through C6.2 and I1; the other verifiers that must stay at baseline; the bundled payload mirror parity; the rest of the unit suite.
- Regressions detected: None identified.
- Coverage of changed behavior: the derived investigation row is reached by the end-to-end verifier run on the real O-003 report, by the two witness tests (a conforming O-003 report and a conforming nine-option report recommending O-002), by the five derivation edge-case tests, and by the sweep over all thirteen MUTATIONS rows; the extracted verdict function is reached by five tests including the accepting-validator and wrong-check failures; the main() path is reached by the end-to-end run.
- Untested areas: the main checkout and a hosted CI run were not observed; the two count rows substituting 99 are not exercised against an instance carrying a count of 99; four subtests of the sweep depend on the instance the selector returns, so a future committed instance lacking a contract-pinned anchor is not exercised; the three mutating verifiers were not run.

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: the count rows substituting 99 would be accepted for an artifact carrying a count of 99, making V4 fail loudly rather than silently, carried to omn-tech-lead and unaccepted; the main checkout and a hosted CI run of the release verification are not observed.
- Monitoring required: V4 detail text containing no mutation anchor or mutation accepted on any release verification; the release checklist FR-02 failing after a new run commits an artifact.

## Verdict

- Decision: pass
- Rationale: no defect was found, all eight criteria were met by commands executed in this run, and the Stage 8 table row for no open critical or high defect and no unmet or blocked criterion yields pass with status complete.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that the gate owner advance the Verification Gate for this change, and that the main checkout and hosted CI observations remain open follow-ups.

## Open Questions

- `Q-001`: Whether the count rows that substitute 99 should be made derived is for omn-tech-lead; it does not alter this verdict. Separately, the implementation report states 14 new tests while the file holds and runs 15 (and 657 total, not 656), an off-by-one in its prose that its author omn-dev-1-implement may correct.
