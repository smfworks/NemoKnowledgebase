# Cold Iron command for Mia EAQ 2.9 bpw on 2x DGX Spark

Run from a checkout of `smfworks/smf-bench` that contains `run_stage1.py`. Use a Python that has `openai`. Hermes venv on the workstation was `/home/mikesai1/.hermes/hermes-agent/venv/bin/python`.

```bash
export SMF_SERVE_RECIPE_ID=SMF-Spark-DSV4.1-Flash-1017-MiaEAQ29-1afc891-tf
python3 run_stage1.py \
  --endpoint http://spark-56bc:8888/v1 \
  --model DeepSeek-V4.1-Flash-1017 \
  --tag cal-dsv41-flash-1017-mia-eaq29-tf-strict-v01 \
  --core-profile strict_v01 \
  --thinking off \
  --timeout 300 \
  --api-key dummy
```

`--thinking off` on this model id sends `chat_template_kwargs.enable_thinking=false` and `reasoning.effort=none`. On the TensorFold serve, `effort=none` alone still thinks. The scored file stored `reasoning_tokens` 0 because the template flag was also set.

Result: `results/stage1_cal-dsv41-flash-1017-mia-eaq29-tf-strict-v01_20261019_144922.json`
