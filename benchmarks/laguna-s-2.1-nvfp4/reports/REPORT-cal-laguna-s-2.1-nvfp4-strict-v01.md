# smf-bench Official A — Laguna S 2.1-NVFP4

**Tag:** `cal-laguna-s-2.1-nvfp4-strict-v01`  
**Profile:** `strict_v01` (Official A, 157 tests) · **Thinking:** off  
**Model:** `poolside/Laguna-S-2.1-NVFP4`  
**Endpoint:** `http://spark-56bc:8888/v1`  
**Engine:** vLLM 0.25.1 + FlashInfer + DFlash · util 0.82 · max_model_len 262144  
**Wall time:** 1945.8s (~32.4 min)  
**Results JSON:** `results/stage1_cal-laguna-s-2.1-nvfp4-strict-v01_20260721_203834.json`  
**Log:** `results/cal-laguna-s-2.1-nvfp4-strict-v01.run.log`

## Headline (multi-metric — not overall % alone)

| Metric | Value |
|--------|------:|
| Overall pass | **107/157 (68.2%)** |
| Errors / timeouts | **0 / 0** |
| Coding | **24/30 (80.0%)** |
| Coding syntax-floor fails | **2/30** (SyntaxError) |
| Tool calling | **2/2 (100%)** |
| Instruction | **27/30 (90.0%)** |
| Math | **8/30 (26.7%)** |
| Reasoning tier0 | **20/30 (66.7%)** |
| Prose | **23/30 (76.7%)** |
| Writing | **3/5 (60.0%)** |

## Per-suite

| Suite | Pass | Total | Rate | Fail | Err |
|-------|-----:|------:|-----:|-----:|----:|
| coding | 24 | 30 | 80.0% | 6 | 0 |
| instruction | 27 | 30 | 90.0% | 3 | 0 |
| math | 8 | 30 | 26.7% | 22 | 0 |
| prose | 23 | 30 | 76.7% | 7 | 0 |
| reasoning | 20 | 30 | 66.7% | 10 | 0 |
| tool_calling | 2 | 2 | 100.0% | 0 | 0 |
| writing | 3 | 5 | 60.0% | 2 | 0 |
| **TOTAL** | **107** | **157** | **68.2%** | **50** | **0** |

## Difficulty (where tagged)

| Diff | Pass | Fail | Total | Rate |
|------|-----:|-----:|------:|-----:|
| easy | 10 | 0 | 10 | 100.0% |
| medium | 14 | 1 | 15 | 93.3% |
| hard | 18 | 7 | 25 | 72.0% |
| expert | 26 | 14 | 40 | 65.0% |
| frontier | 34 | 26 | 60 | 56.7% |
| core | 5 | 2 | 7 | 71.4% |

## Coding failure modes

- SyntaxError (syntax floor): 2 — v3.coding.frontier.10, v3.coding.frontier.11
- Assertion / runtime: 4
  - `v3.coding.expert.03`: Assertion failed: AssertionError
  - `v3.coding.frontier.03`: Assertion failed: AssertionError
  - `v3.coding.frontier.06`: Assertion failed: IndexError: list assignment index out of range
  - `v3.coding.frontier.07`: Assertion failed: AssertionError

## Interpretation notes

- **Calibration tag (`cal-`)**, not a D-series rank claim. Official A / thinking-off.
- **Coding is the architecture signal:** 80% unit_test pass with only 2 SyntaxErrors — strong single-shot syntax floor for an 8.5B-active MoE (contrast GPT-OSS-120B / Mixtral historically ~0–10% coding).
- **Math is weak under thinking-off + regex exact match** (26.7%). Many fails are precision/format (e.g. expected `16.913`) rather than hard capability proofs. A thinking-on diagnostic arm would clarify.
- **Tool calling 100%** with `poolside_v1` parser — native tool path works on this serve.
- **Zero error budget burn** — endpoint stable for full 157; no mid-run crash.
- Serve used request `temperature` from suite defaults (often 0.6); server override is 0.7 when clients omit sampling params.
- Do not compare overall % directly to legacy_181 historical runs (181 tests, different mix).

## Reproduce

```bash
cd /home/mikesai1/workspace/smf-bench
python3 -u run_stage1.py \
  --endpoint http://spark-56bc:8888/v1 \
  --model poolside/Laguna-S-2.1-NVFP4 \
  --tag cal-laguna-s-2.1-nvfp4-strict-v01 \
  --core-profile strict_v01 \
  --thinking off \
  --timeout 300
```
