from __future__ import annotations

from dataclasses import dataclass
from typing import Any


VALID_ROLES = {"student", "teacher", "parent", "admin"}


@dataclass(frozen=True)
class AccessDecision:
    allowed: bool
    required_roles: list[str]
    user_role: str | None
    reason: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "allowed": self.allowed,
            "required_roles": self.required_roles,
            "user_role": self.user_role,
            "reason": self.reason,
        }


def resolve_user_role(user: dict[str, Any] | None) -> str | None:
    if not isinstance(user, dict):
        return None

    tutor_user = user.get("tutor_user")
    if isinstance(tutor_user, dict):
        tutor_role = tutor_user.get("role")
        if isinstance(tutor_role, str):
            normalized = tutor_role.strip().lower()
            if normalized in VALID_ROLES:
                return normalized

    user_role = user.get("role")
    if isinstance(user_role, str):
        normalized = user_role.strip().lower()
        if normalized in VALID_ROLES:
            return normalized
    return None


def required_roles_for_proxy_path(path: str) -> list[str]:
    normalized = f"/{path.lstrip('/')}".lower()
    if normalized.startswith("/api/admin"):
        return ["admin"]
    if normalized.startswith("/api/teacher"):
        return ["teacher", "admin"]
    if normalized.startswith("/api/parent"):
        return ["parent", "admin"]
    return []


def evaluate_access(user: dict[str, Any] | None, required_roles: list[str]) -> AccessDecision:
    user_role = resolve_user_role(user)
    if not required_roles:
        return AccessDecision(allowed=True, required_roles=[], user_role=user_role)

    normalized_required = [role for role in required_roles if role in VALID_ROLES]
    if not normalized_required:
        return AccessDecision(
            allowed=False,
            required_roles=[],
            user_role=user_role,
            reason="RBAC misconfiguration: invalid required roles",
        )
    if user_role is None:
        return AccessDecision(
            allowed=False,
            required_roles=normalized_required,
            user_role=None,
            reason="No role available for authenticated user",
        )
    if user_role in normalized_required:
        return AccessDecision(
            allowed=True,
            required_roles=normalized_required,
            user_role=user_role,
        )
    return AccessDecision(
        allowed=False,
        required_roles=normalized_required,
        user_role=user_role,
        reason="Role does not have access",
    )
