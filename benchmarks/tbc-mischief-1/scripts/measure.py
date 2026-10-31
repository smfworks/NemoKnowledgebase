#!/usr/bin/env python3
"""Measure saved clips. No API calls."""
import json
import subprocess
from pathlib import Path

ROOT = Path("/home/mikesai1/NemoVault/evals/mischief-variant-board")
CLIPS = ROOT / "clips"
FRAMES = ROOT / "frames"
STILLS = ROOT / "stills"


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True, stderr=subprocess.STDOUT)


def probe(path: Path) -> dict:
    raw = run([
        "ffprobe", "-v", "error", "-show_entries",
        "format=duration,size,format_name:stream=codec_type,codec_name,width,height,avg_frame_rate,nb_frames",
        "-of", "json", str(path),
    ])
    return json.loads(raw)


def extract(path: Path, dest: Path, ts: str) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.check_call([
        "ffmpeg", "-y", "-ss", ts, "-i", str(path), "-frames:v", "1", str(dest),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ssim(a: Path, b: Path) -> float | None:
    # Scale b to a, then SSIM. ffmpeg prints to stderr.
    cmd = [
        "ffmpeg", "-i", str(a), "-i", str(b),
        "-lavfi", "[1:v][0:v]scale2ref=flags=bicubic[b][a];[a][b]ssim",
        "-f", "null", "-",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True)
    text = p.stderr
    # All: SSIM Y:0.98 ... All:0.97
    for line in text.splitlines():
        if "All:" in line and "SSIM" in line:
            tail = line.split("All:")[-1].strip().split()[0]
            try:
                return float(tail)
            except ValueError:
                return None
    return None


def main() -> None:
    rows = []
    for clip in sorted(CLIPS.glob("*.mp4")):
        info = probe(clip)
        fmt = info.get("format", {})
        streams = info.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio = [s for s in streams if s.get("codec_type") == "audio"]
        duration = float(fmt.get("duration") or 0)
        stem = clip.stem
        still_id = stem.split("-")[0]
        still = STILLS / f"{still_id}.png"
        frame_dir = FRAMES / stem
        times = ["0", "1", "2", "3", "4"]
        if duration > 0.2:
            times.append(f"{max(0, duration - 0.08):.3f}")
        extracted = []
        for ts in times:
            dest = frame_dir / f"t{ts.replace('.', '_')}.png"
            try:
                extract(clip, dest, ts)
                extracted.append({"t": ts, "file": str(dest)})
            except subprocess.CalledProcessError:
                extracted.append({"t": ts, "file": None})
        lock = None
        drift_2 = None
        drift_last = None
        if still.exists() and extracted and extracted[0]["file"]:
            lock = ssim(Path(extracted[0]["file"]), still)
            if len(extracted) >= 3 and extracted[2]["file"]:
                drift_2 = ssim(Path(extracted[0]["file"]), Path(extracted[2]["file"]))
            if extracted[-1]["file"]:
                drift_last = ssim(Path(extracted[0]["file"]), Path(extracted[-1]["file"]))
        rows.append({
            "file": str(clip),
            "bytes": clip.stat().st_size,
            "duration": duration,
            "width": video.get("width"),
            "height": video.get("height"),
            "fps": video.get("avg_frame_rate"),
            "vcodec": video.get("codec_name"),
            "audio_streams": len(audio),
            "first_frame_ssim": lock,
            "ssim_0_vs_2s": drift_2,
            "ssim_0_vs_last": drift_last,
            "frames": extracted,
        })
        print(clip.name, video.get("width"), video.get("height"), round(duration, 3), "ssim0", lock, "audio", len(audio), flush=True)
    out = ROOT / "measurements.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print("wrote", out, flush=True)


if __name__ == "__main__":
    main()
