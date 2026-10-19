```yaml
implementationReport:
  reportId: IR-2026-1019
  changeReference: run-ca5b47a3f8b7::fix-implementation (defect runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md)
  sourceInputs:
    - type: bug-analysis
      reference: runs/run-ca5b47a3f8b7/states/triage-and-impact/artifacts/bug-analysis.md
    - type: bug-analysis
      reference: runs/run-ca5b47a3f8b7/states/root-cause-analysis/artifacts/bug-analysis.md
  producedBy: dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: complete
  workflowPhase: fix-implementation
  verificationStatus: verified
  inputDigest: sha256:dd1777df9790a5a1f51e15e94cfc534a
  contextDigest: sha256:40e4067f94b3a676e0e3077abdc83487
```

## Metadata

- Report ID: IR-2026-1019
- Change reference: run-ca5b47a3f8b7::fix-implementation, defect runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
- Workflow phase: fix-implementation
- Status: complete
- Verification status: verified
- Review status: pending-review

## Implementation Summary

- Change intent: the X1 admissibility table and the execution guard now share one placeholder definition, so a multi-word, glued-prefix, glued-suffix, unterminated, or one-word placeholder is inadmissible and refused, and only a placeholder that is exactly one whole argument directly after a row-exempt flag stays exempt.
- Approach taken: ladder rung 7 for one new function `placeholders` in .claude/runtime/verify_recovery.py, required because the two guards each carried an inline per-argument test and the accepted fix demands one shared definition (rungs 2 to 6 held nothing that spans split arguments); it treats the span from an argument opening `<` to the argument closing it as one placeholder, an unterminated `<` running to the end, and keeps the reason format `placeholder argument [...] in [...]`; both call sites now call it; no new file, abstraction layer, or dependency.
- Design reference: root-cause-analysis bug-analysis (digest sha256:a3bbd14091b14e29df28a961d5238e82), Fix Strategy and Validation Plan; Triage Gate conditions in runs/run-ca5b47a3f8b7/state.json.
- Out of scope: .claude/runtime/framework_runtime.py, whose release prescription still emits `--detail <what happened>` (upstream root-cause open question 1, owner architect, a follow-up per the Triage Gate); no `--detail` exemption on release; no committed run evidence edited; the triage-phase builder pin test, which the gate's approved scope did not carry; no bundled payload copy of verify_recovery.py exists in this tree (search found only the authoritative file and no tests/test_bundled_payload.py), so none was kept in step.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | .claude/runtime/verify_recovery.py | modified | Add the shared `placeholders` helper and use it in `executable` and `clearing_action_admissible`; update both docstrings | RCA Fix Strategy, proposed fix; Triage Gate scope |
| `C-002` | tests/test_clearing_action_admissibility.py | modified | Add PlaceholderFormTestCase with the six Validation Plan tests and one exempt-flag test; extend the module docstring; existing tests unchanged | RCA Validation Plan, regression tests added; Triage Gate conditions |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Witness: the new multi-word, glued-prefix, glued-suffix, unterminated and exempt-flag tests fail against the committed detection and pass after the fix | regression | `C-001`, `C-002` | `python -m unittest tests.test_clearing_action_admissibility` in an isolated tree copy with the committed verify_recovery.py, then in the worktree | pass |
| `T-002` | Admissibility module: 30 tests, the 23 pre-existing ones unchanged, all pass | unit | `C-001`, `C-002` | `python -m unittest tests.test_clearing_action_admissibility -v` | pass |
| `T-003` | Mutation runs in the isolated copy: full revert, executable-only revert, table-only revert, span not extended, whole-argument check loosened; every mutant fails at least one new test | regression | `C-001`, `C-002` | `python -m unittest tests.test_clearing_action_admissibility` once per mutant, file restored after each | pass |
| `T-004` | Reproduction: `<fill in owner name>` and `<owner>` inadmissible, `tool_failure` admissible on a leased item | regression | `C-001` | `python repro.py` (analyst reproduction script) from the worktree root | pass |
| `T-005` | Builder probe: the runtime's own `--detail <what happened>` release action, plus `<owner>x`, `x<owner>`, `<owner` and `--rationale <fill in text>`, inadmissible and refused by the execution guard | regression | `C-001` | `python builder.py` (analyst probe script) from the worktree root | pass |
| `T-006` | Exempt-flag probe: whole `<role>`, `<who>`, `<text>` after exempt flags yield nothing; multi-word, glued, unterminated after an exempt flag, and a placeholder after no flag, are reported | unit | `C-001` | `python probe_exempt.py` from the worktree root | pass |
| `T-007` | Committed-envelope baseline: all 247 envelopes in before.json keep their true/false verdict; two resolved run-4c51600606df envelopes change reason to `<what happened>`; this run's 2 newer envelopes judge identically under the committed module | regression | `C-001` | `python scan.py after.json` from the worktree root, compared with before.json on `ok`; new envelopes rejudged with the committed module | pass |
| `T-008` | Recovery verification over induced runs: 74/74 checks, X1 passing over 9 open envelopes across 4 runs | integration | `C-001` | `python .claude/runtime/verify_recovery.py` in the isolated tree copy | pass |
| `T-009` | Regression baseline: full suite before and after; 567 then 574 tests, the failing set identical (5 pre-existing, `R-002`), no new failure | regression | `C-001`, `C-002` | `python -m unittest discover -s tests -p "test_*.py"` in isolated copies before and after, failing sets diffed | pass |

## Verification Results

- Verification method: baseline first (admissibility module 23/23 in the worktree, full suite in a pristine isolated copy); then the fix, the unit module, mutation runs, the analyst reproduction and probes, the committed-envelope scan, and the recovery verification, the last only in an isolated copy of the tracked tree so no injected run touched the worktree.
- Commands executed: `python -m unittest tests.test_clearing_action_admissibility -v` (before and after); `python -m unittest discover -s tests -p "test_*.py"` (before and after, isolated copies); `python .claude/runtime/verify_recovery.py` (isolated copy); `python -m unittest tests.test_clearing_action_admissibility` once per mutant, five mutants (isolated copy); `python repro.py`; `python builder.py`; `python probe_exempt.py`; `python scan.py after.json` with a before.json comparison, and the same scan against the committed module; `git status --short` before and after; `python .claude/runtime/implementation_report_validator.py` on this artifact with its invocation envelope, as self-verification.
- Result summary: 9 evidence entries executed, 9 passed, 0 failed; admissibility module 30/30; recovery verification 74/74; full suite 574 run, 569 passed, 5 failed, all 5 pre-existing and identical to the baseline; scan 0 true/false flips over 247 baseline envelopes; 5 of 5 mutants killed.
- Unverified areas: none

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | One test beyond the Validation Plan's named list, `test_only_a_whole_argument_after_an_exempt_flag_stays_exempt`, in `C-002` | RCA Validation Plan, regression tests added | The named tests all use `release`, which has no exempt flag, so a mutant loosening the whole-argument check survived them (`T-003`, fifth mutant); this test kills it and pins the gate-approved exemption rule | not-required |

## Boundary Compliance

- Module boundaries preserved: the change stays inside verify_recovery.py's clearing-action section and its test module; framework_runtime.py, the state engine, and the recovery policy are untouched.
- Public interface changes: one new module-level function `placeholders(argv, exempt)`; `executable` and `clearing_action_admissible` keep their signatures and reason text format.
- Data or migration impact: none; no committed run evidence or ledger was edited, and verdicts over committed envelopes are unchanged (`T-007`).
- Declared side effects: .claude/runtime/verify_recovery.py, tests/test_clearing_action_admissibility.py, this artifact, and its result envelope; tests/ sits at the repository root, outside the dispatch prompt's `.claude/**` line but inside the manifest's repositoryWrites scope (repository minus runs/** and proposals/**), and the Triage Gate decision in runs/run-ca5b47a3f8b7/state.json names that file; the pre-existing modification of .claude/memory/lessons/lessons.store.json predates this invocation and was not touched; scratch files, isolated tree copies, and recovery-verification injected runs live only outside the worktree.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | The builder still emits `--detail <what happened>` on the awaiting-recovery-task release path; X1 now rejects any open envelope carrying it | low | an induced or real run leaving that envelope open fails X1 until the builder follow-up lands | X1 names the placeholder in its reason; 74/74 shows no induced run leaves it open today (`T-008`) |
| `R-002` | Five full-suite tests fail before and after the change: three test_demo_capture end-to-end cases and two test_knowledge backward-compatibility cases | high | they mask any new failure in those two modules | failing set diffed identical before and after (`T-009`); neither module imports verify_recovery.py |
| `R-003` | A filled argument that legitimately contains a literal `<` or `>` is now judged a placeholder | low | a correct action is reported inadmissible or refused | no committed envelope is affected (`T-007`); the reason names the argument text |

## Handoff Notes

- Reviewer focus areas: the span rule in `placeholders` (`C-001`), especially unterminated and stray `>` handling and the `R-003` false-positive edge; the extra exempt-flag test (`V-001`, `C-002`); the two run-4c51600606df reason changes (`T-007`).
- Follow-up work: the builder's `--detail <what happened>` emission in framework_runtime.py, owned by architect per the root-cause open question 1 (`R-001`); a CI run of the unit module and recovery verification, per the root-cause open question 4; a framework change proposal for this change, which this phase may not write.
- Documentation impact: none beyond the updated docstrings in `C-001` and `C-002`.

## Open Questions

None identified.
