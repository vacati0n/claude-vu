# Feature Request — OMT-01 Memory Token Optimizer Command

## Request

Give the framework a command that rewrites its durable knowledge surfaces — memory, context, and
the standing instruction files — to their minimum token cost without changing what they instruct.

The capability comprises three things the framework does not have today:

1. `commands/optimize-memory.md`, a command contract with an active record in
   `registry/commands.yaml`.
2. `runtime/optimize_memory.py`, the runtime module the command executes.
3. An index in `config/self-hosting-profile.md` recording each accepted change proposal against
   the run that carried it.

## Why now

Memory, context, and instruction files are loaded into the context slice of every dispatch. Their
token cost is therefore paid per run rather than once, and it grows monotonically: every
increment that records a decision, a known issue, or a standard makes every later run more
expensive to start. Twenty-one files totalling roughly sixty-five kilobytes are in that position
now. Nothing in the framework reduces that cost, and no existing command's contract covers doing
so.

The framework already owns the shape of this work. A change that alters wording while preserving
meaning is a `structure-preserving-change`, and `workflows/refactor.md` exists to hold that claim
to account: `scope-invariants-and-risk-profile` states what may not change, and
`behavioral-validation` checks that it did not. What is missing is a bounded entry point that
routes there with the scope and the mechanical check already fixed.

## Expected outcome

- An operator types one command and receives a reviewable proposal: per-file token delta, a
  unified diff per candidate, and a named reason for every candidate that was rejected.
- No file is overwritten without a recoverable pre-image and a recorded digest pair.
- Every accepted candidate has passed a mechanical invariant check against its original.
- Generated and evidence surfaces are unreachable by the pass, whatever the operator asks for.
- The framework's registry coverage, self-hosting, and release checks continue to pass.

## Explicit non-goals

- Deciding what belongs in memory or context. That stays with `memory/memory-governance.md`.
- Rewriting source code, agent contracts, registries, workflow specifications, or command
  specifications. None is a knowledge surface loaded per run.
- Proving semantic equivalence. The request asks for a mechanical structural check plus a
  reviewable diff, and asks that the difference between those two be stated rather than blurred.

## Known obstacles the request does not resolve

- A generative model cannot prove it preserved meaning. Any acceptance rule built on its own
  assurance is worthless. The design must therefore judge candidates against the original by a
  rule the framework can run, and must say plainly what that rule does and does not cover.
- The compression pass requires a provider client library and resolvable credentials, neither of
  which the framework carries today. The command must fail before touching a file when they are
  absent, and the offline surfaces must stay usable without them.
