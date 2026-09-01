# Multiverse

One moment. Infinite realities.

<!-- HERO GIF: 1 → 4 → 16 → 64 → ∞ (assets/hero.gif, produced in Phase 1) -->

Same performance.
Same camera.
Different worlds.

Give Multiverse an image or a short clip and it recursively branches that
moment into counterfactual realities — synchronized around the original
timeline, fracturing `1 → 4 → 16 → 64 → 256 → dive → branch again`.

## Install

```bash
git clone https://github.com/lizzij/multiverse-engine.git
cd multiverse-engine
uv sync
uv run multiverse doctor
```

Then either branch your own clip:

```bash
uv run multiverse generate your-video.mp4
```

or generate a fully synthetic seed first (no source media, no copyright
exposure — the whole artifact is end-to-end generated):

```bash
uv run multiverse seed "two inventors argue over a strange machine in a cluttered garage" --out seed.mp4
uv run multiverse generate seed.mp4
```

## 🤖 Using a coding agent?

> "Clone this repo, read RUN_WITH_AGENT.md, and split ./video.mp4 into
> parallel realities using the best renderer available."

See [RUN_WITH_AGENT.md](RUN_WITH_AGENT.md).

## How it works

```text
SOURCE
  ↓
SceneSpec        what exists, what must survive, what may change
  ↓
UniverseTree     semantic branches (potentially unbounded)
  ↓
Materialize      lazy — only visible/selected nodes get expensive renders
  ↓
Renderer         fal H3 Max by default (BYOK: export FAL_KEY=...)
  ↓
Synchronize      normalized timeline, cross-world correspondence
  ↓
Compose          signature fracture → grid → zoom → recurse
```

Two key invariants:

1. **The semantic tree recurses; the pixel reference stays anchored.**
   Every child universe inherits its parent's world state plus one
   divergence, but renders against the *original* source media — never a
   rendered parent — so generation drift doesn't accumulate.
2. **Lazy materialization is mandatory.** The tree is conceptually
   infinite; compute grows with attention, not with `4^depth`. Cost is
   always surfaced before expensive expansion.

## CLI

```bash
multiverse doctor                       # environment / credentials check
multiverse seed "PROMPT"                # generate a synthetic source moment
multiverse generate source.mp4          # analyze + branch into 4 worlds
multiverse branch RUN_ID --node 11      # branch any node into 4 children
multiverse export RUN_ID --preset hero  # hero / participate exports
multiverse inspect RUN_ID               # show the universe tree
```

Every command supports `--json` for noninteractive/agent use.

## Renderers

H3 Max (via [fal.ai](https://fal.ai)) is the default renderer, not the
architecture. Renderers implement a small protocol
(`src/multiverse/renderers/base.py`) — see
[docs/add-a-renderer.md](docs/add-a-renderer.md).

Credentials: `export FAL_KEY="..."`. Keys are never written to the repo,
logs, or run manifests.

## Docs

- [docs/spec.md](docs/spec.md) — full V0 launch specification
- [docs/architecture.md](docs/architecture.md)
- [docs/universe-tree.md](docs/universe-tree.md)
- [ROADMAP.md](ROADMAP.md)

## License

MIT — see [LICENSE](LICENSE). Example media in `examples/` is
user-owned or public-domain only; the software never depends on
copyrighted source material.
