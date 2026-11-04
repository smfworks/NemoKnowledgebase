# Hy4 — Cold Iron stability (n=3) and the thinking-on math diagnostic

- **Date:** 2026-11-04
- **Model:** `tencent/hy4` (OpenRouter)
- **Arm:** same as the scored file — `reasoning.effort=none` + `enable_thinking=false`, all rows 0 reasoning tokens
- **Status:** three complete 157 runs (n=3) plus a 30-item math thinking-on diagnostic. Not a rank change; run 1 remains the filed board row.

## Three Cold Iron runs (strict_v01, effort=none, true off)

| Run | File | Total | Math | Wall | Cost |
|---|---|---|---|---|---|
| 1 | `stage1_cal-hy4-or-strict-v01_20261104_113121.json` | 131/157 (83.4%) | 17/30 | 1191.8 s | $0.163867 |
| 2 | `stage1_cal-hy4-or-strict-v01-run2_20261104_121933.json` | 136/157 (86.6%) | 16/30 | 1158.0 s | $0.149482 |
| 3 | `stage1_cal-hy4-or-strict-v01-run3_20261104_123955.json` | 136/157 (86.6%) | 19/30 | 1188.1 s | $0.156259 |

**Mean 134.3, range 131–136 (5.6 points).** Zero errors in all three; reasoning tokens 0 across all 471 rows; no row finished `length` in runs 2–3 except 6/6/… (see per-file finish counts). Coding floor held at 27/29/28 with no SyntaxErrors in any run. Wall time is stable (~1160–1192 s).

## Math thinking-on diagnostic (30 items, default effort high, 8192-token floor)

**23/30 (76.7%)**, 169,518 reasoning tokens, $0.214028, wall 1466.4 s. File: `math-think-on-hy4-20261104_080857.json`, script `scripts/math_thinking_on_hy4.py`.

Math across arms: thinking-off 17/16/19 of 30 (mean 17.3); thinking-on 23/30. **Recovery ≈ +5.7 items.** Thinking on costs ~170k reasoning tokens and a slower wall on the same 30 items.

## Read

- The off-arm range (131–136) overlaps the preview's own 130, so the honest statement is: Hy4 official is **at or slightly above the preview** on Cold Iron, with the speed and price wins being the reliable part.
- Math weakness is partly a thinking-policy effect (+5.7 with thinking on), partly real: 7 items fail even with 8192 tokens and full reasoning.
- Run 1 (131) stays the filed board row; do not re-rank from the later runs without a fresh recompute — and note run 2/3 would put it 11–12th, overlapping Union Alpha/MiniMax.

## Two discarded diagnostic attempts

Two earlier `math-think-on-hy4` JSONs are in `results/quarantine/`: one all-401 (missing api_key passthrough), one evaluator-signature mismatch (`resp.text` passed where the evaluator wants the APIResponse). Both scripts' errors were fixed before the saved run; the quarantined files are kept for the log.
