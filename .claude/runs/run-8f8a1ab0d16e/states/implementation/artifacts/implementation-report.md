```yaml
implementationReport:
  reportId: IR-2026-0005
  changeReference: CKA-03 -- CI workflow gating every pull request and default-branch push with the discovered unit-test and verifier surfaces (ticket CKA-03 in the adoption backlog under docs/, Epic A)
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-03-feature-request.md
    - type: technical-design
      reference: runs/run-8f8a1ab0d16e/states/solution-design-and-risk-assessment/artifacts/technical-design.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: implementation
  verificationStatus: partially-verified
  inputDigest: sha256:aa002c6a6625f9473332a8db3c0b7f77
  contextDigest: sha256:fbf2e953c78bf37cdf0ac7f7c01da129
```

## Metadata

- Report ID: IR-2026-0005
- Change reference: CKA-03 -- CI workflow gating every pull request and default-branch push with the discovered unit-test and verifier surfaces (ticket CKA-03 in the adoption backlog under docs/, Epic A)
- Workflow phase: implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

## Implementation Summary

- Change intent: every pull request and every default-branch push now carries a CI definition that runs two verification surfaces on ubuntu and windows -- the unit-test suite by standard-library discovery from the repository root, and every proof script matching `verify_*.py` under the framework runtime directory, each in its own job on its own runner -- where previously no CI configuration existed and a regression in any verifier or test could merge silently. A failing verifier fails CI naming itself in its check name, a verifier passes only on exit code 0 plus its own all-checks-passed summary with a non-negative verdict, and branch protection has a stable four-name check contract to bind to.
- Approach taken: the design's selected option O-001 as accepted -- one new workflow definition at `.github/workflows/verify.yml` containing: a discovery job whose single inline interpreter expression globs `verify_*.py` scoped to the framework runtime directory (the bundled package mirror and build output are outside the scope by construction, and no helper file is committed) and publishes the sorted list as job output, refusing an empty set; per-platform unit-test jobs (`tests-ubuntu`, `tests-windows`) provisioned at the packaging floor (3.10) with the package and its declared YAML dependency installed first; per-platform verifier matrices fanned out from the discovery output, one job per discovered script per platform on a fresh runner and fresh checkout, executing the script with no arguments and asserting exit 0 plus the generic summary-and-verdict contract, with fail-fast disabled so no failure cancels a sibling; and two always-run fan-in checks (`verifiers-ubuntu-ok`, `verifiers-windows-ok`) that evaluate every upstream result explicitly and fail -- never succeed and never skip -- on any upstream failure or cancellation. Advisory standing is encoded as absence from the branch-protection required-checks list, never as a per-job failure-tolerance flag; the check-name contract, rollout standings, and the flip's green-self-hosting precondition are documented in the workflow header and in the contributor documentation, with the hand-synced HTML handbook counterpart updated to match. A committed regression net locks the workflow's contract properties into the unit-test suite. Superseded pull-request runs are cancelled; jobs carry read-only repository access and no secrets.
- Design reference: decision records D-001 and D-002 implemented as accepted; D-003 honored by encoding its clean-first flip precondition in the workflow header and documentation while the cleanup itself remains owned by the existing follow-up task; inline decisions D-004 through D-007 implemented; impacted modules M-001 and M-008 delivered, M-003 through M-007 verified untouched, M-002 documented but not writable from this change; sequencing constraints P-001 through P-004 encoded and P-008 delivered; of technical design CKA-03-technical-design.
- Out of scope: the branch-protection required-checks configuration itself -- a hosting-platform settings surface, not a repository file, enacted by its named owners per the design's staged rollout; the orphan-run cleanup, owned by the existing follow-up task; the proof scripts, the existing unit tests, the framework runtime, and every gate-decision surface the ticket names, which are executed or documented here but never modified; and the dependent backlog tickets, including the documentation-synchronization automation. Leaving each is safe because this change is purely additive at the repository level: removing the workflow definition restores the repository's prior state, and no runtime behavior changed in either direction.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `.github/workflows/verify.yml` | added | The CI verification workflow: pull-request and default-branch push triggers, per-platform unit-test jobs, the inline discovery job, one verifier job per discovered script per platform with the generic exit-plus-verdict assertion, two always-run per-platform fan-in checks, read-only permissions, superseded-run cancellation, and the header documenting the check-name contract, the rollout standings, and the flip precondition | `D-001`, `D-002`, `D-004`, `D-005`, `D-006`, `D-007`, `M-001`, `P-001`, `P-002`, `P-003`, `P-004` |
| `C-002` | `tests/test_ci_workflow.py` | added | Committed regression net locking the workflow contract: topology and stable check names, matrix fed from the discovery output with fail-fast disabled, always-run fan-ins with explicit result evaluation, no color-suppression value and no failure-tolerance flag in effective lines, no curated test or verifier filename, the discovery expression enumerating exactly the present verifier set, the verifier-assertion wrapper's accept and reject semantics against synthetic scripts, and documentation parity of the check names | `M-008`, and the design's rename risk and file-addition acceptance intent (its structural-review mitigation), inside this agent's test latitude |
| `C-003` | `README.md` | modified | Contributor-facing record of the CI surface: the two discovered surfaces, the four stable check names and their standings, advisory-by-omission, the flip mechanism and its green-self-hosting precondition, and the self-containment expectation for new verifiers | `M-008`, `P-008` |
| `C-004` | `docs/USER-GUIDE.md` | modified | Handbook section documenting the CI gating, the check-name contract, and the rollout policy where contributors read | `M-008`, `P-008` |
| `C-005` | `docs/user-guide.html` | modified | Hand-synced HTML counterpart of the handbook change, preserving the documentation parity the definition of done requires | `M-008`, `P-008`, `F-013` |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | the workflow parses as YAML and encodes the accepted structure: both triggers, the six-job topology, the four stable check names, the verifier matrices fed from the discovery job's output, fail-fast disabled, always-run fan-ins, read-only permissions, and the 3.10 interpreter floor | static | `C-001` | `python ci_local_checks.py` (temporary verification script executed from a session scratch directory outside the repository) | pass |
| `T-002` | policy and curation scans: no color-suppression value set and no per-job failure-tolerance flag in any effective line, the header documents the check-name contract and standings, and no test or verifier filename is enumerated anywhere in the workflow | static | `C-001` | `python ci_local_checks.py` (same script, same run) | pass |
| `T-003` | the discovery step's inline expression, executed locally with the step-output file redirected, enumerates exactly the seven `verify_*.py` files present under the framework runtime directory, with a matching count and a non-empty guard | unit | `C-001` | `python ci_local_checks.py` (same script, same run) | pass |
| `T-004` | the verifier-assertion wrapper, extracted verbatim from the workflow, accepts a really passing proof script: `verify_manifests.py` executed with no arguments returned exit 0 and `2/2 checks passed -- CONFORMS` | unit | `C-001` | `python ci_local_checks.py` (same script, same run) | pass |
| `T-005` | the wrapper rejects each failure shape: nonzero exit, exit 0 with a negative-verdict summary, and exit 0 with no summary line, against synthetic scripts in a temporary tree; the two platform copies of the wrapper are byte-identical | unit | `C-001` | `python ci_local_checks.py` (same script, same run) | pass |
| `T-006` | the committed regression net: 13 tests locking the workflow topology, stable names, discovery-fed fan-out, fan-in semantics, environment and permission policy, no-curation property, discovery-expression correctness, wrapper accept and reject semantics, and check-name documentation parity across all three documentation surfaces | unit | `C-001`, `C-002`, `C-003`, `C-004`, `C-005` | `python -m unittest discover -s tests -p test_ci_workflow.py` | pass |
| `T-007` | post-change regression: the full suite by discovery from the repository root is green -- 316 tests, OK -- matching the most recent recorded full-suite baseline in count and verdict, so no existing test regressed | regression | `C-001`, `C-002`, `C-003`, `C-004`, `C-005` | `python -m unittest discover -s tests` | pass |

## Verification Results

- Verification method: local static and dynamic verification of the workflow definition -- YAML parse plus structural assertions, local execution of the discovery expression and the verifier-assertion wrapper extracted verbatim from the workflow (positively against a real proof script, negatively against synthetic failing scripts), documentation-parity scans, a committed regression net running inside the unit-test suite, and the full suite by discovery executed after the change. The hosting platform's own execution of the workflow cannot be exercised from this environment; the checks above are the compensating local evidence for exactly the properties a live run would exercise.
- Commands executed: `python -m unittest discover -s tests` (executed once before any change and once after; the pre-change run's per-test verdict stream was truncated by its capture pipe, so the regression claim rests on the post-change run -- 316 tests, OK -- which matches the most recent recorded full-suite baseline in both count and verdict, and on the fact that no source file consumed by the pre-existing 316 tests was modified); `python ci_local_checks.py` from a session scratch directory outside the repository (three runs: the first surfaced three raw-scan findings against the workflow's own header comment, repaired by removing concrete verifier filenames from the comment and scoping the policy scans to effective lines; the final run passed 27 of 27 assertions); `python -m unittest discover -s tests -p test_ci_workflow.py` (13 tests, OK).
- Result summary: 7 test-evidence entries executed, 7 passed, 0 failed; underlying counts: 27 of 27 local assertions, 13 of 13 committed regression-net tests, 316 of 316 full-suite tests.
- Unverified areas: live execution of the workflow on the hosting platform -- the matrix fan-out from the discovery job's output, the rendered per-verifier check names, fan-in behavior under a real upstream failure and a real cancellation, superseded-run cancellation, and both surfaces' results on hosted runner images across the two platforms, including interpreter provisioning, the runner environments' absence of a color-suppression value, and the recovery proof's timing behavior on shared hardware; and the branch-protection binding of the four check names, which is a platform settings surface no repository file can carry.

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | The push trigger in `C-001` names the branch literally as `main` rather than resolving the default branch, and the workflow header flags the literal for correction if the default branch differs | the design's requirement that the workflow trigger on every default-branch push | The trigger syntax requires a literal branch name and the repository snapshot supplied to this run carries no branch metadata from which to read the actual name; the platform-default name was encoded and its confirmation routed to the owner via `Q-002` | not-required |
| `V-002` | The verifier fan-out in `C-001` is realized as two per-platform matrix jobs rather than a single two-axis matrix | `D-001` -- one job per discovered verifier per platform, with one stable fan-in check per platform | The per-platform fan-ins must evaluate their own platform's aggregate result, and the platform reports an aggregate result per upstream job, not per matrix slice; splitting by platform yields exactly the per-verifier-per-platform job set `D-001` states while keeping each fan-in's evaluation exact | not-required |

## Boundary Compliance

- Module boundaries preserved: nothing under the framework payload directory changed -- the proof scripts, the framework runtime, the gate-decision surfaces the ticket names, the bundled package mirror, and the packaging metadata are all untouched, matching the design's no-change-verified modules; the change is additive at the repository level (one workflow definition, one test module, documentation), and the committed regression net's curation scan holds the workflow to the discovery boundary.
- Public interface changes: one new externally referenced contract -- the four stable check names `tests-ubuntu`, `tests-windows`, `verifiers-ubuntu-ok`, and `verifiers-windows-ok` that branch protection binds to, documented as a rename-sensitive contract in the workflow header and both documentation surfaces and locked by `C-002`. No code interface changed.
- Data or migration impact: none -- no data store, schema, or persistent state is created, read differently, or migrated; the workflow reads the repository tree and writes nothing into it.
- Declared side effects: exactly the five change-set paths, plus the two evidence artifacts this invocation wrote -- this report and its result envelope at their envelope-named paths, `runs/run-8f8a1ab0d16e/states/implementation/artifacts/implementation-report.md` and `runs/run-8f8a1ab0d16e/states/implementation/result-envelope.json`. The temporary verification script ran from a session scratch directory outside the repository and wrote nothing inside it; its synthetic verifier fixtures lived in interpreter-managed temporary directories. No other file was written, no external system was reached, and no gate decision was recorded.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | The verifier fan-in checks report red from the first live run on pre-existing repository state: the three orphan run directories the ticket records make the self-hosting proof's run-accounting check fail until the externally owned cleanup lands, and the previous delivery's report records further pre-existing proof-script findings | high | low | In place: advisory standing -- the fan-in and windows names are absent from the required-checks list at merge, so red is visible but non-blocking -- and the flip precondition documented in the workflow header, README, and handbook: a default-branch run showing the self-hosting proof passing before any verifier check becomes required |
| `R-002` | A future workflow edit renames one of the four stable check names, detaching branch protection: a renamed required check blocks every pull request as forever-expected, or blocking silently lapses | low | high | In place: the four names are locked by the committed regression net in `C-002`, which fails the suite on any rename, and are documented as a rename-sensitive contract in the workflow header and both documentation surfaces |
| `R-003` | The recovery proof's backoff-deadline assertion flakes on hosted-runner hardware despite a dedicated runner per verifier, especially on windows | medium | medium | In place: runner-boundary isolation and disabled fail-fast keep a flake from cascading into any other verifier's result; advisory standing keeps a flake from blocking during week one; and the documented flip precondition defers required standing until the advisory-week evidence supports it |

## Handoff Notes

- Reviewer focus areas: the verifier-assertion wrapper in `C-001` (the generic summary-and-verdict contract, duplicated across the two platform jobs -- byte-identity is asserted by `C-002`, but the duplication itself is where drift would start); the fan-in result evaluation (never-skip semantics under failure and cancellation, which only a live run can finally confirm); the branch literal in the push trigger (`V-001`); and the check-name contract sites (`R-002`).
- Follow-up work: enact the day-one required set (only `tests-ubuntu`) in branch protection and record the flip ownership per the design's flip-ownership decision (`Q-003`); validate the first live runs on both platforms (`Q-001`); observe the advisory week and land the externally owned orphan cleanup so the flip precondition can be met; then enact the flip as a settings-only change adding the two fan-in names and `tests-windows`; the documentation-synchronization automation remains with its own backlog ticket.
- Documentation impact: delivered within this change -- README, the handbook, and its hand-synced HTML counterpart all carry the check names, standings, flip mechanism, and orphan handling, and parity is asserted by `C-002`; the only remaining documentation event is recording the flip when its owner enacts it.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | Which run validates the workflow's live behavior on the hosting platform -- the matrix fan-out from the discovery output, the rendered per-verifier check names, fan-in failure and cancellation semantics, and both platforms' suite results -- before the verification claim for this change is treated as sufficient at the Review Gate? | yes | omn-qa | `C-001` |
| `Q-002` | Is the repository's default branch literally `main`, as the push-trigger literal in `C-001` assumes given the snapshot carries no branch metadata? | no | omn-tech-lead | `C-001` |
| `Q-003` | Who enacts the day-one required set and the later flip in branch protection, and where is the flip recorded -- the enactor and record location the design's flip-ownership decision assigns to the tech lead? | no | omn-tech-lead | `C-001` |
