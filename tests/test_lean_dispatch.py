"""Tests for the runtime 0.7.0 performance refactor: the task context, progressive module
loading, context-slice read hints, conditional skill dispatch, parallel groups, the dispatch
prompt's loading discipline, and the execution metrics.

These exercise `.claude/runtime/{framework_runtime,task_context,execution_metrics}.py`
directly against the real framework tree (registries, manifests, modules), in the same way
`tests/test_agent_input_contracts.py` does. Nothing here writes into `.claude/runs`.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import execution_metrics as em  # noqa: E402
import framework_runtime as fr  # noqa: E402
import state_engine as se  # noqa: E402
import task_context as tc  # noqa: E402

DESIGN = """```yaml
design:
  designId: X
```

## Metadata

- Feature or Change ID: X

## Objective

- Desired outcome: the export exists.

## Current-State Assumptions and Constraints

### 4.3 Constraints

| ID | Constraint | Source |
|---|---|---|
| C-001 | the repository abstraction stays the persistence boundary | architecture |

## Architecture and Component Design

### 5.1 Impacted Modules

| ID | Module | Impact type | Basis | Interfaces affected | Confidence |
|---|---|---|---|---|---|
| M-001 | `src/Orders/Export` | extension | S-001 | IExportService | high |

### 5.4 Decisions

| ID | Decision | Architecture-significant | Record |
|---|---|---|---|
| D-001 | Use the existing repository abstraction | yes | ADR |

## Risks and Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R-001 | large exports time out | medium | high | stream rows |

## Open Decisions and Escalations

| ID | Decision needed | Owner |
|---|---|---|
| Q-001 | CSV delimiter for locales | omn-product-owner |
"""

REPORT = """## Change Set

| ID | Path | Change Type | Purpose | Design Ref |
|---|---|---|---|---|
| `C-001` | `src/Orders/Export/CsvExporter.cs` | add | exporter | D-001 |
| `C-002` | `tests/Orders/CsvExporterTests.cs` | add | evidence | D-001 |

## Test Evidence

| ID | Test | Type | Covers | Command | Result |
|---|---|---|---|---|---|
| `T-001` | exports filtered rows | unit | `C-001` | dotnet test | pass |
"""


class TaskContextExtractionTestCase(unittest.TestCase):

    def test_extracts_identified_one_line_facts_from_design_tables(self):
        facts = tc.extract_facts("technical-design.md", DESIGN)
        self.assertIn("C-001: the repository abstraction stays the persistence boundary "
                      "| architecture", facts["constraints"])
        self.assertTrue(any(f.startswith("D-001: Use the existing repository abstraction")
                            for f in facts["decisions"]))
        self.assertTrue(any(f.startswith("M-001:") for f in
                            facts["repository_context"]["relevant_modules"]))
        self.assertTrue(any(f.startswith("R-001:") for f in facts["risks"]))
        self.assertTrue(any(f.startswith("Q-001:") for f in facts["open_questions"]))
        self.assertEqual(facts["objectives"], ["Desired outcome: the export exists."])

    def test_change_set_rows_become_changed_files_with_paths_first(self):
        facts = tc.extract_facts("implementation-report.md", REPORT)
        self.assertEqual(facts["changed_files"],
                         ["src/Orders/Export/CsvExporter.cs (add)",
                          "tests/Orders/CsvExporterTests.cs (add)"])
        self.assertTrue(any(f.startswith("T-001:") for f in
                            facts["validation_requirements"]["evidence"]))

    def test_cells_and_registers_are_capped(self):
        long_cell = "x" * 1000
        text = "## Risks\n\n| ID | Risk |\n|---|---|\n" + "\n".join(
            f"| R-{i:03d} | {long_cell} |" for i in range(200))
        facts = tc.extract_facts("technical-design.md", text)
        self.assertLessEqual(len(facts["risks"]), tc.ROWS_MAX)
        self.assertTrue(all(len(r) <= tc.CELL_MAX * 2 for r in facts["risks"]))

    def test_extraction_is_deterministic(self):
        self.assertEqual(tc.extract_facts("technical-design.md", DESIGN),
                         tc.extract_facts("technical-design.md", DESIGN))


class AffectedAreasAndSkillDispatchTestCase(unittest.TestCase):

    def setUp(self):
        self.records = fr.load_yaml("registry/skills.yaml")["records"]

    def test_triggers_are_found_with_evidence_and_declared_areas_join(self):
        areas = tc.derive_affected_areas(
            [("input:feature-request", "the export respects the user's read permission")],
            declared=["database"])
        self.assertTrue(areas["determinable"])
        self.assertIn("security", areas["triggered"])
        self.assertEqual(areas["triggered"]["security"][0]["term"], "permission")
        self.assertIn("database", areas["triggered"])
        self.assertIn("performance", areas["not_triggered"])

    def test_unknown_never_narrows(self):
        areas = tc.derive_affected_areas([("input:feature-request", "")])
        self.assertFalse(areas["determinable"])
        verdicts = tc.skill_dispatch("implementation", ["S03", "S06", "S08"], areas,
                                     self.records)
        self.assertTrue(all(v["status"] == "required" for v in verdicts))

    def test_domain_general_required_and_untriggered_domain_skill_not_triggered(self):
        areas = tc.derive_affected_areas([("input:feature-request", "rename a button label")])
        verdicts = {v["skillCode"]: v for v in
                    tc.skill_dispatch("implementation", ["S03", "S06", "S12"], areas,
                                      self.records)}
        self.assertEqual(verdicts["S03"]["status"], "required")
        self.assertEqual(verdicts["S12"]["status"], "required")
        self.assertEqual(verdicts["S06"]["status"], "not-triggered")
        self.assertEqual(verdicts["S06"]["specificationPath"],
                         "skills/database/database-engineering.md")

    def test_security_always_required_in_review_and_validation_phases(self):
        areas = tc.derive_affected_areas([("input:feature-request", "rename a button label")])
        for phase in ("quality-review", "regression-validation", "code-quality-review"):
            v = tc.skill_dispatch(phase, ["S09"], areas, self.records)[0]
            self.assertEqual(v["status"], "required", phase)
        v = tc.skill_dispatch("solution-design-and-risk-assessment", ["S09"], areas,
                              self.records)[0]
        self.assertEqual(v["status"], "not-triggered")


class ParallelGroupsTestCase(unittest.TestCase):

    def test_levels_follow_hard_edges_only(self):
        deps = {"a": [], "b": [{"state_id": "a", "kind": "soft"}],
                "c": [{"state_id": "b", "kind": "hard"}],
                "d": [{"state_id": "c", "kind": "hard"}]}
        self.assertEqual(tc.parallel_groups(deps, ["a", "b", "c", "d"]),
                         [["a", "b"], ["c"], ["d"]])

    def test_shipped_implement_feature_graph(self):
        cmd = fr.resolve_command("implement")
        wf = fr.resolve_workflow(cmd["primaryWorkflow"])
        rows = fr.parse_phase_model(wf["specificationPath"])
        deps = fr.derive_dependencies(rows, [])
        groups = tc.parallel_groups(deps, [r["phase"] for r in rows])
        # With no supplied inputs every edge is hard, so every group is one phase wide.
        self.assertEqual([len(g) for g in groups], [1] * len(rows))


class MultiPhaseRequiredPhasesTestCase(unittest.TestCase):
    """`verify_multi_phase.py` M6 derives its role chain from the routed Phase Model."""

    def _roles(self, workflow_id):
        import verify_multi_phase as vmp
        wf = fr.resolve_workflow(workflow_id)
        return vmp.required_phases(fr.parse_phase_model(wf["specificationPath"]))

    def test_implement_feature_keeps_its_historical_chain(self):
        self.assertEqual(self._roles("implement-feature"),
                         {"planning": "execution-planning",
                          "design": "solution-design-and-risk-assessment",
                          "delivery": "implementation"})

    def test_other_workflows_derive_their_own_chain(self):
        self.assertEqual(self._roles("fix-bug")["delivery"], "fix-implementation")
        self.assertEqual(self._roles("fix-bug")["design"], "root-cause-analysis")
        self.assertEqual(self._roles("refactor")["delivery"], "refactor-implementation")
        # No implementation phase: the workflow delivers its last phase.
        self.assertEqual(self._roles("review-pull-request")["delivery"], "merge-decision")
        # A single-phase workflow has only a delivery role.
        self.assertEqual(self._roles("code-quality-scan"), {"delivery": "repository-quality-scan"})


class ProgressiveLoadingTestCase(unittest.TestCase):

    def test_every_agent_splits_into_core_and_on_demand_by_role(self):
        for rec in fr.load_yaml("registry/agents.yaml")["records"]:
            if rec["status"] != "active" or not rec["specificationPath"].endswith("manifest.yaml"):
                continue
            agent = fr.load_agent(rec["identifier"])
            profile = fr.load_profile(agent)
            core_names = sorted(Path(p).name for p in profile["core"])
            self.assertEqual(core_names, ["output.md", "quality.md", "reasoning.md", "system.md"],
                             rec["identifier"])
            od = sorted(Path(m["path"]).name for m in profile["on_demand"])
            self.assertEqual(od, ["examples.md", "execution.md", "identity.md"], rec["identifier"])
            self.assertTrue(all(m["load_when"] for m in profile["on_demand"]))
            self.assertLess(profile["core_bytes"], profile["full_bytes"])
            self.assertEqual(agent["contract_checks"]["result"], "pass", rec["identifier"])
            self.assertEqual(agent["contract_checks"]["contract_sections"]["missing"], [])
            # The load order itself is untouched: the manifest stays the authority.
            self.assertEqual(set(profile["core"]) | {m["path"] for m in profile["on_demand"]},
                             set(agent["load_order"] and [m["path"] for m in agent["modules"]]))

    def test_full_profile_puts_every_module_in_core(self):
        agent = fr.load_agent("planner")
        profile = fr.load_profile(agent, "full")
        self.assertEqual(profile["on_demand"], [])
        self.assertEqual(len(profile["core"]), len(agent["modules"]))


class SliceReadHintsTestCase(unittest.TestCase):

    def test_hints_by_member_kind(self):
        wf = "workflows/implement-feature.md"
        skill_status = {"S06": {"specificationPath": "skills/database/database-engineering.md",
                                "status": "not-triggered", "basis": "not affected"}}
        self.assertEqual(fr.slice_read_hint("registry/agents.yaml", "implementation", wf, {})[0],
                         "runtime-resolved")
        self.assertEqual(fr.slice_read_hint("templates/implementation-report.md",
                                            "implementation", wf, {})[0], "required")
        self.assertEqual(fr.slice_read_hint(wf, "implementation", wf, {})[0], "on-demand")
        self.assertEqual(fr.slice_read_hint("runtime/README.md", "implementation", wf, {})[0],
                         "on-demand")
        self.assertEqual(fr.slice_read_hint("skills/database/database-engineering.md",
                                            "implementation", wf, skill_status)[0], "on-demand")
        self.assertEqual(fr.slice_read_hint("skills/agent-skill-matrix.md", "implementation",
                                            wf, {})[0], "runtime-resolved")
        # The planner cites capability identifiers and skill codes, so it reads the catalogues.
        self.assertEqual(fr.slice_read_hint("registry/skills.yaml", "execution-planning", wf,
                                            {})[0], "required")
        self.assertEqual(fr.slice_read_hint("workflows/workflow-gate-matrix.md",
                                            "scope-and-acceptance", wf, {})[0], "required")

    def test_slice_dedupes_members_and_records_bytes(self):
        sl = fr.build_context_slice("scope-and-acceptance",
                                    [{"type": "feature-request", "text": "x",
                                      "reference": "r", "source_file": "s"}],
                                    "workflows/implement-feature.md", {})
        paths = [m["path"] for m in sl["members"]]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertIn("workflows/workflow-gate-matrix.md", paths)
        self.assertGreater(sl["bytes_total"], sl["bytes_required"])
        self.assertTrue(all(m["read"] in ("required", "on-demand", "runtime-resolved")
                            for m in sl["members"]))


class DispatchPromptTestCase(unittest.TestCase):

    def _envelope(self, **over):
        agent = fr.load_agent("omn-dev-1-implement")
        env = {
            "invocation_id": "inv-x-04-001", "run_id": "run-x", "work_item_id": "run-x::implementation",
            "idempotency_key": "sha256:k", "state_id": "implementation", "phase_index": 4,
            "agent_id": "omn-dev-1-implement", "agent_version": "1.0.0",
            "host_registration": "agents/omn-dev-1-implement.agent.md",
            "capability_bindings": {"manifest": agent["manifest_path"],
                                    "load_order": [m["path"] for m in agent["modules"]],
                                    "load_profile": fr.load_profile(agent),
                                    "contract_checks": agent["contract_checks"]},
            "skill_dispatch": [{"skillCode": "S06", "displayName": "Database Engineering",
                                "status": "not-triggered", "source": "phase-mandatory",
                                "basis": "area database is not affected"}],
            "input_contract": {"supplied": [{"type": "technical-design",
                                             "reference": "runs/run-x/states/d/artifacts/technical-design.md",
                                             "source_file": "s"}]},
            "upstream_artifacts": [{"type": "technical-design", "produced_by": "d",
                                    "reference": "runs/run-x/states/d/artifacts/technical-design.md",
                                    "artifact": "technical-design.md", "bytes": 70000,
                                    "sections": tc.sections_of_interest("technical-design.md")}],
            "task_context": {"path": "runs/run-x/task-context.yaml", "digest": "sha256:t",
                             "bytes": 4000, "affected_areas": {"determinable": True,
                                                                "triggered": ["security"],
                                                                "declared": []}},
            "parallel_group": {"phases": ["implementation"], "dispatchable_now": [],
                               "dispatchable_early": {}, "this_phase_forgoes": []},
            "context_slice": {"members": [
                {"path": "templates/implementation-report.md", "read": "required",
                 "read_reason": "template"},
                {"path": "runtime/README.md", "read": "on-demand", "read_reason": "surface"},
                {"path": "registry/agents.yaml", "read": "runtime-resolved", "read_reason": "r"}],
                "read_required": ["templates/implementation-report.md"],
                "runtime_resolved": ["registry/agents.yaml"]},
            "constraints": {"permitted_writes": ["runs/run-x/states/implementation/artifacts/implementation-report.md"],
                            "prohibited": ["command execution"]},
            "expected_output_schema": {"artifact": "implementation-report.md",
                                       "artifact_path": "runs/run-x/states/implementation/artifacts/implementation-report.md",
                                       "template_ref": "templates/implementation-report.md",
                                       "contract_ref": "agents/omn-dev-1-implement/output.md",
                                       "quality_ref": "agents/omn-dev-1-implement/quality.md",
                                       "result_envelope_path": "runs/run-x/states/implementation/result-envelope.json",
                                       "conditional_artifacts": []},
            "prior_validation": None, "prior_rejection": None,
        }
        env.update(over)
        return env

    def _chain(self):
        return {"command": {"identifier": "implement"},
                "workflow": {"identifier": "implement-feature", "version": "1.0.0"}}

    def test_prompt_states_the_loading_discipline(self):
        prompt = fr.build_dispatch_prompt(self._envelope(), self._chain())
        self.assertIn("Read first: the task context", prompt)
        self.assertIn("task-context.yaml", prompt)
        self.assertIn("Read the core modules, in full", prompt)
        self.assertIn("agents/omn-dev-1-implement/system.md", prompt)
        self.assertIn("identity.md` (agent-contract) -- load before deciding", prompt)
        self.assertIn("Read first: Objective, Constraints, Impacted Modules", prompt)
        self.assertIn("`S06` | Database Engineering | `not-triggered`", prompt)
        self.assertIn("Runtime-resolved members are not yours to read", prompt)
        self.assertIn("Artifact economy", prompt)
        self.assertIn("do not re-read `identity.md` to repeat it", prompt)
        self.assertNotIn("Repair pass", prompt)
        self.assertNotIn("Rework pass", prompt)

    def test_repair_pass_names_the_minimal_module_subset(self):
        env = self._envelope(prior_validation={
            "attempt": 1, "report": "runs/run-x/states/implementation/validation-report.json",
            "result": "fail", "existing_artifacts": ["runs/run-x/states/implementation/artifacts/implementation-report.md"],
            "failures": [{"id": "I3", "severity": "Blocking", "quality_ref": "quality.md",
                          "requirement": "Change Set present", "detail": "missing"}]})
        prompt = fr.build_dispatch_prompt(env, self._chain())
        self.assertIn("## Repair pass", prompt)
        self.assertIn("Load\n`quality.md` and `output.md` first", prompt)

    def test_full_profile_prompt_defers_nothing(self):
        agent = fr.load_agent("omn-dev-1-implement")
        env = self._envelope()
        env["capability_bindings"]["load_profile"] = fr.load_profile(agent, "full")
        prompt = fr.build_dispatch_prompt(env, self._chain())
        self.assertIn("The load profile is `full`", prompt)
        self.assertIn("agents/omn-dev-1-implement/examples.md", prompt)


class ExecutionMetricsTestCase(unittest.TestCase):

    def test_budget_counts_core_and_required_only_under_progressive_rules(self):
        agent = fr.load_agent("planner")
        env = {
            "run_id": "run-x", "state_id": "execution-planning",
            "capability_bindings": {"manifest": agent["manifest_path"],
                                    "load_order": [m["path"] for m in agent["modules"]],
                                    "load_profile": fr.load_profile(agent)},
            "context_slice": {"members": [
                {"path": "registry/agents.yaml", "read": "runtime-resolved"},
                {"path": "templates/execution-plan.md", "read": "required"},
                {"path": "templates/execution-plan.md", "read": "required"}]},
            "input_contract": {"supplied": []}, "upstream_artifacts": [],
            "expected_output_schema": {"template_ref": "templates/execution-plan.md"},
            "host_registration": "agents/planner.agent.md",
        }
        b = em.estimate_dispatch_budget(env, fr.CLAUDE, tc.UPSTREAM_SECTIONS, 1000)
        self.assertLess(b["modules_core_bytes"], b["modules_full_bytes"])
        self.assertLess(b["slice_required_bytes"], b["slice_all_bytes"])
        self.assertEqual(b["task_context_bytes"], 1000)
        self.assertLess(b["progressive_estimate_bytes"], b["legacy_estimate_bytes"])
        self.assertGreater(b["savings_pct"], 0)

    def test_metrics_document_from_an_empty_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            run_dir = Path(tmp) / "run-t"
            run_dir.mkdir()
            store = se.StateStore.create(
                run_dir, run_id="run-t", command_id="implement",
                workflow_id="implement-feature", workflow_version="1.0.0",
                runtime_version=fr.RUNTIME_VERSION, input_digest="sha256:t", inputs=[])
            data = em.compute(run_dir, fr.CLAUDE, store=store, events=[])
            self.assertEqual(data["schema"], em.SCHEMA)
            self.assertEqual(data["agents_executed"]["invocations"], 0)
            self.assertEqual(data["tokens_or_context_estimate"]["savings_pct"], 0.0)
            lines = em.summary_lines(data)
            self.assertTrue(any("context estimate, progressive rules" in ln for ln in lines))
            em.write(run_dir, data)
            self.assertTrue((run_dir / em.FILENAME).exists())
            json.loads((run_dir / em.FILENAME).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
