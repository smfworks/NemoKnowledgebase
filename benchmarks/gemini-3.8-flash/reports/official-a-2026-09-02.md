# Gemini 3.8 Flash Official A (OpenRouter) — 2026-09-02

- Model: `google/gemini-3.8-flash`
- Profile: `strict_v01` Official A, 157 tests, `--thinking off`
- Tag: `cal-gemini-38-flash-or-strict-v01`
- Recipe: `OpenRouter-cloud`
- Result JSON: `results/stage1_cal-gemini-38-flash-or-strict-v01_20260902_201506.json`
- **145/157 (92.4%)**, fail=12, error=0, timeouts=0
- Wall 1164.1 s (19.4 min)
- Mean latency 7.16 s, median 5.93 s (pass tests)
- OpenRouter credits: usage 545.902 → 546.553 (**+$0.65**); remaining ≈ **$38.45** of $585

## Thinking-off analogue

This endpoint refuses `reasoning.effort=none` / `enabled=false` (HTTP 400: “Reasoning is mandatory”). Smoke: default + `max_tokens=64` → empty `content`, 61 reasoning tokens. `reasoning.effort=low` → `content: '4'`, `reasoning_tokens=0`. Runner sends `{effort: "low"}` when `--thinking off` and the model id contains `gemini`. `is_reasoning_model` stayed false (max_tokens default 1024).

## By category

| Category | Pass |
|----------|------|
| instruction | 30/30 |
| tool_calling | 2/2 |
| reasoning | 29/30 |
| coding | 28/30 |
| prose | 28/30 |
| math | 24/30 |
| writing | 4/5 |
| **TOTAL** | **145/157** |

## Failures (12)

- math.hard.03 `5.461`; expert.06 `-0.01384`; expert.07 `-9.417`; expert.08 `29.924`; frontier.06 `16.5545`; frontier.11 `59.596`
- coding.hard.01 AssertionError; expert.07 IndexError
- reasoning.frontier.07 `292`
- prose.hard.04 `[eE]`; expert.03 `e`
- writing_creative: 2/5 keywords (need 3); missing dialogue/discover/create
