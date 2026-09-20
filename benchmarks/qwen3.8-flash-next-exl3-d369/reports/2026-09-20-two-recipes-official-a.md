# Two one-Spark recipes, Official A — 2026-09-20

Same box: spark-d369 (NVIDIA GB10). Same harness: smf-bench `strict_v01`, 157 tests, `--thinking off`. MiniMax H3 on spark-56bc stayed HTTP 200.

## MiaAI-Lab NVFP4 + vLLM (pin)

- Tag: `cal-qwen38-flash-next-tp1-262k-d369-strict-v01`
- Date: 2026-09-05
- Recipe: MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark (later freeze `6b50864` for 24/7 kit)
- Checkpoint: Mia-AiLab/Qwen3.8-Flash-Next-NVFP4
- Result: **137/157 (87.3%)**, fail=20, error=0, wall 3274.7 s
- JSON: `results/stage1_cal-qwen38-flash-next-tp1-262k-d369-strict-v01_20260905_124310.json`

## vcruz305 EXL3 + TabbyAPI

- Tag: `cal-qwen38-flash-next-exl3-tabby-strict-v01`
- Date: 2026-09-20
- Recipe: vcruz305/Qwen3.8-Flash-Next-EXL3-DGX-Spark-recipe `e0ebee8`
- Engine: vcruz305/exllamav3 `329e051`
- Pack: turboderp/Qwen3.8-Flash-Next-exl3 `3.05bpw_h5_ng5`
- API: TabbyAPI `53da791` on `:8899`, `tool_format: qwen3_coder`
- Result: **140/157 (89.2%)**, fail=17, error=0, wall 1662.4 s
- JSON: `results/stage1_cal-qwen38-flash-next-exl3-tabby-strict-v01_20260920_205418.json`

Delta vs Mia pin: 7 fixed, 4 regressed, 13 both-fail. Coding 30/30 both. Tools 2/2 both. SyntaxError 0 both.

Do not quote native `chat.py` first code pass 25.99 tok/s (cold kernels). Quote rerun 79.53.
