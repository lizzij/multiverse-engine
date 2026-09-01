import asyncio
import time

from multiverse.realtime.scheduler import RenderPool


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
