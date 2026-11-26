import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

from core.observability import request_id_ctx, trace_id_ctx

# Configure structlog for structured JSON logging with request/trace context and no PII
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger("vireoniq.request")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        req_id = request_id_ctx.get() or request.headers.get("X-Request-ID", "")
        tr_id = trace_id_ctx.get() or request.headers.get("X-Trace-ID", "")
        structlog.contextvars.bind_contextvars(request_id=req_id, trace_id=tr_id)

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                "http_request",
                method=request.method,
                path=request.url.path,
                status=response.status_code,
                duration=f"{process_time:.4f}s",
            )
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "http_request_error",
                method=request.method,
                path=request.url.path,
                status=500,
                duration=f"{process_time:.4f}s",
                error_type=type(e).__name__,
            )
            raise
        finally:
            structlog.contextvars.clear_contextvars()
