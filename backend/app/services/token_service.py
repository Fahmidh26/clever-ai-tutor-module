from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.services.root_site_client import RootSiteClient, RootSiteClientError


@dataclass
class TokenEstimate:
    estimated_input_tokens: int
    estimated_output_tokens: int
    estimated_total_tokens: int
    reserved_tokens: int


@dataclass
class CreditReservation:
    reserved_tokens: int
    response: dict[str, Any]
    reservation_id: str | None = None


class TokenServiceError(Exception):
    pass


class TokenService:
    def __init__(
        self,
        root_site_client: RootSiteClient,
        *,
        chars_per_token: int = 4,
        reserve_buffer_ratio: float = 1.15,
        default_output_tokens: int = 512,
    ) -> None:
        self._root_site_client = root_site_client
        self._chars_per_token = max(1, chars_per_token)
        self._reserve_buffer_ratio = max(1.0, reserve_buffer_ratio)
        self._default_output_tokens = max(1, default_output_tokens)

    def estimate_tokens(
        self,
        *,
        prompt: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        expected_output_tokens: int | None = None,
    ) -> TokenEstimate:
        normalized_text = self._normalize_input(prompt=prompt, messages=messages)
        estimated_input_tokens = max(1, len(normalized_text) // self._chars_per_token)
        estimated_output = max(1, expected_output_tokens or self._default_output_tokens)
        estimated_total = estimated_input_tokens + estimated_output
        reserved_tokens = max(1, int(estimated_total * self._reserve_buffer_ratio))
        return TokenEstimate(
            estimated_input_tokens=estimated_input_tokens,
            estimated_output_tokens=estimated_output,
            estimated_total_tokens=estimated_total,
            reserved_tokens=reserved_tokens,
        )

    async def reserve_credits(
        self,
        access_token: str,
        *,
        reserved_tokens: int,
        metadata: dict[str, Any] | None = None,
    ) -> CreditReservation:
        safe_reserved_tokens = max(1, reserved_tokens)
        reservation_metadata = dict(metadata or {})
        reservation_metadata["reserved_tokens"] = safe_reserved_tokens
        try:
            response = await self._root_site_client.deduct_credits(
                access_token,
                tokens=safe_reserved_tokens,
                action="reserve",
                metadata=reservation_metadata,
            )
        except RootSiteClientError as exc:
            raise TokenServiceError(f"Failed to reserve credits: {exc.message}") from exc

        reservation_id = self._extract_reservation_id(response)
        return CreditReservation(
            reserved_tokens=safe_reserved_tokens,
            reservation_id=reservation_id,
            response=response,
        )

    async def reconcile_credits(
        self,
        access_token: str,
        *,
        actual_tokens: int,
        reserved_tokens: int,
        reservation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        safe_actual_tokens = max(1, actual_tokens)
        safe_reserved_tokens = max(1, reserved_tokens)
        reconcile_metadata = dict(metadata or {})
        reconcile_metadata["actual_tokens"] = safe_actual_tokens
        reconcile_metadata["reserved_tokens"] = safe_reserved_tokens
        reconcile_metadata["token_delta"] = safe_actual_tokens - safe_reserved_tokens
        if reservation_id:
            reconcile_metadata["reservation_id"] = reservation_id

        try:
            return await self._root_site_client.deduct_credits(
                access_token,
                tokens=safe_actual_tokens,
                action="reconcile",
                metadata=reconcile_metadata,
            )
        except RootSiteClientError as exc:
            raise TokenServiceError(f"Failed to reconcile credits: {exc.message}") from exc

    async def estimate_and_reserve(
        self,
        access_token: str,
        *,
        prompt: str | None = None,
        messages: list[dict[str, Any]] | None = None,
        expected_output_tokens: int | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[TokenEstimate, CreditReservation]:
        estimate = self.estimate_tokens(
            prompt=prompt,
            messages=messages,
            expected_output_tokens=expected_output_tokens,
        )
        reservation = await self.reserve_credits(
            access_token,
            reserved_tokens=estimate.reserved_tokens,
            metadata=metadata,
        )
        return estimate, reservation

    def _normalize_input(
        self,
        *,
        prompt: str | None,
        messages: list[dict[str, Any]] | None,
    ) -> str:
        parts: list[str] = []
        if prompt:
            parts.append(prompt)
        if messages:
            for message in messages:
                role = str(message.get("role", "user"))
                content = message.get("content")
                if isinstance(content, str):
                    content_text = content
                elif isinstance(content, list):
                    content_text = " ".join(str(chunk) for chunk in content)
                else:
                    content_text = str(content or "")
                parts.append(f"{role}: {content_text}")

        normalized = "\n".join(parts).strip()
        if not normalized:
            return "placeholder"
        return normalized

    def _extract_reservation_id(self, response: dict[str, Any]) -> str | None:
        candidate_keys = ("reservation_id", "id", "transaction_id", "deduction_id")
        for key in candidate_keys:
            value = response.get(key)
            if value is not None:
                return str(value)
        return None

