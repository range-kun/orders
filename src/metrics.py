import time

from fastapi import APIRouter, FastAPI
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    generate_latest,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.request_counter = Counter(
            "http_requests_total",
            "Total number of HTTP requests",
            labelnames=["method", "status_code"],
            registry=REGISTRY,
        )
        self.error_counter = Counter("http_errors_total", "Total number of HTTP errors", registry=REGISTRY)
        self.request_duration = Gauge(
            "http_request_duration_seconds", "Duration of HTTP requests in seconds", registry=REGISTRY
        )

    async def dispatch(self, request: Request, call_next):
        try:
            start_time = time.time()
            response = await call_next(request)
        except Exception:
            status_code = 500
            self.error_counter.inc()
            return Response(content={"error": "Internal Server Error"}, status_code=status_code)
        duration = time.time() - start_time
        self.request_duration.set(duration)

        self.request_counter.labels(method=request.method, status_code=response.status_code).inc()
        return response


metrics_router = APIRouter(tags=["metrics"], prefix="/metrics")


@metrics_router.get("", include_in_schema=False)
async def get_metrics():
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)
