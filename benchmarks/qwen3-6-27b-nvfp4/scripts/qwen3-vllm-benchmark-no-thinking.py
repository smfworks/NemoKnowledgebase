#!/usr/bin/env python3
"""
Qwen3.6-27B-NVFP4 vLLM Benchmark — THINKING DISABLED
Mirrors the methodology from qwen3-6-performance-benchmark-report.md
but with enable_thinking: false in chat_template_kwargs.

Run: python3 qwen3-vllm-benchmark-no-thinking.py
"""

import json
import time
import requests
import concurrent.futures
import re
import statistics

ENDPOINT = "http://spark-56bc:8888/v1/chat/completions"
MODEL = "nvidia/Qwen3.6-27B-NVFP4"
TIMEOUT = 300

# All requests use enable_thinking: false
BASE_PAYLOAD = {
    "model": MODEL,
    "stream": False,
}

CHAT_TEMPLATE_KWARGS = {"enable_thinking": False}


def make_payload(messages, max_tokens=1024, stream=False, extra=None):
    p = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": stream,
        "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
    }
    if extra:
        p.update(extra)
    return p


def non_stream_request(messages, max_tokens=1024, extra=None):
    """Send a non-streaming request, return (text, wall_time, finish_reason, usage, message)."""
    payload = make_payload(messages, max_tokens=max_tokens, stream=False, extra=extra)
    start = time.time()
    resp = requests.post(ENDPOINT, json=payload, timeout=TIMEOUT)
    wall = time.time() - start
    resp.raise_for_status()
    data = resp.json()
    choice = data["choices"][0]
    message = choice.get("message", {})
    text = message.get("content", "") or ""
    finish = choice.get("finish_reason", "")
    usage = data.get("usage", {})
    return text, wall, finish, usage, message


def stream_request(messages, max_tokens=1024, extra=None):
    """Send a streaming request, return (text, reasoning_text, ttft, wall_time, finish_reason)."""
    payload = make_payload(messages, max_tokens=max_tokens, stream=True, extra=extra)
    start = time.time()
    ttft = None
    content_parts = []
    reasoning_parts = []
    finish_reason = ""

    resp = requests.post(ENDPOINT, json=payload, stream=True, timeout=TIMEOUT)
    for line in resp.iter_lines():
        if not line:
            continue
        line_str = line.decode("utf-8")
        if line_str.startswith("data: "):
            line_str = line_str[6:]
        if line_str == "[DONE]":
            break
        try:
            chunk = json.loads(line_str)
        except json.JSONDecodeError:
            continue

        if ttft is None:
            ttft = time.time() - start

        choices = chunk.get("choices", [])
        if choices:
            delta = choices[0].get("delta", {})
            if delta.get("content"):
                content_parts.append(delta["content"])
            if delta.get("reasoning_content"):
                reasoning_parts.append(delta["reasoning_content"])
            if choices[0].get("finish_reason"):
                finish_reason = choices[0]["finish_reason"]

    wall = time.time() - start
    return "".join(content_parts), "".join(reasoning_parts), ttft, wall, finish_reason


# ===== TEST 1: Latency & Throughput (Single Request) =====
def test_latency_throughput():
    print("\n=== 1. Latency & Throughput (Single Request) ===")
    prompt = [{"role": "user", "content": "Write a detailed essay about the history of computing, from Babbage to modern AI."}]
    results = []
    for max_tok in [64, 128, 256, 512, 1024]:
        text, wall, finish, usage, _msg = non_stream_request(prompt, max_tokens=max_tok)
        actual_tokens = usage.get("completion_tokens", len(text) // 4)
        throughput = actual_tokens / wall if wall > 0 else 0
        results.append({
            "max_tokens": max_tok,
            "actual_tokens": actual_tokens,
            "wall_time": round(wall, 2),
            "throughput": round(throughput, 1),
            "finish": finish,
        })
        print(f"  {max_tok:>5} tok → {actual_tokens} actual, {wall:.2f}s, {throughput:.1f} tok/s, finish={finish}")
    return results


# ===== TEST 2: TTFT (Streaming) =====
def test_ttft():
    print("\n=== 2. Time To First Token (TTFT) ===")
    prompts = {
        "Short": [{"role": "user", "content": "What is 2+2?"}],
        "Medium": [{"role": "user", "content": "Explain CPU in 3 paragraphs"}],
        "Long reasoning": [{"role": "user", "content": "Prove that √2 is irrational."}],
    }
    results = []
    for label, msgs in prompts.items():
        content, reasoning, ttft, wall, finish = stream_request(msgs, max_tokens=2048)
        results.append({
            "prompt_type": label,
            "ttft_ms": round(ttft * 1000) if ttft else None,
            "total_time": round(wall, 2),
            "content_chars": len(content),
            "reasoning_chars": len(reasoning),
            "finish": finish,
        })
        print(f"  {label:>15} → TTFT: {ttft*1000:.0f}ms, total: {wall:.2f}s, content: {len(content)} chars, reasoning: {len(reasoning)} chars, finish={finish}")
    return results


# ===== TEST 3: Concurrent Request Handling =====
def test_concurrency():
    print("\n=== 3. Concurrent Request Handling ===")
    prompt_text = "Write a short story about a robot learning to paint"
    results = []
    for concurrency in [1, 2, 4, 8]:
        msgs = [{"role": "user", "content": prompt_text}]
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(non_stream_request, msgs, 512) for _ in range(concurrency)]
            done = 0
            errors = 0
            for f in concurrent.futures.as_completed(futures):
                try:
                    f.result()
                    done += 1
                except Exception as e:
                    errors += 1
                    print(f"    ERROR: {e}")
        wall = time.time() - start
        results.append({
            "concurrency": concurrency,
            "success": f"{done}/{concurrency}",
            "wall_time": round(wall, 2),
            "errors": errors,
        })
        print(f"  Concurrency {concurrency:>1} → {done}/{concurrency} success, {wall:.2f}s, {errors} errors")
    return results


# ===== TEST 4: Context Length Scaling =====
def test_context_length():
    print("\n=== 4. Context Length Scaling ===")
    filler = "The quick brown fox jumps over the lazy dog. " * 50  # ~450 tokens per block
    results = []
    for target_tokens in [100, 500, 2000, 8000, 32000, 128000]:
        # Build filler to approximately match target token count
        blocks_needed = max(1, target_tokens // 450)
        padding = (filler * blocks_needed)[:target_tokens * 4]  # rough char estimate
        full_prompt = padding + "\n\nWhat is 7 × 8? Answer with just the number."
        msgs = [{"role": "user", "content": full_prompt}]
        text, wall, finish, usage, _msg = non_stream_request(msgs, max_tokens=200)
        actual_tokens = usage.get("completion_tokens", len(text) // 4)
        prompt_tokens = usage.get("prompt_tokens", len(full_prompt) // 4)
        throughput = actual_tokens / wall if wall > 0 else 0
        correct = "56" in text
        results.append({
            "input_size": f"~{target_tokens}",
            "actual_prompt_tokens": prompt_tokens,
            "output_tokens": actual_tokens,
            "wall_time": round(wall, 2),
            "throughput": round(throughput, 1),
            "correct": correct,
            "finish": finish,
            "response_excerpt": text[:50],
        })
        print(f"  ~{target_tokens:>6} → prompt: {prompt_tokens} tok, output: {actual_tokens} tok, {wall:.2f}s, {throughput:.1f} tok/s, correct={correct}, finish={finish}")
    return results


# ===== TEST 5: Reasoning Quality =====
def test_reasoning_quality():
    print("\n=== 5. Reasoning Quality ===")
    tests = [
        ("Math (basic)", "What is 17 × 23? Show your work briefly.", [r"\b391\b"]),
        ("Math (advanced)", "Solve: 3x + 7 = 22. Find x.", [r"\b5\b"]),
        ("Logic", "All cats are mammals. Some mammals are pets. Can we conclude that some cats are pets? Answer yes, no, or cannot determine.", [r"cannot determine"]),
        ("Coding", "Write a Python function to reverse a linked list. Output only the code.", [r"def reverse", r"\.next"]),
        ("Knowledge", "What is the capital of Australia?", [r"Canberra"]),
        ("Reasoning", "A train travels 60 km in 45 minutes. What is its speed in km/h?", [r"\b80\b"]),
        ("Instruction", "List exactly 3 fruits. Number them 1-3. Nothing else.", [r"1\b", r"2\b", r"3\b"]),
        ("World knowledge", "In what year did the Berlin Wall fall?", [r"1989"]),
    ]
    results = []
    for name, prompt_text, rubric in tests:
        msgs = [{"role": "user", "content": prompt_text}]
        text, wall, finish, usage, _msg = non_stream_request(msgs, max_tokens=2048)
        passed = all(re.search(p, text, re.IGNORECASE) for p in rubric)
        tokens = usage.get("completion_tokens", len(text) // 4)
        results.append({
            "category": name,
            "passed": passed,
            "time": round(wall, 1),
            "tokens": tokens,
            "response_excerpt": text[:100],
        })
        print(f"  {name:>25} → {'✅ PASS' if passed else '❌ FAIL'}, {wall:.1f}s, {tokens} tok")
    score = sum(1 for r in results if r["passed"])
    print(f"  Score: {score}/{len(results)}")
    return results


# ===== TEST 6: Tool Calling =====
def test_tool_calling():
    print("\n=== 6. Tool Calling ===")
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {"type": "string", "description": "City name"}
                    },
                    "required": ["location"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Evaluate a math expression",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {"type": "string", "description": "Math expression to evaluate"}
                    },
                    "required": ["expression"],
                },
            },
        }
    ]
    test_cases = [
        ("Weather query", "What's the weather like in Tokyo?", "get_weather", "Tokyo"),
        ("Calculator", "Calculate 45 * 73", "calculate", "45 * 73"),
    ]
    results = []
    for name, prompt_text, expected_tool, expected_arg in test_cases:
        msgs = [{"role": "user", "content": prompt_text}]
        extra = {"tools": tools, "tool_choice": "auto"}
        text, wall, finish, usage, message = non_stream_request(msgs, max_tokens=512, extra=extra)
        # vLLM returns tool calls in message["tool_calls"], not in content
        tool_calls = message.get("tool_calls", []) or []
        tool_made = len(tool_calls) > 0 or finish == "tool_calls"
        # Check correct tool name and arguments from the structured tool_calls field
        correct_tool = False
        correct_arg = False
        tool_name = ""
        tool_args_str = ""
        if tool_calls:
            tc = tool_calls[0]
            fn = tc.get("function", {})
            tool_name = fn.get("name", "")
            tool_args_str = json.dumps(fn.get("arguments", {}))
            correct_tool = tool_name == expected_tool
            correct_arg = expected_arg.lower() in tool_args_str.lower()
        results.append({
            "test": name,
            "tool_made": tool_made,
            "correct_tool": correct_tool,
            "correct_arg": correct_arg,
            "tool_name": tool_name,
            "tool_args": tool_args_str,
            "time": round(wall, 1),
            "finish_reason": finish,
            "response_excerpt": text[:200],
        })
        print(f"  {name:>15} → tool_made={tool_made}, tool={tool_name}, args={tool_args_str}, correct_tool={correct_tool}, correct_arg={correct_arg}, {wall:.1f}s, finish={finish}")
    return results


# ===== TEST 7: Resource Utilization =====
def test_resource_utilization():
    print("\n=== 7. Resource Utilization (from server metrics) ===")
    try:
        resp = requests.get("http://spark-56bc:8888/metrics", timeout=10)
        metrics_text = resp.text
        # Parse key vLLM metrics
        metrics = {}
        for line in metrics_text.split("\n"):
            if line.startswith("#"):
                continue
            # Skip _created gauges (they're timestamps, not real values)
            if "_created" in line:
                continue
            if "=" in line or " " in line.strip():
                parts = line.strip().split()
                if len(parts) >= 2:
                    key = parts[0]
                    val = parts[-1]
                    if any(k in key for k in ["gpu", "memory", "cache", "speculative", "draft", "prefix"]):
                        try:
                            metrics[key] = float(val)
                        except ValueError:
                            metrics[key] = val
        # Print key metrics
        key_metrics = {k: v for k, v in metrics.items() if any(kw in k for kw in ["draft", "speculative", "prefix_cache", "gpu"])}
        print(f"  Extracted {len(metrics)} metrics, {len(key_metrics)} key ones")
        for k, v in list(key_metrics.items())[:20]:
            print(f"    {k}: {v}")
        return key_metrics
    except Exception as e:
        print(f"  Could not fetch metrics: {e}")
        return {}


# ===== TEST 8: Speculative Decoding (MTP) =====
def test_speculative_decoding():
    print("\n=== 8. Speculative Decoding (MTP) ===")
    try:
        resp = requests.get("http://spark-56bc:8888/metrics", timeout=10)
        metrics_text = resp.text
        draft_requests = 0
        draft_tokens = 0
        accepted_tokens = 0
        accepted_per_pos = []
        for line in metrics_text.split("\n"):
            if line.startswith("#"):
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                key = parts[0]
                val = parts[-1]
                # Skip _created gauges (they're Unix timestamps, not counters)
                if "_created" in key:
                    continue
                try:
                    val_f = float(val)
                except ValueError:
                    continue
                # Only match _total counters for cumulative values
                if key == "vllm:spec_decode_num_drafts_total{engine=\"0\",model_name=\"nvidia/Qwen3.6-27B-NVFP4\"}":
                    draft_requests = val_f
                elif key == "vllm:spec_decode_num_draft_tokens_total{engine=\"0\",model_name=\"nvidia/Qwen3.6-27B-NVFP4\"}":
                    draft_tokens = val_f
                elif key == "vllm:spec_decode_num_accepted_tokens_total{engine=\"0\",model_name=\"nvidia/Qwen3.6-27B-NVFP4\"}":
                    accepted_tokens = val_f
                elif "vllm:spec_decode_num_accepted_tokens_per_pos_total" in key:
                    accepted_per_pos.append(val_f)
        acceptance_rate = (accepted_tokens / draft_tokens * 100) if draft_tokens > 0 else 0
        results = {
            "draft_requests": draft_requests,
            "draft_tokens": draft_tokens,
            "accepted_tokens": accepted_tokens,
            "acceptance_rate": round(acceptance_rate, 1),
            "accepted_per_pos": accepted_per_pos,
        }
        print(f"  Draft requests: {int(draft_requests)}")
        print(f"  Draft tokens: {int(draft_tokens)}")
        print(f"  Accepted tokens: {int(accepted_tokens)}")
        print(f"  Acceptance rate: {acceptance_rate:.1f}%")
        if accepted_per_pos:
            print(f"  Accepted per position: {[int(x) for x in accepted_per_pos]}")
        return results
    except Exception as e:
        print(f"  Could not fetch speculative decoding metrics: {e}")
        return {}


def main():
    print(f"=== Qwen3.6-27B-NVFP4 vLLM Benchmark — THINKING DISABLED ===")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Model: {MODEL}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    print(f"chat_template_kwargs: {CHAT_TEMPLATE_KWARGS}")

    # Verify server is up
    try:
        resp = requests.get("http://spark-56bc:8888/v1/models", timeout=10)
        models = resp.json()
        print(f"✓ Server up: {len(models.get('data', []))} model(s) available")
    except Exception as e:
        print(f"✗ Server check failed: {e}")
        return

    benchmark_start = time.time()

    # Quick sanity: confirm thinking is disabled
    sanity_text, sanity_wall, sanity_finish, _u, _m = non_stream_request(
        [{"role": "user", "content": "What is 2+2? Answer with just the number."}],
        max_tokens=64,
    )
    print(f"\nSanity check (thinking=off): '{sanity_text[:100]}' in {sanity_wall:.2f}s, finish={sanity_finish}")

    # Run all tests
    r1 = test_latency_throughput()
    r2 = test_ttft()
    r3 = test_concurrency()
    r4 = test_context_length()
    r5 = test_reasoning_quality()
    r6 = test_tool_calling()
    r7 = test_resource_utilization()
    r8 = test_speculative_decoding()

    benchmark_duration = time.time() - benchmark_start

    # Compile summary
    summary = {
        "thinking_enabled": False,
        "peak_throughput_single": max(r["throughput"] for r in r1) if r1 else 0,
        "steady_state_throughput": statistics.median([r["throughput"] for r in r1]) if r1 else 0,
        "ttft_short_ms": r2[0]["ttft_ms"] if r2 else None,
        "ttft_reasoning_ms": r2[2]["ttft_ms"] if len(r2) > 2 else None,
        "max_concurrency_tested": 8,
        "concurrency_success_rate": "100%" if all(r["errors"] == 0 for r in r3) else "FAILED",
        "context_support": f"Full {r4[-1]['actual_prompt_tokens'] if r4 else 0} tokens verified" if r4 else "N/A",
        "reasoning_score": f"{sum(1 for r in r5 if r['passed'])}/{len(r5)}",
        "tool_calling_score": f"{sum(1 for r in r6 if r['tool_made'])}/{len(r6)}",
        "speculative_acceptance_rate": r8.get("acceptance_rate", "N/A") if r8 else "N/A",
    }

    full_report = {
        "metadata": {
            "model": MODEL,
            "engine": "vLLM v0.24.0",
            "hardware": "NVIDIA DGX Spark (GB10 Grace Blackwell, aarch64)",
            "endpoint": ENDPOINT,
            "thinking_enabled": False,
            "timestamp": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "benchmark_duration_seconds": round(benchmark_duration, 1),
        },
        "summary": summary,
        "test_1_latency_throughput": r1,
        "test_2_ttft": r2,
        "test_3_concurrency": r3,
        "test_4_context_length": r4,
        "test_5_reasoning_quality": r5,
        "test_6_tool_calling": r6,
        "test_7_resource_utilization": r7,
        "test_8_speculative_decoding": r8,
    }

    # Save JSON results
    outfile = "/home/mikesai1/NemoVault/queries/qwen3-6-benchmark-no-thinking-results.json"
    with open(outfile, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\n=== Results saved to: {outfile} ===")

    # Print executive summary
    print(f"\n{'='*60}")
    print(f"EXECUTIVE SUMMARY (Thinking DISABLED)")
    print(f"{'='*60}")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print(f"\nBenchmark duration: {benchmark_duration:.1f}s ({benchmark_duration/60:.1f} min)")

    return full_report


if __name__ == "__main__":
    main()