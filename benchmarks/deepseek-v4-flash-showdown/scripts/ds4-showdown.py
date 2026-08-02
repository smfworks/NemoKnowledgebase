#!/usr/bin/env python3
"""
Local vs Cloud Showdown Benchmark
DeepSeek V4 Flash (local ds4 on DGX Spark) vs cloud models

Test Categories:
  1. Reasoning Quality (8 tests: math, logic, coding, knowledge, instruction)
  2. Tool Calling (3 tests: weather, calc, multi-tool)
  3. Latency & Throughput (varying output sizes)
  4. TTFT (streaming time to first token)
  5. Coding Challenge (write + verify a working function)

All tests run against each model's OpenAI-compatible API endpoint.
Output: JSON report + markdown summary table.
"""

import asyncio
import json
import time
import sys
import os
import httpx

# ─── CONFIGURATION ───────────────────────────────────────────────────────────

TIMEOUT = httpx.Timeout(120.0, connect=15.0)

# Load API keys from .env
ENV_PATH = os.path.expanduser("~/.hermes/profiles/nemo/.env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                os.environ.setdefault(k, v)

NVIDIA_KEY = os.environ.get("NVIDIA_API_KEY", "")
OLLAMA_KEY = os.environ.get("OLLAMA_API_KEY", "")

# Model lineup
MODELS = [
    {
        "name": "DeepSeek V4 Flash (Local ds4)",
        "short": "DSv4-Flash-Local",
        "endpoint": "http://spark-56bc:8888/v1",
        "model": "deepseek-v4-flash",
        "api_key": "dummy",
        "context": 65536,
        "category": "local",
    },
    {
        "name": "DeepSeek V4 Flash (NVIDIA NIM)",
        "short": "DSv4-Flash-NIM",
        "endpoint": "https://integrate.api.nvidia.com/v1",
        "model": "deepseek-ai/deepseek-v4-flash",
        "api_key": NVIDIA_KEY,
        "context": 131072,
        "category": "cloud-same-model",
    },
    {
        "name": "DeepSeek V4 Flash (Ollama Cloud)",
        "short": "DSv4-Flash-Ollama",
        "endpoint": "http://127.0.0.1:11434/v1",
        "model": "deepseek-v4-flash:cloud",
        "api_key": OLLAMA_KEY or "ollama",
        "context": 131072,
        "category": "cloud-same-model",
    },
    {
        "name": "DeepSeek V4 Pro (NVIDIA NIM)",
        "short": "DSv4-Pro-NIM",
        "endpoint": "https://integrate.api.nvidia.com/v1",
        "model": "deepseek-ai/deepseek-v4-pro",
        "api_key": NVIDIA_KEY,
        "context": 131072,
        "category": "cloud-competitor",
    },
    {
        "name": "Kimi K2.6 (NVIDIA NIM)",
        "short": "Kimi-K2.6-NIM",
        "endpoint": "https://integrate.api.nvidia.com/v1",
        "model": "moonshotai/kimi-k2.6",
        "api_key": NVIDIA_KEY,
        "context": 131072,
        "category": "cloud-competitor",
    },
    {
        "name": "GLM-5.2 (NVIDIA NIM)",
        "short": "GLM-5.2-NIM",
        "endpoint": "https://integrate.api.nvidia.com/v1",
        "model": "z-ai/glm-5.2",
        "api_key": NVIDIA_KEY,
        "context": 131072,
        "category": "cloud-competitor",
    },
    {
        "name": "MiniMax M3 (NVIDIA NIM)",
        "short": "MiniMax-M3-NIM",
        "endpoint": "https://integrate.api.nvidia.com/v1",
        "model": "minimaxai/minimax-m3",
        "api_key": NVIDIA_KEY,
        "context": 131072,
        "category": "cloud-competitor",
    },
]

# ─── TESTS ──────────────────────────────────────────────────────────────────

REASONING_TESTS = [
    ("math_basic", "What is 17 * 23? Show your work briefly.", "391", 1000),
    ("math_advanced", "Solve: if 3x + 7 = 22, what is x?", "5", 1000),
    ("logic", "All cats are mammals. Some mammals are pets. Can we conclude some cats are pets? Answer with clear reasoning.", "cannot", 1500),
    ("coding", "Write a Python function that reverses a linked list.", "def reverse", 2000),
    ("knowledge", "What is the capital of Australia?", "canberra", 500),
    ("reasoning", "If a train travels 60 km in 45 minutes, what is its speed in km/h?", "80", 1000),
    ("instruction", "List exactly 3 fruits. Number them 1 to 3. Nothing else.", "1.", 500),
    ("world_knowledge", "In what year did the Berlin Wall fall?", "1989", 500),
]

TOOL_TESTS = [
    {
        "label": "weather",
        "prompt": "What's the weather in Tokyo right now? Use the tool.",
        "tools": [
            {"type": "function", "function": {"name": "get_weather", "description": "Get current weather for a location",
             "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}}
        ],
        "expected_tool": "get_weather",
        "expected_arg": "tokyo",
    },
    {
        "label": "calc",
        "prompt": "Calculate 45 * 73 using the calculator tool.",
        "tools": [
            {"type": "function", "function": {"name": "calculate", "description": "Evaluate a math expression",
             "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}}
        ],
        "expected_tool": "calculate",
        "expected_arg": "45",
    },
    {
        "label": "multi_tool",
        "prompt": "What's the weather in Paris and what is 12 * 8? Use both tools.",
        "tools": [
            {"type": "function", "function": {"name": "get_weather", "description": "Get current weather for a location",
             "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}},
            {"type": "function", "function": {"name": "calculate", "description": "Evaluate a math expression",
             "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}}}
        ],
        "expected_tool": "get_weather",
        "expected_arg": "paris",
    },
]

CODING_CHALLENGE = "Write a complete Python function called `is_palindrome` that checks if a string is a palindrome. Include type hints, docstring, and handle edge cases (empty string, case sensitivity, spaces/punctuation). Return only the code."

LATENCY_PROMPT = "Write a detailed essay about the history of computing, from Babbage to modern AI."
TTFT_PROMPTS = [
    ("short", "What is 2+2?"),
    ("medium", "Explain how a CPU works in 3 paragraphs."),
    ("coding", "Write a Python function that reverses a linked list. Include type hints and docstring."),
]


async def chat_request(client, model_config, messages, max_tokens=1024, temperature=0.6, tools=None, stream=False):
    """Make a chat completion request to a model endpoint."""
    headers = {"Content-Type": "application/json"}
    if model_config["api_key"] and model_config["api_key"] != "dummy":
        headers["Authorization"] = f"Bearer {model_config['api_key']}"
    
    payload = {
        "model": model_config["model"],
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    
    url = f"{model_config['endpoint']}/chat/completions"
    start = time.perf_counter()
    
    try:
        if stream:
            first_token_time = None
            content = ""
            reasoning = ""
            async with client.stream("POST", url, json={**payload, "stream": True}, headers=headers, timeout=TIMEOUT) as resp:
                if resp.status_code != 200:
                    body = await resp.aread()
                    return {"error": f"HTTP {resp.status_code}: {body[:200]}"}, time.perf_counter() - start, None
                async for line in resp.aiter_lines():
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
                        delta = chunk.get("choices", [{}])[0].get("delta", {})
                        dc = delta.get("content", "")
                        dr = delta.get("reasoning_content", "") or delta.get("reasoning", "")
                        if dc or dr:
                            if first_token_time is None:
                                first_token_time = time.perf_counter()
                        if dc:
                            content += dc
                        if dr:
                            reasoning += dr
            elapsed = time.perf_counter() - start
            ttft = (first_token_time - start) if first_token_time else None
            return {"content": content, "reasoning": reasoning}, elapsed, ttft
        else:
            resp = await client.post(url, json=payload, headers=headers, timeout=TIMEOUT)
            elapsed = time.perf_counter() - start
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code}: {resp.text[:200]}"}, elapsed, None
            return resp.json(), elapsed, None
    except Exception as e:
        elapsed = time.perf_counter() - start
        return {"error": str(e)[:200]}, elapsed, None


async def test_reasoning(client, model_config):
    """Test 1: Reasoning quality — 8 tests."""
    results = []
    passed = 0
    for label, prompt, expected, max_tok in REASONING_TESTS:
        data, elapsed, _ = await chat_request(client, model_config,
            [{"role": "user", "content": prompt}], max_tokens=max_tok, temperature=0.3)
        if "error" in data:
            results.append({"test": label, "passed": False, "error": data["error"], "wall_time_s": round(elapsed, 2)})
            continue
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        content = (msg.get("content", "") or "") + (msg.get("reasoning_content", "") or "")
        is_pass = expected.lower() in content.lower()
        if is_pass:
            passed += 1
        usage = data.get("usage", {})
        results.append({
            "test": label, "passed": is_pass, "wall_time_s": round(elapsed, 2),
            "completion_tokens": usage.get("completion_tokens", 0),
            "content_preview": (msg.get("content", "") or "")[:120],
        })
    return {"passed": passed, "total": len(REASONING_TESTS), "tests": results}


async def test_tool_calling(client, model_config):
    """Test 2: Tool calling — 3 tests."""
    results = []
    passed = 0
    for tc in TOOL_TESTS:
        data, elapsed, _ = await chat_request(client, model_config,
            [{"role": "user", "content": tc["prompt"]}],
            max_tokens=2000, temperature=0.1, tools=tc["tools"])
        if "error" in data:
            results.append({"test": tc["label"], "passed": False, "error": data["error"], "wall_time_s": round(elapsed, 2)})
            continue
        choice = data.get("choices", [{}])[0]
        msg = choice.get("message", {})
        tool_calls = msg.get("tool_calls", [])
        made = len(tool_calls) > 0
        correct_tool = any(c.get("function", {}).get("name") == tc["expected_tool"] for c in tool_calls) if made else False
        all_args = " ".join(c.get("function", {}).get("arguments", "") for c in tool_calls) if tool_calls else ""
        correct_args = tc["expected_arg"].lower() in all_args.lower() if tool_calls else False
        is_pass = made and correct_tool and correct_args
        if is_pass:
            passed += 1
        results.append({
            "test": tc["label"], "passed": is_pass, "tool_calls_made": made,
            "correct_tool": correct_tool, "correct_args": correct_args,
            "num_calls": len(tool_calls), "wall_time_s": round(elapsed, 2),
        })
    return {"passed": passed, "total": len(TOOL_TESTS), "tests": results}


async def test_latency(client, model_config):
    """Test 3: Latency & throughput."""
    results = []
    for max_tokens in [128, 512, 1024]:
        data, elapsed, _ = await chat_request(client, model_config,
            [{"role": "user", "content": LATENCY_PROMPT}], max_tokens=max_tokens, temperature=0.7)
        if "error" in data:
            results.append({"max_tokens": max_tokens, "error": data["error"], "wall_time_s": round(elapsed, 2)})
            continue
        usage = data.get("usage", {})
        ct = usage.get("completion_tokens", 0)
        tps = ct / elapsed if elapsed > 0 else 0
        results.append({
            "max_tokens": max_tokens, "completion_tokens": ct,
            "wall_time_s": round(elapsed, 2), "tokens_per_second": round(tps, 1),
        })
    return results


async def test_ttft(client, model_config):
    """Test 4: TTFT via streaming."""
    results = []
    for label, prompt in TTFT_PROMPTS:
        data, elapsed, ttft = await chat_request(client, model_config,
            [{"role": "user", "content": prompt}], max_tokens=2000, temperature=0.6, stream=True)
        if "error" in data:
            results.append({"prompt": label, "error": data["error"], "wall_time_s": round(elapsed, 2)})
            continue
        content_len = len(data.get("content", ""))
        reasoning_len = len(data.get("reasoning", ""))
        results.append({
            "prompt": label,
            "ttft_ms": round(ttft * 1000, 1) if ttft else None,
            "total_time_s": round(elapsed, 2),
            "content_chars": content_len,
            "reasoning_chars": reasoning_len,
        })
    return results


async def test_coding(client, model_config):
    """Test 5: Coding challenge — generate and check for key elements."""
    data, elapsed, _ = await chat_request(client, model_config,
        [{"role": "user", "content": CODING_CHALLENGE}], max_tokens=2000, temperature=0.3)
    if "error" in data:
        return {"error": data["error"], "wall_time_s": round(elapsed, 2)}
    choice = data.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content", "") or ""
    usage = data.get("usage", {})
    # Check for key elements
    has_def = "def is_palindrome" in content
    has_docstring = '"""' in content or "'''" in content
    has_type_hints = "-> bool" in content or "-> bool:" in content
    has_lower = ".lower()" in content
    has_strip = ".strip()" in content or "replace" in content
    score = sum([has_def, has_docstring, has_type_hints, has_lower, has_strip])
    return {
        "wall_time_s": round(elapsed, 2),
        "completion_tokens": usage.get("completion_tokens", 0),
        "has_function": has_def,
        "has_docstring": has_docstring,
        "has_type_hints": has_type_hints,
        "has_case_handling": has_lower,
        "has_punctuation_handling": has_strip,
        "quality_score": f"{score}/5",
        "code_preview": content[:300],
    }


async def benchmark_model(model_config):
    """Run all tests against one model."""
    print(f"\n{'─' * 60}")
    print(f"Benchmarking: {model_config['name']}")
    print(f"{'─' * 60}")
    report = {"name": model_config["name"], "short": model_config["short"], "category": model_config["category"],
              "endpoint": model_config["endpoint"], "model": model_config["model"]}
    
    async with httpx.AsyncClient() as client:
        # Test 1: Reasoning
        print("  [1/5] Reasoning quality...")
        report["reasoning"] = await test_reasoning(client, model_config)
        print(f"        {report['reasoning']['passed']}/{report['reasoning']['total']} passed")
        
        # Test 2: Tool calling
        print("  [2/5] Tool calling...")
        report["tool_calling"] = await test_tool_calling(client, model_config)
        print(f"        {report['tool_calling']['passed']}/{report['tool_calling']['total']} passed")
        
        # Test 3: Latency
        print("  [3/5] Latency & throughput...")
        report["latency"] = await test_latency(client, model_config)
        for r in report["latency"]:
            if "tokens_per_second" in r:
                print(f"        {r['max_tokens']} tokens: {r['tokens_per_second']} tok/s in {r['wall_time_s']}s")
        
        # Test 4: TTFT
        print("  [4/5] TTFT (streaming)...")
        report["ttft"] = await test_ttft(client, model_config)
        for r in report["ttft"]:
            if "ttft_ms" in r:
                print(f"        {r['prompt']}: TTFT={r['ttft_ms']}ms")
        
        # Test 5: Coding challenge
        print("  [5/5] Coding challenge...")
        report["coding"] = await test_coding(client, model_config)
        if "quality_score" in report["coding"]:
            print(f"        Quality: {report['coding']['quality_score']}")
    
    return report


async def main():
    print("=" * 70)
    print("Local vs Cloud Showdown Benchmark")
    print(f"Models: {len(MODELS)}")
    print(f"Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    all_reports = []
    for model_config in MODELS:
        try:
            report = await benchmark_model(model_config)
            all_reports.append(report)
        except Exception as e:
            print(f"  ERROR benchmarking {model_config['name']}: {e}")
            all_reports.append({"name": model_config["name"], "error": str(e)})
    
    print("\n" + "=" * 70)
    print(f"Complete: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Model':<30} {'Reasoning':>10} {'Tools':>8} {'Coding':>8} {'TTFT(ms)':>10} {'tok/s':>8}")
    print("-" * 70)
    for r in all_reports:
        name = r.get("short", r.get("name", "??"))
        reasoning = f"{r.get('reasoning',{}).get('passed','?')}/{r.get('reasoning',{}).get('total','?')}" if "reasoning" in r else "ERR"
        tools = f"{r.get('tool_calling',{}).get('passed','?')}/{r.get('tool_calling',{}).get('total','?')}" if "tool_calling" in r else "ERR"
        coding = r.get("coding", {}).get("quality_score", "ERR") if "coding" in r else "ERR"
        ttft_vals = [t.get("ttft_ms") for t in r.get("ttft", []) if t.get("ttft_ms")]
        ttft_avg = f"{sum(ttft_vals)/len(ttft_vals):.0f}" if ttft_vals else "N/A"
        lat_vals = [l.get("tokens_per_second") for l in r.get("latency", []) if l.get("tokens_per_second")]
        lat_avg = f"{sum(lat_vals)/len(lat_vals):.1f}" if lat_vals else "N/A"
        print(f"{name:<30} {reasoning:>10} {tools:>8} {coding:>8} {ttft_avg:>10} {lat_avg:>8}")
    
    print("\n__JSON_REPORT_START__")
    print(json.dumps(all_reports, indent=2, default=str))
    print("__JSON_REPORT_END__")

if __name__ == "__main__":
    asyncio.run(main())