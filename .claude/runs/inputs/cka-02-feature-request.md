# Feature Request — CKA-02: Ship the framework payload as package data

## Source

Ticket CKA-02 in the adoption backlog under `docs/` (Epic A — Verification baseline,
Days 0–30). Source recommendation: R1 of the ClaudeKit Adoption Review (2026-08-27).
Type: Task. Priority: Highest. Effort: M. Depends on: nothing.

## Request

A non-editable `pip install` of the `omn-agent` wheel produces a CLI that cannot install
anything: the framework payload (the framework payload directory at the repo root —
runtime, registries, agents, workflows, config, templates) is not packaged into the
wheel, and `omn_agent/source.py::find_source` only looks for a framework tree next to
the package checkout (which exists for an editable install of the source repo, but not
for a wheel installed into site-packages). Every fresh-environment user must pass
`--source <path>` to a framework checkout they may not have.

Three deliverables:

1. Package the framework payload into the wheel: `pyproject.toml` package-data (or
   `MANIFEST.in` with include directives) so a non-editable build carries the full
   payload tree — all managed directories plus the seed directories, subject to the
   same exclusion patterns the installer applies (`__pycache__`, `*.pyc`, etc.).
2. Extend `omn_agent/source.py::find_source` to resolve the bundled payload from the
   installed package location as a fallback after the existing candidates (explicit
   `--source` first, then a tree next to the checkout, then the bundled copy), keeping
   the existing error message actionable when nothing resolves.
3. Regenerate the stale egg-info metadata so the sdist/wheel file lists match the new
   packaging configuration.

## Acceptance criteria (from the ticket, verbatim)

- In a clean venv, `pip install <wheel>` (non-editable) then
  `omn-agent init && install && validate` succeeds with no `--source` flag.
- `omn-agent install --dry-run` enumerates the same payload file count as an
  editable install.

## Constraints

- Additive change only: the ticket list forbids altering `record_gate_decision`, the
  gate matrix semantics, producer exclusion, `runner._require_approval`, or any
  human-block path.
- Source-resolution precedence must not change for existing users: an explicit
  `--source` and a checkout-adjacent tree keep winning over the bundled copy.
- Definition of done for every ticket in the backlog: `tests/` green, all `verify_*.py`
  proof scripts PROVEN, no change to gate-decision behavior, and where docs were
  touched, `user-guide.html` updated to match.

## Priority and deadline

Highest priority; Phase 1 (Days 0–30) of the adoption plan. Blocks CKA-03 (CI gating)
together with CKA-01 (already delivered).
