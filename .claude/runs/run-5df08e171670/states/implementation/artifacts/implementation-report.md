```yaml
implementationReport:
  reportId: IR-2026-1014
  changeReference: run-5df08e171670 / demonstration capture capability (/implement --demo), runtime 0.8.0, delivered in commit 2e9e99e
  sourceInputs:
    - type: technical-design
      reference: runs/run-5df08e171670/states/solution-design-and-risk-assessment/artifacts/technical-design.md
    - type: feature-request
      reference: runs/inputs/demo-mode-feature-request.md
    - type: change-request
      reference: runs/inputs/demo-mode-change-request.md
    - type: business-intent
      reference: runs/inputs/demo-mode-business-intent.md
    - type: architecture-context
      reference: runs/inputs/demo-mode-architecture-context.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: implementation
  verificationStatus: partially-verified
  inputDigest: sha256:54c8a7a4d8c82861eec77601136ce5b9
  contextDigest: sha256:71b01b435a6f92e7b8bf1d1a67c8c50d
```

## Metadata

- Report ID: IR-2026-1014
- Change reference: run-5df08e171670 / demonstration capture capability (/implement --demo), runtime 0.8.0, delivered in commit 2e9e99e
- Workflow phase: implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

## Implementation Summary

- Change intent: A run planned with `--demo` records every governed step as a millisecond-stamped marker, can film the target application window through a detached helper, and compiles a captioned, narrated presentation exactly once after its last gate is decided; a run planned without it reaches the demo package only through one existence check per emitted event.
- Approach taken: No code was written in this invocation. The whole change set was committed in 2e9e99e (2026-09-26), before this phase was dispatched (2026-10-17T12:22:49Z); this phase maps that delivered code onto design M-001 to M-022 and decisions D-001 to D-010 at HEAD 097e8f4 and runs the repository's own tests against it (V-001). The design records the new package, modules, and test files as already delivered, at the rung where a new file is justified: no existing runtime component draws, films, or edits, and each optional tool (Pillow, ffmpeg, OBS Studio, speech engines) stays behind a recorded fallback rather than becoming a dependency (D-006). Demo-related lines in `.claude/runtime/framework_runtime.py` have not changed since 2e9e99e (V-004).
- Design reference: technical-design.md for run-5df08e171670, impacted modules M-001 to M-022, decisions D-001 to D-010, sequencing P-001 to P-011, acceptance criteria AC-001 to AC-014.
- Out of scope: M-023 to M-028 (Phase Model, gate matrix, state transition table and recovery classification, artifact templates and validators, other command records, agent contracts) are cleared by the design as no-change-verified and were not touched; files in commit 2e9e99e outside M-001 to M-022 (other change proposals, run evidence, user-guide reconciliation fixtures) belong to other recorded changes and are not accounted here.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `.claude/runtime/demo/__init__.py` | added | Public surface, event tap, finish check over the state store, and the once-only compilation claim | M-001, D-001, D-005 |
| `C-002` | `.claude/runtime/demo/context.py` | added | Per-run switch file and persisted demo options | M-002, D-001 |
| `C-003` | `.claude/runtime/demo/recorder.py` | added | Events, envelopes, validation reports, and host tool calls to de-duplicated markers | M-003, D-008 |
| `C-004` | `.claude/runtime/demo/timeline.py` | added | Markers to scenes and the three narration registers | M-004, D-009 |
| `C-005` | `.claude/runtime/demo/narration.py` | added | Speech-engine chain, delivery rate, and WAV assembly with recorded fallback | M-005, D-006 |
| `C-006` | `.claude/runtime/demo/captions.py` | added | Timed caption cues, subtitle file, and presenter script | M-006, D-009 |
| `C-007` | `.claude/runtime/demo/obs_ws.py` | added | Standard-library obs-websocket v5 client for the preferred backend | M-007, D-003 |
| `C-008` | `.claude/runtime/demo/capture.py` | added | Window targeting, both capture backends, and the capture manifest | M-008, D-003 |
| `C-009` | `.claude/runtime/demo/capture_helper.py` | added | Detached process that owns the recording and samples occlusion | M-009, D-002 |
| `C-010` | `.claude/runtime/demo/overlays.py` | added | Presentation frame drawn around the footage | M-010, D-009 |
| `C-011` | `.claude/runtime/demo/editor.py` | added | Edit decision list, narration fitting, withheld-span exclusion, and the encoder cut | M-011, D-003, D-006 |
| `C-012` | `.claude/runtime/demo/renderer.py` | added | Drawn-dashboard frames for the lowest substitution rung | M-012, D-006 |
| `C-013` | `.claude/runtime/demo/video_builder.py` | added | Frames and narration to an output, plus the build manifest | M-013, D-006 |
| `C-014` | `.claude/runtime/demo/deck.py` | added | Self-contained HTML deck that is always produced | M-014, D-006 |
| `C-015` | `.claude/runtime/demo/hooks.settings.json` | added | Operator-merged host tool-hook fragment read through the runs-root pointer | M-015, D-001 |
| `C-016` | `.claude/runtime/framework_runtime.py` | modified | Four guarded sites (ledger tap, plan arming, status display, demo subcommand) and the `--demo` parameter group | M-016, D-001, D-007 |
| `C-017` | `.claude/commands/implement.md` | modified | Published documentation of the `--demo` parameter group | M-017, D-007 |
| `C-018` | `.claude/registry/commands.yaml` | modified | Implement record raised to 1.1.0 with the additive parameter group | M-018, D-007 |
| `C-019` | `omn_agent/cli.py` | modified | Wrapper accepts `--demo` on run | M-019 |
| `C-020` | `omn_agent/runner.py` | modified | Wrapper forwards `--demo` to the runtime plan call | M-019 |
| `C-021` | `omn_agent/update.py` | modified | Wrapper forwards `--demo` on re-plan and materialize argv | M-019 |
| `C-022` | `.claude/runtime/README.md` | modified | Documents the demo runtime surface | M-020 |
| `C-023` | `README.md` | modified | Repository readme rows for the demo command forms | M-020 |
| `C-024` | `docs/USER-GUIDE.md` | modified | Operator instructions for demo mode | M-020 |
| `C-025` | `docs/user-guide.html` | modified | Rendered output of the user guide | M-020 |
| `C-026` | `tests/fixtures/fake_obs.py` | added | Local control-server fixture for backend tests | M-021 |
| `C-027` | `tests/test_demo_captions.py` | added | Caption, subtitle, and script tests | M-021 |
| `C-028` | `tests/test_demo_capture.py` | added | Capture, edit, occlusion, routing, and end-to-end edit tests | M-021 |
| `C-029` | `tests/test_demo_mode.py` | added | Switch, recorder, timeline, builder, and CLI tests | M-021 |
| `C-030` | `tests/test_demo_pacing.py` | added | Pacing, plain-language narration, and fitting tests | M-021 |
| `C-031` | `omn_agent/_bundled_payload/commands/implement.md` | modified | Installable copy of C-017 | M-022 |
| `C-032` | `omn_agent/_bundled_payload/registry/commands.yaml` | modified | Installable copy of C-018 | M-022 |
| `C-033` | `omn_agent/_bundled_payload/runtime/README.md` | modified | Installable copy of C-022 | M-022 |
| `C-034` | `omn_agent/_bundled_payload/runtime/demo/__init__.py` | added | Installable copy of C-001 | M-022 |
| `C-035` | `omn_agent/_bundled_payload/runtime/demo/captions.py` | added | Installable copy of C-006 | M-022 |
| `C-036` | `omn_agent/_bundled_payload/runtime/demo/capture.py` | added | Installable copy of C-008 | M-022 |
| `C-037` | `omn_agent/_bundled_payload/runtime/demo/capture_helper.py` | added | Installable copy of C-009 | M-022 |
| `C-038` | `omn_agent/_bundled_payload/runtime/demo/context.py` | added | Installable copy of C-002 | M-022 |
| `C-039` | `omn_agent/_bundled_payload/runtime/demo/deck.py` | added | Installable copy of C-014 | M-022 |
| `C-040` | `omn_agent/_bundled_payload/runtime/demo/editor.py` | added | Installable copy of C-011 | M-022 |
| `C-041` | `omn_agent/_bundled_payload/runtime/demo/hooks.settings.json` | added | Installable copy of C-015 | M-022 |
| `C-042` | `omn_agent/_bundled_payload/runtime/demo/narration.py` | added | Installable copy of C-005 | M-022 |
| `C-043` | `omn_agent/_bundled_payload/runtime/demo/obs_ws.py` | added | Installable copy of C-007 | M-022 |
| `C-044` | `omn_agent/_bundled_payload/runtime/demo/overlays.py` | added | Installable copy of C-010 | M-022 |
| `C-045` | `omn_agent/_bundled_payload/runtime/demo/recorder.py` | added | Installable copy of C-003 | M-022 |
| `C-046` | `omn_agent/_bundled_payload/runtime/demo/renderer.py` | added | Installable copy of C-012 | M-022 |
| `C-047` | `omn_agent/_bundled_payload/runtime/demo/timeline.py` | added | Installable copy of C-004 | M-022 |
| `C-048` | `omn_agent/_bundled_payload/runtime/demo/video_builder.py` | added | Installable copy of C-013 | M-022 |
| `C-049` | `omn_agent/_bundled_payload/runtime/framework_runtime.py` | modified | Installable copy of C-016 | M-022 |
| `C-050` | `tests/__pycache__/test_demo_captions.cpython-314.pyc` | added | Compiled bytecode of C-027 committed with the change | V-005 |
| `C-051` | `tests/__pycache__/test_demo_capture.cpython-314.pyc` | added | Compiled bytecode of C-028 committed with the change | V-005 |
| `C-052` | `tests/__pycache__/test_demo_mode.cpython-314.pyc` | added | Compiled bytecode of C-029 committed with the change | V-005 |
| `C-053` | `tests/__pycache__/test_demo_pacing.cpython-314.pyc` | added | Compiled bytecode of C-030 committed with the change | V-005 |
| `C-054` | `tests/fixtures/__pycache__/fake_obs.cpython-314.pyc` | added | Compiled bytecode of C-026 committed with the change | V-005 |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Full repository suite as regression baseline: 771 run, 767 pass, 4 fail (the three in T-012 and the one in T-022) | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005`, `C-006`, `C-007`, `C-008`, `C-009`, `C-010`, `C-011`, `C-012`, `C-013`, `C-014`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049`, `C-050`, `C-051`, `C-052`, `C-053`, `C-054` | `PYTHONDONTWRITEBYTECODE=1 python tools/run_tests_parallel.py` | fail |
| `T-002` | Demo is off by default, costs nothing, and writes nothing; enable is idempotent; a recorder fault never reaches the runtime (3 tests) | unit | `C-001`, `C-002`, `C-016` | `cd tests && python -m unittest test_demo_mode.DemoSwitchTestCase` | pass |
| `T-003` | Markers carry ms stamps and sequence; replayed event yields no second marker; host hook lands on the active run only; backfill runs once (6 tests) | unit | `C-001`, `C-003` | `cd tests && python -m unittest test_demo_mode.RecorderTestCase` | pass |
| `T-004` | Not finished while a gate is undecided or a phase runs; compiled once whatever the number of finish events; occluded or wholly hidden footage never published (6 tests) | unit | `C-001`, `C-008`, `C-011` | `cd tests && python -m unittest test_demo_capture.FinishAndOcclusionTestCase` | pass |
| `T-005` | HTML deck always produced with fallbacks recorded; GIF fallback without ffmpeg; mp4 path; film waits for the last gate; run completion triggers build (5 tests) | integration | `C-001`, `C-012`, `C-013`, `C-014` | `cd tests && python -m unittest test_demo_mode.BuilderTestCase` | pass |
| `T-006` | Caption splitting and timing, overlay slicing, well-formed subtitle file, script with every spoken line, captions on by default (19 tests) | unit | `C-002`, `C-006`, `C-010` | `cd tests && python -m unittest test_demo_captions` | pass |
| `T-007` | Bookkeeping folded, compression never cuts narration, scenes deterministic (3 tests) | unit | `C-004` | `cd tests && python -m unittest test_demo_mode.TimelineTestCase` | pass |
| `T-008` | Relaxed pace, plain-language explanation of every beat, fit-to-narration, rebalance, speech rate reaches the engine, filtergraph pacing (22 tests) | unit | `C-004`, `C-005`, `C-011` | `cd tests && python -m unittest test_demo_pacing` | pass |
| `T-009` | Control-server config read from the host; probe never raises without an installation; connect failure names the port (3 tests) | unit | `C-007` | `cd tests && python -m unittest test_demo_capture.ObsWebSocketTestCase` | pass |
| `T-010` | Preferred backend authenticates, provisions, records, and stops against the fixture; wrong password refused (3 tests) | integration | `C-007`, `C-008`, `C-026` | `cd tests && python -m unittest test_demo_capture.FakeObsBackendTestCase` | pass |
| `T-011` | Capture manifest: absent, recorded, in-progress states; a second recording is refused (4 tests) | unit | `C-008` | `cd tests && python -m unittest test_demo_capture.CaptureManifestTestCase` | pass |
| `T-012` | End-to-end edit through the installed encoder: playable shorter film, recorded edit decision list, recording audio never published (3 tests: 1 failure, 2 errors) | end-to-end | `C-008`, `C-011` | `cd tests && python -m unittest test_demo_capture.EndToEndEditTestCase` | fail |
| `T-013` | Frame is canvas-sized with a footage hole, aspect ratio kept, long title shrunk, closing card carries run numbers (4 tests) | unit | `C-010` | `cd tests && python -m unittest test_demo_capture.OverlayTestCase` | pass |
| `T-014` | Markers map onto video time; late start excludes missed beats; head-and-tail condensation; cut never longer than its source; filtergraph declares every segment (8 tests) | unit | `C-011` | `cd tests && python -m unittest test_demo_capture.EditDecisionTestCase` | pass |
| `T-015` | Build routing: dashboard without a recording, edit with one, forced drawn mode, failed edit falls back to the dashboard, edit without recording reports (5 tests) | integration | `C-011`, `C-012`, `C-013` | `cd tests && python -m unittest test_demo_capture.BuildRoutingTestCase` | pass |
| `T-016` | Status, backfill, hook inert without an active run, printed hook matches the shipped fragment, wrapper forwards the flag, flag declared on every request parser (6 tests) | integration | `C-015`, `C-016`, `C-019`, `C-020` | `cd tests && python -m unittest test_demo_mode.CliTestCase` | pass |
| `T-017` | Self-hosting release checklist: 7 of 9 pass; S8 fails because run-5df08e171670 has no change proposal yet, and S10 fails on FR-05 and FR-06 for the same cause | static | `C-016`, `C-018` | `python .claude/runtime/verify_self_hosting.py --release-checklist` | fail |
| `T-018` | Registry coverage: every active command record, including implement, resolves to its workflow (8 of 8) | static | `C-018` | `python .claude/runtime/verify_registry_coverage.py` | pass |
| `T-019` | Wrapper CLI and runner regression suite (45 tests) | regression | `C-019`, `C-020` | `cd tests && python -m unittest test_omn_agent` | pass |
| `T-020` | Wrapper update regression suite (14 tests) | regression | `C-021` | `cd tests && python -m unittest test_update` | pass |
| `T-021` | Rendered user guide matches its Markdown source (74 tests) | static | `C-024`, `C-025` | `cd tests && python -m unittest test_render_user_guide` | pass |
| `T-022` | Bundled payload parity: stale list names only `runtime/verify_recovery.py`, which is not in this change set; demo copies match their sources | regression | `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049` | `PYTHONDONTWRITEBYTECODE=1 python tools/run_tests_parallel.py test_bundled_payload` | fail |

## Verification Results

- Verification method: Ran the repository's own unittest suites, per test class for the demo modules and per module for the wrapper, user-guide, and payload checks, plus the framework verifiers, at HEAD 097e8f4 with the working tree as found at dispatch. This invocation made no source change, so the T-001 baseline is also the post-change state. The demo modules were run twice (parallel runner, then per class) and both runs gave the same result.
- Commands executed: `PYTHONDONTWRITEBYTECODE=1 python tools/run_tests_parallel.py test_demo_mode test_demo_capture test_demo_pacing test_demo_captions` (100 run, 97 pass, 3 fail); `PYTHONDONTWRITEBYTECODE=1 python tools/run_tests_parallel.py` (771 run, 767 pass, 4 fail); the per-class and per-module commands in T-002 to T-022; `python .claude/runtime/verify_manifests.py` (2/2 pass); `python .claude/runtime/verify_validators.py` (6/6 pass); `python .claude/runtime/verify_registry_coverage.py` (8/8 pass); `python .claude/runtime/verify_self_hosting.py --release-checklist`, run twice (7/9); `git log`, `git show --stat`, `git diff --stat`, and `git status --short` to establish provenance; `git checkout --` on two run-evidence files to revert the verifier's writes (R-003); `ffmpeg -version` to identify the installed encoder (9.0.2).
- Result summary: 22 evidence entries executed, 18 passed, 4 failed (T-001, T-012, T-017, T-022). Demo tests: 100 executed, 97 passed, 3 failed. Full suite: 771 executed, 767 passed, 4 failed. Framework verifiers: 4 executed, 3 passed, 1 failed. Cause of each failure: T-012, the installed encoder 9.0.2 rejects the `-filter_complex_script` option the delivered editor passes (R-001); T-022, an uncommitted working-tree change to `.claude/runtime/verify_recovery.py` that was present before dispatch (R-002); T-017, this run has no change proposal yet (R-006).
- Unverified areas: the end-to-end filmed edit and audio stripping on this host (C-011, C-008), because T-012 fails; the occlusion-sampling helper C-009, which has no direct test; agreement between the documented parameter surface in C-017 and the parser in C-016, which no test checks (V-003); the demo-flag forwarding in C-021, which no test asserts directly; accuracy of the documentation in C-022 and C-023, checked by inspection only; the C-050 to C-054 bytecode; the live-run demonstrations for AC-001, AC-004, AC-006, AC-007, AC-009, AC-010, AC-012, and AC-013, which need governed recorded runs and a first-time viewer and were not executed in this phase; and the verifiers `verify_vertical_slice.py`, `verify_multi_phase.py`, and `verify_recovery.py`, which were not run because they exercise run directories.

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | C-001 to C-054 were committed in 2e9e99e on 2026-09-26, before this phase was dispatched on 2026-10-17; this phase records the code rather than implementing it, and no pre-change baseline could be taken | Workflow order (implementation follows the Design Gate) and reasoning Stage 2 baseline | Git history shows the commit is an ancestor of HEAD 097e8f4; the operator directive for this phase forbids source modification | Q-002 to omn-tech-lead |
| `V-002` | The T-012 encoder failure at C-011 was left unrepaired | D-006 substitution ladder; AC-002 and AC-008 end-to-end evidence | The operator directive forbids source modification, and a correction changes delivered behaviour the design accepted | Q-001 to architect |
| `V-003` | The parameter-surface reconciliation was not performed: the parser in C-016 registers 10 flags, C-017 documents all 10 in 9 rows, C-018 states only an additive group, and the change-request says seven | P-003 sequencing; AC-014 | This invocation may write only its two outputs, and reconciliation needs a documentation edit | Q-003 to omn-documentation |
| `V-004` | C-016 and C-049 are accounted at HEAD, with `RUNTIME_VERSION` 0.10.0 after later recorded changes, not at the 0.8.0 the design targets; demo-related lines are unchanged since 2e9e99e | M-016 target shape (runtime version 0.8.0) | `git diff 2e9e99e HEAD` on the file shows no changed line mentioning demo; the version bumps are governed by their own proposals | not-required |
| `V-005` | C-050 to C-054 are committed bytecode that serves no accepted element | M-021 test set | The repository already tracks `tests/__pycache__`; they are recorded so the change set is complete | not-required |
| `V-006` | C-001 to C-054 share commit 2e9e99e with 477 unrelated files, so the change cannot be reverted as one commit | Rollback and Rollout position; git collaboration standard (single-purpose commits) | `git show --stat 2e9e99e` reports 531 files changed; rollback must be path-scoped as the design lists | not-required |

## Boundary Compliance

- Module boundaries preserved: By inspection at HEAD, the runtime reaches the demo package only at the four guarded sites in C-016: the ledger tap behind a demo-context existence check, plan arming behind the `--demo` flag, the status display behind the same existence check, and the demo subcommand. Each import is lazy. T-002 shows a fault in the recorder does not reach the runtime. M-023 to M-028 were not touched.
- Public interface changes: Additive only. C-016 adds an optional `--demo` parameter group (default off) and a `demo` subcommand; C-017 and C-018 publish it, with the implement record at 1.1.0; C-019 to C-021 forward the flag. No existing parameter changes meaning.
- Data or migration impact: None identified. No schema or migration. New on-disk state is created only under `runs/<run>/demo/` and at the `runs/.active-demo` pointer, and only the demo layer writes or reads it (D-008, D-010).
- Declared side effects: This invocation wrote only `.claude/runs/run-5df08e171670/states/implementation/artifacts/implementation-report.md` and `.claude/runs/run-5df08e171670/states/implementation/result-envelope.json`. The C-001 to C-054 files were produced outside this invocation, in commit 2e9e99e, and this report records them (V-001). One transient write also happened: running `verify_self_hosting.py --release-checklist` appended replay records to `.claude/runs/run-c5a8d50d3238/state.json` and `.claude/runs/run-c5a8d50d3238/task-context.yaml`. Both files were clean at dispatch, and both were restored to their HEAD content with `git checkout --`, so they carry no net change (R-003).

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | The installed encoder 9.0.2 rejects `-filter_complex_script`, so every filmed edit on this host fails (C-011) | high | A filmed run on this host falls back to the drawn dashboard, which does not meet the filmed-material requirement, and AC-002 and AC-008 cannot be shown end to end | In place: a failed edit falls back to the dashboard and records the error in the build manifest (T-015) |
| `R-002` | An uncommitted change to `.claude/runtime/verify_recovery.py`, present before dispatch and outside this change set, breaks bundled payload parity | high | The suite and T-022 stay red for a reason unrelated to this change | In place: the `git status` taken at dispatch shows the file already modified, and the T-022 stale list names only that file |
| `R-003` | Running `verify_self_hosting.py --release-checklist` writes replay records into committed run evidence | high | Committed run evidence of run-c5a8d50d3238 is modified whenever the verifier runs | In place: this invocation detected the writes with `git status` and restored both files to their HEAD content |
| `R-004` | The occlusion-sampling helper C-009 has no direct automated test, and publication safety depends on it | medium | An occluded span the helper misses could reach a finished presentation | In place: T-004 shows that occluded spans recorded in the manifest are excluded and a wholly hidden recording publishes nothing |
| `R-005` | Rollback needs a path-scoped revert across C-001 to C-054 because the commit mixes changes (V-006) | medium | A careless revert of 2e9e99e would undo unrelated recorded changes | In place: the design's Rollout and Rollback section lists the paths to revert |
| `R-006` | Self-hosting S8, FR-05, and FR-06 stay failing until a change proposal links this run (T-017) | high | The framework release checklist cannot pass for this change | In place: none in this phase; the item is carried as follow-up work |
| `R-007` | The documented and parsed parameter surfaces are offered as AC-014 evidence before they are reconciled (V-003) | medium | The additive-version claim rests on contract surfaces that disagree on the size of the group | In place: the disagreement is recorded here with its counts |

## Handoff Notes

- Reviewer focus areas: C-011 encoder invocation and its fallback (V-002, R-001); C-009 helper with no direct test (R-004); C-016, C-017, and C-018 parameter-surface agreement (V-003, R-007); the four guarded sites in C-016 and the lazy-import zero-cost claim; whether recording delivered code after the fact satisfies the workflow (V-001); path-scoped rollback (V-006).
- Follow-up work: a decision on encoder-version compatibility in C-011 (Q-001); P-003 reconciliation of C-016, C-017, and C-018 (Q-003); a change proposal linking this run, which the closure phase owns (R-006); resolving the uncommitted `verify_recovery.py` change (Q-004); stopping `verify_self_hosting.py` from writing run evidence (Q-005); the live recorded-run demonstrations for the acceptance criteria named under Unverified areas, owned by omn-qa.
- Documentation impact: C-017 may need its parameter count reconciled with the parser (V-003). Documentation in C-022 to C-025 describes the delivered surface and was checked only by inspection and by the T-021 render check. Release communication belongs to the closure phase.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | Is the T-012 failure, where encoder 9.0.2 rejects `-filter_complex_script`, an unsupported-environment limitation or a delivered defect that needs a design-accepted correction? | yes | architect | `C-011`, `C-040` |
| `Q-002` | Does the Review Gate owner accept an implementation phase that records code committed before the phase was dispatched, with no pre-change baseline? | no | omn-tech-lead | `C-001`, `C-016`, `C-049` |
| `Q-003` | Who performs the P-003 reconciliation of the parser, the published parameter documentation, and the registry record, given that this phase may not write them? | no | omn-documentation | `C-016`, `C-017`, `C-018` |
| `Q-004` | Should the uncommitted working-tree change to `.claude/runtime/verify_recovery.py` be committed and synced to the bundled payload, or reverted? | no | omn-orchestrator | `C-031` to `C-049` |
| `Q-005` | Should `verify_self_hosting.py --release-checklist` stop writing replay records into committed run evidence when it runs? | no | omn-orchestrator | none in this change set |
