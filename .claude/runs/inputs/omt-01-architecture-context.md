# Architecture Context — OMT-01 Memory Token Optimizer Command

Supplied by the operator for the `solution-design-and-risk-assessment` phase of the memory token
optimizer change. The system under design is the framework in this repository, so the
current-state architecture is the framework's own structure.

This document names the authoritative records rather than restating them. Every file named is a
member of the frozen context slice recorded in this run's `context-snapshot.json`, so a fact drawn
from one carries a citable digest.

## Component model

| Component type | Discovery registry | Specification |
|---|---|---|
| Agents | `registry/agents.yaml` | `domain-model/agent-specification.md` |
| Skills | `registry/skills.yaml` | `skills/agent-skill-matrix.md` |
| Workflows | `registry/workflows.yaml` | `workflows/refactor.md` and siblings |
| Templates | `registry/templates.yaml` | `templates/` |
| Commands | `registry/commands.yaml` | `commands/` |

`dependency-map.md` records permitted dependency directions. `commands/README.md` records the
distinction between a command contract and a grouped runbook, and the rule that every contract
carries exactly one primary workflow.

## Current-state properties the operator asserts

Each is verifiable in the files named above, and each was checked before this change began.

1. Ten command contracts hold active records in `registry/commands.yaml`, and
   `verify_registry_coverage.py` check `C1` fails if any contract on disk lacks a record.
2. Two contracts already share a primary workflow with another contract: `/document` and `/test`
   route to `implement-feature` and `review-pull-request` respectively, alongside `/implement` and
   `/review`. Sharing a workflow is therefore an established pattern, not a new one.
3. `workflows/refactor.md` declares five phases: `scope-invariants-and-risk-profile`,
   `safety-net-establishment`, `refactor-implementation`, `behavioral-validation`, and
   `closure-and-debt-record`. All five are dispatchable, per `C6`.
4. All thirty-seven declared phases across eight active workflows are dispatchable today.
5. The runtime and its verifiers depend on the standard library and one YAML package. No framework
   surface currently makes a network request or requires a provider credential.
6. `runtime/artifact_lib.py` forbids naming a model, vendor, or provider inside a validated
   artifact, and strips the framework's own path prefix before that scan.
7. `config/self-hosting-profile.md` is parsed by `runtime/self_hosting.py`, which reads named
   sections by heading. A section added after the last parsed heading does not alter what parses.

## Constraints the design must respect

- A command contract resolves to exactly one primary workflow, and that workflow must hold an
  active registry record.
- A new workflow would require a phase model, gate matrix rows with non-producing owners, agent
  manifest entries, runtime context slices, and a registered validator per output artifact. The
  design should establish whether it needs one before incurring that.
- Run evidence under `runs/`, dated reports under `reports/`, and change proposals under
  `proposals/` are excluded from the self-hosting scope rule because rewriting them would falsify
  the record a routed change resolves against. Any capability that writes files must respect the
  same boundary for the same reason.
- The verifiers `verify_registry_coverage.py`, `verify_validators.py`, `verify_recovery.py`, and
  `verify_self_hosting.py` decide current-state truth. The change is accountable to all four.

## Risk targets

| Concern | Target |
|---|---|
| Existing framework guarantees | No regression; identical verifier results plus the added command |
| Irreversible file modification | None reachable without an explicit flag and a written pre-image |
| Dependency creep | The new dependency is confined to the new module's online path |
| Overstated guarantee | The contract states what is checked mechanically and what is not |
