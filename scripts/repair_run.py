"""Retry FAILED nodes of a finished run (spec §54: retry individual worlds).

Re-renders each failed node from its stored beat and its parent's
freeze-safe anchor frame, then updates tree.json + manifest.json.

Usage: uv run python scripts/repair_run.py <run_dir> [summary_file]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from multiverse.media import extract_anchor_frame
from multiverse.renderers.h3_max import render_i2v, upload_media
from multiverse.scene.prompts import compile_i2v_prompt
from multiverse.schemas import NodeStatus
from multiverse.worlds.tree import UniverseTree

run_dir = Path(sys.argv[1].rstrip("/"))
tree = UniverseTree.load(run_dir / "tree.json")
summary = Path(sys.argv[2]).read_text().strip() if len(sys.argv) > 2 else ""
if not summary:
    # fall back to the sidecar next to whatever seed name is conventional
    candidates = list(Path("examples").glob("*.summary.txt"))
    raise SystemExit(f"pass the seed summary file (e.g. {candidates[0] if candidates else 'examples/<seed>.summary.txt'})")

run_settings = json.loads((run_dir / "manifest.json").read_text())
failed = [n for n in tree.nodes.values() if n.status is NodeStatus.FAILED]
print(f"{len(failed)} failed node(s)")
for node in failed:
    parent = tree.nodes[node.parent_id]
    frame = extract_anchor_frame(
        Path(parent.render_path), run_dir / "anchors" / f"{parent.id}_repair.png"
    )
    prompt = compile_i2v_prompt(
        summary,
        node.world_state.get("action", node.premise),
        node.premise,
        node.world_state.get("ending_pose", "a held tableau"),
        node.visible_consequences,
    )
    out = run_dir / "renders" / f"{node.id}.mp4"
    print(f"→ retry [{node.id}] {node.divergence}")
    meta = render_i2v(
        upload_media(frame), prompt, out,
        duration=run_settings["duration"],
        resolution=run_settings.get("resolution", "480p"), seed=43,
    )
    node.render_path = str(out)
    node.status = NodeStatus.READY
    print(f"✓ [{node.id}] repaired ({meta['file_size_bytes'] // 1024} KB)")

tree.save(run_dir / "tree.json")
manifest = json.loads((run_dir / "manifest.json").read_text())
for node in failed:
    manifest["nodes"][node.id]["status"] = "ready"
    manifest["nodes"][node.id]["file"] = f"renders/{node.id}.mp4"
(run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
print("tree.json + manifest.json updated")
