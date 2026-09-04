```yaml
bugAnalysis:
  analysisId: BA-run-27e36c138498-root-cause-analysis
  defectReference: runs/inputs/fix-bug-triage-stall-defect-report.md
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/fix-bug-triage-stall-defect-report.md
    - type: bug-analysis
      reference: runs/run-27e36c138498/states/triage-and-impact/artifacts/bug-analysis.md
    - type: symptom-evidence
      reference: runs/run-27e36c138498/state.json
    - type: symptom-evidence
      reference: runs/run-27e36c138498/recovery-ledger.json
    - type: symptom-evidence
      reference: runs/run-93b302cbdb28/state.json
    - type: symptom-evidence
      reference: runs/run-c5a8d50d3238/state.json
    - type: code-context
      reference: runtime/framework_runtime.py
    - type: code-context
      reference: runtime/verify_validators.py
    - type: code-context
      reference: runtime/verify_registry_coverage.py
    - type: code-context
      reference: workflows/README.md
    - type: code-context
      reference: workflows/fix-bug.md
    - type: code-context
      reference: workflows/review-pull-request.md
    - type: architecture-context
      reference: registry/workflows.yaml
    - type: architecture-context
      reference: runtime/README.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  severity: critical
  reproducibility: deterministic
  inputDigest: sha256:404f062123f5e690c567a64a909193cb
  contextDigest: sha256:859732d5f75f500da7d8e023cf3aafff
```

## Metadata

- Bug ID: runs/inputs/fix-bug-triage-stall-defect-report.md
- Reporter: the supplied defect report, which attributes its observation to check `C6` of the registry coverage verifier; no individual, team, or monitor is named in it
- Severity: critical
- Status: complete

## Symptom Summary

- Observed behavior: a run of the bugfix command accepted the request, enqueued all five workflow phases and four gate work items, and then executed none of them, producing no artifact; one second after acceptance the entry phase moved out of the queue into a blocked state, and the four downstream phases stayed pending behind it
- Expected behavior: a run reaches each phase in turn and completes it, with each phase's declared artifact accepted by its registered validator and no phase reporting a capability or contract blocker, which is the acceptance criteria the supplied defect report states
- First observed date: 2026-08-19, recorded at 07:55:08Z in this run's own transition record. The supplied report gives no earlier date. Two earlier runs dated 2026-08-18 carry the same blocked reason against a different phase, so the underlying condition predates this run.
- Affected environments: known affected is the repository at the revision this phase froze, on this host, for the workflows named in the blast radius below. Known unaffected is none established, because no environment was shown to be free of the condition. Not observed is any other host, checkout, or revision of this repository, none of which this analysis could reach; these are recorded as not observed and are not counted as unaffected.

## Reproduction

- Preconditions: an active workflow Phase Model row, and the count of whitespace-delimited tokens carrying the markdown extension in that row's Output Artifact cell. That count is the varying precondition and it fully determines the outcome: a cell with exactly one such token satisfies every consumer of the column, a cell with none blocks the phase while the coverage proof stays silent, and a cell with two or more blocks the phase while the coverage proof demands a validator for each. No other precondition was found to matter; the owning agent, its manifest, and its registered validator are unchanged across the failing and passing cases, per `E-006` and `E-013`.
- Steps to reproduce: change into the framework directory at the repository root, the one holding `runtime/` and `workflows/`, then run the registry coverage verifier at `runtime/verify_registry_coverage.py` and read check `C6`, which reports every phase with a dispatchable verdict and a recorded reason for each blocker. For any phase it reports blocked, which per `E-007` and `E-008` are the same five phases, run `runtime/framework_runtime.py` with the resolve subcommand and that phase's command and phase identifiers, and observe the run end in a workflow-contract-violation quoting the Output Artifact cell text where a filename was expected. To observe the divergence directly, call the runtime's output-artifact derivation and the coverage proof's artifact collection on the same cell text and compare their results across cells carrying zero, one, and two markdown tokens. For the originally reported instance, read the transitions array of `runs/run-27e36c138498/state.json`, which records that phase blocking and then clearing. Every step is read-only and changes nothing.
- Reproduction frequency: deterministic
- Evidence: every artifact and command result this analysis rests on is registered in the Evidence Register below.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | this run's entry phase transitioned from pending to blocked at 07:55:08Z under guard `G1-CAPABILITY`, with the recorded detail that the owning agent declares no output named by the prose string the workflow routed and declares a bug analysis file instead | `runs/run-27e36c138498/state.json` transitions and the event stream beside it, re-read in this phase | high |
| `E-002` | the same phase transitioned from blocked back to pending at 07:56:30Z with the recorded reason that every guard now passes, and the recovery ledger marks the failure envelope resolved at the same instant | `runs/run-27e36c138498/state.json` and `recovery-ledger.json`, re-read in this phase | high |
| `E-003` | the failure envelope classifies the failure as non-retryable at detection point validation with action rollback, and records the clearing action as reconciling the manifest with the Phase Model, stating explicitly that no runtime command clears it | `runs/run-27e36c138498/recovery-ledger.json` and the phase failure envelope beside it, re-read in this phase | high |
| `E-004` | the runtime derives a phase's artifact by tokenising the Output Artifact cell for names carrying the markdown extension, and returns the cell whole whenever the count of such names is not exactly one | source read of `runtime/framework_runtime.py` in this run | high |
| `E-005` | output-contract resolution requires that derived string to appear both in the owning manifest's declared outputs and as a key of the registered validator map, raising a workflow-contract-violation otherwise; the validator map holds thirteen keys, every one a filename, so no prose string can match | source read of `runtime/framework_runtime.py` and enumeration of the validator map, in this run | high |
| `E-006` | resolving the chain for the reported phase against the frozen revision returns a resolved verdict, naming the bug analysis artifact and its registered validator | the runtime resolve subcommand, run in this run for the entry phase and re-run in this phase for the root-cause phase | high |
| `E-007` | five phases across four other active workflows still carry an Output Artifact cell naming no file, and resolving each one's output contract raises the identical failure class and yields the identical blocked reason; they are the documentation and release handoff phase of implement-feature, the publication phase of investigate, the findings publication phase of research, and both the structural compliance and documentation impact phases of review-pull-request | read-only resolution probe over every record in `registry/workflows.yaml`, executed in this run | high |
| `E-008` | the coverage verifier reports 36 phases with 31 dispatchable and 5 blocked, names the same five phases with reason `awaiting_contract_reconciliation`, and records its own check `C6` as passing while reporting them | `runtime/verify_registry_coverage.py`, run in this run and re-run in this phase with the same result | high |
| `E-009` | the derived dependency graph for this workflow is a single hard chain rooted at the entry phase, with the three middle phases and the closing phase each depending hard, directly or transitively, on it, and with no edge downgraded to soft | the runtime dependency derivation evaluated read-only over the frozen `workflows/fix-bug.md`, in this run | high |
| `E-010` | the Validation Engine coverage proof collects a row's Output Artifact only from tokens carrying the markdown extension, so a cell naming no file contributes nothing and the row is never examined; the absence of any branch that records such a row was confirmed by reading the whole function rather than inferred from the check passing | source read of `runtime/verify_validators.py` in this run | high |
| `E-011` | two earlier implement-feature runs each hold a durable work item for the documentation and release handoff phase in status blocked with reason `awaiting_contract_reconciliation`, written while the condition was active and still present | `runs/run-93b302cbdb28/state.json` and `runs/run-c5a8d50d3238/state.json`, re-read in this phase | high |
| `E-012` | the business consequence is stated as the quality agent being unable to satisfy two conditions of the Agent Definition of Done, the first rollout wave being unable to close, and every defect repair routed under the self-hosting profile's defect-repair class being blocked | the supplied defect report, reported and not independently confirmed in this analysis | low |
| `E-013` | the owning agent manifest declares exactly one output, and the block detail captured at 07:55:08Z already reported that same single declared output, so the manifest side of the comparison did not change between the block and the clearing | `agents/omn-dev-1-bug-analyst/manifest.yaml` read in this run, together with the detail in `E-001` | high |
| `E-014` | the frozen workflow specification still states in prose that four phases are dispatchable and that the entry phase blocks at `G1-CAPABILITY` with reason `awaiting_contract_reconciliation`, contradicting the corrected Phase Model table in the same file and contradicting the measured verdict | `workflows/fix-bug.md` read in this run, cross-checked against `E-006` and `E-008` | high |
| `E-015` | no specification in the repository states that the Output Artifact column must name a validatable file; the material found describes the consequence of a cell that does not, but states no requirement on the column itself. The absence was confirmed by searching the markdown and runtime sources for such a requirement, not assumed from its not being cited. | repository-wide search executed in this run | medium |
| `E-016` | the workflow authoring contract declares the Phase Model table to be the machine contract, states that the Task Router reads it for artifacts and derives the dependency graph from the Input and Output Artifact columns, and then enumerates exactly three rules constraining what may appear in the table: the form of phase identifiers, one owner agent per phase, and a gate matrix row for every gate named. None of the three constrains the Output Artifact column. The absence was confirmed by reading the enumerated rules in full, not inferred from the column not being mentioned. | `workflows/README.md` read in this phase | high |
| `E-017` | the workflow registry requires only that an active record's specification publish a machine-resolvable Phase Model section, failing when the section is missing, and states no requirement on the content of any cell within it. The absence was confirmed by reading the resolution and validation blocks in full. | `registry/workflows.yaml` read in this phase | high |
| `E-018` | three consumers read the same Output Artifact cell under three different rules: the output-contract reader requires exactly one markdown token and returns the cell whole otherwise, the coverage proof collects every markdown token and collects nothing when there are none, and the dependency-graph reader splits the cell into prose terms and matches them by containment. Across the 36 active rows the first two agree on 31 and disagree on 5, and on those 5 the third reader succeeds where the first fails. | read-only probe exercising all three readers over every active Phase Model row, executed in this phase | high |
| `E-019` | the output-contract reader's own source states that its tokenising rule is the same one the coverage proof applies and that the two readers of the column therefore agree, while the next paragraph of the same comment records that a cell naming no file or more than one is returned whole. Exercising both readers on cells carrying zero, one, and two markdown tokens shows they agree only in the single-token case and diverge in both other directions. | source read of `runtime/framework_runtime.py` together with the reader probe, in this phase | high |
| `E-020` | replacing all five prose cells with a single filename, simulated in memory without writing to the repository, changes no dependency edge in any active workflow, because in every one of those rows the prose-derived edge coincides with the row-order fallback the derivation applies when no term matches | in-memory simulation over the parsed Phase Models, executed in this phase | high |
| `E-021` | the five blocked phases hold their workflows to five of six, four of five, four of five, and one of five completable phases; review-pull-request loses both test-risk-validation and merge-decision transitively because its blocked structural compliance phase is the second of five rows, so only its first phase can complete | transitive hard-edge closure computed over the parsed Phase Models, executed in this phase | high |

## Impact Assessment

- User impact: an operator invoking the bugfix command received a run that accepted the request, enqueued every phase and gate, and produced nothing, with no runtime command able to clear the condition and therefore no route to a diagnosis of any defect through the workflow that exists to diagnose defects. The same holds today for operators of the four commands routing the five phases that still carry the condition, and per `E-021` it is worst for pull-request review, where only the first of five phases can complete and the phase that decides whether a change merges is unreachable. No supplied input quantifies how many operators that is; the framework offers no alternative route to those phases, so every operator of an affected command is affected.
- Business impact: taken as given from the supplied defect report, which states that the quality agent cannot satisfy two conditions of the Agent Definition of Done, that the first rollout wave cannot close, and that every defect repair routed under the self-hosting profile's defect-repair class is blocked. That statement came from the reporter rather than from the product owner and was not independently confirmed here, so it is registered at low confidence as `E-012` and is not what the severity rests on.
- Technical impact: availability rather than correctness. A core execution path was wholly unavailable: the entry phase of the defect-repair workflow blocked one second after the run was accepted, the failure is classified non-retryable with action rollback, and the recorded clearing action states that no runtime command clears it, so the runtime had no path back to a working state on its own. Four further workflows cannot reach their terminal phase today, and one cannot get past its second row. Nothing was computed incorrectly and no data was corrupted. Durable run state was written while the condition was active and survives correction of the specification that caused it.
- Blast radius:
  - the whole of this workflow: the entry phase directly, and the root-cause, fix-implementation, regression-validation and closure phases through the hard dependency chain rooted at it, together with the Triage Gate work item enqueued to close the entry phase and therefore unreachable while that phase is blocked
  - implement-feature, which per `E-021` completes five of six phases and cannot reach its terminal documentation and release handoff phase, so no run of it can close
  - investigate, which completes four of five and cannot reach its publication phase
  - research, which completes four of five and cannot reach its findings publication phase
  - review-pull-request, which completes one of five: its structural compliance phase is blocked at the second row, and test-risk-validation and merge-decision are held behind it by hard edges, so no pull request can reach a merge decision through this workflow
  - the commands routing those four workflows, each of which reaches its blocked phase by no alternative path
  - every future Phase Model row authored against the same column, because per `E-018` and `E-019` the divergence is a property of the column's readers and not of the five rows that happen to trip it today; a cell naming two artifacts diverges in the opposite direction, blocking the phase while the coverage proof demands a validator for each name
  - persisted state written while the condition was active and not removed by correcting a specification: two earlier runs each holding a work item durably in status blocked under this reason per `E-011`, plus this run's failure envelope and its append-only recovery-ledger entry, which per `E-003` record the condition permanently by design
  - the reported dispatchability figure itself, which counts phases resolving their own capability chain and therefore reports as dispatchable a phase that a hard predecessor makes permanently unreachable

## Root Cause Analysis

- Root cause statement: no rule anywhere governs what the Phase Model Output Artifact column must contain, while three runtime consumers each read that one cell under a different and unstated requirement, so a cell that satisfies one consumer can block another and nothing at authoring time can detect the conflict.
- Why detection failed earlier: four things had to fail together, and each did. No authoring-time check exists for this column because no constraint exists to check, per `E-016` and `E-017`. The Validation Engine coverage proof, which is the check that exists to catch an artifact with no validator, collects a row's artifact only from tokens carrying the markdown extension, so a prose-only cell contributes nothing and the row passes without being examined, per `E-010`. The registry coverage proof does observe the blocked phases and names each with its reason, but it is written to pass whenever every blocker carries a recorded reason, so per `E-008` it reported five blocked phases and returned a passing verdict in the same run. And the runtime's own source asserts that the two artifact readers of this column agree, per `E-019`, so the divergence was documented as impossible in the one place a maintainer would look to check it.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-007` | no constraint governs the column | the authoring contract declares the Phase Model table the machine contract and enumerates three rules for what may appear in it, none constraining the Output Artifact column, and the registry requires only that the table exist | `E-016`, `E-017` | high |
| `C-008` | three consumers impose three unstated requirements on it | the output-contract reader needs exactly one filename token, the coverage proof accepts any count including none, and the dependency-graph reader needs matchable prose terms, so only a cell naming exactly one file satisfies all three, and the runtime's own source records the first two as agreeing when they diverge for zero tokens and for two | `E-018`, `E-019` | high |
| `C-001` | column authored as prose | the Phase Model stated the entry phase's Output Artifact as a prose decision naming no file, which no rule forbade, while the owning manifest declared exactly one output and that output was a filename | `E-001`, `E-013` | high |
| `C-002` | runtime derives an artifact from the cell | the runtime tokenises the cell for names carrying the markdown extension and, finding none, returns the cell whole, so the prose text became the artifact identifier the phase was held to | `E-004` | high |
| `C-003` | output contract fails to resolve | resolution requires that identifier to be both a declared manifest output and a registered validator key, and the prose text was neither, so resolution raised a workflow-contract-violation | `E-005`, `E-001` | high |
| `C-004` | capability guard converts it to a block | the guard turned that violation into a non-retryable block carrying reason `awaiting_contract_reconciliation`, which the classification matrix records as clearable by no runtime command | `E-001`, `E-003` | high |
| `C-005` | the block propagates along hard edges | the workflow's dependency graph is a single hard chain rooted at the blocked entry phase, so the predecessor guard held all four downstream phases irrespective of their own capability verdicts | `E-009` | high |
| `C-006` | observed symptom | the run enqueued five phases and four gates and produced no artifact, because the only phase eligible to begin was the blocked one | `E-001`, `E-009` | high |

## Fix Strategy

- Proposed fix: give the Output Artifact column a stated contract, and make that contract the thing every consumer of the column reads. What a fix must achieve is that a row which cannot yield an artifact the Validation Engine can decide is rejected when it is authored, rather than resolving differently in three places and surfacing as a run-time block in one of them. Because the cause is the absence of a rule rather than a fault in any one reader, correcting the five cells alone does not remove it: the same divergence returns with the next row authored, and per `E-018` it returns in the opposite direction for a cell naming two artifacts. The fix must also reach the state already persisted while the condition was active, namely the two runs holding a phase durably blocked and this run's failure envelope and append-only ledger entry, because none of that is re-evaluated by editing a specification. It must also leave the defect-repair workflow's own narrative agreeing with its Phase Model table and with the measured verdict, which per `E-014` it does not today. No part of this states how to build the change.
- Alternative options: the first approach states the contract as one artifact file per phase and enforces it at authoring time, so a non-conforming row fails a verification check instead of blocking a run; this keeps every phase's output decided by a validator and makes the three readers agree by construction, but it cannot land until each of the five remaining prose rows has been given an artifact type, a template, and a registered validator, which is the decision recorded as `Q-002`. The second approach states the contract as an optional artifact, letting a phase declare that it emits no validatable file and dispatching it with no Validation Engine verdict; this clears the blocked phases without waiting on artifact-type decisions, but it gives up the guarantee that every phase's output is judged, which is the property the block exists to protect. A third approach separates the concerns the column currently carries at once, giving the machine-read artifact its own column and leaving the prose description in another; this removes the conflict at its source rather than legislating one reading over the others, at the cost of changing the table shape every workflow publishes and every reader parses. What distinguishes them is where the cost falls and what is conserved: the first keeps validation total and pays at authoring, the second keeps authoring free and makes validation partial, the third pays once in structure and removes the ambiguity permanently.
- Regression risk: high
- Regression scope:
  - the phase dependency graph, which per `E-018` reads the same cell as prose terms and matches them by containment; any change to what the column carries changes the terms available to match, and the third alternative above changes the table shape the derivation parses. Measured for the five rows at issue: per `E-020` replacing each prose cell with a single filename changes no edge in any active workflow, because in each case the prose-derived edge coincides with the row-order fallback. That measurement holds for the current row adjacency only and must be re-taken if rows move or if a non-adjacent row is corrected.
  - the Validation Engine coverage proof, which reads the same cell through a different filter and currently passes by never examining the rows at issue; giving the column a contract changes which rows that proof observes and can flip its verdict, and per `E-019` its agreement with the output-contract reader is asserted in source rather than tested
  - the four workflows holding the five phases that still carry the condition, reached through their own Output Artifact and Input columns; giving each phase an artifact type changes cells the dependency graph is derived from, and per `E-021` review-pull-request is the sensitive one because its blocked phase sits at the second of five rows rather than at the end
  - the durable run store, reached through the state machine's transition rules; re-evaluating work items already recorded blocked in earlier runs touches the transition path every run in flight depends on
  - the reported dispatchability figure and the passing verdict of the registry coverage check, which move with all of the above and which other framework records cite as a readiness measure

## Validation Plan

- Verification steps: the condition is removed when the column has a stated contract and every consumer of the column is held to it, so verification must reach the contract and not only the symptom. For every active Phase Model row, the runtime's artifact derivation and the coverage proof's artifact collection must return the same artifact, and that artifact must have a registered validator; a row that cannot satisfy this must fail a check at authoring time rather than resolve three ways. The registry coverage check must report no phase carrying reason `awaiting_contract_reconciliation`, and a rising dispatchable count is not sufficient because that count rises when any blocker of any kind clears. The divergence must be exercised deliberately in both directions, on a cell naming no artifact and on a cell naming two, since per `E-019` the single-artifact case is the only one in which the readers agree today and testing only that case would confirm nothing. A bugfix run reaching regression validation is necessary and demonstrates the symptom is gone, but it does not on its own demonstrate the cause was removed.
- Regression tests added: a check that fails when an active Phase Model row's Output Artifact cell does not satisfy the stated column contract, so the condition is caught at authoring time rather than at run time; a check that the runtime's artifact derivation and the coverage proof's artifact collection agree on every active row, exercised over cells carrying zero, one, and two artifact names, so the agreement is tested rather than asserted; and a check that the derived dependency graph for every active workflow is unchanged by the corrections, so a sequencing regression cannot land unnoticed. These state what should exist; writing them belongs to `omn-dev-1-implement` and running them to `omn-qa`.
- Monitoring signals after release: the per-phase blocked reasons reported by the registry coverage check, where any phase reappearing with reason `awaiting_contract_reconciliation` indicates recurrence; the count of phases that resolve their own capability chain yet sit behind a blocked hard predecessor, which is the number the reported dispatchability figure currently conceals and which per `E-021` is where the real cost of this defect sits; and the number of durable work items across the run store carrying that blocked reason, which must not increase after the fix.

## Closure

- Resolution summary: None identified. The defect is not resolved. The operator correction that removed the precondition for one phase of one workflow is registered as `E-002`, as evidence of the varying precondition rather than as a resolution, and closure is a gate decision this analysis does not record.
- Linked PR and release: None identified.
- Prevention actions: the authoring-time check named under `Regression tests added`, which fails on a non-conforming row instead of leaving it to surface as a run-time block, together with a test that exercises the agreement between the two artifact readers rather than asserting it in source. Both follow from `Why detection failed earlier` and neither is yet an agreed action, because the form of the check depends on the column contract chosen through `Q-002`.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-002` | Which of the three column contracts is adopted, and which artifact type does each of the five phases still carrying the condition emit? The choice decides the form of the authoring-time check and, under the first two alternatives, requires an artifact, a template, and a registered validator per phase. A recorded architecture decision naming the column contract and the artifact type per phase would resolve it. | yes | `architect` | `C-007`, `C-008` |
| `Q-001` | Resolved by this phase, and recorded here so the triage artifact's reference to it resolves. The question was which reading of the Output Artifact column is authoritative. Neither is: per `E-015`, `E-016` and `E-017` no rule constrains the column at all, so no reading is authorised over another, and per `E-018` three consumers read it three ways. The question was mis-framed as a choice between two readers, and the answer is that the contract they would be judged against does not exist. | no | `architect` | `C-001`, `C-002`, `C-007`, `C-008` |
| `Q-003` | Is the defect-repair workflow's narrative merely stale against its own corrected table and the measured verdict, or was the table corrected without the decision the narrative records? Reconciling the two, or recording the decision the correction rests on, would resolve it. | no | `omn-tech-lead` | `C-001` |
| `Q-004` | What becomes of the two earlier runs holding a phase durably blocked under this condition: are they re-opened, re-planned, or closed once the column contract is settled? That is a run-management decision this analysis does not hold. A recorded disposition for each run would resolve it. | no | `omn-orchestrator` | none |
| `Q-005` | No environment other than this host's frozen checkout was reached, so the analysis cannot state whether another host, checkout, or revision carries the same column contents and therefore the same condition. Resolving it needs the condition checked against another checkout, which is environment access this analysis does not hold. | no | `omn-orchestrator` | none |
