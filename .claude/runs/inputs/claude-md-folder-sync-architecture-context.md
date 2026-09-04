# Architecture Context — CLAUDE.md Folder Descriptions Sync

Supplied by the operator for the `scope-invariants-and-risk-profile` phase of the CLAUDE.md
folder-descriptions correction. The system under design is the framework in this repository;
the surface under change is its top-level orientation document.

## Position of the changed surface

`.claude/CLAUDE.md` is a documentation surface, not a resolved runtime surface: no registry
record points at it, no validator parses it, and no workflow phase consumes it as an input
artifact. It is, however, injected into every contributor session as project instructions, so
its accuracy is a governance concern even though its content is load-bearing for humans and
session-context only.

## Authoritative records the added descriptions must match

| Folder to document | Authority on its contents |
|---|---|
| `domain-model/` | The five `*-specification.md` files it contains (agent, command, skill, workflow, memory) |
| `prompts/` | `prompts/README.md` |
| `registry/` | The five `registry/*.yaml` discovery indexes; `dependency-map.md` records their position |
| `runtime/` | `runtime/README.md`, the current-state record of what is implemented |

## Current-state properties the operator asserts

1. `.claude/` contains sixteen directories; CLAUDE.md documents twelve.
2. Every path CLAUDE.md currently cites resolves on the filesystem (verified 2026-08-27):
   `config/self-hosting-profile.md`, `validation/framework-release-checklist.md`,
   `runtime/verify_self_hosting.py`, `runtime/self_hosting.py`,
   `templates/framework-change-proposal.md`.
3. The framework's discovery registries are single-authority; CLAUDE.md describes them, it does
   not duplicate their records.

## Constraints the operator places on the design

- The change must not create a second authority: descriptions summarize, they do not restate
  registry or specification content.
- The diff is confined to `## Folder Descriptions`. A correction that finds defects elsewhere in
  CLAUDE.md names them for a separate routed change rather than folding them in.
