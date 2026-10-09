# Change Request — Per-Phase Model Tier

## Change class

`capability-addition` per `config/self-hosting-profile.md` Routing Table: the framework gains a
registry record and a runtime behaviour it did not have.

Classification evidence: `python .claude/runtime/self_hosting.py route --intent capability-addition`
returns `/implement` over `implement-feature` at `scope-and-acceptance`.

## Surfaces this change is expected to touch

| Surface | Nature of change |
|---|---|
| `registry/` or `config/` | One authoritative tier declaration and tier-to-host-hint mapping (carrier chosen in design) |
| `runtime/framework_runtime.py` | Resolve tier at dispatch, emit additive `model_tier` envelope field, escalation on prior rejection; `RUNTIME_VERSION` increments |
| `runtime/execution_metrics.py` | Report invocations and bytes by tier |
| `config/execution-engine.md`, `config/runtime.md` | Document the envelope field and escalation rule |
| `runtime/verify_*.py`, `tests/` | Verify the declaration covers every dispatchable phase and that escalation is monotonic |
| `omn_agent/_bundled_payload/**` | Mirror refresh via `python tests/test_bundled_payload.py --sync` |

## Not touched

Agent module text, workflow Phase Model tables, gate matrix, validators, templates.
