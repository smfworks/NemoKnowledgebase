#!/usr/bin/env python3
"""Lightweight Praxis-style RAG accuracy: synthetic multi-doc corpus + nDCG/Recall.

Does not replace MTEB/RTEB; validates end-to-end retrieval behavior for domain-ish
content (Spark serve recipes, agents, inference) without downloading BEIR datasets.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import DEFAULT_BASE, DEFAULT_MODEL, RECIPE_ID, SparkEmbedClient, wait_ready  # noqa: E402

CORPUS = [
    {
        "id": "d1",
        "text": "SMF-Spark-vLLM-0.24-marlin is the frozen serve recipe for unsloth/Qwen3.6-35B-A3B-NVFP4 on spark-56bc port 8888 with marlin MoE backend and MTP.",
    },
    {
        "id": "d2",
        "text": "Nemotron-3-Embed-8B-BF16 serves on port 8889 with vLLM 0.24.0 pooling runner. Prefer /v2/embed with input_type query or document for Praxis RAG.",
    },
    {
        "id": "d3",
        "text": "AgentMail for Nemo is nemosmf@agentmail.to. Daily inbox checks use the shared AgentMail API key and agentmail CLI.",
    },
    {
        "id": "d4",
        "text": "DGX Spark GB10 has 128 GB unified memory. UMA gpu-memory-utilization should stay at or below 0.82 for models larger than 60 GB.",
    },
    {
        "id": "d5",
        "text": "Strunk and White composition rules are wired into the strunk-white-prose skill for status briefs and technical writing.",
    },
    {
        "id": "d6",
        "text": "NVIDIA NIM free GLM endpoint is integrate.api.nvidia.com/v1 with model z-ai/glm-5.2 for remote inference without Spark.",
    },
    {
        "id": "d7",
        "text": "The SMF Clearinghouse blog lives at smfclearinghouse.com with posts under content/blog and hero SVGs in public/images/blog.",
    },
    {
        "id": "d8",
        "text": "Co-tenancy note: 8B BF16 embeddings use about 15 GiB. Running alongside the 35B MoE at util 0.75 often leaves only a few GB free.",
    },
]

QUERIES = [
    {
        "id": "q1",
        "text": "Which port and recipe serve Nemotron embedding models for RAG?",
        "relevant": ["d2", "d8"],
    },
    {
        "id": "q2",
        "text": "How do I launch the frozen Qwen 35B NVFP4 model on Spark?",
        "relevant": ["d1"],
    },
    {
        "id": "q3",
        "text": "What is Nemo's AgentMail address?",
        "relevant": ["d3"],
    },
    {
        "id": "q4",
        "text": "GPU memory utilization guidance on DGX Spark UMA for large models",
        "relevant": ["d4", "d8"],
    },
    {
        "id": "q5",
        "text": "Where is the SMF technical blog deployed?",
        "relevant": ["d7"],
    },
    {
        "id": "q6",
        "text": "Remote GLM model via NVIDIA NIM free tier",
        "relevant": ["d6"],
    },
]


def dcg_at_k(rels: list[int], k: int) -> float:
    s = 0.0
    for i, r in enumerate(rels[:k]):
        s += (2**r - 1) / math.log2(i + 2)
    return s


def ndcg_at_k(ranked_ids: list[str], relevant: set[str], k: int = 10) -> float:
    rels = [1 if did in relevant else 0 for did in ranked_ids[:k]]
    ideal = sorted(rels, reverse=True)
    idcg = dcg_at_k(ideal, k)
    if idcg == 0:
        return 0.0
    return dcg_at_k(rels, k) / idcg


def recall_at_k(ranked_ids: list[str], relevant: set[str], k: int = 10) -> float:
    if not relevant:
        return 0.0
    hit = sum(1 for did in ranked_ids[:k] if did in relevant)
    return hit / len(relevant)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", default="")
    ap.add_argument("--no-v2", action="store_true")
    args = ap.parse_args()

    wait_ready(args.base)
    client = SparkEmbedClient(base_url=args.base, model=args.model, use_v2=not args.no_v2)

    docs = [c["text"] for c in CORPUS]
    doc_ids = [c["id"] for c in CORPUS]
    d_emb = client.embed_documents(docs)
    # L2 for safety
    d_emb = d_emb / np.maximum(np.linalg.norm(d_emb, axis=1, keepdims=True), 1e-12)

    per_q = []
    ndcgs, recalls = [], []
    for q in QUERIES:
        q_emb = client.embed_queries([q["text"]])[0]
        q_emb = q_emb / max(np.linalg.norm(q_emb), 1e-12)
        scores = d_emb @ q_emb
        order = np.argsort(-scores)
        ranked = [doc_ids[i] for i in order]
        rel = set(q["relevant"])
        n10 = ndcg_at_k(ranked, rel, 10)
        r3 = recall_at_k(ranked, rel, 3)
        ndcgs.append(n10)
        recalls.append(r3)
        per_q.append(
            {
                "query_id": q["id"],
                "query": q["text"],
                "relevant": q["relevant"],
                "ranked_top5": ranked[:5],
                "scores_top5": [float(scores[i]) for i in order[:5]],
                "ndcg@10": n10,
                "recall@3": r3,
            }
        )
        print(f"{q['id']}: nDCG@10={n10:.3f} R@3={r3:.3f} top={ranked[:3]}")

    out = {
        "serve_recipe_id": RECIPE_ID,
        "model": args.model,
        "base": args.base,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mean_ndcg@10": float(np.mean(ndcgs)),
        "mean_recall@3": float(np.mean(recalls)),
        "per_query": per_q,
    }
    path = Path(
        args.out
        or (
            Path(__file__).resolve().parents[1]
            / "results"
            / f"praxis_rag_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        )
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2))
    print(f"\nmean nDCG@10={out['mean_ndcg@10']:.3f}  mean R@3={out['mean_recall@3']:.3f}")
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
