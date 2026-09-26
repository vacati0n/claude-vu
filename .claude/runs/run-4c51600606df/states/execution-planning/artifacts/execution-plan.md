```yaml
plan:
  planId: CKA-06-execution-plan
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-06-feature-request.md
    - type: product-requirement
      reference: runs/run-4c51600606df/states/scope-and-acceptance/artifacts/scope-definition.md
    - type: product-requirement
      reference: run-4c51600606df Scope Gate decision, conditions SGC-1 to SGC-5
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:5965b9107e59775c3f70f54b0b8609f7
  contextDigest: sha256:9f90eb89f94639cd8aec24f921d08586
# Upstream identifier notation. The approved scope definition SCOPE-2026-0013 uses identifier
# families that would collide with this plan's own registers, so its items are cited here in a
# distinct form: scope items as SC-001 to SC-008, acceptance criteria as AC-001 to AC-014,
# exclusions as X-001 to X-007, scope decisions as D-001 to D-006, and its two open questions as
# SQ-001 and SQ-002. Scope Gate conditions are cited as SGC-1 to SGC-5. Every bare S-nnn, A-nnn,
# R-nnn, T-nnn, and Q-nnn token in this artifact resolves against this plan's own registers.
```

## Executive Summary

The operator handbook becomes a single authored document, `docs/USER-GUIDE.md`, from which the
published `docs/user-guide.html` is generated, so that readers of either form get the same
handbook and a stale published form stops a change instead of surviving it. Success is that no
item of authored content remains present in exactly one of the two files, and that a source edit
landing without a regenerated published file is failed by the repository's verification workflow
with a runnable fix command. The work decomposes into twenty-two tasks across eight execution
waves, beginning in parallel with an inventory of the current one-sided content and an
enumeration of the anchor identifiers the published file exposes today. The highest-impact risk
is `R-003`: if regenerated output varies with ordering, locale, line endings, or platform, the
byte comparison the whole change rests on becomes unusable and every downstream verification
task loses its evidence. Two design questions are routed to `architect` rather than decided
here: how the source expresses the published form's reading affordances, and the anchor notation
that must carry the existing identifier set through regeneration. Plan status is complete; three
open questions are recorded, none blocking, and twelve tasks are assumption-dependent until
`A-001` through `A-010` are confirmed.

## Business Objectives

- Readers of either published form get the same handbook, received by every team that reads the
  operator handbook, measured as zero items of authored prose, table, or code sample present in
  exactly one of the two files after the change. Traces to `S-008`, `S-011`.
- A change that would leave the two published forms disagreeing is stopped before it reaches the
  default branch, received by every contributor and reader of the handbook, measured as the
  repository's verification workflow failing such a change and passing a change where the two
  files agree. Traces to `S-002`, `S-015`, `S-018`.
- The per-change hand-synchronisation cost that every prior delivery in the adoption backlog
  under `docs/` has paid and recorded is removed, received by contributors who change the
  handbook, measured as a contributor editing one file and invoking one documented regeneration
  command, with no instruction to synchronise the two files by hand remaining in
  contributor-facing documentation. Traces to `S-004`, `S-017`, `S-040`.
- The follow-on ticket CKA-12 can regenerate the handbook mechanically when it updates the
  exit-code tables, received by that ticket's delivery, measured as a documented and demonstrated
  regeneration command being available at this change's closure. Traces to `S-023`.
- The published handbook stays usable to the operator audience it serves, received by readers of
  the published form, measured as reviewer confirmation that the five named reading affordances
  and every anchor identifier the file exposes today survive regeneration. Traces to `S-012`,
  `S-024`, `S-029`.

## Technical Objectives

- The published file is a pure function of the source file: regeneration reproduces the committed
  published file exactly and discards any edit made directly to it. Verified by AC-001 and
  AC-002. Traces to business objectives 1 and 3, and to `S-005`, `S-026`.
- Regeneration is deterministic across repeated runs in one environment and across every
  operating system in the repository's verification matrix, line endings included. Verified by
  AC-010 and AC-011. Traces to business objective 2 and to `S-006`.
- The repository's verification workflow carries a drift check that fails a stale published file
  and reports the regeneration command as a string a contributor can run unmodified, added as a
  step over a known build output rather than over a curated file list. Verified by AC-003 and
  AC-004. Traces to business objective 2 and to `S-014`, `S-020`.
- The source document expresses every reading affordance the published form offers, in notation a
  contributor can author as prose rather than as hand-written markup. Verified by AC-007, AC-012,
  and the reported count behind AC-013. Traces to business objectives 3 and 5, and to `S-013`.
- The anchor identifier set the published form exposes today survives regeneration, and each
  anchor resolves to the section carrying the same material. Verified by AC-008. Traces to
  business objective 5 and to `S-039`.
- The published file announces, at the top of the rendered page, that it is generated, which file
  it comes from, and the command that regenerates it. Verified by AC-009. Traces to business
  objective 3 and to `S-016`, `S-036`.
- The change adds a build tool, a regenerated documentation artifact, and a verification step,
  and alters no runtime behaviour, no gate-decision behaviour, and no dependency beyond the
  standard library. Verified by the repository's test suite staying green, every proof script
  reporting PROVEN, and inspection of the change set against the forbidden surfaces the backlog
  names. Traces to business objective 4 and to `S-007`, `S-019`, `S-021`.

## Scope

### In Scope

- The published handbook is a build output of the source handbook, and a direct edit to it does
  not survive regeneration (SC-001; `S-004`, `S-005`, `S-026`). Covered by `T-002`, `T-003`.
- A source change that lands without a regenerated published file is stopped by the repository's
  verification workflow and told the exact fix command (SC-002; `S-014`, `S-015`, `S-018`).
  Covered by `T-015`, `T-016`, `T-019`.
- A one-time two-way reconciliation of the current drift, with every one-sided item of authored
  content resolved and the resolution recorded (SC-003; `S-003`, `S-008`, `S-009`, `S-010`,
  `S-011`, `S-027`, `S-028`, `S-030`). Covered by `T-001`, `T-005`, `T-006`, `T-008`.
- The authored-content test that separates content to merge from a derived label to regenerate,
  applied item by item, with every drop recorded and unsettled items escalated (SGC-1; `S-033`,
  `S-034`, `S-035`, `S-036`). Covered by `T-006`.
- The reconciliation resolution list, persisted as a named artifact of the implementation phase
  so AC-006 has something a reviewer can read (SGC-5; `S-042`). Covered by `T-007`.
- The published form keeps its chapter navigation index, chapter labels, callout blocks, the
  chain diagram, and code samples whose comment lines are distinguishable from the commands
  (SC-004; `S-012`, `S-024`, `S-029`). Covered by `T-010`, `T-011`.
- Every anchor identifier the published form exposes before the change still resolves, after it,
  to the section carrying the same material (SC-004, SGC-3; `S-012`, `S-039`). Covered by
  `T-009`, `T-011`.
- The published page opens with a banner stating that the file is generated and must not be
  edited, naming its source file and its regeneration command (SC-005; `S-016`, `S-036`).
  Covered by `T-017`.
- Regeneration produces the same published file on every repeat and on every platform in the
  verification matrix (SC-006; `S-006`). Covered by `T-004`, `T-022`.
- The source handbook stays a document a contributor reads and edits as prose, with a recorded
  counting rule for the raw-markup measure and the recorded precedence that the anchor criterion
  governs where the two conflict (SC-007, SGC-2; `S-013`, `S-037`, `S-038`). Covered by `T-010`,
  `T-012`, `T-013`, `T-014`.
- Contributor-facing documentation instructs regeneration, and the statement describing the pair
  as hand-synced is retired from the three named targets (SC-008, SGC-4; `S-017`, `S-040`).
  Covered by `T-018`.
- Evidence that the change altered no runtime or gate-decision behaviour and met the backlog's
  definition of done (`S-019`, `S-021`). Covered by `T-020`, `T-021`.
- A validation strategy that carries out the verification method named against each of the
  fourteen approved criteria (`S-032`). Covered by `T-022`.

### Out of Scope

- Generating any other duplicated documentation pair in the repository from a single source
  (X-001). Excluded because the request names exactly one pair and no other pair's reconciliation
  cost has been assessed; revisited when a second pair is identified and its divergence is shown
  to recur.
- Any change to runtime, gate-decision, or approval behaviour (X-002). Excluded because the
  backlog constrains this ticket to an additive change and forbids altering the gate-decision
  surfaces it names; such a change is scoped separately with its own gate evidence.
- Editorial rewriting or restructuring of handbook content beyond resolving content that exists
  in exactly one file (X-003). Excluded because mixing editorial improvement into a
  reconciliation makes the reconciliation impossible to review; revisited when a content review
  of the handbook is requested as its own change.
- Publishing or hosting the generated handbook anywhere outside the repository (X-004). Excluded
  because nothing in the request asks for a hosted site; revisited when a requirement to serve
  the handbook outside the repository is stated.
- Making the handbook's factual claims checkable against the tool's actual behaviour, including
  the exit-code tables (X-005). Excluded because that is the follow-on ticket CKA-12, which
  consumes this change's output; revisited when CKA-12 is scoped.
- An automated visual or structural regression check proving the reading affordances survived a
  regeneration (X-006). Excluded because the request funds one drift check over bytes, and D-006
  accepts affordance preservation by review instead; revisited if an affordance regression
  reaches the published handbook after this change.
- Removing the published handbook from version control in favour of building it only at publish
  time (X-007). Excluded because the drift check compares against the committed file and existing
  repository tests read that file from the working tree; revisited when a publishing pipeline
  exists and those tests no longer read the file.
- Rewriting committed change proposals and run evidence that describe the pair as hand-synced
  (`S-041`). Excluded because the Scope Gate placed them outside AC-014's reach; they are the
  historical record of runs that did pay the hand-synchronisation cost.

### Deferred

None identified. The approved boundary records seven exclusions, each already carrying the
condition that would revisit it, and this plan adds no further deferral of its own: every
in-scope item above is planned in this run rather than postponed.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The renderer is a standard-library tool needing no dependency outside it, consistent with the repository's dependency posture for tooling | `S-007` | The approach decision reopens, the published handbook's stated dependency footprint no longer holds, and the change stops being purely additive | architect |
| A-002 | The repository's verification workflow, delivered by ticket CKA-03, runs on more than one operating system and accepts an added step over a build output without restructuring | `S-015`, `S-020` | `T-016` grows to include workflow restructuring and the cross-platform criterion cannot be evidenced from a single workflow run | architect |
| A-003 | The exact anchor identifier set the published handbook exposes today is established by reading the committed file, and any set named in supplied text is indicative rather than exhaustive | `S-039` | An anchor absent from the baseline is dropped without detection, and the anchor criterion passes against an incomplete comparison | architect |
| A-004 | The framework's artifact writing constraints apply to every artifact this run produces and are enforced by the artifact validators; a breach causes the affected artifact to be rejected and re-emitted, and adds, removes, or changes no task | `S-022` | Nothing in the task structure changes; only the affected artifact is re-emitted | omn-orchestrator |
| A-005 | The implementer applies the recorded authored-content test rather than re-deciding it, and routes items the test does not settle to the deciding agent | `S-033`, `S-034`, `S-035` | Published wording is decided by the implementer where the Scope Gate reserved that decision, and the AC-006 evidence stops being reviewable | omn-product-owner |
| A-006 | The reconciled handbook content is expressible in the source document using notation already present in that file, so the raw-markup measure does not rise | `S-013`, `S-037` | The markup measure is reported as risen, the anchor criterion governs the conflict, and the notation decision must record the tradeoff it took | architect |
| A-007 | The two existing tests that read the published handbook pass unchanged once the reconciliation preserves the strings they assert | `S-030` | Either the reconciliation must preserve content the authored-content test would drop, or those tests change, and both are decisions above the implementer | omn-qa |
| A-008 | One regeneration command line serves every platform in the verification matrix unmodified | `S-014`, `S-018` | `T-015` states a per-platform command form in its acceptance criterion; no task is added or removed | architect |
| A-009 | The handbook carries maintenance material that can hold the regeneration instruction, or such material can be added within this change | `S-040` | `T-018` lands the instruction in two targets rather than three and records the third as not applicable; no task is added or removed | omn-documentation |
| A-010 | The three targets the Scope Gate named are the complete inventory of contributor-facing statements about the handbook pair | `S-040`, SQ-001 | The text review behind AC-014 finds a further hand-synchronisation instruction after `T-018` closed, and that task reopens | omn-documentation |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | An inventoried item is not settled by the recorded authored-content test and is resolved without escalation before the reconciliation is applied | Published wording changes on an implementer's judgement where the Scope Gate reserved that decision; the AC-006 evidence is not reviewable | medium | T-005, T-006, T-007 | `T-006` records the test clause behind every resolution and routes unsettled items to its owner; `T-008` refuses any item left unresolved | omn-product-owner |
| R-002 | requirement | The authored-content test would drop a string that the existing parity test or the dependency-footprint test asserts | The repository's test suite fails, or the reconciliation reopens as a scope change after implementation started | medium | T-005, T-006, T-020 | `T-006` records the asserted strings as non-droppable and escalates the conflict; `Q-003` names the authority that decides it | omn-product-owner |
| R-003 | technical | Regenerated output varies with dictionary ordering, locale, line endings, or the platform running it | The byte comparison the whole change rests on becomes unusable, one matrix leg fails permanently, and every downstream verification task loses its evidence | medium | T-002, T-003, T-004, T-016 | `T-003` fixes the determinism decisions before the renderer is built; `T-004` evidences repeat and cross-platform identity | architect |
| R-004 | technical | An affordance cannot be expressed in the source document without adding markup a contributor would have to hand-write | The readability objective weakens and the raw-markup measure rises against AC-013 | medium | T-010, T-012, T-014 | `T-010` records the tradeoff taken for each affordance; `T-014` reports the count rather than enforcing it, per the recorded precedence | architect |
| R-005 | technical | An anchor identifier the published file exposes today is missing from the enumerated baseline | A dropped anchor passes the page verdict and breaks a link readers already use | medium | T-009, T-011 | `T-009` states its enumeration method and takes the set from the committed file rather than from a supplied list | architect |
| R-006 | dependency | The verification workflow delivered by ticket CKA-03 does not accept an added step over a build output without restructuring, or its matrix does not cover both platforms | `T-016` grows into workflow restructuring, and the cross-platform criterion cannot be evidenced from one run | low | T-004, T-016, T-019 | `T-003` confirms the workflow's shape and matrix before the step is written | architect |
| R-007 | security | The reconciliation merges published-form wording that names internal detail the source document was not intended to carry | Content exposure widens without a review having judged it | low | T-005, T-006, T-008 | `T-008` reviews every merged item against the source that carried it before the change | omn-dev-2-reviewer |
| R-008 | operational | A contributor who has been editing the published file directly continues to do so after the change | Their edit is lost at the next regeneration and their change is failed by the drift check, with no explanation unless the page and the documentation say so | high | T-017, T-018, T-021 | `T-017` puts the notice at the top of the rendered page; `T-018` states the consequence in contributor-facing documentation | omn-documentation |
| R-009 | operational | A reading affordance regresses in a change made after this one | Nothing catches it mechanically, because the accepted boundary funds review rather than an automated affordance check | medium | plan-wide | `T-021` records the gap as accepted and names the condition the boundary already set for funding the automated check | omn-tech-lead |
| R-010 | delivery | A contributor-facing statement about the handbook pair exists outside the three targets the Scope Gate named | The text review behind AC-014 finds a remaining hand-synchronisation instruction after the documentation task closed | medium | T-018 | `T-018` searches contributor-facing documents rather than working from the named list alone | omn-documentation |
| R-011 | delivery | The renderer needs capability outside the standard library | The published handbook's stated dependency footprint stops being true, the backlog's tooling posture is breached, and the approach decision reopens | low | T-002, T-003, T-020 | `T-003` carries the standard-library constraint as a design constraint and records any exception for decision rather than taking it | architect |

## Task Breakdown

### T-001 Inventory the one-sided content across the two published forms

- Owner: omn-context-agent
- Complexity: M (confidence: medium)
- Depends on: none
- Traces to: S-003, S-008, S-032
- Status: ready
- Description: A section-by-section comparison of the two handbook files as committed before this
  change exists, listing every item of prose, table, or code sample present in exactly one of
  them.
- Acceptance Criteria:
  - Every section of both files appears in the comparison, and the comparison states the revision
    of each file it was taken against
  - Each listed item names the file that carries it and the section it sits in
  - The known divergences named in the request, the branch naming templates section and the
    differing order of the gate-ownership material, both appear in the comparison
- Gate: Scope Gate

### T-002 Deliver the renderer that produces the published handbook from the source

- Owner: omn-dev-1-implement
- Complexity: L (confidence: low)
- Depends on: T-003, T-010
- Traces to: S-004, S-005, S-026, A-001
- Status: assumption-dependent
- Description: A tool at `tools/render_user_guide.py` reads `docs/USER-GUIDE.md` and writes
  `docs/user-guide.html` with no manual step between them, following the approved approach and
  the defined source notation.
- Acceptance Criteria:
  - Running the tool over the source file produces the published file without any manual step
  - Two runs over the same source in the same environment produce output with zero differing
    bytes
  - The output carries every affordance the defined source notation expresses
  - The tool runs with no dependency outside the standard library
- Gate: Review Gate

### T-003 Define the technical approach for the renderer and its drift check

- Owner: architect
- Complexity: L (confidence: low)
- Depends on: T-010
- Traces to: S-005, S-006, S-007, S-014, S-019, A-001, A-002, A-008
- Status: assumption-dependent
- Description: An approved approach exists stating how the published file is derived from the
  source, how repeated and cross-platform runs are made byte-identical, how the check mode
  compares and reports, and why the change stays additive.
- Acceptance Criteria:
  - The approach states the decision taken for each named determinism hazard: ordering, locale,
    line endings, and platform
  - The approach states how the check mode compares the regenerated content against the committed
    published file without writing to the working tree
  - The approach names the regeneration command form and states whether one form serves every
    platform in the matrix
  - The approach records that no dependency outside the standard library is introduced, or
    records the exception for decision rather than taking it
  - The approach records the shape and matrix of the existing verification workflow that the
    drift step will be added to
- Gate: Design Gate

### T-004 Verify byte-identical regeneration across repeats and platforms

- Owner: omn-qa
- Complexity: S (confidence: low)
- Depends on: T-016, T-022
- Traces to: S-006, A-002
- Status: assumption-dependent
- Description: Recorded evidence exists that regeneration from the same source produces the same
  published file twice in one environment and on every operating system in the repository's
  verification matrix.
- Acceptance Criteria:
  - Two regenerations from the same source into separate destinations compare with zero differing
    bytes
  - The drift check step passes on every operating system leg of a single verification workflow
    run, line endings included
  - The evidence is recorded against the criteria it satisfies, with the workflow run identified
- Gate: Verification Gate

### T-005 Bring the source handbook into agreement with the recorded resolution list

- Owner: omn-dev-1-implement
- Complexity: L (confidence: low)
- Depends on: T-002, T-007
- Traces to: S-008, S-010, S-011, S-027, S-028, S-030, A-005, A-007
- Status: assumption-dependent
- Description: `docs/USER-GUIDE.md` carries every item the resolution list marks merged and
  nothing the list marks dropped, and the regenerated published file carries the whole of it.
- Acceptance Criteria:
  - Every item the list marks merged is present in the source document
  - Every item the list marks dropped is absent from both files
  - The branch naming templates section appears in the regenerated published file with its token
    reference table, its normalization and validation rules, its viewing-and-changing content,
    and its migration notes
  - The gate-ownership material appears in the published file in the order the source gives it
  - No content is changed beyond the items the list names
  - Every string the existing parity test and the existing dependency-footprint test assert is
    still present in the published file
- Gate: Review Gate

### T-006 Resolve every inventoried one-sided item under the recorded authored-content test

- Owner: omn-product-owner
- Complexity: M (confidence: low)
- Depends on: T-001
- Traces to: S-009, S-033, S-034, S-035, S-036, A-005, A-007
- Status: assumption-dependent
- Description: Every item in the inventory carries one recorded resolution, either merged into the
  source document or deliberately dropped, together with the clause of the recorded test that
  produced it.
- Acceptance Criteria:
  - Every inventoried item carries exactly one resolution and names the test clause behind it
  - Wording that states a fact and exists only in the published form is resolved as merged
  - Wording that only labels or routes within the page is resolved as dropped, with the heading
    it is regenerated from named
  - No drop is recorded without a reason
  - Items the recorded test does not settle are decided by this task's owner, and the decision and
    its rationale are recorded
  - The published form's footer source statement is recorded as folding into the generated banner
    rather than being merged into the source document
  - Any item whose drop would remove a string an existing test asserts is recorded as
    non-droppable, with the conflict named
- Gate: Scope Gate

### T-007 Persist the reconciliation resolution list as a named implementation-phase artifact

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-006
- Traces to: S-009, S-042
- Status: ready
- Description: The resolution list exists as a named artifact of the implementation phase, at a
  path the change's evidence references, carrying every inventoried item with its resolution.
- Acceptance Criteria:
  - The artifact exists at a named path and is referenced from the change's evidence
  - Every item from the inventory appears in it with its recorded resolution and test clause
  - No item is left unresolved
  - A reader who did not build the change can match each entry back to the section of the file
    that carried it
- Gate: Review Gate

### T-008 Review the resolution list against the pre-change comparison

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: high)
- Depends on: T-005, T-007
- Traces to: S-009, S-035
- Status: ready
- Description: A recorded review verdict exists stating whether every one-sided item found before
  the change is resolved in the delivered result.
- Acceptance Criteria:
  - Every item in the pre-change comparison is matched to an entry in the resolution list
  - The reviewer confirms each merged item is present in the source document and each dropped item
    is absent from both files
  - The reviewer records a defect for any drop lacking a reason, and for any merged item whose
    wording names detail the source document was not intended to carry
  - The verdict states whether the criterion for one-sided content is met
- Gate: Review Gate

### T-009 Enumerate the anchor identifier baseline the published handbook exposes today

- Owner: architect
- Complexity: S (confidence: low)
- Depends on: none
- Traces to: S-012, S-039, A-003
- Status: assumption-dependent
- Description: The set of anchor identifiers exposed by `docs/user-guide.html` as committed before
  this change is enumerated and recorded as the baseline the anchor criterion compares against.
- Acceptance Criteria:
  - The enumeration is taken from the committed published file rather than from a supplied list,
    and states the method used to take it
  - Chapter-level anchors and in-chapter anchors are distinguished
  - The baseline is recorded where the page review and the notation decision can both consume it
  - The record states that this set is fixed and must survive regeneration
- Gate: Design Gate

### T-010 Define the source notation for the published form's reading affordances

- Owner: architect
- Complexity: L (confidence: low)
- Depends on: T-009
- Traces to: S-012, S-013, S-024, A-006
- Status: assumption-dependent
- Description: An approved notation exists by which `docs/USER-GUIDE.md` expresses every reading
  affordance the published form offers, without the source becoming a markup document.
- Acceptance Criteria:
  - The notation covers the chapter navigation index, chapter labels, callout blocks, the chain
    diagram, code samples whose comment lines are distinguishable, and section anchors
  - For each affordance the notation states whether it uses notation already present in the source
    document or newly defined notation, and records the tradeoff where it is newly defined
  - The notation reproduces every anchor identifier in the recorded baseline
  - The notation answers how a contributor adds a section, a callout, and a code sample without
    hand-writing markup
- Gate: Design Gate

### T-011 Record a reviewer verdict on the regenerated published page

- Owner: omn-dev-2-reviewer
- Complexity: M (confidence: medium)
- Depends on: T-005, T-009, T-017
- Traces to: S-012, S-016, S-024, S-029, S-039
- Status: ready
- Description: A recorded verdict exists stating whether the regenerated page still presents the
  named reading affordances, resolves every baseline anchor to the section carrying the same
  material, and announces its generated status.
- Acceptance Criteria:
  - The regenerated page is walked against the pre-change page across the chapter navigation
    index, chapter labels, callout blocks, the chain diagram, and code-sample comment
    distinction, with a verdict recorded per item
  - Every anchor identifier in the recorded baseline resolves in the regenerated page to the
    section carrying the same material, and any that does not is recorded as a defect
  - The top of the rendered page is confirmed to state that the file is generated and must not be
    edited, to name its source file, and to give its regeneration command
  - The verdict states whether the affordance criterion and the anchor criterion are met
- Gate: Review Gate

### T-012 Define the raw-markup-line counting rule

- Owner: omn-qa
- Complexity: S (confidence: low)
- Depends on: T-010
- Traces to: S-013, S-037, S-038, A-006
- Status: assumption-dependent
- Description: A recorded rule exists that decides, for any line of `docs/USER-GUIDE.md`, whether
  it counts as raw markup rather than prose, and that an independent reviewer can apply without
  consulting its author.
- Acceptance Criteria:
  - The rule classifies every line of the source document into exactly one of raw markup or prose
  - Two independent applications of the rule to the same revision produce the same count
  - The rule is stated against the notation the approved source notation defines
  - The record states that where the anchor-preservation criterion and the markup-count criterion
    conflict, the anchor criterion governs and the markup count is reported rather than enforced
- Gate: Verification Gate

### T-013 Run the authoring walkthrough on the source notation

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: medium)
- Depends on: T-005, T-010
- Traces to: S-013
- Status: ready
- Description: A recorded walkthrough exists in which a reviewer who did not build the change adds
  new content to a scratch copy of the source handbook using the defined notation and confirms it
  renders.
- Acceptance Criteria:
  - One new section, one callout, and one code sample are added to a scratch copy of the source
    document using notation already present in that file
  - Regeneration renders all three in the published output
  - The walkthrough records any notation the reviewer could not apply without consulting the
    builder
  - The verdict states whether the authoring criterion is met
- Gate: Review Gate

### T-014 Report the raw-markup-line count for both revisions of the source handbook

- Owner: omn-qa
- Complexity: XS (confidence: high)
- Depends on: T-005, T-012
- Traces to: S-013, S-037, S-038
- Status: ready
- Description: A recorded report exists giving the raw-markup-line count for the source document
  as committed before this change and as committed after it, taken with the recorded rule.
- Acceptance Criteria:
  - Both counts are produced with the recorded counting rule and the revision of each is named
  - The report states the difference between the two counts
  - Where the count rose, the report states that the anchor-preservation criterion governs and
    that this criterion is reported rather than enforced
- Gate: Verification Gate

### T-015 Deliver the drift check mode

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-002, T-003
- Traces to: S-014, S-018, A-008
- Status: assumption-dependent
- Description: The renderer offers a mode that re-renders the published content in memory,
  compares it against the committed published file byte for byte, and reports the outcome without
  writing to the working tree.
- Acceptance Criteria:
  - A mismatch exits with a nonzero status
  - An agreeing pair exits with a zero status
  - The failure output contains the regeneration command as a string a contributor can run
    unmodified
  - The mode leaves the working tree unchanged whether it passes or fails
- Gate: Review Gate

### T-016 Wire the drift check into the repository's verification workflow

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-015, and on the external prerequisite in 8.2
- Traces to: S-015, S-020, A-002
- Status: assumption-dependent
- Description: The repository's verification workflow runs the drift check as a step over the
  known build output, on every leg of its matrix.
- Acceptance Criteria:
  - The step is expressed over the known build output rather than over a curated list of files a
    future contributor must extend
  - The step runs on every operating system leg of the workflow matrix
  - The step's failure output, including the regeneration command, reaches the workflow run log
  - Every assertion the existing parity test makes about the workflow still holds
- Gate: Review Gate

### T-017 Emit the generated-file banner at the top of the published handbook

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-016, S-036
- Status: ready
- Description: The regenerated published file opens with a banner, visible when the page is
  rendered, stating that the file is generated and must not be edited, naming its source file,
  and giving its regeneration command.
- Acceptance Criteria:
  - The banner is legible at the top of the rendered page, not only present in the markup
  - The banner names `docs/USER-GUIDE.md` as the source file
  - The banner gives the regeneration command
  - The published form's former footer source statement is carried by this banner and is not
    additionally merged into the source document
- Gate: Review Gate

### T-018 Update contributor-facing documentation to instruct regeneration

- Owner: omn-documentation
- Complexity: M (confidence: low)
- Depends on: T-015
- Traces to: S-017, S-040, S-041, A-009, A-010
- Status: assumption-dependent
- Description: Contributor-facing documentation states that the published handbook is generated
  from `docs/USER-GUIDE.md` and names the regeneration command, and no contributor-facing text
  instructs synchronising the two files by hand.
- Acceptance Criteria:
  - `README.md` states that the published handbook is generated and names the regeneration command
  - The handbook's own maintenance material carries the same instruction, or the absence of such
    material is recorded with the instruction placed in the remaining targets
  - The parity test's docstring no longer describes the two files as hand-synced
  - A search of contributor-facing documents finds no remaining instruction to synchronise the two
    files by hand, and the search's scope is recorded
  - Committed change proposals and run evidence are unchanged
- Gate: Review Gate

### T-019 Demonstrate the drift failure and the passing case

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: T-016, T-022
- Traces to: S-018, A-002
- Status: assumption-dependent
- Description: Recorded evidence exists that the verification workflow fails a source-only change
  and passes a change where the two files agree.
- Acceptance Criteria:
  - A demonstration branch carrying a source-only edit is run through the verification workflow,
    the run fails, and the logged output carries the regeneration command as a runnable string
  - The verification workflow passes on a commit where the source and the published file agree
  - Both runs are recorded as evidence against the criteria they satisfy
- Gate: Verification Gate

### T-020 Confirm the change altered no runtime or gate-decision behaviour

- Owner: omn-dev-2-reviewer
- Complexity: S (confidence: high)
- Depends on: T-016, T-018
- Traces to: S-019, S-021
- Status: ready
- Description: A recorded verdict exists stating that the delivered change set adds a build tool,
  a regenerated documentation artifact, a verification step, and documentation edits, and touches
  no forbidden runtime or gate-decision surface.
- Acceptance Criteria:
  - The change set is checked against each runtime and gate-decision surface the backlog forbids
    altering, with the result recorded per surface
  - The repository's test suite is green
  - Every proof script reports PROVEN
  - The verdict records whether the backlog's definition of done is met
- Gate: Review Gate

### T-021 Publish the release note and closure record

- Owner: omn-documentation
- Complexity: S (confidence: high)
- Depends on: T-004, T-008, T-011, T-013, T-014, T-019, T-020
- Traces to: S-021, S-023
- Status: ready
- Description: A published record states what the change delivered, what the evidence showed, and
  what is knowingly left unguarded.
- Acceptance Criteria:
  - The record states that the published handbook is now generated, names the regeneration
    command, and states the consequence for anyone who has been editing the published file
    directly
  - The record names the regeneration command available to the follow-on ticket and the run that
    demonstrated it
  - The record carries the reported raw-markup count and the reviewer verdicts
  - The record names the accepted gap that no automated check guards the reading affordances, with
    the condition that would fund one
- Gate: Closure Gate

### T-022 Define the validation strategy for the approved criteria

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-003
- Traces to: S-032
- Status: ready
- Description: A validation strategy exists that carries out the verification method the approved
  scope names against each of its fourteen acceptance criteria.
- Acceptance Criteria:
  - Each of the fourteen approved criteria has a named check, the evidence it produces, and its
    pass condition
  - Criteria decided by review rather than by a mechanical check are named as such, with the
    reviewing role identified
  - The strategy states how cross-platform determinism evidence is drawn from a single
    verification workflow run
  - The strategy states how the demonstration of a failing source-only change is staged without
    landing it on the default branch
- Gate: Verification Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-006 | produces-consumes | The resolution decides the items the inventory lists |
| T-006 | T-007 | produces-consumes | The persisted list records the resolutions this task decides |
| T-007 | T-005 | produces-consumes | The reconciliation applies the items the persisted list carries |
| T-007 | T-008 | verification | The review assesses the persisted list |
| T-009 | T-010 | produces-consumes | The notation must reproduce the enumerated anchor identifiers |
| T-009 | T-011 | verification | The page verdict compares against the enumerated anchor baseline |
| T-010 | T-002 | contract | The renderer implements the defined source notation |
| T-010 | T-003 | contract | The approach binds to the notation the source must express |
| T-010 | T-012 | produces-consumes | The counting rule classifies lines against the defined notation |
| T-010 | T-013 | contract | The walkthrough exercises the defined notation |
| T-003 | T-002 | contract | The renderer binds to the approved approach |
| T-003 | T-015 | contract | The check mode binds to the approved approach |
| T-003 | T-022 | contract | The strategy's mechanical checks bind to the approach's determinism and check design |
| T-002 | T-005 | produces-consumes | The reconciliation regenerates the published file with the renderer |
| T-002 | T-015 | produces-consumes | The check mode re-renders using the renderer |
| T-002 | T-017 | produces-consumes | The banner is emitted by the renderer |
| T-005 | T-008 | verification | The review assesses the applied resolutions |
| T-005 | T-011 | verification | The page verdict is taken on the regenerated page |
| T-005 | T-013 | produces-consumes | The walkthrough starts from the reconciled source |
| T-005 | T-014 | produces-consumes | The count is taken over the reconciled source |
| T-017 | T-011 | verification | The page verdict includes the banner at the top of the page |
| T-012 | T-014 | produces-consumes | The count applies the recorded counting rule |
| T-015 | T-016 | produces-consumes | The workflow step runs the check mode |
| T-015 | T-018 | produces-consumes | The documented command is the one the check reports |
| T-016 | T-004 | verification | The cross-platform evidence comes from the wired workflow run |
| T-016 | T-019 | verification | The demonstration runs the wired workflow |
| T-016 | T-020 | verification | The confirmation assesses the delivered change set |
| T-018 | T-020 | verification | The confirmation covers the documentation change in the same change set |
| T-022 | T-004 | produces-consumes | The determinism checks come from the strategy |
| T-022 | T-019 | produces-consumes | The demonstration design comes from the strategy |
| T-004 | T-021 | produces-consumes | The closure record states what the determinism evidence showed |
| T-008 | T-021 | produces-consumes | The closure record states what the list review found |
| T-011 | T-021 | produces-consumes | The closure record states what the page verdict found |
| T-013 | T-021 | produces-consumes | The closure record states what the walkthrough found |
| T-014 | T-021 | produces-consumes | The closure record carries the reported markup count |
| T-019 | T-021 | produces-consumes | The closure record states what the demonstration showed |
| T-020 | T-021 | produces-consumes | The closure record carries the behaviour confirmation |
| Owner of the repository's verification workflow, delivered by ticket CKA-03 | T-016 | external | The drift step is added to a workflow this plan does not own |

### 8.2 External Dependencies

| Responsible party | What is needed | Blocks |
|---|---|---|
| Owner of the repository's verification workflow, delivered by ticket CKA-03 | The workflow keeps a matrix covering both platforms and accepts an added step expressed over a known build output, without restructuring | T-016 |

### 8.3 Implementation Order

- Wave 1: T-001, T-009
- Wave 2: T-006, T-010
- Wave 3: T-003, T-007, T-012
- Wave 4: T-002, T-022
- Wave 5: T-005, T-015, T-017
- Wave 6: T-008, T-011, T-013, T-014, T-016, T-018
- Wave 7: T-004, T-019, T-020
- Wave 8: T-021

## Suggested Workflow

Selected workflow: `implement-feature`.

Selected because the plan delivers new functionality against an approved scope with measurable
acceptance criteria, carries unresolved design decisions that need an approved technical
approach, produces a change set that must be reviewed and verified, and closes with
documentation and release communication.

| Phase | Tasks |
|---|---|
| `scope-and-acceptance` | T-001, T-006 |
| `execution-planning` | plan handoff, this artifact |
| `solution-design-and-risk-assessment` | T-003, T-009, T-010 |
| `implementation` | T-002, T-005, T-007, T-015, T-016, T-017, T-018 |
| `quality-review` | T-004, T-008, T-011, T-012, T-013, T-014, T-019, T-020, T-022 |
| `documentation-and-release-handoff` | T-021 |

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
| context-discovery | T-001 | omn-context-agent | Primary |
| scope-definition | T-006 | omn-product-owner | Primary |
| acceptance-authority | T-006 | omn-product-owner | Primary |
| architecture-analysis | T-003, T-009 | architect | Primary |
| technical-approach-definition | T-003, T-010 | architect | Primary |
| structural-risk-analysis | T-003 | architect | Primary |
| implementation-delivery | T-002, T-005, T-007, T-015, T-016, T-017 | omn-dev-1-implement | Primary |
| code-review | T-008, T-011, T-013, T-020 | omn-dev-2-reviewer | Primary |
| governance-enforcement | T-020 | omn-dev-2-reviewer | Primary |
| quality-verification | T-004, T-014, T-019 | omn-qa | Primary |
| validation-design | T-012, T-022 | omn-qa | Primary |
| documentation | T-018, T-021 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S02 | business/domain-modeling.md | T-001, T-006 | Primary |
| S01 | architecture/clean-architecture-checklist.md | T-003, T-010 | Primary |
| S07 | testing/testing-strategy.md | T-004, T-012, T-019, T-022 | Primary |
| S12 | error-handling/error-handling-strategy.md | T-015 | Secondary |
| S11 | logging/observability-logging.md | T-016 | Secondary |
| S10 | git/git-collaboration.md | T-016, T-019 | Secondary |
| S09 | security/secure-engineering.md | T-008 | Advisory |

## Acceptance Criteria

1. No item of authored prose, table, or code sample is present in exactly one of the two handbook
   files after the change. Verifies business objective 1. Evidence: the persisted resolution list
   from `T-007`, reviewed at `T-008` against the pre-change comparison from `T-001`.
2. Regenerating the published handbook from the committed source reproduces the committed
   published file with zero differing bytes, on every platform in the repository's verification
   matrix and on repeated runs in one environment. Verifies business objectives 1 and 2.
   Evidence: the determinism record from `T-004`.
3. A change to the source handbook that lands without a regenerated published file is failed by
   the repository's verification workflow, and the failure output carries the regeneration
   command as a string a contributor can run unmodified; the same workflow passes where the two
   files agree. Verifies business objective 2. Evidence: the demonstration record from `T-019`.
4. A contributor is told, both in contributor-facing documentation and at the top of the published
   page, that the published handbook is generated and how to regenerate it, and no
   contributor-facing text instructs synchronising the two files by hand. Verifies business
   objective 3. Evidence: the text review recorded at `T-018` and the page verdict at `T-011`.
5. A documented and demonstrated regeneration command is available to the follow-on ticket CKA-12
   at this change's closure. Verifies business objective 4. Evidence: the closure record from
   `T-021`, naming the command and the run that demonstrated it.
6. The published handbook still offers the chapter navigation index, chapter labels, callout
   blocks, the chain diagram, and code samples whose comment lines are distinguishable from the
   commands, and every anchor identifier it exposed before the change still resolves to the
   section carrying the same material. Verifies business objective 5. Evidence: the reviewer
   verdict from `T-011` against the anchor baseline from `T-009`.

## Definition of Done

- [ ] All six plan acceptance criteria are verified with recorded evidence
- [ ] Scope, Design, Review, Verification, and Closure Gates are approved with owners recorded
- [ ] Task acceptance criteria for `T-001` through `T-022` are satisfied or formally waived
- [ ] `A-001` through `A-010` are confirmed or converted to recorded decisions
- [ ] `R-001` through `R-011` are closed or accepted with named owners
- [ ] `Q-001`, `Q-002`, and `Q-003` are closed or explicitly accepted with the decision recorded
- [ ] The resolution list is persisted at a named path and referenced from the change's evidence
- [ ] The repository's test suite is green and every proof script reports PROVEN
- [ ] Documentation and release-impact notes are published
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Does the handbook already carry maintenance material that can hold the regeneration instruction, or must such material be added within this change? | No | omn-documentation | T-018 |
| Q-002 | The parity test's docstring is contributor-facing prose inside a test file. Does correcting it belong to the documentation owner or to the implementation change set? No phase of the selected workflow assigns prose inside test files to a single owner, so the boundary is recorded rather than assumed. | No | omn-tech-lead | T-018 |
| Q-003 | If the recorded authored-content test would drop a string that an existing test asserts, which governs: the test that asserts the string, or the resolution rule that drops it? | No | omn-product-owner | T-005, T-006 |

## Traceability Matrix

| Statement | Covered by |
|---|---|
| S-001 the handbook is published in two files, the second hand-authored with its own design system | T-001 |
| S-002 the two forms are kept in step by hand and nothing verifies agreement | T-016, T-019 |
| S-003 the two forms currently disagree on a whole section and on the order of the gate-ownership material | T-001, T-005 |
| S-004 one file becomes the source and the other a build output | T-002 |
| S-005 a renderer reads the source file and writes the published file | T-002, T-003 |
| S-006 output is deterministic: same input, byte-identical, on every platform in the matrix | T-003, T-004 |
| S-007 the tool uses the standard library only | T-003, A-001 |
| S-008 a one-time two-way reconciliation resolves every one-sided piece of content section by section | T-001, T-005 |
| S-009 published-form content is merged or deliberately dropped, with the decision recorded | T-006, T-007, T-008 |
| S-010 the branch naming templates section is rendered into the published file | T-005 |
| S-011 after the change no content is present in exactly one file | T-005 |
| S-012 the published form's reading affordances are preserved | T-009, T-010, T-011 |
| S-013 how the source expresses those affordances without becoming unreadable is answered here | T-010, T-012, T-013, T-014 |
| S-014 a check mode re-renders in memory, compares byte for byte, exits nonzero, and prints the regeneration command | T-003, T-015 |
| S-015 the check is wired into the existing verification workflow | T-016 |
| S-016 the published file carries a visible generated, do-not-edit banner naming its source and command | T-011, T-017 |
| S-017 the hand-synchronisation process note is retired and replaced by the generation instruction | T-018 |
| S-018 editing the source without regenerating fails verification with the fix command | T-015, T-019 |
| S-019 the change is additive and alters no runtime or gate-decision behaviour | T-003, T-020 |
| S-020 the hook follows the dependency ticket's discovery discipline, a step over a known build output | T-016 |
| S-021 the backlog definition of done: tests green, proof scripts PROVEN, no gate-decision change, handbook regenerated | T-020, T-021 |
| S-022 this run's artifacts observe the recorded writing constraints | A-004 |
| S-023 the follow-on ticket CKA-12 depends on this change | T-021 |
| S-024 D-001, affordance preservation is inside the boundary and the byte comparison cannot decide it | T-010, T-011 |
| S-025 D-002, one-sidedness covers authored content, not presentational markup and derived labels | T-006, A-005 |
| S-026 D-003, the source is the Markdown and the published HTML is the build output | T-002 |
| S-027 D-004, the source's existing order governs and the published form moves to match it | T-005 |
| S-028 D-005, resolve one-sided content and change no content beyond that | T-005 |
| S-029 D-006, affordance preservation is accepted by review rather than by an automated check | T-011, R-009 |
| S-030 the existing parity and dependency-footprint tests bound what the reconciliation may drop | T-005, A-007 |
| S-031 exclusions X-001 to X-007 bound the change | Scope, Out of Scope |
| S-032 fourteen acceptance criteria decide this change, each naming its verification method | T-001, T-022 |
| S-033 SGC-1, fact-stating published-form wording is authored content and merges into the source | T-006 |
| S-034 SGC-1, label-only or route-only published-form strings are derived presentation and are dropped | T-006 |
| S-035 SGC-1, every drop is recorded and ambiguous items escalate rather than being decided by the implementer | T-006, T-008, A-005 |
| S-036 SGC-1, the footer source statement folds into the generated banner rather than being merged twice | T-006, T-017 |
| S-037 SGC-2, the raw-markup-line measure is defined as a rule an independent reviewer can apply | T-012, T-014 |
| S-038 SGC-2, the anchor criterion governs over the markup-count criterion, which is reported rather than enforced | T-012, T-014 |
| S-039 SGC-3, anchor notation is answered explicitly over the fixed set the published file exposes today | T-009, T-010, T-011 |
| S-040 SGC-4, the instruction is corrected in the parity test docstring, `README.md`, and the handbook's maintenance material | T-018, A-009, A-010 |
| S-041 SGC-4, committed change proposals and run evidence are outside this criterion's reach | T-018, Scope, Out of Scope |
| S-042 SGC-5, the resolution list is persisted as a named implementation-phase artifact | T-007 |
