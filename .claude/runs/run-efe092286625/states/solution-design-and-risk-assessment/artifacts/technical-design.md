```yaml
design:
  designId: CKA-01-technical-design
  changeReference: runs/inputs/cka-01-feature-request.md
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-01-feature-request.md
    - type: execution-plan
      reference: runs/run-efe092286625/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002]
  consumesPlan: runs/run-efe092286625/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:fe6d5499a0045f1a0592b6bc1ab9190c
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: CKA-01 — ticket CKA-01 in the adoption backlog under `docs/`, Epic A (verification baseline), carrying recommendation R1 of the toolkit adoption review (2026-08-27)
- Author: architect
- Reviewers: omn-architect, omn-tech-lead (Design Gate owners)
- Last Updated: 2026-08-28

Grounding note: the current-state facts below were established from the supplied inputs and
from source inspection of the repository files this run was authorized to read
(`omn_agent/validator.py`, `omn_agent/common.py`, `omn_agent/runner.py`, `omn_agent/source.py`,
`pyproject.toml`, `README.md`, and the framework payload runtime files the installer
distributes from the payload's `runtime/` directory). "The CLI" throughout this package means
the console tool provided by the `omn_agent` package. This design fulfils plan task T-004 and
constrains the plan tasks named in each section; it creates no task identifiers of its own.

## Objective

Desired structural outcome: a clean-environment installation of the CLI is runnable, the
published dependency claim is true, and the installation-health verification path converts a
missing runtime dependency into a named finding instead of certifying a dead runtime — with
the gate-decision and human-approval machinery structurally untouched.

Architectural objectives:

1. The distribution's install contract carries the third-party module its executed payload
   needs at module top level, so environment resolution succeeds at install time rather than
   failing at first run. Traces to S-001, S-002, S-005, S-008.
2. The shared verification path used by both `validate` and `doctor` gains a static
   import-resolution capability: an installed runtime file whose top-level import cannot be
   resolved produces an ERROR finding that names the unresolved module, without verification
   ever executing payload code. Traces to S-004, S-007, S-009, S-014.
3. The extension is strictly additive: a healthy installation produces no new findings, and
   no gate-decision, producer-exclusion, or human-approval path changes. Traces to S-010,
   S-011, S-016, S-017.
4. The published documentation contract matches the declared dependency set, including the
   HTML handbook wherever documentation is touched. Traces to S-003, S-006, S-012.

In structural scope: the verification helper and shared validation path in
`omn_agent/validator.py` (M-001); the distribution metadata in `pyproject.toml` (M-002); the
dependency claim in `README.md` (M-003) and its handbook mirror `user-guide.html` (M-004).

Out of structural scope (bounds the impact surface): the report model in
`omn_agent/common.py` (M-005); the runner and its approval path (M-006); every installed
payload runtime file, including the gate-decision machinery they carry (M-007); the bootstrap
descriptor schema and builder (M-008); import detection deeper than module top level;
automatic remediation; CI gating (separate backlog tickets). Each exclusion mirrors the
approved scope's X-001 through X-005.

## Requirements Summary

Functional requirements:

- The declared dependency set of the distribution includes the third-party YAML library, so a
  clean-environment install resolves it (S-005, S-008).
- Verification resolves the top-level imports of the installed runtime files it already
  examines, and reports a finding — not an exception, not a healthy result — that names any
  unresolvable module (S-007, S-009).
- The finding surfaces identically in the `doctor` and `validate` commands (S-014).

Non-functional requirements:

- Preservation: a healthy installation is certified healthy with no new findings; the
  existing tests stay green; every proof script stays PROVEN (S-010, S-012, S-016).
- Additivity: no change to `record_gate_decision`, gate matrix semantics, producer
  exclusion, `runner._require_approval`, or any human-block path (S-011).
- Boundedness: detection covers module top-level imports only; function-local, conditional,
  dynamic, and transitive imports are excluded (S-015).

Acceptance intent: supplied verbatim by the ticket and carried by the approved scope
definition (SCOPE-2026-0001, whose eight acceptance criteria each name a scope item and a
verification method) and the execution plan (CKA-01-execution-plan, plan acceptance criteria
1 through 4); cited here rather than restated (S-008, S-009, S-010, S-012).

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | `pyproject.toml` declares `dependencies = []` for the CLI distribution | Source inspection: `pyproject.toml`; S-002 |
| F-002 | `README.md` line 10 states "Python 3.10+, standard library only" | Source inspection: `README.md`; S-003 |
| F-003 | `omn_agent/validator.py::_check_python` verifies a runtime file by existence plus a built-in compile step only; it never resolves the file's imports | Source inspection: `omn_agent/validator.py` (helper at lines 204-214); S-004 |
| F-004 | `run_validation` applies `_check_python` to every runtime entrypoint and every validator reference named by the installed bootstrap descriptor | Source inspection: `omn_agent/validator.py` (descriptor loop) |
| F-005 | `cmd_doctor` calls `run_validation` and extends its report; `cmd_validate` calls `run_validation` directly — both commands share one check path | Source inspection: `omn_agent/validator.py` (command functions at lines 226-237) |
| F-006 | Findings are emitted through a shared report model carrying a stable machine-readable code, message, and optional hint; an ERROR finding makes the command exit non-OK | Source inspection: `omn_agent/common.py` |
| F-007 | The `omn_agent` package itself contains no top-level import of the third-party YAML module; it uses the standard library only | Source inspection: search across `omn_agent/` |
| F-008 | Installed payload runtime files import the third-party module named `yaml` at module top level: the framework runtime entrypoint, the design validator, the plan validator, the artifact library, the artifact contract module, and one verification script | Source inspection: search across the framework payload runtime directory |
| F-009 | Installed payload runtime files import sibling payload modules at module top level (artifact_lib, artifact_contract, framework_runtime, state_engine, recovery_policy, self_hosting), resolved by a path insertion the files perform at their own execution time | Source inspection: payload runtime files and their inline comments |
| F-010 | The runner executes the installed framework runtime as a subprocess of the same interpreter that runs the CLI, so the runtime resolves imports in the environment where the CLI is installed | Source inspection: `omn_agent/runner.py` (invocation) |
| F-011 | `_context_slice_members` in `omn_agent/validator.py` already reads the installed runtime statically via syntax-tree parsing, deliberately not importing it, with the recorded reason that importing would require the runtime's own dependencies in the validation environment | Source inspection: `omn_agent/validator.py` (docstring) |
| F-012 | The bootstrap descriptor names two entrypoints (framework runtime, state engine) and, as validators, every payload file matching the validator filename pattern under the payload runtime directory | Source inspection: `omn_agent/source.py` (descriptor builder) |
| F-013 | `omn_agent/validator.py` contains none of the forbidden symbols (`record_gate_decision`, `_require_approval`, producer exclusion, human-block); those symbols live in `omn_agent/runner.py`, `update.py`, `quality_scan.py`, and `fix_comments.py`, none of which this design touches | Source inspection: symbol search across `omn_agent/` |
| F-014 | Across the entire installed payload runtime directory, the only third-party root module imported at module top level is `yaml`; every other top-level import root is a standard-library module or a sibling payload module | Source inspection: full top-level import inventory of the payload runtime directory |
| F-015 | `validate` and `doctor` are documented as writing nothing | Source inspection: `README.md` command table |
| F-016 | The Design Gate for `implement-feature` is owned by omn-architect and omn-tech-lead, and the producer exclusion rule forbids self-approval | `workflows/workflow-gate-matrix.md` (supplied context) |
| F-017 | The backlog definition of done requires `user-guide.html` to be updated to match wherever documentation is touched | Feature request constraints (S-012) |
| F-018 | The third-party root module named `yaml` is provided by the distribution `pyyaml`: the ticket pairs the runtime dying on that import with the deliverable of declaring `pyyaml` | Feature request (S-004, S-005) |

Fact F-014 is the recorded top-level import inventory required by plan task T-004: it
confirms the plan's assumption that PyYAML is the only undeclared third-party runtime
dependency. Fact F-013, together with the impact surface in 5.1, confirms the plan's
assumption that an additive extension exists touching no forbidden gate-decision or
human-approval path.

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | Operators run `doctor`/`validate` with the same interpreter environment that executes the installed runtime | F-010 establishes the runner uses the same interpreter as the CLI, but nothing prevents an operator invoking verification from a different environment | A finding, or its absence, describes the wrong environment; detection stays correct for the documented single-environment usage, and the finding wording must make the checked environment identifiable | omn-tech-lead |
| A-002 | No existing test asserts the exact healthy-run finding set in a way that any new healthy-path output would break | The preservation constraint C-004 requires the existing tests to pass unchanged | The healthy path must add no output at all; the design already requires healthy-path silence (D-003), so a false assumption tightens nothing but confirms the requirement | omn-qa |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | Additive check only: no alteration of `record_gate_decision`, gate matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path | Hard | S-011 |
| C-002 | functional | The missing-module finding surfaces in both `doctor` and `validate` and names the unresolved module | Hard | S-007, S-009, S-014 |
| C-003 | functional | Detection is bounded to module top-level imports of the installed runtime files; no function-local, conditional, dynamic, or transitive resolution | Hard | S-015 |
| C-004 | quality-attribute | Preservation: healthy installation certified healthy with no new findings; existing tests green; proof scripts PROVEN | Hard | S-010, S-012, S-016 |
| C-005 | security | Verification must not execute installed payload code and must write nothing | Hard | F-011, F-015 |
| C-006 | functional | An unresolvable import is reported as a finding, never raised as an exception out of verification | Hard | S-007 |
| C-007 | compliance | Published documentation states the true dependency footprint, and `user-guide.html` agrees wherever documentation is touched | Hard | S-006, S-012, F-017 |
| C-008 | structural | `pyyaml` is declared in the distribution's dependency metadata so a clean install pulls it | Hard | S-005, S-008 |
| C-009 | quality-attribute | The solution favors the smallest compliant change, so the verification baseline lands within the adoption plan's first phase | Negotiable | S-013, S-015 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `omn_agent/validator.py` (`_check_python` helper on the shared `run_validation` path) | extension | F-003, F-004, F-005 | `validate`/`doctor` report output gains one new stable finding code | confirmed |
| M-002 | `pyproject.toml` distribution metadata | contract-change | F-001 | pip install dependency-resolution contract | confirmed |
| M-003 | `README.md` dependency claim | behavior-change | F-002 | none | confirmed |
| M-004 | `user-guide.html` handbook | behavior-change | F-017 | none | confirmed |
| M-005 | `omn_agent/common.py` report model | no-change-verified | F-006 | none | confirmed |
| M-006 | `omn_agent/runner.py` approval and gate-recording path | no-change-verified | F-013 | none | confirmed |
| M-007 | Installed payload runtime files (the framework payload directory the installer writes into a target repository), including the gate-decision machinery they carry | no-change-verified | F-008, F-013, F-014 | none | confirmed |
| M-008 | `omn_agent/source.py` bootstrap descriptor builder and schema | no-change-verified | F-012 | none | confirmed |

M-005 through M-008 are recorded because a reader of the additive-check-only constraint
(C-001) would reasonably expect them to participate: the report model is reused unchanged,
the runner and every payload file are untouched, and the descriptor schema keeps its shape.
The forbidden symbols named by C-001 do not occur in M-001 (F-013), which is the only code
module this design changes.

Boundary crossing: verification (M-001, running in the CLI's environment) reads — never
executes — files owned by the installed framework payload (M-007). This is the one boundary
the change touches, and it is already crossed the same way by the existing context-slice
check (F-011).

### 5.2 Options Considered

Evaluation criteria, in reasoning order: hard-constraint satisfaction (C-001 through C-008);
impact surface (count of modules with contract-change or dependency-change); reuse leverage
(capabilities satisfied by reuse-as-is or reuse-extended, of the seven surveyed in section
7); quality-attribute satisfaction (C-004 exposure); migration burden (contract-affecting
changes needing a transition); operability impact. Two decisions carry design freedom and
each has its own option family evaluated below on the same criteria: detection (D-001,
options O-001 through O-003) and dependency provisioning (D-002, options O-004 through
O-006). For the provisioning family, the dispositions of C-007 through C-009 are recorded in
each row's Structural change and Outcome cells; C-008 is the forcing hard constraint there.

Detection options (decision D-001):

| Option | Structural change | C-001 | C-002 | C-003 | C-004 exposure | C-005 | C-006 | Impact surface | Reuse leverage | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | Extend `_check_python` in place: after a successful compile, statically collect the checked file's module-top-level import roots and resolve each against the executing environment's import machinery and against sibling payload files in the checked file's own directory; each unresolved root becomes an ERROR finding naming the module | Satisfied | Satisfied | Satisfied | Lowest: only descriptor-named files are checked; sibling rule covers F-009 | Satisfied | Satisfied | 1 | 7 | 1 | Negligible: static parse of files already read for compile | Selected |
| O-002 | New standalone check in `run_validation` walking every payload file under the installed runtime directory with the same resolution rule | Satisfied | Satisfied | Satisfied | Higher: checks files never named by the descriptor, enlarging false-finding exposure | Satisfied | Satisfied | 1 | 5 | 1 | Larger scan per run | Rejected on criteria 3 and 4: reuse leverage 5 versus 7 and higher C-004 exposure; violates no hard constraint |
| O-003 | Dynamic probe: verification imports or executes each runtime file (directly or via subprocess) and reports the import failure it observes | Satisfied | Satisfied | Violated (executes transitive resolution) | Unbounded: any side effect of payload top-level code runs at verification time | Violated | Satisfied | 1 | 4 | 1 | Verification acquires execution cost and side-effect risk | Eliminated on C-005; also exceeds the C-003 bound |

Provisioning options (decision D-002):

| Option | Structural change | C-001 | C-002 | C-003 | C-004 exposure | C-005 | C-006 | Impact surface | Reuse leverage | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O-004 | Declare `pyyaml` in the existing packaging metadata (`pyproject.toml` dependencies); no payload file changes; satisfies the forcing hard constraint C-008 and enables the truthful documentation C-007 requires; smallest compliant change per C-009 | Satisfied | Satisfied | Satisfied | None: verification path and payload untouched | Satisfied | Satisfied | 1 | 1 | 1 | One additional wheel at install time | Adopted for D-002, forced by hard constraint C-008: the only provisioning option satisfying it |
| O-005 | Vendor a minimal YAML parser into the framework payload; violates C-008, which requires the declaration rather than a substitute; costs C-009 points through new structure to maintain | Satisfied | Satisfied | Satisfied | Higher: replaces payload behavior the no-change stance of M-007 protects | Satisfied | Satisfied | 0 | 0 | 0 | Larger payload; parser maintenance burden | Eliminated on C-008 |
| O-006 | Leave the dependency undeclared and rely on detection (D-001) alone; violates C-008; documentation truth (C-007) achievable only by documenting a manual install step | Satisfied | Satisfied | Satisfied | None new, but clean installs stay broken at first run | Satisfied | Satisfied | 0 | 0 | 0 | Broken first run persists for every clean install | Eliminated on C-008 |

Impact surface counts contract-change/dependency-change modules. Reuse leverage is counted
against the capabilities in section 7 that each option exercises.

### 5.3 Selected Approach

- Selected: O-001.
- Structural change: the existing per-file verification helper (M-001), which already
  receives exactly the runtime entrypoints and validator files the descriptor names (F-004,
  F-012), gains a second static step after its compile step. The step derives the checked
  file's module-top-level import roots from the source it already read, and resolves each
  root through two sources: the executing environment's import machinery (the standard
  library's find-spec facility — the correct environment by F-010), and the sibling rule — a
  root resolves if a module file of that name exists in the checked file's own directory,
  which is precisely how the payload files resolve each other at execution time (F-009). A
  root that resolves through neither source produces one ERROR finding through the existing
  report model (F-006), carrying a new stable finding code, the checked file, and the
  unresolved module name, with a hint naming the distribution known to provide it where that
  is known (F-018). Resolution failures inside the lookup are caught and reported as
  findings, never raised (C-006). Because `doctor` reuses `run_validation` (F-005), the
  finding surfaces in both commands with no command-level change. On a healthy installation
  the step emits nothing (D-003). Relative imports and anything below module top level are
  ignored (C-003).
  Per O-004 (D-002): `pyproject.toml` declares `pyyaml` in `dependencies` (M-002, C-008),
  and the documentation claim is corrected (M-003, M-004, C-007) — the CLI package itself
  remains standard-library only (F-007); the declared dependency exists on behalf of the
  payload runtime files the CLI installs and executes with the same interpreter (F-008,
  F-010).
- Rationale: O-001 satisfies every hard constraint, ties O-002 on impact surface and
  migration burden, and wins on reuse leverage (7 versus 5) and on C-004 exposure: it checks
  only the files verification already examines, so the healthy-path preservation obligation
  is confined to the smallest possible file set. It also reuses the codebase's own recorded
  precedent for static-not-imported analysis (F-011). For the companion provisioning
  decision D-002, O-004 is the only option satisfying hard constraint C-008 (O-005 and
  O-006 are eliminated on it), so that decision is forced rather than scored, and it is
  adopted — it is not an alternative to O-001 but the answer to the separate provisioning
  question.
- Highest-scoring rejected alternative and why it lost: O-002. Its broader traversal would
  individually check payload files the descriptor does not name (for example, verification
  proof scripts). But the only undeclared third-party root anywhere in the payload is `yaml`
  (F-014), and it is imported at top level by descriptor-named files (F-008), so the broader
  walk adds no detection value for the stated acceptance criteria while enlarging the
  false-finding exposure on healthy installations and abandoning the existing check site and
  enumeration (reuse leverage 5 versus 7).
- Tradeoffs accepted: payload files that are neither entrypoints nor validators are not
  individually import-checked; a future third-party import confined to such a file would
  surface only when that file executes. Recorded as R-004 with the scope's revisit triggers.
  Detection is also inherently blind below module top level — accepted by C-003 and the
  approved scope exclusion X-002. The forced provisioning decision (O-004, D-002) ends the
  distribution's zero-dependency status (R-003, R-006).

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Missing-dependency detection is a static top-level import-resolution step inside the existing per-file verification helper on the shared validation path, resolving against the executing environment plus sibling payload files, and reporting — never raising — an ERROR finding that names the unresolved root module (implements O-001; commits the verification boundary to a static-analysis quality tradeoff and extends the externally observable finding vocabulary) | Yes | ADR D-001, status Proposed |
| D-002 | The CLI distribution declares `pyyaml` as an install-time dependency on behalf of the payload runtime files it installs and executes with the same interpreter, and published documentation states the corrected footprint (adopts O-004, forced by hard constraint C-008; changes the externally visible install contract) | Yes | ADR D-002, status Proposed |
| D-003 | The new finding uses one new stable code in the existing verification code vocabulary at ERROR severity, with a hint naming the providing distribution; the healthy path emits no new output of any severity (inline message-shape detail within D-001, bounded by C-004 and A-002) | No | Inline |

## API and Data Model Impact

API changes:

- M-002 (contract-change): the distribution's dependency metadata changes from an empty set
  to a set containing `pyyaml`. Transition strategy:
  - Current shape: `dependencies = []` (F-001); installs pull nothing.
  - Target shape: `dependencies` includes `pyyaml`; a clean install pulls it (C-008, S-008).
  - Compatibility approach: strictly additive. Existing installed environments are
    untouched; new installs acquire one additional distribution. No consumer of the CLI's
    commands or exit codes changes.
  - Coexistence period: none required. Environments installed before the change simply lack
    the guarantee — and are exactly what the new detection finding (D-001) makes visible.
  - Retirement condition: not applicable; no old shape is retained.
  - Rollback position: removing the declaration returns the metadata to its current shape;
    already-installed environments keep functioning; the detection finding remains the
    operator's signal for environments where the module is absent.
- M-001 (extension, recorded here for completeness): `validate` and `doctor` output gains
  one new finding code. Additive only: no existing code, message, severity, or exit-code
  mapping changes (F-006), and the healthy path emits nothing new (D-003, C-004).

Contract compatibility notes: the version-range policy for the `pyyaml` declaration is a
delivery decision (Q-001, omn-tech-lead); this design constrains only that the declaration
exists and that a clean install resolves it.

Schema or migration changes: None identified. No data model, stored artifact schema, or
descriptor schema (M-008) changes, so no data migration exists; direction, reversibility,
and transition behavior are therefore not applicable.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Finding reporting with stable codes, severities, hints, and exit-code mapping | Report/Finding model in `omn_agent/common.py` | reuse-as-is | F-006: the model already carries everything the new finding needs; a parallel reporting path would split the single decision point the model exists to provide |
| Surfacing one check in both `doctor` and `validate` | `run_validation` shared path | reuse-as-is | F-005: `doctor` already reuses `run_validation`; placing the check on that path satisfies C-002 with zero command-level change |
| Per-file verification site over exactly the executed runtime files | `_check_python` helper | reuse-extended | F-003, F-004, F-012: the helper already visits every descriptor-named entrypoint and validator and already reads each file's source; the import step extends it in place |
| Static source analysis without executing payload code | Syntax-tree reading precedent (`_check_python` compile step; `_context_slice_members` parse) | reuse-extended | F-011: the codebase already records why verification reads statically instead of importing; the import extraction follows the same pattern |
| Import resolution against the environment that will execute the runtime | Standard library import machinery (find-spec facility) | reuse-as-is | F-007, F-010: resolves in the interpreter environment the runner actually uses, and keeps the CLI package standard-library only |
| Enumerating which files to check | Bootstrap descriptor entrypoints and validators | reuse-as-is | F-012: the descriptor is the installed source of truth for what verification must resolve; a second enumeration would drift from it (O-002 rejected on this) |
| Providing the YAML capability to the payload | pip dependency declaration in existing packaging metadata | reuse-as-is | F-001, F-018: the packaging contract already exists and needs one entry (O-004). The considered alternative — vendoring a YAML parser into the payload (O-005) — was rejected: it contradicts the ticket's verbatim deliverable (S-005, C-008), creates new structure to maintain, and duplicates a capability the ecosystem already provides |

No capability has outcome `none-found`, and the only `rejected` candidate (vendoring) is
recorded with its reason; the selected approach proposes no new structural component.

## Operational Considerations

- Logging and observability updates: one new stable finding code in the `validate`/`doctor`
  report stream (M-001, D-003). Machine consumers keyed on existing codes are unaffected;
  the new code is additive (F-006). The finding names the checked file and the unresolved
  module, which is the observable the acceptance criteria demand (C-002).
- Error handling strategy: every failure mode of the resolution step — unresolvable root,
  lookup errors raised by the import machinery, unreadable source — is converted into a
  report finding on the existing model; nothing propagates as an exception out of
  verification (C-006, M-001). A file that fails to compile keeps its existing
  compile-failure finding and is not additionally import-checked, since its import set is
  not reliably derivable.
- Security considerations: detection is static — verification never executes payload code
  and writes nothing (C-005, F-011, F-015), so no payload side effect can run at
  verification time. The dependency declaration makes an already de facto dependency an
  explicit supply-chain surface (M-002); this is an improvement in visibility, with residual
  exposure recorded as R-006. No secrets, credentials, or elevated access are involved.
- Performance considerations: the added work is one syntax-level pass over files whose text
  verification already reads for the compile step (M-001, F-003), plus one environment
  lookup per distinct import root. Bounded by C-009; no measured performance constraint was
  supplied, and none is asserted.
- Deployment and operability impact: a clean-environment install pulls one additional wheel
  (M-002). Verification behavior in healthy environments is unchanged (C-004); in broken
  environments it changes from false certification to a named ERROR with a non-OK exit
  (F-006), which is the intended operator-facing effect.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The detection contract is fixed: what counts as a top-level import root, the two resolution sources (executing environment; sibling payload file in the checked file's directory), the finding's code, severity, and module-naming message shape, and the healthy path's silence | M-001 | none | Both the verification build and the validation coverage bind to this contract; building either against an unfixed contract forces rework (D-001, D-003) | T-004 (fulfilled by this design: the contract this step fixes is the approved approach that task requires), T-005, T-006 |
| P-002 | The dependency declaration exists in the distribution metadata before the corrected documentation claim is published | M-002, M-003 | none | Documentation must state a footprint that is already declared, or it is false in the opposite direction (C-007, C-008) | T-001, T-002 |
| P-003 | The extended check is demonstrated silent against a healthy installation — every top-level root of every descriptor-named file resolving, including sibling imports — before any reliance on its broken-environment behavior | M-001, M-007 | P-001 | A check that false-positives on healthy installations violates C-004 and cannot be shipped; this is the reversibility safeguard that precedes reliance (F-009, F-014) | T-005, T-006 |
| P-004 | Handbook agreement follows the corrected README statement | M-003, M-004 | P-002 | The handbook mirrors touched documentation (C-007, F-017); mirroring an uncorrected statement propagates the false claim | T-002, T-003 |
| P-005 | Broken-environment demonstration evidence (`doctor` and `validate` findings naming the missing module) is recorded only after the detection contract and healthy-path silence hold | M-001 | P-001, P-003 | Evidence recorded against an unstable contract or an unproven healthy path does not verify the acceptance criteria (C-002, C-004) | T-007 |

The prerequisite graph is acyclic; contract definition (P-001, P-002) precedes every
consumer change; the irreversible reliance step (P-005) is preceded by its safeguard
(P-003). No step is ordered by preference. These are structural constraints, not tasks:
task decomposition belongs to `planner`, and delivery feasibility beyond this structural
order belongs to `omn-tech-lead`. The `Binds` column cites supplied plan tasks and creates
none.

### Test Strategy Focus Areas

For `omn-qa` (constraining T-006 and T-007):

- Broken environment: with the YAML module absent, `doctor` and `validate` each report an
  ERROR finding naming the module, and exit non-OK (C-002).
- Healthy environment: pre/post comparison shows an identical finding set — explicitly
  including that sibling imports (F-009) produce no finding (C-004, R-001).
- Boundedness: a dependency imported only inside a function or behind a condition produces
  no finding (C-003, negative coverage of the scope exclusion X-002).
- Non-raising behavior: a file with an unresolvable import yields a finding, never an
  unhandled exception or a changed exit-code category (C-006).
- Preservation: existing tests green, every proof script PROVEN, and no gate-decision or
  approval code path touched — verifiable by inspection that the change is confined to
  M-001 through M-004 (C-001, F-013).
- Install: clean-environment install resolves the declared dependency and the installed CLI
  starts (C-008).

### Rollout and Rollback

- Rollout: follows the sequencing constraints; P-003's healthy-environment silence evidence
  gates reliance, and P-005 records the acceptance demonstrations.
- Rollback: the detection step and its finding code are removed from M-001, returning
  verification to compile-only behavior; the dependency declaration is removable per the
  M-002 rollback position in section 6; documentation reverts with M-003/M-004. No stored
  state, schema, or gate behavior exists to unwind.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | structural | A future payload runtime file imports a sibling from outside its own directory, or through a mechanism the sibling rule does not cover | False ERROR finding on a healthy installation, violating C-004 | low | M-001, D-001 | P-003 healthy-environment silence proof, plus explicit healthy-path negative coverage in the test focus areas | omn-qa |
| R-002 | operability | An operator runs `doctor`/`validate` from a different interpreter environment than the one that executes the runtime (A-001 false) | The finding, or its absence, describes the wrong environment | medium | M-001, D-001 | The finding message shape fixed in P-001 makes the checked environment identifiable; documentation states that verification checks the environment it runs in | omn-tech-lead |
| R-003 | contract | An install runs where the declared dependency is not obtainable (restricted index, offline) | Clean install of the distribution no longer completes there | low | M-002, D-002 | Rollback position in section 6; the detection finding names the module, so the failure is diagnosable rather than latent; version-range policy resolved via Q-001 | omn-tech-lead |
| R-004 | delivery | A payload file that is neither an entrypoint nor a validator acquires a new third-party top-level import without a matching declaration | The gap surfaces only when that file executes, not at verification (accepted tradeoff of O-001) | low | M-001, D-001 | Scope revisit triggers X-001/X-002 fire on the first such finding; Q-002 records the broadening decision and its owner | omn-tech-lead |
| R-005 | operability | An existing test asserts exact healthy-run output and new healthy-path output breaks it (A-002 false) | Preservation criterion fails in test evidence | low | M-001, P-003 | D-003 keeps the healthy path silent by design; P-003 proves it before reliance | omn-qa |
| R-006 | security | A compromised, yanked, or incompatible release of the declared dependency is served at install time | Clean installs acquire a defective or malicious component | low | M-002, D-002 | Version-range policy decision Q-001; installs remain operator-initiated; the declaration only makes explicit a dependency the runtime already had | omn-tech-lead |

Every approach-affecting assumption has a matching risk (A-001 → R-002, A-002 → R-005); the
one contract change (M-002) carries a proven additive transition and still holds attached
risks R-003 and R-006; no speculative impact exists in 5.1.

## Estimate and Confidence

- Overall: `S` (confidence: high).
- Breakdown: P-001 and P-003 (detection contract, extension of the verification helper, and
  healthy-path proof): `S`; P-002 (one-line dependency declaration): `XS`; P-004
  (documentation and handbook alignment): `XS`; P-005 is verification effort owned by
  `omn-qa` and is not estimated here.
- Scope assumptions: the estimate covers exactly the four changed modules (M-001 through
  M-004); detection bounded to top-level roots of descriptor-named files; a single
  third-party dependency (F-014); no payload runtime file, runner, report-model, or
  descriptor change.
- Uncertainty drivers: minimal — every impacted module is confirmed by source inspection
  and no speculative impact exists. A-001 and A-002 affect message wording and test shape,
  not effort. Confidence is `high` accordingly; it would drop to `medium` only if Q-002 were
  answered by broadening the checked file set.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | What version-range policy should the `pyyaml` declaration carry (lower bound, exclusions, or unpinned)? | No | omn-tech-lead | M-002, D-002, R-006 | Unpinned maximizes install flexibility but widens supply-chain exposure; a bound narrows exposure but can conflict with co-installed tooling. Either answer fits this design; delivery decides before T-001 completes. |
| Q-002 | Should verification later check payload files beyond the descriptor-named set (the accepted tradeoff of O-001)? | No | omn-product-owner | M-001, D-001, R-004 | Broadening closes the R-004 gap at the cost of a larger healthy-path exposure and sits behind the approved scope's revisit triggers X-001/X-002; declining keeps the narrowest compliant check per C-009. |

Neither question blocks execution. Decision records D-001 and D-002 remain at status
`Proposed` and require Design Gate acceptance before P-001's contract is treated as fixed
for the build (T-005).

## Sign-off

- Architect: omn-architect (architecture role, implemented by `architect`, producing role —
  excluded from accepting this package under the producer exclusion rule)
- Tech Lead: omn-tech-lead (accepting owner for the Design Gate)
- QA: omn-qa (verification focus areas in section 9)

Design Gate owners per `workflows/workflow-gate-matrix.md` (F-016): omn-architect and
omn-tech-lead. Because the architecture role produced this package, acceptance rests with
`omn-tech-lead`. Lines are left unsigned by the producing agent. No implementation work was
performed in producing this design.

### Appendix: Traceability

Forward closure — every statement from the normalized inputs maps into the design:

| Statement | Summary | Maps to |
|---|---|---|
| S-001 | Runtime needs a third-party YAML library; manifests and registries are YAML | C-008, M-002, objective 1 |
| S-002 | Distribution declares an empty dependency set | F-001, M-002, C-008 |
| S-003 | Documentation claims standard-library only, falsely | F-002, M-003, C-007 |
| S-004 | Clean install dies on the missing module while verification certifies it, because the helper only compiles | F-003, M-001, objective 2 |
| S-005 | Deliverable: declare `pyyaml` in the distribution dependencies | C-008, D-002, M-002 |
| S-006 | Deliverable: correct the README claim | C-007, M-003 |
| S-007 | Deliverable: extend the helper to resolve top-level imports and report a finding naming the module | C-002, C-006, D-001, M-001 |
| S-008 | Acceptance: clean-venv install pulls the dependency | C-008, P-002 |
| S-009 | Acceptance: `doctor` in a dependency-less environment reports a finding naming the module | C-002, M-001, P-005 |
| S-010 | Acceptance: existing tests remain green | C-004, P-003 |
| S-011 | Additive check only; forbidden gate/approval paths | C-001, M-006, M-007 |
| S-012 | Backlog definition of done, including handbook agreement | C-004, C-007, M-004 |
| S-013 | Priority and phase window; blocks the CI-gating ticket | C-009, Q-002 |
| S-014 | Plan: `validate` held to the same finding behavior as `doctor` | C-002, M-001 |
| S-015 | Plan: detection bounded to top-level imports; deeper analysis excluded | C-003, D-001 |
| S-016 | Plan: healthy installation preserved with no new findings | C-004, P-003 |
| S-017 | Plan: the design records the import inventory and demonstrates no forbidden path is altered | F-013, F-014, objective 3 |

Backward closure: every module in 5.1 traces to facts; D-001 traces to O-001, and D-002
traces to O-004, forced by hard constraint C-008; every option traces to the recorded
constraint set. Lateral closure: every risk attaches to a module or decision; every plan
step references modules from 5.1; ADRs D-001 and D-002 correspond one-to-one to the
significant decisions in 5.4; no speculative impact exists. Register integrity: every
current-state claim in this package carries an F-nnn or A-nnn reference. Plan-task coverage:
T-001 through T-007 are each bound by at least one sequencing constraint, with T-004
fulfilled by this package at P-001.
