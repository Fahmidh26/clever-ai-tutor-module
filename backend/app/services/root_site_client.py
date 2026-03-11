from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urljoin

import httpx
import jwt
from jwt import InvalidTokenError

from app.config import Settings


@dataclass
class RootSiteClientError(Exception):
    message: str
    status_code: int = 502
    details: str | None = None

    def __str__(self) -> str:
        return self.message


class RootSiteClient:
    def __init__(self, settings: Settings, timeout_seconds: float = 20.0) -> None:
        self._settings = settings
        self._timeout_seconds = timeout_seconds
        self._jwks_cache: dict[str, Any] | None = None
        self._jwks_cache_expires_at: float = 0.0
        self._catalog_cache: Any = None
        self._catalog_etag: str | None = None

    async def exchange_authorization_code(self, code: str) -> dict[str, Any]:
        payload = {
            "grant_type": "authorization_code",
            "client_id": self._settings.aisite_oauth_client_id,
            "client_secret": self._settings.aisite_oauth_client_secret,
            "redirect_uri": self._settings.aisite_oauth_redirect_uri,
            "code": code,
        }
        return await self._request_json("POST", "/api/oauth/token", data=payload)

    async def fetch_user_profile(self, access_token: str) -> dict[str, Any]:
        headers = self._auth_headers(access_token)
        try:
            return await self._request_json("GET", "/api/user/details", headers=headers)
        except RootSiteClientError as exc:
            if exc.status_code != 404:
                raise
        return await self._request_json("GET", "/api/user", headers=headers)

    async def get_credits_balance(self, access_token: str) -> dict[str, Any]:
        return await self._request_json("GET", "/api/user/credits", headers=self._auth_headers(access_token))

    async def deduct_credits(
        self,
        access_token: str,
        *,
        amount: int | None = None,
        tokens: int | None = None,
        action: str = "reserve",
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"action": action}
        if amount is not None:
            payload["amount"] = amount
        if tokens is not None:
            payload["tokens"] = tokens
        if metadata:
            payload["metadata"] = metadata
        return await self._request_json(
            "POST",
            "/api/user/credits/deduct",
            headers=self._auth_headers(access_token),
            json=payload,
        )

    async def get_model_catalog(self, access_token: str | None = None) -> Any:
        headers: dict[str, str] = {"Accept": "application/json"}
        if access_token:
            headers.update(self._auth_headers(access_token))
        if self._catalog_etag:
            headers["If-None-Match"] = self._catalog_etag

        response = await self._request("GET", "/api/catalog", headers=headers)
        if response.status_code == 304 and self._catalog_cache is not None:
            return self._catalog_cache
        if response.status_code >= 400:
            self._raise_for_response("Failed to fetch model catalog", response)

        if etag := response.headers.get("etag"):
            self._catalog_etag = etag
        self._catalog_cache = response.json()
        return self._catalog_cache

    async def verify_jwt(self, token: str, audience: str | None = None) -> dict[str, Any]:
        jwks = await self._get_jwks()
        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header.get("kid")
        if not key_id:
            raise RootSiteClientError("Missing key id in JWT header", status_code=401)

        jwk = next((key for key in jwks.get("keys", []) if key.get("kid") == key_id), None)
        if jwk is None:
            jwks = await self._get_jwks(force_refresh=True)
            jwk = next((key for key in jwks.get("keys", []) if key.get("kid") == key_id), None)
        if jwk is None:
            raise RootSiteClientError("JWT signing key not found in JWKS", status_code=401)

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
        expected_audience = audience if audience is not None else self._settings.root_site_jwt_audience
        options = {"verify_aud": bool(expected_audience)}
        try:
            payload = jwt.decode(
                token,
                key=public_key,
                algorithms=["RS256"],
                audience=expected_audience,
                issuer=self._settings.resolved_root_site_jwt_issuer,
                options=options,
            )
        except InvalidTokenError as exc:
            raise RootSiteClientError("Invalid JWT token", status_code=401, details=str(exc)) from exc
        return payload

    async def check_plan_access(self, access_token: str, required_plan: str | None = None) -> dict[str, Any]:
        profile = await self.fetch_user_profile(access_token)
        raw_plan = profile.get("plan") or profile.get("subscription_plan") or profile.get("tier")
        plan = (raw_plan or "").strip().lower()
        subscription_status = str(profile.get("subscription_status", "")).strip().lower()
        has_active_subscription = subscription_status in {"active", "trialing"} or bool(plan)
        has_required_plan = True if not required_plan else plan == required_plan.strip().lower()
        return {
            "plan": raw_plan,
            "subscription_status": subscription_status or None,
            "has_active_subscription": has_active_subscription,
            "has_required_plan": has_required_plan,
        }

    async def fetch_tutor_experts(self, access_token: str, *, domain: str = "expert-chat") -> dict[str, Any]:
        return await self._request_json(
            "GET",
            f"/api/experts?domain={domain}",
            headers=self._auth_headers(access_token),
        )

    async def tutor_expert_chat(
        self,
        access_token: str,
        *,
        message: str,
        expert_id: int | None = None,
        session_id: int | None = None,
        conversation: list[dict[str, Any]] | None = None,
        mode: str | None = None,
        domain: str = "expert-chat",
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "message": message,
            "domain": domain,
            "conversation": conversation or [],
        }
        if expert_id is not None:
            payload["expert_id"] = expert_id
        if session_id is not None:
            payload["session_id"] = session_id
        if mode:
            payload["mode"] = mode
        return await self._request_json(
            "POST",
            "/api/expert-chat",
            headers=self._auth_headers(access_token),
            json=payload,
        )

    async def list_tutor_sessions(self, access_token: str) -> dict[str, Any]:
        return await self._request_json(
            "GET",
            "/api/tutor/sessions",
            headers=self._auth_headers(access_token),
        )

    async def create_tutor_session(
        self,
        access_token: str,
        *,
        expert_id: int | None = None,
        title: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if expert_id is not None:
            payload["expert_id"] = expert_id
        if title:
            payload["title"] = title
        return await self._request_json(
            "POST",
            "/api/tutor/sessions",
            headers=self._auth_headers(access_token),
            json=payload,
        )

    async def get_tutor_session(self, access_token: str, *, session_id: int) -> dict[str, Any]:
        return await self._request_json(
            "GET",
            f"/api/tutor/sessions/{session_id}",
            headers=self._auth_headers(access_token),
        )

    async def list_tutor_modes(self, access_token: str) -> dict[str, Any]:
        return await self._request_json(
            "GET",
            "/api/tutor/modes",
            headers=self._auth_headers(access_token),
        )

    async def set_tutor_session_mode(self, access_token: str, *, session_id: int, mode: str) -> dict[str, Any]:
        return await self._request_json(
            "POST",
            f"/api/tutor/sessions/{session_id}/mode",
            headers=self._auth_headers(access_token),
            json={"mode": mode},
        )

    def _auth_headers(self, access_token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}

    def _add_internal_auth_header(self, headers: dict[str, str] | None) -> dict[str, str]:
        merged_headers = dict(headers or {})
        if self._settings.root_site_x_auth_hex:
            merged_headers["X-Auth-Hex"] = self._settings.root_site_x_auth_hex
        return merged_headers

    async def _get_jwks(self, force_refresh: bool = False) -> dict[str, Any]:
        now = time.monotonic()
        if not force_refresh and self._jwks_cache and now < self._jwks_cache_expires_at:
            return self._jwks_cache

        response = await self._request("GET", self._settings.resolved_root_site_jwks_url, absolute_url=True)
        if response.status_code >= 400:
            self._raise_for_response("Failed to load JWKS", response)

        self._jwks_cache = response.json()
        self._jwks_cache_expires_at = now + self._settings.root_site_jwks_cache_ttl_seconds
        return self._jwks_cache

    async def _request_json(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = await self._request(method, path, headers=headers, data=data, json=json)
        if response.status_code >= 400:
            self._raise_for_response(f"Root site request failed: {path}", response)
        payload = response.json()
        if not isinstance(payload, dict):
            raise RootSiteClientError(
                f"Unexpected response format from root site for {path}",
                status_code=502,
                details="Expected JSON object.",
            )
        return payload

    async def _request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        absolute_url: bool = False,
    ) -> httpx.Response:
        target_url = path if absolute_url else urljoin(f"{self._settings.aisite_oauth_internal_url}/", path.lstrip("/"))
        request_headers = self._add_internal_auth_header(headers)
        async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
            try:
                return await client.request(
                    method=method,
                    url=target_url,
                    headers=request_headers,
                    data=data,
                    json=json,
                )
            except httpx.HTTPError as exc:
                raise RootSiteClientError(
                    message=f"Failed request to root site: {target_url}",
                    status_code=502,
                    details=str(exc),
                ) from exc

    def _raise_for_response(self, message: str, response: httpx.Response) -> None:
        details = response.text
        raise RootSiteClientError(message=message, status_code=response.status_code, details=details)
