```yaml
design:
  designId: CKA-02-technical-design
  changeReference: CKA-02
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/cka-02-feature-request.md
    - type: execution-plan
      reference: runs/run-e0dba6763475/states/execution-planning/artifacts/execution-plan.md
  producedBy: architect
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  decisionRecords: [D-001, D-002]
  consumesPlan: runs/run-e0dba6763475/states/execution-planning/artifacts/execution-plan.md
  inputDigest: sha256:f7ffdf9d3e4b07e7b5b0242843ac6ca7
  contextDigest: sha256:ea8b3b5e9812546f9b4054458bb8143e
```

## Metadata

- Feature or Change ID: CKA-02 (ticket CKA-02 in the adoption backlog under docs/)
- Author: architect
- Reviewers: omn-architect, omn-tech-lead
- Last Updated: 2026-09-03

## Objective

- Desired outcome: a non-editable installation of the built distribution is
  self-contained — the installed package itself carries a resolvable copy of the
  framework payload — while every existing installation mode keeps its current
  resolution behaviour and its current failure guidance, byte-for-byte in precedence
  terms. Traces to S-001, S-004, S-005.
- Architectural objectives:
  1. The distribution artifact carries the complete framework payload tree — all
     managed directories plus the seed directories, filtered by the installer's
     exclusion patterns — at a location resolvable from the installed package.
     Traces to S-004.
  2. The source-resolution contract gains exactly one new candidate, appended
     strictly after the existing candidates, validated by the existing
     framework-tree check, with the existing failure message retained when no
     candidate resolves. Traces to S-005, S-010.
  3. The distribution metadata (source and binary file lists) derives from the new
     packaging configuration with zero discrepancies. Traces to S-006.
- In scope: the packaging configuration (M-001), a bundled payload data subtree
  inside the `omn_agent` package (M-003), the `find_source` candidate order in
  `omn_agent/source.py` (M-002), regenerated distribution metadata (M-004), and the
  regression surface those changes create (M-008).
- Out of scope: any change to gate-decision recording, gate-matrix semantics,
  producer exclusion, approval-requirement enforcement, or any human-block path
  (S-009); the dependent continuous-integration gating ticket CKA-03 (S-012); any
  reordering of source-resolution precedence for existing users (S-010); any change
  to the installer's classification, dry-run, or validation semantics beyond what
  the decided parity-assurance level requires (S-017). The out-of-scope list is
  non-empty because the change touches the shared source-resolution boundary.

## Requirements Summary

### 3.1 Statement Register

Statements are normalized from the supplied feature request (S-001 through S-012,
document order) and the supplied execution plan (S-013 through S-017, document
order).

| ID | Statement | Mapped to |
|---|---|---|
| S-001 | A non-editable install of the built wheel produces a CLI that cannot install: the framework payload is not packaged into the wheel | Objective; M-001, M-003 |
| S-002 | `find_source` only looks for an explicit source or a framework tree next to the package checkout | F-003; M-002 |
| S-003 | Every fresh-environment user must pass the `--source` option to a framework checkout | Objective; C-009 |
| S-004 | Deliverable 1: package the framework payload into the wheel (packaging configuration package data, or a build-inclusion directive file) so a non-editable build carries the full payload tree — all managed plus seed directories, subject to the installer's exclusion patterns | C-003, C-004; M-001, M-003; O-001, O-002 |
| S-005 | Deliverable 2: extend `find_source` to resolve the bundled payload from the installed package location as a fallback after the existing candidates, keeping the existing error message actionable | C-001, C-005, C-006; M-002; D-002 |
| S-006 | Deliverable 3: regenerate the stale distribution metadata so source and binary file lists match the new packaging configuration | C-007; M-004 |
| S-007 | Acceptance: in a clean environment, a non-editable install of the wheel followed by initialize, install, and validate succeeds with no explicit source option | C-009 |
| S-008 | Acceptance: a dry-run install enumerates the same payload file count as an editable install | C-008; Q-001 |
| S-009 | Constraint: additive change only; the named gate-behavior areas must not be altered | C-002 |
| S-010 | Constraint: source-resolution precedence must not change for existing users; explicit source and checkout-adjacent tree keep winning | C-001 |
| S-011 | Constraint: definition of done — test suite green, all proof scripts PROVEN, no gate-decision behavior change, handbook matches touched docs | C-010 |
| S-012 | Priority highest, Phase 1; blocks CKA-03 together with CKA-01 | Out of scope (CKA-03 excluded); context |
| S-013 | The plan assigns the packaging-mechanism decision (T-001) and the resolution-fallback contract (T-003) to this design phase, with tasks T-001 through T-010 as consumers | Delivery Plan Binds column |
| S-014 | The two candidate packaging mechanisms named in the request are stated preferences, not mandates; either satisfies scope and the design decision selects one | O-001, O-002; D-001 |
| S-015 | The packaging decision must enumerate the packaged directory set (managed plus seed) and record the authoritative exclusion-pattern set | P-001; C-003, C-004 |
| S-016 | The resolution contract must state the candidate order with the bundled payload strictly last, where the bundled payload resides under the selected mechanism, and the retained failure guidance | P-002; D-002 |
| S-017 | The parity-assurance level (file-count parity vs file-set identity) is an open question owned by omn-product-owner, resolved by a plan task ahead of validation design; non-blocking | Q-001; P-006 |

### 3.2 Requirements

- Functional requirements:
  - The built distribution carries the complete filtered framework payload tree (S-004).
  - Source resolution falls back to the bundled payload only after the existing
    candidates, from the installed package location (S-005).
  - Distribution metadata matches the new packaging configuration (S-006).
  - A clean-environment non-editable install initializes, installs, and validates
    with no explicit source option (S-007).
- Non-functional requirements:
  - Dry-run payload parity between non-editable and editable installs at the
    assurance level decided upstream (S-008, S-017).
  - Regression posture: suite green, proof scripts PROVEN, no gate-decision
    behavior change, handbook synchronized where docs are touched (S-011).
- Acceptance criteria: supplied verbatim by the ticket and carried by the execution
  plan's acceptance criteria 1 through 5; cited, not restated (S-007, S-008,
  S-010, S-011).

## Current-State Assumptions and Constraints

### 4.1 Facts

| ID | Fact | Established by |
|---|---|---|
| F-001 | The packaging configuration declares a setuptools build backend and exactly one package, `omn_agent`, with no package-data and no data-files declaration | Repository code: `pyproject.toml` |
| F-002 | No build-inclusion directive file (`MANIFEST.in`) exists at the repository root | Repository root file inventory |
| F-003 | `find_source` probes, in order: an explicit `--source` path (accepting the framework tree itself or a repository containing one under either recognized framework-tree directory name), and otherwise a framework tree next to the package checkout under the same two directory names — the repository's dot-prefixed framework payload directory name, and the dot-prefixed directory name held by the `FRAMEWORK_DIR` constant in `omn_agent/repo.py`. No other candidate exists | Repository code: `omn_agent/source.py`, `find_source` |
| F-004 | When no candidate resolves, `find_source` raises a typed error with exit class INVALID_TARGET and a hint naming the `--source` remedy and the files a framework checkout must contain | Repository code: `omn_agent/source.py`, `find_source` |
| F-005 | A directory qualifies as a framework tree only when all four required source files resolve: `runtime/framework_runtime.py`, `runtime/state_engine.py`, `registry/agents.yaml`, `registry/workflows.yaml` (payload-relative paths) | Repository code: `omn_agent/source.py`, `REQUIRED_SOURCE_FILES`, `_is_framework_tree` |
| F-006 | The managed directory set is exactly ten directories (`runtime`, `registry`, `config`, `templates`, `agents`, `workflows`, `skills`, `commands`, `domain-model`, `validation`) and the seed directory set is exactly two (`context`, `memory`) | Repository code: `omn_agent/source.py`, `MANAGED_DIRS`, `SEED_DIRS` |
| F-007 | The installer's exclusion-pattern set has exactly six entries — `__pycache__`, `*.pyc`, `*.pyo`, `.DS_Store`, plus the installer's backup-file suffix pattern and its temporary-file suffix pattern — applied by the payload walk to file names and to every ancestor path segment | Repository code: `omn_agent/source.py`, `EXCLUDE_PATTERNS`, `_walk` |
| F-008 | The installer calls `find_source` once per install or upgrade and rejects a source that resolves to the same path as the target framework directory | Repository code: `omn_agent/installer.py`, `_install_like` |
| F-009 | The installed target framework directory is the dot-prefixed directory named by the `FRAMEWORK_DIR` constant under the target repository, resolved by the repository module independently of source resolution | Repository code: `omn_agent/repo.py`, `FRAMEWORK_DIR`, `framework_root` |
| F-010 | The existing distribution metadata lists only package modules, project files, metadata files, and tests; no framework payload path appears in it | Repository file: `omn_agent.egg-info/SOURCES.txt` |
| F-011 | Validation resolves the installed layout from the target directory only and never consults the package's own location | Repository code: `omn_agent/validator.py`, `run_validation` |
| F-012 | The existing test suite exercises install and upgrade exclusively through explicit `--source` paths | Repository code: `tests/test_omn_agent.py` |
| F-013 | Payload enumeration walks the managed directories of whatever source directory it is given and fails typed when the result is empty; seed enumeration walks the seed directories of the same source | Repository code: `omn_agent/source.py`, `enumerate_payload`, `enumerate_seeds` |

### 4.2 Assumptions

| ID | Assumption | Why needed | Impact if false | Confirmed by |
|---|---|---|---|---|
| A-001 | The build backend carries files into the binary distribution at an importable, resolvable location only when they reside under a declared package directory; a root-level dot-prefixed directory included through source-distribution directives alone does not land at a location resolvable from the installed package in a non-editable install | The mechanism selection between O-001 and O-002 turns on it | O-002 becomes viable; the option evaluation is re-run and D-001 is revisited before P-003 begins | omn-dev-1-implement |
| A-002 | The authoritative payload tree at build time is the framework payload directory at the repository root, and its managed-plus-seed subtree per F-006 is the complete set the bundle must mirror | Bounds what the bundled subtree (M-003) must contain | The packaging enumeration is re-scoped and the completeness check (C-003) is re-baselined | omn-tech-lead |
| A-003 | Keeping the bundled payload subtree synchronized with the authoritative payload tree is achievable within the standard build procedure without touching any gate-behavior path | The bundled copy is only correct while it mirrors the authoritative tree | Drift ships stale payloads to every non-editable install; a sync-verification obligation is added ahead of P-007 | omn-dev-1-implement |

### 4.3 Constraints

| ID | Class | Constraint | Hard or negotiable | Source |
|---|---|---|---|---|
| C-001 | structural | Source-resolution precedence is unchanged: explicit `--source` first, then the checkout-adjacent tree, then — and only then — the bundled payload | Hard | S-005, S-010, F-003 |
| C-002 | structural | Additive change only: gate-decision recording, gate-matrix semantics, producer exclusion, approval-requirement enforcement, and every human-block path are untouched | Hard | S-009 |
| C-003 | functional | The non-editable build carries the complete payload tree: every managed directory plus both seed directories per F-006 | Hard | S-004, S-015, F-006 |
| C-004 | functional | The carried payload contains zero files matching the installer's exclusion-pattern set per F-007 | Hard | S-004, S-015, F-007 |
| C-005 | operability | When no candidate resolves, the failure message retains the existing actionable guidance, naming at least the `--source` remedy | Hard | S-005, F-004 |
| C-006 | structural | The bundled payload must be resolvable from the installed package location in a non-editable install | Hard | S-005 |
| C-007 | migration | Freshly built source and binary distributions show zero discrepancies between their file lists and the configured payload tree | Hard | S-006, F-010 |
| C-008 | quality-attribute | Dry-run payload parity between a non-editable and an editable install of the same revision, at the assurance level decided upstream | Hard | S-008, S-017 |
| C-009 | functional | In a clean environment, a non-editable install followed by initialize, install, and validate succeeds with no explicit source option | Hard | S-003, S-007 |
| C-010 | operability | Delivery regression posture: test suite green, all proof scripts PROVEN, handbook matches every touched document | Hard | S-011 |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | Packaging configuration (`pyproject.toml`) | contract-change | F-001, F-002 | Distribution contract: the file set carried by the source and binary distributions | confirmed |
| M-002 | `omn_agent/source.py` — `find_source` | extension | F-003, F-004 | Source-resolution candidate order; the CLI `--source` option surface | confirmed |
| M-003 | Bundled payload data subtree inside the `omn_agent` package (new structural element) | extension | A-001, A-002 | The bundled-source location consumed by the new last candidate in `find_source` | speculative |
| M-004 | Distribution metadata (`omn_agent.egg-info` file lists) | operational-impact | F-010 | Source and binary distribution file lists | confirmed |
| M-005 | `omn_agent/installer.py` | no-change-verified | F-008 | none | confirmed |
| M-006 | `omn_agent/validator.py` | no-change-verified | F-011 | none | confirmed |
| M-007 | `omn_agent/repo.py` — target resolution | no-change-verified | F-009 | none | confirmed |
| M-008 | `tests/test_omn_agent.py` suite | extension | F-012 | none | confirmed |

M-005 is recorded because a reader would expect the installer to change; it does not.
The installer consumes `find_source` unchanged (F-008), and its source-equals-target
guard is unaffected because the bundled source resolves under the installed package
location, never under the target framework directory (F-009). M-006 is recorded
because validation might be expected to learn about the bundle; it is not: validation
reads the installed target only (F-011). M-007 is recorded because target resolution
shares its dot-prefixed directory name with source resolution's second candidate
class; the two concerns remain separate (F-009). M-003 is speculative because its
shape and existence follow from A-001 and A-002; risk R-001 and R-002 attach to it.

### 5.2 Options Considered

Impact surface counts modules with `contract-change` or `dependency-change`. Reuse
leverage counts capabilities satisfied by `reuse-as-is` or `reuse-extended` in
section 7. Migration burden counts contract-affecting changes requiring a transition
strategy.

| Option | Structural change | C-001 | C-002 | C-003 | C-004 | C-005 | C-006 | Impact surface | Reuse leverage | Quality attributes (C-008, C-009) | Migration burden | Operability | Outcome |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O-001 | Bundle the payload as declared package data inside the `omn_agent` package (new data subtree M-003, declared in M-001); `find_source` gains the bundled location as a strictly-last candidate | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | 1 | 6 | Satisfied: parity and clean-environment walkthrough achievable from the bundled copy | 1 | One additional path probe at resolution time; no change to any existing mode | Selected |
| O-002 | Ship the root-level payload directory through source-distribution include directives (a build-inclusion directive file), leaving the payload at its current root location | Satisfied | Satisfied | Violated for the binary distribution (per A-001) | Satisfied | Satisfied | Violated (per A-001): the payload does not land at a location resolvable from the installed package | 1 | 3 | Not satisfiable: the clean-environment walkthrough fails because no bundled copy resolves | 1 | No resolvable payload in a non-editable install | Eliminated on C-006 (and C-003 for the binary distribution) |
| O-003 | Carry the payload in a second, dedicated data-carrying package installed alongside `omn_agent`; resolution locates the sibling package | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | Satisfied | 3 | 3 | Satisfied: parity and walkthrough achievable, at the cost of coordinating two distribution units | 2 | A second distribution unit must be versioned, built, and released in lockstep; a version skew between the two packages is a new failure mode | Not selected |

### 5.3 Selected Approach

- Selected: O-001.
- Structural change: introduce a bundled payload data subtree inside the `omn_agent`
  package (M-003) that mirrors the authoritative payload tree — every managed
  directory plus both seed directories (F-006), filtered by the installer's
  exclusion-pattern set (F-007) — and declare it as package data in the packaging
  configuration (M-001). Extend `find_source` (M-002) with exactly one new
  candidate: the bundled payload location resolved from the installed package,
  appended strictly after the existing candidates. The existing framework-tree
  validity check (F-005) applies to the bundled candidate unchanged, and the
  existing failure path (F-004) is retained verbatim in guidance content.
  Distribution metadata (M-004) is regenerated from the new configuration.
- Rationale: O-001 is the only option that satisfies every hard constraint while
  keeping the impact surface at one contract-changing module. It carries the highest
  reuse leverage of the three: the validity check, the enumeration and exclusion
  machinery, the failure guidance, and the installer's source handling are all
  reused unchanged.
- Highest-scoring rejected alternative and why it lost: O-003, the dedicated
  data-carrying package. It satisfies every hard constraint and isolates payload
  versioning cleanly, but it triples the impact surface (a new distribution unit,
  its packaging configuration, and a cross-package dependency in resolution),
  halves the reuse leverage, doubles the migration burden, and introduces a
  version-skew failure mode between two distribution units that the single-package
  bundle cannot exhibit. Under the recorded criteria it loses to O-001 on impact
  surface, reuse leverage, migration burden, and operability.
- Tradeoffs accepted: the payload is duplicated inside the package tree, so the
  distribution grows by the payload size and a synchronization obligation exists
  between the authoritative tree and the bundled copy (A-003, risk R-001). The
  alternative that avoids duplication entirely (O-002) fails the resolvability
  constraint, so the duplication is accepted and controlled by the completeness,
  filtering, and parity checks (C-003, C-004, C-008) rather than designed away.

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Carry the framework payload as declared package data inside the `omn_agent` package, as a bundled data subtree mirroring the managed-plus-seed tree under the installer's exclusion filter | Yes | ADR D-001, status Proposed |
| D-002 | Append exactly one bundled-payload candidate to the `find_source` order, strictly after the existing candidates, validated by the existing framework-tree check, with the existing failure guidance retained | Yes | ADR D-002, status Proposed |
| D-003 | Apply the existing framework-tree validity check (F-005) unchanged to the bundled candidate rather than introducing a bundle-specific check | No | Inline; reuses F-005 without structural change |
| D-004 | Regenerate distribution metadata from the new packaging configuration rather than editing the recorded file lists | No | Inline; the metadata is derived output (F-010) |

## API and Data Model Impact

- API changes: no runtime API changes. The externally observable CLI change is
  additive on M-002: source resolution now succeeds in one additional environment
  class (no explicit source, no checkout-adjacent tree, bundled payload present),
  and behaves identically in every existing environment class (C-001). The failure
  behaviour when no candidate resolves is unchanged (C-005, F-004).
- Contract compatibility notes for M-001 (D-001), the distribution contract:
  - Current shape: the source and binary distributions carry only the `omn_agent`
    package modules, project files, and metadata (F-001, F-010).
  - Target shape: the distributions additionally carry the bundled payload data
    subtree (M-003) inside the `omn_agent` package, complete per C-003 and filtered
    per C-004.
  - Compatibility approach: purely additive. No existing file moves or changes;
    editable installs and explicit-source users are unaffected because resolution
    precedence keeps the existing candidates first (C-001).
  - Coexistence period: indefinite by design. The checkout-adjacent tree and the
    bundled copy are both valid sources permanently; precedence (C-001)
    disambiguates deterministically.
  - Retirement condition: not applicable — no existing source mode is retired.
  - Rollback position: withdraw the package-data declaration from M-001 and the
    appended candidate from M-002; the distributions revert to the current shape
    and resolution reverts to F-003 behaviour. No installed target is affected,
    because installed targets are managed by the install manifest, not by the
    distribution contents.
- Schema or migration changes: none identified. No data model, stored schema, or
  installed-target format changes; the install manifest format and the target
  layout (F-009) are untouched. The absence is meaningful: the change is confined
  to what the distribution carries and where resolution looks.

## Reusable Components and Reuse Rationale

| Capability | Candidate | Outcome | Rationale |
|---|---|---|---|
| Framework-tree validity check for the bundled candidate | `_is_framework_tree` over `REQUIRED_SOURCE_FILES` (`omn_agent/source.py`) | reuse-as-is | F-005 already defines what a usable source is; applying it to the bundled candidate keeps one definition of validity (D-003) |
| Payload enumeration and exclusion filtering at install time | `enumerate_payload`, `enumerate_seeds`, `_walk` with `EXCLUDE_PATTERNS` (`omn_agent/source.py`) | reuse-as-is | F-013: enumeration walks whatever source it is given; the bundled source needs no new enumeration path |
| Authoritative exclusion definition for the packaging filter | `EXCLUDE_PATTERNS` constant (`omn_agent/source.py`) | reuse-as-is | F-007 is the single authoritative set (S-015); the packaging filter mirrors it so C-004 has one source of truth |
| Source-candidate resolution | `find_source` (`omn_agent/source.py`) | reuse-extended | F-003: the candidate-list structure accepts one appended candidate without altering existing branches (D-002) |
| Actionable failure guidance | The typed INVALID_TARGET error and hint in `find_source` | reuse-as-is | F-004 already names the `--source` remedy and the required files; C-005 requires keeping it |
| Bundled payload carrier inside the package | None exists | none-found | Search looked across every `omn_agent` package module (F-001 declares the package set), the packaging configuration (F-001), and the distribution metadata (F-010); no data subtree or package-data declaration exists. This licenses the only new structure, M-003 |
| Distribution metadata generation | Build-backend metadata regeneration | reuse-as-is | F-010: the metadata is derived output; regenerating from configuration (D-004) is the existing mechanism |
| Source-equals-target protection | Installer guard in `_install_like` (`omn_agent/installer.py`) | reuse-as-is | F-008: the guard already covers the bundled case, since the bundled source path is under the installed package, never under the target framework directory (F-009) |

## Operational Considerations

- Logging and observability updates: none required. Resolution remains a pure
  lookup; the existing typed-error and report machinery is unchanged (M-002, M-005,
  F-004). The absence is meaningful: adding logging would change surfaces C-002
  obliges this change to leave alone.
- Error handling strategy: the failure path is preserved, not replaced (C-005,
  F-004). When the bundled candidate exists but fails the validity check (F-005),
  it is simply not selected and the existing error with the existing hint is
  raised, exactly as for any other non-qualifying candidate (M-002).
- Security considerations: the distribution becomes a payload delivery vector —
  every consumer of the wheel receives the full framework payload (M-003, D-001).
  The exclusion filter (C-004, F-007) keeps cache, backup, and temporary artifacts
  out of the bundle, and the completeness check (C-003) is paired with a
  distribution inspection so unreviewed content cannot ride along silently (risk
  R-007). The managed directories carry no secrets by contract; nothing in this
  change widens what the installed target executes, because installation semantics
  (M-005) and validation (M-006) are untouched.
- Performance considerations: resolution cost grows by at most one path probe in
  environments where the existing candidates are absent, bounded by the fixed
  candidate order (C-001, M-002). Distribution size grows by the payload size
  (M-003, D-001 tradeoff); no recorded quality attribute constrains distribution
  size, so no optimization is designed for it.

## Delivery Plan

### Sequencing Constraints

| ID | Constraint | Modules | Prerequisites | Reason | Binds |
|---|---|---|---|---|---|
| P-001 | The packaging-mechanism decision (D-001) is accepted at the Design Gate with the packaged directory set (F-006) and the authoritative exclusion-pattern set (F-007) recorded, before any packaging configuration change | M-001, M-003 | none | Every packaging and metadata change binds to the selected mechanism and the recorded sets; changing them later invalidates the bundle | T-001 |
| P-002 | The resolution contract (D-002) — candidate order with the bundled payload strictly last, the bundled location under the selected mechanism, and the retained failure guidance — is accepted before any resolution change | M-002 | P-001 | The bundled location is determined by the mechanism D-001 selects; the fallback cannot be defined against an undecided location | T-003 |
| P-003 | The built distribution carries the complete filtered payload (C-003, C-004) and the bundled subtree passes the framework-tree validity check (F-005), before the resolution fallback is enabled | M-001, M-003 | P-001 | A fallback pointing at an incomplete or invalid bundle converts a clear failure (F-004) into a broken install; the bundle must be proven resolvable-quality first | T-002 |
| P-004 | The bundled candidate is appended strictly after the existing candidates with every existing branch and the failure path unchanged (C-001, C-005) | M-002 | P-002, P-003 | Consumer change follows contract definition, and the fallback may only target a bundle already proven by P-003 | T-004 |
| P-005 | Distribution metadata is regenerated from the new packaging configuration and shows zero discrepancies against the configured payload tree (C-007) | M-004 | P-003 | The metadata is derived from the configuration; regenerating before the configuration is final would re-record stale lists (F-010) | T-005 |
| P-006 | The parity-assurance level for the dry-run comparison (C-008) is decided before parity verification is designed | M-003, M-008 | none | The verification design for parity cannot be written against an undecided assurance level (S-017) | T-008, T-006 |
| P-007 | Full verification — clean-environment walkthrough (C-009), three-environment precedence demonstration (C-001), failure-guidance check (C-005), parity comparison at the decided level (C-008), distribution inspection (C-003, C-004, C-007), the existing suite and proof scripts (C-010) — follows delivery of packaging, fallback, and metadata | M-001, M-002, M-003, M-004, M-008 | P-004, P-005, P-006 | Verification of the boundary must cover the delivered whole; verifying earlier parts individually cannot demonstrate precedence across the three environment classes | T-006, T-007 |
| P-008 | The delivered change is reviewed for additive-only compliance against every named forbidden area (C-002) before closure | M-002, M-005 | P-004, P-005 | The additive-only constraint is a property of the delivered whole and must be checked against it, not against intentions | T-009 |
| P-009 | Documentation of the self-contained install behaviour and the resolution order, with handbook synchronization (C-010), follows verified behaviour | M-001, M-002 | P-007 | Documentation must describe demonstrated behaviour, not planned behaviour | T-010 |

The `Binds` column names the supplied execution plan's tasks each constraint
governs. This design creates no task identifiers; the planner owns T-001 through
T-010.

### Test Strategy Focus Areas

For omn-qa:

- Three-environment precedence demonstration (C-001): explicit source present;
  checkout-adjacent tree present with no explicit source; neither present with the
  bundled payload resolving.
- Failure-guidance check (C-005): an environment where no candidate resolves fails
  with the existing hint naming the `--source` remedy.
- Clean-environment walkthrough (C-009): non-editable install, then initialize,
  install, and validate with no explicit source option.
- Parity comparison (C-008) at the assurance level decided under P-006, paired
  editable versus non-editable.
- Distribution inspection: completeness per F-006 (C-003), zero excluded files per
  F-007 (C-004), zero metadata discrepancies (C-007).
- Regression obligations (C-010): the existing suite, every proof script, and the
  forbidden-area checks from P-008.

### Rollout and Rollback

- Rollout: follows the sequencing constraints P-001 through P-009; the fallback
  (P-004) is enabled only after the bundle is proven (P-003).
- Rollback: withdraw the package-data declaration (M-001) and the appended
  candidate (M-002); the distribution and resolution behaviour revert to the
  current state (F-001, F-003) with no effect on any installed target, per the
  rollback position in the API and Data Model Impact section.

## Risks and Mitigations

| ID | Class | Trigger | Impact | Likelihood | Affects | Mitigation | Owner |
|---|---|---|---|---|---|---|---|
| R-001 | migration | The bundled payload subtree drifts from the authoritative payload tree between builds (A-003 false or sync omitted) | Non-editable installs ship a stale or partial payload; the parity check (C-008) fails | medium | M-003, D-001 | P-003 proves completeness and validity per build; the paired parity comparison in P-007 detects drift; Q-003 resolves where sync verification lives | omn-dev-1-implement |
| R-002 | structural | A-001 is false: the source-distribution include mechanism proves resolvable from an installed package | The evaluation table ranking changes and D-001 must be revisited | low | D-001, M-003 | Confirm A-001 during P-001 acceptance; re-run the section 5.2 evaluation if it fails | omn-dev-1-implement |
| R-003 | contract | The bundled candidate resolves in an environment where an explicit source or a checkout-adjacent tree is present | Existing users' resolved source changes, violating C-001 | low | M-002, D-002, P-004 | The three-environment precedence demonstration in P-007, designed under P-006/P-007 | omn-qa |
| R-004 | operability | The packaged directory set or exclusion filter diverges from F-006/F-007 (A-002 false or mis-enumeration) | The bundle carries excluded files or omits managed or seed files; C-003 or C-004 fails | medium | M-001, M-003, P-003 | P-001 records the authoritative sets before packaging; the distribution inspection in P-007 detects divergence | omn-dev-1-implement |
| R-005 | migration | Regenerated metadata still disagrees with the configured payload (stale entries per F-010 survive) | The zero-discrepancy check (C-007) fails; stale file lists ship | low | M-004, P-005 | The zero-discrepancy comparison executed under P-007 | omn-dev-1-implement |
| R-006 | delivery | Packaging or resolution work touches a forbidden gate-behavior path | C-002 is breached; the change is rejected at review and reworked | low | M-002, P-008 | P-008 checks each named forbidden area explicitly; the suite and proof scripts run under P-007 (C-010) | omn-dev-2-reviewer |
| R-007 | security | Unintended repository content rides into the bundle past the exclusion filter | Every downstream install receives unreviewed content | low | M-003, D-001 | The exclusion filter (C-004) plus the completeness-and-content distribution inspection in P-007 | omn-dev-2-reviewer |

## Estimate and Confidence

- Overall: M (confidence: low). Confidence is low because the estimate depends on
  the speculative impact M-003 and the unconfirmed assumptions A-001 and A-003;
  it rises to medium once P-001 confirms them.
- Breakdown:
  - P-001, P-002 (decision and contract acceptance): S (confidence: high) — bounded
    design work within one boundary each.
  - P-003 (bundle delivery): M (confidence: low) — depends on M-003 (speculative)
    and A-001/A-003.
  - P-004 (fallback delivery): S (confidence: medium) — one appended candidate in a
    known structure (F-003), bounded by the accepted contract.
  - P-005 (metadata regeneration): S (confidence: high) — derived output (F-010).
  - P-006 through P-009 (decision, verification, review, documentation
    constraints): S each (confidence: medium) — well-bounded, but P-007 breadth
    depends on the Q-001 outcome.
- Scope assumptions: the estimate covers the nine sequencing constraints and
  assumes A-001 through A-003 hold. It excludes CKA-03, any gate-behavior surface
  (C-002), any precedence change (C-001), and any dry-run semantic change beyond
  the assurance level decided under P-006.
- Uncertainty drivers: A-001 (mechanism viability boundary) and A-003 (sync
  procedure) are unconfirmed and M-003 is speculative until P-001 accepts D-001;
  Q-001 determines the breadth of the parity portion of P-007.

## Open Decisions and Escalations

| ID | Question | Blocking | Owner | Affects | Consequence |
|---|---|---|---|---|---|
| Q-001 | Is file-count parity or file-set identity the binding assurance for the dry-run comparison (C-008)? Carried from the supplied plan's open question, resolved by its scope-phase task under P-006 | No | omn-product-owner | P-006, P-007, M-003 | Set identity requires per-file comparison of the paired enumerations and would move the deferred plan item into scope; count parity accepts the existing count-level comparison but can pass while contents differ |
| Q-002 | Design Gate acceptance of ADR D-001 and ADR D-002, both at status Proposed | No | omn-tech-lead | D-001, D-002, P-003, P-004 | Acceptance releases P-003 and P-004 to begin; rejection of D-001 re-runs the section 5.2 evaluation (R-002 path); rejection of D-002 returns the fallback contract to P-002 |
| Q-003 | Which build-procedure step verifies that the bundled subtree (M-003) is synchronized with the authoritative payload tree (A-003)? | No | omn-tech-lead | M-003, D-001, P-003 | If a standard build step verifies sync, P-003 evidences it directly; if none exists, an explicit sync-verification obligation is added ahead of P-007 and R-001 likelihood rises |

Decision records D-001 and D-002 remain at status Proposed and require Design Gate
acceptance before P-003 and P-004 begin. Q-002 is owned by omn-tech-lead because,
under the producer exclusion rule, acceptance rests with the non-producing Design
Gate owner; the gate's owners are omn-architect and omn-tech-lead. No entry is
blocking, so package status is complete.

## Sign-off

- Architect: omn-architect (producing role; excluded from accepting this package)
- Tech Lead: omn-tech-lead (accepting owner for the Design Gate)
- QA: omn-qa

Design Gate owners per the workflow gate matrix: omn-architect, omn-tech-lead. Under
the producer exclusion rule, acceptance rests with omn-tech-lead because the
architecture role produced this package. Lines are left unsigned by the producing
agent. No implementation work was performed and no external system was accessed in
producing this design.
