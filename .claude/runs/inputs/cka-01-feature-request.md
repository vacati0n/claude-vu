# Feature Request — CKA-01: Declare PyYAML and make `doctor` detect missing runtime deps

## Source

Ticket CKA-01 in `docs/claudekit-adoption-backlog.md`, Epic A — Verification baseline
(Days 0–30). Source recommendation: R1 of the ClaudeKit Adoption Review (2026-08-27).
Type: Task. Priority: Highest. Effort: S. Depends on: nothing.

## Request

The `omn-agent` CLI imports PyYAML at runtime (agent manifests, registry files are YAML),
but `pyproject.toml` declares `dependencies = []`, and `README.md` line 10 claims the tool
is "standard library only". A `pip install omn-agent` into a clean virtual environment
therefore produces an installation whose runtime dies on `import yaml`, while
`omn-agent validate` / `omn-agent doctor` certify that same installation as healthy,
because `omn_agent/validator.py::_check_python` only `compile()`s the installed runtime
files and never resolves their imports.

Three deliverables:

1. Declare `pyyaml` in `dependencies` in `pyproject.toml` so a clean install pulls it.
2. Correct the "standard library only" claim in `README.md` (line 10) to match reality.
3. Extend `omn_agent/validator.py::_check_python` (currently `compile()`-only) to resolve
   top-level imports of installed runtime files, so `validate`/`doctor` report a finding
   that names the missing module instead of certifying a dead runtime.

## Acceptance criteria (from the ticket, verbatim)

- `pip install` in a clean venv pulls PyYAML.
- `omn-agent doctor` against an install in an env without PyYAML reports a finding
  (not OK) and names the module.
- Existing `tests/` remain green.

## Constraints

- Additive check only: the ticket list forbids altering `record_gate_decision`, the gate
  matrix semantics, producer exclusion, `runner._require_approval`, or any human-block path.
- Definition of done for every ticket in the backlog: `tests/` green, all `verify_*.py`
  proof scripts PROVEN, no change to gate-decision behavior, and where docs were touched,
  `user-guide.html` updated to match.

## Priority and deadline

Highest priority; Phase 1 (Days 0–30) of the adoption plan. Blocks CKA-03 (CI gating)
together with CKA-02.
