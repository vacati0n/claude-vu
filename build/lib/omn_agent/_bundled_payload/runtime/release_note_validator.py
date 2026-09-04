#!/usr/bin/env python3
"""Validation Engine: release-note.md conformance.

Mechanically checks a produced `release-note.md` against the contract set that governs it:

  - `.claude/templates/release-note.md`      rendered form, section and field labels
  - `.claude/agents/omn-documentation.md`    behavioural contract: outputs, decision rules,
                                             constraints
  - `.claude/context/release-context.md`     the release facts a note must not contradict

Scope boundary: `R1` to `R5` are the rules in the agent contract that are decidable by
inspecting the artifact. Whether the note describes what actually shipped is not decidable
from the note alone; what is decidable is internal consistency -- a declared contract change
carries a compatibility statement, a rolled-back release carries a recorded issue, and the
version is one fact rather than two.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import artifact_contract as ac  # noqa: E402
from artifact_lib import Check, strip_md  # noqa: E402

TEMPLATE = "templates/release-note.md"
CONTRACT_REF = "agents/omn-documentation.md"

VERDICTS = ("released", "partial", "rolled-back")
ISSUE_TABLE = ("ID", "Issue", "Impact", "Workaround", "Tracking")

CONTRACT = ac.ArtifactContract(
    artifact="release-note.md",
    producers=("omn-documentation",),
    metadata_key="releaseNote",
    metadata_fields=("releaseId", "version", "sourceInputs", "producedBy", "agentVersion",
                     "schemaVersion", "status", "releaseVerdict", "inputDigest",
                     "contextDigest"),
    statuses=ac.STATUSES_COMPLETE,
    template_ref=TEMPLATE,
    contract_refs=(TEMPLATE, CONTRACT_REF),
    id_prefixes={"K": "Known Issues"},
    sections=(
        ac.Section("Metadata", fields=(
            ac.Field("Version"),
            ac.Field("Release date and time"),
            ac.Field("Environment"),
            ac.Field("Release owner"),
        )),
        ac.Section("Highlights", fields=(
            ac.Field("Feature additions"),
            ac.Field("Bug fixes"),
            ac.Field("Improvements"),
        )),
        ac.Section("Technical Changes and Compatibility", fields=(
            ac.Field("API or contract changes"),
            ac.Field("Database or migration impact"),
            ac.Field("Configuration changes"),
            ac.Field("Backward compatibility notes"),
        )),
        ac.Section("Operational Notes", fields=(
            ac.Field("Deployment considerations"),
            ac.Field("Monitoring and alerts"),
            ac.Field("Rollback criteria", min_words=3),
        )),
        ac.Section("Validation Summary", fields=(
            ac.Field("Test status", min_words=3),
            ac.Field("Known risk acceptance"),
            ac.Field("Post-release checks"),
        )),
        ac.Section("Known Issues", table=ac.Table(ISSUE_TABLE, min_rows=1)),
        ac.Section("Communication", fields=(
            ac.Field("Stakeholders notified"),
            ac.Field("Support handoff notes"),
        )),
    ),
    obligations=(
        ("N1", CONTRACT_REF + "#responsibilities",
         "The note describes the behaviour that was actually delivered"),
        ("N2", CONTRACT_REF + "#responsibilities",
         "Stale content from the prior release has been removed rather than carried forward"),
        ("N3", CONTRACT_REF + "#constraints",
         "Every user-visible change is represented, and none is overstated"),
    ),
)


def semantic_checks(rep, contract):
    """The release-specific rules in `agents/omn-documentation.md`."""
    meta = getattr(rep, "meta", {}) or {}
    body_of = getattr(rep, "body_of", {}) or {}

    def add(cid, ref, severity, description, result, detail=""):
        rep.checks.append(Check(cid, ref, severity, description, result, detail))

    verdict = str(meta.get("releaseVerdict") or "").strip().lower()
    add("R1", TEMPLATE, "Blocking",
        f"releaseVerdict is one of {', '.join(VERDICTS)}",
        "pass" if verdict in VERDICTS else "fail", f"releaseVerdict={verdict!r}")

    # R2 -- the version is one fact. A note whose header and provenance disagree cannot be
    # cited by the closure package that consumes it.
    section_version = strip_md(
        ac.parse_field_bullets(body_of.get("Metadata", "")).get("version", ""))
    meta_version = str(meta.get("version") or "").strip()
    add("R2", TEMPLATE, "Blocking",
        "The version in the metadata block and in the Metadata section are the same",
        "pass" if meta_version and meta_version == section_version else "fail",
        f"metadata={meta_version!r} section={section_version!r}")

    tech = ac.parse_field_bullets(body_of.get("Technical Changes and Compatibility", ""))
    api_change = tech.get("api or contract changes", "")
    compat = tech.get("backward compatibility notes", "")
    declares_change = bool(api_change) and not ac.is_none_marker(api_change)
    states_compat = bool(compat) and not ac.is_none_marker(compat)
    add("R3", CONTRACT_REF + "#responsibilities", "Blocking",
        "A declared contract change carries a backward compatibility statement",
        "pass" if not declares_change or states_compat else "fail",
        f"API or contract changes declared as {api_change!r} with compatibility notes "
        f"{compat!r}" if declares_change and not states_compat
        else ("contract change declared and compatibility stated" if declares_change
              else "no contract change declared"))

    # R4 -- a release that did not fully land has something to say about why.
    issues_body = body_of.get("Known Issues", "")
    _h, rows = ac.find_table(issues_body, ISSUE_TABLE)
    has_issue = bool(rows)
    needs_issue = verdict in ("partial", "rolled-back")
    add("R4", CONTRACT_REF + "#responsibilities", "Blocking",
        "A partial or rolled-back release records at least one known issue",
        "pass" if not needs_issue or has_issue else "fail",
        f"releaseVerdict={verdict!r} with an empty Known Issues section" if needs_issue
        and not has_issue else f"releaseVerdict={verdict!r}, {len(rows)} known issue(s)")

    # R5 -- a rollback is an operational event, so the rollback criteria cannot be silent.
    rollback = ac.parse_field_bullets(body_of.get("Operational Notes", "")).get(
        "rollback criteria", "")
    ok = verdict != "rolled-back" or (bool(rollback) and not ac.is_none_marker(rollback))
    add("R5", CONTRACT_REF + "#responsibilities", "Blocking",
        "A rolled-back release states the criteria the rollback was taken under",
        "pass" if ok else "fail",
        f"rollback criteria={rollback!r} for a rolled-back release" if not ok
        else "rollback criteria stated")

    # R6 -- a note is stakeholder communication, so the audience is named.
    comms = ac.parse_field_bullets(body_of.get("Communication", ""))
    notified = comms.get("stakeholders notified", "")
    add("R6", CONTRACT_REF + "#purpose", "Correctable",
        "The note names the stakeholders it was communicated to",
        "pass" if notified and not ac.is_none_marker(notified) else "fail",
        f"stakeholders notified={notified!r}")

    rep.counts["releaseVerdict"] = verdict
    rep.counts["knownIssues"] = len(rows)
    rep.counts["version"] = meta_version or None
    # A version string is provenance, so a note that carries one that is not a version at all
    # is recorded rather than accepted silently.
    if meta_version and not re.match(r"^v?\d+(\.\d+)*([-+][0-9A-Za-z.\-]+)?$", meta_version):
        add("R7", TEMPLATE, "Correctable", "The version is a recognisable version string",
            "fail", f"version={meta_version!r}")
    else:
        add("R7", TEMPLATE, "Correctable", "The version is a recognisable version string",
            "pass", f"version={meta_version!r}")
    return rep


def validate(artifact_path, envelope: dict | None = None):
    rep = ac.run_contract(CONTRACT, Path(artifact_path), envelope)
    return semantic_checks(rep, CONTRACT)


def main():
    return ac.cli(CONTRACT, extra=semantic_checks)


if __name__ == "__main__":
    sys.exit(main())
