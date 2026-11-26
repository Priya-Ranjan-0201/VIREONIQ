from fastapi.testclient import TestClient

from core.observability import metrics_registry
from main import app


def test_observability_request_id_and_prometheus_metrics():
    metrics_registry.reset()
    client = TestClient(app)

    # 1. Verify X-Request-ID generation and echo
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert res_root.headers.get("X-Request-ID")
    assert res_root.headers.get("X-Trace-ID")

    res_custom = client.get("/", headers={"X-Request-ID": "req-custom-123"})
    assert res_custom.status_code == 200
    assert res_custom.headers.get("X-Request-ID") == "req-custom-123"

    # 2. Verify 404 increments error counter
    res_404 = client.get("/api/v1/nonexistent-observability-probe")
    assert res_404.status_code == 404

    # 3. Record LLM & queue telemetry
    metrics_registry.record_llm_call(
        provider="fake-ci-provider",
        model="deterministic-v1",
        latency_seconds=0.042,
        input_tokens=120,
        output_tokens=64,
        cost_usd=0.0,
    )
    metrics_registry.set_queue_depth("default", 3)

    # 4. Scrape /metrics in Prometheus exposition format
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "text/plain" in res_metrics.headers["content-type"]
    body = res_metrics.text
    assert "vireoniq_http_requests_total" in body
    assert "vireoniq_http_errors_total" in body
    assert "vireoniq_http_request_duration_seconds_sum" in body
    assert "vireoniq_llm_requests_total" in body
    assert "vireoniq_llm_tokens_total" in body
    assert "vireoniq_llm_cost_usd_total" in body
    assert 'vireoniq_celery_queue_depth{queue="default"} 3' in body
