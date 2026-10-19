```yaml
bugAnalysis:
  analysisId: BA-run-34fbc64712b5-root-cause-analysis
  defectReference: FC-027/O-002
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/release-clearing-action-placeholder-defect-report.md
    - type: bug-analysis
      reference: runs/run-34fbc64712b5/states/triage-and-impact/artifacts/bug-analysis.md
    - type: symptom-evidence
      reference: runs/run-34fbc64712b5/state.json
    - type: code-context
      reference: runtime/framework_runtime.py
    - type: code-context
      reference: runtime/verify_recovery.py
    - type: code-context
      reference: runtime/recovery_policy.py
    - type: code-context
      reference: tests/test_clearing_action_admissibility.py
    - type: code-context
      reference: tests/test_gate_rollback.py
  producedBy: dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:71fa90ad70f8c8ffcafa075848b9659e
  contextDigest: sha256:a2e10c34bee5ac0f41eda6d9133bfd16
```

## Metadata

- Bug ID: FC-027/O-002
- Reporter: the FC-027 change proposal, open item `O-002` (owner architect), raised as the supplied defect report (`E-001`, `E-013`)
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: The `release` command the clearing-action builder emits ends `--detail <what happened>`. `shlex` splits that tail into two arguments, `verify_recovery.placeholders` returns `['<what happened>']`, and bash, PowerShell and cmd.exe each reject the line at parse, so `release` never runs (`E-004`, `E-006`, `E-007`, `E-021`). The same command follows "To reclaim it sooner:" in every retry-class action, and that is the only form any current emitter writes (`E-006`, `E-016`). This phase supersedes the triage artifact (`E-022` records the gate it passed). It keeps every triage identifier and changes two facts on registered evidence. No current emitter reaches the non-retry `release` branch (`E-016`), and X1 currently passes, so the verifier failure is latent rather than live (`E-017`).
- Expected behavior: According to the defect report (`E-001`) and the Triage Gate conditions (`E-022`), the emitted `release` action, both on its own and inside the retry reclaim, should parse as written and carry no placeholder that `placeholders` recognises. X1 should admit it without an exemption, and every verifier should still pass. `release` already defaults `--detail` (`E-003`).
- First observed date: the placeholder has been in the builder since its first committed form, dated 2026-09-04 (`E-012`). It was first recorded as a defect, `O-002` of FC-027, on 2026-10-19 (`E-013`) and is still present at the analysed revision.
- Affected environments: known affected: the runtime at the analysed revision, on every retry-class schedule (output-schema-failure, worker-loss, invocation-transport-failure) and in the non-guard `awaiting_recovery_task` builder branch; the bash, PowerShell and cmd.exe shells (`E-005`, `E-006`, `E-007`, `E-021`). Known unaffected: guard-raised blocks, and the gate, rollback, policy-exception and budget-exhausted branches (`E-002`, `E-005`). Not observed: CI and other operating systems.

## Reproduction

- Preconditions: Python with `runtime/` on the import path at the analysed revision; a state work-item dict with `work_type` state. For the builder steps, a classification from `recovery_policy.classify` for a retryable class with budget left, or for aggregation-conflict or dependency-failure with no guard. For the end-to-end steps, a disposable copy of the framework root and the `tests` directory, because the verifiers and the runtime write run directories.
- Steps to reproduce: (1) Import `framework_runtime`, `recovery_policy`, `verify_recovery` and `shlex`. (2) Build `cls = recovery_policy.classify("aggregation-conflict", attempt=1, attempts_lost=0, max_attempts=3, seed="s")`. (3) Call `framework_runtime.clearing_action("run-x", {"state_id": "triage-and-impact", "work_type": "state", "work_item_id": "x"}, cls, cls.blocked_reason)`. (4) Evaluate `verify_recovery.placeholders(shlex.split(action))` and observe `['<what happened>']`. (5) Repeat for dependency-failure, then for each retryable class using `verify_recovery.runtime_command(action)`. (6) In an empty directory, run `bash -n -c` on the action and observe exit 2; feed the same text to PowerShell's parser only and observe `RedirectionNotSupported`. (7) In the disposable copy, use the verifier helpers `plan`, `dispatch`, `act_as_adapter` with a broken artifact, and `complete` to drive `execution-planning` to `retrying`. Run the embedded reclaim with `--detail` dropped and observe "ALREADY RETRYING ... nothing to reclaim". (8) In the copy, set that item to blocked by the recovery controller with `awaiting_recovery_task`. Run `release` without `--detail`, then with a quoted bracket-free detail, and observe `blocked -> pending` and the recorded detail.
- Reproduction frequency: deterministic
- Evidence: the Evidence Register below, `E-001` to `E-022`.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Reports the unquoted --detail placeholder, its reuse in retry prose, X1 rejection since FC-027, a redirect failure in a POSIX shell, severity medium | supplied defect-report, digest sha256:71fa90ad70f8c8ffcafa075848b9659e | low |
| `E-002` | release_cmd is composed once with a literal unquoted --detail placeholder, returned inside retry prose before any guard test and whole for a non-guard awaiting_recovery_task block; gate and policy-exception branches quote values and keep placeholders only on judgement flags | source read of runtime/framework_runtime.py clearing_action, lines 2038-2092, this phase | high |
| `E-003` | release declares --detail optional with default "adapter did not report a result"; on a retrying item cmd_release prints ALREADY RETRYING and returns 0; on a controller-blocked item it records the detail in the resolution, transition, and event | source read of runtime/framework_runtime.py line 6115 and cmd_release lines 3372-3460, this phase | high |
| `E-004` | aggregation-conflict and dependency-failure without a guard return the release command; placeholders yields one entry, the whole bracketed text; 2 of 2 classes | command: scratch probe over every policy class with and without guard G3, this phase | high |
| `E-005` | With guard G3-PREDECESSOR the same non-retry classes yield prose naming no command; gate-approval, capability, context, input classes name no release | command: same scratch probe, guard rows | high |
| `E-006` | output-schema-failure, worker-loss, invocation-transport-failure start "none required" and the embedded command yields the same placeholder, with or without a guard; 3 of 3 classes | command: same scratch probe, runtime_command then placeholders | high |
| `E-007` | bash -n on the emitted action reports a syntax error near newline, exit 2, in an empty directory; nothing executes | command: bash -n -c on the emitted action, this phase | high |
| `E-008` | clearing_action_admissible judged the non-retry action inadmissible naming the placeholder, the retry action admissible as nothing required, and the action without --detail admissible against a controller-blocked item | command: in-memory admissibility script, triage phase of this run | high |
| `E-009` | release exemption set is empty; only gate, rollback, and an awaiting_policy_exception item exempt judgement flags; the "none required" prefix returns admissible before any parsing; the verifier itself drives release with a filled quoted detail | source read of runtime/verify_recovery.py lines 506 and 581-755, this phase | high |
| `E-010` | Non-retryable classes whose blocked reason is awaiting_recovery_task are aggregation-conflict, dependency-failure, gate-rejection; gate-rejection routes to rollback | source read of runtime/recovery_policy.py FAILURE_POLICIES and classify, this phase | high |
| `E-011` | 33 committed ledger entries in 14 runs carry the placeholder: 25 output-schema-failure and 6 worker-loss retry form, 2 pre-rollback gate-rejection release form; confirmed 0 open | command: read-only scan of runs/run-*/recovery-ledger.json, this phase | high |
| `E-012` | The placeholder string entered the builder in the commit dated 2026-09-04 and has not changed since | command: git log -S over runtime/framework_runtime.py | high |
| `E-013` | FC-027 records O-002 open (owner architect), the builder left unchanged, a --detail exemption refused, and quoted text holding angle brackets now judged a placeholder (O-001) | read of proposals/framework-change-proposal-FC-027.md lines 38, 97, 125, 149-150 | medium |
| `E-014` | Placeholder cases use hand-built release strings; the builder pin test scans builder source for subcommand names only; test_gate_rollback carries the old text only as stale persisted fixtures; 64 tests pass in a copy | read of both test modules; unittest run in a disposable copy | high |
| `E-015` | Operator documentation shows release with a quoted "<what happened>" detail, a form placeholders also recognises | read of runtime/README.md line 107 | high |
| `E-016` | No current emitter reaches the non-retry release branch: aggregation-conflict is raised nowhere; dependency-failure is raised only by G3 with guard set and by G5 with reason awaiting_dependency_output; validation yields only output-schema-failure or policy-failure | source read of every classify and envelope call site in runtime/framework_runtime.py and recovery_policy.py | high |
| `E-017` | verify_recovery.py passes 74 of 74; X1 passes over 9 open envelopes across 4 induced runs; confirmed no induced run leaves a release-form envelope open | command: verify_recovery.py in a disposable copy of the framework root and tests | high |
| `E-018` | An induced output-schema-failure leaves the item retrying; its reclaim with --detail dropped exits 0 printing ALREADY RETRYING, nothing to reclaim; the item stays retrying at attempt 1 | command: reclaim probe in the disposable copy | high |
| `E-019` | On an item blocked awaiting_recovery_task by the recovery controller, release without --detail moves it blocked to pending and records "adapter did not report a result"; with a quoted bracket-free detail it records that text | command: release probe in the disposable copy; block set directly in the copy as the precondition | high |
| `E-020` | placeholders is empty for the command without --detail, with a quoted bracket-free detail, and for retry prose embedding either; a quoted "<what happened>" is still flagged | command: in-memory placeholders over candidate forms, this phase | high |
| `E-021` | PowerShell's parser rejects the emitted form with RedirectionNotSupported and accepts both fixed forms; cmd.exe rejects it with a syntax error, exit 1; a Python-launched bash resolved to a non-functional launcher stub and its results were discarded | command: PowerShell ParseInput only; cmd.exe with echo in place of the runtime, empty directory | high |
| `E-022` | Triage Gate approved by tech-lead with conditions: change only clearing_action (README optional), no X1 exemption, committed run evidence untouched, builder-driven tests covering the retry reclaim, every verifier passing | read of runs/run-34fbc64712b5/state.json, gate Triage Gate | high |

## Impact Assessment

- User impact: An operator who copies a prescribed reclaim, or the non-guard clearing action, has the shell refuse it at parse and must edit the command by hand before `release` will run (`E-006`, `E-007`, `E-021`). For the retry form, which is the only one written today, the edited command then reclaims nothing (`E-018`, `Q-004`). The number of operators affected depends on how often retries happen, which was not measured here.
- Business impact: not supplied. No business impact statement accompanied this defect, so severity rests on technical impact alone and `Q-003` routes the question. The reporter's severity in `E-001` is recorded as context only and did not set it.
- Technical impact: An emitted recovery command fails as written on every shell exercised. This is a secondary path with an acceptable workaround: drop `--detail`, which `release` defaults (`E-003`, `E-019`). No state transition, ledger write, or `release` semantics changes, because the command never runs (`E-007`). X1 would refuse an open non-retry envelope, but no emitter writes one today, and the retry form is accepted as prose before parsing (`E-009`, `E-016`, `E-017`).
- Blast radius: the clearing-action builder, both where it returns the command and where it embeds it (`E-002`); the failure envelope files and run recovery ledgers, which hold 33 persisted entries with the placeholder, all resolved and none open (`E-011`); the operator shell boundary in bash, PowerShell and cmd.exe (`E-007`, `E-021`); the recovery verifier's X1 check and its execution guard, which share the `placeholders` definition, a latent failure today (`E-009`, `E-017`); operator documentation that shows a quoted placeholder form (`E-015`). The non-guard non-retry branch is reachable only through a direct builder call (`E-016`). Not reached: guard-raised blocks and the gate, rollback, policy-exception and budget-exhausted branches (`E-002`, `E-005`, `E-010`).

## Root Cause Analysis

- Root cause statement: The clearing-action builder treats `release --detail` as an operator-fill slot and emits it as an unquoted multi-word angle-bracket placeholder, although `release` defaults the flag and needs no human judgement there; as a result, the one shared `release` command it emits breaks the runs-as-written contract that its own gate and policy-exception branches honour and that X1 enforces.
- Why detection failed earlier: no check sends the builder's emitted `release` command through `placeholders` or a shell. The admissibility unit tests use hand-built `release` strings, and the builder pin test only scans source for subcommand names (`E-014`). X1 is the only check that judges emitted actions, and it cannot see this one: no emitter reaches the non-retry branch, and the retry form is accepted on its `none required` prefix before parsing (`E-009`, `E-016`, `E-017`). Before FC-027, no check recognised a multi-word placeholder at all (`E-013`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | trigger | A retryable class with budget left moves the item to retrying and the builder writes its action; no current emitter reaches the non-retry branch, so retry prose is the only live route to the command | `E-016`, `E-018`, `E-011` | high |
| `C-002` | builder | The builder fills --detail with an unquoted multi-word bracket placeholder in one shared command although release runs on its default, unlike the judgement-only placeholders of the gate and policy-exception branches, which eliminates the account that the placeholder is unavoidable | `E-002`, `E-003`, `E-019` | high |
| `C-003` | shell | As written, bash, PowerShell, and cmd.exe each reject the line at parse and release never runs, while the fixed forms parse, which eliminates the account that X1 is merely over-strict | `E-007`, `E-021` | high |
| `C-004` | verifier | The emitted action violates the runs-as-written contract X1 enforces, a placeholder on a flag with no exemption, and quoting the placeholder does not cure it; X1 passes today only because the branch is unreachable and retry prose is not parsed | `E-009`, `E-020`, `E-017` | high |

## Fix Strategy

- Proposed fix: The builder's `release` command, both where it is the whole action and where the retry prose embeds it, must parse as written in bash, PowerShell and cmd.exe, and must leave `placeholders` empty, without any X1 exemption (`E-020`, `E-021`, `E-022`). Recommended: give `--detail` a fixed literal with no angle brackets that truthfully describes an operator clearing the condition, quoted the same way the gate and policy-exception branches already quote their arguments, so the detail `release` records stays accurate (`E-002`, `E-019`). The `none required` prefix and the `release` subcommand name in the builder must not change (`E-009`, `E-014`). The 33 committed resolved entries are run evidence and stay as recorded; none is open (`E-011`, `E-022`).
- Alternative options: (a) Drop `--detail`. This is the smallest change and also parses with no placeholder, but the recorded detail becomes "adapter did not report a result", which misdescribes an operator clearing a non-guard block; X1 admits that form (`E-008`, `E-019`). (b) Quote the existing placeholder. It parses in a shell, but `placeholders` still flags it and the literal bracket text would be recorded, so it is eliminated (`E-013`, `E-020`). (c) Exempt `--detail` in X1. This was refused at both Triage Gates and leaves the shell failure of `C-003` in place (`E-013`, `E-022`).
- Regression risk: low
- Regression scope: retry-class envelopes, which embed the shared command, and X1, which treats them as prose only while the `none required` prefix holds (`E-006`, `E-009`); the non-guard `awaiting_recovery_task` branch, which returns the command whole (`E-002`); the builder pin test, which scans builder source for `release` (`E-014`); X1 and the execution guard, which share `placeholders` (`E-009`); the detail `release` records in the transition, the envelope resolution and the escalation event when the action runs (`E-003`, `E-019`); the stale fixtures in the rollback tests, which deliberately keep the old text (`E-014`); operator documentation, which shows a quoted placeholder form (`E-015`).

## Validation Plan

- Verification steps: Repeat reproduction steps 1 to 5 and expect `placeholders` to be empty for both non-guard classes and all three retry classes. Repeat step 6 and expect bash exit 0 and no PowerShell parse error. Repeat step 8 with the unedited non-retry action and expect `blocked -> pending`, with the new literal recorded as the detail. In a disposable copy of the framework root and `tests`, run `verify_recovery.py` and `verify_multi_phase.py`, expecting every check including X1 to pass, then run every other verifier and the full unit suite.
- Regression tests added: in a new module, `tests/test_release_clearing_action.py`, driven only by builder output and never by hand-built strings: (1) for aggregation-conflict and dependency-failure without a guard, the action's subcommand is `release` and `verify_recovery.placeholders(shlex.split(action))` is empty; (2) for output-schema-failure, worker-loss and invocation-transport-failure, the action starts `none required` and `placeholders(runtime_command(action))` is empty, which covers the retry reclaim; (3) the reclaim's argv equals the non-retry action's argv for the same item; (4) no shell-tokenised argument of either form contains an angle bracket; (5) `clearing_action_admissible` admits the unedited non-retry action against an item the recovery controller blocked, with run-state loading patched in memory; (6) with guard G3-PREDECESSOR the non-retry classes still return prose that names no command. `tests/test_clearing_action_admissibility.py` and the stale fixtures in `tests/test_gate_rollback.py` stay untouched.
- Monitoring signals after release: the X1 result on every `verify_recovery.py` run, expected pass; among envelopes written after the fix, the count whose clearing action yields a non-exempt placeholder, expected 0, where any value above 0 indicates recurrence.

## Closure

- Resolution summary: None identified. The defect is unresolved at root cause analysis. A resolution is recorded only from decisions made at the Fix, Verification, and Closure Gates.
- Linked PR and release: None identified.
- Prevention actions: pending. From the detection failure: send the action each builder branch emits, rather than hand-built strings, through `placeholders` and a parse check, and parse the reclaim command embedded in retry prose.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-004` | Separate defect, outside this fix: the retry prose offers a reclaim that release refuses for a retrying item (`E-018`); decide whether the prose stops offering it or release honours it. | no | architect | `C-001` |
| `Q-005` | Is the non-guard non-retry release branch meant to be reachable? aggregation-conflict has a policy row but no raiser, and dependency-failure arrives guarded or with an overriding reason (`E-016`). | no | architect | `C-001` |
| `Q-001` | Resolved by this phase and kept so the triage reference resolves: PowerShell and cmd.exe reject the emitted form as bash does, and accept the fixed forms (`E-021`). | no | orchestrator | `C-003` |
| `Q-002` | Resolved by this phase and kept so the triage reference resolves: X1 passes today, so the verifier failure is latent; no emitter leaves a non-retry release envelope open (`E-016`, `E-017`). | no | qa | `C-004` |
| `Q-003` | What is the business cost of an unrunnable recovery command for operators? No impact statement was supplied; one would confirm or move the technical-impact severity. | no | product-owner | none |
