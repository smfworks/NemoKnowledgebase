#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/exllamav3/.venv/bin:/usr/local/cuda/bin:$PATH"
export TORCH_CUDA_ARCH_LIST=12.1
export CUDA_HOME=/usr/local/cuda
export EXL3_INT8_GEMV=0 EXL3_MOE_COOP_WIDE=1 EXL3_GR_INT8=1 EXL3_MTP_HEAD_N=65536 EXL3_NGRAM_STREAM=0
MODEL="$HOME/models/Qwen3.8-Flash-Next-EXL3"
OUT="$HOME/logs/exl3-native-test"
mkdir -p "$OUT"
cd "$HOME/exllamav3"
{
  echo "=== $(date -Is) HEAD=$(git rev-parse --short HEAD) ==="
  "$HOME/exllamav3/.venv/bin/python" - <<'PY'
import os, torch
from pathlib import Path
from exllamav3 import ext
p = Path(os.path.expanduser("~/models/Qwen3.8-Flash-Next-EXL3"))
print("torch", torch.__version__, "cuda", torch.version.cuda, "avail", torch.cuda.is_available())
print("ext", ext.exllamav3_ext.__file__)
need = ["config.json", "model.safetensors.index.json", "ngram_embedding.safetensors", "tokenizer.json"]
for n in need:
    f = p / n
    print(("OK" if f.exists() else "MISSING"), n, f.stat().st_size if f.exists() else 0)
shards = list(p.glob("model-*.safetensors"))
print("shards", len(shards), "bytes", sum(s.stat().st_size for s in shards))
print("pack_total_bytes", sum(f.stat().st_size for f in p.rglob("*") if f.is_file()))
PY
} | tee "$OUT/summary.txt"

run_prompt() {
  local tag="$1"
  local prompt="$2"
  "$HOME/drop-model-cache.sh" >/dev/null 2>&1 || true
  sleep 8
  local log="$OUT/${tag}.log"
  echo "=== RUN $tag $(date -Is) ===" | tee -a "$OUT/summary.txt"
  /usr/bin/time -f "WALL %e s  MAXRSS %M KB" \
    taskset -c 5-9,15-19 python examples/chat.py -m "$MODEL" -mode qwen35 \
      -mtp -ndt 5 -dds -dc 0.6 -cq 8,8 -cs 32768 \
      -tps -basic -lm -no_think -topk 1 -maxr 400 \
      -prompt "$prompt" > "$log" 2>&1 || true
  local tps
  tps=$(tr "\r" "\n" < "$log" | grep -oE "[0-9]+(\.[0-9]+)? tokens/second" | tail -1 || true)
  grep -E "Load time|Total size|^Context:|WALL|Traceback|Error|Insufficient" "$log" \
    | tr "\r" "\n" | grep -v "^$" | tail -12 | tee -a "$OUT/summary.txt" || true
  echo "$tag tps=${tps:-NO}" | tee -a "$OUT/summary.txt"
}

CODE='Write a Python function that parses an nginx access log line into a dict with fields ip, timestamp, method, path, status, bytes. Include a docstring, type hints, and a short usage example. Then explain each regex group in one bullet each.'
DEVOPS='Explain, for a DevOps engineer, how Kubernetes horizontal pod autoscaling decides when to scale, including the formula it uses and two common pitfalls. Then give a complete example HPA YAML.'
PROSE='Write a vivid 350-word short story about a lighthouse keeper on a remote island in Alaska who discovers something unexpected washed ashore after a storm.'
MATH='What is 17 * 19? Reply with the integer only.'
FN='Write a Python function is_palindrome(s: str) -> bool. No markdown, just the function.'

run_prompt code "$CODE"
run_prompt devops "$DEVOPS"
run_prompt prose "$PROSE"
run_prompt math "$MATH"
run_prompt fn "$FN"

echo "=== done $(date -Is) ===" | tee -a "$OUT/summary.txt"
