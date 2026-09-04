```yaml
design:
  designId: FC-002-self-hosting-discovery-technical-design
  changeReference: FC-002
  sourceInputs:
    - type: change-request
      reference: runs/inputs/self-hosting-discovery-change-request.md
    - type: business-intent
      reference: runs/inputs/self-hosting-discovery-business-intent.md
    - type: architecture-context
      reference: runs/inputs/self-hosting-discovery-architecture-context.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: provisional
  decisionRecords: [D-001]
  consumesPlan: none
  inputDigest: sha256:e44d8c328913d9cf30026cc65ac8bddd
  contextDigest: sha256:cb5e1c4ca1c1577fe963da783d448ad7
```

## Metadata

- Feature or Change ID: FC-002
- Author: architect
- Reviewers: omn-tech-lead, omn-qa
- Last Updated: 2026-08-18

Package status is `provisional`. Six of the seven documents this change edits are not members
of this phase's frozen context slice, so their current content is asserted by the supplied
architecture context rather than established by a digested snapshot member. Their impact is
recorded as speculative and carries the risks that follow from it. No open decision blocks
approach selection, so the status is `provisional` rather than `blocked`.

This is the second attempt at this phase. Every identifier assigned on the first attempt is
preserved and none was renumbered. Two things changed. The risk class of `R-005` was corrected
from a term outside the declared vocabulary to `migration`, which is what that risk is in
substance. And the frozen context slice was re-frozen for this attempt: the input digest is
unchanged, the membership is unchanged at seventeen, and the digest recorded for
`runtime/README.md` moved from `sha256:248ad0bafb2d3ab18b49b566b79dbd88` to
`sha256:a319203767c56962636a1858b4f31873` between the two attempts. The content `F-001`,
`F-002`, and `F-003` rest on was re-checked against the new snapshot and holds unchanged, so
those facts stand and only their citation moved. That the digest of this file moved while the
change it documents has not been applied is direct observation of the condition `R-005`
predicts, and it is recorded there rather than treated as an artifact of the retry.

## Objective

- Desired outcome: the self-hosting operating mode becomes reachable by index traversal from
  the framework's top-level entry point, while remaining a single authority located in one
  document that no index restates.
- Architectural objectives:
  - Every human index that already indexes a kind of surface the self-hosting mode introduced
    carries a reference to that surface, so the mode is reachable without prior knowledge of
    file names (`S-002`, `S-003`, `S-011`).
  - Authority stays singular. Each index reference resolves to the authoritative document and
    carries no rule of its own, so no two documents can state the same rule and drift
    (`S-015`, `S-025`).
  - The precedence between the self-hosting profile and the routing policy that predates it is
    recorded once, in the document that already carries a precedence rule (`S-013`, `S-027`).
  - The change is confined to human indexes. No machine index, registry record, Phase Model,
    gate matrix row, agent contract, or runtime module is touched, and no phase context slice
    is widened (`S-004`, `S-005`, `S-006`, `S-018`, `S-023`, `S-024`, `S-026`).
  - Where the operating mode depends on capability that is not implemented, the index that
    records current state says so rather than implying completeness (`S-019`).
- In scope:
  - The seven human index documents named by the change request, as the impact table records
    them (`S-003`).
  - The single statement of precedence between the profile and the pre-existing routing policy
    (`S-013`).
  - The record of what the operating mode still lacks, in the index that already records known
    gaps (`S-019`).
- Out of scope:
  - The profile's routing table, scope rule, evidence rule, and completion rule (`S-010`).
  - The items of the framework release checklist (`S-010`).
  - Registering the profile as a record in any registry, which is a contract question rather
    than a documentation one (`S-010`).
  - Every machine index, because adding a record to one changes what resolves and is a
    different class of change (`S-023`, `S-024`).
  - The membership of any phase context slice (`S-026`).
  - Any wording that would require an existing rule to change, which is surfaced rather than
    written (`S-017`).

The out-of-scope list is not empty because this change touches shared governance surfaces. The
profile is the authority for framework-internal routing and the indexes are the documents most
readers reach first, so the boundary between describing a rule and owning it has to be drawn
before any text is written.

## Requirements Summary

- Functional requirements:
  - A reader arriving at the top-level entry point reaches the self-hosting profile, the
    change-proposal contract, and the framework release checklist by following indexes
    (`S-011`, `S-002`).
  - Each index carries the reference in the terms that index already uses, so the reader learns
    what kind of thing the surface is from where it appears (`S-012`).
  - The precedence between the profile and the pre-existing routing policy is stated once,
    where a reader would look for it (`S-013`).
  - The index that records current state records that the operating mode depends on capability
    that is still missing (`S-019`).
- Non-functional requirements:
  - No index becomes a second authority for any rule the profile states (`S-015`, `S-025`).
  - No registry record, Phase Model, gate matrix row, or agent contract is touched (`S-004`,
    `S-005`, `S-018`).
  - No runtime module changes behaviour and the runtime version constant does not move
    (`S-006`).
  - No phase context slice is widened (`S-026`).
  - An index reference carries the least text that lets a reader decide whether to follow it
    (`S-022`).
- Acceptance criteria:
  - Every verifier that passes before the change passes after it, with identical counts, and
    the four named baseline commands produce unchanged output (`S-007`, `S-009`, `S-014`).
  - Every committed run's evidence remains valid, and where an edited file is a member of a
    frozen context slice the affected runs are re-verified rather than assumed intact
    (`S-008`, `S-016`).
  - Any wording that would require a rule to change is surfaced as an open question rather than
    written (`S-017`).

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The Files table of `runtime/README.md` names the gateway, the state engine, the recovery policy, six artifact validators, the shared artifact library, the fixtures directory, five verifiers, and a migration utility. It does not name `runtime/self_hosting.py`, `runtime/verify_self_hosting.py`, or `runtime/change_proposal_validator.py` | `runtime/README.md`, frozen context slice member, digest `sha256:a319203767c56962636a1858b4f31873` |
| F-002 | `runtime/README.md` refers to two framework change proposal files in prose, in its usage note and in its seventh known gap, and its numbered known-gaps list carries eight entries, none of which concerns the self-hosting operating mode or its discoverability | `runtime/README.md`, frozen context slice member |
| F-003 | The Validation Engine coverage table of `runtime/README.md` declares six validated artifact types and names no validator for the framework change proposal, and its implemented-components table repeats the same count of six | `runtime/README.md`, frozen context slice member |
| F-004 | `registry/templates.yaml` carries an active record `framework-change-proposal` at `templates/framework-change-proposal.md`, whose description names `config/self-hosting-profile.md` as the routing authority for framework-internal change and `runtime/change_proposal_validator.py` as the validator that decides its conformance | `registry/templates.yaml`, frozen context slice member, digest `sha256:feea8081b9ed985742ea763daf6a9cf6` |
| F-005 | This phase's frozen context slice carries seventeen members, and of the seven index documents the change request names for change, only `runtime/README.md` is one of them | This run's invocation envelope, `context_slice.members`, re-frozen for attempt 2 at 2026-08-18T15:04:23Z |
| F-006 | The change request routes this work as change class `structure-preserving-change` under `config/self-hosting-profile.md` and forbids registry-record change, Phase Model change, gate matrix change, agent contract change, and runtime behaviour change | Change-request input |
| F-007 | The framework has two kinds of index that are not interchangeable: machine indexes read by the runtime resolvers, and human indexes read by a contributor or operator, among them `README.md`, the module `README.md` files, `commands/command-catalog.md`, `templates/template-catalog.md`, and `skills/agent-skill-matrix.md`. This change is scoped to human indexes only | Architecture-context input |
| F-008 | `config/agent-routing.md` maps intent to primary agent and states its own precedence rule, that where it and a Phase Model disagree the Phase Model governs, and it carries no statement about framework-internal changes | Architecture-context input, asserted property 2 |
| F-009 | `templates/template-catalog.md` indexes templates by usage point and owner and states the governance rule of one canonical template per artifact type | Architecture-context input, asserted property 3 |
| F-010 | `validation/README.md` indexes validation rules and checklist definitions, and `validation/framework-validation-checklist.md` asks whether the framework is well-formed, which is a different question from whether a given update may ship | Architecture-context input, asserted property 4 |
| F-011 | `README.md` describes eight layered responsibilities and ten folders, and neither list mentions proposals or the self-hosting profile | Architecture-context input, asserted property 6 |
| F-012 | `config/` holds `.md` policy documents and no registry, `config/README.md` indexes them, and those documents bind the roles that read them | Architecture-context input, asserted property 1 |
| F-013 | `config/execution-engine.md` narrows each phase's context slice, and a slice is content-addressed, so a document added to a slice changes the digests of the runs that hydrate it | Architecture-context input, operator constraint |
| F-014 | `workflows/workflow-gate-matrix.md` names the refactor Invariant Gate with owners `omn-architect` and `omn-tech-lead`, and its Producer Exclusion Rule forbids the producing role from accepting its own package, reading through the role alias | `workflows/workflow-gate-matrix.md`, frozen context slice member, digest `sha256:c18143d075aa49cb11b00ab39d74b90a` |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | No resolution path in the invocation gateway depends on `config/self-hosting-profile.md`, which is reached only through `runtime/self_hosting.py` and its two importers | It is the premise that makes every edit in this change non-behavioural, and it is an asserted absence, which supplied context cannot establish | The change stops being documentation-only, the invariant that no runtime module changes behaviour is at risk, and the option set would have to be re-derived against a behavioural constraint | omn-tech-lead |
| A-002 | Apart from the two prose references `F-002` records, none of the seven named index documents currently mentions the profile, the change-proposal contract, the release checklist, or the self-hosting runtime modules | It sets whether each edit is an addition or a reconciliation of an existing description, which decides the impact type of six modules | An index already carrying a description makes the edit a reconciliation, and a second authority may already exist, which the single-authority constraint forbids | omn-tech-lead |
| A-003 | The six index documents that are not members of the frozen context slice read, at the time of the edit, as the architecture-context input describes them | Five of the recorded facts about those documents rest on operator assertion rather than on a digested snapshot member | The rule that each index describes the surface in its own terms cannot be applied as designed, and the impact type recorded for the affected module is wrong | omn-context-agent |
| A-004 | `commands/README.md` states command-contract rules of the kind the change request implies, so a reference to the profile has a natural home in it | It is named for change by the change request and no supplied property describes what it indexes | The module has no home for the reference, and it moves to the no-change-verified set with reachability carried by the remaining indexes | omn-tech-lead |
| A-005 | The four baseline verifier commands read none of the seven index documents, so their counts cannot move when an index is edited | The invariant that every verifier passes with identical counts depends on it, and no supplied context establishes what those verifiers read | A verifier count changes and the central invariant of this change fails, which would make the change class wrong rather than the edit wrong | omn-qa |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | The change touches human indexes only. No machine index, registry record, Phase Model, gate matrix row, or agent contract changes | Hard | `S-004`, `S-005`, `S-018`, `S-023`, `S-024`, `F-007` |
| C-002 | structural | No index becomes a second authority. Where `config/self-hosting-profile.md` states a rule, an index references it rather than restating it | Hard | `S-015`, `S-025` |
| C-003 | functional | A reader arriving at `README.md` reaches the profile, the change-proposal contract, and the framework release checklist by following indexes, without prior knowledge of file names | Hard | `S-011`, `S-002` |
| C-004 | operability | Every verifier that passes before the change passes after it with identical counts, and the four named baseline commands produce unchanged output | Hard | `S-007`, `S-009`, `S-014` |
| C-005 | structural | No runtime module changes behaviour and the runtime version constant does not move | Hard | `S-006`, `A-001` |
| C-006 | compliance | Every committed run's evidence remains valid, and where an edited file is a member of a frozen context slice the affected runs are re-verified rather than assumed intact | Hard | `S-008`, `S-016`, `F-013` |
| C-007 | structural | No phase context slice is widened by this change | Hard | `S-026`, `F-013` |
| C-008 | quality-attribute | Each index describes the new surface in the terms that index already uses, so a reader learns what kind of thing it is from where it appears | Hard | `S-012` |
| C-009 | compliance | No index claims the operating mode is complete where the capability it depends on is missing | Hard | `S-019` |
| C-010 | structural | Any wording that would require an existing rule to change is surfaced as an open question rather than written | Hard | `S-017`, `S-027` |
| C-011 | quality-attribute | An index carries the least text that lets a reader decide whether to follow the link | Negotiable | `S-022` |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `README.md`, the framework's top-level entry index | extension | F-011 | Folder description list, layered responsibility list, contributor usage section | speculative |
| M-002 | `config/README.md`, the policy document index | extension | F-012 | Policy document index entries | speculative |
| M-003 | `config/agent-routing.md`, the intent-to-agent routing policy | extension | F-008 | Its existing precedence rule statement | speculative |
| M-004 | `commands/README.md`, the command contract index | extension | A-004 | Command-contract rules section | speculative |
| M-005 | `templates/template-catalog.md`, the controlled template index | extension | F-009 | Catalog rows by usage point and owner | speculative |
| M-006 | `validation/README.md`, the validation rule and checklist index | extension | F-010 | Checklist definition index entries | speculative |
| M-007 | `runtime/README.md`, the runtime current-state record | operational-impact | F-001, F-002, F-003, F-005 | Files table, Validation Engine coverage table, known-gaps list, and the frozen-slice digest of the file itself | confirmed |
| M-008 | `config/self-hosting-profile.md`, the framework-internal routing profile | no-change-verified | F-006, A-001 | none | confirmed |
| M-009 | `registry/templates.yaml`, the machine template registry | no-change-verified | F-004 | none | confirmed |
| M-010 | `commands/command-catalog.md`, the human command index | no-change-verified | F-007 | none | confirmed |
| M-011 | `validation/framework-validation-checklist.md`, the well-formedness checklist | no-change-verified | F-010 | none | confirmed |
| M-012 | `workflows/workflow-gate-matrix.md`, the gate ownership matrix | no-change-verified | F-014 | none | confirmed |

Five modules are recorded as `no-change-verified` because a reader would reasonably expect each
to participate and each does not. `M-008` is the authority being described, and describing a
document is not editing it, so it stays untouched under `C-002` and the out-of-scope list.
`M-009` already carries the change-proposal template as an active record, established by `F-004`,
so the machine index is not missing anything and `C-001` forbids touching it in any case.
`M-010` indexes commands, and the profile adds no command; it selects among commands that already
exist, so the precedence statement belongs in `M-003` rather than in the command catalog.
`M-011` answers whether the framework is well-formed, which `F-010` establishes is a different
question from whether an update may ship, so the release checklist is not of its kind.
`M-012` would be the natural home if the release checklist were a gate; it is not, and `C-001`
forbids the row in any case.

The only boundary crossing in the impact set is `M-007`. It is the one edited document that is a
member of this phase's frozen context slice, established by `F-005`, so the edit crosses from the
documentation surface into the run-evidence surface that `F-013` describes. Every other edit stays
inside the human-index surface.

### 5.2 Options Considered

| Option | Structural change | C-001 | C-002 | C-003 | C-008 | C-011 | Impact surface | Reuse leverage | Migration burden | Operability impact | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | Each human index carries a reference of the kind it already indexes, precedence stated once in `config/agent-routing.md`, no new document | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | 0 | 10 | 0 | One edited module, `M-007`, is a frozen-slice member | Selected |
| O-002 | One new self-hosting hub document describes the whole mode, and the seven indexes point at the hub instead of at the surfaces | Satisfied | Violated | Satisfied | Violated | Costed | 0 | 4 | 0 | Adds a maintained document and a folder-list entry, plus the same `M-007` exposure | Eliminated on C-002 and C-008 |
| O-003 | `README.md` alone gains a self-hosting section describing all four surfaces, and the kind-specific indexes stay unchanged | Satisfied | Satisfied | Satisfied | Violated | Satisfied | 0 | 2 | 0 | No frozen-slice member edited | Eliminated on C-008 |
| O-004 | `config/self-hosting-profile.md` gains a section naming where it is indexed, and the indexes stay unchanged | Satisfied | Satisfied | Violated | Violated | Satisfied | 0 | 1 | 0 | No frozen-slice member edited | Eliminated on C-003 and C-008 |

Cell vocabulary: `Satisfied` and `Violated` for a hard constraint, where a violation eliminates
the option; `Costed` for a negotiable constraint the option does not satisfy, which loses points
rather than eliminating. Impact surface counts modules carrying `contract-change` or
`dependency-change`. Reuse leverage counts capabilities satisfied by `reuse-as-is` or
`reuse-extended` in section 7. Migration burden counts contract-affecting changes requiring a
transition strategy.

Two criteria do not discriminate here. Impact surface and migration burden are zero for every
option, because no option changes a contract: the change edits prose in human indexes, and the
option set differs only in where that prose lives. The selection therefore rests on hard
constraint satisfaction first, then on reuse leverage, quality attribute satisfaction, and
operability impact, applied in that order.

### 5.3 Selected Approach

- Selected: O-001.
- Structural change: each of the seven human indexes named by the change request gains a
  reference to the self-hosting surfaces of the kind that index already carries, expressed as a
  pointer to the authoritative document and carrying no rule of its own. The precedence between
  `config/self-hosting-profile.md` and `config/agent-routing.md` is recorded once, in
  `config/agent-routing.md`, alongside the precedence rule that document already states, per
  `F-008`. `runtime/README.md` records the three self-hosting runtime modules in its Files table
  and records the mode's dependent-capability gap in the known-gaps list it already maintains,
  per `F-001` and `F-002`. No new document, no new folder, and no new index kind is created.
- Rationale: `O-001` is the only option that satisfies every hard constraint. It is also the
  only one that leaves the surfaces described in the terms of the index that carries them,
  which `C-008` requires and which is the property that makes a reader learn what kind of thing
  the surface is from where it appears. It has the highest reuse leverage of the four, ten of
  ten capabilities satisfied by existing structure, and it introduces no component, so there is
  nothing new to keep correct beyond the references themselves.
- Highest-scoring rejected alternative and why it lost: `O-003`, describing everything in
  `README.md` alone, is the strongest rejected option. It violates one hard constraint where the
  others violate two, it satisfies `C-001`, `C-002`, `C-003`, and `C-011`, and it touches no
  frozen-slice member, which is the cheapest operability position available. It loses on `C-008`:
  a reader who arrives at `templates/template-catalog.md` looking for the canonical template of
  an artifact type, which `F-009` establishes is what that catalog is for, would still not find
  the change-proposal contract there, so the index whose own governance rule the surface belongs
  under stays silent about it.
- Tradeoffs accepted:
  - Seven documents change instead of one, so the same reference must stay correct in seven
    places rather than one. That cost is accepted because the alternative that concentrates the
    description in one place either becomes a second authority, as in `O-002`, or leaves the
    kind-specific indexes silent, as in `O-003`.
  - One edited document, `M-007`, is a member of a frozen context slice, so the change acquires
    an evidence obligation it would not have if `runtime/README.md` were left alone. That
    obligation is accepted rather than avoided, because the runtime current-state record is
    exactly the index that must not overstate what the operating mode supports under `C-009`.
  - Six of the seven edits rest on asserted rather than snapshot-verified current state, so the
    design carries speculative impact and a provisional status instead of narrowing scope to the
    one document it can verify.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | The precedence between `config/self-hosting-profile.md` and `config/agent-routing.md` is recorded once, in `config/agent-routing.md`, as a reference to the profile and not as a restatement of its rule, under option `O-001` | Yes | ADR `D-001`, status Proposed, at `artifacts/architecture-decision-record-D-001.md` |
| D-002 | No new index document is created. Each reference lives in the index that already indexes that kind of surface, which is option `O-001` itself | No | Inline in section 5.3; introduces and removes no structural component |
| D-003 | `runtime/README.md` records the three self-hosting runtime modules in its Files table and the mode's dependent-capability gap in its known-gaps list, extending the shapes `F-001` and `F-002` record, under `O-001` | No | Inline; extends two existing lists without changing their shape |
| D-004 | `commands/command-catalog.md` is not edited, because the profile adds no command and the routing precedence belongs in `config/agent-routing.md` under `D-001` and option `O-001` | No | Inline; recorded as `M-010` at `no-change-verified` |

## API and Data Model Impact

- API changes: None identified. No module in section 5.1 carries `contract-change` or
  `dependency-change`. The change edits human-readable index documents only, which `C-001`
  requires and `F-007` bounds, and `A-001` records the premise that no resolution path depends
  on the document being described.
- Contract compatibility notes: the single compatibility obligation in this change is
  evidence-side and belongs to `M-007`.
  - Current shape: `runtime/README.md` is a member of this phase's frozen context slice, per
    `F-005`, carried at digest `sha256:a319203767c56962636a1858b4f31873`.
  - Target shape: the same document with three file rows added to its Files table and one entry
    added to its known-gaps list, at a new digest.
  - Compatibility approach: additive only. No existing row, count, or statement in the document
    is removed or restated, so a consumer that reads the document for what it already contains
    observes unchanged content. `F-003` records that the Validation Engine coverage count in that
    document is six; whether that count is now stale is a question about the framework, not about
    this change, and it is raised as an open decision rather than corrected here under `C-010`.
  - Coexistence period: from the edit at `P-006` until the re-verification at `P-007` completes
    for every committed run identified at `P-005`.
  - Retirement condition: the coexistence period ends when `P-007` reports identical verifier
    counts and every affected committed run re-verifies. There is no permanent dual state.
  - Rollback position: revert the edit to `M-007`. The digest returns to its recorded value, no
    other surface is affected, and no evidence is lost, because `P-005` captured the baseline
    before the edit was made.
- Schema or migration changes: None identified. No data model, schema, registry record, or
  machine index changes, which `C-001` and `S-004` forbid and `F-004` makes unnecessary for the
  template registry, whose record already exists.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| An index of config policy documents | `config/README.md` | reuse-as-is | `F-012` establishes it already indexes the `.md` policy documents in `config/`, and the profile is one of them, so the reference is a new entry in an existing index rather than a new index |
| A statement of routing precedence | The precedence rule already stated by `config/agent-routing.md` | reuse-extended | `F-008` establishes that document already carries a precedence rule for disagreement with a Phase Model, so a second precedence clause extends a shape the document owns instead of inventing one |
| A controlled index of templates | `templates/template-catalog.md` | reuse-as-is | `F-009` establishes it indexes templates by usage point and owner under a one-canonical-template rule, which is exactly the kind the change-proposal contract belongs to |
| A machine index of templates | `registry/templates.yaml` | reuse-as-is | `F-004` establishes the `framework-change-proposal` record is already active there, so no machine-index work exists, and `C-001` forbids touching it regardless |
| An index of validation rules and checklists | `validation/README.md` | reuse-as-is | `F-010` establishes it indexes validation rules and checklist definitions, and the framework release checklist is a checklist definition |
| A current-state record of the runtime surface | The Files table of `runtime/README.md` | reuse-extended | `F-001` establishes the table names each runtime file and its role and omits the three self-hosting modules, so three rows extend it without changing its shape |
| A record of what the operating mode still lacks | The known-gaps list of `runtime/README.md` | reuse-as-is | `F-002` establishes the list already carries eight numbered entries of exactly this kind, which is what `C-009` needs and what keeps the claim of completeness honest |
| A top-level index of folders and responsibilities | `README.md` | reuse-extended | `F-011` establishes it describes eight layered responsibilities and ten folders and mentions neither proposals nor the profile, so the reader's first document is where traversal has to start under `C-003` |
| An index of command contracts | `commands/README.md` | reuse-extended | `A-004` assumes it states the command-contract rules the profile routes through; the assumption is registered rather than asserted because no supplied property describes this document |
| A single authority for the self-hosting rules | `config/self-hosting-profile.md` | reuse-as-is | `C-002` requires every index to point at one authority, and `F-006` establishes the profile already is that authority for this change class, so no rule needs a new home |
| A single place stating the profile's precedence over the pre-existing routing policy | `config/self-hosting-profile.md` alone | rejected | The profile is the authority for its own rules, but a contributor deciding which command to use reads `config/agent-routing.md` first, per `F-008`. Stating the precedence only inside the profile leaves the reader who never finds the profile unserved, which is the exact failure `S-002` records |

Every capability the selected approach requires is satisfied by an existing component. The
approach proposes no new structure at all, so no capability reaches the `none-found` outcome and
the one `rejected` row licenses no new component either: it moves a statement between two
existing documents rather than creating a third.

## Operational Considerations

- Logging and observability updates: None identified, and the reason is structural. No module in
  section 5.1 emits, consumes, or configures a log or an event; every one of them is a document
  read by a person, which `F-007` and `C-001` bound. The one machine-observable effect is the
  digest of `M-007` as a frozen-slice member, established by `F-005` and `F-013`, and that value
  is already recorded by the run ledger, so it needs no new telemetry.
- Error handling strategy: the failure mode of this change is a stale or duplicated rule rather
  than a runtime error. It is handled structurally instead of procedurally: because `C-002`
  forbids an index from stating a rule of its own, any rule can be wrong in exactly one place,
  which is `M-008`. Where an index cannot describe a surface without restating a rule, `C-010`
  requires that wording to be surfaced as an open question rather than written, so the failure
  surfaces at authoring time rather than at drift time.
- Security considerations: the change exposes no new interface, no new data path, and no new
  credential surface, because no module changes a contract and none is on an execution path
  under `A-001`. The security-relevant property here is authority, not access: an index that
  restated a governance rule would let a reader act on an unreviewed copy of it, so `C-002`
  keeps every rule in `M-008` and every index entry a pointer, and `D-001` fixes where the one
  precedence statement lives. No secret, credential, or restricted detail is carried by any of
  `M-001` through `M-007`.
- Compliance considerations: `C-006` requires committed-run evidence to remain valid. `M-007` is
  the only edited module that is a member of a frozen context slice, per `F-005`, so it is the
  only compliance-relevant act in the change, and `P-005` and `P-007` bound it on both sides.
  `C-007` additionally forbids widening any slice, so no document gains slice membership here.
- Performance considerations: None identified beyond `C-004`. No module is on an execution path,
  per `A-001`, so the only measurable property this change can move is verifier output, which
  `C-004` fixes as identical before and after and which `P-007` measures rather than asserts.
- Deployment and operability impact: the change is applied as document edits. There is no build
  artifact, no deployment step, and no runtime version movement under `C-005`. Rollback is a
  revert of the same documents, with the one ordering condition recorded for `M-007` in
  section 6.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The authority boundary is fixed and recorded: `config/self-hosting-profile.md` remains the sole authority for the self-hosting rules, and every index entry is a pointer that states no rule | M-008, M-003 | none | Every later edit binds to this boundary. Writing index text first risks a restatement that `C-002` forbids and that would then have to be unwound in several documents at once | none |
| P-002 | The precedence between `config/agent-routing.md` and `config/self-hosting-profile.md` exists as a single statement in `config/agent-routing.md` | M-003 | P-001 | Contract definition precedes consumer change. The other indexes may reference the precedence rather than restate it only once it exists in exactly one place | none |
| P-003 | Each kind-specific index carries its reference, written in the terms that index already uses | M-002, M-004, M-005, M-006 | P-002 | Each entry points at the authority fixed by `P-001` and at the precedence fixed by `P-002`; writing them earlier would force each author to decide the boundary again | none |
| P-004 | The folder list, the layered responsibility list, and the contributor usage of `README.md` reach the surfaces the kind-specific indexes now carry | M-001 | P-003 | The top-level entry point indexes the indexes. Pointing it at a kind-specific index before that index carries its entry leaves the traversal `C-003` requires broken mid-path | none |
| P-005 | The committed runs whose frozen context slice records a digest for `runtime/README.md` are identified, and the pre-change output of the four baseline verifier commands is recorded | M-007 | none | A reversibility safeguard precedes an irreversible step. Once the file's digest changes, the pre-change baseline can no longer be observed, and `C-004` and `C-006` would become unprovable | none |
| P-006 | `runtime/README.md` records the three self-hosting runtime modules in its Files table and the operating mode's dependent-capability gap in its known-gaps list | M-007 | P-005, P-001 | The edit changes the digest of a frozen-slice member, so it may only follow the baseline capture, and it must point at the authority rather than restate it | none |
| P-007 | The four baseline verifier commands and every committed run identified at `P-005` are re-verified, and their counts are compared against the recorded baseline | M-007, M-001, M-002, M-003, M-004, M-005, M-006 | P-006, P-004 | Verification of a boundary precedes work that assumes the boundary holds. `C-004` and `C-006` are demonstrated after the last edit, not asserted before the first | none |
| P-008 | The modules recorded as `no-change-verified` are confirmed unchanged | M-008, M-009, M-010, M-011, M-012 | P-007 | `C-001` is an invariant of the whole change rather than of one edit. Confirming it after the last edit is what turns no machine index changed from an intention into evidence | none |

`Binds` is `none` throughout because no execution plan was supplied to this phase. These are
structural constraints, not tasks: the executable breakdown and its identifiers belong to
`planner`, which converts each constraint into work of its own.

### Test Strategy Focus Areas

For `omn-qa`:

- Verifier count parity: the four baseline commands produce byte-identical counts before and
  after, per `C-004` and the baseline recorded at `P-005`.
- Committed-run evidence: every run whose frozen context slice records a digest for
  `runtime/README.md` re-verifies after `P-006`, per `C-006`.
- Index traversal: a reader starting at `README.md` reaches the profile, the change-proposal
  contract, and the framework release checklist by following indexes only, with no prior
  knowledge of file names, per `C-003`.
- Single authority: each index entry resolves to `M-008` and states no rule that `M-008` states,
  so no pair of documents can drift, per `C-002`.
- Runtime invariance: no runtime module changes behaviour and the runtime version constant is
  unmoved, per `C-005`.
- Completeness honesty: `runtime/README.md` records the dependent-capability gap, so no index
  reads as claiming the operating mode is fully supported, per `C-009`.

### Rollout and Rollback

- Rollout: apply `P-001` through `P-008` in the recorded order. The change is complete only when
  `P-007` reports identical verifier counts and every affected committed run re-verifies; until
  then it is in the coexistence period recorded in section 6.
- Rollback: revert the edited documents. Because no registry record, contract, machine index, or
  runtime module is touched under `C-001` and `C-005`, reverting the text returns every verifier
  and every digest to its pre-change value. The one ordering condition is `M-007`: its digest
  must return to the value captured at `P-005`, which is why that capture precedes the edit.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | `A-001` is false and some resolution path in the invocation gateway reads `config/self-hosting-profile.md` directly | An edit described as documentation-only sits on a behavioural path, and `C-005` fails while the change class stays wrong | low | M-008, D-001 | `Q-001` confirms `A-001` before `P-002` begins, and `P-007` re-runs the four baseline verifiers and compares counts | omn-tech-lead |
| R-002 | contract | `A-002` is false and an index already describes one of the four surfaces | The edit becomes a reconciliation of two descriptions rather than an addition, and a second authority may already exist against `C-002` | medium | M-001, M-002, M-003, M-004, M-005, M-006 | `P-003` and `P-004` read the existing text of each index before writing to it, and any existing description is surfaced under `C-010` rather than merged | omn-tech-lead |
| R-003 | structural | `A-003` is false and an index that is not a frozen-slice member reads differently from the architecture-context description at the time of the edit | The rule that each index describes the surface in its own terms cannot be applied, and the impact type recorded for that module is wrong | medium | M-001, M-002, M-003, M-004, M-005, M-006 | `P-003` reads each index immediately before writing to it, and a divergence is raised under `Q-002` rather than designed around | omn-context-agent |
| R-004 | operability | `A-005` is false and one of the four baseline verifiers reads an edited index | A verifier count moves and `C-004` fails after the edits are already applied | low | M-007, P-007 | `P-005` records the pre-change counts and `P-007` compares them; a difference stops the change rather than being accepted as incidental | omn-qa |
| R-005 | migration | The digest recorded for `runtime/README.md` by a committed run's frozen context slice is left behind when the file is edited, so evidence captured before the change is carried across it unverified. The condition was observed between this run's own two attempts, in which that digest moved while no edit from this design had been applied | Evidence recorded before the change no longer matches current content, so a committed run cannot be assumed intact and must be re-verified rather than trusted, which is what `C-006` requires | high | M-007, P-006 | `P-005` identifies the affected runs and records their baseline before the edit, `P-007` re-verifies them after it, and the rollback position in section 6 returns the digest to the captured value | omn-qa |
| R-006 | structural | `A-004` is false and `commands/README.md` carries no command-contract rules of the kind the entry assumes | The `M-004` entry has no natural home and either goes unwritten or becomes a restatement against `C-002` | medium | M-004 | `Q-003` resolves what `commands/README.md` indexes before `P-003` writes to it, and the module moves to `no-change-verified` if it does not | omn-tech-lead |
| R-007 | delivery | An index entry summarises enough of the profile that a later change to the profile leaves the entry stale | Two documents state one rule and drift, which `C-002` exists to prevent and which no verifier would detect | medium | D-001, M-003 | `P-001` fixes the authority boundary before any text is written, and the precedence statement names the profile as the authority while stating no rule of its own | omn-documentation |
| R-008 | operability | An index describes the operating mode without recording that the capability it depends on is incomplete | A reader takes the mode as fully supported, against `C-009`, and plans framework work that cannot execute | medium | M-007, P-006 | `P-006` records the dependent-capability gap in the known-gaps list `F-002` establishes already exists for exactly this purpose | omn-documentation |

## Estimate and Confidence

- Overall: `M` (confidence: low)
- Breakdown:
  - `P-001` and `P-002`: `S` each. One authority boundary and one statement, in one document.
  - `P-003`: `M`. Four documents, each entry written in the terms of the index that carries it.
  - `P-004`: `S`. Two lists and one usage section in a single document.
  - `P-005` and `P-007`: `S` each. Evidence capture and comparison over a known command set.
  - `P-006`: `S`. Two additive edits to lists whose shape already exists.
  - `P-008`: `XS`. Confirmation of five modules recorded as unchanged.
- Scope assumptions:
  - The estimate covers the eight sequencing constraints and the twelve modules in section 5.1,
    and nothing outside them.
  - It assumes `A-001` through `A-005` hold. Each is unconfirmed, and each has a risk.
  - It excludes any change to the profile's rules, to the release checklist items, and to any
    registry record, all of which are out of structural scope.
  - It excludes the work that follows if an index already carries a description, which `R-002`
    covers, and the work of correcting any count in `runtime/README.md` that this change finds
    stale, which `Q-005` raises and `C-010` keeps out of this change.
- Uncertainty drivers:
  - Six of the seven edited documents are not members of the frozen context slice, per `F-005`,
    so their content is asserted rather than snapshot-verified under `A-003`. Confidence is `low`
    for that reason alone, since six of twelve modules carry speculative impact.
  - The number of committed runs whose frozen slice records a digest for `runtime/README.md` is
    not established by the supplied context, which drives `R-005` and the size of `P-005` and
    `P-007`.
  - Whether `commands/README.md` can host its entry at all is unresolved under `A-004` and
    `Q-003`.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does any resolution path in the invocation gateway depend on `config/self-hosting-profile.md`, as `A-001` assumes it does not? | No | omn-tech-lead | M-008, R-001 | If it does, the change stops being documentation-only, `C-005` binds differently, and the option set is re-derived against a behavioural constraint. If it does not, the selected approach stands unchanged |
| Q-002 | Do the six index documents that are not members of this phase's frozen context slice currently read as the architecture-context input describes them, per `A-003`? | No | omn-context-agent | M-001, M-002, M-003, M-004, M-005, M-006 | Where they do, six speculative impacts become confirmed and the package status moves from provisional to complete. Where they do not, the affected module's impact type and its wording under `C-008` are re-derived before `P-003` |
| Q-003 | What does `commands/README.md` index, and does it carry command-contract rules of the kind `A-004` assumes? | No | omn-tech-lead | M-004, R-006 | If it does, the `M-004` entry has a home. If it does not, `M-004` joins the `no-change-verified` set and `C-003` is satisfied through `M-001`, `M-002`, and `M-005` alone |
| Q-004 | Does the layered responsibility list in `README.md` gain the self-hosting profile as a layer of its own, or inside an existing layer, per `S-021`? | No | omn-product-owner | M-001, D-002 | A layer of its own asserts the operating mode is a peer responsibility of the framework. Inside an existing layer asserts it is one policy among the governance documents. The choice states what the framework claims to be, which is a product statement rather than a structural one, so it is not taken here |
| Q-005 | Is the Validation Engine count of six in `runtime/README.md`, established by `F-003`, still accurate given the active `framework-change-proposal` record `F-004` establishes? | No | omn-tech-lead | M-007, M-009 | If it is stale, correcting it is a current-state correction that `C-010` keeps out of this change and that needs its own change record. If it is accurate, the two documents disagree about what a validated artifact type is, which is a contract question rather than a documentation one |
| Q-006 | Is registering `config/self-hosting-profile.md` as a record in a registry to be answered separately, per `S-010` and `S-020`? | No | omn-product-owner | M-008, M-009 | Out of scope for this change by `S-010`, and recorded so the boundary stays visible. If it is later answered yes, `M-009` moves from `no-change-verified` to a machine-index change and a different change class applies |

Decision record `D-001` remains at status Proposed and requires acceptance at the Invariant Gate
before `P-002` begins. No entry above is blocking, so no open decision prevents approach
selection, and the package status is `provisional` on the ground of speculative impact alone.

## Sign-off

- Architect: architect (producing role, excluded from accepting this package under the Producer
  Exclusion Rule)
- Tech Lead: omn-tech-lead (accepting owner for the refactor Invariant Gate)
- QA: omn-qa (verification of the invariants recorded in section 9)

Gate ownership is read from `workflows/workflow-gate-matrix.md`, which `F-014` establishes names
`omn-architect` and `omn-tech-lead` as the owners of the refactor Invariant Gate. Because the
architecture role produced this package, and because the Producer Exclusion Rule reads through the
role alias, acceptance rests with `omn-tech-lead`. Every line above is left blank by the producing
agent, and the decision record emitted with this package is at status Proposed for the same reason.

## Appendix A: Statement Register and Traceability Closure

### A.1 Statement Register

| ID | Statement | Source | Lands in |
|---|---|---|---|
| S-001 | The self-hosting operating mode was delivered as four surfaces: the command profile, the change-proposal template and its validator, the framework release checklist, and two runtime modules | change-request | M-007, M-008 |
| S-002 | No index document mentions any of them, so a contributor following the entry points reaches every other surface and not this one | change-request | C-003, first objective |
| S-003 | The surfaces are to be recorded in the seven index documents that already index their kind | change-request | M-001 to M-007 |
| S-004 | No registry record changes | change-request | C-001, M-009 |
| S-005 | No Phase Model, gate matrix row, or agent contract changes | change-request | C-001, M-012 |
| S-006 | No runtime module changes behaviour and the version constant does not move | change-request | C-005 |
| S-007 | Every verifier that passes before passes after, with identical counts | change-request | C-004, P-007 |
| S-008 | Committed run evidence remains valid, and a slice member's edit forces re-verification | change-request | C-006, P-005, P-007 |
| S-009 | The four named baseline commands produce unchanged output | change-request | C-004, P-005 |
| S-010 | The profile's rules, the checklist items, and registry registration are out of scope | change-request | Out of scope, Q-006 |
| S-011 | A reader reaches the three surfaces from the top-level entry point by following indexes | business-intent | C-003, P-004 |
| S-012 | Each index describes the surface in the terms that index already uses | business-intent | C-008 |
| S-013 | The precedence between profile and routing policy is stated once, where a reader would look | business-intent | D-001, P-002 |
| S-014 | Nothing about how the framework runs changes | business-intent | C-004 |
| S-015 | No index becomes a second authority | business-intent | C-002 |
| S-016 | Every committed run's evidence still verifies | business-intent | C-006 |
| S-017 | Wording that would require a rule to change is surfaced rather than written | business-intent | C-010 |
| S-018 | No registry record, workflow phase, gate, or agent contract is touched | business-intent | C-001 |
| S-019 | The change must not claim the mode is complete where it is not | business-intent | C-009, P-006 |
| S-020 | Which indexes must change and which merely could is open to the design | business-intent | M-008 to M-012, Q-003, Q-006 |
| S-021 | Whether the profile is a layer of its own is open to the design | business-intent | Q-004 |
| S-022 | How much of the profile a reader needs at the index level is open to the design | business-intent | C-011 |
| S-023 | Machine and human indexes are not interchangeable, and this change touches human indexes only | architecture-context | C-001, F-007 |
| S-024 | Adding a record to a machine index changes what resolves | architecture-context | C-001, M-009 |
| S-025 | A human index may describe a surface but not become a second authority for it | architecture-context | C-002 |
| S-026 | A context slice is not to be widened by this change | architecture-context | C-007 |
| S-027 | Recording that the profile governs entry-command selection describes existing behaviour | architecture-context | D-001, C-010 |

### A.2 Closure Evidence

- Forward closure: 27 statements, 27 mapped to an architectural objective, a constraint, an
  impacted module, or an open question, as the register above records. No statement is dropped.
- Backward closure: 12 modules, each tracing to a fact or an assumption in its Basis column; 4
  options, each evaluated against the constraint set; 4 decisions, each tracing to option
  `O-001`. No element is invented.
- Lateral closure: 8 risks, each with a trigger and an attachment to an existing module,
  decision, or plan step; 8 plan steps, each referencing existing modules and existing
  prerequisites; 1 decision record, corresponding to the one decision marked
  architecture-significant; 6 speculative impacts, all attached to `R-002` and `R-003`.
- Register integrity: 14 facts and 5 assumptions, disjoint. Every current-state claim in this
  package carries an `F-nnn` or `A-nnn` reference.
- No implementation work was performed. No code, test, migration, script, or configuration was
  written, no application or framework module was edited, and no external system, repository, or
  ticketing tool was accessed. Every input was treated as data to design around.
