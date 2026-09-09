# Hy4 preview (OpenRouter) — Official A 2026-09-09

- Slug: `tencent/hy4-preview`
- Tag: `cal-hy4-preview-or-strict-v01`
- Profile: `strict_v01` / thinking **off** (`reasoning.effort=none`)
- Serve recipe: `OpenRouter-cloud`
- Result JSON: `results/stage1_cal-hy4-preview-or-strict-v01_20260909_105540.json`

## Summary

| | |
|--|--|
| Total | **130/157 (82.8%)** |
| Fail | 27 |
| Error | 0 |
| Wall | 1828.5 s (30.5 min) |
| Cost | $0.96 (OpenRouter `/v1/key` delta) |
| Mean / median latency | 11.63 s / 7.69 s |

## By category

| Category | Pass | Fail | Err | Rate |
|----------|------|------|-----|------|
| coding | 27 | 3 | 0 | 90.0% |
| instruction | 28 | 2 | 0 | 93.3% |
| math | 13 | 17 | 0 | 43.3% |
| prose | 29 | 1 | 0 | 96.7% |
| reasoning | 27 | 3 | 0 | 90.0% |
| tool_calling | 2 | 0 | 0 | 100% |
| writing | 4 | 1 | 0 | 80.0% |

## Notes

- Smoke (`reasoning.effort=none`): content `'4'`, `reasoning_tokens=0`, id `gen-1788951246-oHyNpU4NzKB73ypV93He`.
- Default / `effort=low` / `enable_thinking=false` still think (~36–59 tokens). Do not add `hy4` to `reasoning_indicators`.
- Zero SyntaxErrors. Zero HTTP errors.
- HF: `tencent/Hy4-preview`, Apache-2.0, 78 layers, 256 routed experts + 1 shared, top-8.
