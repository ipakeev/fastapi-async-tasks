import asyncio
from typing import Any

from redis import Redis
from redis.asyncio import Redis as AsyncRedis

from app.store import BaseAccessor


class RedisAccessor(BaseAccessor):
    CONNECT_MAX_TRIES = 5

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.sync_client: Redis | None = None
        self.client: AsyncRedis | None = None

    @property
    def client_class(self) -> type[AsyncRedis]:
        return AsyncRedis

    @property
    def sync_client_class(self) -> type[Redis]:
        return Redis

    async def connect(self) -> None:
        await self._connect_async_redis()
        self._connect_sync_redis()

        # !!! clear redis before stress testing
        await self.client.flushall()

    async def _connect_async_redis(self) -> None:
        self.client = self.client_class.from_url(self.config.REDIS_DSN.__str__())

        tries_count = 0
        while True:
            tries_count += 1
            try:
                await self.client.ping()
                break
            except Exception as exc:
                self.logger.warning(f"Can't connect to AsyncRedis: {str(exc)}")

            if tries_count > self.CONNECT_MAX_TRIES:
                raise Exception("Can't connect to AsyncRedis")
            await asyncio.sleep(1)

    def _connect_sync_redis(self) -> None:
        self.sync_client = self.sync_client_class.from_url(
            self.config.REDIS_DSN.__str__()
        )

        tries_count = 0
        while True:
            tries_count += 1
            try:
                self.sync_client.ping()
                break
            except Exception as exc:
                self.logger.warning(f"Can't connect to SyncRedis: {str(exc)}")

            if tries_count > self.CONNECT_MAX_TRIES:
                raise Exception("Can't connect to SyncRedis")
            asyncio.sleep(1)

    async def disconnect(self) -> None:
        if self.client:
            await self.client.aclose()

        if self.sync_client:
            self.sync_client.close()
