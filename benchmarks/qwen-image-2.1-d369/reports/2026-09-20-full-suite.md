# Qwen-Image-2.1 on spark-d369 — 2026-09-20

23/23 pass. INT8 ConvRot ComfyUI 0.36.0 (`9907383`) on 1× GB10.

- T2I 1024² / 25 step: 20.03 s wall after warmup (poll granularity 4 s)
- Native 2048² / 25 step: 128.08 s
- RGBA sticker: alpha_mean 116.7, alpha_std 126.4
- Edits: `TextEncodeQwenImageEdit` + `VAEEncode` (~28 s each). `TextEncodeQwenImage21(image_1=)` TypeError.

Raw JSON: `results/2026-09-20-full-suite.json`, `results/2026-09-20-edits.json`.
Harness: `scripts/qwen21_full_test.py`.
