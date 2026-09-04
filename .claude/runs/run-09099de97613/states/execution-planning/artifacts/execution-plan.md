```yaml
plan:
  planId: OMT-01-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/omt-01-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:2719daabacb06dca76da89e24b04daed
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
```

## Executive Summary

The framework gains an operator entry point that rewrites its durable knowledge surfaces — memory, context, and the standing instruction files — to a lower token cost without changing what they instruct, together with the runtime module that performs the pass and the discovery record that makes the entry point resolvable. The outcome that defines success is a measured reduction in the recurring cost of those surfaces with zero rules, constraints, or identifiers lost and zero files modified without a recoverable pre-image. The work decomposes into nine tasks across six execution waves, opening in parallel with the current-state inventory (T-001), the judging rule (T-003), the request path (T-004), and the proposal index (T-008). The highest-impact risk is R-002: the judging rule is the only mechanical defence against a candidate that reads plausibly and has quietly dropped a rule, so an incomplete invariant set would let a silent loss through into surfaces that every later run trusts without re-reading. Plan status is complete; assumption A-002 is unconfirmed and holds T-004's demonstration, not its delivery, because the delivery environment carries no provider client library or credential.

## Business Objectives

1. Operators receive a control on the recurring cost of the framework's own knowledge, which today only grows. Measured by a reduction in the recorded token cost of the knowledge surfaces after a reviewed pass. Traces to S-001, S-003, S-005.
2. Operators can see exactly what a pass would change before anything changes, and can undo it afterwards. Measured by an invocation that leaves every in-scope file byte-identical while producing a difference record, and by a recorded undo that restores a modified file. Traces to S-006, S-009.
3. The framework's existing guarantees survive the addition intact, so an operator who never invokes the entry point carries no new obligation and no new risk. Measured by the framework verifiers reporting their prior results plus the one added entry point. Traces to S-010, S-013.
4. A reader of the governance record can reach the run evidence behind any accepted change without opening every proposal to find it. Measured by each accepted proposal appearing in the index against the run that carried it. Traces to S-004.

## Technical Objectives

1. Every candidate rewrite is judged against its original by a rule the framework executes, and a candidate that drops a heading, a fenced block, a table row, a link target, an inline code span, a declared identifier, or a list item is refused with the loss named. Verified by executing the rule against constructed candidates that each drop one class of content, and against a document compared with itself. Traces to business objective 2, and to S-014, which is why acceptance may not rest on the producing model's own assurance.
2. Discovery refuses every generated and evidence surface by path, and the refusal binds regardless of the arguments an operator supplies. Verified by invoking discovery against each denied location and reading the recorded disposition. Traces to business objective 3.
3. No modification reaches disk without a pre-image written first and a digest pair recorded, and the recorded undo restores the pre-image or refuses and says why. Verified by inspecting a session record after a modifying invocation and executing the undo. Traces to business objective 2.
4. The offline surfaces complete with no provider credential and no client library present, and the modifying surface fails before reading any file when either is absent. Verified by executing all three surfaces in an environment carrying neither. Traces to business objective 3, and to A-002.
5. The entry point resolves through framework discovery without a new workflow, phase, gate, role manifest entry, or artifact validator. Verified by the registry coverage verifier reporting its prior phase, owner, skill, and gate counts unchanged with one added command record. Traces to business objective 3.

## Scope

### In Scope

- An operator entry point that reduces the recurring token cost of the knowledge surfaces and reports what it did (S-001, S-003; delivered by T-002, T-004, T-005, T-006)
- A default invocation that modifies nothing and produces a reviewable difference record instead (S-006; delivered by T-005)
- A mechanical judging rule that refuses a candidate which drops content, naming what was dropped (S-007, S-008; delivered by T-003)
- Recoverability: a pre-image and a digest pair for every modification, and an undo that uses them (S-009; delivered by T-005)
- Denial of generated and evidence surfaces, binding regardless of operator argument (S-010; delivered by T-002)
- A command contract that states the checked guarantee and the unchecked one as separate claims (S-011; delivered by T-006)
- Offline surfaces usable with no credential and no client library present (S-012; delivered by T-002, T-005)
- An active discovery record and an index entry for the new entry point (S-002; delivered by T-007)
- An index of accepted change proposals against the runs that carried them (S-004; delivered by T-008)
- Confirmation that existing framework verification results are unchanged plus the added entry point (S-013; verified by T-009)

### Out of Scope

- Executing an optimization pass over this repository's own knowledge surfaces. Excluded because a pass produces its own difference record requiring its own review, and bundling it would place two decisions behind one acceptance.
- Deciding what belongs in memory or context. Excluded because that ownership sits with the governance document for memory and with the lifecycles that add and retire knowledge.
- Rewriting source code, role contracts, discovery registries, workflow specifications, or command specifications. Excluded because none is a knowledge surface loaded per dispatch, so none carries the recurring cost that motivates the change.
- Proving that reworded prose means the same thing. Excluded because it is not decidable by the framework, and asserting it would overstate what the change can keep.
- A new workflow, phase, gate, role, or artifact validator for the entry point. Excluded because the claim the entry point makes is the invariant claim an existing lifecycle already holds to account.

### Deferred

- An advisory threshold that reports when the knowledge surfaces have grown past a stated size. Brought into scope when a subsequent increment establishes what that size should be; the current change measures cost but sets no target for it.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The invariant classes named in technical objective 1 cover the loss modes that matter for these documents; a loss that escapes all of them is visible in the difference record a reviewer reads | S-007, S-014 | The judging rule admits a silent loss, and the guarantee stated in the contract is narrower than the contract claims; the invariant set extends and T-003 re-executes | architect |
| A-002 | A provider client library and resolvable credentials are available at the time an operator first runs a modifying pass | S-012 | The modifying surface cannot be demonstrated end to end; delivery is unaffected because the failure path is itself in scope and testable, but the first live pass has no recorded evidence until an environment exists | omn-qa |
| A-003 | Adding a command record whose primary workflow is already carried by another contract needs no change to that workflow, its phases, its gates, or its owning roles | S-013 | T-007 expands to carry a phase model, gate rows, and role manifest changes, and the exclusion forbidding a new workflow is revisited with omn-product-owner | architect |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | technical | An operator invokes the modifying surface without reading the difference record | A trusted knowledge surface is rewritten unreviewed, and the loss is discovered by a later run behaving differently rather than by a reader | medium | T-005, T-006 | The default invocation modifies nothing, so reaching a modification requires a deliberate second act; the contract states the review step as part of the operator path | omn-dev-1-implement |
| R-002 | technical | The judging rule's invariant set is incomplete, and a candidate that drops a rule expressed only in prose passes it (A-001 false) | A silent loss enters a surface every later run trusts without re-reading, and the contract's guarantee is wider than what is checked | medium | T-003, T-006 | T-003 demonstrates refusal per loss class rather than asserting coverage; T-006 states the checked guarantee and the unchecked one separately so no reader infers more than holds | architect |
| R-003 | security | An operator points the pass at run evidence, dated reports, or change proposals | The record a routed change resolves against is falsified, and the governance layer's verification becomes meaningless | low | T-002 | Denial binds by path inside discovery rather than by argument validation, so no argument reaches the denied surface; T-002 demonstrates refusal at each denied location | omn-dev-1-implement |
| R-004 | operational | A modifying pass is interrupted, or a candidate is accepted and later judged wrong by a reviewer | Files are left rewritten with no route back to what they said | low | T-005 | The pre-image is written before the modification, not after; the undo refuses a file changed since the pass rather than discarding the later edit | omn-dev-1-implement |
| R-005 | dependency | The provider client library or credentials are absent when a pass is attempted (A-002 false) | No modifying pass can run | medium | T-004, T-009 | The failure occurs before any file is read and names the remediation; the offline surfaces remain usable, so scope and undo do not depend on provisioning | omn-qa |
| R-006 | requirement | Adding a command record disturbs an existing workflow, gate, or role contract (A-003 false) | The change becomes a lifecycle change, which the scope excludes | low | T-007, T-009 | T-007 reuses a workflow already shared by two other contracts; T-009 compares every verifier result against the recorded baseline before acceptance | architect |
| R-007 | delivery | The framework verifiers do not return to their baseline after the change | The change cannot be accepted, and the fault is found late | low | T-009 | T-009 runs after registration and compares to a baseline recorded before the work began, so a divergence names what moved | omn-tech-lead |

## Task Breakdown

### T-001 Record the current-state inventory of the knowledge surfaces

- Owner: architect
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-005
- Status: ready
- Description: The set of files that are loaded per dispatch is enumerated with their sizes, and the boundary between a knowledge surface and an artifact a run writes is stated, so that discovery has a definition to implement rather than a convention to infer.
- Acceptance Criteria:
  - Every file in the candidate set is listed with its size and the root that supplies it
  - The rule separating a knowledge surface from a written artifact is stated in one sentence and covers every listed file
- Gate: none

### T-002 Build discovery and the denial rule

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-010, S-012
- Status: ready
- Description: Discovery enumerates the eligible files under the supplied roots and records, for every file it refuses, the reason it was refused; denial of generated and evidence surfaces binds regardless of the arguments supplied.
- Acceptance Criteria:
  - Invoking discovery against a denied location refuses it and records the denial reason
  - A refusal reason is recorded for every skipped file, including files below the size floor and files declaring themselves generated
  - Discovery completes with no provider credential and no client library present
- Gate: Review Gate

### T-003 Build the invariant judging rule

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: none
- Traces to: S-007, S-008, S-014
- Status: ready
- Description: A candidate is judged against its original and refused when it drops a heading, a fenced block, a table row, a link target, an inline code span, a declared identifier, or a list item, or when it falls below the floor that separates compression from deletion; a refusal names what was lost.
- Acceptance Criteria:
  - A document judged against itself reports no violation
  - A candidate constructed to drop one class of content is refused, and the refusal names that class, for every class the rule covers
  - A refused candidate leaves its original byte-identical
- Gate: Review Gate

### T-004 Build the compression request path

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-003, S-012
- Status: assumption-dependent
- Description: A request carrying the document and the compression instruction is issued to the configured provider endpoint, and its response is returned as a candidate; a declined, truncated, or failed request is recorded against that file and leaves the original untouched.
- Acceptance Criteria:
  - A missing client library or unresolvable credentials fails before any file is read and names the remediation
  - A declined or truncated response is recorded as a failure for that file and the pass continues
  - The instruction states what may be removed, what must be rewritten, and what may never change
- Gate: Review Gate

### T-005 Build the session record and the undo

- Owner: omn-dev-1-implement
- Complexity: M (confidence: high)
- Depends on: T-002, T-003, T-004
- Traces to: S-006, S-009
- Status: ready
- Description: A pass writes a session record carrying the per-file token delta, the verdict, a difference record per accepted candidate, and a digest pair; a modification writes the pre-image first, and the undo restores it or refuses a file changed since the pass.
- Acceptance Criteria:
  - The default invocation leaves every in-scope file byte-identical and writes its candidates elsewhere
  - Every modified file has a pre-image on disk and a recorded digest pair
  - The undo restores a modified file, and refuses with a stated reason where the file changed after the pass
- Gate: Review Gate

### T-006 Author the command contract

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-002, T-003, T-005
- Traces to: S-001, S-011
- Status: ready
- Description: The contract states the entry point's purpose, its inputs, the lifecycle it routes to, the operator path from scan to undo, the invariants it checks, and the guarantee it does not check, so a reader infers no more than the change can keep.
- Acceptance Criteria:
  - The checked guarantee and the unchecked guarantee appear as separate statements, and the unchecked one names what stands in for it
  - The operator path names every command in order, including the review step before any modification
  - The denial boundary is stated with the reason it exists
- Gate: Review Gate

### T-007 Register the entry point in discovery

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-006
- Traces to: S-002
- Status: ready
- Description: The entry point holds an active discovery record naming the lifecycle it routes to, and appears in the operator-facing index alongside the existing contracts, so the framework can resolve it.
- Acceptance Criteria:
  - The discovery record resolves to an active lifecycle record and to the contract on disk
  - The index lists the entry point, and the stated contract count matches the contracts on disk
- Gate: Review Gate

### T-008 Index accepted change proposals against their runs

- Owner: omn-documentation
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-004
- Status: ready
- Description: The governance profile carries an index recording each accepted change proposal with the run that carried it, stated as a directory rather than as a second authority, so discovery of proposals remains where it is.
- Acceptance Criteria:
  - Every accepted proposal appears with its change class, routed command, and run
  - The index states that it neither admits a proposal nor exempts one
  - The profile continues to parse, and routing resolves unchanged
- Gate: Review Gate

### T-009 Confirm the framework verifiers return to baseline

- Owner: omn-qa
- Complexity: S (confidence: high)
- Depends on: T-007, T-008
- Traces to: S-013
- Status: ready
- Description: Every framework verifier is executed after the change and its result compared against the baseline recorded before the work began, so a divergence names what moved rather than being discovered later.
- Acceptance Criteria:
  - Coverage, validator, and recovery verification report their baseline results with one added entry point and no other count changed
  - Any divergence from baseline is recorded with the check that moved and the reason
- Gate: Verification Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | produces-consumes | Discovery implements the surface boundary the inventory states |
| T-002 | T-005 | produces-consumes | The session record iterates the files discovery yields |
| T-003 | T-005 | produces-consumes | The verdict recorded per file is the judging rule's decision |
| T-004 | T-005 | produces-consumes | The candidate the session record judges and writes comes from the request path |
| T-002 | T-006 | contract | The contract states the denial boundary discovery implements |
| T-003 | T-006 | contract | The contract states the invariants the judging rule checks, and only those |
| T-005 | T-006 | produces-consumes | The contract states the operator path the session record and undo define |
| T-006 | T-007 | produces-consumes | The discovery record names the contract path, so the contract exists first |
| T-007 | T-009 | verification | Baseline comparison validates the registered entry point |
| T-008 | T-009 | verification | Baseline comparison validates that the profile still parses and routes |
| Operating environment | T-004 | external | A modifying pass waits on a client library and resolvable credentials at invocation time |

### 8.2 External Dependencies

| Responsible party | What is needed | Blocks |
|---|---|---|
| Operating environment | A provider client library and resolvable credentials, at the time a modifying pass is invoked | T-004 |

### 8.3 Implementation Order

- Wave 1: T-001, T-003, T-004, T-008
- Wave 2: T-002
- Wave 3: T-005
- Wave 4: T-006
- Wave 5: T-007
- Wave 6: T-009

## Suggested Workflow

Selected workflow: implement-feature

Selected because: the change adds a capability, a contract, and a discovery record the framework did not have, which is the class the governance profile routes to this lifecycle; the delivered entry point itself routes to `refactor`, and the two are separate questions.

| Phase | Tasks |
|---|---|
| scope-and-acceptance | T-001 |
| execution-planning | T-001 |
| solution-design-and-risk-assessment | T-001, T-003 |
| implementation | T-002, T-003, T-004, T-005, T-006, T-007, T-008 |
| quality-review | T-009 |
| documentation-and-release-handoff | T-006 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| architecture-analysis | T-001 | architect | expert |
| implementation-delivery | T-002, T-003, T-004, T-005, T-007 | omn-dev-1-implement | expert |
| documentation | T-006, T-008 | omn-documentation | expert |
| quality-verification | T-009 | omn-qa | expert |
| code-review | T-009 | omn-dev-2-reviewer | expert |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | skills/architecture/system-design.md | T-001 | advanced |
| S03 | skills/testing/test-strategy.md | T-003, T-009 | advanced |
| S06 | skills/error-handling/error-handling-standards.md | T-004 | advanced |
| S07 | skills/security/secure-coding.md | T-002 | advanced |
| S11 | skills/git/git-collaboration.md | T-006, T-008 | intermediate |
| S12 | skills/logging/logging-standards.md | T-005 | intermediate |

## Acceptance Criteria

1. The recorded token cost of the knowledge surfaces falls after a reviewed pass, measured rather than estimated. Verified by the per-file delta in the session record. Traces to business objective 1.
2. No rule, constraint, or declared identifier is lost by any accepted candidate. Verified by the judging rule's verdict per file and by the difference record a reviewer reads. Traces to business objective 1.
3. An invocation that has not been told to modify leaves every in-scope file byte-identical. Verified by comparing digests before and after. Traces to business objective 2.
4. Every modification is reversible from what the pass itself wrote. Verified by executing the undo against a modifying session and comparing digests to the pre-images. Traces to business objective 2.
5. The framework verifiers report their baseline results with one added entry point and no other count changed. Verified by the recorded comparison in T-009. Traces to business objective 3.
6. Every accepted change proposal is reachable from the index with the run that carried it. Verified by comparing the index against the proposal set. Traces to business objective 4.

## Definition of Done

- [ ] All plan acceptance criteria are verified with recorded evidence
- [ ] All mandatory gates are approved with owners recorded
- [ ] Task acceptance criteria are satisfied or formally waived
- [ ] Assumptions are confirmed or converted to recorded decisions
- [ ] Risks are closed or accepted with named owners
- [ ] Open questions are closed or explicitly accepted
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Who accepts the first modifying pass over this repository's own knowledge surfaces, and against which files, given that the delivery environment cannot demonstrate one? | no | omn-tech-lead | T-004, A-002 |
| Q-002 | Should the invariant set extend to prose-level obligations, and if so by what checkable rule, or does the difference record remain the only control for them? | no | architect | T-003, A-001, R-002 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 | T-006 |
| S-002 | T-007 |
| S-003 | T-004 |
| S-004 | T-008 |
| S-005 | T-001 |
| S-006 | T-005 |
| S-007 | T-003 |
| S-008 | T-003 |
| S-009 | T-005 |
| S-010 | T-002 |
| S-011 | T-006 |
| S-012 | T-002, T-004 |
| S-013 | T-009 |
| S-014 | T-003, A-001 |
