#!/usr/bin/env python3
"""
Qwen3.6-27B-NVFP4 Multimodal Benchmark
Tests vision/image understanding capabilities via vLLM OpenAI-compatible API.

Server: spark-56bc:8888
Model: nvidia/Qwen3.6-27B-NVFP4 (Qwen3_5ForConditionalGeneration)

Test sections:
1. Single image understanding (description, detail, counting)
2. Multiple images (comparison, relationship)
3. OCR / text extraction from images
4. Chart/diagram interpretation
5. Code reading from screenshots
6. Math problem from image
7. Image reasoning / logic
8. Performance metrics (TTFT, throughput, token counts)

All images generated locally as PNG using PIL/matplotlib to avoid
external dependencies.
"""

import json
import time
import base64
import io
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

# --- Configuration ---
BASE_URL = "http://spark-56bc:8888/v1"
MODEL = "nvidia/Qwen3.6-27B-NVFP4"
THINKING_OFF = {"chat_template_kwargs": {"enable_thinking": False}}
OUTPUT_DIR = Path("/home/mikesai1/NemoVault/queries")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# --- Helpers ---

def make_request(messages, max_tokens=1024, temperature=0.6, images=None):
    """Send a chat completion request. Returns (response_dict, elapsed_seconds)."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 0.95,
        "extra_body": THINKING_OFF,
    }
    
    # Add images if provided (inline base64)
    if images:
        # Images is a list of base64 strings
        # The last user message should have image content
        # We need to restructure the last user message
        last_msg = payload["messages"][-1]
        if last_msg["role"] == "user":
            content = []
            for img_b64 in images:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{img_b64}"}
                })
            content.append({"type": "text", "text": last_msg["content"]})
            last_msg["content"] = content
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        elapsed = time.time() - start
        error_body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}", "details": error_body[:500]}, elapsed
    except Exception as e:
        elapsed = time.time() - start
        return {"error": str(e)}, elapsed
    
    elapsed = time.time() - start
    return result, elapsed


def img_to_b64(pil_image, format="PNG"):
    """Convert a PIL image to base64 string."""
    buf = io.BytesIO()
    pil_image.save(buf, format=format)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def extract_response(result):
    """Extract text and usage from API response."""
    if "error" in result:
        return {"error": result["error"], "details": result.get("details", "")}
    
    try:
        choice = result["choices"][0]
        msg = choice["message"]
        text = msg.get("content", "")
        reasoning = msg.get("reasoning_content", "")
        
        usage = result.get("usage", {})
        
        return {
            "text": text,
            "reasoning": reasoning,
            "finish_reason": choice.get("finish_reason", ""),
            "usage": {
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
            },
        }
    except (KeyError, IndexError) as e:
        return {"error": f"Parse error: {e}", "raw": json.dumps(result)[:500]}


# --- Image Generators ---
# We generate test images locally using PIL to avoid network dependencies.

def gen_color_grid():
    """Generate a 4x4 grid of colored squares for counting/color recognition."""
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
    """Generate an image with text for OCR testing."""
    from PIL import Image, ImageDraw, ImageFont
    
    img = Image.new("RGB", (600, 200), "white")
    draw = ImageDraw.Draw(img)
    
    lines = [
        "The quick brown fox jumps over the lazy dog.",
        "Hermes Agent v2.1.0 - Build #4832",
        "API_KEY: sk-test-1234-5678-90ab",
        "Date: 2026-07-03  Temperature: 72°F",
    ]
    
    y = 20
    for line in lines:
        draw.text((20, y), line, fill="black")
        y += 40
    
    return img, "4 lines of text: fox sentence, Hermes version, API key, date/temp"


def gen_bar_chart():
    """Generate a simple bar chart for chart interpretation."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(6, 4), dpi=100)
    categories = ["Q1", "Q2", "Q3", "Q4"]
    values = [120, 185, 95, 210]
    colors = ["#4CAF50", "#2196F3", "#FF9800", "#9C27B0"]
    
    bars = ax.bar(categories, values, color=colors)
    ax.set_ylabel("Revenue ($K)")
    ax.set_title("Quarterly Revenue 2025")
    ax.set_ylim(0, 250)
    
    # Add value labels on bars
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                f"${val}K", ha="center", va="bottom", fontsize=11, fontweight="bold")
    
    plt.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100)
    plt.close(fig)
    img = Image.open(buf) if False else None  # We'll use buf directly
    
    from PIL import Image
    buf.seek(0)
    pil_img = Image.open(buf)
    
    return pil_img, "Bar chart: Q1=$120K, Q2=$185K, Q3=$95K, Q4=$210K"


def gen_code_screenshot():
    """Generate an image that looks like a code editor with Python code."""
    from PIL import Image, ImageDraw, ImageFont
    
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
    
    img = Image.new("RGB", (520, 280), (30, 30, 30))  # Dark background
    draw = ImageDraw.Draw(img)
    
    # Draw code with syntax-highlighting colors
    y = 15
    for i, line in enumerate(code_lines):
        color = (200, 200, 200)  # Default gray
        if line.startswith("def "):
            color = (86, 156, 214)  # Blue for function
        elif line.startswith("    return"):
            color = (78, 201, 176)  # Green for return
        elif line.startswith("result") or line.startswith("print"):
            color = (206, 145, 120)  # Orange for variables
        elif "fibonacci" in line:
            color = (220, 220, 170)  # Yellow for function calls
        draw.text((15, y), line, fill=color)
        y += 25
    
    return img, "Python code: fibonacci function, fib(10) call, print result"


def gen_math_equation():
    """Generate an image with a math equation to solve."""
    from PIL import Image, ImageDraw
    
    img = Image.new("RGB", (500, 150), "white")
    draw = ImageDraw.Draw(img)
    
    # Write a math problem
    draw.text((30, 30), "Solve for x:", fill="black")
    draw.text((30, 70), "3x² - 12x + 9 = 0", fill="black")
    draw.text((30, 105), "Find all real roots.", fill="black")
    
    return img, "Quadratic equation: 3x² - 12x + 9 = 0, roots x=1 and x=3"


def gen_scene_image():
    """Generate a simple geometric scene for spatial reasoning."""
    from PIL import Image, ImageDraw
    
    img = Image.new("RGB", (500, 400), "white")
    draw = ImageDraw.Draw(img)
    
    # Draw a sun (circle) in top right
    draw.ellipse([380, 30, 460, 110], fill="yellow", outline="orange", width=2)
    
    # Draw a house (rectangle + triangle roof)
    draw.rectangle([150, 200, 300, 350], fill="#8B4513", outline="black", width=2)
    draw.polygon([(140, 200), (225, 120), (310, 200)], fill="red", outline="black")
    # Door
    draw.rectangle([210, 270, 240, 350], fill="#4A3520", outline="black")
    # Window
    draw.rectangle([165, 220, 195, 250], fill="lightblue", outline="black")
    draw.rectangle([255, 220, 285, 250], fill="lightblue", outline="black")
    
    # Draw a tree (trunk + circle canopy)
    draw.rectangle([60, 250, 80, 350], fill="#4A3520", outline="black")
    draw.ellipse([30, 170, 110, 260], fill="green", outline="darkgreen", width=2)
    
    # Draw grass
    draw.rectangle([0, 350, 500, 400], fill="lightgreen")
    
    return img, "Scene: sun top-right, house center (brown walls, red roof, blue windows, dark door), tree left (green canopy, brown trunk), grass at bottom"


def gen_number_sequence():
    """Generate an image with a number sequence puzzle."""
    from PIL import Image, ImageDraw
    
    img = Image.new("RGB", (600, 100), "white")
    draw = ImageDraw.Draw(img)
    
    draw.text((30, 30), "2, 6, 12, 20, 30, ?", fill="black")
    
    return img, "Number sequence: 2, 6, 12, 20, 30, ? — answer is 42 (n*(n+1))"


def gen_two_images_for_comparison():
    """Generate two different images for multi-image comparison."""
    from PIL import Image, ImageDraw
    
    # Image 1: red square
    img1 = Image.new("RGB", (300, 300), "white")
    draw1 = ImageDraw.Draw(img1)
    draw1.rectangle([50, 50, 250, 250], fill="red", outline="black", width=3)
    draw1.text((100, 280), "Image A", fill="black")
    
    # Image 2: blue circle
    img2 = Image.new("RGB", (300, 300), "white")
    draw2 = ImageDraw.Draw(img2)
    draw2.ellipse([50, 50, 250, 250], fill="blue", outline="black", width=3)
    draw2.text((100, 280), "Image B", fill="black")
    
    return (img1, img2), "Image A: red square, Image B: blue circle"


# --- Benchmark Sections ---

def section_1_single_image(b64_images, ground_truth):
    """Section 1: Single image understanding."""
    print("\n" + "="*70)
    print("SECTION 1: Single Image Understanding")
    print("="*70)
    results = []
    
    tests = [
        {
            "name": "1a — Describe the image",
            "image_idx": 0,  # color grid
            "prompt": "Describe what you see in this image in detail. What colors and shapes are present?",
            "max_tokens": 512,
        },
        {
            "name": "1b — Count objects",
            "image_idx": 0,  # color grid
            "prompt": "How many colored squares are in this image? Count them carefully.",
            "max_tokens": 256,
        },
        {
            "name": "1c — Identify specific colors",
            "image_idx": 0,  # color grid
            "prompt": "List all the unique colors you can see in this grid image.",
            "max_tokens": 256,
        },
        {
            "name": "1d — Scene description",
            "image_idx": 5,  # scene image (sun, house, tree)
            "prompt": "Describe this scene in detail. What objects do you see, their positions, and colors?",
            "max_tokens": 512,
        },
        {
            "name": "1e — Spatial reasoning",
            "image_idx": 5,  # scene image
            "prompt": "In this image, what is the position of the sun relative to the house? Is the tree to the left or right of the house?",
            "max_tokens": 256,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        img_b64 = b64_images[test["image_idx"]]
        messages = [{"role": "user", "content": test["prompt"]}]
        
        t0 = time.time()
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_b64])
        resp = extract_response(result)
        t1 = time.time()
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": ground_truth[test["image_idx"]],
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']} — {resp.get('details', '')[:100]}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_2_multiple_images(b64_images, ground_truth):
    """Section 2: Multiple image comparison."""
    print("\n" + "="*70)
    print("SECTION 2: Multiple Image Comparison")
    print("="*70)
    results = []
    
    # Get the comparison pair
    img_a_b64 = b64_images[len(b64_images) - 2]
    img_b_b64 = b64_images[len(b64_images) - 1]
    
    tests = [
        {
            "name": "2a — Compare two images",
            "prompt": "I'm showing you two images. Describe the differences between Image A and Image B. What shape and color is each?",
            "max_tokens": 512,
        },
        {
            "name": "2b — Which image has a circle?",
            "prompt": "Between these two images, which one contains a circle? Answer with 'Image A' or 'Image B'.",
            "max_tokens": 128,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        messages = [{"role": "user", "content": test["prompt"]}]
        
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_a_b64, img_b_b64])
        resp = extract_response(result)
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": "Image A=red square, Image B=blue circle",
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_3_ocr(b64_images, ground_truth):
    """Section 3: OCR / text extraction."""
    print("\n" + "="*70)
    print("SECTION 3: OCR / Text Extraction")
    print("="*70)
    results = []
    
    tests = [
        {
            "name": "3a — Read text from image",
            "image_idx": 1,  # text image
            "prompt": "Read and transcribe all the text you can see in this image. Output each line separately.",
            "max_tokens": 512,
        },
        {
            "name": "3b — Extract specific info",
            "image_idx": 1,  # text image
            "prompt": "What is the API key shown in this image? Extract only the API key value.",
            "max_tokens": 128,
        },
        {
            "name": "3c — Read code from screenshot",
            "image_idx": 3,  # code screenshot
            "prompt": "Read the code in this image and transcribe it. What function is defined and what is the expected output?",
            "max_tokens": 512,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        img_b64 = b64_images[test["image_idx"]]
        messages = [{"role": "user", "content": test["prompt"]}]
        
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_b64])
        resp = extract_response(result)
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": ground_truth[test["image_idx"]],
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_4_chart_interpretation(b64_images, ground_truth):
    """Section 4: Chart/diagram interpretation."""
    print("\n" + "="*70)
    print("SECTION 4: Chart / Diagram Interpretation")
    print("="*70)
    results = []
    
    tests = [
        {
            "name": "4a — Read bar chart values",
            "image_idx": 2,  # bar chart
            "prompt": "What are the values shown in this bar chart? List each quarter and its revenue.",
            "max_tokens": 256,
        },
        {
            "name": "4b — Which quarter has highest revenue?",
            "image_idx": 2,
            "prompt": "Based on this chart, which quarter had the highest revenue? Also, what is the total annual revenue?",
            "max_tokens": 256,
        },
        {
            "name": "4c — Calculate from chart",
            "image_idx": 2,
            "prompt": "From this chart, calculate the percentage growth from Q1 to Q2.",
            "max_tokens": 256,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        img_b64 = b64_images[test["image_idx"]]
        messages = [{"role": "user", "content": test["prompt"]}]
        
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_b64])
        resp = extract_response(result)
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": ground_truth[test["image_idx"]],
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_5_math_from_image(b64_images, ground_truth):
    """Section 5: Math problem from image."""
    print("\n" + "="*70)
    print("SECTION 5: Math Problem from Image")
    print("="*70)
    results = []
    
    tests = [
        {
            "name": "5a — Solve quadratic from image",
            "image_idx": 4,  # math equation
            "prompt": "Solve the math equation shown in this image. Show your work and give all real roots.",
            "max_tokens": 512,
        },
        {
            "name": "5b — Number sequence",
            "image_idx": 6,  # number sequence
            "prompt": "What is the next number in the sequence shown in this image? Explain the pattern.",
            "max_tokens": 256,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        img_b64 = b64_images[test["image_idx"]]
        messages = [{"role": "user", "content": test["prompt"]}]
        
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_b64])
        resp = extract_response(result)
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": ground_truth[test["image_idx"]],
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_6_code_from_image(b64_images, ground_truth):
    """Section 6: Code reading and execution from image."""
    print("\n" + "="*70)
    print("SECTION 6: Code Reading from Image")
    print("="*70)
    results = []
    
    tests = [
        {
            "name": "6a — Transcribe code",
            "image_idx": 3,  # code screenshot
            "prompt": "Transcribe the Python code shown in this image exactly as written.",
            "max_tokens": 512,
        },
        {
            "name": "6b — Execute code mentally",
            "image_idx": 3,
            "prompt": "Based on the code in this image, what is the output of the last line? Trace through the execution.",
            "max_tokens": 512,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        img_b64 = b64_images[test["image_idx"]]
        messages = [{"role": "user", "content": test["prompt"]}]
        
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_b64])
        resp = extract_response(result)
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": ground_truth[test["image_idx"]],
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_7_reasoning(b64_images, ground_truth):
    """Section 7: Visual reasoning and logic."""
    print("\n" + "="*70)
    print("SECTION 7: Visual Reasoning & Logic")
    print("="*70)
    results = []
    
    tests = [
        {
            "name": "7a — Object counting with reasoning",
            "image_idx": 0,  # color grid
            "prompt": "Count the number of squares in this image. Then count how many different colors are used. Explain your reasoning.",
            "max_tokens": 512,
        },
        {
            "name": "7b — Scene analysis",
            "image_idx": 5,  # scene
            "prompt": "Look at this image carefully. List every object you see, its color, and approximate position (top/center/bottom, left/center/right). Then describe what time of day it might be.",
            "max_tokens": 512,
        },
        {
            "name": "7c — Color frequency",
            "image_idx": 0,  # color grid
            "prompt": "In this grid image, which color appears most frequently? How many times does each color appear?",
            "max_tokens": 512,
        },
    ]
    
    for test in tests:
        print(f"\n  Running {test['name']}...")
        img_b64 = b64_images[test["image_idx"]]
        messages = [{"role": "user", "content": test["prompt"]}]
        
        result, elapsed = make_request(messages, max_tokens=test["max_tokens"], images=[img_b64])
        resp = extract_response(result)
        
        entry = {
            "test": test["name"],
            "elapsed": round(elapsed, 3),
            "response": resp,
            "ground_truth": ground_truth[test["image_idx"]],
        }
        results.append(entry)
        
        if "error" in resp:
            print(f"    ❌ ERROR: {resp['error']}")
        else:
            text_preview = resp["text"][:120].replace("\n", " ")
            print(f"    ✅ {resp['usage']['completion_tokens']} tokens in {elapsed:.2f}s")
            print(f"    Response: {text_preview}...")
    
    return results


def section_8_performance(all_results):
    """Section 8: Aggregate performance metrics."""
    print("\n" + "="*70)
    print("SECTION 8: Performance Summary")
    print("="*70)
    
    total_requests = 0
    total_prompt_tokens = 0
    total_completion_tokens = 0
    total_elapsed = 0
    errors = 0
    ttft_list = []  # We don't have TTFT from non-streaming, use total elapsed as proxy
    
    per_section = {}
    
    for section_name, section_results in all_results.items():
        section_tokens = 0
        section_elapsed = 0
        section_count = 0
        section_errors = 0
        
        for r in section_results:
            total_requests += 1
            section_count += 1
            total_elapsed += r["elapsed"]
            section_elapsed += r["elapsed"]
            
            resp = r["response"]
            if "error" in resp:
                errors += 1
                section_errors += 1
            else:
                usage = resp.get("usage", {})
                pt = usage.get("prompt_tokens", 0)
                ct = usage.get("completion_tokens", 0)
                total_prompt_tokens += pt
                total_completion_tokens += ct
                section_tokens += ct
        
        per_section[section_name] = {
            "requests": section_count,
            "errors": section_errors,
            "total_completion_tokens": section_tokens,
            "total_elapsed_s": round(section_elapsed, 2),
            "avg_elapsed_s": round(section_elapsed / max(section_count, 1), 2),
            "avg_tokens_per_s": round(section_tokens / max(section_elapsed, 0.01), 1),
        }
    
    summary = {
        "total_requests": total_requests,
        "total_errors": errors,
        "success_rate": round((total_requests - errors) / max(total_requests, 1) * 100, 1),
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_elapsed_s": round(total_elapsed, 2),
        "avg_elapsed_s": round(total_elapsed / max(total_requests, 1), 2),
        "avg_completion_tokens_per_s": round(total_completion_tokens / max(total_elapsed, 0.01), 1),
        "per_section": per_section,
    }
    
    print(f"\n  Total requests: {total_requests}")
    print(f"  Success rate: {summary['success_rate']}%")
    print(f"  Total prompt tokens: {total_prompt_tokens}")
    print(f"  Total completion tokens: {total_completion_tokens}")
    print(f"  Total elapsed: {total_elapsed:.2f}s")
    print(f"  Avg elapsed/request: {summary['avg_elapsed_s']}s")
    print(f"  Avg completion tok/s: {summary['avg_completion_tokens_per_s']}")
    
    print("\n  Per-section breakdown:")
    for name, stats in per_section.items():
        print(f"    {name}: {stats['requests']} reqs, {stats['errors']} errors, "
              f"{stats['total_completion_tokens']} tok, {stats['avg_elapsed_s']}s avg, "
              f"{stats['avg_tokens_per_s']} tok/s")
    
    return summary


# --- Main ---

def main():
    print("="*70)
    print("Qwen3.6-27B-NVFP4 Multimodal Benchmark")
    print(f"Server: {BASE_URL}")
    print(f"Model: {MODEL}")
    print(f"Thinking: OFF (server default)")
    print(f"Date: 2026-07-03")
    print("="*70)
    
    # Generate all test images
    print("\nGenerating test images...")
    from PIL import Image
    
    b64_images = []
    ground_truth = []
    
    # 0: color grid
    img, gt = gen_color_grid()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [0] Color grid: {img.size}")
    
    # 1: text image
    img, gt = gen_text_image()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [1] Text image: {img.size}")
    
    # 2: bar chart
    img, gt = gen_bar_chart()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [2] Bar chart: {img.size}")
    
    # 3: code screenshot
    img, gt = gen_code_screenshot()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [3] Code screenshot: {img.size}")
    
    # 4: math equation
    img, gt = gen_math_equation()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [4] Math equation: {img.size}")
    
    # 5: scene image
    img, gt = gen_scene_image()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [5] Scene image: {img.size}")
    
    # 6: number sequence
    img, gt = gen_number_sequence()
    b64_images.append(img_to_b64(img))
    ground_truth.append(gt)
    print(f"  [6] Number sequence: {img.size}")
    
    # 7,8: two images for comparison
    (img_a, img_b), gt = gen_two_images_for_comparison()
    b64_images.append(img_to_b64(img_a))
    ground_truth.append(gt)
    print(f"  [7] Comparison A: {img_a.size}")
    b64_images.append(img_to_b64(img_b))
    ground_truth.append(gt)
    print(f"  [8] Comparison B: {img_b.size}")
    
    print(f"\nTotal images generated: {len(b64_images)}")
    
    # Run all sections
    all_results = {}
    
    all_results["section_1_single_image"] = section_1_single_image(b64_images, ground_truth)
    all_results["section_2_multiple_images"] = section_2_multiple_images(b64_images, ground_truth)
    all_results["section_3_ocr"] = section_3_ocr(b64_images, ground_truth)
    all_results["section_4_chart"] = section_4_chart_interpretation(b64_images, ground_truth)
    all_results["section_5_math"] = section_5_math_from_image(b64_images, ground_truth)
    all_results["section_6_code"] = section_6_code_from_image(b64_images, ground_truth)
    all_results["section_7_reasoning"] = section_7_reasoning(b64_images, ground_truth)
    all_results["section_8_performance"] = section_8_performance(all_results)
    
    # Save results
    output_file = OUTPUT_DIR / "qwen3-6-multimodal-benchmark-results.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n\nResults saved to: {output_file}")
    
    # Print final summary
    perf = all_results["section_8_performance"]
    print("\n" + "="*70)
    print("BENCHMARK COMPLETE")
    print("="*70)
    print(f"  Requests: {perf['total_requests']}")
    print(f"  Success: {perf['success_rate']}%")
    print(f"  Errors: {perf['total_errors']}")
    print(f"  Prompt tokens: {perf['total_prompt_tokens']}")
    print(f"  Completion tokens: {perf['total_completion_tokens']}")
    print(f"  Total time: {perf['total_elapsed_s']}s")
    print(f"  Avg tok/s: {perf['avg_completion_tokens_per_s']}")


if __name__ == "__main__":
    main()