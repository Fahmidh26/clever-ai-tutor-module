from __future__ import annotations

import json
from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.services.safety_guardrails import check_user_message

_GUARDED_PATHS = {"/api/expert-chat", "/api/expert-chat/stream"}


async def tutor_guardrail_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    if request.method != "POST" or request.url.path not in _GUARDED_PATHS:
        return await call_next(request)

    content_type = request.headers.get("content-type", "").lower()
    if "application/json" not in content_type:
        return await call_next(request)

    raw_body = await request.body()
    if len(raw_body) > 100_000:
        return JSONResponse(
            status_code=413,
            content={"error": "Request body too large for tutor chat endpoint."},
        )

    try:
        payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    except (ValueError, UnicodeDecodeError):
        return JSONResponse(status_code=400, content={"error": "Invalid JSON payload"})

    message = str(payload.get("message") or "")
    decision = check_user_message(message)
    if decision.blocked:
        return JSONResponse(
            status_code=422,
            content={"error": decision.message, "code": decision.code},
        )

    # Preserve body for downstream handlers that call request.json()/request.body().
    request._body = raw_body  # noqa: SLF001
    return await call_next(request)

