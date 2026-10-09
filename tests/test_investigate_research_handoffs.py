"""Contract-level regression tests for the investigate and research hand-off defect.

Between consecutive phases the runtime offers each completed upstream artifact under the
identifier the producing agent's manifest gives its own output (`upstream_inputs`, with the
identifier recorded at lease time). Guard G5-INPUT pools those artifacts with the run's
supplied inputs, narrows the pool to what the consuming agent declares, and for a menu
contract blocks unless one surviving type is on the consumer's accepted list.

Before this repair three of the four hand-offs of `investigate` and of `research` offered an
identifier the consumer did not accept, so every run of either workflow stalled at G5-INPUT:

  problem-framing / research-framing -> discovery    requirement-framing, not accepted by
                                                     omn-context-agent
  option-analysis / option-synthesis -> recommendation  only technical-recommendation reached
                                                     omn-tech-lead, which does not accept it
  recommendation -> publication                      technical-recommendation, not accepted by
                                                     omn-documentation

and both self-hosting profile rows that route to these workflows named an entry input type the
entry agent rejects (`investigation-request`, declared nowhere, and `research-question`,
optional only).

The repair widened two consumer contracts additively (the context agent accepts
`requirement-framing`, documentation accepts `technical-recommendation`), made both
recommendation rows' Input column name `investigation-report.md` so the Task Router routes the
evidence base tech-lead already accepts, and made both profile rows name `problem-statement`.

Every test here exercises the runtime's own functions -- `parse_phase_model`,
`derive_dependencies`, `upstream_inputs`, `narrow_inputs`, `resolve_input_contract`,
`load_agent`, and the profile router -- and invokes no model.

Every test fails against the tree before the repair and passes after it. A test that would pass
either way is not here: the one hand-off that already worked (discovery -> option analysis) is
exercised inside each chain test rather than by a test of its own, and each refusal is asserted
next to the acceptance the repair introduced, so the pair shows the widening admitted exactly
the delivered identifier and nothing more.

Known gaps. `KNOWN_BLOCKED_EDGES` and `KNOWN_UNROUTABLE_PROFILE_ROWS` list the hand-offs and
profile rows this repair deliberately left alone. The census tests assert that the blocked set
is *exactly* that list, so each must still fail today, and repairing one of them later fails the
census until it is removed from the list: the list can only shrink.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402
import release_note_validator as rnv  # noqa: E402
import self_hosting as sh  # noqa: E402
import state_engine as se  # noqa: E402

ENTRY_INPUT = "problem-statement"

# Hand-offs outside this repair's scope that still block at G5-INPUT. Each entry is
# (workflow, consuming phase). Remove an entry when its follow-up repair lands.
KNOWN_BLOCKED_EDGES = frozenset({
    ("implement-feature", "execution-planning"),
    ("implement-feature", "solution-design-and-risk-assessment"),
    ("fix-bug", "root-cause-analysis"),
    ("review-pull-request", "structural-compliance"),
    ("review-pull-request", "merge-decision"),
    ("release", "artifact-packaging"),
    ("release", "communication-and-post-release"),
})

# Profile rows whose Required Inputs the entry agent still rejects. Same rule: shrink only.
KNOWN_UNROUTABLE_PROFILE_ROWS = frozenset({"change-review", "framework-release"})

# The contract version that first accepts the delivered identifier, per changed agent.
CHANGED_AGENTS = {
    "omn-context-agent": ("requirement-framing", (1, 1, 0)),
    "omn-documentation": ("technical-recommendation", (1, 1, 0)),
}
CHANGED_WORKFLOWS = {"investigate": (1, 1, 0), "research": (1, 1, 0)}


def pool(*types: str) -> list:
    return [{"type": t, "reference": f"inline:{t}"} for t in types]


def semver(text: str) -> tuple:
    return tuple(int(p) for p in str(text).split("."))


def workflow_rows(workflow_id: str) -> list:
    return fr.parse_phase_model(fr.resolve_workflow(workflow_id)["specificationPath"])


def lease_identifier(workflow_rec: dict, phase_id: str) -> tuple:
    """(identifier, artifact path) exactly as the lease transition records them.

    The identifier is the producing manifest's output whose artifact equals the phase's
    resolved output artifact, falling back to the file stem. The artifact path points at
    the output's own template, an existing file, so `upstream_inputs` can read it.
    """
    phase = fr.resolve_phase(workflow_rec, phase_id)
    agent = fr.load_agent(phase["owner_agent"])
    output = fr.resolve_output_contract(agent, phase)
    identifier = next((o["identifier"] for o in agent["manifest"].get("outputs") or []
                       if o.get("artifact") == output["artifact"]),
                      Path(output["artifact"]).stem)
    return identifier, output["template_ref"]


class CompletedUpstreamStore:
    """The two store reads `upstream_inputs` makes, over phases recorded as completed."""

    def __init__(self, items: dict):
        self._items = items

    def has_item(self, state_id: str, work_type: str = "state") -> bool:
        return state_id in self._items

    def item(self, state_id: str, work_type: str = "state") -> dict:
        return self._items[state_id]


def g5_verdict(workflow_id: str, phase_id: str, supplied_types: list) -> tuple:
    """Replay guard G5-INPUT for one phase whose predecessors have all committed.

    Returns (passed, narrowed types, detail). The pool is the run's supplied inputs plus
    `upstream_inputs` over the dependency graph the Task Router derives.
    """
    wf = fr.resolve_workflow(workflow_id)
    rows = fr.parse_phase_model(wf["specificationPath"])
    supplied = pool(*supplied_types)
    deps = fr.derive_dependencies(rows, supplied)
    items = {}
    for row in rows:
        if row["phase"] == phase_id:
            break
        identifier, path = lease_identifier(wf, row["phase"])
        items[row["phase"]] = {"status": se.COMPLETED, "artifact_path": path,
                               "artifact_identifier": identifier}
    upstream = fr.upstream_inputs(CompletedUpstreamStore(items), None, phase_id, deps)
    owner = fr.resolve_phase(wf, phase_id)["owner_agent"]
    agent = fr.load_agent(owner)
    narrowed = fr.narrow_inputs(agent, supplied + upstream)
    try:
        fr.resolve_input_contract(agent, narrowed)
        return True, [s["type"] for s in narrowed], "pass"
    except fr.RuntimeError_ as exc:
        return False, [s["type"] for s in narrowed], str(exc)


def route(change_class: str) -> dict:
    """The profile router's own answer, through its command-line entry point."""
    proc = subprocess.run(
        [sys.executable, str(RUNTIME / "self_hosting.py"), "route", "--intent", change_class,
         "--json"], capture_output=True, text=True, cwd=str(REPO))
    if proc.returncode != 0:
        raise AssertionError(f"route --intent {change_class} exited {proc.returncode}: "
                             f"{proc.stdout}{proc.stderr}")
    return json.loads(proc.stdout)


def entry_agent(route_info: dict) -> str:
    wf = fr.resolve_workflow(route_info["workflow"])
    return fr.resolve_phase(wf, route_info["entry_phase"])["owner_agent"]


class ChainTests(unittest.TestCase):
    """Every phase of each chain passes G5-INPUT from problem-statement alone."""

    def assert_chain_passes(self, workflow_id: str):
        for row in workflow_rows(workflow_id):
            with self.subTest(workflow=workflow_id, phase=row["phase"]):
                passed, narrowed, detail = g5_verdict(workflow_id, row["phase"], [ENTRY_INPUT])
                self.assertTrue(passed, f"{workflow_id}/{row['phase']} blocks at G5-INPUT "
                                        f"with pool {narrowed}: {detail}")

    def test_investigate_chain_passes_g5_input_at_every_phase(self):
        self.assert_chain_passes("investigate")

    def test_research_chain_passes_g5_input_at_every_phase(self):
        self.assert_chain_passes("research")


class HandoffTests(unittest.TestCase):
    """The six hand-offs the repair changed, each named, each with what it now carries."""

    def assert_handoff(self, workflow_id: str, phase_id: str, delivered: str):
        passed, narrowed, detail = g5_verdict(workflow_id, phase_id, [ENTRY_INPUT])
        self.assertTrue(passed, f"{workflow_id}/{phase_id}: {detail}")
        self.assertIn(delivered, narrowed,
                      f"{delivered} did not survive narrowing at {workflow_id}/{phase_id}")

    def test_investigate_problem_framing_to_technical_discovery(self):
        self.assert_handoff("investigate", "technical-discovery", "requirement-framing")

    def test_investigate_option_analysis_to_recommendation(self):
        self.assert_handoff("investigate", "recommendation", "investigation-report")

    def test_investigate_recommendation_to_publication(self):
        self.assert_handoff("investigate", "publication", "technical-recommendation")

    def test_research_framing_to_technical_validation(self):
        self.assert_handoff("research", "technical-validation", "requirement-framing")

    def test_research_option_synthesis_to_recommendation_draft(self):
        self.assert_handoff("research", "recommendation-draft", "investigation-report")

    def test_research_recommendation_draft_to_findings_publication(self):
        self.assert_handoff("research", "findings-publication", "technical-recommendation")


class TaskRouterEdgeTests(unittest.TestCase):
    """The Input-column change adds exactly one dependency edge per workflow."""

    EXPECTED = {
        "investigate": {
            "problem-framing": [],
            "technical-discovery": ["problem-framing"],
            "option-analysis": ["technical-discovery"],
            "recommendation": ["technical-discovery", "option-analysis"],
            "publication": ["option-analysis", "recommendation"],
        },
        "research": {
            "research-framing": [],
            "technical-validation": ["research-framing"],
            "option-synthesis": ["technical-validation"],
            "recommendation-draft": ["technical-validation", "option-synthesis"],
            "findings-publication": ["option-synthesis", "recommendation-draft"],
        },
    }

    def test_dependency_graphs_are_the_declared_ones(self):
        for workflow_id, expected in self.EXPECTED.items():
            with self.subTest(workflow=workflow_id):
                graph = fr.derive_dependencies(workflow_rows(workflow_id), pool(ENTRY_INPUT))
                got = {p: [d["state_id"] for d in deps] for p, deps in graph.items()}
                self.assertEqual(got, expected)
                self.assertTrue(all(d["kind"] == "hard"
                                    for deps in graph.values() for d in deps))


class ContractBoundaryTests(unittest.TestCase):
    """Each widening admits the delivered identifier and still refuses its neighbours."""

    def test_context_agent_accepts_framing_and_still_refuses_undeclared(self):
        agent = fr.load_agent("omn-context-agent")
        self.assertTrue(fr.input_contract_satisfiable("omn-context-agent",
                                                      pool("requirement-framing")))
        self.assertFalse(fr.input_contract_satisfiable("omn-context-agent",
                                                       pool("investigation-request")))
        self.assertFalse(fr.input_contract_satisfiable("omn-context-agent", []))
        with self.assertRaises(fr.RuntimeError_) as raised:
            fr.resolve_input_contract(agent, pool("requirement-framing",
                                                  "investigation-request"))
        self.assertIn("declares no input type", str(raised.exception))

    def test_documentation_accepts_recommendation_and_still_refuses_undeclared(self):
        self.assertTrue(fr.input_contract_satisfiable("omn-documentation",
                                                      pool("technical-recommendation")))
        self.assertFalse(fr.input_contract_satisfiable("omn-documentation",
                                                       pool("requirement-framing")))
        self.assertFalse(fr.input_contract_satisfiable("omn-documentation",
                                                       pool("investigation-report")))
        self.assertFalse(fr.input_contract_satisfiable("omn-documentation", []))

    def test_recommendation_is_routed_its_evidence_base_and_tech_lead_menu_is_unchanged(self):
        passed, narrowed, _ = g5_verdict("investigate", "recommendation", [ENTRY_INPUT])
        self.assertTrue(passed)
        self.assertIn("investigation-report", narrowed)
        # tech-lead's own output alone still does not satisfy it: no menu was widened
        self.assertFalse(fr.input_contract_satisfiable("omn-tech-lead",
                                                       pool("technical-recommendation")))

    def test_business_analyst_accepts_routed_input_and_still_refuses_old_ones(self):
        info = route("decision-support")
        self.assertTrue(fr.input_contract_satisfiable(entry_agent(info),
                                                      pool(*info["required_inputs"])))
        self.assertFalse(fr.input_contract_satisfiable(entry_agent(info),
                                                       pool("investigation-request")))
        # optional-only to the entry agent, so it cannot satisfy the menu on its own
        self.assertFalse(fr.input_contract_satisfiable(entry_agent(info),
                                                       pool("research-question")))


class ProfileRouteTests(unittest.TestCase):
    """The two in-scope profile rows plan a run their entry agent accepts."""

    def assert_route_satisfiable(self, change_class: str, command: str, workflow: str):
        info = route(change_class)
        self.assertEqual((info["command"], info["workflow"]), (command, workflow))
        self.assertTrue(
            fr.input_contract_satisfiable(entry_agent(info), pool(*info["required_inputs"])),
            f"{change_class} routes {info['required_inputs']} to {entry_agent(info)}, which "
            f"does not accept them")
        # and that same input carries the whole chain
        for row in workflow_rows(workflow):
            passed, _, detail = g5_verdict(workflow, row["phase"], info["required_inputs"])
            self.assertTrue(passed, f"{workflow}/{row['phase']}: {detail}")

    def test_decision_support_route(self):
        self.assert_route_satisfiable("decision-support", "investigate", "investigate")

    def test_external_research_route(self):
        self.assert_route_satisfiable("external-research", "research", "research")


class KnownGapCensusTests(unittest.TestCase):
    """The blocked sets are exactly the recorded known gaps, so the lists can only shrink."""

    def test_blocked_hand_offs_are_exactly_the_known_gaps(self):
        blocked = set()
        for wf in fr.load_yaml("registry/workflows.yaml")["records"]:
            if wf.get("status") != "active":
                continue
            # the census supplies no run input, so each verdict rests on the hand-off alone
            for row in workflow_rows(wf["identifier"])[1:]:
                passed, _, _ = g5_verdict(wf["identifier"], row["phase"], [])
                if not passed:
                    blocked.add((wf["identifier"], row["phase"]))
        self.assertEqual(blocked, set(KNOWN_BLOCKED_EDGES),
                         "a hand-off outside the known-gap list blocks, or a known gap was "
                         "repaired and must be removed from KNOWN_BLOCKED_EDGES")

    def test_unroutable_profile_rows_are_exactly_the_known_gaps(self):
        profile_rows = [r["change_class"] for r in sh.load_profile()["routing"]]
        unroutable = set()
        for change_class in profile_rows:
            info = route(change_class)
            if not fr.input_contract_satisfiable(entry_agent(info),
                                                 pool(*info["required_inputs"])):
                unroutable.add(change_class)
        self.assertEqual(unroutable, set(KNOWN_UNROUTABLE_PROFILE_ROWS))


def recommendation_producers(workflow_id: str, phase_id: str) -> tuple:
    """(final, draft): the two phases delivering technical-recommendation to `phase_id`.

    Read from the Phase Model through the runtime's own guard path: the final one is the
    producer whose row carries a gate, the draft the one that does not.
    """
    wf = fr.resolve_workflow(workflow_id)
    rows = {r["phase"]: r for r in workflow_rows(workflow_id)}
    passed, _, _ = g5_verdict(workflow_id, phase_id, [ENTRY_INPUT])
    deps = fr.derive_dependencies(list(rows.values()), pool(ENTRY_INPUT))[phase_id]
    producers = [d["state_id"] for d in deps
                 if lease_identifier(wf, d["state_id"])[0] == "technical-recommendation"]
    gated = [p for p in producers if fr.phase_gates(rows[p])]
    drafts = [p for p in producers if not fr.phase_gates(rows[p])]
    return passed, producers, gated, drafts


class RecommendationPrecedenceTests(unittest.TestCase):
    """Two technical-recommendation artifacts reach each findings phase; the documentation
    contract must say which one governs, naming the producing phases the Phase Model gives."""

    FINDINGS = {"investigate": "publication", "research": "findings-publication"}
    DOCS = REPO / ".claude" / "agents" / "omn-documentation"

    def test_documentation_contract_names_the_governing_and_the_draft_recommendation(self):
        identity = (self.DOCS / "identity.md").read_text(encoding="utf-8")
        execution = (self.DOCS / "execution.md").read_text(encoding="utf-8")
        for workflow_id, phase_id in self.FINDINGS.items():
            with self.subTest(workflow=workflow_id):
                passed, producers, gated, drafts = recommendation_producers(workflow_id, phase_id)
                self.assertTrue(passed)
                self.assertEqual((len(producers), len(gated), len(drafts)), (2, 1, 1))
                self.assertIn(f"`{gated[0]}`", identity)
                self.assertIn(f"`{drafts[0]}`", identity)
                row = next(ln for ln in execution.splitlines()
                           if ln.startswith(f"| `{workflow_id}` | `{phase_id}` |"))
                self.assertIn(f"`{gated[0]}`", row)


class ReleaseNoteSourceTypeTests(unittest.TestCase):
    """The release note can record the recommendation it was published from."""

    def test_source_input_vocabulary_names_technical_recommendation(self):
        output = (REPO / ".claude" / "agents" / "omn-documentation" / "output.md").read_text(
            encoding="utf-8")
        declared = re.search(r"Declared `type` values are (.*?)\.\s", output, re.S).group(1)
        self.assertIn("`technical-recommendation`", declared)
        template = (REPO / ".claude" / "templates" / "release-note.md").read_text(encoding="utf-8")
        comment = re.search(r"- type:\s*#([^\n]*)", template).group(1)
        self.assertIn("technical-recommendation", [t.strip() for t in comment.split("|")])
        # and the Validation Engine accepts a release note that records it
        fixture = (RUNTIME / "fixtures" / "release-note.md").read_text(encoding="utf-8")
        self.assertIn("- type: final-change-summary", fixture)
        with tempfile.TemporaryDirectory() as tmp:
            note = Path(tmp) / "release-note.md"
            note.write_text(fixture.replace("- type: final-change-summary",
                                            "- type: technical-recommendation", 1),
                            encoding="utf-8")
            report = rnv.validate(note)
        self.assertTrue(report.passed, report.blocking_failures)


def host_registration_versions(agent_id: str) -> list:
    text = (REPO / ".claude" / "agents" / f"{agent_id}.agent.md").read_text(encoding="utf-8")
    table = re.findall(r"^\|\s*version\s*\|\s*`([^`]+)`\s*\|", text, re.M)
    check = re.findall(r"`metadata\.version` is `([^`]+)`", text)
    return table + check


class VersionAgreementTests(unittest.TestCase):
    """Manifest, registry record, and host registration state one version, at or past the
    contract version that first accepts the delivered identifier."""

    def test_changed_agents_agree_on_their_version_everywhere(self):
        registry = {r["identifier"]: r for r in fr.load_yaml("registry/agents.yaml")["records"]}
        for agent_id, (_, minimum) in CHANGED_AGENTS.items():
            with self.subTest(agent=agent_id):
                manifest_version = fr.load_agent(agent_id)["manifest"]["metadata"]["version"]
                host = host_registration_versions(agent_id)
                self.assertEqual(len(host), 2, f"{agent_id} host registration states its "
                                               f"version {len(host)} time(s), expected 2")
                self.assertEqual({manifest_version, registry[agent_id]["version"], *host},
                                 {manifest_version})
                self.assertGreaterEqual(semver(manifest_version), minimum)

    def test_changed_agents_accept_and_register_the_delivered_identifier(self):
        registry = {r["identifier"]: r for r in fr.load_yaml("registry/agents.yaml")["records"]}
        for agent_id, (identifier, _) in CHANGED_AGENTS.items():
            with self.subTest(agent=agent_id):
                manifest = fr.load_agent(agent_id)["manifest"]
                self.assertIn(identifier,
                              [i["identifier"] for i in manifest["inputs"]["accepted"]])
                data_deps = [d["identifier"] for d in registry[agent_id]["dependencies"]
                             if d.get("dependencyType") == "data"]
                self.assertIn(identifier, data_deps)

    def test_changed_workflows_moved_their_version(self):
        for workflow_id, minimum in CHANGED_WORKFLOWS.items():
            with self.subTest(workflow=workflow_id):
                self.assertGreaterEqual(
                    semver(fr.resolve_workflow(workflow_id)["version"]), minimum)


if __name__ == "__main__":
    unittest.main()
