# Architecture Decision Record

## Metadata

- ADR ID: D-008
- Title: The drift check is a step inside the existing tests job, not a new job and not a proof script
- Date: 2026-09-05
- Status: Proposed
- Owners: omn-architect, omn-tech-lead
- Related Work Items: CKA-06; supplied plan tasks T-015, T-016, T-004, T-019

## Context

- Problem statement: the drift check has to reach a verification surface that can stop a
  merge. The repository's verification workflow offers three shapes it could take: a step
  inside an existing job, a new job of its own, or a proof script picked up by the workflow's
  discovery expression. The three differ in what they cost and, decisively, in whether their
  verdict is bound by branch protection. A check that runs, shows red, and cannot block a
  merge lets a stale published file reach the default branch, which is the outcome the change
  exists to prevent.

- Business and technical constraints: `C-005` requires the workflow's job identifier set to
  be unchanged, because a committed test asserts it. `C-006` requires the check to be
  expressed over the known build output rather than over a curated file list. `C-012`
  requires the workflow's effective text to introduce neither a colour-suppression variable
  nor a failure-masking key. `C-013` requires the failure output to carry the regeneration
  command as a runnable string, and it must reach the run log. `C-004` requires the check to
  run on both platforms.

- Current architecture baseline: `F-014` establishes exactly six jobs. `F-016` establishes
  that `tests/test_ci_workflow.py` asserts the job identifier set equals that six-element
  set, so adding a seventh job fails the unit-test suite in the same commit that adds it.
  `F-015` establishes that the tests job already provisions the interpreter, installs the
  package, runs the suite by discovery, and renders its check name with a platform suffix
  over a two-entry ubuntu and windows matrix. `F-019` establishes the workflow's own
  check-name standing: the ubuntu tests check is required from the first run, and the windows
  tests check and both verifier fan-in checks are advisory until a settings-only flip. `F-033`
  establishes that the parity test extracts steps by positional index only from the discovery
  job and the two per-verifier jobs, never from the tests job, so a step added to the tests
  job disturbs no positional extraction. `F-017` establishes that the workflow text may
  contain no filename matching the test-file or verifier-file patterns; neither handbook path
  and neither the renderer path matches those patterns.

## Decision

- Selected option: `O-001`, of which this is the verification binding.

- Decision statement: the drift check is one step inside the existing tests job. It therefore
  lands under the two rendered check names that job already produces. Its verdict is required
  from the first run on the ubuntu leg, and advisory on the windows leg until the flip; this
  record states that standing rather than assuming the flip has happened. The step is placed
  after the unit-test step and marked to run regardless of that step's outcome, so both
  verification surfaces report in a single run and neither masks the other, while the job
  still fails when either fails. Running a step regardless of a prior step's outcome is not a
  failure-masking key and introduces none, so `C-012` holds. The step invokes the renderer's
  check mode over the one known build output, naming that output rather than any list of
  files a future contributor would have to extend, which is what `C-006` asks for. No job
  identifier, no job name, and no rendered check name changes, so branch protection needs no
  edit and none is proposed.

- Scope of impact: `M-004`, which gains the step; `M-011`, which is examined and unchanged;
  `M-001`, whose check mode this binds to; `M-006`, whose assertions must still pass over the
  edited workflow.

## Alternatives Considered

1. A new job dedicated to the drift check

- Benefits: its own rendered check name, so branch protection could bind to the drift verdict
  specifically and a reader of the checks list would see staleness named as its own concern;
  its failure would be unambiguous rather than shared with the unit-test suite.
- Risks: it fails `F-016`'s assertion in the same commit that adds it, so the change would
  have to relax a committed test in order to land; and the new name would be absent from the
  required-checks list, so the drift verdict would be advisory from the start.
- Why not selected: eliminated on `C-005`, which is hard and traced to `F-016`. The Planning
  Gate condition that routed this question named the same test and the same lines.

2. A proof script picked up by the workflow's discovery expression

- Benefits: no workflow edit at all, which is the cleanest possible expression of the
  discovery discipline; the script would be found automatically and would need no
  configuration.
- Risks: its verdict reaches branch protection only through the verifier fan-in checks, which
  `F-019` establishes are advisory until the flip. The check would therefore run without
  being able to block a merge. Its reporting shape is also wrong: the wrapper parses a
  passing-summary line, whereas the drift check's contract is an exit status plus a runnable
  fix command.
- Why not selected: rejected in the reuse survey. It defeats the scope item that requires a
  contributor to be stopped, and it would fan out one more job per platform for a check that
  compares two files.

3. `O-003` a sidecar-driven variant of the same wiring

- Benefits: none for this decision; the wiring would be identical.
- Risks: none additional here.
- Why not selected: `O-003` was eliminated in `D-001` on the authoring and coupling criteria,
  not on the verification binding, which is neutral between the two.

4. `O-004` derived slugs, with the same wiring

- Benefits: none for this decision.
- Risks: none additional here.
- Why not selected: eliminated on `C-002` in `D-001`.

5. `O-005` inverted direction, with the same wiring

- Benefits: none for this decision.
- Risks: the comparison would run over the Markdown file instead, which no committed test
  reads for its content in the same way.
- Why not selected: eliminated on `C-001`.

## Consequences

- Positive outcomes expected: the drift verdict blocks a merge from the first run on the
  ubuntu leg, without waiting for any branch-protection change and without any settings edit.
  The step reuses an interpreter, a package install, and a platform matrix that already exist,
  so the added cost is one process over two files on each of two legs. The workflow's job
  topology, its four stable check names, and the parity test's positional step extraction are
  all untouched.

- Tradeoffs accepted: the drift verdict is not separately named in the checks list. A reader
  who sees the ubuntu tests check fail learns which surface failed only from the run log, not
  from the check name. This is accepted because a separately named check would either fail
  `F-016` as a new job or be advisory as a fan-in, and neither trade is worth a clearer label.
  On the windows leg the verdict is advisory until the flip, so a windows-only divergence
  shows red without blocking; this design does not depend on the flip and `Q-006` records the
  question rather than assuming an answer.

- Risks introduced: `R-003`, a placement whose verdict reaches only an advisory name, which
  this decision controls by choosing the job whose ubuntu leg is already required; `R-007`,
  the two surfaces masking one another, which the step's placement and its run-regardless
  marking control; `R-010`, a contributor who keeps editing the published file directly and
  meets a required check they did not expect, which the banner and the contributor
  documentation address.

## Validation Plan

- Metrics to monitor: the workflow's job identifier count, expected six; the four rendered
  stable check names, expected unchanged; the pass or fail result of the drift step on each
  leg of a single workflow run; the presence of the regeneration command as a runnable string
  in the failed run's log.

- Verification checkpoints: `P-006`, check mode existing and writing nothing before the
  workflow invokes it; `P-005`, byte identity proven on both platforms before the step is
  wired; `P-008`, the step added with all six job identifiers and all four check names
  unchanged and the parity test still passing; the demonstration that a source-only change
  fails the workflow and that an agreeing pair passes it, recorded against `AC-003` and
  `AC-004`.

- Rollback or reversal conditions: reverse if the step's placement is shown to hide a
  unit-test failure or a drift failure from the same run, which would mean contributors pay
  two round trips for one commit; reversal is a step reordering within the same job and costs
  nothing structural. Reverse the whole binding if `P-005` cannot establish byte identity on
  both platforms, because a step that fails one leg permanently is worse than no step; in
  that case the question returns to the Design Gate owners as a narrowing of `C-004`, not as
  a delivery decision.

## Approval

- Architect:
- Tech Lead:
- Product Owner (if scope-impacting):
