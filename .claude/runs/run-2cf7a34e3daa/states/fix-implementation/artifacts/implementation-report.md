```yaml
implementationReport:
  reportId: IR-2026-1019
  changeReference: run-2cf7a34e3daa fix-bug, defect DF-001 (runs/inputs/release-checklist-mutates-committed-runs-defect-report.md)
  sourceInputs:
    - type: bug-analysis
      reference: runs/run-2cf7a34e3daa/states/triage-and-impact/artifacts/bug-analysis.md
    - type: bug-analysis
      reference: runs/run-2cf7a34e3daa/states/root-cause-analysis/artifacts/bug-analysis.md
  producedBy: dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: fix-implementation
  verificationStatus: partially-verified
  inputDigest: sha256:be1da985437f082809bbbfcd01ee4bae
  contextDigest: sha256:40e4067f94b3a676e0e3077abdc83487
```

## Metadata

- Report ID: IR-2026-1019
- Change reference: run-2cf7a34e3daa fix-bug, defect DF-001 (runs/inputs/release-checklist-mutates-committed-runs-defect-report.md)
- Workflow phase: fix-implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

## Implementation Summary

- Change intent: Running `verify_multi_phase.py` (check `M14`) or the full `verify_self_hosting.py --release-checklist` no longer writes committed run evidence: the replay and every checklist command item execute in disposable copies of the working tree that are removed in a `finally` path, the new check `S11` fails the checklist when the repository or any item's copy changes by content, `M14` fingerprints the copy it replayed and names the bookkeeping files rewritten there, and `verify_recovery.py` removes its injected inputs and runs even when a scenario raises.
- Approach taken: Fix Strategy parts (a) and (b) of the root-cause analysis (digest sha256:fc76dfad9d4cc6bd602edb5b697f9038) taken as written. Ladder: copying, removal, and digesting reuse the standard library (`tempfile`, `shutil`, `hashlib`, `os.walk`, `concurrent.futures`) and git's own file listing (rung 3 and 5); the scratch-tree helpers live in the existing `verify_self_hosting.py` and are reused by `verify_multi_phase.py` and the tests rather than duplicated (rung 2); `fingerprint()` gains one optional root parameter at the call site (rung 6); the two new test modules are rung 7, because no existing test runs the checklist or the `M14` replay and CI discovers tests only under `tests/`. No new dependency, no new runtime module, `RUNTIME_VERSION` unchanged.
- Design reference: root-cause analysis Fix Strategy and Validation Plan (sha256:fc76dfad9d4cc6bd602edb5b697f9038), triage Fix Strategy (sha256:452bd3acfa59bba73d08d2185e413e40), and the Triage Gate conditions recorded in `runs/run-2cf7a34e3daa/state.json`.
- Out of scope: The runtime replay path (`framework_runtime.py`, `state_engine.py`) is untouched, as the Triage Gate requires; it still persists bookkeeping by design, now only inside copies. The replay records already committed in `run-c5a8d50d3238` stay as they are, since rewriting committed evidence is prohibited. The intermittent Windows `os.replace` save failure is a separate defect for routing, not changed here.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `.claude/runtime/verify_multi_phase.py` | modified | `M14` replays in a disposable copy (git view, other runs left out), fingerprints the copy, reports files rewritten there, removes the copy in `finally` | RCA Fix Strategy part (a), its three conditions; Triage Gate condition on isolating `M14` |
| `C-002` | `.claude/runtime/verify_self_hosting.py` | modified | adds `git_paths`, `scratch_tree`, `remove_tree`, `tree_snapshot`, `walk_snapshot`, `snapshot_changes`; each checklist command item runs in its own copy; new check `S11` compares content before and after | RCA Fix Strategy part (b); Triage Gate conditions on copying the working tree and failing on a tree difference |
| `C-003` | `.claude/runtime/verify_recovery.py` | modified | injected-input and injected-run removal moved into a `finally` block | RCA Fix Strategy, recovery cleanup clause |
| `C-004` | `tests/test_verifier_isolation.py` | added | proves `M14` leaves the committed run byte-identical, still fails on a duplicated transition or a rewritten artifact, removes its copy on a raised replay, and that recovery cleans up after a raising scenario | RCA Validation Plan, regression tests; Triage Gate condition on regression tests |
| `C-005` | `tests/test_release_checklist_clean_tree.py` | added | runs the full checklist and asserts the repository unchanged by content and by git status, `S11` passed, and no item wrote in its copy | RCA Validation Plan, checklist regression test |
| `C-006` | `.claude/runtime/README.md` | modified | runtime surface table and idempotency section describe the copy-based `M14` and `S11`; corrects the stale `M13` reference to `M14` | RCA Fix Strategy; documentation of the changed verifiers |
| `C-007` | `.claude/validation/framework-release-checklist.md` | modified | states that every command item runs in a temp-directory copy, that `S11` fails on any content change, and that a writable temp directory is needed per item | RCA Fix Strategy part (b); checklist runnability note |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | `M14` replay leaves `run-c5a8d50d3238` byte-identical and its copy removed; pre-fix witness: HEAD's verifier run in a HEAD archive copy this phase rewrote `state.json` and `task-context.yaml` | regression | `C-001`, `C-002`, `C-004` | `python -m unittest tests.test_verifier_isolation -v` (test_replay_leaves_the_committed_run_byte_identical) | pass |
| `T-002` | a transition appended in the copy during replay still fails `M14`; committed run untouched | regression | `C-001`, `C-004` | `python -m unittest tests.test_verifier_isolation -v` (test_a_duplicated_transition_in_the_copy_still_fails_m14) | pass |
| `T-003` | an artifact rewritten in the copy during replay fails `M14` on `artifact_digests`, proving the fingerprint reads the copy | regression | `C-001`, `C-004` | `python -m unittest tests.test_verifier_isolation -v` (test_a_rewritten_artifact_in_the_copy_still_fails_m14) | pass |
| `T-004` | a replay command that raises still leaves no copy behind and the committed run untouched | unit | `C-001`, `C-002`, `C-004` | `python -m unittest tests.test_verifier_isolation -v` (test_the_copy_is_removed_when_a_replay_command_raises) | pass |
| `T-005` | a raising recovery scenario still removes injected inputs and runs, run in a scratch copy | regression | `C-002`, `C-003`, `C-004` | `python -m unittest tests.test_verifier_isolation -v` (test_injected_inputs_and_runs_are_removed) | pass |
| `T-006` | full checklist: every listed file byte-identical, git status unchanged, `S11` pass, every command item ran with no copy writes (4/4, 468 s, executed by the host after the change; verifier code unchanged since) | end-to-end | `C-002`, `C-005`, `C-007` | `python -m unittest tests.test_release_checklist_clean_tree -v` | pass |
| `T-007` | verifier in the real tree: 15/15, `M14` detail names the disposable copy and the rewritten `state.json`, `task-context.yaml`; content digest of all git-listed files unchanged | end-to-end | `C-001`, `C-002` | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass |
| `T-008` | recovery proof 74/74 with injected runs removed; content digest of all git-listed files unchanged | end-to-end | `C-003` | `python .claude/runtime/verify_recovery.py` | pass |
| `T-009` | default self-hosting proof: 7/8, only `S8` fails because this in-flight run has no change proposal yet; tree unchanged | regression | `C-002` | `python .claude/runtime/verify_self_hosting.py` | fail |
| `T-010` | manifest, registry coverage, validator coverage, and vertical-slice proofs each exit 0; git status unchanged | static | `C-002`, `C-006`, `C-007` | `python .claude/runtime/verify_manifests.py`; `verify_registry_coverage.py`; `verify_validators.py`; `verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass |
| `T-011` | regression suite, 572 tests: 569 pass; 3 fail in test_demo_capture EndToEndEditTestCase (host ffmpeg rejects `filter_complex_script`), identical at HEAD; includes the README contract in test_release_verdict | regression | `C-001`, `C-002`, `C-003`, `C-006` | `python -m unittest` over all 23 `tests/test_*.py` modules except tests.test_release_checklist_clean_tree | fail |

## Verification Results

- Verification method: The reproduction inverted on this Windows host. A pre-fix witness was run first: HEAD extracted with `git archive` into a scratch directory, where `verify_multi_phase.py --run-id run-c5a8d50d3238` passed `M14` yet changed `state.json` and `task-context.yaml` of the run. After the change, the new tests (T-001 to T-006) and the verifiers (T-007 to T-010) were run in the real tree, with `git status --porcelain --untracked-files=all` and a sha256 digest of every git-listed file compared before and after; the tree carried this run's dirty and untracked set throughout. T-006 and the first T-001 to T-005 run were executed by the host after the change in this phase's first dispatch; this resumption added T-003 and re-ran T-001 to T-005, T-007 to T-011. The three T-011 failures were attributed by re-running that test class in a HEAD archive copy, with the same three results.
- Commands executed: `python -m unittest tests.test_verifier_isolation -v` (5/5 OK, 33 s); `python -m unittest tests.test_release_checklist_clean_tree -v` (host, 4/4 OK, 468 s); `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` (exit 0); `python .claude/runtime/verify_recovery.py` (exit 0); `python .claude/runtime/verify_self_hosting.py` (exit 1, `S8` only); `verify_manifests.py`, `verify_registry_coverage.py`, `verify_validators.py`, `verify_vertical_slice.py --run-id run-c5a8d50d3238` (each exit 0); `python -m unittest` over the 23 other test modules (572 run, 3 failing); in a HEAD archive copy, `python -m unittest tests.test_demo_capture.EndToEndEditTestCase` (same 3 failing) and HEAD's `verify_multi_phase.py --run-id run-c5a8d50d3238` (run files changed).
- Result summary: 11 evidence entries executed, 9 passed, 2 failed; both failures are pre-existing and unrelated to the change set (T-009 the in-flight run's missing change proposal, T-011 the host's ffmpeg version); every listed file was byte-identical after every command run in the real tree.
- Unverified areas: Linux and macOS hosts and CI runners (all runs were on one Windows host); the git-unavailable fallback paths of `scratch_tree` and `tree_snapshot` (framework-directory copy and walk), which no test exercises; the full checklist run from a tree with no uncommitted changes (only run with this run's dirty and untracked set); the three test_demo_capture end-to-end cases, which fail on this host before and after the change.

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | The `M14` copy holds git's view of the whole repository minus other run directories, not only runtime, registry, and run (`C-001`, `C-002`) | Triage Gate condition: copy holding runtime, registry and run | The root-cause analysis showed such a minimal copy cannot plan (command specification unresolved) while the whole tree minus other runs replays identically | raised: open question `Q-001` to tech-lead, as the analysis already requested |
| `V-002` | The checklist fails on any content-digest difference over every git-listed file, and on writes inside an item's copy, instead of a git status difference (`C-002`, `C-005`) | Triage Gate condition: fail the checklist on any git status difference | Porcelain lines miss a second write to an already-modified or untracked file; content comparison catches every status difference and those too; T-006 asserts both | raised: open question `Q-002` to tech-lead |
| `V-003` | Each checklist command item gets its own fresh copy rather than one copy shared by the whole checklist (`C-002`) | RCA Fix Strategy part (b), copy granularity | No item can see or be judged by another item's writes; cost measured at about 15 s per item on this host (copy 5.6 s, walk 2.7 s, remove 6.9 s) | not-required |
| `V-004` | The two regression test modules are written under `tests/`, outside the dispatch prompt's `.claude/**` write line (`C-004`, `C-005`) | dispatch permitted-writes line | The manifest's repository write scope is the repository minus `runs/**` and `proposals/**`; CI discovers tests only under `tests/`, as the analysis's regression scope anticipated | not-required |
| `V-005` | The Stage 2 baseline was not executed before the code was written, because the first dispatch was interrupted; it was reconstructed from a HEAD archive copy for the pre-fix witness and the failing test class (`C-001`, `C-002`) | reasoning procedure Stage 2, baseline before change | Attribution of the only post-change failures and the fail-before witness were both obtained by running HEAD code directly | not-required |

## Boundary Compliance

- Module boundaries preserved: The change stays inside the verifier layer and its tests; the runtime (`framework_runtime.py`, `state_engine.py`) and its replay design are untouched, and the copied runtime resolves its own root from its file location, so no runtime path logic changed.
- Public interface changes: `verify_self_hosting.py --release-checklist` gains check `S11` and a `copy_writes` field per executed item in its JSON record; `fingerprint()` in `verify_multi_phase.py` gains an optional framework-root parameter defaulting to the previous behaviour; `M14` detail text now names the copy and rewritten files; command-line arguments and exit-code rules are unchanged.
- Data or migration impact: None; committed run evidence is neither migrated nor rewritten, and no schema changes.
- Declared side effects: `C-001` to `C-007` (written by the first dispatch of this phase; `C-004` edited again in this resumption to add T-003), plus `runs/run-2cf7a34e3daa/states/fix-implementation/artifacts/implementation-report.md` and `runs/run-2cf7a34e3daa/states/fix-implementation/result-envelope.json`. Transient scratch copies under the system temp directory and the session scratch directory were created and removed by the commands above. The modified `memory/lessons/lessons.store.json` in the working tree was written by the runtime's lesson harvest before this phase was dispatched (its digest equals the envelope's `memory_slice.store_digest`) and is not part of this change.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | test_demo_capture EndToEndEditTestCase fails on hosts whose ffmpeg rejects `filter_complex_script` | high | low | attributed as pre-existing by the HEAD archive run; no demo module touched |
| `R-002` | The full checklist now runs inside `unittest discover` (468 s on this Windows host with per-item copies), lengthening the CI test jobs | high | medium | none in place beyond skipping where git is unavailable; raised as `Q-003` |
| `R-003` | The intermittent Windows `os.replace` save failure can make `M14` fail inside its copy | low | low | the copy is removed in `finally` (T-004) and the committed run is no longer the replay target |
| `R-004` | The git-unavailable fallback copies only the framework directory, so a verifier reading `tests/` there would see a narrower tree | low | medium | fallback triggers only when git cannot list the tree; `scratch_tree` requires the runtime sentinel in the listing before trusting it |
| `R-005` | A copy that cannot be removed is reported by a warning, not raised, so a temp copy can be left behind | low | low | the warning names the path; T-001 to T-004 assert removal on this host |
| `R-006` | `verify_self_hosting.py` fails `S8` until this run's change proposal is written | high | low | expected under the self-hosting profile; the proposal is written after closure |

## Handoff Notes

- Reviewer focus areas: `scratch_tree` copy-set selection and `_framework_excluded` (`C-002`, `V-001`); the `S11` verdict construction and the `copy_writes` record (`C-002`, `V-002`); the `M14` branch that re-copies a run outside `runs/` or not listed by git (`C-001`); the `finally` placement in `verify_recovery.py` (`C-003`); the CI duration effect of `C-005` (`R-002`).
- Follow-up work: Decide whether the checklist test stays in the default CI discovery path (`Q-003`); route the Windows save failure as its own defect (`Q-004`); decide whether committed replay records are re-baselined (`Q-005`); a test of the git-unavailable fallback if it is kept.
- Documentation impact: `runtime/README.md` and `validation/framework-release-checklist.md` are updated in this change (`C-006`, `C-007`); the change proposal for this framework-internal change is still to be written after closure.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | Confirm the amended `M14` copy scope (whole repository view minus other runs) in place of the gate's runtime-registry-run wording | no | tech-lead | `C-001`, `C-002` |
| `Q-002` | Confirm the content-digest comparison (plus no writes inside copies) in place of the gate's git status wording | no | tech-lead | `C-002`, `C-005` |
| `Q-003` | Should the multi-minute checklist test run in the default `unittest discover` CI path, or be gated or moved | no | qa | `C-005` |
| `Q-004` | Route the intermittent Windows `os.replace` PermissionError in the state store save as a separate defect | no | orchestrator | none |
| `Q-005` | Keep or re-baseline the replay records already committed in `run-c5a8d50d3238` under the point-in-time evidence rule | no | tech-lead | none |
