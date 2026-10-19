```yaml
implementationReport:
  reportId: IR-2026-1014
  changeReference: run-79276e78d773 implement-feature, lesson store migrated from the JSON document to an OKF v0.2 bundle
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/okf-lessons-feature-request.md
    - type: change-request
      reference: runs/inputs/okf-lessons-change-request.md
    - type: business-intent
      reference: runs/inputs/okf-lessons-business-intent.md
    - type: architecture-context
      reference: runs/inputs/okf-lessons-architecture-context.md
    - type: technical-design
      reference: runs/run-79276e78d773/states/solution-design-and-risk-assessment/artifacts/technical-design.md
  producedBy: omn-dev-1-implement
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: complete
  workflowPhase: implementation
  verificationStatus: verified
  inputDigest: sha256:2ad43fce633baecfb9f82eb8e578f2ad
  contextDigest: sha256:71b01b435a6f92e7b8bf1d1a67c8c50d
```

# Implementation Report: Lesson Store as an OKF v0.2 Bundle

## Metadata

- Report ID: IR-2026-1014
- Change reference: run-79276e78d773, phase implementation, technical design sha256:1f1c57e1efe3d5b22877d3f54fd9fefb with records D-001 to D-006
- Workflow phase: implementation
- Status: complete
- Verification status: verified
- Review status: pending-review

## Implementation Summary

- Change intent: the 43 governed lessons now live in memory/lessons as an OKF v0.2 bundle (one concept document per lesson, a derived index.md and log.md) that passes the §11 check, the JSON store is gone, and every caller above load_store and write_store, render_section included, behaves byte for byte as before.
- Approach taken: O-002 as designed. A new lesson-agnostic module (C-001) carries the frontmatter subset and the §11 check; the store boundary in C-002 maps records to documents through it, and the verifier (C-003) imports only C-001. Both new files sit on the extend-is-impossible rung of the ladder in skills/architecture/clean-architecture-checklist.md: no YAML writer exists in the runtime, the standard library has none, and the installed YAML package is excluded by the design constraint against third-party dependencies, so the design's reuse table records none-found; the atomic write, StoreLock, neutralise, and the digest helper are reused. No dependency was added. Exclusions (C-005, C-006) landed before any bundle file existed (P-004), the live migrate ran only after both suites passed, and the mirror was synced after the last framework edit.
- Design reference: technical-design.md sections 5.3 and 5.4, decisions D-001 to D-012, sequencing P-004 to P-012, API and Data Model Impact, Test Strategy Focus Areas
- Out of scope: runtime/README.md and every other context-slice member (A-008, M-020); KNOWLEDGE_CHANGE_SET and REFERENCE_COMMIT in the knowledge tests (frozen); committed run evidence and proposals; the release note, change proposal, and release checklist run (P-014, later phases); verify_multi_phase.py, verify_vertical_slice.py, verify_recovery.py and the full release-checklist run, held back by operator instruction because they mutate committed runs and are run by the operator; render_section and every loop function above the store boundary, which the design leaves unchanged.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | runtime/okf.py | added | Standard-library OKF v0.2 frontmatter subset writer and parser, document split and join, and the §11 conformance check | D-001, D-007, D-009; P-005 |
| `C-002` | runtime/knowledge.py | modified | Lesson store becomes the bundle: document mapping, index and log derivation, four-step write, lesson_id guard, bundle digest, store-migration-pending refusal, migrate subcommand | D-002, D-003, D-004, D-005, D-008; P-006 |
| `C-003` | runtime/verify_okf_bundle.py | added | Advisory verifier over a bundle path, default memory/lessons, text or JSON output, exit 0 pass or absent, 1 fail, 2 missing path | D-009; P-007 |
| `C-004` | runtime/framework_runtime.py | modified | RUNTIME_VERSION raised from 0.10.0 to 0.11.0 | D-011; P-008 |
| `C-005` | runtime/optimize_memory.py | modified | Optimiser denies any path whose segments hold memory followed by lessons, with a reason naming the lesson bundle | D-006; P-004 |
| `C-006` | omn_agent/source.py | modified | EXCLUDE_PATHS holds memory/lessons and _walk skips that path; the lessons.store.* name pattern is retired | D-006; P-004 |
| `C-007` | validation/framework-release-checklist.md | modified | Advisory item FR-13 owned by omn-qa names the verifier, with its advisory reason under Obligations | D-010; P-007 |
| `C-008` | config/runtime.md | modified | Store and lifecycle paragraph describes the bundle, reserved files, write order, digest, migration, verifier, and the path exclusions | D-012; P-011 |
| `C-009` | memory/README.md | modified | Lessons paragraph names the bundle in place of the JSON store | D-012; P-011 |
| `C-010` | memory/memory-governance.md | modified | Lesson Category source bullet names the bundle | D-012; P-011 |
| `C-011` | memory/memory-resolver.md | modified | Lesson Resolution gains a store bullet naming the bundle | D-012; P-011 |
| `C-012` | memory/lessons/lessons.store.json | removed | JSON store removed by the verified migrate after a record-for-record comparison of 43 lessons | D-005; P-009, P-010 |
| `C-013` | memory/lessons/index.md | added | Derived root index: okf_version frontmatter, Lessons heading, 43 link entries in fingerprint order | D-008; P-009 |
| `C-014` | memory/lessons/log.md | added | Derived change log: 43 Creation entries under date headings, newest first | D-008; P-009 |
| `C-015` | memory/lessons/L-0c65ee3df9.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-016` | memory/lessons/L-14a79151cb.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-017` | memory/lessons/L-16562ce500.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-018` | memory/lessons/L-1a032fb882.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-019` | memory/lessons/L-2120d10ba2.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-020` | memory/lessons/L-22390c2ab0.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-021` | memory/lessons/L-22847e61b4.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-022` | memory/lessons/L-32cc91b20e.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-023` | memory/lessons/L-3999fb5c73.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-024` | memory/lessons/L-4001c21edb.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-025` | memory/lessons/L-41c5dd8f64.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-026` | memory/lessons/L-4619b980fc.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-027` | memory/lessons/L-479b3eeb81.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-028` | memory/lessons/L-48df21734d.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-029` | memory/lessons/L-4a60ec1bdb.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-030` | memory/lessons/L-51be31d9d4.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-031` | memory/lessons/L-54d9e5c9d8.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-032` | memory/lessons/L-58915e88ef.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-033` | memory/lessons/L-58d9ae3d2e.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-034` | memory/lessons/L-606ac5af7f.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-035` | memory/lessons/L-6701578f8b.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-036` | memory/lessons/L-6af13c8ccc.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-037` | memory/lessons/L-6e77db508d.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-038` | memory/lessons/L-750011a2d2.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-039` | memory/lessons/L-7589a73850.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-040` | memory/lessons/L-764bff2fee.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-041` | memory/lessons/L-78c060dbd9.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-042` | memory/lessons/L-7f80924b57.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-043` | memory/lessons/L-86e0622785.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-044` | memory/lessons/L-9b5801a992.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-045` | memory/lessons/L-9f498451bb.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-046` | memory/lessons/L-a1c32dc2c2.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-047` | memory/lessons/L-a6553862f3.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-048` | memory/lessons/L-a73334458a.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-049` | memory/lessons/L-ae8d96f7c5.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-050` | memory/lessons/L-b3ac2f97e3.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-051` | memory/lessons/L-bfdb9bc126.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-052` | memory/lessons/L-cf715d2dd9.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-053` | memory/lessons/L-d1d17da655.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-054` | memory/lessons/L-d5b14c79b4.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-055` | memory/lessons/L-d7942f3a5a.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-056` | memory/lessons/L-d84ea03af4.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-057` | memory/lessons/L-de4ac3f115.md | added | Lesson concept document written by the verified migrate | D-002; P-009 |
| `C-058` | tests/test_knowledge.py | modified | Existing suite moved to the bundle: path-scoped copy-ignore, store helper, idempotency file set, lock name, optimiser, dispatch, fail-open, exclusion, boundary, documentation, and version checks | Test Strategy Focus Areas; P-010 |
| `C-059` | tests/test_okf_bundle.py | added | New suite: subset round-trip and hostile fixtures, document mapping, index, log, fault injection, conformance, verifier exits, migration and refusal | Test Strategy Focus Areas; V-003 |
| `C-060` | omn_agent/_bundled_payload/config/runtime.md | modified | Mirror of config/runtime.md refreshed by the sync step | P-012 |
| `C-061` | omn_agent/_bundled_payload/memory/README.md | modified | Mirror of memory/README.md refreshed by the sync step | P-012 |
| `C-062` | omn_agent/_bundled_payload/memory/memory-governance.md | modified | Mirror of memory/memory-governance.md refreshed by the sync step | P-012 |
| `C-063` | omn_agent/_bundled_payload/memory/memory-resolver.md | modified | Mirror of memory/memory-resolver.md refreshed by the sync step | P-012 |
| `C-064` | omn_agent/_bundled_payload/runtime/framework_runtime.py | modified | Mirror of runtime/framework_runtime.py refreshed by the sync step | P-012 |
| `C-065` | omn_agent/_bundled_payload/runtime/knowledge.py | modified | Mirror of runtime/knowledge.py refreshed by the sync step | P-012 |
| `C-066` | omn_agent/_bundled_payload/runtime/okf.py | added | Mirror of runtime/okf.py refreshed by the sync step | P-012 |
| `C-067` | omn_agent/_bundled_payload/runtime/optimize_memory.py | modified | Mirror of runtime/optimize_memory.py refreshed by the sync step | P-012 |
| `C-068` | omn_agent/_bundled_payload/runtime/verify_okf_bundle.py | added | Mirror of runtime/verify_okf_bundle.py refreshed by the sync step | P-012 |
| `C-069` | omn_agent/_bundled_payload/validation/framework-release-checklist.md | modified | Mirror of validation/framework-release-checklist.md refreshed by the sync step | P-012 |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | Frontmatter subset round-trip and hostile fixtures, document mapping against every record shape, index, log, render parity, fault injection at each write step and at the removal, seeded §11 defects, verifier exits 0, 1, 2 and repeat output, migration with forced mismatch, store-migration-pending refusal: 29 tests | integration | `C-001`, `C-002`, `C-003`, `C-059` | `PYTHONPATH=. python tests/test_okf_bundle.py` | pass |
| `T-002` | Knowledge loop suite on the bundle: harvest, idempotent file set, governance, lock, optimiser denial, dispatch hydration, fail-open, aggregation, payload exclusion, module boundary, documentation, version 0.11.0: 51 tests | regression | `C-002`, `C-004`, `C-005`, `C-006`, `C-008`, `C-009`, `C-010`, `C-011`, `C-058` | `PYTHONPATH=. python tests/test_knowledge.py` | pass |
| `T-003` | Bundled payload mirrors the framework tree after the sync: 11 tests | regression | `C-006`, `C-060`, `C-061`, `C-062`, `C-063`, `C-064`, `C-065`, `C-066`, `C-067`, `C-068`, `C-069` | `PYTHONPATH=. python tests/test_bundled_payload.py` | pass |
| `T-004` | Memory optimiser suite unchanged by the new denial rule: 31 tests | regression | `C-005` | `PYTHONPATH=. python tests/test_optimize_memory.py` | pass |
| `T-005` | Sync refreshes 289 payload files and mirrors nothing under memory/lessons | static | `C-006`, `C-060`, `C-061`, `C-062`, `C-063`, `C-064`, `C-065`, `C-066`, `C-067`, `C-068`, `C-069` | `PYTHONPATH=. python tests/test_bundled_payload.py --sync` | pass |
| `T-006` | Validator coverage verdict equals the pre-change baseline, 6 of 6 | regression | `C-004` | `python runtime/verify_validators.py` | pass |
| `T-007` | Registry coverage verdict equals the pre-change baseline, 8 of 8 | regression | `C-004` | `python runtime/verify_registry_coverage.py` | pass |
| `T-008` | Live migration: 43 records written, read back, compared record for record, JSON store removed; a re-run reports no legacy store | integration | `C-002`, `C-012`, `C-013`, `C-014`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049`, `C-050`, `C-051`, `C-052`, `C-053`, `C-054`, `C-055`, `C-056`, `C-057` | `python runtime/knowledge.py migrate` | pass |
| `T-009` | Live bundle conforms: 43 documents, 2 reserved files, 0 findings, identical output on two runs; a missing path exits 2 | contract | `C-001`, `C-003`, `C-013`, `C-014`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049`, `C-050`, `C-051`, `C-052`, `C-053`, `C-054`, `C-055`, `C-056`, `C-057` | `python runtime/verify_okf_bundle.py` | pass |
| `T-010` | Live list reads 43 lessons from the bundle | integration | `C-002`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049`, `C-050`, `C-051`, `C-052`, `C-053`, `C-054`, `C-055`, `C-056`, `C-057` | `python runtime/knowledge.py list` | pass |
| `T-011` | Live recall shows 2 of 2 eligible lessons for execution-planning with the unchanged prompt section | integration | `C-002`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049`, `C-050`, `C-051`, `C-052`, `C-053`, `C-054`, `C-055`, `C-056`, `C-057` | `python runtime/knowledge.py recall --phase execution-planning --artifact execution-plan.md` | pass |
| `T-012` | Per-lesson and whole-set render bytes, recall over 8 phase and artifact pairs, records, and effectiveness equal the pre-change baseline byte for byte | regression | `C-002`, `C-015`, `C-016`, `C-017`, `C-018`, `C-019`, `C-020`, `C-021`, `C-022`, `C-023`, `C-024`, `C-025`, `C-026`, `C-027`, `C-028`, `C-029`, `C-030`, `C-031`, `C-032`, `C-033`, `C-034`, `C-035`, `C-036`, `C-037`, `C-038`, `C-039`, `C-040`, `C-041`, `C-042`, `C-043`, `C-044`, `C-045`, `C-046`, `C-047`, `C-048`, `C-049`, `C-050`, `C-051`, `C-052`, `C-053`, `C-054`, `C-055`, `C-056`, `C-057` | `python capture.py runtime . after.json` then `cmp baseline.json after.json` | pass |
| `T-013` | Hashes of 1308 run-evidence files outside the carrying run equal the pre-change snapshot | regression | `C-002`, `C-012` | `python runhash.py runs run-79276e78d773 runs-after.json` then `cmp runs-before.json runs-after.json` | pass |
| `T-014` | The release checklist parses with FR-13 advisory, owner omn-qa, naming the verifier | static | `C-007` | `python runtime/self_hosting.py checklist` | pass |

## Verification Results

- Verification method: the regression baseline (both knowledge-related suites, both coverage verifiers, the optimiser suite, a byte capture of render, recall, records and effectiveness, a copy of the store, and run-evidence hashes) was captured read-only before any edit and re-run on the final tree; new tests run against temporary roots only; the live migrate, verifier, list and recall ran on the migrated tree. Runtime script commands are written as run from the framework directory; the first, migrating migrate run and verify_validators.py ran from the repository root through the framework directory, tests ran from the repository root, and capture.py and runhash.py are scratch scripts held outside the repository.
- Commands executed: PYTHONPATH=. python tests/test_okf_bundle.py; PYTHONPATH=. python tests/test_knowledge.py; PYTHONPATH=. python tests/test_bundled_payload.py; PYTHONPATH=. python tests/test_optimize_memory.py; PYTHONPATH=. python tests/test_bundled_payload.py --sync; python runtime/verify_validators.py; python runtime/verify_registry_coverage.py; python runtime/knowledge.py migrate; python runtime/verify_okf_bundle.py; python runtime/knowledge.py list; python runtime/knowledge.py recall --phase execution-planning --artifact execution-plan.md; python capture.py runtime . after.json then cmp baseline.json after.json; python runhash.py runs run-79276e78d773 runs-after.json then cmp runs-before.json runs-after.json; python runtime/self_hosting.py checklist
- Result summary: executed 14, passed 14, failed 0 (122 unit tests across four suites; parity and run-evidence comparisons identical)
- Unverified areas: none

## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| `V-001` | migrate with no JSON store present returns status no-legacy-store and exits 0 without writing (`C-002`) | D-005 states no behaviour for an absent JSON store | A re-run after a completed migration must be harmless; T-008 shows the second run reports the unchanged bundle digest | not-required |
| `V-002` | The lock-contention aggregation test asserts the bundle directory holds only lessons.lock instead of no directory (`C-058`) | Test Strategy Focus Areas, aggregation absence checks | D-003 places the lock inside memory/lessons, so a held lock creates the directory; the assertion still proves nothing else was written | not-required |
| `V-003` | New bundle tests sit in a new module beside the moved suite (`C-059`) | Test Strategy Focus Areas name tests/test_knowledge.py as carrier | Keeps the frozen backward-compatibility suite unchanged in shape; the operator authorised a new test module | not-required |
| `V-004` | write_store renders every file before the first write but leaves the lock to its callers (harvest, govern, migrate), as before the change (`C-002`) | D-003 reads write_store, under the lock | A lock taken inside write_store would deadlock its locked callers; every writer path still holds the lock, shown by the lock tests in T-002 | not-required |

## Boundary Compliance

- Module boundaries preserved: C-001 imports the standard library only, C-003 the standard library and C-001, C-002 the standard library, state_engine and C-001; nothing imports framework_runtime, all asserted by the module boundary tests in T-002.
- Public interface changes: knowledge.py replaces STORE_REL with BUNDLE_REL (memory/lessons), moves LOCK_REL to memory/lessons/lessons.lock, keeps LEGACY_STORE_REL for migrate, removes canonical_bytes and store_path, adds migrate, bundle_digest and bundle_exists, and adds error classes store-unwritable, store-migration-pending and migration-mismatch; load_store and write_store keep their signatures and in-memory shape; recall and harvest report store memory/lessons with the bundle digest; omn_agent/source.py gains EXCLUDE_PATHS; RUNTIME_VERSION is 0.11.0.
- Data or migration impact: one-time forward migration of 43 lessons, all candidate with empty history, verified record for record before the JSON store was removed; reversal is a revert that restores the tracked JSON file and drops the bundle; no run evidence, envelope, ledger or harvest record was rewritten (T-013).
- Declared side effects: the 69 Change Set files plus runs/run-79276e78d773/states/implementation/artifacts/implementation-report.md and runs/run-79276e78d773/states/implementation/result-envelope.json; nothing else was written in the repository. runtime/okf.py already existed untracked in the working tree when this invocation began and was replaced wholesale by C-001. The migrate briefly created and removed memory/lessons/lessons.lock.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| `R-001` | Another checkout pulling the change keeps a JSON-only store until its operator runs migrate | medium | Recall withholds lessons there and aggregation records the harvest as failed, both naming store-migration-pending | Refusal and fail-open are tested in T-001; config/runtime.md names the one-time migrate |
| `R-002` | An interrupted write leaves documents ahead of index.md and log.md until the next write | low | Index or log briefly disagrees with the documents; nothing reads them back | Reserved files are pure functions of the records and every file stays its prior or new version, shown by fault injection in T-001 |
| `R-003` | Recall and harvest now parse one document per lesson instead of one file | low | Dispatch and aggregation time grow linearly with lesson count | Elapsed time stays recorded in knowledge-harvest.json; writes skip unchanged files |
| `R-004` | verify_validators.py check F7 recomputes proposal scope paths relative to the working directory, so run from inside the framework directory it reports 5 of 6 | low | A run from the wrong directory reads as a regression | Pre-existing and unrelated to this change; from the repository root the verdict equals the baseline (T-006) |

## Handoff Notes

- Reviewer focus areas: the write order, orphan removal and migrate comparison in C-002 (V-001, V-004, R-002); the parser acceptance and refusals in C-001; the path exclusions in C-005 and C-006; the changed aggregation assertion in C-058 (V-002).
- Follow-up work: the operator runs the full suite and the release checklist, including verify_multi_phase.py with --run-id, verify_vertical_slice.py and verify_recovery.py, and records FR-13; the change proposal and release note cite this evidence (P-014); a later change may retire the store-migration-pending branch once no JSON-only checkout remains.
- Documentation impact: config/runtime.md, memory/README.md, memory/memory-governance.md and memory/memory-resolver.md updated in C-008 to C-011 and mirrored; runtime/README.md left unchanged as the design requires; the release note must tell operators of other checkouts to run migrate once.

## Open Questions

None identified.
