"""Social exports from a finished run (spec §30–§33).

- story: the committed story path as one continuous film with audio
  crossfades at every scene boundary.
- participate: the final cycle's leaf universes as a numbered grid with
  a "reply N" end card, plus caption text files (spec §30B/§33).
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from multiverse.media import concat_crossfade, duration_seconds

FONT = "/System/Library/Fonts/Helvetica.ttc"

PRESETS = ("story", "participate")


def load_manifest(run_dir: Path) -> dict:
    return json.loads((run_dir / "manifest.json").read_text())


def story_path(manifest: dict) -> list[str]:
    """The engine's committed linear story: each cycle's root → dive target."""
    ids: list[str] = []
    for cyc in manifest["cycles"]:
        root, dive = cyc["root"], cyc.get("dive_to")
        if not ids or ids[-1] != root:
            ids.append(root)
        if dive and dive.startswith(root + "."):
            rel = dive[len(root) + 1 :].split(".")
            ids.extend(root + "." + ".".join(rel[: i + 1]) for i in range(len(rel)))
    return ids


def leaf_nodes(manifest: dict, cycle_index: int = -1) -> list[str]:
    """READY leaves of one cycle's subtree, in id order."""
    root = manifest["cycles"][cycle_index]["root"]
    depth = manifest["depth"]
    root_depth = 0 if root == "0" else len(root.split(".")) - 1
    prefix = "" if root == "0" else root + "."
    return sorted(
        nid for nid, n in manifest["nodes"].items()
        if nid.startswith(prefix) and n["status"] == "ready"
        and len(nid.split(".")) - 1 == root_depth + depth
    )


def export_story(run_dir: Path, out: Path | None = None) -> Path:
    manifest = load_manifest(run_dir)
    clips = [run_dir / manifest["nodes"][i]["file"] for i in story_path(manifest)]
    clips = [c for c in clips if c.exists()]
    if not clips:
        raise ValueError("no committed story scenes found in this run")
    return concat_crossfade(clips, out or run_dir / "exports" / "story.mp4")


def export_participate(run_dir: Path, out: Path | None = None) -> Path:
    """Numbered leaf grid + CTA end card + caption files."""
    manifest = load_manifest(run_dir)
    leaves = leaf_nodes(manifest)
    if len(leaves) < 2:
        raise ValueError("run has fewer than 2 ready leaf universes")
    out = out or run_dir / "exports" / "participate.mp4"
    out.parent.mkdir(parents=True, exist_ok=True)

    cols = min(4, len(leaves))
    rows = -(-len(leaves) // cols)
    cw, ch = 1920 // cols, 1080 // rows
    dur = min(
        duration_seconds(run_dir / manifest["nodes"][n]["file"]) for n in leaves
    )

    inputs, cells = [], []
    for i, nid in enumerate(leaves):
        inputs += ["-i", str(run_dir / manifest["nodes"][nid]["file"])]
        cells.append(
            f"[{i}:v]scale={cw}:{ch}:force_original_aspect_ratio=increase,"
            f"crop={cw}:{ch},fps=24,trim=0:{dur:.2f},setpts=PTS-STARTPTS,"
            f"drawtext=fontfile={FONT}:text='{i + 1:02d}':fontcolor=white:fontsize={ch // 6}:"
            f"borderw=3:bordercolor=black:x=18:y=h-th-14[c{i}]"
        )
    layout = "|".join(f"{(i % cols) * cw}_{(i // cols) * ch}" for i in range(len(leaves)))
    grid = (
        ";".join(cells)
        + f";{''.join(f'[c{i}]' for i in range(len(leaves)))}"
        + f"xstack=inputs={len(leaves)}:layout={layout}:fill=black[grid]"
    )
    endcard = (
        f"color=c=black:size=1920x1080:rate=24:duration=2.2[bg];"
        f"[bg]drawtext=fontfile={FONT}:text='WHICH REALITY NEXT?':fontcolor=white:"
        f"fontsize=96:x=(w-tw)/2:y=h/2-110,"
        f"drawtext=fontfile={FONT}:text='reply 1–{len(leaves)}':fontcolor=white:"
        f"fontsize=64:x=(w-tw)/2:y=h/2+30[card]"
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex",
         f"{grid};{endcard};[grid][card]concat=n=2:v=1[v]",
         "-map", "[v]", "-an", "-pix_fmt", "yuv420p", str(out)],
        check=True,
    )
    _write_captions(out.parent, len(leaves))
    return out


def _write_captions(exports_dir: Path, n: int) -> None:
    captions = exports_dir / "captions"
    captions.mkdir(exist_ok=True)
    (captions / "minimal.txt").write_text("one moment\ninfinite timelines\n")
    (captions / "participate.txt").write_text(
        f"I split one scene into {n} parallel realities.\n\n"
        f"Which one should continue?\n\nreply 1–{n}\n"
    )
    (captions / "technical.txt").write_text(
        "same characters\nsame story\ndifferent generated futures\n\nopen source ↓\n"
    )
