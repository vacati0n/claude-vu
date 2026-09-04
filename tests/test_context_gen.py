"""Tests for dependency-map seeding, generation, and validation coverage.

Covers the ON-165 setup gap: `dependency-map.md` is a context-slice member the
runtime requires at dispatch time, so it must be seeded by install, derivable
by `omn-agent context generate dependency-map`, and its absence must be
reported by `validate`/`doctor` before any run can fail on it.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
import textwrap
import unittest
from pathlib import Path

from omn_agent import cli, context_gen
from omn_agent.common import ExitCode

from test_omn_agent import SOURCE_FILES

RUNTIME_WITH_SLICES = SOURCE_FILES["runtime/framework_runtime.py"] + textwrap.dedent('''
    CONTEXT_SLICE_BASE = [
        "registry/agents.yaml",
        "context/product-context.md",
    ]

    CONTEXT_SLICE_PHASE = {
        "scope-and-acceptance": [
            ("templates/scope-definition.md", "feature-request"),
        ],
        "root-cause-analysis": [
            "templates/scope-definition.md",
            "dependency-map.md",
        ],
    }
''')


class ContextGenTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-agent-ctxtest-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.source = self.tmp / "framework-src"
        for rel, content in SOURCE_FILES.items():
            p = self.source / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding="utf-8")
        (self.source / "runtime" / "framework_runtime.py").write_text(
            RUNTIME_WITH_SLICES, encoding="utf-8")
        self.repo = self.tmp / "repo"
        (self.repo / ".git").mkdir(parents=True)
        self.fw = self.repo / ".omn-agent"

    def run_cli(self, *argv) -> tuple[int, str]:
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main(list(argv))
        return code, out.getvalue()

    def install(self, *extra) -> tuple[int, str]:
        return self.run_cli("install", str(self.repo), "--source",
                            str(self.source), *extra)

    # ---- install seeding ----------------------------------------------------

    def test_install_seeds_dependency_map(self):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        dep = self.fw / "dependency-map.md"
        self.assertTrue(dep.is_file())
        self.assertIn("# Dependency Map", dep.read_text(encoding="utf-8"))
        manifest = json.loads(
            (self.fw / "bootstrap" / "install-manifest.json").read_text())
        self.assertIn("dependency-map.md", manifest["seeds"])

    def test_reinstall_keeps_edited_dependency_map(self):
        self.install()
        dep = self.fw / "dependency-map.md"
        dep.write_text("# Mine now\n", encoding="utf-8")
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        self.assertEqual(dep.read_text(encoding="utf-8"), "# Mine now\n")

    def test_bootstrap_descriptor_requires_dependency_map(self):
        self.install()
        descriptor = json.loads(
            (self.fw / "bootstrap" / "bootstrap.json").read_text())
        self.assertIn("dependency-map.md", descriptor["requiredContext"])

    # ---- validate / doctor coverage -----------------------------------------

    def test_validate_flags_missing_dependency_map(self):
        self.install()
        (self.fw / "dependency-map.md").unlink()
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("dependency-map.md", out)

    def test_doctor_flags_missing_context_slice_member(self):
        # A slice member that is NOT in requiredContext: remove a template the
        # runtime's CONTEXT_SLICE_PHASE names, and doctor must report it.
        self.install()
        (self.fw / "templates" / "scope-definition.md").unlink()
        code, out = self.run_cli("doctor", "-t", str(self.repo))
        self.assertEqual(code, ExitCode.VALIDATION_FAILED, out)
        self.assertIn("V-SLICE", out)
        self.assertIn("templates/scope-definition.md", out)

    def test_validate_passes_on_complete_install(self):
        code, out = self.install()
        self.assertEqual(code, ExitCode.OK, out)
        code, out = self.run_cli("validate", str(self.repo))
        self.assertEqual(code, ExitCode.OK, out)

    # ---- generator -----------------------------------------------------------

    def test_generate_from_node_workspaces(self):
        self.install()
        for name, deps in (("app", {"lib-core": "1.0.0", "left-pad": "1.0.0"}),
                           ("lib-core", {})):
            pkg = self.repo / "packages" / name / "package.json"
            pkg.parent.mkdir(parents=True, exist_ok=True)
            pkg.write_text(json.dumps({"name": name, "dependencies": deps}),
                           encoding="utf-8")
        code, out = self.run_cli("context", "generate", "dependency-map",
                                 "-t", str(self.repo), "--force")
        self.assertEqual(code, ExitCode.OK, out)
        text = (self.fw / "dependency-map.md").read_text(encoding="utf-8")
        self.assertIn("| `app` | `lib-core` |", text)
        # Registry-only dependencies are environment, not structure.
        self.assertNotIn("left-pad", text)

    def test_generate_from_csproj_references(self):
        self.install()
        csproj = self.repo / "src" / "App" / "App.csproj"
        csproj.parent.mkdir(parents=True, exist_ok=True)
        csproj.write_text(
            '<Project><ItemGroup>'
            '<ProjectReference Include="..\\Core\\Core.csproj" />'
            '</ItemGroup></Project>', encoding="utf-8")
        code, out = self.run_cli("context", "generate", "dependency-map",
                                 "-t", str(self.repo), "--force")
        self.assertEqual(code, ExitCode.OK, out)
        text = (self.fw / "dependency-map.md").read_text(encoding="utf-8")
        self.assertIn("| `App` | `Core` |", text)

    def test_generate_placeholder_is_honest_when_nothing_detected(self):
        text = context_gen.render_dependency_map(self.repo)
        self.assertIn("No manifests detected", text)
        self.assertIn("placeholder", text)
        # Never a fabricated graph.
        self.assertNotIn("| `", text)

    def test_generate_refuses_overwrite_without_force(self):
        self.install()
        code, out = self.run_cli("context", "generate", "dependency-map",
                                 "-t", str(self.repo))
        self.assertEqual(code, ExitCode.INCOMPATIBLE, out)
        self.assertIn("--force", out)

    def test_generate_dry_run_writes_nothing(self):
        self.install()
        before = (self.fw / "dependency-map.md").read_text(encoding="utf-8")
        code, out = self.run_cli("context", "generate", "dependency-map",
                                 "-t", str(self.repo), "--dry-run", "--force")
        self.assertEqual(code, ExitCode.DRY_RUN, out)
        self.assertEqual(
            (self.fw / "dependency-map.md").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
