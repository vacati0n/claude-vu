# Registry Coverage Report

Date: 2026-08-18
Increment: Phase 3 of `reports/self-hosting-execution-plan-2026-08-18.md` — Register Operational
Surface.
Machine record: `reports/registry-coverage-2026-08-18.json`, produced by
`runtime/verify_registry_coverage.py`.

## 1. Objective and Exit Criteria

Objective: make command, workflow, and agent coverage match intended usage.

| Exit criterion | Result |
|---|---|
| 100% of active commands resolve to active workflows | Met. 9 of 9 active command records resolve, unresolved = 0 |
| 100% of active workflow phase owners are invocable | Met. 12 of 12 phase owners carry a valid `agents/<agent-id>.agent.md` entry point, unresolved = 0 |

Invocable is used here in the sense the roadmap's target definition gives it: host-invocable
through an `*.agent.md` entry point. That is not the same as runtime-dispatchable, which
additionally needs an agent registry record, a runtime module set, and a registered validator.
Section 7 reports dispatchability separately with counts, so coverage is never read as
capability.

## 2. Coverage Counts

Reproduce with:

```bash
python .claude/runtime/verify_registry_coverage.py
```

| Check | Result | Counts |
|---|---|---|
| C1 every active command record resolves to exactly one active workflow record | PASS | active_commands=9, resolved=9, **unresolved=0**, command_specs_on_disk=9, specs_without_a_record=0 |
| C2 every active workflow publishes a machine-resolvable Phase Model table | PASS | active_workflows=7, with_phase_model=7, **unresolved=0**, phases_total=36 |
| C3 every phase owner named by an active Phase Model is host-invocable | PASS | phase_owners=12, host_invocable=12, **unresolved=0** |
| C4 every phase-mandatory skill resolves to an active skill registry record | PASS | skill_references=101, resolved=101, **unresolved=0** |
| C5 every gate a Phase Model names resolves to a non-producing owner | PASS | gate_references=28, decidable=28, **unresolved=0** |
| C6 phase dispatchability, reported per phase with a reason for each blocker | PASS | phases=36, dispatchable=3, blocked=33 |

C1 to C5 are assertions. C6 is a report: a phase blocked with a recorded reason is the
framework's accurate state, not a coverage failure, so counting blockers is the check.

## 3. Before and After

| Surface | Before | After |
|---|---|---|
| Active command records | 1 (`implement`) | 9 |
| Active workflow records | 3 | 7 |
| Workflows publishing a Phase Model | 1 | 7 |
| Canonical phase identifiers | 6 | 36 |
| Host-invocable agents (`*.agent.md`) | 2 | 12 |
| Registered skills | 9 | 10 (S10 added) |
| Gate rows in the gate matrix | 17 | 28 |
| Runtime-dispatchable phases | 2 | 3 |

## 4. Command Resolution

Every row resolves command record → active workflow record → workflow specification, checked
with the runtime's own resolvers.

| Command | Primary workflow | Workflow status | Owning phase for scoped commands |
|---|---|---|---|
| `/implement` | `implement-feature` | active | full lifecycle |
| `/bugfix` | `fix-bug` | active | full lifecycle |
| `/refactor` | `refactor` | active | full lifecycle |
| `/investigate` | `investigate` | active | full lifecycle |
| `/research` | `research` | active | full lifecycle |
| `/review` | `review-pull-request` | active | full lifecycle |
| `/release` | `release` | active | full lifecycle |
| `/document` | `implement-feature` | active | `documentation-and-release-handoff` |
| `/test` | `review-pull-request` | active | `test-risk-validation` |

Two decisions were required to reach this table.

`/document` and `/test` each named several workflows, which
`domain-model/command-specification.md` forbids. Each now names one primary workflow and carries
a cross-reference table listing the phase that does the same kind of work in every other
lifecycle and the command that reaches it. No routing was invented and no lifecycle lost its
documentation or verification phase.

`/investigate` did not exist as a command contract, which left the active `investigate` workflow
unreachable even though `agents/planner/manifest.yaml` and `agents/architect/manifest.yaml`
declare it in `supportedWorkflows`. `commands/investigate.md` was authored and records its
relationship to `/research` explicitly.

Nine command contracts exist and nine carry records. The seven files under
`commands/<domain>/<name>.md` are grouped runbooks, not contracts; `commands/README.md` now
states that distinction and what it would take for a runbook to become an entry point.

## 5. Phase Model Coverage

36 canonical phase identifiers across 7 active workflows, all parsed by
`framework_runtime.parse_phase_model`.

| Workflow | Phases | Identifiers |
|---|---|---|
| `implement-feature` | 6 | unchanged from the proven slice |
| `fix-bug` | 5 | `triage-and-impact`, `root-cause-analysis`, `fix-implementation`, `regression-validation`, `closure-and-communication` |
| `refactor` | 5 | `scope-invariants-and-risk-profile`, `safety-net-establishment`, `refactor-implementation`, `behavioral-validation`, `closure-and-debt-record` |
| `investigate` | 5 | `problem-framing`, `technical-discovery`, `option-analysis`, `recommendation`, `publication` |
| `research` | 5 | `research-framing`, `technical-validation`, `option-synthesis`, `recommendation-draft`, `findings-publication` |
| `review-pull-request` | 5 | `code-quality-review`, `structural-compliance`, `test-risk-validation`, `documentation-impact`, `merge-decision` |
| `release` | 5 | `readiness-assessment`, `artifact-packaging`, `candidate-validation`, `deployment-execution`, `communication-and-post-release` |

Identifiers were not invented where an authority already published one. Five come from agent
manifests: `scope-invariants-and-risk-profile`, `technical-discovery`, `structural-compliance`,
and `readiness-assessment` from `agents/architect/manifest.yaml`, and `problem-framing` from
`agents/planner/manifest.yaml`. The rest are derived from the state names in
`workflows/workflow-engine.md`, which is the state-machine form of the same workflows, and each
workflow's Phase Identifier Sources table records which rule produced which identifier.

`skills/agent-skill-matrix.md` now carries the canonical identifier for every phase of every
active workflow, including two phases its earlier coarser groupings had folded away
(`safety-net-establishment`, `candidate-validation`) and the split between deciding and
publishing in `investigate` and `research`. No skill requirement was dropped.

## 6. Phase Owner Invocability

| Agent | Phases owned | Entry point | Registry record |
|---|---|---|---|
| `omn-tech-lead` | 6 | `agents/omn-tech-lead.agent.md` | pending |
| `omn-documentation` | 5 | `agents/omn-documentation.agent.md` | pending |
| `omn-qa` | 5 | `agents/omn-qa.agent.md` | pending |
| `architect` | 3 | `agents/architect.agent.md` | present |
| `omn-dev-1-implement` | 3 | `agents/omn-dev-1-implement.agent.md` | pending |
| `omn-dev-2-reviewer` | 3 | `agents/omn-dev-2-reviewer.agent.md` | pending |
| `omn-orchestrator` | 3 | `agents/omn-orchestrator.agent.md` | pending |
| `omn-business-analyst` | 2 | `agents/omn-business-analyst.agent.md` | pending |
| `omn-context-agent` | 2 | `agents/omn-context-agent.agent.md` | pending |
| `omn-dev-1-bug-analyst` | 2 | `agents/omn-dev-1-bug-analyst.agent.md` | pending |
| `omn-product-owner` | 1 | `agents/omn-product-owner.agent.md` | pending |
| `planner` | 1 | `agents/planner.agent.md` | present |

Each of the ten new entry points is an adapter, not a contract. It loads the single-file role
specification plus `agents/agent-contract.md` and `agents/agent-lifecycle.md`, reproduces the
phases the workflow Phase Models assign it, states its gate position under the Producer
Exclusion Rule, names its boundaries from its own specification's Constraints, and closes with a
Registration status table naming exactly what is still missing. None restates role behavior.

One defect was found and fixed while writing them: a bare `: ` inside an unquoted frontmatter
`description` makes the YAML unparseable, and the host reads that frontmatter to register the
subagent. `agents/README.md` now records the constraint along with the two registration layers.

## 7. Dispatchability, Reported Honestly

3 of 36 phases resolve the full `G1-CAPABILITY` and `G2-CONTEXT` chain:

| Command | Workflow | Phase | Owner |
|---|---|---|---|
| `/implement` | `implement-feature` | `execution-planning` | `planner` |
| `/implement` | `implement-feature` | `solution-design-and-risk-assessment` | `architect` |
| `/refactor` | `refactor` | `scope-invariants-and-risk-profile` | `architect` |

The third is new in this increment. It required two runtime changes, both small and both
verified: the frozen context slice now adds the routed workflow's own specification instead of
naming `workflows/implement-feature.md` for every run, and a context slice is declared for
`scope-invariants-and-risk-profile`. Proof:

```bash
python .claude/runtime/framework_runtime.py resolve --command refactor --phase scope-invariants-and-risk-profile
```

returns `RESOLVED` with the architect module set, both skill sets, the output contract, and
`design_validator.py`.

The remaining 33 phases block for two reasons, each with a recorded code:

| Blocked reason | Failure class | Count |
|---|---|---|
| `awaiting_capability_registration` | `missing-capability-failure` | 32 |
| `awaiting_contract_reconciliation` | `workflow-contract-violation` | 1 |

The 32 are phases whose owner is host-invocable but holds no record in `registry/agents.yaml`.
The runtime says so precisely, for example:

```
RUNTIME FAILURE [missing-capability-failure] agent 'omn-qa' has no record in registry/agents.yaml
```

The one contract violation is `review-pull-request/structural-compliance`: `architect` is
registered and host-invocable, but the artifact that phase asks of it, a structural and security
findings assessment, is not declared in its manifest `outputs` and no validator covers it.
Closing that needs either an architect contract change or a review-package validator, both
Phase 4 work.

## 8. Gate Resolvability

28 gate references across the 36 phases, every one resolving to owners in
`workflows/workflow-gate-matrix.md` with at least one owner permitted to decide.

Twelve gate rows were added and three existing rows were completed with a second owner. The
additions are gates a workflow specification already named but the matrix did not carry. The
completions were latent deadlocks: a gate whose only listed owner is the role that produces the
evidence it assesses can never be decided, because the Producer Exclusion Rule forbids
self-approval. That applied to the `implement-feature` Review Gate, the `fix-bug` Verification
Gate, and the `release` Deployment Gate. Three of the newly added `review-pull-request` rows and
the new `release` Artifact Gate row carry a second owner for the same reason. The matrix records
every change with its reason.

One row was retired: `review-pull-request | Readiness Gate | omn-dev-2-reviewer`. Review
readiness is an entry condition of that workflow, not a gate between two of its phases, and no
Phase Model row referenced it.

## 9. Skill Resolution

101 phase-mandatory skill references, all resolving to active records.

S10 (`skills/git/git-collaboration.md`) was registered as `git-collaboration`. It qualifies under
the second ground `skills/agent-skill-matrix.md` already states: a routed workflow phase declares
it mandatory. Eleven routed phases do, across implementation, closure, and release
communication. Registration records identity metadata only, so no agent's resolved skill bundle
changed.

S04 and S05 remain unregistered, and the matrix now says why: no phase the runtime routes
declares either as mandatory.

## 10. No Regression in Proven Evidence

This increment edited files inside the frozen context slice of already-committed runs, so the
prior evidence was re-verified rather than assumed:

```bash
python .claude/runtime/verify_multi_phase.py --run-id run-c5a8d50d3238      # 15/15 PROVEN
python .claude/runtime/verify_vertical_slice.py --run-id run-c5a8d50d3238   # 10/10 PROVEN
python .claude/runtime/verify_vertical_slice.py --run-id run-308f4d0ee447   # 10/10 PROVEN
python .claude/runtime/verify_vertical_slice.py --run-id run-b6780677468b   # 10/10 PROVEN
```

All four pass, including M14, which re-executes runtime commands against the committed run and
proves the fingerprint unchanged, and M11, which proves every blocked item still records a reason
and an escalation.

Note for reproduction on Windows: `verify_multi_phase.py` builds its illegal-transition probe in
the system temp directory, which a sandboxed shell may refuse to overwrite. Run it in a shell
allowed to write there.

## 11. Deferred Items, Recorded Not Hidden

| Item | Why deferred |
|---|---|
| Agent registry records, module sets, and validators for the ten host-invocable agents | Each is a contract-authoring increment of the size of `agents/planner/` or `agents/architect/`, and Phase 4 owns validator coverage. Until then their phases block with a recorded reason |
| `agents/planner/manifest.yaml` declares `scope-and-invariants` for `refactor`, but the owning agent declares `scope-invariants-and-risk-profile` | The runtime resolves the owner, so the mismatch blocks nothing. Correcting it changes a version-pinned contract and would alter digests recorded in committed run evidence, so it belongs in a contract increment |
| `architect` owns one phase per workflow, so `option-analysis` and `option-synthesis` are owned by `omn-tech-lead` with architect support | Elevating architect to a second phase per workflow requires a manifest change. The two workflow specifications record the reassignment and its reason |
| `workflows/workflow-engine.md` names `omn-tech-lead` as owner of the refactor scope state and the architecture role as owner of two analysis states | The Phase Models follow the manifests and registry, which are the machine authorities, and each records the divergence. Rewriting the state tables is Phase 0 reconciliation work |
| `registry/commands.yaml` has no field for a command's owning phase set | `/document` and `/test` are phase-scoped, and that scoping is currently prose in the specification and the catalog. Adding a field means a schema change with `requireAllFields` implications for every record |
| Seven grouped runbooks under `commands/<domain>/` carry no records | Registering them would duplicate the routing a contract already owns. The decision to promote or retire each is open |
| `workflows/implement-feature.md` Phase Model unchanged | Its six phases were already canonical. Only the Approval Gates prose changed, to name the two gates the matrix owns instead of a `Quality Gate` that never existed there |

## 12. Weekly Maturity Metrics

Against section 7 of the self-hosting execution plan:

| Metric | Before | After |
|---|---|---|
| Invocable agents / phase-owning agents | 2 / 12 | 12 / 12 |
| Registered commands / command contracts | 1 / 8 | 9 / 9 |
| Workflows with Phase Model / active workflows | 1 / 3 | 7 / 7 |
| Resolved required skills / total required skills | 18 / 20 | 101 / 101 |
| Dispatchable phases / declared phases | 2 / 6 | 3 / 36 |

The dispatchable ratio falls because the denominator grew from one workflow's phases to seven
workflows' phases. That is the intended shape of this increment: it registers the surface and
makes every blocker explicit and reasoned. Raising the numerator is the next increment's work.
