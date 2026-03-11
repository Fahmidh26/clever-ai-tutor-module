from __future__ import annotations

import json
from collections.abc import AsyncGenerator

import httpx

from app.services.ai_providers.base import BaseProvider, ChatMessage, ModelConfig, ProviderError


class OpenAIProvider(BaseProvider):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = "https://api.openai.com",
        timeout_seconds: float = 60.0,
    ) -> None:
        super().__init__(
            provider_name="openai",
            supported_models=("gpt-4o", "gpt-4o-mini"),
        )
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model_config: ModelConfig,
    ) -> AsyncGenerator[str, None]:
        self.assert_model_supported(model_config.model)

        payload = {
            "model": model_config.model,
            "messages": self._serialize_messages(messages),
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
            "top_p": model_config.top_p,
            "stream": True,
        }
        if model_config.extra:
            payload.update(model_config.extra)

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        }

        endpoint = f"{self._base_url}/v1/chat/completions"
        timeout = model_config.timeout_seconds if model_config.timeout_seconds > 0 else self._timeout_seconds

        async with httpx.AsyncClient(timeout=timeout) as client:
            try:
                async with client.stream("POST", endpoint, headers=headers, json=payload) as response:
                    if response.status_code >= 400:
                        body = await response.aread()
                        raise ProviderError(
                            f"OpenAI request failed ({response.status_code}): {body.decode('utf-8', errors='ignore')}"
                        )

                    async for line in response.aiter_lines():
                        chunk = self._parse_sse_chunk(line)
                        if chunk is None:
                            continue
                        yield chunk
            except httpx.HTTPError as exc:
                raise ProviderError(f"OpenAI streaming request failed: {exc}") from exc

    def count_tokens(self, text: str) -> int:
        normalized = (text or "").strip()
        if not normalized:
            return 1
        return max(1, len(normalized) // 4)

    def _serialize_messages(self, messages: list[ChatMessage]) -> list[dict[str, str]]:
        serialized: list[dict[str, str]] = []
        for message in messages:
            serialized.append(
                {
                    "role": message.role,
                    "content": message.content,
                }
            )
        return serialized

    def _parse_sse_chunk(self, line: str) -> str | None:
        if not line or not line.startswith("data: "):
            return None

        data = line[len("data: ") :].strip()
        if data == "[DONE]":
            return None

        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return None

        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            return None

        delta = choices[0].get("delta")
        if not isinstance(delta, dict):
            return None

        content = delta.get("content")
        if isinstance(content, str) and content:
            return content
        return None
