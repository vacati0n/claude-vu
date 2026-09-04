# Architecture Decision Record

## Metadata

- ADR ID: D-002
- Title: Candidate acceptance is decided by a mechanical invariant check, and the stated guarantee is exactly that check
- Date: 2026-08-28
- Status: Proposed
- Owners: architect (author), omn-tech-lead (Design Gate)
- Related Work Items: OMT-01; modules `M-001`, `M-002`; sequencing constraint `P-002`; risk `R-001`

## Context

- Problem statement: A candidate rewrite is produced by a generative model. The model cannot prove it preserved meaning, and its own assurance that it did is not evidence. Something has to decide whether a candidate may overwrite a file that every later run trusts without re-reading, and whatever the contract then promises a reader must match what that decision actually checks.
- Business and technical constraints: `C-004` permits the framework to assert only guarantees it can decide mechanically, and requires anything else to be stated as unchecked. `C-006` requires a recoverable pre-image before any modification. Upstream statement `S-014` records that acceptance may not rest on the producing model's assurance.
- Current architecture baseline: `F-008` records the twenty-one knowledge surfaces in scope and their size. `F-009` records that the framework already separates what it checks mechanically from what it does not, in the artifact contract that forbids naming a provider and strips its own path prefix before scanning. No framework surface currently accepts generated content into a trusted file.

## Decision

- Selected option: `O-001`.
- Decision statement: A candidate is accepted only when it breaks none of a fixed invariant set extracted from the original: frontmatter reproduced byte for byte; every heading preserved in text, level, and order with none introduced; every fenced block byte-identical; every table's header cells and body row count unchanged; every link target, inline code span, declared rule identifier, and list item preserved; and the candidate not below the floor that separates compression from deletion. A candidate breaking one is refused without a retry, the original is kept byte-identical, and the loss is named. The contract states this set as the guarantee, states that semantic equivalence of reworded prose is not checked, and names the recorded difference record as the control for the remainder.
- Scope of impact: `M-001` implements the check and the refusal path. `M-002` states the checked and unchecked guarantees as separate claims, so no reader infers more than holds.

## Alternatives Considered

1. Option `O-004` — accept a candidate on the producing model's own assurance
- Benefits: No invariant set to design, no false refusals of a candidate that is in fact correct.
- Risks: A candidate that reads plausibly and quietly dropped an obligation is accepted silently into a trusted surface, and the loss surfaces later as a run behaving differently rather than as a reader noticing.
- Why not selected: Violates `C-004`. The assurance is not decidable, and `S-014` records that it is worthless as an acceptance basis.

2. Option `O-002` — a dedicated lifecycle whose own validation phase decides acceptance
- Benefits: Acceptance would be a contracted artifact judged by a registered validator, which is the framework's usual shape.
- Risks: The judgement still needs the same invariant set; the lifecycle adds phases, gates, owners, and a validator around a decision that must be made per file inside the pass, not once per run.
- Why not selected: Violates `C-002`, and misplaces the decision: acceptance is per candidate, and a phase-level artifact cannot refuse one file while accepting another mid-pass.

## Consequences

- Positive outcomes expected: Every accepted candidate has demonstrably kept its structure, its identifiers, and its code. A refusal names what was lost, so a rejected pass is diagnostic rather than opaque. The contract's promise and the implementation's check are the same statement.
- Tradeoffs accepted: The guarantee is narrower than "meaning is preserved", and the contract says so rather than implying otherwise. A correct candidate that restructures a table or merges two list items is refused; that false refusal is accepted as the safe direction of error.
- Risks introduced: `R-001` — the invariant set may miss a loss mode expressed only in prose (`A-001` false), in which case the guarantee is narrower than a careless reader assumes. `Q-001` carries the open question of whether a checkable prose-level rule exists.

## Validation Plan

- Metrics to monitor: The count of refused candidates and the invariant each broke, per session; the count of accepted candidates, each of which must have passed every invariant.
- Verification checkpoints: The rule executed against a document compared with itself, which must report nothing; the rule executed against a constructed candidate per loss class, each of which must be refused with that class named; per `P-002`, both demonstrated before any modifying path exists.
- Rollback or reversal conditions: Reverse if a loss is found in an accepted candidate that the set did not catch. Reversal is extension of the invariant set and re-execution of the demonstrations, together with narrowing the guarantee the contract states; it is not removal of the check, because no weaker acceptance rule satisfies `C-004`.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
