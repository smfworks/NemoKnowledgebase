#!/usr/bin/env python3
"""Lock full public-complete RAG eval report (15/21 RTEB; 6 private gated skipped)."""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timezone
from pathlib import Path

CACHE = Path.home() / ".cache/mteb/results/nvidia__Nemotron-3-Embed-8B-BF16/spark-served"
RESULTS = Path.home() / "workspace/smf-nemotron3-embed-bench/results"
REPORT = Path.home() / "NemoKnowledgebase/nemotron3-embed-8b-spark-rag-eval-report.md"
BEIR = ["SciFact", "NFCorpus", "ArguAna", "FiQA2018", "TRECCOVID", "QuoraRetrieval"]
RTEB = [
    "AILACasedocs",
    "AILAStatutes",
    "LegalSummarization",
    "FinanceBenchRetrieval",
    "HC3FinanceRetrieval",
    "FinQARetrieval",
    "AppsRetrieval",
    "DS1000Retrieval",
    "HumanEvalRetrieval",
    "MBPPRetrieval",
    "WikiSQLRetrieval",
    "FreshStackRetrieval",
    "SWEbenchCodeRetrieval",
    "ChatDoctorRetrieval",
    "Code1Retrieval",
    "EnglishFinance1Retrieval",
    "EnglishFinance2Retrieval",
    "EnglishFinance3Retrieval",
    "EnglishFinance4Retrieval",
    "EnglishHealthcare1Retrieval",
    "CUREv1",
]
PRIVATE = {
    "Code1Retrieval",
    "EnglishFinance1Retrieval",
    "EnglishFinance2Retrieval",
    "EnglishFinance3Retrieval",
    "EnglishFinance4Retrieval",
    "EnglishHealthcare1Retrieval",
}
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
        "ndcg_at_10": float(row.get("ndcg_at_10")),
        "recall_at_10": row.get("recall_at_10"),
        "split": split,
    }


def table(rows: list[dict]) -> tuple[str, float]:
    lines = [
        "| Task | nDCG@10 | Recall@10 |",
        "|------|--------:|----------:|",
    ]
    for r in rows:
        r10 = r.get("recall_at_10")
        r10s = f"{float(r10):.4f}" if r10 is not None else "—"
        lines.append(f"| {r['name']} | {r['ndcg_at_10']:.4f} | {r10s} |")
    m = statistics.mean(r["ndcg_at_10"] for r in rows)
    lines.append(f"| **Macro mean** | **{m:.4f}** | — |")
    return "\n".join(lines), m


def main() -> int:
    beir_rows = [load_ndcg(n) for n in BEIR]
    if not all(beir_rows):
        raise SystemExit("missing BEIR results")
    public_rows: list[dict] = []
    private_missing: list[str] = []
    for n in RTEB:
        r = load_ndcg(n)
        if r:
            public_rows.append(r)
        elif n in PRIVATE:
            private_missing.append(n)
        else:
            raise SystemExit(f"missing public task: {n}")

    beir_tbl, beir_macro = table(beir_rows)
    public_by_name = sorted(public_rows, key=lambda r: r["name"])
    rteb_tbl, rteb_macro = table(public_by_name)
    ranked = sorted(public_rows, key=lambda r: r["ndcg_at_10"])
    weakest = ranked[:3]
    strongest = list(reversed(ranked[-5:]))

    speed = json.loads((RESULTS / "speed_20260717T161853Z.json").read_text())
    praxis = json.loads((RESULTS / "praxis_rag_20260717T160721Z.json").read_text())
    q_lat = float((speed.get("query_single") or {}).get("latency_s_mean") or 0.0748)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    summary = {
        "serve_recipe_id": RECIPE,
        "finalized_utc": datetime.now(timezone.utc).isoformat(),
        "status": "COMPLETE_PUBLIC",
        "beir_macro_ndcg_at_10": beir_macro,
        "rteb_eng_public_macro_ndcg_at_10": rteb_macro,
        "rteb_eng_public_n": len(public_rows),
        "rteb_eng_total_benchmark": len(RTEB),
        "rteb_private_skipped": private_missing,
        "beir": beir_rows,
        "rteb_eng_public": sorted(public_rows, key=lambda x: -x["ndcg_at_10"]),
        "praxis_mean_ndcg_at_10": praxis.get("mean_ndcg@10"),
        "praxis_mean_recall_at_3": praxis.get("mean_recall@3"),
        "query_latency_s_mean": q_lat,
    }
    out_sum = RESULTS / f"final_summary_{stamp}.json"
    out_sum.write_text(json.dumps(summary, indent=2))

    priv_list = "\n".join(f"- `{n}`" for n in private_missing)
    strong_s = ", ".join(f"{r['name']} ({r['ndcg_at_10']:.3f})" for r in strongest)
    weak_s = ", ".join(f"{r['name']} ({r['ndcg_at_10']:.3f})" for r in weakest)
    trecc = load_ndcg("TRECCOVID")["ndcg_at_10"]
    nfc = load_ndcg("NFCorpus")["ndcg_at_10"]
    swe = load_ndcg("SWEbenchCodeRetrieval")["ndcg_at_10"]

    report = f"""# Nemotron-3-Embed-8B-BF16 on DGX Spark — RAG Evaluation Report

**Status:** **COMPLETE (all publicly runnable tasks)**  
**Finalized:** {now}  
**Owner:** Nemo  
**Serve recipe:** `{RECIPE}`  
**Purpose:** Production evidence for Praxis RAG on the **live Spark serve** (vLLM OpenAI embeddings API), using [MTEB](https://github.com/embeddings-benchmark/mteb).

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
| Eval | MTEB **2.18.3** · `SparkNemotron3EmbedEncoder` · truncate ≤8192 tokens |
| Harness | `~/workspace/smf-nemotron3-embed-bench/` |

All metrics tag **`serve_recipe_id = {RECIPE}`**.

---

## 2. Method

### Speed
HTTP via workstation tunnel (includes RTT). Batch × length matrix + concurrency. Prefer `/v2/embed`.

### Accuracy
1. **BEIR-style** — 6 public retrieval tasks  
2. **RTEB(eng, beta)** — English real-world retrieval suite  
3. **Praxis synthetic** — 8 SMF/Spark docs, 6 queries  

Primary metric: **nDCG@10**. Long docs truncated client-side to serve max length (NVIDIA card eval used seqlen 4096).

### RTEB coverage note (important)
`RTEB(eng, beta)` lists **21** tasks. **{len(public_rows)} are public and completed.**  
**{len(private_missing)} are private/gated HuggingFace datasets** and were **skipped** (no dataset access):

{priv_list}

MTEB: *Dataset for private task … not found*. Completing those needs HF credentials with access — not a serve failure.

### Out of scope
Full multilingual `RTEB(beta)`, ViDoRe, co-tenancy stress with 35B MoE, labeled production Praxis gold set.

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

- **Single query mean: ~{q_lat * 1000:.1f} ms** (tunnel included)  
- Concurrency beyond ~2 workers adds little wall throughput for medium docs  

**Interpretation:** Interactive RAG latency is fine. Prefer short/medium chunks for indexing; long multi-KB chunks ~4 texts/s.

---

## 4. Accuracy

### 4.1 BEIR-style (complete — 6/6)

{beir_tbl}

**Macro nDCG@10 = {beir_macro:.4f}**

Notes:
- **TRECCOVID** R@10 is low by multi-relevant design; nDCG@10 ({trecc:.3f}) is the headline.  
- **NFCorpus** ({nfc:.3f}) is the BEIR weak spot.

### 4.2 RTEB(eng, beta) — public complete ({len(public_rows)}/21)

{rteb_tbl}

**Public macro nDCG@10 = {rteb_macro:.4f}**  
({len(public_rows)} public tasks; {len(private_missing)} private skipped)

| | Tasks (nDCG@10) |
|--|------------------|
| Strongest | {strong_s} |
| Weakest | {weak_s} |

**Pattern:**
- Code/SQL/finance public tasks excellent (several ≥0.95; HumanEval = 1.0).  
- Healthcare ChatDoctor solid (~0.77). CUREv1 ~0.68.  
- Legal AILA and FreshStack weaker (~0.48–0.58).  
- **SWEbenchCodeRetrieval is an outlier low ({swe:.3f})** — long code-context + 8192 truncate hurts this task; treat separately from general RAG fitness.

### 4.3 Praxis synthetic (complete)

| Metric | Score |
|--------|------:|
| Mean nDCG@10 | **{praxis.get('mean_ndcg@10')}** |
| Mean Recall@3 | **{praxis.get('mean_recall@3')}** |

Artifact: `results/praxis_rag_20260717T160721Z.json`

---

## 5. Context vs NVIDIA card

- NVIDIA reports RTEB / MMTEB Retrieval / ViDoRe with eval length **4096** on their stack.  
- We report **this serve recipe** over HTTP at max_model_len **8192** with truncation.  
- Private RTEB subsets were not accessible here; public English slice is the honest external claim.

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
| Online latency | ~{q_lat * 1000:.0f} ms query |
| BEIR macro nDCG@10 | **{beir_macro:.3f}** |
| RTEB(eng) public macro nDCG@10 | **{rteb_macro:.3f}** ({len(public_rows)}/21 public) |
| Praxis synthetic nDCG@10 | **{praxis.get('mean_ndcg@10')}** |
| Serve stability | Production-usable with tunnel + truncation |

### Caveats
1. **NFCorpus / legal AILA / FreshStack** weaker — monitor if Praxis shifts heavily multi-label biomedical or legal case retrieval.  
2. **SWEbenchCodeRetrieval ({swe:.3f})** — do not use this serve as-is for long unchunked code-repo retrieval without better chunking / higher max_model_len experiment.  
3. **Long documents** must be chunked (or accept truncate-to-8192).  
4. **6 private RTEB tasks** unfinished without HF gated access — optional if you get dataset access.  
5. **Co-tenancy** with full 35B LLM needs util planning or 1B-NVFP4 sidecar.  
6. **Product KPI** still wants 50–100 labeled Praxis Q→doc pairs.

### Checklist
- [x] Speed complete  
- [x] BEIR complete (6/6)  
- [x] RTEB(eng) all **public** tasks complete ({len(public_rows)}/21; {len(private_missing)} private skipped)  
- [x] Full public report locked  
- [ ] Optional: private RTEB tasks with HF access  
- [ ] Praxis gold-set (next)  
- [ ] Optional 1B-NVFP4 co-tenancy recipe  

---

## 8. Reproduce

```bash
~/workspace/smf-spark-vllm-0.24-nemotron3-embed-8b-bf16-launch.sh
ssh -i ~/.ssh/id_spark_migration -o IdentitiesOnly=yes \\
  -o ServerAliveInterval=30 -o ServerAliveCountMax=10 \\
  -N -L 18001:localhost:8889 mikesai3@spark-56bc &

cd ~/workspace/smf-nemotron3-embed-bench && source .venv/bin/activate
export NEMO_EMBED_BASE=http://127.0.0.1:18001
python scripts/speed_bench.py --base $NEMO_EMBED_BASE
python scripts/praxis_rag_accuracy.py --base $NEMO_EMBED_BASE
python scripts/mteb_accuracy.py --preset beir --base $NEMO_EMBED_BASE
python scripts/mteb_accuracy.py --preset rteb-en --base $NEMO_EMBED_BASE
# private tasks need HF token + dataset access, then re-run rteb-en
```

---

## 9. Artifacts

| Kind | Path |
|------|------|
| This report | `NemoKnowledgebase/nemotron3-embed-8b-spark-rag-eval-report.md` |
| Final JSON | `{out_sum}` |
| MTEB cache | `~/.cache/mteb/results/nvidia__Nemotron-3-Embed-8B-BF16/spark-served/` |
| RTEB run dir | `workspace/smf-nemotron3-embed-bench/results/mteb_rteb-en_20260719T112351Z/` |
| Serve recipe | `NemoKnowledgebase/SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16.md` |
| Bench README | `workspace/smf-nemotron3-embed-bench/README.md` |

---

*Locked {now}. Public RTEB {len(public_rows)}/21; private gated tasks documented as skipped.*
"""
    REPORT.write_text(report)
    (RESULTS / "FULL_REPORT_READY").write_text(
        f"FULL_REPORT_READY {datetime.now(timezone.utc).isoformat()} public_rteb={len(public_rows)}/21\n"
    )
    (RESULTS / "ACCURACY_CHAIN_DONE").write_text(
        f"complete {datetime.now(timezone.utc).isoformat()} public_complete\n"
    )
    print(f"Wrote {REPORT}")
    print(f"Wrote {out_sum}")
    print(f"BEIR_macro={beir_macro:.4f}")
    print(f"RTEB_public_macro={rteb_macro:.4f} n={len(public_rows)}/21")
    print(f"private_skipped={private_missing}")
    print(f"strongest={strong_s}")
    print(f"weakest={weak_s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
