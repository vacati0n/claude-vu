```yaml
releaseNote:
  releaseId: RN-2026-0005-CKA-03
  version: 0+CKA-03-unreleased
  sourceInputs:
    - type: verification-report
      reference: runs/run-8f8a1ab0d16e/states/quality-review/artifacts/review-package.md
    - type: final-change-summary
      reference: runs/run-8f8a1ab0d16e/states/implementation/artifacts/implementation-report.md
  producedBy: omn-documentation
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  releaseVerdict: released
  inputDigest: sha256:01a9cd2a2048444277d596e0426867c2
  contextDigest: sha256:bc0fb4ee128c1855f84c63b3ea12319c
```

## Metadata

- Version: 0+CKA-03-unreleased
- Release date and time: 2026-09-04, at the documentation-and-release-handoff phase of run run-8f8a1ab0d16e
- Environment: the repository tree — all five change-set entries of implementation report IR-2026-0005 are delivered in the repository and were read in full by review package RP-2026-0005; the merge itself is decided at the Closure Gate by omn-orchestrator, not recorded here
- Release owner: omn-tech-lead (owns the branch-protection enactment and the release disposition; per the technical design's rollout as recorded in IR-2026-0005 and RP-2026-0005)

## Highlights

- Feature additions: a CI verification workflow at `.github/workflows/verify.yml` (ticket CKA-03 in the adoption backlog under docs/) now gates every pull request and every default-branch push with two discovered surfaces — the unit-test suite by standard-library discovery on ubuntu and windows, and every proof script matching `verify_*.py` under the framework runtime directory, one job per discovered verifier per platform on a fresh runner — with four stable fan-in check names (`tests-ubuntu`, `tests-windows`, `verifiers-ubuntu-ok`, `verifiers-windows-ok`) for branch protection to bind to. Previously no CI configuration existed and a regression in any verifier or test could merge silently (IR-2026-0005, change C-001).
- Bug fixes: None identified.
- Improvements: contributor documentation now records the CI surface — the two discovered surfaces, the four check names and their standings, the advisory-by-omission rollout, and the flip precondition — in `README.md`, `docs/USER-GUIDE.md`, and the hand-synced `docs/user-guide.html`, with check-name parity across all three asserted by test (IR-2026-0005, changes C-003 to C-005); and a committed 13-test contract net in `tests/test_ci_workflow.py` locks the workflow's rename-sensitive properties into the unit-test suite, independently re-executed by the reviewer this run — 13 tests, OK (IR-2026-0005 change C-002; RP-2026-0005 Test Adequacy Assessment).

## Technical Changes and Compatibility

- API or contract changes: one new externally referenced contract — the four stable check names `tests-ubuntu`, `tests-windows`, `verifiers-ubuntu-ok`, and `verifiers-windows-ok` that branch protection binds to, documented as rename-sensitive in the workflow header and both documentation surfaces and locked by the committed regression net. No code interface changed (IR-2026-0005, Boundary Compliance).
- Database or migration impact: none — no data store, schema, or persistent state is created, read differently, or migrated; the workflow reads the repository tree and writes nothing into it (IR-2026-0005, Boundary Compliance).
- Configuration changes: branch protection must be configured on the hosting platform — a settings surface, not a repository file: `tests-ubuntu` is required from day one; `tests-windows`, `verifiers-ubuntu-ok`, and `verifiers-windows-ok` remain advisory-by-omission and flip to required after the week-one soak, contingent on the flip precondition of a default-branch run showing the self-hosting proof passing once the externally owned orphan-run cleanup lands. Enactment and recording of the flip belong to omn-tech-lead (IR-2026-0005 Handoff Notes and Q-003; RP-2026-0005 Review Scope).
- Backward compatibility notes: the change is purely additive at the repository level — removing the workflow definition restores the repository's prior state, and no runtime behavior changed in either direction, so no consumer relying on prior behavior is affected (IR-2026-0005, Out of scope and Boundary Compliance). The compatibility exposure runs forward, not backward: renaming any of the four check names would detach branch protection, which is why the committed net fails the suite on any rename (IR-2026-0005, risk R-002).

## Operational Notes

- Deployment considerations: nothing to deploy beyond the merge itself; the workflow activates on the triggers once merged. The verifier fan-out costs about 18 hosted jobs per run, accepted by the design against its negotiable cost constraint and mitigated by superseded-run cancellation (RP-2026-0005, Residual Risk). Verification jobs carry read-only repository access and no secrets (RP-2026-0005, Standards and Architecture Conformance).
- Monitoring and alerts: per RP-2026-0005 Residual Risk — watch per-verifier failure and flake rates by platform across the advisory week; the first live run's rendered check names, matrix fan-out from the discovery output, and fan-in behavior under real failure and cancellation; and continued byte-identity of the two platform wrapper copies, where drift fails the committed net. A healthy signal is the four fan-in names green on the default branch once the orphan cleanup lands.
- Rollback criteria: because the change is additive, deleting `.github/workflows/verify.yml` restores the prior repository state (IR-2026-0005, Out of scope). Red advisory verifier fan-ins on pre-existing repository state are expected and never justify reversion; that is exactly what the advisory standing exists to absorb (IR-2026-0005, risk R-001 mitigation).

## Validation Summary

- Test status: reviewed by omn-dev-2-reviewer in review package RP-2026-0005 with verdict approve-with-corrections — all hard design constraints verified against the delivered files, the committed 13-test regression net independently re-executed this run (13 tests, OK), the full-suite result (316 of 316, OK) recorded as claimed by IR-2026-0005 and not re-run, and local assertion runs T-001 through T-005 recorded as claimed with their substance independently reconstructed by the reviewer's own reading. Live hosted-run behavior — matrix fan-out, rendered per-verifier check names, fan-in semantics under real failure and cancellation, and both platforms' hosted-runner results — is verified only structurally until the first hosted runs, and its validation is handed to omn-qa (IR-2026-0005 Q-001; RP-2026-0005 Q-001 and readiness recommendation).
- Known risk acceptance: the roughly 18-job-per-run runner cost is accepted by the design against its negotiable constraint, recorded in the decision record's tradeoffs and owned by the Design Gate owners; the `main` branch-literal assumption stands accepted pending omn-tech-lead's confirmation (RP-2026-0005, Residual Risk).
- Post-release checks: confirm on the first live hosted runs that the discovery-fed matrix fans out per verifier per platform, the per-verifier check names render as documented, the two fan-ins fail — never succeed and never skip — under a real upstream failure and a real cancellation, and both platforms' suites pass (owned by omn-qa, Q-001); confirm a default-branch run shows the self-hosting proof passing after the orphan cleanup lands before any advisory check is flipped to required (RP-2026-0005, Residual Risk).

## Known Issues

| ID | Issue | Impact | Workaround | Tracking |
|---|---|---|---|---|
| `K-001` | The workflow's documented claim that default-branch push runs are never cancelled overstates the guarantee: cancellation of in-progress runs is disabled, but on the hosting platform a pending run in the shared concurrency group can be superseded by a newer push (RP-2026-0005, finding F-001, low severity) | Under rapid consecutive pushes an intermediate push run can be superseded, losing per-commit check attribution in a narrow race; the branch head is still always verified, so no regression lands unobserved | Treat per-commit check attribution on push runs as best-effort until the wording and configuration are reconciled | correction request CR-001 in RP-2026-0005, non-blocking, owner omn-dev-1-implement |
| `K-002` | No committed check ties the workflow's four interpreter-version literals (3.10) to the `requires-python` floor declared in `pyproject.toml` (RP-2026-0005, finding F-002, low severity) | A floor bump in either file alone passes the entire suite, silently diverging CI provisioning from the declared packaging floor | Change both files together whenever the interpreter floor moves, until the coupling test lands | correction request CR-002 in RP-2026-0005, non-blocking, owner omn-dev-1-implement |
| `K-003` | Live hosted-run behavior is verified only structurally: the matrix fan-out, rendered per-verifier check names, fan-in behavior under a real failure and a real cancellation, superseded-run cancellation, and both platforms' hosted-runner results have not been exercised, because no local check can reach them (IR-2026-0005, Unverified areas) | A reader relying on the gating cannot yet treat the live contract as confirmed; a hosted-platform divergence would surface only on the first real runs | None until the first hosted runs; advisory standing limits the blast radius of any surprise to visible-but-non-blocking checks | open question Q-001 in IR-2026-0005 (blocking at the Review Gate) and Q-001 in RP-2026-0005, owner omn-qa |
| `K-004` | The verifier fan-in checks will report red from the first live run on pre-existing repository state: three orphan run directories make the self-hosting proof's run-accounting check fail until the externally owned cleanup lands (IR-2026-0005, risk R-001) | Contributors see red `verifiers-ubuntu-ok` and `verifiers-windows-ok` checks that do not indicate a regression from this change | Read the fan-in checks as advisory during the soak; only `tests-ubuntu` is required day one | IR-2026-0005 risk R-001; cleanup owned by the existing follow-up task per the design's decision record D-003 |
| `K-005` | The push trigger names the branch literally as `main`; the repository snapshot carried no branch metadata to confirm it, and the workflow header flags the literal for correction (IR-2026-0005, deviation V-001) | If the actual default branch differs, no push run ever fires on it and the default-branch surface is silently absent | Correct the single literal in the workflow if the confirmation comes back different | open question Q-002 in IR-2026-0005, non-blocking, owner omn-tech-lead |
| `K-006` | The day-one required set and the later flip are not yet enacted or owned on record: branch protection is a platform settings surface no repository file carries, and the enactor and record location are unconfirmed (IR-2026-0005, Q-003) | Until enactment, no check blocks a merge at all, and the staged rollout the documentation describes is not yet in force | Enact `tests-ubuntu` as required at merge time; the flip follows the soak and its precondition | open question Q-003 in IR-2026-0005, non-blocking, owner omn-tech-lead |

## Communication

- Stakeholders notified: no stakeholder list was supplied, so the audience is inferred from the release-handoff basis of this phase and recorded as inferred — omn-orchestrator, which decides the Closure Gate this package feeds; omn-tech-lead, who owns the branch-protection enactment, the flip, and open questions Q-002 and Q-003; omn-qa, who owns the live hosted-run validation (Q-001); omn-dev-1-implement, who owns corrections CR-001 and CR-002; and repository contributors, who are reached through the delivered documentation in `README.md`, `docs/USER-GUIDE.md`, and `docs/user-guide.html`.
- Support handoff notes: three states will look broken and are not. First, red `verifiers-ubuntu-ok` or `verifiers-windows-ok` during the advisory week is expected on pre-existing state (the orphan run directories, K-004) and blocks nothing. Second, a verifier job that exits 0 can still correctly fail: a pass requires exit code 0 plus the script's own all-checks-passed summary with a non-negative verdict, so a script printing a negative form or a passed-count mismatch fails by design (RP-2026-0005, Standards and Architecture Conformance). Third, a failed fan-in with no failed verifier beneath it means an upstream job was cancelled — the fan-ins evaluate every upstream result and fail, never skip, on cancellation. Where to look first: the failing job's name carries the verifier's own filename, and the workflow header documents the check-name contract, the standings, and the flip precondition. One caution: the header's claim that default-branch push runs are never cancelled overstates the guarantee until CR-001 lands (K-001).
