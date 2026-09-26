# Architecture Decision Record

## Metadata

- ADR ID: D-007
- Title: Determinism is fixed at the renderer's input and output boundary and defended at checkout
- Date: 2026-09-05
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: CKA-06; supplied plan tasks T-003, T-002, T-004, T-016

## Context

- Problem statement: the entire change rests on a byte comparison between a regenerated
  document and a committed one. A byte comparison is only a staleness verdict if the
  regeneration is a function of the source alone. Four named hazards can break that, and
  three of them break it silently on one platform only: dictionary ordering, locale, line
  endings, and the operating system running the tool. The fourth hazard is not in the tool at
  all. Git can translate line endings at checkout, so the committed bytes and the bytes on a
  runner's disk need not be the same, and the comparison would then fail on a correct
  renderer for a reason nothing in the tool can see or fix.

- Business and technical constraints: `C-004` requires byte identity across repeats in one
  environment and across both matrix platforms, line endings included, and is hard. `C-003`
  forbids any dependency outside the standard library, so no formatting or serialisation
  library may be used to normalise anything. `C-014` restricts the renderer to reading two
  fixed paths and writing one, so it cannot inspect or repair its environment. `C-013`
  requires the failure output to carry a regeneration command a contributor runs unmodified,
  which means the command form itself must not vary by platform if it is to be one string.

- Current architecture baseline: `F-015` establishes that the tests job runs on ubuntu and
  windows through a two-entry matrix, so both platforms exercise the same comparison. `F-026`
  establishes that the repository has no line-ending attributes file at its root, so nothing
  currently pins how any file is presented at checkout. `F-029` establishes that the
  published file's shell is self-contained apart from an external font stylesheet link, so
  the renderer's output is fully determined by the source and by a fixed template. The
  published file's content includes arrow, middle-dot, em-dash, check-mark, and ellipsis
  characters, so encoding is load-bearing rather than incidental.

## Decision

- Selected option: `O-001`, of which this is the input and output boundary.

- Decision statement: determinism is established at the renderer's own boundary and defended
  at checkout, in five parts. Encoding is stated explicitly on every read and every write, so
  no platform default and no locale setting participates. The newline written to the output
  is fixed by the renderer rather than delegated to the platform's text-mode translation, and
  the input is normalised to a single newline form before any parsing decision is taken.
  Every sequence that reaches the output is emitted in the source's document order, so no
  collection whose iteration order is unspecified can influence a byte. No value derived from
  the environment reaches the output at all: no build time, no tool version, no host name, no
  computed path, and in particular the generated banner's source-file name and regeneration
  command are literal strings written with forward slashes rather than assembled from path
  components. Checkout-time line-ending translation is pinned for the two handbook paths by a
  repository attributes file, so the bytes on a runner's disk are the bytes that were
  committed.

- Scope of impact: `M-001`, whose I/O boundary this fixes; `M-005`, the attributes file,
  which this decision licenses as new structure; `M-003`, whose byte content becomes
  reproducible; `M-004`, whose comparison step is only meaningful once this holds.

## Alternatives Considered

1. `O-002` renderer-held mapping tables

- Benefits: identical determinism properties, because the maps are held in the tool and are
  emitted in a fixed order; the boundary decisions in this record would apply unchanged.
- Risks: the same content coupling recorded against it in `D-001`.
- Why not selected: it is not a determinism alternative. It scores lower than `O-001` on
  impact surface, reuse leverage, quality attributes, and operability, and it was rejected in
  `D-001` on those grounds. Its determinism profile is neutral, so it neither strengthens nor
  weakens the case made here.

2. `O-003` a committed sidecar data file

- Benefits: none for determinism beyond `O-002`, and one specific hazard added.
- Risks: a sidecar consumed as structured data introduces a second parse whose iteration
  order must also be fixed, widening the boundary this record has to defend.
- Why not selected: rejected in `D-001` for reintroducing a hand-synchronised pair; the extra
  ordering surface is a further reason and not the deciding one.

3. `O-004` derive slugs and labels by algorithm

- Benefits: no determinism difference; derivation is as reproducible as authoring.
- Risks: none additional here.
- Why not selected: eliminated on `C-002`, as recorded in `D-001`. Determinism was not the
  criterion that eliminated it.

4. `O-005` invert the direction

- Benefits: none for determinism.
- Risks: the generated Markdown would face the same four hazards in the opposite direction,
  with no reduction in difficulty.
- Why not selected: eliminated on `C-001`.

5. Rejected within the selected option: rely on the renderer alone and add no attributes file

- Benefits: one fewer file in the change set; nothing outside the tool to reason about.
- Risks: if `A-002` is false, the windows leg fails permanently on a required check with a
  cause the tool cannot observe, and the failure reads as a renderer defect.
- Why not selected: `A-002` cannot be established from the supplied context, and `R-002` is
  the highest-likelihood risk in the change. A control that costs one line and removes the
  most likely failure mode is taken rather than deferred, and `P-005` probes it before the
  step is wired so the control's necessity is evidenced rather than assumed.

## Consequences

- Positive outcomes expected: the byte comparison becomes a staleness verdict rather than a
  platform lottery. The same source produces the same bytes on both matrix platforms, so a
  single workflow run supplies the cross-platform evidence `AC-010` asks for. A single
  regeneration command string serves both platforms, so the banner, the failure output, and
  the contributor documentation all carry one form.

- Tradeoffs accepted: the generated banner carries no build time and no tool version, so a
  reader cannot tell from the page when it was last generated or by which revision of the
  tool. That information would make every regeneration differ from the last and would destroy
  the comparison, so it is deliberately withheld; the repository's own history carries it
  instead. The attributes file is a repository-wide artifact introduced for two paths, and it
  is speculative until `A-002` is settled.

- Risks introduced: `R-002`, checkout translation on the windows leg, which this decision
  exists to control and which `M-005` addresses; `R-008`, the committed file's terminal bytes
  not matching the fixed newline policy, which would require one rewrite of that file and is
  routed by `Q-005`; `R-012`, a parsing defect surfacing as a byte difference somewhere
  unrelated, which `P-004` bounds by requiring a full match against a known-good target
  before anything binds to the comparison.

## Validation Plan

- Metrics to monitor: the count of differing bytes between two regenerations into separate
  destinations in one environment, expected zero; the count of differing bytes between the
  regenerated output and the committed file on each of the two matrix legs, expected zero;
  the pass or fail result of the drift step on each leg of a single workflow run.

- Verification checkpoints: `P-003`, the five boundary decisions fixed before the renderer
  produces any output; `P-004`, the renderer reproducing the committed file byte for byte;
  `P-005`, byte identity proven on both platforms immediately after `P-004` and before the
  drift step is wired, which is the checkpoint that decides whether `M-005` is required; the
  formal determinism evidence recorded against `AC-010` and `AC-011`.

- Rollback or reversal conditions: reverse if `P-005` shows a divergence that neither the
  boundary decisions nor the attributes file can remove, which would mean the byte comparison
  cannot serve as the staleness verdict on both platforms. Reversal is not a code change but a
  scope escalation: the comparison would have to be narrowed to one platform, which weakens
  `C-004` from hard to platform-specific, and that is a decision for the Design Gate owners
  and the product owner rather than for delivery. The attributes file is reversible on its own
  by deletion, with no effect on any file other than the two handbook paths.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
