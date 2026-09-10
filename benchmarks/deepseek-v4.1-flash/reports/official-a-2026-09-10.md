# DeepSeek V4.1 Flash (OpenRouter) — Official A 2026-09-10

- Slug: `deepseek/deepseek-v4.1-flash`
- Tag: `cal-dsv41-flash-or-strict-v01`
- Profile: `strict_v01` / thinking **off** (`reasoning.effort=none`)
- Serve recipe: `OpenRouter-cloud`
- Result JSON: `results/stage1_cal-dsv41-flash-or-strict-v01_20260910_102438.json`
- HF: `deepseek-ai/DeepSeek-V4.1-Flash` (MIT)

## Summary

| | |
|--|--|
| Total | **127/157 (80.9%)** |
| Fail | 30 |
| Error | 0 |
| Wall | 559.0 s (9.3 min) |
| Cost | $0.0689 (OpenRouter `/v1/key` 372.398586 → 372.467452) |
| Mean / median latency | 3.54 s / 2.27 s (all); pass 2.95 s / 2.07 s |
| Tokens used (sum) | 119,968 |

## By category

| Category | Pass | Fail | Err | Rate |
|----------|------|------|-----|------|
| coding | 23 | 7 | 0 | 76.7% |
| instruction | 28 | 2 | 0 | 93.3% |
| math | 16 | 14 | 0 | 53.3% |
| prose | 27 | 3 | 0 | 90.0% |
| reasoning | 27 | 3 | 0 | 90.0% |
| tool_calling | 2 | 0 | 0 | 100% |
| writing | 4 | 1 | 0 | 80.0% |

## By difficulty

| Tier | Pass | Total | Rate |
|------|------|-------|------|
| Easy | 10 | 10 | 100% |
| Medium | 14 | 15 | 93.3% |
| Hard | 21 | 25 | 84.0% |
| Expert | 32 | 40 | 80.0% |
| Frontier | 44 | 60 | 73.3% |
| Other (writing + tools) | 6 | 7 | 85.7% |

## Failure mix

- 0 HTTP errors, 0 timeouts
- 6 SyntaxErrors (2 unterminated string, 1 invalid syntax, 2 `²` U+00B2, 1 `’` U+2019)
- 1 coding AssertionError
- 18 regex misses (14 math, 3 reasoning, 1 prose)
- 2 instruction token transforms (narrated steps instead of the token)
- 2 prose line-count
- 1 writing keyword miss (`writing_creative` 0/5)

## Smoke (Official A analogue)

`What is 2+2?`, temp 0, `max_tokens=64`:

- `reasoning.effort=none` and `enabled=false`: content lands, **0** reasoning tokens
- Default and `enable_thinking=false`: content `'4'`, **32–37** reasoning tokens
- Do **not** add `v4.1` to `reasoning_indicators` (`deepseek` already matches → `max_tokens=4096`)

## Architecture (cited)

- Tech report: 552B backbone, 196B Engram, CED 20+20 layers, 8B active prefill / 16B decode, 1M context, 45T pretrain, 890 B/token global KV
- `config.json`: `DeepseekV41ForCausalLM`, hidden 5120, 40 layers, 384 routed + 1 shared, top-6, `max_position_embeddings=1048576`, vision 32-layer DeepSeek-ViT
- OpenRouter: 1,048,576 context, 384,000 max completion, $0.30/$1.20 list with off-peak $0.15/$0.60, text+image → text
