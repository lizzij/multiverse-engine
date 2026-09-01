# The universe tree

Two distinct concepts (spec §4):

- **Semantic universe tree** — potentially unbounded. Every node has a
  premise, a divergence, inherited `world_state`, and visible
  consequences.
- **Materialized video branches** — rendered lazily, only for nodes that
  earn attention (fullscreen, clicked, exported, audience-selected).

## Node lifecycle

```text
VIRTUAL → PLANNED → QUEUED → RENDERING → READY
                                    ↘ FAILED (individually retryable)
```

## The inheritance rule (spec §17)

Every child gets `parent semantic state + one new divergence`, but its
pixel reference is always the **original source media**, never a rendered
parent. Rendering from rendered parents accumulates generation drift.

```text
                    ORIGINAL SOURCE
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
      A                   A1                A1a
world state A       state A+A1        state A+A1+A1a
```

## Persistence (spec §48)

```text
runs/RUN_ID/
    source/  scene.json  tree.json  manifest.json
    renders/  thumbnails/  exports/
```

`tree.json` is the serialized `UniverseTree`; any node can later become a
new branch root via `multiverse branch RUN_ID --node ID`.
