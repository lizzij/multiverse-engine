"""Divergence planning: propose child universes for a node.

The first four branches are curated conceptual categories (spec §6), not
free-form LLM output — an unrestricted model drifts toward generic
"cyberpunk / neon future" prompts.
"""

from __future__ import annotations

from multiverse.schemas import SceneSpec, Universe
from multiverse.worlds.tree import UniverseTree

# Default launch preset: deliberately high-contrast categories.
FIRST_FOUR = [
    ("past", "Same scene in a radically earlier historical world."),
    ("future", "A mature technological/post-AGI civilization."),
    ("altered_earth", "Major ecological/planetary divergence."),
    ("impossible", "Changed physical/biological assumptions."),
]


def plan_first_four(tree: UniverseTree, scene: SceneSpec) -> list[Universe]:
    """Attach the four curated first-level branches to the root."""
    return [
        tree.add_child(tree.root, premise=premise, divergence=key)
        for key, premise in FIRST_FOUR
    ]


def plan_children(
    tree: UniverseTree, node_id: str, scene: SceneSpec, n: int = 4
) -> list[Universe]:
    """Plan n children for a node via the LLM beat planner and attach them."""
    from multiverse.realtime.planner import plan_beats

    beats = plan_beats(tree.ancestry(node_id), scene.summary, n)
    return [
        tree.add_child(
            node_id,
            premise=b["premise"],
            divergence=b["divergence"],
            world_state={"action": b["action"], "ending_pose": b["ending_pose"]},
            visible_consequences=b["visible_consequences"],
        )
        for b in beats[:n]
    ]
