```yaml
bugAnalysis:
  analysisId: BA-run-5d3c99aaaae1-triage
  defectReference: investigate-chain-input-contracts-defect-report
  sourceInputs:
    - type: defect-report
      reference: runs/inputs/investigate-chain-input-contracts-defect-report.md
  producedBy: omn-dev-1-bug-analyst
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  severity: high
  reproducibility: deterministic
  inputDigest: sha256:90c7b5a6aa846a07964a3815823ec9f2
  contextDigest: sha256:af95bb67d09092740f15c6736e259409
```

## Metadata

- Bug ID: investigate-chain-input-contracts-defect-report
- Reporter: the operator, through a supplied defect report
- Severity: high
- Status: provisional

## Symptom Summary

- Observed behavior: A phase whose predecessor has completed stays blocked at guard G5-INPUT with "no accepted input type supplied", because the artifact the runtime hands over carries an identifier the consuming agent does not list. The blocked phase leaves its successors pending, so the run cannot finish. The defect is wider than reported: 13 of 29 consecutive hand-offs across 6 workflows offer an identifier the consumer does not accept, and 4 of 7 profile routing rows name an entry input the entry agent rejects.
- Expected behavior: Each phase accepts the artifact its Phase Model Input column names from the phase before it, and the profile routes each command with an input type its entry agent accepts, as stated by the operator in the defect report (`E-001`).
- First observed date: Not established. Reproduced in this run on 2026-10-09; the earliest committed evidence read is a stalled investigate run that predates this analysis.
- Affected environments: Known affected is the framework tree of this working copy at runtime 0.9.0, reproduced in a throwaway mirror. Known unaffected, by measurement, are the refactor chain and the fix-bug chain when the entry input type persists in the pool. Not observed are the main checkout, the bundled payload copy, and consumer repositories with their own framework copies.

## Reproduction

- Preconditions: A tree identical to this working copy, mirrored to a scratch location outside the repository so no committed run evidence is touched. No operator input is supplied beyond the single entry type named in each step. Upstream completion in step 3 is simulated by editing only the mirror's run record, and the artifact stands in for a validated one. The working tree was compared before and after (`E-016`).
- Steps to reproduce: (1) In the mirror, ask the profile router for the decision-support class, note the input it names, then plan an investigate run with that input type and read the entry phase reason. (2) Plan an investigate run with problem-statement alone; the entry phase is ready. (3) Mark problem-framing completed with artifact identifier requirement-framing in the mirror run record, approve the Framing Gate, and ask the runtime for the next item; read the technical-discovery reason. (4) Repeat step 3 with problem-statement and investigation-question both supplied and read the same phase. (5) Run the measurement scripts, which compute every hand-off from the manifests and the Phase Models using the runtime's own contract functions.
- Reproduction frequency: deterministic
- Evidence: Every attempt, measurement, and read is recorded in the Evidence Register below.

### Evidence Register

| ID | Evidence | Source | Confidence |
|---|---|---|---|
| `E-001` | The defect report states the mechanism, four sample hand-offs, one profile mismatch, and a medium-to-high severity; none of it was relied on without a first-hand check | Supplied input defect-report, runs/inputs/investigate-chain-input-contracts-defect-report.md | low |
| `E-002` | The runtime offers each completed upstream artifact under the identifier recorded at lease time from the producing agent's manifest output, falling back to the file stem; read at upstream_inputs and at the lease transition | runtime/framework_runtime.py read in this run | high |
| `E-003` | Guard G5-INPUT builds its pool from the run's supplied inputs plus upstream artifacts, keeps only types the consumer manifest declares, and for a menu contract blocks unless one surviving type is in the accepted list; optional-only types do not satisfy it | runtime/framework_runtime.py read in this run: resolve_input_contract, narrow_inputs, guard G5 | high |
| `E-004` | The Phase Model tables of investigate and research each list five phases owned by business-analyst, context-agent, tech-lead, tech-lead, documentation, with Input columns that name artifact files and no identifiers | workflows/investigate.md and workflows/research.md read in this run | high |
| `E-005` | Measurement over every active workflow: 29 consecutive hand-offs, 13 offer an identifier the consumer does not list as accepted; by workflow: investigate 3 of 4, research 3 of 4, implement-feature 2 of 5, review-pull-request 2 of 4, release 2 of 4, fix-bug 1 of 4, refactor 0 of 4, code-quality-scan 0 of 0 | Scratch script handoffs.py run read-only against the runtime's own phase, dependency, and manifest loaders | high |
| `E-006` | Measurement with the entry type supplied, using the real contract function: investigate and research block at 3 phases for every entry type; review-pull-request blocks at 2; release at 1 or 2; implement-feature at 1 for two entry types and 0 for feature-request; fix-bug, refactor, and code-quality-scan block at none | Scratch script supplied2.py run read-only; output identical to the first version that reimplemented the guard | high |
| `E-007` | In the mirror, the router names input investigation-request for decision-support, and a run planned with it blocks the entry phase at G5-INPUT: no accepted input type supplied; accepted business-intent, problem-statement, requirement-input | Mirror run, router and plan commands | high |
| `E-008` | In the mirror, a run planned with problem-statement left problem-framing ready; after simulated completion and Framing Gate approval, technical-discovery blocked at G5-INPUT with accepted framed-objective, research-brief, investigation-question, research-question | Mirror run, plan, next, and failure envelope of technical-discovery | high |
| `E-009` | In the mirror, the same simulation with problem-statement and investigation-question both supplied left technical-discovery ready, so the block is the identifier mismatch and not the gate or the artifact | Mirror run, plan and next | high |
| `E-010` | A committed investigate run, read only, completed problem-framing, technical-discovery, and option-analysis with identifiers requirement-framing, investigation-report, technical-recommendation, then blocked recommendation at G5-INPUT with accepted investigation-report, review-package, validation-report, technical-design; publication is pending and the run waits for a human | runs/run-437e2f765e4b state.json and recommendation failure envelope, read in this run | high |
| `E-011` | Manifest reads: business-analyst outputs requirement-framing; context-agent outputs investigation-report and accepts framed-objective, research-brief, investigation-question, research-question; tech-lead outputs technical-recommendation and accepts investigation-report, review-package, validation-report, technical-design; documentation accepts implementation-report, validation-report, review-package, deployment-status; framed-objective appears in no output declaration and in no runtime file | agents manifests of the four agents and a text search across manifests and runtime, read in this run | high |
| `E-012` | The profile routing table has seven rows; the sole input of four rows (decision-support, external-research, change-review, framework-release) is rejected by the entry agent when tested with the runtime's own contract function; the other three rows each carry at least one accepted type | config/self-hosting-profile.md and scratch script profile.py in the mirror | high |
| `E-013` | In the mirror, planning with problem-statement, investigation-question, and validation-report was accepted, so an up-front mislabelled type is a workaround that clears a downstream guard without being the artifact it claims to be; only plan acceptance was observed | Mirror run, plan command | high |
| `E-014` | The test module for the earlier refactor hand-off defect records that a per-edge check over every workflow edge was deliberately deferred and that thirteen mismatched edges remained after that repair, matching E-005 | tests/test_agent_input_contracts.py docstring read in this run | high |
| `E-015` | The agent loader rejects a manifest whose version differs from its registry record, so a manifest change forces a coordinated version change | runtime/framework_runtime.py, load_agent, read in this run | high |
| `E-016` | After all diagnostics the repository working tree status was identical to its status before them; the only writes were in the scratch mirror and scratch scripts; the absence of changes was confirmed by comparing the two status listings | Version control status taken before and after | high |

## Impact Assessment

- User impact: An operator running the investigate, research, review-pull-request, or release command cannot finish the run without foreknowledge of the guard: investigate and research always stop at 3 phases; the others stop at 1 or 2 unless the right extra type was supplied up front. Operators of fix-bug, refactor, and the code-quality scan are not affected.
- Business impact: No business impact statement was supplied; severity rests on technical impact alone and the question is routed to the product owner.
- Technical impact: Correctness of the framework's own contract: 13 of 29 declared hand-offs are undispatchable under G5-INPUT although the framework declares every phase dispatchable, and 4 of 7 profile rows cannot start a run. A stalled run also fails the self-hosting completion rule. No wrong result is produced and no data is lost; the failure is a visible block, with a workaround that needs advance knowledge and mislabels an input (`E-013`).
- Blast radius: The runtime guard and upstream hand-off path; the agent manifests and registry records of planner, architect, context-agent, tech-lead, documentation, and reviewer as consumers of blocked hand-offs and business-analyst, reviewer, and tech-lead as entry agents of rejected profile rows; the Phase Models of five workflows (investigate, research, review-pull-request, release, and implement-feature when entered through a type the architect does not accept); the self-hosting profile routing table and its router; the self-hosting verifier through stalled runs; the bundled payload mirror of all of these; consumer repositories holding framework copies, not observed. Persisted bad data: the committed stalled investigate run, which holds three completed artifacts and two pending phases and fails the completion rule while it stays on disk.

## Root Cause Analysis

- Root cause statement: Producer output identifiers and consumer accepted-input identifiers are declared independently with no authoritative mapping from a Phase Model Input column to an identifier, so the runtime offers each artifact under a name that the consuming agents' contracts at 13 hand-offs do not list, and the profile independently names entry types no entry agent lists.
- Why detection failed earlier: Manifest, registry, and Phase Model verifiers check each agent or table alone and no check composes a Phase Model edge with the producer's output and the consumer's accepted list; the one earlier repair of this class recorded the per-edge check as deliberately deferred and left thirteen mismatches, and the profile's input types were never tested against the entry agent.

### Causal Chain

| ID | Step | Claim | Evidence | Confidence |
|---|---|---|---|---|
| `C-001` | Independent declarations | Each manifest declares its output and accepted identifiers on its own, and the Phase Model Input column names files, so nothing ties a hand-off to an accepted identifier | `E-004`, `E-011` | high |
| `C-002` | Offer under producer name | The runtime offers the upstream artifact under the producing manifest's output identifier, or the file stem | `E-002` | high |
| `C-003` | Guard narrows and requires a listed type | G5-INPUT discards types the consumer does not declare and, for a menu contract, requires one accepted type; optional-only types do not count | `E-003` | high |
| `C-004` | Mismatch at 13 edges | For 13 of 29 consecutive hand-offs the offered identifier is absent from the consumer's accepted list, in one case (execution-plan at the architect) only optional | `E-005`, `E-011`, `E-014` | high |
| `C-005` | Supplied inputs rescue only some chains | Entry-supplied types survive into later pools and rescue fix-bug, refactor, and some implement-feature edges, but no entry type of investigate or research is accepted by the later consumers | `E-006`, `E-009`, `E-013` | high |
| `C-006` | Profile entry mismatch | Four of seven profile rows name a sole entry input the entry agent rejects, an independent instance of the same missing mapping | `E-007`, `E-012` | high |
| `C-007` | Observed block | The consuming phase blocks at G5-INPUT with the accepted list in its reason, its successors stay pending, and the run stalls | `E-008`, `E-010` | high |

## Fix Strategy

- Proposed fix: Make every Phase Model hand-off deliver the upstream artifact under an identifier the consuming agent accepts, for all 13 mismatched edges and not only the four reported, and make each profile row name an entry type its entry agent accepts, while an input type no agent accepts is still rejected. The change is conditional on the architect settling where the mapping lives, which also decides version and registry changes (`E-015`). Add an automated check over every declared workflow edge and profile route that needs no model. The committed stalled run stays untouched; its disposition is a gate-owner decision.
- Alternative options: Declare the upstream identifiers in each consuming manifest, which changes agent versions and registry records and widens each accepted menu; or add one runtime mapping from an output identifier to an accepted abstract type, which is one change but adds a rule the manifests do not state; or require operators to supply the extra types up front, which hides the defect and mislabels inputs and is not recommended.
- Regression risk: high
- Regression scope: Every workflow whose hand-offs are changed, because guard G5-INPUT is shared by all phases; the sibling pools already passing, such as refactor and fix-bug, because widening an accepted menu changes what narrowing keeps; manifest versions and registry records because the loader compares them; the bundled payload mirror because it copies the same files; the verifiers and tests that pin the profile table and the accepted menus.

## Validation Plan

- Verification steps: In a scratch mirror, repeat the reproduction with the same single entry type per workflow and confirm that every consecutive hand-off of investigate and research, and of the other three affected workflows, passes G5-INPUT once its predecessor's artifact is committed, that each profile row plans without a block at the entry phase, and that a supplied type no agent declares is still rejected.
- Regression tests added: A per-edge test over every active workflow that composes the Phase Model edge, the producer's output identifier, and the consumer's accepted list with the real contract function; a profile test that plans each routing row's entry types against the entry agent; a negative test for an undeclared type; and a producer-existence check for accepted identifiers that are not operator request types.
- Monitoring signals after release: Any run whose work item is blocked at G5-INPUT with the reason awaiting a dependency output after its predecessor completed; the count of blocked hand-offs from the edge test, expected to be zero.

## Closure

- Resolution summary: None identified.
- Linked PR and release: None identified.
- Prevention actions: Run the per-edge and profile-route checks as part of manifest and registry verification so a producer or consumer identifier cannot change alone.

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| `Q-001` | Where should the mapping live: consuming manifests, a runtime alias, the Phase Model, or a combination, and which version and registry changes follow; the guard itself behaves as documented, so the cause may be placed on either side and this alternative is not eliminated | no | architect | `C-001`, `C-004` |
| `Q-002` | Is relying on persisting entry-supplied types to rescue later phases an intended design, or an accident the repair should remove | no | architect | `C-005` |
| `Q-003` | What is the business impact of undispatchable investigate, research, review, and release commands; none was supplied | no | omn-product-owner | `C-007` |
| `Q-004` | Only guard G5-INPUT was measured; whether other guards, validators, and gates then pass for every repaired edge was not observed | no | omn-qa | `C-004`, `C-007` |
| `Q-005` | What becomes of the committed stalled investigate run, which fails the completion rule while it remains; the self-hosting verifier was not run in this analysis, and the claim that all 37 phases are dispatchable was not tested | no | omn-tech-lead | `C-007` |
