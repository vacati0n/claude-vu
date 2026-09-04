```yaml
plan:
  planId: CKA-03-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-03-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:2fa4520294ab5f75c7525d234633a09f
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
```

## Executive Summary

This plan delivers a CI workflow that gates every pull request and every default-branch push on two discovered verification surfaces — the unit-test suite and every `verify_*.py` proof script under the framework payload runtime directory — for the contributors and reviewers of this repository, per ticket CKA-03 in the adoption backlog under `docs/`. Success is defined by the approved scope definition: a regression in any single test or verifier fails CI naming its source, and newly added test or verifier files are covered with no CI configuration change. The work decomposes into ten tasks across six execution waves, beginning with two decisions: the handling of the three pre-existing orphan run directories (T-010) and the ownership of the advisory-to-required flip (T-006). The staged rollout — ubuntu unit-test job required from day one; verifier jobs and the windows job advisory for week one, then required — is encoded in T-004, documented in T-005, and enacted in T-007. The highest-impact risk is R-008: the three orphan-run accounting failures leave a permanently red required check at the flip if T-010's decision is not carried out. Plan status is complete; open questions Q-001 and Q-002 are non-blocking because each is answered by a dedicated decision task (T-010 and T-006).

## Business Objectives

- No regression in the unit-test suite or in any proof-script verdict reaches the default branch unnoticed. Received by framework contributors and reviewers. Measured by every pull request and default-branch push carrying a gating verification run whose failures block merge according to the staged policy. Traces to `S-001`, `S-002`, `S-012`.
- Newly added verification files are covered with zero configuration effort, closing the reviewed sibling project's failure mode of a curated list that silently under-ran its suites. Received by contributors adding tests or verifiers. Measured by a new `tests/test_*.py` or `verify_*.py` file executing in CI with the workflow untouched. Traces to `S-003`, `S-013`, `S-015`.
- The CI hook that six dependent backlog tickets require exists and reaches its fully required state. Received by the owners of CKA-06, CKA-07, CKA-08, CKA-09, CKA-13, and CKA-15. Measured by the workflow being merged and the advisory-to-required flip being enacted and recorded. Traces to `S-020`.

## Technical Objectives

- The CI workflow triggers on every pull request and on every default-branch push, and both triggers run both verification surfaces on ubuntu and windows. Verified by observing one run per trigger containing both platform jobs, each executing both surfaces. Traces to business objective 1 and `A-001`.
- Both verification surfaces are located by discovery: no step enumerates test or verifier files by name in a way that requires a CI configuration edit when a file is added. Verified by configuration review plus a file-addition demonstration. Traces to business objective 2.
- Every discovered verifier executes individually, its PROVEN verdict is asserted, and a failing verifier fails CI naming that script. Verified by a forced single-verifier regression on a throwaway branch. Traces to business objective 1.
- One verifier's crash or flake does not change the reported result of any other verifier in the same CI run, absorbing the recovery verifier's timing sensitivity and its injected-run side effect on the run-accounting check. Verified by forcing a single verifier failure and comparing all other results against a baseline run at the same revision. Traces to business objective 1 and `A-004`.
- The staged rollout policy is encoded in the workflow: the ubuntu unit-test job blocks from day one; the verifier jobs and the windows job are advisory for the first week after merge, then required. Verified by workflow review plus a demonstration that a failing advisory job does not block during week one. Traces to business objectives 1 and 3.
- The CI environment does not set NO_COLOR, and the render tests that assert colour output pass without spurious failure. Verified by environment review plus an observed green run of the render tests on both platforms. Traces to business objective 1.

## Scope

### In Scope

- A CI workflow, delivered in the forge workflow directory, triggering on every pull request and every default-branch push and running both verification surfaces (`S-001`, `S-002`). Maps to T-001, T-002, T-003.
- Discovery-based location of both surfaces, with zero-configuration pickup of newly added test and verifier files (`S-003`, `S-013`, `S-015`). Maps to T-001, T-002, T-003, T-009.
- The unit-test surface, discovered from the repository root, on both platforms, in an environment that does not set NO_COLOR (`S-004`, `S-007`, `S-017`). Maps to T-002.
- The verifier surface: every `verify_*.py` under the framework payload runtime directory executed individually, its PROVEN verdict asserted, a failure naming the verifier, and no cross-verifier cascade (`S-005`, `S-006`, `S-012`, `S-016`). Maps to T-003, T-009.
- The staged rollout policy: encoded in the workflow, documented where contributors will see it with `user-guide.html` parity, flip ownership assigned, and the flip enacted at the end of week one (`S-008`, `S-009`, `S-010`, `S-011`, `S-019`). Maps to T-004, T-005, T-006, T-007.
- A stated, decided handling of the three pre-existing orphan-run accounting failures, so no required check ships permanently red (`S-018`). Maps to T-010.
- Validation coverage and executed verification carrying the approved scope definition's acceptance criteria (`S-012`, `S-013`). Maps to T-008, T-009.
- A small discovery helper script, only if the workflow design selects one, and with no runtime behaviour change (`S-014`). Maps to T-001.

### Out of Scope

- Cleaning up the three pre-existing orphan run directories from 2026-08-27. Excluded because a follow-up task already exists for the cleanup; this plan decides and states the handling (T-010) but does not perform the cleanup.
- Any change to gate-decision runtime behaviour: `record_gate_decision`, the gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path. Excluded because the ticket forbids it; this change is additive CI configuration plus at most a small discovery helper.
- Fixing the recovery proof script's timing sensitivity or the render tests' colour-output assertions. Excluded because the ticket asks CI to absorb these operational facts, not to change the scripts or tests.
- Platforms beyond ubuntu and windows. Excluded because the ticket states the matrix as ubuntu and windows runners.
- Verification surfaces beyond the two named (for example lint, coverage, or packaging) and triggers beyond pull requests and default-branch pushes. Excluded because the request names exactly two surfaces and two triggers.

### Deferred

- CI hooks for the dependent backlog tickets (CKA-06, CKA-07, CKA-08, CKA-09, CKA-13, CKA-15). Enters scope when a dependent ticket requests its extension of this workflow.
- Re-evaluation of the verifier-required policy. Enters scope if the flake rate observed during the advisory week makes a required verifier job indefensible.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The approved Scope Gate condition holds: the default-branch push trigger runs both verification surfaces, and the pull-request-only wording on the verifier surface in the upstream scope artifact is imprecision, not an approved narrowing | S-002 | The verifier jobs are removed from the push trigger; T-001 and T-003 re-scope their trigger coverage | omn-business-analyst |
| A-002 | The ticket's named discovery invocation for the unit-test surface, run from the repository root, is a stated implementation preference and is the intended mechanism | S-004 | T-002 re-scopes its discovery mechanism; the task set is unchanged | omn-tech-lead |
| A-003 | The repository will be hosted on a platform whose CI reads workflow definitions from the repository's `.github/workflows/` directory and provides ubuntu and windows runners | S-007 | T-002, T-003, and T-009 are blocked; the workflow location and the platform matrix re-scope | omn-tech-lead |
| A-004 | Sequential execution of the discovered verifiers in one defined order per runner, never in parallel on one machine, is an acceptable mechanism for the no-cascade outcome; the mechanism decision itself rests with `architect` in T-001 | S-016 | T-001 selects a different isolation mechanism and the isolation acceptance criteria of T-003 re-scope | architect |
| A-005 | The existing follow-up task for orphan-run cleanup can be scheduled before the rollout flip if T-010 selects the clean-first option | S-018 | Only the advisory-window option remains viable for T-010, and the flip in T-007 must re-verify required-check status at flip time | omn-tech-lead |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | The Scope Gate condition recorded in A-001 is overturned and the verifier surface is narrowed to pull requests only | T-001 and T-003 re-scope; default-branch pushes lose verifier coverage | low | T-001, T-003 | A-001 is confirmed by omn-business-analyst before T-001 completes | omn-business-analyst |
| R-002 | requirement | A workflow step enumerates test or verifier files by name | Silent under-coverage, the reviewed sibling project's failure mode; the discovery acceptance criteria fail | medium | T-002, T-003, T-008, T-009 | Discovery acceptance criteria on T-002 and T-003; explicit curation-scan coverage in T-008, executed in T-009 | omn-qa |
| R-003 | technical | The CI environment sets NO_COLOR | Render tests fail spuriously and the unit-test surface reports red without a regression | low | T-002, T-009 | Explicit environment acceptance criterion on T-002, verified in T-009 | omn-dev-1-implement |
| R-004 | dependency | The hosting platform is unavailable or does not provide the assumed workflow directory or the ubuntu and windows runners (A-003 false) | T-002, T-003, and T-009 are blocked; the matrix re-scopes | low | T-002, T-003, T-009 | omn-tech-lead confirms A-003 before the implementation wave begins | omn-tech-lead |
| R-005 | dependency | Repository administration for required-check settings is unavailable at the end of week one | T-007 cannot enact the flip; the staged policy stalls in its advisory state | low | T-007 | T-006 names the administering owner ahead of the flip; the external dependency is tracked in section 8.2 | omn-tech-lead |
| R-006 | operational | The timing-sensitive recovery verifier flakes under CI CPU load | Spurious verifier-job failures; the required flip becomes indefensible | medium | T-003, T-007, T-009 | The isolation and ordering mechanism is decided in T-001; the advisory week is observed through T-009 evidence before T-007 flips | architect |
| R-007 | operational | A crashed verifier leaves injected runs behind that the self-hosting verifier's run-accounting check reads in the same CI run (A-004 concerns this mechanism) | One verifier failure cascades into a second false failure, violating the no-cascade criterion | medium | T-001, T-003, T-009 | T-001 decides the isolation and ordering mechanism; T-009 verifies the no-cascade outcome by forced-failure comparison | architect |
| R-008 | delivery | The three pre-existing orphan run directories still fail the run-accounting check when the verifier jobs become required (A-005 concerns the clean-first option) | A permanently red required check blocks every pull request | high | T-007, T-010 | T-010 decides the handling; T-007 proceeds only when no required check is failing solely because of the orphans | architect |
| R-009 | delivery | Week one ends with no recorded owner or mechanism for the advisory-to-required flip | The rollout policy is never enforced and gating stays advisory indefinitely | medium | T-006, T-007 | T-006 records the owner and the recording mechanism before the workflow merges | omn-tech-lead |

## Task Breakdown

### T-001 Design the CI verification workflow

- Owner: architect
- Complexity: M (confidence: medium)
- Depends on: T-010
- Traces to: S-002, S-003, S-005, S-006, S-007, S-008, S-014, S-015, S-016, A-001
- Status: ready
- Description: A workflow design exists covering the job topology across both triggers and both platforms, the discovery mechanism for each surface (including whether a small discovery helper script is used, within the additive-only boundary), the verifier isolation and ordering mechanism that satisfies the no-cascade outcome, the staged rollout topology, and the statement of the orphan-run handling selected in T-010.
- Acceptance Criteria:
  - The design states how each surface is discovered and shows that no file is enumerated by name
  - The design states the isolation and ordering mechanism and how it prevents one verifier's crash or flake from changing another verifier's reported result, including the injected-run side effect on the run-accounting check
  - The design states the job topology per trigger and per platform and the advisory or required standing of each job over time
  - The design records the orphan-run handling selected in T-010
  - The design confirms no runtime behaviour change, naming the forbidden surfaces as untouched
- Gate: Design Gate

### T-002 Build the discovered unit-test jobs

- Owner: omn-dev-1-implement
- Complexity: S (confidence: low)
- Depends on: T-001
- Traces to: S-002, S-004, S-007, S-011, S-013, S-017, A-002, A-003
- Status: assumption-dependent
- Description: The workflow's unit-test jobs exist per the T-001 design: the full unit-test suite is located by discovery from the repository root and runs on both triggers and on both platforms, in an environment that does not set NO_COLOR, and a test regression is reported as a check failure.
- Acceptance Criteria:
  - One pull-request run and one default-branch push run each show the discovered suite executing on ubuntu and on windows
  - A deliberately failing test causes the unit-test check to report failure, and removing it restores a pass
  - No step of the delivered jobs enumerates test files by name
  - The job environment does not set NO_COLOR and the render tests pass on both platforms
- Gate: Review Gate

### T-003 Build the discovered verifier jobs

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-001
- Traces to: S-003, S-005, S-006, S-012, S-013, S-016, A-003, A-004
- Status: assumption-dependent
- Description: The workflow's verifier jobs exist per the T-001 design: every file matching `verify_*.py` under the framework payload runtime directory is discovered and executed individually per the designed isolation and ordering mechanism, each execution asserts a successful exit with its PROVEN verdict, and a failing verifier fails CI with output naming that script.
- Acceptance Criteria:
  - The number of verifier executions reported by one CI run equals the number of matching files in the tree at the same revision
  - A forced single-verifier regression fails CI and the failure output names that verifier
  - No step of the delivered jobs enumerates verifier files by name
  - The delivered jobs execute the verifiers per the isolation and ordering mechanism the T-001 design states
- Gate: Review Gate

### T-004 Encode the staged rollout policy in the workflow

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-001, T-002, T-003
- Traces to: S-008, S-009, S-010, S-011
- Status: ready
- Description: The staged rollout policy is encoded against the delivered jobs: the ubuntu unit-test job blocks a pull request from day one, and the verifier jobs and the windows job are non-blocking for the first week after merge and blocking thereafter, per the mechanism the T-001 design states.
- Acceptance Criteria:
  - Workflow review shows the ubuntu unit-test job required and the verifier and windows jobs advisory for week one
  - A failing advisory job is demonstrated not to block a pull request during the advisory window
  - The encoding matches the staging stated in the T-001 design
- Gate: Review Gate

### T-005 Document the staged rollout policy for contributors

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-004
- Traces to: S-008, S-019
- Status: ready
- Description: The rollout policy, as delivered, is documented where contributors will see it, including which jobs block when, the flip date and its recorded owner, and the stated orphan-run handling; every documentation page touched has its counterpart in `user-guide.html` updated to match.
- Acceptance Criteria:
  - The published policy text matches the encoded staging, the flip ownership record, and the orphan-run handling statement
  - Every touched documentation page has a matching `user-guide.html` counterpart, verified by parity review
- Gate: Closure Gate

### T-006 Assign ownership of the advisory-to-required flip

- Owner: omn-tech-lead
- Complexity: S (confidence: high)
- Depends on: none
- Traces to: S-009, S-010, S-011
- Status: ready
- Description: A recorded decision exists, before the workflow merges, naming who enacts the flip of the verifier and windows jobs from advisory to required at the end of week one and where that flip is recorded.
- Acceptance Criteria:
  - The decision record names exactly one accountable enactor for the flip
  - The decision record names the mechanism and location where the flip is recorded
- Gate: Design Gate

### T-007 Enact the advisory-to-required flip

- Owner: omn-tech-lead
- Complexity: S (confidence: low)
- Depends on: T-006, T-009, T-010
- Traces to: S-009, S-010, S-018, A-005
- Status: assumption-dependent
- Description: At the end of the first week after merge, the verifier jobs and the windows job are flipped from advisory to required by the owner T-006 named, the flip is recorded per the T-006 mechanism, and at the moment of the flip no required check is failing solely because of the three pre-existing orphan run directories.
- Acceptance Criteria:
  - The verifier and windows jobs are observed as required checks after the flip
  - The flip record exists in the location T-006 named
  - Required-check status at the flip shows no failure attributable solely to the pre-existing orphan runs, consistent with the T-010 decision
- Gate: Closure Gate

### T-008 Design validation coverage for the CI gate

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-012, S-013, S-014, S-015
- Status: ready
- Description: Validation coverage exists carrying every acceptance criterion of the approved scope definition into executable verification steps: regression demonstrations for both surfaces, file-addition pickup demonstrations, the verifier-count measurement, the forced-failure no-cascade comparison, the NO_COLOR environment review, the curation scan of the workflow configuration, the advisory non-blocking demonstration, and the review confirmation that no gate-decision runtime surface changed.
- Acceptance Criteria:
  - Every acceptance criterion of the approved scope definition maps to at least one designed verification step with named evidence
  - The coverage addresses each acceptance criterion of T-002, T-003, and T-004
  - The coverage includes negative demonstrations for both surfaces and both platforms
- Gate: Verification Gate

### T-009 Verify the delivered workflow against the validation coverage

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: T-002, T-003, T-004, T-008
- Traces to: S-006, S-012, S-013, S-016, S-017, S-019, A-003
- Status: assumption-dependent
- Description: The designed validation coverage is executed against the delivered workflow and the evidence is recorded: the demonstrations, the measurement, and the comparisons pass, or every failure is recorded with its named source.
- Acceptance Criteria:
  - Every designed verification step has a recorded pass result or a recorded, named failure
  - The forced single-verifier failure comparison shows every other verifier's reported result identical to the baseline run at the same revision
  - The verifier-count measurement matches the matching-file count at the verified revision
- Gate: Verification Gate

### T-010 Decide the handling of the pre-existing orphan run directories

- Owner: architect
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-018
- Status: ready
- Description: A recorded decision exists selecting one of the two handlings the ticket names for the three pre-existing orphan run directories that fail the self-hosting run-accounting check: the advisory window absorbs the failures, or the orphans are cleaned first via the existing follow-up task; the decision states what must be true at the rollout flip so no required check ships permanently red.
- Acceptance Criteria:
  - Exactly one of the two named handlings is selected and recorded with its rationale
  - The decision states the condition that must hold at the flip and who verifies it
  - If the clean-first option is selected, the decision names the scheduling dependency on the existing follow-up task
- Gate: Design Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-010 | T-001 | decision-gate | The design's stated orphan-run handling and staging statement change with the selected handling |
| T-001 | T-002 | contract | The unit-test jobs bind to the designed topology and discovery mechanism |
| T-001 | T-003 | contract | The verifier jobs bind to the designed discovery, isolation, and ordering mechanism |
| T-001 | T-004 | contract | The staging encoding binds to the designed rollout topology |
| T-002 | T-004 | produces-consumes | The staging attaches required standing to the delivered unit-test jobs |
| T-003 | T-004 | produces-consumes | The staging attaches advisory standing to the delivered verifier jobs |
| T-004 | T-005 | produces-consumes | The documentation describes the policy as delivered, not as intended |
| T-001 | T-008 | contract | The validation coverage targets the designed behaviour and its stated mechanisms |
| T-008 | T-009 | produces-consumes | Verification executes the designed coverage |
| T-002 | T-009 | verification | Verification validates the delivered unit-test jobs |
| T-003 | T-009 | verification | Verification validates the delivered verifier jobs |
| T-004 | T-009 | verification | Verification demonstrates the advisory non-blocking behaviour |
| T-006 | T-007 | decision-gate | The flip is enacted by the owner and mechanism the decision names |
| T-010 | T-007 | decision-gate | The selected orphan-run handling conditions what must hold at the flip |
| T-009 | T-007 | verification | The flip proceeds on recorded verification evidence, including required-check status |

### 8.2 External Dependencies

| Responsible party | What is needed | Blocks |
|---|---|---|
| Hosting platform operator | Availability of the hosted CI service with ubuntu and windows runners for this repository | T-002, T-003, T-009 |
| Repository administrator on the hosting platform | The required-check settings change that enacts the flip at the end of week one | T-007 |

### 8.3 Implementation Order

- Wave 1: T-006, T-010
- Wave 2: T-001
- Wave 3: T-002, T-003, T-008
- Wave 4: T-004
- Wave 5: T-005, T-009
- Wave 6: T-007

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because: the plan delivers new gating functionality with approved scope and measurable acceptance criteria, requires a design decision on workflow topology and isolation, produces implementation, verification, and contributor-facing documentation, and closes with a staged release policy — the full implement-feature phase sequence.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | completed upstream: approved scope definition |
| `execution-planning` | this plan (handoff) |
| `solution-design-and-risk-assessment` | T-001, T-006, T-010 |
| `implementation` | T-002, T-003, T-004 |
| `quality-review` | T-008, T-009 |
| `documentation-and-release-handoff` | T-005, T-007 |

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
| technical-approach-definition | T-001 | architect | Primary |
| architecture-decision-authoring | T-001, T-010 | architect | Primary |
| implementation-delivery | T-002, T-003, T-004 | omn-dev-1-implement | Primary |
| validation-design | T-008 | omn-qa | Primary |
| quality-verification | T-009 | omn-qa | Primary |
| documentation | T-005 | omn-documentation | Primary |
| release-readiness | T-006, T-007 | omn-tech-lead | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | architecture/clean-architecture-checklist.md | T-001, T-010 | Primary |
| S07 | testing/testing-strategy.md | T-008, T-009 | Primary |
| S10 | git/git-collaboration.md | T-002, T-003, T-004, T-007 | Secondary |

## Acceptance Criteria

1. A pull request carrying one deliberately failing test causes the unit-test check to fail on both platforms, and removing the failure restores a pass. Verifies business objective 1. Evidence: demonstration record from T-009.
2. A pull request that breaks any single verifier fails CI, and the failure output names that verifier. Verifies business objective 1. Evidence: forced-regression demonstration record from T-009.
3. Adding a new `tests/test_*.py` file and adding a new `verify_*.py` file under the framework payload runtime directory are each picked up by CI with no CI configuration change. Verifies business objective 2. Evidence: file-addition demonstration records from T-009.
4. The number of verifier executions in one CI run equals the number of `verify_*.py` files in the tree at that revision, each asserted to exit successfully with its PROVEN verdict. Verifies business objectives 1 and 2. Evidence: measurement record from T-009.
5. Forcing one verifier to crash or fail, including the timing-sensitive recovery proof, leaves every other verifier's reported result identical to a baseline run at the same revision. Verifies business objective 1. Evidence: comparison record from T-009.
6. The staged rollout is observed as stated: the ubuntu unit-test job blocks from day one, a failing advisory job does not block during week one, and the flip to required is enacted and recorded with no required check failing solely because of the pre-existing orphan runs. Verifies business objectives 1 and 3. Evidence: workflow review from T-004, advisory-window demonstration from T-009, and the flip record from T-007.
7. The rollout policy is published where contributors will see it, and every touched documentation page has its `user-guide.html` counterpart updated to match. Verifies business objective 3. Evidence: documentation parity review from T-005.

## Definition of Done

- [ ] All seven plan acceptance criteria are verified with recorded evidence
- [ ] Scope, Planning, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for T-001 through T-010 are satisfied or formally waived
- [ ] A-001 through A-005 are confirmed or converted to recorded decisions
- [ ] R-001 through R-009 are closed or accepted with named owners
- [ ] Q-001 and Q-002 are closed or explicitly accepted
- [ ] The backlog definition of done is evidenced: the unit-test suite green, every discovered verifier PROVEN, and review confirmation that no gate-decision runtime surface changed
- [ ] Documentation is published with `user-guide.html` parity for every touched page, and release-impact notes are recorded
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Does the design absorb the three pre-existing orphan-run accounting failures inside the advisory window, or are the orphans cleaned before the rollout flip? Answered by the T-010 decision. | No | architect | T-001, T-007, T-010 |
| Q-002 | Who enacts the advisory-to-required flip at the end of week one, and where is that flip recorded? Answered by the T-006 decision. | No | omn-tech-lead | T-006, T-007 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 — nothing gates a pull request today; regressions merge silently | T-002, T-003 |
| S-002 — a CI workflow runs on every pull request and on default-branch pushes | T-001, T-002, T-003, A-001 |
| S-003 — both surfaces are located by discovery, never a curated list | T-001, T-002, T-003 |
| S-004 — surface 1: the unit-test suite via discovery from the repository root | T-002, A-002 |
| S-005 — surface 2: every `verify_*.py` under the framework payload runtime directory, executed individually, PROVEN asserted | T-003 |
| S-006 — a failing script fails CI naming that verifier | T-003, T-009 |
| S-007 — platform matrix: ubuntu and windows runners | T-002, T-003, A-003 |
| S-008 — rollout policy encoded in the workflow and documented where contributors will see it | T-004, T-005 |
| S-009 — verifier jobs advisory for the first week after merge, then required | T-004, T-006, T-007 |
| S-010 — the windows job is advisory for week one | T-004, T-007 |
| S-011 — the ubuntu unit-test job is required from day one | T-002, T-004 |
| S-012 — acceptance: a PR breaking any single verifier fails CI naming the verifier | T-008, T-009 |
| S-013 — acceptance: a new test or verifier file is picked up with no CI config change | T-008, T-009 |
| S-014 — additive change only; at most a small discovery helper; no runtime behaviour change | T-001, T-008 |
| S-015 — no step may enumerate test or verifier files by name | T-001, T-002, T-003, T-008 |
| S-016 — the recovery proof is timing-sensitive and its crash can cascade into the run-accounting check | T-001, T-003, T-009, A-004 |
| S-017 — CI must not set NO_COLOR; render tests assert colour output | T-002, T-009 |
| S-018 — three pre-existing orphan run directories fail the run-accounting check; the design must state the handling | T-010, A-005, Q-001 |
| S-019 — backlog definition of done: tests green, verifiers PROVEN, no gate-decision change, `user-guide.html` parity | T-005, T-009 |
| S-020 — highest priority; six dependent tickets need this CI hook | T-004, T-007 |
