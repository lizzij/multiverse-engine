# Examples

Each example seed is three small text files — **no media is committed**;
you regenerate the video from the prompt in one command:

```text
seed-<name>.prompt.txt       the exact `multiverse seed` prompt
seed-<name>.summary.txt      identity/style line for continuation prompts
seed-<name>.storyboard.json  (optional) hand-authored first-cycle beat tree
```

Generate any seed, then stream it:

```bash
uv run multiverse seed "$(cat examples/seed-rickle.prompt.txt)" \
  --duration 8 --seed 42 --out examples/seed-rickle.mp4
uv run python scripts/serve.py &
uv run multiverse live examples/seed-rickle.mp4 --cycles 2
```

| seed | style | storyboard |
|---|---|---|
| `seed-rickle` | 2D animation, time-fracture living room | LLM-planned, committed |
| `seed-spiderverse-fall` | comic-book falling shot | LLM-planned, committed |
| `seed-eeaao-joy` | live-action A24 warmth, mother & daughter | hand-authored canonical universes |

Seed guidelines: 5–8 seconds, single continuous shot, one clear subject
and one clear action beat, static-ish camera, ending on a holdable pose
(the "fracture point" children start from). `--seed N` makes it
reproducible.

**Source-media policy** (spec §3): the software never depends on
copyrighted material, and no media ships in this repo. The example
prompts reference well-known styles and characters as *private
prototyping* seeds — what you generate with them, and whether you
publish it, is your responsibility (mind character likenesses and any
music you add). For anything public, write an original prompt: the
pipeline doesn't care.
