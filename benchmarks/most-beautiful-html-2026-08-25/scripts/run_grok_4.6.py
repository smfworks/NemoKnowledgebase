#!/usr/bin/env python3
"""Stream an OpenRouter one-shot HTML generation. Saves content incrementally."""
import json
import os
import time
import urllib.request
from pathlib import Path

out_dir = Path(__file__).resolve().parent
prompt = (out_dir / "prompt.txt").read_text()

MODEL = "x-ai/grok-4.6"
TITLE = "SMF Grok 4.6 most-beautiful HTML one-shot"

payload = {
    "model": MODEL,
    "messages": [{"role": "user", "content": prompt}],
    "max_tokens": 65536,
    "temperature": 0.7,
    "stream": True,
}


def _load_key() -> str:
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


key = _load_key()
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://smfworks.com",
        "X-Title": TITLE,
        "Accept": "text/event-stream",
    },
    method="POST",
)

t0 = time.perf_counter()
content_parts = []
reasoning_parts = []
usage = None
finish_reason = None
model_returned = None
gen_id = None
http_status = None
err = None

try:
    with urllib.request.urlopen(req, timeout=1800) as r:
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
                if len(content_parts) % 40 == 0:
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

elapsed = time.perf_counter() - t0
content = "".join(content_parts)
reasoning = "".join(reasoning_parts)
(out_dir / "content.md").write_text(content)
if reasoning:
    (out_dir / "reasoning.md").write_text(reasoning)
meta = {
    "model_requested": MODEL,
    "http_status": http_status,
    "elapsed_s": elapsed,
    "error": err,
    "usage": usage,
    "id": gen_id,
    "model_returned": model_returned,
    "finish_reason": finish_reason,
    "content_chars": len(content),
    "reasoning_chars": len(reasoning),
    "stream": True,
    "prompt_bytes": len(prompt.encode()),
}
(out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
print(json.dumps(meta, indent=2)[:2500])
if not content:
    raise SystemExit(1)
