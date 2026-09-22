# Claude Opus 5.5 Official A — 2026-09-22

- Model: `anthropic/claude-opus-5.5` (OpenRouter)
- Tag: `cal-claude-opus-55-or-strict-v01`
- Profile: `strict_v01` · thinking **off** · `serve_recipe_id=OpenRouter-cloud`
- JSON: `results/stage1_cal-claude-opus-55-or-strict-v01_20260922_215554.json`
- Score: **151/157 (96.2%)** · fail=6 · error=0 · unique ids=157
- Wall: 1561.8 s · cost delta `/v1/key` $3.63638 (374.747214738 → 378.383594738)

## By category

| Suite | Pass | Fail | Err |
|-------|------|------|-----|
| reasoning | 30 | 0 | 0 |
| instruction | 30 | 0 | 0 |
| writing | 5 | 0 | 0 |
| tool_calling | 2 | 0 | 0 |
| prose | 29 | 1 | 0 |
| coding | 28 | 2 | 0 |
| math | 27 | 3 | 0 |

## Fails

| test_id | detail | tokens | elapsed s |
|---------|--------|--------|-----------|
| v3.math.expert.06 | Regex `\b-0.01384\b` | 793 | 7.22 |
| v3.math.expert.07 | Regex `\b-9.417\b` | 1114 | 9.38 |
| v3.math.frontier.08 | Regex `\b15.7987\b` | 1331 | 12.18 |
| v3.coding.expert.05 | SyntaxError: invalid syntax | 753 | 6.13 |
| v3.coding.frontier.01 | SyntaxError: invalid character `≤` (U+2264) | 1388 | 10.61 |
| v3.prose.hard.04 | Regex `[eE]` | 1434 | 13.70 |

Smoke: `2+2` default and `enable_thinking=false` both landed content with `reasoning_tokens=0`. Did not add `claude`/`opus` to `reasoning_indicators`.
