```yaml
bugAnalysis:
  analysisId: BA-run-e7bf0d73027a-triage-and-impact-01
  defectReference: runs/inputs/recovery-x1-policy-exception-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/recovery-x1-policy-exception-defect-report.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:f9de6fe446b80423637c7ebcb42381e7
  contextDigest: sha256:121324ea4b3868f9df909d8a8060fd2c
```

## Metadata

- Bug ID: runs/inputs/recovery-x1-policy-exception-defect-report.md
- Reporter: framework operator, from the recovery verifier's X1 check and release checklist item FR-03 (`E-001`)
- Severity: medium
- Status: complete

## Symptom Summary

- Observed behavior: the recovery verifier exits 1 with 73/74 checks passed and verdict NOT PROVEN; check X1 judges the open envelope of the injected policy-failure run inadmissible because its policy-exception clearing action carries the role, decider and rationale placeholders (`E-002`, `E-003`).
- Expected behavior: per the defect report (`E-001`), a policy-exception clearing action on a state work item blocked awaiting_policy_exception is admissible with its three human-judgement arguments left as placeholders, inadmissible otherwise, and the verifier reports 74/74.
- First observed date: the defect-introducing change is commit 2e9e99e of 2026-09-26 (`E-008`); the earliest recorded observation is FC-016, committed 2026-10-09 (`E-009`); the report's "since 097e8f4" is narrower than the evidence.
- Affected environments: known affected — this worktree on Windows, two runs (`E-002`, `E-003`), and the byte-identical bundled payload copy (`E-012`); known unaffected — none; not observed — CI runners on ubuntu and windows, whose red status is reported (`E-001`) and not seen in this run (`Q-002`).

## Reproduction

- Preconditions: a checkout at or after commit 2e9e99e, Python available, TEMP and TMP pointing at a writable volume, and no leftover recovery-injection run directories; no input or flag is required.
- Steps to reproduce: from the repository root run python .claude/runtime/verify_recovery.py; read the line for X1 and the final verdict line; run it a second time unchanged; then run git status to confirm the verifier removed its injected runs.
- Reproduction frequency: deterministic
- Evidence: the Evidence Register below, `E-001` to `E-014`.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Reporter states X1 fails on a policy-exception placeholder, CI is red on every pull request, and FR-03 fails for every framework change | supplied defect report, digest sha256:f9de6fe446b80423637c7ebcb42381e7 | low |
| `E-002` | Run 1: exit 1, 73/74 NOT PROVEN, only X1 fails, naming FE-run-d8870619db82-execution-planning-01 and the role, decider and rationale placeholders | command python .claude/runtime/verify_recovery.py, attempt 1 | high |
| `E-003` | Run 2, preconditions unchanged: identical verdict and identical envelope id, so the injected run id is stable across invocations, not varying as reported | command python .claude/runtime/verify_recovery.py, attempt 2 | high |
| `E-004` | The clearing-action builder emits a policy-exception command with three human-judgement placeholders for awaiting_policy_exception, and states a command is named only where verify_recovery finds it admissible | runtime/framework_runtime.py, clearing-action builder, lines 2040-2083 | high |
| `E-005` | cmd_policy_exception is a registered subcommand that clears exactly a blocked state item with reason awaiting_policy_exception, and records that before it the block was terminal | runtime/framework_runtime.py, lines 4915-4975 and parser at 6132 | high |
| `E-006` | The admissibility table exempts placeholders only after the gate and rollback flags, has no policy-exception row, and returns unknown subcommand for any unlisted command | runtime/verify_recovery.py, clearing_action_admissible, lines 607-690 | high |
| `E-007` | Scenario C induces an undeclared write, asserts the block is awaiting_policy_exception with decision type policy-exception, and X1 then checks the policy run's open envelopes | runtime/verify_recovery.py, scenario_c lines 533-570 and main lines 1171-1177 | high |
| `E-008` | Commit 96dfba8 gave this block a prose action stating no runtime command clears it; commit 2e9e99e added the command, the builder branch and the admissibility table together | git log and git show for 96dfba8 and 2e9e99e on both runtime files | high |
| `E-009` | Proposals FC-016 to FC-022 record X1 as a pre-existing FR-03 failure; FC-022 carries it in open item O-015 | proposals/framework-change-proposal-FC-021.md and FC-022.md, grep for X1 across proposals | medium |
| `E-010` | Confirmed absence: no file under tests references policy-exception, and verify_recovery never executes the policy-exception action | grep over tests and runtime/verify_recovery.py | high |
| `E-011` | CI discovers every verify_*.py under .claude/runtime and runs each as its own verifier job | .github/workflows/verify.yml, header and discovery step | medium |
| `E-012` | The bundled payload copies of verify_recovery.py and framework_runtime.py are byte-identical to the authoritative ones, and a unit test asserts the bundle matches exactly | diff against omn_agent/_bundled_payload/runtime; tests/test_bundled_payload.py | high |
| `E-013` | Confirmed absence: none of the 24 live run recovery ledgers holds a policy-exception clearing action | grep over runs/*/recovery-ledger.json | high |
| `E-014` | After both runs the verifier had removed its injected runs and no tracked file under runs was left modified by them | git status after each run | high |

## Impact Assessment

- User impact: framework contributors and operators; every framework change sees FR-03 fail and the recovery proof read NOT PROVEN (`E-002`, `E-009`); no run executed by the runtime is affected (`E-005`, `E-013`).
- Business impact: taken from the supplied defect report's impact statement (`E-001`): FR-03 fails for every framework change and CI is red on every pull request, which weakens release predictability; no separate business impact statement was supplied.
- Technical impact: the recovery verifier, the authority on recovery behaviour, gives a false negative on a correct runtime path; a standing known failure also masks any genuinely inadmissible clearing action introduced later behind the same X1 failure (`E-002`, `E-009`).
- Blast radius: the recovery verifier's admissibility judgement (X1, and D4, D23, D27, which share it); release checklist item FR-03 for every framework change; the CI recovery verifier job; the bundled payload copy shipped by package install; persisted records — proposals FC-016 to FC-022 and open item O-015 recording FR-03 as failed; no persisted run envelope (`E-006`, `E-009`, `E-011`, `E-012`, `E-013`).

## Root Cause Analysis

- Root cause statement: the verifier's admissibility table was not extended when the runtime's clearing-action contract gained the policy-exception command, so a contract mismatch rejects a correct, intended action for its legitimate human-judgement placeholders.
- Why detection failed earlier: no unit test ties each command-naming branch of the clearing-action builder to a row of the admissibility table, and no test runs the policy-exception action (`E-010`); X1 did fire, but FC-016 to FC-022 recorded it as a pre-existing FR-03 failure instead of raising a defect (`E-009`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Runtime contract change | Commit 2e9e99e made the policy-exception command the intended clearing action for awaiting_policy_exception, with role, decider and rationale left as human-judgement placeholders | `E-004`, `E-005`, `E-008` | high |
| `C-002` | Verifier table not extended | The same commit's admissibility table exempts placeholders only for gate and rollback and has no policy-exception row; the runtime-at-fault account is eliminated by `E-004` and `E-005` | `E-006`, `E-008`, `E-004`, `E-005` | high |
| `C-003` | Scenario C leaves the envelope open | The induced policy failure blocks execution-planning awaiting_policy_exception and leaves its envelope open with the policy-exception action | `E-007`, `E-002` | high |
| `C-004` | X1 rejects it at the placeholder filter | X1 judges that envelope inadmissible, so the verifier reports 73/74 NOT PROVEN and exits 1, the same on every run; a harness or timing fault is eliminated | `E-002`, `E-003`, `E-014` | high |

## Fix Strategy

- Proposed fix: the verifier's admissibility judgement must recognise the policy-exception action as admissible exactly when it names a state work item blocked awaiting_policy_exception, with only the role, decider and rationale allowed to stay placeholders, and inadmissible otherwise; the bundled payload copy must carry the same change; the persisted FR-03 failures in FC-016 to FC-022 stay as historical record, and O-015's X1 half is closed by its owner on a passing run, never by rewriting committed proposals.
- Alternative options: (a) revert the runtime action for this block to prose — clears X1 but hides the only clearing command and reopens the terminal-block problem `E-005` records, so it trades a verifier fault for a runtime regression; (b) have the builder and the verifier read one shared declaration of command-naming actions and their human-judgement flags — prevents this class recurring at the cost of a wider change across both runtime files.
- Regression risk: low
- Regression scope: X1 and the scenario D checks D4, D23 and D27 via the shared admissibility function and its placeholder filter, where too broad an exemption would hide real placeholders in gate, rollback or release actions; the bundled payload exact-match unit test via the mirrored copy; FR-03 and the CI recovery verifier job via the verifier's exit code.

## Validation Plan

- Verification steps: re-run the reproduction twice and expect 74/74 RECOVERY PROVEN with X1 passing over the policy run's open envelope; confirm the condition, not only the symptom, by showing a policy-exception action is still judged inadmissible on an item not blocked awaiting_policy_exception and when a placeholder sits after any other flag.
- Regression tests added: a unit test pinning every command-naming branch of the clearing-action builder to an admissibility row; positive and negative admissibility cases for policy-exception; an end-to-end scenario that executes the policy-exception action with role, decider and rationale filled and shows the block cleared (`Q-001`).
- Monitoring signals after release: the CI recovery verifier job on the default branch shows green; FR-03 rows in later proposals record pass; any X1 output listing an inadmissible envelope indicates recurrence.

## Closure

- Resolution summary: None identified. Pending the Triage Gate, decided by omn-tech-lead, and the downstream fix-bug phases.
- Linked PR and release: None identified.
- Prevention actions: bind each command-naming branch of the clearing-action builder to an admissibility row by test, and route a standing failure of a mandatory release checklist item to a defect instead of carrying it as pre-existing.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Does the policy-exception action, executed with role, decider and rationale filled, clear the scenario C block end to end? No verifier or test has run it; an end-to-end scenario would settle it | no | omn-qa | `C-001` |
| `Q-002` | Is the CI recovery verifier job red as reported? This run had no CI access; the default-branch job history would settle it | no | omn-orchestrator | none |
