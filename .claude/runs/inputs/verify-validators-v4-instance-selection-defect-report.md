# Defect Report — verify_validators V4 still fails: instance selection ignores whether the mutation applies

## Summary

The previous repair of V4 (run `run-d8937789961e`, proposal FC-018) fixed the investigation-report
row. `python runtime/verify_validators.py` from the repository root still reports 5 of 6 checks and
`NOT COVERED`, now for a different artifact type. V4 fails for `orchestration-result.md` with:
no mutation anchor for "deciding the gate its own coordination record is the evidence for" in this
instance. The instance is the closure record that the previous repair run itself committed.

## Observed behaviour

- `conforming_instance` returns the last committed instance of the type, in sorted run-directory order.
- The newest committed orchestration result is the closure record of run `run-d8937789961e`.
  A closure record cannot carry its own gate decision, so its only owned row names gate `none`, and
  the derived mutation `award_itself_its_own_gate` finds no row to mutate and returns no anchor.
- V4 then reports the type as uncovered even though the validator rejects the mutation on every
  instance that does carry a gate row (the earlier fix-bug and refactor closure records).

## Expected behaviour

V4 verdicts must not depend on which run committed an artifact last. For each artifact type V4
should use an instance that is conforming and to which the declared mutation applies, trying the
committed instances from newest to oldest, then the governance artifact, then the fixture, and should
fail only when none of them can carry the mutation, naming every candidate that was tried.

## Reproduction

1. From the repository root run `python runtime/verify_validators.py`; V4 fails as above.
2. Read `conforming_instance` and `committed_instances` in `runtime/verify_validators.py`: they take
   `committed[-1]` without testing the mutation against it.

## Evidence and history (verify; do not trust blindly)

- The previous triage concluded that only the investigation-report row was fragile and that the six
  derived rows were lightly fragile. This defect refutes that for the orchestration-result row, so
  the earlier conclusion that no fallback to another instance was needed does not hold.
- The investigation-report derivation added by the previous repair (`recommend_an_unevaluated_option`,
  `resolve_mutation`, `mutation_verdict`) is correct and must be kept.
- Both defects have the same root cause: selection of one instance per type without checking that the
  mutation applies to it. Fixing the selection fixes the class, so any other type that has a
  committed instance without its anchor is covered by the same change.

## Severity and impact

Medium. It makes check FR-02 of the framework release checklist fail whenever the newest committed
instance of a type lacks the anchor, which any ordinary closure or review record can cause.

## Constraints

- Do not weaken V4: a validator that accepts a mutation, or rejects it by the wrong check, must still
  fail V4, and a type for which no candidate instance can carry the mutation must still fail loudly.
- Keep the instance conforming: V3 (the conforming instance passes its validator) must still be
  checked against the instance V4 uses.
- Do not modify, delete or re-generate committed run evidence, and do not change any registered
  validator, template or fixture.
- Add automated regression tests in `tests/` that fail before the fix and pass after: at least a
  newest instance lacking the anchor with an older instance that has it, and the case where no
  candidate can carry the mutation.
- Report, for each of the 13 registered types, how many committed instances exist and how many lack
  the anchor, so the true extent of the fragility is known.
