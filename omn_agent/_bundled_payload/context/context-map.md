# Context Map

## Purpose

Define where authoritative context is stored and when to update each artifact.

## Artifacts

| Context File | Scope | Owner | Update Trigger |
|---|---|---|---|
| `product-context.md` | Product goals, users, outcomes | omn-product-owner | Requirement or roadmap changes |
| `technical-context.md` | Stack and architecture constraints | omn-tech-lead | Architecture/runtime changes |
| `release-context.md` | Release cadence and risks | omn-orchestrator | Release policy or risk model changes |
| `../dependency-map.md` | Module/project dependency graph and blast-radius record | omn-context-agent | A project or module dependency changes; regenerate with `omn-agent context generate dependency-map` |

## Change Discipline

- Update context before starting implementation if assumptions changed.
- Reference context updates in investigation and design outputs.
- Keep context concise and conflict-free.
