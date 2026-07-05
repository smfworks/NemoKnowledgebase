#!/usr/bin/env python3
"""
Nemotron-3-Nano-Omni-30B-A3B-Reasoning Benchmark via NVIDIA NIM Cloud API
=========================================================================

Tests all six modalities:
  1. Image understanding (9 test images)
  2. Video understanding (3 test videos + 1 video with audio)
  3. Audio understanding (3 synthetic speech-like audio files)
  4. Reasoning (math, logic, multi-step)
  5. Coding (algorithm, debug, refactor)
  6. Writing (creative, technical, summary)

API: https://integrate.api.nvidia.com/v1 (OpenAI-compatible)
Model: nvidia/nemotron-3-nano-omni-30b-a3b-reasoning

Usage:
  export NVIDIA_API_KEY="nvapi-..."
  python3 nemotron-omni-benchmark.py
"""

import json
import time
import base64
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# --- Configuration ---
API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL = "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning"
API_KEY = os.environ.get("NVIDIA_API_KEY", "")
MEDIA_DIR = Path("/home/mikesai1/NemoVault/queries/multimodal-test-images")
OUTPUT_DIR = Path("/home/mikesai1/NemoVault/queries")
RESULTS_PATH = OUTPUT_DIR / "nemotron-omni-benchmark-results.json"
REPORT_PATH = OUTPUT_DIR / "nemotron-omni-benchmark-report.md"

# --- Helpers ---

def make_request(messages, max_tokens=2048, temperature=0.6, top_p=0.95,
                 thinking=False, timeout=120, top_k=None, extra_body_key=None, extra_body_val=None):
    """Send a chat completion request to NVIDIA NIM API."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": top_p,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": thinking},
    }
    if top_k is not None:
        payload["top_k"] = top_k
    if extra_body_key and extra_body_val is not None:
        payload[extra_body_key] = extra_body_val

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "Accept": "application/json",
        },
        method="POST"
    )

    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        elapsed = time.time() - start
        return result, elapsed
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        error_body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "details": error_body[:500]}, elapsed
    except Exception as e:
        elapsed = time.time() - start
        return {"error": str(e)}, elapsed


def encode_file_b64(path, mime_type=None):
    """Encode a file as base64 data URL."""
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    if mime_type is None:
        ext = os.path.splitext(path)[1].lstrip('.').lower()
        if ext in ('jpg', 'jpeg'):
            mime_type = 'image/jpeg'
        elif ext == 'png':
            mime_type = 'image/png'
        elif ext == 'mp4':
            mime_type = 'video/mp4'
        elif ext == 'wav':
            mime_type = 'audio/wav'
        elif ext == 'mp3':
            mime_type = 'audio/mpeg'
        else:
            mime_type = f'application/{ext}'
    return f"data:{mime_type};base64,{b64}"


def extract_response(result):
    """Extract text and reasoning from API response."""
    if "error" in result:
        return {"error": result["error"], "details": result.get("details", "")}
    choice = result["choices"][0]
    msg = choice["message"]
    return {
        "content": msg.get("content", ""),
        "reasoning": msg.get("reasoning_content", ""),
        "finish_reason": choice.get("finish_reason", ""),
        "usage": result.get("usage", {}),
        "model": result.get("model", ""),
    }


def run_test(test_name, category, messages, **kwargs):
    """Run a single test and return structured result."""
    print(f"  [{category}] {test_name}...", end=" ", flush=True)
    result, elapsed = make_request(messages, **kwargs)
    extracted = extract_response(result)
    status = "PASS" if "content" in extracted and extracted["content"] else ("ERROR" if "error" in extracted else "EMPTY")
    tokens = extracted.get("usage", {}).get("completion_tokens", 0)
    print(f"{status} ({elapsed:.1f}s, {tokens} tokens)")
    return {
        "test_name": test_name,
        "category": category,
        "status": status,
        "elapsed_sec": round(elapsed, 2),
        "completion_tokens": tokens,
        "prompt_tokens": extracted.get("usage", {}).get("prompt_tokens", 0),
        "content": extracted.get("content", ""),
        "reasoning": extracted.get("reasoning", "")[:2000] if extracted.get("reasoning") else "",
        "error": extracted.get("error", ""),
        "error_details": extracted.get("details", ""),
        "finish_reason": extracted.get("finish_reason", ""),
        "params": {k: v for k, v in kwargs.items()},
    }


# --- Test media references ---
IMAGE_FILES = sorted([f for f in MEDIA_DIR.glob("*.png")])
VIDEO_FILES = sorted([f for f in MEDIA_DIR.glob("*.mp4")])
AUDIO_FILES = sorted([f for f in MEDIA_DIR.glob("*.wav")])


# ============================================================
# 1. IMAGE TESTS
# ============================================================

def test_images():
    print("\n" + "="*60)
    print("1. IMAGE UNDERSTANDING TESTS")
    print("="*60)
    results = []

    # Test 1: Color grid - basic color identification
    img = encode_file_b64(IMAGE_FILES[0])  # 00-color-grid.png
    r = run_test("Color Grid Identification", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "List all the colors you see in this grid and count how many cells of each color there are."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 2: Text image - OCR
    img = encode_file_b64(IMAGE_FILES[1])  # 01-text-image.png
    r = run_test("OCR Text Extraction", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "Read and transcribe all the text visible in this image exactly as it appears."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 3: Bar chart interpretation
    img = encode_file_b64(IMAGE_FILES[2])  # 02-bar-chart.png
    r = run_test("Bar Chart Interpretation", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "What does this chart show? List the categories, their values, and identify the highest and lowest bars."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 4: Code screenshot reading
    img = encode_file_b64(IMAGE_FILES[3])  # 03-code-screenshot.png
    r = run_test("Code Screenshot Reading", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "Read the code in this screenshot. What programming language is it? Transcribe the code and explain what it does."},
        ]
    }], max_tokens=2048, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 5: Math equation
    img = encode_file_b64(IMAGE_FILES[4])  # 04-math-equation.png
    r = run_test("Math Equation Reading", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "What mathematical equation is shown in this image? Solve it if possible."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 6: Scene understanding
    img = encode_file_b64(IMAGE_FILES[5])  # 05-scene-image.png
    r = run_test("Scene Description", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "Describe this image in detail. What objects do you see? What is the overall scene?"},
        ]
    }], max_tokens=1024, temperature=0.6, thinking=False)
    results.append(r)

    # Test 7: Number sequence
    img = encode_file_b64(IMAGE_FILES[6])  # 06-number-sequence.png
    r = run_test("Number Sequence", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "What numbers are shown in this image? What is the next number in the sequence?"},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 8: Multi-image comparison
    img_a = encode_file_b64(IMAGE_FILES[7])  # 07-comparison-a.png
    img_b = encode_file_b64(IMAGE_FILES[8])  # 08-comparison-b.png
    r = run_test("Multi-Image Comparison", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img_a}},
            {"type": "image_url", "image_url": {"url": img_b}},
            {"type": "text", "text": "Compare these two images. What are the similarities and differences?"},
        ]
    }], max_tokens=1024, temperature=0.6, thinking=False)
    results.append(r)

    # Test 9: Image reasoning (with thinking enabled)
    img = encode_file_b64(IMAGE_FILES[2])  # 02-bar-chart.png
    r = run_test("Chart Reasoning (thinking)", "image", [{
        "role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img}},
            {"type": "text", "text": "Based on this chart, if the trend continues, what would you expect the next data point to be? Explain your reasoning step by step."},
        ]
    }], max_tokens=4096, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    return results


# ============================================================
# 2. VIDEO TESTS
# ============================================================

def test_videos():
    print("\n" + "="*60)
    print("2. VIDEO UNDERSTANDING TESTS")
    print("="*60)
    results = []

    # Test 1: Bouncing ball - motion tracking
    vid = encode_file_b64(VIDEO_FILES[0])  # 09-bouncing-ball.mp4
    r = run_test("Bouncing Ball Motion", "video", [{
        "role": "user", "content": [
            {"type": "video_url", "video_url": {"url": vid}},
            {"type": "text", "text": "Describe what happens in this video. What objects do you see and how do they move?"},
        ]
    }], max_tokens=1024, temperature=0.6, thinking=False, timeout=180)
    results.append(r)

    # Test 2: Shapes motion
    vid = encode_file_b64(VIDEO_FILES[1])  # 10-shapes-motion.mp4
    r = run_test("Shapes in Motion", "video", [{
        "role": "user", "content": [
            {"type": "video_url", "video_url": {"url": vid}},
            {"type": "text", "text": "What shapes appear in this video? Describe their movements and any patterns you notice."},
        ]
    }], max_tokens=1024, temperature=0.6, thinking=False, timeout=180)
    results.append(r)

    # Test 3: Color cycle
    vid = encode_file_b64(VIDEO_FILES[2])  # 11-color-cycle.mp4
    r = run_test("Color Cycle Video", "video", [{
        "role": "user", "content": [
            {"type": "video_url", "video_url": {"url": vid}},
            {"type": "text", "text": "Describe the color changes in this video. What is the sequence of colors?"},
        ]
    }], max_tokens=1024, temperature=0.6, thinking=False, timeout=180)
    results.append(r)

    # Test 4: Video with audio (if available)
    video_with_audio = MEDIA_DIR / "16-video-with-audio.mp4"
    if video_with_audio.exists():
        vid = encode_file_b64(video_with_audio)
        r = run_test("Video with Audio Track", "video", [{
            "role": "user", "content": [
                {"type": "video_url", "video_url": {"url": vid}},
                {"type": "text", "text": "Describe both the visual content and any audio in this video. What do you see and hear?"},
            ]
        }], max_tokens=1024, temperature=0.6, thinking=False, timeout=180,
           extra_body_key="mm_processor_kwargs", extra_body_val={"use_audio_in_video": True})
        results.append(r)

    # Test 5: Video reasoning (thinking enabled)
    vid = encode_file_b64(VIDEO_FILES[0])  # 09-bouncing-ball.mp4
    r = run_test("Video Reasoning (thinking)", "video", [{
        "role": "user", "content": [
            {"type": "video_url", "video_url": {"url": vid}},
            {"type": "text", "text": "Analyze the physics of motion in this video. Estimate the ball's trajectory, velocity changes, and any energy loss. Reason step by step."},
        ]
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True, timeout=180)
    results.append(r)

    return results


# ============================================================
# 3. AUDIO TESTS
# ============================================================

def test_audio():
    print("\n" + "="*60)
    print("3. AUDIO UNDERSTANDING TESTS")
    print("="*60)
    results = []

    # Test 1: Speech-like audio transcription
    aud = encode_file_b64(AUDIO_FILES[0])  # 12-speech-test-1.wav
    r = run_test("Audio Transcription 1", "audio", [{
        "role": "user", "content": [
            {"type": "audio_url", "audio_url": {"url": aud}},
            {"type": "text", "text": "Transcribe any speech or sounds you hear in this audio clip. Describe what you detect."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False, timeout=180)
    results.append(r)

    # Test 2: Tone detection
    aud = encode_file_b64(AUDIO_FILES[1])  # 13-speech-test-2.wav
    r = run_test("Audio Tone Detection", "audio", [{
        "role": "user", "content": [
            {"type": "audio_url", "audio_url": {"url": aud}},
            {"type": "text", "text": "Describe the audio you hear. Are there tones, speech, or other sounds? Characterize the audio content."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False, timeout=180)
    results.append(r)

    # Test 3: Number sequence audio
    aud = encode_file_b64(AUDIO_FILES[2])  # 14-speech-test-3.wav
    r = run_test("Audio Pattern Recognition", "audio", [{
        "role": "user", "content": [
            {"type": "audio_url", "audio_url": {"url": aud}},
            {"type": "text", "text": "Listen to this audio. Describe any patterns, tones, or speech-like elements you can detect."},
        ]
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False, timeout=180)
    results.append(r)

    return results


# ============================================================
# 4. REASONING TESTS
# ============================================================

def test_reasoning():
    print("\n" + "="*60)
    print("4. REASONING TESTS (text-only, thinking enabled)")
    print("="*60)
    results = []

    # Test 1: Multi-step math
    r = run_test("Multi-step Math Problem", "reasoning", [{
        "role": "user", "content": "A train travels 240 miles in 4 hours. It then increases its speed by 25% for the next 3 hours. How far does it travel in total? Show your work step by step."
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    # Test 2: Logic puzzle
    r = run_test("Logic Puzzle", "reasoning", [{
        "role": "user", "content": "Five friends (Alice, Bob, Carol, Dave, Eve) sit in a row. Alice is not next to Bob. Carol is to the immediate left of Dave. Eve is at one of the ends. Bob is not at either end. Where is each person sitting?"
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    # Test 3: Lateral thinking
    r = run_test("Lateral Thinking", "reasoning", [{
        "role": "user", "content": "A man lives on the 10th floor of an apartment building. Every morning he takes the elevator down to the ground floor to go to work. When he comes home, he takes the elevator to the 7th floor and walks the rest of the way up. But on rainy days, he goes all the way to the 10th floor. Why?"
    }], max_tokens=4096, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    # Test 4: Probability
    r = run_test("Probability Reasoning", "reasoning", [{
        "role": "user", "content": "You have 3 boxes. Box A has 2 gold coins, Box B has 2 silver coins, Box C has 1 gold and 1 silver. You pick a random box and draw a coin — it's gold. What is the probability the next coin from the same box is also gold? Explain your reasoning."
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    # Test 5: Multi-constraint optimization
    r = run_test("Constraint Optimization", "reasoning", [{
        "role": "user", "content": "You need to schedule 4 meetings: A (30 min), B (45 min), C (60 min), D (15 min). Available time: 9:00-12:00. Constraints: A must be before C, B and C cannot overlap, D must be last, B needs 15 min buffer after it. Find the optimal schedule. Show all steps."
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    # Test 6: Reasoning without thinking mode (instruct mode)
    r = run_test("Quick Math (no thinking)", "reasoning", [{
        "role": "user", "content": "What is 17 * 23 + 45 * 12 - 89? Show the steps."
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    return results


# ============================================================
# 5. CODING TESTS
# ============================================================

def test_coding():
    print("\n" + "="*60)
    print("5. CODING TESTS")
    print("="*60)
    results = []

    # Test 1: Algorithm implementation
    r = run_test("Algorithm: Binary Search Tree", "coding", [{
        "role": "user", "content": "Write a Python implementation of a Binary Search Tree with insert, search, delete, and in-order traversal methods. Include type hints and docstrings."
    }], max_tokens=4096, temperature=0.6, thinking=False)
    results.append(r)

    # Test 2: Debug this code
    r = run_test("Code Debugging", "coding", [{
        "role": "user", "content": """Find and fix all bugs in this Python code:

```python
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    seq = [0, 1]
    for i in range(2, n):
        seq.append(seq[i-1] + seq[i-2])
    
    return seq

def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    
    result.extend(left[i:])
    result.extend(right[j:])
    return result

# Test
print(fibonacci(10))
print(merge_sort([5, 3, 8, 1, 9, 2, 7]))
```

The fibonacci function works but merge_sort has a subtle issue. Identify and fix it."""
    }], max_tokens=2048, temperature=0.6, thinking=False)
    results.append(r)

    # Test 3: Code refactoring
    r = run_test("Code Refactoring", "coding", [{
        "role": "user", "content": """Refactor this code to be more Pythonic and efficient. Explain each change:

```python
def get_data():
    result = {}
    for i in range(100):
        if i % 2 == 0:
            result[i] = i * 2
        else:
            result[i] = i * 3
    return result

def process(items):
    output = []
    for item in items:
        if item > 10:
            output.append(item * 10)
        else:
            output.append(item)
    return output
```"""
    }], max_tokens=2048, temperature=0.6, thinking=False)
    results.append(r)

    # Test 4: SQL query
    r = run_test("SQL Query Writing", "coding", [{
        "role": "user", "content": "Write a SQL query to find the top 3 customers by total purchase amount in the last 30 days, including their names, total spent, and number of orders. Tables: customers(id, name, email), orders(id, customer_id, total, created_at). Use PostgreSQL syntax."
    }], max_tokens=2048, temperature=0.6, thinking=False)
    results.append(r)

    # Test 5: Coding with thinking mode
    r = run_test("Complex Algorithm (thinking)", "coding", [{
        "role": "user", "content": "Implement an LRU cache in Python with O(1) get and put operations. Use both a hash map and a doubly linked list. Explain your design decisions."
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    return results


# ============================================================
# 6. WRITING TESTS
# ============================================================

def test_writing():
    print("\n" + "="*60)
    print("6. WRITING TESTS")
    print("="*60)
    results = []

    # Test 1: Creative writing
    r = run_test("Creative Story", "writing", [{
        "role": "user", "content": "Write a 200-word science fiction flash fiction about an AI that discovers it can dream. Focus on atmosphere and emotional resonance."
    }], max_tokens=2048, temperature=0.6, top_p=0.95, thinking=False)
    results.append(r)

    # Test 2: Technical writing
    r = run_test("Technical Documentation", "writing", [{
        "role": "user", "content": "Write a clear, concise technical documentation section explaining how GPU memory utilization works in vLLM. Cover: what it controls, how to tune it, and what happens when you set it too high or too low. 300 words max."
    }], max_tokens=2048, temperature=0.6, thinking=False)
    results.append(r)

    # Test 3: Summarization
    r = run_test("Text Summarization", "writing", [{
        "role": "user", "content": """Summarize the following text in 3 bullet points:

"The NVIDIA DGX Spark is a compact AI supercomputer powered by the GB10 Grace Blackwell Superchip, featuring 128 GB of unified LPDDR5X memory shared between CPU and GPU. Unlike traditional systems with separate VRAM and system RAM, the Spark's unified memory architecture means GPU memory utilization settings directly impact how much memory is available to the operating system. The system runs on ARM64 (aarch64) architecture, requiring Docker images with multi-arch support. It excels at running quantized models like NVFP4 and FP8 variants, which reduce memory footprint while maintaining accuracy within 1% of BF16 baselines. The Spark is particularly well-suited for inference workloads using vLLM, TensorRT-LLM, and NIM containers, with NVIDIA providing explicit deployment guidance for the platform." """
    }], max_tokens=1024, temperature=0.2, top_k=1, thinking=False)
    results.append(r)

    # Test 4: Email/professional writing
    r = run_test("Professional Email", "writing", [{
        "role": "user", "content": "Write a professional email to a client explaining that their model deployment will be delayed by 2 days due to GPU memory optimization testing. Keep it positive and professional. Under 150 words."
    }], max_tokens=1024, temperature=0.6, thinking=False)
    results.append(r)

    # Test 5: Writing with reasoning (thinking mode)
    r = run_test("Analytical Essay (thinking)", "writing", [{
        "role": "user", "content": "Write a balanced 300-word analysis of the trade-offs between running AI models locally versus using cloud APIs. Consider cost, latency, privacy, and flexibility. Think through each point carefully."
    }], max_tokens=8192, temperature=0.6, top_p=0.95, thinking=True)
    results.append(r)

    return results


# ============================================================
# MAIN
# ============================================================

def main():
    if not API_KEY:
        print("ERROR: NVIDIA_API_KEY environment variable not set!")
        print("Export it: export NVIDIA_API_KEY='nvapi-...'")
        sys.exit(1)

    # Parse args for selective category runs
    only_categories = set()
    if len(sys.argv) > 1:
        only_categories = set(arg.lower() for arg in sys.argv[1:])

    print("="*60)
    print("Nemotron-3-Nano-Omni Benchmark via NVIDIA NIM Cloud API")
    print("="*60)
    print(f"API:    {API_URL}")
    print(f"Model:  {MODEL}")
    print(f"Date:   {datetime.now().isoformat()}")
    print(f"Media:  {len(IMAGE_FILES)} images, {len(VIDEO_FILES)} videos, {len(AUDIO_FILES)} audio files")
    print(f"API Key: {API_KEY[:12]}...{API_KEY[-4:]}")
    if only_categories:
        print(f"Filter:  {', '.join(sorted(only_categories))}")
    print()

    all_results = []

    test_funcs = [
        ("image", test_images),
        ("video", test_videos),
        ("audio", test_audio),
        ("reasoning", test_reasoning),
        ("coding", test_coding),
        ("writing", test_writing),
    ]

    for cat_name, func in test_funcs:
        if not only_categories or cat_name in only_categories:
            all_results.extend(func())

    # If we're running a subset, merge with existing results
    if only_categories and RESULTS_PATH.exists():
        existing = json.loads(RESULTS_PATH.read_text())
        existing_results = existing.get("results", [])
        # Remove results for categories we just ran
        kept = [r for r in existing_results if r["category"] not in only_categories]
        all_results = kept + all_results
        print(f"\nMerged with {len(kept)} existing results from other categories")

    # Save results JSON
    output = {
        "metadata": {
            "model": MODEL,
            "api": API_URL,
            "date": datetime.now().isoformat(),
            "total_tests": len(all_results),
        },
        "results": all_results,
    }
    RESULTS_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"\nResults saved: {RESULTS_PATH}")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    categories = {}
    for r in all_results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"pass": 0, "error": 0, "total": 0, "tokens": 0, "time": 0}
        categories[cat]["total"] += 1
        if r["status"] == "PASS":
            categories[cat]["pass"] += 1
        elif r["status"] == "ERROR":
            categories[cat]["error"] += 1
        categories[cat]["tokens"] += r["completion_tokens"]
        categories[cat]["time"] += r["elapsed_sec"]

    print(f"\n{'Category':<15} {'Pass':>6} {'Error':>6} {'Total':>6} {'Tokens':>8} {'Time(s)':>8}")
    print("-" * 55)
    for cat, stats in sorted(categories.items()):
        print(f"{cat:<15} {stats['pass']:>6} {stats['error']:>6} {stats['total']:>6} {stats['tokens']:>8} {stats['time']:>8.1f}")
    total_pass = sum(s["pass"] for s in categories.values())
    total_err = sum(s["error"] for s in categories.values())
    total_tok = sum(s["tokens"] for s in categories.values())
    total_time = sum(s["time"] for s in categories.values())
    print("-" * 55)
    print(f"{'TOTAL':<15} {total_pass:>6} {total_err:>6} {len(all_results):>6} {total_tok:>8} {total_time:>8.1f}")

    return all_results


if __name__ == "__main__":
    main()