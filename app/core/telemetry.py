import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

# 1. Golden Signals Telemetry Metrics
HTTP_REQUESTS_TOTAL = Counter(
    "clinic_http_requests_total",
    "Total count of HTTP requests processed by endpoint and status",
    ["method", "endpoint", "status_code"]
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "clinic_http_request_duration_seconds",
    "Histogram of request processing duration in seconds",
    ["method", "endpoint"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
)


class TelemetryAndTracingMiddleware(BaseHTTPMiddleware):
    """Middleware that injects X-Request-ID for distributed tracing 
    and captures Prometheus latency and traffic metrics.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or generate correlation Request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        # Skip metrics scraping path from inflating metrics counters
        path = request.url.path
        if path == "/metrics":
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            raise
        finally:
            duration = time.perf_counter() - start_time
            # Record Prometheus Metrics
            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=path,
                status_code=str(status_code)
            ).inc()

            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=request.method,
                endpoint=path
            ).observe(duration)

        response.headers["X-Request-ID"] = request_id
        return response


def get_metrics_response() -> Response:
    """Returns application metrics in Prometheus exposition format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
