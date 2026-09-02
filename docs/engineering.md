# Engineering practices: the live generation pipeline

How distributed-systems and async-orchestration practice maps onto a
single-process asyncio engine driving a remote render farm (fal). The
patterns below are all implemented; file references are current.

## Concurrency model

- **Bounded worker pool with priorities** (`realtime/scheduler.py`):
  a semaphore caps in-flight renders at the fal account's concurrency
  limit; a priority queue orders work (live lane before the low-priority
  identity-refresh lane). Bounding at the choke point is the
  backpressure mechanism — producers (the beat tree) are finite per
  cycle, so no unbounded queues exist.
- **Supervision, not structured cancellation**: children of a fracture
  are awaited with `gather`, and each child *contains* its own failures
  (FAILED status, retry, abandonment) rather than cancelling siblings —
  in this domain a failed universe must never kill its siblings. This is
  a deliberate inversion of `TaskGroup` semantics; the escalation path
  is explicit instead (circuit breaker below).
- **Task lifecycle hygiene**: the pool holds strong references to
  spawned tasks (the event loop only keeps weak ones) and guards
  `set_result`/`set_exception` against cancelled futures.
- **Blocking work off the loop**: every ffmpeg/ffprobe/upload/LLM call
  runs via `asyncio.to_thread`; the event loop only schedules.

## Failure handling

- **Deadlines everywhere a remote can wedge**: every render is wrapped in
  `asyncio.wait_for` (`RENDER_DEADLINE`) — a hung provider request
  becomes FAILED, never a stalled stream.
- **Retries with jittered backoff, once** (`RENDER_RETRIES`): transient
  provider errors get one spaced retry; persistent ones fail fast into
  the degraded path (player fractures into the ready subset; autopilot
  falls back to a surviving leaf).
- **Circuit breaker** (`MAX_CONSECUTIVE_FAILURES`): consecutive render
  failures abort the stream with state checkpointed — a broken provider
  can't silently burn the account (this doubles as the cost governor's
  failure half; spec §37).
- **Error containment by stage**: planning/anchoring failures abandon a
  subtree; storyboard-ahead failures fall back to replanning; the lock
  flap retries inside the renderer adapter. Each stage degrades to the
  next-cheaper behavior instead of propagating.

## State and durability

- **Journal + checkpoint**: `tree.json` is the durable state,
  `manifest.json` the read-optimized projection, `events.jsonl` the
  append-only telemetry. All are written atomically (`tmp` +
  `os.replace`) because three processes read them concurrently.
- **Idempotent, resumable work**: a render already on disk is reused,
  never re-billed; `multiverse live --run-dir` / `multiverse branch`
  resume any run from its journal (crash recovery = the branch feature).
- **Immutable-ish artifacts**: downloads land via temp files and
  renames, so a consumer mid-playback never observes truncation.

## Operations

- **Graceful drain**: SIGINT stops new submissions, lets in-flight
  renders finish, checkpoints, exits; a second SIGINT force-kills.
- **Observability**: `events.jsonl` carries structured
  cycle/render/dive/failure events with timings; the player's status
  panel is a live view over the manifest.
- **Session affinity**: the fal `hint` keeps a stream on warm runners;
  the low-priority lane uses server-side priority so refreshes can never
  delay the live lane.

## References

- [AsyncIO at scale: backpressure, structured concurrency, cancellation](https://www.kherashanu.com/blogs/2020-asyncio-at-scale-backpressure-structured-concurrency-cancellation)
- [Async pipeline backpressure](https://codesignal.com/learn/courses/capstone-a-mini-etl-with-validation/lessons/async-pipeline-backpressure)
- [asyncio queues for AI task orchestration](https://dasroot.net/posts/2026/02/using-asyncio-queues-ai-task-orchestration/)
- [Container-enabled asyncio for AI workflows](https://www.union.ai/blog-post/container-enabled-asyncio-is-all-you-need-to-build-pythonic-ai-workflows-at-scale)
