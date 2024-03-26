import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from celery import Celery, signals

from app.config import settings
from app.store import connect_to_store, disconnect_from_store

T = TypeVar("T")


class AsyncCelery(Celery):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.functions: dict[str, Callable[..., Any]] = {}
        self.loop = asyncio.get_event_loop()

    def connect(self, *_: Any, **__: Any) -> None:
        self.loop.run_until_complete(connect_to_store())

    def disconnect(self, *_: Any, **__: Any) -> None:
        self.loop.run_until_complete(disconnect_from_store())

    def task(
        self,
        task: Callable[..., T] | None = None,
        **opts: Any,
    ) -> Callable:
        create_task = super().task

        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @create_task(**opts)
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> T:
                return self.loop.run_until_complete(func(*args, **kwargs))

            self.functions[wrapper.name] = func

            return wrapper

        if task:
            return decorator(task)

        return decorator


async_celery_app = AsyncCelery("async_celery", broker=settings.REDIS_DSN.__str__())
async_celery_app.autodiscover_tasks(packages=["app.worker.async_celery.tasks"])
async_celery_app.conf.timezone = "UTC"
async_celery_app.conf.worker_proc_alive_timeout = 30

signals.worker_process_init.connect(async_celery_app.connect)
signals.worker_process_shutdown.connect(async_celery_app.disconnect)
