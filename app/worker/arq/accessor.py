from collections.abc import Callable
from typing import Any

import arq
import arq.connections

from app.common.enums import TaskWorkerEnum
from app.worker.arq.tasks import (
    incr_cpu_bound,
    incr_cpu_bound_in_process_pool,
    incr_io_bound,
    incr_io_bound_in_thread_pool,
)
from app.worker.base import AbstractTaskAccessor


class ArqTaskAccessor(AbstractTaskAccessor):
    KEY = TaskWorkerEnum.arq.value

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self._job_pool: arq.ArqRedis | None = None

    async def connect(self) -> None:
        class JobPoolRedis(arq.ArqRedis, self.store.redis.client_class):
            pass

        arq.connections.ArqRedis = JobPoolRedis

        self._job_pool = await arq.create_pool(
            arq.connections.RedisSettings(
                host=self.config.REDIS_DSN.host,
                port=self.config.REDIS_DSN.port,
                username=self.config.REDIS_DSN.username,
                password=self.config.REDIS_DSN.password,
                database=self.config.REDIS_DSN.path.removeprefix("/"),
            )
        )

    async def disconnect(self) -> None:
        if self._job_pool:
            await self._job_pool.close()

    @property
    def tasks(self) -> list[Callable]:
        return [
            incr_io_bound,
            incr_io_bound_in_thread_pool,
            incr_cpu_bound,
            incr_cpu_bound_in_process_pool,
        ]

    async def run(self) -> None:
        async def on_startup(ctx: dict) -> None:
            ctx["store"] = self.store

        worker = arq.Worker(
            functions=self.tasks,
            on_startup=on_startup,
            max_jobs=self.config.ARQ_CONCURRENCY,
            health_check_interval=60,
            handle_signals=False,
            redis_pool=self._job_pool,
        )
        try:
            await worker.main()
        finally:
            await worker.close()

    async def incr_io_bound(self, value: int = 1) -> None:
        await self._job_pool.enqueue_job(incr_io_bound.__name__, self.KEY, value=value)

    async def incr_io_bound_in_thread_pool(self, value: int = 1) -> None:
        await self._job_pool.enqueue_job(
            incr_io_bound_in_thread_pool.__name__, self.KEY, value=value
        )

    async def incr_cpu_bound(self, value: int = 1) -> None:
        await self._job_pool.enqueue_job(incr_cpu_bound.__name__, self.KEY, value=value)

    async def incr_cpu_bound_in_process_pool(self, value: int = 1) -> None:
        await self._job_pool.enqueue_job(
            incr_cpu_bound_in_process_pool.__name__, self.KEY, value=value
        )
