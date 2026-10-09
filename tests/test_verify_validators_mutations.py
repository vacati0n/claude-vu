"""Tests for the declared mutations of the validator coverage verifier.

`V4` of `runtime/verify_validators.py` proves each registered validator decides by mutating a
conforming instance and requiring the named check to reject it. Which instance it mutates
depends on run history: `conforming_instance` tries committed run artifacts last to first in
lexical run-identifier order, then governance records, then the fixture, and takes the first on
which the mutation resolves. A mutation row whose anchor or substitute is copied from one
instance therefore breaks as soon as a run commits a conforming artifact that spells the free
value differently, which is how the investigation-report row stopped `V4` once a real report
recommended `O-003`, and how the orchestration row stopped it once a closure record rendered
its phase identifiers without backticks.

These tests drive the rows over instances that vary their free values, and drive the selector
over candidate lists that vary which candidates can carry the mutation. Every instance is built
from `runtime/fixtures/` in a temporary directory; nothing here writes into the repository.
"""

from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME_DIR = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import framework_runtime as fr  # noqa: E402
import investigation_report_validator as irv  # noqa: E402
import orchestration_result_validator as orv  # noqa: E402
import verify_validators as vv  # noqa: E402

ARTIFACT = "investigation-report.md"
FIXTURE_TEXT = (vv.FIXTURES / ARTIFACT).read_text(encoding="utf-8")
FIXTURE_RECOMMENDATION = "- Recommended option: `O-002`"
OPTION_ROW_O003 = next(ln for ln in FIXTURE_TEXT.splitlines() if ln.startswith("| `O-003` |"))


def apply_row(artifact: str, text: str):
    """Apply the `MUTATIONS` row for this type by the table's own rule, or None if it cannot.

    The row's first element is a literal to find or a callable deriving the (old, new) pair from
    the instance; this reads the row exactly as the table declares it, so a row pinned to one
    instance's values fails here on any instance that spells them differently.
    """
    old, new, _expect, _what = vv.MUTATIONS[artifact]
    if callable(old):
        pair = old(text)
        if not pair:
            return None
        old, new = pair
    if old not in text:
        return None
    return text.replace(old, new, 1)


def recommending(option: str, text: str = FIXTURE_TEXT) -> str:
    assert FIXTURE_RECOMMENDATION in text
    return text.replace(FIXTURE_RECOMMENDATION, f"- Recommended option: `{option}`", 1)


def with_options(count: int) -> str:
    """The fixture widened to `count` evaluated options, each evidence-backed."""
    extra = [f"| `O-{n:03d}` | variant {n} of the sweep | bounded stalls | more moving parts "
             f"| small | `E-001`, `E-002` |" for n in range(4, count + 1)]
    return FIXTURE_TEXT.replace(OPTION_ROW_O003, "\n".join([OPTION_ROW_O003, *extra]), 1)


def only_option(option: str) -> str:
    """A single-option copy: the options table keeps one row, renumbered to `option`."""
    rows = [ln for ln in FIXTURE_TEXT.splitlines() if re.match(r"^\| `O-00[23]` \|", ln)]
    text = FIXTURE_TEXT
    for row in rows:
        text = text.replace(row + "\n", "", 1)
    return recommending(option, text.replace("| `O-001` |", f"| `{option}` |", 1))


class _Workdir(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="vv-mutations-")
        self.work = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def validate(self, text: str, name: str = ARTIFACT):
        path = self.work / name
        path.write_text(text, encoding="utf-8")
        rep = irv.validate(path, None)
        return rep.passed, [c["id"] for c in rep.to_dict()["checks"] if c["result"] == "fail"]


class InvestigationRowOverVariedInstances(_Workdir):
    """The bug's witnesses: these fail on the literal row and pass on the derived one."""

    def test_report_recommending_o003_is_mutated_and_rejected_by_i1(self):
        instance = recommending("O-003")
        self.assertEqual(self.validate(instance), (True, []),
                         "the varied instance must itself conform")
        mutated = apply_row(ARTIFACT, instance)
        self.assertIsNotNone(mutated, "no mutation anchor in a report recommending O-003")
        passed, failed = self.validate(mutated)
        self.assertFalse(passed)
        self.assertIn("I1", failed)

    def test_nine_option_report_recommending_o002_is_rejected_by_i1(self):
        instance = with_options(9)
        self.assertEqual(self.validate(instance), (True, []),
                         "the nine-option instance must itself conform")
        mutated = apply_row(ARTIFACT, instance)
        self.assertIsNotNone(mutated)
        passed, failed = self.validate(mutated)
        self.assertFalse(passed, "the substitute named an option the report evaluated")
        self.assertIn("I1", failed)


class RecommendAnUnevaluatedOption(_Workdir):
    def substitute(self, text: str) -> str:
        pair = vv.recommend_an_unevaluated_option(text)
        self.assertIsNotNone(pair)
        old, new = pair
        self.assertIn(old, text)
        ids = re.findall(r"\bO-\d{3}\b", new)
        self.assertEqual(len(ids), 1)
        return ids[0]

    def test_substitute_is_the_lowest_id_absent_from_the_text(self):
        self.assertEqual(self.substitute(FIXTURE_TEXT), "O-004")
        self.assertEqual(self.substitute(recommending("O-003")), "O-004")
        self.assertEqual(self.substitute(with_options(5)), "O-006")
        self.assertEqual(self.substitute(with_options(9)), "O-010")

    def test_two_named_options_replace_only_the_first(self):
        text = with_options(4).replace(FIXTURE_RECOMMENDATION,
                                       "- Recommended option: `O-003` and `O-004`", 1)
        old, new = vv.recommend_an_unevaluated_option(text)
        self.assertEqual(new.lstrip("\n"), "- Recommended option: `O-005` and `O-004`")
        passed, failed = self.validate(text.replace(old, new, 1))
        self.assertFalse(passed)
        self.assertIn("I1", failed)

    def test_single_option_copy_gets_an_id_absent_from_its_text(self):
        for option in ("O-001", "O-003"):
            with self.subTest(option=option):
                text = only_option(option)
                free = self.substitute(text)
                self.assertNotIn(free, text)
                old, new = vv.recommend_an_unevaluated_option(text)
                _passed, failed = self.validate(text.replace(old, new, 1))
                self.assertIn("I1", failed)

    def test_missing_field_yields_none(self):
        text = FIXTURE_TEXT.replace(FIXTURE_RECOMMENDATION + "\n", "", 1)
        self.assertNotIn("Recommended option", text)
        self.assertIsNone(vv.recommend_an_unevaluated_option(text))
        self.assertEqual(vv.resolve_mutation(ARTIFACT, text)[:2], (None, None))

    def test_field_without_an_option_id_yields_none(self):
        text = FIXTURE_TEXT.replace(FIXTURE_RECOMMENDATION, "- Recommended option: none yet", 1)
        self.assertIsNone(vv.recommend_an_unevaluated_option(text))

    def test_no_free_id_yields_none(self):
        every = " ".join(f"O-{n:03d}" for n in range(1, 1000))
        text = FIXTURE_TEXT + "\n" + every + "\n"
        self.assertIsNone(vv.recommend_an_unevaluated_option(text))


class _StubReport:
    def __init__(self, failed: list):
        self.passed = not failed
        self._failed = failed

    def to_dict(self):
        return {"checks": [{"id": cid, "result": "fail"} for cid in self._failed]}


def stub_validator(failed: list):
    return SimpleNamespace(validate=lambda path, envelope: _StubReport(failed))


class MutationVerdict(_Workdir):
    """The `V4` verdict, extracted from `main()`, still fails for every way of being wrong."""

    def test_real_validator_rejecting_by_the_named_check_passes(self):
        finding, failed = vv.mutation_verdict(ARTIFACT, irv, recommending("O-003"), None,
                                              self.work)
        self.assertIsNone(finding)
        self.assertIn("I1", failed)

    def test_validator_accepting_the_mutation_fails(self):
        finding, failed = vv.mutation_verdict(ARTIFACT, stub_validator([]), FIXTURE_TEXT,
                                              None, self.work)
        self.assertEqual(finding, f"{ARTIFACT}: mutation accepted "
                                  f"(recommending an option the report never evaluated)")
        self.assertEqual(failed, [])

    def test_validator_rejecting_by_another_check_fails(self):
        finding, failed = vv.mutation_verdict(ARTIFACT, stub_validator(["C6.2"]), FIXTURE_TEXT,
                                              None, self.work)
        self.assertEqual(finding, f"{ARTIFACT}: rejected, but not by I1 (by ['C6.2'])")
        self.assertEqual(failed, ["C6.2"])

    def test_mutation_lands_on_the_field_not_an_earlier_indented_duplicate(self):
        decoy = "  " + FIXTURE_RECOMMENDATION + " was the draft choice"
        anchor = "- Constraints and assumptions:"
        line = next(ln for ln in FIXTURE_TEXT.splitlines() if ln.startswith(anchor))
        text = FIXTURE_TEXT.replace(line, line + "\n" + decoy, 1)
        self.assertLess(text.index(decoy), text.index("\n" + FIXTURE_RECOMMENDATION))
        written = {}

        def capture(path, envelope):
            written["text"] = Path(path).read_text(encoding="utf-8")
            return _StubReport(["I1"])

        finding, _failed = vv.mutation_verdict(ARTIFACT, SimpleNamespace(validate=capture),
                                               text, None, self.work)
        self.assertIsNone(finding)
        mutated = written["text"]
        self.assertIn("\n" + decoy + "\n", mutated, "the earlier indented line was edited")
        self.assertNotIn("\n" + FIXTURE_RECOMMENDATION + "\n", mutated,
                         "the Recommended option field was left unmutated")
        self.assertIn("\n- Recommended option: `O-004`\n", mutated)

    def test_missing_anchor_fails_without_running_the_validator(self):
        def boom(path, envelope):
            raise AssertionError("the validator must not run without an anchor")

        text = FIXTURE_TEXT.replace(FIXTURE_RECOMMENDATION + "\n", "", 1)
        finding, failed = vv.mutation_verdict(ARTIFACT, SimpleNamespace(validate=boom), text,
                                              None, self.work)
        self.assertEqual(finding, f"{ARTIFACT}: no mutation anchor for "
                                  f"'recommending an option the report never evaluated' "
                                  f"in this instance")
        self.assertIsNone(failed)


class EveryMutationRow(_Workdir):
    def test_every_registered_validator_has_a_mutation_row(self):
        self.assertEqual(set(vv.MUTATIONS), set(fr.VALIDATORS))

    def test_every_row_resolves_and_is_caught_on_its_fixture(self):
        # A type with a fixture is always checkable, so it is required. A type without one is
        # checked on whatever instance the verifier's own selector returns; when there is none,
        # only that type goes unchecked, and the test still fails if nothing could be checked.
        checked, unavailable = [], []
        for artifact, module in sorted(fr.VALIDATORS.items()):
            with self.subTest(artifact=artifact):
                fixture = vv.FIXTURES / artifact
                if fixture.exists():
                    instance, envelope = fixture, None
                else:
                    instance, _source, envelope_path, _skipped = vv.conforming_instance(artifact)
                    if instance is None:
                        unavailable.append(artifact)
                        continue
                    envelope = (json.loads(envelope_path.read_text(encoding="utf-8"))
                                if envelope_path else None)
                checked.append(artifact)
                text = instance.read_text(encoding="utf-8")
                old, new, expect_id, _what = vv.resolve_mutation(artifact, text)
                self.assertIsNotNone(old, f"no mutation anchor in {instance}")
                finding, failed = vv.mutation_verdict(artifact, __import__(module), text,
                                                      envelope, self.work)
                self.assertIsNone(finding, finding)
                self.assertIn(expect_id, failed)
        required = {a for a in fr.VALIDATORS if (vv.FIXTURES / a).exists()}
        self.assertTrue(checked, "no MUTATIONS row could be checked on any instance")
        self.assertFalse(required & set(unavailable),
                         f"fixture-backed types left unchecked: {sorted(required & set(unavailable))}")


# ------------------------------------------------------------------ orchestration-result.md
ORCH = "orchestration-result.md"
ORCH_FIXTURE_TEXT = (vv.FIXTURES / ORCH).read_text(encoding="utf-8")
ORCH_WHAT = vv.MUTATIONS[ORCH][3]
PH_ROW = re.compile(r"^\| `PH-\d{3}` \|")
# The one row the mutation can land on in the fixture: owned by the orchestrator, at a real gate.
ORCH_GATED_ROW = next(ln for ln in ORCH_FIXTURE_TEXT.splitlines()
                      if PH_ROW.match(ln) and "| `omn-orchestrator` |" in ln)


def plain_rendered(text: str = ORCH_FIXTURE_TEXT) -> str:
    """The fixture with every Phase Progression row's backticks removed, as run-d8937789961e wrote."""
    return "\n".join(ln.replace("`", "") if PH_ROW.match(ln) else ln
                     for ln in text.split("\n"))


def without_gated_orchestrator_row(text: str = ORCH_FIXTURE_TEXT) -> str:
    """A record whose orchestrator row declares no gate, so no rendering can carry the mutation."""
    cells = ORCH_GATED_ROW.strip().strip("|").split("|")
    cells[4], cells[5], cells[6] = " none ", " not-applicable ", " not-applicable "
    assert ORCH_GATED_ROW in text
    return text.replace(ORCH_GATED_ROW, "|" + "|".join(cells) + "|", 1)


def non_conforming(text: str = ORCH_FIXTURE_TEXT) -> str:
    """A record that still carries the anchored row but drops a mandatory section heading."""
    assert "\n## Open Questions\n" in text
    return text.replace("\n## Open Questions\n", "\n## Unresolved Matters\n", 1)


class _Candidates(_Workdir):
    """Drive the selector over a synthetic candidate list instead of the repository's runs."""

    def write(self, name: str, text: str) -> Path:
        path = self.work / name / ORCH
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def select(self, committed: list, fixture_text: str | None):
        fixtures = self.work / "fixtures"
        fixtures.mkdir(exist_ok=True)
        if fixture_text is not None:
            (fixtures / ORCH).write_text(fixture_text, encoding="utf-8")
        with mock.patch.object(vv, "committed_instances", lambda artifact: list(committed)), \
                mock.patch.object(vv, "FIXTURES", fixtures):
            return vv.conforming_instance(ORCH)


class PlainRenderedOrchestrationRows(_Workdir):
    """The locator cause: a conforming record rendering its identifiers plain has an anchor."""

    def test_plain_rendered_record_conforms_and_is_caught_by_o4(self):
        text = plain_rendered()
        self.assertNotIn("`PH-", text)
        path = self.work / ORCH
        path.write_text(text, encoding="utf-8")
        self.assertTrue(orv.validate(path, None).passed, "the plain record must itself conform")
        self.assertIsNotNone(vv.award_itself_its_own_gate(text),
                             "no anchor in a record that renders its identifiers plain")
        finding, failed = vv.mutation_verdict(ORCH, orv, text, None, self.work)
        self.assertIsNone(finding, finding)
        self.assertEqual(failed, ["O4"])

    def test_locator_keys_on_the_identifier_cell_not_a_mention_elsewhere(self):
        text = without_gated_orchestrator_row()
        self.assertIsNone(vv.award_itself_its_own_gate(text))
        self.assertIsNone(vv.award_itself_its_own_gate(plain_rendered(text)))


class InstanceSelection(_Candidates):
    """The selection cause: the selector tries candidates in order and reports every skip."""

    def test_unanchored_last_candidate_is_skipped_for_an_older_anchored_one(self):
        older = self.write("run-a", ORCH_FIXTURE_TEXT)
        last = self.write("run-b", without_gated_orchestrator_row())
        result = self.select([older, last], None)
        self.assertEqual(result[0], older, "the unanchored last candidate was selected")
        self.assertEqual(result[1], "committed run artifact")
        self.assertEqual(result[3], [{"instance": str(last), "source": "committed run artifact",
                                      "reason": f"no mutation anchor for {ORCH_WHAT!r}"}])

    def test_no_applicable_candidate_returns_none_naming_every_candidate(self):
        first = self.write("run-a", without_gated_orchestrator_row())
        second = self.write("run-b", plain_rendered(without_gated_orchestrator_row()))
        instance, source, envelope, skipped = self.select(
            [first, second], without_gated_orchestrator_row())
        self.assertIsNone(instance)
        self.assertIsNone(envelope)
        self.assertEqual(source, "no applicable candidate")
        self.assertEqual([(s["instance"], s["source"]) for s in skipped], [
            (str(second), "committed run artifact"),
            (str(first), "committed run artifact"),
            (str(self.work / "fixtures" / ORCH), "fixture"),
        ])

    def test_falls_back_to_the_fixture_and_reports_the_skip(self):
        only = self.write("run-a", without_gated_orchestrator_row())
        instance, source, _envelope, skipped = self.select([only], ORCH_FIXTURE_TEXT)
        self.assertEqual((instance, source), (self.work / "fixtures" / ORCH, "fixture"))
        self.assertEqual([s["instance"] for s in skipped], [str(only)])

    def test_non_conforming_applicable_candidate_is_selected_not_skipped(self):
        older = self.write("run-a", ORCH_FIXTURE_TEXT)
        last = self.write("run-b", non_conforming())
        result = self.select([older, last], None)
        self.assertEqual(result[0], last,
                         "selection filtered on validator acceptance, which hides a V3 failure")
        self.assertEqual(result[3], [])
        self.assertFalse(orv.validate(last, None).passed, "V3 must still see this rejection")

    def test_accept_all_validator_still_fails_v4_after_selection(self):
        older = self.write("run-a", ORCH_FIXTURE_TEXT)
        last = self.write("run-b", without_gated_orchestrator_row())
        instance = self.select([older, last], None)[0]
        self.assertEqual(instance, older)
        finding, failed = vv.mutation_verdict(ORCH, stub_validator([]),
                                              instance.read_text(encoding="utf-8"), None,
                                              self.work)
        self.assertEqual(finding, f"{ORCH}: mutation accepted ({ORCH_WHAT})")
        self.assertEqual(failed, [])


def v3_block(text: str) -> str:
    """The V3 line and its detail line from the verifier's console output."""
    return re.search(r"^\[(?:PASS|FAIL)\] V3 .*?(?=^\[|\Z)", text, re.M | re.S).group(0)


class SkippedCandidateUnderV3(_Candidates):
    """A candidate passed over for lacking an anchor is still validated, and a rejection fails V3."""

    def test_rejected_unanchored_last_candidate_fails_v3_while_v4_uses_the_older(self):
        older = self.write("run-a", ORCH_FIXTURE_TEXT)
        last = self.write("run-b", non_conforming(without_gated_orchestrator_row()))
        probe = self.work / "probe" / ORCH
        probe.parent.mkdir()
        probe.write_text(last.read_text(encoding="utf-8"), encoding="utf-8")
        self.assertFalse(orv.validate(probe, None).passed, "the skipped candidate must be rejected")
        self.assertIsNone(vv.award_itself_its_own_gate(last.read_text(encoding="utf-8")))
        real = vv.committed_instances

        def committed(artifact):
            return [older, last] if artifact == ORCH else real(artifact)

        out = io.StringIO()
        with mock.patch.object(vv, "committed_instances", committed), \
                mock.patch.object(sys, "argv", ["verify_validators.py"]), \
                contextlib.redirect_stdout(out):
            code = vv.main()
        text = out.getvalue()
        self.assertEqual(code, 1)
        v3 = v3_block(text)
        self.assertIn("[FAIL] V3", v3, "a rejected skipped candidate left V3 passing")
        # The detail prints a list, so the path appears in its repr form.
        self.assertIn(repr(f"{ORCH}: skipped candidate {last}")[1:-1], v3)
        line = next(ln for ln in text.splitlines()
                    if ln.lstrip().startswith(ORCH) and ORCH_WHAT in ln)
        self.assertIn("-> caught by O4", line, "V4 must still mutate the older anchored record")


class MutationConsoleLine(unittest.TestCase):
    """The console reports the outcome it observed, not the check it expected."""

    def run_main(self):
        out = io.StringIO()
        with mock.patch.object(sys, "argv", ["verify_validators.py"]), \
                contextlib.redirect_stdout(out):
            code = vv.main()
        return code, out.getvalue()

    def test_type_with_no_applicable_candidate_is_not_reported_caught(self):
        never = (lambda text: None, None, "O4", ORCH_WHAT)
        with mock.patch.dict(vv.MUTATIONS, {ORCH: never}):
            tried = [vv.instance_label(p) for p, _s, _e in vv.candidate_instances(ORCH)] \
                if hasattr(vv, "candidate_instances") else []
            code, text = self.run_main()
        self.assertEqual(code, 1)
        line = next(ln for ln in text.splitlines()
                    if ln.lstrip().startswith(ORCH) and ORCH_WHAT in ln)
        self.assertNotIn("-> caught by", line, f"the console claimed a catch: {line}")
        self.assertIn("NOT CAUGHT by O4", line)
        v4 = text.split("[FAIL] V4", 1)[1].split("\n[", 1)[0]
        self.assertIn("no candidate carries a mutation anchor", v4)
        self.assertTrue(tried)
        for label in tried:
            self.assertIn(label, v4, f"V4 did not name the candidate {label}")
        # Only this type's V3 outcome is asserted: V3 over the whole tree can fail for reasons
        # unrelated to this test, such as a working-directory-dependent rejection of another type.
        row = next(ln for ln in text.splitlines()
                   if ln.lstrip().startswith(ORCH) and "orchestration_result_validator" in ln)
        self.assertIn(" PASS ", row, f"V3 must still validate a candidate of the type: {row}")
        self.assertNotIn(f"{ORCH}:", v3_block(text), "V3 reported a rejection for the type")

    def test_outcome_text(self):
        self.assertEqual(vv.mutation_outcome("O4", None, ["O4"]), "caught by O4 (all: ['O4'])")
        line = vv.mutation_outcome("O4", f"{ORCH}: no mutation anchor", None)
        self.assertFalse(line.startswith("caught by"), line)


class RealTreeSelection(_Workdir):
    """On the committed run evidence, every registered type has an instance V4 can mutate."""

    def test_every_registered_type_selects_an_applicable_instance_that_is_caught(self):
        for artifact, module in sorted(fr.VALIDATORS.items()):
            with self.subTest(artifact=artifact):
                result = vv.conforming_instance(artifact)
                instance, envelope_path = result[0], result[2]
                self.assertIsNotNone(instance, f"no applicable candidate: {result}")
                text = instance.read_text(encoding="utf-8")
                old, _new, expect_id, _what = vv.resolve_mutation(artifact, text)
                self.assertIsNotNone(old, f"no mutation anchor in the selected {instance}")
                envelope = (json.loads(envelope_path.read_text(encoding="utf-8"))
                            if envelope_path else None)
                finding, failed = vv.mutation_verdict(artifact, __import__(module), text,
                                                      envelope, self.work)
                self.assertIsNone(finding, finding)
                self.assertIn(expect_id, failed)


if __name__ == "__main__":
    unittest.main()
