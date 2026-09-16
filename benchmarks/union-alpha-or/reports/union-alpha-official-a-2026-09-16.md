# Union Alpha Official A — 2026-09-16

**Model:** Union Alpha (`stealth/union-alpha`) via OpenRouter
**Protocol:** Official A · `strict_v01` · 157 · `--thinking off`
**Tag:** `cal-union-alpha-strict-v01`
**Ranking file:** `results/stage1_cal-union-alpha-strict-v01_20260916_155705.json`
**serve_recipe_id:** `OpenRouter-cloud`
**standard_version:** v0.1.1
**reasoning_model:** false (do not add `union-alpha` / `stealth` to `reasoning_indicators`)

## Score

**136/157 (86.6%)** · fail=21 · **error=0** · wall **16540.5s (4.59h)** · API cost **$0.00**

Verified: 157 unique test IDs, 0 dupes, `summary.total==157`.

| Category | Pass | Fail | Err | Rate |
|---|---:|---:|---:|---:|
| reasoning | 30 | 0 | 0 | 100.0% |
| tool_calling | 2 | 0 | 0 | 100.0% |
| instruction | 28 | 2 | 0 | 93.3% |
| coding | 26 | 4 | 0 | 86.7% |
| math | 24 | 6 | 0 | 80.0% |
| prose | 24 | 6 | 0 | 80.0% |
| writing | 2 | 3 | 0 | 40.0% |
| **TOTAL** | **136** | **21** | **0** | **86.6%** |

Coding syntax floor: **1/30 SyntaxError** (`v3.coding.frontier.05` unterminated string). Three other coding fails are `No code in response` (expert.02, frontier.02/04) — extraction empty, not a MoE 0% collapse.

## Failure list (21)

- math regex: hard.05, expert.01/06/07, frontier.02/03
- coding: expert.02 / frontier.02 / frontier.04 (no code); frontier.05 (SyntaxError)
- instruction frontier.05/09 (no output to count)
- prose: easy.01 (5 vs 2 lines), hard.04/05, expert.01/03/08
- writing: article / creative / format (keyword threshold)

4 tests sat on the 300s timeout wall.

## Rank context (Official A thinking-off, not mixed-policy)

Sits **below Kimi K3 (89.2%) and Qwen3.8-Flash-Next local (87.3%)**, **above Hy4 preview (82.8%) and Ox Alpha recut (82.2%)**.

Math 80% thinking-off is the standout vs Ox Alpha’s weaker expert/frontier math; writing 40% is the ceiling on this run.

Intake: `references/union-alpha-openrouter-intake-2026-09-16.md`
