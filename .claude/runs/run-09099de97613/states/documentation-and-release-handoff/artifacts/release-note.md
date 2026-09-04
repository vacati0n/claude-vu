```yaml
releaseNote:
  releaseId: OMT-01-release-note
  version: 0+OMT-01-unreleased
  sourceInputs:
    - type: final-change-summary
      reference: runs/run-09099de97613/states/implementation/artifacts/implementation-report.md
    - type: verification-report
      reference: runs/run-09099de97613/states/quality-review/artifacts/review-package.md
  producedBy: omn-documentation
  agentVersion: 1.0.0
  schemaVersion: 1.0.0
  status: complete
  releaseVerdict: partial
  inputDigest: sha256:06a6e104dd467eb3eab86108dc0e77fa
  contextDigest: sha256:bc0fb4ee128c1855f84c63b3ea12319c
```

## Metadata

- Version: 0+OMT-01-unreleased
- Release date and time: 2026-08-28, at the close of run `run-09099de97613`
- Environment: The framework repository. The change is inert on landing: nothing runs until an operator invokes the new entry point.
- Release owner: omn-orchestrator

## Highlights

- Feature additions: `/optimize-memory`, an operator entry point that rewrites the framework's durable knowledge surfaces — memory, context, and the standing instruction files — to a lower token cost without changing what they instruct. It routes to the existing Refactor lifecycle, because the claim it makes is the invariant claim that lifecycle exists to hold to account. The runtime module `runtime/optimize_memory.py` performs the pass: it discovers what is in scope, proposes a denser rewrite of each file, judges every candidate against its original by a mechanical invariant check, records the outcome, and can undo an applied pass. Also added: an index in `config/self-hosting-profile.md` recording each accepted change proposal against the run that carried it.
- Bug fixes: One defect found and corrected inside this change before release, not carried in from an earlier one. The quality review found that both the pre-image write and the dry-run candidate write joined the session directory with a path that is absolute for a file outside the repository — a join that discards everything to its left. For a scope root outside the repository, backing up a file would have overwritten it with itself and a dry run would have written its candidate straight over the original. Corrected, with five regression tests covering each path shape.
- Improvements: `commands/README.md` and `commands/command-catalog.md` now count and list eleven command contracts rather than ten.

## Technical Changes and Compatibility

- API or contract changes: One additive record in `registry/commands.yaml`, identifier `optimize-memory`, primary workflow `refactor`. No existing record, lookup, or schema changed.
- Database or migration impact: None. No data is migrated and no artifact or run structure changes shape.
- Configuration changes: The optimizer model can be overridden by the `OPTIMIZE_MEMORY_MODEL` environment variable. Nothing else is configurable and nothing needs configuring for the framework to behave as it did before.
- Backward compatibility notes: Fully backward compatible. The command record is additive; command resolution is by identifier, so no existing route changes. The new module imports nothing from the framework runtime and nothing in the framework imports it, so no existing surface acquires the new external dependency — every command that worked before this change works after it, with or without a provider client library installed. The appended section in `config/self-hosting-profile.md` sits after the last parsed heading, so the profile parses and routes exactly as before. No workflow, phase, gate, role contract, or artifact validator changed: 37 phases across 8 workflows, unmoved.

## Operational Notes

- Deployment considerations: Nothing to deploy and nothing to restart. The entry point does nothing until invoked, and its first invocation modifies nothing by default. Using it against a live pass requires a provider client library and resolvable credentials in the environment; neither is needed for the framework itself, nor for the entry point's scan and restore surfaces.
- Monitoring and alerts: Watch the per-pass verdict counts in each session report — specifically how many candidates were refused and which invariant each broke. A pass in which nothing is ever refused looks identical to a pass in which everything was correct, and is the signal that the judgement has stopped working.
- Rollback criteria: Roll the capability back by removing the command record and the command contract together and deleting the module; a partial removal is caught by coverage check `C1`. Roll back an applied optimization pass, which is a separate operation, with `python .claude/runtime/optimize_memory.py restore --manifest runs/optimize-memory/<stamp>/manifest.json`. Neither implies the other.

## Validation Summary

- Test status: 31 automated checks in `tests/test_optimize_memory.py`, all passing, re-executed by the quality review rather than accepted from the implementation report. 6 of 6 framework coverage checks passing, with 11 of 11 active command records resolving. The governance profile parses and routes. The pre-existing test suite is unaffected.
- Known risk acceptance: Two risks accepted at the Verification Gate. The compression request path ships without an end-to-end exercise, because this environment carries no client library and no credential; its failure modes are recorded per file and leave originals untouched, so the exposure is a lost session rather than lost content. The identifier pattern may protect a token that is not an identifier, which produces a false refusal — the safe direction of error for a rule whose job is to refuse.
- Post-release checks: Before the first pass is applied to any knowledge surface, exercise the compression request path end to end in an environment that has the dependency, per correction request `CR-004`. Then run the pass in its default non-modifying form and read the recorded difference record before adding the flag that overwrites.

## Known Issues

| ID | Issue | Impact | Workaround | Tracking |
|---|---|---|---|---|
| `K-001` | The compression request path has never been executed end to end; this environment has no provider client library and no credential | The first live pass is also the first execution of that path, and may fail | Every failure on that path is recorded against the file and leaves the original untouched, so a failed first pass costs a session and no content | `CR-004`; design assumption `A-002` |
| `K-002` | The guarantee is structural and identifier-level, not semantic. A candidate that preserves every heading, table row, identifier, link, code block, and list item may still have reworded prose in a way that changes an obligation expressed only in prose | A reader who assumes "lossless" means "meaning preserved" will assume more than the check provides | Read the recorded unified diff before applying a pass; the command contract states the distinction explicitly | `Q-002` of the quality review; design risk `R-001` |
| `K-003` | Two low findings remain open: a redundant construction in the fenced-block comparison, and no coverage for the session report renderer | Neither affects what the pass does; the renderer produces advisory output only | None required | `CR-003`, `CR-005` |

## Communication

- Stakeholders notified: The operator who requested the change, as the requester of run `run-09099de97613`; the Design Gate and Review Gate owners, through the recorded decisions on that run; future readers, through this note and the change proposal that indexes the run.
- Support handoff notes: The command contract at `commands/optimize-memory.md` is the operator-facing documentation and states the full path from scan to restore. Two points carry most of the support burden and are worth repeating: the pass modifies nothing unless it is explicitly told to, and the guarantee it makes is the invariant table in that contract and not a claim about meaning. An operator asking whether the capability is safe to apply should be pointed at the difference record it writes, which is the control the design names for everything the mechanical check does not cover.
