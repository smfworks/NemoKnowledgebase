# Scorecard: Thinking Machines Inkling 2 Mini (thinkingmachines/inkling-2-mini), 2026-11-20

- Hardware / endpoint / engine version / quant: OpenRouter cloud (provider PrimeIntellect),
  no local quant. 26.4B total / 3.4B active MoE (looped: middle layers ×3, shared weights),
  per vendor card. 1M ctx, max_completion 65,536.
- Params (temperature, top_p, max_tokens, reasoning effort):
  - Cold Iron (Official A, thinking off): temperature 0.0 (runner default), max_tokens 1024
    (mini NOT in reasoning_indicators), reasoning={"effort":"none"} — a TRUE off, verified
    0 reasoning tokens across all 157 items. Unlike Inkling 2 Small (mandatory), mini accepts
    effort=none cleanly.
  - One-shot: temperature 0.7 (script default), max_tokens 65536, reasoning effort unset →
    catalog default high.
- Seed policy: not sent (endpoint supports seed; suite default does not send it).
- Suite, prompt-set sha256, credits: SMF Inference Standard v0.1.1, strict_v01 (157),
  SMF Inference Standard authors, runner ~/workspace/smf-bench (local mods, inkling branch).
  One-shot brief: 81-byte series prompt, cmp-identical to ox-alpha series.
- Runs (n>=3): n=1 — 90/157 (57.3%), 0 errors, wall 3905.2 s (65 min), 0 total reasoning
  tokens. Single run; point estimate, not a settled score.
- Comparison: inkling-2-small (same family/day) 147/157 (93.6) under a minimal-effort
  analogue. The 36-point family gap is mostly math (6/30 vs 26/30) and coding (13/30 vs
  27/30). Board context: ripple-65b 59.2, qwen3-14b 61.8 — mini lands in that tier.
- Variance notes / overlap verdict: single run — no verdict.
- Cost (from provider billing/usage records): $0.0918 summed per-row usage.cost for the 157.
  Key delta: 449.1167 → 449.2115 (+0.0948 incl. one-shot $0.0028 + probes).
- Latency: mean 24.9 s per item, max 118.0 s. Slow for its size on this endpoint — the
  3.4B-active looped design does not translate to fast cloud serving here. One-shot:
  62.2 s wall for 7,708 tokens (still 3× faster than Small's 594B on the same brief
  would suggest… actually Small did it in 19.3 s; mini is the slower of the two today).
- Notable failures: entire math tier above medium (all hard/expert/frontier except easy),
  coding 17/30 including SyntaxError/timeout asserts, reasoning frontier items,
  several prose line-count items. Writing 3/5 and instruction 25/30 are the relative strengths.
- BLOCKED tasks: none.
- Judge: objective regex/evaluator checks only.
- Recommendation: skip it for anything scored. The true-off arm is real (0 reasoning tokens
  everywhere) and the price is tiny ($0.09 per suite), but 57.3% puts it near the bottom of
  the 2026-11 board, and it is slow per item for the class. Its one-shot page is genuinely
  nice for the size — that's the story, not the Cold Iron number. If Michael wants a laptop
  -class local recipe story later, the open weights are the interesting part.
