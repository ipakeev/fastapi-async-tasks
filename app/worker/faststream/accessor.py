from app.common.enums import TaskWorkerEnum
from app.worker.base import AbstractTaskAccessor
from app.worker.faststream.app import faststream_broker


class FastStreamTaskAccessor(AbstractTaskAccessor):
    KEY = TaskWorkerEnum.faststream.value

    async def connect(self) -> None:
        await faststream_broker.connect(url=self.config.REDIS_DSN.__str__())

    async def disconnect(self) -> None:
        await faststream_broker.close()

    async def incr_io_bound(self, value: int = 1) -> None:
        await faststream_broker.publish(
            message={"key": self.KEY, "value": value},
            channel="incr_io_bound",
        )

    async def sync_incr_io_bound(self, value: int = 1) -> None:
        await faststream_broker.publish(
            message={"key": self.KEY, "value": value},
            channel="sync_incr_io_bound",
        )

    async def incr_io_bound_in_thread_pool(self, value: int = 1) -> None:
        await faststream_broker.publish(
            message={"key": self.KEY, "value": value},
            channel="incr_io_bound_in_thread_pool",
        )

    async def incr_cpu_bound(self, value: int = 1) -> None:
        await faststream_broker.publish(
            message={"key": self.KEY, "value": value},
            channel="incr_cpu_bound",
        )

    async def incr_cpu_bound_in_process_pool(self, value: int = 1) -> None:
        await faststream_broker.publish(
            message={"key": self.KEY, "value": value},
            channel="incr_cpu_bound_in_process_pool",
        )
