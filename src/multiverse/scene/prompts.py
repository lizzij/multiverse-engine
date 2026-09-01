"""Prompt compiler: SceneSpec + Universe + provider capabilities → model prompt (spec §20)."""

from __future__ import annotations

from multiverse.schemas import RendererCapabilities, SceneSpec, Universe

PRESERVATION_TEMPLATE = """\
Video 1 is the canonical source performance.

Preserve:
- exact character placement
- actions and gestures
- camera framing
- temporal rhythm
- shot duration

Do not restart or reinterpret the action.

The surrounding reality follows this premise:

{premise}

Visible consequences:

{consequences}

Transform the world strongly enough that the reality is immediately
distinct, while preserving the source performance and temporal structure.

No cuts.
No alternate camera angle.
No unrelated scene.
"""


def compile_prompt(
    scene: SceneSpec, universe: Universe, capabilities: RendererCapabilities
) -> str:
    consequences = "\n".join(f"- {c}" for c in universe.visible_consequences) or "- (none listed)"
    return PRESERVATION_TEMPLATE.format(premise=universe.premise, consequences=consequences)
