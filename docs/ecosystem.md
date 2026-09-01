# Open-source ecosystem study (2026-08)

What exists around H3/H3 Max, what to borrow, and where Multiverse
differentiates. Surveyed 2026-08-31.

## The landscape

### reactor-team/infinite-livestream (Apache-2.0)
Chat-driven perpetual broadcast: Twitch/YouTube `!prompt` → LLM prompt
expansion → FastH3 Preview (MiniMax-H3 35B distilled by FastVideo to
four transformer passes, 90% sparse video attention, 8×B200) → paced
RTMP out. Clean two-part design: a *queue-and-playout contract*
separating generation from a streaming client that handles chat
ingestion and pacing.

- **Borrow:** the RTMP playout client shape (paced output, no gaps) for
  our Twitch/X launch surface; chat-command ingestion maps directly to
  vote-driven dives; the queue/playout contract mirrors our
  engine/player split and confirms it.
- **Differentiation:** it is *linear* infinite TV — disconnected
  prompt-driven clips, no story, no structure. Multiverse is a
  *branching tree of one continuing story* with recursive dives. Nobody
  in the surveyed ecosystem does branching.

### Herrgotts-H3-Infinite-Continuation-Suite (GPL-3.0, ComfyUI)
Keyframe-anchored H3 continuation — independent convergence on our
architecture: repeated last-frames as anchors and "quality resets" that
pull generation back before drift accumulates (= our fracture points +
identity refresh). Two techniques we don't have yet:

- **Freeze-aware cutoff:** detects a frozen/unstable landing tail in a
  generated segment and cuts at a safe boundary *before* it — critical
  QC before a last frame becomes a child's anchor. We should add this
  (simple frame-difference energy check on the tail) to the live lane.
- **Audio-aware stitching:** audio intentionally extends past the video
  cut point (dialogue survives visually discarded frames), with
  context-aware crossfades and de-click at boundaries. Our solo-scene
  audio chains will need exactly this.
- **License hygiene:** GPL-3.0 — reimplement the *ideas* (not
  copyrightable), never copy code into this MIT repo.

### Open-weights H3-Base (MiniMax Community License)
`MiniMaxAI/MiniMax-H3` ships two checkpoints: **FL2VA**
(text + first/last-frame conditioning) and **Ref2VA** (reference-based)
— i.e. our two lanes map 1:1 onto the open checkpoints. Day-0 ComfyUI
support (4 nodes, 6 template workflows); int8 + modulation-LUT pruning
cuts footprint 123.6→42.5 GB, running on an RTX 3060 with offloading;
vLLM-Omni ≥0.26.0 serves an OpenAI-compatible `/v1/videos` for T2VA /
FL2VA / Ref2VA from one diffusion stage.

- **Implication:** the spec's local renderer (§19/§38 "USE LOCAL
  RENDERER") is real: a `h3-local` registry adapter speaking to
  vLLM-Omni gives BYOK-free operation, and FastVideo's FastH3
  distillation is the local path to real-time. The live lane is not
  fal-locked.
- Weights are *community-licensed*, not OSI — flag in local-lane docs.

### Community resources
`MiniMax-AI/awesome-minimax-h3-integration` (official),
`wildminder/awesome-minimax-H3`, and `ai-models-lab/minimax-h3`
(workflows, prompt studio, VRAM calculator) — link from our docs
rather than duplicating.

## Strategic summary

1. **Branching is the moat.** Both serious prior-art projects are
   linear. "Infinite TV exists; Multiverse is infinite *branching* TV
   of your moment" is the launch positioning.
2. **Adopt:** freeze-aware tail cutoff (before anchoring children),
   audio crossfade/de-click stitching, RTMP playout client for Twitch,
   chat-vote dives, `h3-local` (vLLM-Omni FL2VA) renderer adapter.
3. **Validated:** keyframe anchoring as drift control now has two
   independent implementations; our keyframe-skeleton plan
   (realtime-optimization.md layer 2) is the same primitive taken to
   its parallel conclusion.
