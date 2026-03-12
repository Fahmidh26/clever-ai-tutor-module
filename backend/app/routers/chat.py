"""
Local expert chat API — per ARCHITECTURE.md, chat runs on tutor site.
Calls LLM directly, deducts credits via main site.
Optionally persists messages to tutor_messages when session_id is provided.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse

from app.config import settings
from app.services import root_site_client
from app.services.ai_providers.base import ChatMessage, ModelConfig
from app.services.mode_prompts import MODE_IDS, build_system_prompt, normalize_mode
from app.services.rate_limiter import enforce_user_rate_limit

router = APIRouter(prefix="/api", tags=["chat"])


def _get_tutor_user_id(request: Request) -> int | None:
    user = request.session.get("user")
    if not user:
        return None
    tutor_user = user.get("tutor_user")
    if not isinstance(tutor_user, dict):
        return None
    tid = tutor_user.get("tutor_user_id")
    if tid is None:
        return None
    try:
        return int(tid)
    except (TypeError, ValueError):
        return None


@router.post("/expert-chat")
async def expert_chat(request: Request):
    """Local chat: uses tutor LLM provider, deducts credits via main site.
    If session_id is provided, persists user + assistant messages to tutor_messages."""
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
    session_id = body.get("session_id")
    mode = (body.get("mode") or "").strip().lower() or "teach_me"
    hint_level = body.get("hint_level")
    conversation = body.get("conversation") or []

    if not message:
        return JSONResponse(status_code=400, content={"error": "message is required"})
    if mode not in MODE_IDS:
        return JSONResponse(status_code=400, content={"error": f"Invalid mode. Valid: {sorted(MODE_IDS)}"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    tutor_user_id = _get_tutor_user_id(request) if session_id else None
    if session_id and tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced for session persistence"})

    session_mode = mode
    grade_level = None

    # If session_id provided, verify ownership and get session mode/grade
    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "session_id must be an integer"})
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, mode, grade_level FROM tutor_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})
            if not body.get("mode"):
                session_mode = normalize_mode(row["mode"])
            grade_level = row["grade_level"]

    if hint_level is not None:
        try:
            hint_level = max(1, min(3, int(hint_level)))
        except (TypeError, ValueError):
            hint_level = 1
    else:
        hint_level = 1 if mode == "hint" else None

    from app.services import provider_registry

    if not provider_registry.registered_provider_names():
        return JSONResponse(
            status_code=503,
            content={"error": "No LLM provider configured. Set OPENAI_API_KEY for local chat."},
        )

    base_prompt = "You are a helpful tutor. Be clear, concise, and encouraging."
    if expert_id is not None:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, system_prompt FROM tutor_personas WHERE id = $1 AND is_active = TRUE",
                expert_id,
            )
            if row:
                base_prompt = row["system_prompt"] or base_prompt

    system_prompt = build_system_prompt(base_prompt, mode=session_mode, hint_level=hint_level, grade_level=grade_level)

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

    # Persist messages when session_id provided
    if session_id is not None and db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO tutor_messages (session_id, role, content, mode, hint_level, tokens_used, model_used)
                    VALUES ($1, 'user', $2, $3, $4, $5, $6)
                    """,
                    session_id,
                    message,
                    session_mode,
                    hint_level,
                    provider.count_tokens(message),
                    model_config.model,
                )
                await conn.execute(
                    """
                    INSERT INTO tutor_messages (session_id, role, content, mode, hint_level, tokens_used, model_used)
                    VALUES ($1, 'assistant', $2, $3, $4, $5, $6)
                    """,
                    session_id,
                    full_response,
                    session_mode,
                    hint_level,
                    provider.count_tokens(full_response),
                    model_config.model,
                )
                await conn.execute(
                    """
                    UPDATE tutor_sessions
                    SET tokens_used = COALESCE(tokens_used, 0) + $2, model_used = $3
                    WHERE id = $1
                    """,
                    session_id,
                    tokens_used,
                    model_config.model,
                )
        except Exception:
            pass

    return {"response": full_response, "tokens_used": tokens_used, "session_id": session_id}


def _sse_event(event: str, data: dict | str) -> bytes:
    """Format an SSE event."""
    payload = json.dumps(data) if isinstance(data, dict) else data
    return f"event: {event}\ndata: {payload}\n\n".encode("utf-8")


@router.post("/expert-chat/stream")
async def expert_chat_stream(request: Request):
    """Local streaming chat: streams tokens via SSE, deducts credits and persists messages when done."""
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
    session_id = body.get("session_id")
    mode = (body.get("mode") or "").strip().lower() or "teach_me"
    hint_level = body.get("hint_level")
    conversation = body.get("conversation") or []

    if not message:
        return JSONResponse(status_code=400, content={"error": "message is required"})
    if mode not in MODE_IDS:
        return JSONResponse(status_code=400, content={"error": f"Invalid mode. Valid: {sorted(MODE_IDS)}"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    tutor_user_id = _get_tutor_user_id(request) if session_id else None
    if session_id and tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced for session persistence"})

    session_mode = mode
    grade_level = None

    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "session_id must be an integer"})
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, mode, grade_level FROM tutor_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})
            if not body.get("mode"):
                session_mode = normalize_mode(row["mode"])
            grade_level = row["grade_level"]

    if hint_level is not None:
        try:
            hint_level = max(1, min(3, int(hint_level)))
        except (TypeError, ValueError):
            hint_level = 1
    else:
        hint_level = 1 if mode == "hint" else None

    from app.services import provider_registry

    if not provider_registry.registered_provider_names():
        return JSONResponse(
            status_code=503,
            content={"error": "No LLM provider configured. Set OPENAI_API_KEY for local chat."},
        )

    base_prompt = "You are a helpful tutor. Be clear, concise, and encouraging."
    if expert_id is not None:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, name, system_prompt FROM tutor_personas WHERE id = $1 AND is_active = TRUE",
                expert_id,
            )
            if row:
                base_prompt = row["system_prompt"] or base_prompt

    system_prompt = build_system_prompt(base_prompt, mode=session_mode, hint_level=hint_level, grade_level=grade_level)

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

    async def stream_generator():
        full_response = ""
        try:
            yield _sse_event("stream_start", {"session_id": session_id})
            async for chunk in provider.stream_chat(messages, model_config):
                full_response += chunk
                yield _sse_event("token", {"content": chunk})
        except Exception as e:
            yield _sse_event("error", {"message": str(e)})
            return

        tokens_used = provider.count_tokens(message) + provider.count_tokens(full_response)
        try:
            await root_site_client.deduct_credits(
                token,
                tokens=tokens_used,
                action="reconcile",
                metadata={"source": "tutor_expert_chat_stream", "model": model_config.model},
            )
        except Exception:
            pass

        if session_id is not None and db_pool:
            try:
                async with db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO tutor_messages (session_id, role, content, mode, hint_level, tokens_used, model_used)
                        VALUES ($1, 'user', $2, $3, $4, $5, $6)
                        """,
                        session_id,
                        message,
                        session_mode,
                        hint_level,
                        provider.count_tokens(message),
                        model_config.model,
                    )
                    await conn.execute(
                        """
                        INSERT INTO tutor_messages (session_id, role, content, mode, hint_level, tokens_used, model_used)
                        VALUES ($1, 'assistant', $2, $3, $4, $5, $6)
                        """,
                        session_id,
                        full_response,
                        session_mode,
                        hint_level,
                        provider.count_tokens(full_response),
                        model_config.model,
                    )
                    await conn.execute(
                        """
                        UPDATE tutor_sessions
                        SET tokens_used = COALESCE(tokens_used, 0) + $2, model_used = $3
                        WHERE id = $1
                        """,
                        session_id,
                        tokens_used,
                        model_config.model,
                    )
            except Exception:
                pass

        yield _sse_event("stream_end", {"tokens_used": tokens_used, "session_id": session_id})

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
