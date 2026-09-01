"""Record a launch video: the player replaying a finished run.

With every scene READY, the player fractures on its minimum-show cadence
— no loop-holds — so the capture is naturally a tight cut. The side
status panel stays visible.

Usage: uv run python scripts/record_launch.py <run_dir> [out.mp4]
Requires scripts/serve.py running on :8642.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

run = sys.argv[1].rstrip("/")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(run) / "launch-video.mp4"
url = f"http://localhost:8642/web/player.html?run={run}&rec=1"

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    ctx = browser.new_context(
        viewport={"width": 1920, "height": 1080},
        record_video_dir=str(out.parent),
        record_video_size={"width": 1920, "height": 1080},
    )
    page = ctx.new_page()
    page.goto(url)
    page.wait_for_timeout(1500)

    depth = page.evaluate("() => manifest.depth")
    total_cycles = page.evaluate("() => manifest.cycles.length")
    print(f"recording {run}: depth={depth}, cycles={total_cycles}")

    # Follow the replay until the final cycle's deepest grid has played out.
    deadline = time.time() + 300
    while time.time() < deadline:
        state = page.evaluate("() => ({dives, level, diving})")
        print(f"  dive {state['dives']} level {state['level']}", flush=True)
        if state["dives"] >= total_cycles - 1 and state["level"] >= depth:
            break
        time.sleep(2)
    page.wait_for_timeout(8000)  # hold the final grid

    video = page.video
    ctx.close()
    webm = Path(video.path())
    browser.close()

subprocess.run(
    ["ffmpeg", "-v", "error", "-y", "-ss", "0.8", "-i", str(webm),
     "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
     "-an", str(out)],
    check=True,
)
webm.unlink(missing_ok=True)
print(f"launch video: {out}")
