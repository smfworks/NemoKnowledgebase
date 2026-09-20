#!/usr/bin/env python3
"""Qwen-Image-2.1 full suite on spark-d369 ComfyUI :8188. Do not touch 56bc."""
from __future__ import annotations

import json
import statistics
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

BASE = "http://127.0.0.1:8188"
OUT = Path("/home/mikesai4/ComfyUI/tests/qwen21-full")
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "images").mkdir(exist_ok=True)

UNET = "qwen_image_2.1_int8_convrot.safetensors"
CLIP = "qwen3vl_8b_int8_convrot.safetensors"
VAE = "qwen_image_2.1_vae_bf16.safetensors"
TEMP_ABORT_C = 80
POLL_S = 4
MAX_WAIT_S = 900


def gpu_temp_util():
    p = subprocess.run(
        ["nvidia-smi", "--query-gpu=temperature.gpu,utilization.gpu,memory.used", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, check=True,
    )
    t, u, m = [x.strip() for x in p.stdout.strip().split(",")]
    def to_int(x):
        return None if x in ("[N/A]", "N/A", "") else int(float(x))
    return to_int(t) or 0, to_int(u) or 0, to_int(m) or 0


def post_json(path, payload, timeout=60):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def get_json(path, timeout=30):
    with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
        return json.loads(r.read().decode())


def upload_png(path: Path) -> str:
    boundary = "----NemoBoundary"
    data = path.read_bytes()
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{path.name}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        BASE + "/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())["name"]


def t2i_graph(prompt, width, height, steps, seed, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "4": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": prompt}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["5", 0], "seed": seed, "steps": steps, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["4", 0],
        }},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }


def t2i_qwen21_encoder_graph(prompt, width, height, steps, seed, prefix):
    """Native TextEncodeQwenImage21 path (no refs). Latent comes from the encoder."""
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "4": {"class_type": "EmptySD3LatentImage", "inputs": {"width": width, "height": height, "batch_size": 1}},
        "5": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": "auto", "dtype": "default"}},
        "6": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["5", 0], "shift": 3.1}},
        "11": {"class_type": "TextEncodeQwenImage21", "inputs": {
            "clip": ["2", 0], "prompt": prompt, "negative_prompt": "",
            "resolution": 0, "vae": ["3", 0],
        }},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["6", 0], "seed": seed, "steps": steps, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "positive": ["11", 0], "negative": ["11", 1], "latent_image": ["4", 0],
        }},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }


def edit_graph(image_name, prompt, steps, seed, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "20": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "5": {"class_type": "QwenImage21Cache", "inputs": {"model": ["1", 0], "device": "auto", "dtype": "default"}},
        "6": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["5", 0], "shift": 3.1}},
        "11": {"class_type": "TextEncodeQwenImage21", "inputs": {
            "clip": ["2", 0],
            "prompt": prompt,
            "negative_prompt": "",
            "resolution": 1024,
            "vae": ["3", 0],
            "image_1": ["20", 0],
        }},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["6", 0], "seed": seed, "steps": steps, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "positive": ["11", 0], "negative": ["11", 1], "latent_image": ["11", 2],
        }},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }


def edit_fallback_graph(image_name, prompt, steps, seed, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP, "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE}},
        "20": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "5": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3.1}},
        "11": {"class_type": "TextEncodeQwenImageEdit", "inputs": {
            "clip": ["2", 0], "prompt": prompt, "vae": ["3", 0], "image": ["20", 0],
        }},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": ""}},
        "12": {"class_type": "VAEEncode", "inputs": {"pixels": ["20", 0], "vae": ["3", 0]}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["5", 0], "seed": seed, "steps": steps, "cfg": 1.0,
            "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0,
            "positive": ["11", 0], "negative": ["7", 0], "latent_image": ["12", 0],
        }},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }


def score_png(path: Path) -> dict:
    im = Image.open(path)
    px = list(im.getdata())
    n = max(1, len(px) // 16)
    sample = px[::16]
    if im.mode == "RGBA":
        rs, gs, bs, als = zip(*sample)
        alpha_mean = statistics.mean(als)
        alpha_std = statistics.pstdev(als)
    else:
        rs, gs, bs = zip(*[(c[0], c[1], c[2]) if isinstance(c, tuple) else (c, c, c) for c in sample])
        alpha_mean, alpha_std = None, None
    std_r = statistics.pstdev(rs)
    return {
        "mode": im.mode,
        "width": im.size[0],
        "height": im.size[1],
        "bytes": path.stat().st_size,
        "mean_r": round(statistics.mean(rs), 1),
        "mean_g": round(statistics.mean(gs), 1),
        "mean_b": round(statistics.mean(bs), 1),
        "std_r": round(std_r, 1),
        "unique_sampled": len(set(sample)),
        "has_content": std_r > 10,
        "alpha_mean": None if alpha_mean is None else round(alpha_mean, 1),
        "alpha_std": None if alpha_std is None else round(alpha_std, 1),
        "has_transparency": bool(alpha_std is not None and alpha_std > 8 and alpha_mean is not None and alpha_mean < 250),
        "n_pixels": im.size[0] * im.size[1],
        "sampled": n,
    }


def run_graph(graph, prefix, timeout=MAX_WAIT_S):
    t0 = time.time()
    temp0, util0, mem0 = gpu_temp_util()
    if temp0 >= TEMP_ABORT_C:
        return {"ok": False, "error": f"thermal_abort {temp0}C", "latency_s": 0, "temp_c": temp0}
    try:
        resp = post_json("/prompt", {"prompt": graph, "client_id": "qwen21-full"})
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:1500]
        return {"ok": False, "error": f"http {e.code} {body}", "latency_s": round(time.time() - t0, 2), "temp_c": temp0}
    if resp.get("node_errors"):
        return {"ok": False, "error": "node_errors " + json.dumps(resp["node_errors"])[:1500],
                "latency_s": round(time.time() - t0, 2), "temp_c": temp0, "prompt_id": resp.get("prompt_id")}
    pid = resp["prompt_id"]
    deadline = t0 + timeout
    while time.time() < deadline:
        time.sleep(POLL_S)
        hist = get_json(f"/history/{pid}")
        if pid not in hist:
            continue
        h = hist[pid]
        st = h.get("status") or {}
        if not st.get("completed") and st.get("status_str") not in ("success", "error"):
            continue
        latency = round(time.time() - t0, 2)
        temp1, util1, mem1 = gpu_temp_util()
        if st.get("status_str") == "error" or not st.get("completed"):
            return {"ok": False, "error": "exec " + json.dumps(st.get("messages", []))[-1500:],
                    "latency_s": latency, "prompt_id": pid, "temp_c": temp1, "gpu_mem_mb": mem1}
        images = []
        for node_out in (h.get("outputs") or {}).values():
            for im in node_out.get("images") or []:
                images.append(im)
        if not images:
            return {"ok": False, "error": "no_images", "latency_s": latency, "prompt_id": pid, "temp_c": temp1}
        src = Path("/home/mikesai4/ComfyUI/output") / images[0].get("subfolder", "") / images[0]["filename"]
        dest = OUT / "images" / f"{prefix}.png"
        dest.write_bytes(src.read_bytes())
        sc = score_png(dest)
        return {
            "ok": bool(sc["has_content"]),
            "error": None if sc["has_content"] else "blank",
            "latency_s": latency,
            "prompt_id": pid,
            "filename": str(dest),
            "comfy_filename": images[0]["filename"],
            "temp_c": temp1,
            "temp_start_c": temp0,
            "gpu_mem_mb": mem1,
            "gpu_mem_start_mb": mem0,
            **sc,
        }
    return {"ok": False, "error": "timeout", "latency_s": round(time.time() - t0, 2), "prompt_id": pid, "temp_c": gpu_temp_util()[0]}


TESTS = [
    {"id": "PF01_portrait", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Close-up portrait of a middle-aged man with weathered skin, grey stubble, warm window light, 85mm, shallow depth of field, photoreal",
     "w": 1024, "h": 1024, "steps": 25, "seed": 101},
    {"id": "PF02_landscape", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Sunset over red sandstone canyon, long shadows, orange and crimson sky, river below, ultra-wide landscape photograph",
     "w": 1024, "h": 1024, "steps": 25, "seed": 102},
    {"id": "PF03_cuisine", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Overhead food photo: tomato soup in a white bowl, basil, crusty bread, rustic wooden table, steam, natural window light",
     "w": 1024, "h": 1024, "steps": 25, "seed": 103},
    {"id": "PF04_architecture", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Modern glass skyscraper against a clear deep blue sky, wide-angle architectural photograph, sharp geometry, midday",
     "w": 1024, "h": 1024, "steps": 25, "seed": 104},
    {"id": "PF05_animal", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Golden retriever running through a sunlit meadow of tall yellow grass, motion, photoreal wildlife photography",
     "w": 1024, "h": 1024, "steps": 25, "seed": 105},
    {"id": "PF06_abstract", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Abstract geometric composition of neon lime-green planes, black circles, and white halftone dots, flat graphic design, no text",
     "w": 1024, "h": 1024, "steps": 25, "seed": 106},
    {"id": "PF07_people", "cat": "prompt_following", "kind": "t2i",
     "prompt": "Busy Tokyo crosswalk at night, dozens of people with umbrellas, neon reflections on wet pavement, street photography",
     "w": 1024, "h": 1024, "steps": 25, "seed": 107},
    {"id": "PF08_fantasy", "cat": "prompt_following", "kind": "t2i",
     "prompt": "A red dragon coiled on a cliff at dusk, fire breath, volcanic glow, cinematic fantasy concept art",
     "w": 1024, "h": 1024, "steps": 25, "seed": 108},
    {"id": "RS01_512", "cat": "resolution", "kind": "t2i",
     "prompt": "A red ceramic teapot on a wooden table, studio lighting, photoreal",
     "w": 512, "h": 512, "steps": 25, "seed": 201},
    {"id": "RS02_2048", "cat": "resolution", "kind": "t2i",
     "prompt": "A red ceramic teapot on a wooden table, studio lighting, photoreal, fine detail",
     "w": 2048, "h": 2048, "steps": 25, "seed": 202},
    {"id": "RS03_16x9", "cat": "resolution", "kind": "t2i",
     "prompt": "Panoramic mountain lake at dawn, mist, pine forest, cinematic 16:9 landscape",
     "w": 1344, "h": 768, "steps": 25, "seed": 203},
    {"id": "RS04_9x16", "cat": "resolution", "kind": "t2i",
     "prompt": "Tall waterfall in a mossy canyon, looking up, vertical composition, photoreal",
     "w": 768, "h": 1344, "steps": 25, "seed": 204},
    {"id": "TX01_en_mug", "cat": "text", "kind": "t2i",
     "prompt": "A white ceramic coffee mug on a wooden table, printed on the mug in clear black sans-serif letters: QWEN IMAGE 2.1, studio photo",
     "w": 1024, "h": 1024, "steps": 25, "seed": 301},
    {"id": "TX02_cn_sign", "cat": "text", "kind": "t2i",
     "prompt": "A wooden shop sign hanging on a brick wall, carved Chinese calligraphy reading 通义千问, afternoon sunlight, photoreal",
     "w": 1024, "h": 1024, "steps": 25, "seed": 302},
    {"id": "TX03_bilingual", "cat": "text", "kind": "t2i",
     "prompt": "A printed poster on a cafe window. Top line in English: SPARK TEST. Bottom line in Chinese: 春天来了. Clean graphic design, photoreal photograph of the poster",
     "w": 1024, "h": 1024, "steps": 25, "seed": 303},
    {"id": "RGBA01_sticker", "cat": "rgba", "kind": "t2i",
     "prompt": "This is an RGBA image with transparency. A cute cartoon dragon sticker, simple shapes, bold outline. The image has alpha channel and the background is transparent.",
     "w": 1024, "h": 1024, "steps": 25, "seed": 401},
    {"id": "ND01_native_encoder", "cat": "native_encoder", "kind": "t2i21",
     "prompt": "A neon shop sign that reads QWEN IMAGE 2.1, rainy night, reflections on wet pavement",
     "w": 1024, "h": 1024, "steps": 25, "seed": 42},
    {"id": "PR01_1024_s8", "cat": "performance", "kind": "t2i",
     "prompt": "A red ceramic teapot on a wooden table, studio lighting",
     "w": 1024, "h": 1024, "steps": 8, "seed": 501},
    {"id": "PR02_1024_s40", "cat": "performance", "kind": "t2i",
     "prompt": "A red ceramic teapot on a wooden table, studio lighting",
     "w": 1024, "h": 1024, "steps": 40, "seed": 502},
    {"id": "PR03_2048_s8", "cat": "performance", "kind": "t2i",
     "prompt": "A red ceramic teapot on a wooden table, studio lighting",
     "w": 2048, "h": 2048, "steps": 8, "seed": 503},
]


def main():
    health = get_json("/system_stats")
    print("health_ok", health.get("system", {}).get("comfyui_version"), flush=True)
    results = []
    jsonl = (OUT / "results.jsonl").open("w")

    def record(test, res):
        row = {"id": test["id"], "cat": test["cat"], "kind": test["kind"],
               "w": test.get("w"), "h": test.get("h"), "steps": test.get("steps"),
               "prompt": test.get("prompt"), **res}
        results.append(row)
        jsonl.write(json.dumps(row) + "\n")
        jsonl.flush()
        flag = "PASS" if row.get("ok") else "FAIL"
        print(f"{flag} {test['id']} {row.get('latency_s')}s {row.get('error') or ''} {row.get('width')}x{row.get('height')} std={row.get('std_r')} temp={row.get('temp_c')}", flush=True)

    for test in TESTS:
        temp, _, _ = gpu_temp_util()
        if temp >= TEMP_ABORT_C:
            record(test, {"ok": False, "error": f"thermal_abort {temp}C", "latency_s": 0, "temp_c": temp})
            break
        prefix = test["id"]
        if test["kind"] == "t2i":
            g = t2i_graph(test["prompt"], test["w"], test["h"], test["steps"], test["seed"], prefix)
        elif test["kind"] == "t2i21":
            g = t2i_qwen21_encoder_graph(test["prompt"], test["w"], test["h"], test["steps"], test["seed"], prefix)
        else:
            raise ValueError(test)
        res = run_graph(g, prefix)
        record(test, res)

    # Edits: use PF01 as source if it exists
    src = OUT / "images" / "PF01_portrait.png"
    if src.exists():
        try:
            uploaded = upload_png(src)
            print("uploaded", uploaded, flush=True)
        except Exception as e:
            uploaded = None
            print("upload_fail", e, flush=True)
        edits = [
            {"id": "ED01_bg_sunset", "prompt": "Change the background to a sunset beach, keep the person and pose", "seed": 601},
            {"id": "ED02_blue_shirt", "prompt": "Change the person's clothing to a light blue denim shirt, keep face and pose", "seed": 602},
            {"id": "ED03_add_cat", "prompt": "Add a small orange tabby cat sitting on the person's shoulder, keep the rest of the photo", "seed": 603},
        ]
        edit_impl = "qwen21"
        for ed in edits:
            test = {"id": ed["id"], "cat": "edit", "kind": "edit", "w": None, "h": None, "steps": 25, "prompt": ed["prompt"]}
            if not uploaded:
                record(test, {"ok": False, "error": "no_upload", "latency_s": 0})
                continue
            g = edit_graph(uploaded, ed["prompt"], 25, ed["seed"], ed["id"])
            res = run_graph(g, ed["id"])
            if not res.get("ok") and res.get("error", "").startswith("node_errors"):
                print("edit_fallback", ed["id"], flush=True)
                g = edit_fallback_graph(uploaded, ed["prompt"], 25, ed["seed"], ed["id"])
                res = run_graph(g, ed["id"])
                edit_impl = "qwen_image_edit"
            record(test, res)
        results.append({"id": "_edit_impl", "ok": True, "error": None, "impl": edit_impl})
    else:
        print("skip_edits no PF01", flush=True)

    jsonl.close()
    n = [r for r in results if r.get("id") != "_edit_impl"]
    passed = sum(1 for r in n if r.get("ok"))
    failed = sum(1 for r in n if not r.get("ok"))
    report = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "host": "spark-d369",
        "endpoint": BASE,
        "model": "Qwen-Image-2.1 INT8 ConvRot",
        "pass": passed,
        "fail": failed,
        "n": len(n),
        "results": n,
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2))
    lines = [
        f"# Qwen-Image-2.1 full suite — spark-d369",
        f"",
        f"- {passed}/{len(n)} pass",
        f"- endpoint {BASE}",
        f"- INT8 ConvRot + Qwen3-VL-8B INT8, euler/simple cfg 1, shift 3.1",
        f"",
        f"| id | cat | ok | s | size | std | temp | err |",
        f"|----|-----|----|---|------|-----|------|-----|",
    ]
    for r in n:
        lines.append(
            f"| {r.get('id')} | {r.get('cat')} | {r.get('ok')} | {r.get('latency_s')} | "
            f"{r.get('width')}x{r.get('height')} | {r.get('std_r')} | {r.get('temp_c')} | {r.get('error') or ''} |"
        )
    (OUT / "report.md").write_text("\n".join(lines) + "\n")
    print(f"SUMMARY {passed}/{len(n)} pass  report {OUT / 'report.json'}", flush=True)


if __name__ == "__main__":
    main()
