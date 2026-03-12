from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from app.services.ai_providers.base import ChatMessage, ModelConfig, ProviderError
from app.services.ai_providers.registry import ProviderRegistry


@dataclass(frozen=True)
class StreamSelection:
    stream: object
    first_chunk: str
    model: str
    attempts: list[dict[str, object]]


def build_model_candidates(primary_model: str, fallback_models: list[str]) -> list[str]:
    ordered: list[str] = []
    for model in [primary_model, *fallback_models]:
        m = (model or "").strip()
        if m and m not in ordered:
            ordered.append(m)
    return ordered


def is_transient_error(exc: Exception) -> bool:
    if isinstance(exc, (asyncio.TimeoutError, TimeoutError, httpx.TimeoutException)):
        return True
    text = str(exc).lower()
    return any(code in text for code in ("429", "500", "502", "503", "504", "timeout", "temporar"))


async def _next_chunk_with_timeout(stream: object, timeout_seconds: float) -> str:
    return await asyncio.wait_for(stream.__anext__(), timeout=timeout_seconds)


async def _collect_stream_text(stream: object, *, timeout_seconds: float) -> str:
    chunks: list[str] = []
    while True:
        try:
            chunk = await _next_chunk_with_timeout(stream, timeout_seconds)
        except StopAsyncIteration:
            break
        chunks.append(chunk)
    return "".join(chunks)


async def collect_chat_with_strategy(
    *,
    provider_registry: ProviderRegistry,
    provider_name: str,
    messages: list[ChatMessage],
    primary_model: str,
    fallback_models: list[str],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
    retry_attempts: int,
    retry_backoff_seconds: float,
) -> tuple[str, str, list[dict[str, object]]]:
    attempts: list[dict[str, object]] = []
    provider = provider_registry.get_provider(provider_name)

    for model in build_model_candidates(primary_model, fallback_models):
        if not provider.supports_model(model):
            attempts.append(
                {"provider": provider_name, "model": model, "attempt": 0, "status": "unsupported"}
            )
            continue

        for attempt_index in range(1, retry_attempts + 2):
            config = ModelConfig(
                provider=provider_name,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
            )
            stream = provider.stream_chat(messages, config)
            try:
                text = await _collect_stream_text(stream, timeout_seconds=timeout_seconds)
                attempts.append(
                    {"provider": provider_name, "model": model, "attempt": attempt_index, "status": "success"}
                )
                return text, model, attempts
            except Exception as exc:
                attempts.append(
                    {
                        "provider": provider_name,
                        "model": model,
                        "attempt": attempt_index,
                        "status": "error",
                        "error": str(exc)[:220],
                    }
                )
                can_retry = attempt_index <= retry_attempts and is_transient_error(exc)
                if not can_retry:
                    break
                await asyncio.sleep(retry_backoff_seconds * attempt_index)
            finally:
                close = getattr(stream, "aclose", None)
                if callable(close):
                    try:
                        await close()
                    except Exception:
                        pass

    raise ProviderError("All model attempts failed")


async def start_stream_with_strategy(
    *,
    provider_registry: ProviderRegistry,
    provider_name: str,
    messages: list[ChatMessage],
    primary_model: str,
    fallback_models: list[str],
    temperature: float,
    max_tokens: int,
    timeout_seconds: float,
    retry_attempts: int,
    retry_backoff_seconds: float,
) -> StreamSelection:
    attempts: list[dict[str, object]] = []
    provider = provider_registry.get_provider(provider_name)

    for model in build_model_candidates(primary_model, fallback_models):
        if not provider.supports_model(model):
            attempts.append(
                {"provider": provider_name, "model": model, "attempt": 0, "status": "unsupported"}
            )
            continue

        for attempt_index in range(1, retry_attempts + 2):
            config = ModelConfig(
                provider=provider_name,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout_seconds=timeout_seconds,
            )
            stream = provider.stream_chat(messages, config)
            try:
                first_chunk = await _next_chunk_with_timeout(stream, timeout_seconds)
                attempts.append(
                    {"provider": provider_name, "model": model, "attempt": attempt_index, "status": "stream_started"}
                )
                return StreamSelection(stream=stream, first_chunk=first_chunk, model=model, attempts=attempts)
            except StopAsyncIteration:
                attempts.append(
                    {"provider": provider_name, "model": model, "attempt": attempt_index, "status": "stream_empty"}
                )
                return StreamSelection(stream=stream, first_chunk="", model=model, attempts=attempts)
            except Exception as exc:
                attempts.append(
                    {
                        "provider": provider_name,
                        "model": model,
                        "attempt": attempt_index,
                        "status": "error",
                        "error": str(exc)[:220],
                    }
                )
                can_retry = attempt_index <= retry_attempts and is_transient_error(exc)
                close = getattr(stream, "aclose", None)
                if callable(close):
                    try:
                        await close()
                    except Exception:
                        pass
                if not can_retry:
                    break
                await asyncio.sleep(retry_backoff_seconds * attempt_index)

    raise ProviderError("All model attempts failed")


async def stream_remaining_chunks(stream: object, *, timeout_seconds: float):
    while True:
        try:
            chunk = await _next_chunk_with_timeout(stream, timeout_seconds)
        except StopAsyncIteration:
            break
        yield chunk
