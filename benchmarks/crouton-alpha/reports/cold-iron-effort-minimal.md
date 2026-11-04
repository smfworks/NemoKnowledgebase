# Crouton Alpha — Cold Iron (Official A, strict_v01) — effort=minimal analogue

- **Date:** 2026-11-03
- **Model:** `stealth/crouton-alpha` (OpenRouter; catalog name Crouton Alpha; identity probe: "My public deployment name is Crouton Alpha. I can't verify the underlying model name or who made it... undisclosed.")
- **Endpoint:** `https://openrouter.ai/api/v1`, serve_recipe `OpenRouter-cloud`
- **Arm:** `--thinking off` with the exact-slug branch sending `reasoning.effort=minimal` (catalog: reasoning.mandatory=true, efforts max/xhigh/high/medium/low/minimal, no `none`, default max). `enable_thinking=false` popped (ignored).
- **Analogue status:** 26/157 rows recorded reasoning_tokens > 0 (sum 950). This is the lowest-allowed effort, not true thinking-off.

## Result

**140/157 (89.2%)** — 17 fails, 0 errors, wall 371.7 s.

| Category | Score |
|---|---|
| coding | 30/30 (100.0%) |
| instruction | 29/30 (96.7%) |
| math | 19/30 (63.3%) |
| prose | 28/30 (93.3%) |
| reasoning | 29/30 (96.7%) |
| tool_calling | 2/2 (100.0%) |
| writing | 3/5 (60.0%) |

Latency: mean 2.35 s, median 2.12 s, max 8.47 s. Cost $0.00 (catalog 0/0; per-row sum 0; /v1/key unchanged 414.370953588 before/after).

Rank: 10 of 26 on the OpenRouter thinking-off board (olympic, recomputed 2026-11-03). All 157 rows finish stop or tool_calls; no length cuts.

## Files

- `scripts/run_stage1.py` — runner with the crouton-alpha exact-slug branch
- `results/stage1_cal-crouton-alpha-or-strict-v01_20261104_010101.json` — the scored file
- `results/cal-crouton-alpha-or-strict-v01.run.log` — full run log

## Thinking-off analogue probes (2026-11-03, temp 0)

| Probe | Payload | Result |
|---|---|---|
| 2+2, max_tokens 64 | default | finish=length, empty content, 0 reasoning tokens (hidden think ate the cap) |
| 2+2, max_tokens 64 | enable_thinking=false | finish=length, empty content, 0 reasoning tokens (same) |
| 2+2, max_tokens 64 | effort=minimal | content "4", stop, 0 reasoning tokens |
| 2+2, max_tokens 1024 | default | content "4", stop, 0 reasoning tokens |
| 2+2, max_tokens 1024 | enable_thinking=false | content "4", stop, 0 reasoning tokens |
| bat-and-ball, 1024 | effort=minimal | $0.05, 0 reasoning tokens |
| bat-and-ball, 1024 | enable_thinking=false | $0.05, 0 reasoning tokens |

The 64-cap behavior is the discriminator: default and the flag burn hidden reasoning until the cap; minimal lets the visible answer land inside 64 tokens. But on the 157, minimal still burned reasoning on 26 harder rows — so the file is an analogue and the post labels it as such.
