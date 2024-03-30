from collections.abc import Callable
from functools import wraps
from typing import Any

from prometheus_async.aio import count_exceptions, time
from prometheus_client import Counter, Histogram

EXECUTION_TIME = Histogram(
    "task_execution_seconds",
    "Task execution time",
    labelnames=["task_name"],
)
TASKS_FAILED = Counter(
    "tasks_failed",
    "Tasks failed",
    labelnames=["task_name"],
)


def export_task_metrics(func: Callable) -> Callable:
    @count_exceptions(TASKS_FAILED.labels(task_name=func.__name__))
    @time(EXECUTION_TIME.labels(task_name=func.__name__))
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)

    return wrapper
