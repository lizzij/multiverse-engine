"""Autopilot: expand the universe tree concurrently, ahead of playback.

Per docs/realtime-branching.md §4-§6:
- all children of a frontier node render concurrently (p0);
- the committed path uses FIRST-READY-WINS: autopilot commits to
  whichever child materializes first (minimizes hold time), and starts
  planning + rendering that child's children immediately while its
  siblings are still in flight (p1 pipelining);
- tree.json + manifest.json are rewritten on every state change so a
  player can follow along live.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

from multiverse.media import extract_last_frame, extract_tail
from multiverse.realtime.planner import plan_beats
from multiverse.realtime.scheduler import RenderPool
from multiverse.renderers.h3_max import render_reference, upload_media
from multiverse.scene.prompts import compile_continuation_prompt
from multiverse.schemas import NodeStatus, Universe
from multiverse.worlds.tree import UniverseTree

TAIL_SECONDS = 2.0


class Autopilot:
    def __init__(
        self,
        seed_path: Path,
        run_dir: Path,
        scene_summary: str,
        levels: int = 2,
        branches: int = 4,
        duration: int = 8,
        concurrency: int = 10,
    ):
        self.run_dir = run_dir
        self.scene_summary = scene_summary
        self.levels = levels
        self.branches = branches
        self.duration = duration
        self.pool = RenderPool(concurrency)
        self.tree = UniverseTree.new()
        self.committed_path: list[str] = ["0"]
        self.t0 = time.monotonic()

        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "renders").mkdir(exist_ok=True)
        self.seed_path = run_dir / "renders" / "0.mp4"
        shutil.copy(seed_path, self.seed_path)
        root = self.tree.nodes["0"]
        root.render_path = str(self.seed_path)
        root.status = NodeStatus.READY

    # ---------- state ----------

    def _log(self, msg: str) -> None:
        print(f"[{time.monotonic() - self.t0:6.1f}s] {msg}", flush=True)

    def _write_state(self) -> None:
        self.tree.save(self.run_dir / "tree.json")
        manifest = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "committed_path": self.committed_path,
            "nodes": {
                n.id: {
                    "parent": n.parent_id,
                    "status": n.status.value,
                    "file": n.render_path and str(Path(n.render_path).relative_to(self.run_dir)),
                    "premise": n.premise,
                    "depth": n.depth,
                }
                for n in self.tree.nodes.values()
            },
        }
        (self.run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # ---------- pipeline ----------

    async def run(self) -> None:
        self._log("uploading identity anchor ...")
        self.identity_url = await asyncio.to_thread(upload_media, self.seed_path)
        self._write_state()
        await self.expand(self.tree.nodes["0"], level=1)
        self._write_state()
        self._log(
            f"done: {self.pool.completed} renders ok, {self.pool.failed} failed, "
            f"committed path {' -> '.join(self.committed_path)}"
        )

    async def expand(self, node: Universe, level: int) -> None:
        """Plan and render all children of `node`; recurse down first-ready."""
        self._log(f"planning {self.branches} continuations of [{node.id}] ...")
        ancestry = self.tree.ancestry(node.id)
        beats = await asyncio.to_thread(plan_beats, ancestry, self.scene_summary, self.branches)

        parent_clip = Path(node.render_path)
        tail = extract_tail(parent_clip, TAIL_SECONDS, self.run_dir / "anchors" / f"{node.id}_tail.mp4")
        frame = extract_last_frame(parent_clip, self.run_dir / "anchors" / f"{node.id}_last.png")
        tail_url, frame_url = await asyncio.gather(
            asyncio.to_thread(upload_media, tail),
            asyncio.to_thread(upload_media, frame),
        )

        children = []
        for beat in beats:
            child = self.tree.add_child(
                node.id,
                premise=beat["premise"],
                divergence=beat["divergence"],
                world_state={"action": beat["action"], "ending_pose": beat["ending_pose"]},
                visible_consequences=beat["visible_consequences"],
            )
            child.status = NodeStatus.QUEUED
            children.append((child, beat))
        self._write_state()

        # p0 for the frontier level, p1 for deeper pipelined levels.
        priority = 0 if level == 1 else 1
        committed = asyncio.Event()

        async def render_child(child: Universe, beat: dict) -> None:
            prompt = compile_continuation_prompt(
                beat["action"], beat["premise"], beat["ending_pose"],
                beat["visible_consequences"],
            )
            out = self.run_dir / "renders" / f"{child.id}.mp4"
            child.status = NodeStatus.RENDERING
            self._write_state()
            self._log(f"→ submit [{child.id}] {child.divergence} (p{priority})")
            try:
                _, took = await self.pool.run(
                    lambda: render_reference(
                        [self.identity_url, tail_url], prompt, out,
                        duration=self.duration, resolution="768p",
                        aspect_ratio="16:9", seed=42, image_urls=[frame_url],
                    ),
                    priority=priority,
                )
            except Exception as exc:
                child.status = NodeStatus.FAILED
                self._write_state()
                self._log(f"✗ [{child.id}] failed: {exc}")
                return
            child.render_path = str(out)
            child.status = NodeStatus.READY
            self._write_state()
            self._log(f"✓ [{child.id}] ready ({took:.0f}s render)")

            # First-ready-wins: commit and pipeline deeper immediately,
            # while this child's siblings are still rendering.
            if not committed.is_set():
                committed.set()
                self.committed_path.append(child.id)
                self._log(f"★ committed path -> [{child.id}]")
                self._write_state()
                if level < self.levels:
                    await self.expand(child, level + 1)

        await asyncio.gather(*(render_child(c, b) for c, b in children))


def run_autopilot(seed_path: Path, run_dir: Path, scene_summary: str, **kwargs) -> None:
    asyncio.run(Autopilot(seed_path, run_dir, scene_summary, **kwargs).run())
