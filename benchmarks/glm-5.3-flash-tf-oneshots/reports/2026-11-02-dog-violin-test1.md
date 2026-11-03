# Test record — GLM-5.3-Flash one-shot, dog/violin/light-switch/sound

**Date:** 2026-11-02 ~22:12–22:20 EST
**Endpoint:** http://spark-56bc:8888/v1 (TensorFold TP=2, both Sparks) — `/v1/models` id `GLM-5.3-Flash-EXL3`, `/health` ok, idle
**Prompt (verbatim):** "Create a one shot of a dog playing a violin with sound, on stage with a working light switch and audio"
**Params:** temperature 0, thinking off (`chat_template_kwargs.enable_thinking: false`), reasoning_tokens 0.

## Runs

| # | max_tokens | finish | completion | verdict |
|---|-----------|--------|------------|---------|
| 1 | 4096 | `length` | 4096 tokens, truncated mid-`<div>` | unusable alone — cap too small for a full one-shot page |
| 2 | 32768 | `stop` | 11,845 tokens / 41.7 KB | complete document, but corrupted |
| 3 | 32768 | `stop` | 11,845 tokens / 41.7 KB | byte-identical to run 2 (temp 0 → deterministic) — same corruption |

## Check results (run 2, `response.html`)

| Check | Result |
|---|---|
| Well-formed HTML (tag balance) | FAIL — ~20+ malformed regions |
| Dog on stage | PASS (CSS divs: head, ears, tail, bow arm animation) |
| Violin | PASS (body, neck, scroll, strings, animated bow) |
| Sound (Web Audio) | PRESENT but BROKEN — `createOsynth: cillator()` split mid-token (line 669); vibrato LFO code otherwise plausible |
| Light switch UI + handler | PRESENT but BROKEN — handler queries `getElementById('light switch')` (space, line 773); id is `lightSwitch`. Click handler would throw null TypeError |
| Melody data | CORRUPTED — `880, 0. bar: 0.5` (line 716); `[783. good: 0.5]` (line 719) — would throw SyntaxError on parse |
| Stage/curtains/audience | PRESENT (curtains, spotlight, bobbing audience) |

## Corruption signature

Corruption is not random truncation: stray words (`vibrato:`, `chin:`, `good:`, `any:`, `turn:`, `concerto:`, `bar:`) are spliced mid-token and mid-string, inside CSS blocks, HTML tags, and JS string literals alike. 21,724 chars survived of what reads like a clean ~22 KB page. Looks like a decode/sampling fault on the serve (draft-token splice), not a prompt or cap problem — run 2 finished `stop` with the full document structure.

**Known clean runs on this serve exist** (Cold Iron stage1), so this is not a constant. One run = a hint. A verdict on GLM one-shot reliability needs n>=3.

## Verdict

**Raw output does not run** — JS SyntaxError (corrupted melody array, split `createOscillator`) and a null light-switch handler (`getElementById('light switch')` with a space). Both requested features exist in the code but neither works as emitted. This is a **fail for the raw one-shot**, not blocked: the serve answered `stop` both times and the corruption is deterministic (run 3 byte-identical to run 2), so it's reproducible evidence, not a transient.

**Deliverable works after repair.** `response_repaired.html` — 11 surgical fixes, all verified: node --check exit 0, tag balance clean, every DOM id resolves, full audio graph wired (sawtooth+octave+vibrato LFO → lowpass → master → analyser → destination), light switch toggles the stage lights, curtains and audience bob. Open it in any browser.

## Recommendation

Do not score GLM-5.3-Flash one-shots on this serve until the splice corruption is understood — it's a decode/draft fault signature (stray words spliced mid-token), not a prompt or cap problem. If a second independent test shows the same signature, flag it against the TensorFold pin before anyone builds on this serve. Cold Iron stage1 runs on the same boot were clean, so it may be specific to very long single-shot completions (11.8k tokens).

## Files

- `response.json` — full API response (run 2)
- `response_run3.json` / `response_run3_raw.txt` — run 3 (byte-identical content to run 2)
- `response_raw.txt` — run 2 raw content
- `response.html` — run 2 extracted HTML (corrupted, kept for the record)
- `response_repaired.html` — **the deliverable**: 11 surgical fixes, verified clean (node --check exit 0, tag balance OK, zero corruption markers, audio graph + switch wired)
- `truncated_run1.json` — not saved (overwritten); run-1 stats in this record only
