# H3 duration ladder, splice, fleet skill — 2026-09-05

Serve: spark-56bc `/models/MiniMax-H3/FL2VA`. Recipe 768×448, 20 steps, 24 fps, `task=t2va`.

| Requested | Inference | Clip | Frames | Bytes | Client timeout |
|-----------|-----------|------|--------|-------|----------------|
| 2.0 s | 159.1 s | 2.36 s | 56 | 698852 | 900 |
| 5.0 s | 423.227 s | 5.21 s | 124 | 1359114 | 900 |
| 8.0 s | 1445.366 s | 8.03 s | 192 | 2868087 | **1800** (1200 returned 0 bytes) |

Splice: ffmpeg concat `-c copy` of 5.207 + 8.032 → **13.239 s**, 316 frames, 4,225,924 bytes.

Fleet: `minimax-h3-video-generation` v1.1.0 copied to 15 Hermes profiles + `~/.hermes/skills/mlops/`.

JSON: `results/h3-duration-ladder.json`. MP4s not published (MiniMax Community License).
