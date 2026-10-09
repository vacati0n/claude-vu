```yaml
validationReport:
  reportId: VR-2026-1010
  validationReference: run-5f4422f26c3e / fix-bug / verify-validators-v4-instance-selection (defect report runs/inputs/verify-validators-v4-instance-selection-defect-report.md)
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-5f4422f26c3e/states/fix-implementation/artifacts/implementation-report.md
    - type: acceptance-criteria
      reference: inline
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass
  inputDigest: sha256:9f9ea2a9686914263e18c96ae4e7a066
  contextDigest: sha256:f156a71bc88d83d55f5e9fda06d2f8e2
```

## Metadata

- Validation ID: VR-2026-1010
- Validator: omn-qa
- Change under validation: V4 of runtime/verify_validators.py selects, per artifact type, the first committed instance on which the declared mutation resolves, and locates the orchestration gate row with or without backticks (IR-2026-1010)
- Validation date: 2026-10-09

## Validation Scope

- In scope: the eight operator-supplied acceptance criteria for the V4 repair: the verifier result from the repository root, reproduction of the pre-fix failure, the mutation test module, V4 decisiveness and V3 validation of the selected and skipped instances, the row locator on both renderings, the standalone regression targets and the mirror, the full unit suite, and the write-scope constraints.
- Out of scope: the main checkout and hosted CI (never observed, routed to omn-qa follow-up by the root-cause analysis); the orchestration contract's identifier rendering (architect); the working-location rejection of the change proposal from inside the framework directory (omn-tech-lead); code quality, which belongs to omn-dev-2-reviewer; verify_vertical_slice, verify_multi_phase and verify_recovery, excluded by the operator.
- Evidence examined: implementation-report IR-2026-1010 (digest sha256:9f9ea2a9686914263e18c96ae4e7a066, read as a claim source); task-context.yaml of this run; runtime/verify_validators.py and tests/test_verify_validators_mutations.py (read at the sites named); executed commands CMD-1 to CMD-14 listed under Acceptance Criteria Results.

## Test Strategy

- Risk basis: the change alters a path that decides whether a coverage check passes or fails (V4 and its shared V3 instance), so every branch of selection is pinned by test, the verifier is executed on the real tree, the original verifier is replayed to reproduce the defect, and the full suite is executed for the regression surface.
- Levels executed: unit, integration, end-to-end
- Environment: the worktree of this run on Windows, run from the repository root and from inside the framework directory; the pre-fix verifier was loaded from a scratch directory outside the repository and executed against this tree; the hosted CI environment differs and was not observed.
- Not executed: performance and security levels, because the change reads run evidence and writes only temporary copies, with no performance-sensitive or security-relevant handling; verify_vertical_slice, verify_multi_phase and verify_recovery, excluded by operator instruction.

## Acceptance Criteria Results

The Source of every row is the operator dispatch for this phase. Commands: CMD-1 `python runtime/verify_validators.py` (framework directory, from the repository root); CMD-2 the original verifier from `git show HEAD:runtime/verify_validators.py` executed from a scratch directory against this tree through a loader that sets its location to the repository runtime directory; CMD-3 `python tests/test_verify_validators_mutations.py`; CMD-4 the same module run from inside the framework directory with the classes MutationConsoleLine and SkippedCandidateUnderV3; CMD-5 the verbose run of seven named tests; CMD-6 a scratch script calling award_itself_its_own_gate on the selected record and on a backticked variant; CMD-7 `python runtime/verify_registry_coverage.py`; CMD-8 `python runtime/verify_manifests.py`; CMD-9 `python -m unittest tests.test_bundled_payload`; CMD-10 `cmp` of the verifier and its mirror; CMD-11 `git status --short` and `git diff --stat`; CMD-12 `python tools/run_tests_parallel.py` (re-run in this phase); CMD-13 `git checkout --` of the two run-c5a8d50d3238 files after the suite; CMD-14 `git status --short` after CMD-13.

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| AC-001 | `python runtime/verify_validators.py` from the repo root reports 6/6 COVERED and the orchestration-result.md row reads 'caught by O4 (all: [O4])' with no candidate skipped | operator dispatch | end-to-end | met | CMD-1 printed "6/6 checks passed -- COVERED", V4 detail ending "no candidate skipped", and the row "caught by O4 (all: ['O4'])" |
| AC-002 | the pre-fix behaviour is reproduced: the original verifier from git HEAD (a baseline predating BOTH repairs) gives 5/6 on this tree | operator dispatch | end-to-end | met | CMD-2 printed V4 FAIL naming investigation-report.md and orchestration-result.md ("no mutation anchor ... in this instance"), console line "caught by O4 (all: None)", and "5/6 checks passed -- NOT COVERED"; the baseline predates both repairs, and the implementer's account is a supporting claim only |
| AC-003 | tests/test_verify_validators_mutations.py passes 26 of 26 from the repo root and the working-directory-sensitive classes also pass when run from inside the framework directory | operator dispatch | unit | met | CMD-3 printed "Ran 26 tests ... OK"; CMD-4 from inside the framework directory printed "Ran 3 tests ... OK" |
| AC-004 | V4 is still decisive and V3 still validates the instance V4 uses and every skipped candidate: tests pin each and pass | operator dispatch | unit | met | CMD-5 ran ok: InstanceSelection.test_accept_all_validator_still_fails_v4_after_selection, MutationVerdict.test_validator_accepting_the_mutation_fails, MutationVerdict.test_missing_anchor_fails_without_running_the_validator (V4 decisive), SkippedCandidateUnderV3.test_rejected_unanchored_last_candidate_fails_v3_while_v4_uses_the_older (V3 on skipped and used), RealTreeSelection (13 types) |
| AC-005 | the locator accepts identifiers with and without backticks, shown on the real closure record and on a backticked record | operator dispatch | unit | met | CMD-6: selected record is the closure record of run-d8937789961e, contains no backticked PH identifier, locator found the row; a backticked variant and the backticked fixture also found; PlainRenderedOrchestrationRows (2 tests) ok in CMD-5 |
| AC-006 | regression targets standalone and non-mutating: verify_registry_coverage 8/8, verify_manifests 2/2, `python -m unittest tests.test_bundled_payload`, and the mirror byte-identical (`cmp`) | operator dispatch | integration | met | CMD-7 "8/8 checks passed -- COVERED"; CMD-8 "2/2 checks passed -- CONFORMS"; CMD-9 "Ran 11 tests ... OK"; CMD-10 printed MIRROR_IDENTICAL with no difference; CMD-11 after them shows no new tracked change |
| AC-007 | the full unit suite via `python tools/run_tests_parallel.py` was run by the operator at 668 of 668 on this exact tree; cited as operator-supplied | operator dispatch | unit | met | the operator figure is reported, not relied on; CMD-12, re-run here, printed "26/26 modules passed, 668 of 668 discovered tests ran"; CMD-13 restored the two run-c5a8d50d3238 files and CMD-14 shows only the expected paths |
| AC-008 | constraints held: no validator, template, fixture or committed run evidence changed, and only verify_validators.py, its mirror and the new test file differ | operator dispatch | integration | met | CMD-11 and CMD-14: tracked changes are runtime/verify_validators.py and its bundled mirror only (430 insertions, 90 deletions); the test file is untracked and new; the remaining untracked paths are the proposals, run inputs and run directories of the repair runs; no validator, template, fixture or committed run file shows as modified |

## Execution Summary

- Criteria validated: 8
- Met: 8
- Not met: 0
- Blocked: 0

## Defects

None identified.

## Regression Assessment

- Regression scope: V3 acceptance of the selected instance and all 13 artifact types through the shared selector; the mutation verdict per type; the validator coverage verifier's console and JSON output; the bundled payload mirror; the registry and manifest verifiers; every other module of the unit suite.
- Regressions detected: None identified.
- Coverage of changed behavior: the locator on plain and backticked rows, candidate ordering and skip reporting, the no-candidate failure branch, V3 on the first candidate tried, and the console outcome line are each reached by named tests (CMD-3, CMD-5) and by the real-tree run (CMD-1); the end-to-end defect is reproduced before the change (CMD-2) and absent after it (CMD-1).
- Untested areas: the main checkout and hosted CI run evidence; a future instance type with no applicable candidate beyond the synthetic cases the tests build; the count-based derivations on instances other than the ones committed today; the verifier invoked from inside the framework directory for the change proposal type, a separate defect owned elsewhere.

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: the fallback lets V4 pass on an older instance while a newer one goes unmutated (R-001 of the implementation report, medium likelihood); every skip is printed and stored in the JSON summary, so the risk depends on a reader inspecting that line; no role has accepted it.
- Monitoring required: the V4 detail on each release verification: any text naming a skipped candidate or no applicable candidate, and any real-tree selection test failure naming a type and its candidates.

## Verdict

- Decision: pass
- Rationale: all eight criteria are met on executed checks, no defect is open, and no criterion is blocked, so the adjudication table yields pass with status complete; the original verifier reproduces the defect and the repaired verifier clears it with no regression in the 668 tests.
- Blocking defects outstanding: None identified.
- Readiness recommendation: the evidence supports recommending that the Verification Gate owner, a role other than this validator, approve this phase; the gate decision and any merge rest with that owner.

## Open Questions

- Q-001: Should the orchestration contract fix identifier rendering, or must verifiers keep locating rows by meaning as the repaired locator now does? Routes to architect.
- Q-002: Does the same 6/6 result hold on the main checkout and hosted CI with their run evidence, which this validation did not observe? Routes to omn-tech-lead.
