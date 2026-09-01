"""Export the committed story of a live run as one continuous film,
with audio crossfades at every scene boundary.

Usage: uv run python scripts/export_timeline.py <run_dir>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from multiverse.media import concat_crossfade


def story_path(manifest: dict) -> list[str]:
    """Linear story: each cycle's root → … → dive target (id-prefix chain)."""
    ids: list[str] = []
    for cycle in manifest["cycles"]:
        root, dive = cycle["root"], cycle.get("dive_to")
        if not ids or ids[-1] != root:
            ids.append(root)
        if dive:
            rel = dive[len(root) + 1 :].split(".")
            for i in range(1, len(rel) + 1):
                ids.append(root + "." + ".".join(rel[:i]))
    return ids


if __name__ == "__main__":
    run_dir = Path(sys.argv[1])
    manifest = json.loads((run_dir / "manifest.json").read_text())
    ids = story_path(manifest)
    clips = [run_dir / manifest["nodes"][i]["file"] for i in ids]
    clips = [c for c in clips if c.exists()]
    out = concat_crossfade(clips, run_dir / "story-timeline.mp4")
    print(f"{len(clips)} scenes → {out}")
