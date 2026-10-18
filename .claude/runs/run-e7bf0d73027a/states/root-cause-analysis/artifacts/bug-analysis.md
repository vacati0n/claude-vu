```yaml
bugAnalysis:
  analysisId: BA-run-e7bf0d73027a-root-cause-analysis-01
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
  contextDigest: sha256:5d58ca9209219c5223f02f3a6d5f8c67
```

## Metadata

- Bug ID: runs/inputs/recovery-x1-policy-exception-defect-report.md
- Reporter: framework operator, from the recovery verifier's X1 check and release checklist item FR-03 (`E-001`)
- Severity: medium
- Status: complete

## Symptom Summary

- Observed behavior: the recovery verifier exits 1 with 73/74 checks passed and verdict NOT PROVEN; check X1 judges the open envelope of the injected policy-failure run inadmissible because its policy-exception clearing action carries the role, decider and rationale placeholders (`E-002`, `E-003`, `E-015`, `E-022`).
- Expected behavior: per the defect report (`E-001`), a policy-exception clearing action on a state work item blocked awaiting_policy_exception is admissible with its three human-judgement arguments left as placeholders, inadmissible otherwise, and the verifier reports 74/74.
- First observed date: the defect-introducing change is commit 2e9e99e of 2026-09-26 (`E-008`, `E-024`); the earliest recorded observation is FC-016, committed 2026-10-09 (`E-009`); the report's "since 097e8f4" is narrower than the evidence.
- Affected environments: known affected — this worktree on Windows (`E-002`, `E-003`), a temporary copy of its tree with a byte-identical runtime (`E-015`, `E-022`), and the byte-identical bundled payload copy (`E-012`); known unaffected — none; not observed — CI runners on ubuntu and windows, whose red status is reported only (`E-001`, `Q-002`).

## Reproduction

- Preconditions: a checkout at or after commit 2e9e99e, Python available, TEMP and TMP pointing at a writable volume, and no leftover recovery-injection run directories; no input or flag is required, and --keep only retains the injected runs.
- Steps to reproduce: from the repository root, or from a temporary copy of the framework tree, run python .claude/runtime/verify_recovery.py --keep; read the X1 line and the final verdict line; open runs/run-d8870619db82/states/execution-planning/failure-envelope.json to see the open policy envelope; run the verifier again without --keep and confirm the same verdict and that git status is unchanged.
- Reproduction frequency: deterministic
- Evidence: the Evidence Register below, `E-001` to `E-025`; the code sites were located from the functions the defect report names, since the task context named no files.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Reporter states X1 fails on a policy-exception placeholder, CI is red on every pull request, and FR-03 fails for every framework change | supplied defect report, digest sha256:f9de6fe446b80423637c7ebcb42381e7 | low |
| `E-002` | Run 1: exit 1, 73/74 NOT PROVEN, only X1 fails, naming FE-run-d8870619db82-execution-planning-01 and the role, decider and rationale placeholders | command python .claude/runtime/verify_recovery.py in the worktree, triage invocation of this run | high |
| `E-003` | Run 2, preconditions unchanged: identical verdict and identical envelope id, so the injected run id is stable across invocations, not varying as reported | command python .claude/runtime/verify_recovery.py in the worktree, triage invocation of this run | high |
| `E-004` | The clearing-action builder emits a policy-exception command with three human-judgement placeholders for awaiting_policy_exception, and states a command is named only where verify_recovery finds it admissible | runtime/framework_runtime.py, clearing_action, lines 2039-2083, read in this invocation | high |
| `E-005` | cmd_policy_exception is a registered subcommand requiring --owner-role, --decided-by and --rationale that clears only a blocked state item with reason awaiting_policy_exception; it records that before it the block was terminal | runtime/framework_runtime.py, lines 4915-5047 and parser at 6132-6144, read in this invocation | high |
| `E-006` | The admissibility table exempts placeholders only after the gate and rollback flags, has no policy-exception row, and returns unknown subcommand for any unlisted command | runtime/verify_recovery.py, clearing_action_admissible, lines 607-688, read in this invocation | high |
| `E-007` | Scenario C induces an undeclared write, asserts the block is awaiting_policy_exception with decision type policy-exception, and X1 then checks the policy run's open envelopes | runtime/verify_recovery.py, scenario_c lines 533-570 and main lines 1174-1177, read in this invocation | high |
| `E-008` | Commit 96dfba8 gave this block a prose action; commit 2e9e99e added the command, the builder branch and the admissibility table together | git log and git show for 96dfba8 and 2e9e99e on both runtime files | high |
| `E-009` | Proposals FC-016 to FC-022 record X1 as a pre-existing FR-03 failure; FC-022 carries it in open item O-015 | grep for X1 over proposals, and FC-022 lines 178 and 209, re-read in this invocation | medium |
| `E-010` | Confirmed absence: no file under tests references policy-exception or clearing_action_admissible, and verify_recovery never executes the policy-exception action | grep over tests and runtime, re-run in this invocation; only runtime and omn_agent cli and runner match | high |
| `E-011` | CI discovers every verify_*.py under .claude/runtime and runs each as its own verifier job | .github/workflows/verify.yml, lines 5 and 62-79, read in this invocation | medium |
| `E-012` | The bundled payload copies of verify_recovery.py and framework_runtime.py are byte-identical to the authoritative ones, and a unit test asserts the bundle matches exactly | cmp against omn_agent/_bundled_payload/runtime in this invocation; tests/test_bundled_payload.py line 73 | high |
| `E-013` | Confirmed absence: none of the live run recovery ledgers holds a policy-exception clearing action command | grep over runs/*/recovery-ledger.json, triage invocation; refined by `E-023` | high |
| `E-014` | After both worktree runs the verifier had removed its injected runs and no tracked file under runs was left modified by them | git status after each run, triage invocation; re-confirmed by `E-022` | high |
| `E-015` | Attempt 3, changed precondition — a temporary copy of the tree with diff -rq showing the runtime identical, run with --keep: 73/74 NOT PROVEN, only X1 fails, same envelope id | command python .claude/runtime/verify_recovery.py --keep in D:/rvw-tmp-5df08e/rca-e7bf/tree | high |
| `E-016` | The kept policy run's execution-planning is blocked awaiting_policy_exception by the recovery controller; its open envelope is work_type state, producer planner, owner_roles empty, undeclared write memory/architecture.md | state.json and failure-envelope.json of run-d8870619db82 in the temporary copy | high |
| `E-017` | The current table rejects that action as emitted at the placeholder filter, and rejects it fully filled as unknown subcommand policy-exception, so both an exemption and a row are missing | clearing_action_admissible called from a scratch script on the kept envelope, temporary copy | high |
| `E-018` | The action executed exactly as written, with only role, decider and rationale filled, exits 0, moves the item blocked to pending, resolves the envelope, writes policy-exception.json, and leaves no open envelope; X1 then passes over 8 open envelopes in 4 runs | policy-exception run via the runtime in the temporary copy, then check_clearing_actions on the four injected runs | high |
| `E-019` | Negative executions each exit 2 with the store unchanged: producer role planner refused as policy-failure; a pending phase, an item blocked awaiting_recovery_task, one blocked awaiting_human_decision, and a repeat after clearance each refused as request-validation-failure | policy-exception run via the runtime against the four injected runs, temporary copy | high |
| `E-020` | On a completed item the same command exits 0 with REPLAY and records a replay in the store, so a zero exit alone does not mark the action admissible | policy-exception run on run-62db758f9671 execution-planning, temporary copy | high |
| `E-021` | The repaired run holds an open Planning Gate envelope whose gate action carries the same three placeholders, and X1 admits it, so open envelopes with human placeholders at X1 time are by design | scratch probe of open envelopes and the X1 recheck, temporary copy | high |
| `E-022` | Attempt 4, without --keep: exit 1, 73/74 NOT PROVEN, X1 alone fails; the injected runs were removed, run-f94564cb61ce matched the worktree, and the worktree git status equalled its baseline | command python .claude/runtime/verify_recovery.py in the temporary copy; diff -rq; git status in the worktree | high |
| `E-023` | 25 live recovery ledgers; 5 hold resolved awaiting_policy_exception envelopes carrying the older prose action, none open and none naming a command | per-entry read of runs/*/recovery-ledger.json in the worktree | high |
| `E-024` | Pickaxe: def cmd_policy_exception and def clearing_action_admissible both first appear in commit 2e9e99e | git log -S on both runtime files | high |
| `E-025` | The verifier's executable helper fills only the --decided-by placeholder and asserts any other placeholder is a harness fault | runtime/verify_recovery.py, executable, lines 592-604 | high |

## Impact Assessment

- User impact: framework contributors and operators; every framework change sees FR-03 fail and the recovery proof read NOT PROVEN (`E-002`, `E-009`); no run executed by the runtime is affected, since the command itself clears the block correctly (`E-018`, `E-023`).
- Business impact: taken from the supplied defect report's impact statement (`E-001`): FR-03 fails for every framework change, which weakens release predictability; the reported red CI is not observed in this run (`Q-002`); no separate business impact statement was supplied.
- Technical impact: the recovery verifier, the authority on recovery behaviour, gives a false negative on a runtime path proven correct end to end (`E-018`); a standing known failure also masks any genuinely inadmissible clearing action introduced later behind the same X1 failure (`E-009`); no security exposure, as the self-exception guard holds (`E-019`).
- Blast radius: the recovery verifier's admissibility judgement (X1, and D4, D23, D27, which share it); release checklist item FR-03 for every framework change; the CI recovery verifier job (`E-011`); the bundled payload copy shipped by package install (`E-012`); persisted records — proposals FC-016 to FC-022 and open item O-015 recording FR-03 as failed (`E-009`); no persisted open run envelope (`E-013`, `E-023`).

## Root Cause Analysis

- Root cause statement: the verifier's admissibility table was not extended when commit 2e9e99e made policy-exception the runtime's clearing action for awaiting_policy_exception, so it carries neither a placeholder exemption for that command's three human-judgement flags nor a row judging it against the item it names, a contract mismatch that rejects a correct action the runtime executes successfully.
- Why detection failed earlier: no unit test ties each command-naming branch of the clearing-action builder to a row of the admissibility table, and no test or verifier scenario executes the policy-exception action (`E-010`); X1 did fire, but FC-016 to FC-022 recorded it as a pre-existing FR-03 failure instead of raising a defect (`E-009`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Runtime contract change | Commit 2e9e99e made policy-exception the intended clearing action for awaiting_policy_exception, with role, decider and rationale as human-judgement placeholders, and the action clears the block when executed as written | `E-004`, `E-005`, `E-008`, `E-024`, `E-018` | high |
| `C-002` | Verifier table not extended | The same commit's table exempts placeholders only for gate and rollback and has no policy-exception row, so even a filled action is rejected; the runtime-at-fault account is eliminated by `E-018` and `E-019` | `E-006`, `E-008`, `E-017`, `E-018`, `E-019` | high |
| `C-003` | Scenario C leaves the envelope open | The induced policy failure blocks execution-planning awaiting_policy_exception and leaves its envelope open by design, as gate envelopes are; the harness-fault account is eliminated by `E-021` | `E-007`, `E-016`, `E-021` | high |
| `C-004` | X1 rejects it at the placeholder filter | Because of the mismatch in `C-002`, X1 judges that envelope inadmissible and the verifier reports 73/74 NOT PROVEN and exits 1 on every run; a timing or environment fault is eliminated | `E-002`, `E-003`, `E-014`, `E-015`, `E-022` | high |

## Fix Strategy

- Proposed fix: the verifier's admissibility judgement must hold policy-exception admissible exactly when its phase names a state work item whose status is blocked with reason awaiting_policy_exception, exempt from the placeholder filter only the role, decider and rationale of that command, and judge it inadmissible otherwise — including on a completed item, where the command exits 0 by replay (`E-020`); the gate and rollback exemptions stay as they are; the bundled payload copy must change identically; the persisted FR-03 failures in FC-016 to FC-022 stay as historical record, and O-015's X1 half is closed by its owner on a passing run, never by rewriting committed proposals.
- Alternative options: (a) revert the runtime action for this block to prose — clears X1 but hides the only clearing command and reopens the terminal block `E-005` records; (b) have the builder and the verifier read one shared declaration of command-naming actions and their human-judgement flags — prevents this class recurring at the cost of a wider change across both runtime files; (c) pre-fill the role in the action — rejected, as it prescribes a decision and the self-exception guard shows the role is a judgement (`E-019`).
- Regression risk: low
- Regression scope: X1 and the scenario D checks D4, D23 and D27 via the shared admissibility function and its placeholder filter, where too broad an exemption would hide real placeholders in gate, rollback or release actions; the executable helper via its one-placeholder assertion, if a scenario executes the policy-exception action (`E-025`); the bundled payload exact-match unit test via the mirrored copy; FR-03 and the CI recovery verifier job via the verifier's exit code.

## Validation Plan

- Verification steps: in a temporary copy of the tree, run python .claude/runtime/verify_recovery.py --keep and then without --keep, expecting 74/74 RECOVERY PROVEN with X1 passing over the policy run's open envelope, and git status unchanged afterwards; confirm the condition, not only the symptom, by showing the table now judges the emitted policy-exception action admissible on the blocked item and still inadmissible on each negative case below.
- Regression tests added: positive and negative admissibility cases for policy-exception — inadmissible on a pending item, an item blocked awaiting_recovery_task or awaiting_human_decision, a completed item, an unknown phase, a gate name, and a placeholder after --run-id or --phase; unchanged gate and rollback cases; a test pinning every command-naming branch of the clearing-action builder to an admissibility row; an end-to-end scenario that executes the action with role, decider and rationale filled and shows the block cleared and the envelope resolved, as `E-018` did.
- Monitoring signals after release: the recovery verifier job on the default branch shows green, observed first-hand rather than reported; FR-03 rows in later proposals record pass; any X1 output listing an inadmissible envelope indicates recurrence.

## Closure

- Resolution summary: None identified. Pending the downstream fix-bug phases and their gates.
- Linked PR and release: None identified.
- Prevention actions: bind each command-naming branch of the clearing-action builder to an admissibility row by test, and route a standing failure of a mandatory release checklist item to a defect instead of carrying it as pre-existing.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Does the policy-exception action, executed with role, decider and rationale filled, clear the scenario C block end to end? Answered yes in this invocation (`E-018`); retained so the identifier is not reused, and the retest of the fix stays with its owner | no | omn-qa | `C-001` |
| `Q-002` | Is the CI recovery verifier job red as reported? This run had no CI access; the default-branch job history would settle it | no | omn-orchestrator | none |
