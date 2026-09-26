# Implementation Report: Orientation Document Folder Descriptions Sync

```yaml
implementationReport:
  reportId: IR-2026-0008
  changeReference: >-
    folder-descriptions-sync, implemented at
    run-34ca35504b72::refactor-implementation
  sourceInputs:
    - type: validation-report
      reference: runs/run-34ca35504b72/states/safety-net-establishment/artifacts/validation-report.md
    - type: technical-design
      reference: runs/run-34ca35504b72/states/scope-invariants-and-risk-profile/artifacts/technical-design.md
    - type: change-request
      reference: runs/inputs/*-md-folder-sync-change-request.md
    - type: business-intent
      reference: runs/inputs/*-md-folder-sync-business-intent.md
    - type: architecture-context
      reference: runs/inputs/*-md-folder-sync-architecture-context.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: provisional
  workflowPhase: refactor-implementation
  verificationStatus: partially-verified
  inputDigest: sha256:6339224bf55b0319426b6df9bf6bf828
  contextDigest: sha256:8cb5fd5cf493e2c79a982b48f28b0793
```

## Metadata

- Report ID: IR-2026-0008
- Change reference: folder-descriptions-sync, implemented at run-34ca35504b72::refactor-implementation
- Workflow phase: refactor-implementation
- Status: provisional
- Verification status: partially-verified
- Review status: pending-review

Naming note, continuing the convention the technical design established and the safety-net
validation report followed: the changed file is called "the orientation document" throughout,
and the leading token of three supplied input filenames is elided, because the file name and
those filenames each embed a token the model-independence rule forbids reproducing. The
changed file is the project-instructions document at the framework payload root, the one
carrying the `## Folder Descriptions` section; it is identified without being named by its
content digests, `4372781420e4ea81327d737f8be44603` over 2794 bytes before the change and
`59a93ad68e3ddacb8e4e157c2545d676` over 3215 bytes after it. Repository paths are cited
payload-relative, without the leading payload-directory prefix, so a command recorded below as
`python runtime/verify_recovery.py` was invoked from the repository root with that prefix
present. Identifiers of the `D-nnn`, `P-nnn`, `M-nnn`, `F-nnn`, `A-nnn`, `AC-nnn`, and `DF-nnn`
families belong to the upstream technical design and validation report; the `C-nnn`, `T-nnn`,
`V-nnn`, `R-nnn`, and `Q-nnn` families in this report are this report's own namespace, so
upstream constraints, risks, and questions carrying those prefixes are named descriptively
here rather than by their upstream token.

## Implementation Summary

- Change intent: the folder inventory in the orientation document now describes every directory at the framework payload root, sixteen of sixteen, where before it described twelve and silently omitted the framework's domain-specification, prompt-pattern, discovery-index, and executable-runtime directories.
- Approach taken: the additive in-place extension the design selected as its option O-001, implemented as four new one-line rows inserted into the existing list at the positions a reader scanning the tree would reach them, each row authored against the folder's own named authority under design step P-001 and each pre-existing row left untouched; no other section, file, or surface was edited.
- Design reference: design decisions D-001 and D-002, realized under sequencing steps P-001 and P-002 against impacted module M-001, with the pre-change comparison reference taken from the safety-net validation report's baseline block.
- Out of scope: every other section of the orientation document and every other file in the repository, left unchanged because the design's diff-confinement constraint makes any edit outside the section a rejection condition; the change proposal the design's final sequencing step P-004 requires, which is a governance record under `proposals/` that this phase's write scope excludes and whose prerequisite is the verification recorded here; the discrepancy the design records about `dependency-map.md`, which the design routes as a separate change; and the accuracy and granularity judgements the design reserves to the reviewing roles, which are recorded below as unverified rather than decided here.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | the orientation document at the framework payload root, section `## Folder Descriptions` | modified | Add four one-line rows describing `domain-model/`, `prompts/`, `registry/`, and `runtime/`, completing the folder inventory at sixteen of sixteen without altering any pre-existing row | `D-001`, `D-002`, `P-002` (module `M-001`) |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Pre-change regression baseline: every command in this table executed against the unmodified document, establishing the comparison reference; the document's own full-content digest reproduced the value the safety-net report pinned, proving the file was untouched between the two phases | regression | `C-001` | the commands of `T-002` through `T-010`, executed at 02:16Z to 02:19Z before any edit | pass |
| `T-002` | Completeness: every directory at the framework payload root has a row, and the undocumented set is empty | static | `C-001` | inline `python` probe enumerating directory entries at the payload root and differencing them against the row keys parsed from the section | pass |
| `T-003` | Additivity: the twelve pre-existing rows are all present, unchanged, and in their pre-change relative order | static | `C-001` | inline `python` probe re-deriving the row-key order and comparing its digest against the pinned baseline `6a0c112e6f2e9f0f3ef92e728c8216f4` | pass |
| `T-004` | Diff confinement: the document's content outside the section is byte-identical to its pre-change content, and the level-2 section list is unchanged | static | `C-001` | inline `python` probe digesting the out-of-section content and the heading list, compared against the values pinned before the edit | pass |
| `T-005` | The diff is purely additive and lands only inside the section: seven inserted lines, no deleted and no modified line, every hunk within the section's line range | static | `C-001` | `git diff --stat` and `git diff -U0` restricted to the changed file | pass |
| `T-006` | Path resolvability: every backtick-quoted path token the document cites exists on the filesystem, including the four newly cited folders | static | `C-001` | inline `python` probe extracting each backtick-quoted token and testing it for existence | pass |
| `T-007` | The governance-prose content contracts still hold over the framework's documents | regression | `C-001` | `python -m unittest tests.test_content_contracts` | pass |
| `T-008` | Packaged-payload parity still holds, confirming the change requires no bundle re-sync | regression | `C-001` | `python -m unittest tests.test_bundled_payload` | pass |
| `T-009` | The memory-optimization tool, the only module in the repository that names the changed document, is unaffected | regression | `C-001` | `python -m unittest tests.test_optimize_memory` | pass |
| `T-010` | Verifier verdict parity: each of the seven verification scripts reproduces the summary line it produced before the change, including the two that fail at baseline for reasons this change did not introduce | integration | `C-001` | `python runtime/verify_manifests.py`, `python runtime/verify_registry_coverage.py`, `python runtime/verify_validators.py`, `python runtime/verify_recovery.py`, `python runtime/verify_vertical_slice.py`, `python runtime/verify_multi_phase.py`, `python runtime/verify_self_hosting.py`, each from the repository root | pass |
| `T-011` | Attribution control for the two scripts that reported a non-baseline verdict on one measurement pass: both reproduce their baseline verdicts with the change in place, and both also pass with the pre-change content restored, so neither movement is attributable to this change | integration | `C-001` | `python runtime/verify_recovery.py` and `python runtime/verify_vertical_slice.py`, each executed with the changed content in place and again with the pre-change content temporarily restored | pass |

## Verification Results

- Verification method: the safety-net validation report's monitoring instruction was followed literally: the full declared regression surface was executed against the unmodified document to fix the comparison reference, the single additive edit was then made, and the identical surface was re-executed and compared at summary-line granularity, which is the granularity that report's own defect record `DF-001` establishes as the stable one. Structural conformance to the design's constraints was measured by inline probes over the document itself, each computing a digest or a set difference against a value pinned before the edit rather than against a description of it. The two scripts that moved were investigated to a cause and controlled for rather than explained away.
- Commands executed: `python runtime/verify_manifests.py`; `python runtime/verify_registry_coverage.py`; `python runtime/verify_validators.py`; `python runtime/verify_recovery.py`; `python runtime/verify_vertical_slice.py`; `python runtime/verify_multi_phase.py`; `python runtime/verify_self_hosting.py`; `python -m unittest tests.test_content_contracts`; `python -m unittest tests.test_bundled_payload`; `python -m unittest tests.test_optimize_memory`; `git status --porcelain`; `git diff --stat` and `git diff -U0` restricted to the changed file; and inline `python` probes over the document computing its section inventory, row order, out-of-section digest, directory coverage, and path-token resolvability. Each was run from the repository root, before the edit and again after it. The full root suite was deliberately not run, because one of its modules rewrites two generated documents in place, which would be a repository write this phase must not cause.
- Result summary: 11 evidence entries executed, 11 passed, 0 failed, 0 not-run. Underneath them, 55 unit tests executed across three modules with 55 passed and 0 failed, and 88 verification checks executed across seven scripts with 86 passed and 2 failed, both failures being the pre-existing ones the baseline recorded before the edit and reproduced unchanged after it.
- Unverified areas: whether each of the four added descriptions is accurate against its folder's named authority, and whether each stays at summary granularity in the register of the existing rows, which no executed check settles and which the design reserves to `omn-dev-2-reviewer` and to the Invariant Gate; and whether the completed inventory stays complete, which no executed check in either verification surface the CI workflow discovers can assert, because no such check reads the changed document.

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | The insertion positions and the authored wording of the four rows in `C-001` were decided at implementation: the rows were interleaved into the existing list rather than appended, placing the domain-specification row before the contract rows it governs, the prompt-pattern row beside the reusable-knowledge rows, and the discovery-index and runtime rows after the command row, in the order a reader following the routing story meets them | Design decision D-002 and the design's negotiable placement constraint, which fix the content requirement and the insertion principle but leave the text and the position to implementation | The design states the row content as a requirement and says explicitly that the text is authored at implementation under step P-001; interleaving is what the accepted insertion principle asks for, and the pre-existing rows keep their relative order under it, which `T-003` measured rather than assumed | not-required; the latitude is granted by the design element itself, and the register and granularity judgement it leaves open is carried to the Invariant Gate as `Q-003` |
| `V-002` | No durable automated check over the section was added alongside `C-001`, so the completeness the change establishes is re-measurable only by re-running the probes this report records, not by a check the CI workflow discovers | The design's reuse survey, which records verdict parity over the existing scripts as the regression measure and concludes that no new validation structure is required | Adding one would widen the change set past the accepted change and past the diff-confinement constraint that makes any edit outside the section a rejection condition; separately, the safety-net phase established that no path satisfies both this phase's write scope and either verification surface the CI workflow discovers, so no such check is authorable from within this phase's authority | not-required; the departure sits inside the design's own accepted tradeoff, and the underlying write-scope question is carried forward unresolved as `Q-002` |

## Boundary Compliance

- Module boundaries preserved: the change touches one documentation section and nothing else. The design's no-change-verified modules were each read as an authority and none was modified: the discovery-index directory, the executable-runtime directory, the domain-specification directory, and the prompt-pattern directory are described by the new rows and are untouched by them, which `T-005` confirms by showing the only changed lines in the repository attributable to this phase sit inside the section. The document remains a summary layer: each new row names what its folder holds and defers to that folder's own authority, restating no record those authorities hold.
- Public interface changes: none. No contract, registry record, routing row, gate, validator, or workflow phase resolves the changed document, so no interface exists to change; the verification scripts that read the framework's resolved surfaces reproduce their pre-change verdicts under `T-010`.
- Data or migration impact: none. There is no schema, no stored data, and no migration; the change is reversible by deleting the four added rows, with no behavioural or contractual effect.
- Declared side effects: three files were written by this invocation — the orientation document at the framework payload root (`C-001`), `runs/run-34ca35504b72/states/refactor-implementation/artifacts/implementation-report.md`, and `runs/run-34ca35504b72/states/refactor-implementation/result-envelope.json`. One further effect is declared because it is real rather than because it persists: the recovery verification script creates and then deletes its own injected run directories under `runs/` as part of how it induces the failures it proves, so running it, as the safety net's monitoring instruction requires, causes transient writes inside this phase's write-exclusion zone. The effect is net zero and was verified so: the tracked and untracked state of `runs/` was enumerated before and after, and no injected directory survives. During the phase one path appeared under `proposals/` that this invocation did not write and must not be attributed to it — a change proposal recording a different run, written by concurrent activity in this shared working tree at 02:29Z.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | The inventory drifts out of date again as directories are added, because an additive manual edit carries no mechanical guarantee of completeness | medium over time | low; the same class of defect this change corrects, recurring | In place: the completeness probe of `T-002` is recorded here with its method, so any later run can re-execute it, and the count it asserts is stated in the report the Implementation Gate reads. Nothing enforces it automatically; that gap is `R-002` |
| `R-002` | A defect introduced into the section in future goes undetected, because no check in either verification surface the CI workflow discovers reads the changed document | low | medium; the document is injected into every contributor session as authoritative instructions, so a wrong row misleads broadly | In place: nothing mechanical. The safety-net phase established that no authorable path satisfies both this phase's write scope and either discovered surface, and carried the question forward; it is restated here as `Q-002` rather than treated as closed |
| `R-003` | The two verification scripts that fail at baseline are read as regressions of this change by a later comparison | low | low; a false attribution costs an investigation, not a defect | In place: both failures were measured before the edit and reproduced unchanged after it under `T-010`. The multi-phase script fails its `M6` check and the self-hosting script fails its `S8` check, the latter because runs in flight are unaccounted until their change proposals exist, which is a condition this phase cannot clear and does not cause |
| `R-004` | A future parity comparison against the recovery verification script shows a difference no change caused, because that script is intermittently unstable | medium | low; it costs a re-measurement | In place: the instability was characterized rather than absorbed. It crashes in its backoff-wait helper when a queued item carries no availability timestamp, which is a timing race in the script and not a function of any document content. The verdict was reproduced on three consecutive executions after the change, and the control in `T-011` shows the same movement occurs independently of this change |
| `R-005` | A repository-wide measurement taken during this phase is read as evidence about this change, when the working tree was shared with concurrent activity throughout | high, and already realized | low, given the controls | In place: no claim here rests on a whole-repository measurement. Whole-tree status was recorded with its timestamp and treated as contaminated; the two paths that appeared during the phase were enumerated individually and attributed, one to this change and one to concurrent activity; and every verification claim rests on per-file diffs, digests pinned before the edit, and targeted module executions |

## Handoff Notes

- Reviewer focus areas: the four added rows themselves, which carry the only judgement this phase could not settle — whether each description is accurate against its folder's authority, checkable against the five specification files in the domain-specification directory, the prompt directory's own README, the five discovery indexes, and the runtime directory's README; and whether each stays at summary granularity in the register of the existing twelve rows, which is the risk the design attaches to its own concern about a second authority forming. The insertion positions recorded under `V-001` are the other place independent judgement is worth spending, since the placement principle is stated but the positions were chosen here. The structural constraints need no re-derivation: `T-002` through `T-006` measured each of them against values pinned before the edit.
- Follow-up work: the change proposal the design's step P-004 requires, which links this run's artifacts and is the governance record of the verified change, and which this phase's write scope excludes; the durable completeness check that `R-001` and `R-002` leave unmitigated, which cannot be authored until the write-scope question in `Q-002` is answered; the `dependency-map.md` discrepancy the design recorded for separate routing, which the new discovery-index row makes more visible by describing indexes that map does not mention; and the timing race in the recovery verification script characterized under `R-004`, which is a defect in that script and belongs to its own routed change.
- Documentation impact: the change is itself the documentation correction, and it invalidates no other document. The orientation document's Architecture and Contributor Usage sections already referenced the runtime directory that its own inventory omitted; that inconsistency is now resolved by the inventory rather than by touching either section, both of which are byte-identical to their pre-change content under `T-004`. No release note, user-facing document, or generated document is affected, and none was regenerated.

## Open Questions

| ID | Question | Blocking | Owner | Affected changes |
|---|---|---|---|---|
| `Q-001` | The design's verdict-parity constraint requires the verification scripts to keep their current verdicts and separately that no metric regresses. The self-hosting script still reports one unaccounted run, and the change proposal the design's step P-004 requires would remove the last such input and flip that script from failing to passing, which violates the first reading and satisfies the second. Which reading governs when the downstream phase judges parity? Raised by the safety-net phase and unresolved at this one; both baselines are recorded, so either answer is decidable without re-measurement | No | architect | `C-001` |
| `Q-002` | This phase's write scope for test files is confined to the framework payload tree, while both verification surfaces the CI workflow discovers lie outside it, so no durable check over the changed section is authorable from within this phase's authority. Which surface should the grant name? Until it is answered, `R-001` and `R-002` stay unmitigated and `V-002` stands | No | architect | `C-001` |
| `Q-003` | Are the four added descriptions accurate against their named authorities, and does each stay at summary granularity in the register of the existing rows without becoming a second authority beside the records it summarizes? This is the confirmation the change request asked for and the design routed away from the producing roles; this agent verified each row against its authority while authoring it, but the confirming judgement is not this agent's to record | No | omn-dev-2-reviewer | `C-001` |
| `Q-004` | The design's step P-004 requires a change proposal under `proposals/` linking this run's artifacts, and this phase's write scope excludes that directory. Which role produces it, and at which phase, so the self-hosting profile's governance requirement is met for this run? | No | omn-orchestrator | `C-001` |
