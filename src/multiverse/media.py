"""ffmpeg helpers for continuity anchors and timeline assembly.

See docs/realtime-branching.md §2: every continuation render carries the
parent's tail clip and exact final frame alongside the identity seed.
"""

from __future__ import annotations

import subprocess
from pathlib import Path


def _run(args: list[str]) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def duration_seconds(clip: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(clip)],
        check=True, capture_output=True, text=True,
    )
    return float(out.stdout.strip())


def extract_tail(clip: Path, seconds: float, out: Path) -> Path:
    """Last `seconds` of `clip` — the continuity anchor (Video 2)."""
    start = max(duration_seconds(clip) - seconds, 0.0)
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(["-ss", f"{start:.3f}", "-i", str(clip), "-c:v", "libx264",
          "-preset", "fast", "-c:a", "aac", str(out)])
    return out


def extract_last_frame(clip: Path, out: Path) -> Path:
    """Exact final frame — the starting image for a continuation (Image 1)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(["-sseof", "-0.1", "-i", str(clip), "-frames:v", "1", "-update", "1", str(out)])
    return out


def concat(clips: list[Path], out: Path) -> Path:
    """Concatenate clips (video+audio, re-encoded) into one timeline."""
    inputs: list[str] = []
    for clip in clips:
        inputs += ["-i", str(clip)]
    n = len(clips)
    streams = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([*inputs, "-filter_complex", f"{streams}concat=n={n}:v=1:a=1[v][a]",
          "-map", "[v]", "-map", "[a]", str(out)])
    return out
