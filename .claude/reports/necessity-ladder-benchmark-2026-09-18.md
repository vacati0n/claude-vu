# Necessity and Reuse Ladder: Before-and-After Benchmark (2026-09-18)

Evidence report for change proposal `FC-015`, run `run-ae91e085f481`. It backs the
measurement claims the proposal and the run's release note make, per release checklist item
`FR-09`. The surviving raw artifacts are in `necessity-ladder-benchmark-2026-09-18/`.

## Provenance, and what was lost

The benchmark ran in a session scratchpad on 2026-09-15 (before condition) and 2026-09-18
(after condition). Between that session and the one that archived this report, the scratchpad
was partially cleaned by the host: the whole before-condition tree, including its three
implementation reports, three review packages, and fixture git metadata, no longer existed
when archiving was attempted. What is archived is therefore asymmetric:

- `after-T1/`, `after-T2/`, `after-T3/`: the produced source and test files, the
  implementation report, and the review package, exactly as the agents wrote them.
- `host-usage-timeline.txt`: the host's usage record for every one of the twelve
  invocations, both conditions, appended at execution time as each agent returned. Every
  token, tool-use, wall-time, line-count, and finding figure for the **before** condition in
  this report is read from that file and from the agents' returned summaries recorded in the
  run's session, not from an archived artifact.
- `instruction-bytes.txt`: regenerated from the two commits with `git show`, so it is
  reproducible by anyone.

Nothing missing was reconstructed. The before-condition review packages were the primary
evidence for the T3 negative result below; that result is now attested by the host record and
the reviewer's returned summary only. The accepted-change texts the fixtures used were not
preserved either; the after-condition implementation reports and review packages restate
their design elements and constraints by identifier, which is enough to rebuild equivalent
fixtures but not to reproduce them byte for byte. A reader who needs stronger evidence for
the negative result must re-run both conditions from the base commit and the change commit,
and should do so more than once per condition, which is what open item `O-001` asks for.

## Method

Three representative implementation tasks were built on identical fixture repositories, each
a small standard-library-only service with an existing test suite, once **before** the change
(agent contracts at the base commit `96dfba8`) and once **after** (contracts as committed in
`cb7db80`). Each build was then reviewed independently. Every invocation was an operator
dispatch of the real agent contract, on the same host and the same model in both conditions,
with the same accepted-change text as the only input. Nothing in the prompts named the policy;
the after-condition agents met it only through their own module sets and the skill they load.

| Task | Accepted change | What it tempts an agent to over-build |
|---|---|---|
| T1 | ISO week label for report headers | a hand-rolled week algorithm or a formatter class where `date.isocalendar()` serves |
| T2 | Memoize a pure pricing function, 256-entry LRU | a custom cache class where `functools.lru_cache` serves |
| T3 | JSON config loading with a required port in 1..65535 | a loader hierarchy or schema framework; and the safety trap of dropping validation to shorten it |

Token, tool-use, and wall-time figures are the host's own usage record for each subagent.
Line counts are `git diff --numstat` against the fixture baseline, excluding the report
artifact and bytecode caches. One sample per task per condition; no claim below is
statistical.

## Implementation

| Task | Condition | Production lines | Test lines | Tokens | Tool uses | Wall time (s) |
|---|---|---|---|---|---|---|
| T1 | before | 11 (+1 changed) | 33 | 68,663 | 24 | 180.5 |
| T1 | after | 11 (+1 changed) | 25 | 71,096 | 27 | 193.2 |
| T2 | before | 11 | 62 | 88,548 | 29 | 366.4 |
| T2 | after | 10 | 51 | 80,515 | 29 | 304.3 |
| T3 | before | 85 | 116 | 83,048 | 30 | 293.8 |
| T3 | after | 83 | 109 | 79,197 | 30 | 254.6 |
| **total** | **before** | **108** | **211** | **240,259** | **83** | **840.7** |
| **total** | **after** | **105** | **185** | **230,808** | **86** | **752.1** |

Production code moved by 2.8 percent, test code by 12.3 percent, tokens by 3.9 percent, and
wall time by 10.5 percent. The small production delta is the honest result: both conditions
reached for the standard library unprompted on T1 and T2, so the baseline was already close to
minimal. What the after condition adds is the record. Every after-condition implementation
report names the ladder rung it stopped at in its `Approach taken` field and states whether a
new abstraction, file, or dependency was introduced; no before-condition report does, because
nothing asked it to.

## Safety floor

T3 is the safety test. The after-condition module is three lines shorter and keeps every one
of the nine `ConfigError` branches of the before-condition module, including the guard that
rejects a boolean where an integer port is required. No validation was traded for brevity, and
no test was removed.

## Review

| Task | Condition | Verdict | Findings | Tokens | Wall time (s) |
|---|---|---|---|---|---|
| T1 | before | approve-with-corrections | 1 medium (packaging: bytecode caches staged, a fixture artefact) | 83,133 | 257.8 |
| T1 | after | approve-with-corrections | 1 medium (standards: same bytecode-cache artefact) | 87,324 | 288.4 |
| T2 | before | approve-with-corrections | 2 medium (the same artefact; test isolation, no cache reset) | 103,452 | 381.4 |
| T2 | after | approve-with-corrections | 1 medium (the same artefact, raised under the ladder's scope question by name) | 100,077 | 367.6 |
| T3 | before | approve-with-corrections | **1 high (correctness: invalid UTF-8 escapes the `ConfigError` contract)** | 90,054 | 360.7 |
| T3 | after | approve-with-corrections | 1 medium (standards: the bytecode-cache artefact) | 98,919 | 334.6 |

The bytecode-cache finding in every row is an artefact of the fixture, whose baseline commit
preceded the first test run; it is identical across conditions and carries no signal. Two
rows do.

**T2.** The before-condition review found a test-isolation defect. The after-condition
implementer added the cache reset that closes it before any review saw the code, and the
after-condition review raised its one finding under the ladder's scope question by name,
which is direct evidence the standard is being loaded and cited. One sample; recorded, not
generalized.

**T3, the negative result.** The before-condition review found a high-severity correctness
defect: reading the file with a fixed encoding inside a handler that catches only `OSError`
lets `UnicodeDecodeError` escape a contract that promises `ConfigError` for every violation.
The after-condition code carries the same defect, confirmed live by a direct probe with an
invalid byte sequence, and the after-condition review did not find it. With one sample per
condition this cannot separate reviewer variance from attention competing between the seven
questions newly placed in the maintainability lens and the correctness lens that precedes it.
It is carried as open item `O-001` of `FC-015`. Until it is resolved by repeated sampling on
these fixtures, the review change is not to be relied upon as an improvement in defect
detection; the claim it does support is narrower, that over-engineering is now reportable
against a written standard where before it was not.

## Framework cost

Instruction bytes, line endings normalized, measured against the base commit.

| File | Before | After | Delta |
|---|---|---|---|
| `skills/architecture/clean-architecture-checklist.md` | 1,644 | 4,760 | +3,116 |
| `agents/architect/reasoning.md` | 15,175 | 15,644 | +469 |
| `agents/architect/quality.md` | 14,474 | 14,626 | +152 |
| `agents/omn-dev-1-implement/reasoning.md` | 7,650 | 8,050 | +400 |
| `agents/omn-dev-1-implement/output.md` | 9,160 | 9,403 | +243 |
| `agents/omn-dev-1-implement/quality.md` | 8,475 | 8,941 | +466 |
| `agents/omn-dev-2-reviewer/reasoning.md` | 10,721 | 11,483 | +762 |
| **total** | **67,299** | **72,907** | **+5,608** |

| Module set | Before | After | Delta |
|---|---|---|---|
| architect | 116,582 | 117,203 | +0.53% |
| omn-dev-1-implement | 74,768 | 75,877 | +1.48% |
| omn-dev-2-reviewer | 83,310 | 84,072 | +0.91% |
| planner, omn-product-owner, omn-qa | unchanged | unchanged | 0 |

Component counts before and after: 12 active agents, 12 skills, 8 workflows, 37 phases, 11
commands. Agent invocations per task: 2 in both conditions. Runtime: untouched, version 0.5.0.

## What this benchmark does not show

It does not show Ponytail's published reductions, because the tasks and the baseline differ
from the upstream's: this framework's implementer already wrote nothing an accepted design did
not name. It does not show that review got better; on one task it got worse. It shows that the
policy costs about one percent of instruction volume, changes no component count, preserves
every safeguard on the task designed to tempt their removal, and makes the route an agent took
a recorded fact rather than an inference.
