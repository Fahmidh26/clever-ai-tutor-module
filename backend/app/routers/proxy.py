from __future__ import annotations

from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import settings
from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rbac import evaluate_access, required_roles_for_proxy_path

router = APIRouter(tags=["proxy"])

_PROXY_BLOCKED_PREFIXES = ("api/experts", "api/expert-chat", "api/tutor/sessions")


def _is_proxy_blocked(path: str) -> bool:
    normalized = path.lstrip("/")
    return any(normalized.startswith(p) for p in _PROXY_BLOCKED_PREFIXES)


@router.api_route("/api/main-site/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def call_main_site(path: str, request: Request):
    if _is_proxy_blocked(path):
        return JSONResponse(
            status_code=400,
            content={
                "error": "Use local tutor APIs for experts/chat/sessions. See ARCHITECTURE.md.",
                "hint": "Call /api/experts and /api/expert-chat directly (no main-site proxy).",
            },
        )

    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:/api/main-site/{path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    user = request.session.get("user")
    required_roles = required_roles_for_proxy_path(path)
    decision = evaluate_access(user, required_roles)
    if not decision.allowed:
        return JSONResponse(
            status_code=403,
            content={
                "error": "Forbidden",
                "details": decision.reason,
                "required_roles": decision.required_roles,
                "user_role": decision.user_role,
            },
        )

    target_url = urljoin(f"{settings.aisite_oauth_internal_url}/", path.lstrip("/"))
    query_params = dict(request.query_params)
    content_type = request.headers.get("content-type", "").lower()
    accept_header = request.headers.get("accept", "application/json")

    json_body = None
    data_body = None
    if request.method in {"POST", "PUT", "PATCH"}:
        if "application/json" in content_type:
            body = await request.json()
            if isinstance(body, dict):
                json_body = body
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            data_body = dict(await request.form())

    headers = {"Authorization": f"Bearer {token}", "Accept": accept_header}
    if settings.root_site_x_auth_hex:
        headers["X-Auth-Hex"] = settings.root_site_x_auth_hex

    wants_sse = "text/event-stream" in accept_header
    if wants_sse:
        client = httpx.AsyncClient(timeout=None)
        upstream_response = await client.send(
            client.build_request(
                method=request.method,
                url=target_url,
                params=query_params,
                json=json_body,
                data=data_body,
                headers=headers,
            ),
            stream=True,
        )
        if upstream_response.status_code >= 400:
            body = await upstream_response.aread()
            await upstream_response.aclose()
            await client.aclose()
            return JSONResponse(
                status_code=upstream_response.status_code,
                content={"error": "Main-site stream request failed", "details": body.decode("utf-8", errors="ignore")},
            )

        async def sse_iterator():
            try:
                async for chunk in upstream_response.aiter_bytes():
                    yield chunk
            finally:
                await upstream_response.aclose()
                await client.aclose()

        stream_content_type = upstream_response.headers.get("content-type", "text/event-stream")
        return StreamingResponse(
            sse_iterator(),
            status_code=upstream_response.status_code,
            media_type=stream_content_type,
            headers={"Cache-Control": "no-cache"},
        )

    async with httpx.AsyncClient(timeout=30) as client:
        proxy_response = await client.request(
            method=request.method,
            url=target_url,
            params=query_params,
            json=json_body,
            data=data_body,
            headers=headers,
        )

    response_content_type = proxy_response.headers.get("content-type", "").lower()
    if "application/json" in response_content_type:
        return JSONResponse(status_code=proxy_response.status_code, content=proxy_response.json())

    return JSONResponse(
        status_code=proxy_response.status_code,
        content={"ok": proxy_response.is_success, "response_text": proxy_response.text},
    )
