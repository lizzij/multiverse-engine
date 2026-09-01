"""Record a launch video: the player replaying a finished run.

- rec=1 player mode simulates the live generation log (nodes flip
  queued→rendering→ready during the preceding level) and emits precise
  REC_EVENTS timestamps.
- Audio is muxed afterwards: solo (fullscreen) segments carry the
  scene's native audio; grid segments carry a soundtrack (looped).

Usage: uv run python scripts/record_launch.py <run_dir> [out.mp4] [soundtrack]
Requires scripts/serve.py running on :8642.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

TRIM = 0.8  # seconds cut from the head of the capture

run = sys.argv[1].rstrip("/")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(run) / "launch-video.mp4"
soundtrack = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("runs/assets-local/rick-theme.m4a")
url = f"http://localhost:8642/web/player.html?run={run}&rec=1"
manifest = json.loads((Path(run) / "manifest.json").read_text())

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=str(out.parent),
        record_video_size={"width": 1920, "height": 1080},
    )
    t_video_start = time.time()
    page = ctx.new_page()
    page.goto(url)
    page.wait_for_timeout(1200)
    # Map in-page performance.now() to wall clock.
    calib_wall, calib_perf = time.time(), page.evaluate("() => performance.now()")

    depth, total_cycles = manifest["depth"], len(manifest["cycles"])
    print(f"recording {run}: depth={depth}, cycles={total_cycles}")
    deadline = time.time() + 300
    while time.time() < deadline:
        state = page.evaluate("() => ({dives, level})")
        if state["dives"] >= total_cycles - 1 and state["level"] >= depth:
            break
        time.sleep(1)
    page.wait_for_timeout(8000)  # hold the final grid

    events = page.evaluate("() => REC_EVENTS")
    video = page.video
    ctx.close()
    webm = Path(video.path())
    browser.close()


def rel(perf_t: float) -> float:
    return (calib_wall + (perf_t - calib_perf) / 1000.0) - t_video_start - TRIM


# Solo segments: from each 'start'/'dive' event until the next event.
solos = []
for i, ev in enumerate(events):
    if ev["kind"] in ("start", "dive"):
        start = max(rel(ev["t"]), 0.0)
        end = rel(events[i + 1]["t"]) if i + 1 < len(events) else start + 7.0
        solos.append((start, end, ev["root"]))
print("solo segments:", [(f"{s:.1f}", f"{e:.1f}", n) for s, e, n in solos])

duration = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(webm)],
    capture_output=True, text=True, check=True).stdout.strip()) - TRIM

inputs = ["-ss", str(TRIM), "-i", str(webm), "-stream_loop", "-1", "-i", str(soundtrack)]
filters, mix = [], []
# Theme under the grids, muted during solos.
mute = "+".join(f"between(t,{s:.2f},{e:.2f})" for s, e, _ in solos) or "0"
filters.append(
    f"[1:a]atrim=0:{duration:.2f},asetpts=PTS-STARTPTS,"
    f"volume=0.8,volume=enable='{mute}':volume=0[theme]"
)
mix.append("[theme]")
# Native audio on each solo scene.
for k, (s, e, node) in enumerate(solos):
    clip = Path(run) / manifest["nodes"][node]["file"]
    inputs += ["-i", str(clip)]
    d = e - s
    ms = int(s * 1000)
    filters.append(
        f"[{2+k}:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS,"
        f"afade=t=out:st={max(d-0.4,0):.2f}:d=0.4,adelay={ms}|{ms}[solo{k}]"
    )
    mix.append(f"[solo{k}]")
filters.append(f"{''.join(mix)}amix=inputs={len(mix)}:duration=first:normalize=0[a]")

subprocess.run(
    ["ffmpeg", "-v", "error", "-y", *inputs,
     "-filter_complex", ";".join(filters),
     "-map", "0:v", "-map", "[a]", "-t", f"{duration:.2f}",
     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
     "-c:a", "aac", "-b:a", "192k", str(out)],
    check=True,
)
webm.unlink(missing_ok=True)
print(f"launch video: {out}  ({duration:.1f}s, audio muxed)")
