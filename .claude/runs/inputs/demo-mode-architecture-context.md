# Architecture Context — Where demo mode sits in the runtime

## Current-state structure this change extends

`runtime/framework_runtime.py` (about 5,700 lines) implements the executable subset of
`config/runtime.md` and `config/execution-engine.md`. The components relevant here:

- **Execution Context Store** (`RunLedger`). Owns `runs/<run>/events.jsonl`, an append-only
  stream of the fifteen canonical event types in `CANONICAL_EVENTS`. Every state change in a
  run passes through `RunLedger.emit`, which is therefore the single point at which the whole
  progress of a run is observable.
- **Agent Invocation Gateway** (`cmd_dispatch`). Writes the canonical Agent Invocation Envelope
  and the dispatch prompt to `runs/<run>/states/<phase>/`, then leases to the host-subagent
  adapter. The runtime core never talks to a model, so this boundary is the only place the
  exchange with an agent is visible.
- **Validation Engine** (`VALIDATORS`). Writes `validation-report.json` per phase.
- **Task Context** (`task_context.py`) and **execution metrics** (`execution_metrics.py`),
  added in 0.7.0, which already derive per-run documents from persisted evidence only.

## The architectural fact this change rests on

The runtime already records everything a demonstration needs, in order, with timestamps, and
already writes the prompt and the result to disk at the moment each is complete. Nothing new
has to be instrumented. What was missing was a consumer of that record, and a clock that ties
it to a picture.

## Design constraints inherited from the existing architecture

1. **The runtime core owns control flow; adapters own external integration.** Screen capture,
   OBS, ffmpeg, and speech synthesis are external integrations and must sit behind the same
   kind of boundary the model adapters sit behind, not inside the execution path.
2. **Deliberately not implemented** (`runtime/README.md`): a metrics pipeline. Demo mode must
   not become one by the back door. Markers exist to cut a film.
3. **`config/execution-engine.md`**: recovery behaviour is policy-driven and failures are
   classified, never handled at the call site. A demo failure is not a run failure and must
   not enter that machinery at all; it is caught and logged.
4. **Zero-bloat context** (`config/runtime.md`, Progressive Module Loading). Runtime 0.7.0 was
   an effort to reduce what a dispatch reads. A new capability must not add to it.
5. **The installed form.** `FW_PREFIX` exists because the framework is `.claude/` in its own
   repository and `.omn-agent/` once installed elsewhere. Anything path-facing must derive
   from it.

## Integration surface available

`RunLedger.emit` is the natural tap: one function, every event, already ordered and stamped.
The cost of a guard there is one `stat()` per event. `plan_run` is the natural place to arm
the capability, because it is where a run is materialised and where the execution request is
written. `main()`'s subparser set is where an operator-facing surface is added.

## Prior art in this repository to reuse rather than reinvent

- `execution_metrics.py` already estimates per-dispatch context cost and is the right source
  for the token figures a film reports.
- `task_context.py` already parses artifacts deterministically, never by summarisation; the
  same discipline applies to anything a marker asserts.
- `artifact_lib.py` provides shared artifact parsing.
- The colorized `status` tree in `framework_runtime.py` already establishes a visual
  vocabulary for phases, gates, and their statuses.

## Known environmental facts

- Windows is the operator platform. OBS Studio 32.2.2 is installed with obs-websocket
  bundled, but its server is disabled and its configuration is not writable by the agent.
- No system ffmpeg; Pillow is present; Windows SAPI voices are available.
- Claude Desktop is an Electron application: window class `Chrome_WidgetWin_1`, packaged under
  WindowsApps, GPU-composited.

## Risks this change must address

- **Publication risk.** A screen recording may capture something that was not part of the run.
  This is the dominant risk and the architecture must make it impossible to publish silently.
- **Dependency risk.** Three optional external tools, each absent on some host.
- **Evidence risk.** A film is a claim about a run. It must be derivable from the run's own
  record, and it must state where it condensed time.
