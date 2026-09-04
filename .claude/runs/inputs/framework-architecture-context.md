# Architecture Context: AI Engineering Framework

Supplied by the operator for the `solution-design-and-risk-assessment` phase of the
Reviewer Agent change. The system under design is the framework in this repository, so the
current-state architecture is the framework's own structure.

This document does not restate that structure. It names the authoritative records of it.
Every file named below is a member of the frozen context slice recorded in this run's
`context-snapshot.json`, so a fact drawn from one carries a citable digest.

## Component model

The framework is composed of five component types, each with a discovery registry and a
specification set:

| Component type | Discovery registry | Specification |
|---|---|---|
| Agents | `registry/agents.yaml` | `domain-model/agent-specification.md` |
| Skills | `registry/skills.yaml` | `skills/agent-skill-matrix.md` |
| Workflows | `registry/workflows.yaml` | `workflows/implement-feature.md` and siblings |
| Templates | `registry/templates.yaml` | `templates/` |
| Commands | `registry/commands.yaml` | `commands/` |

`dependency-map.md` records the permitted dependency directions between them.
`agents/capability-matrix.md` records capability ownership.
`workflows/workflow-gate-matrix.md` records gate ownership.

## Execution surface

`runtime/README.md` records what of the runtime is implemented, what is specification only,
and the gaps the current slices leave open. It is the current-state record for anything
concerning invocation, adapters, validation, or run evidence.

## What the change must be designed against

The Reviewer Agent change described by the accompanying change request, business intent,
and execution plan is a change to this framework. Its impact surface is therefore made of
framework components: registry records, agent contract module sets, artifact templates,
governance matrices, workflow phase rows, and the runtime's resolution and validation path.

## Known current-state properties the operator asserts

These are supplied as context, not as design conclusions. Each is verifiable in the files
named above.

1. Two agents hold registry records at status `active`: `planner` and `architect`. The
   `omn-*` contracts and `orchestrator`, `backend-developer` hold no registry record.
2. An agent becomes invocable when it holds an active registry record, a manifest with a
   resolvable module load order, a host registration at `agents/<agent-id>.agent.md`, and a
   workflow phase that routes to it with an output artifact the runtime can validate.
3. Review responsibility today sits with `omn-dev-2-reviewer`, which owns the Review Gate
   and the review-pull-request Readiness Gate in the gate matrix, and holds no registry
   record.
4. The runtime executes two phases of `implement-feature`: `execution-planning` and
   `solution-design-and-risk-assessment`. No other phase has a registered validator.

## Constraints the operator places on the design

- Registration and governance records are the framework's own contract surface. A change to
  one is a contract change, not an implementation detail.
- The framework's discovery registries are single-authority. A second authority for the
  same identity metadata is a defect, not a design option.
- No change to gate ownership is authorized by this request without it being recorded as a
  decision with the gate matrix owners named.
