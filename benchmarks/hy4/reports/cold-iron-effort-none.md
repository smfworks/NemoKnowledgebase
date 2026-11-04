# Hy4 (official) — Cold Iron (Official A, strict_v01) — effort=none (true-off analogue)

- **Date:** 2026-11-04
- **Model:** `tencent/hy4` (OpenRouter; catalog name Tencent: Hy4 — official release after the 2026-09 preview)
- **Endpoint:** `https://openrouter.ai/api/v1`, serve_recipe `OpenRouter-cloud`
- **Arm:** `--thinking off` → exact-slug branch sends `reasoning.effort=none` + `enable_thinking=false`. Catalog: reasoning.mandatory=false, efforts high/low/none, default high.
- **True-off status:** all 157 rows recorded reasoning_tokens = 0. This is a true-off file, not an analogue.

## Result

**131/157 (83.4%)** — 26 fails, 0 errors, wall 1191.8 s.

| Category | Score |
|---|---|
| coding | 27/30 (90.0%) |
| instruction | 28/30 (93.3%) |
| math | 17/30 (56.7%) |
| prose | 29/30 (96.7%) |
| reasoning | 26/30 (86.7%) |
| tool_calling | 2/2 (100.0%) |
| writing | 2/5 (40.0%) |

Latency: mean 7.51 s, median 4.17 s, max 36.72 s. Cost: per-row sum $0.163867. `/v1/key` over the whole session (one-shot + smokes + 157): 414.370953588 → 414.550674172, delta $0.179721, which reconciles as one-shot $0.015856 + 157 $0.163867 + $0.000002 of smoke probes.

finish reasons: 147 stop, 2 tool_calls, 8 length. Two of the 8 length rows passed anyway; 6 are budget misses at the 4096 cap (v3.math.frontier.05/06, v3.reasoning.expert.08, v3.reasoning.frontier.06/07/10) — verbose walkthroughs that ate the cap, not proof of inability.

## Delta vs hy4-preview (same arm, 2026-09-09 file)

| Category | hy4 official | hy4 preview |
|---|---|---|
| total | 131/157 (83.4%) | 130/157 (82.8%) |
| math | 17/30 | 13/30 |
| coding | 27/30 | 27/30 |
| reasoning | 26/30 | 27/30 |
| instruction | 28/30 | 28/30 |
| prose | 29/30 | 29/30 |
| writing | 2/5 | 4/5 |
| tool_calling | 2/2 | 2/2 |
| wall | 1191.8 s | 1828.5 s |

Overall +1 point. Math +4, writing −2, reasoning −1, everything else flat. Notably faster and cheaper ($0.417/$1.2505 vs $0.834/$2.501 per 1M).

## Files

- `scripts/run_stage1.py` — runner with the tencent/hy4 exact-slug branch
- `results/stage1_cal-hy4-or-strict-v01_20261104_113121.json` — the scored file
- `results/cal-hy4-or-strict-v01.run.log` — full run log

## Thinking-off probes (2026-11-04, temp 0)

| Probe | Payload | Result |
|---|---|---|
| 2+2, 64 cap | default | finish=length, empty content, 64 reasoning tokens (thinks) |
| 2+2, 64 cap | enable_thinking=false | finish=length, empty content, 64 reasoning tokens (thinks) |
| 2+2, 64 cap | effort=none | visible answer, 0 reasoning tokens |
| bat-and-ball, 1024 | effort=none + enable_thinking=false | full worked answer, stop, 0 reasoning tokens |

`enable_thinking=false` alone is a false clean on this slug — same shape as default. `effort=none` is the off arm; the scored payload is the pair.
