"""Regression tests for the release-verdict defect (fix-bug run run-f94564cb61ce).

Before the repair the documentation release-verdict contract knew only deployment
outcomes -- `released`, `partial`, `rolled-back` -- each read off a supplied deployment
status, while four of the five phases that publish `release-note.md` are never supplied one.
Those phases therefore had no verdict that was both truthful and accepted: the faithful
reading (withheld, `blocked`) failed `R1`, and a deployment verdict with no deployment
evidence passed, because `R1` tested vocabulary membership only.

The repair keys the release position on the phase's communication basis:

  release-handoff      -> handed-off            evidence: a verification record
  findings             -> findings-published    evidence: the final technical recommendation
  documentation-delta  -> delta-published       evidence: the pull request's validation record
  post-release         -> released | partial | rolled-back, read off the deployment status

`R8` decides the verdict against the evidence types the note lists in `sourceInputs`; `R9`
decides it against the phase the invocation envelope names. Withheld is never a passing
verdict. The release phase keeps its verdicts, `R4`, and `R5` unchanged.

Every test that witnesses the defect fails against the tree before the repair; the
release-phase regression tests pass on both, which is the point of them.
"""

from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
CLAUDE = REPO / ".claude"
RUNTIME = CLAUDE / "runtime"
sys.path.insert(0, str(RUNTIME))

import release_note_validator as rnv  # noqa: E402
import verify_validators as vv  # noqa: E402

FIXTURE = (RUNTIME / "fixtures" / "release-note.md").read_text(encoding="utf-8")
INPUT_DIGEST = "sha256:fixture-input-not-run-produced"
CONTEXT_DIGEST = "sha256:fixture-context-not-run-produced"

# The five documentation phases and the position each one's basis yields when its
# evidence is present. Stated here independently of the validator so the tests check it.
PHASES = {
    "documentation-and-release-handoff": ("handed-off", ["verification-report"]),
    "publication": ("findings-published", ["technical-recommendation"]),
    "findings-publication": ("findings-published", ["technical-recommendation"]),
    "documentation-impact": ("delta-published", ["verification-report"]),
    "communication-and-post-release": ("released", ["deployment-status"]),
}
NEW_POSITIONS = ("handed-off", "findings-published", "delta-published")
DEPLOYMENT_VERDICTS = ("released", "partial", "rolled-back")

NO_ISSUES = ("| `K-001` | a scheduled retry only becomes dispatchable when a runtime command is "
             "next invoked | an unattended run does not advance on its own | invoke `next` on "
             "the run | recorded in `runtime/README.md` known gaps |\n")


def note_text(verdict: str, types: list, *, status: str = "complete",
              known_issues: bool = True, rollback: str | None = None) -> str:
    """The fixture note, with its verdict, its source input types, and its status replaced."""
    text = FIXTURE
    block = "".join(f"    - type: {t}\n      reference: inline\n" for t in types)
    text = re.sub(r"  sourceInputs:\n(?:    - type: .*\n      reference: .*\n)+",
                  lambda _m: "  sourceInputs:\n" + block, text, count=1)
    text = text.replace("  releaseVerdict: released", f"  releaseVerdict: {verdict}", 1)
    text = text.replace("  status: complete", f"  status: {status}", 1)
    if not known_issues:
        text = text.replace(NO_ISSUES, "", 1).replace(
            "| ID | Issue | Impact | Workaround | Tracking |\n|---|---|---|---|---|\n",
            "None identified.\n", 1)
    if rollback is not None:
        text = re.sub(r"- Rollback criteria: .*", f"- Rollback criteria: {rollback}", text,
                      count=1)
    return text


def envelope(state_id) -> dict:
    env = {"context_slice": {"input_digest": INPUT_DIGEST, "context_digest": CONTEXT_DIGEST}}
    if state_id is not None:
        env["state_id"] = state_id
    return env


class _Notes(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.work = Path(self._tmp.name)
        self._n = 0

    def tearDown(self):
        self._tmp.cleanup()

    def validate(self, text: str, env=None, validator=rnv):
        self._n += 1
        path = self.work / f"note-{self._n}" / "release-note.md"
        path.parent.mkdir()
        path.write_text(text, encoding="utf-8")
        return validator.validate(path, env)

    @staticmethod
    def result(rep, cid: str):
        found = [c for c in rep.checks if c.id == cid]
        return (found[0].result, found[0].severity) if found else (None, None)

    @staticmethod
    def failed(rep) -> list:
        return [c.id for c in rep.checks if c.result == "fail"]


class WithheldNeverPasses(_Notes):
    def test_withheld_fails_in_every_phase_and_without_an_envelope(self):
        for phase in list(PHASES) + [None]:
            with self.subTest(phase=phase):
                _verdict, types = PHASES.get(phase, ("", ["verification-report"]))
                rep = self.validate(note_text("withheld", types, status="blocked"),
                                    envelope(phase) if phase else None)
                self.assertFalse(rep.passed)
                self.assertIn("R1", self.failed(rep))


class NonDeployingPhasesHaveATruthfulPosition(_Notes):
    """The defect's core: each non-deploying phase can now publish a passing note."""

    def test_each_phase_passes_with_its_basis_position_and_evidence(self):
        for phase, (verdict, types) in PHASES.items():
            with self.subTest(phase=phase):
                rep = self.validate(note_text(verdict, types + ["final-change-summary"]),
                                    envelope(phase))
                self.assertTrue(rep.passed, self.failed(rep))
                self.assertEqual(self.result(rep, "R8")[0], "pass")
                self.assertEqual(self.result(rep, "R9"), ("pass", "Blocking"))

    def test_without_an_envelope_the_phase_rule_is_declared_not_decided(self):
        for phase, (verdict, types) in PHASES.items():
            with self.subTest(phase=phase):
                rep = self.validate(note_text(verdict, types))
                self.assertTrue(rep.passed, self.failed(rep))
                self.assertEqual(self.result(rep, "R9"), ("not-machine-checkable", "Advisory"))

    def test_the_new_positions_need_no_known_issue(self):
        for phase, (verdict, types) in PHASES.items():
            with self.subTest(phase=phase):
                rep = self.validate(note_text(verdict, types, known_issues=False),
                                    envelope(phase))
                self.assertTrue(rep.passed, self.failed(rep))

    def test_the_held_run_preconditions_pass_with_handed_off(self):
        # run-c9fb8d5bbb32's inputs: a verification record and a change summary, no deployment.
        rep = self.validate(note_text("handed-off", ["architecture-context",
                                                     "verification-report",
                                                     "final-change-summary"]),
                            envelope("documentation-and-release-handoff"))
        self.assertTrue(rep.passed, self.failed(rep))


class DeploymentVerdictsNeedDeploymentEvidence(_Notes):
    """The accepted path of the defect: a deployment claim with no deployment evidence."""

    def test_a_deployment_verdict_without_deployment_status_fails(self):
        for verdict in DEPLOYMENT_VERDICTS:
            for env in (None, envelope("communication-and-post-release")):
                with self.subTest(verdict=verdict, envelope=bool(env)):
                    rep = self.validate(note_text(verdict, ["verification-report",
                                                            "final-change-summary"]), env)
                    self.assertIn("R8", self.failed(rep))

    def test_released_on_a_handoff_fails_even_with_deployment_status(self):
        rep = self.validate(note_text("released", ["deployment-status", "verification-report"]),
                            envelope("documentation-and-release-handoff"))
        self.assertIn("R9", self.failed(rep))
        self.assertEqual(self.result(rep, "R8")[0], "pass")

    def test_the_released_precedent_shape_now_fails_on_both_rules(self):
        # run-efe092286625's shape: released, a verification record, no deployment status.
        rep = self.validate(note_text("released", ["verification-report",
                                                   "final-change-summary",
                                                   "stakeholder-list"]),
                            envelope("documentation-and-release-handoff"))
        self.assertGreaterEqual(set(self.failed(rep)), {"R8", "R9"})


class EvidenceTypeSets(_Notes):
    def test_validation_report_is_accepted_beside_verification_report(self):
        for phase, verdict in (("documentation-and-release-handoff", "handed-off"),
                               ("documentation-impact", "delta-published")):
            for evidence in ("verification-report", "validation-report"):
                with self.subTest(verdict=verdict, evidence=evidence):
                    rep = self.validate(note_text(verdict, [evidence]), envelope(phase))
                    self.assertTrue(rep.passed, self.failed(rep))

    def test_each_new_position_fails_without_its_evidence(self):
        cases = (("handed-off", "documentation-and-release-handoff"),
                 ("findings-published", "publication"),
                 ("delta-published", "documentation-impact"))
        for verdict, phase in cases:
            with self.subTest(verdict=verdict):
                rep = self.validate(note_text(verdict, ["final-change-summary"]),
                                    envelope(phase))
                self.assertIn("R8", self.failed(rep))

    def test_findings_need_the_recommendation_not_a_change_summary(self):
        # run-437e2f765e4b recorded its recommendation as final-change-summary.
        rep = self.validate(note_text("findings-published", ["final-change-summary",
                                                             "final-change-summary"]),
                            envelope("publication"))
        self.assertIn("R8", self.failed(rep))

    def test_a_malformed_source_input_list_fails(self):
        text = note_text("handed-off", ["verification-report"]).replace(
            "    - type: verification-report\n      reference: inline\n",
            "    - verification-report\n", 1)
        rep = self.validate(text, envelope("documentation-and-release-handoff"))
        self.assertIn("R8", self.failed(rep))


class PhaseRule(_Notes):
    def test_a_new_position_on_the_release_phase_fails(self):
        for verdict in NEW_POSITIONS:
            with self.subTest(verdict=verdict):
                rep = self.validate(note_text(verdict, ["verification-report",
                                                        "technical-recommendation"]),
                                    envelope("communication-and-post-release"))
                self.assertIn("R9", self.failed(rep))

    def test_a_position_for_another_basis_fails(self):
        rep = self.validate(note_text("findings-published", ["technical-recommendation"]),
                            envelope("documentation-and-release-handoff"))
        self.assertIn("R9", self.failed(rep))

    def test_an_envelope_without_a_known_phase_is_blocking(self):
        for state_id in (None, "fix-implementation"):
            with self.subTest(state_id=state_id):
                rep = self.validate(note_text("handed-off", ["verification-report"]),
                                    envelope(state_id))
                self.assertEqual(self.result(rep, "R9"), ("fail", "Blocking"))

    def test_the_command_line_envelope_reaches_the_phase_rule(self):
        note = self.work / "cli" / "release-note.md"
        note.parent.mkdir()
        note.write_text(note_text("handed-off", ["verification-report"]), encoding="utf-8")
        outcomes = {}
        for phase in ("documentation-and-release-handoff", "communication-and-post-release"):
            env_path = self.work / "cli" / f"{phase}.json"
            env_path.write_text(json.dumps(envelope(phase)), encoding="utf-8")
            out = self.work / "cli" / f"{phase}.out.json"
            proc = subprocess.run(
                [sys.executable, str(RUNTIME / "release_note_validator.py"), str(note),
                 "--envelope", str(env_path), "--json-out", str(out)],
                capture_output=True, text=True, cwd=str(REPO))
            checks = {c["id"]: c for c in json.loads(out.read_text(encoding="utf-8"))["checks"]}
            outcomes[phase] = (proc.returncode, checks.get("R9", {}).get("result"))
        self.assertEqual(outcomes["documentation-and-release-handoff"], (0, "pass"))
        self.assertEqual(outcomes["communication-and-post-release"], (1, "fail"))


class ReleasePhaseUnchanged(_Notes):
    """Regression protection: the release phase decides exactly as it did before."""

    RELEASE = "communication-and-post-release"

    def test_the_fixture_passes_with_and_without_the_release_envelope(self):
        for env in (None, envelope(self.RELEASE)):
            with self.subTest(envelope=bool(env)):
                rep = self.validate(FIXTURE, env)
                self.assertTrue(rep.passed, self.failed(rep))

    def test_partial_and_rolled_back_still_require_a_known_issue(self):
        for verdict in ("partial", "rolled-back"):
            with self.subTest(verdict=verdict):
                bare = self.validate(note_text(verdict, ["deployment-status"],
                                               known_issues=False), envelope(self.RELEASE))
                self.assertIn("R4", self.failed(bare))
                full = self.validate(note_text(verdict, ["deployment-status"]),
                                     envelope(self.RELEASE))
                self.assertTrue(full.passed, self.failed(full))

    def test_rolled_back_still_requires_rollback_criteria(self):
        rep = self.validate(note_text("rolled-back", ["deployment-status"],
                                      rollback="None identified."), envelope(self.RELEASE))
        self.assertIn("R5", self.failed(rep))

    def test_released_still_permits_no_known_issue(self):
        rep = self.validate(note_text("released", ["deployment-status"], known_issues=False),
                            envelope(self.RELEASE))
        self.assertTrue(rep.passed, self.failed(rep))


# ------------------------------------------------------------------ contract agreement
def read(rel: str, root: Path = CLAUDE) -> str:
    return (root / rel).read_text(encoding="utf-8")


def deliverable_rows() -> dict:
    """output.md's Deliverable table: phase -> (basis, positions)."""
    rows = {}
    for line in read("agents/documentation/output.md").splitlines():
        cells = re.findall(r"`([^`]+)`", line)
        if line.startswith("| `") and len(cells) >= 4 and cells[2] in rnv.VERDICT_OF_BASIS:
            rows[cells[1]] = (cells[2], tuple(cells[3:]))
    return rows


class ContractAgreement(unittest.TestCase):
    def test_phase_table_agrees_with_the_output_and_agent_contracts(self):
        rows = deliverable_rows()
        self.assertEqual({p: b for p, (b, _v) in rows.items()}, rnv.PHASE_BASIS)
        for phase, (basis, positions) in rows.items():
            with self.subTest(phase=phase):
                self.assertEqual(positions, rnv.VERDICT_OF_BASIS[basis])
        identity = read("agents/documentation/identity.md")
        for phase, basis in rnv.PHASE_BASIS.items():
            with self.subTest(identity=phase):
                self.assertRegex(identity, rf"\| `{phase}` \| primary \| `{basis}` \|")

    def test_the_vocabulary_is_one_list_everywhere(self):
        expected = set(rnv.VERDICTS)
        self.assertEqual(expected, set(DEPLOYMENT_VERDICTS) | set(NEW_POSITIONS))
        output = read("agents/documentation/output.md")
        row = re.search(r"^\| `releaseVerdict` \|(.*)\|$", output, re.M).group(1)
        self.assertEqual(set(re.findall(r"`([^`]+)`", row)), expected)
        template = read("templates/release-note.md")
        comment = re.search(r"releaseVerdict:\s*#([^\n]*)", template).group(1)
        self.assertEqual({t.strip() for t in comment.split("|")}, expected)
        quality = read("agents/documentation/quality.md")
        r1 = re.search(r"^\| `R1` \|(.*)$", quality, re.M).group(1)
        self.assertEqual(set(re.findall(r"`([^`]+)`", r1)) - {"releaseVerdict"}, expected)
        self.assertRegex(quality, r"(?m)^\| `R8` \|", "quality.md declares no R8")
        self.assertRegex(quality, r"(?m)^\| `R9` \|", "quality.md declares no R9")

    def test_stage_8_yields_a_position_for_every_basis(self):
        reasoning = read("agents/documentation/reasoning.md")
        stage = reasoning.split("## Stage 8", 1)[1].split("## Stage 9", 1)[0]
        rows = []
        for ln in stage.splitlines():
            if ln.startswith("| `"):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                rows.append((set(re.findall(r"`([^`]+)`", cells[0])), cells[2].strip("`"),
                             cells[3].strip("`")))
        for basis, positions in rnv.VERDICT_OF_BASIS.items():
            with self.subTest(basis=basis):
                yielded = {v for b, v, st in rows if basis in b and st == "complete"}
                self.assertEqual(yielded, set(positions))
                self.assertIn((basis, "withheld", "blocked"),
                              {(x, v, st) for b, v, st in rows for x in b},
                              f"no withheld row for {basis}")

    def test_the_charter_and_the_runtime_readme_state_the_basis_rule(self):
        charter = read("agents/documentation/system.md")
        self.assertRegex(charter, r"(?m)^\| Record a handoff, findings, or documentation-delta "
                                  r"publication as released \| Refuse;")
        readme = read("runtime/README.md")
        row = re.search(r"(?m)^\| `release-note.md` \| `release_note_validator.py` \|(.*)$",
                        readme).group(1)
        for phase in rnv.PHASE_BASIS:
            with self.subTest(phase=phase):
                self.assertIn(f"/{phase}`", row)
        for rule in ("`R8`", "`R9`", "`SUPERSEDED_CONTRACTS`"):
            self.assertIn(rule, readme)
        identity = read("agents/documentation/identity.md")
        evidence = identity.split("### Required Evidence Level", 1)[1].split("## ", 1)[0]
        for position in NEW_POSITIONS:
            with self.subTest(required_evidence=position):
                self.assertIn(f"(`{position}`)", evidence)

    def test_versions_agree(self):
        manifest = read("agents/documentation/manifest.yaml")
        self.assertRegex(manifest, r"\n  version: 1\.2\.0\n")
        host = read("agents/documentation.agent.md")
        self.assertIn("| version | `1.2.0` |", host)
        self.assertIn("`metadata.version` is `1.2.0`", host)
        agents = read("registry/agents.yaml")
        rec = agents.split("identifier: documentation\n", 1)[1]
        self.assertRegex(rec, r"^(?:.*\n){0,12}?    version: 1\.2\.0\n")
        templates = read("registry/templates.yaml")
        rec = templates.split("identifier: release-note\n", 1)[1]
        self.assertRegex(rec, r"^(?:.*\n){0,8}?    version: 1\.2\.0\n")
        self.assertIn("Template version 1.2.0.", read("templates/release-note.md"))
        self.assertEqual(rnv.CURRENT_CONTRACT_VERSION, (1, 2, 0))




# ------------------------------------------------------------------ coverage verification
class SupersededContractCandidates(_Notes):
    """verify_validators no longer validates a note produced under the superseded contract."""

    def committed(self, version: str, text: str) -> Path:
        self._n += 1
        state = self.work / f"run-{self._n}" / "states" / "documentation-and-release-handoff"
        (state / "artifacts").mkdir(parents=True)
        note = state / "artifacts" / "release-note.md"
        note.write_text(text, encoding="utf-8")
        env = dict(envelope("documentation-and-release-handoff"),
                   agent_id="documentation", agent_version=version)
        (state / "invocation-envelope.json").write_text(json.dumps(env), encoding="utf-8")
        return note

    def test_a_note_below_the_current_contract_is_superseded(self):
        old = self.committed("1.1.0", note_text("released", ["verification-report"]))
        new = self.committed("1.2.0", note_text("handed-off", ["verification-report"]))
        env_of = lambda p: p.parent.parent / "invocation-envelope.json"  # noqa: E731
        self.assertTrue(vv.superseded_reason("release-note.md", env_of(old)))
        self.assertIsNone(vv.superseded_reason("release-note.md", env_of(new)))
        self.assertIsNone(vv.superseded_reason("release-note.md", None))
        self.assertIsNone(vv.superseded_reason("bug-analysis.md", env_of(old)))
        # A malformed envelope is validated like any candidate, never a crash (review CR-002).
        for broken in ("{not json", "[1, 2]", "\udcff"):
            env_of(old).write_text(broken, encoding="utf-8", errors="surrogateescape")
            self.assertIsNone(vv.superseded_reason("release-note.md", env_of(old)))
        env_of(old).write_text(json.dumps(dict(envelope("documentation-and-release-handoff"),
                                               agent_id="documentation",
                                               agent_version="1.1.0")), encoding="utf-8")
        with mock.patch.object(vv, "committed_instances", return_value=[old, new]):
            listed = [p for p, _s, _e in vv.candidate_instances("release-note.md")]
            superseded = vv.superseded_candidates("release-note.md")
            selected = vv.conforming_instance("release-note.md")[0]
        self.assertNotIn(old, listed)
        self.assertIn(new, listed)
        self.assertEqual([s["instance"] for s in superseded], [vv.instance_label(old)])
        self.assertEqual(selected, new)

    def run_main(self, committed: list) -> dict:
        real = vv.committed_instances
        out = self.work / "vv.json"

        def fake(artifact):
            return committed if artifact == "release-note.md" else real(artifact)

        with mock.patch.object(vv, "committed_instances", side_effect=fake), \
                mock.patch.object(sys, "argv", ["verify_validators.py", "--json-out", str(out)]), \
                mock.patch("sys.stdout"):
            vv.main()
        data = json.loads(out.read_text(encoding="utf-8"))
        return {c["id"]: c for c in data["checks"]}, data

    def test_superseded_notes_are_reported_and_not_validated(self):
        old = self.committed("1.0.0", note_text("released", ["verification-report"]))
        checks, data = self.run_main([old])
        self.assertNotIn("release-note.md: conforming instance rejected", checks["V3"]["detail"])
        self.assertNotIn("release-note.md: skipped candidate", checks["V3"]["detail"])
        summary = next(s for s in data["summaries"] if s["artifact"] == "release-note.md")
        self.assertEqual(summary["instance_source"], "fixture")
        self.assertEqual([s["instance"] for s in summary["superseded_candidates"]],
                         [vv.instance_label(old)])
        self.assertIn("1 release-note.md candidate(s) produced under a superseded contract",
                      checks["V3"]["detail"])

    def test_a_rejected_note_at_the_current_contract_still_fails_v3(self):
        bad = self.committed("1.2.0", note_text("released", ["verification-report"]))
        checks, _data = self.run_main([bad])
        self.assertEqual(checks["V3"]["result"], "fail")
        self.assertIn("release-note.md: conforming instance rejected", checks["V3"]["detail"])


if __name__ == "__main__":
    unittest.main()
