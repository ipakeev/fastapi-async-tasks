import os

from locust import between, HttpUser, task


# env endpoint=io/simple locust --config locust/master.conf -f locust/background.py -i 1
class TaskUser(HttpUser):
    wait_time = between(0.001, 0.001)

    @task
    def execute(self):
        endpoint = os.environ.get("endpoint")

        self.client.post(f"/api/v1/incr/{endpoint}/background", json={"value": 1})
