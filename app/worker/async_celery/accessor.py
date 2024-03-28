from app.common.enums import TaskWorkerEnum
from app.worker.async_celery.tasks import (
    incr_cpu_bound,
    incr_cpu_bound_in_process_pool,
    incr_io_bound,
    incr_io_bound_in_thread_pool,
    sync_incr_io_bound,
)
from app.worker.base import AbstractTaskAccessor


class AsyncCeleryTaskAccessor(AbstractTaskAccessor):
    KEY = TaskWorkerEnum.async_celery.value

    async def incr_io_bound(self, value: int = 1) -> None:
        incr_io_bound.delay(self.KEY, value=value)

    async def sync_incr_io_bound(self, value: int = 1) -> None:
        sync_incr_io_bound.delay(self.KEY, value=value)

    async def incr_io_bound_in_thread_pool(self, value: int = 1) -> None:
        incr_io_bound_in_thread_pool.delay(self.KEY, value=value)

    async def incr_cpu_bound(self, value: int = 1) -> None:
        incr_cpu_bound.delay(self.KEY, value=value)

    async def incr_cpu_bound_in_process_pool(self, value: int = 1) -> None:
        """
        Worker raises
        AssertionError: daemonic processes are not allowed to have children
        """
        incr_cpu_bound_in_process_pool.delay(self.KEY, value=value)
