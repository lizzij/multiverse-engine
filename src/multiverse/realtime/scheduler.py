"""Render pool: fal concurrency slots with priority ordering.

Slot policy (docs/realtime-branching.md §4): total concurrency C (10 for
the current fal account). Blocking renderer calls run in threads; a
semaphore caps in-flight renders. Lower priority number = sooner.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass(order=True)
class _Job:
    priority: int
    seq: int
    fn: Callable[[], Any] = field(compare=False)
    future: asyncio.Future = field(compare=False)


class RenderPool:
    def __init__(self, concurrency: int = 10):
        self._sem = asyncio.Semaphore(concurrency)
        self._queue: asyncio.PriorityQueue[_Job] = asyncio.PriorityQueue()
        self._seq = 0
        self._runner: asyncio.Task | None = None
        self.completed = 0
        self.failed = 0

    async def run(self, fn: Callable[[], Any], priority: int = 0) -> Any:
        """Schedule `fn` (blocking) at `priority`; await its result."""
        if self._runner is None:
            self._runner = asyncio.create_task(self._drain())
        loop = asyncio.get_running_loop()
        job = _Job(priority, self._seq, fn, loop.create_future())
        self._seq += 1
        await self._queue.put(job)
        return await job.future

    async def _drain(self) -> None:
        while True:
            job = await self._queue.get()
            await self._sem.acquire()
            asyncio.create_task(self._execute(job))

    async def _execute(self, job: _Job) -> None:
        started = time.monotonic()
        try:
            result = await asyncio.to_thread(job.fn)
            self.completed += 1
            job.future.set_result((result, time.monotonic() - started))
        except Exception as exc:
            self.failed += 1
            job.future.set_exception(exc)
        finally:
            self._sem.release()
