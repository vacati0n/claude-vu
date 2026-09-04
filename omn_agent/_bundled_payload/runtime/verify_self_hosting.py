#!/usr/bin/env python3
"""Executable proof of the self-hosting operating mode.

Three questions, and the framework answers each about itself.

**Does the profile route?** `config/self-hosting-profile.md` claims that every framework-internal
change resolves to exactly one command. `S1` to `S3` resolve every routing row through the same
registries the runtime gateway reads, and probe every Scope Rule for reachability and precedence.
A profile row naming an unroutable command fails here rather than at execution time.

**Is the evidence requirement enforceable?** `S4` and `S5` assert that the change-proposal
contract is registered — template record, registered validator, importable module — and that the
release checklist parses, names owners the framework actually carries, and names commands that
exist.

**Did it actually happen?** `S6` to `S8` are the ones that cannot be satisfied by writing
documents. Every change proposal under `proposals/` is validated by its own validator; the run
each names is re-read and checked against the profile's Completion Rule, phase by phase; and no
framework run may exist inside the self-hosted window without a proposal accounting for it. That
last check is what makes "self-hosting mode" a state rather than a claim: an ad hoc run breaks it.

`S9` and `S10` are asked only when asked for. `S9` (`--mode-evidence`) is the mode-level criterion:
two or more consecutive framework changes, each carried by its own run. It is deliberately not part
of the default run, because every framework change must pass this verifier as release checklist item
`FR-05`, and the first change under a new profile cannot be preceded by a second one. `S10`
(`--release-checklist`) executes every command-mode item of the framework release checklist.

    python .claude/runtime/verify_self_hosting.py
    python .claude/runtime/verify_self_hosting.py --mode-evidence      # also asserts S9
    python .claude/runtime/verify_self_hosting.py --release-checklist  # also runs FR-nn commands
    python .claude/runtime/verify_self_hosting.py --json-out <path>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import framework_runtime as fr  # noqa: E402
import self_hosting as sh  # noqa: E402

CLAUDE = fr.CLAUDE
REPO = CLAUDE.parent
PROPOSAL_ARTIFACT = "framework-change-proposal.md"


class Report:
    def __init__(self):
        self.checks = []

    def add(self, cid, description, ok, detail=""):
        self.checks.append({"id": cid, "description": description,
                            "result": "pass" if ok else "fail", "detail": detail})

    @property
    def passed(self):
        return all(c["result"] == "pass" for c in self.checks)


# --------------------------------------------------------------------------- helpers


def probe_path(pattern: str) -> str:
    """A representative path for one Scope Rule pattern, so the rule can be probed."""
    pat = pattern.replace("\\", "/")
    return pat[:-3] + "/probe-artifact.md" if pat.endswith("/**") else pat


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def proposal_meta(path: Path) -> dict:
    """The proposal's metadata block, read without validating it."""
    import re

    import yaml
    m = re.search(r"```yaml\s*\n(.*?)\n```", path.read_text(encoding="utf-8"), re.S)
    if not m:
        return {}
    return (yaml.safe_load(m.group(1)) or {}).get("frameworkChangeProposal", {}) or {}


def _phase_status_as_of(run_dir: Path, items: dict, at: str | None) -> dict:
    """Per-phase status and blocked reason as of `at`, from append-only run records.

    `GD-001` in `config/self-hosting-profile.md` makes the Completion Rule a judgement about
    the run as its change was recorded, not about the run as the framework has since made it.
    A phase whose block cleared because capability arrived later did not stop being a blocked
    phase at the moment the change was carried, so the transition log decides, and the
    recovery ledger supplies the reason the block carried.
    """
    if not at:
        return {k: dict(v) for k, v in items.items()}
    state = read_json(run_dir / "state.json")
    out = {k: {"status": None, "blocked_reason": None} for k in items}
    for t in sorted(state.get("transitions") or [], key=lambda x: x.get("seq", 0)):
        if str(t.get("at") or "") > at:
            break
        sid = t.get("state_id")
        if sid in out:
            out[sid]["status"] = t.get("to")
            if t.get("to") != "blocked":
                out[sid]["blocked_reason"] = None
    ledger = read_json(run_dir / "recovery-ledger.json")
    entries = ledger if isinstance(ledger, list) else (ledger.get("entries") or [])
    for e in sorted(entries, key=lambda x: str(x.get("detected_at") or "")):
        sid = e.get("state_id")
        if sid in out and str(e.get("detected_at") or "") <= at                 and out[sid]["status"] == "blocked" and e.get("blocked_reason"):
            out[sid]["blocked_reason"] = e["blocked_reason"]
    for sid, v in out.items():
        if v["status"] is None:
            v["status"] = (items.get(sid) or {}).get("status")
            v["blocked_reason"] = (items.get(sid) or {}).get("blocked_reason")
    return out


def authoring_instant(path: Path) -> str | None:
    """The instant a proposal's claims were true, per `GD-001`.

    Prefers the `Authoring Baseline` section a post-`GD-001` proposal declares. Falls back to
    the `Authored on` date every proposal has carried since the template existed, taken at end
    of day so a same-day transition counts as part of what was recorded.
    """
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^- Authored at:\s*(\S+)\s*$", text, re.M)
    if m:
        return m.group(1)
    m = re.search(r"^- Authored on:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    return m.group(1) + "T23:59:59Z" if m else None


def completion_rule(run_id: str, routed_command: str, as_of: str | None = None) -> dict:
    """Decide `C-2` to `C-5` of the profile's Completion Rule for one run.

    `as_of` is the instant the change was recorded. Supplied, the rule is decided against the
    run as it stood then, per `GD-001`; omitted, against the run as it stands now.
    """
    run_dir = fr.RUNS / run_id
    request = read_json(run_dir / "execution-request.json")
    state = read_json(run_dir / "state.json")
    items = {k: v for k, v in (state.get("work_items") or {}).items()
             if v.get("work_type") == "state"}
    items = _phase_status_as_of(run_dir, items, as_of)

    executed, blocked, unaccounted, unvalidated = [], [], [], []
    for phase, item in items.items():
        status = str(item.get("status") or "")
        if status == "completed":
            executed.append(phase)
            vr = read_json(run_dir / "states" / phase / "validation-report.json")
            if str(vr.get("result", "")).lower() != "pass":
                unvalidated.append(f"{phase}: validation-report result="
                                   f"{vr.get('result')!r}")
        elif status == "blocked":
            if item.get("blocked_reason"):
                blocked.append(phase)
            else:
                unaccounted.append(f"{phase}: blocked with no recorded reason")
        else:
            unaccounted.append(f"{phase}: status={status!r}")

    return {
        "run_id": run_id,
        "C-2": bool(request) and request.get("command_id") == routed_command,
        "C-3": bool(items) and not unaccounted,
        "C-4": not unvalidated,
        "C-5": (run_dir / "completion-package.md").exists(),
        "command_id": request.get("command_id"),
        "workflow_id": request.get("workflow_id"),
        "submitted_at": request.get("submitted_at"),
        "phases": len(items),
        "executed": sorted(executed),
        "blocked": sorted(blocked),
        "unaccounted": unaccounted,
        "unvalidated": unvalidated,
    }


# --------------------------------------------------------------------------- main


def main():  # noqa: C901 - a verifier is a flat sequence of checks by design
    ap = argparse.ArgumentParser(description="Prove the self-hosting operating mode")
    ap.add_argument("--json-out")
    ap.add_argument("--mode-evidence", action="store_true",
                    help="also assert the mode-level criterion: two or more consecutive "
                         "framework changes recorded in self-hosting mode")
    ap.add_argument("--release-checklist", action="store_true",
                    help="also execute every command-mode item of the framework release checklist")
    a = ap.parse_args()

    r = Report()
    print("Self-Hosting Operating Mode Verification")
    print("-" * 100)

    # ------------------------------------------------------------------ S1 profile
    try:
        profile = sh.load_profile()
        r.add("S1", "the self-hosting command profile parses and declares one active profile",
              True,
              f"{profile['identity']['profile identifier']} v"
              f"{profile['identity']['version']}, {len(profile['scope'])} scope rule(s), "
              f"{len(profile['routing'])} routing row(s), {len(profile['evidence'])} evidence "
              f"row(s), {len(profile['completion'])} completion condition(s)")
    except (sh.ProfileError, fr.RuntimeError_) as exc:
        r.add("S1", "the self-hosting command profile parses and declares one active profile",
              False, str(exc))
        profile = None

    # ------------------------------------------------------------------ S2 routing resolves
    routes, routing_failures = {}, []
    if profile:
        for row in profile["routing"]:
            try:
                routes[row["change_class"]] = sh.resolve_route(row["change_class"], profile)
            except (sh.ProfileError, fr.RuntimeError_) as exc:
                routing_failures.append(f"{row['change_class']}: {exc}")
    r.add("S2", "every routing row resolves to an active command, its primary workflow, and a "
          "declared entry phase", bool(routes) and not routing_failures,
          "; ".join(f"{c} -> /{v['command']} -> {v['workflow']}/{v['entry_phase']}"
                    for c, v in routes.items()) if not routing_failures
          else f"{routing_failures}")

    # ------------------------------------------------------------------ S3 scope rules decide
    probes, scope_failures = [], []
    if profile:
        for rule in profile["scope"]:
            for pat in rule["patterns"]:
                p = probe_path(pat)
                d = sh.classify_path(p, profile)
                want_in = rule["decision"] == "in-scope"
                # An inclusion probe may be overridden by an exclusion, which is the precedence
                # the profile declares; what must never happen is an exclusion that does not bind.
                ok = d["rule"] == rule["rule"] if not want_in else (
                    d["rule"] == rule["rule"] or not d["in_scope"])
                probes.append({"rule": rule["rule"], "probe": p, "decided_by": d["rule"],
                               "in_scope": d["in_scope"]})
                if not ok:
                    scope_failures.append(
                        f"{rule['rule']} probe {p} decided by {d['rule']}")
        outside = sh.classify_path("src/service/handler.py", profile)
        if outside["in_scope"]:
            scope_failures.append("a path outside the framework classified as in-scope")
    r.add("S3", "every scope rule is reachable, exclusions take precedence, and a path outside "
          "the framework is out of scope", bool(probes) and not scope_failures,
          f"{len(probes)} probe(s) decided; exclusions bind" if not scope_failures
          else f"{scope_failures}")

    # ------------------------------------------------------------------ S4 contract registered
    reg_failures = []
    templates = fr.load_yaml("registry/templates.yaml").get("records") or []
    rec = next((t for t in templates if t["identifier"] == "framework-change-proposal"), None)
    if rec is None:
        reg_failures.append("no framework-change-proposal record in registry/templates.yaml")
    else:
        if rec.get("status") != "active":
            reg_failures.append(f"template record status is {rec.get('status')!r}")
        if not (CLAUDE / rec["specificationPath"]).exists():
            reg_failures.append(f"template specificationPath does not resolve: "
                                f"{rec['specificationPath']}")
    module = fr.VALIDATORS.get(PROPOSAL_ARTIFACT)
    if module is None:
        reg_failures.append(f"{PROPOSAL_ARTIFACT} has no entry in the VALIDATORS map")
    else:
        try:
            mod = __import__(module)
            if not callable(getattr(mod, "validate", None)):
                reg_failures.append(f"{module} exposes no validate()")
        except Exception as exc:  # noqa: BLE001
            reg_failures.append(f"{module} does not import ({exc})")
    r.add("S4", "the change-proposal contract is registered: template record, registered "
          "validator, importable module", not reg_failures,
          f"templates.yaml -> {rec['specificationPath']}; VALIDATORS[{PROPOSAL_ARTIFACT}] "
          f"-> {module}" if not reg_failures else f"{reg_failures}")

    # ------------------------------------------------------------------ S5 checklist
    items, checklist_failures = [], []
    try:
        items = sh.load_release_checklist()
    except (sh.ProfileError, fr.RuntimeError_) as exc:
        checklist_failures.append(str(exc))
    known_agents = {p.name[: -len(".agent.md")]
                    for p in (CLAUDE / "agents").glob("*.agent.md")}
    for it in items:
        if it["owner_role"] not in known_agents:
            checklist_failures.append(f"{it['id']}: owner {it['owner_role']!r} is not a "
                                      f"host-invocable agent")
        if it["mode"] == "command":
            script = next((t for t in it["verification"].split() if t.endswith(".py")), None)
            if script and not (REPO / script.replace("\\", "/")).exists():
                checklist_failures.append(f"{it['id']}: {script} does not exist")
    if items and not any(i["obligation"] == "mandatory" for i in items):
        checklist_failures.append("no mandatory item declared")
    r.add("S5", "the framework release checklist parses, and every item names a real owner and a "
          "runnable verification", bool(items) and not checklist_failures,
          f"{len(items)} item(s), "
          f"{sum(1 for i in items if i['obligation'] == 'mandatory')} mandatory, "
          f"{sum(1 for i in items if i['mode'] == 'command')} executable"
          if not checklist_failures else f"{checklist_failures}")

    # ------------------------------------------------------------------ S6 proposals validate
    found = sh.proposals()
    validations, proposal_failures = [], []
    validator = __import__(fr.VALIDATORS[PROPOSAL_ARTIFACT]) \
        if PROPOSAL_ARTIFACT in fr.VALIDATORS else None
    for path in found:
        if validator is None:
            break
        rep = validator.validate(path, None)
        d = rep.to_dict()
        meta = proposal_meta(path)
        validations.append({
            "proposal": path.relative_to(CLAUDE).as_posix(),
            "proposalId": meta.get("proposalId"),
            "changeClass": meta.get("changeClass"),
            "routedCommand": meta.get("routedCommand"),
            "runId": meta.get("runId"),
            "authoredOn": authoring_instant(path),
            "result": d["result"],
            "checksPassed": d["checksPassed"],
            "checksRun": d["checksRun"],
            "failed": [c["id"] for c in d["checks"] if c["result"] == "fail"],
        })
        if not rep.passed:
            proposal_failures.append(f"{path.name}: {validations[-1]['failed']}")
    r.add("S6", "every recorded framework change carries a change proposal that passes its own "
          "validator", bool(found) and not proposal_failures,
          f"{len(found)} proposal(s), all accepted: "
          + ", ".join(v["proposalId"] or "?" for v in validations)
          if found and not proposal_failures
          else f"{len(found)} proposal(s); failures: {proposal_failures}")

    # ------------------------------------------------------------------ S7 completion rule
    completions, completion_failures = [], []
    for v in validations:
        if not v["runId"]:
            completion_failures.append(f"{v['proposal']}: names no run")
            continue
        c = completion_rule(v["runId"], v["routedCommand"] or "", v.get("authoredOn"))
        completions.append(c)
        for cid in ("C-2", "C-3", "C-4", "C-5"):
            if not c[cid]:
                completion_failures.append(
                    f"{v['runId']} {cid}: "
                    + (c["unaccounted"] and str(c["unaccounted"]) or "")
                    + (c["unvalidated"] and str(c["unvalidated"]) or "")
                    or f"{v['runId']} {cid} not satisfied")
    r.add("S7", "every recorded change was carried by a run satisfying the profile's Completion "
          "Rule", bool(completions) and not completion_failures,
          "; ".join(f"{c['run_id']}: {len(c['executed'])} executed, {len(c['blocked'])} blocked "
                    f"with a reason, of {c['phases']}" for c in completions)
          if not completion_failures else f"{completion_failures}")

    # ------------------------------------------------------------------ S8 no ad hoc run
    accounted = {c["run_id"] for c in completions}
    window_start = min((c["submitted_at"] for c in completions if c["submitted_at"]),
                       default=None)
    unaccounted_runs = []
    if window_start:
        for req in sorted(fr.RUNS.glob("run-*/execution-request.json")):
            data = read_json(req)
            rid = data.get("run_id") or req.parent.name
            if rid in accounted:
                continue
            if str(data.get("submitted_at") or "") >= window_start:
                unaccounted_runs.append(f"{rid} ({data.get('submitted_at')})")
    r.add("S8", "no framework run inside the self-hosted window is unaccounted for by a change "
          "proposal", bool(window_start) and not unaccounted_runs,
          f"window opens {window_start}; {len(accounted)} run(s) accounted for, none unaccounted"
          if window_start and not unaccounted_runs
          else f"unaccounted: {unaccounted_runs}" if window_start else "no window: no proposal "
          "names a run")

    # ------------------------------------------------------------------ S9 mode evidence
    # Asked only under --mode-evidence. Whether *this* change was self-hosted is S1 to S8, and
    # every framework change must answer that. Whether the *operating mode* is established is a
    # different question with a different subject, and binding it into the per-change checklist
    # would make the first change under the profile unable to pass a checklist it must pass.
    if a.mode_evidence:
        runs_in_order = [c["run_id"] for c in
                         sorted(completions, key=lambda c: c["submitted_at"] or "")]
        distinct = len(set(runs_in_order))
        ordered = all(
            (completions[i]["submitted_at"] or "") <= (completions[i + 1]["submitted_at"] or "")
            for i in range(len(completions) - 1)) if len(completions) > 1 else False
        r.add("S9", "two or more framework changes are recorded consecutively in self-hosting "
              "mode, each carried by its own run", distinct >= 2 and ordered and not
              unaccounted_runs,
              f"{distinct} distinct run(s) in submission order: {' -> '.join(runs_in_order)}"
              if distinct >= 2 and ordered
              else f"{distinct} distinct run(s); ordered={ordered}")

    # ------------------------------------------------------------------ optional: FR-nn
    executed_items = []
    if a.release_checklist:
        print()
        print("Framework release checklist execution")
        for it in items:
            if it["mode"] != "command":
                executed_items.append({**it, "result": "inspection", "returncode": None})
                continue
            proc = subprocess.run(it["verification"], shell=True, cwd=REPO,
                                  capture_output=True, text=True)
            ok = proc.returncode == 0
            tail = (proc.stdout.strip().splitlines() or [""])[-1][:96]
            executed_items.append({**it, "result": "pass" if ok else "fail",
                                   "returncode": proc.returncode, "tail": tail})
            print(f"  [{'PASS' if ok else 'FAIL'}] {it['id']:<6} {it['obligation']:<9} {tail}")
        failed_mandatory = [i["id"] for i in executed_items
                            if i["obligation"] == "mandatory" and i["result"] == "fail"]
        r.add("S10", "every mandatory checklist item with a command passes",
              not failed_mandatory,
              f"{sum(1 for i in executed_items if i['result'] == 'pass')} executed item(s) "
              f"passed" if not failed_mandatory else f"failed: {failed_mandatory}")

    # ------------------------------------------------------------------ output
    print()
    for c in r.checks:
        print(f"[{'PASS' if c['result'] == 'pass' else 'FAIL'}] {c['id']:<3} {c['description']}")
        print(f"       {c['detail']}")

    if validations:
        print()
        print("Change proposals")
        print(f"  {'proposal':<22} {'class':<28} {'command':<12} {'run':<20} result")
        print("  " + "-" * 100)
        for v in validations:
            print(f"  {(v['proposalId'] or '?'):<22} {(v['changeClass'] or '?'):<28} "
                  f"{('/' + (v['routedCommand'] or '?')):<12} {(v['runId'] or '?'):<20} "
                  f"{v['result'].upper()} ({v['checksPassed']}/{v['checksRun']})")

    if completions:
        print()
        print("Completion Rule per run")
        for c in completions:
            print(f"  {c['run_id']}  C-2={c['C-2']} C-3={c['C-3']} C-4={c['C-4']} "
                  f"C-5={c['C-5']}  executed={c['executed']}")

    total = len(r.checks)
    passed = sum(1 for c in r.checks if c["result"] == "pass")
    print()
    print("-" * 100)
    print(f"{passed}/{total} checks passed -- "
          f"{'SELF-HOSTING' if r.passed else 'NOT SELF-HOSTING'}")

    if a.json_out:
        Path(a.json_out).write_text(json.dumps({
            "schema": "framework.runtime/self-hosting.v1",
            "runtime_version": fr.RUNTIME_VERSION,
            "profile": (profile or {}).get("identity"),
            "profile_digest": (profile or {}).get("source_digest"),
            "routes": routes,
            "scope_probes": probes,
            "checklist_items": items,
            "proposals": validations,
            "completions": completions,
            "checklist_execution": executed_items,
            "checks": r.checks,
            "result": "pass" if r.passed else "fail",
        }, indent=2), encoding="utf-8")
        print(f"machine record: {a.json_out}")

    return 0 if r.passed else 1


if __name__ == "__main__":
    sys.exit(main())
