"""Measure image-to-video (keyframe-to-keyframe) latency vs reference-to-video.

Usage: uv run python scripts/probe_i2v.py <start_clip.mp4> <end_clip.mp4>
Uses each clip's final frame as start/end keyframes.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import fal_client

from multiverse.media import extract_last_frame
from multiverse.renderers.h3_max import _download, upload_media

out_dir = Path("runs/probe")
out_dir.mkdir(parents=True, exist_ok=True)

start_img = extract_last_frame(Path(sys.argv[1]), out_dir / "kf_start.png")
end_img = extract_last_frame(Path(sys.argv[2]), out_dir / "kf_end.png")
start_url = upload_media(start_img)
end_url = upload_media(end_img)

PROMPT = (
    "The old scientist slams his gadget down; the floating green crystals "
    "dissolve into falling droplets and warm light returns to the room. "
    "2D cartoon, single continuous take, no cuts."
)

for resolution in ("480P", "768P"):
    t = time.monotonic()
    result = fal_client.subscribe(
        "minimax/h3-max/image-to-video",
        arguments={
            "prompt": PROMPT,
            "image_url": start_url,
            "end_image_url": end_url,
            "duration": 5,
            "resolution": resolution,
            "prompt_expansion_mode": "balanced",
            "seed": 42,
        },
    )
    wall = time.monotonic() - t
    _download(result["video"]["url"], out_dir / f"i2v_{resolution}.mp4")
    print(f"i2v {resolution}: submit→result {wall:6.1f}s   fal timings: {result.get('timings')}")
