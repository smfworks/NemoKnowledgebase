#!/usr/bin/env python3
"""Frozen two-arm sailing-game generation. Do not change the prompt or params."""

import hashlib
import json
import re
import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompt.txt"
ENDPOINT = "http://michaels-mac-mini.tail09297b.ts.net:11434/api/chat"
MODEL = "inkling-2-mini:latest"
NUM_PREDICT = 32768
TEMPERATURE = 0.7
SEED = 20261125
KEEP_ALIVE = "45m"
SILENCE_S = 600
ARMS = [("think-off", False), ("think-on", True)]


def load_key():
    envp = Path.home() / ".hermes/profiles/nemo/.env"
    for line in envp.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if "INKLING_MAC" in k and "API_KEY" in k:
            return v.strip().strip('"').strip("'")
    return ""


def extract_html(content: str):
    text = content or ""
    fence = re.search(r"```(?:html)?\s*\n(.*?)```", text, re.I | re.S)
    if fence:
        page = fence.group(1).strip()
        return page, "fence"
    lower = text.lower()
    start = lower.find("<!doctype html")
    if start < 0:
        start = lower.find("<html")
    if start >= 0:
        end = lower.rfind("</html>")
        if end >= start:
            return text[start : end + len("</html>")].strip(), "tags"
        return text[start:].strip(), "tags-unclosed"
    return "", "none"


def scripts_of(html: str):
    return re.findall(r"<script[^>]*>(.*?)</script>", html, re.I | re.S)


def check_page(html: str, done_reason: str):
    notes = []
    scripts = scripts_of(html) if html else []
    syntax_ok = False
    syntax_errors = []
    if not scripts:
        syntax_errors.append("no inline script")
    else:
        syntax_ok = True
        for i, src in enumerate(scripts):
            path = ROOT / f"_syntax_{i}.js"
            path.write_text(src)
            proc = subprocess.run(
                ["node", "--check", str(path)],
                capture_output=True,
                text=True,
            )
            path.unlink(missing_ok=True)
            if proc.returncode != 0:
                syntax_ok = False
                syntax_errors.append((proc.stderr or proc.stdout or "check failed")[:500])

    def has(pat):
        return re.search(pat, html or "", re.I) is not None

    net_hits = []
    for pat in (r"https?://", r"fetch\s*\(", r"XMLHttpRequest", r"WebSocket"):
        if has(pat):
            net_hits.append(pat)

    arrow_ok = has(r"ArrowLeft") and has(r"ArrowRight")
    if not arrow_ok:
        arrow_ok = has(r"\b37\b") and has(r"\b39\b")

    wind_ok = (
        has(r"wind")
        and (has(r"Math\.cos") or has(r"Math\.sin"))
        and not has(r"ArrowUp")
        and not has(r"throttle")
    )
    buoy_ok = len(re.findall(r"buoy", html or "", re.I)) >= 3
    timer_ok = has(r"timer|elapsed") and has(r"\+\+|Date\.now|performance\.now")
    irons_ok = has(r"irons") and has(r"fillText|textContent|innerHTML")
    items = {
        "1_single_html": bool(html) and has(r"<html"),
        "2_no_network": bool(html) and not net_hits,
        "3_node_check": syntax_ok,
        "4_canvas": has(r"<canvas"),
        "5_raf": has(r"requestAnimationFrame"),
        "6_arrows": arrow_ok,
        "7_wind_not_throttle": wind_ok,
        "8_three_buoys": buoy_ok,
        "9_timer": timer_ok,
        "10_irons_text": irons_ok,
        "11_done_stop": done_reason == "stop",
    }
    return {
        "items": items,
        "pass_count": sum(1 for v in items.values() if v),
        "item_count": len(items),
        "net_hits": net_hits,
        "syntax_errors": syntax_errors,
        "script_count": len(scripts),
        "notes": notes,
        "item_12_browser": "pending",
    }


def run_arm(name, think, prompt, key, dest=None, seed=SEED):
    out = ROOT / (dest or name)
    out.mkdir(parents=True, exist_ok=True)
    body = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True,
        "think": think,
        "keep_alive": KEEP_ALIVE,
        "options": {
            "temperature": TEMPERATURE,
            "seed": seed,
            "num_predict": NUM_PREDICT,
        },
    }
    (out / "request.json").write_text(json.dumps(body, indent=2) + "\n")
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )
    content_parts = []
    thinking_parts = []
    final = {}
    t0 = time.time()
    first_token_s = None
    raw_path = out / "stream.ndjson"
    status = None
    error = None
    try:
        with urllib.request.urlopen(req, timeout=SILENCE_S) as resp, raw_path.open("w") as raw:
            status = resp.status
            while True:
                line = resp.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace")
                raw.write(text)
                raw.flush()
                text = text.strip()
                if not text:
                    continue
                try:
                    chunk = json.loads(text)
                except json.JSONDecodeError:
                    continue
                msg = chunk.get("message") or {}
                piece = msg.get("content") or ""
                thought = msg.get("thinking") or ""
                if piece or thought:
                    if first_token_s is None:
                        first_token_s = round(time.time() - t0, 3)
                if piece:
                    content_parts.append(piece)
                if thought:
                    thinking_parts.append(thought)
                if chunk.get("done"):
                    final = chunk
    except Exception as e:
        err_body = ""
        if hasattr(e, "read"):
            try:
                err_body = e.read().decode(errors="replace")[:1500]
            except Exception:
                err_body = ""
        error = f"{type(e).__name__}: {getattr(e, 'code', '')} {err_body or e}"
        status = getattr(e, "code", status)

    content = "".join(content_parts)
    thinking = "".join(thinking_parts)
    wall = round(time.time() - t0, 3)
    (out / "content.md").write_text(content)
    (out / "thinking.md").write_text(thinking)
    html, how = extract_html(content)
    html_path = out / "game.html"
    if html:
        html_path.write_text(html + ("\n" if not html.endswith("\n") else ""))
    done_reason = final.get("done_reason")
    checks = check_page(html, done_reason)
    eval_count = final.get("eval_count")
    eval_ns = final.get("eval_duration")
    tok_s = None
    if eval_count and eval_ns:
        tok_s = round(eval_count / (eval_ns / 1e9), 2)
    meta = {
        "arm": name,
        "dest": dest or name,
        "seed": seed,
        "think": think,
        "http_status": status,
        "error": error,
        "wall_s": wall,
        "ttft_s": first_token_s,
        "done": bool(final.get("done")),
        "done_reason": done_reason,
        "prompt_eval_count": final.get("prompt_eval_count"),
        "eval_count": eval_count,
        "eval_duration_ns": eval_ns,
        "tokens_per_s": tok_s,
        "load_duration_ns": final.get("load_duration"),
        "total_duration_ns": final.get("total_duration"),
        "content_chars": len(content),
        "thinking_chars": len(thinking),
        "html_extract": how,
        "html_bytes": len(html.encode()) if html else 0,
        "checks": checks,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({k: meta[k] for k in (
        "arm", "http_status", "error", "wall_s", "ttft_s", "done_reason",
        "eval_count", "tokens_per_s", "content_chars", "thinking_chars",
        "html_extract", "html_bytes",
    )}, indent=2))
    print("passes", checks["pass_count"], "/", checks["item_count"])
    return meta


def main():
    prompt = PROMPT_PATH.read_text()
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    key = load_key()
    print("prompt_sha256", digest)
    print("prompt_bytes", len(prompt.encode()))
    print("key_present", bool(key))
    summary = []
    for name, think in ARMS:
        print("START", name, flush=True)
        meta = run_arm(name, think, prompt, key)
        summary.append(meta)
        # Transport failure only: one same-body retry. A finished generation is never rerun.
        if meta["error"] and not meta["done"]:
            print("RETRY", name, meta["error"][:300], flush=True)
            failed = ROOT / f"{name}-transport-fail"
            if failed.exists():
                shutil.rmtree(failed)
            (ROOT / name).rename(failed)
            meta2 = run_arm(name, think, prompt, key)
            meta2["retry_of_error"] = meta["error"]
            (ROOT / name / "meta.json").write_text(json.dumps(meta2, indent=2) + "\n")
            summary[-1] = meta2
    (ROOT / "summary.json").write_text(json.dumps({
        "prompt_sha256": digest,
        "arms": [{k: a[k] for k in (
            "arm", "think", "http_status", "error", "wall_s", "ttft_s",
            "done_reason", "eval_count", "tokens_per_s", "html_bytes",
            "thinking_chars",
        ) if k in a} | {"passes": a.get("checks", {}).get("pass_count")} for a in summary],
    }, indent=2) + "\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
