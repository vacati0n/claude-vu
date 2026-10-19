"""Tests for the OKF v0.2 lesson bundle (runtime 0.11.0): the frontmatter subset in
`runtime/okf.py`, the lesson document mapping, `index.md` and `log.md`, the four-step write
under interruption, the §11 conformance check and its verifier, the store-migration-pending
refusal, and the verify-before-delete migration of the JSON store.

Every test builds its own temporary framework root; nothing here reads from or writes to the
live `runs/` or `memory/` directories.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
CLAUDE = REPO / ".claude"
RUNTIME_DIR = CLAUDE / "runtime"
sys.path.insert(0, str(RUNTIME_DIR))

import knowledge as kl  # noqa: E402
import okf  # noqa: E402

VERIFIER = RUNTIME_DIR / "verify_okf_bundle.py"


# ------------------------------------------------------------------ fixtures


def record(fp: str, *, status: str = "candidate", history=None, evidence=None,
           evidence_state: str = "current", remedy=None, description="a check description",
           first_seen="2026-01-01T00:00:00Z", last_seen="2026-01-02T00:00:00Z",
           phases=("s",)) -> dict:
    kind = "validation-check" if fp.startswith("check:") else "gate-rejection"
    _, art_or_gate, key = fp.split(":", 2)
    return {"lesson_id": kl.lesson_id_for(fp), "fingerprint": fp, "kind": kind,
            "check_id": key if kind == "validation-check" else None,
            "check_description": description if kind == "validation-check" else None,
            "check_severity": "Blocking" if kind == "validation-check" else None,
            "gate": art_or_gate if kind == "gate-rejection" else None,
            "artifact_type": art_or_gate if kind == "validation-check" else "x.md",
            "phases": list(phases), "occurrences": 3, "distinct_runs": 2,
            "first_seen": first_seen, "last_seen": last_seen,
            "evidence": list(evidence if evidence is not None else
                             ["runs/run-a/events.jsonl#E-0001",
                              "runs/run-b/events.jsonl#E-0002",
                              "runs/run-a/events.jsonl#E-0009"]),
            "evidence_state": evidence_state, "status": status, "owner": "tech-lead",
            "rationale": "fixture rationale", "remedy": remedy, "history": list(history or [])}


def entry(action, before, after, actor, time, rationale="because"):
    return {"action": action, "from": before, "to": after, "actor": actor,
            "rationale": rationale, "time": time}


def mixed_records() -> list:
    """Every record shape the live store holds, plus governance history of every kind."""
    return [
        record("check:a.md:C1.1"),
        record("check:a.md:C1.2", status="active", remedy="Read the contract first.",
               history=[entry("approve", "candidate", "active", "Jane Doe", "2026-02-03T10:00:00Z"),
                        entry("annotate", "active", "active", "human:jane", "2026-02-03T11:00:00Z")]),
        record("check:b.md:V4.1", status="retired",
               history=[entry("approve", "candidate", "active", "ops", "2026-02-01T09:00:00Z"),
                        entry("retire", "active", "retired", "ops", "2026-02-05T09:00:00Z")]),
        record("gate:G2-SCOPE:scope-and-acceptance", phases=("scope-and-acceptance",)),
        record("check:c.md:S1", evidence_state="retained", evidence=[], first_seen=None,
               last_seen="2026-01-20T00:00:00Z"),
        record("check:d.md:K2", description=None),
    ]


def make_root() -> Path:
    root = Path(tempfile.mkdtemp(prefix="okf-"))
    (root / "config").mkdir()
    shutil.copy(CLAUDE / kl.POLICY_REL, root / kl.POLICY_REL)
    return root


def store(records: list) -> dict:
    return {"schema": kl.STORE_SCHEMA, "lessons": records}


def files(root: Path) -> dict:
    d = root / kl.BUNDLE_REL
    return {p.name: p.read_bytes() for p in sorted(d.iterdir()) if p.is_file()} \
        if d.is_dir() else {}


def write_legacy(root: Path, records: list) -> Path:
    path = root / kl.LEGACY_STORE_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(store(sorted(records, key=lambda l: l["fingerprint"])),
                                 sort_keys=True, indent=2, ensure_ascii=True) + "\n")
                     .encode("utf-8"))
    return path


def verify(*args) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(VERIFIER), *map(str, args)],
                          capture_output=True, text=True)


# ------------------------------------------------------------------ frontmatter subset


HOSTILE = [
    "line one\nline two", "---", "a\n---\nb", "key: value", "# leading hash", "[not a list]",
    "{not: a map}", 'double " quote', "single ' quote", "back\\slash", "tab\there",
    "caf\u00e9 \u4e2d\u6587", "astral \U0001F600", "123", "-7", "null", "true", "~", "",
    " padded ", "- dash", "| pipe", "> fold", "&anchor", "*alias", "!tag", "%dir", "@at",
    "`tick`", "\r\n", "\x00\x07", "\u2028",
]


class FrontmatterSubsetTestCase(unittest.TestCase):

    def test_hostile_strings_round_trip_on_one_ascii_line_each(self):
        data = {f"k{i}": s for i, s in enumerate(HOSTILE)}
        data["nested"] = {"list": HOSTILE, "empty_list": [], "empty_map": {},
                          "maps": [{"b": s, "a": 1} for s in HOSTILE[:5]]}
        text = okf.dump(data)
        self.assertEqual(okf.dump(data), text)
        text.encode("ascii")
        self.assertEqual(len(text.splitlines()),
                         len(HOSTILE) + 1 + 1 + len(HOSTILE) + 2 + 1 + 5 * 2)
        self.assertNotIn("\n---\n", "\n" + text)
        back = okf.parse(text)
        self.assertEqual(back, data)
        self.assertEqual(list(back), list(data))
        doc = okf.join_document(data, "body\n")
        front, body = okf.parse_document(doc)
        self.assertEqual((front, body), (data, "body\n"))

    def test_every_record_shape_round_trips(self):
        for rec in mixed_records():
            front = kl.lesson_frontmatter(rec)
            text = okf.dump(front, keep_order=(kl.RECORD_KEY,))
            self.assertEqual(okf.parse(text), front, rec["fingerprint"])
            self.assertEqual(list(okf.parse(text)[kl.RECORD_KEY]), list(kl.LESSON_FIELDS))

    def test_scalars_are_typed(self):
        data = {"n": None, "t": True, "f": False, "i": 42, "neg": -3, "s": "42", "e": "null"}
        self.assertEqual(okf.parse(okf.dump(data)), data)
        self.assertIn('s: "42"', okf.dump(data))
        self.assertIn("n: null", okf.dump(data))

    def test_unsupported_values_are_refused(self):
        for bad in ({"x": 1.5}, {"x": (1, 2)}, {"x": b"b"}, {"bad key": 1}, {"x": [[1]]},
                    {"x": {"y z": 1}}):
            with self.assertRaises(okf.OkfError, msg=repr(bad)):
                okf.dump(bad)

    def test_the_parser_accepts_the_documented_extras(self):
        text = ("# comment\nplain: some words\nempty:\ntilde: ~\nsq: 'it''s'\n"
                "flow: [a, 'b c', \"d\", 3]\nmap: {x: 1, y: two}\nnum: 7\nyes: true\n"
                "nested:\n  - a\n  - b: 1\n    c: [1]\n")
        self.assertEqual(okf.parse(text), {
            "plain": "some words", "empty": None, "tilde": None, "sq": "it's",
            "flow": ["a", "b c", "d", 3], "map": {"x": 1, "y": "two"}, "num": 7, "yes": True,
            "nested": ["a", {"b": 1, "c": [1]}]})

    def test_the_parser_refuses_what_is_outside_the_subset(self):
        for bad in ("a: |\n  text\n", "a: >\n  text\n", "a: &x 1\n", "a: *x\n", "a: !t 1\n",
                    "a: 1\na: 2\n", "a: [1, [2]]\n", 'a: "unterminated\n', "  a: 1\n",
                    "a:\n\t- 1\n", "a: b: c\n"):
            with self.assertRaises(okf.OkfError, msg=repr(bad)):
                okf.parse(bad)

    def test_documents_without_or_with_unclosed_frontmatter(self):
        self.assertEqual(okf.parse_document("# title\n"), (None, "# title\n"))
        with self.assertRaises(okf.OkfError):
            okf.parse_document("---\ntype: x\n")


# ------------------------------------------------------------------ bundle content


class BundleContentTestCase(unittest.TestCase):
    """AC-001 to AC-008 and AC-023 over a bundle written from every record shape."""

    @classmethod
    def setUpClass(cls):
        cls.root = make_root()
        cls.records = sorted(mixed_records(), key=lambda l: l["fingerprint"])
        kl.write_store(cls.root, store(cls.records))
        cls.bundle = cls.root / kl.BUNDLE_REL
        cls.docs = {r["lesson_id"]: okf.parse_document(
            (cls.bundle / f"{r['lesson_id']}.md").read_text(encoding="utf-8"))
            for r in cls.records}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_one_document_per_record_and_two_reserved_files(self):
        names = sorted(p.name for p in self.bundle.iterdir())
        self.assertEqual(names, sorted([f"{r['lesson_id']}.md" for r in self.records]
                                       + ["index.md", "log.md"]))

    def test_the_index(self):
        front, body = okf.parse_document((self.bundle / "index.md").read_text(encoding="utf-8"))
        self.assertEqual(front, {"okf_version": "0.2"})
        lines = [l for l in body.splitlines() if l.strip()]
        self.assertEqual(lines[0], "# Lessons")
        self.assertEqual(len(lines) - 1, len(self.records))
        for line, rec in zip(lines[1:], self.records):
            self.assertIn(f"]({rec['lesson_id']}.md) - ", line)
            self.assertTrue((self.bundle / f"{rec['lesson_id']}.md").is_file())

    def test_every_document_against_its_record(self):
        for rec in self.records:
            front, body = self.docs[rec["lesson_id"]]
            self.assertEqual(front["type"], "Lesson")
            self.assertEqual(front["lesson_record"], rec)
            self.assertEqual(front["description"], kl.neutralise(
                rec["check_description"], kl.DESCRIPTION_CAP) or "no description recorded")
            self.assertTrue(front["title"].startswith(rec["kind"]))
            self.assertEqual(front["tags"][:2], [rec["kind"], rec["artifact_type"]])
            self.assertEqual(front["status"], {"candidate": "draft", "active": "stable",
                                               "retired": "deprecated"}[rec["status"]])
            # sources: the distinct evidence paths before the fragment (S-028, Q-001)
            got = {s["resource"][len("../../"):] for s in front.get("sources", [])}
            self.assertEqual(got, {e.split("#", 1)[0] for e in rec["evidence"]})
            self.assertEqual(len(front.get("sources", [])), len(got))
            approvals = [h for h in rec["history"] if h["action"] == "approve"]
            self.assertEqual(len(front.get("verified", [])), len(approvals))
            for v in front.get("verified", []):
                self.assertTrue(v["by"].startswith("human:"))
                self.assertNotIn("human:human:", v["by"])
            if rec["last_seen"] or rec["first_seen"]:
                self.assertEqual(front["generated"]["by"], "knowledge-loop/1.0.0")
            self.assertEqual("stale_after" in front, rec["evidence_state"] == "retained")
            self.assertTrue(body.startswith(f"# {front['title']}\n\nSummary: "))

    def test_the_reader_returns_the_records(self):
        self.assertEqual(kl.load_store(self.root), store(self.records))

    def test_render_section_is_unchanged_over_the_same_lessons(self):
        loaded = kl.load_store(self.root)["lessons"]
        self.assertEqual(kl.render_section(loaded), kl.render_section(self.records))

    def test_the_change_log(self):
        text = (self.bundle / "log.md").read_text(encoding="utf-8")
        self.assertFalse(text.startswith("---"))
        lines = text.splitlines()
        self.assertEqual(lines[0], "# Lesson Change Log")
        dates = [l[3:] for l in lines if l.startswith("## ")]
        self.assertEqual(dates, sorted(set(dates), reverse=True))
        entries = [l for l in lines if l.startswith("- ")]
        self.assertEqual(len(entries),
                         len(self.records) + sum(len(r["history"]) for r in self.records))
        self.assertEqual(sum("**Deprecation**" in e for e in entries), 1)
        self.assertEqual(sum("**Update**" in e for e in entries), 3)
        self.assertIn("by human:Jane-Doe", text)
        self.assertNotIn("because", text)
        self.assertNotIn("fixture rationale", text)
        # newest entry first within a date
        day = lines.index("## 2026-02-03")
        self.assertIn("status stable, by human:jane", lines[day + 2])

    def test_the_bundle_conforms(self):
        verdict = okf.conformance(self.bundle)
        self.assertEqual((verdict["result"], verdict["findings"]), ("pass", []))
        self.assertEqual((verdict["documents"], verdict["reserved"]), (len(self.records), 2))


# ------------------------------------------------------------------ write contract


class WriteContractTestCase(unittest.TestCase):

    def setUp(self):
        self.root = make_root()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_a_second_write_is_byte_identical(self):
        self.assertTrue(kl.write_store(self.root, store(mixed_records())))
        before = files(self.root)
        self.assertFalse(kl.write_store(self.root, store(mixed_records())))
        self.assertEqual(files(self.root), before)

    def test_an_unsafe_lesson_id_writes_nothing(self):
        for bad in ("../escape", "L-ABCDEF0123", "L-0123", None, "L-0123456789/x"):
            rec = record("check:a.md:C1.1")
            rec["lesson_id"] = bad
            with self.assertRaises(kl.KnowledgeError) as cm:
                kl.write_store(self.root, store([record("check:b.md:C1.1"), rec]))
            self.assertEqual(cm.exception.error_class, "store-unwritable")
            self.assertEqual(files(self.root), {})

    def test_an_unsupported_value_writes_nothing(self):
        kl.write_store(self.root, store([record("check:a.md:C1.1")]))
        before = files(self.root)
        rec = record("check:b.md:C1.1")
        rec["occurrences"] = 1.5
        with self.assertRaises(kl.KnowledgeError) as cm:
            kl.write_store(self.root, store([record("check:a.md:C1.1"), rec]))
        self.assertEqual(cm.exception.error_class, "store-unwritable")
        self.assertEqual(files(self.root), before)

    def test_a_record_without_a_document_is_removed(self):
        recs = mixed_records()
        kl.write_store(self.root, store(recs))
        gone = recs.pop()
        (self.root / kl.BUNDLE_REL / "L-0123456789.md.tmp").write_text("x", encoding="utf-8")
        kl.write_store(self.root, store(recs))
        names = set(files(self.root))
        self.assertNotIn(gone["lesson_id"] + ".md", names)
        self.assertNotIn("L-0123456789.md.tmp", names)

    def test_a_broken_document_is_store_unreadable_naming_it(self):
        kl.write_store(self.root, store([record("check:a.md:C1.1")]))
        lid = kl.lesson_id_for("check:a.md:C1.1")
        path = self.root / kl.BUNDLE_REL / f"{lid}.md"
        for text in ("---\ntype: \"Lesson\"\nlesson_record: [x\n---\n", "# no frontmatter\n",
                     "---\ntype: \"Note\"\n---\n",
                     "---\ntype: \"Lesson\"\nlesson_record:\n  lesson_id: \"" + lid + "\"\n---\n"):
            path.write_text(text, encoding="utf-8")
            with self.assertRaises(kl.KnowledgeError) as cm:
                kl.load_store(self.root)
            self.assertEqual(cm.exception.error_class, "store-unreadable")
            self.assertIn(path.name, cm.exception.detail)


class InterruptionTestCase(unittest.TestCase):
    """AC-013: a fault after each write step leaves parseable files, each either its prior or
    its new version, and the next write restores index and log agreement."""

    def setUp(self):
        self.prior = mixed_records()
        nxt = [dict(r) for r in self.prior[1:]]          # one lesson removed
        nxt[0]["occurrences"] = 99                        # one changed
        nxt.append(record("check:z.md:Z9"))               # one added
        self.next = nxt
        self.want = self.fresh(self.next)
        self.old = self.fresh(self.prior)

    def fresh(self, recs) -> dict:
        root = make_root()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        kl.write_store(root, store(recs))
        return files(root)

    def check_state(self, root: Path, label: str):
        for name, data in files(root).items():
            if name.endswith(kl.TMP_SUFFIX):
                continue
            self.assertIn(data, {self.old.get(name), self.want.get(name)}, f"{label}: {name}")
            okf.parse_document(data.decode("utf-8"))
        self.assertEqual(okf.conformance(root / kl.BUNDLE_REL)["result"], "pass", label)
        kl.write_store(root, store(self.next))
        self.assertEqual(files(root), self.want, label)
        self.assertEqual(kl.load_store(root), store(sorted(self.next,
                                                           key=lambda l: l["fingerprint"])))

    def test_a_fault_at_each_replace(self):
        real = kl.os.replace
        steps = 0
        root = make_root()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        kl.write_store(root, store(self.prior))
        calls = []
        with mock.patch.object(kl.os, "replace", side_effect=lambda a, b: (calls.append(b),
                                                                            real(a, b))):
            kl.write_store(root, store(self.next))
        steps = len(calls)
        self.assertEqual(steps, 4)   # changed doc, added doc, log.md, index.md
        for fail_at in range(steps):
            root = make_root()
            self.addCleanup(shutil.rmtree, root, ignore_errors=True)
            kl.write_store(root, store(self.prior))
            count = {"n": 0}

            def flaky(a, b):
                if count["n"] == fail_at:
                    raise OSError("injected fault")
                count["n"] += 1
                return real(a, b)

            with mock.patch.object(kl.os, "replace", side_effect=flaky):
                with self.assertRaises(OSError):
                    kl.write_store(root, store(self.next))
            self.check_state(root, f"replace {fail_at}")

    def test_a_fault_at_the_removal(self):
        root = make_root()
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        kl.write_store(root, store(self.prior))
        with mock.patch.object(Path, "unlink", side_effect=OSError("injected fault")):
            with self.assertRaises(OSError):
                kl.write_store(root, store(self.next))
        self.check_state(root, "removal")


# ------------------------------------------------------------------ conformance


class ConformanceTestCase(unittest.TestCase):
    """AC-014 and AC-015: the check passes a written bundle, fails each seeded defect with its
    rule, and gives identical output and exit status twice."""

    def setUp(self):
        self.root = make_root()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        kl.write_store(self.root, store(mixed_records()))
        self.bundle = self.root / kl.BUNDLE_REL

    def seeded(self, name: str, text: str) -> dict:
        target = Path(tempfile.mkdtemp(prefix="okf-seed-"))
        self.addCleanup(shutil.rmtree, target, ignore_errors=True)
        shutil.copytree(self.bundle, target / "b")
        (target / "b" / name).parent.mkdir(parents=True, exist_ok=True)
        (target / "b" / name).write_text(text, encoding="utf-8")
        return okf.conformance(target / "b", "b")

    def test_each_seeded_defect_fails_with_its_rule(self):
        lid = kl.lesson_id_for("check:a.md:C1.1")
        cases = [
            (f"{lid}.md", "---\ntype: [broken\n---\n", "OKF-11.1"),
            ("note.md", "# no frontmatter\n", "OKF-11.1"),
            (f"{lid}.md", "---\ntype: \"\"\n---\n", "OKF-11.2"),
            ("other.md", "---\ntitle: \"x\"\n---\n", "OKF-11.2"),
            ("index.md", "---\nokf_version: \"0.2\"\nextra: 1\n---\n# Lessons\n", "OKF-11.3-index"),
            ("index.md", "---\nokf_version: \"0.2\"\n---\nnot a heading\n", "OKF-11.3-index"),
            ("index.md", "---\nokf_version: \"0.2\"\n---\n# L\n\nfree text\n", "OKF-11.3-index"),
            ("sub/index.md", "---\nokf_version: \"0.2\"\n---\n# Sub\n", "OKF-11.3-index"),
            ("log.md", "no title\n", "OKF-11.3-log"),
            ("log.md", "# Log\n\n## 2026-13-01\n", "OKF-11.3-log"),
            ("log.md", "# Log\n\n## 2026-01-01\n\n## 2026-02-01\n", "OKF-11.3-log"),
            ("log.md", "# Log\n\n- entry before a date\n", "OKF-11.3-log"),
        ]
        for name, text, rule in cases:
            verdict = self.seeded(name, text)
            self.assertEqual(verdict["result"], "fail", (name, text))
            self.assertEqual({f["rule"] for f in verdict["findings"]}, {rule}, (name, text))

    def test_absent_and_empty_bundles(self):
        self.assertEqual(okf.conformance(self.root / "nowhere")["result"], "absent")
        empty = self.root / "empty"
        empty.mkdir()
        self.assertEqual(okf.conformance(empty)["result"], "absent")

    def test_the_verifier_exit_contract_and_determinism(self):
        first, second = verify(self.bundle), verify(self.bundle)
        self.assertEqual((first.returncode, first.stdout), (0, second.stdout))
        self.assertIn("result: pass", first.stdout)
        as_json = verify(self.bundle, "--json")
        self.assertEqual(json.loads(as_json.stdout)["result"], "pass")
        (self.bundle / "log.md").write_text("no title\n", encoding="utf-8")
        failed, again = verify(self.bundle), verify(self.bundle)
        self.assertEqual((failed.returncode, again.returncode), (1, 1))
        self.assertEqual(failed.stdout, again.stdout)
        self.assertIn("OKF-11.3-log", failed.stdout)
        # The closing summary line the CI verifier jobs parse: one check per file.
        summary = re.compile(r"(?m)^(\d+)/(\d+) checks passed -- (\S+)$")
        ok, bad = summary.findall(first.stdout), summary.findall(failed.stdout)
        self.assertEqual(len(ok), 1)
        self.assertEqual(ok[0][0], ok[0][1])
        self.assertEqual(ok[0][2], "CONFORMANT")
        self.assertEqual((int(bad[0][0]) + 1, bad[0][1], bad[0][2]),
                         (int(ok[0][1]), ok[0][1], "NON-CONFORMANT"))
        missing = verify(self.root / "nowhere")
        self.assertEqual(missing.returncode, 2)
        empty = self.root / "empty"
        empty.mkdir()
        self.assertEqual(verify(empty).returncode, 0)


# ------------------------------------------------------------------ migration


class MigrationTestCase(unittest.TestCase):
    """AC-016 to AC-018 and the store-migration-pending refusal."""

    def setUp(self):
        self.root = make_root()
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        self.records = sorted(mixed_records(), key=lambda l: l["fingerprint"])
        self.legacy = write_legacy(self.root, self.records)

    def test_a_json_only_store_is_refused_by_every_reader_and_writer(self):
        for call in (lambda: kl.load_store(self.root),
                     lambda: kl.write_store(self.root, store(self.records)),
                     lambda: kl.harvest(self.root),
                     lambda: kl.govern(self.root, "approve", self.records[0]["lesson_id"],
                                       actor="t", rationale="r"),
                     lambda: kl.recall(self.root, "s", "a.md")):
            with self.assertRaises(kl.KnowledgeError) as cm:
                call()
            self.assertEqual(cm.exception.error_class, "store-migration-pending")
        ms, shown = kl.dispatch_memory_slice(self.root, {"hydration": "on"}, "s", "a.md")
        self.assertFalse(ms["hydrated"])
        self.assertIn("store-migration-pending", ms["reason"])
        self.assertEqual(shown, [])
        self.assertTrue(self.legacy.exists())
        self.assertFalse(kl.bundle_exists(self.root))

    def test_migrate_verifies_then_removes_the_json_store(self):
        out = kl.migrate(self.root)
        self.assertEqual((out["status"], out["lessons"], out["documents"]),
                         ("migrated", len(self.records), len(self.records)))
        self.assertFalse(self.legacy.exists())
        self.assertFalse((self.root / kl.LOCK_REL).exists())
        loaded = kl.load_store(self.root)["lessons"]
        self.assertEqual(loaded, self.records)
        self.assertEqual({l["lesson_id"] for l in loaded},
                         {l["lesson_id"] for l in self.records})
        self.assertEqual([len(l["history"]) for l in loaded],
                         [len(l["history"]) for l in self.records])
        self.assertEqual(okf.conformance(self.root / kl.BUNDLE_REL)["result"], "pass")
        again = kl.migrate(self.root)
        self.assertEqual(again["status"], "no-legacy-store")
        self.assertEqual(again["store_digest"], out["store_digest"])

    def test_a_forced_mismatch_keeps_the_json_store(self):
        real = kl.load_store

        def altered(root):
            data = real(root)
            data["lessons"][0]["occurrences"] += 1
            return data

        with mock.patch.object(kl, "load_store", side_effect=altered):
            with self.assertRaises(kl.KnowledgeError) as cm:
                kl.migrate(self.root)
        self.assertEqual(cm.exception.error_class, "migration-mismatch")
        self.assertTrue(self.legacy.exists())
        self.assertFalse((self.root / kl.LOCK_REL).exists())
        # a re-run completes the migration
        self.assertEqual(kl.migrate(self.root)["status"], "migrated")
        self.assertFalse(self.legacy.exists())

    def test_migrate_with_both_forms_never_overwrites_the_bundle(self):
        # an earlier migration left both forms; the bundle then moved on alone
        kl._write_bundle(self.root, store(self.records))
        candidate = next(l for l in self.records if l["status"] == "candidate")
        kl.govern(self.root, "approve", candidate["lesson_id"], actor="t", rationale="r")
        later = record("check:e.md:Z9")
        with kl.StoreLock(self.root):
            data = kl.load_store(self.root)
            data["lessons"].append(later)
            kl.write_store(self.root, data)
        before, legacy_bytes = files(self.root), self.legacy.read_bytes()
        with self.assertRaises(kl.KnowledgeError) as cm:
            kl.migrate(self.root)
        self.assertEqual(cm.exception.error_class, "migration-mismatch")
        self.assertIn(later["lesson_id"], cm.exception.detail)
        self.assertIn(candidate["lesson_id"], cm.exception.detail)
        self.assertEqual(files(self.root), before)
        self.assertEqual(self.legacy.read_bytes(), legacy_bytes)
        self.assertFalse((self.root / kl.LOCK_REL).exists())
        loaded = {l["lesson_id"]: l for l in kl.load_store(self.root)["lessons"]}
        self.assertIn(later["lesson_id"], loaded)
        approved = loaded[candidate["lesson_id"]]
        self.assertEqual(approved["status"], "active")
        self.assertEqual([h["action"] for h in approved["history"]], ["approve"])
        done = subprocess.run([sys.executable, str(RUNTIME_DIR / "knowledge.py"), "--root",
                               str(self.root), "migrate"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 2, done.stdout)
        self.assertIn("migration-mismatch", done.stderr)
        self.assertEqual(files(self.root), before)
        self.assertTrue(self.legacy.exists())

    def test_migrate_completes_a_bundle_that_is_a_partial_copy(self):
        # an interrupted migration: some documents written, each equal to its JSON record
        kl._write_bundle(self.root, store(self.records[:2]))
        out = kl.migrate(self.root)
        self.assertEqual((out["status"], out["lessons"]), ("migrated", len(self.records)))
        self.assertFalse(self.legacy.exists())
        self.assertEqual(kl.load_store(self.root)["lessons"], self.records)

    def test_the_command_line(self):
        done = subprocess.run([sys.executable, str(RUNTIME_DIR / "knowledge.py"), "--root",
                               str(self.root), "migrate"], capture_output=True, text=True)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"{len(self.records)} lesson(s) verified record for record", done.stdout)
        self.assertIn("removed", done.stdout)
        listed = subprocess.run([sys.executable, str(RUNTIME_DIR / "knowledge.py"), "--root",
                                 str(self.root), "list"], capture_output=True, text=True)
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn(f"lessons        : {len(self.records)}", listed.stdout)

    def test_harvest_and_recall_report_the_bundle(self):
        kl.migrate(self.root)
        got = kl.recall(self.root, "s", "a.md")
        self.assertEqual(got["store"], "memory/lessons")
        self.assertEqual(got["store_digest"], kl.bundle_digest(self.root))
        out = kl.harvest(self.root)
        self.assertEqual(out["store"], "memory/lessons")
        self.assertEqual(out["store_digest"], kl.bundle_digest(self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
