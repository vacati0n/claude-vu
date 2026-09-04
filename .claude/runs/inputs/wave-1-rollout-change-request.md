# Change Request — Wave 1 Delivery Core Agent Rollout

## Change class

`capability-addition` per `config/self-hosting-profile.md` Routing Table. The framework gains
agent runtime contracts, registry records, and phase execution it did not have.

Classification evidence:

```
python .claude/runtime/self_hosting.py classify --path .claude/agents/omn-product-owner/manifest.yaml
  [IN ] .claude/agents/omn-product-owner/manifest.yaml   SR-1
  framework-internal change

python .claude/runtime/self_hosting.py route --intent capability-addition
  command : /implement   workflow : implement-feature v1.0.0   entry phase : scope-and-acceptance
```

## Surfaces this change is expected to touch

| Surface | Nature of change |
|---|---|
| `agents/<wave-1-id>/` | New runtime module sets: `manifest.yaml` plus the modules its `loadOrder` declares |
| `registry/agents.yaml` | New active records, one per Wave 1 agent |
| `agents/<wave-1-id>.agent.md` | Registration status table updated to match reality |
| `workflows/*.md` Phase Model | Possible Output Artifact column changes, if the artifact-type decision requires them |
| `templates/` | Possible new artifact templates |
| `runtime/framework_runtime.py` | Possible `VALIDATORS` and `CONTEXT_SLICE_PHASE` additions |
| `runtime/*_validator.py` | Possible new validators |
| `reports/` | Board and evidence updates (out of routing scope, `SR-4`) |

The four rows marked *possible* are conditional on the design decision. They are listed so the
blast radius is declared up front rather than discovered during implementation.

## Current state the change starts from

Frozen in `reports/maturity-snapshot-2026-08-18.json`:

- active agent registry records: 2 of 12 phase owners
- host-invocable entrypoints: 12 of 12
- runtime module sets: 2
- dispatchable phases: 3 of 36; blocked: 33, all with reason `awaiting_capability_registration`
- registered validators: 7; artifact types named as files by active Phase Models: 6
- phase-mandatory skill references resolved: 101 of 101
- runs: 6 total, 2 Completed, 4 WaitingForHuman
- active workflows with zero completed runs: 6 of 7

## Behavioral invariants

| ID | Invariant |
|---|---|
| `INV-1` | `implement-feature/execution-planning` and `implement-feature/solution-design-and-risk-assessment` remain dispatchable |
| `INV-2` | `refactor/scope-invariants-and-risk-profile` remains dispatchable |
| `INV-3` | The two Completed runs held as replay references remain readable and their fingerprints unchanged |
| `INV-4` | All four verifiers keep their current verdict; no check moves from pass to fail |
| `INV-5` | No phase-mandatory skill reference becomes unresolved |
| `INV-6` | Gate ownership and the Producer Exclusion Rule are unchanged |

## Constraints

- One primary capability surface per increment.
- No registry activation without the runtime module set it points at.
- No completion claim without a run under `runs/` that carries the evidence.
- Where a phase cannot be made dispatchable inside this increment, it blocks with a recorded
  reason and the increment reports it, rather than the scope being quietly narrowed.

## Requested decision

Which increment sequence makes the four Wave 1 agents dispatchable at the lowest risk to
`INV-1` through `INV-6`, and what artifact type each prose-output phase should emit so that
`D-4` and `D-5` of the Agent Definition of Done become reachable.
