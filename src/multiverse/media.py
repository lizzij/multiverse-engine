"""ffmpeg helpers for continuity anchors and timeline assembly.

See docs/realtime-branching.md §2: every continuation render carries the
parent's tail clip and exact final frame alongside the identity seed.
"""

from __future__ import annotations

import shutil
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


def downscale(clip: Path, height: int, out: Path) -> Path:
    """Downscale a clip (e.g. the identity anchor, to cut reference-token cost)."""
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(["-i", str(clip), "-vf", f"scale=-2:{height}", "-c:v", "libx264",
          "-preset", "fast", "-c:a", "aac", str(out)])
    return out


def freeze_safe_time(clip: Path, window: float = 1.5, noise: float = 0.003, min_dur: float = 0.35) -> float:
    """Latest timestamp safe to anchor on: before any frozen landing tail.

    Runs ffmpeg freezedetect over the clip's last `window` seconds. If the
    tail is frozen/stalled, returns the freeze start minus a small margin;
    otherwise the clip end. (Freeze-aware cutoff — a frozen last frame
    would poison every descendant anchored on it.)
    """
    total = duration_seconds(clip)
    start = max(total - window, 0.0)
    proc = subprocess.run(
        ["ffmpeg", "-v", "info", "-ss", f"{start:.3f}", "-i", str(clip),
         "-vf", f"freezedetect=n={noise}:d={min_dur}", "-an", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    freeze_starts = [
        float(line.rsplit(":", 1)[1])
        for line in proc.stderr.splitlines()
        if "freeze_start" in line
    ]
    if not freeze_starts:
        return total
    return max(start + freeze_starts[0] - 0.05, 0.1)


def extract_anchor_frame(clip: Path, out: Path) -> Path:
    """Freeze-safe final frame — the continuation anchor."""
    t = freeze_safe_time(clip)
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(["-ss", f"{max(t - 0.05, 0):.3f}", "-i", str(clip), "-frames:v", "1",
          "-update", "1", str(out)])
    return out


def concat_crossfade(clips: list[Path], out: Path, fade: float = 0.25) -> Path:
    """Concatenate scenes with audio crossfades and brief video dissolves.

    Removes the click/pop and abrupt sonic reset at scene boundaries so a
    story chain plays as one continuous show.
    """
    if len(clips) == 1:
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(clips[0], out)
        return out
    durations = [duration_seconds(c) for c in clips]
    inputs: list[str] = []
    for clip in clips:
        inputs += ["-i", str(clip)]
    parts, offset = [], 0.0
    vprev, aprev = "0:v", "0:a"
    for i in range(1, len(clips)):
        offset += durations[i - 1] - fade
        vout, aout = f"v{i}", f"a{i}"
        parts.append(f"[{vprev}][{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}[{vout}]")
        parts.append(f"[{aprev}][{i}:a]acrossfade=d={fade}[{aout}]")
        vprev, aprev = vout, aout
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([*inputs, "-filter_complex", ";".join(parts),
          "-map", f"[{vprev}]", "-map", f"[{aprev}]", str(out)])
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
