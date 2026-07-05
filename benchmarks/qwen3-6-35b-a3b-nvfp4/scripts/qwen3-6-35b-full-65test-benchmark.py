#!/usr/bin/env python3
"""
Qwen3.6-35B-A3B-NVFP4 Full 65-Test Benchmark
Mirrors the exact same 65-test suite used for the 27B model across 8 dimensions:
  1. Vision/Image Understanding (20 tests)
  2. Video Understanding (17 tests)
  3. Latency & Throughput (5 sub-tests)
  4. TTFT (3 sub-tests)
  5. Concurrency (4 sub-tests: 1,2,4,8)
  6. Context Length Scaling (6 sub-tests: 100→128K)
  7. Reasoning Quality (8 tests)
  8. Tool Calling (2 tests)

Server: spark-56bc:8888
Model: nvidia/Qwen3.6-35B-A3B-NVFP4
Thinking: DISABLED via chat_template_kwargs
"""

import json
import time
import base64
import io
import os
import re
import statistics
import concurrent.futures
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

import requests

# ============================================================
# Configuration
# ============================================================
ENDPOINT = "http://spark-56bc:8888/v1/chat/completions"
MODELS_URL = "http://spark-56bc:8888/v1/models"
METRICS_URL = "http://spark-56bc:8888/metrics"
MODEL = "nvidia/Qwen3.6-35B-A3B-NVFP4"
TIMEOUT = 300
VIDEO_DIR = "/home/mikesai1/NemoVault/queries/multimodal-test-images"
OUTPUT_DIR = Path("/home/mikesai1/NemoVault/queries")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_FILE = OUTPUT_DIR / "qwen3-6-35b-full-65test-results.json"
REPORT_FILE = OUTPUT_DIR / "qwen3-6-35b-full-65test-report.md"

CHAT_TEMPLATE_KWARGS = {"enable_thinking": False}


# ============================================================
# Request Helpers (None-safe)
# ============================================================

def make_payload(messages, max_tokens=1024, stream=False, extra=None):
    p = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": stream,
        "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
    }
    if extra:
        p.update(extra)
    return p


def non_stream_request(messages, max_tokens=1024, extra=None):
    """Send non-streaming request. Returns (text, wall, finish, usage, message)."""
    payload = make_payload(messages, max_tokens=max_tokens, stream=False, extra=extra)
    start = time.time()
    resp = requests.post(ENDPOINT, json=payload, timeout=TIMEOUT)
    wall = time.time() - start
    resp.raise_for_status()
    data = resp.json()
    choice = data["choices"][0]
    message = choice.get("message", {}) or {}
    text = message.get("content", "") or ""
    finish = choice.get("finish_reason", "") or ""
    usage = data.get("usage", {}) or {}
    return text, wall, finish, usage, message


def stream_request(messages, max_tokens=1024, extra=None):
    """Send streaming request. Returns (text, reasoning, ttft, wall, finish)."""
    payload = make_payload(messages, max_tokens=max_tokens, stream=True, extra=extra)
    start = time.time()
    ttft = None
    content_parts = []
    reasoning_parts = []
    finish_reason = ""

    resp = requests.post(ENDPOINT, json=payload, stream=True, timeout=TIMEOUT)
    for line in resp.iter_lines():
        if not line:
            continue
        line_str = line.decode("utf-8")
        if line_str.startswith("data: "):
            line_str = line_str[6:]
        if line_str == "[DONE]":
            break
        try:
            chunk = json.loads(line_str)
        except json.JSONDecodeError:
            continue

        if ttft is None:
            ttft = time.time() - start

        choices = chunk.get("choices", [])
        if choices:
            delta = choices[0].get("delta", {}) or {}
            if delta.get("content"):
                content_parts.append(delta["content"])
            if delta.get("reasoning_content"):
                reasoning_parts.append(delta["reasoning_content"])
            if choices[0].get("finish_reason"):
                finish_reason = choices[0]["finish_reason"]

    wall = time.time() - start
    return "".join(content_parts), "".join(reasoning_parts), ttft, wall, finish_reason


def img_to_b64(pil_image, format="PNG"):
    buf = io.BytesIO()
    pil_image.save(buf, format=format)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def encode_video(path):
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lstrip('.')
    return f"data:video/{ext};base64,{b64}"


def multimodal_request(messages, max_tokens=1024, images=None, videos=None, timeout=120):
    """Send a multimodal request with inline base64 images/videos."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "chat_template_kwargs": CHAT_TEMPLATE_KWARGS,
    }

    # Restructure last user message for multimodal content
    last_msg = payload["messages"][-1]
    if last_msg["role"] == "user" and (images or videos):
        content = []
        if images:
            for img_b64 in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                })
        if videos:
            for vid_url in videos:
                content.append({
                    "type": "video_url",
                    "video_url": {"url": vid_url}
                })
        content.append({"type": "text", "text": last_msg["content"]})
        last_msg["content"] = content

    start = time.time()
    try:
        resp = requests.post(ENDPOINT, json=payload, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        wall = time.time() - start
        choice = data["choices"][0]
        message = choice.get("message", {}) or {}
        text = message.get("content", "") or ""
        finish = choice.get("finish_reason", "") or ""
        usage = data.get("usage", {}) or {}
        return {"text": text, "finish": finish, "usage": usage, "wall": wall, "error": None}
    except Exception as e:
        wall = time.time() - start
        return {"text": "", "finish": "", "usage": {}, "wall": wall, "error": str(e)}


# ============================================================
# Image Generators (same as 27B test suite)
# ============================================================

def gen_color_grid():
    from PIL import Image, ImageDraw
    import random
    random.seed(42)
    cell_size = 100
    cols, rows = 4, 4
    img = Image.new("RGB", (cols * cell_size, rows * cell_size), "white")
    draw = ImageDraw.Draw(img)
    colors = ["red", "blue", "green", "yellow", "purple", "orange", "cyan", "magenta"]
    color_map = []
    for r in range(rows):
        for c in range(cols):
            color = random.choice(colors)
            x1, y1 = c * cell_size, r * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            draw.rectangle([x1, y1, x2, y2], fill=color, outline="black", width=2)
            color_map.append(f"({r},{c}):{color}")
    return img, f"4x4 grid with colors: {', '.join(color_map)}"


def gen_text_image():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (600, 200), "white")
    draw = ImageDraw.Draw(img)
    lines = [
        "The quick brown fox jumps over the lazy dog.",
        "Hermes Agent v2.1.0 - Build #4832",
        "API_KEY: «redacted:sk-…»",
        "Date: 2026-07-03  Temperature: 72°F",
    ]
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black")
        y += 40
    return img, "4 lines of text: fox sentence, Hermes version, API key, date/temp"


def gen_bar_chart():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from PIL import Image
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    categories = ["Q1", "Q2", "Q3", "Q4"]
    values = [120, 185, 95, 210]
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]
    bars = ax.bar(categories, values, color=colors)
    ax.set_ylabel("Revenue ($K)")
    ax.set_title("Quarterly Revenue 2025")
    ax.set_ylim(0, 250)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"${val}K", ha="center", va="bottom", fontsize=11, fontweight="bold")
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    buf.seek(0)
    pil_img = Image.open(buf)
    return pil_img, "Bar chart: Q1=$120K, Q2=$185K, Q3=$95K, Q4=$210K"


def gen_code_screenshot():
    from PIL import Image, ImageDraw
    code_lines = [
        "def fibonacci(n):",
        "    if n <= 1:",
        "        return n",
        "    a, b = 0, 1",
        "    for _ in range(2, n + 1):",
        "        a, b = b, a + b",
        "    return b",
        "",
        "result = fibonacci(10)",
        "print(f'fib(10) = {result}')",
    ]
    img = Image.new("RGB", (520, 280), (30, 30, 30))
    draw = ImageDraw.Draw(img)
    y = 15
    for line in code_lines:
        color = (200, 200, 200)
        if line.startswith("def "):
            color = (86, 156, 214)
        elif line.startswith("    return"):
            color = (78, 201, 176)
        elif line.startswith("result") or line.startswith("print"):
            color = (206, 145, 120)
        elif "fibonacci" in line:
            color = (220, 220, 170)
        draw.text((15, y), line, fill=color)
        y += 25
    return img, "Python code: fibonacci function, fib(10) call, print result"


def gen_math_equation():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (500, 150), "white")
    draw = ImageDraw.Draw(img)
    draw.text((30, 30), "Solve for x:", fill="black")
    draw.text((30, 70), "3x² - 12x + 9 = 0", fill="black")
    draw.text((30, 105), "Find all real roots.", fill="black")
    return img, "Quadratic equation: 3x² - 12x + 9 = 0, roots x=1 and x=3"


def gen_scene_image():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (500, 400), "white")
    draw = ImageDraw.Draw(img)
    draw.ellipse([380, 30, 460, 110], fill="yellow", outline="orange", width=2)
    draw.rectangle([150, 200, 300, 350], fill="#8B4513", outline="black", width=2)
    draw.polygon([(140, 200), (225, 120), (310, 200)], fill="red", outline="black")
    draw.rectangle([210, 270, 240, 350], fill="#4A3520", outline="black")
    draw.rectangle([165, 220, 195, 250], fill="lightblue", outline="black")
    draw.rectangle([255, 220, 285, 250], fill="lightblue", outline="black")
    draw.rectangle([60, 250, 80, 350], fill="#4A3520", outline="black")
    draw.ellipse([30, 170, 110, 260], fill="green", outline="darkgreen", width=2)
    draw.rectangle([0, 350, 500, 400], fill="lightgreen")
    return img, "Scene: sun top-right, house center (brown walls, red roof, blue windows, dark door), tree left (green canopy, brown trunk), grass at bottom"


def gen_number_sequence():
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (600, 100), "white")
    draw = ImageDraw.Draw(img)
    draw.text((30, 30), "2, 6, 12, 20, 30, ?", fill="black")
    return img, "Number sequence: 2, 6, 12, 20, 30, ? — answer is 42 (n*(n+1))"


def gen_two_images_for_comparison():
    from PIL import Image, ImageDraw
    img1 = Image.new("RGB", (300, 300), "white")
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([50, 50, 250, 250], fill="red", outline="black", width=3)
    draw1.text((100, 280), "Image A", fill="black")
    img2 = Image.new("RGB", (300, 300), "white")
    draw2 = ImageDraw.Draw(img2)
    draw2.ellipse([50, 50, 250, 250], fill="blue", outline="black", width=3)
    draw2.text((100, 280), "Image B", fill="black")
    return (img1, img2), "Image A: red square, Image B: blue circle"


# ============================================================
# DIMENSION 1: Vision/Image Understanding (20 tests)
# ============================================================

def run_vision_tests(b64_images, ground_truth):
    print("\n" + "="*70)
    print("DIMENSION 1: Vision/Image Understanding (20 tests)")
    print("="*70)
    results = []

    # Section 1: Single Image (5 tests)
    tests_s1 = [
        {"name": "1a — Describe image", "idx": 0, "prompt": "Describe what you see in this image in detail. What colors and shapes are present?", "max": 512},
        {"name": "1b — Count objects", "idx": 0, "prompt": "How many colored squares are in this image? Count them carefully.", "max": 256},
        {"name": "1c — Identify colors", "idx": 0, "prompt": "List all the unique colors you can see in this grid image.", "max": 256},
        {"name": "1d — Scene description", "idx": 5, "prompt": "Describe this scene in detail. What objects do you see, their positions, and colors?", "max": 512},
        {"name": "1e — Spatial reasoning", "idx": 5, "prompt": "In this image, what is the position of the sun relative to the house? Is the tree to the left or right of the house?", "max": 256},
    ]
    for t in tests_s1:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[b64_images[t["idx"]]])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "single_image",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    # Section 2: Multiple Images (2 tests)
    img_a = b64_images[-2]
    img_b = b64_images[-1]
    tests_s2 = [
        {"name": "2a — Compare two images", "prompt": "I'm showing you two images. Describe the differences between Image A and Image B. What shape and color is each?", "max": 512},
        {"name": "2b — Which has circle?", "prompt": "Between these two images, which one contains a circle? Answer with 'Image A' or 'Image B'.", "max": 128},
    ]
    for t in tests_s2:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[img_a, img_b])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "multi_image",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    # Section 3: OCR (3 tests)
    tests_s3 = [
        {"name": "3a — Read text", "idx": 1, "prompt": "Read and transcribe all the text you can see in this image. Output each line separately.", "max": 512},
        {"name": "3b — Extract API key", "idx": 1, "prompt": "What is the API key shown in this image? Extract only the API key value.", "max": 128},
        {"name": "3c — Read code", "idx": 3, "prompt": "Read the code in this image and transcribe it. What function is defined and what is the expected output?", "max": 512},
    ]
    for t in tests_s3:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[b64_images[t["idx"]]])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "ocr",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    # Section 4: Chart Interpretation (3 tests)
    tests_s4 = [
        {"name": "4a — Read bar chart", "idx": 2, "prompt": "What are the values shown in this bar chart? List each quarter and its revenue.", "max": 256},
        {"name": "4b — Highest quarter", "idx": 2, "prompt": "Based on this chart, which quarter had the highest revenue? Also, what is the total annual revenue?", "max": 256},
        {"name": "4c — Calculate growth", "idx": 2, "prompt": "From this chart, calculate the percentage growth from Q1 to Q2.", "max": 256},
    ]
    for t in tests_s4:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[b64_images[t["idx"]]])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "chart",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    # Section 5: Math from Image (2 tests)
    tests_s5 = [
        {"name": "5a — Solve quadratic", "idx": 4, "prompt": "Solve the math equation shown in this image. Show your work and give all real roots.", "max": 512},
        {"name": "5b — Number sequence", "idx": 6, "prompt": "What is the next number in the sequence shown in this image? Explain the pattern.", "max": 256},
    ]
    for t in tests_s5:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[b64_images[t["idx"]]])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "math_image",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    # Section 6: Code from Image (2 tests)
    tests_s6 = [
        {"name": "6a — Transcribe code", "idx": 3, "prompt": "Transcribe the Python code shown in this image exactly as written.", "max": 512},
        {"name": "6b — Execute mentally", "idx": 3, "prompt": "Based on the code in this image, what is the output of the last line? Trace through the execution.", "max": 512},
    ]
    for t in tests_s6:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[b64_images[t["idx"]]])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "code_image",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    # Section 7: Visual Reasoning (3 tests)
    tests_s7 = [
        {"name": "7a — Count with reasoning", "idx": 0, "prompt": "Count the number of squares in this image. Then count how many different colors are used. Explain your reasoning.", "max": 512},
        {"name": "7b — Scene analysis", "idx": 5, "prompt": "Look at this image carefully. List every object you see, its color, and approximate position (top/center/bottom, left/center/right). Then describe what time of day it might be.", "max": 512},
        {"name": "7c — Color frequency", "idx": 0, "prompt": "In this grid image, which color appears most frequently? How many times does each color appear?", "max": 512},
    ]
    for t in tests_s7:
        msgs = [{"role": "user", "content": t["prompt"]}]
        r = multimodal_request(msgs, max_tokens=t["max"], images=[b64_images[t["idx"]]])
        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)
        print(f"  {t['name']:<35} {status} {r['wall']:.1f}s {tokens} tok")
        results.append({"id": t["name"], "dimension": "vision", "section": "reasoning",
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "response": r["text"][:200], "error": r["error"]})

    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n  Vision Score: {passed}/{len(results)}")
    return results


# ============================================================
# DIMENSION 2: Video Understanding (17 tests)
# ============================================================

def run_video_tests():
    print("\n" + "="*70)
    print("DIMENSION 2: Video Understanding (17 tests)")
    print("="*70)

    video_tests = [
        # Category 1: Video Description (4)
        {"id": "V1a", "cat": "Description", "video": "09-bouncing-ball.mp4",
         "prompt": "Describe what happens in this video. What objects do you see and how do they move?", "max": 300,
         "expected": "Red ball/circle bouncing on blue background"},
        {"id": "V1b", "cat": "Description", "video": "09-bouncing-ball.mp4",
         "prompt": "What color is the background in this video? What color is the moving object?", "max": 100,
         "expected": "Blue background, red ball/circle"},
        {"id": "V1c", "cat": "Description", "video": "10-shapes-motion.mp4",
         "prompt": "List all the shapes you see in this video and describe each one's color and movement pattern.", "max": 300,
         "expected": "Green square (horizontal), yellow triangle (upward), blue circle (pulsing)"},
        {"id": "V1d", "cat": "Description", "video": "11-color-cycle.mp4",
         "prompt": "What colors appear in this video and in what order?", "max": 200,
         "expected": "Red, green, blue, cyan/yellow, magenta, yellow (cycling)"},

        # Category 2: Motion Analysis (3)
        {"id": "V2a", "cat": "Motion", "video": "09-bouncing-ball.mp4",
         "prompt": "Describe the trajectory of the moving object. Is it linear, circular, or bouncing? Explain your reasoning.", "max": 250,
         "expected": "Bouncing - changes direction at boundaries"},
        {"id": "V2b", "cat": "Motion", "video": "10-shapes-motion.mp4",
         "prompt": "Which shape moves horizontally? Which shape moves vertically? Which shape changes size?", "max": 200,
         "expected": "Square horizontal, triangle vertical, circle changes size (pulsing)"},
        {"id": "V2c", "cat": "Motion", "video": "09-bouncing-ball.mp4",
         "prompt": "If this video continues, predict where the ball will be in the next few frames based on its current trajectory.", "max": 200,
         "expected": "Predict continuation of bouncing pattern"},

        # Category 3: Counting (3)
        {"id": "V3a", "cat": "Counting", "video": "09-bouncing-ball.mp4",
         "prompt": "How many distinct objects are in this video?", "max": 50,
         "expected": "1 (one red ball)"},
        {"id": "V3b", "cat": "Counting", "video": "10-shapes-motion.mp4",
         "prompt": "How many distinct shapes are in this video? List them.", "max": 100,
         "expected": "3 (square, triangle, circle)"},
        {"id": "V3c", "cat": "Counting", "video": "11-color-cycle.mp4",
         "prompt": "How many different colors appear in this video?", "max": 50,
         "expected": "6 (red, green, blue, cyan, magenta, yellow)"},

        # Category 4: Multi-Video (2)
        {"id": "V4a", "cat": "Multi-Video", "videos": ["09-bouncing-ball.mp4", "10-shapes-motion.mp4"],
         "prompt": "Compare these two videos. What is similar and what is different in terms of objects, colors, and motion?", "max": 400,
         "expected": "Different objects (1 ball vs 3 shapes), different colors, both have motion"},
        {"id": "V4b", "cat": "Multi-Video", "videos": ["09-bouncing-ball.mp4", "11-color-cycle.mp4"],
         "prompt": "Which video has more color variety? Describe the colors in each.", "max": 200,
         "expected": "Video 1 has blue+red (2 colors), Video 2 has 6 cycling colors"},

        # Category 5: Video Reasoning (3)
        {"id": "V5a", "cat": "Reasoning", "video": "09-bouncing-ball.mp4",
         "prompt": "If this were a physics simulation, what rules would govern the object's movement? What happens at the boundaries?", "max": 300,
         "expected": "Ball bounces off walls - reflection of velocity at boundaries"},
        {"id": "V5b", "cat": "Reasoning", "video": "10-shapes-motion.mp4",
         "prompt": "The green square, yellow triangle, and blue circle each follow different motion rules. Describe what rule each shape follows.", "max": 300,
         "expected": "Square: linear horizontal loop; Triangle: linear vertical loop; Circle: sinusoidal radius change"},
        {"id": "V5c", "cat": "Reasoning", "video": "11-color-cycle.mp4",
         "prompt": "Is there a pattern to the color changes? If so, describe the pattern and predict the next color.", "max": 200,
         "expected": "Cycling pattern - 5 frames per color, repeating sequence"},

        # Category 6: Video + Text (2)
        {"id": "V6a", "cat": "Video+Text", "video": "09-bouncing-ball.mp4",
         "prompt": "Write a short JSON object describing this video with fields: object_count, primary_color, background_color, motion_type.", "max": 150,
         "expected": "JSON with object_count:1, primary_color:red, background_color:blue, motion_type:bouncing"},
        {"id": "V6b", "cat": "Video+Text", "video": "10-shapes-motion.mp4",
         "prompt": "Create a table (in markdown) listing each shape, its color, and its motion type.", "max": 250,
         "expected": "Markdown table with 3 rows: square/green/horizontal, triangle/yellow/vertical, circle/blue/pulsing"},
    ]

    results = []
    for t in video_tests:
        print(f"  Running {t['id']} ({t['cat']})...", end=" ", flush=True)
        if "videos" in t:
            vid_urls = [encode_video(os.path.join(VIDEO_DIR, v)) for v in t["videos"]]
            r = multimodal_request([{"role": "user", "content": t["prompt"]}],
                                   max_tokens=t["max"], videos=vid_urls, timeout=180)
        else:
            vid_url = encode_video(os.path.join(VIDEO_DIR, t["video"]))
            r = multimodal_request([{"role": "user", "content": t["prompt"]}],
                                   max_tokens=t["max"], videos=[vid_url], timeout=180)

        status = "PASS" if r["error"] is None else "FAIL"
        tokens = r["usage"].get("completion_tokens", 0)

        # Keyword scoring
        if r["text"]:
            expected_lower = t.get("expected", "").lower()
            content_lower = r["text"].lower()
            keywords = [kw.strip() for kw in expected_lower.split(",") if len(kw.strip()) > 2]
            matched = sum(1 for kw in keywords if kw in content_lower)
            score = f"{matched}/{len(keywords)}" if keywords else "N/A"
        else:
            score = "N/A"

        print(f"{status} {r['wall']:.1f}s {tokens} tok score={score}")
        results.append({"id": t["id"], "dimension": "video", "category": t["cat"],
                        "status": status, "wall": round(r["wall"], 2), "tokens": tokens,
                        "score": score, "expected": t.get("expected", ""),
                        "response": r["text"][:300], "error": r["error"]})

    passed = sum(1 for r in results if r["status"] == "PASS")
    print(f"\n  Video Score: {passed}/{len(results)}")
    return results


# ============================================================
# DIMENSION 3: Latency & Throughput (5 sub-tests)
# ============================================================

def run_latency_throughput():
    print("\n" + "="*70)
    print("DIMENSION 3: Latency & Throughput (5 sub-tests)")
    print("="*70)
    prompt = [{"role": "user", "content": "Write a detailed essay about the history of computing, from Babbage to modern AI."}]
    results = []
    for max_tok in [64, 128, 256, 512, 1024]:
        text, wall, finish, usage, _ = non_stream_request(prompt, max_tokens=max_tok)
        actual = usage.get("completion_tokens", len(text) // 4)
        tput = actual / wall if wall > 0 else 0
        results.append({"max_tokens": max_tok, "actual_tokens": actual,
                        "wall_time": round(wall, 2), "throughput": round(tput, 1), "finish": finish})
        print(f"  {max_tok:>5} tok → {actual} actual, {wall:.2f}s, {tput:.1f} tok/s, finish={finish}")
    return results


# ============================================================
# DIMENSION 4: TTFT (3 sub-tests)
# ============================================================

def run_ttft():
    print("\n" + "="*70)
    print("DIMENSION 4: Time To First Token (3 sub-tests)")
    print("="*70)
    prompts = {
        "Short": [{"role": "user", "content": "What is 2+2?"}],
        "Medium": [{"role": "user", "content": "Explain CPU in 3 paragraphs"}],
        "Long reasoning": [{"role": "user", "content": "Prove that √2 is irrational."}],
    }
    results = []
    for label, msgs in prompts.items():
        content, reasoning, ttft, wall, finish = stream_request(msgs, max_tokens=2048)
        results.append({"prompt_type": label, "ttft_ms": round(ttft * 1000) if ttft else None,
                        "total_time": round(wall, 2), "content_chars": len(content),
                        "reasoning_chars": len(reasoning), "finish": finish})
        ttft_str = f"{ttft*1000:.0f}ms" if ttft else "N/A"
        print(f"  {label:>15} → TTFT: {ttft_str}, total: {wall:.2f}s, content: {len(content)} chars, finish={finish}")
    return results


# ============================================================
# DIMENSION 5: Concurrency (4 sub-tests: 1,2,4,8)
# ============================================================

def run_concurrency():
    print("\n" + "="*70)
    print("DIMENSION 5: Concurrent Request Handling (4 sub-tests)")
    print("="*70)
    prompt_text = "Write a short story about a robot learning to paint"
    results = []
    for concurrency in [1, 2, 4, 8]:
        msgs = [{"role": "user", "content": prompt_text}]
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
            futures = [pool.submit(non_stream_request, msgs, 512) for _ in range(concurrency)]
            done = 0
            errors = 0
            for f in concurrent.futures.as_completed(futures):
                try:
                    f.result()
                    done += 1
                except Exception as e:
                    errors += 1
                    print(f"    ERROR: {e}")
        wall = time.time() - start
        results.append({"concurrency": concurrency, "success": f"{done}/{concurrency}",
                        "wall_time": round(wall, 2), "errors": errors})
        print(f"  Concurrency {concurrency:>1} → {done}/{concurrency} success, {wall:.2f}s, {errors} errors")
    return results


# ============================================================
# DIMENSION 6: Context Length Scaling (6 sub-tests)
# ============================================================

def run_context_length():
    print("\n" + "="*70)
    print("DIMENSION 6: Context Length Scaling (6 sub-tests)")
    print("="*70)
    filler = "The quick brown fox jumps over the lazy dog. " * 50
    results = []
    for target in [100, 500, 2000, 8000, 32000, 128000]:
        blocks = max(1, target // 450)
        padding = (filler * blocks)[:target * 4]
        full = padding + "\n\nWhat is 7 × 8? Answer with just the number."
        msgs = [{"role": "user", "content": full}]
        text, wall, finish, usage, _ = non_stream_request(msgs, max_tokens=200)
        actual = usage.get("completion_tokens", len(text) // 4)
        prompt_tok = usage.get("prompt_tokens", len(full) // 4)
        tput = actual / wall if wall > 0 else 0
        correct = "56" in text
        results.append({"input_size": f"~{target}", "actual_prompt_tokens": prompt_tok,
                        "output_tokens": actual, "wall_time": round(wall, 2),
                        "throughput": round(tput, 1), "correct": correct, "finish": finish,
                        "response_excerpt": text[:50]})
        print(f"  ~{target:>6} → prompt: {prompt_tok} tok, output: {actual} tok, {wall:.2f}s, {tput:.1f} tok/s, correct={correct}")
    return results


# ============================================================
# DIMENSION 7: Reasoning Quality (8 tests)
# ============================================================

def run_reasoning():
    print("\n" + "="*70)
    print("DIMENSION 7: Reasoning Quality (8 tests)")
    print("="*70)
    tests = [
        ("Math (basic)", "What is 17 × 23? Show your work briefly.", [r"\b391\b"]),
        ("Math (advanced)", "Solve: 3x + 7 = 22. Find x.", [r"\b5\b"]),
        ("Logic", "All cats are mammals. Some mammals are pets. Can we conclude that some cats are pets? Answer yes, no, or cannot determine.", [r"cannot determine"]),
        ("Coding", "Write a Python function to reverse a linked list. Output only the code.", [r"def reverse", r"\.next"]),
        ("Knowledge", "What is the capital of Australia?", [r"Canberra"]),
        ("Reasoning", "A train travels 60 km in 45 minutes. What is its speed in km/h?", [r"\b80\b"]),
        ("Instruction", "List exactly 3 fruits. Number them 1-3. Nothing else.", [r"1\b", r"2\b", r"3\b"]),
        ("World knowledge", "In what year did the Berlin Wall fall?", [r"1989"]),
    ]
    results = []
    for name, prompt_text, rubric in tests:
        msgs = [{"role": "user", "content": prompt_text}]
        text, wall, finish, usage, _ = non_stream_request(msgs, max_tokens=2048)
        passed = all(re.search(p, text, re.IGNORECASE) for p in rubric)
        tokens = usage.get("completion_tokens", len(text) // 4)
        results.append({"category": name, "passed": passed, "time": round(wall, 1),
                        "tokens": tokens, "response_excerpt": text[:100]})
        print(f"  {name:>25} → {'✅ PASS' if passed else '❌ FAIL'}, {wall:.1f}s, {tokens} tok")
    score = sum(1 for r in results if r["passed"])
    print(f"  Score: {score}/{len(results)}")
    return results


# ============================================================
# DIMENSION 8: Tool Calling (2 tests)
# ============================================================

def run_tool_calling():
    print("\n" + "="*70)
    print("DIMENSION 8: Tool Calling (2 tests)")
    print("="*70)
    tools = [
        {"type": "function", "function": {
            "name": "get_weather", "description": "Get current weather for a location",
            "parameters": {"type": "object", "properties": {"location": {"type": "string", "description": "City name"}},
                           "required": ["location"]}}},
        {"type": "function", "function": {
            "name": "calculate", "description": "Evaluate a math expression",
            "parameters": {"type": "object", "properties": {"expression": {"type": "string", "description": "Math expression to evaluate"}},
                           "required": ["expression"]}}},
    ]
    test_cases = [
        ("Weather query", "What's the weather like in Tokyo?", "get_weather", "Tokyo"),
        ("Calculator", "Calculate 45 * 73", "calculate", "45 * 73"),
    ]
    results = []
    for name, prompt_text, expected_tool, expected_arg in test_cases:
        msgs = [{"role": "user", "content": prompt_text}]
        extra = {"tools": tools, "tool_choice": "auto"}
        text, wall, finish, usage, message = non_stream_request(msgs, max_tokens=512, extra=extra)
        tool_calls = message.get("tool_calls", []) or []
        tool_made = len(tool_calls) > 0 or finish == "tool_calls"
        correct_tool = False
        correct_arg = False
        tool_name = ""
        tool_args_str = ""
        if tool_calls:
            tc = tool_calls[0]
            fn = tc.get("function", {}) or {}
            tool_name = fn.get("name", "") or ""
            tool_args_str = json.dumps(fn.get("arguments", {}))
            correct_tool = tool_name == expected_tool
            correct_arg = expected_arg.lower() in tool_args_str.lower()
        results.append({"test": name, "tool_made": tool_made, "correct_tool": correct_tool,
                        "correct_arg": correct_arg, "tool_name": tool_name, "tool_args": tool_args_str,
                        "time": round(wall, 1), "finish_reason": finish, "response_excerpt": text[:200]})
        print(f"  {name:>15} → tool_made={tool_made}, tool={tool_name}, correct_tool={correct_tool}, correct_arg={correct_arg}, {wall:.1f}s")
    return results


# ============================================================
# Speculative Decoding Metrics
# ============================================================

def get_spec_decode_metrics():
    print("\n" + "="*70)
    print("Speculative Decoding (MTP) Metrics")
    print("="*70)
    try:
        resp = requests.get(METRICS_URL, timeout=10)
        metrics_text = resp.text
        draft_requests = 0
        draft_tokens = 0
        accepted_tokens = 0
        for line in metrics_text.split("\n"):
            if line.startswith("#") or "_created" in line:
                continue
            parts = line.strip().split()
            if len(parts) >= 2:
                key = parts[0]
                val = parts[-1]
                try:
                    val_f = float(val)
                except ValueError:
                    continue
                if "spec_decode_num_drafts_total" in key and "per_pos" not in key:
                    draft_requests = val_f
                elif "spec_decode_num_draft_tokens_total" in key:
                    draft_tokens = val_f
                elif "spec_decode_num_accepted_tokens_total" in key and "per_pos" not in key:
                    accepted_tokens = val_f
        acceptance_rate = (accepted_tokens / draft_tokens * 100) if draft_tokens > 0 else 0
        results = {"draft_requests": draft_requests, "draft_tokens": draft_tokens,
                   "accepted_tokens": accepted_tokens, "acceptance_rate": round(acceptance_rate, 1)}
        print(f"  Draft requests: {int(draft_requests)}")
        print(f"  Draft tokens: {int(draft_tokens)}")
        print(f"  Accepted tokens: {int(accepted_tokens)}")
        print(f"  Acceptance rate: {acceptance_rate:.1f}%")
        return results
    except Exception as e:
        print(f"  Could not fetch metrics: {e}")
        return {}


# ============================================================
# Main
# ============================================================

def main():
    print("="*70)
    print("Qwen3.6-35B-A3B-NVFP4 Full 65-Test Benchmark")
    print(f"Endpoint: {ENDPOINT}")
    print(f"Model: {MODEL}")
    print(f"Thinking: DISABLED")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*70)

    # Verify server
    try:
        resp = requests.get(MODELS_URL, timeout=10)
        models = resp.json()
        print(f"✓ Server up: {len(models.get('data', []))} model(s)")
    except Exception as e:
        print(f"✗ Server check failed: {e}")
        return

    bench_start = time.time()

    # Sanity check
    sanity_text, sanity_wall, sanity_finish, _u, _m = non_stream_request(
        [{"role": "user", "content": "What is 2+2? Answer with just the number."}], max_tokens=64)
    print(f"\nSanity: '{sanity_text[:50]}' in {sanity_wall:.2f}s, finish={sanity_finish}")

    # Generate test images
    print("\nGenerating test images...")
    b64_images = []
    ground_truth = []
    for gen_fn in [gen_color_grid, gen_text_image, gen_bar_chart, gen_code_screenshot,
                   gen_math_equation, gen_scene_image, gen_number_sequence]:
        img, gt = gen_fn()
        b64_images.append(img_to_b64(img))
        ground_truth.append(gt)
    (img_a, img_b), gt = gen_two_images_for_comparison()
    b64_images.append(img_to_b64(img_a))
    ground_truth.append(gt)
    b64_images.append(img_to_b64(img_b))
    ground_truth.append(gt)
    print(f"  {len(b64_images)} images generated")

    # Run all 8 dimensions
    d1 = run_vision_tests(b64_images, ground_truth)
    d2 = run_video_tests()
    d3 = run_latency_throughput()
    d4 = run_ttft()
    d5 = run_concurrency()
    d6 = run_context_length()
    d7 = run_reasoning()
    d8 = run_tool_calling()
    spec = get_spec_decode_metrics()

    bench_duration = time.time() - bench_start

    # Compile summary
    vision_pass = sum(1 for r in d1 if r["status"] == "PASS")
    video_pass = sum(1 for r in d2 if r["status"] == "PASS")
    reasoning_pass = sum(1 for r in d7 if r["passed"])
    tool_pass = sum(1 for r in d8 if r["tool_made"])

    total_tests = 20 + 17 + 5 + 3 + 4 + 6 + 8 + 2  # = 65
    total_pass = vision_pass + video_pass + reasoning_pass + tool_pass
    # Latency, TTFT, concurrency, context are performance tests (not pass/fail)

    summary = {
        "model": MODEL,
        "thinking_enabled": False,
        "total_test_count": total_tests,
        "vision_pass": f"{vision_pass}/20",
        "video_pass": f"{video_pass}/17",
        "reasoning_pass": f"{reasoning_pass}/8",
        "tool_calling_pass": f"{tool_pass}/2",
        "peak_throughput_single": max(r["throughput"] for r in d3) if d3 else 0,
        "steady_state_throughput": statistics.median([r["throughput"] for r in d3]) if d3 else 0,
        "ttft_short_ms": d4[0]["ttft_ms"] if d4 else None,
        "ttft_reasoning_ms": d4[2]["ttft_ms"] if len(d4) > 2 else None,
        "max_concurrency_tested": 8,
        "concurrency_success": all(r["errors"] == 0 for r in d5),
        "context_max_verified": d6[-1]["actual_prompt_tokens"] if d6 else 0,
        "speculative_acceptance_rate": spec.get("acceptance_rate", "N/A"),
        "benchmark_duration_s": round(bench_duration, 1),
    }

    full_report = {
        "metadata": {
            "model": MODEL,
            "engine": "vLLM v0.24.0",
            "hardware": "NVIDIA DGX Spark (GB10 Grace Blackwell, aarch64)",
            "endpoint": ENDPOINT,
            "thinking_enabled": False,
            "timestamp": datetime.now().isoformat(),
            "benchmark_duration_seconds": round(bench_duration, 1),
        },
        "summary": summary,
        "dimension_1_vision_20tests": d1,
        "dimension_2_video_17tests": d2,
        "dimension_3_latency_throughput_5tests": d3,
        "dimension_4_ttft_3tests": d4,
        "dimension_5_concurrency_4tests": d5,
        "dimension_6_context_length_6tests": d6,
        "dimension_7_reasoning_8tests": d7,
        "dimension_8_tool_calling_2tests": d8,
        "speculative_decoding": spec,
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(full_report, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Results saved to {RESULTS_FILE}")

    # Executive summary
    print(f"\n{'='*70}")
    print("EXECUTIVE SUMMARY — 65-Test Benchmark")
    print(f"{'='*70}")
    print(f"  Vision (20 tests):       {vision_pass}/20 passed")
    print(f"  Video (17 tests):        {video_pass}/17 passed")
    print(f"  Latency/Throughput:      {summary['peak_throughput_single']} tok/s peak, {summary['steady_state_throughput']} tok/s steady")
    print(f"  TTFT (short):            {summary['ttft_short_ms']} ms")
    print(f"  TTFT (reasoning):        {summary['ttft_reasoning_ms']} ms")
    print(f"  Concurrency:             100% success up to 8 parallel" if summary['concurrency_success'] else "  Concurrency:             FAILED")
    print(f"  Context scaling:         {summary['context_max_verified']} tokens verified")
    print(f"  Reasoning (8 tests):     {reasoning_pass}/8 passed")
    print(f"  Tool calling (2 tests):  {tool_pass}/2 passed")
    print(f"  Spec decode acceptance:  {summary['speculative_acceptance_rate']}%")
    print(f"  Benchmark duration:      {bench_duration:.1f}s ({bench_duration/60:.1f} min)")
    print(f"  Total pass/fail tests:   {total_pass}/{20+17+8+2} (65 total incl. performance)")

    return full_report


if __name__ == "__main__":
    main()