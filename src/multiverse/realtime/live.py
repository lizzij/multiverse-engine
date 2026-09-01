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
from multiverse.realtime.planner import plan_beats, plan_tree
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
        self.source_seed_path = seed_path
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
        tmp = self.run_dir / "manifest.json.tmp"
        tmp.write_text(json.dumps(manifest, indent=2))
        tmp.replace(self.run_dir / "manifest.json")

    async def run(self) -> None:
        self._log("preparing identity anchor ...")
        identity_small = downscale(
            Path(self.tree.nodes["0"].render_path), 480,
            self.run_dir / "anchors" / "identity_480.mp4",
        )
        self.identity_url = await asyncio.to_thread(upload_media, identity_small)

        root_id = "0"
        next_beats: list[dict] | None = None
        for cycle in range(self.cycles):
            entry = {"root": root_id, "dive_to": None}
            self.cycle_log.append(entry)
            self._write_state()
            self._log(f"=== cycle {cycle}: root [{root_id}] ===")

            if next_beats is None:
                beats = self._load_seed_storyboard() if cycle == 0 else None
                if beats is None:
                    self._log(f"storyboarding cycle of [{root_id}] ...")
                    beats = await asyncio.to_thread(
                        plan_tree, self.tree.ancestry(root_id), self.scene_summary, self.depth
                    )
                    self._log("storyboard ready")
                    if cycle == 0:
                        self._save_seed_storyboard(beats)
                else:
                    self._log("storyboard ready (cached at seed)")
            else:
                beats = next_beats

            # Pre-commit the dive path (semantics known now), so the NEXT
            # cycle's storyboard plans in parallel with this cycle's renders.
            path, path_beats, level_beats = [], [], beats
            for _ in range(self.depth):
                i = random.randrange(min(self.branches, len(level_beats)))
                path.append(i)
                path_beats.append(level_beats[i])
                level_beats = level_beats[i].get("children", [])
            dive_id = root_id + "." + ".".join(str(i + 1) for i in path)
            next_task = None
            if cycle + 1 < self.cycles:
                next_task = asyncio.create_task(asyncio.to_thread(
                    plan_tree, self.tree.ancestry(root_id), self.scene_summary,
                    self.depth, 300, path_beats,
                ))

            await self.expand_cycle(root_id, beats)

            # A viewer's click (control.json, written by scripts/serve.py)
            # overrides the pre-committed autopilot path.
            user_choice = self._read_control()
            if user_choice:
                node = self.tree.nodes.get(user_choice)
                if node and node.status is NodeStatus.READY:
                    self._log(f"☞ viewer dove into [{user_choice}]")
                    if next_task:
                        next_task.cancel()
                        next_task = None
                    entry["dive_to"] = user_choice
                    self._write_state()
                    if cycle + 1 < self.cycles:
                        await self._identity_refresh(node)
                    next_beats = None
                    root_id = user_choice
                    continue

            chosen = self.tree.nodes.get(dive_id)
            if chosen is None or chosen.status is not NodeStatus.READY:
                ready = [
                    n for n in self.tree.nodes.values()
                    if n.parent_id and n.id.startswith(root_id) and n.depth
                    == self.tree.nodes[root_id].depth + self.depth
                    and n.status is NodeStatus.READY
                ]
                if not ready:
                    self._log("no leaves survived; stopping")
                    break
                chosen = random.choice(ready)
                if next_task:
                    next_task.cancel()
                    next_task = None
                self._log(f"pre-committed leaf failed; falling back to [{chosen.id}]")
            entry["dive_to"] = chosen.id
            self._write_state()
            self._log(f"◎ dive -> [{chosen.id}] {chosen.premise[:60]}")
            if cycle + 1 < self.cycles:
                await self._identity_refresh(chosen)
            try:
                next_beats = await next_task if next_task else None
            except Exception as exc:
                self._log(f"next-cycle storyboard failed ({exc}); will replan")
                next_beats = None
            root_id = chosen.id
        self._log(
            f"done: {self.pool.completed} renders ok, {self.pool.failed} failed"
        )

    async def expand_cycle(self, root_id: str, cycle_beats: list[dict]) -> list[Universe]:
        leaves: list[Universe] = []
        root = self.tree.nodes[root_id]

        async def expand(node: Universe, d: int, beats: list[dict]) -> None:
            if d >= self.depth:
                leaves.append(node)
                return
            # Re-rooting on a node whose children already exist (a viewer
            # dove into mid-tree): reuse the rendered subtree instantly.
            existing = self.tree.children(node.id)[: self.branches]
            if len(existing) == self.branches and all(
                c.status is NodeStatus.READY for c in existing
            ):
                await asyncio.gather(*(expand(c, d + 1, []) for c in existing))
                return
            # A planning/anchoring failure abandons this subtree but must
            # never crash the stream (renders already have their own
            # FAILED path; give planning and anchoring the same courtesy).
            try:
                if not beats:
                    beats = await asyncio.to_thread(
                        plan_beats, self.tree.ancestry(node.id), self.scene_summary, self.branches
                    )
                # Freeze-safe anchor: never anchor children on a stalled tail.
                frame = await asyncio.to_thread(
                    extract_anchor_frame,
                    Path(node.render_path), self.run_dir / "anchors" / f"{node.id}_last.png",
                )
                frame_url = await asyncio.to_thread(upload_media, frame)
            except Exception as exc:
                self._log(f"✗ expansion of [{node.id}] abandoned: {exc}")
                return

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
                    # Deadline: a wedged fal request must become FAILED,
                    # not a forever-stall of the whole cycle.
                    _, took = await asyncio.wait_for(self.pool.run(lambda: render_i2v(
                        frame_url, prompt, out,
                        duration=self.duration, resolution=self.resolution,
                        seed=42, hint=self.hint,
                    )), timeout=180)
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

    def _read_control(self) -> str | None:
        """Consume a viewer dive request written by scripts/serve.py."""
        path = self.run_dir / "control.json"
        if not path.exists():
            return None
        try:
            choice = json.loads(path.read_text()).get("dive_to")
        except ValueError:
            choice = None
        path.unlink(missing_ok=True)
        return choice

    # Storyboard-at-seed: the first cycle's beat tree is cached next to
    # the seed file, so repeat streams of the same seed start instantly.
    def _storyboard_cache_path(self) -> Path:
        return self.source_seed_path.with_suffix(".storyboard.json")

    def _load_seed_storyboard(self) -> list[dict] | None:
        path = self._storyboard_cache_path()
        if not path.exists():
            return None
        try:
            data = json.loads(path.read_text())
            if data.get("depth") == self.depth and data.get("branches") == self.branches:
                return data["beats"]
        except (ValueError, KeyError):
            pass
        return None

    def _save_seed_storyboard(self, beats: list[dict]) -> None:
        self._storyboard_cache_path().write_text(json.dumps(
            {"depth": self.depth, "branches": self.branches, "beats": beats}, indent=2
        ))

    async def _identity_refresh(self, leaf: Universe) -> None:
        """Slow lane: re-render the dive target against the seed identity
        anchor (r2v, low priority) before its children anchor on it, so
        drift resets at every cycle boundary. Hidden behind the root's
        fullscreen playback."""
        parent = self.tree.nodes[leaf.parent_id]
        frame = await asyncio.to_thread(
            extract_anchor_frame,
            Path(parent.render_path), self.run_dir / "anchors" / f"{leaf.id}_refresh_src.png",
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
