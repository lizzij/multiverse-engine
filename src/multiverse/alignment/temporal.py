"""Temporal normalization and optional cross-world retiming (spec §22–§23).

All outputs normalize onto a shared 0.0–1.0 timeline (same duration, FPS,
frame count) before compositing. Retiming via DTW is optional and lands
only if independent renders drift in action timing.
"""

from __future__ import annotations

from pathlib import Path


def normalize(clip: Path, duration_seconds: float, fps: float, out: Path) -> Path:
    raise NotImplementedError("temporal normalization lands in Phase 1 (see ROADMAP.md)")
