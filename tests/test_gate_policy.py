"""Tests for the gate auto-approval policy (config/gate-policy.json).

Exercises `load_gate_policy`, `evaluate_auto_approval`, `maybe_auto_decide_gates`, and
`record_gate_decision` in `.claude/runtime/framework_runtime.py` against a hermetic
framework tree: a temp CLAUDE root with a minimal agent registry, a prior run providing
(or withholding) precedent, and a synthetic run holding one completed evidence phase and
one decision-eligible gate.

The invariants pinned here:
  * `human-required` (the default, and a missing policy file) changes nothing;
  * `auto-on-clean-evidence` approves only when EVERY condition holds, and records the
    decision exactly like a human one, attributed to `runtime:auto-policy`;
  * severity at/above threshold, a blocking open question, an escalated deviation, an
    open defect on a QA-owned gate, a pinned gate, or a missing precedent each
    individually hold the gate for a human.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402
import state_engine as se       # noqa: E402

PRODUCER = "omn-dev-1-bug-analyst"
PRODUCER_VERSION = "1.0.0"
WORKFLOW = "fix-bug"
WORKFLOW_VERSION = "1.0.0"
PHASE = "triage-and-impact"
GATE = "Triage Gate"

CLEAN_ARTIFACT = """\
# Bug Analysis

```yaml
bugAnalysis:
  status: complete
  severity: low
```

## Metadata

- Severity: low

## Open Questions

| ID | Question | Blocking | Owner | Affected steps |
|---|---|---|---|---|
| Q-001 | Is the log retention policy affected? | no | omn-tech-lead | none |
"""

BLOCKING_QUESTION_ARTIFACT = CLEAN_ARTIFACT.replace(
    "| Q-001 | Is the log retention policy affected? | no |",
    "| Q-001 | Is the log retention policy affected? | yes |")

CRITICAL_ARTIFACT = CLEAN_ARTIFACT.replace("severity: low", "severity: critical") \
                                  .replace("- Severity: low", "- Severity: critical")

ESCALATED_DEVIATION_ARTIFACT = CLEAN_ARTIFACT + """
## Deviations and Tradeoffs

| ID | Deviation | Design element | Rationale | Escalation |
|---|---|---|---|---|
| V-001 | Bypassed the cache layer | caching strategy | latency evidence | ESC-042 |
"""

OPEN_DEFECT_ARTIFACT = CLEAN_ARTIFACT + """
## Defects

| ID | Severity | Category | Location | Symptom | Reproducibility | Status |
|---|---|---|---|---|---|---|
| DF-001 | medium | functional | src/x.py | wrong total | always | open |
"""


class GatePolicyTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-gate-policy-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.claude = self.tmp / "claude"
        self.runs = self.claude / "runs"
        (self.claude / "registry").mkdir(parents=True)
        (self.claude / "config").mkdir()
        (self.claude / "registry" / "agents.yaml").write_text(json.dumps({
            "records": [{"identifier": PRODUCER, "version": PRODUCER_VERSION,
                         "status": "active",
                         "specificationPath": f"agents/{PRODUCER}/manifest.yaml"}],
        }), encoding="utf-8")   # JSON is valid YAML
        self._patch = mock.patch.multiple(fr, CLAUDE=self.claude, RUNS=self.runs)
        self._patch.start()
        self.addCleanup(self._patch.stop)

    # ---- fixtures ------------------------------------------------------------

    def make_precedent(self, *, agent_version=PRODUCER_VERSION,
                       workflow_version=WORKFLOW_VERSION, decision="approved"):
        prior = self.runs / "run-precedent00"
        (prior / "states" / PHASE).mkdir(parents=True, exist_ok=True)
        (prior / "run-ledger.json").write_text(json.dumps({
            "workflow_id": WORKFLOW, "workflow_version": workflow_version,
            "gates": {GATE: {"decision": decision}},
        }), encoding="utf-8")
        (prior / "states" / PHASE / "state-ledger.json").write_text(
            json.dumps({"agent_version": agent_version}), encoding="utf-8")

    def make_run(self, artifact_text=CLEAN_ARTIFACT, *, owner_roles=None,
                 validation_result="pass"):
        run_id = "run-undertest00"
        run_dir = self.runs / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        store = se.StateStore.create(
            run_dir, run_id=run_id, command_id="bugfix", workflow_id=WORKFLOW,
            workflow_version=WORKFLOW_VERSION, runtime_version=fr.RUNTIME_VERSION,
            input_digest="sha256:test", inputs=[])

        artifact_rel = f"runs/{run_id}/states/{PHASE}/artifacts/bug-analysis.md"
        artifact = self.claude / artifact_rel
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(artifact_text, encoding="utf-8")

        state = se.new_work_item(
            run_id=run_id, workflow_id=WORKFLOW, state_id=PHASE, work_type="state",
            owner_agent_id=PRODUCER, phase_index=1, gate=GATE,
            artifact="bug-analysis.md", depends_on=[])
        state["status"] = se.COMPLETED
        state["artifact_path"] = artifact_rel
        state["completion"] = {"artifact_path": artifact_rel, "validation": {
            "result": validation_result, "checksRun": 17, "checksPassed": 17,
            "blockingFailures": 0, "correctableFailures": 0,
            "undeclaredSideEffects": []}}
        store.add_item(state)

        gate_item = se.new_work_item(
            run_id=run_id, workflow_id=WORKFLOW, state_id=GATE, work_type="gate",
            owner_agent_id=None, phase_index=1, gate=GATE, artifact=None,
            depends_on=[{"state_id": PHASE, "kind": "hard",
                         "basis": "the gate closes this phase"}])
        gate_item["status"] = se.BLOCKED
        gate_item["blocked_reason"] = "awaiting_human_decision"
        store.add_item(gate_item)

        store.add_gate({
            "gate": GATE, "closes_state": PHASE,
            "owner_roles": owner_roles or ["omn-dev-2-reviewer", "omn-tech-lead"],
            "producer_agent": PRODUCER, "decision": None, "owner_role": None,
            "decided_by": None, "rationale": None, "evidence_ref": None,
            "decided_at": None,
        })
        store.save()
        return {"store": store, "ledger": fr.RunLedger(run_dir), "run_dir": run_dir}

    def auto_decide(self, ctx, mode="auto-on-clean-evidence"):
        args = mock.Mock(gate_policy=mode)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            decided = fr.maybe_auto_decide_gates(ctx, args)
        return decided, out.getvalue()

    # ---- policy loading ------------------------------------------------------

    def test_missing_policy_file_defaults_to_human_required(self):
        policy = fr.load_gate_policy()
        self.assertEqual(policy["mode"], "human-required")
        self.assertEqual(policy["severityThreshold"], "high")
        self.assertEqual(policy["pinned"], {})

    def test_policy_file_sets_mode_and_cli_override_wins(self):
        (self.claude / fr.GATE_POLICY_REL).write_text(json.dumps(
            {"mode": "auto-on-clean-evidence", "severityThreshold": "medium"}),
            encoding="utf-8")
        policy = fr.load_gate_policy()
        self.assertEqual(policy["mode"], "auto-on-clean-evidence")
        self.assertEqual(policy["severityThreshold"], "medium")
        self.assertEqual(fr.load_gate_policy("human")["mode"], "human-required")

    def test_unknown_mode_is_a_policy_failure(self):
        (self.claude / fr.GATE_POLICY_REL).write_text(
            json.dumps({"mode": "yolo"}), encoding="utf-8")
        with self.assertRaises(fr.RuntimeError_):
            fr.load_gate_policy()
        with self.assertRaises(fr.RuntimeError_):
            fr.load_gate_policy("yolo")

    # ---- default mode: no behavior change ------------------------------------

    def test_human_required_mode_decides_nothing(self):
        self.make_precedent()
        ctx = self.make_run()
        decided, _ = self.auto_decide(ctx, mode="human-required")
        self.assertEqual(decided, [])
        g = ctx["store"].gate(GATE)
        self.assertIsNone(g["decision"])
        self.assertEqual(ctx["store"].item(GATE, "gate")["status"], se.BLOCKED)

    def test_missing_policy_file_and_no_flag_decides_nothing(self):
        self.make_precedent()
        ctx = self.make_run()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            decided = fr.maybe_auto_decide_gates(ctx, None)
        self.assertEqual(decided, [])
        self.assertIsNone(ctx["store"].gate(GATE)["decision"])

    # ---- clean evidence auto-approves ----------------------------------------

    def test_clean_low_severity_gate_auto_approves(self):
        self.make_precedent()
        ctx = self.make_run()
        decided, out = self.auto_decide(ctx)
        self.assertEqual(decided, [GATE], out)

        g = ctx["store"].gate(GATE)
        self.assertEqual(g["decision"], "approved")
        self.assertEqual(g["decided_by"], fr.AUTO_POLICY_DECIDER)
        self.assertEqual(g["owner_role"], "omn-dev-2-reviewer")
        self.assertIn("severity=low", g["rationale"])
        self.assertIn("precedent=found", g["rationale"])
        self.assertEqual(g["auto_policy"]["mode"], "auto-on-clean-evidence")
        self.assertEqual(g["auto_policy"]["severity_threshold"], "high")
        self.assertTrue(g["auto_policy"]["evaluated"])

        item = ctx["store"].item(GATE, "gate")
        self.assertEqual(item["status"], se.COMPLETED)

        events = ctx["ledger"].events()
        resolved = [e for e in events if e["event_type"] == "escalation_resolved"
                    and e["state_id"] == GATE]
        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["actor_type"], "runtime")
        self.assertEqual(resolved[0]["actor_id"], fr.AUTO_POLICY_DECIDER)
        self.assertIn("auto_policy", resolved[0]["details_ref"])

        run_ledger = json.loads(
            (ctx["run_dir"] / "run-ledger.json").read_text(encoding="utf-8"))
        self.assertEqual(run_ledger["gates"][GATE]["decided_by"],
                         fr.AUTO_POLICY_DECIDER)

    def test_auto_decision_never_names_the_producer_role(self):
        self.make_precedent()
        ctx = self.make_run(owner_roles=[PRODUCER, "omn-tech-lead"])
        decided, _ = self.auto_decide(ctx)
        self.assertEqual(decided, [GATE])
        self.assertEqual(ctx["store"].gate(GATE)["owner_role"], "omn-tech-lead")

    def test_only_producer_roles_listed_holds_for_human(self):
        self.make_precedent()
        ctx = self.make_run(owner_roles=[PRODUCER])
        decided, out = self.auto_decide(ctx)
        self.assertEqual(decided, [])
        self.assertIn("held for a human decision", out)

    # ---- each condition individually holds the gate ---------------------------

    def assert_held(self, ctx, needle):
        decided, out = self.auto_decide(ctx)
        self.assertEqual(decided, [], out)
        g = ctx["store"].gate(GATE)
        self.assertIsNone(g["decision"])
        self.assertEqual(ctx["store"].item(GATE, "gate")["status"], se.BLOCKED)
        self.assertIn("held for a human decision", out)
        self.assertIn(needle, out)

    def test_critical_severity_holds_for_human(self):
        self.make_precedent()
        ctx = self.make_run(CRITICAL_ARTIFACT)
        self.assert_held(ctx, "severity 'critical' is not below 'high'")

    def test_high_severity_holds_for_human(self):
        self.make_precedent()
        high = CLEAN_ARTIFACT.replace("severity: low", "severity: high") \
                             .replace("- Severity: low", "- Severity: high")
        ctx = self.make_run(high)
        self.assert_held(ctx, "severity 'high' is not below 'high'")

    def test_blocking_open_question_holds_for_human(self):
        self.make_precedent()
        ctx = self.make_run(BLOCKING_QUESTION_ARTIFACT)
        self.assert_held(ctx, "open question(s) marked blocking")

    def test_escalated_deviation_holds_for_human(self):
        self.make_precedent()
        ctx = self.make_run(ESCALATED_DEVIATION_ARTIFACT)
        self.assert_held(ctx, "deviation(s) escalated")

    def test_open_defect_holds_qa_owned_gate(self):
        self.make_precedent()
        ctx = self.make_run(OPEN_DEFECT_ARTIFACT,
                            owner_roles=["omn-qa", "omn-tech-lead"])
        self.assert_held(ctx, "unresolved defect(s)")

    def test_open_defect_ignored_on_non_qa_gate(self):
        # The unresolved-defect condition is specific to QA-owned gates.
        self.make_precedent()
        ctx = self.make_run(OPEN_DEFECT_ARTIFACT)
        decided, _ = self.auto_decide(ctx)
        self.assertEqual(decided, [GATE])

    def test_pinned_gate_holds_for_human(self):
        self.make_precedent()
        (self.claude / fr.GATE_POLICY_REL).write_text(json.dumps({
            "mode": "auto-on-clean-evidence",
            "pinned": {WORKFLOW: {GATE: "human-required"}},
        }), encoding="utf-8")
        ctx = self.make_run()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            decided = fr.maybe_auto_decide_gates(ctx, None)
        self.assertEqual(decided, [])
        self.assertIn("pinned=human-required", out.getvalue())

    def test_no_precedent_holds_for_human(self):
        ctx = self.make_run()   # no make_precedent()
        self.assert_held(ctx, "no approved precedent")

    def test_precedent_under_other_agent_version_does_not_count(self):
        self.make_precedent(agent_version="0.9.0")
        ctx = self.make_run()
        self.assert_held(ctx, "no approved precedent")

    def test_precedent_under_other_workflow_version_does_not_count(self):
        self.make_precedent(workflow_version="0.9.0")
        ctx = self.make_run()
        self.assert_held(ctx, "no approved precedent")

    def test_rejected_prior_decision_is_not_precedent(self):
        self.make_precedent(decision="rejected")
        ctx = self.make_run()
        self.assert_held(ctx, "no approved precedent")

    def test_unclean_validation_holds_for_human(self):
        self.make_precedent()
        ctx = self.make_run(validation_result="fail")
        self.assert_held(ctx, "upstream validation is not clean")

    # ---- artifact evidence parsing --------------------------------------------

    def test_artifact_without_severity_is_unaffected_by_threshold(self):
        self.assertIsNone(fr._artifact_severity("# Design\n\nNo severity here.\n"))

    def test_severity_parsed_from_yaml_block_and_bullet(self):
        self.assertEqual(fr._artifact_severity("  severity: Medium\n"), "medium")
        self.assertEqual(fr._artifact_severity("- Severity: critical\n"), "critical")

    # ---- final report ----------------------------------------------------------

    def test_final_report_names_agents_deciders_and_times(self):
        self.make_precedent()
        ctx = self.make_run()
        self.auto_decide(ctx)
        report = fr.build_final_report(ctx)
        # Agent activity: the phase row names its agent and validation outcome.
        self.assertIn("## Agent Activity", report)
        self.assertIn(f"`{PHASE}` | `{PRODUCER}`", report)
        self.assertIn("pass (17/17)", report)
        # Gate decisions: the auto decision is attributed to the policy, with its time.
        self.assertIn("## Gate Decisions", report)
        self.assertIn(f"{fr.AUTO_POLICY_DECIDER} (policy)", report)
        g = ctx["store"].gate(GATE)
        self.assertIn(g["decided_at"], report)
        # Timeline: the ledger's escalation_resolved row appears with its actor.
        self.assertIn("## Timeline", report)
        self.assertIn(f"runtime:{fr.AUTO_POLICY_DECIDER}", report)
        self.assertIn("`escalation_resolved`", report)

    def test_final_report_marks_undecided_gate(self):
        ctx = self.make_run()   # no precedent -> gate stays undecided
        self.auto_decide(ctx)
        report = fr.build_final_report(ctx)
        self.assertIn("| undecided | - |", report)
        self.assertNotIn("(policy)", report)

    def test_duration_formatting(self):
        self.assertEqual(fr._fmt_duration("2026-08-19T08:00:00Z",
                                          "2026-08-19T09:07:28Z"), "1h 7m 28s")
        self.assertEqual(fr._fmt_duration("2026-08-19T08:00:00Z",
                                          "2026-08-19T08:00:15Z"), "15s")
        self.assertEqual(fr._fmt_duration(None, "2026-08-19T08:00:15Z"), "-")
        self.assertEqual(fr._fmt_duration("2026-08-19T08:00:15Z", "not-a-time"), "-")

    def test_shared_recorder_keeps_human_shape(self):
        # A human decision through record_gate_decision writes the same record
        # fields cmd_gate always wrote, with no auto_policy block.
        self.make_precedent()
        ctx = self.make_run()
        store = ctx["store"]
        item = store.item(GATE, "gate")
        g = store.gate(GATE)
        fr.record_gate_decision(
            ctx, item, g, approved=True, owner_role="omn-tech-lead",
            decided_by="dev@example.com", rationale="evidence reviewed",
            evidence_ref="runs/run-undertest00/states/triage-and-impact",
            actor_type="human")
        self.assertEqual(g["decision"], "approved")
        self.assertEqual(g["decided_by"], "dev@example.com")
        self.assertNotIn("auto_policy", g)
        events = ctx["ledger"].events()
        self.assertEqual(events[-1]["actor_type"], "human")
        self.assertNotIn("auto_policy", events[-1]["details_ref"])


if __name__ == "__main__":
    unittest.main()
