from app.store import Store


async def incr_io_bound(ctx: dict, key: str, value: int = 1) -> int:
    store: Store = ctx["store"]
    return await store.core.incr_io_bound(key, value)


async def incr_io_bound_in_thread_pool(ctx: dict, key: str, value: int = 1) -> int:
    store: Store = ctx["store"]
    return await store.core.incr_io_bound_in_thread_pool(key, value)


async def incr_cpu_bound(ctx: dict, key: str, value: int = 1) -> int:
    store: Store = ctx["store"]
    return await store.core.incr_cpu_bound(key, value)


async def incr_cpu_bound_in_process_pool(ctx: dict, key: str, value: int = 1) -> int:
    store: Store = ctx["store"]
    return await store.core.incr_cpu_bound_in_process_pool(key, value)
