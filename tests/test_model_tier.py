"""Tests for the per-phase model tier (runtime 0.9.0): the declaration in
`config/model-tier-policy.json`, the pure resolver and its escalation rule, the additive
`model_tier` envelope record, the event detail and prompt line, the per-tier execution
metrics, and the two registry-coverage checks that guard them.

The declaration and resolver tests run against the real framework tree. The dispatch tests copy
the framework tree (without its runs) into a temporary directory and drive the real command
line there, because the runtime derives its root from its own location: nothing here writes
into `.claude/runs`.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
CLAUDE = REPO / ".claude"
RUNTIME_DIR = CLAUDE / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import execution_metrics as em  # noqa: E402
import framework_runtime as fr  # noqa: E402
import state_engine as se  # noqa: E402
import verify_registry_coverage as vrc  # noqa: E402

TIERS = fr.MODEL_TIERS
PRE_CHANGE_ENVELOPE_KEYS = frozenset((
    "invocation_id", "run_id", "work_item_id", "idempotency_key", "state_id", "phase_index",
    "agent_id", "agent_version", "adapter", "dispatch_mode", "host_registration",
    "capability_bindings", "skill_dispatch", "input_contract", "prior_validation",
    "prior_rejection", "upstream_artifacts", "task_context", "parallel_group",
    "context_slice", "memory_slice", "constraints", "timeout_profile",
    "expected_output_schema", "built_at", "context_budget"))
ORIGINAL_ENVELOPE_FIELDS = (
    "invocation_id", "run_id", "work_item_id", "idempotency_key", "state_id", "phase_index",
    "agent_id", "agent_version", "adapter", "dispatch_mode", "host_registration")


def active_phases() -> dict:
    out = {}
    for rec in fr.load_yaml("registry/workflows.yaml")["records"]:
        if rec.get("status") == "active":
            out[rec["identifier"]] = [r["phase"] for r in
                                      fr.parse_phase_model(rec["specificationPath"])]
    return out


def synthetic_policy() -> dict:
    return {"hints": {"light": "h-light", "standard": "inherit", "deep": "h-deep"},
            "phases": {"w": {"p-light": "light", "p-standard": "standard", "p-deep": "deep"}}}


class DeclarationTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.policy = fr.load_model_tier_policy()
        cls.phases = active_phases()

    def test_the_declaration_ships_and_loads(self):
        self.assertIsNotNone(self.policy)
        self.assertEqual(set(self.policy["hints"]), set(TIERS))

    def test_every_phase_of_every_active_workflow_has_exactly_one_declared_tier(self):
        declared = self.policy["phases"]
        for wid, phases in self.phases.items():
            self.assertEqual(sorted(declared.get(wid, {})), sorted(phases), wid)
            for ph in phases:
                self.assertIn(declared[wid][ph], TIERS, f"{wid}/{ph}")
        self.assertEqual(sum(len(v) for v in self.phases.values()), 37)

    def test_the_standard_tier_inherits_the_host_model(self):
        self.assertEqual(self.policy["hints"]["standard"], fr.INHERIT_HINT)

    def test_at_least_three_of_six_implement_feature_phases_are_non_deep(self):
        impl = self.policy["phases"]["implement-feature"]
        self.assertEqual(len(impl), 6)
        self.assertGreaterEqual(sum(1 for t in impl.values() if t != "deep"), 3)

    def test_operator_resolutions_hold(self):
        impl = self.policy["phases"]["implement-feature"]
        self.assertEqual(impl["execution-planning"], "standard")
        self.assertEqual(impl["scope-and-acceptance"], "light")
        self.assertEqual(impl["documentation-and-release-handoff"], "light")
        for phase in ("solution-design-and-risk-assessment", "implementation",
                      "quality-review"):
            self.assertEqual(impl[phase], "deep")

    def test_hints_live_in_configuration_data_only(self):
        words = [h for h in self.policy["hints"].values() if h != fr.INHERIT_HINT]
        self.assertTrue(words)
        for rel in ("runtime/framework_runtime.py", "runtime/execution_metrics.py",
                    "runtime/verify_registry_coverage.py"):
            text = (CLAUDE / rel).read_text(encoding="utf-8")
            for w in words:
                self.assertIsNone(re.search(rf"\b{re.escape(w)}\b", text, re.I),
                                  f"{w!r} appears in {rel}")

    def test_no_tier_assignment_appears_in_agent_text_or_phase_model_tables(self):
        for p in (CLAUDE / "agents").rglob("*.md"):
            text = p.read_text(encoding="utf-8")
            self.assertNotIn("model_tier", text, str(p))
            self.assertNotIn("model-tier-policy", text, str(p))
        for p in sorted((CLAUDE / "agents").glob("*.agent.md")):
            self.assertRegex(p.read_text(encoding="utf-8"), r"(?m)^model:\s*inherit\s*$")
        for rec in fr.load_yaml("registry/workflows.yaml")["records"]:
            rows = fr.parse_phase_model(rec["specificationPath"])
            self.assertFalse(any("tier" in k for r in rows for k in r), rec["identifier"])

    def test_the_governance_documents_state_the_field_the_rule_and_the_declaration(self):
        runtime_md = (CLAUDE / "config" / "runtime.md").read_text(encoding="utf-8")
        section = runtime_md[runtime_md.index("## Model Tiers"):]
        section = section[:section.index("\n## ", 5)]
        for needed in ("config/model-tier-policy.json", "model_tier", "validation_failed",
                       "supersessions", "never retried at the same tier", "deep",
                       "non_deep_share", "inherit"):
            self.assertIn(needed, section)
        engine_md = (CLAUDE / "config" / "execution-engine.md").read_text(encoding="utf-8")
        self.assertIn("- `model_tier`", engine_md)
        flat = " ".join(section.split())
        self.assertIn("never promotes one", flat)
        self.assertIn("reserved as `inherit`", flat)

    def test_runtime_version_rose_from_the_prior_release(self):
        parts = tuple(int(x) for x in fr.RUNTIME_VERSION.split("."))
        self.assertGreater(parts, (0, 8, 0))


class LoaderTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-tier-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        (self.tmp / "config").mkdir()
        self.path = self.tmp / fr.MODEL_TIER_POLICY_REL
        patcher = mock.patch.object(fr, "CLAUDE", self.tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def write(self, data):
        self.path.write_text(data if isinstance(data, str) else json.dumps(data),
                             encoding="utf-8")

    def test_an_absent_file_is_not_an_error(self):
        self.assertIsNone(fr.load_model_tier_policy())

    def test_a_valid_file_loads(self):
        self.write(synthetic_policy())
        self.assertEqual(fr.load_model_tier_policy()["hints"]["deep"], "h-deep")

    def test_an_unreadable_file_is_a_policy_failure(self):
        self.write("{not json")
        with self.assertRaises(fr.RuntimeError_) as cm:
            fr.load_model_tier_policy()
        self.assertEqual(cm.exception.failure_class, "policy-failure")

    def test_an_unknown_tier_is_a_policy_failure(self):
        bad = synthetic_policy()
        bad["phases"]["w"]["p-light"] = "ultra"
        self.write(bad)
        with self.assertRaises(fr.RuntimeError_) as cm:
            fr.load_model_tier_policy()
        self.assertEqual(cm.exception.failure_class, "policy-failure")

    def test_a_tier_without_a_hint_is_a_policy_failure(self):
        bad = synthetic_policy()
        del bad["hints"]["deep"]
        self.write(bad)
        with self.assertRaises(fr.RuntimeError_):
            fr.load_model_tier_policy()

    def test_a_standard_hint_other_than_inherit_is_a_policy_failure(self):
        bad = synthetic_policy()
        bad["hints"]["standard"] = "h-standard"
        self.write(bad)
        with self.assertRaises(fr.RuntimeError_) as cm:
            fr.load_model_tier_policy()
        self.assertEqual(cm.exception.failure_class, "policy-failure")
        self.assertIn("reserved", str(cm.exception))

    def test_a_blank_hint_is_a_policy_failure(self):
        bad = synthetic_policy()
        bad["hints"]["light"] = "  "
        self.write(bad)
        with self.assertRaises(fr.RuntimeError_):
            fr.load_model_tier_policy()


class ResolverTestCase(unittest.TestCase):

    def setUp(self):
        self.policy = synthetic_policy()

    def resolve(self, phase, validator=0, rollback=0, policy="default"):
        return fr.resolve_model_tier(self.policy if policy == "default" else policy, "w",
                                     phase, {"validator": validator,
                                             "gate_rollback": rollback})

    def test_no_rejection_resolves_the_declared_tier_with_its_hint(self):
        for phase, tier in (("p-light", "light"), ("p-standard", "standard"),
                            ("p-deep", "deep")):
            rec = self.resolve(phase)
            self.assertEqual((rec["tier"], rec["host_hint"], rec["escalation"]),
                             (tier, self.policy["hints"][tier], {}))
            self.assertIn("declared", rec["basis"])

    def test_a_validator_rejection_promotes_one_tier_and_states_why(self):
        rec = self.resolve("p-light", validator=1)
        self.assertEqual(rec["tier"], "standard")
        self.assertEqual(rec["escalation"]["from"], "light")
        self.assertEqual(rec["escalation"]["to"], "standard")
        self.assertIn("1 validator rejection", rec["escalation"]["reason"])

    def test_a_gate_rejection_with_rollback_promotes_one_tier(self):
        rec = self.resolve("p-standard", rollback=1)
        self.assertEqual(rec["tier"], "deep")
        self.assertEqual(rec["escalation"]["gate_rollbacks"], 1)
        self.assertEqual(rec["host_hint"], "h-deep")

    def test_each_rejection_promotes_one_step_and_deep_is_the_ceiling(self):
        self.assertEqual(self.resolve("p-light", validator=1, rollback=1)["tier"], "deep")
        self.assertEqual(self.resolve("p-light", validator=5)["tier"], "deep")

    def test_deep_never_rises_and_records_no_promotion(self):
        rec = self.resolve("p-deep", validator=2, rollback=1)
        self.assertEqual(rec["tier"], "deep")
        self.assertEqual(rec["escalation"], {})
        self.assertIn("ceiling", rec["basis"])

    def test_no_tier_is_ever_lowered(self):
        for phase, base in (("p-light", 0), ("p-standard", 1), ("p-deep", 2)):
            last = base
            for n in range(0, 6):
                got = TIERS.index(self.resolve(phase, validator=n)["tier"])
                self.assertGreaterEqual(got, last)
                self.assertGreaterEqual(got, base)
                last = got

    def test_an_undeclared_phase_is_standard_and_escalates_from_standard(self):
        plain = self.resolve("p-missing")
        self.assertEqual((plain["tier"], plain["host_hint"]), ("standard", "inherit"))
        self.assertIn("no entry", plain["basis"])
        self.assertEqual(self.resolve("p-missing", validator=1)["tier"], "deep")

    def test_an_absent_declaration_inherits_and_never_promotes(self):
        rec = self.resolve("p-light", validator=3, policy=None)
        self.assertEqual((rec["tier"], rec["host_hint"], rec["escalation"]),
                         ("standard", fr.INHERIT_HINT, {}))

    def test_resolution_is_pure_and_repeatable(self):
        first = self.resolve("p-light", validator=1, rollback=1)
        self.assertEqual(first, self.resolve("p-light", validator=1, rollback=1))
        json.dumps(first)


class RejectionCountTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-tier-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def ledger(self, entries):
        (self.tmp / "recovery-ledger.json").write_text(
            json.dumps({"schema": "x", "entries": entries}), encoding="utf-8")

    def test_only_validator_rejections_under_the_phase_count(self):
        self.ledger([
            {"state_id": "p", "reason_code": "validation_failed", "status": "resolved"},
            {"state_id": "p", "reason_code": "validation_failed", "status": "open"},
            {"state_id": "p", "reason_code": "missing_artifact", "status": "resolved"},
            {"state_id": "other", "reason_code": "validation_failed", "status": "open"},
            {"state_id": "Review Gate", "reason_code": "policy_block", "status": "open"}])
        got = fr.count_tier_rejections(self.tmp, {"state_id": "p"})
        self.assertEqual(got, {"validator": 2, "gate_rollback": 0})

    def test_each_supersession_is_one_gate_rejection_with_rollback(self):
        got = fr.count_tier_rejections(
            self.tmp, {"state_id": "p", "supersessions": [{"attempt": 1}, {"attempt": 2}]})
        self.assertEqual(got, {"validator": 0, "gate_rollback": 2})

    def test_a_rollback_recorded_by_the_state_engine_counts_once(self):
        common = dict(actor_type="runtime", actor_id="test", detail="test")
        store = se.StateStore.create(
            self.tmp / "run-tier", run_id="run-tier", command_id="implement",
            workflow_id="implement-feature", workflow_version="1.0.0",
            runtime_version=fr.RUNTIME_VERSION, input_digest="sha256:test", inputs=[])
        item = store.add_item(se.new_work_item(
            run_id="run-tier", workflow_id="implement-feature", state_id="implementation",
            work_type="state", owner_agent_id="omn-dev-1-implement", phase_index=1, gate=None,
            artifact="x.md", depends_on=[]))
        store.transition(item, se.LEASED, reason_code="leased", **common)
        store.transition(item, se.RUNNING, reason_code="execution_started", **common)
        store.transition(item, se.COMPLETED, reason_code="output_accepted",
                         fields={"completion": {"artifact_path": "runs/x/a.md",
                                                "artifact_digest": "sha256:aaa"},
                                 "artifact_path": "runs/x/a.md"}, **common)
        self.assertEqual(fr.count_tier_rejections(self.tmp / "run-tier", item),
                         {"validator": 0, "gate_rollback": 0})
        store.transition(item, se.PENDING, reason_code="enqueued",
                         fields={"supersession": {"authorisation_id": "RB-x-01",
                                                  "gate": "Review Gate",
                                                  "target": "implementation"}}, **common)
        counted = fr.count_tier_rejections(self.tmp / "run-tier", item)
        self.assertEqual(counted, {"validator": 0, "gate_rollback": 1})
        record = fr.resolve_model_tier(fr.load_model_tier_policy(), "implement-feature",
                                       "scope-and-acceptance", counted)
        self.assertEqual((record["tier"], record["escalation"]["gate_rollbacks"]),
                         ("standard", 1))

    def test_an_absent_ledger_counts_nothing(self):
        self.assertEqual(fr.count_tier_rejections(self.tmp, {"state_id": "p"}),
                         {"validator": 0, "gate_rollback": 0})


class MetricsTestCase(unittest.TestCase):

    @staticmethod
    def started(tier=None):
        details = {"invocation_id": "i"}
        if tier:
            details["model_tier"] = tier
        return {"event_type": "invocation_started", "details_ref": details}

    def test_invocations_and_bytes_group_by_tier_and_sum_to_the_totals(self):
        events = [self.started("light"), self.started("deep"), self.started("deep"),
                  self.started("standard"), self.started(), {"event_type": "validation_passed"}]
        per_phase = [
            {"model_tier": "light", "context_estimate": {"progressive_estimate_bytes": 10}},
            {"model_tier": "deep", "context_estimate": {"progressive_estimate_bytes": 30}},
            {"model_tier": None, "context_estimate": {"progressive_estimate_bytes": 7}},
            {"model_tier": "standard", "context_estimate": None}]
        out = em.tier_summary(events, per_phase)
        self.assertEqual(out["by_tier"]["deep"], {"invocations": 2, "estimated_bytes": 30})
        self.assertEqual(out["by_tier"]["untiered"], {"invocations": 1, "estimated_bytes": 7})
        self.assertEqual(out["invocations_total"], 5)
        self.assertEqual(out["estimated_bytes_total"], 47)
        self.assertEqual(out["non_deep_share"], 0.5)

    def test_no_tiered_invocation_leaves_the_share_empty(self):
        out = em.tier_summary([self.started()], [])
        self.assertIsNone(out["non_deep_share"])
        self.assertEqual(out["by_tier"]["untiered"]["invocations"], 1)


class VerifierTestCase(unittest.TestCase):

    def run_check(self, fn, **patches):
        res = vrc.Result()
        patches.setdefault("INHERIT_HINT", fr.INHERIT_HINT)
        with mock.patch.multiple(fr, **patches):
            fn(res)
        return res.checks[0]

    def test_coverage_check_passes_on_the_shipped_declaration(self):
        self.assertEqual(self.run_check(vrc.c7_tier_declaration)["result"], "PASS")

    def test_coverage_check_fails_when_one_phase_entry_is_removed(self):
        policy = json.loads(json.dumps(fr.load_model_tier_policy()))
        del policy["phases"]["release"]["artifact-packaging"]
        check = self.run_check(vrc.c7_tier_declaration,
                               load_model_tier_policy=lambda: policy)
        self.assertEqual(check["result"], "FAIL")
        self.assertEqual(check["counts"]["uncovered"], 1)

    def test_coverage_check_fails_on_an_entry_naming_a_missing_phase(self):
        policy = json.loads(json.dumps(fr.load_model_tier_policy()))
        policy["phases"]["release"]["no-such-phase"] = "light"
        check = self.run_check(vrc.c7_tier_declaration,
                               load_model_tier_policy=lambda: policy)
        self.assertEqual(check["result"], "FAIL")
        self.assertEqual(check["counts"]["stale_entries"], 1)

    def test_coverage_check_fails_below_the_non_deep_bar(self):
        policy = json.loads(json.dumps(fr.load_model_tier_policy()))
        for ph in ("scope-and-acceptance", "documentation-and-release-handoff"):
            policy["phases"]["implement-feature"][ph] = "deep"
        check = self.run_check(vrc.c7_tier_declaration,
                               load_model_tier_policy=lambda: policy)
        self.assertEqual(check["result"], "FAIL")
        self.assertIn("non-deep", check["detail"])

    def test_coverage_check_fails_when_the_standard_hint_is_not_inherit(self):
        policy = json.loads(json.dumps(fr.load_model_tier_policy()))
        policy["hints"]["standard"] = "something-else"
        check = self.run_check(vrc.c7_tier_declaration,
                               load_model_tier_policy=lambda: policy)
        self.assertEqual(check["result"], "FAIL")
        self.assertIn("reserved", check["detail"])

    def test_coverage_check_fails_when_the_file_is_absent(self):
        check = self.run_check(vrc.c7_tier_declaration, load_model_tier_policy=lambda: None)
        self.assertEqual(check["result"], "FAIL")

    def test_monotonic_check_passes_and_fails_on_a_resolver_that_does_not_rise(self):
        self.assertEqual(self.run_check(vrc.c8_escalation_monotonic)["result"], "PASS")

        real = fr.resolve_model_tier

        def flat(policy, workflow_id, phase, rejections=None):
            return real(policy, workflow_id, phase, {})

        check = self.run_check(vrc.c8_escalation_monotonic, resolve_model_tier=flat)
        self.assertEqual(check["result"], "FAIL")


class DispatchTestCase(unittest.TestCase):
    """The real command line, against a copy of the framework tree held in a temp directory."""

    @classmethod
    def make_tree(cls, text: str):
        tmp = Path(tempfile.mkdtemp(prefix="omn-tier-run-"))
        shutil.copytree(CLAUDE, tmp / ".claude", ignore=shutil.ignore_patterns(
            "runs", "__pycache__", "worktrees"))
        (tmp / "req.md").write_text(text, encoding="utf-8")
        return tmp

    @staticmethod
    def cli(tmp: Path, *args):
        return subprocess.run(
            [sys.executable, str(tmp / ".claude" / "runtime" / "framework_runtime.py"), *args],
            cwd=tmp, capture_output=True, text=True, encoding="utf-8")

    @classmethod
    def plan(cls, tmp: Path) -> str:
        done = cls.cli(tmp, "plan", "--command", "implement", "--input",
                       "feature-request=req.md")
        assert done.returncode == 0, done.stderr
        return json.loads(done.stdout[done.stdout.index("{"):])["run_id"]

    @classmethod
    def setUpClass(cls):
        cls.tmp = cls.make_tree("Add a CSV export of orders for administrators.\n")
        cls.run_id = cls.plan(cls.tmp)
        cls.run_dir = cls.tmp / ".claude" / "runs" / cls.run_id
        done = cls.cli(cls.tmp, "dispatch", "--run-id", cls.run_id, "--phase",
                       "scope-and-acceptance")
        assert done.returncode == 0, done.stderr
        cls.dispatch_out = done.stdout

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def state_file(self, phase, name):
        return self.run_dir / "states" / phase / name

    def envelope(self, phase="scope-and-acceptance"):
        return json.loads(self.state_file(phase, "invocation-envelope.json")
                          .read_text(encoding="utf-8"))

    def test_the_envelope_carries_a_complete_tier_record(self):
        rec = self.envelope()["model_tier"]
        self.assertEqual(set(rec), {"tier", "host_hint", "basis", "escalation"})
        self.assertEqual(rec["tier"], "light")
        self.assertEqual(rec["host_hint"], fr.load_model_tier_policy()["hints"]["light"])
        self.assertTrue(rec["basis"])
        self.assertEqual(rec["escalation"], {})

    def test_the_original_envelope_fields_keep_their_names_and_values(self):
        env = self.envelope()
        for key in ORIGINAL_ENVELOPE_FIELDS:
            self.assertIn(key, env)
        self.assertEqual(env["state_id"], "scope-and-acceptance")
        self.assertEqual(env["adapter"], "host-subagent")
        self.assertEqual(env["agent_id"], "omn-product-owner")
        self.assertEqual(env["run_id"], self.run_id)

    def test_only_model_tier_was_added_to_the_envelope_field_set(self):
        self.assertEqual(set(self.envelope()) - PRE_CHANGE_ENVELOPE_KEYS, {"model_tier"})
        self.assertEqual(PRE_CHANGE_ENVELOPE_KEYS - set(self.envelope()), set())

    def test_the_event_and_the_prompt_and_the_console_state_the_tier(self):
        events = [json.loads(ln) for ln in
                  (self.run_dir / "events.jsonl").read_text(encoding="utf-8").splitlines()
                  if ln.strip()]
        started = [e for e in events if e["event_type"] == "invocation_started"]
        self.assertEqual(started[-1]["details_ref"]["model_tier"], "light")
        self.assertFalse(started[-1]["details_ref"]["escalated"])
        prompt = self.state_file("scope-and-acceptance", "dispatch-prompt.md").read_text(
            encoding="utf-8")
        self.assertIn("Model tier: `light`", prompt)
        self.assertIn("Pass the hint as the per-dispatch model override.", prompt)
        self.assertIn("model tier         : light", self.dispatch_out)

    def test_metrics_report_invocations_by_tier(self):
        data = em.compute(self.run_dir, self.tmp / ".claude")
        mt = data["model_tiers"]
        self.assertEqual(mt["by_tier"]["light"]["invocations"], 1)
        self.assertEqual(mt["invocations_total"], data["agents_executed"]["invocations"])
        self.assertEqual(mt["estimated_bytes_total"],
                         data["tokens_or_context_estimate"]["progressive_bytes"])
        self.assertEqual(mt["non_deep_share"], 1.0)

    def test_a_real_validator_rejection_promotes_the_next_dispatch(self):
        tmp = self.make_tree("Add a PDF export of invoices for administrators.\n")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        run_id = self.plan(tmp)
        phase = "scope-and-acceptance"
        run_dir = tmp / ".claude" / "runs" / run_id
        state_dir = run_dir / "states" / phase
        self.assertEqual(self.cli(tmp, "dispatch", "--run-id", run_id, "--phase",
                                  phase).returncode, 0)
        first = json.loads((state_dir / "invocation-envelope.json").read_text(encoding="utf-8"))
        self.assertEqual(first["model_tier"]["tier"], "light")
        # The agent reports an artifact the Validation Engine rejects: the runtime itself
        # ledgers the rejection, which is the recorded state the next dispatch reads.
        artifact = tmp / ".claude" / first["expected_output_schema"]["artifact_path"]
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("# not a scope definition\n", encoding="utf-8")
        (state_dir / "result-envelope.json").write_text(json.dumps({
            "invocation_id": first["invocation_id"], "status": "succeeded",
            "artifact_refs": [first["expected_output_schema"]["artifact_path"]],
            "structured_output": {}, "evidence_refs": [], "confidence": 0.5,
            "declared_side_effects": [".claude/" + first["expected_output_schema"]
                                      ["artifact_path"]],
            "error_class": None, "error_detail": None}), encoding="utf-8")
        self.cli(tmp, "complete", "--run-id", run_id, "--phase", phase)
        entries = json.loads((run_dir / "recovery-ledger.json").read_text(
            encoding="utf-8"))["entries"]
        self.assertEqual([(e["state_id"], e["reason_code"]) for e in entries],
                         [(phase, "validation_failed")])
        self.assertEqual(fr.count_tier_rejections(run_dir, {"state_id": phase}),
                         {"validator": 1, "gate_rollback": 0})
        # let the retry backoff elapse, then dispatch from recorded state alone
        state = run_dir / "state.json"
        state.write_text(re.sub(r'"available_at": "[^"]+"', '"available_at": "2000-01-01T00:00:00Z"',
                                state.read_text(encoding="utf-8")), encoding="utf-8")
        done = self.cli(tmp, "dispatch", "--run-id", run_id, "--phase", phase)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        env = json.loads((state_dir / "invocation-envelope.json").read_text(encoding="utf-8"))
        expected = fr.resolve_model_tier(fr.load_model_tier_policy(), "implement-feature",
                                         phase, {"validator": 1, "gate_rollback": 0})
        self.assertEqual(env["model_tier"], expected)
        self.assertEqual(env["model_tier"]["tier"], "standard")
        self.assertEqual(env["model_tier"]["escalation"]["from"], "light")
        prompt = (state_dir / "dispatch-prompt.md").read_text(encoding="utf-8")
        self.assertIn("promoted", prompt)
        self.assertIn("The hint is `inherit`: pass no model override.", prompt)
        self.assertNotIn("Pass the hint as the per-dispatch model override.", prompt)
        data = em.compute(run_dir, tmp / ".claude")
        by_tier = data["model_tiers"]["by_tier"]
        self.assertEqual((by_tier["light"]["invocations"], by_tier["standard"]["invocations"]),
                         (1, 1))
        self.assertEqual(data["model_tiers"]["invocations_total"],
                         data["agents_executed"]["invocations"])

    def test_a_real_rollback_promotes_the_re_entered_phase(self):
        tmp = self.make_tree("Add an ODS export of ledgers for administrators.\n")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        run_id = self.plan(tmp)
        phase, gate = "scope-and-acceptance", "Scope Gate"
        run_dir = tmp / ".claude" / "runs" / run_id
        self.assertEqual(self.cli(tmp, "dispatch", "--run-id", run_id, "--phase",
                                  phase).returncode, 0)
        # commit the phase as the runtime would on acceptance, so the gate has evidence
        script = (
            "import sys; sys.path.insert(0, sys.argv[1]); import state_engine as se; "
            "from pathlib import Path; rd = Path(sys.argv[2]); st = se.StateStore.load(rd); "
            "it = st.item(sys.argv[3]); art = it['artifact_path']; "
            "f = Path(sys.argv[4]) / art; f.parent.mkdir(parents=True, exist_ok=True); "
            "f.write_text('x'); "
            "st.transition(it, se.COMPLETED, reason_code='output_accepted', "
            "actor_type='runtime', actor_id='test', detail='test', "
            "fields={'completion': {'artifact_path': art, 'artifact_digest': 'sha256:aaa'}}); "
            "st.save()")
        done = subprocess.run(
            [sys.executable, "-c", script, str(tmp / ".claude" / "runtime"), str(run_dir),
             phase, str(tmp / ".claude")], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        rejected = self.cli(tmp, "gate", "--run-id", run_id, "--gate", gate, "--decision",
                            "reject", "--owner-role", "omn-business-analyst", "--decided-by",
                            "tester", "--rationale", "needs rework")
        self.assertEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
        rolled = self.cli(tmp, "rollback", "--run-id", run_id, "--gate", gate, "--owner-role",
                          "omn-business-analyst", "--decided-by", "tester")
        self.assertEqual(rolled.returncode, 0, rolled.stdout + rolled.stderr)
        self.assertEqual(self.cli(tmp, "dispatch", "--run-id", run_id, "--phase",
                                  phase).returncode, 0)
        env = json.loads((run_dir / "states" / phase / "invocation-envelope.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(env["model_tier"]["tier"], "standard")
        esc = env["model_tier"]["escalation"]
        self.assertEqual((esc["from"], esc["gate_rollbacks"], esc["validator_rejections"]),
                         ("light", 1, 0))
        self.assertEqual(env["model_tier"], fr.resolve_model_tier(
            fr.load_model_tier_policy(), "implement-feature", phase,
            {"validator": 0, "gate_rollback": 1}))

    def test_an_absent_declaration_inherits_and_changes_no_other_field(self):
        tmp = self.make_tree("Add a JSON export of customers for administrators.\n")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        (tmp / ".claude" / fr.MODEL_TIER_POLICY_REL).unlink()
        run_id = self.plan(tmp)
        done = self.cli(tmp, "dispatch", "--run-id", run_id, "--phase", "scope-and-acceptance")
        self.assertEqual(done.returncode, 0, done.stderr)
        env = json.loads((tmp / ".claude" / "runs" / run_id / "states" /
                          "scope-and-acceptance" / "invocation-envelope.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual((env["model_tier"]["tier"], env["model_tier"]["host_hint"]),
                         ("standard", fr.INHERIT_HINT))
        self.assertEqual(env["agent_id"], "omn-product-owner")

    def test_a_malformed_declaration_fails_the_dispatch_as_a_policy_failure(self):
        tmp = self.make_tree("Add an XML export of products for administrators.\n")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        run_id = self.plan(tmp)
        (tmp / ".claude" / fr.MODEL_TIER_POLICY_REL).write_text("{broken", encoding="utf-8")
        done = self.cli(tmp, "dispatch", "--run-id", run_id, "--phase", "scope-and-acceptance")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("policy", (done.stdout + done.stderr).lower())
        self.assertFalse((tmp / ".claude" / "runs" / run_id / "states" /
                          "scope-and-acceptance" / "invocation-envelope.json").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
