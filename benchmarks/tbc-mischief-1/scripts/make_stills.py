#!/usr/bin/env python3
"""Generate the four locked stills on local Comfy (Qwen Image 2.1)."""
import json
import time
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8188"
ROOT = Path("/home/mikesai1/NemoVault/evals/mischief-variant-board")
OUT = ROOT / "stills"
PROMPTS = json.loads((ROOT / "prompts.json").read_text())


def graph(prompt: str, seed: int, prefix: str) -> dict:
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "qwen_image_2.1_int8_convrot.safetensors",
                "weight_dtype": "default",
            },
        },
        "2": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3vl_8b_int8_convrot.safetensors",
                "type": "qwen_image",
                "device": "default",
            },
        },
        "3": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "qwen_image_2.1_vae_bf16.safetensors"},
        },
        "4": {
            "class_type": "EmptySD3LatentImage",
            "inputs": {"width": 1280, "height": 720, "batch_size": 1},
        },
        "5": {
            "class_type": "ModelSamplingAuraFlow",
            "inputs": {"model": ["1", 0], "shift": 3.1},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 0], "text": prompt},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 0], "text": ""},
        },
        "8": {
            "class_type": "KSampler",
            "inputs": {
                "model": ["5", 0],
                "seed": seed,
                "steps": 25,
                "cfg": 1.0,
                "sampler_name": "euler",
                "scheduler": "simple",
                "denoise": 1.0,
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["4", 0],
            },
        },
        "9": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["8", 0], "vae": ["3", 0]},
        },
        "10": {
            "class_type": "SaveImage",
            "inputs": {"images": ["9", 0], "filename_prefix": prefix},
        },
    }


def post(path: str, payload: dict | None = None) -> dict:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"} if data else {},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = []
    for still in PROMPTS["stills"]:
        dest = OUT / f"{still['id']}.png"
        if dest.exists() and dest.stat().st_size > 10000:
            print("skip", still["id"], flush=True)
            continue
        body = post(
            "/prompt",
            {"prompt": graph(still["prompt"], still["seed"], f"mischief_{still['id']}"), "client_id": "nemo-mischief"},
        )
        pid = body["prompt_id"]
        jobs.append((still["id"], pid))
        print("queued", still["id"], pid, flush=True)

    pending = dict(jobs)
    while pending:
        time.sleep(8)
        done = []
        for sid, pid in pending.items():
            hist = post(f"/history/{pid}")
            if pid not in hist:
                continue
            entry = hist[pid]
            status = entry.get("status", {})
            if status.get("status_str") not in ("success", "error") and not status.get("completed"):
                continue
            if status.get("status_str") == "error":
                print("ERROR", sid, json.dumps(status)[:800], flush=True)
                done.append(sid)
                continue
            images = entry["outputs"]["10"]["images"]
            img = images[0]
            qs = urllib.parse.urlencode(
                {"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")}
            )
            with urllib.request.urlopen(BASE + "/view?" + qs, timeout=60) as r:
                blob = r.read()
            dest = OUT / f"{sid}.png"
            dest.write_bytes(blob)
            print("saved", dest, len(blob), flush=True)
            done.append(sid)
        for sid in done:
            pending.pop(sid, None)
        if pending:
            print("waiting", list(pending), flush=True)
    print("ALL_STILLS_DONE", flush=True)


if __name__ == "__main__":
    import urllib.parse
    main()
