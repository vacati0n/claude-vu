# Investigation Request — Fan-Out Inside the Implementation Phase

## Question

Should the framework let one implementation phase be carried out by several implementer
invocations working on disjoint tasks at the same time, and if so what is the least risky
design? This is option B of a two-step effort to reduce delivery time and token cost. Step 1
(per-phase model tier, proposal FC-016, runtime 0.9.0) is delivered. Parallel test execution
(`tools/run_tests_parallel.py`) is delivered. The investigation must decide whether a third
change, parallelism within the implementation phase, is justified at all.

## Decision owner

The operator, who will accept or reject a recommendation. The outcome may be "do not build this".

## Why the question exists

The execution plan already declares tasks in waves with dependency edges, so independent tasks
are known. The implementation phase today is one invocation of one agent. In the most recent
implement-feature run (run-ded114f50a46) that phase took 1h55m of the run's 3h00m agent-active
time, the largest single share.

## Facts supplied (verify each; do not trust them blindly)

1. The most recent plan had 14 tasks in 9 waves of widths 2,1,2,1,3,1,1,2,1. The best case is a
   critical path of 9 against 14 serial steps, about 1.5 times faster, before any coordination cost.
2. Most of those tasks edited the same runtime source file, so task-level write sets may overlap far
   more than the dependency edges suggest.
3. The implementer agent's declared tools are Read, Glob, Grep, Edit, Write and Bash. It has no
   tool to start another agent. A host session dispatches agents; a dispatched agent generally
   cannot dispatch further agents.
4. The runtime models one phase as one work item with one lease, one invocation, one idempotency key
   and one result envelope. Phase artifacts are validated by one registered validator, and the
   write scope in the envelope is a single set of permitted patterns.
5. Concurrent edits in one working tree are unsafe. Isolation would need separate working copies and
   a merge step.
6. A large share of the phase's wall clock was running the repository's own test suite, which is
   now addressed separately.

## What the investigation must establish

- Current state: what the runtime, state engine and implementation-report validator assume about
  one invocation per phase, with evidence from the source.
- The feasible option set, including at least: (a) do nothing, (b) a host-level fan-out that
  dispatches several implementer invocations under one phase and merges their reports, (c)
  splitting implementation into several declared phases in the workflow Phase Model, (d) reducing
  implementation time by other means such as task batching or smaller context, measured.
- For each option: what must change (runtime, envelope, validator, contracts), write-scope
  partitioning and conflict handling, how attribution and traceability survive, what an honest
  speedup estimate is using the measured wave widths and the overlap in fact 2, and the risk to
  the framework's independence and gate rules.
- A recommendation, including the case for not building it, with the evidence that would change it.

## Constraints

- Gates, validators, artifact contracts and the one-owner-per-phase accountability rule must not be
  weakened to make parallelism fit.
- The runtime must not call a model.
- Findings must be grounded in files read and commands run, with confidence marked.

## Operator decisions that resolve the framing questions

These are decisions by the operator, supplied as part of the request so the framing does not
have to carry them as open questions.

- Baseline and measure: the baseline is the implementation-phase elapsed wall-clock time of
  run-ded114f50a46, which was 1h55m, for the same task set. Success means a measurably lower
  elapsed time with the time spent running the repository test suite excluded from both sides.
- Token cost: token-cost neutrality is not required. An option that raises the phase's token cost
  by more than 25 percent over that baseline is rejected unless its elapsed-time gain exceeds
  40 percent.
- Priority scale: use the framework's existing severity vocabulary; no new scale is introduced.
