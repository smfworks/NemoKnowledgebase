#!/usr/bin/env python3
"""Probe then run the mischief variant board. Writes JSONL as each job finishes."""
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
CAP = 1.00
MODEL = "tbc/mischief-1"


def key() -> str:
    if os.environ.get("OPENROUTER_API_KEY"):
        return os.environ["OPENROUTER_API_KEY"]
    for path in (Path.home() / ".hermes/.env", Path.home() / ".hermes/profiles/nemo/.env"):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY missing")


API_KEY = key()


def data_url(still_id: str) -> str:
    raw = (ROOT / "stills" / f"{still_id}.jpg").read_bytes()
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


def spent() -> float:
    total = 0.0
    if not LOG.exists():
        return 0.0
    for line in LOG.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        cost = (row.get("usage") or {}).get("cost")
        if isinstance(cost, (int, float)):
            total += cost
    return total


def done_ids() -> set[str]:
    ids = set()
    if not LOG.exists():
        return ids
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


def post_json(url: str, payload: dict | None = None, timeout: int = 120) -> tuple[int, dict | str]:
    data = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST" if payload is not None else "GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read()
            try:
                return r.status, json.loads(body)
            except json.JSONDecodeError:
                return r.status, body[:500].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw[:1500].decode("utf-8", "replace")
        return e.code, parsed


def get_json(url: str) -> tuple[int, dict | str]:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw[:1500].decode("utf-8", "replace")
        return e.code, parsed


def download(url: str, dest: Path) -> int:
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        blob = r.read()
    dest.write_bytes(blob)
    return len(blob)


def frame_payload(still_id: str, frame_type: str = "first_frame") -> list:
    return [
        {
            "type": "image_url",
            "image_url": {"url": data_url(still_id)},
            "frame_type": frame_type,
        }
    ]


def run_job(job_id: str, payload: dict, expect_bill: bool, out_name: str | None) -> None:
    if job_id in done_ids():
        print("skip", job_id, flush=True)
        return
    if expect_bill and spent() + 0.02 > CAP:
        append({"id": job_id, "status": "stopped", "reason": "cap", "spent": spent()})
        raise SystemExit(f"cap hit before {job_id}")
    t0 = time.time()
    http, body = post_json("https://openrouter.ai/api/v1/videos", payload)
    if http >= 400:
        append({
            "id": job_id,
            "status": "rejected",
            "http": http,
            "wall_s": round(time.time() - t0, 2),
            "error": body,
            "sent": {k: payload.get(k) for k in ("model", "duration", "resolution", "aspect_ratio", "seed", "generate_audio") if k in payload},
            "had_frame": "frame_images" in payload,
        })
        return
    job = body if isinstance(body, dict) else {"raw": body}
    poll = job.get("polling_url") or f"https://openrouter.ai/api/v1/videos/{job.get('id')}"
    status = job.get("status", "pending")
    last = job
    deadline = time.time() + 600
    while status not in ("completed", "failed", "cancelled", "expired") and time.time() < deadline:
        time.sleep(5)
        ph, last = get_json(poll)
        if ph >= 400:
            append({"id": job_id, "status": "failed", "http": ph, "error": last, "job_id": job.get("id"), "wall_s": round(time.time() - t0, 2)})
            return
        status = last.get("status") if isinstance(last, dict) else "unknown"
        print("poll", job_id, status, round(time.time() - t0, 1), flush=True)
    wall = round(time.time() - t0, 2)
    if status != "completed":
        append({"id": job_id, "status": status or "timeout", "http": http, "wall_s": wall, "error": last, "job_id": job.get("id")})
        return
    dest = None
    nbytes = None
    if out_name:
        urls = last.get("unsigned_urls") or []
        url = urls[0] if urls else f"https://openrouter.ai/api/v1/videos/{last.get('id')}/content?index=0"
        dest = ROOT / "clips" / out_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        nbytes = download(url, dest)
    usage = last.get("usage") if isinstance(last, dict) else None
    append({
        "id": job_id,
        "status": "completed",
        "http": http,
        "wall_s": wall,
        "job_id": last.get("id"),
        "generation_id": last.get("generation_id"),
        "usage": usage,
        "bytes": nbytes,
        "file": str(dest) if dest else None,
        "sent": {k: payload.get(k) for k in ("duration", "resolution", "aspect_ratio", "seed") if k in payload},
    })
    if spent() > CAP:
        raise SystemExit(f"cap exceeded after {job_id}: {spent()}")


def main() -> None:
    still = "mug"
    base = {
        "model": MODEL,
        "prompt": "The camera holds still. A thin ribbon of steam rises from the coffee.",
        "duration": 3,
        "resolution": "480p",
        "aspect_ratio": "16:9",
    }
    # Probes that should reject before billing.
    run_job("probe-duration-4", {**base, "duration": 4, "frame_images": frame_payload(still)}, False, None)
    run_job("probe-aspect-9-16", {**base, "aspect_ratio": "9:16", "frame_images": frame_payload(still)}, False, None)
    run_job("probe-1080p", {**base, "resolution": "1080p", "frame_images": frame_payload(still)}, False, None)
    run_job("probe-last-frame", {**base, "frame_images": frame_payload(still, "last_frame")}, False, None)
    run_job("probe-audio-true", {**base, "generate_audio": True, "frame_images": frame_payload(still), "seed": 42}, True, "probe-audio.mp4")
    run_job("probe-text-only", dict(base), True, "probe-text-only.mp4")
    run_job("probe-data-url-3s", {**base, "frame_images": frame_payload(still), "seed": 42}, True, "probe-data-url-3s.mp4")
    probe_row = None
    if LOG.exists():
        for line in LOG.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("id") == "probe-data-url-3s":
                probe_row = row
    if not probe_row or probe_row.get("status") != "completed":
        print("STOP board: data-url probe did not complete", probe_row, flush=True)
        return

    for variant in PROMPTS["variants"]:
        payload = {
            "model": MODEL,
            "prompt": variant["prompt"],
            "duration": 5,
            "resolution": "480p",
            "aspect_ratio": "16:9",
            "seed": 42,
            "frame_images": frame_payload(variant["still"]),
        }
        run_job(variant["id"], payload, True, f"{variant['id']}-480p-r1.mp4")

    # Two more seeded repeats of mug-steam.
    steam = next(v for v in PROMPTS["variants"] if v["id"] == "mug-steam")
    for n in (2, 3):
        payload = {
            "model": MODEL,
            "prompt": steam["prompt"],
            "duration": 5,
            "resolution": "480p",
            "aspect_ratio": "16:9",
            "seed": 42,
            "frame_images": frame_payload("mug"),
        }
        run_job(f"mug-steam-r{n}", payload, True, f"mug-steam-480p-r{n}.mp4")

    print("BOARD_DONE", "spent", round(spent(), 4), flush=True)


if __name__ == "__main__":
    main()
