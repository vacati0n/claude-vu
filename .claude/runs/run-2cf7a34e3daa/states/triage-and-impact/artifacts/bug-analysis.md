```yaml
bugAnalysis:
  analysisId: BA-run-2cf7a34e3daa-triage-001
  defectReference: DF-001
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/release-checklist-mutates-committed-runs-defect-report.md
  producedBy: dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:1baebc70bf310ad1b1104d5370b40dac
  contextDigest: sha256:d349d25df9ecf914b11063912c8be2cd
```

## Metadata

- Bug ID: DF-001
- Reporter: an independent review, filed as the defect report `runs/inputs/release-checklist-mutates-committed-runs-defect-report.md` (`E-001`)
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: Reproduced here: running the release checklist item `FR-11` (`verify_multi_phase.py --run-id run-c5a8d50d3238`) on a clean tree leaves `.claude/runs/run-c5a8d50d3238/state.json` and `task-context.yaml` modified, with refreshed `updated_at` stamps, guard `detail` strings re-rendered with current agent identifiers and versions, and new replay records appended (`E-004`, `E-005`, `E-008`). Reported, not re-run here: the full `--release-checklist` exits 0 and leaves the same two files modified (`E-001`, `E-002`).
- Expected behavior: Per the defect report (`E-001`), the release checklist leaves the working tree byte-identical (no modified, added, or deleted file), and each verifier still proves what it proves today when run alone, with `M14` still re-executing the runtime and still reporting any side effect.
- First observed date: Unknown from the report. The committed `state.json` of run-c5a8d50d3238 already carries replay records dated 2026-08-18 to 2026-09-14 (`E-014`), so in-place replays against that run predate the report.
- Affected environments: Known affected: this repository checkout on a Windows host with Python and Git Bash (`E-004`, `E-008`); the reporter's clean checkout (reported, `E-001`). Known unaffected: none established. Not observed: Linux and macOS hosts, CI runners, and sandboxed shells.

## Reproduction

- Preconditions: The working tree is clean for `.claude/runs/run-c5a8d50d3238` (`git status --short` lists nothing under it, as confirmed here in `E-003`), the committed run is present, and the commands run from the repository root. The run under replay must hold at least one `completed` phase, so that `M14` issues `dispatch` and `complete` replays.
- Steps to reproduce: 1) From the repository root run `git status --short` and confirm that nothing under `.claude/runs/run-c5a8d50d3238` is listed. 2) Run `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238`. 3) Run `git status --short` again: `M .claude/runs/run-c5a8d50d3238/state.json` and `M .claude/runs/run-c5a8d50d3238/task-context.yaml` are listed, and `git diff` shows the rewrites described in `E-005`. 4) Restore with `git checkout -- .claude/runs/run-c5a8d50d3238`. 5) As a control, repeat step 2 with `--no-replay` added; the tree stays clean (`E-007`). Restore was performed after every attempt here.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below (`E-001` to `E-016`).

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | DF-001 reports that the full release checklist exits 0 and leaves state.json and task-context.yaml of run-c5a8d50d3238 modified; it names FR-03, FR-04, and FR-11 as the items that touch .claude/runs/ | supplied defect report, digest sha256:1baebc70bf310ad1b1104d5370b40dac | low |
| `E-002` | The dispatching host reports that the full checklist dirtied the same two files and that, of the command items run alone, only FR-11 dirtied the tree; verify_recovery.py and verify_vertical_slice.py left it clean | host observation passed in the dispatch task; not run in this analysis | low |
| `E-003` | Before reproduction, git status --short listed only this run's untracked input and run directory; nothing under run-c5a8d50d3238 | git status --short, run in this analysis | high |
| `E-004` | Attempt 1: verify_multi_phase.py --run-id run-c5a8d50d3238 exited 1 with M14 FAIL ("non-zero exits: plan, dispatch execution-planning"); afterwards state.json and task-context.yaml were modified | command run in this analysis; restored with git checkout | high |
| `E-005` | The attempt 1 diff shows the run-level and per-item updated_at rewritten to the replay time, the G1-CAPABILITY guard detail re-rendered from the current registry (e.g. documentation v1.0.0 to v1.2.0, agent identifiers without their prefix), and replay entries appended to the per-item and run-level replays lists. In task-context.yaml, updated_at and the relevant_agents identifiers are re-rendered | git diff after attempt 1 | high |
| `E-006` | Running framework_runtime.py plan --run-id run-c5a8d50d3238 directly exited 1 with PermissionError [WinError 5] from os.replace of state.json.tmp in StateStore.save, leaving an untracked state.json.tmp; a following dispatch replay exited 0 ("REPLAY ... dispatch suppressed") and the temp file was gone | commands run in this analysis; restored with git checkout | high |
| `E-007` | Control: with --no-replay (M14 skipped), the verifier ran M0 to M13 and git status --short showed no change under the run | verify_multi_phase.py --run-id run-c5a8d50d3238 --no-replay, run in this analysis | high |
| `E-008` | Attempt 2: the same verifier exited 0 with M14 PASS ("events 57 -> 57, transitions 30 -> 30, artifact digests unchanged, 257 replay(s) recorded and suppressed"), yet the same two files were modified (state.json +90 lines) | command run in this analysis; restored with git checkout | high |
| `E-009` | The checklist runner executes every command-mode item through subprocess.run(..., shell=True, cwd=REPO), decides pass or fail from the return code alone, and makes no comparison of the working tree before and after | .claude/runtime/verify_self_hosting.py, release-checklist block (about lines 398-417), read in this analysis | high |
| `E-010` | The checklist declares FR-11 (advisory) as verify_multi_phase.py --run-id run-c5a8d50d3238, FR-04 as verify_vertical_slice.py --run-id run-c5a8d50d3238, and FR-03 as verify_recovery.py | .claude/validation/framework-release-checklist.md, read in this analysis | high |
| `E-011` | M14 re-runs plan, then dispatch and complete for each completed phase, in place against .claude/runs/<run-id> with the repository root as cwd. fingerprint() compares only the run id, event count, transition count, statuses, idempotency keys, and artifact digests. Without --run-id, the verifier targets the most recently modified run | .claude/runtime/verify_multi_phase.py lines 102-133, 541-571, and 591, read in this analysis | high |
| `E-012` | StateStore.save stamps updated_at and rewrites state.json through a temp file and os.replace on every save. set_eligibility saves unconditionally. record_replay appends a persisted entry and saves, and its docstring states that the entry is, by design, the evidence that the replay was suppressed | .claude/runtime/state_engine.py lines 346-350, 476-488, and 518-538, read in this analysis | high |
| `E-013` | refresh calls set_eligibility for every item. evaluate_state_guards renders the G1-CAPABILITY detail from the live registry resolution. refresh_task_context rewrites task-context.yaml whenever anything other than updated_at differs | .claude/runtime/framework_runtime.py lines 2183-2189, 2447, and 3851-3872, read in this analysis | high |
| `E-014` | At HEAD, run-c5a8d50d3238 state.json already holds 253 replay records, dated 2026-08-18T09:28:51Z to 2026-09-14T05:23:45Z; the file was last committed on 2026-09-26 | git show HEAD:...state.json, git log, run in this analysis | high |
| `E-015` | verify_recovery.py plans injected runs and writes inputs under .claude/runs/ through the runtime, with the repository root as cwd. Their removal runs at the end of main(), after every scenario, and not in a finally block; --keep retains them | .claude/runtime/verify_recovery.py lines 121-171 and 1193-1242, read in this analysis | high |
| `E-016` | verify_vertical_slice.py runs no subprocess and writes only when --json-out is given, which the checklist item does not pass | .claude/runtime/verify_vertical_slice.py, read in this analysis | high |

## Impact Assessment

- User impact: Every contributor who runs the mandatory release step (`E-010`) must restore or isolate the committed run afterwards, or risk committing rewritten evidence. Verification verdicts are unaffected (`E-008`).
- Business impact: No business impact statement was supplied, so the severity rests on technical impact alone (`Q-005`).
- Technical impact: Integrity of committed point-in-time run evidence. Each checklist run rewrites a past run's `state.json` and `task-context.yaml`: timestamps, guard details restated as the current registry (agent versions included), and appended replay bookkeeping (`E-005`, `E-008`). Transitions, events, and artifacts stay unchanged (`E-008`). The originals are recoverable from version control, so the effect is medium: the primary path still returns correct results, but its evidence degrades, and the workaround is acceptable.
- Blast radius: (1) the release-checklist runner (`E-009`); (2) the multi-phase verifier's `M14` replay, for any run id passed, or for the most recently modified run, which may be in flight, when none is passed (`E-011`); (3) the runtime state store and task-context writer shared by every runtime command (`E-012`, `E-013`); (4) the committed run-evidence data boundary, `.claude/runs/run-c5a8d50d3238` (`E-004`, `E-008`); (5) persisted data: replay records and a post-carry `updated_at` already committed at `HEAD` (`E-014`); (6) the version-control boundary, when a contributor commits the dirty tree; (7) under a failed save, an added `state.json.tmp` in the committed run directory (`E-006`); (8) latent: injected recovery runs and inputs under `.claude/runs/` if `verify_recovery.py` aborts mid-scenario (`E-015`, `Q-003`).

## Root Cause Analysis

- Root cause statement: The `M14` idempotency proof asserts "no new side effect" while replaying the runtime in place against committed evidence, but the runtime's replay path persists bookkeeping by design and `M14`'s fingerprint excludes exactly that bookkeeping. This contract mismatch is compounded by a checklist runner that executes items against the live repository with no isolation and no tree-integrity check.
- Why detection failed earlier: `M14`'s `fingerprint()` omits `updated_at`, guard details, the `replays` lists, and `task-context.yaml`, and it reports the growing replay count as success (`E-008`, `E-011`). The checklist runner judges by exit code only and never compares `git status` before and after (`E-009`). `FR-11` is advisory, so even an `M14` failure cannot fail the checklist (`E-010`). No automated test runs the checklist and asserts an unchanged tree.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Checklist trigger | The release checklist runs FR-11 against committed run-c5a8d50d3238, with the repository root as cwd and no isolation | `E-009`, `E-010` | high |
| `C-002` | In-place replay | M14 re-executes runtime plan, dispatch, and complete directly on the committed run directory; skipping M14 leaves the tree clean | `E-011`, `E-007` | high |
| `C-003` | Replay is not write-free | The runtime's replay path rewrites state by design: plan re-saves every item with fresh stamps and registry-rendered guard details, replays append persisted records, and task-context.yaml is re-rendered | `E-012`, `E-013`, `E-005` | high |
| `C-004` | Side-effect definition mismatch | M14's fingerprint excludes every field the replay rewrites, so it passes while the store is rewritten | `E-011`, `E-008` | high |
| `C-005` | No tree-integrity check | The runner decides by return code only, and FR-11 is advisory, so the checklist completes without detecting the change | `E-009`, `E-010`, `E-008` | high |
| `C-006` | Observed symptom | git status lists state.json and task-context.yaml of run-c5a8d50d3238 as modified after FR-11, whether M14 passes or fails | `E-004`, `E-008` | high |

Alternatives tested: (a) The dirt comes from the Windows save failure in attempt 1: eliminated, because attempt 2 passed `M14` and still dirtied the same files (`E-008`). (b) `FR-04` writes: eliminated by code read (`E-016`). (c) `FR-03` leaves residue: eliminated on a normal exit by code read (`E-015`); the crash path stays open as `Q-003`. (d) Other checklist items also write: reported as not doing so (`E-002`) but not re-run here, so it stays open as `Q-001`.

## Fix Strategy

- Proposed fix: The release checklist and every verifier it runs must leave all tracked and untracked files under the repository byte-identical. `M14` must still re-execute the runtime against the same request, but its re-execution must not land on committed evidence. It must report every byte-level change the re-execution produced, distinguishing suppressed-replay bookkeeping from a duplicated transition, event, or artifact. The checklist must detect and report any working-tree change its items cause. Persisted data: the replay records already committed at `HEAD` (`E-014`) are left untouched by this fix, because rewriting committed evidence is itself prohibited, and they are declared in the change record; whether to keep them is `Q-002`. This strategy is conditional on `Q-001` confirming that `FR-11` is the only writer.
- Alternative options: (a) Run the whole checklist in a disposable copy of the tree, as contributors do today: simplest, but each verifier run alone still mutates evidence. (b) Snapshot the run directory and restore it after `M14`: keeps the in-place semantics, but a crash between replay and restore leaves the mutation behind (`E-006` shows such crashes occur). (c) Make the runtime's replay path write-free: this revises an intended runtime design (`E-012`), so it is structural and routed to `architect`, not proposed here. (d) Add only a tree-integrity check to the runner: it detects the problem but does not remove it.
- Regression risk: medium
- Regression scope: `M14`, the only live idempotency proof, through the shared runtime commands `plan`/`dispatch`/`complete` and the fixed `.claude/runs` root that the runtime resolves; `verify_recovery.py`, which imports `verify_multi_phase.run_checks` (`E-015`); the checklist runner's `S10` verdict and exit code, shared by `FR-05` and `FR-06` through `verify_self_hosting.py` (`E-009`); the state-store save path (`E-012`), if the replay target changes; and Windows file-replace behaviour on the replay target (`E-006`).

## Validation Plan

- Verification steps: The reproduction inverted. From a clean tree, run `verify_multi_phase.py --run-id run-c5a8d50d3238` and then the full `verify_self_hosting.py --release-checklist`; each time `git status --porcelain --untracked-files=all` must be unchanged, `M14` must still report the replayed commands and the effects they produced, and an induced duplicate transition or artifact change during replay must still fail `M14`. Repeat with a forced failure mid-replay and confirm that the committed run is still byte-identical.
- Regression tests added: an automated test that runs the release checklist and asserts that `git status --porcelain --untracked-files=all` is identical before and after; a test that `M14` detects a non-bookkeeping side effect and reports bookkeeping effects without touching committed evidence; a test that `verify_recovery.py` removes its injected runs when a scenario raises.
- Monitoring signals after release: Any non-empty `git status` after a checklist run; the replay-record count in committed run `state.json` files across commits (any growth from 253 indicates recurrence); any `state.json.tmp` or `recovery-injection-*` file under `.claude/runs/`.

## Closure

- Resolution summary: None identified. The analysis is pending fix implementation and the Triage Gate decision, owned by `tech-lead`.
- Linked PR and release: None identified.
- Prevention actions: Each verifier that executes the runtime must target an isolated copy or prove a byte-level no-write. A side-effect fingerprint must cover every persisted byte, not a chosen subset. The release checklist must assert working-tree integrity as a check in its own right.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Do any items other than FR-11 write under the repository during a full checklist run? This was reported as no (`E-002`) but not re-run here; run the full checklist with M14 isolated and compare the tree | no | qa | `C-001` |
| `Q-002` | Were the 253 replay records and the prefixed guard details committed at HEAD (`E-014`) produced by earlier verifier replays, and should committed evidence keep them or be re-baselined under the point-in-time evidence rule? | no | tech-lead | `C-003` |
| `Q-003` | Does an exception inside a verify_recovery.py scenario leave injected runs and inputs under .claude/runs/? Settle it by inducing a scenario failure | no | qa | none |
| `Q-004` | Separate defect to route: StateStore.save intermittently fails os.replace with PermissionError on Windows, which makes plan exit 1, fails M14, and leaves state.json.tmp (`E-006`, `E-004`) | no | orchestrator | none |
| `Q-005` | No business impact statement was supplied; confirm the business consequence that the technically derived severity (medium) is weighed against | no | product-owner | none |
