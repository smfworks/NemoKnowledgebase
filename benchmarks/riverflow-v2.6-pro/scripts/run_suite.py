#!/usr/bin/env python3
"""Riverflow 2.6 Pro on OpenRouter. Frozen prompts. 2026-10-29.

Measures the images API, not a taste panel. Checklist scoring happens
after the files exist. Do not edit PROMPTS after the first paid call.
"""

from __future__ import annotations

import base64
import io
import json
import os
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
IMG = ROOT / "images"
REFS = ROOT / "refs"
JSONL = ROOT / "results.jsonl"
MODEL = "sourceful/riverflow-v2.6-pro"
IMAGES_URL = "https://openrouter.ai/api/v1/images"
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
COST_CAP_USD = 6.0

# Checklist is frozen here so scoring cannot move after the pictures land.
RUBRIC = {
    "text_plate": [
        "exact string SMF FORGE is readable",
        "no other readable text",
        "one nameplate is the subject",
    ],
    "label_lines": [
        "NORTH DOCK is readable",
        "BATCH 1847 is readable",
        "12 FL OZ is readable",
        "no extra words on the label",
    ],
    "count_seven": [
        "yellow pencil count is 7",
        "pencils form one row",
        "no other objects",
    ],
    "spatial_trio": [
        "red mug is on the left",
        "green apple is in the center",
        "blue book is on the right",
        "no text",
        "no extra objects",
    ],
    "empty_bench": [
        "a bench is present",
        "no people",
        "no animals",
        "no bags or umbrellas",
        "no text",
    ],
    "aspect_5x4": ["one orange", "no text", "width greater than height"],
    "aspect_4x5": ["one lemon", "no text", "height greater than width"],
    "wide_2k": ["a pier", "one yellow bollard on the left third", "no people", "no text"],
    "cube_4k": ["one red cube", "white background", "no text"],
    "mouse_alpha": ["a mouse is the subject", "corner pixels are transparent", "no text"],
    "format_webp": ["one blue bowl", "file magic is webp"],
    "format_jpeg": ["one green bowl", "file magic is jpeg"],
    "ten_swatches": ["ten squares", "order matches the ten reference colors", "no text"],
    "edit_mug": ["mug is yellow", "apple still green and present", "book still blue and present", "no new text"],
    "edit_remove": ["apple is gone", "red mug still on the left", "blue book still on the right", "no new text"],
    "multi_compose": ["nameplate present", "SMF FORGE still readable", "mug apple and book still present"],
}

PROMPTS = {
    "text_plate": (
        "A square studio photograph of one matte black rectangular metal nameplate "
        "centered on a seamless light gray background. The nameplate carries exactly "
        "one line of white engraved capital letters reading SMF FORGE. No other text. "
        "No logo. No people. No extra objects."
    ),
    "label_lines": (
        "A front-facing product photograph of one plain white cylindrical bottle "
        "centered on a seamless white background. The label is white with black "
        "sans-serif text in exactly three lines and no other words. Line 1 reads "
        "NORTH DOCK. Line 2 reads BATCH 1847. Line 3 reads 12 FL OZ. The bottle has "
        "a plain white cap. No logo, no graphics, no extra text."
    ),
    "count_seven": (
        "Exactly seven identical yellow wooden pencils with pink erasers, lying "
        "parallel in a single horizontal row on a seamless white surface. The count "
        "must be seven. No other objects. No text. No hands. Even lighting."
    ),
    "spatial_trio": (
        "A slightly elevated photograph of a seamless white tabletop. Three objects "
        "only. On the left third, one red ceramic mug with the handle pointing right. "
        "In the center, one green apple. On the right third, one closed blue hardcover "
        "book standing upright. No text. No people. No other objects."
    ),
    "empty_bench": (
        "A front-facing photograph of one empty wooden park bench in light rain. "
        "The bench is unoccupied. No people. No animals. No bags. No umbrellas. "
        "No text. Wet pavement. Overcast daylight."
    ),
    "aspect_5x4": (
        "A single whole orange centered on a pale wooden table, photographed from "
        "slightly above. No other objects. No text. Soft daylight."
    ),
    "aspect_4x5": (
        "A single whole lemon centered on a pale wooden table, photographed from "
        "slightly above. No other objects. No text. Soft daylight."
    ),
    "wide_2k": (
        "A wide photograph of a quiet concrete pier at dusk. Wet planks. One yellow "
        "bollard on the left third. No people. No boats. No text. Overcast sky."
    ),
    "cube_4k": (
        "A single matte red cube centered on a seamless white background. Studio "
        "lighting. No text. No other objects."
    ),
    "mouse_alpha": (
        "A single matte black wireless computer mouse, three-quarter view, isolated "
        "product photo. No text. No desk. No colored backdrop."
    ),
    "format_webp": (
        "A single blue ceramic bowl centered on a seamless white background. "
        "No text. No other objects."
    ),
    "format_jpeg": (
        "A single green ceramic bowl centered on a seamless white background. "
        "No text. No other objects."
    ),
    "ten_swatches": (
        "Using the ten reference images in the order they are attached, paint a "
        "white card with exactly ten solid colored squares in one horizontal row. "
        "Match each reference color in order, image 1 through image 10. No text. "
        "No extra squares. White background."
    ),
    "edit_mug": (
        "Change only the mug from red to yellow. Keep the green apple, the blue "
        "book, the white table, and the camera angle. Do not add objects or text."
    ),
    "edit_remove": (
        "Remove the green apple. Fill the space with the same white tabletop. "
        "Do not move the red mug or the blue book. Do not add objects or text."
    ),
    "multi_compose": (
        "Place the black nameplate from the first image flat on the table, in front "
        "of the mug, apple, and book from the second image. Keep those three objects. "
        "Keep the engraved text SMF FORGE unchanged. Do not add other text."
    ),
}


def load_key() -> str:
    env = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if env:
        return env
    for p in (
        Path.home() / ".hermes" / ".env",
        Path.home() / ".hermes" / "profiles" / "nemo" / ".env",
    ):
        if not p.exists():
            continue
        for line in p.read_text(errors="replace").splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY missing")


def done_ids() -> set[str]:
    found = set()
    if not JSONL.exists():
        return found
    for line in JSONL.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("ok") and row.get("id"):
            found.add(row["id"])
    return found


def spent() -> float:
    total = 0.0
    if not JSONL.exists():
        return total
    for line in JSONL.read_text(errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = row.get("usage") or {}
        cost = usage.get("cost")
        if isinstance(cost, (int, float)):
            total += float(cost)
    return total


def append(row: dict) -> None:
    with JSONL.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def call(url: str, payload: dict, key: str, timeout: int) -> dict:
    body = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://www.smfclearinghouse.com",
            "X-Title": "SMF Riverflow 2.6 Pro eval",
        },
        method="POST",
    )
    t0 = time.perf_counter()
    status = None
    headers = {}
    raw = b""
    err = None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            headers = {k.lower(): v for k, v in resp.headers.items()}
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        headers = {k.lower(): v for k, v in exc.headers.items()}
        raw = exc.read()
        err = f"HTTP {exc.code}"
    except Exception as exc:
        err = f"{type(exc).__name__}: {exc}"
    wall = round(time.perf_counter() - t0, 3)
    keep_headers = {
        k: headers.get(k)
        for k in (
            "x-request-id",
            "x-generation-id",
            "openrouter-processing-ms",
            "x-openrouter-generation-id",
            "cf-ray",
        )
        if headers.get(k)
    }
    parsed = None
    if raw:
        try:
            parsed = json.loads(raw.decode())
        except json.JSONDecodeError:
            parsed = {"_non_json": raw[:1500].decode(errors="replace")}
    return {
        "status": status,
        "wall_s": wall,
        "headers": keep_headers,
        "body": parsed,
        "error": err,
        "request_bytes": len(body),
    }


def strip_images(body):
    if isinstance(body, dict):
        out = {}
        for k, v in body.items():
            if k in {"b64_json", "url"} and isinstance(v, str) and len(v) > 400:
                out[k + "_chars"] = len(v)
            elif isinstance(v, str) and len(v) > 2000 and v[:20].replace("+", "").replace("/", "").replace("=", "").isalnum():
                out[k] = f"<omitted {len(v)} chars>"
            else:
                out[k] = strip_images(v)
        return out
    if isinstance(body, list):
        return [strip_images(v) for v in body]
    return body


def save_image(test_id: str, item: dict) -> dict | None:
    b64 = item.get("b64_json")
    if not b64:
        return None
    raw = base64.b64decode(b64)
    media = item.get("media_type") or "application/octet-stream"
    ext = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "image/svg+xml": "svg",
    }.get(media, "bin")
    path = IMG / f"{test_id}.{ext}"
    path.write_bytes(raw)
    info = {
        "path": str(path),
        "bytes": len(raw),
        "media_type": media,
        "magic": raw[:16].hex(),
    }
    try:
        im = Image.open(io.BytesIO(raw))
        info["format"] = im.format
        info["mode"] = im.mode
        info["width"] = im.size[0]
        info["height"] = im.size[1]
        if "A" in im.getbands():
            alpha = im.getchannel("A")
            w, h = im.size
            corners = [
                alpha.getpixel((0, 0)),
                alpha.getpixel((w - 1, 0)),
                alpha.getpixel((0, h - 1)),
                alpha.getpixel((w - 1, h - 1)),
            ]
            extrema = alpha.getextrema()
            info["alpha_corners"] = corners
            info["alpha_extrema"] = extrema
            info["corners_transparent"] = all(c == 0 for c in corners)
        else:
            info["corners_transparent"] = False
    except Exception as exc:
        info["pil_error"] = str(exc)
    if ext in {"png", "jpg", "webp"}:
        try:
            import subprocess

            ocr = subprocess.run(
                ["tesseract", str(path), "stdout", "--psm", "6"],
                capture_output=True,
                text=True,
                timeout=60,
            )
            info["ocr"] = " ".join(ocr.stdout.split())
        except Exception as exc:
            info["ocr_error"] = str(exc)
    return info


def record(test_id: str, kind: str, payload_note: dict, result: dict, extra: dict | None = None) -> dict:
    body = result.get("body") if isinstance(result.get("body"), dict) else {}
    usage = body.get("usage") if isinstance(body, dict) else None
    images = []
    saved = []
    if isinstance(body, dict) and isinstance(body.get("data"), list):
        for item in body["data"]:
            if isinstance(item, dict) and item.get("b64_json"):
                info = save_image(test_id if not images else f"{test_id}-{len(images)}", item)
                if info:
                    saved.append(info)
                images.append(item.get("media_type"))
    ok = result.get("status") == 200 and bool(saved or kind == "probe_reject_expected")
    # A probe that was expected to reject is "ok" only as a recorded HTTP result,
    # not as a generation. Generations are ok only when a file landed.
    if kind == "generation":
        ok = result.get("status") == 200 and bool(saved)
    elif kind == "probe":
        ok = result.get("status") is not None
    row = {
        "id": test_id,
        "kind": kind,
        "ok": ok,
        "status": result.get("status"),
        "wall_s": result.get("wall_s"),
        "request_bytes": result.get("request_bytes"),
        "error": result.get("error"),
        "headers": result.get("headers"),
        "usage": usage,
        "created": body.get("created") if isinstance(body, dict) else None,
        "response": strip_images(body if isinstance(body, dict) else {"_raw": body}),
        "saved": saved,
        "note": payload_note,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if extra:
        row.update(extra)
    append(row)
    cost = (usage or {}).get("cost")
    dims = ""
    if saved:
        dims = f" {saved[0].get('width')}x{saved[0].get('height')} {saved[0].get('format')}"
    log(
        f"{test_id} status={result.get('status')} wall={result.get('wall_s')}s "
        f"cost={cost}{dims} err={result.get('error')}"
    )
    return row


def base_payload(prompt: str) -> dict:
    return {
        "model": MODEL,
        "prompt": prompt,
        "n": 1,
        "resolution": "1K",
        "aspect_ratio": "1:1",
        "output_format": "png",
        "user": "smf-riverflow-v26-2026-10-29",
    }


def over_cap() -> bool:
    total = spent()
    if total >= COST_CAP_USD:
        log(f"STOP cost cap ${total:.4f} >= ${COST_CAP_USD}")
        return True
    return False


def make_swatches() -> list[dict]:
    colors = [
        (220, 30, 30),
        (230, 120, 20),
        (230, 200, 30),
        (30, 160, 50),
        (20, 180, 190),
        (30, 70, 200),
        (120, 40, 180),
        (200, 40, 140),
        (20, 20, 20),
        (140, 140, 140),
    ]
    refs = []
    for i, rgb in enumerate(colors, start=1):
        im = Image.new("RGB", (64, 64), rgb)
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        raw = buf.getvalue()
        path = REFS / f"swatch-{i:02d}.png"
        path.write_bytes(raw)
        refs.append(
            {
                "type": "image_url",
                "image_url": {"url": "data:image/png;base64," + base64.b64encode(raw).decode()},
            }
        )
    return refs


def data_url_from_saved(test_id: str) -> str | None:
    matches = sorted(IMG.glob(f"{test_id}.*"))
    if not matches:
        return None
    im = Image.open(matches[0]).convert("RGB")
    im.thumbnail((1024, 1024))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=85)
    raw = buf.getvalue()
    log(f"ref {test_id} jpeg {len(raw)} bytes")
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def ref_obj(url: str) -> dict:
    return {"type": "image_url", "image_url": {"url": url}}


def main() -> None:
    IMG.mkdir(parents=True, exist_ok=True)
    REFS.mkdir(parents=True, exist_ok=True)
    key = load_key()
    (ROOT / "rubric.json").write_text(json.dumps(RUBRIC, indent=2) + "\n")
    (ROOT / "prompts.json").write_text(json.dumps(PROMPTS, indent=2) + "\n")
    finished = done_ids()
    log(f"resume skip {sorted(finished)} spent ${spent():.4f}")

    # Snapshot the capability record we are testing against.
    if not (ROOT / "endpoints.json").exists():
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/images/models/sourceful/riverflow-v2.6-pro/endpoints",
            headers={"Authorization": f"Bearer {key}"},
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            (ROOT / "endpoints.json").write_bytes(resp.read())
        log("saved endpoints.json")

    def run_probe(test_id: str, payload: dict, timeout: int = 90) -> dict | None:
        if test_id in finished:
            log(f"skip {test_id}")
            return None
        note = {k: payload[k] for k in payload if k not in {"prompt"}}
        note["prompt_len"] = len(payload.get("prompt") or "")
        if "input_references" in payload:
            note["n_refs"] = len(payload["input_references"])
            note.pop("input_references", None)
        result = call(IMAGES_URL, payload, key, timeout)
        return record(test_id, "probe", note, result)

    def run_gen(test_id: str, payload: dict, timeout: int = 540) -> dict | None:
        if test_id in finished:
            log(f"skip {test_id}")
            return None
        if over_cap():
            append({"id": test_id, "kind": "skipped_cap", "ok": False, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
            return None
        note = {
            "resolution": payload.get("resolution"),
            "aspect_ratio": payload.get("aspect_ratio"),
            "size": payload.get("size"),
            "output_format": payload.get("output_format"),
            "background": payload.get("background"),
            "n_refs": len(payload.get("input_references") or []),
            "prompt": payload.get("prompt"),
        }
        log(f"START {test_id}")
        result = call(IMAGES_URL, payload, key, timeout)
        if result.get("status") in {429, 502, 503, 504} or (
            result.get("error") and result.get("status") is None
        ):
            log(f"retry {test_id} after {result.get('status') or result.get('error')}")
            time.sleep(8)
            result = call(IMAGES_URL, payload, key, timeout)
        return record(test_id, "generation", note, result)

    # --- contract probes. These should fail fast if the gateway validates. ---
    smoke_prompt = "a red circle on a white background, no text"
    run_probe("probe_n2", {**base_payload(smoke_prompt), "n": 2}, timeout=60)
    run_probe(
        "probe_aspect_16_1",
        {**base_payload(smoke_prompt), "aspect_ratio": "16:1"},
        timeout=540,
    )
    run_probe(
        "probe_size_1920x1080",
        {
            "model": MODEL,
            "prompt": smoke_prompt,
            "size": "1920x1080",
            "output_format": "png",
            "user": "smf-riverflow-v26-2026-10-29",
        },
        timeout=540,
    )
    run_probe(
        "probe_size_2048x128",
        {
            "model": MODEL,
            "prompt": smoke_prompt,
            "size": "2048x128",
            "output_format": "png",
            "user": "smf-riverflow-v26-2026-10-29",
        },
        timeout=540,
    )
    run_probe("probe_seed", {**base_payload(smoke_prompt), "seed": 7}, timeout=540)
    run_probe(
        "probe_reasoning_effort",
        {**base_payload(smoke_prompt), "reasoning": {"effort": "low"}},
        timeout=540,
    )
    run_probe(
        "probe_thinking_level",
        {
            **base_payload(smoke_prompt),
            "provider": {"options": {"sourceful": {"thinking_level": "low"}}},
        },
        timeout=540,
    )
    run_probe(
        "probe_provider_reasoning",
        {
            **base_payload(smoke_prompt),
            "provider": {"options": {"sourceful": {"reasoning": "low"}}},
        },
        timeout=540,
    )
    run_probe(
        "probe_resolution_8k",
        {**base_payload(smoke_prompt), "resolution": "8K"},
        timeout=120,
    )

    swatches = make_swatches()
    run_probe(
        "probe_refs_11",
        {**base_payload("ten colored squares, no text"), "input_references": swatches + swatches[:1]},
        timeout=120,
    )

    if "probe_chat" not in finished:
        chat_payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": "a red circle on white, no text"}],
            "modalities": ["image", "text"],
            "max_tokens": 64,
        }
        result = call(CHAT_URL, chat_payload, key, 90)
        record("probe_chat", "probe", {"endpoint": CHAT_URL, "modalities": ["image", "text"]}, result)

    # --- scored generations ---
    gens = [
        ("text_plate", base_payload(PROMPTS["text_plate"]), 540),
        ("label_lines", base_payload(PROMPTS["label_lines"]), 540),
        ("count_seven", base_payload(PROMPTS["count_seven"]), 540),
        ("spatial_trio", base_payload(PROMPTS["spatial_trio"]), 540),
        ("empty_bench", base_payload(PROMPTS["empty_bench"]), 540),
        (
            "aspect_5x4",
            {**base_payload(PROMPTS["aspect_5x4"]), "aspect_ratio": "5:4"},
            540,
        ),
        (
            "aspect_4x5",
            {**base_payload(PROMPTS["aspect_4x5"]), "aspect_ratio": "4:5"},
            540,
        ),
        (
            "wide_2k",
            {
                **base_payload(PROMPTS["wide_2k"]),
                "resolution": "2K",
                "aspect_ratio": "16:9",
            },
            540,
        ),
        (
            "cube_4k",
            {
                **base_payload(PROMPTS["cube_4k"]),
                "resolution": "4K",
                "aspect_ratio": "5:4",
            },
            600,
        ),
        (
            "mouse_alpha",
            {
                **base_payload(PROMPTS["mouse_alpha"]),
                "background": "transparent",
                "output_format": "png",
            },
            540,
        ),
        (
            "format_webp",
            {**base_payload(PROMPTS["format_webp"]), "output_format": "webp"},
            540,
        ),
        (
            "format_jpeg",
            {**base_payload(PROMPTS["format_jpeg"]), "output_format": "jpeg"},
            540,
        ),
        (
            "ten_swatches",
            {**base_payload(PROMPTS["ten_swatches"]), "input_references": swatches},
            540,
        ),
    ]
    for test_id, payload, timeout in gens:
        run_gen(test_id, payload, timeout)

    plate = data_url_from_saved("text_plate")
    spatial = data_url_from_saved("spatial_trio")
    if spatial and "edit_mug" not in finished:
        run_gen(
            "edit_mug",
            {
                **base_payload(PROMPTS["edit_mug"]),
                "input_references": [ref_obj(spatial)],
            },
            540,
        )
    if spatial and "edit_remove" not in finished:
        run_gen(
            "edit_remove",
            {
                **base_payload(PROMPTS["edit_remove"]),
                "input_references": [ref_obj(spatial)],
            },
            540,
        )
    if plate and spatial and "multi_compose" not in finished:
        run_gen(
            "multi_compose",
            {
                **base_payload(PROMPTS["multi_compose"]),
                "input_references": [ref_obj(plate), ref_obj(spatial)],
            },
            540,
        )

    # If a reasoning field was accepted and billed, run the same count prompt at xhigh.
    accepted = None
    if JSONL.exists():
        for line in JSONL.read_text().splitlines():
            row = json.loads(line)
            if row.get("id") in {
                "probe_reasoning_effort",
                "probe_thinking_level",
                "probe_provider_reasoning",
            } and row.get("status") == 200 and row.get("saved"):
                accepted = row["id"]
                break
    if accepted and "count_xhigh" not in finished and not over_cap():
        payload = base_payload(PROMPTS["count_seven"])
        if accepted == "probe_reasoning_effort":
            payload["reasoning"] = {"effort": "xhigh"}
        elif accepted == "probe_thinking_level":
            payload["provider"] = {"options": {"sourceful": {"thinking_level": "xhigh"}}}
        else:
            payload["provider"] = {"options": {"sourceful": {"reasoning": "xhigh"}}}
        run_gen("count_xhigh", payload, 600)
        log(f"xhigh arm used the field that {accepted} accepted")

    log(f"DONE spent ${spent():.4f}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
