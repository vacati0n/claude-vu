# Review Package: /implement --demo demonstration capture (run-5df08e171670)

```yaml
reviewPackage:
  packageId: RP-2026-0005
  reviewReference: run-5df08e171670 quality-review; commit 2e9e99e (.claude/runtime/demo/**, demo options and subcommand in .claude/runtime/framework_runtime.py, tests/test_demo_*.py)
  sourceInputs:
    - type: feature-request
      reference: runs/inputs/demo-mode-feature-request.md
    - type: change-request
      reference: runs/inputs/demo-mode-change-request.md
    - type: business-intent
      reference: runs/inputs/demo-mode-business-intent.md
    - type: architecture-context
      reference: runs/inputs/demo-mode-architecture-context.md
    - type: implementation-report
      reference: runs/run-5df08e171670/states/implementation/artifacts/implementation-report.md
    - type: design-reference
      reference: runs/run-5df08e171670/states/solution-design-and-risk-assessment/artifacts/technical-design.md
    - type: test-evidence
      reference: inline (suite runs executed in this review, cited in Test Adequacy Assessment)
  producedBy: omn-dev-2-reviewer
  agentVersion: 1.1.0
  schemaVersion: 1.0.0
  status: complete
  verdict: reject
  inputDigest: sha256:d4a7d2d02caadd26f52a177ab99b2c74
  contextDigest: sha256:dbb6d6ebe90100e36dc74083b2321673
```

## Metadata

- **Review ID:** RP-2026-0005
- **Reviewer:** omn-dev-2-reviewer
- **Change under review:** the `/implement --demo` demonstration-capture capability as committed in 2e9e99e and reported by IR-2026-1014 (C-001 to C-054): `.claude/runtime/demo/**`, the ten demo flags, `enable_demo`, the emit tap, the status display and `cmd_demo` in `.claude/runtime/framework_runtime.py`, and `tests/test_demo_mode.py`, `tests/test_demo_capture.py`, `tests/test_demo_pacing.py`, `tests/test_demo_captions.py`
- **Review date:** 2026-10-17

## Review Scope

- **In scope:** the demo package modules `__init__.py`, `context.py`, `capture.py`, `capture_helper.py`, `editor.py` and `narration.py` at the sites cited in Findings; the four runtime integration sites in `.claude/runtime/framework_runtime.py` (emit tap 819-824, `enable_demo` 1732-1782, status display 2770-2791, `cmd_demo` 5865, parser 6017-6059); the four demo test modules; `.claude/commands/implement.md` flag rows 19-27; the `implement` record in `.claude/registry/commands.yaml`; bundled-payload parity of the demo package, the runtime file and the command spec; IR-2026-1014 claims T-001 to T-022 and deviations V-001 to V-006, measured against the technical design (M-001 to M-028, D-001 to D-010, C-001 to C-015).
- **Out of scope:** the internals of `renderer.py`, `deck.py`, `overlays.py`, `captions.py` and `timeline.py` were not read line by line; they are exercised by the passing pacing, caption and mode suites and carry no finding-bearing site. The omn_agent wrapper modules (C-019 to C-021) were assessed only through the passing `test_omn_agent` suite. The documentation changes C-022 to C-025 were checked only for flag agreement (P-003). M-023 to M-028 are recorded by the design as verified-unchanged and were not re-read. Live recorded-run acceptance criteria belong to omn-qa. `verify_self_hosting.py` (T-017) was not run because it rewrites run evidence; T-017 stays claimed. The T-022 payload drift in `runtime/verify_recovery.py` is outside this change and is not assessed.
- **Evidence reviewed:** IR-2026-1014 (sha256:c3c3f6b4f6a44140885cbbbe44538254); the technical design of this run; the task context; the code sites listed under In scope, read at the cited ranges; the executed results of the demo suites, the full suite, `verify_registry_coverage.py`, a payload byte comparison, and two read-only probes of `editor.scene_spans`/`rebalance_spans` and `capture_helper._merge`, each cited in Test Adequacy Assessment.

## Findings

| ID | Severity | Category | Location | Requirement | Finding | Correction Request | Status |
|---|---|---|---|---|---|---|---|
| F-001 | critical | security | `.claude/runtime/demo/editor.py:196-220` | Design C-005 (only the target window is ever published; publication safety outranks completeness); business intent; S09 secure by default | `rebalance_spans` widens a span (`end += take`) with no occlusion check after `scene_spans` clipped it; it runs in the default relaxed/explain mode (min span 7 s), so footage recorded while another window covered the target is put back into the published film | CR-001 | open |
| F-002 | high | security | `.claude/runtime/demo/capture_helper.py:46-56` | Design C-005; design R-001 accepts only the sampling-period residual | `_merge` discards every detected occlusion shorter than 0.4 s (about 12 frames at 30 fps), so a stretch the helper did see covered is never cut; this exceeds the residual R-001 accepted | CR-002 | open |
| F-003 | high | correctness | `.claude/runtime/demo/editor.py:725` | Design D-002 and C-015 (filmed path is the primary output); AC-008 | The encoder invocation passes `-filter_complex_script`, which the installed encoder rejects (`Unrecognized option`), so every filmed build fails and only the drawn fallback is produced; T-012 fails for this reason | CR-003 | open |
| F-004 | high | security | `.claude/runtime/demo/narration.py:32` | S09 secure by default, explicit by exception; S09 threat review for new external exposure; design reuse row naming the platform speech engines | The `auto` engine chain tries the network speech service first, sending narration text, including the run title taken from the feature request, off the host with no opt-in, no threat review and no mention of egress in `.claude/commands/implement.md` | CR-004 | open |
| F-005 | high | correctness | `.claude/runtime/framework_runtime.py:1732-1760` | Design C-004 (nothing in the observation layer raises into the run); design error-handling strategy naming the arming call as an absorption site; C-008 | `enable_demo` calls `enable`, `backfill` and `capture_status` outside any guard; only `record_start` is wrapped; an I/O or parse fault there raises into run planning between `execution-request.json` and `run_initialized`. The status display (2770-2772) calls `status()` unguarded and the emit tap imports the package outside its guard (822-823) | CR-005 | open |
| F-006 | medium | test-adequacy | `tests/test_demo_capture.py` | S07 missing negative-path coverage; design test focus on publication safety and absorption | No executed check covers occlusion combined with rebalance, the `_merge` threshold, the helper sampling loop, or a fault in the arming call; F-001, F-002 and F-005 all pass the suite undetected | CR-006 | open |
| F-007 | low | maintainability | `.claude/runtime/demo/__init__.py:174-175` | Design D-005 (compile once per run) | `claim_autobuild` returns True on OSError, so a claim fault lets a second build start; output is redundant, not wrong | CR-007 | open |
| F-008 | low | maintainability | `.claude/runtime/demo/__init__.py:33-38` | Design M-016 and the design fact recording four integration sites (documentation agrees with the integration surface) | The package docstring says the runtime touches it at exactly three points; there are four (emit tap, arming call, status display, subcommand) | CR-008 | open |
| F-009 | low | security | `.claude/runtime/demo/narration.py:164` | S09 validate and sanitize all external input | The platform-voice engine interpolates the operator-supplied voice name and the manifest path unescaped into a shell script string; a quote in either breaks the script | CR-009 | open |
| F-010 | low | packaging | `tests/__pycache__/test_demo_*.pyc` | S01 every element serves an accepted need; S10 coherent commits; IR V-005 | Four demo test bytecode files and `fake_obs` bytecode are tracked; they serve no accepted element and drift from their sources | CR-010 | open |

```python
# .claude/runtime/demo/editor.py, rebalance_spans (excerpt): widened with no occlusion test
s["end"] += take
```

## Severity Summary

- **Critical:** 1
- **High:** 4
- **Medium:** 1
- **Low:** 4

## Standards and Architecture Conformance

- **Coding standards:** S12 error handling and S11 logging applied: the observation layer logs and continues at the event tap and capture start, but not at the arming call or status display (F-005, F-007); S07 testing strategy applied: negative paths missing (F-006); otherwise conformant.
- **Architecture rules:** design C-004, C-005, D-002, D-005, P-003 and S01 applied: C-004 violated (F-005), C-005 violated (F-001, F-002), D-002 not met on the installed encoder (F-003), D-005 weakened (F-007); P-003 holds, all ten flags agree across parser, command spec and registry; bundled payload is byte-identical for the demo package, runtime file and command spec.
- **Security criteria:** S09 applied: secure-by-default and threat-review rules violated by the default network speech engine (F-004); input sanitization defect (F-009); publication safety defects F-001, F-002; the capture backends take no audio input and the encoder maps narration only, conformant with the never-publish-capture-audio clause; the OBS probe excludes the password, conformant.
- **Exceptions requested:** None identified.

## Test Adequacy Assessment

- **Test evidence reviewed:** confirmed in this run by `python tools/run_tests_parallel.py test_demo_mode test_demo_capture test_demo_pacing test_demo_captions`: 100 run, 97 pass, 3 fail, all in `EndToEndEditTestCase` from the rejected `-filter_complex_script` option (confirms T-002 to T-011, T-013 to T-016 pass and T-012 fails); confirmed by `python tools/run_tests_parallel.py`: 771 of 771 ran, 28 of 30 modules pass, failures in `test_demo_capture` (3) and `test_bundled_payload` (1, `runtime/verify_recovery.py`) (confirms T-001 and T-022); confirmed by `python .claude/runtime/verify_registry_coverage.py`: 8 of 8, COVERED (T-018); payload parity confirmed by byte comparison; F-001 and F-002 confirmed by read-only probes of `scene_spans`/`rebalance_spans` (occlusion 12-18 s, span 10-12 s widened to 10-17 s) and `_merge` (a 0.3 s span returns empty). Claimed, not confirmed: T-017 (self-hosting 7 of 9, not run), T-019 to T-021 individually (only within the full-suite pass), encoder version 9.0.2.
- **Coverage of changed behavior:** option parsing, context, pacing, captions, narration fallback, capture backends with a fake recorder, and status are covered and pass; the filmed end-to-end edit is covered but fails (F-003); publication safety under occlusion and fault absorption at the arming call are not covered (F-006).
- **Gaps requiring new tests:** for omn-qa: occluded stretch adjacent to a short beat under the default pace and explain mode; detected occlusions shorter than 0.4 s; the helper sampling loop; a fault raised by `enable`, `backfill` or `capture_status` during run planning; a corrupt `build-manifest.json` or `demo-context.json` under the status display; narration `auto` on a host with no network; a filmed build on the installed encoder.

## Correction Requests

| ID | Addresses | Required change | Blocking | Owner |
|---|---|---|---|---|
| CR-001 | F-001 | No published segment overlaps any recorded occlusion span, under every pace and explain setting | yes | omn-dev-1-implement |
| CR-002 | F-002 | Every occlusion the helper detects is excluded from publication, whatever its length; only the R-001 sampling residual remains | yes | omn-dev-1-implement |
| CR-003 | F-003 | A filmed build succeeds on the encoder installed on the operator host, and the supported encoder range is stated | yes | omn-dev-1-implement |
| CR-004 | F-004 | No narration text leaves the host unless the operator explicitly selects a network engine, and that exposure is threat-reviewed and documented | yes | omn-dev-1-implement |
| CR-005 | F-005 | No fault in the arming call, the status display or the emit-tap import can raise into the run; each logs and continues | yes | omn-dev-1-implement |
| CR-006 | F-006 | Executed checks cover each gap listed under Gaps requiring new tests | no | omn-dev-1-implement |
| CR-007 | F-007 | A claim fault cannot start a second build of the same run | no | omn-dev-1-implement |
| CR-008 | F-008 | The package docstring names the integration points the runtime actually uses | no | omn-dev-1-implement |
| CR-009 | F-009 | Operator-supplied voice names and paths cannot alter the speech-engine script | no | omn-dev-1-implement |
| CR-010 | F-010 | No compiled bytecode is tracked in the repository | no | omn-dev-1-implement |

## Residual Risk

- **Accepted risk:** design R-001 sampling-period residual, accepted by omn-qa; design R-012 encode inside the run, accepted by omn-tech-lead; design R-009 host hook scope, accepted by omn-tech-lead.
- **Unmitigated risk:** until CR-001 and CR-002 close, any film already built under the default pace may contain occluded footage; until CR-004 closes, narration text of past runs may have left the host.
- **Monitoring required:** compare each build's edit decision list against the capture manifest's occluded list before a film is shared.

## Verdict

- **Decision:** reject
- **Rationale:** An open critical finding (F-001) publishes occluded footage by default, and four open high findings break publication safety, the filmed path, secure defaults and fault absorption; the Stage 8 table yields reject.
- **Blocking findings outstanding:** F-001, F-002, F-003, F-004, F-005
- **Readiness recommendation:** recommended to omn-qa, the Review Gate decider under producer exclusion, that the Review Gate not pass until CR-001 to CR-005 close and this review is repeated; the decision is omn-qa's.

## Open Questions

| ID | Question | Blocking | Owner | Affects |
|---|---|---|---|---|
| Q-001 | Which encoder versions must the filmed path support (IR Q-001)? | no | architect | F-003, CR-003 |
| Q-002 | Is a network speech engine acceptable at all, and only on explicit opt-in? | no | omn-tech-lead | F-004, CR-004 |
| Q-003 | Does code committed before the implementation phase (IR V-001) satisfy the workflow's phase order? | no | omn-tech-lead | Review Scope |
