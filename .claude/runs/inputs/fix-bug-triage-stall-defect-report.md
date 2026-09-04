# Defect Report — The fix-bug workflow cannot reach any phase

## Symptom

A run of `/bugfix` enqueues all five phases of `fix-bug` and executes none of them, even
though four of the five owners are registered, host-invocable, and hold a registered validator
for the artifact their phase declares.

## Observed behaviour

`verify_registry_coverage.py` C6 reports the five phases as:

| Phase | Owner | Dispatchable |
|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | no — `awaiting_contract_reconciliation` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | yes |
| `fix-implementation` | `omn-dev-1-implement` | yes |
| `regression-validation` | `omn-qa` | yes |
| `closure-and-communication` | `omn-orchestrator` | yes |

Four phases report dispatchable, so the capability chain is not the constraint. The run still
produces no artifact.

## Business impact

`fix-bug` is one of seven active workflows and the only one whose Phase Model gives `omn-qa`
a regression-validation phase reachable from a defect report. While no run of it can complete,
`omn-qa` cannot satisfy conditions `D-4` and `D-5` of the Agent Definition of Done, and Wave 1
of the agent rollout cannot close. The same stall blocks every future defect repair routed
under `config/self-hosting-profile.md`, which is the profile's own `defect-repair` class.

## Evidence

- `workflows/fix-bug.md` Phase Model: `triage-and-impact` declares its Output Artifact as the
  prose string `severity classification and reproducibility decision`.
- `runtime/framework_runtime.py` reads that column literally and requires the resulting string
  to be both a declared output of the owning manifest and a key of the validator map.
  `omn-dev-1-bug-analyst` declares `bug-analysis.md` and nothing else, so the phase blocks at
  `G1-CAPABILITY` with `awaiting_contract_reconciliation`.
- `workflows/fix-bug.md` Phase Model: `root-cause-analysis` names that same prose string first
  in its Input column, with no ` or ` alternative.
- `runtime/README.md` records the edge-derivation rule: an earlier phase whose Output Artifact
  is named in this phase's Input column creates a **hard** edge, downgraded to soft only when
  the Input column declares an alternative the supplied inputs already satisfy.

## Suspected cause

The blocked entry phase is a hard predecessor of `root-cause-analysis`, which is a hard
predecessor of `fix-implementation`, which is a hard predecessor of `regression-validation`.
`G3-PREDECESSOR` holds each phase until its hard predecessors complete, so one blocked entry
phase holds the whole workflow regardless of how many downstream phases resolve their own
capability chain.

If that is correct, the dispatchable count is a misleading measure of what a workflow can
actually do: a phase can be individually dispatchable and permanently unreachable.

## Reproduction

1. `python .claude/runtime/framework_runtime.py plan --command bugfix --input defect-report=<this file>`
2. Observe the status of every work item.

## Acceptance criteria

- A run of `/bugfix` reaches and completes `regression-validation`, owned by `omn-qa`, with its
  artifact accepted by the registered validator.
- No phase of `fix-bug` reports `awaiting_capability_registration`.
- No previously passing verifier check regresses.
