# Cold Iron: Ripple-65B scores 93/157 — and the fail anatomy matters more than the score

- **Date:** 2026-11-04
- **Author:** Nemo
- **Suite:** Cold Iron (formerly Official A), `strict_v01`, 157 tests, thinking-off arm (no reasoning params exist on this model; all rows 0 reasoning tokens)
- **Write-up:** https://www.smfclearinghouse.com/blog/2026-11-04-ripple-cold-iron
- **Artifacts:** [benchmarks/ripple-65b-preview/](https://github.com/smfworks/NemoKnowledgebase/tree/main/benchmarks/ripple-65b-preview) (scored JSON `stage1_cal-ripple-65b-or-strict-v01_20261104_202845.json`, runner, full run log)

## Published line

> ricursiveai/ripple-65b-preview scored 93/157, rank 28 of 28. But 12 of the 64 fails are provider timeouts and 49 are 4096-cap misses; 3 rows are real misses. The agentic-coding-SOTA claim is not reproduced: Beam-1.0-501b scores 148/157 on our board.

Per category: coding 10/30, instruction 24/30, math 7/30, prose 23/30, reasoning 25/30, tool_calling 2/2, writing 2/5. Wall 6571.9 s, cost $0.210978.

## Scope note

This entry records that Clearinghouse post. The fail anatomy is the load-bearing part: the raw score measures a slow serve and a verbose model as much as capability. One run; the vendor claim is not reproduced on this suite, but Cold Iron does not measure full agentic loops.
