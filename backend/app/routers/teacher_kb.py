"""
Teacher KB API (Phase 1.4 starter): create/list KBs and upload/list/delete/preview documents.
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path

from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import JSONResponse

from app.config import settings
from app.services.rate_limiter import enforce_user_rate_limit
from app.services.rbac import evaluate_access

router = APIRouter(prefix="/api/teacher/kb", tags=["teacher-kb"])

_ALLOWED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".txt", ".md"}
_SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9._ -]+")


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


def _require_teacher_or_admin(request: Request) -> JSONResponse | None:
    user = request.session.get("user")
    decision = evaluate_access(user, ["teacher", "admin"])
    if not decision.allowed:
        return JSONResponse(
            status_code=403,
            content={"error": "Teacher or admin role required", "access": decision.as_dict()},
        )
    return None


def _safe_filename(original_name: str) -> str:
    cleaned = _SAFE_NAME_RE.sub("_", (original_name or "").strip())
    return cleaned[:220] or f"document-{uuid.uuid4().hex[:8]}.bin"


@router.post("")
async def create_kb(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    try:
        body = await request.json()
    except Exception:
        body = {}

    name = (body.get("name") or "").strip()
    if not name:
        return JSONResponse(status_code=400, content={"error": "name is required"})

    description = (body.get("description") or "").strip() or None
    subject = (body.get("subject") or "").strip() or None
    visibility = (body.get("visibility") or "private").strip().lower()
    if visibility not in {"private", "class", "public"}:
        return JSONResponse(status_code=400, content={"error": "visibility must be private, class, or public"})

    grade_level_raw = body.get("grade_level")
    grade_level = None
    if grade_level_raw is not None and str(grade_level_raw).strip() != "":
        try:
            grade_level = int(grade_level_raw)
        except (TypeError, ValueError):
            return JSONResponse(status_code=400, content={"error": "grade_level must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO knowledge_bases (owner_id, name, description, subject, grade_level, visibility, status)
                VALUES ($1, $2, $3, $4, $5, $6, 'active')
                RETURNING id, owner_id, name, description, subject, grade_level, visibility, status, created_at, updated_at
                """,
                tutor_user_id,
                name,
                description,
                subject,
                grade_level,
                visibility,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to create knowledge base", "details": str(exc)})

    return {
        "kb": {
            "id": row["id"],
            "owner_id": row["owner_id"],
            "name": row["name"],
            "description": row["description"],
            "subject": row["subject"],
            "grade_level": row["grade_level"],
            "visibility": row["visibility"],
            "status": row["status"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }
    }


@router.get("")
async def list_kbs(request: Request):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT kb.id, kb.name, kb.description, kb.subject, kb.grade_level, kb.visibility, kb.status,
                       kb.created_at, kb.updated_at, COUNT(d.id) AS document_count
                FROM knowledge_bases kb
                LEFT JOIN kb_documents d ON d.kb_id = kb.id
                WHERE kb.owner_id = $1
                GROUP BY kb.id
                ORDER BY kb.updated_at DESC, kb.id DESC
                """,
                tutor_user_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to list knowledge bases", "details": str(exc)})

    return {
        "knowledge_bases": [
            {
                "id": row["id"],
                "name": row["name"],
                "description": row["description"],
                "subject": row["subject"],
                "grade_level": row["grade_level"],
                "visibility": row["visibility"],
                "status": row["status"],
                "document_count": int(row["document_count"] or 0),
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
            }
            for row in rows
        ]
    }


@router.post("/{kb_id:int}/documents/upload")
async def upload_kb_document(request: Request, kb_id: int, file: UploadFile = File(...)):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    original_name = file.filename or "document.bin"
    ext = Path(original_name).suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        return JSONResponse(
            status_code=400,
            content={"error": f"Unsupported file type '{ext}'. Allowed: {sorted(_ALLOWED_EXTENSIONS)}"},
        )

    try:
        content = await file.read()
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Failed to read uploaded file"})

    size = len(content)
    if size == 0:
        return JSONResponse(status_code=400, content={"error": "Uploaded file is empty"})
    if size > settings.kb_upload_max_bytes:
        return JSONResponse(
            status_code=413,
            content={"error": f"File too large. Max bytes: {settings.kb_upload_max_bytes}"},
        )

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    safe_name = _safe_filename(original_name)
    relative_path = Path(str(kb_id)) / f"{uuid.uuid4().hex}_{safe_name}"
    disk_path = Path(settings.kb_upload_dir) / relative_path
    preview = None
    if ext in {".txt", ".md"}:
        preview = content[:1000].decode("utf-8", errors="ignore")

    try:
        async with db_pool.acquire() as conn:
            kb_row = await conn.fetchrow(
                "SELECT id FROM knowledge_bases WHERE id = $1 AND owner_id = $2 AND status = 'active'",
                kb_id,
                tutor_user_id,
            )
            if not kb_row:
                return JSONResponse(status_code=404, content={"error": "Knowledge base not found"})

            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_bytes(content)

            row = await conn.fetchrow(
                """
                INSERT INTO kb_documents (kb_id, filename, file_path, file_type, file_size, status, extracted_text_preview)
                VALUES ($1, $2, $3, $4, $5, 'queued', $6)
                RETURNING id, kb_id, filename, file_path, file_type, file_size, status, extracted_text_preview, created_at
                """,
                kb_id,
                original_name,
                str(relative_path).replace("\\", "/"),
                ext.lstrip("."),
                size,
                preview,
            )
            await conn.execute(
                "UPDATE knowledge_bases SET updated_at = NOW() WHERE id = $1",
                kb_id,
            )
    except Exception as exc:
        try:
            if disk_path.exists():
                disk_path.unlink()
        except Exception:
            pass
        return JSONResponse(status_code=500, content={"error": "Failed to store document", "details": str(exc)})

    return {
        "document": {
            "id": row["id"],
            "kb_id": row["kb_id"],
            "filename": row["filename"],
            "file_path": row["file_path"],
            "file_type": row["file_type"],
            "file_size": int(row["file_size"] or 0),
            "status": row["status"],
            "preview": row["extracted_text_preview"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
        }
    }


@router.get("/{kb_id:int}/documents")
async def list_kb_documents(request: Request, kb_id: int):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            owner_row = await conn.fetchrow(
                "SELECT id FROM knowledge_bases WHERE id = $1 AND owner_id = $2",
                kb_id,
                tutor_user_id,
            )
            if not owner_row:
                return JSONResponse(status_code=404, content={"error": "Knowledge base not found"})

            rows = await conn.fetch(
                """
                SELECT id, kb_id, filename, file_path, file_type, file_size, status, page_count, extracted_text_preview, error_message, created_at
                FROM kb_documents
                WHERE kb_id = $1
                ORDER BY id DESC
                """,
                kb_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to list documents", "details": str(exc)})

    return {
        "documents": [
            {
                "id": row["id"],
                "kb_id": row["kb_id"],
                "filename": row["filename"],
                "file_path": row["file_path"],
                "file_type": row["file_type"],
                "file_size": int(row["file_size"] or 0),
                "status": row["status"],
                "page_count": row["page_count"],
                "preview": row["extracted_text_preview"],
                "error_message": row["error_message"],
                "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            }
            for row in rows
        ]
    }


@router.get("/{kb_id:int}/documents/{document_id:int}/preview")
async def get_kb_document_preview(request: Request, kb_id: int, document_id: int):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT d.id, d.kb_id, d.filename, d.file_type, d.file_path, d.extracted_text_preview
                FROM kb_documents d
                JOIN knowledge_bases kb ON kb.id = d.kb_id
                WHERE d.id = $1 AND d.kb_id = $2 AND kb.owner_id = $3
                """,
                document_id,
                kb_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Document not found"})
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch document preview", "details": str(exc)})

    preview = row["extracted_text_preview"]
    if not preview and str(row["file_type"]).lower() in {"txt", "md"}:
        path = Path(settings.kb_upload_dir) / str(row["file_path"])
        if path.exists():
            try:
                preview = path.read_text(encoding="utf-8", errors="ignore")[:2000]
            except Exception:
                preview = None

    return {
        "document": {
            "id": row["id"],
            "kb_id": row["kb_id"],
            "filename": row["filename"],
            "file_type": row["file_type"],
            "preview": preview,
        }
    }


@router.delete("/{kb_id:int}/documents/{document_id:int}")
async def delete_kb_document(request: Request, kb_id: int, document_id: int):
    rate_limit_response = await enforce_user_rate_limit(
        request,
        endpoint_key=f"{request.method}:{request.url.path}",
    )
    if rate_limit_response is not None:
        return rate_limit_response

    token = request.session.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    role_response = _require_teacher_or_admin(request)
    if role_response is not None:
        return role_response

    tutor_user_id = _get_tutor_user_id(request)
    if tutor_user_id is None:
        return JSONResponse(status_code=401, content={"error": "Tutor user not synced"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT d.id, d.file_path
                FROM kb_documents d
                JOIN knowledge_bases kb ON kb.id = d.kb_id
                WHERE d.id = $1 AND d.kb_id = $2 AND kb.owner_id = $3
                """,
                document_id,
                kb_id,
                tutor_user_id,
            )
            if not row:
                return JSONResponse(status_code=404, content={"error": "Document not found"})

            await conn.execute("DELETE FROM kb_documents WHERE id = $1", document_id)
            await conn.execute("UPDATE knowledge_bases SET updated_at = NOW() WHERE id = $1", kb_id)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to delete document", "details": str(exc)})

    path = Path(settings.kb_upload_dir) / str(row["file_path"])
    try:
        if path.exists():
            path.unlink()
    except Exception:
        pass

    return {"ok": True, "document_id": document_id, "kb_id": kb_id}

