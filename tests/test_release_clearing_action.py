"""Unit tests for the `release` clearing action the runtime's builder emits.

`clearing_action` composes one `release` command and uses it twice: whole, for a state work
item blocked `awaiting_recovery_task` that no guard raised, and embedded as the optional
reclaim in every retry-class action ("To reclaim it sooner: ..."). These tests drive the
builder itself, never a hand-built string, so they pin what an envelope actually carries:

  * for aggregation-conflict and dependency-failure without a guard, the action names
    `release` and `verify_recovery.placeholders` finds nothing in it;
  * for output-schema-failure, worker-loss and invocation-transport-failure, the action
    starts `none required` and the reclaim it embeds carries no placeholder either;
  * the reclaim is the same command as the non-retry action for the same work item;
  * no argument of either form, once shell-tokenised, carries an angle bracket, and the
    `--detail` the command records is one fixed argument;
  * the recovery verifier's admissibility table admits the unedited non-retry action against
    an item the recovery controller blocked, and its execution guard runs it unchanged;
  * with guard G3-PREDECESSOR the non-retry classes still return prose naming no command.
"""

from __future__ import annotations

import shlex
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
RUNTIME = REPO / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME))

import framework_runtime as fr  # noqa: E402
import recovery_policy as rp    # noqa: E402
import state_engine as se       # noqa: E402
import verify_recovery as vr    # noqa: E402

RUN_ID = "run-releaseactiontest"
PHASE = "execution-planning"
NON_RETRY = ("aggregation-conflict", "dependency-failure")
RETRY = ("output-schema-failure", "worker-loss", "invocation-transport-failure")


def _item():
    return {"state_id": PHASE, "work_type": "state", "work_item_id": f"{RUN_ID}::{PHASE}"}


def _classify(failure_class):
    return rp.classify(failure_class, attempt=1, attempts_lost=0, max_attempts=3, seed="s")


def _action(failure_class, guard=None):
    cls = _classify(failure_class)
    return fr.clearing_action(RUN_ID, _item(), cls, cls.blocked_reason, guard=guard)


def _reclaim(action):
    """The command a retry-class action embeds after its `none required` prose."""
    return action[action.index("python"):]


class NonRetryReleaseActionTestCase(unittest.TestCase):
    """The non-guard `awaiting_recovery_task` action runs as written."""

    def test_classes_reach_the_release_branch(self):
        for failure_class in NON_RETRY:
            with self.subTest(failure_class=failure_class):
                cls = _classify(failure_class)
                self.assertNotEqual(cls.action, rp.RETRY)
                self.assertEqual(cls.blocked_reason, "awaiting_recovery_task")

    def test_action_names_release_and_carries_no_placeholder(self):
        for failure_class in NON_RETRY:
            with self.subTest(failure_class=failure_class):
                action = _action(failure_class)
                argv = shlex.split(action)
                self.assertEqual(argv[2], "release")
                self.assertEqual(vr.placeholders(argv), [])

    def test_no_argument_carries_an_angle_bracket(self):
        for failure_class in NON_RETRY:
            with self.subTest(failure_class=failure_class):
                for arg in shlex.split(_action(failure_class)):
                    self.assertNotIn("<", arg)
                    self.assertNotIn(">", arg)

    def test_detail_is_one_fixed_argument_naming_the_operator(self):
        argv = shlex.split(_action("aggregation-conflict"))
        detail = argv[argv.index("--detail") + 1]
        self.assertEqual(argv[-1], detail)
        self.assertIn("operator", detail)
        self.assertEqual(detail, shlex.split(_action("dependency-failure"))[-1])


class RetryReclaimActionTestCase(unittest.TestCase):
    """The reclaim every retry-class action offers runs as written."""

    def test_action_is_prose_first(self):
        for failure_class in RETRY:
            with self.subTest(failure_class=failure_class):
                self.assertEqual(_classify(failure_class).action, rp.RETRY)
                self.assertTrue(_action(failure_class).startswith("none required"))

    def test_reclaim_carries_no_placeholder(self):
        for failure_class in RETRY:
            with self.subTest(failure_class=failure_class):
                action = _action(failure_class)
                argv = shlex.split(_reclaim(action))
                self.assertEqual(argv[2], "release")
                self.assertEqual(vr.placeholders(argv), [])
                self.assertEqual(vr.placeholders(vr.runtime_command(action)), [])

    def test_no_reclaim_argument_carries_an_angle_bracket(self):
        for failure_class in RETRY:
            with self.subTest(failure_class=failure_class):
                for arg in shlex.split(_reclaim(_action(failure_class))):
                    self.assertNotIn("<", arg)
                    self.assertNotIn(">", arg)

    def test_reclaim_is_the_non_retry_command(self):
        expected = shlex.split(_action("aggregation-conflict"))
        for failure_class in RETRY:
            with self.subTest(failure_class=failure_class):
                self.assertEqual(shlex.split(_reclaim(_action(failure_class))), expected)

    def test_reclaim_is_unchanged_by_a_guard(self):
        for failure_class in RETRY:
            with self.subTest(failure_class=failure_class):
                self.assertEqual(_action(failure_class, guard="G3-PREDECESSOR"),
                                 _action(failure_class))


class AdmissibilityTestCase(unittest.TestCase):
    """X1 admits the unedited action where `release` would act on it."""

    @staticmethod
    def _state():
        return {"work_items": {PHASE: {
            "state_id": PHASE, "work_type": "state", "status": se.BLOCKED,
            "blocked_reason": "awaiting_recovery_task", "blocked_by": "recovery-controller",
            "owner_agent_id": "planner"}}, "gates": {}}

    def test_non_retry_action_is_admissible_against_a_controller_block(self):
        for failure_class in NON_RETRY:
            with self.subTest(failure_class=failure_class):
                action = _action(failure_class)
                entry = {"clearing_action": action, "owner_agent_id": "planner",
                         "owner_roles": []}
                with mock.patch.object(vr, "load_state", return_value=self._state()):
                    ok, why = vr.clearing_action_admissible(RUN_ID, entry)
                self.assertTrue(ok, why)
                self.assertTrue(why.startswith("release on"), why)

    def test_execution_guard_runs_the_action_unchanged(self):
        for failure_class in NON_RETRY + RETRY:
            with self.subTest(failure_class=failure_class):
                argv = vr.runtime_command(_action(failure_class))
                self.assertEqual(vr.executable(argv), argv)


class GuardRaisedBlockTestCase(unittest.TestCase):
    """A guard-raised block still names no runtime command."""

    def test_g3_block_is_prose(self):
        for failure_class in NON_RETRY:
            with self.subTest(failure_class=failure_class):
                action = _action(failure_class, guard="G3-PREDECESSOR")
                self.assertIsNone(vr.runtime_command(action))
                self.assertNotIn("release", action)


if __name__ == "__main__":
    unittest.main()
