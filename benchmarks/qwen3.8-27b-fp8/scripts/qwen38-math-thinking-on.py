#!/usr/bin/env python3
"""Re-run the math suite (30 tests) with thinking ON for Qwen3.8-27B-FP8.

Companion to the Official A calibration (which ran thinking OFF, math 15/30).
This run sends enable_thinking=true to quantify how much the reasoning budget
recovers on the math category. Reuses smf_bench evaluators + APIClient.
"""
import asyncio, json, os, sys, time, yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from smf_bench.api_client import APIClient
from smf_bench.evaluators import get_evaluator
from smf_bench.test_registry import TestCase

ENDPOINT = "http://spark-56bc:30000/v1"
MODEL = "Qwen3.8-27B-FP8"
MATH_SUITE = "suites/quality/tier0_deterministic/math.yaml"
TAG = "cal-qwen38-27b-fp8-math-thinking-on"
SERVE_RECIPE = "SMF-Spark-SGLang-qwen38-27b-fp8-eagle"


def load_math_tests():
    with open(MATH_SUITE) as f:
        docs = list(yaml.safe_load_all(f))
    return [d for d in docs if isinstance(d, dict) and d.get("id")]


def _save(results, by_cat, start):
    out = {
        "tag": TAG, "endpoint": ENDPOINT, "model": MODEL,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "thinking": "on", "core_profile": "math_only",
        "serve_recipe_id": SERVE_RECIPE,
        "wall_time_seconds": round(time.time() - start, 1),
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "pass"),
            "failed": sum(1 for r in results if r["status"] == "fail"),
            "error": sum(1 for r in results if r["status"] == "error"),
        },
        "by_category": by_cat, "tests": results,
    }
    path = f"results/stage1_{TAG}_{time.strftime('%Y%m%d_%H%M%S')}.json"
    json.dump(out, open(path, "w"), indent=2)
    print(f"  [saved] {path}")


async def run():
    tests = load_math_tests()
    print(f"Loaded {len(tests)} math tests")
    results = []
    by_cat = {"math": {"pass": 0, "fail": 0, "error": 0}}
    start = time.time()

    async with APIClient(base_url=ENDPOINT, model=MODEL) as client:
        for i, test in enumerate(tests, 1):
            test_id = test["id"]
            prompt = test["prompt"]
            messages = [{"role": "user", "content": prompt}]
            max_tokens = test.get("max_tokens", 4096)
            temperature = test.get("temperature", 0.3)

            # thinking ON: explicitly enable (model default is on)
            chat_kwargs = {
                "max_tokens": max_tokens,
                "temperature": temperature,
                "chat_template_kwargs": {"enable_thinking": True},
            }

            resp = await client.chat(messages, **chat_kwargs)

            if resp.error:
                by_cat["math"]["error"] += 1
                results.append({"test_id": test_id, "category": "math",
                                "status": "error", "error": resp.error[:200],
                                "elapsed": resp.elapsed})
                print(f"  ❌ ERR  {test_id:30s} {resp.error[:50]}")
                continue

            tc = TestCase.from_dict(test)
            evaluator = get_evaluator(test.get("evaluator", "regex_match"))
            result = evaluator(resp, tc)
            passed = result.passed
            detail = result.detail
            status = "pass" if passed else "fail"
            by_cat["math"][status] += 1
            results.append({"test_id": test_id, "category": "math",
                            "status": status, "detail": detail,
                            "elapsed": resp.elapsed,
                            "tokens_used": getattr(resp, "tokens_used", None)})
            mark = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {mark} {test_id:30s} {detail[:60]}")

            if i % 10 == 0:
                _save(results, by_cat, start)

    _save(results, by_cat, start)
    p = by_cat["math"]["pass"]
    print(f"\nMath (thinking ON): {p}/{len(tests)} passed ({p/len(tests)*100:.1f}%)")


if __name__ == "__main__":
    asyncio.run(run())
