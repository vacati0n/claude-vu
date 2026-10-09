# Business Intent — Per-Phase Model Tier

## Problem

Delivery runs spend the strongest, most expensive model on every phase, including phases whose work
is reading, summarising, and filling a template. Cost per run is high and gives the operator no lever
short of changing the whole session's model, which would degrade the phases that need depth.

## Intent

Make cost proportional to difficulty without weakening governance: route light phases to a cheaper
model, keep deep phases on the strongest, and promote automatically when a cheaper attempt fails its
validator or gate.

## Success

- A measurable share of a representative implement-feature run's agent invocations are dispatched at
  a non-deep tier, reported by the runtime's own metrics.
- No gate, validator, or acceptance rule is weakened; every verifier remains at its recorded baseline.
- A rejected cheaper attempt is never retried at the same tier.

## Non-goals

- Choosing vendors or model identifiers inside the runtime.
- Changing which phases exist, who owns them, or what they must produce.
- Running phases concurrently.
