# Official A board — compiled 2026-09-10

Source: `/home/mikesai1/workspace/smf-bench/results/stage1_*.json`
Rule: `strict_v01`, 157 tests, **thinking off**. One row per distinct model/serve.
Thinking-on arms are diagnostic and are not ranked.

| Rank | Model | Score | Err | Coding | Math | Tools | Wall | Where | JSON |
|------|-------|-------|-----|--------|------|-------|------|-------|------|
| 1 (tie) | GPT-6 Astra Pro (batch) | 153/157 (97.5%) | 0 | 30/30 | 28/30 | 2/2 | 283.9 s | OpenRouter Batch | stage1_cal-gpt6-astra-pro-batch-strict-v01_20260909_171401.json |
| 1 (tie) | Grok 4.6 | 153/157 (97.5%) | 0 | 30/30 | 28/30 | 2/2 | 9002.6 s | OpenRouter | stage1_showdown-grok46-strict-v01_20260812_200159.json |
| 3 | Grok 4.5 | 152/157 (96.8%) | 0 | 30/30 | 27/30 | 2/2 | 6707.2 s | OpenRouter | stage1_showdown-grok45-strict-v01_20260810_102512.json |
| 4 (tie) | Gemini 3.8 Flash | 145/157 (92.4%) | 0 | 28/30 | 24/30 | 2/2 | 1164.1 s | OpenRouter | stage1_cal-gemini-38-flash-or-strict-v01_20260902_201506.json |
| 4 (tie) | Muse Spark 1.3 | 145/157 (92.4%) | 0 | 30/30 | 25/30 | 1/2 | 1134.7 s | OpenRouter | stage1_cal-muse-spark-13-or-strict-v01_20260902_234054.json |
| 6 | Claude Fable 5.1 | 142/157 (90.4%) | 0 | 26/30 | 26/30 | 2/2 | 2100.8 s | OpenRouter | stage1_cal-fable-51-or-strict-v01_20260902_184808.json |
| 7 | Kimi K3 | 140/157 (89.2%) | 0 | 23/30 | 24/30 | 2/2 | 2890.8 s | Ollama Cloud | stage1_sweep2-kimi-k3-strict-v01_20260811_050129.json |
| 8 | Qwen3.5-397B | 138/157 (87.9%) | 0 | 19/30 | 27/30 | 2/2 | 6845.1 s | Ollama Cloud | stage1_sweep2-qwen35-397b-strict-v01_20260811_045942.json |
| 9 | Qwen3.8-Flash-Next (TP1 262k) | 137/157 (87.3%) | 0 | 30/30 | 19/30 | 2/2 | 3274.7 s | 1× DGX Spark | stage1_cal-qwen38-flash-next-tp1-262k-d369-strict-v01_20260905_124310.json |
| 10 | Hy4 preview | 130/157 (82.8%) | 0 | 27/30 | 13/30 | 2/2 | 1828.5 s | OpenRouter | stage1_cal-hy4-preview-or-strict-v01_20260909_105540.json |
| 11 | Ox Alpha | 129/157 (82.2%) | 0 | 20/30 | 22/30 | 2/2 | 9478.0 s | OpenRouter | stage1_cal-ox-alpha-strict-v01-20260824_20260824_155541.json |
| 12 | DeepSeek V4 Pro | 128/157 (81.5%) | 0 | 22/30 | 26/30 | 2/2 | 2486.9 s | Ollama Cloud | stage1_sweep2-deepseek-v4-pro-strict-v01_20260811_045944.json |
| 13 | DeepSeek V4.1 Flash | 127/157 (80.9%) | 0 | 23/30 | 16/30 | 2/2 | 559.0 s | OpenRouter | stage1_cal-dsv41-flash-or-strict-v01_20260910_102438.json |
| 14 | Qwen3.8-Max | 125/157 (79.6%) | 0 | 12/30 | 21/30 | 2/2 | 6027.4 s | OpenRouter | stage1_showdown-qwen38-max-strict-v01_20260810_102511.json |
| 15 | Qwen3.8-27B-FP8 | 124/157 (79.0%) | 0 | 26/30 | 15/30 | 2/2 | 6116.3 s | 1× DGX Spark | stage1_cal-qwen38-27b-fp8-strict-v01_20260816_235222.json |
| 16 | Qwen3.6-35B-NVFP4 | 123/157 (78.3%) | 0 | 22/30 | 16/30 | 2/2 | 1907.0 s | 1× DGX Spark | stage1_cal-unsloth-qwen36-35b-nvfp4-strict-v01_20260711_024345.json |
| 17 (tie) | GLM-5.3-Flash UDIQ2XXS | 121/157 (77.1%) | 0 | 25/30 | 12/30 | 2/2 | 7119.9 s | 1× DGX Spark | stage1_cal-glm53-flash-udiq2xxs-d369-strict-v01_20260905_010914.json |
| 17 (tie) | GLM-5.2 | 121/157 (77.1%) | 0 | 14/30 | 17/30 | 2/2 | 3155.6 s | Ollama Cloud | stage1_showdown-glm52-strict-v01_20260810_123329.json |
| 19 | DSV4 Vision-Exp | 117/157 (74.5%) | 0 | 22/30 | 13/30 | 2/2 | 1526.0 s | 2× DGX Spark | stage1_cal-dsv4-vision-exp-f5463e7-strict-v01_20260902_151647.json |
| 20 | Laguna S 2.1-NVFP4 | 107/157 (68.2%) | 0 | 24/30 | 8/30 | 2/2 | 1945.8 s | 1× DGX Spark | stage1_cal-laguna-s-2.1-nvfp4-strict-v01_20260721_203834.json |
| 21 | Mistral Large 3 | 104/157 (66.2%) | 0 | 8/30 | 11/30 | 2/2 | 2307.1 s | Ollama Cloud | stage1_sweep2-mistral-large-3-strict-v01_20260811_045943.json |
| 22 (tie) | GLM-5.3-Flash EXL3 | 103/157 (65.6%) | 0 | 25/30 | 3/30 | 2/2 | 2409.6 s | 1× DGX Spark | stage1_cal-glm53-flash-exl3-493cb88-strict-v01_20260831_125733.json |
| 22 (tie) | Nemotron 3 Ultra | 103/157 (65.6%) | 0 | 14/30 | 12/30 | 2/2 | 6058.1 s | Ollama Cloud | stage1_sweep2-nemotron-3-ultra-strict-v01_20260811_045945.json |
| 24 | DSV4 Flash 0731 (DSpark) | 99/157 (63.1%) | 0 | 7/30 | 24/30 | 2/2 | 7355.7 s | 2× DGX Spark | stage1_cal-dsv4-flash-dspark-strict-v01_20260817_235600.json |
| 25 | Nex-N2.5-Pro free | 81/157 (51.6%) | 12 | 16/30 | 1/30 | 0/2 | 4715.3 s | OpenRouter | stage1_cal-nex-n25-pro-or-strict-v01_20260909_030620.json |

Not ranked (same model, other serve or incomplete): Qwen3.8-Flash-Next TP1 non-262k 133/157; Ox Alpha first morning 127/157; V4.1 Flash thinking-on 130/157; DSV4 Flash thinking-on 97/157; AEON uncensored 113/157 with 8 errors; 150-test partials.
