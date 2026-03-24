from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI

from app.config import settings

VALID_TUTOR_ROLES = {"student", "teacher", "parent", "admin"}
ROLE_PRIORITY = {
    "student": 1,
    "parent": 2,
    "teacher": 3,
    "admin": 4,
}


@dataclass
class TutorUserSyncError(Exception):
    message: str
    status_code: int = 500
    details: str | None = None

    def __str__(self) -> str:
        return self.message


@dataclass
class TutorUserSyncResult:
    tutor_user_id: int
    root_user_id: int
    role: str
    grade_level: int | None
    preferred_language: str
    first_login: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "tutor_user_id": self.tutor_user_id,
            "root_user_id": self.root_user_id,
            "role": self.role,
            "grade_level": self.grade_level,
            "preferred_language": self.preferred_language,
            "first_login": self.first_login,
        }


def _to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        trimmed = value.strip()
        if not trimmed:
            return None
        if trimmed.lstrip("-").isdigit():
            return int(trimmed)
    return None


def _candidate_objects(provider_user: dict[str, Any]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = [provider_user]
    for key in ("user", "data", "profile", "result"):
        nested = provider_user.get(key)
        if isinstance(nested, dict):
            candidates.append(nested)
            nested_user = nested.get("user")
            if isinstance(nested_user, dict):
                candidates.append(nested_user)
    return candidates


def _extract_root_user_id(provider_user: dict[str, Any]) -> int | None:
    for obj in _candidate_objects(provider_user):
        for key in ("root_user_id", "id", "user_id", "uid", "sub", "userId", "user-id"):
            candidate = _to_int(obj.get(key))
            if candidate is not None and candidate > 0:
                return candidate
    return None


def _extract_display_name(provider_user: dict[str, Any]) -> str | None:
    for obj in _candidate_objects(provider_user):
        for key in ("display_name", "name", "full_name", "username"):
            value = obj.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    for obj in _candidate_objects(provider_user):
        email = obj.get("email")
        if isinstance(email, str) and email.strip():
            return email.split("@", maxsplit=1)[0].strip() or None
    return None


def _extract_role(provider_user: dict[str, Any]) -> str | None:
    role_aliases = {
        "admin": "admin",
        "administrator": "admin",
        "superadmin": "admin",
        "super_admin": "admin",
        "teacher": "teacher",
        "instructor": "teacher",
        "educator": "teacher",
        "parent": "parent",
        "guardian": "parent",
        "student": "student",
        "learner": "student",
        "member": "student",
        "user": "student",
    }
    for obj in _candidate_objects(provider_user):
        if obj.get("is_admin") is True or obj.get("is_superuser") is True:
            return "admin"
        for key in ("role", "user_role", "account_role", "type"):
            raw_role = obj.get(key)
            if not isinstance(raw_role, str):
                continue
            normalized = raw_role.strip().lower()
            mapped = role_aliases.get(normalized, normalized)
            if mapped in VALID_TUTOR_ROLES:
                return mapped
    return None


def _normalize_existing_role(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized in VALID_TUTOR_ROLES:
        return normalized
    return None


def _resolve_role_to_persist(provider_role: str | None, existing_role: str | None) -> str:
    if provider_role is None and existing_role is None:
        return "student"
    if provider_role is None:
        return existing_role or "student"
    if existing_role is None:
        return provider_role
    if ROLE_PRIORITY[provider_role] >= ROLE_PRIORITY[existing_role]:
        return provider_role
    return existing_role


def _extract_grade_level(provider_user: dict[str, Any]) -> int | None:
    for obj in _candidate_objects(provider_user):
        for key in ("grade_level", "grade", "class_level"):
            grade_level = _to_int(obj.get(key))
            if grade_level is not None and 0 <= grade_level <= 12:
                return grade_level
    return None


def _extract_preferred_language(provider_user: dict[str, Any]) -> str:
    for obj in _candidate_objects(provider_user):
        for key in ("preferred_language", "language", "locale"):
            value = obj.get(key)
            if isinstance(value, str):
                normalized = value.strip().lower()
                if normalized:
                    return normalized[:10]
    return "en"


def _extract_interests(provider_user: dict[str, Any]) -> Any:
    for obj in _candidate_objects(provider_user):
        interests = obj.get("interests")
        if isinstance(interests, (dict, list)):
            return interests
        if isinstance(interests, str) and interests.strip():
            return [interests.strip()]
    return None


async def sync_tutor_user_on_login(app: FastAPI, provider_user: dict[str, Any]) -> TutorUserSyncResult:
    db_pool = getattr(app.state, "db_pool", None)
    if db_pool is None:
        raise TutorUserSyncError(
            message="Tutor user sync failed because database is not configured",
            status_code=503,
        )

    root_user_id = _extract_root_user_id(provider_user)
    print(f"DEBUG: provider_user keys: {list(provider_user.keys())}")
    print(f"DEBUG: root_user_id extracted: {root_user_id}")

    # NOTE: In local dev mode we may not have a proper root user id coming from the main site.
    # To keep the tutor app functioning for dev/testing, default to a stable fallback id.
    if root_user_id is None and settings.app_env == "development":
        root_user_id = 1
        print("DEBUG: defaulting root_user_id to 1 (development fallback)")

    if root_user_id is None:
        details = "Expected one of: root_user_id, id, user_id, uid"
        if settings.app_env == "development":
            details = f"{details}; got keys: {list(provider_user.keys())}; sample: {dict(list(provider_user.items())[:10])}"
        raise TutorUserSyncError(
            message="Tutor user sync failed because root user id is missing",
            status_code=502,
            details=details,
        )

    display_name = _extract_display_name(provider_user)
    provider_role = _extract_role(provider_user)
    grade_level = _extract_grade_level(provider_user)
    preferred_language = _extract_preferred_language(provider_user)
    interests_json = _extract_interests(provider_user)

    async with db_pool.acquire() as connection:
        async with connection.transaction():
            existing_user = await connection.fetchrow(
                "SELECT id, role FROM tutor_users WHERE root_user_id = $1",
                root_user_id,
            )
            existing_id = int(existing_user["id"]) if existing_user else None
            existing_role = _normalize_existing_role(existing_user["role"]) if existing_user else None
            role = _resolve_role_to_persist(provider_role, existing_role)

            record = await connection.fetchrow(
                """
                INSERT INTO tutor_users (
                    root_user_id,
                    role,
                    display_name,
                    grade_level,
                    preferred_language,
                    interests_json,
                    onboarded_at
                )
                VALUES ($1, $2, $3, $4, $5, $6, NOW())
                ON CONFLICT (root_user_id) DO UPDATE SET
                    role = EXCLUDED.role,
                    display_name = COALESCE(EXCLUDED.display_name, tutor_users.display_name),
                    grade_level = COALESCE(EXCLUDED.grade_level, tutor_users.grade_level),
                    preferred_language = COALESCE(EXCLUDED.preferred_language, tutor_users.preferred_language),
                    interests_json = COALESCE(EXCLUDED.interests_json, tutor_users.interests_json),
                    updated_at = NOW()
                RETURNING id, root_user_id, role, grade_level, preferred_language
                """,
                root_user_id,
                role,
                display_name,
                grade_level,
                preferred_language,
                interests_json,
            )

    if record is None:
        raise TutorUserSyncError(message="Tutor user sync failed unexpectedly", status_code=500)

    return TutorUserSyncResult(
        tutor_user_id=int(record["id"]),
        root_user_id=int(record["root_user_id"]),
        role=str(record["role"]),
        grade_level=record["grade_level"],
        preferred_language=str(record["preferred_language"]),
        first_login=existing_id is None,
    )
