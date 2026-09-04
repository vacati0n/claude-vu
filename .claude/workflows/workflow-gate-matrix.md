# Workflow Gate Matrix

## Purpose

Map each workflow to mandatory gate ownership for consistent quality decisions.

| Workflow | Gate | Required Owners |
|---|---|---|
| implement-feature | Scope Gate | omn-product-owner, omn-business-analyst |
| implement-feature | Planning Gate | omn-tech-lead, omn-orchestrator |
| implement-feature | Design Gate | omn-architect, omn-tech-lead |
| implement-feature | Review Gate | omn-dev-2-reviewer, omn-qa |
| implement-feature | Verification Gate | omn-qa |
| implement-feature | Closure Gate | omn-orchestrator, omn-documentation |
| fix-bug | Triage Gate | omn-dev-1-bug-analyst, omn-tech-lead |
| fix-bug | Fix Gate | omn-dev-2-reviewer |
| fix-bug | Verification Gate | omn-qa, omn-dev-2-reviewer |
| fix-bug | Closure Gate | omn-orchestrator, omn-documentation |
| investigate | Framing Gate | omn-business-analyst, omn-product-owner |
| investigate | Technical Gate | omn-context-agent, omn-architect |
| investigate | Recommendation Gate | omn-tech-lead, omn-orchestrator |
| research | Framing Gate | omn-business-analyst, omn-product-owner |
| research | Technical Validity Gate | omn-context-agent, omn-architect |
| research | Recommendation Gate | omn-tech-lead, omn-orchestrator |
| refactor | Invariant Gate | omn-architect, omn-tech-lead |
| refactor | Implementation Gate | omn-dev-2-reviewer |
| refactor | Regression Gate | omn-qa, omn-dev-2-reviewer |
| refactor | Closure Gate | omn-orchestrator, omn-documentation |
| code-quality-scan | Quality Handoff Gate | omn-dev-2-reviewer, omn-tech-lead |
| review-pull-request | Code Quality Gate | omn-dev-2-reviewer, omn-tech-lead |
| review-pull-request | Architecture Gate | omn-architect, omn-tech-lead |
| review-pull-request | Verification Gate | omn-qa, omn-dev-2-reviewer |
| review-pull-request | Merge Gate | omn-tech-lead, omn-orchestrator |
| release | Readiness Gate | omn-tech-lead, omn-qa |
| release | Artifact Gate | omn-dev-2-reviewer, omn-tech-lead |
| release | Deployment Gate | omn-orchestrator, omn-tech-lead |
| release | Communication Gate | omn-documentation, omn-product-owner |

Every gate named by an active workflow Phase Model appears here, and every row names at least
one owner that does not produce the evidence the gate assesses. A gate whose only owner is the
producing role cannot be decided at all, because the Producer Exclusion Rule below forbids
self-approval, so single-owner rows were completed rather than left as latent deadlocks.

### Rows Added or Completed for Producer Exclusion

| Workflow | Gate | Change | Reason |
|---|---|---|---|
| implement-feature | Review Gate | added omn-qa as second owner | omn-dev-2-reviewer owns `quality-review` and produces the findings log the gate assesses |
| fix-bug | Verification Gate | added omn-dev-2-reviewer as second owner | omn-qa owns `regression-validation` and produces the verification evidence |
| fix-bug | Closure Gate | row added | `closure-and-communication` closes with a gate the matrix did not carry |
| investigate | Recommendation Gate | row added | `recommendation` closes with the gate the workflow specification already named |
| research | Framing Gate, Technical Validity Gate | rows added | both gates were named by the workflow specification but absent here |
| refactor | Implementation Gate, Closure Gate | rows added | both gates were named by the workflow specification but absent here |
| refactor | Regression Gate | unchanged, already carried two owners | omn-qa owns `behavioral-validation`, so the decision rests with the omn-dev-2-reviewer entry this row already named |
| review-pull-request | Code Quality Gate, Architecture Gate, Verification Gate, Merge Gate | rows added | the single `Readiness Gate` row this matrix carried named no phase in the workflow's Phase Model; these four are the gates the state machine and the specification declare |
| review-pull-request | Code Quality Gate, Architecture Gate, Verification Gate | second owner added | the first-listed owner of each produces the evidence its gate assesses |
| release | Artifact Gate, Communication Gate | rows added | both gates were named by the workflow specification but absent here |
| release | Artifact Gate, Deployment Gate | second owner omn-tech-lead | omn-dev-2-reviewer owns `artifact-packaging` and omn-orchestrator owns `deployment-execution` |
| code-quality-scan | Quality Handoff Gate | row added with the workflow | omn-dev-2-reviewer owns `repository-quality-scan` and produces the scan package this gate assesses; the decision rests with omn-tech-lead, the human handoff the workflow terminates at |

The retired row is `review-pull-request | Readiness Gate | omn-dev-2-reviewer`. Review
readiness is an entry condition of that workflow, not a gate between two of its phases, and no
Phase Model row referenced it.

## Usage

Use this matrix when validating whether an output can move to the next phase.

The Planner Agent produces the evidence assessed at the implement-feature Planning Gate.
It does not approve that gate, or any other. Gate approval remains with the owners listed
above.

The Architect Agent produces the evidence assessed at the Design, Invariant, Technical,
Technical Validity, and Architecture Gates, including architecture decision records emitted at
status `Proposed`. Accepting those records is a gate decision owned by the listed gate owners,
never by the producing agent. Gate owner entries naming `omn-architect` name the architecture
role now implemented by `architect`; the reference migration is deferred.

A gate is resolvable when this matrix names its workflow and gate. The runtime reads ownership
from here and never invents a decision, so a Phase Model that names a gate absent from this
matrix would hold its successor blocked with no owner able to release it.

## Producer Exclusion Rule

An agent may not approve a gate for an artifact it produced, even when its role appears in
that gate's owner list. Where the producing role is also a listed owner, approval requires a
different listed owner.

This applies today to the Design and Invariant Gates: `architect` produces the technical
design package and the decision records assessed there, so acceptance rests with
`omn-tech-lead`. It also decides the second owner on every row listed in Rows Added or
Completed for Producer Exclusion above. The same rule applies to any future agent whose role
owns a gate its own output must pass.

The rule reads through role aliases. A gate owned by `omn-architect` cannot be approved by
`architect`, because both identifiers name one role.
