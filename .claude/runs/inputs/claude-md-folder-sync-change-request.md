# Change Request — CLAUDE.md Folder Descriptions Sync

## Change class

`structure-preserving-change` per `config/self-hosting-profile.md` Routing Table. Wording of a
documentation surface changes; no contract, routing, or runtime behaviour changes.

Classification evidence:

```
python .claude/runtime/self_hosting.py classify --path .claude/CLAUDE.md
  [IN ] .claude/CLAUDE.md   SR-1: Every framework surface the runtime resolves lives here
  framework-internal change

python .claude/runtime/self_hosting.py route --intent structure-preserving-change
  command : /refactor   workflow : refactor v1.0.0   entry phase : scope-invariants-and-risk-profile
```

## Defect being corrected

`.claude/CLAUDE.md` section `## Folder Descriptions` enumerates twelve directories. The
`.claude/` tree contains sixteen. Four existing, load-bearing directories are undocumented:

| Missing folder | What it actually holds |
|---|---|
| `domain-model/` | Canonical specifications of the framework's domain concepts: agent, command, skill, workflow, and memory specifications |
| `prompts/` | Curated, versioned prompt patterns used by the task-force agents |
| `registry/` | Single-authority discovery indexes (`agents.yaml`, `commands.yaml`, `skills.yaml`, `templates.yaml`, `workflows.yaml`) the runtime resolves routing against |
| `runtime/` | The executable runtime: state engine, routing resolver, artifact validators, self-hosting classifier, and verification scripts |

The omission is a correctness defect in the orientation document every contributor is told to
read first, and `runtime/` in particular is named repeatedly in CLAUDE.md's own Architecture and
Contributor Usage sections while absent from its folder inventory.

## Surfaces this change is expected to touch

| Surface | Nature of change |
|---|---|
| `.claude/CLAUDE.md` | Four rows added to `## Folder Descriptions`; no other section changes |
| `proposals/` | New change proposal (governance record, `SR-5` out of routing scope) |
| `runs/` | Run evidence written by this run (`SR-3` out of routing scope) |

## Behavioral invariants

| ID | Invariant |
|---|---|
| `INV-1` | No contract, registry record, routing row, gate, or runtime behaviour changes |
| `INV-2` | Every existing row of `## Folder Descriptions` keeps its meaning; only additions occur |
| `INV-3` | All verification scripts (`verify_manifests.py`, `verify_registry_coverage.py`, `verify_validators.py`, `verify_recovery.py`, `verify_self_hosting.py`) keep their current verdict |
| `INV-4` | Every path CLAUDE.md cites resolves on the filesystem after the change, as all currently cited paths already do |

## Constraints

- Descriptions must state what each folder holds today, verified against its contents, not
  aspirational purpose.
- One line per folder, matching the existing list's register and length.
- No reordering of existing rows beyond what alphabet-free structural grouping already present
  requires; new rows are inserted where a reader scanning the tree would look for them.

## Requested decision

Confirm the four added descriptions are accurate against folder contents and that the change is
purely additive to `## Folder Descriptions`.
