# Business Intent — Wave 1 Delivery Core Agent Rollout

## Outcome sought

The framework can carry a change from scope through implementation, review, and quality
without an operator standing in for a missing agent at each step.

## Value

Today the framework decides the route, holds the gates, and keeps the record, but executes
3 of its 36 phases. Every other phase is performed by the operator against the run and recorded
as a blocked phase in a change proposal. That is honest, and it does not scale: the operator is
the bottleneck for every increment, and the framework's own claim to be self-hosting rests on
routing rather than on execution.

Wave 1 converts the delivery core from recorded-blocked to executed. The measurable value is
the number of phases that dispatch and the number of active workflows with a completed run.

## Success criteria

| ID | Criterion | Measure |
|---|---|---|
| `BI-1` | The four Wave 1 agents hold active registry records | `registry/agents.yaml` active record count rises from 2 to 6 |
| `BI-2` | Each of the four has a runtime module set whose load order resolves | 6 module sets under `agents/*/manifest.yaml` |
| `BI-3` | At least one phase owned by a Wave 1 agent dispatches and completes | `verify_registry_coverage.py` C6 dispatchable count rises above 3 |
| `BI-4` | The artifact of every executed Wave 1 phase is accepted by a registered validator | `validation-report.json` present and passing per executed phase |
| `BI-5` | No metric regresses | all four verifiers still report their current verdict |

## Non-goals

- Waves 2 to 4 agents.
- Skill registration for S04 and S05, and normalization of the CI/CD and coding-style assets.
- Any change to gate ownership or to the Producer Exclusion Rule.
- Making all 36 phases dispatchable.

## Acceptance boundary

A Wave 1 agent is accepted only on the full five-part Agent Definition of Done in
`reports/self-hosting-execution-plan-2026-08-18.md` section 9.5. An agent that satisfies the
first three conditions and not the last two is reported as partially rolled out, with the
blocker named. Reporting it as done would make the board unusable as a record.

## Risk posture

Low tolerance for silent breakage of the existing executable path: `execution-planning` and
`solution-design-and-risk-assessment` must keep dispatching, and the two completed runs held as
replay references must stay reproducible. Higher tolerance for an increment that lands
partially and says so.
