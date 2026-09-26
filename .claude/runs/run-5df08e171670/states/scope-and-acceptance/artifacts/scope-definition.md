```yaml
scopeDefinition:
  scopeId: SCOPE-2026-0014
  featureName: "Demo mode: autonomous end-to-end demonstration capture (/implement --demo)"
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/demo-mode-feature-request.md
    - type: change-request
      reference: runs/inputs/demo-mode-change-request.md
    - type: business-intent
      reference: runs/inputs/demo-mode-business-intent.md
    - type: architecture-context
      reference: runs/inputs/demo-mode-architecture-context.md
  producedBy: omn-product-owner
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  scopeVerdict: bounded
  acceptanceCriteriaCount: 14
  inputDigest: sha256:e493e2228df8dd0ad8594c85345f19c8
  contextDigest: sha256:c2da0750ed01891e7ded391831c7f994
```

## Metadata

- Feature name: Demo mode: autonomous end-to-end demonstration capture (/implement --demo)
- Requested by: Operator, request of 2026-09-08 extended 2026-09-12 and 2026-09-14, per `input:feature-request`
- Business goal: a presenter can show the framework working to someone who has never seen it, carrying evidence rather than assertions, and without spending a day preparing it
- Target outcome: a governed run produces by itself a distribution-ready demonstration that a first-time, non-technical audience can follow end to end, containing nothing that was not part of that run
- Scope decision date: 2026-09-14

## Business Context

- Problem statement: what the framework produces is a governed trail of artifacts, gate decisions, validation reports, and recovery ledgers, which is the right record for an auditor and the wrong one for a first meeting; the claim carrying the most weight in that meeting, that specialist roles hand work to each other and that none of them passes a human checkpoint alone, is precisely the claim a table cannot demonstrate, so a newcomer must take it on assertion.
- Value hypothesis: if a run can produce its own filmed record with no human editing step, the cost of showing the framework falls from a day of preparation to nothing, and a first meeting is carried by evidence a sceptical viewer can check.
- Affected users: presenters who must show the framework working; non-technical prospective adopters, older, who will listen rather than read and will not pause or scrub; technical prospective adopters who need to confirm the material is a real run and not a staged mock-up; existing team members onboarding onto a lifecycle.
- Success measure: a complete lifecycle, filmed live, cut without human editing, followed end to end by someone meeting the framework for the first time, and verifiably free of anything that was not part of the run, per `input:business-intent`; the residual thresholds inside that measure are recorded as `Q-001` and `Q-002`.

## In Scope

What this change delivers. One row per bounded deliverable, stated as observable
behaviour rather than as an implementation step.

| ID | Scope Item | Rationale | Priority |
|---|---|---|---|
| `S-001` | An operator can ask, at the moment a run is requested, that the run record itself; the run then proceeds exactly as it would have without the request | `input:feature-request` deliverable 1 asks for an optional recording request on the existing command | must-have |
| `S-002` | Nothing that was not part of the run reaches the finished demonstration: material showing anything other than the target window, and the recording's own audio, are withheld and the withholding is recorded | `input:business-intent` names publication safety the hard constraint; `input:feature-request` acceptance 6 forbids publishing such material | must-have |
| `S-003` | A run that was not asked to record costs nothing for the capability's existence: no additional dependency is required of the host, and no work beyond a single existence check per recorded step is performed | `input:feature-request` acceptance 1 and `input:business-intent` constraint that unused capability is free | must-have |
| `S-004` | A fault anywhere in the recording or presentation path is absorbed and recorded there, leaving the observed run's status, artifacts, gate decisions, and recovery outcome identical to an unrecorded run of the same work | `input:feature-request` constraints: additive only, and nothing in the demo layer may raise into the run it observes | must-have |
| `S-005` | Every governed step of a recorded run, being runtime event, dispatch, agent result, validation verdict, gate decision, and host tool call, is recorded once, in order, stamped in UTC to the millisecond, carrying the exchange as observed at the agent boundary | `input:feature-request` deliverable 1 and acceptance 2 | must-have |
| `S-006` | A recorded run that reaches completion stops its own camera and produces the finished demonstration exactly once, with no further operator command and no human editing step | `input:feature-request` deliverable 1 and acceptance 7; `input:business-intent` outcome that a presenter produces it without editing | must-have |
| `S-007` | The demonstration shows the application actually performing the run, cut against that run's own record, and states on screen the factor by which any waiting was condensed, with rejections and retries shown as they happened | `input:feature-request` deliverable 2 and acceptance 4; `input:business-intent` outcome that what is shown is evidence and non-goal 4 | must-have |
| `S-008` | A viewer meeting the framework for the first time can follow the demonstration end to end: it runs for several minutes, explains each step in ordinary language, shows each spoken line on screen, and arrives with a written script and a subtitle file | `input:feature-request` deliverable 3 and acceptance 5; `input:business-intent` target user 2 and the outcome that a presenter who is not the author can deliver it | must-have |
| `S-009` | Where an optional external tool the demonstration could use is absent from the host, the run still produces a reduced demonstration and records which substitution it made, rather than failing | `input:feature-request` acceptance 8 and the no-new-mandatory-dependency constraint | must-have |
| `S-010` | A different demonstration, for a different audience, can be produced from an existing recording without executing or filming the run again | `input:business-intent` outcome that recording is the expensive part and should happen once | should-have |
| `S-011` | The recording request is discoverable from the command's own published contract, and that contract's recorded version states it gained optional behaviour without changing existing behaviour | `input:change-request` records the command specification and registry record as part of the delivered change | should-have |

## Out of Scope

The boundary. A named exclusion prevents scope drift that an unstated one does not.

| ID | Excluded Item | Reason | Revisit Trigger |
|---|---|---|---|
| `X-001` | A monitoring, metrics, or observability capability built on the recorded steps | `input:business-intent` non-goal 1; the recorded steps exist to cut a demonstration, and `input:architecture-context` records a metrics pipeline as deliberately not implemented | a request for run telemetry is raised as a change in its own right |
| `X-002` | A general-purpose editing capability for material other than a recording of a run | `input:business-intent` non-goal 2: it edits one thing, a recording of a run, against that run | a demand arises to assemble material that is not the record of a run |
| `X-003` | Replacing or altering the final report, the completion package, or the recovery ledger | `input:business-intent` non-goal 3; those remain the governed record and the demonstration is not one | a decision is taken to treat a demonstration as an audit artifact |
| `X-004` | Presenting a run more favourably than it happened, by omitting a rejection or a retry or by hiding that time was condensed | `input:business-intent` non-goal 4; the demonstration's worth to a technical viewer rests on it being a real run | a request arrives for material that does not claim to be the record of a real run |
| `X-005` | Making any external capture, encoding, or speech tool a requirement of the framework, or installing or configuring one on the operator's machine | `input:business-intent` forbids a new mandatory dependency because the framework installs into other repositories; `input:architecture-context` records that the recording application's configuration is not writable here | the framework adopts a mandatory media dependency as a policy decision |
| `X-006` | Any change to gate semantics, the Producer Exclusion Rule, the state machine, recovery classification, or an existing artifact contract | `input:feature-request` constrains the change to additive only, and `input:change-request` records that none of these changed | a demonstration requirement emerges that cannot be met without changing governed lifecycle behaviour |
| `X-007` | Recording by default, and recording from any command other than the one the request names | `input:feature-request` deliverable 1 and acceptance 1 make recording an opt-in request on one command | a request is made to demonstrate a second workflow |
| `X-008` | Publishing, hosting, or distributing a finished demonstration, and deciding that a particular one may be released | the request asks for a distribution-ready demonstration, not for a distribution path; release judgement rests outside this scope, per `Q-004` | a publication or distribution path is requested |

## Acceptance Criteria

Every criterion is measurable, names the in-scope item it bounds, and names the method
that verifies it. A criterion that cannot be verified is an open question, not a
criterion.

| ID | Criterion | Scope Ref | Verification Method | Priority |
|---|---|---|---|---|
| `A-001` | A run requested with recording is recording from the moment the run is accepted, and a run requested without it holds no recording of any kind | `S-001` | demonstration of two runs of the same workflow, one requested with recording and one without, comparing the run's own directory in each case | must-have |
| `A-002` | No segment in which the target window was not the window on screen, and no audio captured by the recording itself, appears in a finished demonstration, and every withheld segment is listed in the recording's manifest | `S-002` | inspection of the recording manifest against the finished demonstration for a run in which the target window was deliberately obscured | must-have |
| `A-003` | A run that did not ask to record requires no tool the framework does not already require and performs one existence check per recorded step and nothing further | `S-003` | review of the unrequested path against the stated cost, confirmed by executing a run on a host where none of the optional tools is present | must-have |
| `A-004` | A fault induced anywhere in the recording or presentation path leaves the observed run's status, artifacts, gate decisions, and recovery outcome identical to an unrecorded run of the same work, and the fault is recorded within the recording's own log | `S-004` | demonstration of a recorded run with an induced recording fault, comparing its ledger and artifacts against an unrecorded run of the same workflow | must-have |
| `A-005` | The framework's existing test suite and its verifiers pass on the delivered change, with no previously passing check weakened to accommodate it | `S-004` | execution of the existing suite and the framework verifiers, plus review of the change for weakened assertions | must-have |
| `A-006` | Every runtime event, dispatch, agent result, validation verdict, gate decision, and host tool call of a recorded run appears exactly once in the run's record, in the order it occurred, stamped in UTC to the millisecond, carrying the exchange observed at the agent boundary, including for a step that was replayed | `S-005` | reconciliation of a completed run's recorded steps against its event stream and phase directories, including a replayed step | must-have |
| `A-007` | A recorded run that reaches completion ends its recording only after its last gate is decided, and yields exactly one finished demonstration without a further command | `S-006` | demonstration of one complete lifecycle run, confirming a single finished demonstration and a recording whose end follows the final gate decision | must-have |
| `A-008` | Every segment of a finished demonstration is material of the application performing that run, and each condensed wait carries its condensation factor visible on screen | `S-007` | review of the finished demonstration against the run's recorded steps, segment by segment | must-have |
| `A-009` | A demonstration produced from a run whose record contains a rejection and a retry shows both | `S-007` | review of a demonstration produced from a run whose ledger records a rejection and a retry | must-have |
| `A-010` | A finished demonstration runs for several minutes rather than under a minute, narrates every step in ordinary language, and shows each narrated line on screen as it is spoken | `S-008` | review by a reviewer who has not seen the framework, against the narration script, to the threshold `Q-001` and `Q-002` settle | must-have |
| `A-011` | Every finished demonstration arrives with a written script a presenter can read beforehand and with a subtitle file | `S-008` | inspection of the output of a completed recorded run | must-have |
| `A-012` | With any one of the optional external tools absent, a recorded run still produces a demonstration and records which substitution it made | `S-009` | demonstration on a host with each optional tool removed in turn, inspecting the recorded substitution in each case | must-have |
| `A-013` | A second demonstration, differing in length or in how it is narrated, is produced from an existing recording without executing or filming the run again | `S-010` | demonstration of two differing outputs produced from one recording | should-have |
| `A-014` | The optional recording request appears in the command's published parameter documentation, and the command's recorded version states an additive change with safe defaults | `S-011` | inspection of the command specification and its registry record against the framework's declared versioning rule | should-have |

## Constraints and Dependencies

- Business constraints: publication safety outranks completeness of the demonstration, so a gap is preferable to unverified material; a team that never uses the capability must not pay for its existence; no new mandatory dependency, because the framework installs into other people's repositories. All three from `input:business-intent`.
- Regulatory or policy constraints: the change is additive only, touching no gate semantics, no Producer Exclusion Rule, no state machine, no recovery classification, and no existing artifact contract, per `input:feature-request`; as a framework-internal capability addition it is governed by `config/self-hosting-profile.md`, which requires it to be carried by a command run and to carry a change proposal linking that run's artifacts.
- Delivery constraints: the capability is already implemented and its tests pass, so this boundary is recorded for delivered behaviour, per `D-001`; the operator platform is Windows, and the recording application's control server is disabled there with its configuration not writable by the framework, per `input:architecture-context`.
- External dependencies: four optional external tools, each absent on some host and none permitted to become mandatory, being an image library (Pillow), a media encoder (ffmpeg), a screen-recording application with its control server (OBS Studio), and a system speech engine, per `input:feature-request` and `input:architecture-context`.

## Scope Decisions

Every decision that moved the boundary, with the rationale that justifies it. A decision
without a rationale cannot be reviewed at the Scope Gate.

| ID | Decision | Rationale | Impact | Decided By |
|---|---|---|---|---|
| `D-001` | The boundary is recorded for a capability already built and tested, stated as what the delivered change must be shown to do rather than as work to begin | `input:change-request` describes a completed change set, the defects already found and fixed within it, and a rollback for code that exists, and `config/self-hosting-profile.md` requires a framework-internal capability addition to be carried by a command run linking its artifacts; scoping it as unstarted work would misrepresent the record this run exists to create | downstream phases verify the delivered behaviour against `A-001` to `A-014` rather than author it, and no criterion was softened to fit what was built | omn-product-owner |
| `D-002` | A drawn or synthetic presentation does not satisfy `S-007`, and survives only as the reduced substitute `S-009` allows when nothing could be filmed | the requester rejected a synthetic dashboard because the demonstration must be evidence of a real run, yet removing the drawn path entirely would break the requirement that an absent dependency degrade rather than fail | the two requirements coexist without contradiction, and a reduced output is never presented as material of the run | omn-product-owner |
| `D-003` | Publication safety is priced above completeness: material that cannot be shown to be of the run is withheld even at the cost of a gap in the demonstration | `input:business-intent` names this the hard constraint that outranks completeness of the film, and `input:architecture-context` names publication the dominant risk | `A-002` can be met by a demonstration with missing segments, and such a gap is not a failure of `S-007` | requester, per `input:business-intent` |
| `D-004` | Recording stays opt-in and confined to the single command the request names, rather than being offered across workflows | the request asks for an optional flag on one existing command, and the zero-cost constraint of `S-003` would otherwise have to be defended on every command surface | demonstrating a second workflow is `X-007`, a separate change with its own boundary | requester, per `input:feature-request` |
| `D-005` | The recorded steps are bounded to cutting a demonstration and are not offered as a record anything else may consume | `input:business-intent` non-goal 1 and the standing decision in `input:architecture-context` not to build a metrics pipeline; a record that acquires consumers acquires a contract nobody scoped | `X-001` holds, and no downstream phase may treat the recorded steps as an interface | requester, per `input:business-intent` |

## Open Questions

| ID | Question | Blocking | Owner | Needed By |
|---|---|---|---|---|
| `Q-001` | What minimum running length settles `A-010`, given that the inputs state only several minutes and the rejection of a thirty-five second cut? | no | omn-business-analyst | Verification Gate |
| `Q-002` | Who performs the first-time-viewer review that decides `A-010`, and what outcome of that review counts as passing? | no | omn-qa | Verification Gate |
| `Q-003` | Which capture path the live presentation will use is unsettled, because the recording application's control server is disabled on the operator platform and its configuration is not writable by the framework; is it enabled, or is the alternative path accepted? | no | omn-tech-lead | Closure Gate |
| `Q-004` | Who approves that a particular finished demonstration may be published, given that `X-008` places distribution outside this change while publication is the dominant risk? | no | omn-tech-lead | Closure Gate |
| `Q-005` | Is the short reference cut for onboarding an existing team a requirement of this change, or is it satisfied by `S-010`? | no | omn-business-analyst | Planning Gate |

## Handoff

- Downstream owner: `planner`, for the execution plan over this boundary, then `architect`, `omn-dev-1-implement`, and `omn-qa` in the phases that follow.
- Gate: Scope Gate, closing `scope-and-acceptance` in `implement-feature`; the matrix names `omn-product-owner` and `omn-business-analyst` as owners, and under the Producer Exclusion Rule the decision on this artifact rests with `omn-business-analyst`.
- Evidence for the gate: in-scope items `S-001` to `S-011`, each with the supplied expectation it delivers; exclusions `X-001` to `X-008`, each with a reason and a revisit trigger; acceptance criteria `A-001` to `A-014`, each bounding one scope item and naming the method that decides it; scope decisions `D-001` to `D-005` with their rationale; open questions `Q-001` to `Q-005`, none of them blocking. No gate decision and no readiness claim is recorded in this artifact.
- Deferred to downstream: decomposition, sequencing, and estimation to `planner`; the technical approach, structure, and technology choices to `architect`; the validation strategy that carries out the named verification methods to `omn-qa`; the publication and release judgement to `omn-tech-lead` under `Q-004`. The items carrying the most uncertainty for design and decomposition are `S-002`, `S-008`, and `S-009`.
