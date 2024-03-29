import asyncio
import time
from collections.abc import AsyncGenerator, Callable, Generator
from contextlib import ExitStack
from typing import Any
from unittest.mock import AsyncMock, patch

import nest_asyncio
import pytest
from fakeredis import FakeRedis
from fakeredis.aioredis import FakeRedis as AsyncFakeRedis
from fastapi import FastAPI
from httpx import AsyncClient

from app import main
from app.redis.accessor import RedisAccessor
from app.store import get_store, lifespan, Store
from app.worker.async_celery.app import async_celery_app
from app.worker.faststream.app import faststream_app, faststream_broker

nest_asyncio.apply()


@pytest.fixture(scope="session", autouse=True)
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def sleep_mock() -> Generator[None, None, None]:
    with (
        patch.object(asyncio, "sleep"),
        patch.object(time, "sleep"),
    ):
        yield


@pytest.fixture(scope="session")
def redis_mock() -> Generator[None, None, None]:
    with (
        patch.object(RedisAccessor, "client_class", AsyncFakeRedis),
        patch.object(RedisAccessor, "sync_client_class", FakeRedis),
        patch("faststream.redis.broker.Redis", AsyncFakeRedis),
    ):
        yield


@pytest.fixture(scope="session", autouse=True)
async def app(redis_mock: None) -> AsyncGenerator[FastAPI, None]:
    async with lifespan(main.app):
        yield main.app


@pytest.fixture(scope="session")
def store(app: FastAPI) -> Store:
    return get_store()


@pytest.fixture
async def cli(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(autouse=True)
async def clear_redis(store: Store) -> AsyncGenerator[None, None]:
    yield

    await store.redis.client.flushall()


@pytest.fixture(scope="session", autouse=True)
def arq_eager_execution(store: Store) -> Generator[AsyncMock, None, None]:
    ctx = {"store": store}
    task_map = {f.__name__: f for f in store.worker.arq.tasks}

    async def resolver(task_name: str, *args: Any, **kwargs: Any) -> Any:
        func = task_map[task_name]
        return await func(ctx, *args, **kwargs)

    with patch.object(
        store.worker.arq._job_pool,
        "enqueue_job",
        side_effect=resolver,
    ) as mock:
        yield mock


@pytest.fixture(scope="session", autouse=True)
def saq_eager_execution(store: Store) -> Generator[AsyncMock, None, None]:
    ctx = {"store": store}
    task_map = {f.__name__: f for f in store.worker.saq.tasks}

    async def resolver(task_name: str, kwargs: Any) -> Any:
        func = task_map[task_name]
        return await func(ctx, **kwargs)

    with patch.object(
        store.worker.saq._queue,
        "enqueue",
        side_effect=resolver,
    ) as mock:
        yield mock


@pytest.fixture(scope="session", autouse=True)
def async_celery_eager_execution(store: Store) -> Generator[None, None, None]:
    # register tasks in celery app
    from app.worker.async_celery import tasks  # noqa: F401

    def execute_task(name: str) -> Callable[..., Any]:
        func = async_celery_app.functions[name]

        def wrapper(args: Any, kwargs: Any) -> Any:
            return asyncio.get_running_loop().run_until_complete(func(*args, **kwargs))

        return wrapper

    patches = [
        patch.object(task, "apply_async", side_effect=execute_task(name))
        for name, task in async_celery_app.tasks.items()
    ]

    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        yield


@pytest.fixture(scope="session", autouse=True)
def faststream_eager_execution(store: Store) -> Generator[AsyncMock, None, None]:
    # register tasks in faststream app
    from app.worker.faststream import tasks  # noqa: F401

    async def resolver(message: dict, channel: str) -> Any:
        func = faststream_app.get(channel)
        return await func(**message)

    with patch.object(
        faststream_broker,
        "publish",
        side_effect=resolver,
    ) as mock:
        yield mock
