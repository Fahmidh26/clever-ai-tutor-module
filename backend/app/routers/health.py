from __future__ import annotations

from fastapi import APIRouter, Request

from app.db.pool import db_healthcheck

router = APIRouter(tags=["health"])


@router.get("/api/health")
@router.get("/health")
async def health(request: Request):
    db = await db_healthcheck(request.app)
    app_ok = db["status"] in {"ok", "not_configured"}
    return {"ok": app_ok, "db": db}
