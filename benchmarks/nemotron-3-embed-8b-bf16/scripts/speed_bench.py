#!/usr/bin/env python3
"""Speed / throughput bench for Nemotron-3-Embed-8B on Spark."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import DEFAULT_BASE, DEFAULT_MODEL, RECIPE_ID, SparkEmbedClient, wait_ready  # noqa: E402

# Synthetic corpus: short / medium / long-ish passages for RAG-like mix
SHORT = "Praxis RAG retrieves Spark serve recipes for Nemotron embeddings."
MED = (
    "Nemotron-3-Embed-8B-BF16 maps multilingual text to 4096-d vectors with query: and passage: "
    "prefixes. Use /v2/embed for retrieval and L2-normalized cosine similarity for ranking."
) * 3
LONG = (MED + " ") * 8  # ~ multi-sentence chunk


def make_texts(n: int, kind: str) -> list[str]:
    base = {"short": SHORT, "medium": MED, "long": LONG}[kind]
    return [f"{base} id={i}" for i in range(n)]


def bench_batch(
    client: SparkEmbedClient,
    texts: list[str],
    *,
    kind: str,
    repeats: int,
) -> dict:
    latencies = []
    # warmup
    if kind == "query":
        client.embed_queries(texts[: min(4, len(texts))])
    else:
        client.embed_documents(texts[: min(4, len(texts))])

    for _ in range(repeats):
        t0 = time.perf_counter()
        if kind == "query":
            embs = client.embed_queries(texts)
        else:
            embs = client.embed_documents(texts)
        dt = time.perf_counter() - t0
        latencies.append(dt)
        dim = embs.shape[1]
    latencies.sort()
    n = len(texts)
    mean = statistics.mean(latencies)
    return {
        "n_texts": n,
        "kind": kind,
        "dim": dim,
        "repeats": repeats,
        "latency_s_mean": mean,
        "latency_s_p50": latencies[len(latencies) // 2],
        "latency_s_p95": latencies[max(0, int(len(latencies) * 0.95) - 1)],
        "latency_s_min": latencies[0],
        "latency_s_max": latencies[-1],
        "texts_per_s": n / mean if mean > 0 else 0.0,
        "ms_per_text": (mean / n) * 1000 if n else 0.0,
    }


def bench_concurrency(
    client: SparkEmbedClient,
    *,
    workers: int,
    texts_per_req: int,
    requests_n: int,
    kind: str = "document",
) -> dict:
    texts = make_texts(texts_per_req, "medium")

    def one(_i: int) -> float:
        t0 = time.perf_counter()
        if kind == "query":
            client.embed_queries(texts)
        else:
            client.embed_documents(texts)
        return time.perf_counter() - t0

    # warmup
    one(-1)
    t_wall0 = time.perf_counter()
    latencies = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = [ex.submit(one, i) for i in range(requests_n)]
        for f in as_completed(futs):
            latencies.append(f.result())
    wall = time.perf_counter() - t_wall0
    total_texts = requests_n * texts_per_req
    return {
        "workers": workers,
        "texts_per_req": texts_per_req,
        "requests": requests_n,
        "wall_s": wall,
        "latency_s_mean": statistics.mean(latencies),
        "latency_s_p50": sorted(latencies)[len(latencies) // 2],
        "req_per_s": requests_n / wall if wall else 0.0,
        "texts_per_s": total_texts / wall if wall else 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Nemotron-3-Embed speed bench")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", default="", help="JSON output path")
    ap.add_argument("--repeats", type=int, default=5)
    ap.add_argument("--no-v2", action="store_true", help="force /v1 with prefixes")
    ap.add_argument("--quick", action="store_true", help="smaller matrix")
    args = ap.parse_args()

    wait_ready(args.base)
    client = SparkEmbedClient(base_url=args.base, model=args.model, use_v2=not args.no_v2)

    batch_sizes = [1, 4, 8, 16, 32] if not args.quick else [1, 8, 16]
    lengths = ["short", "medium"] if args.quick else ["short", "medium", "long"]
    workers_list = [1, 2, 4] if not args.quick else [1, 4]

    results: dict = {
        "serve_recipe_id": RECIPE_ID,
        "model": args.model,
        "base": args.base,
        "use_v2": not args.no_v2,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "batch_matrix": [],
        "concurrency": [],
    }

    print("=== Batch size × length matrix (document embeddings) ===")
    for length in lengths:
        for bs in batch_sizes:
            texts = make_texts(bs, length)
            row = bench_batch(client, texts, kind="document", repeats=args.repeats)
            row["length"] = length
            row["batch_size"] = bs
            results["batch_matrix"].append(row)
            print(
                f"  len={length:6} bs={bs:3}  mean={row['latency_s_mean']:.3f}s  "
                f"p50={row['latency_s_p50']:.3f}s  tps={row['texts_per_s']:.1f}  "
                f"ms/text={row['ms_per_text']:.1f}"
            )

    print("=== Query single-shot latency ===")
    qrow = bench_batch(client, make_texts(1, "short"), kind="query", repeats=max(args.repeats, 10))
    results["query_single"] = qrow
    print(f"  single query mean={qrow['latency_s_mean']*1000:.1f} ms")

    print("=== Concurrency (document, medium, 8 texts/req) ===")
    for w in workers_list:
        crow = bench_concurrency(
            client,
            workers=w,
            texts_per_req=8,
            requests_n=12 if not args.quick else 8,
            kind="document",
        )
        results["concurrency"].append(crow)
        print(
            f"  workers={w}  wall={crow['wall_s']:.2f}s  "
            f"req/s={crow['req_per_s']:.2f}  texts/s={crow['texts_per_s']:.1f}  "
            f"lat_mean={crow['latency_s_mean']:.3f}s"
        )

    out = args.out or str(
        Path(__file__).resolve().parents[1]
        / "results"
        / f"speed_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(json.dumps(results, indent=2))
    print(f"\nWrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
