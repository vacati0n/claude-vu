# Business Intent — Minimum Necessary Change policy

## Outcome the business is buying

Less code, less architecture, less cognitive load, same or better correctness — delivered by
the agents this framework already runs, at no added execution cost. The best code is often
the code the team never had to write.

## Why now

Agents default to over-building: speculative abstractions, helper classes with one caller,
custom implementations of standard-library behaviour, new dependencies where an installed one
serves, and opportunistic refactoring of unrelated code. Each costs review time, tokens,
maintenance, and defect surface. The upstream ruleset this request adapts reports roughly half
the lines of code, a fifth fewer tokens, and a quarter less wall time on comparable tasks with
safety behaviour preserved. Those figures are the upstream's; this change measures its own.

## Constraints on the outcome

- Correctness and required safety stay at one hundred percent. The policy reduces
  unnecessary code, unnecessary decisions, unnecessary dependencies, and unnecessary
  abstractions; it never reduces validation, error handling, security, accessibility,
  observability, testability, or data integrity.
- Execution performance is preserved: no added agent invocation, no added reasoning loop,
  no added workflow step. The framework is already optimized for orchestration cost, and
  this change must not spend that budget.
- The implementation of the policy must itself satisfy the policy: the smallest integration
  that produces the behaviour, with no framework bloat.

## How success is measured

Before and after, on the same representative implementation tasks: lines and files changed,
agent calls, tokens and wall time where the host reports them, test results, and reviewer
findings — read together, never line count alone. Framework-side: component counts unchanged,
added instruction bytes reported, every verifier at baseline.
