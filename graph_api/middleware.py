"""
middleware.py — request lifecycle middleware.

RequestIDMiddleware:
  - Generates a unique UUID for every incoming request
  - Attaches it to the request state so route handlers can reference it
  - Adds it to the response headers as X-Request-ID
  - Logs every request/response with timing and status

Why request IDs?
  When multiple requests are in flight simultaneously, log lines from
  different requests interleave. Without a request ID there is no way
  to reconstruct what happened during a single request. With one, you
  can filter your log aggregator to a single ID and see the complete
  picture: which endpoint was called, what the status was, how long it
  took, and any errors that occurred.

  The frontend should log the X-Request-ID from error responses so
  support can trace exactly what happened server-side.
"""
import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that assigns a unique request ID to every request.

    For each request:
      1. Generates a UUID4 request ID (or reads X-Request-ID from the
         incoming headers if the client provides one — useful for
         end-to-end tracing from the frontend)
      2. Attaches it to request.state.request_id
      3. Logs the incoming request
      4. Times the handler execution
      5. Logs the outgoing response with status and duration
      6. Adds X-Request-ID to the response headers
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Use client-provided ID if present, otherwise generate one
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Log the incoming request
        logger.info(
            f"{request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query": str(request.query_params) or None,
                "client": request.client.host if request.client else None,
            },
        )

        # Time the handler
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start) * 1000, 1)
            logger.error(
                f"Unhandled exception after {duration_ms}ms",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        # Log the response
        log_fn = logger.warning if response.status_code >= 400 else logger.info
        log_fn(
            f"{response.status_code} {request.method} {request.url.path} "
            f"({duration_ms}ms)",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Attach request ID to response so the client can log it
        response.headers["X-Request-ID"] = request_id
        return response
