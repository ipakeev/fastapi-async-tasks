from fastapi import APIRouter

from app.api.v1.router import router as router_v1

router = APIRouter(prefix="/api")
router.include_router(router_v1, prefix="/v1")
