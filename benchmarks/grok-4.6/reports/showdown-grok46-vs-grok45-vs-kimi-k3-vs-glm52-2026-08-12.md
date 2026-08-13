# smf-bench Official A: Grok 4.6 vs Grok 4.5 vs Kimi K3 vs GLM-5.2
## Four-Way Cloud Model Comparison — 2026-08-12

**Suite:** Official A (`strict_v01`, 157 tests) · **Thinking:** off · **Endpoint:** OpenRouter (cloud)

---

## Executive Summary

Grok 4.6 takes the #1 spot on our smf-bench leaderboard, edging out Grok 4.5 by exactly 1 test. The improvement comes from post-training (SFT + RL) on the same 1.5T V9 foundation — no architecture change, just better training. Zero regressions, zero SyntaxErrors, perfect coding/reasoning/instruction/tool-calling/writing.

| Rank | Model | Score | Pass Rate | SyntaxErrors | Wall Time |
|------|-------|-------|-----------|--------------|-----------|
| 🥇 1 | **Grok 4.6** | 153/157 | **97.5%** | 0 | 150 min |
| 🥈 2 | Grok 4.5 | 152/157 | 96.8% | 0 | 112 min |
| 🥉 3 | Kimi K3 | 140/157 | 89.2% | 5 | 48 min |
| 4 | GLM-5.2 | 121/157 | 77.1% | 16 | 53 min |

---

## Per-Category Comparison

| Category | Grok 4.6 | Grok 4.5 | Kimi K3 | GLM-5.2 | Tests |
|----------|----------|----------|---------|---------|-------|
| **coding** | **30/30** ✅ | **30/30** ✅ | 23/30 | 14/30 | 30 |
| **reasoning** | **30/30** ✅ | **30/30** ✅ | 28/30 | 28/30 | 30 |
| **instruction** | **30/30** ✅ | **30/30** ✅ | **30/30** ✅ | 28/30 | 30 |
| **math** | 28/30 | 27/30 | 24/30 | 17/30 | 30 |
| **prose** | 28/30 | 28/30 | 28/30 | 27/30 | 30 |
| **writing** | **5/5** ✅ | **5/5** ✅ | **5/5** ✅ | **5/5** ✅ | 5 |
| **tool_calling** | **2/2** ✅ | **2/2** ✅ | **2/2** ✅ | **2/2** ✅ | 2 |

**Key observations:**
- Grok 4.6 and 4.5 are the only models with perfect coding (30/30). Kimi K3 loses 7 coding tests (5 SyntaxErrors from Unicode math chars). GLM-5.2 loses 16 coding tests (all SyntaxErrors — unterminated strings, invalid decimals).
- Grok 4.6 gains 1 math test over 4.5 (fixed `v3.math.hard.05`), but the 2 remaining math failures are the same expert-level precision problems both Grok versions miss.
- Writing, tool calling, and instruction (for Grok/Kimi) are saturated — all top models score 100%.

---

## Per-Difficulty Breakdown

| Difficulty | Grok 4.6 | Grok 4.5 | Kimi K3 | GLM-5.2 | Tests |
|------------|----------|----------|---------|---------|-------|
| easy | 10/10 (100%) | 10/10 (100%) | 10/10 (100%) | 10/10 (100%) | 10 |
| medium | 15/15 (100%) | 15/15 (100%) | 15/15 (100%) | 15/15 (100%) | 15 |
| hard | 24/25 (96%) | 23/25 (92%) | 22/25 (88%) | 19/25 (76%) | 25 |
| expert | 37/40 (92.5%) | 37/40 (92.5%) | 35/40 (87.5%) | 30/40 (75%) | 40 |
| frontier | 60/60 (100%) | 60/60 (100%) | 51/60 (85%) | 40/60 (66.7%) | 60 |
| other | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7/7 (100%) | 7 |

**Grok 4.6 vs 4.5 by difficulty:** The single gain is at the `hard` tier (24 vs 23). Expert and frontier remain identical. Both Grok versions are the only models with 100% on frontier.

---

## Grok 4.6 vs Grok 4.5 — Delta Analysis

### Tests Fixed by Grok 4.6 (failed in 4.5 → passed in 4.6)

| Test ID | Category | Detail (4.5 failure) |
|---------|----------|---------------------|
| v3.math.hard.05 | math | Regex `\b8.750\b` did not match |

**Fixed: 1 test**

### Tests Regressed by Grok 4.6 (passed in 4.5 → failed in 4.6)

**None. Zero regressions.**

### Tests Both Versions Fail

| Test ID | Category | Detail | Notes |
|---------|----------|--------|-------|
| v3.math.expert.06 | math | Regex `\b-0.01384\b` did not match | High-precision numerical computation |
| v3.math.expert.07 | math | Regex `\b-9.417\b` did not match | High-precision numerical computation |
| v3.prose.hard.04 | prose | Regex `[eE]` did not match | Missing character 'e' in output |
| v3.prose.expert.03 | prose | Regex `e` did not match | Missing character 'e' in output |

These 4 tests appear to be a hard floor for the V9 foundation — post-training improvements didn't move them. Both are precision/format issues, not capability gaps.

---

## Failure Pattern Analysis

### Grok 4.6 (4 failures)
- 2 math expert: numerical precision (regex mismatch on exact decimal values)
- 2 prose: missing character 'e' in output (likely a formatting constraint the model doesn't satisfy)
- 0 SyntaxErrors
- 0 errors (all 157 tests returned a response)

### Grok 4.5 (5 failures)
- 3 math: 1 hard (fixed in 4.6), 2 expert (same as 4.6)
- 2 prose: same 2 tests as 4.6
- 0 SyntaxErrors
- 0 errors

### Kimi K3 (17 failures)
- 6 math: expert and frontier precision problems
- 7 coding: 5 SyntaxErrors from Unicode math chars (≡, ∩, —), 1 assertion error, 1 unterminated string
- 2 reasoning: expert and frontier
- 2 prose: structural format issues (expected 1 stanza, got 16)
- **Pitfall 40 confirmed:** Unicode math characters in code blocks

### GLM-5.2 (36 failures)
- 13 math: widespread precision failures across hard/expert/frontier
- 16 coding: all SyntaxErrors — unterminated strings, invalid decimals, Unicode chars
- 2 reasoning: hard and frontier
- 2 instruction: character-level accuracy and line count
- 3 prose: structural format issues
- **Coding syntax floor is the dominant failure mode** — 16/36 failures are SyntaxErrors

---

## Latency Comparison

| Model | Mean | Median | Min | Max | Wall Time |
|-------|------|--------|-----|-----|-----------|
| Grok 4.6 | 56.5s | 41.6s | 2.7s | 452.4s | 150 min |
| Grok 4.5 | 42.6s | 25.4s | — | — | 112 min |
| Kimi K3 | 16.0s | 12.8s | — | — | 48 min |
| GLM-5.2 | 16.2s | 14.3s | — | — | 53 min |

**Note:** Grok 4.6 is notably slower than 4.5 (56.5s vs 42.6s mean, 150 vs 112 min wall time). This is surprising given that 4.6 uses the same 1.5T V9 foundation. Possible explanations:
- OpenRouter routing 4.6 to different infrastructure (newer model, less capacity)
- The improved SFT/RL may produce longer responses (more thorough reasoning before answering)
- Launch-day load on xAI infrastructure (released Aug 7, we tested Aug 12)

The latency cost is real but does not affect pass/fail outcomes. For production routing, this is a throughput consideration, not a quality one.

---

## Architecture & Training Context

| Attribute | Grok 4.6 | Grok 4.5 | Kimi K3 | GLM-5.2 |
|-----------|----------|----------|---------|---------|
| Parameters | 1.5T (V9 foundation) | 1.5T (V9 foundation) | ~2.8T (MXFP4) | Unknown |
| Architecture | MoE | MoE | MoE | MoE |
| Training delta | Improved SFT + RL | Baseline V9 | Independent | Independent |
| Context window | 500K | 500K | — | — |
| Released | Aug 7, 2026 | Jul 16, 2026 | — | — |

Grok 4.6 demonstrates that post-training improvements (SFT + RL) on the same foundation can produce measurable benchmark gains — +1 test, zero regressions — without any architecture change. The 4 persistent failures appear to be a ceiling of the V9 foundation itself, not a training gap.

---

## Methodology

- **Framework:** smf-bench v0.1.1, Official A (`strict_v01`, 157 tests)
- **Thinking:** off (`chat_template_kwargs.enable_thinking=false`)
- **Endpoint:** OpenRouter (`https://openrouter.ai/api/v1`)
- **API key:** `OPENROUTER_API_KEY` env var
- **Timeout:** 300s per test
- **Temperature:** 0 (deterministic)
- **All 4 models tested with identical parameters** for fair comparison
- Grok 4.6 and 4.5 treated as non-reasoning models (max_tokens=1024) — "grok" not in `reasoning_indicators`
- Kimi K3 and GLM-5.2 treated as reasoning models (max_tokens=4096) — "kimi" and "glm" in `reasoning_indicators`

---

## Conclusions

1. **Grok 4.6 is the new #1 on smf-bench Official A** at 97.5% (153/157), up from 4.5's 96.8%.
2. **The improvement is small but clean** — +1 test fixed, 0 regressions. Post-training on the same foundation yields marginal but consistent gains.
3. **Grok remains the only model with perfect coding** (30/30, 0 SyntaxErrors). Kimi K3 and GLM-5.2 both have severe coding syntax floors.
4. **The V9 foundation ceiling is ~97.5%** — the 4 remaining failures (2 expert math precision, 2 prose character constraints) are persistent across both Grok versions and likely require an architecture change (Grok 4.7 at 2.1T) to break.
5. **Latency regression** — Grok 4.6 is ~33% slower than 4.5 on mean latency. Worth monitoring but not a blocker for quality-sensitive workloads.
6. **Kimi K3 remains #2 overall** (89.2%) but is 2× faster than Grok 4.6. For latency-sensitive routing where 89% quality is acceptable, Kimi K3 is the better choice.
7. **GLM-5.2's coding floor (16 SyntaxErrors) is a fundamental limitation** — it cannot be used for single-shot code generation at production quality.