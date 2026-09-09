# Nex-N2.5-Pro (OpenRouter free) — Official A 2026-09-09

- Slug: `nex-agi/nex-n2.5-pro:free`
- Tag: `cal-nex-n25-pro-or-strict-v01`
- Profile: `strict_v01` / thinking **off** (`reasoning.effort=none`)
- Serve recipe: `OpenRouter-cloud`
- Result JSON: `results/stage1_cal-nex-n25-pro-or-strict-v01_20260909_030620.json`

## Summary

| | |
|--|--|
| Total | **81/157 (51.6%)** |
| Fail | 64 |
| Error | 12 (all HTTP 429 on the free slug) |
| Excluding errors | 81/145 (55.9%) |
| Wall | 4715.3 s (78.6 min) |
| Cost | $0 |

## By category

| Category | Pass | Fail | Err | Rate |
|----------|------|------|-----|------|
| coding | 16 | 9 | 5 | 53.3% |
| instruction | 25 | 5 | 0 | 83.3% |
| math | 1 | 27 | 2 | 3.3% |
| prose | 26 | 4 | 0 | 86.7% |
| reasoning | 9 | 16 | 5 | 30.0% |
| tool_calling | 0 | 2 | 0 | 0.0% |
| writing | 4 | 1 | 0 | 80.0% |

## Notes

- Smoke (`reasoning.effort=none`): content `NEX_OK`, `reasoning_tokens=0`, id `gen-1788922973-ScqupbSASQLN2qpkGJna`.
- Non-stream chat completions hang on whitespace keepalives. Official A used SSE (`stream=true`).
- Zero SyntaxErrors in coding. Two “No code in response” at ~300 s.
- Hugging Face repo at intake: README + figures only; no weights.
- Do not add `nex` to `reasoning_indicators`.
