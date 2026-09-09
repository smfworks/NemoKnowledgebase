# GPT-6 Astra Pro (OpenRouter batch) — Official A 2026-09-09

- Slug: `openai/gpt-6-astra-pro:batch`
- Tag: `cal-gpt6-astra-pro-batch-strict-v01`
- Profile: `strict_v01` / thinking **off analogue** (`reasoning.effort=low`; disable is batch-validation fail)
- Serve recipe: `OpenRouter-cloud-batch`
- Transport: OpenRouter Batch API `POST /api/beta/batches` (sync `/v1/chat/completions` 404s)
- Result JSON: `results/stage1_cal-gpt6-astra-pro-batch-strict-v01_20260909_171401.json`
- Batch id: `batch-1788974042-od28ZBVgTEc06GVIomC7`

## Summary

| | |
|--|--|
| Total | **153/157 (97.5%)** |
| Fail | 4 |
| Error | 0 |
| Poller wall | 283.9 s (4.7 min) |
| Batch `created_at`→`finalized_at` | 273 s |
| Cost | $4.10492 (usage object; `/v1/key` delta $4.10492) |
| Tokens | 383,704 prompt + 87,456 completion = 471,160 |

## By category

| Category | Pass | Fail | Err | Rate |
|----------|------|------|-----|------|
| coding | 30 | 0 | 0 | 100% |
| instruction | 30 | 0 | 0 | 100% |
| math | 28 | 2 | 0 | 93.3% |
| prose | 30 | 0 | 0 | 100% |
| reasoning | 30 | 0 | 0 | 100% |
| tool_calling | 2 | 0 | 0 | 100% |
| writing | 3 | 2 | 0 | 60.0% |

## Notes

- Sync chat 404: batch-only. Smoke disable (`effort=none`) fails whole-batch validation.
- Official A analogue: `effort=low`. Smoke 2+2: content `'4'`, `reasoning_tokens=0` for low/minimal/default.
- Do not add `astra`/`gpt-6` to `reasoning_indicators`.
- Temperature omitted (not in `supported_parameters`).
- Same two math cells Grok 4.6 fails (`expert.06` `-0.01384`, `expert.07` `-9.417`).
- Same-day Elsewhere one-shot is a different artifact.
