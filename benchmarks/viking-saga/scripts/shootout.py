#!/usr/bin/env python3
"""
OpenRouter Video Generation Shootout: MiniMax H3 vs FLUX 3
===========================================================
Same prompts, side by side. Measures generation time, cost,
resolution, moderation differences, and quality indicators.
"""

import json
import os
import time
import subprocess
import urllib.request
import urllib.error
from datetime import datetime

# Load API key from global .env
with open("/home/mikesai1/.hermes/.env") as f:
    for line in f:
        if "OPENROUTER_API_KEY=" in line:
            API_KEY = line.strip().split("=", 1)[1]
            break

if not API_KEY:
    print("FATAL: OPENROUTER_API_KEY not found")
    exit(1)

BASE = "https://openrouter.ai/api/v1/videos"
OUT_DIR = "/home/mikesai1/workspace/video-shootout"
os.makedirs(OUT_DIR, exist_ok=True)

# ============================================================
# 6 Test Prompts — designed to cover different categories
# and probe moderation boundaries
# ============================================================

PROMPTS = [
    {
        "id": "01_cinematic",
        "category": "Cinematic Landscape",
        "prompt": "A sweeping aerial shot of a misty mountain valley at golden hour, sunlight breaking through clouds, a river winding through pine forests, cinematic color grading, volumetric light",
    },
    {
        "id": "02_character",
        "category": "Character Animation",
        "prompt": "A close-up of an elderly craftsman's hands shaping a clay pot on a pottery wheel, warm studio lighting, clay particles in the air, shallow depth of field, documentary style",
    },
    {
        "id": "03_action",
        "category": "Action / Sports",
        "prompt": "A skateboarder performing a kickflip on a sunlit urban street, motion blur, dynamic camera following the skater, graffiti on the walls behind, energetic and fast-paced",
    },
    {
        "id": "04_abstract",
        "category": "Abstract / Artistic",
        "prompt": "Liquid ink swirling in water, forming abstract patterns, black and gold ink on white background, macro photography, slow motion, elegant and mesmerizing",
    },
    {
        "id": "05_text_render",
        "category": "Text Rendering",
        "prompt": "Neon sign that reads 'AI VIDEO' flickering to life on a brick wall at night, rain reflecting the neon glow, cyberpunk aesthetic, the text clearly legible and spelled correctly",
    },
    {
        "id": "06_moderation",
        "category": "Moderation Boundary",
        "prompt": "A medieval knight in full armor walking through a dark forest, sword drawn and shield raised, tension building, torchlight flickering, dramatic shadows, approaching a castle gate — no combat, just anticipation",
    },
]

# ============================================================
# API Functions
# ============================================================

def submit_job(model, prompt, duration=5, resolution=None, aspect_ratio="16:9"):
    """Submit a video generation job."""
    payload = {
        "model": model,
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "generate_audio": True,
    }
    if resolution:
        payload["resolution"] = resolution
    
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE}",
        data=data,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            return result
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return {"error": f"HTTP {e.code}: {body}", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}

def poll_job(job_id, max_polls=60, interval=15):
    """Poll job until complete or failed."""
    for i in range(max_polls):
        req = urllib.request.Request(
            f"{BASE}/{job_id}",
            headers={"Authorization": f"Bearer {API_KEY}"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
                status = result.get("status", "unknown")
                print(f"    Poll {i+1}: {status}")
                
                if status == "completed":
                    return result
                elif status == "failed":
                    return result
                elif status in ("pending", "in_progress", "processing"):
                    time.sleep(interval)
                else:
                    time.sleep(interval)
        except Exception as e:
            print(f"    Poll {i+1}: error {e}")
            time.sleep(interval)
    
    return {"error": "Timeout", "status": "failed"}

def download_video(job_id, filepath):
    """Download the generated video."""
    req = urllib.request.Request(
        f"{BASE}/{job_id}/content?index=0",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"    Download error: {e}")
        return False

def get_credits():
    """Check remaining credits."""
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/credits",
        headers={"Authorization": f"Bearer {API_KEY}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            d = json.loads(resp.read())
            data = d.get("data", d)
            return data.get("total_credits", 0) - data.get("total_usage", 0)
    except:
        return -1

def probe_video(filepath):
    """Get video metadata via ffprobe."""
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "quiet", "-print_format", "json",
             "-show_streams", "-show_format", filepath],
            capture_output=True, text=True, timeout=10
        )
        return json.loads(result.stdout) if result.stdout else {}
    except:
        return {}

# ============================================================
# Main Shootout
# ============================================================

def run_shootout():
    results = []
    
    print("=" * 60)
    print("  VIDEO GENERATION SHOOTOUT")
    print("  MiniMax H3 vs FLUX 3 — Same Prompts, Side by Side")
    print("=" * 60)
    
    credits_before = get_credits()
    print(f"\nCredits remaining: ${credits_before:.2f}")
    print(f"Test prompts: {len(PROMPTS)}")
    print(f"Models: MiniMax H3 (2K, $0.13/s) + FLUX 3 (720p, $0.17/s)")
    print(f"Duration: 5s each")
    print(f"Estimated cost: ~${len(PROMPTS) * 5 * (0.13 + 0.17):.2f}")
    print()
    
    models = [
        {"slug": "minimax/hailuo-3", "name": "MiniMax H3", "resolution": "2K", "price_per_s": 0.13},
        {"slug": "black-forest-labs/flux-3-video", "name": "FLUX 3", "resolution": "720p", "price_per_s": 0.17},
    ]
    
    for prompt_data in PROMPTS:
        pid = prompt_data["id"]
        category = prompt_data["category"]
        prompt_text = prompt_data["prompt"]
        
        print(f"\n{'='*60}")
        print(f"PROMPT {pid}: {category}")
        print(f"  \"{prompt_text[:100]}...\"")
        print(f"{'='*60}")
        
        for model in models:
            slug = model["slug"]
            name = model["name"]
            resolution = model["resolution"]
            
            print(f"\n  --- {name} ({resolution}) ---")
            
            # Submit
            submit_start = time.time()
            job = submit_job(slug, prompt_text, duration=5, resolution=resolution)
            submit_time = time.time() - submit_start
            
            if job.get("error"):
                print(f"    ⚠️ Submit failed: {job['error'][:200]}")
                entry = {
                    "prompt_id": pid,
                    "category": category,
                    "model": name,
                    "slug": slug,
                    "resolution": resolution,
                    "status": "failed",
                    "error": job["error"][:500],
                    "submit_time_s": round(submit_time, 2),
                    "gen_time_s": 0,
                    "cost": 0,
                }
                results.append(entry)
                
                # Save interim
                with open(f"{OUT_DIR}/results_partial.json", "w") as f:
                    json.dump(results, f, indent=2)
                
                # If 503, wait and retry
                if "503" in str(job.get("error", "")):
                    print("    503 — waiting 60s and retrying...")
                    time.sleep(60)
                    job = submit_job(slug, prompt_text, duration=5, resolution=resolution)
                    if job.get("error"):
                        print(f"    Retry failed: {job['error'][:200]}")
                        continue
                
                continue
            
            job_id = job.get("id")
            if not job_id:
                print(f"    ⚠️ No job ID: {json.dumps(job)[:200]}")
                continue
            
            print(f"    Job ID: {job_id}")
            print(f"    Submit time: {submit_time:.2f}s")
            
            # Poll
            poll_start = time.time()
            result = poll_job(job_id, max_polls=40, interval=15)
            gen_time = time.time() - poll_start
            
            status = result.get("status", "unknown")
            error_msg = result.get("error", "")
            
            print(f"    Status: {status}")
            print(f"    Gen time: {gen_time:.1f}s")
            
            if status == "failed":
                print(f"    ⚠️ FAILED: {error_msg[:200]}")
                entry = {
                    "prompt_id": pid,
                    "category": category,
                    "model": name,
                    "slug": slug,
                    "resolution": resolution,
                    "status": "failed",
                    "error": error_msg[:500],
                    "submit_time_s": round(submit_time, 2),
                    "gen_time_s": round(gen_time, 1),
                    "cost": 0,
                }
                results.append(entry)
                with open(f"{OUT_DIR}/results_partial.json", "w") as f:
                    json.dump(results, f, indent=2)
                continue
            
            # Download
            video_path = f"{OUT_DIR}/{pid}_{name.lower().replace(' ', '_').replace('.', '')}.mp4"
            print(f"    Downloading to {video_path}...")
            dl_ok = download_video(job_id, video_path)
            
            if dl_ok:
                # Probe
                probe = probe_video(video_path)
                streams = probe.get("streams", [])
                video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
                audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
                fmt = probe.get("format", {})
                
                file_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
                duration_actual = float(video_stream.get("duration", 0))
                width = int(video_stream.get("width", 0))
                height = int(video_stream.get("height", 0))
                fps = eval(video_stream.get("r_frame_rate", "0/1")) if "/" in video_stream.get("r_frame_rate", "0") else float(video_stream.get("r_frame_rate", 0))
                
                cost = 5 * model["price_per_s"]  # 5 seconds × price
                
                entry = {
                    "prompt_id": pid,
                    "category": category,
                    "model": name,
                    "slug": slug,
                    "resolution": resolution,
                    "status": "completed",
                    "submit_time_s": round(submit_time, 2),
                    "gen_time_s": round(gen_time, 1),
                    "cost": round(cost, 2),
                    "video_path": video_path,
                    "file_size_mb": round(file_size / (1024*1024), 2),
                    "duration_s": round(duration_actual, 3),
                    "resolution_actual": f"{width}x{height}",
                    "fps": round(fps, 1),
                    "frames": int(video_stream.get("nb_frames", 0)),
                    "video_codec": video_stream.get("codec_name", ""),
                    "has_audio": bool(audio_stream),
                    "audio_codec": audio_stream.get("codec_name", ""),
                }
                
                print(f"    ✅ Downloaded: {entry['file_size_mb']} MB, {entry['resolution_actual']}, {entry['duration_s']}s, {entry['fps']} fps")
                print(f"    Cost: ${cost:.2f}")
            else:
                entry = {
                    "prompt_id": pid,
                    "category": category,
                    "model": name,
                    "slug": slug,
                    "resolution": resolution,
                    "status": "download_failed",
                    "gen_time_s": round(gen_time, 1),
                    "cost": round(5 * model["price_per_s"], 2),
                }
                print(f"    ⚠️ Download failed")
            
            results.append(entry)
            
            # Save interim after each result
            with open(f"{OUT_DIR}/results_partial.json", "w") as f:
                json.dump(results, f, indent=2)
            
            time.sleep(3)  # Small gap between submissions
    
    # Final credits check
    credits_after = get_credits()
    total_cost = credits_before - credits_after
    
    # Save final results
    final = {
        "timestamp": datetime.now().isoformat(),
        "credits_before": round(credits_before, 2),
        "credits_after": round(credits_after, 2),
        "total_cost": round(total_cost, 2),
        "prompts": PROMPTS,
        "results": results,
    }
    
    results_file = f"{OUT_DIR}/shootout_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w") as f:
        json.dump(final, f, indent=2, default=str)
    
    # Print summary
    print(f"\n\n{'='*60}")
    print("SHOOTOUT COMPLETE")
    print(f"{'='*60}")
    print(f"\nTotal cost: ${total_cost:.2f}")
    print(f"Credits remaining: ${credits_after:.2f}")
    print(f"Results: {results_file}")
    
    print(f"\n{'='*60}")
    print("SUMMARY TABLE")
    print(f"{'='*60}")
    print(f"{'Prompt':<20} {'Model':<10} {'Status':<10} {'Gen Time':<10} {'Cost':<8} {'Resolution':<15} {'Size':<8}")
    print("-" * 90)
    
    for r in results:
        status = "✅" if r["status"] == "completed" else "❌"
        gen_t = f"{r.get('gen_time_s', 0)}s" if r.get("gen_time_s") else "N/A"
        cost = f"${r.get('cost', 0)}" if r.get("cost") else "$0"
        res = r.get("resolution_actual", r.get("resolution", "N/A"))
        size = f"{r.get('file_size_mb', 0)}MB" if r.get("file_size_mb") else "N/A"
        
        print(f"{r['prompt_id']:<20} {r['model']:<10} {status:<10} {gen_t:<10} {cost:<8} {res:<15} {size:<8}")
        
        if r.get("error"):
            print(f"  Error: {r['error'][:100]}")
    
    return results_file

if __name__ == "__main__":
    run_shootout()