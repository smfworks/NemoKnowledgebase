#!/usr/bin/env python3
"""Vision test for Qwen3.8-27B-FP8 (hybrid GDN VLM) on SGLang.

Generates a synthetic test image (colored shapes + text), sends it as
image_url (base64 data URI), and checks the model's visual understanding.
"""
import asyncio, json, base64, io, time, httpx

BASE_URL = "http://spark-56bc:30000/v1"
MODEL = "Qwen3.8-27B-FP8"
TIMEOUT = httpx.Timeout(300.0, connect=10.0)
KW = {"enable_thinking": False}

def make_test_image():
    """Create a 512x512 PNG with a red circle, blue square, and the text '42'."""
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (512, 512), "white")
    d = ImageDraw.Draw(img)
    d.ellipse([50, 50, 250, 250], fill="red")          # red circle (left)
    d.rectangle([300, 50, 500, 250], fill="blue")      # blue square (right)
    d.rectangle([50, 300, 500, 450], fill="yellow")    # yellow rectangle (bottom)
    d.text((200, 320), "42", fill="black")             # text "42"
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

async def vision_test(client, b64):
    data_uri = f"data:image/png;base64,{b64}"
    cases = [
        ("count_shapes", "How many distinct shapes are in this image? Answer with a number only."),
        ("identify_colors", "What colors are the shapes? List them."),
        ("read_text", "What number is written in the image? Answer with just the number."),
        ("spatial", "Is the red shape a circle or a square? Answer with one word."),
    ]
    out = []
    for label, q in cases:
        payload = {"model": MODEL, "max_tokens": 200, "temperature": 0.0,
                   "chat_template_kwargs": KW,
                   "messages": [{"role": "user", "content": [
                       {"type": "image_url", "image_url": {"url": data_uri}},
                       {"type": "text", "text": q},
                   ]}]}
        s = time.perf_counter()
        r = await client.post(f"{BASE_URL}/chat/completions", json=payload, timeout=TIMEOUT)
        el = time.perf_counter() - s
        if r.status_code != 200:
            out.append({"label": label, "status": r.status_code, "error": r.text[:200]})
            print(f"  [vision] {label}: HTTP {r.status_code}")
            continue
        d = r.json()
        content = d.get("choices", [{}])[0].get("message", {}).get("content", "")
        out.append({"label": label, "answer": content, "wall_s": round(el,3)})
        print(f"  [vision] {label}: {content!r} ({el:.1f}s)")
    return out

async def main():
    print("="*70)
    print(f"Qwen3.8-27B-FP8 vision test | {BASE_URL}")
    print("="*70)
    b64 = make_test_image()
    report = {"model": MODEL, "endpoint": BASE_URL, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
              "serve_recipe_id": "SMF-Spark-SGLang-qwen38-27b-fp8-eagle", "tests": {}}
    async with httpx.AsyncClient() as client:
        report["tests"]["vision"] = await vision_test(client, b64)
    print("\n__JSON_REPORT_START__")
    print(json.dumps(report, indent=2))
    print("__JSON_REPORT_END__")

if __name__ == "__main__":
    asyncio.run(main())
