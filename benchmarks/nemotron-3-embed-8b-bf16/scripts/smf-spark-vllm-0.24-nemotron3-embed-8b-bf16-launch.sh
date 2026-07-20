#!/bin/bash
# SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16 — Nemotron-3-Embed-8B-BF16 on spark-56bc
# Recipe ID: SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16
# Docs: /home/mikesai1/NemoKnowledgebase/SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16.md
set -euo pipefail

RECIPE_ID="SMF-Spark-vLLM-0.24-nemotron3-embed-8b-bf16"
REMOTE="${REMOTE:-mikesai3@spark-56bc}"
CONTAINER="nemotron3-embed-8b-bf16"
IMAGE="vllm/vllm-openai:v0.24.0"
CKPT="/home/mikesai3/Nemotron-3-Embed-8B-BF16"
# Host 8889 keeps 8888 free for SMF-Spark-vLLM-0.24-marlin (LLM)
PORT="${PORT:-8889}"
GPU_UTIL="${GPU_UTIL:-0.45}"
MAX_LEN="${MAX_LEN:-8192}"

echo "=== Launch $RECIPE_ID on $REMOTE (port $PORT) ==="

ssh -o ServerAliveInterval=30 -o ServerAliveCountMax=10 -o BatchMode=yes "$REMOTE" bash -s << EOF
set -euo pipefail
if [ ! -f "$CKPT/config.json" ]; then
  echo "ERROR: missing checkpoint $CKPT (run download first)"
  exit 1
fi
if [ ! -f "$CKPT/model.safetensors.index.json" ] && ! ls "$CKPT"/model-*.safetensors >/dev/null 2>&1; then
  echo "ERROR: weights incomplete under $CKPT"
  exit 1
fi
docker rm -f $CONTAINER 2>/dev/null || true
docker run -d \\
  --name $CONTAINER \\
  --gpus all \\
  -p $PORT:8000 \\
  --shm-size=8g \\
  -v $CKPT:/model:ro \\
  -v /home/mikesai3/.cache/huggingface:/root/.cache/huggingface \\
  $IMAGE \\
  /model \\
  --served-model-name nvidia/Nemotron-3-Embed-8B-BF16 \\
  --trust-remote-code \\
  --dtype bfloat16 \\
  --gpu-memory-utilization $GPU_UTIL \\
  --max-model-len $MAX_LEN \\
  --max-num-seqs 32 \\
  --host 0.0.0.0 \\
  --port 8000
echo "Launched $CONTAINER ($RECIPE_ID)"
docker ps --filter name=$CONTAINER --format '{{.Names}} {{.Status}} {{.Ports}}'
EOF

echo "Endpoint (LAN): http://spark-56bc:$PORT/v1"
echo "Preferred retrieval API: http://spark-56bc:$PORT/v2/embed (input_type=query|document)"
echo "OpenAI-compatible: /v1/embeddings (prefix query: / passage: yourself)"
echo "Tunnel: ssh -L 18001:localhost:$PORT mikesai3@spark-56bc  →  http://127.0.0.1:18001"
echo "Tag results with serve_recipe_id=$RECIPE_ID"
