# Change Request — Lesson Store as an Open Knowledge Format Bundle

## Change class

The change class is `capability-addition`, per the Routing Table in `config/self-hosting-profile.md`.
The framework gains two things it did not have: a new storage contract for lessons (an OKF v0.2
bundle) and a conformance-check capability.

Classification evidence:
- `python .claude/runtime/self_hosting.py classify --path` returns framework-internal (`SR-1`) for
  both `runtime/knowledge.py` and `memory/lessons/lessons.store.json`.
- `python .claude/runtime/self_hosting.py route --intent capability-addition` returns
  `/implement` over `implement-feature` v1.0.0 at `scope-and-acceptance`.

## Surfaces this change is expected to touch

| Surface | Nature of change |
|---|---|
| `runtime/knowledge.py` | Bundle reader and writer, frontmatter serialiser and parser, migration, OKF §11 conformance check, command line |
| `runtime/` (verifier; the carrier is chosen in design) | Standalone deterministic OKF conformance verifier |
| `validation/framework-release-checklist.md` | Possibly an advisory item that runs the conformance verifier |
| `memory/lessons/` | The JSON store is replaced by the bundle: `index.md`, `log.md`, and one concept document per lesson |
| `memory/README.md`, `memory/memory-governance.md`, `memory/memory-resolver.md`, `config/runtime.md` | Describe the bundle |
| `runtime/optimize_memory.py` | Possibly: keep the bundle out of the optimiser |
| `omn_agent/source.py` | The installer exclusion covers the bundle |
| `tests/test_knowledge.py` | Tests for bundle round trip, idempotency, migration and conformance |
| `omn_agent/_bundled_payload/**` | Mirror refreshed with `python tests/test_bundled_payload.py --sync` |

## Not touched

The change does not touch gates, artifact validators, Phase Model tables, agent module text, or run
evidence under `runs/`.
