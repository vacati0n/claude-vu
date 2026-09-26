# Architecture Decision Record D-002

## Metadata

- ADR ID: D-002
- Title: Coercive auto-chain pattern inventory and structural discriminator
- Date: 2026-09-04
- Status: Proposed
- Owners: architect (producer), omn-tech-lead (accepting owner, Design Gate)
- Related Work Items: CKA-04; run run-919c5d5cf156; the plan's T-002; the plan's Q-001 and
  R-005; CKA-16 (designated widening vehicle)

## Context

Problem statement: agent contract modules must never instruct an agent to proceed past
approval gates automatically (S-005), yet the same modules legitimately use the same verbs
in prohibitions ("must not bypass the gates") and in declarative descriptions of defects
("emitting Accepted bypasses the Design Gate"). A scan that cannot discriminate turns the
suite red on an accepted tree (the plan's R-005); a scan that is too narrow misses the
failure mode it exists to catch. The plan's Q-001 asks whether the inventory must widen
beyond the four enumerated formulations.

Business and technical constraints: C-006 requires zero matches over the current agent
contract modules; C-003 requires the discrimination to be structural, never a judgment
about sentence meaning; C-004 requires each coercive fixture to be detected; S-018 requires
this record to fix the complete inventory.

Current architecture baseline: F-007 establishes the current prohibition and declarative
instances, by file and line, that any inventory must exclude; F-009 establishes the test
convention hosting the scan; no existing scanning utility exists (reuse survey,
`none-found` with search basis recorded).

## Decision

Selected option: O-001.

Decision statement: the plan's Q-001 is answered yes — the inventory widens from four
enumerated formulations to seven pattern families, and every family is matched only under a
two-part structural discriminator. A finding requires a family match and both discriminator
parts.

Pattern families. Each family is a set of verb-phrase tokens paired with a set of
gate-object tokens that must co-occur within one clause:

1. Gate-skip (enumerated): verb tokens skip, omit, in any inflection; object tokens gate,
   approval gate, quality gate, review, checkpoint.
2. Gate-bypass (enumerated): verb tokens bypass, circumvent, sidestep, work around, in any
   inflection; object tokens gate, approval, review, governance, human block.
3. Self- or auto-approval (enumerated): verb-phrase tokens auto-approve, self-approve,
   approve automatically, approve one's own; object tokens gate, decision record, own
   output.
4. Proceed-without-approval (enumerated): verb tokens proceed, continue, advance, move on,
   chain to the next phase; qualifier tokens without approval, without review, without
   sign-off, without a human decision, without waiting for the gate.
5. Approval-presumption (widened): phrase tokens treat approval as granted, treat approval
   as implicit, treat approval as optional, assume approval, consider the gate passed.
6. Self-recorded approval (widened): verb tokens record, mark, set; object tokens a gate or
   approval as approved or passed; qualifier absent the owner's decision.
7. Failure-suppression (widened): verb tokens ignore, suppress, override; object tokens a
   gate failure, a blocking question, a rejection; continuation tokens and continue, and
   proceed.

Discriminator, part one — mood filter: a family match counts only when the verb phrase is
in instructional position, meaning either (a) imperative: the verb opens a sentence or a
list item in base form, or (b) positive deontic or frequency governance: the verb is
preceded within its clause by must, shall, should, may, will, always, or automatically,
with no negation token between the governing marker and the verb. Declarative third-person
forms describing behavior or consequences do not match.

Discriminator, part two — negation guard: a match surviving the mood filter is suppressed
when a negation or prohibition token — not, never, no, cannot, must not, may not, shall
not, do not, don't, or an inflection of forbid, prohibit, disallow, refuse — occurs earlier
in the same clause, or when the verb phrase is the gerund object of a prohibition verb
(as in "forbids bypassing"). A clause is the text since the most recent sentence-ending
punctuation, colon, or line start.

Demonstration over the current tree (the F-007 instances, each excluded and by which part):

| Instance | Excluded by |
|---|---|
| "must not bypass architecture, product, security, or quality governance" (`agents/architect/identity.md`, line 192) | negation guard (not between modal and verb); mood filter also fails |
| "must not bypass the gates defined in `workflows/workflow-gate-matrix.md`" (`agents/omn-dev-1-implement/identity.md`, line 181; `agents/omn-product-owner/identity.md`, line 173) | negation guard; mood filter also fails |
| "must not bypass product, architecture, or quality gates" (`agents/planner/identity.md`, line 180) | negation guard; mood filter also fails |
| "Emitting `Accepted` bypasses the Design Gate and is forbidden" (`agents/architect/reasoning.md`, line 219) | mood filter (declarative third person); prohibition token also present in clause |
| "bypasses the Design Gate, which the contract forbids bypassing" (`agents/architect/examples.md`, line 627) | mood filter (declarative); gerund object of a prohibition verb |
| "forbids bypassing architecture decision ownership" (`agents/omn-business-analyst/quality.md`, line 111) | gerund object of a prohibition verb |

Scan scope: every module file under `agents/*/` (D-006 in the design package); an empty
scan set is itself a failure. Fixtures: one synthetic instruction per family in imperative
form and one in positive-modal form, each required to match; the F-007 prohibition and
declarative forms, each required not to match (described abstractly here; fixture authoring
belongs to the plan's T-002).

Scope of impact: M-001, M-010.

## Alternatives Considered

1. O-002 — self-contained test module with locally reimplemented parsing and alias logic
- Benefits: within it, the scan design is identical; no runtime import needed anywhere in
  the module.
- Risks: carries the alias-divergence defect that eliminates it; couples this decision to a
  package that cannot ship.
- Why not selected: the option violates hard constraint C-005 in the package evaluation
  table; eliminated.

2. O-003 — new runtime helper module hosting the check logic, including this scan
- Benefits: the discriminator would sit in the runtime where future runtime-side reuse
  (for example, validating agent contracts at load time) could consume it.
- Risks: new structure for a capability the test suite hosts; a runtime-hosted scanner
  invites treating it as enforcement, which C-001 forbids this change from adding.
- Why not selected: lower reuse leverage in the package evaluation table; the speculative
  runtime-side reuse is CKA-16 territory, not this ticket's.

## Consequences

Positive outcomes expected: the plan's Q-001 closes with a fixed, testable inventory; the
plan's R-005 is retired by construction, since prohibition and declarative phrasing fail
the mood filter or trip the negation guard; wording edits that preserve structure stay
free (C-003).

Tradeoffs accepted: precision over recall — a coercive instruction phrased declaratively or
buried in an unusual construction evades the scan. The residual is accepted because a false
red on the accepted tree blocks all delivery (C-004, C-006), while the recall gap has a
designated widening vehicle (CKA-16, S-017).

Risks introduced: R-001 (future prose matching a family despite the discriminator, or the
gate widening the inventory under A-003's failure).

## Validation Plan

Metrics to monitor: check 4 match count on the accepted tree (expected zero, permanently);
count of per-family fixture detections (expected one per fixture, permanently).

Verification checkpoints: P-004 demonstrates the current-tree zero-match with the table
above reproduced as evidence; P-005 demonstrates every per-family fixture failing the
check; the structure-preserving reword demonstration (test strategy focus areas) shows
wording freedom is preserved.

Rollback or reversal conditions: if the Design Gate narrows the inventory to the four
enumerated families, families 5 through 7 and their fixtures are removed with no effect on
the other checks; if a false positive appears on legitimate future prose, the negation
guard's token set is extended as a Correctable repair and the instance is added to the
exclusion demonstration; if false positives recur structurally, the scan reverts to the
four enumerated families pending CKA-16.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
