```yaml
implementationReport:
  reportId: IR-2026-0001
  changeReference: BENCH-T2
  sourceInputs:
    - type: accepted-change
      reference: ACCEPTED-CHANGE.md (design elements D-001 through D-004, constraints C-001 and C-002)
  producedBy: omn-dev-1-implement
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  workflowPhase: implementation
  verificationStatus: verified
  inputDigest: not-applicable — no invocation envelope governs this run (operator dispatch)
  contextDigest: not-applicable — no invocation envelope governs this run (operator dispatch)
```

## Metadata

- Report ID: IR-2026-0001
- Change reference: BENCH-T2
- Workflow phase: implementation
- Status: complete
- Verification status: verified
- Review status: pending-review

## Implementation Summary

- Change intent: `app.pricing.compute_discount(customer_tier, amount)` now memoizes its
  result per `(customer_tier, amount)` pair, so a repeated call with the same arguments is
  served from cache instead of re-running the simulated expensive rule evaluation. Before
  the change, every call re-ran the evaluation regardless of prior calls with the same
  arguments.
- Approach taken: applied `functools.lru_cache(maxsize=256)` directly as a decorator on
  `compute_discount`. This stops at rung 3 of the necessity and reuse ladder in
  `skills/architecture/clean-architecture-checklist.md` ("does the standard library solve
  it? use it"): the standard library's own bounded, thread-safe LRU cache satisfies D-001
  and D-002 exactly, without a new abstraction, file, or dependency, satisfying the accepted
  change's no-new-third-party-dependency constraint. No lower rung (reuse of an existing
  helper) applied, because the codebase has no existing memoization helper to reuse.
- Design reference: D-001, D-002, D-003, D-004 (ACCEPTED-CHANGE.md).
- Out of scope: no change was made to `RULES`, to the rounding or rate-application logic,
  or to any caller of `compute_discount`; none of these were named by the accepted change,
  and the decorator approach requires no change to them for D-001–D-004 to hold.

## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `app/pricing.py` | modified | Memoize `compute_discount` with an `lru_cache(maxsize=256)` decorator so repeated calls with the same arguments are served from cache, bounded at 256 entries with LRU eviction, while an unknown tier still raises `KeyError` on every call and the call signature is unchanged | D-001, D-002, D-003, D-004 |
| `C-002` | `tests/test_pricing.py` | modified | Add tests proving the cache serves a repeated identical call (D-001), that the cache bound is 256 with LRU eviction (D-002), and that an unknown tier raises `KeyError` on every call without being cached (D-003); add a `setUp` that clears the cache so existing and new tests are deterministic against shared module-level cache state | D-001, D-002, D-003 |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | a second identical call to `compute_discount` is served from cache (one miss, then one hit) | unit | `C-001`, `C-002` | `python -m unittest tests.test_pricing.DiscountCacheTests.test_repeated_call_is_served_from_cache -v` | pass |
| `T-002` | the cache's `maxsize` is 256, and once 300 distinct arguments are supplied the cache holds exactly 256 entries with the least-recently-used entry evicted | unit | `C-001`, `C-002` | `python -m unittest tests.test_pricing.DiscountCacheTests.test_cache_bound_is_256_with_lru_eviction -v` | pass |
| `T-003` | an unknown tier raises `KeyError` on every call, and each such call is a cache miss (never cached) | unit | `C-001`, `C-002` | `python -m unittest tests.test_pricing.DiscountCacheTests.test_unknown_tier_raises_on_every_call_and_is_never_cached -v` | pass |
| `T-004` | the pre-existing `gold` discount and unknown-tier tests still pass unchanged, confirming the call signature and return value are unaffected (D-004) | regression | `C-001`, `C-002` | `python -m unittest tests.test_pricing.DiscountTests -v` | pass |
| `T-005` | the full repository test suite, re-run as the regression baseline comparison against the pre-change baseline captured in Context Loading | regression | `C-001`, `C-002` | `python -m unittest discover -s tests -v` | pass |

## Verification Results

- Verification method: executed the three new unit tests proving D-001, D-002, and D-003
  individually; re-ran the pre-existing `tests/test_pricing.py::DiscountTests` tests to
  confirm D-004 (unchanged signature and behaviour); re-ran the full repository suite via
  `python -m unittest discover -s tests` as the regression baseline comparison against the
  4-test baseline captured before the change.
- Commands executed: `python -m unittest discover -s tests -v` (pre-change baseline, 4
  tests, all passed); `python -m unittest tests.test_pricing.DiscountCacheTests.test_repeated_call_is_served_from_cache -v`; `python -m unittest tests.test_pricing.DiscountCacheTests.test_cache_bound_is_256_with_lru_eviction -v`; `python -m unittest tests.test_pricing.DiscountCacheTests.test_unknown_tier_raises_on_every_call_and_is_never_cached -v`; `python -m unittest tests.test_pricing.DiscountTests -v`; `python -m unittest discover -s tests -v` (post-change, 7 tests).
- Result summary: pre-change baseline — 4 executed, 4 passed, 0 failed. Post-change — 7
  executed, 7 passed, 0 failed, 0 not-run.
- Unverified areas: none.

## Deviations and Tradeoffs

None identified.

## Boundary Compliance

- Module boundaries preserved: yes. The change is confined to the pricing module
  (`app/pricing.py`) and its own test file (`tests/test_pricing.py`); no other module was
  touched, and no new module, package, or cross-module import was introduced.
- Public interface changes: none. `compute_discount(customer_tier, amount)` keeps its
  existing name, parameter order, and return type; `functools.lru_cache` preserves the
  wrapped function's call signature, so every existing caller is unaffected (D-004).
- Data or migration impact: none. The cache is an in-process, in-memory structure with no
  persisted state, schema, or migration involved.
- Declared side effects: `app/pricing.py` (modified), `tests/test_pricing.py` (modified),
  `implementation-report.md` (added). Running the permitted test command (per the required
  evidence) caused the Python interpreter to regenerate its own compiled-bytecode cache
  under `app/__pycache__/` and `tests/__pycache__/`; both directories already existed,
  untracked, before this run. This is an interpreter byproduct of executing the test
  command, not a source or test change, and carries no behaviour of its own.

## Residual Risk

| ID | Risk | Likelihood | Impact | Mitigation actually in place |
|---|---|---|---|---|
| `R-001` | `RULES` is a module-level dict. If a future change mutates it at runtime (e.g., changing a tier's rate) rather than only at import time, `compute_discount`'s cache would keep returning the pre-mutation result for any already-cached `(customer_tier, amount)` pair until the process restarts or `compute_discount.cache_clear()` is called. | low — nothing in the current codebase mutates `RULES` after import | moderate — a stale discount would be returned silently rather than raising | none beyond the accepted design's own scope: D-001–D-004 specify caching by argument pair only, and no rule-mutation path exists today to trigger this |

## Handoff Notes

- Reviewer focus areas: `C-001`'s `functools.lru_cache` behaviour is best checked against
  `T-002` (the 256-entry bound and LRU eviction) and `T-003` (unknown tier never cached),
  since both rely on `lru_cache`'s internal accounting rather than a direct assertion on
  `RULES`; the `R-001` residual risk around `RULES` mutation is also worth an independent
  look.
- Follow-up work: none identified beyond `R-001`; if a future change makes `RULES` mutable
  at runtime, a cache-invalidation mechanism would need to be designed and accepted at that
  time.
- Documentation impact: none identified. No public API or usage change reaches existing
  callers (D-004); the only documentation touched is `compute_discount`'s own docstring,
  updated in place to describe the caching behaviour it now has.

## Open Questions

None identified.
