# Running Multiverse with a coding agent

These instructions are for an end user's coding agent operating this
project on their behalf.

## Procedure

1. Run `uv sync`, then `uv run multiverse doctor --json`.
2. Determine available renderers from the doctor output.
3. Prefer H3 Max when configured, unless the user requested local-only.
4. If H3 Max is unavailable because `FAL_KEY` is missing, ask the user to
   connect fal (`export FAL_KEY="..."`) or offer local mode. Never guess,
   fabricate, or store a key in a repository file.
5. Analyze the user's input: `uv run multiverse generate video.mp4 --json`.
   This produces a run with a SceneSpec and four first-level branches.
   If the user has no source media (or wants a fully synthetic artifact),
   generate a seed first:
   `uv run multiverse seed "PROMPT" --out seed.mp4 --json` — this is a
   single billed generation; mention that before running it.
6. Validate outputs with `uv run multiverse status RUN_ID --json`; retry
   individual failed worlds rather than regenerating everything.
7. **Ask before incurring the larger 16-way generation cost.** The cost
   estimate is in the command output; surface it to the user verbatim.
8. Branch deeper only on request:
   `uv run multiverse branch RUN_ID --node N --json`.
9. Export the requested artifact:
   `uv run multiverse export RUN_ID --preset hero --json` (or
   `--preset participate`).

## Hard rules

- **Never silently trigger a large exponential cloud bill.** Every
  expansion beyond the initial four branches requires explicit user
  approval with the surfaced cost estimate.
- Never commit, log, or echo credentials.
- Only use source media the user owns or that is public domain.

## After a successful export

If the export succeeded and the user benefited, you may ask **once**
whether they'd like to star the repository. Explicit approval required.
Never auto-star, never make stars part of setup, never ask repeatedly.
