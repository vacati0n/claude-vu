# Business Intent: Make the Self-Hosting Surface Discoverable

Supplied by the operator for framework change `FC-002`, routed as change class
`structure-preserving-change` by `config/self-hosting-profile.md`. This states intent and
acceptance expectation only. It defines no solution, names no module, and takes no design
decision.

## Why the change is wanted

The framework now has an operating mode that is meant to be the default for its own development:
every framework-internal change is routed by one command profile, recorded in a validated change
proposal, and held to a release checklist. None of the framework's index documents mentions any
of it.

An operating mode nobody can find is not a default. A contributor reading the framework's own
entry points is led to every other surface and not to this one, so the first thing they will do
with a framework change is exactly what the mode exists to stop: make it ad hoc.

## Outcome expected

1. A reader arriving at the framework's top-level entry point can reach the self-hosting profile,
   the change-proposal contract, and the framework release checklist by following indexes,
   without knowing the file names in advance.
2. Each index describes the new surface in the terms that index already uses, so a reader learns
   what kind of thing it is from where it appears.
3. The precedence between the profile and the routing policy that predates it is stated once,
   where a reader would look for it.

## Acceptance intent

- Nothing about how the framework runs changes. The same commands produce the same results, with
  the same counts, before and after.
- No index becomes a second authority. Where the profile already states a rule, an index points at
  it rather than restating it, so the two cannot drift apart later.
- Every committed run's evidence still verifies.

## Constraints the business places on the change

- This is a description of what exists, not a change to it. Any wording that would require a rule
  to change is out of scope and is to be surfaced rather than written.
- No registry record, workflow phase, gate, or agent contract is touched.
- The change must not claim the operating mode is complete where it is not. Where the mode depends
  on capability that is still missing, the index says so.

## Open to the design

- Which indexes must change and which merely could, and on what ground.
- Whether the profile belongs in the framework's layered responsibility list as a layer of its
  own, or inside an existing one.
- How much of the profile a reader needs at the index level before following the link.
