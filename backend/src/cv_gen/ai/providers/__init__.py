"""AI provider registry and factory."""

from __future__ import annotations

import os

from cv_gen.ai.base import AIProvider


def is_ai_configured() -> bool:
    """Return True if all required AI env vars are set."""
    return all(os.getenv(k) for k in ("AI_PROVIDER", "AI_API_KEY", "AI_MODEL"))


def get_provider() -> AIProvider:
    """Instantiate the configured AI provider.

    Reads ``AI_PROVIDER``, ``AI_API_KEY``, and ``AI_MODEL`` from the
    environment.  Raises if the configuration is incomplete or the
    provider name is unknown.
    """
    name = os.getenv("AI_PROVIDER", "")
    api_key = os.getenv("AI_API_KEY", "")
    model = os.getenv("AI_MODEL", "")

    if not model:
        raise RuntimeError("AI_MODEL environment variable is required")

    if name == "google":
        from cv_gen.ai.providers.google import GoogleProvider

        return GoogleProvider(api_key=api_key, model=model)

    if name == "openai":
        from cv_gen.ai.providers.openai import OpenAIProvider

        return OpenAIProvider(
            api_key=api_key,
            model=model,
            base_url=os.getenv("AI_BASE_URL") or None,
        )

    if name == "anthropic":
        from cv_gen.ai.providers.anthropic import AnthropicProvider

        return AnthropicProvider(api_key=api_key, model=model)

    if name == "openrouter":
        from cv_gen.ai.providers.openai import OpenAIProvider

        return OpenAIProvider(
            api_key=api_key,
            model=model,
            base_url="https://openrouter.ai/api/v1",
            default_headers={"HTTP-Referer": "https://github.com/cv-gen"},
        )

    raise ValueError(f"Unknown AI provider: {name!r}")
