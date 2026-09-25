# Change Request — Embed the necessity and reuse ladder in existing contracts

## Requested change set

The smallest integration that produces the requested behaviour, as proposed by the operator
after inspecting every layer. The architect evaluates it against alternatives and may narrow
it; widening it requires a recorded reason under the same ladder.

| Surface | File | Change |
|---|---|---|
| Written standard | `skills/architecture/clean-architecture-checklist.md` (skill S01) | Add sections stating the ladder, the minimum-necessary-change definition, the safety floor, and the seven review questions; add one anti-pattern and one common mistake. Keep the heading `Skill: Architecture Foundations` unchanged, because the registry `displayName` indexes it |
| Skill identity | `registry/skills.yaml`, `skills/agent-skill-matrix.md` | S01 version 1.0.0 to 1.1.0 (additive guidance is a MINOR change under `domain-model/skill-specification.md`), in the registry record and the Skill Catalog row |
| Architect behaviour | `agents/architect/reasoning.md` | A6 Reuse Survey: candidates are existing components, the standard library, native platform or framework capability, and already-installed dependencies; a `none-found` basis names which of these were searched; a capability no statement requires is recorded as out of scope, not surveyed. A9: introducing a new external dependency is architecture-significant |
| Architect self-check | `agents/architect/quality.md` | A7.3 wording names the candidate kinds a `none-found` basis must cover, so the check states the same rule as the procedure |
| Implementer behaviour | `agents/omn-dev-1-implement/reasoning.md` | Stage 3: choose each entry's route by the ladder, stopping at the first rung that holds; a new file, abstraction, or dependency is justified by the rung that required it. Stage 5: no speculative abstraction, no refactoring of code the accepted change does not touch, no safety-floor item removed or weakened to shorten the change |
| Implementer output | `agents/omn-dev-1-implement/output.md` | `Approach taken` additionally names the ladder rung that justified any new abstraction, file, or dependency. No structural change; the validator's field checks are unaffected |
| Implementer self-check | `agents/omn-dev-1-implement/quality.md` | One Blocking boundary check: no safety-floor item was removed or weakened to reduce code. One not-machine-checkable obligation: every new abstraction, file, or dependency is justified in `Approach taken` |
| Reviewer behaviour | `agents/omn-dev-2-reviewer/reasoning.md` | Stage 4, maintainability lens: apply the seven questions against S01; the seventh routes to the correctness or security lens; a finding is never that the change could be shorter |
| Packaging mirror | `omn_agent/_bundled_payload/**` | Refresh with `python tests/test_bundled_payload.py --sync`; `tests/test_bundled_payload.py` fails on any drift |

Nothing else changes. In particular: no runtime module, no template, no validator, no
workflow specification, no manifest, no host registration, no agent version, no gate matrix
row, no registry record other than the S01 version, no new file.

## Draft wording for the written standard

Offered as the requested content; the implementer may tighten wording, never weaken a rule.

```text
## Necessity and Reuse Ladder

Applies to every design option, every change-set entry, and every review of a change.
Understand the problem first: read the task and the code it touches, and trace the real
flow end to end. Then climb the ladder and stop at the first rung that holds.

1. Does this need to exist? A capability no accepted statement requires is not built; it
   is recorded as out of scope or raised as an open question to the owning role.
2. Does the codebase already have it? Reuse the existing helper, component, or pattern.
3. Does the standard library solve it? Use it.
4. Does the platform or framework in use solve it natively? Use it.
5. Does an already-installed dependency solve it? Use it.
6. Can it be written directly in a few lines at the call site? Write it there.
7. Only then: implement the minimum code necessary. A new abstraction, file, or dependency
   is introduced only when the reason no lower rung held is recorded.

### Minimum necessary change

Required behaviour, required safety, required integration, and required tests together
are the minimum necessary change. Everything outside that boundary requires a recorded
justification: opportunistic refactoring, cleanup of code the change does not touch,
speculative generalization, and configuration or extension points for requirements that
do not yet exist.

### Safety floor

The ladder minimizes unnecessary code, never necessary protection. No simplification may
remove or weaken input validation at a trust boundary, error handling that prevents data
loss, authorization or audit paths, accessibility, observability the design requires, data
integrity, or the tests that prove the change. A shorter implementation is not
automatically better: correctness, readability, and maintainability are requirements, and
line count is not a criterion. Where two equally small solutions differ, the
edge-case-correct one is chosen.

### Review questions

A change is measured against this ladder with seven questions, each answered against the
accepted change and the code, never against line count:

- Existence: was something built that no accepted statement requires?
- Reuse: does the change duplicate something the codebase already provides?
- Dependency: was a dependency added where the standard library, the platform, or an
  installed dependency already served?
- Abstraction: was an interface, wrapper, factory, helper class, or configuration point
  introduced before a second concrete use required it?
- Complexity: does a simpler implementation exist with the same behaviour and the same
  safety?
- Scope: did the change touch code the accepted change did not require?
- Safety: did a simplification remove or weaken anything the safety floor protects?

A finding under the first six questions is a maintainability or architecture finding at
the severity the evidence supports. A finding under the seventh is a correctness or
security finding.
```

Anti-pattern to add: "Speculative abstraction, generalization, or configuration for a
requirement that does not exist." Common mistake to add: "Reducing line count by removing
validation, error handling, or tests."

## Why these surfaces and not others

- The reviewer's own contract forbids a finding without a written standard ("standard
  before opinion"), so over-engineering cannot be raised as a finding today: the written
  standard is the enabling change, and S01 is already the skill every affected phase loads
  and the one the quality-scan workflow already uses for "structural and abstraction
  judgement". Extending S01 is rung 2 of the ladder applied to the ladder itself; a new S13
  would be rung 7 with a taxonomy column, a registry record, a catalog row, and a matrix
  column it does not need.
- The planner's R13 already fails an untraced task as invented scope, and the product
  owner's Stage 3 already requires explicit exclusions. Rung 1 is therefore already
  enforced upstream of design; those contracts are not touched.
- Agent contract versions stay at 1.0.0. Every host registration pins
  `metadata.version is 1.0.0` and aborts otherwise, and the gate auto-approval policy keys
  precedent on producing-agent version; a version bump is a governance decision for the
  tech lead and is recorded as an open question, not taken here.
- No runtime change: S01 already reaches every affected agent through the manifest skill
  bindings and the phase context slices the runtime freezes, so no slice member is added
  and `RUNTIME_VERSION` stays 0.5.0.
