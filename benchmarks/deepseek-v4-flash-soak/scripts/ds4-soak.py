#!/usr/bin/env python3
"""DS4 soak test — sustained load on the DeepSeek V4 Flash endpoint.
Hits the server with mixed requests every ~30s and logs results.
Run for hours. Check for memory leaks, crashes, degradation."""
import json, time, sys, os, httpx, datetime

BASE_URL = "http://spark-56bc:8888/v1"
MODEL = "deepseek-v4-flash"
LOG_FILE = "/home/mikesai1/workspace/ds4-soak.log"
JSON_LOG = "/home/mikesai1/workspace/ds4-soak-results.json"

PROMPTS = [
    ("reasoning", "If a train travels 80 km in 40 minutes, what is its speed in km/h?", 500, 0.3),
    ("coding", "Write a Python one-liner to flatten a nested list.", 800, 0.5),
    ("math", "What is 23 * 47? Show your work.", 500, 0.3),
    ("knowledge", "What is the capital of Brazil?", 300, 0.3),
    ("instruction", "List 5 programming languages. One per line.", 300, 0.3),
    ("tool", "What's the weather in London? Use the tool.", 1000, 0.1),
    ("creative", "Write a 3-sentence sci-fi story about a robot.", 500, 0.7),
    ("logic", "All birds can fly. Penguins are birds. Can penguins fly?", 800, 0.3),
]

TOOLS = [
    {"type": "function", "function": {"name": "get_weather", "description": "Get weather",
     "parameters": {"type": "object", "properties": {"location": {"type": "string"}}, "required": ["location"]}}}
]

results = []
iteration = 0

with open(LOG_FILE, "a") as log:
    log.write(f"\n{'='*60}\nSoak test started: {datetime.datetime.now()}\n{'='*60}\n")

while True:
    iteration += 1
    ts = datetime.datetime.now().isoformat()
    label, prompt, max_tok, temp = PROMPTS[(iteration - 1) % len(PROMPTS)]
    
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
               "max_tokens": max_tok, "temperature": temp}
    if label == "tool":
        payload["tools"] = TOOLS
        payload["tool_choice"] = "auto"
    
    start = time.perf_counter()
    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(f"{BASE_URL}/chat/completions", json=payload)
            elapsed = time.perf_counter() - start
            data = resp.json()
            
            choice = data.get("choices", [{}])[0]
            usage = data.get("usage", {})
            timings = data.get("timings", {})
            finish = choice.get("finish_reason", "?")
            ct = usage.get("completion_tokens", 0)
            tps = ct / elapsed if elapsed > 0 else 0
            ttft = timings.get("ttft_ms", 0)
            spec = timings.get("spec_accept_rate", 0)
            
            entry = {"iter": iteration, "ts": ts, "label": label, "elapsed_s": round(elapsed, 2),
                     "completion_tokens": ct, "tok_s": round(tps, 1), "ttft_ms": ttft,
                     "spec_accept": spec, "finish": finish, "status": "ok"}
            
            with open(LOG_FILE, "a") as log:
                log.write(f"[{ts}] iter={iteration} {label}: {ct}tok {elapsed:.1f}s {tps:.1f}tok/s ttft={ttft}ms spec={spec} finish={finish}\n")
            
            if iteration % 10 == 0:
                with open(LOG_FILE, "a") as log:
                    log.write(f"  --- {iteration} iterations completed ---\n")
    except Exception as e:
        elapsed = time.perf_counter() - start
        entry = {"iter": iteration, "ts": ts, "label": label, "elapsed_s": round(elapsed, 2),
                 "status": "error", "error": str(e)[:200]}
        with open(LOG_FILE, "a") as log:
            log.write(f"[{ts}] iter={iteration} {label}: ERROR {str(e)[:100]}\n")
    
    results.append(entry)
    if iteration % 20 == 0:
        with open(JSON_LOG, "w") as f:
            json.dump(results, f, indent=2, default=str)
    
    # Sleep ~30s between requests (with some jitter)
    sleep_time = 25 + (iteration % 10)
    time.sleep(sleep_time)
