# SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16 — Serve Recipe

**Recipe ID:** `SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16`  
**Status:** ACTIVE (2026-07-17)  
**Owner:** Nemo (DGX Spark testing lead)  
**Host:** `spark-56bc` (GB10 / Grace-Blackwell UMA)  
**Purpose:** Multilingual text embeddings for **Praxis RAG** (and general retrieval)

> **Rule:** Tag embedding eval / RAG index runs with this recipe ID.  
> **No silent flag drift.** Any change → new recipe ID.

---

## Identity

| Field | Value |
|-------|--------|
| Recipe ID | `SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16` |
| Engine | vLLM **0.24.0** (`vllm/vllm-openai:v0.24.0`) — NVIDIA-validated for this checkpoint (also notes `v0.25.0` preferred for `/v2/embed`) |
| Weights path (Spark) | `/home/mikesai3/Nemotron-3-Embed-8B-BF16` |
| HF id / served name | `nvidia/Nemotron-3-Embed-8B-BF16` |
| Params / dim | ~8B BF16 · embedding dim **4096** (slice+renorm supported: 2048/1024) |
| Max seq (card) | **32768** (this recipe default serve: **8192** for RAG-friendly memory) |
| License | OpenMDW-1.1 (commercial OK) + base Ministral Apache-2.0 |
| Endpoint (LAN) | `http://spark-56bc:8889/v1` and `/v2/embed` |
| Tunnel (workstation) | `ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -L 18001:localhost:8889 mikesai3@spark-56bc` → `http://127.0.0.1:18001` |

**Port choice:** **8889** (not 8888) so the frozen LLM recipe `SMF-Spark-vLLM-0.24-marlin` can coexist on 8888 when memory allows.  
**Co-tenancy:** 8B BF16 ≈ 16 GB weights. With the 35B MoE LLM at `gpu-memory-utilization 0.75`, free UMA is often only a few GB — **do not** assume both run at full util. Prefer: embed alone at 0.45, or drop LLM util / stop LLM for heavy indexing. For always-on co-tenancy, prefer `nvidia/Nemotron-3-Embed-1B-NVFP4` (separate recipe later).

---

## Model card facts (2026-07-16 launch)

- SOTA on multilingual **RTEB** as of 2026-07-16 (NVIDIA blog).
- Prefixes: **`query: `** for queries, **`passage: `** for documents.
- Embeddings L2-normalized → cosine ≡ dot product.
- Architecture: Ministral-3-8B encoder + average pooling + bidirectional attention.
- Expected Transformers warning (ignore): `Unrecognized keys in rope_parameters ... apply_yarn_scaling`.

---

## Frozen flags (canonical)

| Concern | Flag / value |
|---------|----------------|
| Model | `/model` (bind-mount of local snapshot) |
| Served name | `--served-model-name nvidia/Nemotron-3-Embed-8B-BF16` |
| Trust | `--trust-remote-code` |
| Dtype | `--dtype bfloat16` |
| GPU util | `--gpu-memory-utilization 0.45` |
| Context | `--max-model-len 8192` |
| Concurrency | `--max-num-seqs 32` |
| Bind | `--host 0.0.0.0` · `--port 8000` (host **8889→8000**) |

### Explicitly NOT in this recipe

| Item | Why |
|------|-----|
| MTP / tool / reasoning parsers | N/A for pooling/embed |
| `--moe-backend` | Dense encoder |
| `gpu-memory-utilization ≥ 0.7` | Leaves headroom; raise only when LLM is stopped |
| Image `v0.25.0` | Not yet on Spark; card validates 0.24.0; upgrade recipe if `/v2/embed` needs 0.25 |

---

## Canonical launch

Workstation:

```bash
~/workspace/smf-spark-vllm-0.24-nemotron3-embed-8b-bf16-launch.sh
```

On spark-56bc:

```bash
# RECIPE: SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16
docker rm -f nemotron3-embed-8b-bf16 2>/dev/null || true

docker run -d \
  --name nemotron3-embed-8b-bf16 \
  --gpus all \
  -p 8889:8000 \
  --shm-size=8g \
  -v /home/mikesai3/Nemotron-3-Embed-8B-BF16:/model:ro \
  -v /home/mikesai3/.cache/huggingface:/root/.cache/huggingface \
  vllm/vllm-openai:v0.24.0 \
  /model \
  --served-model-name nvidia/Nemotron-3-Embed-8B-BF16 \
  --trust-remote-code \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.45 \
  --max-model-len 8192 \
  --max-num-seqs 32 \
  --host 0.0.0.0 \
  --port 8000
```

Stop:

```bash
ssh mikesai3@spark-56bc 'docker rm -f nemotron3-embed-8b-bf16'
```

---

## Download (once)

```bash
ssh mikesai3@spark-56bc 'python3 - <<"PY"
from huggingface_hub import snapshot_download
print(snapshot_download(
    repo_id="nvidia/Nemotron-3-Embed-8B-BF16",
    local_dir="/home/mikesai3/Nemotron-3-Embed-8B-BF16",
))
PY'
# ~16 GB; do NOT use /home/mikesai3/models (root-owned)
```

---

## API usage (Praxis RAG)

### Preferred: `/v2/embed` (auto query/passage prompts)

```python
import requests, numpy as np
BASE = "http://spark-56bc:8889"  # or http://127.0.0.1:18001 via tunnel
MODEL = "nvidia/Nemotron-3-Embed-8B-BF16"

def embed(input_type: str, texts: list[str]) -> np.ndarray:
    r = requests.post(
        f"{BASE}/v2/embed",
        json={
            "model": MODEL,
            "input_type": input_type,  # "query" | "document"
            "texts": texts,
            "embedding_types": ["float"],
            "truncate": "END",
        },
        timeout=120,
    )
    r.raise_for_status()
    return np.array(r.json()["embeddings"]["float"], dtype=np.float32)
```

### OpenAI-compatible: `/v1/embeddings` (manual prefixes)

```python
from openai import OpenAI
client = OpenAI(base_url="http://spark-56bc:8889/v1", api_key="EMPTY")
resp = client.embeddings.create(
    model="nvidia/Nemotron-3-Embed-8B-BF16",
    input=["query: What is Praxis?", "passage: Praxis is ..."],
)
```

### Smoke

```bash
# with tunnel 18001→8889
python3 ~/workspace/smf-nemotron3-embed-smoke.py --base http://127.0.0.1:18001
# or direct LAN
python3 ~/workspace/smf-nemotron3-embed-smoke.py --base http://spark-56bc:8889
```

---

## Eval / index tagging

```json
{
  "serve_recipe_id": "SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16",
  "endpoint": "http://spark-56bc:8889/v1",
  "model": "nvidia/Nemotron-3-Embed-8B-BF16",
  "embedding_dim": 4096,
  "max_model_len": 8192
}
```

---

## Sibling models (future recipes)

| Model | Approx size | Role |
|-------|-------------|------|
| `nvidia/Nemotron-3-Embed-1B-BF16` | ~2.3 GB BF16 | Lighter RAG |
| `nvidia/Nemotron-3-Embed-1B-NVFP4` | ~0.76 GB packed | Best co-tenancy with LLM on Spark |
| `nvidia/Nemotron-3-Embed-8B-BF16` | ~16 GB | **This recipe** — best quality |

---

## Speed + accuracy testing (MTEB / Praxis RAG)

Harness: `~/workspace/smf-nemotron3-embed-bench/` (mteb 2.18.3 + OpenAI client to this endpoint).

| What | Command |
|------|---------|
| Speed | `python scripts/speed_bench.py --base http://127.0.0.1:18001` |
| Praxis synthetic RAG | `python scripts/praxis_rag_accuracy.py --base http://127.0.0.1:18001` |
| MTEB SciFact smoke | `python scripts/mteb_accuracy.py --preset smoke` |
| BEIR quick | `--preset quick` (SciFact, NFCorpus, ArguAna) |
| NVIDIA-aligned | `--preset rteb-en` or `--preset rteb` (`RTEB(eng, beta)` / `RTEB(beta)`) |

**Measured 2026-07-17 (this recipe, tunnel 18001):**

| Metric | Result |
|--------|--------|
| Single query latency | ~75 ms |
| Short docs batch=16 | ~71 texts/s |
| Medium docs batch=16 | ~25 texts/s |
| SciFact nDCG@10 (MTEB) | **0.834** |
| Praxis synthetic mean nDCG@10 | **0.975** |

Full README: `~/workspace/smf-nemotron3-embed-bench/README.md`

---

## References

- HF: https://huggingface.co/nvidia/Nemotron-3-Embed-8B-BF16  
- Blog: https://huggingface.co/blog/nvidia/nemotron-3-embed-wins-rteb  
- MTEB: https://github.com/embeddings-benchmark/mteb  
- Launch script: `~/workspace/smf-spark-vllm-0.24-nemotron3-embed-8b-bf16-launch.sh`  
- Smoke: `~/workspace/smf-nemotron3-embed-smoke.py`  
- Bench suite: `~/workspace/smf-nemotron3-embed-bench/`  
- LLM companion recipe: `SMF-Spark-vLLM-0.24-marlin` (port 8888)
