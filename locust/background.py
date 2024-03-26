import os

from locust import between, HttpUser, task


# locust --config locust/master.conf -f locust/background.py -i 100 -u 10
class TaskUser(HttpUser):
    wait_time = between(0.001, 0.001)

    @task
    def execute(self):
        endpoint = os.environ.get("endpoint")
        endpoints = (
            [endpoint]
            if endpoint
            else ["io/simple", "io/thread", "cpu/simple", "cpu/process"]
        )

        for endpoint in endpoints:
            self.client.post(f"/api/v1/incr/{endpoint}/background", json={"value": 1})
