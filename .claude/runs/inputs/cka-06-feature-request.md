# Feature Request — CKA-06: Generate the HTML handbook from the Markdown handbook, with a drift check

## Source

Ticket CKA-06 in the adoption backlog under `docs/` (Epic A — Verification baseline,
Days 0–30). Source recommendation: R7 of the adoption review dated 2026-08-27.
Type: Story. Priority: High. Effort: M. Depends on: CKA-03, delivered as
`.github/workflows/verify.yml`, which supplies the CI hook this ticket binds to.

## Problem

The repository publishes its operator handbook twice: `docs/USER-GUIDE.md` (1051 lines of
Markdown) and `docs/user-guide.html` (1033 lines of hand-authored HTML with its own design
system — a light/dark token palette, a chapter navigation index, a chain diagram, eyebrow
chapter labels, stable section anchors, callout blocks with tags, and comment-highlighted
code samples). The two are kept in step by hand. Nothing checks that they agree, and they no
longer do: the Markdown carries a whole section, `5b. Branch naming templates` (lines 538 to
616, including a token reference table, normalization and validation rules, a viewing and
changing section, and migration notes) that the HTML does not contain at all, and the two
files order the gate-ownership material differently. Every prior delivery in this backlog has
paid a hand-sync tax and recorded it as such in its own evidence.

Hand synchronization cannot be made reliable by asking contributors to try harder. The fix is
to make one file the source and the other a build output, and to fail CI when the output is
stale.

## Request

Deliver three things.

1. **A renderer.** A new `tools/render_user_guide.py` that reads `docs/USER-GUIDE.md` and
   writes `docs/user-guide.html` deterministically — same input, byte-identical output, on
   every platform the CI matrix runs. Standard library only, consistent with the repository's
   dependency posture for tooling.

2. **A one-time two-way reconciliation of the current drift.** Section by section, every
   piece of content that exists in exactly one of the two files is resolved: content the HTML
   carries and the Markdown does not is merged back into the Markdown or deliberately
   dropped, with the decision recorded; the Markdown's `5b. Branch naming templates` section
   is rendered into the HTML. After the change, no content is present in exactly one file.
   Design affordances the HTML carries today (navigation, anchors, callouts, chapter labels,
   the chain diagram, code-comment highlighting) are a deliberate part of the published
   artifact: preserving them is in scope, and how the source Markdown expresses them without
   becoming unreadable is a design question this change must answer rather than resolve by
   discarding them.

3. **A drift check bound to CI.** A `--check` mode on the renderer that re-renders in memory,
   compares against the committed HTML byte for byte, exits nonzero on a mismatch, and prints
   the exact regeneration command. Wired into the existing CI workflow. The generated HTML
   carries a visible "generated — do not edit" banner naming its source file and the command
   that regenerates it. The hand-sync process note in the contributor documentation is
   retired and replaced by the generation instruction.

## Acceptance criteria (from the ticket, verbatim)

- Editing `USER-GUIDE.md` without regenerating fails CI with the fix command.
- `user-guide.html` opens with a "generated — do not edit" banner.
- No content present in exactly one of the two files after reconciliation.

## Constraints

- Additive change only. The backlog forbids altering `record_gate_decision`, the gate matrix
  semantics, producer exclusion, `runner._require_approval`, or any human-block path. This
  ticket adds a build tool, regenerates a documentation artifact, and adds a CI step; it
  changes no runtime behaviour and no gate-decision behaviour.
- The CI hook must follow the discovery discipline CKA-03 established: the check is a step
  over a known build output, not a curated list of files any future contributor must
  remember to extend.
- Determinism is a hard requirement, not an aspiration: a check that compares bytes is only
  usable if the renderer's output does not vary with dictionary ordering, locale, line
  endings, or the platform running it. Both CI platforms in the matrix must agree.
- Definition of done for every ticket in the backlog: `tests/` green, all `verify_*.py` proof
  scripts PROVEN, no change to gate-decision behaviour, and — where docs were touched —
  the HTML handbook regenerated. This ticket is the one that makes that last clause
  mechanical rather than manual, and CKA-12 already depends on it for exactly that.

## Writing constraints for every phase of this run

- Every artifact validator in this framework rejects the vendor substring "claude" in any
  case. Cite the backlog as "the adoption backlog under `docs/`" and the review as "the
  adoption review dated 2026-08-27". Write framework paths without the leading dot-directory
  prefix — `runtime/framework_runtime.py`, not the full path. Where the handbook's own
  section 3A names an in-editor agent host, refer to it as "the in-editor host section (3A)".

## Priority and deadline

High priority; Phase 1 (Days 0–30) of the adoption plan. CKA-12 depends on this ticket for
regenerating the handbook when it updates the exit-code tables.
