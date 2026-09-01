# Contributing

Thanks for your interest in Multiverse.

1. Read [AGENTS.md](AGENTS.md) — it holds the architecture, invariants,
   and contribution boundaries, and applies to humans too.
2. Set up: `uv sync`, then `uv run multiverse doctor`.
3. Test: `uv run pytest`. Tests must not call paid APIs.
4. New renderers go behind the protocol in
   `src/multiverse/renderers/base.py` — see
   [docs/add-a-renderer.md](docs/add-a-renderer.md).
5. Never commit credentials or copyrighted source media.

Open an issue before large changes; V0 scope is deliberately narrow
(see [ROADMAP.md](ROADMAP.md)).
