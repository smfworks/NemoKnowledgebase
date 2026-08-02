#!/usr/bin/env python3
"""
DeepSeek V4 Flash Benchmark Suite — adapted for ds4/DwarfStar4 engine.
Runs against the OpenAI-compatible /v1 API on the DGX Spark.

Test Categories:
  1. Latency & Throughput (single request, varying output sizes)
  2. TTFT (Time To First Token) via streaming + engine timings
  3. Concurrent request handling (1, 2, 4, 8 parallel)
  4. Context length scaling (100, 500, 2K, 8K, 32K input tokens)
  5. Reasoning quality tests (math, logic, coding, knowledge)
  6. Tool-calling capability tests
  7. Engine metrics (ds4-server timings from response)

Output: JSON report printed to stdout between __JSON_REPORT_START__ and __JSON_REPORT_END__
"""

import asyncio
import json
import time
import sys
import httpx

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
BASE_URL = "http://127.0.0.1:8888/v1"
MODEL = "deepseek-v4-flash"
TIMEOUT = httpx.Timeout(300.0, connect=10.0)

async def chat_completion(client, messages, max_tokens=1024, temperature=0.6, stream=False, tools=None):
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    start = time.perf_counter()
    if stream:
        first_token_time = None
        full_content = ""
        reasoning_content = ""
        async with client.stream("POST", f"{BASE_URL}/chat/completions",
                                  json={**payload, "stream": True}, timeout=TIMEOUT) as resp:
            async for line in resp.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try:
                        chunk = json.loads(line[6:])
                    except json.JSONDecodeError:
                        continue
                    delta = chunk.get("choices", [{}])[0].get("delta", {})
                    if "content" in delta and delta["content"] and first_token_time is None:
                        first_token_time = time.perf_counter()
                    if "content" in delta and delta["content"]:
                        full_content += delta["content"]
                    if "reasoning" in delta and delta["reasoning"]:
                        reasoning_content += delta["reasoning"]
        elapsed = time.perf_counter() - start
        ttft = (first_token_time - start) if first_token_time else None
        return {"content": full_content, "reasoning": reasoning_content}, elapsed, ttft
    else:
        resp = await client.post(f"{BASE_URL}/chat/completions", json=payload, timeout=TIMEOUT)
        elapsed = time.perf_counter() - start
        return resp.json(), elapsed, None

async def test_latency_throughput(client):
    """Test 1: Varying output lengths — measure decode speed and engine timings."""
    results = []
    prompt = "Write a detailed essay about the history of computing, from Babbage to modern AI."
    for max_tokens in [64, 128, 256, 512, 1024]:
        data, elapsed, _ = await chat_completion(client, [{"role": "user", "content": prompt}], max_tokens=max_tokens, temperature=0.7)
        choice = data.get("choices", [{}])[0]
        usage = data.get("usage", {})
        timings = data.get("timings", {})
        ct = usage.get("completion_tokens", 0)
        tps = ct / elapsed if elapsed > 0 else 0
        results.append({
            "max_tokens": max_tokens,
            "completion_tokens": ct,
            "wall_time_s": round(elapsed, 3),
            "tokens_per_second": round(tps, 2),
            "engine_ttft_ms": timings.get("ttft_ms"),
            "engine_decode_tok_s": timings.get("decode_tok_s"),
            "engine_prefill_tok_s": timings.get("prefill_tok_s"),
            "spec_accept_rate": timings.get("spec_accept_rate"),
            "tok_per_step": timings.get("tok_per_step"),
            "finish_reason": choice.get("finish_reason"),
        })
        print(f"  [latency] max_tokens={max_tokens}: {ct} tokens in {elapsed:.2f}s = {tps:.1f} tok/s (engine decode: {timings.get('decode_tok_s', 'N/A')} tok/s, spec: {timings.get('spec_accept_rate', 'N/A')})")
    return results

async def test_ttft(client):
    """Test 2: Time to first token via streaming."""
    results = []
    cases = [
        ("short", "What is 2+2?", 500),
        ("medium", "Explain how a CPU works in 3 paragraphs.", 1500),
        ("long_reasoning", "Prove that the square root of 2 is irrational.", 3000),
        ("coding", "Write a Python function that reverses a linked list. Include type hints and docstring.", 2000),
    ]
    for label, prompt, max_tok in cases:
        data, elapsed, ttft = await chat_completion(client, [{"role": "user", "content": prompt}], max_tokens=max_tok, temperature=0.6, stream=True)
        content_len = len(data.get("content", ""))
        reasoning_len = len(data.get("reasoning", ""))
        results.append({
            "prompt_label": label,
            "ttft_ms": round(ttft * 1000, 1) if ttft else None,
            "total_time_s": round(elapsed, 3),
            "content_chars": content_len,
            "reasoning_chars": reasoning_len,
        })
        ttft_str = f"TTFT={ttft*1000:.0f}ms" if ttft else "TTFT=N/A"
        print(f"  [ttft] {label}: {ttft_str}, total={elapsed:.2f}s, content={content_len}c, reasoning={reasoning_len}c")
    return results

async def test_concurrency(client):
    """Test 3: Concurrent requests — 1, 2, 4, 8 parallel."""
    results = []
    prompt = "Write a short story about a robot learning to paint. Make it vivid and emotional."
    for concurrency in [1, 2, 4, 8]:
        async def single(idx=0):
            return await chat_completion(client, [{"role": "user", "content": f"{prompt} (variant {idx})"}],
                                         max_tokens=512, temperature=0.7, stream=True)
        start = time.perf_counter()
        responses = await asyncio.gather(*[single(i) for i in range(concurrency)], return_exceptions=True)
        wall = time.perf_counter() - start
        ok = [r for r in responses if not isinstance(r, Exception)]
        fail = [r for r in responses if isinstance(r, Exception)]
        total_tokens = 0
        for r in ok:
            # streaming returns (data_dict, elapsed, ttft)
            if isinstance(r, tuple) and len(r) >= 1 and isinstance(r[0], dict):
                total_tokens += len(r[0].get("content", "")) // 4  # rough token estimate
        agg_tps = total_tokens / wall if wall > 0 and total_tokens > 0 else 0
        results.append({
            "concurrency": concurrency,
            "successful": len(ok),
            "failed": len(fail),
            "wall_time_s": round(wall, 3),
            "approx_aggregate_tps": round(agg_tps, 1),
        })
        print(f"  [concurrency] n={concurrency}: {len(ok)}/{concurrency} ok, wall={wall:.2f}s, ~{agg_tps:.1f} agg tok/s")
    return results

async def test_context_scaling(client):
    """Test 4: Context length scaling — 100 to 32K input tokens."""
    results = []
    filler = "The quick brown fox jumps over the lazy dog. " * 10
    for target in [100, 500, 2000, 8000, 32000]:
        text = filler * (target // 100)
        prompt = f"Read the following text. At the end, answer: what is 7 multiplied by 8?\n\nText:\n{text}\n\nQuestion: What is 7 multiplied by 8?"
        data, elapsed, _ = await chat_completion(client, [{"role": "user", "content": prompt}], max_tokens=200, temperature=0.6)
        choice = data.get("choices", [{}])[0]
        usage = data.get("usage", {})
        timings = data.get("timings", {})
        ct = usage.get("completion_tokens", 0)
        pt = usage.get("prompt_tokens", 0)
        tps = ct / elapsed if elapsed > 0 and ct > 0 else 0
        results.append({
            "target_tokens": target,
            "actual_prompt_tokens": pt,
            "completion_tokens": ct,
            "wall_time_s": round(elapsed, 3),
            "tps": round(tps, 2),
            "engine_ttft_ms": timings.get("ttft_ms"),
            "engine_prefill_tok_s": timings.get("prefill_tok_s"),
            "engine_decode_tok_s": timings.get("decode_tok_s"),
            "spec_accept_rate": timings.get("spec_accept_rate"),
        })
        print(f"  [context] ~{target} tokens: {pt} prompt + {ct} output in {elapsed:.2f}s = {tps:.1f} tok/s (TTFT: {timings.get('ttft_ms', 'N/A')}ms)")
    return results

async def test_reasoning_quality(client):
    """Test 5: Reasoning quality — 8 cases."""
    cases = [
        ("math_basic", "What is 17 * 23? Show your work briefly.", "391", 1000),
        ("math_advanced", "Solve: if 3x + 7 = 22, what is x?", "5", 1500),
        ("logic", "All cats are mammals. Some mammals are pets. Can we conclude some cats are pets?", "cannot determine", 1500),
        ("coding", "Write a Python function that reverses a linked list.", "def reverse", 2000),
        ("knowledge", "What is the capital of Australia?", "canberra", 1000),
        ("reasoning", "If a train travels 60 km in 45 minutes, what is its speed in km/h?", "80", 1500),
        ("instruction", "List exactly 3 fruits. Number them 1 to 3. Nothing else.", "1.", 800),
        ("world_knowledge", "In what year did the Berlin Wall fall?", "1989", 800),
    ]
    results = []
    for cat, prompt, expected, max_tok in cases:
        data, elapsed, _ = await chat_completion(client, [{"role": "user", "content": prompt}], max_tokens=max_tok, temperature=0.6)
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        content = (msg.get("content", "") or "")
        reasoning = (msg.get("reasoning_content", "") or "")
        combined = content + reasoning
        passed = expected.lower() in combined.lower()
        timings = data.get("timings", {})
        results.append({
            "category": cat,
            "passed": passed,
            "wall_time_s": round(elapsed, 3),
            "content_preview": content[:200],
            "has_reasoning": bool(reasoning),
            "engine_decode_tok_s": timings.get("decode_tok_s"),
        })
        print(f"  [quality] {cat}: {'PASS' if passed else 'FAIL'} ({elapsed:.1f}s)")
    return results

async def test_tool_calling(client):
    """Test 6: Tool calling capability."""
    tools = [
        {"type": "function", "function": {"name": "get_weather", "description": "Get current weather for a location",
         "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "City name"}}, "required": ["location"]}}},
        {"type": "function", "function": {"name": "calculate", "description": "Evaluate a math expression",
         "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Math expression to evaluate"}}, "required": ["expression"]}}},
    ]
    cases = [
        ("weather", "What's the weather in Tokyo right now? Use the tool.", "get_weather", "tokyo"),
        ("calc", "Calculate 45 * 73 using the calculator tool.", "calculate", "45"),
        ("multi_tool", "What's the weather in Paris and what is 12 * 8? Use both tools.", "get_weather", "paris"),
    ]
    results = []
    for label, prompt, exp_tool, exp_args in cases:
        data, elapsed, _ = await chat_completion(client, [{"role": "user", "content": prompt}],
                                                  max_tokens=2000, temperature=0.1, tools=tools)
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tc = msg.get("tool_calls", [])
        made = len(tc) > 0
        correct_tool = any(c.get("function", {}).get("name") == exp_tool for c in tc) if made else False
        all_args = " ".join(c.get("function", {}).get("arguments", "") for c in tc) if tc else ""
        correct_args = exp_args.lower() in all_args.lower() if tc else False
        finish = choice.get("finish_reason", "")
        results.append({
            "label": label,
            "tool_call_made": made,
            "correct_tool": correct_tool,
            "correct_args": correct_args,
            "num_tool_calls": len(tc),
            "finish_reason": finish,
            "wall_time_s": round(elapsed, 3),
        })
        status = "PASS" if made and correct_tool and correct_args else "FAIL"
        print(f"  [tools] {label}: {status} — {len(tc)} calls, finish={finish} ({elapsed:.1f}s)")
    return results

async def test_engine_stats(client):
    """Test 7: Engine-level stats from ds4-server."""
    results = {}
    # ds4 doesn't have /metrics like vLLM, but the /v1/models endpoint has info
    try:
        resp = await client.get(f"{BASE_URL}/models", timeout=10)
        if resp.status_code == 200:
            models = resp.json()
            results["models"] = models
    except Exception as e:
        results["models_error"] = str(e)[:200]
    return results

async def main():
    print("=" * 70)
    print(f"DeepSeek V4 Flash Benchmark | {BASE_URL} | {MODEL}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    report = {"model": MODEL, "endpoint": BASE_URL, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"), "tests": {}}
    async with httpx.AsyncClient() as client:
        print("\n─ Test 1: Latency & Throughput ─────────────")
        report["tests"]["latency_throughput"] = await test_latency_throughput(client)
        print("\n─ Test 2: TTFT (Streaming) ──────────────────")
        report["tests"]["ttft"] = await test_ttft(client)
        print("\n─ Test 3: Concurrency ──────────────────────")
        report["tests"]["concurrency"] = await test_concurrency(client)
        print("\n─ Test 4: Context Scaling ──────────────────")
        report["tests"]["context_scaling"] = await test_context_scaling(client)
        print("\n─ Test 5: Reasoning Quality ────────────────")
        report["tests"]["reasoning_quality"] = await test_reasoning_quality(client)
        print("\n─ Test 6: Tool Calling ─────────────────────")
        report["tests"]["tool_calling"] = await test_tooling(client) if False else await test_tool_calling(client)
        print("\n─ Test 7: Engine Stats ─────────────────────")
        report["tests"]["engine_stats"] = await test_engine_stats(client)
    print("\n" + "=" * 70)
    print(f"Complete: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("__JSON_REPORT_START__")
    print(json.dumps(report, indent=2, default=str))
    print("__JSON_REPORT_END__")

if __name__ == "__main__":
    asyncio.run(main())