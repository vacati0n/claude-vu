# Architecture Decision Record D-001

## Metadata

- ADR ID: D-001
- Title: Declare the per-phase tier in one shipped data file under config/, with opaque host hints
- Date: 2026-10-08
- Status: Proposed
- Owners: omn-tech-lead (Design Gate owner who accepts), architect (author)
- Related Work Items: run-ded114f50a46 design package, impacted modules M-002, M-001, M-004; planner tasks T-001, T-002, T-003, T-006

## Context

- Problem statement: every phase runs on whatever model the session uses (F-001). The framework needs one authoritative declaration of each phase's tier and of the tier-to-hint mapping, readable by the runtime and verifiable, without a model call and without touching agent text, Phase Model tables, or registry schemas.
- Business and technical constraints: C-001 (one location, keyed by workflow and phase, outside agent text), C-002 (no table column), C-003 (no model identifiers in runtime logic, no model call), C-005 (undeclared phase inherits), C-007 (agent text and validators unchanged), C-010 (mirror by the synchronisation command only).
- Current architecture baseline: F-004 (Phase Model tables are parsed, 37 phases), F-005 (one agent owns phases of unlike weight), F-006 (optional JSON file under config/ with a policy failure on invalid content, config/ is a managed install directory), F-007 (registry records reject unknown fields and enter every context slice), F-017 (the host accepts a per-dispatch override).

## Decision

- Selected option: O-001
- Decision statement: tier data lives in one shipped data file, config/model-tier-policy.json, keyed by workflow and phase, with exactly one host hint per tier. A hint is an opaque host alias string that the runtime copies verbatim and never interprets; the standard tier carries the reserved value inherit, meaning no override is passed, and the light and deep tiers carry the two alias values the host accepts. An absent file or an absent phase entry resolves to standard with inherit. A file that exists but is unreadable, names an unknown tier, or lacks a hint fails dispatch as a policy failure. The initial assignments are the phase-to-tier mapping of decision D-003 in the design package.
- Scope of impact: M-002 (new file), M-001 (loader and resolver), M-004 (coverage check reads the file), M-005 (documentation), M-007 (mirror); no change to M-011, M-012, M-013, M-015.

## Alternatives Considered

1. O-002 Tier column in each Phase Model table
- Benefits: the tier sits beside the phase row it describes.
- Risks: the tables are machine-parsed, so a column changes a parsed contract for the Task Router.
- Why not selected: violates C-002 and is eliminated.

2. O-003 Tier field on workflow records in registry/workflows.yaml
- Benefits: reuses the registry loader and keeps tiers next to workflow records.
- Risks: the record schema rejects unknown fields so the schema must change, and every tier edit changes the context digest of every later slice (F-007, F-020).
- Why not selected: ranks second; a larger impact surface (3 against 2) and a registry schema transition.

3. O-004 Tier declared in agent manifests or entrypoints
- Benefits: sits with the agent that does the work.
- Risks: one agent owns phases of unlike weight (F-005), so a per-agent tier cannot express the mapping, and it places tier text in agent files.
- Why not selected: violates C-001 and C-007 and is eliminated.

4. O-005 Abstract labels with a label-to-alias table in runtime code
- Benefits: the declaration carries no host alias strings.
- Risks: model identifiers would live in runtime logic.
- Why not selected: violates C-003 and is eliminated.

## Consequences

- Positive outcomes expected: one reviewable file states every assignment and hint; the coverage check can compare it with every Phase Model; removing the file restores prior behaviour for every phase.
- Tradeoffs accepted: one new file to maintain; hint values are host-specific strings held in configuration data; a hint takes effect only if the dispatching session passes it on (A-001).
- Risks introduced: R-002 (hint not applied or alias not accepted), R-007 (a phase added without an entry silently inherits until the coverage check runs), R-009 (a wrong declaration routes a deep phase to a cheaper tier).

## Validation Plan

- Metrics to monitor:
  - Count of Phase Model phases with no declaration entry, expected zero.
  - Non-deep share of invocations in a completed implement-feature run, expected at least 3 of 6.
- Verification checkpoints:
  - The coverage check fails against a declaration with one phase removed and against a stale entry.
  - A text search of agent module files finds zero tier assignments and a search of runtime logic finds zero model identifiers.
  - A dispatch with the file absent produces standard with inherit for every phase.
- Rollback or reversal conditions:
  - Delete the file if the host stops accepting the override or if more than one rejected cheaper attempt per run offsets the saving (R-006); every phase then inherits.

## Approval

- Architect: unsigned; the producing agent does not accept its own record.
- Tech Lead: pending the Design Gate decision.
- Product Owner (if scope-impacting): not required; scope is unchanged.
