from app.common.enums import TaskWorkerEnum
from app.worker.async_celery.tasks import (
    incr_cpu_bound,
    incr_cpu_bound_in_process_pool,
    incr_io_bound,
    incr_io_bound_in_thread_pool,
)
from app.worker.base import AbstractTaskAccessor


class AsyncCeleryTaskAccessor(AbstractTaskAccessor):
    KEY = TaskWorkerEnum.async_celery.value

    async def incr_io_bound(self, value: int = 1) -> None:
        await incr_io_bound.apply_async((self.KEY,), {"value": value})

    async def incr_io_bound_in_thread_pool(self, value: int = 1) -> None:
        await incr_io_bound_in_thread_pool.apply_async((self.KEY,), {"value": value})

    async def incr_cpu_bound(self, value: int = 1) -> None:
        await incr_cpu_bound.apply_async((self.KEY,), {"value": value})

    async def incr_cpu_bound_in_process_pool(self, value: int = 1) -> None:
        """
        Worker raises
        AssertionError: daemonic processes are not allowed to have children
        """
        await incr_cpu_bound_in_process_pool.apply_async((self.KEY,), {"value": value})
