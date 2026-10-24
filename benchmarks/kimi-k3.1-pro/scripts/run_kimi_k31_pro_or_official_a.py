#!/usr/bin/env python3
"""Launch Cold Iron for moonshotai/kimi-k3.1-pro on OpenRouter.

Thinking-off arm is reasoning.effort=none (smoke 2026-10-23: content
lands, reasoning_tokens=0). enable_thinking=false still thinks. Exact
slug branch in run_stage1.py. Do not add a broader token.
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
TAG = "cal-kimi-k31-pro-or-strict-v01"
MODEL = "moonshotai/kimi-k3.1-pro"
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
    usage = payload["data"].get("usage")
    print(f"usage_snapshot={usage}", flush=True)


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
