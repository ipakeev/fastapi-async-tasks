from typing import Annotated

from fastapi import APIRouter, Body
from starlette.responses import JSONResponse

from app.api.deps import StoreDep
from app.api.schemas import IncrInputSchema
from app.worker.enums import TaskWorkerEnum

router = APIRouter(tags=["cpu"])


@router.post("/simple/{worker}")
async def simple(
    worker: TaskWorkerEnum, body: Annotated[IncrInputSchema, Body()], store: StoreDep
) -> JSONResponse:
    task = await store.worker.incr_cpu_bound(worker, body.value)
    return JSONResponse({"status": "ok", "message": "cpu-simple"}, background=task)


@router.post("/process/{worker}")
async def in_process_pool(
    worker: TaskWorkerEnum, body: Annotated[IncrInputSchema, Body()], store: StoreDep
) -> JSONResponse:
    task = await store.worker.incr_cpu_bound_in_process_pool(worker, body.value)
    return JSONResponse({"status": "ok", "message": "cpu-process"}, background=task)
