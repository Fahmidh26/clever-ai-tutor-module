from __future__ import annotations

import hashlib
import secrets
from urllib.parse import urlencode

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import settings
from app.services import root_site_client, sync_tutor_user_on_login
from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rbac import resolve_user_role
from app.services.root_site_client import RootSiteClientError
from app.services.tutor_user_sync import TutorUserSyncError

router = APIRouter(tags=["auth"])


def _find_local_dev_account(email: str) -> dict[str, object] | None:
    normalized_email = email.strip().lower()
    for account in settings.local_dev_accounts:
        candidate_email = str(account.get("email") or "").strip().lower()
        if candidate_email and candidate_email == normalized_email:
            return account
    return None


def _build_local_provider_user(account: dict[str, object]) -> dict[str, object]:
    email = str(account.get("email") or "").strip().lower()
    display_name = str(account.get("display_name") or email.split("@", maxsplit=1)[0] or "Local User").strip()
    role = str(account.get("role") or "student").strip().lower()
    provider_user: dict[str, object] = {
        "id": int(account.get("root_user_id") or 0),
        "root_user_id": int(account.get("root_user_id") or 0),
        "email": email,
        "name": display_name,
        "display_name": display_name,
        "role": role,
        "preferred_language": str(account.get("preferred_language") or "en"),
        "auth_source": "local_dev",
    }
    if account.get("grade_level") is not None:
        provider_user["grade_level"] = account.get("grade_level")
    if role == "admin":
        provider_user["is_admin"] = True
    return provider_user


@router.get("/oauth/login")
async def oauth_login(request: Request):
    if settings.auth_mode == "local_dev":
        return RedirectResponse(url=f"{settings.frontend_url}{settings.normalized_local_dev_login_path}")

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
    if settings.auth_mode == "local_dev":
        return RedirectResponse(url=f"{settings.frontend_url}{settings.normalized_local_dev_login_path}")

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
        provider_user_raw = await root_site_client.fetch_user_profile(access_token)
        provider_user = provider_user_raw
        if isinstance(provider_user_raw.get("data"), dict):
            provider_user = provider_user_raw["data"]

        # If the profile doesn't include a numeric ID field, try to extract one from the access token.
        if not any(k in provider_user for k in ("root_user_id", "id", "user_id", "uid")):
            try:
                token_payload = await root_site_client.verify_jwt(access_token)
                for field in ("sub", "user_id", "id"):
                    if field in token_payload:
                        try:
                            provider_user["id"] = int(token_payload[field])
                            break
                        except (TypeError, ValueError):
                            continue
            except Exception:
                # Ignore failures; the sync step will report a friendly error.
                pass

        # As a final fallback for local/dev environments, generate a stable numeric id from email.
        if not any(k in provider_user for k in ("root_user_id", "id", "user_id", "uid")):
            email = provider_user.get("email")
            if isinstance(email, str) and email:
                digest = hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()
                provider_user["id"] = int(digest[:12], 16)

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


@router.get("/api/local-auth/accounts")
async def local_auth_accounts(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    if settings.auth_mode != "local_dev":
        return JSONResponse(status_code=404, content={"error": "Local auth is not enabled"})

    accounts = []
    for account in settings.local_dev_accounts:
        accounts.append(
            {
                "email": account.get("email"),
                "display_name": account.get("display_name"),
                "role": account.get("role"),
                "grade_level": account.get("grade_level"),
            }
        )

    return {
        "auth_mode": settings.auth_mode,
        "password_hint": "Use the configured local dev password from backend settings.",
        "accounts": accounts,
    }


@router.post("/api/local-auth/login")
async def local_auth_login(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    if settings.auth_mode != "local_dev":
        return JSONResponse(status_code=404, content={"error": "Local auth is not enabled"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    email = str(body.get("email") or "").strip().lower()
    password = str(body.get("password") or "")
    if not email or not password:
        return JSONResponse(status_code=400, content={"error": "email and password are required"})
    if password != settings.local_dev_password:
        return JSONResponse(status_code=401, content={"error": "Invalid local dev credentials"})

    account = _find_local_dev_account(email)
    if account is None:
        return JSONResponse(status_code=404, content={"error": "Local dev account not found"})

    provider_user = _build_local_provider_user(account)
    try:
        tutor_user_sync = await sync_tutor_user_on_login(request.app, provider_user)
    except TutorUserSyncError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "details": exc.details},
        )

    access_token = f"local-dev-token:{provider_user['root_user_id']}"
    request.session["access_token"] = access_token
    request.session["user"] = {
        **provider_user,
        "tutor_user": tutor_user_sync.as_dict(),
    }
    return {"ok": True, "access_token": access_token, "role": tutor_user_sync.role}


@router.get("/api/me")
async def me(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    user = request.session.get("user")
    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role = resolve_user_role(user)
    return {"user": user, "access_token": token, "role": role}


@router.post("/api/logout")
@router.get("/api/logout")
async def logout(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    request.session.clear()
    return {"ok": True}
