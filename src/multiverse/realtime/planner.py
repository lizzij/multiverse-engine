"""LLM beat planner via headless `claude -p` (docs/realtime-branching.md §3).

Reuses the user's existing local Claude auth — no separate API key.
Planning is cheap and fast relative to rendering, so it runs ahead of
the render frontier.
"""

from __future__ import annotations

import json
import subprocess

from multiverse.schemas import Universe

PLANNER_PROMPT = """\
You are the story planner for a branching parallel-reality video engine.

THE SOURCE SCENE (identity canon for all realities):
{scene_summary}

THE TIMELINE SO FAR (each scene continues the previous one):
{ancestry}

Plan exactly {n} DIVERGENT continuations of the last scene above. Rules:
- Each continuation begins at the exact instant the last scene ended
  (its ending pose: {parent_ending}).
- Each must fork in a DIFFERENT direction: the world, the characters'
  choices, new characters/elements, or the physics may change — but the
  story must genuinely continue, never reset or replay.
- The {n} continuations must be high-contrast with each other.
- Each scene is ~8 seconds: ONE clear action beat, no montage.
- Each must END on a held, stable pose (a "fracture point") that a
  future scene can begin from.
- Keep the two main characters present and recognizable.

Respond with ONLY a JSON array of {n} objects, no prose, each with keys:
  "divergence": short slug-like phrase for what forks
  "premise": one-sentence premise of this reality
  "action": 2-4 sentences of what visibly happens, concrete and filmable
  "ending_pose": the held final tableau, one sentence
  "visible_consequences": list of 2-3 concrete visual details
"""


def _ancestry_text(ancestry: list[Universe]) -> str:
    lines = []
    for node in ancestry:
        action = node.world_state.get("action", "(the source scene)")
        lines.append(f"- [{node.id}] {node.premise or 'original reality'}: {action}")
    return "\n".join(lines)


def plan_beats(
    ancestry: list[Universe], scene_summary: str, n: int = 4, timeout: int = 240
) -> list[dict]:
    """Plan n divergent continuation beats for the last node in `ancestry`."""
    parent = ancestry[-1]
    prompt = PLANNER_PROMPT.format(
        scene_summary=scene_summary,
        ancestry=_ancestry_text(ancestry),
        n=n,
        parent_ending=parent.world_state.get("ending_pose", "as the scene ends"),
    )
    out = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", "haiku"],
        capture_output=True, text=True, timeout=timeout, check=True,
    )
    text = json.loads(out.stdout)["result"]
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < 0:
        raise ValueError(f"planner returned no JSON array: {text[:200]}")
    beats = json.loads(text[start : end + 1])
    required = {"divergence", "premise", "action", "ending_pose", "visible_consequences"}
    beats = [b for b in beats if required <= set(b)]
    if len(beats) < n:
        raise ValueError(f"planner returned {len(beats)} valid beats, wanted {n}")
    return beats[:n]
