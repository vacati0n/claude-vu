# Feature Request — Wave 1 Delivery Core Agent Rollout

## Request

Make the four Wave 1 delivery core agents of the AI Engineering Framework runtime-dispatchable,
starting with `omn-product-owner`, so that the phases they own stop blocking at
`G1-CAPABILITY` and can execute inside a framework run.

The four agents, in rollout order:

1. `omn-product-owner`
2. `omn-dev-1-implement`
3. `omn-dev-2-reviewer`
4. `omn-qa`

## Why now

Two of twelve phase owners hold an agent registry record today (`planner`, `architect`), so
3 of 36 declared phases across the seven active workflows are dispatchable. Every other phase
is enqueued and blocked with a recorded reason. The delivery path after planning and design —
scope, implementation, review, quality — has no executable owner at all, which is why no active
workflow other than `implement-feature` has a completed run, and why `implement-feature` itself
reaches `WaitingForHuman` rather than `Completed`.

Wave 1 closes that path. It is the prerequisite for Waves 2 to 4, and for the claim that the
framework builds itself rather than being built beside itself.

## Expected outcome

For each of the four agents:

- a runtime module set at `agents/<id>/` whose `manifest.yaml` declares a load order that
  resolves on disk;
- an active record in `registry/agents.yaml`;
- the existing `agents/<id>.agent.md` host entrypoint continuing to resolve;
- at least one completed run in which the agent owns a phase;
- the artifact that phase emits accepted by a registered validator.

## Known obstacles the request does not resolve

These are stated as facts about the current framework, not as instructions about what to do
about them. Deciding what to do about them is the point of routing this through the framework.

1. Eleven of the twelve phases these four agents own declare a **prose** Output Artifact in
   their workflow Phase Model — for example `scoped requirement summary` rather than a named
   file. `framework_runtime.py` reads that column literally and requires the resulting string
   to appear both in the owning manifest's `outputs[].artifact` and in the `VALIDATORS` map, so
   a prose cell cannot resolve to an output contract however the agent is registered.
   `review-pull-request/code-quality-review` is the single exception: it already names
   `review-package.md`, for which a validator and a template exist.

2. No phase these four agents own has an entry in `CONTEXT_SLICE_PHASE`, which declares three
   phases today. A phase without one blocks at `G2-CONTEXT` even after `G1-CAPABILITY` clears.

## Constraints on the request

- One primary capability increment at a time.
- No capability is complete without completed run evidence under `runs/`.
- Registering an agent whose phase still cannot dispatch is not a completed increment; it is
  a partial increment that must say so.
