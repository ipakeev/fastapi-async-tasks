import asyncio

from prometheus_async.aio.web import start_http_server_in_thread

from app.config import settings
from app.store import Store, store_lifespan


async def main() -> None:
    start_http_server_in_thread(port=settings.SAQ_EXPORTER_PORT)

    store: Store
    async with store_lifespan() as store:
        await store.worker.saq.run(web=True, port=settings.SAQ_DASHBOARD_PORT)


if __name__ == "__main__":
    asyncio.run(main())
