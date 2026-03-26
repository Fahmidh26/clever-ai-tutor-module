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
from app.services import provider_registry, root_site_client
from app.services.ai_providers.base import ChatMessage
from app.services.chat_execution import (
    collect_chat_with_strategy,
    start_stream_with_strategy,
    stream_remaining_chunks,
)
from app.services.mode_prompts import MODE_IDS, build_system_prompt, normalize_mode
from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rag_retrieval import retrieve_kb_context, retrieve_multi_kb_context
from app.services.safety_guardrails import sanitize_assistant_output

router = APIRouter(prefix="/api", tags=["chat"])


def _get_tutor_user_id(request: Request) -> int | None:
    user = request.session.get("user")
    if not user:
        return None


async def _resolve_rag_context(
    *,
    conn,
    tutor_user_id: int,
    message: str,
    requested_kb_id: int | None,
    session_class_id: int | None,
) -> tuple[int | None, list[dict[str, object]], str | None]:
    if requested_kb_id is not None:
        kb_row = await conn.fetchrow(
            """
            SELECT kb.id
            FROM knowledge_bases kb
            LEFT JOIN kb_class_assignments a ON a.kb_id = kb.id
            LEFT JOIN class_enrollments e
                   ON e.class_id = a.class_id
                  AND e.student_id = $2
                  AND e.status = 'active'
            WHERE kb.id = $1
              AND kb.status = 'active'
              AND (
                    kb.owner_id = $2
                    OR kb.visibility = 'public'
                    OR e.student_id IS NOT NULL
                  )
            LIMIT 1
            """,
            requested_kb_id,
            tutor_user_id,
        )
        if not kb_row:
            return None, [], "Knowledge base not found or not accessible"
        return requested_kb_id, await retrieve_kb_context(conn=conn, kb_id=requested_kb_id, query=message, top_k=4), None

    if session_class_id is None:
        return None, [], None

    class_kb_rows = await conn.fetch(
        """
        SELECT kb.id
        FROM kb_class_assignments a
        JOIN knowledge_bases kb ON kb.id = a.kb_id
        JOIN class_enrollments e ON e.class_id = a.class_id
        WHERE a.class_id = $1
          AND e.student_id = $2
          AND e.status = 'active'
          AND kb.status = 'active'
        ORDER BY kb.id ASC
        """,
        session_class_id,
        tutor_user_id,
    )
    class_kb_ids = [int(row["id"]) for row in class_kb_rows]
    if not class_kb_ids:
        return None, [], None

    citations = await retrieve_multi_kb_context(conn=conn, kb_ids=class_kb_ids, query=message, top_k=4)
    kb_id = int(citations[0]["kb_id"]) if citations else class_kb_ids[0]
    return kb_id, citations, None
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
    kb_id = body.get("kb_id")
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
    rag_citations: list[dict[str, object]] = []

    # If session_id provided, verify ownership and get session mode/grade
    session_class_id = None
    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "session_id must be an integer"})
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, mode, grade_level, class_id FROM tutor_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})
            if not body.get("mode"):
                session_mode = normalize_mode(row["mode"])
            grade_level = row["grade_level"]
            session_class_id = row["class_id"]

    if hint_level is not None:
        try:
            hint_level = max(1, min(3, int(hint_level)))
        except (TypeError, ValueError):
            hint_level = 1
    else:
        hint_level = 1 if mode == "hint" else None

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

    tutor_user_for_kb = _get_tutor_user_id(request)
    if kb_id is not None:
        if tutor_user_for_kb is None:
            return JSONResponse(status_code=401, content={"error": "Tutor user not synced for KB retrieval"})
        try:
            kb_id = int(kb_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "kb_id must be an integer"})

    if tutor_user_for_kb is not None:
        async with db_pool.acquire() as conn:
            resolved_kb_id, rag_citations, rag_error = await _resolve_rag_context(
                conn=conn,
                tutor_user_id=tutor_user_for_kb,
                message=message,
                requested_kb_id=kb_id,
                session_class_id=session_class_id,
            )
        if rag_error:
            return JSONResponse(status_code=404, content={"error": rag_error})
        kb_id = resolved_kb_id

        if rag_citations:
            context_block = "\n\n".join(
                f"[{idx + 1}] {item['content']}" for idx, item in enumerate(rag_citations)
            )
            system_prompt = (
                f"{system_prompt}\n\n"
                f"RAG CONTEXT (teacher knowledge base id={kb_id}):\n{context_block}\n\n"
                "When using RAG context, cite source chunks inline like [1], [2]."
            )

    messages: list[ChatMessage] = [ChatMessage(role="system", content=system_prompt)]
    for item in conversation:
        if isinstance(item, dict):
            role = item.get("role", "user")
            content = item.get("content", "") or item.get("message", "")
            if content:
                messages.append(ChatMessage(role=str(role), content=str(content)))
    messages.append(ChatMessage(role="user", content=message))

    provider_name = "openai"
    selected_model = settings.openai_default_model
    attempts: list[dict[str, object]] = []
    try:
        full_response, selected_model, attempts = await collect_chat_with_strategy(
            provider_registry=provider_registry,
            provider_name=provider_name,
            messages=messages,
            primary_model=settings.openai_default_model,
            fallback_models=settings.llm_fallback_models_list,
            temperature=0.2,
            max_tokens=1024,
            timeout_seconds=settings.llm_request_timeout_seconds,
            retry_attempts=settings.llm_retry_attempts,
            retry_backoff_seconds=settings.llm_retry_backoff_seconds,
        )
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={
                "error": "LLM request failed after retries/fallback",
                "details": str(e),
                "attempts": attempts,
            },
        )
    full_response = sanitize_assistant_output(full_response)

    provider = provider_registry.get_provider(provider_name)
    tokens_used = provider.count_tokens(message) + provider.count_tokens(full_response)
    try:
        await root_site_client.deduct_credits(
            token,
            tokens=tokens_used,
            action="reconcile",
            metadata={"source": "tutor_expert_chat", "model": selected_model},
        )
    except Exception:
        pass

    # Persist messages when session_id provided
    if session_id is not None and db_pool:
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO tutor_messages (session_id, kb_id, role, content, mode, hint_level, tokens_used, model_used)
                    VALUES ($1, $2, 'user', $3, $4, $5, $6, $7)
                    """,
                    session_id,
                    kb_id,
                    message,
                    session_mode,
                    hint_level,
                    provider.count_tokens(message),
                    selected_model,
                )
                await conn.execute(
                    """
                    INSERT INTO tutor_messages (session_id, kb_id, role, content, mode, hint_level, tokens_used, model_used)
                    VALUES ($1, $2, 'assistant', $3, $4, $5, $6, $7)
                    """,
                    session_id,
                    kb_id,
                    full_response,
                    session_mode,
                    hint_level,
                    provider.count_tokens(full_response),
                    selected_model,
                )
                await conn.execute(
                    """
                    UPDATE tutor_sessions
                    SET tokens_used = COALESCE(tokens_used, 0) + $2, model_used = $3
                    WHERE id = $1
                    """,
                    session_id,
                    tokens_used,
                    selected_model,
                )
        except Exception:
            pass

    return {
        "response": full_response,
        "tokens_used": tokens_used,
        "session_id": session_id,
        "model_used": selected_model,
        "execution_attempts": attempts,
        "citations": [
            {
                "citation": item["citation"],
                "filename": item["filename"],
                "document_id": item["document_id"],
                "chunk_index": item["chunk_index"],
            }
            for item in rag_citations
        ],
    }


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
    kb_id = body.get("kb_id")
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
    rag_citations: list[dict[str, object]] = []

    session_class_id = None
    if session_id is not None:
        try:
            session_id = int(session_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "session_id must be an integer"})
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, mode, grade_level, class_id FROM tutor_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Session not found"})
            if not body.get("mode"):
                session_mode = normalize_mode(row["mode"])
            grade_level = row["grade_level"]
            session_class_id = row["class_id"]

    if hint_level is not None:
        try:
            hint_level = max(1, min(3, int(hint_level)))
        except (TypeError, ValueError):
            hint_level = 1
    else:
        hint_level = 1 if mode == "hint" else None

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

    tutor_user_for_kb = _get_tutor_user_id(request)
    if kb_id is not None:
        if tutor_user_for_kb is None:
            return JSONResponse(status_code=401, content={"error": "Tutor user not synced for KB retrieval"})
        try:
            kb_id = int(kb_id)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "kb_id must be an integer"})

    if tutor_user_for_kb is not None:
        async with db_pool.acquire() as conn:
            resolved_kb_id, rag_citations, rag_error = await _resolve_rag_context(
                conn=conn,
                tutor_user_id=tutor_user_for_kb,
                message=message,
                requested_kb_id=kb_id,
                session_class_id=session_class_id,
            )
        if rag_error:
            return JSONResponse(status_code=404, content={"error": rag_error})
        kb_id = resolved_kb_id

        if rag_citations:
            context_block = "\n\n".join(
                f"[{idx + 1}] {item['content']}" for idx, item in enumerate(rag_citations)
            )
            system_prompt = (
                f"{system_prompt}\n\n"
                f"RAG CONTEXT (teacher knowledge base id={kb_id}):\n{context_block}\n\n"
                "When using RAG context, cite source chunks inline like [1], [2]."
            )

    messages: list[ChatMessage] = [ChatMessage(role="system", content=system_prompt)]
    for item in conversation:
        if isinstance(item, dict):
            role = item.get("role", "user")
            content = item.get("content", "") or item.get("message", "")
            if content:
                messages.append(ChatMessage(role=str(role), content=str(content)))
    messages.append(ChatMessage(role="user", content=message))

    provider_name = "openai"
    provider = provider_registry.get_provider(provider_name)

    async def stream_generator():
        full_response = ""
        selected_model = settings.openai_default_model
        attempts: list[dict[str, object]] = []
        stream = None
        try:
            selection = await start_stream_with_strategy(
                provider_registry=provider_registry,
                provider_name=provider_name,
                messages=messages,
                primary_model=settings.openai_default_model,
                fallback_models=settings.llm_fallback_models_list,
                temperature=0.2,
                max_tokens=1024,
                timeout_seconds=settings.llm_request_timeout_seconds,
                retry_attempts=settings.llm_retry_attempts,
                retry_backoff_seconds=settings.llm_retry_backoff_seconds,
            )
            stream = selection.stream
            selected_model = selection.model
            attempts = selection.attempts

            yield _sse_event(
                "stream_start",
                {
                    "session_id": session_id,
                    "model_used": selected_model,
                    "execution_attempts": attempts,
                    "citations": [
                        {
                            "citation": item["citation"],
                            "filename": item["filename"],
                            "document_id": item["document_id"],
                            "chunk_index": item["chunk_index"],
                        }
                        for item in rag_citations
                    ],
                },
            )

            if selection.first_chunk:
                full_response += selection.first_chunk
                yield _sse_event("token", {"content": selection.first_chunk})

            async for chunk in stream_remaining_chunks(
                stream,
                timeout_seconds=settings.llm_request_timeout_seconds,
            ):
                full_response += chunk
                yield _sse_event("token", {"content": chunk})
        except Exception as e:
            yield _sse_event("error", {"message": str(e), "execution_attempts": attempts})
            return
        finally:
            if stream is not None:
                close = getattr(stream, "aclose", None)
                if callable(close):
                    try:
                        await close()
                    except Exception:
                        pass
        full_response = sanitize_assistant_output(full_response)

        tokens_used = provider.count_tokens(message) + provider.count_tokens(full_response)
        try:
            await root_site_client.deduct_credits(
                token,
                tokens=tokens_used,
                action="reconcile",
                metadata={"source": "tutor_expert_chat_stream", "model": selected_model},
            )
        except Exception:
            pass

        if session_id is not None and db_pool:
            try:
                async with db_pool.acquire() as conn:
                    await conn.execute(
                        """
                        INSERT INTO tutor_messages (session_id, kb_id, role, content, mode, hint_level, tokens_used, model_used)
                        VALUES ($1, $2, 'user', $3, $4, $5, $6, $7)
                        """,
                        session_id,
                        kb_id,
                        message,
                        session_mode,
                        hint_level,
                        provider.count_tokens(message),
                        selected_model,
                    )
                    await conn.execute(
                        """
                        INSERT INTO tutor_messages (session_id, kb_id, role, content, mode, hint_level, tokens_used, model_used)
                        VALUES ($1, $2, 'assistant', $3, $4, $5, $6, $7)
                        """,
                        session_id,
                        kb_id,
                        full_response,
                        session_mode,
                        hint_level,
                        provider.count_tokens(full_response),
                        selected_model,
                    )
                    await conn.execute(
                        """
                        UPDATE tutor_sessions
                        SET tokens_used = COALESCE(tokens_used, 0) + $2, model_used = $3
                        WHERE id = $1
                        """,
                        session_id,
                        tokens_used,
                        selected_model,
                    )
            except Exception:
                pass

        yield _sse_event(
            "stream_end",
            {
                "tokens_used": tokens_used,
                "session_id": session_id,
                "model_used": selected_model,
                "execution_attempts": attempts,
                "citations": [
                    {
                        "citation": item["citation"],
                        "filename": item["filename"],
                        "document_id": item["document_id"],
                        "chunk_index": item["chunk_index"],
                    }
                    for item in rag_citations
                ],
            },
        )

    return StreamingResponse(
        stream_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
