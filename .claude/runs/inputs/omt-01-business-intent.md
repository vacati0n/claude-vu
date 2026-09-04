# Business Intent — OMT-01 Memory Token Optimizer Command

## Goal

Stop the per-run cost of the framework's own knowledge from growing without a control on it.

## Value

Every dispatch loads memory, context, and instruction files into its context slice. That cost is
paid on each run and by every agent the run dispatches. Roughly sixty-five kilobytes across
twenty-one files are in that position today, and the number only rises: recording a decision, a
known issue, or a standard is the framework working correctly, and each recording makes every
later run start more expensive.

Two things follow. Density in these files has a measurable return, unlike density in a document
read once. And the absence of any control means the trend has no counterweight — no phase, no
gate, and no command currently asks whether a knowledge surface is carrying tokens that do not
carry rules.

## Success measures

| Measure | Target |
|---|---|
| Recurring token cost of the knowledge surfaces | Measurably reduced, by measurement rather than estimate |
| Rules, constraints, and identifiers lost | Zero, checked mechanically per file |
| Files overwritten without a recoverable pre-image | Zero |
| Operator review possible before any overwrite | Always: the default performs no overwrite |
| Existing framework verification results | Unchanged, at the same counts plus the added command |

## Acceptance boundary

The framework may claim only what it can check. A structural and identifier-level invariant check
is checkable and is what the capability asserts. Semantic equivalence of reworded prose is not
checkable by the framework, so it is not asserted: the recorded diff is offered to a reviewer
instead, and the difference between the two claims is stated in the command contract rather than
elided.

A capability that quietly overstated its guarantee would be worse than no capability, because the
surfaces it rewrites are the ones every later run trusts without re-reading.

## Constraints

- No degradation of any existing framework guarantee.
- No new obligation on an operator who never runs the command.
- The offline surfaces stay usable with no credentials and no client library present.

## Not intended

- Reducing what the framework knows.
- Making knowledge terser at the cost of making it ambiguous.
- Running the pass automatically, on a schedule, or as part of another lifecycle.
