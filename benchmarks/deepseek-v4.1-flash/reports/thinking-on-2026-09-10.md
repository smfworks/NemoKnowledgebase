# DeepSeek V4.1 Flash (OpenRouter) — thinking-on diagnostic 2026-09-10

Diagnostic arm only. Official A ranking remains thinking-off 127/157 (80.9%).

- Slug: `deepseek/deepseek-v4.1-flash`
- Tag: `cal-dsv41-flash-or-strict-v01-thinking-on`
- Profile: `strict_v01` / thinking **on** (runner default; no `reasoning.effort=none`)
- Serve recipe: `OpenRouter-cloud`
- Result JSON: `results/stage1_cal-dsv41-flash-or-strict-v01-thinking-on_20260910_112819.json`

## Summary

| | Thinking off (Official A) | Thinking on (diagnostic) |
|--|---------------------------|--------------------------|
| Total | **127/157 (80.9%)** | **130/157 (82.8%)** |
| Fail | 30 | 27 |
| Error | 0 | 0 |
| Wall | 559.0 s (9.3 min) | 2699.0 s (45.0 min) |
| Cost | $0.0689 | $0.2482 |
| Mean / median latency | 3.54 s / 2.27 s | 17.17 s / 8.95 s |
| Tokens used (sum) | 119,968 | 341,651 |
| SyntaxErrors | 6 | 14 |

## By category

| Category | Off | On | Delta |
|----------|-----|----|-------|
| coding | 23/30 | 16/30 | −7 |
| instruction | 28/30 | 28/30 | 0 |
| math | 16/30 | 25/30 | +9 |
| prose | 27/30 | 25/30 | −2 |
| reasoning | 27/30 | 29/30 | +2 |
| tool_calling | 2/2 | 2/2 | 0 |
| writing | 4/5 | 5/5 | +1 |

## Delta (off → on)

- Fixed: 16
- Regressed: 13
- Both fail: 14

Math recovery is real. Coding syntax floor got worse (CoT leaking into code). Prose over-generates on structural counts. Not a ranking score.
