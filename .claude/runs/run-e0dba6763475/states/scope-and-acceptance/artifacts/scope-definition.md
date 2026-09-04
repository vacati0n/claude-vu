```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0001
  featureName: Self-contained framework payload in the distributed package
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-02-feature-request.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 6
  inputDigest: sha256:c153cb3a0a4f3d8bc12bb9e8a069b1a0
  contextDigest: sha256:c5cc1c3bdd1db9b2d550e98fd7f931ed
```

## Metadata

- Feature name: Self-contained framework payload in the distributed package
- Requested by: Ticket CKA-02 in the adoption backlog under docs/ (Epic A — Verification baseline, Days 0–30), carrying recommendation R1 of the adoption review dated 2026-08-27
- Business goal: A user who installs the published package into a fresh environment can use the tool immediately, without locating or supplying a separate source checkout
- Target outcome: In a clean environment, a non-editable install of the published package initializes, installs, and validates successfully with no explicit source path, while every existing installation mode keeps its current behaviour
- Scope decision date: 2026-09-03

## Business Context

- Problem statement: A non-editable install of the published package produces a command-line tool that cannot install anything: the framework payload is not carried by the built package, and source resolution only finds a payload tree adjacent to a source checkout, so every fresh-environment user must pass an explicit source path to a checkout they may not have
- Value hypothesis: Removing the checkout dependency makes first-time adoption self-contained, which unblocks the verification-baseline epic and, together with the already-delivered CKA-01, the continuous-integration gating ticket (CKA-03) that depends on this change
- Affected users: Fresh-environment users who install the built package non-editably; secondarily, existing editable-install and explicit-source users, whose behaviour must remain unchanged
- Success measure: The two ticket acceptance checks hold — a clean-environment non-editable install runs init, install, and validate with no explicit source flag, and a dry-run install enumerates the same payload file count as an editable install

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | In a clean environment, a non-editable install of the built package yields a working tool: `omn-agent init`, `omn-agent install`, and `omn-agent validate` succeed with no `--source` flag | Delivers the headline request: fresh-environment users no longer need a framework checkout | must-have |
| `S-002` | A non-editable build carries the complete framework payload — all managed directories plus the seed directories — filtered by the same exclusion patterns the installer already applies, so the payload available to a non-editable install matches an editable install's | Delivers the ticket's first deliverable: the payload travels with the package instead of being assumed present on disk | must-have |
| `S-003` | Source resolution gains the bundled payload as a final fallback while existing behaviour is preserved: an explicit `--source` and a checkout-adjacent tree keep winning over the bundled copy, and when nothing resolves the failure message remains actionable | Delivers the ticket's second deliverable and its compatibility constraint: fresh environments resolve the bundled copy, existing users see no change | must-have |
| `S-004` | The built distribution's file lists accurately reflect the new packaging configuration, with no stale entries left from the previous configuration | Delivers the ticket's third deliverable: the distribution metadata is regenerated to match what is actually packaged | must-have |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Any alteration to gate-decision recording, gate-matrix semantics, producer exclusion, approval-requirement enforcement, or any human-block path | The ticket forbids it explicitly: this change is additive only | A separate change request that targets gate behaviour on its own authority, with its own gate evidence |
| `X-002` | Continuous-integration gating of the verification baseline (ticket CKA-03) | It is a separate backlog ticket that depends on this one; delivering it here would widen this change beyond its request | CKA-03 is scoped as its own change once this scope is accepted and delivered |
| `X-003` | Any change to source-resolution precedence for existing users, including preferring the bundled copy over an explicit source or a checkout-adjacent tree | The ticket constrains precedence to remain unchanged: existing candidates keep winning over the bundled copy | A future request that explicitly asks to reorder resolution precedence and supplies migration guidance for existing users |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | In a clean venv, `pip install <wheel>` (non-editable) followed by `omn-agent init && install && validate` succeeds — all commands exit successfully — with no `--source` flag | `S-001` | Scripted walkthrough in a clean virtual environment: install the built wheel, run the three commands, confirm each exits with status zero | must-have |
| `A-002` | `omn-agent install --dry-run` in a non-editable install enumerates the same payload file count as an editable install at the same revision | `S-002` | Paired dry-run comparison: run the dry-run in a wheel-installed environment and in an editable-install environment of the same revision, and compare the enumerated counts for equality | must-have |
| `A-003` | The payload carried by a non-editable build contains zero files matching the installer's existing exclusion patterns (`__pycache__`, `*.pyc`, and the rest of the applied set) | `S-002` | Inspection of the built distribution's payload file list against the installer's exclusion pattern set | must-have |
| `A-004` | Resolution selects the same source as before this change in each existing configuration — the explicit `--source` when given, the checkout-adjacent tree when present and no explicit source is given — and selects the bundled copy only when neither is present | `S-003` | Demonstration across three environments (explicit source given; adjacent tree present; neither present), observing which source is resolved in each | must-have |
| `A-005` | When no source candidate resolves, the command fails with the existing actionable guidance — the failure message names at least the explicit-source remedy — rather than an unhandled error | `S-003` | Demonstration in an environment where no candidate resolves, reviewing the failure message for the named remedy | must-have |
| `A-006` | Freshly built source and binary distributions show zero discrepancies between their file lists and the configured payload tree: every payload file is listed, and no listed entry is absent from the source tree | `S-004` | Comparison of the freshly built distributions' file lists against the source payload tree | must-have |

## Constraints and Dependencies

- Business constraints: Highest priority; Phase 1 (Days 0–30) of the adoption plan; together with the already-delivered CKA-01, this change blocks CKA-03
- Regulatory or policy constraints: Additive change only — the ticket forbids altering gate-decision recording, gate-matrix semantics, producer exclusion, approval-requirement enforcement, or any human-block path
- Delivery constraints: The backlog's definition of done applies — the existing test suite stays green, all proof scripts report PROVEN, gate-decision behaviour is unchanged, and wherever documentation is touched the handbook (`user-guide.html`) is updated to match
- External dependencies: None stated; the ticket depends on nothing

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | The packaging mechanism is not decided here; the scope states the outcome — a non-editable build carries the payload — and leaves the route to design | The ticket itself offers two routes (package-data configuration or manifest include directives); choosing between them is a technical decision owned by the architect, not a boundary decision | The design phase selects the mechanism; every acceptance criterion is stated mechanism-neutrally so either route can satisfy it | omn-product-owner |
| `D-002` | The backlog's definition-of-done items are recorded as delivery constraints, not duplicated as acceptance criteria | They apply identically to every ticket in the backlog and are enforced by downstream validation; duplicating them here would blur what this change specifically delivers | The acceptance table stays specific to this change; downstream validation enforces the definition of done against the delivery constraints recorded above | omn-product-owner |
| `D-003` | Preservation of existing resolution behaviour is recorded as an in-scope deliverable (`S-003`), not only as a constraint | The ticket states it both as a property of the deliverable (fallback after the existing candidates, error message kept actionable) and as a compatibility constraint; recording it in scope makes it acceptance-testable | A regression in existing users' resolution behaviour fails acceptance (`A-004`, `A-005`) rather than surfacing only as a policy breach | omn-product-owner |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | The ticket's parity check compares payload file counts between a non-editable and an editable install; is count parity the intended assurance, or should the file sets be identical? Count parity could pass while the contents differ | no | requester | Before the test strategy for `A-002` is designed in the validation phase |

## Handoff

- Downstream owner: `planner` consumes this artifact after the Scope Gate; `architect` and `omn-qa` consume it for design and validation strategy
- Gate: Scope Gate, decided by `omn-business-analyst` under the Producer Exclusion Rule; no gate decision is recorded here
- Evidence for the gate: In-scope items `S-001` through `S-004`, exclusions `X-001` through `X-003`, acceptance criteria `A-001` through `A-006`, decisions `D-001` through `D-003`, open question `Q-001`, and the verdict `bounded` at status `complete`, which the question set supports because no blocking question stands
- Deferred to downstream: the packaging mechanism and resolution design (architect); task decomposition, sequencing, and estimates (planner); the test strategy that carries the verification methods, including enforcement of the definition-of-done delivery constraints (omn-qa)
