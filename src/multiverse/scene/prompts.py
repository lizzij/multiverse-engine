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


# Continuation prompt (docs/realtime-branching.md §2): dual anchors —
# Video 1 = identity (original seed), Video 2 = parent tail, Image 1 =
# parent's exact final frame the new scene must begin from.
CONTINUATION_TEMPLATE = """\
Video 1 is the canonical identity and art-style reference for the
characters and world lineage. Keep the characters exactly recognizable
as in Video 1.

Image 1 is the exact first frame of this scene; begin there.

Video 2 shows the immediately preceding moments; continue the motion
seamlessly from its ending. Do not restart or replay Video 2.

Then this happens next:

{action}

This reality's premise:

{premise}

Visible consequences:

{consequences}

Single continuous take. No cuts. No alternate camera angle.
End the scene holding this pose: {ending_pose}
"""


def compile_continuation_prompt(
    action: str, premise: str, ending_pose: str, visible_consequences: list[str]
) -> str:
    consequences = "\n".join(f"- {c}" for c in visible_consequences) or "- (none listed)"
    return CONTINUATION_TEMPLATE.format(
        action=action, premise=premise, ending_pose=ending_pose, consequences=consequences
    )


# I2V live lane: no reference media — the start frame IS the continuity
# anchor, so identity/style must be carried in text.
I2V_CONTINUATION_TEMPLATE = """\
{style}

This scene begins at the exact moment shown in the provided first frame
and continues the ongoing story seamlessly from it. Do not reset or
reinterpret the situation.

What happens next:

{action}

This reality's premise:

{premise}

Visible consequences:

{consequences}

Single continuous take. No cuts. No alternate camera angle.
End the scene holding this pose: {ending_pose}
"""


IDENTITY_REFRESH_TEMPLATE = """\
Video 1 is the canonical identity and art-style reference for the
characters. Image 1 is the exact first frame; begin there and keep the
characters exactly recognizable as in Video 1.

What happens: {action}

Single continuous take. No cuts.
End the scene holding this pose: {ending_pose}
"""


def compile_identity_refresh_prompt(action: str, ending_pose: str) -> str:
    return IDENTITY_REFRESH_TEMPLATE.format(action=action, ending_pose=ending_pose)


def compile_i2v_prompt(
    style: str, action: str, premise: str, ending_pose: str, visible_consequences: list[str]
) -> str:
    consequences = "\n".join(f"- {c}" for c in visible_consequences) or "- (none listed)"
    return I2V_CONTINUATION_TEMPLATE.format(
        style=style, action=action, premise=premise,
        ending_pose=ending_pose, consequences=consequences,
    )
