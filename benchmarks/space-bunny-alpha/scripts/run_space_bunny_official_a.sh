#!/usr/bin/env bash
set -euo pipefail
cd /home/mikesai1/workspace/smf-bench
if [[ -e hf-gate.json ]]; then
  echo "FATAL: hf-gate.json present — park it before Official A cloud" >&2
  exit 2
fi
set -a
# shellcheck disable=SC1091
source /home/mikesai1/.hermes/.env
set +a
if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "FATAL: OPENROUTER_API_KEY empty after sourcing ~/.hermes/.env" >&2
  exit 2
fi
export SMF_SERVE_RECIPE_ID=OpenRouter-cloud
exec python3 -u run_stage1.py \
  --endpoint https://openrouter.ai/api/v1 \
  --model stealth/space-bunny-alpha \
  --tag cal-space-bunny-alpha-strict-v01 \
  --core-profile strict_v01 \
  --thinking off \
  --timeout 300
