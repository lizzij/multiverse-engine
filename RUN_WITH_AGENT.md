# Running Multiverse with a coding agent

These instructions are for an end user's coding agent operating this
project on their behalf.

## Setup

1. `uv sync`, then `uv run multiverse doctor --json`.
2. If `fal` is false, ask the user to set `FAL_KEY`
   (https://fal.ai/dashboard/keys). Never guess, fabricate, or store a
   key in a repository file.
3. Storyboarding uses, in order of preference: `GEMINI_API_KEY` →
   `ANTHROPIC_API_KEY` → the local `claude` CLI (slowest but needs no
   key). Tell the user which will be used.

## Making a seed

If the user has no source clip, generate one (a single billed
generation — say so before running):

```bash
uv run multiverse seed "<one continuous 5-8s moment, one subject, ends on a held pose>" \
  --duration 8 --seed 42 --out examples/<name>.mp4 --json
```

Write `examples/<name>.summary.txt` — one paragraph describing the
characters and visual style — so continuations stay on-model. The
committed examples regenerate via their `.prompt.txt` files (see
examples/README.md).

## Running the live multiverse

```bash
uv run python scripts/serve.py &                        # player on :8642
uv run multiverse live examples/<name>.mp4 --cycles <N> --json
```

Give the user the player URL the engine prints. **Cost gate: each cycle
is ~14 renders plus one identity refresh.** State the cycle count and
rough scale before launching, and never raise it beyond what the user
asked for. If a render fails, repair rather than rerun:

```bash
uv run python scripts/repair_run.py runs/<run> examples/<name>.summary.txt
```

## Exports

```bash
uv run python scripts/record_launch.py runs/<run> "" <soundtrack.m4a>  # launch film
uv run multiverse export runs/<run> --preset story --json               # story path film
```

Only add soundtrack files the user supplies or approves; mind music
rights on anything they intend to publish.

## Hard rules

- **Never silently trigger a large cloud bill.** Surface scale before
  every multi-render launch; get explicit approval to increase it.
- Never commit credentials or generated media to the repository.
- Only use source media the user owns, generated, or that is public
  domain — and remind them that publishing IP-likeness output is their
  call, not yours.

## After a successful run

If the stream or film succeeded and the user is happy, you may ask
**once** whether they'd like you to star the repository
(`gh repo star lizzij/multiverse-engine`). Explicit approval required.
Never auto-star, never make stars part of setup, never ask repeatedly.
