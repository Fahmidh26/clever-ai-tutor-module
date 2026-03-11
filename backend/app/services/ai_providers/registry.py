from __future__ import annotations

from dataclasses import dataclass

from app.services.ai_providers.base import BaseProvider, ProviderError


@dataclass(frozen=True)
class ProviderResolution:
    provider: BaseProvider
    model: str


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, BaseProvider] = {}

    def register(self, provider: BaseProvider) -> None:
        self._providers[provider.provider_name] = provider

    def get_provider(self, provider_name: str) -> BaseProvider:
        provider = self._providers.get(provider_name)
        if provider is None:
            raise ProviderError(f"Provider '{provider_name}' is not registered")
        return provider

    def resolve(self, *, provider_name: str, model: str) -> ProviderResolution:
        provider = self.get_provider(provider_name)
        provider.assert_model_supported(model)
        return ProviderResolution(provider=provider, model=model)

    def has_provider(self, provider_name: str) -> bool:
        return provider_name in self._providers

    def registered_provider_names(self) -> list[str]:
        return sorted(self._providers.keys())
