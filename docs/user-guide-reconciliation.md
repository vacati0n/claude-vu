# Handbook reconciliation: how the one-sided content was resolved

`docs/user-guide.html` is now a build output of `docs/USER-GUIDE.md`. Before that
change the two files were kept in step by hand and had drifted: each carried
authored content the other did not, and the two ordered some of the same material
differently.

This file records the one-time, two-way reconciliation that removed the drift. It
lists every item of authored prose, table, or code sample that existed in exactly
one of the two files before the change, and states how it was resolved and under
which rule. Nothing was resolved silently: an item that is not here was carried by
both files already. That statement is executed rather than asserted: the pre-change
published page is kept as `tests/fixtures/user-guide-pre-change.html`, the page as
regenerated when this reconciliation closed is kept as
`tests/fixtures/user-guide-reconciled.html`, the normalised comparison between the
two is recorded hunk by hunk in `docs/user-guide-reconciliation-diff.md`, and
`tests/test_render_user_guide.py` (`PreChangeEquivalence`) recomputes that
comparison from the two fixtures and fails unless every hunk is recorded there and
classified against a row of this record, an ordering entry, or a construct the
renderer derives. Both sides are frozen, so the proof stays true while the handbook
goes on being edited; a later edit to `docs/USER-GUIDE.md` is a new change, not a
reconciliation hunk.

## What was compared, and how

- Revisions compared: `docs/USER-GUIDE.md` at 1051 lines and `docs/user-guide.html`
  at 1033 lines, as committed immediately before this change. The published
  revision is the pre-change fixture named above, byte for byte; the regenerated
  page it is compared with is the reconciled fixture named above, a render of the
  source as it stood when this reconciliation closed.
- Method: a section-by-section read of both files, plus a normalised structural
  comparison of the pre-change published file against the regenerated one. The
  normalisation collapses whitespace between tags and sorts attributes, then
  compares three streams: the element-and-class sequence, the visible-text stream,
  and the declared-anchor and internal-link-target sets.
- What that comparison established: the regenerated page declares exactly the same
  21 anchor identifiers as the pre-change page, its internal link graph is closed
  over exactly those 21, and every string the repository's committed tests assert in
  either file is still present. The visible-text stream differs in 51 hunks and the
  element-and-class sequence in 66; each is recorded and classified in
  `docs/user-guide-reconciliation-diff.md`, and none is a defect.

## Rulings recorded at the Review Gate

The Review Gate (review package RP-2026-0007) found that the first revision of this
record had dropped two authored command lines with no row, had applied two
resolutions the implementer was not entitled to settle, and had described the
normalised comparison without recording it. This revision closes those findings:

- Items 21 and 22 record the two 5a command lines the published sample carried and
  the source did not. Both are merged into the source, and the published sample
  reads as it did.
- omn-product-owner ruled on the masthead strapline (`Q-001`): the two straplines
  state one fact, so the item is same material in divergent wording under `R1`, not
  a one-sided item. It is recorded in section 3, no longer in section 1.
- omn-product-owner ratified every resolution recorded as dropped: items 16, 17, 18
  and 19 in section 1 and items 43, 44 and 45 in section 2. On the two chain
  accessibility labels (`Q-002`) the ruling is that they are derived presentation
  regenerated from the token list; no authored label field is added to the chain
  construct.
- Item 12's earlier merge of the published chain's lowercase token forms had no
  rule behind it and is reversed: the source's capitalised tokens govern under `R1`
  and the lowercase forms are recorded in section 3 as superseded wording.
- Items 41 and 42 record the two source-only lead-in sentences that now render.
- Item numbers changed. Former items 17 to 21 are now 16 to 20; former 22 to 39 are
  now 23 to 40; former 40 to 42 are now 43 to 45; former item 16 is the first row of
  section 3. Items 1 to 15 are unchanged.

## The rules applied

| Rule | Clause |
|---|---|
| `R1` | The Markdown file is the source of record. Where both files carry the same material in different wording, the Markdown wording governs and the published wording is superseded. Editorial rewriting beyond resolving one-sided content is out of this change. |
| `R2` | Published-form wording that states a fact is authored content and is merged into the Markdown source. |
| `R3` | A published-form string that only labels or routes within the page is derived presentation. It is regenerated from what it labels or points at, and its divergent wording is dropped. |
| `R4` | A string a committed test asserts in either file is non-droppable. It is resolved as merged into the source, never dropped. |
| `R5` | The published footer's source statement folds into the generated banner rather than being merged into the source, so it is stated once. |
| `R6` | Content the Markdown carries and the published form did not reaches the published form by regeneration. |
| `R7` | Where the two files order the same material differently, the source's order governs and the published form moves to match it. |

Presentational scaffolding — the page title, the stylesheet, the style block, the
generated banner, the chapter eyebrow labels, the table wrappers, the numeric-table
marking, the comment marking inside code samples, and the shape a callout takes
around one paragraph or several — is not authored content. It is held by the
renderer or derived from the source, and is assessed by the page walkthrough, the
anchor comparison, and the `derived` classifications of the recorded comparison
rather than here.

## 1. Present only in the published HTML

| # | Item | Section | Resolution | Rule |
|---|---|---|---|---|
| 1 | The dependency-footprint sentence: the CLI package is standard-library only, the installed runtime files import PyYAML, the distribution declares `pyyaml`, and `pip install` pulls it | 2. Installation | non-droppable-merge — now the second half of the Prerequisites paragraph in the source | `R4`, `R2` |
| 2 | "and their module-top-level imports must resolve", qualifying what `install` validates about runtime entrypoints | 2. Installation | merged into the source | `R2` |
| 3 | ", playbooks" in the framework-managed contents cell of the "What gets installed" table | 2. Installation | merged into the source | `R2` |
| 4 | "The connector config stores only environment-variable *names*, never credentials." | 3. Two ways to work | merged into the source, inside the `MCP` callout | `R2` |
| 5 | "A scan lives at `tasks/QS-<NAME>/`" | 4.7 Scan for code junk | merged into the source as "A scan is a normal task living at `tasks/QS-<NAME>/`" | `R2` |
| 6 | "each invocation reads it plus live runtime state and performs every step it can, so re-running is always safe" | 5. Driving a run, `update` loop | merged into the source, inside the `Resumable` callout | `R2` |
| 7 | The troubleshooting row for `V-IMPORT: … imports 'yaml', which does not resolve …`, with the `pip install pyyaml` hint | 8. Troubleshooting | non-droppable-merge — added to the source's troubleshooting table | `R4`, `R2` |
| 8 | The troubleshooting row "The open PR collected review comments (reviewers, Sonar)" | 8. Troubleshooting | merged into the source, with its link to the review-comment loop | `R2` |
| 9 | The troubleshooting row "The Jira ticket changed after work started" | 8. Troubleshooting | merged into the source, with its link to the change-request loop | `R2` |
| 10 | The troubleshooting row "You want a fresh ticket driven to a PR in one go" | 8. Troubleshooting | merged into the source, with its link to the end-to-end run | `R2` |
| 11 | The framework chain's `✓` on the artifact token and the word "human" on its gate token | 1. The mental model | merged — the source's chain line now reads `artifact ✓` and marks `**human gate**` as the gate | `R2` |
| 12 | The delivery chain's "(worktree)" qualifier on the branch token, and the gate marking on its last token | 5a. Branch and Pull Request lifecycle | merged into the source's chain line. The published form's lowercase token forms are not merged: under `R1` the source's capitalised tokens (`Jira → Plan → Branch (worktree) → … → PR → Review`) govern and the lowercase forms are superseded wording, recorded in section 3. The first revision of this record had merged the lowercase forms with no rule behind it; that merge is reversed at the Review Gate | `R2`, `R1` |
| 13 | The 14 callout tags: `MCP`, `Coordination only`, `A normal task`, `Worktree isolation`, `Auto-cleanup`, `Branch safety`, `Approval model`, `Bounded rework`, `Resumable` (twice), `Errors`, `Audit trail`, `Read-only by construction`, `Your files are safe` | throughout | merged — each is now the bolded tag line opening the corresponding blockquote in the source | `R2` |
| 14 | The 21 section anchor identifiers, none of which is derivable from its own heading text | throughout | merged — each is now a brace attribute on the heading it belongs to in the source | `R2` |
| 15 | The 14 internal cross-reference links, whose targets no rule can derive from the surrounding prose | throughout | merged — each is now a Markdown link in the source, on the sentence that already made the cross-reference | `R2` |
| 16 | The four navigation labels that differed from the heading they point at: "The flows, by intent", "Yours vs. the framework's", "Keeping it healthy", "Customizing" | navigation index | dropped — the navigation label is regenerated from the heading text, so the index now reads the full chapter titles; ratified by omn-product-owner at the Review Gate | `R3` |
| 17 | The framework chain's accessibility label, "The framework chain: command to workflow to phase to owner agent to artifact to gate, then the next phase" | 1. The mental model | dropped — the label is derived from the chain's own token list; ratified by omn-product-owner (`Q-002`: derived presentation, no label field is added) | `R3` |
| 18 | The delivery chain's accessibility label, "The delivery chain: Jira to plan to branch in an isolated worktree, implement, validate, push, pull request, review" | 5a. Branch and Pull Request lifecycle | dropped — the label is derived from the chain's own token list; ratified by omn-product-owner (`Q-002`: derived presentation, no label field is added) | `R3` |
| 19 | "view or change with `omn-agent branch-config show\|set\|preview`", inside the branch-naming sentence | 5a. Branch and Pull Request lifecycle | dropped — the source's section 5b, which the published form now carries in full, gives the same instruction with its three subcommands and their flags; ratified by omn-product-owner at the Review Gate | `R1` |
| 20 | The footer sentence "This guide is versioned at `docs/USER-GUIDE.md`." | footer | folded into the generated banner at the top of the page, and not additionally merged into the source | `R5` |
| 21 | The 5a code-sample line `omn-agent pr fix-comments PROJ-42 -t ./my-repo` with its comment "# later: resolve the PR's review comments (see the rework loop)" | 5a. Branch and Pull Request lifecycle | merged into the source's 5a sample, after the `pr create` line, with the comment as written; recorded at the Review Gate (finding F-001), where its absence from the first revision of this record was found | `R2` |
| 22 | The 5a code-sample line `omn-agent update PROJ-42 -t ./my-repo` with its comment "# later: the ticket changed in Jira? carry the change to the PR (see the rework loop)" | 5a. Branch and Pull Request lifecycle | merged into the source's 5a sample, after the `pr fix-comments` line, with the comment as written; recorded at the Review Gate (finding F-001) | `R2` |

Items 17 and 18 change published wording. Whether the two chain accessibility
labels are authored content or derived presentation was routed to the product
owner as `Q-002`; the ruling is that they are derived presentation, so the chain
construct carries no label field and the labels are regenerated from the token
list.

## 2. Present only in the Markdown source

Every item below now reaches the published form by regeneration.

| # | Item | Section | Resolution | Rule |
|---|---|---|---|---|
| 23 | The whole of section `5b. Branch naming templates`: the `omn-agent init` template flags and their prompt behaviour, the "Token reference" table of three tokens, the five normalization steps and four save-time validation rules, the "Viewing and changing templates later" walkthrough, and the "Migration and backward compatibility" notes | 5b | rendered into the published form | `R6` |
| 24 | The `Routed command / Work type` table that maps `implement`, `bugfix`, `refactor`, and `investigate` onto their branch types | 5a | rendered | `R6` |
| 25 | The six-item "Guardrails" list, including `B-BASE-TIP`, the `B-STALE-BASE` warning with its 100-commit default threshold, the blocked fetch-failure case, and `--dry-run` | 5a | rendered — the published form had condensed three of these into two callouts | `R6` |
| 26 | "`.worktrees/` self-ignores via a generated `.gitignore`." | 5a | rendered | `R6` |
| 27 | The "**Implementation only runs in the task's worktree.**" paragraph and the failure cases it names | 5a | rendered | `R6` |
| 28 | The `pr precheck` test-command auto-detection detail, and "Finding none is a recorded warning, not a failure" | 5a | rendered | `R6` |
| 29 | The `pr create` detail: the `type(KEY): summary` title form, the body contents, the `Closes KEY` trailer, and the `--base` / `--draft` / `--dry-run` behaviour | 5a | rendered | `R6` |
| 30 | "Both commands write their outcome onto `tasks/<KEY>/task-plan.json`…" | 5a | rendered | `R6` |
| 31 | The `Section` column of the flows table, giving 4.1 to 4.7 | 4 | rendered | `R6` |
| 32 | "Prefer writing the scope yourself? Pass `--scope-file ./scan-scope.md`." | 4.7 | rendered | `R6` |
| 33 | The four forward pointers to sections 5a, 5c, 5d, and 5e that open the chapter | 5 | rendered | `R6` |
| 34 | The auto-approval condition qualifiers: "retries are fine if the final attempt passed", "artifact types with no severity field are unaffected", and "in the policy" | 5c | rendered | `R6` |
| 35 | "the recorded role is always a listed gate owner that did not produce the evidence", and the worked example's parenthetical | 5c | rendered | `R6` |
| 36 | The final-report detail: the `--report` sample line, one row per phase in workflow order, first dispatch and accepted completion as the endpoints, the retry note, and the actor examples | 5d | rendered | `R6` |
| 37 | The four "Consequences you can rely on" bullets in full, including which context files to fill in | 6 | rendered | `R6` |
| 38 | "and the flag wins when both are given", about the positional target argument | 2 | rendered | `R6` |
| 39 | The unabbreviated troubleshooting symptom strings, which the published form had shortened with ellipses, and the `run --dispatch` / `pr` qualifiers on four rows | 8 | rendered | `R6` |
| 40 | The `omn-agent branch` sample's inline commentary, including "The main checkout is never switched", and its `omn-agent run … --complete --phase implementation --approve` line | 5a | rendered | `R6` |
| 41 | The lead-in sentence "The ticket-driven sequence, end to end:" before the 4.1 terminal sample | 4.1 | rendered; recorded at the Review Gate (finding F-003) | `R6` |
| 42 | The lead-in sentence "The full chain from ticket to review is:" before the delivery chain | 5a | rendered; recorded at the Review Gate (finding F-003) | `R6` |

| # | Item | Section | Resolution | Rule |
|---|---|---|---|---|
| 43 | The inline label "Note: " opening the coordination-only aside | 4.6 | dropped — the block is now a callout whose `Coordination only` tag performs that labelling; ratified by omn-product-owner at the Review Gate | `R3` |
| 44 | The cross-reference wording "see \"When changes are requested\" in section 5" in the rejected-gate troubleshooting row | 8 | dropped — replaced by the published form's link text, "see the rework loop", which routes to the same section; ratified by omn-product-owner at the Review Gate | `R3`, `R2` |
| 45 | The cross-reference wording "see \"One command from ticket to PR\" in section 5b" | 3 | dropped — replaced by the published form's link to the end-to-end run: the subsection does sit under `## 5b`, and the anchor link is the more exact route to it; ratified by omn-product-owner at the Review Gate | `R3`, `R2` |

## 3. Same material, divergent wording

Both files carried these; only the wording differed. Under `R1` the source's wording
governs, so the published form now reads as the source does. No information is lost
in any of them: each pair states the same fact in different words, and the published
form was in every case the shorter of the two. The same class covers divergent
inline markup around the same words (`<em>` against `<strong>`, a code span the
published form lacked, an ordered list the published form had made unordered), a
paragraph boundary one file placed and the other did not, and a code sample one file
set as a block and the other inline.

The authoritative enumeration is the recorded comparison,
`docs/user-guide-reconciliation-diff.md`: every visible-text hunk and every
element-sequence hunk between the pre-change page and the regenerated one, each
classified. A hunk in this class cites the row below whose section it falls in. The
table is therefore an index into that comparison: where the divergences fall, and
what kind they are.

| Section | Kind of divergence | Examples of published wording now superseded |
|---|---|---|
| masthead | strapline — two straplines stating one fact, ruled same material by omn-product-owner (`Q-001`); condensed lede | "Omn-Agent AI Engineering Framework · Team Guide" for "The user guide for teams working with the Omn-Agent AI Engineering Framework"; "specialized agents own phases of real workflows, every output is validated against a contract" |
| 1. The mental model | reworded clauses | "Phases are each owned by one agent"; "Artifacts are the phase outputs (scope-definition, execution-plan, …)" without the file extensions; "Its state lives in `.omn-agent/runs/`" |
| 2. Installation | reworded and abbreviated | "Python 3.10+ and a target repository"; "No manifests detected?"; "the boundary record agents read"; "bootstrap/" for ".omn-agent/bootstrap/" in the install table's first column; the regenerate command inline rather than as a sample block |
| 3. Two ways to work | reworded, abbreviated table cells, cross-reference wording | "It routes to its workflow"; "scope, invariants & risk" for "scope, invariants & risk profile"; "implement-feature" for "implement-feature (docs phase)"; "see Auto-cleanup in chapter 5" for "see "Worktrees clean themselves up" in section 5a" |
| 4. The flows | separators and cross-reference wording | "`/investigate` · `/research`" for "`/investigate` / `/research`"; "chapter 5" for "section 5" |
| 4.1 to 4.7 | reworded lead-ins, merged paragraphs | "an agreed feature request — a ticket with no acceptance criteria is fine"; "refactor / tech-debt ticket keywords route here"; the 4.2 and 4.3 openings run into their "Enter with" paragraph |
| 5. Driving a run | condensed opening, reworded phase-cycle steps | "While agents are working, the run can be watched live in a second terminal — see below."; "Pass → transition; fail → a recorded failure envelope" |
| 5a. Branch and PR lifecycle | condensed callout prose, chain token case, inline sample | the shortened `Worktree isolation` and `Branch safety` bodies; "Branch & Pull Request lifecycle" for "Branch and Pull Request lifecycle"; the lowercase chain tokens "plan", "branch", "implement", "validate", "push", "review" for the source's capitalised ones; `({"defaultBase": "develop"})` inline for the `branch-defaults.json` sample block |
| 5. rework loop | reworded, shortened cross-references | "`--show` prints" for "`omn-agent run KEY --show` prints"; "see Auto-cleanup above" for "section 5a"; "Each phase declares a retry budget" for "Rework is bounded: each phase declares a retry budget" |
| 5. update loop | punctuation and emphasis | "`--gate …`" for "`--gate ...`"; "nothing to do" in italics |
| 5. run, any provider | cross-reference wording | "see Gate auto-approval policy below" for "section 5c" |
| 5c. Gate auto-approval | reworded, merged conditions, list form | "Opt in to let the runtime itself approve gates"; two source conditions the published form had merged into one bullet; the conditions as an unordered list |
| 5d. The final report | condensed bullets | "It's rebuilt on every aggregation"; the shortened Agent Activity and Timeline bullets |
| 5e. Watching a run live | reworded lead-in | "Every `--watch` refresh is an independent status query" for "Watching is read-only by construction. Every refresh …" |
| 6. Yours and the framework's | reworded | "using the install manifest — content hashes recorded at install time" |
| 7. Keeping it healthy | sample line order, reworded | the `upgrade` sample's two lines in the other order; "so a setup gap like a missing `dependency-map.md`" |
| 8. Troubleshooting | abbreviated symptom strings | "`INVALID TARGET: not a repository…`" for the full "target is not a repository or project root" |
| 9. Customizing | punctuation of an aside | "— testing strategy, error handling, security." for "(testing strategy, error handling, security, …)" |
| footer | separators | "the repository's `.claude/` tree · Tool: …" for "this repository's `.claude/` tree. Tool: …" |

## 4. Ordering

Three blocks of material were ordered differently by the two files. Under `R7` the
source's order governs.

| Material | Published order before | Order now |
|---|---|---|
| "Who owns which gate" | last subsection of the "Driving a run" chapter, after the live-view subsection | before the gate auto-approval subsection, where the source places it |
| The framework chain diagram | in the masthead, above the navigation index | inside chapter 1, where the source places it, immediately after the sentence that introduces it |
| The `Branch safety` callout | after the `pr precheck` / `pr create` paragraph | before the "Implementation only runs in the task's worktree" paragraph, where the source places it |

## 5. How to check this list

- Regenerate and compare: `python tools/render_user_guide.py`, then
  `python tools/render_user_guide.py --check`, which must exit zero.
- The equivalence check against the pre-change page is executed by
  `tests/test_render_user_guide.py` (`PreChangeEquivalence`): it recomputes the
  normalised comparison from `tests/fixtures/user-guide-pre-change.html` and
  `tests/fixtures/user-guide-reconciled.html`, and requires every hunk to appear in
  `docs/user-guide-reconciliation-diff.md` with a classification that resolves to a
  row of this record, an entry of section 4, or a derived construct. The test
  module's docstring states how the reconciled fixture was produced and verified.
- The anchor and internal-link assertions, the affordance assertions, and the
  branch-naming-section assertions are executed by
  `tests/test_render_user_guide.py`.
- The strings the reconciliation may not drop are executed by
  `tests/test_ci_workflow.py` and `tests/test_omn_agent.py`, which read both files
  from the working tree and are unchanged by this reconciliation.
