# Space Bunny Alpha — Official A (2026-09-25)

Measured run. Do not name a lab behind the stealth slug.

- Model: `stealth/space-bunny-alpha`
- Tag: `cal-space-bunny-alpha-strict-v01`
- Profile: `strict_v01` / standard v0.1.1
- Thinking: off (`enable_thinking=false` only). Not added to `reasoning_indicators`.
- Recipe: `OpenRouter-cloud`
- Score: **128/157 (81.5%)**, fail 29, error 0
- Wall: 2896.6 s
- Latency: mean 18.43 s, median 11.59 s, max 85.97 s, timeouts 0
- `/v1/key` usage: 379.819363028 before and after (delta 0). Card price $0/$0.
- JSON: `workspace/smf-bench/results/stage1_cal-space-bunny-alpha-strict-v01_20260925_120134.json`

Same-path neighbors (also not in `reasoning_indicators`):

- Union Alpha `stage1_cal-union-alpha-strict-v01_20260916_155705.json`: 136/157, wall 16540.5 s
- MiMo-V2.6-Pro `stage1_cal-mimo-v26-pro-strict-v01_20260924_191609.json`: 128/157, wall 2536.6 s

Ox Alpha best thinking-off file is 129/157 (`stage1_cal-ox-alpha-strict-v01-20260824_20260824_155541.json`) but that slug is in `reasoning_indicators` (max_tokens 4096). Not the same request shape.

Identity probe (max_tokens 1024, thinking off): "My model name, maker, and knowledge cutoff are all undisclosed."
