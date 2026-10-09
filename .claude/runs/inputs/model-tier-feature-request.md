# Feature Request — Per-Phase Model Tier in the Dispatch Envelope

## Request

Let the framework declare, per workflow phase, which class of model should execute it, and carry
that declaration in the dispatch envelope the runtime hands to the host. Today all twelve agent
entrypoints declare `model: inherit`, the envelope has no model field, and every phase therefore
runs on whatever model the operator's session happens to use, however light the phase is.

## Why now

A single implement-feature run costs about 510K estimated context tokens across nine agent
invocations. Runtime 0.7 cut what each agent reads. It did nothing about which model reads it.
Several phases are read-and-summarise work (scope definition, technical discovery, documentation
hand-off, artifact packaging, repository scan) that a smaller model can perform; others
(solution design, root-cause analysis, implementation, quality review) need the strongest model.
The framework's gates and validators decide correctness mechanically, so a cheaper tier is safe
only if a failing phase is promoted rather than retried at the same tier.

## Expected outcome

- A single authoritative declaration of each phase's tier (`light`, `standard`, `deep`) and of the
  mapping from tier to a host model hint, readable by the runtime and verifiable.
- `dispatch` emits a `model_tier` object in the envelope (additive field): the resolved tier, the
  host model hint, and the basis for the choice.
- Escalation: a phase whose artifact was rejected by its validator on a prior attempt, or whose
  gate was rejected and rolled back, is dispatched one tier higher on the next attempt, and the
  envelope records that it was escalated and why. `deep` never escalates further.
- A phase with no declaration resolves to `standard`'s behaviour of inheriting the host model, so
  no existing run, replay, or verifier changes outcome.
- `execution-metrics.json` reports invocations and estimated context bytes by tier.

## Constraints on the request

- Additive only: the original envelope fields, the Phase Model tables, gates, validators, artifact
  contracts, and agent module text are unchanged. Workflow tables are machine-parsed, so a column
  is not added to them.
- The runtime never calls a model; it names a tier and the host chooses. The change must not
  introduce a model call or a vendor SDK dependency.
- Tier assignment is configuration, not agent text, so it must not be duplicated into agent modules.
- Parallel execution of phases is out of scope and is a separate later change.
