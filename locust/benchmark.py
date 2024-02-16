import os
from random import shuffle

from locust import between, HttpUser, task


# env endpoint=io/simple locust --config locust/master.conf -f locust/benchmark.py -i 10
class TaskUser(HttpUser):
    wait_time = between(0.001, 0.001)

    @task
    def execute(self):
        endpoint = os.environ.get("endpoint")

        workers = ["arq", "saq", "faststream", "async-celery"]
        shuffle(workers)

        for worker in workers:
            self.client.post(f"/api/v1/incr/{endpoint}/{worker}", json={"value": 1})
