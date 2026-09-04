"""Per-project branch naming templates.

Stored at ``.omn-agent/config/branch-naming.json`` -- seeded once at
``omn-agent init`` time (flags, an interactive prompt, or sensible defaults)
and then owned by the project, exactly like ``context/`` and ``memory/``.
A missing file is not an error: :func:`load_config` returns the same
defaults it would otherwise have written, so an installation from before
this feature existed keeps working unchanged.

Template tokens: ``{ticket_id}``, ``{short_description}``, and the optional
``{work_type}``. A template is routed by the task's work type -- derived
from its routed command (``implement``/``bugfix``/``refactor``/
``investigate``) unless overridden -- and validated at save time: it must
contain ``{ticket_id}``, use no other tokens, and render (after the
lowercase/hyphen normalization every generated name goes through) to a name
``git check-ref-format`` accepts.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from . import SCHEMA_VERSION
from .common import ExitCode, OmnError, Report
from .manifest import atomic_write
from .repo import framework_root, resolve_target
from .taskplan import load_task

CONFIG_REL = "config/branch-naming.json"
DEFAULTS_REL = "config/branch-defaults.json"
DEFAULT_MAX_LENGTH = 80
DEFAULT_DIVERGENCE_WARNING_THRESHOLD = 100

DEFAULT_TEMPLATES = {
    "feature": "feature/{ticket_id}-{short_description}",
    "bugfix": "bugfix/{ticket_id}-{short_description}",
}

# Routed task command -> work type used to pick a template. Any command (or
# explicit --work-type) not listed here is used verbatim as its own work
# type, falling back to the generic "{work_type}/{ticket_id}-..." pattern.
WORK_TYPE_FOR_COMMAND = {
    "implement": "feature",
    "bugfix": "bugfix",
    "refactor": "refactor",
    "investigate": "chore",
}

KNOWN_TOKENS = {"ticket_id", "short_description", "work_type"}
_TOKEN_RE = re.compile(r"\{([a-zA-Z_]+)\}")
_INVALID_CHARS_RE = re.compile(r"[^a-z0-9_-]+")
_DASH_RUN_RE = re.compile(r"-{2,}")


def work_type_for_command(command: str) -> str:
    return WORK_TYPE_FOR_COMMAND.get(command, command)


def config_path(fw_dir: Path) -> Path:
    return fw_dir / CONFIG_REL


# ---- load / validate / render ---------------------------------------------

def load_config(fw_dir: Path) -> dict:
    """Effective config: saved overrides merged over the built-in defaults."""
    path = config_path(fw_dir)
    templates = dict(DEFAULT_TEMPLATES)
    max_length = DEFAULT_MAX_LENGTH
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"{CONFIG_REL} is unreadable: {exc}",
                           hint="fix the JSON, or re-run 'omn-agent branch-config "
                                "set' to rewrite it")
        if not isinstance(data, dict):
            raise OmnError(ExitCode.UNEXPECTED, f"{CONFIG_REL} is not a JSON object")
        templates.update(data.get("templates") or {})
        max_length = data.get("maxLength", DEFAULT_MAX_LENGTH)
        if not isinstance(max_length, int) or isinstance(max_length, bool) \
                or max_length <= 0:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"{CONFIG_REL}: maxLength must be a positive integer")
    return {"templates": templates, "maxLength": max_length}


def load_branch_defaults(fw_dir: Path) -> dict:
    """Per-repo branch defaults: the integration branch to branch from when
    ``--base`` isn't passed, and the divergence-warning threshold.

    Stored at ``.omn-agent/config/branch-defaults.json``. A missing file is
    not an error -- ``defaultBase: None`` keeps today's main/master fallback,
    so an installation from before this feature existed keeps working
    unchanged. A team whose integration branch is ``develop`` writes
    ``{"defaultBase": "develop"}`` once instead of passing ``--base`` on
    every invocation.
    """
    path = fw_dir / DEFAULTS_REL
    default_base = None
    threshold = DEFAULT_DIVERGENCE_WARNING_THRESHOLD
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"{DEFAULTS_REL} is unreadable: {exc}",
                           hint="fix the JSON (keys: defaultBase, "
                                "divergenceWarningThreshold)")
        if not isinstance(data, dict):
            raise OmnError(ExitCode.UNEXPECTED, f"{DEFAULTS_REL} is not a JSON object")
        default_base = data.get("defaultBase")
        if default_base is not None and (not isinstance(default_base, str)
                                         or not default_base.strip()):
            raise OmnError(ExitCode.UNEXPECTED,
                           f"{DEFAULTS_REL}: defaultBase must be a non-empty "
                           f"string or null")
        threshold = data.get("divergenceWarningThreshold",
                             DEFAULT_DIVERGENCE_WARNING_THRESHOLD)
        if not isinstance(threshold, int) or isinstance(threshold, bool) \
                or threshold <= 0:
            raise OmnError(ExitCode.UNEXPECTED,
                           f"{DEFAULTS_REL}: divergenceWarningThreshold must be "
                           f"a positive integer")
    return {"defaultBase": default_base,
            "divergenceWarningThreshold": threshold}


def _tokens_in(template: str) -> list[str]:
    return _TOKEN_RE.findall(template)


def check_valid_git_branch_name(name: str):
    proc = subprocess.run(["git", "check-ref-format", "--branch", name],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"'{name}' is not a valid git branch name",
                       hint=(proc.stderr or proc.stdout or "").strip())


def render_template(template: str, *, ticket_id: str, short_description: str,
                    work_type: str) -> str:
    values = {"ticket_id": ticket_id, "short_description": short_description,
              "work_type": work_type}

    def _sub(m: re.Match) -> str:
        name = m.group(1)
        if name not in values:
            raise OmnError(ExitCode.INVALID_TARGET,
                           f"branch template uses unknown token '{{{name}}}'",
                           hint=f"supported tokens: "
                                f"{', '.join('{' + t + '}' for t in sorted(KNOWN_TOKENS))}")
        return values[name]

    return _TOKEN_RE.sub(_sub, template)


def sanitize_branch_name(raw: str, max_length: int = DEFAULT_MAX_LENGTH) -> str:
    """lowercase; replace anything outside [a-z0-9_-] with '-'; collapse
    duplicate '-'; trim leading/trailing '-'; enforce max_length -- applied
    per '/'-segment so template-authored path structure (e.g. 'feature/...')
    survives normalization instead of being flattened."""
    segments = []
    for seg in raw.split("/"):
        s = seg.lower()
        s = _INVALID_CHARS_RE.sub("-", s)
        s = _DASH_RUN_RE.sub("-", s)
        s = s.strip("-")
        if s:
            segments.append(s)
    result = "/".join(segments)
    if max_length and len(result) > max_length:
        result = result[:max_length].rstrip("-/")
        result = "/".join(s for s in result.split("/") if s)
    return result


def validate_template(work_type: str, template: str,
                      max_length: int = DEFAULT_MAX_LENGTH):
    """Raise OmnError with a clear message if ``template`` can't be saved."""
    if not template or not template.strip():
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"branch template for '{work_type}' is empty")
    if template.count("{") != template.count("}"):
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"branch template for '{work_type}' has unbalanced "
                       f"braces: {template!r}")
    if "{ticket_id}" not in template:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"branch template for '{work_type}' must contain the "
                       "{ticket_id} token", hint=f"got: {template!r}")
    unknown = sorted(set(_tokens_in(template)) - KNOWN_TOKENS)
    if unknown:
        raise OmnError(
            ExitCode.INVALID_TARGET,
            f"branch template for '{work_type}' uses unknown token(s): "
            f"{', '.join('{' + t + '}' for t in unknown)}",
            hint=f"supported tokens: "
                 f"{', '.join('{' + t + '}' for t in sorted(KNOWN_TOKENS))}")
    sample = render_template(template, ticket_id="PROJ-123",
                             short_description="sample-change", work_type=work_type)
    candidate = sanitize_branch_name(sample, max_length)
    if not candidate:
        raise OmnError(ExitCode.INVALID_TARGET,
                       f"branch template for '{work_type}' produces an empty "
                       f"branch name after sanitization",
                       hint=f"template: {template!r}")
    check_valid_git_branch_name(candidate)


def template_for(templates: dict, work_type: str) -> str:
    if work_type in templates:
        return templates[work_type]
    if work_type in DEFAULT_TEMPLATES:
        return DEFAULT_TEMPLATES[work_type]
    return f"{work_type}/{{ticket_id}}-{{short_description}}"


def resolve_branch_name(fw_dir: Path, *, command: str, ticket_id: str,
                        short_description: str,
                        work_type: str | None = None) -> tuple[str, str, str]:
    """Returns (branch_name, work_type, template_used)."""
    cfg = load_config(fw_dir)
    wt = work_type or work_type_for_command(command)
    tmpl = template_for(cfg["templates"], wt)
    raw = render_template(tmpl, ticket_id=ticket_id,
                          short_description=short_description, work_type=wt)
    name = sanitize_branch_name(raw, cfg["maxLength"])
    if not name:
        raise OmnError(ExitCode.UNEXPECTED,
                       f"branch template for '{wt}' produced an empty branch "
                       "name", hint=f"template: {tmpl!r}")
    check_valid_git_branch_name(name)
    return name, wt, tmpl


# ---- persist ----------------------------------------------------------------

def save_config(fw_dir: Path, *, templates: dict, max_length: int) -> dict:
    """Validate every effective template, then persist the full config."""
    if not isinstance(max_length, int) or isinstance(max_length, bool) \
            or max_length <= 0:
        raise OmnError(ExitCode.INVALID_TARGET,
                       "--max-length must be a positive integer")
    merged = dict(DEFAULT_TEMPLATES)
    merged.update(templates)
    for wt, tmpl in merged.items():
        validate_template(wt, tmpl, max_length)
    data = {"schemaVersion": SCHEMA_VERSION, "maxLength": max_length,
            "templates": merged}
    path = config_path(fw_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, (json.dumps(data, indent=2, sort_keys=True) + "\n")
                .encode("utf-8"))
    return data


def seed_config(fw_dir: Path, *, feature_template: str | None,
                bugfix_template: str | None, max_length: int | None,
                report: Report) -> bool:
    """Write branch-naming.json once, if it doesn't already exist -- seeded
    exactly like context/ and memory/, never overwriting project-owned
    config on a later 'init'. Returns whether it wrote anything."""
    if config_path(fw_dir).exists():
        return False
    templates = dict(DEFAULT_TEMPLATES)
    if feature_template:
        templates["feature"] = feature_template
    if bugfix_template:
        templates["bugfix"] = bugfix_template
    data = save_config(fw_dir, templates=templates,
                       max_length=max_length or DEFAULT_MAX_LENGTH)
    report.success("I-BRANCHCFG", f"wrote {CONFIG_REL} (feature: "
                   f"{data['templates']['feature']!r}, bugfix: "
                   f"{data['templates']['bugfix']!r})")
    return True


def seed_config_interactive(fw_dir: Path, *, max_length: int | None,
                            report: Report, input_fn) -> bool:
    if config_path(fw_dir).exists():
        return False
    print("Branch naming templates (press Enter to accept the default):")

    def ask(prompt: str, default: str) -> str:
        try:
            answer = input_fn(f"  {prompt} [{default}]: ").strip()
        except EOFError:
            answer = ""
        return answer or default

    feature = ask("Feature/implement branch template", DEFAULT_TEMPLATES["feature"])
    bugfix = ask("Bugfix branch template", DEFAULT_TEMPLATES["bugfix"])
    return seed_config(fw_dir, feature_template=feature, bugfix_template=bugfix,
                       max_length=max_length, report=report)


def _require_fw_dir(target: Path) -> Path:
    fw_dir = framework_root(target)
    if not fw_dir.is_dir():
        raise OmnError(ExitCode.INCOMPLETE,
                       "framework is not initialized in the target",
                       hint="run 'omn-agent init <target>' (or 'omn-agent install') "
                            "first")
    return fw_dir


# ---- CLI: branch-config show/set/preview -----------------------------------

def cmd_branch_config_show(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("branch-config show", str(target))
    fw_dir = _require_fw_dir(target)
    saved = {}
    if config_path(fw_dir).exists():
        try:
            saved = json.loads(config_path(fw_dir).read_text(encoding="utf-8-sig")) \
                .get("templates") or {}
        except (OSError, ValueError):
            saved = {}
    cfg = load_config(fw_dir)
    report.info("BC-MAXLEN", f"maxLength: {cfg['maxLength']}")
    for wt, tmpl in sorted(cfg["templates"].items()):
        origin = "project-configured" if wt in saved else "default"
        report.info("BC-TEMPLATE", f"{wt}: {tmpl!r} ({origin})")
    if not config_path(fw_dir).exists():
        report.info("BC-NONE", f"{CONFIG_REL} does not exist yet; showing "
                    "built-in defaults")
    return report.finish()


def _parse_extra_templates(values: list[str]) -> dict:
    out = {}
    for v in values:
        if "=" not in v:
            raise OmnError(ExitCode.INVALID_TARGET,
                           f"--template expects WORKTYPE=TEMPLATE, got: {v!r}")
        wt, tmpl = v.split("=", 1)
        wt = wt.strip()
        if not wt:
            raise OmnError(ExitCode.INVALID_TARGET,
                           f"--template has an empty work type: {v!r}")
        out[wt] = tmpl
    return out


def cmd_branch_config_set(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("branch-config set", str(target))
    fw_dir = _require_fw_dir(target)

    current = load_config(fw_dir)
    templates = dict(current["templates"])
    if args.feature_template:
        templates["feature"] = args.feature_template
    if args.bugfix_template:
        templates["bugfix"] = args.bugfix_template
    templates.update(_parse_extra_templates(args.template))
    max_length = args.max_length or current["maxLength"]

    if not (args.feature_template or args.bugfix_template or args.template
            or args.max_length):
        raise OmnError(ExitCode.INVALID_TARGET,
                       "nothing to set -- pass --feature-template, "
                       "--bugfix-template, --template WORKTYPE=TEMPLATE, or "
                       "--max-length")

    if args.dry_run:
        for wt, tmpl in sorted(templates.items()):
            validate_template(wt, tmpl, max_length)
        report.info("BC-PLAN", f"would write {CONFIG_REL} (maxLength "
                    f"{max_length}, {len(templates)} template(s))")
        report.print()
        return ExitCode.DRY_RUN

    save_config(fw_dir, templates=templates, max_length=max_length)
    report.success("BC-SAVE", f"wrote {CONFIG_REL}")
    return report.finish()


def cmd_branch_config_preview(args) -> ExitCode:
    target = resolve_target(args.target)
    report = Report("branch-config preview", str(target))
    fw_dir = _require_fw_dir(target)
    task, _ = load_task(fw_dir, args.key)

    from . import git_ops
    slug = git_ops.slugify(task.get("summary", "") or task["ticket"])
    name, wt, tmpl = resolve_branch_name(
        fw_dir, command=task["command"], ticket_id=task["ticket"],
        short_description=slug, work_type=args.work_type)
    report.info("BC-PREVIEW", f"{task['ticket']} (work type '{wt}', template "
                f"{tmpl!r}) -> {name}")
    return report.finish()
