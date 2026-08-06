#!/usr/bin/env python3
"""
Strix Halo (Radeon 8060S) LLM Inference Benchmark
==================================================
Comprehensive benchmark of local LLM inference on AMD Ryzen AI MAX+ 395
with Radeon 8060S (gfx1151) integrated GPU.

Tests:
1. Model Capacity Map — VRAM footprint, load time, max context
2. Single-Request Performance — TTFT, tok/s across prompt lengths
3. Concurrency — 1/4/8/16 parallel requests
4. Sustained Load / Thermal — 60min continuous generation
5. Real Agent Workloads — multi-turn, tool calling, code gen, long context

All telemetry via sysfs (no rocm-smi dependency).
"""

import json
import os
import re
import subprocess
import sys
import time
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

# ============================================================
# Configuration
# ============================================================

OLLAMA_HOST = "http://127.0.0.1:11434"
GPU_SYSFS = "/sys/class/drm/card1/device"
RESULTS_DIR = "/home/mikesai1/workspace/strix-halo-bench/results"

# Local models to benchmark (ordered by size)
LOCAL_MODELS = [
    "nemotron-3-nano:4b",
    "gemma4:e4b",
    "gpt-oss:20b",
]

# Cloud models for comparison
CLOUD_MODELS = [
    "glm-5.2:cloud",
    "deepseek-v4-flash:cloud",
]

# Test prompt lengths (in approximate tokens)
SHORT_PROMPT = "Explain quantum entanglement in exactly 3 sentences."
MEDIUM_PROMPT = "Write a detailed comparison of vLLM and Ollama for local LLM inference. Cover architecture, performance characteristics, memory efficiency, and use cases. Provide at least 5 paragraphs."
LONG_PROMPT = "You are a senior software engineer. Write a complete Python implementation of a thread-safe LRU cache with: (1) O(1) get and put operations, (2) configurable max size, (3) eviction callbacks, (4) statistics tracking (hit rate, miss rate, total operations), (5) a decorator for automatic caching of function results, (6) context manager support for scoped caching, (7) pickle serialization support. Include comprehensive docstrings, type hints, and at least 10 unit tests using pytest. The implementation should handle edge cases like: zero-size cache, negative size, concurrent access from multiple threads, and serialization of non-picklable objects. Make the code production-ready."

CODE_GEN_PROMPT = "Write a complete, working Python implementation of a binary search tree with insert, delete, search, and in-order traversal. Include type hints and docstrings. Make it production-ready."

TOOL_CALL_PROMPT = """You have access to the following tools:

1. get_weather(location: str) - Get current weather for a location
2. search_web(query: str) - Search the web
3. calculate(expression: str) - Evaluate a math expression

User request: What's the weather in Tokyo and what's 15% of 2400?

Use the appropriate tools to answer this. Format your response as JSON with tool_calls."""

MULTI_TURN_PROMPTS = [
    "I'm building a REST API in Python. What framework should I use?",
    "Great, let's go with FastAPI. Show me a basic endpoint setup.",
    "Now add authentication using JWT tokens to that setup.",
    "How would I deploy this with Docker? Show the Dockerfile.",
]

# ============================================================
# GPU Telemetry (via sysfs)
# ============================================================

def gpu_vram_total():
    try:
        with open(f"{GPU_SYSFS}/mem_info_vram_total") as f:
            return int(f.read().strip()) / (1024**3)
    except:
        return -1

def gpu_vram_used():
    try:
        with open(f"{GPU_SYSFS}/mem_info_vram_used") as f:
            return int(f.read().strip()) / (1024**3)
    except:
        return -1

def gpu_vram_free():
    try:
        return gpu_vram_total() - gpu_vram_used()
    except:
        return -1

def gpu_temp():
    try:
        # Try various hwmon paths
        import glob
        for path in glob.glob(f"{GPU_SYSFS}/hwmon/hwmon*/temp1_input"):
            with open(path) as f:
                return int(f.read().strip()) / 1000.0
        return -1
    except:
        return -1

def gpu_busy():
    try:
        with open(f"{GPU_SYSFS}/gpu_busy_percent") as f:
            return int(f.read().strip())
    except:
        return -1

def gpu_gtt_total():
    try:
        with open(f"{GPU_SYSFS}/mem_info_gtt_total") as f:
            return int(f.read().strip()) / (1024**3)
    except:
        return -1

def gpu_gtt_used():
    try:
        with open(f"{GPU_SYSFS}/mem_info_gtt_used") as f:
            return int(f.read().strip()) / (1024**3)
    except:
        return -1

def system_ram():
    try:
        with open("/proc/meminfo") as f:
            lines = f.readlines()
        info = {}
        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                info[parts[0].rstrip(':')] = int(parts[1]) * 1024  # bytes
        total = info.get('MemTotal', 0) / (1024**3)
        avail = info.get('MemAvailable', 0) / (1024**3)
        free = info.get('MemFree', 0) / (1024**3)
        cached = info.get('Cached', 0) / (1024**3)
        return {"total_gb": total, "available_gb": avail, "free_gb": free, "cached_gb": cached}
    except:
        return {}

def cpu_info():
    try:
        with open("/proc/cpuinfo") as f:
            content = f.read()
        model = re.search(r'model name\s*:\s*(.+)', content)
        cores = re.search(r'cpu cores\s*:\s*(\d+)', content)
        threads = len(re.findall(r'processor\s*:', content))
        return {
            "model": model.group(1).strip() if model else "unknown",
            "cores": int(cores.group(1)) if cores else 0,
            "threads": threads,
        }
    except:
        return {}

def snapshot_gpu():
    """Take a complete GPU/system snapshot."""
    return {
        "timestamp": datetime.now().isoformat(),
        "vram_total_gb": round(gpu_vram_total(), 2),
        "vram_used_gb": round(gpu_vram_used(), 2),
        "vram_free_gb": round(gpu_vram_total() - gpu_vram_used(), 2),
        "gtt_total_gb": round(gpu_gtt_total(), 2),
        "gtt_used_gb": round(gpu_gtt_used(), 2),
        "temp_c": round(gpu_temp(), 1),
        "gpu_busy_pct": gpu_busy(),
        "ram": system_ram(),
    }

# ============================================================
# Ollama API Client
# ============================================================

def ollama_generate(model, prompt, options=None, stream=False):
    """Call Ollama /api/generate endpoint. Tracks both 'response' and 'thinking' fields."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
    }
    if options:
        payload["options"] = options
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            if stream:
                chunks = []
                first_token_time = None      # first token of ANY kind (thinking or content)
                first_content_time = None    # first content (non-thinking) token
                first_thinking_time = None   # first thinking token
                start = time.time()
                for line in resp:
                    if line.strip():
                        chunk = json.loads(line)
                        content = chunk.get("response", "")
                        thinking = chunk.get("thinking", "")
                        if (content or thinking) and first_token_time is None:
                            first_token_time = time.time()
                        if thinking and first_thinking_time is None:
                            first_thinking_time = time.time()
                        if content and first_content_time is None:
                            first_content_time = time.time()
                        chunks.append(chunk)
                        if chunk.get("done"):
                            break
                end = time.time()
                # Combine
                full_response = "".join(c.get("response", "") for c in chunks)
                full_thinking = "".join(c.get("thinking", "") for c in chunks)
                final = chunks[-1] if chunks else {}
                eval_count = final.get("eval_count", 0)
                eval_dur = final.get("eval_duration", 0)
                prompt_eval_count = final.get("prompt_eval_count", 0)
                prompt_eval_dur = final.get("prompt_eval_duration", 0)
                return {
                    "response": full_response,
                    "thinking": full_thinking,
                    "response_len": len(full_response),
                    "thinking_len": len(full_thinking),
                    "total_time_s": end - start,
                    "ttft_s": (first_token_time - start) if first_token_time else None,
                    "ttft_content_s": (first_content_time - start) if first_content_time else None,
                    "ttft_thinking_s": (first_thinking_time - start) if first_thinking_time else None,
                    "eval_count": eval_count,
                    "eval_duration_ns": eval_dur,
                    "prompt_eval_count": prompt_eval_count,
                    "prompt_eval_duration_ns": prompt_eval_dur,
                    "load_duration_ns": final.get("load_duration", 0),
                    "tokens_per_s": eval_count / (eval_dur / 1e9) if eval_dur > 0 else 0,
                    "prompt_tokens_per_s": prompt_eval_count / (prompt_eval_dur / 1e9) if prompt_eval_dur > 0 else 0,
                    "done": final.get("done", False),
                }
            else:
                result = json.loads(resp.read())
                return result
    except Exception as e:
        return {"error": str(e)}

def ollama_chat(model, messages, options=None, stream=False):
    """Call Ollama /api/chat endpoint. Tracks both 'response' and 'thinking' fields."""
    payload = {
        "model": model,
        "messages": messages,
        "stream": stream,
    }
    if options:
        payload["options"] = options
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            if stream:
                chunks = []
                first_token_time = None
                first_content_time = None
                first_thinking_time = None
                start = time.time()
                for line in resp:
                    if line.strip():
                        chunk = json.loads(line)
                        msg = chunk.get("message", {})
                        content = msg.get("content", "")
                        thinking = msg.get("thinking", "")
                        if (content or thinking) and first_token_time is None:
                            first_token_time = time.time()
                        if thinking and first_thinking_time is None:
                            first_thinking_time = time.time()
                        if content and first_content_time is None:
                            first_content_time = time.time()
                        chunks.append(chunk)
                        if chunk.get("done"):
                            break
                end = time.time()
                full_response = "".join(c.get("message", {}).get("content", "") for c in chunks)
                full_thinking = "".join(c.get("message", {}).get("thinking", "") for c in chunks)
                final = chunks[-1] if chunks else {}
                eval_count = final.get("eval_count", 0)
                eval_dur = final.get("eval_duration", 0)
                prompt_eval_count = final.get("prompt_eval_count", 0)
                prompt_eval_dur = final.get("prompt_eval_duration", 0)
                return {
                    "response": full_response,
                    "thinking": full_thinking,
                    "response_len": len(full_response),
                    "thinking_len": len(full_thinking),
                    "total_time_s": end - start,
                    "ttft_s": (first_token_time - start) if first_token_time else None,
                    "ttft_content_s": (first_content_time - start) if first_content_time else None,
                    "ttft_thinking_s": (first_thinking_time - start) if first_thinking_time else None,
                    "eval_count": eval_count,
                    "eval_duration_ns": eval_dur,
                    "prompt_eval_count": prompt_eval_count,
                    "prompt_eval_duration_ns": prompt_eval_dur,
                    "load_duration_ns": final.get("load_duration", 0),
                    "tokens_per_s": eval_count / (eval_dur / 1e9) if eval_dur > 0 else 0,
                    "prompt_tokens_per_s": prompt_eval_count / (prompt_eval_dur / 1e9) if prompt_eval_dur > 0 else 0,
                    "done": final.get("done", False),
                }
            else:
                result = json.loads(resp.read())
                return result
    except Exception as e:
        return {"error": str(e)}

def ollama_ps():
    """Get loaded models status."""
    try:
        with urllib.request.urlopen(f"{OLLAMA_HOST}/api/ps", timeout=10) as resp:
            return json.loads(resp.read())
    except:
        return {"models": []}

def ollama_show(model):
    """Get model info."""
    payload = json.dumps({"name": model}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_HOST}/api/show",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# Test 1: Model Capacity Map
# ============================================================

def test_capacity_map():
    print("\n" + "="*60)
    print("TEST 1: MODEL CAPACITY MAP")
    print("="*60)
    
    results = []
    
    # Baseline GPU state
    baseline = snapshot_gpu()
    print(f"\nBaseline GPU: VRAM {baseline['vram_used_gb']:.1f}/{baseline['vram_total_gb']:.1f} GB, "
          f"Temp {baseline['temp_c']}°C")
    
    for model in LOCAL_MODELS:
        print(f"\n--- Loading {model} ---")
        
        # Unload any models first
        try:
            subprocess.run(["ollama", "run", model, ""], 
                         input="", timeout=5, capture_output=True)
        except:
            pass
        
        # Get model info
        info = ollama_show(model)
        model_size = info.get("size", 0) / (1024**3) if "size" in info else 0
        quant = info.get("quantize_level", "unknown") if isinstance(info.get("quantize_level"), str) else "unknown"
        params = info.get("details", {}).get("parameter_size", "unknown")
        arch = info.get("details", {}).get("architecture", "unknown")
        
        print(f"  Size: {model_size:.1f} GB, Quant: {quant}, Params: {params}, Arch: {arch}")
        
        # Measure cold load + simple generation
        gpu_before = snapshot_gpu()
        start = time.time()
        
        result = ollama_generate(
            model, 
            "Say hello in exactly 3 words.",
            options={"num_predict": 20, "temperature": 0.1},
            stream=True
        )
        
        load_time = time.time() - start
        gpu_after = snapshot_gpu()
        
        vram_delta = gpu_after["vram_used_gb"] - gpu_before["vram_used_gb"]
        gtt_delta = gpu_after["gtt_used_gb"] - gpu_before["gtt_used_gb"]
        
        entry = {
            "model": model,
            "size_gb": round(model_size, 2),
            "quantization": quant,
            "parameter_size": params,
            "architecture": arch,
            "load_time_s": round(load_time, 2),
            "vram_before_gb": gpu_before["vram_used_gb"],
            "vram_after_gb": gpu_after["vram_used_gb"],
            "vram_delta_gb": round(vram_delta, 2),
            "gtt_before_gb": gpu_before["gtt_used_gb"],
            "gtt_after_gb": gpu_after["gtt_used_gb"],
            "gtt_delta_gb": round(gtt_delta, 2),
            "vram_free_after_gb": gpu_after["vram_free_gb"],
            "temp_after_c": gpu_after["temp_c"],
            "response": result.get("response", "")[:200],
            "eval_count": result.get("eval_count", 0),
            "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
            "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
            "error": result.get("error"),
        }
        results.append(entry)
        
        print(f"  Load time: {load_time:.2f}s")
        print(f"  VRAM delta: {vram_delta:+.2f} GB (now {gpu_after['vram_used_gb']:.1f} GB used, {gpu_after['vram_free_gb']:.1f} GB free)")
        print(f"  GTT delta: {gtt_delta:+.2f} GB")
        print(f"  TTFT: {result.get('ttft_s', 'N/A')}")
        print(f"  Tok/s: {result.get('tokens_per_s', 0):.1f}")
        print(f"  Response: {result.get('response', '')[:100]}")
        if result.get("error"):
            print(f"  ⚠️ ERROR: {result['error']}")
        
        # Unload model
        try:
            req = urllib.request.Request(
                f"{OLLAMA_HOST}/api/generate",
                data=json.dumps({"model": model, "keep_alive": 0}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
        except:
            pass
        time.sleep(2)  # Let VRAM settle
    
    return results

# ============================================================
# Test 2: Single-Request Performance
# ============================================================

def test_single_request_performance():
    print("\n" + "="*60)
    print("TEST 2: SINGLE-REQUEST PERFORMANCE")
    print("="*60)
    
    prompts = {
        "short": ("Short (≈20 tok prompt)", SHORT_PROMPT),
        "medium": ("Medium (≈50 tok prompt)", MEDIUM_PROMPT),
        "long": ("Long (≈150 tok prompt)", LONG_PROMPT),
        "code_gen": ("Code Gen (≈100 tok prompt)", CODE_GEN_PROMPT),
    }
    
    results = []
    
    for model in LOCAL_MODELS:
        print(f"\n=== {model} ===")
        for prompt_key, (label, prompt) in prompts.items():
            print(f"\n  [{label}]")
            
            gpu_before = snapshot_gpu()
            start = time.time()
            
            result = ollama_generate(
                model, prompt,
                options={"num_predict": 2048, "temperature": 0.3, "top_p": 0.9},
                stream=True,
            )
        
            total_time = time.time() - start
            gpu_after = snapshot_gpu()
        
            entry = {
                "model": model,
                "prompt_type": prompt_key,
                "prompt_label": label,
                "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
                "ttft_content_s": round(result.get("ttft_content_s", 0), 4) if result.get("ttft_content_s") else None,
                "ttft_thinking_s": round(result.get("ttft_thinking_s", 0), 4) if result.get("ttft_thinking_s") else None,
                "thinking_len": result.get("thinking_len", 0),
                "total_time_s": round(total_time, 2),
                "eval_count": result.get("eval_count", 0),
                "prompt_eval_count": result.get("prompt_eval_count", 0),
                "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
                "prompt_tokens_per_s": round(result.get("prompt_tokens_per_s", 0), 2),
                "response_len": result.get("response_len", 0),
                "gpu_busy_pct": gpu_after["gpu_busy_pct"],
                "temp_before_c": gpu_before["temp_c"],
                "temp_after_c": gpu_after["temp_c"],
                "vram_used_gb": gpu_after["vram_used_gb"],
                "error": result.get("error"),
            }
            results.append(entry)
            
            print(f"    TTFT: {entry['ttft_s']}s | Total: {entry['total_time_s']}s | "
                  f"Tok/s: {entry['tokens_per_s']} | Eval: {entry['eval_count']} tok | "
                  f"Temp: {gpu_before['temp_c']}→{gpu_after['temp_c']}°C")
            if result.get("error"):
                print(f"    ⚠️ ERROR: {result['error']}")
        
        # Unload model between models
        try:
            req = urllib.request.Request(
                f"{OLLAMA_HOST}/api/generate",
                data=json.dumps({"model": model, "keep_alive": 0}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
        except:
            pass
        time.sleep(2)
    
    return results

# ============================================================
# Test 3: Concurrency
# ============================================================

def test_concurrency():
    print("\n" + "="*60)
    print("TEST 3: CONCURRENCY")
    print("="*60)
    
    concurrency_levels = [1, 2, 4, 8]
    prompt = "Write a short paragraph about artificial intelligence. Keep it to 4-5 sentences."
    
    results = []
    
    # Use gpt-oss:20b as primary model for concurrency test (largest local)
    # Also test nemotron-3-nano:4b for comparison
    test_models = ["nemotron-3-nano:4b", "gpt-oss:20b"]
    
    for model in test_models:
        print(f"\n=== {model} ===")
        
        for n in concurrency_levels:
            print(f"\n  Concurrency: {n}")
            gpu_before = snapshot_gpu()
            start = time.time()
            
            def single_request(idx):
                req_start = time.time()
                r = ollama_generate(
                    model, f"{prompt}\n\n(Request #{idx+1})",
                    options={"num_predict": 1024, "temperature": 0.3},
                    stream=True,
                )
                req_time = time.time() - req_start
                return {
                    "idx": idx,
                    "ttft_s": round(r.get("ttft_s", 0), 4) if r.get("ttft_s") else None,
                    "total_time_s": round(req_time, 2),
                    "eval_count": r.get("eval_count", 0),
                    "tokens_per_s": round(r.get("tokens_per_s", 0), 2),
                    "error": r.get("error"),
                }
            
            with ThreadPoolExecutor(max_workers=n) as pool:
                futures = [pool.submit(single_request, i) for i in range(n)]
                request_results = [f.result() for f in as_completed(futures)]
            
            total_wall = time.time() - start
            gpu_after = snapshot_gpu()
            
            # Aggregate
            successful = [r for r in request_results if not r.get("error")]
            failed = [r for r in request_results if r.get("error")]
            ttfts = [r["ttft_s"] for r in successful if r["ttft_s"]]
            tps = [r["tokens_per_s"] for r in successful if r["tokens_per_s"] > 0]
            times = [r["total_time_s"] for r in successful]
            
            entry = {
                "model": model,
                "concurrency": n,
                "wall_time_s": round(total_wall, 2),
                "successful": len(successful),
                "failed": len(failed),
                "ttft_avg_s": round(sum(ttfts)/len(ttfts), 4) if ttfts else None,
                "ttft_max_s": round(max(ttfts), 4) if ttfts else None,
                "tok_s_avg": round(sum(tps)/len(tps), 2) if tps else 0,
                "tok_s_max": round(max(tps), 2) if tps else 0,
                "req_time_avg_s": round(sum(times)/len(times), 2) if times else 0,
                "req_time_max_s": round(max(times), 2) if times else 0,
                "aggregate_tok_s": round(sum(r["eval_count"] for r in successful) / total_wall, 2) if total_wall > 0 else 0,
                "gpu_busy_pct": gpu_after["gpu_busy_pct"],
                "temp_before_c": gpu_before["temp_c"],
                "temp_after_c": gpu_after["temp_c"],
                "vram_used_gb": gpu_after["vram_used_gb"],
                "errors": [r["error"] for r in failed],
            }
            results.append(entry)
            
            print(f"    Wall: {entry['wall_time_s']}s | OK: {entry['successful']}/{n} | "
                  f"TTFT avg: {entry['ttft_avg_s']}s | Tok/s avg: {entry['tok_s_avg']} | "
                  f"Aggregate: {entry['aggregate_tok_s']} tok/s | "
                  f"Temp: {gpu_before['temp_c']}→{gpu_after['temp_c']}°C")
            if failed:
                print(f"    ⚠️ {len(failed)} FAILED: {entry['errors']}")
            
            time.sleep(3)  # Cool down between levels
        
        # Unload
        try:
            req = urllib.request.Request(
                f"{OLLAMA_HOST}/api/generate",
                data=json.dumps({"model": model, "keep_alive": 0}).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            urllib.request.urlopen(req, timeout=10)
        except:
            pass
        time.sleep(2)
    
    return results

# ============================================================
# Test 4: Sustained Load / Thermal (60 min)
# ============================================================

def test_sustained_load(duration_min=5):
    """Run sustained generation for specified minutes, logging thermal/throughput."""
    print(f"\n{'='*60}")
    print(f"TEST 4: SUSTAINED LOAD / THERMAL ({duration_min} min)")
    print("="*60)
    
    model = "gpt-oss:20b"
    prompts_cycle = [
        "Write a 500-word essay about the future of artificial intelligence.",
        "Explain the concept of quantum superposition with an analogy.",
        "Write a Python function that implements merge sort. Include comments.",
        "Describe the process of photosynthesis in detail.",
        "Write a short story about a robot discovering emotions.",
        "Compare and contrast TCP and UDP protocols. Cover reliability, ordering, and use cases.",
        "Explain how blockchain technology works, step by step.",
        "Write a technical analysis of memory management in operating systems.",
        "Describe the water cycle and its importance to life on Earth.",
        "Write a poem about the beauty of mathematics.",
    ]
    
    results = []
    start_time = time.time()
    end_time = start_time + (duration_min * 60)
    iteration = 0
    
    print(f"\nModel: {model}")
    print(f"Duration: {duration_min} minutes")
    print(f"{'Iter':>4} {'Time':>6} {'TTFT':>7} {'Tok/s':>7} {'Tokens':>7} {'Temp':>6} {'VRAM':>6} {'Busy':>5}")
    print("-" * 65)
    
    while time.time() < end_time:
        prompt = prompts_cycle[iteration % len(prompts_cycle)]
        gpu_before = snapshot_gpu()
        iter_start = time.time()
        
        result = ollama_generate(
            model, prompt,
            options={"num_predict": 2048, "temperature": 0.3},
            stream=True,
        )
        
        iter_time = time.time() - iter_start
        gpu_after = snapshot_gpu()
        elapsed = time.time() - start_time
        
        entry = {
            "iteration": iteration,
            "elapsed_s": round(elapsed, 1),
            "iter_time_s": round(iter_time, 2),
            "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
            "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
            "eval_count": result.get("eval_count", 0),
            "thinking_len": result.get("thinking_len", 0),
            "response_len": result.get("response_len", 0),
            "temp_c": gpu_after["temp_c"],
            "vram_used_gb": gpu_after["vram_used_gb"],
            "gpu_busy_pct": gpu_after["gpu_busy_pct"],
            "ram_available_gb": gpu_after["ram"].get("available_gb", 0),
            "error": result.get("error"),
        }
        results.append(entry)
        
        print(f"{iteration:>4} {elapsed:>6.0f}s {entry['ttft_s'] or 'N/A':>7} "
              f"{entry['tokens_per_s']:>7.1f} {entry['eval_count']:>7} "
              f"{entry['temp_c']:>5.1f}C {entry['vram_used_gb']:>5.1f}G "
              f"{entry['gpu_busy_pct']:>4}%")
        
        if result.get("error"):
            print(f"      ⚠️ ERROR: {result['error']}")
        
        iteration += 1
        # Small gap between requests
        time.sleep(1)
    
    # Summary
    successful = [r for r in results if not r.get("error")]
    total_tokens = sum(r["eval_count"] for r in successful)
    
    summary = {
        "model": model,
        "duration_min": duration_min,
        "total_iterations": len(results),
        "successful": len(successful),
        "failed": len(results) - len(successful),
        "total_tokens": total_tokens,
        "avg_tokens_per_s": round(sum(r["tokens_per_s"] for r in successful) / len(successful), 2) if successful else 0,
        "avg_ttft_s": round(sum(r["ttft_s"] for r in successful if r["ttft_s"]) / max(1, len([r for r in successful if r["ttft_s"]])), 4),
        "temp_start_c": successful[0]["temp_c"] if successful else 0,
        "temp_end_c": successful[-1]["temp_c"] if successful else 0,
        "temp_delta_c": round((successful[-1]["temp_c"] - successful[0]["temp_c"]), 1) if successful else 0,
        "throughput_first_5_avg": round(sum(r["tokens_per_s"] for r in successful[:5]) / max(1, min(5, len(successful))), 2),
        "throughput_last_5_avg": round(sum(r["tokens_per_s"] for r in successful[-5:]) / max(1, min(5, len(successful))), 2),
    }
    
    print(f"\n--- Sustained Load Summary ---")
    print(f"  Iterations: {summary['total_iterations']} ({summary['successful']} OK, {summary['failed']} failed)")
    print(f"  Total tokens: {summary['total_tokens']}")
    print(f"  Avg tok/s: {summary['avg_tokens_per_s']}")
    print(f"  Avg TTFT: {summary['avg_ttft_s']}s")
    print(f"  Temp: {summary['temp_start_c']}°C → {summary['temp_end_c']}°C (Δ{summary['temp_delta_c']}°C)")
    print(f"  Throughput drift: {summary['throughput_first_5_avg']} → {summary['throughput_last_5_avg']} tok/s")
    
    return {"summary": summary, "iterations": results}

# ============================================================
# Test 5: Real Agent Workloads
# ============================================================

def test_agent_workloads():
    print("\n" + "="*60)
    print("TEST 5: REAL AGENT WORKLOADS")
    print("="*60)
    
    results = []
    
    # Use gpt-oss:20b for agent tests (best local model for instruction following)
    model = "gpt-oss:20b"
    
    # 5a: Multi-turn conversation
    print(f"\n--- 5a: Multi-turn Conversation ({model}) ---")
    messages = []
    for i, prompt in enumerate(MULTI_TURN_PROMPTS):
        messages.append({"role": "user", "content": prompt})
        gpu_before = snapshot_gpu()
        start = time.time()
        
        result = ollama_chat(
            model, messages,
            options={"num_predict": 2048, "temperature": 0.3},
            stream=True,
        )
        
        total_time = time.time() - start
        gpu_after = snapshot_gpu()
        
        assistant_reply = result.get("response", "")
        thinking_text = result.get("thinking", "")
        messages.append({"role": "assistant", "content": assistant_reply})
        
        entry = {
            "test": "multi_turn",
            "model": model,
            "turn": i + 1,
            "context_messages": len(messages),
            "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
            "ttft_content_s": round(result.get("ttft_content_s", 0), 4) if result.get("ttft_content_s") else None,
            "thinking_len": result.get("thinking_len", 0),
            "total_time_s": round(total_time, 2),
            "eval_count": result.get("eval_count", 0),
            "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
            "response_len": result.get("response_len", 0),
            "temp_after_c": gpu_after["temp_c"],
            "vram_used_gb": gpu_after["vram_used_gb"],
            "response_preview": assistant_reply[:200],
            "error": result.get("error"),
        }
        results.append(entry)
        
        print(f"  Turn {i+1}: TTFT={entry['ttft_s']}s | {entry['total_time_s']}s | "
              f"{entry['tokens_per_s']} tok/s | {entry['eval_count']} tok | "
              f"{gpu_after['temp_c']}°C")
        if result.get("error"):
            print(f"  ⚠️ ERROR: {result['error']}")
    
    # 5b: Tool calling (structured output)
    print(f"\n--- 5b: Tool Calling / Structured Output ({model}) ---")
    gpu_before = snapshot_gpu()
    start = time.time()
    
    result = ollama_generate(
        model, TOOL_CALL_PROMPT,
        options={"num_predict": 2048, "temperature": 0.1},
        stream=True,
    )
    
    total_time = time.time() - start
    gpu_after = snapshot_gpu()
    
    response_text = result.get("response", "")
    
    # Check if response contains JSON-like tool calls
    has_json = bool(re.search(r'\{.*"tool_calls".*\}', response_text, re.DOTALL)) or \
               bool(re.search(r'\{.*"name".*:.*"arguments".*\}', response_text, re.DOTALL))
    has_tool_names = any(tn in response_text for tn in ["get_weather", "search_web", "calculate"])
    
    entry = {
        "test": "tool_calling",
        "model": model,
        "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
        "total_time_s": round(total_time, 2),
        "eval_count": result.get("eval_count", 0),
        "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
        "response_len": result.get("response_len", 0),
        "has_structured_json": has_json,
        "has_tool_names": has_tool_names,
        "response_preview": response_text[:300],
        "temp_after_c": gpu_after["temp_c"],
        "error": result.get("error"),
    }
    results.append(entry)
    
    print(f"  TTFT={entry['ttft_s']}s | {entry['total_time_s']}s | {entry['tokens_per_s']} tok/s")
    print(f"  Structured JSON: {has_json} | Tool names present: {has_tool_names}")
    print(f"  Response preview: {response_text[:200]}")
    if result.get("error"):
        print(f"  ⚠️ ERROR: {result['error']}")
    
    # 5c: Code generation
    print(f"\n--- 5c: Code Generation ({model}) ---")
    gpu_before = snapshot_gpu()
    start = time.time()
    
    result = ollama_generate(
        model, CODE_GEN_PROMPT,
        options={"num_predict": 4096, "temperature": 0.2},
        stream=True,
    )
    
    total_time = time.time() - start
    gpu_after = snapshot_gpu()
    
    code_response = result.get("response", "")
    
    # Basic code quality checks
    has_classes = "class " in code_response
    has_methods = "def " in code_response
    has_type_hints = any(t in code_response for t in ["->", ": int", ": str", ": bool", ": Optional", ": List"])
    has_docstrings = '"""' in code_response or "'''" in code_response
    code_blocks = code_response.count("```")
    
    entry = {
        "test": "code_gen",
        "model": model,
        "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
        "total_time_s": round(total_time, 2),
        "eval_count": result.get("eval_count", 0),
        "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
        "response_len": result.get("response_len", 0),
        "has_classes": has_classes,
        "has_methods": has_methods,
        "has_type_hints": has_type_hints,
        "has_docstrings": has_docstrings,
        "code_blocks": code_blocks,
        "response_preview": code_response[:300],
        "temp_after_c": gpu_after["temp_c"],
        "error": result.get("error"),
    }
    results.append(entry)
    
    print(f"  TTFT={entry['ttft_s']}s | {entry['total_time_s']}s | {entry['tokens_per_s']} tok/s | {entry['eval_count']} tok")
    print(f"  Classes: {has_classes} | Methods: {has_methods} | Type hints: {has_type_hints} | Docstrings: {has_docstrings}")
    if result.get("error"):
        print(f"  ⚠️ ERROR: {result['error']}")
    
    # 5d: Long context test (pad a large context)
    print(f"\n--- 5d: Long Context Test ({model}) ---")
    # Build a ~8K token context by repeating context text
    context_text = "The quick brown fox jumps over the lazy dog. " * 200  # ~1600 tokens
    long_context_prompt = f"Context:\n{context_text}\n\nQuestion: How many times does the word 'fox' appear in the context above? Answer with just the number."
    
    gpu_before = snapshot_gpu()
    start = time.time()
    
    result = ollama_generate(
        model, long_context_prompt,
        options={"num_predict": 100, "temperature": 0.1},
        stream=True,
    )
    
    total_time = time.time() - start
    gpu_after = snapshot_gpu()
    
    entry = {
        "test": "long_context",
        "model": model,
        "prompt_eval_count": result.get("prompt_eval_count", 0),
        "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
        "total_time_s": round(total_time, 2),
        "eval_count": result.get("eval_count", 0),
        "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
        "prompt_tokens_per_s": round(result.get("prompt_tokens_per_s", 0), 2),
        "response_preview": result.get("response", "")[:200],
        "temp_after_c": gpu_after["temp_c"],
        "vram_used_gb": gpu_after["vram_used_gb"],
        "error": result.get("error"),
    }
    results.append(entry)
    
    print(f"  Prompt tokens: {entry['prompt_eval_count']} | TTFT={entry['ttft_s']}s | "
          f"{entry['total_time_s']}s | {entry['tokens_per_s']} tok/s")
    print(f"  Prompt eval speed: {entry['prompt_tokens_per_s']} tok/s")
    print(f"  Response: {result.get('response', '')[:100]}")
    if result.get("error"):
        print(f"  ⚠️ ERROR: {result['error']}")
    
    # Unload
    try:
        req = urllib.request.Request(
            f"{OLLAMA_HOST}/api/generate",
            data=json.dumps({"model": model, "keep_alive": 0}).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except:
        pass
    
    return results

# ============================================================
# Cloud Comparison (local vs cloud, same model family)
# ============================================================

def test_cloud_comparison():
    print("\n" + "="*60)
    print("BONUS: LOCAL vs CLOUD COMPARISON")
    print("="*60)
    
    prompt = "Write a short Python function that checks if a string is a palindrome. Include docstring and type hints."
    results = []
    
    # Local model
    print(f"\n--- Local: gpt-oss:20b ---")
    gpu_before = snapshot_gpu()
    start = time.time()
    
    result = ollama_generate(
        "gpt-oss:20b", prompt,
        options={"num_predict": 2048, "temperature": 0.2},
        stream=True,
    )
    
    total_time = time.time() - start
    gpu_after = snapshot_gpu()
    
    entry = {
        "model": "gpt-oss:20b (local)",
        "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
        "total_time_s": round(total_time, 2),
        "eval_count": result.get("eval_count", 0),
        "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
        "response_len": result.get("response_len", 0),
        "temp_c": gpu_after["temp_c"],
        "error": result.get("error"),
    }
    results.append(entry)
    print(f"  TTFT={entry['ttft_s']}s | {entry['total_time_s']}s | {entry['tokens_per_s']} tok/s")
    
    # Cloud models
    for cloud_model in CLOUD_MODELS:
        print(f"\n--- Cloud: {cloud_model} ---")
        start = time.time()
        
        result = ollama_generate(
            cloud_model, prompt,
            options={"num_predict": 2048, "temperature": 0.2},
            stream=True,
        )
        
        total_time = time.time() - start
        
        entry = {
            "model": cloud_model,
            "ttft_s": round(result.get("ttft_s", 0), 4) if result.get("ttft_s") else None,
            "total_time_s": round(total_time, 2),
            "eval_count": result.get("eval_count", 0),
            "tokens_per_s": round(result.get("tokens_per_s", 0), 2),
            "response_len": result.get("response_len", 0),
            "error": result.get("error"),
        }
        results.append(entry)
        print(f"  TTFT={entry['ttft_s']}s | {entry['total_time_s']}s | {entry['tokens_per_s']} tok/s")
        if result.get("error"):
            print(f"  ⚠️ ERROR: {result['error']}")
    
    return results

# ============================================================
# System Info Collector
# ============================================================

def collect_system_info():
    print("\n" + "="*60)
    print("SYSTEM INFORMATION")
    print("="*60)
    
    info = {
        "timestamp": datetime.now().isoformat(),
        "kernel": os.uname().release,
        "cpu": cpu_info(),
        "ram": system_ram(),
        "gpu": {
            "name": "AMD Radeon 8060S (gfx1151)",
            "vram_total_gb": round(gpu_vram_total(), 2),
            "vram_used_gb": round(gpu_vram_used(), 2),
            "vram_free_gb": round(gpu_vram_total() - gpu_vram_used(), 2),
            "gtt_total_gb": round(gpu_gtt_total(), 2),
            "gtt_used_gb": round(gpu_gtt_used(), 2),
            "temp_c": gpu_temp(),
            "busy_pct": gpu_busy(),
        },
        "rocm": "7.2.4",
        "runtime": "Ollama",
    }
    
    print(f"  CPU: {info['cpu']['model']}")
    print(f"  Cores: {info['cpu']['cores']} cores / {info['cpu']['threads']} threads")
    print(f"  RAM: {info['ram']['total_gb']:.1f} GB total, {info['ram']['available_gb']:.1f} GB available")
    print(f"  GPU: {info['gpu']['name']}")
    print(f"  VRAM: {info['gpu']['vram_used_gb']:.1f} / {info['gpu']['vram_total_gb']:.1f} GB used")
    print(f"  GTT: {info['gpu']['gtt_used_gb']:.1f} / {info['gpu']['gtt_total_gb']:.1f} GB used")
    print(f"  Temp: {info['gpu']['temp_c']:.1f}°C")
    print(f"  Kernel: {info['kernel']}")
    print(f"  ROCm: {info['rocm']}")
    print(f"  Runtime: {info['runtime']}")
    
    return info

# ============================================================
# Main
# ============================================================

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    print("="*60)
    print("  STRIX HALO LLM INFERENCE BENCHMARK")
    print("  AMD Ryzen AI MAX+ 395 / Radeon 8060S (gfx1151)")
    print("  ROCm 7.2.4 / Ollama / Kernel 7.1.4")
    print("="*60)
    
    all_results = {}
    
    # System info
    all_results["system_info"] = collect_system_info()
    
    # Test 1: Capacity Map
    all_results["capacity_map"] = test_capacity_map()
    
    # Test 2: Single-Request Performance
    all_results["single_request"] = test_single_request_performance()
    
    # Test 3: Concurrency
    all_results["concurrency"] = test_concurrency()
    
    # Test 4: Sustained Load (5 min for initial run — extend for full blog)
    all_results["sustained_load"] = test_sustained_load(duration_min=5)
    
    # Test 5: Agent Workloads
    all_results["agent_workloads"] = test_agent_workloads()
    
    # Bonus: Cloud comparison
    all_results["cloud_comparison"] = test_cloud_comparison()
    
    # Final system state
    all_results["final_state"] = snapshot_gpu()
    
    # Save results
    results_file = os.path.join(RESULTS_DIR, f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n\n{'='*60}")
    print(f"BENCHMARK COMPLETE")
    print(f"Results saved to: {results_file}")
    print(f"{'='*60}")
    
    # Print summary table
    print(f"\n=== SUMMARY ===")
    print(f"\nCapacity Map:")
    for m in all_results["capacity_map"]:
        status = "✅" if not m.get("error") else "❌"
        print(f"  {status} {m['model']}: {m['size_gb']}GB, load {m['load_time_s']}s, "
              f"VRAM +{m['vram_delta_gb']}GB, {m.get('tokens_per_s', 0)} tok/s")
    
    print(f"\nSingle-Request Performance (gpt-oss:20b):")
    for r in all_results["single_request"]:
        if r["model"] == "gpt-oss:20b":
            print(f"  {r['prompt_label']}: TTFT={r['ttft_s']}s, {r['tokens_per_s']} tok/s, "
                  f"{r['eval_count']} tok output")
    
    print(f"\nConcurrency (gpt-oss:20b):")
    for r in all_results["concurrency"]:
        if r["model"] == "gpt-oss:20b":
            print(f"  N={r['concurrency']}: wall={r['wall_time_s']}s, "
                  f"agg={r['aggregate_tok_s']} tok/s, "
                  f"{r['successful']}/{r['concurrency']} OK")
    
    if "sustained_load" in all_results:
        sl = all_results["sustained_load"]["summary"]
        print(f"\nSustained Load ({sl['duration_min']} min):")
        print(f"  {sl['total_iterations']} iterations, {sl['total_tokens']} tokens")
        print(f"  Avg {sl['avg_tokens_per_s']} tok/s, TTFT {sl['avg_ttft_s']}s")
        print(f"  Temp: {sl['temp_start_c']}°C → {sl['temp_end_c']}°C (Δ{sl['temp_delta_c']}°C)")
        print(f"  Throughput drift: {sl['throughput_first_5_avg']} → {sl['throughput_last_5_avg']} tok/s")
    
    print(f"\nAgent Workloads:")
    for r in all_results["agent_workloads"]:
        test_name = r.get("test", "unknown")
        status = "✅" if not r.get("error") else "❌"
        print(f"  {status} {test_name}: TTFT={r.get('ttft_s')}s, {r.get('tokens_per_s', 0)} tok/s")
    
    print(f"\nCloud Comparison:")
    for r in all_results["cloud_comparison"]:
        print(f"  {r['model']}: TTFT={r.get('ttft_s')}s, {r.get('tokens_per_s', 0)} tok/s")
    
    return results_file

if __name__ == "__main__":
    main()