#!/usr/bin/env python3
"""Official A via OpenRouter Batch API (for :batch slugs that 404 on sync chat).

Usage:
  python3 -u scripts/run_official_a_or_batch.py \\
    --model openai/gpt-6-astra-pro:batch \\
    --tag cal-gpt6-astra-pro-batch-strict-v01 \\
    --thinking-effort none
"""
from __future__ import annotations

import argparse
import functools
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
print = functools.partial(print, flush=True)

from run_stage1 import (  # noqa: E402
    CORE_PROFILES,
    STANDARD_VERSION,
    _save_results,
    _serve_recipe_id,
    load_tests,
)
from smf_bench.api_client import APIResponse  # noqa: E402
from smf_bench.evaluators import get_evaluator  # noqa: E402
from smf_bench.test_registry import TestCase  # noqa: E402


def load_key() -> str:
    k = os.environ.get("OPENROUTER_API_KEY")
    if k:
        return k
    env = Path.home() / ".hermes" / ".env"
    for line in env.read_text().splitlines():
        if line.startswith("OPENROUTER_API_KEY="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY not found")


def http_json(method: str, url: str, payload=None, timeout: int = 180):
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {load_key()}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://www.smfclearinghouse.com",
            "X-Title": "SMF Official A OpenRouter batch",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read().decode()
            return r.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode()[:12000]
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {"raw": raw}
        return e.code, parsed


def item_to_response(item: dict) -> APIResponse:
    if item.get("error"):
        return APIResponse(error=json.dumps(item["error"])[:500], elapsed=0.0)
    resp = item.get("response") or {}
    code = resp.get("status_code")
    body = resp.get("body") or {}
    if code and code != 200:
        return APIResponse(
            error=f"HTTP {code}: {json.dumps(body)[:400]}",
            elapsed=0.0,
            raw=body,
        )
    msg = ((body.get("choices") or [{}])[0].get("message") or {})
    usage = body.get("usage") or {}
    reasoning = msg.get("reasoning") or msg.get("reasoning_content") or ""
    return APIResponse(
        text=msg.get("content") or "",
        reasoning=reasoning,
        tool_calls=msg.get("tool_calls") or [],
        usage=usage if isinstance(usage, dict) else {},
        elapsed=0.0,
        finish_reason=((body.get("choices") or [{}])[0].get("finish_reason") or ""),
        raw=body,
    )


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--tag", required=True)
    p.add_argument("--core-profile", default="strict_v01")
    p.add_argument("--thinking-effort", default="none")
    p.add_argument("--poll-s", type=int, default=20)
    p.add_argument("--timeout-s", type=int, default=86400)
    args = p.parse_args()

    if args.core_profile not in CORE_PROFILES:
        print("unknown profile", args.core_profile)
        return 1

    suites_dir = ROOT / "suites"
    all_tests = []
    for path, label in CORE_PROFILES[args.core_profile]:
        full = suites_dir / path.replace("suites/", "")
        tests = load_tests(str(full))
        print(f"  Loaded {len(tests):3d} {label} tests")
        all_tests.extend([(t, label) for t in tests])
    print(f"Total: {len(all_tests)} tests")
    print(f"Model: {args.model}")
    print(f"Tag:   {args.tag}")
    print(f"Thinking effort: {args.thinking_effort}")
    print(f"serve_recipe_id: {_serve_recipe_id()}")

    requests = []
    for test, _label in all_tests:
        max_tokens = test.get("max_tokens", 1024)
        body = {
            "messages": [{"role": "user", "content": test["prompt"]}],
            "max_tokens": max_tokens,
            "include_reasoning": True,
        }
        if args.thinking_effort:
            body["reasoning"] = {"effort": args.thinking_effort}
        tools = (test.get("metadata") or {}).get("tools")
        if tools:
            body["tools"] = tools
        requests.append({"custom_id": test["id"], "body": body})

    payload = {
        "endpoint": "/v1/chat/completions",
        "model": args.model,
        "requests": requests,
    }

    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_json = results_dir / f"stage1_{args.tag}_{stamp}.json"
    submit_path = results_dir / f"{args.tag}.batch_submit.json"

    t0 = time.perf_counter()
    status, submitted = http_json("POST", "https://openrouter.ai/api/beta/batches", payload)
    submit_path.write_text(json.dumps(submitted, indent=2))
    print("submit_http", status, "id", submitted.get("id"), "batch_status", submitted.get("status"))
    if status not in (200, 201, 202) or not submitted.get("id"):
        print("SUBMIT FAIL", json.dumps(submitted)[:2000])
        return 1

    batch_id = submitted["id"]
    (results_dir / f"{args.tag}.batch_id.txt").write_text(batch_id)
    terminal = {"completed", "failed", "expired", "cancelled"}
    last = submitted
    deadline = time.time() + args.timeout_s
    while time.time() < deadline:
        time.sleep(args.poll_s)
        http, last = http_json("GET", f"https://openrouter.ai/api/beta/batches/{batch_id}")
        (results_dir / f"{args.tag}.batch_status.json").write_text(json.dumps(last, indent=2))
        st = last.get("status")
        print(f"poll http={http} status={st} counts={last.get('request_counts')} elapsed={time.perf_counter()-t0:.1f}s")
        if st in terminal:
            break
    else:
        print("TIMEOUT waiting for batch", batch_id)
        return 1

    (results_dir / f"{args.tag}.batch_final.json").write_text(json.dumps(last, indent=2))
    elapsed = time.perf_counter() - t0
    print("batch_terminal", last.get("status"), "usage", last.get("usage"), "wall", round(elapsed, 1))

    by_id = {item.get("custom_id"): item for item in (last.get("results") or [])}
    by_cat: dict = {}
    all_res: list = []
    for test, suite_label in all_tests:
        test_id = test["id"]
        category = test.get("category", suite_label)
        by_cat.setdefault(category, {"pass": 0, "fail": 0, "error": 0})
        item = by_id.get(test_id)
        if item is None:
            print(f"  ❌ ERR  {test_id:45s} [{category:14s}] missing from batch results")
            by_cat[category]["error"] += 1
            all_res.append({
                "test_id": test_id, "category": category, "suite": suite_label,
                "status": "error", "error": "missing from batch results", "elapsed": 0.0,
            })
            continue
        api_resp = item_to_response(item)
        if api_resp.error:
            print(f"  ❌ ERR  {test_id:45s} [{category:14s}] {api_resp.error[:50]}")
            by_cat[category]["error"] += 1
            all_res.append({
                "test_id": test_id, "category": category, "suite": suite_label,
                "status": "error", "error": api_resp.error[:200], "elapsed": api_resp.elapsed,
            })
            continue
        evaluator_name = test.get("evaluator", "text_contains")
        try:
            evaluator = get_evaluator(evaluator_name)
        except KeyError:
            print(f"  ⚠️ SKIP {test_id:45s} [{category:14s}] unknown evaluator {evaluator_name}")
            by_cat[category]["error"] += 1
            continue
        tc = TestCase.from_dict(test)
        result = evaluator(api_resp, tc)
        passed = bool(result.passed)
        detail = result.detail
        if passed:
            by_cat[category]["pass"] += 1
            print(f"  ✅ PASS {test_id:45s} [{category:14s}] {detail[:60]}")
            status_s = "pass"
        else:
            by_cat[category]["fail"] += 1
            print(f"  ❌ FAIL {test_id:45s} [{category:14s}] {str(detail)[:60]}")
            status_s = "fail"
        usage = api_resp.usage or {}
        tokens = usage.get("total_tokens") or usage.get("completion_tokens") or 0
        all_res.append({
            "test_id": test_id, "category": category, "suite": suite_label,
            "status": status_s, "passed": passed, "score": result.score,
            "detail": str(detail)[:400],
            "elapsed": api_resp.elapsed,
            "tokens_used": tokens,
            "evaluator": evaluator_name,
        })

    output = _save_results(
        str(out_json), args.tag, "https://openrouter.ai/api/beta/batches",
        args.model, False, elapsed, by_cat, all_res,
        core_profile=args.core_profile, thinking="off",
    )
    print()
    print("=" * 70)
    print(f"RESULTS BY CATEGORY — {args.tag}")
    print("=" * 70)
    for cat, counts in sorted(by_cat.items()):
        tot = counts["pass"] + counts["fail"] + counts["error"]
        rate = 100 * counts["pass"] / tot if tot else 0
        print(f"  {cat:16s}: {counts['pass']:3d}/{tot:3d} passed ({rate:5.1f}%)  [fail={counts['fail']}, err={counts['error']}]")
    s = output["summary"]
    print("  " + "─" * 50)
    print(f"  TOTAL           : {s['passed']:3d}/{s['total']:3d} passed ({s['pass_rate']:5.1f}%)  [fail={s['failed']}, err={s['error']}]")
    print(f"  Wall time: {elapsed:.1f}s")
    print("=" * 70)
    print("Results saved to:", out_json)
    print("Batch usage:", last.get("usage"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
