# Architecture Decision Record

## Metadata

- ADR ID: D-001
- Title: Verifier surface as a discovery-fed per-verifier matrix fan-out with runner-boundary isolation
- Date: 2026-09-04
- Status: Proposed
- Owners: omn-architect, omn-tech-lead (Design Gate owners)
- Related Work Items: CKA-03 (adoption backlog under `docs/`); execution plan tasks T-003, T-008, T-009 (consumers)

## Context

- Problem statement: every `verify_*.py` under the framework payload runtime directory must run in CI on every pull request and default-branch push, individually, with a failure naming its verifier, and one verifier's crash or flake must not change any other verifier's reported result. The recovery proof is timing-sensitive and, on abnormal termination, leaves injected runs in the working tree's runs area that the self-hosting proof's run-accounting check reads as failures.
- Business and technical constraints: C-002 (discovery, never curation), C-003 (individual execution, failure names the verifier), C-004 (ubuntu and windows matrix), C-006 (no cross-verifier cascade), C-010 (new files covered with no CI configuration change), C-011 (negotiable runner cost), C-012 (discovery scoped to the payload runtime directory, excluding bundled mirrors and build output).
- Current architecture baseline: F-002 (seven proof scripts exist in the framework runtime directory), F-003 (committed mirrors exist outside the payload), F-004 (every script runs with no arguments), F-005/F-006 (each script exits 0 exactly when all checks pass and prints a final summary verdict line), F-007 (the recovery proof mutates the runs area and leaves injected runs behind on crash), F-008 (the self-hosting proof's S8 check fails on any unaccounted run in the tree), F-010 (no CI configuration exists today).

## Decision

- Selected option: O-001 (per the evaluation table in section 5.2 of the technical design).
- Decision statement: the verifier surface is built as a discovery step that globs `verify_*.py` scoped to the framework payload runtime directory and publishes the list as its output, feeding a matrix of jobs — one per discovered verifier per platform — each on a fresh hosted runner with a fresh checkout, executing its verifier with no arguments and asserting exit code 0 plus the script's own all-checks-passed summary; two stable per-platform fan-in checks aggregate the matrix and report failure, never skip, on any upstream failure or cancellation. No execution ordering exists between verifiers; isolation is the runner boundary itself.
- Scope of impact: M-001 (the CI workflow), with read-only execution of M-004 (the proof scripts) and inherent exclusion of M-006 (bundled mirrors and build output) via the discovery scope; M-002 consumes the fan-in names.

## Alternatives Considered

1. O-002 — sequential consolidated loop (one verifier job per platform, discovered scripts iterated in a defined order, mutating recovery proof forced last, in-job workspace reset between scripts, failure naming via log annotations)
- Benefits: about a quarter of the runner cost; simpler job topology; sequential execution avoids concurrent sibling load on the timing-sensitive recovery proof.
- Risks: the no-cascade guarantee is conditional on maintained ordering and reset logic and decays silently when a future mutating verifier is added; failure naming is annotation-grade, not check-grade; the ordering rule embeds one script's name in configuration.
- Why not selected: outscored at reuse leverage (6 versus 8: it replaces the platform's matrix fan-out and fresh-runner isolation with bespoke loop-and-reset logic) and at quality attributes (conditional isolation, weaker failure naming).

2. O-003 — curated per-verifier jobs, one hardcoded workflow job per proof script
- Benefits: strongest naming and isolation with the simplest mental model.
- Risks: a new verifier file is silently not run until CI configuration is edited — the reviewed sibling project's exact failure mode.
- Why not selected: eliminated on hard constraint C-002 (files enumerated by name) and C-010.

3. O-004 — same fan-out topology with advisory-window-only orphan handling
- Benefits: identical structure to the selected option; no scheduling dependency on the cleanup task.
- Risks: a permanently red required check at the flip, or a by-name exemption of the failing verifier.
- Why not selected: eliminated on hard constraint C-009; addressed instead by D-003.

## Consequences

- Positive outcomes expected: a crashed or flaky verifier — including the recovery proof — cannot change any other verifier's reported result, because injected runs exist only in the crashed job's discarded workspace (F-007, F-008); failures surface as individually named checks (S-009); newly added verifiers join the matrix with no configuration change (C-010); verifier ordering ceases to exist as a maintained artifact.
- Tradeoffs accepted: roughly 18 hosted jobs per run versus 4 (C-011, negotiable), mitigated by cancelling superseded runs of the same pull request; per-verifier check names are dynamic, so blocking must bind to the stable fan-in names (D-002).
- Risks introduced: R-001 (recovery-proof flake rate on hosted runners, especially windows), R-006 (runner capacity at peak change rate), R-008 (a future verifier written to depend on execution order), R-009 (pull-request code executing on runners — jobs carry no secrets and read-only access).

## Validation Plan

- Metrics to monitor: per-verifier failure and flake rate during the advisory week, split by platform; verifier-execution count per run versus the scoped-glob file count at the same revision; queue latency per pull-request run.
- Verification checkpoints: the forced-failure no-cascade comparison (crash one verifier, compare all others to a baseline at the same revision); the file-addition pickup demonstration; the curation scan of the workflow; fan-in behavior under upstream cancellation — all in the plan's verification task, per P-002 and P-003 of the design.
- Rollback or reversal conditions: if hosted-runner capacity or the recovery proof's flake rate makes the fan-out indefensible during the advisory week, re-derive from the recorded option table (O-002 is the fallback shape) before any verifier check becomes required; removing the workflow definition restores the repository's current state at any time.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
