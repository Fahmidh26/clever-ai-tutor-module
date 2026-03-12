from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.db.pool import close_db_pool, init_db_pool
from app.logging_config import configure_logging
from app.middleware.request_logging import request_logging_middleware
from app.middleware.tutor_guardrail import tutor_guardrail_middleware
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.experts import router as experts_router
from app.routers.flashcards import router as flashcards_router
from app.routers.health import router as health_router
from app.routers.hints import router as hints_router
from app.routers.mastery import router as mastery_router
from app.routers.proxy import router as proxy_router
from app.routers.quizzes import router as quizzes_router
from app.routers.modes import router as modes_router
from app.routers.sessions import router as sessions_router
from app.routers.teacher_classes import router as teacher_classes_router
from app.routers.teacher_kb import router as teacher_kb_router
from app.services.rate_limiter import close_rate_limiter, init_rate_limiter

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_pool(app)
    await init_rate_limiter(app)
    try:
        yield
    finally:
        await close_rate_limiter(app)
        await close_db_pool(app)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
    same_site="lax",
    https_only=False,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(tutor_guardrail_middleware)
app.middleware("http")(request_logging_middleware)

app.include_router(auth_router)
app.include_router(experts_router)
app.include_router(chat_router)
app.include_router(flashcards_router)
app.include_router(modes_router)
app.include_router(sessions_router)
app.include_router(hints_router)
app.include_router(mastery_router)
app.include_router(quizzes_router)
app.include_router(teacher_classes_router)
app.include_router(teacher_kb_router)
app.include_router(proxy_router)
app.include_router(health_router)


@app.get("/")
async def home():
    return RedirectResponse(url=settings.frontend_url, status_code=307)
