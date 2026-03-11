from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str
    name: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 1024
    top_p: float = 1.0
    timeout_seconds: float = 60.0
    extra: dict[str, Any] = field(default_factory=dict)


class ProviderError(Exception):
    pass


class BaseProvider(ABC):
    provider_name: str
    supported_models: tuple[str, ...]

    def __init__(self, *, provider_name: str, supported_models: tuple[str, ...]) -> None:
        self.provider_name = provider_name
        self.supported_models = supported_models

    def supports_model(self, model: str) -> bool:
        return model in self.supported_models

    def assert_model_supported(self, model: str) -> None:
        if not self.supports_model(model):
            raise ProviderError(
                f"Model '{model}' is not supported by provider '{self.provider_name}'"
            )

    @abstractmethod
    async def stream_chat(
        self,
        messages: list[ChatMessage],
        model_config: ModelConfig,
    ) -> AsyncGenerator[str, None]:
        """Yield response chunks as plain text tokens."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Estimate tokens for the provider's tokenizer behavior."""
