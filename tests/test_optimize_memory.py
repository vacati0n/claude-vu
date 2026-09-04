"""Tests for the memory token optimizer (`.claude/runtime/optimize_memory.py`).

The module's guarantee is its invariant check: a candidate is accepted only when it breaks
none of `I0` to `I9`, and the framework claims exactly that and no more. So most of what is
asserted here is refusal — one constructed candidate per loss class, each of which must be
caught and named. A rule that accepts everything would pass a test suite that only checked
the happy path, which is why the happy path is one test and the losses are ten.

The rest covers the two properties that make the modifying path safe to have at all: denial
of generated and evidence surfaces binds by path regardless of what the caller asks for, and
nothing is overwritten without a recoverable pre-image.

No network, no credentials, no provider client library. Every test here exercises the
offline surface, which is the surface an operator can reach without provisioning anything.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RUNTIME_DIR = Path(__file__).resolve().parent.parent / ".claude" / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import optimize_memory as om  # noqa: E402


DOC = """\
---
name: sample-rule
description: a governed document
---

# Governance Sample

Some introductory prose that is deliberately wordy and could be compressed a great deal
without anyone losing anything of value at all.

## Rules

| Rule | Decision | Reason |
|---|---|---|
| `SR-1` | in-scope | Everything the runtime resolves lives here |
| `SR-2` | out-of-scope | Run evidence, written during execution |

- The first obligation, which must hold.
- The second obligation, which must also hold.

See [the profile](config/self-hosting-profile.md) and `runtime/self_hosting.py`.

## Procedure

```bash
python .claude/runtime/self_hosting.py route --intent capability-addition
```

Closing prose.
"""


class InvariantCheckTests(unittest.TestCase):
    """`I0` to `I9`: what a candidate must not do."""

    def test_identity_is_accepted(self):
        self.assertEqual(om.check(DOC, DOC), [])

    def test_real_framework_document_is_identity_clean(self):
        """The rule must not refuse a document simply for being complicated."""
        profile = (RUNTIME_DIR.parent / "config" / "self-hosting-profile.md")
        text = profile.read_text(encoding="utf-8")
        self.assertEqual(om.check(text, text), [])

    def _violations(self, candidate, prefix):
        found = om.check(DOC, candidate)
        self.assertTrue(any(v.startswith(prefix) for v in found),
                        f"expected a {prefix} violation, got {found}")
        return found

    def test_empty_candidate_is_refused(self):
        self.assertEqual(om.check(DOC, "   \n"), ["I0 empty candidate"])

    def test_altered_frontmatter_is_refused(self):
        self._violations(DOC.replace("description: a governed document\n", ""), "I1")

    def test_dropped_heading_is_refused(self):
        found = self._violations(DOC.replace("## Procedure", "Procedure"), "I2")
        self.assertTrue(any("Procedure" in v for v in found), found)

    def test_introduced_heading_is_refused(self):
        self._violations(DOC.replace("Closing prose.", "## Extra\n\nClosing prose."), "I2")

    def test_altered_code_fence_is_refused(self):
        self._violations(DOC.replace("--intent capability-addition", "--intent x"), "I3")

    def test_dropped_table_row_is_refused(self):
        candidate = DOC.replace(
            "| `SR-2` | out-of-scope | Run evidence, written during execution |\n", "")
        self._violations(candidate, "I4")

    def test_dropped_link_target_is_refused(self):
        self._violations(DOC.replace("[the profile](config/self-hosting-profile.md)",
                                     "the profile"), "I5")

    def test_dropped_code_span_is_refused(self):
        self._violations(DOC.replace("`runtime/self_hosting.py`", "the self-hosting module"),
                         "I6")

    def test_dropped_identifier_is_refused(self):
        found = self._violations(DOC.replace("`SR-1`", "the first rule"), "I7")
        self.assertTrue(any("SR-1" in v for v in found), found)

    def test_dropped_list_item_is_refused(self):
        self._violations(DOC.replace("- The second obligation, which must also hold.\n", ""),
                         "I8")

    def test_over_shrunk_candidate_is_refused(self):
        self._violations(DOC[:120], "I9")

    def test_a_genuine_compression_is_accepted(self):
        """Prose tightened, every checked element intact: the case the rule exists to permit."""
        candidate = DOC.replace(
            "Some introductory prose that is deliberately wordy and could be compressed a great "
            "deal\nwithout anyone losing anything of value at all.",
            "Introductory prose. Compressible.")
        self.assertEqual(om.check(DOC, candidate), [])
        self.assertLess(len(candidate), len(DOC))


class DiscoveryTests(unittest.TestCase):
    """Denial binds by path, not by argument."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _write(self, rel, text=DOC):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_denied_segment_is_refused_even_when_named_directly(self):
        self._write("runs/run-abc/notes.md")
        targets = om.discover([self.root / "runs"], [])
        self.assertTrue(targets)
        self.assertFalse(any(t.eligible for t in targets))
        self.assertIn("denied path segment", targets[0].reason)

    def test_every_denied_segment_binds(self):
        for seg in ("runs", "reports", "proposals", "__pycache__"):
            with self.subTest(segment=seg):
                p = self._write(f"{seg}/doc.md")
                self.assertFalse(om.classify(p).eligible)

    def test_denied_filename_is_refused(self):
        self.assertFalse(om.classify(self._write("notes/CHANGELOG.md")).eligible)

    def test_self_declared_generated_file_is_refused(self):
        p = self._write("notes/gen.md", "<!-- generated by a tool -->\n\n" + DOC)
        target = om.classify(p)
        self.assertFalse(target.eligible)
        self.assertEqual(target.reason, "declares itself generated")

    def test_small_file_is_refused_with_the_floor_named(self):
        target = om.classify(self._write("notes/tiny.md", "# t\n\nshort.\n"))
        self.assertFalse(target.eligible)
        self.assertIn("byte floor", target.reason)

    def test_non_markdown_is_refused(self):
        self.assertFalse(om.classify(self._write("notes/code.py", "x = 1\n" * 200)).eligible)

    def test_an_ordinary_document_is_eligible(self):
        target = om.classify(self._write("notes/rules.md"))
        self.assertTrue(target.eligible, target.reason)
        self.assertEqual(target.reason, "")

    def test_every_skipped_file_carries_a_reason(self):
        self._write("notes/rules.md")
        self._write("notes/CHANGELOG.md")
        self._write("notes/tiny.md", "# t\n")
        for t in om.discover([self.root], []):
            self.assertTrue(t.eligible or t.reason, t.rel)


class SessionPathTests(unittest.TestCase):
    """A session write can only land inside the session.

    `Target.rel` is absolute for a file outside the repository, and joining an absolute path
    discards everything to its left. Before this was fixed, a `--root` outside the repository
    made the pre-image write resolve to the original file, so backing up a file overwrote it
    and a dry run overwrote it too. These tests exist so that cannot return.
    """

    def test_posix_absolute_path_is_confined(self):
        rel = om.session_rel("/home/u/notes/a.md")
        self.assertFalse(rel.startswith("/"))
        self.assertEqual(Path("session/backup") / rel, Path("session/backup/home/u/notes/a.md"))

    def test_windows_drive_path_is_confined(self):
        rel = om.session_rel("C:/Users/u/notes/a.md")
        self.assertNotIn(":", rel)
        self.assertEqual((Path("session") / rel).parts[0], "session")

    def test_parent_traversal_is_stripped(self):
        self.assertEqual(om.session_rel("../../etc/passwd.md"), "etc/passwd.md")

    def test_repository_relative_path_is_unchanged(self):
        self.assertEqual(om.session_rel(".claude/memory/architecture.md"),
                         ".claude/memory/architecture.md")

    def test_a_degenerate_path_still_yields_a_name(self):
        self.assertEqual(om.session_rel("/"), "unnamed.md")


class RestoreTests(unittest.TestCase):
    """Nothing is overwritten without a recoverable pre-image."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def _session(self, target: Path, before: str, after: str):
        """A manifest of the shape an applied pass writes, with the pre-image on disk."""
        session = self.root / "session"
        backup = session / "backup" / target.name
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_text(before, encoding="utf-8")
        manifest = session / "manifest.json"
        manifest.write_text(json.dumps({
            "schema": "framework.runtime/optimize-memory.v1",
            "mode": "apply",
            "results": [{
                "file": om._rel(target), "verdict": "accepted",
                "tokens_before": 100, "tokens_after": 80,
                "digest_before": om.sha256(before), "digest_after": om.sha256(after),
                "backup": om._rel(backup), "violations": [], "note": "",
            }],
        }, indent=2), encoding="utf-8")
        return manifest

    def test_restore_puts_the_pre_image_back(self):
        target = self.root / "rules.md"
        target.write_text("compressed\n", encoding="utf-8")
        manifest = self._session(target, DOC, "compressed\n")
        rc = om.cmd_restore(_Args(manifest=str(manifest), force=False))
        self.assertEqual(rc, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), DOC)

    def test_restore_refuses_a_file_edited_after_the_pass(self):
        target = self.root / "rules.md"
        target.write_text("edited by hand afterwards\n", encoding="utf-8")
        manifest = self._session(target, DOC, "compressed\n")
        rc = om.cmd_restore(_Args(manifest=str(manifest), force=False))
        self.assertEqual(rc, 1)
        self.assertEqual(target.read_text(encoding="utf-8"), "edited by hand afterwards\n")

    def test_force_overrides_the_refusal(self):
        target = self.root / "rules.md"
        target.write_text("edited by hand afterwards\n", encoding="utf-8")
        manifest = self._session(target, DOC, "compressed\n")
        self.assertEqual(om.cmd_restore(_Args(manifest=str(manifest), force=True)), 0)
        self.assertEqual(target.read_text(encoding="utf-8"), DOC)

    def test_a_dry_run_session_has_nothing_to_restore(self):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({"mode": "dry-run", "results": []}), encoding="utf-8")
        self.assertEqual(om.cmd_restore(_Args(manifest=str(manifest), force=False)), 0)


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


if __name__ == "__main__":
    unittest.main()
