from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.router import router
from app.store import lifespan

app = FastAPI(
    title="FastAPI async tasks",
    description="",
    lifespan=lifespan,
)
app.include_router(router)

Instrumentator().instrument(app).expose(app)
