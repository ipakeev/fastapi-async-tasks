import pytest
from httpx import AsyncClient

from app.store import Store
from app.worker.enums import TaskWorkerEnum


@pytest.mark.parametrize(
    "worker, path",
    [
        (TaskWorkerEnum.background, "simple"),
        (TaskWorkerEnum.background, "process"),
        (TaskWorkerEnum.arq, "simple"),
        (TaskWorkerEnum.arq, "process"),
        (TaskWorkerEnum.saq, "simple"),
        (TaskWorkerEnum.saq, "process"),
        (TaskWorkerEnum.async_celery, "simple"),
        (TaskWorkerEnum.async_celery, "process"),
        (TaskWorkerEnum.faststream, "simple"),
        (TaskWorkerEnum.faststream, "process"),
    ],
)
async def test_cpu_bound(
    store: Store,
    cli: AsyncClient,
    worker: TaskWorkerEnum,
    path: str,
) -> None:
    assert await store.redis.client.get(path) is None

    resp = await cli.post(
        f"/api/v1/incr/cpu/{path}/{worker.value}",
        json={"value": 5},
    )
    assert resp.status_code == 200

    assert await store.redis.client.get(worker.value) == b"5"
