# Sol-H3-Spark on spark-56bc (2026-09-11/12)

Two-stage NVIDIA recipe on one DGX Spark GB10. Internal evaluation.
MiniMax H3 Community License + LTX-2.x Community License. Do not publish MP4s.

## Pin

- Tree: `~/Sana` `8e0db4f` (`sol-engine`)
- Runtime: `~/sol-h3-spark-runtime`
- Output: 1344×768, 121 frames, 24 fps, ~5.04 s, H.264 + AAC LC stereo 32 kHz
- Isolated T2VA (warmup excluded): 68.09 s (seed 42), 68.16 s (seed 7)
- NVIDIA published hot E2E: 56.17 s. Not reproduced here.

## Vs locked FL2VA 5 s cell (2026-09-05)

| | FL2VA 20-step | Sol-H3 4+3 |
|---|---|---|
| Wall | 423.2 s | 68.12 s mean |
| Pixels | 768×448 | 1344×768 (3×) |
| Sampler | 20-step H3 | FastH3 4-step + LTX 3-step |

Speedup on that cell: 6.21×. Different product, not faster 20-step H3.

## 20 s file

JSONL max 3 per `infer.py` (4th clip died `FailOnRecompileLimitHit`).
Wrapper path: 3-clip job PASS + 1 fresh job PASS + `ffmpeg -c copy` → 20.200 s / 484 frames.

## Sources of truth

Receipt JSON under `results/`. Batch `results.json` `status` is not truth when SSH times out.
