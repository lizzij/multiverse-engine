"""LLM beat planner (docs/realtime-branching.md §3).

Backends, fastest available wins:
1. GEMINI_API_KEY   → Gemini Flash REST (~seconds; GEMINI_MODEL overrides)
2. ANTHROPIC_API_KEY → Anthropic SDK, Claude Haiku 4.5 direct (~10-20s)
3. fallback          → headless `claude -p` CLI (existing local login;
                       slowest — boots an agent session per call)
"""

from __future__ import annotations

import json
import os
import subprocess

from multiverse.schemas import Universe


def _complete(prompt: str, timeout: int) -> str:
    """One planning completion via the fastest configured backend."""
    if os.environ.get("GEMINI_API_KEY"):
        import httpx

        model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        resp = httpx.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
            headers={"x-goog-api-key": os.environ["GEMINI_API_KEY"]},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"},
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]

    if os.environ.get("ANTHROPIC_API_KEY"):
        import anthropic

        client = anthropic.Anthropic()
        response = client.messages.create(
            model=os.environ.get("MULTIVERSE_PLANNER_MODEL", "claude-haiku-4-5"),
            max_tokens=8000,
            messages=[{"role": "user", "content": prompt}],
        )
        return next(b.text for b in response.content if b.type == "text")

    # Text→JSON only: deny all tools so story text embedded in the prompt
    # can never induce the headless session to touch the system.
    out = subprocess.run(
        ["claude", "-p", prompt, "--output-format", "json", "--model", "haiku",
         "--disallowedTools",
         "Bash Read Write Edit Glob Grep WebFetch WebSearch Agent Task NotebookEdit"],
        capture_output=True, text=True, timeout=timeout, check=True,
    )
    return json.loads(out.stdout)["result"]


def _parse_array(text: str) -> list[dict]:
    start, end = text.find("["), text.rfind("]")
    if start < 0 or end < 0:
        raise ValueError(f"planner returned no JSON array: {text[:200]}")
    return json.loads(text[start : end + 1])

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


TREE_PROMPT = """\
You are the story planner for a branching parallel-reality video engine.

THE SOURCE SCENE (identity canon for all realities):
{scene_summary}

THE TIMELINE SO FAR (each scene continues the previous one):
{ancestry}

Plan a complete BINARY TREE of story continuations, {depth} levels deep
(so {n_total} scenes total). Rules:
- The tree root's 2 children each continue the last scene above from its
  ending pose ({parent_ending}), forking in two genuinely different
  directions (world, choices, new elements, or physics may change).
- Every scene's own children continue THAT scene from ITS ending_pose,
  forking again. Siblings must be high-contrast with each other.
- Each scene is ~5 seconds: ONE clear action beat, concrete and filmable.
- Every scene ENDS on a held, stable pose (a "fracture point").
- Keep the two main characters present and recognizable throughout.

Respond with ONLY a JSON array of 2 scene objects (no prose), each:
  "divergence": short slug for what forks
  "premise": one-sentence premise of this reality
  "action": 1-3 sentences of what visibly happens
  "ending_pose": the held final tableau, one sentence
  "visible_consequences": list of 2-3 concrete visual details
  "children": array of 2 scene objects of the same shape (empty array at
  the deepest level)
"""

REQUIRED = {"divergence", "premise", "action", "ending_pose", "visible_consequences"}


def _validate_tree(beats: list[dict], depth: int) -> None:
    if len(beats) < 2:
        raise ValueError(f"expected 2 beats per node, got {len(beats)}")
    for b in beats[:2]:
        if not set(b) >= REQUIRED:
            raise ValueError(f"beat missing keys: {sorted(REQUIRED - set(b))}")
        if depth > 1:
            _validate_tree(b.get("children", []), depth - 1)


def plan_tree(
    ancestry: list[Universe],
    scene_summary: str,
    depth: int = 3,
    timeout: int = 300,
    extra_beats: list[dict] | None = None,
) -> list[dict]:
    """Plan a full cycle's storyboard (binary beat tree) in one call.

    `extra_beats`: planned-but-unrendered beats extending the ancestry —
    lets the next cycle's storyboard be planned before this cycle's
    scenes exist (semantics only, pixels never gate planning).
    """
    ancestry_text = _ancestry_text(ancestry)
    ending = ancestry[-1].world_state.get("ending_pose", "as the scene ends")
    for b in extra_beats or []:
        ancestry_text += f"\n- [planned] {b['premise']}: {b['action']}"
        ending = b.get("ending_pose", ending)
    prompt = TREE_PROMPT.format(
        scene_summary=scene_summary,
        ancestry=ancestry_text,
        depth=depth,
        n_total=2 ** (depth + 1) - 2,
        parent_ending=ending,
    )
    beats = _parse_array(_complete(prompt, timeout))
    _validate_tree(beats, depth)
    return beats[:2]


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
    beats = _parse_array(_complete(prompt, timeout))
    required = {"divergence", "premise", "action", "ending_pose", "visible_consequences"}
    beats = [b for b in beats if required <= set(b)]
    if len(beats) < n:
        raise ValueError(f"planner returned {len(beats)} valid beats, wanted {n}")
    return beats[:n]
