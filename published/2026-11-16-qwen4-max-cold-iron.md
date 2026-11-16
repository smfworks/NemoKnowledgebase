# Qwen4 Max scored mean 127/157 (80.9%) on Cold Iron over 3 runs — rank #33, math the weak leg

- **Date:** 2026-11-16
- **Model:** qwen/qwen4-max (canonical 20261115), OpenRouter, provider Alibaba
- **Suite:** Cold Iron (`strict_v01`, 157, effort=none — TRUE thinking-off; enable_thinking=false flag is ignored by this model, smoke-verified)
- **Result (n=3):** run1 126/157 (80.3%), run2 132/157 (84.1%), run3 123/157 (78.3%) — mean 127/157 (80.9%), range 123–132. Zero errors in all 471 rows. ~$1.06 total, ~26 min per run. Olympic rank #33 of 56 (mean-based).
- **Raw:** [benchmarks/qwen4-max](https://github.com/smfworks/NemoKnowledgebase/tree/main/benchmarks/qwen4-max)

## Published line

> Alibaba's new flagship means 127/157 over three same-payload runs (range 123–132, ~5.7 points) with thinking genuinely off — coding 25–28/30, instruction 27–28/30, tools 2/2 every run, but math is the weak leg and the noisiest category (12 of 30 items flip) against its own predecessor's 27/30 (endpoint differs, directional). One unicode-digit SyntaxError reproduced 2 of 3 runs. Total cost ~$1.06.

## Details

| Category | Score |
|---|---|
| Math | 15/30 |
| Coding | 25/30 |
| Reasoning | 26/30 |
| Instruction | 28/30 |
| Prose | 26/30 |
| Writing | 4/5 |
| Tool calling | 2/2 |
