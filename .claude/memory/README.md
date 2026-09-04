# Memory Specification

## Memory Model

Memory stores durable engineering knowledge required for consistency across
decisions, implementation, review, and release.

## Persistence

- Memory is persistent across workflow runs.
- Entries must remain addressable and historically traceable.
- Superseded knowledge must be retained with replacement references.

## Update Rules

- Update only when knowledge is validated and reusable.
- Prefer concise, evidence-based statements.
- Avoid transient execution details and unresolved assumptions.
- Link significant updates to decision or release artifacts.

## Ownership

- Product Owner and Business Analyst: business rules and glossary.
- Architect and Tech Lead: architecture and technology stack.
- QA and Reviewer: known issues and quality-related updates.
- Orchestrator: memory consistency and lifecycle governance.
