"""Record a launch video: the player replaying a finished run.

- rec=1 player mode simulates the live generation log (nodes flip
  queued→rendering→ready during the preceding level) and emits precise
  REC_EVENTS timestamps.
- Audio is muxed afterwards: solo (fullscreen) segments carry the
  scene's native audio; grid segments carry a soundtrack (looped).

Usage: uv run python scripts/record_launch.py <run_dir> [out.mp4] [soundtrack] [--hero]
  soundtrack: optional music file for grid sections (omit for scene audio only)
  --hero:     also produce a ~13s square 1.8x hero cut without the panel
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

args = [a for a in sys.argv[1:] if a != "--hero"]
HERO = "--hero" in sys.argv
run = args[0].rstrip("/")
out = (Path(args[1]) if len(args) > 1 and args[1]
       else Path(run) / f"launch-{time.strftime('%H%M%S')}.mp4")  # unique: never clobber an open preview
soundtrack = Path(args[2]) if len(args) > 2 else None
if soundtrack and not soundtrack.exists():
    print(f"soundtrack {soundtrack} not found — proceeding without music")
    soundtrack = None
url = f"http://localhost:8642/web/player.html?run={run}&rec=1" + ("&panel=0" if HERO else "")
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
        time.sleep(0.5)
    page.wait_for_timeout(int(manifest["duration"] * 1000) + 600)  # one playthrough of the final grid

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

THEME_VOL = 0.35   # keep the music a bed, not a lead
RAMP = 1.5         # seconds of fade in/out around each solo

inputs = ["-ss", str(TRIM), "-i", str(webm)]
filters, mix = [], []
audio_base = 1
if soundtrack:
    inputs += ["-stream_loop", "-1", "-i", str(soundtrack)]
    audio_base = 2
    # Theme under the grids: smooth ramps around each solo (0 inside a
    # solo, linear ramp over RAMP seconds on either side).
    factors = [
        f"clip(max(({s:.2f}-t)/{RAMP},(t-{e:.2f})/{RAMP}),0,1)" for s, e, _ in solos
    ] or ["1"]
    gain = factors[0]
    for f in factors[1:]:
        gain = f"min({gain},{f})"
    filters.append(
        f"[1:a]atrim=0:{duration:.2f},asetpts=PTS-STARTPTS,"
        f"volume='{THEME_VOL}*({gain})':eval=frame,"
        f"afade=t=in:d=1,afade=t=out:st={max(duration-2,0):.2f}:d=2[theme]"
    )
    mix.append("[theme]")
# Native audio on each solo scene, gently faded at both ends.
for k, (s, e, node) in enumerate(solos):
    clip = Path(run) / manifest["nodes"][node]["file"]
    inputs += ["-i", str(clip)]
    d = e - s
    ms = int(s * 1000)
    filters.append(
        f"[{audio_base + k}:a]atrim=0:{d:.2f},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,"
        f"afade=t=out:st={max(d-0.5,0):.2f}:d=0.5,adelay={ms}|{ms}[solo{k}]"
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

if HERO:
    # ~13s square hero cut for the feed: 1.8x speed, center crop, muted
    # (spec §5: works muted, autoplaying, mobile).
    hero_out = out.with_name(out.stem + "-hero.mp4")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(out),
         "-vf", "setpts=PTS/1.8,crop=ih:ih,scale=1080:1080,fps=30",
         "-t", "13", "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
         str(hero_out)],
        check=True,
    )
    print(f"hero cut:     {hero_out}")
