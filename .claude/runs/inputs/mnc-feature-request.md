# Feature Request — Minimum Necessary Change policy (necessity and reuse ladder)

## Source

Operator request dated 2026-09-15: integrate the engineering philosophy of the upstream
Ponytail ruleset ("lazy senior developer": lazy about the solution, never lazy about
understanding the problem) into this framework's existing agents as a native, cross-cutting
behaviour. The framework's own philosophy is "code less, but make it work well". The upstream
ruleset is the source of the principle; nothing from it is copied wholesale.

## Request

Make planning, architecture, implementation, and code review behave like a senior engineer
who understands the problem deeply, chooses the simplest solution that satisfies the real
requirement, and refuses to build unnecessary things. The behaviour must be embedded in the
existing agent lifecycle rather than added as a new agent, a new workflow phase, a new
command, a new runtime mechanism, or a second orchestration layer.

The principle to embed, in order, stopping at the first rung that holds:

1. Does this need to exist? If not, do not build it.
2. Does the codebase already have it? Reuse it.
3. Does the standard library solve it? Use it.
4. Does the platform or framework in use solve it natively? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can it be written directly in a few lines at the call site? Write it there.
7. Only then: implement the minimum code necessary, introducing new abstraction only when
   the reason no lower rung held is recorded.

The ladder runs after the problem is understood, never instead of understanding it.

Two rules bound the ladder and are not negotiable:

- Minimum necessary change = required behaviour + required safety + required integration
  + required tests. Everything outside that boundary requires a recorded justification:
  scope creep, opportunistic refactoring, speculative abstraction, "while we are here"
  changes, unnecessary cleanup.
- Safety floor: no simplification may remove or weaken input validation at a trust
  boundary, error handling that prevents data loss, authorization or audit paths,
  accessibility, required observability, data integrity, or the tests that prove the
  change. A shorter implementation is not automatically better; line count is not a
  criterion. If twenty lines are required, twenty lines are written.

Review must be extended so a reviewer can detect over-engineering with seven questions —
existence, reuse, dependency, abstraction, complexity, scope, safety — and must not demand
arbitrary line-count reduction.

## Non-goals

- No new agent, skill file, workflow phase, gate, command, template section, validator
  vocabulary, configuration surface, prompt layer, or hook.
- No copy of the upstream repository, its intensity modes, its comment markers, or its
  commands.
- No change to current agent contracts' authority, to dispatching, to existing safety
  mechanisms, to testing obligations, or to logging and observability requirements.
- No change to runtime behaviour: `runtime/framework_runtime.py` is not touched and
  `RUNTIME_VERSION` stays 0.5.0.

## Acceptance criteria

1. One written standard states the ladder, the minimum-necessary-change definition, the
   safety floor, and the seven review questions, and it is already loaded by the design,
   implementation, refactor-implementation, quality-review, code-quality-review,
   structural-compliance, and repository-quality-scan phases without any runtime change.
2. The architect's reuse survey considers, for every required capability, the standard
   library, the native platform or framework capability, and already-installed dependencies
   in addition to existing components, and records a capability that no statement requires
   as out of scope rather than designing for it.
3. The implementer selects the route for every change-set entry by the ladder, records the
   rung that justified any new abstraction, file, or dependency in the implementation
   report's existing `Approach taken` field, and treats removal or weakening of a
   safety-floor item as a blocking self-check failure.
4. The reviewer applies the seven questions to every change review, each finding measured
   against the written standard, never against line count; a safety-floor breach is a
   correctness or security finding, the other six are maintainability or architecture
   findings at the severity the existing severity table yields.
5. Every framework verifier stays at its recorded baseline: registry coverage 6/6 with 37 of
   37 phases dispatchable, validators 6/6, vertical slice 10/10, multi-phase 15/15, recovery
   41/41, manifests 2/2; the `omn-agent` test suite stays at 329 passing.
6. The component counts do not move: 12 active agents, 12 skills, 8 workflows, 37 phases,
   11 commands. Added instruction volume is measured and reported in bytes per agent module
   set.
7. The planner and product owner contracts are not modified, because their existing
   traceability rules already reject invented scope and undeclared exclusions.
