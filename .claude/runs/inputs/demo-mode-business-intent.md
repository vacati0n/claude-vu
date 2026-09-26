# Business Intent — Showing the framework working

## The problem this exists to solve

The framework's value is invisible. What it produces is a governed trail: artifacts, gate
decisions, validation reports, recovery ledgers. Every one of those is the right output for an
auditor and the wrong output for a first meeting. Explaining the framework today means
narrating a state table to someone who has no reason yet to care, and the claim doing the most
work in that conversation — that specialist agents hand work to each other and that no agent
can get past a human checkpoint — is precisely the claim a table cannot demonstrate.

## Target users

| User | What they need |
|---|---|
| Presenter | To show the framework working, without spending a day editing video |
| Prospective adopter, non-technical | To understand the shape of the process without reading the screen |
| Prospective adopter, technical | To confirm the film is a real run and not a staged mock-up |
| Existing team | A short reference cut of a lifecycle, for onboarding |

The second is the demanding one and drove the final design. The stated audience is older and
non-technical. They will listen rather than read; they will not pause and scrub; they will not
know what a dispatch is. A film for them must run long enough to follow, explain each step in
ordinary words, and carry captions for anyone who cannot hear it.

## Business outcomes sought

- A presenter can produce a distribution-ready demonstration from a real run without editing.
- What is shown is evidence, not a mock-up: every frame is the real application, and the film
  states how it was condensed.
- The demonstration can be re-cut for a different audience from the same recording, because
  recording is the expensive part and it should happen once.
- A presenter who is not the author can deliver it, from a written script.

## Non-goals

- Not a monitoring or observability product. The markers exist to cut a film, not to run a
  dashboard.
- Not a general video editor. It edits one thing: a recording of a run, against that run.
- Not a replacement for the final report, the completion package, or the recovery ledger.
- Not a way to make a run look better than it was. A rejection, a retry, and a condensed wait
  are all shown, with the condensation factor stated on screen.

## Constraints the business places on the solution

- A demonstration is made to be published, so nothing that was not part of the run may end up
  in it. This is the hard constraint, and it outranks completeness of the film.
- The capability must cost nothing when unused. A team that never runs a demonstration must
  not pay for its existence in dependencies or in runtime.
- No new mandatory dependency, because the framework installs into other people's repositories.

## How success is judged

A complete lifecycle, filmed live, cut without human editing, understandable end to end by
someone meeting the framework for the first time, and verifiably free of anything that was not
part of the run.
