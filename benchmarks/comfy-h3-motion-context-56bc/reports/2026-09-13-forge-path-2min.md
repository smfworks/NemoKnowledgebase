# Forge-path story receipts — spark-56bc (2026-09-13)

Internal eval. MiniMax H3 Community License. Do not publish MP4s.
Host: spark-56bc, 1× DGX Spark GB10, 128 GB UMA.
Stack: ComfyUI 0.35.0, torch 2.14.0+cu130, INT8 ConvRot + turbo v4-600, Motion-Context 0.6.2.
Recipe: 1344×768, 24 fps, 243-frame request, 6-step turbo.

Human (Michael, 2026-09-13): picture **excellent**. Dialogue **garbled / unintelligible** — win later.

## Three-clip smoke (no hops)

| File | Clip | Wall | Peak | ffprobe |
|---|---|---|---|---|
| 36 | A1 meadow seed 80 | 1062 s | 83°C | 10.125 s / 243 f |
| 37 | B1 porch seed 81 | abort 85°C @ 7 min, retry 1062 s | 84°C | 10.125 s / 243 f |
| 38 | C1 blade seed 82 | 1062 s | 84°C | 10.125 s / 243 f |
| 39 | fadeblack-8f ×2 | — | — | **29.766 s / 713 f** |

Dialogue failure on 36/39: speech energy 9.00–9.75 s; fade offset 9.791667 s.

Reshoot A1 only (seed 80, line “Almost home.” finished by 8 s):

| File | ASR | ffprobe |
|---|---|---|
| 40 | “Almost home.” 7.86–9.24 s; energy gone by 9.50 s | 10.125 s / 243 f |
| 41 | 40 + 37 + 38 fadeblack | **29.766 s / 713 f** |

## 2 min story (three takes)

Cannot hop 40/37/38 — no SaveLatent. Rebuilt hop-1 with unique prefixes `forgeA` / `forgeB` / `forgeC`.

| Take | Windows | Concat | Duration |
|---|---|---|---|
| A meadow gold | 4 hops, `-c copy` | `42-forge2-takeA.mp4` | **37.784 s / 906 f / 14.6 MB** |
| B porch dusk | 4 hops | `43-forge2-takeB.mp4` | **37.784 s / 906 f / 11.6 MB** |
| C lamp interior | 5 hops | `44-forge2-takeC.mp4` | **46.993 s / 1127 f / 9.8 MB** |
| Story | two fadeblack-8f | `45-forge2-2min.mp4` | **122.342 s / 2926 f / 65.0 MB** |

Hop-1 wall **1062 s**. Hop 2+ **1202–1222 s**.

Thermal aborts ≥85°C (all retried PASS): B1×2, B2, B3, C1, C4. After soak, start **<58°C**, cool **≥240 s**.

Driver: `~/comfyui-minimax-h3-dgx-spark/bin/forge-2min-driver.py`. Log: `logs/forge-2min.jsonl`.

Drive folder `13XWI67-DjuqbqL1_F-VGKQajeLbC2ZH4` (internal).
