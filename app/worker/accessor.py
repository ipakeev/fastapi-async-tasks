from starlette.background import BackgroundTask

from app.common.enums import TaskWorkerEnum
from app.store import Store
from app.worker.arq.accessor import ArqTaskAccessor
from app.worker.async_celery.accessor import AsyncCeleryTaskAccessor
from app.worker.background.accessor import BackgroundTaskAccessor
from app.worker.base import AbstractTaskAccessor
from app.worker.faststream.accessor import FastStreamTaskAccessor
from app.worker.saq.accessor import SaqTaskAccessor


class WorkerAccessor(AbstractTaskAccessor):
    def __init__(self, store: Store) -> None:
        super().__init__(store)

        self.background = BackgroundTaskAccessor(store)
        self.arq = ArqTaskAccessor(store)
        self.saq = SaqTaskAccessor(store)
        self.async_celery = AsyncCeleryTaskAccessor(store)
        self.faststream = FastStreamTaskAccessor(store)

    async def connect(self) -> None:
        self.logger.info("Connecting to workers")
        await self.background.connect()
        await self.arq.connect()
        await self.saq.connect()
        await self.async_celery.connect()
        await self.faststream.connect()
        self.logger.info("Connected to workers")

    async def disconnect(self) -> None:
        self.logger.info("Disconnecting from workers")
        await self.background.disconnect()
        await self.arq.disconnect()
        await self.saq.disconnect()
        await self.async_celery.disconnect()
        await self.faststream.disconnect()
        self.logger.info("Disconnected from workers")

    def _get_task_accessor(self, worker: TaskWorkerEnum) -> AbstractTaskAccessor:
        match worker:
            case TaskWorkerEnum.background:
                return self.background
            case TaskWorkerEnum.arq:
                return self.arq
            case TaskWorkerEnum.saq:
                return self.saq
            case TaskWorkerEnum.async_celery:
                return self.async_celery
            case TaskWorkerEnum.faststream:
                return self.faststream
            case _:
                raise NotImplementedError

    async def _dummy_work(self) -> None:
        await self.store.core.async_calculations(count=100)

    async def incr_io_bound(self, worker: TaskWorkerEnum, value: int) -> BackgroundTask:
        await self._dummy_work()
        accessor = self._get_task_accessor(worker)
        return BackgroundTask(accessor.incr_io_bound, value=value)

    async def incr_io_bound_in_thread_pool(
        self, worker: TaskWorkerEnum, value: int
    ) -> BackgroundTask:
        await self._dummy_work()
        accessor = self._get_task_accessor(worker)
        return BackgroundTask(accessor.incr_io_bound_in_thread_pool, value=value)

    async def incr_cpu_bound(
        self, worker: TaskWorkerEnum, value: int
    ) -> BackgroundTask:
        await self._dummy_work()
        accessor = self._get_task_accessor(worker)
        return BackgroundTask(accessor.incr_cpu_bound, value=value)

    async def incr_cpu_bound_in_process_pool(
        self, worker: TaskWorkerEnum, value: int
    ) -> BackgroundTask:
        await self._dummy_work()
        accessor = self._get_task_accessor(worker)
        return BackgroundTask(accessor.incr_cpu_bound_in_process_pool, value=value)
