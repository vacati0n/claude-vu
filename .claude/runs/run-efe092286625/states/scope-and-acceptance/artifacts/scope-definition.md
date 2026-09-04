```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0001
  featureName: Declare PyYAML and make doctor detect missing runtime dependencies
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-01-feature-request.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 8
  inputDigest: sha256:c11c3ae32c8bc1ffae41e19265d962b4
  contextDigest: sha256:c5cc1c3bdd1db9b2d550e98fd7f931ed
```

## Metadata

- Feature name: Declare PyYAML and make doctor detect missing runtime dependencies
- Requested by: Ticket CKA-01 in the adoption backlog under `docs/`, Epic A — Verification baseline, carrying recommendation R1 of the toolkit adoption review (2026-08-27)
- Business goal: A fresh installation of the `omn-agent` CLI works, its documentation tells the truth about what the tool needs, and its installation health verification can be trusted to catch a broken installation instead of certifying it
- Target outcome: A clean-environment install produces a runnable CLI; health verification run against an environment missing a runtime dependency reports a finding that names the missing module; everything existing verification certifies today still holds
- Scope decision date: 2026-08-27

## Business Context

- Problem statement: The CLI needs a third-party YAML library at runtime, but a fresh install into a clean environment does not bring it, the documentation claims the tool needs nothing beyond the standard library, and the tool's own health checks certify that broken installation as healthy — so a new adopter receives a dead runtime that the install, the docs, and the doctor all call fine
- Value hypothesis: If the required dependency arrives with the installation, the documentation states the true dependency footprint, and health verification names what is missing, then clean installs work the first time and `doctor`/`validate` become trustworthy enough for the adoption plan's Phase 1 verification baseline and the CI gating (CKA-03) that depends on it
- Affected users: Anyone installing the CLI into a clean environment; operators who rely on `omn-agent validate` and `omn-agent doctor` to certify installation health; readers of the project documentation; downstream, the CI gating change (CKA-03) that needs a doctor worth gating on
- Success measure: Supplied by the ticket verbatim: `pip install` in a clean venv pulls PyYAML; `omn-agent doctor` against an install in an environment without PyYAML reports a finding (not OK) and names the module; existing `tests/` remain green

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | A fresh installation of the CLI into a clean environment includes every runtime dependency the CLI needs, and the installed runtime starts rather than dying on a missing module | Delivers ticket deliverable 1 and the verbatim acceptance expectation that a clean-venv install pulls PyYAML | must-have |
| `S-002` | Published documentation tells the truth about the tool's dependency footprint; the incorrect claim that it needs nothing beyond the standard library is gone wherever a third-party dependency exists | Delivers ticket deliverable 2: correct the "standard library only" claim to match reality | must-have |
| `S-003` | An operator who runs the CLI's installation health verification against an environment missing a runtime dependency is told so: verification reports a finding, not a healthy result, and the finding names the missing module | Delivers ticket deliverable 3 and the verbatim acceptance expectation that doctor reports a finding (not OK) and names the module | must-have |
| `S-004` | Behaviour that existing verification certifies today is preserved: a healthy installation is still certified healthy, the existing tests still pass, and gate-decision and human-approval behaviour is unchanged | Delivers the verbatim acceptance expectation that existing `tests/` remain green, and the additive-check-only constraint (`D-003`) | must-have |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Auditing or declaring runtime dependencies other than PyYAML | PyYAML is the only undeclared dependency the ticket identifies; the extended verification check exists to surface any other missing top-level import as a finding rather than pre-declaring it | The extended check reports an unresolved top-level import other than the YAML module |
| `X-002` | Detecting imports deeper than the top-level imports of installed runtime files — function-local, conditional, or dynamic imports, and transitive dependencies of third-party packages | The ticket bounds the check to resolving top-level imports, and the additive-check-only constraint argues for the narrowest check that delivers the stated outcome | A missed-dependency defect traced to a non-top-level import, or a backlog ticket requesting deeper resolution |
| `X-003` | Automatic remediation — verification installing or repairing a missing dependency it finds | The request asks that verification report and name what is missing, not fix it | An explicit remediation request from operators |
| `X-004` | CI gating on verification results, and the work of any other backlog ticket (CKA-02, CKA-03) | The ticket names CKA-03 as a separate dependent change that this change, together with CKA-02, merely unblocks | CKA-01 and CKA-02 delivered and CKA-03 scoped as its own change |
| `X-005` | Any change to gate-decision behaviour: `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path | Expressly forbidden by the ticket's additive-check-only constraint | Only a separate, explicitly authorized governance change |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | Installing the CLI with `pip install` into a freshly created virtual environment pulls PyYAML, and the installed CLI starts without a missing-module failure | `S-001` | clean-venv install, then inspection of the resolved dependency set and an invocation of the installed CLI | must-have |
| `A-002` | No published documentation claims the tool needs only the standard library, and the stated dependency footprint matches the declared dependencies | `S-002` | review of the `README.md` dependency claim against the declared dependency set | must-have |
| `A-003` | The HTML handbook `user-guide.html` agrees with every documentation statement this change touches | `S-002` | side-by-side review of the touched documentation and `user-guide.html` | must-have |
| `A-004` | `omn-agent doctor` run against an install in an environment without PyYAML reports a finding (not OK) and names the missing module | `S-003` | demonstration: remove PyYAML from the environment, run doctor, and read the reported finding | must-have |
| `A-005` | `omn-agent validate` run against the same PyYAML-less installation reports a finding that names the missing module | `S-003` | demonstration: in the same broken environment, run validate and read the reported finding | must-have |
| `A-006` | Against an installation whose runtime dependencies all resolve, doctor and validate still report a healthy result with no new findings | `S-004` | run doctor and validate in an environment with all dependencies present and compare against the pre-change result | must-have |
| `A-007` | The existing test suite in `tests/` passes unchanged | `S-004` | run the existing test suite and read its result | must-have |
| `A-008` | Every `verify_*.py` proof script reports PROVEN | `S-004` | run each proof script and read its verdict | must-have |

## Constraints and Dependencies

- Business constraints: Highest priority in the adoption backlog; Phase 1 (Days 0–30) of the adoption plan; together with CKA-02, this change blocks CKA-03 (CI gating)
- Regulatory or policy constraints: Additive check only — the backlog forbids altering `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path; the backlog definition of done requires `tests/` green, all `verify_*.py` proof scripts PROVEN, no change to gate-decision behaviour, and `user-guide.html` updated to match wherever docs are touched
- Delivery constraints: Phase 1 (Days 0–30) window of the adoption plan; the ticket depends on nothing and can start immediately
- External dependencies: PyYAML, the third-party library the runtime needs and this change causes a clean install to provide; no other external dependency is stated

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | The missing-dependency check is bounded to resolving top-level imports of installed runtime files; deeper or dynamic import analysis is excluded (`X-002`) | The ticket bounds deliverable 3 to top-level import resolution, and the additive-check-only constraint favours the narrowest check that delivers the stated outcome | A dependency imported only inside a function or behind a condition is not caught at verification time and would still surface at runtime | omn-product-owner |
| `D-002` | `validate` is held to the same missing-module finding behaviour as `doctor`, although the ticket's verbatim acceptance criteria name only doctor | The request states that validate and doctor together should report a finding that names the missing module; bounding doctor alone would leave validate certifying the dead runtime this change exists to stop certifying | Adds criterion `A-005`; delivery is not acceptable while validate still reports a broken installation as healthy | omn-product-owner |
| `D-003` | Preservation of existing certified behaviour is recorded as an in-scope item (`S-004`) rather than left implicit in the constraints | The ticket makes "existing tests remain green" an acceptance expectation and forbids any gate-decision change; the gate must be able to check preservation rather than assume it | Delivery is not acceptable on detection alone: a healthy installation must remain certified healthy and gate behaviour untouched | omn-product-owner |

## Open Questions

None identified.

## Handoff

- Downstream owner: `planner` consumes this artifact after the Scope Gate; `architect` and `omn-qa` consume the criteria for the technical approach and the validation strategy
- Gate: Scope Gate; under the Producer Exclusion Rule the decision on this artifact rests with `omn-business-analyst`, and no gate decision is recorded here
- Evidence for the gate: scope items `S-001`–`S-004`; exclusions `X-001`–`X-005`; acceptance criteria `A-001`–`A-008`, each carrying a scope reference and a verification method; scope decisions `D-001`–`D-003` with rationale; no open questions; scope verdict `bounded` at status `complete`
- Deferred to downstream: decomposition into tasks, waves, and estimates (`planner`); the technical approach to dependency declaration, documentation correction, and import resolution (`architect` and the implementing roles); test strategy design and validation execution (`omn-qa`); the item carrying the most design uncertainty is `S-003`, the import-resolution extension under the additive-check-only constraint
