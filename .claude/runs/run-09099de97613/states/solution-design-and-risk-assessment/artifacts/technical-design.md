```yaml
design:
  designId: OMT-01-technical-design
  changeReference: OMT-01
  sourceInputs:
    - type: change-request
      reference: runs/inputs/omt-01-change-request.md
    - type: business-intent
      reference: runs/inputs/omt-01-business-intent.md
    - type: architecture-context
      reference: runs/inputs/omt-01-architecture-context.md
    - type: execution-plan
      reference: runs/run-09099de97613/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002]
  consumesPlan: runs/run-09099de97613/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:1bb78e10f8fa731f5cbf36b2ba77d72c
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: OMT-01
- Author: architect
- Reviewers: omn-tech-lead, omn-dev-2-reviewer, omn-qa
- Last Updated: 2026-08-28

## Objective

- Desired outcome: The framework carries an operator entry point that lowers the recurring token cost of its durable knowledge surfaces without changing what those surfaces instruct, and carries the runtime module that performs the pass.
- Architectural objectives: Add the capability without adding a lifecycle surface, so the framework's phase, gate, owner, and validator counts move by nothing (S-013). Keep the destructive path unreachable by accident and reversible when reached (S-006, S-009). Confine the new external dependency to the one code path that needs it (S-012). Make the accepted guarantee mechanically decidable, so the framework claims only what it checks (S-007, S-011, S-014).
- In scope: The entry-point contract, the runtime module that executes it, the discovery record that resolves it, and the proposal index the change request names.
- Out of scope: Executing a pass over this repository's own knowledge surfaces; deciding what belongs in memory or context; rewriting source, role contracts, discovery registries, or lifecycle specifications; proving semantic equivalence of reworded prose; a new lifecycle surface of any kind.

## Requirements Summary

- Functional requirements: An entry point that enumerates the knowledge surfaces, proposes a denser rewrite of each, judges each candidate against its original, and reports the outcome (S-001, S-003). A default invocation that modifies nothing (S-006). A candidate that loses content refused with the loss named (S-007, S-008). A pre-image and digest pair per modification, with a recorded undo (S-009). Denial of generated and evidence surfaces that binds regardless of argument (S-010). An active discovery record and an index entry (S-002). An index of accepted proposals against their runs (S-004).
- Non-functional requirements: The offline surfaces complete with no client library and no credential present, and the modifying surface fails before reading any file when either is absent (S-012). No existing framework guarantee regresses; verifier results move by the one added entry point and nothing else (S-013). The entry-point contract distinguishes the checked guarantee from the unchecked one (S-011).
- Acceptance criteria: Those recorded upstream in the approved scope definition and in the execution plan's Acceptance Criteria section, covering S-001 through S-014. This package adds none and narrows none.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | Ten command contracts hold active discovery records, and coverage check `C1` fails when a contract on disk carries no record | `registry/commands.yaml`; `runtime/verify_registry_coverage.py` |
| F-002 | Two contracts already share a primary workflow with another contract, so sharing is an established pattern rather than a new one | `registry/commands.yaml`; `commands/command-catalog.md` |
| F-003 | The `refactor` workflow declares five phases, and all five are dispatchable today | `workflows/refactor.md`; coverage check `C6` |
| F-004 | All thirty-seven declared phases across eight active workflows are dispatchable | coverage check `C6` |
| F-005 | No framework surface currently makes a network request or requires a provider credential; the runtime depends on the standard library and one YAML package | `pyproject.toml`; `runtime/` |
| F-006 | Run evidence, dated reports, and change proposals are excluded from the governance scope rule because rewriting them would falsify the record a routed change resolves against | `config/self-hosting-profile.md`, rules `SR-3` to `SR-5` |
| F-007 | The governance profile is parsed section by section by heading, so a section appended after the last parsed heading does not alter what parses | `runtime/self_hosting.py` |
| F-008 | Twenty-one markdown files across the memory root, the context root, and the standing instruction set are loaded per dispatch, totalling roughly sixty-five kilobytes | Inventory recorded by plan task T-001 |
| F-009 | A validated artifact may not name a model, vendor, or provider, and the framework's own path prefix is stripped before that scan | `runtime/artifact_lib.py`; `runtime/artifact_contract.py` |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The invariant classes in `D-002` cover the loss modes that matter for these documents; a loss escaping all of them is visible in the difference record a reviewer reads | The accepted guarantee is defined by that set, so its adequacy is the guarantee's adequacy | A silent loss reaches a trusted surface; the invariant set extends and the contract's stated guarantee narrows to match | omn-dev-2-reviewer at the Review Gate |
| A-002 | A client library and resolvable credentials exist at the time an operator first invokes a modifying pass | The compressing path cannot execute without them | The modifying path is undemonstrated; delivery is unaffected because its absence path is itself in scope, but the first live pass carries no recorded evidence | omn-qa |
| A-003 | Adding a contract whose primary workflow another contract already carries needs no change to that workflow, its phases, its gates, or its owning roles | `O-001` is chosen on exactly this basis | `O-001` collapses into `O-002`'s cost, and the exclusion forbidding a new lifecycle surface is revisited | architect, by executing coverage verification after registration |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | A command contract resolves to exactly one primary workflow, and that workflow holds an active discovery record | hard | `commands/README.md`; `registry/commands.yaml` |
| C-002 | structural | The change adds no workflow, phase, gate row, role manifest entry, or artifact validator | hard | Upstream scope exclusion `X-006` |
| C-003 | security | Run evidence, dated reports, and change proposals are never rewritten, whatever an operator asks for | hard | `F-006` |
| C-004 | quality-attribute | The framework asserts only guarantees it can decide mechanically; anything else is stated as unchecked | hard | Business intent, acceptance boundary |
| C-005 | operability | A new external dependency binds only the code path that needs it; every other surface keeps working without it | hard | `F-005`; upstream scope item `S-007` |
| C-006 | operability | No modification reaches disk without a recoverable pre-image written first | hard | Upstream scope item `S-004` |
| C-007 | compliance | No validated artifact of this run names a model, vendor, or provider | hard | `F-009` |
| C-008 | quality-attribute | Existing verifier results move by the one added contract and by nothing else | hard | Upstream statement `S-013` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `runtime/optimize_memory.py` | extension | `F-008`, `A-002`; the module that performs discovery, compression, judging, recording, and undo over the surfaces F-008 enumerates | Its own command surface: `scan`, `run`, `restore` | confirmed |
| M-002 | `commands/optimize-memory.md` | extension | `F-001`; a contract on disk must carry a discovery record, so the contract is half of an indivisible pair | Operator entry surface | confirmed |
| M-003 | `registry/commands.yaml` | contract-change | `F-001`, `F-002`, `A-003`; a new active record whose primary workflow is `refactor`, on the pattern F-002 records | Command resolution, read by `resolve_command` | confirmed |
| M-004 | `commands/command-catalog.md` | extension | `F-001`; the operator-facing index of the contracts F-001 counts | Reader-facing index only; nothing resolves against it | confirmed |
| M-005 | `commands/README.md` | behavior-change | `F-001`; the stated contract count becomes wrong when a contract is added and the count is not corrected | Reader-facing statement only | confirmed |
| M-006 | `config/self-hosting-profile.md` | extension | `F-007`; an appended index section, after the last parsed heading | None; `load_profile` reads named sections and this adds no parsed section | confirmed |
| M-007 | `workflows/refactor.md` | no-change-verified | `F-002`, `F-003`, `A-003`; a reader expects a shared workflow to change, and coverage verification decides that it does not | None | confirmed |
| M-008 | `runtime/framework_runtime.py` | no-change-verified | `F-003`, `F-004`; a reader expects a new entry point to need a context slice and a validator entry, and it does not, because it dispatches no phase of its own | None | confirmed |
| M-009 | `agents/` role manifests | no-change-verified | `F-003`, `A-003`; a reader expects a new capability to need an owning role, and the phases that carry it already have owners | None | confirmed |

### 5.2 Options Considered

| Option | Structural change | C-001 exactly one primary workflow | C-002 no new lifecycle surface | C-003 evidence immutability | C-004 no unverifiable guarantee | C-005 dependency confinement | Impact surface | Reuse leverage | Migration burden | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | A contract routing to the existing `refactor` workflow, plus a runtime module whose judging rule decides acceptance | satisfied: one record, `primaryWorkflow: refactor`, already active | satisfied: no phase, gate, role, or validator added | satisfied: denial binds inside discovery, not at argument parsing | satisfied: acceptance is the invariant set, and the contract states what it excludes | satisfied: the client library is imported inside the compressing path only | 6 modules changed, 3 verified unchanged | high: reuses five dispatchable phases, their gates, owners, and validators | none: no existing consumer changes | selected |
| O-002 | A dedicated `optimize-memory` workflow with its own phases, gates, artifact, and validator | satisfied: one record pointing at the new workflow | violated: adds five phases, gate rows with non-producing owners, role manifest entries, context slices, and a validator | satisfied by the same discovery denial | satisfied, at the cost of a second artifact contract asserting it | satisfied | 6 modules plus a phase model, a gate matrix, four role manifests, two registries, and a validator | none: duplicates a lifecycle that already holds this exact claim | high: every added surface becomes a permanent maintenance obligation | rejected: violates `C-002`, and duplicates the invariant claim `refactor` already owns |
| O-003 | No entry point; a maintenance script invoked outside the framework | not applicable: no contract exists to resolve | satisfied trivially | violated: nothing binds the denial, because nothing governs the script | violated: no contract states any guarantee, checked or otherwise | satisfied | 1 module | none: the framework gains no capability it can route, gate, or verify | none | rejected: violates `C-003` and `C-004`; the capability would sit outside every control that makes it safe |
| O-004 | The contract and module of `O-001`, with acceptance resting on the producing model's own assurance instead of a judging rule | satisfied | satisfied | satisfied | violated: the assurance is not decidable, and `S-014` records that it is worthless as an acceptance basis | satisfied | 6 modules changed | high, but spent on an unsafe path | none | rejected: violates `C-004`; a plausible-reading candidate that dropped a rule would be accepted silently |

### 5.3 Selected Approach

- Selected: `O-001`.
- Structural change: One new runtime module and one new contract, joined by one new discovery record whose primary workflow is one that already exists and is already dispatchable. Three reader-facing documents are corrected to match. No lifecycle surface is added, and three modules are recorded as verified unchanged so a reader is not left to assume it.
- Rationale: The claim the entry point makes — wording changed, meaning did not — is the invariant claim the `refactor` lifecycle exists to hold to account. `scope-invariants-and-risk-profile` states what may not change and `behavioral-validation` checks that it did not, which is the shape of this work rather than an approximation of it. Routing there costs one record. `C-001` permits it and `F-002` shows two contracts already do it. The acceptance rule lives in the module, where it is executable, rather than in prose, where it would be an assertion.
- Highest-scoring rejected alternative and why it lost: `O-002`. It satisfies every constraint except `C-002`, and it fails that one for nothing gained: its five new phases would restate an invariant claim the framework already models, and every new gate row, role manifest entry, context slice, and validator it introduced would be a permanent obligation carried to describe work an existing lifecycle already describes.
- Tradeoffs accepted: The entry point cannot express a phase the `refactor` workflow does not have. That is accepted because none is needed and because gaining one later is a smaller change than carrying five unused ones now. The framework gains its first external network dependency, confined by `C-005` to a single import site, so no existing surface acquires it.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | The entry point routes to the existing `refactor` workflow rather than to a workflow of its own | yes | `architecture-decision-record-D-001.md` |
| D-002 | Acceptance of a candidate is decided by a mechanical invariant check against the original, and the guarantee the contract states is exactly that check and no more | yes | `architecture-decision-record-D-002.md` |
| D-003 | Denial of generated and evidence surfaces is implemented inside discovery by path, not by validating operator arguments | no | None; a direct consequence of `C-003`, recorded here |
| D-004 | The default invocation modifies nothing, and modification requires an explicit second act | no | None; a direct consequence of `C-006` and upstream decision `D-002` |
| D-005 | The proposal index is appended after the last parsed heading of the governance profile, and states that it is a directory rather than an authority | no | None; a direct consequence of `F-007` |

## API and Data Model Impact

- API changes: One new discovery record in `registry/commands.yaml` (`M-003`), which is a contract change to command resolution in the additive direction only. Current shape: ten active records. Target shape: eleven, the new one identical in schema to the existing records and naming an already-active workflow. Compatibility approach: additive; `resolve_command` looks records up by identifier, so no existing lookup changes. Coexistence period: none required, because no record is replaced. Retirement condition: the record retires if the entry point is withdrawn, by setting its status rather than deleting it, per the registry's status vocabulary. Rollback position: remove the record and the contract file together; leaving one without the other fails coverage check `C1`, which is the intended detection.
- Contract compatibility notes: The module's own command surface (`M-001`) is new, so it has no compatibility obligation. The session record it writes is versioned by a schema identifier from its first revision, so a later reader can tell which shape it is reading.
- Schema or migration changes: None. No existing record, artifact, or run structure changes shape, and no data is migrated.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| A lifecycle that holds an invariant-preservation claim to account | `workflows/refactor.md` | reuse-as-is | Its five phases already state invariants, establish a safety net, implement, validate against the invariants, and record what was left; no phase is missing and none is unused |
| Structure-preserving change routing | `config/self-hosting-profile.md`, `structure-preserving-change` row | reuse-as-is | An operator's later use of the entry point classifies there without a new routing row |
| A shared primary workflow across two contracts | `/document` and `/test` records | reuse-as-is | Establishes the pattern `M-003` follows, so the record needs no new rule to be legitimate |
| Markdown structure parsing for the judging rule | `runtime/artifact_lib.py` parsing helpers | rejected | Those helpers read a rendered artifact into the artifact contract's section model; the judging rule needs positional fidelity between two documents, which is a different question, and bending the shared helpers to answer it would couple artifact validation to this module |
| A digest and evidence-recording convention | `runtime/framework_runtime.py` run evidence layout | reuse-extended | The session record follows the same shape — a manifest, a schema identifier, digests — without writing into `runs/<run-id>/`, which `C-003` forbids |
| A ready-made token-cost measurement | Framework surfaces | none-found | Searched `runtime/`, `omn_agent/`, and the registries; nothing measures token cost, so the module asks the provider endpoint to count and falls back to a stated estimate when it cannot |

## Operational Considerations

- Logging and observability updates: The module prints a per-file disposition as it runs and writes both a human report and a machine manifest per session (`M-001`), because a pass that modifies trusted files must leave a record a reader can audit after the fact. Derives from `C-006`.
- Error handling strategy: Three failure classes are distinguished rather than collapsed (`M-001`). A missing client library or unresolvable credential fails before any file is read, per `C-005`. A declined or truncated response is recorded against that file and the pass continues. A candidate that breaks an invariant is refused without a retry, per `C-004`, because a second attempt at a broken candidate is not more likely to be correct.
- Security considerations: The denial boundary is the security property of this change (`C-003`). It is implemented inside discovery by path segment and filename, so an operator argument cannot reach a denied surface — argument validation would leave a bypass wherever a path arrived by another route. The module writes only inside its own session directory and the files discovery yielded. It reads credentials from the environment through the client library and never records them; the session record holds digests and token counts, not content excerpts of credentials. No repository path is transmitted beyond the document text a compression request carries, which is the file's own content.
- Performance considerations: One request per eligible file, issued sequentially (`M-001`). Twenty-one files (`F-008`) makes a pass minutes rather than seconds, which is acceptable for an operator-initiated maintenance action and avoids a concurrency layer that would complicate the failure accounting. The compression instruction is marked for prefix caching, so the instruction is not re-billed per file. Derives from `C-005`.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The surface boundary is defined before discovery implements it | M-001 | none | Discovery encodes a definition; encoding a convention instead is how a denial boundary acquires a gap | T-001, T-002 |
| P-002 | The judging rule is demonstrated per loss class, and the request path returns a candidate, before any modifying path exists | M-001 | P-001 | The rule is the only mechanical defence, per `D-002`; a modifying path built ahead of it could be exercised before its guard is proven, and it has nothing to judge until the request path yields a candidate | T-003, T-004, T-005 |
| P-003 | The pre-image write precedes the modification within a single file's handling, not merely within a session | M-001 | P-002 | `C-006` is a per-file property; a session-level backup pass would leave a window in which a modification has no pre-image | T-005 |
| P-004 | The contract exists before the discovery record names it | M-002, M-003 | P-003 | Coverage check `C1` resolves the record's specification path, so the record is unresolvable until the contract exists | T-006, T-007 |
| P-005 | Coverage, validator, and recovery verification run after registration and after the profile edit, against a baseline recorded before the change | M-003, M-006 | P-004 | `C-008` is a comparison, and a comparison needs both sides captured | T-009 |
| P-006 | The proposal index is appended after the last parsed heading of the governance profile, and adds no parsed section | M-006 | none | `F-007`; a section inserted among the parsed headings would change what `load_profile` reads, turning a reader-facing index into a routing change | T-008 |

### Test Strategy Focus Areas

- The judging rule against a document compared with itself, which must report nothing, and against a constructed candidate per loss class, each of which must be refused with the loss named. This is the highest-value coverage in the change, because `D-002` makes it the acceptance rule.
- The denial boundary, exercised at each denied location and by an argument that attempts to reach one, per `C-003`.
- The absent-dependency path, exercised with no client library present, which must fail before any file is read, per `C-005`.
- The recovery path: a pre-image restored, and a file changed after the pass refused rather than overwritten, per `C-006`.
- Coverage, validator, and recovery verification compared against the pre-change baseline, per `C-008`.

### Rollout and Rollback

- Rollout: The contract, the module, and the discovery record land together; the index and count corrections land with them. Nothing executes on landing — the entry point runs only when an operator invokes it — so the change is inert until used, and the first use is a non-modifying invocation by construction.
- Rollback: Remove the discovery record and the contract together, and delete the module. Coverage check `C1` detects a partial removal, which is the intended detection. Any pass already applied is undone independently through the module's own restore path, from the session record it wrote; rollback of the capability and rollback of a pass are separate operations and neither implies the other.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | The invariant set in `D-002` misses a loss mode expressed only in prose (`A-001` false) | A candidate that reads plausibly and dropped an obligation is accepted into a surface every later run trusts without re-reading | medium | D-002, M-001 | The set covers every positionally checkable class, the contract states the guarantee as exactly that set, and the difference record is named as the control for the remainder rather than left implied | architect |
| R-002 | security | A path reaches a rewrite by a route the denial did not anticipate | Run evidence, a dated report, or a change proposal is rewritten, and the record a routed change resolves against is falsified | low | D-003, M-001 | Denial binds by path segment and filename inside discovery, which every candidate passes through, rather than at the argument boundary where a second route would bypass it | architect |
| R-003 | operability | A modification is written before its pre-image (`P-003` violated in implementation) | A file is left rewritten with no route back | low | P-003, M-001 | `P-003` states the ordering as a per-file property, and the session record's digest pair makes a missing pre-image detectable after the fact | omn-dev-1-implement |
| R-004 | contract | The discovery record lands without the contract, or the reverse | Command resolution is inconsistent, and coverage check `C1` fails | low | M-002, M-003 | `P-004` orders them; `C1` detects the inconsistency rather than allowing it to persist | omn-dev-1-implement |
| R-005 | delivery | The provider dependency is absent when a pass is attempted (`A-002` false) | No modifying pass runs | medium | M-001, A-002 | `C-005` confines the dependency so the offline surfaces still work; the absent-dependency failure is explicit and names its remediation | omn-qa |
| R-006 | structural | Adding a contract to a shared workflow disturbs that workflow, its gates, or its owning roles (`A-003` false) | The change becomes a lifecycle change, which `C-002` forbids | low | M-007, M-009, A-003 | `M-007` and `M-009` are recorded as no-change-verified rather than assumed, and `P-005` makes coverage verification decide it | architect |
| R-007 | performance | A knowledge surface grows past what one request can carry | That file cannot be compressed in a single pass | low | M-001 | The truncated response is recorded as a failure for that file and the original is kept; the pass continues, so one oversized file does not end a session | omn-dev-1-implement |

## Estimate and Confidence

- Overall: M (confidence: high)
- Breakdown: The runtime module (`M-001`) is M — discovery, the judging rule, the request path, the session record, and the undo, of which the judging rule carries most of the difficulty because its adequacy is the guarantee. The contract (`M-002`) is S. The discovery record and the three reader-facing corrections (`M-003` to `M-005`) are XS together. The profile index (`M-006`) is XS. Verification against baseline is S.
- Scope assumptions: `A-003` holds, so no lifecycle surface is touched. The knowledge surface set is the twenty-one files of `F-008`, and the module discovers rather than hard-codes it, so a change in that set costs nothing.
- Uncertainty drivers: Only one is material — whether the invariant set is adequate (`A-001`, `R-001`). It is the reason the confidence attaches to the structure of the change rather than to the quality of the compressions it will produce, which this package does not predict and the contract does not promise.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Should the invariant set extend to prose-level obligations, and by what checkable rule, or does the reviewed difference record remain the only control for them? | no | architect | D-002, R-001, A-001 | If it should, the set extends in a later change and the contract's stated guarantee widens with it; until then the contract's narrower claim is the accurate one |
| Q-002 | Who accepts the first modifying pass over this repository's own knowledge surfaces, and against which files, given that the delivery environment demonstrates no live pass? | no | omn-tech-lead | A-002, R-005 | The capability ships correct and unexercised against production surfaces; the first live pass carries its own review and its own difference record |
| Q-003 | `D-001` and `D-002` are recorded at status Proposed. Acceptance belongs to the Design Gate owners, not to this agent | no | omn-tech-lead | D-001, D-002 | Both decisions are already implemented by the selected approach; a rejection at the Design Gate returns the package rather than the code |

## Sign-off

- Architect:
- Tech Lead:
- QA:
