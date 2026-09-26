# Change Request — Demo mode (`/implement --demo`), runtime 0.8.0

## Change class

`capability-addition`, as classified by `config/self-hosting-profile.md` and confirmed by
`python .claude/runtime/self_hosting.py classify --path .claude/runtime/demo/editor.py`.
The framework gains a runtime behaviour it did not have. Routed to `/implement` over
`workflows/implement-feature.md`, entry phase `scope-and-acceptance`.

## What changes

### New: the demo package, `runtime/demo/` (14 modules, about 5,600 lines)

| Module | Responsibility |
|---|---|
| `__init__.py` | The public surface and the three integration points; the autonomous-build claim |
| `context.py` | `DemoContext`: the per-run switch and its options |
| `recorder.py` | Canonical events, on-disk envelopes, and host tool hooks to execution markers |
| `timeline.py` | Markers to presentation scenes; the three narration registers |
| `narration.py` | Text-to-speech engine chain, delivery rate, WAV assembly |
| `captions.py` | Spoken lines to timed cues, a subtitle file, and a script |
| `obs_ws.py` | A standard-library obs-websocket v5 client |
| `capture.py` | Window targeting, both capture backends, the capture manifest |
| `capture_helper.py` | The detached process that owns a recording and watches for occlusion |
| `overlays.py` | The presentation frame drawn around the footage |
| `editor.py` | Edit decision list, narration fitting, the ffmpeg cut |
| `renderer.py`, `video_builder.py`, `deck.py` | The drawn-dashboard fallback when nothing was filmed |

### Modified: `runtime/framework_runtime.py`

- `RUNTIME_VERSION` 0.7.0 to 0.8.0.
- `add_request_args` gains the `--demo` parameter group (seven optional flags).
- `plan_run` gains `enable_demo()`, called after the execution request is written and before
  the first event, so the recording opens on the run being accepted.
- `RunLedger.emit` gains a tap guarded by one `Path.exists()`.
- A new `demo` subcommand: status, build, backfill, host hook, record start and stop.

### Modified: registry and command contract

- `registry/commands.yaml`: the `implement` record 1.0.0 to 1.1.0 (MINOR, additive parameters
  with safe defaults, per the versioning strategy in `domain-model/command-specification.md`).
- `commands/implement.md`: a Parameters section documenting the flag group.

### Modified: CLI wrapper and documentation

- `omn_agent/cli.py`, `runner.py`, `update.py`: `--demo` forwarded to the runtime.
- `runtime/README.md`, `docs/USER-GUIDE.md` (section 5g) and its rendered HTML, `README.md`.

### New: tests

`tests/test_demo_mode.py`, `test_demo_capture.py`, `test_demo_pacing.py`,
`test_demo_captions.py`, and `tests/fixtures/fake_obs.py` — 1,718 lines, 92 cases.

## What does not change

No workflow specification, Phase Model, gate matrix, agent contract, artifact template,
validator, state transition table, recovery policy, or existing registry record other than the
`implement` command's own version. No existing test was weakened; two were tightened where
this change made their former assertions wrong.

## Defects found and fixed during the change

Each was found by inspecting output, not by reading code:

1. Window-level `gdigrab` returns black frames on a GPU-composited Electron window.
2. ffmpeg on Windows ignores `q` on a piped stdin, so recordings were never finalised; they
   are now Matroska and stopped with a console break.
3. `SW_RESTORE` un-maximises a maximised window.
4. A variable-rate capture defeats `tpad`, so every hold silently padded nothing.
5. The ffmpeg backend films a place on the screen, so a window losing focus filmed the
   operator's desktop. Occlusion is now watched for, recovered from, and excluded.
6. `run_completed` fires before the closing gate is decided, so the camera stopped one beat
   short of the final approval.
7. The film was compiled twice, because two events both mean "finished".

## Rollback

Delete `runtime/demo/` and the four test modules, revert the three integration points in
`framework_runtime.py`, restore `RUNTIME_VERSION` to 0.7.0, revert the `implement` record to
1.0.0 and its specification, and revert the CLI and documentation edits. No run evidence
outside `runs/<run>/demo/` is invalidated, because nothing else was written.
