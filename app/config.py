from pydantic import RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    REDIS_DSN: RedisDsn = "redis://"
    FASTAPI_WORKERS: int = 3

    ARQ_EXPORTER_PORT: int = 8001
    ARQ_CONCURRENCY: int = 3

    SAQ_EXPORTER_PORT: int = 8002
    SAQ_DASHBOARD_PORT: int = 8082
    SAQ_CONCURRENCY: int = 3

    FASTSTREAM_EXPORTER_PORTS: list[int] = [8003]
    FASTSTREAM_CONCURRENCY: int = 1

    ASYNC_CELERY_CONCURRENCY: int = 3


settings = Settings()
