#!/usr/bin/env python
"""Run the unit suite in parallel worker processes.

`python -m unittest discover -s tests` runs every test serially and takes about 26 minutes.
Most of that is a handful of modules whose tests each build a git fixture, so one process
per module is bounded by the slowest module. This runner splits each module into chunks of
a few tests and runs the chunks in separate processes, which keeps every CPU busy. Results
are the same unittest results; the total test count is summed from each chunk's own
`Ran N tests` line and compared with the number of tests discovered.

    python tools/run_tests_parallel.py                 # every tests/test_*.py
    python tools/run_tests_parallel.py -j 4            # four at a time
    python tools/run_tests_parallel.py --chunk 0       # one process per module
    python tools/run_tests_parallel.py test_model_tier test_gate_rollback
    python tools/run_tests_parallel.py --expect 642    # fail unless exactly 642 ran

Exit status is 0 only when every module passed and, if `--expect` is given, the summed test
count matches. A module that crashes before unittest reports a count is a failure.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import time
import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"
RAN = re.compile(r"^Ran (\d+) tests? in ([\d.]+)s", re.M)


def discover(names: list[str]) -> list[tuple[str, list[str]]]:
    """Return (module, [test ids]) pairs, ids resolved the way `discover -s tests` resolves them."""
    sys.path.insert(0, str(TESTS))
    modules = [n[:-3] if n.endswith(".py") else n for n in names] or         sorted(p.stem for p in TESTS.glob("test_*.py"))
    loader = unittest.TestLoader()
    found = []
    for module in modules:
        ids: list[str] = []
        stack = [loader.loadTestsFromName(module)]
        while stack:
            item = stack.pop()
            if isinstance(item, unittest.TestSuite):
                stack.extend(reversed(list(item)))
            else:
                ids.append(item.id())
        found.append((module, ids))
    return found


def run_chunk(module: str, ids: list[str]) -> dict:
    started = time.monotonic()
    # PYTHONPATH=tests makes sibling imports (`from test_omn_agent import ...`) resolve exactly
    # as they do under `discover -s tests`; a dotted `tests.<name>` would not.
    env = {**os.environ, "PYTHONPATH": os.pathsep.join(
        [str(TESTS)] + ([os.environ["PYTHONPATH"]] if os.environ.get("PYTHONPATH") else []))}
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", *ids],
        cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    out = proc.stdout + proc.stderr
    ran = RAN.search(out)
    return {
        "module": module,
        "ok": proc.returncode == 0 and ran is not None,
        "tests": int(ran.group(1)) if ran else 0,
        "seconds": time.monotonic() - started,
        "output": out,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("modules", nargs="*", help="test module names; default is every tests/test_*.py")
    ap.add_argument("-j", "--jobs", type=int, default=min(16, os.cpu_count() or 1),
                    help="processes at once (default: min(16, cpu count))")
    ap.add_argument("--chunk", type=int, default=4,
                    help="tests per process; 0 runs each module in one process (default: 4)")
    ap.add_argument("--expect", type=int, help="fail unless exactly this many tests ran")
    args = ap.parse_args()

    found = discover(args.modules)
    discovered = sum(len(ids) for _, ids in found)
    # Largest files first, so the slow modules start immediately instead of last.
    found.sort(key=lambda m: (TESTS / f"{m[0]}.py").stat().st_size, reverse=True)
    units = []
    for module, ids in found:
        size = args.chunk if args.chunk > 0 else max(len(ids), 1)
        units += [(module, ids[i:i + size]) for i in range(0, len(ids), size)]

    started = time.monotonic()
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = [pool.submit(run_chunk, m, ids) for m, ids in units]
        for fut in as_completed(futures):
            r = fut.result()
            results.append(r)
            if not r["ok"]:
                print(f"FAIL {r['module']:<34} {r['tests']:>4} tests {r['seconds']:>7.1f}s", flush=True)

    wall = time.monotonic() - started
    total = sum(r["tests"] for r in results)
    failed = [r for r in results if not r["ok"]]
    by_module: dict[str, list] = {}
    for r in results:
        by_module.setdefault(r["module"], []).append(r)
    for module, rs in sorted(by_module.items(), key=lambda kv: -sum(r["seconds"] for r in kv[1])):
        print(f"{'ok  ' if all(r['ok'] for r in rs) else 'FAIL'} {module:<34} "
              f"{sum(r['tests'] for r in rs):>4} tests {sum(r['seconds'] for r in rs):>7.1f}s of work "
              f"in {len(rs)} process(es)")
    for r in failed:
        print(f"\n=== {r['module']} ===\n{r['output']}")
    print(f"\n{len(by_module) - len({r['module'] for r in failed})}/{len(by_module)} modules passed, "
          f"{total} of {discovered} discovered tests ran, {wall:.1f}s wall "
          f"({sum(r['seconds'] for r in results):.1f}s of work, -j {args.jobs}, chunk {args.chunk})")
    if total != discovered:
        print(f"FAIL: discovered {discovered} tests but {total} reported; a process died before reporting")
        return 1
    if args.expect is not None and total != args.expect:
        print(f"FAIL: expected {args.expect} tests, ran {total}")
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
