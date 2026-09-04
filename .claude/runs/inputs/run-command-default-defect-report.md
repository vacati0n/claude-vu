# Defect Report: A subcommand given `--run-id` re-plans the run under the default command

Framework change `FC-002`, routed as change class `defect-repair` by
`config/self-hosting-profile.md`. Reference record: `reports/defect-record-DEF-001-2026-08-18.json`.

## Observed behaviour

Every `framework_runtime.py` subcommand that takes `--run-id` also takes `--command`, whose
default is `implement`. Each of them calls `plan_run(args)` first, which materialises the run
from the command argument rather than from the run's own record. So a subcommand issued against
an existing non-`implement` run, without repeating `--command`, re-plans that run under
`implement-feature`.

Two runs were corrupted this way while executing framework change `FC-002` in self-hosting mode:

- `run-36e1d3d32384`, by `next --run-id run-36e1d3d32384`
- `run-0db4765d0eab`, by `dispatch --run-id run-0db4765d0eab --phase scope-invariants-and-risk-profile`

In both, six `implement-feature` work items were written into a `refactor` run's state store, and
the five `refactor` phases were then evaluated against the `implement-feature` Phase Model and
recorded as `workflow-contract-violation` with reason `awaiting_contract_reconciliation`.

## Expected behaviour

A run carries its command and workflow in `execution-request.json` and `state.json`. A subcommand
naming an existing run should operate on that run as it is, and an explicit `--command` that
disagrees with the stored one should be refused rather than silently applied.

## Reproduction

1. `plan --command refactor --input change-request=<path> --input business-intent=<path> --input architecture-context=<path>`
2. `next --run-id <the run id from step 1>`
3. Read `state.json`: it now carries eleven state work items across two workflows.

## Impact

The defect is not cosmetic and it is not narrow.

- It corrupts the state store irreversibly through the documented usage. `runtime/README.md`
  shows `next --run-id <run-id>` and `status --run-id <run-id>` without `--command`.
- Re-planning with the correct command does not repair it: both phase sets remain, and the
  refactor entry phase then blocks on a dependency belonging to the other workflow.
- It blocks the self-hosting operating mode for six of the seven commands the profile routes,
  because every command other than `/implement` corrupts its own run at the second step.

No artifact or validated evidence was lost in either corrupted run: no phase had executed.

## Severity and blast radius

Severity: high. Blast radius: every run of every command other than `/implement`, at every
subcommand after `plan`.

## Constraints on the fix

- The stored command is the authority for an existing run. A changed request is a different
  request and starts a new run, which is the runtime's existing rule for inputs and applies
  equally here.
- A disagreement between an explicit `--command` and the stored one is a request-validation
  failure, not something to resolve by preferring either side silently.
- No run identity changes. `run_id` is a digest of command, workflow, and inputs, and this fix
  changes none of them.
- The fix must not weaken the case it is built for: `plan` with no `--run-id` keeps its default.
