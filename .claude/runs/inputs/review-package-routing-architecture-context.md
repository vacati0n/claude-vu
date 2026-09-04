# Architecture Context: Routing the Review Package

Supplied by the operator for framework change `FC-001`. The system under design is the framework
in this repository, so the current-state architecture is the framework's own structure.

This document does not restate that structure. It names the authoritative records of it. Every
file named below is a member of the frozen context slice recorded in this run's
`context-snapshot.json`, so a fact drawn from one carries a citable digest.

## The surface this change touches

| Concern | Authoritative record |
|---|---|
| Which phase emits which artifact | the `## Phase Model` table of each `workflows/*.md` |
| Which artifact types the runtime can validate | the `VALIDATORS` map in `runtime/framework_runtime.py` |
| Whether a phase can be dispatched | the `G1-CAPABILITY` chain, reported per phase by `runtime/verify_registry_coverage.py` |
| Gate ownership | `workflows/workflow-gate-matrix.md` |
| Artifact contract | `templates/review-package.md`, enforced by `runtime/review_package_validator.py` |

`dependency-map.md` records the permitted dependency directions between component types.
`runtime/README.md` records what of the runtime is implemented and which gaps remain open.

## Known current-state properties the operator asserts

Each is verifiable in the files named above.

1. `workflows/review-pull-request.md` declares five phases. Every Output Artifact cell in that
   table is prose describing a deliverable; none names a file.
2. `review-package.md` is registered in `registry/templates.yaml`, carries a validator in the
   `VALIDATORS` map, and passes `verify_validators.py` against its fixture with a declared
   mutation caught by `P3`.
3. `verify_validators.py` check `V1` reads the Output Artifact column of every active Phase Model
   and treats any token ending in `.md` as a routed artifact type. It asserts coverage in one
   direction only: every routed artifact has a validator. A validated artifact that no phase
   routes is invisible to it.
4. `runtime/framework_runtime.resolve_output_contract` resolves a phase's declared artifact
   against the owning agent's manifest outputs and the `VALIDATORS` map. A phase whose artifact
   is prose resolves no file contract.
5. `review-pull-request/structural-compliance` currently blocks with failure class
   `workflow-contract-violation`, recorded in `reports/registry-coverage-report-2026-08-18.md`
   section 7, because the artifact that phase asks of `architect` is neither declared in the
   architect manifest's `outputs` nor covered by a validator.
6. `code-quality-review` is owned by `omn-dev-2-reviewer`, which is host-invocable through
   `agents/omn-dev-2-reviewer.agent.md` and holds no record in `registry/agents.yaml`.

## Constraints the operator places on the design

- A Phase Model is a machine-read contract. The runtime derives sequencing edges from its Input
  and Output Artifact columns, so a change to either changes what the runtime enforces.
- A phase's declared artifact must be one the Validation Engine can decide, or the phase becomes
  undispatchable for a new reason. Trading one blocked reason for another is not an improvement
  and must be surfaced if it would occur.
- Committed run evidence must remain valid. Any file inside a frozen context slice that this
  change edits requires the affected runs to be re-verified rather than assumed intact.
- The framework's discovery registries are single-authority. This change adds no second place
  where an artifact type is declared.
