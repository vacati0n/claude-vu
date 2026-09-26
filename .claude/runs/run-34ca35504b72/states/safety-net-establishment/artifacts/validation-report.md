# Validation Report: Safety Net for the Folder Descriptions Sync

```yaml
validationReport:
  reportId: run-34ca35504b72-safety-net-establishment-validation-report
  validationReference: >-
    folder-descriptions-sync: the additive four-row extension of the orientation
    document's `## Folder Descriptions` section, selected as option O-001 by the
    technical design of run-34ca35504b72
  validationBasis: safety-net
  sourceInputs:
    - type: technical-design
      reference: runs/run-34ca35504b72/states/scope-invariants-and-risk-profile/artifacts/technical-design.md
    - type: architecture-context
      reference: >-
        runs/inputs/*-md-folder-sync-architecture-context.md (digest
        sha256:36a5a86305d4a0bcfe63560e13e3c0f3; the filename's leading token is
        elided because the model-independence rule forbids reproducing it)
  producedBy: omn-qa
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  verdict: pass-with-reservations
  inputDigest: sha256:b81549f82159b643e7b59ab4f73ee0b9
  contextDigest: sha256:b5595bb4fe87f1067bbee4dd85d57c35
```

## Metadata

- Validation ID: run-34ca35504b72-safety-net-establishment-validation-report
- Validator: omn-qa
- Change under validation: the pre-change safety net for the additive four-row extension of the `## Folder Descriptions` section of the orientation document, the project-instructions file at the framework payload root; the change itself does not exist yet at this phase.
- Validation date: 2026-09-04

Naming note, following the convention the technical design established: the changed file is called "the orientation document" throughout, and the leading token of the supplied input filenames is elided, because each embeds a token the model-independence rule forbids naming. No criterion's meaning is altered by either substitution; the elided input is disambiguated by the digest recorded in `sourceInputs`. Identifiers of the form `C-nnn`, `F-nnn`, `A-nnn`, `P-nnn`, `R-nnn`, and `S-nnn` belong to the technical design and are always introduced by their kind; the `AC-nnn`, `DF-nnn`, and `Q-nnn` families belong to this report alone.

## Validation Scope

- In scope: the pre-change verification baseline for the ten criteria the technical design binds this change to (assumption A-004 and hard constraints C-001 through C-009), the executable checks that will settle each of them once the edit exists, and the regression surface an edit to the orientation document could plausibly disturb: the five verification scripts under `runtime/`, the root unit-test suite, the packaged-payload parity check, the governance-prose content contracts, the resolvability of every path token the document cites, and the three level-2 sections of the document outside `## Folder Descriptions`.
- Out of scope: the accuracy of the four descriptions against their named folder authorities, which the technical design routes to `omn-dev-2-reviewer` as its own open question; the summary-granularity and register judgement behind constraints C-006 and C-009, which the design routes to the Invariant Gate under its risk R-001 with `omn-tech-lead` as owner; the `dependency-map.md` discrepancy the design records for separate routing; and code quality, which belongs to `omn-dev-2-reviewer`.
- Evidence examined: the technical design of the upstream phase, read in full from the invocation envelope; the supplied architecture context, read in full from the same envelope; the invocation envelope at `runs/run-34ca35504b72/states/safety-net-establishment/invocation-envelope.json`; the work-item record for this phase in `runs/run-34ca35504b72/state.json`; the orientation document in full; the Phase Model table of `workflows/refactor.md`; the CI verification workflow `.github/workflows/verify.yml` in full; and the executed commands recorded in the Test Strategy and criteria tables below.

## Test Strategy

- Risk basis: the Stage 4 depth table's last row governs this change. The edit is confined to a documentation section with no state effect: the orientation document is resolved by no registry record, parsed by no validator, and consumed as an input artifact by no workflow phase, and this run confirmed independently that the file is absent from the installer's payload map (267 payload files, none of them this document) and that no script under `runtime/` and no module under `tests/` reads it. That row warrants criterion-level checks only. This run deliberately went above that floor and executed the full regression surface at baseline, because constraint C-007 makes verification-script verdict parity the declared regression measure of this change, and fixing that baseline before the edit exists is this phase's entire purpose. The depth table sets a floor, not a ceiling.
- Levels executed: unit and integration. Unit covers the root suite by its own discovery and the static structural probes over the orientation document. Integration covers the five verification scripts under `runtime/`, each of which exercises a runtime resolution chain end to end within the repository.
- Environment: the repository working tree on Windows 11 under Python 3.14.0, at commit 96dfba8, with the orientation document clean at its committed blob bd1f2b01f531e14aa59d8fa1d908e10f391fdfc9. This differs from the CI target in two ways that are recorded rather than assumed away: CI provisions Python 3.10 on ubuntu-latest and windows-latest, and `pytest` is not installed locally, so the suite was executed through `python -m unittest discover -s tests`, which is the command CI itself runs. The tree also carries unrelated uncommitted modifications to four repository-root governance documents that predate this run.
- Not executed: end-to-end, because no runtime-resolved surface consumes the changed document, so no end-to-end path traverses it. Performance, because no executable path changes and no recorded quality attribute is affected. Security, because no access path, credential handling, or trust boundary changes; the added rows summarize folders already described across the repository's own governance documents. None of the three was warranted by the Stage 4 row that governs this change.

## Acceptance Criteria Results

| ID | Criterion | Source | Method | Result | Evidence |
|---|---|---|---|---|---|
| `AC-001` | The sixteen-directory count (F-001) remains current at implementation time; it was asserted as of 2026-08-27 | `technical-design.md` assumption A-004 | unit | met | Re-derived from the filesystem on 2026-09-04 by enumerating the directory entries at the framework payload root with `python -c "import os; [d for d in os.listdir(...) if os.path.isdir(...)]"` and differencing that set against the row keys parsed from the section: sixteen directories present, unchanged from the 2026-08-27 assertion, twelve documented, and the undocumented set exactly `domain-model`, `prompts`, `registry`, `runtime`, identical to the gap the design asserts. The assumption holds as of this run. Its forward exposure to design step P-001 is carried in Residual Risk rather than claimed as settled here. |
| `AC-002` | The diff is confined to `## Folder Descriptions` of the orientation document; the change is rejected if the diff leaves the section | `technical-design.md` constraint C-001 | integration, deferred | blocked | No edit exists at this phase, so no diff can be examined; `git status --porcelain` confirms the file is clean at its committed blob bd1f2b01. Settled post-change by `git diff` over the orientation document showing hunks only inside the section, and by the pinned out-of-section digest below remaining `415bac853e64fc049cad7a60164181e5` over 1903 bytes. |
| `AC-003` | The change is purely additive: every existing row keeps its meaning and relative order | `technical-design.md` constraint C-002 | unit, deferred | blocked | No edit exists, so additivity cannot be observed. Baseline pinned this run: twelve rows in the order `context/, config/, agents/, skills/, workflows/, commands/, templates/, memory/, validation/, reports/, proposals/, runs/`, digest `6a0c112e6f2e9f0f3ef92e728c8216f4`. Settled post-change by re-deriving that order and confirming the twelve appear unchanged and in the same relative sequence. |
| `AC-004` | No contract, registry record, routing row, gate, or runtime behaviour changes | `technical-design.md` constraint C-003 | integration, deferred | blocked | No edit exists, so no diff scope can be assessed. Settled post-change by `git status --porcelain` showing no modified path outside the orientation document, `proposals/`, and `runs/`, together with the five verification scripts holding the summary lines recorded under `AC-008`. |
| `AC-005` | After the change, every directory under `.claude/` has a row: sixteen of sixteen | `technical-design.md` constraint C-004 | unit, deferred | blocked | The criterion states a post-change condition and no edit exists. Baseline measured this run and recorded under `AC-001`: sixteen directories present, twelve documented, four undocumented. Settled post-change by re-running the same enumeration and confirming the undocumented set is empty. |
| `AC-006` | Each added description accurately states what the folder holds today, verified against the folder's named authority | `technical-design.md` constraint C-005 | integration, attempted | blocked | No description exists yet to verify, and the accuracy judgement is not this agent's to make: the technical design routes it to `omn-dev-2-reviewer` as its own open question. Settled by the reviewer confirming each row against its named authority, after design step P-001 fixes the wording. |
| `AC-007` | No second authority is created: descriptions summarize, they do not restate registry or specification content | `technical-design.md` constraint C-006 | integration, attempted | blocked | No row text exists, and no mechanical method can settle whether a summary has become a second authority; it is a granularity judgement. The design assigns it to the Invariant Gate review under its risk R-001, owned by `omn-tech-lead`. Settled by that review confirming each added row stays at summary granularity against its named authority. |
| `AC-008` | All five verification scripts keep their current verdicts; no metric regresses | `technical-design.md` constraint C-007 | integration, deferred | blocked | Parity is a post-change comparison and no edit exists. The baseline the comparison runs against was captured this run by executing each of the five scripts from the repository root, and is recorded verbatim in the Baseline block below. Settled post-change by re-running all five and comparing summary lines. Two readings of "keep their current verdicts" are open and are raised as `Q-001`; the baseline is recorded at both the summary-line and check-count level so either reading is decidable without re-deriving it. |
| `AC-009` | Every path the orientation document cites resolves on the filesystem after the change | `technical-design.md` constraint C-008 | unit, deferred | blocked | The criterion states a post-change condition and no edit exists. Baseline measured this run by extracting every backtick-quoted path token from the document and testing each for existence: all eighteen resolve, none unresolved, corroborating design fact F-008 as of 2026-09-04. Settled post-change by re-running that extraction and confirming each token resolves, including the four new ones. |
| `AC-010` | One line per folder, matching the existing list's register and length; new rows inserted where a reader scanning the tree would look | `technical-design.md` constraint C-009 | unit, attempted | blocked | No rows exist to measure. The line-count and insertion-index halves are mechanically checkable against the twelve-row baseline pinned under `AC-003`; the register and length judgement is not, and the design assigns it to the Invariant Gate review. Settled by that review together with a post-change re-derivation of the row list. |

Baseline captured this run, and the reference the post-change comparison is made against:

```
orientation document      2794 bytes  sha256/32 4372781420e4ea81327d737f8be44603
  section only                        sha256/32 5ac9f9e04e4528b797624ce9173611e6
  everything outside it 1903 bytes    sha256/32 415bac853e64fc049cad7a60164181e5
  level-2 section list                sha256/32 0703acbd090d2b838459a32cfe46bf3a
  row order (12 rows)                 sha256/32 6a0c112e6f2e9f0f3ef92e728c8216f4
directories at payload root  16    documented 12    undocumented 4
cited path tokens            18    resolved   18    unresolved  0
installer payload map       267 files, orientation document absent
```

```
runtime/verify_registry_coverage.py   exit 0    6/6 checks passed -- COVERED
runtime/verify_validators.py          exit 0    6/6 checks passed -- COVERED
runtime/verify_recovery.py            exit 0  41/41 checks passed -- RECOVERY PROVEN
runtime/verify_vertical_slice.py      exit 0  10/10 checks passed -- PROVEN
runtime/verify_self_hosting.py        exit 1    7/8 checks passed -- NOT SELF-HOSTING
python -m unittest discover -s tests  exit 0
python -m unittest tests.test_bundled_payload    11 tests, OK
python -m unittest tests.test_content_contracts  13 tests, OK
```

The failing check inside `runtime/verify_self_hosting.py` is S8, and it fails for a reason unrelated to this change: framework runs inside the self-hosted window that no change proposal accounts for. It is recorded here as the observed baseline, not as a regression. Parity for this script therefore means the summary line still reading `7/8 checks passed -- NOT SELF-HOSTING`, not the script passing.

## Execution Summary

- Criteria validated: 10
- Met: 1
- Not met: 0
- Blocked: 9

## Defects

| ID | Severity | Category | Location | Symptom | Reproducibility | Status |
|---|---|---|---|---|---|---|
| `DF-001` | medium | operational | `runtime/verify_self_hosting.py`, check S8, whose inputs are the contents of `proposals/` and `runs/` | Three executions of the same command in this run, minutes apart and with no edit to the document under validation between them, reported different S8 detail: the first listed four unaccounted runs and the later ones listed a single unaccounted run. The summary line stayed `7/8 checks passed -- NOT SELF-HOSTING` across all three. The parity baseline constraint C-007 depends on is therefore stable at summary-line granularity and not stable at check-detail granularity, so that criterion is only partially settleable by comparison against a recorded baseline. | always | open |
| `DF-002` | low | operational | `runs/run-34ca35504b72/states/safety-net-establishment/invocation-envelope.json`, the `source_file` value of the `technical-design` entry in `input_contract.supplied` | The technical-design entry records an absolute filesystem path rooted at a specific machine, while the architecture-context entry beside it in the same list records a repository-relative path. The two entries use different path conventions. Both resolve in this working tree, so no input was lost. | always | open |

## Regression Assessment

- Regression scope: everything an edit to the orientation document could plausibly disturb, fixed before examination began: the five verification scripts under `runtime/`; the root unit-test suite as discovered by `python -m unittest discover -s tests`; the packaged-payload parity check in `tests/test_bundled_payload.py`, which would fail if the document were part of the installer payload and the bundle were left unsynced; the governance-prose content contracts in `tests/test_content_contracts.py`; the resolvability of the eighteen path tokens the document cites; and the three level-2 sections of the document outside `## Folder Descriptions`.
- Regressions detected: None identified.
- Coverage of changed behavior: no altered behavior exists at this phase, so none was reached. Every element of the declared regression scope was instead exercised at baseline in this run and its result recorded above: all five verification scripts executed from the repository root, the full root suite executed to completion, both named test modules executed individually, every cited path token resolved, and the document's section inventory, row order, and out-of-section content pinned by digest. One plausible regression was actively investigated and ruled out rather than assumed: the orientation document is absent from the installer's payload map, so the edit requires no bundle re-sync and cannot break payload parity.
- Untested areas: the accuracy of the four descriptions against their folder authorities, which no executed check can settle and which the design routes to `omn-dev-2-reviewer`; the summary-granularity and register judgements behind constraints C-006 and C-009, which no executed check can settle and which the design routes to the Invariant Gate; and the orientation document itself, which no check in either CI-discovered verification surface reads, so the section under change carries no mechanical coverage today. The full root suite's exit code was captured but its test count was not, because the command's output was truncated by the pipeline that ran it; only the exit code, which is the condition CI itself asserts, is claimed as evidence.

## Residual Risk

- Accepted risk: that the additive manual edit gives no mechanical guarantee the inventory stays complete as directories are added later, leaving completeness enforced only at review time against the count in constraint C-004. This tradeoff was accepted by `architect` in the technical design's selected-approach section and attached there to its risk R-004; the accepting owner for the Invariant Gate that carries it forward is `omn-tech-lead`. It is recorded here, not accepted here.
- Unmitigated risk: no executed check in either CI-discovered surface reads the orientation document, so a defect introduced into the section would be caught by human review alone; the parity baseline moves under framework activity outside this run (`DF-001`), so a post-change comparison can show a difference this change did not cause; and assumption A-004 is confirmed only as of 2026-09-04, so a directory added between now and implementation would move the completeness target constraint C-004 measures against.
- Monitoring required: re-run all five verification scripts and `python -m unittest discover -s tests` from the repository root immediately before and immediately after the edit, in the same working tree and with no unrelated framework activity in between, and compare summary lines rather than check details; re-derive the directory count, the undocumented set, and the twelve-row order at implementation start, as design step P-001 requires; and confirm the out-of-section digest recorded above is unchanged before any closure artifact records the change as done.

## Verdict

- Decision: pass-with-reservations
- Rationale: the Stage 8 table row for no open critical or high defect with at least one blocked criterion and none not-met yields exactly this verdict. The safety net this phase exists to produce was established: every element of the declared regression scope was executed at baseline, the comparison reference is pinned by digest and by verdict, and each of the ten criteria carries the specific check that will settle it. Nine criteria are blocked because they state post-change conditions and no change exists at this phase, which is structural to `safety-net-establishment` rather than a failure of anything; the one criterion evaluable before the change, the design's assumption A-004, was re-derived and is met. Two defects stand open, both below the blocking threshold, and neither contradicts a criterion.
- Blocking defects outstanding: None identified.
- Readiness recommendation: recommend proceeding to `refactor-implementation` with the baseline block above as the parity reference. Three conditions are recommended for the downstream phases rather than decided here: that design step P-001 re-derive the directory count and row order before the edit, since assumption A-004 is confirmed only as of this run's date; that the architect answer `Q-001` before `AC-008` is judged at `behavioral-validation`, because the expected change proposal will move the one input the self-hosting check still reports; and that the post-change parity comparison be made against summary lines rather than check details, given `DF-001`. The gate decision for this workflow is not this agent's to make.

## Open Questions

- `Q-001`: constraint C-007 requires all five verification scripts to "keep their current verdicts", and separately that "no metric regresses". The only run `runtime/verify_self_hosting.py` check S8 still reports as unaccounted is run-34ca35504b72 itself, so the change proposal that design step P-004 requires would remove the last unaccounted run and flip that script from `7/8 checks passed -- NOT SELF-HOSTING` to a passing verdict. That flip violates the first reading and satisfies the second. Which reading governs? Routed to `architect`, who owns constraint C-007. Affects `AC-008`. This agent has established both baselines so either answer is decidable without further measurement, and has not chosen between them, because narrowing a constraint to make it satisfiable is not this agent's to do.
- `Q-002`: this phase's permitted write scope for test files is confined to the framework payload tree, while the repository's two CI-discovered verification surfaces are the root `tests/` directory, discovered by `python -m unittest discover -s tests`, and files matching `verify_*.py` under `runtime/`, enumerated by the discovery job in `.github/workflows/verify.yml`. No path satisfies both, so a durable, CI-executed safety-net check cannot be authored from within this phase's authority. No test file was written this run, consistent with the technical design's reuse survey, which records verdict parity over the existing scripts as the regression measure and concludes that no new validation structure is required. Which surface should the grant name? Routed to `architect`. Affects the untested area recorded above.
