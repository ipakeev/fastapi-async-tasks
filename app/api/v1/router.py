from fastapi import APIRouter

from app.api.v1.endpoints.incr import cpu_bound, io_bound

router = APIRouter()
router.include_router(io_bound.router, prefix="/incr/io")
router.include_router(cpu_bound.router, prefix="/incr/cpu")
