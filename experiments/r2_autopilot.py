"""R2: concurrent autopilot expansion.

Usage:  uv run python scripts/r2_autopilot.py <seed.mp4> [levels]
Output: runs/live-<timestamp>/ (renders/, tree.json, manifest.json)

Verifies the R2 milestone: LLM-planned beats, all children rendering
concurrently on the fal slots, first-ready-wins commitment, and eager
p1 pipelining of the committed child's children.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from autopilot_engine import run_autopilot  # local: historical engine, superseded by realtime/live.py

SCENE_SUMMARY = (
    "A cynical elderly mad scientist with spiky pale blue hair and a white "
    "lab coat argues with his anxious teenage grandson in a yellow t-shirt, "
    "in a cluttered suburban living room during an unstable-time event: "
    "sickly green tint, floating green crystals, frozen debris. 2D adult "
    "animation, flat cel-shading, thick outlines, static medium-wide shot."
)

if __name__ == "__main__":
    seed = Path(sys.argv[1])
    levels = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    run_dir = Path("runs") / f"live-{time.strftime('%Y%m%d-%H%M%S')}"
    run_autopilot(seed, run_dir, SCENE_SUMMARY, levels=levels)
    print(f"\nrun: {run_dir}")
