import pytest
from httpx import AsyncClient

from app.common.enums import TaskWorkerEnum
from app.store import Store


@pytest.mark.parametrize(
    "worker, path",
    [
        (TaskWorkerEnum.background, "simple"),
        (TaskWorkerEnum.background, "sync"),
        (TaskWorkerEnum.background, "thread"),
        (TaskWorkerEnum.arq, "simple"),
        (TaskWorkerEnum.arq, "sync"),
        (TaskWorkerEnum.arq, "thread"),
        (TaskWorkerEnum.saq, "simple"),
        (TaskWorkerEnum.saq, "sync"),
        (TaskWorkerEnum.saq, "thread"),
        (TaskWorkerEnum.async_celery, "simple"),
        (TaskWorkerEnum.async_celery, "sync"),
        (TaskWorkerEnum.async_celery, "thread"),
        (TaskWorkerEnum.faststream, "simple"),
        (TaskWorkerEnum.faststream, "sync"),
        (TaskWorkerEnum.faststream, "thread"),
    ],
)
async def test_io_bound(
    store: Store,
    cli: AsyncClient,
    worker: TaskWorkerEnum,
    path: str,
) -> None:
    assert await store.redis.client.get(path) is None

    resp = await cli.post(
        f"/api/v1/incr/io/{path}/{worker.value}",
        json={"value": 5},
    )
    assert resp.status_code == 200

    assert await store.redis.client.get(worker.value) == b"5"
