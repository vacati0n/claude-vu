"""Unit tests for the recovery verifier's clearing-action admissibility table.

`verify_recovery.py` check X1 judges every open envelope's clearing action against the work
item it names, through `clearing_action_admissible`. These tests pin that table hermetically,
against a synthetic run state, so a regression names the row that drifted:

  * the `policy-exception` action the runtime emits for a state work item blocked
    `awaiting_policy_exception` is admissible with its role, decider, and rationale left as
    placeholders, and admissible filled in by a listed, non-producing role;
  * the same action is inadmissible everywhere else -- a pending, completed, or differently
    blocked item, an unknown phase, a gate name, a placeholder outside the three human
    flags, a role the envelope does not list, or the producer's own role -- and the
    placeholder exemption never extends past that one blocked item;
  * the gate row keeps its own exemption, and a non-gate command gains none;
  * the rollback row keeps its pre-existing verdicts against a real rejected-gate store:
    only the decider may stay a placeholder, and the role guard still holds;
  * every subcommand the runtime's clearing-action builder can name has a row in the table,
    so a new command-naming branch cannot ship without one;
  * a placeholder is recognised in every form it can take once `shlex` has split the action
    -- several words, glued to a prefix or a suffix, unterminated, or one word -- so each is
    judged inadmissible by the table and refused by the execution guard, while the same
    action filled in stays admissible and runs unchanged; after an exempt flag, only a
    placeholder that is one whole argument keeps the exemption.
"""

from __future__ import annotations

import inspect
import re
import shlex
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402
import recovery_policy as rp    # noqa: E402
import state_engine as se       # noqa: E402
import verify_recovery as vr    # noqa: E402

RUN_ID = "run-admissibilitytest"
PHASE = "execution-planning"
PRODUCER = "planner"
GATE = "Planning Gate"


def _item(state_id, work_type="state", status=se.PENDING, blocked_reason=None,
          owner=PRODUCER):
    return {"state_id": state_id, "work_type": work_type, "status": status,
            "blocked_reason": blocked_reason, "blocked_by": None,
            "owner_agent_id": owner}


def _state(status=se.BLOCKED, blocked_reason="awaiting_policy_exception"):
    return {
        "work_items": {
            PHASE: _item(PHASE, status=status, blocked_reason=blocked_reason),
            f"gate:{GATE}": _item(GATE, work_type="gate", status=se.BLOCKED,
                                  blocked_reason="awaiting_human_decision", owner=None),
        },
        "gates": {GATE: {"decision": None, "closes_state": PHASE,
                         "producer_agent": PRODUCER, "owner_roles": []}},
    }


def _policy_action(phase=PHASE, role="<role>", who="<who>", text="<text>", run_id=RUN_ID):
    return (f"python {fr.FW_PREFIX}/runtime/framework_runtime.py policy-exception "
            f"--run-id {run_id} --phase {fr._shell_word(phase)} --owner-role {role} "
            f"--decided-by {who} --rationale {text}")


def _entry(action, owner_roles=None):
    return {"clearing_action": action, "owner_agent_id": PRODUCER,
            "owner_roles": owner_roles or []}


class _Table(unittest.TestCase):
    def judge(self, action, state=None, owner_roles=None):
        with mock.patch.object(vr, "load_state", return_value=state or _state()):
            return vr.clearing_action_admissible(RUN_ID, _entry(action, owner_roles))


class PolicyExceptionAdmissibleTestCase(_Table):
    """The emitted action is admissible on exactly the item it was emitted for."""

    def test_emitted_action_with_placeholders_is_admissible(self):
        action = fr.clearing_action(
            RUN_ID, _item(PHASE), SimpleNamespace(action=rp.ESCALATE,
                                                  failure_class="policy-failure",
                                                  budget_exhausted=False,
                                                  breaker_open=False),
            "awaiting_policy_exception")
        self.assertIn(" policy-exception ", action)
        ok, why = self.judge(action)
        self.assertTrue(ok, why)

    def test_filled_listed_non_producer_role_is_admissible(self):
        ok, why = self.judge(_policy_action(role="omn-tech-lead", who="someone",
                                            text="false-positive"),
                             owner_roles=["omn-tech-lead"])
        self.assertTrue(ok, why)


class PolicyExceptionInadmissibleTestCase(_Table):
    """Every other position of the same action is judged inadmissible."""

    def assert_inadmissible(self, action, state=None, owner_roles=None, reason=None):
        ok, why = self.judge(action, state, owner_roles)
        self.assertFalse(ok, why)
        if reason:
            self.assertIn(reason, why)

    def test_pending_item(self):
        self.assert_inadmissible(_policy_action(), _state(se.PENDING, None),
                                 reason="placeholder")

    def test_completed_item_although_the_command_replays_there(self):
        self.assert_inadmissible(_policy_action(), _state(se.COMPLETED, None),
                                 reason="placeholder")

    def test_blocked_awaiting_recovery_task(self):
        self.assert_inadmissible(_policy_action(),
                                 _state(se.BLOCKED, "awaiting_recovery_task"),
                                 reason="placeholder")

    def test_blocked_awaiting_human_decision(self):
        self.assert_inadmissible(_policy_action(),
                                 _state(se.BLOCKED, "awaiting_human_decision"),
                                 reason="placeholder")

    def test_wrong_block_with_filled_arguments_is_judged_by_the_row(self):
        self.assert_inadmissible(
            _policy_action(role="omn-tech-lead", who="someone", text="why"),
            _state(se.BLOCKED, "awaiting_recovery_task"),
            reason="blocked_reason=awaiting_recovery_task")

    def test_unknown_phase(self):
        self.assert_inadmissible(
            _policy_action(phase="no-such-phase", role="omn-tech-lead", who="x", text="y"),
            reason="not a state work item")

    def test_gate_name_is_not_a_state_item(self):
        self.assert_inadmissible(
            _policy_action(phase=f"gate:{GATE}", role="omn-tech-lead", who="x", text="y"),
            reason="not a state work item")

    def test_placeholder_after_run_id_is_not_exempt(self):
        self.assert_inadmissible(_policy_action(run_id="<run>"), reason="'<run>'")

    def test_placeholder_phase_is_not_exempt(self):
        self.assert_inadmissible(_policy_action(phase="<phase>"), reason="'<phase>'")

    def test_unlisted_role(self):
        self.assert_inadmissible(_policy_action(role="omn-qa", who="x", text="y"),
                                 owner_roles=["omn-tech-lead"], reason="may not decide")

    def test_producer_role_may_not_except_itself(self):
        self.assert_inadmissible(_policy_action(role=PRODUCER, who="x", text="y"),
                                 reason="may not decide")


class ExemptionScopeTestCase(_Table):
    """The policy-exception exemption leaves the other rows' exemptions as they were."""

    def test_gate_action_keeps_its_exemption(self):
        action = (f"python {fr.FW_PREFIX}/runtime/framework_runtime.py gate --run-id {RUN_ID} "
                  f"--gate {fr._shell_word(GATE)} --decision approve --owner-role <role> "
                  f"--decided-by <who> --rationale <text>")
        ok, why = self.judge(action)
        self.assertTrue(ok, why)

    def test_release_gains_no_exemption_on_a_policy_blocked_item(self):
        action = (f"python {fr.FW_PREFIX}/runtime/framework_runtime.py release "
                  f"--run-id {RUN_ID} --phase {PHASE} --reason tool_failure "
                  f"--owner-role <role>")
        ok, why = self.judge(action)
        self.assertFalse(ok, why)
        self.assertIn("placeholder", why)


class PlaceholderFormTestCase(_Table):
    """Every form of placeholder is recognised, by the table and by the execution guard alike.

    Each case is a `release` on a leased item, where the release row alone would admit the
    action, so a refusal can only come from the placeholder. The reason must name the whole
    placeholder, and `executable` must refuse the same argv, since both share one definition.
    """

    @staticmethod
    def release(reason):
        return (f"python {fr.FW_PREFIX}/runtime/framework_runtime.py release "
                f"--run-id {RUN_ID} --phase {PHASE} --reason {reason}")

    def assert_refused(self, reason, placeholder):
        action = self.release(reason)
        ok, why = self.judge(action, _state(se.LEASED, None))
        self.assertFalse(ok, why)
        self.assertIn(f"placeholder argument [{placeholder!r}]", why)
        with self.assertRaises(AssertionError):
            vr.executable(vr.runtime_command(action))

    def test_multi_word_placeholder_is_inadmissible(self):
        self.assert_refused("<fill in owner name>", "<fill in owner name>")

    def test_glued_prefix_placeholder_is_inadmissible(self):
        self.assert_refused("x<owner>", "x<owner>")

    def test_glued_suffix_placeholder_is_inadmissible(self):
        self.assert_refused("<owner>x", "<owner>x")

    def test_unterminated_placeholder_is_inadmissible(self):
        self.assert_refused("<owner --detail filled", "<owner --detail filled")

    def test_single_word_placeholder_is_inadmissible(self):
        self.assert_refused("<owner>", "<owner>")

    def test_valid_action_is_admissible(self):
        action = self.release("tool_failure")
        ok, why = self.judge(action, _state(se.LEASED, None))
        self.assertTrue(ok, why)
        argv = vr.runtime_command(action)
        self.assertEqual(vr.executable(argv), argv)

    def test_only_a_whole_argument_after_an_exempt_flag_stays_exempt(self):
        for who, text in (("<who>", "<fill in text>"), ("x<who>", "<text>"),
                          ("<who>x", "<text>"), ("<who>", "<text")):
            with self.subTest(who=who, text=text):
                action = (f"python {fr.FW_PREFIX}/runtime/framework_runtime.py gate "
                          f"--run-id {RUN_ID} --gate {fr._shell_word(GATE)} "
                          f"--decision approve --owner-role <role> --decided-by {who} "
                          f"--rationale {text}")
                ok, why = self.judge(action)
                self.assertFalse(ok, why)
                self.assertIn("placeholder argument", why)


class RollbackRowUnchangedTestCase(unittest.TestCase):
    """The rollback row keeps the verdicts it gave before the policy-exception row existed.

    Judged against a real state store with a rejected gate, because the row loads the store
    to check the rollback range and the attempt budget. Only the decider may stay a
    placeholder; the role and the rationale are filled in by the builder and validated, so
    each refusal is checked for its reason, not only its verdict.
    """

    def setUp(self):
        tmp = Path(tempfile.mkdtemp(prefix="omn-admissibility-"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        common = dict(actor_type="runtime", actor_id="test", detail="test")
        store = se.StateStore.create(
            tmp / RUN_ID, run_id=RUN_ID, command_id="implement",
            workflow_id="implement-feature", workflow_version="1.0.0",
            runtime_version=fr.RUNTIME_VERSION, input_digest="sha256:test", inputs=[])
        phase = store.add_item(se.new_work_item(
            run_id=RUN_ID, workflow_id="implement-feature", state_id=PHASE, work_type="state",
            owner_agent_id=PRODUCER, phase_index=1, gate=None, artifact="x.md", depends_on=[]))
        store.transition(phase, se.LEASED, reason_code="leased", **common)
        store.transition(phase, se.RUNNING, reason_code="execution_started", **common)
        store.transition(phase, se.COMPLETED, reason_code="output_accepted",
                         fields={"completion": {"artifact_path": "runs/x/a.md",
                                                "artifact_digest": "sha256:aaa"},
                                 "artifact_path": "runs/x/a.md"}, **common)
        self.gate_item = store.add_item(se.new_work_item(
            run_id=RUN_ID, workflow_id="implement-feature", state_id=GATE, work_type="gate",
            owner_agent_id=None, phase_index=1, gate=GATE, artifact=None,
            depends_on=[{"state_id": PHASE, "kind": "hard", "basis": "the gate closes it"}]))
        store.add_gate({"gate": GATE, "closes_state": PHASE,
                        "owner_roles": [PRODUCER, "omn-tech-lead"],
                        "producer_agent": PRODUCER, "decision": None, "owner_role": None,
                        "decided_by": None, "rationale": None, "evidence_ref": None,
                        "decided_at": None, "decision_history": []})
        store.save()
        self.store, self.common = store, common
        patcher = mock.patch.object(vr, "RUNS", tmp)
        patcher.start()
        self.addCleanup(patcher.stop)

    def reject(self):
        self.store.gate(GATE).update({"decision": "rejected", "owner_role": "omn-tech-lead",
                                      "decided_by": "someone", "rationale": "no"})
        self.store.transition(self.gate_item, se.FAILED, reason_code="validation_failed",
                              **self.common)

    def emitted(self):
        return fr.rollback_clearing_action(RUN_ID, {"store": self.store}, GATE)

    @staticmethod
    def with_value(action, flag, value):
        argv = shlex.split(action, posix=True)
        argv[argv.index(flag) + 1] = value
        return shlex.join(argv)

    def judge(self, action):
        return vr.clearing_action_admissible(RUN_ID, _entry(action))

    def assert_inadmissible(self, action, reason):
        ok, why = self.judge(action)
        self.assertFalse(ok, why)
        self.assertIn(reason, why)

    def test_emitted_action_leaves_only_the_decider_and_is_admissible(self):
        self.reject()
        action = self.emitted()
        argv = shlex.split(action, posix=True)
        self.assertEqual(argv[2], "rollback")
        placeholders = [(argv[i - 1], a) for i, a in enumerate(argv)
                        if a.startswith("<") and a.endswith(">")]
        self.assertEqual(placeholders, [("--decided-by", "<who>")])
        ok, why = self.judge(action)
        self.assertTrue(ok, why)

    def test_filled_decider_stays_admissible(self):
        self.reject()
        ok, why = self.judge(self.with_value(self.emitted(), "--decided-by", "someone"))
        self.assertTrue(ok, why)

    def test_role_placeholder_is_not_exempt(self):
        self.reject()
        self.assert_inadmissible(self.with_value(self.emitted(), "--owner-role", "<role>"),
                                 "placeholder")

    def test_rationale_placeholder_is_not_exempt(self):
        self.reject()
        self.assert_inadmissible(self.with_value(self.emitted(), "--rationale", "<text>"),
                                 "placeholder")

    def test_producer_role_may_not_authorise(self):
        self.reject()
        self.assert_inadmissible(self.with_value(self.emitted(), "--owner-role", PRODUCER),
                                 "may not decide")

    def test_unlisted_role_may_not_authorise(self):
        self.reject()
        self.assert_inadmissible(self.with_value(self.emitted(), "--owner-role", "omn-qa"),
                                 "may not decide")

    def test_gate_that_does_not_stand_rejected(self):
        action = (f"python {fr.FW_PREFIX}/runtime/framework_runtime.py rollback "
                  f"--run-id {RUN_ID} --gate {fr._shell_word(GATE)} --target {PHASE} "
                  f"--owner-role omn-tech-lead --decided-by <who> --rationale why")
        self.assert_inadmissible(action, "decision=None")


class BuilderTablePinTestCase(_Table):
    """Every subcommand the clearing-action builder names has an admissibility row."""

    def test_every_builder_subcommand_has_a_row(self):
        source = (inspect.getsource(fr.clearing_action)
                  + inspect.getsource(fr.rollback_clearing_action))
        subs = sorted(set(re.findall(r"framework_runtime\.py ([a-z][a-z-]*)", source)))
        self.assertIn("policy-exception", subs)
        for sub in subs:
            with self.subTest(sub=sub):
                ok, why = self.judge(
                    f"python {fr.FW_PREFIX}/runtime/framework_runtime.py {sub} "
                    f"--run-id {RUN_ID} --phase no-such-phase --gate no-such-gate")
                self.assertFalse(why.startswith("unknown subcommand"), why)


if __name__ == "__main__":
    unittest.main()
