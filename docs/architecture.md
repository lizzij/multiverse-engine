# Architecture

The lasting abstraction (spec §56) — models will change, this won't:

```text
SOURCE
  ↓
SceneSpec          scene/analyzer.py — what exists, what survives, what may change
  ↓
UniverseState      schemas.py — premise, divergence, world_state, consequences
  ↓
Divergence         worlds/planner.py — curated first four, then LLM planning
  ↓
UniverseTree       worlds/tree.py — lazy, semantic, potentially unbounded
  ↓
Materialize(node)  pipeline.py — attention-driven, cost-gated
  ↓
Renderer           renderers/ — protocol; h3-max is the first provider
  ↓
Synchronize        alignment/temporal.py — shared 0.0–1.0 timeline
  ↓
Compose            compose/ — deterministic fracture / zoom / export
```

North-star API:

```python
world = multiverse.root("video.mp4")
children = await world.branch(4)
deeper = await children[2].branch(4)
await deeper[1].materialize()
await world.export("infinite")
```

The product is a filesystem/tree abstraction over visual possibility
space.

Key boundaries:

- **Core never imports provider SDKs.** Adapters import lazily.
- **The generator never lays out the multiverse.** Composition is
  deterministic media processing (FFmpeg/PyAV).
- **Render tiers** (spec §9): Hero 768p for the first four and fullscreen
  reveals; Grid 480p for the sixteen; Fractal/procedural for 64+.
