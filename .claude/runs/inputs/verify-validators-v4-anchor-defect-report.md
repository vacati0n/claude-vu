# Defect Report — verify_validators V4 fails once a real run commits an investigation report

## Summary

`python runtime/verify_validators.py`, run from the repository root, reports 5 of 6 checks and
`NOT COVERED`. Check V4, "every registered validator rejects a mutated artifact, by the named
check", fails for one artifact type. Before run `run-437e2f765e4b` committed its first real
investigation report, the same command reported 6 of 6. No validator, template or verifier source
file changed between the two results, so the change in outcome comes from run evidence alone.

## Observed behaviour

The failure detail names the artifact `investigation-report.md` and reads: no mutation anchor for
"recommending an option the report never evaluated".

## Expected behaviour

V4 depends on which artifacts runs happen to have committed. It should not. For every registered
artifact type it should find a conforming instance that carries the text the mutation needs, and
should still prove that the validator rejects the mutated artifact by the named check.

## Reproduction

1. From the repository root run `python runtime/verify_validators.py`.
2. Read V4: it fails for `investigation-report.md`.
3. The committed instance it selects is the investigation report of run `run-437e2f765e4b`
   (states/technical-discovery/artifacts/investigation-report.md).
4. That report's recommendation line names a different option than the literal text the V4 mutation
   table searches for, so the search finds no anchor.

## Evidence supplied by the operator (verify; do not trust blindly)

- `runtime/verify_validators.py` has a function `committed_instances(artifact)` that collects the
  artifacts of a type that committed runs produced, and `conforming_instance(artifact)` which prefers
  the last committed instance over a governance artifact or a fixture.
- The mutation table in the same file maps `investigation-report.md` to a literal search string
  `- Recommended option: ` followed by a backticked option id, replaced by a different id; the
  literal was written against the fixture's content.
- Other artifact types in that table also use literal search strings (for example the implementation
  report's `- Review status: pending-review`), so the same fragility may exist for them and be hidden
  only because the last committed instance happens to contain the literal.
- "Last committed" means last in sorted run-directory order, and run identifiers are content hashes,
  so which instance is last is arbitrary.

## Severity and impact

Medium. The failure does not corrupt data. It makes check FR-02 of the framework release checklist
fail for any framework change committed after a real investigation run exists, so it blocks a clean
release verification, and the verifier can start failing for other artifact types whenever a new run
commits an artifact that lacks a literal anchor.

## Constraints

- Do not weaken V4: it must still fail when a validator does not reject its mutation.
- Do not modify, delete or re-generate any committed run evidence, including `run-437e2f765e4b`.
- Do not change any registered validator, template or the mutation intent of any table row.
- The fix needs an automated regression test that fails before the fix and passes after, in the
  repository's existing test style (`tests/`, run by `python -m unittest discover -s tests`).
- Report how many other artifact types share the fragility, and fix them in the same change if the
  root cause is the same.
