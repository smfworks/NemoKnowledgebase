# Union Alpha (OpenRouter stealth) intake — 2026-09-16

Class of work: mystery/stealth cloud model → Official A. Card page: https://openrouter.ai/stealth/union-alpha

## Identity (API, not rumor)

| Field | Value |
|---|---|
| id | `stealth/union-alpha` |
| Released | 2026-09-16 (OpenRouter created 14:42:03Z) |
| Context / max out | 262,144 / 131,072 |
| Pricing | prompt=0, completion=0 |
| Reasoning | **not** in `supported_parameters`. Smoke: content lands, `reasoning_tokens=0` |
| Card modalities | text+image → text |
| Tools | `tools`, `tool_choice`, `response_format` (JSON object, no schema enforce) |
| Tokenizer / HF id | `Other` / null |
| Provider | single: `Stealth`. Prompts may be retained, **not used for training** (Stealth Model Terms) |

Manifest: `models/union-alpha-or.yaml`. Official A uses **text-only** capabilities (apples-to-apples vs Grok/Kimi/GLM). Do not gate Official A on vision.

**Do NOT add `union-alpha` or `stealth` to `reasoning_indicators`.** Default `max_tokens=1024` is correct.

## Smoke (measured)

- `2+2` at `max_tokens=64`, temp 0: `content='4'`, empty `reasoning`, `reasoning_tokens=0`, 110.6s. **Not** the empty-content trap.
- Identity: “Union Alpha”, maker currently anonymous, stealth/preview, no knowledge cutoff claimed. No GPT/Claude/Gemini leak.
- Tools: native `get_weather(city=Boston, unit=celsius)`, `finish_reason=tool_calls`, 7.1s.

## Official A launch hygiene

1. `hf-gate.json` absent — log must show `hf_gate: not found`.
2. `export SMF_SERVE_RECIPE_ID=OpenRouter-cloud`
3. Tag `cal-union-alpha-strict-v01`, `strict_v01`, `--thinking off`, `--timeout 300`.
4. Snapshot `/v1/key` before/after. Pre-launch usage: 372.815761538 (daily 0).
5. First live test: `v3.math.easy.01` PASS 113.0s (regex 15072).

Do not write a leaderboard % until `summary.total == 157` and `error == 0` on the clean tag.
