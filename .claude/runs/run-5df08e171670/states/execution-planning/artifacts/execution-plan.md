```yaml
plan:
  planId: PLAN-2026-0014
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/demo-mode-feature-request.md
  producedBy: planner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  inputDigest: sha256:563fa9d0a3547f8f865e6410fb0f4547
  contextDigest: sha256:096076ff2cb34a9c66bf3c375efd1124
```

Notation. `S-001` to `S-011` are adopted verbatim from the in-scope register of the upstream
scope definition `SCOPE-2026-0014` (`runs/run-5df08e171670/states/scope-and-acceptance/artifacts/scope-definition.md`,
digest `sha256:c86aec5912c479f65ef54cdaec08ac1f`); `S-012` to `S-014` normalize its Constraints
and Dependencies section. `Q-001` to `Q-005` are that artifact's open questions, carried
forward with the ownership corrections the Scope Gate required. `AC-nnn` denotes an acceptance
criterion of that artifact, `X-nnn` an exclusion, and `D-nnn` a scope decision; `A-nnn`,
`R-nnn`, `T-nnn`, and `Q-nnn` are this plan's own registers.

## Executive Summary

This plan governs a framework-internal capability addition that lets a run record itself and
compile a distribution-ready demonstration with no human editing step, for presenters who must
show the framework working to a first-time, non-technical audience. Per scope decision `D-001`
the capability is already built and its tests pass, so the plan decomposes the delivered change
into reconciliation, verification, and governance closure rather than into fresh construction.
Success is a complete lifecycle run that films itself, cuts itself, and is followed end to end
by a viewer who has never seen the framework, containing nothing that was not part of that run.
The work is 32 tasks across 5 execution waves, owned by eight agents, with 44 dependency edges
and three prerequisites outside the plan's authority. The highest-impact risk is `R-003`: the
capture path for the live presentation is unsettled, and while it stays unsettled only the
reduced substitute is demonstrable, which leaves `AC-008` undemonstrable; the decision that
closes it, `T-004`, is therefore scheduled in wave 1. Plan status is `complete`: all six open
questions are non-blocking, and the uncalibrated running-length threshold behind `AC-010` is
planned against its decidable core under assumption `A-002`.

## Business Objectives

- `BO-01` A first-time, non-technical viewer can follow a governed run end to end and judge it
  as evidence rather than assertion; measured by that viewer completing the demonstration and
  recording the outcome of the review. Traces `S-007`, `S-008`.
- `BO-02` A presenter obtains the demonstration from the run itself, with no editing step and
  no second command; measured by one complete recorded lifecycle yielding exactly one finished
  demonstration. Traces `S-001`, `S-006`, `S-010`.
- `BO-03` Material that cannot be shown to be of the run never leaves the team; measured by the
  absence of withheld segments from any finished demonstration and by each withholding being
  listed. Traces `S-002`.
- `BO-04` A team that never uses the capability pays nothing for its existence; measured by an
  unrequested run requiring no additional host tool and performing one existence check per
  emitted event. Traces `S-003`, `S-009`.
- `BO-05` The framework's governed delivery is unaffected by the capability's presence;
  measured by an observed run's status, artifacts, gate decisions, and recovery outcome being
  identical with and without recording, and by the existing suite and verifiers passing.
  Traces `S-004`, `S-012`, `S-014`.
- `BO-06` The framework's own change record holds for this addition; measured by the command
  contract carrying an additive version record and by a change proposal linking this run's
  artifacts. Traces `S-011`, `S-013`.

## Technical Objectives

- `TO-01` Every governed step of a recorded run is captured once, in order, stamped in UTC to
  the millisecond, carrying the exchange observed at the agent boundary, including for a
  replayed step; verified by reconciliation against the run's event stream and phase
  directories. Serves `BO-01`.
- `TO-02` Every segment of a finished demonstration is material of the application performing
  that run, with each condensed wait carrying its factor on screen and any rejection or retry
  shown; verified by segment-level review against the run's record. Serves `BO-01`.
- `TO-03` The presentation layer is intelligible without prior knowledge: it runs to minutes,
  narrates in ordinary language, shows each spoken line on screen, and ships a script and a
  subtitle file; verified by first-time-viewer review and output inspection. Serves `BO-01`.
- `TO-04` Recording opens at the moment the run is accepted when requested and never otherwise;
  verified by comparing the run directories of a requested and an unrequested run of the same
  workflow. Serves `BO-02`.
- `TO-05` Compilation occurs exactly once, after the final gate decision, with no further
  command; verified on one complete lifecycle run. Serves `BO-02`.
- `TO-06` Material not shown to be of the target window, and the recording's own audio, are
  withheld and the withholding is recorded; verified by inspecting the recording manifest
  against the finished demonstration. Serves `BO-03`.
- `TO-07` No fault in the recording or presentation path reaches the observed run; verified by
  inducing a fault and comparing ledger and artifacts against an unrecorded run. Serves `BO-05`.
- `TO-08` No optional external tool is required, and each absence yields a recorded
  substitution rather than a failure; verified with each optional tool absent in turn. Serves
  `BO-04`.
- `TO-09` A second demonstration, differing in length or narration, is produced from an existing
  recording without executing or filming the run again; verified by two differing outputs from
  one recording. Serves `BO-02`.
- `TO-10` The command's published contract carries the optional recording request and a version
  record stating an additive change with safe defaults; verified by inspection against the
  declared versioning rule. Serves `BO-06`.
- `TO-11` The existing test suite and the framework verifiers pass over the whole change with no
  previously passing check weakened; verified by executing them and reviewing the change for
  weakened assertions. Serves `BO-05`.

## Scope

### In Scope

- `S-001` An operator can ask, when a run is requested, that the run record itself, and the run
  then proceeds exactly as it would have without the request — `T-002`, `T-003`.
- `S-002` Nothing that was not part of the run reaches the finished demonstration; withheld
  material is recorded — `T-006`, `T-007`.
- `S-003` A run that was not asked to record costs nothing for the capability's existence —
  `T-008`, `T-009`.
- `S-004` A fault anywhere in the recording or presentation path is absorbed and recorded there,
  leaving the observed run identical to an unrecorded one — `T-010`, `T-011`, `T-012`.
- `S-005` Every governed step of a recorded run is recorded once, in order, stamped in UTC to
  the millisecond, carrying the agent-boundary exchange — `T-013`, `T-014`.
- `S-006` A recorded run that reaches completion stops its own camera and compiles exactly once,
  with no further command and no editing step — `T-014`, `T-015`.
- `S-007` The demonstration shows the application performing the run, cut against that run's
  record, with condensation stated on screen and rejections and retries shown — `T-004`,
  `T-016`, `T-017`.
- `S-008` A first-time viewer can follow the demonstration end to end: minutes long, ordinary
  language, each spoken line on screen, arriving with a script and a subtitle file — `T-018`,
  `T-019`, `T-020`, `T-021`, `T-022`.
- `S-009` An absent optional external tool yields a reduced demonstration with its substitution
  recorded, rather than a failure — `T-023`, `T-024`.
- `S-010` A second demonstration for a different audience is produced from an existing recording
  without executing or filming the run again — `T-025`, `T-026`, `T-027`.
- `S-011` The recording request is discoverable from the command's published contract, whose
  recorded version states it gained optional behaviour additively — `T-012`, `T-028`, `T-029`.
- `S-012` The change is additive only: no gate semantics, Producer Exclusion Rule, state
  machine, recovery classification, or existing artifact contract is altered — `T-001`, `T-012`.
- `S-013` The change is governed by the self-hosting profile: carried by a command run and
  carrying a change proposal that links that run's artifacts — `T-030`, `T-031`.
- `S-014` The existing test suite and the framework verifiers pass over the delivered change
  with no previously passing check weakened — `T-012`, `T-032`.

### Out of Scope

- `X-001` Telemetry, metrics, or observability built on the recorded steps — excluded by `D-005`;
  the record is bounded to cutting a demonstration and is not an interface.
- `X-002` A general-purpose editing capability for material other than a recording of a run —
  excluded because the capability edits one thing, a run's own recording, against that run.
- `X-003` Replacing or altering the final report, the completion package, or the recovery
  ledger — excluded because those remain the governed record and a demonstration is not one.
- `X-004` Presenting a run more favourably than it happened — excluded because the material's
  worth rests on it being the record of a real run.
- `X-005` Making any external capture, encoding, or speech tool mandatory, or installing or
  configuring one on the operator's machine — excluded by the no-new-mandatory-dependency
  constraint.
- `X-006` Any change to gate semantics, the Producer Exclusion Rule, the state machine, recovery
  classification, or an existing artifact contract — excluded by the additive-only constraint
  recorded as `S-012`.
- `X-007` Recording by default, and recording from any command other than the one the request
  names — excluded by `D-004`.
- `X-008` Publishing, hosting, or distributing a finished demonstration, and deciding that a
  particular one may be released — excluded because release judgement rests outside this
  boundary; the approver is named by `Q-004`.

### Deferred

- A short onboarding reference cut as a deliverable distinct from `S-010` — brought into scope
  if `T-025` decides `Q-005` against it being satisfied by `S-010`.
- Enabling the recording application's control server on the operator platform — brought into
  scope only as an operator-side action if `T-004` decides `Q-003` that way; configuring that
  application remains `X-005`.

## Assumptions

| ID | Assumption | Basis | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The change set the change-request input records is complete and is the artifact this plan governs, per `D-001` | plan-wide | The plan governs the wrong artifact; reconciliation tasks become construction tasks and the wave structure is re-derived | omn-tech-lead |
| A-002 | Until `Q-001` and `Q-002` settle, `AC-010` is planned against its decidable core: narration of every step in ordinary language and each spoken line shown on screen, with running length uncalibrated | `S-008` | A settled threshold above what was delivered reopens the audience layer for re-pacing work | omn-product-owner |
| A-003 | The live presentation runs on the operator platform the architecture-context names, so `Q-003` is a choice between the alternative capture path and an operator-side enablement outside this change | `S-007` | A different host changes the capture options and the reconciliation scope of `T-006` and `T-016` | omn-tech-lead |
| A-004 | A reviewer who has not seen the framework is available to perform the `AC-010` review before the Verification Gate | `S-008` | `AC-010` cannot be decided in this run and moves to a follow-up with its own owner | omn-qa |
| A-005 | The closure-phase work can be carried out even though the runtime's implemented surface does not execute `documentation-and-release-handoff` | plan-wide | `T-029`, `T-030`, and `T-031` have no executing owner and the Closure Gate cannot be evidenced | omn-orchestrator |

## Risks

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | requirement | `Q-001` or `Q-002` is unresolved when the Verification Gate is reached | `AC-010` has no pass condition and plan acceptance cannot close | medium | T-018, T-019, T-022 | Settle both before the Verification Gate through `T-018` and `T-019` | omn-product-owner |
| R-002 | requirement | `Q-005` is unresolved when the Planning Gate is decided | The re-cut scope reopens after planning and `S-010` acceptance shifts | medium | T-025, T-026, T-027 | Decide `Q-005` in wave 1 through `T-025` | omn-product-owner |
| R-003 | technical | `Q-003` is unresolved when the reconciliation wave starts | Only the reduced substitute is demonstrable, and `AC-008` cannot be demonstrated at all | high | T-004, T-006, T-016, T-017 | Decide the capture path in wave 1 through `T-004`, before any dependent reconciliation | omn-tech-lead |
| R-004 | technical | A correction made during reconciliation adjusts an existing check to keep the suite green | `S-014` fails change-wide and the additive-only claim is lost | low | plan-wide | Change-wide regression evidence in `T-032` and weakened-assertion review in `T-012` | omn-dev-2-reviewer |
| R-005 | dependency | No reviewer unfamiliar with the framework is available before the Verification Gate | The `AC-010` review cannot be performed and `BO-01` is unevidenced | medium | T-022 | Nominate the reviewer while `T-019` defines the review | omn-qa |
| R-006 | dependency | The verification host cannot be varied to present each optional external tool absent in turn | `AC-012` cannot be demonstrated and `TO-08` is unevidenced | medium | T-024 | Agree the host variation with the verification host owner before `T-024` starts | omn-qa |
| R-007 | security | A recorded window or a recorded agent-boundary exchange carries restricted content into a finished demonstration | Disclosure outside the team, the dominant risk `D-003` names | medium | T-006, T-007, T-016 | Publication-safety evidence in `T-007` and the named approver from `T-005` | omn-tech-lead |
| R-008 | operational | A finished demonstration is released before `Q-004` names who may approve release | Material leaves the team with no accountable approver | medium | T-005, T-029 | Name the approver in `T-005` and record the path in `T-029` | omn-tech-lead |
| R-009 | operational | The run reaches `documentation-and-release-handoff` and blocks at capability resolution | Closure tasks are unevidenced and the Closure Gate has nothing to decide on | medium | T-029, T-030, T-031 | Settle the closure route in `T-030` before the closure tasks start | omn-orchestrator |
| R-010 | delivery | A reconciliation task finds a divergence needing more than a bounded correction | The run returns to `solution-design-and-risk-assessment` and waves 2 to 5 are re-derived | medium | T-002, T-006, T-008, T-010, T-013, T-015, T-016, T-020, T-023, T-026, T-028 | Fix the delivered structure in `T-001` before reconciliation, and route divergence through `T-012` | omn-tech-lead |

## Task Breakdown

### T-001 Record the technical design of the delivered demonstration capability

- Owner: architect
- Complexity: L (confidence: medium)
- Depends on: none
- Traces to: S-001, S-004, S-012
- Status: ready
- Description: The delivered capability's structure, its integration points with the run
  lifecycle, and the boundary that keeps it additive are recorded as the design of record,
  with the structural risks that boundary rests on.
- Acceptance Criteria:
  - The design package names every integration point between the capability and the run
    lifecycle, and states for each how the observed run is left unchanged.
  - The design package states the additive-only boundary of `S-012` and the evidence by which
    a reviewer can check that no governed lifecycle behaviour was altered.
- Gate: Design Gate

### T-002 Reconcile the opt-in recording request against S-001

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-001
- Status: ready
- Description: The delivered request path is reconciled against `S-001`, so that recording is
  in effect from the moment a requested run is accepted and a run proceeds identically whether
  or not it was requested, with any divergence recorded or corrected within the boundary of
  `T-001`.
- Acceptance Criteria:
  - The reconciliation record shows the point at which recording begins relative to run
    acceptance, with no divergence from `S-001` left open.
  - The reconciliation record confirms the requested and unrequested paths differ in no step of
    the run lifecycle.
- Gate: none

### T-003 Produce the paired-run evidence for the recording request

- Owner: omn-qa
- Complexity: S (confidence: high)
- Depends on: T-002
- Traces to: S-001
- Status: ready
- Description: Evidence exists for `AC-001` from two runs of the same workflow, one requested
  with recording and one without, compared by their run directories.
- Acceptance Criteria:
  - The evidence shows the requested run recording from the moment of acceptance.
  - The evidence shows the unrequested run holding no recording of any kind.
- Gate: Verification Gate

### T-004 Decide the capture path for the live presentation

- Owner: omn-tech-lead
- Complexity: M (confidence: low)
- Depends on: none
- Traces to: S-002, S-007
- Status: assumption-dependent
- Description: `Q-003` is settled: either the recording application's control server is enabled
  on the operator platform, or the alternative capture path is accepted as the one the live
  presentation uses, with the consequence for `S-007` stated either way.
- Acceptance Criteria:
  - The decision names the capture path the live presentation will use and the party who owns
    the host it runs on.
  - The decision states whether real-window material is obtainable on that path, and therefore
    whether `AC-008` is demonstrable or is carried as an accepted gap under `D-003`.
- Gate: Design Gate

### T-005 Name the approver for releasing a finished demonstration

- Owner: omn-tech-lead
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-002
- Status: ready
- Description: `Q-004` is settled by naming the role that approves that a particular finished
  demonstration may leave the team, given that distribution itself is `X-008`.
- Acceptance Criteria:
  - The named approver is a registered role, recorded with the condition under which approval
    is given.
  - The record states that approval is required before any finished demonstration is shown
    outside the producing team.
- Gate: Closure Gate

### T-006 Reconcile the capture boundary against S-002

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-001, T-004
- Traces to: S-002
- Status: assumption-dependent
- Description: The delivered capture path is reconciled against `S-002` on the path `T-004`
  selected, so that material in which the target window was not the window on screen, and the
  recording's own audio, are withheld and each withholding is recorded in the manifest.
- Acceptance Criteria:
  - The reconciliation record shows every withholding condition the capture path detects and
    the manifest entry it writes for each.
  - The reconciliation record confirms the recording's own audio never reaches a finished
    demonstration.
- Gate: none

### T-007 Produce the publication-safety evidence for an obscured-window run

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-006
- Traces to: S-002
- Status: ready
- Description: Evidence exists for `AC-002` from a run in which the target window was
  deliberately obscured, inspecting the recording manifest against the finished demonstration.
- Acceptance Criteria:
  - The evidence shows no segment in which the target window was not the window on screen, and
    no audio captured by the recording itself, present in the finished demonstration.
  - The evidence shows every withheld segment listed in the recording manifest.
- Gate: Verification Gate

### T-008 Reconcile the unrequested run's cost against S-003

- Owner: omn-dev-1-implement
- Complexity: S (confidence: high)
- Depends on: T-001
- Traces to: S-003
- Status: ready
- Description: The cost a run pays when it did not ask to record is reconciled against `S-003`,
  so that no additional host dependency is required and no work beyond a single existence check
  per emitted event is performed.
- Acceptance Criteria:
  - The reconciliation record shows the unrequested path importing nothing from the
    demonstration package.
  - The reconciliation record shows exactly one existence check per emitted event and no
    further work on that path.
- Gate: none

### T-009 Produce the unrequested-run cost evidence

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-008
- Traces to: S-003
- Status: ready
- Description: Evidence exists for `AC-003` from a review of the unrequested path against its
  stated cost, confirmed by executing a run on a host where none of the optional external tools
  is present.
- Acceptance Criteria:
  - The evidence shows the run completing on a host without any optional external tool.
  - The evidence shows the per-event cost matching the single existence check `S-003` states.
- Gate: Verification Gate

### T-010 Reconcile fault absorption against S-004

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-004
- Status: ready
- Description: The delivered isolation of the recording and presentation path is reconciled
  against `S-004`, so that a fault raised anywhere in that path is absorbed and recorded there
  and reaches no part of the observed run.
- Acceptance Criteria:
  - The reconciliation record names each boundary at which a fault is absorbed and the log it
    is recorded in.
  - The reconciliation record shows no path by which a fault in the demonstration layer can
    alter the observed run's status, artifacts, gate decisions, or recovery outcome.
- Gate: none

### T-011 Produce the induced-fault evidence

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-010
- Traces to: S-004
- Status: ready
- Description: Evidence exists for `AC-004` from a recorded run with an induced fault in the
  recording path, compared against an unrecorded run of the same workflow.
- Acceptance Criteria:
  - The evidence shows identical status, artifacts, gate decisions, and recovery outcome across
    the two runs.
  - The evidence shows the induced fault recorded within the recording's own log.
- Gate: Verification Gate

### T-012 Assess the delivered change for governance conformance

- Owner: omn-dev-2-reviewer
- Complexity: L (confidence: medium)
- Depends on: T-002, T-006, T-008, T-010, T-013, T-015, T-016, T-020, T-023, T-026, T-028
- Traces to: S-004, S-011, S-012, S-014
- Status: ready
- Description: The delivered change, as the reconciliation tasks left it, is assessed
  change-wide for conformance to the additive-only boundary, to the declared versioning rule,
  and to the prohibition on weakening an existing check, with findings classified by severity.
- Acceptance Criteria:
  - The findings record confirms no gate semantics, Producer Exclusion Rule, state machine,
    recovery classification, or existing artifact contract was altered.
  - The findings record confirms the command's recorded version states an additive change with
    safe defaults, satisfying `AC-014`.
  - The findings record confirms no previously passing check was weakened anywhere in the
    change, this being a change-wide assessment rather than one scoped to a single task.
- Gate: Review Gate

### T-013 Reconcile the marker record against S-005

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-005
- Status: ready
- Description: The delivered record of a recorded run is reconciled against `S-005`, so that
  every runtime event, dispatch, agent result, validation verdict, gate decision, and host tool
  call appears once, in order, stamped in UTC to the millisecond, carrying the exchange observed
  at the agent boundary, with a replayed step producing no second entry.
- Acceptance Criteria:
  - The reconciliation record maps each of the six governed step kinds to the point at which it
    is recorded.
  - The reconciliation record shows the rule by which a replayed step is recognised and not
    recorded twice.
- Gate: none

### T-014 Produce the completed-run reconciliation evidence

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-013, T-015
- Traces to: S-005, S-006
- Status: ready
- Description: Evidence exists for `AC-006` and `AC-007` from one complete lifecycle run,
  reconciling its recorded steps against its event stream and phase directories and observing
  where its recording ended.
- Acceptance Criteria:
  - The evidence shows each governed step once, in order, stamped in UTC to the millisecond,
    including a replayed step.
  - The evidence shows the recording ending after the final gate decision and exactly one
    finished demonstration produced without a further command.
- Gate: Verification Gate

### T-015 Reconcile the closure of a recorded run against S-006

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-001
- Traces to: S-006
- Status: ready
- Description: The delivered closure path is reconciled against `S-006`, so that a completing
  recorded run stops its own recording only after its last gate is decided and compiles the
  finished demonstration exactly once.
- Acceptance Criteria:
  - The reconciliation record shows the signal that ends recording and its position relative to
    the final gate decision.
  - The reconciliation record shows the guard that prevents a second compilation when more than
    one completion signal is emitted.
- Gate: none

### T-016 Reconcile the cut of the demonstration against S-007

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-001, T-004
- Traces to: S-007
- Status: assumption-dependent
- Description: The delivered editing path is reconciled against `S-007` on the capture path
  `T-004` selected, so that every marker maps onto a frame of the recording, each condensed wait
  states its factor on screen, and a rejection or retry in the run's record appears in the cut.
- Acceptance Criteria:
  - The reconciliation record shows the mapping from a recorded step to the frame it cuts
    against, and the fallback when a marker has no frame.
  - The reconciliation record shows the condensation factor rendered on screen for every
    condensed wait.
- Gate: none

### T-017 Produce the segment-level evidence that the demonstration is material of the run

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-016
- Traces to: S-007
- Status: ready
- Description: Evidence exists for `AC-008` and `AC-009` from a segment-by-segment review of a
  finished demonstration against the recorded steps of the run it was cut from, that run's
  ledger carrying a rejection and a retry.
- Acceptance Criteria:
  - The evidence records, for each segment, the recorded step it corresponds to and that the
    segment is material of the application performing the run.
  - The evidence shows the rejection and the retry present in the demonstration, and every
    condensed wait carrying its factor on screen.
- Gate: Verification Gate

### T-018 Decide the minimum running length that settles AC-010

- Owner: omn-product-owner
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-008
- Status: ready
- Description: `Q-001` is settled by stating the minimum running length a finished demonstration
  must reach for a first-time audience, given that the inputs state only several minutes and
  that a thirty-five second cut was rejected.
- Acceptance Criteria:
  - The decision states a minimum running length as a number, not as a description.
  - The decision states whether the delivered output meets that length or requires re-pacing.
- Gate: Scope Gate

### T-019 Define the first-time-viewer review that decides AC-010

- Owner: omn-qa
- Complexity: S (confidence: medium)
- Depends on: none
- Traces to: S-008
- Status: ready
- Description: `Q-002` is settled by defining who performs the review that decides `AC-010`,
  what the reviewer is asked, and what outcome counts as passing.
- Acceptance Criteria:
  - The definition names the reviewer profile, the questions asked, and the passing outcome.
  - The definition states how the outcome is recorded as evidence for the Verification Gate.
- Gate: Verification Gate

### T-020 Reconcile the audience-facing presentation layer against S-008

- Owner: omn-dev-1-implement
- Complexity: M (confidence: low)
- Depends on: T-001
- Traces to: S-008
- Status: assumption-dependent
- Description: The delivered narration, caption, script, and subtitle outputs are reconciled
  against the decidable core of `S-008` under `A-002`: every step narrated in ordinary language,
  each spoken line shown on screen as it is spoken, and a script and subtitle file produced.
- Acceptance Criteria:
  - The reconciliation record shows every governed step of a recorded run carrying a narrated
    line and a corresponding on-screen caption.
  - The reconciliation record states the running length the delivered output produces, for
    comparison against the threshold `T-018` sets.
- Gate: none

### T-021 Produce the inspection evidence for the presenter outputs

- Owner: omn-qa
- Complexity: XS (confidence: high)
- Depends on: T-020
- Traces to: S-008
- Status: ready
- Description: Evidence exists for `AC-011` from inspecting the output of a completed recorded
  run for the written script and the subtitle file.
- Acceptance Criteria:
  - The evidence shows a written script a presenter can read beforehand present in the output.
  - The evidence shows a subtitle file present in the output and aligned to the narrated lines.
- Gate: Verification Gate

### T-022 Conduct the first-time-viewer review of a finished demonstration

- Owner: omn-qa
- Complexity: M (confidence: low)
- Depends on: T-018, T-019, T-020
- Traces to: S-008
- Status: assumption-dependent
- Description: Evidence exists for `AC-010` from a review by a reviewer who has not seen the
  framework, conducted as `T-019` defines and judged against the length `T-018` sets.
- Acceptance Criteria:
  - The review outcome is recorded against the passing condition `T-019` defined.
  - The record states whether the demonstration met the minimum running length `T-018` set and
    whether every step was followed in ordinary language.
- Gate: Verification Gate

### T-023 Reconcile the substitution path for absent optional tools against S-009

- Owner: omn-dev-1-implement
- Complexity: M (confidence: medium)
- Depends on: T-001
- Traces to: S-009
- Status: ready
- Description: The delivered degradation path is reconciled against `S-009`, so that the absence
  of any one optional external tool yields a reduced demonstration with the substitution
  recorded, and never a failure or a reduced output presented as material of the run.
- Acceptance Criteria:
  - The reconciliation record names, for each of the four optional external tools, the
    substitution made when it is absent and where that substitution is recorded.
  - The reconciliation record confirms a reduced output is never presented as material of the
    run, per `D-002`.
- Gate: none

### T-024 Produce the substitution evidence with each optional tool absent in turn

- Owner: omn-qa
- Complexity: L (confidence: medium)
- Depends on: T-023
- Traces to: S-009
- Status: ready
- Description: Evidence exists for `AC-012` from a host on which each optional external tool is
  removed in turn, inspecting the recorded substitution in each case.
- Acceptance Criteria:
  - The evidence shows a demonstration still produced with each of the four optional tools
    absent in turn.
  - The evidence shows the substitution recorded in each of those four cases.
- Gate: Verification Gate

### T-025 Decide whether the onboarding reference cut is a deliverable of this change

- Owner: omn-product-owner
- Complexity: XS (confidence: high)
- Depends on: none
- Traces to: S-010
- Status: ready
- Description: `Q-005` is settled by deciding whether the short reference cut for onboarding an
  existing team is a requirement of this change or is satisfied by `S-010`.
- Acceptance Criteria:
  - The decision states one of the two outcomes and the scope consequence of it.
  - Where the reference cut is a requirement, the decision states the deliverable it adds and
    the criterion that would decide it.
- Gate: Scope Gate

### T-026 Reconcile re-cutting from an existing recording against S-010

- Owner: omn-dev-1-implement
- Complexity: S (confidence: medium)
- Depends on: T-001, T-025
- Traces to: S-010
- Status: ready
- Description: The delivered path that produces a further demonstration from an existing
  recording is reconciled against `S-010` as `T-025` bounds it, so that a second output differing
  in length or narration is produced without executing or filming the run again.
- Acceptance Criteria:
  - The reconciliation record shows the inputs a second cut consumes and confirms none of them
    requires re-running or re-filming the run.
  - The reconciliation record states which of the differing-output dimensions, length or
    narration, the delivered path supports.
- Gate: none

### T-027 Produce the two-cut evidence from one recording

- Owner: omn-qa
- Complexity: S (confidence: medium)
- Depends on: T-026
- Traces to: S-010
- Status: ready
- Description: Evidence exists for `AC-013` from two demonstrations produced from one existing
  recording, differing in length or in how they are narrated.
- Acceptance Criteria:
  - The evidence shows two outputs from one recording that differ in length or narration.
  - The evidence shows neither output required the run to be executed or filmed again.
- Gate: Verification Gate

### T-028 Reconcile the command's published contract against S-011

- Owner: omn-dev-1-implement
- Complexity: XS (confidence: high)
- Depends on: T-001
- Traces to: S-011
- Status: ready
- Description: The command specification and its registry record are reconciled against `S-011`,
  so that the optional recording request is documented in the command's published parameters and
  its recorded version states an additive change with safe defaults.
- Acceptance Criteria:
  - The reconciliation record shows the optional request documented in the command's parameter
    documentation.
  - The reconciliation record shows the registry version increment and the versioning rule it
    was applied under.
- Gate: none

### T-029 Publish the release communication for the capability

- Owner: omn-documentation
- Complexity: S (confidence: low)
- Depends on: T-005, T-028, T-032
- Traces to: S-011
- Status: assumption-dependent
- Description: The capability's release note and user-facing documentation are published as one
  release communication, stating the optional request, its safe default, the release-approval
  path `T-005` named, and the verification outcome recorded in `T-032`.
- Acceptance Criteria:
  - The release note states the change as additive with safe defaults and cites the verification
    evidence it rests on.
  - The user-facing documentation describes the optional recording request and names the
    approver required before a finished demonstration leaves the team.
- Gate: Closure Gate

### T-030 Settle how the closure-phase work is carried out

- Owner: omn-orchestrator
- Complexity: S (confidence: low)
- Depends on: none
- Traces to: S-013
- Status: assumption-dependent
- Description: `Q-006` is settled by stating how `documentation-and-release-handoff` work is
  carried out and recorded for this run, given that the runtime's implemented surface does not
  execute that phase.
- Acceptance Criteria:
  - The decision states the route by which `T-029` and `T-031` are executed and their outputs
    recorded as run evidence.
  - The decision states what the Closure Gate owners will decide on if the phase itself does not
    dispatch.
- Gate: Closure Gate

### T-031 Produce the framework change proposal linking this run's artifacts

- Owner: omn-documentation
- Complexity: M (confidence: low)
- Depends on: T-030, T-032
- Traces to: S-013
- Status: assumption-dependent
- Description: The change proposal required of a framework-internal capability addition is
  produced from `templates/framework-change-proposal.md` and links the artifacts this run
  carried, as `config/self-hosting-profile.md` requires.
- Acceptance Criteria:
  - The proposal links the scope definition, this plan, the design package, the review findings,
    and the verification evidence of this run by path.
  - The proposal records the change class, the scope rows of the change, and the rollback the
    change-request input states.
- Gate: Closure Gate

### T-032 Produce the change-wide regression evidence

- Owner: omn-qa
- Complexity: M (confidence: medium)
- Depends on: T-012
- Traces to: S-014
- Status: ready
- Description: Evidence exists for `AC-005` over the whole change: the existing test suite and
  the framework verifiers, including the release-checklist verifier `S-013` requires, are
  executed and their results recorded as run evidence.
- Acceptance Criteria:
  - The evidence shows the existing suite and the framework verifiers passing on the change as
    reviewed, with results recorded per check.
  - The evidence records that no previously passing check was weakened, cross-referencing the
    finding `T-012` recorded.
- Gate: Verification Gate

## Dependencies

### 8.1 Dependency Edges

| From | To | Type | Justification |
|---|---|---|---|
| T-001 | T-002 | contract | The reconciliation binds to the integration points the design of record fixes |
| T-001 | T-006 | contract | The capture boundary is reconciled against the structure the design records |
| T-001 | T-008 | contract | The unrequested path's cost is reconciled against the recorded integration points |
| T-001 | T-010 | contract | Fault absorption is reconciled against the isolation boundary the design states |
| T-001 | T-013 | contract | The recorded step set is reconciled against the boundaries the design names |
| T-001 | T-015 | contract | The closure signal is reconciled against the lifecycle integration the design records |
| T-001 | T-016 | contract | The cut is reconciled against the marker-to-frame relation the design fixes |
| T-001 | T-020 | contract | The presentation layer is reconciled against the structure the design records |
| T-001 | T-023 | contract | The substitution path is reconciled against the optional-tool boundary the design states |
| T-001 | T-026 | contract | The second-cut path is reconciled against the recorded inputs the design names |
| T-001 | T-028 | contract | The published contract is reconciled against the additive boundary the design states |
| T-004 | T-006 | decision-gate | Which capture path is used decides what withholding conditions are reconciled |
| T-004 | T-016 | decision-gate | Which capture path is used decides whether the cut is over real-window material |
| T-025 | T-026 | decision-gate | Whether the reference cut is a deliverable decides the second-cut scope |
| T-002 | T-003 | verification | The evidence validates the request path the reconciliation settled |
| T-002 | T-012 | verification | The review assesses the reconciled request path |
| T-006 | T-007 | verification | The evidence validates the withholding behaviour the reconciliation settled |
| T-006 | T-012 | verification | The review assesses the reconciled capture boundary |
| T-008 | T-009 | verification | The evidence validates the unrequested-path cost the reconciliation settled |
| T-008 | T-012 | verification | The review assesses the reconciled unrequested path |
| T-010 | T-011 | verification | The evidence validates the fault absorption the reconciliation settled |
| T-010 | T-012 | verification | The review assesses the reconciled isolation boundary |
| T-013 | T-012 | verification | The review assesses the reconciled record of governed steps |
| T-013 | T-014 | verification | The evidence reconciles the recorded steps the reconciliation settled |
| T-015 | T-012 | verification | The review assesses the reconciled closure signal |
| T-015 | T-014 | verification | The same completed run evidences the end of recording and the single compilation |
| T-016 | T-012 | verification | The review assesses the reconciled cut |
| T-016 | T-017 | verification | The evidence validates the cut the reconciliation settled |
| T-018 | T-022 | decision-gate | The minimum running length decides what the review judges against |
| T-019 | T-022 | decision-gate | The review definition decides how the review is conducted and what passes |
| T-020 | T-012 | verification | The review assesses the reconciled presentation layer |
| T-020 | T-021 | verification | The evidence inspects the outputs the reconciliation settled |
| T-020 | T-022 | verification | The review is conducted on the presentation layer the reconciliation settled |
| T-023 | T-012 | verification | The review assesses the reconciled substitution path |
| T-023 | T-024 | verification | The evidence validates the substitutions the reconciliation settled |
| T-026 | T-012 | verification | The review assesses the reconciled second-cut path |
| T-026 | T-027 | verification | The evidence validates the second-cut path the reconciliation settled |
| T-028 | T-012 | verification | The review assesses the command record against the versioning rule |
| T-028 | T-029 | produces-consumes | The release communication states the published contract the reconciliation settled |
| T-005 | T-029 | decision-gate | The release communication records the approval path the decision named |
| T-012 | T-032 | policy-gate | The Review Gate closes corrective iteration before regression evidence is final |
| T-032 | T-029 | produces-consumes | The release communication cites the verification evidence |
| T-030 | T-031 | decision-gate | The closure route decides how the proposal is produced and recorded |
| T-032 | T-031 | produces-consumes | The proposal links the verification evidence as a run artifact |

### 8.2 External Dependencies

These are prerequisites outside the plan's authority. They are conditions on the named tasks and
are not edges in 8.1, so the order in 8.3 recomputes from 8.1 alone.

| Responsible party | What is needed | Blocks |
|---|---|---|
| Presentation host operator | Either the recording application's control server enabled on the operator platform, or written acceptance of the alternative capture path | T-004 |
| First-time-viewer reviewer nominated by omn-product-owner | A reviewer who has not seen the framework, available before the Verification Gate | T-022 |
| Verification host owner | A host on which each of the four optional external tools can be made absent in turn | T-024 |

### 8.3 Implementation Order

- Wave 1: T-001, T-004, T-005, T-018, T-019, T-025, T-030
- Wave 2: T-002, T-006, T-008, T-010, T-013, T-015, T-016, T-020, T-023, T-026, T-028
- Wave 3: T-003, T-007, T-009, T-011, T-012, T-014, T-017, T-021, T-022, T-024, T-027
- Wave 4: T-032
- Wave 5: T-029, T-031

## Suggested Workflow

Selected workflow: `implement-feature`

Selected because the change adds new functionality to the framework and is already routed to
that workflow by the self-hosting profile, whose phases carry the design, review, verification,
and closure evidence `S-012`, `S-013`, and `S-014` require. The plan recommends this routing and
does not start it.

| Phase | Tasks |
|---|---|
| scope-and-acceptance | T-018, T-025 |
| execution-planning | none; this plan is that phase's output |
| solution-design-and-risk-assessment | T-001, T-004 |
| implementation | T-002, T-006, T-008, T-010, T-013, T-015, T-016, T-020, T-023, T-026, T-028 |
| quality-review | T-003, T-007, T-009, T-011, T-012, T-014, T-017, T-019, T-021, T-022, T-024, T-027, T-032 |
| documentation-and-release-handoff | T-005, T-029, T-030, T-031 |

| Gate | Required owners |
|---|---|
| Scope Gate | omn-product-owner, omn-business-analyst |
| Planning Gate | omn-tech-lead, omn-orchestrator |
| Design Gate | omn-architect, omn-tech-lead |
| Review Gate | omn-dev-2-reviewer, omn-qa |
| Verification Gate | omn-qa |
| Closure Gate | omn-orchestrator, omn-documentation |

## Required Capabilities

### 10.1 Agent Capabilities

| Capability | Tasks | Owning agent | Proficiency |
|---|---|---|---|
| acceptance-authority | T-018, T-025 | omn-product-owner | Primary |
| technical-approach-definition | T-001 | architect | Primary |
| structural-risk-analysis | T-001 | architect | Primary |
| option-evaluation | T-004 | omn-tech-lead | Primary |
| release-readiness | T-005 | omn-tech-lead | Primary |
| implementation-delivery | T-002, T-006, T-008, T-010, T-013, T-015, T-016, T-020, T-023, T-026, T-028 | omn-dev-1-implement | Primary |
| validation-design | T-019 | omn-qa | Primary |
| quality-verification | T-003, T-007, T-009, T-011, T-014, T-017, T-021, T-022, T-024, T-027, T-032 | omn-qa | Primary |
| code-review | T-012 | omn-dev-2-reviewer | Primary |
| governance-enforcement | T-012 | omn-dev-2-reviewer | Primary |
| run-coordination | T-030 | omn-orchestrator | Primary |
| documentation | T-031 | omn-documentation | Primary |
| release-communication | T-029 | omn-documentation | Primary |

### 10.2 Required Skills

| Skill | File | Tasks | Level |
|---|---|---|---|
| S01 | skills/architecture/clean-architecture-checklist.md | T-001, T-010 | Advisory |
| S02 | skills/business/domain-modeling.md | T-018, T-025, T-029 | Primary |
| S07 | skills/testing/testing-strategy.md | T-003, T-007, T-009, T-011, T-014, T-017, T-019, T-021, T-022, T-024, T-027, T-032 | Primary |
| S08 | skills/performance/performance-engineering.md | T-008, T-009 | Advisory |
| S09 | skills/security/secure-engineering.md | T-006, T-007, T-016 | Advisory |
| S11 | skills/logging/observability-logging.md | T-013, T-014 | Secondary |
| S12 | skills/error-handling/error-handling-strategy.md | T-010, T-023 | Secondary |

## Acceptance Criteria

1. A run requested with recording records from the moment the run is accepted, and a run
   requested without it holds no recording of any kind. Verifies `BO-02`. Evidence: the paired-run
   record from `T-003`.
2. A viewer who has not seen the framework follows a finished demonstration end to end, to the
   length `T-018` sets and by the review `T-019` defines. Verifies `BO-01`. Evidence: the recorded
   review outcome from `T-022`.
3. Every segment of that demonstration is material of the application performing the run, with
   each condensed wait carrying its factor on screen and a rejection and a retry shown. Verifies
   `BO-01`. Evidence: the segment-level record from `T-017`.
4. One complete recorded lifecycle run ends its recording after the final gate decision and
   yields exactly one finished demonstration, arriving with a script and a subtitle file, with no
   further command. Verifies `BO-02`. Evidence: `T-014` and `T-021`.
5. For a run in which the target window was deliberately obscured, no withheld segment appears in
   the finished demonstration and every withholding is listed in the manifest. Verifies `BO-03`.
   Evidence: the manifest comparison from `T-007`.
6. A run that did not request recording requires no tool the framework does not already require
   and performs one existence check per emitted event. Verifies `BO-04`. Evidence: `T-009`.
7. With each optional external tool absent in turn, a recorded run still produces a demonstration
   and records the substitution it made. Verifies `BO-04`. Evidence: `T-024`.
8. A second demonstration, differing in length or narration, is produced from an existing
   recording without executing or filming the run again. Verifies `BO-02`. Evidence: `T-027`.
9. A fault induced in the recording or presentation path leaves the observed run's status,
   artifacts, gate decisions, and recovery outcome identical to an unrecorded run. Verifies
   `BO-05`. Evidence: `T-011`.
10. The existing test suite and the framework verifiers pass over the whole change with no
    previously passing check weakened. Verifies `BO-05`. Evidence: `T-032`, with the
    weakened-assertion finding from `T-012`.
11. The command's published contract documents the optional recording request and its recorded
    version states an additive change with safe defaults. Verifies `BO-06`. Evidence: the
    conformance finding from `T-012`.
12. The change carries a change proposal linking this run's artifacts and satisfies the framework
    release checklist. Verifies `BO-06`. Evidence: `T-031` and the checklist result in `T-032`.

## Definition of Done

- [ ] Every plan acceptance criterion 1 to 12 is verified and its named evidence is recorded as
      run evidence.
- [ ] The Scope, Planning, Design, Review, Verification, and Closure Gates are decided by the
      owners named in Suggested Workflow, with each decision recorded.
- [ ] Every task's acceptance criteria are satisfied, or waived with the waiving owner recorded.
- [ ] Assumptions `A-001` to `A-005` are confirmed by their named roles or converted to recorded
      decisions.
- [ ] Risks `R-001` to `R-010` are closed or accepted with their named owners recorded.
- [ ] Open questions `Q-001` to `Q-006` are closed or explicitly accepted by their named owners.
- [ ] The release communication is published, and the change proposal linking this run's
      artifacts exists.
- [ ] The framework release checklist result for this change is recorded.
- [ ] Durable outcomes are recorded to memory per `memory/memory-governance.md`.

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | What minimum running length settles `AC-010`, given that the inputs state only several minutes and that a thirty-five second cut was rejected? | no | omn-product-owner (reassigned from omn-business-analyst at the Scope Gate) | T-018, T-020, T-022 |
| Q-002 | Who performs the first-time-viewer review that decides `AC-010`, and what outcome of that review counts as passing? | no | omn-qa | T-019, T-022 |
| Q-003 | Which capture path will the live presentation use, given that the recording application's control server is disabled on the operator platform and its configuration is not writable here? | no | omn-tech-lead | T-004, T-006, T-016, T-017 |
| Q-004 | Who approves that a particular finished demonstration may be released, given that `X-008` places distribution outside this change while publication is the dominant risk? | no | omn-tech-lead | T-005, T-029 |
| Q-005 | Is the short reference cut for onboarding an existing team a requirement of this change, or is it satisfied by `S-010`? | no | omn-product-owner (reassigned from omn-business-analyst at the Scope Gate) | T-025, T-026, T-027 |
| Q-006 | How is `documentation-and-release-handoff` work carried out and recorded for this run, given that the runtime's implemented surface does not execute that phase? | no | omn-orchestrator | T-029, T-030, T-031 |
