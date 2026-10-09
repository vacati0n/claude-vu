# Architecture Context — Per-Phase Model Tier

- The runtime core never talks to a model (`runtime/framework_runtime.py` header). It builds the
  canonical envelope and hands it to an adapter. A tier is therefore advice carried in the envelope.
- Envelope fields added in 0.7.0 are additive; a consumer reading only the original eleven fields
  reads them unchanged. `model_tier` follows the same rule.
- All twelve `agents/*.agent.md` entrypoints declare `model: inherit`. The host (Claude Code) accepts
  a per-dispatch model override on subagent invocation, which is how a tier hint becomes effective;
  the entrypoint frontmatter stays `inherit`.
- Workflow Phase Model tables are parsed by the Task Router; adding a column would change a parsed
  contract, so tier data lives outside them, keyed by workflow and phase.
- Replay checks (M14) require artifacts written by `write_run_ledger` to be stable when content is
  unchanged; any new field must be deterministic from run state.
- Rejected attempts are recorded in the run's recovery ledger and attempt counters; escalation must
  derive from that recorded state, not from in-memory state.
- Keep loading policy in runtime and `config/`, never in agent modules (`verify_vertical_slice` C10).
- `runtime/README.md` is large and read by agents; new documentation goes in `config/runtime.md`.
- Edit `.claude/`, then `python tests/test_bundled_payload.py --sync`; never hand-edit `omn_agent/_bundled_payload/`.
