# Defect Report: the refactor workflow cannot hand phase 2 to phase 3

Routed as change class `defect-repair` by `config/self-hosting-profile.md`, whose Scope Rule
`SR-1` places the offending file inside the framework surface.

## Observed behaviour

`workflows/refactor.md` declares a linear five-phase chain in which
`refactor-implementation` depends on `safety-net-establishment`. The runtime offers a phase
the artifacts of its declared dependencies, under the `identifier` the producing agent's
manifest gives its own output (`runtime/framework_runtime.py`, `upstream_inputs`).

`agents/omn-qa/manifest.yaml` declares exactly one output identifier, `validation-report`.
`agents/omn-dev-1-implement/manifest.yaml` accepts exactly three input identifiers:
`technical-design`, `bug-analysis`, `test-baseline-record`. The two sets are disjoint, and the
run-level inputs of a `refactor` run (`change-request`, `business-intent`,
`architecture-context`) intersect neither. Guard `G5-INPUT` therefore blocks the phase:

    G5-INPUT: [request-validation-failure] no accepted input type supplied;
    accepted: ['technical-design', 'bug-analysis', 'test-baseline-record']

The third accepted identifier, `test-baseline-record`, is produced by no agent in the
framework. It occurs in exactly two places in the whole tree: the accepted-input list in
`agents/omn-dev-1-implement/manifest.yaml`, and one enumeration comment in
`templates/implementation-report.md`. It reads as the name the safety-net phase's output was
once expected to carry.

This is observable now, not hypothetically: in `run-34ca35504b72`, phases 1 and 2 are
`completed` with validated artifacts, and `refactor-implementation` stands `blocked` with
recorded reason `awaiting_dependency_output` and the guard detail quoted above.

## Expected behaviour

The phase that implements a behaviour-preserving refactor should accept the artifact its own
workflow declares as the output of the phase it depends on. `agents/omn-dev-1-implement`
already states this intent in its `minimumSatisfaction` prose, which names "a baseline
validation record for a behaviour-preserving refactor" as the third way its contract can be
satisfied. The manifest's accepted list does not implement that sentence.

## Reproduction

1. `plan --command refactor` with the three refactor inputs.
2. Execute `scope-invariants-and-risk-profile`, approve the Invariant Gate, execute
   `safety-net-establishment` to a validated `validation-report`.
3. `next --run-id <run>`: `refactor-implementation` is `blocked` at `G5-INPUT`, and nothing in
   the run is dispatchable.

## Impact

The `/refactor` command cannot complete a run. Three of its five phases are unreachable through
the documented usage, and the two gates that assess them can never be decided.

The break is specific to this phase. The other two phases that dispatch
`agents/omn-dev-1-implement` resolve correctly and are demonstrated by completed runs:
`implement-feature/implementation` receives `technical-design` from
`solution-design-and-risk-assessment`, and `fix-bug/fix-implementation` receives `bug-analysis`
from `root-cause-analysis`.

There is a second-order governance consequence. Completion Rule `C-3` of
`config/self-hosting-profile.md` accepts a phase only as executed with a validated artifact or
blocked with a recorded reason. The scheduler records a block only on the frontier phase; a
phase behind an unfinished predecessor receives a `wait` verdict and stays `pending`, which is
neither accepted state. A run stalled by this defect therefore fails `C-3` permanently, and
check `S8` of `verify_self_hosting.py` counts it as unaccounted with no change proposal able to
rescue it. `run-34ca35504b72` is in exactly that condition and is the reason the framework
currently reads `7/8 -- NOT SELF-HOSTING`.

No validated evidence has been lost. Both completed phases retain their artifacts and gate
decisions.

## Severity and blast radius

Severity: high. Blast radius: every run of `/refactor`, at the transition from phase 2 to
phase 3, plus the self-hosting verdict for as long as a run sits stalled inside the window.

## Constraints on the fix

- The decided direction is to widen the consumer, not to rename the producer. `omn-qa` emits
  `validation-report` in four phases across three workflows; renaming its output identifier for
  the sake of one consumer would change three working handoffs to repair one broken one.
- The widening must be additive. `technical-design` and `bug-analysis` keep their meaning and
  their phases, and the menu contract must continue to refuse a dispatch that supplies none of
  the accepted identifiers.
- `minimumSatisfaction` prose and the accepted list must agree after the change.
- No agent gains a capability, a tool, or a write scope. This is an input-contract correction.
- The enumeration comment in `templates/implementation-report.md` should stop advertising an
  identifier no agent produces.
