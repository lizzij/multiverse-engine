"""RTMP playout client: broadcast a live run as a continuous stream.

Follows the manifest's story frontier (current scene → first-ready
child → … → next cycle root), looping the current scene while the next
one renders — the same diegetic hold the web player uses, but as a
gap-free RTMP feed for Twitch/YouTube.

Design (after reactor-team/infinite-livestream's queue-and-playout
split): each scene is transcoded to uniform MPEG-TS and appended into
one long-lived ffmpeg muxer that paces (-re) and pushes to the RTMP
URL. Point it at a .flv path to test without a streaming server.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

SEGMENT_ARGS = [
    "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,"
           "pad=1280:720:(ow-iw)/2:(oh-ih)/2,fps=30",
    "-c:v", "libx264", "-preset", "veryfast", "-b:v", "3500k",
    "-pix_fmt", "yuv420p", "-g", "60",
    "-c:a", "aac", "-ar", "44100", "-b:a", "160k",
    "-f", "mpegts",
]


class Playout:
    def __init__(self, run_dir: Path, rtmp_url: str):
        self.run_dir = run_dir
        out_fmt = ["-f", "flv"] if not rtmp_url.endswith(".ts") else ["-f", "mpegts"]
        self.mux = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-re", "-f", "mpegts", "-i", "pipe:0",
             "-c", "copy", *out_fmt, rtmp_url],
            stdin=subprocess.PIPE,
        )

    def play(self, clip: Path) -> None:
        seg = subprocess.run(
            ["ffmpeg", "-v", "error", "-i", str(clip), *SEGMENT_ARGS, "pipe:1"],
            stdout=subprocess.PIPE, check=True,
        )
        self.mux.stdin.write(seg.stdout)
        self.mux.stdin.flush()

    def close(self) -> None:
        self.mux.stdin.close()
        self.mux.wait()


def _manifest(run_dir: Path) -> dict:
    return json.loads((run_dir / "manifest.json").read_text())


def _first_ready_child(m: dict, node_id: str) -> str | None:
    kids = sorted(
        (k for k, v in m["nodes"].items() if v["parent"] == node_id),
        key=lambda k: int(k.split(".")[-1]),
    )
    for k in kids:
        if m["nodes"][k]["status"] == "ready":
            return k
    return None


def _next_cycle_root(m: dict, node_id: str) -> str | None:
    for i, cyc in enumerate(m["cycles"]):
        if cyc.get("dive_to") == node_id and i + 1 < len(m["cycles"]):
            return m["cycles"][i + 1]["root"]
    return None


def stream(run_dir: Path, rtmp_url: str, max_scenes: int = 0, max_holds: int = 30) -> None:
    playout = Playout(run_dir, rtmp_url)
    current = _manifest(run_dir)["cycles"][0]["root"]
    played = holds = 0
    try:
        while True:
            m = _manifest(run_dir)
            clip = run_dir / m["nodes"][current]["file"]
            playout.play(clip)
            played += 1
            print(f"▶ [{current}] (scene {played})", flush=True)
            if max_scenes and played >= max_scenes:
                break
            nxt = _first_ready_child(m, current) or _next_cycle_root(m, current)
            if nxt:
                current, holds = nxt, 0
            else:
                holds += 1  # loop the scene — the diegetic hold
                if holds >= max_holds:
                    print("frontier exhausted; ending stream", flush=True)
                    break
                time.sleep(0.1)
    finally:
        playout.close()


if __name__ == "__main__":
    stream(
        Path(sys.argv[1]), sys.argv[2],
        max_scenes=int(sys.argv[3]) if len(sys.argv) > 3 else 0,
    )
