"""
OpenAI provider for local chat execution. Per ARCHITECTURE.md, tutor calls LLM directly.
"""
from __future__ import annotations

import json

import httpx

from app.services.ai_providers.base import BaseProvider, ChatMessage, ModelConfig, ProviderError


class OpenAIProvider(BaseProvider):
    provider_name = "openai"
    supported_models = ("gpt-4o", "gpt-4o-mini", "gpt-4")

    def __init__(self, *, api_key: str, base_url: str = "https://api.openai.com/v1", timeout: float = 60.0):
        super().__init__(provider_name=self.provider_name, supported_models=self.supported_models)
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model_config: ModelConfig,
    ):
        self.assert_model_supported(model_config.model)
        payload = {
            "model": model_config.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
            "temperature": model_config.temperature,
            "max_tokens": model_config.max_tokens,
        }
        async with httpx.AsyncClient(timeout=model_config.timeout_seconds or self._timeout) as client:
            response = await client.post(
                f"{self._base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self._api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            if response.status_code >= 400:
                raise ProviderError(
                    f"OpenAI API error {response.status_code}: {response.text[:500]}"
                )
            async for line in response.aiter_lines():
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:].strip()
                if data == "[DONE]":
                    break
                try:
                    obj = json.loads(data)
                except json.JSONDecodeError:
                    continue
                for choice in obj.get("choices", []):
                    delta = choice.get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content

    def count_tokens(self, text: str) -> int:
        """Heuristic: ~4 chars per token for English."""
        if not text:
            return 0
        return max(1, len(text) // 4)
