#!/usr/bin/env python3
"""Math-only Official A diagnostic for tencent/hy4: thinking ON (default effort high).
Not a ranking run. Compares against the effort=none 157 arms."""
import asyncio, json, os, sys, time, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from smf_bench.api_client import APIClient
from smf_bench.evaluators import get_evaluator
from smf_bench.test_registry import TestCase

ENDPOINT = os.environ.get("ENDPOINT", "https://openrouter.ai/api/v1")
MODEL = os.environ.get("MODEL", "tencent/hy4")
TIMEOUT = int(os.environ.get("TIMEOUT", "300"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "8192"))
SUITE = ROOT / "suites/quality/tier0_deterministic/math.yaml"
OUT = ROOT / "results" / f"math-think-on-hy4-{time.strftime('%Y%m%d_%H%M%S')}.json"


def load_tests():
    tests = []
    with open(SUITE) as f:
        for d in yaml.safe_load_all(f):
            if d is None:
                continue
            if isinstance(d, list):
                tests.extend(d)
            elif isinstance(d, dict):
                if "tests" in d and isinstance(d["tests"], list):
                    tests.extend(d["tests"])
                elif "id" in d or "test_id" in d:
                    tests.append(d)
    return tests


async def main():
    tests = load_tests()
    print(f"math tests: {len(tests)} thinking=ON (default effort high) max_tokens={MAX_TOKENS}", flush=True)
    rows = []
    t0 = time.time()
    passed = failed = errored = 0
    api_key = os.environ.get("OPENROUTER_API_KEY") or "dummy"
    async with APIClient(base_url=ENDPOINT, model=MODEL, timeout=TIMEOUT, api_key=api_key) as client:
        for i, test in enumerate(tests, 1):
            tid = test.get("id") or test.get("test_id")
            if "prompt" in test:
                messages = [{"role": "user", "content": test["prompt"]}]
            else:
                messages = test["messages"]
            mt = test.get("max_tokens") or MAX_TOKENS
            mt = max(int(mt), MAX_TOKENS)
            t1 = time.time()
            try:
                resp = await client.chat(
                    messages,
                    max_tokens=mt,
                    temperature=test.get("temperature", 0),
                )
                err = None
            except Exception as e:
                resp = None
                err = str(e)[:200]
            elapsed = time.time() - t1
            if err or resp is None or not resp.succeeded:
                errored += 1
                rows.append({"test_id": tid, "status": "error", "error": err, "elapsed": elapsed})
                print(f"  ERR {tid} {elapsed:.1f}s {err}", flush=True)
                continue
            tc = TestCase.from_dict(test)
            evaluator_name = test.get("evaluator", "text_contains")
            try:
                evaluator = get_evaluator(evaluator_name)
                result = evaluator(resp, tc)
                ok = bool(result.passed)
                detail = str(getattr(result, "detail", "") or getattr(result, "actual", ""))
            except Exception as e:
                ok, detail = False, f"evaluator error: {e}"
            status = "pass" if ok else "fail"
            if ok:
                passed += 1
            else:
                failed += 1
            usage = resp.usage or {}
            ctd = usage.get("completion_tokens_details") or {}
            rows.append({
                "test_id": tid, "status": status, "detail": str(detail)[:200],
                "elapsed": elapsed, "completion_tokens": usage.get("completion_tokens"),
                "reasoning_tokens": ctd.get("reasoning_tokens"),
                "cost": usage.get("cost"),
                "finish_reason": resp.finish_reason,
            })
            print(f"  {'PASS' if ok else 'FAIL'} {tid:45s} {elapsed:5.1f}s {str(detail)[:70]}", flush=True)

    dt = time.time() - t0
    summary = {"total": len(tests), "passed": passed, "failed": failed, "error": errored,
               "pass_rate": round(passed / len(tests) * 100, 1) if tests else 0, "wall_time_seconds": round(dt, 1)}
    out = {"tag": "math-think-on-hy4", "endpoint": ENDPOINT, "model": MODEL,
           "thinking": "on (default effort high, no explicit effort sent)",
           "max_tokens_floor": MAX_TOKENS, "summary": summary, "tests": rows}
    OUT.write_text(json.dumps(out, indent=2))
    print(json.dumps(summary, indent=2), flush=True)
    print(f"saved {OUT}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
