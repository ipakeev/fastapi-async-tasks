import asyncio
import queue
import ssl
import threading
from collections.abc import Callable
from typing import Any

import faststream
from faststream.redis import RedisBroker
from prometheus_async.aio.web import start_http_server, ThreadedMetricsHTTPServer
from prometheus_async.types import ServiceDiscovery

from app.common.logger import get_logger
from app.config import settings
from app.store import connect_to_store, disconnect_from_store

logger = get_logger(__name__)


def start_http_server_in_thread(
    *,
    try_ports: list[int],
    addr: str = "",
    ssl_ctx: ssl.SSLContext | None = None,
    service_discovery: ServiceDiscovery | None = None,
) -> ThreadedMetricsHTTPServer:
    """
    Start an asyncio HTTP(S) server in a new thread with an own event loop.

    Ideal to expose your metrics in non-asyncio Python 3 applications.
    """
    q: queue.Queue = queue.Queue()
    loop = asyncio.new_event_loop()

    def server() -> None:
        asyncio.set_event_loop(loop)
        for port in try_ports:
            try:
                http = loop.run_until_complete(
                    start_http_server(
                        port=port,
                        addr=addr,
                        ssl_ctx=ssl_ctx,
                        service_discovery=service_discovery,
                    )
                )
                break
            except OSError:
                pass

        logger.info(f"FastStream exporter started on port {port}")
        q.put(http)
        loop.run_forever()
        loop.run_until_complete(http.close())

    t = threading.Thread(target=server, name="FastStreamExporter", daemon=True)
    t.start()

    return ThreadedMetricsHTTPServer(q.get(), t, loop)


class FastStream(faststream.FastStream):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.tasks: dict[str, Callable[..., Any]] = {}

        self.on_startup(self.connect)
        self.on_shutdown(self.disconnect)

    async def connect(self, *_: Any, **__: Any) -> None:
        await connect_to_store()

        await self.broker.connect(url=settings.REDIS_DSN.__str__())

    async def disconnect(self, *_: Any, **__: Any) -> None:
        await disconnect_from_store()

        await self.broker.close()

    async def run(self, *args: Any, **kwargs: Any) -> None:
        # bind metrics exporters
        start_http_server_in_thread(try_ports=settings.FASTSTREAM_EXPORTER_PORTS)

        await super().run(*args, **kwargs)

    def task(self, func: Callable) -> Callable:
        task = self.broker.subscriber(func.__name__)(func)
        self.tasks[func.__name__] = task
        return task

    def get(self, channel: str) -> Callable[..., Any]:
        return self.tasks[channel]


faststream_broker = RedisBroker()
faststream_app = FastStream(faststream_broker)
