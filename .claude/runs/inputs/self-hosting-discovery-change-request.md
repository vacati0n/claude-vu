# Change Request: Make the Self-Hosting Surface Discoverable

Framework change `FC-002`, routed as change class `structure-preserving-change` by
`config/self-hosting-profile.md`.

## What is asked for

The self-hosting operating mode was delivered as four new surfaces:

- `config/self-hosting-profile.md`, the one command profile for framework-internal change routing
- `templates/framework-change-proposal.md` and its validator, the required change record
- `validation/framework-release-checklist.md`, the checklist a framework update must satisfy
- `runtime/self_hosting.py` and `runtime/verify_self_hosting.py`, the executable form of both

None of the framework's index documents mentions any of them. A contributor following
`README.md` and the module READMEs reaches every other surface of the framework and does not
reach this one, so the operating mode that is supposed to be the default is the one a reader is
least likely to find.

## The change

Record the new surfaces in the index documents that already index their kind:

- the folder descriptions and contributor usage in `README.md`
- `config/README.md`, where routing and governance policies are indexed
- `config/agent-routing.md`, which currently answers "which command for which intent" without
  reference to the profile that overrides it for framework-internal changes
- `commands/README.md`, whose command-contract rules are the ones the profile routes through
- `templates/template-catalog.md`, the controlled index of templates
- `validation/README.md`, the index of validation rules and checklists
- `runtime/README.md`, the current-state record of the runtime and its known gaps

## Behavioural invariants

Nothing about how the framework runs may change.

1. No registry record changes. No command, workflow, agent, skill, or template gains, loses, or
   alters a record.
2. No Phase Model, gate matrix row, or agent contract changes.
3. No runtime module changes behaviour. `RUNTIME_VERSION` does not move.
4. Every verifier that passes before the change passes after it, with identical counts.
5. Every committed run's evidence remains valid. Where an edited file is a member of a frozen
   context slice, the affected runs are re-verified rather than assumed intact.

## Baseline

The commands whose output must not change:

- `python .claude/runtime/verify_registry_coverage.py`
- `python .claude/runtime/verify_validators.py`
- `python .claude/runtime/verify_self_hosting.py`
- `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238`

## Out of scope

- Any change to the profile's routing table, scope rule, evidence rule, or completion rule.
- Any change to the release checklist items.
- Registering the profile as a record in a registry. Whether a profile is a registered component
  type is a contract question, not a documentation one.
