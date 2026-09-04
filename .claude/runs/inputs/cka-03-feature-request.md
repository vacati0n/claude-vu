# Feature Request — CKA-03: CI workflow gating every PR (tests + verifiers, by discovery)

## Source

Ticket CKA-03 in the adoption backlog under `docs/` (Epic A — Verification baseline,
Days 0–30). Source recommendation: R1 of the adoption review (2026-08-27).
Type: Story. Priority: Highest. Effort: M. Depends on: CKA-01 (delivered,
run-efe092286625) and CKA-02 (delivered, run-e0dba6763475).

## Request

Nothing gates a pull request today: the unit-test suite and the framework's proof
scripts run only when a contributor remembers to run them locally. The adoption review
identified this as the highest-leverage baseline gap — a regression in any verifier or
test can merge silently.

Deliverable: a new CI workflow that runs on every pull request (and on pushes to the
default branch) with two verification surfaces, both located **by discovery, never a
curated file list** (the reviewed sibling project's failure mode was a hand-curated
test list that silently ran 14 of 77 suites):

1. The unit-test suite via `python -m unittest discover -s tests` from the repo root.
2. Every proof script matching `verify_*.py` under the framework payload runtime
   directory, each executed individually and asserted to exit successfully with its
   `PROVEN` verdict. A failing script must fail CI **naming that verifier**.

Platform matrix: ubuntu and windows runners.

Rollout policy (encoded in the workflow, documented where contributors will see it):
- Verifier jobs are advisory (non-blocking) for the first week after merge, then
  required.
- The windows job is advisory for week 1.
- The ubuntu unit-test job is required from day one.

## Acceptance criteria (from the ticket, verbatim)

- A PR that breaks any single verifier fails CI naming the verifier.
- Adding a new `tests/test_*.py` or `verify_*.py` file is picked up with no CI config
  change.

## Constraints

- Additive change only: the ticket list forbids altering `record_gate_decision`, the
  gate matrix semantics, producer exclusion, `runner._require_approval`, or any
  human-block path. This ticket adds CI configuration and, at most, a small discovery
  helper script; it changes no runtime behavior.
- Discovery, not curation: no workflow step may enumerate test or verifier files by
  name in a way that requires editing CI config when a file is added.
- Known operational facts the design must absorb:
  - The recovery proof script is timing-sensitive under CPU load (a backoff-deadline
    assertion) and its crash can leave injected runs behind that fail the self-hosting
    proof's run-accounting check downstream — verifier ordering/isolation in CI must
    not let one flake cascade.
  - Some render tests assert color output and fail spuriously when `NO_COLOR` is set
    in the environment; CI must not set it.
  - The working tree currently carries three pre-existing orphan run directories from
    2026-08-27 that fail the self-hosting run-accounting check (S8); a follow-up task
    exists. CI design must state how this is handled (advisory window covers it, or
    the orphans are cleaned first) rather than shipping a permanently red required job.
- Definition of done for every ticket in the backlog: `tests/` green, all `verify_*.py`
  proof scripts PROVEN, no change to gate-decision behavior, and where docs were
  touched, `user-guide.html` updated to match.

## Priority and deadline

Highest priority; the closing ticket of Phase 1 (Days 0–30) of the adoption plan.
CKA-06, CKA-07, CKA-08, CKA-09, CKA-13, and CKA-15 all depend on this CI hook existing.
