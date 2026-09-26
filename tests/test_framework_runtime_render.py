"""Tests for the colorized tree / icon / JSON status rendering added to
`framework_runtime.py`.

`framework_runtime.py` is not part of the `omn_agent` package: it's the framework's own
runtime, whose authoritative source lives at `.claude/runtime/` next to this repo's
`omn_agent/` package (see `omn_agent/source.py`) and which gets installed into a target
repo as `.omn-agent/runtime/framework_runtime.py` and driven by `omn_agent.runner`.
These tests import it directly to exercise the renderer against a real
`state_engine.StateStore`, independent of the CLI wrapper (covered separately in
`tests/test_run_show.py`).
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

RUNTIME_DIR = Path(__file__).resolve().parent.parent / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import framework_runtime as fr  # noqa: E402
import state_engine as se  # noqa: E402


class _FakeStream:
    """Stand-in for sys.stdout: a real TextIOWrapper resists attribute patching."""

    def __init__(self, *, isatty=False, encoding="utf-8"):
        self._isatty = isatty
        self.encoding = encoding

    def isatty(self):
        return self._isatty

    def write(self, _s):
        pass

    def flush(self):
        pass


def _status_args(run_id, *, json=False, no_color=False, color=False, compact=False):
    return argparse.Namespace(run_id=run_id, json=json, no_color=no_color, color=color,
                              compact=compact)


class RenderingHelpersTestCase(unittest.TestCase):
    """Unit tests for the small helpers, no state store required."""

    def test_icon_set_picks_unicode_when_stdout_supports_it(self):
        with mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(encoding="utf-8"))):
            icons, arrow = fr._icon_set()
        self.assertEqual(icons, fr.STATUS_ICON)
        self.assertEqual(arrow, fr._GATE_ARROW)

    def test_icon_set_falls_back_to_ascii_on_legacy_codepage(self):
        with mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(encoding="cp1252"))):
            icons, arrow = fr._icon_set()
        self.assertEqual(icons, fr.ASCII_STATUS_ICON)
        self.assertEqual(arrow, fr._GATE_ARROW_ASCII)
        for icon in icons.values():
            icon.encode("cp1252")  # would raise if still non-ASCII

    def test_use_color_defaults_to_the_real_tty_check(self):
        args = _status_args("r")
        with mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(isatty=True))):
            self.assertTrue(fr._use_color(args))
        with mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(isatty=False))):
            self.assertFalse(fr._use_color(args))

    def test_color_flag_forces_it_on_even_off_a_tty(self):
        args = _status_args("r", color=True)
        with mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(isatty=False))):
            self.assertTrue(fr._use_color(args))

    def test_no_color_flag_forces_it_off_even_on_a_tty(self):
        args = _status_args("r", no_color=True)
        with mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(isatty=True))):
            self.assertFalse(fr._use_color(args))

    def test_no_color_env_var_wins_over_tty(self):
        args = _status_args("r")
        with mock.patch.dict(os.environ, {"NO_COLOR": "1"}), \
             mock.patch.object(fr, "sys", mock.Mock(stdout=_FakeStream(isatty=True))):
            self.assertFalse(fr._use_color(args))


class _StoreFixture(unittest.TestCase):
    """Builds a small, realistic StateStore: one phase per status this renderer
    distinguishes, so every icon/color/reason-text branch is exercised."""

    RUN_ID = "run-rendertest01"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fr-render-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = self.tmp / self.RUN_ID
        self.store = se.StateStore.create(
            self.run_dir, run_id=self.RUN_ID, command_id="implement",
            workflow_id="implement-feature", workflow_version="1.0.0",
            runtime_version="0.5.0", input_digest="sha256:aaa", inputs=[])

        self._add_state(1, "scope-and-acceptance", "omn-product-owner",
                        status=se.COMPLETED, gate="Scope Gate",
                        gate_decision={"decision": "approve",
                                      "owner_role": "omn-tech-lead"})
        self._add_state(2, "execution-planning", "planner", status=se.RUNNING)
        self._add_state(3, "solution-design-and-risk-assessment", "architect",
                        status=se.BLOCKED,
                        extra={"blocked_reason": "awaiting_capability"})
        self._add_state(4, "implementation", "omn-dev-1-implement", status=se.RETRYING,
                        extra={"failure_class": "tool_failure", "attempt": 1,
                               "max_attempts": 3,
                               "available_at": "2026-08-20T12:00:00Z"})
        self._add_state(5, "quality-review", "omn-dev-2-reviewer", status=se.COMPLETED,
                        gate="Review Gate")  # gate_decision=None -> blocked, undecided
        self.store.save()

    def _add_state(self, phase_index, state_id, owner, *, status, extra=None,
                   gate=None, gate_decision=None):
        item = se.new_work_item(
            run_id=self.RUN_ID, workflow_id="implement-feature", state_id=state_id,
            work_type="state", owner_agent_id=owner, phase_index=phase_index,
            gate=gate, artifact=None, depends_on=[])
        item["status"] = status
        item["eligible"] = True
        item["guards"] = []
        if extra:
            item.update(extra)
        self.store.add_item(item)
        if gate:
            gate_item = se.new_work_item(
                run_id=self.RUN_ID, workflow_id="implement-feature", state_id=gate,
                work_type="gate", owner_agent_id=None, phase_index=phase_index,
                gate=None, artifact=None, depends_on=[])
            gate_item["status"] = se.COMPLETED if gate_decision else se.BLOCKED
            if not gate_decision:
                gate_item["blocked_reason"] = "awaiting_human_decision"
            self.store.add_item(gate_item)
            self.store.add_gate({
                "gate": gate, "closes_state": state_id,
                "owner_roles": ["omn-tech-lead"], "producer_agent": owner,
                **(gate_decision or {}),
            })


class RenderTreeTestCase(_StoreFixture):
    def test_every_phase_and_its_gate_appear_nested(self):
        lines = fr.render_tree(self.store, color=False)
        text = "\n".join(lines)
        self.assertIn("Phase 1", text)
        self.assertIn("scope-and-acceptance", text)
        gate_line = next(l for l in lines if "Scope Gate" in l)
        self.assertTrue(gate_line.startswith("      "), gate_line)  # nested deeper

    def test_status_icons_cover_completed_running_blocked_retrying(self):
        text = "\n".join(fr.render_tree(self.store, color=False))
        icons, _ = fr._icon_set()
        self.assertIn(icons[se.COMPLETED], text)
        self.assertIn(icons[se.RUNNING], text)
        self.assertIn(icons[se.BLOCKED], text)
        self.assertIn(icons[se.RETRYING], text)

    def test_color_true_adds_ansi_escapes(self):
        plain = "\n".join(fr.render_tree(self.store, color=False))
        colored = "\n".join(fr.render_tree(self.store, color=True))
        self.assertNotIn("\x1b[", plain)
        self.assertIn("\x1b[", colored)

    def test_blocked_and_retrying_reasons_are_explained(self):
        text = "\n".join(fr.render_tree(self.store, color=False))
        self.assertIn("awaiting_capability", text)
        self.assertIn("tool_failure", text)
        self.assertIn("attempt 2 of 3", text)

    def test_undecided_gate_shows_blocked_reason_and_pending_owners(self):
        lines = fr.render_tree(self.store, color=False)
        gate_line = next(l for l in lines if "Review Gate" in l)
        self.assertIn("awaiting_human_decision", gate_line)
        self.assertIn("omn-tech-lead", gate_line)


class EdgeCaseTestCase(unittest.TestCase):
    """Two cases the fixed mixed-status fixture above doesn't reach: an all-completed
    run (zero blocked/retrying items) and a gate blocked with no owner_roles at all."""

    RUN_ID = "run-rendertest02"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fr-render-edge-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.run_dir = self.tmp / self.RUN_ID
        self.store = se.StateStore.create(
            self.run_dir, run_id=self.RUN_ID, command_id="implement",
            workflow_id="implement-feature", workflow_version="1.0.0",
            runtime_version="0.5.0", input_digest="sha256:bbb", inputs=[])

    def test_all_completed_run_renders_and_serializes_cleanly(self):
        for idx, (state_id, owner) in enumerate(
                [("scope-and-acceptance", "omn-product-owner"),
                 ("execution-planning", "planner")], start=1):
            item = se.new_work_item(
                run_id=self.RUN_ID, workflow_id="implement-feature", state_id=state_id,
                work_type="state", owner_agent_id=owner, phase_index=idx, gate=None,
                artifact=None, depends_on=[])
            item["status"] = se.COMPLETED
            item["eligible"] = True
            item["guards"] = []
            self.store.add_item(item)
        self.store.save()

        text = "\n".join(fr.render_tree(self.store, color=False))
        self.assertIn("scope-and-acceptance", text)
        self.assertIn("execution-planning", text)

        payload = fr.state_json(self.store)
        self.assertEqual(len(payload["phases"]), 2)
        self.assertTrue(all(s["status"] == se.COMPLETED
                            for p in payload["phases"] for s in p["steps"]))
        json.dumps(payload)  # must not raise

    def test_blocked_gate_with_no_owner_roles_shows_only_blocked_reason(self):
        item = se.new_work_item(
            run_id=self.RUN_ID, workflow_id="implement-feature",
            state_id="scope-and-acceptance", work_type="state",
            owner_agent_id="omn-product-owner", phase_index=1, gate="Scope Gate",
            artifact=None, depends_on=[])
        item["status"] = se.COMPLETED
        item["eligible"] = True
        item["guards"] = []
        self.store.add_item(item)

        gate_item = se.new_work_item(
            run_id=self.RUN_ID, workflow_id="implement-feature", state_id="Scope Gate",
            work_type="gate", owner_agent_id=None, phase_index=1, gate=None,
            artifact=None, depends_on=[])
        gate_item["status"] = se.BLOCKED
        gate_item["blocked_reason"] = "awaiting_human_decision"
        self.store.add_item(gate_item)
        self.store.add_gate({"gate": "Scope Gate", "closes_state": "scope-and-acceptance",
                             "owner_roles": [], "producer_agent": "omn-product-owner"})
        self.store.save()

        lines = fr.render_tree(self.store, color=False)
        gate_line = next(l for l in lines if "Scope Gate" in l)
        self.assertIn("awaiting_human_decision", gate_line)
        self.assertNotIn("()", gate_line)  # no dangling empty parens when reason is bare

        payload = fr.state_json(self.store)
        gate_entry = payload["phases"][0]["gates"][0]
        self.assertEqual(gate_entry["owner_roles"], [])
        json.dumps(payload)  # must not raise


class ReArmedGateAndSupersededStepTestCase(unittest.TestCase):
    """A phase re-entered by an authorised rollback and the gate it re-armed render in
    every view: the plain table and the tree name both, and the JSON view carries the
    `rollback` block on the step and the `decision_history` on the gate."""

    RUN_ID = "run-rendertest02"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="fr-render-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = se.StateStore.create(
            self.tmp / self.RUN_ID, run_id=self.RUN_ID, command_id="implement",
            workflow_id="implement-feature", workflow_version="1.0.0",
            runtime_version="0.5.0", input_digest="sha256:bbb", inputs=[])
        step = se.new_work_item(
            run_id=self.RUN_ID, workflow_id="implement-feature", state_id="implementation",
            work_type="state", owner_agent_id="omn-dev-1-implement", phase_index=4,
            gate=None, artifact=None, depends_on=[])
        step.update({"status": se.PENDING, "eligible": True, "queue_status": "Ready",
                     "attempt": 1,
                     "supersessions": [{"authorisation_id": "RB-run-rendertest02-review-gate-01",
                                        "gate": "Review Gate", "attempt": 1,
                                        "completion": {"artifact_path": "x",
                                                       "artifact_digest": "sha256:1"}}]})
        self.store.add_item(step)
        gate_item = se.new_work_item(
            run_id=self.RUN_ID, workflow_id="implement-feature", state_id="Review Gate",
            work_type="gate", owner_agent_id=None, phase_index=5, gate=None, artifact=None,
            depends_on=[])
        self.store.add_item(gate_item)   # pending, re-armed
        self.store.add_gate({
            "gate": "Review Gate", "closes_state": "quality-review",
            "owner_roles": ["omn-dev-2-reviewer", "omn-qa"],
            "producer_agent": "omn-dev-2-reviewer", "decision": None, "owner_role": None,
            "decided_by": None, "rationale": None, "evidence_ref": None, "decided_at": None,
            "decision_history": [{"decision": "rejected", "owner_role": "omn-qa",
                                  "decided_by": "qa", "decided_at": "2026-09-06T09:05:36Z",
                                  "superseded_by": "RB-run-rendertest02-review-gate-01"}],
        })
        self.store.save()

    def test_table_and_tree_name_the_supersession_and_the_re_arm(self):
        for lines in (fr.state_table(self.store), fr.render_tree(self.store, color=False)):
            step_line = next(l for l in lines if "implementation" in l)
            self.assertIn("attempt 1 superseded under RB-run-rendertest02-review-gate-01",
                          step_line)
            # the step line now also names the gate in its supersession suffix, so the
            # gate's own row is the one without it
            gate_line = next(l for l in lines if "Review Gate" in l and "superseded" not in l)
            self.assertIn("omn-dev-2-reviewer, omn-qa", gate_line)
            self.assertIn("re-armed after rejected by omn-qa", gate_line)

    def test_json_carries_rollback_block_and_decision_history(self):
        payload = fr.state_json(self.store)
        step = next(s for ph in payload["phases"] for s in ph["steps"])
        gate = next(g for ph in payload["phases"] for g in ph["gates"])
        self.assertEqual(step["rollback"], {
            "gate": "Review Gate",
            "authorisation_id": "RB-run-rendertest02-review-gate-01",
            "superseded_attempt": 1})
        self.assertEqual((step["status"], step["eligible"], step["attempt"]),
                         ("pending", True, 1))
        self.assertEqual((gate["status"], gate["decision"]), ("pending", None))
        self.assertEqual(gate["decision_history"], [{
            "decision": "rejected", "owner_role": "omn-qa", "decided_by": "qa",
            "decided_at": "2026-09-06T09:05:36Z",
            "superseded_by": "RB-run-rendertest02-review-gate-01"}])
        json.dumps(payload)

    def test_steps_without_supersessions_carry_no_rollback_key(self):
        plain = se.new_work_item(
            run_id=self.RUN_ID, workflow_id="implement-feature", state_id="scope",
            work_type="state", owner_agent_id="omn-product-owner", phase_index=1,
            gate=None, artifact=None, depends_on=[])
        self.store.add_item(plain)
        payload = fr.state_json(self.store)
        scope = next(s for ph in payload["phases"] for s in ph["steps"]
                     if s["state_id"] == "scope")
        self.assertNotIn("rollback", scope)
        gate = next(g for ph in payload["phases"] for g in ph["gates"])
        self.assertIn("decision_history", gate)


class StateJsonTestCase(_StoreFixture):
    def test_schema_and_shape(self):
        payload = fr.state_json(self.store)
        self.assertEqual(payload["schema"], "framework.runtime/status-view.v1")
        self.assertEqual(payload["run_id"], self.RUN_ID)
        self.assertEqual(len(payload["phases"]), 5)
        phase1 = next(p for p in payload["phases"] if p["phase_index"] == 1)
        self.assertEqual(phase1["steps"][0]["state_id"], "scope-and-acceptance")
        self.assertEqual(phase1["gates"][0]["state_id"], "Scope Gate")
        self.assertEqual(phase1["gates"][0]["decision"], "approve")
        self.assertIn("summary", payload)

    def test_is_json_serializable(self):
        json.dumps(fr.state_json(self.store))  # must not raise


class CmdStatusTestCase(_StoreFixture):
    def _run(self, **arg_kwargs):
        args = _status_args(self.RUN_ID, **arg_kwargs)
        buf = io.StringIO()
        with mock.patch.object(fr, "RUNS", self.tmp), \
             contextlib.redirect_stdout(buf):
            rc = fr.cmd_status(args)
        return rc, buf.getvalue()

    def test_default_matches_original_plain_table_and_keeps_full_sections(self):
        rc, out = self._run(no_color=True)  # no_color=True == today's default off a TTY
        self.assertEqual(rc, 0)
        self.assertIn("work item", out)  # plain table header, unchanged
        self.assertIn("State transitions (ordered)", out)
        self.assertIn(f'"run_id": "{self.RUN_ID}"', out)  # trailing json summary
        self.assertNotIn("Phase 1", out)  # tree header must not leak into plain mode

    def test_compact_color_shows_tree_and_stops_before_transitions(self):
        rc, out = self._run(color=True, compact=True)
        self.assertEqual(rc, 0)
        self.assertIn("Phase 1", out)
        self.assertNotIn("State transitions (ordered)", out)

    def test_json_flag_prints_only_the_json_projection(self):
        rc, out = self._run(json=True)
        self.assertEqual(rc, 0)
        payload = json.loads(out)
        self.assertEqual(payload["schema"], "framework.runtime/status-view.v1")
        self.assertNotIn("State transitions", out)


if __name__ == "__main__":
    unittest.main()
