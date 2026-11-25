#!/usr/bin/env python3
"""Runs 2 and 3. Same prompt and decoding params. Paired seeds. Does not touch run 1."""

import hashlib
import json
import os
import subprocess
from pathlib import Path

from run_arms import PROMPT_PATH, ROOT, load_key, run_arm

PAIRS = [
    (2, 20261126),
    (3, 20261127),
]
ARMS = [("think-off", False), ("think-on", True)]


def main():
    prompt = PROMPT_PATH.read_text()
    digest = hashlib.sha256(prompt.encode()).hexdigest()
    key = load_key()
    print("prompt_sha256", digest, flush=True)
    print("prompt_bytes", len(prompt.encode()), flush=True)
    print("key_present", bool(key), flush=True)
    summary = []
    for run_n, seed in PAIRS:
        for name, think in ARMS:
            dest = f"{name}-r{run_n}"
            print("START", dest, "seed", seed, flush=True)
            meta = run_arm(name, think, prompt, key, dest=dest, seed=seed)
            if meta.get("error") and not meta.get("done"):
                print("RETRY", dest, str(meta.get("error"))[:300], flush=True)
                failed = ROOT / f"{dest}-transport-fail"
                if failed.exists():
                    import shutil
                    shutil.rmtree(failed)
                (ROOT / dest).rename(failed)
                meta = run_arm(name, think, prompt, key, dest=dest, seed=seed)
                meta["retry_of_transport"] = True
                (ROOT / dest / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
            summary.append({
                "dest": dest,
                "seed": seed,
                "think": think,
                "http_status": meta.get("http_status"),
                "error": meta.get("error"),
                "wall_s": meta.get("wall_s"),
                "done_reason": meta.get("done_reason"),
                "eval_count": meta.get("eval_count"),
                "tokens_per_s": meta.get("tokens_per_s"),
                "html_bytes": meta.get("html_bytes"),
                "thinking_chars": meta.get("thinking_chars"),
                "passes": (meta.get("checks") or {}).get("pass_count"),
            })
            print("passes", summary[-1]["passes"], flush=True)
    (ROOT / "summary-r2-r3.json").write_text(json.dumps({
        "prompt_sha256": digest,
        "arms": summary,
    }, indent=2) + "\n")
    arms = ",".join(row["dest"] for row in summary if (ROOT / row["dest"] / "game.html").exists())
    print("PROBE", arms, flush=True)
    env = os.environ.copy()
    env["PROBE_ARMS"] = arms
    env["PROBE_OUT"] = "browser-probe-r2-r3.json"
    probe = subprocess.run(
        ["node", str(ROOT / "browser_probe.cjs")],
        cwd=str(ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    (ROOT / "browser-probe-r2-r3.log").write_text((probe.stdout or "") + "\n" + (probe.stderr or ""))
    print("probe_exit", probe.returncode, flush=True)
    if probe.returncode != 0:
        print((probe.stderr or "")[:1500], flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
