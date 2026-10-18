# AI Engineering Framework

A governed engineering framework for Claude Code: agents, skills, workflows, gates,
templates, and memory for structured delivery, defect resolution, technical investigation,
review, and release. The whole framework lives under `.claude/`, where Claude Code reads it
directly; there is no separate CLI or installer. See `.claude/CLAUDE.md` for the layer model.

The runtime under `.claude/runtime/` needs Python 3.10+ and PyYAML (`pip install pyyaml`).

## Commands

Work starts from a Claude Code slash command. Each command contract in `.claude/commands/`
routes to exactly one workflow (`.claude/registry/commands.yaml`), and the workflow's phases
are carried by the subagents under `.claude/agents/`.

| Command | Workflow |
|---|---|
| `/implement` | `implement-feature` |
| `/bugfix` | `fix-bug` |
| `/refactor` | `refactor` |
| `/investigate` | `investigate` |
| `/research` | `research` |
| `/review` | `review-pull-request` |
| `/quality-scan` | `code-quality-scan` |
| `/test` | `review-pull-request` |
| `/document` | `implement-feature` |
| `/release` | `release` |
| `/optimize-memory` | `refactor` |

`.claude/commands/command-catalog.md` is the authoritative index. Grouped runbooks such as
`/implement:implement-feature` or `/review:review-pr` document how to start a lifecycle
through one of these contracts.

## The runtime

`.claude/runtime/framework_runtime.py` holds run state, dispatches phases to their owner
agents, validates every artifact, and holds each transition at its gate until the owner role
records a decision. The slash commands drive it; it can also be called directly:

```bash
python .claude/runtime/framework_runtime.py plan --command implement     --input feature-request=.claude/runs/inputs/<request>.md
python .claude/runtime/framework_runtime.py status --run-id <run-id>
```

`.claude/runtime/README.md` documents every subcommand, the gate policy, recovery, and demo
mode.

## Changing the framework itself

A framework-internal change is routed, not chosen:

```bash
python .claude/runtime/self_hosting.py classify --path <path>
python .claude/runtime/self_hosting.py route --intent <change-class>
python .claude/runtime/verify_self_hosting.py --release-checklist
```

## Tests

```bash
python -m unittest discover -s tests
python tools/run_tests_parallel.py      # the same suite, in parallel
```

## Continuous integration

`.github/workflows/verify.yml` runs on every pull request and on pushes to the
default branch, on ubuntu and windows, with two surfaces located **by
discovery, never a curated file list**: the unit-test suite above, and every
proof script matching `verify_*.py` under `.claude/runtime/` — each verifier in
its own job on its own runner, so a failing verifier fails CI naming itself and
one verifier's crash or flake (including the timing-sensitive recovery proof)
cannot change any other verifier's result. A verifier passes only when it exits
0 **and** its own `N/N checks passed` summary shows a non-negative verdict.
Adding a `tests/test_*.py` or `verify_*.py` file needs no CI change.

Branch protection binds to four stable check names — renaming any of them is a
contract change:

| Check | Standing |
|---|---|
| `tests-ubuntu` | required from day one |
| `tests-windows` | advisory week 1, required after the flip |
| `verifiers-ubuntu-ok` | advisory week 1, required after the flip |
| `verifiers-windows-ok` | advisory week 1, required after the flip |

Advisory means *absent from the required-checks list* (failures still show
red); `continue-on-error` is never used. The flip is a settings-only change,
enacted only after a default-branch run shows `verify_self_hosting.py` passing
(the pre-existing orphan run directories must be cleaned first). The workflow
never sets `NO_COLOR`, and new verifiers must be self-contained: runnable
alone, with no arguments, in any order.

`docs/user-guide.html` is generated from `docs/USER-GUIDE.md`: edit the
Markdown, then run `python tools/render_user_guide.py` to regenerate the
HTML. The `tests` job also runs `python tools/render_user_guide.py --check`,
which fails a pull request whose HTML is stale and prints the regeneration
command above. A change made directly to `docs/user-guide.html` is discarded
by the next regeneration.
