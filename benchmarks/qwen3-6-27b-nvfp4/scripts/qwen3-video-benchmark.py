#!/usr/bin/env python3
"""
Qwen3.6-27B-NVFP4 Video Understanding Benchmark
Tests video understanding capabilities via vLLM OpenAI-compatible API.

Server: spark-56bc:8888
Model: nvidia/Qwen3.6-27B-NVFP4 (Qwen3_5ForConditionalGeneration)
Video support: limit_mm_per_prompt: {"image":4,"video":2}
"""

import json
import time
import base64
import os
import urllib.request
import urllib.error
from datetime import datetime

SERVER_URL = "http://spark-56bc:8888"
MODEL = "nvidia/Qwen3.6-27B-NVFP4"
VIDEO_DIR = "/home/mikesai1/NemoVault/queries/multimodal-test-images"
RESULTS_PATH = "/home/mikesai1/NemoVault/queries/qwen3-6-video-benchmark-results.json"
REPORT_PATH = "/home/mikesai1/NemoVault/queries/qwen3-6-video-benchmark-report.md"

def encode_video(path):
    """Encode video file as base64 data URL."""
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode()
    ext = os.path.splitext(path)[1].lstrip('.')
    return f"data:video/{ext};base64,{b64}"

def send_video_request(video_path, prompt, max_tokens=512, timeout=120):
    """Send a video understanding request to vLLM."""
    video_data_url = encode_video(video_path)
    video_size = len(video_data_url)
    
    payload = {
        "model": MODEL,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "video_url", "video_url": {"url": video_data_url}},
                {"type": "text", "text": prompt}
            ]
        }],
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False}
    }
    
    req = urllib.request.Request(
        f"{SERVER_URL}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        t1 = time.time()
        return {
            "success": True,
            "content": data["choices"][0]["message"]["content"],
            "usage": data.get("usage"),
            "latency": t1 - t0,
            "video_size_bytes": video_size,
        }
    except urllib.error.HTTPError as e:
        t1 = time.time()
        return {
            "success": False,
            "error": f"HTTP {e.code}: {e.read().decode()[:300]}",
            "latency": t1 - t0,
        }
    except Exception as e:
        t1 = time.time()
        return {
            "success": False,
            "error": str(e),
            "latency": t1 - t0,
        }

def send_multi_video_request(video_paths, prompt, max_tokens=512, timeout=120):
    """Send a request with multiple videos."""
    content_blocks = []
    for vp in video_paths:
        content_blocks.append({
            "type": "video_url",
            "video_url": {"url": encode_video(vp)}
        })
    content_blocks.append({"type": "text", "text": prompt})
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content_blocks}],
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": False}
    }
    
    req = urllib.request.Request(
        f"{SERVER_URL}/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}
    )
    
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        t1 = time.time()
        return {
            "success": True,
            "content": data["choices"][0]["message"]["content"],
            "usage": data.get("usage"),
            "latency": t1 - t0,
        }
    except Exception as e:
        t1 = time.time()
        return {
            "success": False,
            "error": str(e),
            "latency": t1 - t0,
        }

# ============================================================
# TEST DEFINITIONS
# ============================================================

tests = [
    # === Category 1: Basic Video Description ===
    {
        "id": "V1a",
        "category": "Video Description",
        "video": "09-bouncing-ball.mp4",
        "prompt": "Describe what happens in this video. What objects do you see and how do they move?",
        "max_tokens": 300,
        "expected": "Red ball/circle bouncing on blue background",
    },
    {
        "id": "V1b",
        "category": "Video Description",
        "video": "09-bouncing-ball.mp4",
        "prompt": "What color is the background in this video? What color is the moving object?",
        "max_tokens": 100,
        "expected": "Blue background, red ball/circle",
    },
    {
        "id": "V1c",
        "category": "Video Description",
        "video": "10-shapes-motion.mp4",
        "prompt": "List all the shapes you see in this video and describe each one's color and movement pattern.",
        "max_tokens": 300,
        "expected": "Green square (horizontal), yellow triangle (upward), blue circle (pulsing)",
    },
    {
        "id": "V1d",
        "category": "Video Description",
        "video": "11-color-cycle.mp4",
        "prompt": "What colors appear in this video and in what order?",
        "max_tokens": 200,
        "expected": "Red, green, blue, cyan/yellow, magenta, yellow (cycling)",
    },

    # === Category 2: Motion Analysis ===
    {
        "id": "V2a",
        "category": "Motion Analysis",
        "video": "09-bouncing-ball.mp4",
        "prompt": "Describe the trajectory of the moving object. Is it linear, circular, or bouncing? Explain your reasoning.",
        "max_tokens": 250,
        "expected": "Bouncing - changes direction at boundaries",
    },
    {
        "id": "V2b",
        "category": "Motion Analysis",
        "video": "10-shapes-motion.mp4",
        "prompt": "Which shape moves horizontally? Which shape moves vertically? Which shape changes size?",
        "max_tokens": 200,
        "expected": "Square horizontal, triangle vertical, circle changes size (pulsing)",
    },
    {
        "id": "V2c",
        "category": "Motion Analysis",
        "video": "09-bouncing-ball.mp4",
        "prompt": "If this video continues, predict where the ball will be in the next few frames based on its current trajectory.",
        "max_tokens": 200,
        "expected": "Predict continuation of bouncing pattern",
    },

    # === Category 3: Counting & Quantitative ===
    {
        "id": "V3a",
        "category": "Counting & Quantitative",
        "video": "09-bouncing-ball.mp4",
        "prompt": "How many distinct objects are in this video?",
        "max_tokens": 50,
        "expected": "1 (one red ball)",
    },
    {
        "id": "V3b",
        "category": "Counting & Quantitative",
        "video": "10-shapes-motion.mp4",
        "prompt": "How many distinct shapes are in this video? List them.",
        "max_tokens": 100,
        "expected": "3 (square, triangle, circle)",
    },
    {
        "id": "V3c",
        "category": "Counting & Quantitative",
        "video": "11-color-cycle.mp4",
        "prompt": "How many different colors appear in this video?",
        "max_tokens": 50,
        "expected": "6 (red, green, blue, cyan, magenta, yellow)",
    },

    # === Category 4: Multi-Video Comparison ===
    {
        "id": "V4a",
        "category": "Multi-Video Comparison",
        "videos": ["09-bouncing-ball.mp4", "10-shapes-motion.mp4"],
        "prompt": "Compare these two videos. What is similar and what is different in terms of objects, colors, and motion?",
        "max_tokens": 400,
        "expected": "Different objects (1 ball vs 3 shapes), different colors, both have motion",
    },
    {
        "id": "V4b",
        "category": "Multi-Video Comparison",
        "videos": ["09-bouncing-ball.mp4", "11-color-cycle.mp4"],
        "prompt": "Which video has more color variety? Describe the colors in each.",
        "max_tokens": 200,
        "expected": "Video 1 has blue+red (2 colors), Video 2 has 6 cycling colors",
    },

    # === Category 5: Video Reasoning ===
    {
        "id": "V5a",
        "category": "Video Reasoning",
        "video": "09-bouncing-ball.mp4",
        "prompt": "If this were a physics simulation, what rules would govern the object's movement? What happens at the boundaries?",
        "max_tokens": 300,
        "expected": "Ball bounces off walls - reflection of velocity at boundaries",
    },
    {
        "id": "V5b",
        "category": "Video Reasoning",
        "video": "10-shapes-motion.mp4",
        "prompt": "The green square, yellow triangle, and blue circle each follow different motion rules. Describe what rule each shape follows.",
        "max_tokens": 300,
        "expected": "Square: linear horizontal loop; Triangle: linear vertical loop; Circle: sinusoidal radius change",
    },
    {
        "id": "V5c",
        "category": "Video Reasoning",
        "video": "11-color-cycle.mp4",
        "prompt": "Is there a pattern to the color changes? If so, describe the pattern and predict the next color.",
        "max_tokens": 200,
        "expected": "Cycling pattern - 5 frames per color, repeating sequence",
    },

    # === Category 6: Video + Text (Following Instructions) ===
    {
        "id": "V6a",
        "category": "Video + Text Instructions",
        "video": "09-bouncing-ball.mp4",
        "prompt": "Write a short JSON object describing this video with fields: object_count, primary_color, background_color, motion_type.",
        "max_tokens": 150,
        "expected": "JSON with object_count:1, primary_color:red, background_color:blue, motion_type:bouncing",
    },
    {
        "id": "V6b",
        "category": "Video + Text Instructions",
        "video": "10-shapes-motion.mp4",
        "prompt": "Create a table (in markdown) listing each shape, its color, and its motion type.",
        "max_tokens": 250,
        "expected": "Markdown table with 3 rows: square/green/horizontal, triangle/yellow/vertical, circle/blue/pulsing",
    },
]

# ============================================================
# RUN TESTS
# ============================================================

results = []
total_start = time.time()

print(f"{'ID':<6} {'Category':<28} {'Status':<8} {'Time':>6} {'Tokens':>12} {'Score':>6}")
print("-" * 80)

for test in tests:
    test_id = test["id"]
    category = test["category"]
    expected = test.get("expected", "")
    
    if "videos" in test:
        video_paths = [os.path.join(VIDEO_DIR, v) for v in test["videos"]]
        result = send_multi_video_request(video_paths, test["prompt"], test.get("max_tokens", 512))
    else:
        video_path = os.path.join(VIDEO_DIR, test["video"])
        result = send_video_request(video_path, test["prompt"], test.get("max_tokens", 512))
    
    if result["success"]:
        content = result["content"]
        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        latency = result["latency"]
        
        # Simple scoring: check if expected keywords are present
        expected_lower = expected.lower()
        content_lower = content.lower()
        keywords = [kw.strip() for kw in expected_lower.split(",") if len(kw.strip()) > 2]
        matched = sum(1 for kw in keywords if kw in content_lower)
        score = f"{matched}/{len(keywords)}" if keywords else "N/A"
        
        status = "PASS"
        status_char = "✅"
        
        print(f"{test_id:<6} {category:<28} {status:<8} {latency:>5.1f}s {prompt_tokens:>5}+{completion_tokens:<5} {score:>6}")
        
        results.append({
            "id": test_id,
            "category": category,
            "status": status,
            "video": test.get("video", test.get("videos")),
            "prompt": test["prompt"],
            "expected": expected,
            "response": content,
            "latency": latency,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "score": score,
            "video_size_bytes": result.get("video_size_bytes"),
        })
    else:
        status = "FAIL"
        status_char = "❌"
        print(f"{test_id:<6} {category:<28} {status:<8} {'N/A':>6} {'N/A':>12} {'N/A':>6}")
        print(f"       Error: {result.get('error', 'unknown')[:200]}")
        
        results.append({
            "id": test_id,
            "category": category,
            "status": status,
            "video": test.get("video", test.get("videos")),
            "prompt": test["prompt"],
            "expected": test.get("expected", ""),
            "error": result.get("error"),
            "latency": result.get("latency"),
        })

total_time = time.time() - total_start
print(f"\n{'='*80}")
print(f"Total time: {total_time:.1f}s | Tests: {len(results)} | Passed: {sum(1 for r in results if r['status']=='PASS')} | Failed: {sum(1 for r in results if r['status']=='FAIL')}")

# Save results
output = {
    "model": MODEL,
    "server": SERVER_URL,
    "date": datetime.now().isoformat(),
    "config": {
        "limit_mm_per_prompt": {"image": 4, "video": 2},
        "thinking": False,
        "speculative_decoding": True,
    },
    "total_time": total_time,
    "total_tests": len(results),
    "passed": sum(1 for r in results if r["status"] == "PASS"),
    "failed": sum(1 for r in results if r["status"] == "FAIL"),
    "results": results,
}

with open(RESULTS_PATH, "w") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print(f"Results saved to {RESULTS_PATH}")