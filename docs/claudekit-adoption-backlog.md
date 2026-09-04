# ClaudeKit Adoption Backlog

Ticket list implementing the adoption plan from the ClaudeKit Adoption Review
(2026-08-27). Three epics map to the 30/60/90-day phases. Every ticket is an
additive check or tooling change: none may alter `record_gate_decision`, the
gate matrix semantics, producer exclusion, `runner._require_approval`, or any
human-block path. Effort: S (&le; 1 day), M (2–4 days), L (about a week).
`Source` cites the recommendation ID in the review.

## Epic A — Verification baseline (Days 0–30)

Goal: every PR is gated; a wheel installs standalone; guide drift is impossible.

### CKA-01 — Declare PyYAML and make `doctor` detect missing runtime deps
- **Type:** Task · **Priority:** Highest · **Effort:** S · **Source:** R1
- **Depends on:** —
- **Scope:** Add `pyyaml` to `dependencies` in `pyproject.toml`. Fix the
  "standard library only" claim in `README.md:10`. Extend
  `omn_agent/validator.py::_check_python` (currently `compile()`-only) to
  resolve top-level imports of installed runtime files so `validate`/`doctor`
  fail on a missing dependency instead of certifying a dead runtime.
- **Acceptance criteria:**
  - `pip install` in a clean venv pulls PyYAML.
  - `omn-agent doctor` against an install in an env without PyYAML reports a
    finding (not OK) and names the module.
  - Existing `tests/` remain green.

### CKA-02 — Ship the `.claude/` payload as package data
- **Type:** Task · **Priority:** Highest · **Effort:** M · **Source:** R1
- **Depends on:** —
- **Scope:** `pyproject.toml` package-data (or `MANIFEST.in`) so a
  non-editable wheel carries the framework payload; `source.find_source`
  resolves it from the installed location. Regenerate stale egg-info.
- **Acceptance criteria:**
  - In a clean venv, `pip install <wheel>` (non-editable) then
    `omn-agent init && install && validate` succeeds with no `--source` flag.
  - `omn-agent install --dry-run` enumerates the same payload file count as an
    editable install.

### CKA-03 — CI workflow gating every PR (tests + verifiers, by discovery)
- **Type:** Story · **Priority:** Highest · **Effort:** M · **Source:** R1
- **Depends on:** CKA-01, CKA-02
- **Scope:** New CI workflow on PRs: `python -m unittest discover -s tests`
  plus every `.claude/runtime/verify_*.py` asserting its `PROVEN` exit —
  both located by discovery, never a curated file list (claudekit's 14-of-77
  `npm test` failure mode). Matrix: ubuntu + windows. Verifier jobs advisory
  for the first week, then required. Windows job advisory week 1.
- **Acceptance criteria:**
  - A PR that breaks any single verifier fails CI naming the verifier.
  - Adding a new `tests/test_*.py` or `verify_*.py` file is picked up with no
    CI config change.

### CKA-04 — Content-contract tests over governance prose
- **Type:** Task · **Priority:** High · **Effort:** S · **Source:** R5
- **Depends on:** — (lands with or before CKA-03)
- **Scope:** New `tests/test_content_contracts.py` asserting structure the
  code depends on: every `workflow-gate-matrix.md` row has at least one owner
  outside `producer_aliases(producer)`; superseded agent files carry their
  status marker on line 1; the four root governance docs carry a `Status:`
  banner (CKA-05); no agent contract module matches coercive auto-chain
  patterns. Assert on structure (cells, first-line markers), not sentences.
- **Acceptance criteria:**
  - Mutating a fixture gate matrix to a producer-only owner row fails a test.
  - Suite runs green against current tree once CKA-05 lands.

### CKA-05 — Status banners on the four orphaned root governance docs
- **Type:** Task · **Priority:** High · **Effort:** S · **Source:** Phase-1 governance hygiene
- **Depends on:** —
- **Scope:** Add an explicit `Status: specification — not implemented` banner
  to `working-memory.md`, `rule-engine.md`, root `quality-gates.md`, and
  `decision-matrix.md`, each cross-linking its executable counterpart
  (`workflow-gate-matrix.md`, `recovery_policy.py`, the run-state model).
  No other content changes; full reconciliation is CKA-18.
- **Acceptance criteria:** each file's banner is present and pinned by CKA-04.

### CKA-06 — Generate `user-guide.html` from `USER-GUIDE.md` with a drift check
- **Type:** Story · **Priority:** High · **Effort:** M · **Source:** R7
- **Depends on:** CKA-03 (for the CI hook)
- **Scope:** New `tools/render_user_guide.py`; one-time two-way
  reconciliation of the current drift (the HTML's extra `fix-comments` prose
  merged back or dropped section by section; the MD's `5b. Branch naming
  templates` section rendered in). Generated banner in the HTML; `--check`
  mode in CI compares bytes and prints the regeneration command. Retire the
  hand-sync process note.
- **Acceptance criteria:**
  - Editing `USER-GUIDE.md` without regenerating fails CI with the fix command.
  - `user-guide.html` opens with a "generated — do not edit" banner.
  - No content present in exactly one of the two files after reconciliation.

## Epic B — Schema and boundary integrity (Days 31–60)

Goal: a prose edit can no longer silently change the enforced DAG; the CLI is
tested against the engine it drives.

### CKA-07 — `verify_schema.py`: structural validation of Phase Model and gate matrix
- **Type:** Story · **Priority:** Highest · **Effort:** L · **Source:** R2
- **Depends on:** CKA-03
- **Scope:** Eighth verifier validating every workflow's `## Phase Model`
  (column set; exactly one `*.md` per Output Artifact cell; Input terms
  resolvable under `terms_match` rules, flagging sub-`MIN_TERM_LEN` terms),
  the gate matrix (3 cells per row; owners are known roles), and manifests
  (`supportedWorkflows` pairs resolve). Diff-based severity: violations on
  files changed vs the PR base are errors, legacy files warn; a missing base
  ref FAILS the job (never warn-only degradation). Pure rule functions split
  from git discovery. Allowlist entries require a reason of 20+ chars and a
  known rule ID.
- **Acceptance criteria:**
  - Fixture tests: reformatted table, renamed `## Phase Model` heading,
    two-artifact cell, and a 5-char input term each trip their named rule.
  - Running with an unset/invalid base ref exits nonzero with a clear message.
  - One-week warn-only soak completed before the job is flipped to required.

### CKA-08 — Coverage check: `VALIDATORS` and `CONTEXT_SLICE_PHASE` vs Phase Models
- **Type:** Task · **Priority:** High · **Effort:** M · **Source:** R3
- **Depends on:** CKA-03
- **Scope:** Extend `verify_registry_coverage.py`: every Phase Model output
  artifact has a `VALIDATORS` entry and every phase a `CONTEXT_SLICE_PHASE`
  entry, so the failure surfaces in CI instead of at dispatch as a G1/G2
  block. (Generation of the dicts from the registry is out of scope; checking
  first.)
- **Acceptance criteria:** fixture with an uncovered row fails naming the row
  and the missing dict.

### CKA-09 — Split-brain detector: `taskplan.ROUTES` vs `registry/commands.yaml`
- **Type:** Task · **Priority:** High · **Effort:** M · **Source:** R3
- **Depends on:** CKA-03
- **Scope:** Check that every active registry command record is either
  routable by the CLI or listed in an explicit CLI-unrouted exemption list
  carrying a reason. Fold `quality_scan.py`'s hard-coded route into `ROUTES`.
  Triage the 6 currently unroutable commands (add route or exempt with
  reason) in the same PR.
- **Acceptance criteria:**
  - A new active command record with no route and no exemption fails CI.
  - `omn-agent plan`/`quality-scan` behavior unchanged for existing tickets.

### CKA-10 — `plan --json` machine-readable output; retire the run-id regex scrape
- **Type:** Story · **Priority:** Highest · **Effort:** M · **Source:** R8
- **Depends on:** —
- **Scope:** `framework_runtime.cmd_plan` gains `--json` emitting
  `{run_id, workflow, phases[]}`. `runner.py` and `update.py` consume it;
  `RUN_ID_RE` stdout scrape kept as fallback for one release, then removed.
  Human stdout unchanged.
- **Acceptance criteria:**
  - `update` flow records the run id with the regex path disabled in a test.
  - The "record it manually in task-plan.json" fallback message is
    unreachable when `--json` is available.

### CKA-11 — Real-engine contract test suite for the CLI↔runtime boundary
- **Type:** Story · **Priority:** Highest · **Effort:** L · **Source:** R8
- **Depends on:** CKA-10
- **Scope:** New `tests/test_engine_contract.py` driving the REAL
  `framework_runtime.py` through plan → dispatch → complete → gate → status
  on a scratch task, pinning the `framework.runtime/status-view.v1` fields
  that `fix_comments._status_json`/`_steps`/`_gates`/`_awaiting_gate` parse.
  Existing stub suites stay.
- **Acceptance criteria:** removing any field the CLI reads from
  `state_json` fails this suite (prove once by mutation).

### CKA-12 — Stop exit-code flattening in `runner._finish`
- **Type:** Task · **Priority:** Medium · **Effort:** S · **Source:** R8
- **Depends on:** CKA-11 (pins behavior before the change)
- **Scope:** Map runtime exit codes 1–4 to distinct documented CLI codes
  instead of collapsing to `UNEXPECTED = 7`. Code 8 (`APPROVAL_REQUIRED`)
  untouched. Fix `update.py:294` discarding the `next` return code. Update
  the exit-code tables in `cli.py`, README, and USER-GUIDE (regenerating the
  HTML via CKA-06).
- **Acceptance criteria:**
  - A blocked dispatch and a retrying dispatch produce distinct documented
    CLI exit codes.
  - Zero/non-zero semantics unchanged; code 8 byte-identical.

## Epic C — Evidence over declaration (Days 61–90)

Goal: write-scope claims are evidence-backed; upgrades can retire files
safely; a third dispatchable command needs no third copy-pasted drive loop.

### CKA-13 — Tree-verified side effects at `cmd_complete` (observe mode)
- **Type:** Story · **Priority:** Highest · **Effort:** L · **Source:** R4
- **Depends on:** CKA-03, CKA-11
- **Scope:** When the task has a bound worktree, capture
  `git status --porcelain` at dispatch and at complete; delta minus
  `declared_side_effects` minus the committed artifact = undeclared writes,
  recorded in `validation-report.json` under a new `tree_check` block.
  Config: `off | observe | enforce`, default `observe`. Phases without
  worktrees record `tree_check: not-applicable`. Gitignore semantics plus a
  small documented ignore list.
- **Acceptance criteria (scratch-repo unit tests):**
  - Undeclared write → recorded as a violation in observe mode.
  - Declared + permitted write → clean.
  - Gitignored path → clean.
  - `verify_vertical_slice.py` extended with one tree-verified completion.

### CKA-14 — Flip side-effect verification to `enforce`
- **Type:** Task · **Priority:** High · **Effort:** S · **Source:** R4
- **Depends on:** CKA-13 plus one full workflow cycle of observe-mode soak
  with zero false positives (or each triaged into the ignore list)
- **Scope:** Default `enforce`: undeclared writes fail validation exactly as
  a declared-but-unpermitted write does today, same failure-envelope shape,
  feeding auto-approval condition 2. Rollback = set flag to `observe`.
- **Acceptance criteria:** enforce-mode test shows the identical failure
  envelope class as the existing unpermitted-write path; gate auto-approval
  is held (never granted) on a tree violation.

### CKA-15 — Upgrade deletion ledger (hash-guarded prune)
- **Type:** Story · **Priority:** High · **Effort:** L · **Source:** R6
- **Depends on:** CKA-03, CKA-07
- **Scope:** New `.claude/bootstrap/deletions.json`; bidirectional CI check
  (a payload file deleted in a PR needs a ledger entry; a ledger entry
  matching a live payload file is an error). `installer.upgrade` prunes a
  ledgered path only when its hash matches the recorded install hash, always
  leaving a `.omn-bak`; modified or unmanaged files reported, never deleted;
  `--dry-run` previews prunes. Entries carry the retiring version and are
  prunable after one major cycle.
- **Acceptance criteria (extend `test_omn_agent.py`):**
  - Ledgered + unmodified → pruned with backup.
  - Ledgered + user-modified → kept with warning.
  - Live-file-vs-ledger conflict → CI check fails.
  - Empty ledger → byte-identical behavior to today.

### CKA-16 — Anti-rationalization tables and named gates in agent contracts
- **Type:** Task · **Priority:** Medium · **Effort:** S · **Source:** R9
- **Depends on:** CKA-04 (pins the language)
- **Scope:** Add anti-rationalization tables (thought → reality) and named,
  addressable hard-gate blocks to the implementer, reviewer, and QA contract
  modules; extend `test_content_contracts.py` to pin their presence.
- **Acceptance criteria:** contract tests fail if a table or named gate is
  removed; module line budgets respected.

### CKA-17 — `omn-agent gates`: cross-task pending-decision enumeration
- **Type:** Task · **Priority:** Medium · **Effort:** M · **Source:** R10
- **Depends on:** CKA-10
- **Scope:** Read-only subcommand sweeping `tasks/*/task-plan.json` and run
  state via `status --json`, listing every gate awaiting a human decision
  with task, gate name, eligible owner roles, and the exact
  `omn-agent run ... --gate ...` command to decide it. `--json` output.
- **Acceptance criteria:** with two tasks holding pending gates, both are
  listed with copy-pasteable decide commands; no state is mutated (pinned by
  a read-only test like `--show`'s).

### CKA-18 — Reconcile gate vocabularies; retire or implement orphaned specs
- **Type:** Story · **Priority:** Medium · **Effort:** M · **Source:** Phase-3 governance
- **Depends on:** CKA-05
- **Scope:** One executable gate vocabulary (`workflow-gate-matrix.md`
  stays authoritative). Root `quality-gates.md` and `config/quality-gates.md`
  either rewritten as commentary on the matrix or retired with the
  superseded-doc convention; `working-memory.md`, `rule-engine.md`,
  `decision-matrix.md` each get an explicit decision: implement, rewrite as
  description of what exists, or retire. Complete the deferred
  `omn-architect` → `architect` reference migration in the gate matrix so
  `producer_aliases` can shrink.
- **Acceptance criteria:**
  - Grep for the retired vocabulary (e.g. `WAIVED`, 15-minute cooldown)
    finds no live normative doc without a status banner.
  - `producer_aliases` no longer needs the `omn-architect` entry; gate-policy
    tests stay green.

### CKA-19 — Extract shared `runtime_client.py` from the drive loops
- **Type:** Story · **Priority:** Medium · **Effort:** L · **Source:** Phase-3 refactor (enabled by R8)
- **Depends on:** CKA-11 (contract tests make the refactor safe)
- **Scope:** New `omn_agent/runtime_client.py` owning the drive loop,
  `_materialize`, `_archive_run`, and the status-JSON readers currently
  duplicated between `update.py` and `quality_scan.py` and borrowed as
  underscore-privates by three modules. `update`/`quality_scan` become thin
  callers; finding-code prefixes (`U-`/`Q-`) preserved.
- **Acceptance criteria:** all existing `test_update.py` /
  `test_quality_scan.py` / `test_fix_comments.py` tests pass unchanged; no
  cross-module underscore imports remain (pinned by a small import-graph
  test).

### CKA-20 — Journals practice
- **Type:** Task · **Priority:** Low · **Effort:** S · **Source:** R11
- **Depends on:** —
- **Scope:** `docs/journals/` with an INDEX and ONE filename convention
  (`YYYY-MM-DD-slug.md`), documented in the contributing notes. Seed it with
  a post-mortem of the PyYAML/packaging defect (CKA-01/02) as the first
  entry.
- **Acceptance criteria:** index exists; first journal entry merged; the
  convention is stated where contributors will see it.

## Sequencing summary

```
Phase 1: CKA-01 CKA-02 → CKA-03 ; CKA-04 CKA-05 CKA-06
Phase 2: CKA-07 CKA-08 CKA-09 (need CKA-03) ; CKA-10 → CKA-11 → CKA-12
Phase 3: CKA-13 → CKA-14 ; CKA-15 (needs CKA-07) ; CKA-16 (needs CKA-04)
         CKA-17 (needs CKA-10) ; CKA-18 (needs CKA-05) ; CKA-19 (needs CKA-11) ; CKA-20
```

Definition of done for every ticket: `tests/` green, all seven (later eight)
`verify_*.py` PROVEN, no change to gate-decision behavior, and — where docs
were touched — `user-guide.html` regenerated.
