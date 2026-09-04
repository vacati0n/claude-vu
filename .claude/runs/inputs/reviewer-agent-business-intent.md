# Business Intent: Reviewer Agent

Supplied by the operator for the `solution-design-and-risk-assessment` phase of the
Reviewer Agent change. This states intent and acceptance expectation only. It defines no
solution, names no module, and takes no design decision.

## Why the change is wanted

Review coverage in the framework is currently assigned case by case. Implementation plans
and code changes should instead be reviewed by one accountable role, so that the same
expectations apply to every governed change rather than varying with whoever picks the
review up.

## Outcome expected

1. One accountable framework role reviews implementation plans and code changes before
   they progress.
2. That role states an explicit outcome for each of the five named review dimensions:
   architecture compliance, coding quality, testing strategy, security, and framework
   governance.
3. Review results are consumable by the delivery and quality roles that act on them,
   without a reader having to reconstruct what was reviewed or what the verdict was.

## Acceptance intent

- A governed change carries a recorded verdict from the review role.
- An emitted review result records an outcome for every declared review dimension.
- The role is discoverable through the framework's own discovery surfaces, on the same
  terms as the roles already registered.

## Constraints the business places on the change

- The change adds a role to the framework. It does not change what any existing role is
  accountable for without that being surfaced as a decision.
- No numeric coverage target is set. Coverage is expressed as a proportion and measured,
  not committed to at a level.
- Nothing in this intent asks for the new role to be exercised on real work as part of
  this change.

## Open to the design

- Whether the new role coexists with existing review responsibility or supersedes it.
- What the review result artifact contains beyond the per-dimension outcome.
- When, in the delivery sequence, the role becomes routable by a workflow.
