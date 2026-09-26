# Feature Request — Autonomous end-to-end demonstration capture (`/implement --demo`)

## Source

Operator request, 2026-09-08, extended 2026-09-12 and 2026-09-14. Type: capability addition.
Priority: High — the capability exists to support a live product presentation, and the
framework had no way to show itself working.

## Request

The framework can execute a governed multi-agent run but cannot *show* one. Explaining it to
someone who has not seen it means talking over a state table. Add a capability by which a run
records itself and produces a distribution-ready demonstration film with no human editing
step, so that a presenter has evidence rather than assertions.

Three deliverables, in the order they were asked for:

1. **`/implement --demo`.** An optional flag on the existing command that turns on recording
   for a run. Every canonical runtime event, dispatch prompt, agent result, validation
   verdict, gate decision, and host tool call becomes a millisecond-stamped execution marker.
   At run completion the framework compiles the presentation itself, with no further command.
2. **Film the real application.** The first implementation drew a synthetic dashboard. That
   was rejected: the demonstration must show Claude Desktop actually doing the work, recorded
   from the screen, with the marker stream used to decide where to cut rather than to draw.
3. **Explain it to a non-technical audience.** The first cut ran 35 seconds with terse
   technical narration. The audience is older and non-technical, so the film must run for
   several minutes, explain every step in plain language, show each spoken line on screen as
   a caption, and be accompanied by a written script the presenter can read beforehand.

## Acceptance criteria

- `--demo` on `plan` records a run; without it the demo package is never imported and the
  runtime's only cost is one file-existence check per emitted event.
- Markers carry UTC millisecond timestamps and the exchange with each agent as observed at
  the adapter boundary; a replayed event does not produce a second marker.
- A recording of the Claude Desktop window can be started and stopped from the runtime, keeps
  running while the run proceeds, and records the instant its own clock read zero.
- The editor maps every marker onto a frame of that recording and cuts the footage against the
  run, condensing waiting with the factor stated on screen.
- A demonstration for a first-time audience runs to minutes, is narrated in plain language,
  carries captions, and ships with a script and a subtitle file.
- Footage that filmed anything other than the target window is never published.
- A run that completes while filming stops its own camera and compiles the film once.
- Absent optional dependencies degrade to a recorded fallback rather than a failure.
- The existing test suite stays green and the framework verifiers continue to pass.

## Constraints

- Additive only. No change to gate semantics, the Producer Exclusion Rule, the state machine,
  recovery classification, or any existing artifact contract.
- No new mandatory dependency. Pillow, ffmpeg, OBS Studio, and every text-to-speech engine are
  optional, and each absence must be a recorded fallback.
- Nothing in the demo layer may raise into the run it observes.
- Only the target window may ever be recorded, and the recording's own audio is never
  published.
