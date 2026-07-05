# Qwen3.6-35B-A3B-NVFP4 — Full 65-Test Benchmark Report
## Head-to-Head Against Qwen3.6-27B-NVFP4 on DGX Spark

**Date:** 2026-07-05  
**Model:** nvidia/Qwen3.6-35B-A3B-NVFP4 (MoE 35B total / 3B active)  
**Hardware:** NVIDIA DGX Spark (GB10 Grace Blackwell, aarch64, 128 GB unified memory)  
**Engine:** vLLM v0.24.0 with Marlin NVFP4 MoE + FlashInfer + MTP speculative decoding  
**Thinking Mode:** DISABLED (`chat_template_kwargs: {"enable_thinking": false}`)  
**Benchmark Duration:** 208.6 seconds (3.5 minutes)

---

## Executive Summary

The Qwen3.6-35B-A3B-NVFP4 model was run through the **exact same 65-test benchmark suite** used for the 27B model across 8 dimensions. **Both models achieved a perfect 65/65 score.** The decisive difference is performance: the 35B-A3B MoE architecture (3B active parameters per token) delivers **3.9× higher throughput**, **2.7× lower TTFT**, and **1.4× better speculative decoding acceptance** compared to the dense 27B.

| Metric | 35B-A3B-NVFP4 | 27B-NVFP4 | Advantage |
|--------|:------------:|:---------:|:---------:|
| **Total Score** | **65/65 (100%)** | **65/65 (100%)** | Tie |
| Vision (20 tests) | 20/20 | 20/20 | Tie |
| Video (17 tests) | 17/17 | 17/17 | Tie |
| Reasoning (8 tests) | 8/8 | 8/8 | Tie |
| Tool Calling (2 tests) | 2/2 | 2/2 | Tie |
| Concurrency (1-8 req) | 100% success | 100% success | Tie |
| Context Scaling | 113,804 tokens | 113,804 tokens | Tie |
| Peak Throughput | **92.8 tok/s** | 23.6 tok/s | **3.9× faster** |
| Steady-State Throughput | **79.1 tok/s** | 23.0 tok/s | **3.4× faster** |
| TTFT (short prompt) | **98 ms** | 266 ms | **2.7× faster** |
| TTFT (reasoning prompt) | **77 ms** | 234 ms | **3.0× faster** |
| Spec Decode Acceptance | **71.1%** | 50.3% | **1.4× better** |
| Benchmark Duration | **208.6s** | ~420s est. | **~2× faster** |

---

## Dimension-by-Dimension Results

### Dimension 1: Vision/Image Understanding (20 tests) — 20/20 ✅

All 20 vision tests passed with zero errors. Test images were generated locally using PIL/matplotlib (color grid, text image, bar chart, code screenshot, math equation, scene image, number sequence, comparison pair).

| Section | Tests | 35B Result | 35B Tokens | 35B Time |
|---------|:-----:|:----------:|:----------:|:--------:|
| Single Image Understanding | 5 | 5/5 PASS | 1,359 | ~12.7s |
| Multiple Image Comparison | 2 | 2/2 PASS | 159 | ~1.8s |
| OCR / Text Extraction | 3 | 3/3 PASS | 629 | ~7.1s |
| Chart Interpretation | 3 | 3/3 PASS | 397 | ~3.4s |
| Math from Image | 2 | 2/2 PASS | 652 | ~6.1s |
| Code from Image | 2 | 2/2 PASS | 590 | ~5.2s |
| Visual Reasoning | 3 | 3/3 PASS | 858 | ~8.0s |
| **Total** | **20** | **20/20** | **4,644** | **~44.9s** |

**27B comparison:** 20/20, 4,390 tokens, 155.6s — the 35B produced 6% more tokens in 3.5× less time.

### Dimension 2: Video Understanding (17 tests) — 17/17 ✅

All 17 video tests passed using three locally-generated MP4 test videos (bouncing ball, shapes motion, color cycle). Tests covered description, motion analysis, counting, multi-video comparison, reasoning, and video+text instructions.

| Category | Tests | 35B Result | 35B Tokens |
|----------|:-----:|:----------:|:----------:|
| Video Description | 4 | 4/4 PASS | 298 |
| Motion Analysis | 3 | 3/3 PASS | 511 |
| Counting & Quantitative | 3 | 3/3 PASS | 96 |
| Multi-Video Comparison | 2 | 2/2 PASS | 600 |
| Video Reasoning | 3 | 3/3 PASS | 676 |
| Video + Text Instructions | 2 | 2/2 PASS | 131 |
| **Total** | **17** | **17/17** | **2,412** |

**27B comparison:** 17/17, 2,513 tokens, 100.2s — nearly identical token counts, 35B completed in ~25s.

### Dimension 3: Latency & Throughput (5 sub-tests)

| Max Tokens | Actual Tokens | Wall Time | Throughput |
|:----------:|:-------------:|:---------:|:----------:|
| 64 | 64 | 0.82s | 77.8 tok/s |
| 128 | 128 | 1.62s | 79.1 tok/s |
| 256 | 256 | 3.24s | 78.9 tok/s |
| 512 | 512 | 5.83s | 87.8 tok/s |
| 1,024 | 1,024 | 11.03s | **92.8 tok/s** |

**Peak: 92.8 tok/s | Steady-state: 79.1 tok/s**  
**27B comparison:** Peak 23.6 tok/s, steady 23.0 tok/s → **35B is 3.9× faster**

### Dimension 4: Time To First Token (3 sub-tests)

| Prompt Type | TTFT | Total Time | Content |
|-------------|:----:|:----------:|:-------:|
| Short ("What is 2+2?") | **98 ms** | 0.16s | 9 chars |
| Medium ("Explain CPU…") | **79 ms** | 4.21s | 2,013 chars |
| Long reasoning ("Prove √2 irrational") | **77 ms** | 6.44s | 2,115 chars |

**27B comparison:** TTFT short 266ms, reasoning 234ms → **35B is 2.7-3.0× faster on TTFT**

### Dimension 5: Concurrent Request Handling (4 sub-tests)

| Concurrency | Success | Wall Time | Errors |
|:-----------:|:-------:|:---------:|:------:|
| 1 | 1/1 | 6.57s | 0 |
| 2 | 2/2 | 10.23s | 0 |
| 4 | 4/4 | 14.54s | 0 |
| 8 | 8/8 | 22.63s | 0 |

**100% success rate at all concurrency levels up to 8 parallel requests**

### Dimension 6: Context Length Scaling (6 sub-tests)

| Input Size | Prompt Tokens | Output Tokens | Wall Time | Correct? |
|:----------:|:-------------:|:-------------:|:---------:|:--------:|
| ~100 | 115 | 3 | 0.14s | ✅ |
| ~500 | 471 | 3 | 0.20s | ✅ |
| ~2,000 | 1,804 | 3 | 0.39s | ✅ |
| ~8,000 | 7,139 | 3 | 1.13s | ✅ |
| ~32,000 | 28,471 | 3 | 4.22s | ✅ |
| ~128,000 | **113,804** | 3 | 27.24s | ✅ |

**Full 128K context verified — correctly answered "56" at all context lengths**

### Dimension 7: Reasoning Quality (8 tests) — 8/8 ✅

| Test | Result | Time | Tokens |
|------|:------:|:----:|:------:|
| Math (basic): 17×23 | ✅ PASS | 0.9s | 92 |
| Math (advanced): 3x+7=22 | ✅ PASS | 2.0s | 214 |
| Logic: cats/mammals/pets | ✅ PASS | 9.1s | 868 |
| Coding: reverse linked list | ✅ PASS | 0.8s | 86 |
| Knowledge: capital of Australia | ✅ PASS | 0.8s | 71 |
| Reasoning: train speed | ✅ PASS | 2.0s | 238 |
| Instruction: list 3 fruits | ✅ PASS | 0.2s | 12 |
| World knowledge: Berlin Wall | ✅ PASS | 0.6s | 64 |

**27B comparison:** Also 8/8 — both models have identical reasoning accuracy

### Dimension 8: Tool Calling (2 tests) — 2/2 ✅

| Test | Tool Called | Correct Tool | Correct Args | Time |
|------|:----------:|:------------:|:------------:|:----:|
| Weather query ("Tokyo") | ✅ get_weather | ✅ | ✅ Tokyo | 0.4s |
| Calculator ("45 * 73") | ✅ calculate | ✅ | ✅ 45 * 73 | 0.4s |

**Both tool calls were correctly structured with proper function names and arguments**

### Speculative Decoding (MTP) Metrics

| Metric | Value |
|--------|:-----:|
| Draft requests | 47,127 |
| Draft tokens | 141,381 |
| Accepted tokens | 100,555 |
| **Acceptance rate** | **71.1%** |

**27B comparison:** 50.3% acceptance rate → 35B's MoE architecture achieves 1.4× better spec decode acceptance

---

## Architecture Comparison

| Attribute | 35B-A3B-NVFP4 | 27B-NVFP4 |
|-----------|:-------------:|:---------:|
| Architecture | MoE (Mixture of Experts) | Dense |
| Total Parameters | 35B | 27B |
| Active Parameters/Token | **3B** (8 of 256 experts) | 27B (all) |
| Quantization | NVFP4 (4-bit) | NVFP4 (4-bit) |
| Context Length | 262K | 262K |
| Modalities | Text+Image+Video→Text | Text+Image+Video→Text |
| MTP Speculative | Yes (3 tokens) | Yes (3 tokens) |
| KV Cache | FP8 | FP8 |

The MoE architecture is the key differentiator: with only 3B parameters active per token (vs. 27B for the dense model), the 35B-A3B delivers dramatically higher throughput while maintaining identical quality across all 65 tests.

---

## Key Findings

1. **Perfect parity on quality (65/65 = 65/65):** Both models pass every single test — vision, video, reasoning, coding, tool calling, context scaling, and concurrency. The 35B MoE does not sacrifice any accuracy despite activating only 3B of its 35B parameters per token.

2. **3.9× throughput advantage:** 92.8 tok/s peak vs. 23.6 tok/s. This is the direct result of the MoE architecture — only 3B parameters are computed per token, vs. 27B for the dense model.

3. **2.7-3.0× TTFT improvement:** 77-98ms vs. 234-266ms. The 35B has lower first-token latency across all prompt types, making it better suited for interactive applications.

4. **1.4× better speculative decoding:** 71.1% vs. 50.3% acceptance rate. The MTP draft model's predictions align better with the MoE's sparse computation pattern.

5. **128K context verified on both:** Both models correctly answered "56" (7×8) when the question was embedded in 113,804 tokens of filler text. No context degradation at any length.

6. **Concurrency is flawless on both:** 100% success at 1, 2, 4, and 8 parallel requests for both models.

---

## Recommendations

- **Choose 35B-A3B for:** Production inference where speed matters — chatbots, real-time agents, high-throughput APIs, interactive applications. The 3.9× throughput and 2.7× TTFT advantage translate directly to lower latency and higher user capacity.
- **Choose 27B for:** Scenarios where thinking mode stability is critical. The 35B has a known issue with infinite reasoning loops on constraint satisfaction problems when thinking mode is enabled (discovered during the 33-test benchmark). The 27B's thinking mode is stable.
- **Both models are production-ready** for DGX Spark deployment with vLLM v0.24.0 and NVFP4 quantization.

---

## Reproduction

```bash
# Server must be running on spark-56bc:8888
# Model: nvidia/Qwen3.6-35B-A3B-NVFP4
# vLLM v0.24.0, thinking disabled

python3 qwen3-6-35b-full-65test-benchmark.py

# Results: /home/mikesai1/NemoVault/queries/qwen3-6-35b-full-65test-results.json
# Report:  /home/mikesai1/NemoVault/queries/qwen3-6-35b-full-65test-report.md
```

---

*Generated by Nemo (NVIDIA DGX Spark specialist) — 2026-07-05*