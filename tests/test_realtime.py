import asyncio
import subprocess
import time
from pathlib import Path

from multiverse.media import concat_crossfade, duration_seconds, freeze_safe_time
from multiverse.realtime.scheduler import RenderPool


def _synth_clip(out: Path, seconds: float, frozen_tail: float = 0.0) -> Path:
    """Test clip: moving pattern + tone; optionally a frozen still tail."""
    moving = seconds - frozen_tail
    filters = f"testsrc=size=320x180:rate=24:duration={moving}[v0]"
    if frozen_tail > 0:
        filters += (
            f";color=c=gray:size=320x180:rate=24:duration={frozen_tail}[v1];"
            "[v0][v1]concat=n=2:v=1[v]"
        )
    else:
        filters += ";[v0]null[v]"
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y",
         "-f", "lavfi", "-i", f"sine=frequency=440:duration={seconds}",
         "-filter_complex", filters, "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-c:a", "aac", str(out)],
        check=True,
    )
    return out


def test_freeze_safe_time_detects_frozen_tail(tmp_path: Path):
    frozen = _synth_clip(tmp_path / "frozen.mp4", 4.0, frozen_tail=1.0)
    clean = _synth_clip(tmp_path / "clean.mp4", 4.0)
    assert freeze_safe_time(frozen) < 3.4      # cut before the frozen second
    assert freeze_safe_time(clean) > 3.8       # clean clip: anchor at the end


def test_concat_crossfade_durations(tmp_path: Path):
    clips = [_synth_clip(tmp_path / f"c{i}.mp4", 2.0) for i in range(3)]
    out = concat_crossfade(clips, tmp_path / "out.mp4", fade=0.25)
    total = duration_seconds(out)
    assert abs(total - (6.0 - 2 * 0.25)) < 0.35


def test_h3_local_registered_but_unavailable(monkeypatch):
    from multiverse.renderers import registry

    monkeypatch.delenv("H3_LOCAL_URL", raising=False)
    assert "h3-local" in registry.available()
    assert registry.get("h3-local").is_available() is False


def test_pool_caps_concurrency():
    peak = 0
    active = 0

    def job():
        nonlocal peak, active
        active += 1
        peak = max(peak, active)
        time.sleep(0.05)
        active -= 1
        return "ok"

    async def main():
        pool = RenderPool(concurrency=3)
        results = await asyncio.gather(*(pool.run(job) for _ in range(10)))
        assert all(r[0] == "ok" for r in results)
        assert pool.completed == 10

    asyncio.run(main())
    assert peak <= 3


def test_pool_prefers_low_priority_number():
    order: list[str] = []

    def job(name):
        order.append(name)
        time.sleep(0.02)

    async def main():
        pool = RenderPool(concurrency=1)
        # occupy the single slot, then enqueue p1 before p0
        first = pool.run(lambda: job("warmup"), priority=0)
        await asyncio.sleep(0.01)
        late = [pool.run(lambda: job("p1"), priority=1), pool.run(lambda: job("p0"), priority=0)]
        await asyncio.gather(first, *late)

    asyncio.run(main())
    assert order[0] == "warmup"
    assert order.index("p0") < order.index("p1")


def test_story_path_and_leaves():
    from multiverse.compose.export import leaf_nodes, story_path

    manifest = {
        "depth": 2, "branches": 2,
        "cycles": [
            {"root": "0", "dive_to": "0.1.2"},
            {"root": "0.1.2", "dive_to": "0.1.2.2.1"},
        ],
        "nodes": {
            nid: {"status": "ready", "parent": None}
            for nid in ["0", "0.1", "0.2", "0.1.1", "0.1.2", "0.2.1", "0.2.2",
                        "0.1.2.1", "0.1.2.2", "0.1.2.1.1", "0.1.2.1.2",
                        "0.1.2.2.1", "0.1.2.2.2"]
        },
    }
    assert story_path(manifest) == ["0", "0.1", "0.1.2", "0.1.2.2", "0.1.2.2.1"]
    assert leaf_nodes(manifest, 0) == ["0.1.1", "0.1.2", "0.2.1", "0.2.2"]
    assert leaf_nodes(manifest, 1) == ["0.1.2.1.1", "0.1.2.1.2", "0.1.2.2.1", "0.1.2.2.2"]


def test_scene_summary_sidecar(tmp_path):
    from multiverse.realtime.live import DEFAULT_SCENE_SUMMARY, scene_summary_for

    seed = tmp_path / "seed.mp4"
    seed.touch()
    assert scene_summary_for(seed) == DEFAULT_SCENE_SUMMARY
    seed.with_suffix(".summary.txt").write_text("custom style\n")
    assert scene_summary_for(seed) == "custom style"


def test_pool_surfaces_failures():
    def bad():
        raise RuntimeError("boom")

    async def main():
        pool = RenderPool(concurrency=2)
        try:
            await pool.run(bad)
        except RuntimeError as exc:
            assert "boom" in str(exc)
        else:
            raise AssertionError("expected failure")
        assert pool.failed == 1

    asyncio.run(main())
