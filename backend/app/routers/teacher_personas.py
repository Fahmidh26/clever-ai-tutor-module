from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.rate_limiter import enforce_user_rate_limit
from app.services.teacher_access import get_tutor_user_id, require_roles

router = APIRouter(prefix="/api/teacher/personas", tags=["teacher-personas"])


@router.get("")
async def list_teacher_personas(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, slug, name, tagline, personality, system_prompt, teaching_style,
                       subject_expertise, is_custom, sort_order
                FROM tutor_personas
                WHERE is_active = TRUE
                ORDER BY is_custom ASC, sort_order ASC, id ASC
                """
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to list personas", "details": str(exc)})

    return {
        "personas": [
            {
                "id": row["id"],
                "slug": row["slug"],
                "name": row["name"],
                "tagline": row["tagline"],
                "personality": row["personality"],
                "system_prompt": row["system_prompt"],
                "teaching_style": row["teaching_style"],
                "subject_expertise": row["subject_expertise"],
                "is_custom": row["is_custom"],
            }
            for row in rows
        ]
    }


@router.get("/classes/{class_id:int}")
async def get_class_persona_policy(request: Request, class_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT c.id, c.name, c.persona_id, c.settings_json,
                       p.name AS persona_name, p.tagline, p.system_prompt, p.teaching_style
                FROM classes c
                LEFT JOIN tutor_personas p ON p.id = c.persona_id
                WHERE c.id = $1 AND c.teacher_id = $2
                """,
                class_id,
                teacher_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to load class persona policy", "details": str(exc)})

    if not row:
        return JSONResponse(status_code=404, content={"error": "Class not found"})

    settings_json = row["settings_json"] or {}
    overlay = settings_json.get("teacher_persona_overlay") if isinstance(settings_json, dict) else None

    return {
        "class": {"id": row["id"], "name": row["name"]},
        "policy": {
            "persona_id": row["persona_id"],
            "persona_name": row["persona_name"],
            "tagline": row["tagline"],
            "teaching_style": row["teaching_style"],
            "overlay_instructions": overlay,
            "effective_prompt_preview": "\n\n".join(
                part for part in [row["system_prompt"], overlay] if isinstance(part, str) and part.strip()
            ),
        },
    }


@router.post("/classes/{class_id:int}")
async def assign_class_persona_policy(request: Request, class_id: int):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    teacher_id = get_tutor_user_id(request)
    if teacher_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    try:
        persona_id = int(body.get("persona_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "persona_id must be an integer"})
    overlay_instructions = str(body.get("overlay_instructions") or "").strip() or None

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            persona_row = await conn.fetchrow(
                "SELECT id, name, system_prompt, teaching_style FROM tutor_personas WHERE id = $1 AND is_active = TRUE",
                persona_id,
            )
            if not persona_row:
                return JSONResponse(status_code=404, content={"error": "Persona not found"})

            class_row = await conn.fetchrow(
                "SELECT id, settings_json FROM classes WHERE id = $1 AND teacher_id = $2",
                class_id,
                teacher_id,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Class not found"})

            settings_json = class_row["settings_json"] or {}
            if not isinstance(settings_json, dict):
                settings_json = {}
            settings_json["teacher_persona_overlay"] = overlay_instructions

            await conn.execute(
                """
                UPDATE classes
                SET persona_id = $3,
                    settings_json = $4
                WHERE id = $1 AND teacher_id = $2
                """,
                class_id,
                teacher_id,
                persona_id,
                settings_json,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to assign persona policy", "details": str(exc)})

    preview_parts = [persona_row["system_prompt"]]
    if overlay_instructions:
        preview_parts.append(overlay_instructions)
    return {
        "ok": True,
        "class_id": class_id,
        "policy": {
            "persona_id": persona_id,
            "persona_name": persona_row["name"],
            "teaching_style": persona_row["teaching_style"],
            "overlay_instructions": overlay_instructions,
            "effective_prompt_preview": "\n\n".join(preview_parts),
        },
    }


@router.post("/preview")
async def preview_persona_policy(request: Request):
    rate_limit_response = await enforce_user_rate_limit(request, endpoint_key=f"{request.method}:{request.url.path}")
    if rate_limit_response is not None:
        return rate_limit_response

    _, role_response = require_roles(request, ["teacher", "admin"])
    if role_response is not None:
        return role_response

    try:
        body = await request.json()
    except Exception:
        body = {}

    try:
        persona_id = int(body.get("persona_id"))
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "persona_id must be an integer"})
    overlay_instructions = str(body.get("overlay_instructions") or "").strip() or None

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            persona_row = await conn.fetchrow(
                """
                SELECT id, name, tagline, personality, system_prompt, teaching_style
                FROM tutor_personas
                WHERE id = $1 AND is_active = TRUE
                """,
                persona_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to preview persona", "details": str(exc)})

    if not persona_row:
        return JSONResponse(status_code=404, content={"error": "Persona not found"})

    return {
        "preview": {
            "persona_id": persona_row["id"],
            "persona_name": persona_row["name"],
            "tagline": persona_row["tagline"],
            "teaching_style": persona_row["teaching_style"],
            "summary": f"{persona_row['name']} teaches in a {persona_row['teaching_style']} style.",
            "effective_prompt_preview": "\n\n".join(
                part for part in [persona_row["system_prompt"], overlay_instructions] if part
            ),
        }
    }
