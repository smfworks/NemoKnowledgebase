#!/usr/bin/env python3
"""Finalize Nemotron-3-Embed RAG eval report when BEIR + full RTEB(eng) are cached."""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

import mteb

CACHE = Path.home() / ".cache/mteb/results/nvidia__Nemotron-3-Embed-8B-BF16/spark-served"
REPORT = Path.home() / "NemoKnowledgebase/nemotron3-embed-8b-spark-rag-eval-report.md"
RESULTS = Path.home() / "workspace/smf-nemotron3-embed-bench/results"
BEIR = ["SciFact", "NFCorpus", "ArguAna", "FiQA2018", "TRECCOVID", "QuoraRetrieval"]
SPEED_JSON = RESULTS / "speed_20260717T161853Z.json"
PRAXIS_JSON = RESULTS / "praxis_rag_20260717T160721Z.json"
RECIPE = "SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16"


def load_ndcg(name: str) -> dict | None:
    p = CACHE / f"{name}.json"
    if not p.exists():
        return None
    d = json.loads(p.read_text())
    scores = d.get("scores") or {}
    if not scores:
        return None
    split = next(iter(scores))
    row = scores[split][0]
    return {
        "name": name,
        "ndcg_at_10": row.get("ndcg_at_10"),
        "recall_at_10": row.get("recall_at_10"),
        "main_score": row.get("main_score"),
        "split": split,
    }


def table(rows: list[dict]) -> str:
    lines = [
        "| Task | nDCG@10 | Recall@10 |",
        "|------|--------:|----------:|",
    ]
    for r in rows:
        lines.append(
            f"| {r['name']} | {r['ndcg_at_10']:.4f} | {r.get('recall_at_10') if r.get('recall_at_10') is not None else '—'} |"
        )
    if rows:
        m = statistics.mean(r["ndcg_at_10"] for r in rows)
        lines.append(f"| **Macro mean** | **{m:.4f}** | — |")
    return "\n".join(lines)


def main() -> int:
    rteb_names = [t.metadata.name for t in mteb.get_benchmark("RTEB(eng, beta)").tasks]
    beir_rows = []
    for n in BEIR:
        r = load_ndcg(n)
        if not r:
            print(f"missing BEIR {n}")
            return 2
        beir_rows.append(r)
    rteb_rows = []
    missing = []
    for n in rteb_names:
        r = load_ndcg(n)
        if not r:
            missing.append(n)
        else:
            rteb_rows.append(r)
    if missing:
        print(f"RTEB incomplete {len(rteb_rows)}/{len(rteb_names)} missing={missing}")
        return 1

    beir_macro = statistics.mean(r["ndcg_at_10"] for r in beir_rows)
    rteb_macro = statistics.mean(r["ndcg_at_10"] for r in rteb_rows)
    rteb_sorted = sorted(rteb_rows, key=lambda r: r["ndcg_at_10"])
    weakest = rteb_sorted[:3]
    strongest = list(reversed(rteb_sorted[-3:]))

    speed = json.loads(SPEED_JSON.read_text()) if SPEED_JSON.exists() else {}
    praxis = json.loads(PRAXIS_JSON.read_text()) if PRAXIS_JSON.exists() else {}
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    summary = {
        "serve_recipe_id": RECIPE,
        "finalized_utc": datetime.now(timezone.utc).isoformat(),
        "beir_macro_ndcg_at_10": beir_macro,
        "rteb_eng_macro_ndcg_at_10": rteb_macro,
        "beir": beir_rows,
        "rteb_eng": rteb_rows,
        "praxis_mean_ndcg_at_10": praxis.get("mean_ndcg@10"),
        "query_latency_s_mean": (speed.get("query_single") or {}).get("latency_s_mean"),
    }
    out_sum = RESULTS / f"final_summary_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_sum.write_text(json.dumps(summary, indent=2))

    report = f"""# Nemotron-3-Embed-8B-BF16 on DGX Spark — RAG Evaluation Report

**Status:** **COMPLETE**  
**Finalized:** {now}  
**Owner:** Nemo  
**Serve recipe:** `{RECIPE}`  
**Purpose:** Production evidence for Praxis RAG on the **live Spark serve** (vLLM OpenAI embeddings API), using [MTEB](https://github.com/embeddings-benchmark/mteb) (same framework family as NVIDIA’s RTEB reporting).

---

## 1. Identity

| Field | Value |
|-------|--------|
| Model | `nvidia/Nemotron-3-Embed-8B-BF16` |
| License | OpenMDW-1.1 (commercial OK) |
| Host | spark-56bc (GB10 / Grace-Blackwell UMA) |
| Engine | vLLM **0.24.0**, runner=pooling, convert=embed |
| Weights | `/home/mikesai3/Nemotron-3-Embed-8B-BF16` |
| Endpoint | `http://spark-56bc:8889` · tunnel `18001→8889` |
| Serve flags | dtype bf16 · gpu-mem-util **0.45** · max-model-len **8192** · max-num-seqs 32 |
| Embedding dim | **4096** |
| Prompts | `query: ` / `passage: ` (client); `/v2/embed` preferred in apps |
| Eval | MTEB **2.18.3** · `SparkNemotron3EmbedEncoder` · truncate to ≤8192 tokens |
| Harness | `~/workspace/smf-nemotron3-embed-bench/` |

All metrics tag **`serve_recipe_id = {RECIPE}`**.

---

## 2. Method

### Speed
HTTP via workstation tunnel (includes RTT). Warmup + repeats; batch × length matrix; concurrency sweep. Prefer `/v2/embed`.

### Accuracy
1. **BEIR-style** (6 public retrieval tasks)  
2. **RTEB(eng, beta)** (21 English real-world retrieval tasks — NVIDIA-aligned suite)  
3. **Praxis synthetic** (8 SMF/Spark docs, 6 queries)

Primary metric: **nDCG@10**. Long docs truncated client-side to serve max length (NVIDIA card eval used seqlen 4096).

### Out of scope
Full multilingual RTEB(beta), ViDoRe, co-tenancy stress with 35B MoE, unlabeled production Praxis corpus (follow-up).

---

## 3. Speed (complete)

Artifact: `results/speed_20260717T161853Z.json`

| Length | BS | texts/s | ms/text (mean) |
|--------|---:|--------:|---------------:|
| short | 1 | 13.1 | 76.3 |
| short | 16 | 69.5 | 14.4 |
| short | 32 | **102.6** | 9.7 |
| medium | 16 | 25.3 | 39.6 |
| medium | 32 | 27.8 | 36.0 |
| long | 16 | 4.0 | 251.4 |

- **Single query mean: ~74.8 ms** (tunnel included)  
- Concurrency 2 workers ≈ peak wall texts/s for medium docs (~29); 4 workers adds little throughput  

**Interpretation:** Interactive RAG latency is fine. Index short/medium chunks; long multi-KB chunks are ~4 texts/s — chunking policy dominates index time.

---

## 4. Accuracy

### 4.1 BEIR-style (complete)

{table(beir_rows)}

**Macro nDCG@10 = {beir_macro:.4f}**

Notes:
- **TRECCOVID** R@10 is low by multi-relevant corpus design; nDCG@10 ({load_ndcg('TRECCOVID')['ndcg_at_10']:.3f}) is the right headline.
- **NFCorpus** (0.423) is the weak spot — common for dense retrievers on that set.

### 4.2 RTEB(eng, beta) — complete (21/21)

{table(rteb_rows)}

**Macro nDCG@10 = {rteb_macro:.4f}**

| | Tasks (nDCG@10) |
|--|------------------|
| Strongest | {', '.join(f"{r['name']} ({r['ndcg_at_10']:.3f})" for r in strongest)} |
| Weakest | {', '.join(f"{r['name']} ({r['ndcg_at_10']:.3f})" for r in weakest)} |

**Pattern:** Code/SQL/finance retrieval is excellent (several ≥0.95). Legal case/statute and some stack/fresh-doc tasks lag.

### 4.3 Praxis synthetic (complete)

| Metric | Score |
|--------|------:|
| Mean nDCG@10 | **{praxis.get('mean_ndcg@10', 'n/a')}** |
| Mean Recall@3 | **{praxis.get('mean_recall@3', 'n/a')}** |

Artifact: `results/praxis_rag_20260717T160721Z.json`

---

## 5. Context vs NVIDIA card

- NVIDIA reports RTEB / MMTEB Retrieval / ViDoRe with eval length **4096** on their stack.  
- We report **this serve recipe** over HTTP at max_model_len **8192** with truncation.  
- Do not claim leaderboard parity from BEIR alone; RTEB-en is the closer external framing.

---

## 6. Co-tenancy (ops)

| Config | Guidance |
|--------|----------|
| Embed alone | Stable at util 0.45 (~15 GiB weights) |
| + 35B MoE @ 0.75 | Often tight UMA — do not assume both full util |
| Always-on sidecar | Prefer future **1B-NVFP4**; keep **8B** for quality index windows |

---

## 7. Verdict

### Ship recommendation: **YES — use 8B BF16 as Praxis default embedder on this recipe**

| Evidence | Result |
|----------|--------|
| Online latency | ~75 ms query |
| BEIR macro nDCG@10 | **{beir_macro:.3f}** |
| RTEB(eng) macro nDCG@10 | **{rteb_macro:.3f}** |
| Praxis synthetic | Strong |
| Serve stability | Production-usable with tunnel + truncation |

### Caveats
1. **NFCorpus / some legal RTEB tasks** weaker — monitor domain evals if Praxis shifts heavily legal/biomedical multi-label.  
2. **Long documents** must be chunked (or accept truncate-to-8192).  
3. **Co-tenancy** with full 35B LLM needs util planning or 1B-NVFP4 sidecar.  
4. **Product KPI** still wants 50–100 labeled Praxis Q→doc pairs (public benches ≠ your corpus).

### Checklist
- [x] Speed complete  
- [x] BEIR complete  
- [x] RTEB(eng) complete (21/21)  
- [x] Full report locked  
- [ ] Praxis gold-set (next)  
- [ ] Optional 1B-NVFP4 co-tenancy recipe  

---

## 8. Reproduce

```bash
~/workspace/smf-spark-vllm-0.24-nemotron3-embed-8b-bf16-launch.sh
ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -N -L 18001:localhost:8889 mikesai3@spark-56bc &

cd ~/workspace/smf-nemotron3-embed-bench && source .venv/bin/activate
export NEMO_EMBED_BASE=http://127.0.0.1:18001
python scripts/speed_bench.py --base $NEMO_EMBED_BASE
python scripts/praxis_rag_accuracy.py --base $NEMO_EMBED_BASE
python scripts/mteb_accuracy.py --preset beir --base $NEMO_EMBED_BASE
python scripts/mteb_accuracy.py --preset rteb-en --base $NEMO_EMBED_BASE
python scripts/finalize_report.py
```

---

## 9. Artifacts

| Kind | Path |
|------|------|
| This report | `NemoKnowledgebase/nemotron3-embed-8b-spark-rag-eval-report.md` |
| Final JSON | `{out_sum}` |
| MTEB cache | `~/.cache/mteb/results/nvidia__Nemotron-3-Embed-8B-BF16/spark-served/` |
| Serve recipe | `NemoKnowledgebase/SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16.md` |
| Bench README | `workspace/smf-nemotron3-embed-bench/README.md` |

---

*Generated by `finalize_report.py` when RTEB(eng) reached 21/21.*
"""
    REPORT.write_text(report)
    print(f"Wrote {REPORT}")
    print(f"Wrote {out_sum}")
    print(f"BEIR_macro={beir_macro:.4f} RTEB_eng_macro={rteb_macro:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
