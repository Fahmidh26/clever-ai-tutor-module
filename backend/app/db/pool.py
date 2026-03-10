from __future__ import annotations

import asyncpg
from fastapi import FastAPI

from app.config import settings


async def init_db_pool(app: FastAPI) -> None:
    if not settings.database_url:
        app.state.db_pool = None
        return

    app.state.db_pool = await asyncpg.create_pool(
        dsn=settings.database_url,
        min_size=settings.db_pool_min_size,
        max_size=settings.db_pool_max_size,
    )


async def close_db_pool(app: FastAPI) -> None:
    db_pool = getattr(app.state, "db_pool", None)
    if db_pool is not None:
        await db_pool.close()
        app.state.db_pool = None


async def db_healthcheck(app: FastAPI) -> dict[str, str]:
    db_pool = getattr(app.state, "db_pool", None)
    if db_pool is None:
        return {"status": "not_configured"}

    try:
        async with db_pool.acquire() as connection:
            await connection.fetchval("SELECT 1")
        return {"status": "ok"}
    except Exception:
        return {"status": "error"}
