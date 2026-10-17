# Architecture Context — Knowledge Management Loop

- The runtime core never talks to a model (`runtime/framework_runtime.py` header). It builds the
  canonical envelope and hands it to an adapter. Lessons are therefore data carried in the envelope
  and rendered into the dispatch prompt.
- The envelope already reserves `memory_slice` (today `{hydrated: false, reason: ...}`) and the
  context slice records `excluded: memory/*`. `config/runtime.md` says memory hydration is opt-in per
  run. Envelope additions since 0.7.0 are additive; `model_tier` (0.9.0) is the latest precedent.
- The idempotency key (`cmd_dispatch`) names the unit of work and must survive a rollback; replay
  checks (`verify_multi_phase` M12 and M14) re-run commands against committed run
  `run-c5a8d50d3238` and require stable output. A run whose `execution-request.json` predates the
  opt-in must therefore dispatch exactly as today.
- Evidence sources on disk: `runs/<run>/events.jsonl` (`validation_failed` carries
  `details_ref.failures`, a list of check IDs, and `details_ref.report`; `rollback_scheduled` carries
  gate and target), `runs/<run>/recovery-ledger.json` (`failure_class`, `guard`, `reason_code`), and
  `runs/<run>/states/<phase>/validation-report.json` (each check's `id`, `description`, `severity`;
  the file is overwritten by later attempts, so descriptions resolve from any report of the same
  artifact type). Gate-approval waits (`approval_wait`) are normal flow, not lessons.
- `runs/` and `proposals/` are excluded from the bundled payload and from implementer writes; the
  lesson store must therefore live under `memory/`, and harvest must tolerate a repository with no
  `runs/` (an installed copy).
- `runtime/optimize_memory.py` rewrites `memory/*.md` for token cost; a machine-maintained store
  must not be mangled by it (check its scan rules).
- Keep loading policy in runtime and `config/`, never in agent modules (`verify_vertical_slice` C10).
- `runtime/README.md` is large and read by agents; new documentation goes in `config/runtime.md`
  and the `memory/` documents.
- Edit the framework directory, then `python tests/test_bundled_payload.py --sync`; never hand-edit
  `omn_agent/_bundled_payload/`. The full unit suite takes about 26 minutes.
- Artifact validators reject the substring of the host vendor name (check `C3.2`); write paths
  without the dot-directory prefix.
