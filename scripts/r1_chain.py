"""R1 go/no-go: chain seed → child → grandchild with dual anchors.

The question (docs/realtime-branching.md §8): does the story continue,
and do the characters stay themselves, across chained generations?

Usage:  uv run python scripts/r1_chain.py <seed.mp4>
Output: runs/r1chain/child.mp4, grandchild.mp4, timeline.mp4
"""

from __future__ import annotations

import sys
from pathlib import Path

from multiverse.media import concat, extract_last_frame, extract_tail
from multiverse.renderers.h3_max import render_reference, upload_media
from multiverse.scene.prompts import compile_continuation_prompt

# Hand-authored beats (R1 isolates the anchor question; the LLM planner
# comes later). Each continues the previous scene and ends on a held
# fracture point.
BEATS = [
    {
        "id": "child",
        "action": (
            "The old scientist slams his beeping gadget onto the coffee "
            "table. The floating green crystals shatter at once into a "
            "gentle rain of glowing droplets. The frozen furniture drops "
            "back into place with a thud. The green tint drains away and "
            "warm normal evening light returns to the living room. The boy "
            "lowers his arms in stunned relief."
        ),
        "premise": (
            "The timeline where the gadget works: time stabilizes and the "
            "room returns to normal."
        ),
        "ending_pose": (
            "the scientist stands smug with arms crossed while the boy "
            "wipes his brow in relief"
        ),
        "visible_consequences": [
            "green crystals dissolve into falling glowing droplets",
            "furniture settles back onto the floor",
            "warm normal lighting replaces the green tint",
        ],
    },
    {
        "id": "grandchild",
        "action": (
            "The television behind them switches itself on with a burst of "
            "static, showing another identical scientist and boy staring "
            "back out of the screen. Both characters slowly turn their "
            "heads toward the TV. The sickly green tint begins creeping "
            "back in from the edges of the room, and a single green "
            "crystal rises from the carpet."
        ),
        "premise": (
            "The stabilized timeline is being watched by another reality: "
            "the split was never fixed, only moved."
        ),
        "ending_pose": (
            "both characters frozen mid-turn, staring at the TV, faces lit "
            "by its glow"
        ),
        "visible_consequences": [
            "the TV shows a mirrored version of the two characters",
            "green tint creeping back from the room's edges",
            "one green crystal rising from the carpet",
        ],
    },
]

TAIL_SECONDS = 2.0
DURATION = 8


def main() -> None:
    seed_path = Path(sys.argv[1])
    out_dir = Path("runs/r1chain")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("uploading identity anchor (seed) ...")
    identity_url = upload_media(seed_path)

    parent_path = seed_path
    chain = [seed_path]
    for beat in BEATS:
        out = out_dir / f"{beat['id']}.mp4"
        chain.append(out)
        if out.exists():
            print(f"✓ {beat['id']} (cached)")
            parent_path = out
            continue

        tail = extract_tail(parent_path, TAIL_SECONDS, out_dir / f"{beat['id']}_parent_tail.mp4")
        frame = extract_last_frame(parent_path, out_dir / f"{beat['id']}_parent_last.png")
        print(f"→ {beat['id']}: uploading continuity anchors ...")
        tail_url = upload_media(tail)
        frame_url = upload_media(frame)

        prompt = compile_continuation_prompt(
            beat["action"], beat["premise"], beat["ending_pose"],
            beat["visible_consequences"],
        )
        print(f"→ rendering {beat['id']} ...")
        meta = render_reference(
            [identity_url, tail_url], prompt, out,
            duration=DURATION, resolution="768p", aspect_ratio="16:9",
            seed=42, image_urls=[frame_url],
        )
        print(f"✓ {beat['id']}  ({meta['file_size_bytes'] // 1024} KB)")
        parent_path = out

    timeline = concat(chain, out_dir / "timeline.mp4")
    print(f"timeline: {timeline}")
    print("\nThe question: does the story continue, and do the characters stay themselves?")


if __name__ == "__main__":
    main()
