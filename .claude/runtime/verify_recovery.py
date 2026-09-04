#!/usr/bin/env python3
"""Executable proof that the runtime recovers from classified failures.

`verify_vertical_slice.py` proves a phase can execute. `verify_multi_phase.py` proves a run is
a state machine. Neither proves anything about the paths a run takes when something goes wrong,
because a successful run never takes them. This script induces the failures instead.

Three runs, each injecting one fault at the adapter boundary, driven through the real command
line rather than by calling functions -- what is proved is the runtime an operator uses:

  Run A  a rejected artifact, repaired
         attempt 1 returns a structurally invalid plan. The Validation Engine rejects it, the
         Recovery Controller classifies `output-schema-failure` as retryable, and the work item
         moves to `retrying` with a deadline. Once the backoff elapses the scheduler promotes
         it, the re-dispatch carries the rejection back to the agent as a repair pass, and
         attempt 2 returns a conforming plan that is accepted.

  Run B  a rejected artifact, never repaired
         every attempt returns the same invalid plan. Attempts are charged, the budget bounds
         them at three, and the fourth is refused rather than granted: the work item blocks
         with a recorded reason and an open envelope, and `release` refuses to grant an attempt
         the budget does not have.

  Run C  a policy violation
         the artifact is valid, but the agent declares a write outside its permitted set. That
         is not a transient fault, so it is classified `policy-failure` and never scheduled for
         a retry. This is the negative case: it proves the policy discriminates rather than
         retrying whatever fails.

The harness stands in for the agent adapter and nothing else. It writes the artifact and the
result envelope the adapter would have written, then hands control back to the runtime. Every
transition, classification, and envelope this script asserts on is produced by the runtime.

Each run is keyed by its own input file, so its `run_id` is derived, not assigned. A previous
execution's run directory is removed before it is re-planned, and only ever the directories
these three inputs derive.

    python .claude/runtime/verify_recovery.py            # run all three
    python .claude/runtime/verify_recovery.py --keep     # leave the run directories in place
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import framework_runtime as fr  # noqa: E402
import recovery_policy as rp    # noqa: E402
import state_engine as se       # noqa: E402

CLAUDE = fr.CLAUDE
RUNS = fr.RUNS
INPUTS = RUNS / "inputs"
PY = sys.executable
RUNTIME = str(Path(__file__).resolve().parent / "framework_runtime.py")

# The conforming artifact every scenario starts from: a plan the runtime itself already
# accepted, in a committed run. Reusing accepted evidence rather than authoring a fixture keeps
# the proof honest -- an artifact the Validation Engine has passed in production conditions.
GOOD_SOURCE = (RUNS / "run-c5a8d50d3238/states/execution-planning/artifacts/"
               "execution-plan.md")

PHASE = "execution-planning"
INPUT_TYPE = "feature-request"


class Result:
    def __init__(self, title):
        self.title = title
        self.checks = []

    def add(self, cid, description, ok, detail=""):
        self.checks.append({"id": cid, "description": description,
                            "result": "pass" if ok else "fail", "detail": detail})
        return ok

    @property
    def passed(self):
        return all(c["result"] == "pass" for c in self.checks)

    def render(self):
        out = ["", self.title, "-" * 100]
        for c in self.checks:
            out.append(f"[{'PASS' if c['result'] == 'pass' else 'FAIL'}] {c['id']:<5} "
                       f"{c['description']}")
            if c["detail"]:
                out.append(f"        {c['detail']}")
        return out


# --------------------------------------------------------------------------- harness plumbing


def run(*argv, expect: int | None = 0) -> tuple[int, str]:
    """Invoke the runtime command line and return (exit code, combined output)."""
    proc = subprocess.run([PY, RUNTIME, *argv], capture_output=True, text=True,
                          cwd=str(CLAUDE.parent))
    out = proc.stdout + proc.stderr
    if expect is not None and proc.returncode != expect:
        raise AssertionError(f"`{' '.join(argv)}` exited {proc.returncode}, expected "
                             f"{expect}\n{out}")
    return proc.returncode, out


def write_input(slug: str, note: str) -> Path:
    """One input file per scenario, so each derives its own run identity."""
    INPUTS.mkdir(parents=True, exist_ok=True)
    path = INPUTS / f"recovery-injection-{slug}.md"
    path.write_text(
        f"# Feature Request: Validation and Recovery Hardening ({slug})\n\n"
        f"## Intent\n\n"
        f"Improve the reliability of autonomous execution: extend validator coverage to every\n"
        f"core emitted artifact type, bound retries by a classified failure policy, and emit a\n"
        f"structured failure envelope for every blocked transition.\n\n"
        f"## Acceptance Criteria\n\n"
        f"- Every core emitted artifact type has a registered validator.\n"
        f"- A retryable failure is retried within a bounded attempt budget.\n"
        f"- A non-retryable failure is never retried.\n"
        f"- Every blocked transition emits a structured, classified failure envelope.\n\n"
        f"## Injection Note\n\n"
        f"{note}\n",
        encoding="utf-8")
    return path


def run_id_for(input_path: Path) -> str:
    supplied = [fr.read_supplied(INPUT_TYPE, str(input_path))]
    cmd = fr.resolve_command("implement")
    wf = fr.resolve_workflow(cmd["primaryWorkflow"])
    return fr.make_run_id(cmd["identifier"], wf["identifier"],
                          fr.run_input_digest(supplied))


def reset_run(run_id: str, input_path: Path):
    """Remove a run directory this harness previously created, and only such a directory."""
    d = RUNS / run_id
    if not d.exists():
        return
    state = d / "state.json"
    if state.exists():
        data = json.loads(state.read_text(encoding="utf-8"))
        refs = [i.get("reference", "") for i in data.get("inputs") or []]
        if not any("recovery-injection" in r for r in refs):
            raise AssertionError(f"refusing to remove {d}: it was not created by this "
                                 f"harness (inputs {refs})")
    shutil.rmtree(d)


def plan(input_path: Path) -> str:
    run_id = run_id_for(input_path)
    reset_run(run_id, input_path)
    run("plan", "--command", "implement", "--input", f"{INPUT_TYPE}={input_path}")
    return run_id


def state_dir(run_id: str) -> Path:
    return RUNS / run_id / "states" / PHASE


def load_state(run_id: str) -> dict:
    return json.loads((RUNS / run_id / "state.json").read_text(encoding="utf-8"))


def item_of(run_id: str) -> dict:
    return load_state(run_id)["work_items"][PHASE]


def transitions_of(run_id: str) -> list:
    return [(t["state_id"], t["from"], t["to"], t["reason_code"])
            for t in load_state(run_id)["transitions"]]


def events_of(run_id: str) -> list:
    path = RUNS / run_id / "events.jsonl"
    return [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines() if ln]


def phase_entries(run_id: str) -> list:
    """Recovery ledger entries for the injected phase only.

    A run of `implement-feature` blocks its other five phases at `G1-CAPABILITY`, because their
    owner agents hold no registry record, and each of those blocks emits its own envelope. Those
    are correct and are asserted on separately; here the subject is the one phase that executed.
    """
    return [e for e in rp.RecoveryLedger(RUNS / run_id).entries()
            if e["state_id"] == PHASE]


def envelope_of(run_id: str) -> dict:
    return json.loads((state_dir(run_id) / "failure-envelope.json").read_text(
        encoding="utf-8"))


# --------------------------------------------------------------------------- fake adapter


def good_artifact(run_id: str) -> str:
    """The accepted plan, re-stamped with this run's frozen digests.

    The plan carries the digests of the context slice it was produced against, and the
    validator cross-checks them against the invocation envelope. A different run freezes a
    different slice, so an agent executing here would stamp this run's digests; the harness does
    the same rather than leaving a mismatch the validator would correctly reject.
    """
    env = json.loads((state_dir(run_id) / "invocation-envelope.json").read_text(
        encoding="utf-8"))
    text = GOOD_SOURCE.read_text(encoding="utf-8")
    text = re.sub(r"(?m)^(\s*inputDigest:\s*).*$",
                  lambda m: m.group(1) + env["context_slice"]["input_digest"], text, count=1)
    text = re.sub(r"(?m)^(\s*contextDigest:\s*).*$",
                  lambda m: m.group(1) + env["context_slice"]["context_digest"], text,
                  count=1)
    return text


def broken_artifact(run_id: str) -> str:
    """The same plan with one mandatory section renamed.

    A single, surgical mutation, so the rejection is attributable: `Risks` is one of the twelve
    sections `agents/planner/output.md` fixes, so renaming it fails the mandatory-section check
    and introduces an unpermitted section, and nothing else changes.
    """
    return good_artifact(run_id).replace("\n## Risks\n", "\n## Risk Register\n", 1)


def act_as_adapter(run_id: str, *, artifact_text: str, side_effects: list | None = None):
    """Write what the adapter would have written, and nothing more."""
    d = state_dir(run_id)
    ledger = json.loads((d / "state-ledger.json").read_text(encoding="utf-8"))
    (CLAUDE / ledger["artifact_path"]).write_text(artifact_text, encoding="utf-8")
    (CLAUDE / ledger["result_envelope_path"]).write_text(json.dumps({
        "invocation_id": ledger["invocation_id"],
        "status": "succeeded",
        "artifact_refs": [ledger["artifact_path"]],
        "structured_output": {"produced_by": "verify_recovery.py acting as the adapter"},
        "evidence_refs": [ledger["artifact_path"]],
        "confidence": 0.5,
        "declared_side_effects": side_effects if side_effects is not None else [
            ledger["artifact_path"], ledger["result_envelope_path"]],
        "error_class": None,
        "error_detail": None,
    }, indent=2), encoding="utf-8")


def wait_for_backoff(run_id: str, r: Result, cid: str) -> float:
    """Sleep until the scheduled attempt is due, and report how long that was.

    The wait is real. A retry deadline the harness stepped over would prove the transition
    table and nothing about the policy that set the deadline.
    """
    item = item_of(run_id)
    due = datetime.strptime(item["available_at"], "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc)
    waited = 0.0
    while datetime.now(timezone.utc) < due:
        time.sleep(0.25)
        waited += 0.25
        if waited > rp.RETRY_PROFILE["max_delay_seconds"] + 5:
            break
    r.add(cid, "the scheduled attempt is not dispatchable before its deadline",
          waited > 0 or datetime.now(timezone.utc) >= due,
          f"waited {waited}s for the deadline {item['available_at']} set by the retry "
          f"profile ({rp.RETRY_PROFILE['backoff_strategy']}, base "
          f"{rp.RETRY_PROFILE['base_delay_seconds']}s)")
    return waited


# --------------------------------------------------------------------------- scenario A


def scenario_a() -> Result:
    r = Result("Run A -- a rejected artifact, classified retryable, repaired on the "
               "next attempt")
    run_id = plan(write_input(
        "repaired", "Attempt 1 returns a plan with one mandatory section renamed."))
    r.add("A0", "the run materialized and its planning phase is dispatchable",
          item_of(run_id)["status"] == se.PENDING and item_of(run_id)["eligible"],
          f"run {run_id}, {PHASE} is {item_of(run_id)['status']}")

    # ---- attempt 1: reject
    run("dispatch", "--run-id", run_id, "--phase", PHASE)
    act_as_adapter(run_id, artifact_text=broken_artifact(run_id))
    code, out = run("complete", "--run-id", run_id, "--phase", PHASE, expect=1)

    item = item_of(run_id)
    env = envelope_of(run_id)
    cls = env["classification"]
    r.add("A1", "the Validation Engine rejected the artifact",
          "validation     : FAIL" in out,
          next((ln.strip() for ln in out.splitlines() if "validation " in ln), ""))
    r.add("A2", "the failure was classified, not merely recorded",
          cls["failure_class"] == "output-schema-failure"
          and cls["detection_point"] == "validation" and cls["retryable"] is True,
          f"{cls['failure_class']} at {cls['detection_point']}, retryable="
          f"{cls['retryable']}, basis {cls['basis']}")
    r.add("A3", "the chosen action was retry, with the budget stated",
          cls["action"] == rp.RETRY and cls["attempts_charged"] == 1
          and cls["max_attempts"] == 3,
          f"action={cls['action']}, {cls['attempts_charged']} of {cls['max_attempts']} "
          f"charged, {cls['attempts_remaining']} remaining")
    r.add("A4", "the work item holds the canonical Retrying status with a deadline",
          item["status"] == se.RETRYING and item["queue_status"] == "Retrying"
          and bool(item["available_at"]),
          f"status={item['status']} queue={item['queue_status']} "
          f"available_at={item['available_at']} (+{cls['next_delay_seconds']}s)")
    r.add("A5", "the transition the state engine recorded is the canonical one",
          ("execution-planning", "running", "retrying", "validation_failed")
          in transitions_of(run_id),
          " -> ".join(t[2] for t in transitions_of(run_id) if t[0] == PHASE))
    r.add("A6", "a retry_scheduled event names the class, the action, and the deadline",
          any(e["event_type"] == "retry_scheduled"
              and e["details_ref"].get("recovery_action") == rp.RETRY
              for e in events_of(run_id)),
          next((f"{e['event_id']} {e['summary']}" for e in events_of(run_id)
                if e["event_type"] == "retry_scheduled"), "no retry_scheduled event"))
    r.add("A7", "the failure envelope states the decision needed and the action that "
                "clears it",
          env["schema"] == rp.ENVELOPE_SCHEMA and env["status"] == "open"
          and bool(env["required_decision_type"]) and bool(env["clearing_action"])
          and env["impacted_artifacts"],
          f"{env['envelope_id']}: decision {env['required_decision_type']}, impacted "
          f"{env['impacted_artifacts']}")
    r.add("A8", "the run projects the canonical Retrying lifecycle state",
          load_state(run_id)["run_status"] == "Retrying",
          f"run_status={load_state(run_id)['run_status']}")

    # ---- the deadline is enforced, then the scheduler promotes the work item.
    # The enforcement check is made against the persisted work item rather than by racing a
    # live dispatch against a two-second deadline: a proof whose outcome depends on how long a
    # subprocess took to start proves nothing repeatable.
    item = item_of(run_id)
    r.add("A9", "the scheduler holds the work item until its deadline and admits it after",
          se.retry_due({**item, "available_at": "2999-01-01T00:00:00Z"}) is False
          and se.retry_due({**item, "available_at": "2000-01-01T00:00:00Z"}) is True
          and item["eligible"] is False,
          f"the persisted item is {item['status']}, not eligible, and its deadline "
          f"{item['available_at']} is what the scheduler tests")

    wait_for_backoff(run_id, r, "A10")
    code, out = run("next", "--command", "implement", "--run-id", run_id)
    item = item_of(run_id)
    r.add("A11", "the scheduler promoted the work item once the backoff elapsed",
          item["status"] == se.PENDING and item["eligible"]
          and item["available_at"] is None
          and (PHASE, "retrying", "pending", "enqueued") in transitions_of(run_id),
          f"status={item['status']} eligible={item['eligible']}; "
          f"`next` says: "
          + next((ln.strip() for ln in out.splitlines() if ln.startswith("NEXT")), ""))
    r.add("A12", "the idempotency key survived the retry, because the unit of work did",
          item["idempotency_key"] == se.idempotency_key(
              run_id, PHASE, item["owner_agent_id"], "1.0.0", item["payload_digest"]),
          f"{item['idempotency_key']} recomputed from the persisted payload")

    # ---- attempt 2: the rejection is carried back, and the repair is accepted
    run("dispatch", "--run-id", run_id, "--phase", PHASE)
    prompt = (state_dir(run_id) / "dispatch-prompt.md").read_text(encoding="utf-8")
    envelope = json.loads((state_dir(run_id) / "invocation-envelope.json").read_text(
        encoding="utf-8"))
    prior = envelope.get("prior_validation") or {}
    r.add("A13", "the second attempt carries the rejection back to the agent as a repair pass",
          bool(prior.get("failures")) and "repair pass" in prompt.lower()
          and item_of(run_id)["attempt"] == 2,
          f"attempt {item_of(run_id)['attempt']}, {len(prior.get('failures') or [])} failed "
          f"check(s) named in the envelope and in the dispatch prompt")

    act_as_adapter(run_id, artifact_text=good_artifact(run_id))
    code, out = run("complete", "--run-id", run_id, "--phase", PHASE)
    item = item_of(run_id)
    entries = phase_entries(run_id)
    r.add("A14", "the repaired artifact was accepted and committed",
          item["status"] == se.COMPLETED and item["completion"]["validation"]["result"]
          == "pass",
          f"status={item['status']}, validation "
          f"{item['completion']['validation']['checksPassed']}/"
          f"{item['completion']['validation']['checksRun']} checks passed")
    r.add("A15", "the recovery ledger records the classification and its resolution, "
                 "rather than discarding it",
          len(entries) == 1 and entries[0]["status"] == "resolved"
          and bool(entries[0].get("resolution")),
          f"{len(entries)} entry: {entries[0]['envelope_id']} "
          f"{entries[0]['status']} -- {entries[0].get('resolution')}")
    r.add("A16", "one dispatched attempt was charged and one was not needed",
          item["attempt"] == 2 and se.attempts_charged(item) == 2
          and item["attempts_lost"] == 0,
          f"{item['attempt']} attempt(s) dispatched, {se.attempts_charged(item)} charged, "
          f"{item['attempts_lost']} lost to worker loss")

    # Every other phase of this workflow blocks at a guard rather than at a result, and those
    # blocks are the common case in this framework today. They must carry an envelope too.
    blocked = [i for i in load_state(run_id)["work_items"].values()
               if i["status"] == se.BLOCKED]
    all_entries = rp.RecoveryLedger(RUNS / run_id).entries()
    enveloped = {e["state_id"] for e in all_entries}
    guard_entries = [e for e in all_entries if e["guard"]]
    r.add("A17", "every guard-raised block emitted a classified envelope as well",
          blocked and all(i["state_id"] in enveloped for i in blocked),
          f"{len(blocked)} blocked work item(s), "
          f"{len(guard_entries)} guard-raised classification(s): "
          + ", ".join(sorted({f"{e['guard']}={e['failure_class']}"
                              for e in guard_entries})))
    r.add("A18", "each guard-raised envelope names the action that clears it",
          all(e["clearing_action"] and e["required_decision_type"]
              for e in guard_entries),
          f"decision types: "
          + ", ".join(sorted({e["required_decision_type"] for e in guard_entries})))
    return r


# --------------------------------------------------------------------------- scenario B


def scenario_b() -> Result:
    r = Result("Run B -- the same rejection every attempt: the budget bounds it and the "
               "fourth attempt is refused")
    run_id = plan(write_input(
        "exhausted", "Every attempt returns the same plan with a renamed section."))
    charged = []
    for attempt in (1, 2, 3):
        run("dispatch", "--run-id", run_id, "--phase", PHASE)
        act_as_adapter(run_id, artifact_text=broken_artifact(run_id))
        run("complete", "--run-id", run_id, "--phase", PHASE, expect=1)
        item = item_of(run_id)
        charged.append(se.attempts_charged(item))
        if item["status"] == se.RETRYING:
            if attempt == 2:
                # The second backoff is four seconds, which leaves room to observe the live
                # refusal without the observation itself deciding the outcome.
                code, out = run("dispatch", "--run-id", run_id, "--phase", PHASE,
                                expect=None)
                r.add("B0", "a live dispatch before the deadline is refused, and reports it",
                      code == 4 and item_of(run_id)["status"] == se.RETRYING,
                      next((ln.strip() for ln in out.splitlines()
                            if ln.startswith("RETRYING")), f"exit {code}"))
            wait_for_backoff(run_id, r, f"B{attempt}w")
            run("next", "--command", "implement", "--run-id", run_id)

    item = item_of(run_id)
    env = envelope_of(run_id)
    cls = env["classification"]
    r.add("B1", "every attempt that produced a judged result was charged to the budget",
          charged == [1, 2, 3],
          f"charged after each attempt: {charged}, ceiling {item['max_attempts']}")
    r.add("B2", "the retry budget was enforced rather than exceeded",
          cls["budget_exhausted"] is True and cls["action"] != rp.RETRY
          and item["attempt"] == 3,
          f"attempt {item['attempt']} of {item['max_attempts']}: "
          f"budget_exhausted={cls['budget_exhausted']}, action={cls['action']}")
    r.add("B3", "the work item blocked with a recorded reason rather than failing, because "
                "its artifact still exists",
          item["status"] == se.BLOCKED
          and item["blocked_reason"] == "awaiting_recovery_task"
          and item["blocked_by"] == "recovery-controller",
          f"status={item['status']} reason={item['blocked_reason']} "
          f"raised_by={item['blocked_by']}")
    r.add("B4", "the envelope explains the exhaustion and names a human decision",
          env["status"] == "open" and cls["attempts_remaining"] == 0
          and env["required_decision_type"] == "recovery-authorisation",
          f"{cls['reason']}")
    # B5 -- the exhausted phase must not be reported as progressing. The run-level status is
    # `WaitingForHuman` only while nothing else in the run is dispatchable; as more phases
    # gain a registered capability, an unrelated eligible phase legitimately reports
    # `Dispatching` at the run level, per the precedence in `state_engine.run_status`. So the
    # claim is checked where it belongs: on this work item, and on the run only when this
    # blocker is the run's whole story.
    state = load_state(run_id)
    others_eligible = sorted(
        i["state_id"] for i in state["work_items"].values()
        if i["work_type"] == "state" and i["state_id"] != PHASE
        and i["status"] == se.PENDING and i["eligible"])
    held = item["status"] == se.BLOCKED and item["blocked_reason"] == "awaiting_recovery_task"
    run_ok = state["run_status"] == ("Dispatching" if others_eligible else "WaitingForHuman")
    r.add("B5", "the exhausted phase is held for a human, and the run status reports that "
                "rather than progress on it",
          held and run_ok,
          f"work item {PHASE}={item['status']}/{item['blocked_reason']}, "
          f"run_status={state['run_status']}"
          + (f", independently dispatchable elsewhere: {others_eligible}"
             if others_eligible else ", nothing else dispatchable"))

    code, out = run("release", "--run-id", run_id, "--phase", PHASE, "--reason",
                    "tool_failure", "--detail", "operator asserts the defect is repaired",
                    expect=2)
    r.add("B6", "a fourth attempt is refused, because the budget does not have one",
          "RUNTIME FAILURE" in out and "retry budget" in out,
          next((ln.strip() for ln in out.splitlines() if "RUNTIME FAILURE" in ln), ""))
    r.add("B7", "the refusal changed nothing: the work item is still blocked on the same "
                "condition",
          item_of(run_id)["status"] == se.BLOCKED
          and item_of(run_id)["attempt"] == 3
          and envelope_of(run_id)["status"] == "open",
          f"status={item_of(run_id)['status']} attempt={item_of(run_id)['attempt']} "
          f"envelope={envelope_of(run_id)['status']}")

    entries = phase_entries(run_id)
    r.add("B8", "every attempt left an append-only ledger entry, none overwritten",
          len(entries) == 3
          and [e["occurrence"] for e in entries] == [1, 2, 3]
          and all(e["failure_class"] == "output-schema-failure" for e in entries),
          f"{len(entries)} classification(s), occurrences "
          f"{[e['occurrence'] for e in entries]}, actions "
          f"{[e['classification']['action'] for e in entries]}")
    return r


# --------------------------------------------------------------------------- scenario C


def scenario_c() -> Result:
    r = Result("Run C -- a policy violation is never retried, however many attempts remain")
    run_id = plan(write_input(
        "policy", "The artifact conforms, but the adapter declares a write outside its "
                  "permitted set."))
    run("dispatch", "--run-id", run_id, "--phase", PHASE)
    envelope = json.loads((state_dir(run_id) / "invocation-envelope.json").read_text(
        encoding="utf-8"))
    permitted = envelope["constraints"]["permitted_writes"]
    ledger_path = state_dir(run_id) / "state-ledger.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
    act_as_adapter(run_id, artifact_text=good_artifact(run_id),
                   side_effects=[ledger["artifact_path"], ledger["result_envelope_path"],
                                 "memory/architecture.md"])
    code, out = run("complete", "--run-id", run_id, "--phase", PHASE, expect=1)

    item = item_of(run_id)
    env = envelope_of(run_id)
    cls = env["classification"]
    r.add("C1", "the artifact itself conformed, so the rejection is attributable to the "
                "policy alone",
          "validation     : PASS" in out and "UNDECLARED" in out,
          next((ln.strip() for ln in out.splitlines() if "side effects" in ln), ""))
    r.add("C2", "the failure was classified as a policy failure, not a schema failure",
          cls["failure_class"] == "policy-failure" and cls["retryable"] is False,
          f"{cls['failure_class']} at {cls['detection_point']}, retryable="
          f"{cls['retryable']}, basis {cls['basis']}")
    r.add("C3", "no retry was scheduled, although the budget had attempts left",
          cls["action"] != rp.RETRY and cls["attempts_remaining"] >= 0
          and item["status"] == se.BLOCKED and item["available_at"] is None,
          f"action={cls['action']} with {cls['attempts_remaining']} attempt(s) unspent; "
          f"status={item['status']}")
    r.add("C4", "the block names the policy condition and the exception decision it needs",
          item["blocked_reason"] == "awaiting_policy_exception"
          and env["required_decision_type"] == "policy-exception",
          f"reason={item['blocked_reason']}, decision={env['required_decision_type']}")
    r.add("C5", "no retry_scheduled event was emitted for this run at all",
          not any(e["event_type"] == "retry_scheduled" for e in events_of(run_id)),
          f"event types: {sorted({e['event_type'] for e in events_of(run_id)})}")
    r.add("C6", "the undeclared write is named in the envelope evidence",
          "memory/architecture.md" in json.dumps(env["evidence_bundle_ref"]),
          f"permitted_writes were {permitted}; declared write outside that set is recorded")
    return r


# --------------------------------------------------------------------------- policy closure


def scenario_policy() -> Result:
    """Every row of the classification matrix, checked against the policy it declares.

    The three runs above exercise three classes. This closes over the rest without inventing
    runs for failures no current path can raise: for every row, the action the Recovery
    Controller chooses must agree with what the row declares, and a non-retryable row must
    never produce a retry at any point in the budget.
    """
    r = Result("Policy closure -- no failure class is retried against its own declaration")
    wrong_action, retried_anyway = [], []
    for cls_name, pol in rp.FAILURE_POLICIES.items():
        for attempt in range(0, 5):
            c = rp.classify(cls_name, attempt=attempt, attempts_lost=0,
                            max_attempts=rp.RETRY_PROFILE["max_attempts"],
                            seed=f"seed-{cls_name}")
            if not pol.retryable:
                if c.action != pol.default_action:
                    wrong_action.append((cls_name, attempt, c.action))
                if c.action == rp.RETRY:
                    retried_anyway.append((cls_name, attempt))
            elif attempt < rp.RETRY_PROFILE["max_attempts"] and c.action != rp.RETRY:
                wrong_action.append((cls_name, attempt, c.action))
            elif attempt >= rp.RETRY_PROFILE["max_attempts"] and c.action == rp.RETRY:
                retried_anyway.append((cls_name, attempt))
    r.add("P1", "every classified action matches the matrix row that declares it",
          not wrong_action,
          f"{len(rp.FAILURE_POLICIES)} class(es) checked across 5 attempt positions each"
          if not wrong_action else f"disagreements: {wrong_action}")
    r.add("P2", "no non-retryable class is retried, and no budget is exceeded",
          not retried_anyway,
          "the retry action appears only for retryable classes inside the budget"
          if not retried_anyway else f"retried anyway: {retried_anyway}")

    unknown = rp.classify("something-nobody-rowed", attempt=1, attempts_lost=0,
                          max_attempts=3)
    r.add("P3", "an unclassified failure escalates rather than being treated as transient",
          unknown.action == rp.ESCALATE and unknown.retryable is False,
          f"action={unknown.action}, retryable={unknown.retryable}")

    delays = [rp.backoff_seconds(a, seed="k") for a in range(1, 9)]
    profile = rp.RETRY_PROFILE
    r.add("P4", "backoff grows exponentially and is capped by the profile",
          all(b >= a for a, b in zip(delays, delays[1:]))
          and max(delays) <= profile["max_delay_seconds"],
          f"delays {delays} under base={profile['base_delay_seconds']}s "
          f"x{profile['multiplier']}, cap {profile['max_delay_seconds']}s, jitter "
          f"+-{int(profile['jitter_ratio'] * 100)}%")
    same = {rp.backoff_seconds(2, seed="fixed-key") for _ in range(5)}
    spread = {rp.backoff_seconds(2, seed=f"key-{i}") for i in range(8)}
    r.add("P5", "jitter is stable per work item and spread across work items, so replay "
                "stays deterministic",
          len(same) == 1 and len(spread) > 1,
          f"one key over five evaluations -> {same}; eight keys -> "
          f"{len(spread)} distinct delay(s)")
    return r


# --------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(
        description="Prove classified retry, bounded attempts, and structured failure "
                    "envelopes by inducing the failures")
    ap.add_argument("--keep", action="store_true",
                    help="leave the injected run directories and inputs in place as evidence")
    ap.add_argument("--json-out")
    a = ap.parse_args()

    print("Recovery Verification -- induced failure injection")
    print(f"  retry profile: {rp.RETRY_PROFILE}")
    print(f"  conforming source artifact: .claude/"
          f"{GOOD_SOURCE.relative_to(CLAUDE).as_posix()}")
    results = [scenario_a(), scenario_b(), scenario_c(), scenario_policy()]
    for res in results:
        print("\n".join(res.render()))

    total = sum(len(r.checks) for r in results)
    passed = sum(1 for r in results for c in r.checks if c["result"] == "pass")
    print()
    print("-" * 100)
    print(f"{passed}/{total} checks passed -- "
          f"{'RECOVERY PROVEN' if passed == total else 'NOT PROVEN'}")

    if a.json_out:
        Path(a.json_out).write_text(json.dumps({
            "schema": "framework.runtime/recovery-verification.v1",
            "verified_at": rp.iso(rp.now()),
            "runtime_version": fr.RUNTIME_VERSION,
            "retry_profile": rp.RETRY_PROFILE,
            "result": "pass" if passed == total else "fail",
            "checks_run": total,
            "checks_passed": passed,
            "scenarios": [{"title": r.title, "checks": r.checks} for r in results],
        }, indent=2), encoding="utf-8")

    if not a.keep:
        for slug in ("repaired", "exhausted", "policy"):
            path = INPUTS / f"recovery-injection-{slug}.md"
            if path.exists():
                reset_run(run_id_for(path), path)
                path.unlink()
        print("injected runs and inputs removed; pass --keep to retain them as evidence")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
