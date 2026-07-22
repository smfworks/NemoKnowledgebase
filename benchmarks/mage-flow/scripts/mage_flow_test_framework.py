#!/usr/bin/env python3
"""Mage-Flow Test Framework — comprehensive qualitative and performance evaluation.

Categories:
  1. Prompt Following — does the model render what's asked?
  2. Resolution & Aspect Ratio — native resolution from 512 to 2048, extreme ratios
  3. Text Rendering — English and Chinese text in images
  4. Batch Generation — mixed resolutions/seeds in one packed forward
  5. Image Editing — background swap, style transfer, object modification, restoration
  6. Performance — latency vs resolution, memory profiling, step scaling

Outputs:
  - Images saved to ~/workspace/mage-flow-test-results/
  - JSON metrics to ~/workspace/mage-flow-test-results/report.json
  - Markdown report to ~/workspace/mage-flow-test-results/report.md
"""
import os
import sys
import time
import json
import math
import traceback
from pathlib import Path

# --- gfx1151 ROCm setup ---
os.environ.setdefault('VF_HF_ATTN_IMPL', 'eager')
os.environ.setdefault('LD_LIBRARY_PATH', os.path.expanduser('~/workspace/env/mage-flow.env/lib/python3.11/site-packages/_rocm_sdk_core/lib'))
os.environ.setdefault('LIBDRM_DATA_PATH', '/usr/share/libdrm')

from mage_flow.models.modules._attn_backend import set_attn_backend
set_attn_backend('sdpa')

import mage_flow.models.mage_flow as mf_module
_orig_init = mf_module.MageFlowModel.__init__
def _patched_init(self, config):
    if hasattr(config, 'attn_type'):
        config.attn_type = 'sdpa'
    set_attn_backend('sdpa')
    _orig_init(self, config)
mf_module.MageFlowModel.__init__ = _patched_init

import torch
import numpy as np
from PIL import Image
from mage_flow import MageFlowPipeline

# --- Config ---
T2I_MODEL = os.path.expanduser('~/workspace/models/Mage-Flow-Turbo')
EDIT_MODEL = os.path.expanduser('~/workspace/models/Mage-Flow-Edit-Turbo')
OUTPUT_DIR = os.path.expanduser('~/workspace/mage-flow-test-results')
os.makedirs(OUTPUT_DIR, exist_ok=True)

results = {
    "framework": "Mage-Flow Test Framework",
    "model_t2i": "Mage-Flow-Turbo (4-step)",
    "model_edit": "Mage-Flow-Edit-Turbo (4-step)",
    "hardware": "AMD Ryzen AI MAX+ 395, Radeon 8060S (gfx1151), 51.5 GB UMA",
    "kernel": "7.1.4-070104-generic",
    "torch": torch.__version__,
    "categories": {},
    "summary": {}
}


def image_metrics(img: Image.Image) -> dict:
    """Compute basic image quality metrics."""
    arr = np.array(img)
    return {
        "size": f"{img.size[0]}x{img.size[1]}",
        "mean": round(float(arr.mean()), 1),
        "std": round(float(arr.std()), 1),
        "unique_values": int(len(np.unique(arr))),
        "channel_r": round(float(arr[:,:,0].mean()), 1) if arr.ndim == 3 else 0,
        "channel_g": round(float(arr[:,:,1].mean()), 1) if arr.ndim == 3 else 0,
        "channel_b": round(float(arr[:,:,2].mean()), 1) if arr.ndim == 3 else 0,
        "has_content": bool(arr.std() > 10),
        "file_size_kb": 0,  # filled after save
    }


def save_image(img: Image.Image, name: str) -> str:
    path = os.path.join(OUTPUT_DIR, name)
    img.save(path)
    return path


def run_t2i(pipe, prompt, steps=4, cfg=1.0, h=1024, w=1024, seed=42, label=""):
    """Run a single T2I generation and record metrics."""
    t0 = time.time()
    try:
        img = pipe.generate([prompt], steps=steps, cfg=cfg, heights=[h], widths=[w], seeds=[seed])[0]
        elapsed = time.time() - t0
        fname = f"t2i_{label}.png"
        path = save_image(img, fname)
        metrics = image_metrics(img)
        metrics["file_size_kb"] = round(os.path.getsize(path) / 1024, 1)
        metrics["latency_s"] = round(elapsed, 2)
        metrics["prompt"] = prompt[:80]
        metrics["steps"] = steps
        metrics["cfg"] = cfg
        metrics["seed"] = seed
        metrics["status"] = "PASS" if metrics["has_content"] else "FAIL_BLANK"
        return metrics
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "prompt": prompt[:80],
            "latency_s": round(elapsed, 2),
            "status": f"ERROR: {type(e).__name__}: {str(e)[:100]}",
        }


def run_edit(pipe, prompt, ref_img, steps=4, cfg=1.0, max_size=1024, seed=42, label=""):
    """Run a single image edit and record metrics."""
    t0 = time.time()
    try:
        result = pipe.edit([prompt], [ref_img], steps=steps, cfg=cfg, max_size=max_size, seeds=[seed])[0]
        elapsed = time.time() - t0
        fname = f"edit_{label}.png"
        path = save_image(result, fname)
        metrics = image_metrics(result)
        metrics["file_size_kb"] = round(os.path.getsize(path) / 1024, 1)
        metrics["latency_s"] = round(elapsed, 2)
        metrics["instruction"] = prompt[:80]
        metrics["status"] = "PASS" if metrics["has_content"] else "FAIL_BLANK"
        return metrics
    except Exception as e:
        elapsed = time.time() - t0
        return {
            "instruction": prompt[:80],
            "latency_s": round(elapsed, 2),
            "status": f"ERROR: {type(e).__name__}: {str(e)[:100]}",
        }


def gpu_mem():
    return round(torch.cuda.memory_allocated() / 1e9, 2)


# =====================================================================
# Category 1: Prompt Following
# =====================================================================
def test_prompt_following(pipe):
    print("\n{'='*60}", flush=True)
    print("Category 1: Prompt Following", flush=True)
    print("{'='*60}", flush=True)
    tests = [
        ("portrait", "A close-up portrait of an elderly African man with deep wrinkles, wearing a traditional hat, soft natural lighting, ultra realistic."),
        ("landscape", "The Salar de Uyuni mirror surface captured at high noon, with intimate stillness permeating the air. National Geographic editorial, cinematic depth."),
        ("cuisine", "An immersive close-up of a steaming bowl of Sichuan mapo tofu over jasmine rice, served on a hand-thrown ceramic plate. Shot with a Hasselblad H6D-100c."),
        ("architecture", "A brutalist concrete library building at golden hour, sharp angular shadows, blue sky, architectural photography style."),
        ("animal", "A majestic snow leopard sitting on a rocky cliff in the Himalayas, fur blowing in the wind, ultra-detailed, wildlife photography."),
        ("abstract", "An abstract digital art piece with swirling neon colors, geometric shapes, and a futuristic cyberpunk aesthetic."),
        ("people_group", "A diverse group of five friends laughing together at an outdoor cafe, candid street photography, warm afternoon light."),
        ("fantasy", "A dragon perched on a castle tower at sunset, epic fantasy art, dramatic lighting, highly detailed scales and stone texture."),
    ]
    cat_results = []
    for label, prompt in tests:
        print(f"  [{label}] {prompt[:60]}...", flush=True)
        m = run_t2i(pipe, prompt, h=1024, w=1024, label=label)
        m["test"] = label
        cat_results.append(m)
        print(f"    → {m['status']}, {m.get('latency_s','?')}s, std={m.get('std','?')}", flush=True)
    return cat_results


# =====================================================================
# Category 2: Resolution & Aspect Ratio
# =====================================================================
def test_resolution(pipe):
    print("\n{'='*60}", flush=True)
    print("Category 2: Resolution & Aspect Ratio", flush=True)
    print("{'='*60}", flush=True)
    prompt = "A serene Japanese garden with a koi pond, cherry blossoms, and a wooden bridge at sunrise."
    resolutions = [
        ("512_square", 512, 512),
        ("1024_square", 1024, 1024),
        ("1536_square", 1536, 1536),
        ("portrait_2x3", 1024, 768),    # 4:3 portrait
        ("landscape_3x2", 768, 1024),   # 4:3 landscape
        ("extreme_portrait", 2048, 512),  # 4:1 extreme
        ("extreme_landscape", 512, 2048), # 1:4 extreme
        ("square_small", 768, 768),
        ("wide_panorama", 768, 1536),
    ]
    cat_results = []
    for label, h, w in resolutions:
        print(f"  [{label}] {h}x{w}...", flush=True)
        m = run_t2i(pipe, prompt, h=h, w=w, label=label)
        m["test"] = label
        m["resolution"] = f"{h}x{w}"
        cat_results.append(m)
        print(f"    → {m['status']}, {m.get('latency_s','?')}s", flush=True)
    return cat_results


# =====================================================================
# Category 3: Text Rendering
# =====================================================================
def test_text_rendering(pipe):
    print("\n{'='*60}", flush=True)
    print("Category 3: Text Rendering", flush=True)
    print("{'='*60}", flush=True)
    tests = [
        ("text_en_simple", "A white coffee mug on a wooden table with the text 'HELLO WORLD' printed on it in bold black letters."),
        ("text_en_sign", "A vintage neon sign on a brick wall that reads 'OPEN 24 HOURS' in glowing red and blue letters."),
        ("text_en_poster", "A motivational poster on an office wall with the text 'DREAM BIG' in large white font on a blue background."),
        ("text_en_book", "A book cover on a desk with the title 'The Art of AI' printed in elegant gold lettering."),
        ("text_zh_simple", "一张白色卡片上写着中文文字'你好世界'，黑色毛笔书法风格。"),
        ("text_mixed", "A poster with both English text 'WELCOME' and Chinese text '欢迎' side by side, clean modern design."),
    ]
    cat_results = []
    for label, prompt in tests:
        print(f"  [{label}] {prompt[:60]}...", flush=True)
        m = run_t2i(pipe, prompt, h=1024, w=1024, label=label)
        m["test"] = label
        cat_results.append(m)
        print(f"    → {m['status']}, {m.get('latency_s','?')}s", flush=True)
    return cat_results


# =====================================================================
# Category 4: Batch Generation
# =====================================================================
def test_batch(pipe):
    print("\n{'='*60}", flush=True)
    print("Category 4: Batch Generation (mixed resolutions in one forward)", flush=True)
    print("{'='*60}", flush=True)
    prompts = [
        "A futuristic city skyline at night with neon lights and flying cars.",
        "A peaceful mountain lake at dawn with mist rising from the water.",
        "A steampunk airship floating above Victorian London, brass and copper details.",
    ]
    heights = [512, 1024, 768]
    widths = [1024, 1024, 1536]
    seeds = [1, 2, 3]

    print(f"  Batch: {len(prompts)} images, mixed resolutions...", flush=True)
    t0 = time.time()
    try:
        images = pipe.generate(prompts, steps=4, cfg=1.0, heights=heights, widths=widths, seeds=seeds)
        elapsed = time.time() - t0
        cat_results = {
            "batch_size": len(prompts),
            "latency_total_s": round(elapsed, 2),
            "latency_per_image_s": round(elapsed / len(prompts), 2),
            "images": [],
            "status": "PASS",
        }
        for i, (img, prompt) in enumerate(zip(images, prompts)):
            fname = f"batch_{i}.png"
            path = save_image(img, fname)
            m = image_metrics(img)
            m["file_size_kb"] = round(os.path.getsize(path) / 1024, 1)
            m["prompt"] = prompt[:60]
            m["resolution"] = f"{heights[i]}x{widths[i]}"
            m["seed"] = seeds[i]
            cat_results["images"].append(m)
        print(f"    → {len(images)} images in {elapsed:.2f}s ({elapsed/len(prompts):.2f}s/img)", flush=True)
    except Exception as e:
        elapsed = time.time() - t0
        cat_results = {
            "batch_size": len(prompts),
            "latency_total_s": round(elapsed, 2),
            "status": f"ERROR: {type(e).__name__}: {str(e)[:200]}",
        }
        print(f"    → ERROR: {e}", flush=True)
    return cat_results


# =====================================================================
# Category 5: Image Editing
# =====================================================================
def test_editing(pipe, edit_pipe):
    print("\n{'='*60}", flush=True)
    print("Category 5: Image Editing", flush=True)
    print("{'='*60}", flush=True)

    # Generate a source image first using T2I
    print("  Generating source image for editing...", flush=True)
    source = pipe.generate(
        ["A golden retriever dog sitting in a park on a sunny day, realistic photo."],
        steps=4, cfg=1.0, heights=[1024], widths=[1024], seeds=[42]
    )[0]
    save_image(source, "edit_source_dog.png")

    # Also use the bundled dog image
    dog_path = os.path.expanduser('~/workspace/Mage/mage_flow/assets/dog.jpg')
    dog_img = Image.open(dog_path).convert("RGB") if os.path.exists(dog_path) else source

    tests = [
        ("bg_swap", "Replace the background with a field of sunflowers", dog_img),
        ("bg_beach", "Replace the background with a tropical beach at sunset", dog_img),
        ("style_cyberpunk", "Transform this into a cyberpunk neon style artwork", source),
        ("style_oil", "Convert this image to an oil painting style", source),
        ("object_add", "Add a red balloon floating next to the dog", dog_img),
        ("color_change", "Change the dog's fur color to white", dog_img),
        ("time_of_day", "Change the scene to nighttime with moonlight", source),
        ("weather", "Make it rain heavily in the scene", source),
    ]
    cat_results = []
    for label, instruction, ref in tests:
        print(f"  [{label}] {instruction[:60]}...", flush=True)
        m = run_edit(edit_pipe, instruction, ref, steps=4, cfg=1.0, max_size=1024, label=label)
        m["test"] = label
        cat_results.append(m)
        print(f"    → {m['status']}, {m.get('latency_s','?')}s", flush=True)
    return cat_results


# =====================================================================
# Category 6: Performance Benchmarking
# =====================================================================
def test_performance(pipe):
    print("\n{'='*60}", flush=True)
    print("Category 6: Performance Benchmarking", flush=True)
    print("{'='*60}", flush=True)
    prompt = "A detailed architectural photograph of a modern glass skyscraper against a clear blue sky."

    # 6a: Resolution scaling
    print("\n  [6a] Resolution scaling...", flush=True)
    res_results = []
    for h, w in [(512, 512), (768, 768), (1024, 1024), (1536, 1536)]:
        # Warm up
        try:
            pipe.generate([prompt], steps=4, cfg=1.0, heights=[h], widths=[w], seeds=[99])
        except:
            pass
        torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        img = pipe.generate([prompt], steps=4, cfg=1.0, heights=[h], widths=[w], seeds=[42])
        elapsed = time.time() - t0
        peak_mem = torch.cuda.max_memory_allocated() / 1e9
        m = {"resolution": f"{h}x{w}", "latency_s": round(elapsed, 2), "peak_gpu_mem_gb": round(peak_mem, 2)}
        res_results.append(m)
        print(f"    {h}x{w}: {elapsed:.2f}s, {peak_mem:.2f} GB peak", flush=True)

    # 6b: Step scaling
    print("\n  [6b] Step scaling (1024x1024)...", flush=True)
    step_results = []
    for steps in [4, 8, 12, 20]:
        t0 = time.time()
        img = pipe.generate([prompt], steps=steps, cfg=1.0 if steps <= 4 else 5.0, heights=[1024], widths=[1024], seeds=[42])
        elapsed = time.time() - t0
        m = {"steps": steps, "cfg": 1.0 if steps <= 4 else 5.0, "latency_s": round(elapsed, 2)}
        step_results.append(m)
        print(f"    {steps} steps: {elapsed:.2f}s", flush=True)

    return {"resolution_scaling": res_results, "step_scaling": step_results}


# =====================================================================
# Main
# =====================================================================
def main():
    print("=" * 60, flush=True)
    print("Mage-Flow Test Framework", flush=True)
    print(f"Hardware: {results['hardware']}", flush=True)
    print(f"Kernel: {results['kernel']}", flush=True)
    print(f"Torch: {results['torch']}", flush=True)
    print("=" * 60, flush=True)

    # Load T2I model
    print("\nLoading T2I model (Mage-Flow-Turbo)...", flush=True)
    t0 = time.time()
    pipe = MageFlowPipeline.from_pretrained(T2I_MODEL, device='cuda')
    print(f"Loaded in {time.time()-t0:.1f}s. GPU mem: {gpu_mem()} GB", flush=True)

    # Category 1: Prompt Following
    results["categories"]["1_prompt_following"] = test_prompt_following(pipe)

    # Category 2: Resolution & Aspect Ratio
    results["categories"]["2_resolution"] = test_resolution(pipe)

    # Category 3: Text Rendering
    results["categories"]["3_text_rendering"] = test_text_rendering(pipe)

    # Category 4: Batch Generation
    results["categories"]["4_batch"] = test_batch(pipe)

    # Category 6: Performance (before swapping models)
    try:
        results["categories"]["6_performance"] = test_performance(pipe)
    except Exception as e:
        results["categories"]["6_performance"] = {"status": f"ERROR: {e}"}
        print(f"  Performance tests error: {e}", flush=True)

    # Save partial results before model swap
    json_path = os.path.join(OUTPUT_DIR, "report.json")
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nPartial results saved to {json_path}", flush=True)

    # Unload T2I, load Edit model for editing tests
    print("\nUnloading T2I model...", flush=True)
    del pipe
    torch.cuda.empty_cache()
    print(f"GPU mem after unload: {gpu_mem()} GB", flush=True)

    # Generate source image with T2I, then switch to edit model
    print("\nReloading T2I for source image generation...", flush=True)
    t2i_pipe = MageFlowPipeline.from_pretrained(T2I_MODEL, device='cuda')
    source = t2i_pipe.generate(
        ["A golden retriever dog sitting in a park on a sunny day, realistic photo."],
        steps=4, cfg=1.0, heights=[1024], widths=[1024], seeds=[42]
    )[0]
    save_image(source, "edit_source_dog.png")
    del t2i_pipe
    torch.cuda.empty_cache()

    print("\nLoading Edit model (Mage-Flow-Edit-Turbo)...", flush=True)
    t0 = time.time()
    edit_pipe = MageFlowPipeline.from_pretrained(EDIT_MODEL, device='cuda')
    print(f"Loaded in {time.time()-t0:.1f}s. GPU mem: {gpu_mem()} GB", flush=True)

    # Category 5: Image Editing
    try:
        results["categories"]["5_editing"] = test_editing_with_source(edit_pipe, source)
    except Exception as e:
        results["categories"]["5_editing"] = [{"status": f"ERROR: {e}"}]
        print(f"  Editing tests error: {e}", flush=True)

    # Summary
    total_tests = 0
    passed = 0
    failed = 0
    errors = 0
    for cat_name, cat_data in results["categories"].items():
        if isinstance(cat_data, list):
            for item in cat_data:
                total_tests += 1
                if item.get("status") == "PASS":
                    passed += 1
                elif "ERROR" in item.get("status", ""):
                    errors += 1
                else:
                    failed += 1
        elif isinstance(cat_data, dict):
            if "status" in cat_data:
                total_tests += 1
                if cat_data["status"] == "PASS":
                    passed += 1
                elif "ERROR" in cat_data["status"]:
                    errors += 1
                else:
                    failed += 1

    results["summary"] = {
        "total_tests": total_tests,
        "passed": passed,
        "failed": failed,
        "errors": errors,
        "pass_rate": round(passed / max(total_tests, 1) * 100, 1),
    }

    # Save JSON
    json_path = os.path.join(OUTPUT_DIR, "report.json")
    with open(json_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n{'='*60}", flush=True)
    print(f"Results saved to {json_path}", flush=True)
    print(f"Images saved to {OUTPUT_DIR}/", flush=True)
    print(f"Summary: {passed}/{total_tests} passed, {failed} failed, {errors} errors", flush=True)
    print(f"{'='*60}", flush=True)

    return results


def test_editing_with_source(edit_pipe, source):
    """Editing tests with pre-generated source image."""
    dog_path = os.path.expanduser('~/workspace/Mage/mage_flow/assets/dog.jpg')
    dog_img = Image.open(dog_path).convert("RGB") if os.path.exists(dog_path) else source

    tests = [
        ("bg_swap_sunflowers", "Replace the background with a field of sunflowers", dog_img),
        ("bg_swap_beach", "Replace the background with a tropical beach at sunset", dog_img),
        ("style_cyberpunk", "Transform this into a cyberpunk neon style artwork", source),
        ("style_oil_painting", "Convert this image to an oil painting style", source),
        ("object_add_balloon", "Add a red balloon floating next to the dog", dog_img),
        ("color_change_white", "Change the dog's fur color to white", dog_img),
        ("time_night", "Change the scene to nighttime with moonlight", source),
        ("weather_rain", "Make it rain heavily in the scene", source),
    ]
    cat_results = []
    for label, instruction, ref in tests:
        print(f"  [{label}] {instruction[:60]}...", flush=True)
        m = run_edit(edit_pipe, instruction, ref, steps=4, cfg=1.0, max_size=1024, label=label)
        m["test"] = label
        cat_results.append(m)
        print(f"    → {m['status']}, {m.get('latency_s','?')}s", flush=True)
    return cat_results


if __name__ == "__main__":
    main()