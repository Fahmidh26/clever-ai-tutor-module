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
from app.services.kb_pipeline import KBPipelineError, chunk_text, clean_text, embed_chunks, extract_text_from_document
from app.services.rag_retrieval import retrieve_kb_context
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


def _vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{float(v):.8f}" for v in values) + "]"


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


@router.get("/{kb_id:int}/assignments")
async def list_kb_assignments(request: Request, kb_id: int):
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
            kb_row = await conn.fetchrow(
                "SELECT id FROM knowledge_bases WHERE id = $1 AND owner_id = $2",
                kb_id,
                tutor_user_id,
            )
            if not kb_row:
                return JSONResponse(status_code=404, content={"error": "Knowledge base not found"})

            rows = await conn.fetch(
                """
                SELECT c.id, c.name, c.subject, c.grade_level, c.invite_code,
                       COUNT(DISTINCT e.id) AS roster_count
                FROM kb_class_assignments a
                JOIN classes c ON c.id = a.class_id
                LEFT JOIN class_enrollments e ON e.class_id = c.id AND e.status = 'active'
                WHERE a.kb_id = $1 AND c.teacher_id = $2
                GROUP BY c.id
                ORDER BY c.name ASC
                """,
                kb_id,
                tutor_user_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to fetch KB assignments", "details": str(exc)})

    return {
        "classes": [
            {
                "id": row["id"],
                "name": row["name"],
                "subject": row["subject"],
                "grade_level": row["grade_level"],
                "invite_code": row["invite_code"],
                "roster_count": int(row["roster_count"] or 0),
            }
            for row in rows
        ]
    }


@router.post("/{kb_id:int}/assignments")
async def assign_kb_to_class(request: Request, kb_id: int):
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
    class_id_raw = body.get("class_id")
    try:
        class_id = int(class_id_raw)
    except (TypeError, ValueError):
        return JSONResponse(status_code=400, content={"error": "class_id must be an integer"})

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            kb_row = await conn.fetchrow(
                "SELECT id FROM knowledge_bases WHERE id = $1 AND owner_id = $2",
                kb_id,
                tutor_user_id,
            )
            if not kb_row:
                return JSONResponse(status_code=404, content={"error": "Knowledge base not found"})
            class_row = await conn.fetchrow(
                "SELECT id FROM classes WHERE id = $1 AND teacher_id = $2",
                class_id,
                tutor_user_id,
            )
            if not class_row:
                return JSONResponse(status_code=404, content={"error": "Class not found"})

            await conn.execute(
                """
                INSERT INTO kb_class_assignments (kb_id, class_id)
                VALUES ($1, $2)
                ON CONFLICT (kb_id, class_id) DO NOTHING
                """,
                kb_id,
                class_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to assign KB to class", "details": str(exc)})

    return {"ok": True, "kb_id": kb_id, "class_id": class_id}


@router.delete("/{kb_id:int}/assignments/{class_id:int}")
async def remove_kb_assignment(request: Request, kb_id: int, class_id: int):
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
            result = await conn.execute(
                """
                DELETE FROM kb_class_assignments a
                USING knowledge_bases kb, classes c
                WHERE a.kb_id = $1
                  AND a.class_id = $2
                  AND kb.id = a.kb_id
                  AND c.id = a.class_id
                  AND kb.owner_id = $3
                  AND c.teacher_id = $3
                """,
                kb_id,
                class_id,
                tutor_user_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to remove KB assignment", "details": str(exc)})

    if not result.endswith("1"):
        return JSONResponse(status_code=404, content={"error": "Assignment not found"})
    return {"ok": True, "kb_id": kb_id, "class_id": class_id}


@router.post("/{kb_id:int}/documents/{document_id:int}/process")
async def process_kb_document(request: Request, kb_id: int, document_id: int):
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
                SELECT d.id, d.kb_id, d.file_path, d.file_type
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
            await conn.execute(
                "UPDATE kb_documents SET status = 'processing', error_message = NULL WHERE id = $1",
                document_id,
            )
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to start processing", "details": str(exc)})

    file_path = Path(settings.kb_upload_dir) / str(row["file_path"])
    if not file_path.exists():
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE kb_documents SET status = 'error', error_message = $2 WHERE id = $1",
                    document_id,
                    "Uploaded file not found on disk",
                )
        except Exception:
            pass
        return JSONResponse(status_code=404, content={"error": "Uploaded file not found on disk"})

    try:
        extracted = extract_text_from_document(file_path, str(row["file_type"] or ""))
        extracted = clean_text(extracted)
        chunks = chunk_text(
            extracted,
            chunk_size=settings.kb_chunk_size_chars,
            chunk_overlap=settings.kb_chunk_overlap_chars,
            max_chunks=settings.kb_max_chunks_per_document,
        )
        if not chunks:
            raise KBPipelineError("No extractable text found in document")
        vectors = await embed_chunks(chunks)
    except Exception as exc:
        message = str(exc)
        try:
            async with db_pool.acquire() as conn:
                await conn.execute(
                    "UPDATE kb_documents SET status = 'error', error_message = $2 WHERE id = $1",
                    document_id,
                    message[:1000],
                )
        except Exception:
            pass
        return JSONResponse(status_code=422, content={"error": "Document processing failed", "details": message})

    try:
        async with db_pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute("DELETE FROM kb_chunks WHERE document_id = $1", document_id)
                for idx, (chunk, embedding) in enumerate(zip(chunks, vectors)):
                    await conn.execute(
                        """
                        INSERT INTO kb_chunks (document_id, kb_id, chunk_index, content, embedding, metadata_json)
                        VALUES ($1, $2, $3, $4, $5::vector, $6::jsonb)
                        """,
                        document_id,
                        kb_id,
                        idx,
                        chunk,
                        _vector_literal(embedding),
                        "{}",
                    )
                await conn.execute(
                    """
                    UPDATE kb_documents
                    SET status = 'ready',
                        extracted_text_preview = $2,
                        error_message = NULL
                    WHERE id = $1
                    """,
                    document_id,
                    extracted[:2000],
                )
                await conn.execute("UPDATE knowledge_bases SET updated_at = NOW() WHERE id = $1", kb_id)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to store processed chunks", "details": str(exc)})

    return {
        "ok": True,
        "kb_id": kb_id,
        "document_id": document_id,
        "status": "ready",
        "chunk_count": len(chunks),
        "embedding_model": settings.embedding_model,
    }


@router.post("/{kb_id:int}/documents/process-queued")
async def process_queued_kb_documents(request: Request, kb_id: int, limit: int = 10):
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

    limit = max(1, min(50, limit))
    async with db_pool.acquire() as conn:
        kb_row = await conn.fetchrow(
            "SELECT id FROM knowledge_bases WHERE id = $1 AND owner_id = $2",
            kb_id,
            tutor_user_id,
        )
        if not kb_row:
            return JSONResponse(status_code=404, content={"error": "Knowledge base not found"})
        rows = await conn.fetch(
            """
            SELECT id
            FROM kb_documents
            WHERE kb_id = $1 AND status IN ('queued', 'error')
            ORDER BY id ASC
            LIMIT $2
            """,
            kb_id,
            limit,
        )

    results: list[dict[str, object]] = []
    for row in rows:
        doc_id = int(row["id"])
        response = await process_kb_document(request=request, kb_id=kb_id, document_id=doc_id)
        if isinstance(response, JSONResponse):
            results.append({"document_id": doc_id, "status": "error"})
        else:
            results.append({"document_id": doc_id, "status": "ready", "chunk_count": response.get("chunk_count", 0)})

    return {"kb_id": kb_id, "processed": len(results), "results": results}


@router.post("/{kb_id:int}/retrieve")
async def retrieve_kb_chunks(request: Request, kb_id: int):
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

    query = (body.get("query") or "").strip()
    if not query:
        return JSONResponse(status_code=400, content={"error": "query is required"})
    top_k = body.get("top_k", 5)
    try:
        top_k = max(1, min(20, int(top_k)))
    except (TypeError, ValueError):
        top_k = 5

    db_pool = getattr(request.app.state, "db_pool", None)
    if db_pool is None:
        return JSONResponse(status_code=503, content={"error": "Database not configured"})

    try:
        async with db_pool.acquire() as conn:
            kb_row = await conn.fetchrow(
                "SELECT id FROM knowledge_bases WHERE id = $1 AND owner_id = $2",
                kb_id,
                tutor_user_id,
            )
            if not kb_row:
                return JSONResponse(status_code=404, content={"error": "Knowledge base not found"})

            reranked = await retrieve_kb_context(conn=conn, kb_id=kb_id, query=query, top_k=top_k)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": "Failed to retrieve chunks", "details": str(exc)})

    return {"kb_id": kb_id, "query": query, "top_k": top_k, "results": reranked}


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
