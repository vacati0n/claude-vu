# Technical Design — Demonstration capture and presentation capability, runtime 0.8.0

```yaml
design:
  designId: design-run-5df08e171670-demo-mode
  changeReference: runs/inputs/demo-mode-change-request.md
  sourceInputs:
    - type: change-request
      reference: runs/inputs/demo-mode-change-request.md
    - type: business-intent
      reference: runs/inputs/demo-mode-business-intent.md
    - type: architecture-context
      reference: runs/inputs/demo-mode-architecture-context.md
    - type: execution-plan
      reference: runs/run-5df08e171670/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003, D-004, D-005, D-006, D-007]
  consumesPlan: runs/run-5df08e171670/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:9e9073415ebad3696033cda9e8b1d17e
  contextDigest: sha256:f1246957f39ca8eb9e7e10121d72bc16
```

## Metadata

- Feature or Change ID: run-5df08e171670 / demonstration capture capability, runtime 0.8.0
- Author: architect (agent), version 1.0.0
- Reviewers: omn-tech-lead (accepting owner at the Design Gate), omn-qa (verification focus areas)
- Last Updated: 2026-09-14

## Objective

- Desired outcome: a governed run can observe itself and, on reaching its final gate, produce
  a presentation cut from footage of the application that performed it, with the observation
  path costing an unrequested run one existence check per emitted event and never able to
  affect the run it watches.

- Architectural objectives:
  - A single observation point exists at which the whole progress of a run is visible, and no
    second instrumentation surface is created. Traces S-005.
  - The observation path is switched per run and is absent from the process image of a run
    that did not request it. Traces S-001, S-003.
  - Every external integration the capability needs sits behind an adapter boundary outside
    the execution path, and each one's absence is a recorded substitution rather than a
    failure. Traces S-004, S-009.
  - No control or error path leads from the observation layer into the run's state machine,
    recovery classification, or gate decisions. Traces S-004, S-012.
  - Material that cannot be shown to be of the target window is structurally excluded before
    anything is published, and the exclusion is itself recorded. Traces S-002.
  - Compilation is a single, idempotent consequence of the run having nothing left to decide.
    Traces S-006.
  - The recording and the edit are separable, so a second presentation is derivable from an
    existing recording. Traces S-010.
  - The capability's operator-facing surface is carried by the existing command's published
    contract under an additive version. Traces S-011.
  - Delivered structure is described and judged as it is, against the acceptance criteria as
    written. Traces S-013, C-013.

- In scope: the observation package `runtime/demo/`, its integration sites in
  `runtime/framework_runtime.py`, the command specification and registry record for the
  `implement` command, the installable payload copy, the wrapper forwarding, the runtime and
  user documentation, and the delivered test set. This design is a design of record: the
  structure it describes exists and its tests pass (A-002), and the design's purpose is to
  justify that structure and register the decisions it embodies.

- Out of scope, structurally: the workflow Phase Model, the gate matrix and its Producer
  Exclusion Rule, the state transition table, recovery classification, existing artifact
  templates and their validators, every other command registry record, and every agent
  contract. None of these is touched, and each is recorded at `no-change-verified` in 5.1 so
  that a reader can tell it was cleared rather than overlooked. Also structurally out of
  scope: any durable interface over the marker record (C-007), and any framework-performed
  installation or configuration of an external tool on the operator's host (C-002).

## Requirements Summary

The statement register `S-001` to `S-014` is adopted unchanged from the Scope Gate-approved
scope definition (`runs/run-5df08e171670/states/scope-and-acceptance/artifacts/scope-definition.md`),
which is the normalization of the supplied feature request, change request, business intent,
and architecture context. Adopting it rather than re-deriving a second register keeps one
statement identity across the run. Acceptance criteria are cited in the execution plan's
`AC-001` to `AC-014` form, not restated; the scope definition numbers the same criteria in an
`A-` series, which this package does not use because `A-nnn` is its assumption scheme.

- Functional requirements:
  - Opt-in recording requested at the moment a run is requested, on one command only —
    S-001, S-003; bounded by C-011; verified by AC-001, AC-003.
  - Every governed step recorded once, in order, stamped in UTC to the millisecond, carrying
    the exchange observed at the agent boundary, including for a replayed step — S-005;
    verified by AC-006.
  - Self-terminating recording and exactly one compilation after the final gate decision —
    S-006; bounded by C-011; verified by AC-007.
  - Every segment of the finished presentation is material of the application performing that
    run, with each condensed wait carrying its factor on screen — S-007; bounded by C-015;
    verified by AC-008, AC-009.
  - A second presentation derivable from an existing recording without re-running or
    re-filming — S-010; verified by AC-013.
  - The recording request discoverable from the command's published contract, whose recorded
    version states an additive change with safe defaults — S-011; bounded by C-012; verified
    by AC-014.

- Non-functional requirements:
  - Publication safety: nothing that was not part of the run reaches a finished presentation,
    and every withheld span is listed — S-002; bounded by C-005; verified by AC-002.
  - Zero cost when unused: no tool the framework does not already require, and one existence
    check per emitted event and nothing further — S-003; bounded by C-003, C-009; verified by
    AC-003.
  - Fault containment: a fault anywhere in the observation or presentation path leaves the
    run's status, artifacts, gate decisions, and recovery outcome identical to an unrecorded
    run, and is recorded in the observation layer's own log — S-004; bounded by C-004, C-008;
    verified by AC-004.
  - No mandatory dependency: each optional external tool's absence yields a recorded
    substitution — S-009; bounded by C-002; verified by AC-012.
  - Intelligibility to a first-time viewer: minutes long, ordinary language, on-screen
    captions, a presenter script, and a subtitle file — S-008; bounded by C-014; verified by
    AC-010, AC-011.
  - Additive only: no gate semantics, Producer Exclusion Rule, state machine, recovery
    classification, or existing artifact contract changes — S-012; bounded by C-001; verified
    by AC-005.
  - Governed by the self-hosting profile, carried by a command run — S-013; bounded by C-013;
    this run is that carriage.
  - The existing suite and the framework verifiers pass with no previously passing check
    weakened — S-014; verified by AC-005.

- Acceptance criteria: the acceptance intent of statements S-001 to S-014 is cited as
  `AC-001` to `AC-014` from the execution plan
  (digest `sha256:16e36bbc4df40a72ba578548e1e72388`). No criterion is restated, narrowed, or
  reworded here; C-013 forbids it, and the capture-path finding in 4.2 and D-003 is recorded
  as an accepted gap against `AC-008` as written rather than as a change to it.

## Current-State Assumptions and Constraints

**Divergence from the recorded change set, raised under the Planning Gate's condition on
A-001.** Assumption A-001 — that the change-request input records the complete delivered
change set — was carried forward for confirmation by omn-tech-lead, and task T-001 required
this design to test it against the delivered structure. It does not hold in full. Four
divergences were found and are recorded as facts F-019 to F-022, carried as impacted modules
M-015, M-016, M-020 and M-022, raised as risk R-003, and routed as open question Q-002. They
are not absorbed into the narrative: each is a statement the change record makes that the
delivered structure contradicts, and none of them is corrected by this agent. In this
agent's judgement each is a bounded correction to the record rather than undelivered
construction, because none changes delivered behaviour; that judgement is A-005 and its
confirmation belongs to omn-tech-lead under R-010 of the execution plan.

**Repository rescan.** The task context named no relevant modules or files
(`repository_context.relevant_modules` and `relevant_files` are both empty), so the design
read the delivered sites directly: the package directory `runtime/demo/`, the integration
sites and request parser in `runtime/framework_runtime.py`, `commands/implement.md`, the
`implement` record in `registry/commands.yaml`, the wrapper modules under `omn_agent/`, the
runtime and user documentation, and the delivered test set. The reason for the rescan is that
T-001 cannot be performed against a context that names no files, and A-001 cannot be tested
without reading the structure it claims to describe.

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | Every state change in a run passes through the ledger's single emit function, which appends to one ordered stream of fifteen canonical event types | input:architecture-context, Current-state structure |
| F-002 | The invocation envelope and the dispatch prompt are written to the phase directory before the adapter is leased, and the runtime core never talks to a model, so the adapter boundary is the only place the exchange with an agent is visible | input:architecture-context, Current-state structure |
| F-003 | The Validation Engine writes one validation report per phase | input:architecture-context, Current-state structure |
| F-004 | The task-context and execution-metrics modules added in 0.7.0 derive per-run documents from persisted evidence only | input:architecture-context, Current-state structure |
| F-005 | The runtime already records everything a presentation needs, ordered and stamped, so nothing new had to be instrumented; what was missing was a consumer and a clock | input:architecture-context, The architectural fact this change rests on |
| F-006 | The install-prefix variable exists because the framework occupies one directory in its own repository and another once installed elsewhere, and anything path-facing derives from it | input:architecture-context, Design constraints 5 |
| F-007 | The operator platform is Windows; the recording application 32.2.2 is installed with its control server bundled but disabled, and its configuration is not writable by the agent | input:architecture-context, Known environmental facts |
| F-008 | No system encoder is installed on the operator host; an image library is present; platform speech voices are available | input:architecture-context, Known environmental facts |
| F-009 | The target window belongs to a GPU-composited desktop application | input:architecture-context, Known environmental facts |
| F-010 | The delivered package `runtime/demo/` holds fourteen Python modules with the responsibilities the change record tabulates | input:change-request, What changes; read of `runtime/demo/` |
| F-011 | The package's public surface exposes enable, event tap, status, build, backfill, record start and stop, capture status, and host-hook ingestion | read of `runtime/demo/__init__.py` |
| F-012 | Every site in `runtime/framework_runtime.py` that reaches the package is guarded by one existence check on the run's switch file, and the package is imported inside the guard | read of `runtime/framework_runtime.py` |
| F-013 | The event tap discards an event whose canonical identifier already produced a marker, so a replayed event does not produce a second marker | read of `runtime/demo/recorder.py` |
| F-014 | Compilation is claimed by an exclusive file creation performed before the build, so a second finishing event does not compile again and a crashed build is not retried automatically | read of `runtime/demo/__init__.py` |
| F-015 | The camera stops and the film is compiled only when every phase is committed and every gate is decided, read from the run's own state store rather than the ledger's summary, because the summary counts phases and a gate is not a phase | read of `runtime/demo/__init__.py` |
| F-016 | Two capture backends exist, the control-server backend preferred and the encoder backend second; the encoder's window-level input is deliberately unused because a GPU-composited window returns black frames, so the window's rectangle is captured instead | read of `runtime/demo/capture.py` |
| F-017 | The encoder backend raises the target and refuses to start unless the target is the foreground window, and a detached helper samples foreground state while filming, merges spans closer than one second into one interruption, and records the occluded spans so that footage is excluded | read of `runtime/demo/capture.py`, `runtime/demo/capture_helper.py` |
| F-018 | A long span keeps its head and tail at real speed and condenses only its middle, with the condensation factor stated on screen | read of `runtime/demo/editor.py` |
| F-019 | The package directory also holds a delivered configuration fragment wiring host tool calls to the runtime's observation subcommand through a pointer file at the runs root; the change record's module table itemises only the fourteen Python modules | read of `runtime/demo/hooks.settings.json`; input:change-request, What changes |
| F-020 | `runtime/framework_runtime.py` reaches the package at four guarded sites — the ledger tap, arming during run planning, the observation subcommand, and the run status display — while the change record and the package's own surface documentation both state three integration points | read of `runtime/framework_runtime.py`, `runtime/demo/__init__.py`; input:change-request, What changes |
| F-021 | The request parser registers ten recording arguments and the command specification documents nine, while the change record states a group of seven optional flags; the command registry record is at 1.1.0 | read of `runtime/framework_runtime.py`, `commands/implement.md`, `registry/commands.yaml`; input:change-request, What changes |
| F-022 | The installable payload under `omn_agent/_bundled_payload/` carries the whole delivered change including the package, the runtime, the command specification and the registry record, while the change record names only the three wrapper modules under `omn_agent/` | read of `omn_agent/`; input:change-request, What changes |
| F-023 | The delivered test set is four test modules and one control-server fixture, as the change record states | read of `tests/`; input:change-request, What changes |
| F-024 | The gate matrix names omn-architect and omn-tech-lead as the Design Gate owners for this workflow, its Producer Exclusion Rule reads through role aliases, and it records that acceptance of this agent's output rests with omn-tech-lead | workflows/workflow-gate-matrix.md |
| F-025 | The runtime and the user documentation both carry the capability, and the wrapper modules forward the request to the runtime | read of `runtime/README.md`, `docs/USER-GUIDE.md`, `omn_agent/cli.py`, `omn_agent/runner.py`, `omn_agent/update.py` |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | Outside the four sites this design re-read — the package directory, the integration sites and request parser, the command contract and registry record, and the wrapper and payload copies — the change record is a complete account of the delivered change | The design of record must govern the whole delivered artifact, and only part of it was re-read | Further divergences exist; the reconciliation sequencing in P-001 does not bound the correction, and R-010 of the execution plan returns the run to this phase | omn-tech-lead |
| A-002 | The capability's delivered tests pass as the execution plan records; this design executes nothing | The design justifies delivered structure rather than proposing construction, which is only sound if the structure behaves as recorded | The design of record describes behaviour that does not hold, and every acceptance reconciliation becomes construction | omn-qa |
| A-003 | The live presentation runs on the operator platform F-007 describes | The capture-path settlement in D-003 rests on that host's configuration | The available backends differ, D-003 is re-decided, and the P-002 evidence is re-produced on the actual host | omn-tech-lead |
| A-004 | Enabling the recording application's control server through its own interface is an operator act, not a framework act, so it does not make an external tool a framework requirement | D-003 keeps the preferred backend reachable without breaching C-002 | The preferred backend is unreachable within the boundary, and the encoder backend becomes the only path rather than the fallback | omn-tech-lead |
| A-005 | The four divergences F-019 to F-022 are corrections to the record rather than undelivered construction, because none of them changes delivered behaviour | P-001 sequences a bounded reconciliation ahead of every acceptance activity | The reconciliation is construction, the wave structure of the execution plan is re-derived, and R-010 of that plan fires | omn-tech-lead |
| A-006 | The condensation factor stated on screen and the withheld-span list in the capture manifest are, together, what makes a presentation honest about how it was made | C-005 and C-015 are satisfied by exclusion plus disclosure rather than by completeness | Disclosure is judged insufficient, and AC-002 or AC-008 requires a structural change to the editor rather than an inspection | omn-qa |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | Additive only: no gate semantics, Producer Exclusion Rule, state machine, recovery classification, or existing artifact contract changes | Hard | S-012 |
| C-002 | operability | No new mandatory dependency, and the framework installs or configures no external tool on the operator's host | Hard | S-009; input:business-intent, Constraints |
| C-003 | quality-attribute | A run that did not request recording performs one existence check per emitted event and nothing further, and never imports the package | Hard | S-003 |
| C-004 | operability | Nothing in the observation layer may raise into the run it observes | Hard | S-004; input:feature-request, Constraints |
| C-005 | security | Only the target window may ever be recorded, the recording's own audio is never published, and publication safety outranks completeness | Hard | S-002; input:business-intent, Constraints |
| C-006 | structural | External integration sits behind an adapter boundary, outside the execution path, as model adapters do | Hard | input:architecture-context, Design constraints 1 |
| C-007 | structural | The marker record exists to cut a presentation and must not become a metrics or observability pipeline, nor be offered as an interface | Hard | input:architecture-context, Design constraints 2; the scope definition's decision bounding the recorded steps |
| C-008 | operability | A fault in the observation path is not a run failure and must not enter failure classification; it is caught and logged | Hard | input:architecture-context, Design constraints 3 |
| C-009 | quality-attribute | A new capability must not add to what a dispatch reads | Hard | input:architecture-context, Design constraints 4 |
| C-010 | structural | Anything path-facing derives from the install-prefix variable | Hard | F-006 |
| C-011 | functional | Recording is opt-in on the one command the request names, and compilation occurs exactly once, after the final gate decision | Hard | S-001, S-006 |
| C-012 | migration | The command's recorded version states an additive change with safe defaults under the declared versioning rule | Hard | S-011 |
| C-013 | functional | Delivered behaviour is judged against the acceptance criteria as written; no criterion is softened, narrowed, or reworded to match what was built | Hard | the scope definition's decision that the boundary is recorded for a capability already built |
| C-014 | quality-attribute | The presentation runs to minutes, narrates every step in ordinary language, and shows each spoken line on screen, with the running-length threshold open until Q-003 settles it | Negotiable | S-008 |
| C-015 | functional | Every segment of a finished presentation is material of the application performing that run | Hard | S-007 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `runtime/demo/__init__.py` | extension | F-011 | the package's public surface; the event tap; the compilation claim | confirmed |
| M-002 | `runtime/demo/context.py` | extension | F-011 | the per-run switch file and its persisted options | confirmed |
| M-003 | `runtime/demo/recorder.py` | extension | F-013 | the marker stream; the reads of the event stream, envelopes, and validation reports | confirmed |
| M-004 | `runtime/demo/timeline.py` | extension | F-018 | markers to scenes; the narration registers | confirmed |
| M-005 | `runtime/demo/narration.py` | extension | F-008 | the speech-engine chain and the assembled audio | confirmed |
| M-006 | `runtime/demo/captions.py` | extension | F-011 | timed cues, the subtitle file, the presenter script | confirmed |
| M-007 | `runtime/demo/obs_ws.py` | extension | F-007 | the local control-server protocol client | confirmed |
| M-008 | `runtime/demo/capture.py` | extension | F-016 | window targeting; both backends; the capture manifest | confirmed |
| M-009 | `runtime/demo/capture_helper.py` | extension | F-017 | the detached process boundary; occlusion sampling | confirmed |
| M-010 | `runtime/demo/overlays.py` | extension | F-011 | the drawn presentation frame around the footage | confirmed |
| M-011 | `runtime/demo/editor.py` | extension | F-018 | the edit decision list; narration fitting; the encoder invocation | confirmed |
| M-012 | `runtime/demo/renderer.py` | extension | F-010 | the drawn dashboard state and its frames | confirmed |
| M-013 | `runtime/demo/video_builder.py` | extension | F-010 | frames and narration to an output; the build manifest | confirmed |
| M-014 | `runtime/demo/deck.py` | extension | F-010 | the self-contained presentation deck | confirmed |
| M-015 | `runtime/demo/hooks.settings.json` | operational-impact | F-019 | host tool-hook wiring; the pointer file at the runs root | confirmed |
| M-016 | `runtime/framework_runtime.py` | contract-change | F-012, F-020, F-021 | the ledger tap; run-planning arming; the observation subcommand; the status display; the request parameter surface; the runtime version | confirmed |
| M-017 | `commands/implement.md` | contract-change | F-021 | the command's published parameter documentation | confirmed |
| M-018 | the `implement` record in `registry/commands.yaml` | contract-change | F-021 | the command's recorded version and description | confirmed |
| M-019 | `omn_agent/cli.py`, `omn_agent/runner.py`, `omn_agent/update.py` | behavior-change | F-025 | forwarding of the recording request to the runtime | confirmed |
| M-020 | `runtime/README.md`, `docs/USER-GUIDE.md` and its rendered output, and the repository readme | operational-impact | F-025, F-020 | the documented runtime surface and the operator instructions | confirmed |
| M-021 | `tests/test_demo_mode.py`, `test_demo_capture.py`, `test_demo_pacing.py`, `test_demo_captions.py`, `tests/fixtures/fake_obs.py` | extension | F-023 | the delivered test set for the capability | confirmed |
| M-022 | `omn_agent/_bundled_payload/` | extension | F-022 | the installable copy of the framework carrying the change | confirmed |
| M-023 | `workflows/implement-feature.md` and its Phase Model | no-change-verified | F-005 | none | confirmed |
| M-024 | `workflows/workflow-gate-matrix.md` and its Producer Exclusion Rule | no-change-verified | F-024 | none | confirmed |
| M-025 | the state transition table and recovery classification in `config/execution-engine.md` | no-change-verified | F-012, C-008 | none | confirmed |
| M-026 | the artifact templates under `templates/` and their validators under `runtime/` | no-change-verified | F-004 | none | confirmed |
| M-027 | every command record in `registry/commands.yaml` other than `implement` | no-change-verified | F-021 | none | confirmed |
| M-028 | the agent contracts under `agents/` | no-change-verified | F-002 | none | confirmed |

Boundary crossings in the impacted set, each recorded because architecture decisions
concentrate at them: the runtime process to the detached capture process (M-009, D-002); the
runtime to the recording application over its local control server (M-007, D-003); the
runtime to the external encoder process (M-011, M-013); the runtime to the platform speech
engines (M-005); the runtime to the windowing system through platform calls (M-008); the host
session to the runtime through the tool-hook fragment and the pointer file at the runs root,
which is the one write outside the run's own directory (M-015, D-001); and the observation
layer to the run's persisted evidence, which it reads and never writes (M-003, C-007).

### 5.2 Options Considered

Criteria are applied in the fixed order of the reasoning procedure: (1) hard-constraint
satisfaction, (2) impact surface as the count of `contract-change` and `dependency-change`
modules, (3) reuse leverage as capabilities satisfied by reuse out of the twenty-two surveyed
in section 7, (4) quality-attribute satisfaction, (5) migration burden as the count of
contract-affecting changes needing a transition, (6) operability impact.

| Option | Structural change | 1 Hard constraints | 2 Impact surface | 3 Reuse leverage | 4 Quality attributes | 5 Migration burden | 6 Operability | Outcome |
|---|---|---|---|---|---|---|---|---|
| O-001 | Tap the single event emission point behind a per-run switch and a lazy import; a detached helper owns the recording; the edit is cut after the final gate decision | all satisfied | 3 | 12 of 22 | meets C-003, C-004, C-005, C-009; capture survives independently of the run process | 3 | one extra process only while filming; faults absorbed in the observation layer | selected |
| O-002 | The same tap, with the recording owned inside the runtime process | all satisfied | 3 | 12 of 22 | meets C-003, C-009; weakens C-004 because the recording shares the run's process and its failure modes | 3 | the recording ends with the run process and occlusion cannot be watched independently of it | rejected |
| O-003 | Instrument each phase and dispatch site directly, writing markers at every call site | violates C-003, C-006 | 3 | 11 of 22 | fails C-003: cost cannot be confined to one guard when every instrumented site pays | 3 | observation concerns spread through the execution path | eliminated (C-003) |
| O-004 | Reconstruct the presentation after the fact from persisted evidence only, with no live tap and no camera | violates C-015 | 2 | 10 of 22 | meets C-003, C-004; produces no material of the application | 2 | no live process at all | eliminated (C-015) |
| O-005 | Build a general run-telemetry pipeline and cut the presentation as one consumer of it | violates C-007 | 4 | 12 of 22 | meets C-003; commits the framework to a durable telemetry interface | 4 | a second durable interface to own and version | eliminated (C-007) |
| O-006 | Draw a synthetic dashboard of the run instead of filming it | violates C-015 | 2 | 9 of 22 | meets C-003, C-004; the picture is a diagram of the run, not the run | 2 | no external capture at all | eliminated (C-015) |

### 5.3 Selected Approach

- Selected: O-001.

- Structural change: one observation point at the ledger's emit function, reached only through
  an existence check on a per-run switch file and a lazy import, feeding a marker stream that
  is read by a scene layer, a narration and caption layer, and an editor. Capture is an
  adapter with two backends and is owned by a process detached from the run. Compilation is a
  once-claimed consequence of the run having nothing left to decide. Every optional external
  tool sits behind a substitution ladder whose lowest rung draws the run instead of filming
  it. Nothing in the layer writes outside the run's own directory except the pointer file at
  the runs root that the host tool-hook fragment reads.

- Rationale: the single emission point already carries everything a presentation needs, in
  order and stamped (F-001, F-005), so the capability needed a consumer and a clock rather
  than new instrumentation. Placing the consumer at that one point is what makes C-003
  satisfiable as written — the unrequested path costs exactly one existence check (F-012) —
  and what keeps C-009 true, because a dispatch reads nothing new. Detaching capture is what
  makes C-004 structural rather than merely careful: a recording owned outside the run's
  process cannot take the run down with it, and can watch the target while the run proceeds
  (F-017). Reading the run's own state store rather than the ledger summary is what makes
  C-011's "after the final gate decision" true rather than approximately true (F-015).

- Highest-scoring rejected alternative and why it lost: O-002. It ties O-001 on criteria 1,
  2, 3 and 5 and loses on criterion 4, then again on criterion 6. Owning the recording inside
  the runtime process makes the recording share the run's lifetime and its failure modes,
  which weakens C-004 from a structural property to a discipline, and leaves no independent
  observer able to notice that the target window stopped being the window on screen — the
  precise mechanism C-005 depends on. The evaluation table is re-derivable to the same
  conclusion: with criteria 1 to 3 and 5 equal, criterion 4 separates them.

- Tradeoffs accepted:
  - A second process exists while filming, and can be orphaned if the run dies abnormally
    (R-005).
  - The compilation claim is written before the build, so a crashed build leaves a run with no
    presentation and no automatic retry; that is deliberate, because an automatic retry of a
    crashing encode repeats the cost for the same result (F-014, R-007).
  - On the host as configured, the preferred backend is unreachable and the encoder backend
    records the screen rectangle the window occupies rather than the window itself, which
    leaves a residual that is accepted and recorded rather than reworded (D-003, R-001,
    R-011).
  - The tool-hook fragment is an operator-merged configuration rather than a framework-written
    one, so tool-call observation is optional and its absence is silent (D-001, R-009).
  - The layer is deliberately not an interface, so nothing downstream may build on the marker
    record (C-007, D-004 consequence in 8).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Observe the run at the single event emission point, behind a per-run switch file and a lazy import; supply tool-call observation through an optional configuration fragment the operator merges into the host session, read through a pointer file at the runs root | Yes | `architecture-decision-record-D-001.md` |
| D-002 | Let a process detached from the run own the recording and watch the target while the run proceeds | Yes | `architecture-decision-record-D-002.md` |
| D-003 | Select the capture backend by probing the control server at start, with the window-rectangle backend as the recorded fallback, and carry the window-identity residual as an accepted gap against `AC-008` as written | Yes | `architecture-decision-record-D-003.md` |
| D-004 | Catch and log every fault inside the observation layer, and keep it out of failure classification and recovery entirely | Yes | `architecture-decision-record-D-004.md` |
| D-005 | Compile exactly once per run, claimed by an exclusive file creation made before the build, and only when the run's own state store shows every phase committed and every gate decided | Yes | `architecture-decision-record-D-005.md` |
| D-006 | Degrade through a recorded substitution ladder for every optional external tool, whose lowest rung draws the run rather than failing | Yes | `architecture-decision-record-D-006.md` |
| D-007 | Carry the operator-facing surface on the existing command's published contract as an additive minor version with safe defaults, rather than as a new command | Yes | `architecture-decision-record-D-007.md` |
| D-008 | Keep the marker record private to the presentation path: no runtime interface exposes it, and no artifact contract consumes it | No | inline; it is the direct application of C-007 and adds no structure |
| D-009 | Fix the presentation-layer choices — the three narration registers, the pacing defaults, the head-and-tail condensation shape, and the overlay vocabulary borrowed from the status tree | No | inline; each is a presentation parameter and changes no boundary |
| D-010 | Place every file the layer writes under the run's own directory, derived from the install-prefix variable, with the single documented exception of the pointer file at the runs root | No | inline; it is the direct application of C-010 and the exception is carried by D-001 |

## API and Data Model Impact

- API changes: three contract-change modules, each additive.

  **M-016, the runtime's operator-facing surface.** Current shape: a request parser without
  recording parameters and a subcommand set without an observation subcommand, at runtime
  version 0.7.0. Target shape: the same parser with a recording parameter group added, an
  observation subcommand added, and the runtime version at 0.8.0. Compatibility approach:
  every added parameter is optional with a safe default of off, so an existing invocation is
  unchanged in both form and behaviour; the added subcommand occupies a name that was free.
  Coexistence period: none is required, because no existing form is superseded. Retirement
  condition: not applicable for the same reason. Rollback position: revert the four guarded
  sites and restore the runtime version, which returns the file to a state in which the
  package is unreachable; no run evidence outside the run's own observation directory is
  invalidated, because nothing else was written.

  **M-017, the command's published parameter documentation.** Current shape: a specification
  without a Parameters section for recording. Target shape: the same specification documenting
  the recording parameter group. Compatibility approach: documentation of an additive surface;
  no existing documented parameter changes meaning. Coexistence period: none. Retirement
  condition: not applicable. Rollback position: revert the specification to its prior text.
  Note that F-021 records the delivered parser and this specification disagreeing on the size
  of that surface, which P-003 sequences ahead of the contract being offered as evidence.

  **M-018, the command's registry record.** Current shape: version 1.0.0. Target shape:
  version 1.1.0 with a description stating an additive parameter group with a safe default.
  Compatibility approach: a minor increment under the declared versioning rule, which is what
  C-012 requires and what `AC-014` verifies; every dependent version constraint in the
  registry admits the new version. Coexistence period: none; a minor increment supersedes no
  prior form. Retirement condition: not applicable. Rollback position: restore the record to
  1.0.0 together with M-017, so the specification and the record never disagree about the
  contract's version.

- Contract compatibility notes: the three contract changes are consistent only as a set — the
  parser, the specification, and the registry record describe one surface — so P-003 requires
  them to agree before any of them is offered as evidence of the versioning rule, and the
  rollback positions above are taken together, never singly. No other registry record and no
  artifact contract changes (M-026, M-027), which is what keeps C-001 true.

- Schema or migration changes: None identified. No database, no persisted schema owned by
  another component, and no existing on-disk artifact changes shape, so there is no migration
  with a direction, a reversibility, or a reader-and-writer transition to state. The change
  does introduce new on-disk state: the per-run switch file, the marker stream, the
  observation log, the capture manifest, the compilation claim, and the finished outputs, all
  under the run's own directory, plus the pointer file at the runs root. Each is written only
  by the observation layer and read only by it (C-007, D-008), each is created rather than
  migrated, and removing the layer leaves them as inert files in past run directories that no
  reader consults, which is the reversibility position for this new state.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| An ordered, timestamped record of every run step | the run ledger's canonical event stream | reuse-as-is | F-001: every state change already passes through one point, in order, stamped |
| The exchange observed at the agent boundary | the invocation envelope and dispatch prompt written per phase | reuse-as-is | F-002: both are on disk at the moment each is complete, at the only place the exchange is visible |
| The per-phase validation verdict | the validation report written by the Validation Engine | reuse-as-is | F-003: the verdict a presentation must show is already persisted |
| Per-dispatch context cost figures | the execution-metrics module | reuse-as-is | F-004: it already estimates the figures a presentation reports, from persisted evidence only |
| Deterministic parsing of artifacts | the shared artifact-parsing library and the task-context module's parse-never-summarise discipline | reuse-as-is | F-004: anything a marker asserts must be parsed, not summarised, and that discipline already exists |
| A visual vocabulary for phases, gates, and statuses | the runtime's colorized status tree | reuse-extended | it already fixes how phases, gates, and their statuses read; the overlays extend that vocabulary to a video frame rather than inventing a second one |
| Path resolution across the two installed forms | the install-prefix variable | reuse-as-is | F-006, C-010: every path-facing element derives from it |
| Observation of host tool calls | the host session's own tool-hook mechanism | reuse-as-is | F-019: the host already posts every tool call, so no interception had to be built |
| True window capture unaffected by what is in front of it | the recording application driven over its local control server | reuse-extended | F-016: it provides window capture directly; the layer provisions its own scene collection and profile and never edits the operator's |
| Screen capture requiring no host configuration | the external encoder's screen-grab input, over the target window's rectangle | reuse-extended | F-016: available with no setup; its window-level input is unusable against a GPU-composited window (F-009), so the rectangle is captured |
| Speech synthesis | the platform speech engines, tried in a fixed order | reuse-as-is | F-008: voices are present on the operator host and each engine's absence falls to the next |
| Frame composition | the image library | reuse-as-is | F-008: present on the operator host and sufficient for the drawn frames |
| A signal that the run has nothing left to decide | the ledger's run-completion event and its summary | rejected | F-015: the summary counts phases and a gate is not a phase, so it fires while the closing gate is undecided; the run's own state store is read instead |
| Recovery and retry handling for a failed observation step | the runtime's failure classification and recovery machinery | rejected | C-008 forbids a fault in this layer entering that machinery at all, so reusing it would breach the constraint it exists to honour |
| A client for the recording application's control protocol | none | none-found | searched the runtime package, the metrics and task-context modules, the artifact library, and the wrapper modules; no protocol client exists, and C-002 forbids adding a dependency, so M-007 is standard library only |
| Mapping a marker stream onto footage and deciding the edit | none | none-found | searched the same set; nothing there holds a time base or maps one onto frames, which is the whole of what makes the footage editable — new structure M-004 and M-011 |
| A presentation frame, opening and closing cards, and lower thirds | none | none-found | searched the same set including the status tree, which renders a terminal tree and not a video frame — new structure M-010 |
| Timed subtitle cues and a presenter script derived from spoken lines | none | none-found | searched the same set; no component derives timing from recorded audio — new structure M-006 |
| A substitute presentation when nothing was filmed | none | none-found | searched the same set; no renderer, encoder wrapper, or deck builder exists — new structure M-012, M-013, M-014 |
| A per-run capability switch with persisted options | none | none-found | searched the runtime's run directory layout and the state store; the store holds lifecycle state and admits no per-capability switch without changing it, which C-001 forbids — new structure M-002 |
| Marker capture with replay de-duplication | none | none-found | searched the event stream and the metrics module; neither de-duplicates a replayed event, because neither needed to — new structure M-003 |
| A recording process that outlives the command that started it and watches its target | none | none-found | searched the runtime for any detached-process facility; the runtime leases adapters synchronously and owns no background process — new structure M-009 |

Twelve of the twenty-two capabilities are satisfied by reuse, which is the figure criterion 3
of the evaluation table uses. New structure is proposed only for the eight rows whose outcome
is `none-found` and never over the two `rejected` candidates, each of which records why it is
unsuitable rather than being passed over.

## Operational Considerations

- Logging and observability updates: the layer writes its own log in the run's observation
  directory, and every entry point catches and logs there rather than raising (M-001, C-004).
  The marker stream, the capture manifest, and the build manifest are the layer's own record
  of what it did and what it substituted, and the run status display reports marker count,
  filming state, and expected output (M-016, F-020). None of this is framework observability:
  C-007 and D-008 keep the marker record private to the presentation path, so no dashboard,
  metric, or downstream contract may consume it.

- Error handling strategy: faults are absorbed at the boundary of the observation layer and
  never classified (C-008, D-004). Three absorption sites carry the property — the event tap,
  the arming call during run planning, and the capture start — and each logs and continues.
  The substitution ladder of D-006 is the second half of the strategy: an absent external tool
  is not a fault but a recorded substitution, so the failure surface is confined to faults
  that are genuinely unexpected. The deliberate non-recovery is the compilation claim
  (F-014): a crashed build is not retried, and the run ends with a recorded absence rather
  than a repeated cost (R-007).

- Security considerations: the dominant risk is publication, not compromise (C-005). Three
  structural controls carry it. The capture session refuses to start unless the target is the
  foreground window, so an unrelated window is not captured by accident (F-017, M-008). The
  detached helper samples foreground state while filming and records the occluded spans so
  that footage is excluded and listed rather than silently published (F-017, M-009, R-001).
  The recording's own audio is never published, so nothing the host's microphone or output
  captured reaches a finished presentation (C-005, R-002). A fourth control bounds the
  tool-hook fragment: it records tool names and an excerpt of each target and never file
  contents (F-019), and because it is merged into a host session's settings rather than into
  a run, it observes every tool call that session makes while any run is recording (M-015,
  R-009). Restricted content reaching a recorded window or a recorded agent exchange is a
  residual this design cannot eliminate structurally, which is why P-004 places verification
  of the exclusion ahead of any presentation being offered for release and why the release
  approver remains an open question (Q-005).

- Performance considerations: the constraint is C-003, expressed as a measurable property
  rather than an expectation — one existence check per emitted event on the unrequested path,
  and no import of the package. F-012 establishes that the guard is the only cost, and P-005
  places its measurement ahead of the property being asserted (R-004). C-009 is satisfied
  structurally rather than by tuning: the capability adds nothing to what a dispatch reads,
  because it reads the run's evidence after the fact and contributes no module to any agent's
  load order. On the requested path the costs are real and bounded to the recorded run: one
  marker append per event, one additional process while filming, and an encode at the end
  whose duration scales with the recording (R-012).

- Deployment and operability impact: no new mandatory dependency (C-002), so the capability
  installs wherever the framework installs and each optional tool's absence is a recorded
  substitution (D-006). Two operator-facing operability notes follow from the design rather
  than from packaging: the preferred capture backend requires the operator to enable the
  control server through the recording application's own interface, which the framework will
  not do for them (A-004, C-002, Q-001); and the tool-hook fragment requires a manual merge
  into the host session's settings, which is why its absence is silent (M-015, D-001). The
  installable payload carries the whole change (F-022, M-022), so an installed copy of the
  framework gains the capability with the same guarded cost.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The divergence register F-019 to F-022 is reconciled against the change record and closed before any acceptance evidence is produced | M-015, M-016, M-020, M-022 | none | Evidence produced against an incomplete account of the delivered change is evidence about the wrong artifact; A-001 must be settled before anything rests on it | T-001, T-002, T-012 |
| P-002 | The capture backend in force for the live presentation is recorded before any segment-level evidence is produced | M-007, M-008 | P-001 | The segment-level criterion is assessed against whichever backend produced the footage, and the two backends leave different residuals (D-003) | T-004, T-006, T-016, T-017 |
| P-003 | The request parser, the published parameter documentation, and the registry record are brought into agreement before the command contract is offered as evidence of the additive change | M-016, M-017, M-018 | P-001 | Contract definition precedes every consumer change; a published contract that understates its own surface cannot evidence the versioning rule (F-021) | T-002, T-028, T-029 |
| P-004 | The withheld-span exclusion is verified on a run whose target window was deliberately obscured before any presentation is offered for release | M-008, M-009, M-011 | P-002 | A reversibility safeguard precedes an irreversible step, and publication cannot be undone (C-005) | T-005, T-006, T-007 |
| P-005 | The cost of the unrequested path is measured before the zero-cost property is asserted | M-001, M-016 | P-001 | Verification of a boundary precedes work that assumes the boundary holds (C-003) | T-003, T-008, T-009 |
| P-006 | Fault absorption is demonstrated against an induced fault before the recording path is exercised on a run whose outcome matters | M-001, M-016 | P-005 | The same rule: C-004 must be shown to hold before a governed run is asked to depend on it | T-010, T-011 |
| P-007 | One complete recorded lifecycle exists before the marker reconciliation and the closure behaviour are assessed | M-001, M-003 | P-004, P-006 | Replay de-duplication, the final-gate stop, and the compile-once property are only observable on a run that reached its last gate decision (F-013, F-014, F-015) | T-013, T-014, T-015, T-020, T-021, T-022 |
| P-008 | The substitution ladder is exercised with each optional external tool absent in turn before the no-mandatory-dependency property is asserted | M-005, M-008, M-012, M-013, M-014 | P-007 | The ladder's lower rungs are reachable only when the rungs above them are absent, so the property cannot be shown on a fully equipped host (C-002) | T-023, T-024 |
| P-009 | A second presentation is produced from the recording made at P-007, without filming or executing the run again | M-004, M-011 | P-007 | Re-cutting is demonstrable only against a recording that already exists, which is the separation of recording from editing that the approach rests on (S-010) | T-025, T-026, T-027 |
| P-010 | The change-wide regression evidence is produced only after every reconciliation above has closed | M-016, M-021 | P-001, P-003, P-005, P-006, P-007, P-008, P-009 | A suite run taken before the record corrections close does not evidence the change that will be released (S-014) | T-012, T-030, T-031, T-032 |
| P-011 | The running-length threshold and the first-time-viewer review definition are settled before the audience-layer evidence is assessed against the audience criterion | M-004, M-006 | none | A criterion with no threshold and no pass condition has no decidable outcome, so evidence produced against it cannot be assessed either way (Q-003, Q-004) | T-018, T-019, T-022 |

Every task of the supplied breakdown appears in the Binds column above: `T-001` to `T-032`
are each carried by at least one sequencing constraint, and none is left constrained only
indirectly. The audience-layer tasks are additionally bounded by the pacing parameters D-009
fixes, and the closure tasks by Q-007.

### Test Strategy Focus Areas

For omn-qa, in the order the sequencing constraints reach them:

- The unrequested path, measured rather than reviewed: that the package is absent from the
  process image and the per-event cost is the guard alone (C-003, P-005).
- Fault absorption under an induced fault at each of the three absorption sites, comparing the
  observed run's status, artifacts, gate decisions, and recovery outcome against an unrecorded
  run of the same work (C-004, C-008, P-006).
- Replay de-duplication: that a replayed event produces no second marker, and that marker
  order and millisecond stamping reconcile against the event stream and the phase directories
  (F-013, P-007).
- The closure behaviour: that the camera stops only after the last gate is decided and that
  exactly one presentation is produced without a further command, including on a run that
  emits more than one finishing event (F-014, F-015, P-007).
- The exclusion path on a deliberately obscured run: that every occluded span appears in the
  capture manifest and that no excluded footage appears in the finished presentation
  (C-005, P-004).
- The substitution ladder with each optional tool absent in turn, confirming that each absence
  is recorded rather than inferred (C-002, P-008).
- The condensation disclosure: that every condensed span carries its factor on screen and that
  a rejection and a retry both appear (C-015, `AC-008`, `AC-009`).
- Re-cutting: two presentations differing in length or narration from one recording, with no
  second filming (S-010, P-009).
- The three contract surfaces read together for agreement on the size of the parameter group
  (F-021, P-003).

### Rollout and Rollback

- Rollout: the capability is already delivered and inert until requested, so rollout is the
  closure of P-001 to P-011 rather than an enablement step. The one host-side action rollout
  may require is the operator enabling the control server for the live presentation, which is
  an operator act outside the framework (A-004, Q-001), and the one optional action is merging
  the tool-hook fragment into the host session's settings (M-015).

- Rollback: remove the package directory and the delivered test set, revert the four guarded
  sites in the runtime and restore the runtime version, revert the command specification and
  the registry record together so they never disagree, revert the wrapper forwarding and the
  documentation, and regenerate the installable payload so it does not carry a capability the
  repository no longer has (M-022). The change record states the same position for the first
  four of these; the payload and the status-display site are additions this design records
  under F-020 and F-022, and a rollback taken from the change record alone would leave both
  behind. No run evidence outside each run's own observation directory is invalidated, because
  the layer writes nothing else except the pointer file at the runs root, which is removed with
  it.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | security | The target window stops being the window on screen for an interval shorter than the helper's sampling period, or between its last sample and the stop | Footage that was not of the run reaches a finished presentation, breaching the constraint that outranks completeness | medium | M-008, M-009, D-003 | Verify the withheld-span list against the finished presentation on a deliberately obscured run at P-004, and withhold rather than publish where the manifest is silent | omn-qa |
| R-002 | security | The recording's own audio track is carried into a finished presentation by a build path that does not strip it | Audio that was never part of the run is published | low | M-011, D-003 | Inspect the finished presentation's tracks as part of the segment-level review at P-004 | omn-dev-2-reviewer |
| R-003 | delivery | A further divergence between the change record and the delivered change is found after the acceptance reconciliations have started | The plan governs an incomplete artifact; reconciliation tasks become construction tasks and the wave structure is re-derived under the execution plan's R-010 | medium | M-016, M-022 | Close the divergence register at P-001 before any acceptance evidence is produced, and route confirmation of A-001 and A-005 to the owner the Planning Gate assigned | omn-tech-lead |
| R-004 | performance | The unrequested path is exercised and the guard is not the only cost, because a caller reaches the package outside a guard | The zero-cost property fails as written and `AC-003` cannot be met | low | M-016, D-001 | Measure the unrequested path at P-005 rather than reviewing it, on a host where no optional tool is present | omn-qa |
| R-005 | operability | The run process dies abnormally while the detached helper is filming | An orphaned recording process holds the target and the capture manifest is left in a recording state | medium | M-009, D-002 | Verify the stop path on an aborted run as part of the fault-absorption work at P-006 | omn-dev-1-implement |
| R-006 | contract | The request parser, the published parameter documentation, and the registry record are offered as evidence while they disagree on the size of the parameter group | `AC-014` is evidenced against a contract that understates its own surface, and the additive-version claim is unsupported | high | M-017, M-018, D-007 | Bring the three into agreement at P-003 before any of them is offered as evidence | omn-documentation |
| R-007 | operability | The build crashes after the compilation claim is written | The run ends with no presentation, no automatic retry, and a claim file that suppresses a later attempt | medium | M-001, D-005 | Treat a claimed-but-absent output as a recorded absence during the closure assessment at P-007, and decide manually whether to re-cut from the existing recording at P-009 | omn-tech-lead |
| R-008 | structural | A downstream consumer treats the marker record as an interface it may depend on | The layer acquires a durable contract it was designed not to have, and the constraint against a metrics pipeline is breached by accretion | low | M-003, D-004 | Keep the record undocumented as an interface and assess any proposed consumer against the constraint during the governance review at P-010 | omn-tech-lead |
| R-009 | security | The tool-hook fragment is merged into a host session's settings and that session performs work unrelated to a recorded run while a run is recording | Tool names and target excerpts from unrelated work enter a run's marker record and may reach a presentation | medium | M-015, D-001 | Verify the pointer-file gating on a session performing unrelated work as part of the exclusion verification at P-004 | omn-tech-lead |
| R-010 | operability | The control server is enabled for the live presentation, changing the backend from the one the delivered evidence was produced on | The segment-level evidence describes a capture path the presentation does not use, and the accepted gap in D-003 no longer describes the delivered behaviour | medium | M-008, D-003 | Record the backend in force at P-002 before any segment-level evidence is produced, and re-produce that evidence if the backend changes afterwards | omn-tech-lead |
| R-011 | delivery | The criterion requiring every segment to be material of the application is assessed against the rectangle backend and the accepted gap is not carried forward with it | The criterion appears satisfied when a residual remains, or is quietly reworded to match the backend, which the binding constraint forbids | medium | D-003 | Carry the accepted gap as a named condition of the segment-level evidence at P-002 and P-004, and never as an amendment to the criterion | omn-qa |
| R-012 | performance | A long recorded run reaches its final gate and the encode runs while the operator expects the run to be finished | The run appears to hang after its last gate decision, on a path the operator did not ask to wait for | low | M-011, D-005 | Confirm the reported state during the complete-lifecycle run at P-007 and record the observed encode cost with it | omn-tech-lead |
| R-013 | delivery | The existing suite or a framework verifier fails on the delivered change, or a previously passing check is found weakened to accommodate it | The additive-only claim is lost change-wide and the delivered capability cannot be accepted | medium | M-016, M-021 | Produce the change-wide regression evidence at P-010, after every record correction has closed, and review the change for weakened assertions rather than only for a green result | omn-qa |
| R-014 | operability | The presentation's honesty rests on disclosure and the disclosure is judged insufficient at review | The exclusion-plus-disclosure position behind A-006 fails and the editor requires a structural change rather than an inspection | low | M-011, D-003 | Review the condensation disclosure and the withheld-span list together at P-004 rather than separately | omn-qa |

## Estimate and Confidence

- Overall: `M` (confidence: medium). The construction is delivered, so the architectural
  effort this estimate covers is the reconciliation of the record against the delivered
  structure and the settlement of the capture path — multiple modules, three contract surfaces
  that must be made to agree, and no migration.

- Breakdown:
  - P-001, the divergence register across four modules: `S` (confidence: medium). It is bounded
    if A-005 holds and unbounded if it does not, which is what the confidence qualifier carries.
  - P-002 and P-004, the capture path and the exclusion verification: `M` (confidence: medium).
    Two backends with different residuals, and a control whose verification depends on
    reproducing an occlusion.
  - P-003, the three contract surfaces: `S` (confidence: high). The disagreement is enumerable
    and the target shape is fixed by the delivered parser.
  - P-005 and P-006, the cost and absorption properties: `S` (confidence: high). Both are
    measurable against an unrecorded run of the same work.
  - P-007, P-008 and P-009, the lifecycle, ladder, and re-cut evidence: `M` (confidence: low).
    Each depends on a host that can be varied and on a run that reaches its final gate, neither
    of which this design controls.
  - P-010, the change-wide regression evidence: `S` (confidence: medium).
  - P-011, the settlement of the audience criterion: `XS` (confidence: medium). Two decisions
    with named owners in section 12 and no construction in either.

- Scope assumptions: the estimate rests on A-001 (nothing further diverges outside the four
  re-read sites), A-002 (the delivered tests pass and nothing is re-implemented), A-003 (the
  presentation runs on the host F-007 describes), and A-005 (the divergences are record
  corrections rather than construction). If A-005 fails, the overall level is not `M` and the
  work is not reconciliation.

- Uncertainty drivers: the open divergence register and its confirmation (R-003); the
  unsettled operator election on the capture backend and the accepted gap that hangs on it
  (R-010, R-011); the host variation that the substitution ladder requires (P-008); and the
  unsettled running-length threshold and reviewer identity for the audience criterion, which
  bound the pacing work without bounding this design.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does the operator enable the recording application's control server for the live presentation, or does the presentation run on the window-rectangle backend that D-003 records as in force on the host as configured? | no | omn-tech-lead | D-003, M-008 | Enabling it removes the window-identity residual and changes the backend the delivered evidence was produced on, so the P-002 evidence is re-produced; leaving it disabled keeps the residual as the accepted gap D-003 records against `AC-008` as written. This is the residual of the capture-path question the execution plan carries, whose architectural half D-003 settles |
| Q-002 | Are the four divergences F-019 to F-022 bounded corrections to the change record, as A-005 judges, or do they indicate undelivered construction? | no | omn-tech-lead | M-015, M-016, M-020, M-022 | Confirmed as corrections, P-001 closes them and the acceptance reconciliations proceed; found to be construction, the execution plan's R-010 fires and its wave structure is re-derived from this phase. Raised here rather than absorbed, as the Planning Gate's condition on A-001 requires |
| Q-003 | What minimum running length settles the audience criterion, given that the inputs state only "several minutes" and that a first cut of thirty-five seconds was rejected? | no | omn-product-owner | M-004, M-006 | A threshold above what was delivered reopens the audience layer for re-pacing; a threshold at or below it closes `AC-010`'s length component against the delivered pacing parameters D-009 fixes |
| Q-004 | Who performs the first-time-viewer review that decides the audience criterion, and what outcome counts as a pass? | no | omn-qa | M-004, M-006 | Without a named reviewer and a pass condition, `AC-010` has no decidable outcome and moves to a follow-up with its own owner |
| Q-005 | Who approves that a particular finished presentation may be released, given that publication and distribution are out of scope? | no | omn-tech-lead | P-004 | Unanswered, material can leave the team with no accountable approver, which is the exposure the publication controls in section 8 exist to bound |
| Q-006 | Is the short reference cut for onboarding an existing team a deliverable of this change, or satisfied by the re-cut path? | no | omn-product-owner | P-009 | A deliverable adds an output to the re-cut work; satisfied by the re-cut path, P-009's two-cut evidence closes it |
| Q-007 | How is the closure-phase work carried out and recorded, given that the runtime's implemented surface does not execute it? | no | omn-orchestrator | P-010 | Unanswered, the closure tasks have no executing owner and the Closure Gate has nothing to decide on |
| Q-008 | Do the Design Gate owners accept decision records D-001 to D-007, which are emitted at status `Proposed`? | no | omn-tech-lead | D-001, D-002, D-003, D-004, D-005, D-006, D-007 | Acceptance permits implementation to proceed against this design; rejection of any record returns this phase, because the selected approach in 5.3 is the conjunction of all seven. The owner is named under the Producer Exclusion Rule, which excludes the producing role from deciding this gate |

## Sign-off

Design Gate owners for this workflow, per `workflows/workflow-gate-matrix.md`: omn-architect
and omn-tech-lead (F-024). This agent produced the technical design package and the seven
decision records assessed at that gate, and the Producer Exclusion Rule reads through role
aliases, so the producing role's entry cannot decide this gate and the accepting owner is
**omn-tech-lead**. No line below is offered to the producing role, and every line is left
unsigned.

- Tech Lead (accepting owner, omn-tech-lead): _______________
- QA (omn-qa, verification focus areas in section 9): _______________
