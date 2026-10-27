#!/usr/bin/env python3
"""Launch Cold Iron for openai/gpt-6.1-terra on OpenRouter.

Thinking-off arm is reasoning.effort=none plus the runner's
enable_thinking=false. Smoke 2026-10-27: enable_thinking=false alone
still spends reasoning tokens on the bat-and-ball item. effort=none
zeros them, alone or with the flag, and the answer stays $0.05.
Exact slug branch in run_stage1.py. Do not add a broader token.
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
TAG = "cal-gpt61-terra-or-strict-v01"
MODEL = "openai/gpt-6.1-terra"
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
    raw = data.get("data") or data
    # /v1/key includes a label and org ids. Keep timestamp and usage only.
    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "usage": raw.get("usage") if isinstance(raw, dict) else None,
    }
    path.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"usage_snapshot={payload['usage']}", flush=True)


def main() -> None:
    key = load_key()
    os.environ["OPENROUTER_API_KEY"] = key
    os.environ["SMF_SERVE_RECIPE_ID"] = "OpenRouter-cloud"
    os.environ["SMF_REASONING_EFFORT"] = "none"
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
        "off",
        "--timeout",
        "300",
        "--api-key",
        key,
    ]
    os.execvp(cmd[0], cmd)


if __name__ == "__main__":
    main()
