# Experiments

Development spikes and probes, kept for the record. These proved the
architecture and produced the measurements in
[docs/realtime-optimization.md](../docs/realtime-optimization.md);
they are not part of the user-facing pipeline.

| script | what it proved |
|---|---|
| `spike52.py` | spec §52 go/no-go: 4 reference-to-video worlds in a synchronized 2×2 grid read as one event |
| `r1_chain.py` | dual-anchor story continuation survives chained generations (seed → child → grandchild) |
| `r2_autopilot.py` | concurrent rendering + first-ready-wins path commitment |
| `probe_latency.py` | reference-to-video end-to-end latency (~31–52s; reference tokenization dominates) |
| `probe_i2v.py` | image-to-video keyframe latency (~4s at 480p — the real-time unlock) |

They may bit-rot as the main modules evolve; run them with a grain of
salt.
