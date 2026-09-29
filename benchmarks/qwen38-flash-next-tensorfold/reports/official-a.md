# Qwen3.8-Flash-Next TensorFold — Official A (2026-09-29)

Measured on the live single-Spark serve. Do not mix this score with the Mia NVFP4 137/157 row or the EXL3 140/157 row.

- Model id: `Qwen3.8-Flash-Next`
- Endpoint: `http://spark-56bc:8888/v1` (no API key)
- Tag: `cal-qwen38-flash-next-tensorfold-strict-v01`
- Profile: `strict_v01` / standard v0.1.1
- Thinking: off (`chat_template_kwargs.enable_thinking=false`). Default serve still thinks. Smoke the same morning: thinking-off content `4`, reasoning empty; default content `4` with a reasoning string.
- Recipe: `SMF-Spark-TensorFold-0.3.6.3-qwen38-856bb6b`
- Checkout: `MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark-TensorFold` `@856bb6b`
- Image: `v0.3.6.3-5f313914582d`
- Checkpoint: `Vontra/Qwen3.8-Flash-Next-MLX-4bit-MTP` (`dadefa8066e3be900a0d148d0f5a2f4eb1cf6534`)
- Score: **131/157 (83.4%)**, fail 26, error 0
- Wall: 1884.8 s
- hf-gate: yellow. H=2560, MoE intermediate=640, 48 layers, 512 experts, top-10, tile aligned, `intermediate_size_risk` true, not NVFP4. Stamped `effective_m_at_max_seqs` 0.078125 uses the runner default of 4 sequences, not the live `PARALLEL=5`.
- JSON: `results/stage1_cal-qwen38-flash-next-tensorfold-strict-v01_20260929_115051.json`

Categories:

| category | pass |
| --- | --- |
| math | 17/30 |
| coding | 27/30 |
| reasoning | 25/30 |
| instruction | 27/30 |
| prose | 29/30 |
| writing | 4/5 |
| tool_calling | 2/2 |

Same-day recipe checks on the same serve, before Official A, so they did not share the GPU with the 157:

- `tools/toolcheck.py` OK
- `tools/visioncheck.py` OK
- `tools/needle.py` 194893 tokens, prefill 101.5083 s, total 106.7 s, answer correct
- `tools/bench.py` prefill 1933 / 2332 / 2446 / 2377 tok/s at 855 / 3205 / 12636 / 50350 tokens. Decode 69.9 tok/s code greedy, 57.5 tok/s chat sampled.

Neighbors, different engines, do not flatten:

- Mia NVFP4 TP=1 262k: 137/157, wall 3274.7 s (`stage1_cal-qwen38-flash-next-tp1-262k-d369-strict-v01_20260905_124310.json`)
- EXL3 TabbyAPI: 140/157, wall 1662.4 s (`stage1_cal-qwen38-flash-next-exl3-tabby-strict-v01_20260920_205418.json`)
- Hy4 preview: 130/157, wall 1828.5 s
