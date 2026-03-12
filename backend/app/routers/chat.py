"""
Local expert chat API — per ARCHITECTURE.md, chat runs on tutor site.
Calls LLM directly, deducts credits via main site.
"""
from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.config import settings
from app.services import root_site_client
from app.services.ai_providers.base import ChatMessage, ModelConfig
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/expert-chat")
async def expert_chat(request: Request):
    """Local chat: uses tutor LLM provider, deducts credits via main site."""
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})

    body = await request.json()
    message = (body.get("message") or "").strip()
    expert_id = body.get("expert_id")
    conversation = body.get("conversation") or []

    if not message:
        return JSONResponse(status_code=400, content={"error": "message is required"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    from app.services import provider_registry

    if not provider_registry.registered_provider_names():
        return JSONResponse(
            status_code=503,
            content={"error": "No LLM provider configured. Set OPENAI_API_KEY for local chat."},
        )

    system_prompt = "You are a helpful tutor. Be clear, concise, and encouraging."
    if expert_id is not None:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, system_prompt FROM tutor_personas WHERE id = $1 AND is_active = TRUE",
                expert_id,
            )
            if row:
                system_prompt = row["system_prompt"] or system_prompt

    messages: list[ChatMessage] = [ChatMessage(role="system", content=system_prompt)]
    for item in conversation:
        if isinstance(item, dict):
            role = item.get("role", "user")
            content = item.get("content", "") or item.get("message", "")
            if content:
                messages.append(ChatMessage(role=str(role), content=str(content)))
    messages.append(ChatMessage(role="user", content=message))

    model_config = ModelConfig(
        provider="openai",
        model=settings.openai_default_model,
        temperature=0.2,
        max_tokens=1024,
    )

    try:
        provider = provider_registry.get_provider("openai")
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"error": "OpenAI provider not available"},
        )

    full_response = ""
    try:
        async for chunk in provider.stream_chat(messages, model_config):
            full_response += chunk
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"error": "LLM request failed", "details": str(e)},
        )

    tokens_used = provider.count_tokens(message) + provider.count_tokens(full_response)
    try:
        await root_site_client.deduct_credits(
            token,
            tokens=tokens_used,
            action="reconcile",
            metadata={"source": "tutor_expert_chat", "model": model_config.model},
        )
    except Exception:
        pass

    return {"response": full_response, "tokens_used": tokens_used}
