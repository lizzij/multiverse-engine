# Roadmap

Status against the V0 build order (spec §53), plus where the project
actually went: live mode (originally Phase 7) was pulled forward once
image-to-video latency (~4s/scene) made real-time branching possible —
see [docs/realtime-optimization.md](docs/realtime-optimization.md).

- [x] **§52 spike (go/no-go)** — 4 synchronized worlds read as one event ✓
- [x] **Phase 0 — visual proof**: seed, four renders, 1→4 grid.
- [x] **Phase 1 — cinematic proof** *(via the live path)*: recursive
      fracture, dive-and-recurse, recorded launch films with audio.
- [~] **Phase 2 — repo**: seed CLI, schemas, UniverseTree, persistent
      runs, exports ✓; `generate`/`branch`/`export` CLI verbs still
      stubs (the live pipeline covers their use cases via scripts).
- [~] **Phase 3 — web UI**: live player with fracture/dive/click/audio ✓;
      upload-your-video web flow not built.
- [~] **Phase 4 — agent native**: `doctor --json`, `seed --json`,
      RUN_WITH_AGENT.md, cost gates ✓; JSON verbs for the live engine
      pending.
- [ ] **Phase 5 — distribution loop**: participate-mode export,
      branch-the-winner posting flow, share captions.
- [~] **Phase 6 — additional renderers**: `h3-local` (vLLM-Omni FL2VA)
      adapter written, unvalidated against a live deployment.
- [x] **Phase 7 — live mode** *(pulled forward)*: storyboard-ahead
      planning, concurrent I2V lane, dive cycles, click-to-dive,
      identity refresh, RTMP playout client.

## Next

1. Rights-clean original-seed hero film + the spec §51 X thread.
2. JSON control surface for the live engine (`multiverse live ... --json`).
3. Participate mode (numbered 16-grid + reply-to-vote → dive).
4. Fast planner as default (Gemini/Anthropic API backends exist; CLI
   fallback is the slow path).
5. Validate `h3-local` against a real vLLM-Omni deployment.
