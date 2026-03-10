from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import Request, Response


async def request_logging_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex
    logger = structlog.get_logger().bind(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
    )

    started_at = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception("request_failed", duration_ms=elapsed_ms)
        raise

    elapsed_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers["x-request-id"] = request_id
    logger.info("request_complete", status_code=response.status_code, duration_ms=elapsed_ms)
    return response
