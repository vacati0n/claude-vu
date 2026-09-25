## Metadata

- ADR ID: D-001
- Title: Carry the necessity-and-reuse standard by extending the existing Architecture Foundations skill (S01) in place
- Date: 2026-09-17
- Status: Proposed
- Owners: architect, omn-tech-lead
- Related Work Items: SCOPE-2026-0007; execution plan tasks T-001, T-002, T-014

## Context

- Problem statement: The requested necessity-and-reuse standard must reach seven named
  phases — `solution-design-and-risk-assessment`, `implementation`,
  `refactor-implementation`, `quality-review`, `code-quality-review`,
  `structural-compliance`, `repository-quality-scan` — without a runtime change and without
  any new repository file.
- Business and technical constraints: `C-001` forbids a new agent, skill file, workflow
  phase, gate, command, template section, validator vocabulary, configuration surface,
  prompt layer, or hook. `C-002` forbids any change to `runtime/framework_runtime.py`.
  `C-006` requires the carrier to already reach all seven named phases through existing
  bindings.
- Current architecture baseline: `F-001` establishes that S01
  (`skills/architecture/clean-architecture-checklist.md`) is declared by ten agent
  manifests, including `architect`, `omn-dev-1-implement`, and `omn-dev-2-reviewer`; `F-002`
  and `F-003` establish that S01 reaches all seven named phases today, six through
  context-slice membership and one (the architect's own design phase) through the agent's
  manifest skill binding; `F-005` establishes S01's identity is recorded in
  `registry/skills.yaml` and `skills/agent-skill-matrix.md` at version `1.0.0`.

## Decision

- Selected option: O-001.
- Decision statement: Extend S01 in place with the ladder, the minimum-necessary-change
  definition, the safety floor, and the seven review questions, plus one new anti-pattern and
  one new common-mistake entry, and raise its recorded version from `1.0.0` to `1.1.0`.
- Scope of impact: `M-001` directly; downstream reference effect on `M-002`, `M-003` (the
  skill's registry identity), `M-004`, `M-005` (the architect's own procedure, which cites
  the standard by the skill's display name), and `M-006` through `M-009` (the implementer's
  and reviewer's forthcoming procedure edits, which reference the same standard by the same
  name).

## Alternatives Considered

1. O-002: Add the standard's content to `domain-model/agent-specification.md`
- Benefits: already a shared, agent-spanning document referenced by every agent's
  `identity.md`.
- Risks: not loaded by five of the seven named phases without a new binding.
- Why not selected: violates `C-006` directly — `domain-model/agent-specification.md` is not
  a context-slice member of `implementation`, `refactor-implementation`, `quality-review`,
  `code-quality-review`, or `repository-quality-scan`.

2. O-003: Duplicate the standard's content into each affected agent's own `reasoning.md`
- Benefits: no shared file is widened; each agent's procedure text stays self-contained.
- Risks: the same content maintained in three or more places diverges over time.
- Why not selected: violates `C-006` — `structural-compliance` is not owned by
  `omn-dev-2-reviewer` at all, so no single agent's `reasoning.md` reaches every phase — and
  reproduces, inside the standard's own delivery mechanism, the duplication the standard
  itself forbids.

3. O-004: Introduce a new, dedicated skill file for the ladder
- Benefits: single-responsibility; the general architecture-checklist skill is not widened
  with unrelated governance content.
- Risks: a new skill file requires a new registry record, a new skill-matrix row, and new
  manifest bindings across every affected agent and phase.
- Why not selected: violates `C-001` directly.

## Consequences

- Positive outcomes expected: the standard reaches all seven named phases immediately, with
  zero new files and zero runtime change; the change is reversible by a plain text revert.
- Tradeoffs accepted: S01 now carries two conceptually distinct bodies of guidance — general
  clean-architecture principles and the necessity-and-reuse governance ladder — inside one
  skill file, widening what "Architecture Foundations" covers.
- Risks introduced: `R-001` (version-classification uncertainty under `A-003`); `R-004` (a
  future phase not covered by existing bindings).

## Validation Plan

- Metrics to monitor: the registry coverage verifier continuing to resolve S01 by its display
  name after the version bump; the seven named phases' resolved skill bindings and
  context-slice membership continuing to include S01 unchanged in mechanism.
- Verification checkpoints: `P-002` (version identity updated only after content is final);
  `T-009`'s post-change baseline verification.
- Rollback or reversal conditions: if a phase is found not to receive S01 as expected, revert
  the version bump and the content addition and escalate through `Q-001`; no data or contract
  is affected by a rollback, because nothing this decision touches is a runtime contract.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
