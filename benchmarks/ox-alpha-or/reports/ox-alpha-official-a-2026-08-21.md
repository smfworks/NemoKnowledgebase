# Ox Alpha Official A — 2026-08-21

**Date:** August 21, 2026
**Model:** Ox Alpha (`stealth/ox-alpha`) via OpenRouter
**Profile:** Official A (`strict_v01`, 157 tests, `--thinking off`, timeout 300s)
**Tag:** `cal-ox-alpha-strict-v01`
**Recipe:** `OpenRouter-cloud` (no M10 hf_gate — cloud stealth, architecture undisclosed)
**Result file:** `results/stage1_cal-ox-alpha-strict-v01_20260821_112422.json`
**Wall time:** 5681 s (94.7 min)
**Cost:** $0 (free stealth preview)

This is **measurement / calibration**, not a D-series ranking resume.

## Headline

**127/157 (80.9%), 0 errors, 0 timeouts.** Places **#6** on the 2026-08-12 cloud Official A board, between DeepSeek V4 Pro (81.5%) and Qwen3.8-Max (79.6%). Not a Grok-class model. Strong reasoning/writing/tools; coding syntax floor and expert-math precision are the gaps.

## Overall vs cloud board (Official A, 157)

| Rank | Model | Score | SyntaxErrors | Wall |
|------|-------|-------|--------------|------|
| 1 | Grok 4.6 | 153/157 (97.5%) | 0 | 150 min |
| 2 | Grok 4.5 | 152/157 (96.8%) | 0 | 112 min |
| 3 | Kimi K3 | 140/157 (89.2%) | 5 | 48 min |
| 4 | Qwen3.5-397B | 137/157 (87.9%) | — | — |
| 5 | DeepSeek V4 Pro | 128/157 (81.5%) | — | — |
| **6** | **Ox Alpha** | **127/157 (80.9%)** | **9** | **95 min** |
| 7 | Qwen3.8-Max | 125/157 (79.6%) | — | — |
| 8 | GLM-5.2 | 121/157 (77.1%) | 16 | 53 min |
| 9 | Mistral Large 3 | 104/157 (66.2%) | — | — |

Ranks 1–5 and 7–9 are the 2026-08-12 Official A snapshot (skill / memory). Ox Alpha is the only new run on 2026-08-21.

## Per-category

| Category | Ox Alpha | Grok 4.6 | Kimi K3 | GLM-5.2 | Tests |
|----------|----------|----------|---------|---------|-------|
| coding | **20/30 (66.7%)** | 30/30 | 23/30 | 14/30 | 30 |
| reasoning | **27/30 (90.0%)** | 30/30 | 28/30 | 28/30 | 30 |
| instruction | **26/30 (86.7%)** | 30/30 | 30/30 | 28/30 | 30 |
| math | **20/30 (66.7%)** | 28/30 | 24/30 | 17/30 | 30 |
| prose | **27/30 (90.0%)** | 28/30 | 28/30 | 27/30 | 30 |
| writing | **5/5 (100%)** | 5/5 | 5/5 | 5/5 | 5 |
| tool_calling | **2/2 (100%)** | 2/2 | 2/2 | 2/2 | 2 |

## Per-difficulty

| Tier | Ox Alpha | Grok 4.6 | Kimi K3 | GLM-5.2 | Tests |
|------|----------|----------|---------|---------|-------|
| easy | 10/10 | 10/10 | 10/10 | 10/10 | 10 |
| medium | 15/15 | 15/15 | 15/15 | 15/15 | 15 |
| hard | 24/25 | 24/25 | 22/25 | 19/25 | 25 |
| expert | 30/40 | 37/40 | 35/40 | 30/40 | 40 |
| frontier | 41/60 | 60/60 | 51/60 | 40/60 | 60 |
| other | 7/7 | 7/7 | 7/7 | 7/7 | 7 |

Easy/medium/hard are essentially Grok-clean (the one hard miss is `v3.math.hard.05`, which Grok 4.6 *fixed*). Collapse is **expert + frontier**.

## Latency

| | Mean | Median | P90 | Wall |
|--|------|--------|-----|------|
| Ox Alpha | 36.2 s | 27.7 s | 77.7 s | 94.7 min |

Faster than Grok 4.6 (56.5 s mean / 150 min wall), slower than Kimi/GLM (~16 s). OpenRouter Stealth p50 throughput was ~27–53 tok/s on the model card during this window.

## Failure inventory (30)

### Math (10) — regex precision, not timeouts

| Test | Expected |
|------|----------|
| v3.math.hard.05 | `8.750` (circumscribed R) |
| v3.math.expert.01 | `14.595` (relativity Δt) |
| v3.math.expert.02 | `7.683` (binding energy) |
| v3.math.expert.03 | `135.96` (Hohmann days) |
| v3.math.expert.06 | `-0.01384` (**V9 ceiling** — Grok 4.6 also fails) |
| v3.math.expert.07 | `-9.417` (**V9 ceiling** — Grok 4.6 also fails) |
| v3.math.expert.08 | `29.924` |
| v3.math.frontier.02 | `0.978308` |
| v3.math.frontier.10 | `0.7819` |
| v3.math.frontier.11 | `59.596` |

`hard.05` is the test Grok 4.6 uniquely fixed vs 4.5. Ox Alpha still misses it.

### Coding (10) — syntax floor, Kimi-like not GLM-collapse

**9 SyntaxError, 1 AssertionError.** Unicode math/punct in code (Pitfall 40 family):

- `≈` U+2248 (`expert.02`)
- `×` U+00D7 (`expert.07`)
- `→` U+2192 (`frontier.04`)
- `—` U+2014 (`frontier.05`, `frontier.10`)
- unterminated string (`frontier.02`, `.08`, `.12`)
- `'(' was never closed` (`frontier.03`)
- AssertionError (`frontier.07`)

Better than GLM-5.2 (16 SyntaxErrors / 14/30 coding). Worse than Kimi K3 (5 SyntaxErrors / 23/30) and far from Grok (0 / 30/30).

### Reasoning (3)

- `expert.02` boxed name `Fenna`
- `frontier.06` `\b321\b`
- `frontier.07` `\b292\b`

### Instruction (4)

- `expert.01` 6 lines vs 8
- `frontier.04` string transform (`a9gre9dni9ckk13` vs `a9gredni9ckk12`)
- `frontier.06` 7 sentences vs 176 (over-generation)
- `frontier.11` 9 lines vs 94 (over-generation)

### Prose (3) — all frontier over-generation

- `frontier.03` 1 stanza vs 44
- `frontier.04` 1 stanza vs 35
- `frontier.11` 1 line vs 47

Grok’s two V9 prose ceiling fails (`prose.hard.04`, `prose.expert.03`) are **not** in this fail list — Ox Alpha appears to have passed those two. Not a claim that Ox “beats Grok on prose”; overall prose is 27/30 vs Grok 28/30.

## Endpoint / identity (probes, same morning)

OpenRouter card (live `/v1/models`):

- **id** `stealth/ox-alpha`, ctx **1,048,576**, max out **131,072**
- **Free** (`prompt=0`, `completion=0`)
- Architecture: `text+image+video → text`, tokenizer `Other`
- **Reasoning mandatory**, default effort `max`; `supported_efforts`: max/high/low
- Default sampling: **temp 1.0, top_p 0.95**
- Tools + `response_format` + `reasoning` / `include_reasoning` / `reasoning_effort`
- Provider: single **Stealth** endpoint. OpenRouter: prompts/completions **retained, not used for training**
- Released 2026-08-20

Smoke (not Official A):

| Probe | Result |
|-------|--------|
| Identity | Locked: “ox-alpha, undisclosed organization.” No GPT/Claude/Gemini/Grok/GLM/Qwen leak (EN + ZH) |
| Tools | Native OpenAI tool_call `get_weather(Boston, celsius)` |
| JSON | `{"city":"Boston","temp_f":72}` under `response_format=json_object` |
| Vision | **Works** on data-URL PNG (red field / blue circle / yellow bar) and HTTPS PNG (`OXALPHA` on blue). Wikimedia URL fetch 400’d at OpenRouter, not a model miss |
| Video | **Claimed, not served.** `404 No endpoints found that support video URLs` |
| Reasoning effort=low | Bat/ball → `$0.05` (correct) |
| 2+2 @ max_tokens=64 | content=`4`, reasoning in side channel (not content-null) |

Community fingerprinting (X, unconfirmed) points at Zhipu/GLM-5.x. **We did not confirm that.** The model will not self-identify a lab.

## Method notes

- Manifest: `models/ox-alpha-or.yaml` (`served_name: stealth/ox-alpha`). Official A gated **text-only** so scores are apples-to-apples vs Grok/Kimi/GLM.
- `ox-alpha` added to `run_stage1.py` `reasoning_indicators` → `max_tokens=4096`, timeout 300s.
- First launch aborted (SIGTERM 143) after it auto-loaded cwd `hf-gate.json` stamped `qwen3_5_hybrid_gdn`. Relaunch with gate parked. Result JSON has **no** `hf_gate` key.
- `--thinking off` sent; provider still emits a `reasoning` field (mandatory). Answers landed in `content`. Evaluators did not need the content-null fallback on the smoke.
- Official A does **not** exercise vision/video. Those are probe-only.

## Operational take

**Use for:** free long-context coding/agent experiments, tool-calling, writing, vision-in (images). 1M ctx is real on the card.

**Do not use for:** production coding that must stay ASCII-clean; anything that needs Grok-tier math; video (endpoint doesn’t accept video URLs today).

**Vs lab stack:** local Qwen3.8-27B DSpark (`:8888`) is the on-prem serve. Ox Alpha is a **cloud free preview**, not a replacement, and the vendor can pull it without notice.

## Key findings

1. **80.9% Official A** — mid-pack cloud, ~1 pt under DeepSeek V4 Pro, ~3.8 above GLM-5.2, **16.6 pts under Grok 4.6**.
2. **Coding is the tell:** 20/30 with 9 SyntaxErrors and Unicode operators in code — Kimi-like, not Grok-clean, not GLM-broken.
3. **Math 20/30** shares Grok’s two V9 ceiling items (`expert.06`, `expert.07`) and misses eight more, including `hard.05` that 4.6 fixed.
4. **Reasoning 27/30, writing 5/5, tools 2/2** — the marketing (“coding + agentic + production”) is half-true: agentic/tools/writing hold; single-shot coding syntax does not.
5. **Vision yes, video no** on this OpenRouter route. Don’t trust the modality string without a probe.
6. **Identity is sealed.** Treat “GLM stealth” as rumor until a lab claims it or we get a tokenizer/weight fingerprint.
