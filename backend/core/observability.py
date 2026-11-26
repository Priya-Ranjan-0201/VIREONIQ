"""
Observability Telemetry, Prometheus Metrics & OpenTelemetry-Compatible Trace Context.

Provides thread-safe in-process metric aggregation exported in standard Prometheus
text exposition format (`text/plain; version=0.0.4`), request-ID tracing, and
structured LLM latency/token/cost accounting without leaking PII.
"""

from __future__ import annotations

import threading
import time
import uuid
from collections import defaultdict
from contextvars import ContextVar
from typing import Dict, Tuple

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

request_id_ctx: ContextVar[str] = ContextVar("vireoniq_request_id", default="")
trace_id_ctx: ContextVar[str] = ContextVar("vireoniq_trace_id", default="")


class MetricsRegistry:
    """In-memory thread-safe Prometheus metric registry for HTTP, LLM, and queue signals."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.http_requests_total: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self.http_errors_total: Dict[Tuple[str, str], int] = defaultdict(int)
        self.http_duration_sum: Dict[Tuple[str, str], float] = defaultdict(float)
        self.http_duration_count: Dict[Tuple[str, str], int] = defaultdict(int)

        self.llm_requests_total: Dict[Tuple[str, str], int] = defaultdict(int)
        self.llm_tokens_total: Dict[Tuple[str, str, str], int] = defaultdict(int)
        self.llm_cost_usd_total: Dict[Tuple[str, str], float] = defaultdict(float)
        self.llm_latency_sum: Dict[Tuple[str, str], float] = defaultdict(float)
        self.llm_latency_count: Dict[Tuple[str, str], int] = defaultdict(int)

        self.celery_queue_depth: Dict[str, int] = defaultdict(int)

    def reset(self) -> None:
        with self._lock:
            self.http_requests_total.clear()
            self.http_errors_total.clear()
            self.http_duration_sum.clear()
            self.http_duration_count.clear()
            self.llm_requests_total.clear()
            self.llm_tokens_total.clear()
            self.llm_cost_usd_total.clear()
            self.llm_latency_sum.clear()
            self.llm_latency_count.clear()
            self.celery_queue_depth.clear()

    def record_http_request(self, method: str, path: str, status_code: int, duration_seconds: float) -> None:
        safe_path = _normalize_path(path)
        with self._lock:
            self.http_requests_total[(method, safe_path, str(status_code))] += 1
            self.http_duration_sum[(method, safe_path)] += duration_seconds
            self.http_duration_count[(method, safe_path)] += 1
            if status_code >= 400:
                self.http_errors_total[(method, safe_path)] += 1

    def record_llm_call(
        self,
        provider: str,
        model: str,
        latency_seconds: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        with self._lock:
            self.llm_requests_total[(provider, model)] += 1
            self.llm_tokens_total[(provider, model, "input")] += max(0, input_tokens)
            self.llm_tokens_total[(provider, model, "output")] += max(0, output_tokens)
            self.llm_cost_usd_total[(provider, model)] += max(0.0, cost_usd)
            self.llm_latency_sum[(provider, model)] += max(0.0, latency_seconds)
            self.llm_latency_count[(provider, model)] += 1

    def set_queue_depth(self, queue_name: str, depth: int) -> None:
        with self._lock:
            self.celery_queue_depth[queue_name] = max(0, depth)

    def render_prometheus(self) -> str:
        lines = [
            "# HELP vireoniq_http_requests_total Total HTTP requests processed",
            "# TYPE vireoniq_http_requests_total counter",
        ]
        with self._lock:
            for (method, path, status), val in sorted(self.http_requests_total.items()):
                lines.append(
                    f'vireoniq_http_requests_total{{method="{_esc(method)}",path="{_esc(path)}",status="{_esc(status)}"}} {val}'
                )

            lines.extend([
                "# HELP vireoniq_http_errors_total Total HTTP 4xx/5xx error responses",
                "# TYPE vireoniq_http_errors_total counter",
            ])
            for (method, path), val in sorted(self.http_errors_total.items()):
                lines.append(
                    f'vireoniq_http_errors_total{{method="{_esc(method)}",path="{_esc(path)}"}} {val}'
                )

            lines.extend([
                "# HELP vireoniq_http_request_duration_seconds Total HTTP latency sum and count",
                "# TYPE vireoniq_http_request_duration_seconds summary",
            ])
            for (method, path), dur_val in sorted(self.http_duration_sum.items()):
                cnt = self.http_duration_count[(method, path)]
                lines.append(
                    f'vireoniq_http_request_duration_seconds_sum{{method="{_esc(method)}",path="{_esc(path)}"}} {dur_val:.6f}'
                )
                lines.append(
                    f'vireoniq_http_request_duration_seconds_count{{method="{_esc(method)}",path="{_esc(path)}"}} {cnt}'
                )

            lines.extend([
                "# HELP vireoniq_llm_requests_total Total LLM calls by provider and model",
                "# TYPE vireoniq_llm_requests_total counter",
            ])
            for (provider, model), llm_req_cnt in sorted(self.llm_requests_total.items()):
                lines.append(
                    f'vireoniq_llm_requests_total{{provider="{_esc(provider)}",model="{_esc(model)}"}} {llm_req_cnt}'
                )

            lines.extend([
                "# HELP vireoniq_llm_tokens_total Total LLM tokens processed",
                "# TYPE vireoniq_llm_tokens_total counter",
            ])
            for (provider, model, direction), tok_cnt in sorted(self.llm_tokens_total.items()):
                lines.append(
                    f'vireoniq_llm_tokens_total{{provider="{_esc(provider)}",model="{_esc(model)}",direction="{_esc(direction)}"}} {tok_cnt}'
                )

            lines.extend([
                "# HELP vireoniq_llm_cost_usd_total Cumulative estimated LLM USD cost",
                "# TYPE vireoniq_llm_cost_usd_total counter",
            ])
            for (provider, model), cost_val in sorted(self.llm_cost_usd_total.items()):
                lines.append(
                    f'vireoniq_llm_cost_usd_total{{provider="{_esc(provider)}",model="{_esc(model)}"}} {cost_val:.6f}'
                )

            lines.extend([
                "# HELP vireoniq_llm_latency_seconds LLM call latency summary",
                "# TYPE vireoniq_llm_latency_seconds summary",
            ])
            for (provider, model), lat_val in sorted(self.llm_latency_sum.items()):
                cnt = self.llm_latency_count[(provider, model)]
                lines.append(
                    f'vireoniq_llm_latency_seconds_sum{{provider="{_esc(provider)}",model="{_esc(model)}"}} {lat_val:.6f}'
                )
                lines.append(
                    f'vireoniq_llm_latency_seconds_count{{provider="{_esc(provider)}",model="{_esc(model)}"}} {cnt}'
                )

            lines.extend([
                "# HELP vireoniq_celery_queue_depth Current Celery queue depth",
                "# TYPE vireoniq_celery_queue_depth gauge",
            ])
            for queue_name, val in sorted(self.celery_queue_depth.items()):
                lines.append(f'vireoniq_celery_queue_depth{{queue="{_esc(queue_name)}"}} {val}')

        return "\n".join(lines) + "\n"


metrics_registry = MetricsRegistry()


def _esc(val: str) -> str:
    return val.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "")


def _normalize_path(path: str) -> str:
    """Collapse numeric/UUID-like segments to avoid high-cardinality metric labels or PII leakage."""
    parts = []
    for seg in path.split("/"):
        if not seg:
            continue
        if seg.isdigit() or (len(seg) >= 32 and "-" in seg):
            parts.append("{id}")
        else:
            parts.append(seg)
    return "/" + "/".join(parts)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Attaches X-Request-ID and traceparent correlation headers and records Prometheus HTTP metrics."""

    async def dispatch(self, request: Request, call_next) -> Response:
        req_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        trace_id = request.headers.get("traceparent") or uuid.uuid4().hex

        tok_req = request_id_ctx.set(req_id)
        tok_tr = trace_id_ctx.set(trace_id)
        start = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = req_id
            response.headers["X-Trace-ID"] = trace_id
            return response
        finally:
            duration = time.perf_counter() - start
            route = request.scope.get("route")
            route_path = getattr(route, "path", request.url.path)
            metrics_registry.record_http_request(request.method, route_path, status_code, duration)
            request_id_ctx.reset(tok_req)
            trace_id_ctx.reset(tok_tr)
