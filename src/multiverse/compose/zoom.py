"""Zoom/dive transitions: into one tiny branch, then recurse (spec §10)."""

from __future__ import annotations

from pathlib import Path


def dive(grid: Path, target_cell: tuple[int, int], out: Path) -> Path:
    raise NotImplementedError("zoom compositor lands in Phase 1 (see ROADMAP.md)")
