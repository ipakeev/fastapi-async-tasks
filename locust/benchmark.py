import os
from random import shuffle

from locust import between, HttpUser, task


# locust --config locust/master.conf -f locust/benchmark.py -i 100 -u 10
class TaskUser(HttpUser):
    wait_time = between(0.001, 0.001)

    @task
    def execute(self):
        endpoint = os.environ.get("endpoint")
        endpoints = (
            [endpoint]
            if endpoint
            else ["io/simple", "io/sync", "io/thread", "cpu/simple", "cpu/process"]
        )

        worker = os.environ.get("worker")
        workers = (
            [worker]
            if worker
            else ["arq", "saq", "faststream", "async-celery"]
        )

        params = [(endpoint, worker) for endpoint in endpoints for worker in workers]
        shuffle(params)

        for endpoint, worker in params:
            self.client.post(f"/api/v1/incr/{endpoint}/{worker}", json={"value": 1})
