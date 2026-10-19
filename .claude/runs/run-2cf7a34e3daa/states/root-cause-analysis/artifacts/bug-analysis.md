```yaml
bugAnalysis:
  analysisId: BA-run-2cf7a34e3daa-rca-001
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
  contextDigest: sha256:a2e10c34bee5ac0f41eda6d9133bfd16
```

## Metadata

- Bug ID: DF-001
- Reporter: an independent review, filed as the defect report `runs/inputs/release-checklist-mutates-committed-runs-defect-report.md` (`E-001`)
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: Reproduced in this run, twice in the triage phase on this checkout (`E-004`, `E-008`) and twice in this phase in a fresh disposable copy of the working tree (`E-019`, `E-020`): running checklist item `FR-11` alone, or the full release checklist, leaves `state.json` and `task-context.yaml` of committed run `run-c5a8d50d3238` modified (refreshed `updated_at` stamps, guard details re-rendered from the current registry, appended replay records), while the verifier reports `M14` PASS. No other file is added, removed, or modified (`E-020`).
- Expected behavior: Per the defect report (`E-001`): the release checklist leaves the working tree byte-identical, each verifier still proves what it proves today when run alone, and `M14` still re-executes the runtime and still reports any side effect the re-execution produces.
- First observed date: Unknown from the report. Committed `state.json` of `run-c5a8d50d3238` already carries replay records dated 2026-08-18 to 2026-09-14 (`E-014`), so in-place replays predate the report.
- Affected environments: Known affected: this checkout on a Windows host (`E-004`, `E-008`) and a fresh git-initialised copy of the same working tree on that host (`E-019`, `E-020`); the reporter's clean checkout (reported, `E-001`). Known unaffected: none established. Not observed: Linux and macOS hosts, sandboxed shells, and CI runners, which never run the checklist or the `M14` replay (`E-030`).

## Reproduction

- Preconditions: `$FW` denotes the framework root directory under the repository root (the directory holding `runtime/`, `registry/`, and `runs/`). `git status --porcelain --untracked-files=all` lists nothing under `$FW/runs/run-c5a8d50d3238` (`E-003`, `E-017`); the committed run holds at least one `completed` phase, so `M14` issues `dispatch` and `complete` replays; commands run from the repository root. Run the steps in a disposable copy of the working tree (`E-017`) to avoid touching committed evidence.
- Steps to reproduce: 1) Copy the working tree, excluding `.git`, `__pycache__`, and any nested worktrees, to a temporary directory, then `git init` and commit everything there as a baseline. 2) In the copy, `git status --porcelain --untracked-files=all` prints nothing. 3) From the copy root run `python $FW/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238`: exit 0, `M14` PASS. 4) `git status --porcelain --untracked-files=all` lists `$FW/runs/run-c5a8d50d3238/state.json` and `task-context.yaml` as modified. 5) Reset the copy, then run `python $FW/runtime/verify_self_hosting.py --release-checklist` (about 90 s); step 4 shows the same two files and nothing else. 6) Control: repeat step 3 with `--no-replay`; the copy stays clean (`E-007`). 7) Delete the copy.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below (`E-001` to `E-030`).

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | DF-001 reports that the full release checklist exits 0 and leaves state.json and task-context.yaml of run-c5a8d50d3238 modified; it names FR-03, FR-04, and FR-11 as the items touching runs/ | supplied defect report, digest sha256:1baebc70bf310ad1b1104d5370b40dac | low |
| `E-002` | The dispatching host reported that, of the command items run alone, only FR-11 dirtied the tree; superseded by `E-018` and `E-020` | host observation passed to the triage phase; not run by this agent | low |
| `E-003` | Before triage reproduction, git status listed nothing under run-c5a8d50d3238 | git status --short, run in the triage phase of this run | high |
| `E-004` | Triage attempt 1: verify_multi_phase.py --run-id run-c5a8d50d3238 exited 1 with M14 FAIL (non-zero exit of plan); state.json and task-context.yaml were left modified | command run in the triage phase of this run; restored with git checkout | high |
| `E-005` | The attempt 1 diff rewrites run-level and per-item updated_at, re-renders the G1-CAPABILITY guard detail from the current registry, appends replay entries, and re-renders task-context.yaml updated_at and agent identifiers | git diff in the triage phase of this run | high |
| `E-006` | framework_runtime.py plan --run-id run-c5a8d50d3238 once exited 1 with PermissionError from os.replace in StateStore.save, leaving an untracked state.json.tmp | commands run in the triage phase of this run | high |
| `E-007` | Control: with --no-replay (M14 skipped) git status showed no change under the run | verify_multi_phase.py --no-replay, run in the triage phase of this run | high |
| `E-008` | Triage attempt 2: verifier exited 0 with M14 PASS (events 57 -> 57, transitions 30 -> 30, 257 replays recorded and suppressed), yet the same two files were modified | command run in the triage phase of this run | high |
| `E-009` | The checklist runner executes each command item with subprocess.run(shell=True, cwd=REPO), judges by return code only, and never compares the tree before and after | runtime/verify_self_hosting.py lines 402-421, read in this phase | high |
| `E-010` | The checklist declares FR-03 verify_recovery.py, FR-04 verify_vertical_slice.py and FR-11 verify_multi_phase.py, both with --run-id run-c5a8d50d3238; FR-11 is advisory | validation/framework-release-checklist.md, read in this phase | high |
| `E-011` | M14 re-runs plan, then dispatch and complete per completed phase, against the committed run with the repository root as cwd; fingerprint() compares only run id, event and transition counts, statuses, idempotency keys, and artifact digests | runtime/verify_multi_phase.py lines 116-133 and 541-571, read in this phase | high |
| `E-012` | StateStore.save stamps updated_at and rewrites state.json on every save; record_replay appends a persisted entry by design | runtime/state_engine.py, read in the triage phase of this run | high |
| `E-013` | refresh re-saves every item, guard details render from the live registry, and task-context.yaml is rewritten when anything but updated_at differs | runtime/framework_runtime.py, read in the triage phase of this run | high |
| `E-014` | At HEAD, run-c5a8d50d3238 state.json already holds 253 replay records dated 2026-08-18 to 2026-09-14 | git show and git log, run in the triage phase of this run | high |
| `E-015` | verify_recovery.py writes inputs and plans injected runs under runs/ through the runtime at the repository root; their removal runs once at the end of main(), after all scenarios, outside any try/finally | runtime/verify_recovery.py lines 118-178 and 1193-1242, read in this phase | high |
| `E-016` | verify_vertical_slice.py runs no subprocess and writes only with --json-out, which the checklist item does not pass | runtime/verify_vertical_slice.py, read in the triage phase of this run | high |
| `E-017` | The whole working tree (tracked, modified, and untracked files; .git and __pycache__ excluded) was copied to a temporary directory, git-initialised, and committed: 1865 files, git status empty | copy and git commands run in this phase; copy deleted afterwards | high |
| `E-018` | Run alone in the copy, each leaving git status empty and a full content-hash manifest (ignored files included) with 0 added, removed, or modified files: FR-01 exit 0, FR-02 exit 0, FR-03 exit 0 (59 s), FR-04 exit 0, FR-05 (the same command as FR-06) exit 1 | each command item run from the copy root in this phase, manifest compared before and after | high |
| `E-019` | Run alone in the copy, FR-11 exited 0 with 15/15 and M14 PASS; git status and manifest showed exactly state.json and task-context.yaml of run-c5a8d50d3238 modified (90 insertions, 18 deletions) | verify_multi_phase.py --run-id run-c5a8d50d3238, run in the copy in this phase | high |
| `E-020` | Full verify_self_hosting.py --release-checklist in the copy: exit 1 after 90 s; FR-01..FR-04 and FR-11 pass, FR-05/FR-06 fail; afterwards only the same two files were modified, 0 added or removed | command run from the copy root in this phase, manifest compared before and after | high |
| `E-021` | FR-05/FR-06 fail on S8 because in-flight run-2cf7a34e3daa has no change proposal yet; the read-only verify_self_hosting.py in the real tree gives identical verdict lines and left real git status unchanged | verify_self_hosting.py run in the copy and in the real tree in this phase | high |
| `E-022` | In the copy, verify_recovery.main() with scenario_b replaced in-process by a raising function exited 1 with the exception and left 18 untracked files: input recovery-injection-repaired.md and 17 files of injected run-62db758f9671 | in-process substitution run against the copy in this phase; no source file changed | high |
| `E-023` | A copy holding only runtime/, registry/ and runs/run-c5a8d50d3238 cannot replay: framework_runtime.py plan exited 2 with context-integrity-failure, command specificationPath does not resolve: commands/implement.md | command run in a second disposable copy in this phase | high |
| `E-024` | A copy of the whole framework tree minus other run directories replays: the copied verifier exited 0, 15/15, same M14 detail; the copy's run files changed and the source tree manifest did not; the runtime resolves its root from its own file location | command run in a third disposable copy in this phase; runtime/framework_runtime.py lines 117-118 | high |
| `E-025` | fingerprint() reads artifact digests at the module-level framework root joined with each run-relative artifact_path, not at the run directory it is given; the committed run's artifact paths are runs/run-c5a8d50d3238/states/... | runtime/verify_multi_phase.py line 122 and run-c5a8d50d3238 state.json, read in this phase | high |
| `E-026` | None of the checklist's verifiers, the runtime, or the state engine invokes git; copy-vs-real verdict parity is confirmed for FR-05 in `E-021` | grep over the nine runtime modules, run in this phase | high |
| `E-027` | The main checkout's framework root holds 14 nested worktrees, excluded only through the local .git/info/exclude; an existing test copies the framework tree to a temp directory ignoring runs, __pycache__, and worktrees, removed via addCleanup | directory listing and git check-ignore in the main checkout; tests/test_policy_exception_command.py lines 70-75, read in this phase | high |
| `E-028` | In the copy, a second write to an already-modified tracked file and to an untracked file left git status --porcelain --untracked-files=all output identical, while the content manifest showed both files changed | commands run in the copy in this phase | high |
| `E-029` | The real tree carries 1 modified tracked file and 24 untracked files under runs/ at analysis time, nothing under run-c5a8d50d3238; unchanged by this phase's copy work | git status --porcelain --untracked-files=all in the real tree, run in this phase | high |
| `E-030` | No test or CI step runs the release checklist or M14 with replay; CI runs python -m unittest discover -s tests | grep over tests/ and .github/, and .github/workflows/verify.yml, read in this phase | high |

## Impact Assessment

- User impact: Every contributor who runs the mandatory release step (`E-010`) must isolate or restore the committed run afterwards, or risk committing rewritten evidence. Verification verdicts are unaffected (`E-008`, `E-019`).
- Business impact: No business impact statement was supplied, so the severity rests on technical impact alone (`Q-005`).
- Technical impact: Integrity of committed point-in-time run evidence: each checklist run rewrites a past run's `state.json` and `task-context.yaml` with timestamps, current-registry guard details, and appended replay bookkeeping (`E-005`, `E-019`). Transitions, events, and artifacts stay unchanged (`E-008`). Originals are recoverable from version control: a primary path degrades with an acceptable workaround, so medium.
- Blast radius: (1) the release-checklist runner (`E-009`); (2) the multi-phase verifier's `M14` replay, for any run id passed, or for the most recently modified run, possibly in flight, when none is passed (`E-011`); (3) the runtime state store and task-context writer shared by every runtime command (`E-012`, `E-013`); (4) the committed run-evidence data boundary `runs/run-c5a8d50d3238`, the only writer being `FR-11` (`E-019`, `E-020`); (5) persisted data: replay records already committed at HEAD (`E-014`); (6) the version-control boundary, when a dirty tree is committed; (7) under a failed save, an added `state.json.tmp` in the committed run (`E-006`); (8) under a scenario exception, injected recovery inputs and runs left under `runs/`, now reproduced (`E-015`, `E-022`).

## Root Cause Analysis

- Root cause statement: The `M14` idempotency proof asserts "no new side effect" while replaying the runtime in place against committed run evidence, although the runtime's replay path persists bookkeeping by design and `M14`'s fingerprint excludes exactly that bookkeeping; the checklist runner then executes `FR-11`, the only writing item, at the repository root with no isolation and no tree-integrity check, so the contract mismatch lands on committed evidence undetected.
- Why detection failed earlier: `M14`'s `fingerprint()` omits `updated_at`, guard details, the `replays` lists, and `task-context.yaml`, and reports the growing replay count as success (`E-011`, `E-019`). The checklist runner judges by exit code only and never compares the tree (`E-009`). `FR-11` is advisory, so even an `M14` failure cannot fail the checklist (`E-010`). No test or CI step runs the checklist or the `M14` replay, so nothing ever observed the tree after it (`E-030`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Checklist trigger | The release checklist runs FR-11 against committed run-c5a8d50d3238 with the repository root as cwd and no isolation; FR-11 is the only item that writes | `E-009`, `E-010`, `E-018`, `E-020` | high |
| `C-002` | In-place replay | M14 re-executes runtime plan, dispatch, and complete on the run directory the runtime resolves from its own location; skipping M14 leaves the tree clean, relocating the runtime relocates the writes | `E-011`, `E-007`, `E-024` | high |
| `C-003` | Replay is not write-free | The runtime's replay path rewrites state by design: re-saved items with fresh stamps and registry-rendered guard details, appended replay records, re-rendered task-context.yaml | `E-012`, `E-013`, `E-005` | high |
| `C-004` | Side-effect definition mismatch | M14's fingerprint excludes every field the replay rewrites, so M14 passes while the store is rewritten | `E-011`, `E-008`, `E-019` | high |
| `C-005` | No tree-integrity check | The runner decides by return code only, FR-11 is advisory, and no test observes the tree afterwards, so the change goes undetected | `E-009`, `E-010`, `E-030` | high |
| `C-006` | Observed symptom | git status lists state.json and task-context.yaml of run-c5a8d50d3238 as modified after FR-11 or the full checklist, whether M14 passes or fails, and nothing else | `E-004`, `E-008`, `E-019`, `E-020` | high |

Alternatives tested: (a) the Windows save failure causes the dirt: eliminated, since a passing `M14` dirties the same files (`E-008`, `E-019`). (b) `FR-04` writes: eliminated by code read (`E-016`) and execution (`E-018`). (c) `FR-03` leaves residue: eliminated on a normal exit (`E-018`); the exception path does leave residue (`E-022`) but did not produce the reported symptom and is carried in the radius. (d) Other items write (`E-002`, reported): eliminated by per-item and full-checklist runs with content manifests (`E-018`, `E-020`).

## Fix Strategy

- Proposed fix: The release checklist and every verifier it runs, including each run alone, must leave every tracked and untracked file byte-identical. Strategy part (a), `M14` replay in a disposable copy removed in a finally block with unchanged verdict semantics, holds only with three conditions. First, the copy holds the whole framework tree the runtime resolves; runtime, registry, and run alone cannot plan (`E-023`). Other run directories and nested worktrees may be left out (`E-024`, `E-027`). Second, `fingerprint()` and the change report read the copy, not the module-level root (`E-025`); otherwise artifact digests are compared on untouched originals and a duplicated artifact write goes unseen. Third, `M14` reports the byte-level changes inside the copy, separating replay bookkeeping from a duplicated transition, event, or artifact. Strategy part (b), checklist items in a copy of the working tree as it is, holds with three conditions. The copy set is git's view of the working tree (tracked plus untracked-not-ignored), never a raw directory copy that drags in nested worktrees (`E-027`). Verdicts stay unchanged, since no verifier reads git (`E-021`, `E-026`). The integrity check compares file content of the whole tree, or at least of every dirty and untracked path, not porcelain lines only (`E-028`, `E-029`), and it also fails on writes an item makes inside the copy, so isolation does not mask a future regression of part (a). `verify_recovery.py` removes its injected runs and inputs even when a scenario raises (`E-022`). Persisted data: committed replay records (`E-014`) are left untouched and declared in the change record (`Q-002`).
- Alternative options: (a) Run the whole checklist in a copy only: simplest, but each verifier run alone still mutates evidence. (b) Snapshot and restore the run directory around `M14`: a crash between replay and restore leaves the mutation (`E-006`). (c) Make the runtime's replay path write-free: revises an intended runtime design (`E-012`), so structural and routed to `architect`. (d) Tree-integrity check alone: detects but does not remove. (e) Skip part (b)'s copy once part (a) holds, and keep only the integrity check on the real tree: no item writes after part (a) (`E-018`), and writes stay visible rather than discarded.
- Regression risk: medium
- Regression scope: `M14`, the only live idempotency proof, through the runtime commands `plan`/`dispatch`/`complete` and the root the runtime resolves from its file location (`E-024`); `fingerprint()` and `latest_state_run()` through the module-level root (`E-025`); `verify_recovery.py` through its import of `verify_multi_phase` (`E-015`) and its own cleanup path (`E-022`); the runner's `S10` verdict and exit code shared by `FR-05`/`FR-06` (`E-009`, `E-021`); the state-store save path on Windows inside a copy (`E-006`); CI duration through `unittest discover` if a checklist test lands in `tests/` (`E-030`, `E-020`).

## Validation Plan

- Verification steps: The reproduction inverted, run from a clean real tree and repeated with an existing dirty and untracked set (`E-029`). Run `verify_multi_phase.py --run-id run-c5a8d50d3238`, `verify_recovery.py`, and the full `--release-checklist`. After each, a content-hash manifest of the tree (ignored files aside) must be identical, and `M14` must still report the replayed commands and the byte-level bookkeeping it produced in its copy. An induced duplicate transition or artifact rewrite during replay must still fail `M14`. A raised `verify_recovery.py` scenario must leave no injected run or input. No temporary copy may remain afterwards, even when a replay or save fails mid-way.
- Regression tests added: the checklist run asserting an unchanged tree by file content, not porcelain only (`E-028`), and independent of the checklist verdict, since `FR-05`/`FR-06` can fail on `S8` for an in-flight run (`E-021`). Also: `M14` leaving `runs/run-c5a8d50d3238` byte-identical; `M14` failing on a non-bookkeeping side effect, feasible in a temp-tree fixture following the existing pattern (`E-027`); `verify_recovery.py` cleaning up when a scenario raises, inducible by in-process substitution (`E-022`); a test that the copy is removed when a replay command fails.
- Monitoring signals after release: Any tree change after a checklist run; replay-record count in committed run `state.json` files across commits (growth beyond 253 indicates recurrence, `E-014`); any `state.json.tmp` or `recovery-injection-*` file under `runs/`; leftover temporary copies in the system temp directory.

## Closure

- Resolution summary: None identified. The analysis is pending fix implementation; closure is decided at the Closure Gate, not here.
- Linked PR and release: None identified.
- Prevention actions: Every verifier that executes the runtime targets an isolated copy or proves a byte-level no-write; side-effect fingerprints cover every persisted byte and read the tree they replayed; the release checklist asserts working-tree integrity by content as a check in its own right; harness cleanup runs in a finally path.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Answered in this phase: no item other than FR-11 writes under the repository, alone or in a full checklist run (`E-018`, `E-020`); kept for traceability | no | qa | `C-001` |
| `Q-002` | Were the 253 replay records committed at HEAD (`E-014`) produced by earlier verifier replays, and should committed evidence keep them or be re-baselined under the point-in-time evidence rule? | no | tech-lead | `C-003` |
| `Q-003` | Answered in this phase: yes, a raised verify_recovery.py scenario leaves the injected input and run behind (`E-022`); cleanup outside finally confirmed by source (`E-015`) | no | qa | none |
| `Q-004` | Separate defect to route: StateStore.save intermittently fails os.replace with PermissionError on Windows, making plan exit 1, failing M14, and leaving state.json.tmp (`E-006`, `E-004`) | no | orchestrator | none |
| `Q-005` | No business impact statement was supplied; confirm the business consequence the technically derived severity (medium) is weighed against | no | product-owner | none |
| `Q-006` | The Triage Gate condition names a copy holding runtime, registry, and run; evidence shows that copy cannot plan (`E-023`) while the whole framework tree minus other runs can (`E-024`); confirm the amended copy scope | no | tech-lead | none |
| `Q-007` | The Triage Gate condition fails on a git status difference; porcelain lines miss repeat writes to dirty or untracked files (`E-028`), present in this tree now (`E-029`); confirm a content-based comparison | no | tech-lead | none |
