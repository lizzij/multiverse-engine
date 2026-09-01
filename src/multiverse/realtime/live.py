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

from multiverse.media import downscale, extract_anchor_frame
from multiverse.realtime.planner import plan_tree
from multiverse.realtime.scheduler import RenderPool
from multiverse.renderers.h3_max import render_i2v, render_reference, upload_media
from multiverse.scene.prompts import compile_i2v_prompt
from multiverse.schemas import NodeStatus, Universe
from multiverse.worlds.tree import UniverseTree


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
        self.hint = run_dir.name  # fal runner session affinity for the stream
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
            if cycle + 1 < self.cycles:
                await self._identity_refresh(chosen)
            root_id = chosen.id
        self._log(
            f"done: {self.pool.completed} renders ok, {self.pool.failed} failed"
        )

    async def expand_cycle(self, root_id: str) -> list[Universe]:
        leaves: list[Universe] = []
        root = self.tree.nodes[root_id]
        # Storyboard-ahead: the whole cycle's beat tree in one planner call,
        # hidden behind the root's fullscreen playback. Zero planning
        # latency during the cycle.
        self._log(f"storyboarding cycle of [{root_id}] ...")
        cycle_beats = await asyncio.to_thread(
            plan_tree, self.tree.ancestry(root_id), self.scene_summary, self.depth
        )
        self._log("storyboard ready")

        async def expand(node: Universe, d: int, beats: list[dict]) -> None:
            if d >= self.depth:
                leaves.append(node)
                return
            # Freeze-safe anchor: never anchor children on a stalled tail.
            frame = extract_anchor_frame(
                Path(node.render_path), self.run_dir / "anchors" / f"{node.id}_last.png"
            )
            frame_url = await asyncio.to_thread(upload_media, frame)

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
                prompt = compile_i2v_prompt(
                    self.scene_summary, beat["action"], beat["premise"],
                    beat["ending_pose"], beat["visible_consequences"],
                )
                out = self.run_dir / "renders" / f"{child.id}.mp4"
                self._log(f"→ submit [{child.id}] {beat['divergence']}")
                try:
                    _, took = await self.pool.run(lambda: render_i2v(
                        frame_url, prompt, out,
                        duration=self.duration, resolution=self.resolution,
                        seed=42, hint=self.hint,
                    ))
                except Exception as exc:
                    child.status = NodeStatus.FAILED
                    self._write_state()
                    self._log(f"✗ [{child.id}] failed: {exc}")
                    return
                child.render_path = str(out)
                child.status = NodeStatus.READY
                self._write_state()
                self._log(f"✓ [{child.id}] ready ({took:.0f}s)")
                # Eager: descend the moment this child's pixels exist.
                await expand(child, d + 1, beat.get("children", []))

            await asyncio.gather(*(render_child(b) for b in beats[: self.branches]))

        await expand(root, 0, cycle_beats)
        return leaves

    async def _identity_refresh(self, leaf: Universe) -> None:
        """Slow lane: re-render the dive target against the seed identity
        anchor (r2v, low priority) before its children anchor on it, so
        drift resets at every cycle boundary. Hidden behind the root's
        fullscreen playback."""
        parent = self.tree.nodes[leaf.parent_id]
        frame = extract_anchor_frame(
            Path(parent.render_path), self.run_dir / "anchors" / f"{leaf.id}_refresh_src.png"
        )
        frame_url = await asyncio.to_thread(upload_media, frame)
        prompt = (
            "Video 1 is the canonical identity and art-style reference for "
            "the characters. Image 1 is the exact first frame; begin there "
            "and keep the characters exactly recognizable as in Video 1.\n\n"
            f"What happens: {leaf.world_state.get('action', leaf.premise)}\n\n"
            "Single continuous take. No cuts. "
            f"End the scene holding this pose: {leaf.world_state.get('ending_pose', 'a held tableau')}"
        )
        out = self.run_dir / "renders" / f"{leaf.id}.mp4"
        self._log(f"↺ identity refresh [{leaf.id}] (r2v, low priority)")
        try:
            _, took = await self.pool.run(lambda: render_reference(
                [self.identity_url], prompt, out,
                duration=self.duration, resolution=self.resolution,
                aspect_ratio="16:9", seed=42, image_urls=[frame_url],
            ), priority=2)
            self._log(f"↺ refreshed [{leaf.id}] ({took:.0f}s)")
        except Exception as exc:
            self._log(f"↺ refresh failed, keeping I2V render: {exc}")

def run_live(seed_path: Path, run_dir: Path, scene_summary: str, **kwargs) -> None:
    asyncio.run(LiveEngine(seed_path, run_dir, scene_summary, **kwargs).run())
