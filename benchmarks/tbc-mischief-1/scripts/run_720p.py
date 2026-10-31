#!/usr/bin/env python3
"""720p rerolls of the four pinned board tiles. Same prompts, seed 42."""
import base64
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path("/home/mikesai1/NemoVault/evals/mischief-variant-board")
PROMPTS = json.loads((ROOT / "prompts.json").read_text())
LOG = ROOT / "runs.jsonl"
KEEP = ["mug-roll", "rain-car", "door-open", "fox-turn"]
CAP = 1.00


def key() -> str:
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    for path in (Path.home() / ".hermes/.env", Path.home() / ".hermes/profiles/nemo/.env"):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("no key")


API_KEY = key()


def spent() -> float:
    total = 0.0
    for line in LOG.read_text().splitlines():
        if not line.strip():
            continue
        cost = (json.loads(line).get("usage") or {}).get("cost")
        if isinstance(cost, (int, float)):
            total += cost
    return total


def done_ids() -> set[str]:
    ids = set()
    for line in LOG.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("status") in ("completed", "rejected", "failed"):
            ids.add(row["id"])
    return ids


def append(row: dict) -> None:
    with LOG.open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps({k: row.get(k) for k in ("id", "status", "http", "wall_s", "usage", "error")}), flush=True)


def post(url: str, payload: dict | None = None) -> tuple[int, dict | str]:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw[:1500].decode("utf-8", "replace")
        return e.code, parsed


def get(url: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read())


def data_url(still_id: str) -> str:
    raw = (ROOT / "stills" / f"{still_id}.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def main() -> None:
    by_id = {v["id"]: v for v in PROMPTS["variants"]}
    for vid in KEEP:
        job_id = f"{vid}-720p"
        if job_id in done_ids():
            print("skip", job_id, flush=True)
            continue
        if spent() + 0.05 > CAP:
            raise SystemExit(f"cap before {job_id}")
        variant = by_id[vid]
        payload = {
            "model": "tbc/mischief-1",
            "prompt": variant["prompt"],
            "duration": 5,
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "seed": 42,
            "frame_images": [{
                "type": "image_url",
                "image_url": {"url": data_url(variant["still"])},
                "frame_type": "first_frame",
            }],
        }
        t0 = time.time()
        http, body = post("https://openrouter.ai/api/v1/videos", payload)
        if http >= 400 or not isinstance(body, dict):
            append({"id": job_id, "status": "rejected", "http": http, "error": body, "wall_s": round(time.time() - t0, 2)})
            continue
        poll = body.get("polling_url") or f"https://openrouter.ai/api/v1/videos/{body.get('id')}"
        last = body
        status = body.get("status", "pending")
        while status not in ("completed", "failed", "cancelled", "expired") and time.time() - t0 < 600:
            time.sleep(5)
            _, last = get(poll)
            status = last.get("status") if isinstance(last, dict) else "unknown"
            print("poll", job_id, status, round(time.time() - t0, 1), flush=True)
        wall = round(time.time() - t0, 2)
        if status != "completed":
            append({"id": job_id, "status": status or "timeout", "wall_s": wall, "error": last})
            continue
        dest = ROOT / "clips" / f"{vid}-720p.mp4"
        url = (last.get("unsigned_urls") or [f"https://openrouter.ai/api/v1/videos/{last.get('id')}/content?index=0"])[0]
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
        with urllib.request.urlopen(req, timeout=180) as r:
            blob = r.read()
        dest.write_bytes(blob)
        append({
            "id": job_id,
            "status": "completed",
            "http": http,
            "wall_s": wall,
            "job_id": last.get("id"),
            "generation_id": last.get("generation_id"),
            "usage": last.get("usage"),
            "bytes": len(blob),
            "file": str(dest),
            "sent": {"duration": 5, "resolution": "720p", "aspect_ratio": "16:9", "seed": 42},
        })
    print("720P_DONE", "spent", round(spent(), 4), flush=True)


if __name__ == "__main__":
    main()
