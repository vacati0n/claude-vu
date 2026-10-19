```yaml
validationReport:
  reportId: VR-run-2cf7a34e3daa-regression-validation
  validationReference: run-2cf7a34e3daa::fix-implementation (IR-2026-1019) for the release-checklist evidence-rewrite defect in runs/inputs/release-checklist-mutates-committed-runs-defect-report.md
  validationBasis: regression
  sourceInputs:
    - type: implementation-report
      reference: runs/run-2cf7a34e3daa/states/fix-implementation/artifacts/implementation-report.md
    - type: acceptance-criteria
      reference: runs/inputs/release-checklist-mutates-committed-runs-defect-report.md
    - type: known-issues
      reference: runs/run-2cf7a34e3daa/state.json
    - type: task-context
      reference: runs/run-2cf7a34e3daa/task-context.yaml
  producedBy: qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass
  inputDigest: sha256:3e5cde9e0332e6c0e628bbd5b5a3d164
  contextDigest: sha256:9c329f33acd5b4756270f19f411bdb04
```

## Metadata

- Validation ID: VR-run-2cf7a34e3daa-regression-validation
- Validator: qa
- Change under validation: IR-2026-1019 (digest sha256:3d91a8444e03ab96d034cea520d96522): per-item disposable copies and check S11 in verify_self_hosting.py, copy-based M14 replay in verify_multi_phase.py, finally-block cleanup in verify_recovery.py, two new test modules, README and release-checklist text (C-001 to C-007)
- Validation date: 2026-10-19

## Validation Scope

- In scope: the three Expected behaviour statements of the defect report (AC-001 to AC-003); the regression surface: each of the seven checklist verifiers and verify_manifests.py run alone in place with the checklist's arguments, the default no-argument verify_multi_phase.py against the most recently modified run, M14's detection of a real side effect, verify_recovery.py's 74 checks and its cleanup, the failure path of S11, committed run-c5a8d50d3238 and this in-flight run under .claude/runs, and the remaining 567-test suite; Fix Gate findings F-001 to F-004 taken as regression leads.
- Out of scope: conformance of the copy scope and of the content-digest comparison to the Triage Gate's wording (deviations V-001 and V-002), which the implementation report routes to tech-lead and which dev-2-reviewer assessed at the Fix Gate; code quality of the change and of its tests, owned by dev-2-reviewer; the intermittent Windows os.replace save failure, a separate defect the implementation report routes to orchestrator; keeping or re-baselining the replay records already committed in run-c5a8d50d3238, owned by tech-lead.
- Evidence examined: implementation report IR-2026-1019; defect report (sha256:1baebc70bf310ad1b1104d5370b40dac); task-context.yaml; Triage and Fix Gate rationales in runs/run-2cf7a34e3daa/state.json; git diff of verify_self_hosting.py, verify_multi_phase.py, verify_recovery.py, runtime/README.md and framework-release-checklist.md; tests/test_verifier_isolation.py and tests/test_release_checklist_clean_tree.py; and these commands run in this phase: python .claude/runtime/verify_self_hosting.py --release-checklist --json-out (record outside the repository); python -m unittest tests.test_verifier_isolation tests.test_release_checklist_clean_tree -v; verify_registry_coverage.py, verify_validators.py, verify_recovery.py, verify_vertical_slice.py --run-id run-c5a8d50d3238, verify_self_hosting.py, verify_multi_phase.py --run-id run-c5a8d50d3238, verify_manifests.py and verify_multi_phase.py with no arguments, each in place; python tools/run_tests_parallel.py over the 22 other test modules; in a git archive HEAD extract outside the repository: HEAD's verify_multi_phase.py --run-id run-c5a8d50d3238 as the pre-fix witness, HEAD's seven verifiers, HEAD's --release-checklist timed, and python -m unittest tests.test_demo_capture.EndToEndEditTestCase; an S11 negative control on a scratch copy outside the repository; git status --porcelain --untracked-files=all and a sha256 of every git ls-files --cached --others --exclude-standard file before and after every repository command.

## Test Strategy

- Risk basis: the change alters whether committed run evidence is written, so a full before-and-after state comparison (porcelain status plus sha256 of all 1883 git-listed files) surrounded every repository command; S11 adds a path that decides whether the checklist passes, so both of its failure branches were induced; scratch_tree, fingerprint() and the checklist runner are called by verifiers and tests, so every verifier invocation, including the default run selection, was exercised; cleanup now sits in finally blocks, so the raised-replay and raised-scenario cases were executed; the mandatory release step's duration changed, so it was measured against a HEAD baseline on the same host.
- Levels executed: unit, integration, end-to-end, performance, security
- Environment: this worktree with the uncommitted change set and this run's 48-line dirty and untracked set present throughout; Windows 11 Pro 10.0.26200, Python 3.14.0, git 2.51.2 with core.filemode false, system temp in the user profile; it differs from the CI ubuntu-latest and windows-latest runners and from a clean checkout; the HEAD extract is not a git work tree, so HEAD timing is a baseline for the same host, not for the same tree state.
- Not executed: CI-runner execution on ubuntu-latest and windows-latest, because external systems are outside this agent's authority and no POSIX host is available here; every level above ran on this one Windows host.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| `AC-001` | Running the release checklist leaves the working tree exactly as it found it: no modified, added or deleted file under the repository. | defect report, Expected behaviour bullet 1 | end-to-end | met | Confirmed: verify_self_hosting.py --release-checklist exit 1 from S8 alone (FR-05, FR-06 fail on it); S11 pass, 1883 files compared, copy_writes empty for all 7 command items; this phase's own status and 1883 digests identical before and after, and again around the clean-tree test's repeat; pre-fix witness: HEAD's verifier rewrote state.json and task-context.yaml of run-c5a8d50d3238 while passing M14 15/15 |
| `AC-002` | Each verifier the checklist runs can still be run on its own, with the same arguments, and still proves what it proves today. `verify_multi_phase.py` still re-executes the runtime against the same request (`M14`) and still reports any side effect the re-execution produces. | defect report, Expected behaviour bullet 2 | end-to-end | met | Confirmed: in place, registry 8/8, validators 6/6, recovery 74/74, vertical slice 10/10, multi-phase 15/15, manifests 2/2, equal to HEAD's verifiers in the HEAD extract; self-hosting 7/8 failing only S8 on this in-flight run, absent from the extract (8/8 there); tree unchanged after each; M14 re-executed 5 commands in a copy and names state.json, task-context.yaml rewritten there; unittest: a duplicated transition and a rewritten artifact in the copy each fail M14 |
| `AC-003` | An automated test runs the release checklist and asserts that `git status` is unchanged afterwards. | defect report, Expected behaviour bullet 3 | end-to-end | met | Confirmed: python -m unittest tests.test_verifier_isolation tests.test_release_checklist_clean_tree -v, 9/9 OK in 234 s; test_git_status_is_unchanged, test_every_listed_file_is_byte_identical, test_s11_ran_and_passed and test_every_command_item_ran ran the full checklist from the repository root and passed |

## Execution Summary

- Criteria validated: 3
- Met: 3
- Not met: 0
- Blocked: 0

## Defects

None identified.

## Regression Assessment

- Regression scope: the checklist runner and its exit decision (S10 still decided by item exit codes), each verifier's standalone result under its checklist arguments, M14's detection of a real side effect, verify_recovery.py's 74 checks and its cleanup of injected runs, the fingerprint() signature reused by tests, committed run-c5a8d50d3238 and this in-flight run under .claude/runs, and the remaining unit suite including the README contract test and the CI workflow test.
- Regressions detected: None identified.
- Coverage of changed behavior: per-item copies and S11 by the checklist run, the clean-tree test, and a negative control in which an item writing into the tree and an item writing inside its copy each fail S11 while S10 passes, run through the git-unavailable fallback of scratch_tree and tree_snapshot; the M14 copy replay, copy fingerprint, rewritten-file report and finally-removal by both in-place forms and the four M14 tests, the no-argument form selecting this in-flight run and leaving it byte-identical; recovery cleanup by the raised-scenario test and two in-place runs; the remaining suite 567 of 567 ran, 564 passed, the only failures being the 3 test_demo_capture EndToEndEditTestCase cases (ffmpeg rejects filter_complex_script), which fail identically in the HEAD extract; no scratch copy was left in the system temp directory.
- Untested areas: POSIX hosts and the CI runners; a mode-only change, which S11's content comparison would not detect while git status reports it on a host with core.filemode true (Fix Gate finding F-003), not observable on this host; a cleanup error inside verify_recovery.py's finally block masking a scenario exception (finding F-004), not induced; a checklist run from a tree with no uncommitted changes; an S11 failure through the git-available copy path, since the negative control ran through the fallback path; the warning path when a copy cannot be removed; no committed test induces an S11 failure (finding F-001), so a later change that disabled S11 would still pass the suite.

## Residual Risk

- Accepted risk: None identified.
- Unmitigated risk: the mandatory release step takes 192 s on this host against 69 s for HEAD's checklist measured here, and the clean-tree test repeats it inside unittest discover on both CI unit jobs; on the implementation report's question to this role on whether that test stays in the default discovery path, this report recommends it stays, because it is the only automated check enforcing AC-003, and leaves the duration to tech-lead; S11's failure path is unpinned by any committed test; mode-only changes escape S11 on hosts that track file mode; every result here comes from one Windows host.
- Monitoring required: any non-empty git status or changed file digest after a checklist run; the S11 detail in the release-checklist result of each change proposal; CI unit-job duration on ubuntu-latest and windows-latest once these tests land; directories prefixed checklist-, m14-replay- or recovery-test- left in the system temp directory; the replay-record count in committed run-c5a8d50d3238 state.json staying constant across commits.

## Verdict

- Decision: pass
- Rationale: The Stage 8 first row applies: no defect is open at any severity and all three criteria are met on checks executed in this phase, with the pre-fix behaviour reproduced at HEAD and both S11 failure branches proven by a negative control.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend that dev-2-reviewer, who decides the Verification Gate under producer exclusion, treat this report as supporting approval, weighing the unmitigated risks above, chiefly the checklist duration and the unpinned S11 failure path.

## Open Questions

- `Q-001`: Should a committed test induce a write and assert that S11 fails, so that S11 cannot be disabled unnoticed (Fix Gate finding F-001); routes to tech-lead.
- `Q-002`: Should S11 also compare file mode on hosts that track it, so that its check covers every git status difference (Fix Gate finding F-003); routes to architect.
- `Q-003`: Is a release checklist of 192 s against 69 s at HEAD on this host, repeated inside both CI unit jobs, an acceptable cost for the mandatory release step; routes to tech-lead.
