# Real-time recursive story branching

Design for the live mode: while a scene plays, its continuations are
generated concurrently; each continuation extends the *story* into a
parallel reality (actions, characters, and world may all diverge), and
every continuation is itself a branch point. The stream never ends.

This extends the V0 spec (docs/spec.md) and **amends invariant §17**.

---

## 1. The two hard problems

### 1a. Continuation breaks the anchor invariant

Spec §17: every render uses the original source as pixel reference, so
drift never accumulates. That works because V0 branches are *reskins of
the same moment*. A story continuation is a *different moment* — it must
begin where its parent ended, which forces chaining renders, which is
exactly the drift path §17 forbids.

### 1b. The critical path is sequential

A child render needs its parent's final frames as input. Therefore:

```text
render(child) cannot start before render(parent) completes
```

Measured on H3 Max: one 8s 768p reference render ≈ 45–60s wall clock
(L). Playback consumes a scene every 8–15s (P). Since L > P and the
chain is sequential, **no amount of parallel workers makes a single
timeline advance faster than one scene per L.** Depth is latency-bound.
Breadth is not: all children of one parent depend only on that parent,
so they render concurrently on the fal queue. Depth = latency problem,
breadth = throughput problem. The design exploits breadth and *hides*
depth.

---

## 2. Amended invariant: dual anchors (replaces §17 for continuations)

Split the single "pixel reference" into two roles:

```text
IDENTITY ANCHOR    original seed video          who/what/style — never changes
CONTINUITY ANCHOR  parent's tail (last ~2s)     where the story is
                   + parent's final frame       the exact starting image
```

Every continuation render passes (H3 Max supports up to 12 mixed refs):

```text
reference_video_urls = [seed.mp4, parent_tail.mp4]     Video 1, Video 2
reference_image_urls = [parent_last_frame.png]         Image 1
```

Prompt contract (prompt compiler v2):

```text
Video 1 is the canonical identity and art-style reference for the
characters and world lineage. Image 1 is the exact first frame of this
scene; begin there. Video 2 shows the immediately preceding moments;
continue the motion seamlessly from its ending.

Then this happens next: [ACTION BEAT]

This reality's premise: [WORLD PREMISE]
Visible consequences: [CONSEQUENCES]

Single continuous take. No cuts. End the scene holding [ENDING POSE].
```

Drift control:
- The identity anchor is present in **every** render at every depth, so
  character/style drift is pulled back toward the seed each generation
  instead of compounding.
- Optional drift score: embedding similarity between each output and the
  seed's subjects; regenerate a node whose score falls below threshold.
- Deep timelines (depth ≳ 6–8) may still stylize. Treat it diegetically:
  distant realities *should* look stranger.

The semantic rule is unchanged: `child = parent state + one divergence`,
except divergence is now narrative as well as environmental — the world,
the characters' choices, and new elements may all fork, provided the
scene *begins* at the parent's ending instant.

---

## 3. Plan-ahead narrative layer (cheap, unbounded)

Rendering is expensive and latency-bound; planning is neither. An LLM
story planner runs arbitrarily far ahead of the render frontier,
populating VIRTUAL nodes (existing NodeStatus) with beats:

```python
class Beat(BaseModel):
    divergence: str            # what forks in this reality
    premise: str               # the world/story premise
    action: str                # what happens during the scene
    ending_pose: str           # the held "fracture point" it ends on
    visible_consequences: list[str]
```

Planner input: the full ancestry chain of beats + world states + the
seed SceneSpec. Planner output: 4 divergent continuations that all begin
at the parent's ending instant.

**Branchability constraint:** every beat must end on a *fracture point*
— a held gesture, look, or tableau — so that any child can begin from a
stable pose. The planner designs for splittability; the renderer is told
to "end the scene holding [ENDING POSE]".

Planner implementation: `claude -p --output-format json` (headless
Claude Code) — reuses the user's existing local auth, no new API key,
and matches the repo's agent-native ethos. ~seconds per node; can plan
hundreds of nodes ahead for pennies.

---

## 4. Scheduler: attention-weighted speculative rendering

State machine per node (existing): `VIRTUAL → PLANNED → QUEUED →
RENDERING → READY / FAILED`.

Priority = distance from the **playback frontier** (the node currently
on screen, per viewer):

```text
p0  children of the playing node          speculative 4-way prefetch
p1  children of the *likely next* node    autopilot: known; interactive: none yet
p2  everything else                       planner-only, never rendered
```

Mechanics:
- The moment a render completes, immediately extract its tail + last
  frame, upload them, and submit its children (if p0/p1) — the pipeline
  runs ahead of playback, not in step with it.
- When the viewer (or autopilot) commits to child C: promote C's
  children to p0; cancel or deprioritize sibling subtrees' outstanding
  jobs (fal queue exposes cancel URLs). Sunk speculative renders are
  kept — they're already-paid content for grid mode.
- Beyond depth+1 from the frontier, nodes stay VIRTUAL. Compute grows
  with attention (spec §25), even in live mode.
- All fal submissions go through the existing lock-flap retry.

Throughput sanity check: steady-state interactive play with 4-way
speculation ≈ 4 renders per accepted scene. With L ≈ 60s and scenes
looping ~L before fracturing (see §5), that's ~4 concurrent jobs — well
within queue limits; cost governor below is the real constraint.

---

## 5. Hiding L: diegetic buffering (the key playback trick)

The stream can't fracture every 8s (L > P). Instead of a spinner:

```text
scene plays (8s) → scene LOOPS while children render,
green time-instability shimmer intensifying each loop
→ children READY → the fracture fires mid-performance
```

Buffering *is* time instability. The seed's Rickle-in-Time grammar
(green tint, crystalline shimmer, ghost afterimages) makes latency part
of the fiction: a reality holds, quivers harder and harder, then
shatters into its continuations. Variable-tempo fracturing reads as
dramatic pacing, not as lag.

Fallbacks, in order: seamless loop with shimmer overlay → slow-motion
tail hold → (never) a loading indicator.

Additional L reducers: 480p for non-hero panes (Tier B), shorter child
durations, `prompt_expansion_mode=balanced`, eager tail upload.

---

## 6. Playback surface (V0 live)

A local player, manifest-driven — no streaming infra:

```text
realtime daemon                        web player (web/)
  tree.json + manifest.json  ←poll──   plays READY node
  writes renders/ as files             loops + shimmer when starving
                                       CSS/WebGL fracture on READY
                                       click a pane = commit path (dive)
```

Two modes:
- **autopilot** — the daemon picks each next reality (weighted random);
  lean-back infinite stream; the path is known one step ahead, so
  speculation is p1-cheap. This is the Twitch-able mode.
- **interactive** — viewer clicks a pane to dive; 4-way p0 speculation;
  commit cancels siblings.

Chat-driven voting (Twitch/X polls choosing the branch) is autopilot
with the picker swapped for an external vote — same scheduler.

---

## 7. Cost governance

Speculation multiplies spend (~4× per accepted scene at p0). Governor:

- budget rate ($/min of stream) checked before every submission batch;
- degrade ladder: hero pane 768p → siblings 480p → siblings as stills
  (Tier C) → pause speculation, autopilot only;
- hard session cap → stream loops existing tree instead of growing it;
- all estimates surfaced (spec §37); `estimate_cost()` per submission.

---

## 8. Build order

- **R1 — sequential proof (no concurrency):** tail/frame extraction →
  `claude -p` beat planner → 4 continuation renders → manifest → web
  player with loop-shimmer-fracture. Proves story continuity + the
  diegetic buffer. Autopilot only.
- **R2 — concurrency:** asyncio scheduler, async fal submits, eager
  child submission on render completion, buffer-ahead, cancellation.
- **R3 — interactivity:** click-to-dive, sibling deprioritization,
  vote-driven picker.
- **R4 — drift scoring & re-anchoring;** cost governor hardening.

The §52-style go/no-go for R1: generate seed → child → grandchild down
one timeline and watch them back-to-back. Question: *does the story
continue and do the characters stay themselves?* If identity survives
three chained generations with dual anchors, the architecture holds.
