#!/usr/bin/env python3
"""Math-only diagnostic: thinking ON for DSV4 Vision-Exp. Not Official A."""
import asyncio, json, os, sys, time, yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from smf_bench.api_client import APIClient
from smf_bench.evaluators import get_evaluator
from smf_bench.test_registry import TestCase

ENDPOINT = os.environ.get("ENDPOINT", "http://spark-56bc:8888/v1")
MODEL = os.environ.get("MODEL", "deepseek-v4-flash-vision-exp")
TIMEOUT = int(os.environ.get("TIMEOUT", "300"))
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "8192"))
SUITE = ROOT / "suites/quality/tier0_deterministic/math.yaml"
OUT = ROOT / "results" / f"math-think-on-dsv4v-{time.strftime('%Y%m%d_%H%M%S')}.json"


def load_tests():
    tests = []
    with open(SUITE) as f:
        for d in yaml.safe_load_all(f):
            if not d:
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
    print(f"math tests: {len(tests)} thinking=ON max_tokens={MAX_TOKENS}", flush=True)
    rows = []
    t0 = time.time()
    async with APIClient(base_url=ENDPOINT, model=MODEL, timeout=TIMEOUT) as client:
        for test in tests:
            tid = test.get("id") or test.get("test_id")
            messages = [{"role": "user", "content": test["prompt"]}] if "prompt" in test else test["messages"]
            mt = max(int(test.get("max_tokens") or MAX_TOKENS), MAX_TOKENS)
            t1 = time.time()
            try:
                resp = await client.chat(
                    messages,
                    max_tokens=mt,
                    temperature=test.get("temperature", 0),
                    chat_template_kwargs={"thinking": True},
                )
                err = None
            except Exception as e:
                resp, err = None, str(e)
            elapsed = time.time() - t1
            if err:
                passed, detail, score, tokens, text, reasoning = False, f"ERROR: {err}", 0.0, 0, "", ""
            else:
                result = get_evaluator(test.get("evaluator", "regex_match"))(resp, TestCase.from_dict(test))
                passed, detail, score = result.passed, result.detail, result.score
                text = (resp.text or "")[:400]
                reasoning = (resp.reasoning or "")[:200]
                tokens = getattr(resp, "tokens_used", None) or getattr(resp, "completion_tokens", None) or 0
            status = "pass" if passed else "fail"
            print(f"  {'✅' if passed else '❌'} {tid:32} {elapsed:6.1f}s {detail}", flush=True)
            rows.append({"test_id": tid, "status": status, "elapsed": elapsed, "detail": detail, "tokens_used": tokens, "content_preview": text, "reasoning_preview": reasoning})
            if len(rows) % 5 == 0:
                OUT.write_text(json.dumps({"n": len(rows), "passed": sum(1 for r in rows if r["status"]=="pass"), "tests": rows}, indent=2))
    wall = time.time() - t0
    passed = sum(1 for r in rows if r["status"] == "pass")
    payload = {"tag": "diag-math-think-on-dsv4v", "thinking": "on", "n": len(rows), "passed": passed, "failed": len(rows)-passed, "pass_rate": round(100.0*passed/len(rows),1) if rows else 0, "wall_time_seconds": wall, "tests": rows}
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"DONE {passed}/{len(rows)} ({payload['pass_rate']}%) wall={wall:.0f}s -> {OUT}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
