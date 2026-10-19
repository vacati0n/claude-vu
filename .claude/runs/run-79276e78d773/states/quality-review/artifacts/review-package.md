```yaml
reviewPackage:
  packageId: RP-2026-0011
  reviewReference: run-79276e78d773 implement-feature quality-review, the uncommitted working-tree change against HEAD 915e884 that moves the lesson store to an OKF v0.2 bundle (implementation report IR-2026-1014)
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/okf-lessons-feature-request.md
    - type: change-request
      reference: runs/inputs/okf-lessons-change-request.md
    - type: business-intent
      reference: runs/inputs/okf-lessons-business-intent.md
    - type: architecture-context
      reference: runs/inputs/okf-lessons-architecture-context.md
    - type: implementation-report
      reference: runs/run-79276e78d773/states/implementation/artifacts/implementation-report.md
    - type: technical-design
      reference: runs/run-79276e78d773/states/solution-design-and-risk-assessment/artifacts/technical-design.md
    - type: pull-request-diff
      reference: working tree versus HEAD 915e884, excluding runs/run-79276e78d773/
    - type: test-evidence
      reference: inline
    - type: standards-checklist
      reference: OKF v0.2 SPEC copy supplied by the operator, held outside the repository
  producedBy: omn-dev-2-reviewer
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: complete
  verdict: approve-with-corrections
  inputDigest: sha256:e9e4b6d6d164a98a1648f8e99ddf8fa2
  contextDigest: sha256:dbb6d6ebe90100e36dc74083b2321673
```

## Metadata

- Review ID: RP-2026-0011
- Reviewer: omn-dev-2-reviewer
- Change under review: Lesson store as an OKF v0.2 bundle at memory/lessons (run-79276e78d773, change-set entries C-001 to C-069 of IR-2026-1014), uncommitted in the working tree over HEAD 915e884
- Review date: 2026-10-17

## Review Scope

- In scope: runtime/okf.py (new); runtime/verify_okf_bundle.py (new); runtime/knowledge.py (bundle read and write, lock path, index and log rendering, migrate, store digest); runtime/optimize_memory.py (bundle denial); omn_agent/source.py (path exclusion); runtime/framework_runtime.py (version); validation/framework-release-checklist.md (FR-13); config/runtime.md, memory/README.md, memory/memory-governance.md, memory/memory-resolver.md; tests/test_okf_bundle.py (new) and tests/test_knowledge.py; the migrated live bundle memory/lessons (43 concept documents, index.md, log.md) and the removal of memory/lessons/lessons.store.json; the operator's six review points (list markers, absent verified key, round-trip and render byte identity, parser robustness against hostile content, orphan deletion and atomicity under the lock, exclusion by relative path).
- Out of scope: the omn_agent/_bundled_payload mirror files were not read line by line, because they are produced by the sync step and their byte parity with the framework tree is asserted by tests/test_bundled_payload.py, which was run; the architecture decision records D-001 to D-006 were not opened, because the technical design states each decision and was read in full; verify_multi_phase, verify_vertical_slice and verify_recovery were not run, because the operator forbade running them in place; acceptance-criteria and release-threshold validation belongs to omn-qa; run evidence under runs/ other than the documents named below was not examined, because the change does not edit it.
- Evidence reviewed: full diff of runtime/knowledge.py, runtime/optimize_memory.py, runtime/framework_runtime.py, omn_agent/source.py, validation/framework-release-checklist.md, the four memory and config documents, and tests/test_knowledge.py (git diff against HEAD); runtime/okf.py, runtime/verify_okf_bundle.py and tests/test_okf_bundle.py read in full; memory/lessons/index.md and memory/lessons/log.md read in full; implementation report IR-2026-1014 read in full; technical design run-79276e78d773-okf-lesson-bundle-technical-design read in full; the four okf-lessons input documents read in full; the OKF v0.2 SPEC copy read for sections 3.1, 4.1, 5.1 to 5.5, 7, 8, 9 and 11; executed results listed under Test Adequacy Assessment.

## Findings

| ID | Severity | Category | Location | Requirement | Finding | Correction Request | Status |
|---|---|---|---|---|---|---|---|
| `F-001` | high | correctness | runtime/knowledge.py:533 (migrate) | Technical design C-011 and D-005 (migrated lessons keep identifiers, fields and history; JSON store removed only after verified migration) and the transition rule "with both present, the bundle is authoritative and migrate completes the removal" | When the JSON store and the bundle are both present and differ, migrate rewrites the bundle from the JSON store, deletes every concept document the JSON store lacks and discards governance history recorded only in the bundle, then reports success and removes the JSON store. Reproduced in a scratch copy: an approval made on the bundle and a lesson harvested after the JSON snapshot were both lost while migrate printed "42 lesson(s) verified record for record". Readers and writers refuse only a JSON-only state, so after a migration-mismatch or an interruption harvest and governance keep writing to the bundle, and the documented re-run then destroys that work. Classified high, not critical, because no current checkout is shown to be in the both-forms state (Q-002). | `CR-001` | open |
| `F-002` | low | correctness | runtime/okf.py:476 (conformance, OKF-11.1) | OKF v0.2 SPEC section 11 rule 1 and design constraint C-022 (the check works on any bundle path) | The verifier accepts any bundle path but reports valid YAML outside the writer's subset (block scalars, anchors, multi-line plain scalars, nested flow) as OKF-11.1 "frontmatter is not parseable", so a conformant third-party bundle is reported as failing section 11 without saying the failure is the subset limit. The behaviour itself is an accepted design tradeoff (technical design section 5.3, Tradeoffs accepted, D-007), which is the evidence that sets this at low rather than medium; what remains is that neither the verifier's usage text nor its finding detail discloses the limit. The lesson bundle path is unaffected. | `CR-002` | open |
| `F-003` | low | correctness | runtime/optimize_memory.py:312 (_denied) | Technical design C-014 and S-030 (the optimiser exclusion is scoped by relative path) | The memory followed by lessons segment pair is matched over every part of the absolute path rather than the path relative to the scan root, unlike classify, which computes the relative path with _rel. A framework placed under any ancestor directory pair memory/lessons would have every scanned document denied. No layout the framework names produces that pair, so there is no behavioural consequence today. | `CR-003` | open |

## Severity Summary

- Critical: 0
- High: 1
- Medium: 0
- Low: 2

## Standards and Architecture Conformance

- Coding standards: Standard-library-only rule (C-016) conforms: tests/test_knowledge.py ModuleBoundaryTestCase passed, asserting runtime/okf.py imports only the standard library and the verifier only okf. Determinism and skip-equal write (C-008) conform: the second write is byte-identical in tests and the CLI JSON output keeps sort_keys. The serialisation subset of D-007 is implemented as designed. Deviations from design C-011 and C-014 are recorded as F-001 and F-003.
- Architecture rules: Design O-002 boundaries conform: runtime/okf.py imports nothing from the framework, runtime/knowledge.py and runtime/verify_okf_bundle.py depend on it one-way, and callers above load_store and write_store are unchanged. The four-step write order of D-003 (documents, orphan and temporary-file removal, log.md, index.md last, each by temporary file and os.replace) conforms. The OKF v0.2 reserved-file rules (sections 3.1, 8, 9) conform on the live bundle: verify_okf_bundle reported pass over 43 documents and 2 reserved files. The migration transition rule of D-005 does not conform (F-001).
- Security criteria: Design C-017 (no field value can alter document, index or log structure, or form a path outside the bundle) conforms: every string is double-quoted with non-printable-ASCII characters escaped, index titles escape backslash and square brackets, log entries carry no free text, actors are sanitised by okf_actor, and lesson_id is guarded by the pattern L- followed by ten lowercase hex characters before any file name is formed; tests/test_okf_bundle.py exercises hostile strings and an unsafe lesson_id. No credential or secret is introduced.
- Exceptions requested: None identified.

## Test Adequacy Assessment

- Test evidence reviewed: Confirmed in this run, from the repository root with the temporary directory set to D: because the C: drive had no free space (TMPDIR, TMP and TEMP set to a scratch directory on D:): PYTHONPATH=. python tests/test_okf_bundle.py, 29 tests OK (T-001); PYTHONPATH=. python tests/test_knowledge.py, 51 tests OK (T-002; a first run with the default temporary directory on C: produced 1 failure and 7 errors, all disk-full, not attributable to the change); PYTHONPATH=. python tests/test_bundled_payload.py, 11 tests OK (T-003); PYTHONPATH=. python tests/test_optimize_memory.py, 31 tests OK (T-004; first run on C: errored with No space left on device); python runtime/verify_validators.py, 6 of 6 COVERED (T-006, run from the repository root; R-004 of the report concerns a run from inside the framework directory); python runtime/verify_registry_coverage.py, 8 of 8 COVERED (T-007); python runtime/verify_okf_bundle.py, pass, 43 documents, 2 reserved, 0 findings, exit 0 (T-009); python runtime/knowledge.py list --json, 43 lessons (T-010); python runtime/knowledge.py recall for execution-planning and execution-plan.md, 2 shown of 2 eligible (T-011); python runtime/self_hosting.py checklist, FR-13 advisory, owner omn-qa (T-014); git status and the live bundle digest sha256:c605eff29d802a01367a0497dee76c94 unchanged before and after. Reproduction for F-001 in a scratch copy outside the repository: python runtime/knowledge.py with --root set to the copy, approve on one lesson, then migrate, with the JSON store restored from git show HEAD. Inspection commands, all read-only: git status, git diff and git show against HEAD, and python runtime/review_package_validator.py over this package with its invocation envelope, PASS 31 of 31. Claimed in IR-2026-1014 and not re-run: T-005 (sync writes the mirror; corroborated by T-003), T-008 (live migrate; corroborated by the absent JSON store and 43 documents), T-012 and T-013 (scratch scripts held outside the repository; T-012 partly corroborated by the render-parity unit test).
- Coverage of changed behavior: Covered by executed tests: subset dump and parse round-trip over hostile strings and every live record shape, refusal of out-of-subset input, document mapping and field derivation, index and log rendering, render_section byte parity, idempotent second write, unsafe lesson_id and unsupported value refusals, orphan and temporary-file removal, fault injection at each replace and at the removal, seeded conformance defects per rule, verifier exit codes, JSON-only refusal, migrate of a JSON-only store, forced mismatch then re-run, optimiser denial for index.md, log.md and a concept document, payload exclusion by path, documentation text, and the version string. Not covered: migrate with both forms present and divergent (F-001), the verifier against valid YAML outside the subset (F-002), and the optimiser denial under an ancestor directory pair memory/lessons (F-003).
- Gaps requiring new tests: (1) migrate with the JSON store and the bundle both present, where the bundle holds an extra lesson and a governance history entry the JSON store lacks, asserting that no bundle document or history entry is lost (F-001, CR-001); (2) the verifier on a bundle holding valid YAML outside the subset, asserting the disclosed result (F-002, CR-002); (3) optimiser classification of a memory document whose absolute path has memory/lessons above the scan root (F-003, CR-003); handed to omn-qa.

## Correction Requests

| ID | Addresses | Required change | Blocking | Owner |
|---|---|---|---|---|
| `CR-001` | `F-001` | migrate never removes or overwrites a lesson document or a governance history entry that the JSON store lacks; when both forms exist and differ it either refuses with a named error class and writes nothing, or completes only when the two agree, as the architect rules under Q-001; a test proves the divergent case | yes | omn-dev-1-implement |
| `CR-002` | `F-002` | the verifier's usage text and its OKF-11.1 finding state that frontmatter outside the supported subset is reported as unparseable, or the verifier distinguishes out-of-subset YAML from unparseable YAML, so a fail on a third-party bundle is not read as a section 11 violation | no | architect |
| `CR-003` | `F-003` | the optimiser's lesson-bundle denial matches memory/lessons only within the path relative to the scan root, as C-014 states, with a test for an ancestor pair | no | omn-dev-1-implement |

## Residual Risk

- Accepted risk: After an interruption, concept documents can disagree with index.md and log.md until the next write (design A-003 and Tradeoffs accepted; the design names omn-business-analyst as confirming A-003 and omn-tech-lead as accepting owner of the Design Gate it passed); governance actions recorded after migration are lost on a revert unless re-applied (design Rollout and Rollback, accepting owner omn-tech-lead); recall parses one document per lesson at each hydrated dispatch (A-005, omn-tech-lead).
- Unmitigated risk: Other checkouts that still hold a JSON-only store must run migrate once; until CR-001 closes, any of them that reaches the both-forms state through an interruption or a migration-mismatch and then records a governance action or a harvest loses that work on the next migrate. Whether an install ever held a JSON store is unconfirmed (Q-002).
- Monitoring required: The elapsed time recorded in knowledge-harvest.json as the lesson count grows (design R-006); FR-13 advisory verifier results in change proposals; the migrate outcome and any migration-mismatch reported by other checkouts after they pull the change.

## Verdict

- Decision: approve-with-corrections
- Rationale: One high finding (F-001) is open with a blocking correction request, no critical finding is open, and executed test evidence was reviewed, so the first matching row of the Stage 8 table is the open-high row, which yields approve-with-corrections with status complete.
- Blocking findings outstanding: F-001
- Readiness recommendation: Recommended to omn-qa, owner of the Review Gate, that the change not progress until CR-001 is closed with a test for the divergent both-forms case and re-reviewed; CR-002 and CR-003 may be carried as non-blocking improvements. This is a recommendation, not a gate decision.

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| `Q-001` | When the JSON store and the bundle are both present and differ, which form wins: the bundle, as design section 6 states, or the JSON store, as design section 5.3 implies by "re-running it after an interruption rewrites the bundle"? | no | architect | CR-001 required outcome |
| `Q-002` | Can any installed copy hold a JSON store written by runtime 0.10.0, contrary to the design's statement that installs never held one, so that it could reach the both-forms state after upgrading? | no | omn-tech-lead | F-001 severity and the verdict; a yes raises F-001 to critical and the verdict to reject |
