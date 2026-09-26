# Performance Refactor Report: Runtime 0.7.0

Date: 2026-09-08. Scope: dispatch cost of one task through the framework. Method: audit the
runtime and one representative `/implement` run, classify every expensive operation, change the
runtime and the loading discipline only, measure before and after on the same persisted runs,
and re-run every framework verifier and the test suite.

The workflow is unchanged: every phase, agent, skill resolution, gate, validator, template, and
artifact contract that ran before still runs. What changed is how much each dispatched agent is
asked to read, what it is handed instead of re-deriving, and what the run records about its own
cost.

## 1. Performance audit

Representative task: `/implement` -> `implement-feature`, run `run-4c51600606df` (six phases,
nine agent invocations including one repair and one rework pass, six gates, 69 h wall clock,
about 12.6 h of agent-active time, of which one overnight review attempt accounts for 10 h).

What one dispatch asked its agent to read, before this change:

| Component | Size | Read by |
|---|---|---|
| The agent's full module set, "each in full, do not skim" | 64-108 KB per agent (`examples.md` alone 7-32 KB; `identity.md` 14-22 KB) | every agent, every attempt, including repair passes |
| Context slice base: four registries, capability matrix, skill matrix, gate matrix, three context files | ~93 KB | every phase (the tech lead's lifecycle module said "read every artifact the slice names") |
| `runtime/README.md` in the phase slice | 43 KB | 20 of 37 phases |
| Upstream artifacts, in full | scope 22 KB, plan 55 KB, design 72 KB + 28 KB of ADRs, implementation report 30 KB, review package 29 KB | each downstream agent |
| Adapter, envelope, prompt, template | ~15-25 KB | every dispatch |
| Skill files | 1.2-1.7 KB each | every phase-required and manifest-declared skill |

Bottlenecks, by category:

- **A. Required, kept.** Six phases and six gates of implement-feature; per-phase artifact
  validation (32-78 checks); the implementer's baseline test run, evidence run, and regression
  run; the reviewer's independent read of the diff; the QA-owned gates; the repair and rework
  loops.
- **B. Required but duplicated.** (1) Every agent re-performed the Initialization checks the
  runtime had already made when building the envelope: manifest identity, version, status,
  load order, and counting the twelve sections of `identity.md`. (2) Every downstream agent
  re-derived the objective, scope, acceptance criteria, decisions, constraints, and changed
  files from the full upstream artifacts. (3) The registries and matrices the runtime had
  already resolved routing against were in every slice as reading material. (4) The gate
  matrix was listed twice in the scope and framing slices. (5) A repair pass re-read the full
  module set although the prompt said to load only what the findings need. (6) Within one
  runtime command, `refresh()` re-resolved the full capability chain (registries, manifest,
  every module digested) once per pending work item, re-reading each file from disk each
  time.
- **C. Required but unnecessarily sequential.** The runtime already supports a dependency
  graph and guards leasing on hard predecessors, but `next` named one action, the runbooks
  drove one phase at a time, and nothing reported which phases could run together.
- **D. Conditional work executed for every task.** The database skill was read for every
  design, implementation, and root-cause phase whether or not persistence was touched; the
  performance skill for every review and validation phase; security, React, and Avalonia
  wherever a manifest named them.
- **E. Context and token waste.** Items in the table above, plus artifacts of 22-72 KB whose
  length no validator requires, and the `runtime/README.md` slice member on phases that never
  touch the runtime.

## 2. Before and after execution flow

```text
BEFORE

Command
 -> plan (one work item per phase and gate; chain dependencies)
 -> for each phase, strictly one at a time:
      next -> dispatch
      -> agent: read manifest + 7 modules in full + adapter + envelope
               + every slice member (registries, matrices, runtime README, skills)
               + every upstream artifact in full
               + repeat the Initialization contract checks
               + rescan the repository
      -> complete (validate)  -> gate
 -> repair/rework: the same full read again
 -> completion package + final report
```

```text
AFTER

Command
 -> plan (same work items; parallel groups printed; task-context.yaml written)
 -> next (names the phase, and every phase dispatchable alongside it)
 -> dispatch
      -> envelope: load_profile (core / on-demand), contract_checks (done by the runtime),
                   skill_dispatch (required / not-triggered), slice read hints,
                   task_context, upstream sections to read first, context_budget
      -> agent: read task-context.yaml
               + 4 core modules (system, reasoning, output, quality)
               + slice members marked required
               + skills marked required
               + upstream sections marked read-first; the rest on demand
               + start from the recorded repository context
 -> complete (same validator, same gate) -> execution-metrics.json updated
 -> repair pass: quality.md + output.md + the module the failed check names
 -> completion package + final report (+ Execution Metrics section)
```

## 3. Changed files

| File | Change |
|---|---|
| `runtime/task_context.py` (new) | Task context builder: deterministic fact extraction from accepted artifacts, affected-area derivation, skill-dispatch verdicts, upstream section map, parallel-group computation, YAML read/write |
| `runtime/execution_metrics.py` (new) | Execution metrics document and the per-dispatch legacy-vs-progressive context estimate |
| `runtime/framework_runtime.py` | Version 0.7.0. Per-process read cache. `load_profile`, `contract_checks`, `slice_read_hint`, `soft_pending`, `refresh_task_context`, `write_execution_metrics`. Slice dedupe and read hints. Envelope gains `load_profile`, `contract_checks`, `skill_dispatch`, `task_context`, `upstream_artifacts[].sections`, `parallel_group`, `context_budget`. Dispatch prompt rewritten around the loading discipline and artifact economy. `next` lists co-dispatchable phases and early-start choices. `plan` prints parallel groups. New `metrics` subcommand; `--load-profile`, `--affected-area`, `next --all`. Final report gains an Execution Metrics section |
| `agents/*.agent.md` (12) | Bootstrap Step 2: load the module set under the envelope's load profile, accept the runtime's contract checks; no module text duplicated (verifier C10) |
| `agents/*/execution.md` (12) | Initialization: load the core tier, load on-demand modules on their trigger, accept `contract_checks` for the twelve sections; tech lead reads the members marked required |
| `config/runtime.md` | Read hints under Context Loading; new sections Task Context, Progressive Module Loading, Conditional Skill Dispatch, Execution Metrics |
| `config/execution-engine.md` | Envelope field list (additive), context-narrowing rules, concurrent leases policy, new Artifact Economy policy |
| `skills/skill-resolver.md` | New section Domain-conditional skill reading, with the trigger table and its rules |
| `runtime/README.md` | Files table, usage, new section on what a dispatch asks an agent to read, run layout, implemented table |
| `docs/USER-GUIDE.md`, `docs/user-guide.html` | New section 5f; HTML regenerated by the renderer |
| `tests/test_lean_dispatch.py` (new) | 19 tests over extraction, affected areas, skill dispatch, parallel groups, load profile, read hints, prompt, metrics |
| `omn_agent/_bundled_payload/**` | Mirror of the framework payload, regenerated by `tests/test_bundled_payload.py --sync` |
| `reports/performance-refactor-report-2026-09-08.md` (this file) | Audit, measurements, and the record of what is preserved |

No workflow specification, Phase Model, gate matrix, registry, manifest, template, validator, or
skill file changed.

## 4. Preserved workflow

Mandatory and unchanged:

- Every phase of every active workflow, in the order and with the hard dependencies its Phase
  Model declares. `plan_run`, `derive_dependencies`, the guards G1-G5, and the gate guards are
  untouched.
- Every gate, its owners, the Producer Exclusion Rule, the auto-approval policy, rollback, and
  supersession.
- Every phase owner agent and every agent's module set. All seven modules remain in the
  manifest load order and remain binding; three of them are now loaded on a stated trigger
  instead of up front. `dispatch --load-profile full` restores the previous read.
- Every skill resolution. Phase-mandatory and manifest-declared codes still resolve through
  `registry/skills.yaml`, and G1 still blocks a phase whose codes do not. Domain-general skills
  (S01, S02, S03, S07, S10, S11, S12) are always read when named. Security is always read in
  review and validation phases.
- Every validator and every check in it; every artifact template and output contract; the
  frozen context slice's membership and digests; the idempotency key derivation; the result
  envelope contract; the recovery matrix and retry profile.
- Every existing runtime subcommand and argument. New fields are additive; a consumer that
  reads the original envelope fields reads them unchanged.

## 5. Removed duplication

| Duplication | Resolution |
|---|---|
| Each agent re-verified manifest identity, version, status, load order, and the twelve contract sections | Performed once by the runtime at dispatch, recorded in `capability_bindings.contract_checks`; agents accept a `pass` record |
| Each downstream agent re-derived objective, scope, criteria, decisions, constraints, changed files, risks, and open questions from full upstream artifacts | Carried once in `task-context.yaml`, rebuilt from accepted artifacts at every transition; upstream artifacts are read by section |
| Registries and matrices read by every agent | Marked `runtime-resolved`; the planner, whose artifact is validated against them, keeps the skill registry and capability matrix as `required` |
| `runtime/README.md`, the domain model, and the routed workflow specification read by every phase in their slice | Marked `on-demand` with the decision that needs them |
| The gate matrix frozen twice in four slices | Deduplicated at slice construction |
| Repair pass re-read the whole module set | The prompt names `quality.md`, `output.md`, and the module the failed check's quality reference names |
| `refresh()` re-read every registry, manifest, and module per pending work item per command | Per-process read cache keyed by path, mtime, and size |
| Repository rescanned by every agent | `repository_context` in the task context names the relevant modules and files from the accepted design and change set, and the conditions under which a rescan is warranted |

## 6. Parallelization

The runtime now computes parallel groups (topological levels over hard edges), records them in
the task context and `plan` output, lists every co-dispatchable phase in `next`, and carries
`parallel_group` in each envelope. Two eligible phases may hold leases at once; this is safe
because the guards already refuse to lease a phase before its hard predecessors commit and the
runtime refuses two writers of one artifact path.

Honest finding: the shipped Phase Models are chains. Every Input column either names the
immediately preceding phase's artifact or names none, in which case the runtime derives an edge
to the preceding row. Parallel groups are therefore one phase wide for every workflow when only
hard edges exist. The one exception is the soft edge from `scope-and-acceptance` to
`execution-planning` when a feature request is supplied: the planner may start early, but doing
so forgoes the scope definition as its input. The runtime reports that as a choice with its
cost ("dispatchable early") and the default sequence still waits. Widening any group further
would require changing an Input column, which changes the logical workflow and was out of
bounds. Within-phase parallelism is not available either: subagents cannot spawn subagents.

## 7. Conditional dispatch

| Skill | Area | Triggered by | Default when undeterminable |
|---|---|---|---|
| S04 Avalonia | `avalonia-ui` | avalonia, xaml, view-model, mvvm, desktop ui | required |
| S05 React | `react-frontend` | react, jsx, tsx, hooks, redux, frontend | required |
| S06 Database | `database` | database, sql, migration, entity framework, orm, persistence layer, transaction boundary, data model | required |
| S08 Performance | `performance` | performance, latency, throughput, benchmark, p95/p99, load test, profiling | required |
| S09 Security | `security` | security, authentication, authorization, token, secret, credential, permission, encryption, injection, xss, csrf, cors, pii | required; always required in review and validation phases |

Triggers are scanned over the supplied inputs and every accepted upstream artifact; the
operator may declare an area with `--affected-area` (additive, persisted). A `not-triggered`
skill stays resolved and is read if the work reveals its domain, which the artifact then
records. Phases and gates are not conditional: every phase still runs.

## 8. Performance metrics

Measured with `framework_runtime.py metrics`, which applies today's read hints to the persisted
envelopes of historical runs. Tokens are estimated at four bytes per token.

| Run | Workflow | Invocations | Legacy estimate | Progressive estimate | Reduction |
|---|---|---|---|---|---|
| `run-4c51600606df` | implement-feature | 9 (6 agents) | ~509,800 tokens | ~236,100 tokens | 53.7% |
| `run-34ca35504b72` | refactor | 8 (4 agents) | ~437,000 tokens | ~181,400 tokens | 58.5% |
| `run-3e6f6a248b99` | fix-bug | 6 (4 agents) | ~444,600 tokens | ~201,500 tokens | 54.7% |

Per phase of the implement-feature run:

| Phase | Legacy | Progressive | Reduction |
|---|---|---|---|
| scope-and-acceptance | ~54,200 | ~20,700 | 61.8% |
| execution-planning | ~57,100 | ~28,500 | 50.1% |
| solution-design-and-risk-assessment | ~106,200 | ~50,200 | 52.7% |
| implementation | ~108,300 | ~53,300 | 50.8% |
| quality-review | ~95,300 | ~47,600 | 50.0% |
| documentation-and-release-handoff | ~88,700 | ~35,800 | 59.7% |

Other counts for the implement-feature run: context members required 48 of 99 declared; files
read by more than one dispatch 16 (was 25); phases 6, invocations 9, validation runs 8 passed
and 1 failed, gates 6. A fresh scope-and-acceptance dispatch on the new runtime measured
~45,300 -> ~18,800 tokens (58.5%).

What is not measured: the agents' own reading of repository source and their reasoning tokens,
which the runtime does not control, and the effect of the artifact-economy policy on artifact
length, which will show in the next runs' `upstream_full_bytes`. Wall-clock time is dominated
by human gate waits and idle attempts (one review attempt spanned an overnight pause), so no
duration claim is made beyond the token estimate.

## 9. Regression validation

| Check | Result |
|---|---|
| `verify_manifests.py` | 2/2 CONFORMS |
| `verify_registry_coverage.py` | 6/6 COVERED |
| `verify_validators.py` | 6/6 COVERED |
| `verify_recovery.py` (full dispatch, complete, retry, rollback cycles on the new runtime) | 74/74 RECOVERY PROVEN |
| `verify_multi_phase.py --run-id run-4c51600606df` (including M14 live replay through the new dispatch and complete) | 15/15 PROVEN |
| `verify_multi_phase.py` on the refactor (`run-34ca35504b72`) and fix-bug (`run-3e6f6a248b99`) runs | 15/15 PROVEN each, after M6 was made workflow-aware (see Remaining bottlenecks); 14/15 before, the failure being M6's pinned implement-feature phase names |
| `verify_vertical_slice.py --slice implement`, `--slice architect` (adapter duplication check C10 included) | 10/10 PROVEN each |
| `verify_self_hosting.py --release-checklist` | 9/9 SELF-HOSTING |
| `tests/test_lean_dispatch.py` (new) | 19 tests OK |
| Runtime, gate, contract, and handbook test modules | 205 tests OK |
| `tests/test_bundled_payload.py` after `--sync` | 11 tests OK |
| Full suite `python -m unittest discover -s tests` | 493 tests OK in 13m09s (baseline before the change: all tests OK in 13m41s) |

Backward compatibility exercised: existing runs replay unchanged (M14), `omn-agent` drives the
runtime through the same subcommands and parses the same status JSON, and the pre-0.7.0 read
behaviour is one flag away.

## 10. Remaining bottlenecks

- **Artifact length.** Artifacts of 22-72 KB are the largest remaining per-phase read. The
  artifact-economy policy is stated in the prompt and the execution-engine specification, but
  no validator measures it; the next runs will show whether it holds, and a length advisory
  check per validator is the natural follow-up.
- **Workflow serialisation.** Parallel groups are one phase wide by construction. A future
  workflow revision that lets the reviewer and QA phases consume the implementation report
  directly, or that splits review lenses across owners, would create genuine groups; it is a
  workflow change and needs its own change proposal.
- **Repository reading.** The task context records relevant modules and files, but each agent
  still reads the code at those sites itself; nothing caches file contents across agents, and
  nothing should until a content-addressed cache with the same integrity rules as the context
  slice exists.
- **Gate waits.** Wall clock is dominated by human gate decisions. The auto-approval policy
  covers clean evidence; a notification path or deadline for held gates does not exist.
- **Self-hosting record.** This change was applied directly and is recorded here rather than
  carried by a governed run; a change proposal under `proposals/` with run evidence is the
  follow-up the self-hosting profile expects.
- **`verify_multi_phase.py` M6** (fixed in this change). It pinned implement-feature's phase
  identifiers and so failed on every other workflow. It now derives the chain from the routed
  Phase Model: the delivery phase is the one whose owner holds the `implementation-delivery`
  capability (else the last phase), and the two roles before it are its nearest hard
  predecessors. Every persisted run of every workflow that actually traversed its chain now
  passes; the two August runs that stalled with blocked phases fail M6 honestly, as they should.

## Trade-offs, stated

- On-demand modules are binding but not in context until their trigger. An agent that
  mis-recognises a trigger reads `identity.md` or `execution.md` late rather than never; the
  Validation Engine and the gate judge the artifact by the same contracts either way, and the
  operator can force `--load-profile full`.
- Domain-conditional skills depend on a keyword derivation. It errs toward inclusion (unknown
  never narrows, security always read in review), and the operator can declare an area.
- The task context is a projection. It carries identifiers so the reader can open the source;
  it never replaces the artifact as evidence, and the validators still read the artifacts.
