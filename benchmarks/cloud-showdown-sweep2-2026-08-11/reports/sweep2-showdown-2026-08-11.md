# Sweep 2 Cloud Model Showdown — Final Eight-Model Report — 2026-08-11

**Date:** August 10-11, 2026
**Models:** 8 cloud models across OpenRouter and Ollama Cloud
**Profile:** Official A (strict_v01, 157 tests, thinking off, temp=0, timeout=300s)

## Final Leaderboard

| Rank | Model | Score | Wall Time | Mean Latency | Errors |
|------|-------|-------|-----------|-------------|--------|
| 🥇 | **Grok 4.5** (OpenRouter) | **152/157 (96.8%)** | 111.8 min | 42.6s | 0 |
| 🥈 | Kimi K3 (Ollama Cloud, 1T MXFP4) | 140/157 (89.2%) | 48.2 min | 16.0s | 0 |
| 🥉 | Qwen 3.5 397B (Ollama Cloud) | 138/157 (87.9%) | 114.1 min | 41.4s | 0 |
| 4 | DeepSeek V4 Pro (Ollama Cloud) | 128/157 (81.5%) | 41.4 min | 13.7s | 0 |
| 5 | Qwen3.8-Max (OpenRouter) | 125/157 (79.6%) | 100.5 min | 29.0s | 0 |
| 6 | GLM-5.2 (Ollama Cloud) | 121/157 (77.1%) | 52.6 min | 16.2s | 0 |
| 7 | Mistral Large 3 (Ollama Cloud, 675B) | 104/157 (66.2%) | 38.5 min | 8.7s | 0 |
| 8 | Nemotron 3 Ultra (Ollama Cloud) | 103/157 (65.6%) | 101.0 min | 28.1s | 0 |

## Per-Category Breakdown

| Category | Grok 4.5 | Kimi K3 | Qwen 3.5 397B | DeepSeek V4 | Qwen3.8-Max | GLM-5.2 | Mistral L3 | Nemotron 3U |
|----------|----------|---------|--------------|-------------|-------------|---------|------------|-------------|
| math | 27/30 (90%) | 24/30 (80%) | 27/30 (90%) | 26/30 (87%) | 21/30 (70%) | 17/30 (57%) | 11/30 (37%) | 12/30 (40%) |
| coding | 30/30 (100%) | 23/30 (77%) | 19/30 (63%) | 22/30 (73%) | 12/30 (40%) | 14/30 (47%) | 8/30 (27%) | 14/30 (47%) |
| reasoning | 30/30 (100%) | 28/30 (93%) | 26/30 (87%) | 24/30 (80%) | 29/30 (97%) | 28/30 (93%) | 23/30 (77%) | 25/30 (83%) |
| instruction | 30/30 (100%) | 30/30 (100%) | 29/30 (97%) | 25/30 (83%) | 30/30 (100%) | 28/30 (93%) | 28/30 (93%) | 22/30 (73%) |
| prose | 28/30 (93%) | 28/30 (93%) | 30/30 (100%) | 24/30 (80%) | 26/30 (87%) | 27/30 (90%) | 28/30 (93%) | 23/30 (77%) |
| writing | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 5/5 (100%) | 4/5 (80%) | 5/5 (100%) |
| tool_calling | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) | 2/2 (100%) |

## Difficulty Tier

| Tier | Grok 4.5 | Kimi K3 | Qwen 3.5 397B | DeepSeek V4 | Qwen3.8-Max | GLM-5.2 | Mistral L3 | Nemotron 3U |
|------|----------|---------|--------------|-------------|-------------|---------|------------|-------------|
| easy | 100% | 100% | 100% | 90% | 100% | 100% | 100% | 100% |
| medium | 100% | 100% | 100% | 100% | 100% | 100% | 87% | 100% |
| hard | 92% | 88% | 100% | 100% | 84% | 76% | 84% | 80% |
| expert | 92% | 88% | 85% | 80% | 75% | 75% | 55% | 60% |
| frontier | 100% | 85% | 78% | 67% | 70% | 67% | 53% | 45% |

## Failure Patterns

| Type | Grok 4.5 | Kimi K3 | Qwen 3.5 397B | DeepSeek V4 | Qwen3.8-Max | GLM-5.2 | Mistral L3 | Nemotron 3U |
|------|----------|---------|--------------|-------------|-------------|---------|------------|-------------|
| SyntaxError | 0 | 5 | 11 | 6 | 18 | 16 | 18 | 16 |
| Regex mismatch | 5 | 9 | 7 | 10 | 11 | 16 | 26 | 23 |
| Structural | 0 | 1 | 1 | 11 | 3 | 4 | 4 | 15 |
| Other assertion | 0 | 2 | 0 | 2 | 0 | 0 | 3 | 0 |

## Key Findings

1. **Grok 4.5 is the definitive cloud model.** 96.8% across 157 tests, zero SyntaxErrors, 100% at frontier difficulty. No challenger has come within 7 points across two days of testing.

2. **Kimi K3 (#2, 89.2%) is the best value model.** 2.3× faster than Grok at only 7.6 points lower. Best non-Grok coding score (77%) with only 5 SyntaxErrors. Unique Unicode math char issue in code (≡, ∩, —) — see Pitfall 40.

3. **Qwen 3.5 397B (#3, 87.9%) is the math/prose specialist.** Ties Grok at math 90%, only model with perfect prose 100%. But coding 63% and slow (114 min) limit general utility. Notable: 100% at hard difficulty — no model does better at that tier.

4. **DeepSeek V4 Pro (#4, 81.5%) is the speed champion.** Fastest wall time (41.4 min) among 80%+ scorers. Strong math (87%) and coding (73%), but weak instruction (83%) and prose (80%).

5. **Reasoning MoE syntax floor is universal.** Every non-Grok model produces SyntaxErrors at hard+ coding: Kimi 5, Qwen 3.5 11, DeepSeek 6, Qwen 3.8 18, GLM 16, Mistral 18, Nemotron 16. Grok's zero is the outlier, not the norm.

6. **Nemotron 3 Ultra is the biggest disappointment.** 65.6% in 101 minutes — slower than Kimi K3 (48 min) while scoring 23.6 points lower. Math 40%, coding 47%, instruction 73%. Not competitive in this field.

7. **Frontier difficulty separates the field.** Grok 100% → Kimi 85% → Qwen 3.8 70% → Qwen 3.5 78% → DeepSeek 67% → GLM 67% → Mistral 53% → Nemotron 45%. The hardest tests are where model quality matters most.

## Model Identifiers

| Model | Provider | Served Name | Params | Quant | Context |
|-------|----------|-------------|--------|-------|---------|
| Grok 4.5 | OpenRouter | `x-ai/grok-4.5` | — | — | — |
| Kimi K3 | Ollama Cloud | `kimi-k3:cloud` | 1T | MXFP4 | 1M |
| Qwen 3.5 397B | Ollama Cloud | `qwen3.5:397b` | 397B | — | — |
| DeepSeek V4 Pro | Ollama Cloud | `deepseek-v4-pro:cloud` | — | — | — |
| Qwen3.8-Max | OpenRouter | `qwen/qwen3.8-max` | — | — | — |
| GLM-5.2 | Ollama Cloud | `glm-5.2:cloud` | — | — | — |
| Mistral Large 3 | Ollama Cloud | `mistral-large-3:675b` | 675B | — | — |
| Nemotron 3 Ultra | Ollama Cloud | `nemotron-3-ultra:cloud` | — | — | — |

## Result Files

- `results/stage1_showdown-grok45-strict-v01_20260810_102512.json` (Aug 10)
- `results/stage1_showdown-qwen38-max-strict-v01_20260810_102511.json` (Aug 10)
- `results/stage1_showdown-glm52-strict-v01_20260810_123329.json` (Aug 10)
- `results/stage1_sweep2-kimi-k3-strict-v01_20260811_050129.json` (Aug 11)
- `results/stage1_sweep2-qwen35-397b-strict-v01_20260811_045942.json` (Aug 11)
- `results/stage1_sweep2-deepseek-v4-pro-strict-v01_20260811_045944.json` (Aug 11)
- `results/stage1_sweep2-mistral-large-3-strict-v01_20260811_045943.json` (Aug 11)
- `results/stage1_sweep2-nemotron-3-ultra-strict-v01_20260811_045945.json` (Aug 11)

## Conclusion

Eight cloud models benchmarked across two days. Grok 4.5 is THE model — the only one above 90%, the only one with zero coding SyntaxErrors, the only one with 100% at frontier difficulty. The gap is real and consistent across every category except writing/tool_calling (where all models hit 100%).

Recommended cloud model hierarchy for SMF Works:
1. **Grok 4.5** — primary (correctness-critical agent work, coding, math)
2. **Kimi K3** — fast secondary (89.2% at 2.3× speed, good for non-critical paths)
3. **DeepSeek V4 Pro** — budget option (81.5% at 41 min, fastest wall time for >80%)
4. Everything else — fallback/specialty only