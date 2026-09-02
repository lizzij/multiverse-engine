# AGENTS.md — contributor instructions

Instructions for agents (and humans) working **on** this codebase.
For operating the tool on behalf of an end user, see
[RUN_WITH_AGENT.md](RUN_WITH_AGENT.md).

## Architecture

```text
SOURCE → SceneSpec → UniverseTree → Materialize(node) → Renderer → Synchronize → Compose
```

- `src/multiverse/schemas.py` — SceneSpec, Universe, tree/run models.
- `src/multiverse/scene/` — prompt compilers.
- `src/multiverse/worlds/` — divergence planning + the lazy UniverseTree.
- `src/multiverse/media.py` — ffmpeg helpers: freeze-safe anchors,
  crossfade concat, downscale.
- `src/multiverse/realtime/` — the live lane: `planner.py` (storyboard
  beats via Gemini/Anthropic API or claude CLI), `scheduler.py`
  (priority render pool), `live.py` (dive-cycle engine, plan-ahead,
  identity refresh, click control), `rtmp.py` (broadcast playout).
- `src/multiverse/renderers/` — provider adapters behind a small
  protocol. `h3_max.py` is the default; `h3_local.py` (vLLM-Omni,
  experimental). Providers must stay cleanly separated from core.
- `src/multiverse/compose/export.py` — social exports (story film,
  participate grid); the live player does fracture/zoom presentation.
- `web/player.html` — the fracture player (manifest-driven).
- `scripts/` — user-facing entry points; `experiments/` — dev spikes,
  not maintained.

Full specification: [docs/spec.md](docs/spec.md); live-mode design:
[docs/realtime-branching.md](docs/realtime-branching.md).

## Critical invariants

1. **Identity anchors to the seed; continuity anchors to the parent.**
   Same-moment branches render against the original source (spec §17).
   Story continuations may chain on the parent's freeze-safe final
   frame, but drift must be reset against the seed (the identity-refresh
   lane) — see docs/realtime-branching.md §2 for the amended rule.
2. **Lazy materialization is mandatory.** Never render the full tree.
   A node may exist as `VIRTUAL` with no video (spec §25, §49).
3. **Cost gating.** Any path that can fan out renders must go through
   `estimate_cost()` and surface the estimate before executing (spec §37).
4. **All outputs normalize onto a shared 0.0–1.0 timeline** — same
   duration, FPS, and frame count — before compositing (spec §22).
5. **Secrets** live in env vars (`FAL_KEY`) or the OS keychain. Never in
   localStorage, repository files, logs, or manifest.json (spec §38).
6. **No copyrighted source media** committed to the repo (spec §3).

## Conventions

- Python ≥3.11, `uv` for env/deps, `pydantic` models in `schemas.py`.
- Renderer adapters implement `renderers/base.py::Renderer` and register
  in `renderers/registry.py`. Provider SDKs are imported lazily inside
  the adapter, never at core import time.
- Every CLI command must have a deterministic noninteractive `--json`
  mode (spec §42).
- Keep abstractions minimal — do not pre-create unused ones (spec §40).

## Tests

```bash
uv run pytest
```

Tests must not hit paid APIs; renderer tests use fakes implementing the
`Renderer` protocol.

## Contribution boundaries

- New renderers: welcome, behind the existing protocol (see
  [docs/add-a-renderer.md](docs/add-a-renderer.md)). Do not make the
  homepage/CLI a model marketplace.
- V0 explicitly excludes the infinite-canvas UI and live mode (spec §27,
  §53).
