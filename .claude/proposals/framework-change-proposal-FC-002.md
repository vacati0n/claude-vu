# Framework Change Proposal: Repair the Defaulted Command on an Existing Run

```yaml
frameworkChangeProposal:
  proposalId: FC-002
  changeClass: defect-repair
  routedCommand: bugfix
  routedWorkflow: fix-bug
  runId: run-c9bdf5dbca7a
  profileRef: config/self-hosting-profile.md
  profileVersion: 1.0.0
  producedBy: operator
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
```

## Metadata

- Proposal identifier: FC-002
- Change title: Repair the defaulted command on an existing run
- Change class: defect-repair
- Routed command: `/bugfix`
- Run identifier: run-c9bdf5dbca7a
- Authored on: 2026-08-18

## Change Statement

- Objective: stop a subcommand issued against an existing run from re-planning that run under the argument parser's default command, which corrupted two runs during this increment.
- In scope: `plan_run` command resolution, the `--command` default in `add_request_args`, the command `cmd_dispatch` resolves its chain against, and the runtime version.
- Out of scope: run identity, the `resolve` subcommand's own default, and any change to what `plan` does when no run is named.
- Acceptance basis: the recorded reproduction no longer corrupts a run, an explicit disagreement is refused, and every prior proof still passes.

## Scope Classification

| Path | Scope Rule | Decision | Note |
|---|---|---|---|
| `.claude/runtime/framework_runtime.py` | `SR-1` | in-scope | The three call sites the defect runs through |
| `.claude/reports/defect-record-DEF-001-2026-08-18.json` | `SR-4` | out-of-scope | The defect record, emitted as evidence rather than routed as a change |
| `.claude/runs/run-c9bdf5dbca7a/state.json` | `SR-3` | out-of-scope | Run evidence written by the runtime during this change |

## Routing Decision

- Change class: defect-repair
- Selector satisfied by: a registered capability behaved other than its contract declares, in that a run carrying one command was re-planned under another
- Command: `/bugfix`
- Primary workflow: fix-bug
- Entry phase: triage-and-impact
- Required inputs supplied: `defect-report`

## Run Evidence

| Evidence ID | Link | Status |
|---|---|---|
| `E-1` | `runs/run-c9bdf5dbca7a/execution-request.json` | `/bugfix` over `fix-bug` v1.0.0, one `defect-report` input, submitted 2026-08-18T14:40:53Z |
| `E-2` | `runs/run-c9bdf5dbca7a/run-ledger.json` | Run ledger written by the runtime |
| `E-3` | `runs/run-c9bdf5dbca7a/events.jsonl` | Ordered canonical events, five work items enqueued and blocked |
| `E-4` | `runs/run-c9bdf5dbca7a/state.json` | Five phases, all blocked `awaiting_capability_registration`, each with the agent named |
| `E-5` | `runs/run-c9bdf5dbca7a/completion-package.md` | Aggregated package recording that no phase executed and why |
| `E-6` | `runs/run-c9bdf5dbca7a/state.json` | No phase of `fix-bug` is dispatchable, so the artifact link is the run's own record that every phase blocked, per the Evidence Rule |
| `E-7` | `runs/run-c9bdf5dbca7a/completion-package.md` | No phase executed, so there is no validation report; the aggregated statement of that stands in its place, per the Evidence Rule |

`E-6` and `E-7` are not taken on trust. `change_proposal_validator.py` check `F12` resolves every phase of `fix-bug` through the runtime's capability chain and confirms that none is dispatchable, and that the run records no completed phase. A proposal claiming this for a workflow that could have executed something is rejected.

## Phase Disposition

| Phase | Owner Agent | Runtime Status | Disposition | Performed By | Evidence |
|---|---|---|---|---|---|
| `triage-and-impact` | `omn-dev-1-bug-analyst` | blocked | Blocked `awaiting_capability_registration`; severity high and blast radius recorded in the supplied defect report, which names both corrupted runs | operator | `runs/inputs/run-command-default-defect-report.md` |
| `root-cause-analysis` | `omn-dev-1-bug-analyst` | blocked | Blocked `awaiting_capability_registration`; cause traced to `plan_run` resolving the command from `args.command`, whose default every `--run-id` subcommand inherits | operator | `reports/defect-record-DEF-001-2026-08-18.json` |
| `fix-implementation` | `omn-dev-1-implement` | blocked | Blocked `awaiting_capability_registration`; the operator added `stored_command`, made an existing run's own record the authority, refused a disagreeing `--command`, and pointed `cmd_dispatch` at the stored command | operator | `runtime/framework_runtime.py` |
| `regression-validation` | `omn-qa` | blocked | Blocked `awaiting_capability_registration`; the reproduction was re-run and every prior proof re-executed, recorded in Verification below | operator | this proposal, Verification section |
| `closure-and-communication` | `omn-orchestrator` | blocked | Blocked `awaiting_capability_registration`; closure is this proposal and the two discarded-run records | operator | `reports/discarded-run-run-36e1d3d32384-2026-08-18.json` |

## Gate Decisions

| Gate | Decision | Owner Role | Decided By | Rationale |
|---|---|---|---|---|
| Triage Gate | approve | omn-tech-lead | operator on behalf of omn-tech-lead | Severity high and blast radius every non-implement command accepted as stated; the defect blocks the operating mode this increment delivers, so it is repaired inside it rather than deferred |
| Fix Gate | approve | omn-dev-2-reviewer | operator on behalf of omn-dev-2-reviewer | The fix reads the run's own record, refuses a contradicting argument rather than preferring a side, and leaves run identity and the no-run-id default untouched |

The Verification and Closure Gates are recorded undecided in the completion package, because each assesses evidence a blocked phase never produced. No gate was waived.

## Verification

| Check | Command | Result |
|---|---|---|
| The recorded reproduction no longer corrupts a run | `python .claude/runtime/framework_runtime.py next --run-id run-0db4765d0eab` | pass; five refactor phases only, entry phase Ready, no implement-feature item enqueued |
| An explicit disagreeing command is refused | `python .claude/runtime/framework_runtime.py next --run-id run-0db4765d0eab --command implement` | pass; `request-validation-failure`, naming both the stored and the given command |
| Registry coverage unchanged | `python .claude/runtime/verify_registry_coverage.py` | pass; 6/6, dispatchable 3 of 36, blocked 33 |
| Validator coverage unchanged | `python .claude/runtime/verify_validators.py` | pass; 4/4 over 7 artifact types |
| Recovery behaviour unchanged | `python .claude/runtime/verify_recovery.py` | pass; 41/41 across 3 injected runs, which exercise the changed call sites |
| Committed run evidence still verifies | `python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238` | pass; 10/10 PROVEN, and the same for three further runs after the version bump |
| Multi-phase state machine still proves out | `python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238` | pass; 15/15 PROVEN |

## Risk and Rollback

- Blast radius: three call sites in one runtime module, plus the runtime version. No contract, registry record, workflow, or artifact changes.
- Risk assessment: the fix changes which value `plan_run` resolves a command from, so a caller that relied on the default to re-target an existing run would now be refused. That behaviour is the defect, and `verify_recovery.py` exercises the changed path 41 times across three injected runs. The residual risk is a legacy run directory carrying neither `execution-request.json` nor a state store, where `stored_command` returns `None` and the previous default applies; no such run exists in this repository.
- Rollback procedure: restore `resolve_command(args.command)` in `plan_run`, restore the `--command` default to `implement` in `add_request_args`, restore `args.command` in `cmd_dispatch`, and return `RUNTIME_VERSION` to 0.4.0. Nothing else was written, and no run evidence would be invalidated. Rolling back reopens the defect.

## Release Checklist Result

| Item | Requirement | Result | Evidence |
|---|---|---|---|
| `FR-01` | Registry coverage | pass | 6/6 checks, unresolved=0 |
| `FR-02` | Validator coverage and decisiveness | pass | 4/4 checks, 7 artifact types |
| `FR-03` | Recovery behaviour | pass | 41/41 checks across 3 injected runs |
| `FR-04` | Committed evidence still verifies | pass | `run-c5a8d50d3238` 10/10 PROVEN, plus three further runs |
| `FR-05` | Self-hosting governance resolves | pass | `verify_self_hosting.py` S1 to S8 |
| `FR-06` | Change carried by the routed command with a linked proposal | pass | `run-c9bdf5dbca7a` is a `/bugfix` run; this proposal links its record |
| `FR-07` | `RUNTIME_VERSION` moved only if runtime behaviour changed | pass | Runtime behaviour changed, so 0.4.0 to 0.4.1 |
| `FR-08` | Documentation matches delivered behaviour | pass | The `## Usage` section of `runtime/README.md` now states that an existing run's own record is the authority for its command, and that a disagreeing `--command` is refused |
| `FR-09` | Capability claims backed by evidence, gaps recorded | pass | The reproduction and its refusal are both commands in Verification; the two corrupted runs are recorded rather than quietly deleted |
| `FR-10` | Rollback stated | pass | Risk and Rollback above; three call sites and one constant |
| `FR-11` | Multi-phase state machine still proves out | pass | 15/15 PROVEN |
| `FR-12` | Release note where consumer-visible behaviour changed | accepted | Behaviour visible to an operator did change. The Communication Gate owner accepted this proposal's Verification section as the note for a repository with no external framework consumer yet |

## Open Items

| ID | Item | Owner | Disposition |
|---|---|---|---|
| `O-001` | No phase of `fix-bug` is dispatchable, so a defect repair is carried entirely by the operator against a fully blocked run | omn-tech-lead | Deferred; it is the same capability-registration gap known gap 1 records |
| `O-002` | Two runs were corrupted before the repair and are recorded under `reports/` rather than under `runs/`, because a corrupted store cannot be re-planned into a valid one | omn-orchestrator | Closed by record; both carry their state, their reason, and their disposition |
| `O-003` | The profile's Evidence Rule required a phase artifact from every routed change, which no `/bugfix` run can produce. It was amended during this change to make `E-6` and `E-7` conditional on dispatchability, decided by the runtime rather than the author | omn-orchestrator | Closed; the amendment is recorded in the increment report as bootstrap-owned |

## Sign-off

- Proposed by: operator, under `config/self-hosting-profile.md` v1.0.0
- Accepted by: omn-tech-lead at the Triage Gate and omn-dev-2-reviewer at the Fix Gate, recorded by the operator
- Acceptance basis: the reproduction fails to reproduce, the refusal path is exercised, every prior proof re-executed unchanged, and each of the three open items is either deferred with a named owner or closed by a record
