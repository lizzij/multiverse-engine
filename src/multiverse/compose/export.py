"""Social export presets: hero-infinite, participate-16, poster, GIF (spec §30, §32).

Primary launch artifact: 1080×1080 square.
"""

from __future__ import annotations

from pathlib import Path

PRESETS = ("hero", "participate", "four-world", "rapid-cycle")
SIZES = {"square": (1080, 1080), "portrait": (1080, 1350), "landscape": (1920, 1080)}


def export(run_dir: Path, preset: str, root_node: str = "0") -> Path:
    raise NotImplementedError("exports land in Phase 2/5 (see ROADMAP.md)")
