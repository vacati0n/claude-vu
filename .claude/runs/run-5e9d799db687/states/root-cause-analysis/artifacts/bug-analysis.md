```yaml
bugAnalysis:
  analysisId: BA-run-5e9d799db687-root-cause-analysis
  defectReference: runs/inputs/recovery-x1-missing-regression-tests-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/recovery-x1-missing-regression-tests-defect-report.md
    - type: reproduction-context
      reference: runs/run-5e9d799db687/states/triage-and-impact/artifacts/bug-analysis.md
    - type: regression-targets
      reference: runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md
    - type: implementation-report
      reference: runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md
    - type: validation-report
      reference: runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md
    - type: environment-context
      reference: runs/run-e7bf0d73027a/state.json
    - type: code-context
      reference: tests/test_clearing_action_admissibility.py
    - type: code-context
      reference: runtime/verify_recovery.py
    - type: code-context
      reference: runtime/framework_runtime.py
    - type: code-context
      reference: runtime/recovery_policy.py
    - type: code-context
      reference: tests/test_gate_rollback.py
    - type: code-context
      reference: tests/test_model_tier.py
    - type: code-context
      reference: tests/test_knowledge.py
    - type: architecture-context
      reference: config/task-queue.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: medium
  reproducibility: deterministic
  inputDigest: sha256:7412953e071deb829255cfefaf1cc9e5
  contextDigest: sha256:5d58ca9209219c5223f02f3a6d5f8c67
```

## Metadata

- Bug ID: runs/inputs/recovery-x1-missing-regression-tests-defect-report.md
- Reporter: omn-qa (defects DF-001 and DF-002 of run-e7bf0d73027a), carried by the Verification Gate rejection of omn-dev-2-reviewer and written up in the supplied defect report
- Severity: medium
- Status: provisional

## Symptom Summary

- Observed behavior: the regression suite delivered with the X1 policy-exception fix of run-e7bf0d73027a holds no automated case that executes the policy-exception runtime command and no unchanged-rollback admissibility case, so QA scored AC-009 and AC-007 not-met and the Verification Gate was rejected (`E-002`, `E-003`, `E-004`, `E-013`, `E-014`). DF-001 and DF-002 are analysed as one defect: one symptom, one origin in the same Validation Plan, one rejection.
- Expected behavior: per the root-cause Validation Plan of run-e7bf0d73027a (`E-010`) and the supplied report (`E-001`), the test suite carries an end-to-end case that executes the emitted policy-exception action with only role, decider and rationale filled and shows the block cleared, the envelope resolved and the guards applied, plus an unchanged-rollback case beside the gate-exemption case, with the recovery verifier still at 74 checks.
- First observed date: 2026-10-18T03:52:13Z, the Verification Gate rejection of run-e7bf0d73027a (`E-014`); the gap has existed since fix-implementation of that run completed; ongoing.
- Affected environments: known affected: this worktree at HEAD 097e8f4 with the uncommitted run-e7bf0d73027a fix, Windows, Python 3.14.0 (`E-002`, `E-009`); known unaffected: none; not observed: the CI ubuntu and windows runners and any other Python version.

## Reproduction

- Preconditions: repository root of this worktree at HEAD 097e8f4 with the run-e7bf0d73027a working-tree changes present (modified runtime/verify_recovery.py and its bundled copy, untracked tests/test_clearing_action_admissibility.py) (`E-007`, `E-009`); Python 3.14.0; TEMP and TMP pointed at a drive with free space; no other precondition varies the outcome, since the defect is the absence of tests.
- Steps to reproduce: 1. from the repository root run python -m unittest tests.test_clearing_action_admissibility -v and observe 16 tests, OK, none named for rollback; 2. run grep -rn "cmd_policy_exception" tests/ and observe no match (exit 1); 3. run grep -rln "policy-exception" tests/ and observe only the admissibility module, which builds or inspects action strings and never executes one; 4. run grep -rln "clearing_action_admissible" tests/ and observe only the admissibility module; 5. run grep -n "policy-exception" .claude/runtime/verify_recovery.py and observe that no verifier scenario executes the command.
- Reproduction frequency: deterministic
- Evidence: see the Evidence Register below, `E-001` to `E-026`.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | Defect report states DF-001 and DF-002 as always-present medium gaps, expected behaviour, two reproduction steps, and blast radius tests only | supplied defect-report, digest sha256:7412953e071deb829255cfefaf1cc9e5 | low |
| `E-002` | Executed: the admissibility module runs 16 tests, OK; the names include test_gate_action_keeps_its_exemption and no rollback case | python -m unittest tests.test_clearing_action_admissibility, run in triage and again in this phase | high |
| `E-003` | Executed: no file under tests/ names cmd_policy_exception (exit 1); only the admissibility module names policy-exception and it contains no subprocess call or runtime main invocation (confirmed absence) | grep -rn over tests/, run in triage and again in this phase | high |
| `E-004` | Executed: no test method in the admissibility module names rollback (exit 1, confirmed absence); its only rollback reference is the builder pin reading rollback_clearing_action source | grep of tests/test_clearing_action_admissibility.py, run in this phase | high |
| `E-005` | Executed: clearing_action_admissible is reached by exactly one module under tests/ | grep -rln clearing_action_admissible tests/, run in this phase | high |
| `E-006` | Read: verify_recovery.py names policy-exception only at the scenario C envelope assertion and the admissibility rows; D4, D23, D27, X1 call check_clearing_actions; the executable helper fills only the --decided-by placeholder | .claude/runtime/verify_recovery.py, read in this phase | high |
| `E-007` | Read: the working-tree change to verify_recovery.py adds the policy-exception exemption predicate and row and leaves the rollback row and its exemption set {--decided-by} unchanged | git diff of .claude/runtime/verify_recovery.py (37 insertions, 2 deletions), run in this phase | high |
| `E-008` | Executed: the bundled verify_recovery.py is byte-identical to the runtime copy | cmp of .claude/runtime/verify_recovery.py and omn_agent/_bundled_payload/runtime/verify_recovery.py, run in this phase | high |
| `E-009` | Executed: HEAD is 097e8f4; the admissibility module is untracked and verify_recovery.py is modified uncommitted; interpreter is Python 3.14.0 | git rev-parse, git status, python --version, run in this phase | high |
| `E-010` | Read: the root-cause Validation Plan of run-e7bf0d73027a lists unchanged gate and rollback cases and an end-to-end scenario executing the action with role, decider and rationale filled | runs/run-e7bf0d73027a/states/root-cause-analysis/artifacts/bug-analysis.md, Validation Plan, read in this phase | high |
| `E-011` | Read: the implementation report records deviation V-001 (no end-to-end scenario, because a verifier check changes the 74 total and the verifier helper allows only --decided-by as placeholder) and records no deviation for the absent rollback case | runs/run-e7bf0d73027a/states/fix-implementation/artifacts/implementation-report.md, read in this phase | high |
| `E-012` | Read: the Fix Gate was approved by omn-dev-2-reviewer with V-001 and the unpinned rollback row carried as conditions rather than required | runs/run-e7bf0d73027a/state.json, Fix Gate rationale, read in this phase | high |
| `E-013` | Read: QA scored AC-007 and AC-009 not-met, opened DF-001 and DF-002 medium, returned fail, and listed as untested the filled-role guard against a non-empty envelope owner list, noting the induced envelope lists none | runs/run-e7bf0d73027a/states/regression-validation/artifacts/validation-report.md, read in this phase | high |
| `E-014` | Read: Verification Gate rejected by omn-dev-2-reviewer at 2026-10-18T03:52:13Z naming DF-001 and DF-002, no risk accepted | runs/run-e7bf0d73027a/state.json, read in this phase | high |
| `E-015` | Read: cmd_policy_exception replays on a terminal item, refuses a non-blocked item and any other blocked_reason, refuses a role the envelope does not list only where it lists any, and refuses the producer's own role and its aliases | .claude/runtime/framework_runtime.py cmd_policy_exception and producer_aliases, read in this phase | high |
| `E-016` | Reported, not executed in triage: the emitted action exits 0, unblocks the item, resolves the envelope; verifier 74/74; full suite green apart from test_demo_capture | run-e7bf0d73027a root-cause, implementation, QA and Fix Gate records | low |
| `E-017` | Executed: verify_recovery.py reports 74/74 RECOVERY PROVEN with C4, D4, D23, D27, X1 passing over 9 open envelopes in 47 s; it removed its injected runs and inputs, and git status was identical before and after, so run-f94564cb61ce was not rewritten | python .claude/runtime/verify_recovery.py and git status --porcelain diff, run in this phase | high |
| `E-018` | Executed in an isolated copy of .claude/ (runs, __pycache__, worktrees excluded) under D:\rvw-tmp-5df08e: plan implement, dispatch execution-planning, write the accepted plan of run-c5a8d50d3238 re-stamped with the envelope digests and declare memory/architecture.md; complete exits 1; the item is blocked awaiting_policy_exception; the envelope is open, decision type policy-exception, owner_roles empty, owner_agent_id planner; the clearing action, identical in the recovery ledger, is the policy-exception command with exactly the placeholders role, who, text | scratch driver outside the repository invoking the copied framework_runtime.py with cwd at the copy root, run in this phase | high |
| `E-019` | Executed: the emitted action with the producer role planner exits 2 with policy-failure naming the producer; item still blocked, work items unchanged, no policy-exception.json written | same isolated tree, run in this phase | high |
| `E-020` | Executed: the emitted action with a non-producer role exits 0; item pending with blocked_reason cleared and one policy_exceptions record; envelope and ledger entry resolved by the named decider; policy-exception.json granted over memory/architecture.md; one escalation_resolved event; a second execution exits 2 as not blocked; repository git status unchanged | same isolated tree, run in this phase | high |
| `E-021` | Executed and read: because the runtime emits owner_roles empty for this block (apply_classified_failure passes none, emit_guard_envelope lists roles only for gates), a role name that no registry defines was accepted in `E-020`; with owner_roles rewritten to omn-tech-lead in the isolated envelope, omn-qa and planner are refused as not a recorded owner (exit 2, no write) and omn-tech-lead clears; no governance file names who may decide a policy exception | isolated tree run, framework_runtime.py apply_classified_failure and emit_guard_envelope, config/task-queue.md, read in this phase | high |
| `E-022` | Executed: the rollback row judged against a temp state store gives identical verdicts with the HEAD and the working-tree verify_recovery.py: the emitted rollback action (role filled, --decided-by placeholder) and a filled decider admissible; a role or rationale placeholder inadmissible by placeholder reason; producer and unlisted roles inadmissible by role reason; an unrejected gate inadmissible | scratch probe importing each verify_recovery.py copy with RUNS patched to a temp directory, run in this phase | high |
| `E-023` | Executed: widening the rollback exemption to role, decider and rationale makes a rationale placeholder admissible and turns the role-placeholder refusal into a role-guard refusal; emptying the exemption makes the emitted rollback action inadmissible | same probe against two mutated copies in D:\rvw-tmp-5df08e, run in this phase | high |
| `E-024` | Executed: with the producer guard disabled the producer role exits 0 and clears; with envelope resolution removed the item returns to pending while envelope and ledger stay open; with the builder emitting --role the emitted action carries no --owner-role and cannot be filled as written | isolated e2e driver against three mutated runtime copies in D:\rvw-tmp-5df08e, run in this phase | high |
| `E-025` | Read: test_model_tier and test_knowledge copy .claude/ with runs, __pycache__ and worktrees ignored into a temp directory and run the real CLI with cwd at the copy; FW_PREFIX is derived from the tree's directory name, so the emitted action's relative path resolves there; test_gate_rollback builds temp state stores with a rejected gate; scenario C of verify_recovery.py induces the block by declaring memory/architecture.md outside permitted writes | tests/test_model_tier.py, tests/test_knowledge.py, tests/test_gate_rollback.py, verify_recovery.py scenario_c, framework_runtime.py FW_PREFIX, read in this phase | high |
| `E-026` | Executed: the full suite ran 787 tests in 992 s with 1 failure and 2 errors, all in test_demo_capture.EndToEndEditTestCase; repository git status unchanged; some suite cases created transient git repositories under the user temp directory on C: regardless of TEMP | python -m unittest discover -s tests, the CI command, run in this phase | high |

## Impact Assessment

- User impact: framework contributors and operators of run-e7bf0d73027a; that run cannot reach closure while the Verification Gate stands rejected (`E-014`); no runtime user sees wrong behaviour in the covered paths, now confirmed first-hand (`E-017`, `E-019`, `E-020`).
- Business impact: no business impact statement was supplied; severity rests on technical impact alone, and the question is routed to omn-product-owner as `Q-003`.
- Technical impact: a regression in the policy-exception command's guards, its state transition, its envelope resolution, or the builder's emitted arguments (`E-024`), or in the rollback row's placeholder exemption (`E-023`), would pass every test under tests/ undetected (`E-003`, `E-004`, `E-005`); the rollback row stays reachable only through verifier checks D4, D23, D27 (`E-006`). Severity medium: a secondary path (regression detection) is absent and a workflow path (closure of run-e7bf0d73027a) is blocked, with acceptable workarounds in the verifier checks and a formal risk decision. Separately, the listed-role guard is unreachable for runtime-emitted policy-exception envelopes, so any non-producer role name clears the block (`E-021`); that is a separate security-relevant contract gap, not part of this defect, routed as `Q-005`.
- Blast radius: the repository test suite (admissibility module); the runtime policy-exception command surface left without execution coverage; the verifier admissibility table's rollback and policy-exception rows and their bundled-payload copy (`E-006`, `E-008`); the run record and closure of run-e7bf0d73027a; the uncommitted working-tree state the new tests must build on (`E-009`); no persisted bad data was written, since the rejected gate in run-e7bf0d73027a is a correct record.

## Root Cause Analysis

- Root cause statement: no step between the root-cause Validation Plan and the Fix Gate traced each planned regression case to a delivered test, so the unchanged-rollback case was dropped without being recorded and the end-to-end case was deferred on a verifier 74-check constraint that a case in the test suite does not touch, and the Fix Gate carried both gaps forward instead of holding them.
- Why detection failed earlier: the implementation report's deviation table, the one record mapping plan items to delivered work, captured V-001 but not the rollback omission (`E-011`), and the Fix Gate review saw both gaps and carried them as conditions rather than rejecting (`E-012`); no check observed in this run requires item-by-item Validation Plan tracing before the Fix Gate, and whether one should exist is `Q-001`.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Plan sets two targets | The root-cause Validation Plan required an unchanged-rollback case and an end-to-end case that executes the policy-exception action with role, decider and rationale filled | `E-010` | high |
| `C-002` | End-to-end case deferred on a misplaced constraint | Fix-implementation read the 74-check verifier total and the single-placeholder verifier helper as excluding the end-to-end case, did not place it in the test suite where the total is unaffected, and escalated it as V-001 | `E-011`, `E-006`, `E-025` | high |
| `C-003` | Rollback case dropped unrecorded | Fix-implementation added a gate-exemption case but no rollback case and recorded no deviation for it | `E-011`, `E-004`, `E-002` | high |
| `C-004` | Fix Gate carries both gaps | The Fix Gate was approved with both gaps carried forward as conditions, so no phase before QA required them | `E-012` | high |
| `C-005` | Coverage gap in the delivered suite | No test executes cmd_policy_exception and no test pins the rollback row, while the behaviour they would pin is correct today and observably breaks under mutation | `E-002`, `E-003`, `E-004`, `E-005`, `E-017`, `E-020`, `E-022`, `E-023`, `E-024` | high |
| `C-006` | Observed symptom | QA scored AC-007 and AC-009 not-met and the Verification Gate was rejected, leaving run-e7bf0d73027a unable to close | `E-013`, `E-014` | high |

Alternatives tested: the cases exist elsewhere and QA missed them, eliminated by `E-003`, `E-005`, `E-006`; the gap was a formally accepted risk, eliminated by `E-014`; the rollback row's behaviour changed under the X1 fix, eliminated by `E-007` and by execution in `E-022`; the untested command behaviour is itself defective, eliminated first-hand by `E-017`, `E-019`, `E-020`, which supersede the reported `E-016`; an end-to-end case is infeasible without touching the verifier or the shared run tree, eliminated by `E-018` and `E-025`.

## Fix Strategy

- Proposed fix: the test suite must gain (a) an end-to-end case that runs in its own copy of the framework tree, drives a state item to blocked awaiting_policy_exception the way verifier scenario C does, executes the clearing action read from the failure envelope with only role, decider and rationale substituted, and asserts exit 0, item pending with blocked_reason cleared, envelope and ledger entry resolved by the decider, the decision file and the escalation_resolved event, plus refusal with no state change of the producer's own role on the emitted envelope and of an unlisted role once the copy's envelope lists owners (`E-015`, `E-018` to `E-021`); and (b) an unchanged-rollback case pinning the rollback row to its pre-fix verdicts (`E-022`); runtime and verifier source stay unchanged, the verifier stays at 74, and a real runtime defect exposed while writing them returns to root-cause analysis; the permissive empty-owner-list behaviour of `E-021` is not asserted as correct, pending `Q-005`.
- Alternative options: a new verifier scenario covers the same path but changes the 74-check total, needs the single-placeholder helper widened, and touches bundled-payload parity (`E-006`, `E-008`); an in-process call of cmd_policy_exception with constructed arguments is faster but does not prove the emitted string parses and runs, so it misses the builder mutation of `E-024`; a formal risk acceptance by omn-tech-lead closes the gate without tests and is that role's decision, not a fix.
- Regression risk: low
- Regression scope: the run tree under .claude/runs, whose location the runtime derives from its own file path and which the end-to-end case shares unless it runs in a temp copy (the run-f94564cb61ce restore duty is the precedent); committed run evidence run-c5a8d50d3238, read as the conforming plan, connected through the scenario C injection; the admissibility module's existing 16 cases and its builder pin, connected through shared fixtures; the bundled-payload parity test, connected through the shared verify_recovery.py copy; suite run time (992 s baseline) and temp-directory space, connected through the tree copy per case, so copies are kept to the two the cases need (`E-026`).

## Validation Plan

- Verification steps: rerun the five reproduction steps and observe a rollback case listed and a case that executes the policy-exception command; map each regression item of the root-cause Validation Plan (`E-010`) to a named passing test or a recorded deviation; on temporary copies, show the end-to-end case fails for each `E-024` mutation and the rollback case fails for each `E-023` mutation; run python .claude/runtime/verify_recovery.py and observe 74/74 with git status unchanged; run python -m unittest discover -s tests and observe only the three known test_demo_capture failures of `E-026`; observe no residue under .claude/runs.
- Regression tests added: (1) end-to-end: build the tree with shutil.copytree of .claude/ ignoring runs, __pycache__ and worktrees into tempfile.mkdtemp, removed by addCleanup; copy run-c5a8d50d3238's accepted execution-plan.md into the copy or read it from the source tree; write a feature-request input; run plan --command implement, dispatch --phase execution-planning; write the plan re-stamped with the invocation envelope's input and context digests and a result envelope declaring memory/architecture.md beyond permitted_writes; complete must exit 1; read clearing_action from failure-envelope.json, shlex-split it, substitute the three placeholders in place, set argv[0] to sys.executable, run with cwd at the copy root; assert producer planner exits 2 with every work item unchanged and no policy-exception.json, then a registered non-producer role such as omn-tech-lead exits 0 with item pending, envelope and recovery-ledger entry resolved with resolved_by human and the decider, policy-exception.json granted over memory/architecture.md, one escalation_resolved event, and a repeat exiting 2 as not blocked; a second copy lists omn-tech-lead in the envelope's owner_roles and asserts omn-qa exits 2 with no write; must catch the producer-guard, envelope-resolution and builder-flag mutations of `E-024`; (2) rollback, in tests/test_clearing_action_admissibility.py: a temp StateStore with execution-planning completed and Planning Gate failed rejected, owners planner and omn-tech-lead, producer planner, vr.RUNS patched to the temp directory; the action from fr.rollback_clearing_action is admissible, its single placeholder is the decider, a filled decider stays admissible; a role placeholder and a rationale placeholder are each inadmissible with placeholder in the reason; producer and unlisted roles inadmissible; must catch both `E-023` mutations, so the role and rationale assertions check the reason, not only the boolean.
- Monitoring signals after release: the CI unit and recovery-verifier jobs observed first-hand as green on the default branch; the admissibility module's test count rising from 16; any Validation Plan regression item with no mapped test at a Fix Gate indicates recurrence.

## Closure

- Resolution summary: None identified; the defect is open and closure is a gate decision made elsewhere.
- Linked PR and release: None identified; pending fix-implementation of this run.
- Prevention actions: trace every Validation Plan regression item to a delivered test or a recorded deviation before the Fix Gate is requested, routed as `Q-001`; place end-to-end cases in the test suite when a verifier check total is fixed.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Should the framework require item-by-item tracing of Validation Plan regression cases to delivered tests before the Fix Gate; answered by a design decision on the implement and Fix Gate contracts | no | architect | `C-002`, `C-003`, `C-004` |
| `Q-002` | Is the untested behaviour correct first-hand; answered in this phase by `E-017`, `E-019`, `E-020`, kept to record the answer | no | omn-dev-1-bug-analyst | `C-005` |
| `Q-003` | What is the business impact of the blocked closure and the coverage gap; answered by a business impact statement | no | omn-product-owner | none |
| `Q-004` | The run-e7bf0d73027a fix and its test module are uncommitted (`E-009`); who sequences their commit relative to the tests this run adds | no | omn-orchestrator | none |
| `Q-005` | Runtime-emitted policy-exception envelopes list no owner roles, so any non-producer role name clears the block (`E-021`); which roles may decide a policy exception and should the envelope list them; answered by a design decision, then a separate defect if the runtime must change | no | architect | none |
