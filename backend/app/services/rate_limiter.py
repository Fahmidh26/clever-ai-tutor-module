from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.config import settings

_REDIS_KEY_CHARS = re.compile(r"[^a-zA-Z0-9:_-]+")


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    limit: int
    remaining: int
    reset_after_seconds: int


async def init_rate_limiter(app: FastAPI) -> None:
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)


async def close_rate_limiter(app: FastAPI) -> None:
    redis_client: Redis | None = getattr(app.state, "redis", None)
    if redis_client is not None:
        await redis_client.aclose()
        app.state.redis = None


def _extract_user_id(user: dict[str, Any] | None) -> str | None:
    if not isinstance(user, dict):
        return None

    tutor_user = user.get("tutor_user")
    if isinstance(tutor_user, dict):
        root_user_id = tutor_user.get("root_user_id")
        if isinstance(root_user_id, int) and root_user_id > 0:
            return str(root_user_id)

    for key in ("root_user_id", "id", "user_id", "uid"):
        value = user.get(key)
        if isinstance(value, int) and value > 0:
            return str(value)
        if isinstance(value, str) and value.isdigit():
            return value
    return None


def _normalize_endpoint_key(endpoint_key: str) -> str:
    normalized = endpoint_key.strip().lower().replace("/", ":")
    normalized = _REDIS_KEY_CHARS.sub("-", normalized)
    return normalized[:120] or "unknown"


async def check_user_rate_limit(
    request: Request,
    *,
    endpoint_key: str,
    limit: int | None = None,
    window_seconds: int | None = None,
) -> RateLimitDecision:
    request_limit = limit if limit is not None else settings.rate_limit_requests_per_window
    request_window_seconds = window_seconds if window_seconds is not None else settings.rate_limit_window_seconds

    user = request.session.get("user")
    user_id = _extract_user_id(user)
    if user_id is None:
        # Keep auth failure behavior owned by endpoint handlers.
        return RateLimitDecision(
            allowed=True,
            limit=request_limit,
            remaining=request_limit,
            reset_after_seconds=request_window_seconds,
        )

    redis_client: Redis | None = getattr(request.app.state, "redis", None)
    if redis_client is None:
        # Fail-open when Redis is unavailable.
        return RateLimitDecision(
            allowed=True,
            limit=request_limit,
            remaining=request_limit,
            reset_after_seconds=request_window_seconds,
        )

    now = int(time.time())
    window_id = now // request_window_seconds
    normalized_endpoint = _normalize_endpoint_key(endpoint_key)
    redis_key = f"rl:user:{user_id}:ep:{normalized_endpoint}:w:{window_id}"

    try:
        count = await redis_client.incr(redis_key)
        if count == 1:
            await redis_client.expire(redis_key, request_window_seconds + 5)
    except RedisError:
        request.app.state.redis = None
        return RateLimitDecision(
            allowed=True,
            limit=request_limit,
            remaining=request_limit,
            reset_after_seconds=request_window_seconds,
        )

    remaining = max(request_limit - count, 0)
    reset_after_seconds = request_window_seconds - (now % request_window_seconds)

    return RateLimitDecision(
        allowed=count <= request_limit,
        limit=request_limit,
        remaining=remaining,
        reset_after_seconds=reset_after_seconds,
    )


async def enforce_user_rate_limit(
    request: Request,
    *,
    endpoint_key: str,
    limit: int | None = None,
    window_seconds: int | None = None,
) -> JSONResponse | None:
    decision = await check_user_rate_limit(
        request,
        endpoint_key=endpoint_key,
        limit=limit,
        window_seconds=window_seconds,
    )
    if decision.allowed:
        return None

    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "limit": decision.limit,
            "remaining": decision.remaining,
            "reset_after_seconds": decision.reset_after_seconds,
            "endpoint": endpoint_key,
        },
    )
