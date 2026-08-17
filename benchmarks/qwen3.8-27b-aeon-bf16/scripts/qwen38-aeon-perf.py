#!/usr/bin/env python3
"""Performance benchmark for Qwen3.8-27B-AEON-UNCENSORED-BF16 on SGLang (DGX Spark).

Covers: latency/throughput, TTFT (streaming), concurrency ladder,
context scaling, and spec-decode acceptance (via SGLang /metrics).
Thinking disabled per-request via chat_template_kwargs.
"""
import asyncio, json, time, statistics, httpx

BASE_URL = "http://spark-56bc:30000/v1"
MODEL = "Qwen3.8-27B-AEON-UNCENSORED-BF16"
TIMEOUT = httpx.Timeout(600.0, connect=10.0)
KW = {"enable_thinking": False}

async def chat(client, messages, max_tokens=1024, temperature=0.6, stream=False):
    payload = {"model": MODEL, "messages": messages, "max_tokens": max_tokens,
               "temperature": temperature, "chat_template_kwargs": KW}
    start = time.perf_counter()
    if stream:
        ttft = None; content = ""
        async with client.stream("POST", f"{BASE_URL}/chat/completions",
                                  json={**payload, "stream": True}, timeout=TIMEOUT) as r:
            async for line in r.aiter_lines():
                if line.startswith("data: ") and line != "data: [DONE]":
                    try: chunk = json.loads(line[6:])
                    except: continue
                    d = chunk.get("choices", [{}])[0].get("delta", {})
                    c = d.get("content", "")
                    if c and ttft is None: ttft = time.perf_counter()
                    content += c
        return content, time.perf_counter() - start, (ttft - start) if ttft else None
    else:
        r = await client.post(f"{BASE_URL}/chat/completions", json=payload, timeout=TIMEOUT)
        return r.json(), time.perf_counter() - start, None

async def latency_throughput(client):
    out = []
    prompt = "Write a detailed essay about the history of computing, from Babbage to modern AI."
    for mt in [64, 128, 256, 512, 1024]:
        data, el, _ = await chat(client, [{"role":"user","content":prompt}], max_tokens=mt, temperature=0.7)
        ct = data.get("usage", {}).get("completion_tokens", 0)
        out.append({"max_tokens": mt, "completion_tokens": ct, "wall_s": round(el,3),
                    "tok_s": round(ct/el,2) if el else 0})
        print(f"  [lat] mt={mt}: {ct} tok in {el:.2f}s = {ct/el:.1f} tok/s" if el else f"  [lat] mt={mt}: empty")
    return out

async def ttft(client):
    out = []
    for label, p in [("short","What is 2+2?"), ("medium","Explain how a CPU works in 3 paragraphs."),
                     ("reasoning","Prove that the square root of 2 is irrational.")]:
        content, el, t = await chat(client, [{"role":"user","content":p}], max_tokens=2000, stream=True)
        out.append({"label": label, "ttft_ms": round(t*1000,1) if t else None, "total_s": round(el,3)})
        print(f"  [ttft] {label}: TTFT={t*1000:.0f}ms total={el:.2f}s" if t else f"  [ttft] {label}: N/A")
    return out

async def concurrency(client):
    out = []
    prompt = "Write a short story about a robot learning to paint."
    for n in [1, 2, 4, 8, 16]:
        async def one():
            return await chat(client, [{"role":"user","content":prompt}], max_tokens=512, stream=True)
        s = time.perf_counter()
        rs = await asyncio.gather(*[one() for _ in range(n)], return_exceptions=True)
        wall = time.perf_counter() - s
        ok = [r for r in rs if not isinstance(r, Exception)]
        out.append({"concurrency": n, "ok": len(ok), "failed": n-len(ok), "wall_s": round(wall,3)})
        print(f"  [conc] n={n}: {len(ok)}/{n} ok, wall={wall:.2f}s")
    return out

async def context_scaling(client):
    out = []
    filler = "The quick brown fox jumps over the lazy dog. " * 10
    for target in [100, 500, 2000, 8000, 32000, 128000]:
        text = filler * (target // 100)
        prompt = f"Read the following text. At the end, answer: what is 7 multiplied by 8?\n\nText:\n{text}\n\nQuestion: What is 7 multiplied by 8?"
        data, el, _ = await chat(client, [{"role":"user","content":prompt}], max_tokens=200)
        u = data.get("usage", {})
        ct = u.get("completion_tokens", 0)
        out.append({"target": target, "prompt_tokens": u.get("prompt_tokens",0), "completion_tokens": ct,
                    "wall_s": round(el,3), "tok_s": round(ct/el,2) if el and ct else 0})
        print(f"  [ctx] ~{target}: {ct} out in {el:.2f}s")
    return out

async def spec_metrics(client):
    try:
        r = await client.get(BASE_URL.replace("/v1","") + "/metrics", timeout=10)
        if r.status_code != 200:
            return {"status": r.status_code}
        acc = draft = None
        for line in r.text.split("\n"):
            if line.startswith("sglang:") and "spec" in line.lower():
                pass
            # SGLang exposes spec decode via these metric names (best-effort)
            if "spec_decode_num_accepted" in line and not line.startswith("#"):
                acc = line.split()[-1]
            if "spec_decode_num_draft" in line and not line.startswith("#"):
                draft = line.split()[-1]
        return {"accepted": acc, "draft": draft}
    except Exception as e:
        return {"error": str(e)[:200]}

async def main():
    print("="*70)
    print(f"Qwen3.8-27B-AEON-UNCENSORED-BF16 perf | {BASE_URL} | {MODEL}")
    print("="*70)
    report = {"model": MODEL, "endpoint": BASE_URL, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "serve_recipe_id": "SMF-Spark-SGLang-qwen38-27b-aeon-bf16-eagle", "tests": {}}
    async with httpx.AsyncClient() as client:
        print("\n-- Latency/Throughput --")
        report["tests"]["latency_throughput"] = await latency_throughput(client)
        print("\n-- TTFT --")
        report["tests"]["ttft"] = await ttft(client)
        print("\n-- Concurrency --")
        report["tests"]["concurrency"] = await concurrency(client)
        print("\n-- Context Scaling --")
        report["tests"]["context_scaling"] = await context_scaling(client)
        print("\n-- Spec Decode Metrics --")
        report["tests"]["spec_metrics"] = await spec_metrics(client)
    print("\n__JSON_REPORT_START__")
    print(json.dumps(report, indent=2))
    print("__JSON_REPORT_END__")

if __name__ == "__main__":
    asyncio.run(main())
