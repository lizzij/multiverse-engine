"""Measure real end-to-end reference-to-video latency, phase by phase.

Usage: uv run python scripts/probe_latency.py <seed.mp4>
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import fal_client

from multiverse.media import extract_last_frame, extract_tail
from multiverse.renderers.h3_max import REFERENCE_TO_VIDEO_ENDPOINT, _download, upload_media

seed = Path(sys.argv[1])
out_dir = Path("runs/probe")
out_dir.mkdir(parents=True, exist_ok=True)

t0 = time.monotonic()
tail = extract_tail(seed, 2.0, out_dir / "tail.mp4")
frame = extract_last_frame(seed, out_dir / "last.png")
print(f"extract:      {time.monotonic() - t0:6.1f}s")

t = time.monotonic()
seed_url = upload_media(seed)
tail_url = upload_media(tail)
frame_url = upload_media(frame)
print(f"uploads:      {time.monotonic() - t:6.1f}s")

PROMPT = (
    "Video 1 is the identity reference. Image 1 is the exact first frame; "
    "begin there. Video 2 shows the preceding moments; continue seamlessly "
    "from its ending. The two characters look at each other and shrug in "
    "unison. Single continuous take, no cuts."
)

for resolution in ("768P", "480P"):
    t = time.monotonic()
    result = fal_client.subscribe(
        REFERENCE_TO_VIDEO_ENDPOINT,
        arguments={
            "prompt": PROMPT,
            "duration": 5,
            "resolution": resolution,
            "aspect_ratio": "16:9",
            "prompt_expansion_mode": "balanced",
            "seed": 42,
            "reference_video_urls": [seed_url, tail_url],
            "reference_image_urls": [frame_url],
        },
    )
    wall = time.monotonic() - t
    t = time.monotonic()
    _download(result["video"]["url"], out_dir / f"probe_{resolution}.mp4")
    dl = time.monotonic() - t
    print(f"{resolution}: submit→result {wall:6.1f}s   download {dl:5.1f}s   fal timings: {result.get('timings')}")
