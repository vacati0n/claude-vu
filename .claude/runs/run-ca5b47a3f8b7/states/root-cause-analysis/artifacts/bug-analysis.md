```yaml
bugAnalysis:
  analysisId: BA-run-ca5b47a3f8b7-root-cause-analysis
  defectReference: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
    - type: bug-analysis
      reference: runs/run-ca5b47a3f8b7/states/triage-and-impact/artifacts/bug-analysis.md
    - type: symptom-evidence
      reference: runs/run-ca5b47a3f8b7/state.json
    - type: code-context
      reference: runtime/verify_recovery.py
    - type: code-context
      reference: runtime/framework_runtime.py
    - type: code-context
      reference: tests/test_clearing_action_admissibility.py
  producedBy: dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:aee763c105fb957aa177c2ed4e1298a9
  contextDigest: sha256:a2e10c34bee5ac0f41eda6d9133bfd16
```

## Metadata

- Bug ID: runs/inputs/recovery-x1-multi-word-placeholder-defect-report.md
- Reporter: independent review raised after the X1 policy-exception repair (FC-024, FC-025), per the supplied report `E-001`
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: a clearing action whose angle-bracket placeholder spans several words, is glued to other text, or is unterminated is judged admissible by the X1 table and accepted by the execution guard, while the same action with a one-word placeholder is rejected (`E-002`, `E-006`, `E-014`).
- Expected behavior: any placeholder that is not one whole argument after a row-exempt flag is inadmissible and refused by the execution guard, existing exemptions and committed verdicts unchanged, per the supplied report `E-001` and the Triage Gate conditions `E-013`.
- First observed date: unknown; the supplied report is undated and follows FC-024/FC-025; first reproduced in this run on 2026-10-18 and again in this phase.
- Affected environments: known affected: this repository at commit 340a41b on Windows with the repository Python; known unaffected: none established; not observed: CI and other platforms (see `Q-004`).

## Reproduction

- Preconditions: repository checkout at commit 340a41b; working directory is the repository root; a synthetic state whose only work item `execution-planning` is a state item with status leased (repeated with status blocked, blocked_by recovery); the verifier's state loader patched to return that state.
- Steps to reproduce: 1) import the recovery verifier from the runtime directory and patch its state loader to return the synthetic state; 2) judge the release action for `execution-planning` with `--reason <fill in owner name>`, then `--reason <owner>`, then `--reason tool_failure`; 3) build the runtime's own clearing action for an aggregation-conflict item blocked awaiting a recovery task and judge it under leased and blocked states; 4) pass each tokenised action to the execution guard; 5) observe that only the one-word placeholder is rejected; 6) parse the builder's action as written with a shell syntax check.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below; every attempt, including the rejecting control cases and the counterfactual runs, is recorded there.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Report states the multi-word placeholder is admissible, no committed or induced envelope carries one, and only a future builder change would expose it (hypothesis H) | supplied defect-report, digest sha256:aee763c105fb957aa177c2ed4e1298a9 | low |
| `E-002` | Three runs, identical each time: `<fill in owner name>` admissible, `<owner>` inadmissible as placeholder, `tool_failure` admissible | host reproduction script repro.py, run three times in triage | high |
| `E-003` | Clearing-action tokenisation splits the first line of the action with shlex in POSIX mode, so whitespace inside angle brackets separates arguments | read of runtime/verify_recovery.py, runtime_command | high |
| `E-004` | Both guards detect a placeholder only as one argv element that starts with `<` and ends with `>`; the admissibility table additionally exempts an element after a row-exempt flag | read of runtime/verify_recovery.py, clearing_action_admissible and executable | high |
| `E-005` | The runtime's own builder emits `release ... --reason tool_failure --detail <what happened>` for an aggregation-conflict item; it tokenises to `<what`, `happened>`, is admissible under leased and blocked states, and the execution guard returns it unchanged | analyst probe calling the builder and both guards, scratch builder.py | high |
| `E-006` | `<owner>x`, `x<owner>`, unterminated `<owner`, and `--rationale <fill in text>` on release are each admissible and accepted by the execution guard | same analyst probe, varying one placeholder form at a time | high |
| `E-007` | The builder's release prescription embeds the unquoted literal `--detail <what happened>`; it is returned bare on the awaiting-recovery-task path and appended to every retry-class prose action; release's `--detail` has a runtime default | read of runtime/framework_runtime.py, clearing_action and the release argument parser | high |
| `E-008` | The builder's action as written fails a shell parse with a syntax error near newline, exit 2, so it cannot run as written | shell parse-only check (bash -n) of the emitted action | high |
| `E-009` | 247 committed envelopes: 17 open, all admissible; 118 inadmissible, all resolved; 0 errors; output identical to the host baseline | host scan script scan.py rerun in triage, compared with before.json | high |
| `E-010` | 120 committed command actions: whole placeholders are only `<who>`, `<role>`, `<text>` after exempt flags; split placeholders occur only in two resolved run-4c51600606df envelopes (`--detail <what happened>`), both already inadmissible for state reasons | analyst token scan over every committed recovery ledger | high |
| `E-011` | 23 admissibility unit tests pass; confirmed by search that none uses a multi-word, glued, or unterminated placeholder | unittest run of tests/test_clearing_action_admissibility.py, plus grep of that file | high |
| `E-012` | The latest committed recovery verification report records runtime 0.4.0, so it cannot show X1's result under the current runtime | read of reports/recovery-verification-2026-08-18.json | medium |
| `E-013` | Triage Gate approved by tech-lead: scope is the shared detection plus its unit tests, no `--detail` exemption, builder placeholder left as follow-up, exemptions and committed true/false verdicts kept | read of runs/run-ca5b47a3f8b7/state.json, gate Triage Gate | high |
| `E-014` | Reproduction rerun in this phase at the unchanged worktree gives the same three verdicts as `E-002` | repro.py run in this phase | high |
| `E-015` | With a detection that spans arguments from an opening `<` to its closing `>`, all 247 committed envelopes keep their true/false verdict versus before.json; only the two run-4c51600606df envelopes change reason, now citing `<what happened>` | analyst run of scan.py in the host prototype tree outside the worktree | high |
| `E-016` | The same counterfactual detection proves the recovery verification 74/74, X1 passing over 9 open envelopes across 4 induced runs, matching the host record | analyst run of verify_recovery.py in the prototype tree only; host proto-recovery.txt | high |
| `E-017` | Under that detection, multi-word, glued prefix, glued suffix, unterminated, and builder `<what happened>` forms are inadmissible and refused by the execution guard; the 23 existing tests, including the gate, rollback decider, and policy-exception exemptions, pass | analyst probe and unittest run in the prototype tree | high |

## Impact Assessment

- User impact: an operator handed the builder's awaiting-recovery-task release prescription receives a command that a shell rejects as written (`E-008`); the X1 proof that every emitted action runs as written passes over it (`E-005`).
- Business impact: no business impact statement was supplied; severity rests on technical impact alone (`Q-003`).
- Technical impact: X1 and the execution guard return a wrong verdict for every split, glued, or unterminated placeholder (`E-002`, `E-006`); no committed open envelope verdict is wrong today (`E-009`); no state, gate, or data mutation follows; the security area was triggered by the word token, which here means argv tokens, and no credential or exposure is involved (`E-004`).
- Blast radius: recovery verification harness (X1 table over every open envelope and the scenario-D execution guard, via one shared predicate); runtime failure-envelope builder (release prescription and retry-class reclaim suffix, plus status surfaces that print recorded actions); committed run evidence (two resolved run-4c51600606df envelopes persist the split form); admissibility unit tests that pin the current predicate.

## Root Cause Analysis

- Root cause statement: the placeholder notation is free text in angle brackets that may contain whitespace and is emitted unquoted, while both guards recognise a placeholder only as one post-tokenisation argument starting with `<` and ending with `>`, so builder and verifier share no single definition of a placeholder and any split, glued, or unterminated form escapes detection.
- Why detection failed earlier: the 23 unit tests exercise only one-word whole-argument placeholders (`E-011`); X1 judges only open envelopes and the only committed carriers are resolved (`E-009`, `E-010`); the builder pin test checks that each subcommand has a row, not that emitted placeholders are single arguments; no check parses an emitted action as a shell would (`E-008`).

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | builder emission | the current builder already emits an unquoted multi-word placeholder on its release path, overturning hypothesis H that only a future change would | `E-005`, `E-007`, `E-010` | high |
| `C-002` | tokenisation | POSIX splitting yields `<what` and `happened>`; splitting is correct shell semantics, not the fault, since a shell rejects the same text | `E-003`, `E-005`, `E-008` | high |
| `C-003` | detection contract | the predicate assumes a placeholder survives as one whole argument; hand-written glued and unterminated forms escape too, so the builder is not the sole cause, and a predicate spanning arguments closes every form | `E-004`, `E-006`, `E-017` | high |
| `C-004` | admissibility verdict | with no placeholder found, the release row's state check alone decides and returns admissible | `E-002`, `E-005`, `E-014` | high |
| `C-005` | execution guard | the execution guard applies the same predicate and passes an argv that cannot run as written | `E-004`, `E-005`, `E-008` | high |

## Fix Strategy

- Proposed fix: one placeholder definition, shared by the admissibility table and the execution guard, must treat every argument from an opening `<` to its closing `>` (or to the end when unterminated) as one placeholder, and exempt only a placeholder that is exactly one whole argument after a row-exempt flag; release `--detail` gains no exemption (`E-013`); committed run evidence stays unedited, the two run-4c51600606df envelopes keeping their inadmissible verdict with a changed reason (`E-015`).
- Alternative options: (a) reject any argument containing `<` or `>` outside an exempt whole argument, simpler but reporting fragments rather than the whole placeholder text; (b) also change the builder to stop emitting `--detail <what happened>`, which removes the source but lies outside the approved scope and is held as `Q-001`; (c) exempt `--detail` on release, rejected by the gate and contrary to X1's runnable-as-written purpose (`E-007`, `E-013`).
- Regression risk: medium
- Regression scope: X1 verdicts on all open envelopes via the shared predicate; scenario-D rollback executions via the execution guard; gate, rollback decider, and policy-exception exemptions via the exempt-flag rule; any future open envelope carrying the builder's bare release prescription, which X1 will then correctly reject, via the builder literal; committed-envelope verdict baseline via the scan comparison; admissibility unit tests via the pinned predicate.

## Validation Plan

- Verification steps: rerun the reproduction expecting `<fill in owner name>` inadmissible, `<owner>` inadmissible, `tool_failure` admissible; rerun the builder probe expecting the builder action, glued, and unterminated forms inadmissible and refused by the execution guard; rerun scan.py and confirm every envelope's true/false verdict equals before.json; run the full recovery verification in an isolated copy and the unit tests, expecting 74/74 and all pass.
- Regression tests added: new in tests/test_clearing_action_admissibility.py, each judged inadmissible and refused by executable: test_multi_word_placeholder_is_inadmissible, test_glued_prefix_placeholder_is_inadmissible, test_glued_suffix_placeholder_is_inadmissible, test_unterminated_placeholder_is_inadmissible, test_single_word_placeholder_is_inadmissible; plus test_valid_action_is_admissible; kept unchanged: test_gate_action_keeps_its_exemption, test_emitted_action_leaves_only_the_decider_and_is_admissible, test_emitted_action_with_placeholders_is_admissible.
- Monitoring signals after release: the X1 detail line and the per-envelope true/false verdicts against before.json; any open envelope with a `<` outside an exempt whole argument judged admissible indicates recurrence.

## Closure

- Resolution summary: None identified. Pending fix-implementation, the Fix Gate, and regression validation.
- Linked PR and release: None identified.
- Prevention actions: one placeholder definition shared by both guards and pinned by tests across every placeholder form, and a follow-up so the builder emits only runnable or exempt actions (`Q-001`).

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Follow-up outside the approved scope: the builder's release prescription still emits `--detail <what happened>`, which the corrected detection will reject and a shell cannot parse; a builder change filling or dropping it resolves it. | no | architect | `C-001` |
| `Q-002` | Resolved by this phase and kept so the triage reference resolves: no induced run regresses; under the corrected detection X1 passes over 9 open envelopes and the verification is 74/74 (`E-016`), where the committed report could not show it (`E-012`). | no | orchestrator | `C-004` |
| `Q-003` | No business impact statement was supplied; severity rests on technical impact alone. A supplied statement would confirm or move it. | no | product-owner | none |
| `Q-004` | Behaviour was observed only on this host's checkout; CI and other platforms were not reached. A CI run of the unit tests and recovery verification resolves it. | no | orchestrator | none |
