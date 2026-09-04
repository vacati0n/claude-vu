```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0003
  featureName: Pull-request CI gate for discovered unit tests and proof-script verdicts
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-03-feature-request.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 12
  inputDigest: sha256:2fa4520294ab5f75c7525d234633a09f
  contextDigest: sha256:c5cc1c3bdd1db9b2d550e98fd7f931ed
```

## Metadata

- Feature name: Pull-request CI gate for discovered unit tests and proof-script verdicts
- Requested by: Ticket CKA-03 in the adoption backlog under `docs/` (Epic A — Verification baseline, Days 0–30), tracing to recommendation R1 of the adoption review (2026-08-27)
- Business goal: No regression in the unit-test suite or in any proof-script verdict can reach the default branch unnoticed
- Target outcome: Every pull request is verified automatically on both stated platforms, a verification failure names its source, and newly added test or verifier files are covered with no configuration effort
- Scope decision date: 2026-09-04

## Business Context

- Problem statement: Nothing gates a pull request today; the unit-test suite and the framework's proof scripts run only when a contributor remembers to run them locally, so a regression in any verifier or test can merge silently
- Value hypothesis: Gating every pull request on both verification surfaces closes the highest-leverage baseline gap the adoption review identified, protects every later change, and provides the CI hook that six dependent backlog tickets (CKA-06, CKA-07, CKA-08, CKA-09, CKA-13, CKA-15) require
- Affected users: Framework contributors and reviewers, whose regressions currently merge undetected; owners of the dependent backlog tickets that need the CI hook to exist
- Success measure: Stated in the ticket's acceptance criteria — a pull request that breaks any single verifier fails CI naming the verifier, and adding a new `tests/test_*.py` or `verify_*.py` file is picked up with no CI configuration change

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | Every pull request and every push to the default branch automatically runs the full unit-test suite, located by discovery, and any test regression is reported as a check failure | Delivers the first verification surface the ticket names; today the suite runs only on contributor memory | must-have |
| `S-002` | Every proof script matching `verify_*.py` under the framework payload runtime directory is executed individually on every pull request, its PROVEN verdict is asserted, and a failing verifier fails CI naming that verifier | Delivers the second verification surface and the ticket's verbatim expectation that a failure names the verifier | must-have |
| `S-003` | A newly added test or verifier file is exercised by CI with no CI configuration change | Delivers the discovery-never-curation expectation, guarding against the reviewed sibling project's failure mode of a hand-curated list that silently ran 14 of 77 suites | must-have |
| `S-004` | Both verification surfaces run on ubuntu and on windows for every pull request | Delivers the stated platform matrix | must-have |
| `S-005` | The staged rollout policy is encoded in the workflow and documented where contributors will see it: the ubuntu unit-test job required from day one; the verifier jobs and the windows job advisory for the first week after merge, then required | Delivers the stated rollout policy and its contributor-facing documentation | must-have |
| `S-006` | A crash or flake of one verifier does not change the reported result of any other verifier in the same CI run | Absorbs the stated operational fact that the recovery proof script is timing-sensitive and its crash can leave state that fails a downstream accounting check | must-have |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Cleaning up the three pre-existing orphan run directories from 2026-08-27 | A follow-up task already exists for the cleanup; this change is required only to state and absorb their handling so no required check ships permanently red | The design selects the clean-first option under `Q-001`, or the follow-up task is scheduled ahead of the rollout flip |
| `X-002` | Any change to gate-decision runtime behaviour: `record_gate_decision`, the gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path | The ticket forbids it; this change is additive CI configuration plus at most a small discovery helper, and changes no runtime behaviour | A separately scoped and governed change explicitly targets gate behaviour |
| `X-003` | CI surfaces beyond the two named verification surfaces (for example lint, coverage, or packaging), or triggers beyond pull requests and default-branch pushes | The request names exactly two verification surfaces and two triggers | A dependent backlog ticket (CKA-06, CKA-07, CKA-08, CKA-09, CKA-13, or CKA-15) requests an additional hook on this workflow |
| `X-004` | Fixing the recovery proof script's timing sensitivity or the render tests' colour-output assertions | The ticket asks CI to absorb these known operational facts, not to change the scripts or tests themselves | The flake rate observed during the advisory week makes the verifier job indefensible as a required check |
| `X-005` | Platforms beyond ubuntu and windows | The ticket states the matrix as ubuntu and windows runners | A contributor platform outside the stated matrix is shown to carry a verification gap |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | Every pull request and every default-branch push triggers a CI run in which the discovered unit-test suite executes, and a single deliberately failing test causes the unit-test check to report failure | `S-001` | demonstration: open a pull request carrying one failing test and observe the check fail; remove the failure and observe it pass | must-have |
| `A-002` | The CI environment does not set `NO_COLOR`, and the render tests that assert colour output pass in CI without spurious failure | `S-001` | review of the delivered workflow environment plus an observed green run of the render tests on both platforms | must-have |
| `A-003` | Every file matching `verify_*.py` under the framework payload runtime directory executes individually in a pull-request run, the number executed equals the number of matching files at that revision, and each is asserted to exit successfully with its PROVEN verdict | `S-002` | measurement: compare the verifier executions reported by one CI run against a count of matching files in the tree at the same revision | must-have |
| `A-004` | A pull request that breaks any single verifier fails CI, and the failure names that verifier | `S-002` | demonstration: introduce a single-verifier regression on a throwaway branch and observe the CI failure output name that script | must-have |
| `A-005` | Adding a new `tests/test_*.py` file is picked up by CI with no CI configuration change | `S-003` | demonstration: add a trivial new test file on a branch and observe it execute in the pull-request run with the workflow untouched | must-have |
| `A-006` | Adding a new `verify_*.py` file under the framework payload runtime directory is picked up by CI with no CI configuration change | `S-003` | demonstration: add a trivial new verifier on a branch and observe it execute, with its verdict asserted, with the workflow untouched | must-have |
| `A-007` | No CI step enumerates test or verifier files by name in a way that requires editing CI configuration when a file is added | `S-003` | review of the delivered workflow configuration against the discovery-not-curation constraint | must-have |
| `A-008` | Both verification surfaces complete on ubuntu and on windows runners within the same pull-request run | `S-004` | demonstration: observe one pull-request run containing both platform jobs, each executing both surfaces | must-have |
| `A-009` | The workflow encodes the stated staging: the ubuntu unit-test job blocks a pull request from day one; the verifier jobs and the windows job are non-blocking for the first week after merge and blocking thereafter | `S-005` | review of the delivered workflow against the stated policy, plus demonstration that a failing advisory job does not block a pull request during week one | must-have |
| `A-010` | The rollout policy is documented where contributors will see it, and every documentation page touched has its counterpart in `user-guide.html` updated to match | `S-005` | documentation review comparing the published policy text and the guide for parity | must-have |
| `A-011` | The delivered change states how the three pre-existing orphan-run accounting failures are handled — absorbed by the advisory window or cleaned first — and no required check is failing solely because of them at the moment the verifier jobs become required | `S-005` | review of the delivered handling statement plus observation of required-check status at the rollout flip | must-have |
| `A-012` | Forcing one verifier to crash or fail, including the timing-sensitive recovery proof, leaves every other verifier's reported result identical to a baseline run at the same revision | `S-006` | demonstration: force a single verifier failure and compare all other verifier results against the baseline run | must-have |

## Constraints and Dependencies

- Business constraints: Highest priority; the closing ticket of Phase 1 (Days 0–30) of the adoption plan; six later backlog tickets depend on this CI hook existing
- Regulatory or policy constraints: Additive change only — no alteration to `record_gate_decision`, the gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path; discovery, not curation — no step may enumerate test or verifier files by name; the backlog definition of done applies: `tests/` green, all `verify_*.py` proof scripts PROVEN, no change to gate-decision behaviour, and `user-guide.html` updated to match wherever docs are touched
- Delivery constraints: Staged rollout as stated in the ticket (ubuntu unit-test job required day one; verifier jobs and the windows job advisory for week one, then required); the pre-existing orphan-run accounting failures must not leave a required check permanently red; the CI environment must not set `NO_COLOR`; one verifier's flake or crash must not cascade into other verifiers' results
- External dependencies: CKA-01 (delivered, run-efe092286625) and CKA-02 (delivered, run-e0dba6763475); a hosted CI platform providing ubuntu and windows runners

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | The rollout-policy documentation, including `user-guide.html` parity wherever docs are touched, is inside this change | The ticket requires the policy documented where contributors will see it, and the backlog definition of done requires guide parity for touched docs | Delivery is not complete when the workflow runs; it is complete when contributors can read the staging policy where they look | omn-product-owner |
| `D-002` | Orphan-run cleanup is excluded (`X-001`); the change must instead state and absorb the handling so that no required check is permanently red | The ticket names two acceptable handlings and a follow-up task already exists for the cleanup itself | The verifier surface may report the pre-existing accounting failure during the advisory week; it may not still be red once the jobs become required (`A-011`) | omn-product-owner |
| `D-003` | Flake isolation is bounded as an outcome — one verifier's failure cannot alter another's result — not as an ordering or isolation mechanism | The ticket states the operational fact the design must absorb; the mechanism that absorbs it is the architect's decision | Design retains freedom of mechanism while the no-cascade outcome stays independently checkable at `A-012` | omn-product-owner |
| `D-004` | A small discovery helper script, if the design chooses one, lies inside this boundary; any runtime behaviour change lies outside it | Stated verbatim in the ticket's constraints | Implementation may add a helper without a scope change, and any runtime behaviour edit is a boundary violation rather than a widening | requester (ticket CKA-03) |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | Does the design absorb the three pre-existing orphan-run accounting failures inside the advisory window, or are the orphans cleaned before the rollout flip? | no | architect | technical-design phase |
| `Q-002` | Who owns flipping the verifier and windows jobs from advisory to required at the end of week one, and how is that flip recorded? | no | omn-tech-lead | before the workflow merges |

## Handoff

- Downstream owner: `planner` for decomposition and `architect` for the workflow design, after the Scope Gate
- Gate: Scope Gate; under the Producer Exclusion Rule the decision on this artifact rests with `omn-business-analyst`, and no gate decision is recorded here
- Evidence for the gate: in-scope items `S-001` through `S-006`; exclusions `X-001` through `X-005`, each with reason and revisit trigger; criteria `A-001` through `A-012`, each bound to one scope item with a named verification method; decisions `D-001` through `D-004` with rationale; questions `Q-001` and `Q-002`, both non-blocking; verdict bounded with status complete
- Deferred to downstream: the workflow structure and job topology, the discovery mechanism, the isolation and ordering mechanism (`D-003`), the choice between the two orphan-handling options (`Q-001`), the mechanics and ownership of the week-one flip (`Q-002`), decomposition into tasks and estimates, and the test strategy that carries the verification methods out
