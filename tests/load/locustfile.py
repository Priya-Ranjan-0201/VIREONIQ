"""
Manual Load Test Definition (Locust) for VIREONIQ API.

Run manually against a staging or local dev instance:
    locust -f tests/load/locustfile.py --host=http://127.0.0.1:8000
"""

from locust import HttpUser, between, task


class VireoniqApiUser(HttpUser):
    wait_time = between(0.5, 2.0)

    @task(5)
    def health_check(self) -> None:
        self.client.get("/health", name="/health")

    @task(2)
    def metrics_scrape(self) -> None:
        self.client.get("/metrics", name="/metrics")

    @task(1)
    def root_info(self) -> None:
        self.client.get("/", name="/")
