import asyncio
from collections.abc import Callable
from typing import Any

import saq
from aiohttp.web_runner import AppRunner, TCPSite
from saq.web.aiohttp import create_app

from app.worker.base import AbstractTaskAccessor
from app.worker.enums import TaskWorkerEnum
from app.worker.saq.tasks import (
    incr_cpu_bound,
    incr_cpu_bound_in_process_pool,
    incr_io_bound,
    incr_io_bound_in_thread_pool,
)


class SaqTaskAccessor(AbstractTaskAccessor):
    KEY = TaskWorkerEnum.saq.value

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._queue: saq.Queue | None = None

    async def connect(self) -> None:
        client = self.store.redis.client_class.from_url(self.config.REDIS_DSN.__str__())
        self._queue = saq.Queue(client)

    async def disconnect(self) -> None:
        if self._queue:
            await self._queue.disconnect()

    @property
    def tasks(self) -> list[Callable]:
        return [
            incr_io_bound,
            incr_io_bound_in_thread_pool,
            incr_cpu_bound,
            incr_cpu_bound_in_process_pool,
        ]

    async def run(self, web: bool = False, port: int = 8090) -> None:
        async def on_worker_startup(ctx: dict) -> None:
            ctx["store"] = self.store

        worker = saq.Worker(
            self._queue,
            functions=self.tasks,
            startup=on_worker_startup,
            concurrency=self.config.SAQ_CONCURRENCY,
        )

        if web:
            app = create_app([self._queue])
            task = asyncio.create_task(worker.start())

            try:
                runner = AppRunner(app)
                await runner.setup()
                site = TCPSite(runner, port=port)
                await site.start()

                await asyncio.Event().wait()
            finally:
                await worker.stop()
                task.cancel()
        else:
            await worker.start()

    async def incr_io_bound(self, value: int = 1) -> None:
        await self._queue.enqueue(
            incr_io_bound.__name__, kwargs={"key": self.KEY, "value": value}
        )

    async def incr_io_bound_in_thread_pool(self, value: int = 1) -> None:
        await self._queue.enqueue(
            incr_io_bound_in_thread_pool.__name__,
            kwargs={"key": self.KEY, "value": value},
        )

    async def incr_cpu_bound(self, value: int = 1) -> None:
        await self._queue.enqueue(
            incr_cpu_bound.__name__, kwargs={"key": self.KEY, "value": value}
        )

    async def incr_cpu_bound_in_process_pool(self, value: int = 1) -> None:
        await self._queue.enqueue(
            incr_cpu_bound_in_process_pool.__name__,
            kwargs={"key": self.KEY, "value": value},
        )
