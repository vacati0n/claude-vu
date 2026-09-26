```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0013
  featureName: Generated HTML handbook with a drift check
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-06-feature-request.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 14
  inputDigest: sha256:5965b9107e59775c3f70f54b0b8609f7
  contextDigest: sha256:c5cc1c3bdd1db9b2d550e98fd7f931ed
```

## Metadata

- Feature name: Generated HTML handbook with a drift check
- Requested by: the adoption backlog under `docs/`, ticket CKA-06, from recommendation R7 of the adoption review dated 2026-08-27
- Business goal: One handbook, published in two forms that cannot disagree, with divergence caught before it reaches the default branch
- Target outcome: Contributors change the handbook in one place, readers of either published form get the same handbook, and a stale published form stops a change instead of surviving it
- Scope decision date: 2026-09-05

## Business Context

- Problem statement: The operator handbook is published twice and kept in step by hand. Nothing checks that the two published forms agree, and they no longer do: one carries a whole section on branch naming templates that the other does not, and the two order the gate-ownership material differently. A reader of one form gets a different handbook from a reader of the other, and no contributor is told when the two have parted.
- Value hypothesis: If one published form is derived from the other and staleness is caught before a change lands, divergence stops recurring, and the per-change synchronisation cost that every prior delivery in this backlog has paid and recorded disappears.
- Affected users: Teams reading the operator handbook in either published form; contributors who change the handbook and today must remember to update both; the follow-on ticket CKA-12, which needs the handbook regenerated when it updates the exit-code tables.
- Success measure: No change that leaves the two published forms disagreeing reaches the default branch, because the repository's verification fails it first; and after this change no authored content is present in exactly one of the two files.

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | The published HTML handbook is a build output of the Markdown handbook: regenerating it from `docs/USER-GUIDE.md` reproduces the committed `docs/user-guide.html` exactly, and an edit made directly to the published file does not survive regeneration | Delivers the requested renderer that "reads `docs/USER-GUIDE.md` and writes `docs/user-guide.html`", restated as the source-of-truth outcome it serves rather than as the tool that realises it | must-have |
| `S-002` | A contributor who changes the Markdown handbook without regenerating the published HTML is stopped by the repository's continuous integration and told the exact command that fixes it | Delivers the stated acceptance expectation that editing `USER-GUIDE.md` without regenerating fails CI with the fix command | must-have |
| `S-003` | After this change no authored content is present in exactly one of the two handbook files: everything the Markdown carries appears in the published HTML, and everything the published HTML carried is either present in the Markdown or recorded as deliberately dropped | Delivers the requested one-time two-way reconciliation of the current drift, including the Markdown's branch naming templates section and the differing order of the gate-ownership material | must-have |
| `S-004` | The published HTML handbook keeps the reading affordances it offers today: a chapter navigation index, per-section anchors, chapter labels, callout blocks, the chain diagram, and code samples whose comment lines are distinguishable from the commands | Delivers the request's statement that these affordances are a deliberate part of the published artifact and that preserving them is part of the deliverable, not an optional extra; recorded as a boundary in `D-001` | must-have |
| `S-005` | A reader who opens the published HTML handbook is told at the top of the page that the file is generated and must not be edited, which file it comes from, and the command that regenerates it | Delivers the stated acceptance expectation that the published file opens with a "generated, do not edit" banner naming its source and its regeneration command | must-have |
| `S-006` | Regenerating the handbook from the same Markdown produces the same published file every time and on every platform the repository's verification runs on, so the staleness answer is the same everywhere | Delivers the stated hard requirement that determinism is not an aspiration, since a byte comparison is only usable if the output does not vary with ordering, locale, line endings, or platform | must-have |
| `S-007` | The Markdown handbook stays a document a contributor reads and edits as prose, so adding a section, a callout, or a code sample does not mean hand-writing markup | Delivers the request's statement that how the source expresses the affordances without becoming unreadable is a question this change must answer rather than sidestep | should-have |
| `S-008` | Contributors are told to regenerate the published handbook, and no instruction to synchronise it by hand remains anywhere they would read | Delivers the request that the hand-synchronisation process note be retired and replaced by the generation instruction | should-have |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | Generating any other duplicated documentation pair in the repository from a single source | The request names exactly one pair; every other pair has its own audience, its own content, and its own reconciliation cost that nobody has assessed | A second duplicated documentation pair is identified and its divergence is shown to recur |
| `X-002` | Any change to runtime, gate-decision, or approval behaviour | The backlog constrains this ticket to an additive change and forbids altering `record_gate_decision`, the gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path | Never within this change; such a change is scoped separately with its own gate evidence |
| `X-003` | Editorial rewriting or restructuring of handbook content beyond resolving content that exists in exactly one file | The request bounds the content change to resolving one-sided content; mixing editorial improvement into a reconciliation makes the reconciliation impossible to review | A content review of the handbook is requested as its own change |
| `X-004` | Publishing or hosting the generated handbook anywhere outside the repository | Nothing in the request asks for a hosted site; the published file is committed and read in place | A requirement to serve the handbook outside the repository is stated |
| `X-005` | Making the handbook's factual claims checkable against the tool's actual behaviour, including the exit-code tables | That is the separate follow-on ticket CKA-12, which depends on this one; conflating them would make this change's acceptance depend on content accuracy work nobody has scoped | CKA-12 is scoped, at which point it consumes this change's output |
| `X-006` | An automated visual or structural regression check that proves the reading affordances survived a regeneration | The request asks for one drift check, over bytes; a check that decides whether a page still reads well is a separate capability with its own tooling and its own failure modes, and `D-006` records that preservation is accepted by review instead | An affordance regression reaches the published handbook after this change, showing review is not sufficient |
| `X-007` | Removing the published HTML handbook from version control in favour of building it only at publish time | The drift check compares against the committed file, and existing repository tests read that file from the working tree; dropping it would defeat both | A publishing pipeline exists that builds and serves the handbook, and the repository tests no longer read the file |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | Regenerating the handbook from the committed Markdown produces a file byte-identical to the committed `docs/user-guide.html`, with no manual step in between | `S-001` | regenerate on a clean checkout and compare the working tree against the commit; the comparison reports zero differing bytes | must-have |
| `A-002` | A sentence added directly to `docs/user-guide.html`, and not to the Markdown, is absent from the file after regeneration | `S-001` | demonstration: insert one sentence into the published file, regenerate, and confirm the sentence is gone | must-have |
| `A-003` | A commit that changes `docs/USER-GUIDE.md` without regenerating `docs/user-guide.html` fails the repository's verification workflow, and the failure output contains the regeneration command as a string a contributor can run unmodified | `S-002` | run a demonstration branch carrying a Markdown-only edit through the verification workflow; the run fails and the logged output carries the command | must-have |
| `A-004` | The verification workflow passes on a commit where the Markdown and the published HTML agree | `S-002` | the verification workflow run on the delivery branch after regeneration completes without a drift failure | must-have |
| `A-005` | Every section heading present in `docs/USER-GUIDE.md` is present in `docs/user-guide.html`, including the branch naming templates section with its token reference table, its normalization and validation rules, its viewing-and-changing content, and its migration notes | `S-003` | section-by-section comparison of the two files' heading sets, plus a content read of the branch naming templates section in the regenerated output | must-have |
| `A-006` | Every item of authored prose, table, or code sample that exists today in exactly one of the two files appears in the change's evidence with its resolution recorded as either merged into the Markdown or deliberately dropped, and no listed item is left unresolved | `S-003` | review of the recorded resolution list against a section-by-section comparison of the two files as committed before this change | must-have |
| `A-007` | The regenerated published handbook still offers a chapter navigation index, chapter labels, callout blocks, the chain diagram, and code samples in which comment lines are visually distinguishable from the commands | `S-004` | reviewer walkthrough of the regenerated page against the pre-change page, item by item across the five named affordances | must-have |
| `A-008` | Every section anchor that `docs/user-guide.html` exposes before this change still resolves, after it, to the section carrying the same material | `S-004` | comparison of the anchor identifier sets before and after, followed by a click-through of each anchor in the regenerated page | must-have |
| `A-009` | The regenerated `docs/user-guide.html` opens with a banner that is visible when the page is rendered, states that the file is generated and must not be edited, names `docs/USER-GUIDE.md` as its source, and gives the regeneration command | `S-005` | open the regenerated page and read the top of the rendered page, confirming all three elements are present and legible | must-have |
| `A-010` | Regenerating from the same Markdown on every operating system in the repository's verification matrix produces byte-identical output, line endings included | `S-006` | the drift check step passing on every leg of a single verification workflow run | must-have |
| `A-011` | Two regenerations from the same Markdown in the same environment produce byte-identical output | `S-006` | regenerate twice into separate destinations and compare; the comparison reports zero differing bytes | must-have |
| `A-012` | A contributor can add a new section, a callout, and a code sample to `docs/USER-GUIDE.md` using notation already present elsewhere in that file, and the regeneration renders all three | `S-007` | authoring walkthrough: a reviewer who did not build the change adds one of each to a scratch copy, regenerates, and inspects the output | should-have |
| `A-013` | The number of lines in `docs/USER-GUIDE.md` consisting of raw markup rather than prose is no greater after this change than in the file as committed before it | `S-007` | count the raw-markup lines in both revisions of the file and compare the two counts | should-have |
| `A-014` | The repository's contributor-facing documentation instructs a contributor to regenerate `docs/user-guide.html`, and carries no remaining instruction to synchronise the two files by hand | `S-008` | text review of every contributor-facing document that mentions the handbook pair, confirming the generation instruction is present and no hand-synchronisation instruction remains | should-have |

## Constraints and Dependencies

- Business constraints: High priority, Phase 1 of the adoption plan in the adoption backlog under `docs/`. The follow-on ticket CKA-12 depends on this one for regenerating the handbook when it updates the exit-code tables, so this change gates that one. Every prior delivery in this backlog has paid a hand-synchronisation cost and recorded it in its own evidence.
- Regulatory or policy constraints: Additive change only. The backlog forbids altering `record_gate_decision`, the gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path, and this change alters no runtime behaviour and no gate-decision behaviour. Tooling is standard library only, consistent with the repository's dependency posture for tooling. Documentation this run produces avoids the vendor substring the artifact validators reject, writes framework paths without the leading dot-directory prefix, cites the source backlog as "the adoption backlog under `docs/`" and the source review as "the adoption review dated 2026-08-27", and refers to the handbook's in-editor host section as "the in-editor host section (3A)".
- Delivery constraints: The definition of done for every ticket in this backlog applies: `tests/` green, all `verify_*.py` proof scripts PROVEN, no change to gate-decision behaviour, and the published handbook regenerated wherever documentation was touched. Determinism is a hard requirement rather than an aspiration: the output must not vary with dictionary ordering, locale, line endings, or the platform running it, and both platforms in the verification matrix must agree. The continuous-integration hook follows the discovery discipline the dependency ticket established: a step over a known build output, not a curated list of files a future contributor must remember to extend.
- External dependencies: `.github/workflows/verify.yml`, delivered by CKA-03, supplies the continuous-integration hook this change binds to. The existing parity test in `tests/test_ci_workflow.py` requires the published handbook to remain a committed file carrying every stable check name and the verification workflow filename, and the existing dependency-footprint test in `tests/test_omn_agent.py` requires it to carry the tool's true dependency footprint; both bound what the reconciliation may drop.

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | Preserving the published handbook's existing reading affordances is inside this change's boundary; an outcome that satisfies the byte comparison while dropping them does not satisfy this scope | The byte comparison checks the published file against a regeneration of itself, so it cannot detect a degraded published artifact and would pass a stripped-down page as readily as the current one. The affordances are what makes the published form usable to the operator audience the handbook serves, and the supplied request names preserving them as part of the deliverable rather than as a preference | Acceptance of this change is decided partly by review, through `A-007` and `A-008`, and not by the byte comparison alone. The change must carry the affordances through the reconciliation and answer how the source expresses them, which raises its difficulty and hands an unresolved notation question to design rather than closing it by discarding the affordances | omn-product-owner |
| `D-002` | "No content present in exactly one of the two files" is read as covering authored prose, tables, and code samples, not the presentational markup and derived labels the published form necessarily carries | A published HTML form always carries markup and derived labels its Markdown source does not, so a literal reading makes the criterion unsatisfiable and would force deletion of exactly the affordances `D-001` protects. What the requester would notice the absence of is content, not scaffolding | `A-006` is assessed over authored content only. Derived scaffolding is assessed instead by `A-007` and `A-008`, so nothing is left unchecked by the narrower reading | omn-product-owner |
| `D-003` | The Markdown handbook is the source and the published HTML is the build output | The request states this direction, and only one direction lets a byte comparison decide staleness. Treating the richer published form as the source would leave the Markdown as the derived file that contributors actually read and edit, which inverts the problem rather than solving it | An edit made directly to the published handbook is lost at the next regeneration and is failed by the drift check. Anyone who has been editing that file changes where they work | omn-product-owner |
| `D-004` | Where the two files order the same material differently, the source's existing order governs and the published form moves to match it; the source is not reordered to preserve the published form's current order | After this change the published order is a function of the source, so preserving the published order would mean reordering the source to serve its own output. The ordering difference is drift to resolve, not content to protect, and `X-003` keeps editorial reordering out of this change | The gate-ownership material moves in the published handbook from the end of the driving-a-run chapter to the position the Markdown gives it, which readers of the published page will see change | omn-product-owner |
| `D-005` | The change resolves each one-sided item of authored content and records the resolution, and changes no content beyond that | The request bounds the content change to resolving one-sided content. Editorial improvement has a different reviewer and different evidence, and mixing it in would make it impossible to tell a reconciliation decision from a rewrite when reviewing the result | Content that both files already carry is carried through unchanged, including passages a reviewer would otherwise improve. Those improvements wait for the separate change `X-003` names | omn-product-owner |
| `D-006` | Preservation of the reading affordances is accepted by human review rather than by an automated visual or structural regression check | The request asks for one drift check, over bytes. A check that decides whether a page still reads well needs its own tooling, its own baseline, and its own failure handling, none of which the request funds or describes | A future regression in the affordances is not caught mechanically, only at review. `X-006` records that gap explicitly and names the condition that would bring the automated check back into scope | omn-product-owner |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | Which contributor-facing document holds the hand-synchronisation instruction this change retires? No prose note stating it was found in the repository's contributor documentation; the nearest statements are the definition of done in the adoption backlog under `docs/`, which already says the published handbook is regenerated, and the docstring of the parity test in `tests/test_ci_workflow.py`, which still describes the pair as hand-synced | no | omn-business-analyst | before implementation |
| `Q-002` | For each item of authored prose that exists today only in the published HTML, including the masthead strapline, the navigation labels that differ from the Markdown headings, and the footer sentence, is the item merged into the Markdown or dropped? The request authorises this change to decide each and record it, but names no owner for calls that change published wording | no | omn-business-analyst | before implementation |

## Handoff

- Downstream owner: `planner`, for decomposition of this boundary into an execution plan, then `architect` for the approach and `omn-qa` for the validation strategy built against these criteria
- Gate: Scope Gate. Under the Producer Exclusion Rule the decision on this artifact rests with `omn-business-analyst`, the other named owner; this agent produced the evidence the gate assesses and records no decision on it
- Evidence for the gate: eight in-scope items `S-001` to `S-008`; seven exclusions `X-001` to `X-007`, each with a reason and a revisit trigger; fourteen acceptance criteria `A-001` to `A-014`, each naming the in-scope item it bounds and the method that decides it; six scope decisions `D-001` to `D-006` with the rationale and impact behind each; two open questions `Q-001` and `Q-002`, neither blocking
- Deferred to downstream: how the source expresses the reading affordances `S-004` names without costing the readability `S-007` requires, together with every other technical, structural, and notation choice, to `architect`; task breakdown, sequence, and estimates to `planner`; the validation strategy that carries out the verification methods named against `A-001` to `A-014`, to `omn-qa`; merge, readiness, and release decisions to their owners. This artifact records no gate decision and makes no readiness claim
