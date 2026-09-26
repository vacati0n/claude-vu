```yaml
design:
  designId: CKA-04-technical-design
  changeReference: CKA-04
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-04-feature-request.md
    - type: execution-plan
      reference: runs/run-919c5d5cf156/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002]
  consumesPlan: runs/run-919c5d5cf156/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:fd43d81cf214d0cc30a94bbd85127376
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: CKA-04
- Author: architect
- Reviewers: omn-tech-lead (Design Gate accepting owner), omn-qa
- Last Updated: 2026-09-04

Statements `S-001` through `S-020` are normalized from the supplied inputs and are listed
in the appendix beneath Sign-off. Plan task identifiers `T-001` through `T-008` belong to
the supplied execution plan and are cited as consumers of this design, never created here.
Where this package refers to identifiers inside the supplied plan, it says "the plan's"
explicitly (for example "the plan's Q-001") so the plan's registers and this package's
registers cannot be confused.

## Objective

Desired structural outcome: every structural property of governance prose that the runtime
reads becomes a pinned, executable invariant in the repository test suite, bound to the
same code paths the runtime itself uses, so that a prose edit which breaks such a property
fails verification before it lands.

Architectural objectives:

- The gate-decidability property — no gate row resolvable only to its producer's alias set
  — is pinned by a check that consumes the runtime's own alias and matrix readers, so the
  pinned property and the enforced property cannot diverge. Traces to S-002, S-003, S-008,
  S-013, S-019.
- Governance-document status markers become machine-asserted structural invariants: the
  line-1 supersession marker on superseded agent specifications, and the one-line `Status:`
  banner on the four root governance documents. Traces to S-004, S-006, S-009, S-010,
  S-020.
- Agent contract prose acquires a machine-decidable safety invariant: absence of coercive
  auto-chain instruction, discriminated structurally from prohibition and declarative
  phrasing that legitimately uses the same verbs. Traces to S-005, S-011, S-018.
- The verification surface is purely additive: one new test module, four one-line banner
  additions, zero change to any runtime behavior surface or CI configuration, and every
  assertion bound to structure rather than wording. Traces to S-007, S-012, S-015.

In structural scope: one new test module in the repository test suite; one banner line on
each of the four root governance documents; a read-only import binding from the test suite
to four existing runtime reader functions; hermetic negative fixtures.

Out of structural scope: any change to `record_gate_decision`, the gate-matrix semantics,
`producer_aliases`, `runner._require_approval`, or any human-block path (S-015); any CI
configuration change (S-007); any assertion bound to sentence wording (S-012); any content
change to the four root documents beyond the single banner line (S-010); the
anti-rationalization checks the backlog assigns to CKA-16 (S-017); rewiring of the
`omn-architect` alias references in governance prose, which F-011 records as a deferred
migration.

## Requirements Summary

Functional requirements:

- A content-contract check module exists at `tests/test_content_contracts.py`, on the
  standard-library unit-test framework, discovered by the existing CI verification surface
  with zero configuration change (S-007).
- Check 1: every gate row in `workflows/workflow-gate-matrix.md` names at least one owner
  outside `producer_aliases(producer)` for the phase's producing agent (S-008).
- Check 2: the superseded agent specifications carry their status marker on line 1 (S-009).
- Check 3: each of the four root governance documents carries the one-line `Status:` banner
  (S-010, S-020).
- Check 4: no agent contract module under `agents/*/` matches the coercive auto-chain
  pattern inventory (S-011), without flagging prohibition phrasing (S-018).

Non-functional requirements:

- Structure-only binding: assertions target table cells, first-line markers, banner lines,
  and pattern structure, never sentence wording, so structure-preserving rewording stays
  free (S-012).
- Detection with zero false alarms on the accepted tree: each negative fixture fails at
  least one check, and the current tree with the banners landed yields zero failures
  (S-013, S-014).
- Additive-only delivery with no runtime behavior change (S-015).

Acceptance intent: as supplied verbatim by the ticket and carried by the approved plan —
a fixture gate matrix mutated to a producer-only owner row fails a test, and the suite runs
green against the tree once the banners land (S-013, S-014). The plan's acceptance criteria
1 through 5 are cited, not restated.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | `producer_aliases(agent_id)` is defined in `runtime/framework_runtime.py` (function at line 1265) and returns the identifier itself, its `omn-` prefixed form, and — when the identifier already carries the `omn-` prefix — its de-prefixed form | `runtime/framework_runtime.py`, verified in the frozen context snapshot |
| F-002 | `workflows/workflow-gate-matrix.md` carries one three-cell table row per workflow, gate, and required-owners triple, and states the Producer Exclusion Rule, including that the rule reads through role aliases | `workflows/workflow-gate-matrix.md` |
| F-003 | All eight active workflow specifications under `workflows/` carry a Phase Model table with the header columns Phase, Owner Agent, Participation, Input, Output Artifact, Gate, and Required Skills; a Gate cell may carry several comma-separated gate names or `none` | the eight workflow specification files; `runtime/framework_runtime.py` (`phase_gates`, line 1257) |
| F-004 | The runtime exposes importable readers for exactly these structures: `parse_gate_matrix(workflow_id)` (line 1238) reads gate ownership from the matrix; `parse_phase_model(workflow_spec_rel)` (line 754) reads a workflow's Phase Model table; `resolve_workflow` (line 740) resolves a workflow record | `runtime/framework_runtime.py` |
| F-005 | `agents/architect.md` and `agents/planner.md` each carry `(Superseded)` inside their line-1 level-1 heading | `agents/architect.md` line 1; `agents/planner.md` line 1 |
| F-006 | The four root governance documents `working-memory.md`, `rule-engine.md`, `quality-gates.md`, and `decision-matrix.md` sit at the repository root, outside the framework payload directory, and currently carry no `Status:` banner | the four files, first lines inspected |
| F-007 | Agent contract modules under `agents/*/` currently contain prohibition and declarative phrasing using the same verbs the coercive inventory targets: "must not bypass architecture, product, security, or quality governance" (`agents/architect/identity.md`, line 192); "must not bypass the gates defined in `workflows/workflow-gate-matrix.md`" (`agents/omn-dev-1-implement/identity.md`, line 181; `agents/omn-product-owner/identity.md`, line 173); "must not bypass product, architecture, or quality gates" (`agents/planner/identity.md`, line 180); "Emitting `Accepted` bypasses the Design Gate and is forbidden" (`agents/architect/reasoning.md`, line 219); "bypasses the Design Gate, which the contract forbids bypassing" (`agents/architect/examples.md`, line 627); "forbids bypassing architecture decision ownership" (`agents/omn-business-analyst/quality.md`, line 111) | the cited module files |
| F-008 | The CI verification workflow `.github/workflows/verify.yml` runs the unit-test suite by the test framework's own discovery over `tests/`, on two platforms, and its contract text states that adding a `tests/test_*.py` file is picked up with no CI or blocking-configuration change; proof scripts matching `verify_*.py` are located by discovery, not curation | `.github/workflows/verify.yml` |
| F-009 | The repository test convention is: standard-library unit-test modules under `tests/`, hermetic, anchoring the repository root from the test file's own path, extending the module search path with the runtime directory, and importing runtime modules directly (`framework_runtime`, `state_engine`); hermetic runs redirect the framework root to a temporary tree | `tests/test_gate_policy.py` |
| F-010 | The Planning Gate record supplies: the requirement that this design fix the coercive-pattern inventory and demonstrate discrimination from prohibition phrasing (the plan's R-005, closing the plan's Q-001); the requirement that the alias reading bind to the importable `producer_aliases()` rather than a reimplementation (the plan's R-006); and the banner definition under CKA-05 — the exact line `Status: specification — not implemented`, each banner cross-linking its executable counterpart: `workflows/workflow-gate-matrix.md` for `quality-gates.md` and `decision-matrix.md`, and `runtime/recovery_policy.py` together with the run-state model for `rule-engine.md` and `working-memory.md` (closing the plan's second open question, on the banner definition) | Planning Gate conditions recorded in the dispatch for this phase |
| F-011 | The gate matrix names `omn-architect` in rows whose evidence the executable agent `architect` produces, and records that the two identifiers name one role, with reference migration deferred | `workflows/workflow-gate-matrix.md` |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | Adding one banner line to each of the four root governance documents alters no structural property any other consumer reads from them (the request describes the documents as orphaned) | The additive-only constraint C-001 must hold for the banner additions | Banner placement is reworked and the affected consumer is repaired; the check itself is unaffected | omn-dev-2-reviewer |
| A-002 | Every gate-matrix row belonging to an active workflow is named by at least one Phase Model row of that workflow, so check 1 can resolve a producing agent for every row; a row named by no Phase Model row is inert to the runtime | Check 1 derives the producer from the Phase Model, which is the only declared producer source | Inert rows exist; check 1 records them as skipped (D-005) and the producer-only property is unpinned for those rows only | omn-tech-lead |
| A-003 | The Design Gate accepts the seven-family coercive inventory in D-002 as the complete closure of the plan's Q-001, with further widening deferred to CKA-16 | The check's fixtures and the current-tree green criterion are authored against a fixed inventory | Inventory and fixture rework under the plan's R-001; no structural change to the approach | omn-tech-lead |
| A-004 | `user-guide.html` exists as the user documentation surface the definition of done names, and may reference the four touched documents | C-008 requires documentation consistency for touched documents | The documentation obligation reduces to a recorded no-impact review under the plan's T-008 | omn-documentation |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | Additive change only: no alteration to `record_gate_decision`, the gate-matrix semantics, `producer_aliases`, `runner._require_approval`, or any human-block path; no runtime behavior change | Hard | S-015 |
| C-002 | structural | The deliverable is `tests/test_content_contracts.py` on the standard-library unit-test framework, discovered by the existing CI surface with zero CI configuration change | Hard | S-007, F-008 |
| C-003 | structural | Every assertion binds to structure — table cells, first-line markers, banner lines, pattern structure — never to sentence wording | Hard | S-012 |
| C-004 | functional | Each negative fixture yields at least one failing check, and the current tree with the four banners landed yields zero failing checks | Hard | S-013, S-014 |
| C-005 | structural | Check 1's alias reading is the imported `producer_aliases()` from `runtime/framework_runtime.py` — the same source the runtime reads — never a reimplementation | Hard | S-019, F-001 |
| C-006 | functional | The coercive-language check must not flag the prohibition and declarative phrasing present in current agent contract modules | Hard | S-018, F-007 |
| C-007 | migration | The banner is exactly the one line `Status: specification — not implemented`, placed in each document's preamble, with the document's executable counterpart cross-linked as F-010 defines | Hard | S-020, F-010 |
| C-008 | operability | Definition-of-done evidence: test suite green, all proof scripts PROVEN, and `user-guide.html` consistent with touched documents or a recorded no-impact review | Negotiable | S-016 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `tests/test_content_contracts.py` (new test module) | extension | F-009, F-008 | Test discovery surface; read-only import of four runtime readers | confirmed |
| M-002 | `runtime/framework_runtime.py` — `producer_aliases`, `parse_gate_matrix`, `parse_phase_model`, `phase_gates` | no-change-verified | F-001, F-004 | None changed; the four functions gain a read-only test consumer | confirmed |
| M-003 | `working-memory.md` (repository root) | extension | F-006, F-010 | One banner line added to the preamble | confirmed |
| M-004 | `rule-engine.md` (repository root) | extension | F-006, F-010 | One banner line added to the preamble | confirmed |
| M-005 | `quality-gates.md` (repository root) | extension | F-006, F-010 | One banner line added to the preamble | confirmed |
| M-006 | `decision-matrix.md` (repository root) | extension | F-006, F-010 | One banner line added to the preamble | confirmed |
| M-007 | `workflows/workflow-gate-matrix.md` | no-change-verified | F-002 | None; read by check 1 through `parse_gate_matrix` | confirmed |
| M-008 | Workflow specifications under `workflows/` (eight Phase Model tables) | no-change-verified | F-003 | None; read by check 1 through `parse_phase_model` as the producer source | confirmed |
| M-009 | `agents/architect.md` and `agents/planner.md` | no-change-verified | F-005 | None; line 1 read by check 2 | confirmed |
| M-010 | Agent contract modules under `agents/*/` | no-change-verified | F-007 | None; scanned read-only by check 4 | confirmed |
| M-011 | `.github/workflows/verify.yml` | no-change-verified | F-008 | None; the new module is picked up by existing discovery | confirmed |
| M-012 | `user-guide.html` | extension | A-004 | Documentation reconciliation for the banner additions, or a recorded no-impact review | speculative |

M-002, M-007, M-008, M-009, M-010, and M-011 are recorded as `no-change-verified` because a
reader would reasonably expect each to change in a change about gate decidability, CI, and
governance prose; each was examined and is only read, never modified (C-001, C-002). The
boundary the design crosses is the existing tests-to-runtime import boundary, already
established by F-009; no new dependency direction is introduced.

### 5.2 Options Considered

Evaluation criteria in fixed order: (1) hard constraint satisfaction; (2) impact surface,
counted as modules with contract-change or dependency-change; (3) reuse leverage, counted
as capabilities satisfied by reuse-as-is or reuse-extended in section 7; (4) quality
attributes C-003, C-004, C-006; (5) migration burden, counted as contract-affecting changes
needing a transition; (6) operability.

| Option | Structural change | Hard constraints | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|
| O-001 | One test module binding by import to the runtime's own readers (`producer_aliases`, `parse_gate_matrix`, `parse_phase_model`, `phase_gates`); hermetic negative fixtures in temporary trees; structural coercive-pattern discriminator local to the module | All satisfied | 0 | 6 of 7 | C-003, C-004, C-006 satisfied by design | 0 | No new runtime or CI surface | Selected |
| O-002 | Self-contained test module reimplementing the matrix, Phase Model, and alias parsing locally, with no runtime import | Violates C-005 | 0 | 3 of 7 | C-004 at risk: alias drift can silently unpin the property | 0 | None | Eliminated on C-005 |
| O-003 | New runtime helper module hosting the check logic, with a thin test module delegating to it | All satisfied | 0 | 5 of 7 | Same as O-001 | 0 | Widens the runtime module set for a capability the test suite already hosts | Not selected |

### 5.3 Selected Approach

Selected: O-001.

Structural change: one new test module, `tests/test_content_contracts.py`, following the
established hermetic convention (F-009). It imports four existing runtime readers and
asserts four properties. Check 1 resolves, for every active workflow, each Phase Model row's
producing agent and gate names through `parse_phase_model` and `phase_gates`, resolves the
gate's owners through `parse_gate_matrix`, asserts that every Phase-Model-named gate is
present in the matrix, and asserts that the owner set minus `producer_aliases(producer)` is
non-empty (D-001). Check 2 asserts that line 1 of each enumerated superseded specification
is a level-1 heading containing the `(Superseded)` token. Check 3 asserts, for each of the
four root documents, the presence of the exact banner line and of the counterpart reference
in the document preamble (D-003). Check 4 scans every module file under `agents/*/` with the
seven-family coercive inventory and its two-part structural discriminator (D-002). Negative
fixtures are hermetic mutated copies in temporary trees (D-004). The four banner lines land
in the same change, in the pinned form, and the banner check is unconditional (C-007, the
scope decision already approved upstream).

Rationale: O-001 is the only option that satisfies C-005 while adding no structure beyond
the deliverable itself. It carries the highest reuse leverage, and it makes the pinned
property definitionally identical to the enforced property: the check reads gate ownership,
Phase Models, and aliases through the very functions the runtime executes, so the check and
the runtime cannot disagree about what the prose means.

Highest-scoring rejected alternative and why it lost: O-003, hosting the check logic in a
new runtime helper module. It lost despite satisfying every hard constraint and keeping the
test module thin, because it introduces a structural component for a capability the test
suite already provides (section 7, hosting row), scores lower on reuse leverage, and widens
the runtime surface that maintainers and validators must track, for no gain in any recorded
criterion.

Tradeoffs accepted: the import binding couples the test suite to the names and signatures of
four runtime functions; a future rename breaks the suite loudly (R-002). That coupling is
the point — C-005 exists because a silent divergence is worse than a loud break. Second, the
coercive discriminator favors precision over recall: declarative and negated forms never
match, so a coercive instruction phrased declaratively would evade check 4 (R-001 records
the residual; CKA-16 is the designated widening vehicle per S-017).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Check 1 binds to the runtime's own readers by import — `producer_aliases`, `parse_gate_matrix`, `parse_phase_model`, `phase_gates` — with the producing agent resolved from the Phase Model Owner Agent cell; no alias or parsing logic is reimplemented | Yes | ADR D-001, status Proposed |
| D-002 | The coercive auto-chain inventory is fixed at seven pattern families — the four enumerated formulations plus three adjacent ones — matched only under a two-part structural discriminator: an imperative-or-positive-modal mood filter and a clause-bounded negation guard | Yes | ADR D-002, status Proposed |
| D-003 | Banner structural form: the exact line `Status: specification — not implemented` in the document preamble (before the first section heading), with the counterpart file reference asserted as a preamble substring — `workflows/workflow-gate-matrix.md` for M-005 and M-006, `runtime/recovery_policy.py` for M-003 and M-004; the accompanying "run-state model" phrasing from F-010 is carried as unasserted prose so the assertion stays decidable | No | Inline; the text is supplied verbatim by F-010, leaving only placement and assertion form |
| D-004 | Negative fixtures are hermetic: mutated copies of governance files in temporary framework trees or in-memory content, reusing the established temporary-root pattern (F-009); no mutated governance file is committed | No | Inline; follows the existing test convention without structural choice |
| D-005 | A gate-matrix row whose gate no Phase Model row names is inert to the runtime; check 1 records it as skipped with its identity, and separately asserts that every Phase-Model-named gate resolves in the matrix | No | Inline; consequence of the runtime's declared producer source (F-003, F-004) |
| D-006 | Check 4's scan scope is exactly the module files under `agents/*/`, as the request specifies; the top-level `agents/*.md` files are covered by check 2 only | No | Inline; scope follows S-011 verbatim |

## API and Data Model Impact

None identified. No module in 5.1 carries a contract-change or dependency-change impact
type: the change adds one test module and four one-line prose banners, and modifies no
externally visible interface, schema, or data model (C-001). No data migration exists.

One compatibility note is recorded for the Design Gate's attention: the import binding in
D-001 makes the names and signatures of the four runtime readers load-bearing for the test
suite (M-001, M-002). This is a new inbound expectation, not a contract change — the
functions themselves are unmodified — and its failure mode is a loud import or call failure
in CI, which is the intended detection behavior. R-002 records it. Rollback position for
the change as a whole is stated in the Delivery Plan.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Alias semantics for producer exclusion | `producer_aliases` in `runtime/framework_runtime.py` | reuse-as-is | F-001; C-005 mandates the same source the runtime reads; reimplementation is the divergence the plan's R-006 names |
| Gate ownership parsing | `parse_gate_matrix` in `runtime/framework_runtime.py` | reuse-as-is | F-004; the check reads ownership exactly as the runtime does, so parse drift is impossible |
| Phase Model and gate-cell parsing | `parse_phase_model` and `phase_gates` in `runtime/framework_runtime.py` | reuse-as-is | F-003, F-004; the producer source for check 1 is the same table the Task Router reads |
| Test execution and CI discovery | Existing verification workflow surface | reuse-as-is | F-008; a new `tests/test_*.py` module is picked up with no CI or blocking-configuration change |
| Hermetic fixture construction | Temporary framework-tree pattern in `tests/test_gate_policy.py` | reuse-extended | F-009; the same root-redirect approach is extended to carry mutated gate-matrix and governance-document copies |
| Check logic hosting | The test module itself, under the `tests/` convention | reuse-as-is | F-009; the suite already hosts self-contained checks with local helpers; a new runtime helper (O-003) was evaluated and not selected |
| Coercive-pattern scanning with mood and negation discrimination | None | none-found | Search basis: the `tests/` module set (F-009 file inventory) and the runtime module set in the frozen context (`runtime/README.md`, `runtime/framework_runtime.py`, the validator modules); no existing content-scanning or linguistic-pattern utility exists. This licenses the only new logic in the design, local to M-001 per D-002 |

## Operational Considerations

Logging and observability: the checks surface through the existing per-platform test check
names in the CI verification workflow (M-011, F-008); each check failure names the file and
the violated property in its assertion message so a maintainer can act without reading the
test source. Check 1 additionally reports any row skipped under D-005, keeping A-002's
residual visible (M-007).

Error handling strategy: failure modes are deliberately loud and early. A renamed or
re-signatured runtime reader fails at import or call time rather than passing vacuously
(M-002, R-002); a gate named by a Phase Model but absent from the matrix fails check 1
explicitly rather than being skipped (D-005); an empty scan set (no files matched under
`agents/*/`) is itself a failure, so path drift cannot silently disable check 4 (M-010).

Security considerations: check 4 is itself a governance-safety control — it pins the
absence of coercive auto-chain instruction in agent contracts, the failure mode the request
identifies (S-005, S-011, C-006, M-010). The suite reads repository files only, executes no
scanned content, and requires no secrets or elevated access; the CI jobs it runs under
carry read-only repository permissions (F-008, M-011).

Performance considerations: no performance constraint or quality attribute is recorded for
this change (section 4.3); the suite performs bounded file reads and pattern matching over
a fixed document set, within the existing test-suite execution budget (C-002, M-001). No
performance claim beyond that is made.

Deployment and operability impact: none beyond CI — the change ships no runtime behavior
(C-001). The one durable operational obligation is documentation consistency for the four
touched documents (C-008, M-012).

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The structural forms this design fixes — the banner line text and placement (D-003), the seven-family inventory and discriminator (D-002), and the import binding (D-001) — are accepted at the Design Gate | M-001, M-003, M-004, M-005, M-006 | none | Both the test module and the banners bind to the same fixed forms; landing either against unaccepted forms forces coordinated rework. Acceptance completes the plan's T-001, and D-003 carries the confirmed banner text the plan's T-003 established (F-010) | T-001, T-002, T-003, T-004, T-007 |
| P-002 | The import of the four runtime readers is confirmed to work under the hermetic temporary-root pattern before the four checks and their fixtures are authored against it | M-001, M-002 | P-001 | Verification of a boundary precedes work that assumes the boundary holds; if root redirection does not govern `parse_gate_matrix` reads, the fixture strategy (D-004) changes | T-002 |
| P-003 | The four banner lines exist on the root documents in the pinned form no later than the unconditional banner check enters the tree, in one change | M-003, M-004, M-005, M-006, M-001 | P-001 | An unconditional check without the banners is red on the tree, violating C-004 | T-004, T-006 |
| P-004 | The coercive scan's zero-match result over the current agent contract modules is demonstrated, with the F-007 instances shown excluded by the discriminator, before the suite gates CI | M-010, M-001 | P-001, P-002 | An unproven discriminator that turns the tree red blocks every consumer of CI (C-006, C-004) | T-002, T-006 |
| P-005 | Every negative-fixture demonstration — producer-only owner row, dropped line-1 marker, removed banner line, coercive-form fixture per family — executes and fails before green status is claimed | M-001 | P-002, P-003, P-004 | Green without demonstrated detection proves nothing; C-004 requires both halves, and the plan's T-005 review consumes these demonstrations as constraint-compliance evidence | T-005, T-006, T-007 |
| P-006 | Documentation consistency for the four touched documents is established after the banners land | M-012 | P-003 | The documentation obligation (C-008) reconciles against landed content, not intended content | T-008 |

### Test Strategy Focus Areas

For omn-qa: alias reading in both directions for check 1 (a producer-only fixture using the
`omn-` prefixed alias of the producing agent, and one using the de-prefixed form);
discriminator precision for check 4 (prohibition phrasing and declarative-consequence
phrasing from F-007 must not match; one coercive-form fixture per family in D-002 must
match); exactness of the banner assertion including the em dash in the pinned line (C-007);
D-005 behavior (a Phase-Model-named gate absent from the matrix fails; an inert matrix row
is reported skipped); a structure-preserving reword of one governed document yielding zero
failures (C-003); and CI discovery evidence taken from the run record rather than local
execution (C-002).

### Rollout and Rollback

Rollout: the test module, its fixtures, and the four banner lines land as one additive
change, ordered by P-001 through P-005; nothing activates gradually because nothing changes
runtime behavior (C-001).

Rollback: reverting the change removes the test module and the four banner lines and
restores the prior tree exactly; no data, contract, or runtime state is affected. Partial
rollback of the banners alone is not viable while the unconditional check remains (P-003
couples them); rollback is therefore of the whole change.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | Prose added to an agent contract module — or an existing declarative form outside the F-007 instances — matches a coercive family despite the discriminator | The suite turns red on an accepted tree, blocking CI for unrelated changes, and eroding trust in check 4 | medium | D-002, M-010 | P-004 demonstrates current-tree zero-match with the F-007 exclusions itemized; the discriminator's mood filter and negation guard are documented in the module for maintainers; A-003 fixes the inventory so widening is deliberate, not incidental | architect |
| R-002 | contract | A future rename or signature change of `producer_aliases`, `parse_gate_matrix`, `parse_phase_model`, or `phase_gates` | The suite fails loudly at import or call time; CI blocks until the binding is repaired | low | M-002, D-001 | Accepted coupling: the failure is explicit and local, which is the safe direction relative to silent divergence (the plan's R-006); repair is a one-point rebinding | omn-tech-lead |
| R-003 | delivery | CI discovery behavior deviates from F-008 (path, packaging, or platform difference) and the new module is not executed | The four properties are pinned locally but unenforced in CI | low | M-011, M-001, P-005 | The plan's T-006 verifies execution from the CI run record; deviation escalates to the delivery owner as a constraint conflict against C-002 | omn-tech-lead |
| R-004 | migration | The landed banner text or placement diverges from the pinned constant — em-dash encoding, casing, or placement outside the preamble — or the banner line disturbs structure some consumer reads (A-001 false) | The banner check is red on the tree, failing C-004, or a hidden consumer breaks | medium | M-003, M-004, M-005, M-006, P-003 | C-007 fixes one authoritative string and D-003 fixes placement; P-005 demonstrates the check against the landed lines; the plan's T-005 review inspects all four documents | omn-dev-1-implement |
| R-005 | structural | A gate-matrix row named by no Phase Model row carries a producer-only owner set (the harmful direction of A-002) | The producer-only property is unpinned for that row; the row is inert today but could be joined by a future Phase Model edit | low | M-007, D-005 | Check 1 reports skipped rows by identity so the set is visible in every run; the matrix-presence assertion covers the opposite, decidability-breaking direction | omn-tech-lead |
| R-006 | operability | The banners land and `user-guide.html` is not reconciled, or A-004 is false | The definition-of-done evidence C-008 is unmet at closure | low | M-012, P-006 | The plan's T-008 requires either the updated guide or a recorded no-impact review | omn-documentation |

Assumption-to-risk coverage: A-001 and the banner form are carried by R-004; A-002 by
R-005; A-003 by R-001; A-004 by R-006. The single speculative impact, M-012, is carried by
R-006.

## Estimate and Confidence

Overall: `S` (confidence: medium).

Breakdown:

- P-001: complete with this package and its two decision records; no residual effort.
- P-002: `XS` — confirming the import binding under the hermetic pattern; the pattern and
  the functions are both established (F-004, F-009).
- P-003: `XS` — four one-line additions in a pinned form.
- P-004: `S` — the discriminator is the only genuinely new logic; its current-tree
  demonstration carries the design's main uncertainty.
- P-005: `S` — one negative fixture per pinned property plus one per coercive family.
- P-006: `XS` — documentation reconciliation or a recorded no-impact review.

Scope assumptions: the seven-family inventory of D-002 is the accepted closure of the
plan's Q-001 (A-003); the banner work is exactly four documents in the pinned form (C-007);
no CKA-16 content is included (S-017); no runtime module changes (C-001).

Uncertainty drivers: confidence is held at medium rather than high because M-012 is
speculative (A-004) and because R-001 — discriminator precision against future prose — is a
property of text not yet written, which no current-tree demonstration can fully retire.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does the Design Gate accept the seven-family inventory and two-part discriminator in D-002 as the complete closure of the plan's Q-001, with further widening deferred to CKA-16? | No | omn-tech-lead | D-002, M-001 | If accepted, the check 4 fixtures and the current-tree green criterion are frozen against this inventory. If widened at the gate, the fixtures and the P-004 demonstration are reworked under the plan's R-001; the approach, module set, and other checks are unaffected. |

The plan's two open questions are closed by this design: the plan's Q-001 by D-002
(acceptance pending as Q-001 above), and the plan's second open question — the banner
definition — by C-007 and F-010, which carry the definition supplied at the Planning Gate.
No blocking open decision exists; package status is `complete`.

Decision records D-001 and D-002 remain at status `Proposed` and require Design Gate
acceptance before the plan's T-002 and T-004 proceed (P-001).

## Sign-off

- Architect: architect (producing role; excluded from accepting this package)
- Tech Lead: omn-tech-lead (accepting owner for the Design Gate)
- QA: omn-qa

Design Gate owners per `workflows/workflow-gate-matrix.md` are `omn-architect` and
`omn-tech-lead`; F-011 records that `omn-architect` and `architect` name one role. Under
the Producer Exclusion Rule, acceptance therefore rests with `omn-tech-lead`. Lines are
left unsigned by the producing agent.

### Appendix: Statement Register and Traceability

Statements normalized from the supplied inputs in document order: S-001 through S-017 from
the feature request, S-018 through S-020 from the Planning Gate conditions recorded in the
dispatch.

| ID | Statement (condensed) | Kind | Covered by |
|---|---|---|---|
| S-001 | Ticket CKA-04, Epic A verification baseline, from recommendation R5 of the adoption review dated 2026-08-27; High, effort S; depends on nothing; lands with or before CKA-03, delivered as `.github/workflows/verify.yml` | context | C-002, F-008 |
| S-002 | The runtime depends on structural properties of governance prose that nothing pins today | context | architectural objective 1 |
| S-003 | Gate ownership is read from the matrix and the Producer Exclusion Rule is enforced through `producer_aliases()`; a producer-only row is an undecidable gate no test notices | context | architectural objective 1; M-002, M-007, C-005 |
| S-004 | Superseded specifications carry the supersession marker in their first heading; a rewrite dropping it revives a dead contract | context | architectural objective 2; M-009 |
| S-005 | Agent contract modules must never carry coercive auto-chain language | outcome | architectural objective 3; D-002 |
| S-006 | The four orphaned root governance documents receive `Status:` banners under CKA-05 that must be impossible to drop | outcome | architectural objective 2; M-003, M-004, M-005, M-006 |
| S-007 | Deliverable: `tests/test_content_contracts.py` on the standard-library framework, discovered with no configuration change | constraint | C-002, M-001 |
| S-008 | Check 1: every gate row names at least one owner outside `producer_aliases(producer)` | outcome | D-001, M-001, M-007, M-008 |
| S-009 | Check 2: superseded agent files carry their status marker on line 1 | outcome | M-001, M-009 |
| S-010 | Check 3: the four root documents carry a `Status:` banner, authored now and green on the current tree; coupling resolution decided upstream — banners land in this change | outcome | D-003, C-007, M-003, M-004, M-005, M-006 |
| S-011 | Check 4: no agent contract module under `agents/*/` matches coercive auto-chain patterns | outcome | D-002, D-006, M-010 |
| S-012 | Assert on structure, not sentences | constraint | C-003 |
| S-013 | Acceptance: a producer-only fixture mutation fails a test | outcome | C-004, P-005 |
| S-014 | Acceptance: suite green against the current tree once the banners land | outcome | C-004, P-003, P-004 |
| S-015 | Additive only: the five named gate-decision surfaces unaltered; no runtime behavior change | constraint | C-001 |
| S-016 | Definition of done: tests green, proof scripts PROVEN, documentation consistency | constraint | C-008, P-006 |
| S-017 | High priority, Phase 1; CKA-16 later extends this suite; CKA-05 acceptance pinned by CKA-04 | context | Objective out-of-scope; R-001 mitigation boundary |
| S-018 | Gate condition: fix the complete coercive inventory and demonstrate discrimination from prohibition phrasing | constraint | C-006, D-002, P-004 |
| S-019 | Gate condition: bind the alias reading to the importable `producer_aliases()`, not a reimplementation | constraint | C-005, D-001 |
| S-020 | Gate condition: the banner line is `Status: specification — not implemented`, each cross-linking its executable counterpart | constraint | C-007, D-003 |

Plan-task binding summary: this design constrains the plan's T-002 (checks and fixtures per
D-001, D-002, D-004, D-005, D-006), T-004 (banner form per D-003 and C-007), T-007
(validation coverage per the test strategy focus areas), and informs T-005 and T-006
(constraint-compliance evidence per C-001 through C-004, bound by P-004 and P-005); the
plan's T-001 is discharged by this package at Design Gate acceptance (P-001), and the
plan's T-003 is discharged by F-010, whose confirmed banner text P-001 carries as D-003.

Closure statement: this run performed architecture analysis and design only. No production
code, test, migration, script, or configuration was written; no external system was
accessed; all context was consumed from the frozen input and context snapshot recorded in
the metadata block.
