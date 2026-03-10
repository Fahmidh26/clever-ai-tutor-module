from __future__ import annotations

from urllib.parse import urljoin

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(tags=["proxy"])


@router.api_route("/api/main-site/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def call_main_site(path: str, request: Request):
    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    target_url = urljoin(f"{settings.aisite_oauth_internal_url}/", path.lstrip("/"))
    query_params = dict(request.query_params)
    content_type = request.headers.get("content-type", "").lower()

    json_body = None
    data_body = None
    if request.method in {"POST", "PUT", "PATCH"}:
        if "application/json" in content_type:
            body = await request.json()
            if isinstance(body, dict):
                json_body = body
        elif "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
            data_body = dict(await request.form())

    async with httpx.AsyncClient(timeout=30) as client:
        proxy_response = await client.request(
            method=request.method,
            url=target_url,
            params=query_params,
            json=json_body,
            data=data_body,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        )

    response_content_type = proxy_response.headers.get("content-type", "").lower()
    if "application/json" in response_content_type:
        return JSONResponse(status_code=proxy_response.status_code, content=proxy_response.json())

    return JSONResponse(
        status_code=proxy_response.status_code,
        content={"ok": proxy_response.is_success, "response_text": proxy_response.text},
    )
