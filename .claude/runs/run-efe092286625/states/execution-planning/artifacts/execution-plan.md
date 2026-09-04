```yaml
plan:
  planId: CKA-01-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-01-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:c11c3ae32c8bc1ffae41e19265d962b4
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
```

## Executive Summary

The `omn-agent` CLI's installation, documentation, and installation-health verification are made truthful for anyone installing into a clean environment: the runtime YAML dependency arrives with the install, the published documentation states the real dependency footprint, and `doctor` and `validate` report a finding naming any missing top-level runtime dependency instead of certifying a dead runtime. Success is defined by the ticket's verbatim criteria: a clean-venv `pip install` pulls PyYAML, `doctor` against a PyYAML-less environment reports a finding that names the module, and the existing `tests/` remain green. The work decomposes into seven tasks across four execution waves, opening in parallel with the dependency declaration (T-001) and the additive verification-approach definition (T-004). Any change to gate-decision or human-approval behaviour is out of scope and expressly forbidden by the ticket. The highest-impact risk is R-002: if no additive extension of the verification check can avoid the forbidden paths, the detection deliverable re-scopes with `omn-product-owner`. Plan status is complete; assumptions A-001 through A-003 require confirmation before the dependent tasks T-005 and T-007 execute.

## Business Objectives

1. A clean-environment installation of the CLI is runnable on first install: anyone installing into a fresh virtual environment receives a working runtime rather than one that dies on a missing module. Measured by a clean-venv install producing an installed CLI that starts without a missing-module failure. Traces to S-004, S-006, S-009.
2. Operators can trust installation-health verification: a broken installation is reported as broken with the missing module named, and a healthy installation remains certified healthy, so the verification baseline is worth building on. Measured by the finding reported against a dependency-less environment and by the preservation of currently certified behaviour. Traces to S-005, S-008, S-010, S-011.
3. Published documentation tells the truth about the tool's dependency footprint, so readers and adopters are not misled. Measured by the documentation's dependency claim matching the declared dependency set. Traces to S-003, S-007, S-013.

## Technical Objectives

1. The package's declared dependency set includes the third-party YAML library the runtime needs, so a clean-environment install resolves it. Verified by inspecting the resolved dependency set after a clean-venv install. Traces to business objective 1.
2. Installation verification resolves the top-level imports of installed runtime files and reports a finding naming any module that fails to resolve, in both `doctor` and `validate`. Verified by demonstration against an environment missing PyYAML. Traces to business objective 2.
3. The verification extension is strictly additive: `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, and every human-block path are unchanged; the existing `tests/` pass; every `verify_*.py` proof script reports PROVEN; a healthy installation is still certified healthy with no new findings. Verified by the existing test suite, the proof scripts, and a pre/post comparison of verification results in a healthy environment. Traces to business objective 2.
4. Corrected documentation is internally consistent: `README.md` and the HTML handbook `user-guide.html` agree with each other and with the declared dependency set. Verified by side-by-side review. Traces to business objective 3.

## Scope

### In Scope

- A fresh installation of the CLI into a clean environment includes every runtime dependency the CLI needs, and the installed runtime starts (S-006, S-009; delivered by T-001)
- Published documentation truthfully states the dependency footprint, including the HTML handbook wherever documentation is touched (S-007, S-013; delivered by T-002, T-003)
- Installation-health verification reports a finding that names any missing top-level runtime dependency, in both `doctor` and `validate` (S-008, S-010; delivered by T-004, T-005)
- Preservation of currently certified behaviour: a healthy installation is still certified healthy, the existing `tests/` stay green, every `verify_*.py` proof script reports PROVEN, and gate-decision behaviour is untouched (S-011, S-012, S-013; verified by T-006, T-007)

### Out of Scope

- Auditing or declaring runtime dependencies other than PyYAML. Excluded because PyYAML is the only undeclared dependency the ticket identifies; the extended check exists to surface any other missing top-level import as a finding rather than pre-declaring it.
- Import detection deeper than the top-level imports of installed runtime files, including function-local, conditional, and dynamic imports and transitive dependencies of third-party packages. Excluded because the ticket bounds the check to top-level import resolution and the additive-check-only constraint favours the narrowest check that delivers the stated outcome.
- Automatic remediation, meaning verification installing or repairing a missing dependency it finds. Excluded because the request asks that verification report and name what is missing, not fix it.
- CI gating on verification results and the work of any other backlog ticket (CKA-02, CKA-03). Excluded because the ticket names CKA-03 as a separate dependent change that this change, together with CKA-02, merely unblocks.
- Any change to gate-decision behaviour: `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path. Excluded because the ticket's additive-check-only constraint expressly forbids it.

### Deferred

None identified. The approved upstream scope definition records revisit triggers on its exclusions rather than deferring work into this plan.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | An additive extension of the `_check_python` verification can resolve top-level imports and name missing modules without altering any forbidden gate-decision or human-approval path | S-008, S-012 | The detection deliverable re-scopes with `omn-product-owner`; T-005 is blocked until a compliant approach or a re-scoped ticket exists | architect |
| A-002 | PyYAML is the only currently undeclared runtime dependency; any other missing import is surfaced by the extended check rather than pre-declared | S-006 | T-001, T-002, and T-003 extend to cover the additional dependency, and the upstream revisit trigger for other dependencies fires | architect |
| A-003 | A clean virtual environment and a dependency-less demonstration environment are available for recording acceptance evidence | S-009, S-010 | T-007 cannot record evidence and plan acceptance is unverifiable until the environments are provided | omn-qa |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | The current repository diverges from the ticket's description of the dependency declaration, the documentation claim, or the verification check | T-001, T-002, and T-005 re-scope and their estimates are invalidated | low | T-001, T-002, T-005 | T-004 records the current-state inventory before any build task starts | architect |
| R-002 | technical | No additive extension of the verification check can name missing top-level imports without touching a forbidden gate-decision or human-approval path (A-001 false) | The detection deliverable cannot be built as scoped; T-005 blocks and the ticket re-scopes with `omn-product-owner` | low | T-004, T-005 | T-004 resolves the approach before the build; escalation to `omn-product-owner` if no compliant approach exists | architect |
| R-003 | technical | The extended check reports findings for imports that legitimately do not resolve in a healthy installation | A healthy installation is no longer certified healthy, violating the preservation criteria | medium | T-005, T-006, T-007 | T-004 bounds what counts as a resolvable top-level import of an installed runtime file; T-006 designs explicit healthy-environment negative coverage | omn-qa |
| R-004 | dependency | Another undeclared runtime dependency is discovered during approach definition or build (A-002 false) | T-001, T-002, and T-003 extend; the upstream revisit trigger for additional dependencies fires | low | T-001, T-002, T-003 | The top-level import inventory recorded in T-004 confirms or refutes A-002 before the build completes | architect |
| R-005 | dependency | PyYAML is not installable from the package index at demonstration time | The clean-install acceptance evidence cannot be recorded | low | T-007 | T-006 confirms demonstration-environment availability, including index reachability, before evidence recording begins | omn-qa |
| R-006 | operational | The clean-venv or dependency-less demonstration environment is unavailable (A-003 false) | T-007 is blocked and plan acceptance cannot be verified | low | T-007 | T-006 confirms environment availability early, ahead of evidence recording | omn-qa |
| R-007 | delivery | Delivery slips beyond the Phase 1 (Days 0-30) window of the adoption plan | The CI gating change (CKA-03) remains blocked | low | plan-wide | Wave 1 tasks have no prerequisites and can start immediately; the plan carries no external decision on its critical path | omn-tech-lead |

## Task Breakdown

### T-001 Declare the runtime YAML dependency

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-006, S-009
- Status: ready
- Description: The package metadata in `pyproject.toml` declares PyYAML as a runtime dependency, so that installing the CLI into a clean environment resolves it and the installed runtime starts without a missing-module failure.
- Acceptance Criteria:
  - A `pip install` of the CLI into a freshly created virtual environment pulls PyYAML into the resolved dependency set
  - The installed CLI starts in that environment without a missing-module failure
- Gate: Review Gate

### T-002 Correct the published dependency claim

- Owner: omn-documentation
- Complexity: XS (confidence: high)
- Depends on: T-001
- Traces to: S-007
- Status: ready
- Description: `README.md` no longer claims the tool needs only the standard library, and its stated dependency footprint matches the declared dependency set.
- Acceptance Criteria:
  - No published documentation claims the tool needs only the standard library
  - The stated dependency footprint matches the dependency set declared by T-001
- Gate: Closure Gate

### T-003 Align the HTML handbook with the corrected documentation

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-007, S-013
- Status: ready
- Description: The HTML handbook `user-guide.html` agrees with every documentation statement this change touches, and release-impact notes for the dependency change are drafted.
- Acceptance Criteria:
  - A side-by-side review shows `user-guide.html` agrees with every touched documentation statement
  - Release-impact notes for the dependency and verification change are drafted
- Gate: Closure Gate

### T-004 Define the additive import-resolution approach for installation verification

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: none
- Traces to: S-008, S-012
- Status: ready
- Description: An approved approach exists for extending the `_check_python` verification, currently compilation-only, so that it resolves the top-level imports of installed runtime files and names any unresolvable module, demonstrated to leave `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, and every human-block path untouched; the approach records the current-state inventory of top-level imports, confirming or refuting A-002.
- Acceptance Criteria:
  - The approach states how a missing top-level import is detected and how the resulting finding names the missing module
  - The approach demonstrates that no forbidden gate-decision or human-approval path is altered, confirming or refuting A-001
  - The recorded top-level import inventory of installed runtime files confirms or refutes A-002
- Gate: Design Gate

### T-005 Extend installation verification to report missing top-level imports

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-004
- Traces to: S-008, S-010, S-012, A-001
- Status: assumption-dependent
- Description: Installation verification run against an install in an environment missing a runtime dependency reports a finding, not a healthy result, and the finding names the missing module, in both `doctor` and `validate`; verification behaviour against a healthy installation is unchanged.
- Acceptance Criteria:
  - `omn-agent doctor` against an install in an environment without PyYAML reports a finding (not OK) that names the missing module
  - `omn-agent validate` against the same installation reports a finding that names the missing module
  - Against an installation whose runtime dependencies all resolve, `doctor` and `validate` report a healthy result with no new findings
- Gate: Review Gate

### T-006 Design validation coverage for installation, detection, and preservation criteria

- Owner: omn-qa
- Complexity: S (confidence: high)
- Depends on: T-004
- Traces to: S-009, S-010, S-011, S-012, S-013
- Status: ready
- Description: Validation coverage exists for every plan acceptance criterion: the clean-venv install, the broken-environment findings from `doctor` and `validate`, healthy-environment preservation, the existing test suite, the proof scripts, and documentation agreement; availability of the demonstration environments is confirmed, confirming or refuting A-003.
- Acceptance Criteria:
  - Coverage addresses every plan acceptance criterion and every task acceptance criterion of T-001, T-002, T-003, and T-005
  - Healthy-environment preservation has explicit negative coverage: no new findings against an installation whose dependencies all resolve
  - Availability of the clean-venv and dependency-less demonstration environments is confirmed
- Gate: Verification Gate

### T-007 Record acceptance evidence for installation, detection, documentation, and preservation

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: T-001, T-002, T-003, T-005, T-006
- Traces to: S-009, S-010, S-011, S-013, A-003
- Status: assumption-dependent
- Description: Recorded evidence exists for every plan acceptance criterion, produced by executing the coverage designed in T-006 against the delivered work.
- Acceptance Criteria:
  - The clean-venv install demonstration and the installed CLI start are recorded
  - The broken-environment findings from `doctor` and `validate`, each naming the missing module, are recorded
  - The documentation review of `README.md` and `user-guide.html` against the declared dependency set is recorded
  - The `tests/` result, every `verify_*.py` verdict at PROVEN, and the healthy-environment pre/post verification comparison are recorded
- Gate: Verification Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | produces-consumes | The corrected documentation states the dependency footprint that T-001 declares |
| T-002 | T-003 | produces-consumes | The handbook mirrors the documentation statements that T-002 touches |
| T-004 | T-005 | decision-gate | The build's scope binds to the approved additive approach, which also confirms A-001 |
| T-004 | T-006 | contract | Coverage design targets the finding behaviour and resolution bounds the approach defines |
| T-001 | T-007 | verification | Evidence recording validates the declared dependency through the install demonstration |
| T-002 | T-007 | verification | Evidence recording validates the corrected dependency claim |
| T-003 | T-007 | verification | Evidence recording validates handbook agreement with the touched documentation |
| T-005 | T-007 | verification | Evidence recording validates detection and preservation behaviour |
| T-006 | T-007 | produces-consumes | Evidence recording executes the coverage that T-006 designs |
| Package index hosting PyYAML | T-007 | external | The clean-install demonstration waits on PyYAML being installable from the package index |

### 8.2 External Dependencies

| Responsible party | What is needed | Blocks |
|---|---|---|
| Package index hosting PyYAML | PyYAML installable into a clean virtual environment at demonstration time | T-007 |

### 8.3 Implementation Order

- Wave 1: T-001, T-004
- Wave 2: T-002, T-005, T-006
- Wave 3: T-003
- Wave 4: T-007

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because: the plan delivers new user-facing behaviour (a working clean install and a missing-dependency finding) against verbatim acceptance criteria, carries a design decision on the additive verification approach, and closes with documentation and release-impact updates; this plan is itself the `execution-planning` phase output of that workflow, following the approved scope definition.

| Phase | Tasks |
|---|---|
| scope-and-acceptance | completed upstream: scope definition approved at the Scope Gate |
| execution-planning | this plan (handoff) |
| solution-design-and-risk-assessment | T-004 |
| implementation | T-001, T-005 |
| quality-review | T-006, T-007 |
| documentation-and-release-handoff | T-002, T-003 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| technical-approach-definition | T-004 | architect | Primary |
| implementation-delivery | T-001, T-005 | omn-dev-1-implement | Primary |
| validation-design | T-006 | omn-qa | Primary |
| quality-verification | T-007 | omn-qa | Primary |
| documentation | T-002, T-003 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | architecture/clean-architecture-checklist.md | T-004 | Primary |
| S07 | testing/testing-strategy.md | T-006, T-007 | Primary |
| S12 | error-handling/error-handling-strategy.md | T-005 | Secondary |

## Acceptance Criteria

1. A `pip install` of the CLI into a freshly created clean virtual environment pulls PyYAML, and the installed CLI starts without a missing-module failure. Verifies business objective 1. Evidence: the install demonstration record from T-007.
2. `omn-agent doctor` run against an install in an environment without PyYAML reports a finding (not OK) that names the missing module, and `omn-agent validate` run against the same installation reports a finding that names the missing module. Verifies business objective 2. Evidence: the broken-environment demonstration record from T-007.
3. No published documentation claims the tool needs only the standard library; the stated dependency footprint matches the declared dependency set, and `user-guide.html` agrees with every touched documentation statement. Verifies business objective 3. Evidence: the documentation review record from T-007.
4. Currently certified behaviour is preserved: against an installation whose runtime dependencies all resolve, `doctor` and `validate` report a healthy result with no new findings; the existing `tests/` pass unchanged; every `verify_*.py` proof script reports PROVEN; and no gate-decision or human-approval path changed. Verifies business objective 2. Evidence: the test-suite result, proof-script verdicts, and healthy-environment pre/post comparison recorded by T-007 at the Verification Gate.

## Definition of Done

- [ ] Plan acceptance criteria 1 through 4 are verified with recorded evidence
- [ ] The Scope, Planning, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for T-001 through T-007 are satisfied or formally waived
- [ ] A-001 through A-003 are confirmed or converted to recorded decisions
- [ ] R-001 through R-007 are closed or accepted with named owners
- [ ] The existing `tests/` result and every `verify_*.py` verdict at PROVEN are recorded
- [ ] `README.md` and `user-guide.html` agree with the declared dependency set, and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Traceability Matrix

Statement register from input normalization, with forward coverage. Statements are drawn from the feature request in document order. Statements classified `context` shape interpretation and assert no requirement; they require no task.

| Statement | Kind | Summary | Covered by |
|---|---|---|---|
| S-001 | context | The CLI needs a third-party YAML library at runtime because manifests and registry files are YAML | context; motivates business objective 1 |
| S-002 | context | The package metadata declares an empty dependency list, so a clean install does not pull the YAML library | context; motivates T-001 |
| S-003 | context | The published documentation claims the tool needs only the standard library, which is false | context; motivates T-002 |
| S-004 | context | A clean-venv install produces an installation whose runtime dies on the missing YAML module | context; motivates business objective 1 |
| S-005 | context | `validate` and `doctor` certify that broken installation as healthy because `_check_python` only compiles runtime files and never resolves their imports | context; motivates T-004, T-005 |
| S-006 | outcome | Deliverable 1: PyYAML is declared in the dependencies in `pyproject.toml` so a clean install pulls it | T-001, A-002 |
| S-007 | outcome | Deliverable 2: the standard-library-only claim in `README.md` is corrected to match reality | T-002, T-003 |
| S-008 | outcome | Deliverable 3: `_check_python` is extended to resolve top-level imports so `validate` and `doctor` report a finding naming the missing module | T-004, T-005, A-001 |
| S-009 | outcome | Acceptance: `pip install` in a clean venv pulls PyYAML | T-001, T-006, T-007, A-003 |
| S-010 | outcome | Acceptance: `doctor` against an install in an environment without PyYAML reports a finding (not OK) and names the module | T-005, T-006, T-007, A-003 |
| S-011 | constraint | Acceptance: the existing `tests/` remain green | T-006, T-007 |
| S-012 | constraint | Additive check only: no alteration of `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path | T-004, T-005, A-001 |
| S-013 | constraint | Backlog definition of done: `tests/` green, all `verify_*.py` proof scripts PROVEN, no gate-decision behaviour change, `user-guide.html` updated where documentation is touched | T-003, T-006, T-007 |
| S-014 | context | Highest priority; Phase 1 (Days 0-30) of the adoption plan; blocks CKA-03 together with CKA-02; source is ticket CKA-01 in the adoption backlog under `docs/`, carrying recommendation R1 of the toolkit adoption review (2026-08-27) | context; motivates R-007 |
