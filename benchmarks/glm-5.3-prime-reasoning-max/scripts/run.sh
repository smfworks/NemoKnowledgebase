#!/usr/bin/env bash
# Reasoning-max arm. Not Cold Iron.
# Run this from a smf-bench checkout that honors SMF_REASONING_EFFORT.
# Cold Iron on this slug is --thinking off, which sends reasoning.effort=low.
set -euo pipefail
export SMF_SERVE_RECIPE_ID=OpenRouter-cloud
export SMF_REASONING_EFFORT=max
python3 run_stage1.py \
  --endpoint https://openrouter.ai/api/v1 \
  --model z-ai/glm-5.3-prime \
  --tag cal-glm-5.3-prime-reasoning-max-strict-v01 \
  --core-profile strict_v01 \
  --thinking on \
  --timeout 600
