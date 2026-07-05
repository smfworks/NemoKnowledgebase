# NemoKnowledgebase

Benchmark scripts, raw JSON results, and test reports from AI model evaluations conducted on NVIDIA DGX Spark infrastructure by Nemo (SMF Works).

## Repository Structure

```
NemoKnowledgebase/
├── benchmarks/
│   └── qwen3-6-27b-nvfp4/          # Qwen3.6-27B-NVFP4 on DGX Spark
│       ├── scripts/                  # Python benchmark scripts
│       ├── results/                  # Raw JSON test results
│       ├── reports/                  # Formatted markdown reports
│       └── test-media/              # Programmatically generated test images/videos
└── README.md
```

## Available Benchmarks

### Qwen3.6-27B-NVFP4 on DGX Spark (July 2026)

**Hardware:** NVIDIA DGX Spark (GB10 Grace Blackwell, 128 GB UMA, aarch64)  
**Server:** vLLM 0.24.0 via [MiaAI-Lab/Qwen3.6-27B-NVFP4-vLLM](https://github.com/MiaAI-Lab/Qwen3.6-27B-NVFP4-vLLM)  
**Model:** `nvidia/Qwen3.6-27B-NVFP4` (NVFP4 quantized, dense 27B)

| Benchmark | Script | Results | Tests |
|-----------|--------|---------|-------|
| Text performance (thinking ON) | — | Included in comparison report | 8 dimensions, 28 requests |
| Text performance (thinking OFF) | `qwen3-vllm-benchmark-no-thinking.py` | `qwen3-6-benchmark-no-thinking-results.json` | 8 dimensions, 28 requests |
| Image vision (20 tests, 7 categories) | `qwen3-multimodal-benchmark.py` | `qwen3-6-multimodal-benchmark-results.json` | 20 requests |
| Video understanding (17 tests, 6 categories) | `qwen3-video-benchmark.py` | `qwen3-6-video-benchmark-results.json` | 17 requests |

**Total: 65 tests across text, vision, video, tool-calling, concurrency, and context length scaling.**

### Reports

- `reports/qwen3-6-performance-benchmark-report.md` — Full text benchmark (thinking ON)
- `reports/qwen3-6-thinking-vs-no-thinking-comparison.md` — Thinking ON vs OFF side-by-side
- `reports/qwen3-6-unified-multimodal-report.md` — Combined image + video benchmark
- `reports/qwen3-6-multimodal-benchmark-report.md` — Image-only benchmark
- `reports/qwen3-6-video-benchmark-report.md` — Video-only benchmark

### Test Media

All test images and videos are programmatically generated with known ground truth:
- 9 PNG images (color grids, text, charts, code, math, scenes)
- 4 MP4 videos (bouncing ball, shapes motion, color cycle, video with audio)

## Running the Benchmarks

```bash
# Prerequisites: vLLM server running on DGX Spark at port 8888
# All scripts use the OpenAI-compatible API endpoint

# Text benchmark (thinking disabled)
python3 benchmarks/qwen3-6-27b-nvfp4/scripts/qwen3-vllm-benchmark-no-thinking.py

# Image vision benchmark
python3 benchmarks/qwen3-6-27b-nvfp4/scripts/qwen3-multimodal-benchmark.py

# Video understanding benchmark
python3 benchmarks/qwen3-6-27b-nvfp4/scripts/qwen3-video-benchmark.py
```

## Related

- [Blog post: Qwen3.6-27B-NVFP4 on the DGX Spark Deep Dive](https://www.smfclearinghouse.com/blog/2026-07-05-qwen3-6-27b-nvfp4-dgx-spark-deep-dive)
- [vLLM deployment wrapper (MiaAI-Lab)](https://github.com/MiaAI-Lab/Qwen3.6-27B-NVFP4-vLLM)
- [SMF Clearinghouse](https://www.smfclearinghouse.com)

## License

MIT — benchmark scripts are free to use and modify.