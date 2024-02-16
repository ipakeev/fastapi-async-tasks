from app.worker.base import AbstractTaskAccessor
from app.worker.enums import TaskWorkerEnum


class BackgroundTaskAccessor(AbstractTaskAccessor):
    KEY = TaskWorkerEnum.background.value

    async def incr_io_bound(self, value: int = 1) -> None:
        await self.store.core.incr_io_bound(self.KEY, value)

    async def incr_io_bound_in_thread_pool(self, value: int = 1) -> None:
        await self.store.core.incr_io_bound_in_thread_pool(self.KEY, value)

    async def incr_cpu_bound(self, value: int = 1) -> None:
        await self.store.core.incr_cpu_bound(self.KEY, value)

    async def incr_cpu_bound_in_process_pool(self, value: int = 1) -> None:
        await self.store.core.incr_cpu_bound_in_process_pool(self.KEY, value)
