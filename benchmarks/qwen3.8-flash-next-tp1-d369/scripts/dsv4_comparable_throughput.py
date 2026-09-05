#!/usr/bin/env python3
"""DSV4-comparable throughput cells against any OpenAI-compatible /v1.

Cells (thinking off analogue):
  256 x c=1   single-stream decode
  256 x c=6   aggregate at seq ceiling
  8k  x c=1   daytime prefill / TTFT

Matches dsv4-dual-spark-serve throughput pin methodology:
  thinking off, cache-bust, count completion_tokens via stream_options.include_usage.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx


def filler_tokens(n: int) -> str:
    # ~1 token per "word" for ASCII filler; 8k cell uses this as prompt body.
    return " ".join(f"w{i:05d}" for i in range(n))


def one_stream(client: httpx.Client, url: str, model: str, prompt: str, max_tokens: int, thinking_off: bool) -> dict:
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if thinking_off:
        body["chat_template_kwargs"] = {"enable_thinking": False, "reasoning_effort": "low"}
        body["thinking"] = False
    t0 = time.perf_counter()
    ttft = None
    content = []
    usage = {}
    finish = None
    with client.stream("POST", url, json=body, timeout=httpx.Timeout(600.0)) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if not line or not line.startswith("data: "):
                continue
            payload = line[6:]
            if payload.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if chunk.get("usage"):
                usage = chunk["usage"]
            choices = chunk.get("choices") or []
            if not choices:
                continue
            delta = choices[0].get("delta") or {}
            piece = delta.get("content") or delta.get("reasoning_content") or delta.get("reasoning") or ""
            if piece and ttft is None:
                ttft = time.perf_counter() - t0
            if delta.get("content"):
                content.append(delta["content"])
            if choices[0].get("finish_reason"):
                finish = choices[0]["finish_reason"]
    wall = time.perf_counter() - t0
    completion = usage.get("completion_tokens") or 0
    prompt_n = usage.get("prompt_tokens") or 0
    decode_s = wall - (ttft or 0)
    return {
        "ttft_s": ttft,
        "wall_s": wall,
        "prompt_tokens": prompt_n,
        "completion_tokens": completion,
        "decode_tok_s": (completion / decode_s) if completion and decode_s > 0 else None,
        "prefill_tok_s": (prompt_n / ttft) if prompt_n and ttft else None,
        "finish": finish,
        "content_len": sum(len(x) for x in content),
    }


def run_cell(client, url, model, name, prompt, max_tokens, concurrency, repeats):
    rows = []
    for r in range(repeats):
        if concurrency == 1:
            rows.append(one_stream(client, url, model, prompt + f"\n[cachebust {time.time()} {r}]", max_tokens, True))
        else:
            with ThreadPoolExecutor(max_workers=concurrency) as ex:
                futs = [
                    ex.submit(
                        one_stream,
                        client,
                        url,
                        model,
                        prompt + f"\n[cachebust {time.time()} {r} {i}]",
                        max_tokens,
                        True,
                    )
                    for i in range(concurrency)
                ]
                batch = [f.result() for f in as_completed(futs)]
            # aggregate decode over wall of slowest in batch
            wall = max(x["wall_s"] for x in batch)
            toks = sum(x["completion_tokens"] for x in batch)
            rows.append(
                {
                    "ttft_s": min((x["ttft_s"] or 9e9) for x in batch),
                    "wall_s": wall,
                    "prompt_tokens": sum(x["prompt_tokens"] for x in batch),
                    "completion_tokens": toks,
                    "decode_tok_s": toks / wall if wall else None,
                    "prefill_tok_s": None,
                    "finish": "batch",
                    "content_len": sum(x["content_len"] for x in batch),
                    "n": concurrency,
                }
            )
    return {"cell": name, "concurrency": concurrency, "repeats": repeats, "runs": rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--endpoint", default="http://spark-d369:8080/v1")
    p.add_argument("--model", default="glm-5.3-flash")
    p.add_argument("--out", default="")
    args = p.parse_args()
    url = args.endpoint.rstrip("/") + "/chat/completions"
    prompt_short = "Write a numbered list of 20 mundane facts about granite. No preamble."
    prompt_8k = (
        "You will be given a long document. After it, reply with exactly OK.\n\n"
        + filler_tokens(7500)
        + "\n\nReply with exactly OK."
    )
    out = {"endpoint": args.endpoint, "model": args.model, "cells": []}
    with httpx.Client() as client:
        print("cell 256 x c=1", flush=True)
        out["cells"].append(run_cell(client, url, args.model, "256xc1", prompt_short, 256, 1, 3))
        print(json.dumps(out["cells"][-1]["runs"][-1], indent=2), flush=True)
        print("cell 256 x c=6", flush=True)
        out["cells"].append(run_cell(client, url, args.model, "256xc6", prompt_short, 256, 6, 1))
        print(json.dumps(out["cells"][-1]["runs"][-1], indent=2), flush=True)
        print("cell 8k x c=1", flush=True)
        out["cells"].append(run_cell(client, url, args.model, "8kxc1", prompt_8k, 16, 1, 2))
        print(json.dumps(out["cells"][-1]["runs"][-1], indent=2), flush=True)
    if args.out:
        with open(args.out, "w") as f:
            json.dump(out, f, indent=2)
        print("wrote", args.out, flush=True)
    else:
        json.dump(out, sys.stdout, indent=2)
        print()


if __name__ == "__main__":
    main()
