from abc import abstractmethod
from typing import Any

from starlette.background import BackgroundTask

from app.store import BaseAccessor


class AbstractTaskAccessor(BaseAccessor):
    @abstractmethod
    async def incr_io_bound(self, *args: Any, **kwargs: Any) -> BackgroundTask | None:
        raise NotImplementedError

    @abstractmethod
    async def incr_io_bound_in_thread_pool(
        self, *args: Any, **kwargs: Any
    ) -> BackgroundTask | None:
        raise NotImplementedError

    @abstractmethod
    async def incr_cpu_bound(self, *args: Any, **kwargs: Any) -> BackgroundTask | None:
        raise NotImplementedError

    @abstractmethod
    async def incr_cpu_bound_in_process_pool(
        self, *args: Any, **kwargs: Any
    ) -> BackgroundTask | None:
        raise NotImplementedError
