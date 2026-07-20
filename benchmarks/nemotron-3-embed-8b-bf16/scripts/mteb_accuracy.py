#!/usr/bin/env python3
"""Accuracy eval via MTEB (same framework NVIDIA used for RTEB / MMTEB retrieval).

Presets:
  smoke   — SciFact only (minutes; validates wiring + prefixes)
  quick   — SciFact + NFCorpus + ArguAna (standard BEIR retrieval, ~tens of min)
  beir    — common BEIR retrieval set used in MTEB eng
  rteb-en — RTEB(eng, beta) — English slice of NVIDIA's retrieval benchmark
  rteb    — full RTEB(beta) — long-running, closest to card reporting

NVIDIA reported NDCG@10 on RTEB with max sequence length 4096; our serve is
max_model_len=8192 (truncate END on API).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import mteb

sys.path.insert(0, str(Path(__file__).resolve().parent))
from client import DEFAULT_BASE, DEFAULT_MODEL, RECIPE_ID, wait_ready  # noqa: E402
from mteb_encoder import SparkNemotron3EmbedEncoder  # noqa: E402

PRESETS: dict[str, list[str] | str] = {
    "smoke": ["SciFact"],
    "quick": ["SciFact", "NFCorpus", "ArguAna"],
    "beir": [
        "SciFact",
        "NFCorpus",
        "ArguAna",
        "FiQA2018",
        "TRECCOVID",
        "QuoraRetrieval",
    ],
    "rteb-en": "RTEB(eng, beta)",
    "rteb": "RTEB(beta)",
}


def resolve_tasks(preset: str, extra: list[str]) -> list:
    if preset not in PRESETS:
        raise SystemExit(f"unknown preset {preset}; choose from {list(PRESETS)}")
    spec = PRESETS[preset]
    if isinstance(spec, str):
        tasks = list(mteb.get_benchmark(spec).tasks)
    else:
        tasks = list(mteb.get_tasks(tasks=spec))
    if extra:
        tasks.extend(list(mteb.get_tasks(tasks=extra)))
    return tasks


def main() -> int:
    ap = argparse.ArgumentParser(description="MTEB accuracy for Spark Nemotron-3-Embed")
    ap.add_argument("--base", default=DEFAULT_BASE, help="e.g. http://127.0.0.1:18001")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--preset", default="smoke", choices=list(PRESETS))
    ap.add_argument("--tasks", nargs="*", default=[], help="extra task names")
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--out-dir", default="", help="results directory")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    wait_ready(args.base)
    tasks = resolve_tasks(args.preset, args.tasks)
    print(f"Preset={args.preset}  n_tasks={len(tasks)}")
    for t in tasks:
        print(f"  - {t.metadata.name}")

    model = SparkNemotron3EmbedEncoder(
        base_url=args.base,
        model_name=args.model,
        batch_size=args.batch_size,
    )

    out_dir = Path(
        args.out_dir
        or (
            Path(__file__).resolve().parents[1]
            / "results"
            / f"mteb_{args.preset}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        )
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "serve_recipe_id": RECIPE_ID,
        "model": args.model,
        "base": args.base,
        "preset": args.preset,
        "batch_size": args.batch_size,
        "tasks": [t.metadata.name for t in tasks],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "mteb_version": mteb.__version__,
        "framework": "https://github.com/embeddings-benchmark/mteb",
        "note": "NVIDIA card used RTEB / MMTEB Retrieval / ViDoRe-V3 text with seqlen 4096",
    }
    (out_dir / "run_meta.json").write_text(json.dumps(meta, indent=2))

    # MTEB caches under ~/.cache/mteb by default
    results = mteb.evaluate(
        model,
        tasks=tasks,
        encode_kwargs={"batch_size": args.batch_size},
        overwrite_strategy="always" if args.overwrite else "only-missing",
        show_progress_bar=True,
    )

    # Persist summary
    summary_path = out_dir / "summary.json"
    try:
        # ModelResult API varies slightly by version — best-effort dump
        if hasattr(results, "to_dict"):
            payload = results.to_dict()
        elif hasattr(results, "model_dump"):
            payload = results.model_dump()
        else:
            payload = {"repr": str(results)}
        summary_path.write_text(json.dumps(payload, indent=2, default=str))
    except Exception as e:  # noqa: BLE001
        summary_path.write_text(json.dumps({"error": str(e), "repr": repr(results)}, indent=2))

    print("\n=== Results (primary metrics) ===")
    try:
        # Iterate task results if available
        task_results = getattr(results, "task_results", None) or getattr(results, "results", None)
        if task_results is None and hasattr(results, "__iter__"):
            task_results = list(results)
        if task_results is not None:
            for tr in task_results:
                name = getattr(tr, "task_name", None) or getattr(tr, "name", str(tr))
                scores = getattr(tr, "scores", None) or getattr(tr, "main_score", None)
                print(f"  {name}: {scores}")
        else:
            print(results)
    except Exception:
        print(results)

    print(f"\nMeta: {out_dir / 'run_meta.json'}")
    print(f"Summary: {summary_path}")
    print("Tag: serve_recipe_id=" + RECIPE_ID)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
