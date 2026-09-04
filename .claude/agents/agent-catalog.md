# Agent Catalog

## Objective

Provide a quick routing map from intent to the right specialist agent.

## Intent Routing

| Intent | Primary Agent | Supporting Agents |
|---|---|---|
| Engineering planning and task decomposition | planner | omn-product-owner, omn-business-analyst, omn-tech-lead |
| Feature implementation | omn-dev-1-implement | planner, architect, omn-dev-2-reviewer, omn-qa |
| Bug fixing | omn-dev-1-bug-analyst | omn-dev-1-implement, omn-qa, omn-tech-lead |
| Architectural change | architect | omn-tech-lead, omn-dev-2-reviewer, planner |
| Product and requirement clarification | omn-product-owner | omn-business-analyst |
| Documentation updates | omn-documentation | omn-dev-2-reviewer, omn-product-owner |
| Repository quality scan | omn-dev-2-reviewer | omn-tech-lead |
| Release preparation | omn-tech-lead | omn-qa, omn-orchestrator, omn-documentation |
| Cross-cutting orchestration | omn-orchestrator | all relevant specialists |

## Host Entry Points

Every agent named as a phase owner by an active workflow Phase Model is host-invocable
through `agents/<agent-id>.agent.md`.

| Agent | Entry point | Contract layout | Registry record |
|---|---|---|---|
| planner | `agents/planner.agent.md` | runtime module set | present |
| architect | `agents/architect.agent.md` | runtime module set | present |
| omn-product-owner | `agents/omn-product-owner.agent.md` | runtime module set | present |
| omn-business-analyst | `agents/omn-business-analyst.agent.md` | runtime module set | present |
| omn-context-agent | `agents/omn-context-agent.agent.md` | runtime module set | present |
| omn-tech-lead | `agents/omn-tech-lead.agent.md` | runtime module set | present |
| omn-dev-1-bug-analyst | `agents/omn-dev-1-bug-analyst.agent.md` | runtime module set | present |
| omn-dev-1-implement | `agents/omn-dev-1-implement.agent.md` | runtime module set | present |
| omn-dev-2-reviewer | `agents/omn-dev-2-reviewer.agent.md` | runtime module set | present |
| omn-qa | `agents/omn-qa.agent.md` | runtime module set | present |
| omn-documentation | `agents/omn-documentation.agent.md` | runtime module set | present |
| omn-orchestrator | `agents/omn-orchestrator.agent.md` | runtime module set | present |

## Retired Roles

`orchestrator`, `backend-developer`, and `omn-planning-generate-clarification-questions` are
retired. None owns a phase in any active Phase Model, none has a contract on disk, and each
holds a `retired` record in `registry/agents.yaml` so the runtime rejects it by status rather
than failing to resolve it. `agents/retired-roles.md` records the reason and superseding role
for each; route work as follows.

| Retired identifier | Route to |
|---|---|
| `orchestrator` | `omn-orchestrator` |
| `backend-developer` | `omn-dev-1-implement` |
| `omn-planning-generate-clarification-questions` | `omn-business-analyst` |

## Escalation Rules

- Escalate unresolved design conflicts to `architect`.
- Escalate schedule or delivery risk to `omn-tech-lead` and `omn-orchestrator`.
- Escalate acceptance ambiguity to `omn-product-owner`.
- Route requirement-to-task decomposition to `planner` before implementation begins.
- Route impact analysis and technical approach to `architect` before implementation begins.
- `omn-architect` is deprecated; it names the architecture role now implemented by `architect`.
