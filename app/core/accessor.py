import asyncio
import random
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

from app.common.metrics import export_task_metrics
from app.store import BaseAccessor, Store


class CoreAccessor(BaseAccessor):
    THREAD_COUNT = 3
    PROCESS_COUNT = 3

    def __init__(self, store: Store) -> None:
        super().__init__(store)

        self._loop = asyncio.get_event_loop()
        self._thread_executor = ThreadPoolExecutor(max_workers=self.THREAD_COUNT)
        self._process_executor = ProcessPoolExecutor(max_workers=self.PROCESS_COUNT)

    async def disconnect(self) -> None:
        self._thread_executor.shutdown(wait=True)
        self._process_executor.shutdown(wait=True)

    @staticmethod
    def heavy_calculations(count: int = 1_000_000) -> None:
        for i in range(count):
            _ = i % random.randint(1, 100)

    @staticmethod
    async def async_calculations(count: int = 1_000_000) -> None:
        for i in range(count):
            _ = i % random.randint(1, 100)
            await asyncio.sleep(0.0)

    @export_task_metrics
    async def incr_io_bound(self, key: str, value: int = 1) -> int:
        await asyncio.sleep(0.1)
        return await self.store.redis.client.incr(key, value)

    @export_task_metrics
    async def incr_io_bound_in_thread_pool(self, key: str, value: int = 1) -> int:
        def func() -> int:
            time.sleep(0.1)
            return self.store.redis.sync_client.incr(key, value)

        return await self._loop.run_in_executor(self._thread_executor, func)

    @export_task_metrics
    async def incr_cpu_bound(self, key: str, value: int = 1) -> int:
        self.heavy_calculations()
        return await self.store.redis.client.incr(key, value)

    @export_task_metrics
    async def incr_cpu_bound_in_process_pool(self, key: str, value: int = 1) -> int:
        await self._loop.run_in_executor(
            self._process_executor, self.heavy_calculations
        )
        return await self.store.redis.client.incr(key, value)
