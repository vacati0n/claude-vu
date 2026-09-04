# Architecture Context: The Framework's Discovery Surfaces

Supplied by the operator for framework change `FC-002`. The system under change is the framework
in this repository, so the current-state architecture is the framework's own structure.

This document does not restate that structure. It names the authoritative records of it. Every
file named below is a member of the frozen context slice recorded in this run's
`context-snapshot.json`, so a fact drawn from one carries a citable digest.

## What a discovery surface is here

The framework has two kinds of index, and they are not interchangeable.

| Kind | Read by | Examples |
|---|---|---|
| Machine index | the runtime resolvers | `registry/*.yaml`, the `## Phase Model` tables, `workflows/workflow-gate-matrix.md` |
| Human index | a contributor or an operator | `README.md`, the module `README.md` files, `commands/command-catalog.md`, `templates/template-catalog.md`, `skills/agent-skill-matrix.md` |

This change touches human indexes only. A machine index is a contract surface: adding a record
to one changes what resolves, which is a different class of change than describing what exists.

## Known current-state properties the operator asserts

Each is verifiable in the files named.

1. `config/` holds `.md` policy documents and no registry. `config/README.md` indexes them, and
   the runtime reads none of them directly; they bind the roles that read them.
2. `config/agent-routing.md` maps intent to primary agent and states its own precedence rule:
   where it and a Phase Model disagree, the Phase Model governs. It carries no statement about
   framework-internal changes.
3. `templates/template-catalog.md` indexes templates by usage point and owner, and states the
   governance rule of one canonical template per artifact type.
4. `validation/README.md` indexes validation rules and checklist definitions.
   `validation/framework-validation-checklist.md` asks whether the framework is well-formed and
   is a different question from whether a given update may ship.
5. `runtime/README.md` records the implemented surface, the file roles, and a numbered list of
   known gaps. It is the current-state record cited by every increment report.
6. `README.md` describes eight layered responsibilities and ten folders. Neither list mentions
   proposals or the self-hosting profile.
7. `runtime/framework_runtime.py` reads `config/self-hosting-profile.md` only through
   `runtime/self_hosting.py`, which is imported by `runtime/change_proposal_validator.py` and
   `runtime/verify_self_hosting.py`. No resolution path in the gateway depends on it, so editing
   documentation about it cannot change what the gateway resolves.

## Constraints the operator places on the change

- A human index may describe a surface; it may not become a second authority for it. Where the
  profile already states a rule, an index references it rather than restating it, so the two
  cannot drift.
- `config/execution-engine.md` narrows each phase's context slice. A document added to a slice
  changes the digests of runs that hydrate it, so the slice is not to be widened by this change.
- The framework's precedence rules are contract statements. Recording that the profile governs
  entry-command selection for framework-internal changes is a statement about existing behaviour;
  changing what governs would be out of scope.
