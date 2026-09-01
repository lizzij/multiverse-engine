# Real-time optimization: getting L below P

Goal: the next scene finishes generating before its parent finishes
playing (P = 5s). Investigation of where the latency lives and how to
remove it. All numbers measured on this account (2026-08-31).

## Measured latencies (5s clip, end-to-end submit→result)

| mode | resolution | total | inference | overhead |
|---|---|---|---|---|
| reference-to-video (3 refs) | 768P | 51.8s | 30.3s | ~21s |
| reference-to-video (3 refs) | 480P | 30.8s | 9.9s  | ~21s |
| reference-to-video (warm)   | 480P | 19–29s | — | — |
| **image-to-video (2 keyframes)** | **480P** | **4.1s** | **0.9s** | ~3s |
| image-to-video (2 keyframes) | 768P | 6.8s | 3.2s | ~4s |

The finding: the ~21s "fixed overhead" was almost entirely
**reference-video tokenization**. Image conditioning skips it. I2V is
~7× faster end-to-end and cheaper (no reference-video token billing).

**480P I2V at 4.1s < 5s playback: real-time is achievable.**

## The layered strategy

### Layer 1 — switch continuations from r2v to I2V (the unlock)

`minimax/h3-max/image-to-video` accepts:
- `image_url` — first frame → pass the **parent's final frame**:
  continuity becomes pixel-exact by construction;
- `end_image_url` — last frame → optional ending keyframe.

Our fracture-point constraint (every scene ends on a held pose) was
already the right primitive: velocity at the cut is ~zero, so a child
started from that frame is seamless. Native audio is included in I2V
output (verified: AAC track present).

Chain cadence becomes ~4–6s/level ≈ P. The player can fracture on
every loop boundary.

### Layer 2 — keyframe-skeleton pipeline (breaks depth entirely)

The only sequential dependency left is "child needs parent's final
frame." Invert the pipeline: generate the **keyframe chain first**,
videos second.

```text
planner beats ──► ending keyframes (fast image model, ~2-4s each,
                   chained: child keyframe conditioned on parent's)
                        │
                        ▼
     ALL videos render in parallel:
     I2V(image_url=parent_end_kf, end_image_url=own_end_kf, prompt=beat)
```

A depth-3 tree (14 scenes) = 14 keyframes (chains of 3, paths parallel,
~10s total) + 14 videos in 2 waves of the 10 slots (~10-15s) — the
whole cycle materializes in ~25s, before the root's first loop ends.
Depth stops being latency-bound at all.

### Layer 3 — identity maintenance (the cost of leaving r2v)

I2V has no identity-anchor input; identity is carried only by the start
frame. Drift risk grows with depth. Mitigations:
- fracture-point poses keep both characters in frame in every keyframe;
- a **slow lane**: periodic r2v "hero" re-render of the committed-path
  node with the seed identity anchor (off the critical path, quietly
  replaces the pane);
- keyframe correction: if an embedding-similarity check against the
  seed's characters falls below threshold, regenerate that keyframe
  with an identity-conditioned image edit before rendering its videos.

### Layer 4 — broadcast-delay scheduling (rhythm, not races)

Decouple the generation clock from the playback clock. The playhead
runs a fixed delay D (~30s) behind the generation frontier, and
fractures fire on a **fixed cadence at loop boundaries** (e.g. every
2-3 loops) instead of "whenever ready". Live TV's seven-second delay,
applied to reality: zero visible waiting, deterministic rhythm, and the
shimmer becomes pure drama rather than actual buffering. Viewer
interaction (dive votes) steers the frontier, taking effect one delay
window later — which maps exactly onto the vote-driven X/Twitch loop.

### Layer 5 — smaller wins
- Pass fal CDN URLs of parent outputs directly as inputs (skip
  download→extract→upload, ~4s, when tails are needed at all).
- `sync_mode` for base64 round-trip on small clips.
- 480P for all live panes; 768P only for the slow-lane hero re-renders.
- Engine resume from tree.json (crash recovery for long streams).

## Bottom line

r2v (dual video anchors) stays the **quality lane** — launch films,
hero exports, identity refresh. I2V keyframe-chaining becomes the
**live lane**: ~4s/scene, pixel-exact cuts, native audio, real-time at
5s beats — and with the keyframe skeleton, entire levels materialize
in parallel.
