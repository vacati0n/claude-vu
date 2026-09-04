"""Bundled framework payload: sync parity, packaging coverage, and the
source-resolution fallback (ticket CKA-02).

A non-editable wheel install has no framework checkout next to the package,
so the package carries its own copy of the framework payload under
``omn_agent/_bundled_payload`` and ``find_source`` falls back to it as the
last candidate. The bundle is a committed mirror of the repository's
authoritative framework payload tree; whenever that tree changes, refresh
the mirror with:

    python tests/test_bundled_payload.py --sync

The tests here fail on any drift, so a stale bundle cannot ship silently.
"""

from __future__ import annotations

import glob
import hashlib
import shutil
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest import mock

from omn_agent import source as source_mod
from omn_agent.common import ExitCode, OmnError
from omn_agent.source import (BUNDLED_PAYLOAD_DIR, MANAGED_DIRS,
                              REQUIRED_SOURCE_FILES, SEED_DIRS, _excluded,
                              _is_framework_tree, _walk, find_source)

REPO = Path(__file__).resolve().parent.parent
AUTHORITATIVE = REPO / ".claude"
PACKAGE_DIR = REPO / "omn_agent"
BUNDLE = PACKAGE_DIR / BUNDLED_PAYLOAD_DIR
SYNC_COMMAND = "python tests/test_bundled_payload.py --sync"


def payload_map(root: Path) -> dict[str, Path]:
    """rel posix path -> absolute path, filtered exactly like the installer."""
    files: dict[str, Path] = {}
    for d in MANAGED_DIRS + SEED_DIRS:
        files.update(_walk(root / d, root))
    return files


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sync_bundle() -> int:
    """Regenerate the bundle as an exact filtered mirror; returns file count."""
    if BUNDLE.exists():
        shutil.rmtree(BUNDLE)
    payload = payload_map(AUTHORITATIVE)
    for rel, src in payload.items():
        dest = BUNDLE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dest)
    return len(payload)


class BundleParityTestCase(unittest.TestCase):
    """The committed bundle is an exact mirror of the authoritative payload."""

    def test_bundle_exists_and_is_a_framework_tree(self):
        self.assertTrue(BUNDLE.is_dir(), f"missing bundle; run: {SYNC_COMMAND}")
        self.assertTrue(_is_framework_tree(BUNDLE),
                        f"bundle lacks required source files; run: {SYNC_COMMAND}")

    def test_bundle_matches_authoritative_payload_exactly(self):
        expected = payload_map(AUTHORITATIVE)
        actual = payload_map(BUNDLE)
        self.assertEqual(sorted(expected), sorted(actual),
                         f"bundled payload file set drifted; run: {SYNC_COMMAND}")
        stale = [rel for rel in sorted(expected)
                 if _digest(expected[rel]) != _digest(actual[rel])]
        self.assertEqual(stale, [],
                         f"bundled payload content drifted; run: {SYNC_COMMAND}")

    def test_bundle_carries_no_excluded_or_stray_files(self):
        # Raw walk, no filter: everything physically inside the bundle must be
        # part of the filtered payload map -- nothing matching the installer's
        # exclusion patterns, nothing outside the managed and seed directories.
        allowed = set(payload_map(BUNDLE))
        for path in BUNDLE.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(BUNDLE).as_posix()
            self.assertFalse(any(_excluded(part) for part in Path(rel).parts),
                             f"excluded file inside bundle: {rel}; run: {SYNC_COMMAND}")
            self.assertIn(rel, allowed,
                          f"stray file inside bundle: {rel}; run: {SYNC_COMMAND}")


class PackagingDeclarationTestCase(unittest.TestCase):
    """pyproject's package-data declaration covers every bundled file."""

    def _declared_patterns(self) -> list[str]:
        cfg = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
        return cfg["tool"]["setuptools"]["package-data"]["omn_agent"]

    def test_declaration_targets_only_the_bundle(self):
        patterns = self._declared_patterns()
        self.assertTrue(patterns)
        for pattern in patterns:
            self.assertTrue(pattern.startswith(BUNDLED_PAYLOAD_DIR + "/"), pattern)

    def test_declared_globs_cover_every_bundled_file(self):
        # setuptools resolves package-data with glob(..., recursive=True)
        # relative to the package directory; reproduce that here so a payload
        # shape the patterns cannot reach (e.g. a dot-named directory) fails
        # loudly instead of silently missing from the built wheel.
        matched: set[str] = set()
        for pattern in self._declared_patterns():
            for hit in glob.glob(str(PACKAGE_DIR / pattern), recursive=True):
                p = Path(hit)
                if p.is_file():
                    matched.add(p.relative_to(BUNDLE).as_posix())
        bundled = {p.relative_to(BUNDLE).as_posix()
                   for p in BUNDLE.rglob("*") if p.is_file()}
        self.assertEqual(bundled - matched, set(),
                         "bundled files the pyproject package-data globs miss")


class FindSourceFallbackTestCase(unittest.TestCase):
    """Candidate order: explicit --source, checkout-adjacent tree, bundle."""

    def setUp(self):
        # resolve() so short-form (8.3) temp paths compare equal to the
        # resolved paths find_source returns.
        self.tmp = Path(tempfile.mkdtemp(prefix="omn-bundle-test-")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def _stub_tree(self, root: Path) -> Path:
        for rel in REQUIRED_SOURCE_FILES:
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("# stub\n", encoding="utf-8")
        return root

    def _fake_package(self, *, with_bundle: bool, with_adjacent: bool) -> Path:
        pkg = self.tmp / "site-packages" / "omn_agent"
        pkg.mkdir(parents=True, exist_ok=True)
        if with_bundle:
            self._stub_tree(pkg / BUNDLED_PAYLOAD_DIR)
        if with_adjacent:
            self._stub_tree(pkg.parent / ".claude")
        return pkg

    def _patched(self, pkg: Path):
        # find_source derives both the checkout-adjacent candidates and the
        # bundled candidate from this module-level __file__.
        return mock.patch.object(source_mod, "__file__", str(pkg / "source.py"))

    def test_bundle_resolves_when_no_other_candidate_exists(self):
        pkg = self._fake_package(with_bundle=True, with_adjacent=False)
        with self._patched(pkg):
            self.assertEqual(find_source(None), pkg / BUNDLED_PAYLOAD_DIR)

    def test_checkout_adjacent_tree_wins_over_bundle(self):
        pkg = self._fake_package(with_bundle=True, with_adjacent=True)
        with self._patched(pkg):
            self.assertEqual(find_source(None), pkg.parent / ".claude")

    def test_explicit_source_wins_over_everything(self):
        pkg = self._fake_package(with_bundle=True, with_adjacent=True)
        explicit = self._stub_tree(self.tmp / "explicit-src")
        with self._patched(pkg):
            self.assertEqual(find_source(str(explicit)), explicit.resolve())

    def test_invalid_explicit_source_never_falls_back_to_bundle(self):
        pkg = self._fake_package(with_bundle=True, with_adjacent=False)
        bogus = self.tmp / "not-a-framework"
        bogus.mkdir()
        with self._patched(pkg):
            with self.assertRaises(OmnError) as ctx:
                find_source(str(bogus))
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)
        self.assertIn("--source", ctx.exception.hint or "")

    def test_invalid_bundle_is_not_selected_and_failure_stays_actionable(self):
        pkg = self._fake_package(with_bundle=False, with_adjacent=False)
        (pkg / BUNDLED_PAYLOAD_DIR).mkdir()  # present but not a framework tree
        with self._patched(pkg):
            with self.assertRaises(OmnError) as ctx:
                find_source(None)
        self.assertEqual(ctx.exception.exit_code, ExitCode.INVALID_TARGET)
        self.assertIn("no framework source found", ctx.exception.message)
        self.assertIn("--source <path>", ctx.exception.hint or "")

    def test_repo_checkout_still_resolves_its_own_payload_tree(self):
        # In this repository the checkout-adjacent tree must keep winning over
        # the committed bundle: precedence is unchanged for existing users.
        self.assertEqual(find_source(None), AUTHORITATIVE)


if __name__ == "__main__":
    if "--sync" in sys.argv:
        count = sync_bundle()
        print(f"bundled payload refreshed: {count} files -> {BUNDLE}")
    else:
        unittest.main(verbosity=2)
