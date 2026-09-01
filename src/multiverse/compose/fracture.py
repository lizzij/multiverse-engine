"""Signature fracture transition: 1 → 4 synchronized panes (spec §28–§29).

Deterministic FFmpeg/PyAV compositing. The generator never produces the
multiverse layout; this module does. Splits happen in normalized time —
no child restarts from frame zero.
"""

from __future__ import annotations

from pathlib import Path


def fracture(source: Path, children: list[Path], at_t: float, out: Path) -> Path:
    """Fracture `source` into `children` at normalized time `at_t` (0.0–1.0)."""
    raise NotImplementedError("fracture compositor lands in Phase 0/1 (see ROADMAP.md)")
