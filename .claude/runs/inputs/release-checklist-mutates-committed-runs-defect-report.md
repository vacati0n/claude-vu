# Defect Report — the release checklist rewrites committed run evidence

## Summary

`python .claude/runtime/verify_self_hosting.py --release-checklist` is the command every framework
change must pass (`CLAUDE.md`, `validation/framework-release-checklist.md`). Running it on a clean
checkout leaves the working tree dirty: committed run evidence under `.claude/runs/` is rewritten in
place. Contributors therefore run the checklist on a temporary copy of the tree so that they do not
commit, or have to revert, changes to a past run. An independent review recorded this as `DF-001`.

## Observed behaviour

- DF-001 (medium, always): after `python .claude/runtime/verify_self_hosting.py --release-checklist`
  on a clean checkout, `git status --short` reports
  `M .claude/runs/run-c5a8d50d3238/state.json` and
  `M .claude/runs/run-c5a8d50d3238/task-context.yaml`. The diff rewrites `updated_at` timestamps
  and re-renders the resolution `detail` of work items, for example an owner agent identifier.
- Items `FR-03` (`verify_recovery.py`), `FR-04` (`verify_vertical_slice.py --run-id run-c5a8d50d3238`)
  and `FR-11` (`verify_multi_phase.py --run-id run-c5a8d50d3238`) are the checklist items that run
  against, or write into, `.claude/runs/`. `FR-03` creates and removes its own injected runs there;
  a crash between creation and removal leaves them behind.
- The checklist itself executes every command-mode item with the repository root as working
  directory, so any item that writes run state writes the committed tree.

## Expected behaviour

- Running the release checklist leaves the working tree exactly as it found it: no modified, added
  or deleted file under the repository.
- Each verifier the checklist runs can still be run on its own, with the same arguments, and still
  proves what it proves today. `verify_multi_phase.py` still re-executes the runtime against the
  same request (`M14`) and still reports any side effect the re-execution produces.
- An automated test runs the release checklist and asserts that `git status` is unchanged
  afterwards.

## Reproduction

1. On a clean checkout: `git status --short` prints nothing.
2. `python .claude/runtime/verify_self_hosting.py --release-checklist` (exit 0, about 75 s).
3. `git status --short` prints the two modified files above.
4. Running each command item alone shows that `verify_multi_phase.py --run-id run-c5a8d50d3238`
   alone produces the same two modified files.

## Impact

- Severity: medium. Verification results are correct, but the mandatory release step corrupts the
  record it verifies unless the contributor works around it, and a careless commit would rewrite
  past run evidence.
- Blast radius: `runtime/verify_self_hosting.py` (the checklist runner), `runtime/verify_multi_phase.py`
  (the `M14` live replay), and possibly `runtime/verify_recovery.py`. No run executes differently.
