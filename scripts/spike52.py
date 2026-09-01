"""The §52 spike — the go/no-go experiment.

Branch one source moment into four high-contrast worlds via H3 Max
reference-to-video, then compose a synchronized 2x2 grid. The only
question: does it read as ONE event occurring in FOUR realities?

Usage:  uv run python scripts/spike52.py <source.mp4> [duration]
Output: runs/spike52/<world>.mp4 + runs/spike52/grid.mp4
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from multiverse.renderers import registry
from multiverse.renderers.h3_max import render_reference, upload_media
from multiverse.scene.prompts import compile_prompt
from multiverse.schemas import SceneSpec, Universe

# Spec §6: the first four are curated, deliberately high-contrast categories.
WORLDS = [
    Universe(
        id="past_1890",
        premise=(
            "The same room and argument in the year 1890: a gaslit Victorian "
            "parlor-workshop. The old inventor wears a waistcoat and wild "
            "muttonchops; the boy wears suspenders and a collarless shirt. "
            "The beeping gadget is a whirring brass-and-mahogany contraption."
        ),
        visible_consequences=[
            "gas lamps and candlelight instead of electric light",
            "dark wood, velvet drapes, patterned wallpaper",
            "brass instruments and clockwork parts frozen mid-air",
        ],
    ),
    Universe(
        id="post_agi",
        premise=(
            "The same room and argument in a mature post-AGI civilization. "
            "The living room is a seamless, self-reconfiguring habitat grown "
            "by machine intelligence; soft volumetric interfaces hover in the "
            "air, and a calm robotic steward stands inert in the background."
        ),
        visible_consequences=[
            "walls of smooth adaptive material with faint circuitry bloom",
            "holographic panes and drones frozen mid-air instead of furniture",
            "the gadget is a levitating seamless orb",
        ],
    ),
    Universe(
        id="ocean_civ",
        premise=(
            "The same room and argument in an ocean civilization: the living "
            "room is inside a glass-domed habitat on the seafloor. Deep blue "
            "water and bioluminescent sea life are visible beyond the walls."
        ),
        visible_consequences=[
            "fish and kelp drifting past dome windows",
            "coral-encrusted furniture, nautical materials",
            "shafts of blue-green light rippling through water",
        ],
    ),
    Universe(
        id="low_gravity",
        premise=(
            "The same room and argument under impossible low-gravity biology: "
            "everything drifts. The characters are elongated and willowy, "
            "adapted to a world where things barely fall."
        ),
        visible_consequences=[
            "furniture and debris floating and slowly tumbling",
            "hair and clothing drifting upward",
            "dust motes hanging in shafts of light",
        ],
    ),
]

# What every branch must preserve from the seed.
SCENE = SceneSpec(
    summary="An old scientist argues with an anxious boy in a cluttered living room.",
    invariants=[
        "character positions (scientist left, boy right)",
        "gesture timing (boy throws hands up in panic)",
        "static medium-wide camera framing",
        "scene duration",
    ],
    mutable_dimensions=["world", "era", "technology", "ecology", "physics"],
)


def main() -> None:
    source = Path(sys.argv[1])
    duration = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    out_dir = Path("runs/spike52")
    out_dir.mkdir(parents=True, exist_ok=True)
    caps = registry.get("h3-max").capabilities

    print(f"uploading source: {source}")
    source_url = upload_media(source)

    clips: list[Path] = []
    for world in WORLDS:
        out = out_dir / f"{world.id}.mp4"
        clips.append(out)
        if out.exists():
            print(f"✓ {world.id} (cached)")
            continue
        print(f"→ rendering {world.id} ...")
        meta = render_reference(
            source_url,
            compile_prompt(SCENE, world, caps),
            out,
            duration=duration,
            resolution="768p",
            aspect_ratio="16:9",
            seed=42,
        )
        print(f"✓ {world.id}  ({meta['file_size_bytes'] // 1024} KB)")

    grid = out_dir / "grid.mp4"
    print("compositing 2x2 grid ...")
    inputs: list[str] = []
    for clip in clips:
        inputs += ["-i", str(clip)]
    filters = (
        "".join(
            f"[{i}:v]scale=672:384,fps=24,setpts=PTS-STARTPTS[v{i}];" for i in range(4)
        )
        + "[v0][v1][v2][v3]xstack=inputs=4:layout=0_0|w0_0|0_h0|w0_h0[out]"
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", filters,
         "-map", "[out]", "-an", "-t", str(duration), str(grid)],
        check=True,
    )
    print(f"grid: {grid}")
    print("\nThe only question: does this read as ONE event in FOUR realities?")


if __name__ == "__main__":
    main()
