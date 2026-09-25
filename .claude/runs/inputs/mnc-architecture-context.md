# Architecture Context — where build-or-not decisions live today

Current-state facts established by inspection on 2026-09-15 at runtime 0.5.0.

## Layers and insertion points

- Skills are the framework's reusable engineering knowledge, loaded per agent through the
  manifest `skills` block and per phase through the frozen context slice
  (`framework_runtime.CONTEXT_SLICE_PHASE`). S01 `skills/architecture/clean-architecture-checklist.md`
  is declared by ten agent manifests including `architect`, `omn-dev-1-implement`, and
  `omn-dev-2-reviewer`, and is a slice member of `implementation`,
  `refactor-implementation`, `quality-review`, `code-quality-review`,
  `repository-quality-scan`, `structural-compliance`, `technical-discovery`,
  `technical-validation`, `option-analysis`, and `option-synthesis`. It is 1,690 bytes and
  already carries three seed rules: "Introduce a new layer only when it reduces coupling or
  clarifies ownership", "Creating abstractions without real variation points" (common
  mistake), and "Sharing utility modules that hide cross-layer dependencies".
- Skill identity metadata (code, category, version, status) lives in `registry/skills.yaml`
  and the Skill Catalog of `skills/agent-skill-matrix.md`; skill files carry none. The
  category taxonomy is closed; extending it is a registry schema change.
- Agents are runtime module sets loaded in `manifest.yaml` `loadOrder`:
  system, identity, reasoning, execution, output, quality, examples. Host registrations
  (`agents/<id>.agent.md`) are adapters that pin `metadata.version is 1.0.0` and abort on a
  mismatch. Module digests are frozen into each run's invocation envelope; drift against a
  historical run is informational under decision GD-001.
- The dispatch prompt built by the runtime carries routing and addressing only; every
  instruction about how to do the work lives in the module set. There are no host hooks or
  settings files in this repository; the dispatch envelope is the only injection mechanism,
  and it injects the module set and the context slice.

## Where the seven decisions are made now

| Decision | Owner today | Existing rule |
|---|---|---|
| What to build | `omn-product-owner` Stage 3 (S-nnn / X-nnn), `planner` R4 and R13 | Untraced task is invented scope, a hard failure; unstated exclusion is the common drift |
| Whether to create new structure | `architect` A6 Reuse Survey, A7 options, A9 significance; identity decision rules | "Prefer the simplest architecture", "prefer extending a proven reusable component before creating new structural elements"; A6 outcomes reuse-as-is, reuse-extended, rejected, none-found; new structure only after rejected or none-found; A7.3 requires a none-found basis. Candidates today are "existing components" only: the standard library, platform capability, and installed dependencies are not named |
| Whether to reuse existing code | `architect` A6; `omn-dev-1-implement` Stage 2 reads existing code first | Same as above; implementer decision rule "prefer the smallest change that satisfies the accepted element over a wider refactor taken in passing" |
| Whether to introduce a dependency | `architect` impact type `dependency-change` scores against options; not named as architecture-significant | A9 significance list: contract change, dependency direction or boundary, structural component, costly reversal, quality-attribute tradeoff |
| How much code to write | `omn-dev-1-implement` Stage 5.2 "write the code the entry describes, and nothing the entry does not describe"; invariant 1 "accepted change only" | No route-selection rule between reuse, standard library, direct code, and new abstraction |
| When to stop | `omn-dev-1-implement` decision rule "never widen the change set"; quality check V3; `omn-dev-2-reviewer` Stage 4 lenses | Reviewer lenses: correctness, architecture, standards, security, maintainability, test-adequacy, packaging. Junk-detection lenses (duplication, dead-code, over-abstraction, generated-noise, legacy-drift, reviewability) exist for `repository-quality-scan` only |
| Safety floor | `omn-dev-1-implement` security constraint "must not weaken an existing authorization, validation, or audit path"; quality B4 no test weakened | No check names error handling, accessibility, observability, or data integrity |

## Validator constraints that bound any change

- `runtime/review_package_validator.py` `CATEGORIES` already accepts all thirteen categories
  for every review phase; only the reviewer `output.md` prose restricts the junk lenses to
  the scan phase.
- `runtime/implementation_report_validator.py` checks declared field bullets by label and
  non-emptiness (C4) and table columns by declared header (C4.5); adding a column or a
  bullet changes the contract, changing a field's description does not.
- `runtime/design_validator.py` D7.3 checks that a `none-found` row states a basis; it does
  not check which candidate kinds the basis names.
- Every artifact validator rejects the vendor substring, and the dot-directory path prefix
  is stripped before that scan (C3.2).
- `tests/test_bundled_payload.py` fails on any drift between the framework tree and the
  mirror under `omn_agent/_bundled_payload/`; `--sync` regenerates the mirror.

## Baseline measurements (2026-09-15, this worktree)

- `verify_registry_coverage.py` 6/6, 37 of 37 phases dispatchable; `verify_validators.py`
  6/6; `verify_manifests.py` 2/2; `verify_recovery.py` 41/41;
  `verify_vertical_slice.py --run-id run-c5a8d50d3238` 10/10;
  `verify_multi_phase.py --run-id run-c5a8d50d3238` 15/15;
  `verify_self_hosting.py` 7/8, S8 failing on four pre-existing runs from 2026-08-27 to
  2026-09-04 that carry no proposal (recorded as `O-005` of FC-006).
- `python -m unittest discover -s tests`: 329 tests, OK, 855 s.
- Module-set bytes: planner 91,711; architect 119,162; omn-dev-1-implement 76,418;
  omn-dev-2-reviewer 85,093; omn-product-owner 73,869; omn-qa 93,035.
- Active agents 12, skills 12 (S01 to S12), workflows 8, phases 37, commands 11.

## Environmental constraint

The repository's primary checkout carries roughly 194 uncommitted changes at runtime 0.8.0
that this worktree's base commit does not have. Of the files this change proposes to touch,
only `agents/omn-dev-1-implement/identity.md` (one line) and `templates/implementation-report.md`
have uncommitted edits there, and `runtime/framework_runtime.py` differs by about 1,700
lines. The change therefore avoids the runtime and the implementation-report template
entirely, so it can be carried onto the newer base without conflict.
