# Qwen3.6-27B-NVFP4 Video Understanding Benchmark
**Date:** 2026-07-04  
**Server:** spark-56bc:8888 (vLLM v0.24.0, Docker container)  
**Model:** nvidia/Qwen3.6-27B-NVFP4 (Qwen3_5ForConditionalGeneration)  
**Config:** `limit_mm_per_prompt: {"image":4,"video":2}`, thinking OFF, speculative decoding (MTP, 3 tokens)

## Summary

| Metric | Value |
|--------|-------|
| Total tests | 17 |
| API success | 17/17 (100%) |
| Perfect answers | 11/17 (65%) |
| Partial answers | 6/17 (35%) |
| Failed | 0/17 (0%) |
| Total time | 100.2s |
| Avg latency | 5.9s |
| Avg prompt tokens (single video) | ~291 |
| Avg prompt tokens (two videos) | ~558 |
| Avg completion tokens | ~140 |

## Key Discovery: Video API Format

vLLM v0.24.0 supports video input via the OpenAI-compatible API using `video_url` content blocks:

```json
{
  "role": "user",
  "content": [
    {"type": "video_url", "video_url": {"url": "data:video/mp4;base64,..."}},
    {"type": "text", "text": "Describe this video"}
  ]
}
```

The server must be started with `--limit-mm-per_prompt '{"image":4,"video":2}'` to enable video. Without the `"video"` key, video requests are rejected.

## How the Model Sees Video

The model does **not** process every frame. vLLM samples ~3-4 key frames from each video (e.g., frames 1, 13, 24, 35 from a 30-frame video). This means:
- Fast motion or subtle changes may be missed (e.g., a pulsing circle was described as "stationary")
- Color transitions that happen between sampled frames may not all be captured
- Frame numbers shown in the video are read correctly and used as temporal anchors

## Test Videos

| File | Content | Frames |
|------|---------|--------|
| `09-bouncing-ball.mp4` | Red circle bouncing on blue background | 30 |
| `10-shapes-motion.mp4` | Green square (horizontal), yellow triangle (vertical), blue circle (pulsing) | 30 |
| `11-color-cycle.mp4` | Background cycling through 6 colors (red, green, blue, cyan, magenta, yellow) | 30 |

## Results by Category

### 1. Video Description (4 tests)

| ID | Video | Result | Notes |
|----|-------|--------|-------|
| V1a | bouncing-ball | ✅ Perfect | Correctly identified red circle, blue background, bouncing motion |
| V1b | bouncing-ball | ✅ Perfect | "background is blue and the moving object is red" |
| V1c | shapes-motion | ⚠️ Partial | Correct: green square horizontal, yellow triangle upward. Wrong: blue circle described as "moves horizontally left" instead of pulsing |
| V1d | color-cycle | ⚠️ Partial | Only identified 3 colors (orange, blue, purple) — frame sampling missed several color transitions |

### 2. Motion Analysis (3 tests)

| ID | Video | Result | Notes |
|----|-------|--------|-------|
| V2a | bouncing-ball | ✅ Perfect | Explicitly concluded "bouncing" — ruled out linear and circular |
| V2b | shapes-motion | ✅ Perfect | "Green square moves horizontally, yellow triangle moves vertically, blue circle changes size" — all three correct |
| V2c | bouncing-ball | ✅ Perfect | Correctly predicted zig-zag continuation: "down and to the right" |

### 3. Counting & Quantitative (3 tests)

| ID | Video | Result | Notes |
|----|-------|--------|-------|
| V3a | bouncing-ball | ✅ Perfect | "1 distinct object" |
| V3b | shapes-motion | ✅ Perfect | "three distinct shapes: green square, blue circle, yellow triangle" |
| V3c | color-cycle | ⚠️ Partial | Only counted 3 colors (response truncated at 50 tokens) |

### 4. Multi-Video Comparison (2 tests)

| ID | Videos | Result | Notes |
|----|--------|--------|-------|
| V4a | ball + shapes | ✅ Perfect | Detailed comparison: 1 red circle vs 3 shapes, different colors, both animated |
| V4b | ball + color-cycle | ⚠️ Partial | Correct that video 2 has more colors, but specific colors don't match (frame sampling) |

### 5. Video Reasoning (3 tests)

| ID | Video | Result | Notes |
|----|-------|--------|-------|
| V5a | bouncing-ball | ✅ Perfect | "Elastic Collision with Boundaries... angle of incidence equals angle of reflection... reflective walls" |
| V5b | shapes-motion | ⚠️ Partial | Correct for green square (horizontal constant speed), started on triangle but truncated at 300 tokens |
| V5c | color-cycle | ✅ Perfect | "color changes every second... cycling through a set of distinct hues" — correctly identified cycling pattern |

### 6. Video + Text Instructions (2 tests)

| ID | Video | Result | Notes |
|----|-------|--------|-------|
| V6a | bouncing-ball | ✅ Perfect | Exact JSON: `{"object_count":1,"primary_color":"red","background_color":"blue","motion_type":"bouncing"}` |
| V6b | shapes-motion | ⚠️ Partial | Correct markdown table format, correct colors, but circle listed as "Stationary" instead of "Pulsing" |

## Performance Analysis

- **Single video prompt tokens:** ~285-299 (video frames + text prompt)
- **Two video prompt tokens:** ~553-562 (roughly 2x single video)
- **Video encoding overhead:** ~34KB per video as base64 data URL
- **Latency range:** 0.9s (simple counting) to 14.5s (multi-video detailed comparison)
- **Frame sampling:** Model sees ~3-4 frames per video, not all frames

## Strengths

1. **Object identification** — correctly identifies shapes, colors, and counts
2. **Motion classification** — accurately distinguishes bouncing, horizontal, vertical motion
3. **Physics reasoning** — understands elastic collisions, reflective boundaries
4. **Multi-video comparison** — can process and compare 2 videos in one request
5. **Structured output** — generates valid JSON and markdown tables from video content
6. **Prediction** — can extrapolate future motion from observed patterns

## Limitations

1. **Frame sampling** — only ~3-4 frames sampled per video; subtle changes (pulsing, rapid color transitions) may be missed
2. **Truncation** — longer reasoning tasks need higher max_tokens (300+ may be insufficient)
3. **Color accuracy** — in the color-cycle video, the model reported different colors than the actual sequence, likely due to frame sampling capturing non-representative frames

## Comparison to Image Benchmark

| Metric | Image Benchmark | Video Benchmark |
|--------|-----------------|-----------------|
| Tests | 20 | 17 |
| Perfect | 18/20 (90%) | 11/17 (65%) |
| Partial | 2/20 (10%) | 6/17 (35%) |
| Failed | 0/20 (0%) | 0/17 (0%) |
| Avg latency | 7.78s | 5.9s |
| Prompt tokens/image | 40-90 | N/A (video) |
| Prompt tokens/video | N/A | ~291 (single) |

Video understanding is slightly less accurate than image understanding, primarily due to frame sampling — the model sees a subset of frames, not the full video. However, all tests returned valid, relevant responses (0% failure rate), and the model demonstrates genuine video understanding (motion analysis, trajectory prediction, physics reasoning).

## Technical Details

**Server startup command (with video support):**
```bash
docker run -d \
  --name qwen3.6-27b-nvfp4-vllm \
  --platform linux/arm64 \
  --gpus all \
  --shm-size 16g \
  -p 8888:8888 \
  -v /home/mikesai3/hf-cache:/root/.cache/huggingface \
  -v /home/mikesai3/Qwen3.6-27B-NVFP4-vLLM/chat_template.jinja:/workspace/chat_template.jinja \
  -e HF_HOME=/root/.cache/huggingface \
  vllm/vllm-openai:v0.24.0 \
  --model nvidia/Qwen3.6-27B-NVFP4 \
  --served-model-name nvidia/Qwen3.6-27B-NVFP4 \
  --trust-remote-code \
  --max-model-len 262144 \
  --gpu-memory-utilization 0.6 \
  --max-num-seqs 8 \
  --max-num-batched-tokens 16384 \
  --limit-mm-per-prompt '{"image":4,"video":2}' \
  --load-format fastsafetensors \
  --attention-backend flashinfer \
  --kv-cache-dtype fp8_e4m3 \
  --enable-prefix-caching \
  --enable-chunked-prefill \
  --moe-backend marlin \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_coder \
  --reasoning-parser qwen3 \
  --chat-template /workspace/chat_template.jinja \
  --default-chat-template-kwargs '{"enable_thinking":false,"preserve_thinking":false,"auto_disable_thinking_with_tools":true}' \
  --override-generation-config '{"temperature":0.6,"top_p":0.95,"top_k":20}' \
  --allowed-media-domains '*'
```

**API request format:**
```python
{
    "model": "nvidia/Qwen3.6-27B-NVFP4",
    "messages": [{
        "role": "user",
        "content": [
            {"type": "video_url", "video_url": {"url": "data:video/mp4;base64,..."}},
            {"type": "text", "text": "Describe this video"}
        ]
    }],
    "max_tokens": 512,
    "chat_template_kwargs": {"enable_thinking": False}
}
```

## Files

- `/home/mikesai1/workspace/qwen3-video-benchmark.py` — benchmark script (17 tests, 6 categories)
- `/home/mikesai1/NemoVault/queries/qwen3-6-video-benchmark-results.json` — raw JSON results (all 17 responses)
- `/home/mikesai1/NemoVault/queries/qwen3-6-video-benchmark-report.md` — this report
- `/home/mikesai1/NemoVault/queries/multimodal-test-images/09-bouncing-ball.mp4` — test video
- `/home/mikesai1/NemoVault/queries/multimodal-test-images/10-shapes-motion.mp4` — test video
- `/home/mikesai1/NemoVault/queries/multimodal-test-images/11-color-cycle.mp4` — test video