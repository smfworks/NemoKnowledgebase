# Comfy native MiniMax H3 + Motion-Context — spark-56bc receipts (2026-09-12/13)

Internal eval. MiniMax H3 Community License. Do not publish MP4s.
Host: spark-56bc, 1× DGX Spark GB10, 128 GB UMA.
Stack: madeye/comfyui-minimax-h3-dgx-spark `4441d0c`, ComfyUI 0.35.0, torch 2.14.0+cu130,
INT8 ConvRot FL2VA, turbo LoRA v4-600, Motion-Context 0.6.2.
Listen: 127.0.0.1:8188 only.

Quality pin is human watch (Michael), not PSNR. PSNR is adjacent-frame comparison
(A last vs B first vs in-clip neighbors).

## 640×384 / 6-step turbo

| Job | Wall | ffprobe | Peak |
|---|---|---|---|
| T2V smoke | 79.47 s | 640×384, 124f, 5.167 s, H.264+AAC 32 kHz | 80°C |
| Chain A | 79.68 s | 124f / 5.167 s | — |
| Chain B context=22 | 76.50 s | 102f / 4.250 s (trim 22) | — |
| Concat A+B `-c copy` | — | 226f / 9.449 s | — |

Join PSNR A-last vs B-first 20.39 dB vs in-clip 21.24 / 20.02 dB.

## 1344×768 / 243-frame request / 6-step turbo / context_length=22

Request length 243 frames = 10.125 s (17k+5 grid). Hops N>1 trim 22 frames → 221f / 9.209 s.

| Hop | Seed | Wall | Delivered | Concat (A…N) | Join PSNR (last vs first / in-clip) | Peak |
|---|---|---|---|---|---|---|
| A | 42 | 1057 s (17:37) | 243f / 10.125 s | — | — | 83°C |
| B | 43 | 1178 s (19:38) | 221f / 9.209 s | 464f / 19.366 s | 18.53 vs 19.69 / 18.05 | 83°C |
| C | 44 | 1190 s (19:50) | 221f / 9.209 s | 685f / 28.575 s | 17.72 vs 18.80 / 17.22 | 82°C |
| D | 45 | 1190 s (19:50) | 221f / 9.209 s | 906f / 37.784 s | 18.17 vs 18.87 / 18.04 | 82°C |
| E | 46 | 1191 s (19:51) | 221f / 9.209 s | 1127f / 46.993 s | 17.01 vs 17.84 / 16.63 | 83°C |
| F | 47 | 1191 s (19:51) | 221f / 9.209 s | 1348f / 56.202 s | 16.03 vs 16.26 / 15.65 | 83°C |
| G–K | 48–52 | 1202 s each | 221f / 9.209 s | hops 7–11 | — | 83°C |
| L first | 53 | abort | — | — | — | **85°C** at t=260 |
| L retry | 53 | 1202 s | 221f / 9.209 s | — | — | 83°C |
| M | 54 | 1202 s | 221f / 9.209 s | — | — | 84°C |
| N | 55 | 1202 s | 221f / 9.209 s | **3116f / 129.874 s / 104.6 MB** | 13.51 vs 14.17 / 13.14 | 84°C |

GPU sum hops 1–14 ≈ 4.7 h.
Sampling 1344×768: ~150–173 s/it (6 steps). 640×384: ~8 s/it.

## Sol-H3 contrast (same box, drained for Comfy)

Isolated T2VA 68.09 / 68.16 s, 1344×768 / 121f / 5.04 s. No duration knob.
FL2VA last-frame glue PSNR 22.84 dB (old 20-step API 34.88 dB).

## Thermal / occupancy

Start GPU <65°C. Abort ≥85°C. One heavy engine per GB10.
spark-56bc = Comfy generate. spark-d369 = Qwen3.8-Flash-Next first-pass VLM.
Do not restore Sol-H3 or FL2VA without draining Comfy.
