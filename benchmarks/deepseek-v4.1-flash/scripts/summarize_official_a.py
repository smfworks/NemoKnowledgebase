#!/usr/bin/env python3
"""Summarize a completed Official A stage1 JSON for the V4.1 Flash report."""
from __future__ import annotations

import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def main(path: str) -> None:
    d = json.loads(Path(path).read_text())
    tests = d.get("tests", [])
    print("tag", d.get("tag"))
    print("model", d.get("model"))
    print("thinking", d.get("thinking"))
    print("recipe", d.get("serve_recipe_id"))
    print("profile", d.get("core_profile"))
    print("standard", d.get("standard_version"))
    print("wall_s", d.get("wall_time_seconds"))
    print("summary", d.get("summary"))
    print("by_category", json.dumps(d.get("by_category"), indent=2))

    diff_stats = defaultdict(lambda: {"pass": 0, "total": 0, "fail": 0, "error": 0})
    for t in tests:
        parts = t["test_id"].split(".")
        diff = parts[2] if len(parts) >= 3 else "other"
        if t.get("category") in ("writing", "tool_calling") or t["test_id"].startswith("writing") or t["test_id"].startswith("tool"):
            diff = "other"
        diff_stats[diff]["total"] += 1
        st = t.get("status")
        if st == "pass":
            diff_stats[diff]["pass"] += 1
        elif st == "fail":
            diff_stats[diff]["fail"] += 1
        else:
            diff_stats[diff]["error"] += 1
    print("difficulty", dict(diff_stats))

    fails = [t for t in tests if t.get("status") != "pass"]
    print("n_fail_or_err", len(fails))
    syntax = [t for t in tests if "SyntaxError" in (t.get("detail") or "")]
    regex = [t for t in tests if t.get("status") != "pass" and "Regex" in (t.get("detail") or "")]
    structural = [t for t in tests if t.get("status") != "pass" and "Expected" in (t.get("detail") or "")]
    empty = [t for t in tests if t.get("status") != "pass" and not (t.get("response") or t.get("output") or "")]
    print("syntax", len(syntax), "regex", len(regex), "structural", len(structural))
    print("FAILS")
    for t in fails:
        print(f"  {t.get('status'):5s} {t['test_id']:40s} {t.get('elapsed')}s {(t.get('detail') or '')[:90]}")

    passed = [t["elapsed"] for t in tests if t.get("status") == "pass" and isinstance(t.get("elapsed"), (int, float))]
    all_e = [t["elapsed"] for t in tests if isinstance(t.get("elapsed"), (int, float))]
    if all_e:
        print("latency_all mean", round(statistics.mean(all_e), 2), "median", round(statistics.median(all_e), 2), "max", round(max(all_e), 2))
    if passed:
        print("latency_pass mean", round(statistics.mean(passed), 2), "median", round(statistics.median(passed), 2))


if __name__ == "__main__":
    main(sys.argv[1])
