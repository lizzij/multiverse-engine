"""Live infinite multiverse engine.

The cycle: root plays fullscreen → fracture 1→2→4→8 (each pane continues
its parent's story by ~5s) → a random leaf is chosen, the player zooms
into it, and it becomes the next cycle's root. Forever.

Concurrency (C=10 slots): branching factor 2 keeps every wave ≤ 8
renders. Plan-ahead: a node's children's beats are planned from
semantics while the node itself is still rendering, so only pixels ever
gate the pipeline. Children submit eagerly the moment their parent's
pixels land (continuity anchors always come from the finished parent).

The engine writes manifest.json on every state change; the web player
(web/player.html) polls it and follows along.
"""

from __future__ import annotations

import asyncio
import json
import random
import shutil
import time
from datetime import datetime
from pathlib import Path

from multiverse.media import downscale, extract_last_frame, extract_tail
from multiverse.realtime.planner import plan_beats
from multiverse.realtime.scheduler import RenderPool
from multiverse.renderers.h3_max import render_reference, upload_media
from multiverse.scene.prompts import compile_continuation_prompt
from multiverse.schemas import NodeStatus, Universe
from multiverse.worlds.tree import UniverseTree

TAIL_SECONDS = 2.0


class LiveEngine:
    def __init__(
        self,
        seed_path: Path,
        run_dir: Path,
        scene_summary: str,
        cycles: int = 2,
        depth: int = 3,
        branches: int = 2,
        duration: int = 5,
        resolution: str = "480p",
        concurrency: int = 10,
    ):
        self.run_dir = run_dir
        self.scene_summary = scene_summary
        self.cycles = cycles
        self.depth = depth
        self.branches = branches
        self.duration = duration
        self.resolution = resolution
        self.pool = RenderPool(concurrency)
        self.tree = UniverseTree.new()
        self.cycle_log: list[dict] = []
        self.t0 = time.monotonic()

        (run_dir / "renders").mkdir(parents=True, exist_ok=True)
        (run_dir / "anchors").mkdir(exist_ok=True)
        seed_local = run_dir / "renders" / "0.mp4"
        shutil.copy(seed_path, seed_local)
        root = self.tree.nodes["0"]
        root.render_path = str(seed_local)
        root.status = NodeStatus.READY

    def _log(self, msg: str) -> None:
        print(f"[{time.monotonic() - self.t0:6.1f}s] {msg}", flush=True)

    def _write_state(self) -> None:
        self.tree.save(self.run_dir / "tree.json")
        manifest = {
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "duration": self.duration,
            "depth": self.depth,
            "branches": self.branches,
            "cycles": self.cycle_log,
            "nodes": {
                n.id: {
                    "parent": n.parent_id,
                    "status": n.status.value,
                    "file": n.render_path and str(Path(n.render_path).relative_to(self.run_dir)),
                    "premise": n.premise,
                }
                for n in self.tree.nodes.values()
            },
        }
        (self.run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    async def run(self) -> None:
        self._log("preparing identity anchor ...")
        identity_small = downscale(
            Path(self.tree.nodes["0"].render_path), 480,
            self.run_dir / "anchors" / "identity_480.mp4",
        )
        self.identity_url = await asyncio.to_thread(upload_media, identity_small)

        root_id = "0"
        for cycle in range(self.cycles):
            entry = {"root": root_id, "dive_to": None}
            self.cycle_log.append(entry)
            self._write_state()
            self._log(f"=== cycle {cycle}: root [{root_id}] ===")
            leaves = await self.expand_cycle(root_id)
            ready = [l for l in leaves if l.status is NodeStatus.READY]
            if not ready:
                self._log("no leaves survived; stopping")
                break
            chosen = random.choice(ready)
            entry["dive_to"] = chosen.id
            self._write_state()
            self._log(f"◎ dive -> [{chosen.id}] {chosen.premise[:60]}")
            root_id = chosen.id
        self._log(
            f"done: {self.pool.completed} renders ok, {self.pool.failed} failed"
        )

    async def expand_cycle(self, root_id: str) -> list[Universe]:
        leaves: list[Universe] = []

        async def expand(node: Universe, d: int, beats_task: asyncio.Task | None) -> None:
            if d >= self.depth:
                leaves.append(node)
                return
            beats = await (beats_task or self._plan(node))
            parent_clip = Path(node.render_path)
            tail = extract_tail(parent_clip, TAIL_SECONDS, self.run_dir / "anchors" / f"{node.id}_tail.mp4")
            frame = extract_last_frame(parent_clip, self.run_dir / "anchors" / f"{node.id}_last.png")
            tail_url, frame_url = await asyncio.gather(
                asyncio.to_thread(upload_media, tail),
                asyncio.to_thread(upload_media, frame),
            )

            async def render_child(beat: dict) -> None:
                child = self.tree.add_child(
                    node.id,
                    premise=beat["premise"],
                    divergence=beat["divergence"],
                    world_state={"action": beat["action"], "ending_pose": beat["ending_pose"]},
                    visible_consequences=beat["visible_consequences"],
                )
                child.status = NodeStatus.RENDERING
                self._write_state()
                # Plan-ahead: the grandchildren's beats need only this
                # child's semantics, so planning overlaps its render.
                grand_task = self._plan(child) if d + 1 < self.depth else None
                prompt = compile_continuation_prompt(
                    beat["action"], beat["premise"], beat["ending_pose"],
                    beat["visible_consequences"],
                )
                out = self.run_dir / "renders" / f"{child.id}.mp4"
                self._log(f"→ submit [{child.id}] {beat['divergence']}")
                try:
                    _, took = await self.pool.run(lambda: render_reference(
                        [self.identity_url, tail_url], prompt, out,
                        duration=self.duration, resolution=self.resolution,
                        aspect_ratio="16:9", seed=42, image_urls=[frame_url],
                    ))
                except Exception as exc:
                    child.status = NodeStatus.FAILED
                    self._write_state()
                    self._log(f"✗ [{child.id}] failed: {exc}")
                    if grand_task:
                        grand_task.cancel()
                    return
                child.render_path = str(out)
                child.status = NodeStatus.READY
                self._write_state()
                self._log(f"✓ [{child.id}] ready ({took:.0f}s)")
                # Eager: descend the moment this child's pixels exist.
                await expand(child, d + 1, grand_task)

            await asyncio.gather(*(render_child(b) for b in beats[: self.branches]))

        root = self.tree.nodes[root_id]
        await expand(root, 0, None)
        return leaves

    def _plan(self, node: Universe) -> asyncio.Task:
        async def _run():
            return await asyncio.to_thread(
                plan_beats, self.tree.ancestry(node.id), self.scene_summary, self.branches
            )
        return asyncio.create_task(_run())


def run_live(seed_path: Path, run_dir: Path, scene_summary: str, **kwargs) -> None:
    asyncio.run(LiveEngine(seed_path, run_dir, scene_summary, **kwargs).run())
