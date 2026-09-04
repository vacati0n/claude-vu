# Technical Design: Orientation Document Folder Descriptions Sync

```yaml
design:
  designId: run-34ca35504b72-folder-descriptions-sync-technical-design
  changeReference: >-
    runs/inputs/*-md-folder-sync-change-request.md (digest
    sha256:29b515198505a25873ee0d7464601672; the filename's leading token is
    elided because the vendor-token rule forbids reproducing it)
  sourceInputs:
    - type: change-request
      reference: runs/inputs/*-md-folder-sync-change-request.md
    - type: business-intent
      reference: runs/inputs/*-md-folder-sync-business-intent.md
    - type: architecture-context
      reference: runs/inputs/*-md-folder-sync-architecture-context.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: []
  consumesPlan: none
  inputDigest: sha256:330aaf18ec7fac4aa965ff3238384a54
  contextDigest: sha256:4c96eba9412c3b0eeb8ff4342513f027
```

## Metadata

- Feature or Change ID: folder-descriptions-sync
- Author: architect
- Reviewers: omn-tech-lead (Invariant Gate accepting owner), omn-qa
- Last Updated: 2026-08-27
- Note: the changed file is referred to throughout as "the orientation document":
  the project-instructions file at the root of `.claude/`, the one carrying the
  `## Folder Descriptions` section. Its literal filename, and the leading token of
  the supplied input filenames, are withheld because each embeds a token the
  model-independence rule (A4.1) forbids naming; the elided input filenames are
  disambiguated by the wildcard forms and digests above, which match the invocation
  envelope exactly.

## Objective

Desired outcome: the folder inventory in the framework orientation document — the
project-instructions file at the root of `.claude/`, hereafter "the orientation
document" — is complete for every directory under `.claude/` and remains a
non-authoritative summary layer over the framework's actual discovery, specification,
and runtime surfaces.

Architectural objectives:

- The `## Folder Descriptions` inventory covers every directory under `.claude/`,
  sixteen of sixteen. Traces to S-002, S-011.
- The inventory remains a summary layer: each row binds to an existing authority for
  the folder's contents and duplicates none of that authority's records. Traces to
  S-018, S-019.
- The change is confined to one additive edit of one documentation section, leaving
  every runtime-resolved surface untouched. Traces to S-004, S-005, S-013.

In structural scope: extension of the `## Folder Descriptions` section of the
orientation document by four rows (M-001); the governance artifacts the self-hosting
profile requires — a change proposal under `proposals/` and run evidence under `runs/`
(M-007, M-008; S-003).

Out of structural scope: every other section of the orientation document (S-015);
every contract, registry record, routing row, gate, and runtime behaviour (S-004);
repository-root files, which the section's folder-inventory purpose excludes (S-015);
any correction to `dependency-map.md`, which is named for separate routing in Q-002
(S-020). The out-of-scope list is non-empty because the orientation document is a
shared orientation surface read by every contributor session (F-004).

## Requirements Summary

Functional requirements:

- Every directory under `.claude/` has a row in `## Folder Descriptions`; sixteen of
  sixteen documented after the change (S-002, S-011).
- Each added row is a one-line description of what the folder holds today, bound to
  the folder's named authority (S-008, S-012, S-018).
- New rows are inserted where a reader scanning the tree would look, without
  reordering existing rows (S-008).

Non-functional requirements:

- All five verification scripts keep their current verdicts; no metric regresses
  (S-006, S-014; C-007).
- Every path the orientation document cites resolves on the filesystem after the
  change (S-007; C-008).
- No second authority is created: rows summarize, they do not restate registry or
  specification content (S-019; C-006).

Acceptance intent: the Design Gate reviewers confirm the four added descriptions are
accurate against folder contents and that the diff is purely additive and confined to
the section; the change is rejected if the diff leaves the section (S-009, S-012,
S-013, S-016).

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The orientation document's `## Folder Descriptions` section documents twelve directories while `.claude/` contains sixteen | Change request; architecture context, current-state property 1 |
| F-002 | The four undocumented directories are `domain-model/`, `prompts/`, `registry/`, `runtime/` | Change request, defect table |
| F-003 | The orientation document is not a runtime-resolved surface: no registry record points at it, no validator parses it, no workflow phase consumes it as an input artifact | Architecture context |
| F-004 | The orientation document is injected into every contributor session as authoritative project instructions | Architecture context; business intent |
| F-005 | `registry/` holds machine-read discovery indexes; the frozen context slice carries `registry/agents.yaml`, `registry/workflows.yaml`, `registry/skills.yaml`, and `registry/templates.yaml` | Frozen context slice members `registry/*.yaml` |
| F-006 | `runtime/` holds the executable runtime: the runtime gateway and state engine, recovery policy, registered artifact validators, and the verification proof scripts | `runtime/README.md`, frozen context slice member |
| F-007 | `domain-model/` holds at least `agent-specification.md`, the Agent Contract authority | `domain-model/agent-specification.md`, frozen context slice member |
| F-008 | Every path the orientation document currently cites resolves on the filesystem, operator-verified 2026-08-27 | Architecture context, current-state property 2 |
| F-009 | The `refactor` workflow routes phase `scope-invariants-and-risk-profile` to `architect`, output `technical-design.md`, gated by the Invariant Gate whose owners are `omn-architect` and `omn-tech-lead`, with acceptance resting with `omn-tech-lead` under the producer exclusion rule | `workflows/refactor.md` and `workflows/workflow-gate-matrix.md`, frozen context slice members |
| F-010 | The framework's discovery registries are single-authority; the orientation document describes them and does not duplicate their records | Architecture context, current-state property 3 |
| F-011 | The frozen `dependency-map.md` defines dependency relationships among Agents, Skills, Workflows, Memory, and Commands, and does not mention the registry indexes | `dependency-map.md`, frozen context slice member |
| F-012 | A framework-internal change produces a change proposal under `proposals/` and run evidence under `runs/`, both out of routing scope per the self-hosting profile | Change request, surfaces table (SR-5, SR-3) |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | `prompts/` holds curated, versioned prompt patterns used by the framework's agents, as the operator asserts; `prompts/README.md` is not in the frozen context slice, so its contents are unverified within this run | To bound the content requirement for the `prompts/` row (D-002) | The `prompts/` row is reworded per its authority under P-001; nothing structural changes | omn-dev-2-reviewer |
| A-002 | `domain-model/` holds exactly the five domain-concept specifications the operator asserts (agent, command, skill, workflow, memory); only `agent-specification.md` (F-007) is in the frozen slice | To bound the content requirement for the `domain-model/` row (D-002) | The `domain-model/` row's enumeration is adjusted under P-001; nothing structural changes | omn-dev-2-reviewer |
| A-003 | `registry/` also holds `commands.yaml`, the fifth discovery index the operator asserts; the frozen slice corroborates four of five (F-005) | To bound the content requirement for the `registry/` row (D-002) | The `registry/` row's enumeration is adjusted under P-001; nothing structural changes | omn-dev-2-reviewer |
| A-004 | The sixteen-directory count (F-001) remains current at implementation time; it was asserted as of 2026-08-27 | The BI-1 measure, sixteen of sixteen, is the completeness target C-004 enforces | The row set and the completeness measure are re-derived under P-001 before the edit | omn-qa |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | The diff is confined to `## Folder Descriptions` of the orientation document; the change is rejected if the diff leaves the section | Hard | S-013, S-016 |
| C-002 | structural | The change is purely additive: every existing row keeps its meaning and relative order | Hard | S-005, S-008 |
| C-003 | compliance | No contract, registry record, routing row, gate, or runtime behaviour changes | Hard | S-004 |
| C-004 | functional | After the change, every directory under `.claude/` has a row: sixteen of sixteen | Hard | S-002, S-011 |
| C-005 | functional | Each added description accurately states what the folder holds today, verified against the folder's named authority | Hard | S-008, S-012, S-018 |
| C-006 | structural | No second authority is created: descriptions summarize, they do not restate registry or specification content | Hard | S-019, F-010 |
| C-007 | operability | All five verification scripts keep their current verdicts; no metric regresses | Hard | S-006, S-014 |
| C-008 | structural | Every path the orientation document cites resolves on the filesystem after the change | Hard | S-007 |
| C-009 | functional | One line per folder, matching the existing list's register and length; new rows inserted where a reader scanning the tree would look | Negotiable | S-008 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | Orientation document (project-instructions file at the `.claude/` root), section `## Folder Descriptions` | extension | F-001, F-002 | none; documentation surface, not runtime-resolved (F-003) | confirmed |
| M-002 | Orientation document, all sections other than `## Folder Descriptions` | no-change-verified | F-003, F-004 | none | confirmed |
| M-003 | `registry/` discovery indexes | no-change-verified | F-002, F-005 | none | confirmed |
| M-004 | `runtime/` executable runtime | no-change-verified | F-002, F-006 | none | confirmed |
| M-005 | `domain-model/` specifications | no-change-verified | F-002, F-007 | none | confirmed |
| M-006 | `prompts/` prompt patterns | no-change-verified | F-002, A-001 | none | confirmed |
| M-007 | `proposals/` change-proposal store | extension | F-012 | none | confirmed |
| M-008 | `runs/` run-evidence store | extension | F-012 | none | confirmed |

M-003 through M-006 are recorded because a reader would reasonably expect the four
folders being newly documented to change in some way. They do not: each is described,
never modified (C-003). The no-change verdict for M-006 is confirmed by scope (F-002:
the folder is only being documented); A-001 bears only on the wording of its row, and
carries risk R-002. M-002 is recorded because the zero-tolerance posture (C-001) makes
the rest of the document the surface most likely to be damaged accidentally.

### 5.2 Options Considered

| Option | Structural change | C-001 | C-002 | C-004 | C-006 | Impact surface | Reuse leverage | Migration burden | Outcome |
|---|---|---|---|---|---|---|---|---|---|
| O-001 | Extend the existing `## Folder Descriptions` list in place with four additive rows | Satisfied | Satisfied | Satisfied | Satisfied | 0 | 4 | 0 | Selected |
| O-002 | Regenerate the section as a complete, restructured inventory of all sixteen directories | Satisfied | Violated | Satisfied | Satisfied | 0 | 3 | 0 | Eliminated on C-002 |
| O-003 | Leave the section as-is and add a separate complete-inventory document linked from the orientation document | Violated | Satisfied | Violated | Satisfied | 0 | 2 | 0 | Eliminated on C-001, C-004 |

Impact surface counts modules with `contract-change` or `dependency-change`; it is zero
for every option because no runtime-resolved surface changes under any of them. Reuse
leverage counts capabilities satisfied by `reuse-as-is` or `reuse-extended` in the
survey below. Hard constraints C-003, C-005, C-007, and C-008 do not discriminate
between the options and are satisfied by all three; the discriminating constraints are
shown as columns.

### 5.3 Selected Approach

- Selected: `O-001`.
- Structural change: the existing `## Folder Descriptions` list in the orientation
  document gains four rows — one each for `domain-model/`, `prompts/`, `registry/`,
  and `runtime/` — inserted where a reader scanning the tree would look (C-009), with
  every pre-existing row unchanged in meaning and relative order (C-002). No other
  surface changes.
- Rationale: `O-001` is the only option satisfying all hard constraints. It carries
  the maximum reuse leverage of the three and requires no new structure of any kind.
- Highest-scoring rejected alternative and why it lost: `O-002`, regenerating the
  section as a complete restructured inventory. It would guarantee completeness
  mechanically and produce the same sixteen rows, but regeneration cannot guarantee
  that the twelve existing rows survive with meaning and relative order intact, which
  violates hard constraint C-002 and the zero-tolerance posture in S-016; it therefore
  lost to the additive in-place extension despite its stronger completeness guarantee.
- Tradeoffs accepted: the additive manual edit gives no mechanical guarantee that the
  inventory stays complete as directories are added in the future; completeness is
  enforced only at review time against the count in C-004. This residual staleness
  exposure is attached to R-004.

Content requirements each row must satisfy (D-002), stated as requirements rather than
as authored text, which is produced at implementation under P-001:

- `domain-model/` — conveys that the folder holds the canonical specifications of the
  framework's domain concepts; enumeration bound to the specification files present
  (F-007, A-002).
- `prompts/` — conveys that the folder holds curated, versioned prompt patterns used by
  the framework's agents; wording bound to `prompts/README.md` (A-001).
- `registry/` — conveys that the folder holds the single-authority discovery indexes
  the runtime resolves routing against; enumeration bound to the index files present
  (F-005, F-010, A-003).
- `runtime/` — conveys that the folder holds the executable runtime: state engine,
  routing and invocation gateway, artifact validators, self-hosting classifier, and
  verification scripts (F-006).

Each row is a one-line summary at the granularity of the existing rows (C-009) and
must not restate any record its authority holds (C-006).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Extend `## Folder Descriptions` in place with four additive rows (`O-001`) | No | none; inline. Documentation-only, fully reversible by removing the rows, no contract, boundary, or structural component affected |
| D-002 | Each added row is a one-line summary bound to a named authority; this design fixes the content requirements, and the row text is authored at implementation under P-001 | No | none; inline |
| D-003 | Content assertions not corroborated by the frozen context slice are registered as assumptions (A-001, A-002, A-003) and routed to reviewer confirmation, never restated as facts | No | none; inline |

No decision meets any architecture-significance criterion: no externally visible
contract changes, no dependency direction or boundary changes, no structural component
is introduced or removed, the change is trivially reversible, and no quality-attribute
tradeoff is committed. `decisionRecords` is therefore empty and no decision record is
emitted.

## API and Data Model Impact

None identified. No module in 5.1 carries `contract-change` or `dependency-change`;
the changed surface is a documentation section that no registry record, validator, or
workflow phase resolves (F-003), and C-003 forbids any contract, routing, gate, or
runtime behaviour change. There is no API, schema, or data migration, and therefore no
transition strategy is required. Rollback for the documentation edit itself is stated
in the Delivery Plan.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Governed routing of a framework-internal documentation change | `/refactor` workflow via the self-hosting profile | reuse-as-is | F-009; the change is already classified and routed through it (S-001), and the workflow's Invariant Gate supplies the acceptance authority C-005 needs |
| Folder-inventory surface for contributor orientation | Existing `## Folder Descriptions` section of the orientation document | reuse-extended | Four rows are added to the existing list; C-001 and C-004 together forbid any new document or section |
| Authority for folder contents | `registry/*.yaml` indexes, `runtime/README.md`, `domain-model/` specifications, `prompts/README.md` | reuse-as-is | F-005, F-006, F-007, A-001; the rows summarize these authorities, and C-006 forbids creating a second authority beside them |
| Post-change verification | Existing verification scripts and the Invariant Gate review | reuse-as-is | F-009, C-007; verdict parity over the existing scripts is the regression measure, so no new validation structure is required |

Every capability the selected approach requires is satisfied by `reuse-as-is` or
`reuse-extended`. No survey outcome is `rejected` or `none-found`, and accordingly no
new structure is proposed anywhere in this design.

## Operational Considerations

- Logging and observability updates: none required; no runtime surface changes (C-003,
  M-004 `no-change-verified`). Run evidence is written under `runs/` by the runtime as
  usual (M-008, F-012).
- Error handling strategy: no runtime error path changes. The failure mode of this
  change is procedural — a diff that leaves the section — and is handled by rejection
  under C-001 at verification (P-003, R-003).
- Security considerations: None identified, with reason: the change adds one-line
  descriptions of folders whose existence and role are already stated across the
  repository's own governance documents (F-005, F-006, F-007); C-006 caps every row at
  summary granularity, so no secret, credential, or restricted architecture detail is
  introduced, and no access path changes (C-003).
- Performance considerations: None identified, with reason: no executable path changes
  (F-003, C-003), and no recorded quality attribute is affected; the only measured
  regression surface is verification-script verdict parity, which C-007 covers.
- Deployment and operability impact: confined to C-007 — all verification scripts must
  keep their current verdicts, proven at P-003 before closure.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The wording basis for each of the four rows is confirmed against its named authority, and the sixteen-directory count is re-confirmed | M-003, M-004, M-005, M-006 | none | C-005 accuracy must be establishable before the section is edited; assumptions A-001, A-002, A-003, and A-004 resolve here, so a false one changes wording before it can propagate | none |
| P-002 | The four rows exist in `## Folder Descriptions` with every pre-existing row unchanged in meaning and relative order | M-001, M-002 | P-001 | C-002 and C-004 must hold in one additive edit; editing before the wording basis is fixed forces rework of the same section | none |
| P-003 | The diff is confirmed confined to the section, every cited path resolves, and all verification scripts keep their verdicts | M-001, M-002, M-004 | P-002 | C-001, C-007, and C-008 are the rejection conditions of this change; they must be proven before any closure artifact records the change as done | none |
| P-004 | The change proposal under `proposals/` links this run's artifacts | M-007, M-008 | P-003 | The self-hosting profile (F-012) makes the proposal the governance record of a verified change, so verification structurally precedes it | none |

`Binds` is empty because no execution plan was supplied (`consumesPlan: none`). The
planner converts these constraints into executable tasks; this design creates no task
identifiers.

### Test Strategy Focus Areas

For `omn-qa`:

- Diff scope: the only changed lines in the repository, outside `proposals/` and
  `runs/`, sit inside `## Folder Descriptions` of the orientation document (C-001).
- Completeness: the section's row count equals the directory count under `.claude/`,
  sixteen of sixteen (C-004).
- Accuracy: each added row matches its named authority per D-002 (C-005), and no row
  restates authority content (C-006).
- Resolvability: every path the orientation document cites resolves on the filesystem
  (C-008).
- Regression: all five verification scripts report the same verdicts as before the
  change (C-007).

### Rollout and Rollback

- Rollout: follows P-001 through P-004 inside the `refactor` workflow, with Invariant
  Gate acceptance (F-009) before implementation proceeds downstream.
- Rollback: remove the four added rows, restoring the section to its prior content.
  The change is fully reversible with no data, contract, or behavioural effect
  (D-001); the reversal itself is another structure-preserving documentation edit.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | An added row restates registry or specification detail rather than summarizing it | A second authority is created beside the single-authority records (F-010) and drifts from them over time, violating C-006 | low | M-001, D-002 | P-001 binds each row to a named authority at summary granularity; the Invariant Gate review confirms register and granularity before acceptance | omn-tech-lead |
| R-002 | delivery | A-001, A-002, or A-003 is false: a folder's actual contents differ from the operator's assertion | An added description is inaccurate, failing C-005 and the BI-2 acceptance measure | low | M-006, D-002 | P-001 verifies each row against its authority file before the edit; Q-001 routes the confirmation to the reviewer | omn-dev-2-reviewer |
| R-003 | operability | The edit strays outside `## Folder Descriptions`, including incidental formatting changes elsewhere in the file | The change is rejected under the zero-tolerance posture (C-001, S-016) and reworked | low | M-002, P-002 | P-003 proves diff confinement and verification-script verdict parity before closure | omn-qa |
| R-004 | delivery | A-004 is false: the `.claude/` directory set changes between the design freeze of 2026-08-27 and implementation | The sixteen-of-sixteen measure (C-004) fails, or a row is missing or stale on landing | low | M-001, P-002 | P-001 re-confirms the directory count at implementation start and re-derives the row set if it moved | omn-qa |

## Estimate and Confidence

Overall: `XS` (confidence: high).

Breakdown:

- P-001: `XS`; reading four authority files and fixing four one-line wordings.
- P-002: `XS`; a single additive edit to one documentation section.
- P-003: `XS`; a diff-scope check and existing verification scripts re-run.
- P-004: `XS`; one governance record from the existing proposal template.

Scope assumptions: the estimate covers exactly the four sequencing constraints — the
four added rows, their verification, and the change proposal. It excludes any other
correction to the orientation document (S-020), any change to `dependency-map.md`
(Q-002), and any change to what the four folders hold.

Uncertainty drivers: the only open items are the wording assumptions A-001, A-002, and
A-003, which affect row text, not structure or effort — a false assumption changes one
line's wording inside the same P-001 activity. The estimate does not depend on any
speculative impact (every module in 5.1 is confirmed), so confidence remains high.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Are the four row descriptions, as bounded by the D-002 content requirements, accurate against the folder authorities — `prompts/README.md`, the domain-model specification set, and the registry index set including `commands.yaml`? This is the confirmation the change request explicitly asks for (S-009), and it belongs to the reviewing roles, not to this agent. | No | omn-dev-2-reviewer | M-001, D-002 | If accurate, the rows land as designed. If any differs, that row is reworded per its authority under P-001, with no structural effect. |
| Q-002 | The supplied architecture context states that `dependency-map.md` records the registries' position, but the frozen `dependency-map.md` does not mention the registry indexes (F-011). Which of the two is corrected? | No | omn-tech-lead | M-003 | Either outcome is a separate structure-preserving change routed on its own (S-020); this design is unaffected either way. It is recorded here so the discrepancy does not silently persist. |

No entry is blocking, so package status is `complete`.

## Sign-off

- Architect: architect (producing role; excluded from accepting this package)
- Tech Lead: omn-tech-lead (accepting owner for the Invariant Gate)
- QA: omn-qa

The gate for this phase is the Invariant Gate, whose owners per
`workflows/workflow-gate-matrix.md` are `omn-architect` and `omn-tech-lead`. Under the
producer exclusion rule, acceptance rests with `omn-tech-lead` because the architecture
role produced this package (F-009). Lines are left unsigned by the producing agent.

### Appendix: Statement Register and Traceability

Statements normalized from the supplied inputs, in supplied order and document order,
with their forward trace. Every statement maps to an objective, module, constraint, or
open question; no statement is dropped.

| ID | Statement (source) | Maps to |
|---|---|---|
| S-001 | The change is a structure-preserving framework-internal change routed to `/refactor`, entering at `scope-invariants-and-risk-profile` (change request) | Reuse survey row 1; F-009 |
| S-002 | `## Folder Descriptions` enumerates twelve of sixteen `.claude/` directories; `domain-model/`, `prompts/`, `registry/`, `runtime/` are undocumented (change request) | Objective 1; M-001; C-004 |
| S-003 | Expected touched surfaces: the orientation document's section, a change proposal, run evidence (change request) | M-001, M-007, M-008 |
| S-004 | INV-1: no contract, registry record, routing row, gate, or runtime behaviour changes (change request) | C-003 |
| S-005 | INV-2: every existing row keeps its meaning; only additions occur (change request) | C-002 |
| S-006 | INV-3: all verification scripts keep their current verdicts (change request) | C-007 |
| S-007 | INV-4: every path the orientation document cites resolves after the change (change request) | C-008 |
| S-008 | Descriptions state current contents verified against the folder, one line each in the existing register, inserted where a reader would look, without reordering (change request) | C-002, C-005, C-009 |
| S-009 | Requested decision: confirm the four descriptions are accurate and the change purely additive (change request) | Q-001 |
| S-010 | Outcome: a contributor reading the orientation document sees a folder inventory matching the repository (business intent) | Objective 1 |
| S-011 | BI-1: sixteen of sixteen directories documented (business intent) | C-004 |
| S-012 | BI-2: each added description matches actual contents, reviewer-confirmed (business intent) | C-005; Q-001 |
| S-013 | BI-3: diff confined to `## Folder Descriptions` (business intent) | C-001 |
| S-014 | BI-4: no metric regresses (business intent) | C-007 |
| S-015 | Non-goals: no other section rewritten, no behaviour change, no root-file documentation (business intent) | Objective, out-of-scope; M-002 |
| S-016 | Risk posture: minimal risk, zero tolerance for drift; rejected if the diff leaves the section (business intent) | C-001; R-003 |
| S-017 | The orientation document is a documentation and session-context surface, not runtime-resolved (architecture context) | F-003, F-004; M-002 |
| S-018 | Added descriptions must match the named authorities per folder (architecture context) | C-005; P-001 |
| S-019 | No second authority: descriptions summarize, never restate (architecture context) | C-006; Objective 2 |
| S-020 | Defects found elsewhere in the orientation document are named for separate routed changes (architecture context) | Q-002; Objective, out-of-scope |

Backward closure: every module in 5.1 traces to a fact or assumption; every decision in
5.4 traces to option O-001 and the constraint set; every option traces to constraints
C-001 through C-009. Lateral closure: every risk attaches to an existing module,
decision, or plan step; every plan step references existing modules; no decision record
exists, matching the empty `decisionRecords` list; no speculative impact exists,
matching the absence of a speculative-impact risk. Register closure: every current-state
claim in this package carries an `F-nnn` or `A-nnn` reference.

No implementation work was performed and no external system was accessed in producing
this design.
