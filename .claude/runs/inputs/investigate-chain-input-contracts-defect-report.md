# Defect Report — The investigate workflow cannot hand a phase's artifact to the next phase

## Summary

No run of the `investigate` workflow can complete under the runtime without operator-performed
work. Between consecutive phases, the runtime offers the upstream artifact to the next agent under
the producing agent's own output identifier, and the consuming agent's manifest does not list that
identifier as an accepted input. The next phase then blocks at guard G5-INPUT with "no accepted
input type supplied". The same agents own the phases of the `research` workflow, which is expected to
fail the same way. Separately, the self-hosting profile routes `/investigate` with an input type that
no agent declares.

## Mechanism (verified by the operator against the source and the manifests)

- `runtime/framework_runtime.py`, function `upstream_inputs`, offers each completed upstream
  artifact under `artifact_identifier`, which is the identifier the producing agent's manifest gives
  its own output. `resolve_input_contract` then rejects the phase when none of the supplied types is
  among the consuming agent's `inputs.accepted` identifiers.
- Output identifiers and accepted inputs, read from the manifests of the four agents involved:

| Hand-off | Upstream identifier offered | Consuming agent accepts |
|---|---|---|
| problem-framing to technical-discovery | `requirement-framing` (omn-business-analyst output) | omn-context-agent: `framed-objective`, `research-brief`, `investigation-question`, `research-question` |
| technical-discovery to option-analysis | `investigation-report` (omn-context-agent output) | omn-tech-lead accepts `investigation-report`: this hand-off works |
| option-analysis to recommendation | `technical-recommendation` (omn-tech-lead output) | omn-tech-lead: `investigation-report`, `review-package`, `validation-report`, `technical-design` |
| recommendation to publication | `technical-recommendation` (omn-tech-lead output) | omn-documentation: `implementation-report`, `validation-report`, `review-package`, `deployment-status` |

- The context agent accepts `framed-objective`, and nothing in the runtime or any manifest produces
  an artifact under that identifier.
- The self-hosting profile's routing table row `decision-support` lists `investigation-request` as
  the required input. No agent manifest, registry record or runtime file declares that identifier.
  The entry agent, omn-business-analyst, accepts `business-intent`, `problem-statement` and
  `requirement-input`, and its manifest says a problem statement is the input of an `investigate` run.

## Observed behaviour

- A run planned with the profile's input type blocked at its entry phase: "no accepted input type
  supplied; accepted: business-intent, problem-statement, requirement-input".
- A run planned with `problem-statement` completed `problem-framing`, then `technical-discovery`
  blocked with "no accepted input type supplied; accepted: framed-objective, research-brief,
  investigation-question, research-question". Supplying `investigation-question` as an extra input
  up front is a workaround that has to be known in advance.
- In run `run-437e2f765e4b`, `technical-discovery` and `option-analysis` completed, then
  `recommendation` blocked with "no accepted input type supplied; accepted: investigation-report,
  review-package, validation-report, technical-design". Its successor `publication` stays pending.
  Under the self-hosting Completion Rule a run with a pending phase fails check C-3, so the
  self-hosting verifier check S7 fails on that run.

## Expected behaviour

Each phase of `investigate` (and of `research`, which shares agents and artifact types) accepts the
artifact its Phase Model Input column names from the previous phase, so a run can progress from entry
to the last phase with every phase dispatchable once its predecessor has committed. The profile routes
`/investigate` with an input type the entry agent accepts.

## Reproduction

1. `python runtime/self_hosting.py route --intent decision-support` names the input
   `investigation-request`; plan a run with it and read the blocked entry phase.
2. Plan a run with `problem-statement`, complete problem-framing (any validated artifact), and read
   the state of technical-discovery.
3. The manifests listed above can be read directly to see the missing identifiers.

## Severity and impact

Medium to high. The framework declares all 37 phases dispatchable and its profile routes
decision-support changes to `/investigate`, yet no investigation can finish without operator-performed
work, and one such unfinished run now fails self-hosting check S7. The analyst should confirm severity.

## Constraints

- Keep the guard's protective purpose: an input type that no agent accepts must still be rejected.
- A manifest, registry or profile change is a framework contract change: the analysis must establish
  whether agent versions, host registrations or registry records must change with it and how verifiers
  (`verify_manifests`, `verify_registry_coverage`, the bundled payload test) treat that.
- Decide whether the repair belongs in the manifests (accept the upstream identifiers), in the runtime
  (an alias from an output identifier to an accepted abstract type such as `framed-objective`), in the
  profile, or in a combination, by the necessity and reuse ladder: the smallest change that removes the
  cause for every affected workflow. Report whether `research` has the same four gaps.
- Do not weaken validators, gates, the Phase Model tables or the producer exclusion rule.
- Do not modify committed run evidence, including runs `run-437e2f765e4b`, `run-d8937789961e` and
  `run-5f4422f26c3e`.
- Add automated regression tests that fail before the repair and pass after, covering each hand-off
  for `investigate` and `research` without invoking a model, and the profile route.
- Acceptance outcome to show after the repair: for an `investigate` run, every phase passes guard
  G5-INPUT once its predecessor's artifact is committed (demonstrate with a scratch run outside the
  repository, not with committed evidence).
