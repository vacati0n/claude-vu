```yaml
bugAnalysis:
  analysisId: BA-run-34fbc64712b5-triage-and-impact
  defectReference: FC-027/O-002
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/release-clearing-action-placeholder-defect-report.md
  producedBy: dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:71fa90ad70f8c8ffcafa075848b9659e
  contextDigest: sha256:d349d25df9ecf914b11063912c8be2cd
```

## Metadata

- Bug ID: FC-027/O-002
- Reporter: the FC-027 change proposal, open item `O-002` (owner architect), raised as the supplied defect report (`E-001`, `E-013`)
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: For a state work item blocked `awaiting_recovery_task` without guard `G3-PREDECESSOR`, `clearing_action` returns a `release` command ending `--detail <what happened>`; `shlex` splits the tail into `<what` and `happened>`, `verify_recovery.placeholders` returns `['<what happened>']`, X1 admissibility judges the action inadmissible, and a POSIX shell refuses the command with a syntax error (exit 2) so `release` never runs (`E-004`, `E-007`, `E-008`). The same command follows "To reclaim it sooner:" in every retry-class action (`E-006`). The report's account of the shell failure (redirect from a missing file `what`) differs from what this run observed (a syntax error on the trailing `>`); the observation is recorded, the report is not carried forward (`E-001`, `E-007`).
- Expected behavior: Per the defect report (`E-001`), the emitted `release` action parses as written and carries no placeholder `placeholders` recognises, the retry-class reclaim names the same runnable command, and X1 admits the action while every other verifier still passes; `release` already defaults `--detail` (`E-003`).
- First observed date: the placeholder is present in the builder since its first committed form dated 2026-09-04 (`E-012`); first recorded as a defect as `O-002` of FC-027 on 2026-10-19 (`E-013`); ongoing at the analysed revision.
- Affected environments: known affected: the runtime at the analysed revision, every non-guard `awaiting_recovery_task` block (aggregation-conflict, dependency-failure) and every retry-class action (`E-004`, `E-006`, `E-010`); known unaffected: the guard-raised `G3-PREDECESSOR` path, which emits prose (`E-005`); not observed: the host's native non-POSIX shells, and a full `verify_recovery.py` run over its induced scenarios (`Q-001`, `Q-002`).

## Reproduction

- Preconditions: Python with `.claude/runtime` on the import path at the analysed revision; a state work item dict with `work_type` state; a classification from `recovery_policy.classify` for a non-retryable class whose blocked reason is `awaiting_recovery_task` (aggregation-conflict or dependency-failure) with no guard, or for a retryable class with budget left (output-schema-failure, worker-loss, invocation-transport-failure).
- Steps to reproduce: (1) import `framework_runtime`, `recovery_policy`, and `verify_recovery`; (2) build `cls = recovery_policy.classify("aggregation-conflict", attempt=1, attempts_lost=0, max_attempts=3, seed="s")`; (3) call `framework_runtime.clearing_action("run-x", {"state_id": "triage-and-impact", "work_type": "state", "work_item_id": "x"}, cls, cls.blocked_reason)`; (4) evaluate `verify_recovery.placeholders(shlex.split(action))` and observe `['<what happened>']`; (5) repeat with dependency-failure, then with each retryable class using `verify_recovery.runtime_command(action)`; (6) in an empty scratch directory run the action through `bash -c` and observe the syntax error and exit 2; (7) with `verify_recovery.load_state` replaced in memory by a state holding the item blocked by the recovery controller, call `clearing_action_admissible` on the action and on the same action with `--detail <what happened>` removed.
- Reproduction frequency: deterministic
- Evidence: the Evidence Register below, `E-001` to `E-015`.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Reports the unquoted --detail placeholder in the release action, its reuse in retry prose, X1 rejection since FC-027, a redirect failure in a POSIX shell, severity medium | supplied defect-report, digest sha256:71fa90ad70f8c8ffcafa075848b9659e | low |
| `E-002` | release_cmd is composed once with a literal unquoted --detail placeholder, returned whole for a non-guard awaiting_recovery_task block and appended to retry prose; the gate and policy-exception branches quote their values and leave placeholders only on owner-role, decided-by, rationale | source read of runtime/framework_runtime.py clearing_action, lines 2038-2084 | high |
| `E-003` | release declares --detail optional with default "adapter did not report a result"; release --help lists it as optional | source read of runtime/framework_runtime.py line 6115; command framework_runtime.py release --help | high |
| `E-004` | For aggregation-conflict and dependency-failure without a guard, the action ends --detail followed by two argv entries; placeholders returns one entry, the whole bracketed text; 2 of 2 classes | command: scratch script calling clearing_action, shlex.split, verify_recovery.placeholders | high |
| `E-005` | With guard G3-PREDECESSOR the same classification yields prose naming no command | command: same scratch script, guard path | high |
| `E-006` | For output-schema-failure, worker-loss, invocation-transport-failure the action starts "none required" and its embedded command yields the same placeholder; 3 of 3 classes | command: same scratch script, runtime_command then placeholders | high |
| `E-007` | The emitted action run through bash fails with "syntax error near unexpected token newline", exit 2; the command does not execute | command: bash -c with the emitted action, in an empty scratch directory | high |
| `E-008` | clearing_action_admissible: non-retry action inadmissible, reason names the placeholder; retry action admissible as "retry: nothing required"; same action without --detail admissible against the blocked item | command: scratch script with an in-memory state stand-in; no run directory read or written | high |
| `E-009` | The exemption set for release is empty; only gate, rollback, and an awaiting_policy_exception item exempt human flags, and --detail is in none of them; retry prose short-circuits before parsing | source read of runtime/verify_recovery.py runtime_command, placeholders, clearing_action_admissible | high |
| `E-010` | Non-retryable classes with blocked reason awaiting_recovery_task are aggregation-conflict, dependency-failure, gate-rejection; the recovery controller emits envelopes with no guard; gate-rejection routes to rollback | source read of runtime/recovery_policy.py FAILURE_POLICIES and framework_runtime.py emit call sites | high |
| `E-011` | 33 recovery-ledger entries across 14 committed runs carry the placeholder action (31 retry form, 2 release form); all resolved; confirmed 0 open | command: scratch read-only scan of runs/run-*/recovery-ledger.json | high |
| `E-012` | The placeholder string is present in the builder since the commit dated 2026-09-04 that first added it | command: git log -S over runtime/framework_runtime.py | high |
| `E-013` | FC-027 records O-002 open (owner architect), the builder left unchanged, and a --detail exemption refused at its Triage Gate; quoted text containing angle brackets is now judged a placeholder (O-001) | read of proposals/framework-change-proposal-FC-027.md lines 38, 125, 150 | medium |
| `E-014` | 30 admissibility tests pass; placeholder cases use hand-built release strings; the builder pin test checks only subcommand names; no test drives the emitted release action | read and run of tests/test_clearing_action_admissibility.py | high |
| `E-015` | Operator documentation shows release with a quoted --detail placeholder, a form placeholders also recognises when not exempt | read of runtime/README.md line 107 | high |

## Impact Assessment

- User impact: an operator clearing a non-guard `awaiting_recovery_task` block, or reclaiming a retry-scheduled item early, copies the prescribed command and the shell refuses it; the operator must edit the command by hand before `release` runs (`E-004`, `E-006`, `E-007`). Affected population: every operator of the runtime meeting those conditions; frequency of those conditions is not measured here.
- Business impact: not supplied. No business impact statement accompanied this defect, so the severity rests on technical impact alone and `Q-003` routes the question; the reporter's severity in `E-001` is recorded as context and did not set it.
- Technical impact: a secondary recovery path fails as written, with an acceptable workaround (omit `--detail`, which `release` defaults) (`E-003`, `E-008`); no state transition, ledger write, or `release` semantics is altered, because the command never executes (`E-007`); the recovery verifier refuses any open envelope carrying the non-retry form, while the retry form escapes X1 because it is judged as prose (`E-008`, `E-009`).
- Blast radius: the clearing-action builder in the runtime and every failure envelope it writes for non-guard `awaiting_recovery_task` blocks and retry-class schedules (`E-002`, `E-010`); the per-condition failure envelope files and run recovery ledgers, where persisted entries carry the placeholder (33 entries across 14 committed runs, all resolved, none open) and are echoed unchanged by `status` and `next` through the live clearing-action lookup (`E-011`); the operator shell boundary (`E-007`); the recovery verifier X1 and its execution guard, which share one placeholder definition (`E-008`, `E-009`); operator documentation that shows the same command with a quoted placeholder (`E-015`). Not reached: guard-raised blocks (`E-005`), gate, rollback, and policy-exception actions (`E-002`). Not observed: non-POSIX shells and the induced runs of a full verifier run (`Q-001`, `Q-002`).

## Root Cause Analysis

- Root cause statement: The clearing-action builder emits `--detail` as an unquoted human-fill placeholder although `release` defaults that flag and no human judgement attaches to it, so the `release` action breaks the runs-as-written contract that the gate and policy-exception branches honour and that X1 enforces by exempting placeholders only on judgement flags.
- Why detection failed earlier: the admissibility unit tests exercise placeholder forms only on hand-built `release` strings and the builder pin test checks only which subcommands the builder names, so no test drives the action the builder actually emits through `placeholders` (`E-014`); X1 judges only open envelopes of its induced runs, the retry form is short-circuited as prose before parsing (`E-009`), and before FC-027 no check recognised a multi-word placeholder at all (`E-013`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | trigger | A state item is blocked awaiting_recovery_task by the recovery controller with no guard, or a retryable class is scheduled for retry | `E-010`, `E-004`, `E-006` | high |
| `C-002` | builder | The builder composes release_cmd with a literal unquoted placeholder on --detail, a flag release defaults and drops nothing without, which eliminates the account that the placeholder is unavoidable | `E-002`, `E-003`, `E-008` | high |
| `C-003` | shell | Run as written, the trailing bracket is parsed as a redirect with no target, the shell rejects the line, and release never executes, independent of any verifier, which eliminates the account that X1 is merely over-strict | `E-007` | high |
| `C-004` | verifier | The action carries a placeholder on a flag outside every exemption set, so X1 judges the non-retry form inadmissible while the retry form escapes because prose is not parsed | `E-008`, `E-009` | high |

## Fix Strategy

- Proposed fix: the `release` action the builder emits, alone and inside the retry-class reclaim prose, must parse as written in a POSIX shell and carry no placeholder that `placeholders` recognises on a non-judgement flag; either omit `--detail` so `release` applies its default, or supply a quoted literal free of angle brackets, since quoted text containing brackets is itself judged a placeholder (`E-013`). Committed resolved envelopes carrying the old text are run evidence and stay as recorded; none is open, so none is read by X1 (`E-011`).
- Alternative options: (a) omit `--detail`: smallest change, but the recorded detail becomes "adapter did not report a result", which misdescribes a non-guard escalation such as aggregation-conflict; (b) supply a quoted, bracket-free detail derived from the failure class: the recorded transition stays accurate, at the cost of one more value the builder must quote correctly; (c) exempt `--detail` in X1: refused at the FC-027 Triage Gate (`E-013`) and leaves the shell failure of `C-003` in place.
- Regression risk: low
- Regression scope: retry-class actions, which embed the same release_cmd string; non-guard aggregation-conflict and dependency-failure envelopes, which return it whole; the builder pin test, which regex-scans the builder source for subcommand names and must still find `release`; X1 and the `executable` guard, which share the `placeholders` definition; the transition and event detail `release` records when invoked from the action, which changes text if a detail is supplied; operator documentation, which shows the same command form (`E-015`).

## Validation Plan

- Verification steps: repeat steps 1 to 5 of the reproduction and expect `placeholders` to return an empty list for both non-guard classes and all three retry classes; repeat step 7 and expect the unedited action admissible against the blocked item; run the emitted action in a POSIX shell against a scratch run whose item is blocked `awaiting_recovery_task` by the recovery controller and expect exit 0 and the release transition recorded; run `verify_recovery.py` and expect X1 and every other check to pass, then run every other verifier.
- Regression tests added: a test that calls the builder itself, for every branch that names a command including the retry reclaim, and asserts `placeholders` returns nothing outside the judgement-flag exemptions; a test that asserts the emitted action has no unquoted angle bracket after shell tokenisation.
- Monitoring signals after release: the X1 result on every `verify_recovery.py` run, expected pass; the count of open envelopes whose clearing action yields a non-exempt placeholder, expected 0, where any value above 0 indicates recurrence.

## Closure

- Resolution summary: None identified. The defect is unresolved at triage; resolution is recorded only from decisions made at the Fix, Verification, and Closure Gates.
- Linked PR and release: None identified.
- Prevention actions: pending; derived from detection failure: drive builder-emitted actions, not hand-built strings, through the admissibility table, and parse the reclaim command embedded in retry prose.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | How do the host's native non-POSIX shells treat the emitted action? Only bash was exercised; running it there would settle whether the shell failure is universal. | no | orchestrator | `C-003` |
| `Q-002` | Does a full verify_recovery.py run currently fail X1, or do its induced scenarios never leave a non-guard release envelope open? Not run here because it writes run directories outside permitted writes; running it would settle whether the X1 failure is live or latent. | no | qa | `C-004` |
| `Q-003` | What is the business cost of an unrunnable recovery command for operators? No impact statement was supplied; needed to confirm the technical-impact severity. | no | product-owner | none |
