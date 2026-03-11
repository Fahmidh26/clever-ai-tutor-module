from __future__ import annotations

import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import settings
from app.services import root_site_client, sync_tutor_user_on_login
from app.services.root_site_client import RootSiteClientError
from app.services.tutor_user_sync import TutorUserSyncError

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

    try:
        token_data = await root_site_client.exchange_authorization_code(code)
        access_token = token_data.get("access_token")
        if not access_token:
            return JSONResponse(status_code=500, content={"error": "No access_token in token response"})
        provider_user = await root_site_client.fetch_user_profile(access_token)
        tutor_user_sync = await sync_tutor_user_on_login(request.app, provider_user)
    except RootSiteClientError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details},
        )
    except TutorUserSyncError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details},
        )

    request.session["access_token"] = access_token
    request.session["user"] = {
        **provider_user,
        "tutor_user": tutor_user_sync.as_dict(),
    }

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
