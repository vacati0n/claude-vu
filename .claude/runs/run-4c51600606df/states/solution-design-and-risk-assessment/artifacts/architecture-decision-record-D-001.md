# Architecture Decision Record

## Metadata

- ADR ID: D-001
- Title: Non-derivable published-form values are authored in the source, not mapped in the renderer
- Date: 2026-09-05
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: CKA-06; supplied plan tasks T-009, T-010, T-002, T-003

## Context

- Problem statement: the published handbook shows values that its Markdown source does not
  contain and cannot produce by any rule. There are three such sets. The 21 section anchor
  identifiers, none of which is the slug of its own heading (`F-002`, `F-004`). The 9
  navigation labels, 4 of which differ from the heading text they point at (`F-005`). The 14
  callout tags, none of which appears in the source paragraph the callout wraps (`F-007`).
  Making the published file a build output means deciding where those values live. Nothing
  else in the change can be settled until it is, because the renderer's grammar, the source's
  authoring contract, and the anchor criterion all follow from the answer.

- Business and technical constraints: `C-002` requires every anchor identifier the published
  file exposes today to still resolve after the change, and the file's internal link graph is
  closed over exactly those identifiers (`F-003`), so losing one breaks a link as well as an
  anchor. `C-001` fixes the Markdown file as the source and the published file as its output.
  `C-010` requires a contributor to add a section, a callout, or a code sample using notation
  present in the source file, without hand-writing markup. `C-011` asks that the count of
  raw-markup lines in the source not rise, and the Scope Gate has already ruled that where
  `C-011` and `C-002` conflict, `C-002` governs and the count is reported rather than
  enforced. `C-015` requires the five named reading affordances to survive.

- Current architecture baseline: `F-001` establishes the two files and their sizes. `F-009`
  establishes that the source contains no link in bracket-and-parenthesis form and no
  blockquote line, so any construct used to carry these values is new to this document even
  when it is ordinary Markdown. `F-008` establishes that the source already marks asides with
  a bolded lead-in run, 20 times. `F-011` establishes that the two chain diagrams already sit
  in fenced blocks. `F-028` establishes that the source's chapter numbering already carries
  the structure the published page renders as chapters and subsections.

## Decision

- Selected option: `O-001`.

- Decision statement: every value the published form carries that is not derivable from the
  source is authored in the source, on the line whose rendering it governs, in one brace
  attribute construct written at the end of that line. On a heading the attribute carries the
  section's anchor identifier and, where the navigation label differs from the heading text,
  that label. On a callout it carries the block's variant where one exists. The renderer
  holds a grammar and a fixed page shell, and holds no map keyed to document content. Three
  further constructs are reused rather than invented: a callout is a blockquote whose leading
  bolded run becomes its tag, a chain diagram is a fenced block whose info string names it,
  and a code sample keeps the fenced form and info string it already has. Chapter labels, the
  navigation index, the numeric-table marking, the section nesting, and the comment marking
  inside code samples are all derived by the renderer from what the source already contains.

- Scope of impact: `M-002` gains the authoring contract; `M-003` gains its generation
  contract and keeps its 21 identifiers; `M-001` is written against this grammar and against
  nothing else. `D-002` through `D-006` and `D-010` are consequences of this decision and are
  recorded inline in the design package rather than as separate records.

## Alternatives Considered

1. `O-002` renderer-held mapping tables keyed by heading and paragraph text

- Benefits: satisfies every hard constraint; reproduces all 21 identifiers exactly; leaves
  the source's raw-markup line count untouched, which is the strongest case that can be made
  against the selected option; the source stays plain prose with no construct a contributor
  has to learn.
- Risks: gives `M-001` a content dependency on `M-002`, which is a dependency in the wrong
  direction — the tool must know the document in order to render it. A heading reworded for
  readability silently loses its anchor, because the map key no longer matches and nothing
  reports it. Adding a chapter requires editing a program.
- Why not selected: it is the highest-scoring rejected alternative and it loses on four of
  the six evaluation criteria: impact surface 3 against 2, reuse leverage 4 of 9 against 5 of
  9, operability, and `C-010`. Under this option a contributor who adds a chapter must edit a
  program to give it an anchor, which is a worse authoring burden than the markup `C-010`
  exists to avoid.

2. `O-003` a committed sidecar data file carrying the same three maps

- Benefits: satisfies every hard constraint; keeps the maps out of the tool, so the tool
  stays content-free; the source stays plain prose.
- Risks: the sidecar and the source must be kept in step by hand. That is the precise defect
  this whole change exists to remove, reintroduced one level down and with no check over it.
- Why not selected: it scores identically to `O-002` on impact surface, reuse leverage, and
  migration burden, and worse on operability. Structurally it is self-contradicting: a change
  whose purpose is to end hand synchronisation cannot be built on a hand-synchronised pair.

3. `O-004` derive slugs and navigation labels by algorithm and accept the changes

- Benefits: no new notation at all; the smallest possible authoring burden; the raw-markup
  count is untouched.
- Risks: all 21 anchors and all 21 internal links change in one commit.
- Why not selected: eliminated on `C-002`, which is a hard constraint. `F-004` establishes
  that not one identifier is derivable, so this option does not degrade the anchor set, it
  replaces it.

4. `O-005` invert the direction and generate the Markdown from the published file

- Benefits: every affordance is preserved by construction, because the richer form is the
  authored one; reuse leverage against the published file's own structure is total.
- Risks: the file contributors read and edit becomes generated markup.
- Why not selected: eliminated on `C-001`, which fixes the direction, and which the Scope
  Gate settled as a scope decision before this phase began.

## Consequences

- Positive outcomes expected: the anchor identifier set becomes an authored, reviewable
  property of the source rather than an artifact of a slug algorithm. The renderer holds no
  document content, so adding a chapter, renaming a heading, or adding a callout is a
  documentation act. The internal link graph becomes checkable at build time (`D-010`), which
  converts one part of `C-002` from a review obligation into a build-time one.

- Tradeoffs accepted: the source gains notation it does not carry today (`F-009`), so a
  contributor learns one attribute construct and one blockquote form. The brace attribute was
  chosen over a separate-line form because `AC-013` counts lines and 21 identifiers on
  separate lines would raise the count by 21, whereas a line suffix raises it by zero lines;
  whether a prose line with a trailing attribute counts as markup is the counting rule's
  decision, owned by `T-012`, and this record states the input rather than the rule. The
  chapter numbering already present in the source headings becomes load-bearing for the
  chapter label, the navigation number, and the section nesting.

- Risks introduced: `R-004`, a reconciliation item the fixed notation cannot express;
  `R-006`, a later change that renames an attribute and its links together, breaking an
  external link that no mechanical check guards because `X-006` excludes one; `R-001`, a
  baseline enumerated against a revision that is not the delivery revision.

## Validation Plan

- Metrics to monitor: the count of anchor identifiers in the regenerated published file
  against the 21 of the recorded baseline; the count of internal link targets against the
  same set; the count of navigation entries against 9; the count of callout blocks against
  14; the reported raw-markup line count for the source before and after.

- Verification checkpoints: `P-001`, the baseline fixed and its enumeration method recorded;
  `P-002`, the notation closed over every affordance and every baseline identifier before the
  renderer is built; `P-004`, the renderer reproducing the committed published file byte for
  byte; the authoring walkthrough by a reviewer who did not build the change, which decides
  `C-010` and `AC-012`; the page verdict against the baseline, which decides `C-002` and
  `AC-008`.

- Rollback or reversal conditions: reverse if the authoring walkthrough finds that a reviewer
  cannot add a section, a callout, or a code sample without consulting the builder, which
  would mean the notation failed the objective it was chosen for. Reversal means moving the
  three value sets into a renderer-held map, that is adopting `O-002`, which is reachable
  from this state because the values would already be enumerated and correct; the cost of
  reversal is the coupling `O-002` was rejected for, not rework of the values themselves.
  The source remains a valid Markdown document with or without the attributes, so no reversal
  step is destructive.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
