from fastapi import APIRouter
from starlette.responses import JSONResponse

from app.api.deps import StoreDep
from app.api.schemas import IncrInputSchema
from app.common.enums import TaskWorkerEnum

router = APIRouter(tags=["io"])


@router.post("/simple/{worker}")
async def simple(
    worker: TaskWorkerEnum, body: IncrInputSchema, store: StoreDep
) -> JSONResponse:
    task = await store.worker.incr_io_bound(worker, body.value)
    return JSONResponse({"status": "ok", "message": "io-simple"}, background=task)


@router.post("/thread/{worker}")
async def in_thread_pool(
    worker: TaskWorkerEnum, body: IncrInputSchema, store: StoreDep
) -> JSONResponse:
    task = await store.worker.incr_io_bound_in_thread_pool(worker, body.value)
    return JSONResponse({"status": "ok", "message": "io-thread"}, background=task)
