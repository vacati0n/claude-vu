# Change Request — OMT-01 Memory Token Optimizer Command

## Change class

`capability-addition`, per `config/self-hosting-profile.md` `## Routing Table`. The framework
gains a command contract, a registry record, and a runtime behaviour it did not have.

Classification was performed before the work began:

```
python .claude/runtime/self_hosting.py classify --path .claude/commands/optimize-memory.md \
    --path .claude/runtime/optimize_memory.py --path .claude/config/self-hosting-profile.md
python .claude/runtime/self_hosting.py route --intent capability-addition
```

Every touched path resolves in-scope under `SR-1`. The route resolves to `/implement` ->
`implement-feature`, entry phase `scope-and-acceptance`.

## Paths touched

| Path | Scope Rule | Change |
|---|---|---|
| `.claude/commands/optimize-memory.md` | `SR-1` | New command contract |
| `.claude/runtime/optimize_memory.py` | `SR-1` | New runtime module |
| `.claude/registry/commands.yaml` | `SR-1` | New active command record |
| `.claude/commands/command-catalog.md` | `SR-1` | New catalog row |
| `.claude/commands/README.md` | `SR-1` | Command contract count corrected |
| `.claude/config/self-hosting-profile.md` | `SR-1` | New proposal index section |

## Required behaviour

- The command routes to `refactor`, not to a new workflow. Its claim is the invariant claim that
  workflow already holds to account, and a second workflow asserting the same thing would be a
  second answer to a question the framework has already answered.
- The runtime module defaults to a dry run. Overwriting is an explicit flag.
- Every applied overwrite is preceded by a pre-image write and followed by a digest pair.
- Candidates are judged against the original by a mechanical rule, and a candidate that breaks
  it is discarded without a retry.
- Denied paths bind regardless of caller arguments.

## Constraints

- No change to any existing workflow, phase model, agent manifest, gate matrix row, or validator.
  A change that required one would be a larger change than this one claims to be.
- No new dependency for any existing surface. The provider client library is required only by the
  new module's online path, and only at the point it makes a request.
- `verify_registry_coverage.py`, `verify_self_hosting.py`, and the framework release checklist
  must pass after the change, at the same counts as before plus the one added command.

## Out of scope

- Executing an optimization pass against this repository's own memory and context. Adding the
  capability and using it are separate changes; the second is the operator's decision and carries
  its own review of its own diffs.
- Any change to what the knowledge surfaces say.
