#!/usr/bin/env python3
"""Launch thinking-on Official A arm for deepseek/deepseek-v4.1-flash.

Diagnostic only — not Official A ranking. Loads OPENROUTER_API_KEY from
~/.hermes/.env. Snapshots /v1/key usage before exec'ing run_stage1.py.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/home/mikesai1/workspace/smf-bench")
ENV = Path("/home/mikesai1/.hermes/.env")
TAG = "cal-dsv41-flash-or-strict-v01-thinking-on"
MODEL = "deepseek/deepseek-v4.1-flash"
ENDPOINT = "https://openrouter.ai/api/v1"


def load_key() -> str:
    for line in ENV.read_text().splitlines():
        s = line.strip()
        if s.startswith("OPENROUTER_API_KEY="):
            return s.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY missing from ~/.hermes/.env")


def snapshot_usage(key: str, path: Path) -> None:
    req = urllib.request.Request(
        f"{ENDPOINT}/key",
        headers={"Authorization": f"Bearer {key}"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "data": data.get("data") or data,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"usage_before={payload['data'].get('usage')}", flush=True)


def main() -> None:
    key = load_key()
    os.environ["OPENROUTER_API_KEY"] = key
    os.environ["SMF_SERVE_RECIPE_ID"] = "OpenRouter-cloud"
    os.chdir(ROOT)
    results = ROOT / "results"
    results.mkdir(exist_ok=True)
    snapshot_usage(key, results / f"{TAG}.usage_before.json")
    cmd = [
        sys.executable,
        "-u",
        str(ROOT / "run_stage1.py"),
        "--endpoint",
        ENDPOINT,
        "--model",
        MODEL,
        "--tag",
        TAG,
        "--core-profile",
        "strict_v01",
        "--thinking",
        "on",
        "--timeout",
        "300",
        "--api-key",
        key,
    ]
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
