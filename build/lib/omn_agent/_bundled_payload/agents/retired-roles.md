# Retired Roles Register

## Objective

Record every role identifier that appears in framework documents but is not part of the
active framework design, together with the reason it was retired, the role that supersedes
it, and how remaining references resolve.

A role is **active** when it owns at least one phase in an active workflow Phase Model. A
role that owns no phase, holds no registry record, and has no contract on disk is not an
unimplemented agent; it is an identifier the framework never adopted. This register is the
authoritative resolution for such identifiers, so that no reader and no runtime path is left
resolving a name that does not exist.

## Retirement Decisions

| Role | Retired on | Superseded by | Reason |
|---|---|---|---|
| `orchestrator` | 2026-08-19 | `omn-orchestrator` | duplicate identifier for the coordination role |
| `backend-developer` | 2026-08-19 | `omn-dev-1-implement` | technology specialization is carried by skills, not by agents |
| `omn-planning-generate-clarification-questions` | 2026-08-19 | `omn-business-analyst` | task-shaped identifier, not a role; duplicated an owned capability |

Each decision is recorded in `registry/agents.yaml` as a record at status `retired`, so a
runtime attempt to load one fails with an explicit policy failure naming the status rather
than an unresolved-identifier failure.

## `orchestrator`

- Status: retired
- Retired on: 2026-08-19
- Superseding agent: `omn-orchestrator` (`agents/omn-orchestrator.agent.md`)
- Reason: duplicate ownership of the coordination role

`orchestrator` and `omn-orchestrator` named one role. `omn-orchestrator` is the identifier
every active workflow, `workflows/workflow-gate-matrix.md`, and `agents/capability-matrix.md`
use; it owns three phases across the active Phase Models and holds a host entry point.
`orchestrator` owns no phase, holds no host entry point, and has no contract file. It was
never a second role, so it is retired rather than implemented.

Evidence:

- `omn-orchestrator` is the owner agent for `fix-bug/closure-and-communication`,
  `refactor/closure-and-debt-record`, and `release/deployment-execution`.
- `agents/capability-matrix.md` gives `omn-orchestrator` Primary for Orchestration and
  Routing. No second agent holds that column.
- No `agents/orchestrator.md` and no `agents/orchestrator/` module set has ever existed.

## `backend-developer`

- Status: retired
- Retired on: 2026-08-19
- Superseding agent: `omn-dev-1-implement` (`agents/omn-dev-1-implement.agent.md`)
- Reason: the framework expresses technology specialization through skills, not through
  stack-specific agents

`backend-developer` was carried as a "specialized execution profile". The framework has one
Primary owner of Implementation Delivery, `omn-dev-1-implement`, which is deliberately
stack-neutral. Stack-specific expertise reaches it through the skill registry — for example
`skills/dotnet/engineering-playbook.md`, `skills/react/react-engineering.md`, and
`skills/avalonia/desktop-ux-guidelines.md` — resolved per phase by the Skill Registry Loader.
Introducing a stack-named agent would create a second Primary owner for a capability the
matrix assigns to exactly one agent, which the capability model does not permit.

Evidence:

- `omn-dev-1-implement` is the sole Primary for Implementation Delivery in
  `agents/capability-matrix.md` and owns the implementation phase of `implement-feature`,
  `fix-bug`, and `refactor`.
- No active workflow Phase Model names `backend-developer` as an owner agent or participant.
- No `agents/backend-developer.md` and no `agents/backend-developer/` module set has ever
  existed.

## `omn-planning-generate-clarification-questions`

- Status: retired
- Retired on: 2026-08-19
- Superseding agents: `omn-business-analyst` for requirement clarification;
  `omn-product-owner` for acceptance arbitration
- Reason: the identifier names a task, not a role, and duplicated a capability already owned

The identifier describes an activity — generating clarification questions — rather than an
accountable role. That activity is a declared capability, `requirement-clarification`, held
by `omn-business-analyst`, which produces `requirement-framing.md` and is contracted to name
every gap and unresolved assumption rather than close it by inference. Where clarification
concerns acceptance boundaries rather than requirements, `omn-product-owner` arbitrates.

Retaining the identifier as an agent also broke the ownership model: its row in
`agents/capability-matrix.md` claimed Primary for Product Scope and Acceptance alongside
`omn-product-owner` and `omn-business-analyst`, giving one column three Primary owners.

Evidence:

- `registry/agents.yaml` records `requirement-clarification` among the capabilities of
  `omn-business-analyst`.
- No active workflow Phase Model names the identifier as an owner agent or participant.
- No contract file for the identifier has ever existed.

## Reference Resolution Rule

Where a retired identifier still appears in a document, it names the superseding role in the
table above. Two reference classes are deliberately preserved rather than rewritten.

**Executed agent contract modules.** `agents/planner/` and `agents/architect/` module files
are digest-pinned by committed run evidence: each invocation envelope records the digest of
every module loaded, and `runtime/verify_vertical_slice.py` check `C6` fails on drift.
Rewriting them would invalidate the provenance record of a run that actually executed.
Their machine-readable collaboration and escalation fields — held in `manifest.yaml`, which
carries no recorded digest — have been rewired to `omn-orchestrator`, so runtime resolution
reads the active identifier. The prose references inside the pinned modules are a deferred
migration that lands the next time those contracts are revised and re-run.

**Historical evidence and dated reports.** Everything under `runs/` and every dated document
under `reports/` records what was true when it was written. These are audit records, not
active references, and are never edited in place.

Unbackticked prose naming "orchestrator" as an English role name — as in "escalate to
orchestrator and tech lead" in command specifications — is role language, not an identifier
reference, and is consistent with "tech lead" appearing beside it. It is left as written.

## Related Records

- `agents/omn-architect.md` records a separate deprecation, of `omn-architect` in favour of
  `architect`, under the same supersession pattern.
- `agents/agent-catalog.md` routes intent to active agents and points here for retired ones.
- `agents/capability-matrix.md` carries a row for every active agent only.
