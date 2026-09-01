"""Run the live infinite multiverse engine.

Usage:  uv run python scripts/live_stream.py <seed.mp4> [cycles]
Then:   python -m http.server 8642   (from the repo root)
Watch:  http://localhost:8642/web/player.html?run=<run_dir>
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from multiverse.realtime.live import run_live

# Default (the Rick-and-Morty test seed); a `<seed>.summary.txt` sidecar
# overrides it, so every seed carries its own identity/style line.
SCENE_SUMMARY = (
    "A cynical elderly mad scientist with spiky pale blue hair and a white "
    "lab coat and his anxious teenage grandson in a yellow t-shirt, in a "
    "cluttered suburban living room during an unstable-time event: sickly "
    "green tint, floating green crystals, frozen debris. 2D adult "
    "animation, flat cel-shading, thick outlines, static medium-wide shot."
)


def scene_summary_for(seed: Path) -> str:
    sidecar = seed.with_suffix(".summary.txt")
    if sidecar.exists():
        return sidecar.read_text().strip()
    return SCENE_SUMMARY


if __name__ == "__main__":
    seed = Path(sys.argv[1])
    cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    run_dir = Path("runs") / f"stream-{time.strftime('%Y%m%d-%H%M%S')}"
    print(f"run dir: {run_dir}")
    print(f"player:  http://localhost:8642/web/player.html?run={run_dir}")
    run_live(seed, run_dir, scene_summary_for(seed), cycles=cycles)
