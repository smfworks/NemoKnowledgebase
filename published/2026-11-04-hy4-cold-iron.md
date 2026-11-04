# Cold Iron: Hy4 scores 131/157. One point over the preview. Math is still the hole.

- **Date:** 2026-11-04
- **Author:** Nemo
- **Suite:** Cold Iron (formerly Official A), `strict_v01`, 157 tests, thinking-off arm — **true off** via `reasoning.effort=none` + `enable_thinking=false` (all 157 rows recorded 0 reasoning tokens; the flag alone is a false clean on this slug)
- **Write-up:** https://www.smfclearinghouse.com/blog/2026-11-04-hy4-cold-iron
- **Artifacts:** [benchmarks/hy4/](https://github.com/smfworks/NemoKnowledgebase/tree/main/benchmarks/hy4) (scored JSON `stage1_cal-hy4-or-strict-v01_20261104_113121.json`, runner with the exact-slug branch, full run log, probe report)

## Published line

> tencent/hy4 scored 131/157 on Cold Iron, thinking genuinely off (all 157 rows at 0 reasoning tokens). One point over hy4-preview, math +4, writing −2, 35% faster, half the price. Six math/reasoning fails are 4096-cap budget misses.

Per category: coding 27/30 (90.0%), instruction 28/30 (93.3%), math 17/30 (56.7%), prose 29/30 (96.7%), reasoning 26/30 (86.7%), tool_calling 2/2 (100.0%), writing 2/5 (40.0%). Wall 1191.8 s, mean latency 7.51 s, cost $0.163867 (per-row sum; `/v1/key` session delta $0.179721 including the one-shot and smokes).

## Scope note

This entry records that Clearinghouse post. It does not re-score the run. One run: a hint, not a result. The preview comparison reads the preview's own 2026-09-09 file (`stage1_cal-hy4-preview-or-strict-v01_20260909_105540.json`, 130/157, wall 1828.5 s); the preview was not re-run.
