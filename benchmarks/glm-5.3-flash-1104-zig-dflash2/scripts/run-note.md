# Cold Iron command for this boot

Thinking off. Model id from `/v1/models` on this boot: `GLM-5.3-Flash`.

```bash
cd /home/mikesai1/workspace/smf-bench
/home/mikesai1/.hermes/hermes-agent/venv/bin/python -u run_stage1.py \
  --endpoint http://spark-56bc:8020/v1 \
  --model GLM-5.3-Flash \
  --tag cal-glm53-flash-1104-zig-dflash2-strict-v01 \
  --core-profile strict_v01 \
  --thinking off \
  --timeout 300
```

Result: `results/stage1_cal-glm53-flash-1104-zig-dflash2-strict-v01_20261105_024541.json`

The JSON field `serve_recipe_id` says `SMF-Spark-vLLM-0.24-marlin`. That field is a stale process default. The serve is TensorFold Zig, image `tensorfold-glm53-spark:74e19a63a9a5`, checkout `138123c`, weights `76c0b517`, drafter DFlash2.
