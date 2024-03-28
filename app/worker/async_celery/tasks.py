from app.store import get_store
from app.worker.async_celery.app import async_celery_app


@async_celery_app.task
async def incr_io_bound(key: str, value: int = 1) -> int:
    store = get_store()
    return await store.core.incr_io_bound(key, value)


@async_celery_app.task
async def sync_incr_io_bound(key: str, value: int = 1) -> int:
    store = get_store()
    return await store.core.sync_incr_io_bound(key, value)


@async_celery_app.task
async def incr_io_bound_in_thread_pool(key: str, value: int = 1) -> int:
    store = get_store()
    return await store.core.incr_io_bound_in_thread_pool(key, value)


@async_celery_app.task
async def incr_cpu_bound(key: str, value: int = 1) -> int:
    store = get_store()
    return await store.core.incr_cpu_bound(key, value)


@async_celery_app.task
async def incr_cpu_bound_in_process_pool(key: str, value: int = 1) -> int:
    store = get_store()
    return await store.core.incr_cpu_bound_in_process_pool(key, value)
