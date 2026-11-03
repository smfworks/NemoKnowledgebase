# Test 2 verdict — does the splice corruption follow length?

**Date:** 2026-11-03 ~00:35 EST
**Design:** three prompts at ascending output length, same serve (`spark-56bc:8888`, `GLM-5.3-Flash-EXL3`), temp 0, thinking off, max_tokens 32768. One run per cell (temp 0 is deterministic per prompt; the point is fault characterization, not comparison).

## Results

| Cell | Prompt | finish | Tokens | Latency | Splice markers | JS syntax | Tag balance | ID refs |
|---|---|---|---|---|---|---|---|---|
| A short | lightbulb toggle | stop | 1,360 | 16.7 s | **0** | PASS | PASS | all resolve |
| B medium | solar system, 8 labeled planets | stop | 2,230 | 31.1 s | **0** | PASS | PASS | all resolve |
| C long | playable piano + record/playback | stop | 6,049 | 83.7 s | **0**¹ | PASS | PASS | all resolve |

¹ One regex hit for `at 50%` is a false positive — it's a legitimate CSS `radial-gradient(ellipse 80% 60% at 50% 0%, …)`.

## Feature delivery

- **A:** bulb + toggle button + click handler — complete. ("MISSING lightbulb" in my first pass was my regex, not the file — it's `.bulb` / "Lightbulb Toggle".)
- **B:** all 8 planets named and labeled, orbits animated.
- **C:** real piano design — per-key `playNote(midi)` with `freqOf`, 5-partial inharmonic piano tone on `createOscillator`, 16 record / 12 playback references. Delivers the ask.

## Verdict

**Clean sweep: 0 splice-corruption markers in all three cells, all JS parses, all DOM ids resolve.** The corruption signature from 2026-11-02 did **not** reproduce at 1.4k, 2.2k, or 6k output tokens.

So the fault is **not a constant** and not length-monotone in a simple way: the corrupted run was 11,845 tokens and byte-identical across two runs; today's clean cells top out at 6k. Best characterization: a rare, deterministic-for-a-given-prompt decode/draft fault that shows up in very long completions (≳10k tokens), possibly prompt-dependent. One more datapoint at ~10k+ would tighten the threshold, but the actionable finding stands either way.

## Recommendation

- **Do not flag the pin.** The serve is healthy for one-shots up to at least ~6k tokens. The 2026-11-02 dog-violin result stands as a real but rare failure — keep it on record with its corrupted `response.html` as the specimen.
- **For long one-shots (≳10k expected tokens), spot-check the output for the splice signature before trusting it** — cheap regex, catches it immediately. That's the workflow I'd adopt for GLM on this serve.
- No serve restart, no config change made or needed.

## Files

- `test2/A_short/`, `test2/B_medium/`, `test2/C_long/` — `response.json`, `raw.txt`, `extracted.html` per cell
- `test2/summary.json`, `test2/verdicts.json` — machine-readable scores
