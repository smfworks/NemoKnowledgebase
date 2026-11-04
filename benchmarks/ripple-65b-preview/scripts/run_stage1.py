#!/usr/bin/env python3
"""Parameterized Stage 1 / Core benchmark runner (SMF Inference Standard v0.1.1).

Usage:
  # Official A — new ranking (157 tests)
  python3 run_stage1.py --endpoint http://spark-56bc:8888/v1 --model MODEL --tag TAG \\
      --core-profile strict_v01 --timeout 300

  # Official B — historical Stage1 continuity (181 tests; default)
  python3 run_stage1.py --endpoint http://spark-56bc:8889/v1 --model MODEL --tag TAG
  python3 run_stage1.py ... --resume

  # Hardware-Friendly Gate (M10) — auto-ingested into results as hf_gate:
  #   --hf-gate PATH | SMF_HF_GATE_PATH | ./hf-gate.json | NemoKnowledgebase search by tag
  #   --require-hf-gate  abort if no gate file (new model intake)

See NemoKnowledgebase/smf-inference-standard-v0.1.md
"""
import sys
import asyncio
import functools
import json
import os
import time
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
print = functools.partial(print, flush=True)

import yaml
from smf_bench.api_client import APIClient, APIResponse
from smf_bench.evaluators import get_evaluator
from smf_bench.test_registry import TestCase
from smf_bench.hf_gate import (
    DEFAULT_SERVE_RECIPE_ID,
    STANDARD_VERSION,
    load_hf_gate,
)

# ─── Test suite definition (SMF Inference Standard v0.1) ─────────────────────
# See NemoKnowledgebase/smf-inference-standard-v0.1.md
# strict_v01 = Official A (157): tier0 five suites + tool_calling + writing
# legacy_181 = Official B (181): strict + freeform reasoning(8) + agentic(16)
STRICT_V01_SUITES = [
    ("suites/quality/tier0_deterministic/math.yaml", "math"),
    ("suites/quality/tier0_deterministic/coding.yaml", "coding"),
    ("suites/quality/tier0_deterministic/reasoning.yaml", "reasoning_tier0"),
    ("suites/quality/tier0_deterministic/instruction.yaml", "instruction"),
    ("suites/quality/tier0_deterministic/prose.yaml", "prose"),
    ("suites/quality/writing/writing.yaml", "writing"),
    ("suites/quality/tool_calling/tool_calling.yaml", "tool_calling"),
]
LEGACY_181_EXTRA = [
    ("suites/quality/reasoning/reasoning.yaml", "reasoning"),
    ("suites/quality/agentic/agentic.yaml", "agentic"),
]
CORE_PROFILES = {
    "strict_v01": STRICT_V01_SUITES,
    "legacy_181": STRICT_V01_SUITES + LEGACY_181_EXTRA,
}
# Back-compat alias used elsewhere
QUALITY_SUITES = CORE_PROFILES["legacy_181"]

# Reasoning models need more tokens to complete chain-of-thought before answer
REASONING_MODEL_DEFAULTS = {
    "max_tokens": 4096,
    "temperature": 0.6,
}


def load_tests(path: str) -> list[dict]:
    with open(path) as f:
        # Handle both single and multi-document YAML files
        docs = list(yaml.safe_load_all(f))
    tests = []
    for doc in docs:
        if doc is None:
            continue
        if isinstance(doc, list):
            tests.extend(doc)
        elif isinstance(doc, dict):
            tests.append(doc)
    return tests


def is_reasoning_model(model_name: str, tag: str = "") -> bool:
    """Check if this is a reasoning model that needs higher token limits."""
    combined = (model_name + " " + tag).lower()
    reasoning_indicators = ["nemotron", "deepseek", "o1", "o3", "qwen3", "gpt-oss", "glm", "minimax", "mistral-large-3", "kimi", "ox-alpha"]
    return any(ind in combined for ind in reasoning_indicators)


# Reasoning models generate long chain-of-thought before the answer.
# 120s is too tight — measured runs show 90–120s per request for 4096-token
# generations on reasoning models. Auto-raise to 300s for reasoning models
# unless the user explicitly set a timeout.
REASONING_TIMEOUT = 300.0
DEFAULT_TIMEOUT = 120.0


def _estimate_prompt_tokens(text: str) -> int:
    """Rough token estimate (~4 chars/token) for context budget checks."""
    return max(1, len(text) // 4)


def _find_latest_results(results_dir: str, tag: str) -> str | None:
    """Find the most recent results file matching the given tag."""
    import glob
    pattern = os.path.join(results_dir, f"stage1_{tag}_*.json")
    files = sorted(glob.glob(pattern), key=os.path.getmtime, reverse=True)
    return files[0] if files else None


def _load_completed_test_ids(filepath: str) -> set[str]:
    """Load test IDs that already have a pass/fail/skip result from a prior run."""
    with open(filepath) as f:
        data = json.load(f)
    tests = data.get("tests", [])
    # Only skip tests that have a definitive (non-error) status —
    # error tests should be retried, not skipped.
    return {t["test_id"] for t in tests
            if t.get("test_id") and t.get("status") in ("pass", "fail", "skip")}


def _load_prior_results(filepath: str) -> tuple[list[dict], dict, float]:
    """Load prior run results for merging. Returns (tests, by_category, wall_time)."""
    with open(filepath) as f:
        data = json.load(f)
    tests = data.get("tests", [])
    by_cat = data.get("by_category", {})
    wall = data.get("wall_time_seconds", 0.0)
    return tests, by_cat, wall


def _serve_recipe_id() -> str:
    return os.environ.get("SMF_SERVE_RECIPE_ID", DEFAULT_SERVE_RECIPE_ID)


def _save_results(filepath, tag, endpoint, model, reasoning, elapsed, by_cat, all_res,
                  core_profile="legacy_181", thinking="off", hf_gate=None):
    """Save results to JSON file (used for both incremental and final saves)."""
    total_pass = sum(v["pass"] for v in by_cat.values())
    total_fail = sum(v["fail"] for v in by_cat.values())
    total_error = sum(v["error"] for v in by_cat.values())
    grand_total = total_pass + total_fail + total_error
    grand_rate = total_pass / grand_total * 100 if grand_total > 0 else 0
    output = {
        "tag": tag, "endpoint": endpoint, "model": model,
        "timestamp": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        "reasoning_model": reasoning,
        "standard_version": STANDARD_VERSION,
        "core_profile": core_profile,
        "thinking": thinking,
        "reasoning_effort": os.environ.get("SMF_REASONING_EFFORT", "").strip().lower() or None,
        "serve_recipe_id": _serve_recipe_id(),
        "wall_time_seconds": round(elapsed, 1),
        "summary": {
            "total": grand_total, "passed": total_pass,
            "failed": total_fail, "error": total_error,
            "pass_rate": round(grand_rate, 1),
        },
        "by_category": by_cat,
        "tests": all_res,
    }
    if hf_gate is not None:
        output["hf_gate"] = hf_gate
    with open(filepath, "w") as f:
        json.dump(output, f, indent=2)
    return output


def _parse_harmony_response(resp: APIResponse) -> APIResponse:
    """Parse GPT-OSS Harmony format response from /v1/completions.

    Harmony output format uses channels delimited by special tokens:
      <|channel|>analysis<|message|>...reasoning...<|end|>
      <|channel|>commentary<|message|>...commentary...<|end|>
      <|channel|>final<|message|>...answer...<|end|>

    The model may also output without the <|channel|> prefix, like:
      analysis<|message|>...<|end|>final<|message|>...<|end|>

    Extract the 'final' channel content as the answer text, and 'analysis'
    channel content as reasoning.
    """
    import re
    text = resp.text

    reasoning = ""
    answer = ""

    # Pattern to extract channel content: optional <|channel|>, channel name,
    # <|message|> delimiter, then content until <|end|> or next channel
    # Group 1 = channel name, Group 2 = content
    channel_pattern = r'(?:<\|channel\|>)?(analysis|commentary|final)<\|message\|>(.*?)(?:<\|end\|>|<\|channel\|>|$)'
    channels = re.findall(channel_pattern, text, re.DOTALL)

    if channels:
        for ch_name, ch_content in channels:
            ch_content = ch_content.strip()
            if ch_name == "final":
                answer = ch_content
            elif ch_name == "analysis":
                reasoning = ch_content
            elif ch_name == "commentary":
                # Commentary is supplementary; don't use it for answer
                pass
    else:
        # Fallback: try simpler pattern without <|message|> delimiter
        # Format might be: "analysisReasoning<|end|>finalAnswer"
        final_match = re.search(r'final(.*?)(?:<\|end\|>|$)', text, re.DOTALL)
        if final_match:
            answer = final_match.group(1).strip()

        analysis_match = re.search(r'analysis(.*?)(?:<\|end\|>|final|commentary)', text, re.DOTALL)
        if analysis_match:
            reasoning = analysis_match.group(1).strip()

    # If still no answer, use raw text with channel markers stripped
    if not answer:
        cleaned = re.sub(r'<\|channel\|>', '', text)
        cleaned = re.sub(r'<\|message\|>', '', cleaned)
        cleaned = re.sub(r'<\|end\|>', '', cleaned)
        cleaned = re.sub(r'^(analysis|commentary|final)\s*', '', cleaned).strip()
        answer = cleaned

    resp.text = answer
    resp.reasoning = reasoning
    return resp


async def run_benchmark(endpoint: str, model: str, tag: str, timeout: float = 120.0,
                        use_completions: bool = False, tokenizer_path: str = "",
                        resume: bool = False, core_profile: str = "legacy_181",
                        thinking: str = "off",
                        hf_gate_path: str | None = None,
                        require_hf_gate: bool = False,
                        api_key: str = "dummy"):
    """Run quality suites against the given endpoint (SMF Inference Standard v0.1).

    core_profile:
      strict_v01  — Official A (157): tier0 + tool_calling + writing
      legacy_181  — Official B (181): strict + reasoning(8) + agentic(16)
    thinking:
      off — send chat_template_kwargs enable_thinking=false (Official A default)
      on  — model default thinking (document in result metadata; not for ranking)

    If use_completions=True, send requests via /v1/completions instead of
    /v1/chat/completions. This bypasses vLLM's chat parser (e.g. the Harmony
    reasoning parser used by GPT-OSS models that requires downloading a vocab
    file from Azure blob storage, which may be unavailable in Docker).

    When use_completions=True and tokenizer_path is provided, the HuggingFace
    tokenizer is loaded to apply the chat template client-side before sending
    the raw prompt to /v1/completions, preserving instruction-following quality.

    If resume=True, load the most recent results file for this tag and skip
    tests that already completed (pass/fail/skip). Error tests are retried.
    Results are merged into a new file.

    hf_gate_path / SMF_HF_GATE_PATH / cwd hf-gate.json: M10 hardware-friendly gate.
    require_hf_gate: abort if no gate file (new model intake).
    """
    if core_profile not in CORE_PROFILES:
        print(f"ERROR: unknown --core-profile {core_profile!r}; choose from {list(CORE_PROFILES)}")
        return None
    suite_list = CORE_PROFILES[core_profile]
    if thinking not in ("off", "on"):
        print(f"ERROR: --thinking must be 'off' or 'on', got {thinking!r}")
        return None
    suites_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "suites")

    # ── M10: Hardware-Friendly Gate ─────────────────────────────────────────
    try:
        hf_gate = load_hf_gate(
            hf_gate_path,
            tag=tag,
            cwd=os.getcwd(),
            required=require_hf_gate,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: hf_gate: {e}")
        return None
    if hf_gate:
        print(f"  hf_gate: loaded ({hf_gate.get('resolve_reason', '?')})")
        print(f"           path={hf_gate.get('path')}")
        print(f"           verdict={hf_gate.get('verdict')} "
              f"arch={hf_gate.get('architecture')} "
              f"smoke={hf_gate.get('serve_smoke')}")
        if hf_gate.get("verdict") == "red":
            print("ERROR: hf_gate verdict=red — do not start Core (standard §5.5.3). "
                  "Fix serve/identity or override only for unofficial debug.")
            return None
        if hf_gate.get("verdict") == "yellow":
            print("  ⚠ hf_gate verdict=yellow — official allowed but must be labeled")
    else:
        print("  hf_gate: not found (optional unless --require-hf-gate)")

    # Load tokenizer for chat template application if using completions mode
    _tokenizer = None
    if use_completions:
        tok_path = tokenizer_path or os.environ.get("SMF_BENCH_TOKENIZER_PATH", "")
        if not tok_path:
            print("ERROR: --use-completions requires --tokenizer-path or SMF_BENCH_TOKENIZER_PATH env var")
            return None
        from transformers import AutoTokenizer
        _tokenizer = AutoTokenizer.from_pretrained(tok_path)
        print(f"Loaded tokenizer from {tok_path} for client-side chat template")
    
    print(f"  Core profile: {core_profile} (standard {STANDARD_VERSION})")
    print(f"  Thinking mode: {thinking}")
    print(f"  Reasoning effort: {os.environ.get('SMF_REASONING_EFFORT', '').strip().lower() or '(unset)'}")
    print(f"  serve_recipe_id: {_serve_recipe_id()}")
    # Load all test suites for this profile
    all_tests = []
    for path, label in suite_list:
        full_path = os.path.join(suites_dir, path.replace("suites/", ""))
        if not os.path.exists(full_path):
            print(f"  ⚠ Skipping {label}: file not found at {full_path}")
            continue
        tests = load_tests(full_path)
        print(f"  Loaded {len(tests):3d} {label} tests")
        all_tests.extend([(t, label) for t in tests])
    
    print(f"\nTotal: {len(all_tests)} tests across {len(suite_list)} suites")
    print(f"Endpoint: {endpoint}")
    print(f"Model:    {model}")
    print(f"Tag:      {tag}")
    print()
    
    # Determine token/temperature defaults
    reasoning = is_reasoning_model(model, tag)
    defaults = REASONING_MODEL_DEFAULTS if reasoning else {}
    if reasoning:
        print(f"  (reasoning model detected: using max_tokens={defaults['max_tokens']})")

    # ── Fix 3: Timeout auto-tuning ──────────────────────────────────────────
    # If the caller didn't explicitly raise the timeout and this is a reasoning
    # model, auto-raise to 300s. Measured runs show reasoning models routinely
    # take 90–120s for 4096-token generations; 120s default cuts them off.
    effective_timeout = timeout
    if reasoning and timeout <= DEFAULT_TIMEOUT + 1:
        effective_timeout = REASONING_TIMEOUT
        print(f"  (auto-raising timeout: 120s → {REASONING_TIMEOUT:.0f}s for reasoning model)")
    print(f"  (per-request timeout: {effective_timeout:.0f}s)")
    print()

    # ── Fix 2: Resume from prior results ────────────────────────────────────
    results_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
    os.makedirs(results_dir, exist_ok=True)
    prior_completed: set[str] = set()
    prior_results: list[dict] = []
    prior_by_cat: dict = {}
    prior_wall_time: float = 0.0

    if resume:
        prior_file = _find_latest_results(results_dir, tag)
        if prior_file:
            prior_completed = _load_completed_test_ids(prior_file)
            prior_results, prior_by_cat, prior_wall_time = _load_prior_results(prior_file)
            skipped = len([t for t in all_tests if t[0]["id"] in prior_completed])
            remaining = len(all_tests) - skipped
            print(f"  📂 Resume: loaded {len(prior_completed)} completed test IDs from {os.path.basename(prior_file)}")
            print(f"     Skipping {skipped} completed tests, {remaining} to run (including retried errors)")
            print()
        else:
            print(f"  📂 Resume: no prior results found for tag '{tag}', starting fresh")
            print()

    # Set up results file early for incremental saving
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(results_dir, f"stage1_{tag}_{timestamp}.json")
    
    async with APIClient(
        base_url=endpoint,
        model=model,
        api_key=api_key,
        timeout=effective_timeout,
    ) as client:
        healthy = await client.health_check()
        if not healthy:
            print("ERROR: Endpoint not reachable")
            return None
        print(f"Endpoint healthy: {healthy}")
        print()

        # ── Fix 1: Pre-flight context validation ───────────────────────────
        # Query the server's max_model_len and verify max_tokens + prompt
        # will fit. If max_tokens is too large for the context window, auto-cap
        # it to leave room for the prompt.
        server_max_len = await client.get_max_model_len()
        if server_max_len is not None:
            print(f"  Server max_model_len: {server_max_len} tokens")
            # Check if the reasoning default max_tokens (4096) leaves room
            # for at least a small prompt
            requested_max = defaults.get("max_tokens", 1024)
            if requested_max >= server_max_len:
                # max_tokens >= context window: every request would fail with HTTP 400
                # Auto-cap to leave at least 512 tokens for the prompt
                capped = max(256, server_max_len - 512)
                print(f"  ⚠ max_tokens={requested_max} >= max_model_len={server_max_len}")
                print(f"     Auto-capping max_tokens to {capped} (leaving 512 for prompt)")
                REASONING_MODEL_DEFAULTS["max_tokens"] = capped
                defaults["max_tokens"] = capped
            elif requested_max > server_max_len * 0.8:
                # max_tokens eats >80% of context — risky for long prompts
                capped = max(256, server_max_len - 1024)
                print(f"  ⚠ max_tokens={requested_max} > 80% of max_model_len={server_max_len}")
                print(f"     Auto-capping max_tokens to {capped} (leaving 1024 for prompt)")
                REASONING_MODEL_DEFAULTS["max_tokens"] = capped
                defaults["max_tokens"] = capped
            else:
                print(f"  ✓ max_tokens={requested_max} fits within max_model_len={server_max_len}")
        else:
            print(f"  ⚠ Could not query server max_model_len — skipping context validation")
            print(f"     If you see HTTP 400 'context length' errors, the server's")
            print(f"     --max-model-len is too small. Restart vLLM with a larger value.")
        print()

        # Initialize results containers — seed with prior results when resuming
        results_by_cat: dict = {}
        all_results: list[dict] = []
        if resume and prior_results:
            # Deep-copy prior by_category counts so we don't mutate the loaded dict
            import copy
            # Never seed error rows: they are retried and would double-count
            # (pass + leftover 429) if left in all_results.
            seeded = [t for t in prior_results if t.get("status") in ("pass", "fail", "skip")]
            results_by_cat = copy.deepcopy(prior_by_cat)
            for cat, counts in list(results_by_cat.items()):
                counts["error"] = 0
            all_results = list(seeded)
            print(f"  Seeded results with {len(all_results)} prior test results (errors dropped for retry)")
            print()

        start_time = time.perf_counter()
        new_count = 0  # Track only newly-run tests for incremental save cadence

        for i, (test, suite_label) in enumerate(all_tests):
            test_id = test["id"]
            category = test.get("category", suite_label)

            # ── Fix 2: Skip already-completed tests ─────────────────────────
            if test_id in prior_completed:
                continue

            prompt = test["prompt"]
            messages = [{"role": "user", "content": prompt}]
            
            # Use test-specific max_tokens or model default
            max_tokens = test.get("max_tokens", defaults.get("max_tokens", 1024))
            temperature = test.get("temperature", defaults.get("temperature", 0.3))
            
            # ── Fix 1: Per-test context safety cap ──────────────────────────
            # Even with the pre-flight check, individual test prompts vary
            # in length. If this prompt is long, cap max_tokens further.
            if server_max_len is not None:
                prompt_tokens = _estimate_prompt_tokens(prompt)
                safe_max = server_max_len - prompt_tokens - 64  # 64-token safety margin
                if max_tokens > safe_max:
                    max_tokens = max(64, safe_max)
            
            # Build kwargs
            chat_kwargs = {"max_tokens": max_tokens, "temperature": temperature}
            if test.get("metadata", {}).get("tools"):
                chat_kwargs["tools"] = test["metadata"]["tools"]
            # Qwen3.6 / similar: thinking on by default — Official A calib uses off
            if thinking == "off":
                chat_kwargs["chat_template_kwargs"] = {"enable_thinking": False}
                # Some OpenRouter endpoints forbid disabling reasoning
                # (`effort: none` / `enabled: false` → HTTP 400). Official A
                # ranking is thinking-off; send the lowest effort that still
                # lands content. Do NOT add these names to reasoning_indicators
                # (that would bump every test to max_tokens=4096).
                ml = model.lower()
                if ml == "minimax/minimax-m3.1-flash:free":
                    # MiniMax M3.1 Flash free (2026-10-19): catalog
                    # reasoning.mandatory=true, efforts
                    # max/xhigh/high/medium/low, default max.
                    # effort=none and enabled=false are HTTP 400.
                    # enable_thinking=false still thinks on identity
                    # (18 reasoning tokens) and the bat-and-ball item
                    # (55). effort=low alone lands content with
                    # reasoning_tokens=0. Combining it with
                    # enable_thinking=false still thinks and flipped
                    # the bat-and-ball answer ($0.10 vs $0.05).
                    # Exact slug. minimax is already in
                    # reasoning_indicators; do not add a broader token.
                    chat_kwargs.pop("chat_template_kwargs", None)
                    chat_kwargs["reasoning"] = {"effort": "low"}
                elif "gemini-4-argon" in ml:
                    # Gemini 4 Argon (2026-10-13): default and
                    # enable_thinking=false both land content "4" with
                    # reasoning_tokens=0. effort=none and enabled=false
                    # are HTTP 400. Do not copy Gemini 3.8's effort=low.
                    # Do not add "gemini" to reasoning_indicators.
                    pass
                elif "gemini" in ml:
                    # Gemini 3.8 Flash: disable 400; enable_thinking=false
                    # is ignored. effort=low lands content with
                    # reasoning_tokens=0. Do not add "gemini" to
                    # reasoning_indicators.
                    chat_kwargs["reasoning"] = {"effort": "low"}
                elif "muse" in ml:
                    # Muse Spark 1.3 (2026-09-02) and Muse Wonder
                    # (2026-10-12): disable is HTTP 400; enable_thinking=false
                    # is ignored. Lowest listed effort that lands content is
                    # minimal. Wonder 2+2: minimal content '4', 20 reasoning
                    # tokens; low still finish=length at max_tokens=64.
                    # Not true off. Do not add "muse" to reasoning_indicators.
                    chat_kwargs["reasoning"] = {"effort": "minimal"}
                elif "nex" in ml and "next" not in ml:
                    # Nex-N2.5 (2026-09-08): vendor documents
                    # reasoning_effort=none as non-thinking. Default is
                    # medium/adaptive. Do not add "nex" to
                    # reasoning_indicators. "next" contains "nex";
                    # Qwen3.8-Flash-Next must not take this branch.
                    chat_kwargs["reasoning"] = {"effort": "none"}
                    # Free OpenRouter endpoint keepalives non-stream
                    # requests with whitespace and never closes; SSE
                    # (`: OPENROUTER PROCESSING` then tokens) is the
                    # path that actually returns content.
                    chat_kwargs["stream"] = True
                elif "hy4" in ml:
                    # Hy4 preview (2026-09-09): effort=none and
                    # enabled=false both land content with
                    # reasoning_tokens=0. Default / effort=low /
                    # enable_thinking=false still think (~36–59
                    # tokens). Do not add "hy4"/"tencent" to
                    # reasoning_indicators.
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif "deepseek-v4.1" in ml or "v4.1-flash" in ml:
                    # DeepSeek V4.1 Flash (2026-09-10): default and
                    # enable_thinking=false still think (~32–37
                    # tokens on 2+2). effort=none and enabled=false
                    # land content with reasoning_tokens=0. Do not add
                    # "v4.1" to reasoning_indicators (deepseek already
                    # matches).
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif "gpt-6-luna" in ml:
                    # GPT-6 Luna / Luna Pro (2026-09-22): default and
                    # enable_thinking=false still think (~37–68
                    # tokens on 2+2). effort=none and enabled=false
                    # land content with reasoning_tokens=0. Do not
                    # copy Astra Pro's effort=low analogue (Astra
                    # forbids disable; Luna allows none). Do not add
                    # "luna"/"gpt-6" to reasoning_indicators (luna
                    # would also match lunaris).
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif ml in ("fireworks/ember-1", "xiaomi/mimo-v2.6-pro"):
                    # Ember-1 and MiMo-V2.6-Pro (2026-09-24): default
                    # and enable_thinking=false still think (Ember ~34
                    # reasoning tokens, MiMo ~2). effort=none and
                    # enabled=false land content with
                    # reasoning_tokens=0. effort=low/minimal still
                    # think. Exact slug match — do not add ember,
                    # fireworks, mimo, or xiaomi to
                    # reasoning_indicators (keeps max_tokens=1024).
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif ml == "mistralai/mistral-large-4-0":
                    # Mistral Large 4.0 re-smoke 2026-10-29: catalog
                    # lists high/none, default high, mandatory false.
                    # Provider rejects effort=none and enabled=false
                    # (HTTP 400; supported high/low/medium). The
                    # 2026-10-06 none path is no longer accepted.
                    # enable_thinking=false still thinks. effort=low
                    # alone lands content "4" with 31 reasoning tokens.
                    # Pairing low with the flag raises that to 35.
                    # Not true off. Pop the flag. Lowest provider
                    # effort. Do not add mistral-large-4 to
                    # reasoning_indicators (keeps max_tokens=1024).
                    chat_kwargs.pop("chat_template_kwargs", None)
                    chat_kwargs["reasoning"] = {"effort": "low"}
                elif ml == "stepfun/step-5-preview":
                    # Step 5 Preview (2026-10-10): reasoning is mandatory
                    # (catalog supported_efforts high/medium/low, default
                    # medium). effort=none and enabled=false → HTTP 400.
                    # Default and enable_thinking=false still think (44
                    # reasoning tokens on 2+2). effort=low and
                    # effort=minimal both land content "4" with 26
                    # reasoning tokens. Use catalog effort=low. Exact
                    # slug — do not add stepfun or step to
                    # reasoning_indicators (keeps max_tokens=1024).
                    chat_kwargs["reasoning"] = {"effort": "low"}
                elif ml == "nvidia/nemotron-3.5-super-vl:free":
                    # Nemotron 3.5 Super VL free (2026-10-15): catalog
                    # reasoning.mandatory=false, no effort list.
                    # Default thinks (49 reasoning tokens on 2+2).
                    # enable_thinking=false still thinks (37).
                    # effort=none, alone or with enable_thinking=false,
                    # lands content "4" with reasoning_tokens=0.
                    # Exact slug — "nemotron" is already in
                    # reasoning_indicators from Lightning; do not add
                    # a broader token.
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif ml == "reflection/beam-1.0-501b-a23b":
                    # Beam 1.0 (2026-10-16): reasoning.mandatory=true.
                    # Catalog efforts max/xhigh/high/medium/low, default
                    # max. effort=none and enabled=false → HTTP 400
                    # ("cannot be disabled"). Default and
                    # enable_thinking=false still return a reasoning
                    # string (150 chars on 2+2) with content "4".
                    # usage has no reasoning_tokens field. effort=low
                    # lands content "4" with a shorter reasoning string
                    # (134 chars). Lowest listed effort. Exact slug —
                    # do not add reflection or beam to
                    # reasoning_indicators (keeps max_tokens=1024).
                    chat_kwargs["reasoning"] = {"effort": "low"}
                elif ml == "z-ai/glm-5.3-prime":
                    # GLM-5.3-Prime (2026-10-16): reasoning.mandatory=true.
                    # Catalog efforts max/high/low, default max.
                    # enable_thinking=false still thinks (29 reasoning
                    # tokens on 2+2). effort=low lands content "4" with
                    # reasoning_tokens=0. Exact slug. The max arm is
                    # SMF_REASONING_EFFORT=max with --thinking on, not
                    # this branch. Do not add a broader glm token.
                    chat_kwargs["reasoning"] = {"effort": "low"}
                elif ml == "moonshotai/kimi-k3.1-pro":
                    # Kimi K3.1 Pro (2026-10-23): reasoning.mandatory=false.
                    # Catalog efforts max/high/low/none, default max,
                    # default_enabled true. Default thinks (44 reasoning
                    # tokens on 2+2). enable_thinking=false still thinks
                    # (26 on 2+2, 79 on bat-and-ball). effort=none lands
                    # content with reasoning_tokens=0, alone or with
                    # enable_thinking=false. Bat-and-ball stays $0.05.
                    # Exact slug. "kimi" is already in reasoning_indicators.
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif ml == "openai/gpt-6.1-terra":
                    # GPT-6.1 Terra (2026-10-27): reasoning.mandatory=false.
                    # Catalog efforts max/xhigh/high/medium/low/none, default
                    # medium, default_enabled true. Default 2+2 and
                    # enable_thinking=false both land content "4" with
                    # reasoning_tokens=0. That is a false clean. The
                    # bat-and-ball item with enable_thinking=false still
                    # spends 25 reasoning tokens and an empty reasoning
                    # string, content "$0.05". effort=none lands the same
                    # answer with reasoning_tokens=0, alone or with
                    # enable_thinking=false. Exact slug. Do not add gpt-6
                    # or terra to reasoning_indicators.
                    chat_kwargs["reasoning"] = {"effort": "none"}
                elif ml == "stealth/crouton-alpha":
                    # Crouton Alpha (2026-11-03): reasoning.mandatory=true.
                    # Catalog efforts max/xhigh/high/medium/low/minimal, no
                    # none, default max. Default 2+2 at max_tokens=64 lands
                    # finish=length with empty content and 0 reported
                    # reasoning tokens (hidden think ate the cap).
                    # enable_thinking=false does the same — a false clean.
                    # effort=minimal at max_tokens=64 lands content "4",
                    # finish=stop, reasoning_tokens=0, and at the 64 cap the
                    # visible answer alone fills the budget, so the reasoning
                    # phase is suppressed, not hidden. Bat-and-ball at
                    # minimal answers $0.05 with 0 reasoning tokens.
                    # Exact slug. Do not add crouton or stealth to
                    # reasoning_indicators (stealth would match every
                    # stealth slug). Pop the flag: mandatory reasoning,
                    # the flag is ignored anyway.
                    chat_kwargs.pop("chat_template_kwargs", None)
                    chat_kwargs["reasoning"] = {"effort": "minimal"}
                elif ml == "tencent/hy4":
                    # Hy4 official (2026-11-04): reasoning.mandatory=false.
                    # Catalog efforts high/low/none, default high,
                    # default_enabled true. Default and enable_thinking=false
                    # both burn the whole 64 cap on hidden reasoning and
                    # return nothing (64 reasoning tokens each on 2+2).
                    # effort=none lands visible content with 0 reasoning
                    # tokens; paired with enable_thinking=false the
                    # bat-and-ball item answers fully at 0 reasoning tokens.
                    # Matches the hy4-preview analogue after a fresh smoke.
                    # Do not add tencent or hy4 to reasoning_indicators.
                    chat_kwargs["reasoning"] = {"effort": "none"}
            elif thinking == "on":
                # Explicit effort. Catalog default is not a recorded payload.
                # SMF_REASONING_EFFORT=max is the reasoning-max arm. It is not
                # Official A. Short YAML caps (128-1024) fill with reasoning
                # and leave content empty, so floor those to 4096. YAML stays.
                effort = os.environ.get("SMF_REASONING_EFFORT", "").strip().lower()
                if effort:
                    chat_kwargs["reasoning"] = {"effort": effort}
                    if max_tokens < 4096:
                        max_tokens = 4096
                        chat_kwargs["max_tokens"] = max_tokens

            if test_id == "v3.math.easy.01":
                print(
                    "  payload_check",
                    "reasoning=" + json.dumps(chat_kwargs.get("reasoning")),
                    "ctk=" + json.dumps(chat_kwargs.get("chat_template_kwargs")),
                    "model=" + model,
                )

            if use_completions:
                # Apply chat template client-side, then use /v1/completions
                # GPT-OSS Harmony format uses analysis/commentary/final channels
                messages = [{"role": "user", "content": prompt}]
                templated = _tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
                # Stop tokens to prevent generation beyond the answer
                # No stop tokens — let the model generate the full Harmony
                # response (analysis + commentary + final channels), then parse
                # out the final channel. Stopping on <|end|> would kill generation
                # after the first (analysis) channel before reaching final.
                stop_tokens = ["<|start|>"]
                resp = await client.completion(templated, max_tokens=max_tokens,
                                               temperature=temperature,
                                               stop=stop_tokens)
                # Parse Harmony response: extract final channel content
                if resp.succeeded and resp.text:
                    resp = _parse_harmony_response(resp)
            else:
                resp = await client.chat(messages, **chat_kwargs)
            
            if resp.error:
                print(f"  ❌ ERR  {test_id:45s} [{category:14s}] {resp.error[:50]}")
                results_by_cat.setdefault(category, {"pass": 0, "fail": 0, "error": 0})
                results_by_cat[category]["error"] += 1
                all_results.append({
                    "test_id": test_id, "category": category, "suite": suite_label,
                    "status": "error", "error": resp.error[:200],
                    "elapsed": resp.elapsed,
                })
                continue
            
            tc = TestCase.from_dict(test)
            evaluator_name = test.get("evaluator", "text_contains")
            try:
                evaluator = get_evaluator(evaluator_name)
            except KeyError:
                print(f"  ⚠️ SKIP {test_id:45s} [{category:14s}] — unknown evaluator '{evaluator_name}'")
                results_by_cat.setdefault(category, {"pass": 0, "fail": 0, "error": 0})
                results_by_cat[category]["error"] += 1
                all_results.append({
                    "test_id": test_id, "category": category, "suite": suite_label,
                    "status": "skip", "passed": False,
                    "score": 0.0, "detail": f"Unknown evaluator: {evaluator_name}",
                    "elapsed": resp.elapsed, "tokens_used": 0,
                    "evaluator": evaluator_name,
                })
                continue
            result = evaluator(resp, tc)
            
            icon = "✅" if result.passed else "❌"
            status = "PASS" if result.passed else "FAIL"
            print(f"  {icon} {status:4s} {test_id:45s} [{category:14s}] {resp.elapsed:5.1f}s {result.detail[:55]}")
            
            results_by_cat.setdefault(category, {"pass": 0, "fail": 0, "error": 0})
            if result.passed:
                results_by_cat[category]["pass"] += 1
            else:
                results_by_cat[category]["fail"] += 1
            
            all_results.append({
                "test_id": test_id, "category": category, "suite": suite_label,
                "status": status.lower(), "passed": result.passed,
                "score": result.score, "detail": result.detail[:200],
                "elapsed": resp.elapsed,
                "tokens_used": resp.usage.get("total_tokens", 0) if resp.usage else 0,
                "prompt_tokens": (resp.usage or {}).get("prompt_tokens"),
                "completion_tokens": (resp.usage or {}).get("completion_tokens"),
                "reasoning_tokens": ((resp.usage or {}).get("completion_tokens_details") or {}).get("reasoning_tokens"),
                "cost": (resp.usage or {}).get("cost"),
                "finish_reason": resp.finish_reason,
                "evaluator": evaluator_name,
            })
            # Incremental save every 10 new tests
            new_count += 1
            if new_count % 10 == 0:
                _save_results(results_file, tag, endpoint, model, reasoning,
                              time.perf_counter() - start_time + prior_wall_time,
                              results_by_cat, all_results, core_profile=core_profile,
                              thinking=thinking, hf_gate=hf_gate)
        
        elapsed_total = time.perf_counter() - start_time + prior_wall_time
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"RESULTS BY CATEGORY — {tag}")
    print(f"{'='*70}")
    total_pass = 0
    total_fail = 0
    total_error = 0
    for cat in sorted(results_by_cat.keys()):
        r = results_by_cat[cat]
        total = r["pass"] + r["fail"] + r["error"]
        rate = r["pass"] / total * 100 if total > 0 else 0
        print(f"  {cat:16s}: {r['pass']:3d}/{total:3d} passed ({rate:5.1f}%)  [fail={r['fail']}, err={r['error']}]")
        total_pass += r["pass"]
        total_fail += r["fail"]
        total_error += r["error"]
    
    grand_total = total_pass + total_fail + total_error
    grand_rate = total_pass / grand_total * 100 if grand_total > 0 else 0
    print(f"  {'─'*50}")
    print(f"  {'TOTAL':16s}: {total_pass:3d}/{grand_total:3d} passed ({grand_rate:5.1f}%)  [fail={total_fail}, err={total_error}]")
    print(f"  Wall time: {elapsed_total:.1f}s")
    if hf_gate:
        print(f"  hf_gate.verdict: {hf_gate.get('verdict')}")
    print(f"{'='*70}")

    # Final save — same path as incremental (no second timestamped file)
    output = _save_results(
        results_file, tag, endpoint, model, reasoning,
        elapsed_total, results_by_cat, all_results,
        core_profile=core_profile,
        thinking=thinking,
        hf_gate=hf_gate,
    )
    print(f"\nResults saved to: {results_file}")

    return output


def main():
    parser = argparse.ArgumentParser(description="Stage 1 / Core benchmark runner (SMF Inference Standard v0.1.1)")
    parser.add_argument("--endpoint", required=True, help="OpenAI-compatible endpoint URL (e.g. http://spark-56bc:8889/v1)")
    parser.add_argument("--model", required=True, help="Model name as served by the endpoint")
    parser.add_argument("--tag", required=True, help="Short tag for this model (e.g. nemotron-3-nano-30b)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"Per-request timeout in seconds (default: {DEFAULT_TIMEOUT:.0f}; "
                             f"auto-raised to {REASONING_TIMEOUT:.0f}s for reasoning models)")
    parser.add_argument("--use-completions", action="store_true",
                        help="Use /v1/completions instead of /v1/chat/completions (bypasses chat parser)")
    parser.add_argument("--tokenizer-path", default="",
                        help="Path to HuggingFace tokenizer dir for client-side chat template (required with --use-completions)")
    parser.add_argument("--resume", action="store_true",
                        help="Resume from the most recent results file for this tag: "
                             "skip tests that already passed/failed/skip, retry errors, "
                             "merge all results into a new file")
    parser.add_argument("--core-profile", default="legacy_181",
                        choices=sorted(CORE_PROFILES.keys()),
                        help="Suite set: strict_v01 (Official A, 157 tests) or "
                             "legacy_181 (Official B, 181 tests, historical Stage1). "
                             "Default legacy_181 for continuity; use strict_v01 for new official ranks.")
    parser.add_argument("--thinking", default="off", choices=["off", "on"],
                        help="Thinking/CoT: off (Official A ranking default) or on "
                             "(optional diagnostic arm). Sends chat_template_kwargs "
                             "enable_thinking=false when off.")
    parser.add_argument(
        "--hf-gate",
        default=None,
        metavar="PATH",
        help="Path to hf-gate.json or hf-gate.md (M10). "
             "Also: SMF_HF_GATE_PATH env, ./hf-gate.json, or NemoKnowledgebase search by --tag.",
    )
    parser.add_argument(
        "--require-hf-gate",
        action="store_true",
        help="Abort if no hardware friendly gate file is found (required for new model intake).",
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("OPENROUTER_API_KEY", "dummy"),
        help="API key for the endpoint (Bearer auth). Defaults to OPENROUTER_API_KEY env var or 'dummy'.",
    )
    args = parser.parse_args()

    result = asyncio.run(run_benchmark(
        args.endpoint, args.model, args.tag, args.timeout,
        use_completions=args.use_completions,
        tokenizer_path=args.tokenizer_path,
        resume=args.resume,
        core_profile=args.core_profile,
        thinking=args.thinking,
        hf_gate_path=args.hf_gate,
        require_hf_gate=args.require_hf_gate,
        api_key=args.api_key,
    ))
    if result is None:
        sys.exit(1)


if __name__ == "__main__":
    main()