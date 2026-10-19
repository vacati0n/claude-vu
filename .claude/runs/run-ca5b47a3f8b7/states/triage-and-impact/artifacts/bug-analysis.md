```yaml
bugAnalysis:
  analysisId: BA-run-ca5b47a3f8b7-triage-01
  defectReference: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
  producedBy: dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:aee763c105fb957aa177c2ed4e1298a9
  contextDigest: sha256:d349d25df9ecf914b11063912c8be2cd
```

## Metadata

- Bug ID: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
- Reporter: independent review raised after the X1 policy-exception repair (FC-024, FC-025), per the supplied report `E-001`
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: a clearing action whose angle-bracket placeholder spans several words, is glued to other text, or is unterminated is judged admissible by the X1 table and accepted by the execution guard, while the same action with a one-word placeholder is rejected (`E-002`, `E-006`).
- Expected behavior: any placeholder that is not one whole argument after a flag the row exempts is inadmissible and refused by the execution guard, with every existing exemption and committed verdict unchanged, per the supplied report `E-001`.
- First observed date: unknown; the supplied report is undated and follows FC-024/FC-025; first reproduced in this run on 2026-10-18.
- Affected environments: known affected: this repository at commit 340a41b on Windows with the repository Python; known unaffected: none established; not observed: CI, other platforms, and a full recovery verification run with induced runs (see `Q-002`).

## Reproduction

- Preconditions: repository checkout at commit 340a41b; working directory is the repository root; a synthetic state whose only work item `execution-planning` is a state item with status leased (repeated with status blocked, blocked_by recovery); the verifier's state loader patched to return that state.
- Steps to reproduce: 1) import the recovery verifier from the runtime directory and patch its state loader to return the synthetic state; 2) judge the release action for `execution-planning` with `--reason <fill in owner name>`, then `--reason <owner>`, then `--reason tool_failure`; 3) build the runtime's own clearing action for an aggregation-conflict item blocked awaiting a recovery task and judge it under leased and blocked states; 4) pass each tokenised action to the execution guard; 5) observe that only the one-word placeholder is rejected; 6) parse the builder's action as written with a shell syntax check.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below; every attempt, including the rejecting control cases, is recorded there.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Report states the multi-word placeholder is admissible, no committed or induced envelope carries one, and only a future builder change would expose it (hypothesis H) | supplied defect-report, digest sha256:aee763c105fb957aa177c2ed4e1298a9 | low |
| `E-002` | Three runs, identical each time: `<fill in owner name>` admissible, `<owner>` inadmissible as placeholder, `tool_failure` admissible | host reproduction script repro.py, run three times in this run | high |
| `E-003` | Clearing-action tokenisation splits the first line of the action with shlex in POSIX mode, so whitespace inside angle brackets separates arguments | read of runtime/verify_recovery.py, runtime_command | high |
| `E-004` | Both guards detect a placeholder only as one argv element that starts with `<` and ends with `>`; the admissibility table additionally exempts an element after a row-exempt flag | read of runtime/verify_recovery.py, clearing_action_admissible and executable | high |
| `E-005` | The runtime's own builder emits `release ... --reason tool_failure --detail <what happened>` for an aggregation-conflict item; it tokenises to `<what`, `happened>`, is admissible under leased and blocked states, and the execution guard returns it unchanged | analyst probe calling the builder and both guards, scratch builder.py | high |
| `E-006` | `<owner>x`, `x<owner>`, unterminated `<owner`, and `--rationale <fill in text>` on release are each admissible and accepted by the execution guard | same analyst probe, varying one placeholder form at a time | high |
| `E-007` | The builder's release prescription embeds the unquoted literal `--detail <what happened>`; it is returned bare on the awaiting-recovery-task path and appended to every retry-class prose action; release's `--detail` has a runtime default | read of runtime/framework_runtime.py, clearing_action and the release argument parser | high |
| `E-008` | The builder's action as written fails a shell parse with a syntax error near newline, exit 2, so it cannot run as written | shell parse-only check (bash -n) of the emitted action | high |
| `E-009` | 247 committed envelopes: 17 open, all admissible; 118 inadmissible, all resolved; 0 errors; output identical to the host baseline | host scan script scan.py rerun in this run, compared with before.json | high |
| `E-010` | 120 committed command actions: whole placeholders are only `<who>`, `<role>`, `<text>` after exempt flags; split placeholders occur only in two resolved run-4c51600606df envelopes (`--detail <what happened>`), both already inadmissible for state reasons | analyst token scan over every committed recovery ledger | high |
| `E-011` | 23 admissibility unit tests pass; confirmed by search that none uses a multi-word, glued, or unterminated placeholder | unittest run of tests/test_clearing_action_admissibility.py, plus grep of that file | high |
| `E-012` | The latest committed recovery verification report records runtime 0.4.0, so it cannot show X1's result under the current runtime | read of reports/recovery-verification-2026-08-18.json | medium |

## Impact Assessment

- User impact: an operator handed the builder's awaiting-recovery-task release prescription receives a command that a shell rejects as written (`E-008`); the X1 proof that every emitted action runs as written passes over it (`E-005`).
- Business impact: no business impact statement was supplied; severity rests on technical impact alone (`Q-003`).
- Technical impact: X1 and the execution guard return a wrong verdict for every split, glued, or unterminated placeholder (`E-002`, `E-006`); no committed open envelope's verdict is wrong today (`E-009`); no state, gate, or data mutation follows from the verdict; severity medium, a secondary verification path giving wrong results with an acceptable manual workaround.
- Blast radius: recovery verification harness (X1 table over every open envelope and the scenario-D execution guard, via one shared predicate); runtime failure-envelope builder (release prescription and retry-class reclaim suffix, plus status surfaces that print recorded actions); committed run evidence (two resolved run-4c51600606df envelopes persist the split form); admissibility unit tests that pin the current predicate.

## Root Cause Analysis

- Root cause statement: the placeholder notation is free text in angle brackets that may contain whitespace and is emitted unquoted, while both guards recognise a placeholder only as one post-tokenisation argument starting with `<` and ending with `>`, so builder and verifier share no single definition of a placeholder and any split, glued, or unterminated form escapes detection.
- Why detection failed earlier: the 23 unit tests exercise only one-word whole-argument placeholders (`E-011`); X1 judges only open envelopes and the only committed carriers are resolved (`E-009`, `E-010`); the builder pin test checks that each subcommand has a row, not that emitted placeholders are single arguments; no check parses an emitted action as a shell would (`E-008`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | builder emission | the current builder already emits an unquoted multi-word placeholder on its release path, overturning hypothesis H that only a future change would | `E-005`, `E-007`, `E-010` | high |
| `C-002` | tokenisation | POSIX splitting yields `<what` and `happened>`; splitting is correct shell semantics, not the fault, since a shell rejects the same text | `E-003`, `E-005`, `E-008` | high |
| `C-003` | detection contract | the predicate assumes a placeholder survives as one whole argument, so split, glued, and unterminated forms present no matching element | `E-004`, `E-006` | high |
| `C-004` | admissibility verdict | with no placeholder found, the release row's state check alone decides and returns admissible | `E-002`, `E-005` | high |
| `C-005` | execution guard | the execution guard applies the same predicate and passes an argv that cannot run as written | `E-004`, `E-005`, `E-008` | high |

## Fix Strategy

- Proposed fix: one placeholder definition, shared by both guards, must recognise any angle-bracket marker in the action as written, whether multi-word, glued, or unterminated, and exempt only a placeholder forming one whole argument after a row-exempt flag; every action the builder emits must then be either runnable as written or exempt, conditional on `Q-001`; the two committed run-4c51600606df envelopes stay unedited, keeping their inadmissible verdict with a changed reason.
- Alternative options: (a) correct only the verifier and let X1 surface the builder's release prescription wherever it is open, deferring the builder change; (b) reject any `<` or `>` in any argument outside an exempt whole argument, simpler but also rejecting quoted multi-word placeholders after exempt flags; (c) exempt `--detail` on release, which widens the table and contradicts X1's runnable-as-written purpose given the runtime default (`E-007`).
- Regression risk: medium
- Regression scope: X1 verdicts on all open envelopes via the shared predicate; scenario-D rollback executions via the execution guard; builder output for gate, rollback, and policy-exception exemptions via the exempt-flag rule; retry-class prose and release prescriptions via the builder's release literal; admissibility unit tests via the pinned predicate; committed-envelope verdict baseline via the scan comparison.

## Validation Plan

- Verification steps: rerun the reproduction and the builder probe expecting multi-word, glued, and unterminated placeholders inadmissible and refused by the execution guard, one-word non-exempt placeholders still rejected, and exempt `<who>`, `<role>`, `<text>` still admissible; confirm every builder branch yields an action that parses in a shell or is exempt; rerun the scan and compare each envelope's boolean verdict with the baseline; run the full recovery verification to a full pass.
- Regression tests added: in the admissibility test module, inadmissible cases for multi-word, glued prefix and suffix, unterminated, and one-word placeholders, an admissible valid action, execution-guard refusals for the same forms, and a builder pin asserting every emitted placeholder is one whole argument after an exempt flag.
- Monitoring signals after release: the X1 detail line and the per-envelope boolean verdicts against the committed baseline; any open envelope carrying a `<` outside an exempt whole argument indicates recurrence.

## Closure

- Resolution summary: None identified. Pending the Triage Gate decision by tech-lead and the downstream phases.
- Linked PR and release: None identified.
- Prevention actions: a single placeholder definition shared by the builder pin test and the verifier, and a test that parses every builder-emitted action as a shell would.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Is release `--detail` free text the builder must fill (it has a runtime default) or a human-judgement flag the table should exempt? Once detection is corrected the builder's own release prescription becomes inadmissible; a contract decision resolves it. | yes | architect | `C-001`, `C-005` |
| `Q-002` | Does any induced X1 run leave an open envelope on the bare release path? Not run here: the full recovery verification writes and removes injected runs, outside this phase's permitted writes, and the latest committed report predates the current runtime (`E-012`); a full run resolves it. | no | orchestrator | `C-004` |
| `Q-003` | No business impact statement was supplied; severity rests on technical impact alone. A supplied statement would confirm or move it. | no | product-owner | none |
