"""Unit tests for the authorised rollback past a rejected gate.

`verify_recovery.py` Run D proves the whole path on the real command line. These tests pin
the pieces that path is built from, hermetically, so a regression names the piece:

  * the state engine admits exactly two exits from a terminal status -- `completed ->
    pending` (`superseded`) for a state work item and `failed -> pending`
    (`rollback_authorised`) for a gate -- and refuses `superseded` without a supersession
    record, moving the prior completion into `supersessions` when it is supplied;
  * the dispatch write scope accepts the attempt-scoped artifact path an envelope declares
    while the idempotency payload keeps the canonical path, so the key survives a re-entry;
  * the clearing action is class-aware: a gate rejection names the `rollback` command with
    the gate, on the gate's own envelope and on a G4-blocked successor's, and states the
    refusal rather than a command once the target's budget is spent; the authoriser is never
    defaulted from the rejection -- `--decided-by` stays a placeholder;
  * the scheduler returns a guard-raised block to `pending` when its guards fall to a wait,
    for state and gate work items alike, resolving the envelope;
  * `rollback_range` is the target's completed downstream cone -- every completed phase that
    transitively hard-depends on it, the closed phase included, and a completed dependent off
    the closed phase's ancestor chain (fix-bug's `root-cause-analysis`) too -- and refuses a
    target that is not a hard ancestor;
  * `rollback_preconditions` refuses, writing nothing, when an approved gate stands over any
    phase in range, the closed phase included (an approved sibling gate);
  * while a gate stands rejected, `next` names the rollback first and withholds every
    undecided gate on the same phase, and `recovery` derives an open gate-rejection
    envelope's clearing action live while leaving the envelope as written.
"""

from __future__ import annotations

import argparse
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
import recovery_policy as rp    # noqa: E402
import state_engine as se       # noqa: E402

RUN_ID = "run-rollbacktest"
COMMON = dict(actor_type="runtime", actor_id="test", detail="test")


def _store(tmp: Path) -> se.StateStore:
    return se.StateStore.create(
        tmp / RUN_ID, run_id=RUN_ID, command_id="implement", workflow_id="implement-feature",
        workflow_version="1.0.0", runtime_version=fr.RUNTIME_VERSION,
        input_digest="sha256:test", inputs=[])


def _state(store, state_id, phase_index, depends_on=(), owner="planner"):
    return store.add_item(se.new_work_item(
        run_id=RUN_ID, workflow_id="implement-feature", state_id=state_id, work_type="state",
        owner_agent_id=owner, phase_index=phase_index, gate=None, artifact="x.md",
        depends_on=[{"state_id": d, "kind": "hard", "basis": "test"} for d in depends_on]))


def _gate(store, name, phase_index, closes, owners=("omn-tech-lead",), producer="planner"):
    item = store.add_item(se.new_work_item(
        run_id=RUN_ID, workflow_id="implement-feature", state_id=name, work_type="gate",
        owner_agent_id=None, phase_index=phase_index, gate=name, artifact=None,
        depends_on=[{"state_id": closes, "kind": "hard", "basis": "the gate closes this phase"}]))
    store.add_gate({"gate": name, "closes_state": closes, "owner_roles": list(owners),
                    "producer_agent": producer, "decision": None, "owner_role": None,
                    "decided_by": None, "rationale": None, "evidence_ref": None,
                    "decided_at": None, "decision_history": []})
    return item


def _complete(store, item, artifact_path="runs/x/a.md", digest="sha256:aaa"):
    store.transition(item, se.LEASED, reason_code="leased", **COMMON)
    store.transition(item, se.RUNNING, reason_code="execution_started", **COMMON)
    store.transition(item, se.COMPLETED, reason_code="output_accepted",
                     fields={"completion": {"artifact_path": artifact_path,
                                            "artifact_digest": digest},
                             "artifact_path": artifact_path},
                     **COMMON)


class StateEngineTerminalityTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)

    def test_exactly_two_authorised_exits_are_declared(self):
        self.assertEqual(se.AUTHORISED_EXITS, {
            "state": {(se.COMPLETED, se.PENDING): "superseded"},
            "gate": {(se.FAILED, se.PENDING): "rollback_authorised"}})
        for work_type, table in se.TRANSITIONS.items():
            leaving = {k: v for k, v in table.items() if k[0] in se.TERMINAL_STATUSES}
            self.assertEqual(leaving, se.AUTHORISED_EXITS[work_type], work_type)

    def test_superseded_requires_a_record_and_moves_the_completion(self):
        item = _state(self.store, "p", 1)
        _complete(self.store, item)
        with self.assertRaises(se.TransitionError):
            self.store.transition(item, se.PENDING, reason_code="enqueued", **COMMON)
        with self.assertRaises(se.TransitionError):
            self.store.transition(item, se.PENDING, reason_code="enqueued",
                                  fields={"supersession": {"gate": "G"}}, **COMMON)
        self.assertEqual(item["status"], se.COMPLETED)
        self.assertEqual(item["supersessions"], [])

        rec = self.store.transition(
            item, se.PENDING, reason_code="enqueued",
            fields={"supersession": {"authorisation_id": "RB-1", "gate": "G"}}, **COMMON)
        self.assertEqual(rec["trigger"], "superseded")
        self.assertEqual(item["status"], se.PENDING)
        self.assertIsNone(item["completion"])
        self.assertFalse(item["eligible"])
        self.assertEqual(len(item["supersessions"]), 1)
        sup = item["supersessions"][0]
        self.assertEqual(sup["authorisation_id"], "RB-1")
        self.assertEqual(sup["attempt"], 0)
        self.assertEqual(sup["completion"],
                         {"artifact_path": "runs/x/a.md", "artifact_digest": "sha256:aaa"})
        self.assertNotIn("supersession", item)

    def test_a_record_on_any_other_pair_is_refused(self):
        item = _state(self.store, "p", 1)
        with self.assertRaises(se.TransitionError):
            self.store.transition(item, se.LEASED, reason_code="leased",
                                  fields={"supersession": {"authorisation_id": "RB-1"}},
                                  **COMMON)

    def test_every_other_exit_from_completed_and_failed_is_refused(self):
        done = _state(self.store, "done", 1)
        _complete(self.store, done)
        dead = _state(self.store, "dead", 2)
        self.store.transition(dead, se.LEASED, reason_code="leased", **COMMON)
        self.store.transition(dead, se.RETRYING, reason_code="tool_failure", **COMMON)
        self.store.transition(dead, se.FAILED, reason_code="terminal_failure", **COMMON)
        g_failed = _gate(self.store, "GF", 1, "done")
        self.store.transition(g_failed, se.FAILED, reason_code="validation_failed", **COMMON)
        g_done = _gate(self.store, "GC", 2, "dead")
        self.store.transition(g_done, se.COMPLETED, reason_code="output_accepted", **COMMON)

        allowed = []
        for item in (done, dead, g_failed, g_done):
            frm = item["status"]
            for to in se.STATUSES:
                before = json.dumps(item, sort_keys=True)
                fields = ({"supersession": {"authorisation_id": "RB-1"}}
                          if (item["work_type"], frm, to) == ("state", se.COMPLETED, se.PENDING)
                          else None)
                try:
                    self.store.transition(item, to, reason_code="enqueued", fields=fields,
                                          **COMMON)
                    allowed.append((item["work_type"], frm, to))
                    item.update(json.loads(before))
                except se.TransitionError:
                    pass
        self.assertEqual(sorted(allowed), [("gate", se.FAILED, se.PENDING),
                                           ("state", se.COMPLETED, se.PENDING)])

    def test_rebinding_the_same_payload_after_supersession_keeps_the_key(self):
        item = _state(self.store, "p", 1)
        key = self.store.bind_payload(item, owner_agent_id="planner", agent_version="1.0.0",
                                      payload_digest="sha256:one")
        _complete(self.store, item)
        self.store.transition(item, se.PENDING, reason_code="enqueued",
                              fields={"supersession": {"authorisation_id": "RB-1"}}, **COMMON)
        again = self.store.bind_payload(item, owner_agent_id="planner", agent_version="1.0.0",
                                        payload_digest="sha256:one")
        self.assertEqual(again, key)


class WriteScopeTestCase(unittest.TestCase):
    """Q-006: the declared path is attempt-scoped, the payload path is canonical."""

    def envelope(self, artifact_rel):
        return {"expected_output_schema": {"artifact_path": artifact_rel,
                                           "result_envelope_path": "runs/r/states/p/result-envelope.json",
                                           "conditional_artifacts": []},
                "constraints": {"permitted_writes": [artifact_rel,
                                                     "runs/r/states/p/result-envelope.json"],
                                "write_exclusions": ["runs/**"]}}

    def test_attempt_scoped_artifact_path_is_a_permitted_write(self):
        env = self.envelope("runs/r/states/p/artifacts/attempt-2/execution-plan.md")
        self.assertTrue(fr.permitted_write(
            "runs/r/states/p/artifacts/attempt-2/execution-plan.md", env))
        # the canonical path is not declared by this attempt, so writing it is refused:
        # attempt 1's artifact is immutable
        self.assertFalse(fr.permitted_write("runs/r/states/p/artifacts/execution-plan.md", env))

    def test_canonical_path_fixes_the_key_regardless_of_the_attempt_directory(self):
        canonical = "runs/r/states/p/artifacts/execution-plan.md"
        k1 = se.idempotency_key("r", "p", "planner", "1.0.0",
                                se.digest("ctx", "in", "1.0.0", canonical))
        k2 = se.idempotency_key("r", "p", "planner", "1.0.0",
                                se.digest("ctx", "in", "1.0.0", canonical))
        self.assertEqual(k1, k2)
        self.assertNotEqual(k1, se.idempotency_key(
            "r", "p", "planner", "1.0.0",
            se.digest("ctx", "in", "1.0.0",
                      "runs/r/states/p/artifacts/attempt-2/execution-plan.md")))


class ClearingActionTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)
        self.phase = _state(self.store, "execution-planning", 1)
        _complete(self.store, self.phase)
        self.gate = _gate(self.store, "Planning Gate", 1, "execution-planning",
                          owners=("planner", "omn-tech-lead"))
        g = self.store.gate("Planning Gate")
        g.update({"decision": "rejected", "owner_role": "omn-tech-lead",
                  "decided_by": "Vu Cao", "rationale": "no"})
        self.ctx = {"store": self.store, "run_dir": self.tmp / RUN_ID,
                    "ledger": fr.RunLedger(self.tmp / RUN_ID)}
        self.cls = rp.classify("gate-rejection", attempt=1, attempts_lost=0, max_attempts=3)

    def test_gate_rejection_on_the_gate_names_rollback_with_the_gate(self):
        action = fr.clearing_action(RUN_ID, self.gate, self.cls, "awaiting_recovery_task",
                                    ctx=self.ctx)
        self.assertIn("framework_runtime.py rollback", action)
        self.assertIn('--gate "Planning Gate"', action)
        self.assertIn("--target execution-planning", action)
        self.assertIn("--owner-role omn-tech-lead", action)
        # the authoriser is a second human decision: never defaulted from who rejected
        self.assertIn("--decided-by <who>", action)
        self.assertNotIn("Vu Cao", action)
        self.assertNotIn("release", action)
        placeholders = [w for w in action.split() if w.startswith("<")]
        self.assertEqual(placeholders, ["<who>"])

    def test_gate_rejection_on_a_blocked_successor_names_the_same_command(self):
        successor = _state(self.store, "design", 2, depends_on=("execution-planning",))
        action = fr.clearing_action(RUN_ID, successor, self.cls, "awaiting_recovery_task",
                                    ctx=self.ctx, gate="Planning Gate", guard="G4-GATE")
        self.assertIn("rollback", action)
        self.assertIn('--gate "Planning Gate"', action)
        self.assertNotIn("release", action)

    def test_exhausted_target_states_the_refusal_instead_of_a_command(self):
        self.phase["attempt"] = 3
        action = fr.clearing_action(RUN_ID, self.gate, self.cls, "awaiting_recovery_task",
                                    ctx=self.ctx)
        self.assertNotIn("framework_runtime.py", action)
        self.assertIn("no further attempt", action)
        self.assertIn("repeated gate failure", action)

    def test_g3_dead_predecessor_block_names_no_release(self):
        cls = rp.classify("dependency-failure", attempt=0, attempts_lost=0, max_attempts=3)
        action = fr.clearing_action(RUN_ID, self.phase, cls, "awaiting_recovery_task",
                                    ctx=self.ctx, guard="G3-PREDECESSOR")
        self.assertNotIn("framework_runtime.py", action)
        self.assertIn("guard-raised", action)

    def test_other_recovery_task_blocks_still_name_release(self):
        cls = rp.classify("output-schema-failure", attempt=1, attempts_lost=0, max_attempts=3)
        # a Recovery-Controller block over a rejected artifact with budget left is retried,
        # so force the non-retry branch by using a non-retryable class
        cls = rp.classify("aggregation-conflict", attempt=1, attempts_lost=0, max_attempts=3)
        action = fr.clearing_action(RUN_ID, self.phase, cls, "awaiting_recovery_task",
                                    ctx=self.ctx)
        self.assertIn("release", action)

    def test_gate_rejection_options_offer_no_exception(self):
        self.assertFalse(any("exception" in o for o in rp.CLASS_OPTIONS["gate-rejection"]))
        self.assertTrue(any("rollback" in o for o in rp.CLASS_OPTIONS["gate-rejection"]))

    def test_g4_rejection_verdict_carries_the_gate_as_a_field(self):
        v = fr.verdict("G4-GATE", "t", "block", "policy_block", "d", "awaiting_recovery_task",
                       "gate-rejection", gate="Planning Gate")
        self.assertEqual(v["gate"], "Planning Gate")
        self.assertIsNone(fr.verdict("G1-CAPABILITY", "t", "pass", "enqueued", "d")["gate"])


class RefreshWaitCorrectionTestCase(unittest.TestCase):
    """Q-007: a guard-raised block whose guards fall to `wait` returns to pending, for
    both work types, and its envelope is resolved."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)
        self.run_dir = self.tmp / RUN_ID
        self.ctx = {"store": self.store, "run_dir": self.run_dir,
                    "ledger": fr.RunLedger(self.run_dir), "rows": [], "deps": {},
                    "command": {"identifier": "implement"}, "supplied": []}

    def _blocked(self, item, reason, failure_class):
        self.store.transition(
            item, se.BLOCKED, reason_code="policy_block", **COMMON,
            fields={"blocked_reason": reason, "blocked_by": "guard",
                    "blocked_detail": "x", "failure_class": failure_class})
        cls = rp.classify(failure_class, attempt=0, attempts_lost=0, max_attempts=3)
        fr.emit_failure_envelope(self.ctx, item, cls, reason_code="policy_block", detail="x",
                                 detected_by="test", guard="G4-GATE", blocked_reason=reason,
                                 resulting_status=se.BLOCKED)

    def _wait(self, gid):
        return [fr.verdict(gid, "t", "wait", "dependency_wait", "waiting on the predecessor")]

    def test_blocked_state_item_returns_to_pending_when_guards_wait(self):
        item = _state(self.store, "successor", 2)
        self._blocked(item, "awaiting_recovery_task", "gate-rejection")
        with mock.patch.object(fr, "evaluate_state_guards",
                               return_value=self._wait("G3-PREDECESSOR")), \
                contextlib.redirect_stdout(io.StringIO()):
            out = fr.refresh(self.ctx)
        self.assertEqual(item["status"], se.PENDING)
        self.assertFalse(item["eligible"])
        self.assertEqual(item["queue_status"], "Waiting")
        self.assertIsNone(item["blocked_reason"])
        self.assertIsNone(item["failure_class"])
        self.assertEqual([(t["from"], t["to"], t["trigger"]) for t in out["transitions"]],
                         [(se.BLOCKED, se.PENDING, "blocker_cleared")])
        entries = rp.RecoveryLedger(self.run_dir).entries()
        self.assertTrue(entries and all(e["status"] == "resolved" for e in entries))
        self.assertIn("now reports a wait", entries[0]["resolution"])

    def test_blocked_gate_item_returns_to_pending_when_guards_wait(self):
        _state(self.store, "p", 1)
        gate = _gate(self.store, "G", 1, "p")
        self._blocked(gate, "awaiting_human_decision", "gate-approval-required")
        with mock.patch.object(fr, "evaluate_gate_guards",
                               return_value=self._wait("G6-GATE-EVIDENCE")), \
                contextlib.redirect_stdout(io.StringIO()):
            fr.refresh(self.ctx)
        self.assertEqual(gate["status"], se.PENDING)
        self.assertIsNone(gate["blocked_reason"])
        # `next` offers only blocked gates, so a pending gate is not offered
        self.assertNotEqual(fr.next_action(self.store)["action"], "gate")

    def test_a_block_the_recovery_controller_raised_is_left_alone(self):
        item = _state(self.store, "p", 1)
        self.store.transition(
            item, se.BLOCKED, reason_code="policy_block", **COMMON,
            fields={"blocked_reason": "awaiting_recovery_task",
                    "blocked_by": "recovery-controller", "blocked_detail": "x",
                    "failure_class": "output-schema-failure"})
        with mock.patch.object(fr, "evaluate_state_guards",
                               return_value=self._wait("G3-PREDECESSOR")), \
                contextlib.redirect_stdout(io.StringIO()):
            fr.refresh(self.ctx)
        self.assertEqual(item["status"], se.BLOCKED)

    def test_a_block_whose_guards_still_block_stays_blocked(self):
        item = _state(self.store, "p", 1)
        self._blocked(item, "awaiting_recovery_task", "gate-rejection")
        block = [fr.verdict("G4-GATE", "t", "block", "policy_block", "still rejected",
                            "awaiting_recovery_task", "gate-rejection", gate="G")]
        with mock.patch.object(fr, "evaluate_state_guards", return_value=block), \
                contextlib.redirect_stdout(io.StringIO()):
            fr.refresh(self.ctx)
        self.assertEqual(item["status"], se.BLOCKED)


class RollbackRangeTestCase(unittest.TestCase):
    """The range is the target's completed downstream cone (architect ruling on F4)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)
        chain = [("scope", 1, ()), ("planning", 2, ("scope",)), ("design", 3, ("planning",)),
                 ("implementation", 4, ("design",)),
                 ("quality-review", 5, ("implementation",))]
        for sid, n, deps in chain:
            _complete(self.store, _state(self.store, sid, n, depends_on=deps))
        # the successor never consumed the evidence: pending, and never superseded
        _state(self.store, "handoff", 6, depends_on=("quality-review",))

    def test_default_target_is_the_closed_phase_alone(self):
        self.assertEqual(fr.rollback_range(self.store, "quality-review", "quality-review"),
                         ["quality-review"])

    def test_ancestor_target_supersedes_every_completed_phase_through_the_closed_one(self):
        self.assertEqual(fr.rollback_range(self.store, "implementation", "quality-review"),
                         ["quality-review", "implementation"])
        self.assertEqual(fr.rollback_range(self.store, "planning", "quality-review"),
                         ["quality-review", "implementation", "design", "planning"])

    def test_non_ancestor_target_is_refused(self):
        with self.assertRaises(ValueError):
            fr.rollback_range(self.store, "handoff", "quality-review")
        with self.assertRaises(ValueError):
            fr.rollback_range(self.store, "nowhere", "quality-review")

    def test_a_completed_dependent_off_the_closed_phase_ancestor_chain_is_superseded(self):
        """fix-bug shape: `fix-implementation` hard-depends on both `triage-and-impact` and
        `root-cause-analysis`. A rollback past the Fix Gate to triage must supersede the
        completed root-cause analysis too -- it stands on the evidence being rebuilt even
        though it is not an ancestor of the closed phase via the target."""
        store = se.StateStore.create(
            self.tmp / "run-fixbug", run_id="run-fixbug", command_id="bugfix",
            workflow_id="fix-bug", workflow_version="1.0.0",
            runtime_version=fr.RUNTIME_VERSION, input_digest="sha256:test", inputs=[])

        def phase(sid, n, deps=()):
            return store.add_item(se.new_work_item(
                run_id="run-fixbug", workflow_id="fix-bug", state_id=sid, work_type="state",
                owner_agent_id="x", phase_index=n, gate=None, artifact="x.md",
                depends_on=[{"state_id": d, "kind": "hard", "basis": "test"} for d in deps]))

        _complete(store, phase("triage-and-impact", 1))
        _complete(store, phase("root-cause-analysis", 2, ("triage-and-impact",)))
        _complete(store, phase("fix-implementation", 3,
                               ("triage-and-impact", "root-cause-analysis")))
        verification = phase("regression-verification", 4, ("fix-implementation",))
        phase("release-handoff", 5, ("regression-verification",))

        self.assertEqual(fr.rollback_range(store, "triage-and-impact", "fix-implementation"),
                         ["fix-implementation", "root-cause-analysis", "triage-and-impact"])
        self.assertEqual(fr.rollback_range(store, "root-cause-analysis", "fix-implementation"),
                         ["fix-implementation", "root-cause-analysis"])
        # the default target's cone is the closed phase alone while nothing after it completed
        self.assertEqual(fr.rollback_range(store, "fix-implementation", "fix-implementation"),
                         ["fix-implementation"])
        # ... and includes a completed successor once one exists: it consumed the evidence
        _complete(store, verification)
        self.assertEqual(fr.rollback_range(store, "fix-implementation", "fix-implementation"),
                         ["regression-verification", "fix-implementation"])
        self.assertEqual(fr.hard_descendants(store, "triage-and-impact"),
                         {"root-cause-analysis", "fix-implementation",
                          "regression-verification", "release-handoff"})


class RollbackPreconditionsTestCase(unittest.TestCase):
    """CR-001: no approved gate may stand over any phase in range, the closed phase included.

    `implement-feature` puts the Review Gate and the Verification Gate on `quality-review`.
    When the Review Gate stands rejected and the Verification Gate was approved, the rollback
    is refused exactly as it is for an approved gate on an intermediate phase, and the refusal
    writes nothing."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)
        _complete(self.store, _state(self.store, "implementation", 1, owner="omn-dev-1-implement"))
        _complete(self.store, _state(self.store, "quality-review", 2,
                                     depends_on=("implementation",), owner="omn-dev-2-reviewer"))
        _state(self.store, "handoff", 3, depends_on=("quality-review",))
        self.review = _gate(self.store, "Review Gate", 2, "quality-review",
                            owners=("omn-dev-2-reviewer", "omn-qa"), producer="omn-dev-2-reviewer")
        self.store.gate("Review Gate").update({"decision": "rejected", "owner_role": "omn-qa",
                                               "decided_by": "qa", "rationale": "no"})
        self.store.transition(self.review, se.FAILED, reason_code="validation_failed", **COMMON)
        self.verification = _gate(self.store, "Verification Gate", 2, "quality-review",
                                  owners=("omn-qa",), producer="omn-dev-2-reviewer")

    def test_an_undecided_sibling_gate_admits_the_rollback(self):
        pre = fr.rollback_preconditions(self.store, "Review Gate", "omn-qa", None)
        self.assertEqual(pre["phases"], ["quality-review"])
        self.assertEqual(pre["target"], "quality-review")
        pre = fr.rollback_preconditions(self.store, "Review Gate", "omn-qa", "implementation")
        self.assertEqual(pre["phases"], ["quality-review", "implementation"])

    def test_an_approved_sibling_gate_on_the_closed_phase_refuses_with_no_store_change(self):
        self.store.gate("Verification Gate").update({"decision": "approved",
                                                     "owner_role": "omn-qa",
                                                     "decided_by": "qa", "rationale": "fine"})
        self.store.transition(self.verification, se.COMPLETED, reason_code="output_accepted",
                              **COMMON)
        before = json.dumps(self.store.data, sort_keys=True)
        for target in (None, "implementation"):
            with self.assertRaises(fr.RuntimeError_) as raised:
                fr.rollback_preconditions(self.store, "Review Gate", "omn-qa", target)
            message = str(raised.exception)
            self.assertIn("[policy-failure]", message)
            self.assertIn("approved gate ['Verification Gate']", message)
            self.assertIn("cannot be re-armed", message)
        self.assertEqual(json.dumps(self.store.data, sort_keys=True), before)

    def test_an_approved_gate_on_an_intermediate_phase_is_refused_the_same_way(self):
        design_gate = _gate(self.store, "Design Gate", 1, "implementation",
                            owners=("architect",), producer="omn-dev-1-implement")
        self.store.gate("Design Gate").update({"decision": "approved"})
        self.store.transition(design_gate, se.COMPLETED, reason_code="output_accepted", **COMMON)
        with self.assertRaises(fr.RuntimeError_) as raised:
            fr.rollback_preconditions(self.store, "Review Gate", "omn-qa", "implementation")
        self.assertIn("approved gate ['Design Gate']", str(raised.exception))
        # the closed phase alone is still admissible: the approved gate is outside the range
        self.assertEqual(fr.rollback_preconditions(self.store, "Review Gate", "omn-qa",
                                                   None)["phases"], ["quality-review"])

    def test_the_other_refusals_still_hold_and_write_nothing(self):
        before = json.dumps(self.store.data, sort_keys=True)
        with self.assertRaises(fr.RuntimeError_):   # the producer may not authorise
            fr.rollback_preconditions(self.store, "Review Gate", "omn-dev-2-reviewer", None)
        with self.assertRaises(fr.RuntimeError_):   # a non-ancestor target
            fr.rollback_preconditions(self.store, "Review Gate", "omn-qa", "handoff")
        with self.assertRaises(fr.RuntimeError_):   # a gate that does not stand rejected
            fr.rollback_preconditions(self.store, "Verification Gate", "omn-qa", None)
        self.assertEqual(json.dumps(self.store.data, sort_keys=True), before)


class RejectedGateSurfacingTestCase(unittest.TestCase):
    """CR-004: on a run holding a standing rejection, `next` names the rollback ahead of any
    decision over the rejected evidence, the auto-approval path holds the sibling gate, and
    `recovery` derives an open gate-rejection envelope's action live -- the stranded-store
    case, where the persisted envelope still prescribes `release`."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)
        self.run_dir = self.tmp / RUN_ID
        _complete(self.store, _state(self.store, "implementation", 1, owner="omn-dev-1-implement"))
        _complete(self.store, _state(self.store, "quality-review", 2,
                                     depends_on=("implementation",), owner="omn-dev-2-reviewer"))
        self.successor = _state(self.store, "handoff", 3, depends_on=("quality-review",))
        self.review = _gate(self.store, "Review Gate", 2, "quality-review",
                            owners=("omn-dev-2-reviewer", "omn-qa"), producer="omn-dev-2-reviewer")
        self.store.gate("Review Gate").update({"decision": "rejected", "owner_role": "omn-qa",
                                               "decided_by": "qa",
                                               "rationale": "nine corrections"})
        self.store.transition(self.review, se.FAILED, reason_code="validation_failed", **COMMON)
        self.verification = _gate(self.store, "Verification Gate", 2, "quality-review",
                                  owners=("omn-qa",), producer="omn-dev-2-reviewer")
        self.store.transition(self.verification, se.BLOCKED, reason_code="policy_block",
                              fields={"blocked_reason": "awaiting_human_decision",
                                      "blocked_by": "guard", "blocked_detail": "x"}, **COMMON)
        self.ctx = {"store": self.store, "run_dir": self.run_dir,
                    "ledger": fr.RunLedger(self.run_dir)}

    def test_next_action_alone_would_offer_the_sibling_gate(self):
        # the hazard the notice pre-empts: the scheduler's own choice is a decision on the
        # Verification Gate, over the evidence the Review Gate rejected
        act = fr.next_action(self.store)
        self.assertEqual((act["action"], act["item"]["state_id"]),
                         ("gate", "Verification Gate"))
        self.assertEqual(fr.sibling_rejection(self.store, self.store.gate("Verification Gate"))
                         ["gate"], "Review Gate")
        self.assertIsNone(fr.sibling_rejection(self.store, self.store.gate("Review Gate")))

    def test_rollback_notice_names_the_rollback_first_and_withholds_the_sibling(self):
        lines = fr.rollback_notice(RUN_ID, self.ctx)
        self.assertTrue(lines[0].startswith("NEXT: authorise the rollback"))
        self.assertIn("Review Gate", lines[0])
        command = lines[1].strip()
        self.assertTrue(command.startswith("python "))
        self.assertIn("framework_runtime.py rollback", command)
        self.assertIn('--gate "Review Gate"', command)
        self.assertIn("--target quality-review", command)
        self.assertIn("--owner-role omn-qa", command)
        self.assertIn("--decided-by <who>", command)
        self.assertIn("rejected by omn-qa: nine corrections", lines[2])
        self.assertIn("['Verification Gate'] also close quality-review", lines[3])
        self.assertIn("no decision is offered", lines[3])

    def test_no_notice_once_the_gate_is_re_armed(self):
        self.store.gate("Review Gate").update({"decision": None})
        self.store.transition(self.review, se.PENDING, reason_code="enqueued", **COMMON)
        self.assertEqual(fr.rollback_notice(RUN_ID, self.ctx), [])
        self.assertIsNone(fr.sibling_rejection(self.store, self.store.gate("Verification Gate")))

    def test_live_clearing_action_replaces_a_stale_prescription_and_keeps_the_rest(self):
        stale_release = (f"python x/runtime/framework_runtime.py release --run-id {RUN_ID} "
                         f"--phase handoff --reason tool_failure --detail <what happened>")
        successor_env = {"work_type": "state", "state_id": "handoff",
                         "failure_class": "gate-rejection", "clearing_action": stale_release}
        live = fr.live_clearing_action(RUN_ID, self.ctx, successor_env)
        self.assertIn("rollback", live)
        self.assertIn('--gate "Review Gate"', live)
        self.assertNotIn("release", live)
        # the rejected gate's own stale awaiting-decision envelope prescribes the approval it
        # can no longer take; it too is derived live
        gate_env = {"work_type": "gate", "state_id": "Review Gate",
                    "failure_class": "gate-approval-required",
                    "clearing_action": "python x gate --gate Review Gate --decision approve"}
        self.assertIn("rollback", fr.live_clearing_action(RUN_ID, self.ctx, gate_env))
        # an unrelated envelope is returned as recorded
        other = {"work_type": "state", "state_id": "implementation",
                 "failure_class": "output-schema-failure", "clearing_action": "as recorded"}
        self.assertEqual(fr.live_clearing_action(RUN_ID, self.ctx, other), "as recorded")
        # and so is everything once no gate stands rejected
        self.store.gate("Review Gate").update({"decision": None})
        self.store.transition(self.review, se.PENDING, reason_code="enqueued", **COMMON)
        self.assertEqual(fr.live_clearing_action(RUN_ID, self.ctx, successor_env), stale_release)

    def test_cmd_recovery_prints_the_live_action_and_leaves_the_envelope_as_written(self):
        self.store.save()
        cls = rp.classify("gate-rejection", attempt=1, attempts_lost=0, max_attempts=3)
        with contextlib.redirect_stdout(io.StringIO()):
            fr.emit_failure_envelope(self.ctx, self.successor, cls, reason_code="policy_block",
                                     detail="Review Gate was rejected", detected_by="test",
                                     guard="G4-GATE", blocked_reason="awaiting_recovery_task",
                                     resulting_status=se.BLOCKED, gate="Review Gate")
        # age the envelope into the stranded shape: the string a pre-fix runtime persisted
        ledger_path = self.run_dir / rp.RecoveryLedger.FILENAME
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
        stale = (f"python x/runtime/framework_runtime.py release --run-id {RUN_ID} "
                 f"--phase handoff --reason tool_failure --detail <what happened>")
        data["entries"][0]["clearing_action"] = stale
        data["entries"][0]["proposed_options"] = ["approve an exception and proceed"]
        ledger_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        persisted = ledger_path.read_bytes()

        buf = io.StringIO()
        with mock.patch.object(fr, "RUNS", self.tmp), contextlib.redirect_stdout(buf):
            rc = fr.cmd_recovery(argparse.Namespace(run_id=RUN_ID, open_only=True))
        out = buf.getvalue()
        self.assertEqual(rc, 0)
        clear_by = next(ln for ln in out.splitlines() if ln.strip().startswith("clear by"))
        self.assertIn("rollback", clear_by)
        self.assertIn('--gate "Review Gate"', clear_by)
        self.assertIn("--decided-by <who>", clear_by)
        recorded = next(ln for ln in out.splitlines() if ln.strip().startswith("recorded as"))
        self.assertIn(stale, recorded)
        self.assertNotIn("approve an exception", out)
        self.assertIn("authorise a rollback", out)
        self.assertEqual(ledger_path.read_bytes(), persisted)


class StatusViewTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-rollback-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.store = _store(self.tmp)
        self.phase = _state(self.store, "implementation", 1)
        _complete(self.store, self.phase)
        self.gate = _gate(self.store, "Review Gate", 1, "implementation",
                          owners=("omn-dev-2-reviewer", "omn-qa"), producer="omn-dev-1-implement")
        g = self.store.gate("Review Gate")
        g.update({"decision": "rejected", "owner_role": "omn-qa", "decided_by": "qa",
                  "decided_at": "2026-09-06T09:05:36Z", "rationale": "nine corrections"})
        self.store.transition(self.gate, se.FAILED, reason_code="validation_failed", **COMMON)
        # the authorised rollback, as `cmd_rollback` records it
        self.store.transition(
            self.phase, se.PENDING, reason_code="enqueued",
            fields={"supersession": {"authorisation_id": "RB-x-review-gate-01",
                                     "gate": "Review Gate", "target": "implementation"}},
            **COMMON)
        g["decision_history"].append({"decision": "rejected", "owner_role": "omn-qa",
                                      "decided_by": "qa", "decided_at": "2026-09-06T09:05:36Z",
                                      "superseded_by": "RB-x-review-gate-01"})
        g.update({"decision": None, "owner_role": None, "decided_by": None, "rationale": None,
                  "decided_at": None})
        self.store.transition(self.gate, se.PENDING, reason_code="enqueued", **COMMON)
        self.store.set_eligibility(self.phase, True, [])

    def test_state_json_carries_the_rollback_block_and_the_decision_history(self):
        view = fr.state_json(self.store)
        step = view["phases"][0]["steps"][0]
        gate = view["phases"][0]["gates"][0]
        self.assertEqual((step["status"], step["eligible"], step["attempt"]),
                         (se.PENDING, True, 0))
        self.assertEqual(step["rollback"], {"gate": "Review Gate",
                                            "authorisation_id": "RB-x-review-gate-01",
                                            "superseded_attempt": 0})
        self.assertEqual((gate["status"], gate["decision"]), (se.PENDING, None))
        self.assertEqual(gate["decision_history"][0]["decision"], "rejected")
        self.assertEqual(gate["decision_history"][0]["superseded_by"], "RB-x-review-gate-01")
        json.dumps(view)

    def test_plain_table_and_tree_name_the_supersession_and_the_re_arm(self):
        table = "\n".join(fr.state_table(self.store))
        self.assertIn("superseded under RB-x-review-gate-01", table)
        self.assertIn("re-armed after rejected by omn-qa", table)
        tree = "\n".join(fr.render_tree(self.store, color=False))
        self.assertIn("superseded under RB-x-review-gate-01", tree)
        self.assertIn("re-armed after rejected by omn-qa", tree)

    def test_completion_package_lists_the_superseded_attempt(self):
        ctx = {"store": self.store, "run_dir": self.tmp / RUN_ID,
               "ledger": fr.RunLedger(self.tmp / RUN_ID)}
        package = fr.build_completion_package(ctx)
        self.assertIn("## Superseded Attempts", package)
        self.assertIn("RB-x-review-gate-01", package)
        self.assertIn("sha256:aaa", package)
        report = fr.build_final_report(ctx)
        self.assertIn("re-armed after 1 prior decision(s): rejected by omn-qa", report)


if __name__ == "__main__":
    unittest.main(verbosity=2)
