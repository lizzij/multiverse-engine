# Roadmap

Status against the V0 build order (spec §53), plus where the project
actually went: live mode (originally Phase 7) was pulled forward once
image-to-video latency (~4s/scene) made real-time branching possible —
see [docs/realtime-optimization.md](docs/realtime-optimization.md).

- [x] **§52 spike (go/no-go)** — 4 synchronized worlds read as one event.
- [x] **Phase 0 — visual proof**: seed, four renders, 1→4 grid.
- [x] **Phase 1 — cinematic proof** *(via the live path)*: recursive
      fracture, dive-and-recurse, recorded launch films with audio,
      13s square hero cuts (`record_launch.py --hero`).
- [x] **Phase 2 — repo**: seed CLI, schemas, UniverseTree, persistent
      resumable runs, exports (`multiverse export`).
- [~] **Phase 3 — web UI**: live player with fracture/dive/click/audio
      and a status panel ✓; an upload-your-video web flow is the one
      remaining piece (the CLI covers it today).
- [x] **Phase 4 — agent native**: every command has `--json`
      (doctor/seed/live/generate/branch/status/inspect/export),
      RUN_WITH_AGENT.md, cost gates, circuit breaker.
- [x] **Phase 5 — distribution loop**: participate export (numbered
      grid + end card + captions), branch-the-winner
      (`multiverse branch RUN --node N`), launch thread
      ([docs/launch-thread.md](docs/launch-thread.md)), reproducible
      examples incl. the rights-clean `seed-tinkers`.
- [~] **Phase 6 — additional renderers**: `h3-local` (vLLM-Omni FL2VA)
      adapter written and registered; validation blocked on access to a
      live vLLM-Omni deployment (needs a ≥RTX 3060-class GPU host).
- [x] **Phase 7 — live mode** *(pulled forward)*: storyboard-ahead
      planning, concurrent I2V lane with retry/deadline/breaker,
      dive cycles, click-to-dive, identity refresh, RTMP playout,
      checkpoint/resume, events.jsonl telemetry.

## Later

- Web upload flow (Phase 3 completion).
- Validate `h3-local` on a real vLLM-Omni deployment.
- Vote-driven dives on the RTMP path (chat → control channel).
- Dollar-denominated cost governor (the failure half — the circuit
  breaker — is in; the spend-rate half needs fal pricing telemetry).
