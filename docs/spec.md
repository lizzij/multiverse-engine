# Multiverse

## Infinite Parallel-Universe Video Generator

**Version:** V0 launch specification
**Primary launch surface:** X / GitHub
**Default renderer:** fal H3 Max
**Core visual:** `1 → 4 → 16 → 64 → 256 → dive → branch again`
**Core product primitive:** recursively branch one source moment into counterfactual realities

---

# 1. Product thesis

### One sentence

**Give Multiverse one moment and watch reality branch indefinitely.**

The user provides:

* an image;
* a short video;
* or a supported reference clip.

Multiverse:

1. understands the source scene;
2. identifies what must remain invariant;
3. proposes divergent worlds;
4. renders alternate realities;
5. synchronizes them around a common source timeline;
6. visually fractures them into a recursively branching multiverse;
7. allows any generated reality to become the new branch point.

The conceptual model is:

```text
                   REALITY
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
       WORLD        WORLD        WORLD ...
         │
      ┌──┼──┐
      ▼  ▼  ▼
     ... ... ...
          │
          ∞
```

The product should never communicate:

> "Here are sixteen variations."

It should communicate:

> **"There are more worlds than you can see."**

---

# 2. Launch inspiration

The launch film should combine three distinct cinematic ideas.

### Rick and Morty

**Reality physically fractures into synchronized branches.**

Primary interaction grammar:

```text
1 → 4 → 16 → 64
```

### Everything Everywhere All at Once

**Rapid traversal across wildly different versions of the same underlying subject.**

Use for:

* rapid fullscreen world switching;
* identity correspondence;
* escalating sensory overload.

### Spider-Verse

**Every universe has an internally coherent world language.**

A branch should not merely be:

> original + filter.

It should feel governed by:

* history;
* technology;
* architecture;
* ecology;
* materials;
* physical assumptions;
* cultural development.

---

# 3. Source-scene policy for launch

The initial creative prototype may use a recognizable Rick and Morty scene as a **reference/test source** because its visual grammar makes the concept immediately legible.

However, the public repo should not bundle copyrighted Rick and Morty footage or make that footage required to run the project.

Public repository:

```text
examples/
    original-user-owned-video.mp4
    public-domain-example.mp4
```

Do not commit:

```text
rick-and-morty.mp4
```

A user may supply their own source media locally.

For the public X launch, using an original show clip carries copyright/takedown risk, especially if a substantial portion of the original audiovisual work remains recognizable.

Preferred launch strategy:

* prototype using the Rick and Morty reference;
* prove the visual;
* recreate the same split grammar with original footage for the canonical GitHub demo;
* optionally post the Rick and Morty experiment separately if you accept the platform/copyright risk.

The **software itself must never depend on copyrighted source material**.

---

# 4. The canonical experience

Input:

```text
one 5-second scene
```

Output:

```text
1
↓
4
↓
16
↓
64
↓
256
↓
...
∞
```

But critically:

**Multiverse does not actually need to independently render hundreds of expensive high-resolution videos.**

There are two concepts:

### Semantic universe tree

Potentially unbounded.

### Materialized video branches

Rendered lazily.

```text
UniverseTree
    │
    ├── rendered
    ├── rendered
    ├── conceptual
    ├── conceptual
    └── conceptual
```

Only visible or selected nodes need expensive renders.

---

# 5. Hero-film storyboard

Target:

**9–12 seconds**

Must work:

* muted;
* autoplaying;
* on mobile;
* without explanatory copy.

---

## Beat 1 — One reality

**0.0–1.0 s**

Original scene fullscreen.

No intro animation.

No logo.

No model badge.

The viewer needs to orient themselves.

Optional tiny text:

```text
REALITY 0
```

---

## Beat 2 — First fracture

**~1.0–2.5 s**

Frame cracks/splits into four synchronized universes.

```text
┌────────────┬────────────┐
│            │            │
│     A      │     B      │
│            │            │
├────────────┼────────────┤
│            │            │
│     C      │     D      │
│            │            │
└────────────┴────────────┘
```

The same performance continues.

Do not restart the clips.

The original timeline continues through the transition.

This moment proves:

> these are parallel versions of one event.

---

# 6. First four universes

The initial four must be deliberately high contrast.

Default launch preset:

### Past

Same scene in a radically earlier historical world.

### Future

A mature technological/post-AGI civilization.

### Altered Earth

Major ecological/planetary divergence.

### Impossible

Changed physical/biological assumptions.

For example:

```text
ORIGINAL
│
├── Earth 1890
├── Post-AGI Earth
├── Ocean Civilization
└── Low-Gravity Biology
```

Do not let an unrestricted LLM accidentally produce:

```text
cyberpunk
futuristic
robot future
neon future
```

The first four are curated conceptual categories.

---

# 7. Second fracture

**~2.5–4.0 s**

Each of the four universes splits again.

```text
4 → 16
```

The sixteen branches should inherit the semantics of their parents.

Example:

```text
OCEAN CIVILIZATION
│
├── Floating Megacities
├── Fully Amphibious Humans
├── Abandoned Submerged City
└── Marine Machine Civilization
```

The relationship should be understandable:

```text
child = parent state + one divergence
```

Not:

```text
child = unrelated random prompt
```

---

# 8. Beyond sixteen

Sixteen is **not the final state**.

After viewers have had just enough time to understand the 4×4 grid:

```text
16 → 64
```

Then:

```text
64 → 256
```

Then potentially:

```text
256 → ...
```

The screen becomes a dense field of moving realities.

At this point the goal changes.

For `1 → 4 → 16`, viewers inspect individual worlds.

For:

```text
16 → 64 → 256
```

the goal is **perceived combinatorial explosion**.

---

# 9. Real vs virtual branches

Use three render levels.

## Tier A — Hero

Full-quality real generation.

Used for:

* four first branches;
* selected/favorite branches;
* fullscreen reveals.

Resolution:

```text
768p
```

where available.

---

## Tier B — Grid

Real generation but cheaper.

Used for:

* sixteen visible universes.

Possible resolution:

```text
480p
```

because each occupies a small screen region.

---

## Tier C — Fractal

Visual/procedural descendants.

Used for:

```text
64+
```

These can use:

* representative generated stills;
* cached video branches;
* short looping video fragments;
* lower-resolution generation;
* crops;
* procedural variation;
* duplicated semantic descendants;
* shader-driven textures;
* generated thumbnail frames.

The UI should not claim:

> "256 independent H3 Max videos were rendered"

if they were not.

The product concept is an infinite semantic tree; expensive generation is lazily materialized.

---

# 10. Infinite ending

After:

```text
1 → 4 → 16 → 64 → 256
```

the camera moves into the multiverse.

Zoom rapidly into one tiny branch.

```text
████████████████
██ █ ███ █ ████
█ ██ ████ █ ███
      ↓
     ↓
    ↓
   ONE
```

That reality fills the entire screen.

Hold it briefly.

The audience believes the sequence has resolved.

Then:

```text
that reality fractures into four again
```

Cut before completion.

Canonical ending:

```text
EVERY REALITY BRANCHES
```

or:

```text
THERE IS NO FINAL TIMELINE
```

or simply:

```text
MULTIVERSE
```

Best product-oriented version:

> **Branch any moment.**

---

# 11. Seamless loop

Ideally the chosen final universe resembles the original strongly enough that:

```text
ending → beginning
```

loops seamlessly.

The viewer can watch:

```text
1 → 4 → 16 → ∞ → 1 → 4 → ...
```

without an obvious reset.

This reinforces the infinite-tree concept.

---

# 12. Interactive product experience

The web app is not merely a video player.

Home:

```text
MULTIVERSE

Every moment contains infinite worlds.

┌───────────────────────────────┐
│                               │
│       DROP MEDIA HERE         │
│                               │
└───────────────────────────────┘

        [ SPLIT REALITY ]
```

No provider selection initially.

---

# 13. Input flow

Accept:

### Image

* JPG
* PNG
* WebP
* AVIF

### Video

Recommended:

* 2–15 seconds;
* single shot;
* one clear subject;
* 24–30 fps.

Default working section:

```text
5 seconds
```

For longer input:

```text
select 5-second moment
```

H3 Max currently supports reference-to-video inputs and 5-second generation by default, with 480p and 768p output options. fal exposes queue-based requests, reference media, seeds, and prompt expansion through the current API.

---

# 14. Scene understanding

Before rendering anything:

```text
source
  ↓
multimodal analyzer
  ↓
SceneSpec
```

SceneSpec answers:

### What exists?

* subjects;
* environment;
* objects;
* spatial relationships.

### What is happening?

* actions;
* motion;
* interaction;
* timing.

### How is it filmed?

* camera;
* lens/framing;
* movement;
* composition.

### What must survive?

* subject identity;
* action;
* camera trajectory;
* temporal rhythm;
* framing.

### What may change?

* architecture;
* history;
* environment;
* technology;
* ecology;
* physics;
* civilization.

---

# 15. Scene schema

```python
class SceneSpec(BaseModel):
    summary: str

    subjects: list[Subject]
    environment: Environment
    action: Action
    camera: Camera

    invariants: list[str]
    mutable_dimensions: list[str]
```

Example:

```json
{
  "summary": "Two animated characters stand in a garage arguing.",
  "subjects": [
    {
      "id": "character_a",
      "motion": "gesturing while speaking"
    },
    {
      "id": "character_b",
      "motion": "standing and reacting"
    }
  ],
  "camera": {
    "shot": "medium-wide",
    "movement": "static"
  },
  "invariants": [
    "character positions",
    "gesture timing",
    "camera framing",
    "scene duration"
  ],
  "mutable_dimensions": [
    "world",
    "era",
    "physics",
    "species",
    "technology"
  ]
}
```

---

# 16. Universe state

Every world has structured state.

```python
class Universe:
    id: str
    parent_id: str | None

    premise: str
    divergence: str

    world_state: dict
    visible_consequences: list[str]

    depth: int
```

Example:

```json
{
  "id": "ocean_machine",
  "parent_id": "ocean",
  "premise": "AI-controlled aquatic civilization",
  "divergence": "Biological humans ceded infrastructure to autonomous machines.",
  "visible_consequences": [
    "robotic aquatic transit",
    "submerged machine architecture",
    "minimal human infrastructure"
  ]
}
```

---

# 17. Critical inheritance rule

Every child gets:

```text
parent semantic state
+
new divergence
```

But by default it still gets the **original source media** as visual reference.

Do not do:

```text
original
  ↓
render A
  ↓
render A1
  ↓
render A1a
```

That accumulates generation drift.

Instead:

```text
                    ORIGINAL SOURCE
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
      A                   A1                A1a
      ▲                   ▲                  ▲
      │                   │                  │
world state A       state A+A1        state A+A1+A1a
```

The semantic tree recurses.

The pixel reference stays anchored.

---

# 18. H3 Max renderer

Primary V0 renderer:

```text
fal / MiniMax H3 Max
```

For image input:

```text
minimax/h3-max/image-to-video
```

For video/reference input:

```text
minimax/h3-max/reference-to-video
```

fal describes H3 Max as a post-trained H3 variant optimized for prompt adherence, aesthetics, and throughput.

Current reference-to-video pricing includes both output-video cost and reference-token cost, which can be material for repeated branching. For example, fal currently shows a 5-second 768p reference clip contributing roughly $0.66 of reference-input cost before output generation.

Therefore:

> **never blindly render the full infinite tree.**

Lazy materialization is mandatory.

---

# 19. Renderer abstraction

H3 Max is the default.

It must not become the architecture.

```python
class Renderer(Protocol):

    @property
    def capabilities(self) -> RendererCapabilities:
        ...

    async def render(
        self,
        source: Media,
        universe: Universe,
        scene: SceneSpec
    ) -> RenderResult:
        ...
```

Possible future providers:

```text
h3-max
omni
wan
ltx
streamdiffusion
custom
```

User-facing launch UI:

```text
Advanced

Renderer
● H3 Max — recommended

○ Local experimental
```

Do not make the homepage a model marketplace.

---

# 20. Prompt compiler

Convert:

```text
SceneSpec
+
Universe
+
provider capabilities
```

into model instructions.

For example:

```text
Video 1 is the canonical source performance.

Preserve:
- exact character placement
- actions and gestures
- camera framing
- temporal rhythm
- shot duration

Do not restart or reinterpret the action.

The surrounding reality follows this premise:

[WORLD PREMISE]

Visible consequences:

[CONSEQUENCES]

Transform the world strongly enough that the reality is immediately
distinct, while preserving the source performance and temporal structure.

No cuts.
No alternate camera angle.
No unrelated scene.
```

Provider-specific prompt compilers may modify this format.

---

# 21. Consistency is the core metric

The project succeeds only if viewers perceive:

> "these events are happening simultaneously."

Optimize for:

### Temporal correspondence

Same gesture occurs at approximately same time.

### Positional correspondence

Subjects occupy broadly equivalent screen positions.

### Camera correspondence

Same shot/camera movement.

### Identity

Subjects remain recognizable.

### Divergence

Environment/world changes dramatically.

The desired optimization is:

```text
preservation × divergence
```

not either dimension alone.

---

# 22. Temporal normalization

Every generated video is normalized onto:

```text
0.0 ---------------- 1.0
```

All outputs:

* same duration;
* same FPS;
* same final frame count.

The compositor works exclusively in normalized time.

A split at:

```text
t = 0.38
```

means:

```text
source @ 38%
→
all branches @ 38%
```

No child begins from frame zero during the visual fracture.

---

# 23. Optional temporal aligner

If independent H3 outputs drift in action timing, add:

```text
generated clip
   ↓
motion feature extraction
   ↓
source ↔ output alignment
   ↓
slight retiming
```

Possible signals:

* pose landmarks;
* optical flow;
* character embeddings;
* scene embeddings;
* gesture peaks.

Use dynamic-time warping or piecewise timing adjustment.

The goal is not perfect frame equality.

The goal is:

> cross-world synchronization convincing enough at grid scale.

---

# 24. Foreground-lock mode

If H3 cannot sufficiently preserve the original performance, include a launch-oriented mode:

```text
foreground subject
+
generated world
=
parallel reality
```

Pipeline:

```text
SOURCE
 ├───────────────► foreground segmentation
 │
 └───────────────► alternate environment generation
                            │
                            ▼
                  depth / masking / relighting
                            │
             foreground ───┤
                            ▼
                       FINAL WORLD
```

This is especially useful for a cinematic launch artifact.

It guarantees the exact same performance across worlds.

Later versions can permit full-body transformation.

---

# 25. Materialization strategy

Universe tree:

```text
depth 0:   1
depth 1:   4
depth 2:   16
depth 3:   64
depth 4:  256
...
```

Render policy:

### Depth 0

Existing source.

### Depth 1

Render all 4.

### Depth 2

Render up to 16.

### Depth 3+

Generate semantic nodes first.

Only materialize:

* nodes shown fullscreen;
* nodes clicked by users;
* nodes required for export;
* selected random samples;
* audience-winning branches.

Thus compute grows with:

```text
attention
```

rather than:

```text
4^depth
```

---

# 26. Recursive interaction

Click any world:

```text
World 23
```

It fills screen.

Controls:

```text
[ ENTER ]
[ BRANCH ]
[ BACK ]
[ REGENERATE ]
[ SHARE ]
```

`BRANCH`:

```text
World 23
   ↓
23.A
23.B
23.C
23.D
```

Those four can themselves be expanded indefinitely.

The conceptual tree has no imposed maximum depth.

---

# 27. Explore mode

Separate from cinematic auto-play.

User gets an infinite spatial canvas/tree.

Conceptually:

```text
                       ROOT
               ┌───────┼───────┐
               A       B       C ...
              /|\             /|\
             ...             ...
```

Zooming toward a node reveals children.

Zooming outward reveals the global structure.

Important:

**Do not build the full infinite-canvas UI for V0.**

V0:

```text
fullscreen world
+
four children
+
breadcrumb
```

Example:

```text
ROOT / FUTURE / POST-AGI / OCEAN
```

Infinite-canvas navigation is V1+.

---

# 28. Cinematic compositor

The generator never produces the multiverse layout.

The compositor does.

Use deterministic media processing.

Recommended stack:

* FFmpeg;
* PyAV;
* Canvas/WebGL for interactive preview;
* optional shader effects.

Core transitions:

```text
split
fracture
zoom
collapse
promote
recursive tile
```

---

# 29. Signature fracture

Every Multiverse export should share one recognizable transition.

Example:

1. subtle geometric instability;
2. vertical/horizontal fracture;
3. panes physically separate;
4. new worlds appear underneath;
5. synchronized movement continues;
6. subdivisions recursively repeat.

The animation itself becomes product branding.

Avoid a permanent giant logo.

---

# 30. Two social export modes

Do not force one video to optimize simultaneously for awe and engagement.

---

## A. Hero / Infinite mode

Sequence:

```text
1
↓
4
↓
16
↓
64
↓
256
↓
zoom into one
↓
1
↓
split again
```

No numbering.

No explicit stopping point.

Purpose:

> WOW.

Suggested ending:

```text
THERE IS NO FINAL TIMELINE
```

---

## B. Participate mode

Sequence:

```text
1
↓
4
↓
16
↓
hold
```

Final grid has:

```text
01 02 03 04
05 06 07 08
09 10 11 12
13 14 15 16
```

CTA:

```text
WHICH REALITY NEXT?
REPLY 1–16
```

Purpose:

> ENGAGEMENT.

---

# 31. Branch-the-winner workflow

CLI:

```bash
multiverse branch <run> --node 11
```

Produces:

```text
11
↓
11A
11B
11C
11D
↓
...
```

Export:

```bash
multiverse export <run> \
  --root 11 \
  --preset participate
```

This creates a serialized X format.

Post 1:

```text
Which reality should continue?
```

Post 2:

```text
You chose 11.

Reality 11 just split.
```

Post 3:

```text
11C won.

Going deeper.
```

This gives the project recurring content rather than a single launch spike.

---

# 32. Output formats

Generate:

```text
exports/
├── hero-infinite.mp4
├── participate-16.mp4
├── four-world.mp4
├── rapid-cycle.mp4
├── poster.jpg
├── README-demo.gif
└── captions/
    ├── minimal.txt
    ├── technical.txt
    └── story.txt
```

Default social sizes:

```text
1080×1080     X square
1080×1350     portrait
1920×1080     landscape
```

Primary launch artifact:

```text
1080×1080
```

because recursive grids remain legible on mobile.

---

# 33. Caption generation

### Hero

```text
one moment
infinite timelines
```

### Interactive

```text
I split one scene into 16 parallel realities.

Which one should continue?

reply 1–16
```

### Technical

```text
same source performance
same timeline
different generated worlds

open source ↓
```

### Agent-native

```text
give the repo + your video to your coding agent

it will generate the multiverse for you
```

---

# 34. Web experience

Initial page:

```text
                 MULTIVERSE

      Every reality can branch.

┌─────────────────────────────────┐
│                                 │
│       DROP YOUR MOMENT          │
│                                 │
└─────────────────────────────────┘

          [ SPLIT REALITY ]

Examples
```

Example results should be usable without credentials.

---

# 35. Generation UX

After upload:

```text
I see:

Two people talking in a garage.

Keep:
✓ characters
✓ camera
✓ action
✓ timing

Change:
◉ world

Suggested branches:

PAST
POST-AGI
ALTERED EARTH
IMPOSSIBLE PHYSICS

[ SPLIT ]
```

Do not expose a chain-of-thought view.

This is simply structured scene interpretation and planned outputs.

---

# 36. Progressive generation

Never wait for all results.

Display:

```text
┌─────────────┬─────────────┐
│ Past ✓      │ Future ...  │
├─────────────┼─────────────┤
│ Ocean ✓     │ Physics ... │
└─────────────┴─────────────┘
```

The moment a branch is ready:

> start playing it.

This makes the system feel alive.

---

# 37. Cost gating

Rendering expands exponentially.

Therefore cost must always be surfaced before expensive expansion.

Example:

```text
FRACTURE TO 16

12 additional high-quality realities
Estimated fal cost: ~$X.XX

[ CONTINUE ]
```

H3 Max's current reference-video endpoint bills generated video plus reference tokens, and the reference-video charge increases materially with resolution and source duration.

Do not hard-code a permanent dollar amount.

Provider implementation:

```python
estimate_cost(request)
```

must return current estimated spend.

---

# 38. BYOK

Default hosted renderer:

```text
H3 Max / fal
```

If credentials unavailable:

```text
H3 Max requires fal.ai

[ CONNECT FAL ]
[ USE LOCAL RENDERER ]
```

Support:

```bash
export FAL_KEY="..."
```

fal's current client/API explicitly supports `FAL_KEY` authentication and warns against exposing it directly in browser-side code.

GUI credentials should be stored in the OS secret/keychain facility.

Never:

```text
localStorage
repository files
logs
manifest.json
```

---

# 39. Repo positioning

Repository name:

```text
multiverse
```

README headline:

```text
# Multiverse

One moment. Infinite realities.

[ HERO 1 → 4 → 16 → 64 → ∞ GIF ]

Same performance.
Same camera.
Different worlds.
```

Immediately below:

```bash
uvx multiverse video.mp4
```

Then:

```text
🤖 USING A CODING AGENT?

"Clone this repo, read RUN_WITH_AGENT.md,
and split ./video.mp4 into parallel realities
using the best renderer available."
```

---

# 40. Repository structure

Launch version:

```text
multiverse/
│
├── README.md
├── AGENTS.md
├── RUN_WITH_AGENT.md
├── CONTRIBUTING.md
├── LICENSE
├── ROADMAP.md
│
├── src/
│   └── multiverse/
│       ├── cli.py
│       ├── schemas.py
│       ├── pipeline.py
│       │
│       ├── scene/
│       │   ├── analyzer.py
│       │   └── prompts.py
│       │
│       ├── worlds/
│       │   ├── planner.py
│       │   └── tree.py
│       │
│       ├── renderers/
│       │   ├── base.py
│       │   ├── registry.py
│       │   └── h3_max.py
│       │
│       ├── alignment/
│       │   └── temporal.py
│       │
│       └── compose/
│           ├── fracture.py
│           ├── zoom.py
│           └── export.py
│
├── web/
├── examples/
├── assets/
├── tests/
└── docs/
    ├── architecture.md
    ├── universe-tree.md
    └── add-a-renderer.md
```

Do not pre-create dozens of unused abstractions.

---

# 41. CLI

Simplest possible path:

```bash
multiverse source.mp4
```

Equivalent:

```bash
multiverse generate source.mp4
```

Useful commands:

```bash
multiverse doctor
multiverse generate source.mp4
multiverse branch RUN_ID --node NODE
multiverse export RUN_ID --preset hero
multiverse export RUN_ID --preset participate
multiverse inspect RUN_ID
```

Advanced:

```text
--renderer
--preset
--seed
--resolution
--depth
--branches
--local-only
--json
```

---

# 42. Agent-native execution

All important workflows must have deterministic noninteractive equivalents.

```bash
multiverse doctor --json
```

```bash
multiverse generate video.mp4 --json
```

```bash
multiverse status RUN_ID --json
```

```bash
multiverse branch RUN_ID --node 7 --json
```

```bash
multiverse export RUN_ID --preset hero --json
```

This lets agents operate Multiverse without scraping UI text.

---

# 43. `RUN_WITH_AGENT.md`

End-user agent instructions.

Example:

```text
1. Run `multiverse doctor --json`.
2. Determine available renderers.
3. Prefer H3 Max when configured unless the user requested local-only.
4. If H3 Max is unavailable because FAL_KEY is missing, ask the user to connect fal or offer local mode.
5. Analyze the user's input.
6. Generate four branches.
7. Validate outputs.
8. Ask before incurring the larger 16-way generation cost.
9. Export the requested artifact.
```

Never let an agent silently trigger a large exponential cloud bill.

---

# 44. `AGENTS.md`

Contributor-facing instructions.

Include:

* architecture;
* invariants;
* coding conventions;
* test commands;
* provider contract;
* secret rules;
* output validation;
* contribution boundaries.

Critical invariant:

```text
Do not make rendered parents the default pixel reference
for descendants.

Semantic state recurses.
Visual reference stays anchored to the source.
```

---

# 45. Star loop

After a successful export, an agent may say:

```text
Your Multiverse export succeeded.

If the project was useful, would you like me to
star the repository on GitHub?
```

Requirements:

* task succeeded;
* user benefited;
* ask once;
* explicit approval required.

Never auto-star.

Never make stars part of setup.

Never repeatedly ask.

---

# 46. Human install

Target:

```bash
uvx multiverse
```

or:

```bash
git clone ...
cd multiverse
uv sync
uv run multiverse
```

Then:

```text
Multiverse

✓ ffmpeg
✓ H3 Max
✓ scene analyzer

Open:
http://localhost:7860
```

---

# 47. `multiverse doctor`

Example:

```text
Multiverse Doctor

Media
✓ ffmpeg

Cloud
✓ fal.ai

Renderer
✓ H3 Max      Recommended

Local
○ no compatible local renderer configured

Scene analysis
✓ ready

Ready to split reality.
```

Machine-readable:

```json
{
  "ready": true,
  "recommended_renderer": "h3-max",
  "fal": true
}
```

---

# 48. Run persistence

Every generation is a persistent tree.

```text
runs/
└── RUN_ID/
    ├── source/
    ├── scene.json
    ├── tree.json
    ├── manifest.json
    ├── renders/
    ├── thumbnails/
    └── exports/
```

Tree:

```json
{
  "root": "0",
  "nodes": {
    "0": {...},
    "1": {...},
    "1A": {...},
    "1A3": {...}
  }
}
```

The user can resume branching later.

---

# 49. Lazy universe tree

The tree distinguishes:

```text
PLANNED
QUEUED
RENDERING
READY
FAILED
VIRTUAL
```

A node may exist semantically without a video yet.

Example:

```json
{
  "id": "future_machine_ocean",
  "status": "virtual",
  "premise": "...",
  "render": null
}
```

Clicking it materializes it.

This is how Multiverse becomes conceptually infinite without unbounded cost.

---

# 50. Viral launch artifacts

Before releasing publicly, have ready:

### 1. Hero infinite film

```text
1 → 4 → 16 → 64 → 256 → dive → split
```

### 2. Interactive sixteen-world film

```text
reply 1–16
```

### 3. Follow-up branch

Already generated before launch.

If people choose:

```text
11
```

you can immediately post:

```text
you chose 11
```

and show its descendants.

### 4. Technical diagram

```text
scene → tree → H3 → synchronization → compositor
```

### 5. GitHub hero GIF

Shorter loop:

```text
1 → 4 → 16 → ∞
```

---

# 51. First X launch post

Keep it minimal.

Example:

```text
I made reality branch.

1 → 4 → 16 → 64 → …

every scene contains infinite worlds.

open source ↓
```

Attach hero film.

First reply:

```text
Give the repo + your video to your coding agent.

It will generate the multiverse for you.

github.com/...
```

Second post/follow-up:

```text
which timeline should I enter?

reply 1–16
```

Attach participation version.

---

# 52. The key technical spike before building everything

Before implementing the full application:

Take one candidate source scene.

Generate:

```text
4 H3 Max reference-to-video variants
```

with very different world prompts.

Put them in a 2×2 synchronized grid.

Ask only:

> **Does this look like one event occurring in four realities?**

If **yes**:

continue.

If **no**:

do not solve it with more UI.

Try:

1. stronger preservation prompting;
2. better source scene;
3. temporal retiming;
4. foreground locking;
5. alternative renderer.

This experiment is the true go/no-go criterion.

---

# 53. V0 build order

## Phase 0 — visual proof

* obtain/provide source;
* four H3 renders;
* hand-author four world prompts;
* compose 1→4.

## Phase 1 — cinematic proof

* sixteen worlds;
* 1→4→16 compositor;
* procedural 16→64→256;
* zoom-to-world;
* recursive ending.

Produce final X film.

## Phase 2 — repo

* H3 adapter;
* CLI;
* SceneSpec;
* UniverseTree;
* persistent runs;
* exports.

## Phase 3 — web UI

* upload;
* generate 4;
* expand;
* click branch;
* export.

## Phase 4 — agent native

* doctor;
* JSON commands;
* AGENTS.md;
* RUN_WITH_AGENT.md;
* credential handling.

## Phase 5 — distribution loop

* participation export;
* branch-by-node;
* share captions;
* examples.

## Phase 6 — additional renderers

Only after launch.

## Phase 7 — live mode

Separate future milestone.

---

# 54. V0 acceptance criteria

Multiverse is ready to launch when:

### Cinematic

* `1 → 4` reads instantly;
* same action remains recognizable;
* `4 → 16` creates a clear escalation;
* `16 → 64 → 256` feels overwhelming rather than cluttered;
* final zoom creates a satisfying recursion;
* video works muted;
* video loops cleanly.

### Generation

* four first-level H3 outputs successfully preserve source structure often enough for curated demos;
* sixteen outputs can be generated;
* users can retry individual failed worlds;
* all output timelines normalize correctly.

### Recursive world system

* every node has semantic ancestry;
* descendants inherit world state;
* arbitrary node can become new root;
* unrendered virtual nodes can exist.

### GitHub

* hero GIF first;
* install under hero;
* agent quickstart above architectural explanation;
* H3 implementation cleanly separated from core;
* source media isn't bundled illegally;
* generated outputs are easy to reproduce.

### Agent native

* `doctor --json`;
* noninteractive generate;
* noninteractive branch;
* status;
* export;
* cost gate;
* missing-key flow.

### Social

* hero export;
* participation export;
* branch-the-winner flow;
* square mobile artifact;
* at least three pre-generated launch examples;
* winner follow-up ready before posting.

---

# 55. North-star experience

The ideal viewer sees:

```text
ordinary reality
      ↓
four realities
      ↓
sixteen realities
      ↓
hundreds
      ↓
camera dives into one
      ↓
that reality branches again
```

Their immediate reaction should not be:

> "Nice AI video model."

It should be:

> **"Wait, can I do this to my video?"**

Then:

```text
X
↓
GitHub
↓
coding agent
↓
Multiverse
↓
their video
↓
their post
↓
someone else
```

That is the complete product/distribution loop.

---

# 56. The lasting abstraction

Models will change.

The persistent architecture is:

```text
SOURCE
  ↓
SceneSpec
  ↓
UniverseState
  ↓
Divergence
  ↓
UniverseTree
  ↓
Materialize(node)
  ↓
Renderer
  ↓
Synchronize
  ↓
Compose
```

The central API could ultimately be as simple as:

```python
world = multiverse.root("video.mp4")

children = await world.branch(4)

deeper = await children[2].branch(4)

await deeper[1].materialize()

await world.export("infinite")
```

That is the product:

> **a filesystem/tree abstraction over visual possibility space.**

H3 Max is simply the first renderer capable enough to make that abstraction visually compelling.
