# MiniMax H3 FL2VA on spark-56bc — video production (2026-09-05)

Serve: `http://spark-56bc:8000` model id `/models/MiniMax-H3/FL2VA`.
Container `minimax-h3-fl2va`, image `sm121-fp8`. Multipart `POST /v1/videos/sync`.

Checkpoint partition accepts **`t2va` and `fl2va` only**. Ref2VA (audio/video reference) is not loaded.

| Cell | HTTP | Wall / inference | Output |
|------|------|------------------|--------|
| T2VA 768×448, 20 steps, 2s | 200 | **159.1 s** client | 2.357 s, 768×448 H.264 @ 24 fps + AAC stereo 32 kHz, 698,852 bytes |
| FL2VA first-frame PNG, same recipe | 200 | **180.047 s** (`x-inference-time-s`) | 2.357 s, same codecs, 357,384 bytes; peak mem **92,752 MB** |

Geometric identity on FL2VA frame 0 vs source PNG (left / right RGB):
`(220, 40, 40)` → `(216.7, 39.0, 37.9)` and `(35.8, 67.3, 182)` → `(34.0, 65.1, 178)`.

Rejected (this checkpoint): `task=i2va` 500; `t2va` + image 500; `audio_reference`/`video_reference` as UploadFile 400; `/v1/audio/speech` 400 (no voices).

JSON: `results/h3-mm-summary.json`, `results/h3-seq-results.json`.
Generated MP4s are internal evaluation artifacts and are not published (MiniMax Community License).
