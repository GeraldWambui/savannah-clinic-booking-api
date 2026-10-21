import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """Middleware that injects an X-Request-ID correlation header and 
    tracks request execution duration in X-Process-Time header.
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        return response
