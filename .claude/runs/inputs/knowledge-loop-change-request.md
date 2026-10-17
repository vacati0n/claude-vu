# Change Request — Knowledge Management Loop

## Change class

`capability-addition` per `config/self-hosting-profile.md` Routing Table: the framework gains a
runtime behaviour (harvest, govern, recall) and a governed memory category it did not have.

Classification evidence: `python .claude/runtime/self_hosting.py route --intent capability-addition`
returns `/implement` over `implement-feature` at `scope-and-acceptance`;
`self_hosting.py classify` on `runtime/framework_runtime.py` and on `memory/README.md` both return
framework-internal (`SR-1`).

## Surfaces this change is expected to touch

| Surface | Nature of change |
|---|---|
| `runtime/` (new module, carrier chosen in design) | Harvest, fingerprint upsert, lifecycle, recall, effectiveness accounting; CLI |
| `runtime/framework_runtime.py` | Populate `memory_slice` and a prompt section at dispatch for runs that opted in; trigger harvest on aggregation; `RUNTIME_VERSION` increments |
| `runtime/execution_metrics.py` | Lessons hydrated per invocation |
| `memory/` | New governed lessons store; `README.md`, `memory-governance.md`, `memory-resolver.md` describe the category |
| `config/runtime.md` | Memory Loading and Writeback Policy describe the implemented behaviour and the opt-in rule |
| `tests/`, `runtime/verify_*.py` | Unit tests for harvest idempotency, eligibility, recall ranking, and backward compatibility |
| `omn_agent/_bundled_payload/**` | Mirror refresh via `python tests/test_bundled_payload.py --sync` |

## Not touched

Gates, validators, templates of existing artifacts, Phase Model tables, agent module text.
