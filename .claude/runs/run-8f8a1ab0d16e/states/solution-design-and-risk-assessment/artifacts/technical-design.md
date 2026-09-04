```yaml
design:
  designId: CKA-03-technical-design
  changeReference: CKA-03
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-03-feature-request.md
    - type: execution-plan
      reference: runs/run-8f8a1ab0d16e/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002, D-003]
  consumesPlan: runs/run-8f8a1ab0d16e/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:339765ecb332b53789a324f2f73636c3
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: CKA-03 (ticket CKA-03 in the adoption backlog under `docs/`)
- Author: architect
- Reviewers: omn-architect, omn-tech-lead (Design Gate owners)
- Last Updated: 2026-09-04

Statement register (normalized from the supplied inputs, in supply and document order):

| ID | Statement | Source |
|---|---|---|
| S-001 | A CI workflow runs on every pull request and on pushes to the default branch | Feature request |
| S-002 | Both verification surfaces are located by discovery, never a curated file list | Feature request |
| S-003 | Surface 1 is the unit-test suite via the standard-library unittest discovery invocation the ticket names, run from the repository root | Feature request |
| S-004 | Surface 2 is every proof script matching `verify_*.py` under the framework payload runtime directory, each executed individually and asserted to exit successfully with its passing verdict | Feature request |
| S-005 | The platform matrix is ubuntu and windows runners | Feature request |
| S-006 | Verifier jobs are advisory for the first week after merge, then required | Feature request |
| S-007 | The windows job is advisory for week one | Feature request |
| S-008 | The ubuntu unit-test job is required from day one | Feature request |
| S-009 | Acceptance: a pull request that breaks any single verifier fails CI naming that verifier | Feature request |
| S-010 | Acceptance: adding a new `tests/test_*.py` or `verify_*.py` file is picked up with no CI configuration change | Feature request |
| S-011 | Additive change only: no alteration of the gate-decision runtime surfaces the ticket names; at most a small discovery helper script; no runtime behavior change | Feature request |
| S-012 | No workflow step may enumerate test or verifier files by name in a way that requires editing CI configuration when a file is added | Feature request |
| S-013 | The recovery proof script is timing-sensitive under CPU load, and its crash can leave injected runs behind that fail the self-hosting proof's run-accounting check downstream; ordering and isolation must prevent one flake from cascading | Feature request |
| S-014 | CI must not set NO_COLOR; some render tests assert color output and fail spuriously when it is set | Feature request |
| S-015 | Three pre-existing orphan run directories from 2026-08-27 fail the self-hosting run-accounting check; the design must state the handling rather than shipping a permanently red required job | Feature request |
| S-016 | Backlog definition of done: unit tests green, every proof script passing, no gate-decision behavior change, and documentation parity with the contributor handbook counterpart where documentation is touched | Feature request |
| S-017 | Approved gate condition: the default-branch push trigger runs both verification surfaces | Execution plan (A-001, approved Scope Gate condition) |
| S-018 | The plan delegates to this design: the verifier isolation and ordering mechanism, the orphan-run handling decision, and the advisory-standing encoding with the flip enacted per the ownership decision the tech lead records | Execution plan (A-004, T-001, T-006, T-010) |

## Objective

Desired structural outcome: a repository-level verification boundary exists at the hosting platform that gates change flow into the default branch on the two discovered surfaces, without touching any framework runtime behavior.

Architectural objectives:

- A verification boundary exercises both surfaces on every pull request and on every default-branch push, on both platforms. Traces to S-001, S-005, S-017.
- The composition of each surface is a function of the repository tree, established by scoped discovery, never by configuration listing files. Traces to S-002, S-010, S-012.
- Each verifier execution is an isolated, individually named unit of report: one verifier's crash or flake cannot change another verifier's reported result, and a failure names its verifier. Traces to S-004, S-009, S-013.
- Blocking authority is a single stable contract of named checks whose standing can move from advisory to required without structural change to the workflow. Traces to S-006, S-007, S-008, S-018.
- The boundary is purely additive to the framework: no gate-decision runtime surface changes. Traces to S-011.

In structural scope: the CI workflow definition, the check-name contract it exposes, the branch-protection required-checks configuration that references it, and the contributor documentation of the rollout policy.

Out of structural scope: the gate-decision runtime surfaces named by the ticket (F-012) — untouched; the unit tests and proof scripts themselves (F-001, F-002) — executed, never modified; execution of the orphan-run cleanup (F-014) — owned by the existing follow-up task; platforms beyond ubuntu and windows; verification surfaces or triggers beyond the two named. The out-of-scope list bounds the impact surface: this change adds a consumer of the framework's verification outputs and adds nothing inside the framework.

## Requirements Summary

Functional requirements:

- Trigger on every pull request and every default-branch push, both surfaces on both triggers (S-001, S-017).
- Surface 1: the unit-test suite located by standard-library discovery from the repository root (S-003).
- Surface 2: every `verify_*.py` under the framework payload runtime directory, discovered at job runtime, executed individually, each asserted to exit successfully with its passing verdict (S-004).
- A failing verifier fails CI naming that verifier (S-009).
- Newly added test or verifier files are covered with no CI configuration change (S-010, S-012).

Non-functional requirements:

- Isolation: one verifier's crash or flake does not change another verifier's reported result in the same run (S-013).
- Environment: NO_COLOR is not set in the CI environment (S-014).
- Rollout: ubuntu unit-test check required from day one; verifier checks and the windows checks advisory for week one, then required (S-006, S-007, S-008).
- No required check ships permanently red on account of the pre-existing orphan runs (S-015).

Acceptance intent: the ticket's two verbatim acceptance criteria (S-009, S-010), carried by the planner's acceptance criteria; cited from the execution plan rather than restated.

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | A unit-test suite of fourteen `test_*.py` files exists under `tests/`, runnable by standard-library test discovery from the repository root | Repository grounding: `tests/` listing; repository readme |
| F-002 | Seven proof scripts matching `verify_*.py` exist in the framework runtime directory: verify_manifests, verify_multi_phase, verify_recovery, verify_registry_coverage, verify_self_hosting, verify_validators, verify_vertical_slice | Repository grounding: framework runtime directory listing |
| F-003 | Committed mirrors of the proof scripts exist outside the framework payload, under the distributable package's bundled-payload runtime tree and under build output; the packaging metadata documents the bundling | Repository grounding: tree listing; packaging metadata |
| F-004 | Every proof script declares only optional command-line arguments and is runnable with none | Repository grounding: argument declarations in all seven scripts |
| F-005 | Every proof script exits 0 exactly when all of its checks pass, and prints a final summary line of the form "N/N checks passed" followed by its verdict token | Repository grounding: main routines of all seven scripts |
| F-006 | The success verdict token varies by script (PROVEN, RECOVERY PROVEN, CONFORMS, COVERED, SELF-HOSTING); every failure verdict token begins with "NOT " or is "NON-CONFORMANT" | Repository grounding: verdict lines of all seven scripts |
| F-007 | The recovery proof injects run directories and input files into the working tree's runs area during execution, removes them on normal completion (a keep flag retains them), and leaves them behind on abnormal termination | Repository grounding: recovery proof source; feature request |
| F-008 | The self-hosting proof's S8 run-accounting check fails when any framework run in the working tree's runs area is unaccounted for by a change proposal | Repository grounding: self-hosting proof source; feature request |
| F-009 | The package declares a Python floor of 3.10, and the framework runtime files require the YAML library, declared as a distribution dependency | Repository grounding: packaging metadata; repository readme |
| F-010 | No CI configuration exists in the repository today; there is no workflow directory | Repository grounding: tree listing (no `.github/` present) |
| F-011 | The run-status renderer suppresses color when NO_COLOR is set, and render tests assert colored output | Repository readme; feature request |
| F-012 | The framework runtime implements the gate-decision surfaces the ticket forbids changing: gate recording, gate-matrix semantics, producer exclusion, the approval requirement, and the human-block paths | Feature request (named surfaces); repository grounding: framework runtime directory |
| F-013 | Contributor documentation lives under `docs/` with a hand-maintained HTML handbook counterpart that must mirror documentation changes | Repository grounding: `docs/` listing; feature request definition of done |
| F-014 | Three pre-existing orphan run directories dated 2026-08-27 fail the self-hosting proof's S8 run-accounting check, and an existing follow-up task covers their cleanup | Feature request |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The repository is hosted on a platform whose CI reads workflow definitions from `.github/workflows/`, provides ubuntu and windows hosted runners, supports matrix fan-out from a discovery step's output with per-job check names, and supports branch protection that requires named checks | The whole topology, the check-name contract, and the advisory encoding bind to this hosting model | Workflow location, matrix, failure naming, and blocking mechanism all re-scope; M-001 and M-002 are re-designed | omn-tech-lead |
| A-002 | Hosted runner images do not set NO_COLOR by default | The unit-test surface must satisfy C-007 without extra machinery | An explicit environment normalization is added to the workflow design as a follow-up change | omn-qa (environment review during verification) |
| A-003 | The existing orphan-cleanup follow-up task can land on the default branch before the end of the advisory week | The clean-first handling in D-003 conditions the flip on it | The flip is deferred by P-007's precondition rather than enacted red; the rollout policy's week-one date slips | omn-tech-lead |
| A-004 | The three orphan run directories are the only pre-existing repository state failing any verifier at the merge revision | The claim that the verifier surface can be green at the flip rests on it | Additional pre-existing failures surface during the advisory week and must be resolved, or the flip is deferred | omn-qa (advisory-week evidence) |
| A-005 | A dedicated hosted runner per verifier gives the recovery proof's backoff-deadline assertion enough CPU headroom for an acceptable flake rate | The recovery proof is timing-sensitive (S-013); isolation must not itself induce flakes | The required standing of the affected verifier check is indefensible at the flip; the plan's deferred re-evaluation of the verifier-required policy triggers | omn-qa (advisory-week observation) |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | functional | The workflow triggers on every pull request and every default-branch push, and both triggers run both surfaces | Hard | S-001, S-017 |
| C-002 | structural | Both surfaces are located by discovery; no step enumerates test or verifier files by name for inclusion | Hard | S-002, S-012 |
| C-003 | functional | Every discovered verifier executes individually; a failure fails CI naming that verifier | Hard | S-004, S-009 |
| C-004 | structural | The platform matrix is ubuntu and windows | Hard | S-005 |
| C-005 | structural | Additive only: no gate-decision runtime surface changes; at most a small discovery helper | Hard | S-011, F-012 |
| C-006 | operability | One verifier's crash or flake must not change another verifier's reported result in the same run | Hard | S-013, F-007, F-008 |
| C-007 | operability | The CI environment does not set NO_COLOR | Hard | S-014, F-011 |
| C-008 | quality-attribute | Staged rollout: ubuntu unit-test check required from day one; verifier checks and windows checks advisory for week one, then required; advisory failures must remain visible | Hard | S-006, S-007, S-008 |
| C-009 | quality-attribute | No required check may be permanently red on account of the pre-existing orphan runs; the handling is stated in the design | Hard | S-015, F-014 |
| C-010 | functional | A newly added test or verifier file is covered with no CI configuration change, including no blocking-configuration change | Hard | S-010 |
| C-011 | operability | Runner-minute cost and queue latency per run stay proportionate to the repository's change rate | Negotiable | Derived from S-005 and the fan-out in this design |
| C-012 | structural | The verifier discovery scope is the framework payload runtime directory only; the bundled mirrors and build output are outside the verification surface | Hard | S-004, F-003 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | CI verification workflow (new definition under `.github/workflows/`) | extension | F-010, A-001 | Check-name contract; pull-request and default-branch push trigger surface | confirmed |
| M-002 | Branch-protection required-checks configuration (hosting platform settings) | extension | A-001 | References into the check-name contract | speculative |
| M-003 | Unit-test suite under `tests/` | no-change-verified | F-001 | none (executed, not modified) | confirmed |
| M-004 | Proof scripts in the framework runtime directory | no-change-verified | F-002, F-004 | none (executed, not modified) | confirmed |
| M-005 | Gate-decision runtime surfaces (gate recording, gate-matrix semantics, producer exclusion, approval requirement, human-block paths) | no-change-verified | F-012 | none | confirmed |
| M-006 | Bundled-payload mirror and build-output copies of the proof scripts | no-change-verified | F-003 | none (excluded by C-012 discovery scope, not by name enumeration) | confirmed |
| M-007 | Packaging metadata (interpreter floor and dependency declaration) | no-change-verified | F-009 | none (consumed by CI provisioning, not modified) | confirmed |
| M-008 | Contributor documentation set, including the handbook counterpart | extension | F-013 | rollout-policy pages and their HTML counterpart | confirmed |
| M-009 | Pre-existing orphan run directories in the runs area | operational-impact | F-008, F-014 | read by the self-hosting proof's run-accounting check | confirmed |

M-003 through M-007 are recorded as `no-change-verified` because a reader would reasonably expect a CI change to touch tests, verifiers, runtime, mirrors, or packaging; it touches none of them. M-009 carries `operational-impact` because its presence turns one verifier check red until the cleanup owned elsewhere lands (D-003); this change does not modify it. The only boundary crossing in the impact set is between the repository and the hosting platform's check surface (M-001 to M-002), which is where D-002 concentrates.

### 5.2 Options Considered

Impact surface counts modules with contract-change or dependency-change. Reuse leverage counts capabilities satisfied by reuse-as-is or reuse-extended in section 7. Migration burden counts contract-affecting changes requiring a transition strategy. Quality attributes assesses C-008's visibility requirement plus C-003's failure-naming strength and C-006's isolation strength.

| Option | Structural change | C-002 discovery | C-006 no-cascade | C-008 rollout visibility | C-009 no permanent red | Impact surface | Reuse leverage | Quality attributes | Migration burden | Operability cost | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | Discovery-fed per-verifier matrix fan-out: a discovery step globs the payload runtime directory and emits the list as job output; one matrix job per verifier per platform, each on a fresh runner and fresh checkout; stable per-platform fan-in checks aggregate; blocking authority lives solely in the required-checks list; orphans cleaned before the flip (D-003) | Satisfied (scoped glob) | Satisfied structurally (no shared workspace exists between verifiers) | Satisfied (advisory checks show red without blocking; per-verifier check names) | Satisfied (flip conditioned on cleanup, P-006/P-007) | 0 | 8 | Full: naming by check name, isolation by runner boundary, advisory failures visible | 1 (check-name contract, section 6) | High: about 18 jobs per run | Selected |
| O-002 | Sequential consolidated loop: one verifier job per platform iterates the discovered scripts in a defined order with the mutating recovery proof forced last and an in-job workspace reset between scripts; failure naming via log annotations; advisory standing encoded as the workflow's per-job failure-tolerance flag for week one, removed by a workflow edit at the flip; orphans cleaned before the flip | C-002 satisfied for inclusion (scoped glob); ordering embeds one script's name | C-006 conditionally satisfied: holds only while the ordering rule and reset logic are maintained; a future mutating verifier is not auto-ordered safely | C-008 violated in spirit: the failure-tolerance flag reports a failing advisory job as a passing check, hiding week-one failures | C-009 satisfied (same cleanup condition) | 0 | 6 | Partial: annotation naming only; isolation is ordering-conditional; advisory failures masked green | 2 (check-name contract, plus the flip is a workflow semantic change) | Low: 4 jobs per run | Rejected on C-006's conditional isolation and C-008's masked advisory visibility: loses at reuse leverage and quality attributes (see 5.3) |
| O-003 | Curated per-verifier jobs: one hardcoded workflow job per proof script | Violated: files enumerated by name; a new verifier requires a CI edit | Satisfied | Satisfied | Satisfied | 0 | 6 | Full naming, full isolation | 1 | High | Eliminated on C-002 (and C-010) |
| O-004 | O-001 topology with advisory-window-only orphan handling: the run-accounting verifier stays red through the advisory week and the flip proceeds by exempting or accepting the red required check | Satisfied | Satisfied | Satisfied | Violated: at the flip the required verifier surface is permanently red, or the red verifier is exempted by name, which is curation | 0 | 8 | Full naming and isolation; policy integrity broken | 1 | High | Eliminated on C-009 (exemption path also violates C-002) |

### 5.3 Selected Approach

- Selected: O-001.
- Structural change: one new workflow definition (M-001) establishing, per trigger and per platform: (1) a unit-test job running the standard-library discovery invocation the ticket names from the repository root, in an environment where NO_COLOR is absent; (2) a discovery step that globs `verify_*.py` scoped to the framework payload runtime directory (C-012) and publishes the discovered list as its output — expressed inline in the workflow using the same interpreter the jobs already require, so no helper file is added (see section 7); (3) a matrix of verifier jobs fanned out from that output, one job per discovered verifier per platform, each on a fresh runner with a fresh checkout, executing its verifier with no arguments (F-004) and asserting success as exit code 0 plus the script's own all-checks-passed summary line (F-005, F-006) — a generic assertion, never a per-script verdict-token list; (4) one stable fan-in check per platform that reports success only when every discovered verifier job succeeded and reports failure — never a skip — when any was cancelled; (5) blocking authority carried exclusively by the branch-protection required-checks list (M-002), which at merge names only the ubuntu unit-test check, and at the flip additionally names the two fan-in checks and the windows unit-test check (D-002).
- Rationale: O-001 and O-002 both survive the hard constraints; O-001 wins at criterion 3 (reuse leverage 8 versus 6: O-002 replaces the platform's matrix fan-out and fresh-runner isolation with bespoke loop-and-reset logic) and the win is corroborated at criterion 4 (quality attributes: per-verifier check names satisfy S-009 in the strongest available form; runner-boundary isolation satisfies C-006 structurally rather than conditionally, which is decisive given F-007 and F-008 — a crashed recovery proof's injected runs exist only in its own discarded workspace and can never reach the self-hosting proof's S8 check; advisory failures stay visibly red, which C-008's observation purpose requires). Verifier ordering thereby becomes moot: no execution order exists to maintain, so no ordering rule can decay when a verifier is added (C-010).
- Highest-scoring rejected alternative and why it lost: O-002, the sequential consolidated loop. It costs roughly a quarter of the runner minutes and would satisfy today's no-cascade requirement through the recovery-last ordering rule. It lost because its isolation guarantee is conditional on maintained ordering and reset logic that silently decays when a future mutating verifier is added, its failure naming is annotation-grade rather than check-grade, and its advisory encoding masks failing advisory jobs as green checks, defeating the advisory week's evidentiary purpose and weakening the flip decision that R-001 depends on.
- Tradeoffs accepted: O-001 spends materially more hosted-runner capacity per run (about 18 jobs versus 4), accepted against negotiable C-011 and mitigated by cancelling superseded runs of the same pull request (section 8, R-006). The per-verifier matrix also produces dynamic check names for individual verifiers; blocking therefore binds to the stable fan-in names, never to per-verifier names (D-002), which is what keeps C-010 satisfied at the blocking layer.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | The verifier surface is a discovery-fed per-verifier matrix fan-out with a fresh runner and checkout per verifier and stable per-platform fan-in checks; isolation is by runner boundary, and no execution ordering exists | Yes | ADR D-001, status Proposed |
| D-002 | Blocking authority lives solely in the branch-protection required-checks list referencing the stable check names; advisory standing is encoded as absence from that list, never as the per-job failure-tolerance flag; the flip is a settings-only change enacted by the owner the tech lead's decision names | Yes | ADR D-002, status Proposed |
| D-003 | Orphan-run handling: clean-first — the existing cleanup follow-up task lands before the flip, with the advisory week as buffer; the flip precondition is a default-branch run at the flip revision showing the self-hosting proof passing | Yes | ADR D-003, status Proposed |
| D-004 | The unit-test surface uses the discovery invocation the ticket names, from the repository root, on both platforms, provisioned at the packaging floor (Python 3.10) with the declared YAML dependency installed (F-009); the workflow declares no NO_COLOR value anywhere (C-007) | No | Inline; forced by S-003, C-004, C-007 and F-009 |
| D-005 | Verifier success assertion is generic: exit code 0 plus the script's own all-checks-passed summary (F-005), guarded against the negative verdict markers (F-006); no per-script verdict-token list exists | No | Inline; forced by F-005, F-006 and C-002's no-curation spirit |
| D-006 | Discovery scope is rooted at the framework payload runtime directory, so the bundled mirrors and build output (M-006) are excluded inherently, not by name enumeration | No | Inline; forced by C-012 and F-003 |
| D-007 | No separate discovery helper file is committed; discovery is a single inline expression in the workflow | No | Inline; see section 7 rejection rationale |

## API and Data Model Impact

- API changes: none to any application or framework runtime interface. No module in 5.1 carries `contract-change`. The change introduces one new externally referenced interface: the check-name contract between the workflow (M-001) and the branch-protection required-checks list (M-002).
- Contract compatibility notes for the check-name contract (D-002):
  - Current shape: no CI checks exist (F-010); branch protection references nothing.
  - Target shape: stable check names — one unit-test check per platform and one verifier fan-in check per platform — plus dynamic per-verifier check names that are informational only and never referenced by blocking configuration.
  - Compatibility approach: purely additive; nothing existing is renamed or removed.
  - Coexistence period: the advisory week, during which the fan-in and windows checks exist and report but are not required.
  - Retirement condition: advisory standing retires at the flip, when the fan-in checks and the windows unit-test check enter the required list (P-007).
  - Rollback position: remove the added names from the required list to return to the pre-flip standing, or remove the workflow definition to return the repository to its current state; no data or runtime behavior is affected in either direction.
- Schema or migration changes: none identified. The change writes no persistent data and performs no migration; the only stateful surface it reads is the runs area, which the orphan cleanup (owned by the existing follow-up task, F-014) modifies under D-003.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Unit-test discovery and execution | Standard-library unittest discovery over `tests/` | reuse-as-is | F-001 establishes the suite is discoverable from the repository root; S-003 names the invocation |
| Verifier pass/fail authority | The proof scripts' own exit-code and summary-verdict contract | reuse-as-is | F-005 and F-006: the scripts already decide and report; CI asserts their contract and re-implements nothing |
| Verifier file discovery | The interpreter's standard-library globbing, scoped per C-012 | reuse-as-is | The jobs already require the interpreter (F-009); one expression suffices on both platforms with no shell divergence |
| Verifier file discovery | A dedicated discovery helper script committed to the repository | rejected | The need is a single scoped glob expression; a committed helper adds a file that must also be mirrored into the bundled payload (F-003), creating sync burden, and would itself need test coverage — disproportionate to the capability (D-007) |
| Per-verifier fan-out with named results | Hosting platform matrix fan-out from a discovery step's output, with per-job check names | reuse-as-is | A-001; gives S-009's failure naming as first-class check names with no bespoke reporting |
| Workspace isolation between verifiers | Fresh hosted runner and fresh checkout per matrix job | reuse-as-is | A-001; makes C-006 structural against F-007/F-008 with zero custom logic |
| Workspace isolation between verifiers | In-job workspace reset between sequential verifier executions | rejected | Bespoke, ordering-conditional logic whose guarantee decays silently when a mutating verifier is added; evaluated and outscored as part of O-002 |
| Blocking authority | Branch-protection required-checks list | reuse-as-is | A-001; the platform's native, auditable blocking mechanism; the flip becomes a settings-only change |
| Advisory (visible, non-blocking) standing | The workflow's per-job failure-tolerance flag (the mechanism the task directive names as continue-on-error) | rejected | It reports a failing advisory job as a passing check, hiding exactly the week-one failures C-008's observation purpose and R-001's evidence gathering need; advisory standing is achieved by omission from the required list instead (D-002) |
| Dependency provisioning | Package-manager installation of the declared dependency set at the declared floor | reuse-as-is | F-009: the floor and the YAML dependency are already declared by packaging metadata; CI consumes, never redefines |
| Orphan-run cleanup | The existing cleanup follow-up task | reuse-as-is | F-014: cleanup work already has an owner and a task; D-003 sequences it, this change never performs it |
| A stable, single blocking name per verification surface | Existing aggregation check in the repository's CI surface | none-found | Search basis: the repository tree carries no CI configuration at all (F-010), and the supplied context names no existing aggregation facility; the fan-in checks and the workflow definition are therefore new structure, licensed by this row and F-010 |

The `none-found` row licenses the only new structure in this design: the workflow definition itself and its two fan-in checks.

## Operational Considerations

- Logging and observability updates: every verifier execution is an individually named check (M-001, C-003), so the CI surface names a failing verifier without log spelunking; each verifier job additionally surfaces the script's own summary line (F-005) in its log, and the failure path emits a log annotation naming the script for the pull-request view. Advisory-week failures are visibly red by design (D-002, C-008).
- Error handling strategy: the fan-in checks evaluate every upstream verifier job's result explicitly and report failure — never skip — when any upstream job failed or was cancelled (M-001, C-006), because a skipped check neither blocks nor informs. A verifier crash is contained to its own runner and workspace (D-001, F-007), so the self-hosting proof's S8 check (F-008) can never observe another job's injected runs. The unit-test jobs and verifier jobs are independent: neither surface's failure suppresses the other's report (C-001).
- Security considerations: pull-request triggers execute repository code from the merge candidate on hosted runners; the verification jobs therefore use no secrets and declare least-privilege read-only repository access (M-001, R-009). No gate-decision runtime surface is touched (M-005, C-005, F-012), so no approval or human-block path can be weakened by this change. Branch-protection administration (M-002) stays with the repository administrator; this design grants no new write authority to anything.
- Performance considerations: the fan-out costs about 18 hosted jobs per run against negotiable C-011; superseded runs of the same pull request are cancelled to bound queue pressure (R-006). The recovery proof's timing sensitivity (S-013) is mitigated by giving it a dedicated runner with no concurrent sibling load (D-001, A-005); its flake rate is measured during the advisory week before its check becomes required (P-007, R-001). No performance claim is made beyond these two recorded constraints.

## Delivery Plan

The supplied execution plan's tasks are consumers of this design: T-001 is realized by this package, and its delegated isolation-and-ordering mechanism binds through P-003; T-010's orphan-run handling binds through P-006 under D-003. The `Binds` column states which planner tasks each constraint binds. No task identifiers are created here.

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The stable check-name contract (per-platform unit-test names and per-platform fan-in names) is defined before any job is built | M-001, M-002 | none | Branch protection, the flip, and the documentation all bind to these names; defining them after the jobs forces renames that detach blocking configuration (R-005) | T-002, T-003, T-004, T-006 |
| P-002 | Both discovery mechanisms exist as scoped globs, demonstrably enumerating no file by name, before either surface's jobs are considered complete | M-001, M-003, M-004, M-006 | none | C-002 and C-012 are properties of the discovery mechanism itself; retrofitting discovery onto enumerated jobs re-creates the curated-list failure mode | T-002, T-003, T-008 |
| P-003 | Per-verifier isolation (fresh runner, fresh checkout, no shared workspace, no execution ordering) is structurally in place before the verifier surface reports results anywhere | M-001, M-004 | P-002 | C-006 must hold from the first reported run: a cascade observed before isolation exists poisons the advisory-week evidence the flip depends on | T-001, T-003, T-009 |
| P-004 | The job environment demonstrably carries no NO_COLOR value before the unit-test surface reports | M-001, M-003 | none | C-007: a spuriously red unit-test check on day one blocks every pull request, because that check is required from merge | T-002, T-009 |
| P-005 | At merge, the required-checks list names only the ubuntu unit-test check; the fan-in and windows names exist but stay out of the list | M-002 | P-001 | C-008's day-one staging is a property of the blocking configuration; listing verifier checks before the advisory week violates the approved rollout | T-004, T-006 |
| P-006 | The orphan cleanup lands on the default branch, and a default-branch run shows the self-hosting proof passing, before the flip | M-009, M-002 | P-003 | C-009 and D-003: the flip precondition is observable only once the verifier surface reports in isolation | T-007, T-010 |
| P-007 | The flip — adding the two fan-in checks and the windows unit-test check to the required list, as a settings-only change with no workflow edit — is enacted only after advisory-week evidence exists and P-006 holds | M-002 | P-005, P-006 | D-002 and C-008: required standing without flake-rate evidence and a green run-accounting verifier ships a red or indefensible required check | T-007, T-009 |
| P-008 | Contributor documentation of the delivered check names, standings, flip mechanism, and orphan handling — with handbook-counterpart parity — reflects the encoded state, not the intended state | M-008 | P-005 | S-016 and F-013: documentation of names and standings written before they are encoded documents intentions and drifts | T-005 |

### Test Strategy Focus Areas

For omn-qa (feeding the plan's validation-coverage and verification tasks): forced single-verifier regression demonstrating CI failure naming that verifier (S-009); verifier-execution count equal to the scoped-glob file count at the same revision (C-012); file-addition pickup for both surfaces with zero configuration change, including zero blocking-configuration change (C-010); forced-failure no-cascade comparison — crash one verifier, including the recovery proof, and compare every other verifier's result to a baseline at the same revision (C-006); environment review confirming NO_COLOR absent on both platforms and render tests green (C-007, A-002); demonstration that a failing advisory check is red yet non-blocking during week one (C-008, D-002); curation scan of the workflow for any enumerated test or verifier filename (C-002); review confirmation that no gate-decision runtime surface changed (C-005, M-005); fan-in behavior under upstream cancellation (never reports success or skip).

### Rollout and Rollback

- Rollout: merge with the day-one required set (P-005); observe the advisory week, during which verifier and windows failures are visible but non-blocking and the orphan cleanup lands (P-006); enact the flip as a settings-only change per P-007, recorded by the owner and mechanism the tech lead's decision names (Q-001).
- Rollback: at any stage, removing check names from the required list restores the prior blocking standing, and removing the workflow definition restores the repository's current state (F-010); both are non-destructive, and neither touches framework runtime behavior (C-005).

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | operability | The recovery proof's backoff-deadline assertion fails under hosted-runner CPU variance despite a dedicated runner (A-005 false), especially on windows | Spurious red verifier checks; the flip for the affected checks becomes indefensible | medium | M-004, D-001, P-007 | Advisory week measures the flake rate before required standing (P-007); if indefensible, the plan's deferred re-evaluation of the verifier-required policy triggers rather than flipping | omn-tech-lead |
| R-002 | delivery | The orphan cleanup task does not land before the end of the advisory week (A-003 false) | The flip precondition P-006 is unmet at the planned date | medium | P-006, D-003 | P-007 defers the flip until the precondition holds, rather than enacting a red required check; slippage is recorded with the flip record | omn-tech-lead |
| R-003 | structural | A-001 is false: the hosting platform lacks the workflow directory, the runner matrix, matrix-from-output fan-out, or required named checks | M-001 and M-002 re-scope; the topology and blocking mechanism are re-designed | low | M-001, M-002 | Confirm A-001 before the implementation wave begins; this design's option table records the alternatives to re-derive from | omn-tech-lead |
| R-004 | operability | A runner image sets NO_COLOR (A-002 false) | Render tests fail spuriously and the day-one required unit-test check blocks every pull request | low | M-001, P-004 | Environment review is an explicit verification focus; if set, an environment normalization is added to the workflow design as a bounded follow-up | omn-qa |
| R-005 | contract | A workflow edit renames a job in the required-checks list | The renamed check is forever "expected" and blocks every pull request, or blocking silently lapses | medium | M-001, M-002, D-002 | The check-name contract is recorded in section 6 and P-001 defines names first; documentation (P-008) marks them as a contract; structural review treats a rename as a contract change | omn-dev-2-reviewer |
| R-006 | operability | Fan-out volume saturates hosted-runner capacity at peak change rate (C-011) | Delayed pull-request feedback across the repository | medium | M-001, D-001 | Superseded runs of the same pull request are cancelled; C-011 is negotiable and the cost is an accepted, recorded tradeoff of the O-001 selection | omn-tech-lead |
| R-007 | delivery | Pre-existing failures beyond the three orphans exist at the merge revision (A-004 false) | The verifier surface is red at the flip for reasons the orphan cleanup does not cure | medium | P-007, M-004 | The advisory week exists to surface exactly this; P-007's precondition (green self-hosting run at head) defers the flip until resolved | omn-qa |
| R-008 | structural | A future verifier is written to depend on another verifier having run first | Under D-001 isolation it fails or passes spuriously, since no ordering exists | low | D-001, M-004 | The self-containment expectation (runnable alone with no arguments, F-004) is recorded here and in the documentation as a structural expectation for new verifiers | omn-dev-2-reviewer |
| R-009 | security | Verification jobs later acquire secrets or write permissions while still executing pull-request code | Untrusted merge-candidate code can exfiltrate or act with elevated rights | low | M-001, D-001 | Design constraint: verification jobs carry no secrets and least-privilege read-only access (section 8); structural review treats any permission widening in this workflow as a security-relevant contract change | omn-dev-2-reviewer |

## Estimate and Confidence

- Overall: M (confidence: medium).
- Breakdown: P-001 S — naming is design-bound and small; P-002 S — two scoped discovery mechanisms; P-003 M — the matrix fan-out with fan-in result evaluation is the largest structural piece; P-004 XS — an environment guarantee plus its review; P-005 S — initial blocking configuration; P-006 S — sequencing an externally owned cleanup and observing one green run; P-007 S — a settings-only change gated on recorded evidence; P-008 S — documentation with handbook parity.
- Scope assumptions: the estimate covers the eight sequencing constraints and assumes A-001 holds and the seven existing verifiers remain zero-argument runnable (F-004); it excludes the orphan cleanup work itself, any change to tests or verifiers, and the dependent backlog tickets' future extensions of this workflow.
- Uncertainty drivers: A-001 (hosting facilities, R-003) and A-005 (recovery-proof flake rate on hosted runners, R-001) dominate; windows runner variance is the single largest unknown and is exactly what the advisory soak window measures. Confidence stays medium, not high, because M-002 is speculative until A-001 is confirmed.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Who enacts the advisory-to-required flip, and where is the flip recorded? The mechanism is fixed by D-002 (settings-only change to the required list); the enactor and record location are the tech lead's decision, per the plan's dedicated decision task | No | omn-tech-lead | M-002, P-007, D-002 | Named enactor and record location: the flip proceeds on schedule per P-007. Unrecorded: R-005-adjacent drift risk and the plan's stall risk materialize — gating stays advisory indefinitely |
| Q-002 | Is A-001 confirmed — does the hosting platform provide the workflow directory, both runner images, matrix-from-output fan-out, and required named checks? | No | omn-tech-lead | M-001, M-002 | Confirmed: this design stands as selected. Not confirmed: O-001's mechanisms re-derive against the actual platform facilities from the recorded option table; the surfaces and constraints are unchanged |
| Q-003 | When within the advisory week does the existing orphan-cleanup follow-up task land (A-003)? | No | omn-tech-lead | P-006, D-003 | Lands in-week: the flip proceeds at the planned date. Lands late: P-007 defers the flip until P-006 holds; the rollout date slips and the slippage is recorded with the flip record |

All entries are non-blocking, so package status is `complete`. Decision records D-001, D-002, and D-003 remain at status Proposed and require Design Gate acceptance before the implementation-facing constraints P-001 through P-003 are built against.

## Sign-off

- Architect: architect (producing role; excluded from accepting this package under the producer exclusion rule in `workflows/workflow-gate-matrix.md`)
- Design Gate owners: omn-architect, omn-tech-lead — accepting owner: omn-tech-lead, named explicitly because the architecture role produced this package
- QA: omn-qa (verification focus areas in the Delivery Plan)

Lines are left unsigned by the producing agent. No implementation work was performed and no external system was accessed in producing this package; all context came from the supplied inputs and the frozen repository snapshot.
