# Business Intent — CLAUDE.md Folder Descriptions Sync

## Outcome sought

A contributor reading `.claude/CLAUDE.md` — the document the framework itself instructs every
contributor to read first — sees a folder inventory that matches the repository.

## Value

CLAUDE.md is loaded into every agent session as authoritative project instructions. Its
`## Folder Descriptions` section is the map a contributor and every routed agent orients by.
Today that map omits four of the sixteen directories under `.claude/`, including `runtime/`,
which the same document's Contributor Usage section requires contributors to invoke, and
`registry/`, which the routing the document mandates resolves against. A map that silently
omits the framework's execution and discovery surfaces misleads exactly the audience the
document exists to orient.

## Success criteria

| ID | Criterion | Measure |
|---|---|---|
| `BI-1` | Every directory under `.claude/` has a row in `## Folder Descriptions` | 16 of 16 directories documented |
| `BI-2` | Each added description matches the folder's actual contents | Reviewer confirms against `domain-model/`, `prompts/README.md`, `registry/*.yaml`, `runtime/README.md` |
| `BI-3` | Nothing else about CLAUDE.md changes | Diff confined to `## Folder Descriptions` |
| `BI-4` | No metric regresses | All verification scripts keep their current verdict |

## Non-goals

- Rewriting any other CLAUDE.md section.
- Changing what any folder holds or how the runtime resolves it.
- Documenting repository-root files (`README.md`, `dependency-map.md`); the section is a folder
  inventory and stays one.

## Risk posture

Minimal-risk documentation change. Zero tolerance for any behavioural or contract drift; the
change is rejected if the diff leaves `## Folder Descriptions`.
