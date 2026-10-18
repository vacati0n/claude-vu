"""End-to-end tests for the `policy-exception` command, executed as the runtime emits it.

A state work item blocked `awaiting_policy_exception` is cleared only by the clearing action
its failure envelope carries. These tests drive the real command line, in a copy of the
framework tree held in a temp directory, to that block the way `verify_recovery.py`
scenario C induces it -- an accepted artifact whose result envelope declares a write
outside the role's permitted set -- and then execute the clearing action read from the
envelope with only its three human arguments (role, decider, rationale) filled in:

  * the producer's own role is refused, and nothing in the run changes;
  * a non-producing role clears the block: the item returns to the queue, the envelope and
    its recovery-ledger entry are resolved by the named decider, the decision is recorded
    over the undeclared write, one `escalation_resolved` event is emitted, and a repeat is
    refused because nothing is blocked any more;
  * once the envelope lists its owners, a role it does not list is refused with no write.

Nothing is written under the repository's own `.claude/runs`: each case builds and removes
its own tree. The permissive behaviour for an envelope that lists no owners is exercised
but not asserted as correct; which roles may decide a policy exception is an open design
question.
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLAUDE = REPO / ".claude"
sys.path.insert(0, str(CLAUDE / "runtime"))

import recovery_policy as rp  # noqa: E402
import state_engine as se     # noqa: E402

PHASE = "execution-planning"
PRODUCER = "planner"
UNDECLARED = "memory/architecture.md"
# The conforming artifact: a plan the runtime already accepted, in committed run evidence.
# It is read from the repository's tree and never written.
GOOD_SOURCE = (CLAUDE / "runs" / "run-c5a8d50d3238" / "states" / PHASE / "artifacts"
               / "execution-plan.md")
HUMAN = {"--owner-role": "<role>", "--decided-by": "<who>", "--rationale": "<text>"}
REQUEST = (
    "# Feature Request: Policy Exception End-to-End\n\n"
    "## Intent\n\n"
    "Prove that a phase blocked on an undeclared write is cleared by the action its\n"
    "failure envelope names.\n\n"
    "## Acceptance Criteria\n\n"
    "- The emitted clearing action executes with only its human arguments filled in.\n")


def _strip(node):
    """A JSON tree with every `updated_at` removed: a refusal rewrites only timestamps."""
    if isinstance(node, dict):
        return {k: _strip(v) for k, v in node.items() if k != "updated_at"}
    if isinstance(node, list):
        return [_strip(v) for v in node]
    return node


class _BlockedTree(unittest.TestCase):
    """A framework tree copy with one run whose planning phase is blocked on a policy."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-pex-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        shutil.copytree(CLAUDE, self.tmp / ".claude", ignore=shutil.ignore_patterns(
            "runs", "__pycache__", "worktrees"))
        (self.tmp / "req.md").write_text(REQUEST, encoding="utf-8")

        done = self.cli("plan", "--command", "implement", "--input", "feature-request=req.md")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.run_id = json.loads(done.stdout[done.stdout.index("{"):])["run_id"]
        self.run_dir = self.tmp / ".claude" / "runs" / self.run_id
        self.state_dir = self.run_dir / "states" / PHASE

        done = self.cli("dispatch", "--run-id", self.run_id, "--phase", PHASE)
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        self.act_as_adapter()
        done = self.cli("complete", "--run-id", self.run_id, "--phase", PHASE)
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)

        item = self.item()
        self.assertEqual((item["status"], item["blocked_reason"]),
                         (se.BLOCKED, "awaiting_policy_exception"))
        self.envelope = self.failure_envelope()
        self.assertEqual(self.envelope["required_decision_type"], "policy-exception")
        self.assertEqual(self.envelope["owner_agent_id"], PRODUCER)

    # ------------------------------------------------------------------ plumbing

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, str(self.tmp / ".claude" / "runtime" / "framework_runtime.py"),
             *args], cwd=self.tmp, capture_output=True, text=True, encoding="utf-8")

    def act_as_adapter(self):
        """Write the accepted plan and a result envelope declaring one write too many."""
        ledger = json.loads((self.state_dir / "state-ledger.json").read_text(encoding="utf-8"))
        env = json.loads((self.state_dir / "invocation-envelope.json").read_text(
            encoding="utf-8"))
        text = GOOD_SOURCE.read_text(encoding="utf-8")
        for key, value in (("inputDigest", env["context_slice"]["input_digest"]),
                           ("contextDigest", env["context_slice"]["context_digest"])):
            text = re.sub(rf"(?m)^(\s*{key}:\s*).*$", lambda m: m.group(1) + value, text,
                          count=1)
        fw = self.tmp / ".claude"
        (fw / ledger["artifact_path"]).write_text(text, encoding="utf-8")
        (fw / ledger["result_envelope_path"]).write_text(json.dumps({
            "invocation_id": ledger["invocation_id"],
            "status": "succeeded",
            "artifact_refs": [ledger["artifact_path"]],
            "structured_output": {"produced_by": "test acting as the adapter"},
            "evidence_refs": [ledger["artifact_path"]],
            "confidence": 0.5,
            "declared_side_effects": [ledger["artifact_path"], ledger["result_envelope_path"],
                                      UNDECLARED],
            "error_class": None,
            "error_detail": None,
        }, indent=2), encoding="utf-8")

    def state(self):
        return json.loads((self.run_dir / "state.json").read_text(encoding="utf-8"))

    def item(self):
        return self.state()["work_items"][PHASE]

    def failure_envelope(self):
        return json.loads((self.state_dir / "failure-envelope.json").read_text(
            encoding="utf-8"))

    def phase_entries(self):
        return [e for e in rp.RecoveryLedger(self.run_dir).entries()
                if e["state_id"] == PHASE]

    def snapshot(self):
        """Every fact the command could change, timestamps aside."""
        return _strip({"work_items": self.state()["work_items"],
                       "ledger": rp.RecoveryLedger(self.run_dir).read(),
                       "envelope": self.failure_envelope()})

    def execute(self, role, who="Test Decider", text="a reviewed false positive"):
        """Run the envelope's clearing action as written, its three human arguments filled."""
        argv = shlex.split(self.envelope["clearing_action"], posix=True)
        self.assertEqual(argv[:3], ["python", ".claude/runtime/framework_runtime.py",
                                    "policy-exception"])
        for flag, placeholder in HUMAN.items():
            self.assertIn(flag, argv, f"the emitted action names no {flag}: {argv}")
            self.assertEqual(argv[argv.index(flag) + 1], placeholder)
        filled = {"--owner-role": role, "--decided-by": who, "--rationale": text}
        for flag, value in filled.items():
            argv[argv.index(flag) + 1] = value
        left = [a for a in argv if a.startswith("<") and a.endswith(">")]
        self.assertEqual(left, [], f"placeholders outside the human arguments: {argv}")
        argv[0] = sys.executable
        return subprocess.run(argv, cwd=self.tmp, capture_output=True, text=True,
                              encoding="utf-8")

    def assert_refused_without_write(self, role, reason):
        before = self.snapshot()
        done = self.execute(role)
        out = done.stdout + done.stderr
        self.assertEqual(done.returncode, 2, out)
        self.assertIn("policy-failure", out)
        self.assertIn(reason, out)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.state_dir / "policy-exception.json").exists())


class EmittedPolicyExceptionActionTestCase(_BlockedTree):
    """The emitted action, executed: the producer is refused, a non-producer clears."""

    def test_emitted_action_refuses_the_producer_then_clears_for_a_non_producer(self):
        self.assert_refused_without_write(PRODUCER, "may not except")

        done = self.execute("omn-tech-lead", who="Test Decider")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)

        item = self.item()
        self.assertEqual(item["status"], se.PENDING)
        self.assertIsNone(item["blocked_reason"])
        self.assertEqual(len(item["policy_exceptions"]), 1)
        self.assertEqual(item["policy_exceptions"][0]["owner_role"], "omn-tech-lead")

        envelope = self.failure_envelope()
        self.assertEqual(envelope["status"], "resolved")
        self.assertEqual(envelope["resolved_by"], "human:Test Decider")
        entries = self.phase_entries()
        self.assertTrue(entries)
        self.assertEqual({(e["status"], e["resolved_by"]) for e in entries},
                         {("resolved", "human:Test Decider")})

        decision = json.loads((self.state_dir / "policy-exception.json").read_text(
            encoding="utf-8"))
        self.assertEqual(decision["owner_role"], "omn-tech-lead")
        self.assertEqual(decision["decided_by"], "Test Decider")
        self.assertEqual(decision["granted_over"], [UNDECLARED])

        events = [json.loads(ln) for ln in (self.run_dir / "events.jsonl").read_text(
            encoding="utf-8").splitlines() if ln]
        resolved = [e for e in events if e["event_type"] == "escalation_resolved"
                    and e.get("state_id") == PHASE]
        self.assertEqual(len(resolved), 1)

        again = self.execute("omn-tech-lead")
        self.assertEqual(again.returncode, 2, again.stdout + again.stderr)
        self.assertIn("not blocked", again.stdout + again.stderr)


class ListedOwnerPolicyExceptionTestCase(_BlockedTree):
    """Where the envelope lists its owners, a role it does not list is refused."""

    def test_unlisted_role_is_refused_without_write(self):
        path = self.state_dir / "failure-envelope.json"
        env = self.failure_envelope()
        env["owner_roles"] = ["omn-tech-lead"]
        path.write_text(json.dumps(env, indent=2), encoding="utf-8")
        self.assert_refused_without_write("omn-qa", "not a recorded owner")


if __name__ == "__main__":
    unittest.main()
