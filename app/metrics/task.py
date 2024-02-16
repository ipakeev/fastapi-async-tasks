from collections.abc import Callable

from prometheus_async.aio import count_exceptions, time
from prometheus_client import Counter, Histogram

EXECUTION_TIME = Histogram("task_execution_seconds", "Task execution time")
TASKS_FAILED = Counter("tasks_failed", "Tasks failed")


def export_task_metrics(func: Callable) -> Callable:
    time_metric = time(EXECUTION_TIME)
    failed_metric = count_exceptions(TASKS_FAILED)

    return failed_metric(time_metric(func))
