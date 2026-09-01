"""Source media → SceneSpec via a multimodal analyzer (spec §14).

V0 stub: Phase 2 wires this to a vision model. The contract is fixed:
analyze() must fill invariants (what survives every branch) and
mutable_dimensions (what a divergence may change).
"""

from __future__ import annotations

from pathlib import Path

from multiverse.schemas import SceneSpec


def analyze(source_path: Path) -> SceneSpec:
    raise NotImplementedError("scene analysis lands in Phase 2 (see ROADMAP.md)")
