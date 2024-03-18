from enum import Enum


class TaskWorkerEnum(str, Enum):
    background = "background"
    arq = "arq"
    saq = "saq"
    async_celery = "async-celery"
    faststream = "faststream"
