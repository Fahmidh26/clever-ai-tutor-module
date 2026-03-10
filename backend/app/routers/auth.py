from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import settings

router = APIRouter(tags=["auth"])


@router.get("/oauth/login")
async def oauth_login(request: Request):
    if not settings.aisite_oauth_client_id or not settings.aisite_oauth_client_secret:
        return JSONResponse(
            status_code=500,
            content={"error": "OAuth client credentials are missing in backend/.env"},
        )

    state = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state

    query = urlencode(
        {
            "response_type": "code",
            "client_id": settings.aisite_oauth_client_id,
            "redirect_uri": settings.aisite_oauth_redirect_uri,
            "scope": "basic",
            "state": state,
        }
    )
    authorize_url = f"{settings.aisite_oauth_base_url}/oauth/authorize?{query}"
    return RedirectResponse(url=authorize_url)


@router.get("/oauth/callback")
async def oauth_callback(request: Request, code: str | None = None, state: str | None = None):
    session_state = request.session.pop("oauth_state", None)
    if not state or not session_state or state != session_state:
        return JSONResponse(status_code=403, content={"error": "Invalid oauth state"})

    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing authorization code"})

    token_url = f"{settings.aisite_oauth_internal_url}/api/oauth/token"
    user_url = f"{settings.aisite_oauth_internal_url}/api/user"

    async with httpx.AsyncClient(timeout=15) as client:
        token_response = await client.post(
            token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.aisite_oauth_client_id,
                "client_secret": settings.aisite_oauth_client_secret,
                "redirect_uri": settings.aisite_oauth_redirect_uri,
                "code": code,
            },
        )

        if token_response.status_code >= 400:
            return JSONResponse(
                status_code=token_response.status_code,
                content={"error": "Token exchange failed", "details": token_response.text},
            )

        token_data = token_response.json()
        access_token = token_data.get("access_token")
        if not access_token:
            return JSONResponse(status_code=500, content={"error": "No access_token in token response"})

        user_response = await client.get(
            user_url,
            headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        )

        if user_response.status_code >= 400:
            return JSONResponse(
                status_code=user_response.status_code,
                content={"error": "Failed to fetch user profile", "details": user_response.text},
            )

        provider_user = user_response.json()

    request.session["access_token"] = access_token
    request.session["user"] = provider_user

    return RedirectResponse(url=f"{settings.frontend_url}{settings.normalized_post_login_path}")


@router.get("/api/me")
async def me(request: Request):
    user = request.session.get("user")
    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    return {"user": user, "access_token": token}


@router.post("/api/logout")
@router.get("/api/logout")
async def logout(request: Request):
    request.session.clear()
    return {"ok": True}
