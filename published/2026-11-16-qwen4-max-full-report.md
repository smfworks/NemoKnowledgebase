# Qwen4 Max, the full report: one sentence, 471 tests, and a family wobble confirmed

- **Date:** 2026-11-16
- **Model:** qwen/qwen4-max (canonical 20261115), OpenRouter, provider Alibaba
- **Suite:** Comprehensive session report — one-shot + 3x Cold Iron (`strict_v01`, effort=none TRUE off) n=3 aggregate
- **Result:** One-shot AURORA 46,506 bytes clean ($0.098). Cold Iron mean 127/157 (80.9%), range 123-132, zero errors in 471 requests, ~$1.06. 19% of items flip at least once; math the weak leg (15-19/30 every run) and the entire range below the predecessor's single-run 87.9%. Session cost $1.16, reconciled to the key delta.
- **Raw:** [benchmarks/qwen4-max](https://github.com/smfworks/NemoKnowledgebase/tree/main/benchmarks/qwen4-max)

## Published line

> The whole-day verdict: a mechanically perfect, mid-board generalist whose own family's math score is the strongest argument against it. Coding 89%, instruction 91%, tools 100% on the means; math 55.6%; video input is the party trick nothing else on the board has.

This is the aggregate write-up; the per-test rows above carry the individual runs. No new runs were performed for this post.
