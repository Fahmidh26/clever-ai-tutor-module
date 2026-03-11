from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx

from app.services.ai_providers.base import BaseProvider, ChatMessage, ModelConfig, ProviderError


class AnthropicProvider(BaseProvider):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.anthropic.com",
        api_version: str = "2023-06-01",
        timeout_seconds: float = 60.0,
    ) -> None:
        super().__init__(
            provider_name="anthropic",
            supported_models=("claude-4-sonnet", "claude-4-haiku"),
        )
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._api_version = api_version
        self._timeout_seconds = timeout_seconds

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model_config: ModelConfig,
    ) -> AsyncGenerator[str, None]:
        self.assert_model_supported(model_config.model)
        system_prompt, non_system_messages = self._split_system_messages(messages)

        payload: dict[str, object] = {
            "model": model_config.model,
            "messages": self._serialize_messages(non_system_messages),
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "top_p": model_config.top_p,
            "stream": True,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if model_config.extra:
            payload.update(model_config.extra)

        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": self._api_version,
            "content-type": "application/json",
            "accept": "text/event-stream",
        }

        endpoint = f"{self._base_url}/v1/messages"
        timeout = model_config.timeout_seconds if model_config.timeout_seconds > 0 else self._timeout_seconds

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    if response.status_code >= 400:
                        body = await response.aread()
                        raise ProviderError(
                            f"Anthropic request failed ({response.status_code}): {body.decode('utf-8', errors='ignore')}"
                        )

                    async for line in response.aiter_lines():
                        chunk = self._parse_sse_chunk(line)
                        if chunk is None:
                            continue
                        yield chunk
            except httpx.HTTPError as exc:
                raise ProviderError(f"Anthropic streaming request failed: {exc}") from exc

    def count_tokens(self, text: str) -> int:
        normalized = (text or "").strip()
        if not normalized:
            return 1
        return max(1, len(normalized) // 4)

    def _split_system_messages(self, messages: list[ChatMessage]) -> tuple[str | None, list[ChatMessage]]:
        system_parts: list[str] = []
        non_system_messages: list[ChatMessage] = []

        for message in messages:
            if message.role == "system":
                content = message.content.strip()
                if content:
                    system_parts.append(content)
            else:
                non_system_messages.append(message)

        system_prompt = "\n\n".join(system_parts).strip() or None
        return system_prompt, non_system_messages

    def _serialize_messages(self, messages: list[ChatMessage]) -> list[dict[str, object]]:
        serialized: list[dict[str, object]] = []
        for message in messages:
            role = "assistant" if message.role == "assistant" else "user"
            serialized.append(
                {
                    "role": role,
                    "content": message.content,
                }
            )
        return serialized

    def _parse_sse_chunk(self, line: str) -> str | None:
        if not line or not line.startswith("data: "):
            return None

        data = line[len("data: ") :].strip()
        if not data or data == "[DONE]":
            return None

        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return None

        payload_type = payload.get("type")
        if payload_type == "content_block_delta":
            delta = payload.get("delta")
            if isinstance(delta, dict):
                text = delta.get("text")
                if isinstance(text, str) and text:
                    return text
        return None
