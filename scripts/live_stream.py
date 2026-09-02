"""Run the live infinite multiverse engine (thin wrapper over the CLI).

Usage:  uv run python scripts/live_stream.py <seed.mp4> [cycles]
Then:   uv run python scripts/serve.py     (player + click-to-dive on :8642)
Watch:  http://localhost:8642/web/player.html?run=<run_dir>

Equivalent: `uv run multiverse live <seed.mp4> --cycles N`.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from multiverse.realtime.live import run_live

if __name__ == "__main__":
    seed = Path(sys.argv[1])
    cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    run_dir = Path("runs") / f"stream-{time.strftime('%Y%m%d-%H%M%S')}"
    print(f"run dir: {run_dir}")
    print(f"player:  http://localhost:8642/web/player.html?run={run_dir}")
    run_live(seed, run_dir, cycles=cycles)
