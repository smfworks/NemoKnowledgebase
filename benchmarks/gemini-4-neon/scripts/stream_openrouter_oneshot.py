#!/usr/bin/env python3
"""Stream one OpenRouter chat completion into a workspace directory.

Usage:
  OPENROUTER_API_KEY may be unset; key is loaded from ~/.hermes/.env.
  OUT_DIR must contain prompt.txt. Writes content.md, reasoning.md, meta.json.

  OUT_DIR=... MODEL=moonshotai/kimi-k3.1-pro python3 stream_openrouter_oneshot.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

out_dir = Path(os.environ.get("OUT_DIR", ".")).resolve()
model = os.environ.get("MODEL", "stealth/ox-alpha")
title = os.environ.get("X_TITLE", f"SMF OpenRouter one-shot {out_dir.name}")
prompt = (out_dir / "prompt.txt").read_text()


def load_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    for path in (
        Path.home() / ".hermes" / ".env",
        Path.home() / ".hermes" / "profiles" / "nemo" / ".env",
        Path.home() / ".hermes" / "profiles" / "aiona" / ".env",
    ):
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if line.startswith("OPENROUTER_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("OPENROUTER_API_KEY not found in env or ~/.hermes/.env")


payload = {
    "model": model,
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": int(os.environ.get("MAX_TOKENS", "65536")),
    "temperature": float(os.environ.get("TEMPERATURE", "0.7")),
    "stream": True,
}
effort = os.environ.get("REASONING_EFFORT", "").strip()
if effort:
    payload["reasoning"] = {"effort": effort}

req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {load_key()}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smfworks.com",
        "X-Title": title,
        "Accept": "text/event-stream",
    },
    method="POST",
)

t0 = time.perf_counter()
content_parts, reasoning_parts = [], []
usage = finish_reason = model_returned = gen_id = http_status = err = None

try:
    with urllib.request.urlopen(req, timeout=int(os.environ.get("TIMEOUT_S", "1800"))) as r:
        http_status = r.status
        buf = b""
        while True:
            chunk = r.read(4096)
            if not chunk:
                break
            buf += chunk
            while b"\n" in buf:
                line, buf = buf.split(b"\n", 1)
                line = line.strip()
                if not line or not line.startswith(b"data:"):
                    continue
                data = line[5:].strip()
                if data == b"[DONE]":
                    buf = b""
                    break
                try:
                    obj = json.loads(data.decode())
                except json.JSONDecodeError:
                    continue
                gen_id = obj.get("id") or gen_id
                model_returned = obj.get("model") or model_returned
                if obj.get("usage"):
                    usage = obj["usage"]
                chs = obj.get("choices") or []
                if not chs:
                    continue
                ch = chs[0]
                finish_reason = ch.get("finish_reason") or finish_reason
                delta = ch.get("delta") or {}
                if delta.get("content"):
                    content_parts.append(delta["content"])
                if delta.get("reasoning") or delta.get("reasoning_content"):
                    reasoning_parts.append(
                        delta.get("reasoning") or delta.get("reasoning_content")
                    )
                if content_parts and len(content_parts) % 40 == 0:
                    (out_dir / "content.md").write_text("".join(content_parts))
except Exception as e:
    err = {"type": type(e).__name__, "str": str(e)}
    if hasattr(e, "read"):
        try:
            err["body"] = e.read().decode()[:8000]
        except Exception:
            pass
    if hasattr(e, "code"):
        http_status = e.code

content = "".join(content_parts)
reasoning = "".join(reasoning_parts)
(out_dir / "content.md").write_text(content)
if reasoning:
    (out_dir / "reasoning.md").write_text(reasoning)
meta = {
    "model_requested": model,
    "http_status": http_status,
    "elapsed_s": time.perf_counter() - t0,
    "error": err,
    "usage": usage,
    "id": gen_id,
    "model_returned": model_returned,
    "finish_reason": finish_reason,
    "content_chars": len(content),
    "reasoning_chars": len(reasoning),
    "stream": True,
    "reasoning_effort": effort or None,
}
(out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
print(json.dumps(meta, indent=2)[:2500])
if not content:
    raise SystemExit(1)
