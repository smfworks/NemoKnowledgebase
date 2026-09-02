# Claude Fable 5.1 Official A (OpenRouter) — 2026-09-02

- Model: `anthropic/claude-fable-5.1`
- Profile: `strict_v01` Official A, 157 tests, `--thinking off`
- Tag: `cal-fable-51-or-strict-v01`
- Recipe: `OpenRouter-cloud`
- Result JSON: `results/stage1_cal-fable-51-or-strict-v01_20260902_184808.json`
- **142/157 (90.4%)**, fail=15, error=0, timeouts=0
- Wall 2100.8 s (35.0 min)
- Mean latency 13.36 s, median 12.27 s
- OpenRouter credits: usage 539.004 → 545.859 (**+$6.85**); remaining ≈ **$39.14** of $585

## By category

| Category | Pass |
|----------|------|
| reasoning | 30/30 |
| tool_calling | 2/2 |
| instruction | 27/30 |
| prose | 27/30 |
| math | 26/30 |
| coding | 26/30 |
| writing | 4/5 |
| **TOTAL** | **142/157** |

## Failures (15)

- math.expert.06 `-0.01384`, expert.07 `-9.417`, expert.08 `29.924`, frontier.11 `59.596`
- coding.hard.04 / frontier.06 / frontier.10: no code (tokens_used=0)
- coding.expert.05: SyntaxError
- instruction.hard.04 / expert.04 / frontier.04: explained instead of emitting the token
- prose.hard.04: missing `[eE]`; frontier.02 / .05: line-count
- writing_creative: 0/5 keywords
