#!/usr/bin/env bash
set -euo pipefail
# Requires smf-bench checkout and live endpoint
ENDPOINT="${ENDPOINT:-http://spark-56bc:8888/v1}"
cd "$(dirname "$0")/../../../smf-bench" 2>/dev/null || cd "${SMF_BENCH:-$HOME/workspace/smf-bench}"
python3 -u run_stage1.py \
  --endpoint "$ENDPOINT" \
  --model poolside/Laguna-S-2.1-NVFP4 \
  --tag cal-laguna-s-2.1-nvfp4-strict-v01 \
  --core-profile strict_v01 \
  --thinking off \
  --timeout 300
