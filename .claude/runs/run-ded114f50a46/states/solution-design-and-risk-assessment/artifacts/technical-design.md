```yaml
design:
  designId: DES-run-ded114f50a46-model-tier
  changeReference: runs/inputs/model-tier-change-request.md
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/model-tier-feature-request.md
    - type: change-request
      reference: runs/inputs/model-tier-change-request.md
    - type: business-intent
      reference: runs/inputs/model-tier-business-intent.md
    - type: architecture-context
      reference: runs/inputs/model-tier-architecture-context.md
    - type: execution-plan
      reference: runs/run-ded114f50a46/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002]
  consumesPlan: runs/run-ded114f50a46/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:040b2777c92658f6406de4d87a19c7a7
  contextDigest: sha256:0cf589d87741618e90104e90710f8162
```

## Metadata

- Feature or Change ID: run-ded114f50a46, per-phase model tier in the dispatch envelope
- Author: architect
- Reviewers: omn-tech-lead (Design Gate owner who accepts the records), omn-qa
- Last Updated: 2026-10-08

## Objective

- Desired outcome: one authoritative data carrier assigns a tier to every workflow phase; dispatch resolves the tier from that carrier and from recorded run state, carries it in one additive envelope record, promotes it after a recorded rejection, and reports per-tier figures, with no model call and no change to any gate, validator, or contract.
- Architectural objectives:
  - One data carrier, keyed by workflow and phase and separate from the Phase Model tables and from agent text, holds every tier assignment and one host hint per tier (S-001, S-004).
  - Tier resolution is a pure derivation from that carrier plus recorded run state, so an in-session dispatch and a fresh-session dispatch agree (S-002, S-003).
  - The invocation envelope boundary gains one additive record and the original fields keep name and value (S-002, S-004).
  - Per-tier accounting derives from the event stream and envelopes the runtime already persists (S-005).
  - Declaration coverage and escalation monotonicity are checkable at the existing registry-coverage verification surface (S-006).
  - The distributed copy equals the authoritative tree, the version value identifies the change, and the rules are stated in the runtime governance documents (S-007, S-008, S-009).
- In scope:
  - The tier declaration file, the resolver and loader in the runtime, the envelope record, the event detail, and the dispatch prompt line (S-001, S-002, S-003, S-004).
  - Per-tier execution metrics, two verification checks, governance documentation, version increment, and mirror refresh (S-005, S-006, S-007, S-008, S-009).
- Out of scope:
  - X-001: concurrent phase execution, a separate later change.
  - X-002: model identifiers in runtime logic, any model call, any vendor dependency.
  - X-003 and X-005: agent module text, entrypoint model declarations, Phase Model tables, the gate matrix, validators, templates, artifact contracts.
  - X-004: which phases exist, who owns them, and what they produce.
  - X-006: lowering a tier after success or adaptive tiering.
  - An operator switch to disable or override a tier for one dispatch: no statement requires it, so it is raised as Q-004 and not designed.

## Requirements Summary

- Functional requirements:
  - S-001: each phase of every active workflow has exactly one declared tier of light, standard, or deep, and each tier has one host hint, stated once outside agent text.
  - S-002: every dispatch envelope carries an additive tier record stating resolved tier, host hint, and basis.
  - S-003: a phase whose prior attempt was rejected by its validator, or whose gate was rejected and rolled back, resolves one tier higher on its next attempt, with the reason recorded; deep never rises and no tier is lowered.
  - S-004: a phase with no declaration inherits the host model, and no existing run, replay, or verifier changes outcome.
  - S-005: execution metrics report invocations and estimated context bytes by tier, and the non-deep share.
  - S-006: framework verification fails on a phase with no declared tier and on an escalation that does not rise.
  - S-007: the distributed copy carries the same tier behaviour as the authoritative copy.
  - S-008: the envelope field and the escalation rule are stated in the runtime governance documentation.
  - S-009: the runtime version value increments.
- Non-functional requirements:
  - Additivity and determinism: the tier record is deterministic from run state and replay-stable, and original envelope fields are unchanged (S-002, S-004).
  - Model independence: the runtime names a tier and a hint, never calls a model, and adds no vendor dependency (S-002).
  - Auditability: a promotion records its reason and a rejected cheaper attempt is never retried at the same tier (S-003).
  - Cost visibility: per-tier figures sum to the run totals (S-005).
  - Success bar supplied by the operator: at least 3 of the 6 implement-feature phases resolve to a non-deep tier (S-001, S-005).
- Acceptance criteria:
  - Plan acceptance criterion 1: zero uncovered phases and at least 3 of 6 implement-feature phases non-deep (S-001, S-005; UAC-001, UAC-002, UAC-016).
  - Plan acceptance criterion 2: metrics list invocations and bytes per tier summing to the run totals (S-005; UAC-015).
  - Plan acceptance criterion 3: one-tier promotion with a stated reason, deep stays deep, identical across sessions (S-003; UAC-008 to UAC-012).
  - Plan acceptance criterion 4: every existing verifier at its recorded baseline and an undeclared phase inherits (S-004; UAC-013, UAC-014).
  - Plan acceptance criterion 5: every envelope of an implement-feature run carries a complete tier record with original fields unchanged (S-002; UAC-005, UAC-006).
  - Plan acceptance criterion 6: zero model invocations, zero vendor dependencies, zero tier assignments in agent text (S-002; UAC-004, UAC-007).
  - Plan acceptance criterion 7: four documented items, version value rises, mirror differs in zero files (S-007, S-008, S-009; UAC-019 to UAC-021).

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | All twelve agent entrypoints declare `model: inherit` and the invocation envelope has no model field | feature-request input, Request section; agents/*.agent.md frontmatter |
| F-002 | Envelope fields added since 0.7.0 are additive: a consumer reading only the original eleven fields reads them unchanged | architecture-context input; config/execution-engine.md, Agent Invocation Envelope |
| F-003 | The runtime core never invokes a model; it builds the envelope and hands it to an adapter, so a tier is advice carried in the envelope | architecture-context input; runtime/framework_runtime.py header and cmd_dispatch |
| F-004 | Phase Model tables are machine-parsed by section heading and header-keyed columns; the 8 active workflows publish 37 phases, 6 of them in implement-feature | runtime/framework_runtime.py parse_phase_model; workflows/*.md; architecture-context input |
| F-005 | One agent owns phases of unlike weight: omn-dev-2-reviewer owns quality-review and artifact-packaging, omn-documentation owns five phases across five workflows | Phase Model tables of the eight workflow specifications |
| F-006 | load_gate_policy is the precedent for a runtime-read JSON file under config/: an absent file keeps prior behaviour and an unreadable file is a policy failure; the installer syncs config/ as a managed directory | runtime/framework_runtime.py load_gate_policy; config/gate-policy.md; omn_agent/source.py MANAGED_DIRS |
| F-007 | Registry workflow records reject unknown fields, and registry/workflows.yaml is a member of every phase's frozen context slice | registry/workflows.yaml automation.validation; invocation envelope context_slice.members |
| F-008 | The recovery ledger is append-only per run, one entry per classified failure carrying state_id, failure_class, and reason_code; resolved entries stay in place | runtime/recovery_policy.py RecoveryLedger; runtime/framework_runtime.py emit_failure_envelope |
| F-009 | A validator rejection is ledgered under the phase's state_id with reason code validation_failed; a missing artifact is ledgered as an uncharged transport failure with a different reason code | runtime/framework_runtime.py cmd_complete; runtime/recovery_policy.py FAILURE_POLICIES |
| F-010 | An authorised rollback appends the superseded attempt to the append-only supersessions list of the phase's work item, and a gate rejection is ledgered under the gate's own state_id | runtime/state_engine.py header; runtime/framework_runtime.py record_gate_decision |
| F-011 | Every dispatch appends an invocation_started event for the phase to the append-only event stream, and execution metrics count invocations from it | runtime/framework_runtime.py cmd_dispatch; runtime/execution_metrics.py compute |
| F-012 | The per-phase invocation envelope is rewritten at each dispatch, a rollback re-entry snapshots the prior attempt, and metrics derive each phase's context estimate from the current envelope | runtime/framework_runtime.py cmd_dispatch and snapshot_attempt; runtime/execution_metrics.py |
| F-013 | The registry coverage verifier iterates every workflow and phase row of the active Phase Models and is the mandatory FR-01 item of the framework release checklist | runtime/verify_registry_coverage.py; validation/framework-release-checklist.md |
| F-014 | The runtime version value is 0.8.0, and 0.7.0 and 0.8.0 each added fields additively | runtime/framework_runtime.py RUNTIME_VERSION; config/execution-engine.md |
| F-015 | runtime/README.md is 61682 bytes and a frozen context member read by agents, while config/runtime.md already documents Execution Metrics and loading policy | invocation envelope context_slice.members; config/runtime.md; architecture-context input |
| F-016 | The authoritative tree is edited first and omn_agent/_bundled_payload/ is a mirror refreshed by the payload synchronisation command of tests/test_bundled_payload.py; package-data globs cover every bundled file | architecture-context input; tests/test_bundled_payload.py; pyproject.toml |
| F-017 | The host accepts a per-dispatch model override on subagent invocation, which is how a tier hint becomes effective; entrypoint frontmatter stays inherit | architecture-context input |
| F-018 | The dispatch prompt and the dispatch console output are the surfaces by which the dispatching session learns the routing of a dispatch | runtime/framework_runtime.py build_dispatch_prompt and cmd_dispatch |
| F-019 | The tests/ directory carries runtime-behaviour tests including tests/test_gate_policy.py and tests/test_lean_dispatch.py | tests/ directory listing |
| F-020 | Dispatch derives a payload digest from the context digest, input digest, agent version, and canonical artifact path, and a changed payload under an active lease is a context-integrity failure | runtime/framework_runtime.py cmd_dispatch |
| F-021 | Artifact validators are keyed by artifact type, not by phase or tier | runtime/framework_runtime.py VALIDATORS |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The dispatching session reads the tier record or the prompt line and passes the hint as the per-dispatch override; the runtime cannot observe it | Only this step makes a tier effective, since the runtime never calls a model | The hint is advisory, cost does not fall, and metrics count declared tiers rather than models run | omn-tech-lead |
| A-002 | The success bar of at least 3 of 6 implement-feature phases non-deep, supplied by the operator, stands as the acceptance measure | The scope artifact left the minimum share open, and the mapping decision D-003 is sized to it | The tier of the planning phase and of other phases in D-003 changes | omn-business-analyst |
| A-003 | The host accepts one cheaper hint value and one strongest hint value that the implementer can name in the declaration | The declaration needs two concrete values besides the reserved inherit value | The light or deep tier has no effective hint and falls back to inherit behaviour | omn-tech-lead |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | A tier is declared per workflow and phase, once, in one location outside agent text | hard | feature-request input constraints; scope exclusion X-003 |
| C-002 | structural | Phase Model tables and the gate matrix keep their parsed shape; no column is added | hard | feature-request input; architecture-context input |
| C-003 | structural | The runtime names a tier and a hint; it never calls a model, embeds a model identifier in logic, or adds a vendor dependency | hard | business-intent input non-goals; feature-request input; exclusion X-002 |
| C-004 | migration | The envelope change is additive: original fields keep name and value, and the new record is deterministic from run state | hard | architecture-context input; feature-request input |
| C-005 | migration | A phase with no declaration inherits the host model, and no existing run, replay, or verifier changes outcome | hard | feature-request input expected outcome; statement S-004 |
| C-006 | functional | Escalation is promotion-only, capped at deep, derived from recorded state, and identical in-session and from recorded state alone | hard | feature-request input; architecture-context input; statement S-003 |
| C-007 | structural | Agent module text, entrypoint declarations, validators, templates, and artifact contracts are unchanged | hard | change-request input Not touched; exclusions X-003 and X-005 |
| C-008 | quality-attribute | At least 3 of the 6 implement-feature phases resolve to a non-deep tier | hard | operator resolution recorded in the execution plan assumptions |
| C-009 | operability | Documentation goes to config/runtime.md and config/execution-engine.md, and runtime/README.md is not enlarged | negotiable | architecture-context input; statement S-008 |
| C-010 | migration | The authoritative tree is edited first and the distributed copy is refreshed only by the payload synchronisation command | hard | architecture-context input; change-request input |
| C-011 | quality-attribute | Artifacts written by write_run_ledger stay stable when content is unchanged | hard | architecture-context input, replay check |
| C-012 | functional | Execution metrics report invocations and estimated context bytes by tier, and the per-tier values sum to the run totals | hard | feature-request input; statement S-005 |
| C-013 | compliance | A tier is advice: no gate, validator, or acceptance rule is weakened and correctness stays decided mechanically | hard | business-intent input success criteria |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | runtime/framework_runtime.py | contract-change | F-002, F-003, F-011, F-012, F-018 | invocation envelope (new model_tier record), invocation_started event detail, dispatch prompt header, dispatch console output | confirmed |
| M-002 | config/model-tier-policy.json (new file) | extension | F-004, F-005, F-006 | declaration read by M-001 and M-004 | confirmed |
| M-003 | runtime/execution_metrics.py | contract-change | F-011, F-012 | execution-metrics document, additive per-tier keys | confirmed |
| M-004 | runtime/verify_registry_coverage.py | extension | F-013 | verifier report, two added checks | confirmed |
| M-005 | config/runtime.md | extension | F-015 | one new governance section | confirmed |
| M-006 | config/execution-engine.md | extension | F-002 | Agent Invocation Envelope section, one field line | confirmed |
| M-007 | omn_agent/_bundled_payload/ | extension | F-016 | bundled mirror of the authoritative tree | confirmed |
| M-008 | tests/ (new model-tier test file beside tests/test_gate_policy.py) | extension | F-019 | test suite | confirmed |
| M-009 | runtime/recovery_policy.py | no-change-verified | F-008, F-009 | recovery ledger, read only | confirmed |
| M-010 | runtime/state_engine.py | no-change-verified | F-010 | supersessions list, read only | confirmed |
| M-011 | workflows/ Phase Model tables of the eight workflow specifications and workflows/workflow-gate-matrix.md | no-change-verified | F-004 | none | confirmed |
| M-012 | registry/workflows.yaml | no-change-verified | F-007, F-020 | none | confirmed |
| M-013 | agents/*.agent.md entrypoints and agents/ module sets | no-change-verified | F-001, F-017 | none | confirmed |
| M-014 | runtime/README.md | no-change-verified | F-015 | none | confirmed |
| M-015 | runtime/ artifact validators, including runtime/design_validator.py | no-change-verified | F-021 | none | confirmed |

### 5.2 Options Considered

| Option | Structural change | Hard constraints | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|
| O-001 | Shipped data file under config/ keyed by workflow and phase plus one hint per tier; loader and pure resolver beside load_gate_policy; additive envelope record; escalation from ledger and supersessions; per-tier metrics from events; two checks in the coverage verifier | Satisfies C-001 to C-013 | 2 (M-001 and M-003 contract-change) | 11 capabilities reused | Deterministic from run state, verifiable, replay-stable (C-004, C-006, C-011) | 2 additive contract changes, no schema transition | Absent file inherits, malformed file fails dispatch loudly, one file to maintain | Selected |
| O-002 | Tier column added to each Phase Model table and read by the Task Router | Violates C-002 | Not scored (C-002 applies) | Not scored (C-002 applies) | Not scored (C-002 applies) | Not scored (C-002 applies) | Not scored (C-002 applies) | Eliminated by C-002 |
| O-003 | Tier field added to workflow records in registry/workflows.yaml and read by the Task Router | Satisfies C-001 to C-013 after a registry schema change | 3 (M-001, M-003, and the registry record schema of M-012 under this option) | 11 capabilities reused | Deterministic, but every tier edit changes the context digest of every later slice (F-007, F-020) | 3 contract changes, the registry schema needing a transition | Tier edits need a registry schema and version change | Not selected, ranked second |
| O-004 | Tier declared in each agent manifest or entrypoint, keyed by agent | Violates C-001 and C-007 | Not scored (C-001, C-007 apply) | Not scored (C-001, C-007 apply) | Not scored (C-001, C-007 apply) | Not scored (C-001, C-007 apply) | Not scored (C-001, C-007 apply) | Eliminated by C-001 and C-007 |
| O-005 | Declaration carries abstract tier labels and a label-to-alias table sits in runtime code | Violates C-003 | Not scored (C-003 applies) | Not scored (C-003 applies) | Not scored (C-003 applies) | Not scored (C-003 applies) | Not scored (C-003 applies) | Eliminated by C-003 |
| O-006 | Escalation counted by in-memory attempt counters of the dispatching session | Violates C-006 | Not scored (C-006 applies) | Not scored (C-006 applies) | Not scored (C-006 applies) | Not scored (C-006 applies) | Not scored (C-006 applies) | Eliminated by C-006 |

### 5.3 Selected Approach

- Selected: O-001
- Structural change: one shipped declaration file (M-002) is read by the runtime (M-001) at dispatch. A pure resolver turns declared tier plus recorded rejections into a resolved tier, a hint, and a basis, and writes them as one additive record in the envelope and as a detail on the invocation_started event. Metrics (M-003) group invocations and bytes by that tier, and the coverage verifier (M-004) checks coverage and monotonicity.
- Rationale: it is the only viable option with the smallest impact surface (2 against 3 for O-003), it reuses the optional-file loader precedent, the recovery ledger, the supersessions list, the event stream, and the existing verifier (see the reuse section), and it keeps the Phase Model tables, registry schema, agent text, and validators untouched (C-001, C-002, C-005, C-007).
- Highest-scoring rejected alternative and why it lost: O-003 ranks second; it satisfies the hard constraints but adds a third contract change to the workflow registry schema and changes the context digest of every later phase slice whenever a tier is edited (F-007, F-020), so it lost at the impact-surface criterion.
- Tradeoffs accepted:
  - A new data file is introduced, because no existing carrier holds phase-keyed data outside the parsed tables (see the reuse section).
  - Host hint strings live in configuration data, so changing the host's accepted values means editing that file, not runtime logic (C-003).
  - A hint is effective only if the dispatching session passes it on (A-001), so the runtime proves what it advised, not what ran.
  - Execution planning is placed at standard, leaving exactly 3 of 6 implement-feature phases non-deep, with no margin for a first-attempt rejection of a standard phase (R-001).

#### Answers to the plan's two open questions

- Form of the host model hint (D-001): an opaque host alias string held in the declaration, one per tier. The standard tier carries the reserved value inherit, meaning no override is passed. The light and deep tiers carry the two alias values the host accepts, named by the implementer from the host's accepted set (A-003). The runtime copies a hint verbatim and never branches on its value.
- Phase-to-tier mapping (D-003): the mapping table after the decisions table below.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Carry tier data in one shipped data file under config/, keyed by workflow and phase, with one opaque host hint per tier and the reserved inherit value for standard; load it by the optional-file pattern; an absent file or absent phase entry resolves to standard with inherit; a malformed file fails dispatch as a policy failure; selects O-001 and constrains T-001, T-002, T-003, T-006 | Yes | architecture-decision-record-D-001.md |
| D-002 | Resolve the tier at dispatch as a pure derivation from the declaration and recorded run state: one tier of promotion per recorded rejection, counting validator rejections ledgered under the phase and gate-rejection rollbacks recorded as supersessions, capped at deep; write the result as an additive model_tier record carrying tier, host hint, basis, and escalation with its reason, and as an event detail, and show it in the dispatch prompt and console output; selects O-001 and constrains T-006, T-008, T-009 | Yes | architecture-decision-record-D-002.md |
| D-003 | Assign tiers by work kind: light for read-and-summarise and template-fill phases, standard for bounded-judgement analysis and validation, deep for structural design, root cause, implementation, and review judgement; the request's named categories resolve as in the mapping below; selects O-001 and constrains T-002, T-003, T-004 | No | none; recorded inline |
| D-004 | Metrics add a by-tier table of invocations counted from invocation_started events and estimated bytes taken from each phase's latest envelope, a bucket named untiered for records that predate the field, and the non-deep share of tiered invocations; selects O-001 and constrains T-010 | No | none; recorded inline |
| D-005 | Add two checks to the existing coverage verifier (declaration coverage including the 3-of-6 bar and the request's named categories, and escalation monotonicity over every tier and rejection count), document the field and rule in config/runtime.md and config/execution-engine.md, raise the version value as a minor increment, and refresh the mirror last; selects O-001 and constrains T-011, T-012, T-013, T-014 | No | none; recorded inline |

### Phase-to-Tier Mapping

| Workflow | light | standard | deep |
|---|---|---|---|
| code-quality-scan | `repository-quality-scan` | none | none |
| fix-bug | `closure-and-communication` | `triage-and-impact`, `regression-validation` | `root-cause-analysis`, `fix-implementation` |
| implement-feature | `scope-and-acceptance`, `documentation-and-release-handoff` | `execution-planning` | `solution-design-and-risk-assessment`, `implementation`, `quality-review` |
| investigate | `problem-framing`, `technical-discovery`, `publication` | `option-analysis`, `recommendation` | none |
| refactor | `closure-and-debt-record` | `safety-net-establishment`, `behavioral-validation` | `scope-invariants-and-risk-profile`, `refactor-implementation` |
| release | `artifact-packaging`, `communication-and-post-release` | `readiness-assessment`, `candidate-validation`, `deployment-execution` | none |
| research | `research-framing`, `technical-validation`, `findings-publication` | `option-synthesis`, `recommendation-draft` | none |
| review-pull-request | `documentation-impact` | `test-risk-validation`, `merge-decision` | `code-quality-review`, `structural-compliance` |

Mapping rules, applied in order so the table is reproducible:

- The request's named light categories resolve as scope definition to scope-and-acceptance, technical discovery to technical-discovery, documentation hand-off to documentation-and-release-handoff, artifact packaging to artifact-packaging, and repository scan to repository-quality-scan.
- The request's named deep categories resolve as solution design to solution-design-and-risk-assessment, root-cause analysis to root-cause-analysis, implementation to implementation, and quality review to quality-review.
- An unnamed phase takes the tier of the named phase it matches by artifact and work kind: technical-validation follows technical-discovery, fix-implementation and refactor-implementation follow implementation, code-quality-review follows quality-review, and scope-invariants-and-risk-profile and structural-compliance follow solution design.
- Every remaining phase is standard when it analyses or validates, and light when it frames, publishes, or packages a closure record.
- Result: 14 light, 14 standard, 9 deep, 37 in total. implement-feature resolves 2 light, 1 standard, 3 deep, so 3 of its 6 phases are non-deep (C-008). Moving execution-planning to light is the only lever that adds margin (Q-001).

## API and Data Model Impact

- API changes:
  - M-001: the invocation envelope gains one top-level record named model_tier with tier, host hint, basis, and escalation (empty when none); the invocation_started event gains the resolved tier and an escalated flag as detail; the dispatch prompt header and console output gain one line stating tier and hint.
  - M-003: the execution-metrics document gains additive keys for per-tier invocations, per-tier estimated bytes, and the non-deep share.
  - M-002: a new declaration file read by M-001 and M-004; it is read, never written, by the runtime.
- Contract compatibility notes:
  - M-001, current shape: an envelope of the original fields plus those added by 0.7.0 and 0.8.0; target shape: the same fields plus model_tier. Compatibility approach: additive field, no existing field renamed or retyped, so a consumer reading the original eleven fields is unaffected (F-002, C-004). Coexistence period: indefinite, because envelopes written before the change simply lack the record. Retirement condition: none, the record is permanent. Rollback position: remove the field and the resolver call and delete M-002; every phase then inherits as before.
  - M-003, current shape: a document of schema v1 with the keys it carries today; target shape: the same document plus the by-tier keys. Compatibility approach: additive keys inside the same schema version, with a bucket named untiered for envelopes and events that predate the record so sums hold. Coexistence period: indefinite for historical runs. Retirement condition: none. Rollback position: drop the added keys; historical documents are unchanged.
  - Transition behaviour for readers: a reader that ignores unknown keys is unaffected, and the reversal path for both modules is deletion of the additions with no data to restore.
- Schema or migration changes: None identified. No persisted run data is rewritten and M-002 is a new file, so migration direction is not applicable and reversal is complete by removing the file and the added keys.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Phase-keyed tier declaration carrier | Workflow Phase Model tables | rejected | The tables are machine-parsed and a column would change a parsed contract (C-002, F-004) |
| Phase-keyed tier declaration carrier | registry/workflows.yaml workflow records | rejected | Records reject unknown fields and the file digest enters every slice, so each edit changes later context digests (F-007, F-020) |
| Phase-keyed tier declaration carrier | Agent manifests and entrypoints | rejected | They are keyed by agent while one agent owns phases of unlike weight (F-005), and tier text must stay out of agent text (C-001, C-007) |
| Phase-keyed tier declaration carrier | config/gate-policy.json | rejected | It is a team-authored optional file holding gate modes and is not shipped, so a framework-owned declaration must not share it (F-006) |
| Phase-keyed tier declaration carrier | Any existing carrier of phase-keyed data | none-found | Searched existing components (config, registry, workflows, agents), the standard library, native host capability, and installed dependencies; none holds phase-keyed tier data |
| Optional data file loading with a policy failure on invalid content | load_gate_policy in runtime/framework_runtime.py | reuse-extended | The same pattern applies to a second file: absent keeps prior behaviour, invalid fails loudly (F-006) |
| Tier resolution and escalation derivation | runtime/framework_runtime.py dispatch path | reuse-extended | Resolver and loader sit beside load_gate_policy, so no new module is introduced |
| Tier resolution and escalation derivation | runtime/recovery_policy.py | rejected | It classifies failures into recovery actions; tier advice is a dispatch concern, so the module is read here and not extended (F-008) |
| Validator-rejection history | RecoveryLedger entries read from runtime/recovery_policy.py | reuse-as-is | Entries already carry state_id and reason code, and resolved entries are never pruned (F-008, F-009) |
| Gate-rejection-with-rollback history | supersessions list in runtime/state_engine.py | reuse-as-is | Each authorised rollback already appends one append-only record per superseded attempt (F-010) |
| Per-tier invocation counts | invocation_started events | reuse-extended | The event already exists per dispatch and metrics already count it; one detail is added (F-011) |
| Per-tier estimated context bytes | Per-phase context estimate in runtime/execution_metrics.py | reuse-extended | The estimate exists per phase; it is grouped by the tier of the phase's latest envelope (F-012) |
| Declaration coverage and monotonicity verification | runtime/verify_registry_coverage.py | reuse-extended | It already iterates every workflow and phase row and is the mandatory FR-01 item (F-013) |
| Surfacing the hint to the dispatching session | Dispatch prompt and console output | reuse-extended | They already name routing for each dispatch; one line is added (F-018) |
| Applying the hint to the invoked agent | Host per-dispatch model override | reuse-as-is | The host provides the override natively, so the runtime builds no adapter of its own (F-017, C-003) |
| Governance documentation | config/runtime.md and config/execution-engine.md | reuse-extended | They already document the envelope and metrics; a section and a field line are added (C-009) |
| Governance documentation | runtime/README.md | rejected | At 61682 bytes it is read by agents, and growing it adds cost to every run (F-015, C-009) |
| Distributed copy refresh | Payload synchronisation command of tests/test_bundled_payload.py | reuse-as-is | The mirror is refreshed by that command alone (F-016, C-010) |

## Operational Considerations

- Logging and observability updates: the invocation_started event carries the resolved tier and escalated flag, the envelope carries the full record with its basis and reason, and metrics report per-tier figures (M-001, M-003, C-012).
- Error handling strategy: a missing file or a phase with no entry resolves to standard with inherit and is not an error (C-005). A file that exists but is unreadable, names an unknown tier, or lacks a hint fails dispatch as a policy failure, so a team that wrote a declaration never gets a silent fallback (M-002, F-006). A transport failure that produced nothing to judge never escalates, because only judged rejections carry a capability signal (F-009, C-006).
- Security considerations: assessed against M-002 and M-001. The declaration holds alias strings only, no credential and no secret, and a tier changes which reader handles a phase but not which checks decide it, so no gate, validator, or acceptance rule is weakened (C-013). The residual exposure is a wrong or tampered declaration routing a deep phase to a cheaper tier; mechanical validation and gate decisions still bound the effect, and the change set review covers the file (R-009).
- Performance considerations: this is the objective of the change. Cost is advised downward per phase while the context bytes read per dispatch are unchanged, so the saving rests on the hint being applied (A-001, C-008). Resolution reads one small file and one ledger per dispatch, which is negligible against a dispatch (M-001).
- Deployment and operability impact: no migration and no new dependency. The declaration ships in the managed config directory, so installed copies receive it by the normal update (F-006, C-010).

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The declaration structure, hint form, and phase-to-tier assignments are fixed and the file exists before any consumer is written | M-002 | none | Contract definition precedes every consumer change, and the resolver, verifier, and metrics all read this contract | T-001, T-002, T-003 |
| P-002 | The escalation rule, naming the recorded state read for each rejection kind, the deep ceiling, and the reason format, is fixed before the resolver is extended | M-009, M-010 | none | The rule is the contract the escalation behaviour and its check bind to | T-008 |
| P-003 | Tier resolution and the additive model_tier record exist in the runtime before escalation, metrics, or documentation depend on the record shape | M-001, M-002 | P-001 | The record shape is the contract those consumers read | T-006 |
| P-004 | Promotion-only escalation extends the resolver, reading the ledger and the supersessions list without changing either | M-001, M-009, M-010 | P-002, P-003 | Escalation extends the resolution and relies on the recorded state staying as it is | T-009 |
| P-005 | Per-tier metrics read the record and the event detail after the record shape is fixed | M-003 | P-003 | Metrics consume the record shape defined in P-003 | T-010 |
| P-006 | The coverage and monotonicity checks are added after the declaration exists and after escalation exists | M-004, M-002 | P-001, P-004 | Verification of a boundary follows the boundary it verifies | T-011 |
| P-007 | The runtime version value rises in the same change set that first emits the record | M-001 | P-003 | The version identifies the release that first emits the record, so consumers can tell envelopes with and without it apart | T-014 |
| P-008 | Additivity, escalation equality across sessions, and every existing verifier at its baseline are verified on the finished behaviour before documentation or the mirror is frozen | M-001, M-003, M-004, M-008 | P-004, P-005, P-006, P-007 | Work that assumes the boundary holds, documentation and the mirror, must follow its verification | T-004, T-005, T-007 |
| P-009 | The field and rule are documented after the verified behaviour is known | M-005, M-006, M-014 | P-008 | Documented behaviour must match implemented behaviour, and the README must not grow | T-013 |
| P-010 | The mirror is refreshed last, by the synchronisation command only | M-007 | P-009 | The mirror must equal the final authoritative tree, and a later edit invalidates it | T-012 |

### Test Strategy Focus Areas

- Coverage fails when one phase entry is removed, when an entry names a phase that no longer exists, and when a tier has no hint; implement-feature shows at least 3 of 6 phases non-deep.
- Escalation for each rejection kind: one tier up after a validator rejection, one tier up after a gate rejection with rollback, deep stays deep, a transport failure does not escalate, and an undeclared phase escalates from standard.
- A dispatch built from recorded state alone in a fresh session yields the same tier, hint, and reason as the in-session dispatch.
- Field-by-field comparison of original envelope fields against a pre-change envelope for the same run state, and every existing verifier including replay stability at its recorded baseline.
- Per-tier metrics sum to the run totals for a completed implement-feature run, with historical runs landing in the untiered bucket.
- An absent declaration file inherits everywhere; a malformed file fails dispatch with a policy failure.
- Zero tier assignments in agent module text and zero model identifiers in runtime logic.

### Rollout and Rollback

- Rollout: the resolver may land before the declaration because an absent file means inherit; the declaration is then added, verification runs on a full implement-feature run, documentation follows, and the mirror is refreshed last.
- Rollback: delete the declaration file and every phase inherits; revert the added envelope record, event detail, prompt line, and metrics keys; no run data is migrated and historical evidence is unchanged.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | delivery | A standard implement-feature phase, such as execution planning, is rejected on its first attempt and promoted to deep | The non-deep share of a run falls below 3 of 6 invocations although the declared tiers meet the bar | medium | D-003 | Metrics report the share per run (P-005); moving execution planning to light adds margin if the bar needs it (Q-001) | architect |
| R-002 | operability | The dispatching session does not pass the hint, or the host stops accepting the override, or a named alias is not accepted | Tiers are advisory, cost does not fall, and metrics count advice rather than models run | medium | D-001 | Record the host dependency (A-001, A-003); the alias values are confirmed against the host by Q-002 before the declaration is finalised | omn-tech-lead |
| R-003 | contract | A new envelope field, event detail, or metrics key changes an artifact the replay check or another verifier compares | An existing verifier leaves its recorded baseline | medium | M-001 | Additive and deterministic output only; verify on the finished behaviour (P-008) | omn-dev-1-implement |
| R-004 | structural | The rejection count reads the wrong ledger entries, such as transport failures or gate-state entries, or a gate rejection without rollback | Escalation differs from the rule or between sessions | medium | D-002 | The rule names state id and reason code and the supersessions list (P-002); a monotonicity and equality check (P-006, P-008) | omn-dev-1-implement |
| R-005 | migration | The mirror is hand-edited, or the authoritative tree changes after the refresh | The parity check reports differing files | medium | P-010 | The refresh runs last and only by the synchronisation command (P-010) | omn-documentation |
| R-006 | operability | Cheaper tiers produce more rejected attempts | Promotion invocations offset the saving | low | D-003 | Per-tier invocation counts make the effect visible (P-005) | omn-tech-lead |
| R-007 | structural | A phase is added or renamed in a Phase Model without a declaration entry | The phase silently inherits and the cost lever lapses unnoticed | medium | M-002 | The coverage check fails on an uncovered phase (P-006) | architect |
| R-008 | delivery | Adding two checks to the coverage verifier changes a recorded count that a baseline comparison reads as drift | A release verification reports a false regression | medium | M-004 | Q-003 confirms what the baseline records; the comparison is made on the verdict and per-check results (P-008) | omn-qa |
| R-009 | security | A wrong or tampered declaration assigns a cheaper tier to a deep phase | A weaker reader produces more rejected attempts, though validators and gates still decide correctness | low | D-001 | The declaration file is part of the reviewed change set and the coverage check pins the named categories (P-006, P-008) | omn-dev-2-reviewer |

## Estimate and Confidence

- Overall: M (confidence: medium)
- Breakdown:
  - M-001: M, resolver, record, event detail, and prompt line in one module with two additive contract changes.
  - M-002: S, one data file holding 37 assignments and 3 hints.
  - M-003: S, one grouping added to an existing computation.
  - M-004: M, two checks, one of them over every tier and rejection count.
  - M-005, M-006: S, documentation only.
  - M-007, M-008: S, mirror refresh and one new test file.
- Scope assumptions:
  - The 14 planner tasks are the delivery shape; this estimate is architectural and sizes no task.
  - Effort excludes host-side effectiveness (A-001, A-003), which the framework cannot implement.
  - No other registered surface needs a coverage entry for the new file.
- Uncertainty drivers:
  - Host alias values are not yet named (Q-002).
  - What the recorded verifier baseline contains is unconfirmed (Q-003).
  - The 3-of-6 bar rests on an operator resolution outside the scope artifact (A-002).

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Does the operator accept execution planning at standard, giving exactly 3 of 6 non-deep with no margin, or should it move to light for margin | no | omn-business-analyst | D-003 | Standard keeps planning quality but leaves no margin (R-001); light gives 4 of 6 but exposes the plan validator to a cheaper reader |
| Q-002 | Which two host alias values does the declaration use for the light and deep hints | no | omn-tech-lead | D-001 | A value the host does not accept makes that tier advisory only (R-002); a confirmed value makes the tier effective |
| Q-003 | Does the recorded baseline of the registry coverage verifier count its checks, so that adding two reads as drift | no | omn-qa | P-006 | If counted, the baseline is refreshed alongside the change; if not, no action is needed (R-008) |
| Q-004 | Is a per-dispatch operator switch to disable or override tiering wanted | no | omn-product-owner | D-002 | If wanted it becomes a new scope item with its own design; if not, absence of the file is the only off position |

## Sign-off

- Design Gate owners: omn-architect, omn-tech-lead; the producer exclusion rule applies, so acceptance of D-001 and D-002 rests with omn-tech-lead.
- Architect: unsigned; this agent does not sign its own gate.
- Tech Lead: unsigned; decision records D-001 and D-002 stay at status Proposed until the Design Gate decision.
- QA: unsigned; review of the test strategy focus areas by omn-qa.
