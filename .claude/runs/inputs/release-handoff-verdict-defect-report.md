# Defect Report — The documentation agent cannot complete an implement-feature release handoff

## Summary

`omn-documentation` is registered to own `documentation-and-release-handoff`, the last phase of
`implement-feature`. That phase declares its inputs as "verification report, change summary" on the
`release-handoff` communication basis and has no deployment step. Deployment belongs to the separate
`release` workflow. The agent's release-verdict contract, however, only describes deployment
outcomes. A handoff whose change has been verified in the run's working tree but not deployed has
no truthful verdict that the validator accepts, so the phase cannot produce a passing artifact
without misstating what happened, and an `implement-feature` run cannot close honestly.

## Mechanism (verified by the operator against the source)

- `agents/omn-documentation/reasoning.md`, Stage 8 "Determine the release position": the verdict
  "is read off this table against the supplied deployment status. It is not chosen." Its rows are
  `released` (every change in scope reached its target environment), `partial`, `rolled-back`, and
  "withheld / `blocked`" for "deployment status absent or unreadable for a phase that requires it".
  No row covers a phase that does not require a deployment status.
- `agents/omn-documentation/output.md:76` declares `releaseVerdict` as `released` | `partial` |
  `rolled-back`; `agents/omn-documentation/quality.md:92` check `R1` (Blocking) requires one of
  those three; `runtime/release_note_validator.py:32` enforces `VERDICTS = ("released", "partial",
  "rolled-back")`; `templates/release-note.md:36` lists the same three.
- `workflows/implement-feature.md:44`: `documentation-and-release-handoff` takes "verification
  report, change summary" and emits `release-note.md` "on the `release-handoff` communication
  basis". It is not supplied a `deployment-status`.

## Observed behaviour

- Run `run-c9fb8d5bbb32` (`/implement`, knowledge management loop), invocation
  `inv-c9fb8d5bbb32-06-001`: after both the Review Gate and the Verification Gate approved, the
  `omn-documentation` subagent wrote `releaseVerdict: withheld` with status `blocked` and envelope
  status `escalation_required` (`context-absent`). It self-checked 60 rules: 59 pass and `R1` fails.
  Twice the operator, acting as omn-orchestrator, ruled that `released` applies and cited three
  precedents. Both times the agent declined, because `released` asserts that the change reached
  its target environment and the evidence does not show that. The run is held at its last phase.
- Precedent runs `run-e0dba6763475`, `run-efe092286625` and `run-ded114f50a46` published `released`
  for the same undeployed working-tree handoff. Their Environment lines say the change "has not been
  merged, released, or deployed to any other environment". The validator accepted them, so the
  contract has been satisfied by a verdict whose defined meaning was not true of those changes.
- Related, already recorded: FC-020 open item `O-006`. The same contract has no verdict for a
  findings publication (`investigate`/`research` `publication` phase), and `partial` in the
  release note of `run-437e2f765e4b` is a placeholder.

## Expected behaviour

For a phase whose workflow declares no deployment step, the documentation agent can read a
truthful release position off its Stage 8 table. The validator, the output contract, the
quality check and the template accept it, and the note does not assert a deployment fact. Phases
that do deploy keep their current verdicts and rules unchanged.

## Reproduction

1. Plan any `implement-feature` run and carry it to `documentation-and-release-handoff` with both
   quality-review gates approved (or read run `run-c9fb8d5bbb32`).
2. Dispatch the phase. A contract-faithful agent applies Stage 8, finds no row for a phase without
   a deployment status, and emits `withheld`. `python .claude/runtime/release_note_validator.py`
   over that artifact fails `R1`.

## Impact

Every `implement-feature` run, and every framework self-hosting change routed through `/implement`,
ends in this phase. Each one either blocks or publishes `released` against its own definition.
Severity: high for governance integrity (the release record misstates deployment); no runtime crash.

## Constraints from the operator

- Do not rewrite the evidence of earlier runs, and do not re-label their verdicts.
- Phases that consume `deployment-status` (`release` workflow) must behave exactly as before.
