# Scope Definition — Memory Token Optimizer Command

```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0006
  featureName: Memory Token Optimizer Command
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/omt-01-feature-request.md
    - type: change-request
      reference: runs/inputs/omt-01-change-request.md
    - type: business-intent
      reference: runs/inputs/omt-01-business-intent.md
    - type: architecture-context
      reference: runs/inputs/omt-01-architecture-context.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 10
  inputDigest: sha256:39be708b47d19eb28667e5e4c7785813
  contextDigest: sha256:c5cc1c3bdd1db9b2d550e98fd7f931ed
```

## Metadata

- Feature name: Memory Token Optimizer Command
- Requested by: vuhoangcao
- Business goal: Put a control on the per-run cost of the framework's own durable knowledge, which currently only grows.
- Target outcome: An operator can reduce the recurring token cost of the knowledge surfaces, sees exactly what would change before it changes, and can undo it afterwards.
- Scope decision date: 2026-08-28

## Business Context

- Problem statement: Memory, context, and standing instruction files are read into the context slice of every dispatch, so their size is a cost paid per run and by every agent a run dispatches. That cost rises with every increment that records a decision, a standard, or a known issue, and no phase, gate, or command currently asks whether those files carry words that carry no rule.
- Value hypothesis: Density in a file read once per run has a return that density in a file read once does not. Reducing the recurring surface lowers the cost of every future run without reducing what the framework knows.
- Affected users: Operators who start runs, and every agent dispatched by a run, because each receives the knowledge surfaces in its context slice.
- Success measure: A measured reduction in the token cost of the knowledge surfaces, with zero rules, constraints, or identifiers lost and zero files overwritten without a recoverable pre-image.

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | An operator entry point that reduces the token cost of the durable knowledge surfaces and reports what it did | The requested capability; nothing in the framework offers it today | Must |
| `S-002` | The entry point reports its proposal without modifying any file unless the operator explicitly asks for modification | The surfaces are trusted by later runs without re-reading, so an unreviewed rewrite is the principal hazard | Must |
| `S-003` | Every candidate rewrite is judged against its original by a rule the framework runs, and a candidate that fails is discarded with the failure named | The business intent permits the framework to claim only what it can check | Must |
| `S-004` | Every modification is recoverable: a pre-image is written before the modification and a recorded command puts it back | Reversibility is what makes an operator's review recoverable from being wrong | Must |
| `S-005` | Generated and evidence surfaces are unreachable by the entry point regardless of what the operator asks for | Rewriting the record of what the framework did would falsify the evidence a routed change resolves against | Must |
| `S-006` | The entry point states, in its own contract, which guarantee is machine-checked and which is not | A capability that overstates its guarantee is worse than none, given what it rewrites | Must |
| `S-007` | The offline surfaces of the entry point work with no provider credential and no client library installed | An operator must be able to see the scope and undo a pass without provisioning anything | Should |
| `S-008` | The entry point carries an active discovery record and appears in the command index alongside the existing contracts | An entry point the framework cannot resolve is not an entry point | Must |
| `S-009` | Each accepted change proposal is indexed against the run that carried it | Requested with the capability; a reader can reach the evidence without opening every proposal | Should |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Running an optimization pass over this repository's own knowledge surfaces | Adding the capability and using it are separate changes; the second carries its own review of its own diffs | An operator decides to run it and routes that as its own change |
| `X-002` | Deciding what belongs in memory or context | Owned by `memory/memory-governance.md` and the lifecycles that add and retire knowledge | A governance change moves that ownership |
| `X-003` | Rewriting source code, agent contracts, registries, workflow specifications, or command specifications | None is a knowledge surface loaded per run, so none carries the recurring cost that motivates this | Evidence that one of them is loaded per run |
| `X-004` | Proving that reworded prose means the same thing | Not decidable by the framework; asserting it would overstate the guarantee | A checkable equivalence method exists |
| `X-005` | Running the pass automatically, on a schedule, or inside another lifecycle | Every pass rewrites trusted surfaces and must be an operator's explicit act | Sustained evidence that reviewed passes are uneventful |
| `X-006` | A new workflow, phase, gate, agent, or artifact validator for this entry point | The claim it makes is one an existing lifecycle already holds to account | The claim changes into one no existing lifecycle covers |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | The entry point resolves through framework discovery, and every entry point on disk carries a discovery record | `S-008` | Run the registry coverage verifier and read check `C1` | Must |
| `A-002` | Invoking the entry point with no modification flag leaves every file in scope byte-identical, and writes its proposal elsewhere | `S-002` | Compare digests of every in-scope file before and after an unmodified invocation | Must |
| `A-003` | A candidate that drops a heading, a fenced block, a table row, a link target, an inline code span, or a declared identifier is discarded, and the discarded reason names what was dropped | `S-003` | Execute the judging rule against constructed candidates that each drop one of those, and confirm each is refused with the reason named | Must |
| `A-004` | A candidate that changes nothing is accepted by the judging rule | `S-003` | Execute the judging rule with a document against itself and confirm no violation is reported | Must |
| `A-005` | Every modified file has a pre-image on disk and a recorded digest pair, and the recorded undo restores it | `S-004` | Inspect the session record after a modifying invocation, then execute the undo and compare digests | Must |
| `A-006` | A path under run evidence, dated reports, or change proposals is refused with the denial recorded, including when named explicitly | `S-005` | Invoke the scan against each denied location and read the recorded disposition | Must |
| `A-007` | The entry point's contract states the checked guarantee and the unchecked one as separate claims | `S-006` | Inspection of the contract at the Scope Gate and the Review Gate | Must |
| `A-008` | The scope and undo surfaces complete successfully with no provider credential and no client library present, and the modifying surface fails before reading any file when they are absent | `S-007` | Execute all three in an environment with neither and record the exit behaviour | Should |
| `A-009` | All framework verifiers pass after the change at their prior counts plus the one added entry point | `S-001`, `S-008` | Run the registry coverage, validator, recovery, and self-hosting verifiers and compare to the recorded baseline | Must |
| `A-010` | Each accepted change proposal is reachable from the index together with the run that carried it | `S-009` | Inspection of the index against the proposal set at the Review Gate | Should |

## Constraints and Dependencies

- Business constraints: No new obligation on an operator who never invokes the entry point. No degradation of any existing framework guarantee.
- Regulatory or policy constraints: The governance profile forbids modifying run evidence, dated reports, and change proposals; the entry point inherits that boundary rather than restating it as a preference.
- Delivery constraints: No change to any existing lifecycle, phase, gate owner, role contract, or artifact validator. A change requiring one would be larger than this change claims to be.
- External dependencies: A provider client library and resolvable credentials, required only by the modifying surface at the point it makes a request. Neither is present in the delivery environment, which bounds what can be demonstrated rather than what can be delivered.

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | The entry point reuses an existing lifecycle rather than introducing one | The claim it makes — that wording changed and meaning did not — is the invariant claim an existing lifecycle exists to hold to account, and a second lifecycle asserting the same thing would be a second answer to a settled question | Removes a phase model, gate rows, role manifest entries, and a validator from the change | omn-product-owner |
| `D-002` | Non-modifying invocation is the default; modification requires an explicit flag | The surfaces rewritten are trusted by later runs without re-reading, so the failure mode of an unreviewed rewrite is silent and durable | Adds a step to the operator's path and removes the accidental-overwrite hazard | omn-product-owner |
| `D-003` | The checked guarantee is structural and identifier-level, and the contract says so rather than implying more | The business intent permits the framework to claim only what it can check, and the reviewed difference record is offered as the control for the rest | Bounds `S-003` and creates `X-004` | omn-product-owner |
| `D-004` | Using the capability on this repository is excluded from this change | A pass over the framework's own knowledge produces its own difference record needing its own review; bundling it would put two decisions behind one acceptance | Creates `X-001`; the capability ships unexercised against production surfaces | omn-product-owner |
| `D-005` | Denial of generated and evidence surfaces binds regardless of operator argument | An operator who can widen the pass into run evidence can falsify the record a routed change resolves against, and no legitimate use needs that | Removes an operator affordance deliberately | omn-product-owner |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | Should a later change add an advisory threshold that reports when the knowledge surfaces have grown past a stated size, so growth is noticed rather than discovered? | no | omn-product-owner | A subsequent increment |
| `Q-002` | The modifying surface cannot be exercised end to end in the delivery environment, which has no provider client library and no credential. Who accepts the first live pass, and against which surfaces? | no | omn-tech-lead | Before `X-001` is routed as its own change |

## Handoff

- Downstream owner: planner, for the `execution-planning` phase
- Gate: Scope Gate
- Evidence for the gate: This artifact; the four supplied inputs and their recorded digests; the classification and routing decision recorded in the change request.
- Deferred to downstream: The judging rule's specific invariants and thresholds, the session record's layout, the module's command surface, task breakdown, sequencing, and effort. This artifact fixes what must be true, not how.
