from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.utils.logger import get_logger


class BaseAccessor:
    def __init__(self, store: "Store") -> None:
        self.store = store
        self.config = settings
        self.logger = get_logger(self.__class__.__name__)

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass


class Store:
    def __init__(self) -> None:
        from app.core.accessor import CoreAccessor
        from app.redis.accessor import RedisAccessor
        from app.worker.accessor import WorkerAccessor

        self.core = CoreAccessor(self)
        self.redis = RedisAccessor(self)
        self.worker = WorkerAccessor(self)

        self.logger = get_logger("store")

    async def connect(self) -> None:
        self.logger.info("Connecting to Store")
        await self.redis.connect()
        await self.worker.connect()
        await self.core.connect()
        self.logger.info("Connected to Store")

    async def disconnect(self) -> None:
        self.logger.info("Disconnecting from Store")
        await self.core.disconnect()
        await self.worker.disconnect()
        await self.redis.disconnect()
        self.logger.info("Disconnected from Store")


_store: Store | None = None


def get_store() -> Store:
    assert _store, "Store is not initialized"
    return _store


async def connect_to_store() -> Store:
    global _store

    if not _store:
        _store = Store()
        await _store.connect()

    return _store


async def disconnect_from_store() -> None:
    global _store

    if _store:
        await _store.disconnect()
        _store = None


@asynccontextmanager
async def store_lifespan() -> AsyncGenerator[Store, None]:
    await connect_to_store()
    try:
        yield get_store()
    finally:
        await disconnect_from_store()


@asynccontextmanager
async def lifespan(*_: FastAPI) -> AsyncGenerator[None, None]:
    async with store_lifespan():
        yield
