"""Contract-level regression test for the refactor phase-2-to-phase-3 handoff defect.

`agents/omn-qa/manifest.yaml` declares exactly one output identifier,
`validation-report`, and the Phase Model of `workflows/refactor.md` hands that
artifact from `safety-net-establishment` to `refactor-implementation`, a phase
`omn-dev-1-implement` owns. Until this fix that agent's accepted-input menu named
`technical-design`, `bug-analysis` and `test-baseline-record`, and the third of
those was declared as an output by no agent at all. The producing and consuming
sets were therefore disjoint: `narrow_inputs` discarded the delivered artifact
before `resolve_input_contract` ever saw it, the menu rule then failed because
every surviving type was merely optional, and guard G5-INPUT blocked the phase
with reason `awaiting_dependency_output`.

These tests pin the corrected manifest at the two points that made the defect
possible -- that the consumer accepts the identifier its producer actually emits,
and that no identifier on its accepted menu lacks a producer -- and they pin the
widening as additive rather than as a substitution, by replaying the sibling
phases' pools and the refusal case.

Narrowing is asserted in its own right. The artifact was lost at narrowing, not
at resolution, so a check that only observes the final verdict would still pass
if narrowing regressed and something else happened to satisfy the menu.

Scope note. The two framework-wide checks the root-cause analysis names -- a
per-edge check over every declared workflow data edge, and a check that every
accepted identifier anywhere has a producer -- are deliberately not here. Both
fail against the repository as it stands today (fourteen mismatched edges before
this fix and thirteen after; twenty-seven producerless accepted identifiers, of
which twenty-six are legitimate operator-supplied request types), and both are
routed as their own change rather than shipped inside this repair.

They import the framework's own runtime from `.claude/runtime`, so they exercise
the real guard path rather than a restatement of it.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402

CONSUMER = "omn-dev-1-implement"
PRODUCER = "omn-qa"

# The identifier withdrawn by this fix. It was declared as an output by no agent,
# and had never been supplied as an input by any run.
WITHDRAWN = "test-baseline-record"

# Run-level input types as the three commands that dispatch this agent actually
# record them, taken from committed run state rather than invented here.
REFACTOR_RUN_INPUTS = ["change-request", "business-intent", "architecture-context"]
IMPLEMENT_RUN_INPUTS = ["feature-request"]
BUGFIX_RUN_INPUTS = ["defect-report"]


def pool(*types: str) -> list:
    """The shape the guard assembles: run-level supplied inputs plus upstream artifacts."""
    return [{"type": t, "reference": f"inline:{t}"} for t in types]


def accepted_identifiers(agent: dict) -> list:
    spec = agent["manifest"].get("inputs", {}) or {}
    return [i["identifier"] for i in (spec.get("accepted") or [])]


def output_identifiers(agent: dict) -> list:
    return [o["identifier"] for o in (agent["manifest"].get("outputs") or [])]


def producer_map() -> dict:
    """identifier -> the agents declaring it as an output, across every active record."""
    registry = fr.load_yaml("registry/agents.yaml")
    producers: dict[str, list] = {}
    for record in registry.get("records") or []:
        if record.get("status") != "active":
            continue
        manifest = fr.load_yaml(record["specificationPath"])
        for out in manifest.get("outputs") or []:
            producers.setdefault(out["identifier"], []).append(record["identifier"])
    return producers


class ProducerConsumerIdentifierTests(unittest.TestCase):
    """The two conditions whose absence let the disjoint sets exist."""

    def setUp(self):
        self.consumer = fr.load_agent(CONSUMER)
        self.producer = fr.load_agent(PRODUCER)
        self.accepted = accepted_identifiers(self.consumer)

    def test_consumer_accepts_the_identifier_the_producer_emits(self):
        emitted = output_identifiers(self.producer)
        self.assertTrue(emitted, f"{PRODUCER} declares no output identifier")
        self.assertTrue(
            set(emitted) & set(self.accepted),
            f"{PRODUCER} emits {emitted} and {CONSUMER} accepts {self.accepted}; "
            f"the sets are disjoint, so the refactor handoff cannot pass G5-INPUT")

    def test_validation_report_is_the_identifier_in_question(self):
        self.assertIn("validation-report", output_identifiers(self.producer))
        self.assertIn("validation-report", self.accepted)

    def test_no_accepted_identifier_lacks_a_producer(self):
        producers = producer_map()
        orphans = [i for i in self.accepted if i not in producers]
        self.assertEqual(
            orphans, [],
            f"{CONSUMER} accepts {orphans}, which no active agent manifest declares "
            f"as an output; an accepted identifier no agent can produce is a menu "
            f"entry no handoff can ever satisfy")

    def test_withdrawn_identifier_is_no_longer_accepted(self):
        self.assertNotIn(WITHDRAWN, self.accepted)

    def test_manifest_and_registry_declare_the_same_version(self):
        # load_agent raises on a mismatch; this states the coupling explicitly, so a
        # manifest bumped without its registry record fails here by name.
        registry = fr.load_yaml("registry/agents.yaml")
        record = next(r for r in registry["records"] if r["identifier"] == CONSUMER)
        self.assertEqual(self.consumer["manifest"]["metadata"]["version"],
                         record["version"])


class NarrowingTests(unittest.TestCase):
    """Narrowing is where the delivered artifact was lost."""

    def setUp(self):
        self.consumer = fr.load_agent(CONSUMER)

    def test_validation_report_survives_narrowing(self):
        supplied = pool(*REFACTOR_RUN_INPUTS, "validation-report")
        kept = [s["type"] for s in fr.narrow_inputs(self.consumer, supplied)]
        self.assertIn("validation-report", kept)

    def test_narrowing_still_drops_an_undeclared_type(self):
        kept = [s["type"] for s in
                fr.narrow_inputs(self.consumer, pool("defect-report", "bug-analysis"))]
        self.assertEqual(kept, ["bug-analysis"])


class InputContractResolutionTests(unittest.TestCase):
    """The menu rule, replayed over the pools the three dispatching commands build."""

    def setUp(self):
        self.consumer = fr.load_agent(CONSUMER)

    def resolve(self, supplied: list) -> dict:
        return fr.resolve_input_contract(
            self.consumer, fr.narrow_inputs(self.consumer, supplied))

    def test_refactor_pool_resolves(self):
        contract = self.resolve(pool(*REFACTOR_RUN_INPUTS, "validation-report"))
        self.assertIn("validation-report",
                      [s["type"] for s in contract["supplied"]])

    def test_refactor_pool_is_satisfiable_through_the_guard_entry_point(self):
        self.assertTrue(fr.input_contract_satisfiable(
            CONSUMER, pool(*REFACTOR_RUN_INPUTS, "validation-report")))

    def test_implement_feature_pool_still_resolves(self):
        self.assertTrue(fr.input_contract_satisfiable(
            CONSUMER, pool(*IMPLEMENT_RUN_INPUTS, "technical-design")))

    def test_fix_bug_pool_still_resolves(self):
        self.assertTrue(fr.input_contract_satisfiable(
            CONSUMER, pool(*BUGFIX_RUN_INPUTS, "bug-analysis")))

    def test_menu_still_refuses_a_pool_carrying_no_accepted_identifier(self):
        with self.assertRaises(fr.RuntimeError_) as raised:
            self.resolve(pool(*REFACTOR_RUN_INPUTS))
        self.assertIn("no accepted input type supplied", str(raised.exception))

    def test_menu_still_refuses_an_empty_pool(self):
        self.assertFalse(fr.input_contract_satisfiable(CONSUMER, []))

    def test_withdrawn_identifier_no_longer_satisfies_the_menu(self):
        self.assertFalse(fr.input_contract_satisfiable(CONSUMER, pool(WITHDRAWN)))


if __name__ == "__main__":
    unittest.main()
