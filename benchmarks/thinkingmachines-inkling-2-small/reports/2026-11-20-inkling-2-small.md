# Scorecard: Thinking Machines Inkling 2 Small (thinkingmachines/inkling-2-small), 2026-11-20

- Hardware / endpoint / engine version / quant: OpenRouter cloud (provider Nebius), no local
  quant. 594B total MoE, 17B active per vendor card. 1M ctx, max_completion 943,718.
- Params (temperature, top_p, max_tokens, reasoning effort):
  - Cold Iron (Official A, thinking-off analogue): temperature 0.0 (runner default),
    max_tokens 1024 (inkling NOT in reasoning_indicators), reasoning={"effort":"minimal"} —
    lowest listed effort. effort=none and enabled=false are HTTP 400 (reasoning mandatory).
  - One-shot: temperature 0.7 (script default, no vendor default in catalog),
    max_tokens 943718, reasoning effort unset → catalog default high.
- Seed policy: not sent (endpoint supports seed; suite default does not send it).
- Suite, prompt-set sha256, credits: SMF Inference Standard v0.1.1, strict_v01 (157),
  SMF Inference Standard authors, runner ~/workspace/smf-bench @ 5d9ddf6. One-shot brief:
  81-byte series prompt (byte-identical to ox-alpha series, cmp verified).
- Runs (n>=3): n=1 — 147/157 (93.6%), 0 errors, wall 600.1 s. Single run; treat as a
  point estimate, not a settled score. Prior single-run board entries: astra 95.5, sol 94.9,
  hydrogen 96.2, carbon 93.6.
- Comparison model(s) and their mean/range: inkling 93.6 (n=1) sits even with gemini-4-carbon
  (93.6) and between muse-wonder (94.3) and fable-5.2 mean 90.9 (n=3). No overlap verdict
  possible at n=1.
- Variance notes / overlap verdict: single run — no verdict. Board rank is provisional.
- Cost (from provider billing/usage records, not list price): $0.1828 summed per-row
  usage.cost for the 157. Key delta check: 448.9145 → 449.1167 (+0.2023 including the
  one-shot $0.0124 and probes).
- Latency: mean 3.8 s per item, max 28.1 s (fast for a 594B MoE). One-shot: 19.3 s wall
  for 12,470 tokens.
- Notable failures (item ids): v3.math.expert.06/07/08, v3.math.frontier.11 (regex
  exact-number misses), v3.coding.expert.07, v3.coding.frontier.01, v3.coding.frontier.05
  (assertion + one unterminated string literal), v3.reasoning.frontier.07,
  v3.prose.expert.03, v3.prose.frontier.11 (line-count).
- BLOCKED tasks: none.
- Judge (named, not under test) and blinding: objective regex/evaluator checks only; no
  blind judging needed for this suite.
- Recommendation: Inkling 2 Small lands in the top tier on its first thinking-off run —
  93.6 with the floor-effort analogue (minimal, since the model refuses to turn reasoning
  off). The striking part is speed: 3.8 s mean per item and a 12k-token one-shot page in
  19 s is far quicker than anything else at this score. n=1, so if we want it ranked above
  carbon we should take two more runs before it goes on any locked board. Worth the runs.
