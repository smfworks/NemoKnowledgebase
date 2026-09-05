# Qwen3.8-Flash-Next TP=1 on spark-d369 — Official A (2026-09-05)

Harness: smf-bench Official A `strict_v01`, 157 tests, `--thinking off`, timeout 300s.

| Run | Tag | Recipe | Pass | Wall |
|-----|-----|--------|------|------|
| 262k MTP=3 | `cal-qwen38-flash-next-tp1-262k-d369-strict-v01` | `SMF-Spark-d369-Qwen38FN-TP1-262k-mtp3-fp8kv-gmu0780-kv16` | 137/157 (87.3%) | 3274.7 s |
| 16k MTP=0 (fallback after NV OOM) | `cal-qwen38-flash-next-tp1-d369-strict-v01` | `SMF-Spark-d369-Qwen38FN-TP1-16k-mtp0-fp8kv-gmu0671` | 133/157 (84.7%) | 5583.0 s |

Comparators on the same kit / same harness:

- GLM-5.3-Flash Unsloth UD-IQ2_XXS llama.cpp on d369: 121/157 (77.1%), tag `cal-glm53-flash-udiq2xxs-d369-strict-v01`
- DSV4 Vision-Exp TP=2 Official A (2026-09-02): 117/157 (74.5%), tag `cal-dsv4-vision-exp-f5463e7-strict-v01`

Checkpoint: `Mia-AiLab/Qwen3.8-Flash-Next-NVFP4` revision `925d7be6c14c6c9442ef83e8f05b5a3c39304f69`. Recipe: [MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark](https://github.com/MiaAI-Lab/Qwen3.8-Flash-Next-Single-DGX-Spark).
